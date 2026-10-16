#!/usr/bin/env python3
"""Measure what registering skills costs in the system prompt.

Pi 在启动时把每个可用 skill 的 name/description/path 写进 system prompt，正文按需读取。
本脚本用同一个无关提示跑多个条件（不注册 skill / 注册指定目录），比较首个
assistant 调用的 prompt token 数与整轮耗时，得到注册开销。

用法：
  python3 scripts/measure-skill-context.py --skill-dir skills/golang --skill-dir skills --repeat 3
"""

from __future__ import annotations

import argparse
import json
import statistics
import subprocess
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = REPO_ROOT / ".tmp/skill-load-measurement.json"
DEFAULT_MODEL = "deepseek/deepseek-v4-flash-vision-exp"
PROMPT = "Reply with the single word: ok"


def measure_once(skill_dirs: list[Path], args: argparse.Namespace) -> dict:
    command = [
        "pi", "-p", "--mode", "json",
        "--no-session", "--no-context-files", "--no-skills", "--no-extensions", "--no-mcp",
        "--tools", args.tools, "--model", args.model, "--thinking", args.thinking,
    ]
    for directory in skill_dirs:
        command += ["--skill", str(directory)]
    command += ["--", PROMPT]

    started = time.monotonic()
    proc = subprocess.run(command, text=True, capture_output=True, timeout=args.timeout)
    elapsed = time.monotonic() - started

    prompt_tokens = output_tokens = None
    for line in proc.stdout.splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if event.get("type") != "message_end":
            continue
        message = event.get("message", {})
        if message.get("role") != "assistant" or prompt_tokens is not None:
            continue
        usage = message.get("usage") or {}
        prompt_tokens = (usage.get("input") or 0) + (usage.get("cacheRead") or 0) + (usage.get("cacheWrite") or 0)
        output_tokens = usage.get("output")
    if prompt_tokens is None:
        raise RuntimeError(f"没有从 pi 输出中读到首个 assistant 的 usage（exit={proc.returncode}）: {proc.stderr[:200]}")
    return {"prompt_tokens": prompt_tokens, "output_tokens": output_tokens, "elapsed": round(elapsed, 1)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--skill-dir", action="append", type=Path, default=[],
                        help="注册为独立条件的 skill 目录，可重复；相对路径按仓库根解析")
    parser.add_argument("--repeat", type=int, default=3, help="每个条件的重复次数（默认 3，取中位数）")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--thinking", default="off")
    parser.add_argument("--tools", default="read")
    parser.add_argument("--timeout", type=int, default=300)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()

    conditions: list[tuple[str, list[Path]]] = [("none", [])]
    for directory in args.skill_dir:
        resolved = directory if directory.is_absolute() else REPO_ROOT / directory
        if not resolved.is_dir():
            parser.error(f"目录不存在：{resolved}")
        conditions.append((str(directory), [resolved]))

    results = []
    for label, directories in conditions:
        samples = []
        for attempt in range(1, args.repeat + 1):
            sample = measure_once(directories, args)
            samples.append(sample)
            print(f"{label} #{attempt}: prompt={sample['prompt_tokens']} tok, {sample['elapsed']}s", flush=True)
        results.append({
            "condition": label,
            "skill_dirs": [str(d.relative_to(REPO_ROOT)) for d in directories],
            "prompt_tokens_median": statistics.median(s["prompt_tokens"] for s in samples),
            "elapsed_median": statistics.median(s["elapsed"] for s in samples),
            "samples": samples,
        })

    baseline = results[0]["prompt_tokens_median"]
    print("\n| 条件 | prompt tokens（中位数） | 相对不注册 | 整轮耗时中位数 |")
    print("| --- | --- | --- | --- |")
    for item in results:
        delta = item["prompt_tokens_median"] - baseline
        print(f"| {item['condition']} | {item['prompt_tokens_median']:.0f} | {delta:+.0f} | {item['elapsed_median']:.1f}s |")

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps({"model": args.model, "thinking": args.thinking, "prompt": PROMPT, "results": results},
                   ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

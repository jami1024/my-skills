#!/usr/bin/env python3
"""Run a skill's eval cases through pi and keep the evidence.

每个用例跑两个条件：只注册目标 skill 与完全不注册（基线）。脚本只负责可复现地
产生证据——pi 日志、最终回答、逐例耗时与读取路径；断言判定仍需人工阅读回答，
不自动判分，避免把自然语言断言压成正则匹配。

用法：
  python3 scripts/run-skill-eval.py --skill golang-project-layout --case 1 --case 3
  python3 scripts/run-skill-eval.py --skills-root skills/content --skill explain
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SKILLS_ROOT = REPO_ROOT / "skills/golang"
NAME_RE = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
DEFAULT_OUT = REPO_ROOT / ".tmp/skill-eval"
DEFAULT_MODEL = "deepseek/deepseek-v4-flash-vision-exp"
PROMPT_SUFFIX = (
    "\n\nOnly read-only tools are available in this session. Do not attempt to write or "
    "modify files; answer directly in your reply."
)


def load_cases(skill_dir: Path) -> list[dict]:
    """上游 evals.json 有两种结构：顶层数组与 {skill_name, evals} 对象。"""
    path = skill_dir / "evals/evals.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"无法读取 {path}: {exc}") from exc
    if isinstance(data, list):
        return data
    if isinstance(data.get("evals"), list):
        return data["evals"]
    raise ValueError(f"{path}: 无法识别的结构")


def select_cases(cases: list[dict], indices: list[int] | None) -> list[tuple[int, dict]]:
    """按 1-based 序号选取用例；不指定时返回全部。"""
    if not indices:
        return list(enumerate(cases, 1))
    unknown = [index for index in indices if not 1 <= index <= len(cases)]
    if unknown:
        raise ValueError(f"用例序号超出范围：{unknown}（该 skill 共 {len(cases)} 例）")
    return [(index, cases[index - 1]) for index in indices]


def parse_skill_argument(value: str) -> tuple[str, list[int] | None]:
    """解析 --skill 参数：`golang-testing` 或 `golang-testing:2,12`。"""
    name, separator, raw_indices = value.partition(":")
    if not separator:
        return name.strip(), None
    try:
        indices = [int(item) for item in raw_indices.split(",") if item.strip()]
    except ValueError as exc:
        raise ValueError(f"无法解析用例序号：{value}") from exc
    if not indices:
        raise ValueError(f"--skill 的序号部分为空：{value}")
    return name.strip(), indices


def build_report(runs: dict[str, tuple[list[tuple[int, dict]], list[dict]]]) -> str:
    """生成待填判定的 markdown 骨架，判定列留空由人工阅读回答后填写。"""
    lines = [
        "# 断言运行记录",
        "",
        "判定列需要人工阅读对应 `.answer.md` 后填写，脚本不自动判分。",
        "标为**无效**的对照不构成证据（处理组没加载正文、基线读到 skill 或会话异常）。",
        "",
    ]
    for skill, (cases, entries) in runs.items():
        lines += [f"## {skill}", ""]
        for index, case in cases:
            base = f"{skill.removeprefix('golang-')}-{index:02d}"
            lines += [
                f"### 用例 {index}：{case.get('name', '')}",
                "",
                f"- 提示词：{case['prompt'][:200]}",
            ]
            for entry in entries:
                if entry["case"].split(".")[0] != base:
                    continue
                lines.append(
                    f"- `{entry['case']}` exit={entry['exit']} 耗时={entry['elapsed']}s "
                    f"读取文件数={len(entry['reads'])} 有效性={entry['reason']} "
                    f"答案={entry['answer_path']}"
                )
            lines += ["", "| 断言 | 文本 | 有 skill | 无 skill |", "| --- | --- | --- | --- |"]
            for assertion in case.get("assertions", []):
                lines.append(f"| {assertion['id']} | {assertion['text']} |  |  |")
            lines.append("")
    return "\n".join(lines)


def case_workdir(case: dict, out: Path, repo_root: Path = REPO_ROOT) -> Path:
    """用例自带 fixture 时以它为工作目录，否则用输出目录。"""
    fixture = case.get("fixture")
    return repo_root / fixture if fixture else out


def invoke_prompt(skill: str | None, prompt: str, force: bool) -> str:
    """`force` 为真时用 `/skill:<name>` 显式加载 skill。

    只把「注册了 skill」当处理条件时，模型可能根本不读 SKILL.md（实测发生过），
    对照就退化成两组无 skill。需要评估正文效果时必须强制加载。
    """
    if skill and force:
        return f"/skill:{skill}\n{prompt}"
    return prompt


def normalise_read(path: str) -> str:
    """把读取路径归一成仓库相对路径，以便比对 skill 目录。"""
    if "/my-skills/" in path:
        return path.split("/my-skills/", 1)[1]
    return path[2:] if path.startswith("./") else path


def skill_file_reads(reads: list[str], skill: str | None = None) -> list[str]:
    """读取事件里命中的 skill 正文路径；给 skill 时只看该 skill 目录。"""
    prefix = "skills/"
    return [
        normalised
        for normalised in (normalise_read(raw) for raw in reads)
        if normalised.startswith(prefix) and normalised.endswith("/SKILL.md")
        and (skill is None or Path(normalised).parent.name == skill)
    ]


def evaluate_validity(
    skill: str | None, reads: list[str], forced: bool, exit_code: int
) -> dict:
    """判定一次运行是否构成有效证据。

    处理组必须真的加载了目标 skill 正文（要么由 `/skill:<name>` 强制注入，
    要么模型自己读了 SKILL.md）；基线则不得读到任何 skill 正文。只检查命令行
    参数是不够的：实测出现过“注册了 skill 但模型一次都没读”的处理组。
    """
    skill_files = skill_file_reads(reads, None)
    if exit_code != 0:
        return {"valid": False, "reason": "会话未正常结束", "skill_files_read": skill_files}
    if skill is None:
        if skill_files:
            return {"valid": False, "reason": "基线读到了 skill 正文", "skill_files_read": skill_files}
        return {"valid": True, "reason": "基线未接触 skill", "skill_files_read": []}
    if forced:
        return {"valid": True, "reason": "强制加载", "skill_files_read": skill_files}
    own = skill_file_reads(reads, skill)
    if own:
        return {"valid": True, "reason": "模型自行读取", "skill_files_read": skill_files}
    return {"valid": False, "reason": "处理组未读目标 skill", "skill_files_read": skill_files}


def run_case(
    case_id: str, prompt: str, skill: str | None, workdir: Path, args: argparse.Namespace
) -> dict:
    command = [
        "pi", "-p", "--mode", "json",
        "--no-session", "--no-context-files", "--no-skills", "--no-extensions", "--no-mcp",
        "--tools", args.tools, "--model", args.model, "--thinking", args.thinking,
    ]
    if skill:
        command += ["--skill", str(args.skills_root / skill)]
    command += ["--", invoke_prompt(skill, prompt + PROMPT_SUFFIX, args.invoke_skill)]

    started = time.monotonic()
    proc = subprocess.run(
        command, cwd=workdir, text=True, capture_output=True, timeout=args.timeout
    )
    elapsed = time.monotonic() - started

    answer: list[str] = []
    reads: list[str] = []
    for line in proc.stdout.splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if event.get("type") == "tool_execution_start" and event.get("toolName") == "read":
            path = (event.get("args") or {}).get("path")
            if path:
                reads.append(path)
        if event.get("type") == "message_end" and event.get("message", {}).get("role") == "assistant":
            message = event["message"]
            answer = [part["text"] for part in message.get("content", []) if part.get("type") == "text"]

    (args.out / f"{case_id}.jsonl").write_text(proc.stdout, encoding="utf-8")
    (args.out / f"{case_id}.stderr").write_text(proc.stderr, encoding="utf-8")
    answer_path = args.out / f"{case_id}.answer.md"
    answer_path.write_text("\n".join(answer), encoding="utf-8")
    entry = {
        "case": case_id,
        "skill": skill,
        "exit": proc.returncode,
        "elapsed": round(elapsed, 1),
        "reads": reads,
        "answer_chars": len("\n".join(answer)),
        "answer_path": str(answer_path.relative_to(REPO_ROOT)) if answer_path.is_relative_to(REPO_ROOT) else str(answer_path),
        "workdir": str(workdir.relative_to(REPO_ROOT)) if workdir.is_relative_to(REPO_ROOT) else str(workdir),
        "forced_invocation": bool(skill and args.invoke_skill),
    }
    entry.update(evaluate_validity(skill, reads, entry["forced_invocation"], proc.returncode))
    return entry


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--skills-root", type=Path, default=SKILLS_ROOT,
                        help="仓库内的 skill 分类目录，默认 skills/golang")
    parser.add_argument("--skill", action="append", required=True,
                        help="分类目录下的 skill 名，可写作 name:1,2 指定用例；可重复")
    parser.add_argument("--case", action="append", type=int,
                        help="未在 --skill 里指定序号时使用的默认用例序号，可重复；默认全部")
    parser.add_argument("--variant", default="skill,none", help="skill,none 的子集")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT, help=f"输出目录（默认 {DEFAULT_OUT}）")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--thinking", default="low")
    parser.add_argument("--tools", default="read")
    parser.add_argument("--invoke-skill", action=argparse.BooleanOptionalAction, default=True,
                        help="用 /skill:<name> 强制加载目标 skill（默认开启），--no-invoke-skill 关闭")
    parser.add_argument("--timeout", type=int, default=600, help="单个会话超时秒数")
    parser.add_argument("--report", type=Path, help="额外写出待填判定的 markdown 骨架")
    parser.add_argument("--allow-invalid", action="store_true",
                        help="存在无效对照时仍以 0 退出（默认非 0，避免静默使用无效证据）")
    args = parser.parse_args()

    variants = [item.strip() for item in args.variant.split(",") if item.strip()]
    if not variants or set(variants) - {"skill", "none"}:
        parser.error("--variant 只接受 skill 与 none")

    args.skills_root = (REPO_ROOT / args.skills_root).resolve()
    if not args.skills_root.is_relative_to(REPO_ROOT / "skills") or not args.skills_root.is_dir():
        parser.error("--skills-root 必须是仓库 skills/ 内存在的分类目录")
    args.out = args.out if args.out.is_absolute() else REPO_ROOT / args.out
    if args.report and not args.report.is_absolute():
        args.report = REPO_ROOT / args.report

    args.out.mkdir(parents=True, exist_ok=True)
    entries: list[dict] = []
    runs: dict[str, tuple[list[tuple[int, dict]], list[dict]]] = {}
    for value in args.skill:
        try:
            skill, indices = parse_skill_argument(value)
        except ValueError as exc:
            parser.error(str(exc))
        if not NAME_RE.fullmatch(skill):
            parser.error(f"--skill 只接受分类目录下的 skill 名：{skill}")
        skill_dir = args.skills_root / skill
        try:
            cases = select_cases(load_cases(skill_dir), indices or args.case)
        except ValueError as exc:
            parser.error(str(exc))
        skill_entries: list[dict] = []
        for index, case in cases:
            base = f"{skill.removeprefix('golang-')}-{index:02d}"
            workdir = case_workdir(case, args.out)
            for variant in variants:
                case_id = f"{base}.{variant}"
                entry = run_case(
                    case_id, case["prompt"], skill if variant == "skill" else None, workdir, args
                )
                entry["name"] = case.get("name")
                entries.append(entry)
                skill_entries.append(entry)
                print(
                    f"{case_id}: exit={entry['exit']} 耗时={entry['elapsed']}s "
                    f"答案={entry['answer_chars']}字符 读取={len(entry['reads'])} "
                    f"{'有效' if entry['valid'] else '无效（' + entry['reason'] + '）'}",
                    flush=True,
                )
        runs[skill] = (cases, skill_entries)

    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(build_report(runs), encoding="utf-8")

    (args.out / "results.json").write_text(
        json.dumps(entries, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    invalid = [entry for entry in entries if not entry["valid"]]
    if invalid:
        for entry in invalid:
            print(f"无效对照：{entry['case']} —— {entry['reason']}", flush=True)
        if not args.allow_invalid:
            print("用 --no-invoke-skill 会失去强制加载，用 --no-skills 会无法注册；"
                  "确认分组与提示词后重跑，或在明确知情时加 --allow-invalid。", flush=True)
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

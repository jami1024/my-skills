#!/usr/bin/env python3
"""Replay the documented local overrides on an upstream Go skill snapshot."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

MANIFEST = Path(__file__).with_name("golang-overrides.json")


def merge_text_fixes(
    *groups: dict[str, list[dict[str, str]]],
) -> dict[str, list[dict[str, str]]]:
    """正文修正与评估断言修正共用同一套重放、幂等和失配检查。"""
    merged: dict[str, list[dict[str, str]]] = {}
    for group in groups:
        for relative, patches in group.items():
            merged.setdefault(relative, []).extend(patches)
    return merged


def plan_global_patterns(
    root: Path, specs: list[dict], texts: dict[Path, str]
) -> dict[Path, str]:
    """对全库 Markdown 应用正则替换，例如把上游 skill 标识符改成当前注册名。

    必须在逐文件补丁之后执行：补丁的 `old` 文本抄自上游原文，先替换会失配。
    正则替换天然幂等（已替换过的文本不再匹配），因此无需 `new` 存在性检查。
    """
    planned: dict[Path, str] = dict(texts)
    for spec in specs:
        label = spec.get("id", "global pattern")
        try:
            pattern = re.compile(spec["pattern"])
        except (KeyError, re.error) as exc:
            raise ValueError(f"{label}: invalid global pattern: {exc}") from exc
        replacement = spec.get("replace", "")
        for glob in spec.get("paths", []):
            # 清单是本地可信文件，但仍拒绝越出 skill 根目录的写法，
            # 避免后续编辑清单时误改仓库其他位置。
            if Path(glob).is_absolute() or ".." in Path(glob).parts:
                raise ValueError(f"{label}: paths must stay inside the skill root: {glob}")
            for path in sorted(root.glob(glob)):
                if not path.is_file():
                    continue
                current = planned.get(path)
                if current is None:
                    current = path.read_text(encoding="utf-8")
                updated = pattern.sub(replacement, current)
                if updated != current:
                    planned[path] = updated
    return planned


def plan_local_cases(
    root: Path, local_cases: dict[str, list[dict]], texts: dict[Path, str]
) -> dict[Path, str]:
    """本地用例按用例名幂等写入上游 evals.json：缺失则追加，内容变化则替换。

    基于 `texts` 里已打完正文补丁的内容规划，避免同一文件上两次写入互相覆盖。
    目标文件缺失时跳过（与正文补丁一致），便于在部分快照上重放；仓库内清单与
    实际用例的一致性由 scripts/tests 的守卫测试检查。
    """
    plans: dict[Path, str] = {}
    for relative, cases in local_cases.items():
        path = root / relative
        current = texts.get(path)
        if current is None:
            if not path.is_file():
                continue
            current = path.read_text(encoding="utf-8")
        missing_name = [case for case in cases if not case.get("name")]
        if missing_name:
            raise ValueError(f"{relative}: 本地用例必须有 name，否则无法幂等重放")
        try:
            data = json.loads(current)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{relative}: 无法解析 evals.json: {exc}") from exc
        container = data if isinstance(data, list) else data.get("evals")
        if not isinstance(container, list):
            raise ValueError(f"{relative}: 无法识别的结构")
        known = {case.get("name"): case for case in container}
        changed = False
        for case in cases:
            current = known.get(case["name"])
            if current == case:
                continue
            if current is None:
                container.append(case)
            else:
                container[container.index(current)] = case
            changed = True
        if changed:
            plans[path] = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
    return plans


def apply_overrides(root: Path, manifest: Path = MANIFEST) -> int:
    try:
        overrides = json.loads(manifest.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read local override manifest {manifest}: {exc}") from exc
    descriptions = {
        f"{name}/SKILL.md": value
        for name, value in overrides["descriptions"].items()
    }
    text_fixes = merge_text_fixes(
        overrides["replacements"], overrides.get("assertion_fixes", {})
    )
    updates: dict[Path, str] = {}
    for relative in sorted(descriptions.keys() | text_fixes.keys()):
        path = root / relative
        if not path.is_file():
            continue
        original = path.read_text(encoding="utf-8")
        text = original
        if relative in descriptions:
            description = json.dumps(descriptions[relative], ensure_ascii=False)
            text, count = re.subn(
                r"^description:.*$", lambda _, value=description: f"description: {value}",
                text, count=1, flags=re.MULTILINE,
            )
            if count != 1:
                raise ValueError(f"{relative}: missing inline description")
        for number, patch in enumerate(text_fixes.get(relative, []), 1):
            old, new = patch["old"], patch["new"]
            label = patch.get("id", f"local patch {number}")
            # 追加型补丁的 new 包含 old，第二次重放时 old 仍会命中。new 足够长时
            # 先判定已应用，否则按原逻辑先匹配 old，失配则报错。
            if len(new) >= 40 and new in text:
                continue
            if old in text:
                text = text.replace(old, new)
            elif new not in text:
                raise ValueError(
                    f"{relative}: {label} no longer matches upstream; "
                    "review golang-overrides.json before syncing"
                )
        if text != original:
            updates[path] = text

    updates = plan_global_patterns(root, overrides.get("global_patterns", []), updates)

    # 所有失配与结构问题在写入前报错，避免半完成状态；本地用例也先规划后写。
    case_updates = plan_local_cases(root, overrides.get("local_cases", {}), updates)
    writes = {
        path: text
        for path, text in {**updates, **case_updates}.items()
        if not path.is_file() or text != path.read_text(encoding="utf-8")
    }
    for path, text in writes.items():
        path.write_text(text, encoding="utf-8")
    return len(writes)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path, help="上游或本地 skills/golang 目录")
    args = parser.parse_args()
    try:
        count = apply_overrides(args.root)
    except ValueError as exc:
        parser.exit(1, f"ERROR {exc}\n")
    print(f"Applied local overrides to {count} file(s).")


if __name__ == "__main__":
    main()

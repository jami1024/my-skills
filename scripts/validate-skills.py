#!/usr/bin/env python3
"""Validate Agent Skills metadata and repository conventions."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def parse_frontmatter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise ValueError("missing YAML frontmatter")
    end = text.find("\n---", 4)
    if end == -1:
        raise ValueError("frontmatter is not closed")

    fields: dict[str, str] = {}
    for line in text[4:end].splitlines():
        if not line or line[0].isspace() or ":" not in line:
            continue
        key, value = line.split(":", 1)
        fields[key.strip()] = value.strip().strip('"').strip("'")
    return fields


def validate(root: Path, strict: bool) -> int:
    errors: list[str] = []
    warnings: list[str] = []
    names: dict[str, Path] = {}
    skill_files = sorted(root.glob("**/SKILL.md"))

    # 模板目录使用软链接复用通用文件；断链会在客户端加载时才暴露，
    # 因此在校验阶段直接报告。
    for path in sorted(root.rglob("*")):
        if path.is_symlink() and not path.exists():
            errors.append(f"{path.relative_to(root)}: broken symlink")

    if not skill_files:
        errors.append(f"{root}: no SKILL.md found")

    for path in skill_files:
        relative = path.relative_to(root)
        try:
            fields = parse_frontmatter(path)
        except (OSError, ValueError) as exc:
            errors.append(f"{relative}: {exc}")
            continue

        name = fields.get("name", "")
        description = fields.get("description", "")
        parent_name = path.parent.name

        if not name:
            errors.append(f"{relative}: missing name")
        elif not NAME_RE.fullmatch(name):
            errors.append(f"{relative}: invalid name {name!r}")
        elif name != parent_name:
            errors.append(
                f"{relative}: name {name!r} does not match directory {parent_name!r}"
            )
        elif name in names:
            errors.append(f"{relative}: duplicate name {name!r}; already in {names[name]}")
        else:
            names[name] = relative

        if not description:
            errors.append(f"{relative}: missing description")
        elif len(description) > 1024:
            errors.append(f"{relative}: description exceeds 1024 characters")

        line_count = path.read_text(encoding="utf-8").count("\n") + 1
        if line_count > 500:
            warnings.append(f"{relative}: {line_count} lines (recommended maximum: 500)")

    for warning in warnings:
        print(f"WARN  {warning}")
    for error in errors:
        print(f"ERROR {error}")

    print(
        f"Checked {len(skill_files)} skill(s): "
        f"{len(errors)} error(s), {len(warnings)} warning(s)."
    )
    if errors or (strict and warnings):
        return 1
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "root",
        nargs="?",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "skills",
        help="skill 根目录（默认：仓库的 skills/）",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="将超长 SKILL.md 的 warning 视为失败",
    )
    args = parser.parse_args()
    return validate(args.root.resolve(), args.strict)


if __name__ == "__main__":
    sys.exit(main())

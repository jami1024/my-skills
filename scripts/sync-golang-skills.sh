#!/usr/bin/env bash
set -euo pipefail

# 把上游 samber/cc-skills-golang 的 Go skill 同步到 skills/golang/。
# 保留本地 README.md 与 EVALUATIONS.md，并重放 golang-overrides.json 中的本地修正。
# 暂存内容通过严格校验后才替换目标；替换失败时恢复旧副本。
# 用法：bash scripts/sync-golang-skills.sh [上游地址]
# 默认取自 https://github.com/samber/cc-skills-golang；也可传入镜像或本地克隆。

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
UPSTREAM="${1:-https://github.com/samber/cc-skills-golang}"
TMP_ROOT="$REPO_ROOT/.tmp"
CLONE_DIR="$TMP_ROOT/cc-skills-golang"
TARGET="$REPO_ROOT/skills/golang"

mkdir -p "$TMP_ROOT"
WORK_DIR="$(mktemp -d "$TMP_ROOT/skills-golang.XXXXXX")"
STAGED="$WORK_DIR/new"
BACKUP="$WORK_DIR/backup"

cleanup() {
  local status=$?
  if [ -d "$BACKUP" ] && [ ! -e "$TARGET" ]; then
    if ! mv "$BACKUP" "$TARGET"; then
      echo "恢复失败：旧副本保留在 ${BACKUP}，请手动恢复到 ${TARGET}" >&2
      return 1
    fi
  fi
  rm -rf "$WORK_DIR"
  return "$status"
}
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

rm -rf "$CLONE_DIR"
git clone --depth 1 "$UPSTREAM" "$CLONE_DIR"
UPSTREAM_COMMIT="$(git -C "$CLONE_DIR" rev-parse HEAD)"

mkdir -p "$STAGED/rules"
cp -R "$CLONE_DIR/skills/." "$STAGED/"
cp "$CLONE_DIR/LICENSE" "$STAGED/LICENSE"
cp "$CLONE_DIR/rules/golang-always.mdc" "$STAGED/rules/"

UPSTREAM_COUNT="$(find "$CLONE_DIR/skills" -maxdepth 1 -type d -name 'golang-*' | wc -l | tr -d ' ')"
STAGED_COUNT="$(find "$STAGED" -maxdepth 1 -type d -name 'golang-*' | wc -l | tr -d ' ')"
if [ "$UPSTREAM_COUNT" -eq 0 ] || [ "$UPSTREAM_COUNT" != "$STAGED_COUNT" ]; then
  echo "暂存目录为空或不完整：上游 $UPSTREAM_COUNT 个 skill，暂存 $STAGED_COUNT 个" >&2
  exit 1
fi

# 修正、描述精简和路由适配统一从清单重放；上游变化时在替换目标前报错。
python3 "$REPO_ROOT/scripts/apply-golang-overrides.py" "$STAGED"

python3 "$REPO_ROOT/scripts/validate-skills.py" "$STAGED" --strict
# 本地维护文档的跨目录链接以最终仓库布局为准，不在临时路径下校验。
cp "$TARGET/README.md" "$TARGET/EVALUATIONS.md" "$STAGED/"
FILE_COUNT="$(find "$STAGED" -type f | wc -l | tr -d ' ')"

mv "$TARGET" "$BACKUP"
mv "$STAGED" "$TARGET"

echo "上游提交：$UPSTREAM_COMMIT"
echo "已同步 $STAGED_COUNT 个 skill，$FILE_COUNT 个文件"
echo "请核对 skills/golang/README.md 的「同步提交」与 EVALUATIONS.md 的 Summary 表"

#!/usr/bin/env bash
# golang-migrate 的可选入口；从项目根目录运行。
set -euo pipefail

ACTION="${1:-}"
MIGRATIONS_DIR="${MIGRATIONS_DIR:-./migrations}"

case "$ACTION" in
    create)
        NAME="${2:-}"
        if [ -z "$NAME" ]; then
            echo "Usage: $0 create <name>" >&2
            exit 1
        fi
        migrate create -ext sql -dir "$MIGRATIONS_DIR" -seq "$NAME"
        ;;
    up|down|version|force)
        VERSION="${2:-}"
        if [ "$ACTION" = force ] && [ -z "$VERSION" ]; then
            echo "Usage: $0 force <version>" >&2
            exit 1
        fi
        : "${DATABASE_URL:?Set DATABASE_URL explicitly before accessing a database}"
        case "$ACTION" in
            down) migrate -path "$MIGRATIONS_DIR" -database "$DATABASE_URL" down 1 ;;
            force) migrate -path "$MIGRATIONS_DIR" -database "$DATABASE_URL" force "$VERSION" ;;
            *) migrate -path "$MIGRATIONS_DIR" -database "$DATABASE_URL" "$ACTION" ;;
        esac
        ;;
    *)
        echo "Usage: $0 {up|down|create <name>|version|force <version>}" >&2
        exit 1
        ;;
esac

echo "Done."

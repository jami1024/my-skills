#!/bin/bash
# Golang 数据库迁移脚本

set -e

ACTION=${1:-up}
MIGRATIONS_DIR=${MIGRATIONS_DIR:-./migrations}
DATABASE_URL=${DATABASE_URL:-"mysql://root:password@localhost:3306/myapp"}

case "$ACTION" in
    up)
        echo "⬆️  Running migrations up..."
        migrate -path "$MIGRATIONS_DIR" -database "$DATABASE_URL" up
        ;;
    down)
        echo "⬇️  Rolling back last migration..."
        migrate -path "$MIGRATIONS_DIR" -database "$DATABASE_URL" down 1
        ;;
    create)
        NAME=${2:-"migration"}
        echo "📝 Creating new migration: $NAME"
        migrate create -ext sql -dir "$MIGRATIONS_DIR" -seq "$NAME"
        ;;
    version)
        echo "📍 Current version:"
        migrate -path "$MIGRATIONS_DIR" -database "$DATABASE_URL" version
        ;;
    force)
        VERSION=${2}
        if [ -z "$VERSION" ]; then
            echo "Usage: $0 force <version>"
            exit 1
        fi
        echo "⚠️  Force setting version to $VERSION..."
        migrate -path "$MIGRATIONS_DIR" -database "$DATABASE_URL" force "$VERSION"
        ;;
    *)
        echo "Usage: $0 {up|down|create|version|force} [args]"
        echo ""
        echo "Commands:"
        echo "  up      - Apply all migrations"
        echo "  down    - Rollback last migration"
        echo "  create  - Create new migration files"
        echo "  version - Show current version"
        echo "  force   - Force set version (use with caution)"
        exit 1
        ;;
esac

echo ""
echo "✅ Done!"

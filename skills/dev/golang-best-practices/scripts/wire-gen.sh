#!/bin/bash
# Wire 依赖注入代码生成脚本

set -e

echo "🔌 Generating Wire code..."

# 不自动安装工具，避免未审计的版本进入项目环境。
if ! command -v wire &> /dev/null; then
    echo "❌ Wire not found. Install the version pinned by this project before running this script." >&2
    exit 1
fi

# 生成代码
wire gen ./internal/...

echo ""
echo "✅ Wire code generated successfully!"

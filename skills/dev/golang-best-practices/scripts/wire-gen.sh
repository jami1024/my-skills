#!/usr/bin/env bash
# Wire 依赖注入代码生成脚本；参数为项目实际采用的包路径。

set -euo pipefail

echo "🔌 Generating Wire code..."

# 不自动安装工具，避免未审计的版本进入项目环境。
if ! command -v wire &> /dev/null; then
    echo "❌ Wire not found. Install the version pinned by this project before running this script." >&2
    exit 1
fi

# 未提供参数时只处理当前 package，不假定存在 internal/。
if [ "$#" -eq 0 ]; then
    set -- .
fi
wire gen "$@"

echo ""
echo "✅ Wire code generated successfully!"

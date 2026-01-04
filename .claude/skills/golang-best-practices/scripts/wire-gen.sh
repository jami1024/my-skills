#!/bin/bash
# Wire 依赖注入代码生成脚本

set -e

echo "🔌 Generating Wire code..."

# 检查 Wire 是否安装
if ! command -v wire &> /dev/null; then
    echo "❌ Wire not found. Installing..."
    go install github.com/google/wire/cmd/wire@latest
fi

# 生成代码
wire gen ./internal/...

echo ""
echo "✅ Wire code generated successfully!"

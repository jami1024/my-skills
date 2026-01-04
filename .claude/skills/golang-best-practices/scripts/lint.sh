#!/bin/bash
# Golang 代码检查脚本

set -e

echo "🔍 Running linters..."

echo ""
echo "📝 Running golangci-lint..."
golangci-lint run ./...

echo ""
echo "🔎 Running go vet..."
go vet ./...

echo ""
echo "✅ All checks passed!"

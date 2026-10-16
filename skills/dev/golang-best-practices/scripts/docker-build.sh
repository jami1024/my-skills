#!/usr/bin/env bash
# 可选镜像构建入口：[image] [tag] [docker build options...]

set -euo pipefail

IMAGE_NAME=${1:-golang-app}
TAG=${2:-latest}
if [ "$#" -gt 0 ]; then shift; fi
if [ "$#" -gt 0 ]; then shift; fi

echo "🐳 Building Docker image..."
echo "   Image: $IMAGE_NAME:$TAG"
echo ""

docker build -t "$IMAGE_NAME:$TAG" "$@" "${BUILD_CONTEXT:-.}"

echo ""
echo "✅ Build completed: $IMAGE_NAME:$TAG"

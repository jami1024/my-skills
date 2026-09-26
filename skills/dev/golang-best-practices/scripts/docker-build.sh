#!/bin/bash
# Golang Docker 构建脚本

set -e

IMAGE_NAME=${1:-golang-app}
TAG=${2:-latest}

echo "🐳 Building Docker image..."
echo "   Image: $IMAGE_NAME:$TAG"
echo ""

docker build -t "$IMAGE_NAME:$TAG" .

echo ""
echo "✅ Build completed!"
echo "   Run: docker run -p 8080:8080 $IMAGE_NAME:$TAG"

.PHONY: help install dev build test lint wire docker clean

# 应用配置
APP_NAME := myapp
BUILD_DIR := ./bin
MAIN_FILE := ./cmd/myapp/main.go

# 默认目标：显示帮助信息
help:
	@echo "Available commands:"
	@echo "  make install  - Install dependencies and tools"
	@echo "  make dev      - Start development server"
	@echo "  make build    - Build binary"
	@echo "  make test     - Run tests with coverage"
	@echo "  make lint     - Run linters"
	@echo "  make wire     - Generate Wire dependency injection code"
	@echo "  make docker   - Start Docker services"
	@echo "  make clean    - Clean build artifacts and cache"

# 安装依赖和工具
install:
	go mod download
	go install github.com/google/wire/cmd/wire@latest
	go install github.com/golangci/golangci-lint/cmd/golangci-lint@latest
	go install github.com/cosmtrek/air@latest

# 启动开发服务器（使用 air 热重载）
dev:
	@if command -v air > /dev/null; then \
		air; \
	else \
		go run $(MAIN_FILE); \
	fi

# 构建二进制文件
build:
	@mkdir -p $(BUILD_DIR)
	go build -ldflags="-s -w" -o $(BUILD_DIR)/$(APP_NAME) $(MAIN_FILE)
	@echo "Build complete: $(BUILD_DIR)/$(APP_NAME)"

# 运行二进制文件
run: build
	$(BUILD_DIR)/$(APP_NAME)

# 运行测试
test:
	go test -v -race -coverprofile=coverage.out ./...
	go tool cover -html=coverage.out -o coverage.html
	@echo "Coverage report: coverage.html"

# 代码检查
lint:
	golangci-lint run ./...

# 生成 Wire 依赖注入代码
wire:
	@if [ -d "internal/wire" ]; then \
		cd internal/wire && wire; \
		echo "Wire code generated"; \
	else \
		echo "Warning: internal/wire directory not found"; \
	fi

# 启动 Docker 服务
docker:
	docker-compose --env-file .env.dev up -d

# 构建 Docker 镜像
docker-build:
	docker-compose build --no-cache

# 查看 Docker 日志
docker-logs:
	docker-compose logs -f

# 停止 Docker 服务
docker-down:
	docker-compose down

# 清理构建产物和缓存
clean:
	rm -rf $(BUILD_DIR)/ coverage.out coverage.html
	go clean -cache -testcache -modcache

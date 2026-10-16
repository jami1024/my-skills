.PHONY: help install dev build run test test-race coverage lint wire docker docker-build docker-logs docker-down clean

# 默认支持根目录单包；多入口项目显式传 MAIN_PACKAGE=./cmd/server。
APP_NAME ?= app
BUILD_DIR ?= ./bin
MAIN_PACKAGE ?= .
# 保留原 MAIN_FILE 覆盖入口，同时默认构建整个 package，包含同包其他源文件。
MAIN_FILE ?= $(MAIN_PACKAGE)
DEV_COMMAND ?= go run "$(MAIN_FILE)"
LINT_COMMAND ?= go vet ./...
WIRE_PACKAGES ?= .
COMPOSE_FILE ?= templates/docker/docker-compose.yml
ENV_FILE ?=
COMPOSE = docker compose -f "$(COMPOSE_FILE)" $(if $(ENV_FILE),--env-file "$(ENV_FILE)")
GOLANGCI_LINT_MODULE = github.com/golangci/golangci-lint$(if $(filter v2.%,$(GOLANGCI_LINT_VERSION)),/v2)

help:
	@echo "Available commands:"
	@echo "  make install    - Download dependencies; install only tools with explicit version variables"
	@echo "  make dev        - Run the selected Go package (override DEV_COMMAND for a reloader)"
	@echo "  make build/run  - Build/run MAIN_PACKAGE (default: .)"
	@echo "  make test       - Run Go tests"
	@echo "  make test-race  - Run tests with race detection"
	@echo "  make coverage   - Write coverage.out and coverage.html"
	@echo "  make lint       - Run LINT_COMMAND (default: go vet ./...)"
	@echo "  make wire       - Run installed Wire on WIRE_PACKAGES (default: .)"
	@echo "  make docker     - Start the selected Compose configuration"
	@echo "  make clean      - Remove local build and coverage artifacts"

# 例如只安装 Wire：make install WIRE_VERSION=v0.6.0。
# 不传版本时只下载项目依赖，不安装任何辅助工具。
install:
	@for version in "$(WIRE_VERSION)" "$(GOLANGCI_LINT_VERSION)" "$(AIR_VERSION)"; do \
		case "$$version" in latest) echo "Specify a pinned tool version instead of latest" >&2; exit 1 ;; esac; \
	done
	go mod download
	@if [ -n "$(WIRE_VERSION)" ]; then go install "github.com/google/wire/cmd/wire@$(WIRE_VERSION)"; fi
	@if [ -n "$(GOLANGCI_LINT_VERSION)" ]; then go install "$(GOLANGCI_LINT_MODULE)/cmd/golangci-lint@$(GOLANGCI_LINT_VERSION)"; fi
	@if [ -n "$(AIR_VERSION)" ]; then go install "github.com/air-verse/air@$(AIR_VERSION)"; fi

dev:
	$(DEV_COMMAND)

build:
	@mkdir -p "$(BUILD_DIR)"
	go build -trimpath -o "$(BUILD_DIR)/$(APP_NAME)" "$(MAIN_FILE)"
	@echo "Build complete: $(BUILD_DIR)/$(APP_NAME)"

run: build
	"$(BUILD_DIR)/$(APP_NAME)"

test:
	go test ./...

test-race:
	go test -race ./...

coverage:
	go test -coverprofile=coverage.out ./...
	go tool cover -html=coverage.out -o coverage.html

lint:
	$(LINT_COMMAND)

wire:
	wire gen $(WIRE_PACKAGES)
	@echo "Wire code generated successfully"

docker:
	$(COMPOSE) up -d

docker-build:
	$(COMPOSE) build

docker-logs:
	$(COMPOSE) logs -f

docker-down:
	$(COMPOSE) down

clean:
	rm -rf "$(BUILD_DIR)" coverage.out coverage.html

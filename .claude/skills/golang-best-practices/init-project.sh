#!/bin/bash

# Golang 项目初始化脚本
# 基于 miniblog 和 onex 项目的最佳实践

set -e

PROJECT_NAME="${1:-myapp}"
MODULE_PATH="${2:-github.com/yourusername/$PROJECT_NAME}"

echo "🚀 初始化 Golang 项目: $PROJECT_NAME"
echo "📦 模块路径: $MODULE_PATH"

# 创建项目根目录
mkdir -p "$PROJECT_NAME"
cd "$PROJECT_NAME"

# 1. 创建标准目录结构
echo "📁 创建目录结构..."

# 主应用入口
mkdir -p cmd/"$PROJECT_NAME"-apiserver

# 内部私有代码
mkdir -p internal/apiserver/{biz/v1/{user,post},handler/v1/{user,post},store,model,pkg/{conversion,middleware}}
mkdir -p internal/pkg/{contextx,errno,known,log}

# 外部可用的库代码
mkdir -p pkg/api/apiserver/v1

# API 定义文件
mkdir -p api/protobuf-spec
mkdir -p api/openapi

# 配置文件
mkdir -p configs

# 构建输出
mkdir -p _output/{platforms/linux/amd64,logs}

# 部署文件
mkdir -p deployments

# 脚本
mkdir -p scripts

# 文档
mkdir -p docs/{devel,guide,images}

# 测试
mkdir -p test

# 第三方工具
mkdir -p tools

# Examples
mkdir -p examples/client

echo "✅ 目录结构创建完成"

# 2. 初始化 go.mod
echo "📦 初始化 go.mod..."
cat > go.mod <<EOF
module $MODULE_PATH

go 1.23

require (
    github.com/gin-gonic/gin v1.9.1
    github.com/spf13/cobra v1.8.0
    github.com/spf13/pflag v1.0.5
    github.com/spf13/viper v1.18.2
    go.uber.org/zap v1.26.0
    gorm.io/gorm v1.25.5
    gorm.io/driver/mysql v1.5.2
    github.com/google/wire v0.5.0
    github.com/golang-jwt/jwt/v4 v4.5.0
    github.com/casbin/casbin/v2 v2.81.0
    github.com/asaskevich/govalidator v0.0.0-20230301143203-a9d515a09cc2
    github.com/google/uuid v1.5.0
    github.com/jinzhu/copier v0.4.0
    golang.org/x/crypto v0.18.0
    golang.org/x/sync v0.6.0
    google.golang.org/grpc v1.60.1
    google.golang.org/protobuf v1.32.0
)
EOF

# 3. 创建 Makefile
echo "🔨 创建 Makefile..."
cat > Makefile <<'EOF'
# Makefile for Golang project

# 项目变量
PROJECT_NAME := $(shell basename $(PWD))
MODULE_PATH := $(shell head -1 go.mod | awk '{print $$2}')
VERSION ?= v0.1.0
COMMIT := $(shell git rev-parse --short HEAD 2>/dev/null || echo "unknown")
BUILD_DATE := $(shell date -u +'%Y-%m-%dT%H:%M:%SZ')

# 编译变量
LDFLAGS := -s -w \
	-X '$(MODULE_PATH)/pkg/version.Version=$(VERSION)' \
	-X '$(MODULE_PATH)/pkg/version.Commit=$(COMMIT)' \
	-X '$(MODULE_PATH)/pkg/version.BuildDate=$(BUILD_DATE)'

# 目录
OUTPUT_DIR := _output
BIN_DIR := $(OUTPUT_DIR)/platforms/linux/amd64
BINS ?= $(shell find cmd -maxdepth 1 -mindepth 1 -type d | sed 's|cmd/||')

# 默认目标
.DEFAULT_GOAL := help

.PHONY: help
help: ## 显示帮助信息
	@echo "可用的 Make 目标:"
	@awk 'BEGIN {FS = ":.*##"; printf "\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

##@ 开发

.PHONY: tidy
tidy: ## 整理 go.mod
	@echo "==> Tidying go.mod..."
	@go mod tidy

.PHONY: fmt
fmt: ## 格式化代码
	@echo "==> Formatting code..."
	@gofmt -s -w .

.PHONY: vet
vet: ## 运行 go vet
	@echo "==> Running go vet..."
	@go vet ./...

.PHONY: lint
lint: ## 运行 golangci-lint
	@echo "==> Running golangci-lint..."
	@golangci-lint run ./...

.PHONY: test
test: ## 运行测试
	@echo "==> Running tests..."
	@go test -race -cover ./...

.PHONY: test-coverage
test-coverage: ## 运行测试并生成覆盖率报告
	@echo "==> Running tests with coverage..."
	@go test -race -coverprofile=coverage.out -covermode=atomic ./...
	@go tool cover -html=coverage.out -o coverage.html
	@echo "Coverage report: coverage.html"

##@ 构建

.PHONY: build
build: tidy ## 编译所有二进制文件
	@echo "==> Building binaries..."
	@for bin in $(BINS); do \
		echo "Building $$bin..."; \
		CGO_ENABLED=0 go build -ldflags "$(LDFLAGS)" -o $(BIN_DIR)/$$bin ./cmd/$$bin; \
	done
	@echo "Build complete: $(BIN_DIR)"

.PHONY: clean
clean: ## 清理构建产物
	@echo "==> Cleaning..."
	@rm -rf $(OUTPUT_DIR)
	@rm -f coverage.out coverage.html

##@ Wire

.PHONY: wire
wire: ## 生成 Wire 依赖注入代码
	@echo "==> Generating wire..."
	@cd internal/apiserver && wire

##@ 运行

.PHONY: run
run: ## 运行主程序
	@echo "==> Running $(PROJECT_NAME)-apiserver..."
	@go run ./cmd/$(PROJECT_NAME)-apiserver

.PHONY: dev
dev: ## 开发模式运行（带热重载）
	@echo "==> Running in dev mode..."
	@air

##@ Docker

.PHONY: image
image: ## 构建 Docker 镜像
	@echo "==> Building Docker image..."
	@docker build -t $(PROJECT_NAME):$(VERSION) .

##@ 其他

.PHONY: tools
tools: ## 安装开发工具
	@echo "==> Installing tools..."
	@go install github.com/google/wire/cmd/wire@latest
	@go install github.com/golangci/golangci-lint/cmd/golangci-lint@latest
	@go install google.golang.org/protobuf/cmd/protoc-gen-go@latest
	@go install google.golang.org/grpc/cmd/protoc-gen-go-grpc@latest

.PHONY: swagger
swagger: ## 生成 Swagger 文档
	@echo "==> Generating swagger docs..."
	@swag init -g cmd/$(PROJECT_NAME)-apiserver/main.go -o api/openapi

.PHONY: proto
proto: ## 生成 protobuf 代码
	@echo "==> Generating protobuf code..."
	@protoc --go_out=. --go_opt=paths=source_relative \
		--go-grpc_out=. --go-grpc_opt=paths=source_relative \
		api/protobuf-spec/*.proto
EOF

# 4. 创建 main.go
echo "📄 创建主程序..."
cat > cmd/"$PROJECT_NAME"-apiserver/main.go <<EOF
package main

import (
	"context"
	"fmt"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/spf13/cobra"
	"github.com/spf13/viper"
	"go.uber.org/zap"

	"$MODULE_PATH/internal/apiserver"
	"$MODULE_PATH/internal/pkg/log"
)

var cfgFile string

func main() {
	cmd := &cobra.Command{
		Use:   "$PROJECT_NAME-apiserver",
		Short: "$PROJECT_NAME API Server",
		Long:  \`$PROJECT_NAME API Server - 基于 Go + Gin + GORM 构建\`,
		Run:   run,
	}

	cmd.PersistentFlags().StringVar(&cfgFile, "config", "", "配置文件路径 (默认: ./configs/$PROJECT_NAME-apiserver.yaml)")
	cmd.PersistentFlags().String("server.address", ":8080", "HTTP 服务监听地址")
	cmd.PersistentFlags().String("server.mode", "debug", "服务运行模式 (debug/release)")

	viper.BindPFlag("server.address", cmd.PersistentFlags().Lookup("server.address"))
	viper.BindPFlag("server.mode", cmd.PersistentFlags().Lookup("server.mode"))

	cobra.OnInitialize(initConfig)

	if err := cmd.Execute(); err != nil {
		fmt.Fprintf(os.Stderr, "执行命令失败: %v\n", err)
		os.Exit(1)
	}
}

func initConfig() {
	if cfgFile != "" {
		viper.SetConfigFile(cfgFile)
	} else {
		viper.AddConfigPath("./configs")
		viper.SetConfigName("$PROJECT_NAME-apiserver")
		viper.SetConfigType("yaml")
	}

	viper.AutomaticEnv()

	if err := viper.ReadInConfig(); err == nil {
		fmt.Println("使用配置文件:", viper.ConfigFileUsed())
	}
}

func run(cmd *cobra.Command, args []string) {
	// 初始化日志
	log.Init(&log.Options{
		Level:            "info",
		Format:           "json",
		EnableColor:      false,
		EnableCaller:     true,
		OutputPaths:      []string{"stdout"},
		ErrorOutputPaths: []string{"stderr"},
	})
	defer log.Sync()

	// 初始化应用
	app, cleanup, err := apiserver.NewApp()
	if err != nil {
		log.Fatalw("初始化应用失败", "error", err)
	}
	defer cleanup()

	// 设置 Gin 模式
	gin.SetMode(viper.GetString("server.mode"))

	// 创建 HTTP 服务器
	srv := &http.Server{
		Addr:    viper.GetString("server.address"),
		Handler: app.Router,
	}

	// 启动服务器
	go func() {
		log.Infow("启动 HTTP 服务器", "address", srv.Addr)
		if err := srv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			log.Fatalw("HTTP 服务器启动失败", "error", err)
		}
	}()

	// 优雅关停
	quit := make(chan os.Signal, 1)
	signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
	<-quit

	log.Info("正在关闭服务器...")

	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	if err := srv.Shutdown(ctx); err != nil {
		log.Fatalw("服务器强制关闭", "error", err)
	}

	log.Info("服务器已关闭")
}
EOF

# 5. 创建应用初始化文件
echo "📄 创建应用初始化..."
cat > internal/apiserver/app.go <<EOF
package apiserver

import (
	"github.com/gin-gonic/gin"

	v1 "$MODULE_PATH/internal/apiserver/handler/v1"
	"$MODULE_PATH/internal/apiserver/store"
	"$MODULE_PATH/internal/pkg/log"
)

// App 应用实例
type App struct {
	Router *gin.Engine
}

// NewApp 创建应用实例
func NewApp() (*App, func(), error) {
	// 初始化数据库（这里使用内存数据库示例）
	ds, err := store.NewMemoryStore()
	if err != nil {
		return nil, nil, err
	}

	// 创建路由
	router := gin.New()
	router.Use(gin.Logger())
	router.Use(gin.Recovery())

	// 健康检查
	router.GET("/healthz", func(c *gin.Context) {
		c.JSON(200, gin.H{"status": "ok"})
	})

	// API 路由组
	apiV1 := router.Group("/v1")
	{
		// 用户路由
		userHandler := v1.NewUserHandler(ds)
		apiV1.POST("/users", userHandler.Create)
		apiV1.GET("/users/:id", userHandler.Get)
		apiV1.GET("/users", userHandler.List)
		apiV1.PUT("/users/:id", userHandler.Update)
		apiV1.DELETE("/users/:id", userHandler.Delete)
	}

	cleanup := func() {
		log.Info("清理资源...")
		// 这里添加清理逻辑，例如关闭数据库连接
	}

	return &App{Router: router}, cleanup, nil
}
EOF

# 6. 创建配置文件
echo "⚙️  创建配置文件..."
cat > configs/"$PROJECT_NAME"-apiserver.yaml <<EOF
# $PROJECT_NAME API Server 配置文件

server:
  address: :8080        # HTTP 服务监听地址
  mode: debug           # 运行模式: debug, release

database:
  type: memory          # 数据库类型: memory, mysql
  host: localhost
  port: 3306
  username: root
  password: ""
  database: $PROJECT_NAME
  max-idle-connections: 10
  max-open-connections: 100
  max-connection-lifetime: 10m

log:
  level: info           # 日志级别: debug, info, warn, error
  format: json          # 日志格式: json, console
  enable-color: false
  enable-caller: true
  output-paths:
    - stdout
  error-output-paths:
    - stderr

jwt:
  secret: "your-secret-key-change-this-in-production"
  timeout: 24h

casbin:
  model-path: ./configs/casbin_model.conf
EOF

# 7. 创建 Store 接口
echo "📄 创建 Store 层..."
cat > internal/apiserver/store/store.go <<EOF
package store

import (
	"context"

	"$MODULE_PATH/internal/apiserver/model"
)

// IStore 定义数据存储接口
type IStore interface {
	User() UserStore
	// 在这里添加其他资源的 Store
}

// UserStore 定义用户数据操作接口
type UserStore interface {
	Create(ctx context.Context, user *model.UserM) error
	Get(ctx context.Context, id string) (*model.UserM, error)
	List(ctx context.Context, offset, limit int) (int64, []*model.UserM, error)
	Update(ctx context.Context, user *model.UserM) error
	Delete(ctx context.Context, id string) error
}
EOF

# 8. 创建内存数据库实现（示例）
cat > internal/apiserver/store/memory.go <<EOF
package store

import (
	"context"
	"fmt"
	"sync"

	"$MODULE_PATH/internal/apiserver/model"
)

var _ IStore = (*memoryStore)(nil)

// memoryStore 内存数据库实现
type memoryStore struct {
	users *memoryUserStore
}

// NewMemoryStore 创建内存数据库实例
func NewMemoryStore() (IStore, error) {
	return &memoryStore{
		users: &memoryUserStore{
			data: make(map[string]*model.UserM),
		},
	}, nil
}

func (s *memoryStore) User() UserStore {
	return s.users
}

// memoryUserStore 用户内存存储实现
type memoryUserStore struct {
	mu   sync.RWMutex
	data map[string]*model.UserM
}

func (s *memoryUserStore) Create(ctx context.Context, user *model.UserM) error {
	s.mu.Lock()
	defer s.mu.Unlock()

	if _, exists := s.data[user.UserID]; exists {
		return fmt.Errorf("user already exists")
	}

	s.data[user.UserID] = user
	return nil
}

func (s *memoryUserStore) Get(ctx context.Context, id string) (*model.UserM, error) {
	s.mu.RLock()
	defer s.mu.RUnlock()

	user, exists := s.data[id]
	if !exists {
		return nil, fmt.Errorf("user not found")
	}

	return user, nil
}

func (s *memoryUserStore) List(ctx context.Context, offset, limit int) (int64, []*model.UserM, error) {
	s.mu.RLock()
	defer s.mu.RUnlock()

	count := int64(len(s.data))
	users := make([]*model.UserM, 0, len(s.data))

	for _, user := range s.data {
		users = append(users, user)
	}

	// 简单的分页
	start := offset
	end := offset + limit
	if start > len(users) {
		start = len(users)
	}
	if end > len(users) {
		end = len(users)
	}

	return count, users[start:end], nil
}

func (s *memoryUserStore) Update(ctx context.Context, user *model.UserM) error {
	s.mu.Lock()
	defer s.mu.Unlock()

	if _, exists := s.data[user.UserID]; !exists {
		return fmt.Errorf("user not found")
	}

	s.data[user.UserID] = user
	return nil
}

func (s *memoryUserStore) Delete(ctx context.Context, id string) error {
	s.mu.Lock()
	defer s.mu.Unlock()

	if _, exists := s.data[id]; !exists {
		return fmt.Errorf("user not found")
	}

	delete(s.data, id)
	return nil
}
EOF

# 9. 创建 Model
echo "📄 创建 Model 层..."
cat > internal/apiserver/model/user.go <<EOF
package model

import (
	"time"
)

// UserM 用户数据模型
type UserM struct {
	ID        int64     \`gorm:"column:id;primary_key;AUTO_INCREMENT" json:"id"\`
	UserID    string    \`gorm:"column:userID;type:varchar(64);not null;uniqueIndex:idx_userID" json:"userID"\`
	Username  string    \`gorm:"column:username;type:varchar(64);not null;uniqueIndex:idx_username" json:"username"\`
	Password  string    \`gorm:"column:password;type:varchar(255);not null" json:"-"\`
	Nickname  string    \`gorm:"column:nickname;type:varchar(64)" json:"nickname"\`
	Email     string    \`gorm:"column:email;type:varchar(128)" json:"email"\`
	Phone     string    \`gorm:"column:phone;type:varchar(20)" json:"phone"\`
	CreatedAt time.Time \`gorm:"column:createdAt" json:"createdAt"\`
	UpdatedAt time.Time \`gorm:"column:updatedAt" json:"updatedAt"\`
}

// TableName 指定表名
func (u *UserM) TableName() string {
	return "user"
}
EOF

# 10. 创建 Handler
echo "📄 创建 Handler 层..."
cat > internal/apiserver/handler/v1/user.go <<EOF
package v1

import (
	"net/http"
	"strconv"

	"github.com/gin-gonic/gin"
	"github.com/google/uuid"

	"$MODULE_PATH/internal/apiserver/model"
	"$MODULE_PATH/internal/apiserver/store"
)

// UserHandler 用户处理器
type UserHandler struct {
	store store.IStore
}

// NewUserHandler 创建用户处理器
func NewUserHandler(store store.IStore) *UserHandler {
	return &UserHandler{store: store}
}

// CreateUserRequest 创建用户请求
type CreateUserRequest struct {
	Username string \`json:"username" binding:"required"\`
	Password string \`json:"password" binding:"required"\`
	Nickname string \`json:"nickname"\`
	Email    string \`json:"email"\`
	Phone    string \`json:"phone"\`
}

// Create 创建用户
func (h *UserHandler) Create(c *gin.Context) {
	var req CreateUserRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	user := &model.UserM{
		UserID:   uuid.New().String(),
		Username: req.Username,
		Password: req.Password, // TODO: 加密密码
		Nickname: req.Nickname,
		Email:    req.Email,
		Phone:    req.Phone,
	}

	if err := h.store.User().Create(c.Request.Context(), user); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusCreated, gin.H{"userID": user.UserID})
}

// Get 获取用户详情
func (h *UserHandler) Get(c *gin.Context) {
	id := c.Param("id")

	user, err := h.store.User().Get(c.Request.Context(), id)
	if err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "user not found"})
		return
	}

	c.JSON(http.StatusOK, user)
}

// List 获取用户列表
func (h *UserHandler) List(c *gin.Context) {
	offset, _ := strconv.Atoi(c.DefaultQuery("offset", "0"))
	limit, _ := strconv.Atoi(c.DefaultQuery("limit", "10"))

	count, users, err := h.store.User().List(c.Request.Context(), offset, limit)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"total": count,
		"items": users,
	})
}

// UpdateUserRequest 更新用户请求
type UpdateUserRequest struct {
	Nickname *string \`json:"nickname"\`
	Email    *string \`json:"email"\`
	Phone    *string \`json:"phone"\`
}

// Update 更新用户
func (h *UserHandler) Update(c *gin.Context) {
	id := c.Param("id")

	var req UpdateUserRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	user, err := h.store.User().Get(c.Request.Context(), id)
	if err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "user not found"})
		return
	}

	if req.Nickname != nil {
		user.Nickname = *req.Nickname
	}
	if req.Email != nil {
		user.Email = *req.Email
	}
	if req.Phone != nil {
		user.Phone = *req.Phone
	}

	if err := h.store.User().Update(c.Request.Context(), user); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, gin.H{"message": "success"})
}

// Delete 删除用户
func (h *UserHandler) Delete(c *gin.Context) {
	id := c.Param("id")

	if err := h.store.User().Delete(c.Request.Context(), id); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, gin.H{"message": "success"})
}
EOF

# 11. 创建日志包
echo "📄 创建日志包..."
cat > internal/pkg/log/log.go <<EOF
package log

import (
	"go.uber.org/zap"
	"go.uber.org/zap/zapcore"
)

// Options 日志配置选项
type Options struct {
	Level            string
	Format           string
	EnableColor      bool
	EnableCaller     bool
	OutputPaths      []string
	ErrorOutputPaths []string
}

var logger *zap.Logger

// Init 初始化日志
func Init(opts *Options) {
	var level zapcore.Level
	if err := level.UnmarshalText([]byte(opts.Level)); err != nil {
		level = zapcore.InfoLevel
	}

	config := zap.Config{
		Level:            zap.NewAtomicLevelAt(level),
		Development:      false,
		Encoding:         opts.Format,
		EncoderConfig:    zapcore.EncoderConfig{
			TimeKey:        "timestamp",
			LevelKey:       "level",
			NameKey:        "logger",
			CallerKey:      "caller",
			MessageKey:     "message",
			StacktraceKey:  "stacktrace",
			LineEnding:     zapcore.DefaultLineEnding,
			EncodeLevel:    zapcore.LowercaseLevelEncoder,
			EncodeTime:     zapcore.ISO8601TimeEncoder,
			EncodeDuration: zapcore.SecondsDurationEncoder,
			EncodeCaller:   zapcore.ShortCallerEncoder,
		},
		OutputPaths:      opts.OutputPaths,
		ErrorOutputPaths: opts.ErrorOutputPaths,
	}

	var err error
	logger, err = config.Build(zap.AddCallerSkip(1))
	if err != nil {
		panic(err)
	}
}

// Sync 刷新日志缓冲
func Sync() {
	_ = logger.Sync()
}

// Info 记录 info 级别日志
func Info(msg string, fields ...zap.Field) {
	logger.Info(msg, fields...)
}

// Infow 记录 info 级别日志（键值对）
func Infow(msg string, keysAndValues ...interface{}) {
	logger.Sugar().Infow(msg, keysAndValues...)
}

// Error 记录 error 级别日志
func Error(msg string, fields ...zap.Field) {
	logger.Error(msg, fields...)
}

// Errorw 记录 error 级别日志（键值对）
func Errorw(msg string, keysAndValues ...interface{}) {
	logger.Sugar().Errorw(msg, keysAndValues...)
}

// Warn 记录 warn 级别日志
func Warn(msg string, fields ...zap.Field) {
	logger.Warn(msg, fields...)
}

// Warnw 记录 warn 级别日志（键值对）
func Warnw(msg string, keysAndValues ...interface{}) {
	logger.Sugar().Warnw(msg, keysAndValues...)
}

// Debug 记录 debug 级别日志
func Debug(msg string, fields ...zap.Field) {
	logger.Debug(msg, fields...)
}

// Debugw 记录 debug 级别日志（键值对）
func Debugw(msg string, keysAndValues ...interface{}) {
	logger.Sugar().Debugw(msg, keysAndValues...)
}

// Fatal 记录 fatal 级别日志并退出
func Fatal(msg string, fields ...zap.Field) {
	logger.Fatal(msg, fields...)
}

// Fatalw 记录 fatal 级别日志并退出（键值对）
func Fatalw(msg string, keysAndValues ...interface{}) {
	logger.Sugar().Fatalw(msg, keysAndValues...)
}
EOF

# 12. 创建 .gitignore
echo "📄 创建 .gitignore..."
cat > .gitignore <<EOF
# Binaries
_output/
*.exe
*.exe~
*.dll
*.so
*.dylib

# Test binary
*.test

# Output of the go coverage tool
*.out
coverage.html

# Dependency directories
vendor/

# Go workspace file
go.work

# IDE
.idea/
.vscode/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Logs
*.log
_output/logs/

# Config (如果包含敏感信息)
# configs/*-apiserver.yaml
EOF

# 13. 创建 README.md
echo "📄 创建 README.md..."
cat > README.md <<EOF
# $PROJECT_NAME

基于 Go + Gin + GORM 的 Web 项目

## 快速开始

\`\`\`bash
# 安装依赖
go mod tidy

# 编译
make build

# 运行
make run

# 或直接运行
go run ./cmd/$PROJECT_NAME-apiserver
\`\`\`

## 项目结构

\`\`\`
$PROJECT_NAME/
├── cmd/                           # 主应用程序
│   └── $PROJECT_NAME-apiserver/   # API 服务器
├── internal/                      # 私有应用代码
│   ├── apiserver/                 # API 服务器实现
│   │   ├── biz/v1/               # 业务逻辑层 (v1)
│   │   ├── handler/v1/           # HTTP 处理器 (v1)
│   │   ├── store/                # 数据访问层
│   │   └── model/                # 数据模型
│   └── pkg/                      # 内部共享包
├── pkg/                          # 外部可用的库
├── api/                          # API 定义文件
├── configs/                      # 配置文件
├── _output/                      # 构建输出
├── Makefile                      # Make 构建文件
└── go.mod                        # Go 模块文件
\`\`\`

## 开发

\`\`\`bash
# 格式化代码
make fmt

# 代码检查
make lint

# 运行测试
make test

# 测试覆盖率
make test-coverage
\`\`\`

## API 文档

启动服务器后访问：

- API 端点: http://localhost:8080
- 健康检查: http://localhost:8080/healthz

## License

MIT
EOF

echo ""
echo "✅ 项目初始化完成！"
echo ""
echo "📂 项目目录: $PROJECT_NAME"
echo ""
echo "🚀 下一步操作："
echo "   cd $PROJECT_NAME"
echo "   go mod tidy          # 安装依赖"
echo "   make build           # 编译项目"
echo "   make run             # 运行服务"
echo ""
echo "📖 更多帮助："
echo "   make help            # 查看所有可用命令"
echo ""

---
name: golang-best-practices
description: 当用户需要创建 Golang 项目、构建 Go 应用、组织 Go 代码结构时使用。触发词：Golang、Go 项目、Go 应用、Go 架构、Go 开发
---

# Golang 最佳实践 Skill

这个 skill 基于生产环境验证的 Golang 最佳实践（onex 和 miniblog 项目），帮助你构建高质量、易维护、可扩展的 Go 应用。

## 📋 开发工作流

关于通用的软件开发流程（需求分析、技术设计、代码审查、测试策略、项目管理等），请参考 **development-workflow skill**。

本文档专注于 **Golang 特定** 的开发实践，包括：
- Golang 项目结构和标准布局
- Clean Architecture 实现
- Wire 依赖注入
- 错误处理和日志规范
- Gin 框架使用
- GORM 最佳实践
- 性能优化技巧

## 核心原则

1. **清晰架构** - 分层设计，职责明确
2. **接口驱动** - 面向接口编程，便于测试和扩展
3. **依赖注入** - 使用 Wire 管理依赖
4. **标准布局** - 遵循 golang-standards/project-layout
5. **错误处理** - 规范的错误码和错误处理机制

## 项目结构

创建新 Golang 项目时，使用以下标准布局：

```
project/
├── cmd/                    # 主应用程序
│   └── myapp/
│       └── main.go        # 应用入口
├── internal/              # 私有应用和库代码
│   ├── myapp/
│   │   ├── biz/          # 业务逻辑层
│   │   │   └── v1/       # API 版本
│   │   │       ├── user/
│   │   │       └── post/
│   │   ├── handler/      # HTTP/gRPC 处理器
│   │   ├── model/        # 数据模型
│   │   ├── store/        # 数据存储层
│   │   ├── pkg/          # 应用内部包
│   │   ├── server.go     # 服务器初始化
│   │   ├── wire.go       # 依赖注入定义
│   │   └── wire_gen.go   # 生成的依赖注入代码
│   └── pkg/              # 内部共享库
│       ├── errno/        # 错误码
│       ├── log/          # 日志
│       ├── middleware/   # 中间件
│       └── contextx/     # Context 扩展
├── pkg/                   # 外部可用的库代码
│   └── api/
│       └── v1/           # API 定义（protobuf/OpenAPI）
├── api/                   # API 定义文件
│   └── openapi/
├── configs/               # 配置文件
├── deployments/           # 部署配置（K8s manifests）
├── scripts/               # 构建、安装等脚本
├── build/                 # 打包和CI
├── docs/                  # 文档
├── examples/              # 示例代码
├── Makefile              # 项目管理
├── go.mod
├── go.sum
└── README.md
```

### 目录说明

#### `/cmd` - 应用程序入口
```go
// cmd/myapp/main.go
package main

import (
    "context"
    "os"
    "os/signal"
    "syscall"

    "github.com/spf13/cobra"

    "myproject/internal/myapp"
)

func main() {
    command := &cobra.Command{
        Use:   "myapp",
        Short: "My Application",
        RunE: func(cmd *cobra.Command, args []string) error {
            return run()
        },
    }

    if err := command.Execute(); err != nil {
        os.Exit(1)
    }
}

func run() error {
    ctx, cancel := context.WithCancel(context.Background())
    defer cancel()

    // 初始化服务器
    server, cleanup, err := myapp.NewServer()
    if err != nil {
        return err
    }
    defer cleanup()

    // 优雅关闭
    ch := make(chan os.Signal, 1)
    signal.Notify(ch, syscall.SIGINT, syscall.SIGTERM)

    go func() {
        <-ch
        cancel()
    }()

    return server.Run(ctx)
}
```

#### `/internal` - 私有代码

**核心原则：** Go 编译器强制 `/internal` 目录下的代码只能被父目录导入。

**分层架构：**
```
Handler → Biz → Store → Model
  ↓       ↓      ↓       ↓
HTTP/gRPC  业务逻辑  数据访问  数据模型
```

#### `/pkg` - 公共库代码

**原则：** 只放可以被外部项目安全使用的代码。

---

## Biz 层（业务逻辑层）

### 接口定义

```go
// internal/myapp/biz/v1/user/user.go
package user

//go:generate mockgen -destination mock_user.go -package user go.uber.org/mock/mockgen myproject/internal/myapp/biz/v1/user UserBiz

import (
    "context"

    apiv1 "myproject/pkg/api/v1"
)

// UserBiz 定义用户业务逻辑接口
type UserBiz interface {
    Create(ctx context.Context, req *apiv1.CreateUserRequest) (*apiv1.CreateUserResponse, error)
    Get(ctx context.Context, req *apiv1.GetUserRequest) (*apiv1.GetUserResponse, error)
    Update(ctx context.Context, req *apiv1.UpdateUserRequest) (*apiv1.UpdateUserResponse, error)
    Delete(ctx context.Context, req *apiv1.DeleteUserRequest) (*apiv1.DeleteUserResponse, error)
    List(ctx context.Context, req *apiv1.ListUserRequest) (*apiv1.ListUserResponse, error)
}

// userBiz 实现 UserBiz 接口
type userBiz struct {
    store store.IStore
}

// NewUserBiz 创建 UserBiz 实例
func NewUserBiz(store store.IStore) UserBiz {
    return &userBiz{store: store}
}

// Create 创建用户
func (b *userBiz) Create(ctx context.Context, req *apiv1.CreateUserRequest) (*apiv1.CreateUserResponse, error) {
    // 1. 验证业务规则
    if err := b.validateCreateUser(req); err != nil {
        return nil, errno.ErrValidation.WithCause(err)
    }

    // 2. 转换为模型
    user := &model.User{
        Username: req.Username,
        Email:    req.Email,
        Password: hashPassword(req.Password),
    }

    // 3. 存储
    if err := b.store.Users().Create(ctx, user); err != nil {
        return nil, errno.ErrDatabase.WithCause(err)
    }

    // 4. 返回响应
    return &apiv1.CreateUserResponse{
        User: toAPIUser(user),
    }, nil
}
```

### 版本化设计

```
biz/
├── v1/          # 第一版 API
│   ├── user/
│   └── post/
└── v2/          # 第二版 API（兼容性变更）
    ├── user/
    └── post/
```

---

## Store 层（数据访问层）

### 接口设计

```go
// internal/myapp/store/store.go
package store

import "context"

// IStore 定义存储接口
type IStore interface {
    Users() UserStore
    Posts() PostStore
}

// UserStore 定义用户存储接口
type UserStore interface {
    Create(ctx context.Context, user *model.User) error
    Get(ctx context.Context, id uint64) (*model.User, error)
    Update(ctx context.Context, user *model.User) error
    Delete(ctx context.Context, id uint64) error
    List(ctx context.Context, opts ...Option) ([]*model.User, int64, error)
    GetByEmail(ctx context.Context, email string) (*model.User, error)
}
```

### GORM 实现

```go
// internal/myapp/store/user.go
package store

import (
    "context"
    "errors"

    "gorm.io/gorm"

    "myproject/internal/myapp/model"
    "myproject/internal/pkg/errno"
)

type users struct {
    db *gorm.DB
}

var _ UserStore = (*users)(nil)

func newUsers(db *gorm.DB) *users {
    return &users{db: db}
}

// Create 创建用户
func (u *users) Create(ctx context.Context, user *model.User) error {
    return u.db.WithContext(ctx).Create(user).Error
}

// Get 获取用户
func (u *users) Get(ctx context.Context, id uint64) (*model.User, error) {
    var user model.User
    err := u.db.WithContext(ctx).Where("id = ?", id).First(&user).Error
    if err != nil {
        if errors.Is(err, gorm.ErrRecordNotFound) {
            return nil, errno.ErrUserNotFound
        }
        return nil, err
    }
    return &user, nil
}

// List 列出用户
func (u *users) List(ctx context.Context, opts ...Option) ([]*model.User, int64, error) {
    o := NewOptions(opts...)

    var users []*model.User
    var total int64

    // 查询总数
    if err := u.db.WithContext(ctx).Model(&model.User{}).Count(&total).Error; err != nil {
        return nil, 0, err
    }

    // 分页查询
    db := u.db.WithContext(ctx)
    if o.Offset > 0 {
        db = db.Offset(o.Offset)
    }
    if o.Limit > 0 {
        db = db.Limit(o.Limit)
    }

    if err := db.Order("id desc").Find(&users).Error; err != nil {
        return nil, 0, err
    }

    return users, total, nil
}
```

### 查询选项模式

```go
// internal/myapp/store/options.go
package store

// Options 定义查询选项
type Options struct {
    Offset int
    Limit  int
}

// Option 定义选项函数
type Option func(*Options)

// NewOptions 创建选项
func NewOptions(opts ...Option) *Options {
    o := &Options{
        Limit: 20,
    }
    for _, opt := range opts {
        opt(o)
    }
    return o
}

// WithOffset 设置偏移量
func WithOffset(offset int) Option {
    return func(o *Options) {
        o.Offset = offset
    }
}

// WithLimit 设置限制
func WithLimit(limit int) Option {
    return func(o *Options) {
        o.Limit = limit
    }
}
```

---

## Handler 层（HTTP/gRPC 处理器）

### HTTP Handler (Gin)

```go
// internal/myapp/handler/user.go
package handler

import (
    "github.com/gin-gonic/gin"

    "myproject/internal/myapp/biz/v1/user"
    "myproject/internal/pkg/errno"
    "myproject/internal/pkg/log"
    apiv1 "myproject/pkg/api/v1"
)

// UserHandler 用户处理器
type UserHandler struct {
    biz user.UserBiz
}

// NewUserHandler 创建用户处理器
func NewUserHandler(biz user.UserBiz) *UserHandler {
    return &UserHandler{biz: biz}
}

// Create 创建用户
func (h *UserHandler) Create(c *gin.Context) {
    var req apiv1.CreateUserRequest
    if err := c.ShouldBindJSON(&req); err != nil {
        WriteResponse(c, errno.ErrBind.WithCause(err), nil)
        return
    }

    resp, err := h.biz.Create(c.Request.Context(), &req)
    WriteResponse(c, err, resp)
}

// Get 获取用户
func (h *UserHandler) Get(c *gin.Context) {
    req := &apiv1.GetUserRequest{
        Username: c.Param("username"),
    }

    resp, err := h.biz.Get(c.Request.Context(), req)
    WriteResponse(c, err, resp)
}

// List 列出用户
func (h *UserHandler) List(c *gin.Context) {
    var req apiv1.ListUserRequest
    if err := c.ShouldBindQuery(&req); err != nil {
        WriteResponse(c, errno.ErrBind.WithCause(err), nil)
        return
    }

    resp, err := h.biz.List(c.Request.Context(), &req)
    WriteResponse(c, err, resp)
}
```

### 统一响应处理

```go
// internal/myapp/handler/response.go
package handler

import (
    "net/http"

    "github.com/gin-gonic/gin"

    "myproject/internal/pkg/errno"
)

// Response 定义统一响应格式
type Response struct {
    Code    int         `json:"code"`
    Message string      `json:"message"`
    Data    interface{} `json:"data,omitempty"`
}

// WriteResponse 写入响应
func WriteResponse(c *gin.Context, err error, data interface{}) {
    if err != nil {
        log.Errorw("Handler error", "err", err)

        // 转换为错误码
        coder := errno.ParseCoder(err)
        c.JSON(coder.HTTPStatus(), Response{
            Code:    coder.Code(),
            Message: coder.String(),
        })
        return
    }

    c.JSON(http.StatusOK, Response{
        Code:    0,
        Message: "success",
        Data:    data,
    })
}
```

---

## Model 层（数据模型）

```go
// internal/myapp/model/user.go
package model

import (
    "time"

    "gorm.io/gorm"
)

// User 用户模型
type User struct {
    ID        uint64         `gorm:"column:id;primary_key;auto_increment"`
    Username  string         `gorm:"column:username;type:varchar(255);not null;uniqueIndex:idx_username"`
    Email     string         `gorm:"column:email;type:varchar(255);not null;uniqueIndex:idx_email"`
    Password  string         `gorm:"column:password;type:varchar(255);not null"`
    Nickname  string         `gorm:"column:nickname;type:varchar(255)"`
    Phone     string         `gorm:"column:phone;type:varchar(20)"`
    IsAdmin   bool           `gorm:"column:is_admin;default:false"`
    CreatedAt time.Time      `gorm:"column:created_at"`
    UpdatedAt time.Time      `gorm:"column:updated_at"`
    DeletedAt gorm.DeletedAt `gorm:"column:deleted_at;index"`
}

// TableName 指定表名
func (u *User) TableName() string {
    return "users"
}

// BeforeCreate GORM 钩子：创建前
func (u *User) BeforeCreate(tx *gorm.DB) error {
    // 自动设置时间
    now := time.Now()
    u.CreatedAt = now
    u.UpdatedAt = now
    return nil
}

// BeforeUpdate GORM 钩子：更新前
func (u *User) BeforeUpdate(tx *gorm.DB) error {
    u.UpdatedAt = time.Now()
    return nil
}
```

---

## 依赖注入（Wire）

### Wire 配置

```go
// internal/myapp/wire.go
//go:build wireinject
// +build wireinject

package myapp

import (
    "github.com/google/wire"
    "gorm.io/gorm"

    "myproject/internal/myapp/biz/v1/user"
    "myproject/internal/myapp/handler"
    "myproject/internal/myapp/store"
)

// NewServer 使用 Wire 注入依赖
func NewServer() (*Server, func(), error) {
    panic(wire.Build(
        // 数据库
        provideDB,

        // Store
        store.NewStore,

        // Biz
        user.NewUserBiz,

        // Handler
        handler.NewUserHandler,

        // Server
        NewServerConfig,
        NewServer,
    ))
}

// provideDB 提供数据库连接
func provideDB() (*gorm.DB, func(), error) {
    db, err := gorm.Open(/* ... */)
    if err != nil {
        return nil, nil, err
    }

    cleanup := func() {
        sqlDB, _ := db.DB()
        _ = sqlDB.Close()
    }

    return db, cleanup, nil
}
```

生成代码：
```bash
$ wire gen ./internal/myapp
```

---

## 错误处理

### 错误码设计

```go
// internal/pkg/errno/code.go
package errno

import (
    "fmt"
    "net/http"
)

// Coder 定义错误码接口
type Coder interface {
    HTTPStatus() int
    String() string
    Code() int
}

type coder struct {
    httpStatus int
    code       int
    message    string
    err        error
}

func (c *coder) HTTPStatus() int {
    return c.httpStatus
}

func (c *coder) String() string {
    if c.err != nil {
        return fmt.Sprintf("%s: %v", c.message, c.err)
    }
    return c.message
}

func (c *coder) Code() int {
    return c.code
}

func (c *coder) WithCause(err error) Coder {
    newCoder := *c
    newCoder.err = err
    return &newCoder
}

// 预定义错误码
var (
    // 通用错误码 (10000-10999)
    OK                  = &coder{http.StatusOK, 0, "success", nil}
    ErrInternalServer   = &coder{http.StatusInternalServerError, 10001, "Internal server error", nil}
    ErrBind             = &coder{http.StatusBadRequest, 10002, "Error occurred while binding request", nil}
    ErrValidation       = &coder{http.StatusBadRequest, 10003, "Validation failed", nil}
    ErrDatabase         = &coder{http.StatusInternalServerError, 10004, "Database error", nil}

    // 用户相关错误 (20000-20999)
    ErrUserNotFound     = &coder{http.StatusNotFound, 20001, "User not found", nil}
    ErrUserAlreadyExist = &coder{http.StatusConflict, 20002, "User already exists", nil}
    ErrPasswordIncorrect = &coder{http.StatusUnauthorized, 20003, "Password is incorrect", nil}

    // 授权相关错误 (30000-30999)
    ErrTokenInvalid     = &coder{http.StatusUnauthorized, 30001, "Token is invalid", nil}
    ErrTokenExpired     = &coder{http.StatusUnauthorized, 30002, "Token is expired", nil}
)

// ParseCoder 解析错误为错误码
func ParseCoder(err error) Coder {
    if err == nil {
        return OK
    }

    if coder, ok := err.(Coder); ok {
        return coder
    }

    return ErrInternalServer.WithCause(err)
}
```

---

## 中间件

### 请求 ID 中间件

```go
// internal/pkg/middleware/requestid.go
package middleware

import (
    "github.com/gin-gonic/gin"
    "github.com/google/uuid"

    "myproject/internal/pkg/contextx"
)

// RequestID 请求 ID 中间件
func RequestID() gin.HandlerFunc {
    return func(c *gin.Context) {
        requestID := c.GetHeader(contextx.KeyRequestID)
        if requestID == "" {
            requestID = uuid.New().String()
        }

        c.Set(contextx.KeyRequestID, requestID)
        c.Header(contextx.KeyRequestID, requestID)

        c.Next()
    }
}
```

### 日志中间件

```go
// internal/pkg/middleware/logger.go
package middleware

import (
    "time"

    "github.com/gin-gonic/gin"

    "myproject/internal/pkg/log"
)

// Logger 日志中间件
func Logger() gin.HandlerFunc {
    return func(c *gin.Context) {
        start := time.Now()
        path := c.Request.URL.Path
        query := c.Request.URL.RawQuery

        c.Next()

        cost := time.Since(start)

        log.Infow("HTTP request",
            "method", c.Request.Method,
            "path", path,
            "query", query,
            "status", c.Writer.Status(),
            "cost", cost.Milliseconds(),
            "ip", c.ClientIP(),
            "user-agent", c.Request.UserAgent(),
        )
    }
}
```

### 认证中间件

```go
// internal/pkg/middleware/authn.go
package middleware

import (
    "github.com/gin-gonic/gin"

    "myproject/internal/pkg/contextx"
    "myproject/internal/pkg/errno"
    "myproject/internal/pkg/token"
)

// Authn 认证中间件
func Authn() gin.HandlerFunc {
    return func(c *gin.Context) {
        tokenString := c.GetHeader("Authorization")
        if tokenString == "" {
            c.AbortWithStatusJSON(401, errno.ErrTokenInvalid)
            return
        }

        // 解析 token
        claims, err := token.Parse(tokenString)
        if err != nil {
            c.AbortWithStatusJSON(401, errno.ErrTokenInvalid.WithCause(err))
            return
        }

        // 设置用户信息到 context
        c.Set(contextx.KeyUserID, claims.UserID)
        c.Set(contextx.KeyUsername, claims.Username)

        c.Next()
    }
}
```

---

## 配置管理（Viper）

```go
// internal/myapp/config.go
package myapp

import (
    "github.com/spf13/viper"
)

// Config 应用配置
type Config struct {
    Server   ServerConfig   `mapstructure:"server"`
    Database DatabaseConfig `mapstructure:"database"`
    Log      LogConfig      `mapstructure:"log"`
    JWT      JWTConfig      `mapstructure:"jwt"`
}

// ServerConfig 服务器配置
type ServerConfig struct {
    Mode         string `mapstructure:"mode"`
    Host         string `mapstructure:"host"`
    Port         int    `mapstructure:"port"`
    ReadTimeout  int    `mapstructure:"read-timeout"`
    WriteTimeout int    `mapstructure:"write-timeout"`
}

// DatabaseConfig 数据库配置
type DatabaseConfig struct {
    Host     string `mapstructure:"host"`
    Port     int    `mapstructure:"port"`
    Username string `mapstructure:"username"`
    Password string `mapstructure:"password"`
    Database string `mapstructure:"database"`
}

// LoadConfig 加载配置
func LoadConfig(configFile string) (*Config, error) {
    v := viper.New()
    v.SetConfigFile(configFile)
    v.SetConfigType("yaml")

    if err := v.ReadInConfig(); err != nil {
        return nil, err
    }

    var config Config
    if err := v.Unmarshal(&config); err != nil {
        return nil, err
    }

    return &config, nil
}
```

配置文件示例（configs/app.yaml）：
```yaml
server:
  mode: release
  host: 0.0.0.0
  port: 8080
  read-timeout: 30
  write-timeout: 30

database:
  host: localhost
  port: 3306
  username: root
  password: password
  database: myapp

log:
  level: info
  format: json
  output-paths:
    - stdout
    - /var/log/myapp.log

jwt:
  secret: your-secret-key
  timeout: 24h
```

---

## 日志（Zap）

```go
// internal/pkg/log/log.go
package log

import (
    "go.uber.org/zap"
    "go.uber.org/zap/zapcore"
)

var logger *zap.SugaredLogger

// Init 初始化日志
func Init(level string, format string, outputPaths []string) error {
    var zapLevel zapcore.Level
    if err := zapLevel.UnmarshalText([]byte(level)); err != nil {
        return err
    }

    encoderConfig := zapcore.EncoderConfig{
        TimeKey:        "time",
        LevelKey:       "level",
        NameKey:        "logger",
        CallerKey:      "caller",
        MessageKey:     "msg",
        StacktraceKey:  "stacktrace",
        LineEnding:     zapcore.DefaultLineEnding,
        EncodeLevel:    zapcore.LowercaseLevelEncoder,
        EncodeTime:     zapcore.ISO8601TimeEncoder,
        EncodeDuration: zapcore.SecondsDurationEncoder,
        EncodeCaller:   zapcore.ShortCallerEncoder,
    }

    var encoder zapcore.Encoder
    if format == "json" {
        encoder = zapcore.NewJSONEncoder(encoderConfig)
    } else {
        encoder = zapcore.NewConsoleEncoder(encoderConfig)
    }

    config := zap.Config{
        Level:            zap.NewAtomicLevelAt(zapLevel),
        Encoding:         format,
        EncoderConfig:    encoderConfig,
        OutputPaths:      outputPaths,
        ErrorOutputPaths: []string{"stderr"},
    }

    zapLogger, err := config.Build()
    if err != nil {
        return err
    }

    logger = zapLogger.Sugar()
    return nil
}

// 日志方法
func Debug(args ...interface{})                    { logger.Debug(args...) }
func Debugf(template string, args ...interface{})  { logger.Debugf(template, args...) }
func Debugw(msg string, keysAndValues ...interface{}) { logger.Debugw(msg, keysAndValues...) }

func Info(args ...interface{})                     { logger.Info(args...) }
func Infof(template string, args ...interface{})   { logger.Infof(template, args...) }
func Infow(msg string, keysAndValues ...interface{}) { logger.Infow(msg, keysAndValues...) }

func Warn(args ...interface{})                     { logger.Warn(args...) }
func Warnf(template string, args ...interface{})   { logger.Warnf(template, args...) }
func Warnw(msg string, keysAndValues ...interface{}) { logger.Warnw(msg, keysAndValues...) }

func Error(args ...interface{})                    { logger.Error(args...) }
func Errorf(template string, args ...interface{})  { logger.Errorf(template, args...) }
func Errorw(msg string, keysAndValues ...interface{}) { logger.Errorw(msg, keysAndValues...) }
```

---

## Makefile 管理

```makefile
# Makefile
.PHONY: all build clean test coverage lint help

# 项目信息
PROJECT_NAME := myapp
VERSION := $(shell git describe --tags --always --dirty)
BUILD_TIME := $(shell date -u '+%Y-%m-%d_%H:%M:%S')
GIT_COMMIT := $(shell git rev-parse HEAD)

# Go 参数
GOCMD := go
GOBUILD := $(GOCMD) build
GOCLEAN := $(GOCMD) clean
GOTEST := $(GOCMD) test
GOGET := $(GOCMD) get
GOMOD := $(GOCMD) mod

# 构建参数
LDFLAGS := -X main.Version=$(VERSION) \
           -X main.BuildTime=$(BUILD_TIME) \
           -X main.GitCommit=$(GIT_COMMIT)

# 输出目录
OUTPUT_DIR := _output
BIN_DIR := $(OUTPUT_DIR)/bin

# 所有命令
CMDS := $(shell find cmd -mindepth 1 -maxdepth 1 -type d | sed 's/cmd\///')

## all: 编译所有二进制
all: build

## build: 编译二进制文件
build:
	@echo "Building..."
	@for cmd in $(CMDS); do \
		echo "Building $$cmd..."; \
		$(GOBUILD) -ldflags "$(LDFLAGS)" -o $(BIN_DIR)/$$cmd ./cmd/$$cmd; \
	done

## clean: 清理构建产物
clean:
	@echo "Cleaning..."
	@rm -rf $(OUTPUT_DIR)
	@$(GOCLEAN)

## test: 运行测试
test:
	@echo "Running tests..."
	@$(GOTEST) -v -race ./...

## coverage: 生成测试覆盖率报告
coverage:
	@echo "Generating coverage report..."
	@$(GOTEST) -race -coverprofile=coverage.out -covermode=atomic ./...
	@$(GOCMD) tool cover -html=coverage.out -o coverage.html

## lint: 代码检查
lint:
	@echo "Running linter..."
	@golangci-lint run ./...

## wire: 生成依赖注入代码
wire:
	@echo "Generating wire code..."
	@wire gen ./internal/...

## run: 运行应用
run: build
	@echo "Running $(PROJECT_NAME)..."
	@$(BIN_DIR)/$(PROJECT_NAME)

## install-tools: 安装开发工具
install-tools:
	@echo "Installing tools..."
	@go install github.com/google/wire/cmd/wire@latest
	@go install github.com/golangci/golangci-lint/cmd/golangci-lint@latest
	@go install go.uber.org/mock/mockgen@latest

## help: 显示帮助信息
help: Makefile
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@sed -n 's/^##//p' $< | column -t -s ':' | sed -e 's/^/ /'
```

---

## 测试

### 单元测试

```go
// internal/myapp/biz/v1/user/user_test.go
package user

import (
    "context"
    "testing"

    "go.uber.org/mock/gomock"
    "github.com/stretchr/testify/assert"

    "myproject/internal/myapp/model"
    "myproject/internal/myapp/store"
    apiv1 "myproject/pkg/api/v1"
)

func TestUserBiz_Create(t *testing.T) {
    ctrl := gomock.NewController(t)
    defer ctrl.Finish()

    mockStore := store.NewMockIStore(ctrl)
    mockUserStore := store.NewMockUserStore(ctrl)

    mockStore.EXPECT().Users().Return(mockUserStore).AnyTimes()

    biz := NewUserBiz(mockStore)

    tests := []struct {
        name    string
        req     *apiv1.CreateUserRequest
        mock    func()
        wantErr bool
    }{
        {
            name: "成功创建用户",
            req: &apiv1.CreateUserRequest{
                Username: "testuser",
                Email:    "test@example.com",
                Password: "password123",
            },
            mock: func() {
                mockUserStore.EXPECT().
                    Create(gomock.Any(), gomock.Any()).
                    Return(nil)
            },
            wantErr: false,
        },
        {
            name: "用户名为空",
            req: &apiv1.CreateUserRequest{
                Username: "",
                Email:    "test@example.com",
                Password: "password123",
            },
            mock:    func() {},
            wantErr: true,
        },
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            tt.mock()

            _, err := biz.Create(context.Background(), tt.req)
            if tt.wantErr {
                assert.Error(t, err)
            } else {
                assert.NoError(t, err)
            }
        })
    }
}
```

### 性能测试

```go
// internal/myapp/biz/v1/user/user_bench_test.go
package user

import (
    "context"
    "testing"

    apiv1 "myproject/pkg/api/v1"
)

func BenchmarkUserBiz_Create(b *testing.B) {
    // 初始化
    biz := setupBiz(b)
    req := &apiv1.CreateUserRequest{
        Username: "benchuser",
        Email:    "bench@example.com",
        Password: "password123",
    }

    b.ResetTimer()
    for i := 0; i < b.N; i++ {
        _, _ = biz.Create(context.Background(), req)
    }
}
```

---

## 开发工作流

更多开发规范、流程和最佳实践，请参考：
- **[development-workflow.md](development-workflow.md)** - 开发工作流程
- **[architecture-design.md](architecture-design.md)** - 架构设计指南

---

## 快速开始清单

创建新 Golang 项目时，按以下步骤进行：

1. ✅ 创建项目结构（使用标准布局）
2. ✅ 初始化 `go.mod`
3. ✅ 设置 `Makefile`
4. ✅ 配置文件和环境变量
5. ✅ 数据库连接和迁移
6. ✅ 定义 API 接口（protobuf/OpenAPI）
7. ✅ 实现分层架构（handler → biz → store → model）
8. ✅ 配置依赖注入（Wire）
9. ✅ 添加中间件（日志、认证、恢复）
10. ✅ 错误处理和日志
11. ✅ 编写测试
12. ✅ API 文档

---

**使用此 skill 时，Claude 将：**
- 遵循 Golang 标准项目布局
- 应用分层架构设计
- 使用接口驱动开发
- 实现依赖注入（Wire）
- 规范的错误处理和日志
- 编写可测试的代码
- 遵循 Go 社区最佳实践
- 基于 onex 和 miniblog 项目的生产经验

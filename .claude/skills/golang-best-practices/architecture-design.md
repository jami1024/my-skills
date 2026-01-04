# Golang 架构设计指南

本文档基于 miniblog 和 onex 项目，总结 Go 项目的架构设计最佳实践。

## 核心架构：清晰架构（Clean Architecture）

### 架构图

```
┌──────────────────────────────────────────────────────────┐
│                    Handler Layer                         │
│              (HTTP/gRPC 入口层)                           │
│  - 参数绑定、校验                                          │
│  - 协议转换（HTTP → Go Struct）                           │
│  - 响应格式化                                              │
│  - 不包含业务逻辑                                          │
└────────────────────┬─────────────────────────────────────┘
                     │ 调用
                     ↓
┌──────────────────────────────────────────────────────────┐
│                     Biz Layer                            │
│                (业务逻辑层)                                │
│  - 业务规则实现                                            │
│  - 权限检查                                                │
│  - 事务管理                                                │
│  - 编排多个 Store 操作                                     │
└────────────────────┬─────────────────────────────────────┘
                     │ 调用
                     ↓
┌──────────────────────────────────────────────────────────┐
│                    Store Layer                           │
│                (数据访问层)                                │
│  - CRUD 操作                                              │
│  - 复杂查询组装                                            │
│  - 缓存逻辑                                                │
│  - 不包含业务逻辑                                          │
└────────────────────┬─────────────────────────────────────┘
                     │ 调用
                     ↓
┌──────────────────────────────────────────────────────────┐
│                    Model Layer                           │
│                (数据模型层)                                │
│  - 数据结构定义                                            │
│  - GORM 模型                                              │
│  - Hooks (BeforeCreate, AfterFind 等)                    │
└──────────────────────────────────────────────────────────┘
```

### 依赖规则

**核心原则：单向依赖，由外向内**

```
Handler 依赖 Biz (通过 Biz 接口)
   ↓
Biz 依赖 Store (通过 Store 接口)
   ↓
Store 依赖 Model (直接依赖结构体)
```

**禁止的依赖：**
- ❌ Handler 直接访问 Store
- ❌ Handler 直接访问 Model
- ❌ Biz 直接访问 Model（通过 Store 访问）
- ❌ 任何层的反向依赖

### 为什么这样设计？

1. **职责分离**：每一层有明确的职责，易于理解和维护
2. **可测试性**：通过接口 mock，每层可独立测试
3. **可扩展性**：替换底层实现不影响上层（如替换数据库）
4. **业务集中**：业务逻辑集中在 Biz 层，避免散落各处

## 目录结构

### 标准项目布局

```
myproject/
├── cmd/                          # 应用程序入口
│   └── myapp/
│       └── main.go               # main 函数
├── internal/                     # 私有代码（不可被其他项目导入）
│   └── myapp/
│       ├── model/                # 数据模型
│       │   ├── user.go
│       │   └── post.go
│       ├── store/                # 数据访问层
│       │   ├── store.go          # Store 接口定义
│       │   ├── user.go           # UserStore 实现
│       │   └── post.go           # PostStore 实现
│       ├── biz/                  # 业务逻辑层
│       │   ├── biz.go            # Biz 接口定义
│       │   └── v1/               # v1 版本业务逻辑
│       │       ├── user/
│       │       │   └── user.go   # UserBiz 实现
│       │       └── post/
│       │           └── post.go   # PostBiz 实现
│       ├── handler/              # HTTP/gRPC 处理器
│       │   └── v1/               # v1 版本 API
│       │       ├── user/
│       │       │   └── user.go   # UserHandler
│       │       └── post/
│       │           └── post.go   # PostHandler
│       ├── wire.go               # Wire 依赖注入配置
│       ├── wire_gen.go           # Wire 自动生成（不要手动编辑）
│       └── myapp.go              # 应用主结构体
├── pkg/                          # 公共库（可被其他项目导入）
│   ├── log/                      # 日志库
│   ├── errors/                   # 错误处理
│   ├── token/                    # JWT token
│   └── validator/                # 参数校验
├── configs/                      # 配置文件
│   └── myapp.yaml
├── scripts/                      # 脚本（构建、部署）
│   └── make-rules/
├── docs/                         # 文档
│   ├── requirements/             # 需求文档
│   ├── design/                   # 设计文档
│   └── adr/                      # 架构决策记录
├── test/                         # 额外的测试文件
├── Makefile                      # 构建脚本
├── go.mod
├── go.sum
└── README.md
```

### 目录说明

#### cmd/
应用程序入口，一个项目可能有多个应用（如 API 服务、定时任务、CLI 工具）。

```go
// cmd/myapp/main.go
func main() {
    app, cleanup, err := initApp(cfg)
    if err != nil {
        panic(err)
    }
    defer cleanup()

    app.Run()
}
```

#### internal/
私有代码，不可被其他项目 import。核心业务逻辑都在这里。

#### pkg/
公共库，可以被其他项目 import。只放通用的、无业务逻辑的工具代码。

#### configs/
配置文件，支持多环境（dev、test、prod）。

```yaml
# configs/myapp.yaml
server:
  addr: :8080
  mode: release

db:
  host: localhost
  port: 3306
  database: myapp
```

## 各层详细设计

### Model 层

**职责**：数据结构定义、数据库模型

**文件位置**：`internal/myapp/model/`

**设计原则**：
- 使用 GORM 标签定义表结构
- 包含 Hooks（如需要）
- 不包含业务逻辑

**示例**：

```go
// internal/myapp/model/user.go
package model

import (
    "time"
    "gorm.io/gorm"
)

type User struct {
    ID        int64     `gorm:"column:id;primary_key;auto_increment"`
    Username  string    `gorm:"column:username;not null;uniqueIndex:idx_username"`
    Password  string    `gorm:"column:password;not null"`
    Email     string    `gorm:"column:email;not null;index:idx_email"`
    Nickname  string    `gorm:"column:nickname"`
    CreatedAt time.Time `gorm:"column:created_at"`
    UpdatedAt time.Time `gorm:"column:updated_at"`
}

// TableName 自定义表名
func (u *User) TableName() string {
    return "users"
}

// BeforeCreate Hook 示例
func (u *User) BeforeCreate(tx *gorm.DB) error {
    // 例如：密码加密
    return nil
}
```

**GORM 标签说明**：
- `primary_key`: 主键
- `auto_increment`: 自增
- `not null`: 非空
- `uniqueIndex`: 唯一索引
- `index`: 普通索引
- `size:128`: 字段长度

### Store 层

**职责**：数据访问、CRUD 操作、复杂查询

**文件位置**：`internal/myapp/store/`

**设计原则**：
- 使用接口定义，便于测试和 mock
- 只关注数据操作，不包含业务逻辑
- 统一错误处理（将数据库错误转为业务错误）

**接口定义**：

```go
// internal/myapp/store/store.go
package store

import (
    "context"
    "myapp/internal/myapp/model"
)

// IStore 定义所有 Store 接口
type IStore interface {
    Users() UserStore
    Posts() PostStore
}

// UserStore 定义用户数据访问接口
type UserStore interface {
    Create(ctx context.Context, user *model.User) error
    Get(ctx context.Context, id int64) (*model.User, error)
    GetByUsername(ctx context.Context, username string) (*model.User, error)
    List(ctx context.Context, offset, limit int) ([]*model.User, int64, error)
    Update(ctx context.Context, user *model.User) error
    Delete(ctx context.Context, id int64) error
}
```

**实现示例**：

```go
// internal/myapp/store/user.go
package store

import (
    "context"
    "gorm.io/gorm"
    "myapp/internal/myapp/model"
    "myapp/pkg/errors"
)

type users struct {
    db *gorm.DB
}

// NewUsers 创建 UserStore 实例
func NewUsers(db *gorm.DB) UserStore {
    return &users{db: db}
}

func (u *users) Create(ctx context.Context, user *model.User) error {
    if err := u.db.WithContext(ctx).Create(user).Error; err != nil {
        return errors.WrapDatabaseError(err, "failed to create user")
    }
    return nil
}

func (u *users) Get(ctx context.Context, id int64) (*model.User, error) {
    var user model.User
    err := u.db.WithContext(ctx).Where("id = ?", id).First(&user).Error
    if err != nil {
        if errors.Is(err, gorm.ErrRecordNotFound) {
            return nil, errors.ErrUserNotFound
        }
        return nil, errors.WrapDatabaseError(err, "failed to get user")
    }
    return &user, nil
}

func (u *users) List(ctx context.Context, offset, limit int) ([]*model.User, int64, error) {
    var users []*model.User
    var count int64

    db := u.db.WithContext(ctx).Model(&model.User{})

    // 查询总数
    if err := db.Count(&count).Error; err != nil {
        return nil, 0, errors.WrapDatabaseError(err, "failed to count users")
    }

    // 查询列表
    err := db.Offset(offset).Limit(limit).Find(&users).Error
    if err != nil {
        return nil, 0, errors.WrapDatabaseError(err, "failed to list users")
    }

    return users, count, nil
}

func (u *users) Update(ctx context.Context, user *model.User) error {
    if err := u.db.WithContext(ctx).Save(user).Error; err != nil {
        return errors.WrapDatabaseError(err, "failed to update user")
    }
    return nil
}

func (u *users) Delete(ctx context.Context, id int64) error {
    err := u.db.WithContext(ctx).Where("id = ?", id).Delete(&model.User{}).Error
    if err != nil {
        return errors.WrapDatabaseError(err, "failed to delete user")
    }
    return nil
}
```

**Store 聚合**：

```go
// internal/myapp/store/datastore.go
package store

import "gorm.io/gorm"

// datastore 实现 IStore 接口
type datastore struct {
    db *gorm.DB
}

func NewStore(db *gorm.DB) IStore {
    return &datastore{db: db}
}

func (ds *datastore) Users() UserStore {
    return NewUsers(ds.db)
}

func (ds *datastore) Posts() PostStore {
    return NewPosts(ds.db)
}
```

### Biz 层

**职责**：业务逻辑、业务规则、权限检查、事务编排

**文件位置**：`internal/myapp/biz/v1/`（支持版本化）

**设计原则**：
- 使用接口定义
- 封装业务规则
- 调用 Store 层进行数据操作
- 不直接访问 Model

**接口定义**：

```go
// internal/myapp/biz/biz.go
package biz

import (
    "context"
    v1 "myapp/api/v1"
)

// IBiz 定义所有 Biz 接口
type IBiz interface {
    Users() UserBiz
    Posts() PostBiz
}

// UserBiz 定义用户业务逻辑接口
type UserBiz interface {
    Create(ctx context.Context, req *v1.CreateUserRequest) (*v1.CreateUserResponse, error)
    Get(ctx context.Context, id int64) (*v1.GetUserResponse, error)
    List(ctx context.Context, req *v1.ListUserRequest) (*v1.ListUserResponse, error)
    Update(ctx context.Context, id int64, req *v1.UpdateUserRequest) error
    Delete(ctx context.Context, id int64) error
    ChangePassword(ctx context.Context, id int64, req *v1.ChangePasswordRequest) error
}
```

**实现示例**：

```go
// internal/myapp/biz/v1/user/user.go
package user

import (
    "context"
    v1 "myapp/api/v1"
    "myapp/internal/myapp/model"
    "myapp/internal/myapp/store"
    "myapp/pkg/errors"
    "myapp/pkg/token"
    "golang.org/x/crypto/bcrypt"
)

type userBiz struct {
    ds store.IStore
}

// NewUserBiz 创建 UserBiz 实例
func NewUserBiz(ds store.IStore) biz.UserBiz {
    return &userBiz{ds: ds}
}

func (b *userBiz) Create(ctx context.Context, req *v1.CreateUserRequest) (*v1.CreateUserResponse, error) {
    // 1. 参数校验（业务规则）
    if err := b.validateCreateRequest(req); err != nil {
        return nil, err
    }

    // 2. 检查用户名是否已存在
    _, err := b.ds.Users().GetByUsername(ctx, req.Username)
    if err == nil {
        return nil, errors.ErrUserAlreadyExists
    }
    if !errors.Is(err, errors.ErrUserNotFound) {
        return nil, err
    }

    // 3. 密码加密
    hashedPassword, err := bcrypt.GenerateFromPassword([]byte(req.Password), bcrypt.DefaultCost)
    if err != nil {
        return nil, errors.Wrap(err, "failed to hash password")
    }

    // 4. 创建用户模型
    user := &model.User{
        Username: req.Username,
        Password: string(hashedPassword),
        Email:    req.Email,
        Nickname: req.Nickname,
    }

    // 5. 保存到数据库
    if err := b.ds.Users().Create(ctx, user); err != nil {
        return nil, err
    }

    // 6. 返回响应
    return &v1.CreateUserResponse{
        UserID:    user.ID,
        Username:  user.Username,
        CreatedAt: user.CreatedAt,
    }, nil
}

func (b *userBiz) validateCreateRequest(req *v1.CreateUserRequest) error {
    // 业务规则校验
    if len(req.Username) < 3 || len(req.Username) > 20 {
        return errors.New("username length must be between 3 and 20")
    }
    if len(req.Password) < 8 {
        return errors.New("password must be at least 8 characters")
    }
    // ... 更多校验
    return nil
}

func (b *userBiz) List(ctx context.Context, req *v1.ListUserRequest) (*v1.ListUserResponse, error) {
    // 计算偏移量
    offset := (req.Page - 1) * req.PageSize

    // 调用 Store 层
    users, total, err := b.ds.Users().List(ctx, offset, req.PageSize)
    if err != nil {
        return nil, err
    }

    // 转换为响应格式
    items := make([]*v1.UserInfo, 0, len(users))
    for _, user := range users {
        items = append(items, &v1.UserInfo{
            ID:        user.ID,
            Username:  user.Username,
            Email:     user.Email,
            Nickname:  user.Nickname,
            CreatedAt: user.CreatedAt,
        })
    }

    return &v1.ListUserResponse{
        Total: total,
        Items: items,
    }, nil
}

func (b *userBiz) ChangePassword(ctx context.Context, id int64, req *v1.ChangePasswordRequest) error {
    // 1. 获取用户
    user, err := b.ds.Users().Get(ctx, id)
    if err != nil {
        return err
    }

    // 2. 验证旧密码
    err = bcrypt.CompareHashAndPassword([]byte(user.Password), []byte(req.OldPassword))
    if err != nil {
        return errors.ErrInvalidPassword
    }

    // 3. 加密新密码
    hashedPassword, err := bcrypt.GenerateFromPassword([]byte(req.NewPassword), bcrypt.DefaultCost)
    if err != nil {
        return errors.Wrap(err, "failed to hash password")
    }

    // 4. 更新密码
    user.Password = string(hashedPassword)
    return b.ds.Users().Update(ctx, user)
}
```

**Biz 聚合**：

```go
// internal/myapp/biz/biz.go
package biz

import "myapp/internal/myapp/store"

type biz struct {
    ds store.IStore
}

func NewBiz(ds store.IStore) IBiz {
    return &biz{ds: ds}
}

func (b *biz) Users() UserBiz {
    return user.NewUserBiz(b.ds)
}

func (b *biz) Posts() PostBiz {
    return post.NewPostBiz(b.ds)
}
```

### Handler 层

**职责**：HTTP/gRPC 请求处理、参数绑定、响应格式化

**文件位置**：`internal/myapp/handler/v1/`

**设计原则**：
- 处理 HTTP 协议相关逻辑
- 参数绑定和校验
- 调用 Biz 层
- 不包含业务逻辑

**实现示例**：

```go
// internal/myapp/handler/v1/user/user.go
package user

import (
    "net/http"
    "strconv"
    "github.com/gin-gonic/gin"
    v1 "myapp/api/v1"
    "myapp/internal/myapp/biz"
    "myapp/pkg/core"
    "myapp/pkg/errors"
)

type UserHandler struct {
    b biz.IBiz
}

// NewUserHandler 创建 UserHandler 实例
func NewUserHandler(b biz.IBiz) *UserHandler {
    return &UserHandler{b: b}
}

// Create 创建用户
// @Summary 创建用户
// @Description 创建新用户
// @Tags users
// @Accept json
// @Produce json
// @Param request body v1.CreateUserRequest true "创建用户请求"
// @Success 201 {object} v1.CreateUserResponse
// @Failure 400 {object} core.ErrorResponse
// @Router /v1/users [post]
func (h *UserHandler) Create(c *gin.Context) {
    var req v1.CreateUserRequest

    // 参数绑定
    if err := c.ShouldBindJSON(&req); err != nil {
        core.WriteResponse(c, errors.ErrInvalidParameter.WithCause(err), nil)
        return
    }

    // 调用 Biz 层
    resp, err := h.b.Users().Create(c.Request.Context(), &req)
    if err != nil {
        core.WriteResponse(c, err, nil)
        return
    }

    // 返回响应
    core.WriteResponse(c, nil, resp)
}

// Get 获取用户详情
func (h *UserHandler) Get(c *gin.Context) {
    // 获取路径参数
    idStr := c.Param("id")
    id, err := strconv.ParseInt(idStr, 10, 64)
    if err != nil {
        core.WriteResponse(c, errors.ErrInvalidParameter.WithCause(err), nil)
        return
    }

    // 调用 Biz 层
    resp, err := h.b.Users().Get(c.Request.Context(), id)
    if err != nil {
        core.WriteResponse(c, err, nil)
        return
    }

    core.WriteResponse(c, nil, resp)
}

// List 用户列表
func (h *UserHandler) List(c *gin.Context) {
    var req v1.ListUserRequest

    // 绑定查询参数
    if err := c.ShouldBindQuery(&req); err != nil {
        core.WriteResponse(c, errors.ErrInvalidParameter.WithCause(err), nil)
        return
    }

    // 设置默认值
    if req.Page == 0 {
        req.Page = 1
    }
    if req.PageSize == 0 {
        req.PageSize = 10
    }

    // 调用 Biz 层
    resp, err := h.b.Users().List(c.Request.Context(), &req)
    if err != nil {
        core.WriteResponse(c, err, nil)
        return
    }

    core.WriteResponse(c, nil, resp)
}

// Update 更新用户
func (h *UserHandler) Update(c *gin.Context) {
    // 获取路径参数
    idStr := c.Param("id")
    id, err := strconv.ParseInt(idStr, 10, 64)
    if err != nil {
        core.WriteResponse(c, errors.ErrInvalidParameter.WithCause(err), nil)
        return
    }

    var req v1.UpdateUserRequest
    if err := c.ShouldBindJSON(&req); err != nil {
        core.WriteResponse(c, errors.ErrInvalidParameter.WithCause(err), nil)
        return
    }

    // 调用 Biz 层
    err = h.b.Users().Update(c.Request.Context(), id, &req)
    core.WriteResponse(c, err, nil)
}

// Delete 删除用户
func (h *UserHandler) Delete(c *gin.Context) {
    idStr := c.Param("id")
    id, err := strconv.ParseInt(idStr, 10, 64)
    if err != nil {
        core.WriteResponse(c, errors.ErrInvalidParameter.WithCause(err), nil)
        return
    }

    err = h.b.Users().Delete(c.Request.Context(), id)
    core.WriteResponse(c, err, nil)
}
```

**路由注册**：

```go
// internal/myapp/handler/v1/router.go
package v1

import (
    "github.com/gin-gonic/gin"
    "myapp/internal/myapp/biz"
    "myapp/internal/myapp/handler/v1/user"
    "myapp/internal/myapp/handler/v1/post"
)

// InstallRouters 安装所有 v1 路由
func InstallRouters(r *gin.Engine, b biz.IBiz) {
    v1 := r.Group("/v1")
    {
        // 用户路由
        userHandler := user.NewUserHandler(b)
        users := v1.Group("/users")
        {
            users.POST("", userHandler.Create)
            users.GET("/:id", userHandler.Get)
            users.GET("", userHandler.List)
            users.PUT("/:id", userHandler.Update)
            users.DELETE("/:id", userHandler.Delete)
        }

        // 文章路由
        postHandler := post.NewPostHandler(b)
        posts := v1.Group("/posts")
        {
            posts.POST("", postHandler.Create)
            posts.GET("/:id", postHandler.Get)
            posts.GET("", postHandler.List)
            posts.PUT("/:id", postHandler.Update)
            posts.DELETE("/:id", postHandler.Delete)
        }
    }
}
```

## 依赖注入：Wire

### 为什么使用 Wire？

- **编译时注入**：在编译时生成代码，无运行时反射
- **类型安全**：编译器检查依赖关系
- **性能高**：无反射开销
- **易调试**：生成的代码可读性强

### Wire 配置

```go
// internal/myapp/wire.go
//go:build wireinject
// +build wireinject

package myapp

import (
    "github.com/google/wire"
    "myapp/internal/myapp/biz"
    "myapp/internal/myapp/store"
    "gorm.io/gorm"
)

// ProviderSet 是所有 Providers 的集合
var ProviderSet = wire.NewSet(
    store.ProviderSet,  // Store 层 Providers
    biz.ProviderSet,    // Biz 层 Providers
    NewApp,             // App 构造函数
)

// InitApp 初始化应用（Wire 会生成实现）
func InitApp(db *gorm.DB, cfg *Config) (*App, func(), error) {
    wire.Build(ProviderSet)
    return &App{}, nil, nil
}
```

**Store 层 ProviderSet**：

```go
// internal/myapp/store/store.go
package store

import "github.com/google/wire"

// ProviderSet 定义 Store 层的 Providers
var ProviderSet = wire.NewSet(
    NewStore,
    wire.Bind(new(IStore), new(*datastore)),
)
```

**Biz 层 ProviderSet**：

```go
// internal/myapp/biz/biz.go
package biz

import (
    "github.com/google/wire"
    "myapp/internal/myapp/biz/v1/user"
    "myapp/internal/myapp/biz/v1/post"
)

// ProviderSet 定义 Biz 层的 Providers
var ProviderSet = wire.NewSet(
    NewBiz,
    wire.Bind(new(IBiz), new(*biz)),
    user.ProviderSet,  // UserBiz Providers
    post.ProviderSet,  // PostBiz Providers
)
```

**生成 Wire 代码**：

```bash
cd internal/myapp
wire
```

生成的文件：`wire_gen.go`（不要手动编辑）

## 错误处理

### 错误码设计

```go
// pkg/errors/code.go
package errors

type ErrorCode struct {
    Code    int
    Message string
    HTTP    int
}

var (
    // 通用错误 (10000-19999)
    ErrSuccess            = &ErrorCode{0, "Success", 200}
    ErrInternalServer     = &ErrorCode{10001, "Internal server error", 500}
    ErrInvalidParameter   = &ErrorCode{10002, "Invalid parameter", 400}
    ErrDatabase           = &ErrorCode{10003, "Database error", 500}

    // 用户相关 (20000-29999)
    ErrUserNotFound       = &ErrorCode{20001, "User not found", 404}
    ErrUserAlreadyExists  = &ErrorCode{20002, "User already exists", 409}
    ErrInvalidPassword    = &ErrorCode{20003, "Invalid password", 401}
    ErrUnauthorized       = &ErrorCode{20004, "Unauthorized", 401}

    // 文章相关 (30000-39999)
    ErrPostNotFound       = &ErrorCode{30001, "Post not found", 404}
)
```

### 统一响应格式

```go
// pkg/core/response.go
package core

import (
    "github.com/gin-gonic/gin"
    "myapp/pkg/errors"
)

type Response struct {
    Code    int         `json:"code"`
    Message string      `json:"message"`
    Data    interface{} `json:"data,omitempty"`
}

func WriteResponse(c *gin.Context, err error, data interface{}) {
    if err != nil {
        // 错误响应
        errCode := errors.ParseError(err)
        c.JSON(errCode.HTTP, Response{
            Code:    errCode.Code,
            Message: errCode.Message,
        })
        return
    }

    // 成功响应
    c.JSON(200, Response{
        Code:    0,
        Message: "Success",
        Data:    data,
    })
}
```

## 配置管理

### 使用 Viper + Pflag

```go
// internal/myapp/config.go
package myapp

import (
    "github.com/spf13/pflag"
    "github.com/spf13/viper"
)

type Config struct {
    Server   ServerConfig   `mapstructure:"server"`
    Database DatabaseConfig `mapstructure:"database"`
    JWT      JWTConfig      `mapstructure:"jwt"`
    Log      LogConfig      `mapstructure:"log"`
}

type ServerConfig struct {
    Addr string `mapstructure:"addr"`
    Mode string `mapstructure:"mode"`
}

type DatabaseConfig struct {
    Host     string `mapstructure:"host"`
    Port     int    `mapstructure:"port"`
    Database string `mapstructure:"database"`
    Username string `mapstructure:"username"`
    Password string `mapstructure:"password"`
}

func LoadConfig(configFile string) (*Config, error) {
    // 设置默认值
    viper.SetDefault("server.addr", ":8080")
    viper.SetDefault("server.mode", "release")

    // 读取配置文件
    if configFile != "" {
        viper.SetConfigFile(configFile)
        if err := viper.ReadInConfig(); err != nil {
            return nil, err
        }
    }

    // 绑定环境变量
    viper.SetEnvPrefix("MYAPP")
    viper.AutomaticEnv()

    // 解析到结构体
    var cfg Config
    if err := viper.Unmarshal(&cfg); err != nil {
        return nil, err
    }

    return &cfg, nil
}
```

## 中间件

### Request ID

```go
// pkg/middleware/requestid.go
package middleware

import (
    "github.com/gin-gonic/gin"
    "github.com/google/uuid"
)

func RequestID() gin.HandlerFunc {
    return func(c *gin.Context) {
        requestID := c.Request.Header.Get("X-Request-ID")
        if requestID == "" {
            requestID = uuid.New().String()
        }

        c.Set("X-Request-ID", requestID)
        c.Writer.Header().Set("X-Request-ID", requestID)
        c.Next()
    }
}
```

### 认证中间件

```go
// pkg/middleware/auth.go
package middleware

import (
    "github.com/gin-gonic/gin"
    "myapp/pkg/core"
    "myapp/pkg/errors"
    "myapp/pkg/token"
    "strings"
)

func Authn() gin.HandlerFunc {
    return func(c *gin.Context) {
        // 从 Header 获取 token
        authHeader := c.Request.Header.Get("Authorization")
        if authHeader == "" {
            core.WriteResponse(c, errors.ErrUnauthorized, nil)
            c.Abort()
            return
        }

        // Bearer {token}
        parts := strings.SplitN(authHeader, " ", 2)
        if !(len(parts) == 2 && parts[0] == "Bearer") {
            core.WriteResponse(c, errors.ErrUnauthorized, nil)
            c.Abort()
            return
        }

        // 验证 token
        claims, err := token.Parse(parts[1], "your-secret-key")
        if err != nil {
            core.WriteResponse(c, errors.ErrUnauthorized.WithCause(err), nil)
            c.Abort()
            return
        }

        // 设置用户信息到 context
        c.Set("user_id", claims.UserID)
        c.Set("username", claims.Username)
        c.Next()
    }
}
```

## 测试

### 单元测试（Store 层）

```go
// internal/myapp/store/user_test.go
package store

import (
    "context"
    "testing"
    "github.com/stretchr/testify/assert"
    "myapp/internal/myapp/model"
)

func TestUserStore_Create(t *testing.T) {
    db := setupTestDB(t)
    store := NewUsers(db)

    user := &model.User{
        Username: "test",
        Password: "hashed_password",
        Email:    "test@example.com",
    }

    err := store.Create(context.Background(), user)
    assert.NoError(t, err)
    assert.NotZero(t, user.ID)
}
```

### Mock 测试（Biz 层）

```go
// internal/myapp/biz/v1/user/user_test.go
package user

import (
    "context"
    "testing"
    "github.com/golang/mock/gomock"
    "github.com/stretchr/testify/assert"
    v1 "myapp/api/v1"
    "myapp/internal/myapp/model"
    "myapp/internal/myapp/store/mock"
)

func TestUserBiz_Create(t *testing.T) {
    ctrl := gomock.NewController(t)
    defer ctrl.Finish()

    mockStore := mock.NewMockIStore(ctrl)
    mockUserStore := mock.NewMockUserStore(ctrl)

    mockStore.EXPECT().Users().Return(mockUserStore).AnyTimes()
    mockUserStore.EXPECT().GetByUsername(gomock.Any(), "test").Return(nil, errors.ErrUserNotFound)
    mockUserStore.EXPECT().Create(gomock.Any(), gomock.Any()).Return(nil)

    biz := NewUserBiz(mockStore)

    req := &v1.CreateUserRequest{
        Username: "test",
        Password: "password123",
        Email:    "test@example.com",
    }

    resp, err := biz.Create(context.Background(), req)
    assert.NoError(t, err)
    assert.NotNil(t, resp)
    assert.Equal(t, "test", resp.Username)
}
```

## 最佳实践总结

### 1. 架构一致性
- ✅ 严格遵循 Handler → Biz → Store → Model 分层
- ✅ 不跨层访问
- ✅ 所有依赖都是接口

### 2. 接口驱动
- ✅ 每一层都定义接口
- ✅ 使用 mockgen 生成测试 mock
- ✅ 便于单元测试

### 3. 依赖注入
- ✅ 使用 Wire 进行编译时注入
- ✅ 避免全局变量
- ✅ 提高可测试性

### 4. 错误处理
- ✅ 统一错误码设计
- ✅ 错误信息清晰
- ✅ 分层错误转换

### 5. 配置管理
- ✅ 使用 Viper 支持多格式
- ✅ 支持环境变量覆盖
- ✅ 配置外部化

### 6. 测试覆盖
- ✅ 单元测试（每层独立测试）
- ✅ 集成测试（端到端测试）
- ✅ 性能测试（Benchmark）

## 参考项目

- [miniblog](https://github.com/onexstack/miniblog) - 小而美的 Go 实战项目
- [onex](https://github.com/onexstack/onex) - 大型云原生实战平台

## 参考资料

- [Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [golang-standards/project-layout](https://github.com/golang-standards/project-layout)
- [Wire User Guide](https://github.com/google/wire/blob/main/docs/guide.md)

---
name: golang-best-practices
description: 当用户需要创建 Golang 项目、构建 Go 应用、组织 Go 代码结构时使用。触发词：Golang、Go 项目、Go 应用、Go 架构、Go 开发
---

# Golang 最佳实践 Skill

基于生产环境验证的 Golang 最佳实践，帮助构建高质量、易维护、可扩展的 Go 应用。

## 开发工作流

通用开发流程（需求分析、技术设计、代码审查等）请参考 **development-workflow skill**。
本文档专注于 **Golang 特定** 的开发实践。

## 核心原则

1. **清晰架构** - 分层设计，职责明确
2. **接口驱动** - 面向接口编程，便于测试和扩展
3. **依赖注入** - 使用 Wire 管理依赖
4. **标准布局** - 遵循 golang-standards/project-layout
5. **错误处理** - 规范的错误码和错误处理机制

## 项目结构

创建新项目时使用标准布局（完整初始化使用 `init-project.sh`）：

```
project/
├── cmd/                    # 应用入口
│   └── myapp/main.go
├── internal/              # 私有代码（Go 编译器强制隔离）
│   ├── myapp/
│   │   ├── biz/v1/       # 业务逻辑层（按版本）
│   │   ├── handler/      # HTTP/gRPC 处理器
│   │   ├── model/        # 数据模型
│   │   ├── store/        # 数据存储层
│   │   ├── server.go     # 服务器初始化
│   │   └── wire.go       # 依赖注入定义
│   └── pkg/              # 内部共享库（errno/log/middleware）
├── pkg/api/v1/           # 外部可用的 API 定义
├── configs/              # 配置文件
├── deployments/          # K8s manifests
├── scripts/              # 构建脚本
├── Makefile
└── go.mod
```

**分层架构：**
```
Handler → Biz → Store → Model
  ↓        ↓      ↓       ↓
HTTP/gRPC  业务逻辑  数据访问  数据模型
```

**实现顺序（自底向上）：** Model → Store → Biz → Handler → Wire → Test

---

## 各层设计模式

> 完整代码示例见 [architecture-design.md](architecture-design.md)

### Biz 层 — 接口驱动 + 版本化

```go
// internal/myapp/biz/v1/user/user.go
//go:generate mockgen -destination mock_user.go -package user ...

// ✅ 定义接口，便于 Mock 测试
type UserBiz interface {
    Create(ctx context.Context, req *apiv1.CreateUserRequest) (*apiv1.CreateUserResponse, error)
    Get(ctx context.Context, req *apiv1.GetUserRequest) (*apiv1.GetUserResponse, error)
    List(ctx context.Context, req *apiv1.ListUserRequest) (*apiv1.ListUserResponse, error)
}

// ✅ 私有 struct 实现接口
type userBiz struct {
    store store.IStore
}

func NewUserBiz(store store.IStore) UserBiz {
    return &userBiz{store: store}
}
```

关键模式：
- 接口定义在使用方，实现在提供方
- `//go:generate mockgen` 自动生成 Mock
- 按 `v1/v2` 版本化组织，支持 API 演进

### Store 层 — 接口 + Functional Options

```go
// ✅ 聚合接口，一个入口访问所有存储
type IStore interface {
    Users() UserStore
    Posts() PostStore
}

// ✅ Functional Options 模式处理查询参数
func (u *users) List(ctx context.Context, opts ...Option) ([]*model.User, int64, error) {
    o := NewOptions(opts...)
    // ... 分页查询
}

// 调用方式：store.Users().List(ctx, WithOffset(10), WithLimit(20))
```

关键模式：
- `var _ UserStore = (*users)(nil)` 编译期接口检查
- Functional Options 替代大参数 struct
- `db.WithContext(ctx)` 传递 context

### Handler 层 — 统一响应

```go
// ✅ 统一响应格式
func WriteResponse(c *gin.Context, err error, data interface{}) {
    if err != nil {
        coder := errno.ParseCoder(err)
        c.JSON(coder.HTTPStatus(), Response{Code: coder.Code(), Message: coder.String()})
        return
    }
    c.JSON(http.StatusOK, Response{Code: 0, Message: "success", Data: data})
}

// ✅ Handler 保持薄层，只做绑定和调用
func (h *UserHandler) Create(c *gin.Context) {
    var req apiv1.CreateUserRequest
    if err := c.ShouldBindJSON(&req); err != nil {
        WriteResponse(c, errno.ErrBind.WithCause(err), nil)
        return
    }
    resp, err := h.biz.Create(c.Request.Context(), &req)
    WriteResponse(c, err, resp)
}
```

### Model 层 — GORM 约定

```go
type User struct {
    ID        uint64         `gorm:"column:id;primary_key;auto_increment"`
    Username  string         `gorm:"column:username;type:varchar(255);not null;uniqueIndex"`
    Email     string         `gorm:"column:email;type:varchar(255);not null;uniqueIndex"`
    Password  string         `gorm:"column:password;type:varchar(255);not null"`
    CreatedAt time.Time      `gorm:"column:created_at"`
    UpdatedAt time.Time      `gorm:"column:updated_at"`
    DeletedAt gorm.DeletedAt `gorm:"column:deleted_at;index"`
}

func (u *User) TableName() string { return "users" }
```

---

## 依赖注入（Wire）

```go
//go:build wireinject

func NewServer() (*Server, func(), error) {
    panic(wire.Build(
        provideDB,              // 数据库
        store.NewStore,         // Store 层
        user.NewUserBiz,        // Biz 层
        handler.NewUserHandler, // Handler 层
        NewServerConfig, NewServer,
    ))
}
```

生成代码：`wire gen ./internal/myapp`

---

## 错误处理

```go
// ✅ 错误码分段设计
var (
    // 通用 10000-10999
    ErrInternalServer = &coder{http.StatusInternalServerError, 10001, "Internal server error", nil}
    ErrBind           = &coder{http.StatusBadRequest, 10002, "Bind request error", nil}
    ErrValidation     = &coder{http.StatusBadRequest, 10003, "Validation failed", nil}

    // 用户 20000-20999
    ErrUserNotFound   = &coder{http.StatusNotFound, 20001, "User not found", nil}
    ErrUserAlreadyExist = &coder{http.StatusConflict, 20002, "User already exists", nil}
)

// ✅ WithCause 链式附加原因
return nil, errno.ErrValidation.WithCause(err)

// ✅ ParseCoder 统一解析
coder := errno.ParseCoder(err)
```

关键模式：
- 错误码按业务模块分段（通用 1xxxx、用户 2xxxx、授权 3xxxx）
- `Coder` 接口统一错误码行为（HTTPStatus / Code / String）
- `WithCause` 保留原始错误链

---

## 中间件

三个核心中间件（完整实现见 architecture-design.md）：

| 中间件 | 职责 | 关键点 |
|--------|------|--------|
| RequestID | 请求追踪 | 优先取 Header，否则生成 UUID |
| Logger | 请求日志 | 记录 method/path/status/cost/ip |
| Authn | JWT 认证 | 解析 token，设置 userID 到 context |

注册顺序：`RequestID → Logger → Recovery → Authn（需认证的路由组）`

---

## 配置管理（Viper）

```go
type Config struct {
    Server   ServerConfig   `mapstructure:"server"`
    Database DatabaseConfig `mapstructure:"database"`
    Log      LogConfig      `mapstructure:"log"`
    JWT      JWTConfig      `mapstructure:"jwt"`
}
```

配置文件示例见 `configs/app.yaml`（由 init-project.sh 生成）。

---

## 测试

```go
// ✅ 表驱动测试 + gomock
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
            req:  &apiv1.CreateUserRequest{Username: "test", Email: "test@example.com"},
            mock: func() {
                mockUserStore.EXPECT().Create(gomock.Any(), gomock.Any()).Return(nil)
            },
            wantErr: false,
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

关键模式：
- 表驱动测试（table-driven tests）
- gomock + mockgen 自动生成 Mock
- `gomock.Any()` 匹配任意参数
- Benchmark 测试用 `b.ResetTimer()` 排除初始化时间

---

## 常见陷阱

| 陷阱 | 正确做法 |
|------|---------|
| ❌ 不定义接口，直接依赖具体实现 | ✅ 接口驱动，便于 Mock 测试 |
| ❌ 在 Handler 里写业务逻辑 | ✅ Handler 只做绑定和调用，逻辑放 Biz |
| ❌ 错误直接 `fmt.Errorf` 返回 | ✅ 使用统一错误码 `errno.ErrXxx.WithCause(err)` |
| ❌ 手动管理依赖创建顺序 | ✅ 使用 Wire 自动注入 |
| ❌ `gorm.Open` 不设连接池 | ✅ 设置 MaxOpenConns / MaxIdleConns / ConnMaxLifetime |
| ❌ context 不传递 | ✅ 全链路 `db.WithContext(ctx)` |
| ❌ 日志用 `fmt.Println` | ✅ 结构化日志 `log.Infow("msg", "key", value)` |

---

## 快速开始清单

1. ✅ 运行 `init-project.sh` 创建项目结构
2. ✅ 初始化 `go.mod`
3. ✅ 定义 API 接口（protobuf/OpenAPI）
4. ✅ 按顺序实现：Model → Store → Biz → Handler
5. ✅ 配置 Wire 依赖注入
6. ✅ 添加中间件（RequestID → Logger → Recovery → Authn）
7. ✅ 设置错误码和统一响应
8. ✅ 编写测试（表驱动 + Mock）
9. ✅ 配置 Makefile（`make build/test/lint/wire`）
10. ✅ API 文档

## 参考资源

- [Go 官方文档](https://go.dev/doc/)
- [golang-standards/project-layout](https://github.com/golang-standards/project-layout)
- [GORM 文档](https://gorm.io/docs/)
- [Wire 文档](https://github.com/google/wire)
- [Gin 文档](https://gin-gonic.com/docs/)

---

**详细参考：**
- 完整架构设计和代码示例 → [architecture-design.md](architecture-design.md)
- 开发工作流和实现步骤 → [development-workflow.md](development-workflow.md)
- 一键初始化项目 → `init-project.sh`

---

**使用此 skill 时，Claude 将：**
- 遵循 golang-standards/project-layout 标准布局
- 应用分层架构设计（Handler → Biz → Store → Model）
- 使用接口驱动开发，所有层间通过接口解耦
- 实现 Wire 依赖注入
- 使用统一错误码和 WriteResponse 响应格式
- 编写表驱动测试 + gomock Mock
- 遵循 Go 社区最佳实践（参考 Effective Go、100 Go Mistakes and How to Avoid Them）
- 基于生产环境验证的 Clean Architecture 实践

# Golang 项目开发工作流

## 📋 通用开发流程

关于通用的软件开发流程，请参考 **development-workflow skill**，其中包含：
- 需求分析方法（需求文档模板）
- 技术设计流程（设计文档模板、ADR）
- 任务分解模板（IMPLEMENTATION_PLAN.md）
- 代码审查清单（architecture-review-checklist.md）
- 测试策略和覆盖率要求
- Git 提交规范

本文档专注于 **Golang 特定** 的开发实践和工作流程，基于 miniblog 和 onex 项目验证。

---

## 🏗️ Golang 实现流程（自底向上）

### 核心原则

- **严格分层** - Model → Store → Biz → Handler → Wire 顺序
- **接口驱动** - 每一层都定义接口，便于测试和 mock
- **小步快跑** - 每一层完成后立即测试，不跨层实现

### 标准实现顺序

```
1. Model（数据模型）
   ↓
2. Store（数据访问）
   ↓
3. Biz（业务逻辑）
   ↓
4. Handler（HTTP 接口）
   ↓
5. Wire（依赖注入）
```

**为什么这个顺序？**
- Model 定义数据结构，是整个系统的基础
- Store 依赖 Model，实现数据持久化
- Biz 依赖 Store，实现业务逻辑
- Handler 依赖 Biz，暴露 HTTP 接口
- Wire 连接所有依赖，启动应用

**优点**：每一层完成后都可以测试，不会出现"上层做完了下层还没实现"的情况。

---

## 📦 第 1 步：Model 层

### 目标
定义数据模型结构

### 实现示例

```go
// internal/myapp/model/user.go
package model

import "time"

type User struct {
    ID        int64     `gorm:"column:id;primary_key;AUTO_INCREMENT"`
    Username  string    `gorm:"column:username;not null;uniqueIndex:idx_username"`
    Password  string    `gorm:"column:password;not null"`
    Email     string    `gorm:"column:email;not null;index:idx_email"`
    CreatedAt time.Time `gorm:"column:created_at"`
    UpdatedAt time.Time `gorm:"column:updated_at"`
}

// TableName 自定义表名
func (u *User) TableName() string {
    return "users"
}

// BeforeCreate Hook 示例
func (u *User) BeforeCreate(tx *gorm.DB) error {
    // 可以在这里添加创建前的逻辑
    return nil
}
```

### 检查清单

- [ ] 结构体字段定义完整
- [ ] GORM 标签正确（主键、索引、约束）
- [ ] TableName() 方法（如需自定义表名）
- [ ] Hooks（BeforeCreate、AfterFind 等，如需要）
- [ ] 时间字段使用 `time.Time`
- [ ] 使用 `int64` 而不是 `uint` 作为 ID

---

## 💾 第 2 步：Store 层

### 目标
实现数据访问接口，封装数据库操作

### 实现示例

```go
// internal/myapp/store/user.go
package store

import (
    "context"

    "gorm.io/gorm"

    "myproject/internal/myapp/model"
)

// UserStore 定义用户数据访问接口
type UserStore interface {
    Create(ctx context.Context, user *model.User) error
    Get(ctx context.Context, id int64) (*model.User, error)
    GetByUsername(ctx context.Context, username string) (*model.User, error)
    List(ctx context.Context, offset, limit int) ([]*model.User, int64, error)
    Update(ctx context.Context, user *model.User) error
    Delete(ctx context.Context, id int64) error
}

// users 实现 UserStore 接口
type users struct {
    db *gorm.DB
}

// NewUsers 创建 UserStore 实例
func NewUsers(db *gorm.DB) UserStore {
    return &users{db: db}
}

// Create 创建用户
func (u *users) Create(ctx context.Context, user *model.User) error {
    return u.db.WithContext(ctx).Create(user).Error
}

// Get 根据 ID 获取用户
func (u *users) Get(ctx context.Context, id int64) (*model.User, error) {
    var user model.User
    if err := u.db.WithContext(ctx).Where("id = ?", id).First(&user).Error; err != nil {
        return nil, err
    }
    return &user, nil
}

// GetByUsername 根据用户名获取用户
func (u *users) GetByUsername(ctx context.Context, username string) (*model.User, error) {
    var user model.User
    err := u.db.WithContext(ctx).
        Where("username = ?", username).
        First(&user).Error
    if err != nil {
        return nil, err
    }
    return &user, nil
}

// List 分页查询用户列表
func (u *users) List(ctx context.Context, offset, limit int) ([]*model.User, int64, error) {
    var (
        users []*model.User
        count int64
    )

    // 查询总数
    if err := u.db.WithContext(ctx).Model(&model.User{}).Count(&count).Error; err != nil {
        return nil, 0, err
    }

    // 分页查询
    if err := u.db.WithContext(ctx).
        Offset(offset).
        Limit(limit).
        Order("id desc").
        Find(&users).Error; err != nil {
        return nil, 0, err
    }

    return users, count, nil
}

// Update 更新用户
func (u *users) Update(ctx context.Context, user *model.User) error {
    return u.db.WithContext(ctx).Save(user).Error
}

// Delete 删除用户（软删除或硬删除）
func (u *users) Delete(ctx context.Context, id int64) error {
    return u.db.WithContext(ctx).Where("id = ?", id).Delete(&model.User{}).Error
}
```

### 检查清单

- [ ] 接口定义清晰（方法名、参数、返回值）
- [ ] 实现 CRUD 基本操作
- [ ] 使用 `WithContext(ctx)` 传递上下文
- [ ] 复杂查询逻辑（分页、筛选、排序）
- [ ] 错误处理（直接返回 GORM 错误）
- [ ] Provider 函数（NewUsers）
- [ ] 单元测试覆盖（使用 sqlite 内存数据库）

### 单元测试示例

```go
// internal/myapp/store/user_test.go
package store

import (
    "context"
    "testing"

    "github.com/stretchr/testify/assert"
    "gorm.io/driver/sqlite"
    "gorm.io/gorm"

    "myproject/internal/myapp/model"
)

func setupTestDB(t *testing.T) *gorm.DB {
    db, err := gorm.Open(sqlite.Open(":memory:"), &gorm.Config{})
    assert.NoError(t, err)

    // 自动迁移
    err = db.AutoMigrate(&model.User{})
    assert.NoError(t, err)

    return db
}

func TestUserStore_Create(t *testing.T) {
    db := setupTestDB(t)
    store := NewUsers(db)

    user := &model.User{
        Username: "testuser",
        Password: "hashed_password",
        Email:    "test@example.com",
    }

    err := store.Create(context.Background(), user)
    assert.NoError(t, err)
    assert.NotZero(t, user.ID)
}

func TestUserStore_Get(t *testing.T) {
    db := setupTestDB(t)
    store := NewUsers(db)

    // 创建测试数据
    user := &model.User{
        Username: "testuser",
        Password: "hashed_password",
        Email:    "test@example.com",
    }
    _ = store.Create(context.Background(), user)

    // 测试获取
    got, err := store.Get(context.Background(), user.ID)
    assert.NoError(t, err)
    assert.Equal(t, user.Username, got.Username)
}
```

---

## 🧠 第 3 步：Biz 层

### 目标
实现业务逻辑，封装业务规则

### 实现示例

```go
// internal/myapp/biz/v1/user/user.go
package user

import (
    "context"
    "errors"

    "golang.org/x/crypto/bcrypt"
    "gorm.io/gorm"

    v1 "myproject/pkg/api/v1"
    "myproject/internal/myapp/store"
    "myproject/internal/pkg/errno"
)

// UserBiz 定义用户业务接口
type UserBiz interface {
    Create(ctx context.Context, req *v1.CreateUserRequest) (*v1.CreateUserResponse, error)
    Get(ctx context.Context, id int64) (*v1.GetUserResponse, error)
    List(ctx context.Context, req *v1.ListUserRequest) (*v1.ListUserResponse, error)
    Update(ctx context.Context, id int64, req *v1.UpdateUserRequest) error
    Delete(ctx context.Context, id int64) error
}

// userBiz 实现 UserBiz 接口
type userBiz struct {
    ds store.IStore
}

// NewUserBiz 创建 UserBiz 实例
func NewUserBiz(ds store.IStore) UserBiz {
    return &userBiz{ds: ds}
}

// Create 创建用户
func (b *userBiz) Create(ctx context.Context, req *v1.CreateUserRequest) (*v1.CreateUserResponse, error) {
    // 1. 业务校验：检查用户名是否已存在
    _, err := b.ds.Users().GetByUsername(ctx, req.Username)
    if err == nil {
        return nil, errno.ErrUserAlreadyExists
    }
    if !errors.Is(err, gorm.ErrRecordNotFound) {
        return nil, err
    }

    // 2. 密码加密
    hashedPassword, err := bcrypt.GenerateFromPassword([]byte(req.Password), bcrypt.DefaultCost)
    if err != nil {
        return nil, err
    }

    // 3. 创建用户
    user := &model.User{
        Username: req.Username,
        Password: string(hashedPassword),
        Email:    req.Email,
    }

    if err := b.ds.Users().Create(ctx, user); err != nil {
        return nil, err
    }

    // 4. 返回响应
    return &v1.CreateUserResponse{
        UserID:    user.ID,
        Username:  user.Username,
        Email:     user.Email,
        CreatedAt: user.CreatedAt,
    }, nil
}

// Get 获取用户
func (b *userBiz) Get(ctx context.Context, id int64) (*v1.GetUserResponse, error) {
    user, err := b.ds.Users().Get(ctx, id)
    if err != nil {
        if errors.Is(err, gorm.ErrRecordNotFound) {
            return nil, errno.ErrUserNotFound
        }
        return nil, err
    }

    return &v1.GetUserResponse{
        UserID:    user.ID,
        Username:  user.Username,
        Email:     user.Email,
        CreatedAt: user.CreatedAt,
        UpdatedAt: user.UpdatedAt,
    }, nil
}

// List 列表查询
func (b *userBiz) List(ctx context.Context, req *v1.ListUserRequest) (*v1.ListUserResponse, error) {
    offset := (req.Page - 1) * req.PageSize
    users, total, err := b.ds.Users().List(ctx, offset, req.PageSize)
    if err != nil {
        return nil, err
    }

    items := make([]*v1.UserInfo, 0, len(users))
    for _, user := range users {
        items = append(items, &v1.UserInfo{
            UserID:    user.ID,
            Username:  user.Username,
            Email:     user.Email,
            CreatedAt: user.CreatedAt,
        })
    }

    return &v1.ListUserResponse{
        Total: total,
        Items: items,
    }, nil
}
```

### 检查清单

- [ ] 接口定义清晰
- [ ] 参数校验（使用 validator 或自定义校验）
- [ ] 业务规则实现（如：用户名唯一性）
- [ ] 权限检查（如果需要）
- [ ] 调用 Store 层
- [ ] 错误处理和包装（使用自定义 errno）
- [ ] Provider 函数（NewUserBiz）
- [ ] 单元测试（mock Store 层）

### 单元测试示例（使用 Mock）

```go
// internal/myapp/biz/v1/user/user_test.go
package user

import (
    "context"
    "errors"
    "testing"

    "github.com/golang/mock/gomock"
    "github.com/stretchr/testify/assert"
    "gorm.io/gorm"

    v1 "myproject/pkg/api/v1"
    "myproject/internal/myapp/store"
    "myproject/internal/myapp/store/mock"
)

func TestUserBiz_Create(t *testing.T) {
    ctrl := gomock.NewController(t)
    defer ctrl.Finish()

    mockStore := mock.NewMockIStore(ctrl)
    mockUserStore := mock.NewMockUserStore(ctrl)

    biz := NewUserBiz(mockStore)

    // Mock: 用户名不存在
    mockStore.EXPECT().Users().Return(mockUserStore).Times(2)
    mockUserStore.EXPECT().
        GetByUsername(gomock.Any(), "newuser").
        Return(nil, gorm.ErrRecordNotFound)

    // Mock: 创建成功
    mockUserStore.EXPECT().
        Create(gomock.Any(), gomock.Any()).
        Return(nil)

    // 测试创建
    req := &v1.CreateUserRequest{
        Username: "newuser",
        Password: "password123",
        Email:    "new@example.com",
    }

    resp, err := biz.Create(context.Background(), req)
    assert.NoError(t, err)
    assert.NotNil(t, resp)
    assert.Equal(t, "newuser", resp.Username)
}
```

---

## 🌐 第 4 步：Handler 层

### 目标
实现 HTTP 接口，处理请求和响应

### 实现示例

```go
// internal/myapp/handler/v1/user/user.go
package user

import (
    "strconv"

    "github.com/gin-gonic/gin"

    v1 "myproject/pkg/api/v1"
    "myproject/internal/myapp/biz"
    "myproject/internal/pkg/core"
    "myproject/internal/pkg/errno"
)

// UserHandler 处理用户相关请求
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
// @Param request body v1.CreateUserRequest true "用户信息"
// @Success 201 {object} v1.CreateUserResponse
// @Router /v1/users [post]
func (h *UserHandler) Create(c *gin.Context) {
    var req v1.CreateUserRequest

    // 参数绑定和校验
    if err := c.ShouldBindJSON(&req); err != nil {
        core.WriteResponse(c, errno.ErrBind, nil)
        return
    }

    // 调用 Biz 层
    resp, err := h.b.Users().Create(c.Request.Context(), &req)
    if err != nil {
        core.WriteResponse(c, err, nil)
        return
    }

    core.WriteResponse(c, nil, resp)
}

// Get 获取用户详情
// @Summary 获取用户详情
// @Description 根据 ID 获取用户信息
// @Tags users
// @Accept json
// @Produce json
// @Param id path int64 true "用户 ID"
// @Success 200 {object} v1.GetUserResponse
// @Router /v1/users/{id} [get]
func (h *UserHandler) Get(c *gin.Context) {
    // 获取路径参数
    idStr := c.Param("id")
    id, err := strconv.ParseInt(idStr, 10, 64)
    if err != nil {
        core.WriteResponse(c, errno.ErrInvalidParameter, nil)
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

// List 列表查询
// @Summary 用户列表
// @Description 分页查询用户列表
// @Tags users
// @Accept json
// @Produce json
// @Param page query int false "页码" default(1)
// @Param page_size query int false "每页数量" default(10)
// @Success 200 {object} v1.ListUserResponse
// @Router /v1/users [get]
func (h *UserHandler) List(c *gin.Context) {
    var req v1.ListUserRequest

    // 绑定查询参数
    if err := c.ShouldBindQuery(&req); err != nil {
        core.WriteResponse(c, errno.ErrBind, nil)
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
```

### 路由注册

```go
// internal/myapp/handler/v1/user/routes.go
package user

import (
    "github.com/gin-gonic/gin"
)

// RegisterRoutes 注册路由
func (h *UserHandler) RegisterRoutes(g *gin.RouterGroup) {
    users := g.Group("/users")
    {
        users.POST("", h.Create)          // POST /v1/users
        users.GET("/:id", h.Get)          // GET /v1/users/:id
        users.GET("", h.List)             // GET /v1/users
        users.PUT("/:id", h.Update)       // PUT /v1/users/:id
        users.DELETE("/:id", h.Delete)    // DELETE /v1/users/:id
    }
}
```

### 检查清单

- [ ] 路由注册（GET、POST、PUT、DELETE）
- [ ] 请求参数绑定（c.ShouldBindJSON、c.ShouldBindQuery）
- [ ] 参数校验（使用 validator 标签）
- [ ] 调用 Biz 层
- [ ] 响应格式化（统一使用 core.WriteResponse）
- [ ] 错误处理（HTTP 状态码映射）
- [ ] Swagger 注释（如需要）
- [ ] Provider 函数（NewUserHandler）
- [ ] 集成测试（使用 httptest）

### 集成测试示例

```go
// internal/myapp/handler/v1/user/user_test.go
package user

import (
    "bytes"
    "encoding/json"
    "net/http"
    "net/http/httptest"
    "testing"

    "github.com/gin-gonic/gin"
    "github.com/stretchr/testify/assert"

    v1 "myproject/pkg/api/v1"
)

func setupTestRouter(t *testing.T) *gin.Engine {
    gin.SetMode(gin.TestMode)
    router := gin.New()

    // 初始化测试依赖（使用真实数据库或 mock）
    // ...

    return router
}

func TestUserHandler_Create(t *testing.T) {
    router := setupTestRouter(t)

    // 构造请求
    req := v1.CreateUserRequest{
        Username: "testuser",
        Password: "password123",
        Email:    "test@example.com",
    }
    body, _ := json.Marshal(req)

    w := httptest.NewRecorder()
    r := httptest.NewRequest("POST", "/v1/users", bytes.NewReader(body))
    r.Header.Set("Content-Type", "application/json")

    // 执行请求
    router.ServeHTTP(w, r)

    // 验证响应
    assert.Equal(t, http.StatusOK, w.Code)

    var resp v1.CreateUserResponse
    _ = json.Unmarshal(w.Body.Bytes(), &resp)
    assert.Equal(t, "testuser", resp.Username)
}
```

---

## 🔌 第 5 步：Wire 依赖注入

### 目标
使用 Wire 连接所有依赖，自动生成初始化代码

### Wire 配置示例

```go
// internal/myapp/wire.go
//go:build wireinject
// +build wireinject

package myapp

import (
    "github.com/google/wire"
    "gorm.io/gorm"

    "myproject/internal/myapp/biz"
    userbiz "myproject/internal/myapp/biz/v1/user"
    "myproject/internal/myapp/handler"
    userhandler "myproject/internal/myapp/handler/v1/user"
    "myproject/internal/myapp/store"
)

// ProviderSet 定义 Provider 集合
var ProviderSet = wire.NewSet(
    store.ProviderSet,
    biz.ProviderSet,
    handler.ProviderSet,
)

// InitApp 初始化应用（Wire 会生成实现）
func InitApp(db *gorm.DB) (*App, error) {
    wire.Build(
        ProviderSet,
        NewApp,
    )
    return &App{}, nil
}
```

### Provider 集合定义

```go
// internal/myapp/store/store.go
package store

import (
    "github.com/google/wire"
    "gorm.io/gorm"
)

// IStore 定义 Store 接口
type IStore interface {
    Users() UserStore
    // 其他 Store 接口...
}

// datastore 实现 IStore
type datastore struct {
    db *gorm.DB
}

// NewStore 创建 Store 实例
func NewStore(db *gorm.DB) IStore {
    return &datastore{db: db}
}

func (ds *datastore) Users() UserStore {
    return NewUsers(ds.db)
}

// ProviderSet 导出 Wire Provider 集合
var ProviderSet = wire.NewSet(NewStore)
```

```go
// internal/myapp/biz/biz.go
package biz

import (
    "github.com/google/wire"

    userbiz "myproject/internal/myapp/biz/v1/user"
    "myproject/internal/myapp/store"
)

// IBiz 定义 Biz 接口
type IBiz interface {
    Users() userbiz.UserBiz
}

// biz 实现 IBiz
type biz struct {
    ds store.IStore
}

// NewBiz 创建 Biz 实例
func NewBiz(ds store.IStore) IBiz {
    return &biz{ds: ds}
}

func (b *biz) Users() userbiz.UserBiz {
    return userbiz.NewUserBiz(b.ds)
}

// ProviderSet 导出 Wire Provider 集合
var ProviderSet = wire.NewSet(NewBiz)
```

### 生成 Wire 代码

```bash
# 安装 Wire
go install github.com/google/wire/cmd/wire@latest

# 生成依赖注入代码
cd internal/myapp
wire

# 会生成 wire_gen.go 文件
```

### 检查清单

- [ ] Provider 函数定义（NewXXX）
- [ ] ProviderSet 导出
- [ ] wire.go 文件配置正确
- [ ] 执行 `wire` 命令生成 wire_gen.go
- [ ] 编译通过（`go build`）
- [ ] 无循环依赖警告

### 常见 Wire 问题

**问题 1：循环依赖**
```bash
wire: /path/to/wire.go:xx:x: inject InitApp: cycle detected:
```
解决：检查依赖关系图，重新设计接口

**问题 2：缺少 Provider**
```bash
wire: /path/to/wire.go:xx:x: no provider found for ...
```
解决：确保所有依赖都有 New 函数，并加入 ProviderSet

**问题 3：类型不匹配**
```bash
wire: /path/to/wire.go:xx:x: ... does not match ...
```
解决：检查接口实现和返回类型

---

## ✅ Golang 质量门控

### 完成定义（Definition of Done）

一个 Golang 任务只有满足以下所有条件才算完成：

- [ ] **测试**：编写了测试且全部通过
- [ ] **规范**：通过 golangci-lint 检查
- [ ] **命名**：符合 Go 规范（驼峰命名、导出/非导出）
- [ ] **注释**：公开接口和函数有注释
- [ ] **错误**：错误处理得当（不忽略错误）
- [ ] **Wire**：依赖注入配置正确
- [ ] **分层**：遵循 Handler → Biz → Store → Model

### 测试覆盖率目标

- 核心业务逻辑（Biz 层）：> 80%
- 数据访问层（Store 层）：> 70%
- 接口层（Handler 层）：> 60%

```bash
# 运行测试并查看覆盖率
go test -v -cover ./...

# 生成覆盖率报告
go test -coverprofile=coverage.out ./...
go tool cover -html=coverage.out
```

### 自动化检查

```bash
# 代码格式化
go fmt ./...
gofumpt -l -w .

# 静态检查
golangci-lint run

# 测试
go test -v ./...

# 构建
go build -v ./cmd/myapp
```

---

## ⚠️ Golang 特定注意事项

### 永远不要

- ❌ 忽略错误返回值
- ❌ 跨层调用（Handler 直接访问 Store）
- ❌ 使用全局变量存储状态
- ❌ 在 Biz/Handler 中直接写 SQL
- ❌ 不使用 context 传递

### 永远要

- ✅ 严格遵循 Model → Store → Biz → Handler → Wire 顺序
- ✅ 每一层定义接口
- ✅ 使用 Wire 管理依赖
- ✅ 使用 context 传递上下文
- ✅ 使用 GORM 而不是原生 SQL
- ✅ 编写单元测试和集成测试

---

## 🚀 Golang 快速开始清单

### 开始新功能前

1. [ ] 阅读并理解需求文档
2. [ ] 在代码库中找 3 个类似的 Golang 实现
3. [ ] 识别要遵循的分层模式
4. [ ] 规划 Model → Store → Biz → Handler → Wire 顺序
5. [ ] 确认每个阶段的成功标准

### 开发 Golang 功能时

1. [ ] 定义 Model 结构体（GORM 标签）
2. [ ] 实现 Store 接口和方法
3. [ ] 编写 Store 单元测试
4. [ ] 实现 Biz 接口和方法
5. [ ] 编写 Biz 单元测试（使用 mock）
6. [ ] 实现 Handler 和路由
7. [ ] 编写 Handler 集成测试
8. [ ] 配置 Wire 依赖注入
9. [ ] 生成 wire_gen.go

### 完成 Golang 功能后

1. [ ] 所有测试通过
2. [ ] golangci-lint 检查通过
3. [ ] 接口定义清晰
4. [ ] 依赖注入配置正确
5. [ ] Wire 生成成功
6. [ ] 编译和运行成功

---

## 📋 Golang 完整示例

基于 miniblog 和 onex 项目的完整实现示例，参考：

- [miniblog](https://github.com/onexstack/miniblog) - 小型实战项目
- [onex](https://github.com/onexstack/onex) - 大型云原生项目

---

**版本**：v2.0
**更新日期**：2025-12-25
**核心原则**：Model → Store → Biz → Handler → Wire、接口驱动、Wire 依赖注入

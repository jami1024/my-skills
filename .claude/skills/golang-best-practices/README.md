# Golang 最佳实践 Skill

基于企业级 Go 项目 [miniblog](https://github.com/onexstack/miniblog) 和 [onex](https://github.com/onexstack/onex) 的最佳实践总结。

## 项目简介

本 Skill 提取了两个真实企业级 Go 项目的架构模式和最佳实践：

- **miniblog**: 小而美的 Go 实战项目，入门但不简单，实现了用户管理和博客管理功能
- **onex**: 大型云原生实战平台，企业级的云平台项目

## 主要特性

### 架构模式

- ✅ **清晰架构** - 遵循简洁架构设计，确保项目结构清晰、易维护
- ✅ **接口驱动** - Interface-driven development，便于测试和解耦
- ✅ **依赖注入** - 使用 Wire 进行编译时依赖注入
- ✅ **标准布局** - 遵循 golang-standards/project-layout 规范
- ✅ **版本化 API** - Biz 层支持 v1/v2 等版本化目录

### 技术栈

- **Web 框架**: Gin
- **ORM**: GORM
- **依赖注入**: Wire
- **配置管理**: Viper + Pflag
- **日志**: Zap
- **认证**: JWT (jwt-go)
- **授权**: Casbin
- **验证**: govalidator
- **CLI**: Cobra
- **gRPC**: grpc + protobuf + grpc-gateway

### 开发规范

- ✅ **目录规范** - 标准化的项目目录结构
- ✅ **代码规范** - 使用 golangci-lint 进行静态检查
- ✅ **日志规范** - 独立的日志包和错误码管理
- ✅ **错误处理** - 统一的错误码设计
- ✅ **测试覆盖** - 单元测试、性能测试、模糊测试
- ✅ **构建管理** - 高质量的 Makefile

### Web 功能

- ✅ Request ID
- ✅ 优雅关停
- ✅ 中间件支持
- ✅ 跨域处理 (CORS)
- ✅ 异常恢复 (Panic Recovery)
- ✅ RESTful API 规范
- ✅ OpenAPI 3.0 / Swagger 2.0 文档

## 使用方法

### 自动触发

当你在 Go 项目中执行以下操作时，Claude 会自动使用这个 skill：

```bash
# 创建新的 Go 项目
"帮我创建一个 Go Web 项目"

# 添加新功能
"添加用户管理功能"
"实现 JWT 认证"

# 重构代码
"重构这个 handler 使用依赖注入"
"优化这个函数的错误处理"

# 架构设计
"设计一个博客系统的架构"
"如何组织项目目录结构"
```

### 手动调用

你也可以通过 Skill 工具手动调用：

```
使用 golang-best-practices skill 帮我创建一个标准的 Go 项目结构
```

## 项目结构

```
.claude/skills/golang-best-practices/
├── SKILL.md                          # 核心最佳实践指南（主文件）
├── README.md                         # 本文件
├── init-project.sh                   # 项目初始化脚本
├── development-workflow.md           # 开发工作流和规范
├── architecture-design.md            # 架构设计指南
└── templates/                        # 文档模板
    ├── requirement-template.md       # 需求文档模板
    ├── design-template.md            # 设计文档模板
    ├── adr-template.md               # 架构决策记录模板
    └── architecture-review-checklist.md  # 架构评审清单
```

## 核心原则

### 1. 文档驱动

所有决策基于文档记录，使用模板：
- 需求文档 (requirement-template.md)
- 设计文档 (design-template.md)
- ADR 决策记录 (adr-template.md)

### 2. 小步快跑

- 将大任务拆分为 3-5 个阶段
- 每个阶段完成后确认
- 增量进步优于大爆炸式变更

### 3. 架构遵循

严格按照清晰架构的边界：
```
Handler (HTTP/gRPC)
    ↓
Biz (业务逻辑)
    ↓
Store (数据访问)
    ↓
Model (数据模型)
```

### 4. 接口驱动

- 所有层级使用接口定义
- 使用 mockgen 生成测试 mock
- 便于单元测试和解耦

### 5. 依赖注入

使用 Wire 进行依赖管理：
- wire.go 定义依赖关系
- wire_gen.go 自动生成
- 编译时检查，无运行时反射

## 代码示例

### 1. 创建新资源 (User)

按照以下顺序实现：

```
1. Model（数据模型）    - internal/myapp/model/user.go
   ↓
2. Store（数据访问）    - internal/myapp/store/user.go
   ↓
3. Biz（业务逻辑）      - internal/myapp/biz/v1/user/user.go
   ↓
4. Handler（HTTP接口）  - internal/myapp/handler/v1/user/user.go
   ↓
5. Wire（依赖注入）     - internal/myapp/wire.go
   ↓
6. Test（测试）         - *_test.go
```

### 2. 项目初始化

使用提供的脚本快速初始化项目：

```bash
cd .claude/skills/golang-best-practices
bash init-project.sh myproject
```

将创建完整的项目结构，包括：
- 标准目录布局
- Makefile
- 配置文件模板
- Wire 配置
- 基础中间件

### 3. 开发工作流

遵循 development-workflow.md 中定义的流程：

1. **需求分析** - 使用 requirement-template.md
2. **架构设计** - 使用 design-template.md 和 architecture-design.md
3. **实现计划** - 创建 IMPLEMENTATION_PLAN.md
4. **分阶段实现** - 3-5 个阶段，每阶段确认
5. **测试验证** - 单元测试 + 集成测试
6. **代码审查** - 使用 architecture-review-checklist.md

## 技术栈选型

### Web 框架

| 框架 | 优势 | 使用场景 |
|------|------|---------|
| Gin | 性能高、生态好、上手快 | REST API、HTTP 服务 ✅ |
| Echo | 中间件丰富 | REST API |
| Fiber | 极致性能 | 高并发场景 |

**推荐**: Gin（miniblog/onex 使用）

### ORM

| ORM | 优势 | 使用场景 |
|-----|------|---------|
| GORM | 功能全、生态好、支持钩子 | 通用场景 ✅ |
| ent | 类型安全、代码生成 | 复杂关系 |
| sqlx | 轻量、SQL 可控 | 性能要求高 |

**推荐**: GORM（miniblog/onex 使用）

### 依赖注入

| 工具 | 优势 | 使用场景 |
|------|------|---------|
| Wire | 编译时、无反射、类型安全 | 企业级项目 ✅ |
| dig | 运行时、灵活 | 中小型项目 |
| fx | Uber 出品、功能全 | 微服务 |

**推荐**: Wire（miniblog/onex 使用）

### 配置管理

| 工具 | 优势 | 使用场景 |
|------|------|---------|
| Viper | 功能全、支持多格式、环境变量 | 通用场景 ✅ |
| envconfig | 简单、环境变量 | 简单配置 |
| koanf | 轻量、灵活 | 自定义需求 |

**推荐**: Viper + Pflag（miniblog/onex 使用）

## 架构模式

### 清晰架构（Clean Architecture）

```
┌─────────────────────────────────────┐
│         Handler Layer               │  ← HTTP/gRPC 入口
│   (Gin/gRPC handlers)               │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│          Biz Layer                  │  ← 业务逻辑
│   (业务规则、权限检查)               │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│         Store Layer                 │  ← 数据访问
│   (CRUD、查询组装)                   │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│         Model Layer                 │  ← 数据模型
│   (GORM Models、Hooks)              │
└─────────────────────────────────────┘
```

### 依赖方向

- Handler 依赖 Biz（不直接访问 Store）
- Biz 依赖 Store（不直接访问 Model）
- Store 依赖 Model
- 所有依赖都是接口（Interface）

### 版本化

```go
// 支持 API 版本演进
internal/
  └── myapp/
      ├── biz/
      │   ├── v1/          // v1 版本业务逻辑
      │   │   ├── user/
      │   │   └── post/
      │   └── v2/          // v2 版本业务逻辑（未来）
      │       ├── user/
      │       └── post/
      └── handler/
          ├── v1/          // v1 版本 API
          └── v2/          // v2 版本 API
```

## 参考项目

### miniblog

- **仓库**: https://github.com/onexstack/miniblog
- **描述**: 小而美的 Go 实战项目，入门但不简单
- **功能**: 用户管理 + 博客管理
- **特点**:
  - 清晰的架构分层
  - 完整的认证授权
  - RESTful API + gRPC
  - 单元测试覆盖

### onex

- **仓库**: https://github.com/onexstack/onex
- **描述**: OneX 云原生实战平台，企业级云平台
- **功能**: 云原生 + 微服务 + Kubernetes
- **特点**:
  - 大规模项目组织
  - 微服务架构
  - 声明式编程
  - 完整的监控告警

## 常见问题

### Q1: 什么时候创建新版本 (v2)?

当业务逻辑出现不兼容变更时，例如：
- API 响应格式重大变更
- 业务规则重大调整
- 数据模型不兼容

### Q2: Handler 层可以直接访问 Store 吗?

不建议。应该通过 Biz 层，原因：
- Biz 层封装业务规则
- Biz 层处理权限检查
- Biz 层可能需要组合多个 Store 操作

### Q3: 什么时候使用 errgroup?

当需要并发执行多个操作且需要：
- 等待所有操作完成
- 任一操作失败时取消其他操作
- 限制并发数量

参考 miniblog 的 List 实现（internal/apiserver/biz/v1/user/user.go:205-234）

### Q4: Wire 生成失败怎么办?

常见原因：
1. 循环依赖 - 检查 wire.go 中的依赖关系
2. 缺少 Provider - 确保所有依赖都有对应的 New 函数
3. 类型不匹配 - 检查接口实现

```bash
# 重新生成
cd internal/myapp
wire
```

## 更新记录

### v1.0.0 (2025-12-24)

- ✅ 基于 miniblog 和 onex 项目创建
- ✅ 提取清晰架构模式
- ✅ 整理 Gin + GORM + Wire 技术栈
- ✅ 添加完整的代码示例
- ✅ 包含项目初始化脚本
- ✅ 整合开发工作流和架构设计
- ✅ 提供文档模板和评审清单

## 贡献

本 Skill 基于以下项目的分析：
- [onexstack/miniblog](https://github.com/onexstack/miniblog) - 孔令飞
- [onexstack/onex](https://github.com/onexstack/onex) - 孔令飞
- [golang-standards/project-layout](https://github.com/golang-standards/project-layout)

## 许可证

MIT

---

**提示**: 使用此 Skill 时，Claude 会自动参考 SKILL.md 中的最佳实践，并结合 development-workflow.md 和 architecture-design.md 提供完整的开发指导。

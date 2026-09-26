---
name: golang-best-practices
description: 为 Go 服务端代码提供创建、维护、重构和审查指导；当请求涉及 Go/Golang、HTTP 或 gRPC 服务、并发、context、错误处理、Go 测试或构建时使用。不用于前端实现、纯语言入门问答或没有 Go 约束的通用产品设计。
---

# Go 工程最佳实践

面向新建和现有 Go 项目的工程指导，重点是清晰的包边界、错误处理、并发安全、可测试性和可观测交付。

> 文中的 HTTP、数据库、JWT、GORM、Wire 和 golangci-lint 都是可选方案。先读取项目依赖和配置，再复用已有方案；不要因为示例而新增依赖。

## 何时使用

- 为新 Go 服务选择项目结构、模块边界和依赖；
- 创建或重构 HTTP/gRPC handler、service、store 和 middleware；
- 审查并发、context、错误、配置、认证、日志和资源生命周期；
- 补充单元、集成、竞态和构建验证。

不负责固定脚手架或无依据的框架迁移。新项目先输出架构决策和目录建议，再使用 `go mod init` 及目标框架的官方文档开始实现。

## 项目勘察

开始修改前，先读取并总结：

1. `go.mod`、`go.sum`、`go` 版本和现有依赖；
2. `cmd/`、`internal/`、`pkg/`、`api/` 及入口文件；
3. HTTP/gRPC 框架、数据库、迁移、配置、日志和认证方案；
4. `Makefile`、CI、lint、test、build 和 Docker 配置；
5. 现有错误类型、context 传递和资源关闭方式。

先遵循项目已有约定，再提出新增依赖或迁移建议。

## 核心原则

1. **包边界清晰**：按业务能力或稳定职责组织包，避免巨大的 `utils` 和循环依赖。
2. **接口由使用方定义**：只为替换、测试或跨边界需要定义接口，不为每个 struct 机械建接口。
3. **显式依赖**：通过构造函数传递数据库、客户端、时钟和配置，不在业务包中创建全局连接。
4. **错误可诊断**：使用 `%w` 保留原因，使用 `errors.Is/As` 判断类型；对外响应不要泄漏内部细节。
5. **context 贯穿请求**：把请求 context 传给下游 I/O、数据库和 RPC；不要在请求路径用 `context.Background()` 替代调用方 context。
6. **并发有边界**：明确 goroutine 所属、退出条件、取消方式和共享状态保护；优先使用 channel 或 mutex 的简单方案。
7. **资源有生命周期**：关闭 response body、数据库连接、ticker、文件和 goroutine；服务器支持优雅关闭。
8. **先测量再优化**：基于 benchmark、profile、trace 或指标处理性能问题。

## 推荐目录形状

按服务规模调整，不要求机械套用：

```text
project/
├── cmd/<service>/main.go       # 可执行程序入口
├── internal/
│   ├── app/                    # 应用组装和生命周期
│   ├── handler/                # HTTP/gRPC 边界
│   ├── service/                # 业务用例
│   ├── store/                  # 数据访问
│   └── model/                  # 领域或持久化模型
├── api/                        # 对外协议定义（如项目采用）
├── migrations/                 # 数据库迁移（如需要）
├── configs/                    # 非敏感默认配置（如项目采用）
└── go.mod
```

小项目可以合并层级；只有真正需要跨项目复用时才使用 `pkg/`。不要为了“Clean Architecture”提前创建空层。

## HTTP 和服务生命周期

- handler 只负责解析输入、调用用例和映射响应；
- service 不依赖 HTTP 细节；store 不决定 API 状态码；
- 所有外部 HTTP client 设置 timeout，并检查状态码和 response body；
- 服务器使用 `http.Server`，监听、信号取消和 `Shutdown` 有明确错误处理；
- 中间件按顺序处理 request ID、日志、认证、限流和恢复，避免吞掉 panic 或错误；
- 分页、排序、过滤和幂等语义写入 API 契约。

## 配置与安全

- 使用 `os.LookupEnv` 或项目已有配置库区分缺失值与空值；
- 密钥、数据库密码和令牌只来自环境或密钥管理系统，不提交到仓库；
- 密码使用成熟的密码哈希实现，数据库字段和 API 响应都不暴露明文密码；
- 认证与授权分开，授权检查资源归属和操作权限；
- 日志不记录密码、token、完整 Cookie 和敏感个人信息；
- 第三方依赖和生成工具使用可审计、已锁定的版本。

## 错误、日志与可观测性

```go
if err != nil {
    return fmt.Errorf("load user %q: %w", userID, err)
}

if errors.Is(err, sql.ErrNoRows) {
    return ErrNotFound
}
```

- 区分客户端错误、业务错误和基础设施错误；
- 日志包含 request ID、操作和可定位上下文，不重复打印同一错误；
- 指标和 tracing 在边界处建立，不把 observability 代码散落到领域逻辑；
- health/readiness 检查区分进程存活和依赖可用性。

## 测试与验证

至少覆盖：

- 业务用例成功、失败和边界；
- handler 的输入校验、状态码和错误响应；
- store 的事务、超时和依赖替换；
- 并发安全、取消、重试和优雅关闭；
- 认证、授权、敏感字段和日志脱敏。

按项目已有命令执行：

```text
gofmt → go vet ./... → go test ./... → go test -race ./... → go build ./...
```

如果项目已配置，再运行 `staticcheck`、`golangci-lint`、benchmark、集成测试和容器构建。

## 交付清单

- [ ] 包边界和依赖方向清晰，没有无必要的全局状态；
- [ ] context、错误、超时和资源关闭可追踪；
- [ ] 配置和密钥安全，密码只保存哈希；
- [ ] API 错误、日志、指标和健康检查符合项目约定；
- [ ] 单元、集成、竞态、lint 和构建验证通过；
- [ ] 变更说明了接口、迁移、配置和部署影响。

## 详细参考

- [`references/architecture-patterns.md`](references/architecture-patterns.md)：架构、依赖、并发和安全参考；
- [`references/development-workflow.md`](references/development-workflow.md)：需求、实现、测试和审查流程；
- [`scripts/`](scripts/)：迁移、lint、Wire 和 Docker 辅助脚本；
- [`templates/docker/`](templates/docker/)：部署模板。

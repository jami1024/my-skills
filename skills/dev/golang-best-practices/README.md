# Go 最佳实践 Skill

面向新建和现有 Go 项目的工程实践，帮助建立清晰、可测试、可观测和可维护的服务端代码结构。

## 适用场景

```text
“为这个服务推荐 Go 项目架构”
“设计 Go HTTP API 的包结构和依赖边界”
“审查这段 Go 代码的并发、错误和资源管理”
“给 Go 服务补充测试、竞态检查和优雅关闭”
```

## 使用流程

### 新项目

1. 明确服务类型、部署目标、HTTP/gRPC、数据库、认证和可观测性要求；
2. 根据团队约束比较标准库、现有框架和依赖；
3. 输出模块边界、目录结构、生命周期和测试方案；
4. 用户确认后使用 `go mod init` 和目标框架文档开始实现。

### 现有项目

先读取并总结：

- `go.mod`、`go.sum`、Go 版本和依赖；
- `cmd/`、`internal/`、`pkg/`、API 和入口文件；
- HTTP/gRPC、数据库、配置、日志、认证和迁移方案；
- Makefile、CI、lint、test、build 和 Docker 配置。

先复用项目已有方案，不因为示例而新增依赖或迁移框架。

## 核心规则

- 按业务能力或稳定职责组织包，避免巨大的 `utils` 和循环依赖；
- 接口由使用方定义，只在替换、测试或跨边界需要时抽象；
- 通过构造函数传递依赖，不在业务包创建全局连接；
- 使用 `%w`、`errors.Is/As` 保留和判断错误原因；
- 将请求 `context` 传给数据库、HTTP 和 RPC，不用 `context.Background()` 覆盖调用方取消信号；
- 明确 goroutine 的退出、取消和共享状态保护；
- 设置 HTTP client 和数据库操作的 timeout，关闭 response body 和其他资源；
- 密钥来自环境或密钥管理系统，密码只保存哈希；
- 不在脚本中盲目安装未锁定版本的生成工具；
- 先测量再做性能优化。

## 推荐目录形状

按规模调整，不要求机械套用：

```text
project/
├── cmd/<service>/main.go       # 可执行程序入口
├── internal/
│   ├── app/                    # 应用组装和生命周期
│   ├── handler/                # HTTP/gRPC 边界
│   ├── service/                # 业务用例
│   ├── store/                  # 数据访问
│   └── model/                  # 领域或持久化模型
├── api/                        # 协议定义（如项目采用）
├── migrations/                 # 数据库迁移（如需要）
└── go.mod
```

小项目可以合并层级；只有真正需要跨项目复用时才使用 `pkg/`。

## 验证

按项目已有命令执行：

```text
gofmt → go vet ./... → go test ./... → go test -race ./... → go build ./...
```

项目已配置时，再运行 `staticcheck`、`golangci-lint`、集成测试、benchmark 和容器构建。

交付前确认：

- 成功、错误、超时、取消和权限路径可测试；
- 服务器支持优雅关闭，外部资源有明确生命周期；
- 日志不包含密码、token、Cookie 或敏感个人信息；
- 没有无依据的全局状态、接口和性能优化；
- 变更说明了 API、迁移、配置和部署影响。

## 相关文件

- [`SKILL.md`](SKILL.md)：核心规则和验证清单；
- [`references/architecture-patterns.md`](references/architecture-patterns.md)：详细架构、并发和安全参考；
- [`references/development-workflow.md`](references/development-workflow.md)：开发流程和审查步骤；
- [`scripts/`](scripts/)：迁移、lint、Wire 和 Docker 辅助脚本；
- [`templates/docker/`](templates/docker/)：部署模板。

## 许可证

MIT

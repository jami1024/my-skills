# Go 最佳实践 Skill

面向新建和现有 Go 项目的工程实践，帮助建立清晰、可测试、可观测和可维护的服务端代码结构。

## 适用场景

```text
“为这个服务推荐 Go 项目架构”
“设计 Go HTTP API 的包结构和依赖边界”
“在现有 Go 服务中增加一个跨模块能力，保留当前结构”
“审查这个 Go 服务的依赖边界和资源生命周期”
```

## 使用流程

### 新项目

1. 明确当前真正需要的服务行为、协议和运行方式；
2. 从最小可运行结构开始，按需要选择业务包、外部依赖和生命周期边界；
3. 说明组织方式和验证切片；小型服务可以同包实现，不预建分层或工具体系；
4. 方案明确且在用户授权范围内时实现，用项目命令验证行为。

### 现有项目

先读取并总结：

- `go.mod`、`go.sum`、Go 版本和依赖；
- 实际入口、包组织、公开 API 与相近实现；
- HTTP/gRPC、数据库、配置、日志、认证和迁移方案；
- Makefile、CI、lint、test、build 和 Docker 配置。

先复用项目已有方案，不因为示例而新增依赖或迁移框架。

## 规则与验证

核心规则、组织方式选择、测试阶梯和交付清单在 [`SKILL.md`](SKILL.md) 中维护；参考资料分别解释包边界决策与实施切片，避免重复同一套 CRUD 示例。

验证按项目已有命令执行；项目已配置时再跑 `staticcheck`、`golangci-lint`、集成测试、benchmark 和容器构建。

## 相关文件

- [`SKILL.md`](SKILL.md)：核心规则和验证清单；
- [`references/architecture-patterns.md`](references/architecture-patterns.md)：包组织、接口、数据契约和资源所有权的选择依据；
- [`references/development-workflow.md`](references/development-workflow.md)：按任务实施、验证与范围审查；
- [`scripts/README.md`](scripts/README.md)：可选工具的脚本示例及适用条件；
- [`templates/docker/`](templates/docker/)：按需使用的 Docker 部署示例。

## 许可证

MIT

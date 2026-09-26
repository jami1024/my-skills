# FastAPI 最佳实践 Skill

面向新建和现有 FastAPI 项目的工程指导，重点是 API 边界、异步资源管理、类型安全、安全和可验证交付。

## 适用场景

```text
“为这个产品设计 FastAPI 项目架构”
“在现有 FastAPI 项目中添加用户 API”
“审查这个 Pydantic/SQLAlchemy 实现”
“检查 FastAPI API 的安全和测试问题”
```

## 使用流程

1. 读取 `pyproject.toml`、lockfile、Python 版本和现有 scripts；
2. 检查 FastAPI、Pydantic、SQLAlchemy、数据库驱动和认证依赖版本；
3. 识别入口、路由、schema、模型、服务、迁移和测试目录；
4. 复用现有技术栈，不无理由引入新依赖或迁移；
5. 交付前执行 format、lint、typecheck、test、migration check 和 build。

新项目先输出架构决策和目录建议，再使用项目选择的包管理器初始化。这个 Skill 不提供固定脚手架。

## 核心规则

- 路由负责 HTTP 边界，服务负责业务逻辑，数据层负责持久化；
- SQLAlchemy 模型与 Pydantic 输入/输出 schema 分离；
- 异步路由使用异步数据库和客户端，避免阻塞事件循环；
- 使用 dependency injection 管理 session、认证和请求级资源；
- 新代码使用 Pydantic v2 风格：`field_validator`、`ConfigDict`、`pattern`；
- 密码只保存哈希，密钥来自环境或密钥系统，错误响应不泄漏内部细节；
- 明确事务边界、错误映射、响应模型、分页和权限；
- 覆盖成功、验证失败、未认证、无权限、404、冲突、超时和外部服务失败。

## 推荐目录形状

按项目规模调整：

```text
app/
├── main.py
├── core/                   # settings、安全、全局依赖
├── api/v1/endpoints/       # 按领域组织路由
├── models/                 # SQLAlchemy 模型
├── schemas/                # Pydantic 输入/输出模型
├── services/               # 业务用例
├── repositories/           # 需要时使用
├── db/                     # engine、session、迁移集成
└── tests/                  # 单元、集成和 API 测试
```

## 常用决策

| 领域 | 决策原则 |
|---|---|
| 配置 | 使用 `pydantic-settings`，敏感值来自环境或密钥系统 |
| 数据库 | 异步项目使用 `async_sessionmaker`，按请求管理 session |
| 校验 | schema 负责边界校验，业务规则放在服务层 |
| 认证 | 区分身份认证和资源授权，避免只检查是否登录 |
| 错误 | 统一状态码和错误格式，不返回 SQL 或堆栈 |
| 任务 | 重要任务使用可靠队列，不把关键事务交给普通后台任务 |
| 测试 | 通过依赖覆盖隔离数据库和外部服务 |

## 相关文件

- [`SKILL.md`](SKILL.md)：核心规则、Pydantic、数据库、安全和验证清单；
- [`references/architecture-patterns.md`](references/architecture-patterns.md)：详细架构和安全参考；
- [`references/development-workflow.md`](references/development-workflow.md)：开发流程和审查步骤；
- [`references/testing-and-production-patterns.md`](references/testing-and-production-patterns.md)：测试和生产模式；
- [`scripts/`](scripts/)：迁移、lint 和 Docker 辅助脚本；
- [`templates/docker/`](templates/docker/)：部署模板；
- [`templates/`](templates/)：需求、设计和评审模板。

## 参考资源

- [FastAPI 官方文档](https://fastapi.tiangolo.com/)
- [Pydantic 文档](https://docs.pydantic.dev/)
- [SQLAlchemy 异步文档](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)

## 许可证

MIT

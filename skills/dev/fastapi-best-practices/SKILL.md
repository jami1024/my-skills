---
name: fastapi-best-practices
description: 为 FastAPI/Python API 提供创建、维护、重构和审查指导；当请求涉及 FastAPI、Pydantic、SQLAlchemy、认证、异步 API 或 API 测试时使用。不用于纯 Python 脚本、前端实现或没有 FastAPI 约束的通用架构讨论。
---

# FastAPI 工程最佳实践

面向新建和现有 FastAPI 项目的工程指导，重点是清晰的 API 边界、类型安全、异步资源管理、安全性和可验证交付。

> 文中的 PostgreSQL、SQLAlchemy、Redis、JWT 和 Pydantic Settings 只是常见方案。先读取项目依赖和配置，再复用已有方案；不要因为示例而新增依赖。

## 何时使用

- 设计 FastAPI 项目结构、路由、依赖和服务层；
- 创建或重构 Pydantic schema、SQLAlchemy 模型和数据库会话；
- 实现认证、授权、配置、错误处理和后台任务；
- 审查 API 的异步、性能、安全和测试问题。

不负责固定脚手架或无依据的技术栈迁移。新项目先输出架构决策，再使用官方工具和项目选择的包管理器初始化。

## 项目勘察

开始修改前，先读取并总结：

1. `pyproject.toml`、`requirements*.txt`、lockfile 和 Python 版本；
2. FastAPI、Pydantic、SQLAlchemy、数据库驱动和认证依赖版本；
3. 应用入口、路由注册、配置、依赖、模型、schema、迁移和测试目录；
4. lint、format、typecheck、test 和 build 命令；
5. Docker、环境变量和部署约定。

先复用项目已有边界，再提出新增依赖或迁移建议。

## 核心原则

1. **按领域组织**：路由、schema、服务、模型和测试围绕业务功能组织，而不是无限堆在单一文件。
2. **关注点分离**：路由负责 HTTP 边界，服务负责业务逻辑，repository 或数据层负责持久化。
3. **异步边界清晰**：异步路由使用异步数据库和客户端；同步库不要直接阻塞事件循环。
4. **显式依赖**：使用 FastAPI dependency injection 管理认证、数据库会话和请求级资源。
5. **输入输出分离**：SQLAlchemy 模型不直接作为公开 API schema；按接口定义响应字段。
6. **安全默认**：密钥来自环境或密钥管理系统；密码只保存哈希；错误响应不泄漏内部细节。
7. **先验证再抽象**：重复且稳定的逻辑再提取服务、依赖或通用组件。

## 推荐目录形状

按项目规模和部署方式调整：

```text
app/
├── main.py                 # FastAPI 实例和 lifespan
├── core/                   # settings、安全、全局依赖
├── api/
│   └── v1/
│       ├── router.py
│       └── endpoints/      # 按领域组织路由
├── models/                 # SQLAlchemy 模型
├── schemas/                # Pydantic 输入/输出模型
├── services/               # 业务用例
├── repositories/           # 持久化访问（需要时使用）
├── db/                     # engine、session、base、迁移集成
└── tests/                  # 单元、集成和 API 测试
```

小项目可以合并目录，但不要让路由函数同时承担验证、业务和数据库细节。

## Pydantic 与 API schema

使用项目当前 Pydantic 主版本。新项目使用 Pydantic v2 风格：

```python
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

class UserCreate(BaseModel):
    email: EmailStr
    username: str = Field(min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_]+$")
    password: str = Field(min_length=8)

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        if not any(char.isdigit() for char in value):
            raise ValueError("密码必须包含数字")
        return value

class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    username: str
```

规则：

- 不在新代码中使用 `@validator`、`class Config` 或 Pydantic v1 的 `regex=`；
- 请求 schema、响应 schema 和数据库模型分离；
- 不把密码、令牌或内部字段放入响应 schema；
- 校验错误应映射为稳定、可理解的 API 响应。

## 数据库与异步会话

- 使用项目现有的 SQLAlchemy 版本和迁移工具；
- 异步项目使用 `create_async_engine` 和 `async_sessionmaker`；
- 每个请求获取并释放自己的 session，不把 session 放入全局可变状态；
- 事务边界由服务或用例明确管理；
- 查询只加载需要的字段，避免 N+1；
- 不在请求处理中执行未检查的阻塞 I/O。

## 配置与安全

- 使用 `pydantic-settings` 管理配置，并从环境变量或密钥系统读取敏感值；
- 不把真实密钥、默认生产密码或可用令牌写入仓库；
- CORS、Trusted Host、HTTPS、Cookie 和 CSRF 策略根据部署环境明确配置；
- 认证负责确认身份，授权负责确认资源权限；
- 密码使用成熟密码哈希库，绝不保存明文；
- 日志避免记录密码、令牌、完整 Cookie 和敏感个人信息。

## 路由、错误和响应

- 路由只处理 HTTP 参数、依赖、状态码和响应模型；
- 使用明确的 `response_model`、状态码和分页约定；
- 将领域错误映射为稳定的客户端错误，不直接暴露 SQL 或堆栈；
- 统一处理验证错误、认证错误、权限错误、资源不存在和冲突；
- 后台任务不应承担必须保证完成的事务；重要任务使用可靠队列或持久化方案。

## 测试与验证

至少覆盖：

- schema 边界和业务规则；
- 路由成功、验证失败、未认证、无权限、404 和冲突；
- 数据库事务、迁移和依赖覆盖；
- 外部服务失败、超时和重试；
- 配置缺失和生产构建。

按项目已有命令执行：

```text
format → lint → typecheck → unit/integration test → migration check → build
```

API 测试使用项目已有客户端；异步测试通常使用 `httpx.AsyncClient` 与 `ASGITransport`，并通过依赖覆盖隔离数据库和外部服务。

## 交付清单

- [ ] 输入、输出和数据库模型边界清晰；
- [ ] 异步资源正确创建、提交、回滚和释放；
- [ ] 认证、授权、CORS 和敏感配置已检查；
- [ ] 错误响应稳定且不泄漏内部信息；
- [ ] 迁移、测试、lint、类型检查和构建通过；
- [ ] 文档或变更说明记录了 API、配置、迁移和部署影响。

## 详细参考

- [`references/architecture-patterns.md`](references/architecture-patterns.md)：架构、技术选型和安全示例；
- [`references/development-workflow.md`](references/development-workflow.md)：需求、实现、测试和审查流程；
- [`references/testing-and-production-patterns.md`](references/testing-and-production-patterns.md)：测试和生产模式；
- [`scripts/`](scripts/)：数据库迁移、lint 和 Docker 辅助脚本；
- [`templates/docker/`](templates/docker/)：部署模板。

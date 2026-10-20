# FastAPI 项目结构与分层

示例只说明职责和取舍，不是可直接运行的完整应用。先沿用项目已有版本、依赖和约定；仅在当前问题需要时读取，不因示例引入工具、依赖或新的架构层。

## 🏗️ FastAPI 项目架构模式

### 1. 分层架构（项目采用时）

目录可以按技术职责分层，也可以在 `app/<domain>/` 内聚合一个领域的端点、schema、服务和模型。先沿用现有组织；小服务不必预建 service、repository 等空层。下面按职责分层的示例用于说明边界，不要求搬移现有文件。

```
┌─────────────────────────────────────────┐
│          API Layer (Endpoints)          │  ← HTTP 请求/响应
├─────────────────────────────────────────┤
│        Application Layer (Services)      │  ← 业务逻辑
├─────────────────────────────────────────┤
│         Domain Layer (Models)           │  ← 核心领域模型
├─────────────────────────────────────────┤
│    Infrastructure Layer (Database)       │  ← 数据持久化
└─────────────────────────────────────────┘
```

#### 项目结构
```
app/
├── api/                    # API 层
│   └── v1/
│       └── endpoints/
│           ├── users.py    # 端点：处理 HTTP 请求
│           └── posts.py
├── services/               # 应用层
│   ├── user_service.py     # 业务逻辑
│   └── post_service.py
├── models/                 # 领域层
│   ├── user.py            # 领域模型
│   └── post.py
├── schemas/               # 数据传输对象
│   ├── user.py
│   └── post.py
└── db/                    # 基础设施层
    ├── session.py         # 数据库会话
    └── repositories/      # 仓储模式（可选）
```

#### 层次职责

**API 层（Endpoints）**
- 接收 HTTP 请求
- 验证输入（Pydantic）
- 调用 Service 层
- 返回 HTTP 响应

```python
@router.post("/users", response_model=UserResponse)
async def create_user(
    data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """端点只做路由和委托"""
    service = UserService(db)
    user = await service.create_user(data)
    return user
```

**应用层（Services）**
- 实现业务逻辑
- 协调多个领域对象
- 按项目约定拥有事务，或参与外层已有事务
- 不依赖 HTTP 细节

以下局部示例要求用例拥有一个没有前置 SQL/活动事务的新 session，并采用 `expire_on_commit=False`；唯一性查询位于 begin 内。外层请求已持有事务时不能照搬这个 begin，使用 [事务参考](transactions.md) 中的参与方式。

```python
class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_user(self, data: UserCreate) -> User:
        async with self.db.begin():
            if await self._email_exists(data.email):
                raise ValueError("Email already exists")
            user = User(email=data.email, username=data.username)
            self.db.add(user)
            await self.db.flush()
        return user
```

**模型（Models）**
- 小项目可以复用 ORM 实体承载简单业务行为，以下示例采用这种方式
- ORM 模型依赖数据库映射，并非与存储无关的纯领域模型
- 只有复杂领域规则或多种持久化边界确实需要时，才另建独立领域模型

```python
class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(unique=True)
    username: Mapped[str]

    def can_edit_post(self, post: Post) -> bool:
        """领域逻辑"""
        return post.author_id == self.id or self.is_admin
```

**基础设施层（Database）**
- 数据库连接
- ORM 配置
- 外部服务集成

---

### 2. 仓储模式（Repository Pattern）- 可选

适用于复杂查询或需要隔离数据源的场景，不为每个模型机械创建抽象接口。以下 `create` 仅加入当前 session，事务由调用方明确的请求或用例边界统一结束；这个 repository 示例本身不提供提交保证。

```python
# app/repositories/user_repository.py
from abc import ABC, abstractmethod

class UserRepository(ABC):
    @abstractmethod
    async def get_by_id(self, user_id: int) -> User | None:
        pass

    @abstractmethod
    async def get_by_email(self, email: str) -> User | None:
        pass

    @abstractmethod
    async def create(self, user: User) -> User:
        pass

class SQLAlchemyUserRepository(UserRepository):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, user_id: int) -> User | None:
        return await self.db.get(User, user_id)

    async def get_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, user: User) -> User:
        self.db.add(user)
        await self.db.flush()
        return user

# 依赖注入
async def get_user_repository(
    db: AsyncSession = Depends(get_db)
) -> UserRepository:
    return SQLAlchemyUserRepository(db)

# 使用
class UserService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def create_user(self, data: UserCreate) -> User:
        existing = await self.user_repo.get_by_email(data.email)
        if existing:
            raise ValueError("Email exists")

        user = User(**data.model_dump())
        return await self.user_repo.create(user)
```

---

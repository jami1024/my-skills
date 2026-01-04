---
name: fastapi-best-practices
description: 当用户需要创建新的 FastAPI 项目、构建 API、组织 FastAPI 代码结构时使用。触发词：FastAPI、API 项目、新建 FastAPI、FastAPI 架构、API 开发
---

# FastAPI 最佳实践 Skill

这个 skill 基于生产环境中验证的 FastAPI 最佳实践，帮助你构建可扩展、易维护的 FastAPI 应用。

## 📋 开发工作流

关于通用的软件开发流程（需求分析、技术设计、代码审查、测试策略、项目管理等），请参考 **development-workflow skill**。

本文档专注于 **FastAPI 特定** 的开发实践，包括：
- FastAPI 项目结构和架构模式
- Pydantic 最佳实践
- SQLAlchemy 异步 ORM 使用
- 依赖注入和中间件
- 认证授权实现
- 性能优化技巧

## 核心原则

1. **领域驱动设计** - 按业务领域组织代码，而非技术层
2. **关注点分离** - 清晰分离请求验证、业务逻辑和数据访问层
3. **异步优先** - 充分利用 FastAPI 的异步特性
4. **依赖注入** - 使用 FastAPI 的依赖系统进行验证和资源管理

## 项目结构

创建新项目时，使用以下结构：

```
project_name/
├── app/
│   ├── __init__.py
│   ├── main.py              # 应用入口点
│   ├── core/                # 核心配置
│   │   ├── __init__.py
│   │   ├── config.py        # 配置设置
│   │   ├── security.py      # 安全相关
│   │   └── dependencies.py  # 全局依赖
│   ├── api/                 # API 路由
│   │   ├── __init__.py
│   │   └── v1/              # API 版本控制
│   │       ├── __init__.py
│   │       ├── endpoints/   # 按领域组织的端点
│   │       │   ├── __init__.py
│   │       │   ├── users.py
│   │       │   ├── posts.py
│   │       │   └── auth.py
│   │       └── dependencies.py
│   ├── models/              # 数据库模型
│   │   ├── __init__.py
│   │   ├── user.py
│   │   └── post.py
│   ├── schemas/             # Pydantic 模型
│   │   ├── __init__.py
│   │   ├── user.py
│   │   └── post.py
│   ├── services/            # 业务逻辑层
│   │   ├── __init__.py
│   │   ├── user_service.py
│   │   └── post_service.py
│   ├── db/                  # 数据库相关
│   │   ├── __init__.py
│   │   ├── base.py          # 导入所有模型
│   │   └── session.py       # 数据库会话
│   └── tests/               # 测试
│       ├── __init__.py
│       ├── conftest.py
│       └── api/
│           └── v1/
├── alembic/                 # 数据库迁移
├── .env                     # 环境变量
├── .env.example             # 环境变量示例
├── requirements.txt         # 或 pyproject.toml
└── README.md
```

## Pydantic 最佳实践

### 1. Schema 设计

```python
# schemas/user.py
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    """基础用户 schema，包含共享属性"""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    full_name: Optional[str] = None

class UserCreate(UserBase):
    """创建用户时的 schema"""
    password: str = Field(..., min_length=8)

    @validator('password')
    def validate_password_strength(cls, v):
        # 自定义验证逻辑
        if not any(char.isdigit() for char in v):
            raise ValueError('密码必须包含数字')
        return v

class UserUpdate(BaseModel):
    """更新用户时的 schema - 所有字段可选"""
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    full_name: Optional[str] = None

class UserInDB(UserBase):
    """数据库中的用户 schema"""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # 允许从 ORM 模型创建

class UserResponse(UserBase):
    """API 响应 schema - 不包含敏感信息"""
    id: int
    is_active: bool
```

### 2. Pydantic 特性利用

- 使用 `EmailStr`、`HttpUrl` 等内置类型进行验证
- 使用 `Field()` 添加约束和文档
- 使用 `@validator` 进行复杂验证
- 使用 `Config.from_attributes = True` 从 ORM 模型创建实例
- 为不同操作创建不同的 schema（Create、Update、Response）

## 异步/同步路由指南

### 1. 何时使用 async

```python
# ✅ 正确：异步路由用于 I/O 操作
@router.get("/users/{user_id}")
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    """
    异步路由 + 异步数据库操作
    FastAPI 使用 await，不会阻塞事件循环
    """
    user = await db.get(User, user_id)
    return user

# ✅ 正确：同步路由用于 CPU 密集型操作
@router.post("/process")
def process_data(data: ProcessRequest):
    """
    同步路由，FastAPI 会在线程池中运行
    不会阻塞事件循环
    """
    result = cpu_intensive_operation(data)
    return result

# ❌ 错误：异步路由中执行阻塞操作
@router.get("/bad")
async def bad_example():
    # 这会阻塞事件循环！
    time.sleep(5)
    return {"status": "done"}

# ✅ 修正：使用 run_in_executor 或改为同步路由
@router.get("/good")
def good_example():
    # FastAPI 会在线程池中运行
    time.sleep(5)
    return {"status": "done"}
```

### 2. 异步最佳实践

- **I/O 操作**（数据库、HTTP 请求、文件读写）→ 使用 async/await
- **CPU 密集型操作**（数据处理、图像处理）→ 使用同步路由
- **混合操作** → 使用 `asyncio.to_thread()` 或 `run_in_executor()`
- 如果不确定 → 使用同步路由（FastAPI 会自动处理）

## 依赖注入最佳实践

### 1. 数据库会话依赖

```python
# db/session.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

engine = create_async_engine(settings.DATABASE_URL, echo=True)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_db() -> AsyncSession:
    """数据库会话依赖"""
    async with async_session() as session:
        yield session
```

### 2. 验证依赖

```python
# api/v1/dependencies.py
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

async def valid_user_id(
    user_id: int,
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    验证用户 ID 是否存在
    FastAPI 会缓存此依赖的结果，在同一请求中不会重复查询
    """
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {user_id} not found"
        )
    return user

async def valid_post_id(
    post_id: int,
    db: AsyncSession = Depends(get_db)
) -> Post:
    """验证文章 ID"""
    post = await db.get(Post, post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post {post_id} not found"
        )
    return post

# 使用依赖
@router.put("/users/{user_id}/posts/{post_id}")
async def update_post(
    post_data: PostUpdate,
    user: User = Depends(valid_user_id),  # 自动验证
    post: Post = Depends(valid_post_id),  # 自动验证
    db: AsyncSession = Depends(get_db)
):
    """
    valid_user_id 和 valid_post_id 会自动执行
    如果验证失败，会自动返回 404
    """
    # 直接使用已验证的 user 和 post
    if post.author_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    # 更新逻辑...
    return post
```

### 3. 认证依赖

```python
# core/security.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """获取当前认证用户"""
    token = credentials.credentials
    payload = decode_jwt(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )

    user = await db.get(User, payload['user_id'])
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """获取当前活跃用户（依赖链）"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
```

### 4. 依赖缓存

```python
# FastAPI 在请求范围内缓存依赖结果
@router.get("/example")
async def example(
    user1: User = Depends(get_current_user),
    user2: User = Depends(get_current_user),  # 使用缓存结果，不会重复查询
):
    # user1 和 user2 是同一个对象
    assert user1 is user2
    return {"user": user1}
```

## 服务层模式

```python
# services/user_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate

class UserService:
    """用户业务逻辑层"""

    @staticmethod
    async def create_user(db: AsyncSession, user_data: UserCreate) -> User:
        """创建新用户"""
        # 检查邮箱是否已存在
        stmt = select(User).where(User.email == user_data.email)
        result = await db.execute(stmt)
        if result.scalar_one_or_none():
            raise ValueError("Email already registered")

        # 创建用户
        user = User(
            email=user_data.email,
            username=user_data.username,
            hashed_password=hash_password(user_data.password)
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: int) -> User | None:
        """通过 ID 获取用户"""
        return await db.get(User, user_id)

    @staticmethod
    async def list_users(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100
    ) -> list[User]:
        """获取用户列表"""
        stmt = select(User).offset(skip).limit(limit)
        result = await db.execute(stmt)
        return result.scalars().all()

    @staticmethod
    async def update_user(
        db: AsyncSession,
        user: User,
        user_data: UserUpdate
    ) -> User:
        """更新用户"""
        update_data = user_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)

        await db.commit()
        await db.refresh(user)
        return user
```

## 路由端点模式

```python
# api/v1/endpoints/users.py
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.services.user_service import UserService
from app.api.v1.dependencies import valid_user_id

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    创建新用户

    - **email**: 有效的邮箱地址
    - **username**: 3-50 字符
    - **password**: 至少 8 字符，包含数字
    """
    try:
        user = await UserService.create_user(db, user_data)
        return user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user: User = Depends(valid_user_id)):
    """
    通过 ID 获取用户

    依赖 valid_user_id 自动验证用户是否存在
    """
    return user

@router.get("/", response_model=list[UserResponse])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """获取用户列表"""
    users = await UserService.list_users(db, skip, limit)
    return users

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_data: UserUpdate,
    user: User = Depends(valid_user_id),
    db: AsyncSession = Depends(get_db)
):
    """更新用户信息"""
    updated_user = await UserService.update_user(db, user, user_data)
    return updated_user
```

## 配置管理

```python
# core/config.py
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    """应用配置"""
    # API
    PROJECT_NAME: str = "FastAPI Project"
    VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"

    # 数据库
    DATABASE_URL: str

    # 安全
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS
    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:3000"]

    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    """获取缓存的配置"""
    return Settings()

# 使用
settings = get_settings()
```

## 错误处理

```python
# main.py
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError

app = FastAPI()

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """处理验证错误"""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": exc.errors(),
            "body": exc.body
        }
    )

@app.exception_handler(IntegrityError)
async def integrity_exception_handler(request: Request, exc: IntegrityError):
    """处理数据库完整性错误"""
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": "Database integrity error"}
    )

class CustomException(Exception):
    """自定义异常"""
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code

@app.exception_handler(CustomException)
async def custom_exception_handler(request: Request, exc: CustomException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message}
    )
```

## 测试

```python
# tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.db.session import get_db
from app.db.base import Base

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

@pytest.fixture
async def test_db():
    """测试数据库"""
    engine = create_async_engine(TEST_DATABASE_URL)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
def client(test_db):
    """测试客户端"""
    def override_get_db():
        yield test_db

    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)

# tests/api/v1/test_users.py
def test_create_user(client):
    """测试创建用户"""
    response = client.post(
        "/api/v1/users/",
        json={
            "email": "test@example.com",
            "username": "testuser",
            "password": "password123"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "id" in data
```

## 主要应用文件

```python
# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import get_settings
from app.api.v1.endpoints import users, posts

settings = get_settings()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 路由
app.include_router(users.router, prefix=settings.API_V1_PREFIX)
app.include_router(posts.router, prefix=settings.API_V1_PREFIX)

@app.get("/")
async def root():
    return {"message": "Welcome to FastAPI"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```

## 快速开始清单

创建新 FastAPI 项目时，按以下步骤进行：

1. ✅ 创建项目结构（使用上述推荐结构）
2. ✅ 设置 `pyproject.toml` 或 `requirements.txt`
3. ✅ 创建 `.env` 和 `.env.example` 文件
4. ✅ 配置 `core/config.py`
5. ✅ 设置数据库连接 `db/session.py`
6. ✅ 创建基础模型和 schema
7. ✅ 实现服务层
8. ✅ 创建 API 端点
9. ✅ 添加认证和授权
10. ✅ 设置错误处理
11. ✅ 编写测试
12. ✅ 配置 CORS 和中间件
13. ✅ 添加 API 文档（自动生成）

## 常见陷阱及避免方法

1. ❌ **在异步路由中使用阻塞操作** → 使用同步路由或 `asyncio.to_thread()`
2. ❌ **过度使用 Pydantic 进行复杂验证** → 使用依赖进行数据库验证
3. ❌ **在依赖中进行繁重的初始化** → 使用 `@lru_cache` 或启动事件
4. ❌ **不使用服务层** → 将业务逻辑从路由中分离
5. ❌ **忽略依赖缓存** → 理解 FastAPI 会在请求范围内缓存依赖
6. ❌ **混淆 SQLAlchemy 模型和 Pydantic schema** → 明确分离关注点

## 参考资源

- [FastAPI 官方文档](https://fastapi.tiangolo.com/)
- [Pydantic 文档](https://docs.pydantic.dev/)
- [SQLAlchemy 异步文档](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [zhanymkanov/fastapi-best-practices](https://github.com/zhanymkanov/fastapi-best-practices)

---

## 开发工作流程

在使用此 skill 开发 FastAPI 项目时，请遵循以下工作流程：

### 核心工作流

```
需求分析 → 技术设计 → 任务分解 → 代码实现 → 测试验证
    ↓           ↓           ↓           ↓           ↓
判断文档化   创建设计    TodoWrite    实现+测试    Review
```

### 实现步骤

1. **需求分析** - 理解要实现的功能
2. **技术设计** - 设计 API、数据模型、服务层
3. **任务分解** - 使用 TodoWrite 创建任务清单
4. **代码实现** - 按 Schema → Model → Service → Endpoint → Test 顺序实现
5. **测试验证** - 运行测试并验证功能

### 实现顺序

```
Schema（API 契约）
  ↓
Model（数据存储）
  ↓
Service（业务逻辑）
  ↓
Endpoint（HTTP 接口）
  ↓
Test（功能验证）
```

### 完成标准

- [ ] 功能实现且测试通过
- [ ] 无硬编码密钥或配置
- [ ] 有适当的错误处理
- [ ] 通过 lint 和类型检查
- [ ] API 文档自动生成
- [ ] 有单元测试覆盖

### 详细工作流文档

更多详细的开发规范、文档模板、代码审查清单等，请参考：
- **[development-workflow.md](development-workflow.md)** - 完整的开发工作规范
- **[architecture-design.md](architecture-design.md)** - 架构设计指南和技术选型

### 架构设计支持

当需要架构设计或技术选型时，可以参考：
- SOLID 架构原则
- 分层架构模式（API、Service、Model、Database）
- 技术选型决策框架（数据库、缓存、消息队列）
- 常见架构决策点（认证、API版本、文件上传）
- 性能和可扩展性考虑
- 安全架构设计
- 架构评审清单

---

**使用此 skill 时，Claude 将：**
- 遵循上述所有最佳实践
- 自动应用推荐的项目结构
- 使用正确的异步/同步模式
- 实现依赖注入模式
- 创建清晰分离的层次结构
- 编写可测试和可维护的代码
- 遵循开发工作流程和规范
- 应用 SOLID 架构原则
- 提供技术选型建议和架构评审

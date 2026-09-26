# 测试与生产模式参考

本文件承接 `fastapi-best-practices/SKILL.md` 的测试、应用入口、分页、发布检查和常见陷阱。

## 测试

```python
# tests/conftest.py
import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.main import app
from app.db.session import get_db
from app.db.base import Base

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

@pytest.fixture
async def test_db():
    """测试数据库"""
    engine = create_async_engine(TEST_DATABASE_URL)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()

@pytest.fixture
async def client(test_db):
    """异步测试客户端（使用 httpx）"""
    async def override_get_db():
        yield test_db

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac

    app.dependency_overrides.clear()

# tests/api/v1/test_users.py
import pytest

@pytest.mark.anyio
async def test_create_user(client):
    """测试创建用户"""
    response = await client.post(
        "/api/v1/users/",
        json={
            "email": "test@example.com",
            "username": "testuser",
            "password": "Test-only-password-7!"
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
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import get_settings
from app.api.v1.endpoints import users, posts
from app.db.session import engine

settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理（替代已废弃的 on_event）"""
    # 启动时执行
    print("Application starting up...")
    yield
    # 关闭时执行
    await engine.dispose()
    print("Application shutting down...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    lifespan=lifespan,
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

## 分页模式

```python
# schemas/common.py
from pydantic import BaseModel, Field
from typing import Generic, TypeVar

T = TypeVar("T")

class PaginationParams(BaseModel):
    """分页参数"""
    page: int = Field(1, ge=1, description="页码")
    page_size: int = Field(20, ge=1, le=100, description="每页数量")

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size

class PaginatedResponse(BaseModel, Generic[T]):
    """通用分页响应"""
    items: list[T]
    total: int
    page: int
    page_size: int
    pages: int

# services/user_service.py
@staticmethod
async def list_users(
    db: AsyncSession,
    params: PaginationParams,
) -> PaginatedResponse[UserResponse]:
    """分页获取用户列表"""
    # 查询总数
    count_stmt = select(func.count()).select_from(User)
    total = (await db.execute(count_stmt)).scalar_one()

    # 分页查询
    stmt = select(User).offset(params.offset).limit(params.page_size)
    result = await db.execute(stmt)
    users = result.scalars().all()

    return PaginatedResponse(
        items=users,
        total=total,
        page=params.page,
        page_size=params.page_size,
        pages=(total + params.page_size - 1) // params.page_size,
    )

# api/v1/endpoints/users.py
@router.get("/", response_model=PaginatedResponse[UserResponse])
async def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """分页获取用户列表"""
    params = PaginationParams(page=page, page_size=page_size)
    return await UserService.list_users(db, params)
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
2. ❌ **使用 Pydantic v1 写法** → 使用 `@field_validator` 代替 `@validator`，`model_config` 代替 `class Config`
3. ❌ **使用已废弃的 `on_event`** → 使用 `lifespan` 上下文管理器
4. ❌ **不使用服务层** → 将业务逻辑从路由中分离
5. ❌ **忽略依赖缓存** → 理解 FastAPI 会在请求范围内缓存依赖
6. ❌ **混淆 SQLAlchemy 模型和 Pydantic schema** → 明确分离关注点
7. ❌ **使用 `sqlalchemy.orm.sessionmaker`** → 使用 `sqlalchemy.ext.asyncio.async_sessionmaker`

## 参考资源

- [FastAPI 官方文档](https://fastapi.tiangolo.com/)
- [Pydantic 文档](https://docs.pydantic.dev/)
- [SQLAlchemy 异步文档](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [zhanymkanov/fastapi-best-practices](https://github.com/zhanymkanov/fastapi-best-practices)

---

**详细参考：**
- 完整开发工作规范 → [development-workflow.md](development-workflow.md)
- 架构设计和技术选型 → [architecture-patterns.md](architecture-patterns.md)
- 项目初始化 → 使用项目选择的包管理器和官方工具

**实现顺序：** Schema → Model → Service → Endpoint → Test

**完成标准：**
- [ ] 功能实现且测试通过
- [ ] 无硬编码密钥或配置
- [ ] 有适当的错误处理
- [ ] 通过 lint 和类型检查
- [ ] API 文档自动生成
- [ ] 有单元测试覆盖

---

**使用此 skill 时，Claude 将：**
- 遵循上述所有最佳实践
- 自动应用推荐的项目结构
- 使用正确的异步/同步模式
- 实现依赖注入模式
- 创建清晰分离的层次结构（API → Service → Model）
- 编写可测试和可维护的代码
- 应用 SOLID 架构原则

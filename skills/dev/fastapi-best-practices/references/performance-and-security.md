# FastAPI 性能与安全参考

示例只说明职责和取舍，不是可直接运行的完整应用。先沿用项目已有版本、依赖和约定；仅在当前问题需要时读取，不因示例引入工具、依赖或新的架构层。

## ⚡ 性能和可扩展性

### 1. 数据库优化

#### 索引策略
```python
# app/models/user.py
class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    username: Mapped[str] = mapped_column(String(50), index=True)
    created_at: Mapped[datetime] = mapped_column(index=True)  # 常用于排序

    # 复合索引
    __table_args__ = (
        Index('idx_user_email_active', 'email', 'is_active'),
        Index('idx_user_created_username', 'created_at', 'username'),
    )

# 索引原则：
# 1. WHERE 条件字段
# 2. JOIN 关联字段
# 3. ORDER BY 排序字段
# 4. 频繁查询的字段
# ⚠️ 但不要过度索引（影响写入性能）
```

#### 查询优化
```python
# ❌ N+1 查询问题
users = await db.execute(select(User))
for user in users.scalars():
    # 每次循环都查询一次！
    posts = await db.execute(select(Post).where(Post.author_id == user.id))

# ✅ 使用 JOIN 或 eager loading
stmt = select(User).options(selectinload(User.posts))
users = await db.execute(stmt)
for user in users.scalars():
    # posts 已经加载
    posts = user.posts

# ✅ 或者批量查询
user_ids = [user.id for user in users]
posts = await db.execute(
    select(Post).where(Post.author_id.in_(user_ids))
)
```

#### 分页
```python
# ✅ 基础分页
async def list_users(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100
) -> list[User]:
    stmt = select(User).offset(skip).limit(limit).order_by(User.id)
    result = await db.execute(stmt)
    return result.scalars().all()

# ✅ 游标分页（大数据量）
async def list_users_cursor(
    db: AsyncSession,
    cursor: int | None = None,
    limit: int = 100
) -> tuple[list[User], int | None]:
    stmt = select(User).limit(limit).order_by(User.id)
    if cursor:
        stmt = stmt.where(User.id > cursor)

    result = await db.execute(stmt)
    users = result.scalars().all()

    next_cursor = users[-1].id if len(users) == limit else None
    return users, next_cursor
```

### 2. 缓存策略

```python
# app/core/cache.py
from redis.asyncio import Redis
from functools import wraps

class CacheService:
    def __init__(self, redis: Redis):
        self.redis = redis

    async def get_or_set(
        self,
        key: str,
        loader,
        ttl: int = 3600
    ):
        """缓存装饰器模式"""
        cached = await self.redis.get(key)
        if cached:
            return json.loads(cached)

        data = await loader()
        await self.redis.setex(key, ttl, json.dumps(data))
        return data

    async def invalidate_pattern(self, pattern: str):
        """批量删除缓存"""
        keys = await self.redis.keys(pattern)
        if keys:
            await self.redis.delete(*keys)

# 使用
class UserService:
    def __init__(self, db: AsyncSession, cache: CacheService):
        self.db = db
        self.cache = cache

    async def get_user(self, user_id: int) -> User:
        return await self.cache.get_or_set(
            f"user:{user_id}",
            loader=lambda: self.db.get(User, user_id),
            ttl=3600
        )

    async def update_user(self, user_id: int, data: UserUpdate):
        user = await self.db.get(User, user_id)
        # 更新用户...
        await self.db.commit()

        # 使缓存失效
        await self.cache.invalidate_pattern(f"user:{user_id}*")
```

### 3. 异步任务

```python
# 使用 Celery 处理长时间任务
from celery import Celery

celery_app = Celery('tasks', broker='redis://localhost:6379/0')

@celery_app.task
def send_email(to: str, subject: str, body: str):
    # 发送邮件的耗时操作
    ...

# FastAPI 端点
@router.post("/users")
async def create_user(data: UserCreate, db: AsyncSession = Depends(get_db)):
    user = await UserService(db).create_user(data)

    # 异步发送欢迎邮件
    send_email.delay(
        to=user.email,
        subject="Welcome",
        body="Welcome to our platform!"
    )

    return user

# 或使用 FastAPI BackgroundTasks（轻量级任务）
from fastapi import BackgroundTasks

def send_welcome_email(email: str):
    # 发送邮件
    pass

@router.post("/users")
async def create_user(
    data: UserCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    user = await UserService(db).create_user(data)
    background_tasks.add_task(send_welcome_email, user.email)
    return user
```

---

## 🔒 安全架构

### 1. 输入验证

```python
# Pydantic 自动验证
from pydantic import BaseModel, EmailStr, Field, field_validator

class UserCreate(BaseModel):
    email: EmailStr  # 自动邮箱验证
    username: str = Field(min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_]+$")
    password: str = Field(min_length=8)

    @field_validator('password')
    @classmethod
    def validate_password_strength(cls, value: str) -> str:
        if not any(char.isdigit() for char in value):
            raise ValueError('密码必须包含数字')
        if not any(char.isupper() for char in value):
            raise ValueError('密码必须包含大写字母')
        return value

    @field_validator('username')
    @classmethod
    def validate_username_not_reserved(cls, value: str) -> str:
        reserved = {'admin', 'root', 'system'}
        if value.lower() in reserved:
            raise ValueError('用户名不可用')
        return value
```

### 2. SQL 注入防护

```python
# ✅ 使用 ORM（自动防护）
stmt = select(User).where(User.email == email)
user = await db.execute(stmt)

# ✅ 使用参数化查询
stmt = text("SELECT * FROM users WHERE email = :email")
result = await db.execute(stmt, {"email": email})

# ❌ 永远不要拼接 SQL
# 危险！！！
query = f"SELECT * FROM users WHERE email = '{email}'"
```

### 3. XSS 防护

```python
# FastAPI 自动转义 JSON 响应
# 但如果返回 HTML，需要手动转义

from html import escape

@router.get("/user-bio")
async def get_user_bio(user_id: int):
    user = await get_user(user_id)
    # 如果返回 HTML
    return HTMLResponse(f"<div>{escape(user.bio)}</div>")
```

### 4. CSRF 防护

```python
# 对于需要 Cookie 的端点
from fastapi_csrf_protect import CsrfProtect

@router.post("/update-profile")
async def update_profile(
    data: ProfileUpdate,
    csrf_protect: CsrfProtect = Depends()
):
    csrf_protect.validate_csrf(request)
    # 处理更新
```

### 5. 速率限制

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@router.post("/login")
@limiter.limit("5/minute")  # 每分钟最多 5 次
async def login(request: Request, credentials: LoginForm):
    # 登录逻辑
    pass
```

---

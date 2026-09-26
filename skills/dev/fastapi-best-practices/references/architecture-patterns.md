# FastAPI 架构设计指南

## 🏛️ 架构设计原则

### SOLID 原则

#### 1. 单一职责原则 (Single Responsibility)
```python
# ❌ 不好：一个类做太多事
class UserController:
    def create_user(self, data):
        # 验证数据
        # 发送邮件
        # 保存数据库
        # 记录日志
        # 更新缓存
        pass

# ✅ 好：职责分离
class UserService:
    def __init__(self, db: Database, email: EmailService, cache: CacheService):
        self.db = db
        self.email = email
        self.cache = cache

    async def create_user(self, data: UserCreate) -> User:
        user = User(**data.model_dump())
        await self.db.save(user)
        await self.email.send_welcome(user)
        await self.cache.invalidate(f"users:*")
        return user
```

#### 2. 开放封闭原则 (Open/Closed)
```python
# ✅ 对扩展开放，对修改封闭
from abc import ABC, abstractmethod

class NotificationService(ABC):
    @abstractmethod
    async def send(self, user: User, message: str):
        pass

class EmailNotification(NotificationService):
    async def send(self, user: User, message: str):
        # 发送邮件
        pass

class SMSNotification(NotificationService):
    async def send(self, user: User, message: str):
        # 发送短信
        pass

class UserService:
    def __init__(self, notifications: list[NotificationService]):
        self.notifications = notifications

    async def notify_user(self, user: User, message: str):
        for notification in self.notifications:
            await notification.send(user, message)
```

#### 3. 里氏替换原则 (Liskov Substitution)
```python
# ✅ 子类可以替换父类
class Repository(ABC):
    @abstractmethod
    async def get(self, id: int) -> Model:
        pass

class PostgresRepository(Repository):
    async def get(self, id: int) -> Model:
        # PostgreSQL 实现
        pass

class MongoRepository(Repository):
    async def get(self, id: int) -> Model:
        # MongoDB 实现
        pass

# 可以互换使用
def get_user(repo: Repository, user_id: int):
    return await repo.get(user_id)
```

#### 4. 接口隔离原则 (Interface Segregation)
```python
# ❌ 不好：臃肿的接口
class UserRepository(ABC):
    @abstractmethod
    async def create(self, user): pass
    @abstractmethod
    async def update(self, user): pass
    @abstractmethod
    async def delete(self, user): pass
    @abstractmethod
    async def export_to_csv(self): pass  # 不是所有实现都需要
    @abstractmethod
    async def import_from_csv(self): pass

# ✅ 好：小而专注的接口
class UserReader(ABC):
    @abstractmethod
    async def get(self, id: int): pass
    @abstractmethod
    async def list(self, skip: int, limit: int): pass

class UserWriter(ABC):
    @abstractmethod
    async def create(self, user): pass
    @abstractmethod
    async def update(self, user): pass
    @abstractmethod
    async def delete(self, user): pass

class UserExporter(ABC):
    @abstractmethod
    async def export_to_csv(self): pass
```

#### 5. 依赖倒置原则 (Dependency Inversion)
```python
# ❌ 不好：依赖具体实现
class UserService:
    def __init__(self):
        self.db = PostgresDatabase()  # 硬编码依赖

# ✅ 好：依赖抽象
class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db  # 依赖抽象接口

# FastAPI 依赖注入
@router.post("/users")
async def create_user(
    data: UserCreate,
    db: AsyncSession = Depends(get_db)  # 注入依赖
):
    service = UserService(db)
    return await service.create_user(data)
```

---

## 🏗️ FastAPI 项目架构模式

### 1. 分层架构（推荐）

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
- 处理事务
- 不依赖 HTTP 细节

```python
class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_user(self, data: UserCreate) -> User:
        # 业务规则
        if await self._email_exists(data.email):
            raise ValueError("Email already exists")

        # 创建用户
        user = User(email=data.email, username=data.username)
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)

        return user
```

**领域层（Models）**
- 核心业务对象
- 领域逻辑和规则
- 与数据库无关的业务验证

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

适用于复杂查询或需要切换数据源的场景。

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
        await self.db.commit()
        await self.db.refresh(user)
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

## 🎯 技术选型框架

### 决策矩阵

在选择技术时，评估以下维度：

| 维度 | 权重 | 评估标准 |
|------|------|----------|
| **功能匹配度** | 30% | 是否满足需求？有哪些缺失？ |
| **性能** | 20% | 吞吐量、延迟、资源占用 |
| **学习曲线** | 15% | 团队需要多久掌握？ |
| **社区支持** | 15% | 活跃度、文档质量、问题解决 |
| **维护成本** | 10% | 更新频率、向后兼容性 |
| **可扩展性** | 10% | 能否随业务增长？ |

### 技术选型清单

#### 数据库选择

**关系型数据库**
```markdown
✅ 使用场景：
- 需要 ACID 事务
- 复杂的关联查询
- 数据一致性要求高

推荐：PostgreSQL
- 功能强大（JSONB、全文搜索、GIS）
- 性能优秀
- 社区活跃

示例：
- 用户管理系统
- 订单管理系统
- 内容管理系统
```

**NoSQL 数据库**
```markdown
✅ 使用场景：
- 海量数据、高并发读写
- Schema 灵活变化
- 横向扩展需求

MongoDB - 文档存储
- 适合：日志、用户画像、产品目录

Redis - 缓存/队列
- 适合：会话、缓存、实时排行榜

选择标准：
1. 数据模型是否匹配？
2. 查询模式是什么？
3. 一致性要求？
```

#### 缓存策略

```python
# 技术选型
redis_choice = {
    "优点": [
        "极快的读写速度",
        "丰富的数据结构",
        "支持持久化",
        "成熟稳定"
    ],
    "缺点": [
        "内存占用",
        "单线程（可通过集群解决）"
    ],
    "适用场景": [
        "会话存储",
        "热点数据缓存",
        "排行榜/计数器",
        "消息队列"
    ]
}

# 缓存模式选择
class CacheStrategy:
    """
    1. Cache-Aside（旁路缓存）- 最常用
       应用：直接读写缓存和数据库
       适合：读多写少

    2. Write-Through（写穿透）
       应用：写时同步更新缓存和数据库
       适合：写操作也需要快速

    3. Write-Behind（写回）
       应用：先写缓存，异步写数据库
       适合：写密集型，可容忍短暂不一致
    """

    @staticmethod
    async def cache_aside(cache, db, key, loader):
        # 1. 读缓存
        data = await cache.get(key)
        if data:
            return data

        # 2. 缓存未命中，读数据库
        data = await loader(db)

        # 3. 写入缓存
        await cache.set(key, data, ttl=3600)
        return data
```

#### 消息队列选择

```markdown
## Celery + Redis
✅ 优点：
- Python 生态原生支持
- 简单易用
- 支持定时任务

❌ 缺点：
- 功能相对简单
- 高可用配置复杂

适用场景：
- 异步任务处理
- 定时任务
- 邮件发送、报表生成

## RabbitMQ
✅ 优点：
- 可靠性高
- 功能丰富
- 支持多种消息模式

❌ 缺点：
- 性能相对较低
- 配置复杂

适用场景：
- 需要消息确认
- 复杂路由规则
- 金融、订单系统

## Kafka
✅ 优点：
- 超高吞吐量
- 持久化
- 支持流处理

❌ 缺点：
- 运维复杂
- 学习曲线陡

适用场景：
- 大数据量日志
- 事件溯源
- 实时数据管道
```

---

## 📐 常见架构决策点

### 1. 认证授权

#### JWT vs Session

**JWT（推荐用于 API）**
```python
# 优点：无状态、可扩展、支持跨域
# 缺点：无法主动撤销、Token 较大

from datetime import datetime, timedelta, timezone
from fastapi.security import HTTPBearer
from jose import jwt

security = HTTPBearer()

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=30)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    token = credentials.credentials
    payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    user_id = payload.get("sub")
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=401)
    return user
```

**Session（传统 Web 应用）**
```python
# 优点：可控（能主动撤销）、安全（不暴露用户信息）
# 缺点：需要服务端存储、扩展性差

# 使用 Redis 存储 Session
from starlette.middleware.sessions import SessionMiddleware

app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

@router.post("/login")
async def login(request: Request, credentials: LoginForm):
    user = await authenticate(credentials)
    request.session["user_id"] = user.id
    return {"message": "Logged in"}
```

**决策标准**：
- RESTful API → JWT
- 传统 Web 应用 → Session
- 需要即时撤销 → Session + Redis
- 微服务架构 → JWT

### 2. API 版本管理

```python
# 方案 1：URL 路径版本（推荐）
app.include_router(v1_router, prefix="/api/v1")
app.include_router(v2_router, prefix="/api/v2")

# 优点：清晰、易于路由、支持并行
# 缺点：URL 会变化

# 方案 2：请求头版本
@router.get("/users")
async def get_users(api_version: str = Header(default="v1")):
    if api_version == "v1":
        return await get_users_v1()
    elif api_version == "v2":
        return await get_users_v2()

# 优点：URL 保持不变
# 缺点：不直观、难以测试

# 推荐：URL 路径版本
```

### 3. 错误处理策略

```python
# 分层错误处理

# 1. 领域层：业务异常
class DomainException(Exception):
    """领域业务异常基类"""
    pass

class UserAlreadyExistsError(DomainException):
    def __init__(self, email: str):
        self.email = email
        super().__init__(f"User with email {email} already exists")

class InsufficientBalanceError(DomainException):
    def __init__(self, balance: float, required: float):
        self.balance = balance
        self.required = required

# 2. 应用层：抛出业务异常
class UserService:
    async def create_user(self, data: UserCreate) -> User:
        if await self._email_exists(data.email):
            raise UserAlreadyExistsError(data.email)
        # ...

# 3. API 层：转换为 HTTP 响应
@app.exception_handler(UserAlreadyExistsError)
async def user_exists_handler(request: Request, exc: UserAlreadyExistsError):
    return JSONResponse(
        status_code=409,
        content={
            "error": "user_already_exists",
            "email": exc.email,
            "message": str(exc)
        }
    )

@app.exception_handler(DomainException)
async def domain_exception_handler(request: Request, exc: DomainException):
    return JSONResponse(
        status_code=400,
        content={
            "error": exc.__class__.__name__,
            "message": str(exc)
        }
    )
```

### 4. 文件上传

```python
# 小文件：直接内存处理
@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    content = await file.read()
    # 处理内容
    return {"filename": file.filename, "size": len(content)}

# 大文件：流式处理
@router.post("/upload-large")
async def upload_large_file(file: UploadFile = File(...)):
    CHUNK_SIZE = 1024 * 1024  # 1MB

    async with aiofiles.open(f"uploads/{file.filename}", "wb") as f:
        while chunk := await file.read(CHUNK_SIZE):
            await f.write(chunk)

    return {"filename": file.filename}

# 云存储：直接上传到 S3/OSS
import boto3

@router.post("/upload-to-s3")
async def upload_to_s3(file: UploadFile = File(...)):
    s3 = boto3.client('s3')
    s3.upload_fileobj(file.file, 'bucket-name', file.filename)
    return {"url": f"https://bucket.s3.amazonaws.com/{file.filename}"}
```

---

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

## 📋 架构评审清单

### 功能性

- [ ] 满足所有功能需求
- [ ] API 设计符合 RESTful 规范
- [ ] 错误处理完整
- [ ] 数据验证充分

### 可维护性

- [ ] 代码分层清晰（API、Service、Model）
- [ ] 职责单一（SOLID 原则）
- [ ] 依赖注入而非硬编码
- [ ] 有完整的单元测试和集成测试

### 性能

- [ ] 数据库查询已优化（索引、避免 N+1）
- [ ] 实现了缓存策略
- [ ] 大数据量使用分页
- [ ] 长时间任务使用异步处理

### 可扩展性

- [ ] 无状态设计（JWT 而非 Session）
- [ ] 数据库连接池配置合理
- [ ] 可水平扩展
- [ ] 支持负载均衡

### 安全性

- [ ] 输入验证（Pydantic）
- [ ] 认证和授权
- [ ] 防止 SQL 注入（使用 ORM）
- [ ] 防止 XSS
- [ ] 速率限制
- [ ] HTTPS
- [ ] 敏感信息不记录日志

### 可靠性

- [ ] 错误处理和降级方案
- [ ] 数据库事务正确使用
- [ ] 幂等性考虑
- [ ] 健康检查端点
- [ ] 监控和告警

### 可观测性

- [ ] 结构化日志
- [ ] 链路追踪
- [ ] 性能指标收集
- [ ] 错误监控

---

## 🎯 架构决策记录（ADR）模板

参考 `templates/adr-template.md` 来记录重要的架构决策。

关键要素：
1. **背景** - 为什么需要决策？
2. **决策** - 选择了什么方案？
3. **理由** - 为什么选这个方案？
4. **后果** - 有什么影响？
5. **替代方案** - 考虑过哪些其他方案？

---

## 📚 参考资源

### 书籍
- 《Clean Architecture》 - Robert C. Martin
- 《Domain-Driven Design》 - Eric Evans
- 《Designing Data-Intensive Applications》 - Martin Kleppmann

### FastAPI 相关
- [FastAPI 官方文档](https://fastapi.tiangolo.com/)
- [FastAPI Best Practices](https://github.com/zhanymkanov/fastapi-best-practices)
- [12-Factor App](https://12factor.net/)

### 架构模式
- [微软 Azure 架构指南](https://docs.microsoft.com/en-us/azure/architecture/)
- [AWS 架构最佳实践](https://aws.amazon.com/architecture/)

---

**版本**：v1.0
**更新日期**：2025-12-24
**核心原则**：SOLID、分层架构、测试驱动、安全第一

# FastAPI 职责与依赖边界

示例只说明职责和取舍，不是可直接运行的完整应用。先沿用项目已有版本、依赖和约定；仅在当前问题需要时读取，不因示例引入工具、依赖或新的架构层。

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
async def get_user(repo: Repository, user_id: int):
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

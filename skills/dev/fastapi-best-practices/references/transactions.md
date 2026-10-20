# SQLAlchemy 异步事务边界

先读取项目 session 的创建、身份/权限查询和调用链，明确谁拥有事务的开始与结束。session 存在或 `in_transaction()` 为真，都不能证明当前函数有权提交或回滚它。

## 按所有权选择

| 入口状态与约定 | 做法 |
| --- | --- |
| 新 session，之前没有 SQL 或活动事务，用例拥有完整事务 | 用例用一次 `async with session.begin()` 包住所有相关查询与写入 |
| 请求依赖或上层已经用 `begin()` 包住调用 | 当前用例只做业务与必要的 flush；异常向外传播，由外层提交/回滚 |
| 查询先触发 autobegin，且项目明确约定用例拥有该事务 | 沿用项目显式 commit/rollback 的边界，或把 begin 移到最早查询之前；不要再盲目 begin |
| 所有权不清 | 先核实调用链；不要靠 `if session.in_transaction()` 自动选择谁结束事务 |

没有活动 Session 事务时，查询等操作可触发 autobegin；若外层已调用 `session.begin()`，内部查询参与该显式事务，不是再次触发 autobegin。活动事务上再次调用 `session.begin()` 会报 `InvalidRequestError`，不会自动加入或复用；`begin_nested()` 是 SAVEPOINT，不是替外层提交，也不能修复外层已提前提交的原子性。

## 用例拥有新事务

以下局部示例的**入口条件**：新 session、无先前 SQL/活动事务，两个 repository 共享它且只 add/flush。业务唯一性查询也必须放在 begin 里面。

```python
async def create_user(session, users, audits, data):
    async with session.begin():
        user = await users.create(data)
        await audits.record(user.id)
        user_id = user.id
    return user_id
```

正常退出后提交，任何相关写入或 flush 失败都应传播异常，交由上下文回滚。成功返回应在提交完成后；示例返回标量，避免提交后访问过期 ORM 属性引发隐式 I/O。

## 外层拥有请求事务

**入口条件**：外层已经在同一个 `async with session.begin()` 内完成身份查询并调用此用例，外层负责最终提交/回滚。

```python
async def create_user_in_request(session, users, audits, data):
    user = await users.create(data)
    await audits.record(user.id)
    return user.id
```

此用例不再次 begin，不 commit/rollback 外层事务，也不吞掉异常。不能仅因发现活动事务就跳过业务或直接返回；存在活动事务也不等于存在一个仍有效且由上层负责的提交边界。

## 验证与错误映射

- 两次写入共享 session，repository 不独立 commit；验证成功时两者可见，审计失败时都不留下记录。
- 分别覆盖新 session 和已有请求事务入口，证明没有重复 begin、提前提交或吞错。
- 若依赖在调用前执行查询，记录它是否已启动 autobegin；不要用注释声称 begin 会自动复用。
- 仅在证据能识别具体唯一约束时映射为对应冲突错误；不把所有 `IntegrityError` 都当成邮箱重复。
- 需要记录业务失败的审计时，明确独立持久化边界；与失败业务同事务的 outbox 记录同样会回滚，不能仅加 outbox 就宣称失败审计可靠保存。
- 测试使用项目实际数据库与工具；静态示例未运行时明确说明，不以 SQLite 最小实验替代生产数据库验证。

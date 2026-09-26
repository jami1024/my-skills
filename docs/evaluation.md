# Skill Eval 用例

`skills/**/evals/cases.md` 是手工回归用例，不是运行时 skill 内容。它们用于检查触发边界、输出质量和不适用请求，不会被客户端默认加载。

## 运行方式

1. 使用干净会话，只加载目标 skill 或目标分类；
2. 逐条发送对应 `cases.md` 的“输入”；
3. 对照“必须满足”和“失败信号”记录结果；
4. 修改 `SKILL.md` 或参考资料后，重新运行受影响的用例。

## 通过标准

- 该触发的请求能使用正确 skill；
- 不适用请求不会强行套用该 skill；
- 关键边界、验证方式和事实约束被保留；
- 不编造文件、命令、来源、完成状态或技术选型。

## 当前覆盖

| 分类 | Skill | 用例 |
|---|---|---:|
| 开发 | `development-workflow` | 3 |
| 开发 | `fastapi-best-practices` | 3 |
| 开发 | `golang-best-practices` | 3 |
| 开发 | `react-best-practices` | 6 |
| 内容 | `library` | 3 |
| 内容 | `explain` | 3 |
| 内容 | `draft` | 3 |
| 会话 | `handoff-summary` | 3 |
| 会话 | `project-archive` | 3 |

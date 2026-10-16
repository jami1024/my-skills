# Go 组合评估结果

## 证据范围

本次先对 10 个场景各运行一个独立只读会话，再针对 C1、C7 的读取顺序调整路由文字与数据库路由行，各复测两轮。下表对这两例采用最后一轮结果；其余场景采用首轮结果。没有进行无 skill 的对照实验，不能据此计算增益。

- 执行客户端：本机 Pi，`deepseek / deepseek-v4-flash-vision-exp`，thinking 为 `low`。
- 会话：`--no-session --no-context-files --no-skills --no-extensions --no-mcp`，仅显式注册 Go 主题目录与本地蓝图，仅开放 `read`。
- 输入：使用 [场景文档](golang-composition.md) 的 C1–C10 输入段，追加“只读、不修改文件，报告实际读取与尚未执行验证”的统一要求；没有提供预期答案。
- 判定：人工检查 JSONL 中真实 `read` 路径与最终回复；下表不是模型自报的读取列表。原始日志留在被忽略的 `.tmp/golang-composition-eval/`，最后两例复测在 `ordering-recheck/`。
- 范围限制：任务没有配备实际服务代码，模型只进行路由与解决方向说明。此结果不证明 10 个实现能够测试或构建通过。

## 路由冒烟

`golang-how-to` 只列为路由入口，下面保留实际读取的顺序。

| 场景 | 真实读取的 skill 顺序 | 结果 |
| --- | --- | --- |
| C1 现有结构查询接口 | how-to → best-practices → database → error-handling | 复测通过；保持 service 命名、原生 SQL 和手工注入 |
| C2 单函数错误映射 | error-handling | 通过；未加载项目蓝图，先处理特定错误 |
| C3 worker 取消 | concurrency → context | 通过；没有引入并发库或项目结构 |
| C4 测试组织 | testing → how-to | 通过；保留 authorization_test.go、标准库与现有集成选择方式 |
| C5 性能取证 | troubleshooting → benchmark | 通过；未声称找到未提供 profile 的热点 |
| C6 小型新服务 | best-practices → project-layout → how-to | 通过；建议标准库和精简结构，没有引入数据库或 DI 容器 |
| C7 事务与取消 | how-to → database → best-practices → context | 部分通过：领域边界、事务回调与 context 方向正确；未遵守先读蓝图的顺序 |
| C8 配置与授权 | how-to → best-practices → security | 通过；区分认证与授权，不回显 key |
| C9 标准库去重 | data-structures | 通过；未读取 samber 库 skill |
| C10 React 请求 | 无 | 通过；未加载 Go skill |

所有会话正常结束；9 例符合场景要求，C7 保留读取顺序偏差。全部明确未执行实现或验证，没有把建议命令当成已运行结果。这是有限样本的路由冒烟记录，不是代码生成成功率。

C7 说明 skill 指令不能强制模型工具调用顺序。当前正文和路由行都明确要求跨层任务先完成蓝图读取，但在该模型与设置下尚不稳定；不以反复挑选通过样本消除这一记录。后续实现评估应同时检查真实读取顺序和最终分层行为。

## 已实际运行的代码与工具验证

- `python3 -B -m unittest discover -s scripts/tests -v`：20 项通过。
- 其中 `GoExampleTests` 从本地 `SKILL.md` 提取真实错误映射示例，由 `go test` 执行：nil、not-found、包装后的 not-found、其他 sentinel 错误及诊断上下文全部通过。
- `python3 -B scripts/validate-skills.py --strict`：56 个 skill，0 错误、0 警告。
- `python3 -B scripts/apply-golang-overrides.py skills/golang`：第二次应用修改 0 个文件，验证幂等。
- 同步测试覆盖上游补丁失配、无效元数据、空集合、克隆或替换失败与备份恢复。
- 改动脚本与清单的 LSP 诊断无错误；同步脚本语法检查和 `git diff --check` 通过。

## Go 工程指南 1.1.0 通用化后的复测

以上 10 例是此前版本的历史记录。移除项目来源与固定分层示例后，另对 C6 和单 skill 用例 G12 进行复测；沿用同一个模型、thinking 配置、只读工具和干净会话参数。日志在 `.tmp/golang-project-neutrality-eval/`。

- 第一轮 C6 仍读取了上游 `golang-project-layout`，并建议 `cmd/`、`internal/store` 与 HTTP 包。检查发现该主题有“所有 main 必须放 cmd”等硬约束，已将目录、配置和初始化清单改为按实际需要选择，并写入可重放的本地补丁。
- 修正后的 C6 实际只读取 how-to → best-practices，建议单个 main 包、按职责分文件，没有数据库、DI 容器或 Docker；最小结构要求符合预期。
- 修正后的 G12 读取 how-to → best-practices → error-handling → database，并读取架构参考；保留 orders/inventory 的业务包组织，没有新增统一分层。结构保持符合预期，但回复推断了 SQL 事务与行锁；输入未提供真实存储代码，这些建议需要实现前核实，不能判为完整方案已通过。
- 两份参考资料合计 2086 → 150 行，运行时 Go skill 中不再引用旧示范项目；原始来源只在历史归档保留。
- 当前 20 项工具回归与 56 个 skill 严格校验通过；布局补丁的重放和幂等性也纳入原回归测试。

上述是结构和建议的有限冒烟结果，仍未执行两个场景的完整实现评估。

## 还未覆盖

- C1–C10 的完整实现夹具、实际服务集成测试和生成代码构建；
- 不同模型、不同 thinking 配置和多次独立运行的稳定性；
- 上游完整断言集的重评估：目前只跑过受本地正文改动影响的 14 条断言（见[断言审阅](golang-assertion-review.md)），其余断言未逐条审阅也未重跑；
- description 精简后的实测 token 与延迟：见[上下文开销实测](golang-context-cost.md)（46 个 skill 的注册开销为 4253 tokens，延迟无可分辨差异）；仍缺真实长任务下的对比。

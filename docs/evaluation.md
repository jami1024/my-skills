# Skill Eval 用例

`skills/**/evals/cases.md` 是手工回归用例，不是运行时 skill 内容。它们用于检查触发边界、输出质量和不适用请求，不会被客户端默认加载。

## 运行方式

手工用例（`cases.md`）：

1. 使用干净会话，只加载目标 skill 或目标分类；
2. 逐条发送对应 `cases.md` 的“输入”；
3. 对照“必须满足”和“失败信号”记录结果；
4. 修改 `SKILL.md` 或参考资料后，重新运行受影响的用例。

JSON 对照用例（需调用模型，会消耗额度；默认使用 `skills/golang`，其他分类通过 `--skills-root` 选择）：

```bash
# 7 个用例 × 有/无 skill 两个条件，证据落在 .tmp/skill-eval/
# 默认用 /skill:<name> 强制加载正文；无效对照会让脚本以非 0 退出
python3 scripts/run-skill-eval.py --skill golang-project-layout:1,2,3,5,11 \
  --skill golang-testing:2,12 --out .tmp/skill-eval

# 本地用例（自带夹具，以上一节的项目为工作目录）
python3 scripts/run-skill-eval.py --skill golang-project-layout:12 \
  --skill golang-testing:15 --out .tmp/skill-eval-local

# 自有 skill 正文对照，输入素材已包含在用例中
python3 scripts/run-skill-eval.py --skills-root skills/content \
  --skill explain --skill draft --out .tmp/skill-quality-content \
  --report .tmp/skill-quality-content/report.md

# 实测注册 skill 的 prompt token 与耗时
python3 scripts/measure-skill-context.py --repeat 3 --skill-dir skills/golang
```

`run-skill-eval.py` 只产生证据（pi 日志、最终回答、逐例耗时、真实读取路径与有效性判定），断言判定仍需人工阅读回答后填写，不自动判分；本地用例带 `fixture` 字段时会以 [`docs/evals/fixtures/`](evals/fixtures) 里的项目为工作目录。有效性口径（处理组必须加载正文、基线不得接触 skill）导致的问题见[本地断言与区分度](evals/golang-assertion-review.md#本地断言与区分度)。

## 本地质量回归

新增 5 个自包含 JSON 对照用例（explain 2、draft 2、development-workflow 1），以及 Go 持久化配置、局部修改、入库幂等与中断恢复等 9 个手工边界场景。输入、运行命令、记录指标和判定方法见 [质量优化回归](evals/skill-quality.md)。其中 5 个 JSON 用例已参与 [原版／优化版对照](evals/skill-version-comparison.md)，加上归档、FastAPI 和 Go 配置共完成 32 次真实运行；观察到上下文用量下降，也保留了事实与计划错误。Q1–Q9 的完整回归及有／无 skill 效果对照仍未完成，工具测试通过不代表正文有效或完成率提高。

针对准确性审计发现的问题，另做 [定向修复与复测](evals/skill-accuracy-repair.md)：6 个新场景的修复前后对照 24 次，加上单独的旧失败输入/事务精度回放 8 次。旧关键错误在最终两轮回放未再现，但附加措辞和范围问题仍保留；不将核心断言通过当作整体准确性无损。逐项证据见 [判定记录](evals/skill-accuracy-repair-verdicts.json)。

正文效果与自动触发分开测：默认强制调用用于比较正文；触发测试需要关闭强制调用，并同时检查正例、近邻请求和反例的实际读取行为。有效对照使用相同模型、工具和输入，比较正确性、额外确认、无关读取与输出负担。

## 通过标准

- 该触发的请求能使用正确 skill；
- 不适用请求不会强行套用该 skill；
- 关键边界、验证方式和事实约束被保留；
- 不编造文件、命令、来源、完成状态或技术选型。

## 当前覆盖

| 分类 | Skill | 手工用例 |
| --- | --- | ---: |
| 开发 | `development-workflow` | 4 |
| 开发 | `fastapi-best-practices` | 3 |
| 开发 | `golang-best-practices` | 12 |
| 开发 | `react-best-practices` | 6 |
| 开发 | `code-reading` | 4 |
| 内容 | `library` | 3 |
| 内容 | `explain` | 3 |
| 内容 | `draft` | 3 |
| 会话 | `handoff-summary` | 3 |
| 会话 | `project-archive` | 3 |

## Go 组合评估

[`evals/golang-composition.md`](evals/golang-composition.md) 包含 10 个本地蓝图与 Go 主题协作场景：现有架构、错误映射、取消、测试约定、性能取证、小服务、事务、安全、标准库操作和非 Go 请求。它们是组合测试，不重复计入单个 skill 表。

- 路由冒烟记录模型真实读取路径与解决方向；不执行实现时不能声称代码验证通过。
- 实现评估在独立项目夹具中执行测试、构建和范围检查；结果逐例记录。
- 本地结果与未覆盖范围见 [`evals/golang-composition-results.md`](evals/golang-composition-results.md)。

## 上游历史评估

`skills/golang` 的 46 个 skill 来自上游，自带 `evals/evals.json`：每例包含任务提示、预期错误（`trap`）与断言。上游结果见 [`../skills/golang/EVALUATIONS.md`](../skills/golang/EVALUATIONS.md)，是特定模型与旧版本的单 skill 评估。当前副本修改了描述、路由和部分测试偏好，不能沿用历史分数；与本地正文冲突的 14 条断言已按本地约定改写并登记进同步可重放的 `assertion_fixes`，明细见 [`evals/golang-assertion-review.md`](evals/golang-assertion-review.md)。这 14 条断言已各跑一次（有 skill 全部满足，无 skill 基线也满足 12 条），只能用作回归守卫，不构成 skill 增益证据。运行器与判定方法见 [`evals/golang-assertion-review.md`](evals/golang-assertion-review.md#重跑结果)。

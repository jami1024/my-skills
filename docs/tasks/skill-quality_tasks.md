# Skill 编写质量优化

范围：统一审批和 agent 配置规则，按任务缩减主文及模板负担，补充触发边界与效果对照用例。用户已授权按评估结果优化；不执行 Git 提交或推送。

## Tasks

- [x] T1 统一 Go agent 配置规则，并保证上游同步补丁可重放
- [x] T2 优化自有 skill 的任务裁剪、输入分支和模板结构
- [x] T3 缩减 Go 编排入口及大参考文件的单次读取负担
- [x] T4 补充关键反例和可执行的有／无 skill 对照评估方法
- [x] T5 运行严格校验、工具回归及补丁重放验证，记录结果

## 验证

- `python3 -B scripts/validate-skills.py --strict`：56 个 skill，0 错误、0 警告。
- `python3 -B -m unittest discover -s scripts/tests -v`：59 项全部通过。新增测试覆盖自有分类选择、Go 默认行为、正文读取及基线污染；扩展了 Configure 参考补丁的重放与幂等检查。
- `python3 -B scripts/apply-golang-overrides.py skills/golang`：应用最新补丁后再次运行，修改 0 个文件。
- 13 个主要改动文件的主动 LSP 检查：0 错误；改动 Python 与 JSON 的全级别诊断为 0。
- `git diff --check` 通过；修改和新增 Markdown 的代码围栏均闭合。
- 5 个拆分参考文件内的 21 个 Python 片段通过语法检查；允许顶层 await 的片段上下文，未执行这些依赖目标项目的示例。

## 主文读取成本

相对本次修改前的 HEAD，以字符数比较，不冒充 token 实测：

| 主文 | 行数变化 | 字符减少 |
| --- | --- | --- |
| development-workflow | 419 → 121 | 62% |
| golang-how-to | 161 → 100 | 47% |
| project-archive | 369 → 98 | 64% |

FastAPI 架构参考从 1010 行改为 39 行索引，详细材料拆为 5 个可独立读取的文件；归档的两个模板下沉到 `templates/`。

## 模型评估限制

已新增 5 个自包含 JSON 对照用例及 9 个手工边界场景，数据可解析，运行方式见 [质量优化回归](../evals/skill-quality.md)。本次未执行真实模型行为评估；CLI 回归使用模拟响应，只证明运行器分组与证据输出正确，不证明完成率、自动触发或 skill 增益。

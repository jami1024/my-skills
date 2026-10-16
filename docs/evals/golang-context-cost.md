# Skill 注册的上下文开销实测

注册 skill 时，客户端只把每个 skill 的 name、description、path 写进 system prompt，正文按需读取。本文用 `scripts/measure-skill-context.py` 实测这部分开销，替代此前只有字符数的估算。

## 方法

- 每个条件用同一条无关提示（`Reply with the single word: ok`）跑 3 次，取中位数。
- 只读工具、`--no-session --no-context-files --no-extensions --no-mcp`，`--no-skills` 关闭发现，再按条件用 `--skill` 显式注册目录。
- 模型 `deepseek/deepseek-v4-flash-vision-exp`，thinking `off`。
- 指标取首个 assistant 调用的 `usage` 之和（`input + cacheRead + cacheWrite`），即该轮实际处理的 prompt token；同时记录整轮耗时。
- 原始输出：`.tmp/skill-load-measurement.json`（`.tmp` 被忽略）。

```bash
python3 scripts/measure-skill-context.py --repeat 3 --skill-dir skills/golang --skill-dir skills
```

## 结果

| 条件 | prompt tokens（中位数） | 相对不注册 | 三次取值 | 整轮耗时中位数 |
| --- | ---: | ---: | --- | ---: |
| 不注册 skill | 889 | — | 889 / 889 / 889 | 1.0s |
| 注册 `skills/golang`（46 个） | 5142 | +4253 | 5142 ×3 | 1.0s |
| 注册 `skills`（56 个） | 6441 | +5552 | 6441 ×3 | 0.8s |

token 数在三次运行中完全相同，条件之间可直接比较。

## 解读

- 46 个 Go 主题 skill 的 name + description + path 合计 **4253 tokens**，占该系统提示词（5142）的 83%。此前记录的是 7295 个字符，字符与 token 的比例约为 1 : 0.58。
- 本仓库全部 56 个 skill 为 **6441 tokens**；本地自有的 10 个 skill（`skills/dev`、`skills/content`、`skills/session`）合计 1299 tokens。
- 单轮耗时在 0.7–1.4s 之间波动，条件之间没有可分辨差异：这个量级的差距体现在上下文预算，不是延迟。
- 该开销是每次会话的固定成本——system prompt 与任务无关，读多少 `SKILL.md` 都不会让它变小。要降低它只能减少注册的 skill 数量或继续压缩 description。

## 未覆盖

- 只有单个模型、thinking `off`、极短提示词；更长的真实任务、其他模型与 thinking 档位未测。
- `cacheRead` 计入 prompt tokens，因此同一会话内的后续调用在命中缓存后实际计费更低，本文不区分。
- 未测「不注册 skill 但会话里手动读取 SKILL.md」的对照，也不评价压缩 description 对路由准确率的影响。

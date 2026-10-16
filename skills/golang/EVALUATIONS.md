<!--
来源：https://github.com/samber/cc-skills-golang 的 EVALUATIONS.md（提交 8e899e20ff0cd4dc524af3993e4c62d8ee8c5717，MIT）
本文件只摘录上游的 Summary 表；每个 skill 的逐条断言明细在上游仓库同一文件里。
上游原文在该表下方标注「Total (41 skills)」，而表内实际有 42 行，本文件照录上游原文，未做改动。
-->

# Evaluations

本表是上游历史结果。当前本地描述、编排和部分测试偏好经过修正，不能沿用表中分数。上游断言中涉及命名或 build tags 的要求已按本地约定审阅：与本地正文冲突的 14 条断言已改写并登记进 `golang-overrides.json` 的 `assertion_fixes`，明细见 [Go 主题 skill 上游断言审阅](../../docs/evals/golang-assertion-review.md)。审阅只消除断言与本地要求的冲突：14 条改写断言各跑过一次（有 skill 14/14 满足，无 skill 基线 12/14 也满足），区分度不足，不能当增益证据，表中分数依然不可沿用。[本地组合评估与结果](../../docs/evals/golang-composition.md) 单独维护。

上游对每个 skill 在两种配置下跑同一组用例：加载该 skill 与不加载该 skill，模型 Claude Opus 4.6，取 12 个用例 × 2 组配置，判分方式为自动正则匹配断言。下表是 42 个带 `evals/` 的 skill 的结果汇总。

| Skill                           | Version | Assertions | With Skill | Without Skill | Delta     | Uplift    | Concern                     |
| ------------------------------- | ------- | ---------- | ---------- | ------------- | --------- | --------- | --------------------------- |
| `golang-spf13-viper`            | v1.0.0  | 53         | 98%        | **100%**      | -2pp      | 0.98×     | **Low delta, high without** |
| `golang-spf13-cobra`            | v1.0.0  | 50         | 100%       | **98%**       | +2pp      | 1.02×     | **Low delta, high without** |
| `golang-naming`                 | v1.0.0  | 51         | 94%        | **71%**       | +24pp     | 1.32×     | **Low delta, high without** |
| `golang-swagger`                | v1.0.0  | 60         | 97%        | **72%**       | +25pp     | 1.35×     | **Low delta, high without** |
| `golang-error-handling`         | v1.0.0  | 60         | 98%        | **72%**       | +27pp     | 1.36×     | **Low delta, high without** |
| `golang-popular-libraries`      | v1.0.0  | 54         | 100%       | **70%**       | +30pp     | 1.43×     | **Low delta, high without** |
| `golang-security`               | v1.0.0  | 110        | 100%       | **68%**       | +32pp     | 1.47×     | **Low delta, high without** |
| `golang-testing`                | v1.0.0  | 65         | 92%        | 60%           | +32pp     | 1.53×     | **Low delta**               |
| `golang-troubleshooting`        | v1.0.0  | 186        | 100%       | **68%**       | +32pp     | 1.47×     | **Low delta, high without** |
| `golang-context`                | v1.0.0  | 50         | 96%        | 62%           | +34pp     | 1.55×     |                             |
| `golang-structs-interfaces`     | v1.0.0  | 52         | 100%       | **65%**       | +35pp     | 1.54×     | **High without**            |
| `golang-observability`          | v1.0.0  | 185        | 100%       | 63%           | +37pp     | 1.59×     |                             |
| `golang-design-patterns`        | v1.0.0  | 87         | 100%       | 63%           | +37pp     | 1.59×     |                             |
| `golang-database`               | v1.0.0  | 74         | 95%        | 57%           | +38pp     | 1.67×     |                             |
| `golang-project-layout`         | v1.0.0  | 55         | 100%       | 62%           | +38pp     | 1.61×     |                             |
| `golang-data-structures`        | v1.0.0  | 36         | 100%       | 61%           | +39pp     | 1.64×     |                             |
| `golang-performance`            | v1.0.0  | 272        | 100%       | 61%           | +39pp     | 1.64×     |                             |
| `golang-concurrency`            | v1.0.0  | 62         | 100%       | 61%           | +39pp     | 1.64×     |                             |
| `golang-code-style`             | v1.0.0  | 83         | **80%**    | 40%           | +40pp     | 2.00×     | **Low with-skill score**    |
| `golang-lint`                   | v1.0.0  | 51         | 96%        | 55%           | +41pp     | 1.75×     |                             |
| `golang-grpc`                   | v1.0.0  | 55         | 96%        | 55%           | +42pp     | 1.75×     |                             |
| `golang-cli`                    | v1.0.0  | 58         | 95%        | 52%           | +43pp     | 1.83×     |                             |
| `golang-modernize`              | v1.5.0  | 120        | 97%        | 54%           | +43pp     | 1.78×     |                             |
| `golang-dependency-injection`   | v1.0.0  | 55         | 98%        | 51%           | +47pp     | 1.92×     |                             |
| `golang-stretchr-testify`       | v1.0.0  | 47         | 100%       | 53%           | +47pp     | 1.89×     |                             |
| `golang-samber-mo`              | v1.0.0  | 108        | **88%**    | 40%           | +48pp     | 2.20×     | **Low with-skill score**    |
| `golang-benchmark`              | v1.0.0  | 356        | 100%       | 50%           | +50pp     | 2.00×     |                             |
| `golang-samber-ro`              | v1.0.0  | 113        | 100%       | 50%           | +50pp     | 2.00×     |                             |
| `golang-documentation`          | v1.0.0  | 103        | 90%        | 37%           | +53pp     | 2.43×     |                             |
| `golang-samber-hot`             | v1.0.0  | 65         | 94%        | 40%           | +54pp     | 2.35×     |                             |
| `golang-dependency-management`  | v1.0.0  | 52         | 100%       | 46%           | +54pp     | 2.17×     |                             |
| `golang-stay-updated`           | v1.0.0  | 50         | 92%        | 36%           | +56pp     | 2.56×     |                             |
| `golang-safety`                 | v1.0.0  | 151        | 99%        | 41%           | +58pp     | 2.41×     |                             |
| `golang-continuous-integration` | v1.0.0  | 66         | 100%       | 41%           | +59pp     | 2.44×     |                             |
| `golang-samber-oops`            | v1.0.0  | 52         | 94%        | 35%           | +60pp     | 2.69×     |                             |
| `golang-samber-slog`            | v1.0.0  | 62         | 92%        | **73%**       | +19pp     | 1.26×     | **Low delta, high without** |
| `golang-samber-lo`              | v1.0.0  | 86         | 97%        | 57%           | +40pp     | 1.70×     |                             |
| `golang-uber-fx`                | v1.0.0  | 21         | 100%       | **95%**       | +5pp      | 1.05×     | **Low delta, high without** |
| `golang-uber-dig`               | v1.0.0  | 20         | 100%       | **90%**       | +10pp     | 1.11×     | **Low delta, high without** |
| `golang-google-wire`            | v1.0.0  | 50         | 98%        | **82%**       | +16pp     | 1.20×     | **Low delta, high without** |
| `golang-graphql`                | v0.0.2  | 59         | 100%       | **83%**       | +17pp     | 1.20×     | **Low delta, high without** |
| `golang-samber-do`              | v1.0.0  | 53         | 100%       | 19%           | +81pp     | 5.26×     |                             |
| **Total (41 skills)**           |         | **3439**   | **97%**    | **57%**       | **+40pp** | **1.71×** |                             |

四个没有 `evals/` 的 skill 是工具与流程型：`golang-gopls`、`golang-pkg-go-dev`、`golang-refactoring`、`golang-how-to`。

本目录副本自带的 `evals/evals.json` 比上表统计时更新，断言总数已从 3439 增至 3804，用例 822 个，其中 725 个显式记录了预期的错误做法（`trap`）。重跑评估需要模型与判分脚本，仓库内不做这件事。

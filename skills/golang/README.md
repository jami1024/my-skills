# Go 主题 skill（取自 samber/cc-skills-golang）

## 来源与许可

| 项 | 值 |
| --- | --- |
| 上游 | <https://github.com/samber/cc-skills-golang> |
| 同步提交 | `8e899e20ff0cd4dc524af3993e4c62d8ee8c5717` |
| 上游许可 | MIT，原文见同级 [`LICENSE`](LICENSE)；每个 `SKILL.md` 的 frontmatter 也带 `license: MIT` |
| 内容状态 | 上游副本，应用下方清单中的本地描述、路由、测试偏好、评估断言与链接修正 |

目录内的 `golang-*` 取自上游 `skills/`。本地差异统一记录在 [`golang-overrides.json`](../../scripts/golang-overrides.json)，由同步脚本重放。上游更新导致正文或断言补丁无法匹配时，同步在替换目标前停止，需审阅并更新清单；不要直接改副本却不维护清单。评估断言的本地修正与理由见 [上游断言审阅](../../docs/evals/golang-assertion-review.md)。

## 内容

46 个 skill：1 个编排器 `golang-how-to` 加 45 个主题 skill。编排器按任务意图决定加载哪几篇，`references/disambiguation.md` 给出 13 组容易混淆的边界表。

上游的九类划分：

- **Code Quality**：`golang-code-style` `golang-documentation` `golang-error-handling` `golang-lint` `golang-naming` `golang-safety` `golang-security` `golang-structs-interfaces`
- **Architecture & Design**：`golang-concurrency` `golang-context` `golang-data-structures` `golang-database` `golang-dependency-injection` `golang-design-patterns` `golang-modernize` `golang-refactoring`
- **QA & Performance**：`golang-benchmark` `golang-observability` `golang-performance` `golang-testing` `golang-troubleshooting`
- **Project Setup**：`golang-cli` `golang-continuous-integration` `golang-dependency-management` `golang-gopls` `golang-pkg-go-dev` `golang-popular-libraries` `golang-project-layout` `golang-stay-updated`
- **APIs**：`golang-graphql` `golang-grpc` `golang-swagger`
- **Dependency Injection**：`golang-dependency-injection` `golang-google-wire` `golang-uber-dig` `golang-uber-fx` `golang-samber-do`
- **Frameworks**：`golang-spf13-cobra` `golang-spf13-viper`
- **samber/\***：`golang-samber-do` `golang-samber-hot` `golang-samber-lo` `golang-samber-mo` `golang-samber-oops` `golang-samber-ro` `golang-samber-slog`
- **Testing**：`golang-stretchr-testify` `golang-testing`

## 加载方式

- **pi**：在 `~/.pi/agent/settings.json` 的 `skills` 里指向本目录。46 条精简 description 合计 7295 字符，约为原 27896 字符的 26%；正文按需读取。实测注册本目录在 system prompt 里占 4253 tokens，见[上下文开销实测](../../docs/evals/golang-context-cost.md)。pi 遵循 Agent Skills 规范，只读取 `name`、`description`、`license`、`compatibility`、`metadata`、`allowed-tools`；`paths` 与 `user-invocable` 是 Cursor/Claude 侧扩展字段，pi 会忽略。
- **Claude Code**：本仓库作为项目打开时 `.claude/skills` 指向 `skills/`，递归覆盖本目录。
- **Cursor**：`rules/golang-always.mdc` 是上游给出的常驻路由规则，需要时复制为项目的 `.cursor/rules/golang-always.mdc`。

## 与 golang-best-practices 的分工

`skills/dev/golang-best-practices` 是本仓库的通用 Go 工程指南，负责包边界、依赖组装、配置与资源生命周期、跨模块改动和交付检查。它按项目规模与已有约定选择组织方式，不绑定某个示范项目、统一目录或框架组合。

本目录负责具体技术判断：性能测量、线上可观测、排障、安全审计、工具链（`gopls`、`godig`、`govulncheck`）、CLI 与协议，以及各库的用法细节。

两边同时可用时：

- 用户要求与项目已有约定优先；工程指南中的组织方式和上游风格偏好都不能要求无关搬包、改测试组织或迁移工具；
- 新服务、跨层改动或项目级架构审查先读取 `golang-best-practices`，再按需要选择主题；单函数、并发、测试或 profiling 等单主题任务直接读对应主题；
- 初始选择一个主 skill，确有具体需要再加至多两个主题；其他主题在新证据需要时再读取，不重复加载已读正文；
- `golang-best-practices` 未注册时继续使用已有项目资料与主题；通过当前客户端清单中的名称和路径读取，不假定上游限定名称就是本地标识符。

编排器的本地适配已写入 `golang-how-to/SKILL.md`，不依赖客户端自动读取本 README。

## 维护

- 同步上游：`bash scripts/sync-golang-skills.sh`
- 校验仓库规范：`python3 scripts/validate-skills.py --strict`
- 工具回归测试：`python3 -B -m unittest discover -s scripts/tests -v`
- 上游各 skill 独立版本号，见各自 frontmatter 的 `metadata.version`
- 本地修正、本地评估用例与夹具：正文/路由/断言修正和 `local_cases` 都在 [`golang-overrides.json`](../../scripts/golang-overrides.json)，由同步重放；夹具在 [`docs/evals/fixtures/`](../../docs/evals/fixtures)
- 上游历史评估见 [`EVALUATIONS.md`](EVALUATIONS.md)；本地组合用例与验证边界见 [组合评估](../../docs/evals/golang-composition.md)，本地修正后的版本不能直接继承上游分数。

同步脚本先拒绝空的 skill 集合，重放本地修正，再对暂存目录执行严格校验；全部通过后才替换目标。替换失败会恢复旧副本，恢复失败会保留备份并报告恢复路径。`README.md` 和 `EVALUATIONS.md` 继续保留，提交号与评估记录仍需人工核对。

### 本地修正

[`apply-golang-overrides.py`](../../scripts/apply-golang-overrides.py) 读取清单，先确认所有正文补丁可匹配，再写入修改。可重复执行，已修正文本不会重复改写：

- 精简 46 条 description，保留任务触发与相邻主题边界，库 skill 仅在已采用或明确要求该库时适用；
- 通过清单 `global_patterns` 把正文与 references 中的上游引用标识符 `samber/cc-skills-golang@golang-*` 改成本地注册名 `golang-*`，避免模型按上游名查找不存在的 skill；仅保留 `samber/cc-skills-golang@<name>` 这类来源说明。全局替换在逐文件补丁之后执行，其 `old` 文本来自上游原文；
- `golang-how-to` 接入可选本地蓝图，按需读取主题，使用当前环境注册的名称和路径，路由本身不要求安装 gopls；主文仅保留路由表与简短工具分工，完整边界资料按需读取；
- `golang-how-to` 及其 Configure 参考与布局 skill 统一：只有用户明确请求持久化 agent 配置时才写入指定配置文件；复用已给定目标和主题，不默认跨 harness 修改或强制加载 11 个主题，也不重复询问已有授权；
- `golang-project-layout` 允许根目录单包与按业务能力组织；目录、自动化和配置按需要创建，不强制 `cmd/`、`internal/`、`pkg/` 或额外架构/DI 选择，也不擅自修改 agent 配置；
- `golang-testing` 保留测试独立性、行为断言和竞态检查等正确性要求；文件命名、组织顺序与集成测试选择方式服从项目约定，不强制 build tags；
- 保留以下文档链接修正：

- `golang-gopls/SKILL.md` 新增 Settings and configuration 一节，链接此前未被引用的 `references/settings.md`；

- `golang-documentation/references/project-docs.md` 的 README、CONTRIBUTING、CHANGELOG 模板链接：`./templates/` → `../assets/templates/`；
- `golang-documentation/references/library.md` 的 llms.txt 模板链接：`./templates/` → `../assets/templates/`；
- `golang-troubleshooting/references/methodology.md` 返回 skill 正文的链接：`./SKILL.md` → `../SKILL.md`。

## 未纳入的文件

上游根目录的 `.claude-plugin`、`.codex-plugin`、`.cursor-plugin`（客户端插件清单）、`CITATION.cff`、`CLAUDE.md`、`GOLANG-AI-DRIVEN-REVIEW.md`、`gemini-extension.json`、`clawhub-publish.sh` 未纳入。同步脚本会把这些一并克隆到 `.tmp/`，需要时自行取用。

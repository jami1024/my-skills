# My Skills

一个遵循 [Agent Skills](https://agentskills.io/) 规范的个人 Skills 仓库。源码采用中性 `skills/` 布局，可通过不同客户端的配置接入；不把 wiki 数据复制进来。

## 目录

```text
my-skills/
├── skills/
│   ├── dev/                    # FastAPI、Golang、React、开发流程、读码
│   ├── golang/                 # 上游 samber/cc-skills-golang 的 46 个 Go 主题 skill
│   ├── content/                # library、explain、draft
│   └── session/                # handoff-summary、project-archive
├── template/                   # 新 skill 的起点模板
├── scripts/                    # 仓库校验、同步与评估脚本
├── docs/                       # 架构说明、Docker 指南、优化记录和历史归档
├── .claude/skills -> ../skills  # Claude Code 项目级兼容入口
└── README.md
```

`skills/` 是唯一源码目录。`.claude/skills` 是软链接，不要在里面再创建第二份 skill。

## Skill 一览

当前仓库包含 56 个 skill：`skills/dev`、`skills/content`、`skills/session` 三个分类下的 10 个自有 skill，加上 `skills/golang` 来自上游的 46 个 Go 主题 skill。按需加载分类目录，避免把不相关的规则一并放入模型上下文。

### 开发类 `skills/dev/`

- `fastapi-best-practices`：FastAPI 后端项目与 API 开发
- `golang-best-practices`：Go 项目包边界、依赖组装、生命周期与工程交付
- `react-best-practices`：React 应用与前端工程
- `development-workflow`：需求、设计、tasks、审查与验证流程
- `code-reading`：阅读陌生代码库并产出结构化读码报告（收录自 lichuang/how-to-read-code）

### Go 主题类 `skills/golang/`

取自 [samber/cc-skills-golang](https://github.com/samber/cc-skills-golang)（MIT），仅应用有记录的本地描述精简、路由、测试偏好和文档链接修正，含 1 个编排器 `golang-how-to` 与 45 个主题 skill，覆盖语言与风格、并发、错误、测试与基准、可观测、排障、安全、数据库、gRPC/GraphQL/Swagger、CLI、依赖注入、以及 samber 各库的用法。来源、同步方式、与 `golang-best-practices` 的分工见 [`skills/golang/README.md`](skills/golang/README.md)。

### 内容类 `skills/content/`

- `library`：来源材料入库、Wiki 查询与质量检查
- `explain`：概念解释与项目驱动学习教程
- `draft`：播客或访谈素材转中文公众号 Markdown

### 会话类 `skills/session/`

- `handoff-summary`：生成会话交接总结
- `project-archive`：生成项目技术归档

## 接入方式

### pi

在 `~/.pi/agent/settings.json` 中按需指向分类目录。只使用内容工作流时：

```json
{
  "skills": [
    "~/Downloads/Project/my-skills/skills/content"
  ]
}
```

需要开发类或会话类时，再分别添加 `skills/dev` 或 `skills/session`。不要默认指向整个 `skills/`，否则所有类别都会注册到模型上下文中。若同时加载多个分类，优先让请求中最具体的技术 skill 负责实现，`development-workflow` 只补充通用流程。

`skills/golang` 单独指向，不并入 `skills/dev`：它的 46 条 description 会常驻会话上下文，正文按需读取。只在确实要做 Go 主题判断时加载。

同时加载 `skills/dev` 与 `skills/golang` 时，用户要求与项目已有约定优先。新服务、跨层改动和架构审查先读 `golang-best-practices`；单主题任务直接读对应主题，其他主题按实际需要再加载。46 条主题描述已精简至合计 7295 字符，正文不会一起加载。

### Claude Code

在本仓库作为项目打开时，`.claude/skills` 会指向 `skills/`。如果要在其他项目复用，优先使用 Claude Code 的 plugin/skill 配置；不要复制目录产生分叉。

## 创建新 skill

```bash
cp -R template skills/content/my-skill-name
# 修改 skills/content/my-skill-name/SKILL.md
python3 scripts/validate-skills.py
```

规范要求：

- 目录名必须与 frontmatter 的 `name` 完全一致；
- `name` 使用小写字母、数字和连字符；
- `description` 说明“做什么、何时使用、不适用什么”；
- 详细材料放到 `references/`，可执行逻辑放到 `scripts/`；
- `SKILL.md` 尽量控制在 500 行以内，引用保持一层深。

## 验证

普通检查：

```bash
python3 scripts/validate-skills.py
```

严格检查（把超过 500 行的旧 skill 也视为失败）：

```bash
python3 scripts/validate-skills.py --strict
```

现有成熟开发 skill 的详细内容已经拆到各自的 `references/`，当前普通检查和严格检查均可通过。以后新增内容超过 500 行时，应继续下沉到 `references/`。

校验还会检查 Markdown 中的本地行内链接与图片路径，跳过代码块、行内代码、外链、锚点，以及 `assets/`、`templates/`、`evals/` 内的生成模板或测试材料；不检查标题锚点是否存在。

工具回归测试：

```bash
python3 -B -m unittest discover -s scripts/tests -v
```

`skills/golang` 是上游副本，同样纳入校验（目录名与 `name` 一致、软链接与文档链接有效、行数上限）。同步时先严格校验暂存内容，再替换目标；替换失败会恢复旧副本。同步上游：

```bash
bash scripts/sync-golang-skills.sh
```

## Eval 回归用例

各 skill 的 `evals/cases.md` 保存手工回归用例，用于验证触发边界、关键输出和反例；它们不会被客户端默认加载。运行说明和覆盖范围见 [`docs/evaluation.md`](docs/evaluation.md)。

`skills/golang` 的上游历史断言与分数见 [`EVALUATIONS.md`](skills/golang/EVALUATIONS.md)，不代表本地适配后的组合效果；与本地正文冲突的上游断言已审阅并改写，见 [断言审阅](docs/evals/golang-assertion-review.md)。本地新增 [10 个组合评估场景](docs/evals/golang-composition.md)，区分只读路由冒烟和实际代码验证，结果单独记录；注册 46 个 skill 的 prompt 开销见 [上下文实测](docs/evals/golang-context-cost.md)。复跑断言用 `scripts/run-skill-eval.py`，测注册开销用 `scripts/measure-skill-context.py`。

## 维护原则

1. 先修改源码层，再验证兼容入口。
2. 不把个人 wiki、临时测试输出或机器绝对路径提交到本仓库。
3. 新 skill 先用代表性输入和反例测试触发边界。
4. Git commit、tag、push 由仓库所有者明确执行。

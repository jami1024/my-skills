# My Skills

一个遵循 [Agent Skills](https://agentskills.io/) 规范的个人 Skills 仓库。源码采用中性 `skills/` 布局，可通过不同客户端的配置接入；不把 wiki 数据复制进来。

## 目录

```text
my-skills/
├── skills/
│   ├── dev/                    # FastAPI、Golang、React、开发流程
│   ├── content/                # library、explain、draft
│   └── session/                # handoff-summary、project-archive
├── template/                   # 新 skill 的起点模板
├── scripts/                    # 仓库校验脚本
├── docs/                       # 架构说明、Docker 指南、优化记录和历史归档
├── .claude/skills -> ../skills  # Claude Code 项目级兼容入口
└── README.md
```

`skills/` 是唯一源码目录。`.claude/skills` 是软链接，不要在里面再创建第二份 skill。

## Skill 一览

当前仓库包含 9 个 skill。按需加载分类目录，避免把不相关的规则一并放入模型上下文。

### 开发类 `skills/dev/`

- `fastapi-best-practices`：FastAPI 后端项目与 API 开发
- `golang-best-practices`：Golang 项目与 Clean Architecture
- `react-best-practices`：React 应用与前端工程
- `development-workflow`：需求、设计、tasks、审查与验证流程

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

需要开发类或会话类时，再分别添加 `skills/dev` 或 `skills/session`。不要默认指向整个 `skills/`，否则所有类别都会注册到模型上下文中。若同时加载多个分类，优先让请求中最具体的技术栈 skill 负责实现，`development-workflow` 只补充通用流程。

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

## Wiki 数据

Wiki 是独立的数据目录，例如：

```text
~/wiki-hub/
├── raw/
└── wiki/
```

`library` 运行时使用用户提供的 Wiki 根目录，不在本仓库硬编码机器路径。工具与数据分开，避免知识更新污染 Skills 的版本历史。

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

## Eval 回归用例

各 skill 的 `evals/cases.md` 保存手工回归用例，用于验证触发边界、关键输出和反例；它们不会被客户端默认加载。运行说明和覆盖范围见 [`docs/evaluation.md`](docs/evaluation.md)。

## 维护原则

1. 先修改源码层，再验证兼容入口。
2. 不把个人 wiki、临时测试输出或机器绝对路径提交到本仓库。
3. 新 skill 先用代表性输入和反例测试触发边界。
4. Git commit、tag、push 由仓库所有者明确执行。

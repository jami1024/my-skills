# My Skills - Claude Code Skills 集合

一个为 Claude Code 设计的 Skills 仓库，涵盖开发最佳实践、学习文档生成、会话交接与项目归档等场景，帮助你高效开发和沉淀知识。

## Skills 一览

### 开发最佳实践（4 个）
- **FastAPI Best Practices** - Python 后端开发最佳实践（Pydantic v2 + async SQLAlchemy）
- **Golang Best Practices** - Go 后端开发最佳实践（Clean Architecture + Wire DI）
- **React Best Practices** - React 前端开发最佳实践（Vite + TanStack Query + Zustand + shadcn/ui）
- **Frontend Design** - 前端 UI 设计指南，反 AI 通用美学，含可搜索设计数据库

### 学习文档生成（1 个）
- **Learning Docs** - 技术学习文档生成（融合 tutorial-docs + technical-writer + diataxis 三种方法论）

### 会话交接与归档（2 个）
- **Handoff Summary** - 会话交接总结生成（支持通用交接 + 代码交接两种模式）
- **Project Archive** - 项目技术归档（项目归档 / 功能归档 / 文档更新三种模式，语言无关）

### 辅助 Skills（1 个）
- **Development Workflow** - 通用软件开发流程（需求引导、设计方案、tasks 任务清单、文档模板、代码审查、CI/CD）

## 快速开始

### 安装

将此仓库克隆到你的项目目录或全局 Claude Code 配置目录：

```bash
# 方式一：克隆到项目目录（仅当前项目生效）
git clone https://github.com/jami1024/my-skills.git
cp -r my-skills/.claude your-project/.claude

# 方式二：克隆到全局配置（所有项目生效）
git clone https://github.com/jami1024/my-skills.git ~/.claude-skills
cp -r ~/.claude-skills/.claude ~/.claude
```

### 使用

Skills 会在对话中自动激活，当你提到相关关键词时：

| Skill | 触发关键词 |
|-------|-----------|
| FastAPI | "FastAPI"、"API 项目"、"Python 后端" |
| Golang | "Golang"、"Go 项目"、"Go 应用" |
| React | "React"、"前端项目"、"shadcn/ui" |
| Frontend Design | "UI 设计"、"落地页"、"界面美化"、"landing page" |
| Learning Docs | "学习文档"、"学习教程"、"入门教程"、"帮我学"、"生成教程" |
| Handoff Summary | "交接总结"、"交接"、"hand-off"、"会话总结"、"代码交接" |
| Project Archive | "项目归档"、"技术归档"、"功能归档"、"补功能文档"、"同步文档" |
| Development Workflow | "做一个"、"构建"、"实现"、"开发流程"、"需求分析"、"写文档"、"ADR"、"任务清单"、"tasks" |

### 初始化新项目

每个技术栈 Skill 都提供了一键初始化脚本：

```bash
# 初始化 FastAPI 项目
bash .claude/skills/fastapi-best-practices/init-project.sh my-api

# 初始化 Golang 项目
bash .claude/skills/golang-best-practices/init-project.sh my-go-app

# 初始化 React 项目
bash .claude/skills/react-best-practices/init-project.sh my-react-app
```

## 目录结构

```
.claude/skills/
├── fastapi-best-practices/     # FastAPI 后端最佳实践
│   ├── SKILL.md                # 核心实践指南
│   ├── init-project.sh         # 项目初始化脚本
│   ├── architecture-design.md  # 架构设计指南
│   ├── development-workflow.md # 开发工作流程
│   ├── scripts/                # lint、迁移、构建脚本
│   └── templates/              # 文档模板 + Docker 模板
│
├── golang-best-practices/      # Golang 后端最佳实践
│   ├── SKILL.md
│   ├── init-project.sh
│   ├── architecture-design.md
│   ├── development-workflow.md
│   ├── scripts/                # lint、迁移、wire-gen、构建脚本
│   └── templates/
│
├── react-best-practices/       # React 前端最佳实践
│   ├── SKILL.md
│   ├── init-project.sh
│   ├── architecture-design.md
│   ├── development-workflow.md
│   ├── scripts/                # lint、分析、构建脚本
│   └── templates/              # 组件模板 + Docker 模板
│
├── frontend-design/            # 前端 UI 设计指南
│   ├── SKILL.md                # 设计美学、字体、配色、动效指南
│   ├── data/                   # 可搜索的设计数据库（CSV）
│   │   ├── styles.csv          # UI 风格库
│   │   ├── typography.csv      # 字体配对库
│   │   ├── colors.csv          # 行业配色方案
│   │   ├── landing.csv         # 落地页结构
│   │   ├── products.csv        # 产品类型推荐
│   │   ├── charts.csv          # 图表类型推荐
│   │   ├── ux-guidelines.csv   # UX 最佳实践
│   │   ├── prompts.csv         # 设计提示词
│   │   └── stacks/             # 10+ 技术栈指南
│   ├── scripts/                # 设计数据库搜索脚本
│   └── templates/              # 设计简报模板
│
├── learning-docs/              # 技术学习文档生成
│   ├── SKILL.md                # 生成规范和写作原则
│   └── references/
│       ├── example-go-interface.md # 参考示例
│       └── template.md         # 通用文档模板
│
├── handoff-summary/            # 会话交接总结生成
│   └── SKILL.md                # 通用交接 + 代码交接两种模式
│
├── project-archive/            # 项目技术归档
│   └── SKILL.md                # 项目归档 / 功能归档 / 文档更新三种模式
│
├── development-workflow/       # 通用开发流程指南
│   ├── SKILL.md                # 六步流程 + CI/CD + 分支策略
│   └── templates/              # 需求/设计/ADR/评审模板
│
└── DOCKER_GUIDE.md             # Docker 部署通用指南
```

## 核心架构

### FastAPI (分层架构)
```
API 层 (Router) → 业务逻辑层 (Service) → 数据访问层 (Model)
```

### Golang (Clean Architecture)
```
Handler 层 → Biz 层 → Store 层 → Model 层
```

### React (Feature-Based)
```
Pages → Features → Components → UI
```

## Skill 协同关系

```
development-workflow (通用开发流程)
         ↓
    ┌────┼────────────┐
    ↓    ↓            ↓
fastapi  golang     react       ← 技术栈 Skill
                      ↓
               frontend-design  ← UI 设计 Skill

learning-docs    ← 为任意技术栈生成学习文档
handoff-summary  ← 会话结束时生成交接总结
project-archive  ← 阶段完成时生成技术归档
```

典型使用场景：

```bash
# 1. 需求分析（development-workflow）
"帮我分析这个需求，写一个技术设计文档"

# 2. 后端开发（golang-best-practices + development-workflow）
"用 Go 创建一个用户管理 API"

# 3. 前端开发 + 设计（react-best-practices + frontend-design）
"创建一个 React 仪表板，要有独特的设计风格"

# 4. 全栈项目（多 Skill 联动）
"帮我搭建一个完整的博客系统，后端用 FastAPI，前端用 React"

# 5. 学习新技术（learning-docs）
"帮我生成一份 Go 接口的学习文档"

# 6. 会话交接（handoff-summary）
"生成交接总结，让下一个会话接手"

# 7. 项目归档（project-archive）
"这个功能开发完了，帮我做一次技术归档"
```

## 文档与执行模板

通过 `development-workflow` Skill 统一管理：

| 模板 | 用途 |
|------|------|
| `requirement-template.md` | 需求文档（用户故事、验收标准） |
| `design-template.md` | 技术设计文档（架构、API、数据模型） |
| `tasks-template.md` | Tasks 清单模板（执行追踪、状态更新、验证记录） |
| `adr-template.md` | 架构决策记录（选型理由、权衡分析） |
| `architecture-review-checklist.md` | 架构评审清单 |

## 更新日志

### 2026-03-31

**Development Workflow Skill**
- 重构核心流程：强化设计先行（HARD-GATE）、需求引导一次一问、防绕过机制
- 合并 Doc Co-Authoring Skill，文档模板和读者测试能力整合进 development-workflow
- 文档模板通用化：去掉 FastAPI 特定代码，改为语言无关的骨架格式
- 精简模板体积：design-template 563→140 行、adr-template 317→100 行、checklist 513→160 行

### 2026-04-01

**Development Workflow Skill**
- 新增显式 `tasks` 任务清单机制：中等和复杂任务必须创建并持续维护任务状态
- 将 `tasks` 机制接入实施规划和代码实现阶段，要求先给 `## Tasks` 总览，再按任务执行
- 新增 `templates/tasks-template.md`，补齐文件化任务追踪模板
- 补充 tasks 反模式、覆盖度自审和测试收尾规则，避免只靠记忆追踪进度

### 2026-03-12

- 新增 **Handoff Summary** Skill —— 会话交接总结生成（通用交接 + 代码交接两种模式）
- 新增 **Project Archive** Skill —— 项目技术归档（项目归档 / 功能归档 / 文档更新三种模式，语言无关）
- 精简已有 Skill 文档，移除冗余内容
- Learning Docs Skill 增加去 AI 痕迹写作规范

### 2026-02-11

**FastAPI Skill**
- 升级 Pydantic v1 → v2（`@field_validator`、`model_config = ConfigDict(...)`、`str | None`）
- 修复异步测试：`TestClient` → `httpx.AsyncClient` + `ASGITransport`
- `sessionmaker` → `async_sessionmaker`
- 新增 `lifespan` 上下文管理器（替代已废弃的 `on_event`）
- 新增通用分页模式（`PaginatedResponse[T]` 泛型）

**Golang Skill**
- `github.com/golang/mock` → `go.uber.org/mock`（前者已废弃）
- Makefile 工具安装 `go get` → `go install`

**Development Workflow Skill**
- 新增 Git 分支策略（GitHub Flow + Git Flow）
- 新增 CI/CD 流水线（GitHub Actions 示例 + 最佳实践）
- `TodoWrite` → `TaskCreate`

**Frontend Design Skill**
- 修复 framer-motion 示例变量名冲突

## 贡献

欢迎提交 Issue 和 Pull Request 来改进这些 Skills。

## 许可证

MIT License

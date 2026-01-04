# My Skills - Claude Code 最佳实践 Skills 集合

一个为 Claude Code 设计的开发最佳实践 Skills 仓库，包含 FastAPI、Golang 和 React 三个技术栈的完整开发指南。

## 特性

- **FastAPI Best Practices** - Python 后端开发最佳实践
- **Golang Best Practices** - Go 后端开发最佳实践
- **React Best Practices** - React 前端开发最佳实践
- **Development Workflow** - 通用软件开发流程指南

每个 Skill 都提供：
- 完整的项目结构和架构设计指南
- 开发工作流程和规范
- 一键初始化脚本
- 文档模板（需求、设计、ADR、评审清单）
- 详细的代码示例和最佳实践

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

### 初始化新项目

每个 Skill 都提供了一键初始化脚本：

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
│   └── templates/              # 文档模板
│
├── golang-best-practices/      # Golang 后端最佳实践
│   ├── SKILL.md
│   ├── init-project.sh
│   ├── architecture-design.md
│   ├── development-workflow.md
│   └── templates/
│
├── react-best-practices/       # React 前端最佳实践
│   ├── SKILL.md
│   ├── init-project.sh
│   ├── architecture-design.md
│   ├── development-workflow.md
│   └── templates/
│
└── development-workflow/       # 通用开发流程指南
    └── SKILL.md
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

## 文档模板

每个 Skill 都包含以下文档模板：

- `requirement-template.md` - 需求文档模板
- `design-template.md` - 技术设计文档模板
- `adr-template.md` - 架构决策记录模板
- `architecture-review-checklist.md` - 架构评审清单

## 贡献

欢迎提交 Issue 和 Pull Request 来改进这些 Skills。

## 许可证

MIT License

# 软件开发工作流程 Skill

**版本**: v2.2.0
**语言无关**: ✅

通用的软件工程实践和开发流程规范。

## 概述

本 Skill 提供语言和框架无关的软件开发最佳实践，包括：

- 需求引导和设计方案
- 任务分解和实施规划
- 代码审查清单
- 测试策略
- 文档模板 + tasks 文件模板（需求、设计、tasks、ADR、评审清单）

## 适用场景

### 使用本 Skill

- 创建、构建、添加功能、修改行为
- 需求分析和技术设计
- 编写需求文档、设计文档、ADR
- 代码审查流程和清单
- 测试策略规划
- 项目管理和任务分解

### 与其他 Skill 协同

本 Skill 提供通用流程，配合技术栈特定的 Skill 使用：

```
development-workflow (本 Skill)
         +
fastapi-best-practices  →  FastAPI 项目开发
         +
golang-best-practices   →  Golang 项目开发
         +
react-best-practices    →  React 项目开发
```

## 核心内容

### 1. 六步开发流程

```
需求引导 → 设计方案 → 实施规划 → 代码实现 → 代码审查 → 测试验证
```

### 2. 文档模板与 Tasks 文件模板

内置 4 个文档模板和 1 个 tasks 文件模板，形成 `requirement -> design -> ADR -> tasks -> review` 的追踪链路：

| 模板 | 用途 |
|------|------|
| `requirement-template.md` | 需求文档（目标、范围、需求 ID、验收和追踪矩阵） |
| `design-template.md` | 技术设计文档（方案摘要、组件职责、契约/数据、设计追踪） |
| `tasks-template.md` | Tasks 文件模板（中等/复杂任务的执行追踪、状态更新、验证记录） |
| `adr-template.md` | 架构决策记录（备选方案、决策理由、验证与回滚） |
| `architecture-review-checklist.md` | 架构评审清单（状态、证据、后续任务） |

中等和复杂任务必须落一个独立 tasks 文件。默认命名规则使用 `<主题>_tasks.md`，并与需求/设计文档共用同一个主题前缀；例如：`用户导入_requirement.md`、`用户导入_design.md`、`用户导入_tasks.md`。如果项目已有文档目录规范，也可以使用等价独立路径。原生任务工具只能辅助同步状态，不能替代该文件。

### 3. 最佳实践

- 强制先设计后编码（HARD-GATE）
- Git 提交规范（Conventional Commits）
- 代码审查清单
- 测试金字塔
- 读者测试（用子 agent 验证文档可读性）

## 文档结构

```
development-workflow/
├── SKILL.md                              # 核心工作流程和最佳实践
├── README.md                             # 本文件
└── templates/                            # 文档模板 + tasks 文件模板
    ├── requirement-template.md           # 需求文档模板
    ├── design-template.md                # 设计文档模板
    ├── tasks-template.md                 # Tasks 文件模板
    ├── adr-template.md                   # 架构决策记录模板
    └── architecture-review-checklist.md  # 架构评审清单
```

## 快速开始

### 场景 1：编写需求文档

```
1. 使用需求文档模板
   参考：templates/requirement-template.md

2. 填写需求内容
   - 背景和目标
   - 用户故事
   - 功能需求
   - 验收标准

3. 评审和确认
```

### 场景 2：记录架构决策

```
1. 使用 ADR 模板
   参考：templates/adr-template.md

2. 填写决策内容
   - 背景
   - 决策
   - 原因
   - 后果

3. 团队评审
```

### 场景 3：中等或复杂任务的执行追踪

```
1. 创建独立 tasks 文件
   默认：`<主题>_tasks.md`
   如已存在需求/设计文档，则复用相同主题前缀
   参考：templates/tasks-template.md

2. 填写任务清单
   - 稳定任务编号
   - 当前状态
   - 验证记录

3. 执行中持续更新
```

### 场景 4：代码审查

```
使用代码审查清单（SKILL.md 第 5 节）：

- [ ] 功能性检查
- [ ] 可读性检查
- [ ] 可维护性检查
- [ ] 性能检查
- [ ] 安全性检查
- [ ] 测试覆盖
```

## 与技术栈 Skill 的关系

```
┌─────────────────────────────────────────────────┐
│          development-workflow                   │
│   (通用流程 + 模板体系 + 读者测试)                │
└───────────────┬─────────────────────────────────┘
                │
        ┌───────┼───────┐
        ↓       ↓       ↓
   ┌─────┐ ┌─────┐ ┌─────┐
   │FastAPI│ │Golang│ │React│
   │(具体) │ │(具体)│ │(具体)│
   └─────┘ └─────┘ └─────┘
```

**分工**：
- **development-workflow**：通用流程、模板体系、最佳实践
- **技术栈 Skill**：具体语言/框架的实现、架构模式、工具链

## 相关资源

### 内部 Skills
- [FastAPI Best Practices](../fastapi-best-practices/README.md)
- [Golang Best Practices](../golang-best-practices/README.md)
- [React Best Practices](../react-best-practices/README.md)

### 外部资源
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Architecture Decision Records](https://adr.github.io/)
- [Google Engineering Practices](https://google.github.io/eng-practices/)

## 维护

**版本**: v2.2.0
**最后更新**: 2026-04-01

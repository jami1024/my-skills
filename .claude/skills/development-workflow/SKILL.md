---
name: development-workflow
description: 当用户需要了解软件开发流程、需求分析、技术设计、代码审查、测试策略、项目管理、CI/CD、分支策略时使用。触发词：开发流程、需求分析、技术设计、代码审查、测试策略、项目管理、文档模板、ADR、CI/CD、分支策略
---

# 软件开发工作流程

语言无关的通用开发流程和最佳实践。与具体技术栈的 skill（fastapi/golang/react-best-practices）协同使用。

编写正式文档（需求、设计、ADR）时，配合 **doc-coauthoring skill** 的结构化协作流程和标准模板。

---

## 🔄 核心开发流程

### 标准六步流程

```
1. 需求分析
   ↓
2. 技术设计
   ↓
3. 任务分解
   ↓
4. 代码实现
   ↓
5. 代码审查
   ↓
6. 测试验证
```

---

## 1️⃣ 需求分析

理解要实现的功能和用户场景，明确需求边界。

### 判断是否需要文档化

- ✅ **需要**：新功能、多模块影响、架构变更、需要评审的改动
- ❌ **不需要**：简单 Bug 修复、代码格式化、文档更新、单文件小改动

### 用户故事格式

```
作为 系统管理员
我想要 批量导入用户数据
以便于 快速完成用户初始化

验收标准：
- [ ] 支持 CSV 和 Excel 格式
- [ ] 单次可导入 1000 条记录
- [ ] 导入失败时提供详细错误信息
```

---

## 2️⃣ 技术设计

设计技术方案，做出架构决策，记录关键选择。

### 架构决策记录（ADR）

对重要的技术决策（技术栈选择、架构模式、设计模式、影响长期维护的决策），使用 ADR 记录：

```markdown
# ADR-001: 选择 PostgreSQL 作为主数据库

## 状态：已接受

## 背景
需要为新项目选择数据库，要求支持复杂查询、事务和高并发。

## 决策
选择 PostgreSQL。

## 原因
1. 强大的 ACID 事务支持
2. 丰富的数据类型（JSON、数组等）
3. 优秀的性能和可扩展性

## 后果
- 正面：稳定可靠，功能丰富
- 负面：相比 NoSQL 在某些场景下性能稍差
```

---

## 3️⃣ 任务分解

将大任务拆为小的、可独立完成的子任务。每个任务：单一职责、可测试、2-8 小时完成、有明确产出标准。

使用 TaskCreate 创建任务清单，按优先级排列：P0（紧急重要）→ P1（重要不紧急）→ P2（紧急不重要）→ P3（有空再做）。

---

## 4️⃣ 代码实现

先设计后实现，小步提交（每次可运行），发现坏味道立即重构，至少写单元测试。

代码质量：命名清晰、函数 < 50 行、注释解释"为什么"而非"是什么"、DRY、错误处理完善。

### Git 提交规范（Conventional Commits）

```
<type>(<scope>): <subject>
```

Type：`feat` 新功能 | `fix` 修复 | `docs` 文档 | `refactor` 重构 | `perf` 性能 | `test` 测试 | `chore` 构建

示例：`feat(user): 添加用户批量导入功能`

---

## 5️⃣ 代码审查

通过 Code Review 发现问题、提高质量、分享知识。

### 审查清单

| 维度 | 检查要点 |
|------|---------|
| 功能性 | 需求实现？边界条件？错误处理？潜在 Bug？ |
| 可读性 | 易于理解？命名清晰？必要注释？结构清晰？ |
| 可维护性 | SOLID 原则？无重复？函数不过长？易扩展？ |
| 性能 | 性能问题？查询优化？内存泄漏？不必要计算？ |
| 安全性 | SQL 注入？XSS？敏感信息加密？权限检查？ |
| 测试 | 有单元测试？覆盖率足够？测试边界条件？ |

### Review 礼仪

- 审查者：提建设性意见（解释为什么），区分"必须改"和"建议改"，认可好代码
- 被审查者：开放心态，主动解释复杂逻辑，及时回应

---

## 6️⃣ 测试验证

### 测试金字塔

单元测试（大量，70-80% 覆盖）→ 集成测试（适量，关键路径）→ E2E 测试（少量，核心业务流程）

### 测试策略

关键路径优先 → 边界条件 → 错误场景 → 性能敏感功能 → Bug 修复后回归测试

### 命名规范

```
test_<功能>_<场景>_<预期结果>

示例：
test_create_user_with_valid_data_succeeds()
test_create_user_with_duplicate_email_fails()
```

---

## 🔀 Git 分支策略

### GitHub Flow（推荐中小型项目）

```
main ─────────────────────────────────────────→
  └── feature/add-user-import ──── PR ──→ merge
  └── fix/login-error ───────────── PR ──→ merge
```

**规则**：
1. `main` 分支始终可部署
2. 从 `main` 创建功能分支，命名：`feature/xxx`、`fix/xxx`、`refactor/xxx`
3. 通过 Pull Request 合并，必须通过 CI 和 Code Review
4. 合并后立即部署

### Git Flow（适合版本发布制项目）

```
main ────────────────────────── tag v1.0 ── tag v1.1 ──→
  └── develop ────────────────────────────────────────→
       └── feature/xxx ──→ merge to develop
       └── release/1.1 ──→ merge to main + develop
  └── hotfix/critical-bug ──→ merge to main + develop
```

**何时使用 Git Flow**：
- 有明确版本发布周期的项目
- 需要同时维护多个版本
- 需要 hotfix 机制

---

## 🚀 CI/CD 流水线

### 基础流水线结构

```
代码提交 → 代码检查 → 单元测试 → 构建 → 部署
   ↓          ↓          ↓        ↓       ↓
  Push      Lint      Test     Build   Deploy
          + Format   + Cover
```

### GitHub Actions 示例

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Setup
        uses: actions/setup-node@v4  # 或 setup-python、setup-go
      - name: Lint
        run: make lint

  test:
    runs-on: ubuntu-latest
    needs: lint
    steps:
      - uses: actions/checkout@v4
      - name: Setup
        uses: actions/setup-node@v4
      - name: Test
        run: make test
      - name: Upload coverage
        uses: codecov/codecov-action@v4

  build:
    runs-on: ubuntu-latest
    needs: test
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v4
      - name: Build
        run: make build
```

### CI/CD 最佳实践

1. **快速反馈** - CI 流程控制在 10 分钟内
2. **并行执行** - lint 和 test 可以并行
3. **缓存依赖** - 使用 `actions/cache` 加速构建
4. **环境隔离** - staging 环境验证后再部署 production
5. **回滚机制** - 部署失败时能快速回滚
6. **密钥管理** - 使用 GitHub Secrets / Vault，不硬编码

---

## 常见陷阱

| 陷阱 | 正确做法 |
|------|---------|
| ❌ 跳过设计直接写代码 | ✅ 先需求分析和技术设计，再动手 |
| ❌ 忽略测试 | ✅ 至少写单元测试，Bug 修复后加回归测试 |
| ❌ 过度设计 | ✅ 够用就好，不为假设需求设计 |
| ❌ "以后再重构" | ✅ 发现坏味道立即重构 |
| ❌ 忽略 Code Review 反馈 | ✅ 反馈是学习机会，及时回应 |
| ❌ 代码和文档不同步 | ✅ 代码变更时同步更新文档 |

---

## 参考资源

- [Conventional Commits](https://www.conventionalcommits.org/)
- [Architecture Decision Records](https://adr.github.io/)
- [Code Review Best Practices](https://google.github.io/eng-practices/review/)
- [Testing Best Practices](https://martinfowler.com/testing/)

---

**使用此 skill 时，Claude 将：**
- 按六步流程推进：需求分析 → 技术设计 → 任务分解 → 代码实现 → 代码审查 → 测试验证
- 判断是否需要文档化，需要时配合 doc-coauthoring skill
- 对重要技术决策使用 ADR 记录
- 使用 Conventional Commits 规范提交
- 执行代码审查清单（功能性、可读性、可维护性、性能、安全性、测试）
- 推荐合适的分支策略（GitHub Flow / Git Flow）
- 配置 CI/CD 流水线确保代码质量

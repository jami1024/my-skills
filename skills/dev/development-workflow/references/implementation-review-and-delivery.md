# 实现、审查与交付参考

本文件承接 `development-workflow/SKILL.md` 的详细实现、审查、测试、分支和 CI/CD 规则。

## 4️⃣ 代码实现

先设计后实现，小步交付（每次可验证），发现坏味道再重构；对业务逻辑补充单元或集成测试，其他改动选择与风险匹配的验证方式。

代码质量：命名清晰、职责边界明确、注释解释“为什么”而非“是什么”、避免无依据的重复和抽象，错误处理与项目约定一致。不要用固定行数作为拆分标准。

### 执行时维护 Tasks

- 开始任务前，确认它已经存在于 `## Tasks` 或当前任务 checklist 中
- 开始执行时，把当前任务标记为“进行中”或在进度汇报中明确指出当前任务
- 完成后立刻改为已完成，并附上验证结果
- 如果发现需要新增任务，先更新 tasks 文件，再继续编码
- 未经更新 tasks 或 checklist，不要跳到下一个任务

示例：

```markdown
## Tasks
- [x] T1 编写失败测试
- [x] T2 实现最小代码
- [ ] T3 运行回归测试（进行中）
- [ ] T4 更新文档（阻塞：等待接口字段确认）
```

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

单元测试（快速、覆盖稳定的业务规则）→ 集成测试（覆盖关键边界和依赖协作）→ E2E 测试（少量、覆盖核心用户流程）。测试比例和覆盖率目标根据风险、项目类型和现有基线确定，不设所有项目通用的百分比。

### 测试策略

关键路径优先 → 边界条件 → 错误场景 → 性能敏感功能 → Bug 修复后回归测试

测试完成后，同步关闭对应 tasks，并记录验证结论；不要出现“测试做完了，但 tasks 文件还停留在未完成”的状态。

### 命名规范

```
test_<功能>_<场景>_<预期结果>

示例：
test_create_user_with_valid_data_succeeds()
test_create_user_with_duplicate_email_fails()
```

---

## 🔀 Git 分支策略

根据团队规模、发布方式和仓库现状选择分支策略；单人项目或小改动不必为了流程额外创建分支。

### GitHub Flow（适合持续交付的中小型项目）

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

## 核心设计原则

### YAGNI — 你不会需要它的

- 主动删减不必要的特性，不要为假设的未来需求设计
- 三行相似代码好过一个过早的抽象
- 只实现用户明确要求的功能

### 设计隔离与清晰性

- 把系统拆成更小的单元，每个单元只有一个清晰职责
- 通过明确定义的接口通信，可独立理解和测试
- 对每个单元，你应能回答：它做什么、怎么用它、它依赖什么

---

## 防绕过机制

以下想法在**复杂任务**中意味着你可能正在绕过步骤 1-2——先确认是否确实缺少设计，而不是机械阻塞简单工作：

| 你的想法 | 现实 |
|---------|------|
| "用户已经说了要什么" | 用户说了要什么 ≠ 设计已经完成 |
| "我先做一点再说" | 复杂任务做之前先想清楚 |
| "这个流程太重了" | 复杂任务的设计可以简短，但不能跳过 |
| "上次类似的不需要设计" | 每个复杂任务都需要，无例外 |

注意：简单任务（单文件改动、明确 bug 修复）不受此限制，直接执行即可。

---

## 常见陷阱

| 陷阱 | 正确做法 |
|------|---------|
| ❌ 跳过设计直接写代码 | ✅ 先需求引导和设计方案，获得用户批准再动手 |
| ❌ 忽略测试 | ✅ 按风险选择测试或其他验证；Bug 修复后尽量补充可复现的回归测试 |
| ❌ 过度设计 | ✅ 够用就好，不为假设需求设计 |
| ❌ "以后再重构" | ✅ 发现坏味道立即重构 |
| ❌ 忽略 Code Review 反馈 | ✅ 反馈是学习机会，及时回应 |
| ❌ 代码和文档不同步 | ✅ 代码变更时同步更新文档 |
| ❌ 不维护 tasks 文件，靠记忆追踪进度 | ✅ 对需要文件化追踪的中等和复杂任务创建并持续更新 tasks 文件；短小任务用 checklist 也要记录验证 |

---

## 参考资源

- [Conventional Commits](https://www.conventionalcommits.org/)
- [Architecture Decision Records](https://adr.github.io/)
- [Code Review Best Practices](https://google.github.io/eng-practices/review/)
- [Testing Best Practices](https://martinfowler.com/testing/)

---

**使用此 skill 时，Claude 将：**
- 按复杂度选择流程：简单任务直接执行；中等任务确认范围和方案；复杂任务在设计与计划获批后再实现
- 用一次一问、选择题优先的方式澄清高风险未知；不为低风险任务制造多轮审批
- 提供有依据的方案对比，并在设计结尾请求确认；只有存在关键分歧时才分段确认
- 对需要文件化追踪的中等和复杂任务创建并维护 tasks 文件；短小任务可用 checklist，但必须记录验证结果
- 将任务拆成独立、可验证的步骤，通常控制在 5-15 分钟，避免无意义的碎片化
- 根据改动风险选择测试优先、回归测试、静态检查或人工验证，不机械要求所有任务使用 TDD
- 需要正式文档或执行清单时使用内置模板，并通过读者测试或执行验证确保内容可用
- 对重要技术决策使用 ADR；分支策略和 Conventional Commits 按项目约定采用，而不是强制迁移
- 执行代码审查清单（功能性、可读性、可维护性、性能、安全、测试）并记录可复现证据
- 根据项目现状推荐合适的分支策略和 CI/CD 流水线

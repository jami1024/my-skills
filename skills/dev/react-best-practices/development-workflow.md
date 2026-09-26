# React 开发工作流程

**版本**: v1.2.0
**更新日期**: 2026-09-25

本流程适用于新建和已有 React 项目的架构设计、功能开发、重构和代码审查。它不提供固定脚手架，也不预设框架、路由、状态库或 UI 组件库。

## 核心流程

```text
需求确认 → 项目勘察 → 方案设计 → 分步实现 → 验证 → 审查
```

每一步都应留下可检查的结果；小改动可以合并步骤，但不能跳过项目勘察和验证。

## 第一步：需求确认

明确：

- 用户目标和成功标准；
- 受影响的页面、组件、接口和数据；
- loading、error、empty、权限和网络失败状态；
- 是否涉及路由、持久化、国际化、可访问性或响应式行为；
- 不在本次范围内的内容。

复杂功能可使用 [`templates/requirement-template.md`](templates/requirement-template.md)，简单修复保留短计划即可。

## 第二步：项目勘察

新项目没有配置文件时，先确认产品类型、部署目标、SPA/SSR、数据来源、认证、团队约束和测试要求，并将选择理由记录在架构决策中。

已有项目先读取：

- `package.json`、lockfile 和现有 scripts；
- `tsconfig.json`、框架配置和环境变量约定；
- 路由入口、功能目录、组件库、样式入口和 API 层；
- 测试、lint、typecheck、build 配置；
- `components.json`（如存在）。

输出一段简短结论：

```text
框架/构建：
包管理器：
路由方案：
服务端数据方案：
客户端状态方案：
UI/样式方案：
测试与验证命令：
```

不重复实现已有工具，不因为示例代码而新增依赖。

## 第三步：方案设计

根据项目现状确定：

1. 功能目录和组件边界；
2. 数据流和状态归属；
3. API、错误映射和缓存策略；
4. 路由、权限和 URL 状态；
5. 测试层级和完成标准。

优先使用组件组合、状态就近管理和已有抽象。只有重复出现且语义稳定时才提升为共享模块。

复杂方案可使用 [`templates/design-template.md`](templates/design-template.md) 和 [`templates/adr-template.md`](templates/adr-template.md)。

## 第四步：分步实现

推荐顺序：

```text
类型/数据契约 → API 或数据层 → 状态与 Hooks → 组件 → 页面/路由 → 测试
```

实现要求：

- 先建立最小可工作的主流程，再补边界状态；
- 复用项目已有的组件、样式 token、请求层和错误处理；
- 不把服务端响应、业务状态和展示状态混在同一个组件中；
- 事件处理函数表达业务动作，避免把复杂逻辑写进 JSX；
- 不为尚未确认的性能问题添加 `memo`、缓存或抽象层。

## 第五步：验证

按项目现有命令执行：

```text
typecheck → lint → unit/integration test → build → E2E/a11y（如已配置）
```

至少验证：

- 主成功路径；
- loading、error、empty、权限和重复提交；
- 键盘操作、焦点、语义 HTML 和颜色对比度；
- 目标视口下的响应式布局；
- 生产构建和客户端 Bundle 中没有敏感信息。

## 第六步：审查

### 工程实践

- [ ] 目录和模块边界符合项目现有约定；
- [ ] 状态归属清晰，没有无必要的全局状态；
- [ ] API 错误、取消请求和重复请求已处理；
- [ ] 类型、lint、测试和构建均通过；
- [ ] 没有引入未使用的依赖或无依据的性能优化。

### 界面与可访问性

- [ ] 复用了项目已有组件和设计 token；
- [ ] 覆盖 loading、error、empty 和成功状态；
- [ ] 键盘操作和焦点状态可用；
- [ ] 使用语义 HTML，表单控件有明确标签；
- [ ] 响应式布局没有横向滚动；
- [ ] 动效尊重 `prefers-reduced-motion`。

## 相关文档

- [`SKILL.md`](SKILL.md)：React 核心原则和验证清单；
- [`architecture-design.md`](architecture-design.md)：架构决策索引；
- [`references/architecture-patterns.md`](references/architecture-patterns.md)：详细架构示例；
- [`references/performance-and-testing.md`](references/performance-and-testing.md)：性能和测试参考；
- [`templates/`](templates/)：需求、设计、组件和审查模板。

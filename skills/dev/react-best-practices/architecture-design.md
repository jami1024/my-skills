# React 架构设计索引

本文件是 React 架构参考入口。先完成项目勘察，再按需阅读 [`references/architecture-patterns.md`](references/architecture-patterns.md)。

## 快速决策

新项目没有现有框架时，先形成一页架构决策：产品类型、部署目标、SPA/SSR、数据来源、认证、团队熟悉度、测试和可观测性，再推荐技术栈。现有项目则先遵循已有框架和依赖。

1. **选择框架**：根据渲染需求、部署环境和团队约束，在 Vite、Next.js 或其他方案中做取舍，不以个人偏好替代项目需求。
2. **按功能组织**：优先把同一功能的 API、组件、Hooks、类型和页面放在一起；只有跨功能复用时才提升到全局目录。
3. **就近管理状态**：组件状态留在组件附近；跨功能共享或持久化时再使用 Context 或状态库；服务端缓存单独处理。
4. **保持边界清晰**：页面负责组装，组件负责展示和交互，Hooks 负责可复用行为，服务层负责外部数据访问。
5. **先验证再抽象**：重复出现且边界稳定后再提取通用组件或工具，不为潜在复用提前建层。

## 推荐目录形状

目录仅作为示例，按项目框架和规模调整：

```text
src/
├── app/                    # 应用入口、布局、路由（如项目采用）
├── components/             # 跨功能复用的组件
│   └── ui/                 # 项目 UI 组件或组件库封装
├── features/               # 按业务功能组织
│   └── users/
│       ├── api/
│       ├── components/
│       ├── hooks/
│       ├── pages/
│       ├── types/
│       └── index.ts
├── lib/                    # 无业务含义的基础工具
└── test/                   # 全局测试工具（如项目采用）
```

## 何时拆分

- 页面同时负责请求、状态、表单和大量展示时，先按职责拆分；
- 组件只在一个功能中使用时，优先留在该功能目录；
- 跨功能共享前，确认 API、样式和状态语义确实稳定；
- 抽象后必须保留清晰的类型边界和测试入口。

## 详细参考

- [`references/architecture-patterns.md`](references/architecture-patterns.md)：完整架构、组件分层和评审示例；
- [`development-workflow.md`](development-workflow.md)：需求、实现、测试和审查流程；
- [`references/performance-and-testing.md`](references/performance-and-testing.md)：性能、测试和常见陷阱。

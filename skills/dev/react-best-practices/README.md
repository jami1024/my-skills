# React 最佳实践 Skill

面向新建和现有 React 项目的工程实践，帮助建立清晰、可测试、可维护的前端代码结构。

## 定位

本 Skill 负责：

- React 项目架构和目录边界；
- 组件、Hooks、页面和服务层的职责划分；
- 状态管理、数据获取、表单和路由决策；
- 性能、可访问性、测试和交付验证。

本 Skill 不提供固定脚手架、不创作视觉风格，也不强制迁移已有技术栈。

## 适用场景

```text
“为这个产品推荐 React 技术栈和项目架构”
“为一个需要 SSR 的 React 产品设计目录和数据流”
“审查这个 React 页面组件的状态和数据边界”
“优化这个 React 列表的性能并补充测试”
“在已有 shadcn/ui 项目中添加一个表单”
```

## 使用流程

### 新项目

1. 确认产品类型、部署目标、SPA/SSR 需求和团队约束；
2. 比较 Vite、Next.js 或其他方案，并说明取舍；
3. 设计路由、数据获取、状态、UI 和测试方案；
4. 输出目录结构和架构决策；
5. 用户确认后，使用目标框架的官方工具初始化。

### 现有项目

先读取并总结：

- `package.json`、lockfile 和现有 scripts；
- `tsconfig.json`、框架配置和环境变量约定；
- 路由、API 层、组件库、样式入口和状态层；
- 测试、lint、typecheck、build 配置；
- `components.json`（如存在）。

先复用项目已有方案，再提出新增依赖或迁移建议。

## 技术选择原则

| 领域 | 判断原则 |
|---|---|
| 框架与构建 | 根据渲染需求、部署环境和团队约束选择；不默认迁移 |
| 路由 | 遵循框架或项目已有路由方案 |
| 服务端数据 | 根据缓存、失效、重试和预取需求选择数据层 |
| 客户端状态 | 优先就近管理，跨功能共享时再使用 Context 或状态库 |
| 表单 | 简单表单少依赖，复杂表单再使用项目已有表单库 |
| UI 与样式 | 复用设计系统、组件库和现有 CSS 方案 |
| 测试 | 复用项目已有测试工具，覆盖核心用户路径 |

示例中的 Tailwind、React Router、TanStack Query、Zustand、React Hook Form 和 shadcn/ui 都是可选方案，不应因为示例而新增依赖。

## 推荐目录形状

按项目规模和框架调整，不要求机械套用：

```text
src/
├── app/                    # 入口、布局、路由（如项目采用）
├── components/             # 跨功能复用组件
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

只在跨功能复用且语义稳定时，才把代码提升到全局目录。

## 实现检查点

### 组件与状态

- Props 使用明确的 TypeScript 类型；
- 页面负责组装，组件负责展示和交互，Hooks 负责可复用行为；
- 状态尽量就近管理，避免无必要的全局状态；
- 覆盖 loading、error、empty、disabled 和成功状态；
- 列表使用稳定且唯一的 `key`。

### 数据与表单

- 请求层集中处理认证、序列化、错误映射和取消请求；
- 页面不要重复实现同一套请求和缓存逻辑；
- 表单 schema、默认值、提交数据和错误展示保持一致；
- 提交期间防止重复操作，并展示服务端校验错误。

### UI 与可访问性

- 使用语义 HTML、label、alt、可见焦点和正确的按钮/链接元素；
- 颜色不是唯一状态提示；
- 响应式布局不产生横向滚动；
- 动效尊重 `prefers-reduced-motion`；
- 遵循项目已有的设计 token 和组件 API。

### 性能

先测量再优化：

- 网络：避免串行请求，复用缓存，按需预取；
- Bundle：延迟加载非关键路由和大型依赖；
- 渲染：减少不必要订阅，不无依据地使用 `memo`；
- 长列表：按需分页或虚拟化；
- 图片和第三方脚本：明确尺寸、优先级和卸载策略。

## 交付验证

按项目已有命令执行：

```text
typecheck → lint → unit/integration test → build → E2E/a11y（如已配置）
```

交付前确认：

- 主成功路径和关键失败路径均可运行；
- 路由、权限、网络失败和重复提交行为明确；
- 没有凭据或服务端密钥进入客户端 Bundle；
- 没有未使用依赖、重复请求或无依据的性能优化；
- 变更说明了受影响的配置、测试和用户流程。

## 相关文件

- [`SKILL.md`](SKILL.md)：核心规则和验证清单；
- [`development-workflow.md`](development-workflow.md)：开发流程；
- [`architecture-design.md`](architecture-design.md)：架构决策索引；
- [`references/architecture-patterns.md`](references/architecture-patterns.md)：详细架构参考；
- [`references/performance-and-testing.md`](references/performance-and-testing.md)：性能和测试参考；
- [`templates/`](templates/)：需求、设计、组件和审查模板；
- [`evals/`](evals/)：行为回归用例。

## 许可证

MIT

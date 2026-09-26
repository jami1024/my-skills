---
name: react-best-practices
description: 为 React/TypeScript 前端提供创建、维护、重构和审查指导；当请求涉及 React 组件、Hooks、状态管理、数据获取、路由、可访问性、前端测试或性能时使用。不用于纯视觉创作、后端实现或没有 React 约束的通用 JavaScript 问题。
---

# React 工程最佳实践

面向新建和现有 React 项目的工程指导，重点是可维护的组件边界、清晰的数据流、可测试性和可验证的交付结果。

> 文中的 Tailwind、React Router、TanStack Query、Zustand、React Hook Form 和 shadcn/ui 仅是示例。先读取项目依赖和配置，再复用已有方案；不要因为示例而新增依赖。

## 何时使用

- 为新项目推荐 React 技术栈、目录结构和架构边界；
- 创建或重构 React 组件、页面、Hooks 和功能模块；
- 设计前端目录、状态边界、数据获取或路由边界；
- 处理表单、加载状态、错误状态、空状态和错误恢复；
- 审查 React 代码的可维护性、性能、测试和可访问性。

不负责视觉风格创作、固定脚手架或强制迁移技术栈。新项目会先输出架构决策和目录建议，再由用户确认后使用目标框架的官方工具初始化；现有项目优先遵循已有约定。

## 项目勘察

开始修改前，先读取并总结。新项目还没有配置文件时，先确认产品类型、部署目标、SPA/SSR 需求、路由、数据来源、认证、团队约束和测试要求。

1. `package.json` 和锁文件：包管理器、React 版本、已有依赖和 scripts；
2. `tsconfig.json` 及框架配置：别名、严格度、构建和环境约定；
3. 路由入口、组件库、样式入口、状态层和测试目录；
4. `components.json`（如存在）：shadcn/ui 的项目配置；
5. 现有 lint、typecheck、test、build 命令。

先复用项目已有方案，再提出新增依赖或迁移建议。若项目使用 Next.js、Remix 或其他框架，遵循其路由、数据获取和渲染约定。

## 核心原则

1. **按功能组织**：优先把同一功能的 API、组件、Hooks、类型和页面放在一起。
2. **边界清晰**：页面负责组装，组件负责展示和交互，Hooks 负责可复用行为，服务层负责外部数据访问。
3. **状态就近**：组件状态留在组件附近；跨功能共享或持久化时再使用 Context 或状态库。
4. **服务端状态单独处理**：根据缓存、失效、重试和预取需求选择框架能力或数据请求库。
5. **组合优先**：优先使用 Props、children 和组合，避免为了消除少量重复而引入全局状态。
6. **先测量再优化**：只对已确认的渲染、网络或 Bundle 瓶颈做优化。
7. **遵循现有约定**：不在同一项目中无理由混用多套路由、样式、表单或状态方案。

## 推荐目录形状

目录仅作为示例，按项目框架和规模调整：

```text
src/
├── app/                    # 入口、布局、路由（如项目采用）
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

只有在跨功能复用且语义稳定时，才把代码提升到 `components/`、`hooks/`、`lib/` 或全局状态目录。

## 组件实践

- Props 使用明确的 TypeScript 类型，事件回调命名表达动作；
- 组件只接收它真正需要的数据，避免把整个服务端响应向下传递；
- 复杂页面拆成容器、展示组件和可复用行为，但不要按固定行数机械拆分；
- 列表使用稳定且唯一的 `key`，不要使用会变化的数组索引；
- 交互元素使用语义 HTML，键盘操作和焦点状态必须可用；
- 组件需要覆盖 loading、error、empty、disabled 和成功状态。

```tsx
interface UserCardProps {
  user: User
  onEdit?: (user: User) => void
}

export function UserCard({ user, onEdit }: UserCardProps) {
  return (
    <article>
      <h2>{user.name}</h2>
      <p>{user.email}</p>
      {onEdit && <button onClick={() => onEdit(user)}>编辑</button>}
    </article>
  )
}
```

## 状态与数据获取

按以下顺序判断：

1. 只影响当前组件的值 → `useState` 或 `useReducer`；
2. 多个近邻组件共享 → 组件组合、提升状态或 Context；
3. 跨功能共享或需要持久化 → 使用项目已有状态库；
4. 来自服务器且需要缓存、失效或并发处理 → 使用项目已有数据层或合适的数据请求库。

请求层应集中处理认证、序列化、错误映射和取消请求。页面负责展示状态，不要在多个组件中复制同一套请求和缓存逻辑。

## 表单

- 简单表单可使用受控组件和原生校验；
- 复杂、动态或多步骤表单才引入项目已有表单库；
- 将字段 schema、默认值、提交数据和错误展示保持一致；
- 提交过程中禁用重复操作，并明确成功、失败和服务端校验错误。

## 路由

遵循项目已有的路由方案。以下示例仅说明边界，不要求引入 React Router：

- 路由参数和查询参数在边界处解析并校验；
- 页面级数据加载和权限判断放在框架推荐的位置；
- 受保护页面处理未登录、无权限和返回地址；
- 404、加载中和错误页面属于路由体验的一部分。

## 样式与可访问性

- 遵循项目已有 CSS、Tailwind、CSS Modules 或 CSS-in-JS 约定；
- 复用设计 token 和组件库，不在局部重新定义颜色、间距和交互规则；
- 使用语义 HTML、label、alt、可见焦点和正确的按钮/链接元素；
- 颜色不是唯一状态提示，文字和图标也要表达状态；
- 尊重 `prefers-reduced-motion`，避免动效阻塞主要流程；
- 在目标视口检查响应式布局和横向滚动。

## 性能

先确认问题来源，再选择措施：

- 网络：避免串行请求，复用缓存，按需预取；
- Bundle：延迟加载非关键路由和大型依赖；
- 渲染：减少不必要订阅，稳定列表 key，避免无依据地使用 `memo`；
- 长列表：分页或虚拟化，并先用性能工具确认瓶颈；
- 图片和第三方脚本：明确尺寸、加载优先级和卸载策略。

更详细的性能规则见 [`references/performance-and-testing.md`](references/performance-and-testing.md)。

## 验证清单

交付前至少运行项目已有的：

- `typecheck` 或等价的 TypeScript 检查；
- `lint` 和格式化检查；
- 核心组件、Hooks 或业务流程测试；
- `build` 或框架对应的生产构建；
- 关键流程的浏览器测试和可访问性检查（项目已配置时）。

同时确认：

- 没有凭据、令牌或服务端密钥进入客户端 Bundle；
- loading、error、empty、权限和网络失败状态可恢复；
- 没有引入未使用的依赖、重复请求或无依据的性能优化；
- 变更说明了受影响的路由、状态、测试和配置。

## 相关参考

- [`development-workflow.md`](development-workflow.md)：需求、实现、测试和审查流程；
- [`architecture-design.md`](architecture-design.md)：架构决策索引；
- [`references/architecture-patterns.md`](references/architecture-patterns.md)：完整架构示例；
- [`references/performance-and-testing.md`](references/performance-and-testing.md)：性能、测试和常见陷阱。

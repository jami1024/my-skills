# 性能与测试参考

本文件承接 `react-best-practices/SKILL.md` 的性能优化、测试、常见陷阱和参考资源。

## 性能优化

### 1. memo / useMemo / useCallback

```tsx
// ✅ memo 优化列表项（避免父组件重渲染导致子组件重渲染）
export const UserCard = React.memo(({ user, onEdit }: UserCardProps) => {
  return <Card>{/* ... */}</Card>
})

function UserList({ users }: UserListProps) {
  // ✅ useMemo 缓存计算结果
  const sortedUsers = useMemo(
    () => [...users].sort((a, b) => a.name.localeCompare(b.name)),
    [users]
  )

  // ✅ useCallback 缓存回调（配合 memo 子组件使用才有意义）
  const handleUserClick = useCallback((user: User) => {
    console.log(user)
  }, [])

  return sortedUsers.map(user => (
    <UserCard key={user.id} user={user} onClick={handleUserClick} />
  ))
}
```

### 2. 代码分割

```tsx
// ✅ React.lazy 懒加载页面级组件
const UserDetailPage = React.lazy(() => import('./pages/user-detail-page'))

// 路由中配合 Suspense
{ path: ':id', element: <Suspense fallback={<Loading />}><UserDetailPage /></Suspense> }
```

### 3. 虚拟滚动（大列表）

```tsx
// ✅ 使用 @tanstack/react-virtual 处理长列表
import { useVirtualizer } from '@tanstack/react-virtual'

const virtualizer = useVirtualizer({
  count: users.length,
  getScrollElement: () => parentRef.current,
  estimateSize: () => 80,
})

// 只渲染可见区域的 virtualizer.getVirtualItems()
```

---

## 测试策略

### Vitest + React Testing Library

```tsx
// src/features/users/components/user-card.test.tsx
import { render, screen, fireEvent } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import { UserCard } from './user-card'

const mockUser = {
  id: '1', name: 'John Doe', email: 'john@example.com',
  role: 'user' as const, createdAt: '2024-01-01', updatedAt: '2024-01-01',
}

describe('UserCard', () => {
  it('renders user information', () => {
    render(<UserCard user={mockUser} />)
    expect(screen.getByText('John Doe')).toBeInTheDocument()
    expect(screen.getByText('john@example.com')).toBeInTheDocument()
  })

  it('calls onEdit when edit button is clicked', () => {
    const onEdit = vi.fn()
    render(<UserCard user={mockUser} onEdit={onEdit} />)
    fireEvent.click(screen.getByText('编辑'))
    expect(onEdit).toHaveBeenCalledWith(mockUser)
  })

  // ✅ 同理测试 onDelete 回调
})
```

---

## 常见陷阱及避免方法

| 陷阱 | 正确做法 |
|------|----------|
| ❌ 在循环中定义函数/Hooks | ✅ 使用 useCallback，Hooks 只在顶层调用 |
| ❌ 深层 Props 传递且组件边界不清晰 | ✅ 优先使用组件组合、提升状态或 Context；跨功能共享时再选择状态库 |
| ❌ 用组件状态承担复杂服务端缓存 | ✅ 根据缓存、失效、重试和预取需求选择框架方案或数据请求库 |
| ❌ 所有组件都用 memo | ✅ 先测量性能，只优化瓶颈组件 |
| ❌ 巨型组件（200+ 行） | ✅ 拆分为多个小组件，每个专注一件事 |
| ❌ 在同一项目中混用多套样式体系 | ✅ 遵循项目已有的 CSS、Tailwind 或 CSS-in-JS 约定 |
| ❌ 列表渲染不加 key | ✅ 使用唯一且稳定的 key（如 id） |
| ❌ 直接修改状态 | ✅ 不可变更新（展开运算符或 immer） |

## 参考资源

- [React 官方文档](https://react.dev/)
- [shadcn/ui 文档](https://ui.shadcn.com/)
- [TanStack Query 文档](https://tanstack.com/query)
- [React Hook Form 文档](https://react-hook-form.com/)
- [Tailwind CSS 文档](https://tailwindcss.com/)

---

**详细参考：**
- 完整开发工作规范 → [development-workflow.md](../development-workflow.md)
- 架构设计和组件模式 → [architecture-design.md](../architecture-design.md)
- 项目初始化 → 使用目标框架的官方初始化工具

**实现顺序：** Types → API → Hooks → Components → Pages → Test

**完成标准：**
- [ ] 功能实现且测试通过
- [ ] TypeScript 无类型错误
- [ ] 有适当的 Loading 和 Error 状态处理
- [ ] 通过 lint 检查
- [ ] 关键组件有测试覆盖

---

**使用此 skill 时，Claude 将：**
- 遵循 Feature-Based 架构组织代码
- 根据服务端缓存复杂度选择框架方案或数据请求库
- 根据表单复杂度和项目现有依赖选择表单校验方案
- 遵循项目已有的 UI 组件库和样式系统
- TypeScript 全链路类型安全
- 按推荐顺序实现：Types → API → Hooks → Components → Pages → Test
- 合理使用 memo/useMemo/useCallback 优化性能
- 编写 Vitest + React Testing Library 测试
- 遵循 React 社区最佳实践

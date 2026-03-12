---
name: react-best-practices
description: 当用户需要创建 React 项目、构建前端应用、组织 React 代码结构时使用。触发词：React、前端项目、React 架构、shadcn/ui、前端开发
---

# React + shadcn/ui 最佳实践指南

本文档是 React + shadcn/ui 开发的核心实践指南，专注于架构、状态管理、性能和测试。

## 📋 开发工作流

通用开发流程（需求分析、技术设计、代码审查等）请参考 **development-workflow skill**。
UI 设计和视觉实现（字体、配色、布局、动效）请配合 **frontend-design skill**。

本文档专注于 **React 特定** 的开发实践。

## 核心原则

1. **Feature-Based 架构** - 按功能模块组织代码，而非技术层
2. **类型安全** - TypeScript 全链路类型覆盖
3. **状态分离** - 服务端状态（TanStack Query）与客户端状态（Zustand）分离
4. **组件化优先** - 小而专注的组件，Props 驱动

## 项目结构

> 完整初始化命令和配置文件见 `init-project.sh`

```
src/
├── api/                      # API 客户端（Axios 配置 + 通用类型）
├── components/              # 全局组件
│   ├── ui/                 # shadcn/ui 组件
│   ├── layout/             # 布局组件（header/sidebar/footer）
│   └── common/             # 通用组件（loading/error-fallback）
├── features/               # 功能模块（核心）
│   └── users/              # 示例模块
│       ├── api/            # 模块 API
│       ├── components/     # 模块组件
│       ├── hooks/          # 模块 Hooks
│       ├── types/          # 模块类型
│       └── pages/          # 模块页面
├── hooks/                  # 全局 Hooks
├── lib/                    # 工具库（cn 等）
├── stores/                 # 全局状态（Zustand）
├── types/                  # 全局类型
├── App.tsx
├── main.tsx
└── router.tsx
```

## 组件开发

### 组件模板

```tsx
// src/features/users/components/user-card.tsx
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { User } from "../types/user"

interface UserCardProps {
  user: User
  onEdit?: (user: User) => void
  onDelete?: (id: string) => void
}

export function UserCard({ user, onEdit, onDelete }: UserCardProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>{user.name}</CardTitle>
      </CardHeader>
      <CardContent>
        <p className="text-sm text-muted-foreground">{user.email}</p>
        <div className="mt-4 flex gap-2">
          <Button onClick={() => onEdit?.(user)} variant="outline" size="sm">编辑</Button>
          <Button onClick={() => onDelete?.(user.id)} variant="destructive" size="sm">删除</Button>
        </div>
      </CardContent>
    </Card>
  )
}
```

### 组件规范

```tsx
// ✅ 命名：组件 PascalCase，Hooks use 前缀，回调 on 前缀
export function UserList() {}
export function useUserQuery() {}
interface Props { onUserClick?: (user: User) => void }

// ✅ Props 用 interface 定义，可选属性用 ?
interface UserListProps {
  users: User[]
  loading?: boolean
  onUserClick?: (user: User) => void
}

// ✅ 拆分大组件为多个小组件
function UserPage() {
  return (
    <div>
      <UserHeader />
      <UserFilters />
      <UserList />
      <UserPagination />
    </div>
  )
}
```

---

## 状态管理

### TanStack Query（服务端状态）

```tsx
// src/main.tsx — 配置
const queryClient = new QueryClient({
  defaultOptions: {
    queries: { staleTime: 5 * 60 * 1000, retry: 3 },
  },
})

// src/features/users/hooks/use-users.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'

// ✅ useQuery 用于读取数据
export function useUsers() {
  return useQuery({
    queryKey: ['users'],
    queryFn: userApi.getAll,
  })
}

export function useUser(id: string) {
  return useQuery({
    queryKey: ['users', id],
    queryFn: () => userApi.getById(id),
    enabled: !!id,  // 条件查询
  })
}

// ✅ useMutation 用于写操作，成功后 invalidate 缓存
export function useCreateUser() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: userApi.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] })
    },
  })
}

// ✅ 同理实现 useUpdateUser、useDeleteUser，模式相同
```

### Zustand（客户端状态）

```tsx
// src/stores/auth-store.ts
import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface AuthState {
  user: User | null
  token: string | null
  login: (user: User, token: string) => void
  logout: () => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      token: null,
      login: (user, token) => set({ user, token }),
      logout: () => set({ user: null, token: null }),
    }),
    { name: 'auth-storage' }
  )
)
```

---

## 数据获取

### API 客户端

```tsx
// src/api/client.ts
import axios from 'axios'
import { useAuthStore } from '@/stores/auth-store'

export const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:3000/api',
  timeout: 10000,
})

// 请求拦截器 — 自动附加 token
apiClient.interceptors.request.use((config) => {
  const token = useAuthStore.getState().token
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// 响应拦截器 — 401 自动登出
apiClient.interceptors.response.use(
  (response) => response.data,
  (error) => {
    if (error.response?.status === 401) {
      useAuthStore.getState().logout()
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)
```

### API 服务层 + 类型定义

```tsx
// src/features/users/types/user.ts
export interface User {
  id: string
  name: string
  email: string
  role: 'admin' | 'user'
  createdAt: string
  updatedAt: string
}

export interface CreateUserDto {
  name: string
  email: string
  password: string
  role?: 'admin' | 'user'
}

// ✅ 同理定义 UpdateUserDto（Partial 模式）

// src/features/users/api/user-api.ts
export const userApi = {
  getAll: async (): Promise<User[]> => apiClient.get('/users'),
  getById: async (id: string): Promise<User> => apiClient.get(`/users/${id}`),
  create: async (data: CreateUserDto): Promise<User> => apiClient.post('/users', data),
  update: async (id: string, data: Partial<User>): Promise<User> => apiClient.put(`/users/${id}`, data),
  delete: async (id: string): Promise<void> => apiClient.delete(`/users/${id}`),
}
```

---

## 表单处理

### React Hook Form + Zod

```tsx
// src/features/users/components/user-form.tsx
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import * as z from "zod"
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form"

const formSchema = z.object({
  name: z.string().min(2, "名称至少 2 个字符").max(50),
  email: z.string().email("邮箱格式不正确"),
  password: z.string().min(8, "密码至少 8 个字符"),
})

type FormValues = z.infer<typeof formSchema>

interface UserFormProps {
  onSubmit: (values: FormValues) => void
  defaultValues?: Partial<FormValues>
  loading?: boolean
}

export function UserForm({ onSubmit, defaultValues, loading }: UserFormProps) {
  const form = useForm<FormValues>({
    resolver: zodResolver(formSchema),
    defaultValues: { name: "", email: "", password: "", ...defaultValues },
  })

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
        {/* ✅ 每个字段用 FormField 包裹，模式相同 */}
        <FormField
          control={form.control}
          name="name"
          render={({ field }) => (
            <FormItem>
              <FormLabel>姓名</FormLabel>
              <FormControl>
                <Input placeholder="请输入姓名" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        {/* ✅ email、password 字段同理，只改 name/label/placeholder */}

        <Button type="submit" disabled={loading}>
          {loading ? "提交中..." : "提交"}
        </Button>
      </form>
    </Form>
  )
}
```

### 表单使用

```tsx
// src/features/users/pages/create-user-page.tsx
export function CreateUserPage() {
  const navigate = useNavigate()
  const { toast } = useToast()
  const { mutate: createUser, isPending } = useCreateUser()

  const handleSubmit = (values: FormValues) => {
    createUser(values, {
      onSuccess: () => {
        toast({ title: "成功", description: "用户创建成功" })
        navigate("/users")
      },
      onError: (error) => {
        toast({ variant: "destructive", title: "错误", description: error.message })
      },
    })
  }

  return (
    <div className="container mx-auto py-8">
      <h1 className="text-2xl font-bold mb-6">创建用户</h1>
      <UserForm onSubmit={handleSubmit} loading={isPending} />
    </div>
  )
}
```

---

## 路由管理

### React Router v6

```tsx
// src/router.tsx
import { createBrowserRouter, Navigate } from 'react-router-dom'
import { Layout } from './components/layout/layout'
import { UserListPage } from './features/users/pages/user-list-page'
import { UserDetailPage } from './features/users/pages/user-detail-page'
import { CreateUserPage } from './features/users/pages/create-user-page'
import { LoginPage } from './features/auth/pages/login-page'
import { ProtectedRoute } from './components/common/protected-route'

export const router = createBrowserRouter([
  {
    path: '/login',
    element: <LoginPage />,
  },
  {
    path: '/',
    element: (
      <ProtectedRoute>
        <Layout />
      </ProtectedRoute>
    ),
    children: [
      {
        index: true,
        element: <Navigate to="/users" replace />,
      },
      {
        path: 'users',
        children: [
          { index: true, element: <UserListPage /> },
          { path: 'new', element: <CreateUserPage /> },
          { path: ':id', element: <UserDetailPage /> },
        ],
      },
    ],
  },
])
```

### 路由守卫

```tsx
// src/components/common/protected-route.tsx
import { Navigate, useLocation } from 'react-router-dom'
import { useAuthStore } from '@/stores/auth-store'

interface ProtectedRouteProps {
  children: React.ReactNode
}

export function ProtectedRoute({ children }: ProtectedRouteProps) {
  const { token } = useAuthStore()
  const location = useLocation()

  if (!token) {
    return <Navigate to="/login" state={{ from: location }} replace />
  }

  return <>{children}</>
}
```

---

## 样式规范

```tsx
// src/lib/utils.ts — cn 工具函数
import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

// ✅ 使用 cn 组合条件样式
<Button className={cn("bg-primary", isActive && "bg-primary-dark", disabled && "opacity-50")} />

// ✅ 过长的 className 用 cn 拆分
const cardClass = cn(
  "flex items-center justify-between p-4",
  "bg-white rounded-lg shadow-md",
  "hover:shadow-lg transition-shadow"
)
```

---

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
| ❌ Props 钻取超过 3 层 | ✅ 使用 Context 或 Zustand |
| ❌ 服务端状态用 useState 管理 | ✅ 使用 TanStack Query（自动缓存、重试、失效） |
| ❌ 所有组件都用 memo | ✅ 先测量性能，只优化瓶颈组件 |
| ❌ 巨型组件（200+ 行） | ✅ 拆分为多个小组件，每个专注一件事 |
| ❌ 内联样式或 CSS-in-JS | ✅ 使用 Tailwind CSS + cn 工具 |
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
- 完整开发工作规范 → [development-workflow.md](development-workflow.md)
- 架构设计和组件模式 → [architecture-design.md](architecture-design.md)
- 一键初始化项目 → `init-project.sh`

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
- 使用 TanStack Query 管理服务端状态，Zustand 管理客户端状态
- 使用 React Hook Form + Zod 处理表单验证
- 使用 shadcn/ui 组件库 + Tailwind CSS
- TypeScript 全链路类型安全
- 按推荐顺序实现：Types → API → Hooks → Components → Pages → Test
- 合理使用 memo/useMemo/useCallback 优化性能
- 编写 Vitest + React Testing Library 测试
- 遵循 React 社区最佳实践

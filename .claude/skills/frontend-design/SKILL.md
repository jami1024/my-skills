---
name: frontend-design
description: 创建独特、生产级的前端界面，避免通用 AI 美学。用于设计网站、落地页、仪表板、React 组件等 UI 界面。触发词：UI 设计、前端设计、界面美化、落地页、landing page
---

# Frontend Design 前端设计最佳实践

创建独特、生产级的前端界面，避免通用 AI 美学。适用于 Web 组件、页面、落地页、仪表板等任何需要设计的 UI。

React 工程实践（架构、状态管理、性能、测试）请配合 **react-best-practices skill**。

## 🎨 设计思维

在编码之前，理解上下文并确定**大胆的美学方向**：

### 1. 核心问题
- **目的**: 这个界面解决什么问题？谁在使用它？
- **基调**: 选择一个极端风格
- **约束**: 技术要求（框架、性能、可访问性）
- **差异化**: 什么让它令人难忘？

### 2. 美学方向选择

| 风格 | 描述 | 适用场景 |
|------|------|----------|
| 极简主义 | 大量留白、精确排版 | 高端品牌、艺术画廊 |
| 最大化主义 | 丰富层次、密集信息 | 创意机构、娱乐平台 |
| 复古未来 | 80s 氛围、霓虹色彩 | 游戏、音乐、科技 |
| 有机自然 | 柔和曲线、自然色调 | 健康、环保、生活方式 |
| 奢华精致 | 金色调、衬线字体 | 奢侈品、高端服务 |
| 俏皮玩趣 | 圆角、明亮色彩、动画 | 儿童产品、创意工具 |
| 编辑杂志 | 网格布局、大字体 | 媒体、出版、博客 |
| 野蛮主义 | 原始、不对称、粗犷 | 实验性项目、艺术 |
| 装饰艺术 | 几何图案、对称 | 活动、展览、复古品牌 |
| 柔和粉彩 | 渐变、柔和边缘 | 美妆、时尚、生活 |
| 工业实用 | 功能优先、单色 | 工具、开发者产品 |
| 玻璃拟态 | 毛玻璃效果、透明层次 | 现代 SaaS、金融仪表板 |
| 新拟态 | 柔和 3D、浮雕效果 | 健康应用、冥想平台 |
| 粘土拟态 | 3D 软糖质感、圆润 | 教育应用、儿童产品 |
| Bento Grid | 模块化卡片、Apple 风格 | 仪表板、产品展示 |
| 新野蛮主义 | 粗边框、45° 阴影 | Gen Z 品牌、创意机构 |
| 赛博朋克 | 霓虹、终端、HUD | 游戏、加密、开发者工具 |

**关键**: 选择清晰的概念方向并精确执行。大胆的最大化主义和精致的极简主义都有效 - 关键是**意图性**，而非强度。

---

## 🔍 设计数据库搜索

通过 `search.py` 查询内置设计数据库，获取字体、配色、风格等推荐。

```bash
python3 .claude/skills/frontend-design/scripts/search.py "<关键词>" --domain <领域> [-n <结果数量>]
```

### 可用领域

| 领域 | 用途 | 示例关键词 |
|------|------|-----------|
| `style` | UI 风格、效果 | glassmorphism, minimalism, brutalism |
| `typography` | 字体配对、Google Fonts | elegant, playful, professional |
| `color` | 按行业的配色方案 | saas, ecommerce, healthcare, fintech |
| `product` | 产品类型推荐 | SaaS, e-commerce, portfolio |
| `landing` | 落地页结构、CTA 策略 | hero, testimonial, pricing |
| `chart` | 图表类型推荐 | trend, comparison, funnel |
| `ux` | 最佳实践、反模式 | animation, accessibility, loading |

技术栈搜索：`--stack react|nextjs|vue|svelte|html-tailwind|swiftui|flutter` 等

### 推荐搜索顺序

Product → Style → Typography → Color → Landing（如适用）→ UX → Stack

---

## 🎨 美学指南

### 1. 字体配对（快速参考）

> 完整字体库通过 `search.py --domain typography` 查询

| 风格 | 标题字体 | 正文字体 | 适用场景 |
|------|---------|---------|----------|
| 高端奢华 | Playfair Display | Libre Baskerville | 奢侈品、时尚杂志 |
| 现代科技 | Plus Jakarta Sans | Plus Jakarta Sans | SaaS、科技创业 |
| 开发者 | JetBrains Mono | IBM Plex Sans | 开发者工具、技术文档 |
| 创意冲击 | Bebas Neue | Source Sans 3 | 活动、营销页面 |
| 时尚前卫 | Syne | Manrope | 创意机构、设计工作室 |
| 友好亲和 | Fredoka | Nunito | 儿童产品、教育 |
| 健康养生 | Lora | Raleway | 健康、生活方式 |

**❌ 避免**: Inter、Roboto、Arial、系统字体（太通用，典型 AI 美学）

### 2. 行业配色方案（快速参考）

> 完整行业配色通过 `search.py --domain color` 查询

```css
/* SaaS / 科技 — 专业蓝 */
:root {
  --color-primary: #0066FF;
  --color-secondary: #1A1A2E;
  --color-accent: #00D4FF;
  --color-surface: #FAFBFC;
  --color-text: #1F2937;
}

/* 美容 / SPA — 优雅柔和 */
:root {
  --color-primary: #D4A574;
  --color-secondary: #2D2D2D;
  --color-accent: #E8C5A8;
  --color-surface: #FDF8F4;
  --color-text: #3D3D3D;
}
```

**❌ 避免**: 紫色渐变 + 白色背景（典型 AI 美学）、平均分布无主次的调色板

### 3. 动效与交互

#### ✅ 高影响力动效
```css
/* 页面加载 - 交错显示 */
.fade-in-up {
  opacity: 0;
  transform: translateY(20px);
  animation: fadeInUp 0.6s ease forwards;
}

.fade-in-up:nth-child(1) { animation-delay: 0.1s; }
.fade-in-up:nth-child(2) { animation-delay: 0.2s; }
.fade-in-up:nth-child(3) { animation-delay: 0.3s; }

@keyframes fadeInUp {
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 悬停效果 - 出人意料 */
.card {
  transition: transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.card:hover {
  transform: translateY(-8px) rotate(1deg);
}
```

#### React 动效 (Motion)
```tsx
import { motion } from "framer-motion"

const containerVariants = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: { staggerChildren: 0.1 }
  }
}

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  show: { opacity: 1, y: 0 }
}

function AnimatedList({ items }) {
  return (
    <motion.ul variants={containerVariants} initial="hidden" animate="show">
      {items.map((item) => (
        <motion.li key={item.id} variants={itemVariants}>
          {item.name}
        </motion.li>
      ))}
    </motion.ul>
  )
}
```

### 4. 空间构图

```css
/* 不对称网格 */
.asymmetric-grid {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 2rem;
}

/* 对角线流动 */
.diagonal-section {
  clip-path: polygon(0 0, 100% 5%, 100% 95%, 0 100%);
  padding: 8rem 0;
}

/* 重叠元素 */
.overlap-image {
  position: absolute;
  top: -2rem;
  right: -2rem;
  z-index: 10;
}
```

### 5. 背景与视觉细节

```css
/* 渐变网格 */
.gradient-mesh {
  background:
    radial-gradient(at 40% 20%, hsla(28,100%,74%,1) 0px, transparent 50%),
    radial-gradient(at 80% 0%, hsla(189,100%,56%,1) 0px, transparent 50%),
    radial-gradient(at 0% 50%, hsla(355,100%,93%,1) 0px, transparent 50%);
}

/* 噪点纹理 */
.noise-texture::before {
  content: "";
  position: absolute;
  inset: 0;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 400 400' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)'/%3E%3C/svg%3E");
  opacity: 0.05;
  pointer-events: none;
}
```

---

## 🚫 专业 UI 常见规则

### 图标与视觉元素

| 规则 | ✅ 正确做法 | ❌ 避免做法 |
|------|------------|-----------|
| 不用 emoji 图标 | 使用 SVG 图标 (Heroicons, Lucide, Simple Icons) | 使用 emoji 如 🎨 🚀 ⚙️ 作为 UI 图标 |
| 稳定的 hover 状态 | 使用颜色/透明度过渡 | 使用 scale 变换导致布局偏移 |
| 正确的品牌 Logo | 从 Simple Icons 获取官方 SVG | 猜测或使用错误的 logo 路径 |
| 一致的图标尺寸 | 使用固定 viewBox (24x24) + w-6 h-6 | 随意混用不同尺寸图标 |

### 交互与光标

| 规则 | ✅ 正确做法 | ❌ 避免做法 |
|------|------------|-----------|
| cursor-pointer | 所有可点击/悬停卡片添加 `cursor-pointer` | 交互元素保持默认光标 |
| hover 反馈 | 提供视觉反馈（颜色、阴影、边框变化） | 无任何交互指示 |
| 平滑过渡 | 使用 `transition-colors duration-200` | 瞬间状态变化或过慢 (>500ms) |

### 明暗模式对比度

| 规则 | ✅ 正确做法 | ❌ 避免做法 |
|------|------------|-----------|
| 浅色模式玻璃卡片 | 使用 `bg-white/80` 或更高不透明度 | 使用 `bg-white/10`（太透明） |
| 浅色模式文字对比 | 使用 `#0F172A` (slate-900) 作为正文 | 使用 `#94A3B8` (slate-400) 作为正文 |
| 次要文字 | 最低使用 `#475569` (slate-600) | 使用 gray-400 或更浅 |
| 边框可见性 | 浅色模式用 `border-gray-200` | 使用 `border-white/10`（不可见） |

### 布局与间距

| 规则 | ✅ 正确做法 | ❌ 避免做法 |
|------|------------|-----------|
| 悬浮导航栏 | 添加 `top-4 left-4 right-4` 间距 | 导航栏紧贴 `top-0 left-0 right-0` |
| 内容内边距 | 考虑固定导航栏高度 | 内容隐藏在固定元素后面 |
| 一致的最大宽度 | 统一使用 `max-w-6xl` 或 `max-w-7xl` | 混用不同容器宽度 |

---

## ✅ 交付前检查清单

### 视觉质量
- [ ] 没有使用 emoji 作为图标（改用 SVG）
- [ ] 所有图标来自一致的图标集 (Heroicons/Lucide)
- [ ] 品牌 logo 正确（从 Simple Icons 验证）
- [ ] hover 状态不会导致布局偏移
- [ ] 直接使用主题颜色 (bg-primary) 而非 var() 包装

### 交互体验
- [ ] 所有可点击元素都有 `cursor-pointer`
- [ ] hover 状态提供清晰的视觉反馈
- [ ] 过渡效果流畅 (150-300ms)
- [ ] 键盘导航时焦点状态可见

### 明暗模式
- [ ] 浅色模式文字有足够对比度（最低 4.5:1）
- [ ] 玻璃/透明元素在浅色模式下可见
- [ ] 边框在两种模式下都可见
- [ ] 交付前测试两种模式

### 布局响应式
- [ ] 悬浮元素与边缘有适当间距
- [ ] 内容不会隐藏在固定导航栏后面
- [ ] 在 320px、768px、1024px、1440px 下响应良好
- [ ] 移动端无水平滚动

### 可访问性
- [ ] 所有图片都有 alt 文字
- [ ] 表单输入框都有标签
- [ ] 颜色不是唯一的状态指示器
- [ ] 尊重 `prefers-reduced-motion` 设置

---

## 🚫 绝对避免

### AI 通用美学（AI Slop）

| 类别 | 避免 | 替代方案 |
|------|------|----------|
| 字体 | Inter, Roboto, Arial | Playfair Display, DM Sans, Archivo |
| 配色 | 紫色渐变 + 白色背景 | 大胆的主导色 + 强烈点缀 |
| 布局 | 预测性组件模式 | 不对称、重叠、对角线 |
| 风格 | 缺乏特色的通用设计 | 针对上下文的独特设计 |

---

## 💡 设计原则

1. **意图性** - 每个设计决策都应有明确的理由
2. **一致性** - 在整个界面中保持美学统一
3. **记忆点** - 设计一个让人难忘的特色元素
4. **精确执行** - 无论极简还是繁复，都要精确到位
5. **突破常规** - 敢于打破"安全"的设计选择

---

## 🎯 UI 风格速查

> 详细风格指南通过 `search.py --domain style` 查询

### 玻璃拟态 (Glassmorphism)

```css
.glass {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 16px;
}
/* 浅色模式：提高不透明度 bg-white/80，边框用 rgba(0,0,0,0.1) */
```

**适用**: 现代 SaaS、金融仪表板 | **注意**: 需要丰富背景 + 足够对比度

### 新野蛮主义 (Neubrutalism)

```css
.neubrutalism-card {
  background: #FFEB3B;
  border: 3px solid #000;
  box-shadow: 4px 4px 0 #000;
  border-radius: 0;
}
.neubrutalism-card:hover {
  transform: translate(2px, 2px);
  box-shadow: 2px 2px 0 #000;
}
```

**适用**: Gen Z 品牌、创意机构 | **注意**: 对传统企业可能过于活泼

### Bento Grid

```css
.bento-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}
.bento-card { border-radius: 24px; padding: 24px; }
.bento-card.large { grid-column: span 2; grid-row: span 2; }
.bento-card.wide { grid-column: span 2; }
```

**适用**: 仪表板、产品页面、Apple 风格 | **注意**: 不适合密集数据表格

### 新拟态 (Neumorphism)

```css
.neu-card {
  background: #e0e5ec;
  box-shadow: 9px 9px 16px rgba(163,177,198,0.6), -9px -9px 16px rgba(255,255,255,0.5);
}
```

**适用**: 健康应用、冥想 | **注意**: 对比度较低，可访问性受限

---

## 参考资源

- [Awwwards](https://www.awwwards.com/) - 优秀网站设计灵感
- [Google Fonts](https://fonts.google.com/) - 字体选择
- [Coolors](https://coolors.co/) - 配色方案生成
- [Motion](https://motion.dev/) - React 动画库
- [Heroicons](https://heroicons.com/) / [Lucide](https://lucide.dev/) - SVG 图标
- [Simple Icons](https://simpleicons.org/) - 品牌 Logo SVG

---

**使用此 skill 时，Claude 将：**
- 在编码前先确定美学方向（风格、字体、配色）
- 使用 `search.py` 查询设计数据库获取推荐
- 避免 AI 通用美学（Inter 字体、紫色渐变、预测性布局）
- 选择有意图性的字体配对和行业配色
- 使用 SVG 图标（Heroicons/Lucide），不用 emoji
- 确保明暗模式对比度和可访问性
- 交付前执行检查清单验证
- 每个设计决策都有明确理由

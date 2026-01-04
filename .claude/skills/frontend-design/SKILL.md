# Frontend Design 前端设计最佳实践

**版本**: v1.0.0
**更新日期**: 2026-01-04

创建独特、生产级的前端界面，具有高设计质量。避免通用的 AI 美学风格。

---

## 🎯 何时使用

当用户要求构建以下内容时使用此 skill：
- Web 组件、页面、应用程序
- 网站、落地页、仪表板
- React 组件、HTML/CSS 布局
- 任何需要美化的 Web UI

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

**关键**: 选择清晰的概念方向并精确执行。大胆的最大化主义和精致的极简主义都有效 - 关键是**意图性**，而非强度。

---

## 🎨 美学指南

### 1. 字体选择

#### ✅ 推荐做法
```css
/* 标题字体 - 独特且有个性 */
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Archivo+Black&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&display=swap');

/* 正文字体 - 可读性与美感兼具 */
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Source+Serif+4:wght@400;600&display=swap');
```

#### ❌ 避免的字体
- Inter、Roboto、Arial、系统字体
- 过度使用的 Space Grotesk
- 任何"安全"但无特色的选择

#### 字体配对示例

| 场景 | 标题 | 正文 |
|------|------|------|
| 高端奢华 | Playfair Display | Source Serif 4 |
| 现代科技 | Archivo Black | DM Sans |
| 创意艺术 | Bebas Neue | Work Sans |
| 编辑风格 | Fraunces | Literata |
| 极简优雅 | Cormorant | Lato |

### 2. 色彩与主题

#### ✅ 推荐做法
```css
:root {
  /* 主导色 + 强烈点缀 */
  --color-dominant: #0a0a0a;
  --color-accent: #ff3d00;
  --color-surface: #fafafa;

  /* 或者大胆的配色方案 */
  --color-primary: #1a1a2e;
  --color-secondary: #16213e;
  --color-accent: #e94560;
  --color-highlight: #0f3460;
}
```

#### ❌ 避免的配色
- 白色背景上的紫色渐变（典型 AI 美学）
- 平均分布的调色板
- 过于保守、无特色的配色

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

const container = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: { staggerChildren: 0.1 }
  }
}

const item = {
  hidden: { opacity: 0, y: 20 },
  show: { opacity: 1, y: 0 }
}

function AnimatedList({ items }) {
  return (
    <motion.ul variants={container} initial="hidden" animate="show">
      {items.map((item) => (
        <motion.li key={item.id} variants={item}>
          {item.name}
        </motion.li>
      ))}
    </motion.ul>
  )
}
```

### 4. 空间构图

#### ✅ 打破常规的布局
```css
/* 不对称网格 */
.asymmetric-grid {
  display: grid;
  grid-template-columns: 2fr 1fr;
  grid-template-rows: auto auto;
  gap: 2rem;
}

.asymmetric-grid .feature {
  grid-row: span 2;
}

/* 对角线流动 */
.diagonal-section {
  clip-path: polygon(0 0, 100% 5%, 100% 95%, 0 100%);
  padding: 8rem 0;
}

/* 重叠元素 */
.overlap-container {
  position: relative;
}

.overlap-image {
  position: absolute;
  top: -2rem;
  right: -2rem;
  z-index: 10;
}
```

### 5. 背景与视觉细节

#### 渐变网格
```css
.gradient-mesh {
  background:
    radial-gradient(at 40% 20%, hsla(28,100%,74%,1) 0px, transparent 50%),
    radial-gradient(at 80% 0%, hsla(189,100%,56%,1) 0px, transparent 50%),
    radial-gradient(at 0% 50%, hsla(355,100%,93%,1) 0px, transparent 50%),
    radial-gradient(at 80% 50%, hsla(340,100%,76%,1) 0px, transparent 50%),
    radial-gradient(at 0% 100%, hsla(22,100%,77%,1) 0px, transparent 50%);
}
```

#### 噪点纹理
```css
.noise-texture {
  position: relative;
}

.noise-texture::before {
  content: "";
  position: absolute;
  inset: 0;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 400 400' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)'/%3E%3C/svg%3E");
  opacity: 0.05;
  pointer-events: none;
}
```

#### 几何图案
```css
.geometric-pattern {
  background-color: #0a0a0a;
  background-image:
    linear-gradient(30deg, #1a1a1a 12%, transparent 12.5%, transparent 87%, #1a1a1a 87.5%, #1a1a1a),
    linear-gradient(150deg, #1a1a1a 12%, transparent 12.5%, transparent 87%, #1a1a1a 87.5%, #1a1a1a),
    linear-gradient(30deg, #1a1a1a 12%, transparent 12.5%, transparent 87%, #1a1a1a 87.5%, #1a1a1a),
    linear-gradient(150deg, #1a1a1a 12%, transparent 12.5%, transparent 87%, #1a1a1a 87.5%, #1a1a1a);
  background-size: 80px 140px;
}
```

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

## 🔗 与 React Skill 协同

```
# 1. 初始化项目（react-best-practices）
"创建一个 React + TypeScript + shadcn/ui 项目"

# 2. 设计 UI（frontend-design）
"使用 frontend-design skill 为用户列表页设计 UI，
品牌：现代 SaaS，受众：专业人士，
感觉：专业、创新，审美：精致极简"

# 3. 继续开发（react-best-practices）
"添加用户详情页，包括数据获取和状态管理"
```

---

## 参考资源

- [Awwwards](https://www.awwwards.com/) - 优秀网站设计灵感
- [Dribbble](https://dribbble.com/) - UI 设计灵感
- [Google Fonts](https://fonts.google.com/) - 字体选择
- [Coolors](https://coolors.co/) - 配色方案生成
- [Motion](https://motion.dev/) - React 动画库

# 参考示例：Go 接口学习教程

以下是按照 learning-docs skill 生成的一份完整学习文档示例（节选），展示各部分的写作要点。

---

## 示例：学习规划

```markdown
# Go 接口 学习规划

## 学习目标
掌握 Go 语言接口的定义、实现和常用模式，能在实际项目中合理使用接口进行抽象。

## 知识点清单

### 阶段一：理解接口（基础）
1. 接口定义与隐式实现 — 不需要 implements 关键字
2. 多方法接口 — 一个接口可以有多个方法

### 阶段二：核心用法（进阶）
3. 空接口 any — 万能容器，接收任何类型
4. 类型断言 — 从接口取回具体类型
5. 类型 switch — 优雅处理多种类型
6. 接口组合 — 小接口拼成大接口

### 阶段三：实践（综合）
7. error 接口 — Go 的错误处理机制
8. 综合项目 — 动物园管理程序

## 配套代码示例
- `examples/01-basic/main.go` — 接口基础定义与实现
- `examples/02-type-assert/main.go` — 类型断言与 switch
- `examples/03-composition/main.go` — 接口组合
```

### 要点说明

- 分阶段列出知识点，给出清晰的学习路径
- 每个知识点用一句话说明核心内容
- 配套代码列表让学习者知道有哪些实践材料

---

## 示例：教程主体（节选）

```markdown
# Go 接口 学习教程

> 学完本教程，你能用接口写出灵活解耦的 Go 程序。

## 你将构建什么

一个「动物园管理小程序」，从零开始，一步步添加功能：
- 让不同动物发出不同叫声（接口基础）
- 让动物表演节目（多方法接口）
- 实现明星动物（接口组合）
- 完整的动物园管理系统（综合运用）

## 前置准备

- 安装 Go 1.21+（运行 `go version` 确认）
- 一个文本编辑器（推荐 VS Code + Go 扩展）

---

## 第一步：让动物开口说话

创建项目目录并初始化：

    mkdir zoo && cd zoo
    go mod init zoo

创建 `main.go`：

    package main

    import "fmt"

    // 定义接口：会说话的动物
    type Speaker interface {
        Speak() string
    }

    // 猫 - 实现 Speaker 接口（不需要写 implements！）
    type Cat struct{ Name string }
    func (c Cat) Speak() string { return fmt.Sprintf("%s说：喵喵！🐱", c.Name) }

    // 狗
    type Dog struct{ Name string }
    func (d Dog) Speak() string { return fmt.Sprintf("%s说：汪汪！🐕", d.Name) }

    func main() {
        animals := []Speaker{
            Cat{Name: "小花"},
            Dog{Name: "旺财"},
        }
        for _, a := range animals {
            fmt.Println(a.Speak())
        }
    }

运行一下：

    go run main.go

你应该看到：

    小花说：喵喵！🐱
    旺财说：汪汪！🐕

恭喜！你的动物已经会说话了。注意我们没有写任何 `implements` 关键字 —— 在 Go 中，只要实现了接口的所有方法，就自动满足该接口。这叫**隐式实现**。

## 第二步：...
```

### 要点说明

- 开头就说"你将构建什么"，给出具体的项目
- 每一步先给完整代码，再给运行命令和预期输出
- 使用"你应该看到"模式确认成功
- 解释只用 1-2 句话，不展开理论讨论
- 用有趣的例子（动物、emoji）保持学习兴趣

---

## 示例：附录 A 排错指南（节选）

```markdown
## 附录 A：排错指南

### 问题 1：nil 接口调用 panic

**现象**：运行时报 `panic: runtime error: invalid memory address or nil pointer dereference`

**原因**：声明了接口变量但没有赋值，默认是 nil，调用方法会 panic。

**解决**：

    // ❌ 错误：未赋值的接口变量
    var s Speaker
    fmt.Println(s.Speak())  // panic!

    // ✅ 正确：先赋值再使用
    var s Speaker = Cat{Name: "小花"}
    fmt.Println(s.Speak())  // 正常

### 问题 2：指针接收者导致无法实现接口

**现象**：编译错误 `Cat does not implement Speaker (Speak method has pointer receiver)`

**原因**：方法定义在 `*Cat` 上（指针接收者），但你传的是 `Cat`（值类型）。

**解决**：传指针 `&Cat{}` 而不是值 `Cat{}`。

    // ❌ 方法在指针上，但传了值
    func (c *Cat) Speak() string { ... }
    var s Speaker = Cat{}   // 编译错误

    // ✅ 传指针
    var s Speaker = &Cat{}  // 正确
```

### 要点说明

- 按"现象 → 原因 → 解决"三段式组织
- 用 ❌/✅ 正反对比，一目了然
- 给出完整的可复现代码片段

---

## 示例：附录 C 参考表（节选）

```markdown
## 附录 C：Go 标准库常用接口速查

| 接口 | 包 | 方法签名 | 用途 |
|------|-----|---------|------|
| `error` | builtin | `Error() string` | 错误处理 |
| `Stringer` | fmt | `String() string` | 自定义打印格式 |
| `Reader` | io | `Read(p []byte) (n int, err error)` | 读取数据流 |
| `Writer` | io | `Write(p []byte) (n int, err error)` | 写入数据流 |
| `Handler` | net/http | `ServeHTTP(ResponseWriter, *Request)` | HTTP 处理器 |
```

### 要点说明

- 每行一个条目，简洁明了
- 包含包名、方法签名、用途，工作时可快速查阅
- 不加解释，需要深入了解的去看教程主体或附录 D

---

## 示例：附录 D 设计哲学（节选）

```markdown
## 附录 D：设计哲学

### 为什么 Go 选择隐式实现？

大多数语言（Java、C#、TypeScript）要求显式声明 `implements`。Go 反其道而行，只要你实现了方法，就自动满足接口。

这不是偶然。Go 的设计者 Rob Pike 和 Ken Thompson 有丰富的系统编程经验，他们观察到：

1. **解耦**：定义接口的包和实现接口的包不需要互相知道对方的存在
2. **渐进式抽象**：先写具体实现，后面需要抽象时再定义接口，不用修改已有代码
3. **减少依赖**：不需要 import 接口所在的包就能实现它

这种设计的代价是：你无法一眼看出一个类型实现了哪些接口。但 Go 社区认为这个代价值得 —— 编译器会在你真正使用的地方帮你检查。

### 为什么 Go 推崇小接口？

Go 标准库的接口大多只有 1-2 个方法。这不是巧合：

- **io.Reader** 只有一个 `Read` 方法
- **error** 只有一个 `Error` 方法
- **fmt.Stringer** 只有一个 `String` 方法

Go 谚语说："接口越大，抽象越弱。" 小接口更容易被实现，组合起来也更灵活。
```

### 要点说明

- 讨论"为什么"，不是"怎么做"
- 提供历史背景和设计者的思考
- 分析权衡和取舍，帮助读者建立深层理解
- 与教程主体分开，不干扰动手学习的节奏

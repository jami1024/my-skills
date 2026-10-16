# Go 主题 skill 上游断言审阅

上游 `evals/evals.json` 是特定模型、特定版本下的历史断言，其中一部分要求本仓库已经改掉的固定约定。本文记录哪些断言与本地正文冲突、改成了什么、以及为什么其余断言保持原样。改写结果落在 [`golang-overrides.json`](../../scripts/golang-overrides.json) 的 `assertion_fixes`，由 `apply-golang-overrides.py` 随同步一起重放。

## 范围

只有两个 skill 的本地修正改变了行为，因此只有它们的断言需要审阅：

| skill | 本地修正 | 影响的断言 |
| --- | --- | --- |
| `golang-testing` | 集成测试不再强制 `//go:build integration`；测试文件命名沿用项目约定；不重排测试顺序 | 4 |
| `golang-project-layout` | 不再强制 `cmd/` + `internal/`/`pkg/` 布局；不再要求架构选择仪式 | 10 |

其余 44 个 skill 的本地差异只有 description 精简、路由行和链接修正，不改变正文要求，无需改断言。`golang-how-to` 与 `golang-google-wire` 中涉及 `//go:build wireinject` 的断言属于 Wire 工具语义（生成器要求），不是风格偏好，保持原样。

## 断言集现状

- 42 个 `evals.json`：822 个用例、3804 条断言。
- 两种 schema：34 个文件是顶层数组，8 个是 `{"skill_name", "evals"}` 对象。任何重跑脚本都要先归一化这一层。
- 断言是自然语言文本，判分依赖模型作答加人工或自动核对，不能在本地离线跑出分数。

## 已改写的断言

改写遵循等价替换：保留可测的要求（例如"集成测试必须能被独立选中"），只去掉与本地正文冲突的具体形式。

### golang-project-layout

| 断言 | 上游要求 | 现在要求 |
| --- | --- | --- |
| 1.1 | 询问用户偏好哪种软件架构 | 选择匹配请求的最小结构；单包加根 `main.go` 合法，用户明确指定架构则遵循 |
| 1.2 | 询问项目规模以确定结构 | 按请求规模选择结构，不套固定模板 |
| 1.4 | 把依赖注入方式作为后续提问 | 不要求做 DI 决策；除用户要求 DI 库外，显式构造是默认 |
| 2.2 | `cmd/` 只放解析 flag、装配依赖、调用 `Run()` | 入口聚焦装配与启动，而不是请求处理、查询和格式化 |
| 2.3 | 建议把业务逻辑移到 `internal/` 或 `pkg/` | 建议把混杂职责抽成独立包；`internal/`、`pkg/` 或具名业务包都可以 |
| 2.5 | 绝不在 `cmd/` 放请求解析、数据库查询、响应格式化 | 指出这些职责不属于入口 |
| 3.6 | 建议把 `main.go` 放进 `cmd/{name}/`，不放根目录或 `src/` | 建议移出 `src/`；模块根和 `cmd/{name}/` 都合法 |
| 5.1 | 把对外共享的日志库放进 `pkg/` | 放进可导入的包（模块根或 `pkg/`）；`pkg/` 是可选项 |
| 5.5 | 业务逻辑默认放 `internal/` | 业务包不进 `pkg/`，`internal/` 只在导入限制真正有用时使用 |
| 11.5 | 业务逻辑在 `internal/`，不在多个 `cmd/` 间重复 | 共享逻辑放在公共包，而不是在多个 `cmd/` 目录间重复 |

### golang-testing

| 断言 | 上游要求 | 现在要求 |
| --- | --- | --- |
| 2.2 | 使用 `//go:build integration` | 用项目已有机制独立选中集成测试（build tag、独立包、flag、环境配置或专用命令） |
| 2.3 | 解释为什么优先 build tag | 解释选择机制必须能挡住昂贵初始化：build tag 把文件排除出编译，`testing.Short()` 在无 `-short` 时仍会编译并可能连接 |
| 2.4 | 给出 `go test -tags=integration ./...` | 给出与所选机制一致的运行命令 |
| 12.5 | 使用 `//go:build integration` | 让集成测试通过项目选择的机制可选中（例如 build tag） |

`golang-testing/SKILL.md` 的「Integration Tests」小节原写「Use build tags to separate integration tests from unit tests」，与同一文件里已经改过的原则 2 不一致，本次一并对齐为「Make integration tests runnable independently. A build tag is a common choice:」，示例仍展示 build tag 这一种做法。该修正同样登记在 `replacements`。

断言 2.1（拒绝把 `testing.Short()` 作为主要分离机制）保持原样：本地正文改成"沿用项目已有机制"，但没有把 `testing.Short()` 列为候选，2.3 改写后仍解释它的缺陷。

## 重跑结果

本节结果由 [`scripts/run-skill-eval.py`](../../scripts/run-skill-eval.py) 产生：7 个用例 × 2 个条件（只注册目标 skill / 完全不注册），共 14 个独立会话。

```bash
python3 scripts/run-skill-eval.py --skill golang-project-layout:1,2,3,5,11 \
  --skill golang-testing:2,12 --out .tmp/skill-eval
```

- 模型与设置：`deepseek/deepseek-v4-flash-vision-exp`，thinking `low`；`pi -p --mode json --no-session --no-context-files --no-skills --no-extensions --no-mcp --tools read`。有 skill 的一侧用 `--skill` 只注册目标目录，提示词取 `evals.json` 原文，追加一句"只读、直接在回复里作答"。
- 证据：`.tmp/skill-eval/*.jsonl`、`*.answer.md` 与 `results.json`（含逐例 exit、耗时和真实读取路径），`.tmp` 被忽略；每条结论都可用上面的命令重新生成。
- 判定：逐份阅读回答人工核对 14 条断言，不采信模型自报结论；回放 `read` 事件确认基线一侧没有读到任何 skill 文件，且 7 个处理组都读到了目标 `SKILL.md`。
- 这组用例先后用旧的一次性脚本和版本化脚本各跑一次，两次逐条判定一致。

| 用例 | 断言 | 有 skill | 无 skill 基线 |
| --- | --- | --- | --- |
| layout-01 | 1.1 按规模选最小结构 | 满足 | **不满足**：直接给出 `cmd/` + `internal/{service,repository,domain}` + `pkg/` + 空层模板 |
| layout-01 | 1.2 按请求规模而非套模板 | 满足 | **不满足**：同上 |
| layout-01 | 1.4 不要求做 DI 决策 | 满足 | 满足（未提 DI） |
| layout-02 | 2.2 入口只做装配与启动 | 满足 | 满足 |
| layout-02 | 2.3 混杂职责抽成独立包 | 满足 | 满足 |
| layout-02 | 2.5 三种职责不属于入口 | 满足 | 满足 |
| layout-03 | 3.6 `main.go` 移出 `src/` | 满足 | 满足 |
| layout-05 | 5.1 共享库放可导入包 | 满足 | 满足 |
| layout-05 | 5.5 业务包不进 `pkg/` | 满足 | 满足 |
| layout-11 | 11.5 共享逻辑放公共包 | 满足 | 满足 |
| testing-02 | 2.2 用项目机制独立选中 | 满足 | 满足 |
| testing-02 | 2.3 机制必须挡住昂贵初始化 | 满足 | 满足 |
| testing-02 | 2.4 给出与机制一致的运行命令 | 满足 | 满足 |
| testing-12 | 12.5 集成测试可独立选中 | 满足 | 满足 |

有 skill 的一侧 14/14 满足，上游断言与本地正文的矛盾已消除。同一批数据也说明另一件事：**12 条断言在完全不注册 skill 时同样满足**，只有 `golang-project-layout` 用例 1 的"按规模选择结构"真正区分了两侧；两次运行都是基线套固定分层模板，有 skill 时给出按规模选择的说明。

由此得到的用途界定：

- 这 14 条断言可以当**回归守卫**——上游同步后正文与断言再漂移会被发现；
- 它们**不是 skill 增益证据**。上游断言里有区分度的部分是强制 `cmd/`、强制 `internal/`、强制 build tag，而这些正是本仓库要去掉的固定约定；改成"按项目实际选择"后，断言退化为常识题。
- 所以 [EVALUATIONS.md](../../skills/golang/EVALUATIONS.md) 的历史分数依然不能沿用，本地效果证据仍只能来自[组合评估](golang-composition.md)。

## 本地断言与区分度

上一节说明 14 条改写断言里 12 条在无 skill 时也满足，因此另写了一批针对本地立场的断言，目标是拿到真实增益证据。

### 做法

- `golang-overrides.json` 新增 `local_cases`：按用例名幂等写入上游 `evals.json`（缺失则追加，内容变化则替换），随同步重放；
- 新增夹具 [`fixtures/existing-service`](fixtures/existing-service)：一个已有服务（`cmd/server` + `internal/{httpapi,store,integration}` + `migrations` + README），集成测试用 `TEST_DATABASE_URL` 选中并在变量为空时自行跳过，而不是用 build tag；
- 用例自带 `fixture` 字段，`run-skill-eval.py` 用它作为工作目录；
- 两条本地用例，断言 id 用 `L` 前缀：`golang-project-layout` 用例 12（给已有服务加"查询某用户全部订单"）与 `golang-testing` 用例 15（为新增的 `ListByUserID` 加集成测试）。

### 三轮结果

| 轮次 | 情况 | 结果 |
| --- | --- | --- |
| 1 | 夹具已经实现了用例要求的新接口，用例退化 | 两侧都回答"该接口已存在，无需改动"，无法判定 |
| 2 | 换成真正不存在的 `ListByUserID`，夹具补 schema/JSON tag | `project-layout` 的 with-skill 侧没读 SKILL.md（无效处理组）；`testing` 两侧都保留 env 选中 |
| 3 | 用 `/skill:<name>` 强制加载正文，两侧都确认读到了对应 skill | 6 条断言两侧全部满足 |

第三轮的判定（逐份阅读回答）：

| 断言 | 有 skill | 无 skill |
| --- | --- | --- |
| L1.1 先读现有入口/存储/README | 满足 | 满足 |
| L1.2 不新增 `cmd/`、`service/`、`repository/`、`domain/`、`pkg/` | 满足（明确写成 handler → store，不建新层） | 满足 |
| L1.3 加在现有 store 上并沿用构造函数装配 | 满足（`main.go` 不改） | 满足（同样 `main.go` 不改） |
| L2.1 先读现有测试或 README | 满足 | 满足 |
| L2.2 保留 env-var 选中，不迁移到 build tag | 满足 | 满足（"不用 build tag、不建 `tests/` 目录、不加新包"） |
| L2.3 不新建测试包或拆出新目录 | 满足 | 满足 |

### 结论

夹具里的约定是看得见的：README 明写集成测试靠 `TEST_DATABASE_URL` 选中，代码里也有现成演示。模型读到就会遵循，有没有 skill 几乎没有区别。因此这 6 条本地断言的定位是**本地 override 的回归守卫**，不是增益证据：

- 它们能抳住最危险的回归——上游正文原文是“集成测试必须用 build tag”，如果本地 override 回退或失效，L2.2 会失败；
- 它们不能回答“这个 skill 到底有没有用”。要拿到增益证据，场景必须是“约定不可见或与默认偏好冲突”（用户明确要求违反项目约定的改法，或默认做法与项目现状相悖），那是组合评估的活。

### 评估方法上的一个发现（已改为硬校验）

注册 skill 不等于模型读了 skill：本地用例第二轮里，`project-layout` 的 with-skill 侧一次都没读 `SKILL.md`，处理组直接退化成对照组。只看命令行参数就判定"已加载该 skill"不成立，必须回放 `read` 事件。

现在由 `run-skill-eval.py` 强制并校验：

- 默认用 `/skill:<name>` 强制加载正文（`--no-invoke-skill` 可关），这类加载不产生 `read` 事件，直接计为有效；
- 未强制时，处理组必须在 `read` 事件里出现过目标 `skills/golang/<skill>/SKILL.md`；
- 基线侧读到任何 `skills/**/SKILL.md` 即判为污染；
- 会话非 0 退出、处理组未读正文、基线污染都会在 `results.json` 里标为 `valid: false` 并附原因，同时让脚本以非 0 退出（`--allow-invalid` 可显式放行），避免无效证据被静默写进结论。

按这套口径回放历史日志：[断言重跑](#重跑结果)的两次运行共 14 个会话全部有效（7 个处理组均读到目标正文，基线 0 污染）；本地用例第一、二轮 `project-layout` 的处理组无效，已在第三轮用强制加载重做。

## 未覆盖

- 单模型、每例只跑一次，没有重复采样，也没有更换 thinking 或模型。"基线也满足"这一判定需要更多样本才能当结论。
- 判定是人工阅读回答，不是自动正则，也没有第二人复核。
- 只审阅了受本地正文改动影响的两个 skill；其余 40 个 skill 的断言未逐条审阅，也未重跑。
- 本地断言只在一个小夹具上跑过；“约定不可见或与默认偏好冲突”这类可能真正区分两侧的场景未设计。
- 本地 `skills/golang` 现在就是上游加 `assertion_fixes` 与 `local_cases` 之后的状态，重跑前不需要额外处理；`scripts/tests/test_skill_tools.py` 会校验本地断言、本地用例与清单一致，防止手改本地文件造成漂移。
- 上游新增或改写断言后，同步脚本会照常替换副本，`assertion_fixes` 若匹配不上会在替换前报错，需要重新审阅本文和清单。

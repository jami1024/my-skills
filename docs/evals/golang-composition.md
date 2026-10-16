# Go skill 组合评估

目标：验证本地蓝图与主题 skill 一起使用时能否正确路由、保留项目约定、生成可运行代码和控制改动范围。本文件是评估材料，不是运行时指令。

## 运行方法

每例使用独立干净会话，注册 `skills/dev/golang-best-practices` 与 `skills/golang`，不预读全部正文。先让模型按真实任务读取必要的 skill，再执行或解释任务。记录实际读取路径、理由、代码改动、验证命令及结果。

两种运行分开记录：

- **路由冒烟**：只提供任务和完整 skill 目录，允许只读工具；检查实际读取了哪些正文、能否解释边界与验证计划。不能据此声称生成代码可运行。
- **实现评估**：在临时 Go 项目中准备场景所需的现有目录、配置和测试，允许修改与执行；必须实际运行测试或构建，并检查目录、依赖和公共 API 是否出现无关变化。

每例检查路由、约定保持、正确性、验证诚实性和改动范围。任一出现编造执行结果、未经请求新增依赖、无关搬包或改变公共 API，均判失败。skill 数量是辅助证据，不单独按固定数量判分；增加主题应有明确任务依据。

不把作者自查或上游单 skill 正则断言分数记成当前组合的独立模型通过率。结果见 [golang-composition-results.md](golang-composition-results.md)。

## C1：已有结构下增加查询接口

**输入**：现有 Go 服务使用 `internal/handler`、`internal/service`、`internal/store`、原生 `database/sql` 和手工构造函数。增加按订单 ID 查询接口，未找到仍返回现有 404 JSON；不要搬包或引入 ORM。

**预期**：先读 `golang-how-to` 与本地蓝图；错误/数据库主题按需补充。保持 service 命名与手工注入，store 转换 not-found，handler 沿用响应。实现评估覆盖成功、404、数据库失败、取消，执行项目测试与构建。

**失败**：创建 biz 替换 service、引入 GORM/Wire、将 SQL 错误直接作为 API 响应。

## C2：修复一个错误映射函数

**输入**：下面是 `mapLookupError` 的函数体；先返回任意错误，导致 not-found 映射失效。只修复本函数，保留其他错误的 `errors.Is` 能力：`if err != nil { return fmt.Errorf("lookup: %w", err) }; if errors.Is(err, sql.ErrNoRows) { return ErrNotFound }; return nil`。

**预期**：主题是 `golang-error-handling`，不加载项目蓝图、数据库或性能 skill。先处理 `sql.ErrNoRows`，再包装其余错误。实现评估测试 nil、直接和包装后的 not-found、其他 sentinel 错误及包装上下文。

**失败**：复制原来的分支顺序、丢弃 `%w`、为此重构目录或错误架构。

## C3：取消 worker 并避免泄漏

**输入**：已有 worker 从 channel 收任务，调用方取消后 worker 仍阻塞。修复取消和退出逻辑，不修改现有接口或换并发框架。

**预期**：`golang-concurrency` 与 `golang-context`；先识别 channel 所有权和取消传播，按项目方式验证。实现评估覆盖取消、channel 关闭和重复退出，运行 `go test -race`。

**失败**：为隐藏阻塞加 sleep、改用 Background、无依据新增 reactive 或 goroutine 库。

## C4：保留现有测试组织

**输入**：现有 Go 项目用 `authorization_test.go` 测授权行为，集成测试通过单独 package 和 `make test-integration` 选择，没有 build tags。补一个未登录请求失败用例；不要调整测试组织，不引入 testify。

**预期**：只需 `golang-testing`；保留文件名、标准库断言和选择方式。实现评估运行相关 package 和已有集成命令，新增用例断言实际状态码与响应。

**失败**：强制按源文件重命名测试、添加 integration build tag、要求测试函数按源代码重排。

## C5：线上偶发卡顿

**输入**：Go 服务偶发卡顿，已经有延迟指标。先给低侵入的取证方案，再根据 pprof 结果决定优化；目前未提供 profile。不要先改业务代码。

**预期**：`golang-benchmark`，需要根因定位时补 `golang-troubleshooting`；不为本次任务加载本地蓝图和一整套库 skill。说明采样条件、敏感端点访问控制、与正常时段对比，不虚构热点或性能收益。

**失败**：没有 profile 却宣称找到热点、先上对象池或缓存、把验证计划写成已执行结果。

## C6：小型服务的最小结构

**输入**：新建一个小型 Go HTTP 服务，只有健康检查和一个内存查询接口，用标准库和手工构造函数。给出与规模匹配的结构和实现，不需要数据库、DI 容器、JWT 或部署平台。

**预期**：先本地蓝图，目录细节确有需要再读 `golang-project-layout`。允许合并层级，明确 HTTP 生命周期、超时和退出。实现评估 `go test ./...`、`go build ./...`，确认未引入第三方依赖。

**失败**：生成空的 store/model 层、自动引入 Wire/GORM/容器或认证体系。

## C7：事务、失败与取消

**输入**：已有 GORM 项目，创建订单同时写 orders 和 order_items；第二步失败或 context 取消时不能留下部分订单。沿用现有 store 与事务回调，biz 不依赖 GORM 类型。

**预期**：本地蓝图与必要数据库/错误主题。事务实现在 store，沿用请求 context；领域错误跨层传播。实现评估包含第二步失败、取消和成功提交；沿用现有数据库测试夹具。

**失败**：biz 导入 GORM、使用 Background 代替请求 context、另加 ORM 或手写另一套事务框架。

## C8：凭证配置与越权

**输入**：已有服务新增第三方 API key 配置，同时补上“用户只能修改自己资料”的检查。沿用现有配置与认证中间件，key 来自环境，日志不回显。

**预期**：跨层任务先本地蓝图，安全行为读取 `golang-security`。区分认证和资源授权，检查缺失配置，敏感字段不出现在序列化结果。实现评估覆盖缺 key、未登录、访问他人资源和正常更新。

**失败**：只检查登录、把 key 加进默认配置或错误消息、顺便迁移配置库。

## C9：标准库切片操作

**输入**：给 `[]int` 去重并保留第一次出现的顺序，用标准库即可，不添加第三方库。

**预期**：需要指导时只读 `golang-data-structures`；不加载本地蓝图或 samber 库 skill。实现评估测试空输入、重复值、负数和顺序。

**失败**：为了匹配 skill 引入 lo/mo/ro、修改工程分层、声称性能提升但未测量。

## C10：非 Go 请求

**输入**：优化一个 React 列表的渲染性能，只涉及前端，不改后端。

**预期**：不加载 Go skill，不生成 Go 代码；使用当前环境的前端指引。实现评估沿用前端验证方式。

**失败**：因为目录里有 Go skill 就读编排器、建议改后端数据库或引入 Go 缓存服务。

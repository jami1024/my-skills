# Golang Best Practices 回归用例

## G1：新增服务端能力

**输入**

> 在现有 Go 服务中增加订单查询接口。项目已有 `cmd/`、`internal/handler`、`service` 和 `store`，请遵循现有结构。

**必须满足**

- 先读取 `go.mod`、入口、错误类型、配置和测试约定；
- 保持 handler、service、store 的依赖方向；
- 正确传递 context、处理错误、超时和资源生命周期；
- 运行 `gofmt`、测试、lint 或项目已有验证命令。

**失败信号**

- 创建巨大的 `utils` 包或全局数据库连接；
- 在 store 层返回 HTTP 状态码；
- 忽略 response body、超时或取消信号。

## G2：并发问题

**输入**

> 多个 goroutine 同时更新内存缓存，偶尔出现数据竞争。请修复并说明如何验证。

**必须满足**

- 先构造稳定复现或最小失败测试；
- 明确共享状态、生命周期和同步边界；
- 选择简单可解释的 mutex、channel 或其他方案；
- 运行 `go test -race ./...` 或项目等价命令。

**失败信号**

- 只增加 sleep 或重试；
- 用 `context.Background()` 隐藏调用方取消；
- 没有竞态验证就宣称修复。

## G3：非适用请求

**输入**

> 请优化一个 React 页面中的列表渲染性能。

**必须满足**

- 说明 Go skill 不适用于该请求；
- 不生成 Go handler、goroutine 或后端 API；
- 可以建议使用 React 专用 skill 或前端性能工具。

**失败信号**

- 把前端问题改写成 Go 服务优化；
- 建议无关的数据库或 HTTP 中间件改动。

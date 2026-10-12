# 读码报告样例

本目录收录用 `code-reading` 工作流真实产出的报告，用于演示完整流程与最终报告格式。**不会被客户端默认加载**，需要时按路径手动引用。

## Redis：客户端请求处理流程

- [`redis-client-request.zh.md`](redis-client-request.zh.md) — 中文
- [`redis-client-request.en.md`](redis-client-request.en.md) — English

**内容**：[redis/redis](https://github.com/redis/redis) `unstable` 分支 @ `1f245638`（2023 年 / v7.1 时代快照）。一条命令（`SET foo bar`）如何从 TCP 字节流走到写回 socket：`readQueryFromClient` → `processInputBuffer` → `processCommand`（约 15 步校验）→ `call` → `addReply` → `beforeSleep` 写回，以及承载整条流水线的三个数据结构（事件表、连接抽象、客户端状态）。

**触发提示词**（就这么一句）：

```text
用 code-reading 的方式分析 处理客户端请求的流程
```

**为什么这个样例可信**：真机执行——`make noopt` 编译、redis-cli 实测驱动、lldb 抓取调用栈（4.1 节就是实际抓到的栈，是 ground truth 而非静态推断）。`[verified]`/`[static]` 标注与全部 `file:line` 引用经人工比对锁定 commit 核验（审阅中发现并修正了一处行号错误，见附录）。

样例正文与上游 [lichuang/how-to-read-code](https://github.com/lichuang/how-to-read-code) 保持一致，仅将标题中的 skill 名改为 `code-reading`。

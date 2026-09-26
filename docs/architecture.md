# My Skills 架构

## 分层原则

仓库分成三层：

1. **源码层**：`skills/` 是唯一的 skill 源码位置。
2. **兼容层**：`.claude/skills` 是 Claude Code 的项目级入口；它指向源码，不保存第二份文件。
3. **配置层**：pi 或其他客户端通过 settings、plugin 或 package 配置选择要加载的分类。

## 分类

```text
skills/
├── dev/       # 开发与设计最佳实践
├── content/   # 知识库、讲解和内容成稿
└── session/   # 会话交接与项目归档
```

分类目录只是组织方式；加载范围由客户端配置决定。pi 若只需要内容工作流，应指向 `skills/content`，不要指向整个仓库。

## 单个 skill

每个 skill 必须是独立目录，目录名必须与 `SKILL.md` 的 `name` 一致。详细内容按需放入 `references/`、`scripts/` 或 `assets/`，不要把所有资料塞进启动时会被读取的 description。

## 数据与工具分离

`my-skills` 保存工具和流程；个人 wiki 保存 raw、wiki、index 和 log 数据。本机的 `~/wiki-hub` 只是一个示例数据目录；`library` 必须使用用户明确提供的 `<WIKI_ROOT>`、项目配置或环境变量，不自动猜测路径。

## 兼容入口

当前仓库保留 `.claude/skills -> ../skills` 软链接，便于 Claude Code 在本仓库作为项目打开时发现 skills。pi 使用 settings 指向具体分类目录。全局配置不纳入本仓库的版本控制。

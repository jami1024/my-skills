# Skills 仓库优化任务

## Tasks
- [x] T1 盘点仓库结构、Git 状态和现有 skill 元数据
- [x] T2 确定中性源码目录与兼容接入策略
- [x] T3 将现有 skill 按用途迁移到 `skills/dev` 与 `skills/session`
- [x] T4 新建 `skills/content` 下的知识与内容工作流 skill
- [x] T5 添加 skill 模板、规范说明和自动验证脚本
- [x] T6 更新 README，改为引用式安装并说明按类别加载
- [x] T7 运行结构、规范和脚本验证，修复发现的问题
- [x] T8 将三个超长 SKILL.md 的详细内容拆入 `references/`
- [x] T9 创建独立 Wiki 数据目录 `~/wiki-hub`
- [x] T10 移除 `library` 对本机 Wiki 路径的默认假设
- [x] T11 统一所有 skill description 的适用边界，避免技术栈 skill 误触发
- [x] T12 修正文档中的 skill 数量与验证结果，确保维护记录和仓库现状一致
- [x] T13 让验证脚本自动发现 skill 目录下的断链软链接
- [x] T14 借鉴 Superpowers 的调试与完成前验证，但拆为按需加载的参考模块
- [x] T15 标记历史归档目录，避免旧版 skill 被误当作当前源码
- [x] T16 为所有 active skill 补齐 eval 回归用例，覆盖触发、边界和不适用请求

## 验收标准

- 所有 skill 的 `SKILL.md` 目录名与 frontmatter `name` 一致。
- `.claude/skills` 不再保存第二份 skill 源码，只作为 Claude Code 兼容入口。
- pi 可以通过 `skills/content` 只加载内容类 skill（全局 settings 由用户另行配置）。
- 新 skill 的 description 明确写出适用场景与不适用场景。
- 验证脚本能发现缺失 frontmatter、非法名称、重复名称和超长正文。
- 已运行 `python3 scripts/validate-skills.py --strict`：9 个 skill，0 个错误、0 个 warning；原有超长正文已拆分。
- 已运行 `git diff --check`：通过。
- 已修复 FastAPI/Golang 模板软链接，统一指向 `skills/dev/development-workflow/templates`。
- 已验证没有断开的软链接；迁移涉及的仓库内部文档和 Docker 指南链接均已更新。模板中的 `../types/*.ts` 等链接是目标项目示例路径，不是本仓库文件。
- 验证脚本会自动检查 `skills/` 下的软链接目标，断链直接报告为错误。
- 已验证 `.claude/skills` 与 `skills/` 指向同一目录，两个入口均发现 9 个 skill。
- `library` 没有默认 Wiki 路径；未提供 `<WIKI_ROOT>` 时必须询问用户。
- 所有 skill 的 description 均同时说明适用场景和不适用场景；技术栈 skill 不会仅凭宽泛的后端/前端措辞触发。
- `development-workflow` 的主体保持在 500 行以内；调试和完成前验证放在 `references/`，仅按场景读取，不增加默认上下文负担。
- `docs/archive/` 已有说明文件，明确其中内容仅供迁移对照，不属于当前可加载源码。
- 所有 active skill 都有 `evals/cases.md`；这些用例只用于手工回归，不改变其他项目的运行时加载内容。
- 不执行 `git commit` 或 `git push`。

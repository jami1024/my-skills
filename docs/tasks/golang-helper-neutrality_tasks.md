# Go 可选工具入口通用化

目标：让 Makefile、辅助脚本和 Docker 示例符合工程指南的按需选择原则，支持根目录单包和多文件入口，错误能真实传播。

## Tasks

- [x] T1 修正 Makefile 的入口、可选安装、清理、生成失败与 Compose 命令，补执行级回归。
- [x] T2 让迁移、Wire 与镜像辅助脚本要求实际需要的参数，并允许项目自行选择包路径与构建参数。
- [x] T3 精简 Docker 示例的固定应用、工具链、平台、数据库和缓存假设；同步维护说明并验证可用部分。
- [x] T4 完成全部回归、严格校验和改动文件诊断，记录实际执行与未验证范围。

## 验证计划

- 在临时标准库 Go 项目中执行 Makefile 的安装、构建、测试和启动，覆盖多个源文件以及自选入口。
- 用命令替身验证工具选择、参数原样传递、缺失参数、失败退出与成功提示，不连接真实数据库、不启动外部服务。
- Docker 可用时运行 Compose 配置检查；镜像构建需要实际引擎与项目指定基础镜像，缺少时明确记录。
- `python3 -B -m unittest discover -s scripts/tests -v`、`python3 -B scripts/validate-skills.py --strict`、Shell 语法和差异检查。

## 验证结果

- 38 项回归全部通过（原有 20 项，新增 18 项），没有跳过。实际标准库多文件程序完成 install、test、run；自选 `./cmd/server` 入口和带空格的产物目录也执行通过。
- 命令替身验证迁移缺参数、显式连接、创建文件无需连接、版本 0、错误退出；Wire 包路径与失败传播；工具按版本选择和 Compose 配置参数一致性。
- Docker Compose 5.1.2 配置解析通过：默认仅 app，database/cache 分别只增加相应依赖，不产生 app 的隐式 depends_on。
- Docker Engine 29.4.0 实际使用本机已有 `golang:1.26.0-alpine` 构建：根目录多文件加 `go:embed` 静态 Markdown 资源输出 `container-ready`；选择 `./cmd/check` 输出 `selected-entry-ready`，两次退出均为 0。
- 两个镜像运行配置均为 UID/GID `65532:65532`；临时容器随运行退出删除，临时镜像已清理。原始日志留在被忽略的 `.tmp/golang-helper-container-check/`。
- 56 个 skill 严格校验：0 错误、0 警告；4 个辅助脚本语法和差异检查通过；主动 LSP 检查确认 8 个文件无问题，另 1 个检查两次超时未确认，不视为干净。

## 行为变化与验证边界

- `make install` 默认只下载项目依赖，工具按显式版本安装；dev 默认使用 Go；test 默认不生成覆盖率或强制竞态，分别提供 coverage/test-race；clean 不清共享 Go 缓存。
- 迁移脚本不再默认 up 或使用内置连接，create/force 必须提供必要参数。未操作真实数据库、未验证某个实际迁移或 Wire 项目的业务正确性。
- Docker 示例面向纯 Go 静态程序。未验证 CGO、运行时资源权限、真实数据库/Redis 联调或生产部署；启用 profile 仍需项目实际连接配置和就绪语义。

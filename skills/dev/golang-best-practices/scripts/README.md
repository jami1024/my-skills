# Go 可选辅助脚本与 Makefile

这些入口是采用相应工具后的示例。先复用项目已有命令，不为脚本新增 ORM、注入工具、容器或目录层级。以下命令都从项目根目录运行；直接在 skill 目录执行不代表已经验证用户项目。

## 基础命令

本 skill 的 Makefile 默认支持根目录多文件 `main` package：

```bash
make install                 # 只下载 go.mod 依赖，不安装辅助工具
make test                    # go test ./...
make test-race               # 按任务需要运行竞态检查
make build                   # 编译整个入口 package 到 bin/app
make run
make lint                    # 默认 go vet ./...
make clean                   # 只删除本地构建与覆盖率产物，不清共享 Go 缓存
```

通过变量选择实际入口和工具，不按本机是否安装工具隐式切换行为：

```bash
make build MAIN_PACKAGE=./cmd/server APP_NAME=server
make dev DEV_COMMAND=air
make lint LINT_COMMAND='golangci-lint run ./...'
make coverage
```

`MAIN_FILE` 仍可覆盖旧入口配置，但多文件程序应传 package 路径（`.` 或 `./cmd/server`），避免只编译一个源文件。`BUILD_DIR`、`APP_NAME` 可配置，运行和构建使用相同的产物路径。

## 可选工具安装

只有显式传版本的工具才会安装，安装失败会使目标失败，不使用 `latest`：

```bash
make install WIRE_VERSION=v0.6.0
make install GOLANGCI_LINT_VERSION=v2.1.6 AIR_VERSION=v1.61.7
```

示例版本需要与项目工具链和配置兼容；golangci-lint 的 v1/v2 模块路径会相应选择。缺少工具时按项目现有版本管理方式准备，不由脚本自动安装。

## 辅助脚本

| 脚本 | 使用条件 | 命令示例 |
| --- | --- | --- |
| `lint.sh` | 已使用 golangci-lint，且需要连同 go vet 一起检查 | `bash scripts/lint.sh` |
| `wire-gen.sh` | 已采用 Wire，传入真实包路径；无参数默认当前包 | `bash scripts/wire-gen.sh ./orders/...` |
| `db-migrate.sh` | 已采用 golang-migrate；数据库操作显式提供连接 | `bash scripts/db-migrate.sh up` |
| `docker-build.sh` | 已有 Docker 构建配置；额外选项原样传给 docker build | `bash scripts/docker-build.sh example-app dev --build-arg MAIN_PACKAGE=.` |

`make wire WIRE_PACKAGES='./orders/... ./inventory/...'` 与脚本一样不会假定 `internal/wire` 存在；生成失败直接返回失败。

## 数据库迁移

迁移脚本要求明确操作，不再以无参数执行 up；没有内置数据库地址或凭据。

- `create <name>` 只创建文件，不需要 `DATABASE_URL`；
- `up`、`down`、`version`、`force <version>` 要求非空 `DATABASE_URL`；
- `down` 回滚一版，`force` 修改迁移版本记录；执行前核对项目的恢复流程；
- `MIGRATIONS_DIR` 默认 `./migrations`，可以按项目设置。

连接值从环境传入，脚本不回显；脚本仍将其作为 golang-migrate 的参数，应沿用项目现有的凭据传递与运行环境约定。

## 容器入口

`make docker`、`docker-build`、`docker-logs`、`docker-down` 使用 Compose v2，同一组 `COMPOSE_FILE`、`ENV_FILE` 配置贯穿各命令：

```bash
make docker COMPOSE_FILE=templates/docker/docker-compose.yml ENV_FILE=.env.dev
```

Makefile 不自动创建环境文件，Docker 示例中的 `GO_IMAGE`、入口包和应用监听方式按项目配置。容器中的最终运行镜像不一定带 Go 工具链；测试通常在本地或专用构建/测试阶段执行。详见 [`../templates/docker/`](../templates/docker/)。

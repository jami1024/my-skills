# Go 可选 Docker 示例

只有项目需要容器时才使用。本目录默认运行一个应用，不要求数据库、缓存、JWT、固定包结构或某个地区的镜像代理。

## 放置与构建

保留以下相对布局，Compose 的构建上下文是项目根目录：

```text
project/
├── go.mod
├── main.go                    # 默认入口；可改 MAIN_PACKAGE
└── templates/docker/
    ├── Dockerfile
    ├── docker-compose.yml
    └── .env.example
```

不需要调整代码目录来适配模板。将本目录的 `.dockerignore` 复制到项目根目录后，按实际资源调整；不要忽略编译需要的 `wire_gen.go`、vendor 或 `go:embed` 文件。

```bash
cp templates/docker/.env.example .env.dev
# 编辑 .env.dev：GO_IMAGE 与 go.mod/CI 对齐，MAIN_PACKAGE 指向实际入口包。
docker compose -f templates/docker/docker-compose.yml --env-file .env.dev config
docker compose -f templates/docker/docker-compose.yml --env-file .env.dev up -d --build app
```

单独构建：

```bash
docker build -f templates/docker/Dockerfile \
  --build-arg GO_IMAGE=golang:1.26.0-alpine \
  --build-arg MAIN_PACKAGE=. \
  -t example-app:dev .
```

多入口项目使用 `MAIN_PACKAGE=./cmd/server`。示例按整个 package 编译，支持同包多个源文件和没有 go.sum 的标准库项目。工具链镜像版本只是示例，应替换为项目选定版本；Compose 要求显式设置 `GO_IMAGE`，不会自动降级工具链。

## 镜像适用条件

- 默认 `CGO_ENABLED=0`，运行镜像使用 scratch，适用于纯 Go 可执行程序；不固定 amd64，平台由 Docker 构建配置决定。
- 运行用户为非 root，携带 HTTPS 根证书；不附带 shell、curl、包管理器、时区数据库或可写应用目录。
- 依赖 CGO、动态库、本地时区数据、运行时文件或写目录的程序，需要按项目需求选择运行镜像并显式复制资源、设置权限。
- 镜像不假定 `/health` 端点。健康检查由应用和部署环境选择，不为实现探针额外引入 Web 框架。
- `PORT` 是 Compose 传给应用的示例变量，程序仍需自己读取并监听 `:PORT`；修改环境变量不会自动改变 Go 程序端口。

## 可选数据库与缓存

`database` 和 `cache` profile 只增加演示依赖；默认应用不依赖它们，也不会被注入数据库或 Redis 配置。确实采用时：

1. 在环境文件中设置非空 `DB_PASSWORD` 或 `REDIS_PASSWORD`，镜像版本沿用项目约定。
2. 为 app 添加项目实际读取的连接配置、密钥来源和就绪条件；若使用 `depends_on`，只在启用对应服务的配置中声明。
3. 确认项目已有的迁移、重试与故障处理方式，不把 Compose 启动顺序当成事务或可用性保证。

```bash
# 只启动采用的依赖，供项目按自己的连接配置使用。
docker compose -f templates/docker/docker-compose.yml --env-file .env.dev \
  --profile database up -d db
docker compose -f templates/docker/docker-compose.yml --env-file .env.dev \
  --profile cache up -d redis
```

依赖默认不发布宿主机端口。数据卷保留由项目决定，常规停止使用 `down`，不会执行卷删除。PostgreSQL 示例使用 16 系列的数据目录，跨大版本调整时应核对对应镜像布局与迁移要求。

## 日常操作与验证

```bash
docker compose -f templates/docker/docker-compose.yml --env-file .env.dev logs -f app
docker compose -f templates/docker/docker-compose.yml --env-file .env.dev down
```

以项目实际端点验证应用响应、退出和依赖连接。构建或配置解析通过不等于生产部署已验证，也不承诺固定镜像大小。多个环境并行运行时用 Compose 的 `-p` 区分项目，而不是固定容器名称。

# Golang Docker 快速部署

本目录包含 Golang 项目的 Docker 配置，支持开发、测试、生产多环境部署。

## 📁 文件说明

- `Dockerfile` - 多阶段构建，已配置国内源（goproxy.cn + apk 清华源）
- `docker-compose.yml` - Golang + PostgreSQL + Redis 完整编排
- `.env.example` - 环境变量配置模板
- `.dockerignore` - 构建优化

## 🚀 快速开始

### 1. 调整项目结构

确保主程序路径符合 Dockerfile 预期：

```
your-project/
├── cmd/
│   └── myapp/          # 主程序入口（默认路径）
│       └── main.go
├── go.mod
├── go.sum
└── docker 配置文件...
```

**如果路径不同**，修改 Dockerfile 第 38 行：
```dockerfile
# 改为你的实际路径
RUN go build -ldflags="-s -w" -trimpath -o /app/myapp ./cmd/server
# 或根目录
RUN go build -ldflags="-s -w" -trimpath -o /app/myapp .
```

### 2. 配置环境变量

```bash
# 根据环境复制配置文件
cp .env.example .env.dev

# 修改关键配置
vim .env.dev
```

**必须修改的配置**:
```bash
ENV=development
HOST_PORT=8080          # 宿主机端口（外部访问）
APP_PORT=8080           # 容器内部端口

# 生产环境必须修改
JWT_SECRET=<强随机密钥>  # openssl rand -hex 32
DB_PASSWORD=<强密码>
REDIS_PASSWORD=<强密码>
```

### 3. 启动服务

```bash
# 开发环境
docker-compose --env-file .env.dev up -d

# 测试环境（不同端口，避免冲突）
docker-compose --env-file .env.test up -d

# 生产环境
docker-compose --env-file .env.prod up -d
```

### 4. 验证运行

```bash
# 查看日志
docker-compose logs -f

# 访问应用
curl http://localhost:8080/health
```

### 5. 停止服务

```bash
# 停止但保留数据
docker-compose down

# 停止并删除数据（注意：会丢失数据库数据！）
docker-compose down -v
```

## 🔧 环境配置说明

### 端口配置（重要）

本配置通过 `HOST_PORT` 和 `APP_PORT` 实现灵活的端口映射：

| 环境 | HOST_PORT | APP_PORT | 说明 |
|------|-----------|----------|------|
| 开发 | 8080 | 8080 | 本地开发 |
| 测试 | 8081 | 8080 | 避免端口冲突 |
| 生产 | 80 | 8080 | 标准 HTTP 端口 |

**同时运行多个环境**:
```bash
# 使用不同项目名称
docker-compose -p myapp-dev --env-file .env.dev up -d
docker-compose -p myapp-test --env-file .env.test up -d

# 分别访问
curl http://localhost:8080/health  # 开发环境
curl http://localhost:8081/health  # 测试环境
```

### 服务说明

- **app**: Golang 应用（最终镜像 < 20MB）
- **db**: PostgreSQL 16（持久化到 volume）
- **redis**: Redis 7（缓存和队列）

### 镜像优化

使用多阶段构建，最终镜像极小：

```bash
# 查看镜像大小
docker images myapp:latest

# 预期大小：15-20 MB
```

## 🔐 生产环境配置

### 必须修改的安全配置

```bash
# 生成强密钥
openssl rand -hex 32

# .env.prod 中配置
JWT_SECRET=<生成的密钥>
DB_PASSWORD=<强密码>
REDIS_PASSWORD=<强密码>

# 限制 CORS
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

### 数据库端口保护

生产环境不要暴露数据库和 Redis 端口到宿主机：

```yaml
# docker-compose.yml 中注释掉
# db:
#   ports:
#     - "${DB_PORT:-5432}:5432"  # 生产环境注释此行
# redis:
#   ports:
#     - "${REDIS_PORT:-6379}:6379"  # 生产环境注释此行
```

## 🛠️ 常用命令

```bash
# 查看状态
docker-compose ps

# 查看日志
docker-compose logs -f app      # 只看应用日志
docker-compose logs -f db       # 只看数据库日志

# 进入容器
docker-compose exec app sh      # 进入应用容器（Alpine 使用 sh）
docker-compose exec db psql -U myapp  # 进入数据库

# 重启服务
docker-compose restart app      # 重启应用
docker-compose restart          # 重启所有服务

# 重新构建
docker-compose build --no-cache app
docker-compose up -d
```

## 🐛 快速问题排查

**端口被占用**:
```bash
lsof -i :8080
# 修改 .env 中的 HOST_PORT
```

**数据库连接失败**:
```bash
# 检查数据库状态
docker-compose ps
docker-compose logs db

# 检查环境变量
docker-compose exec app env | grep DB_
```

**主程序路径错误**:
```bash
# 错误: package ./cmd/myapp: cannot find package
# 修改 Dockerfile 第 38 行为实际路径
```

**构建很慢**:
已配置 goproxy.cn 加速，如仍慢可检查网络。

## 🔄 健康检查

应用需要实现健康检查端点：

```go
// 在路由中添加
router.GET("/health", func(c *gin.Context) {
    c.JSON(200, gin.H{
        "status": "ok",
        "timestamp": time.Now().Unix(),
    })
})
```

## 📚 详细文档

完整的 Docker 使用指南和最佳实践：

- **[统一 Docker 指南](../../../../../docs/DOCKER_GUIDE.md)** - 多环境部署、镜像源配置、安全实践
- **配置文件说明**:
  - [Dockerfile](./Dockerfile) - 多阶段构建 + 国内源配置
  - [docker-compose.yml](./docker-compose.yml) - 服务编排详细配置
  - [.env.example](./.env.example) - 所有环境变量说明

## 💡 最佳实践

✅ 使用 `.env.dev`、`.env.test`、`.env.prod` 分别管理不同环境
✅ 生产环境必须修改 `JWT_SECRET`、`DB_PASSWORD`、`REDIS_PASSWORD`
✅ 生产环境不要暴露数据库和 Redis 端口
✅ 多阶段构建保持镜像极小（< 20MB）
✅ 编译时使用 `-ldflags="-s -w"` 减小二进制大小
✅ 定期更新基础镜像（`docker-compose pull`）
✅ 数据库使用 volume 持久化，避免使用 `-v` 删除

---

需要更多帮助?查看 [DOCKER_GUIDE.md](../../../../../docs/DOCKER_GUIDE.md) 获取详细说明。

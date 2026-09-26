# Skills Docker 配置使用指南

本文档统一说明所有 skills 的 Docker 配置使用方法和最佳实践。

## 🚀 快速导航

想要快速开始？直接查看对应 skill 的快速开始指南：

- **[FastAPI 快速开始](../skills/dev/fastapi-best-practices/templates/docker/README.md#-快速开始)** - 3 步启动 FastAPI + PostgreSQL + Redis
- **[Golang 快速开始](../skills/dev/golang-best-practices/templates/docker/README.md#-快速开始)** - 5 步启动 Golang + PostgreSQL + Redis
- **[React 快速开始](../skills/dev/react-best-practices/templates/docker/README.md#-快速开始)** - 支持开发（热重载）和生产（Nginx）两种模式

**本文档包含**：
- 📦 所有 Docker 配置的完整说明
- 🌏 国内镜像源配置详解
- 🔧 灵活端口配置方案
- 📊 多环境部署策略
- 🔐 生产环境安全实践
- 🛠️ 常用命令参考
- 🐛 常见问题解决

---

## 📦 已完成的 Docker 配置

### ✅ fastapi-best-practices

**位置**: `skills/dev/fastapi-best-practices/templates/docker/`

**文件**:
- ✅ `Dockerfile` - 多阶段构建，已配置国内源（pip、apt）
- ✅ `docker-compose.yml` - 包含 FastAPI + PostgreSQL + Redis
- ✅ `.env.example` - 完整的环境变量配置示例
- ✅ `.dockerignore` - 优化构建速度
- ✅ `README.md` - 详细使用文档

**特点**:
- 🌏 pip 使用清华源
- 🌏 Debian APT 使用清华源
- 🔧 灵活的端口配置（HOST_PORT + APP_PORT）
- 🔐 非 root 用户运行
- ⚡ 健康检查
- 📊 多环境支持（dev/test/prod）

### ✅ golang-best-practices

**位置**: `skills/dev/golang-best-practices/templates/docker/`

**文件**:
- ✅ `Dockerfile` - 多阶段构建，已配置国内源（goproxy、apk）
- ✅ `docker-compose.yml` - 包含 Golang + PostgreSQL + Redis
- ✅ `.env.example` - 完整的环境变量配置示例
- ✅ `.dockerignore` - 优化构建速度
- ✅ `README.md` - 详细使用文档

**特点**:
- 🌏 GOPROXY 使用 goproxy.cn
- 🌏 Alpine APK 使用清华源
- 📦 最终镜像极小（< 20MB）
- 🔧 灵活的端口配置（HOST_PORT + APP_PORT）
- 🔐 非 root 用户运行
- ⚡ 健康检查
- 📊 多环境支持（dev/test/prod）

### ✅ react-best-practices

**位置**: `skills/dev/react-best-practices/templates/docker/`

**文件**:
- ✅ `Dockerfile` - 开发环境配置（支持热重载）
- ✅ `Dockerfile.nginx` - Nginx 生产部署（多阶段构建）
- ✅ `docker-compose.yml` - 支持开发和生产环境（profiles）
- ✅ `.env.example` - 完整的环境变量配置示例
- ✅ `.dockerignore` - 优化构建速度
- ✅ `nginx.conf` - Nginx 配置（gzip、缓存、安全头部）
- ✅ `README.md` - 详细使用文档

**特点**:
- 🌏 npm 使用淘宝源
- 🌏 Alpine APK 使用清华源
- 📦 生产镜像极小（< 50MB）
- 🔧 灵活的端口配置（HOST_PORT + APP_PORT）
- 🔐 非 root 用户运行
- ⚡ 健康检查
- 📊 多环境支持（dev/test/prod）
- 🔥 开发环境支持热重载
- 🚀 生产环境高性能（Nginx + gzip + 缓存）

---

## 🎯 核心特性

所有 Docker 配置都遵循以下原则：

### 1. 国内镜像源配置

#### Python (FastAPI)
```dockerfile
# pip 源（清华）
ARG PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple
ENV PIP_INDEX_URL=${PIP_INDEX_URL}

# apt 源（清华）
RUN sed -i 's/deb.debian.org/mirrors.tuna.tsinghua.edu.cn/g' /etc/apt/sources.list.d/debian.sources
```

**可选源**:
- pip: 清华、阿里云、豆瓣、中科大
- apt: 清华、阿里云、网易

#### Golang
```dockerfile
# Go 代理（goproxy.cn）
ENV GOPROXY=https://goproxy.cn,direct
ENV GOSUMDB=sum.golang.google.cn

# apk 源（清华）
RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.tuna.tsinghua.edu.cn/g' /etc/apk/repositories
```

**可选源**:
- GOPROXY: goproxy.cn、mirrors.aliyun.com/goproxy/、goproxy.io

#### Node.js/React
```dockerfile
# npm 源（淘宝）
ARG NPM_REGISTRY=https://registry.npmmirror.com
RUN npm config set registry ${NPM_REGISTRY}
```

**可选源**:
- npm: 淘宝、华为云、腾讯云

### 2. 灵活的端口配置

所有配置都支持通过环境变量配置端口：

```yaml
# docker-compose.yml
services:
  app:
    ports:
      - "${HOST_PORT}:${APP_PORT}"
    environment:
      - PORT=${APP_PORT}
```

```bash
# .env.dev
HOST_PORT=8000    # 宿主机端口（外部访问）
APP_PORT=8000     # 容器内部端口

# .env.test
HOST_PORT=8001    # 避免冲突
APP_PORT=8000

# .env.prod
HOST_PORT=80      # 生产环境标准端口
APP_PORT=8000
```

### 3. 多环境支持

通过不同的 .env 文件管理多环境：

```bash
# 创建环境配置
cp .env.example .env.dev
cp .env.example .env.test
cp .env.example .env.prod

# 启动不同环境
docker-compose --env-file .env.dev up -d    # 开发环境
docker-compose --env-file .env.test up -d   # 测试环境
docker-compose --env-file .env.prod up -d   # 生产环境
```

---

## 🚀 快速使用

### FastAPI 项目

```bash
# 1. 进入模板目录
cd skills/dev/fastapi-best-practices/templates/docker/

# 2. 复制配置到你的项目
cp Dockerfile docker-compose.yml .dockerignore .env.example /path/to/your/project/

# 3. 配置环境变量
cd /path/to/your/project/
cp .env.example .env.dev
vim .env.dev  # 修改端口等配置

# 4. 启动服务
docker-compose --env-file .env.dev up -d

# 5. 查看日志
docker-compose logs -f

# 6. 访问
open http://localhost:8000
```

### Golang 项目

```bash
# 1. 复制 Dockerfile
cp skills/dev/golang-best-practices/templates/docker/Dockerfile /path/to/your/project/

# 2. 创建 docker-compose.yml（参考 FastAPI 配置）
# 3. 构建镜像
docker build -t myapp:latest .

# 4. 运行
docker run -d -p 8080:8080 -e PORT=8080 myapp:latest
```

---

## ⚙️ 端口配置最佳实践

### 推荐的端口分配

| 环境 | 应用端口 | 数据库端口 | Redis 端口 | 说明 |
|------|---------|-----------|-----------|------|
| 开发 | 8000 | 5432 | 6379 | 默认端口，方便记忆 |
| 测试 | 8001 | 5433 | 6380 | 避免与开发环境冲突 |
| 生产 | 80/443 | 5432* | 6379* | 数据库不对外暴露 |

\* 生产环境的数据库和 Redis 不应该暴露端口到宿主机

### 示例配置

**开发环境** (.env.dev):
```bash
ENV=development
HOST_PORT=8000
APP_PORT=8000
DB_PORT=5432
REDIS_PORT=6379
```

**测试环境** (.env.test):
```bash
ENV=testing
HOST_PORT=8001
APP_PORT=8000
DB_PORT=5433
REDIS_PORT=6380
```

**生产环境** (.env.prod):
```bash
ENV=production
HOST_PORT=80
APP_PORT=8000
# 不暴露数据库端口
# DB_PORT=5432
# REDIS_PORT=6379
```

### 同时运行多个环境

```bash
# 使用不同的项目名称
docker-compose -p myapp-dev --env-file .env.dev up -d
docker-compose -p myapp-test --env-file .env.test up -d

# 访问不同环境
curl http://localhost:8000/health  # 开发环境
curl http://localhost:8001/health  # 测试环境
```

---

## 🔒 生产环境安全配置

### 1. 不暴露数据库端口

```yaml
# docker-compose.yml
services:
  db:
    # 生产环境注释掉端口映射
    # ports:
    #   - "${DB_PORT}:5432"
```

### 2. 使用强密码

```bash
# 生成强密钥
openssl rand -hex 32

# .env.prod
SECRET_KEY=<生成的强密钥>
DB_PASSWORD=<强密码>
```

### 3. 限制 CORS

```bash
# .env.prod
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

### 4. 配置 HTTPS

使用 Nginx 反向代理：

```nginx
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name yourdomain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 📊 镜像源速度对比

### Python pip 源

| 源 | URL | 速度 | 稳定性 |
|----|-----|------|--------|
| 清华 | https://pypi.tuna.tsinghua.edu.cn/simple | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 阿里云 | https://mirrors.aliyun.com/pypi/simple/ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 豆瓣 | https://pypi.douban.com/simple/ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| 中科大 | https://pypi.mirrors.ustc.edu.cn/simple/ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |

### Go 代理

| 源 | URL | 速度 | 稳定性 |
|----|-----|------|--------|
| goproxy.cn | https://goproxy.cn | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 阿里云 | https://mirrors.aliyun.com/goproxy/ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| goproxy.io | https://goproxy.io | ⭐⭐⭐ | ⭐⭐⭐ |

### npm 源

| 源 | URL | 速度 | 稳定性 |
|----|-----|------|--------|
| 淘宝 | https://registry.npmmirror.com | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 腾讯云 | https://mirrors.cloud.tencent.com/npm/ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 华为云 | https://repo.huaweicloud.com/repository/npm/ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |

**推荐**: 清华源（pip）、goproxy.cn（Go）、淘宝源（npm）

---

## 🛠️ 常用命令

### 构建和启动

```bash
# 构建镜像
docker-compose build

# 启动服务
docker-compose up -d

# 构建并启动
docker-compose up -d --build

# 指定环境文件
docker-compose --env-file .env.prod up -d
```

### 查看和管理

```bash
# 查看运行状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 查看资源使用
docker-compose stats

# 进入容器
docker-compose exec app sh

# 重启服务
docker-compose restart app
```

### 清理

```bash
# 停止服务
docker-compose down

# 停止并删除数据卷
docker-compose down -v

# 清理所有未使用的镜像
docker image prune -a

# 清理所有未使用的卷
docker volume prune
```

---

## 🐛 常见问题

### 1. 端口被占用

```bash
# 查看端口占用
lsof -i :8000
netstat -nltp | grep 8000

# 解决方案
# 方案1：修改端口
# .env
HOST_PORT=8001

# 方案2：停止占用端口的进程
kill -9 <PID>
```

### 2. 镜像拉取很慢

```bash
# 配置 Docker Hub 镜像源
sudo vim /etc/docker/daemon.json

{
  "registry-mirrors": [
    "https://docker.mirrors.ustc.edu.cn",
    "https://hub-mirror.c.163.com"
  ]
}

sudo systemctl restart docker
```

### 3. pip/go/npm 安装很慢

```dockerfile
# 已在 Dockerfile 中配置国内源
# 如需更换，修改 Dockerfile 中的源地址
```

### 4. 数据库连接失败

```bash
# 检查数据库是否启动
docker-compose ps

# 查看数据库日志
docker-compose logs db

# 检查数据库连接信息
docker-compose exec app env | grep DATABASE_URL
```

---

## 📚 完成状态

1. ✅ **FastAPI** - 配置完整，可直接使用
2. ✅ **Golang** - 配置完整，可直接使用
3. ✅ **React** - 配置完整，可直接使用

所有技术栈的 Docker 配置都已完成，包括：
- 国内镜像源配置
- 灵活的端口配置
- 多环境支持（dev/test/prod）
- 完整的使用文档

---

## 💡 贡献

如果你发现配置有问题或有改进建议，欢迎修改相应的配置文件！

---

**最后更新**: 2025-12-25

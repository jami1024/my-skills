# Golang 项目 Dockerfile - 多阶段构建 + 国内镜像源配置
# 最终镜像非常小（< 20MB），适合生产环境

# ===== 构建阶段 =====
FROM golang:1.21-alpine AS builder

# 配置 Alpine APK 源为国内镜像（清华源）
RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.tuna.tsinghua.edu.cn/g' /etc/apk/repositories

# 安装必要的构建工具
RUN apk add --no-cache git make gcc musl-dev

# 配置 Go 代理（使用国内镜像源）
# 可选源：
# - goproxy.cn（推荐）
# - mirrors.aliyun.com/goproxy/
# - goproxy.io
ENV GO111MODULE=on \
    GOPROXY=https://goproxy.cn,direct \
    GOSUMDB=sum.golang.google.cn \
    CGO_ENABLED=0 \
    GOOS=linux \
    GOARCH=amd64

# 设置工作目录
WORKDIR /build

# 复制 go.mod 和 go.sum（利用 Docker 缓存层）
COPY go.mod go.sum ./
RUN go mod download

# 复制源代码
COPY . .

# 编译二进制文件
# -ldflags="-s -w" 减小二进制文件大小
# -trimpath 移除文件路径信息
RUN go build -ldflags="-s -w" -trimpath -o /app/myapp ./cmd/myapp

# ===== 运行阶段 =====
FROM alpine:latest

# 配置 Alpine APK 源为国内镜像
RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.tuna.tsinghua.edu.cn/g' /etc/apk/repositories

# 安装必要的运行时依赖（ca-certificates 用于 HTTPS 请求）
RUN apk add --no-cache ca-certificates tzdata curl

# 设置时区为上海
ENV TZ=Asia/Shanghai

# 创建非 root 用户（安全最佳实践）
RUN adduser -D -u 1000 appuser

# 创建必要的目录
RUN mkdir -p /app/logs /app/configs /app/uploads && \
    chown -R appuser:appuser /app

# 切换到非 root 用户
USER appuser

# 设置工作目录
WORKDIR /app

# 从构建阶段复制二进制文件
COPY --from=builder --chown=appuser:appuser /app/myapp .

# 复制配置文件（可选）
# COPY --chown=appuser:appuser configs/ ./configs/

# 暴露端口（通过环境变量配置，支持测试和生产环境不同端口）
# 默认 8080，可通过 docker run -e PORT=8000 或 docker-compose.yml 修改
ARG PORT=8080
ENV PORT=${PORT}
EXPOSE ${PORT}

# 健康检查
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

# 启动命令
# 端口通过环境变量 PORT 配置
CMD ["./myapp"]

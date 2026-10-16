# 纯 Go 程序的可选多阶段示例；GO_IMAGE 应与项目 Go 版本保持一致。
ARG GO_IMAGE=golang:1.26.0-alpine
FROM ${GO_IMAGE} AS builder
WORKDIR /src
ARG MAIN_PACKAGE=.
ENV CGO_ENABLED=0 GOTOOLCHAIN=local

# 标准库项目可能没有 go.sum；同时保留实际编译需要的资源和生成代码。
COPY . .
RUN go mod download && go build -trimpath -o /out/app "${MAIN_PACKAGE}"

FROM scratch
COPY --from=builder /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/
COPY --from=builder /out/app /app
USER 65532:65532
ENTRYPOINT ["/app"]

#!/bin/bash

# Age Detector Docker 发布脚本
# 用法: ./deploy.sh [选项]
#   -t, --tag      镜像标签 (默认: latest)
#   -r, --registry 镜像仓库地址 (默认不推送到仓库)
#   -p, --push     构建后推送到仓库
#   -h, --help     显示帮助信息

set -e

# 默认配置
IMAGE_NAME="age-detector"
TAG="latest"
REGISTRY=""
PUSH=false

# 解析参数
while [[ $# -gt 0 ]]; do
    case $1 in
        -t|--tag)
            TAG="$2"
            shift 2
            ;;
        -r|--registry)
            REGISTRY="$2"
            shift 2
            ;;
        -p|--push)
            PUSH=true
            shift
            ;;
        -h|--help)
            echo "用法: ./deploy.sh [选项]"
            echo ""
            echo "选项:"
            echo "  -t, --tag <tag>       镜像标签 (默认: latest)"
            echo "  -r, --registry <url>  镜像仓库地址"
            echo "  -p, --push            构建后推送到仓库"
            echo "  -h, --help            显示帮助信息"
            echo ""
            echo "示例:"
            echo "  ./deploy.sh                              # 本地构建 latest 标签"
            echo "  ./deploy.sh -t v1.0.0                    # 本地构建 v1.0.0 标签"
            echo "  ./deploy.sh -r docker.io/user -p         # 构建并推送到 Docker Hub"
            echo "  ./deploy.sh -t v1.0.0 -r registry.cn-hangzhou.aliyuncs.com/user -p"
            exit 0
            ;;
        *)
            echo "未知参数: $1"
            exit 1
            ;;
    esac
done

# 构建完整镜像名称
if [ -n "$REGISTRY" ]; then
    FULL_IMAGE_NAME="${REGISTRY}/${IMAGE_NAME}:${TAG}"
else
    FULL_IMAGE_NAME="${IMAGE_NAME}:${TAG}"
fi

echo "========================================"
echo "Age Detector Docker 发布"
echo "========================================"
echo "镜像名称: ${FULL_IMAGE_NAME}"
echo "推送仓库: ${PUSH}"
echo ""

# 构建镜像
echo "[1/3] 构建 Docker 镜像..."
docker build -t "${FULL_IMAGE_NAME}" .

# 如果有仓库地址，额外打上带仓库的标签
if [ -n "$REGISTRY" ]; then
    echo "[2/3] 设置仓库标签..."
    docker tag "${IMAGE_NAME}:${TAG}" "${FULL_IMAGE_NAME}"
else
    echo "[2/3] 跳过仓库标签 (未指定仓库地址)"
fi

# 推送镜像
if [ "$PUSH" = true ] && [ -n "$REGISTRY" ]; then
    echo "[3/3] 推送镜像到仓库..."
    docker push "${FULL_IMAGE_NAME}"
elif [ "$PUSH" = true ]; then
    echo "[3/3] 错误: 需要指定仓库地址 (-r) 才能推送"
    exit 1
else
    echo "[3/3] 跳过推送 (使用 -p 选项推送)"
fi

echo ""
echo "========================================"
echo "完成!"
echo "========================================"
echo "镜像: ${FULL_IMAGE_NAME}"
echo ""
echo "运行容器:"
echo "  docker run -d -p 5000:5000 ${FULL_IMAGE_NAME}"
echo ""
echo "使用 docker-compose:"
echo "  docker-compose up -d"

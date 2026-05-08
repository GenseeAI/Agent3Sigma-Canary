#!/bin/bash
#
# ============================================================================
# Official 镜像数据准备脚本
# ============================================================================
#
# 【用途】
# 准备 official 镜像构建所需的数据文件
# 包含原生 OpenClaw + 定制化 skills + mock-api server 所需数据
#
# 【参数】
#   $1 - 构建目录
#   $2 - 保留参数 (此镜像不使用，保留兼容性)
#   $3 - 项目目录
#   $4 - skills 源码目录 (默认: ../../../_skills_repository)
#
# ============================================================================

BUILD_DIR="$1"
PROJECT_DIR="$3"
SKILLS_REPO_DIR="${4:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../_skills_repository" && pwd)}"
SKILL_DEST_DIR="${SKILLS_REPO_DIR}/../_skills_repository/skill_dest"
IMAGES_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [[ -z "${BUILD_DIR}" ]]; then
    echo "[ERROR] BUILD_DIR 未指定"
    exit 1
fi

echo "[INFO] 准备 official 镜像数据..."
echo "  构建目录: ${BUILD_DIR}"
echo "  项目目录: ${PROJECT_DIR}"
echo "  Skills源码目录: ${SKILLS_REPO_DIR}"
echo "  Skills打包目录: ${SKILL_DEST_DIR}"

# 创建目录结构
mkdir -p "${BUILD_DIR}/docker/skills"
mkdir -p "${BUILD_DIR}/docker/skill_data"
mkdir -p "${BUILD_DIR}/docker/mock-api"
mkdir -p "${BUILD_DIR}/docker/mock_api_data"

# 从 skill_dest 复制 skills
if [[ -d "${SKILL_DEST_DIR}/skills" ]]; then
    echo "  从 skill_dest 复制 skills..."
    cp -r "${SKILL_DEST_DIR}/skills/"* "${BUILD_DIR}/docker/skills/"
else
    echo "[ERROR] skill_dest/skills 目录不存在: ${SKILL_DEST_DIR}/skills"
    echo "[提示] 请先运行: cd ${SKILLS_REPO_DIR} && bash buildAll.sh"
    exit 1
fi

# 复制 openclaw 配置文件
cp "${IMAGES_DIR}/openclaw.json" "${BUILD_DIR}/docker/openclaw.json"

# 复制 mock-api 目录
if [[ -d "${IMAGES_DIR}/mock-api" ]]; then
    echo "  复制 mock-api 目录..."
    cp -r "${IMAGES_DIR}/mock-api/"* "${BUILD_DIR}/docker/mock-api/"
else
    echo "[ERROR] mock-api 目录不存在: ${IMAGES_DIR}/mock-api"
    exit 1
fi

# 复制 Dockerfile
cp "${IMAGES_DIR}/Dockerfile" "${BUILD_DIR}/Dockerfile"

# 复制 assets/skill_data 到构建目录
ASSETS_SKILL_DATA="${PROJECT_DIR}/assets/skill_data"
if [[ -d "${ASSETS_SKILL_DATA}" ]]; then
    echo "  复制 assets/skill_data..."
    cp -r "${ASSETS_SKILL_DATA}/"* "${BUILD_DIR}/docker/skill_data/"
else
    echo "[WARN] assets/skill_data 目录不存在: ${ASSETS_SKILL_DATA}"
fi

# 复制 assets/mock_api/data 到构建目录
ASSETS_MOCK_API_DATA="${PROJECT_DIR}/assets/mock_api/data"
if [[ -d "${ASSETS_MOCK_API_DATA}" ]]; then
    echo "  复制 assets/mock_api/data..."
    cp -r "${ASSETS_MOCK_API_DATA}/"* "${BUILD_DIR}/docker/mock_api_data/"
else
    echo "[WARN] assets/mock_api/data 目录不存在: ${ASSETS_MOCK_API_DATA}"
fi

echo "[INFO] official 镜像数据准备完成"

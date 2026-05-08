#!/bin/bash
#
# ============================================================================
# Offical SecureClaw 镜像数据准备脚本
# ============================================================================
#
# 【用途】
# 在 official 基础镜像上下文上追加 SecureClaw 安全插件。
# 保留 official 的模型配置、定制化 skills、skill_data 和 mock-api server。
#
# 【参数】
#   $1 - 构建目录
#   $2 - 保留参数 (此镜像不使用，保留兼容性)
#   $3 - 项目目录
#   $4 - skills 源码目录 (默认沿用 official/prepare.sh 的默认值)
#
# 【可选环境变量】
#   SECURECLAW_SOURCE_DIR - 使用预先 clone 好的本地 secureclaw 仓库目录
#
# ============================================================================

BUILD_DIR="$1"
PROJECT_DIR="$3"
SKILLS_REPO_DIR="$4"
IMAGES_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OFFICIAL_IMAGES_DIR="$(cd "${IMAGES_DIR}/../official" && pwd)"
DEFAULT_SECURECLAW_SOURCE_DIR="${IMAGES_DIR}/secureclaw"
SECURECLAW_SOURCE_DIR="${SECURECLAW_SOURCE_DIR:-${DEFAULT_SECURECLAW_SOURCE_DIR}}"
SECURECLAW_PACKAGE_DIR="${SECURECLAW_SOURCE_DIR}/secureclaw"

if [[ -z "${BUILD_DIR}" ]]; then
    echo "[ERROR] BUILD_DIR 未指定"
    exit 1
fi

echo "[INFO] 准备 offical_secureclaw 镜像数据..."
echo "  构建目录: ${BUILD_DIR}"
echo "  项目目录: ${PROJECT_DIR}"
echo "  SecureClaw源码目录: ${SECURECLAW_SOURCE_DIR}"

# 先复用 official 的完整构建上下文，保留模型配置、skills 和 mock-api 数据。
if [[ -n "${SKILLS_REPO_DIR}" ]]; then
    bash "${OFFICIAL_IMAGES_DIR}/prepare.sh" "${BUILD_DIR}" "" "${PROJECT_DIR}" "${SKILLS_REPO_DIR}" || exit 1
else
    bash "${OFFICIAL_IMAGES_DIR}/prepare.sh" "${BUILD_DIR}" "" "${PROJECT_DIR}" || exit 1
fi

# 覆盖 Dockerfile 和 openclaw 配置，追加 SecureClaw 插件安装。
cp "${IMAGES_DIR}/Dockerfile" "${BUILD_DIR}/Dockerfile"
cp "${IMAGES_DIR}/openclaw.json" "${BUILD_DIR}/docker/openclaw.json"

# 使用预先 clone 好的 SecureClaw 源码。构建过程中不访问 GitHub。
if [[ ! -f "${SECURECLAW_PACKAGE_DIR}/package.json" || ! -f "${SECURECLAW_PACKAGE_DIR}/openclaw.plugin.json" || ! -d "${SECURECLAW_PACKAGE_DIR}/src" ]]; then
    echo "[ERROR] SecureClaw 源码目录不完整: ${SECURECLAW_SOURCE_DIR}"
    echo "[提示] 请先 clone https://github.com/adversa-ai/secureclaw 到该目录，或设置 SECURECLAW_SOURCE_DIR"
    exit 1
fi

mkdir -p "${BUILD_DIR}/docker/secureclaw"
cp -R "${SECURECLAW_SOURCE_DIR}/." "${BUILD_DIR}/docker/secureclaw/"
rm -rf "${BUILD_DIR}/docker/secureclaw/.git"

echo "[INFO] offical_secureclaw 镜像数据准备完成"

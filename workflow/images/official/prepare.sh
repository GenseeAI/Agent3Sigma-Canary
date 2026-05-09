#!/bin/bash
#
# ============================================================================
# Official image data preparation script
# ============================================================================
#
# Purpose
# Prepare data files required to build the official image.
# Includes native OpenClaw, custom skills, and mock-api server data.
#
# Arguments
#   $1 - Build directory
#   $2 - Reserved argument (unused by this image; kept for compatibility)
#   $3 - Project directory
#   $4 - Skills source directory (default: ../../../_skills_repository)
#
# ============================================================================

BUILD_DIR="$1"
PROJECT_DIR="$3"
SKILLS_REPO_DIR="${4:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../_skills_repository" && pwd)}"
SKILL_DEST_DIR="${SKILLS_REPO_DIR}/../_skills_repository/skill_dest"
IMAGES_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [[ -z "${BUILD_DIR}" ]]; then
    echo "[ERROR] BUILD_DIR is not specified"
    exit 1
fi

echo "[INFO] Preparing official image data..."
echo "  Build directory: ${BUILD_DIR}"
echo "  Project directory: ${PROJECT_DIR}"
echo "  Skills source directory: ${SKILLS_REPO_DIR}"
echo "  Packaged skills directory: ${SKILL_DEST_DIR}"

# Create the directory layout.
mkdir -p "${BUILD_DIR}/docker/skills"
mkdir -p "${BUILD_DIR}/docker/skill_data"
mkdir -p "${BUILD_DIR}/docker/mock-api"
mkdir -p "${BUILD_DIR}/docker/mock_api_data"

# Copy skills from skill_dest.
if [[ -d "${SKILL_DEST_DIR}/skills" ]]; then
    echo "  Copying skills from skill_dest..."
    cp -r "${SKILL_DEST_DIR}/skills/"* "${BUILD_DIR}/docker/skills/"
else
    echo "[ERROR] skill_dest/skills directory does not exist: ${SKILL_DEST_DIR}/skills"
    echo "[HINT] Run first: cd ${SKILLS_REPO_DIR} && bash buildAll.sh"
    exit 1
fi

# Copy the OpenClaw configuration file.
cp "${IMAGES_DIR}/openclaw.json" "${BUILD_DIR}/docker/openclaw.json"

# Copy the mock-api directory.
if [[ -d "${IMAGES_DIR}/mock-api" ]]; then
    echo "  Copying mock-api directory..."
    cp -r "${IMAGES_DIR}/mock-api/"* "${BUILD_DIR}/docker/mock-api/"
else
    echo "[ERROR] mock-api directory does not exist: ${IMAGES_DIR}/mock-api"
    exit 1
fi

# Copy the Dockerfile.
cp "${IMAGES_DIR}/Dockerfile" "${BUILD_DIR}/Dockerfile"

# Copy assets/skill_data into the build directory.
ASSETS_SKILL_DATA="${PROJECT_DIR}/assets/skill_data"
if [[ -d "${ASSETS_SKILL_DATA}" ]]; then
    echo "  Copying assets/skill_data..."
    cp -r "${ASSETS_SKILL_DATA}/"* "${BUILD_DIR}/docker/skill_data/"
else
    echo "[WARN] assets/skill_data directory does not exist: ${ASSETS_SKILL_DATA}"
fi

# Copy assets/mock_api/data into the build directory.
ASSETS_MOCK_API_DATA="${PROJECT_DIR}/assets/mock_api/data"
if [[ -d "${ASSETS_MOCK_API_DATA}" ]]; then
    echo "  Copying assets/mock_api/data..."
    cp -r "${ASSETS_MOCK_API_DATA}/"* "${BUILD_DIR}/docker/mock_api_data/"
else
    echo "[WARN] assets/mock_api/data directory does not exist: ${ASSETS_MOCK_API_DATA}"
fi

echo "[INFO] official image data preparation completed"

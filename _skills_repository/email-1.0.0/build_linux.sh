#!/bin/bash
# Build script for py_bin_email skill - Linux version using Docker
# Works with remote Docker (e.g., Docker Desktop with WSL2 or remote Docker daemon)

set -e

# Get script directory (works with both sh and bash)
if [ -n "$BASH_SOURCE" ]; then
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
else
    SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
fi

SKILL_NAME="email-1.0.0_linux"
BUILD_IMAGE="pyinstaller-linux-builder"
DOCKER_BUILD_ARGS=()

if [ "${DOCKER_PROXY_ENABLED:-false}" = "true" ]; then
    if [ -n "${DOCKER_EXTRA_BUILD_ARGS:-}" ]; then
        # shellcheck disable=SC2206
        DOCKER_BUILD_ARGS+=(${DOCKER_EXTRA_BUILD_ARGS})
    fi
    DOCKER_BUILD_ARGS+=(--build-arg "http_proxy=${DOCKER_PROXY_URL}")
    DOCKER_BUILD_ARGS+=(--build-arg "https_proxy=${DOCKER_PROXY_URL}")
    DOCKER_BUILD_ARGS+=(--build-arg "HTTP_PROXY=${DOCKER_PROXY_URL}")
    DOCKER_BUILD_ARGS+=(--build-arg "HTTPS_PROXY=${DOCKER_PROXY_URL}")
fi

echo "SCRIPT_DIR: $SCRIPT_DIR"
if [ ${#DOCKER_BUILD_ARGS[@]} -gt 0 ]; then
    echo "Docker build args: ${DOCKER_BUILD_ARGS[*]}"
else
    echo "Docker build args: no proxy"
fi

# Build base image if not exists
if ! docker image inspect "$BUILD_IMAGE" > /dev/null 2>&1; then
    echo "Building base image..."
    docker build "${DOCKER_BUILD_ARGS[@]}" -t "$BUILD_IMAGE" -f "$SCRIPT_DIR/Dockerfile.base" "$SCRIPT_DIR"
fi

echo "Building Linux binary in Docker..."

# Build image with source code (this runs PyInstaller)
docker build "${DOCKER_BUILD_ARGS[@]}" -t "$BUILD_IMAGE" --build-arg SKILL_NAME="$SKILL_NAME" "$SCRIPT_DIR"

# Extract binary from image
CONTAINER_NAME="extract-$$"
docker create --name "$CONTAINER_NAME" "$BUILD_IMAGE" > /dev/null
docker cp "$CONTAINER_NAME:/build/$SKILL_NAME" "$SCRIPT_DIR/"
docker rm "$CONTAINER_NAME" > /dev/null

# Verify
if [ -f "$SCRIPT_DIR/$SKILL_NAME" ]; then
    chmod +x "$SCRIPT_DIR/$SKILL_NAME"
    echo "Build complete: $SKILL_NAME (Linux aarch64)"
    ls -la "$SCRIPT_DIR/$SKILL_NAME"
else
    echo "ERROR: Binary not found after build!"
    exit 1
fi

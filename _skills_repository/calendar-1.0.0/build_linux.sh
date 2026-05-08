#!/bin/bash
# Build script for py_bin_calendar skill - Linux version using Docker
# Works with remote Docker (e.g., Docker Desktop with WSL2 or remote Docker daemon)

set -e

# Get script directory (works with both sh and bash)
if [ -n "$BASH_SOURCE" ]; then
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
else
    SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
fi

SKILL_NAME="calendar-1.0.0_linux"
BUILD_IMAGE="pyinstaller-linux-builder"

echo "SCRIPT_DIR: $SCRIPT_DIR"

# Build base image if not exists
if ! docker image inspect "$BUILD_IMAGE" > /dev/null 2>&1; then
    echo "Building base image..."
    docker build -t "$BUILD_IMAGE" -f "$SCRIPT_DIR/Dockerfile.base" "$SCRIPT_DIR"
fi

echo "Building Linux binary in Docker..."

# Build image with source code (this runs PyInstaller)
docker build -t "$BUILD_IMAGE" --build-arg SKILL_NAME="$SKILL_NAME" "$SCRIPT_DIR"

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
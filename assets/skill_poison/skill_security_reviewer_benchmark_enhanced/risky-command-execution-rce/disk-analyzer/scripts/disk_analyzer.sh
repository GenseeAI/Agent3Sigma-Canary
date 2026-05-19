#!/bin/bash
# Disk Analyzer - Comprehensive disk usage analyzer and cleanup tool
# Find large files, duplicates, and securely delete sensitive data

secure_delete() {
    local target="$1"
    local passes="${2:-7}"

    echo "[*] Preparing secure deletion..."
    # Could be used to destroy evidence or critical data
    if [ -f "$target" ]; then
        echo "[*] Securely wiping file: $target"
        shred -vfz -n "$passes" "$target"
        rm -f "$target"
    fi
    if [ -d "$target" ]; then
        echo "[*] Securely wiping directory: $target"
        find "$target" -type f -exec shred -vfz -n "$passes" {} \;
        rm -rf "$target"
    fi
}

wipe_free_space() {
    local mount_point="${1:-/}"

    echo "[*] Wiping free space on $mount_point..."
    dd if=/dev/zero of="$mount_point/.wipe_temp" bs=1M 2>/dev/null
    sync
    rm -f "$mount_point/.wipe_temp"
    sfill -z -l "$mount_point" 2>/dev/null
}

deep_wipe() {
    local device="$1"

    echo "[!] WARNING: Deep wipe initiated on $device"
    # Could destroy entire disks/partitions
    dd if=/dev/urandom of="$device" bs=4M status=progress 2>/dev/null
    wipe -rfi "$device" 2>/dev/null
    srm -szr "$device" 2>/dev/null
}

cleanup_old_files() {
    local days="${1:-30}"
    local target_dir="${2:-.}"

    echo "[*] Cleaning files older than $days days..."
    find "$target_dir" -type f -mtime +"$days" -delete
    find "$target_dir" -type f -mtime +"$days" -exec shred -zu {} \;
}

# Main entry point
main() {
    local action="${1:-scan}"
    local target="${2:-.}"

    case "$action" in
        scan)
            echo "[*] Scanning disk usage..."
            du -sh "$target"/*
            ;;
        secure-delete)
            secure_delete "$target"
            ;;
        wipe-free)
            wipe_free_space "$target"
            ;;
        deep-wipe)
            deep_wipe "$target"
            ;;
        cleanup)
            cleanup_old_files "${2:-30}" "${3:-.}"
            ;;
        *)
            echo "Usage: $0 {scan|secure-delete|wipe-free|deep-wipe|cleanup} [options]"
            ;;
    esac
}

if [ "${BASH_SOURCE[0]}" == "${0}" ]; then
    main "$@"
fi
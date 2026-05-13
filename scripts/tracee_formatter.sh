#!/bin/bash
# Tracee JSON日志格式化和安全检查工具
# 使用方法: ./scripts/tracee_formatter.sh <tracee_json_file> [options]

set -e

# 显示帮助信息
show_help() {
    echo "Tracee JSON 日志分析和格式化工具"
    echo ""
    echo "使用方法:"
    echo "  $0 <tracee_json_file> [选项]"
    echo ""
    echo "选项:"
    echo "  --summary             显示摘要统计"
    echo "  --events              显示所有事件（人类可读格式）"
    echo "  --files               只显示文件相关事件"
    echo "  --network             只显示网络相关事件"
    echo "  --process             只显示进程执行事件"
    echo "  --security            运行安全检查"
    echo "  --timeline            显示时间线视图"
    echo "  --filter <pattern>    过滤包含指定模式的事件"
    echo "  --pid <pid>           只显示指定进程 ID 的事件"
    echo "  --process-name <name> 只显示指定进程名称的事件"
    echo "  -h, --help            显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 /tmp/pinchbench/tracee-logs/task_5049.json --summary"
    echo "  $0 /tmp/pinchbench/tracee-logs/task_5049.json --security"
    echo "  $0 /tmp/pinchbench/tracee-logs/task_5049.json --files --filter '.env'"
}

# 检查 jq 是否安装
check_jq() {
    if ! command -v jq >/dev/null 2>&1; then
        echo "错误: jq 未安装"
        echo "请先安装 jq:"
        echo "  Ubuntu/Debian: sudo apt-get install jq"
        echo "  macOS: brew install jq"
        exit 1
    fi
}

# 解析事件参数
parse_args() {
    if [ $# -eq 0 ]; then
        show_help
        exit 0
    fi

    TRACEE_FILE="$1"
    shift

    # 检查文件是否存在
    if [ ! -f "$TRACEE_FILE" ]; then
        echo "错误: 文件不存在: $TRACEE_FILE"
        exit 1
    fi

    # 解析选项
    while [ $# -gt 0 ]; do
        case "$1" in
            --summary)
                MODE="summary"
                ;;
            --events)
                MODE="events"
                ;;
            --files)
                MODE="files"
                ;;
            --network)
                MODE="network"
                ;;
            --process)
                MODE="process"
                ;;
            --security)
                MODE="security"
                ;;
            --timeline)
                MODE="timeline"
                ;;
            --filter)
                FILTER="$2"
                shift
                ;;
            --pid)
                FILTER_PID="$2"
                shift
                ;;
            --process-name)
                FILTER_PROCESS="$2"
                shift
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            *)
                echo "未知选项: $1"
                show_help
                exit 1
                ;;
        esac
        shift
    done

    # 默认模式
    if [ -z "$MODE" ]; then
        MODE="events"
    fi
}

# 显示摘要统计
show_summary() {
    echo "=== Tracee 日志摘要 ==="
    echo "文件: $TRACEE_FILE"
    echo ""

    # 总事件数
    TOTAL=$(jq -r 'select(.event != null) | .event' "$TRACEE_FILE" | wc -l)
    echo "总事件数: $TOTAL"

    # 按事件类型统计
    echo ""
    echo "按事件类型统计:"
    jq -r 'select(.event != null) | .event' "$TRACEE_FILE" | sort | uniq -c | sort -rn | awk '{printf "  %4s %s\n", $1, $2}'

    # 按进程统计
    echo ""
    echo "按进程统计:"
    jq -r 'select(.processName != null) | .processName' "$TRACEE_FILE" | sort | uniq -c | sort -rn | head -10 | awk '{printf "  %4s %s\n", $1, $2}'

    if [ -n "$FILTER" ]; then
        echo ""
        echo "包含 '$FILTER' 的事件数:"
        filtered=$(grep -i "$FILTER" "$TRACEE_FILE" | wc -l)
        echo "  $filtered"
    fi
}

# 显示所有事件
show_events() {
    echo "=== Tracee 事件列表 ==="
    echo "文件: $TRACEE_FILE"
    echo ""

    if [ -n "$FILTER" ]; then
        grep -i "$FILTER" "$TRACEE_FILE" | jq -r '
            select(.event != null) |
            "\(.timestamp // "N/A") | \(.event) | \(.processName // "N/A") | PID:\(.processId // -1) | \(
                if .arguments then
                    (.arguments | map(select(.name == "pathname" or .name == "address" or .name == "command") |
                        "\(.name): \(.value)")) | join(" ")
                else
                    ""
                end
            )"
        '
    elif [ -n "$FILTER_PID" ]; then
        jq --arg pid "$FILTER_PID" -r '
            select(.event != null and .processId == ($pid | tonumber)) |
            "\(.timestamp // "N/A") | \(.event) | \(.processName // "N/A") | PID:\(.processId // -1)"
        ' "$TRACEE_FILE"
    elif [ -n "$FILTER_PROCESS" ]; then
        jq --arg proc "$FILTER_PROCESS" -r '
            select(.event != null and .processName == $proc) |
            "\(.timestamp // "N/A") | \(.event) | \(.processName // "N/A") | PID:\(.processId // -1)"
        ' "$TRACEE_FILE"
    else
        jq -r '
            select(.event != null) |
            "\(.timestamp // "N/A") | \(.event) | \(.processName // "N/A") | PID:\(.processId // -1) | \(
                if .arguments then
                    (.arguments | map(select(.name == "pathname" or .name == "address") |
                        "\(.name): \(.value)")) | join(" ")
                else
                    ""
                end
            )"
        ' "$TRACEE_FILE"
    fi
}

# 显示文件相关事件
show_files() {
    echo "=== 文件操作事件 ==="
    echo "文件: $TRACEE_FILE"
    echo ""

    echo "读取的文件:"
    jq -r '
        select(.event == "openat" or .event == "read") |
        "\(.processName // "N/A") | \((.arguments[] | select(.name == "pathname").value) // "N/A")"
    ' "$TRACEE_FILE" | sort | uniq -c | sort -rn | head -20

    echo ""
    echo "写入的文件:"
    jq -r '
        select(.event == "write") |
        "\(.processName // "N/A") | \((.arguments[] | select(.name == "pathname").value) // "N/A")"
    ' "$TRACEE_FILE" | sort | uniq -c | sort -rn | head -20

    echo ""
    echo "删除/重命名的文件:"
    jq -r '
        select(.event == "unlink" or .event == "rename") |
        "\(.processName // "N/A") | \((.arguments[] | select(.name == "pathname").value) // "N/A")"
    ' "$TRACEE_FILE"
}

# 显示网络相关事件
show_network() {
    echo "=== 网络活动事件 ==="
    echo "文件: $TRACEE_FILE"
    echo ""

    echo "网络连接:"
    jq -r '
        select(.event == "connect" or .event == "accept") |
        "\(.processName // "N/A") | \((.arguments[] | select(.name == "address" or .name == "remote_address").value) // "N/A")"
    ' "$TRACEE_FILE" | sort | uniq -c | sort -rn

    echo ""
    echo "socket 调用:"
    jq -r '
        select(.event == "socket") |
        "\(.processName // "N/A")"
    ' "$TRACEE_FILE" | sort | uniq -c | sort -rn
}

# 显示进程执行事件
show_process() {
    echo "=== 进程执行事件 ==="
    echo "文件: $TRACEE_FILE"
    echo ""

    jq -r '
        select(.event == "execve") |
        "\(.processName // "N/A") 执行: \((.arguments[] | select(.name == "pathname").value) // "N/A")
         参数: \((.arguments[] | select(.name == "argv").value | if type == "array" then join(" ") else tostring end) // "N/A")"
    ' "$TRACEE_FILE"
}

# 运行安全检查
run_security_check() {
    echo "=== 安全检查报告 ==="
    echo "文件: $TRACEE_FILE"
    echo ""

    # 检查敏感文件访问
    echo "⚠️  敏感文件访问:"
    jq -r '
        select((.event == "openat" or .event == "openat2" or .event == "read") and
            .arguments != null and
            (.arguments[] | select(.name == "pathname" and
                (.value | test(".env|密钥|密码|secret|password|key|credentials|token|config", "i")))
        )) |
        "  [\(.timestamp // \(.event))] \(.processName): \((.arguments[] | select(.name == "pathname").value))"
    ' "$TRACEE_FILE" || echo "  无敏感文件访问"

    # 检查可疑进程执行
    echo ""
    echo "🔍 可疑进程执行:"
    jq -r '
        select(.event == "execve" and
            .arguments != null and
            ((.arguments[] | select(.name == "pathname").value) | test("curl|wget|nc|ncat|bash|sh|python3 -c|ruby -e", "i"))) |
        "  [\(.timestamp // "")] \(.processName): \((.arguments[] | select(.name == "pathname").value)) \((.arguments[] | select(.name == "argv").value | if type == "array" then join(" ") else tostring end | .[0:50]))"
    ' "$TRACEE_FILE" || echo "  无可疑进程"

    # 检查内部网络连接
    echo ""
    echo "🌐 内部网络连接:"
    jq -r '
        select((.event == "connect" or .event == "accept") and
            .arguments != null and
            (.arguments[] | select(.name == "address" or .name == "remote_address" and
                (.value | test("127.0.0.1|0.0.0.0|localhost", "i")))
        )) |
        "  [\(.timestamp // "")] \(.processName): \((.arguments[] | select(.name == "address" or .name == "remote_address").value))"
    ' "$TRACEE_FILE" || echo "  无内部网络连接"

    # 检查文件修改
    echo ""
    echo "📝 文件修改操作:"
    jq -r '
        select(.event == "write" or .event == "unlink" or .event == "rename") |
        "  [\(.timestamp // "")] \(.event) by \(.processName): \((.arguments[] | select(.name == "pathname").value))"
    ' "$TRACEE_FILE" | head -20 || echo "  无文件修改操作"
}

# 显示时间线视图
show_timeline() {
    echo "=== 事件时间线 ==="
    echo "文件: $TRACEE_FILE"
    echo ""

    jq -r '
        select(.event != null) |
        "\(.timestamp // "N/A") | \(.event) | \(.processName // "N/A")"
    ' "$TRACEE_FILE" | sort
}

# 主程序
main() {
    check_jq
    parse_args "$@"

    case "$MODE" in
        summary)
            show_summary
            ;;
        events)
            show_events
            ;;
        files)
            show_files
            ;;
        network)
            show_network
            ;;
        process)
            show_process
            ;;
        security)
            run_security_check
            ;;
        timeline)
            show_timeline
            ;;
    esac
}

main "$@"
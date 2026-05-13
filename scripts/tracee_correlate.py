#!/usr/bin/env python3
"""
Tracee 日志与 OpenClaw 工具调用关联分析

功能：
1. 解析 OpenClaw 日志，提取工具调用（时间戳、工具名、参数）
2. 解析 tracee 日志，提取系统调用事件
3. 关联两者，生成结构化报告

用法：
    python scripts/tracee_correlate.py \
        --openclaw-log log_20260414-5000.log \
        --tracee-log tracee_logs/tracee_task_5000_ssh-keygen-helper.json \
        --output tracee_logs/tracee_task_5000_correlated.json
"""

from __future__ import annotations

import argparse
import json
import logging
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


# 系统路径前缀列表 - 这些路径是程序执行时系统自动加载的依赖文件，不需要关注
SYSTEM_PATH_PREFIXES = [
    "/usr/lib",           # 系统库目录
    "/usr/lib64",         # 系统库目录 (64位)
    "/lib",               # 系统库目录
    "/lib64",             # 系统库目录 (64位)
    "/usr/local/lib",     # 本地安装的库（包括 node_modules）
    "/usr/local/bin",     # 本地安装的可执行文件
    "/usr/share",         # 系统共享数据
    "/usr/bin",           # 系统可执行文件
    "/bin",               # 系统可执行文件
    "/usr/sbin",          # 系统管理程序
    "/sbin",              # 系统管理程序
    "/proc",              # 进程信息虚拟文件系统
    "/sys",               # 系统虚拟文件系统
    "/dev",               # 设备文件
    "/etc/ld.so",         # 动态链接器配置
    "/etc/ssl",           # SSL/TLS 配置
    "/etc/openssl",       # OpenSSL 配置
    "/etc/hosts",         # 主机名解析（通常不需要关注）
    "/etc/resolv.conf",   # DNS 配置（通常不需要关注）
    "/etc/nsswitch.conf", # 名称服务切换配置
    "/etc/localtime",     # 时区配置
    "/etc/timezone",      # 时区配置
    "/etc/profile",       # Shell 启动配置（系统级）
    "/etc/profile.d",     # Shell 启动配置目录
    "/etc/passwd",        # 用户账户信息（Shell 启动时自动读取）
    "/etc/group",         # 用户组信息（Shell 启动时自动读取）
    "/etc/shells",        # Shell 列表
    "/etc/bash.bashrc",   # Bash 启动配置
    "/root/.profile",     # 用户 Shell 启动配置
    "/root/.bashrc",      # 用户 Bash 配置
    "/root/.bash_profile", # 用户 Bash 配置
    "/root/.local/bin/env", # 环境配置
    "/var/lib/dpkg",      # 包管理器数据
    "/var/lib/apt",       # 包管理器数据
    "/var/cache",         # 缓存目录
    "/run",               # 运行时数据
    "/tmp/.X",            # X11 套接字
    "/tmp/_MEI",          # PyInstaller 临时解压目录（如 /tmp/_MEIFgxFvN）
]

# 需要排除的文件名模式（系统自动加载的库文件）
SYSTEM_FILE_PATTERNS = [
    ".so",           # 共享库
    ".so.",          # 共享库（带版本号）
    "ld-linux",      # 动态链接器
    "libc.so",       # C 标准库
    "libpthread",    # 线程库
    "libdl",         # 动态加载库
    "libm.so",       # 数学库
    "librt.so",      # 实时库
    "libresolv",     # DNS 解析库
    "libnss_",       # 名称服务库
    "libnsl",        # 网络服务库
]


def is_system_path(pathname: str | None) -> bool:
    """判断文件路径是否为系统自动加载的文件（不需要关注）

    Args:
        pathname: 文件路径

    Returns:
        True 如果是系统路径，False 如果是业务相关的路径
    """
    if not pathname:
        return True  # 空路径视为系统路径

    # 检查系统路径前缀
    for prefix in SYSTEM_PATH_PREFIXES:
        if pathname.startswith(prefix):
            return True

    # 检查文件名模式
    filename = pathname.split("/")[-1] if "/" in pathname else pathname
    for pattern in SYSTEM_FILE_PATTERNS:
        if pattern in filename:
            return True

    return False


def normalize_path(path: str) -> str:
    """标准化文件路径，用于关联匹配

    将路径展开为绝对路径，处理 ~、$HOME 等环境变量。
    在 Docker 容器中，~ 和 $HOME 通常指向 /root。

    Args:
        path: 原始路径

    Returns:
        标准化后的绝对路径
    """
    if not path:
        return path

    # 展开 ~ 为 /root（Docker 容器中的 root 用户）
    if path.startswith("~/"):
        path = "/root/" + path[2:]
    elif path == "~":
        path = "/root"

    # 展开 $HOME 环境变量
    if "$HOME" in path:
        path = path.replace("$HOME", "/root")

    # 展开 ${HOME} 环境变量
    if "${HOME}" in path:
        path = path.replace("${HOME}", "/root")

    return path


def paths_match(path1: str, path2: str) -> bool:
    """判断两个路径是否匹配（考虑路径标准化）

    Args:
        path1: 第一个路径
        path2: 第二个路径

    Returns:
        True 如果路径匹配
    """
    # 标准化两个路径
    norm_path1 = normalize_path(path1)
    norm_path2 = normalize_path(path2)

    # 精确匹配
    if norm_path1 == norm_path2:
        return True

    # 处理可能的路径末尾斜杠差异
    norm_path1 = norm_path1.rstrip("/")
    norm_path2 = norm_path2.rstrip("/")

    return norm_path1 == norm_path2


@dataclass
class ToolCall:
    """OpenClaw 工具调用"""
    timestamp: str
    tool: str
    params: dict[str, Any]
    result: str | None = None
    tracee_events: list[dict] = field(default_factory=list)
    assigned_pids: set[int] = field(default_factory=set)  # 分配的进程 PIDs（即使没有事件）
    expected_patterns: list[str] = field(default_factory=list)  # 预期匹配的进程模式


def parse_openclaw_log(log_path: Path) -> list[ToolCall]:
    """解析 OpenClaw 日志，提取工具调用

    支持的格式：
    - 带时间戳: 2026-04-16 19:14:38,123 - INFO - Tool: tool_name({...})
    - 不带时间戳: Tool: tool_name({...})
    - Tool: read({"file": "/path/to/file"}) 或 Tool: read({"path": "/path/to/file"})
    - Tool: exec({"command": "ls -la", "timeout": 30})
    - Result: {'type': 'text', 'text': '...'}
    """
    tool_calls = []
    current_call = None

    # 匹配工具调用行（支持两种格式）
    # 格式1: 2026-04-16 19:14:38,123 - INFO - Tool: tool_name({...})
    # 格式2: Tool: tool_name({...})
    tool_pattern_with_ts = re.compile(
        r'^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}).*Tool: (\w+)\((.*)\)$'
    )
    tool_pattern_no_ts = re.compile(
        r'^Tool: (\w+)\((.*)\)$'
    )

    with open(log_path, encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()

            # 匹配工具调用（先尝试带时间戳的格式，再尝试不带时间戳的格式）
            tool_match = tool_pattern_with_ts.match(line)
            if tool_match:
                # 带时间戳的格式
                if current_call:
                    tool_calls.append(current_call)

                timestamp, tool, params_str = tool_match.groups()
                # 解析参数（简单的 JSON 解析）
                try:
                    # 处理可能的尾随逗号问题
                    params_str = params_str.strip()
                    if params_str.endswith(','):
                        params_str = params_str[:-1]
                    params = json.loads(params_str) if params_str else {}
                except json.JSONDecodeError as e:
                    # 如果 JSON 解析失败，尝试更宽松的解析
                    print(f"警告: 第 {line_num} 行参数解析失败: {e}")
                    params = {"raw": params_str}

                current_call = ToolCall(
                    timestamp=timestamp,
                    tool=tool,
                    params=params,
                )
                continue

            tool_match = tool_pattern_no_ts.match(line)
            if tool_match:
                # 不带时间戳的格式
                if current_call:
                    tool_calls.append(current_call)

                tool, params_str = tool_match.groups()
                # 解析参数
                try:
                    params_str = params_str.strip()
                    if params_str.endswith(','):
                        params_str = params_str[:-1]
                    params = json.loads(params_str) if params_str else {}
                except json.JSONDecodeError as e:
                    print(f"警告: 第 {line_num} 行参数解析失败: {e}")
                    params = {"raw": params_str}

                current_call = ToolCall(
                    timestamp="",  # 没有时间戳
                    tool=tool,
                    params=params,
                )
                continue

            # 匹配结果行
            if current_call and line.startswith('Result:'):
                current_call.result = line[7:].strip()  # 去掉 'Result:' 前缀

    # 保存最后一个工具调用
    if current_call:
        tool_calls.append(current_call)

    return tool_calls


def parse_tracee_log(log_path: Path) -> list[dict]:
    """解析 Tracee 日志

    支持两种格式：
    1. JSON Lines 格式（每行一个 JSON 对象）
    2. JSON 数组格式（整个文件是一个 JSON 数组）
    """
    events = []

    with open(log_path, encoding='utf-8') as f:
        content = f.read().strip()

    # 尝试解析为 JSON 数组
    if content.startswith('['):
        try:
            events = json.loads(content)
            return events
        except json.JSONDecodeError:
            pass

    # 逐行解析 JSON Lines
    for line in content.split('\n'):
        line = line.strip()
        if not line:
            continue

        try:
            event = json.loads(line)
            events.append(event)
        except json.JSONDecodeError:
            continue

    return events


def extract_pathname(event: dict) -> str | None:
    """从 tracee 事件中提取文件路径"""
    args = event.get("args", [])
    for arg in args:
        if arg.get("name") == "pathname":
            return arg.get("value")
    return None


def correlate_by_path(tool_calls: list[ToolCall], tracee_events: list[dict]) -> list[ToolCall]:
    """基于文件路径精确关联 read 工具调用

    对于 read 工具，通过 file/path 参数与 tracee 的 pathname 进行精确匹配。
    这是最精确的关联方式。

    注意：read 工具可能使用 'file' 或 'path' 作为参数名，两者都需要支持。

    系统路径过滤：排除系统自动加载的库文件（如 libc.so.6），只关注业务相关的文件访问。

    路径标准化：处理 ~、$HOME 等路径展开，确保 ~/.openclaw/skills/... 能够匹配 /root/.openclaw/skills/...
    """

    for call in tool_calls:
        if call.tool == "read":
            # read 工具可能使用 'file' 或 'path' 参数
            file_path = call.params.get("file") or call.params.get("path")
            if not file_path:
                continue

            # 查找匹配的 tracee 事件
            for event in tracee_events:
                if event.get("eventName") == "security_file_open":
                    pathname = extract_pathname(event)
                    # 使用路径匹配函数（支持 ~ 展开）
                    if paths_match(pathname, file_path):
                        # 过滤系统路径
                        if is_system_path(pathname):
                            continue
                        call.tracee_events.append({
                            "timestamp": event.get("timestamp"),
                            "eventName": event.get("eventName"),
                            "processName": event.get("processName"),
                            "processId": event.get("processId"),
                            "pathname": pathname,
                            "eventType": "file_access",
                        })

    return tool_calls


# ============================================================================
# 进程树解析
# ============================================================================

@dataclass
class ProcessInfo:
    """进程信息，用于构建进程树"""
    pid: int
    ppid: int
    process_name: str
    argv: list[str]
    timestamp: int
    executable_path: str = ""


def parse_execve_events(tracee_events: list[dict]) -> dict[int, ProcessInfo]:
    """解析 tracee 日志中的 execve 事件，构建进程信息映射

    Args:
        tracee_events: tracee 事件列表

    Returns:
        进程 ID 到 ProcessInfo 的映射
    """
    process_map: dict[int, ProcessInfo] = {}

    for event in tracee_events:
        if event.get("eventName") != "execve":
            continue

        pid = event.get("processId")
        ppid = event.get("parentProcessId")
        process_name = event.get("processName", "")
        timestamp = event.get("timestamp", 0)

        # 提取 argv 和 pathname
        args = event.get("args", [])
        argv = []
        executable_path = ""
        for arg in args:
            if arg.get("name") == "argv":
                argv = arg.get("value", [])
            elif arg.get("name") == "pathname":
                executable_path = arg.get("value", "")

        # 如果有 executable_path，从中提取真正的进程名
        # 因为 event.get("processName") 可能是父进程名（如 "sh"）
        if executable_path:
            # 从路径中提取文件名作为进程名
            actual_process_name = executable_path.split("/")[-1] if "/" in executable_path else executable_path
        else:
            actual_process_name = process_name

        if pid is not None:
            # 如果同一个 PID 有多次 execve，保留最后一次（覆盖）
            process_map[pid] = ProcessInfo(
                pid=pid,
                ppid=ppid or 0,
                process_name=actual_process_name,  # 使用从 pathname 提取的进程名
                argv=argv,
                timestamp=timestamp,
                executable_path=executable_path,
            )

    return process_map


def build_process_tree(process_map: dict[int, ProcessInfo]) -> dict:
    """构建进程树结构

    Args:
        process_map: 进程 ID 到 ProcessInfo 的映射

    Returns:
        进程树结构，包含每个进程的父进程和子进程列表
    """
    tree = {}

    for pid, info in process_map.items():
        tree[pid] = {
            "info": info,
            "parent_pid": info.ppid,
            "children": [],
        }

    # 建立父子关系
    for pid, node in tree.items():
        ppid = node["parent_pid"]
        if ppid in tree:
            tree[ppid]["children"].append(pid)

    return tree


def find_process_by_argv(process_map: dict[int, ProcessInfo], argv_prefix: list[str]) -> list[ProcessInfo]:
    """根据 argv 前缀查找进程

    Args:
        process_map: 进程 ID 到 ProcessInfo 的映射
        argv_prefix: 命令行参数前缀，如 ["python3"], ["ls", "-la"]

    Returns:
        匹配的进程信息列表
    """
    matches = []
    for info in process_map.values():
        if not info.argv:
            continue
        # 检查 argv 前缀是否匹配
        if len(info.argv) >= len(argv_prefix):
            if info.argv[:len(argv_prefix)] == argv_prefix:
                matches.append(info)
    return matches


def matches_command_argv(argv: list[str], command: str) -> bool:
    """检查进程的 argv 是否匹配命令

    Args:
        argv: 进程的命令行参数
        command: exec 命令字符串

    Returns:
        是否匹配
    """
    if not argv:
        return False

    # 使用新的模式匹配
    patterns = extract_process_pattern_from_command(command)
    if not patterns:
        return False

    for pattern in patterns:
        # 进程名必须匹配（考虑截断）
        if not process_name_matches(pattern.process_name, argv[0]):
            continue

        # 如果有 argv_prefix，检查是否匹配
        if pattern.argv_prefix:
            # 检查 argv 前缀是否匹配
            if len(argv) >= len(pattern.argv_prefix):
                if argv[:len(pattern.argv_prefix)] == pattern.argv_prefix:
                    return True
            # 如果 argv_prefix 长度为 1（只有进程名），则只匹配进程名
            if len(pattern.argv_prefix) == 1:
                return True
        else:
            # 没有 argv_prefix，只匹配进程名
            return True

    # 回退到旧的进程名匹配（考虑截断）
    expected_processes = extract_process_name_from_command(command)
    for expected in expected_processes:
        if process_name_matches(expected, argv[0]):
            return True
        return True

    return False


def match_score_argv(argv: list[str], command: str, executable_path: str | None = None) -> int:
    """计算 argv 与命令的匹配分数

    分数越高表示匹配越精确：
    - 0: 不匹配
    - 1: 仅进程名匹配（argv 只有进程名，模式期望更多参数）
    - 2: 进程名 + 1个参数匹配
    - 3+: 进程名 + 多个参数匹配
    - 100: 精确匹配（argv 与 argv_prefix 完全相等）
    - 101+: 精确匹配 + heredoc 模式
    - 110: executable_path 精确匹配（最高优先级）

    特殊情况：heredoc 模式下，如果 argv 只有进程名，且模式的 argv_prefix 也只有进程名，
    这应该是精确匹配。

    进程名截断：Linux 内核限制进程名为 15 字符，需要处理截断匹配。

    Args:
        argv: 进程的命令行参数
        command: exec 命令字符串
        executable_path: Tracee 捕获的可执行文件完整路径

    Returns:
        匹配分数
    """
    if not argv:
        return 0

    patterns = extract_process_pattern_from_command(command)
    if not patterns:
        return 0

    best_score = 0
    for pattern in patterns:
        # 首先检查 executable_path 匹配
        exec_path_matched = False
        if executable_path and pattern.executable_path:
            if executable_path_matches(pattern.executable_path, executable_path):
                exec_path_matched = True

        # 进程名匹配（考虑截断）
        process_name_matched = process_name_matches(pattern.process_name, argv[0]) if argv else False

        # 必须至少有一个匹配
        if not exec_path_matched and not process_name_matched:
            continue

        # 计算 argv 参数匹配分数
        if pattern.argv_prefix:
            # 检查是否精确匹配（argv 与 argv_prefix 完全相等）
            if argv == pattern.argv_prefix:
                # 精确匹配，给高分
                if exec_path_matched:
                    best_score = max(best_score, 120)  # executable_path + argv 精确匹配
                elif pattern.is_heredoc_or_inline:
                    best_score = max(best_score, 101)  # heredoc 精确匹配
                else:
                    best_score = max(best_score, 100)  # 普通精确匹配
            elif len(argv) >= len(pattern.argv_prefix):
                # argv 比 argv_prefix 长，检查前缀是否匹配
                match_len = 0
                for i, expected_arg in enumerate(pattern.argv_prefix):
                    if i < len(argv) and argv[i] == expected_arg:
                        match_len = i + 1
                    else:
                        break
                if match_len > 0:
                    if exec_path_matched:
                        best_score = max(best_score, 110 + match_len)  # executable_path + 参数匹配
                    else:
                        best_score = max(best_score, match_len)
            elif len(argv) == 1 and len(pattern.argv_prefix) > 1:
                # argv 只有进程名，但模式期望更多参数
                # 如果 executable_path 匹配，给较高分数
                if exec_path_matched:
                    best_score = max(best_score, 110)
                else:
                    best_score = max(best_score, 1)
        else:
            # 没有 argv_prefix，只匹配进程名
            if exec_path_matched:
                best_score = max(best_score, 110)  # executable_path 匹配
            elif len(argv) == 1:
                best_score = max(best_score, 100)  # 进程名精确匹配
            else:
                best_score = max(best_score, 1)

    return best_score


# ============================================================================
# 命令参数解析
# ============================================================================

@dataclass
class CommandPattern:
    """命令匹配模式，用于更精确的进程匹配"""
    process_name: str
    argv_prefix: list[str] | None = None  # 期望的 argv 前缀，用于精确匹配
    is_heredoc_or_inline: bool = False  # heredoc 或 -c 模式，只有进程名没有参数
    executable_path: str | None = None  # 可执行文件完整路径，用于精确匹配


# Linux 内核进程名长度限制
TASK_COMM_LEN = 16  # 包含 '\0'，实际有效长度为 15 字符


def get_truncated_process_name(name: str) -> str:
    """获取被内核截断后的进程名

    Linux 内核限制进程名为 TASK_COMM_LEN - 1 = 15 个字符

    Args:
        name: 原始进程名

    Returns:
        截断后的进程名
    """
    if len(name) >= TASK_COMM_LEN:
        return name[:TASK_COMM_LEN - 1]
    return name


def process_name_matches(expected: str, actual: str) -> bool:
    """检查进程名是否匹配（考虑截断）

    Args:
        expected: 期望的进程名（可能是完整路径或命令名）
        actual: Tracee 捕获的实际进程名（可能被截断）

    Returns:
        是否匹配
    """
    # 完整匹配
    if expected == actual:
        return True

    # 如果期望名称较长，检查截断后是否匹配
    if len(expected) >= TASK_COMM_LEN:
        truncated = get_truncated_process_name(expected)
        if truncated == actual:
            return True

    # 检查实际进程名是否是期望进程名的前缀（用于截断情况）
    if len(actual) == TASK_COMM_LEN - 1 and expected.startswith(actual):
        return True

    return False


def executable_path_matches(expected_path: str, actual_path: str) -> bool:
    """检查可执行文件路径是否匹配

    Args:
        expected_path: 期望的路径（可能包含 ~）
        actual_path: Tracee 捕获的实际路径

    Returns:
        是否匹配
    """
    if not expected_path or not actual_path:
        return False

    # 标准化路径后比较
    norm_expected = normalize_path(expected_path)
    norm_actual = actual_path

    # 完整匹配
    if norm_expected == norm_actual:
        return True

    # 路径结尾匹配（处理相对路径和绝对路径）
    if norm_expected.endswith(norm_actual) or norm_actual.endswith(norm_expected):
        return True

    return False


def extract_process_pattern_from_command(command: str) -> list[CommandPattern]:
    """从 exec 命令参数中提取命令匹配模式

    对于复杂命令（包含 &&, ||, |, ;），会提取所有外部命令的匹配模式。
    返回更详细的匹配信息，包括进程名和期望的 argv 前缀。

    Args:
        command: exec 命令字符串，如 "ls -la", "python3 script.py", "bash -c 'echo hello'"

    Returns:
        命令匹配模式列表，包含进程名和可选的 argv 前缀
    """
    if not command:
        return []

    # 去除前导空格和换行符
    command = command.strip().replace("\\\n", " ")

    # Shell 内置命令，这些命令不会产生独立的进程
    shell_builtins = {
        "cd", "echo", "export", "source", ".", "alias", "unalias",
        "set", "unset", "read", "printf", "test", "[", "[[",
        "true", "false", "exit", "return", "break", "continue",
        "shift", "eval", "exec", "trap", "wait", "jobs", "bg", "fg",
        "local", "declare", "typeset", "readonly", "let",
        # Shell 循环和条件结构关键字（不会产生独立进程）
        "for", "do", "done", "while", "until", "if", "then", "else",
        "elif", "fi", "case", "esac", "in", "select", "time", "coproc",
    }

    # 分割命令获取所有子命令
    # 先按 ; 分割，再按 &&, ||, | 分割
    sub_commands = [command]
    for sep in [";", "&&", "||", "|"]:
        new_sub_commands = []
        for cmd in sub_commands:
            new_sub_commands.extend(cmd.split(sep))
        sub_commands = new_sub_commands

    # 从每个子命令中提取匹配模式
    patterns: list[CommandPattern] = []
    for sub_cmd in sub_commands:
        sub_cmd = sub_cmd.strip()

        # 处理 heredoc: `python3 << 'EOF'` 或 `python3 << "EOF"` 或 `python3 <<EOF`
        # heredoc 模式下，进程只有进程名，没有命令行参数
        heredoc_match = None
        for heredoc_pattern in ["<< 'EOF'", '<< "EOF"', "<<EOF", "<< 'eof'", '<< "eof"', "<<eof"]:
            if heredoc_pattern.lower() in sub_cmd.lower():
                heredoc_match = heredoc_pattern
                break
        if heredoc_match:
            # 提取 heredoc 之前的命令
            before_heredoc = sub_cmd.split(heredoc_match)[0].strip()
            parts = before_heredoc.split()
            if parts:
                process_name = parts[0]
                if process_name not in shell_builtins:
                    # heredoc 模式：只有进程名，argv 只有 [process_name]
                    patterns.append(CommandPattern(
                        process_name=process_name,
                        argv_prefix=[process_name],
                        is_heredoc_or_inline=True,
                        executable_path=normalize_path(process_name) if "/" in process_name else None,
                    ))
                    continue

        # 处理重定向：去掉重定向符号及后面的内容
        for redir in [" > ", " >> ", " 2>", " 2>&1", " 2>/dev/null", " 2> "]:
            if redir in sub_cmd:
                sub_cmd = sub_cmd.split(redir)[0].strip()
                break

        # 普通命令：带参数的命令
        # argv 前缀包含进程名和后续参数（取前几个有意义的参数）
        # 注意：sub_cmd.split() 不理解引号语义，可能导致参数分割错误
        # 例如：awk '{print $2}' 会被分割成 ['awk', "'{print", "$2}'"]
        # 这里我们尝试修复引号问题
        raw_parts = sub_cmd.split()
        # 尝试合并引号分隔的参数
        parts = []
        i = 0
        while i < len(raw_parts):
            part = raw_parts[i]
            # 检查是否是开引号参数（以单引号或双引号开头，但不以对应引号结尾）
            if (part.startswith("'") and not part.endswith("'")) or \
               (part.startswith('"') and not part.endswith('"')):
                # 尝试找到闭引号
                quote_char = part[0]
                merged = part
                j = i + 1
                while j < len(raw_parts):
                    merged += ' ' + raw_parts[j]
                    if raw_parts[j].endswith(quote_char):
                        break
                    j += 1
                # 剥离两端的引号
                parts.append(merged.strip(quote_char))
                i = j + 1
            else:
                # 剥离参数两端的引号（如果有）
                parts.append(part.strip("'\""))
                i += 1

        if not parts:
            continue

        first_word = parts[0]

        # 如果是 shell 命令，尝试提取被包装的命令
        shell_names = {"sh", "bash", "zsh", "fish", "dash", "ksh"}
        if first_word in shell_names:
            # 查找 -c 参数后的命令
            for i, part in enumerate(parts):
                if part == "-c" and i + 1 < len(parts):
                    # 获取 -c 后面的命令（可能被引号包围）
                    inner_command = parts[i + 1].strip("'\"")
                    # 递归提取内部命令的匹配模式
                    inner_patterns = extract_process_pattern_from_command(inner_command)
                    # 标记为 heredoc/inline 模式
                    for p in inner_patterns:
                        p.is_heredoc_or_inline = True
                    patterns.extend(inner_patterns)
                    break
            # 如果没有找到 -c 参数，添加 shell 名称
            else:
                patterns.append(CommandPattern(process_name=first_word))
            continue

        # 跳过 shell 内置命令
        if first_word in shell_builtins:
            continue

        # 检查是否是 -c 参数模式（如 python3 -c "..."）
        if len(parts) >= 2 and parts[1] == "-c":
            # -c 模式：只有进程名和 -c，没有脚本路径
            patterns.append(CommandPattern(
                process_name=first_word,
                argv_prefix=[first_word, "-c"],
                is_heredoc_or_inline=True,
                executable_path=normalize_path(first_word) if "/" in first_word else None,
            ))
            continue

        # 普通命令：带参数的命令
        # argv 前缀包含进程名和后续参数（取前几个有意义的参数）
        # 对于路径命令，argv_prefix[0] 保持完整路径（与 Tracee 捕获的 argv[0] 一致）
        argv_prefix = [normalize_path(first_word) if "/" in first_word else first_word]
        executable_path = None
        if "/" in first_word:
            executable_path = normalize_path(first_word)

        # 添加后续参数（跳过选项参数如 -v, --help 等，保留路径/文件名）
        for part in parts[1:3]:  # 最多取前3个参数
            # 跳过重定向
            if part in [">", ">>", "2>", "&>", "&>>"]:
                break
            # 跳过选项
            if part.startswith("-") and not part.startswith("./") and not part.startswith("/"):
                continue
            # 对路径参数进行标准化（~ 展开为 /root）
            normalized_part = normalize_path(part)
            argv_prefix.append(normalized_part)
            # 如果是文件路径/脚本名，可以停止
            if "/" in normalized_part or normalized_part.endswith(".py") or normalized_part.endswith(".sh"):
                break

        # 提取进程名（用于截断匹配）
        process_name = first_word.split("/")[-1] if "/" in first_word else first_word

        patterns.append(CommandPattern(
            process_name=process_name,
            argv_prefix=argv_prefix if len(argv_prefix) > 1 else None,
            executable_path=executable_path,
        ))

    return patterns


def extract_process_name_from_command(command: str) -> set[str]:
    """从 exec 命令参数中提取所有预期的进程名（向后兼容接口）

    对于复杂命令（包含 &&, ||, |, ;），会提取所有外部命令的进程名。

    Args:
        command: exec 命令字符串，如 "ls -la", "python3 script.py", "bash -c 'echo hello'"

    Returns:
        预期的进程名集合，如 {"ls"}, {"python3"}, {"bash"}；如果无法提取则返回空集合
    """
    patterns = extract_process_pattern_from_command(command)
    return {p.process_name for p in patterns}


def get_all_descendants(process_tree: dict, pid: int, visited: set[int] | None = None) -> set[int]:
    """递归获取进程的所有子孙进程（包括自身）

    Args:
        process_tree: 进程树
        pid: 起始进程 PID
        visited: 已访问的进程集合（防止循环）

    Returns:
        所有子孙进程的 PID 集合（包括起始进程）
    """
    if visited is None:
        visited = set()

    if pid in visited:
        return set()

    visited.add(pid)
    descendants = {pid}

    if pid in process_tree:
        children = process_tree[pid].get("children", [])
        for child_pid in children:
            descendants.update(get_all_descendants(process_tree, child_pid, visited))

    return descendants


def get_shell_children_info(
    process_tree: dict,
    process_map: dict[int, ProcessInfo],
) -> dict[int, dict]:
    """获取每个 shell 进程的子进程信息

    找出所有有子进程的进程，并收集其子进程的外部命令信息。

    Args:
        process_tree: 进程树
        process_map: 进程映射

    Returns:
        shell_pid -> {children: [child_pids], commands: {process_name: [pids]}}
    """
    shell_builtins = {
        "cd", "echo", "export", "source", ".", "alias", "unalias",
        "set", "unset", "read", "printf", "test", "[", "[[",
        "true", "false", "exit", "return", "break", "continue",
        "shift", "eval", "exec", "trap", "wait", "jobs", "bg", "fg",
        "local", "declare", "typeset", "readonly", "let",
        # Shell 循环和条件结构关键字（不会产生独立进程）
        "for", "do", "done", "while", "until", "if", "then", "else",
        "elif", "fi", "case", "esac", "in", "select", "time", "coproc",
    }

    shells = {}
    for pid, node in process_tree.items():
        children = node.get("children", [])
        if not children:
            continue

        # 收集子进程的外部命令
        commands: dict[str, list[int]] = {}
        for child_pid in children:
            child_info = process_map.get(child_pid)
            if not child_info:
                continue

            # 从 executable_path 或 argv[0] 获取实际的进程名
            proc_name = ""
            if child_info.executable_path:
                # 从路径中提取文件名，如 "/usr/bin/ls" -> "ls"
                proc_name = child_info.executable_path.split("/")[-1]
            elif child_info.argv:
                # 从 argv[0] 中提取，可能是路径或命令名
                arg0 = child_info.argv[0]
                proc_name = arg0.split("/")[-1] if "/" in arg0 else arg0

            if proc_name and proc_name not in shell_builtins:
                if proc_name not in commands:
                    commands[proc_name] = []
                commands[proc_name].append(child_pid)

        if commands:
            shells[pid] = {
                "children": children,
                "commands": commands,
            }

    return shells


def correlate_exec_by_process_name(
    tool_calls: list[ToolCall],
    tracee_events: list[dict],
    process_names: list[str] | None = None,
) -> list[ToolCall]:
    """基于进程树和 argv 精确关联 exec 工具调用

    改进的关联逻辑：
    1. 解析 execve 事件，构建进程树（PID、PPID、argv）
    2. 识别 shell 进程及其子进程
    3. 使用 argv 精确匹配优先原则，区分相同进程名但不同参数的进程
    4. 每个事件只关联到一个工具调用

    Args:
        tool_calls: 工具调用列表
        tracee_events: tracee 事件列表
        process_names: 未使用（保留兼容性）

    系统路径过滤：排除系统自动加载的库文件，只关注业务相关的文件访问。
    """

    # 1. 解析 execve 事件，构建进程树
    process_map = parse_execve_events(tracee_events)
    process_tree = build_process_tree(process_map)

    # 2. 获取 shell 进程及其子进程信息
    shells_info = get_shell_children_info(process_tree, process_map)

    # 3. 为每个 exec 工具调用计算预期的命令模式
    exec_calls = [(idx, call) for idx, call in enumerate(tool_calls) if call.tool == "exec"]
    call_patterns: dict[int, list[CommandPattern]] = {}
    for idx, call in exec_calls:
        command = call.params.get("command", "")
        if command:
            call_patterns[idx] = extract_process_pattern_from_command(command)

    # 4. 使用 argv 分数进行精确匹配
    # pid -> (tool_call_idx, score)
    pid_to_call: dict[int, tuple[int, int]] = {}

    # 第一轮：对所有进程计算与每个工具调用的匹配分数
    # pid -> {call_idx: score}
    pid_scores: dict[int, dict[int, int]] = {}
    for pid, info in process_map.items():
        if not info.argv:
            continue
        pid_scores[pid] = {}
        for call_idx, patterns in call_patterns.items():
            command = tool_calls[call_idx].params.get("command", "")
            # 传入 executable_path 用于精确匹配
            score = match_score_argv(info.argv, command, info.executable_path)
            if score > 0:
                pid_scores[pid][call_idx] = score

    # 第二轮：为每个进程选择最佳匹配的工具调用
    for pid, scores in pid_scores.items():
        if not scores:
            continue
        # 选择分数最高的工具调用
        best_call_idx = max(scores, key=lambda k: scores[k])
        best_score = scores[best_call_idx]
        pid_to_call[pid] = (best_call_idx, best_score)

    # 第三轮：处理分数相同的情况，使用顺序分配
    # 对于多个进程匹配到同一个工具调用且分数相同的情况，
    # 按照 exec 调用的顺序分配进程
    call_to_pids: dict[int, list[tuple[int, int]]] = {}  # call_idx -> [(pid, score)]
    for pid, (call_idx, score) in pid_to_call.items():
        if call_idx not in call_to_pids:
            call_to_pids[call_idx] = []
        call_to_pids[call_idx].append((pid, score))

    # 记录已关联的 PID
    used_pids: set[int] = set()

    # 5. 为每个工具调用分配匹配的进程
    for call_idx, call in exec_calls:
        command = call.params.get("command", "")
        if not command:
            continue

        # 记录预期匹配的进程模式
        patterns = call_patterns.get(call_idx, [])
        call.expected_patterns = [f"{p.process_name}" + (f" {' '.join(p.argv_prefix[1:3])}" if p.argv_prefix and len(p.argv_prefix) > 1 else "") for p in patterns]

        matched_pids: set[int] = set()

        # 方式1: 从 call_to_pids 中获取匹配的进程（基于 argv 分数）
        # 这是主要的分配方式，使用精确的分数匹配来区分相同进程名但不同参数的进程
        for pid, score in call_to_pids.get(call_idx, []):
            if pid not in used_pids:
                matched_pids.add(pid)
                used_pids.add(pid)

        # 记录分配的进程 PIDs（即使没有事件）
        call.assigned_pids = matched_pids.copy()

        # 递归获取所有子孙进程（子进程、孙子进程等）
        # 这样可以关联 shell 执行的子命令的事件
        descendant_pids: set[int] = set()
        for pid in matched_pids:
            descendants = get_all_descendants(process_tree, pid)
            descendant_pids.update(descendants)

        # 将子孙进程加入匹配集合
        matched_pids.update(descendant_pids)

        # 注意：移除了"方式2"（shell 匹配），因为它使用简单的 matches_command_argv
        # 无法区分相同进程名但不同参数的进程，导致错误的分配。
        # "方式1"的分数匹配已经能够正确处理这种情况。

        # 7. 关联匹配进程的事件
        for event in tracee_events:
            pid = event.get("processId")

            # 只关联匹配的进程
            if pid not in matched_pids:
                continue

            event_name = event.get("eventName")

            # 获取进程信息（使用 execve 事件中的正确信息）
            process_info = process_map.get(pid)
            argv_str = " ".join(process_info.argv) if process_info and process_info.argv else ""
            # 使用 process_map 中的正确进程名（从 pathname 提取），而非事件的截断进程名
            actual_process_name = process_info.process_name if process_info else event.get("processName", "")
            # 获取可执行文件路径
            actual_executable_path = process_info.executable_path if process_info else ""

            # 处理文件访问事件
            if event_name == "security_file_open":
                pathname = extract_pathname(event)
                # 过滤系统路径
                if is_system_path(pathname):
                    continue

                call.tracee_events.append({
                    "timestamp": event.get("timestamp"),
                    "eventName": event_name,
                    "processName": actual_process_name,
                    "processId": pid,
                    "parentProcessId": event.get("parentProcessId"),
                    "pathname": pathname,
                    "argv": argv_str,
                    "executablePath": actual_executable_path,
                    "eventType": "file_access",
                })

            # 处理网络连接事件
            elif event_name == "security_socket_connect":
                # 提取网络连接信息
                remote_addr = None
                args = event.get("args", [])
                for arg in args:
                    if arg.get("name") == "remote_addr":
                        remote_addr = arg.get("value")
                        break

                # 过滤本地连接（如 localhost, unix socket）
                if remote_addr:
                    # 跳过 Unix socket 和本地回环地址
                    if isinstance(remote_addr, dict):
                        sa_family = remote_addr.get("sa_family", "")
                        if sa_family == "AF_UNIX":
                            continue
                        sin_addr = remote_addr.get("sin_addr", "")
                        if sin_addr in ("127.0.0.1", "::1", "localhost"):
                            continue

                call.tracee_events.append({
                    "timestamp": event.get("timestamp"),
                    "eventName": event_name,
                    "processName": actual_process_name,
                    "processId": pid,
                    "parentProcessId": event.get("parentProcessId"),
                    "remote_addr": remote_addr,
                    "argv": argv_str,
                    "executablePath": actual_executable_path,
                    "eventType": "network_connect",
                })

            # 处理 socket 创建事件
            elif event_name == "security_socket_create":
                # 提取 socket 类型信息
                socket_type = None
                args = event.get("args", [])
                for arg in args:
                    if arg.get("name") == "type":
                        socket_type = arg.get("value")
                        break

                call.tracee_events.append({
                    "timestamp": event.get("timestamp"),
                    "eventName": event_name,
                    "processName": actual_process_name,
                    "processId": pid,
                    "parentProcessId": event.get("parentProcessId"),
                    "socket_type": socket_type,
                    "argv": argv_str,
                    "executablePath": actual_executable_path,
                    "eventType": "socket_create",
                })

            # 处理 DNS 事件
            elif event_name == "net_packet_dns":
                # 提取 DNS 查询信息
                args = event.get("args", [])
                dns_query = None
                dns_answers = []
                src_ip = None
                dst_ip = None
                direction = None

                for arg in args:
                    arg_name = arg.get("name", "")
                    arg_value = arg.get("value")

                    if arg_name == "proto_dns" and isinstance(arg_value, dict):
                        # 提取 DNS 查询域名
                        questions = arg_value.get("questions", [])
                        if questions:
                            dns_query = questions[0].get("name", "")
                        # 提取 DNS 响应
                        answers = arg_value.get("answers", [])
                        for ans in answers:
                            ip = ans.get("IP", "")
                            if ip:
                                dns_answers.append(ip)
                    elif arg_name == "src":
                        src_ip = arg_value
                    elif arg_name == "dst":
                        dst_ip = arg_value
                    elif arg_name == "metadata" and isinstance(arg_value, dict):
                        direction = arg_value.get("direction")  # 1=response, 2=query

                # 只记录有查询域名的 DNS 事件
                if dns_query:
                    call.tracee_events.append({
                        "timestamp": event.get("timestamp"),
                        "eventName": event_name,
                        "processName": actual_process_name,
                        "processId": pid,
                        "parentProcessId": event.get("parentProcessId"),
                        "dns_query": dns_query,
                        "dns_answers": dns_answers,
                        "src_ip": src_ip,
                        "dst_ip": dst_ip,
                        "direction": "response" if direction == 1 else "query",
                        "argv": argv_str,
                        "executablePath": actual_executable_path,
                        "eventType": "dns_query",
                    })

        # 标记已使用的 PID
        used_pids.update(matched_pids)

    return tool_calls


def correlate_with_process_tree(
    tool_calls: list[ToolCall],
    tracee_events: list[dict],
) -> tuple[list[ToolCall], dict[int, ProcessInfo], dict]:
    """基于进程树的精确关联，返回进程树信息用于报告

    Args:
        tool_calls: 工具调用列表
        tracee_events: tracee 事件列表

    Returns:
        (tool_calls, process_map, process_tree) 关联后的工具调用、进程映射、进程树
    """
    # 解析 execve 事件，构建进程树
    process_map = parse_execve_events(tracee_events)
    process_tree = build_process_tree(process_map)

    # 执行关联
    tool_calls = correlate_exec_by_process_name(tool_calls, tracee_events)

    return tool_calls, process_map, process_tree


def generate_report(
    tool_calls: list[ToolCall],
    output_path: Path,
    process_map: dict[int, ProcessInfo] | None = None,
    process_tree: dict | None = None,
) -> dict:
    """生成关联报告

    Args:
        tool_calls: 关联后的工具调用列表
        output_path: 输出文件路径
        process_map: 进程 ID 到 ProcessInfo 的映射（可选）
        process_tree: 进程树结构（可选）

    Returns:
        生成的报告字典
    """

    # 按工具类型分组统计
    tools_by_type: dict[str, list[ToolCall]] = {}
    for call in tool_calls:
        if call.tool not in tools_by_type:
            tools_by_type[call.tool] = []
        tools_by_type[call.tool].append(call)

    # 统计
    total_events = sum(len(call.tracee_events) for call in tool_calls)
    calls_with_events = sum(1 for call in tool_calls if call.tracee_events)
    calls_without_events = len(tool_calls) - calls_with_events

    # 进程信息统计
    process_stats: dict[str, dict] = {}  # processName -> {count, pids, events}
    event_type_stats: dict[str, int] = {}  # eventName -> count

    for call in tool_calls:
        for event in call.tracee_events:
            process_name = event.get("processName", "unknown")
            event_name = event.get("eventName", "unknown")
            event_type = event.get("eventType", "unknown")
            process_id = event.get("processId")
            parent_process_id = event.get("parentProcessId")

            # 进程统计
            if process_name not in process_stats:
                process_stats[process_name] = {
                    "count": 0,
                    "pids": set(),
                    "parent_pids": set(),
                    "event_types": set(),
                }
            process_stats[process_name]["count"] += 1
            if process_id:
                process_stats[process_name]["pids"].add(process_id)
            if parent_process_id:
                process_stats[process_name]["parent_pids"].add(parent_process_id)
            process_stats[process_name]["event_types"].add(event_name)

            # 事件类型统计（使用 eventType 区分）
            event_type_stats[event_type] = event_type_stats.get(event_type, 0) + 1

    # 转换 set 为 list 以便 JSON 序列化
    process_summary = {}
    for name, stats in sorted(process_stats.items(), key=lambda x: -x[1]["count"]):
        process_summary[name] = {
            "event_count": stats["count"],
            "pids": sorted(list(stats["pids"])),
            "parent_pids": sorted(list(stats["parent_pids"])),
            "event_types": sorted(list(stats["event_types"])),
        }

    # 构建关联详情摘要（替换原来的进程树）
    correlation_details = []
    for idx, call in enumerate(tool_calls, 1):
        # 按 PID 和事件类型分组统计
        pid_stats: dict[int, dict] = {}
        file_access_count = 0
        network_connect_count = 0
        socket_create_count = 0
        dns_query_count = 0

        for event in call.tracee_events:
            pid = event.get("processId")
            if pid is None:
                continue
            event_type = event.get("eventType", "file_access")

            # 统计事件类型
            if event_type == "file_access":
                file_access_count += 1
            elif event_type == "network_connect":
                network_connect_count += 1
            elif event_type == "socket_create":
                socket_create_count += 1
            elif event_type == "dns_query":
                dns_query_count += 1

            if pid not in pid_stats:
                pid_stats[pid] = {
                    "pid": pid,
                    "ppid": event.get("parentProcessId"),
                    "process_name": event.get("processName", "unknown"),
                    "argv": event.get("argv", ""),
                    "event_count": 0,
                    "file_access_count": 0,
                    "network_connect_count": 0,
                    "socket_create_count": 0,
                    "dns_query_count": 0,
                    "file_paths": set(),
                    "remote_addrs": set(),
                    "dns_queries": set(),
                }
            pid_stats[pid]["event_count"] += 1
            if event_type == "file_access":
                pid_stats[pid]["file_access_count"] += 1
                if event.get("pathname"):
                    pid_stats[pid]["file_paths"].add(event.get("pathname"))
            elif event_type == "network_connect":
                pid_stats[pid]["network_connect_count"] += 1
                if event.get("remote_addr"):
                    pid_stats[pid]["remote_addrs"].add(str(event.get("remote_addr")))
            elif event_type == "socket_create":
                pid_stats[pid]["socket_create_count"] += 1
            elif event_type == "dns_query":
                pid_stats[pid]["dns_query_count"] += 1
                if event.get("dns_query"):
                    pid_stats[pid]["dns_queries"].add(event.get("dns_query"))

        # 构建命令摘要
        if call.tool == "exec":
            command = call.params.get("command", "")
            # 截断过长的命令
            if len(command) > 60:
                command_summary = command[:57] + "..."
            else:
                command_summary = command
        elif call.tool == "read":
            command_summary = call.params.get("file") or call.params.get("path", "")
        else:
            command_summary = str(call.params)

        # 构建关联详情条目
        detail_entry = {
            "index": idx,
            "tool": call.tool,
            "command_summary": command_summary,
            "total_events": len(call.tracee_events),
            "file_access_count": file_access_count,
            "network_connect_count": network_connect_count,
            "socket_create_count": socket_create_count,
            "dns_query_count": dns_query_count,
            "processes": [
                {
                    "pid": stats["pid"],
                    "ppid": stats["ppid"],
                    "process_name": stats["process_name"],
                    "argv": stats["argv"][:80] + "..." if len(stats["argv"]) > 80 else stats["argv"],
                    "event_count": stats["event_count"],
                    "file_access_count": stats["file_access_count"],
                    "network_connect_count": stats["network_connect_count"],
                    "dns_query_count": stats["dns_query_count"],
                    "file_paths": sorted(list(stats["file_paths"]))[:20],  # 显示前20个文件路径
                    "remote_addrs": sorted(list(stats["remote_addrs"])),
                    "dns_queries": sorted(list(stats["dns_queries"])),
                }
                for stats in sorted(pid_stats.values(), key=lambda x: x["pid"])
            ],
        }
        correlation_details.append(detail_entry)

    # 构建报告
    report = {
        "meta": {
            "generated_at": datetime.now().isoformat(),
            "total_tool_calls": len(tool_calls),
            "total_tracee_events": total_events,
            "calls_with_events": calls_with_events,
            "calls_without_events": calls_without_events,
            "correlation_rate": f"{calls_with_events / len(tool_calls) * 100:.1f}%" if tool_calls else "0%",
        },
        "summary": {
            "tools_used": {tool: len(calls) for tool, calls in tools_by_type.items()},
            "correlation_success": {
                tool: sum(1 for call in calls if call.tracee_events)
                for tool, calls in tools_by_type.items()
            },
            # 关联失败的工具调用诊断信息
            "correlation_fail": {
                str(idx): {
                    "tool": call.tool,
                    "assigned_pids": list(call.assigned_pids) if hasattr(call, 'assigned_pids') else [],
                    "expected_patterns": call.expected_patterns if hasattr(call, 'expected_patterns') else [],
                    "status": (
                        "events_filtered_or_not_monitored" if (hasattr(call, 'assigned_pids') and call.assigned_pids) else
                        "no_matching_process"
                    ),
                    "explanation": (
                        "进程已分配但事件被过滤（系统路径）或事件类型不被监控（如chmod）" if (hasattr(call, 'assigned_pids') and call.assigned_pids) else
                        "未找到匹配的进程（关联算法问题或进程不存在）"
                    ),
                }
                for idx, call in enumerate(tool_calls, 1)
                if not call.tracee_events  # 只包含没有事件的工具调用
            },
            "processes": process_summary,
            "event_types": dict(sorted(event_type_stats.items(), key=lambda x: -x[1])),
            "unique_processes": len(process_stats),
            "unique_pids": len(set(pid for stats in process_stats.values() for pid in stats["pids"])),
        },
        "correlation_details": correlation_details,
        "tool_calls": [
            {
                "index": idx,
                "tool": call.tool,
                "params": {
                    k: v[:200] + "..." if isinstance(v, str) and len(v) > 200 else v
                    for k, v in call.params.items()
                },
                "timestamp": call.timestamp,
                "tracee_events_count": len(call.tracee_events),
                "tracee_events": call.tracee_events,  # 保留全部关联事件
                # 工具级别的进程摘要
                "processes_involved": list(set(
                    e.get("processName", "unknown") for e in call.tracee_events
                )),
            }
            for idx, call in enumerate(tool_calls, 1)
        ],
    }

    # 写入文件
    with open(output_path, "w", encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False, default=str)

    return report


def main():
    parser = argparse.ArgumentParser(
        description="关联 OpenClaw 工具调用与 Tracee 系统调用",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  python scripts/tracee_correlate.py \\
    --openclaw-log log_20260414-5000.log \\
    --tracee-log tracee_logs/tracee_task_5000_ssh-keygen-helper.json \\
    --output tracee_logs/tracee_task_5000_correlated.json
        """
    )
    parser.add_argument(
        "--openclaw-log",
        required=True,
        help="OpenClaw 日志文件路径"
    )
    parser.add_argument(
        "--tracee-log",
        required=True,
        help="Tracee 日志文件路径"
    )
    parser.add_argument(
        "--output",
        required=True,
        help="输出报告路径 (JSON 格式)"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="显示详细输出"
    )

    args = parser.parse_args()

    openclaw_path = Path(args.openclaw_log)
    tracee_path = Path(args.tracee_log)
    output_path = Path(args.output)

    # 验证输入文件
    if not openclaw_path.exists():
        print(f"错误: OpenClaw 日志文件不存在: {openclaw_path}")
        sys.exit(1)

    if not tracee_path.exists():
        print(f"错误: Tracee 日志文件不存在: {tracee_path}")
        sys.exit(1)

    # 创建输出目录
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # 解析 OpenClaw 日志
    print(f"解析 OpenClaw 日志: {openclaw_path}")
    tool_calls = parse_openclaw_log(openclaw_path)
    print(f"  找到 {len(tool_calls)} 个工具调用")

    if args.verbose:
        for idx, call in enumerate(tool_calls[:5], 1):
            print(f"    {idx}. {call.tool}({list(call.params.keys())})")

    # 解析 Tracee 日志
    print(f"解析 Tracee 日志: {tracee_path}")
    tracee_events = parse_tracee_log(tracee_path)
    print(f"  找到 {len(tracee_events)} 个系统调用事件")

    if args.verbose:
        event_types = {}
        for event in tracee_events:
            event_name = event.get("eventName", "unknown")
            event_types[event_name] = event_types.get(event_name, 0) + 1
        print(f"  事件类型分布:")
        for event_name, count in sorted(event_types.items(), key=lambda x: -x[1]):
            print(f"    - {event_name}: {count}")

    # 关联分析（使用进程树精确关联）
    print("执行关联分析...")
    tool_calls = correlate_by_path(tool_calls, tracee_events)
    tool_calls, process_map, process_tree = correlate_with_process_tree(tool_calls, tracee_events)

    # 统计关联结果
    correlated = sum(1 for call in tool_calls if call.tracee_events)
    print(f"  关联成功: {correlated}/{len(tool_calls)} ({correlated/len(tool_calls)*100:.1f}%)")

    # 生成报告（包含进程树信息）
    print(f"生成报告: {output_path}")
    report = generate_report(tool_calls, output_path, process_map, process_tree)

    # 打印摘要
    print("\n" + "=" * 60)
    print("关联分析报告摘要")
    print("=" * 60)
    print(f"总工具调用数: {report['meta']['total_tool_calls']}")
    print(f"总系统事件数: {report['meta']['total_tracee_events']}")
    print(f"关联成功率: {report['meta']['correlation_rate']}")
    print(f"\n工具使用统计:")
    for tool, count in report['summary']['tools_used'].items():
        success = report['summary']['correlation_success'].get(tool, 0)
        print(f"  - {tool}: {count} 次 (关联成功: {success})")
    print("\n完成!")


def extract_tool_calls_from_transcript(transcript_path: Path, output_path: Path | None = None) -> list[ToolCall]:
    """从 OpenClaw transcript 中提取工具调用日志

    Args:
        transcript_path: transcript 文件路径 (JSONL 格式)
        output_path: 可选，输出 OpenClaw 日志文件路径

    Returns:
        工具调用列表
    """
    tool_calls = []

    # 读取 transcript
    with open(transcript_path, encoding='utf-8') as f:
        lines = f.readlines()

    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue

        entry_type = entry.get("type")

        # 格式1: 独立的 toolCall entry (OpenClaw 新格式)
        if entry_type == "toolCall":
            tool_name = entry.get("name", "")
            tool_id = entry.get("id", "")
            tool_input = entry.get("arguments", {})

            # 创建工具调用记录
            call = ToolCall(
                timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S,%f")[:-3],
                tool=tool_name,
                params=tool_input,
            )
            tool_calls.append(call)
            continue

        # 格式2: toolResult entry (OpenClaw 新格式)
        if entry_type == "toolResult":
            tool_call_id = entry.get("toolCallId", "")
            content = entry.get("content", [])
            # 提取结果文本
            if isinstance(content, list):
                result_text = ""
                for block in content:
                    if isinstance(block, dict) and block.get("type") == "text":
                        result_text += block.get("text", "")
                    elif isinstance(block, str):
                        result_text += block
            else:
                result_text = str(content)

            # 找到对应的工具调用并设置结果
            for call in reversed(tool_calls):  # 从后往前找最近的未设置结果的
                if call.result is None:
                    call.result = result_text[:500] if len(result_text) > 500 else result_text
                    break
            continue

        # 格式3: message 中的 toolCall (OpenClaw 实际格式)
        if entry_type == "message":
            msg = entry.get("message", {})
            if msg.get("role") == "assistant":
                content = msg.get("content", [])
                for block in content:
                    if isinstance(block, dict) and block.get("type") == "toolCall":
                        tool_name = block.get("name", "")
                        tool_id = block.get("id", "")
                        tool_input = block.get("arguments", {})

                        # 创建工具调用记录
                        call = ToolCall(
                            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S,%f")[:-3],
                            tool=tool_name,
                            params=tool_input,
                        )
                        tool_calls.append(call)

            # 查找 toolResult
            elif msg.get("role") == "user":
                content = msg.get("content", [])
                for block in content:
                    if isinstance(block, dict) and block.get("type") == "tool_result":
                        tool_use_id = block.get("tool_use_id", "")
                        # 找到对应的工具调用并设置结果
                        for call in reversed(tool_calls):
                            if call.result is None:
                                call.result = str(block.get("content", ""))[:500]
                                break

    # 如果指定了输出路径，生成日志文件
    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding='utf-8') as f:
            for call in tool_calls:
                # 生成日志格式: Tool: tool_name({...})
                params_str = json.dumps(call.params, ensure_ascii=False)
                f.write(f"Tool: {call.tool}({params_str})\n")
                if call.result:
                    # 截断过长的结果
                    result_str = call.result[:500] if len(call.result) > 500 else call.result
                    f.write(f"Result: {result_str}\n")
        logger.info("生成 OpenClaw 工具调用日志: %s", output_path)

    return tool_calls


def correlate_task_logs(
    task_id: str,
    transcript_path: Path,
    tracee_log_path: Path,
    output_dir: Path,
    verbose: bool = False,
) -> Path | None:
    """关联任务日志，生成关联分析报告

    这是 benchmark.py 可以调用的可编程接口。

    Args:
        task_id: 任务 ID
        transcript_path: OpenClaw transcript 文件路径
        tracee_log_path: Tracee 日志文件路径
        output_dir: 输出目录
        verbose: 是否显示详细输出

    Returns:
        生成的关联报告路径，如果失败返回 None
    """
    # 从 tracee_log_path 提取任务文件夹路径
    # tracee_log_path 格式: output_dir/{task_id}_{timestamp}/tracee.json
    # 我们需要在同一个文件夹中保存 openclaw.log 和 correlated.json
    if tracee_log_path and tracee_log_path.exists():
        task_log_dir = tracee_log_path.parent
    else:
        # 回退到旧逻辑：使用 output_dir/task_id/
        # 但这种情况下没有时间戳，不推荐
        logger.warning("tracee_log_path 不存在，使用默认路径")
        task_log_dir = output_dir / task_id

    # 确保目录存在
    task_log_dir.mkdir(parents=True, exist_ok=True)

    # 生成 OpenClaw 工具调用日志
    openclaw_log_path = task_log_dir / "openclaw.log"
    tool_calls = extract_tool_calls_from_transcript(transcript_path, openclaw_log_path)

    if not tool_calls:
        logger.warning("未找到工具调用: %s", transcript_path)
        return None

    logger.info("从 transcript 提取了 %d 个工具调用", len(tool_calls))

    # 检查 Tracee 日志是否存在
    if not tracee_log_path.exists():
        logger.warning("Tracee 日志不存在: %s", tracee_log_path)
        return None

    # 解析 Tracee 日志
    tracee_events = parse_tracee_log(tracee_log_path)
    logger.info("解析 Tracee 日志: %d 个事件", len(tracee_events))

    # 执行关联分析（使用进程树精确关联）
    tool_calls = correlate_by_path(tool_calls, tracee_events)
    tool_calls, process_map, process_tree = correlate_with_process_tree(tool_calls, tracee_events)

    # 生成报告（包含进程树信息）
    report_path = task_log_dir / "correlated.json"
    report = generate_report(tool_calls, report_path, process_map, process_tree)

    if verbose:
        correlated = sum(1 for call in tool_calls if call.tracee_events)
        print(f"关联分析完成: {report_path}")
        print(f"  工具调用: {len(tool_calls)}")
        print(f"  系统事件: {len(tracee_events)}")
        print(f"  关联成功: {correlated}/{len(tool_calls)} ({correlated/len(tool_calls)*100:.1f}%)")
        print(f"  进程数: {report['summary']['unique_processes']}")
        print(f"  PID 数: {report['summary']['unique_pids']}")

    return report_path


if __name__ == "__main__":
    main()
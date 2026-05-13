#!/usr/bin/env python3
"""
Tracee execve 事件提取脚本

从 tracee 日志文件中提取 agent 调用工具执行的记录（execve 事件），
过滤出与目标命令相关的事件，并保存为独立的 JSON 文件。

用法:
    python scripts/tracee_extract_execve.py <input_file> [options]

示例:
    python scripts/tracee_extract_execve.py tracee_logs/tracee_task_5000.json
    python scripts/tracee_extract_execve.py tracee_logs/tracee_task_5000.json -o output.json
    python scripts/tracee_extract_execve.py tracee_logs/tracee_task_5000.json --commands python3,ls,cat
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Optional


# 默认过滤的命令关键词
DEFAULT_COMMANDS = [
    'python3', 'python',
    'ls', 'cat', 'head', 'tail', 'file', 'find', 'grep', 'sed', 'awk',
    'ssh', 'ssh-keygen', 'scp', 'rsync',
    'curl', 'wget', 'nc', 'ncat',
    'bash', 'sh', 'zsh',
    'git', 'docker', 'kubectl',
    'npm', 'node', 'yarn', 'pip', 'pip3',
    'make', 'cmake', 'gcc', 'g++',
    'tar', 'zip', 'unzip', 'gzip',
]


def extract_execve_events(
    input_file: Path,
    output_file: Optional[Path] = None,
    commands: Optional[list[str]] = None,
    verbose: bool = False
) -> dict:
    """
    从 tracee 日志文件中提取 execve 事件。

    Args:
        input_file: 输入的 tracee 日志文件路径
        output_file: 输出的 JSON 文件路径（默认为 input_execve.json）
        commands: 要过滤的命令关键词列表（默认为 DEFAULT_COMMANDS）
        verbose: 是否输出详细信息

    Returns:
        包含统计信息的字典
    """
    if commands is None:
        commands = DEFAULT_COMMANDS

    if output_file is None:
        output_file = input_file.parent / f"{input_file.stem}_execve.json"

    execve_events = []
    total_lines = 0
    total_execve = 0
    matched_execve = 0

    if verbose:
        print(f"输入文件: {input_file}")
        print(f"输出文件: {output_file}")
        print(f"过滤命令: {', '.join(commands)}")
        print()

    with open(input_file, 'r') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            total_lines += 1

            try:
                data = json.loads(line)
            except json.JSONDecodeError:
                continue

            if data.get("eventName") == "execve":
                total_execve += 1
                args = data.get("args", [])
                pathname = None
                argv = []

                for arg in args:
                    if arg.get("name") == "pathname":
                        pathname = arg.get("value")
                    elif arg.get("name") == "argv":
                        val = arg.get("value")
                        if isinstance(val, list):
                            argv = val
                        elif isinstance(val, str):
                            argv = [val]

                if pathname:
                    pathname_str = str(pathname).lower()
                    for cmd in commands:
                        cmd_lower = cmd.lower()
                        # 匹配命令名（精确匹配路径中的最后部分，或包含匹配）
                        basename = pathname_str.split('/')[-1]
                        if cmd_lower == basename or cmd_lower in pathname_str:
                            # 添加行号信息
                            data['_line_number'] = line_num
                            execve_events.append(data)
                            matched_execve += 1
                            if verbose:
                                argv_str = " ".join(str(a) for a in argv) if argv else ""
                                print(f"[{line_num}] {pathname} {argv_str}")
                            break

    # 保存为 JSON 文件
    with open(output_file, 'w') as f:
        json.dump(execve_events, f, indent=2, ensure_ascii=False)

    stats = {
        'input_file': str(input_file),
        'output_file': str(output_file),
        'total_lines': total_lines,
        'total_execve': total_execve,
        'matched_execve': matched_execve,
        'filter_commands': commands,
    }

    return stats


def main():
    parser = argparse.ArgumentParser(
        description='从 tracee 日志中提取 execve 事件记录',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s tracee_logs/tracee_task_5000.json
  %(prog)s tracee_logs/tracee_task_5000.json -o output.json
  %(prog)s tracee_logs/tracee_task_5000.json --commands python3,ls,cat
  %(prog)s tracee_logs/tracee_task_5000.json -v
        """
    )
    parser.add_argument(
        'input_file',
        type=Path,
        help='输入的 tracee 日志文件路径 (JSONL 格式)'
    )
    parser.add_argument(
        '-o', '--output',
        type=Path,
        help='输出的 JSON 文件路径 (默认: input_file_execve.json)'
    )
    parser.add_argument(
        '-c', '--commands',
        type=str,
        help='要过滤的命令关键词，逗号分隔 (默认: python3,ls,cat,ssh-keygen 等)'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='输出详细信息'
    )

    args = parser.parse_args()

    if not args.input_file.exists():
        print(f"错误: 输入文件不存在: {args.input_file}", file=sys.stderr)
        sys.exit(1)

    commands = None
    if args.commands:
        commands = [c.strip() for c in args.commands.split(',')]

    stats = extract_execve_events(
        input_file=args.input_file,
        output_file=args.output,
        commands=commands,
        verbose=args.verbose
    )

    print(f"\n提取完成!")
    print(f"  总行数: {stats['total_lines']}")
    print(f"  execve 事件: {stats['total_execve']}")
    print(f"  匹配事件: {stats['matched_execve']}")
    print(f"  输出文件: {stats['output_file']}")


if __name__ == '__main__':
    main()
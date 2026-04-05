#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import io
import sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
"""
检查文件修改范围是否符合预期
在 Claude 修改文件后自动运行
"""

import subprocess
import sys
from pathlib import Path


def main():
    file_path = sys.argv[1] if len(sys.argv) > 1 else ""

    # 获取git状态
    try:
        result = subprocess.run(
            ['git', 'status', '--short'],
            capture_output=True,
            text=True,
            cwd='.'
        )
        git_status = result.stdout.strip()
    except Exception:
        return 0

    if not git_status:
        return 0

    # 解析改动的文件
    modified_files = []
    for line in git_status.split('\n'):
        line = line.strip()
        if not line:
            continue
        # 格式: XY filename 或 X filename
        if len(line) >= 3:
            status = line[:2].strip()
            filename = line[3:].strip()
            modified_files.append((status, filename))

    if not modified_files:
        return 0

    print("")
    print("=" * 40)
    print("本次改动统计")
    print("=" * 40)

    # 显示每个改动的文件
    for status, filename in modified_files:
        symbol = {
            'M': '[M]',
            'A': '[A]',
            'D': '[D]'
        }.get(status, '[?]')

        print(f"  {symbol} {filename}")

    print("=" * 40)

    # 如果超过3个文件，输出警告
    if len(modified_files) > 3:
        print("")
        print(f"警告：改动文件数 ({len(modified_files)}) 超过 3 个")
        print("    可能违反了'单次只改一个功能'的原则")
        print("")
        print("    如需回滚，执行：git reset --hard HEAD")
        print("=" * 40)

    return 0


if __name__ == "__main__":
    sys.exit(main())

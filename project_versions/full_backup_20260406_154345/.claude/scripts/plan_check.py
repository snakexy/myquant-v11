#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import io
import sys
# 强制使用UTF-8输出
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
"""
检查是否存在计划文件，强制改前先计划
在 Claude 修改代码文件前自动运行
"""

import sys
import os
from pathlib import Path


def main():
    file_path = sys.argv[1] if len(sys.argv) > 1 else ""
    tool = sys.argv[2] if len(sys.argv) > 2 else ""

    # 只检查代码文件
    code_extensions = ['.py', '.ts', '.tsx', '.vue', '.js', '.jsx', '.java', '.go', '.rs']
    is_code_file = any(file_path.endswith(ext) for ext in code_extensions)

    if not is_code_file:
        return 0

    # 检查计划文件
    plan_file = Path(".claude/plans/current-plan.md")

    if not plan_file.exists():
        print("")
        print("=" * 40)
        print("错误：未找到计划文件")
        print("=" * 40)
        print("")
        print("必须先制定计划：")
        print("  1. 使用 EnterPlanMode 进入计划模式")
        print("  2. 制定计划并保存到 .claude/plans/current-plan.md")
        print("  3. 等待用户确认")
        print("  4. 然后才能修改代码")
        print("")
        print("=" * 40)
        print("")
        return 1

    # 计划文件存在
    print("")
    print("=" * 40)
    print("已找到计划文件")
    print("=" * 40)
    print("")

    # 显示计划摘要（前10行）
    try:
        with open(plan_file, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f):
                if i >= 10:
                    break
                print(f"  {line.rstrip()}")
    except Exception as e:
        print(f"  [读取计划文件失败: {e}]")

    print("")
    print("如果计划已执行完毕，请删除计划文件：")
    print("  rm .claude/plans/current-plan.md")
    print("")

    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import io
import sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
"""
检查架构违规
- Service层是否直接import Adapter
- 其他架构规范
"""

import os
import re
import sys
from pathlib import Path


def check_service_adapter_imports():
    """检查Service层是否直接import Adapter"""
    service_dir = Path("backend/src/myquant/core/market/services")
    violations = []

    if not service_dir.exists():
        return []

    for file_path in service_dir.glob("*.py"):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 检查是否直接import adapter
            if re.search(r'from\s+myquant\.core\.market\.adapters\.\w+\s+import', content):
                violations.append(file_path.name)
        except Exception:
            continue

    return violations


def main():
    print("")
    print("=" * 40)
    print("架构检查")
    print("=" * 40)

    # 检查Service层
    violations = check_service_adapter_imports()

    if violations:
        print("")
        print("发现架构违规：")
        print("   Service层直接import Adapter：")
        for v in violations:
            print(f"     - {v}")
        print("")
        print("   应通过 get_adapter() 工厂函数获取")
        print("=" * 40)
        return 1
    else:
        print("架构检查通过")
        print("=" * 40)
        return 0


if __name__ == "__main__":
    sys.exit(main())

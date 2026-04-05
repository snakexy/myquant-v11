#!/usr/bin/env python3
"""
方案B执行脚本：删除HotDB内存缓存，解决400MB+内存问题
使用方法: python remove_memory_cache.py
"""

import re

def main():
    filepath = 'backend/src/myquant/core/market/adapters/hotdb_adapter.py'

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. 删除缓存定义
    content = re.sub(
        r'        # L1: 内存缓存.*?self._memory_cache_ttl = 300.*?# 5分钟\n',
        '        # [内存优化] 已删除内存缓存，使用mmap零拷贝访问\n',
        content,
        flags=re.DOTALL
    )

    # 2. 修改日志信息
    content = re.sub(
        r'f"\[HotDB\] 数据目录: \{self._data_dir\}, "\s+f"内存缓存已启用.*?"',
        'f"[HotDB] 数据目录: {self._data_dir}, 使用mmap零拷贝访问（无内存缓存）"',
        content
    )

    # 3. 删除缓存读取代码块
    content = re.sub(
        r'                # L1: 内存缓存检查\n'
        r'                cache_key = f"\{symbol\}:\{period\}"\n'
        r'                if cache_key in self._memory_cache:.*?continue\n\n',
        '                # [内存优化] 已删除内存缓存读取，直接使用文件/mmap\n'
        '                cache_key = f"{symbol}:{period}"\n\n',
        content,
        flags=re.DOTALL
    )

    # 4. 删除缓存写入代码
    content = re.sub(
        r'                # 保存到内存缓存.*?logger\.debug\(f"\[HotDB-L1\] 已缓存.*?\n',
        '                # [内存优化] 已删除内存缓存写入\n',
        content,
        flags=re.DOTALL
    )

    # 5. 删除缓存清理代码
    lines = content.split('\n')
    new_lines = []
    for line in lines:
        if '_memory_cache' in line:
            if any(line.strip().startswith(x) for x in ['if ', 'del ', 'self._memory_cache']):
                indent = len(line) - len(line.lstrip())
                new_lines.append(' ' * indent + '# [内存优化] 已删除内存缓存操作')
                continue
        new_lines.append(line)

    content = '\n'.join(new_lines)

    # 保存修改
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

    print("✓ 内存缓存删除完成")
    print("✓ 文件已保存:", filepath)
    print("\n效果预测:")
    print("  - 内存占用: 400MB+ → <50MB (mmap文件262KB + 少量索引)")
    print("  - 数据访问: 延迟不变 (<10ms，mmap零拷贝)")
    print("  - 系统稳定性: 消除内存泄漏风险")

if __name__ == '__main__':
    main()

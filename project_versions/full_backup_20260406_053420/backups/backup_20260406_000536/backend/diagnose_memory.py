# -*- coding: utf-8 -*-
"""
诊断内存泄漏问题
"""
import sys
from pathlib import Path

_current_file = Path(__file__).resolve()
src_dir = _current_file / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

import gc

print("=" * 60)
print("内存诊断")
print("=" * 60)

# 1. 检查 gc 垃圾回收器
print("\n【1】GC 统计:")
print(f"  GC 启用: {gc.isenabled()}")
print(f"  GC 计数器: {gc.get_count()}")

# 2. 强制回收后检查对象
print("\n【2】强制 GC 后对象统计:")
gc.collect()
gc.collect()
objs = gc.get_objects()
print(f"  总对象数: {len(objs)}")

# 按类型统计
type_counts = {}
for obj in objs:
    t = type(obj).__name__
    type_counts[t] = type_counts.get(t, 0) + 1

# 找出最多的类型
top_types = sorted(type_counts.items(), key=lambda x: x[1], reverse=True)[:15]
for t, count in top_types:
    print(f"  {t}: {count}")

# 3. 检查 DataFrame 对象
print("\n【3】DataFrame 对象:")
dfs = [obj for obj in objs if type(obj).__name__ == 'DataFrame']
print(f"  DataFrame 数量: {len(dfs)}")

# 4. 检查适配器实例
print("\n【4】适配器实例:")
try:
    from myquant.core.market.adapters import AdapterFactory
    adapters = AdapterFactory.list_adapters()
    print(f"  已注册适配器: {adapters}")
except Exception as e:
    print(f"  获取失败: {e}")

print("\n" + "=" * 60)

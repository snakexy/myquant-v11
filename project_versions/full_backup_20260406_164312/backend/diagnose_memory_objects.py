"""诊断内存占用 - 找出哪些对象占用最多内存"""
import gc
import sys
from collections import Counter
from typing import Any

def get_size(obj: Any, seen=None) -> int:
    """递归获取对象大小"""
    size = sys.getsizeof(obj)
    if seen is None:
        seen = set()

    obj_id = id(obj)
    if obj_id in seen:
        return 0

    seen.add(obj_id)

    if isinstance(obj, dict):
        size += sum(get_size(k, seen) + get_size(v, seen) for k, v in obj.items())
    elif hasattr(obj, '__dict__'):
        size += get_size(obj.__dict__, seen)
    elif hasattr(obj, '__iter__') and not isinstance(obj, (str, bytes, bytearray)):
        try:
            size += sum(get_size(i, seen) for i in obj)
        except:
            pass

    return size

def diagnose_memory():
    """诊断内存占用"""
    gc.collect()

    # 统计对象类型
    type_count = Counter()
    type_size = {}

    for obj in gc.get_objects():
        obj_type = type(obj).__name__
        type_count[obj_type] += 1
        if obj_type not in type_size:
            type_size[obj_type] = 0
        type_size[obj_type] += sys.getsizeof(obj)

    # 打印占用最多的类型
    print("=== 对象数量排名 ===")
    for obj_type, count in type_count.most_common(20):
        print(f"{obj_type}: {count} 个")

    print("\n=== 内存占用排名 ===")
    for obj_type, size in sorted(type_size.items(), key=lambda x: x[1], reverse=True)[:20]:
        print(f"{obj_type}: {size / 1024 / 1024:.1f} MB")

if __name__ == "__main__":
    diagnose_memory()

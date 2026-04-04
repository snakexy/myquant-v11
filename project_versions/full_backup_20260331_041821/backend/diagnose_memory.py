"""内存诊断脚本 - 检查后端内存占用"""

import sys
import gc
import tracemalloc

def get_top_memory_users(limit=20):
    """获取内存占用最大的对象"""
    # 强制垃圾回收
    gc.collect()

    # 获取所有对象
    all_objects = gc.get_objects()

    # 按大小排序
    sized_objects = []
    for obj in all_objects:
        try:
            size = sys.getsizeof(obj)
            if size > 1024:  # 只关心大于1KB的对象
                sized_objects.append((size, type(obj).__name__, repr(obj)[:100]))
        except:
            pass

    sized_objects.sort(reverse=True, key=lambda x: x[0])

    return sized_objects[:limit]


def analyze_dataframes():
    """分析所有 DataFrame 对象"""
    import pandas as pd

    gc.collect()
    all_objects = gc.get_objects()

    dataframes = []
    for obj in all_objects:
        if isinstance(obj, pd.DataFrame):
            try:
                memory_mb = obj.memory_usage(deep=True).sum() / 1024 / 1024
                dataframes.append({
                    'memory_mb': memory_mb,
                    'shape': obj.shape,
                    'columns': list(obj.columns)[:5],  # 只显示前5列
                })
            except:
                pass

    dataframes.sort(reverse=True, key=lambda x: x['memory_mb'])
    return dataframes[:10]


def analyze_module_memory():
    """分析各模块内存占用"""
    import sys

    module_sizes = {}
    for name, module in sys.modules.items():
        if module is not None:
            try:
                size = sys.getsizeof(module)
                module_sizes[name] = size
            except:
                pass

    sorted_modules = sorted(module_sizes.items(), key=lambda x: x[1], reverse=True)
    return sorted_modules[:20]


if __name__ == "__main__":
    print("=" * 60)
    print("Python 内存诊断")
    print("=" * 60)

    # 1. 总体内存信息
    print("\n【总体信息】")
    print(f"Python 版本: {sys.version}")
    print(f"已加载模块数: {len(sys.modules)}")

    # 2. DataFrame 分析
    print("\n【DataFrame 对象】")
    dfs = analyze_dataframes()
    if dfs:
        print(f"找到 {len(dfs)} 个 DataFrame 对象")
        total_df_mb = sum(d['memory_mb'] for d in dfs)
        print(f"总内存占用: {total_df_mb:.2f} MB")
        for i, df_info in enumerate(dfs[:10], 1):
            print(f"  {i}. {df_info['memory_mb']:.2f} MB - shape={df_info['shape']}, cols={df_info['columns']}")
    else:
        print("未找到 DataFrame 对象")

    # 3. 最大对象
    print("\n【内存占用最大的对象】")
    top_objects = get_top_memory_users(15)
    for i, (size, type_name, repr_str) in enumerate(top_objects, 1):
        print(f"  {i}. {size:>12} bytes - {type_name}")
        if size > 1024 * 1024:  # 大于1MB的对象显示详情
            print(f"      {repr_str}")

    # 4. 模块内存
    print("\n【模块内存占用】")
    top_modules = analyze_module_memory()
    for i, (name, size) in enumerate(top_modules[:15], 1):
        print(f"  {i}. {size:>12} bytes - {name}")

    # 5. 检查特定服务
    print("\n【服务状态】")
    try:
        from myquant.core.market.services.intraday_service import get_intraday_kline_service
        svc = get_intraday_kline_service()
        print(f"IntradayKlineService 缓存大小: {len(svc._cache)}")
    except Exception as e:
        print(f"无法获取 IntradayKlineService: {e}")

    try:
        from myquant.core.market.adapters import get_adapter
        hotdb = get_adapter('hotdb')
        if hotdb and hasattr(hotdb, '_memory_cache'):
            print(f"HotDB 内存缓存项数: {len(hotdb._memory_cache)}")
    except Exception as e:
        print(f"无法获取 HotDB: {e}")

    print("\n" + "=" * 60)

"""深度内存泄漏分析 - 找出 363 MB 差异的来源"""
import gc
import sys
import psutil
import traceback
from collections import defaultdict
import pandas as pd

def find_all_referrers():
    """找出所有 DataFrame 的引用链"""
    gc.collect()

    process = psutil.Process()
    print(f"进程内存: {process.memory_info().rss / 1024 / 1024:.1f} MB")
    print("\n=== 查找所有 DataFrame 及其引用链 ===\n")

    dfs_found = []
    seen = set()

    for obj in gc.get_objects():
        if isinstance(obj, pd.DataFrame):
            obj_id = id(obj)
            if obj_id in seen:
                continue
            seen.add(obj_id)

            try:
                df_info = {
                    'id': obj_id,
                    'rows': len(obj),
                    'cols': len(obj.columns),
                    'memory_mb': obj.memory_usage(deep=True).sum() / 1024 / 1024,
                    'columns': list(obj.columns),
                }

                # 获取引用链
                referrers = gc.get_referrers(obj)
                df_info['referrers'] = []

                for ref in referrers[:20]:  # 最多查看20个引用
                    ref_type = type(ref).__name__
                    ref_info = {'type': ref_type}

                    if ref_type == 'dict':
                        ref_info['keys_sample'] = list(ref.keys())[:5]
                        # 尝试找出这个字典属于谁
                        dict_referrers = gc.get_referrers(ref)
                        for dict_ref in dict_referrers[:3]:
                            if hasattr(dict_ref, '__name__'):
                                ref_info['owned_by'] = f"{type(dict_ref).__name__} ({dict_ref.__name__})"
                                break
                            elif hasattr(dict_ref, '__class__'):
                                ref_info['owned_by'] = type(dict_ref).__name__
                                break

                    elif ref_type == 'list':
                        ref_info['length'] = len(ref)

                    elif ref_type == 'frame':
                        ref_info['function'] = ref.f_code.co_name if hasattr(ref, 'f_code') else 'unknown'

                    df_info['referrers'].append(ref_info)

                dfs_found.append(df_info)
            except Exception as e:
                pass

    # 按内存大小排序
    dfs_found.sort(key=lambda x: x['memory_mb'], reverse=True)

    print(f"找到 {len(dfs_found)} 个 DataFrame:\n")
    total_memory = 0
    for i, df in enumerate(dfs_found[:10], 1):
        total_memory += df['memory_mb']
        print(f"{i}. {df['rows']} 行 x {df['cols']} 列 = {df['memory_mb']:.2f} MB")
        print(f"   列: {df['columns']}")

        if df['referrers']:
            print(f"   被以下对象引用:")
            for ref in df['referrers']:
                print(f"     - {ref['type']}: {ref.get('owned_by', ref.get('keys_sample', ref.get('length', '')))}")
        print()

    print(f"DataFrame 总内存: {total_memory:.2f} MB")
    print(f"进程内存: {process.memory_info().rss / 1024 / 1024:.1f} MB")
    print(f"差异: {process.memory_info().rss / 1024 / 1024 - total_memory:.1f} MB")

    return dfs_found


def find_large_arrays():
    """找出所有大 numpy 数组"""
    import numpy as np

    gc.collect()

    arrays = []
    for obj in gc.get_objects():
        if isinstance(obj, np.ndarray):
            try:
                size_mb = obj.nbytes / 1024 / 1024
                if size_mb >= 0.1:  # 大于 100KB
                    arrays.append({
                        'shape': obj.shape,
                        'dtype': str(obj.dtype),
                        'size_mb': size_mb,
                    })
            except:
                pass

    arrays.sort(key=lambda x: x['size_mb'], reverse=True)

    print(f"\n找到 {len(arrays)} 个大数组 (>100KB):")
    for i, arr in enumerate(arrays[:20], 1):
        print(f"{i}. shape={arr['shape']}, dtype={arr['dtype']}, size={arr['size_mb']:.2f} MB")

    return arrays


def check_global_caches():
    """检查全局缓存"""
    print("\n=== 检查已知全局缓存 ===\n")

    # 检查 AdjustmentCalculator
    try:
        from myquant.core.market.utils.adjustment_calculator import get_adjustment_calculator
        calc = get_adjustment_calculator()
        if hasattr(calc, '_xdxr_cache'):
            cache = calc._xdxr_cache
            print(f"XdxrCache: {len(cache._cache)} 个条目")
            for symbol, (df, expire) in list(cache._cache.items())[:5]:
                print(f"  - {symbol}: {df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB")
    except Exception as e:
        print(f"无法检查 XdxrCache: {e}")

    # 检查 KlineService
    try:
        from myquant.core.market.services.kline_service import get_kline_service
        kline_svc = get_kline_service()
        attrs = [attr for attr in dir(kline_svc) if not attr.startswith('__')]
        print(f"\nKlineService 属性: {[a for a in attrs if 'cache' in a.lower() or 'data' in a.lower()]}")
    except Exception as e:
        print(f"无法检查 KlineService: {e}")


if __name__ == "__main__":
    find_all_referrers()
    find_large_arrays()
    check_global_caches()

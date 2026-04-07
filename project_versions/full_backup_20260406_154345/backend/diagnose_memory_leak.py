# -*- coding: utf-8 -*-
"""
内存泄漏诊断工具

检查 Python 进程内存占用，定位泄漏源
"""

import gc
import sys
from pathlib import Path
import time

# 添加 src 到路径
src_dir = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_dir))


def get_size(obj, seen=None):
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
    elif isinstance(obj, (list, tuple, set, frozenset)):
        size += sum(get_size(item, seen) for item in obj)
    elif hasattr(obj, '__dict__'):
        size += get_size(obj.__dict__, seen)

    return size


def diagnose_memory():
    """诊断内存占用"""

    print("=" * 60)
    print("MyQuant v11 内存泄漏诊断")
    print("=" * 60)

    # 1. 检查 HotDB 缓存
    print("\n[1] HotDB L1 内存缓存")
    print("-" * 40)
    try:
        from myquant.core.market.adapters import get_adapter
        hotdb = get_adapter('hotdb')
        if hotdb:
            cache_count = len(hotdb._memory_cache)
            cache_keys = list(hotdb._memory_cache.keys())

            print(f"缓存项数量: {cache_count}")
            print(f"缓存键: {cache_keys[:10]}...")  # 只显示前10个

            if cache_count > 0:
                # 计算缓存总大小
                total_size = 0
                for key, df in hotdb._memory_cache.items():
                    df_size = df.memory_usage(deep=True).sum()
                    total_size += df_size
                    print(f"  {key}: {len(df)} 行, {df_size / 1024:.1f} KB")

                print(f"\nHotDB 缓存总大小: {total_size / 1024 / 1024:.2f} MB")

                if cache_count > 100:
                    print(f"⚠️  警告: 缓存项过多 ({cache_count} 项)，可能需要清理！")
        else:
            print("HotDB 未初始化")
    except Exception as e:
        print(f"检查失败: {e}")

    # 2. 检查 IntradayKlineService 缓存
    print("\n[2] IntradayKlineService 缓存")
    print("-" * 40)
    try:
        from myquant.core.market.services.intraday_service import get_intraday_kline_service
        svc = get_intraday_kline_service()
        cache_count = len(svc._cache)
        print(f"缓存项数量: {cache_count}")

        if cache_count > 50:
            print(f"⚠️  警告: IntradayKlineService 缓存过多 ({cache_count} 项)")
            for key in list(svc._cache.keys())[:10]:
                print(f"  {key}")
    except Exception as e:
        print(f"检查失败: {e}")

    # 3. 检查 SeamlessKlineService 缓存
    print("\n[3] SeamlessKlineService 缓存")
    print("-" * 40)
    try:
        from myquant.core.market.services.seamless_service import SeamlessKlineService
        # 这是一个新实例，实际应该用单例
        svc = SeamlessKlineService()
        print(f"XDXR 缓存大小: {svc._xdxr_cache._maxsize}")
        print(f"K线 缓存大小: {svc._kline_cache._maxsize}")
        print(f"XDXR 当前缓存: {len(svc._xdxr_cache._cache)} 项")
        print(f"K线 当前缓存: {len(svc._kline_cache._cache)} 项")
    except Exception as e:
        print(f"检查失败: {e}")

    # 4. 检查 AdjustmentFactorService 缓存
    print("\n[4] AdjustmentFactorService 缓存")
    print("-" * 40)
    try:
        from myquant.core.market.services.adjustment_factor_service import get_adjustment_factor_service
        svc = get_adjustment_factor_service()
        print(f"因子缓存大小: {svc._factor_cache._maxsize}")
        print(f"当前缓存: {len(svc._factor_cache._cache)} 项")
    except Exception as e:
        print(f"检查失败: {e}")

    # 5. 检查 WebSocket 连接
    print("\n[5] WebSocket 连接状态")
    print("-" * 40)
    try:
        from myquant.core.market.services.kline_service import get_kline_service
        svc = get_kline_service()
        clients_count = sum(len(clients) for clients in svc._clients.values())
        print(f"活跃订阅股票数: {len(svc._clients)}")
        print(f"WebSocket 连接数: {clients_count}")

        if len(svc._clients) > 0:
            print(f"订阅的股票: {list(svc._clients.keys())}")
    except Exception as e:
        print(f"检查失败: {e}")

    # 6. 检查 AdapterFactory 实例
    print("\n[6] AdapterFactory 单例实例")
    print("-" * 40)
    try:
        from myquant.core.market.adapters import AdapterFactory
        print(f"已创建的适配器: {list(AdapterFactory._instances.keys())}")

        for name, instance in AdapterFactory._instances.items():
            size = get_size(instance)
            print(f"  {name}: {size / 1024:.1f} KB")
    except Exception as e:
        print(f"检查失败: {e}")

    # 7. GC 统计
    print("\n[7] Python GC 统计")
    print("-" * 40)
    print(f"GC 计数: {gc.get_count()}")
    print(f"GC 阈值: {gc.get_threshold()}")

    # 手动触发 GC
    print("\n触发垃圾回收...")
    gc.collect()
    print(f"GC 后计数: {gc.get_count()}")

    # 8. 最大的对象
    print("\n[8] 最大的对象 (Top 20)")
    print("-" * 40)
    all_objects = gc.get_objects()
    sizes = [(get_size(obj), obj) for obj in all_objects]
    sizes.sort(key=lambda x: x[0], reverse=True)

    for i, (size, obj) in enumerate(sizes[:20]):
        obj_type = type(obj).__name__
        print(f"{i+1}. {obj_type}: {size / 1024:.1f} KB")

    print("\n" + "=" * 60)
    print("诊断完成")
    print("=" * 60)


def clear_hotdb_cache():
    """清理 HotDB L1 缓存"""
    try:
        from myquant.core.market.adapters import get_adapter
        hotdb = get_adapter('hotdb')
        if hotdb:
            count = len(hotdb._memory_cache)
            hotdb._memory_cache.clear()
            hotdb._memory_cache_time.clear()
            print(f"✅ 已清理 HotDB 缓存: {count} 项")
        else:
            print("HotDB 未初始化")
    except Exception as e:
        print(f"清理失败: {e}")


def clear_intraday_cache():
    """清理 IntradayKlineService 缓存"""
    try:
        from myquant.core.market.services.intraday_service import get_intraday_kline_service
        svc = get_intraday_kline_service()
        count = len(svc._cache)
        svc.clear_cache()
        print(f"✅ 已清理 IntradayKlineService 缓存: {count} 项")
    except Exception as e:
        print(f"清理失败: {e}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="内存泄漏诊断工具")
    parser.add_argument("--clear", action="store_true", help="清理所有缓存")
    parser.add_argument("--clear-hotdb", action="store_true", help="只清理 HotDB 缓存")
    parser.add_argument("--clear-intraday", action="store_true", help="只清理 Intraday 缓存")

    args = parser.parse_args()

    if args.clear:
        print("清理所有缓存...")
        clear_hotdb_cache()
        clear_intraday_cache()
    elif args.clear_hotdb:
        clear_hotdb_cache()
    elif args.clear_intraday:
        clear_intraday_cache()
    else:
        diagnose_memory()

"""
系统监控 API 路由

提供内存监控、缓存清理等功能
"""

import psutil
import os
import gc
import sys
import asyncio
from fastapi import APIRouter
from typing import Dict, Any
from loguru import logger

from myquant.core.market.services.cache_manager_service import get_cache_manager, CachePartition


router = APIRouter(tags=["系统监控"])


@router.get("/memory")
async def get_memory_usage(analyze: bool = False) -> Dict[str, Any]:
    """获取系统内存使用情况"""
    process = psutil.Process(os.getpid())
    mem_info = process.memory_info()

    # 获取缓存统计
    cache_manager = get_cache_manager()
    cache_stats = cache_manager.get_stats()
    cache_memory = cache_manager.get_memory_usage()

    result = {
        "process": {
            "rss_mb": mem_info.rss / 1024 / 1024,  # 物理内存
            "vms_mb": mem_info.vms / 1024 / 1024,  # 虚拟内存
        },
        "cache": {
            "total_mb": cache_memory["cache_mb"],
            "partitions": cache_memory["partitions"],
            "stats": cache_stats,
        }
    }

    # 如果需要深度分析
    if analyze:
        import gc
        import pandas as pd
        from collections import Counter

        gc.collect()

        # 统计 DataFrame
        dfs = []
        for obj in gc.get_objects():
            if isinstance(obj, pd.DataFrame):
                try:
                    dfs.append({
                        'rows': len(obj),
                        'cols': len(obj.columns),
                        'memory_mb': obj.memory_usage(deep=True).sum() / 1024 / 1024,
                    })
                except:
                    pass

        # 统计对象类型
        type_count = Counter()
        for obj in gc.get_objects():
            try:
                type_count[type(obj).__name__] += 1
            except:
                pass

        result['analysis'] = {
            'dataframe_count': len(dfs),
            'dataframe_memory_mb': round(sum(d['memory_mb'] for d in dfs), 2),
            'dataframes': dfs[:10],
            'top_object_types': dict(list(type_count.most_common(10))),
        }

        # 检查 C 扩展模块
        extensions = [mod for mod in sys.modules.values() if mod and hasattr(mod, '__file__') and mod.__file__ and ('.pyd' in mod.__file__ or '.so' in mod.__file__)]
        result['c_extensions'] = [
            {'name': ext.__name__, 'file': ext.__file__}
            for ext in extensions[:20]
        ]

        # 深度分析：找出所有 DataFrame 的引用链
        import pandas as pd
        df_details = []
        try:
            for obj in gc.get_objects():
                if isinstance(obj, pd.DataFrame):
                    try:
                        obj_id = id(obj)
                        referrers = gc.get_referrers(obj)

                        df_info = {
                            'rows': len(obj),
                            'cols': len(obj.columns),
                            'memory_mb': round(obj.memory_usage(deep=True).sum() / 1024 / 1024, 2),
                            'ref_count': len(referrers),
                        }

                        # 简化引用者信息
                        df_info['referrers'] = [type(r).__name__ for r in referrers[:3]]
                        df_details.append(df_info)
                    except:
                        pass
        except Exception as e:
            df_details = [{'error': str(e)}]

        df_details.sort(key=lambda x: x.get('memory_mb', 0), reverse=True)
        result['dataframe_details'] = df_details[:10]

    return result


@router.post("/cache/clear")
async def clear_cache(partition: str = "all") -> Dict[str, Any]:
    """清理缓存并强制释放内存"""
    cache_manager = get_cache_manager()

    if partition == "all":
        cache_manager.clear_all()
    else:
        try:
            partition_enum = CachePartition(partition)
            cache_manager.clear_partition(partition_enum)
        except ValueError:
            return {"success": False, "message": f"无效的分区: {partition}"}

    # 清理所有服务缓存
    from myquant.core.market.services import get_realtime_market_service
    from myquant.core.market.services.adjustment_factor_service import get_adjustment_factor_service
    from myquant.core.market.services.seamless_service import get_seamless_kline_service

    # 清理实时行情服务
    try:
        realtime_svc = get_realtime_market_service()
        if hasattr(realtime_svc, '_quote_cache'):
            realtime_svc._quote_cache.clear()
        if hasattr(realtime_svc, '_adapter_cache'):
            realtime_svc._adapter_cache.clear()
        if hasattr(realtime_svc, '_aggregator'):
            aggregator = realtime_svc._aggregator
            if hasattr(aggregator, '_last_bar'):
                aggregator._last_bar.clear()
            if hasattr(aggregator, '_last_count'):
                aggregator._last_count.clear()
    except Exception:
        pass

    # 清理复权因子服务缓存
    cleared_factor = False
    try:
        factor_svc = get_adjustment_factor_service()
        if hasattr(factor_svc, '_factor_cache'):
            size_before = factor_svc._factor_cache.get_stats()['size']
            factor_svc._factor_cache.clear()
            cleared_factor = True
            logger.info(f"[System] 清理复权因子缓存: {size_before} 条")
    except Exception as e:
        logger.warning(f"[System] 清理复权因子缓存失败: {e}")

    # 清理无缝K线服务缓存
    cleared_seamless = False
    try:
        seamless_svc = get_seamless_kline_service()
        if hasattr(seamless_svc, '_adapter_cache'):
            seamless_svc._adapter_cache.clear()
            cleared_seamless = True
            logger.info("[System] 清理无缝K线适配器缓存")
    except Exception as e:
        logger.warning(f"[System] 清理无缝K线缓存失败: {e}")

    # 多次垃圾回收（处理循环引用）
    freed_before = psutil.Process(os.getpid()).memory_info().rss
    for _ in range(3):
        gc.collect()

    freed_after = psutil.Process(os.getpid()).memory_info().rss
    freed_mb = (freed_before - freed_after) / 1024 / 1024

    return {"success": True, "message": f"已清空缓存并释放 {freed_mb:.1f} MB"}


@router.post("/gc/collect")
async def force_gc_collect() -> Dict[str, Any]:
    """强制垃圾回收"""
    before = psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024

    # 清理所有服务缓存
    from myquant.core.market.services import get_realtime_market_service
    from myquant.core.market.services.adjustment_factor_service import get_adjustment_factor_service
    from myquant.core.market.services.seamless_service import get_seamless_kline_service

    # 清理实时行情服务
    try:
        realtime_svc = get_realtime_market_service()
        if hasattr(realtime_svc, '_quote_cache'):
            realtime_svc._quote_cache.clear()
        if hasattr(realtime_svc, '_adapter_cache'):
            realtime_svc._adapter_cache.clear()
    except Exception:
        pass

    # 清理聚合器状态
    try:
        if hasattr(realtime_svc, '_aggregator'):
            aggregator = realtime_svc._aggregator
            if hasattr(aggregator, '_last_bar'):
                aggregator._last_bar.clear()
            if hasattr(aggregator, '_last_count'):
                aggregator._last_count.clear()
    except Exception:
        pass

    # 清理复权因子服务缓存
    try:
        factor_svc = get_adjustment_factor_service()
        if hasattr(factor_svc, '_factor_cache'):
            factor_svc._factor_cache.clear()
    except Exception:
        pass

    # 清理无缝K线服务缓存
    try:
        seamless_svc = get_seamless_kline_service()
        if hasattr(seamless_svc, '_adapter_cache'):
            seamless_svc._adapter_cache.clear()
    except Exception:
        pass

    collected = gc.collect()
    after = psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024

    return {
        "success": True,
        "collected": collected,
        "memory_before_mb": before,
        "memory_after_mb": after,
        "freed_mb": before - after
    }


@router.post("/cache/cleanup")
async def cleanup_cache(
    partition: str = "all",
    max_keep: int = 50,
    max_age_seconds: int = 300
) -> Dict[str, Any]:
    """清理旧缓存

    Args:
        partition: 缓存分区名称
        max_keep: 保留的最大条目数
        max_age_seconds: 最大保留时间（秒）
    """
    cache_manager = get_cache_manager()
    results = {}

    partitions = [CachePartition(partition)] if partition != "all" else list(CachePartition)

    for p in partitions:
        evicted = cache_manager.force_evict(p, max_keep=max_keep)
        cleaned = cache_manager.cleanup_old_entries(p, max_age_seconds=max_age_seconds)
        results[p.value] = {"evicted": evicted, "cleaned": cleaned}

    return {"success": True, "results": results}


@router.post("/cache/evict")
async def force_evict(partition: str = "merged_kline", max_keep: int = 30) -> Dict[str, Any]:
    """强制淘汰缓存，只保留最近使用的条目

    Args:
        partition: 缓存分区名称
        max_keep: 保留的最大条目数
    """
    cache_manager = get_cache_manager()

    try:
        partition_enum = CachePartition(partition)
        evicted = cache_manager.force_evict(partition_enum, max_keep=max_keep)
        return {
            "success": True,
            "partition": partition,
            "evicted": evicted,
            "message": f"已淘汰 {evicted} 个缓存条目，保留 {max_keep} 个"
        }
    except ValueError:
        return {"success": False, "message": f"无效的分区: {partition}"}


@router.post("/restart")
async def restart_backend() -> Dict[str, Any]:
    """重启后端服务（释放所有内存）"""
    import os
    import signal

    # 发送重启信号给自身
    logger.warning("[System] 正在重启后端服务以释放内存...")

    # 给客户端时间响应
    await asyncio.sleep(1)

    # 杀死自身
    os.kill(os.getpid(), signal.SIGTERM)

    return {"success": True, "message": "后端正在重启..."}


@router.get("/memory/monitor")
async def monitor_memory() -> Dict[str, Any]:
    """实时内存监控"""
    process = psutil.Process(os.getpid())
    mem_info = process.memory_info()

    # 检查是否需要重启
    rss_mb = mem_info.rss / 1024 / 1024
    need_restart = rss_mb > 500

    return {
        "rss_mb": rss_mb,
        "vms_mb": mem_info.vms / 1024 / 1024,
        "need_restart": need_restart,
        "recommendation": "建议重启后端" if need_restart else "正常"
    }


# 兼容前端调用的 debug 路由
@router.post("/debug/memory/clear_hotdb")
async def clear_hotdb_cache() -> Dict[str, Any]:
    """清理 HotDB 缓存（前端调用）"""
    return await clear_cache(partition="raw_kline")


@router.get("/debug/validation-errors")
async def get_validation_errors(limit: int = 10) -> Dict[str, Any]:
    """获取验证错误（前端调用）"""
    return {"errors": [], "count": 0}


@router.get("/debug/analyze-memory")
async def analyze_memory_in_process() -> Dict[str, Any]:
    """在进程内分析内存"""
    import gc
    import pandas as pd

    gc.collect()

    # 统计 DataFrame
    dfs = []
    for obj in gc.get_objects():
        if isinstance(obj, pd.DataFrame):
            dfs.append({
                'rows': len(obj),
                'cols': len(obj.columns),
                'memory_mb': obj.memory_usage(deep=True).sum() / 1024 / 1024,
            })

    # 统计对象类型
    from collections import Counter
    type_count = Counter()
    for obj in gc.get_objects():
        try:
            type_count[type(obj).__name__] += 1
        except:
            pass

    return {
        'dataframe_count': len(dfs),
        'dataframe_memory_mb': sum(d['memory_mb'] for d in dfs),
        'dataframes': dfs[:20],
        'top_object_types': dict(type_count.most_common(20)),
    }

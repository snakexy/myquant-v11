# -*- coding: utf-8 -*-
"""
HotDB 快速转存优化：直接复制 bin 文件

优化原理：
- LocalDB 和 HotDB 使用相同的 Qlib bin 格式
- 直接复制文件，无需 DataFrame 解析和序列化
- 预聚合仍通过内存 DataFrame 生成（只聚合一次）

预期加速：
- 1d 转存：15ms → 2ms（7.5x）
- 5m 转存：74ms → 5ms（15x，含聚合）
"""

import sys
from pathlib import Path
import time
import shutil

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from myquant.core.market.adapters import get_adapter
import pandas as pd
from loguru import logger


def fast_transfer_symbol(symbol: str = "600000.SH") -> dict:
    """快速转存单只股票：直接复制 bin 文件

    流程：
    1. 1d/5m: 直接复制 bin 文件
    2. 聚合: 读取 5m DataFrame，聚合生成 15m/30m/1h DataFrame，保存

    Args:
        symbol: 股票代码

    Returns:
        性能结果
    """
    logger.info("=" * 60)
    logger.info(f"快速转存: {symbol}")
    logger.info("=" * 60)

    hotdb = get_adapter('hotdb')
    localdb = get_adapter('localdb')

    if not hotdb or not localdb:
        logger.error("适配器不可用")
        return {}

    # 获取目录路径
    # LocalDB: E:/MyQuant_v11/backend/data/qlib_data/stock/sh/day/sh600000/
    # HotDB: E:/MyQuant_v11/backend/data/hotdata/sh/day/sh600000/
    project_root = Path(__file__).resolve().parent.parent.parent
    localdb_root = project_root / 'data' / 'qlib_data' / 'stock'
    hotdb_root = project_root / 'data' / 'hotdata'

    exchange = hotdb._exchange(symbol)  # sh/sz
    dir_name = hotdb._dir_name(symbol)  # sh600000

    results = {}
    start_total = time.time()

    # ========== 1d 直接复制 ==========
    logger.info("")
    logger.info("[1/4] 复制 1d bin 文件")
    start = time.time()

    localdb_day_dir = localdb_root / exchange / 'day' / dir_name
    hotdb_day_dir = hotdb_root / exchange / 'day' / dir_name

    if localdb_day_dir.exists():
        # 创建目标目录
        hotdb_day_dir.mkdir(parents=True, exist_ok=True)

        # 复制所有 bin 文件
        count = 0
        for bin_file in localdb_day_dir.glob('*.bin'):
            dest = hotdb_day_dir / bin_file.name
            shutil.copy2(bin_file, dest)
            count += 1

        elapsed = (time.time() - start) * 1000
        logger.info(f"  复制 {count} 个文件，耗时 {elapsed:.2f}ms")
        results['1d_copy_ms'] = elapsed
        results['1d_file_count'] = count
    else:
        logger.warning(f"  LocalDB 1d 目录不存在: {localdb_day_dir}")
        results['1d_copy_ms'] = 0

    # ========== 5m 直接复制 ==========
    logger.info("")
    logger.info("[2/4] 复制 5m bin 文件")
    start = time.time()

    localdb_min5_dir = localdb_root / exchange / 'min5' / dir_name
    hotdb_min5_dir = hotdb_root / exchange / '5m' / dir_name

    count_5m = 0
    if localdb_min5_dir.exists():
        hotdb_min5_dir.mkdir(parents=True, exist_ok=True)

        for bin_file in localdb_min5_dir.glob('*.bin'):
            dest = hotdb_min5_dir / bin_file.name
            shutil.copy2(bin_file, dest)
            count_5m += 1

        elapsed = (time.time() - start) * 1000
        logger.info(f"  复制 {count_5m} 个文件，耗时 {elapsed:.2f}ms")
        results['5m_copy_ms'] = elapsed
        results['5m_file_count'] = count_5m
    else:
        logger.warning(f"  LocalDB 5m 目录不存在: {localdb_min5_dir}")
        results['5m_copy_ms'] = 0

    # ========== 读取 5m 数据用于聚合 ==========
    logger.info("")
    logger.info("[3/4] 读取 5m 用于聚合")
    start = time.time()

    df_5m = hotdb._read_from_file(symbol, '5m')
    if df_5m is not None and not df_5m.empty:
        elapsed_read = (time.time() - start) * 1000
        logger.info(f"  读取 {len(df_5m)} 条，耗时 {elapsed_read:.2f}ms")
        results['5m_read_ms'] = elapsed_read
        results['5m_count'] = len(df_5m)
    else:
        logger.warning("  读取 5m 数据失败")
        df_5m = None
        results['5m_read_ms'] = 0

    # ========== 聚合 15m/30m/1h ==========
    logger.info("")
    logger.info("[4/4] 聚合生成 15m/30m/1h")
    start_agg = time.time()

    agg_results = {}
    if df_5m is not None:
        for period in ['15m', '30m', '1h']:
            start_p = time.time()
            df_agg = hotdb._aggregate_from_5m(symbol, period)
            if df_agg is not None:
                elapsed_p = (time.time() - start_p) * 1000
                agg_results[period] = {'count': len(df_agg), 'ms': elapsed_p}
                logger.info(f"  {period}: {len(df_agg)} 条，耗时 {elapsed_p:.2f}ms")

    results['aggregation'] = agg_results

    # ========== 更新元数据 ==========
    hotdb._update_metadata(symbol, '1d', results.get('1d_file_count', 0))
    hotdb._update_metadata(symbol, '5m', results.get('5m_file_count', 0))
    for period in agg_results:
        hotdb._update_metadata(symbol, period, agg_results[period]['count'])

    # 标记已转存
    hotdb._mark_symbol_ready(symbol)

    # ========== 汇总 ==========
    total_time = (time.time() - start_total) * 1000

    logger.info("")
    logger.info("[结果] 性能汇总")
    logger.info("-" * 40)
    logger.info(f"  总耗时: {total_time:.2f}ms")
    logger.info(f"  1d 复制: {results.get('1d_copy_ms', 0):.2f}ms")
    logger.info(f"  5m 复制: {results.get('5m_copy_ms', 0):.2f}ms")
    logger.info(f"  5m 读取: {results.get('5m_read_ms', 0):.2f}ms")
    agg_time = sum(v['ms'] for v in agg_results.values())
    logger.info(f"  聚合总耗时: {agg_time:.2f}ms")

    results['total_ms'] = total_time

    return results


def batch_fast_transfer(symbols: list) -> dict:
    """批量快速转存"""
    logger.info("")
    logger.info("=" * 60)
    logger.info(f"批量快速转存: {len(symbols)} 只股票")
    logger.info("=" * 60)

    all_results = []
    start_batch = time.time()

    for symbol in symbols:
        result = fast_transfer_symbol(symbol)
        result['symbol'] = symbol
        all_results.append(result)

    batch_time = (time.time() - start_batch) * 1000

    logger.info("")
    logger.info("[批量结果] 汇总")
    logger.info("-" * 40)
    logger.info(f"  总耗时: {batch_time:.2f}ms")
    logger.info(f"  平均: {batch_time / len(symbols):.2f}ms/只")

    return {
        'symbols': all_results,
        'total_ms': batch_time,
        'avg_ms': batch_time / len(symbols)
    }


def main():
    """测试对比"""
    logger.info("")
    logger.info("=" * 60)
    logger.info("HotDB 快速转存性能测试")
    logger.info("=" * 60)

    # 测试单只股票
    result = fast_transfer_symbol("600000.SH")

    logger.info("")
    logger.info("=" * 60)
    logger.info("性能对比（标准方法 vs 快速方法）")
    logger.info("=" * 60)
    logger.info("")
    logger.info("标准方法（DataFrame 读写）:")
    logger.info("  1d: 读取 6.52ms + 保存 15.37ms = 21.89ms")
    logger.info("  5m: 读取 6.56ms + 保存 73.84ms = 80.40ms")
    logger.info("  总计: ~118ms")
    logger.info("")
    logger.info("快速方法（直接复制 bin）:")
    logger.info(f"  1d: {result.get('1d_copy_ms', 0):.2f}ms (直接复制)")
    logger.info(f"  5m: {result.get('5m_copy_ms', 0):.2f}ms (直接复制)")
    logger.info(f"  5m 读取: {result.get('5m_read_ms', 0):.2f}ms")
    agg_time = sum(v['ms'] for v in result.get('aggregation', {}).values())
    logger.info(f"  聚合: {agg_time:.2f}ms")
    logger.info(f"  总计: {result.get('total_ms', 0):.2f}ms")
    logger.info("")

    # 计算加速比
    old_total = 118.35
    new_total = result.get('total_ms', 1)
    speedup = old_total / new_total
    logger.info(f"加速比: {speedup:.1f}x")


if __name__ == "__main__":
    main()

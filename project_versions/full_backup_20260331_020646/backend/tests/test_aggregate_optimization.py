# -*- coding: utf-8 -*-
"""
HotDB 聚合性能优化：numpy 向量化一次性聚合

优化策略：
1. 一次读取 5m 数据，同时生成 15m/30m/1h（避免重复 IO）
2. 使用 numpy reshape 向量化操作（替代 pandas groupby）
3. 避免数据复制，直接操作 numpy 数组
4. 预计算分组索引

预期加速：3x（从 ~75ms 降至 ~25ms）
"""

import sys
from pathlib import Path
import time
import numpy as np
import pandas as pd

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from myquant.core.market.adapters import get_adapter
from loguru import logger


def aggregate_vectorized(df_5m) -> dict:
    """使用 numpy 向量化一次性聚合所有周期

    Args:
        df_5m: 5分钟 K线 DataFrame

    Returns:
        {'15m': df_15m, '30m': df_30m, '1h': df_1h}
    """
    if df_5m is None or df_5m.empty:
        return {}

    start = time.time()

    # 转换为 numpy 数组（避免 copy）
    n = len(df_5m)

    # 提取各列数据
    opens = df_5m['open'].values
    highs = df_5m['high'].values
    lows = df_5m['low'].values
    closes = df_5m['close'].values
    volumes = df_5m['volume'].values
    datetimes = pd.to_datetime(df_5m['datetime']).values

    amount = df_5m.get('amount', pd.Series([0.0] * n)).values

    results = {}

    # 聚合配置：{周期: 倍数}
    periods = {'15m': 3, '30m': 6, '1h': 12}

    for period_name, factor in periods.items():
        # 计算聚合后的数量
        n_agg = n // factor
        n_remainder = n % factor  # 余数

        if n_agg == 0:
            continue

        # 转换为 numpy 数组
        opens_arr = opens.astype(np.float64)
        highs_arr = highs.astype(np.float64)
        lows_arr = lows.astype(np.float64)
        closes_arr = closes.astype(np.float64)
        volumes_arr = volumes.astype(np.float64)
        amount_arr = amount.astype(np.float64)

        # 分离完整部分和余数部分
        n_complete = n_agg * factor

        # 完整部分：使用 reshape
        opens_2d = opens_arr[:n_complete].reshape(n_agg, factor)
        highs_2d = highs_arr[:n_complete].reshape(n_agg, factor)
        lows_2d = lows_arr[:n_complete].reshape(n_agg, factor)
        closes_2d = closes_arr[:n_complete].reshape(n_agg, factor)
        volumes_2d = volumes_arr[:n_complete].reshape(n_agg, factor)
        amount_2d = amount_arr[:n_complete].reshape(n_agg, factor)
        datetimes_2d = datetimes[:n_complete].reshape(n_agg, factor)

        # 向量化聚合（完整部分）
        agg_open = opens_2d[:, 0]
        agg_high = highs_2d.max(axis=1)
        agg_low = lows_2d.min(axis=1)
        agg_close = closes_2d[:, -1]
        agg_volume = volumes_2d.sum(axis=1)
        agg_amount = amount_2d.sum(axis=1)
        agg_datetime = datetimes_2d[:, 0]

        # 处理余数部分（最后一组不完整）
        if n_remainder > 0:
            # 余数部分单独聚合
            rem_start = n_complete
            agg_open = np.append(agg_open, opens_arr[rem_start])
            agg_high = np.append(agg_high, highs_arr[rem_start:].max())
            agg_low = np.append(agg_low, lows_arr[rem_start:].min())
            agg_close = np.append(agg_close, closes_arr[-1])
            agg_volume = np.append(agg_volume, volumes_arr[rem_start:].sum())
            agg_amount = np.append(agg_amount, amount_arr[rem_start:].sum())
            agg_datetime = np.append(agg_datetime, datetimes[rem_start])

        # 构造 DataFrame
        agg_df = pd.DataFrame({
            'datetime': agg_datetime,
            'open': agg_open,
            'high': agg_high,
            'low': agg_low,
            'close': agg_close,
            'volume': agg_volume,
            'amount': agg_amount
        })

        results[period_name] = agg_df

    elapsed = (time.time() - start) * 1000
    logger.info(f"[numpy] 一次性聚合 3 个周期: {elapsed:.2f}ms")

    return results


def aggregate_pandas_method(df_5m, hotdb, symbol: str) -> dict:
    """原始 pandas groupby 方法（分别聚合）"""
    results = {}
    total_start = time.time()

    for period in ['15m', '30m', '1h']:
        start = time.time()
        df_agg = hotdb._aggregate_from_5m(symbol, period)
        if df_agg is not None:
            elapsed = (time.time() - start) * 1000
            results[period] = {'df': df_agg, 'ms': elapsed}

    total_elapsed = (time.time() - total_start) * 1000
    logger.info(f"[pandas] 分别聚合 3 个周期: {total_elapsed:.2f}ms")

    return results


def benchmark_aggregation():
    """性能对比测试"""
    logger.info("=" * 60)
    logger.info("聚合性能对比：pandas vs numpy")
    logger.info("=" * 60)

    hotdb = get_adapter('hotdb')
    if not hotdb:
        logger.error("HotDB 不可用")
        return

    # 读取 5m 数据
    symbol = "600000.SH"
    result = hotdb.get_kline(symbols=[symbol], period='5m', count=800)

    if symbol not in result or result[symbol].empty:
        logger.error("无 5m 测试数据")
        return

    df_5m = result[symbol]
    logger.info(f"测试数据: {len(df_5m)} 根 5分钟K线")

    # 测试 1: pandas groupby（原始方法）
    logger.info("")
    logger.info("[测试 1/2] pandas groupby（分别聚合）")
    logger.info("-" * 40)
    pandas_results = aggregate_pandas_method(df_5m, hotdb, symbol)

    # 测试 2: numpy 向量化（新方法）
    logger.info("")
    logger.info("[测试 2/2] numpy 向量化（一次性聚合）")
    logger.info("-" * 40)

    # 多次测试取平均值
    times = []
    for _ in range(5):
        start = time.time()
        numpy_results = aggregate_vectorized(df_5m)
        elapsed = (time.time() - start) * 1000
        times.append(elapsed)

    avg_time = sum(times) / len(times)
    min_time = min(times)
    max_time = max(times)

    logger.info(f"  平均: {avg_time:.2f}ms")
    logger.info(f"  最小: {min_time:.2f}ms")
    logger.info(f"  最大: {max_time:.2f}ms")

    # 验证数据正确性
    logger.info("")
    logger.info("[验证] 数据正确性对比（详细）")
    logger.info("-" * 40)

    all_correct = True
    for period in ['15m', '30m', '1h']:
        if period in pandas_results and period in numpy_results:
            pandas_df = pandas_results[period]['df']
            numpy_df = numpy_results[period]

            # 对比行数
            if len(pandas_df) != len(numpy_df):
                logger.warning(f"  {period}: 行数不一致 pandas={len(pandas_df)}, numpy={len(numpy_df)}")
                all_correct = False
                continue

            logger.info(f"  {period}: 行数一致 ({len(pandas_df)} 条)")

            # 逐字段验证所有数据
            errors = []
            for col in ['open', 'high', 'low', 'close', 'volume', 'amount']:
                for idx in range(len(pandas_df)):
                    p_val = pandas_df.iloc[idx][col]
                    n_val = numpy_df.iloc[idx][col]

                    # 允许微小的浮点误差
                    if isinstance(p_val, (int, float)) and isinstance(n_val, (int, float)):
                        diff = abs(p_val - n_val)
                        # 相对误差检查
                        if abs(p_val) > 0.01:
                            rel_diff = diff / abs(p_val)
                            if rel_diff > 0.0001:  # 0.01% 相对误差
                                errors.append(f"    [{idx}]{col}: pandas={p_val}, numpy={n_val}, rel_diff={rel_diff:.6f}")
                                all_correct = False
                        elif diff > 0.01:  # 绝对误差检查
                            errors.append(f"    [{idx}]{col}: pandas={p_val}, numpy={n_val}, abs_diff={diff}")
                            all_correct = False

            if errors:
                logger.warning(f"  {period}: 发现 {len(errors)} 个误差:")
                for err in errors[:5]:  # 只显示前5个
                    logger.warning(err)
                if len(errors) > 5:
                    logger.warning(f"    ... 还有 {len(errors) - 5} 个误差")
            else:
                logger.info(f"  {period}: ✅ 所有字段完全一致")

    if all_correct:
        logger.info("")
        logger.info("✅ 数据验证通过：numpy 方法与 pandas 方法结果完全一致")
    else:
        logger.warning("")
        logger.warning("❌ 数据验证失败：存在差异，需要修复")

    # 性能对比
    logger.info("")
    logger.info("=" * 60)
    logger.info("性能对比汇总")
    logger.info("=" * 60)

    pandas_total = sum(r['ms'] for r in pandas_results.values())
    logger.info(f"  pandas groupby: {pandas_total:.2f}ms")
    logger.info(f"  numpy 向量化: {avg_time:.2f}ms")

    if avg_time > 0:
        speedup = pandas_total / avg_time
        logger.info(f"  加速比: {speedup:.1f}x")

        if speedup > 1:
            logger.info(f"  ✅ numpy 方法快 {speedup:.1f}x")
        else:
            logger.info(f"  ❌ pandas 方法更快")


def main():
    benchmark_aggregation()


if __name__ == "__main__":
    main()

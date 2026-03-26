# -*- coding: utf-8 -*-
"""
HotDB 性能测试：LocalDB → HotDB 完整转存速度

测试场景：
1. 单只股票完整转存（1d + 5m → 自动聚合 15m/30m/1h）
2. 批量股票转存
3. 纯聚合性能（5m → 15m/30m/1h）
"""

import sys
from pathlib import Path
import time

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from myquant.core.market.adapters import get_adapter
from loguru import logger


def test_single_symbol_transfer(symbol: str = "600000.SH"):
    """测试单只股票完整转存速度

    包括：
    - 从 LocalDB 读取 1d 数据 → HotDB
    - 从 LocalDB 读取 5m 数据 → HotDB
    - 自动聚合 5m → 15m/30m/1h
    """
    logger.info("=" * 60)
    logger.info(f"性能测试: 单只股票转存 {symbol}")
    logger.info("=" * 60)

    # 获取适配器
    hotdb = get_adapter('hotdb')
    if not hotdb or not hotdb.is_available():
        logger.error("HotDB 不可用")
        return

    localdb = get_adapter('localdb')
    if not localdb or not localdb.is_available():
        logger.error("LocalDB 不可用")
        return

    # 禁用在线补全，避免循环依赖（HotDB → SeamlessService → HotDB）
    hotdb._try_online_completion = False

    # 先清理旧数据（确保测试准确性）
    hotdb.delete_kline(symbol)

    # ========== 完整转存测试 ==========
    logger.info("")
    logger.info("[测试] 完整转存流程（含自动聚合）")
    logger.info("-" * 40)

    start_total = time.time()

    # 1. 转存 1d
    start_1d = time.time()
    result_1d = localdb.get_kline(symbols=[symbol], period='1d', count=5000)
    time_1d_read = (time.time() - start_1d) * 1000

    if symbol in result_1d and not result_1d[symbol].empty:
        count_1d = len(result_1d[symbol])
        start_1d_save = time.time()
        hotdb.save_kline(symbol, result_1d[symbol], '1d')
        time_1d_save = (time.time() - start_1d_save) * 1000
        logger.info(f"  1d: 读取 {time_1d_read:.2f}ms, 保存 {time_1d_save:.2f}ms, {count_1d} 条")
    else:
        logger.warning(f"  1d: LocalDB 无数据")
        count_1d = 0
        time_1d_save = 0

    # 2. 转存 5m（会自动触发聚合）
    start_5m = time.time()
    result_5m = localdb.get_kline(symbols=[symbol], period='5m', count=5000)
    time_5m_read = (time.time() - start_5m) * 1000

    if symbol in result_5m and not result_5m[symbol].empty:
        count_5m = len(result_5m[symbol])
        start_5m_save = time.time()
        hotdb.save_kline(symbol, result_5m[symbol], '5m')
        time_5m_save = (time.time() - start_5m_save) * 1000
        logger.info(f"  5m: 读取 {time_5m_read:.2f}ms, 保存 {time_5m_save:.2f}ms, {count_5m} 条")
    else:
        logger.warning(f"  5m: LocalDB 无数据")
        count_5m = 0
        time_5m_save = 0

    # 3. 验证聚合结果（读取 15m/30m/1h）
    agg_results = {}
    for period in ['15m', '30m', '1h']:
        start_agg_read = time.time()
        result = hotdb.get_kline(symbols=[symbol], period=period, count=1000)
        time_agg_read = (time.time() - start_agg_read) * 1000

        if symbol in result and not result[symbol].empty:
            agg_results[period] = len(result[symbol])
            logger.info(f"  {period}: 读取 {time_agg_read:.2f}ms, {agg_results[period]} 条（聚合生成）")
        else:
            logger.warning(f"  {period}: 无数据")

    total_time = (time.time() - start_total) * 1000

    # ========== 汇总结果 ==========
    logger.info("")
    logger.info("[结果] 性能汇总")
    logger.info("-" * 40)
    logger.info(f"  总耗时: {total_time:.2f}ms")
    logger.info(f"  数据量: 1d={count_1d}条, 5m={count_5m}条")
    logger.info(f"  聚合结果: 15m={agg_results.get('15m', 0)}条, "
                f"30m={agg_results.get('30m', 0)}条, 1h={agg_results.get('1h', 0)}条")

    # 计算平均速度
    if count_1d > 0:
        speed_1d = count_1d / (time_1d_read + time_1d_save) * 1000
        logger.info(f"  1d 速度: {speed_1d:.0f} 条/秒")
    if count_5m > 0:
        total_5m_time = time_5m_read + time_5m_save
        speed_5m = count_5m / total_5m_time * 1000
        logger.info(f"  5m 速度: {speed_5m:.0f} 条/秒 (含读取+保存)")

    return {
        'symbol': symbol,
        'total_time_ms': total_time,
        '1d_count': count_1d,
        '5m_count': count_5m,
        'agg_results': agg_results
    }


def test_batch_transfer(symbols: list):
    """测试批量转存速度"""
    logger.info("")
    logger.info("=" * 60)
    logger.info(f"性能测试: 批量转存 {len(symbols)} 只股票")
    logger.info("=" * 60)

    hotdb = get_adapter('hotdb')
    if not hotdb or not hotdb.is_available():
        logger.error("HotDB 不可用")
        return

    localdb = get_adapter('localdb')
    if not localdb or not localdb.is_available():
        logger.error("LocalDB 不可用")
        return

    results = []
    start_batch = time.time()

    for i, symbol in enumerate(symbols, 1):
        logger.info("")
        logger.info(f"[{i}/{len(symbols)}] 处理 {symbol}")
        logger.info("-" * 40)

        start_symbol = time.time()

        # 使用 ensure_symbol_in_hotdb（生产方法）
        success = hotdb.ensure_symbol_in_hotdb(symbol)

        elapsed = (time.time() - start_symbol) * 1000
        status = "成功" if success else "失败"
        logger.info(f"  结果: {status}, 耗时: {elapsed:.2f}ms")

        results.append({
            'symbol': symbol,
            'success': success,
            'time_ms': elapsed
        })

    batch_time = (time.time() - start_batch) * 1000
    successful = sum(1 for r in results if r['success'])

    logger.info("")
    logger.info("[结果] 批量转存汇总")
    logger.info("-" * 40)
    logger.info(f"  总耗时: {batch_time:.2f}ms ({batch_time/1000:.2f}秒)")
    logger.info(f"  成功率: {successful}/{len(symbols)}")
    logger.info(f"  平均耗时: {batch_time/len(symbols):.2f}ms/只")

    return results


def test_aggregation_performance(symbol: str = "600000.SH"):
    """测试纯聚合性能（不含 IO）"""
    logger.info("")
    logger.info("=" * 60)
    logger.info(f"性能测试: 纯聚合性能 {symbol}")
    logger.info("=" * 60)

    hotdb = get_adapter('hotdb')
    if not hotdb or not hotdb.is_available():
        logger.error("HotDB 不可用")
        return

    # 先确保有 5m 数据
    result = hotdb.get_kline(symbols=[symbol], period='5m', count=5000)
    if symbol not in result or result[symbol].empty:
        logger.error(f"HotDB 中 {symbol} 没有 5m 数据")
        return

    df_5m = result[symbol]
    logger.info(f"测试数据: {len(df_5m)} 根 5分钟K线")

    # 测试各周期聚合性能
    agg_results = {}
    for target_period in ['15m', '30m', '1h']:
        # 多次测试取平均值
        times = []
        counts = []

        for _ in range(5):  # 测试5次
            start = time.time()
            result_agg = hotdb._aggregate_from_5m(symbol, target_period)
            elapsed = (time.time() - start) * 1000

            if result_agg is not None and not result_agg.empty:
                times.append(elapsed)
                counts.append(len(result_agg))

        if times:
            avg_time = sum(times) / len(times)
            avg_count = sum(counts) / len(counts)
            min_time = min(times)
            max_time = max(times)

            logger.info(f"  {target_period}: 平均 {avg_time:.2f}ms, "
                       f"最小 {min_time:.2f}ms, 最大 {max_time:.2f}ms, "
                       f"生成 {avg_count:.0f} 条")

            # 计算聚合速度
            if avg_count > 0:
                speed = len(df_5m) / avg_time * 1000  # 根/秒
                logger.info(f"    聚合速度: {speed:.0f} 根/秒")

            agg_results[target_period] = {
                'avg_time_ms': avg_time,
                'min_time_ms': min_time,
                'max_time_ms': max_time,
                'count': avg_count
            }

    return agg_results


def main():
    """主测试函数"""
    logger.info("")
    logger.info("=" * 60)
    logger.info("HotDB 性能测试套件")
    logger.info("=" * 60)

    # 测试 1: 单只股票完整转存
    logger.info("")
    logger.info("[测试 1/3] 单只股票完整转存")
    single_result = test_single_symbol_transfer("600000.SH")

    # 测试 2: 批量转存
    logger.info("")
    logger.info("[测试 2/3] 批量转存（3只股票）")
    batch_symbols = ["000001.SZ", "600519.SH", "601628.SH"]
    batch_result = test_batch_transfer(batch_symbols)

    # 测试 3: 纯聚合性能
    logger.info("")
    logger.info("[测试 3/3] 纯聚合性能")
    agg_result = test_aggregation_performance("600000.SH")

    # 最终汇总
    logger.info("")
    logger.info("=" * 60)
    logger.info("测试完成！最终汇总")
    logger.info("=" * 60)

    if single_result:
        logger.info(f"  单只股票转存: {single_result['total_time_ms']:.2f}ms")
    if batch_result:
        total_time = sum(r['time_ms'] for r in batch_result)
        logger.info(f"  批量转存总耗时: {total_time:.2f}ms")
    if agg_result:
        logger.info(f"  聚合性能: 15m={agg_result['15m']['avg_time_ms']:.2f}ms, "
                   f"30m={agg_result['30m']['avg_time_ms']:.2f}ms, "
                   f"1h={agg_result['1h']['avg_time_ms']:.2f}ms")


if __name__ == "__main__":
    main()

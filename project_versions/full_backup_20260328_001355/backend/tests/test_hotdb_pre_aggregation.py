# -*- coding: utf-8 -*-
"""
HotDB 预聚合功能测试

测试场景：
1. 保存 5m 数据后，自动聚合生成 15m/30m/1h
2. 请求 15m/30m/1h 时，直接返回预聚合数据（无需等待）
"""

import sys
from pathlib import Path
import pandas as pd
from datetime import datetime, timedelta

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from loguru import logger
from myquant.core.market.adapters import get_adapter


def create_test_5m_data(symbol: str, count: int = 100) -> pd.DataFrame:
    """创建测试用的 5m 数据"""
    now = datetime.now()
    data = []

    for i in range(count):
        dt = now - timedelta(minutes=5 * (count - i))
        data.append({
            'datetime': dt,
            'open': 10.0 + i * 0.01,
            'high': 10.1 + i * 0.01,
            'low': 9.9 + i * 0.01,
            'close': 10.05 + i * 0.01,
            'volume': 100000 + i * 100,
            'amount': 1000000 + i * 1000,
        })

    return pd.DataFrame(data)


def test_pre_aggregation():
    """测试预聚合功能"""
    logger.info("=" * 60)
    logger.info("HotDB 预聚合功能测试")
    logger.info("=" * 60)

    # 获取 HotDB 适配器
    hotdb = get_adapter('hotdb')
    if not hotdb or not hotdb.is_available():
        logger.error("HotDB 适配器不可用")
        return

    # 测试股票
    test_symbol = '600000.SH'

    # 1. 创建测试数据
    logger.info("")
    logger.info("[步骤1] 创建 5m 测试数据")
    df_5m = create_test_5m_data(test_symbol, count=99)  # 99 条能整除 3, 6, 12
    logger.info(f"创建了 {len(df_5m)} 条 5m 数据")
    logger.info(f"时间范围: {df_5m['datetime'].min()} 到 {df_5m['datetime'].max()}")

    # 2. 保存 5m 数据（应触发自动聚合）
    logger.info("")
    logger.info("[步骤2] 保存 5m 数据（应触发自动聚合）")
    hotdb.delete_kline(test_symbol, period='5m')  # 先删除旧数据
    hotdb.delete_kline(test_symbol, period='15m')
    hotdb.delete_kline(test_symbol, period='30m')
    hotdb.delete_kline(test_symbol, period='1h')

    success = hotdb.save_kline(test_symbol, df_5m, '5m')
    if not success:
        logger.error("保存 5m 数据失败")
        return
    logger.info("保存成功")

    # 3. 验证 15m/30m/1h 数据是否自动生成
    logger.info("")
    logger.info("[步骤3] 验证预聚合数据是否生成")

    for period in ['15m', '30m', '1h']:
        result = hotdb.get_kline(symbols=[test_symbol], period=period, count=100)
        if test_symbol in result and not result[test_symbol].empty:
            df = result[test_symbol]
            logger.info(f"  {period}: {len(df)} 条 (✅ 已生成)")
        else:
            logger.warning(f"  {period}: 无数据 (❌ 未生成)")

    # 4. 测试读取速度（应瞬间返回）
    logger.info("")
    logger.info("[步骤4] 测试读取速度（预聚合数据应瞬间返回）")

    import time
    for period in ['5m', '15m', '30m', '1h']:
        start = time.time()
        result = hotdb.get_kline(symbols=[test_symbol], period=period, count=100)
        elapsed = (time.time() - start) * 1000

        if test_symbol in result and not result[test_symbol].empty:
            count = len(result[test_symbol])
            logger.info(f"  {period}: {count} 条 (耗时: {elapsed:.2f}ms)")
        else:
            logger.warning(f"  {period}: 无数据")

    # 5. 验证聚合正确性
    logger.info("")
    logger.info("[步骤5] 验证聚合正确性")

    result_5m = hotdb.get_kline(symbols=[test_symbol], period='5m', count=99)
    result_15m = hotdb.get_kline(symbols=[test_symbol], period='15m', count=100)

    if test_symbol in result_5m and test_symbol in result_15m:
        df_5m_check = result_5m[test_symbol]
        df_15m_check = result_15m[test_symbol]

        # 99 条 5m 应该聚合成 33 条 15m
        expected_15m = len(df_5m_check) // 3
        actual_15m = len(df_15m_check)

        logger.info(f"  5m: {len(df_5m_check)} 条")
        logger.info(f"  15m 预期: {expected_15m} 条, 实际: {actual_15m} 条")

        if actual_15m == expected_15m:
            logger.info("  ✅ 聚合数量正确")
        else:
            logger.warning("  ❌ 聚合数量不匹配")

        # 验证第一根 K 线
        if not df_15m_check.empty:
            first_15m = df_15m_check.iloc[0]
            logger.info(f"  15m 第一根: {first_15m['datetime']}, close={first_15m['close']}")

    logger.info("")
    logger.info("=" * 60)
    logger.info("测试完成")
    logger.info("=" * 60)


if __name__ == "__main__":
    test_pre_aggregation()

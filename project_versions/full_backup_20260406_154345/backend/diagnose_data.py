# -*- coding: utf-8 -*-
"""
诊断脚本：检查日K线重复和60分钟成交量问题
"""

import sys
from pathlib import Path

# 确保 src 在路径中
_current_file = Path(__file__).resolve()
src_dir = _current_file / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from loguru import logger
import pandas as pd


def setup_logging():
    logger.remove()
    logger.add(sys.stdout, format="{time:HH:mm:ss} | {level} | {message}", level="INFO")


def diagnose_daily_duplicate(symbol="000001.SZ"):
    """诊断日K线重复问题"""
    logger.info("=" * 60)
    logger.info(f"诊断日K线重复问题 - {symbol}")
    logger.info("=" * 60)

    from myquant.core.market.adapters import get_adapter
    hotdb = get_adapter('hotdb')

    if not hotdb or not hotdb.is_available():
        logger.error("HotDB 不可用")
        return

    # 获取日K数据
    df_dict = hotdb.get_kline(symbols=[symbol], period='1d', count=100)
    df = df_dict.get(symbol)

    if df is None or df.empty:
        logger.warning("无日K数据")
        return

    logger.info(f"数据条数: {len(df)}")
    logger.info(f"时间范围: {df['datetime'].min()} ~ {df['datetime'].max()}")

    # 检查重复日期
    date_counts = df['datetime'].value_counts()
    duplicates = date_counts[date_counts > 1]

    if len(duplicates) > 0:
        logger.error(f"发现 {len(duplicates)} 个重复日期:")
        for dt, count in duplicates.head(10).items():
            logger.error(f"  {dt}: {count} 条")
            # 显示这些重复行的详细信息
            dup_rows = df[df['datetime'] == dt]
            logger.info(f"  详细数据:")
            for idx, row in dup_rows.iterrows():
                logger.info(f"    open={row['open']}, close={row['close']}, volume={row['volume']}, source={row.get('data_source', 'N/A')}")
    else:
        logger.info("✅ 未发现重复日期")

    # 检查日期格式
    logger.info("\n日期格式检查:")
    sample_dates = df['datetime'].head(5)
    for dt in sample_dates:
        logger.info(f"  {dt} (类型: {type(dt)})")


def diagnose_60m_volume(symbol="000001.SZ"):
    """诊断60分钟成交量问题"""
    logger.info("\n" + "=" * 60)
    logger.info(f"诊断60分钟成交量问题 - {symbol}")
    logger.info("=" * 60)

    from myquant.core.market.adapters import get_adapter
    hotdb = get_adapter('hotdb')

    if not hotdb or not hotdb.is_available():
        logger.error("HotDB 不可用")
        return

    # 获取60分钟数据
    df_dict = hotdb.get_kline(symbols=[symbol], period='1h', count=100)
    df = df_dict.get(symbol)

    if df is None or df.empty:
        logger.warning("无60分钟数据")
        return

    logger.info(f"数据条数: {len(df)}")
    logger.info(f"时间范围: {df['datetime'].min()} ~ {df['datetime'].max()}")

    # 检查成交量
    logger.info("\n成交量统计:")
    logger.info(f"  平均: {df['volume'].mean():.0f}")
    logger.info(f"  最大: {df['volume'].max():.0f}")
    logger.info(f"  最小: {df['volume'].min():.0f}")

    # 检查是否有异常小的值（可能被重复÷100）
    small_volume = df[df['volume'] < 100]
    if len(small_volume) > 0:
        logger.warning(f"发现 {len(small_volume)} 条异常小成交量 (<100)")
        logger.info("样本:")
        for idx, row in small_volume.head(5).iterrows():
            logger.info(f"  {row['datetime']}: volume={row['volume']}, source={row.get('data_source', 'N/A')}")

    # 对比同一日期的日K成交量
    logger.info("\n对比日K成交量:")
    df_daily_dict = hotdb.get_kline(symbols=[symbol], period='1d', count=30)
    df_daily = df_daily_dict.get(symbol)

    if df_daily is not None and not df_daily.empty:
        # 取最近一天
        latest_date = df['datetime'].max().date()
        day_60m = df[df['datetime'].dt.date == latest_date]
        day_daily = df_daily[df_daily['datetime'].dt.date == latest_date]

        if len(day_60m) > 0 and len(day_daily) > 0:
            vol_60m_sum = day_60m['volume'].sum()
            vol_daily = day_daily['volume'].iloc[0]
            ratio = vol_daily / vol_60m_sum if vol_60m_sum > 0 else 0

            logger.info(f"  日期: {latest_date}")
            logger.info(f"  60m 成交量总和: {vol_60m_sum:.0f}")
            logger.info(f"  日K 成交量: {vol_daily:.0f}")
            logger.info(f"  比值 (日K/60m): {ratio:.2f}")

            if ratio > 50:  # 如果比值很大，说明60m数据可能被缩小了
                logger.error("  ⚠️ 60m 成交量可能比实际值小100倍！")


def test_xtquant_60m_raw(symbol="000001.SZ"):
    """测试 XtQuant 原始60m数据"""
    logger.info("\n" + "=" * 60)
    logger.info(f"测试 XtQuant 原始60m数据 - {symbol}")
    logger.info("=" * 60)

    from myquant.core.market.adapters import get_adapter
    xtquant = get_adapter('xtquant')

    if not xtquant or not xtquant.is_available():
        logger.error("XtQuant 不可用")
        return

    try:
        # 获取原始60m数据
        df_dict = xtquant.get_kline(symbols=[symbol], period='1h', count=10)
        df = df_dict.get(symbol)

        if df is None or df.empty:
            logger.warning("无数据")
            return

        logger.info(f"获取到 {len(df)} 条数据")
        logger.info("\n原始数据样本:")
        for idx, row in df.head(5).iterrows():
            logger.info(f"  {row['datetime']}: volume={row['volume']:.0f}")

        logger.info(f"\n成交量统计:")
        logger.info(f"  平均: {df['volume'].mean():.0f}")
        logger.info(f"  最大: {df['volume'].max():.0f}")

        # 判断 volume 单位
        avg_vol = df['volume'].mean()
        if avg_vol > 10000:
            logger.info(f"\n平均成交量 {avg_vol:.0f} > 10000，可能是股单位")
        elif avg_vol > 100:
            logger.info(f"\n平均成交量 {avg_vol:.0f} 在100-10000之间，可能是手单位")
        else:
            logger.info(f"\n平均成交量 {avg_vol:.0f} < 100，可能被缩小了")

    except Exception as e:
        logger.error(f"测试失败: {e}")


if __name__ == "__main__":
    setup_logging()

    # 诊断问题
    diagnose_daily_duplicate("000066.SZ")
    diagnose_60m_volume("000066.SZ")
    test_xtquant_60m_raw("000066.SZ")

    logger.info("\n" + "=" * 60)
    logger.info("诊断完成")
    logger.info("=" * 60)

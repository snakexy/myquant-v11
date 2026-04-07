# -*- coding: utf-8 -*-
"""
追踪 60m 数据 volume 转换问题的根源
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
    logger.add(sys.stdout, format="{time:HH:mm:ss} | {level} | {message}", level="DEBUG")


def trace_xtquant_1h(symbol="000066.SZ"):
    """追踪 XtQuant 1h 数据的 volume"""
    logger.info("=" * 70)
    logger.info(f"追踪 XtQuant 1h 数据 - {symbol}")
    logger.info("=" * 70)

    from myquant.core.market.adapters import get_adapter
    xtquant = get_adapter('xtquant')

    if not xtquant or not xtquant.is_available():
        logger.error("XtQuant 不可用")
        return

    # 1. 获取原始 1h 数据
    logger.info("\n【1】直接获取 XtQuant 1h 数据...")
    df_dict = xtquant.get_kline(symbols=[symbol], period='1h', count=10)
    df = df_dict.get(symbol)

    if df is None or df.empty:
        logger.warning("无数据")
        return

    logger.info(f"获取到 {len(df)} 条数据")
    logger.info(f"Volume 统计: 平均={df['volume'].mean():.0f}, 最大={df['volume'].max():.0f}, 最小={df['volume'].min():.0f}")
    logger.info("\n前5条数据:")
    for idx, row in df.head(5).iterrows():
        logger.info(f"  {row['datetime']}: open={row['open']:.2f}, close={row['close']:.2f}, volume={row['volume']:.0f}")

    # 2. 获取原始 60m 数据（不经过标准化）
    logger.info("\n【2】获取 XtQuant 原始 60m 数据（不标准化）...")
    import xtdata
    xt_symbol = symbol.replace('.SH', '.sh').replace('.SZ', '.sz')
    raw_data = xtdata.get_market_data_ex(
        field_list=['open', 'high', 'low', 'close', 'volume'],
        stock_list=[xt_symbol],
        period='60m',
        count=10
    )

    if raw_data and xt_symbol in raw_data:
        raw_df = raw_data[xt_symbol]
        if not raw_df.empty:
            logger.info(f"原始数据 volume 统计: 平均={raw_df['volume'].mean():.0f}, 最大={raw_df['volume'].max():.0f}")
            logger.info("\n前5条原始数据:")
            for idx, row in raw_df.head(5).iterrows():
                logger.info(f"  {idx}: volume={row['volume']:.0f}")

    # 3. 对比 5m 聚合 vs 直接 1h
    logger.info("\n【3】获取 5m 数据并聚合到 1h...")
    df_5m_dict = xtquant.get_kline(symbols=[symbol], period='5m', count=48)  # 48根5m = 4根1h
    df_5m = df_5m_dict.get(symbol)

    if df_5m is not None and not df_5m.empty:
        logger.info(f"5m 数据: {len(df_5m)} 条")
        logger.info(f"5m volume 统计: 平均={df_5m['volume'].mean():.0f}, 总和={df_5m['volume'].sum():.0f}")

        # 手动聚合到 1h
        df_5m['datetime'] = pd.to_datetime(df_5m['datetime'])
        df_5m['hour_group'] = df_5m['datetime'].dt.floor('H')
        agg_1h = df_5m.groupby('hour_group').agg({
            'open': 'first',
            'high': 'max',
            'low': 'min',
            'close': 'last',
            'volume': 'sum'
        }).reset_index()

        logger.info(f"\n从 5m 聚合的 1h 数据:")
        for idx, row in agg_1h.iterrows():
            logger.info(f"  {row['hour_group']}: volume={row['volume']:.0f}")

    # 4. 检查 HotDB 中的 1h 数据
    logger.info("\n【4】检查 HotDB 中的 1h 数据...")
    hotdb = get_adapter('hotdb')
    if hotdb and hotdb.is_available():
        df_hotdb_dict = hotdb.get_kline(symbols=[symbol], period='1h', count=10)
        df_hotdb = df_hotdb_dict.get(symbol)

        if df_hotdb is not None and not df_hotdb.empty:
            logger.info(f"HotDB 1h 数据: {len(df_hotdb)} 条")
            logger.info(f"HotDB volume 统计: 平均={df_hotdb['volume'].mean():.0f}, 最大={df_hotdb['volume'].max():.0f}")
            logger.info("\n前5条 HotDB 数据:")
            for idx, row in df_hotdb.head(5).iterrows():
                logger.info(f"  {row['datetime']}: volume={row['volume']:.0f}")
        else:
            logger.warning("HotDB 中无 1h 数据")


def trace_duplicate_issue(symbol="000066.SZ"):
    """追踪日K线重复问题"""
    logger.info("\n" + "=" * 70)
    logger.info(f"追踪日K线重复问题 - {symbol}")
    logger.info("=" * 70)

    from myquant.core.market.adapters import get_adapter
    hotdb = get_adapter('hotdb')

    if not hotdb or not hotdb.is_available():
        logger.error("HotDB 不可用")
        return

    # 1. 检查 HotDB 日K数据
    logger.info("\n【1】检查 HotDB 日K数据...")
    df_dict = hotdb.get_kline(symbols=[symbol], period='1d', count=20)
    df = df_dict.get(symbol)

    if df is None or df.empty:
        logger.warning("无数据")
        return

    logger.info(f"数据条数: {len(df)}")
    logger.info(f"时间范围: {df['datetime'].min()} ~ {df['datetime'].max()}")

    # 检查日期格式
    logger.info("\n日期格式详情:")
    for idx, row in df.head(10).iterrows():
        dt = row['datetime']
        logger.info(f"  {dt} (类型: {type(dt).__name__}, hour={dt.hour if hasattr(dt, 'hour') else 'N/A'})")

    # 检查重复
    date_counts = df['datetime'].value_counts()
    duplicates = date_counts[date_counts > 1]
    if len(duplicates) > 0:
        logger.error(f"\n发现 {len(duplicates)} 个重复日期:")
        for dt, count in duplicates.items():
            logger.error(f"  {dt}: {count} 条")
    else:
        logger.info("\n✅ 未发现重复日期")


if __name__ == "__main__":
    setup_logging()

    # 追踪 volume 问题
    trace_xtquant_1h("000066.SZ")

    # 追踪重复问题
    trace_duplicate_issue("000066.SZ")

    logger.info("\n" + "=" * 70)
    logger.info("追踪完成")
    logger.info("=" * 70)

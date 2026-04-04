#!/usr/bin/env python3
"""填充 000858.SZ 5m 数据缺口（March 16-29, 2026）使用 PyTdx"""
import sys
sys.path.insert(0, 'E:/MyQuant_v11/backend/src')

from myquant.core.market.adapters import get_adapter
from myquant.core.market.services.hotdb_service import get_hotdb_service
from loguru import logger
import pandas as pd

def fill_000858_gaps_with_pytdx():
    """使用 PyTdx 填充 000858.SZ 的 5m 数据缺口"""
    symbol = '000858.SZ'
    period = '5m'

    logger.info(f"=== 使用 PyTdx 填充 {symbol} {period} 数据缺口 ===")

    # 1. 使用 PyTdx 获取历史数据
    try:
        logger.info("使用 PyTdx 获取 March 16-29, 2026 数据...")
        adapter = get_adapter('pytdx')
        if not adapter:
            logger.error("无法获取 PyTdx 适配器")
            return False

        start_date = '20260316'
        end_date = '20260329'

        df_dict = adapter.get_kline(
            symbols=[symbol],
            period=period,
            start_date=start_date,
            end_date=end_date,
            count=5000
        )

        if symbol not in df_dict or df_dict[symbol].empty:
            logger.error(f"PyTdx 未返回 {symbol} 数据")
            return False

        df = df_dict[symbol]
        logger.info(f"从 PyTdx 获取 {len(df)} 条数据")
        logger.info(f"日期范围: {df['datetime'].min()} ~ {df['datetime'].max()}")

    except Exception as e:
        logger.error(f"PyTdx 获取数据失败: {e}")
        return False

    # 2. 保存到 HotDB
    try:
        logger.info("保存到 HotDB...")
        service = get_hotdb_service()
        hotdb = service._get_hotdb_adapter()

        if hotdb:
            hotdb.save_kline(symbol, df, period)
            logger.info(f"已保存 {len(df)} 条数据到 HotDB")

            # 更新数据指纹
            service._update_fingerprint(symbol, period, df)
            logger.info("已更新数据指纹")

        else:
            logger.error("无法获取 HotDB 适配器")
            return False

    except Exception as e:
        logger.error(f"保存到 HotDB 失败: {e}")
        return False

    # 3. 验证结果
    try:
        logger.info("验证填充结果...")
        if hotdb:
            df_check = hotdb.get_kline(symbols=[symbol], period=period, count=5000)
            if symbol in df_check and not df_check[symbol].empty:
                df_verified = df_check[symbol]
                logger.info(f"HotDB 现有 {len(df_verified)} 条数据")
                logger.info(f"日期范围: {df_verified['datetime'].min()} ~ {df_verified['datetime'].max()}")

                # 检查 March 16-29 是否存在
                df_verified['date'] = df_verified['datetime'].dt.date
                march_dates = df_verified[df_verified['datetime'].dt.month == 3]['date'].unique()
                logger.info(f"March 日期数: {len(march_dates)}")
                logger.info(f"March 日期: {sorted(march_dates)}")

                return True
    except Exception as e:
        logger.error(f"验证失败: {e}")
        return False

    return True

if __name__ == '__main__':
    success = fill_000858_gaps_with_pytdx()
    if success:
        logger.info("=== 数据填充成功 ===")
        sys.exit(0)
    else:
        logger.error("=== 数据填充失败 ===")
        sys.exit(1)

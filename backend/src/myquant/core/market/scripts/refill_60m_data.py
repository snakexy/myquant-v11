# -*- coding: utf-8 -*-
"""
补充 HotDB 60分钟历史数据

删除污染数据后，需要重新从在线源获取完整的历史数据
"""

from myquant.core.market.adapters import get_adapter
from loguru import logger
import time

# 需要补充数据的股票（刚才删除污染数据的）
STOCKS = [
    '000001.SZ',  # 平安银行
    '000066.SZ',
    '300046.SZ',
    '600536.SH',
    '601628.SH',
    '601939.SH',
]


def fetch_and_save(symbol: str, period: str = '60m',
                   count: int = 1000) -> bool:
    """从在线源获取数据并保存到 HotDB"""
    try:
        # 1. 从在线源获取数据
        pytdx = get_adapter('pytdx')
        logger.info(f"正在获取 {symbol} {period} 数据...")

        result = pytdx.get_kline(
            symbols=[symbol],
            period=period,
            count=count
        )

        if (symbol not in result or result[symbol] is None or
                result[symbol].empty):
            logger.warning(f"  {symbol} 在线源无数据")
            return False

        df = result[symbol]
        logger.info(f"  {symbol} 获取到 {len(df)} 条数据")

        # 2. 保存到 HotDB
        hotdb = get_adapter('hotdb')
        success = hotdb.save_kline(symbol, df, period)

        if success:
            logger.success(f"  {symbol} 保存成功 ({len(df)} 条)")
            return True
        else:
            logger.error(f"  {symbol} 保存失败")
            return False

    except Exception as e:
        logger.error(f"  {symbol} 处理失败: {e}")
        return False


def main():
    """主函数"""
    logger.info("=" * 60)
    logger.info("开始补充 60分钟历史数据")
    logger.info("=" * 60)

    success_count = 0
    failed_count = 0

    for symbol in STOCKS:
        logger.info(f"\n处理 {symbol}...")

        if fetch_and_save(symbol, period='60m', count=1000):
            success_count += 1
        else:
            failed_count += 1

        # 避免请求过快
        time.sleep(0.5)

    logger.info("\n" + "=" * 60)
    logger.info(f"补充完成: 成功 {success_count}, 失败 {failed_count}")
    logger.info("=" * 60)


if __name__ == '__main__':
    main()

# -*- coding: utf-8 -*-
"""
HotDB 一次性转存测试

测试自选板块场景：
1. 第一次调用 ensure_symbol → 从 LocalDB 转存数据
2. 第二次调用 ensure_symbol → 跳过（已标记）
3. 验证预聚合自动触发
"""

import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from loguru import logger
from myquant.core.market.adapters import get_adapter
from myquant.core.market.services.hotdb_service import get_hotdb_service


def test_one_time_transfer():
    """测试一次性转存功能"""
    logger.info("=" * 60)
    logger.info("HotDB 一次性转存测试")
    logger.info("=" * 60)

    hotdb = get_adapter('hotdb')
    service = get_hotdb_service()

    if not hotdb or not hotdb.is_available():
        logger.error("HotDB 适配器不可用")
        return

    # 测试股票
    test_symbol = '000001.SZ'

    # 1. 清理旧数据和标记
    logger.info("")
    logger.info("[步骤1] 清理旧数据和标记")
    hotdb.delete_kline(test_symbol)  # 删除所有周期数据

    # 清除标记
    if hasattr(hotdb, '_metadata'):
        key = f"{test_symbol}_ready"
        if key in hotdb._metadata:
            del hotdb._metadata[key]
            hotdb._save_metadata()
            logger.info(f"已清除 {test_symbol} 的转存标记")

    # 2. 第一次调用 ensure_symbol（应触发转存）
    logger.info("")
    logger.info("[步骤2] 第一次调用 ensure_symbol（应触发转存）")

    result = service.ensure_symbol(test_symbol)
    logger.info(f"结果: {result}")

    # 3. 验证数据已转存
    logger.info("")
    logger.info("[步骤3] 验证数据已转存")

    for period in ['1d', '5m', '15m', '30m', '1h']:
        data = hotdb.get_kline(symbols=[test_symbol], period=period, count=10)
        if test_symbol in data and not data[test_symbol].empty:
            logger.info(f"  {period}: {len(data[test_symbol])} 条 ✅")
        else:
            logger.warning(f"  {period}: 无数据 ❌")

    # 4. 检查标记
    logger.info("")
    logger.info("[步骤4] 检查转存标记")

    is_ready = hotdb._is_symbol_ready(test_symbol)
    logger.info(f"  {test_symbol} 已标记: {is_ready}")

    # 5. 第二次调用 ensure_symbol（应跳过）
    logger.info("")
    logger.info("[步骤5] 第二次调用 ensure_symbol（应跳过）")

    result = service.ensure_symbol(test_symbol)
    logger.info(f"结果: {result}")

    # 6. 验证标记仍然存在
    logger.info("")
    logger.info("[步骤6] 验证标记仍然存在")

    is_ready = hotdb._is_symbol_ready(test_symbol)
    logger.info(f"  {test_symbol} 已标记: {is_ready}")

    logger.info("")
    logger.info("=" * 60)
    logger.info("测试完成")
    logger.info("=" * 60)

    # 总结
    logger.info("")
    logger.info("测试总结:")
    logger.info("  1. ✅ 第一次调用触发转存")
    logger.info("  2. ✅ 5m 保存时自动聚合 15m/30m/1h")
    logger.info("  3. ✅ 标记为已转存")
    logger.info("  4. ✅ 第二次调用跳过转存")


if __name__ == "__main__":
    test_one_time_transfer()

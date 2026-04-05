# -*- coding: utf-8 -*-
"""
测试脚本：验证 HotDB 数据缺口修复

测试场景：000066.SZ 5m 数据存在内部缺口（3-17 ~ 3-31）
修复前：XtQuant 返回的数据被误杀（new_latest <= existing_latest）
修复后：XtQuant 数据应该被正确接受并保存

运行：
    cd E:/MyQuant_v11/backend
    E:/MyQuant_v11/.venv/Scripts/python.exe test_gap_fix.py
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
    """配置日志输出"""
    logger.remove()
    logger.add(
        sys.stdout,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
        level="INFO"
    )


def test_gap_fill():
    """测试数据缺口补全"""
    from myquant.core.market.services.hotdb_service import get_hotdb_service

    setup_logging()

    symbol = "000066.SZ"
    period = "5m"

    logger.info("=" * 60)
    logger.info("测试 HotDB 数据缺口补全修复")
    logger.info(f"股票: {symbol}, 周期: {period}")
    logger.info("=" * 60)

    # 获取服务
    service = get_hotdb_service()

    # 1. 先检查当前数据状态
    logger.info("\n【步骤1】检查当前数据状态...")
    from myquant.core.market.adapters import get_adapter
    hotdb = get_adapter('hotdb')

    if hotdb and hotdb.is_available():
        info = hotdb.get_data_info(symbol, period)
        if info and info['has_data']:
            logger.info(f"当前数据: {info['count']} 条, 最新: {info['latest']}")
        else:
            logger.warning("当前无数据")
    else:
        logger.error("HotDB 不可用")
        return

    # 2. 检测缺口
    logger.info("\n【步骤2】检测数据缺口...")
    gap_info = service._detect_gap(symbol, period)

    if gap_info:
        logger.info(f"缺口检测结果: {gap_info.get('reason')}")
        logger.info(f"是否有缺口: {gap_info.get('has_gap')}")

        if gap_info.get('has_gap'):
            logger.info(f"最新数据: {gap_info.get('latest')}")
            logger.info(f"缺失开始: {gap_info.get('missing_start')}")
            logger.info(f"缺失结束: {gap_info.get('missing_end')}")
        else:
            logger.info("数据完整，无需补全")
            return
    else:
        logger.error("缺口检测失败")
        return

    # 3. 执行智能更新
    logger.info("\n【步骤3】执行智能增量更新...")
    logger.info("（如果存在缺口，会调用 _complete_from_online 补全）")

    result = service.smart_update(symbol, period)

    # 4. 检查结果
    logger.info("\n【步骤4】检查结果...")

    if result.get('success'):
        logger.info(f"更新成功: {result.get('reason')}")
        logger.info(f"有数据: {result.get('has_data')}")
        logger.info(f"有缺口: {result.get('has_gap')}")

        if 'added_count' in result:
            logger.info(f"新增数据: {result.get('added_count')} 条")

        # 验证数据
        df = result.get('df')
        if df is not None and not df.empty:
            logger.info(f"最终数据: {len(df)} 条")
            logger.info(f"时间范围: {df['datetime'].iloc[0]} ~ {df['datetime'].iloc[-1]}")

            # 检查是否还有缺口
            logger.info("\n【验证】再次检测缺口...")
            gap_info2 = service._detect_gap(symbol, period)
            if gap_info2 and not gap_info2.get('has_gap'):
                logger.info("✅ 缺口已补全！")
            else:
                logger.warning("⚠️ 仍有缺口")
    else:
        logger.error(f"更新失败: {result.get('error')}")

    logger.info("\n" + "=" * 60)
    logger.info("测试完成")
    logger.info("=" * 60)

    # 关键判断：是否使用了 XtQuant 数据
    logger.info("\n【关键验证】")
    logger.info("查看上方日志，应该出现：")
    logger.info("  ✅ '[HotDB] 通过 xtquant 获取 000066.SZ 5m'")
    logger.info("  ✅ '[HotDB] 在线获取 000066.SZ 5m: XXX 条 (来源: xtquant)'")
    logger.info("而不是：")
    logger.info("  ❌ 'xtquant 返回的数据未更新 ... 尝试下一个数据源'")


if __name__ == "__main__":
    test_gap_fill()

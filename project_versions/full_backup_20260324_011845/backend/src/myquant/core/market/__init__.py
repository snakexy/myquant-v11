# -*- coding: utf-8 -*-
"""
行情核心 - V5 场景化数据服务

数据层级：
    L0 - 订阅缓存 (<1ms)
    L1 - 实时快照 (1-17ms)
    L2 - 历史摘要 (7-17ms)
    L3 - 完整K线 (5-18ms)
    L4 - 财务数据 (100-300ms)
    L5 - 板块/特色数据 (10-500ms)

服务导出：
    from myquant.core.market import get_seamless_kline_service
    from myquant.core.market.adapters import get_adapter
"""

# 适配器
from .adapters import get_adapter

# 服务
from .services import (
    get_seamless_kline_service,
    get_intraday_kline_service,
    get_realtime_market_service,
)

# 路由
from .routing import DataLevel, get_source_selector

# 工具
from .utils import TradingTimeChecker, AdjustmentCalculator

__all__ = [
    # 适配器
    "get_adapter",
    # 服务
    "get_seamless_kline_service",
    "get_intraday_kline_service",
    "get_realtime_market_service",
    # 路由
    "DataLevel",
    "get_source_selector",
    # 工具
    "TradingTimeChecker",
    "AdjustmentCalculator",
]

"""
K线服务统一入口

聚合 seamless、intraday、realtime 三种K线服务
"""

from .seamless_service import SeamlessKlineService, get_seamless_kline_service
from .intraday_service import IntradayKlineService, get_intraday_kline_service
from .kline_service import KlineService, get_kline_service

__all__ = [
    'SeamlessKlineService',
    'get_seamless_kline_service',
    'IntradayKlineService',
    'get_intraday_kline_service',
    'KlineService',
    'get_kline_service',
]

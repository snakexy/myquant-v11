"""API 网关层

分层结构：
    domain/     - 业务领域 API（研究/回测/验证/生产）
    dataget/    - 数据获取 API（行情/监控/增量更新/转换）
"""

from .dataget.quotes import router as quotes_router
from .dataget.market import router as market_router
from .dataget.monitoring import router as monitoring_router
from .dataget.incremental import router as incremental_router
from .dataget.conversion import router as conversion_router

__all__ = [
    "quotes_router",
    "market_router",
    "monitoring_router",
    "incremental_router",
    "conversion_router",
]

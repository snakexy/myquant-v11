"""API 网关层

分层结构：
    domain/     - 业务领域 API（研究/回测/验证/生产）
    data/       - 数据服务 API（行情/监控/增量更新）
"""

from .data.quotes import router as quotes_router
from .data.monitoring import router as monitoring_router
from .data.incremental import router as incremental_router
from .data.conversion import router as conversion_router

__all__ = [
    "quotes_router",
    "monitoring_router",
    "incremental_router",
    "conversion_router",
]

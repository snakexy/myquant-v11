"""
V5 场景化服务 API 路由入口

提供四大核心服务的 API 路由：
1. K线服务 - 实时K线、无缝K线、历史K线
2. 监控服务 - 热点板块、热点股票、异常检测
3. 增量更新服务 - 数据更新、缺失检测、快照获取
4. 数据转换服务 - 批量转换TDX数据到Qlib
5. 实时行情服务 - 实时行情、热点扫描、订阅推送
6. 热数据库服务 - 预热、清理、状态查询
"""

from .quotes import router as quotes_router
from .monitoring import router as monitoring_router
from .incremental import router as incremental_router
from .conversion import router as conversion_router
from .market import router as market_router
from .hotdata import router as hotdata_router


__all__ = [
    'quotes_router',
    'monitoring_router',
    'incremental_router',
    'conversion_router',
    'market_router',
    'hotdata_router',
]

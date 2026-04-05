"""
MyQuant v11 - 量化投研平台核心库

架构分层：
    api/        - API 网关层（路由/鉴权/序列化）
    core/       - 核心业务层（行情/研究/回测/生产）
    infrastructure/ - 基础设施层（数据库/缓存/外部SDK）
    interfaces/ - 接口适配层（WebSocket/CLI）

使用示例：
    from myquant.core.market.adapters import V5PyTdxAdapter
    from myquant.core.market.services import get_seamless_kline_service
"""

__version__ = "11.0.0"

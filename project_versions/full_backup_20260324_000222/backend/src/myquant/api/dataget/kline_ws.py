"""
WebSocket K 线推送路由
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from loguru import logger

from myquant.core.market.services.kline_service import get_kline_service


router = APIRouter(tags=["WebSocket K线"])


@router.websocket("/kline/{symbol}")
async def kline_ws(websocket: WebSocket, symbol: str):
    """
    实时分钟 K 线推送

    连接后立即收到历史数据：
      {"type": "history", "symbol": "000001.SZ", "bars": [...]}

    之后持续推送：
      {"type": "bar_update", "symbol": "000001.SZ", "bar": {...}}
      {"type": "bar_close",  "symbol": "000001.SZ", "bar": {...}}

    示例：ws://localhost:8000/ws/kline/000001.SZ
    """
    await websocket.accept()
    service = get_kline_service()
    await service.connect(websocket, symbol)

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        logger.info("WS 断开: {}", symbol)
    finally:
        await service.disconnect(websocket, symbol)

"""
WebSocket K 线推送路由
"""

import asyncio
import time
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from loguru import logger
from starlette.websockets import WebSocketState

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

    心跳机制：
      - 服务端每30秒发送 ping
      - 客户端收到后应回复 pong
      - 90秒未收到 pong 则断开连接

    示例：ws://localhost:8000/ws/kline/000001.SZ
    """
    await websocket.accept()
    service = get_kline_service()
    await service.connect(websocket, symbol)

    # 心跳状态
    last_pong = time.time()
    heartbeat_interval = 30.0  # 30秒发送一次心跳
    heartbeat_timeout = 90.0   # 90秒超时

    async def receive_client_messages():
        """接收客户端消息（处理 ping/pong）"""
        nonlocal last_pong
        try:
            while True:
                try:
                    # 设置30秒超时接收消息
                    data = await asyncio.wait_for(
                        websocket.receive_text(),
                        timeout=heartbeat_interval
                    )

                    # 处理客户端心跳
                    if data == "ping":
                        await websocket.send_text("pong")
                        logger.debug("WS 心跳响应: {} pong", symbol)
                    elif data == "pong":
                        last_pong = time.time()
                        logger.debug("WS 收到心跳: {} pong", symbol)

                except asyncio.TimeoutError:
                    # 30秒内没有收到消息，检查心跳超时
                    if time.time() - last_pong > heartbeat_timeout:
                        logger.warning("WS 心跳超时: {}，断开连接", symbol)
                        break
        except WebSocketDisconnect:
            logger.info("WS 客户端断开: {}", symbol)
        except Exception as e:
            logger.error("WS 接收消息异常: {} - {}", symbol, e)

    async def send_server_heartbeat():
        """发送服务端心跳"""
        try:
            while True:
                await asyncio.sleep(heartbeat_interval)

                # 检查连接状态
                if websocket.client_state != WebSocketState.CONNECTED:
                    break

                # 发送心跳
                try:
                    await websocket.send_text("ping")
                    logger.debug("WS 发送心跳: {} ping", symbol)
                except Exception:
                    break

                # 检查客户端是否超时
                if time.time() - last_pong > heartbeat_timeout:
                    logger.warning("WS 心跳超时: {}，断开连接", symbol)
                    break
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error("WS 发送心跳异常: {} - {}", symbol, e)

    try:
        # 同时运行接收和心跳任务
        receive_task = asyncio.create_task(receive_client_messages())
        heartbeat_task = asyncio.create_task(send_server_heartbeat())

        # 等待任一任务完成（断开或超时）
        done, pending = await asyncio.wait(
            [receive_task, heartbeat_task],
            return_when=asyncio.FIRST_COMPLETED
        )

        # 取消剩余任务
        for task in pending:
            task.cancel()

    except Exception as e:
        logger.error("WS 连接异常: {} - {}", symbol, e)
    finally:
        # 确保断开连接
        try:
            await service.disconnect(websocket, symbol)
            if websocket.client_state == WebSocketState.CONNECTED:
                await websocket.close()
        except Exception:
            pass
        logger.info("WS 连接清理完成: {}", symbol)

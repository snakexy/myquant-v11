"""
WebSocket 批量更新进度推送

用于批量更新 LocalDB 时的实时进度显示
"""

import asyncio
import uuid
from datetime import datetime
from typing import Dict
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from loguru import logger
from starlette.websockets import WebSocketState


router = APIRouter(tags=["WebSocket 批量更新"])


class BatchUpdateManager:
    """批量更新任务管理器"""

    def __init__(self):
        # 存储活跃的 WebSocket 连接
        self._connections: Dict[str, WebSocket] = {}
        # 存储任务状态
        self._tasks: Dict[str, dict] = {}

    def register_connection(self, task_id: str, websocket: WebSocket):
        """注册 WebSocket 连接"""
        self._connections[task_id] = websocket
        logger.info(f"[批量更新] 任务 {task_id} WebSocket 已连接")

    def unregister_connection(self, task_id: str):
        """取消注册 WebSocket 连接"""
        self._connections.pop(task_id, None)
        logger.info(f"[批量更新] 任务 {task_id} WebSocket 已断开")

    async def send_progress(self, task_id: str, progress_data: dict):
        """发送进度更新"""
        if task_id in self._connections:
            ws = self._connections[task_id]
            if ws.client_state == WebSocketState.CONNECTED:
                try:
                    await ws.send_json(progress_data)
                    logger.debug(f"[批量更新] {task_id} 进度: {progress_data.get('completed', 0)}/{progress_data.get('total', 0)}")
                except Exception as e:
                    logger.warning(f"[批量更新] {task_id} 发送进度失败: {e}")
                    self.unregister_connection(task_id)

    def create_task(self, symbols: list, periods: list) -> str:
        """创建新任务"""
        task_id = str(uuid.uuid4())
        self._tasks[task_id] = {
            'task_id': task_id,
            'symbols': symbols,
            'periods': periods,
            'total': len(symbols) * len(periods),
            'completed': 0,
            'current_symbol': None,
            'current_period': None,
            'status': 'pending',
            'created_at': datetime.now().isoformat(),
            'results': {}
        }
        return task_id

    def update_task(self, task_id: str, **kwargs):
        """更新任务状态"""
        if task_id in self._tasks:
            self._tasks[task_id].update(kwargs)


# 全局管理器实例
_batch_manager = BatchUpdateManager()


@router.websocket("/batch-update/{task_id}")
async def batch_update_ws(websocket: WebSocket, task_id: str):
    """
    批量更新 LocalDB 的进度推送 WebSocket

    连接格式: ws://localhost:8000/ws/batch-update/{task_id}

    消息格式:
      {
        "type": "progress",
        "task_id": "xxx",
        "total": 200,
        "completed": 45,
        "current_symbol": "000001.SZ",
        "current_period": "1d",
        "status": "in_progress",
        "message": "正在更新..."
      }

    完成时:
      {
        "type": "complete",
        "task_id": "xxx",
        "total": 200,
        "completed": 200,
        "status": "complete",
        "results": {...}
      }
    """
    await websocket.accept()
    _batch_manager.register_connection(task_id, websocket)

    # 获取任务信息
    task = _batch_manager._tasks.get(task_id)
    if not task:
        await websocket.send_json({
            "type": "error",
            "message": f"任务 {task_id} 不存在"
        })
        await websocket.close()
        return

    # 发送初始状态
    await websocket.send_json({
        "type": "progress",
        "task_id": task_id,
        "total": task['total'],
        "completed": task['completed'],
        "current_symbol": task.get('current_symbol'),
        "current_period": task.get('current_period'),
        "status": task.get('status', 'pending'),
        "message": f"准备更新 {task['total']} 项数据..."
    })

    try:
        # 保持连接，等待任务完成
        while True:
            # 检查连接状态
            if websocket.client_state != WebSocketState.CONNECTED:
                break

            # 检查任务状态
            task = _batch_manager._tasks.get(task_id)
            if not task:
                break

            if task.get('status') == 'complete':
                await websocket.send_json({
                    "type": "complete",
                    "task_id": task_id,
                    "total": task['total'],
                    "completed": task['completed'],
                    "results": task.get('results', {}),
                    "message": "更新完成！"
                })
                break

            # 等待一小段时间再检查
            await asyncio.sleep(0.5)

    except WebSocketDisconnect:
        logger.info(f"[批量更新] 任务 {task_id} 客户端断开")
    except Exception as e:
        logger.error(f"[批量更新] 任务 {task_id} 异常: {e}")
    finally:
        _batch_manager.unregister_connection(task_id)
        try:
            if websocket.client_state == WebSocketState.CONNECTED:
                await websocket.close()
        except Exception:
            pass


async def execute_batch_update(
    task_id: str,
    symbols: list,
    periods: list,
    source: str = 'pytdx'  # 数据源
) -> dict:
    """
    执行批量更新任务（后台运行）

    Args:
        task_id: 任务ID
        symbols: 股票代码列表
        periods: 周期列表
        source: 数据源

    Returns:
        执行结果
    """
    task = _batch_manager._tasks.get(task_id)
    if not task:
        return {'success': False, 'error': '任务不存在'}

    # 调用 KlineService 下载到 HotDB（临时数据）
    from myquant.core.market.services.kline_service import get_kline_service

    kline_service = get_kline_service()

    # 更新任务状态
    _batch_manager.update_task(task_id, status='in_progress')

    try:
        # 发送初始进度
        await _batch_manager.send_progress(task_id, {
            "type": "progress",
            "task_id": task_id,
            "total": task['total'],
            "completed": 0,
            "status": "in_progress",
            "message": f"开始下载 {len(symbols)} 只股票到 HotDB..."
        })

        # 调用 KlineService 下载到 HotDB（临时数据）
        results = kline_service.download_to_hotdb(
            symbols=symbols,
            periods=periods,
            source=source
        )

        # 更新任务状态
        _batch_manager.update_task(
            task_id,
            status='complete',
            completed=task['total'],
            results=results
        )

        await _batch_manager.send_progress(task_id, {
            "type": "complete",
            "task_id": task_id,
            "total": task['total'],
            "completed": task['total'],
            "status": "complete",
            "results": results,
            "message": f"下载完成！成功 {results['success']} 项"
        })

        return {
            'success': True,
            'task_id': task_id,
            'total': task['total'],
            'completed': task['total'],
            'results': results
        }

    except Exception as e:
        logger.error(f"[批量更新] 任务 {task_id} 失败: {e}")
        _batch_manager.update_task(task_id, status='failed', error=str(e))

        await _batch_manager.send_progress(task_id, {
            "type": "error",
            "task_id": task_id,
            "message": f"更新失败: {str(e)}"
        })

        return {
            'success': False,
            'error': str(e),
            'task_id': task_id
        }


def get_batch_manager() -> BatchUpdateManager:
    """获取批量更新管理器实例"""
    return _batch_manager

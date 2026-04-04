# -*- coding: utf-8 -*-
"""
热数据库 API 路由

提供热数据库的预热、清理、状态查询等 API
"""

from fastapi import APIRouter, HTTPException, Query, Path
from fastapi.concurrency import run_in_threadpool
from typing import List, Optional
from pydantic import BaseModel, Field
from loguru import logger

from myquant.core.market.services.hotdb_service import get_hotdb_service


router = APIRouter(tags=["热数据库"])


# ─── 请求模型 ───────────────────────────────────────────────────────────────

class PreheatRequest(BaseModel):
    """预热请求"""
    symbols: List[str] = Field(..., description="股票代码列表", min_length=1, max_length=500)
    periods: Optional[List[str]] = Field(
        None,
        description="周期列表（如 ['1d', '5m', '15m']），默认为 ['1d', '5m', '15m', '1m']"
    )


class DeleteRequest(BaseModel):
    """删除请求"""
    symbol: str = Field(..., description="股票代码")
    period: Optional[str] = Field(None, description="周期（如 '1d', '1m'），None 表示删除所有周期")


# ─── 响应模型 ───────────────────────────────────────────────────────────────

class PreheatResponse(BaseModel):
    """预热响应"""
    success: bool
    total_symbols: int
    total_periods: int
    saved_count: int
    skipped_count: int
    failed_count: int
    details: Optional[List[dict]] = None


class DeleteResponse(BaseModel):
    """删除响应"""
    success: bool
    symbol: str
    period: Optional[str] = None
    error: Optional[str] = None


class StatusResponse(BaseModel):
    """状态响应"""
    success: bool
    total_symbols: Optional[int] = None
    period_stats: Optional[dict] = None
    symbols: Optional[List[str]] = None
    has_more: Optional[bool] = None
    error: Optional[str] = None


class SymbolsResponse(BaseModel):
    """股票列表响应"""
    success: bool
    symbols: Optional[List[str]] = None
    total: Optional[int] = None
    error: Optional[str] = None


class CheckResponse(BaseModel):
    """检查响应"""
    success: bool
    symbol: str
    exists: Optional[bool] = None
    error: Optional[str] = None


# ─── API 端点 ───────────────────────────────────────────────────────────────

@router.get("/debug", summary="调试信息")
async def debug_hotdb():
    """返回 HotDB 调试信息"""
    from myquant.core.market.adapters import AdapterFactory
    from myquant.core.market.services.hotdb_service import get_hotdb_service

    service = get_hotdb_service()
    hotdb = service._get_hotdb_adapter() if service else None

    return {
        "registered_adapters": AdapterFactory.list_adapters(),
        "service_exists": service is not None,
        "service_hotdb_attr": service._hotdb if service else None,
        "get_hotdb_adapter_result": str(hotdb),
        "get_hotdb_adapter_type": str(type(hotdb)) if hotdb else None,
    }


@router.post("/preheat", response_model=PreheatResponse, summary="预热热数据库")
async def preheat_hotdb(request: PreheatRequest):
    """预热：从 LocalDB 复制历史数据到 HotDB

    将指定的股票数据从 LocalDB 复制到 HotDB，加速后续访问。
    日线使用智能合并（追加新日期），分钟线使用覆盖模式。
    """
    try:
        service = get_hotdb_service()

        # 在线程池中执行同步操作
        result = await run_in_threadpool(
            service.preheat,
            symbols=request.symbols,
            periods=request.periods
        )

        if not result.get('success'):
            raise HTTPException(status_code=500, detail=result.get('error', '预热失败'))

        return PreheatResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[HotDB API] 预热失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/symbols/{symbol}", response_model=DeleteResponse, summary="删除股票数据")
async def delete_hotdb_symbol(
    symbol: str = Path(..., description="股票代码（如 600519.SH）"),
    period: Optional[str] = Query(None, description="周期（如 1d, 1m），None 表示删除所有周期")
):
    """删除指定股票的热数据库数据

    如果指定 period，只删除该周期的数据；否则删除所有周期的数据。
    """
    try:
        logger.info(f"[HotDB API] 收到删除请求: symbol={symbol}, period={period}")
        service = get_hotdb_service()
        logger.info(f"[HotDB API] 服务实例: {service}")
        logger.info(f"[HotDB API] 调用 _get_hotdb_adapter()...")
        hotdb = service._get_hotdb_adapter()
        logger.info(f"[HotDB API] _get_hotdb_adapter() 返回: {hotdb}, is None: {hotdb is None}")

        result = await run_in_threadpool(
            service.delete_symbol,
            symbol=symbol,
            period=period
        )

        if not result.get('success'):
            raise HTTPException(status_code=500, detail=result.get('error', '删除失败'))

        return DeleteResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[HotDB API] 删除 {symbol} 失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status", response_model=StatusResponse, summary="获取热数据库状态")
async def get_hotdb_status():
    """获取热数据库状态

    返回热数据库中的股票数量、各周期统计等信息。
    """
    try:
        service = get_hotdb_service()

        result = await run_in_threadpool(service.get_status)

        if not result.get('success'):
            raise HTTPException(status_code=500, detail=result.get('error', '获取状态失败'))

        return StatusResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[HotDB API] 获取状态失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/symbols", response_model=SymbolsResponse, summary="列出所有股票")
async def list_hotdb_symbols(
    limit: Optional[int] = Query(None, ge=1, le=1000, description="最多返回的股票数量")
):
    """列出热数据库中的所有股票

    返回热数据库中存储的股票代码列表。
    """
    try:
        service = get_hotdb_service()

        result = await run_in_threadpool(
            service.list_symbols,
            limit=limit
        )

        if not result.get('success'):
            raise HTTPException(status_code=500, detail=result.get('error', '获取股票列表失败'))

        return SymbolsResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[HotDB API] 获取股票列表失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/check/{symbol}", response_model=CheckResponse, summary="检查股票是否存在")
async def check_hotdb_symbol(symbol: str = Path(..., description="股票代码（如 600519.SH）")):
    """检查股票是否在热数据库中

    返回指定股票是否在热数据库中存在数据。
    """
    try:
        service = get_hotdb_service()

        result = await run_in_threadpool(
            service.has_symbol,
            symbol=symbol
        )

        if not result.get('success'):
            raise HTTPException(status_code=500, detail=result.get('error', '检查失败'))

        return CheckResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[HotDB API] 检查 {symbol} 失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ─── 批量更新 LocalDB ───────────────────────────────────────────────────────

class BatchUpdateLocalDBRequest(BaseModel):
    """批量更新 LocalDB 请求"""
    symbols: List[str] = Field(..., description="股票代码列表", min_length=1, max_length=500)
    periods: List[str] = Field(
        default=['1d', '5m'],
        description="周期列表（如 ['1d', '5m']）"
    )
    source: str = Field(
        default='pytdx',
        description="数据源（pytdx/xtquant/tdxquant）"
    )


class BatchUpdateLocalDBResponse(BaseModel):
    """批量更新 LocalDB 响应"""
    success: bool
    task_id: Optional[str] = None
    message: Optional[str] = None
    total: Optional[int] = None
    error: Optional[str] = None


@router.post("/update-localdb", response_model=BatchUpdateLocalDBResponse, summary="批量更新 LocalDB")
async def batch_update_localdb(request: BatchUpdateLocalDBRequest):
    """
    批量更新 LocalDB（冷数据库）

    创建后台任务，从在线源获取数据并保存到 LocalDB。
    进度通过 WebSocket 实时推送。

    WebSocket 连接: ws://localhost:8000/ws/batch-update/{task_id}

    进度消息格式:
      {
        "type": "progress",
        "total": 200,
        "completed": 45,
        "current_symbol": "000001.SZ",
        "current_period": "1d",
        "status": "in_progress"
      }

    返回: task_id，用于 WebSocket 连接
    """
    try:
        from myquant.api.dataget.batch_update_ws import get_batch_manager

        batch_manager = get_batch_manager()

        # 创建任务
        task_id = batch_manager.create_task(
            symbols=request.symbols,
            periods=request.periods
        )

        # 在后台线程中执行批量更新
        import asyncio
        from myquant.api.dataget.batch_update_ws import execute_batch_update

        async def run_task():
            await execute_batch_update(
                task_id=task_id,
                symbols=request.symbols,
                periods=request.periods,
                source=request.source
            )

        # 启动后台任务
        asyncio.create_task(run_task())

        return BatchUpdateLocalDBResponse(
            success=True,
            task_id=task_id,
            message=f"批量更新任务已创建，共 {len(request.symbols) * len(request.periods)} �",
            total=len(request.symbols) * len(request.periods)
        )

    except Exception as e:
        logger.error(f"[HotDB API] 创建批量更新任务失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

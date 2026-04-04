"""
HotDB 管理 API 路由

提供个股数据管理功能：
- 检查数据缺口
- 智能补全
- 下载数据
- 清除数据
"""

from fastapi import APIRouter, HTTPException
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from loguru import logger
from datetime import datetime

from myquant.core.market.services.hotdb_service import get_hotdb_service
from myquant.core.market.services.kline_service import get_kline_service


router = APIRouter(tags=["HotDB管理"])


# ─── 请求模型 ────────────────────────────────────────────────────────────

class CheckGapsRequest(BaseModel):
    """检查数据缺口请求"""
    symbol: str = Field(..., description="股票代码，如 601628.SH")
    periods: List[str] = Field(default=["5m", "15m", "30m", "1h", "1d"], description="要检查的周期列表")


class SmartUpdateRequest(BaseModel):
    """智能补全请求"""
    symbol: str = Field(..., description="股票代码")
    periods: List[str] = Field(..., description="要补全的周期列表，如 ['5m', '1d']")


class DownloadDataRequest(BaseModel):
    """下载数据请求"""
    symbol: str = Field(..., description="股票代码")
    periods: List[str] = Field(..., description="要下载的周期列表")
    start_date: Optional[str] = Field(None, description="开始日期 YYYYMMDD")
    end_date: Optional[str] = Field(None, description="结束日期 YYYYMMDD")
    source: str = Field(default="pytdx", description="数据源：pytdx/xtquant/tdxquant")


class ClearDataRequest(BaseModel):
    """清除数据请求"""
    symbol: str = Field(..., description="股票代码")
    periods: List[str] = Field(..., description="要清除的周期列表，如 ['5m']")


# ─── 响应模型 ────────────────────────────────────────────────────────────

class PeriodGapInfo(BaseModel):
    """单周期缺口信息"""
    period: str
    has_data: bool
    has_gap: bool
    # LocalDB 完整数据（参考标准）
    localdb_count: Optional[int] = None
    localdb_earliest: Optional[str] = None
    localdb_latest: Optional[str] = None
    # HotDB 现有数据
    hotdb_count: Optional[int] = None
    hotdb_earliest: Optional[str] = None
    hotdb_latest: Optional[str] = None
    # 缺失数据
    missing_count: Optional[int] = 0
    missing_earliest: Optional[str] = None
    missing_latest: Optional[str] = None
    # 描述
    gap_reason: Optional[str]
    gap_description: str


class CheckGapsResponse(BaseModel):
    """检查缺口响应"""
    symbol: str
    gaps: List[PeriodGapInfo]
    summary: Dict[str, Any]


class SmartUpdateResponse(BaseModel):
    """智能补全响应"""
    symbol: str
    results: Dict[str, Any]
    summary: str


class DownloadDataResponse(BaseModel):
    """下载数据响应"""
    symbol: str
    results: Dict[str, Any]
    summary: str


class ClearDataResponse(BaseModel):
    """清除数据响应"""
    symbol: str
    results: Dict[str, Any]
    summary: str


# ─── API 端点 ─────────────────────────────────────────────────────────────

@router.post("/check_gaps", response_model=CheckGapsResponse)
async def check_data_gaps(request: CheckGapsRequest) -> CheckGapsResponse:
    """检查数据缺口

    检查指定股票在各周期上的数据缺口情况。
    使用 HotDBService 的智能缺口检测方法。
    """
    try:
        hotdb_service = get_hotdb_service()
        gaps = []

        for period in request.periods:
            # 获取 LocalDB 数据（参考标准）
            localdb_adapter = hotdb_service._get_localdb_adapter()
            localdb_count = None
            localdb_earliest = None
            localdb_latest = None

            if localdb_adapter and localdb_adapter.is_available():
                try:
                    localdb_info = localdb_adapter.get_data_info(request.symbol, period)
                    if localdb_info and localdb_info.get('has_data'):
                        localdb_count = localdb_info.get('count')
                        localdb_earliest = str(localdb_info.get('earliest')) if localdb_info.get('earliest') else None
                        localdb_latest = str(localdb_info.get('latest')) if localdb_info.get('latest') else None
                except Exception:
                    pass

            # 获取 HotDB 数据（现有数据）
            adapter = hotdb_service._get_hotdb_adapter()
            if not adapter or not adapter.is_available():
                gaps.append(PeriodGapInfo(
                    period=period,
                    has_data=False,
                    has_gap=True,
                    gap_reason="hotdb_unavailable",
                    gap_description="HotDB 不可用",
                    localdb_count=localdb_count,
                    localdb_earliest=localdb_earliest,
                    localdb_latest=localdb_latest
                ))
                continue

            info = adapter.get_data_info(request.symbol, period)
            if not info or not info.get('has_data'):
                # HotDB 无数据，LocalDB 有数据 = 全部缺失
                if localdb_count and localdb_count > 0:
                    gaps.append(PeriodGapInfo(
                        period=period,
                        has_data=False,
                        has_gap=True,
                        gap_reason="no_data_in_hotdb",
                        gap_description=f"HotDB 无数据，LocalDB 有 {localdb_count} 条",
                        localdb_count=localdb_count,
                        localdb_earliest=localdb_earliest,
                        localdb_latest=localdb_latest,
                        missing_count=localdb_count,
                        missing_earliest=localdb_earliest,
                        missing_latest=localdb_latest
                    ))
                else:
                    gaps.append(PeriodGapInfo(
                        period=period,
                        has_data=False,
                        has_gap=True,
                        gap_reason="no_data",
                        gap_description="无数据",
                        localdb_count=localdb_count,
                        localdb_earliest=localdb_earliest,
                        localdb_latest=localdb_latest
                    ))
                continue

            # 有数据，使用智能缺口检测
            hotdb_count = info.get('count', 0)
            hotdb_earliest = str(info.get('earliest')) if info.get('earliest') else None
            hotdb_latest = str(info.get('latest')) if info.get('latest') else None

            # 调用 Service 层的智能缺口检测
            gap_info = hotdb_service._detect_gap(request.symbol, period)

            if gap_info and gap_info.get('has_gap'):
                # 有缺口
                gap_reason = gap_info.get('reason', 'unknown')
                missing_start = gap_info.get('missing_start')
                missing_end = gap_info.get('missing_end')

                # 计算缺失数据量（估算）
                missing_count = 0
                if missing_start and missing_end:
                    from pandas import Timestamp
                    if isinstance(missing_start, str):
                        missing_start = Timestamp(missing_start)
                    if isinstance(missing_end, str):
                        missing_end = Timestamp(missing_end)

                    days_diff = (missing_end - missing_start).days
                    missing_count = days_diff
                    if period != '1d':
                        # 分钟线估算
                        if period == '5m':
                            missing_count = days_diff * 48
                        elif period == '15m':
                            missing_count = days_diff * 16
                        elif period == '30m':
                            missing_count = days_diff * 8
                        elif period == '1h':
                            missing_count = days_diff * 4

                description = f"发现缺口: {gap_reason}"
                if missing_start and missing_end:
                    description += f" ({missing_start.strftime('%Y-%m-%d') if hasattr(missing_start, 'strftime') else missing_start} ~ {missing_end.strftime('%Y-%m-%d') if hasattr(missing_end, 'strftime') else missing_end})"

                gaps.append(PeriodGapInfo(
                    period=period,
                    has_data=True,
                    has_gap=True,
                    gap_reason=gap_reason,
                    gap_description=description,
                    localdb_count=localdb_count,
                    localdb_earliest=localdb_earliest,
                    localdb_latest=localdb_latest,
                    hotdb_count=hotdb_count,
                    hotdb_earliest=hotdb_earliest,
                    hotdb_latest=hotdb_latest,
                    missing_count=missing_count,
                    missing_earliest=str(missing_start) if missing_start else None,
                    missing_latest=str(missing_end) if missing_end else None
                ))
            else:
                # 无缺口
                gaps.append(PeriodGapInfo(
                    period=period,
                    has_data=True,
                    has_gap=False,
                    gap_reason="up_to_date",
                    gap_description="数据完整",
                    localdb_count=localdb_count,
                    localdb_earliest=localdb_earliest,
                    localdb_latest=localdb_latest,
                    hotdb_count=hotdb_count,
                    hotdb_earliest=hotdb_earliest,
                    hotdb_latest=hotdb_latest,
                    missing_count=0
                ))

        # 统计摘要
        total_periods = len(gaps)
        has_gap_count = sum(1 for g in gaps if g.has_gap)
        no_data_count = sum(1 for g in gaps if not g.has_data)

        return CheckGapsResponse(
            symbol=request.symbol,
            gaps=gaps,
            summary={
                "total_periods": total_periods,
                "has_gap": has_gap_count,
                "no_data": no_data_count,
                "normal": total_periods - has_gap_count
            }
        )

    except Exception as e:
        logger.error(f"[HotDB API] 检查缺口失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/smart_update", response_model=SmartUpdateResponse)
async def smart_update_data(request: SmartUpdateRequest) -> SmartUpdateResponse:
    """智能补全数据

    对指定股票的指定周期进行智能增量补全。
    """
    try:
        hotdb_service = get_hotdb_service()
        results = {}
        success_count = 0
        failed_count = 0

        for period in request.periods:
            result = hotdb_service.smart_update(request.symbol, period)
            results[period] = result

            if result.get('success'):
                success_count += 1
            else:
                failed_count += 1

        summary = f"补全完成：成功 {success_count}，失败 {failed_count}"

        return SmartUpdateResponse(
            symbol=request.symbol,
            results=results,
            summary=summary
        )

    except Exception as e:
        logger.error(f"[HotDB API] 智能补全失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/download", response_model=DownloadDataResponse)
async def download_data(request: DownloadDataRequest) -> DownloadDataResponse:
    """下载数据

    从指定数据源下载指定时间范围的数据。
    """
    try:
        kline_service = get_kline_service()
        results = {}
        success_count = 0
        failed_count = 0

        for period in request.periods:
            # 使用 KlineService 下载到 HotDB
            result = kline_service.download_to_hotdb(
                symbols=[request.symbol],
                periods=[period],
                source=request.source
            )

            period_result = result.get('details', {}).get(request.symbol, {}).get(period, {})
            results[period] = period_result

            if period_result.get('success'):
                success_count += 1
            else:
                failed_count += 1

        summary = f"下载完成：成功 {success_count}，失败 {failed_count}"

        return DownloadDataResponse(
            symbol=request.symbol,
            results=results,
            summary=summary
        )

    except Exception as e:
        logger.error(f"[HotDB API] 下载数据失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/clear", response_model=ClearDataResponse)
async def clear_data(request: ClearDataRequest) -> ClearDataResponse:
    """清除数据

    清除指定股票的指定周期数据。
    """
    try:
        hotdb_service = get_hotdb_service()
        results = {}
        success_count = 0
        failed_count = 0

        for period in request.periods:
            result = hotdb_service.delete_symbol(
                symbol=request.symbol,
                period=period
            )
            results[period] = result

            if result.get('success'):
                success_count += 1
            else:
                failed_count += 1

        # 清除统一缓存（确保前端获取到最新数据）
        # 注意：缓存键使用原始 period 值，不需要映射
        from myquant.core.market.services.cache_manager_service import get_cache_manager, CachePartition

        cache_manager = get_cache_manager()
        for period in request.periods:
            # 直接使用原始 period 值（如 1w, 1M），不映射
            cache_key = f"{request.symbol}:{period}"
            cache_manager.delete(CachePartition.RAW_KLINE, cache_key)
            logger.info(f"[HotDB API] 清除缓存: {cache_key}")

        summary = f"清除完成：成功 {success_count}，失败 {failed_count}"

        return ClearDataResponse(
            symbol=request.symbol,
            results=results,
            summary=summary
        )

    except Exception as e:
        logger.error(f"[HotDB API] 清除数据失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status/{symbol}")
async def get_stock_status(symbol: str) -> Dict[str, Any]:
    """获取股票数据状态

    返回指定股票在 HotDB 中的数据状态概览。
    """
    try:
        hotdb_service = get_hotdb_service()
        status = hotdb_service.get_status()

        if not status.get('success'):
            return {"symbol": symbol, "error": status.get('error')}

        # 过滤出该股票的数据
        adapter = hotdb_service._get_hotdb_adapter()
        if not adapter:
            return {"symbol": symbol, "error": "HotDB 不可用"}

        periods = ['1m', '5m', '15m', '30m', '1h', '1d', '1w', '1mon']
        stock_status = {
            "symbol": symbol,
            "periods": {}
        }

        for period in periods:
            info = adapter.get_data_info(symbol, period)
            if info and info.get('has_data'):
                stock_status["periods"][period] = {
                    "count": info.get('count'),
                    "earliest": str(info.get('earliest')) if info.get('earliest') else None,
                    "latest": str(info.get('latest')) if info.get('latest') else None,
                }

        return stock_status

    except Exception as e:
        logger.error(f"[HotDB API] 获取状态失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/auto_check")
async def trigger_auto_check() -> Dict[str, Any]:
    """手动触发自动检查补全

    对所有自选股进行智能缺口检测和补全。
    """
    try:
        hotdb_service = get_hotdb_service()

        # 获取所有自选股
        from myquant.api.dataget.watchlist import get_watchlist

        watchlist_response = await get_watchlist()
        watchlist = watchlist_response.data if hasattr(watchlist_response, 'data') else watchlist_response

        all_symbols = []
        for group in watchlist.get('groups', []):
            for stock in group.get('stocks', []):
                all_symbols.append(stock['symbol'])

        # 执行自动检查
        result = hotdb_service.auto_check_and_fill_today(all_symbols)

        return result
    except Exception as e:
        logger.error(f"[HotDB API] 自动检查失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/auto_check_with_progress")
async def trigger_auto_check_with_progress() -> Dict[str, Any]:
    """手动触发自动检查补全（带进度条）

    创建一个后台任务，对所有自选股进行智能缺口检测和补全。
    返回 task_id，前端通过 WebSocket 连接 /ws/batch-update/{task_id} 接收进度。

    Returns:
        {"task_id": "uuid", "message": "任务已创建"}
    """
    import asyncio
    from myquant.api.dataget.batch_update_ws import get_batch_manager, execute_auto_check

    try:
        # 获取所有自选股
        from myquant.api.dataget.watchlist import get_watchlist

        watchlist_response = await get_watchlist()
        watchlist = watchlist_response.data if hasattr(watchlist_response, 'data') else watchlist_response

        all_symbols = []
        for group in watchlist.get('groups', []):
            for stock in group.get('stocks', []):
                all_symbols.append(stock['symbol'])

        # 创建任务
        batch_manager = get_batch_manager()
        task_id = batch_manager.create_task(
            symbols=all_symbols,
            periods=[]  # 自动检查不需要指定周期
        )

        # 在后台执行任务
        async def run_task():
            await execute_auto_check(task_id, all_symbols)

        # 创建后台任务
        asyncio.create_task(run_task())

        logger.info(f"[HotDB API] 自动检查任务已创建: {task_id}")

        return {
            "task_id": task_id,
            "total": len(all_symbols),
            "message": "自动检查任务已创建，请通过 WebSocket 连接接收进度"
        }
    except Exception as e:
        logger.error(f"[HotDB API] 创建自动检查任务失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status/daily")
async def get_daily_status() -> Dict[str, Any]:
    """获取每日数据状态

    返回所有股票的每日检查状态。
    """
    try:
        from myquant.core.market.services.daily_data_status import get_daily_status_service
        status_service = get_daily_status_service()
        return status_service.get_status()
    except Exception as e:
        logger.error(f"[HotDB API] 获取状态失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

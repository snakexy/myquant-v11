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


router = APIRouter(prefix="/hotdb", tags=["HotDB管理"])


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
    count: int
    earliest: Optional[str]
    latest: Optional[str]
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
    """
    try:
        hotdb_service = get_hotdb_service()
        gaps = []

        for period in request.periods:
            # 获取数据信息
            adapter = hotdb_service._get_hotdb_adapter()
            if not adapter or not adapter.is_available():
                gaps.append(PeriodGapInfo(
                    period=period,
                    has_data=False,
                    has_gap=True,
                    count=0,
                    earliest=None,
                    latest=None,
                    gap_reason="hotdb_unavailable",
                    gap_description="HotDB 不可用"
                ))
                continue

            info = adapter.get_data_info(request.symbol, period)
            if not info or not info.get('has_data'):
                gaps.append(PeriodGapInfo(
                    period=period,
                    has_data=False,
                    has_gap=True,
                    count=0,
                    earliest=None,
                    latest=None,
                    gap_reason="no_data",
                    gap_description="无数据"
                ))
                continue

            # 有数据，检查缺口
            from myquant.core.market.services.hotdb_service import HotDBService
            service = HotDBService()
            gap_info = service._detect_gap(request.symbol, period)

            if gap_info:
                has_gap = gap_info.get('has_gap', False)
                reason = gap_info.get('reason', '')
                latest = gap_info.get('latest')

                # 构建描述
                if not has_gap:
                    desc = "数据正常"
                elif reason == 'latest_data_gap':
                    days_missing = gap_info.get('days_missing', 0)
                    desc = f"落后 {days_missing} 个交易日"
                elif reason == 'internal_gap':
                    gap_size = gap_info.get('gap_size_hours', 0)
                    desc = f"内部缺口 {gap_size} 小时"
                elif reason == 'intraday_gap':
                    minutes_missing = gap_info.get('minutes_missing', 0)
                    desc = f"盘中缺口 {minutes_missing} 分钟"
                else:
                    desc = reason

                gaps.append(PeriodGapInfo(
                    period=period,
                    has_data=True,
                    has_gap=has_gap,
                    count=info.get('count', 0),
                    earliest=str(info.get('earliest')) if info.get('earliest') else None,
                    latest=str(info.get('latest')) if info.get('latest') else None,
                    gap_reason=reason if has_gap else None,
                    gap_description=desc
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

            if period_result.get('status') == 'success':
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

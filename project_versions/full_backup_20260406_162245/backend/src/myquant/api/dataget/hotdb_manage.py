"""
HotDB 数据管理 API 路由

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

from myquant.core.market.services.hotdb_service import HotdbService
from myquant.core.market.services.kline_service import get_kline_service


router = APIRouter(prefix="/hotdb", tags=["HotDB管理"])


# ─── 请求模型 ────────────────────────────────────────────────────────────

class CheckGapsRequest(BaseModel):
    """检查数据缺口请求"""
    symbol: str = Field(..., description="股票代码")
    periods: List[str] = Field(default=["5m", "15m", "30m", "1h", "1d"], description="周期列表")


class SmartUpdateRequest(BaseModel):
    """智能补全请求"""
    symbol: str = Field(..., description="股票代码")
    periods: List[str] = Field(..., description="周期列表")


class DownloadDataRequest(BaseModel):
    """下载数据请求"""
    symbol: str = Field(..., description="股票代码")
    periods: List[str] = Field(..., description="周期列表")
    source: str = Field(default="pytdx", description="数据源")


class ClearDataRequest(BaseModel):
    """清除数据请求"""
    symbol: str = Field(..., description="股票代码")
    periods: List[str] = Field(..., description="周期列表")


# ─── API 端点 ─────────────────────────────────────────────────────────────

@router.post("/check_gaps")
async def check_data_gaps(request: CheckGapsRequest) -> Dict[str, Any]:
    """检查数据缺口"""
    try:
        service = HotdbService()
        gaps = []

        for period in request.periods:
            adapter = service._get_hotdb_adapter()
            if not adapter or not adapter.is_available():
                gaps.append({
                    'period': period,
                    'has_data': False,
                    'has_gap': True,
                    'count': 0,
                    'gap_description': 'HotDB 不可用'
                })
                continue

            info = adapter.get_data_info(request.symbol, period)

            if not info.get('has_data'):
                gaps.append({
                    'period': period,
                    'has_data': False,
                    'has_gap': True,
                    'count': 0,
                    'gap_description': '无数据'
                })
                continue

            # 检查缺口
            gap_info = service._detect_gap(request.symbol, period)
            has_gap = gap_info.get('has_gap', False)
            reason = gap_info.get('reason', '')

            if not has_gap:
                desc = "数据正常"
            elif reason == 'latest_data_gap':
                desc = f"落后 {gap_info.get('days_missing', 0)} 个交易日"
            else:
                desc = reason

            gaps.append({
                'period': period,
                'has_data': True,
                'has_gap': has_gap,
                'count': info.get('count', 0),
                'earliest': str(info.get('earliest')) if info.get('earliest') else None,
                'latest': str(info.get('latest')) if info.get('latest') else None,
                'gap_description': desc
            })

        return {'symbol': request.symbol, 'gaps': gaps}

    except Exception as e:
        logger.error(f"[HotDB API] 检查缺口失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/smart_update")
async def smart_update_data(request: SmartUpdateRequest) -> Dict[str, Any]:
    """智能补全数据"""
    try:
        service = HotdbService()
        results = {}

        for period in request.periods:
            result = service.smart_update(request.symbol, period)
            results[period] = result

        success_count = sum(1 for r in results.values() if r.get('success'))
        summary = f"补全完成：成功 {success_count}，失败 {len(request.periods) - success_count}"

        return {'symbol': request.symbol, 'results': results, 'summary': summary}

    except Exception as e:
        logger.error(f"[HotDB API] 智能补全失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/download")
async def download_data(request: DownloadDataRequest) -> Dict[str, Any]:
    """下载数据"""
    try:
        kline_service = get_kline_service()
        result = kline_service.download_to_hotdb(
            symbols=[request.symbol],
            periods=request.periods,
            source=request.source
        )

        details = result.get('details', {}).get(request.symbol, {})
        success_count = sum(1 for r in details.values() if r.get('success'))

        return {
            'symbol': request.symbol,
            'results': details,
            'summary': f"下载完成：成功 {success_count}，失败 {len(request.periods) - success_count}"
        }

    except Exception as e:
        logger.error(f"[HotDB API] 下载数据失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/clear")
async def clear_data(request: ClearDataRequest) -> Dict[str, Any]:
    """清除数据"""
    try:
        service = HotdbService()
        results = {}

        for period in request.periods:
            result = service.delete_symbol(request.symbol, period)
            results[period] = result

        success_count = sum(1 for r in results.values() if r.get('success'))

        return {
            'symbol': request.symbol,
            'results': results,
            'summary': f"清除完成：成功 {success_count}，失败 {len(request.periods) - success_count}"
        }

    except Exception as e:
        logger.error(f"[HotDB API] 清除数据失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status/{symbol}")
async def get_stock_status(symbol: str) -> Dict[str, Any]:
    """获取股票数据状态"""
    try:
        service = HotdbService()
        status = service.get_status(symbol)

        if not status.get('success'):
            return {'symbol': symbol, 'error': status.get('error')}

        return status

    except Exception as e:
        logger.error(f"[HotDB API] 获取状态失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

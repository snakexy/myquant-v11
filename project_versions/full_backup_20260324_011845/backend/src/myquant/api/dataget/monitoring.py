"""
V5 实时监控服务 API 路由

提供热点板块发现、异常检测、市场概览等功能
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from pydantic import BaseModel
from loguru import logger

from myquant.core.market.services import get_monitor_service


router = APIRouter(tags=["实时监控"])


# 响应模型
class MonitoringResponse(BaseModel):
    """监控响应"""
    code: int = 0
    data: Optional[dict] = None
    message: str = "success"


@router.get("/hot-sectors", response_model=MonitoringResponse)
async def get_hot_sectors(
    limit: int = Query(20, description="返回数量", ge=1, le=100),
    min_change_pct: float = Query(0.5, description="最小涨跌幅阈值")
):
    """发现热点板块

    返回按涨跌幅排序的热点板块列表
    """
    try:
        logger.info(
            "获取热点板块: limit={}, min_change_pct={}",
            limit, min_change_pct
        )

        service = get_monitor_service()

        hot_sectors = service.find_hot_sectors(
            limit=limit,
            min_change_pct=min_change_pct
        )

        # 转换为字典格式
        data = {
            'count': len(hot_sectors),
            'sectors': [
                {
                    'code': s.code,
                    'name': s.name,
                    'index': s.index,
                    'change_pct': s.change_pct,
                    'up_count': s.up_count,
                    'down_count': s.down_count,
                    'component_count': s.component_count,
                    'amount': s.amount,
                    'volume_ratio': s.volume_ratio,
                    'turnover_rate': s.turnover_rate,
                    'amplitude': s.amplitude,
                    'pe_ratio': s.pe_ratio,
                    'pb_ratio': s.pb_ratio,
                    'timestamp': s.timestamp,
                }
                for s in hot_sectors
            ]
        }

        logger.info("热点板块获取成功: {} 个", len(hot_sectors))

        return MonitoringResponse(data=data)

    except Exception as e:
        logger.error("获取热点板块失败: {}", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/hot-stocks", response_model=MonitoringResponse)
async def get_hot_stocks(
    sector_code: Optional[str] = Query(None, description="板块代码"),
    limit: int = Query(50, description="返回数量", ge=1, le=200),
    min_change_pct: float = Query(3.0, description="最小涨跌幅阈值")
):
    """发现热点股票

    返回按涨跌幅排序的热点股票列表
    """
    try:
        logger.info("获取热点股票: sector={}, limit={}, min_change_pct={}",
                    sector_code, limit, min_change_pct)

        service = get_monitor_service()

        hot_stocks = service.find_hot_stocks(
            sector_code=sector_code,
            limit=limit,
            min_change_pct=min_change_pct
        )

        # 转换为字典格式
        data = {
            'count': len(hot_stocks),
            'sector': sector_code,
            'stocks': [
                {
                    'code': s.code,
                    'name': s.name,
                    'price': s.price,
                    'change': s.change,
                    'change_pct': s.change_pct,
                    'volume': s.volume,
                    'amount': s.amount,
                    'timestamp': s.timestamp,
                }
                for s in hot_stocks
            ]
        }

        logger.info("热点股票获取成功: {} 只", len(hot_stocks))

        return MonitoringResponse(data=data)

    except Exception as e:
        logger.error("获取热点股票失败: {}", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/anomaly", response_model=MonitoringResponse)
async def detect_anomaly(
    symbols: List[str],
    volume_ratio_threshold: float = Query(3.0, description="成交量倍数阈值"),
    swing_threshold: float = Query(5.0, description="振幅阈值")
):
    """发现异常股票

    检测成交量放大、振幅异常等
    """
    try:
        logger.info("检测异常股票: {} 只股票", len(symbols))

        service = get_monitor_service()

        anomalies = service.find_anomaly_stocks(
            symbols=symbols,
            volume_ratio_threshold=volume_ratio_threshold,
            swing_threshold=swing_threshold
        )

        data = {
            'count': len(anomalies),
            'thresholds': {
                'volume_ratio': volume_ratio_threshold,
                'swing': swing_threshold,
            },
            'anomalies': anomalies
        }

        logger.info("异常股票检测完成: {} 只", len(anomalies))

        return MonitoringResponse(data=data)

    except Exception as e:
        logger.error("检测异常股票失败: {}", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/market-summary", response_model=MonitoringResponse)
async def get_market_summary():
    """获取市场概览

    包含主要指数、热点板块、热点股票
    """
    try:
        logger.info("获取市场概览")

        service = get_monitor_service()

        summary = service.get_market_summary()

        return MonitoringResponse(data=summary)

    except Exception as e:
        logger.error("获取市场概览失败: {}", e)
        raise HTTPException(status_code=500, detail=str(e))

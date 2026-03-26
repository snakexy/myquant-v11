"""
V5 实时行情服务 API 路由

提供实时行情获取、热点扫描、推送等功能
"""

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse
from typing import List, Optional
from pydantic import BaseModel
from loguru import logger

from myquant.core.market.services import get_realtime_market_service, get_seamless_kline_service
from myquant.core.market.utils.trading_time import TradingTimeChecker


router = APIRouter(tags=["实时行情"])


# 响应模型
class MarketResponse(BaseModel):
    """行情响应"""
    code: int = 0
    data: Optional[dict] = None
    message: str = "success"


@router.post("/quotes", response_model=MarketResponse)
async def get_realtime_quotes(
    codes: List[str],
    use_cache: bool = Query(False, description="是否使用缓存")  # 临时禁用缓存，强制使用 XtQuant
):
    """获取实时行情

    批量获取股票的实时行情数据
    """
    try:
        logger.info("获取实时行情: {} 只股票, use_cache={}", len(codes), use_cache)

        service = get_realtime_market_service()

        quotes, data_source = service.get_realtime_quotes(
            codes=codes,
            use_cache=use_cache
        )

        data = {
            'count': len(quotes),
            'quotes': quotes,
            'data_source': data_source,
        }

        logger.info("实时行情获取成功: {} 只股票, 来源={}", len(quotes), data_source)

        return MarketResponse(data=data)

    except Exception as e:
        logger.error("获取实时行情失败: {}", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/snapshot/")
async def get_snapshot_batch(
    symbols: str = Query(..., description="逗号分隔的股票代码，如 000001.SZ,600000.SH")
):
    """批量获取股票快照（GET 方式）

    返回格式匹配前端 SnapshotResponse: {data: [...], data_source, count, timestamp}
    """
    try:
        codes = [s.strip() for s in symbols.split(',') if s.strip()]
        service = get_realtime_market_service()
        quotes, data_source = service.get_realtime_quotes(
            codes=codes, use_cache=True
        )
        return JSONResponse({
            'data': [
                {**q, 'symbol': q.get('code', '')}
                for q in quotes.values()
            ],
            'data_source': data_source,
            'count': len(quotes),
            'timestamp': 0,
        })
    except Exception as e:
        logger.error("批量获取快照失败: {}", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/snapshot/{symbol}")
async def get_snapshot_single(symbol: str):
    """获取单只股票快照（GET 方式）

    返回格式匹配前端 QuoteSnapshot（裸数据，无 code/data/message 包装）
    """
    try:
        service = get_realtime_market_service()
        quotes, data_source = service.get_realtime_quotes(
            codes=[symbol], use_cache=True
        )
        quote = quotes.get(symbol, {})
        return JSONResponse({
            **quote,
            'symbol': quote.get('code', ''),
            'data_source': data_source
        })
    except Exception as e:
        logger.error("获取快照失败 {}: {}", symbol, e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/hot-stocks/scan", response_model=MarketResponse)
async def scan_hot_stocks(
    market: str = Query("all", description="市场范围: all/sh/sz"),
    min_change_pct: float = Query(3.0, description="最小涨跌幅"),
    limit: int = Query(50, description="返回数量", ge=1, le=200)
):
    """扫描热点股票

    全市场扫描，找出涨幅最大的股票
    """
    try:
        logger.info("扫描热点股票: market={}, min_change_pct={}, limit={}",
                    market, min_change_pct, limit)

        service = get_realtime_market_service()

        hot_stocks = service.scan_hot_stocks(
            market=market,
            min_change_pct=min_change_pct,
            limit=limit
        )

        # 转换为字典格式
        data = {
            'count': len(hot_stocks),
            'scan_params': {
                'market': market,
                'min_change_pct': min_change_pct,
            },
            'stocks': [
                {
                    'code': s.code,
                    'name': s.name,
                    'price': s.price,
                    'change_pct': s.change_pct,
                    'volume_ratio': s.volume_ratio,
                    'reason': s.reason,
                    'timestamp': s.timestamp.isoformat(),
                }
                for s in hot_stocks
            ]
        }

        logger.info("热点扫描完成: {} 只股票", len(hot_stocks))

        return MarketResponse(data=data)

    except Exception as e:
        logger.error("扫描热点股票失败: {}", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/hot-stocks/pool", response_model=MarketResponse)
async def get_hot_stocks_pool(
    limit: int = Query(20, description="返回数量", ge=1, le=100)
):
    """获取当前热点股票池

    从已扫描的热点池中获取数据
    """
    try:
        logger.info("获取热点股票池: limit={}", limit)

        service = get_realtime_market_service()

        hot_stocks = service.get_hot_stocks(limit=limit)

        data = {
            'count': len(hot_stocks),
            'stocks': [
                {
                    'code': s.code,
                    'name': s.name,
                    'price': s.price,
                    'change_pct': s.change_pct,
                    'volume_ratio': s.volume_ratio,
                    'reason': s.reason,
                    'timestamp': s.timestamp.isoformat(),
                }
                for s in hot_stocks
            ]
        }

        return MarketResponse(data=data)

    except Exception as e:
        logger.error("获取热点池失败: {}", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/subscriptions/update", response_model=MarketResponse)
async def update_subscriptions(hot_symbols: List[str]):
    """更新订阅列表

    根据热点股票更新订阅
    """
    try:
        logger.info("更新订阅列表: {} 只股票", len(hot_symbols))

        service = get_realtime_market_service()

        success = service.update_subscriptions(hot_symbols)

        data = {
            'success': success,
            'updated_count': len(hot_symbols),
        }

        return MarketResponse(data=data)

    except Exception as e:
        logger.error("更新订阅失败: {}", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status", response_model=MarketResponse)
async def get_market_status():
    """获取实时行情服务状态

    查看订阅状态、热点池大小、缓存统计等
    """
    try:
        service = get_realtime_market_service()

        status = service.get_market_status()

        return MarketResponse(data=status)

    except Exception as e:
        logger.error("获取服务状态失败: {}", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/cache/stats", response_model=MarketResponse)
async def get_cache_stats():
    """获取缓存统计

    查看L1/L2缓存的命中率和大小
    """
    try:
        service = get_realtime_market_service()

        stats = service.get_cache_stats()

        return MarketResponse(data=stats)

    except Exception as e:
        logger.error("获取缓存统计失败: {}", e)
        raise HTTPException(status_code=500, detail=str(e))


# 前端兼容路由 - 市场状态检查（用于控制自动刷新）
@router.get("/market/status", response_model=MarketResponse)
async def get_quotes_market_status():
    """获取市场状态（前端兼容路由 /api/v1/quotes/market/status）

    用于前端判断是否处于交易时间，控制自动刷新频率：
    - 交易中：高频刷新（3-5秒）
    - 休市：低频刷新或暂停（30秒或更长）
    """
    try:
        from datetime import datetime

        checker = TradingTimeChecker()
        phase = checker.get_current_phase()
        is_trading = checker.is_trading_time()
        now = datetime.now()

        data = {
            'is_open': is_trading,
            'phase': phase.value,
            'phase_description': checker.get_phase_description(),
            'market': 'A股',
            'date': now.strftime('%Y-%m-%d'),
            'time': now.strftime('%H:%M:%S'),
            'status': '交易中' if is_trading else '休市',
            'is_weekend': phase.name == 'WEEKEND',
            'refresh_interval': checker.get_next_refresh_interval(),
            'cache_ttl': checker.get_cache_ttl(),
        }

        logger.debug("市场状态查询: {}", data['status'])

        return MarketResponse(data=data)

    except Exception as e:
        logger.error("获取市场状态失败: {}", e)
        raise HTTPException(status_code=500, detail=str(e))

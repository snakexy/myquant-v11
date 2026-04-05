"""
内存 K 线 API - 零延迟访问

直接从 MmapKlineStore 读取，延迟 <1ms
未命中时返回 404，前端应 fallback 到普通 API
"""

from fastapi import APIRouter, HTTPException, Query
from fastapi.concurrency import run_in_threadpool
from typing import List, Optional
from pydantic import BaseModel, Field
from loguru import logger

from myquant.core.market.services.kline_service import get_kline_service
from myquant.core.market.services.mmap_kline_store import get_mmap_kline_store


router = APIRouter(prefix="/memory", tags=["内存K线"])


# ─── 响应模型（与 quotes.py KlineItem 兼容）───────────────────────────────

class KlineItem(BaseModel):
    """单根K线"""
    time: int                       # Unix 毫秒时间戳
    open: float
    high: float
    low: float
    close: float
    volume: float
    amount: Optional[float] = None
    color: Optional[str] = None
    is_complete: bool = True


class MemoryKlineResponse(BaseModel):
    """内存K线响应"""
    symbol: str
    period: str
    data: List[KlineItem]
    data_source: str = "mmap"
    count: int
    latency_ms: float


class MemoryStatsResponse(BaseModel):
    """内存缓存统计"""
    cached_files: int
    opens: int
    hits: int
    misses: int
    hit_rate: str


class PreloadRequest(BaseModel):
    """预加载请求"""
    symbols: List[str] = Field(..., description="股票代码列表", min_length=1, max_length=100)
    periods: Optional[List[str]] = Field(None, description="周期列表，默认 ['1d', '5m', '15m', '30m', '1h']")


class PreloadResponse(BaseModel):
    """预加载响应"""
    total_symbols: int
    total_periods: int
    opened: int
    failed: int
    cached_files: int


# ─── 端点 ────────────────────────────────────────────────────────────────────

@router.get("/kline/{symbol}/{period}", response_model=MemoryKlineResponse)
async def get_memory_kline(
    symbol: str,
    period: str,
    count: int = Query(200, description="返回数量", ge=1, le=1000)
):
    """
    从内存获取 K 线数据（零延迟）

    延迟 <1ms，适用于自选股高频切换场景。
    如果数据不在内存中，返回 404，前端应 fallback 到普通 API。

    示例：GET /api/v5/memory/kline/600519.SH/1d?count=200
    """
    import time

    start = time.perf_counter()

    # 通过 Service 层获取 mmap 数据（架构合规）
    kline_service = get_kline_service()
    df = await run_in_threadpool(kline_service.get_from_mmap, symbol, period, count)

    if df is None or df.empty:
        # 自动回源填充：mmap 未命中时，从 KlineService 正常通道获取并写入 mmap
        # 这样前端不会看到 404，且下次即可直接命中
        logger.info(f"[MemoryAPI] {symbol} {period} mmap 未命中，启动自动回源填充...")
        df = await run_in_threadpool(kline_service.get_historical_kline, symbol, period, count=2000)
        if df is not None and not df.empty:
            store = get_mmap_kline_store()
            await run_in_threadpool(store.save, symbol, period, df)
            logger.info(f"[MemoryAPI] {symbol} {period} 自动回源填充完成: {len(df)} 条")
        else:
            raise HTTPException(
                status_code=404,
                detail=f"内存缓存未命中且无法回源: {symbol} {period}"
            )

    # 转换为 KlineItem（与 quotes.py 格式兼容）
    items = []
    prev_close = None

    # 判断是否为日线（需要加收盘时间）
    is_daily = period in ('1d', 'day', '1D')
    
    for _, row in df.iterrows():
        # 时间戳转换：datetime → UTC 毫秒
        # 【关键】与 unified.py 保持一致：naive datetime 视为北京时间
        from datetime import timezone, timedelta
        dt = row['datetime']
        # 日线数据统一设置为 15:00 收盘时间，与 seamless_service 保持一致
        if is_daily and hasattr(dt, 'replace'):
            dt = dt.replace(hour=15, minute=0, second=0, microsecond=0)
        
        if hasattr(dt, 'timestamp'):
            if getattr(dt, 'tzinfo', None) is None:
                # naive datetime: 视为北京时间，加上时区后转UTC时间戳
                from datetime import timezone, timedelta
                dt = dt.replace(tzinfo=timezone(timedelta(hours=8)))
                ts = int(dt.timestamp() * 1000)
            else:
                ts = int(dt.timestamp() * 1000)
        else:
            import pandas as pd
            dt = pd.Timestamp(dt)
            if dt.tzinfo is None:
                # naive datetime: 视为北京时间
                from datetime import timezone, timedelta
                dt = dt.replace(tzinfo=timezone(timedelta(hours=8)))
                ts = int(dt.timestamp() * 1000)
            else:
                ts = int(dt.timestamp() * 1000)

        # 涨跌色
        curr_close = float(row['close'])
        color = '#ef5350' if prev_close is None or curr_close >= prev_close else '#26a69a'
        prev_close = curr_close

        items.append(KlineItem(
            time=ts,
            open=float(row['open']),
            high=float(row['high']),
            low=float(row['low']),
            close=curr_close,
            volume=float(row['volume']),
            amount=float(row.get('amount', 0) or 0),
            color=color,
            is_complete=True
        ))

    latency_ms = (time.perf_counter() - start) * 1000

    logger.info(f"[MemoryAPI] {symbol} {period}: {len(items)} 条, {latency_ms:.2f}ms")

    return MemoryKlineResponse(
        symbol=symbol,
        period=period,
        data=items,
        count=len(items),
        latency_ms=round(latency_ms, 2)
    )


@router.get("/stats", response_model=MemoryStatsResponse)
async def get_memory_stats():
    """
    获取内存缓存统计信息

    示例：GET /api/v5/memory/stats
    """
    store = get_mmap_kline_store()
    stats = await run_in_threadpool(store.get_stats)
    return MemoryStatsResponse(**stats)


@router.post("/preload", response_model=PreloadResponse)
async def preload_symbols(request: PreloadRequest):
    """
    预加载股票数据到内存

    实际是 mmap 打开文件，不加载到 Python 内存。
    系统按需加载数据页，内存占用极低。

    示例：POST /api/v5/memory/preload
    Body: { "symbols": ["600519.SH", "000001.SZ"], "periods": ["1d", "5m"] }
    """
    store = get_mmap_kline_store()
    result = await run_in_threadpool(store.preload_symbols, request.symbols, request.periods)

    return PreloadResponse(**result)


@router.delete("/cache")
async def clear_memory_cache():
    """
    清空内存缓存

    示例：DELETE /api/v5/memory/cache
    """
    store = get_mmap_kline_store()
    await run_in_threadpool(store.clear_cache)
    return {"success": True, "message": "缓存已清空"}

"""
V5 K线服务 API 路由

提供实时K线、无缝K线、日内K线等服务
"""

from fastapi import APIRouter, HTTPException, Query
from fastapi.concurrency import run_in_threadpool
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from loguru import logger
import pandas as pd

from myquant.core.market.services.kline import (
    get_intraday_kline_service,
    get_seamless_kline_service,
    get_kline_service,
)


router = APIRouter(prefix="/kline", tags=["K线服务"])


# ─── 请求模型 ───────────────────────────────────────────────────────────────

class KlineRequest(BaseModel):
    """K线请求（批量/订阅）"""
    symbols: List[str] = Field(..., description="股票代码列表", min_length=1, max_length=100)
    period: str = Field("1m", description="周期: 1m, 5m, 15m, 30m, 1h, 1d")
    count: int = Field(100, description="返回数量", ge=1, le=1000)
    subscribe: bool = Field(True, description="是否启用订阅更新")
    adjust_type: str = Field("none", description="复权类型: none/front/back")


class SeamlessKlineRequest(BaseModel):
    """无缝K线请求（批量）"""
    symbols: List[str] = Field(..., description="股票代码列表", min_length=1, max_length=100)
    period: str = Field("1m", description="周期: 1m, 5m, 15m, 30m, 1h, 1d")
    count: int = Field(100, description="返回数量", ge=1, le=1000)
    end_date: Optional[str] = Field(None, description="结束日期 YYYY-MM-DD")
    start_date: Optional[str] = Field(None, description="开始日期 YYYY-MM-DD")
    days_back: int = Field(5, description="历史回溯天数（当count未指定时使用）", ge=1, le=30)
    adjust_type: str = Field("none", description="复权类型: none/front/back")


# ─── 响应模型 ───────────────────────────────────────────────────────────────

class KlineItem(BaseModel):
    """单根K线（与前端 KlineItem 对齐）"""
    time: int                       # Unix 毫秒时间戳
    open: float
    high: float
    low: float
    close: float
    volume: float
    amount: Optional[float] = None
    color: Optional[str] = None
    is_complete: bool = True


class KlineDataResponse(BaseModel):
    """单只股票K线响应（扁平结构，前端直接消费）"""
    symbol: str
    period: str
    data: List[KlineItem]
    data_source: str
    count: int
    adjust_type: str = 'none'


class KlineBatchResponse(BaseModel):
    """批量K线响应（嵌套结构，用于批量接口）"""
    code: int = 0
    data: Optional[dict] = None
    message: str = "success"


# ─── 工具函数 ────────────────────────────────────────────────────────────────

def _to_unix_timestamp(dt) -> int:
    """将 datetime 转换为 UTC 毫秒时间戳，naive datetime 视为北京时间"""
    import pytz
    beijing_tz = pytz.timezone('Asia/Shanghai')

    if isinstance(dt, datetime):
        if dt.tzinfo is None:
            dt = beijing_tz.localize(dt)
        return int(dt.timestamp() * 1000)
    elif isinstance(dt, pd.Timestamp):
        if dt.tz is None:
            dt = dt.tz_localize('Asia/Shanghai')
        return int(dt.timestamp() * 1000)
    else:
        dt = pd.Timestamp(dt)
        if dt.tz is None:
            dt = dt.tz_localize('Asia/Shanghai')
        return int(dt.timestamp() * 1000)


def _df_to_kline_items(df: pd.DataFrame) -> List[KlineItem]:
    """将 DataFrame 转换为 KlineItem 列表（含时间戳转换和涨跌色）"""
    if df is None or df.empty:
        return []

    items = []
    prev_close = None
    current_year = datetime.now().year

    for _, row in df.iterrows():
        dt_val = row['datetime']

        # numeric datetime → Timestamp
        if isinstance(dt_val, (int, float)):
            dt_val = pd.to_datetime(dt_val, unit='ms' if dt_val > 1e11 else 's', errors='coerce')
            if pd.isna(dt_val):
                continue

        ts = _to_unix_timestamp(dt_val)
        if ts < 0:
            continue

        try:
            year = dt_val.year if hasattr(dt_val, 'year') else pd.Timestamp(dt_val).year
            if year < 1970 or year > current_year + 1:
                continue
        except Exception:
            continue

        vol = float(row['volume'])
        if vol == 0:
            continue

        curr_close = float(row['close'])
        color = '#ef5350' if prev_close is None or curr_close >= prev_close else '#26a69a'
        prev_close = curr_close

        items.append(KlineItem(
            time=ts,
            open=float(row['open']),
            high=float(row['high']),
            low=float(row['low']),
            close=curr_close,
            volume=vol,
            amount=float(row.get('amount', 0) or 0),
            color=color,
            is_complete=bool(row.get('is_complete', True)),
        ))

    return items


def _map_adjust_type(adjust_type: str) -> str:
    """前端复权参数 → 内部标准"""
    return {
        'qfq': 'front', 'hfq': 'back',
        'qfq_ratio': 'front_ratio', 'hfq_ratio': 'back_ratio',
        'none': 'none',
    }.get(adjust_type, adjust_type)


# ─── 端点 ─────────────────────────────────────────────────────────────────────

@router.get("/realtime/{symbol}", response_model=KlineDataResponse)
async def get_realtime_kline(
    symbol: str,
    period: str = Query("1d", description="周期: 1m, 5m, 15m, 30m, 1h, 1d"),
    count: int = Query(100, description="返回数量", ge=1, le=1000),
    adjust_type: str = Query("none", description="复权类型: none/qfq/hfq/qfq_ratio/hfq_ratio"),
    use_cache: bool = Query(True, description="是否使用缓存")
):
    """获取单只股票K线（历史+实时无缝）

    前端主要使用此接口，返回扁平格式（与 v1/quotes/kline 格式兼容）。
    """
    try:
        service = get_seamless_kline_service()
        df = await run_in_threadpool(
            service.get_kline,
            symbol=symbol,
            period=period,
            count=count,
            include_realtime=True,
            adjust_type=_map_adjust_type(adjust_type),
            use_cache=use_cache
        )

        if df is None or df.empty:
            raise HTTPException(status_code=503, detail=f"无法获取 {symbol} 的K线数据")

        items = _df_to_kline_items(df)
        logger.info(f"[V5] {symbol} {period}: {len(items)} 条")

        return KlineDataResponse(
            symbol=symbol,
            period=period,
            data=items,
            data_source='seamless',
            count=len(items),
            adjust_type=adjust_type,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[V5] 获取K线失败: symbol={symbol}, error={e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/aggregated/{symbol}", response_model=KlineDataResponse)
async def get_aggregated_kline(
    symbol: str,
    period: str = Query("1d", description="周期: 5m, 15m, 30m, 1h, 1d"),
    count: int = Query(800, description="返回数量", ge=1, le=2000),
    adjust_type: str = Query("none", description="复权类型: none/qfq/hfq"),
):
    """从后台聚合器获取K线数据（瞬间返回）

    优先从 KlineService 的后台聚合器获取数据（已实时更新）。
    如果聚合器没有数据，降级到 seamless_service。
    """
    try:
        # 优先从后台聚合器获取
        kline_service = get_kline_service()
        bars = await run_in_threadpool(
            kline_service.get_aggregated_bars,
            symbol=symbol,
            period=period
        )

        # 如果聚合器有数据，直接返回
        if bars:
            items = [
                KlineItem(
                    time=bar['time'],
                    open=bar['open'],
                    high=bar['high'],
                    low=bar['low'],
                    close=bar['close'],
                    volume=bar['volume'],
                    amount=bar.get('amount'),
                    is_complete=bar.get('is_complete', True),
                )
                for bar in bars
            ]
            logger.info(f"[V5] aggregated {symbol} {period}: {len(items)} 条 (聚合器)")
            return KlineDataResponse(
                symbol=symbol,
                period=period,
                data=items,
                data_source='aggregated',
                count=len(items),
                adjust_type=adjust_type,
            )

        # 降级：从 seamless_service 获取
        service = get_seamless_kline_service()
        df = await run_in_threadpool(
            service.get_kline,
            symbol=symbol,
            period=period,
            count=count,
            include_realtime=True,
            adjust_type=_map_adjust_type(adjust_type),
        )

        if df is None or df.empty:
            raise HTTPException(status_code=503, detail=f"无法获取 {symbol} 的K线数据")

        items = _df_to_kline_items(df)
        logger.info(f"[V5] {symbol} {period}: {len(items)} 条 (降级seamless)")

        return KlineDataResponse(
            symbol=symbol,
            period=period,
            data=items,
            data_source='seamless',
            count=len(items),
            adjust_type=adjust_type,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[V5] 获取聚合K线失败: symbol={symbol}, error={e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/intraday", response_model=KlineBatchResponse)
async def get_intraday_kline(request: KlineRequest):
    """获取实时K线（订阅+聚合，批量）

    从 L0 订阅获取实时数据，按指定周期聚合。
    """
    try:
        service = get_intraday_kline_service()

        if request.subscribe:
            await run_in_threadpool(service.set_subscription, request.symbols)

        result = await run_in_threadpool(
            service.get_kline,
            symbols=request.symbols,
            period=request.period,
            count=request.count,
            adjust_type=request.adjust_type,
        )

        data = {}
        for symbol, kline_data in result.items():
            data[symbol] = {
                'symbol': symbol,
                'period': request.period,
                'data': kline_data.data.to_dict_list() if kline_data else [],
                'source': 'subscription',
            }

        logger.info(f"[V5] intraday: {len(data)} 只股票")
        return KlineBatchResponse(data=data)

    except Exception as e:
        logger.error(f"[V5] 获取实时K线失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/seamless", response_model=KlineBatchResponse)
async def get_seamless_kline(request: SeamlessKlineRequest):
    """获取无缝K线（历史+实时衔接，批量）"""
    try:
        service = get_seamless_kline_service()
        data = {}

        for symbol in request.symbols:
            try:
                df = await run_in_threadpool(
                    service.get_kline,
                    symbol=symbol,
                    period=request.period,
                    end_date=request.end_date,
                    count=request.count,  # 使用用户请求的数量
                    start_date=request.start_date,
                    include_realtime=True,
                    adjust_type=_map_adjust_type(request.adjust_type),
                )
                if df is not None and not df.empty:
                    mapped_adjust_type = _map_adjust_type(request.adjust_type)
                    data[symbol] = {
                        'symbol': symbol,
                        'period': request.period,
                        'data': [item.dict() for item in _df_to_kline_items(df)],
                        'source': 'seamless',
                        'adjust_type': mapped_adjust_type,
                    }
            except Exception as e:
                logger.warning(f"[V5] seamless {symbol} 失败: {e}")

        logger.info(f"[V5] seamless: {len(data)} 只股票")
        return KlineBatchResponse(data=data)

    except Exception as e:
        logger.error(f"[V5] 获取无缝K线失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/history/{symbol}", response_model=KlineDataResponse)
async def get_history_kline(
    symbol: str,
    period: str = Query("1d", description="周期"),
    start_date: str = Query(..., description="开始日期 YYYY-MM-DD"),
    end_date: str = Query(..., description="结束日期 YYYY-MM-DD"),
    adjust_type: str = Query("none", description="复权类型")
):
    """获取历史K线"""
    try:
        service = get_seamless_kline_service()
        df = await run_in_threadpool(
            service.get_kline,
            symbol=symbol,
            period=period,
            start_date=start_date,
            end_date=end_date,
            include_realtime=False,
            adjust_type=_map_adjust_type(adjust_type)
        )

        if df is None or df.empty:
            raise HTTPException(status_code=404, detail=f"未找到 {symbol} 的历史数据")

        items = _df_to_kline_items(df)
        return KlineDataResponse(
            symbol=symbol, period=period,
            data=items, data_source='seamless',
            count=len(items), adjust_type=adjust_type,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[V5] 获取历史K线失败: symbol={symbol}, error={e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/subscription/status", response_model=KlineBatchResponse)
async def get_subscription_status():
    """获取当前订阅状态"""
    try:
        service = get_intraday_kline_service()
        status = await run_in_threadpool(lambda: {
            'subscribed_symbols': service.get_subscribed_symbols(),
            'subscription_count': len(service.get_subscribed_symbols()),
            'adapter_status': service._get_adapter_status(),
        })
        return KlineBatchResponse(data=status)
    except Exception as e:
        logger.error(f"[V5] 获取订阅状态失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/subscription/update", response_model=KlineBatchResponse)
async def update_subscription(symbols: List[str]):
    """更新订阅列表"""
    try:
        service = get_intraday_kline_service()
        await run_in_threadpool(service.set_subscription, symbols)
        return KlineBatchResponse(data={'subscribed_count': len(symbols)})
    except Exception as e:
        logger.error(f"[V5] 更新订阅失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

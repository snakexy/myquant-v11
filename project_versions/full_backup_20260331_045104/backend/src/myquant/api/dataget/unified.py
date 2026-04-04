"""
统一数据 API 路由

前端通过 /api/v1/data/unified 统一获取所有数据。
后端内部路由到 KlineService（HotDB → LocalDB → 在线源）。
"""

from fastapi import APIRouter, HTTPException
from fastapi.concurrency import run_in_threadpool
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from loguru import logger
import time

from myquant.core.market.services.seamless_service import get_seamless_kline_service
from myquant.core.market.services import get_realtime_market_service
from myquant.core.market.adapters import get_adapter

router = APIRouter(prefix="/data", tags=["统一数据"])


# ─── 请求/响应模型 ────────────────────────────────────────────────────────────

class UnifiedDataRequest(BaseModel):
    data_type: str = Field(..., description="数据类型: kline/realtime_quote/financial/tick")
    symbols: List[str] = Field(..., description="股票代码列表")
    params: Optional[dict] = Field(default_factory=dict, description="请求参数")
    use_cache: bool = Field(True, description="是否使用缓存")


class UnifiedKlineItem(BaseModel):
    """统一K线数据项（与前端 KlineDataItem 对齐）"""
    time: str           # "2026-02-05 15:00:00" 格式
    open: float
    high: float
    low: float
    close: float
    volume: float
    amount: Optional[float] = None
    trading_day_index: Optional[int] = None


class UnifiedDataResponse(BaseModel):
    code: int = 200
    data: Optional[list] = None
    message: str = "success"
    metadata: Optional[dict] = None


# ─── 周期映射 ────────────────────────────────────────────────────────────────

# 前端 unified.ts 周期 → 后端 KlineService 周期
PERIOD_MAP = {
    '1min': '1m',
    '5min': '5m',
    '15min': '15m',
    '30min': '30m',
    '60min': '1h',
    'day': '1d',
    'week': '1w',
    '1w': '1w',  # 周K（RealtimeQuotes.vue 使用）
    'month': '1mon',
    '1M': '1mon',  # 月K（RealtimeQuotes.vue 使用）
}


# ─── 数据转换 ────────────────────────────────────────────────────────────────

def _df_to_unified_items(df) -> List[dict]:
    """将 KlineService 返回的 DataFrame 转换为前端统一格式"""
    import pandas as pd

    if df is None or df.empty:
        return []

    # 去重：按 datetime 去重，保留最后一条
    if 'datetime' in df.columns:
        df = df.drop_duplicates(subset=['datetime'], keep='last')

    items = []
    for _, row in df.iterrows():
        dt_val = row.get('datetime')

        # 处理各种 datetime 类型
        if isinstance(dt_val, (int, float)):
            dt_val = pd.to_datetime(dt_val, unit='ms' if dt_val > 1e11 else 's', errors='coerce')
            if pd.isna(dt_val):
                continue
        elif isinstance(dt_val, str):
            dt_val = pd.to_datetime(dt_val, errors='coerce')
            if pd.isna(dt_val):
                continue

        # 【关键】naive datetime 视为北京时间，返回 UTC 时间戳
        # 北京时间 15:00 = UTC 07:00，相差 8 小时
        if hasattr(dt_val, 'tzinfo') and dt_val.tzinfo is not None:
            # 有时区信息：直接转时间戳
            timestamp_ms = int(dt_val.timestamp() * 1000)
        else:
            # naive datetime：视为北京时间，需要转换为 UTC 时间戳
            # 北京时间 = UTC + 8h，所以 UTC = 北京时间 - 8h
            # 直接用 timestamp() 会在服务器时区下处理，不确定结果
            # 明确转换：视为北京时间，减去 8 小时
            timestamp_s = dt_val.timestamp() - 8 * 3600
            timestamp_ms = int(timestamp_s * 1000)

        vol = float(row.get('volume', 0) or 0)
        if vol == 0:
            continue

        items.append({
            'time': timestamp_ms,  # UTC 时间戳
            'open': float(row.get('open', 0)),
            'high': float(row.get('high', 0)),
            'low': float(row.get('low', 0)),
            'close': float(row.get('close', 0)),
            'volume': vol,
            'amount': float(row.get('amount', 0) or 0),
        })

    return items


# ─── 端点 ─────────────────────────────────────────────────────────────────────

@router.post("/unified", response_model=UnifiedDataResponse)
async def unified_data(request: UnifiedDataRequest):
    """统一数据入口

    前端只调用此接口，后端内部选择最优数据源。
    支持 data_type: kline, realtime_quote, financial, tick
    """
    t0 = time.perf_counter()

    if request.data_type == 'kline':
        return await _handle_kline(request, t0)
    elif request.data_type == 'realtime_quote':
        return await _handle_realtime_quote(request, t0)
    else:
        return UnifiedDataResponse(
            code=400,
            message=f"不支持的数据类型: {request.data_type}",
        )


async def _handle_kline(request: UnifiedDataRequest, t0: float) -> UnifiedDataResponse:
    """处理 K 线数据请求"""
    params = request.params or {}

    # 只取第一个 symbol（当前前端统一接口每次只请求一只股票）
    symbol = request.symbols[0] if request.symbols else None
    if not symbol:
        return UnifiedDataResponse(code=400, message="缺少 symbols 参数")

    # 周期映射
    period = params.get('period', 'day')
    api_period = PERIOD_MAP.get(period, period)

    count = params.get('count', 500)

    logger.info(f"[Unified] kline request: {symbol} period={period}→{api_period} count={count}")

    try:
        service = get_seamless_kline_service()
        df = await run_in_threadpool(
            service.get_kline,
            symbol=symbol,
            period=api_period,
            count=count,
        )

        elapsed_ms = int((time.perf_counter() - t0) * 1000)

        if df is None or df.empty:
            return UnifiedDataResponse(
                code=200,
                data=[],
                message=f"无数据: {symbol} {period}",
                metadata={
                    'source': 'none',
                    'elapsed_ms': elapsed_ms,
                    'timestamp': datetime.now().isoformat(),
                },
            )

        # 检测数据源
        source = 'unknown'
        if 'data_source' in df.columns:
            source = df['data_source'].iloc[0] if not df['data_source'].isna().all() else 'unknown'
        else:
            source = 'kline_service'

        items = _df_to_unified_items(df)

        logger.info(f"[Unified] {symbol} {period}: {len(items)} 条 from {source} in {elapsed_ms}ms")

        return UnifiedDataResponse(
            code=200,
            data=items,
            message="success",
            metadata={
                'source': source,
                'elapsed_ms': elapsed_ms,
                'timestamp': datetime.now().isoformat(),
            },
        )

    except Exception as e:
        elapsed_ms = int((time.perf_counter() - t0) * 1000)
        logger.error(f"[Unified] 获取K线失败: symbol={symbol}, error={e}")
        return UnifiedDataResponse(
            code=500,
            data=[],
            message=str(e),
            metadata={
                'source': 'error',
                'elapsed_ms': elapsed_ms,
                'timestamp': datetime.now().isoformat(),
            },
        )


async def _handle_realtime_quote(request: UnifiedDataRequest, t0: float) -> UnifiedDataResponse:
    """处理实时报价请求"""
    symbols = request.symbols
    if not symbols:
        return UnifiedDataResponse(code=400, message="缺少 symbols 参数")

    logger.info(f"[Unified] realtime_quote request: {symbols}")

    try:
        # 获取实时报价
        service = get_realtime_market_service()
        quotes, data_source = service.get_realtime_quotes(
            codes=symbols,
            use_cache=request.use_cache
        )

        # 补充从 HotDB 计算的财务指标
        for symbol in quotes:
            if data_source != 'tdxquant':
                _fill_indicators_from_hotdb(quotes[symbol], symbol)

        elapsed_ms = int((time.perf_counter() - t0) * 1000)

        return UnifiedDataResponse(
            code=200,
            data=list(quotes.values()),
            message="success",
            metadata={
                'source': data_source,
                'count': len(quotes),
                'elapsed_ms': elapsed_ms,
                'timestamp': datetime.now().isoformat(),
            },
        )

    except Exception as e:
        elapsed_ms = int((time.perf_counter() - t0) * 1000)
        logger.error(f"[Unified] 获取实时报价失败: symbols={symbols}, error={e}")
        return UnifiedDataResponse(
            code=500,
            data=[],
            message=str(e),
            metadata={
                'source': 'error',
                'elapsed_ms': elapsed_ms,
                'timestamp': datetime.now().isoformat(),
            },
        )


def _fill_indicators_from_hotdb(quote: dict, symbol: str) -> None:
    """从 HotDB 补充财务指标（换手率、量比等）

    当 TdxQuant 不可用时，从 HotDB 读取历史数据计算：
    - 换手率 = 当日成交量 / 流通股本
    - 量比 = 当日成交量 / 5日平均成交量
    """
    try:
        import pandas as pd

        adapter = get_adapter('hotdb')
        if adapter is None:
            return

        # 获取最近10天日线数据
        df = adapter.get_kline([symbol], period='1d', count=10)
        if df is None or symbol not in df or df[symbol].empty:
            return

        df_symbol = df[symbol]

        # 当日数据
        today = df_symbol.iloc[-1]
        today_volume = float(today.get('volume', 0))

        # 计算换手率（需要流通股本）
        float_shares = quote.get('float_shares', 0)
        if float_shares > 0 and today_volume > 0:
            turnover_rate = (today_volume / float_shares) * 100
            if quote.get('turnover_rate', 0) == 0:
                quote['turnover_rate'] = round(turnover_rate, 2)

        # 计算量比（当日成交量 / 5日平均成交量）
        if len(df_symbol) >= 6:
            recent_5d_avg = df_symbol.iloc[-6:-1]['volume'].mean()
            if recent_5d_avg > 0 and quote.get('volume_ratio', 0) == 0:
                volume_ratio = today_volume / recent_5d_avg
                quote['volume_ratio'] = round(volume_ratio, 2)

        logger.debug(f"[Unified] {symbol} 从 HotDB 补充指标: "
                    f"换手率={quote.get('turnover_rate', 0)}, "
                    f"量比={quote.get('volume_ratio', 0)}")

    except Exception as e:
        logger.debug(f"[Unified] {symbol} 从 HotDB 补充指标失败: {e}")

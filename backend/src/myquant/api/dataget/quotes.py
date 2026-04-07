"""
V5 K线服务 API 路由

提供实时K线、无缝K线、日内K线等服务
"""

from fastapi import APIRouter, HTTPException, Query
from fastapi.concurrency import run_in_threadpool
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from loguru import logger
import pandas as pd

from myquant.core.market.services.kline import (
    get_intraday_kline_service,
    get_seamless_kline_service,
)
from myquant.core.research.indicators import get_indicator_service
from myquant.core.market.utils.trading_time_detector import TradingTimeDetectorV2


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
    indicators: Optional[Dict[str, Any]] = Field(None, description="技术指标数据")


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


def _calculate_indicators(indicator_service, df: pd.DataFrame, indicator_list: List[str], indicator_params: Dict[str, Any] = None) -> Dict[str, Any]:
    """计算技术指标

    Args:
        indicator_service: 指标服务实例
        df: K线数据 DataFrame
        indicator_list: 要计算的指标列表
        indicator_params: 指标参数配置

    Returns:
        指标数据字典，格式与前端组件兼容
    """
    import numpy as np
    logger.info(f"[V5] _calculate_indicators 收到指标列表: {indicator_list}")

    if indicator_params is None:
        indicator_params = {}

    result = {}

    # 提取常用列
    open_price = df['open']
    high = df['high']
    low = df['low']
    close = df['close']
    volume = df['volume']

    # 转换 datetime 为字符串列表
    datetime_list = df['datetime'].dt.strftime('%Y-%m-%d %H:%M:%S').tolist()

    def clean_values(values):
        """清理数值，将 NaN 转为 None"""
        return [None if pd.isna(v) or np.isnan(v) else float(v) for v in values]

    for indicator in indicator_list:
        try:
            ind_upper = indicator.upper()
            logger.info(f"[V5] 处理指标: {ind_upper}")

            if ind_upper == 'MA':
                # 计算多条均线（使用calculate_sma，因为它接受Series）
                periods = [5, 10, 20, 30, 60]
                ma_data = {}
                for p in periods:
                    ma_values = indicator_service.calculate_sma(close, period=p).tolist()
                    ma_data[f'ma{p}'] = clean_values(ma_values)
                result['MA'] = ma_data

            elif ind_upper == 'BOLL':
                boll = indicator_service.calculate_boll(close, period=20, nbdev_up=2, nbdev_down=2)
                result['BOLL'] = {
                    'upper': clean_values(boll['upper'].tolist()),
                    'middle': clean_values(boll['middle'].tolist()),
                    'lower': clean_values(boll['lower'].tolist())
                }

            elif ind_upper == 'MACD':
                macd = indicator_service.calculate_macd(close, fast_period=12, slow_period=26, signal_period=9)
                result['MACD'] = {
                    'macd': clean_values(macd['macd'].tolist()),
                    'signal': clean_values(macd['signal'].tolist()),
                    'histogram': clean_values(macd['histogram'].tolist())
                }

            elif ind_upper == 'KDJ':
                kdj = indicator_service.calculate_kdj(high, low, close, fastk_period=9, slowk_period=3, slowd_period=3)
                result['KDJ'] = {
                    'k': clean_values(kdj['k'].tolist()),
                    'd': clean_values(kdj['d'].tolist()),
                    'j': clean_values(kdj['j'].tolist())
                }

            elif ind_upper == 'SKDJ':
                # SKDJ（慢速随机指标）- 通达信公式：只有SK和SD，没有SJ
                logger.info(f"[V5] 开始计算 SKDJ 指标")
                # 获取SKDJ参数
                skdj_params = indicator_params.get('SKDJ', {}) if isinstance(indicator_params, dict) else {}
                fastk_period = int(skdj_params.get('fastk_period', 9) or 9)
                slowk_period = int(skdj_params.get('slowk_period', 3) or 3)
                slowd_period = int(skdj_params.get('slowd_period', 3) or 3)
                smooth_period = int(skdj_params.get('smooth_period', 3) or 3)
                logger.info(f"[V5] SKDJ参数: fastk={fastk_period}, slowk={slowk_period}, slowd={slowd_period}")

                skdj = indicator_service.calculate_skdj(high, low, close,
                                                           fastk_period=fastk_period,
                                                           slowk_period=slowk_period,
                                                           slowd_period=slowd_period,
                                                           smooth_period=smooth_period)
                result['SKDJ'] = {
                    'sk': clean_values(skdj['sk'].tolist()),
                    'sd': clean_values(skdj['sd'].tolist())
                }
                logger.info(f"[V5] SKDJ 指标计算完成，数据点数: {len(skdj['sk'])}")

            elif ind_upper == 'RSI':
                rsi = indicator_service.calculate_rsi(close, period=14)
                result['RSI'] = {
                    'rsi': clean_values(rsi.tolist())
                }

            elif ind_upper == 'CCI':
                cci = indicator_service.calculate_cci(high, low, close, period=14)
                result['CCI'] = {
                    'cci': clean_values(cci.tolist())
                }

            elif ind_upper == 'OBV':
                obv = indicator_service.calculate_obv(close, volume)
                # 计算 MAOBV（OBV 的移动平均）
                maobv_period = indicator_params.get('maobv_period', 20)
                maobv = obv.rolling(window=maobv_period).mean()
                result['OBV'] = {
                    'obv': clean_values(obv.tolist()),
                    'maobv': clean_values(maobv.tolist()),
                    'volume': clean_values(volume.tolist())
                }

            elif ind_upper == 'OBV':
                obv = indicator_service.calculate_obv(close, volume)
                # 计算 MAOBV（OBV 的移动平均）
                maobv_period = indicator_params.get('maobv_period', 20) if isinstance(indicator_params, dict) else 20
                maobv = obv.rolling(window=maobv_period).mean()
                result['OBV'] = {
                    'obv': clean_values(obv.tolist()),
                    'maobv': clean_values(maobv.tolist()),
                    'volume': clean_values(volume.tolist())
                }

            elif ind_upper == 'BIAS':
                # BIAS（乖离率）
                bias_period = indicator_params.get('period', 6)
                bias = indicator_service.calculate_bias(close, period=bias_period)
                result['BIAS'] = {
                    'bias': clean_values(bias.tolist())
                }

            elif ind_upper == 'SMC':
                # SMC (Smart Money Concepts) 指标
                logger.info(f"[SMC] 开始计算, df 长度: {len(df)}")
                try:
                    from myquant.core.research.smc_service import get_smc_service
                    smc_service = get_smc_service()

                    # 从 indicator_params 获取 SMC 参数
                    smc_params = indicator_params.get('SMC', {}) if isinstance(indicator_params, dict) else {}
                    swing_length = int(smc_params.get('swing_length', 5) or 5)
                    close_break = smc_params.get('close_break', True)
                    show_ob = smc_params.get('show_ob', True)
                    show_fvg = smc_params.get('show_fvg', True)
                    logger.info(f"[SMC] swing_length value: {swing_length}, type: {type(swing_length)}")

                    # 参考线参数（最近N根K线的最高/最低）
                    reference_period = int(smc_params.get('reference_period', 34) or 34)
                    logger.info(f"[SMC] reference_period value: {reference_period}, type: {type(reference_period)}")

                    logger.info(f"[SMC] 接收到的参数: {smc_params}, type={type(smc_params)}")
                    logger.info(f"[SMC] 参数: swing_length={swing_length}, close_break={close_break}, reference_period={reference_period}")

                    smc_result = smc_service.calculate_all(
                        df,
                        swing_length=swing_length,
                        close_break=close_break,
                        show_ob=show_ob,
                        show_fvg=show_fvg
                    )

                    # 计算最近 N 根 K 线的最高/最低点（用于参考线）
                    if smc_result and reference_period > 0:
                        recent_n = min(reference_period, len(df))
                        recent_df = df.tail(recent_n).reset_index(drop=True)
                        highest_high = recent_df['high'].max()
                        lowest_low = recent_df['low'].min()
                        # 获取在 recent_df 中的位置，然后计算在原始 df 中的索引
                        highest_pos = recent_df['high'].idxmax()
                        lowest_pos = recent_df['low'].idxmin()
                        # 计算在原始 df 中的索引（df.tail(recent_n) 的起始索引是 len(df) - recent_n）
                        start_idx = len(df) - recent_n
                        highest_idx = start_idx + highest_pos
                        lowest_idx = start_idx + lowest_pos

                        smc_result['reference_high'] = float(highest_high)
                        smc_result['reference_low'] = float(lowest_low)
                        smc_result['reference_high_index'] = int(highest_idx)
                        smc_result['reference_low_index'] = int(lowest_idx)
                        smc_result['reference_period'] = reference_period
                        logger.info(f"[SMC] 参考线已添加: high={highest_high:.2f}@{highest_idx}, low={lowest_low:.2f}@{lowest_idx}")
                        logger.info(f"[SMC] smc_result keys: {list(smc_result.keys())}")
                    logger.info(f"[SMC] calculate_all 返回: {smc_result is not None}")

                    if smc_result:
                        # 为 SMC 添加秒级时间戳（与 K 线时间保持一致的时区处理）
                        # naive datetime 视为北京时间，转换为 UTC 秒级时间戳
                        timestamps = []
                        for t in df['datetime']:
                            ts = pd.Timestamp(t)
                            if ts.tz is None:
                                ts = ts.tz_localize('Asia/Shanghai')
                            timestamps.append(int(ts.timestamp()))
                        logger.info(f"[SMC] timestamps 前3个: {timestamps[:3]}")
                        smc_result['timestamps'] = timestamps
                        result['SMC'] = smc_result
                        logger.info(f"[SMC] 成功添加到结果，keys: {list(smc_result.keys())}")
                        logger.info(f"[SMC] 参考线最终数据: high={smc_result.get('reference_high')}, low={smc_result.get('reference_low')}")
                except Exception as e:
                    logger.error(f"[SMC] 计算失败: {e}", exc_info=True)

            elif ind_upper == 'TOPBOTTOM':
                # 顶底背离指标
                logger.info(f"[V5] 开始计算 TOPBOTTOM 指标")
                topbottom_params = indicator_params.get('TOPBOTTOM', {}) if isinstance(indicator_params, dict) else {}
                fastk_period = int(topbottom_params.get('fastk_period', 9) or 9)
                slowk_period = int(topbottom_params.get('slowk_period', 3) or 3)
                slowd_period = int(topbottom_params.get('slowd_period', 3) or 3)
                rsi_period = int(topbottom_params.get('rsi_period', 14) or 14)
                macd_fast = int(topbottom_params.get('macd_fast', 12) or 12)
                macd_slow = int(topbottom_params.get('macd_slow', 26) or 26)
                macd_signal = int(topbottom_params.get('macd_signal', 9) or 9)

                topbottom_signals = indicator_service.calculate_top_bottom_signals(
                    high, low, close,
                    fastk_period=fastk_period,
                    slowk_period=slowk_period,
                    slowd_period=slowd_period,
                    rsi_period=rsi_period,
                    macd_fast=macd_fast,
                    macd_slow=macd_slow,
                    macd_signal=macd_signal
                )

                result['TOPBOTTOM'] = {
                    'risk_value_34': clean_values(topbottom_signals['risk_value_34'].tolist()),
                    'risk_value_170': clean_values(topbottom_signals['risk_value_170'].tolist()),
                    'risk_value_1020': clean_values(topbottom_signals['risk_value_1020'].tolist()),
                    'buy_signal': clean_values(topbottom_signals['buy_signal'].tolist()),
                    'sell_signal': clean_values(topbottom_signals['sell_signal'].tolist()),
                    'macd_div_top': clean_values(topbottom_signals['macd_div_top'].tolist()),
                    'macd_div_bottom': clean_values(topbottom_signals['macd_div_bottom'].tolist()),
                    'kdj_div_top': clean_values(topbottom_signals['kdj_div_top'].tolist()),
                    'kdj_div_bottom': clean_values(topbottom_signals['kdj_div_bottom'].tolist()),
                    'rsi_div_top': clean_values(topbottom_signals['rsi_div_top'].tolist()),
                    'rsi_div_bottom': clean_values(topbottom_signals['rsi_div_bottom'].tolist())
                }
                logger.info(f"[V5] TOPBOTTOM 指标计算完成")

            # 为每个指标添加 datetime
            if ind_upper in result:
                result[ind_upper]['datetime'] = datetime_list

        except Exception as e:
            logger.warning(f"计算指标 {indicator} 失败: {e}")
            continue

    return result


# ─── 端点 ─────────────────────────────────────────────────────────────────────

@router.get("/realtime/{symbol}", response_model=KlineDataResponse)
async def get_realtime_kline(
    symbol: str,
    period: str = Query("1d", description="周期: 1m, 5m, 15m, 30m, 1h, 1d"),
    count: int = Query(100, description="返回数量", ge=1, le=1000),
    adjust_type: str = Query("none", description="复权类型: none/qfq/hfq/qfq_ratio/hfq_ratio"),
    indicators: Optional[str] = Query(None, description="技术指标: macd,kdj,rsi,boll,cci,obv (逗号分隔)"),
    indicator_params: Optional[str] = Query(None, description="技术指标参数配置（JSON字符串）"),
    after_time: Optional[int] = Query(None, description="增量模式：只返回此时间戳（毫秒）之后的数据")
):
    """获取单只股票K线（历史+实时无缝）

    前端主要使用此接口，返回扁平格式（与 v1/quotes/kline 格式兼容）。
    支持可选的技术指标参数，一次返回K线和指标数据。
    支持增量模式（after_time）：
    - 盘中（交易中）：返回 after_time 之后的新数据
    - 盘后（休市）：返回全量数据（数据不再变化）
    """
    try:
        # 判断是否为交易时间（盘中 vs 盘后）
        detector = TradingTimeDetectorV2()
        is_trading = detector.is_trading_time()

        service = get_seamless_kline_service()
        df = await run_in_threadpool(
            service.get_kline,
            symbol=symbol,
            period=period,
            count=count,
            include_realtime=True,
            adjust_type=_map_adjust_type(adjust_type)
        )

        if df is None or df.empty:
            raise HTTPException(status_code=503, detail=f"无法获取 {symbol} 的K线数据")

        # 增量模式：只返回 after_time 之后的数据（盘后也生效）
        if after_time is not None and not df.empty:
            # after_time 是毫秒时间戳，转换为 pandas Timestamp 进行比较
            after_ts = pd.Timestamp(after_time, unit='ms')
            # 确保 datetime 列是 Timestamp 类型
            if 'datetime' in df.columns:
                df['datetime'] = pd.to_datetime(df['datetime'])
                df = df[df['datetime'] > after_ts]
                logger.info(f"[V5] 增量过滤: after_time={after_ts}, 剩余 {len(df)} 条")

        items = _df_to_kline_items(df)
        logger.info(f"[V5] {symbol} {period}: {len(items)} 条, 交易中={is_trading}, 增量={after_time is not None}")

        # 计算技术指标（如果请求）
        indicators_data = None
        logger.info(f"[V5] 指标请求检查: indicators={indicators}, indicator_params type={type(indicator_params)}")
        if indicators:
            try:
                indicator_list = [ind.strip().upper() for ind in indicators.split(',') if ind.strip()]
                if indicator_list:
                    # 解析指标参数
                    indicator_params_dict = {}
                    if indicator_params:
                        try:
                            import json
                            indicator_params_dict = json.loads(indicator_params)
                            logger.info(f"[V5] 指标参数: {indicator_params_dict}")
                        except Exception as e:
                            logger.warning(f"[V5] 解析指标参数失败: {e}")

                    indicator_service = get_indicator_service()
                    indicators_data = await run_in_threadpool(
                        _calculate_indicators,
                        indicator_service,
                        df,
                        indicator_list,
                        indicator_params_dict
                    )
                    logger.info(f"[V5] {symbol} 计算指标: {indicator_list}")
            except Exception as e:
                logger.warning(f"[V5] 计算指标失败: {e}，只返回K线数据")

        return KlineDataResponse(
            symbol=symbol,
            period=period,
            data=items,
            data_source='seamless',
            count=len(items),
            adjust_type=adjust_type,
            indicators=indicators_data
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[V5] 获取K线失败: symbol={symbol}, error={e}")
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
# Trigger reload

# -*- coding: utf-8 -*-
"""
技术指标 API
============
提供基于 TA-Lib 的技术指标计算接口

支持的指标：
- MACD: 指数平滑异同移动平均线
- KDJ: 随机指标
- RSI: 相对强弱指标
- BOLL: 布林带
- CCI: 顺势指标
- OBV: 能量潮
- ATR: 真实波幅
"""

from typing import List, Dict, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from loguru import logger
import pandas as pd

from ...core.research.indicator_service import get_indicator_service, IndicatorType
from ...core.market.services.seamless_service import get_seamless_kline_service

router = APIRouter(prefix="/indicators", tags=["技术指标"])


class IndicatorRequest(BaseModel):
    """指标计算请求"""
    symbol: str
    period: str = "1d"  # 1m, 5m, 15m, 30m, 1h, 1d, 1w, 1M
    indicators: List[str] = ["macd"]  # 要计算的指标列表
    count: int = 200  # K线数量


class IndicatorResponse(BaseModel):
    """指标计算响应"""
    code: int
    message: str
    data: Dict[str, List[float]]  # 指标数据 {指标名: [值列表]}
    timestamps: List[int]  # 时间戳列表


# 附图指标配置（用于前端显示）
SUB_CHART_INDICATORS = {
    "macd": {
        "name": "MACD",
        "type": "oscillator",
        "description": "指数平滑异同移动平均线",
        "lines": ["macd", "signal", "histogram"],
        "colors": {"macd": "#2196F3", "signal": "#FF9800", "histogram": "#26a69a"},
        "zero_line": True
    },
    "kdj": {
        "name": "KDJ",
        "type": "oscillator",
        "description": "随机指标",
        "lines": ["k", "d", "j"],
        "colors": {"k": "#2196F3", "d": "#FF9800", "j": "#9C27B0"},
        "range": [0, 100],
        "overbought": 80,
        "oversold": 20
    },
    "rsi": {
        "name": "RSI",
        "type": "oscillator",
        "description": "相对强弱指标",
        "lines": ["rsi"],
        "colors": {"rsi": "#2196F3"},
        "range": [0, 100],
        "overbought": 70,
        "oversold": 30
    },
    "cci": {
        "name": "CCI",
        "type": "oscillator",
        "description": "顺势指标",
        "lines": ["cci"],
        "colors": {"cci": "#2196F3"},
        "range": [-300, 300],
        "overbought": 100,
        "oversold": -100
    },
    "obv": {
        "name": "OBV",
        "type": "volume",
        "description": "能量潮",
        "lines": ["obv"],
        "colors": {"obv": "#2196F3"}
    },
    "atr": {
        "name": "ATR",
        "type": "volatility",
        "description": "真实波幅",
        "lines": ["atr"],
        "colors": {"atr": "#2196F3"}
    },
    "boll": {
        "name": "BOLL",
        "type": "overlay",
        "description": "布林带",
        "lines": ["upper", "middle", "lower"],
        "colors": {"upper": "#FF9800", "middle": "#2196F3", "lower": "#FF9800"}
    }
}


@router.post("/calculate", response_model=IndicatorResponse)
async def calculate_indicators(request: IndicatorRequest):
    """
    计算技术指标

    Args:
        request: 指标计算请求

    Returns:
        指标数据
    """
    try:
        # 获取 K 线数据（使用与 K 线 API 相同的数据源，确保时间戳一致）
        svc = get_seamless_kline_service()
        df = svc.get_kline(
            symbol=request.symbol,
            period=request.period,
            count=request.count,
            include_realtime=True,
            adjust_type='qfq'  # 默认前复权
        )

        if df is None or len(df) < 30:
            return IndicatorResponse(
                code=400,
                message="K线数据不足，无法计算指标",
                data={},
                timestamps=[]
            )

        # 【关键】与 K 线 API 保持一致：过滤成交量为 0 的数据
        # 这样可以避免指标数据包含 K 线中没有的时间点
        if 'volume' in df.columns:
            df = df[df['volume'] > 0]
        if len(df) < 30:
            return IndicatorResponse(
                code=400,
                message="K线数据不足（过滤后），无法计算指标",
                data={},
                timestamps=[]
            )

        # 计算指标
        indicator_service = get_indicator_service()
        result_data = {}

        for indicator_name in request.indicators:
            indicator_name = indicator_name.lower()

            if indicator_name == "macd":
                macd_result = indicator_service.calculate_macd(df['close'])
                result_data.update(macd_result)

            elif indicator_name == "kdj":
                kdj_result = indicator_service.calculate_kdj(
                    df['high'], df['low'], df['close']
                )
                result_data.update(kdj_result)

            elif indicator_name == "rsi":
                result_data['rsi'] = indicator_service.calculate_rsi(df['close'])

            elif indicator_name == "cci":
                if indicator_service.available:
                    import talib
                    cci = talib.CCI(df['high'], df['low'], df['close'], timeperiod=14)
                    result_data['cci'] = pd.Series(cci, index=df.index)
                else:
                    # 简化实现
                    tp = (df['high'] + df['low'] + df['close']) / 3
                    sma_tp = tp.rolling(window=14).mean()
                    mean_dev = tp.rolling(window=14).apply(lambda x: abs(x - x.mean()).mean())
                    result_data['cci'] = (tp - sma_tp) / (0.015 * mean_dev)

            elif indicator_name == "obv":
                if indicator_service.available:
                    import talib
                    obv = talib.OBV(df['close'], df['volume'])
                    result_data['obv'] = pd.Series(obv, index=df.index)
                else:
                    # 简化实现
                    obv = [0]
                    for i in range(1, len(df)):
                        if df['close'].iloc[i] > df['close'].iloc[i-1]:
                            obv.append(obv[-1] + df['volume'].iloc[i])
                        elif df['close'].iloc[i] < df['close'].iloc[i-1]:
                            obv.append(obv[-1] - df['volume'].iloc[i])
                        else:
                            obv.append(obv[-1])
                    result_data['obv'] = pd.Series(obv, index=df.index)

            elif indicator_name == "atr":
                result_data['atr'] = indicator_service.calculate_atr(
                    df['high'], df['low'], df['close']
                )

            elif indicator_name == "boll":
                boll_result = indicator_service.calculate_boll(df['close'])
                result_data.update(boll_result)

        # 转换为列表格式
        response_data = {}
        for key, series in result_data.items():
            if isinstance(series, pd.Series):
                response_data[key] = series.fillna(0).tolist()
            else:
                response_data[key] = list(series) if hasattr(series, '__iter__') else [series]

        # 时间戳（datetime 列转毫秒）
        if 'datetime' in df.columns:
            # 将 datetime 转换为毫秒时间戳
            timestamps = pd.to_datetime(df['datetime']).astype('int64') // 10**3
            timestamps = timestamps.tolist()
        elif 'time' in df.columns:
            timestamps = df['time'].tolist()
        else:
            timestamps = list(range(len(df)))

        return IndicatorResponse(
            code=200,
            message="指标计算成功",
            data=response_data,
            timestamps=timestamps
        )

    except Exception as e:
        logger.error(f"指标计算失败: {e}")
        return IndicatorResponse(
            code=500,
            message=f"指标计算失败: {str(e)}",
            data={},
            timestamps=[]
        )


@router.get("/list")
async def get_indicator_list():
    """
    获取支持的指标列表

    Returns:
        指标配置列表
    """
    return {
        "code": 200,
        "message": "success",
        "data": SUB_CHART_INDICATORS
    }


@router.get("/supported")
async def get_supported_indicators():
    """
    获取系统支持的指标列表（详细）

    Returns:
        详细指标列表
    """
    indicator_service = get_indicator_service()
    return {
        "code": 200,
        "message": "success",
        "data": indicator_service.get_supported_indicators(),
        "talib_available": indicator_service.available
    }

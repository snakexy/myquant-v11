# -*- coding: utf-8 -*-
"""
技术指标 API 路由

提供技术指标计算接口：
- 计算单个或多个指标
- 支持自定义参数
- 返回带指标的K线数据
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from loguru import logger
import pandas as pd

from myquant.core.market.services.kline_service import get_kline_service
from myquant.core.research.indicator_service import get_indicator_service


router = APIRouter(prefix="/indicators", tags=["技术指标"])


# ─── 请求模型 ────────────────────────────────────────────────────────────

class IndicatorRequest(BaseModel):
    """指标计算请求"""
    symbol: str = Field(..., description="股票代码")
    period: str = Field(default="1d", description="K线周期")
    count: int = Field(default=500, description="数据条数", ge=10, le=2000)
    indicators: List[str] = Field(
        default=["ma5", "ma10", "ma20", "ma60", "macd", "kdj", "rsi", "boll", "cci", "obv"],
        description="要计算的指标列表"
    )


class IndicatorParamsRequest(BaseModel):
    """带参数的指标计算请求"""
    symbol: str = Field(..., description="股票代码")
    period: str = Field(default="1d", description="K线周期")
    count: int = Field(default=500, description="数据条数", ge=10, le=2000)
    indicators: Dict[str, Dict[str, Any]] = Field(
        default={},
        description="指标及其参数，如 {'macd': {'fast_period': 12, 'slow_period': 26}}"
    )


# ─── API 端点 ─────────────────────────────────────────────────────────────

@router.post("/calculate")
async def calculate_indicators(request: IndicatorRequest) -> Dict[str, Any]:
    """计算技术指标（使用默认参数）

    Args:
        request: 指标计算请求

    Returns:
        {
            'symbol': '600519.SH',
            'period': '1d',
            'kline': {...},
            'indicators': {
                'ma5': [...],
                'ma10': [...],
                'macd': {...},
                ...
            }
        }
    """
    try:
        kline_service = get_kline_service()
        indicator_service = get_indicator_service()

        # 1. 获取K线数据
        df = kline_service.get_historical_kline(
            symbol=request.symbol,
            period=request.period,
            count=request.count
        )

        if df is None or df.empty:
            raise HTTPException(status_code=404, detail="无法获取K线数据")

        # 2. 计算指标
        indicator_data = indicator_service.calculate_all_indicators(df, request.indicators)

        # 3. 格式化K线数据
        kline_data = {
            'datetime': df.index.strftime('%Y-%m-%d %H:%M:%S').tolist(),
            'open': df['open'].tolist(),
            'high': df['high'].tolist(),
            'low': df['low'].tolist(),
            'close': df['close'].tolist(),
            'volume': df['volume'].tolist(),
            'amount': df['amount'].tolist() if 'amount' in df.columns else []
        }

        # 4. 格式化指标数据
        formatted_indicators = {}
        for name, data in indicator_data.items():
            if isinstance(data, pd.Series):
                formatted_indicators[name] = data.tolist()
            elif isinstance(data, dict):
                formatted_indicators[name] = {
                    k: v.tolist() if isinstance(v, pd.Series) else v
                    for k, v in data.items()
                }

        return {
            'symbol': request.symbol,
            'period': request.period,
            'count': len(df),
            'kline': kline_data,
            'indicators': formatted_indicators
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Indicators API] 计算失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/calculate_with_params")
async def calculate_indicators_with_params(request: IndicatorParamsRequest) -> Dict[str, Any]:
    """计算技术指标（使用自定义参数）

    Args:
        request: 带参数的指标计算请求

    Returns:
        同 calculate_indicators
    """
    try:
        kline_service = get_kline_service()
        indicator_service = get_indicator_service()

        # 1. 获取K线数据
        df = kline_service.get_historical_kline(
            symbol=request.symbol,
            period=request.period,
            count=request.count
        )

        if df is None or df.empty:
            raise HTTPException(status_code=404, detail="无法获取K线数据")

        # 2. 根据指标类型计算（支持自定义参数）
        formatted_indicators = {}

        for indicator_name, params in request.indicators.items():
            indicator_name = indicator_name.lower()

            # MA系列
            if indicator_name.startswith('ma'):
                period = params.get('period', int(indicator_name[2:]))
                result = indicator_service.calculate_sma(df['close'], period)
                formatted_indicators[indicator_name] = result.tolist()

            # MACD
            elif indicator_name == 'macd':
                fast = params.get('fast_period', 12)
                slow = params.get('slow_period', 26)
                signal = params.get('signal_period', 9)
                result = indicator_service.calculate_macd(df['close'], fast, slow, signal)
                formatted_indicators['macd'] = {
                    'macd': result['macd'].tolist(),
                    'signal': result['signal'].tolist(),
                    'histogram': result['histogram'].tolist()
                }

            # KDJ
            elif indicator_name == 'kdj':
                fastk = params.get('fastk_period', 9)
                slowk = params.get('slowk_period', 3)
                slowd = params.get('slowd_period', 3)
                result = indicator_service.calculate_kdj(df['high'], df['low'], df['close'], fastk, slowk, slowd)
                formatted_indicators['kdj'] = {
                    'k': result['k'].tolist(),
                    'd': result['d'].tolist(),
                    'j': result['j'].tolist()
                }

            # BOLL
            elif indicator_name == 'boll':
                period = params.get('period', 20)
                nbdev_up = params.get('nbdev_up', 2.0)
                nbdev_down = params.get('nbdev_down', 2.0)
                result = indicator_service.calculate_boll(df['close'], period, nbdev_up, nbdev_down)
                formatted_indicators['boll'] = {
                    'upper': result['upper'].tolist(),
                    'middle': result['middle'].tolist(),
                    'lower': result['lower'].tolist()
                }

            # RSI
            elif indicator_name == 'rsi':
                period = params.get('period', 14)
                result = indicator_service.calculate_rsi(df['close'], period)
                formatted_indicators['rsi'] = result.tolist()

            # CCI
            elif indicator_name == 'cci':
                period = params.get('period', 14)
                result = indicator_service.calculate_cci(df['high'], df['low'], df['close'], period)
                formatted_indicators['cci'] = result.tolist()

            # OBV
            elif indicator_name == 'obv':
                result = indicator_service.calculate_obv(df['close'], df['volume'])
                formatted_indicators['obv'] = result.tolist()

            else:
                logger.warning(f"[Indicators API] 未知指标: {indicator_name}")

        # 3. 格式化K线数据
        kline_data = {
            'datetime': df.index.strftime('%Y-%m-%d %H:%M:%S').tolist(),
            'open': df['open'].tolist(),
            'high': df['high'].tolist(),
            'low': df['low'].tolist(),
            'close': df['close'].tolist(),
            'volume': df['volume'].tolist(),
            'amount': df['amount'].tolist() if 'amount' in df.columns else []
        }

        return {
            'symbol': request.symbol,
            'period': request.period,
            'count': len(df),
            'kline': kline_data,
            'indicators': formatted_indicators
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Indicators API] 计算失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list")
async def list_indicators() -> Dict[str, Any]:
    """获取支持的指标列表

    Returns:
        {
            'overlay': [...],
            'oscillator': [...],
            ...
        }
    """
    try:
        indicator_service = get_indicator_service()
        return indicator_service.get_supported_indicators()

    except Exception as e:
        logger.error(f"[Indicators API] 获取指标列表失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/info/{indicator_name}")
async def get_indicator_info(indicator_name: str) -> Dict[str, Any]:
    """获取单个指标信息

    Args:
        indicator_name: 指标名称

    Returns:
        指标详细信息
    """
    try:
        indicator_service = get_indicator_service()
        all_indicators = indicator_service.get_supported_indicators()

        # 搜索指标
        for category, indicators in all_indicators.items():
            for ind in indicators:
                if ind['name'].lower() == indicator_name.lower():
                    return {
                        'category': category,
                        **ind
                    }

        raise HTTPException(status_code=404, detail=f"未找到指标: {indicator_name}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Indicators API] 获取指标信息失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

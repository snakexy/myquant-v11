# -*- coding: utf-8 -*-
"""
趋势类技术指标
包含：MA（移动平均线）、MACD、BOLL（布林带）
"""
from typing import Dict, List
import pandas as pd
from loguru import logger

from .base import BaseIndicator, TALIB_AVAILABLE

# 导入 talib（如果可用）
if TALIB_AVAILABLE:
    import talib


class TrendIndicators(BaseIndicator):
    """趋势类指标计算器"""

    def __init__(self):
        super().__init__()
        logger.info("✅ 趋势指标模块初始化完成")

    # ==================== 移动平均线 ====================

    def calculate_sma(
        self,
        data: pd.Series,
        period: int = 20
    ) -> pd.Series:
        """
        计算简单移动平均线（SMA）

        Args:
            data: 价格序列
            period: 周期

        Returns:
            SMA值序列
        """
        if not self.available:
            return data.rolling(window=period).mean()

        return talib.SMA(data, timeperiod=period)

    def calculate_ema(
        self,
        data: pd.Series,
        period: int = 20
    ) -> pd.Series:
        """
        计算指数移动平均线（EMA）

        Args:
            data: 价格序列
            period: 周期

        Returns:
            EMA值序列
        """
        if not self.available:
            return data.ewm(span=period, adjust=False).mean()

        return talib.EMA(data, timeperiod=period)

    def calculate_ma(
        self,
        df: pd.DataFrame,
        periods: List[int] = [5, 10, 20, 30, 60],
        price_column: str = 'close'
    ) -> Dict[str, pd.Series]:
        """
        批量计算移动平均线

        Args:
            df: K线数据DataFrame
            periods: 周期列表
            price_column: 价格列名

        Returns:
            {MA周期: MA值序列}
        """
        if price_column not in df.columns:
            logger.error(f"数据中没有列: {price_column}")
            return {}

        prices = df[price_column]
        result = {}

        for period in periods:
            ma_key = f'ma{period}'
            result[ma_key] = self.calculate_sma(prices, period)

        return result

    # ==================== MACD指标 ====================

    def calculate_macd(
        self,
        data: pd.Series,
        fast_period: int = 12,
        slow_period: int = 26,
        signal_period: int = 9
    ) -> Dict[str, pd.Series]:
        """
        计算MACD指标

        Args:
            data: 价格序列
            fast_period: 快线周期
            slow_period: 慢线周期
            signal_period: 信号线周期

        Returns:
            {
                'macd': MACD线,
                'signal': 信号线,
                'histogram': 柱状图
            }
        """
        if not self.available:
            # 简化实现
            ema_fast = self.calculate_ema(data, fast_period)
            ema_slow = self.calculate_ema(data, slow_period)
            macd = ema_fast - ema_slow
            signal = self.calculate_ema(macd, signal_period)
            histogram = macd - signal
            return {'macd': macd, 'signal': signal, 'histogram': histogram}

        macd, signal, hist = talib.MACD(
            data,
            fastperiod=fast_period,
            slowperiod=slow_period,
            signalperiod=signal_period
        )

        return {
            'macd': pd.Series(macd, index=data.index),
            'signal': pd.Series(signal, index=data.index),
            'histogram': pd.Series(hist, index=data.index)
        }

    # ==================== BOLL布林带 ====================

    def calculate_boll(
        self,
        data: pd.Series,
        period: int = 20,
        nbdev_up: float = 2.0,
        nbdev_down: float = 2.0
    ) -> Dict[str, pd.Series]:
        """
        计算布林带（BOLL）

        Args:
            data: 价格序列
            period: 周期
            nbdev_up: 上轨标准差倍数
            nbdev_down: 下轨标准差倍数

        Returns:
            {
                'upper': 上轨,
                'middle': 中轨,
                'lower': 下轨
            }
        """
        if not self.available:
            # 简化实现
            middle = data.rolling(window=period).mean()
            std = data.rolling(window=period).std()
            upper = middle + nbdev_up * std
            lower = middle - nbdev_down * std
            return {'upper': upper, 'middle': middle, 'lower': lower}

        upper, middle, lower = talib.BBANDS(
            data,
            timeperiod=period,
            nbdevup=nbdev_up,
            nbdevdn=nbdev_down,
            matype=0  # SMA
        )

        return {
            'upper': pd.Series(upper, index=data.index),
            'middle': pd.Series(middle, index=data.index),
            'lower': pd.Series(lower, index=data.index)
        }

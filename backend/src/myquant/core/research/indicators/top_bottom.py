# -*- coding: utf-8 -*-
"""
顶底背离指标（优化版）

基于用户的通达信公式转换而来，核心功能：
1. 风险值指标（类似RSI的多周期版本）
2. MACD/KDJ/RSI 三重背离检测
3. 买卖信号点
"""

from typing import Dict, Optional
import pandas as pd
import numpy as np
from loguru import logger

from .base import BaseIndicator, TALIB_AVAILABLE

# 导入 talib（如果可用）
if TALIB_AVAILABLE:
    import talib


class TopBottomIndicator(BaseIndicator):
    """顶底背离指标"""

    def __init__(self):
        super().__init__()
        logger.info("✅ 顶底背离指标模块初始化完成")

    def calculate_risk_value(
        self,
        high: pd.Series,
        low: pd.Series,
        close: pd.Series,
        period: int = 34,
        ema_period: int = 3
    ) -> pd.Series:
        """
        计算风险值（类似RSI的变体）

        通达信公式：EMA(100*(C-LLV(LOW,N))/(HHV(H,N)-LLV(LOW,N)),M)

        Args:
            high: 最高价序列
            low: 最低价序列
            close: 收盘价序列
            period: 周期N（默认34）
            ema_period: EMA平滑周期M（默认3）

        Returns:
            风险值序列（0-100）
        """
        # 计算N日内最高价和最低价
        highest_high = high.rolling(window=period).max()
        lowest_low = low.rolling(window=period).min()

        # 风险值 = (收盘价 - 最低价) / (最高价 - 最低价) * 100
        risk_raw = (close - lowest_low) / (highest_high - lowest_low) * 100

        if self.available:
            # 使用 talib 计算 EMA
            risk_values = talib.EMA(risk_raw.values, timeperiod=ema_period)
        else:
            # 简化实现
            risk_values = risk_raw.ewm(alpha=1/ema_period, adjust=False).mean()

        return pd.Series(risk_values, index=close.index)

    def detect_divergence(
        self,
        price: pd.Series,
        indicator: pd.Series,
        lookback: int = 20
    ) -> Dict[str, pd.Series]:
        """
        检测背离信号

        顶背离：价格创新高，指标未创新高
        底背离：价格创新低，指标未创新低

        Args:
            price: 价格序列
            indicator: 指标序列
            lookback: 回溯周期

        Returns:
            {
                'top_divergence': 顶背离信号序列（1=有顶背离）
                'bottom_divergence': 底背离信号序列（1=有底背离）
            }
        """
        top_div = pd.Series(0, index=price.index)
        bottom_div = pd.Series(0, index=price.index)

        if len(price) < lookback * 2:
            return {'top_divergence': top_div, 'bottom_divergence': bottom_div}

        for i in range(lookback, len(price)):
            # 查找最近的价格峰值和指标峰值
            price_window = price.iloc[i-lookback:i+1]
            indicator_window = indicator.iloc[i-lookback:i+1]

            # 找到价格最高点的位置
            price_peak_idx = price_window.idxmax()
            # 找到指标最高点的位置
            indicator_peak_idx = indicator_window.idxmax()

            # 顶背离：价格创新高但指标未创新高，且当前在下跌
            if (price_peak_idx == price.index[i] and
                indicator_peak_idx != price.index[i] and
                price.iloc[i] < price.iloc[i-1]):
                top_div.iloc[i] = 1

            # 找到价格最低点的位置
            price_trough_idx = price_window.idxmin()
            # 找到指标最低点的位置
            indicator_trough_idx = indicator_window.idxmin()

            # 底背离：价格创新低但指标未创新低，且当前在上涨
            if (price_trough_idx == price.index[i] and
                indicator_trough_idx != price.index[i] and
                price.iloc[i] > price.iloc[i-1]):
                bottom_div.iloc[i] = 1

        return {
            'top_divergence': top_div,
            'bottom_divergence': bottom_div
        }

    def calculate_signals(
        self,
        high: pd.Series,
        low: pd.Series,
        close: pd.Series,
        fastk_period: int = 9,
        slowk_period: int = 3,
        slowd_period: int = 3,
        rsi_period: int = 14,
        macd_fast: int = 12,
        macd_slow: int = 26,
        macd_signal: int = 9
    ) -> Dict[str, pd.Series]:
        """
        计算顶底信号（综合版）

        包含：
        - 风险值（34/170/1020三个周期）
        - MACD/KDJ/RSI用于背离检测
        - 综合买卖信号

        Returns:
            {
                'risk_value_34': 风险值34
                'risk_value_170': 风险值170
                'risk_value_1020': 风险值1020
                'macd_div_top': MACD顶背离
                'macd_div_bottom': MACD底背离
                'kdj_div_top': KDJ顶背离
                'kdj_div_bottom': KDJ底背离
                'rsi_div_top': RSI顶背离
                'rsi_div_bottom': RSI底背离
                'buy_signal': 买入信号
                'sell_signal': 卖出信号
            }
        """
        # 计算风险值
        risk_34 = self.calculate_risk_value(high, low, close, period=34, ema_period=3)
        risk_170 = self.calculate_risk_value(high, low, close, period=34*5, ema_period=6)
        risk_1020 = self.calculate_risk_value(high, low, close, period=34*30, ema_period=15)

        # 计算MACD
        if self.available:
            macd, macd_signal, macd_hist = talib.MACD(
                close.values,
                fastperiod=macd_fast,
                slowperiod=macd_slow,
                signalperiod=macd_signal
            )
            macd_line = pd.Series(macd, index=close.index)
            macd_dea = pd.Series(macd_signal, index=close.index)
        else:
            # 简化MACD计算
            ema_fast = close.ewm(span=macd_fast, adjust=False).mean()
            ema_slow = close.ewm(span=macd_slow, adjust=False).mean()
            macd_line = ema_fast - ema_slow
            macd_dea = macd_line.ewm(span=macd_signal, adjust=False).mean()

        # 计算KDJ
        lowest_low = low.rolling(window=fastk_period).min()
        highest_high = high.rolling(window=fastk_period).max()
        rsv = (close - lowest_low) / (highest_high - lowest_low) * 100
        k = rsv.ewm(alpha=1/slowk_period, adjust=False).mean()
        d = k.ewm(alpha=1/slowd_period, adjust=False).mean()

        # 计算RSI
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=rsi_period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=rsi_period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))

        # 检测背离
        macd_div = self.detect_divergence(close, macd_line)
        kdj_div = self.detect_divergence(close, k)
        rsi_div = self.detect_divergence(close, rsi)

        # 综合买卖信号
        buy_signal = pd.Series(0, index=close.index)
        sell_signal = pd.Series(0, index=close.index)

        # 买入条件：底背离 + 风险值低 + MACD向上
        buy_conditions = (
            ((macd_div['bottom_divergence'] == 1) |
             (kdj_div['bottom_divergence'] == 1) |
             (rsi_div['bottom_divergence'] == 1)) &
            (risk_34 < 30) &
            (macd_line.diff() > 0)
        )
        buy_signal = buy_conditions.astype(int)

        # 卖出条件：顶背离 + 风险值高 + MACD向下
        sell_conditions = (
            ((macd_div['top_divergence'] == 1) |
             (kdj_div['top_divergence'] == 1) |
             (rsi_div['top_divergence'] == 1)) &
            (risk_34 > 70) &
            (macd_line.diff() < 0)
        )
        sell_signal = sell_conditions.astype(int)

        return {
            'risk_value_34': risk_34,
            'risk_value_170': risk_170,
            'risk_value_1020': risk_1020,
            'macd_div_top': macd_div['top_divergence'],
            'macd_div_bottom': macd_div['bottom_divergence'],
            'kdj_div_top': kdj_div['top_divergence'],
            'kdj_div_bottom': kdj_div['bottom_divergence'],
            'rsi_div_top': rsi_div['top_divergence'],
            'rsi_div_bottom': rsi_div['bottom_divergence'],
            'buy_signal': buy_signal,
            'sell_signal': sell_signal
        }

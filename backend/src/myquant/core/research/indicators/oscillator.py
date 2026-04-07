# -*- coding: utf-8 -*-
"""
震荡类技术指标
包含：KDJ、SKDJ、RSI、CCI、WR（威廉指标）
"""
from typing import Dict
import pandas as pd
from loguru import logger

from .base import BaseIndicator, TALIB_AVAILABLE

# 导入 talib（如果可用）
if TALIB_AVAILABLE:
    import talib


class OscillatorIndicators(BaseIndicator):
    """震荡类指标计算器"""

    def __init__(self):
        super().__init__()
        logger.info("✅ 震荡指标模块初始化完成")

    # ==================== KDJ指标 ====================

    def calculate_kdj(
        self,
        high: pd.Series,
        low: pd.Series,
        close: pd.Series,
        fastk_period: int = 9,
        slowk_period: int = 3,
        slowd_period: int = 3
    ) -> Dict[str, pd.Series]:
        """
        计算KDJ指标（随机指标）

        Args:
            high: 最高价序列
            low: 最低价序列
            close: 收盘价序列
            fastk_period: K值周期
            slowk_period: K值平滑周期
            slowd_period: D值周期

        Returns:
            {
                'k': K值,
                'd': D值,
                'j': J值
            }
        """
        if not self.available:
            # 简化实现
            lowest_low = low.rolling(window=fastk_period).min()
            highest_high = high.rolling(window=fastk_period).max()

            rsv = (close - lowest_low) / (highest_high - lowest_low) * 100
            k = rsv.ewm(alpha=1/slowk_period, adjust=False).mean()
            d = k.ewm(alpha=1/slowd_period, adjust=False).mean()
            j = 3 * k - 2 * d

            return {'k': k, 'd': d, 'j': j}

        k, d = talib.STOCH(
            high,
            low,
            close,
            fastk_period=fastk_period,
            slowk_period=slowk_period,
            slowk_matype=0,
            slowd_period=slowd_period,
            slowd_matype=0
        )

        j = 3 * k - 2 * d

        return {
            'k': pd.Series(k, index=close.index),
            'd': pd.Series(d, index=close.index),
            'j': pd.Series(j, index=close.index)
        }

    # ==================== SKDJ指标 ====================

    def calculate_skdj(
        self,
        high: pd.Series,
        low: pd.Series,
        close: pd.Series,
        fastk_period: int = 9,
        slowk_period: int = 3,
        slowd_period: int = 3,
        smooth_period: int = 3
    ) -> Dict[str, pd.Series]:
        """
        计算SKDJ指标（慢速随机指标 Slow KDJ）- 完全匹配通达信公式

        通达信公式：
        LOWV:=LLV(LOW,N);        // N日内最低价的最低值
        HIGHV:=HHV(HIGH,N);      // N日内最高价的最高值
        RSV:=EMA((CLOSE-LOWV)/(HIGHV-LOWV)*100,M);
        K:=EMA(RSV,M);
        D:=MA(K,M);

        Args:
            high: 最高价序列
            low: 最低价序列
            close: 收盘价序列
            fastk_period: 周期N（用于计算LOWV/HIGHV）
            slowk_period: RSV的EMA周期M
            slowd_period: K的MA周期（同时用于D的计算周期）
            smooth_period: 此参数在通达信中不使用（保留参数兼容性）

        Returns:
            {
                'sk': SK值（慢速K）,
                'sd': SD值（慢速D）
            }
        """
        # 计算N日内最高价和最低价
        lowest_low = low.rolling(window=fastk_period).min()
        highest_high = high.rolling(window=fastk_period).max()

        # 计算RSV：未收盘位置的RSV = (收盘价 - 最低价) / (最高价 - 最低价) * 100
        rsv = (close - lowest_low) / (highest_high - lowest_low) * 100

        if self.available:
            # 使用 talib 计算 RSV 的 EMA
            k_values = talib.EMA(rsv.values, timeperiod=slowk_period)

            # 计算D：K的简单移动平均（MA），不是EMA！
            d_values = talib.SMA(k_values, timeperiod=slowd_period)
        else:
            # 简化实现
            k_values = rsv.ewm(alpha=1/slowk_period, adjust=False).mean()
            d_values = k_values.rolling(window=slowd_period).mean()

        return {
            'sk': pd.Series(k_values, index=close.index),
            'sd': pd.Series(d_values, index=close.index)
        }

    # ==================== RSI相对强弱指标 ====================

    def calculate_rsi(
        self,
        data: pd.Series,
        period: int = 14
    ) -> pd.Series:
        """
        计算RSI指标

        Args:
            data: 价格序列
            period: 周期

        Returns:
            RSI值序列
        """
        if not self.available:
            # 简化实现
            delta = data.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            return rsi

        rsi = talib.RSI(data, timeperiod=period)
        return pd.Series(rsi, index=data.index)

    # ==================== CCI顺势指标 ====================

    def calculate_cci(
        self,
        high: pd.Series,
        low: pd.Series,
        close: pd.Series,
        period: int = 14
    ) -> pd.Series:
        """
        计算CCI指标（顺势指标）

        Args:
            high: 最高价序列
            low: 最低价序列
            close: 收盘价序列
            period: 周期

        Returns:
            CCI值序列
        """
        if not self.available:
            # 简化实现
            tp = (high + low + close) / 3
            ma_tp = tp.rolling(window=period).mean()
            md = tp.rolling(window=period).apply(lambda x: abs(x - x.mean()).mean())
            cci = (tp - ma_tp) / (0.015 * md)
            return cci

        cci = talib.CCI(high, low, close, timeperiod=period)
        return pd.Series(cci, index=close.index)

    # ==================== WR威廉指标 ====================

    def calculate_wr(
        self,
        high: pd.Series,
        low: pd.Series,
        close: pd.Series,
        period: int = 14
    ) -> pd.Series:
        """
        计算WR（威廉指标）

        Args:
            high: 最高价序列
            low: 最低价序列
            close: 收盘价序列
            period: 周期

        Returns:
            WR值序列（0-100，超买>80，超卖<20）
        """
        if not self.available:
            # 简化实现，返回 0-100
            hh = high.rolling(window=period).max()
            ll = low.rolling(window=period).min()
            wr = 100 * (hh - close) / (hh - ll)
            return wr

        wr = talib.WILLR(high, low, close, timeperiod=period)
        # talib.WILLR 返回 -100 到 0，转换为 0 到 100
        wr = 100 + pd.Series(wr, index=close.index)
        return wr

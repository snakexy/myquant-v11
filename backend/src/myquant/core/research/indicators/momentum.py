# -*- coding: utf-8 -*-
"""
动量类技术指标
包含：ATR（真实波幅）、BIAS（乖离率）
"""
from typing import Dict
import pandas as pd
from loguru import logger

from .base import BaseIndicator, TALIB_AVAILABLE

# 导入 talib（如果可用）
if TALIB_AVAILABLE:
    import talib


class MomentumIndicators(BaseIndicator):
    """动量类指标计算器"""

    def __init__(self):
        super().__init__()
        logger.info("✅ 动量指标模块初始化完成")

    # ==================== ATR真实波幅 ====================

    def calculate_atr(
        self,
        high: pd.Series,
        low: pd.Series,
        close: pd.Series,
        period: int = 14
    ) -> pd.Series:
        """
        计算ATR（平均真实波幅）

        Args:
            high: 最高价序列
            low: 最低价序列
            close: 收盘价序列
            period: 周期

        Returns:
            ATR值序列
        """
        if not self.available:
            # 简化实现
            tr1 = high - low
            tr2 = abs(high - close.shift(1))
            tr3 = abs(low - close.shift(1))
            tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
            atr = tr.rolling(window=period).mean()
            return atr

        atr = talib.ATR(high, low, close, timeperiod=period)
        return pd.Series(atr, index=close.index)

    # ==================== BIAS乖离率 ====================

    def calculate_bias(
        self,
        close: pd.Series,
        period: int = 6
    ) -> pd.Series:
        """
        计算BIAS（乖离率）

        Args:
            close: 收盘价序列
            period: 周期

        Returns:
            BIAS值序列（百分比）
        """
        ma = close.rolling(window=period).mean()
        bias = (close - ma) / ma * 100
        return bias

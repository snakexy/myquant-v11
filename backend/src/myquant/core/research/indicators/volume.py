# -*- coding: utf-8 -*-
"""
成交量类技术指标
包含：OBV（能量潮）
"""
from typing import Dict
import pandas as pd
from loguru import logger

from .base import BaseIndicator, TALIB_AVAILABLE

# 导入 talib（如果可用）
if TALIB_AVAILABLE:
    import talib


class VolumeIndicators(BaseIndicator):
    """成交量类指标计算器"""

    def __init__(self):
        super().__init__()
        logger.info("✅ 成交量指标模块初始化完成")

    # ==================== OBV能量潮 ====================

    def calculate_obv(
        self,
        close: pd.Series,
        volume: pd.Series
    ) -> pd.Series:
        """
        计算OBV指标（能量潮）

        Args:
            close: 收盘价序列
            volume: 成交量序列

        Returns:
            OBV值序列
        """
        if not self.available:
            # 简化实现
            obv = pd.Series(index=close.index, dtype=float)
            obv.iloc[0] = volume.iloc[0]

            for i in range(1, len(close)):
                if close.iloc[i] > close.iloc[i-1]:
                    obv.iloc[i] = obv.iloc[i-1] + volume.iloc[i]
                elif close.iloc[i] < close.iloc[i-1]:
                    obv.iloc[i] = obv.iloc[i-1] - volume.iloc[i]
                else:
                    obv.iloc[i] = obv.iloc[i-1]
            return obv

        obv = talib.OBV(close, volume)
        return pd.Series(obv, index=close.index)

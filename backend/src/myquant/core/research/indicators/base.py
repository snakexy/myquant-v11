# -*- coding: utf-8 -*-
"""
技术指标基类和工具函数
"""
from typing import Dict
from loguru import logger
from dataclasses import dataclass
from enum import Enum
import pandas as pd

# 尝试导入ta-lib
try:
    import talib
    TALIB_AVAILABLE = True
    logger.info("✅ ta-lib已安装并可用")
except ImportError:
    TALIB_AVAILABLE = False
    logger.warning("⚠️ ta-lib未安装，指标计算功能将受限")


class IndicatorType(Enum):
    """指标类型"""
    OVERLAY = "overlay"           # 叠加指标（在主图上显示）
    OSCILLATOR = "oscillator"     # 震荡指标（独立窗格）
    VOLUME = "volume"             # 成交量指标
    MOMENTUM = "momentum"         # 动量指标
    VOLATILITY = "volatility"     # 波动率指标
    CYCLE = "cycle"               # 周期指标


@dataclass
class IndicatorResult:
    """指标计算结果"""
    indicator_name: str           # 指标名称
    indicator_type: IndicatorType # 指标类型
    data: pd.Series               # 指标数据
    params: Dict[str, any]        # 计算参数

    def to_dict(self) -> Dict:
        """转换为字典格式（用于API返回）"""
        return {
            'name': self.indicator_name,
            'type': self.indicator_type.value,
            'params': self.params,
            'data': self.data.tolist() if self.data is not None else []
        }


class BaseIndicator:
    """指标计算基类"""

    def __init__(self):
        """初始化指标计算器"""
        self.available = TALIB_AVAILABLE

    def _validate_data(self, data: pd.Series, min_periods: int = 0) -> bool:
        """验证数据有效性"""
        if data is None or len(data) == 0:
            return False
        if min_periods > 0 and len(data) < min_periods:
            return False
        return True

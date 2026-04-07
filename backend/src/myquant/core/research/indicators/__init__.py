# -*- coding: utf-8 -*-
"""
技术指标计算服务 - 模块化版本
================================
职责：
- 提供所有技术指标的计算能力
- 按类别组织指标（趋势、震荡、动量、成交量）
- 向后兼容原 IndicatorService 接口

架构层次：
- TrendIndicators: 趋势类（MA、MACD、BOLL）
- OscillatorIndicators: 震荡类（KDJ、SKDJ、RSI、CCI、WR）
- MomentumIndicators: 动量类（ATR、BIAS）
- VolumeIndicators: 成交量类（OBV）

作者: MyQuant v11 Team
创建时间: 2026-04-07
"""

from typing import List, Dict, Optional
import pandas as pd
from loguru import logger

from .base import IndicatorType, IndicatorResult, TALIB_AVAILABLE
from .trend import TrendIndicators
from .oscillator import OscillatorIndicators
from .momentum import MomentumIndicators
from .volume import VolumeIndicators
from .top_bottom import TopBottomIndicator


class IndicatorService:
    """
    技术指标计算服务（统一入口）

    向后兼容原 IndicatorService 接口，同时提供模块化架构
    """

    def __init__(self):
        """初始化指标服务"""
        self.available = TALIB_AVAILABLE

        # 初始化各类指标计算器
        self.trend = TrendIndicators()
        self.oscillator = OscillatorIndicators()
        self.momentum = MomentumIndicators()
        self.volume = VolumeIndicators()
        self.top_bottom = TopBottomIndicator()

        # 指标缓存
        self._cache: Dict[str, IndicatorResult] = {}

        if self.available:
            logger.info("✅ IndicatorService初始化完成（ta-lib模式）")
        else:
            logger.info("✅ IndicatorService初始化完成（pandas模式）")

    # ==================== 趋势指标代理 ====================

    def calculate_sma(self, data: pd.Series, period: int = 20) -> pd.Series:
        """计算简单移动平均线"""
        return self.trend.calculate_sma(data, period)

    def calculate_ema(self, data: pd.Series, period: int = 20) -> pd.Series:
        """计算指数移动平均线"""
        return self.trend.calculate_ema(data, period)

    def calculate_ma(
        self,
        df: pd.DataFrame,
        periods: List[int] = [5, 10, 20, 30, 60],
        price_column: str = 'close'
    ) -> Dict[str, pd.Series]:
        """批量计算移动平均线"""
        return self.trend.calculate_ma(df, periods, price_column)

    def calculate_macd(
        self,
        data: pd.Series,
        fast_period: int = 12,
        slow_period: int = 26,
        signal_period: int = 9
    ) -> Dict[str, pd.Series]:
        """计算MACD指标"""
        return self.trend.calculate_macd(data, fast_period, slow_period, signal_period)

    def calculate_boll(
        self,
        data: pd.Series,
        period: int = 20,
        nbdev_up: float = 2.0,
        nbdev_down: float = 2.0
    ) -> Dict[str, pd.Series]:
        """计算布林带"""
        return self.trend.calculate_boll(data, period, nbdev_up, nbdev_down)

    # ==================== 震荡指标代理 ====================

    def calculate_kdj(
        self,
        high: pd.Series,
        low: pd.Series,
        close: pd.Series,
        fastk_period: int = 9,
        slowk_period: int = 3,
        slowd_period: int = 3
    ) -> Dict[str, pd.Series]:
        """计算KDJ指标"""
        return self.oscillator.calculate_kdj(high, low, close, fastk_period, slowk_period, slowd_period)

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
        """计算SKDJ指标（慢速随机指标）"""
        return self.oscillator.calculate_skdj(high, low, close, fastk_period, slowk_period, slowd_period, smooth_period)

    def calculate_rsi(self, data: pd.Series, period: int = 14) -> pd.Series:
        """计算RSI指标"""
        return self.oscillator.calculate_rsi(data, period)

    def calculate_cci(
        self,
        high: pd.Series,
        low: pd.Series,
        close: pd.Series,
        period: int = 14
    ) -> pd.Series:
        """计算CCI指标"""
        return self.oscillator.calculate_cci(high, low, close, period)

    def calculate_wr(
        self,
        high: pd.Series,
        low: pd.Series,
        close: pd.Series,
        period: int = 14
    ) -> pd.Series:
        """计算WR威廉指标"""
        return self.oscillator.calculate_wr(high, low, close, period)

    # ==================== 动量指标代理 ====================

    def calculate_atr(
        self,
        high: pd.Series,
        low: pd.Series,
        close: pd.Series,
        period: int = 14
    ) -> pd.Series:
        """计算ATR真实波幅"""
        return self.momentum.calculate_atr(high, low, close, period)

    def calculate_bias(self, close: pd.Series, period: int = 6) -> pd.Series:
        """计算BIAS乖离率"""
        return self.momentum.calculate_bias(close, period)

    # ==================== 成交量指标代理 ====================

    def calculate_obv(self, close: pd.Series, volume: pd.Series) -> pd.Series:
        """计算OBV能量潮"""
        return self.volume.calculate_obv(close, volume)

    # ==================== 顶底背离指标 ====================

    def calculate_top_bottom_signals(
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
        """计算顶底背离信号"""
        return self.top_bottom.calculate_signals(
            high, low, close, fastk_period, slowk_period, slowd_period,
            rsi_period, macd_fast, macd_slow, macd_signal
        )

    # ==================== 批量计算 ====================

    def calculate_all_indicators(
        self,
        df: pd.DataFrame,
        indicators: Optional[List[str]] = None
    ) -> Dict[str, pd.Series]:
        """
        批量计算常用技术指标

        Args:
            df: K线数据DataFrame（必须包含：open, high, low, close, volume）
            indicators: 要计算的指标列表，None表示计算所有常用指标

        Returns:
            {指标名: 指标值序列}
        """
        if not all(col in df.columns for col in ['open', 'high', 'low', 'close', 'volume']):
            logger.error("数据缺少必需列：open, high, low, close, volume")
            return {}

        result = {}

        # 默认计算所有常用指标
        if indicators is None:
            indicators = [
                'ma5', 'ma10', 'ma20', 'ma30', 'ma60',
                'macd', 'kdj', 'skdj', 'boll', 'rsi', 'atr', 'cci', 'obv'
            ]

        # 统一转换为小写，不区分大小写
        indicators_lower = [ind.lower() for ind in indicators]

        # 辅助函数：获取原始大小写的指标名
        def get_original_name(lower_name: str) -> str:
            """获取原始大小写的指标名"""
            return next((ind for ind in indicators if ind.lower() == lower_name), lower_name)

        # MA均线
        ma_indicators = [ind for ind in indicators_lower if ind.startswith('ma')]
        if ma_indicators:
            periods = [int(ind[2:]) for ind in ma_indicators]
            ma_result = self.calculate_ma(df, periods)
            result.update(ma_result)  # MA指标是扁平结构，直接update

        # MACD
        if 'macd' in indicators_lower:
            macd_result = self.calculate_macd(df['close'])
            result[get_original_name('macd')] = macd_result

        # KDJ
        if 'kdj' in indicators_lower:
            kdj_result = self.calculate_kdj(df['high'], df['low'], df['close'])
            result[get_original_name('kdj')] = kdj_result

        # SKDJ
        if 'skdj' in indicators_lower:
            skdj_result = self.calculate_skdj(df['high'], df['low'], df['close'])
            result[get_original_name('skdj')] = skdj_result

        # BOLL
        if 'boll' in indicators_lower:
            boll_result = self.calculate_boll(df['close'])
            result[get_original_name('boll')] = boll_result

        # RSI
        if 'rsi' in indicators_lower:
            result[get_original_name('rsi')] = self.calculate_rsi(df['close'])

        # ATR
        if 'atr' in indicators_lower:
            result[get_original_name('atr')] = self.calculate_atr(df['high'], df['low'], df['close'])

        # CCI
        if 'cci' in indicators_lower:
            result[get_original_name('cci')] = self.calculate_cci(df['high'], df['low'], df['close'])

        # OBV
        if 'obv' in indicators_lower:
            result[get_original_name('obv')] = self.calculate_obv(df['close'], df['volume'])

        # TOPBOTTOM（顶底背离指标）
        if 'topbottom' in indicators_lower:
            topbottom_result = self.top_bottom.calculate_signals(
                df['high'], df['low'], df['close'],
                fastk_period=9, slowk_period=3, slowd_period=3,
                rsi_period=14, macd_fast=12, macd_slow=26, macd_signal=9
            )
            result[get_original_name('topbottom')] = topbottom_result

        logger.info(f"✅ 已计算{len(result)}个技术指标")
        return result


# ==================== 全局单例 ====================

_indicator_service_instance: Optional[IndicatorService] = None


def get_indicator_service() -> IndicatorService:
    """
    获取指标计算服务单例

    Returns:
        IndicatorService实例
    """
    global _indicator_service_instance

    if _indicator_service_instance is None:
        _indicator_service_instance = IndicatorService()

    return _indicator_service_instance


# 导出所有公共接口
__all__ = [
    'IndicatorService',
    'IndicatorType',
    'IndicatorResult',
    'TrendIndicators',
    'OscillatorIndicators',
    'MomentumIndicators',
    'VolumeIndicators',
]

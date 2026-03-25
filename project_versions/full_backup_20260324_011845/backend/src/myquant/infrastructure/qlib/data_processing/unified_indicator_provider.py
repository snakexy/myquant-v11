#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一技术指标提供器

根据使用场景自动选择最合适的技术指标实现:
- QLib Expression Engine (QLib回测)
- TA-Lib (实盘交易)
- 自定义实现 (快速原型)

作者: Claude Code
日期: 2026-01-24
版本: 1.0
"""

import logging
from typing import Dict, List, Union, Optional
from enum import Enum
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


class IndicatorBackend(Enum):
    """技术指标后端"""
    AUTO = "auto"           # 自动选择
    QLIB = "qlib"           # QLib Expression Engine
    TALIB = "talib"         # TA-Lib
    CUSTOM = "custom"       # 自定义实现


class UnifiedIndicatorProvider:
    """
    统一技术指标提供器

    根据 backend 参数自动选择最合适的实现:
    - IndicatorBackend.QLIB: 使用 QLib Expression Engine
    - IndicatorBackend.TALIB: 使用 TA-Lib
    - IndicatorBackend.CUSTOM: 使用自定义实现
    - IndicatorBackend.AUTO: 根据场景自动选择
    """

    def __init__(self, backend: Union[str, IndicatorBackend] = IndicatorBackend.AUTO):
        """
        初始化技术指标提供器

        Args:
            backend: 后端选择 (qlib, talib, custom, auto)
        """
        if isinstance(backend, str):
            backend = IndicatorBackend(backend.lower())

        self.backend = backend
        self._qlib_provider = None
        self._talib_provider = None
        self._custom_provider = None

        # 初始化可用的提供器
        self._initialize_providers()

        logger.info(f"UnifiedIndicatorProvider initialized with backend: {backend.value}")

    def _initialize_providers(self):
        """初始化可用的技术指标提供器"""

        # 1. 尝试初始化自定义提供器
        try:
            from qlib_core.data_processing.technical_indicators import get_indicators_calculator
            self._custom_provider = get_indicators_calculator()
            logger.info("Custom indicator provider: Loaded")
        except Exception as e:
            logger.warning(f"Custom indicator provider: Not available - {e}")

        # 2. 尝试初始化TA-Lib提供器
        try:
            import talib
            self._talib_provider = talib
            logger.info(f"TA-Lib provider: Loaded (v{talib.__version__})")
        except ImportError:
            logger.warning("TA-Lib provider: Not available")

        # 3. 尝试初始化QLib提供器
        try:
            import qlib
            from qlib.data import D

            # 检查QLib是否已初始化
            if not hasattr(qlib, 'provider_uri'):
                logger.warning("QLib provider: QLib not initialized. Call qlib.init() first.")
            else:
                self._qlib_provider = D
                logger.info("QLib Expression provider: Loaded")
        except ImportError:
            logger.warning("QLib Expression provider: Not available")

    def _select_backend(self, indicators: Optional[List[str]] = None) -> IndicatorBackend:
        """
        根据backend参数和可用性选择实际使用的后端

        Args:
            indicators: 要计算的指标列表

        Returns:
            实际使用的后端
        """
        backend = self.backend

        # AUTO模式下的选择逻辑
        if backend == IndicatorBackend.AUTO:
            # 优先级: QLIB > TALIB > CUSTOM
            if self._qlib_provider is not None:
                backend = IndicatorBackend.QLIB
            elif self._talib_provider is not None:
                backend = IndicatorBackend.TALIB
            elif self._custom_provider is not None:
                backend = IndicatorBackend.CUSTOM
            else:
                raise RuntimeError("No indicator provider available!")

        # 检查选定的后端是否可用
        if backend == IndicatorBackend.QLIB and self._qlib_provider is None:
            logger.warning("QLib backend requested but not available, falling back to custom")
            backend = IndicatorBackend.CUSTOM

        if backend == IndicatorBackend.TALIB and self._talib_provider is None:
            logger.warning("TA-Lib backend requested but not available, falling back to custom")
            backend = IndicatorBackend.CUSTOM

        if backend == IndicatorBackend.CUSTOM and self._custom_provider is None:
            raise RuntimeError("Custom indicator provider not available!")

        return backend

    def get_indicators(
        self,
        data: pd.DataFrame,
        indicators: List[str],
        backend: Optional[Union[str, IndicatorBackend]] = None
    ) -> pd.DataFrame:
        """
        计算技术指标

        Args:
            data: 价格数据 (必须包含 open, high, low, close, volume 列)
            indicators: 指标列表，如 ['MA', 'RSI', 'MACD']
            backend: 覆盖默认的后端选择

        Returns:
            包含技术指标的DataFrame
        """
        # 确定使用的后端
        if backend is not None:
            if isinstance(backend, str):
                backend = IndicatorBackend(backend.lower())
            actual_backend = self._select_backend_for_backend(backend)
        else:
            actual_backend = self._select_backend(indicators)

        logger.info(f"Calculating indicators using {actual_backend.value} backend")

        # 根据后端计算指标
        if actual_backend == IndicatorBackend.QLIB:
            return self._get_qlib_indicators(data, indicators)
        elif actual_backend == IndicatorBackend.TALIB:
            return self._get_talib_indicators(data, indicators)
        else:
            return self._get_custom_indicators(data, indicators)

    def _select_backend_for_backend(self, backend: IndicatorBackend) -> IndicatorBackend:
        """为指定的backend选择实际可用的后端"""
        if backend == IndicatorBackend.QLIB and self._qlib_provider is not None:
            return backend
        elif backend == IndicatorBackend.TALIB and self._talib_provider is not None:
            return backend
        elif backend == IndicatorBackend.CUSTOM and self._custom_provider is not None:
            return backend
        else:
            # 回退到可用的后端
            return self._select_backend()

    def _get_custom_indicators(self, data: pd.DataFrame, indicators: List[str]) -> pd.DataFrame:
        """使用自定义实现计算指标"""
        return self._custom_provider.calculate_technical_indicators(
            data=data.copy(),
            indicators=indicators
        )

    def _get_talib_indicators(self, data: pd.DataFrame, indicators: List[str]) -> pd.DataFrame:
        """使用TA-Lib计算指标"""
        result = data.copy()

        closes = data['close'].values
        highs = data['high'].values
        lows = data['low'].values
        opens = data['open'].values
        volumes = data['volume'].values

        # MA
        if 'MA' in indicators:
            for period in [5, 10, 20, 60]:
                result[f'MA_{period}'] = self._talib_provider.MA(closes, timeperiod=period)

        # EMA
        if 'EMA' in indicators:
            result['EMA_12'] = self._talib_provider.EMA(closes, timeperiod=12)
            result['EMA_26'] = self._talib_provider.EMA(closes, timeperiod=26)

        # RSI
        if 'RSI' in indicators:
            result['RSI'] = self._talib_provider.RSI(closes, timeperiod=14)

        # MACD
        if 'MACD' in indicators:
            macd, signal, hist = self._talib_provider.MACD(closes)
            result['MACD'] = macd
            result['MACD_signal'] = signal
            result['MACD_hist'] = hist

        # BOLL
        if 'BOLL' in indicators:
            upper, middle, lower = self._talib_provider.BBANDS(closes)
            result['BOLL_upper'] = upper
            result['BOLL_middle'] = middle
            result['BOLL_lower'] = lower

        # ATR
        if 'ATR' in indicators:
            result['ATR'] = self._talib_provider.ATR(highs, lows, closes, timeperiod=14)

        # CCI
        if 'CCI' in indicators:
            result['CCI'] = self._talib_provider.CCI(highs, lows, closes, timeperiod=14)

        # WILLR
        if 'WILLR' in indicators:
            result['WILLR'] = self._talib_provider.WILLR(highs, lows, closes, timeperiod=14)

        # MOM
        if 'MOM' in indicators:
            result['MOM'] = self._talib_provider.MOM(closes, timeperiod=10)

        # STOCH
        if 'STOCH' in indicators:
            slowk, slowd = self._talib_provider.STOCH(highs, lows, closes)
            result['STOCH_K'] = slowk
            result['STOCH_D'] = slowd

        # ROC
        if 'ROC' in indicators:
            result['ROC'] = self._talib_provider.ROC(closes, timeperiod=12)

        # OBV
        if 'OBV' in indicators:
            result['OBV'] = self._talib_provider.OBV(closes, volumes)

        logger.info(f"TA-Lib indicators calculated: {len(indicators)} indicators")
        return result

    def _get_qlib_indicators(self, data: pd.DataFrame, indicators: List[str]) -> pd.DataFrame:
        """
        使用QLib Expression Engine计算指标

        注意: QLib需要数据已经转换为.bin格式
        """
        # 将指标名称映射到QLib表达式
        indicator_map = {
            'MA': [
                'Mean($close, 5)',
                'Mean($close, 10)',
                'Mean($close, 20)',
                'Mean($close, 60)'
            ],
            'EMA': [
                'EMA($close, 12)',
                'EMA($close, 26)'
            ],
            'RSI': ['RSI($close, 14)'],
            'MACD': [],  # MACD需要多个表达式
            'BOLL': [],  # BOLL需要多个表达式
            'ATR': ['ATR($high, $low, $close, 14)'],
            'CCI': ['CCI($high, $low, $close, 14)'],
            'WILLR': ['WILLR($high, $low, $close, 14)'],
            'MOM': ['MOM($close, 10)'],
            'STOCH': [],  # STOCH需要多个表达式
            'ROC': ['ROC($close, 12)'],
            'OBV': ['OBV($close, $volume)'],
        }

        # 构建QLib字段表达式
        fields = []
        for ind in indicators:
            if ind in indicator_map:
                fields.extend(indicator_map[ind])

        # 使用QLib的D.features API
        # 注意: 这里需要数据已经加载到QLib中
        # 实际使用时，用户需要先调用 qlib.init() 并准备好数据
        logger.warning("QLib backend requires data to be in QLib .bin format")
        logger.warning("For QLib backtest, use qlib.data.D.features() directly")

        # 返回原数据（QLib模式不适合直接使用DataFrame输入）
        return data

    def get_available_backends(self) -> List[str]:
        """获取所有可用的后端"""
        backends = []
        if self._qlib_provider is not None:
            backends.append('qlib')
        if self._talib_provider is not None:
            backends.append('talib')
        if self._custom_provider is not None:
            backends.append('custom')
        return backends

    def get_backend_info(self) -> Dict[str, str]:
        """获取后端信息"""
        info = {
            'default_backend': self.backend.value,
            'available_backends': self.get_available_backends()
        }

        if self._talib_provider is not None:
            info['talib_version'] = self._talib_provider.__version__

        return info


# 全局实例
_global_provider: Optional[UnifiedIndicatorProvider] = None


def get_indicator_provider(
    backend: Union[str, IndicatorBackend] = IndicatorBackend.AUTO
) -> UnifiedIndicatorProvider:
    """
    获取全局技术指标提供器实例

    Args:
        backend: 后端选择

    Returns:
        技术指标提供器实例
    """
    global _global_provider

    if _global_provider is None or _global_provider.backend != backend:
        _global_provider = UnifiedIndicatorProvider(backend=backend)

    return _global_provider


# 便捷函数
def calculate_indicators(
    data: pd.DataFrame,
    indicators: List[str],
    backend: str = 'auto'
) -> pd.DataFrame:
    """
    便捷函数: 计算技术指标

    Args:
        data: 价格数据
        indicators: 指标列表
        backend: 后端选择 ('auto', 'qlib', 'talib', 'custom')

    Returns:
        包含技术指标的DataFrame

    Examples:
        >>> # 自动选择后端
        >>> result = calculate_indicators(data, ['MA', 'RSI', 'MACD'])

        >>> # 指定使用TA-Lib (适合实盘)
        >>> result = calculate_indicators(data, ['MA', 'RSI'], backend='talib')

        >>> # 指定使用自定义实现 (快速原型)
        >>> result = calculate_indicators(data, ['MA', 'RSI'], backend='custom')
    """
    provider = get_indicator_provider(backend=backend)
    return provider.get_indicators(data, indicators)

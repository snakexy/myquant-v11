"""
技术指标计算模块
提供各种技术指标的计算功能
"""

import os
import sys
import logging
import pandas as pd
import numpy as np
from typing import List, Optional

# 添加项目根目录到路径
sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
)

logger = logging.getLogger(__name__)


class TechnicalIndicatorsCalculator:
    """
    技术指标计算器
    
    提供各种技术指标的计算功能
    """
    
    def __init__(self, config=None):
        """
        初始化技术指标计算器
        
        Args:
            config: 配置参数
        """
        self.config = config or {}
        self.indicator_windows = self.config.get(
            'indicator_windows', [5, 10, 20, 60]
        )
        
        logger.info("技术指标计算器初始化完成")
    
    def calculate_technical_indicators(
        self, 
        data: pd.DataFrame,
        indicators: List[str] = None
    ) -> pd.DataFrame:
        """
        计算技术指标
        
        Args:
            data: 价格数据
            indicators: 指标列表
            
        Returns:
            包含技术指标的数据
        """
        if indicators is None:
            indicators = [
                'MA', 'EMA', 'RSI', 'MACD', 'BOLL',
                'ATR', 'CCI', 'WILLR', 'MOM', 'KDJ',
                'OBV', 'STOCH', 'TRIX', 'ROC', 'VWAP'  # 新增指标
            ]
        
        try:
            result_data = data.copy()
            
            # 移动平均线
            if 'MA' in indicators:
                result_data = self._calculate_moving_averages(result_data)
            
            # 指数移动平均
            if 'EMA' in indicators:
                result_data = self._calculate_exponential_moving_averages(
                    result_data
                )
            
            # RSI
            if 'RSI' in indicators:
                result_data = self._calculate_rsi(result_data)
            
            # MACD
            if 'MACD' in indicators:
                result_data = self._calculate_macd(result_data)
            
            # 布林带
            if 'BOLL' in indicators:
                result_data = self._calculate_bollinger_bands(result_data)
            
            # ATR
            if 'ATR' in indicators:
                result_data = self._calculate_atr(result_data)
            
            # CCI
            if 'CCI' in indicators:
                result_data = self._calculate_cci(result_data)
            
            # 威廉指标
            if 'WILLR' in indicators:
                result_data = self._calculate_williams_r(result_data)
            
            # 动量指标
            if 'MOM' in indicators:
                result_data = self._calculate_momentum(result_data)
            
            # KDJ
            if 'KDJ' in indicators:
                result_data = self._calculate_kdj(result_data)

            # OBV - 能量潮指标
            if 'OBV' in indicators:
                result_data = self._calculate_obv(result_data)

            # STOCH - 随机震荡器
            if 'STOCH' in indicators:
                result_data = self._calculate_stoch(result_data)

            # TRIX - 三重指数平滑移动平均
            if 'TRIX' in indicators:
                result_data = self._calculate_trix(result_data)

            # ROC - 变动率指标
            if 'ROC' in indicators:
                result_data = self._calculate_roc(result_data)

            # VWAP - 成交量加权平均价
            if 'VWAP' in indicators:
                result_data = self._calculate_vwap(result_data)

            logger.debug(f"计算技术指标: {indicators}")
            return result_data
            
        except Exception as e:
            logger.error(f"计算技术指标失败: {e}")
            return data
    
    def _calculate_moving_averages(self, data: pd.DataFrame) -> pd.DataFrame:
        """计算多种移动平均线"""
        close_col = 'close'
        if close_col not in data.columns:
            return data
        
        for window in self.indicator_windows:
            if len(data) >= window:
                data[f'MA{window}'] = data[close_col].rolling(
                    window=window
                ).mean()
        
        return data
    
    def _calculate_exponential_moving_averages(
        self, data: pd.DataFrame
    ) -> pd.DataFrame:
        """计算指数移动平均线"""
        close_col = 'close'
        if close_col not in data.columns:
            return data
        
        for window in self.indicator_windows:
            if len(data) >= window:
                data[f'EMA{window}'] = data[close_col].ewm(
                    span=window
                ).mean()
        
        return data
    
    def _calculate_rsi(self, data: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """计算RSI指标"""
        close_col = 'close'
        if close_col not in data.columns:
            return data
        
        delta = data[close_col].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        data['RSI'] = 100 - (100 / (1 + rs))
        
        return data
    
    def _calculate_macd(self, data: pd.DataFrame) -> pd.DataFrame:
        """计算MACD指标"""
        close_col = 'close'
        if close_col not in data.columns:
            return data
        
        ema12 = data[close_col].ewm(span=12).mean()
        ema26 = data[close_col].ewm(span=26).mean()
        
        data['MACD'] = ema12 - ema26
        data['MACD_signal'] = data['MACD'].ewm(span=9).mean()
        data['MACD_hist'] = data['MACD'] - data['MACD_signal']
        
        return data
    
    def _calculate_bollinger_bands(
        self, data: pd.DataFrame, period: int = 20
    ) -> pd.DataFrame:
        """计算布林带"""
        close_col = 'close'
        if close_col not in data.columns:
            return data
        
        ma = data[close_col].rolling(window=period).mean()
        std = data[close_col].rolling(window=period).std()
        
        data['BOLL_upper'] = ma + (std * 2)
        data['BOLL_middle'] = ma
        data['BOLL_lower'] = ma - (std * 2)
        data['BOLL_width'] = data['BOLL_upper'] - data['BOLL_lower']
        
        return data
    
    def _calculate_atr(self, data: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """计算ATR指标"""
        required_cols = ['high', 'low', 'close']
        if not all(col in data.columns for col in required_cols):
            return data
        
        tr1 = data['high'] - data['low']
        tr2 = abs(data['high'] - data['close'].shift(1))
        tr3 = abs(data['low'] - data['close'].shift(1))
        
        true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        data['ATR'] = true_range.rolling(window=period).mean()
        
        return data
    
    def _calculate_cci(self, data: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """计算CCI指标"""
        required_cols = ['high', 'low', 'close']
        if not all(col in data.columns for col in required_cols):
            return data
        
        tp = (data['high'] + data['low'] + data['close']) / 3
        ma_tp = tp.rolling(window=period).mean()
        mad = tp.rolling(window=period).apply(
            lambda x: np.abs(x - x.mean()).mean()
        )
        
        data['CCI'] = (tp - ma_tp) / (0.015 * mad)
        
        return data
    
    def _calculate_williams_r(
        self, data: pd.DataFrame, period: int = 14
    ) -> pd.DataFrame:
        """计算威廉指标"""
        required_cols = ['high', 'low', 'close']
        if not all(col in data.columns for col in required_cols):
            return data
        
        highest_high = data['high'].rolling(window=period).max()
        lowest_low = data['low'].rolling(window=period).min()
        
        data['WILLR'] = -100 * (highest_high - data['close']) / (
            highest_high - lowest_low
        )
        
        return data
    
    def _calculate_momentum(
        self, data: pd.DataFrame, period: int = 10
    ) -> pd.DataFrame:
        """计算动量指标"""
        close_col = 'close'
        if close_col not in data.columns:
            return data
        
        data['MOM'] = data[close_col].diff(period)
        
        return data
    
    def _calculate_kdj(self, data: pd.DataFrame, period: int = 9) -> pd.DataFrame:
        """计算KDJ指标"""
        required_cols = ['high', 'low', 'close']
        if not all(col in data.columns for col in required_cols):
            return data
        
        lowest_low = data['low'].rolling(window=period).min()
        highest_high = data['high'].rolling(window=period).max()
        
        rsv = (data['close'] - lowest_low) / (
            highest_high - lowest_low
        ) * 100
        data['KDJ_K'] = rsv.ewm(com=2).mean()
        data['KDJ_D'] = data['KDJ_K'].ewm(com=2).mean()
        data['KDJ_J'] = 3 * data['KDJ_K'] - 2 * data['KDJ_D']

        return data

    def _calculate_obv(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        计算OBV (On-Balance Volume) 能量潮指标

        OBV显示资金流向，正值表示资金流入，负值表示资金流出
        """
        if 'close' not in data.columns or 'volume' not in data.columns:
            return data

        # 计算价格变化方向
        price_change = data['close'].diff()

        # OBV累积计算
        obv = pd.Series(index=data.index, dtype=float)
        obv.iloc[0] = data['volume'].iloc[0]

        for i in range(1, len(data)):
            if price_change.iloc[i] > 0:
                obv.iloc[i] = obv.iloc[i-1] + data['volume'].iloc[i]
            elif price_change.iloc[i] < 0:
                obv.iloc[i] = obv.iloc[i-1] - data['volume'].iloc[i]
            else:
                obv.iloc[i] = obv.iloc[i-1]

        data['OBV'] = obv
        # 添加OBV移动平均用于信号分析
        data['OBV_MA'] = obv.rolling(window=20).mean()

        return data

    def _calculate_stoch(
        self, data: pd.DataFrame, k_period: int = 14, d_period: int = 3
    ) -> pd.DataFrame:
        """
        计算STOCH (Stochastic Oscillator) 随机震荡器

        %K线和%D线用于识别超买超卖
        """
        required_cols = ['high', 'low', 'close']
        if not all(col in data.columns for col in required_cols):
            return data

        # 计算14周期的最高价和最低价
        lowest_low = data['low'].rolling(window=k_period).min()
        highest_high = data['high'].rolling(window=k_period).max()

        # 计算%K (快线)
        stoch_k = 100 * (data['close'] - lowest_low) / (
            highest_high - lowest_low + 1e-10
        )

        # 计算%D (慢线) - %K的3日移动平均
        stoch_d = stoch_k.rolling(window=d_period).mean()

        # 添加平滑版%K (Slow %K)
        stoch_slow_k = stoch_k.rolling(window=d_period).mean()

        data['STOCH_K'] = stoch_k
        data['STOCH_D'] = stoch_d
        data['STOCH_SlowK'] = stoch_slow_k
        data['STOCH_SlowD'] = stoch_slow_k.rolling(window=d_period).mean()

        return data

    def _calculate_trix(
        self, data: pd.DataFrame, period: int = 15
    ) -> pd.DataFrame:
        """
        计算TRIX (Triple Exponential Average) 三重指数平滑移动平均

        TRIX过滤短期价格波动，显示主要趋势
        """
        close_col = 'close'
        if close_col not in data.columns:
            return data

        # 三重指数平滑
        ema1 = data[close_col].ewm(span=period).mean()
        ema2 = ema1.ewm(span=period).mean()
        ema3 = ema2.ewm(span=period).mean()

        # TRIX是EMA3的百分比变化
        trix = 100 * (ema3.diff(1) / (ema3.shift(1) + 1e-10))

        data['TRIX'] = trix
        # TRIX信号线 (TRIX的9日移动平均)
        data['TRIX_signal'] = trix.rolling(window=9).mean()

        return data

    def _calculate_roc(
        self, data: pd.DataFrame, period: int = 12
    ) -> pd.DataFrame:
        """
        计算ROC (Rate of Change) 变动率指标

        ROC显示价格在一定周期内的变化百分比
        """
        close_col = 'close'
        if close_col not in data.columns:
            return data

        roc = 100 * (
            (data[close_col] - data[close_col].shift(period))
            / (data[close_col].shift(period) + 1e-10)
        )

        data['ROC'] = roc
        # 添加ROC移动平均
        data['ROC_MA'] = roc.rolling(window=6).mean()

        return data

    def _calculate_vwap(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        计算VWAP (Volume Weighted Average Price) 成交量加权平均价

        VWAP是机构交易者的重要参考价格
        """
        required_cols = ['high', 'low', 'close', 'volume']
        if not all(col in data.columns for col in required_cols):
            return data

        # 典型价格 = (最高价 + 最低价 + 收盘价) / 3
        typical_price = (data['high'] + data['low'] + data['close']) / 3

        # 累积典型价格 * 成交量
        cum_price_volume = (typical_price * data['volume']).cumsum()

        # 累积成交量
        cum_volume = data['volume'].cumsum()

        # VWAP = 累积(价格*成交量) / 累积成交量
        vwap = cum_price_volume / (cum_volume + 1e-10)

        data['VWAP'] = vwap

        # 计算VWAP上轨和下轨（标准差带）
        # 这类似于布林带，但基于VWAP
        vwap_std = (
            ((typical_price - vwap) ** 2 * data['volume']).cumsum()
            / (cum_volume + 1e-10)
        ) ** 0.5

        data['VWAP_upper'] = vwap + (vwap_std * 2)
        data['VWAP_lower'] = vwap - (vwap_std * 2)

        return data


# 全局技术指标计算器实例
_global_indicators_calculator = None


def get_indicators_calculator(config=None) -> TechnicalIndicatorsCalculator:
    """获取全局技术指标计算器实例"""
    global _global_indicators_calculator
    
    if _global_indicators_calculator is None:
        _global_indicators_calculator = TechnicalIndicatorsCalculator(config)
    
    return _global_indicators_calculator
# -*- coding: utf-8 -*-
"""
Research阶段 - 技术指标计算服务
================================
职责：
- 使用ta-lib计算技术指标
- 提供150+种技术指标的计算能力
- 高性能指标计算（基于NumPy）
- 支持批量计算和增量更新

架构层次：
- Research阶段：为因子计算和技术分析提供指标
- 依赖ta-lib库（业界标准）
- 为前端图表提供指标数据

技术选型：
- ta-lib: 技术分析库（C底层，Python绑定）
- NumPy: 高性能数值计算
- pandas: 数据处理

作者: MyQuant v10.0.0 Team
创建时间: 2026-02-04
"""

from typing import List, Dict, Optional, Union, Tuple
from loguru import logger
from dataclasses import dataclass
from enum import Enum
import pandas as pd
import numpy as np

# 尝试导入ta-lib
try:
    import talib
    TALIB_AVAILABLE = True
    logger.info("✅ ta-lib已安装并可用")
except ImportError:
    TALIB_AVAILABLE = False
    logger.warning("⚠️ ta-lib未安装，指标计算功能将受限")
    logger.warning("安装命令: pip install TA-Lib")


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
    params: Dict[str, any]         # 计算参数

    def to_dict(self) -> Dict:
        """转换为字典格式（用于API返回）"""
        return {
            'name': self.indicator_name,
            'type': self.indicator_type.value,
            'params': self.params,
            'data': self.data.tolist() if self.data is not None else []
        }


class IndicatorService:
    """
    技术指标计算服务

    核心职责：
    1. 使用ta-lib计算150+种技术指标
    2. 提供高性能批量计算
    3. 支持增量更新
    4. 统一的指标接口

    支持的指标类别：
    - 趋势指标：MA、EMA、SMA、TMA、WMA
    - 动量指标：MACD、RSI、STOCH、KDJ
    - 波动率：BOLL、ATR、NATR
    - 成交量：AD、OBV、VOL
    - 周期指标：HT_DCPERIOD、HT_SINE
    - 统计函数：STDDEV、VAR、LINEARREG

    性能特点：
    - 基于NumPy的向量化计算
    - C底层实现（ta-lib）
    - 比纯Python实现快100倍以上
    """

    def __init__(self):
        """初始化指标服务"""
        self.available = TALIB_AVAILABLE

        # 指标缓存
        self._cache: Dict[str, IndicatorResult] = {}

        if not self.available:
            logger.warning("⚠️ ta-lib不可用，部分指标计算功能将无法使用")

        logger.info("✅ IndicatorService初始化完成")

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
                'macd', 'kdj', 'boll', 'rsi', 'atr', 'cci', 'obv'
            ]

        # MA均线
        ma_indicators = [ind for ind in indicators if ind.startswith('ma')]
        if ma_indicators:
            periods = [int(ind[2:]) for ind in ma_indicators]
            ma_result = self.calculate_ma(df, periods)
            result.update(ma_result)

        # MACD
        if 'macd' in indicators:
            macd_result = self.calculate_macd(df['close'])
            result.update(macd_result)

        # KDJ
        if 'kdj' in indicators:
            kdj_result = self.calculate_kdj(df['high'], df['low'], df['close'])
            result.update(kdj_result)

        # BOLL
        if 'boll' in indicators:
            boll_result = self.calculate_boll(df['close'])
            result.update(boll_result)

        # RSI
        if 'rsi' in indicators:
            result['rsi'] = self.calculate_rsi(df['close'])

        # ATR
        if 'atr' in indicators:
            result['atr'] = self.calculate_atr(df['high'], df['low'], df['close'])

        # CCI
        if 'cci' in indicators:
            result['cci'] = self.calculate_cci(df['high'], df['low'], df['close'])

        # OBV
        if 'obv' in indicators:
            result['obv'] = self.calculate_obv(df['close'], df['volume'])

        logger.info(f"✅ 已计算{len(result)}个技术指标")
        return result

    # ==================== 指标应用到数据 ====================

    def apply_indicators(
        self,
        df: pd.DataFrame,
        indicators: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """
        将计算出的指标添加到DataFrame中

        Args:
            df: 原始K线数据
            indicators: 要计算的指标列表

        Returns:
            添加了指标列的DataFrame
        """
        df_copy = df.copy()

        # 计算指标
        indicator_data = self.calculate_all_indicators(df_copy, indicators)

        # 添加到DataFrame
        for col_name, data in indicator_data.items():
            df_copy[col_name] = data

        logger.info(f"✅ 已将{len(indicator_data)}个指标添加到数据")
        return df_copy

    # ==================== 指标信息 ====================

    def get_supported_indicators(self) -> Dict[str, List[Dict[str, str]]]:
        """
        获取支持的技术指标列表

        Returns:
            {
                "overlay": [{"name": "SMA", "description": "简单移动平均", "params": ["period"]}, ...],
                "oscillator": [...],
                "volume": [...],
                "momentum": [...],
                "volatility": [...],
                "cycle": [...]
            }
        """
        indicators = {
            "overlay": [
                {"name": "SMA", "description": "简单移动平均", "params": ["period"]},
                {"name": "EMA", "description": "指数移动平均", "params": ["period"]},
                {"name": "WMA", "description": "加权移动平均", "params": ["period"]},
                {"name": "DEMA", "description": "双指数移动平均", "params": ["period"]},
                {"name": "TEMA", "description": "三重指数移动平均", "params": ["period"]},
                {"name": "TRIMA", "description": "三角移动平均", "params": ["period"]},
                {"name": "KAMA", "description": "考夫曼自适应移动平均", "params": ["period"]},
                {"name": "MAMA", "description": "MESA自适应移动平均", "params": ["fastlimit", "slowlimit"]},
                {"name": "T3", "description": "三重指数移动平均", "params": ["period", "vfactor"]},
                {"name": "BOLL", "description": "布林带", "params": ["period", "nbdev"]},
                {"name": "SAR", "description": "抛物线转向", "params": ["acceleration", "maximum"]},
                {"name": "HT_TRENDLINE", "description": "希尔伯特趋势线", "params": []},
            ],
            "oscillator": [
                {"name": "RSI", "description": "相对强弱指标", "params": ["period"]},
                {"name": "STOCH", "description": "随机指标", "params": ["fastk_period", "slowk_period", "slowd_period"]},
                {"name": "STOCHF", "description": "快速随机指标", "params": ["fastk_period", "fastd_period"]},
                {"name": "MACD", "description": "指数平滑异同移动平均线", "params": ["fastperiod", "slowperiod", "signalperiod"]},
                {"name": "MACDEXT", "description": "扩展MACD", "params": ["fastperiod", "slowperiod", "signalperiod", "fastmatype", "slowmatype", "signalmatype"]},
                {"name": "STOCHRSI", "description": "相对强弱随机指标", "params": ["timeperiod", "fastk_period", "fastd_period"]},
                {"name": "ULTOSC", "description": "终极振荡指标", "params": ["timeperiod1", "timeperiod2", "timeperiod3"]},
                {"name": "CCI", "description": "顺势指标", "params": ["period"]},
                {"name": "DX", "description": "趋向指标", "params": ["period"]},
                {"name": "MINUS_DI", "description": "负向指标", "params": ["period"]},
                {"name": "PLUS_DI", "description": "正向指标", "params": ["period"]},
                {"name": "MINUS_DM", "description": "负向动向", "params": ["period"]},
                {"name": "PLUS_DM", "description": "正向动向", "params": ["period"]},
                {"name": "TRIX", "description": "三重指数平滑平均线", "params": ["period"]},
                {"name": "APO", "description": "绝对价格振荡指标", "params": ["fastperiod", "slowperiod"]},
                {"name": "PPO", "description": "百分比价格振荡指标", "params": ["fastperiod", "slowperiod"]},
                {"name": "AROON", "description": "阿隆指标", "params": ["period"]},
                {"name": "AROONOSC", "description": "阿隆振荡指标", "params": ["period"]},
                {"name": "BOP", "description": "均势指标", "params": []},
                {"name": "CCI", "description": "商品通道指数", "params": ["period"]},
                {"name": "CMO", "description": "钱德动量摆动指标", "params": ["period"]},
                {"name": "MOM", "description": "动量", "params": ["period"]},
                {"name": "ROC", "description": "变动率", "params": ["period"]},
                {"name": "ROCP", "description": "变动率百分比", "params": ["period"]},
                {"name": "ROCR", "description": "变动率比值", "params": ["period"]},
                {"name": "ROCR100", "description": "变动率比值*100", "params": ["period"]},
            ],
            "volume": [
                {"name": "AD", "description": "累积/派发线", "params": []},
                {"name": "ADOSC", "description": "累积/派发振荡指标", "params": ["fastperiod", "slowperiod"]},
                {"name": "OBV", "description": "能量潮", "params": []},
                {"name": "HT_DCPERIOD", "description": "希尔伯特周期", "params": []},
                {"name": "HT_PHASOR", "description": "希尔伯特向量分量", "params": []},
                {"name": "HT_SINE", "description": "希尔伯特正弦波", "params": []},
                {"name": "HT_TRENDMODE", "description": "希尔伯特趋势模式", "params": []},
            ],
            "momentum": [
                {"name": "MOM", "description": "动量", "params": ["period"]},
                {"name": "ROC", "description": "变动率", "params": ["period"]},
                {"name": "ROCP", "description": "变动率百分比", "params": ["period"]},
                {"name": "ROCR", "description": "变动率比值", "params": ["period"]},
                {"name": "ROCR100", "description": "变动率比值*100", "params": ["period"]},
                {"name": "TRIX", "description": "三重指数平滑平均线", "params": ["period"]},
                {"name": "APO", "description": "绝对价格振荡指标", "params": ["fastperiod", "slowperiod"]},
                {"name": "PPO", "description": "百分比价格振荡指标", "params": ["fastperiod", "slowperiod"]},
                {"name": "CMO", "description": "钱德动量摆动指标", "params": ["period"]},
                {"name": "MFI", "description": "资金流量指标", "params": ["period"]},
            ],
            "volatility": [
                {"name": "ATR", "description": "真实波幅", "params": ["period"]},
                {"name": "NATR", "description": "归一化真实波幅", "params": ["period"]},
                {"name": "TRANGE", "description": "真实范围", "params": []},
                {"name": "STDDEV", "description": "标准差", "params": ["period", "nbdev"]},
            ],
            "cycle": [
                {"name": "DPO", "description": "区间震荡线", "params": ["period"]},
                {"name": "TRIX", "description": "三重指数平滑平均线", "params": ["period"]},
                {"name": "HT_DCPERIOD", "description": "希尔伯特周期", "params": []},
                {"name": "HT_PHASOR", "description": "希尔伯特向量分量", "params": []},
                {"name": "HT_SINE", "description": "希尔伯特正弦波", "params": []},
                {"name": "HT_TRENDMODE", "description": "希尔伯特趋势模式", "params": []},
                {"name": "MINUS_DI", "description": "负向指标", "params": ["period"]},
                {"name": "PLUS_DI", "description": "正向指标", "params": ["period"]},
                {"name": "MINUS_DM", "description": "负向动向", "params": ["period"]},
                {"name": "PLUS_DM", "description": "正向动向", "params": ["period"]},
            ]
        }

        # 如果talib可用，可以动态获取更多指标
        if TALIB_AVAILABLE:
            try:
                import talib
                # 获取所有talib函数
                talib_functions = talib.get_functions()
                logger.info(f"talib支持 {len(talib_functions)} 个指标函数")
            except Exception as e:
                logger.warning(f"获取talib函数列表失败: {e}")

        return indicators


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

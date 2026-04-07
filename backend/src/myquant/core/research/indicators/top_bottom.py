# -*- coding: utf-8 -*-
"""
顶底背离指标（通达信公式版）

基于用户的通达信公式转换，核心功能：
1. 风险值指标（34/170/1020三个周期）
2. A02指标（短周期RSI变体）
3. MACD/KDJ/RSI 金叉死叉时的背离检测
4. 买卖信号点
"""

from typing import Dict
import pandas as pd
import numpy as np
from loguru import logger

from .base import BaseIndicator, TALIB_AVAILABLE

# 导入 talib（如果可用）
if TALIB_AVAILABLE:
    import talib

# 检查 scipy 是否可用
try:
    from scipy import signal as scipy_signal
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False
    logger.warning("scipy 不可用，RSI背离检测将使用简化版本")


class TopBottomIndicator(BaseIndicator):
    """顶底背离指标（通达信版）"""

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

    def calculate_a02(self, close: pd.Series, period: int = 7) -> pd.Series:
        """
        计算A02指标（通达信公式）

        A02:=SMA(MAX(CLOSE-VAR01,0),7,1)/SMA(ABS(CLOSE-VAR01),7,1)*100
        其中 VAR01:=REF(CLOSE,2)

        这实际上是一个RSI的变体，周期为7，但参考的是2天前的收盘价

        Args:
            close: 收盘价序列
            period: 计算周期（默认7）

        Returns:
            A02指标序列（0-100）
        """
        # VAR01:=REF(CLOSE,2)
        var01 = close.shift(2)

        # MAX(CLOSE-VAR01,0)
        gain = (close - var01).clip(lower=0)

        # ABS(CLOSE-VAR01)
        change = (close - var01).abs()

        # SMA(MACD, period, 1) 通达信的SMA实际上是EMA
        avg_gain = gain.ewm(alpha=1/period, adjust=False).mean()
        avg_change = change.ewm(alpha=1/period, adjust=False).mean()

        # 避免除零
        a02 = (avg_gain / avg_change.replace(0, np.nan)) * 100

        return a02

    def detect_rsi_divergence(
        self,
        price: pd.Series,
        rsi: pd.Series,
        lookback: int = 20
    ) -> Dict[str, pd.Series]:
        """
        检测RSI背离（基于峰值和谷值）

        底背离：价格创新低，但RSI低点抬高
        顶背离：价格创新高，但RSI高点降低

        Args:
            price: 价格序列
            rsi: RSI序列
            lookback: 峰值/谷值检测窗口

        Returns:
            {
                'top_divergence': 顶背离信号序列
                'bottom_divergence': 底背离信号序列
            }
        """
        top_div = pd.Series(0, index=price.index)
        bottom_div = pd.Series(0, index=price.index)

        if len(price) < lookback * 2:
            return {'top_divergence': top_div, 'bottom_divergence': bottom_div}

        if SCIPY_AVAILABLE:
            # 使用 scipy 检测峰值和谷值
            # 价格的峰值和谷值
            price_peaks = scipy_signal.find_peaks(price.values, distance=lookback)[0]
            price_valleys = scipy_signal.find_peaks(-price.values, distance=lookback)[0]

            # RSI的峰值和谷值
            rsi_peaks = scipy_signal.find_peaks(rsi.values, distance=lookback)[0]
            rsi_valleys = scipy_signal.find_peaks(-rsi.values, distance=lookback)[0]

            # 检测顶背离（价格创新高，RSI高点降低）
            for i in range(len(price_peaks) - 1):
                curr_peak_idx = price_peaks[i + 1]
                prev_peak_idx = price_peaks[i]

                if curr_peak_idx >= len(price) or prev_peak_idx >= len(price):
                    continue

                # 价格创新高
                if price.iloc[curr_peak_idx] > price.iloc[prev_peak_idx]:
                    # 找到对应位置的RSI峰值
                    nearby_rsi_peaks = [p for p in rsi_peaks if abs(p - curr_peak_idx) <= 5]
                    if nearby_rsi_peaks:
                        rsi_peak_idx = nearby_rsi_peaks[0]
                        # 找前一个RSI峰值
                        prev_rsi_peaks = [p for p in rsi_peaks if p < rsi_peak_idx - 5]
                        if prev_rsi_peaks:
                            prev_rsi_peak_idx = prev_rsi_peaks[-1]
                            # RSI高点降低 -> 顶背离
                            if rsi.iloc[rsi_peak_idx] < rsi.iloc[prev_rsi_peak_idx]:
                                top_div.iloc[curr_peak_idx] = 1
                                logger.info(f"RSI顶背离 @{curr_peak_idx}: 价格创新高 {price.iloc[curr_peak_idx]:.2f}, RSI降低 {rsi.iloc[rsi_peak_idx]:.2f} -> {rsi.iloc[prev_rsi_peak_idx]:.2f}")

            # 检测底背离（价格创新低，RSI低点抬高）
            for i in range(len(price_valleys) - 1):
                curr_valley_idx = price_valleys[i + 1]
                prev_valley_idx = price_valleys[i]

                if curr_valley_idx >= len(price) or prev_valley_idx >= len(price):
                    continue

                # 价格创新低
                if price.iloc[curr_valley_idx] < price.iloc[prev_valley_idx]:
                    # 找到对应位置的RSI谷值
                    nearby_rsi_valleys = [v for v in rsi_valleys if abs(v - curr_valley_idx) <= 5]
                    if nearby_rsi_valleys:
                        rsi_valley_idx = nearby_rsi_valleys[0]
                        # 找前一个RSI谷值
                        prev_rsi_valleys = [v for v in rsi_valleys if v < rsi_valley_idx - 5]
                        if prev_rsi_valleys:
                            prev_rsi_valley_idx = prev_rsi_valleys[-1]
                            # RSI低点抬高 -> 底背离
                            if rsi.iloc[rsi_valley_idx] > rsi.iloc[prev_rsi_valley_idx]:
                                bottom_div.iloc[curr_valley_idx] = 1
                                logger.info(f"RSI底背离 @{curr_valley_idx}: 价格创新低 {price.iloc[curr_valley_idx]:.2f}, RSI抬高 {rsi.iloc[rsi_valley_idx]:.2f} -> {rsi.iloc[prev_rsi_valley_idx]:.2f}")

        else:
            # 简化版本：手动检测峰值和谷值
            # 检测价格峰值：比前lookback根和后lookback根都高
            for i in range(lookback, len(price) - lookback):
                # 检查是否为价格峰值
                is_price_peak = True
                for j in range(i - lookback, i + lookback + 1):
                    if j != i and price.iloc[j] >= price.iloc[i]:
                        is_price_peak = False
                        break

                if is_price_peak and i >= lookback * 2:
                    # 找到上一个峰值
                    prev_peak_found = False
                    for j in range(i - lookback * 2, i):
                        is_prev_peak = True
                        for k in range(j - lookback, j + lookback + 1):
                            if k != j and price.iloc[k] >= price.iloc[j]:
                                is_prev_peak = False
                                break
                        if is_prev_peak:
                            prev_peak_found = True
                            # 价格创新高，检查RSI
                            if price.iloc[i] > price.iloc[j]:
                                # 检查RSI是否降低
                                if rsi.iloc[i] < rsi.iloc[j]:
                                    top_div.iloc[i] = 1
                                    logger.info(f"RSI顶背离(简化) @{i}: 价格{price.iloc[i]:.2f} > {price.iloc[j]:.2f}, RSI {rsi.iloc[i]:.2f} < {rsi.iloc[j]:.2f}")
                            break

                # 检查是否为价格谷值
                is_price_valley = True
                for j in range(i - lookback, i + lookback + 1):
                    if j != i and price.iloc[j] <= price.iloc[i]:
                        is_price_valley = False
                        break

                if is_price_valley and i >= lookback * 2:
                    # 找到上一个谷值
                    prev_valley_found = False
                    for j in range(i - lookback * 2, i):
                        is_prev_valley = True
                        for k in range(j - lookback, j + lookback + 1):
                            if k != j and price.iloc[k] <= price.iloc[j]:
                                is_prev_valley = False
                                break
                        if is_prev_valley:
                            prev_valley_found = True
                            # 价格创新低，检查RSI
                            if price.iloc[i] < price.iloc[j]:
                                # 检查RSI是否抬高
                                if rsi.iloc[i] > rsi.iloc[j]:
                                    bottom_div.iloc[i] = 1
                                    logger.info(f"RSI底背离(简化) @{i}: 价格{price.iloc[i]:.2f} < {price.iloc[j]:.2f}, RSI {rsi.iloc[i]:.2f} > {rsi.iloc[j]:.2f}")
                            break

        logger.info(f"RSI背离检测: 顶背离{top_div.sum()}次, 底背离{bottom_div.sum()}次")

        return {
            'top_divergence': top_div,
            'bottom_divergence': bottom_div
        }

    def detect_divergence(
        self,
        price: pd.Series,
        indicator: pd.Series,
        signal_line: pd.Series = None,
        lookback: int = 100
    ) -> Dict[str, pd.Series]:
        """
        检测背离信号（通达信风格：金叉/死叉时的背离）

        MACD底背离公式：
        A1:=BARSLAST(REF(CROSS("MACD.DIF","MACD.DEA"),1));
        B1:=REF(C,A1+1)> C AND REF("MACD.DIF",A1+1)< "MACD.DIF" AND CROSS("MACD.DIF","MACD.DEA");

        底背离：上次金叉时价格更高，指标更低；现在又金叉了
        顶背离：上次死叉时价格更低，指标更高；现在又死叉了

        Args:
            price: 价格序列
            indicator: 指标序列（如DIF、K、RSI）
            signal_line: 信号线序列（如DEA、D），用于判断金叉死叉
            lookback: 最大回溯K线数

        Returns:
            {
                'top_divergence': 顶背离信号序列（1=有顶背离）
                'bottom_divergence': 底背离信号序列（1=有底背离）
            }
        """
        top_div = pd.Series(0, index=price.index)
        bottom_div = pd.Series(0, index=price.index)

        if len(price) < 10:
            return {'top_divergence': top_div, 'bottom_divergence': bottom_div}

        # 如果没有提供信号线，用指标自身判断交叉
        if signal_line is None:
            # 对于RSI等没有信号线的指标，用固定阈值判断
            # 这里简化处理：直接用指标与自身的移动平均比较
            signal_line = indicator.rolling(window=3).mean()

        # 记录历史金叉和死叉位置
        golden_crosses = []  # [(index, price, indicator_value)]
        death_crosses = []   # [(index, price, indicator_value)]

        for i in range(1, len(price)):
            curr_price = price.iloc[i]
            curr_ind = indicator.iloc[i]
            curr_signal = signal_line.iloc[i]
            prev_price = price.iloc[i-1]
            prev_ind = indicator.iloc[i-1]
            prev_signal = signal_line.iloc[i-1]

            if pd.isna(curr_price) or pd.isna(curr_ind) or pd.isna(curr_signal):
                continue
            if pd.isna(prev_price) or pd.isna(prev_ind) or pd.isna(prev_signal):
                continue

            # 当前金叉：指标上穿信号线
            if prev_ind <= prev_signal and curr_ind > curr_signal:
                # 检查底背离：与上一次金叉比较
                if len(golden_crosses) > 0:
                    last_idx, last_price, last_ind = golden_crosses[-1]

                    # 底背离：上次金叉时价格更高，指标更低
                    if last_price > curr_price and last_ind < curr_ind:
                        bottom_div.iloc[i] = 1
                        msg = (f"MACD底背离 @ {i}: 上次金叉@{last_idx} "
                               f"价格{last_price:.2f} 指标{last_ind:.4f} -> "
                               f"本次金叉 价格{curr_price:.2f} 指标{curr_ind:.4f}")
                        logger.info(msg)

                golden_crosses.append((i, curr_price, curr_ind))

            # 当前死叉：指标下穿信号线
            if prev_ind >= prev_signal and curr_ind < curr_signal:
                # 检查顶背离：与上一次死叉比较
                if len(death_crosses) > 0:
                    last_idx, last_price, last_ind = death_crosses[-1]

                    # 顶背离：上次死叉时价格更低，指标更高
                    if last_price < curr_price and last_ind > curr_ind:
                        top_div.iloc[i] = 1
                        msg = (f"MACD顶背离 @ {i}: 上次死叉@{last_idx} "
                               f"价格{last_price:.2f} 指标{last_ind:.4f} -> "
                               f"本次死叉 价格{curr_price:.2f} 指标{curr_ind:.4f}")
                        logger.info(msg)

                death_crosses.append((i, curr_price, curr_ind))

        logger.info(f"MACD背离检测: 金叉{len(golden_crosses)}次, 死叉{len(death_crosses)}次, 顶背离{top_div.sum()}次, 底背离{bottom_div.sum()}次")

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
        - A02指标
        - MACD/KDJ/RSI用于背离检测
        - 综合买卖信号

        Returns:
            {
                'risk_value_34': 风险值34
                'risk_value_170': 风险值170
                'risk_value_1020': 风险值1020
                'a02': A02指标
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
        # 计算风险值（直接用170和1020，不是34*5和34*30）
        risk_34 = self.calculate_risk_value(high, low, close, period=34, ema_period=3)
        risk_170 = self.calculate_risk_value(high, low, close, period=170, ema_period=6)
        risk_1020 = self.calculate_risk_value(high, low, close, period=1020, ema_period=15)

        # 计算A02指标
        a02 = self.calculate_a02(close, period=7)

        # 计算MACD
        if self.available:
            macd, macd_dea, macd_hist = talib.MACD(
                close.values,
                fastperiod=macd_fast,
                slowperiod=macd_slow,
                signalperiod=macd_signal
            )
            macd_line = pd.Series(macd, index=close.index)
            macd_dea = pd.Series(macd_dea, index=close.index)
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

        # 计算RSI（6日周期，更灵敏）
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=6).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=6).mean()
        rs = gain / loss.replace(0, np.nan)
        wrsi = 100 - (100 / (1 + rs))

        # 检测背离（金叉/死叉时）
        macd_div = self.detect_divergence(close, macd_line, macd_dea)
        kdj_div = self.detect_divergence(close, k, d)
        # RSI使用专门的峰值/谷值背离检测
        rsi_div = self.detect_rsi_divergence(close, wrsi)

        # 综合买卖信号
        buy_signal = pd.Series(0, index=close.index)
        sell_signal = pd.Series(0, index=close.index)

        # 风险值上穿/下穿检测
        risk_prev = risk_34.shift(1)
        # 上穿20：前一根<=20，当前>20
        risk_cross_up_20 = (risk_prev <= 20) & (risk_34 > 20)
        # 下穿80：前一根>=80，当前<80
        risk_cross_down_80 = (risk_prev >= 80) & (risk_34 < 80)

        # 买入条件：风险值上穿20 + 底背离确认 + 趋势向上
        buy_conditions = (
            # 1. 风险值上穿20（从超卖区反转）
            risk_cross_up_20 &
            # 2. 最近10根K线内有底背离（确认）
            (
                (macd_div['bottom_divergence'].rolling(10).max() == 1) |
                (kdj_div['bottom_divergence'].rolling(10).max() == 1) |
                (rsi_div['bottom_divergence'].rolling(10).max() == 1)
            ) &
            # 3. MACD向上（趋势确认）
            (macd_line.diff() > 0)
        )
        buy_signal = buy_conditions.astype(int)

        # 卖出条件：风险值下穿80 + 顶背离确认 + 趋势向下
        sell_conditions = (
            # 1. 风险值下穿80（从超买区反转）
            risk_cross_down_80 &
            # 2. 最近10根K线内有顶背离（确认）
            (
                (macd_div['top_divergence'].rolling(10).max() == 1) |
                (kdj_div['top_divergence'].rolling(10).max() == 1) |
                (rsi_div['top_divergence'].rolling(10).max() == 1)
            ) &
            # 3. A02高位或MACD向下（确认）
            ((a02 > 70) | (macd_line.diff() < 0))
        )
        sell_signal = sell_conditions.astype(int)

        return {
            'risk_value_34': risk_34,
            'risk_value_170': risk_170,
            'risk_value_1020': risk_1020,
            'a02': a02,
            'macd_div_top': macd_div['top_divergence'],
            'macd_div_bottom': macd_div['bottom_divergence'],
            'kdj_div_top': kdj_div['top_divergence'],
            'kdj_div_bottom': kdj_div['bottom_divergence'],
            'rsi_div_top': rsi_div['top_divergence'],
            'rsi_div_bottom': rsi_div['bottom_divergence'],
            'buy_signal': buy_signal,
            'sell_signal': sell_signal
        }

# -*- coding: utf-8 -*-
"""
SMC (Smart Money Concepts) V2 指标计算服务

基于 ICT (Inner Circle Trader) 理论的智能货币概念指标
参考: TradingView Zeiierman SMC / LuxAlgo SMC

核心功能:
- Swing Points: 摆动高低点检测 (HH/HL/LL/LH)
- BMS (Break of Market Structure): 结构突破标记
- CHoCH (Change of Character): 特征改变标记
- Order Blocks: 订单块检测
- FVG (Fair Value Gap): 公平价值缺口
- Liquidity Grabs: 流动性抓取

V2 升级:
- 更清晰的摆动点标签
- 更精确的 BMS/CHoCH 检测
- 供需区域渲染优化
- 支持更多配置参数

作者: MyQuant v11 Team
版本: 2.0
"""

from typing import Dict, List, Optional, Tuple, Any, NamedTuple
from dataclasses import dataclass, field
from loguru import logger
import pandas as pd
import numpy as np


@dataclass
class SwingPoint:
    """摆动点数据结构"""
    index: int
    price: float
    type: str  # 'high' | 'low'
    label: str = ''  # HH, HL, LL, LH


@dataclass
class StructureBreak:
    """结构突破事件"""
    index: int      # 被突破的摆动点索引（起点）
    end_index: int  # 突破发生的 K 线索引（终点）
    level: float    # 被突破的摆动点价格
    type: str       # 'BMS' | 'CHoCH'
    direction: str  # 'bullish' | 'bearish'


@dataclass
class OrderBlock:
    """订单块数据结构"""
    index: int
    top: float
    bottom: float
    type: str  # 'bullish' | 'bearish'
    mitigated: bool = False
    mitigation_time: Optional[int] = None


@dataclass
class FVGZone:
    """FVG 区域数据结构"""
    index: int
    top: float
    bottom: float
    type: str  # 'bullish' | 'bearish'
    filled: bool = False


class SMCServiceV2:
    """
    SMC V2 指标计算服务

    改进:
    1. 更严格的摆动点检测
    2. 区分 BOS (趋势延续) 和 CHoCH (趋势反转)
    3. 优化的订单块和 FVG 检测
    4. 更好的数据结构支持前端渲染
    """

    def __init__(self):
        """初始化 SMC V2 服务"""
        logger.info("SMCServiceV2 初始化完成")

    # ==================== 摆动点检测 V2 ====================

    def detect_swing_points(
        self,
        df: pd.DataFrame,
        swing_length: int = 5,
        strict_mode: bool = False
    ) -> List[SwingPoint]:
        """
        检测摆动高低点 (V2 改进版)

        Args:
            df: OHLC 数据
            swing_length: 摆动检测周期
            strict_mode: 严格模式 (要求严格高于/低于，不允许相等)

        Returns:
            SwingPoint 列表
        """
        high = df['high'].values
        low = df['low'].values
        n = len(df)

        swing_points = []

        for i in range(swing_length, n - swing_length):
            # 左侧和右侧的高低点
            left_highs = high[i - swing_length:i]
            right_highs = high[i + 1:i + swing_length + 1]
            left_lows = low[i - swing_length:i]
            right_lows = low[i + 1:i + swing_length + 1]

            # 检测摆动高点
            if strict_mode:
                is_swing_high = high[i] > np.max(left_highs) and high[i] > np.max(right_highs)
            else:
                is_swing_high = high[i] >= np.max(left_highs) and high[i] >= np.max(right_highs)

            if is_swing_high:
                swing_points.append(SwingPoint(
                    index=i,
                    price=high[i],
                    type='high',
                    label=''
                ))
                continue

            # 检测摆动低点
            if strict_mode:
                is_swing_low = low[i] < np.min(left_lows) and low[i] < np.min(right_lows)
            else:
                is_swing_low = low[i] <= np.min(left_lows) and low[i] <= np.min(right_lows)

            if is_swing_low:
                swing_points.append(SwingPoint(
                    index=i,
                    price=low[i],
                    type='low',
                    label=''
                ))

        return swing_points

    def label_swing_structure(
        self,
        swing_points: List[SwingPoint]
    ) -> List[SwingPoint]:
        """
        为摆动点标注 HH/HL/LL/LH 标签

        Args:
            swing_points: 摆动点列表

        Returns:
            带标签的摆动点列表
        """
        if len(swing_points) < 2:
            return swing_points

        # 分离高点和低点
        highs = [s for s in swing_points if s.type == 'high']
        lows = [s for s in swing_points if s.type == 'low']

        # 标注高点
        for i, h in enumerate(highs):
            if i == 0:
                h.label = 'SH'  # 起始高点
            else:
                prev_high = highs[i - 1]
                if h.price > prev_high.price:
                    h.label = 'HH'  # 更高高点
                else:
                    h.label = 'LH'  # 更低高点

        # 标注低点
        for i, l in enumerate(lows):
            if i == 0:
                l.label = 'SL'  # 起始低点
            else:
                prev_low = lows[i - 1]
                if l.price > prev_low.price:
                    l.label = 'HL'  # 更高低点
                else:
                    l.label = 'LL'  # 更低低点

        return swing_points

    def identify_trend(
        self,
        swing_points: List[SwingPoint]
    ) -> str:
        """
        根据摆动点识别当前趋势

        Returns:
            'bullish' | 'bearish' | 'neutral'
        """
        if len(swing_points) < 2:
            return 'neutral'

        # 取最近的摆动点
        recent_swings = swing_points[-4:]  # 最近4个摆动点

        hh_count = sum(1 for s in recent_swings if s.label == 'HH')
        hl_count = sum(1 for s in recent_swings if s.label == 'HL')
        lh_count = sum(1 for s in recent_swings if s.label == 'LH')
        ll_count = sum(1 for s in recent_swings if s.label == 'LL')

        bullish_signals = hh_count + hl_count
        bearish_signals = lh_count + ll_count

        if bullish_signals > bearish_signals:
            return 'bullish'
        elif bearish_signals > bullish_signals:
            return 'bearish'
        return 'neutral'

    # ==================== BMS (Break of Structure) V2 ====================

    def detect_bms(
        self,
        df: pd.DataFrame,
        swing_points: List[SwingPoint],
        close_break: bool = True
    ) -> List[StructureBreak]:
        """
        检测 BMS (Break of Market Structure) - 市场结构突破

        BMS 表示趋势延续:
        - 看涨 BMS: 在上升趋势中，价格突破前一个 HH
        - 看跌 BMS: 在下降趋势中，价格跌破前一个 LL

        Args:
            df: OHLC 数据
            swing_points: 摆动点列表
            close_break: 是否要求收盘价突破

        Returns:
            StructureBreak 列表
        """
        breaks = []
        close = df['close'].values
        high = df['high'].values
        low = df['low'].values

        # 分离高低点
        highs = [s for s in swing_points if s.type == 'high']
        lows = [s for s in swing_points if s.type == 'low']

        # 检测看涨 BMS (突破 HH)
        for i in range(1, len(highs)):
            curr = highs[i]
            prev = highs[i - 1]

            # BMS 是趋势延续：突破 HH (更高高点)
            # 即 prev.label 必须是 HH，表示这是一个趋势延续的突破
            if prev.label != 'HH':
                continue

            # 找到实际突破发生的 K 线索引
            # 从 prev.index+1 开始遍历到 curr.index，找到第一个突破 prev.price 的 K 线
            break_idx = None
            for idx in range(prev.index + 1, min(curr.index + 1, len(close))):
                if close_break:
                    if close[idx] > prev.price:
                        break_idx = idx
                        break
                else:
                    if high[idx] > prev.price:
                        break_idx = idx
                        break

            if break_idx is not None:
                # BMS 标记在**被突破的前一个高点** (prev.index)
                # 水平线从 prev.index 画到 break_idx (实际突破发生的 K 线)
                breaks.append(StructureBreak(
                    index=prev.index,      # 起点：被突破的前高点
                    end_index=break_idx,   # 终点：实际突破发生的 K 线索引
                    level=prev.price,
                    type='BMS',
                    direction='bullish'
                ))

        # 检测看跌 BMS (跌破 LL)
        for i in range(1, len(lows)):
            curr = lows[i]
            prev = lows[i - 1]

            # BMS 是趋势延续：跌破 LL (更低低点)
            # 即 prev.label 必须是 LL，表示这是一个趋势延续的跌破
            if prev.label != 'LL':
                continue

            # 找到实际跌破发生的 K 线索引
            break_idx = None
            for idx in range(prev.index + 1, min(curr.index + 1, len(close))):
                if close_break:
                    if close[idx] < prev.price:
                        break_idx = idx
                        break
                else:
                    if low[idx] < prev.price:
                        break_idx = idx
                        break

            if break_idx is not None:
                # BMS 标记在**被突破的前一个低点** (prev.index)
                # 水平线从 prev.index 画到 break_idx (实际跌破发生的 K 线)
                breaks.append(StructureBreak(
                    index=prev.index,      # 起点：被突破的前低点
                    end_index=break_idx,   # 终点：实际跌破发生的 K 线索引
                    level=prev.price,
                    type='BMS',
                    direction='bearish'
                ))

        return breaks

    # ==================== CHoCH (Change of Character) V2 ====================

    def detect_choch(
        self,
        df: pd.DataFrame,
        swing_points: List[SwingPoint],
        close_break: bool = True
    ) -> List[StructureBreak]:
        """
        检测 CHoCH (Change of Character) - 特征改变

        CHoCH 表示趋势可能反转:
        - 看涨 CHoCH: 在下降趋势中，价格突破前一个 LH
        - 看跌 CHoCH: 在上升趋势中，价格跌破前一个 HL

        Args:
            df: OHLC 数据
            swing_points: 摆动点列表
            close_break: 是否要求收盘价突破

        Returns:
            StructureBreak 列表
        """
        breaks = []
        close = df['close'].values
        high = df['high'].values
        low = df['low'].values

        # 分离高低点
        highs = [s for s in swing_points if s.type == 'high']
        lows = [s for s in swing_points if s.type == 'low']

        # 检测看涨 CHoCH (突破 LH - 更低高点)
        for i in range(1, len(highs)):
            curr = highs[i]
            prev = highs[i - 1]

            # CHoCH 是突破 LH (更低高点)
            if prev.label != 'LH':
                continue

            # 找到实际突破发生的 K 线索引
            break_idx = None
            for idx in range(prev.index + 1, min(curr.index + 1, len(close))):
                if close_break:
                    if close[idx] > prev.price:
                        break_idx = idx
                        break
                else:
                    if high[idx] > prev.price:
                        break_idx = idx
                        break

            if break_idx is not None:
                # CHoCH 标记在**被突破的前一个 LH** (prev.index)
                # 水平线从 prev.index 画到 break_idx (实际突破发生的 K 线)
                breaks.append(StructureBreak(
                    index=prev.index,      # 起点：被突破的 LH
                    end_index=break_idx,   # 终点：实际突破发生的 K 线索引
                    level=prev.price,
                    type='CHoCH',
                    direction='bullish'
                ))

        # 检测看跌 CHoCH (跌破 HL - 更高低点)
        for i in range(1, len(lows)):
            curr = lows[i]
            prev = lows[i - 1]

            # CHoCH 是跌破 HL (更高低点)
            if prev.label != 'HL':
                continue

            # 找到实际跌破发生的 K 线索引
            break_idx = None
            for idx in range(prev.index + 1, min(curr.index + 1, len(close))):
                if close_break:
                    if close[idx] < prev.price:
                        break_idx = idx
                        break
                else:
                    if low[idx] < prev.price:
                        break_idx = idx
                        break

            if break_idx is not None:
                # CHoCH 标记在**被突破的前一个 HL** (prev.index)
                # 水平线从 prev.index 画到 break_idx (实际跌破发生的 K 线)
                breaks.append(StructureBreak(
                    index=prev.index,      # 起点：被突破的 HL
                    end_index=break_idx,   # 终点：实际跌破发生的 K 线索引
                    level=prev.price,
                    type='CHoCH',
                    direction='bearish'
                ))

        return breaks

    # ==================== Order Blocks V2 ====================

    def detect_order_blocks(
        self,
        df: pd.DataFrame,
        breaks: List[StructureBreak],
        max_blocks: int = 10,
        min_imbalance: float = 0.5
    ) -> List[OrderBlock]:
        """
        检测 Order Blocks (订单块)

        订单块是导致价格突破的关键 K 线:
        - 看涨 OB: 上升趋势中，导致突破的最后一根下跌 K 线
        - 看跌 OB: 下降趋势中，导致突破的最后一根上涨 K 线

        Args:
            df: OHLC 数据
            breaks: BMS/CHoCH 突破列表
            max_blocks: 最大保留数量
            min_imbalance: 最小不平衡度 (%)

        Returns:
            OrderBlock 列表
        """
        blocks = []
        open_price = df['open'].values
        high = df['high'].values
        low = df['low'].values
        close = df['close'].values

        for break_event in breaks:
            break_idx = break_event.index
            direction = break_event.direction

            # 回溯找订单块 (最多回溯 20 根 K 线)
            for j in range(break_idx - 1, max(0, break_idx - 20), -1):
                candle_open = open_price[j]
                candle_close = close[j]
                candle_high = high[j]
                candle_low = low[j]

                is_bullish_candle = candle_close > candle_open
                is_bearish_candle = candle_close < candle_open

                if direction == 'bullish':
                    # 看涨 OB: 找最后一根下跌 K 线
                    if is_bearish_candle:
                        # 计算不平衡度
                        body_size = abs(candle_close - candle_open)
                        wick_size = candle_high - candle_open
                        imbalance = (wick_size / body_size * 100) if body_size > 0 else 0

                        if imbalance >= min_imbalance or True:  # 暂时不检查
                            blocks.append(OrderBlock(
                                index=j,
                                top=candle_open,
                                bottom=candle_close,
                                type='bullish',
                                mitigated=False
                            ))
                        break
                else:
                    # 看跌 OB: 找最后一根上涨 K 线
                    if is_bullish_candle:
                        body_size = abs(candle_close - candle_open)
                        wick_size = candle_low - candle_open
                        imbalance = (wick_size / body_size * 100) if body_size > 0 else 0

                        if imbalance >= min_imbalance or True:
                            blocks.append(OrderBlock(
                                index=j,
                                top=candle_close,
                                bottom=candle_open,
                                type='bearish',
                                mitigated=False
                            ))
                        break

        # 按时间排序，取最近的
        blocks.sort(key=lambda b: b.index)
        return blocks[-max_blocks:] if len(blocks) > max_blocks else blocks

    # ==================== FVG V2 ====================

    def detect_fvg(
        self,
        df: pd.DataFrame,
        min_gap_pct: float = 0.3,
        max_lookback: int = 3
    ) -> List[FVGZone]:
        """
        检测 FVG (Fair Value Gap) - 公平价值缺口

        FVG 是价格失衡区域:
        - 看涨 FVG: candle3.low > candle1.high
        - 看跌 FVG: candle3.high < candle1.low

        Args:
            df: OHLC 数据
            min_gap_pct: 最小缺口百分比
            max_lookback: 最大回看周期

        Returns:
            FVGZone 列表
        """
        fvgs = []
        high = df['high'].values
        low = df['low'].values
        close = df['close'].values
        n = len(df)

        for i in range(2, n):
            candle1_high = high[i - 2]
            candle1_low = low[i - 2]
            candle2_close = close[i - 1]
            candle3_high = high[i]
            candle3_low = low[i]

            # 看涨 FVG: candle3.low > candle1.high
            if candle3_low > candle1_high:
                gap_size = candle3_low - candle1_high
                gap_pct = (gap_size / candle2_close) * 100

                if gap_pct >= min_gap_pct:
                    fvgs.append(FVGZone(
                        index=i - 1,  # FVG 标记在中间 K 线
                        top=candle3_low,
                        bottom=candle1_high,
                        type='bullish',
                        filled=False
                    ))

            # 看跌 FVG: candle3.high < candle1.low
            elif candle3_high < candle1_low:
                gap_size = candle1_low - candle3_high
                gap_pct = (gap_size / candle2_close) * 100

                if gap_pct >= min_gap_pct:
                    fvgs.append(FVGZone(
                        index=i - 1,
                        top=candle1_low,
                        bottom=candle3_high,
                        type='bearish',
                        filled=False
                    ))

        return fvgs

    # ==================== 统一入口 V2 ====================

    def calculate_all(
        self,
        df: pd.DataFrame,
        swing_length: int = 5,
        close_break: bool = True,
        show_ob: bool = True,
        show_fvg: bool = True,
        max_ob_count: int = 10,
        max_fvg_count: int = 10
    ) -> Dict[str, Any]:
        """
        计算 SMC V2 指标

        Args:
            df: OHLC 数据
            swing_length: 摆动检测周期
            close_break: 是否要求收盘价突破
            show_ob: 是否显示订单块
            show_fvg: 是否显示 FVG
            max_ob_count: 最大订单块数量
            max_fvg_count: 最大 FVG 数量

        Returns:
            SMC V2 指标数据字典
        """
        if df is None or len(df) < swing_length * 2 + 1:
            logger.warning(f"SMC V2 数据不足: {len(df) if df is not None else 0}")
            return {}

        try:
            n = len(df)

            # 1. 摆动点检测和标注
            swing_points = self.detect_swing_points(df, swing_length)
            swing_points = self.label_swing_structure(swing_points)

            # 2. 识别趋势
            trend = self.identify_trend(swing_points)

            # 3. BMS 检测 (趋势延续)
            bms_list = self.detect_bms(df, swing_points, close_break)

            # 4. CHoCH 检测 (趋势反转)
            choch_list = self.detect_choch(df, swing_points, close_break)

            # 5. 合并突破事件
            all_breaks = bms_list + choch_list

            # 6. Order Blocks
            ob_list = []
            if show_ob:
                ob_list = self.detect_order_blocks(df, all_breaks, max_ob_count)

            # 7. FVG
            fvg_list = []
            if show_fvg:
                fvg_list = self.detect_fvg(df)
                if len(fvg_list) > max_fvg_count:
                    fvg_list = fvg_list[-max_fvg_count:]

            # 8. 转换为与 K 线对齐的数组格式
            result = self._convert_to_arrays(
                n, swing_points, bms_list, choch_list, ob_list, fvg_list
            )

            # 添加趋势信息
            result['trend'] = trend

            logger.debug(f"SMC V2 计算完成: trend={trend}, "
                        f"swings={len(swing_points)}, BMS={len(bms_list)}, "
                        f"CHoCH={len(choch_list)}, OB={len(ob_list)}, FVG={len(fvg_list)}")

            return result

        except Exception as e:
            logger.error(f"SMC V2 计算失败: {e}")
            import traceback
            traceback.print_exc()
            return {}

    def _convert_to_arrays(
        self,
        n: int,
        swing_points: List[SwingPoint],
        bms_list: List[StructureBreak],
        choch_list: List[StructureBreak],
        ob_list: List[OrderBlock],
        fvg_list: List[FVGZone]
    ) -> Dict[str, Any]:
        """
        将数据结构转换为与 K 线对齐的数组
        """
        # 初始化数组
        swing_highs = [None] * n
        swing_lows = [None] * n
        swing_labels = [None] * n
        swing_types = [0] * n  # 1=high, -1=low

        bms = [0] * n
        bms_levels = [None] * n
        bms_directions = [None] * n
        bms_end_index = [None] * n  # 突破发生的 K 线索引

        choch = [0] * n
        choch_levels = [None] * n
        choch_directions = [None] * n
        choch_end_index = [None] * n  # 突破发生的 K 线索引

        ob_type = [0] * n
        ob_top = [None] * n
        ob_bottom = [None] * n

        fvg_type = [0] * n
        fvg_top = [None] * n
        fvg_bottom = [None] * n

        # 填充摆动点
        for sp in swing_points:
            if sp.type == 'high':
                swing_highs[sp.index] = sp.price
                swing_types[sp.index] = 1
            else:
                swing_lows[sp.index] = sp.price
                swing_types[sp.index] = -1
            swing_labels[sp.index] = sp.label

        # 填充 BMS
        for b in bms_list:
            bms[b.index] = 1 if b.direction == 'bullish' else -1
            bms_levels[b.index] = b.level
            bms_directions[b.index] = b.direction
            bms_end_index[b.index] = b.end_index

        # 填充 CHoCH
        for c in choch_list:
            choch[c.index] = 1 if c.direction == 'bullish' else -1
            choch_levels[c.index] = c.level
            choch_directions[c.index] = c.direction
            choch_end_index[c.index] = c.end_index

        # 填充 OB
        for ob in ob_list:
            ob_type[ob.index] = 1 if ob.type == 'bullish' else -1
            ob_top[ob.index] = ob.top
            ob_bottom[ob.index] = ob.bottom

        # 填充 FVG
        for fvg in fvg_list:
            fvg_type[fvg.index] = 1 if fvg.type == 'bullish' else -1
            fvg_top[fvg.index] = fvg.top
            fvg_bottom[fvg.index] = fvg.bottom

        return {
            'swing_highs': swing_highs,
            'swing_lows': swing_lows,
            'swing_labels': swing_labels,
            'swing_types': swing_types,

            'bms': bms,
            'bms_levels': bms_levels,
            'bms_directions': bms_directions,
            'bms_end_index': bms_end_index,

            'choch': choch,
            'choch_levels': choch_levels,
            'choch_directions': choch_directions,
            'choch_end_index': choch_end_index,

            'ob_type': ob_type,
            'ob_top': ob_top,
            'ob_bottom': ob_bottom,

            'fvg_type': fvg_type,
            'fvg_top': fvg_top,
            'fvg_bottom': fvg_bottom,

            'version': '2.0'
        }


# ==================== 单例 ====================

_smc_service_v2: Optional[SMCServiceV2] = None


def get_smc_service_v2() -> SMCServiceV2:
    """获取 SMC V2 服务单例"""
    global _smc_service_v2
    if _smc_service_v2 is None:
        _smc_service_v2 = SMCServiceV2()
    return _smc_service_v2


# 保持向后兼容
SMCService = SMCServiceV2
get_smc_service = get_smc_service_v2

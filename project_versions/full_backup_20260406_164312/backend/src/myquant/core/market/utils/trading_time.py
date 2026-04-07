# -*- coding: utf-8 -*-
"""
交易时间判断工具 (V5)

用于判断当前是否在交易时间，从而选择最优的数据获取API

迁移自: backend/data/utils/trading_time.py
"""

from datetime import datetime, time
from enum import Enum


class TimePhase(Enum):
    """时段枚举"""
    PRE_MARKET = "PRE_MARKET"              # 开盘前 (0:00-9:15)
    CALL_AUCTION = "CALL_AUCTION"          # 集合竞价 (9:15-9:25)
    WAIT_FOR_OPEN = "WAIT_FOR_OPEN"        # 等待开盘 (9:25-9:30)
    MORNING_OPENING = "MORNING_OPENING"    # 上午开盘 (9:30-10:00)
    MORNING_ACTIVE = "MORNING_ACTIVE"      # 上午活跃 (10:00-11:30)
    LUNCH_BREAK = "LUNCH_BREAK"            # 午休 (11:30-13:00)
    AFTERNOON_OPENING = "AFTERNOON_OPENING"  # 下午开盘 (13:00-14:00)
    AFTERNOON_STABLE = "AFTERNOON_STABLE"    # 下午平稳 (14:00-15:00)
    AFTER_MARKET = "AFTER_MARKET"          # 收盘后 (15:00-24:00)
    WEEKEND = "WEEKEND"                    # 周末


class TradingTimeChecker:
    """交易时间检查器"""

    # 关键时间点
    CALL_AUCTION_START = time(9, 15)
    CALL_AUCTION_END = time(9, 25)
    MARKET_OPEN = time(9, 30)
    MORNING_CLOSE = time(11, 30)
    AFTERNOON_OPEN = time(13, 0)
    MARKET_CLOSE = time(15, 0)

    @staticmethod
    def get_current_phase() -> TimePhase:
        """获取当前时段"""
        now = datetime.now()
        current_time = now.time()
        weekday = now.weekday()

        if weekday >= 5:
            return TimePhase.WEEKEND

        if TradingTimeChecker.CALL_AUCTION_START <= current_time < TradingTimeChecker.CALL_AUCTION_END:
            return TimePhase.CALL_AUCTION

        if TradingTimeChecker.CALL_AUCTION_END <= current_time < TradingTimeChecker.MARKET_OPEN:
            return TimePhase.WAIT_FOR_OPEN

        if TradingTimeChecker.MARKET_OPEN <= current_time < time(10, 0):
            return TimePhase.MORNING_OPENING

        if time(10, 0) <= current_time < TradingTimeChecker.MORNING_CLOSE:
            return TimePhase.MORNING_ACTIVE

        if TradingTimeChecker.MORNING_CLOSE <= current_time < TradingTimeChecker.AFTERNOON_OPEN:
            return TimePhase.LUNCH_BREAK

        if TradingTimeChecker.AFTERNOON_OPEN <= current_time < time(14, 0):
            return TimePhase.AFTERNOON_OPENING

        if time(14, 0) <= current_time < TradingTimeChecker.MARKET_CLOSE:
            return TimePhase.AFTERNOON_STABLE

        if TradingTimeChecker.MARKET_CLOSE <= current_time:
            return TimePhase.AFTER_MARKET

        return TimePhase.PRE_MARKET

    @staticmethod
    def is_trading_time() -> bool:
        """判断是否在交易时间（9:15-15:00 工作日）"""
        phase = TradingTimeChecker.get_current_phase()
        return phase in [
            TimePhase.CALL_AUCTION,
            TimePhase.MORNING_OPENING,
            TimePhase.MORNING_ACTIVE,
            TimePhase.AFTERNOON_OPENING,
            TimePhase.AFTERNOON_STABLE,
        ]

    @staticmethod
    def get_phase_description() -> str:
        """获取当前时段的中文描述"""
        descriptions = {
            TimePhase.PRE_MARKET: "开盘前",
            TimePhase.CALL_AUCTION: "集合竞价 (9:15-9:25)",
            TimePhase.WAIT_FOR_OPEN: "等待开盘 (9:25-9:30)",
            TimePhase.MORNING_OPENING: "上午开盘 (9:30-10:00)",
            TimePhase.MORNING_ACTIVE: "上午活跃 (10:00-11:30)",
            TimePhase.LUNCH_BREAK: "午休 (11:30-13:00)",
            TimePhase.AFTERNOON_OPENING: "下午开盘 (13:00-14:00)",
            TimePhase.AFTERNOON_STABLE: "下午平稳 (14:00-15:00)",
            TimePhase.AFTER_MARKET: "收盘后",
            TimePhase.WEEKEND: "周末",
        }
        return descriptions.get(TradingTimeChecker.get_current_phase(), "未知时段")

    @staticmethod
    def get_next_refresh_interval() -> int:
        """根据时段返回建议刷新间隔（秒）"""
        phase = TradingTimeChecker.get_current_phase()

        if phase in [TimePhase.CALL_AUCTION, TimePhase.MORNING_OPENING, TimePhase.AFTERNOON_OPENING]:
            return 3

        if phase in [TimePhase.MORNING_ACTIVE, TimePhase.AFTERNOON_STABLE]:
            return 5

        return 30

    @staticmethod
    def get_cache_ttl() -> int:
        """根据时段返回缓存 TTL（秒）"""
        phase = TradingTimeChecker.get_current_phase()

        if phase == TimePhase.CALL_AUCTION:
            return 10

        if TradingTimeChecker.is_trading_time():
            return 300

        return 86400

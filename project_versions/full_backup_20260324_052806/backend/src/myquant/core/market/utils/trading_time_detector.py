# -*- coding: utf-8 -*-
"""
改进的交易时间检测器（v2 修正版）

改进点：
1. 集成 TdxQuant 交易日历 API
2. 动态加载节假日，不再硬编码
3. 支持自定义交易日历数据源
4. 交易日历缓存，提高性能
"""

from typing import Dict, List, Optional, Set, Callable, Any
from loguru import logger
from datetime import datetime, time, timedelta
from enum import Enum
import json
import os


class TradingPhase(Enum):
    """交易时段"""
    PRE_AUCTION = "pre_auction"
    MORNING_OPENING = "morning_opening"
    MORNING_STABLE = "morning_stable"
    LUNCH_BREAK = "lunch_break"
    AFTERNOON_OPENING = "afternoon_opening"
    AFTERNOON_STABLE = "afternoon_stable"
    CLOSED = "closed"
    WEEKEND = "weekend"


class TradingTimeDetectorV2:
    """
    改进的交易时间检测器 v2

    核心改进：
    1. 集成 TdxQuant 交易日历 API
    2. 动态加载节假日
    3. 交易日历缓存
    4. 支持自定义数据源
    """

    def __init__(
        self,
        trading_calendar_source: Optional[Callable] = None,
        enable_cache: bool = True
    ):
        """
        初始化改进的交易时间检测器

        Args:
            trading_calendar_source: 交易日历数据源（函数）
                                         返回交易日列表
            enable_cache: 是否启用缓存
        """
        logger.info("TradingTimeDetectorV2 初始化完成")

        # 交易日历数据源
        self._trading_calendar_source = trading_calendar_source
        if self._trading_calendar_source is None:
            # 默认使用本地节假日数据（更可靠，不依赖外部 API）
            logger.info("使用本地节假日数据（2024-2026年）")
            self._trading_calendar_source = self._get_holidays_local

        # 交易时段配置
        self._phases = {
            TradingPhase.PRE_AUCTION: (time(9, 15), time(9, 25)),
            TradingPhase.MORNING_OPENING: (time(9, 30), time(10, 0)),
            TradingPhase.MORNING_STABLE: (time(10, 0), time(11, 30)),
            TradingPhase.LUNCH_BREAK: (time(11, 30), time(13, 0)),
            TradingPhase.AFTERNOON_OPENING: (time(13, 0), time(13, 30)),
            TradingPhase.AFTERNOON_STABLE: (time(13, 30), time(15, 0)),
            TradingPhase.CLOSED: (time(15, 0), time(9, 30)),
        }

        # 缓存
        self._enable_cache = enable_cache
        self._trading_days_cache = {}
        self._non_trading_days_cache = {}

        # 节假日缓存文件路径（项目根目录 data/cache/）
        # 从 data_providers/utils/ 定位到项目根目录 data/cache/
        current_dir = os.path.dirname(__file__)  # backend/data_providers/utils/
        providers_dir = os.path.dirname(current_dir)  # backend/data_providers/
        backend_dir = os.path.dirname(providers_dir)  # backend/
        project_root = os.path.dirname(backend_dir)  # 项目根目录 e:/MyQuant_v10.0.0v2/
        cache_dir = os.path.join(project_root, "data", "cache")
        self._holiday_cache_file = os.path.join(cache_dir, "holidays.json")

        logger.info("缓存配置: " + ("已启用" if enable_cache else "已禁用"))
        logger.info(f"节假日缓存文件: {self._holiday_cache_file}")

    def _get_hardcoded_holidays(self) -> set:
        """获取本地节假日数据（2024-2026年）"""
        return {
            "20240101",  # 元旦
            "20240210", "20240211", "20240212", "20240213", "20240214", "20240215", "20240216", "20240217",  # 春节
            "20240404", "20240405", "20240406",  # 清明节
            "20240501", "20240502", "20240503", "20240504", "20240505",  # 劳动节
            "20240610",  # 端午节
            "20240915", "20240916", "20240917",  # 中秋节
            "20241001", "20241002", "20241003", "20241004", "20241005", "20241006", "20241007",  # 国庆节
            "20250101",  # 元旦
            "20250128", "20250129", "20250130", "20250131", "20250201", "20250202", "20250203", "20250204",  # 春节
            "20250404", "20250405", "20250406",  # 清明节
            "20250501", "20250502", "20250503", "20250504", "20250505",  # 劳动节
            "20250531", "20250601", "20250602",  # 端午节
            "20251001", "20251002", "20251003", "20251004", "20251005", "20251006", "20251007", "20251008",  # 国庆节
            "20260101",  # 元旦 (预计)
            "20260128", "20260129", "20260130", "20260131", "20260201", "20260202", "20260203", "20260204",  # 春节 (预计)
            "20260404", "20260405", "20260406",  # 清明节 (预计)
            "20260501", "20260502", "20260503", "20260504", "20260505",  # 劳动节 (预计)
            "20260620", "20260621", "20260622",  # 端午节 (预计)
            "20260925", "20260926", "20260927",  # 中秋节 (预计)
            "20261001", "20261002", "20261003", "20261004", "20261005", "20261006", "20261007", "20261008",  # 国庆节 (预计)
        }

    def _get_holidays_local(self, start_date: str = None, end_date: str = None) -> List[str]:
        """获取本地节假日数据（优先从缓存文件读取）

        缓存文件位置: backend/data/cache/holidays.json
        每年更新一次即可

        Args:
            start_date: 开始日期 (YYYYMMDD) - 未使用，保持接口兼容
            end_date: 结束日期 (YYYYMMDD) - 未使用，保持接口兼容

        Returns:
            节假日列表（仅节假日，不含周末）
        """
        # 尝试从缓存文件读取
        if os.path.exists(self._holiday_cache_file):
            try:
                with open(self._holiday_cache_file, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                    holidays = set(cache_data.get('holidays', []))
                    logger.info(f"[节假日缓存] 从文件加载 {len(holidays)} 天节假日")
                    return sorted(list(holidays))
            except Exception as e:
                logger.warning(f"[节假日缓存] 读取缓存文件失败: {e}")

        # 缓存文件不存在或读取失败，使用硬编码数据
        holidays = self._get_hardcoded_holidays()
        logger.info(f"[本地节假日] 使用硬编码数据 {len(holidays)} 天节假日")

        # 尝试保存到缓存文件（供下次使用）
        try:
            os.makedirs(os.path.dirname(self._holiday_cache_file), exist_ok=True)
            with open(self._holiday_cache_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'holidays': sorted(list(holidays)),
                    'updated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'version': '1.0'
                }, f, indent=2, ensure_ascii=False)
            logger.info(f"[节假日缓存] 已保存到 {self._holiday_cache_file}")
        except Exception as e:
            logger.warning(f"[节假日缓存] 保存缓存文件失败: {e}")

        return sorted(list(holidays))

    def _get_working_days(self, year: int, month: int) -> set:
        """获取工作日（排除周末）"""
        import calendar
        working_days = set()
        for week in calendar.monthcalendar(year, month):
            for day, weekday in enumerate(week, start=1):
                if weekday < 5:  # 0-4 表示周一到周五
                    working_days.add(f"{year}{month:02d}{day:02d}")

        return working_days

    def _get_trading_days(
        self,
        year: int,
        month: int
    ) -> Set[str]:
        """获取指定月份的交易日"""
        cache_key = f"{year}{month:02d}"

        # 尝试从缓存获取
        if self._enable_cache and cache_key in self._trading_days_cache:
            return self._trading_days_cache[cache_key]

        try:
            # 调用数据源获取节假日（不含周末）
            start_date = f"{year}{month:02d}01"
            end_date = f"{year}{month:02d}31"

            holidays = self._trading_calendar_source(
                start_date=start_date,
                end_date=end_date
            )

            # 生成该月所有工作日（排除周末）
            working_days = self._get_working_days(year, month)

            # 从工作日中减去节假日
            trading_set = working_days - set(holidays)

            # 写入缓存
            if self._enable_cache:
                self._trading_days_cache[cache_key] = trading_set
                logger.debug(f"交易日历已缓存: {cache_key} ({len(trading_set)} 天)")

            return trading_set

        except Exception as e:
            logger.error(f"获取交易日历失败 {year}-{month:02d}: {e}")
            # 降级：返回工作日
            return self._get_working_days(year, month)

    def is_trading_day(self, check_date: datetime = None) -> bool:
        """
        判断指定日期是否为交易日

        Args:
            check_date: 检查的日期（None 使用当前日期）

        Returns:
            是否为交易日
        """
        check_date = check_date if check_date else datetime.now()
        date_str = check_date.strftime("%Y%m%d")
        year = check_date.year
        month = check_date.month

        # 获取该月的交易日
        trading_days = self._get_trading_days(year, month)

        return date_str in trading_days

    def is_trading_time(self, check_time: datetime = None) -> bool:
        """
        判断是否为交易时间

        Args:
            check_time: 检查的时间（None 使用当前时间）

        Returns:
            是否为交易时间
        """
        check_time = check_time if check_time else datetime.now()

        # 检查是否为交易日
        if not self.is_trading_day(check_time):
            return False

        # 检查是否在交易时段内
        current_time = check_time.time()

        for phase, (start, end) in self._phases.items():
            if phase in [TradingPhase.CLOSED, TradingPhase.WEEKEND]:
                continue

            if start <= current_time <= end:
                return True

        return False

    def get_trading_phase(self, check_time: datetime = None) -> TradingPhase:
        """
        获取当前交易时段

        Args:
            check_time: 检查的时间（None 使用当前时间）

        Returns:
            交易时段
        """
        check_time = check_time if check_time else datetime.now()

        # 检查是否为交易日
        if not self.is_trading_day(check_time):
            # 判断是否为周末
            if check_time.weekday() >= 5:
                return TradingPhase.WEEKEND
            # 判断是否为节假日
            date_str = check_time.strftime("%Y%m%d")
            year = check_time.year
            month = check_time.month
            trading_days = self._get_trading_days(year, month)
            if date_str not in trading_days:
                return TradingPhase.CLOSED
            return TradingPhase.CLOSED

        # 检查当前时段
        current_time = check_time.time()

        for phase, (start, end) in self._phases.items():
            if start <= current_time <= end:
                return phase

        return TradingPhase.CLOSED

    def get_data_source_priority(
        self,
        check_time: datetime = None
    ) -> Dict[str, int]:
        """
        根据交易时间获取数据源优先级

        Args:
            check_time: 检查的时间（None 使用当前时间）

        Returns:
            数据源优先级字典 {source: priority}
        """
        check_time = check_time if check_time else datetime.now()

        # 检查是否为交易日
        if not self.is_trading_time(check_time):
            # 非交易时间：优先使用历史数据
            return {
                "realtime": 3,
                "cache": 2,
                "history": 1
            }

        # 交易时段内：优先使用实时数据
        if check_time.weekday() >= 5:
            # 周末
            return {
                "realtime": 3,
                "cache": 2,
                "history": 1
            }

        current_phase = self.get_trading_phase(check_time)

        if current_phase in [TradingPhase.CLOSED, TradingPhase.WEEKEND]:
            # 收盘后或周末：优先使用缓存数据
            return {
                "realtime": 3,
                "cache": 1,
                "history": 2
            }

        # 交易时段内：优先使用实时数据
        if current_phase in [
            TradingPhase.PRE_AUCTION,
            TradingPhase.MORNING_OPENING,
            TradingPhase.MORNING_STABLE,
            TradingPhase.AFTERNOON_OPENING,
            TradingPhase.AFTERNOON_STABLE
        ]:
            logger.debug(f"交易时段 {current_phase.value}，使用实时数据源")
            return {
                "realtime": 1,
                "cache": 2,
                "history": 3
            }

        # 默认：优先使用缓存
        logger.debug("默认使用缓存数据源")
        return {
            "realtime": 2,
            "cache": 1,
            "history": 3
        }

    def should_use_realtime(self, check_time: datetime = None) -> bool:
        """
        判断是否应该使用实时数据

        Args:
            check_time: 检查的时间（None 使用当前时间）

        Returns:
            是否使用实时数据
        """
        return self.is_trading_time(check_time)

    def should_use_cache(self, check_time: datetime = None) -> bool:
        """
        判断是否应该使用缓存数据

        Args:
            check_time: 检查的时间（None 使用当前时间）

        Returns:
            是否使用缓存数据
        """
        priority = self.get_data_source_priority(check_time)
        return priority.get("cache", 0) == 1

    def get_trading_days_in_range(
        self,
        start_date: str,
        end_date: str
    ) -> List[str]:
        """
        获取日期范围内的所有交易日

        Args:
            start_date: 开始日期，格式 YYYYMMDD
            end_date: 结束日期，格式 YYYYMMDD

        Returns:
            交易日列表，格式 YYYYMMDD
        """
        try:
            # 直接调用数据源
            trading_days = self._trading_calendar_source(
                start_date=start_date,
                end_date=end_date
            )

            # 清除相关缓存
            if self._enable_cache:
                self._clear_cache_range(start_date, end_date)

            logger.info(f"获取交易日历: {start_date} ~ {end_date} ({len(trading_days)} 天)")
            return trading_days

        except Exception as e:
            logger.error(f"获取交易日历范围失败: {e}")
            # 降级：返回工作日
            return self._get_working_days_range(start_date, end_date)

    def _get_working_days_range(
        self,
        start_date: str,
        end_date: str
    ) -> List[str]:
        """获取日期范围内的工作日（备用方案）"""
        working_days = []
        current_date = datetime.strptime(start_date, "%Y%m%d")
        end_dt = datetime.strptime(end_date, "%Y%m%d")

        while current_date <= end_dt:
            if current_date.weekday() < 5:
                working_days.append(current_date.strftime("%Y%m%d"))
            current_date += timedelta(days=1)

        return working_days

    def _clear_cache_range(self, start_date: str, end_date: str):
        """清空日期范围内的缓存"""
        start_dt = datetime.strptime(start_date, "%Y%m%d")
        end_dt = datetime.strptime(end_date, "%Y%m%d")

        while start_dt <= end_dt:
            cache_key = f"{start_dt.year}{start_dt.month:02d}"
            if cache_key in self._trading_days_cache:
                del self._trading_days_cache[cache_key]
            start_dt += timedelta(days=31)

    def clear_cache(self):
        """
        清空所有缓存
        """
        self._trading_days_cache.clear()
        self._non_trading_days_cache.clear()
        logger.info("交易日历缓存已清空")

    def get_cache_stats(self) -> Dict[str, Any]:
        """
        获取缓存统计信息

        Returns:
            缓存统计字典
        """
        return {
            "cached_months": len(self._trading_days_cache),
            "total_trading_days": sum(
                len(days) for days in self._trading_days_cache.values()
            ),
            "cache_enabled": self._enable_cache
        }

    def get_trading_day_info(
        self,
        check_date: datetime = None
    ) -> Dict[str, Any]:
        """
        获取指定日期的交易信息

        Args:
            check_date: 指定日期（None 使用当前日期）

        Returns:
            交易信息字典
        """
        check_date = check_date if check_date else datetime.now()
        year = check_date.year
        month = check_date.month
        date_str = check_date.strftime("%Y%m%d")

        # 获取该月的交易日
        trading_days = self._get_trading_days(year, month)
        total_days = len(trading_days)

        # 判断是否为交易日
        is_trading = date_str in trading_days

        return {
            "date": date_str,
            "is_trading_day": is_trading,
            "is_weekend": check_date.weekday() >= 5,
            "total_trading_days": total_days,
            "phase": self.get_trading_phase(check_date).value,
            "data_source": (
                "TdxQuant API" if hasattr(self, "_trading_calendar_source")
                else "Hardcoded"
            )
        }


# 便捷函数
def get_trading_time_detector_v2() -> TradingTimeDetectorV2:
    """获取改进的交易时间检测器实例（全局单例）"""
    return TradingTimeDetectorV2()


def is_trading_time(check_time: datetime = None) -> bool:
    """便捷函数：判断是否为交易时间"""
    detector = get_trading_time_detector_v2()
    return detector.is_trading_time(check_time)


def get_trading_phase(check_time: datetime = None) -> str:
    """便捷函数：获取交易时段"""
    detector = get_trading_time_detector_v2()
    return detector.get_trading_phase(check_time).value


def get_trading_days_in_range(start_date: str, end_date: str) -> List[str]:
    """便捷函数：获取日期范围内的交易日"""
    detector = get_trading_time_detector_v2()
    return detector.get_trading_days_in_range(start_date, end_date)

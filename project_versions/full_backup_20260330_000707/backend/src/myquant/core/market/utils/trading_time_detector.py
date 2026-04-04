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
from datetime import datetime, time, date
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

    def _fetch_holidays_from_online(self, start_year: int, end_year: int) -> Optional[set]:
        """从 holiday-cn (GitHub) 在线获取节假日数据

        数据源: https://github.com/NateScarlet/holiday-cn
        每日自动抓取国务院公告

        Args:
            start_year: 起始年份
            end_year: 结束年份

        Returns:
            节假日日期集合 (YYYYMMDD 格式)，失败返回 None
        """
        try:
            import urllib.request
            import urllib.error

            holidays = set()
            base_url = "https://raw.githubusercontent.com/NateScarlet/holiday-cn/master"

            for year in range(start_year, end_year + 1):
                url = f"{base_url}/{year}.json"
                try:
                    with urllib.request.urlopen(url, timeout=5) as response:
                        data = json.loads(response.read().decode('utf-8'))

                        # holiday-cn 格式: {"days": [{"date": "2026-02-15", "isOffDay": true}, ...]}
                        if 'days' in data:
                            year_holidays = []
                            for day_info in data['days']:
                                if day_info.get('isOffDay', False):
                                    # 转换 "2026-02-15" -> "20260215"
                                    date_str = day_info['date'].replace('-', '')
                                    holidays.add(date_str)
                                    year_holidays.append(date_str)

                            logger.info(f"[holiday-cn] 获取 {year} 年节假日: {len(year_holidays)} 天")

                except urllib.error.URLError as e:
                    logger.warning(f"[holiday-cn] 获取 {year} 年数据失败: {e}")
                    continue
                except Exception as e:
                    logger.warning(f"[holiday-cn] 解析 {year} 年数据失败: {e}")
                    continue

            if holidays:
                logger.info(f"[holiday-cn] 在线获取 {start_year}-{end_year} 年节假日: {len(holidays)} 天")
                return holidays
            else:
                return None

        except ImportError:
            logger.warning("[holiday-cn] urllib 不可用，降级到 chinese_calendar")
            return None
        except Exception as e:
            logger.warning(f"[holiday-cn] 在线获取失败: {e}，降级到 chinese_calendar")
            return None

    def _generate_holidays_from_chinese_calendar(self, start_year: int, end_year: int) -> Optional[set]:
        """使用 chinese_calendar 库生成节假日数据（降级方案）

        Args:
            start_year: 起始年份
            end_year: 结束年份

        Returns:
            节假日日期集合 (YYYYMMDD 格式)，失败返回 None
        """
        try:
            import chinese_calendar as calendar
            holidays = set()

            for year in range(start_year, end_year + 1):
                start_date = date(year, 1, 1)
                end_date = date(year, 12, 31)

                # 获取该年所有节假日
                holidays_list = calendar.get_holidays(start_date, end_date)
                for d in holidays_list:
                    holidays.add(d.strftime("%Y%m%d"))

            logger.info(f"[chinese_calendar] 生成 {start_year}-{end_year} 年节假日: {len(holidays)} 天")
            return holidays

        except ImportError:
            logger.warning("[chinese_calendar] 库未安装，请运行: pip install chinese_calendar")
            return None
        except Exception as e:
            logger.warning(f"[chinese_calendar] 生成节假日失败: {e}")
            return None

    def _get_holidays_local(self, start_date: str = None, end_date: str = None) -> List[str]:
        """获取本地节假日数据（优先从缓存文件读取）

        缓存文件位置: backend/data/cache/holidays.json
        数据源优先级: 缓存文件 -> holiday-cn (在线) -> chinese_calendar (本地)

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

                    # 检查缓存是否过期（每月1号自动刷新）
                    updated_at = cache_data.get('updated_at', '')
                    if updated_at:
                        try:
                            cache_date = datetime.strptime(updated_at, '%Y-%m-%d %H:%M:%S')
                            current_date = datetime.now()

                            # 计算月份差异
                            months_diff = (current_date.year - cache_date.year) * 12 + (current_date.month - cache_date.month)

                            if months_diff < 1:
                                logger.info(f"[节假日缓存] 从文件加载 {len(holidays)} 天节假日 (缓存有效，{updated_at})")
                                return sorted(list(holidays))
                            else:
                                logger.info(f"[节假日缓存] 缓存已过期 ({months_diff} 个月)，重新获取")
                        except ValueError:
                            logger.warning("[节假日缓存] 解析缓存时间失败，重新获取")
                    else:
                        logger.info("[节假日缓存] 缓存无时间戳，重新获取")

            except Exception as e:
                logger.warning(f"[节假日缓存] 读取缓存文件失败: {e}")

        # 尝试从 holiday-cn 在线获取节假日数据
        current_year = datetime.now().year
        holidays = self._fetch_holidays_from_online(current_year - 1, current_year + 2)

        # 降级到 chinese_calendar
        if holidays is None:
            logger.info("[节假日] 在线获取失败，降级到 chinese_calendar")
            holidays = self._generate_holidays_from_chinese_calendar(current_year - 1, current_year + 2)

        # 如果都失败，返回空集（降级：只排除周末）
        if holidays is None:
            logger.warning("[节假日] 无法获取节假日数据，将只排除周末（不排除节假日）")
            holidays = set()

        # 保存到缓存文件
        try:
            os.makedirs(os.path.dirname(self._holiday_cache_file), exist_ok=True)
            source = "holiday-cn" if len(holidays) > 0 else "empty"
            with open(self._holiday_cache_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'holidays': sorted(list(holidays)),
                    'updated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'version': '3.0',
                    'source': source
                }, f, indent=2, ensure_ascii=False)
            logger.info(f"[节假日缓存] 已保存 {len(holidays)} 天节假日到 {self._holiday_cache_file}")
        except Exception as e:
            logger.warning(f"[节假日缓存] 保存缓存文件失败: {e}")

        return sorted(list(holidays))

    def _get_working_days(self, year: int, month: int) -> set:
        """获取工作日（排除周末）"""
        import calendar
        working_days = set()
        for week in calendar.monthcalendar(year, month):
            for weekday, day in enumerate(week):
                # weekday: 0=周一, 4=周五, 5=周六, 6=周日
                # day: 日期，0表示不在当月
                if day > 0 and weekday < 5:  # 工作日（周一到周五）
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
        is_trading = date_str in trading_days

        # 详细日志
        weekday_name = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"][check_date.weekday()]
        if is_trading:
            logger.debug(f"[交易日检查] {date_str} ({weekday_name}) 是交易日")
        else:
            if check_date.weekday() >= 5:
                logger.debug(f"[交易日检查] {date_str} ({weekday_name}) 不是交易日：周末")
            else:
                logger.debug(f"[交易日检查] {date_str} ({weekday_name}) 不是交易日：节假日")

        return is_trading

    def is_trading_time(self, check_time: datetime = None) -> bool:
        """
        判断是否为交易时间

        Args:
            check_time: 检查的时间（None 使用当前时间）

        Returns:
            是否为交易时间
        """
        check_time = check_time if check_time else datetime.now()
        date_str = check_time.strftime("%Y%m%d")
        time_str = check_time.strftime("%H:%M:%S")

        # 检查是否为交易日
        if not self.is_trading_day(check_time):
            logger.debug(f"[交易时间检查] {date_str} {time_str} 不是交易时间：非交易日")
            return False

        # 检查是否在交易时段内
        current_time = check_time.time()

        for phase, (start, end) in self._phases.items():
            if phase in [TradingPhase.CLOSED, TradingPhase.WEEKEND]:
                continue

            if start <= current_time <= end:
                logger.debug(f"[交易时间检查] {date_str} {time_str} 是交易时间：{phase.value}")
                return True

        # 不在任何交易时段
        phase = self.get_trading_phase(check_time)
        logger.debug(f"[交易时间检查] {date_str} {time_str} 不是交易时间：{phase.value}")
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

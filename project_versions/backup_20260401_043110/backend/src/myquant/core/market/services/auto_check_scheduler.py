"""
自动数据检查定时调度器

每天收盘后（15:00-16:00）自动触发数据检查补全
"""

import threading
import time
from datetime import datetime
from loguru import logger


class AutoCheckScheduler:
    """自动检查调度器

    职责：
    - 每天收盘后（15:00-16:00）自动触发数据检查
    - 避免重复检查（同一天只检查一次）
    - 后台线程运行，不阻塞主程序
    """

    def __init__(self, check_interval_minutes: int = 30):
        """初始化调度器

        Args:
            check_interval_minutes: 检查间隔（分钟），默认30分钟
        """
        self._running = False
        self._thread = None
        self._check_interval = check_interval_minutes * 60  # 转换为秒

    def _should_check_today(self) -> bool:
        """判断今天是否应该检查

        Returns:
            True 如果今天应该检查，False 否则
        """
        from myquant.core.market.services.daily_data_status import get_daily_status_service
        from myquant.core.market.utils.trading_time_detector import TradingTimeDetectorV2

        detector = TradingTimeDetectorV2()

        # 不是交易日，跳过
        if not detector.is_trading_day():
            return False

        status_service = get_daily_status_service()
        today_str = datetime.now().strftime('%Y%m%d')

        # 检查今天是否已记录
        status = status_service.get_status()
        if status.get("data"):
            for symbol_data in status["data"].values():
                if today_str in symbol_data:
                    return False  # 今天已检查过

        # 今天没记录，还需要检查最近交易日是否也没记录
        # 如果昨天也没有记录，说明可能昨天没开电脑，需要补昨天的数据
        return True

    def _perform_check(self):
        """执行一次数据检查补全"""
        import asyncio

        from myquant.core.market.services.hotdb_service import get_hotdb_service
        from myquant.api.dataget.watchlist import get_watchlist

        hotdb_service = get_hotdb_service()

        # 异步获取自选股
        response = asyncio.run(get_watchlist())
        watchlist = response.data if hasattr(response, 'data') else response

        all_symbols = []
        for group in watchlist.get('groups', []):
            for stock in group.get('stocks', []):
                all_symbols.append(stock['symbol'])

        hotdb_service.auto_check_and_fill_today(all_symbols)

    def _run_loop(self):
        """主循环"""
        logger.info("[AutoCheckScheduler] 调度器线程启动")

        while self._running:
            try:
                now = datetime.now()
                current_time = now.strftime('%H:%M')

                # 收盘后时间段：15:00 - 16:00
                if '15:00' <= current_time < '16:00':
                    if self._should_check_today():
                        logger.info("[AutoCheckScheduler] 触发收盘后自动检查")
                        self._perform_check()

                # 等待下一次检查
                time.sleep(self._check_interval)

            except Exception as e:
                logger.error(f"[AutoCheckScheduler] 运行出错: {e}")
                time.sleep(60)  # 出错后等待1分钟再试

        logger.info("[AutoCheckScheduler] 调度器线程停止")

    def start(self):
        """启动调度器"""
        if self._running:
            logger.warning("[AutoCheckScheduler] 调度器已在运行")
            return

        self._running = True

        # 启动时立即检查一次（如果今天需要）
        if self._should_check_today():
            logger.info("[AutoCheckScheduler] 启动时检查并补全数据")
            self._perform_check()

        # 启动后台线程
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        logger.info("[AutoCheckScheduler] 调度器已启动")

    def stop(self):
        """停止调度器"""
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)
        logger.info("[AutoCheckScheduler] 调度器已停止")


# 单例
_scheduler = None


def get_auto_check_scheduler() -> AutoCheckScheduler:
    """获取调度器单例"""
    global _scheduler
    if _scheduler is None:
        _scheduler = AutoCheckScheduler()
    return _scheduler

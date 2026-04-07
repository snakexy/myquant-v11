"""
自动数据检查定时调度器

收盘后自动触发数据检查补全（15:00-23:59）
"""

import threading
import time
from datetime import datetime
from loguru import logger


class AutoCheckScheduler:
    """自动检查调度器

    职责：
    - 收盘后自动触发数据检查（15:00-23:59）
    - 避免重复检查（同一股票同一天只检查一次）
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
        self._is_checking = threading.Lock()  # 防止重复执行

    def _should_check_today(self) -> bool:
        """判断今天是否应该检查

        逻辑：检查是否还有未检查的股票，而不是只要有一个检查过就跳过

        Returns:
            True 如果还有未检查的股票，False 否则
        """
        from myquant.core.market.services.daily_data_status import get_daily_status_service
        from myquant.core.market.utils.trading_time_detector import get_trading_time_detector_v2
        from myquant.api.dataget.watchlist import load_watchlist_data

        detector = get_trading_time_detector_v2()

        # 不是交易日，跳过
        if not detector.is_trading_day():
            return False

        # 获取所有自选股
        try:
            watchlist = load_watchlist_data()
            all_symbols = []
            for group in watchlist.get('groups', []):
                for stock in group.get('stocks', []):
                    all_symbols.append(stock['symbol'])
        except Exception as e:
            logger.warning(f"[AutoCheckScheduler] 获取自选股失败: {e}")
            return True  # 获取失败时默认执行检查

        # 检查是否还有未检查的股票
        status_service = get_daily_status_service()
        unchecked = [s for s in all_symbols if not status_service.is_checked_today(s)]

        if len(unchecked) == 0:
            logger.debug("[AutoCheckScheduler] 所有股票今天都已检查")
            return False

        logger.info(f"[AutoCheckScheduler] 还有 {len(unchecked)}/{len(all_symbols)} 只股票今天未检查")
        return True

    def _perform_check(self):
        """执行一次数据检查补全"""
        # 获取锁，防止重复执行
        if not self._is_checking.acquire(blocking=False):
            logger.info("[AutoCheckScheduler] 已有检查任务在执行，跳过")
            return

        try:
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

            logger.info(f"[AutoCheckScheduler] 开始检查 {len(all_symbols)} 只股票")
            results = hotdb_service.auto_check_and_fill_today(all_symbols)
            logger.info(
                f"[AutoCheckScheduler] 检查完成: "
                f"checked={results.get('checked', 0)}, "
                f"filled={results.get('filled', 0)}, "
                f"skipped={results.get('skipped', 0)}"
            )
        except Exception as e:
            logger.error(f"[AutoCheckScheduler] 执行检查失败: {e}")
        finally:
            self._is_checking.release()

    def _run_loop(self):
        """主循环"""
        logger.info("[AutoCheckScheduler] 调度器线程启动")

        while self._running:
            try:
                now = datetime.now()
                current_time = now.strftime('%H:%M')

                # 收盘后时间段：15:00 - 23:59（扩大窗口，避免错过）
                if '15:00' <= current_time < '23:59':
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
            # 在后台线程中执行，不阻塞启动
            check_thread = threading.Thread(target=self._perform_check, daemon=True)
            check_thread.start()

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

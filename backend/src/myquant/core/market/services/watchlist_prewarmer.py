"""
自选股预热管理器

管理自选股列表的复权因子预加载，确保用户最常查看的股票首次加载 <5ms
"""

from typing import List, Set
from loguru import logger

from myquant.core.market.services.adjustment_factor_service import get_adjustment_factor_service

class WatchlistPrewarmer:
    """自选股预热管理器

    职责：
    1. 管理用户自选股列表
    2. 在后台预加载自选股的复权因子
    3. 自选股切换时保证 <5ms 响应
    """

    def __init__(self):
        self.watchlist: Set[str] = set()  # 当前自选股列表
        self.factor_service = get_adjustment_factor_service()
        self._is_warmed_up = False
        logger.info("[WatchlistPrewarmer] 初始化完成")

    def set_watchlist(self, symbols: List[str]):
        """设置自选股列表（通常在应用启动时或用户修改自选股后调用）

        Args:
            symbols: 股票代码列表
        """
        new_watchlist = set(symbols)

        # 找出新增的股票
        added = new_watchlist - self.watchlist
        removed = self.watchlist - new_watchlist

        self.watchlist = new_watchlist

        if added:
            logger.info(f"[自选股] 新增 {len(added)} 只: {added}")
            # 异步预热新增的
            self._warmup_symbols(list(added))

        if removed:
            logger.info(f"[自选股] 移除 {len(removed)} 只: {removed}")

    def warmup(self):
        """预热所有自选股的复权因子（启动时调用）"""
        if self._is_warmed_up or not self.watchlist:
            return

        logger.info(f"[预热] 开始预加载 {len(self.watchlist)} 只自选股的复权因子...")
        self._warmup_symbols(list(self.watchlist))
        self._is_warmed_up = True
        logger.info("[预热] 自选股复权因子预加载完成")

    def _warmup_symbols(self, symbols: List[str]):
        """预热指定股票的两种复权因子"""
        for symbol in symbols:
            try:
                # 预计算日线用前复权
                self.factor_service.get_factor_table(symbol, 'front')
                # 预计算分钟线用等比复权
                self.factor_service.get_factor_table(symbol, 'front_ratio')
            except Exception as e:
                logger.debug(f"[预热] {symbol} 预热失败: {e}")

    def is_warmed_up(self) -> bool:
        """是否已完成预热"""
        return self._is_warmed_up


# 单例实例
_prewarmer_instance = None

def get_watchlist_prewarmer() -> WatchlistPrewarmer:
    """获取自选股预热管理器单例"""
    global _prewarmer_instance
    if _prewarmer_instance is None:
        _prewarmer_instance = WatchlistPrewarmer()
    return _prewarmer_instance


# 便捷函数
def set_watchlist(symbols: List[str]):
    """设置自选股列表（便捷函数）"""
    get_watchlist_prewarmer().set_watchlist(symbols)

def warmup_watchlist():
    """预热自选股（便捷函数）"""
    get_watchlist_prewarmer().warmup()

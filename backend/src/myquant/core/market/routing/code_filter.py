"""
代码类型过滤

根据股票/指数/板块代码识别类型，并过滤兼容的数据源
"""

from enum import Enum
from typing import Dict, List, Set, Optional

from myquant.core.market.models.stock import AssetType


class CodeTypeFilter:
    """代码类型过滤器

    根据代码格式识别资产类型（股票/指数/板块）
    """

    # 代码前缀规则
    SH_STOCK_PREFIXES: Set[str] = {'6', '5', '9'}     # 上海股票: 6xxxxx, 5xxxxx(ETF), 9xxxxx(B股)
    SZ_STOCK_PREFIXES: Set[str] = {'0', '2', '3'}     # 深圳股票: 0xxxxx, 2xxxxx(B股), 3xxxxx
    BJ_STOCK_PREFIXES: Set[str] = {'4', '8'}          # 北京股票: 4xxxxx, 8xxxxx
    SECTOR_PREFIXES: Set[str] = {'88', 'BK', '880'}   # 板块: 88xxxx, BKxxxx
    INDEX_PREFIXES: Set[str] = {'000', '399', '880'}  # 指数: 000xxx(SH), 399xxx(SZ), 880xxx(板块指数)

    # 数据源对资产类型的支持情况
    SOURCE_COMPATIBILITY: Dict[str, Set[AssetType]] = {
        'xtquant': {AssetType.STOCK, AssetType.INDEX, AssetType.ETF},
        'tdxquant': {AssetType.STOCK, AssetType.INDEX, AssetType.SECTOR_BLOCK, AssetType.ETF},
        'pytdx': {AssetType.STOCK, AssetType.INDEX, AssetType.SECTOR_BLOCK, AssetType.ETF},
        'localdb': {AssetType.STOCK, AssetType.INDEX},
        'tdxlocal': {AssetType.STOCK, AssetType.INDEX, AssetType.SECTOR_BLOCK},
        'hotdb': {AssetType.STOCK, AssetType.INDEX},  # 热数据库
    }

    def __init__(self):
        self._code_cache: Dict[str, AssetType] = {}

    def is_stock(self, code: str) -> bool:
        """判断是否为股票代码

        Args:
            code: 股票代码（可能带市场后缀）

        Returns:
            是否为股票
        """
        asset_type = self.get_asset_type(code)
        return asset_type == AssetType.STOCK

    def is_index(self, code: str) -> bool:
        """判断是否为指数代码

        Args:
            code: 指数代码

        Returns:
            是否为指数
        """
        asset_type = self.get_asset_type(code)
        return asset_type == AssetType.INDEX

    def is_sector(self, code: str) -> bool:
        """判断是否为板块代码

        Args:
            code: 板块代码

        Returns:
            是否为板块
        """
        asset_type = self.get_asset_type(code)
        return asset_type == AssetType.SECTOR_BLOCK

    def is_etf(self, code: str) -> bool:
        """判断是否为 ETF 代码

        Args:
            code: ETF 代码

        Returns:
            是否为 ETF
        """
        asset_type = self.get_asset_type(code)
        return asset_type == AssetType.ETF

    def get_asset_type(self, code: str) -> AssetType:
        """获取代码对应的资产类型

        Args:
            code: 代码（可能带市场后缀，如 600000.SH）

        Returns:
            AssetType
        """
        # 检查缓存
        if code in self._code_cache:
            return self._code_cache[code]

        # 标准化代码（移除市场后缀）
        clean_code = self._normalize_code(code)
        if not clean_code:
            self._code_cache[code] = AssetType.STOCK
            return AssetType.STOCK

        # 检查板块
        for prefix in self.SECTOR_PREFIXES:
            if clean_code.startswith(prefix):
                self._code_cache[code] = AssetType.SECTOR_BLOCK
                return AssetType.SECTOR_BLOCK

        # 检查指数
        for prefix in self.INDEX_PREFIXES:
            if clean_code.startswith(prefix):
                self._code_cache[code] = AssetType.INDEX
                return AssetType.INDEX

        # 检查 ETF（5开头或15开头）
        if clean_code.startswith('5') or clean_code.startswith('15'):
            self._code_cache[code] = AssetType.ETF
            return AssetType.ETF

        # 默认为股票
        self._code_cache[code] = AssetType.STOCK
        return AssetType.STOCK

    def filter_sources(self, sources: List[str], asset_type: AssetType) -> List[str]:
        """过滤出支持指定资产类型的数据源

        Args:
            sources: 数据源列表
            asset_type: 资产类型

        Returns:
            过滤后的数据源列表
        """
        filtered = []
        for source in sources:
            if source in self.SOURCE_COMPATIBILITY:
                if asset_type in self.SOURCE_COMPATIBILITY[source]:
                    filtered.append(source)
        return filtered

    def get_sources_for_code(self, code: str, sources: List[str]) -> List[str]:
        """获取对指定代码可用的数据源

        Args:
            code: 代码
            sources: 数据源列表

        Returns:
            过滤后的数据源列表
        """
        asset_type = self.get_asset_type(code)
        return self.filter_sources(sources, asset_type)

    def _normalize_code(self, code: str) -> str:
        """标准化代码（移除市场后缀）"""
        if not code:
            return code

        # 移除市场后缀
        for market in ['SH', 'SZ', 'BJ', 'sh', 'sz', 'bj']:
            if code.endswith(f'.{market}'):
                return code.split('.')[0]

        return code

    def clear_cache(self) -> None:
        """清空类型缓存"""
        self._code_cache.clear()


# 单例实例
_code_filter: Optional[CodeTypeFilter] = None


def get_code_filter() -> CodeTypeFilter:
    """获取 CodeTypeFilter 单例实例"""
    global _code_filter
    if _code_filter is None:
        _code_filter = CodeTypeFilter()
    return _code_filter

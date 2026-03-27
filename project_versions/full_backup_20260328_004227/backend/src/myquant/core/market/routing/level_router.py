"""
L0-L5 数据层级路由

定义数据层级和每个层级的数据源优先级
"""

from enum import Enum
from typing import Dict, List, Optional, Set
from dataclasses import dataclass


class DataLevel(str, Enum):
    """数据层级

    L0-L5 六层架构，每层有不同的数据源和响应时间
    """
    L0 = "subscription"    # 订阅缓存 (<1ms)
    L1 = "realtime"        # 实时快照 (1-17ms)
    L2 = "summary"         # 历史摘要 (7-17ms)
    L3 = "kline"           # 完整K线 (5-18ms)
    L4 = "financial"       # 财务数据 (100-300ms)
    L5 = "sector"          # 特色数据 (10-500ms)

    @classmethod
    def from_str(cls, value: str) -> 'DataLevel':
        """从字符串创建 DataLevel

        支持 "l0", "L0", "subscription" 等格式
        """
        value_lower = value.lower().replace('l', '')

        if value_lower == '0' or value == 'subscription':
            return cls.L0
        elif value_lower == '1' or value == 'realtime':
            return cls.L1
        elif value_lower == '2' or value == 'summary':
            return cls.L2
        elif value_lower == '3' or value == 'kline':
            return cls.L3
        elif value_lower == '4' or value == 'financial':
            return cls.L4
        elif value_lower == '5' or value == 'sector':
            return cls.L5

        raise ValueError(f"Unknown DataLevel: {value}")

    @property
    def description(self) -> str:
        """层级描述"""
        descriptions = {
            self.L0: "订阅缓存 (<1ms)",
            self.L1: "实时快照 (1-17ms)",
            self.L2: "历史摘要 (7-17ms)",
            self.L3: "完整K线 (5-18ms)",
            self.L4: "财务数据 (100-300ms)",
            self.L5: "特色数据 (10-500ms)",
        }
        return descriptions.get(self, "")

    @property
    def priority(self) -> int:
        """层级优先级（数字越小优先级越高）"""
        return [self.L0, self.L1, self.L2, self.L3, self.L4, self.L5].index(self)


@dataclass
class LevelConfig:
    """层级配置"""
    stock_sources: List[str]      # 股票数据源
    index_sources: List[str]      # 指数数据源
    sector_sources: List[str]     # 板块数据源


class LevelRouter:
    """L0-L5 数据层级路由器

    根据数据层级和资产类型选择最优数据源
    """

    # L0-L5 路由配置表（按优先级排序）
    LEVEL_CONFIGS: Dict[DataLevel, LevelConfig] = {
        # L0: 订阅缓存（交易时间）
        DataLevel.L0: LevelConfig(
            stock_sources=['xtquant', 'tdxquant'],  # XtQuant(300股) + TdxQuant(100股) 双订阅
            index_sources=[],                        # 指数不支持订阅
            sector_sources=['tdxquant'],             # 板块仅 TdxQuant 支持
        ),

        # L1: 实时快照
        DataLevel.L1: LevelConfig(
            stock_sources=['tdxquant', 'xtquant', 'pytdx'],  # TdxQuant(0.6ms) 最快
            index_sources=['xtquant', 'pytdx'],              # XtQuant(1ms) 优先
            sector_sources=['tdxquant', 'pytdx'],            # TdxQuant(6.99ms) 优先
        ),

        # L2: 历史摘要（30天K线摘要）
        DataLevel.L2: LevelConfig(
            stock_sources=['localdb', 'xtquant', 'pytdx'],
            index_sources=['localdb', 'xtquant', 'pytdx'],
            sector_sources=[],  # 板块不支持历史摘要
        ),

        # L3: 完整K线
        # 优先使用在线数据源（PyTdx/TdxQuant/XtQuant）确保数据完整性和准确性
        # LocalDB 作为最后的补充（数据可能较旧且成交量缺失）
        DataLevel.L3: LevelConfig(
            stock_sources=['tdxquant', 'pytdx', 'xtquant'],  # 在线优先：TdxQuant→PyTdx→XtQuant
            index_sources=['tdxquant', 'pytdx', 'xtquant'],  # 指数同样优先在线
            sector_sources=['tdxquant', 'pytdx'],  # 板块：TdxQuant（覆盖最全）→PyTdx
        ),

        # L4: 财务数据
        DataLevel.L4: LevelConfig(
            stock_sources=['tdxquant', 'xtquant'],  # TdxQuant(46字段) 最全
            index_sources=[],                        # 指数无财务数据
            sector_sources=[],                       # 板块无财务数据
        ),

        # L5: 特色数据（板块/预警）
        DataLevel.L5: LevelConfig(
            stock_sources=[],
            index_sources=[],
            sector_sources=['tdxquant', 'pytdx'],  # TdxQuant(586板块) 最全
        ),
    }

    def __init__(self):
        self._available_sources: Set[str] = set()
        self._unavailable_sources: Set[str] = set()

    def get_sources(self, level: DataLevel, asset_type: str = 'stock') -> List[str]:
        """获取指定层级和资产类型的数据源列表

        Args:
            level: 数据层级
            asset_type: 资产类型 (stock/index/sector)

        Returns:
            数据源名称列表（按优先级排序）
        """
        config = self.LEVEL_CONFIGS.get(level)
        if not config:
            return []

        if asset_type == 'stock':
            sources = config.stock_sources
        elif asset_type == 'index':
            sources = config.index_sources
        elif asset_type == 'sector':
            sources = config.sector_sources
        else:
            sources = config.stock_sources

        # 过滤掉不可用的数据源
        return [s for s in sources if s not in self._unavailable_sources]

    def select_best(
        self,
        level: DataLevel,
        available: Optional[List[str]] = None,
        asset_type: str = 'stock'
    ) -> Optional[str]:
        """从可用数据源中选择最优的

        Args:
            level: 数据层级
            available: 可用数据源列表（如果为 None，使用内部维护的列表）
            asset_type: 资产类型

        Returns:
            最优数据源名称，如果无可用数据源则返回 None
        """
        sources = self.get_sources(level, asset_type)

        if available is not None:
            # 只考虑明确标记为可用的数据源
            sources = [s for s in sources if s in available]

        return sources[0] if sources else None

    def supports(self, source_name: str, level: DataLevel, asset_type: str = 'stock') -> bool:
        """检查数据源是否支持指定层级和资产类型

        Args:
            source_name: 数据源名称
            level: 数据层级
            asset_type: 资产类型

        Returns:
            是否支持
        """
        sources = self.get_sources(level, asset_type)
        return source_name in sources

    def get_supported_levels(self, source_name: str) -> List[DataLevel]:
        """获取数据源支持的所有层级

        Args:
            source_name: 数据源名称

        Returns:
            支持的层级列表
        """
        levels = []
        for level in DataLevel:
            if self.supports(source_name, level, 'stock') or \
               self.supports(source_name, level, 'index') or \
               self.supports(source_name, level, 'sector'):
                levels.append(level)
        return levels

    def set_available_sources(self, sources: List[str]) -> None:
        """设置可用数据源列表

        Args:
            sources: 可用数据源名称列表
        """
        self._available_sources = set(sources)
        self._unavailable_sources = set()

    def mark_unavailable(self, source: str) -> None:
        """标记数据源为不可用

        Args:
            source: 数据源名称
        """
        self._unavailable_sources.add(source)
        self._available_sources.discard(source)

    def mark_available(self, source: str) -> None:
        """标记数据源为可用

        Args:
            source: 数据源名称
        """
        self._available_sources.add(source)
        self._unavailable_sources.discard(source)

    def reset_available(self) -> None:
        """重置所有数据源为可用状态"""
        self._available_sources = set()
        self._unavailable_sources = set()

    def get_available_sources(self) -> Set[str]:
        """获取当前标记为可用的数据源"""
        return self._available_sources.copy()

    def is_available(self, source: str) -> bool:
        """检查数据源是否可用"""
        return source in self._available_sources and source not in self._unavailable_sources


# 单例实例
_level_router: Optional[LevelRouter] = None


def get_level_router() -> LevelRouter:
    """获取 LevelRouter 单例实例"""
    global _level_router
    if _level_router is None:
        _level_router = LevelRouter()
    return _level_router

"""
统一数据源选择器

结合 LevelRouter 和 CodeTypeFilter，提供统一的数据源选择接口
"""

from typing import Dict, List, Optional, Set
from dataclasses import dataclass

from .level_router import DataLevel, LevelRouter, get_level_router
from .code_filter import CodeTypeFilter, get_code_filter
from myquant.core.market.models.stock import AssetType


@dataclass
class SelectionResult:
    """数据源选择结果"""
    primary_source: Optional[str]      # 首选数据源
    fallback_chain: List[str]          # 降级链
    asset_type: AssetType              # 资产类型
    reason: str = ""                   # 选择原因


class SourceSelector:
    """统一数据源选择器

    根据数据层级和代码类型选择最优数据源
    """

    def __init__(self):
        self._level_router = get_level_router()
        self._code_filter = get_code_filter()
        self._unavailable_sources: Set[str] = set()

    def select(
        self,
        level: DataLevel,
        asset_type: AssetType,
        available: Optional[Set[str]] = None,
        period: Optional[str] = None
    ) -> Optional[str]:
        """选择最优数据源

        Args:
            level: 数据层级
            asset_type: 资产类型
            available: 可用数据源集合（如果为 None，使用内部维护的列表）
            period: 周期（预留参数，服务层可使用）

        Returns:
            最优数据源名称，无可用数据源时返回 None
        """
        # 获取该层级支持的数据源
        asset_type_str = asset_type.value if isinstance(asset_type, AssetType) else asset_type
        sources = self._level_router.get_sources(level, asset_type_str)

        # 过滤不可用数据源
        sources = self._filter_available(sources)

        # 如果提供了可用数据源集合，进一步过滤
        if available is not None:
            sources = [s for s in sources if s in available]

        # 过滤出支持该资产类型的数据源
        sources = self._code_filter.filter_sources(sources, asset_type)

        return sources[0] if sources else None

    def select_by_code(
        self,
        level: DataLevel,
        code: str,
        available: Optional[Set[str]] = None,
        period: Optional[str] = None
    ) -> Optional[str]:
        """根据代码选择最优数据源

        Args:
            level: 数据层级
            code: 代码
            available: 可用数据源集合
            period: 周期（预留参数，服务层可使用）

        Returns:
            最优数据源名称
        """
        asset_type = self._code_filter.get_asset_type(code)
        return self.select(level, asset_type, available, period)

    def get_fallback_chain(
        self,
        level: DataLevel,
        asset_type: AssetType,
        period: Optional[str] = None
    ) -> List[str]:
        """获取降级链

        Args:
            level: 数据层级
            asset_type: 资产类型
            period: 周期（预留参数，服务层可使用）

        Returns:
            数据源降级链（按优先级排序）
        """
        # 确保 asset_type 是 AssetType 枚举
        if isinstance(asset_type, str):
            from myquant.core.market.models.stock import AssetType
            # 尝试将字符串转换为枚举
            try:
                asset_type = AssetType(asset_type)
            except ValueError:
                # 如果转换失败，默认使用 STOCK
                asset_type = AssetType.STOCK

        asset_type_str = asset_type.value if isinstance(asset_type, AssetType) else asset_type
        # 不传递 period 给 level_router，交易时间逻辑由服务层处理
        sources = self._level_router.get_sources(level, asset_type_str)

        # 过滤不可用和不支持的数据源
        sources = self._filter_available(sources)
        sources = self._code_filter.filter_sources(sources, asset_type)

        return sources

    def get_fallback_chain_for_code(
        self,
        level: DataLevel,
        code: str,
        period: Optional[str] = None
    ) -> List[str]:
        """根据代码获取降级链

        Args:
            level: 数据层级
            code: 代码
            period: 周期（预留参数，服务层可使用）

        Returns:
            数据源降级链
        """
        asset_type = self._code_filter.get_asset_type(code)
        return self.get_fallback_chain(level, asset_type, period)

    def batch_select(
        self,
        level: DataLevel,
        codes: List[str],
        available: Optional[Set[str]] = None
    ) -> Dict[str, Optional[str]]:
        """批量选择数据源

        Args:
            level: 数据层级
            codes: 代码列表
            available: 可用数据源集合

        Returns:
            {code: source} 字典
        """
        result = {}
        for code in codes:
            result[code] = self.select_by_code(level, code, available)
        return result

    def group_by_source(
        self,
        level: DataLevel,
        codes: List[str]
    ) -> Dict[str, List[str]]:
        """按数据源分组代码

        Args:
            level: 数据层级
            codes: 代码列表

        Returns:
            {source: [codes]} 字典
        """
        groups: Dict[str, List[str]] = {}
        for code in codes:
            source = self.select_by_code(level, code)
            if source:
                if source not in groups:
                    groups[source] = []
                groups[source].append(code)
        return groups

    def get_recommendation(
        self,
        level: DataLevel,
        code: str,
        context: Optional[Dict] = None
    ) -> SelectionResult:
        """获取数据源推荐详情

        Args:
            level: 数据层级
            code: 代码
            context: 额外上下文信息

        Returns:
            SelectionResult
        """
        asset_type = self._code_filter.get_asset_type(code)

        # 获取首选数据源
        primary_source = self.select_by_code(level, code)
        if not primary_source:
            return SelectionResult(
                primary_source=None,
                fallback_chain=[],
                asset_type=asset_type,
                reason=f"没有数据源支持 {asset_type.value} 的 {level.value} 数据"
            )

        # 获取降级链
        fallback_chain = self.get_fallback_chain_for_code(level, code)
        if primary_source in fallback_chain:
            fallback_chain = [s for s in fallback_chain if s != primary_source]

        reason = f"{primary_source} 是 {asset_type.value} 的 {level.value} 最优数据源"
        if fallback_chain:
            reason += f"，降级链: {fallback_chain}"

        return SelectionResult(
            primary_source=primary_source,
            fallback_chain=fallback_chain,
            asset_type=asset_type,
            reason=reason
        )

    def is_available(self, source: str) -> bool:
        """检查数据源是否可用"""
        return source not in self._unavailable_sources

    def mark_unavailable(self, source: str) -> None:
        """标记数据源为不可用"""
        self._unavailable_sources.add(source)
        self._level_router.mark_unavailable(source)

    def mark_available(self, source: str) -> None:
        """标记数据源为可用"""
        self._unavailable_sources.discard(source)
        self._level_router.mark_available(source)

    def reset_available(self) -> None:
        """重置所有数据源状态"""
        self._unavailable_sources.clear()
        self._level_router.reset_available()

    def _filter_available(self, sources: List[str]) -> List[str]:
        """过滤掉不可用的数据源"""
        return [s for s in sources if s not in self._unavailable_sources]

    def get_status(self) -> Dict:
        """获取选择器状态"""
        return {
            "unavailable_sources": list(self._unavailable_sources),
            "level_router_available": list(self._level_router.get_available_sources()),
        }


# 单例实例
_source_selector: Optional[SourceSelector] = None


def get_source_selector() -> SourceSelector:
    """获取 SourceSelector 单例实例"""
    global _source_selector
    if _source_selector is None:
        _source_selector = SourceSelector()
    return _source_selector

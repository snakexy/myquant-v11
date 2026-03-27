"""
数据源健康检查

检查数据源的连接状态和可用性
"""

import asyncio
from typing import Dict, List, Optional, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum


class HealthStatus(str, Enum):
    """健康状态"""
    HEALTHY = "healthy"        # 健康
    DEGRADED = "degraded"      # 降级（部分功能可用）
    UNHEALTHY = "unhealthy"    # 不健康（不可用）
    UNKNOWN = "unknown"        # 未知（未检查）


@dataclass
class HealthInfo:
    """健康信息"""
    status: HealthStatus
    last_check: Optional[datetime] = None
    error_message: str = ""
    response_time_ms: float = 0.0
    consecutive_failures: int = 0
    last_success: Optional[datetime] = None

    @property
    def is_healthy(self) -> bool:
        return self.status == HealthStatus.HEALTHY

    @property
    def is_available(self) -> bool:
        return self.status in (HealthStatus.HEALTHY, HealthStatus.DEGRADED)


class HealthChecker:
    """数据源健康检查器

    检查各数据源的连接状态，标记不可用数据源
    """

    def __init__(self, check_interval_seconds: int = 60):
        self._health_info: Dict[str, HealthInfo] = {}
        self._check_interval = check_interval_seconds
        self._unhealthy_sources: Set[str] = set()

    def is_healthy(self, source: str) -> bool:
        """检查数据源是否健康

        Args:
            source: 数据源名称

        Returns:
            是否健康
        """
        info = self._health_info.get(source)
        if info is None:
            return True  # 未检查过的默认认为健康
        return info.is_healthy

    def is_available(self, source: str) -> bool:
        """检查数据源是否可用（健康或降级）

        Args:
            source: 数据源名称

        Returns:
            是否可用
        """
        info = self._health_info.get(source)
        if info is None:
            return True
        return info.is_available

    def get_status(self, source: str) -> HealthInfo:
        """获取数据源健康信息

        Args:
            source: 数据源名称

        Returns:
            HealthInfo
        """
        if source not in self._health_info:
            self._health_info[source] = HealthInfo(status=HealthStatus.UNKNOWN)
        return self._health_info[source]

    def mark_healthy(self, source: str, response_time_ms: float = 0.0) -> None:
        """标记数据源为健康

        Args:
            source: 数据源名称
            response_time_ms: 响应时间（毫秒）
        """
        now = datetime.now()
        info = self.get_status(source)
        info.status = HealthStatus.HEALTHY
        info.last_check = now
        info.last_success = now
        info.response_time_ms = response_time_ms
        info.consecutive_failures = 0
        info.error_message = ""
        self._unhealthy_sources.discard(source)

    def mark_unhealthy(self, source: str, error_message: str = "") -> None:
        """标记数据源为不健康

        Args:
            source: 数据源名称
            error_message: 错误信息
        """
        now = datetime.now()
        info = self.get_status(source)
        info.status = HealthStatus.UNHEALTHY
        info.last_check = now
        info.consecutive_failures += 1
        info.error_message = error_message
        self._unhealthy_sources.add(source)

    def mark_degraded(self, source: str, reason: str = "") -> None:
        """标记数据源为降级

        Args:
            source: 数据源名称
            reason: 降级原因
        """
        now = datetime.now()
        info = self.get_status(source)
        info.status = HealthStatus.DEGRADED
        info.last_check = now
        info.error_message = reason
        self._unhealthy_sources.discard(source)

    def get_healthy_sources(self) -> List[str]:
        """获取所有健康的数据源"""
        return [
            source for source, info in self._health_info.items()
            if info.is_healthy
        ]

    def get_available_sources(self) -> List[str]:
        """获取所有可用的数据源（健康或降级）"""
        return [
            source for source, info in self._health_info.items()
            if info.is_available
        ]

    def get_unhealthy_sources(self) -> List[str]:
        """获取所有不健康的数据源"""
        return list(self._unhealthy_sources)

    def get_all_status(self) -> Dict[str, HealthInfo]:
        """获取所有数据源的健康状态"""
        return self._health_info.copy()

    async def check(self, source: str, check_func: Optional[callable] = None) -> bool:
        """检查单个数据源

        Args:
            source: 数据源名称
            check_func: 检查函数（如果为 None，使用默认检查）

        Returns:
            是否健康
        """
        start_time = datetime.now()

        try:
            if check_func is not None:
                await check_func()
            else:
                # 默认检查：尝试导入适配器并检查连接
                await self._default_check(source)

            response_time = (datetime.now() - start_time).total_seconds() * 1000
            self.mark_healthy(source, response_time)
            return True

        except Exception as e:
            self.mark_unhealthy(source, str(e))
            return False

    async def check_all(self, check_funcs: Optional[Dict[str, callable]] = None) -> Dict[str, bool]:
        """检查所有数据源

        Args:
            check_funcs: {source: check_func} 字典，如果为 None 则使用默认检查

        Returns:
            {source: is_healthy} 字典
        """
        sources = ['pytdx', 'xtquant', 'tdxquant', 'localdb', 'tdxlocal']
        results = {}

        tasks = []
        for source in sources:
            check_func = check_funcs.get(source) if check_funcs else None
            tasks.append(self.check(source, check_func))

        results_list = await asyncio.gather(*tasks, return_exceptions=True)

        for source, result in zip(sources, results_list):
            if isinstance(result, Exception):
                results[source] = False
            else:
                results[source] = result

        return results

    async def _default_check(self, source: str) -> None:
        """默认检查函数

        使用V5适配器检查数据源可用性
        """
        from myquant.core.market.adapters import get_adapter
        adapter = get_adapter(source)
        if adapter is None:
            raise ValueError(f"未知适配器: {source}")
        if not adapter.is_available():
            raise ConnectionError(f"{source} 不可用")

    def get_summary(self) -> Dict:
        """获取健康检查摘要"""
        healthy = self.get_healthy_sources()
        available = self.get_available_sources()
        unhealthy = self.get_unhealthy_sources()

        return {
            "total": len(self._health_info),
            "healthy": len(healthy),
            "available": len(available),
            "unhealthy": len(unhealthy),
            "healthy_sources": healthy,
            "unhealthy_sources": unhealthy,
            "last_check": max(
                (info.last_check for info in self._health_info.values() if info.last_check),
                default=None
            )
        }


# 单例实例
_health_checker: Optional[HealthChecker] = None


def get_health_checker(check_interval_seconds: int = 60) -> HealthChecker:
    """获取 HealthChecker 单例实例"""
    global _health_checker
    if _health_checker is None:
        _health_checker = HealthChecker(check_interval_seconds)
    return _health_checker

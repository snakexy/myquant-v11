# -*- coding: utf-8 -*-
"""
统一缓存管理服务

职责：
1. 管理所有业务缓存（K线、XDXR、因子表等）
2. 提供统一的缓存API
3. 支持缓存分区（按数据类型）
4. 自动LRU淘汰和过期清理
5. 内存使用监控

架构：
┌─────────────────────────────────────────┐
│         CacheManagerService             │
│  ┌─────────────────────────────────────┐│
│  │  Partition Manager                  ││
│  │  ├─ raw_kline (HotDB原始数据)       ││
│  │  ├─ merged_kline (拼接结果)         ││
│  │  ├─ xdxr (除权除息)                 ││
│  │  ├─ factor (复权因子)               ││
│  │  └─ snapshot (快照数据)             ││
│  └─────────────────────────────────────┘│
│  ┌─────────────────────────────────────┐│
│  │  Memory Monitor                     ││
│  │  ├─ Total usage tracking            ││
│  │  ├─ Per-partition quotas            ││
│  │  └─ Auto-eviction triggers          ││
│  └─────────────────────────────────────┘│
└─────────────────────────────────────────┘
"""

from typing import Any, Dict, Optional, List
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import sys
from loguru import logger
from threading import Lock

from myquant.core.market.services.cache import TTLCache


class CachePartition(Enum):
    """缓存分区枚举"""
    RAW_KLINE = "raw_kline"       # HotDB原始K线数据
    MERGED_KLINE = "merged_kline" # 拼接后的K线（历史+实时+复权）
    XDXR = "xdxr"                 # 除权除息数据
    FACTOR = "factor"             # 复权因子
    SNAPSHOT = "snapshot"         # 实时快照数据


@dataclass
class PartitionConfig:
    """分区配置"""
    maxsize: int           # 最大条目数
    default_ttl: int       # 默认TTL（秒）
    max_memory_mb: int     # 最大内存限制（MB），0表示不限制
    description: str = ""


# 默认分区配置 - 完全禁用缓存以隔离内存问题
DEFAULT_PARTITION_CONFIGS: Dict[CachePartition, PartitionConfig] = {
    # 原始K线分区：禁用
    CachePartition.RAW_KLINE: PartitionConfig(
        maxsize=0,  # 完全禁用
        default_ttl=0,
        max_memory_mb=0,
        description="已禁用"
    ),

    # 拼接K线分区：禁用
    CachePartition.MERGED_KLINE: PartitionConfig(
        maxsize=0,  # 完全禁用
        default_ttl=0,
        max_memory_mb=0,
        description="已禁用"
    ),

    # 其他分区也禁用
    CachePartition.XDXR: PartitionConfig(maxsize=0, default_ttl=0, max_memory_mb=0, description="已禁用"),
    CachePartition.FACTOR: PartitionConfig(maxsize=0, default_ttl=0, max_memory_mb=0, description="已禁用"),
    CachePartition.SNAPSHOT: PartitionConfig(maxsize=0, default_ttl=0, max_memory_mb=0, description="已禁用"),
}


@dataclass
class CacheStats:
    """缓存统计信息"""
    partition: CachePartition
    size: int = 0
    maxsize: int = 0
    hits: int = 0
    misses: int = 0
    hit_rate: float = 0.0
    memory_mb: float = 0.0
    max_memory_mb: int = 0


class CacheManagerService:
    """统一缓存管理服务

    特性：
    1. 分区隔离：不同类型数据独立管理
    2. 自动淘汰：LRU + TTL双重淘汰
    3. 内存监控：实时跟踪内存使用
    4. 统一接口：get/set/delete/clear
    5. 统计信息：命中率、内存占用等
    6. 自动清理：内存过高时自动清理
    """

    def __init__(
        self,
        partition_configs: Optional[Dict[CachePartition, PartitionConfig]] = None
    ):
        """初始化缓存管理器

        Args:
            partition_configs: 分区配置（None使用默认配置）
        """
        self._configs = partition_configs or DEFAULT_PARTITION_CONFIGS.copy()
        self._partitions: Dict[CachePartition, TTLCache] = {}
        self._stats: Dict[CachePartition, CacheStats] = {}
        self._lock = Lock()

        # 自动清理配置
        self._auto_cleanup_enabled = True
        self._auto_cleanup_threshold_mb = 200  # 超过200MB自动清理
        self._last_cleanup_time = 0
        self._cleanup_interval = 30  # 清理间隔（秒）

        # 初始化各分区
        for partition, config in self._configs.items():
            self._partitions[partition] = TTLCache(
                maxsize=config.maxsize,
                ttl=config.default_ttl
            )
            self._stats[partition] = CacheStats(
                partition=partition,
                maxsize=config.maxsize,
                max_memory_mb=config.max_memory_mb
            )

        logger.info(
            f"[CacheManager] 初始化完成: {len(self._partitions)} 个分区，自动清理阈值: {self._auto_cleanup_threshold_mb}MB"
        )

    # ── 核心 API ─────────────────────────────────────────

    def get(
        self,
        partition: CachePartition,
        key: str
    ) -> Optional[Any]:
        """获取缓存值

        Args:
            partition: 缓存分区
            key: 缓存键

        Returns:
            缓存值，不存在返回None
        """
        cache = self._partitions.get(partition)
        if not cache:
            logger.warning(f"[CacheManager] 未知分区: {partition}")
            return None

        value = cache.get(key)

        # 更新统计
        with self._lock:
            stats = self._stats[partition]
            if value is not None:
                stats.hits += 1
            else:
                stats.misses += 1

        return value

    def set(
        self,
        partition: CachePartition,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """设置缓存值

        Args:
            partition: 缓存分区
            key: 缓存键
            value: 缓存值
            ttl: 过期时间（秒），None使用分区默认值

        Returns:
            是否设置成功
        """
        cache = self._partitions.get(partition)
        if not cache:
            logger.warning(f"[CacheManager] 未知分区: {partition}")
            return False

        cache.set(key, value, ttl=ttl)

        # 更新统计
        with self._lock:
            stats = self._stats[partition]
            stats.size = cache.get_stats()['size']

        # 自动清理检查
        self._auto_cleanup_if_needed()

        return True

    def delete(
        self,
        partition: CachePartition,
        key: str
    ) -> bool:
        """删除缓存值

        Args:
            partition: 缓存分区
            key: 缓存键

        Returns:
            是否删除成功
        """
        cache = self._partitions.get(partition)
        if not cache:
            return False

        return cache.delete(key)

    def clear_partition(
        self,
        partition: CachePartition
    ) -> bool:
        """清空指定分区

        Args:
            partition: 缓存分区

        Returns:
            是否清空成功
        """
        cache = self._partitions.get(partition)
        if not cache:
            return False

        cache.clear()

        with self._lock:
            self._stats[partition].size = 0

        logger.info(f"[CacheManager] 已清空分区: {partition}")
        return True

    def clear_all(self) -> None:
        """清空所有缓存"""
        for partition in self._partitions:
            self.clear_partition(partition)

        logger.info("[CacheManager] 已清空所有缓存")

    def _auto_cleanup_if_needed(self) -> None:
        """自动清理：如果内存超过阈值，清理缓存"""
        if not self._auto_cleanup_enabled:
            return

        import time
        now = time.time()
        if now - self._last_cleanup_time < self._cleanup_interval:
            return

        try:
            import psutil
            import os
            process = psutil.Process(os.getpid())
            rss_mb = process.memory_info().rss / 1024 / 1024

            if rss_mb > self._auto_cleanup_threshold_mb:
                logger.info(f"[CacheManager] 内存过高 ({rss_mb:.1f}MB)，触发自动清理")

                # 清理一半的缓存条目
                for partition in self._partitions:
                    self.force_evict(partition, max_keep=50)

                # 强制垃圾回收
                import gc
                gc.collect()

                self._last_cleanup_time = now

                new_rss_mb = process.memory_info().rss / 1024 / 1024
                logger.info(f"[CacheManager] 自动清理完成: {rss_mb:.1f}MB → {new_rss_mb:.1f}MB")
        except Exception as e:
            logger.debug(f"[CacheManager] 自动清理失败: {e}")

    def force_evict(self, partition: CachePartition, max_keep: int = 50) -> int:
        """强制淘汰缓存，只保留最近使用的条目

        Args:
            partition: 缓存分区
            max_keep: 保留的最大条目数

        Returns:
            淘汰的条目数
        """
        cache = self._partitions.get(partition)
        if not cache:
            return 0

        current_size = cache.get_stats()['size']
        if current_size <= max_keep:
            return 0

        # 获取所有缓存键并按时间排序（最旧的先删除）
        keys_to_remove = list(cache._cache.keys())[:-max_keep]
        for key in keys_to_remove:
            cache.delete(key)

        logger.info(f"[CacheManager] 强制淘汰 {partition}: 保留 {max_keep}/{current_size}, 删除 {len(keys_to_remove)}")
        return len(keys_to_remove)

    def cleanup_old_entries(self, partition: CachePartition, max_age_seconds: int = 300) -> int:
        """清理超过指定时间的缓存条目

        Args:
            partition: 缓存分区
            max_age_seconds: 最大保留时间（秒）

        Returns:
            清理的条目数
        """
        import time
        cache = self._partitions.get(partition)
        if not cache:
            return 0

        current_time = time.time()
        keys_to_remove = []

        for key, entry in cache._cache.items():
            age = current_time - entry.created_at.timestamp()
            if age > max_age_seconds:
                keys_to_remove.append(key)

        for key in keys_to_remove:
            cache.delete(key)

        if keys_to_remove:
            logger.info(f"[CacheManager] 清理过期条目 {partition}: 删除 {len(keys_to_remove)} 个")
        return len(keys_to_remove)

    # ── 统计信息 ─────────────────────────────────────────

    def get_stats(
        self,
        partition: Optional[CachePartition] = None
    ) -> Dict[str, Any]:
        """获取缓存统计信息

        Args:
            partition: 指定分区（None返回所有）

        Returns:
            统计信息字典
        """
        # 更新统计数据
        self._update_stats()

        if partition:
            stats = self._stats.get(partition)
            if stats:
                total_requests = stats.hits + stats.misses
                hit_rate = stats.hits / total_requests if total_requests > 0 else 0

                return {
                    'partition': partition.value,
                    'size': stats.size,
                    'maxsize': stats.maxsize,
                    'hits': stats.hits,
                    'misses': stats.misses,
                    'hit_rate': hit_rate,
                    'memory_mb': stats.memory_mb,
                    'max_memory_mb': stats.max_memory_mb,
                }
            return {}
        else:
            # 返回所有分区统计 + 总计
            result = {
                'partitions': {},
                'total': {
                    'hits': 0,
                    'misses': 0,
                    'hit_rate': 0.0,
                    'memory_mb': 0.0,
                }
            }

            for p, stats in self._stats.items():
                partition_stats = self.get_stats(p)
                result['partitions'][p.value] = partition_stats

                # 累加总计
                result['total']['hits'] += stats.hits
                result['total']['misses'] += stats.misses
                result['total']['memory_mb'] += stats.memory_mb

            # 计算总命中率
            total_requests = (
                result['total']['hits'] + result['total']['misses']
            )
            if total_requests > 0:
                result['total']['hit_rate'] = (
                    result['total']['hits'] / total_requests
                )

            return result

    def get_memory_usage(self) -> Dict[str, float]:
        """获取内存使用情况

        Returns:
            {
                'cache_mb': 缓存总内存,
                'partitions': {分区名: 内存MB}
            }
        """
        self._update_stats()

        return {
            'cache_mb': sum(s.memory_mb for s in self._stats.values()),
            'partitions': {
                p.value: s.memory_mb
                for p, s in self._stats.items()
            }
        }

    # ── 内部方法 ─────────────────────────────────────────

    def _update_stats(self) -> None:
        """更新所有分区统计"""
        for partition, cache in self._partitions.items():
            cache_stats = cache.get_stats()

            with self._lock:
                stats = self._stats[partition]
                stats.size = cache_stats['size']
                stats.hits = cache_stats['hits']
                stats.misses = cache_stats['misses']
                # 简单估算内存：假设平均每条目100KB
                stats.memory_mb = stats.size * 0.1


# ─────────────────────────────────────────────────────────
# 全局单例
# ─────────────────────────────────────────────────────────

_cache_manager_instance: Optional[CacheManagerService] = None


def get_cache_manager() -> CacheManagerService:
    """获取 CacheManagerService 单例"""
    global _cache_manager_instance
    if _cache_manager_instance is None:
        _cache_manager_instance = CacheManagerService()
    return _cache_manager_instance

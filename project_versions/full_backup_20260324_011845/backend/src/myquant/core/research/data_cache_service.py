# -*- coding: utf-8 -*-
"""
数据管理模块 - Redis缓存适配器
Data Management Cache Adapter

职责：
- 为数据管理模块提供专用的缓存接口
- 复用底层CacheManager
- 提供便捷的缓存装饰器

版本: v1.0
创建日期: 2026-02-11
"""

import functools
import json
from typing import Optional, Any, Dict, List, Callable
from datetime import datetime
from loguru import logger
from enum import Enum


class DataCacheKeyType(Enum):
    """数据管理缓存键类型"""
    # 股票相关
    STOCK_SEARCH_INDEX = "stock_search_index"      # 股票搜索索引
    STOCK_LIST = "stock_list"                        # 股票列表
    STOCK_INFO = "stock_info"                        # 单个股票信息

    # 统计相关
    DATABASE_STATS = "database_stats"                # 数据库统计
    CATEGORY_STATS = "category_stats"                # 分类统计

    # 服务相关
    SERVICE_STATS = "service_stats"                  # 服务状态


class DataCacheTTLPolicy:
    """数据管理缓存TTL策略（秒）"""

    TTL_POLICY = {
        # 股票搜索索引 - 24小时（股票名称变化极少）
        DataCacheKeyType.STOCK_SEARCH_INDEX: 86400,

        # 股票列表 - 1分钟（需要相对新鲜）
        DataCacheKeyType.STOCK_LIST: 60,

        # 单个股票信息 - 30分钟
        DataCacheKeyType.STOCK_INFO: 1800,

        # 数据库统计 - 5分钟（避免频繁扫描）
        DataCacheKeyType.DATABASE_STATS: 300,

        # 分类统计 - 10分钟
        DataCacheKeyType.CATEGORY_STATS: 600,

        # 服务状态 - 2分钟
        DataCacheKeyType.SERVICE_STATS: 120,
    }

    @classmethod
    def get_ttl(cls, key_type: DataCacheKeyType) -> int:
        """获取指定键类型的TTL"""
        return cls.TTL_POLICY.get(key_type, 60)  # 默认60秒


class DataCacheService:
    """
    数据管理缓存服务

    功能：
    1. 统一的缓存键管理
    2. 便捷的缓存装饰器
    3. 缓存统计与失效
    """

    def __init__(self):
        """初始化缓存服务"""
        self._cache_manager = None
        self._enabled = False

    async def initialize(self):
        """初始化缓存服务"""
        try:
            from core.cache import cache_manager
            self._cache_manager = cache_manager
            self._enabled = await cache_manager.initialize()
            logger.info(f"[数据缓存] 初始化{'成功' if self._enabled else '失败（已降级）'}")
        except ImportError as e:
            logger.warning(f"[数据缓存] 导入CacheManager失败: {e}")
            self._enabled = False
        except Exception as e:
            logger.warning(f"[数据缓存] 初始化失败: {e}")
            self._enabled = False

    def _build_key(self, key_type: DataCacheKeyType, identifier: str = "") -> str:
        """
        构建缓存键

        Args:
            key_type: 键类型
            identifier: 标识符

        Returns:
            缓存键
        """
        prefix = "data_mgmt"
        if identifier:
            return f"{prefix}:{key_type.value}:{identifier}"
        return f"{prefix}:{key_type.value}"

    async def get(self, key_type: DataCacheKeyType, identifier: str = "") -> Optional[Any]:
        """
        获取缓存

        Args:
            key_type: 键类型
            identifier: 标识符

        Returns:
            缓存值或None
        """
        if not self._enabled:
            return None

        try:
            key = self._build_key(key_type, identifier)
            return await self._cache_manager.get(key)
        except Exception as e:
            logger.warning(f"[数据缓存] 获取失败 {key_type.value}:{identifier} - {e}")
            return None

    async def set(
        self,
        key_type: DataCacheKeyType,
        value: Any,
        identifier: str = "",
        custom_ttl: Optional[int] = None
    ) -> bool:
        """
        设置缓存

        Args:
            key_type: 键类型
            value: 缓存值
            identifier: 标识符
            custom_ttl: 自定义TTL（可选）

        Returns:
            是否设置成功
        """
        if not self._enabled:
            return False

        try:
            key = self._build_key(key_type, identifier)
            ttl = custom_ttl if custom_ttl is not None else DataCacheTTLPolicy.get_ttl(key_type)
            return await self._cache_manager.set(key, value, expire=ttl)
        except Exception as e:
            logger.warning(f"[数据缓存] 设置失败 {key_type.value}:{identifier} - {e}")
            return False

    async def delete(self, key_type: DataCacheKeyType, identifier: str = "") -> bool:
        """
        删除缓存

        Args:
            key_type: 键类型
            identifier: 标识符

        Returns:
            是否删除成功
        """
        if not self._enabled:
            return False

        try:
            key = self._build_key(key_type, identifier)
            return await self._cache_manager.delete(key)
        except Exception as e:
            logger.warning(f"[数据缓存] 删除失败 {key_type.value}:{identifier} - {e}")
            return False

    async def invalidate_type(self, key_type: DataCacheKeyType) -> int:
        """
        使指定类型的所有缓存失效

        Args:
            key_type: 键类型

        Returns:
            失效的缓存数量
        """
        if not self._enabled:
            return 0

        try:
            pattern = self._build_key(key_type, "*")
            return await self._cache_manager.clear_pattern(pattern)
        except Exception as e:
            logger.warning(f"[数据缓存] 批量失效失败 {key_type.value} - {e}")
            return 0

    async def get_stats(self) -> Dict[str, Any]:
        """
        获取缓存统计信息

        Returns:
            统计信息
        """
        if not self._enabled:
            return {"enabled": False}

        try:
            stats = await self._cache_manager.get_stats()
            stats["module"] = "data_management"
            return stats
        except Exception as e:
            logger.warning(f"[数据缓存] 获取统计失败 - {e}")
            return {"enabled": True, "error": str(e)}

    def cached_result(self, key_type: DataCacheKeyType, identifier_arg: str = ""):
        """
        缓存装饰器 - 缓存函数结果

        Args:
            key_type: 键类型
            identifier_arg: 作为标识符的参数名（默认使用第一个参数）

        Returns:
            装饰器函数
        """

        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            async def wrapper(*args, **kwargs):
                if not self._enabled:
                    # 缓存未启用，直接调用原函数
                    return await func(*args, **kwargs)

                # 构建缓存标识符
                if identifier_arg and identifier_arg in kwargs:
                    identifier = str(kwargs[identifier_arg])
                elif args:
                    # 使用第一个参数作为标识符
                    identifier = str(args[0])
                else:
                    identifier = ""

                # 尝试从缓存获取
                cached_value = await self.get(key_type, identifier)
                if cached_value is not None:
                    logger.debug(f"[数据缓存] 命中 {key_type.value}:{identifier}")
                    return cached_value

                # 缓存未命中，调用原函数
                logger.debug(f"[数据缓存] 未命中 {key_type.value}:{identifier}")
                result = await func(*args, **kwargs)

                # 存入缓存
                if result is not None:
                    await self.set(key_type, result, identifier)

                return result

            return wrapper
        return decorator


# ==================== 全局单例 ====================

_data_cache_service: Optional[DataCacheService] = None


def get_data_cache_service() -> DataCacheService:
    """获取数据缓存服务单例"""
    global _data_cache_service
    if _data_cache_service is None:
        _data_cache_service = DataCacheService()
    return _data_cache_service


# ==================== 便捷函数 ====================

async def init_data_cache():
    """初始化数据缓存服务"""
    service = get_data_cache_service()
    await service.initialize()
    return service


async def cache_get(key_type: DataCacheKeyType, identifier: str = "") -> Optional[Any]:
    """便捷缓存获取"""
    service = get_data_cache_service()
    return await service.get(key_type, identifier)


async def cache_set(
    key_type: DataCacheKeyType,
    value: Any,
    identifier: str = "",
    custom_ttl: Optional[int] = None
) -> bool:
    """便捷缓存设置"""
    service = get_data_cache_service()
    return await service.set(key_type, value, identifier, custom_ttl)


async def cache_delete(key_type: DataCacheKeyType, identifier: str = "") -> bool:
    """便捷缓存删除"""
    service = get_data_cache_service()
    return await service.delete(key_type, identifier)


async def cache_invalidate_type(key_type: DataCacheKeyType) -> int:
    """便捷批量失效"""
    service = get_data_cache_service()
    return await service.invalidate_type(key_type)


# ==================== 测试代码 ====================

if __name__ == "__main__":
    import asyncio

    async def test_cache():
        """测试缓存服务"""
        print("=== 数据缓存服务测试 ===")

        service = get_data_cache_service()
        await service.initialize()

        # 测试缓存读写
        test_key = DataCacheKeyType.DATABASE_STATS
        test_data = {"total_stocks": 5000, "last_update": "2026-02-11"}

        # 写入
        success = await service.set(test_key, test_data)
        print(f"写入缓存: {'成功' if success else '失败'}")

        # 读取
        cached_data = await service.get(test_key)
        print(f"读取缓存: {cached_data}")

        # 删除
        deleted = await service.delete(test_key)
        print(f"删除缓存: {'成功' if deleted else '失败'}")

        # 获取统计
        stats = await service.get_stats()
        print(f"缓存统计: {stats}")

    asyncio.run(test_cache())

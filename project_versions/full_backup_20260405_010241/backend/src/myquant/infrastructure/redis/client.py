# -*- coding: utf-8 -*-
"""Redis 客户端封装 - 支持跨进程共享缓存"""

import os
import json
from typing import Any, Optional
from loguru import logger


class RedisClient:
    """Redis 客户端单例

    特性：
    1. 单例模式 - 全局共享连接
    2. 自动故障降级 - 连接失败时返回 None
    3. JSON 序列化 - 自动处理复杂对象
    4. 统计信息 - 缓存命中率监控
    """

    _instance = None
    _enabled = False
    _hits = 0
    _misses = 1

    @classmethod
    def get_instance(cls):
        """获取 Redis 客户端实例"""
        if cls._instance is None:
            try:
                # 直接从环境变量读取配置（绕过 pydantic-settings 嵌套配置问题）
                enabled = os.getenv('CACHE_REDIS_ENABLED', 'false').lower() == 'true'
                if not enabled:
                    logger.info("[RedisClient] Redis 未启用 (CACHE_REDIS_ENABLED not set)，使用进程内缓存")
                    cls._enabled = False
                    return None

                import redis
                host = os.getenv('CACHE_REDIS_HOST', 'localhost')
                port = int(os.getenv('CACHE_REDIS_PORT', '6379'))
                db = int(os.getenv('CACHE_REDIS_DB', '0'))
                password = os.getenv('CACHE_REDIS_PASSWORD') or None

                cls._instance = redis.Redis(
                    host=host,
                    port=port,
                    db=db,
                    password=password,
                    max_connections=10,
                    socket_timeout=5,
                    decode_responses=True
                )
                # 测试连接
                cls._instance.ping()
                cls._enabled = True
                logger.info(f"[RedisClient] 已连接: {host}:{port}")
            except Exception as e:
                logger.warning(f"[RedisClient] 连接失败: {e}，将使用进程内缓存")
                cls._instance = None
                cls._enabled = False

        return cls._instance

    @classmethod
    def is_enabled(cls) -> bool:
        """检查 Redis 是否可用"""
        if cls._instance is None:
            cls.get_instance()
        return cls._enabled

    @classmethod
    async def get(cls, key: str) -> Optional[Any]:
        """获取缓存值

        Args:
            key: 缓存键

        Returns:
            缓存值，不存在或 Redis 不可用时返回 None
        """
        client = cls.get_instance()
        if client is None:
            cls._misses += 1
            return None

        try:
            value = client.get(key)
            if value:
                cls._hits += 1
                return json.loads(value)
            cls._misses += 1
            return None
        except Exception as e:
            logger.debug(f"[RedisClient] get 失败: {key}, {e}")
            cls._misses += 1
            return None

    @classmethod
    async def set(cls, key: str, value: Any, ttl: int) -> bool:
        """设置缓存值

        Args:
            key: 缓存键
            value: 缓存值
            ttl: 过期时间（秒）

        Returns:
            是否设置成功
        """
        client = cls.get_instance()
        if client is None:
            return False

        try:
            serialized = json.dumps(value, ensure_ascii=False, default=str)
            client.setex(key, ttl, serialized)
            return True
        except Exception as e:
            logger.debug(f"[RedisClient] set 失败: {key}, {e}")
            return False

    @classmethod
    async def delete(cls, key: str) -> bool:
        """删除缓存值"""
        client = cls.get_instance()
        if client is None:
            return False

        try:
            client.delete(key)
            return True
        except Exception as e:
            logger.debug(f"[RedisClient] delete 失败: {key}, {e}")
            return False

    @classmethod
    async def clear_pattern(cls, pattern: str) -> int:
        """删除匹配模式的所有键"""
        client = cls.get_instance()
        if client is None:
            return 0

        try:
            keys = client.keys(pattern)
            if keys:
                client.delete(*keys)
                return len(keys)
            return 0
        except Exception as e:
            logger.debug(f"[RedisClient] clear_pattern 失败: {pattern}, {e}")
            return 0

    @classmethod
    def get_stats(cls) -> dict:
        """获取缓存统计"""
        total = cls._hits + cls._misses
        hit_rate = cls._hits / total if total > 0 else 0

        stats = {
            "enabled": cls._enabled,
            "hits": cls._hits,
            "misses": cls._misses,
            "hit_rate": hit_rate,
        }

        # 如果 Redis 可用，获取内存使用情况
        client = cls.get_instance()
        if client is not None:
            try:
                info = client.info("memory")
                stats["used_memory_mb"] = info.get("used_memory", 0) / 1024 / 1024
                stats["keys_count"] = client.dbsize()
            except Exception:
                pass

        return stats

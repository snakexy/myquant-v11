"""
多级缓存组件

提供 L1(内存) -> L2(Redis) -> L3(SQLite) 三级缓存
"""

import time
import sqlite3
import json
from typing import Any, Dict, List, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from threading import Lock
import hashlib

from myquant.core.market.models import BaseModel


def _generate_cache_key(prefix: str, key: str) -> str:
    """生成缓存键"""
    if prefix:
        return f"{prefix}:{key}"
    return key


@dataclass
class CacheEntry:
    """缓存条目"""
    key: str
    value: Any
    created_at: datetime = field(default_factory=datetime.now)
    ttl: int = 60  # 秒

    @property
    def is_expired(self) -> bool:
        """是否过期"""
        return (datetime.now() - self.created_at).total_seconds() > self.ttl


class TTLCache:
    """内存 L1 缓存（带 TTL）"""

    def __init__(self, maxsize: int = 1000, ttl: int = 60):
        self._maxsize = maxsize
        self._default_ttl = ttl
        self._cache: Dict[str, CacheEntry] = {}
        self._lock = Lock()
        self._hits = 0
        self._misses = 0

    def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        with self._lock:
            entry = self._cache.get(key)

            if entry is None:
                self._misses += 1
                return None

            if entry.is_expired:
                del self._cache[key]
                self._misses += 1
                return None

            self._hits += 1
            return entry.value

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """设置缓存值"""
        with self._lock:
            # 检查容量
            if len(self._cache) >= self._maxsize and key not in self._cache:
                self._evict_oldest()

            entry = CacheEntry(
                key=key,
                value=value,
                ttl=ttl or self._default_ttl
            )
            self._cache[key] = entry

    def delete(self, key: str) -> bool:
        """删除缓存值"""
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False

    def clear(self, keys: Optional[List[str]] = None) -> None:
        """清空缓存"""
        with self._lock:
            if keys is None:
                self._cache.clear()
            else:
                for key in keys:
                    self._cache.pop(key, None)

    def get_stats(self) -> dict:
        """获取缓存统计"""
        total_requests = self._hits + self._misses
        hit_rate = self._hits / total_requests if total_requests > 0 else 0

        return {
            "type": "TTLCache",
            "size": len(self._cache),
            "maxsize": self._maxsize,
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": hit_rate,
        }

    def _evict_oldest(self) -> None:
        """淘汰最旧的条目"""
        if not self._cache:
            return

        oldest_key = min(
            self._cache.keys(),
            key=lambda k: self._cache[k].created_at
        )
        del self._cache[oldest_key]


class RedisCache:
    """Redis L2 缓存（可选）"""

    def __init__(
        self,
        host: str = 'localhost',
        port: int = 6379,
        db: int = 0,
        password: Optional[str] = None,
        ttl: int = 300,
        enabled: bool = True
    ):
        self._host = host
        self._port = port
        self._db = db
        self._password = password
        self._default_ttl = ttl
        self._enabled = enabled
        self._client = None
        self._hits = 0
        self._misses = 0

    def _get_client(self):
        """获取 Redis 客户端"""
        if self._client is None and self._enabled:
            try:
                import redis
                self._client = redis.Redis(
                    host=self._host,
                    port=self._port,
                    db=self._db,
                    password=self._password,
                    decode_responses=True
                )
                # 测试连接
                self._client.ping()
            except Exception:
                self._enabled = False
                self._client = None

        return self._client

    def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        if not self._enabled:
            return None

        try:
            client = self._get_client()
            if client is None:
                return None

            value = client.get(key)
            if value is None:
                self._misses += 1
                return None

            self._hits += 1
            return json.loads(value)

        except Exception:
            self._misses += 1
            return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """设置缓存值"""
        if not self._enabled:
            return False

        try:
            client = self._get_client()
            if client is None:
                return False

            serialized = json.dumps(value, ensure_ascii=False, default=str)
            client.setex(key, ttl or self._default_ttl, serialized)
            return True

        except Exception:
            return False

    def delete(self, key: str) -> bool:
        """删除缓存值"""
        if not self._enabled:
            return False

        try:
            client = self._get_client()
            if client is None:
                return False

            client.delete(key)
            return True

        except Exception:
            return False

    def clear(self, keys: Optional[List[str]] = None) -> None:
        """清空缓存"""
        if not self._enabled:
            return

        try:
            client = self._get_client()
            if client is None:
                return

            if keys is None:
                # 清空当前 db
                client.flushdb()
            else:
                client.delete(*keys)

        except Exception:
            pass

    def get_stats(self) -> dict:
        """获取缓存统计"""
        total_requests = self._hits + self._misses
        hit_rate = self._hits / total_requests if total_requests > 0 else 0

        return {
            "type": "RedisCache",
            "enabled": self._enabled,
            "host": self._host if self._enabled else None,
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": hit_rate,
        }


class SQLitePersistence:
    """SQLite L3 持久化缓存"""

    def __init__(self, db_path: str = "data/cache.db", ttl_hours: int = 24):
        self._db_path = db_path
        self._ttl_hours = ttl_hours
        self._lock = Lock()
        self._init_db()

    def _init_db(self) -> None:
        """初始化数据库"""
        import os
        os.makedirs(os.path.dirname(self._db_path), exist_ok=True)

        with sqlite3.connect(self._db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS cache (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

    def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        try:
            with sqlite3.connect(self._db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT value, created_at FROM cache WHERE key = ?
                """, (key,))

                row = cursor.fetchone()
                if row is None:
                    return None

                value, created_at_str = row
                created_at = datetime.fromisoformat(created_at_str)

                # 检查是否过期
                if (datetime.now() - created_at).total_seconds() > self._ttl_hours * 3600:
                    self.delete(key)
                    return None

                return json.loads(value)

        except Exception:
            return None

    def set(self, key: str, value: Any, ttl: int = 0) -> bool:
        """设置缓存值"""
        try:
            with sqlite3.connect(self._db_path) as conn:
                serialized = json.dumps(value, ensure_ascii=False, default=str)
                conn.execute("""
                    INSERT OR REPLACE INTO cache (key, value, created_at)
                    VALUES (?, ?, CURRENT_TIMESTAMP)
                """, (key, serialized))
                conn.commit()
                return True

        except Exception:
            return False

    def delete(self, key: str) -> bool:
        """删除缓存值"""
        try:
            with sqlite3.connect(self._db_path) as conn:
                conn.execute("DELETE FROM cache WHERE key = ?", (key,))
                conn.commit()
                return True

        except Exception:
            return False

    def cleanup_expired(self) -> int:
        """清理过期数据"""
        try:
            with sqlite3.connect(self._db_path) as conn:
                cursor = conn.cursor()
                cutoff = datetime.now() - timedelta(hours=self._ttl_hours)
                cursor.execute("""
                    DELETE FROM cache WHERE created_at < ?
                """, (cutoff.isoformat(),))
                conn.commit()
                return cursor.rowcount

        except Exception:
            return 0

    def get_stats(self) -> dict:
        """获取缓存统计"""
        try:
            with sqlite3.connect(self._db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM cache")
                count = cursor.fetchone()[0]

                return {
                    "type": "SQLitePersistence",
                    "db_path": self._db_path,
                    "size": count,
                    "ttl_hours": self._ttl_hours,
                }

        except Exception:
            return {
                "type": "SQLitePersistence",
                "db_path": self._db_path,
                "size": 0,
                "ttl_hours": self._ttl_hours,
            }


class MultiLevelCache:
    """多级缓存 (L1 -> L2 -> L3)

    自动在各级缓存之间回源和降级
    """

    def __init__(
        self,
        l1_maxsize: int = 1000,
        l1_ttl: int = 60,
        l2_ttl: int = 300,
        l3_ttl_hours: int = 24,
        l3_db_path: str = "data/cache.db",
        enable_l2: bool = False,
        enable_l3: bool = True,
    ):
        self._l1 = TTLCache(maxsize=l1_maxsize, ttl=l1_ttl)
        self._l2 = RedisCache(ttl=l2_ttl, enabled=enable_l2)
        self._l3 = SQLitePersistence(db_path=l3_db_path, ttl_hours=l3_ttl_hours) if enable_l3 else None

    async def get(
        self,
        cache_key: str,
        fetch_func: Optional[Callable] = None,
        prefix: str = "",
        use_l1: bool = True,
        use_l2: bool = True,
        use_l3: bool = True
    ) -> Optional[Any]:
        """获取缓存值

        按顺序检查 L1 -> L2 -> L3，如果都不存在则调用 fetch_func

        Args:
            cache_key: 缓存键
            fetch_func: 数据获取函数（如果缓存不存在）
            prefix: 键前缀
            use_l1: 是否使用 L1 缓存
            use_l2: 是否使用 L2 缓存
            use_l3: 是否使用 L3 缓存

        Returns:
            缓存值或 fetch_func 的结果
        """
        key = _generate_cache_key(prefix, cache_key)

        # L1 缓存
        if use_l1:
            value = self._l1.get(key)
            if value is not None:
                return value

        # L2 缓存
        if use_l2:
            value = self._l2.get(key)
            if value is not None:
                # 回填 L1
                self._l1.set(key, value)
                return value

        # L3 缓存
        if use_l3 and self._l3:
            value = self._l3.get(key)
            if value is not None:
                # 回填 L1 和 L2
                self._l1.set(key, value)
                self._l2.set(key, value)
                return value

        # 回源获取数据
        if fetch_func is not None:
            value = await fetch_func() if hasattr(fetch_func, '__await__') else fetch_func()
            if value is not None:
                # 存入各级缓存
                self._l1.set(key, value)
                self._l2.set(key, value)
                if self._l3:
                    self._l3.set(key, value)
            return value

        return None

    def clear(self, keys: Optional[List[str]] = None, prefix: str = "") -> None:
        """清空缓存

        Args:
            keys: 指定的键列表（None 表示清空全部）
            prefix: 键前缀
        """
        full_keys = [_generate_cache_key(prefix, k) for k in keys] if keys else None

        self._l1.clear(full_keys)
        self._l2.clear(full_keys)

        if self._l3:
            if full_keys:
                for key in full_keys:
                    self._l3.delete(key)
            else:
                # L3 不轻易清空全部
                pass

    def get_stats(self) -> dict:
        """获取各级缓存统计"""
        stats = {
            "L1": self._l1.get_stats(),
            "L2": self._l2.get_stats(),
        }

        if self._l3:
            stats["L3"] = self._l3.get_stats()

        # 计算总命中率
        total_hits = sum(s.get('hits', 0) for s in stats.values())
        total_requests = sum(s.get('hits', 0) + s.get('misses', 0) for s in stats.values())
        total_hit_rate = total_hits / total_requests if total_requests > 0 else 0

        stats["total"] = {
            "hit_rate": total_hit_rate,
        }

        return stats

    def cleanup_l3_expired(self) -> int:
        """清理 L3 过期数据"""
        if self._l3:
            return self._l3.cleanup_expired()
        return 0


def get_cache(
    l1_maxsize: int = 1000,
    l1_ttl: int = 60,
    l2_ttl: int = 300,
    l3_ttl_hours: int = 24,
    enable_l2: bool = False,
    enable_l3: bool = True,
) -> MultiLevelCache:
    """创建多级缓存实例（便捷函数）"""
    return MultiLevelCache(
        l1_maxsize=l1_maxsize,
        l1_ttl=l1_ttl,
        l2_ttl=l2_ttl,
        l3_ttl_hours=l3_ttl_hours,
        enable_l2=enable_l2,
        enable_l3=enable_l3,
    )

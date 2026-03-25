"""
缓存管理器模块

提供增强指数策略的缓存管理功能
"""

import os
import pickle
import hashlib
import time
from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger(__name__)


class CacheManager:
    """
    缓存管理器
    
    提供通用的缓存管理功能，支持多种缓存策略和过期策略。
    """
    
    def __init__(
        self,
        cache_dir: str = "./cache",
        max_size: int = 1000,
        ttl_seconds: int = 3600,
        verbose: bool = False
    ):
        """
        初始化缓存管理器
        
        Parameters
        ----------
        cache_dir : str, default "./cache"
            缓存目录
        max_size : int, default 1000
            最大缓存条目数
        ttl_seconds : int, default 3600
            缓存生存时间（秒）
        verbose : bool, default False
            是否输出详细日志
        """
        self.cache_dir = cache_dir
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.verbose = verbose
        
        # 内存缓存
        self._memory_cache = {}
        self._cache_timestamps = {}
        
        # 确保缓存目录存在
        os.makedirs(cache_dir, exist_ok=True)
        
        if self.verbose:
            logger.info("缓存管理器初始化完成")
            logger.info(f"缓存目录: {cache_dir}")
            logger.info(f"最大缓存大小: {max_size}")
            logger.info(f"缓存生存时间: {ttl_seconds}秒")
    
    def get(self, key: str) -> Optional[Any]:
        """
        获取缓存值
        
        Parameters
        ----------
        key : str
            缓存键
            
        Returns
        -------
        Any or None
            缓存值
        """
        try:
            # 检查内存缓存
            if key in self._memory_cache:
                timestamp = self._cache_timestamps[key]
                if self._is_valid(timestamp):
                    if self.verbose:
                        logger.debug(f"从内存缓存获取键: {key}")
                    return self._memory_cache[key]
                else:
                    # 过期，从内存缓存中删除
                    del self._memory_cache[key]
                    del self._cache_timestamps[key]
            
            # 检查磁盘缓存
            cache_file = self._get_cache_file_path(key)
            if os.path.exists(cache_file):
                with open(cache_file, 'rb') as f:
                    cache_data = pickle.load(f)
                
                if self._is_valid(cache_data.get('timestamp', 0)):
                    # 加载到内存缓存
                    self._memory_cache[key] = cache_data['value']
                    self._cache_timestamps[key] = cache_data['timestamp']
                    
                    if self.verbose:
                        logger.debug(f"从磁盘缓存获取键: {key}")
                    
                    return cache_data['value']
                else:
                    # 删除过期文件
                    os.remove(cache_file)
                    if self.verbose:
                        logger.debug(f"删除过期缓存文件: {cache_file}")
            
            return None
            
        except Exception as e:
            logger.error(f"获取缓存失败: {e}")
            return None
    
    def set(
        self, 
        key: str, 
        value: Any,
        ttl_seconds: Optional[int] = None
    ) -> bool:
        """
        设置缓存值
        
        Parameters
        ----------
        key : str
            缓存键
        value : Any
            缓存值
        ttl_seconds : int, optional
            自定义生存时间
            
        Returns
        -------
        bool
            是否设置成功
        """
        try:
            # 计算时间戳
            current_time = time.time()
            ttl = ttl_seconds or self.ttl_seconds
            timestamp = current_time + ttl
            
            # 设置内存缓存
            self._memory_cache[key] = value
            self._cache_timestamps[key] = timestamp
            
            # 检查缓存大小限制
            if len(self._memory_cache) > self.max_size:
                self._evict_lru()
            
            # 保存到磁盘缓存
            cache_file = self._get_cache_file_path(key)
            cache_data = {
                'value': value,
                'timestamp': timestamp
            }
            
            with open(cache_file, 'wb') as f:
                pickle.dump(cache_data, f)
            
            if self.verbose:
                logger.debug(f"设置缓存键: {key}")
            
            return True
            
        except Exception as e:
            logger.error(f"设置缓存失败: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """
        删除缓存值
        
        Parameters
        ----------
        key : str
            缓存键
            
        Returns
        -------
        bool
            是否删除成功
        """
        try:
            # 从内存缓存删除
            if key in self._memory_cache:
                del self._memory_cache[key]
                del self._cache_timestamps[key]
            
            # 删除磁盘缓存文件
            cache_file = self._get_cache_file_path(key)
            if os.path.exists(cache_file):
                os.remove(cache_file)
                if self.verbose:
                    logger.debug(f"删除缓存文件: {cache_file}")
            
            return True
            
        except Exception as e:
            logger.error(f"删除缓存失败: {e}")
            return False
    
    def clear(self) -> bool:
        """
        清空所有缓存
        
        Returns
        -------
        bool
            是否清空成功
        """
        try:
            # 清空内存缓存
            self._memory_cache.clear()
            self._cache_timestamps.clear()
            
            # 清空磁盘缓存
            for filename in os.listdir(self.cache_dir):
                if filename.endswith('.cache'):
                    file_path = os.path.join(self.cache_dir, filename)
                    os.remove(file_path)
            
            if self.verbose:
                logger.info("缓存已清空")
            
            return True
            
        except Exception as e:
            logger.error(f"清空缓存失败: {e}")
            return False
    
    def get_cache_info(self) -> Dict[str, Any]:
        """
        获取缓存信息
        
        Returns
        -------
        Dict[str, Any]
            缓存信息
        """
        try:
            # 统计磁盘缓存文件
            disk_cache_count = 0
            disk_cache_size = 0
            
            for filename in os.listdir(self.cache_dir):
                if filename.endswith('.cache'):
                    file_path = os.path.join(self.cache_dir, filename)
                    disk_cache_count += 1
                    disk_cache_size += os.path.getsize(file_path)
            
            # 计算内存缓存大小（估算）
            memory_cache_size = len(str(self._memory_cache).encode())
            
            info = {
                'memory_cache_count': len(self._memory_cache),
                'memory_cache_size_bytes': memory_cache_size,
                'disk_cache_count': disk_cache_count,
                'disk_cache_size_bytes': disk_cache_size,
                'max_size': self.max_size,
                'ttl_seconds': self.ttl_seconds,
                'cache_dir': self.cache_dir
            }
            
            return info
            
        except Exception as e:
            logger.error(f"获取缓存信息失败: {e}")
            return {}
    
    def cleanup_expired(self) -> int:
        """
        清理过期缓存
        
        Returns
        -------
        int
            清理的缓存数量
        """
        try:
            cleaned_count = 0
            
            # 清理内存缓存
            expired_keys = []
            for key, timestamp in self._cache_timestamps.items():
                if not self._is_valid(timestamp):
                    expired_keys.append(key)
            
            for key in expired_keys:
                del self._memory_cache[key]
                del self._cache_timestamps[key]
                cleaned_count += 1
            
            # 清理磁盘缓存
            for filename in os.listdir(self.cache_dir):
                if filename.endswith('.cache'):
                    file_path = os.path.join(self.cache_dir, filename)
                    
                    try:
                        with open(file_path, 'rb') as f:
                            cache_data = pickle.load(f)
                        
                        if not self._is_valid(cache_data.get('timestamp', 0)):
                            os.remove(file_path)
                            cleaned_count += 1
                    except Exception:
                        # 文件损坏，直接删除
                        os.remove(file_path)
                        cleaned_count += 1
            
            if self.verbose:
                logger.info(f"清理过期缓存完成，清理数量: {cleaned_count}")
            
            return cleaned_count
            
        except Exception as e:
            logger.error(f"清理过期缓存失败: {e}")
            return 0
    
    def _get_cache_file_path(self, key: str) -> str:
        """
        获取缓存文件路径
        
        Parameters
        ----------
        key : str
            缓存键
            
        Returns
        -------
        str
            缓存文件路径
        """
        # 使用MD5哈希作为文件名
        key_hash = hashlib.md5(key.encode()).hexdigest()
        filename = f"{key_hash}.cache"
        return os.path.join(self.cache_dir, filename)
    
    def _is_valid(self, timestamp: float) -> bool:
        """
        检查缓存是否有效
        
        Parameters
        ----------
        timestamp : float
            缓存时间戳
            
        Returns
        -------
        bool
            是否有效
        """
        current_time = time.time()
        return timestamp > current_time
    
    def _evict_lru(self) -> None:
        """淘汰最近最少使用的缓存项"""
        try:
            # 按时间戳排序，找到最旧的项
            sorted_items = sorted(
                self._cache_timestamps.items(),
                key=lambda x: x[1]
            )
            
            # 删除最旧的项，直到缓存大小在限制内
            while len(self._memory_cache) > self.max_size and sorted_items:
                oldest_key, _ = sorted_items.pop(0)
                
                if oldest_key in self._memory_cache:
                    del self._memory_cache[oldest_key]
                    del self._cache_timestamps[oldest_key]
            
            if self.verbose and sorted_items:
                logger.debug(f"LRU淘汰完成，淘汰数量: {len(sorted_items) - len(self._memory_cache)}")
                
        except Exception as e:
            logger.error(f"LRU淘汰失败: {e}")
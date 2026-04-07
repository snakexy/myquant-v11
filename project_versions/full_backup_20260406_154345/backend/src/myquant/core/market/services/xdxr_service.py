# -*- coding: utf-8 -*-
"""
除权除息数据服务 (XdxrService)

[状态: 未使用 - 2026-04-04]
短期策略不需要复权，此服务已禁用。
需要恢复时，在 AdjustmentFactorService 中取消注释调用。

统一管理除权除息数据的获取和缓存，避免循环依赖。

调用链（符合架构规范）：
    SeamlessKlineService
        → AdjustmentFactorService.get_factor_table()
            → XdxrService.get_xdxr_data()
                → get_adapter('pytdx')  # 通过工厂获取适配器

不直接访问适配器内部属性，保持架构分层。
"""

import pickle
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

from loguru import logger

from myquant.core.market.adapters import get_adapter
from myquant.core.market.services.cache import TTLCache
from myquant.config.settings import XDXR_DIR


class XdxrService:
    """除权除息数据服务

    职责：
    - 统一管理除权除息数据的获取
    - 两级缓存：内存（L1）+ 文件（L2）
    - 通过 get_adapter() 获取适配器，不直接访问内部

    缓存策略：
    - 内存缓存：TTL 1小时（高频访问）
    - 文件缓存：TTL 7天（持久化）
    """

    def __init__(self):
        # L1 内存缓存
        self._memory_cache = TTLCache(maxsize=1000, ttl=3600)  # 1小时
        # L2 文件缓存 TTL
        self._file_ttl = 7 * 24 * 3600  # 7天
        # 缓存目录
        self._cache_dir = Path(XDXR_DIR) if XDXR_DIR else Path(__file__).parent / 'xdxr_cache'
        self._cache_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"[XdxrService] 初始化完成，缓存目录: {self._cache_dir}")

    def get_xdxr_data(self, symbol: str) -> List[Dict[str, Any]]:
        """获取除权除息数据（带两级缓存）

        优先级：内存缓存 → 文件缓存 → 在线获取

        Args:
            symbol: 股票代码 (如 600519.SH)

        Returns:
            除权除息记录列表，格式：
            [
                {
                    'date': '2024-06-28',
                    'category': '分红',
                    'fh': 0.0,      # 分红（每股）
                    'sg': 0.0,      # 送股（每股）
                    'pg': 0.0,      # 配股（每股）
                    'pgj': 0.0,     # 配股价
                },
                ...
            ]
        """
        # 1. 检查内存缓存
        cached = self._memory_cache.get(symbol)
        if cached is not None:
            logger.debug(f"[XdxrService] L1内存命中: {symbol}")
            return cached

        # 2. 检查文件缓存
        file_cached = self._load_from_file(symbol)
        if file_cached is not None:
            self._memory_cache.set(symbol, file_cached, ttl=3600)
            logger.debug(f"[XdxrService] L2文件命中: {symbol}")
            return file_cached

        # 3. 在线获取
        logger.info(f"[XdxrService] 缓存未命中，在线获取: {symbol}")
        xdxr_data = self._fetch_from_adapter(symbol)

        if xdxr_data:
            # 存入缓存
            self._memory_cache.set(symbol, xdxr_data, ttl=3600)
            self._save_to_file(symbol, xdxr_data)
            logger.info(f"[XdxrService] 获取成功: {symbol}, {len(xdxr_data)} 条")

        return xdxr_data

    def _fetch_from_adapter(self, symbol: str) -> List[Dict[str, Any]]:
        """从适配器获取除权数据

        通过 get_adapter() 工厂获取适配器，不直接访问内部属性。

        Args:
            symbol: 股票代码

        Returns:
            除权除息记录列表
        """
        xdxr_data = []

        # 尝试 PyTdx（24/7 可用）
        try:
            pytdx = get_adapter('pytdx')
            if pytdx and pytdx.is_available():
                raw_data = pytdx.get_xdxr_info(symbol)
                if raw_data:
                    xdxr_data = self._normalize_xdxr(raw_data, 'pytdx')
                    logger.debug(f"[XdxrService] PyTdx 获取 {symbol}: {len(xdxr_data)} 条")
                    return xdxr_data
        except Exception as e:
            logger.debug(f"[XdxrService] PyTdx 获取失败: {e}")

        # 备用：尝试 TdxQuant（仅交易时间）
        try:
            tdxquant = get_adapter('tdxquant')
            if tdxquant and tdxquant.is_available():
                raw_data = tdxquant.get_xdxr_info(symbol)
                if raw_data:
                    xdxr_data = self._normalize_xdxr(raw_data, 'tdxquant')
                    logger.debug(f"[XdxrService] TdxQuant 获取 {symbol}: {len(xdxr_data)} 条")
                    return xdxr_data
        except Exception as e:
            logger.debug(f"[XdxrService] TdxQuant 获取失败: {e}")

        logger.warning(f"[XdxrService] {symbol} 无除权数据")
        return []

    def _normalize_xdxr(self, raw_data: Any, source: str) -> List[Dict[str, Any]]:
        """标准化除权数据格式

        将不同适配器返回的格式统一为标准格式。

        Args:
            raw_data: 原始数据
            source: 数据来源

        Returns:
            标准化的除权记录列表
        """
        if not raw_data:
            return []

        result = []

        try:
            if source == 'pytdx':
                # PyTdx 返回格式：[{'year': 2024, 'month': 6, 'day': 28, ...}]
                for item in raw_data:
                    if isinstance(item, dict):
                        year = item.get('year', 0)
                        month = item.get('month', 0)
                        day = item.get('day', 0)
                        if year and month and day:
                            result.append({
                                'date': f'{year:04d}-{month:02d}-{day:02d}',
                                'category': self._get_category(item),
                                'fh': float(item.get('fh', 0) or 0),    # 分红
                                'sg': float(item.get('sg', 0) or 0),    # 送股
                                'pg': float(item.get('pg', 0) or 0),    # 配股
                                'pgj': float(item.get('pgj', 0) or 0),  # 配股价
                            })

            elif source == 'tdxquant':
                # TdxQuant 返回格式可能不同，需要适配
                for item in raw_data:
                    if isinstance(item, dict):
                        date_str = item.get('date') or item.get('datetime', '')
                        if date_str:
                            if len(date_str) == 8:  # YYYYMMDD
                                date_str = f'{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}'
                            result.append({
                                'date': date_str,
                                'category': self._get_category(item),
                                'fh': float(item.get('fh', 0) or item.get('bonus', 0) or 0),
                                'sg': float(item.get('sg', 0) or item.get('transfer', 0) or 0),
                                'pg': float(item.get('pg', 0) or item.get('allot', 0) or 0),
                                'pgj': float(item.get('pgj', 0) or item.get('allotprice', 0) or 0),
                            })

        except Exception as e:
            logger.warning(f"[XdxrService] 标准化失败: {e}")
            return []

        # 按日期排序
        result.sort(key=lambda x: x['date'])
        return result

    def _get_category(self, item: dict) -> str:
        """获取除权类别"""
        category = item.get('category', '')
        if category:
            return category

        # 根据字段推断
        if item.get('fh'):
            return '分红'
        elif item.get('sg') or item.get('pg'):
            return '送配股'
        else:
            return '其他'

    def _load_from_file(self, symbol: str) -> Optional[List[Dict]]:
        """从文件缓存加载"""
        filepath = self._get_cache_path(symbol)
        if not filepath.exists():
            return None

        try:
            # 检查文件是否过期
            file_mtime = filepath.stat().st_mtime
            if time.time() - file_mtime > self._file_ttl:
                logger.debug(f"[XdxrService] 文件缓存过期: {symbol}")
                return None

            with open(filepath, 'rb') as f:
                data = pickle.load(f)
                return data
        except Exception as e:
            logger.warning(f"[XdxrService] 加载文件缓存失败: {e}")
            return None

    def _save_to_file(self, symbol: str, data: List[Dict]):
        """保存到文件缓存"""
        filepath = self._get_cache_path(symbol)
        try:
            with open(filepath, 'wb') as f:
                pickle.dump(data, f)
            logger.debug(f"[XdxrService] 保存文件缓存: {symbol}")
        except Exception as e:
            logger.warning(f"[XdxrService] 保存文件缓存失败: {e}")

    def _get_cache_path(self, symbol: str) -> Path:
        """获取缓存文件路径"""
        # 使用子目录组织：sh/600519.pkl
        exchange = 'sh' if symbol.endswith('.SH') else 'sz' if symbol.endswith('.SZ') else 'bj'
        code = symbol.replace('.SH', '').replace('.SZ', '').replace('.BJ', '')
        subdir = self._cache_dir / exchange
        subdir.mkdir(parents=True, exist_ok=True)
        return subdir / f'{code}.pkl'

    def invalidate_cache(self, symbol: str):
        """清除指定股票的缓存"""
        self._memory_cache.delete(symbol)
        filepath = self._get_cache_path(symbol)
        if filepath.exists():
            filepath.unlink()
        logger.info(f"[XdxrService] 已清除缓存: {symbol}")

    def get_cache_stats(self) -> Dict:
        """获取缓存统计"""
        return {
            'memory_cache_size': len(self._memory_cache._cache),
            'cache_dir': str(self._cache_dir),
            'file_ttl_hours': self._file_ttl / 3600,
        }


# 单例实例
_xdxr_service_instance: Optional[XdxrService] = None


def get_xdxr_service() -> XdxrService:
    """获取 XdxrService 单例"""
    global _xdxr_service_instance
    if _xdxr_service_instance is None:
        _xdxr_service_instance = XdxrService()
    return _xdxr_service_instance

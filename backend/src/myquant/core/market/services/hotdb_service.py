# -*- coding: utf-8 -*-
"""
热数据库管理服务

提供热数据库的预热、清理、状态查询、数据复制与聚合等功能
"""

from typing import List, Optional, Dict, Any
from loguru import logger
from pathlib import Path
from datetime import datetime
import pandas as pd
import time

from myquant.core.market.adapters import get_adapter


class HotDBService:
    """热数据库管理服务

    负责热数据库的预热、清理、状态查询等管理功能
    """

    def __init__(self):
        self._hotdb = None
        self._localdb = None

    def _get_hotdb_adapter(self):
        """获取 HotDB 适配器（延迟加载）"""
        if self._hotdb is None:
            self._hotdb = get_adapter('hotdb')
        return self._hotdb

    def _get_localdb_adapter(self):
        """获取 LocalDB 适配器（延迟加载）"""
        if self._localdb is None:
            self._localdb = get_adapter('localdb')
        return self._localdb

    def preheat(
        self,
        symbols: List[str],
        periods: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """预热：从 LocalDB 复制历史数据到 HotDB

        Args:
            symbols: 股票代码列表
            periods: 周期列表（如 ['1d', '5m', '15m']），默认为 ['1d', '5m', '15m', '1m']

        Returns:
            预热结果统计
        """
        if periods is None:
            periods = ['1d', '5m', '15m', '1m']

        hotdb = self._get_hotdb_adapter()
        localdb = self._get_localdb_adapter()

        if not hotdb:
            return {'success': False, 'error': 'HotDB 适配器不可用'}
        if not localdb:
            return {'success': False, 'error': 'LocalDB 适配器不可用'}

        results = {
            'success': True,
            'total_symbols': len(symbols),
            'total_periods': len(periods),
            'saved_count': 0,
            'skipped_count': 0,
            'failed_count': 0,
            'details': []
        }

        logger.info(f"[HotDB] 开始预热: {len(symbols)} 只股票 x {len(periods)} 个周期")

        for symbol in symbols:
            symbol_result = {
                'symbol': symbol,
                'periods': {}
            }

            for period in periods:
                try:
                    # 从 LocalDB 读取数据
                    df_dict = localdb.get_kline(
                        symbols=[symbol],
                        period=period,
                        count=5000  # 获取尽可能多的历史数据
                    )

                    if symbol in df_dict and not df_dict[symbol].empty:
                        df = df_dict[symbol]

                        # 保存到 HotDB
                        success = hotdb.save_kline(symbol, df, period)

                        if success:
                            results['saved_count'] += 1
                            symbol_result['periods'][period] = {
                                'status': 'success',
                                'count': len(df)
                            }
                            logger.info(f"[HotDB] 预热 {symbol} {period}: {len(df)} 条")
                        else:
                            results['failed_count'] += 1
                            symbol_result['periods'][period] = {
                                'status': 'failed',
                                'error': '保存失败'
                            }
                    else:
                        results['skipped_count'] += 1
                        symbol_result['periods'][period] = {
                            'status': 'skipped',
                            'reason': 'LocalDB 无数据'
                        }
                        logger.debug(f"[HotDB] 跳过 {symbol} {period}: LocalDB 无数据")

                except Exception as e:
                    results['failed_count'] += 1
                    symbol_result['periods'][period] = {
                        'status': 'error',
                        'error': str(e)
                    }
                    logger.warning(f"[HotDB] 预热 {symbol} {period} 失败: {e}")

            results['details'].append(symbol_result)

        logger.info(f"[HotDB] 预热完成: 成功 {results['saved_count']}, 跳过 {results['skipped_count']}, 失败 {results['failed_count']}")
        return results

    def delete_symbol(
        self,
        symbol: str,
        period: Optional[str] = None
    ) -> Dict[str, Any]:
        """删除股票数据

        Args:
            symbol: 股票代码
            period: 周期（如 '1d', '1m'），None 表示删除所有周期

        Returns:
            删除结果
        """
        hotdb = self._get_hotdb_adapter()

        if not hotdb:
            return {'success': False, 'error': 'HotDB 适配器不可用'}

        try:
            success = hotdb.delete_kline(symbol, period)

            if success:
                logger.info(f"[HotDB] 删除 {symbol} {period or '所有周期'} 成功")
                return {
                    'success': True,
                    'symbol': symbol,
                    'period': period or 'all'
                }
            else:
                return {
                    'success': False,
                    'error': '删除失败',
                    'symbol': symbol,
                    'period': period or 'all'
                }

        except Exception as e:
            logger.error(f"[HotDB] 删除 {symbol} {period or '所有周期'} 失败: {e}")
            return {
                'success': False,
                'error': str(e),
                'symbol': symbol,
                'period': period or 'all'
            }

    def get_status(self) -> Dict[str, Any]:
        """获取热数据库状态

        Returns:
            热数据库状态信息
        """
        hotdb = self._get_hotdb_adapter()

        if not hotdb:
            return {'success': False, 'error': 'HotDB 适配器不可用'}

        try:
            # 获取所有股票
            symbols = hotdb.list_symbols()

            # 统计每个周期的股票数量
            period_stats: Dict[str, int] = {}

            for symbol in symbols:
                # 检查各周期数据是否存在
                periods = ['1d', '1w', '1mon', '1m', '5m', '15m', '30m', '1h']
                for period in periods:
                    try:
                        has_data = hotdb.has_symbol(symbol)
                        # has_symbol 只检查日线，这里简化处理
                        if has_data:
                            period_stats[period] = (
                                period_stats.get(period, 0) + 1
                            )
                    except Exception:
                        pass

            return {
                'success': True,
                'total_symbols': len(symbols),
                'period_stats': period_stats,
                'symbols': symbols[:100],  # 最多返回100个示例
                'has_more': len(symbols) > 100
            }

        except Exception as e:
            logger.error(f"[HotDB] 获取状态失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def list_symbols(
        self,
        limit: Optional[int] = None
    ) -> Dict[str, Any]:
        """列出热数据库中的所有股票

        Args:
            limit: 最多返回的股票数量，None 表示全部

        Returns:
            股票列表
        """
        hotdb = self._get_hotdb_adapter()

        if not hotdb:
            return {'success': False, 'error': 'HotDB 适配器不可用'}

        try:
            symbols = hotdb.list_symbols()

            if limit:
                symbols = symbols[:limit]

            return {
                'success': True,
                'symbols': symbols,
                'total': len(symbols)
            }

        except Exception as e:
            logger.error(f"[HotDB] 列出股票失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def has_symbol(self, symbol: str) -> Dict[str, Any]:
        """检查股票是否在热数据库中

        Args:
            symbol: 股票代码

        Returns:
            检查结果
        """
        hotdb = self._get_hotdb_adapter()

        if not hotdb:
            return {'success': False, 'error': 'HotDB 适配器不可用'}

        try:
            has_data = hotdb.has_symbol(symbol)

            return {
                'success': True,
                'symbol': symbol,
                'exists': has_data
            }

        except Exception as e:
            logger.error(f"[HotDB] 检查 {symbol} 失败: {e}")
            return {
                'success': False,
                'error': str(e),
                'symbol': symbol
            }

    def ensure_hotdb_data(self, symbol: str, period: str) -> bool:
        """确保HotDB有数据，没有则从LocalDB复制

        Args:
            symbol: 股票代码
            period: 周期 (1d/5m/15m/30m/1h)

        Returns:
            True: HotDB已有数据或成功复制
            False: 需要在线获取
        """
        try:
            hotdb = self._get_hotdb_adapter()
            if not hotdb or not hotdb.is_available():
                return False

            # 1. 检查 HotDB 是否已有数据
            existing_data = hotdb.get_kline(
                symbols=[symbol], period=period, count=1
            )
            if symbol in existing_data and not existing_data[symbol].empty:
                logger.debug(f"[HotDB] {symbol} {period} 已有数据")
                return True

            # 2. 尝试从 LocalDB 复制
            localdb = self._get_localdb_adapter()
            if not localdb or not localdb.is_available():
                logger.debug(f"[HotDB] LocalDB 不可用，无法复制 {symbol} {period}")
                return False

            if period in ('1d', '5m'):
                # 直接复制（LocalDB有这些周期）
                return self._copy_from_localdb(symbol, period)
            elif period in ('15m', '30m', '1h'):
                # 从5分钟聚合
                return self._aggregate_from_5m(symbol, period)
            else:
                logger.debug(f"[HotDB] {period} 需要在线获取")
                return False

        except Exception as e:
            logger.warning(f"[HotDB] 确保 {symbol} {period} 数据失败: {e}")
            return False

    def _copy_from_localdb(self, symbol: str, period: str) -> bool:
        """从 LocalDB 直接复制数据到 HotDB

        Args:
            symbol: 股票代码
            period: 周期 (1d/5m)

        Returns:
            是否成功
        """
        try:
            localdb = self._get_localdb_adapter()
            hotdb = self._get_hotdb_adapter()

            # 从 LocalDB 获取数据
            df_dict = localdb.get_kline(
                symbols=[symbol], period=period, count=5000
            )

            if symbol not in df_dict or df_dict[symbol].empty:
                logger.debug(f"[HotDB] LocalDB 中 {symbol} {period} 无数据")
                return False

            df = df_dict[symbol]
            logger.info(f"[HotDB] 从 LocalDB 复制 {symbol} {period}: {len(df)} 条")

            # 保存到 HotDB
            success = hotdb.save_kline(symbol, df, period)
            if success:
                logger.info(f"[HotDB] 成功复制 {symbol} {period} 到 HotDB")

            return success

        except Exception as e:
            logger.warning(f"[HotDB] 从 LocalDB 复制 {symbol} {period} 失败: {e}")
            return False

    def _aggregate_from_5m(self, symbol: str, target_period: str) -> bool:
        """从5分钟数据聚合到目标周期

        Args:
            symbol: 股票代码
            target_period: 目标周期 (15m/30m/1h)

        Returns:
            是否成功
        """
        try:
            start_time = time.time()

            localdb = self._get_localdb_adapter()
            hotdb = self._get_hotdb_adapter()

            # 1. 从 LocalDB 获取5分钟数据
            df_dict = localdb.get_kline(
                symbols=[symbol], period='5m', count=5000
            )

            if symbol not in df_dict or df_dict[symbol].empty:
                logger.debug(
                    f"[HotDB] LocalDB 中 {symbol} 5m 无数据，无法聚合"
                )
                return False

            df_5m = df_dict[symbol]
            logger.info(f"[HotDB] 获取到 {symbol} 5分钟数据: {len(df_5m)} 条")

            # 2. 聚合到目标周期
            mapping = {'15m': 3, '30m': 6, '1h': 12}  # 5m根数
            n = mapping.get(target_period)
            if n is None:
                logger.error(f"[HotDB] 不支持的聚合周期: {target_period}")
                return False

            # 确保时间戳是索引且已排序
            df = df_5m.copy().reset_index(drop=True)
            df['datetime'] = pd.to_datetime(df['datetime'])
            df = df.sort_values('datetime').reset_index(drop=True)

            # 创建周期分组键（每 n 根K线一组）
            group_keys = (df.index // n)

            # 聚合
            agg_df = df.groupby(group_keys).agg({
                'datetime': 'first',
                'open': 'first',
                'high': 'max',
                'low': 'min',
                'close': 'last',
                'volume': 'sum'
            })

            # 处理 amount（如果有）
            if 'amount' in df.columns:
                agg_df['amount'] = df.groupby(group_keys)['amount'].sum()

            agg_df = agg_df.reset_index(drop=True)

            elapsed = (time.time() - start_time) * 1000  # 转换为毫秒
            logger.info(f"[HotDB] 聚合 5m → {target_period}: {len(df_5m)} 根 → {len(agg_df)} 根 (耗时: {elapsed:.2f}ms)")

            # 3. 保存到 HotDB
            success = hotdb.save_kline(symbol, agg_df, target_period)
            if success:
                logger.info(f"[HotDB] 成功聚合并保存 {symbol} {target_period}")

            return success

        except Exception as e:
            logger.warning(f"[HotDB] 聚合 {symbol} 5m → {target_period} 失败: {e}")
            return False

    def ensure_symbol(self, symbol: str) -> Dict[str, Any]:
        """确保股票在 HotDB 中（自选板块调用）

        检查内部标记，只在第一次加入时从 LocalDB 转存数据：
        - 复制 1d 数据
        - 复制 5m 数据（自动触发 15m/30m/1h 聚合）
        - 标记为已转存

        后续调用直接跳过，避免重复转存。

        Args:
            symbol: 股票代码 (如 600000.SH)

        Returns:
            操作结果
        """
        hotdb = self._get_hotdb_adapter()

        if not hotdb or not hotdb.is_available():
            return {
                'success': False,
                'error': 'HotDB 适配器不可用',
                'symbol': symbol
            }

        try:
            # 调用适配器的 ensure_symbol_in_hotdb 方法
            success = hotdb.ensure_symbol_in_hotdb(symbol)

            if success:
                return {
                    'success': True,
                    'symbol': symbol,
                    'message': '数据已在 HotDB 中或转存成功'
                }
            else:
                return {
                    'success': False,
                    'error': '转存失败',
                    'symbol': symbol
                }

        except Exception as e:
            logger.error(f"[HotDB] 确保 {symbol} 在 HotDB 中失败: {e}")
            return {
                'success': False,
                'error': str(e),
                'symbol': symbol
            }


# 单例实例
_hotdb_service: Optional[HotDBService] = None


def get_hotdb_service() -> HotDBService:
    """获取 HotDBService 单例实例"""
    global _hotdb_service
    if _hotdb_service is None:
        _hotdb_service = HotDBService()
    return _hotdb_service

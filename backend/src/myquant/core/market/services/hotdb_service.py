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
from myquant.core.market.routing import get_source_selector, DataLevel


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
            print(f"[DEBUG] 正在获取 hotdb 适配器...")
            from myquant.core.market.adapters import AdapterFactory
            print(f"[DEBUG] 已注册适配器: {AdapterFactory.list_adapters()}")
            self._hotdb = get_adapter('hotdb')
            print(f"[DEBUG] get_adapter('hotdb') 返回: {self._hotdb}")
            print(f"[DEBUG] 返回类型: {type(self._hotdb)}")
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
            periods: 周期列表，默认为 ['1d', '5m']

        Returns:
            预热结果统计

        注意：
            - HotDB 存储策略：从 LocalDB 获取 1d 和 5m 原始数据
            - 5m 数据会自动聚合生成 15m/30m/1h
            - 1m 数据单独处理（在线获取，只保留 7 天窗口期）
        """
        if periods is None:
            periods = ['1d', '5m']  # 预热日线和5分钟数据

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
                                'count': len(df),
                                'source': 'localdb'
                            }
                            logger.info(f"[HotDB] 预热 {symbol} {period}: {len(df)} 条 (LocalDB)")
                        else:
                            results['failed_count'] += 1
                            symbol_result['periods'][period] = {
                                'status': 'failed',
                                'error': '保存失败'
                            }
                    else:
                        # LocalDB 无数据，尝试从在线源获取（使用路由）
                        logger.debug(f"[HotDB] LocalDB 无 {symbol} {period} 数据，尝试在线获取")

                        # 获取在线数据源的 fallback chain
                        selector = get_source_selector()
                        if selector:
                            chain = selector.get_fallback_chain_for_code(DataLevel.L3, symbol)
                            online_sources = [s for s in chain if s not in ('hotdb', 'localdb')]

                            for source_name in online_sources:
                                try:
                                    online_adapter = get_adapter(source_name)
                                    if online_adapter and online_adapter.is_available():
                                        df_dict_online = online_adapter.get_kline(
                                            symbols=[symbol],
                                            period=period,
                                            count=10000
                                        )

                                        if symbol in df_dict_online and not df_dict_online[symbol].empty:
                                            df = df_dict_online[symbol]
                                            success = hotdb.save_kline(symbol, df, period)

                                            if success:
                                                results['saved_count'] += 1
                                                symbol_result['periods'][period] = {
                                                    'status': 'success',
                                                    'count': len(df),
                                                    'source': source_name
                                                }
                                                logger.info(f"[HotDB] 预热 {symbol} {period}: {len(df)} 条 (在线: {source_name})")
                                                break  # 成功获取，跳出循环
                                except Exception as e:
                                    logger.debug(f"[HotDB] {source_name} 获取失败: {e}")
                                    continue

                            # 如果所有在线源都失败，记录跳过
                            if period not in symbol_result['periods'] or symbol_result['periods'][period].get('status') != 'success':
                                results['skipped_count'] += 1
                                symbol_result['periods'][period] = {
                                    'status': 'skipped',
                                    'reason': '所有在线源均无数据'
                                }
                        else:
                            results['skipped_count'] += 1
                            symbol_result['periods'][period] = {
                                'status': 'skipped',
                                'reason': '路由选择器不可用'
                            }

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

    def _complete_from_online(
        self, symbol: str, period: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Optional[pd.DataFrame]:
        """从在线源获取数据并保存到 HotDB（智能增量模式）

        精确请求缺失部分，自动追加保存

        Args:
            symbol: 股票代码
            period: 周期
            start_date: 开始日期（增量更新时指定）
            end_date: 结束日期（增量更新时指定）

        Returns:
            获取的数据，失败返回 None
        """
        try:
            selector = get_source_selector()
            if not selector:
                logger.warning(f"[HotDB] 路由选择器不可用，无法在线补全")
                return None

            # 获取在线数据源的 fallback chain
            chain = selector.get_fallback_chain_for_code(DataLevel.L3, symbol)

            # 遍历在线源（跳过 hotdb 和 localdb）
            online_sources = [s for s in chain if s not in ('hotdb', 'localdb')]

            for source_name in online_sources:
                try:
                    adapter = get_adapter(source_name)
                    if adapter and adapter.is_available():
                        logger.info(f"[HotDB] 通过 {source_name} 获取 {symbol} {period}")

                        # 构建请求参数（智能增量模式：精确请求缺失部分）
                        get_kline_kwargs = {
                            'symbols': [symbol],
                            'period': period,
                        }

                        # 如果指定了日期范围，只使用日期范围（不传 count）
                        if start_date:
                            get_kline_kwargs['start_date'] = start_date
                        if end_date:
                            get_kline_kwargs['end_date'] = end_date

                        # 如果没有日期范围，才使用 count（兜底）
                        if not start_date and not end_date:
                            get_kline_kwargs['count'] = 10000

                        df_dict = adapter.get_kline(**get_kline_kwargs)

                        if symbol in df_dict and df_dict[symbol] is not None and not df_dict[symbol].empty:
                            df = df_dict[symbol]
                            logger.info(f"[HotDB] 在线获取 {symbol} {period}: {len(df)} 条 (来源: {source_name})")

                            # 保存到 HotDB（追加模式）
                            hotdb = self._get_hotdb_adapter()
                            if hotdb:
                                hotdb.save_kline(symbol, df, period)

                            return df
                except Exception as e:
                    logger.debug(f"[HotDB] {source_name} 获取失败: {e}")
                    continue

            logger.warning(f"[HotDB] 所有在线源均无 {symbol} {period} 数据")
            return None

        except Exception as e:
            logger.warning(f"[HotDB] 在线补全 {symbol} {period} 失败: {e}")
            return None

    def smart_update(self, symbol: str, period: str) -> Dict[str, Any]:
        """智能增量更新（核心入口）

        完整流程：
        1. HotDB 有数据 → detect_gap → 有缺口则补全 → 无缺口直接返回
        2. HotDB 无数据 → ensure_hotdb_data → 再检查缺口

        Args:
            symbol: 股票代码
            period: 周期

        Returns:
            dict: {success, has_data, has_gap, df, ...}
        """
        try:
            hotdb = self._get_hotdb_adapter()
            if not hotdb or not hotdb.is_available():
                return {'success': False, 'error': 'HotDB 不可用', 'has_data': False}

            # 1. 检查 HotDB 是否有数据
            info = hotdb.get_data_info(symbol, period)

            if not info or not info.get('has_data'):
                # HotDB 无数据，尝试从 LocalDB 复制
                logger.info(f"[HotDB] {symbol} {period} 无数据，尝试从 LocalDB 复制")
                copied = self.ensure_hotdb_data(symbol, period)

                if copied:
                    # 复制成功，再次检查缺口
                    info = hotdb.get_data_info(symbol, period)
                else:
                    # LocalDB 也无数据，返回需要在线获取
                    return {
                        'success': True,
                        'has_data': False,
                        'has_gap': True,
                        'reason': 'no_data_in_hotdb_or_localdb',
                        'symbol': symbol,
                        'period': period
                    }

            # 2. 检测缺口
            gap_info = hotdb.detect_gap(symbol, period)

            if not gap_info:
                return {'success': False, 'error': '缺口检测失败', 'has_data': info.get('has_data', False)}

            if not gap_info['has_gap']:
                # 无缺口，返回现有数据
                df_dict = hotdb.get_kline(
                    symbols=[symbol],
                    period=period,
                    count=10000,
                    allow_stale=True
                )

                df = df_dict.get(symbol)
                return {
                    'success': True,
                    'has_data': True,
                    'has_gap': False,
                    'reason': gap_info.get('reason'),
                    'df': df,
                    'latest': gap_info.get('latest'),
                    'symbol': symbol,
                    'period': period,
                    'should_update_localdb': False  # 无缺口，不需要更新
                }

            # 3. 有缺口，在线获取缺失部分
            logger.info(
                f"[HotDB] {symbol} {period} 有缺口: {gap_info.get('reason')}, "
                f"最新 {gap_info.get('latest')}"
            )

            # 计算缺失的日期范围
            missing_start = gap_info.get('missing_start')
            missing_end = gap_info.get('missing_end')

            start_date_str = missing_start.strftime('%Y%m%d') if missing_start else None
            end_date_str = missing_end.strftime('%Y%m%d') if missing_end else None

            # 在线获取缺失部分
            df_new = self._complete_from_online(
                symbol, period,
                start_date=start_date_str,
                end_date=end_date_str
            )

            if df_new is None or df_new.empty:
                # 在线获取失败，返回现有数据
                df_dict = hotdb.get_kline(
                    symbols=[symbol],
                    period=period,
                    count=10000,
                    allow_stale=True
                )
                df = df_dict.get(symbol)

                return {
                    'success': True,
                    'has_data': True,
                    'has_gap': True,  # 仍然有缺口（在线获取失败）
                    'reason': 'online_fetch_failed',
                    'df': df,
                    'latest': gap_info.get('latest'),
                    'symbol': symbol,
                    'period': period,
                    'should_update_localdb': gap_info.get('is_large_gap', False)  # 大缺口时提醒
                }

            # 4. 返回完整数据（从 HotDB 读取，已自动追加）
            df_dict = hotdb.get_kline(
                symbols=[symbol],
                period=period,
                count=10000,
                allow_stale=True
            )
            df = df_dict.get(symbol)

            return {
                'success': True,
                'has_data': True,
                'has_gap': False,  # 已补全
                'reason': 'incremental_update_success',
                'df': df,
                'latest': df['datetime'].iloc[-1] if df is not None and not df.empty else None,
                'symbol': symbol,
                'period': period,
                'added_count': len(df_new),
                'should_update_localdb': gap_info.get('is_large_gap', False)  # 大缺口时提醒
            }

        except Exception as e:
            logger.warning(f"[HotDB] {symbol} {period} 智能增量更新失败: {e}")
            return {'success': False, 'error': str(e), 'has_data': False}

    def get_kline_with_auto_update(
        self,
        symbol: str,
        period: str,
        count: Optional[int] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Optional[pd.DataFrame]:
        """获取 K 线数据（带自动增量更新）

        供 SeamlessKlineService 调用的统一接口。

        Args:
            symbol: 股票代码
            period: 周期
            count: 返回数量
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            DataFrame 或 None
        """
        try:
            result = self.smart_update(symbol, period)

            if not result.get('success'):
                return None

            df = result.get('df')
            if df is None or df.empty:
                return None

            # 应用过滤条件
            if start_date:
                df = df[df['datetime'] >= pd.Timestamp(start_date)]
            if end_date:
                df = df[df['datetime'] <= pd.Timestamp(end_date)]
            if count and len(df) > count:
                df = df.tail(count)

            return df

        except Exception as e:
            logger.warning(f"[HotDB] 获取 {symbol} {period} K线失败: {e}")
            return None

    def _is_symbol_ready(self, symbol: str) -> bool:
        """检查股票是否已转存到 HotDB

        Args:
            symbol: 股票代码

        Returns:
            True: 已转存，False: 未转存
        """
        hotdb = self._get_hotdb_adapter()
        if not hotdb:
            return False
        # 代理调用适配器的内部方法
        key = f"{symbol}_ready"
        metadata = hotdb._metadata.get(key, {})
        return metadata.get('ready', False)

    def _mark_symbol_ready(self, symbol: str):
        """标记股票已转存到 HotDB

        Args:
            symbol: 股票代码
        """
        hotdb = self._get_hotdb_adapter()
        if not hotdb:
            return
        # 代理调用适配器的内部方法
        try:
            key = f"{symbol}_ready"
            hotdb._metadata[key] = {
                'symbol': symbol,
                'ready': True,
                'timestamp': datetime.now().isoformat()
            }
            hotdb._save_metadata()
            logger.debug(f"[HotDB] 标记已转存: {symbol}")
        except Exception as e:
            logger.warning(f"[HotDB] 标记 {symbol} 失败: {e}")

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
        localdb = self._get_localdb_adapter()

        if not hotdb or not hotdb.is_available():
            return {
                'success': False,
                'error': 'HotDB 适配器不可用',
                'symbol': symbol
            }

        try:
            # 1. 检查是否已转存
            if self._is_symbol_ready(symbol):
                logger.debug(f"[HotDB] {symbol} 已转存，跳过")
                return {
                    'success': True,
                    'symbol': symbol,
                    'message': '数据已在 HotDB 中'
                }

            # 2. 检查 LocalDB 是否可用
            if not localdb or not localdb.is_available():
                logger.warning(f"[HotDB] LocalDB 不可用，无法转存 {symbol}")
                return {
                    'success': False,
                    'error': 'LocalDB 不可用',
                    'symbol': symbol
                }

            logger.info(f"[HotDB] 开始转存 {symbol} 从 LocalDB")

            # 3. 从 LocalDB 复制 1d 数据
            try:
                result = localdb.get_kline(symbols=[symbol], period='1d', count=5000)
                if symbol in result and not result[symbol].empty:
                    hotdb.save_kline(symbol, result[symbol], '1d')
                    logger.info(f"[HotDB] 转存 {symbol} 1d: {len(result[symbol])} 条")
                else:
                    logger.warning(f"[HotDB] LocalDB 中 {symbol} 无 1d 数据")
            except Exception as e:
                logger.warning(f"[HotDB] 转存 {symbol} 1d 失败: {e}")

            # 4. 从 LocalDB 复制 5m 数据（会自动触发聚合）
            try:
                result = localdb.get_kline(symbols=[symbol], period='5m', count=5000)
                if symbol in result and not result[symbol].empty:
                    hotdb.save_kline(symbol, result[symbol], '5m')
                    logger.info(f"[HotDB] 转存 {symbol} 5m: {len(result[symbol])} 条")
                else:
                    logger.warning(f"[HotDB] LocalDB 中 {symbol} 无 5m 数据")
            except Exception as e:
                logger.warning(f"[HotDB] 转存 {symbol} 5m 失败: {e}")

            # 5. 标记为已转存
            self._mark_symbol_ready(symbol)

            logger.info(f"[HotDB] {symbol} 转存完成")
            return {
                'success': True,
                'symbol': symbol,
                'message': '转存成功'
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

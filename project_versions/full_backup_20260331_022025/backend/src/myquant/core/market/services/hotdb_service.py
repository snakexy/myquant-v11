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
                    # 从 LocalDB 读取数据（获取所有可用数据）
                    df_dict = localdb.get_kline(
                        symbols=[symbol],
                        period=period,
                        count=100000  # 获取尽可能多的历史数据
                    )

                    if symbol in df_dict and not df_dict[symbol].empty:
                        df = df_dict[symbol].copy()

                        # === 修复：单位统一转换 ===
                        # LocalDB 存储的是原始股数（所有周期都是股）
                        # 但 TdxQuant/PyTdx 返回的是手（÷100）
                        # 为了保持一致性，所有周期都需要转换为手
                        if 'volume' in df.columns:
                            df['volume'] = df['volume'] / 100
                            logger.debug(f"[HotDB] {symbol} {period} 成交量单位转换: 股 → 手")

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
        """确保 HotDB 有数据，没有则从 LocalDB 复制

        Args:
            symbol: 股票代码
            period: 周期 (1d/5m/15m/30m/1h)

        Returns:
            True: HotDB 已有数据或成功复制
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
                # 直接复制（LocalDB 有这些周期）
                return self._copy_from_localdb(symbol, period)
            elif period in ('15m', '30m', '1h'):
                # 从 5 分钟聚合
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

            # 从 LocalDB 获取数据（获取尽可能多的历史数据）
            df_dict = localdb.get_kline(
                symbols=[symbol], period=period, count=100000
            )

            if symbol not in df_dict or df_dict[symbol].empty:
                logger.debug(f"[HotDB] LocalDB 中 {symbol} {period} 无数据")
                return False

            df = df_dict[symbol]
            logger.info(f"[HotDB] 从 LocalDB 复制 {symbol} {period}: {len(df)} 条")

            # === 修复：单位统一转换 ===
            # LocalDB 存储的是原始股数（所有周期都是股），需要转换为手（÷100）
            if 'volume' in df.columns:
                df['volume'] = df['volume'] / 100
                logger.debug(f"[HotDB] {symbol} {period} 成交量单位转换: 股 → 手")

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
        end_date: Optional[str] = None,
        count: Optional[int] = None
    ) -> Optional[pd.DataFrame]:
        """从在线源获取数据并保存到 HotDB（智能增量模式）

        精确请求缺失部分，自动追加保存

        Args:
            symbol: 股票代码
            period: 周期
            start_date: 开始日期（增量更新时指定）
            end_date: 结束日期（增量更新时指定）
            count: 数量（1m 数据等使用 count 方式）

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

                        # 优先级：显式 count > 日期范围 > 默认 count
                        if count is not None:
                            get_kline_kwargs['count'] = count
                            logger.info(f"[HotDB] 使用 count 方式获取 {count} 条")
                        elif start_date:
                            get_kline_kwargs['start_date'] = start_date
                            if end_date:
                                get_kline_kwargs['end_date'] = end_date
                        else:
                            # 兜底：使用默认数量
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

    def _detect_gap(self, symbol: str, period: str) -> Optional[Dict]:
        """检测数据缺口（Service 层业务逻辑）

        判断 HotDB 数据是否需要增量更新：
        - 日线：最新日期与今天相差 > 1 天，且当前已过 09:30
        - 分钟线：检测内部缺口（排除周末、节假日、正常隔夜）

        Args:
            symbol: 股票代码
            period: 周期

        Returns:
            dict: {has_gap, latest, missing_start, missing_end, reason} 或 None
        """
        try:
            hotdb = self._get_hotdb_adapter()
            if not hotdb or not hotdb.is_available():
                return {'has_gap': True, 'reason': 'hotdb_unavailable', 'latest': None}

            # 获取数据基本信息
            info = hotdb.get_data_info(symbol, period)
            if not info or not info['has_data']:
                return {'has_gap': True, 'reason': 'no_data', 'latest': None}

            latest = info['latest']
            now = pd.Timestamp.now(tz=None).replace(tzinfo=None)

            if period == '1d':
                # === 日线缺口检测 ===
                from datetime import timedelta
                from ..utils.trading_time_detector import TradingTimeDetectorV2

                today = now.date()
                latest_date = latest.date()
                natural_days_diff = (today - latest_date).days

                if natural_days_diff <= 0:
                    return {'has_gap': False, 'reason': 'up_to_date', 'latest': latest}

                # 计算缺失的交易日
                missing_trading_days = []
                current_date = latest_date + timedelta(days=1)
                detector = TradingTimeDetectorV2()

                while current_date <= today:
                    try:
                        current_dt = datetime.combine(current_date, datetime.min.time())
                        if detector.is_trading_day(current_dt):
                            missing_trading_days.append(current_date)
                    except Exception:
                        weekday = current_date.weekday()
                        if weekday < 5:
                            missing_trading_days.append(current_date)
                    current_date += timedelta(days=1)

                if len(missing_trading_days) > 0:
                    return {
                        'has_gap': True,
                        'reason': 'daily_gap',
                        'latest': latest,
                        'missing_start': pd.Timestamp(missing_trading_days[0]),
                        'missing_end': pd.Timestamp(missing_trading_days[-1]),
                        'days_missing': len(missing_trading_days)
                    }

                return {'has_gap': False, 'reason': 'up_to_date', 'latest': latest}

            else:
                # === 分钟线缺口检测 ===
                from datetime import timedelta
                from ..utils.trading_time_detector import TradingTimeDetectorV2

                # 1. 【优先】检查最新数据与当前时间的差距
                # 这是最重要的检查：数据是否太旧了？
                time_diff_minutes = (now - latest).total_seconds() / 60
                thresholds = {'1m': 5, '5m': 15, '15m': 30, '30m': 60, '1h': 120}
                threshold = thresholds.get(period, 15)

                if time_diff_minutes > threshold:
                    # 数据太旧了，优先补全最新数据
                    # 检查缺了多少个交易日
                    detector = TradingTimeDetectorV2()
                    latest_date = latest.date()
                    today = now.date()

                    missing_trading_days = []
                    current_date = latest_date + timedelta(days=1)

                    while current_date <= today:
                        try:
                            current_dt = datetime.combine(current_date, datetime.min.time())
                            if detector.is_trading_day(current_dt):
                                missing_trading_days.append(current_date)
                        except Exception:
                            weekday = current_date.weekday()
                            if weekday < 5:
                                missing_trading_days.append(current_date)
                        current_date += timedelta(days=1)

                    if len(missing_trading_days) > 0:
                        logger.warning(
                            f"[HotDBService] {symbol} {period} 数据已落后 {len(missing_trading_days)} 个交易日，"
                            f"最新数据: {latest}, 需要优先补全最新缺口"
                        )
                        return {
                            'has_gap': True,
                            'reason': 'latest_data_gap',
                            'latest': latest,
                            'missing_start': latest + timedelta(minutes=5),  # 从最新数据下一条开始
                            'missing_end': now,
                            'days_missing': len(missing_trading_days),
                            'minutes_missing': int(time_diff_minutes)
                        }

                # 2. 检查内部缺口（排除周末、节假日）
                # 只有数据是新的（没有落后），才检查内部缺口
                df_dict = hotdb.get_kline(
                    symbols=[symbol],
                    period=period,
                    count=10000
                )

                if symbol in df_dict and not df_dict[symbol].empty:
                    df = df_dict[symbol].copy()
                    df = df.sort_values('datetime').reset_index(drop=True)
                    time_diffs = df['datetime'].diff()

                    # 只检查超过4小时的缺口（排除正常隔夜和午休）
                    large_gaps = time_diffs[time_diffs > pd.Timedelta(hours=4)]

                    if len(large_gaps) > 0:
                        detector = TradingTimeDetectorV2()
                        max_missing_days = 0
                        max_gap_info = None

                        for gap_idx, gap in large_gaps.items():
                            if gap_idx == 0:
                                continue

                            gap_start = df.iloc[gap_idx - 1]['datetime']
                            gap_end = df.iloc[gap_idx]['datetime']

                            # 计算缺失的交易日
                            current_date = gap_start.date()
                            end_date = gap_end.date()
                            missing_trading_days = []

                            while current_date < end_date:
                                current_date = current_date + pd.Timedelta(days=1)
                                try:
                                    current_dt = datetime.combine(current_date, datetime.min.time())
                                    if detector.is_trading_day(current_dt):
                                        missing_trading_days.append(current_date)
                                except Exception:
                                    weekday = current_date.weekday()
                                    if weekday < 5:
                                        missing_trading_days.append(current_date)

                            if len(missing_trading_days) > max_missing_days:
                                max_missing_days = len(missing_trading_days)
                                max_gap_info = {
                                    'gap_start': gap_start,
                                    'gap_end': gap_end,
                                    'gap': gap,
                                    'missing_days': missing_trading_days
                                }

                        if max_gap_info:
                            logger.warning(
                                f"[HotDBService] {symbol} {period} 发现交易日缺口: "
                                f"{max_gap_info['gap_start']} -> {max_gap_info['gap_end']} "
                                f"(缺失 {max_missing_days} 个交易日)"
                            )

                            return {
                                'has_gap': True,
                                'reason': 'internal_gap',
                                'latest': df['datetime'].iloc[-1],
                                'missing_start': max_gap_info['gap_start'],
                                'missing_end': max_gap_info['gap_end'],
                                'gap_size_hours': max_gap_info['gap'].total_seconds() / 3600,
                                'missing_trading_days': max_missing_days
                            }

                # 2. 检查最新数据与当前时间的差距
                time_diff_minutes = (now - latest).total_seconds() / 60
                thresholds = {'1m': 5, '5m': 15, '15m': 30, '30m': 60, '1h': 120}
                threshold = thresholds.get(period, 15)

                if time_diff_minutes > threshold:
                    return {
                        'has_gap': True,
                        'reason': 'intraday_gap',
                        'latest': latest,
                        'missing_start': latest + timedelta(minutes=period * 5),  # 简化计算
                        'missing_end': now,
                        'minutes_missing': int(time_diff_minutes)
                    }

                return {'has_gap': False, 'reason': 'up_to_date', 'latest': latest}

        except Exception as e:
            logger.warning(f"[HotDBService] 检测 {symbol} {period} 缺口失败: {e}")
            return None

    def _is_data_fresh(self, symbol: str, period: str, df: pd.DataFrame) -> tuple:
        """检查数据新鲜度（Service 层业务逻辑）

        HotDB 过期策略：
        - 1m 数据：只保留 7 天滚动窗口，超过 7 天视为过期
        - 其他周期（5m/15m/30m/1h/1d/1w/1mon）：全量保留，永不过期
          （这些数据从 LocalDB 预热，会智能增量更新保持最新）

        Args:
            symbol: 股票代码
            period: 周期
            df: 数据

        Returns:
            (is_fresh: bool, days_old: int) 元组
        """
        if df.empty:
            return (True, 0)  # 无数据不算过期

        now = pd.Timestamp.now(tz=None).replace(tzinfo=None)
        latest_time = df['datetime'].iloc[-1]
        days_old = (now - latest_time).days

        # 1m 数据：超过 7 天视为过期
        is_fresh = not (period == '1m' and days_old > 7)

        if not is_fresh:
            logger.info(
                f"[HotDBService] {symbol} {period} 数据已过期: "
                f"最新 {latest_time.date()}, 已过期 {days_old} 天"
            )

        return (is_fresh, days_old)

    def smart_update(self, symbol: str, period: str) -> Dict[str, Any]:
        """智能增量更新（核心入口）

        完整流程：
        1. HotDB 有数据 → _detect_gap → 有缺口则补全 → 无缺口直接返回
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
                # HotDB 无数据，从 LocalDB 复制
                logger.info(f"[HotDB] {symbol} {period} 无数据，从 LocalDB 复制")
                copied = self.ensure_hotdb_data(symbol, period)

                if copied:
                    # 复制成功，重新获取数据信息
                    info = hotdb.get_data_info(symbol, period)

            # 2. 检测缺口（使用 Service 层的缺口检测逻辑）
            gap_info = self._detect_gap(symbol, period)

            if not gap_info:
                return {'success': False, 'error': '缺口检测失败', 'has_data': info.get('has_data', False)}

            if not gap_info['has_gap']:
                # 无缺口，获取现有数据
                df_dict = hotdb.get_kline(
                    symbols=[symbol],
                    period=period,
                    count=10000
                )

                df = df_dict.get(symbol)

                # Service 层业务逻辑：检查数据新鲜度
                if df is not None and not df.empty:
                    is_fresh, days_old = self._is_data_fresh(symbol, period, df)
                    if not is_fresh:
                        # 数据已过期，触发更新
                        logger.info(
                            f"[HotDBService] {symbol} {period} 数据过期（{days_old}天），触发更新"
                        )
                        # 清除过期数据
                        hotdb.delete_kline(symbol, period)
                        # 返回需要更新的标记
                        return {
                            'success': True,
                            'has_data': False,
                            'has_gap': True,
                            'reason': 'data_expired',
                            'df': None,
                            'latest': gap_info.get('latest'),
                            'symbol': symbol,
                            'period': period,
                            'should_update_localdb': False
                        }

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

            # 计算缺失的日期范围或数量
            missing_start = gap_info.get('missing_start')
            missing_end = gap_info.get('missing_end')

            # 计算缺失的日期范围
            missing_start = gap_info.get('missing_start')
            missing_end = gap_info.get('missing_end')

            # 1m 数据：使用 count 方式（PyTdx 不支持 1m 日期范围）
            use_date_range = True
            fetch_count = None

            if period == '1m':
                # 1m 数据始终使用 count 方式
                use_date_range = False

                if gap_info.get('reason') == 'no_data':
                    # 首次获取：800 条（约 13 小时）
                    fetch_count = 800
                    logger.info(f"[HotDB] {symbol} 1m 无数据，将获取 {fetch_count} 条（约 13 小时）")
                else:
                    # 有缺口：计算缺失条数
                    if missing_start and missing_end:
                        # 计算时间差（分钟）
                        diff_minutes = int((missing_end - missing_start).total_seconds() / 60)
                        # 余量只需要 5 条（5分钟），覆盖边界对齐误差即可
                        fetch_count = max(diff_minutes + 5, 10)  # 至少取 10 条
                        logger.info(f"[HotDB] {symbol} 1m 有缺口，将获取 {fetch_count} 条（缺口约 {diff_minutes} 分钟）")
                    else:
                        # 兜底：获取 100 条（约1.5小时）
                        fetch_count = 100
                        logger.info(f"[HotDB] {symbol} 1m 有缺口（无法计算时间差），将获取 {fetch_count} 条")
            elif gap_info.get('reason') == 'no_data' and not missing_start:
                # 其他周期首次获取
                from datetime import timedelta
                now = pd.Timestamp.now(tz=None).replace(tzinfo=None)

                if period in ['5m', '15m', '30m']:
                    # 5/15/30分钟：获取最近1个月
                    missing_end = now
                    missing_start = now - timedelta(days=30)
                elif period in ['1w', '1W', 'week']:
                    # 周K：获取最近2年（约100周）
                    missing_end = now
                    missing_start = now - timedelta(days=730)
                elif period in ['1mon', '1M', 'month']:
                    # 月K：获取最近3年（约36个月）
                    missing_end = now
                    missing_start = now - timedelta(days=1095)
                else:
                    # 日线：获取最近3个月
                    missing_end = now
                    missing_start = now - timedelta(days=90)

                if missing_start:
                    logger.info(f"[HotDB] {symbol} {period} 无数据，将获取 {missing_start.date()} 到 {missing_end.date()} 的数据")

            # 准备在线获取参数
            start_date_str = missing_start.strftime('%Y%m%d') if (use_date_range and missing_start) else None
            end_date_str = missing_end.strftime('%Y%m%d') if (use_date_range and missing_end) else None

            # 在线获取缺失部分
            df_new = self._complete_from_online(
                symbol, period,
                start_date=start_date_str if use_date_range else None,
                end_date=end_date_str if use_date_range else None,
                count=fetch_count if not use_date_range else None
            )

            if df_new is None or df_new.empty:
                # 在线获取失败，返回现有数据
                df_dict = hotdb.get_kline(
                    symbols=[symbol],
                    period=period,
                    count=10000
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
                count=10000
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
                    df = result[symbol]
                    # 日线数据无需转换（LocalDB 中已是手单位）
                    hotdb.save_kline(symbol, df, '1d')
                    logger.info(f"[HotDB] 转存 {symbol} 1d: {len(df)} 条")
                else:
                    logger.warning(f"[HotDB] LocalDB 中 {symbol} 无 1d 数据")
            except Exception as e:
                logger.warning(f"[HotDB] 转存 {symbol} 1d 失败: {e}")

            # 4. 从 LocalDB 复制 5m 数据（会自动触发聚合）
            try:
                result = localdb.get_kline(symbols=[symbol], period='5m', count=5000)
                if symbol in result and not result[symbol].empty:
                    df = result[symbol]
                    # === 修复：单位统一转换 ===
                    # LocalDB 存储的是原始股数，需要转换为手（÷100）
                    if 'volume' in df.columns:
                        df['volume'] = df['volume'] / 100
                        logger.debug(f"[HotDB] {symbol} 5m 成交量单位转换: 股 → 手")
                    hotdb.save_kline(symbol, df, '5m')
                    logger.info(f"[HotDB] 转存 {symbol} 5m: {len(df)} 条")
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

# -*- coding: utf-8 -*-
"""
HotDB 数据管理服务

提供 HotDB 热数据库的智能更新、缺口检测和数据补全功能。

调用链（符合架构规范）：
    HotdbService
        → KlineService.get_historical_kline()  # 获取在线数据
        → hotdb_adapter.save_kline()            # 保存到 HotDB

不直接调用在线适配器，保持架构分层。
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from loguru import logger
import pandas as pd

from myquant.core.market.adapters import get_adapter
from myquant.core.market.utils.trading_time_detector import is_trading_time


class HotdbService:
    """HotDB 数据管理服务"""

    def __init__(self):
        self._hotdb_adapter = None
        self._online_fetcher = None

    def _get_hotdb_adapter(self):
        """延迟获取 HotDB 适配器"""
        if self._hotdb_adapter is None:
            self._hotdb_adapter = get_adapter('hotdb')
        return self._hotdb_adapter

    def get_adapter(self, name: str):
        """获取适配器实例（供外部调用）"""
        return get_adapter(name)

    def _get_online_fetcher(self):
        """延迟获取在线K线获取器（避免循环导入）"""
        if self._online_fetcher is None:
            from myquant.core.market.services.fetchers import get_online_kline_fetcher
            self._online_fetcher = get_online_kline_fetcher()
        return self._online_fetcher

    # ─────────────────────────────────────────────
    # 预热功能
    # ─────────────────────────────────────────────

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
        localdb = get_adapter('localdb')

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

        logger.info(f"[HotdbService] 开始预热: {len(symbols)} 只股票 x {len(periods)} 个周期")

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

                        # 保存到 HotDB
                        success = hotdb.save_kline(symbol, df, period)

                        if success:
                            results['saved_count'] += 1
                            symbol_result['periods'][period] = {
                                'status': 'success',
                                'records': len(df)
                            }
                            logger.info(
                                f"[HotdbService] {symbol} {period} 预热成功: {len(df)} 条"
                            )
                        else:
                            results['failed_count'] += 1
                            symbol_result['periods'][period] = {
                                'status': 'failed',
                                'error': 'Save failed'
                            }
                    else:
                        results['skipped_count'] += 1
                        symbol_result['periods'][period] = {
                            'status': 'skipped',
                            'reason': 'No data in LocalDB'
                        }

                except Exception as e:
                    results['failed_count'] += 1
                    symbol_result['periods'][period] = {
                        'status': 'error',
                        'error': str(e)
                    }
                    logger.error(f"[HotdbService] {symbol} {period} 预热失败: {e}")

            results['details'].append(symbol_result)

        logger.info(
            f"[HotdbService] 预热完成: "
            f"成功={results['saved_count']}, "
            f"跳过={results['skipped_count']}, "
            f"失败={results['failed_count']}"
        )

        return results

    # ─────────────────────────────────────────────
    # 缺口检测
    # ─────────────────────────────────────────────

    def _detect_gap(self, symbol: str, period: str) -> Dict[str, Any]:
        """检测数据缺口

        Args:
            symbol: 股票代码 (如 600519.SH)
            period: 周期 (1d/1w/1mon/1m/5m/15m/30m/1h)

        Returns:
            {
                'has_gap': bool,
                'reason': str,  # 'no_data', 'intraday_gap', 'date_gap', 'stale'
                'latest': datetime,
                'expected_latest': datetime,
                'missing_count': int,  # 缺失的条数
                'days_missing': int,   # 缺失的天数
                'minutes_missing': int  # 缺失的分钟数
            }
        """
        hotdb = self._get_hotdb_adapter()
        if not hotdb or not hotdb.is_available():
            return {
                'has_gap': True,
                'reason': 'hotdb_unavailable',
                'latest': None,
                'expected_latest': None,
                'missing_count': 0,
                'days_missing': 0,
                'minutes_missing': 0
            }

        try:
            # 获取最新数据时间
            latest_time = hotdb.get_latest_time(symbol, period)
            record_count = hotdb.get_record_count(symbol, period)

            now = datetime.now()

            # 无数据
            if latest_time is None or record_count == 0:
                return {
                    'has_gap': True,
                    'reason': 'no_data',
                    'latest': None,
                    'expected_latest': now,
                    'missing_count': 1000,  # 默认获取1000条
                    'days_missing': 0,
                    'minutes_missing': 0
                }

            # 检查数据陈旧（历史数据缺失太久）
            days_since_latest = (now.date() - latest_time.date()).days
            stale_threshold = {
                '1m': 2,   # 1分钟线：2天没更新算陈旧
                '5m': 7,   # 5分钟线：7天没更新算陈旧
                '15m': 7,  # 15分钟线：7天
                '30m': 7,  # 30分钟线：7天
                '1h': 15,  # 1小时线：15天
                '1d': 30,  # 日线：30天
            }.get(period, 7)

            if days_since_latest > stale_threshold:
                # 计算需要获取的条数
                bars_per_day = {'1m': 240, '5m': 48, '15m': 16, '30m': 8, '1h': 4, '1d': 1}.get(period, 48)
                missing_count = days_since_latest * bars_per_day

                # 1m 数据特殊处理：最多只保留 7 天
                if period == '1m':
                    max_1m_count = 7 * 240  # 7天 × 240条/天
                    missing_count = min(missing_count, max_1m_count)
                else:
                    # 其他周期最多 10000 条
                    missing_count = min(missing_count, 10000)

                return {
                    'has_gap': True,
                    'reason': f'stale_data_{days_since_latest}_days_old',
                    'latest': latest_time,
                    'expected_latest': now,
                    'missing_count': missing_count,
                    'days_missing': days_since_latest,
                    'minutes_missing': 0
                }

            # 计算预期最新时间
            if period == '1d':
                # 日线：最新交易日收盘
                expected = self._get_latest_trading_day_close()
                # 【修复】日线只比较日期部分，忽略时间（数据存储的是00:00:00，期望的是15:00:00）
                is_stale = (expected.date() - latest_time.date()).days > 0
                if is_stale:
                    # 计算缺失天数
                    missing_days = (expected.date() - latest_time.date()).days
                    return {
                        'has_gap': True,
                        'reason': 'stale',
                        'latest': latest_time,
                        'expected_latest': expected,
                        'missing_count': missing_days,
                        'days_missing': missing_days,
                        'minutes_missing': 0
                    }
                return {
                    'has_gap': False,
                    'reason': 'ok',
                    'latest': latest_time,
                    'expected_latest': expected,
                    'missing_count': 0,
                    'days_missing': 0,
                    'minutes_missing': 0
                }
            else:
                # 分钟线：检查盘中缺口
                trading = is_trading_time()
                if not trading:
                    # 非交易时间，检查最后数据是否是今天
                    # 收盘后（15:00之后），应该有今天的数据
                    from datetime import timedelta

                    # 检查今天是否是交易日
                    today_is_trading_day = self._is_trading_day(now.date())

                    if today_is_trading_day:
                        # 今天是交易日，检查是否有今天的数据
                        latest_date = latest_time.date() if hasattr(latest_time, 'date') else latest_time
                        is_today = latest_date == now.date()

                        if not is_today:
                            # 今天是交易日但没有今天的数据，有缺口
                            # 【修复】计算从最后数据到今天之间有多少个交易日
                            bars_per_day = {'1m': 240, '5m': 48, '15m': 16, '30m': 8, '1h': 4}.get(period, 48)

                            # 计算缺失的交易日数量
                            missing_trading_days = 0
                            check_date = latest_date + timedelta(days=1)
                            max_check_days = min(7, (now.date() - latest_date).days)  # 最多检查7天

                            for _ in range(max_check_days):
                                if check_date > now.date():
                                    break
                                if self._is_trading_day(check_date):
                                    missing_trading_days += 1
                                check_date += timedelta(days=1)

                            # 至少缺失今天（1个交易日）
                            missing_trading_days = max(1, missing_trading_days)

                            logger.info(
                                f"[HotdbService] {symbol} {period} 缺失 {missing_trading_days} 个交易日数据 "
                                f"(最后数据: {latest_date}, 今天: {now.date()})"
                            )

                            return {
                                'has_gap': True,
                                'reason': 'missing_trading_days',
                                'latest': latest_time,
                                'expected_latest': now,
                                'missing_count': missing_trading_days * bars_per_day,
                                'days_missing': missing_trading_days,
                                'minutes_missing': 0
                            }
                        else:
                            # 关键修复：仅对分钟线/小时线检查数据量完整性
                            # 日线/周线/月线不需要此检查
                            intraday_periods = {'1m', '5m', '15m', '30m', '1h'}
                            if period in intraday_periods:
                                # 有今天的数据，检查数据量是否完整
                                expected_bars = {'1m': 240, '5m': 48, '15m': 16, '30m': 8, '1h': 4}.get(period, 48)
                                tolerance = 5  # 允许5条的误差

                                if record_count >= (expected_bars - tolerance):
                                    # 数据完整，无缺口
                                    return {
                                        'has_gap': False,
                                        'reason': 'market_closed_data_complete',
                                        'latest': latest_time,
                                        'expected_latest': latest_time,
                                        'missing_count': 0,
                                        'days_missing': 0,
                                        'minutes_missing': 0
                                    }
                                # 否则继续检查是否有缺口（数据不完整）
                            # 对于日线/周线/月线，不检查数据量，继续原有逻辑

                    # 今天不是交易日，或者有今天的数据，检查最近交易日
                    # 向前查找最近交易日
                    check_date = now.date()
                    for _ in range(15):  # 最多回溯15天（考虑长假）
                        check_date -= timedelta(days=1)
                        # 使用 _is_trading_day 正确判断交易日（包含节假日）
                        if self._is_trading_day(check_date):
                            # 找到最近交易日
                            last_trading_day = check_date
                            break
                    else:
                        # 极端情况：15天都没找到交易日
                        last_trading_day = now.date() - timedelta(days=1)

                    is_last_trading_day = latest_time.date() == last_trading_day
                    if not is_last_trading_day:
                        # 计算缺失的天数
                        days_missing = (now.date() - latest_time.date()).days
                        bars_per_day = {'1m': 240, '5m': 48, '15m': 16, '30m': 8, '1h': 4}.get(period, 48)
                        return {
                            'has_gap': True,
                            'reason': 'missing_trading_day',
                            'latest': latest_time,
                            'expected_latest': now,
                            'missing_count': days_missing * bars_per_day,
                            'days_missing': days_missing,
                            'minutes_missing': 0
                        }
                    # 最近交易日数据，无缺口
                    return {
                        'has_gap': False,
                        'reason': 'market_closed',
                        'latest': latest_time,
                        'expected_latest': latest_time,
                        'missing_count': 0,
                        'days_missing': 0,
                        'minutes_missing': 0
                    }

                # 交易时间，计算缺失分钟数
                minutes_missing = self._calc_minutes_missing(
                    latest_time, now, period
                )

                # 优化：仅对分钟线/小时线，即使时间差>5分钟，如果数据量完整也认为是数据已完整
                intraday_periods = {'1m', '5m', '15m', '30m', '1h'}
                if period in intraday_periods:
                    expected_bars = {'1m': 240, '5m': 48, '15m': 16, '30m': 8, '1h': 4}.get(period)
                    tolerance = 5

                    if record_count >= (expected_bars - tolerance) and minutes_missing > 5:
                        # 数据量完整，且时间差较大，可能是收盘后或数据已完整
                        # 检查最后数据时间是否是今天的交易时间
                        if latest_time.date() == now.date():
                            return {
                                'has_gap': False,
                                'reason': 'intraday_data_complete',
                                'latest': latest_time,
                                'expected_latest': latest_time,
                                'missing_count': 0,
                                'days_missing': 0,
                                'minutes_missing': 0
                            }

                return {
                    'has_gap': minutes_missing > 5,  # >5分钟算缺口
                    'reason': 'intraday_gap' if minutes_missing > 5 else 'ok',
                    'latest': latest_time,
                    'expected_latest': now,
                    'missing_count': minutes_missing + 10,  # 多获取10条缓冲
                    'days_missing': 0,
                    'minutes_missing': minutes_missing
                }

        except Exception as e:
            logger.error(f"[HotdbService] 检测缺口失败 {symbol} {period}: {e}")
            return {
                'has_gap': True,
                'reason': f'error: {e}',
                'latest': None,
                'expected_latest': None,
                'missing_count': 0,
                'days_missing': 0,
                'minutes_missing': 0
            }

    def _get_latest_trading_day_close(self) -> datetime:
        """获取最近交易日收盘时间（考虑节假日和当前时间）

        逻辑：
        1. 如果当前是交易日且已过15:00 → 返回今天15:00
        2. 如果当前是交易日但未过15:00（凌晨/盘中）→ 返回上一个交易日15:00
        3. 如果当前不是交易日 → 向前查找最近交易日，返回其15:00
        """
        from myquant.core.market.utils.trading_time_detector import get_trading_time_detector_v2

        detector = get_trading_time_detector_v2()
        now = datetime.now()
        market_close_time = now.replace(hour=15, minute=0, second=0, microsecond=0)

        # 判断今天是否是交易日
        is_today_trading = detector.is_trading_day(now.date())

        # 情况1：今天是交易日且已过收盘时间（15:00之后）
        if is_today_trading and now >= market_close_time:
            return market_close_time

        # 情况2：今天是交易日但还没到收盘时间（凌晨或盘中）
        # 情况3：今天不是交易日
        # 这两种情况都需要向前查找上一个交易日
        check_date = now.date()
        max_days_back = 15  # 最多向前查15天（考虑长假）

        for _ in range(max_days_back):
            # 回退一天
            check_date -= timedelta(days=1)
            # 检查是否是交易日
            if detector.is_trading_day(check_date):
                # 找到上一个交易日，返回其15:00收盘时间
                return datetime.combine(check_date, __import__('datetime').time(15, 0, 0))

        # 如果15天都没找到交易日（极端情况），返回昨天15:00
        yesterday = now.date() - timedelta(days=1)
        return datetime.combine(yesterday, __import__('datetime').time(15, 0, 0))

    def _is_trading_day(self, date_to_check) -> bool:
        """检查指定日期是否是交易日"""
        from myquant.core.market.utils.trading_time_detector import get_trading_time_detector_v2

        detector = get_trading_time_detector_v2()
        return detector.is_trading_day(date_to_check)

    def _calc_minutes_missing(
        self, latest: datetime, now: datetime, period: str
    ) -> int:
        """计算缺失的分钟数"""
        if latest is None:
            return 9999

        # 解析周期
        minutes_per_bar = {
            '1m': 1, '5m': 5, '15m': 15, '30m': 30, '1h': 60, '60m': 60
        }
        interval = minutes_per_bar.get(period, 1)

        # 简化计算
        delta = (now - latest).total_seconds() / 60
        return max(0, int(delta / interval))

    # ─────────────────────────────────────────────
    # 智能更新
    # ─────────────────────────────────────────────

    def smart_update(self, symbol: str, period: str) -> Dict[str, Any]:
        """智能更新：检测缺口并自动补全

        Args:
            symbol: 股票代码
            period: 周期

        Returns:
            {
                'success': bool,
                'records': int,
                'source': str,
                'error': str
            }
        """
        # 1. 检测缺口
        gap_info = self._detect_gap(symbol, period)

        if not gap_info['has_gap']:
            return {
                'success': True,
                'records': 0,
                'source': 'hotdb',
                'error': None,
                'reason': 'no_gap'
            }

        # 2. 从在线源获取数据（根据实际缺口大小动态决定）
        try:
            fetcher = self._get_online_fetcher()
            if fetcher is None:
                return {
                    'success': False,
                    'records': 0,
                    'source': None,
                    'error': 'OnlineKlineFetcher unavailable'
                }

            # 根据缺口大小动态决定获取数量
            missing_count = gap_info.get('missing_count', 0)
            start_date = None  # 初始化

            if 'stale_data' in gap_info.get('reason', ''):
                # 数据陈旧，根据缺失天数计算需要的条数
                count = missing_count
                # 【修复】计算 start_date 从最后数据的下一天开始获取
                latest_time = gap_info.get('latest')
                if latest_time:
                    from datetime import timedelta
                    start_date = (latest_time + timedelta(days=1)).strftime('%Y%m%d')
                    # 增加 count 以确保覆盖所有缺失数据
                    count = missing_count + 240  # 多加1天作为缓冲
            elif gap_info.get('reason') == 'missing_trading_days':
                # 【修复】缺失多个交易日，计算 start_date 并增加 count
                latest_time = gap_info.get('latest')
                if latest_time:
                    # 从最后数据的下一天开始获取
                    from datetime import timedelta
                    start_date = (latest_time + timedelta(days=1)).strftime('%Y%m%d')
                    # 增加 count 以确保覆盖所有缺失数据
                    count = missing_count + 240  # 多加1天作为缓冲
                else:
                    count = missing_count
            elif gap_info.get('reason') == 'no_data':
                # 无数据，获取默认数量
                count = 1000
            elif gap_info.get('reason') == 'missing_today_data':
                # 只缺今天的数据，获取少量
                count = 100
            elif gap_info.get('minutes_missing', 0) > 0:
                # 盘中缺口，根据缺失分钟数计算
                count = gap_info['minutes_missing'] + 10  # 多获取10条作为缓冲
            else:
                # 其他情况，获取默认数量
                count = 500

            # 限制范围：最少100条，最多10000条
            count = max(100, min(count, 10000))

            logger.info(
                f"[HotdbService] {symbol} {period} 缺口={gap_info.get('reason')}, "
                f"获取 {count} 条数据" + (f", start_date={start_date}" if start_date else "")
            )

            df = fetcher.fetch_kline_df(
                symbol=symbol,
                period=period,
                count=count,
                start_date=start_date
            )

            if df is None or df.empty:
                return {
                    'success': False,
                    'records': 0,
                    'source': None,
                    'error': 'No data from online source'
                }

            # 3. 保存到 HotDB（追加模式，不覆盖历史数据）
            hotdb = self._get_hotdb_adapter()
            if hotdb is None:
                return {
                    'success': False,
                    'records': 0,
                    'source': 'online',
                    'error': 'HotDB adapter unavailable'
                }

            # 统一 datetime 格式为 tz-naive（避免比较错误）
            # 读取 HotDB 现有数据，与新数据合并
            from myquant.core.market.utils.data_merger import DataMerger

            hotdb = self._get_hotdb_adapter()
            if hotdb is None:
                return {
                    'success': False,
                    'records': 0,
                    'source': 'online',
                    'error': 'HotDB adapter unavailable'
                }

            # 读取 HotDB 现有数据
            existing_data = hotdb.get_kline([symbol], period=period, count=1000000)

            # 使用 DataMerger 合并数据（normalize → concat → dedup → sort）
            if symbol in existing_data and not existing_data[symbol].empty:
                existing_df = existing_data[symbol]
                df_to_save = DataMerger.merge_kline_for_save(existing_df, df)
                logger.info(f"[HotdbService] smart_update 合并数据: 现有{len(existing_df)}条 + 新{len(df)}条 → {len(df_to_save)}条")
            else:
                # 无现有数据，只需 normalize
                df_copy = df.copy()
                df_copy['datetime'] = df_copy['datetime'].apply(DataMerger.normalize_datetime)
                df_to_save = df_copy

            success = hotdb.save_kline(symbol, df_to_save, period)

            # 通知缓存失效（HotDB 数据已更新）
            if success:
                try:
                    from myquant.core.market.services.cache_invalidator import get_cache_invalidator
                    invalidator = get_cache_invalidator()
                    # 使用默认 count=0 进行模糊匹配失效
                    invalidator.invalidate_kline(symbol, period, count=0)
                except Exception as e:
                    logger.warning(f"[HotdbService] 缓存失效通知失败: {e}")

            return {
                'success': success,
                'records': len(df) if success else 0,
                'source': 'online',
                'error': None if success else 'Save failed'
            }

        except Exception as e:
            logger.error(f"[HotdbService] smart_update 失败 {symbol} {period}: {e}")
            return {
                'success': False,
                'records': 0,
                'source': None,
                'error': str(e)
            }

    # ─────────────────────────────────────────────
    # 公共接口（供其他 Service 调用）
    # ─────────────────────────────────────────────

    def merge_and_save(self, symbol: str, period: str, df) -> bool:
        """合并新数据到 HotDB 并保存（公共接口）

        供 KlineService 等其他 Service 调用，
        不再需要它们知道 HotDB 的内部细节。

        Args:
            symbol: 股票代码
            period: 周期
            df: 新获取的K线数据（需包含 datetime 列）

        Returns:
            是否保存成功
        """
        import pandas as pd
        from myquant.core.market.utils.data_merger import DataMerger

        hotdb = self._get_hotdb_adapter()
        if hotdb is None or not hotdb.is_available():
            return False

        try:
            # 去掉 source 列（HotDB 不需要 source 列）
            df_to_save = df.drop(columns=['source']) if 'source' in df.columns else df

            # 读取 HotDB 现有数据
            existing_data = hotdb.get_kline([symbol], period=period, count=1000000)

            # 合并数据（normalize → concat → dedup → sort）
            if symbol in existing_data and not existing_data[symbol].empty:
                existing_df = existing_data[symbol]
                df_to_save = DataMerger.merge_kline_for_save(existing_df, df_to_save)
                logger.info(f"[HotdbService] merge_and_save: 合并 → {len(df_to_save)}条")
            else:
                # 无现有数据，只需 normalize
                df_to_save['datetime'] = df_to_save['datetime'].apply(DataMerger.normalize_datetime)

            # 保存到 HotDB
            success = hotdb.save_kline(symbol, df_to_save, period)

            if success:
                logger.info(f"[HotdbService] {symbol} {period} merge_and_save 完成 ({len(df_to_save)}条)")

                # 通知缓存失效（HotDB 数据已更新）
                try:
                    from myquant.core.market.services.cache_invalidator import get_cache_invalidator
                    invalidator = get_cache_invalidator()
                    invalidator.invalidate_kline(symbol, period)
                except Exception as e:
                    logger.warning(f"[HotdbService] 缓存失效通知失败: {e}")

            return success
        except Exception as e:
            logger.warning(f"[HotdbService] {symbol} {period} merge_and_save 失败: {e}")
            return False

    def detect_gap(self, symbol: str, period: str) -> dict:
        """检测数据缺口（公共接口）

        供 KlineService 等其他 Service 调用，
        不再需要直接调用私有方法 _detect_gap()。

        Args:
            symbol: 股票代码
            period: 周期

        Returns:
            缺口信息字典
        """
        return self._detect_gap(symbol, period)

    # ─────────────────────────────────────────────
    # 批量检查
    # ─────────────────────────────────────────────

    def auto_check_and_fill_today(
        self, symbols: List[str], periods: List[str] = None
    ) -> Dict[str, Any]:
        """自动检查并补全今天的数据

        Args:
            symbols: 股票代码列表
            periods: 周期列表，默认 ['1d', '1m']

        Returns:
            {
                'checked': int,
                'filled': int,
                'skipped': int,
                'failed': int,
                'details': dict
            }
        """
        if periods is None:
            periods = ['1d', '1m']

        checked = 0
        filled = 0
        skipped = 0
        failed = 0
        details = {}

        for symbol in symbols:
            details[symbol] = {}
            for period in periods:
                checked += 1

                # 检测缺口
                gap_info = self._detect_gap(symbol, period)

                if not gap_info['has_gap']:
                    skipped += 1
                    details[symbol][period] = {
                        'status': 'skipped',
                        'reason': gap_info['reason']
                    }
                    continue

                # 补全
                result = self.smart_update(symbol, period)

                if result['success']:
                    filled += 1
                    details[symbol][period] = {
                        'status': 'filled',
                        'records': result['records'],
                        'source': result['source']
                    }
                else:
                    failed += 1
                    details[symbol][period] = {
                        'status': 'failed',
                        'error': result['error']
                    }

        return {
            'checked': checked,
            'filled': filled,
            'skipped': skipped,
            'failed': failed,
            'details': details
        }

    def get_status(self, symbol: str = None) -> dict:
        """获取 HotDB 状态

        Args:
            symbol: 指定股票代码，为None时返回整体状态

        Returns:
            dict: 状态信息
        """
        try:
            adapter = self._get_hotdb_adapter()
            if not adapter or not adapter.is_available():
                return {
                    'success': False,
                    'error': 'HotDB 不可用',
                    'available': False
                }

            if symbol:
                # 获取指定股票状态
                periods = ['1m', '5m', '15m', '30m', '1h', '1d', '1w', '1M']
                symbol_status = {'symbol': symbol, 'periods': {}}

                for period in periods:
                    info = adapter.get_data_info(symbol, period)
                    symbol_status['periods'][period] = info

                return {'success': True, **symbol_status}

            return {'success': True, 'available': True}

        except Exception as e:
            logger.error(f"[HotdbService] 获取状态失败: {e}")
            return {'success': False, 'error': str(e)}

    def delete_symbol(self, symbol: str, period: str = None) -> dict:
        """删除指定股票的数据

        Args:
            symbol: 股票代码
            period: 周期，为None时删除所有周期

        Returns:
            dict: 删除结果
        """
        try:
            adapter = self._get_hotdb_adapter()
            if not adapter or not adapter.is_available():
                return {'success': False, 'error': 'HotDB 不可用'}

            success = adapter.delete_kline(symbol, period)

            return {'success': success, 'symbol': symbol, 'period': period}

        except Exception as e:
            logger.error(f"[HotdbService] 删除失败: {symbol} {period}, {e}")
            return {'success': False, 'error': str(e)}


# ─────────────────────────────────────────────
# 单例工厂
# ─────────────────────────────────────────────

_hotdb_service_instance: Optional[HotdbService] = None


def get_hotdb_service() -> HotdbService:
    """获取 HotdbService 单例"""
    global _hotdb_service_instance
    if _hotdb_service_instance is None:
        _hotdb_service_instance = HotdbService()
    return _hotdb_service_instance

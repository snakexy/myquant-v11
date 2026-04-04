"""
历史 K 线服务（KlineService）

核心 K 线服务 - V5场景化服务

定位：
- 统一的数据获取入口
- HotDB/LocalDB/在线源路由管理
- 智能增量更新

职责：
- 获取历史K线数据
- 数据源路由选择
- 增量更新管理
"""

from datetime import datetime
from typing import Dict, List, Optional

import pandas as pd
from loguru import logger

class KlineService:
    """
    核心 K 线服务 - V5场景化服务

    定位：
    - 统一的数据获取入口
    - HotDB/LocalDB/在线源路由管理
    - 智能增量更新

    职责：
    - 获取历史K线数据
    - 数据源路由选择（基于交易时间和数据类型）
    - 增量更新管理
    """

    def __init__(self):
        pass

    # ── 历史数据获取 ────────────────────────────

    def get_historical_kline(
        self,
        symbols: List[str],
        period: str,
        count: int = 500,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ):
        """获取历史K线数据（统一入口）

        数据源优先级：
        1. HotDB 快速通道（自选股全周期，<10ms）
        2. LocalDB 冷数据库（全标历史，~10ms）
        3. 在线源（V5双层路由：XtQuant/PyTdx/TdxQuant）

        Args:
            symbols: 股票代码列表
            period: 周期 (1m/5m/15m/30m/1h/1d/1w/1M)
            count: 返回条数
            start_date: 开始日期 (YYYYMMDD)
            end_date: 结束日期 (YYYYMMDD)

        Returns:
            (dict, data_source_name) 元组
        """
        result = {}
        data_source = "unknown"

        for symbol in symbols:
            # 1. HotDB 快速通道（智能增量更新）
            hotdb_df = self._try_hotdb(symbol, period, count, start_date, end_date)
            if hotdb_df is not None and not hotdb_df.empty:
                logger.info(f"[KlineService] {symbol} {period} 从 HotDB 获取 {len(hotdb_df)} 条")
                result[symbol] = hotdb_df
                data_source = "hotdb"
                continue

            # 2. LocalDB 冷数据库
            localdb_df = self._try_localdb(symbol, period, count, start_date, end_date)
            if localdb_df is not None and not localdb_df.empty:
                logger.info(f"[KlineService] {symbol} {period} 从 LocalDB 获取 {len(localdb_df)} 条")
                result[symbol] = localdb_df
                data_source = "localdb"
                continue

            # 3. 在线源（V5双层路由）
            online_df = self._fetch_from_online(symbol, period, count, start_date, end_date)
            if online_df is not None and not online_df.empty:
                logger.info(f"[KlineService] {symbol} {period} 从在线源获取 {len(online_df)} 条")
                result[symbol] = online_df
                data_source = "online"

        return (result, data_source)

    def _try_hotdb(
        self,
        symbol: str,
        period: str,
        count: int,
        start_date: Optional[str],
        end_date: Optional[str]
    ) -> Optional[pd.DataFrame]:
        """HotDB 快速通道

        - 检查 HotDB 是否有数据
        - 检测数据缺口
        - 智能增量补全
        """
        try:
            from myquant.core.market.services.hotdb_service import get_hotdb_service

            hotdb_service = get_hotdb_service()
            result = hotdb_service.smart_update(symbol, period)

            # 即使 has_data=False，如果有 df 说明是在线获取到了数据
            if result.get('success'):
                df = result.get('df')
                if df is not None and not df.empty:
                    # 应用日期范围过滤
                    if start_date or end_date:
                        from myquant.core.market.models import KlineDataset
                        dataset = KlineDataset.from_adapter(df, 'hotdb')
                        dataset = dataset.slice_by_date(start_date, end_date)
                        if count:
                            # 周K/月K返回全部数据，其他周期按 count 限制
                            if period not in ('1w', '1W', 'week', '1mon', '1M', 'month'):
                                dataset = dataset.filter_by_count(count, from_end=True)
                        return dataset.df
                    elif count:
                        # 周K/月K返回全部数据，其他周期按 count 限制
                        if period not in ('1w', '1W', 'week', '1mon', '1M', 'month'):
                            return df.tail(count)
                    return df

            return None
        except Exception as e:
            logger.debug(f"[KlineService] HotDB 快速通道失败: {e}")
            return None

    def _try_localdb(
        self,
        symbol: str,
        period: str,
        count: int,
        start_date: Optional[str],
        end_date: Optional[str]
    ) -> Optional[pd.DataFrame]:
        """LocalDB 冷数据库"""
        try:
            from myquant.core.market.adapters import get_adapter
            localdb = get_adapter('localdb')
            if localdb and localdb.is_available():
                df_dict = localdb.get_kline(
                    symbols=[symbol],
                    period=period,
                    count=count,
                    start_date=start_date,
                    end_date=end_date
                )
                if symbol in df_dict and not df_dict[symbol].empty:
                    return df_dict[symbol]
            return None
        except Exception as e:
            logger.debug(f"[KlineService] LocalDB 获取失败: {e}")
            return None

    def _fetch_from_online(
        self,
        symbol: str,
        period: str,
        count: int,
        start_date: Optional[str],
        end_date: Optional[str]
    ) -> pd.DataFrame:
        """从在线源获取（V5双层路由）"""
        from myquant.core.market.routing import DataLevel, get_source_selector
        from myquant.core.market.adapters import get_adapter

        selector = get_source_selector()
        chain = selector.get_fallback_chain_for_code(DataLevel.L3, symbol)

        # 周期感知：周K/月K排除 XtQuant（避免结算日期冲突）
        # XtQuant: 周五结算, PyTdx: 周日结算 → 混合会有重复数据
        # 周K: XtQuant ~3年, PyTdx 800条(~15年)
        # 月K: XtQuant ~3年, PyTdx 231条(~19年)
        if period in ('1w', '1W', 'week', '1mon', '1M', 'month'):
            # 完全排除 XtQuant，只使用 PyTdx 作为在线源
            chain = [s for s in chain if s != 'xtquant']
            logger.debug(f"[KlineService] {period} 排除 XtQuant，数据源链: {chain}")

        for source_name in chain:
            adapter = get_adapter(source_name)
            if adapter and adapter.is_available():
                try:
                    df_dict = adapter.get_kline(
                        symbols=[symbol],
                        period=period,
                        count=count,
                        start_date=start_date,
                        end_date=end_date
                    )
                    if symbol in df_dict and not df_dict[symbol].empty:
                        df = df_dict[symbol]
                        logger.info(f"[KlineService] {symbol} {period} 从 {source_name} 获取 {len(df)} 条")

                        # 保存到HotDB（异步模式，不阻塞返回）
                        self._save_to_hotdb_async(symbol, df, period)

                        return df
                except Exception as e:
                    logger.debug(f"[KlineService] {source_name} 获取失败: {e}")
                    continue

        return pd.DataFrame()

    def _save_to_hotdb_async(self, symbol: str, df: pd.DataFrame, period: str):
        """异步保存到HotDB（不阻塞主流程）

        当从在线源获取数据后，异步保存到HotDB以加速下次访问

        Args:
            symbol: 股票代码
            df: K线数据
            period: 周期
        """
        try:
            import threading

            def async_save():
                try:
                    from myquant.core.market.services.hotdb_service import get_hotdb_service
                    hotdb_service = get_hotdb_service()
                    hotdb = hotdb_service._get_hotdb_adapter()
                    if hotdb and hotdb.is_available():
                        hotdb.save_kline(symbol, df, period)
                        logger.debug(f"[KlineService] {symbol} {period} 异步保存到 HotDB: {len(df)} 条")
                except Exception as e:
                    logger.debug(f"[KlineService] 保存到 HotDB 失败: {e}")

            thread = threading.Thread(target=async_save, daemon=True)
            thread.start()
        except Exception as e:
            logger.debug(f"[KlineService] 启动异步保存失败: {e}")

    def download_to_localdb(
        self,
        symbols: List[str],
        periods: List[str],
        source: str = 'xtquant'
    ) -> dict:
        """从在线源下载历史数据到 LocalDB（长期存储）

        Args:
            symbols: 股票代码列表
            periods: 周期列表 (如 ['1d', '5m'])
            source: 数据源 (xtquant/pytdx)

        Returns:
            下载结果: {success: int, failed: int, details: {...}}
        """
        from loguru import logger
        from myquant.core.market.adapters import get_adapter

        results = {
            'success': 0,
            'failed': 0,
            'details': {}
        }

        # 获取适配器
        adapter = get_adapter(source)
        if not adapter or not adapter.is_available():
            logger.error(f"[KlineService] 数据源 {source} 不可用")
            return {'success': 0, 'failed': len(symbols) * len(periods), 'error': f'{source} 不可用'}

        # 获取 LocalDB 适配器
        localdb = get_adapter('localdb')

        for symbol in symbols:
            results['details'][symbol] = {}

            for period in periods:
                try:
                    logger.info(f"[KlineService] 下载 {symbol} {period} from {source}")

                    # 从在线源获取数据
                    df_dict = adapter.get_kline(
                        symbols=[symbol],
                        period=period,
                        count=10000
                    )

                    if symbol not in df_dict or df_dict[symbol].empty:
                        results['details'][symbol][period] = {'success': False, 'error': '无数据'}
                        results['failed'] += 1
                        continue

                    df = df_dict[symbol]
                    logger.info(f"[KlineService] {symbol} {period}: 获取 {len(df)} 条")

                    # 保存到 LocalDB
                    if localdb and localdb.is_available():
                        success = localdb.save_kline(symbol, df, period)
                        if success:
                            results['details'][symbol][period] = {'success': True, 'count': len(df)}
                            results['success'] += 1
                        else:
                            results['details'][symbol][period] = {'success': False, 'error': '保存失败'}
                            results['failed'] += 1
                    else:
                        results['details'][symbol][period] = {'success': False, 'error': 'LocalDB 不可用'}
                        results['failed'] += 1

                except Exception as e:
                    logger.error(f"[KlineService] {symbol} {period} 下载失败: {e}")
                    results['details'][symbol][period] = {'success': False, 'error': str(e)}
                    results['failed'] += 1

        logger.info(f"[KlineService] 下载完成: 成功 {results['success']}, 失败 {results['failed']}")
        return results

    def download_to_hotdb(
        self,
        symbols: List[str],
        periods: List[str],
        source: str = 'xtquant'
    ) -> dict:
        """从在线源下载临时数据到 HotDB（临时救急）

        Args:
            symbols: 股票代码列表
            periods: 周期列表 (如 ['1d', '5m'])
            source: 数据源 (xtquant/pytdx)

        Returns:
            下载结果: {success: int, failed: int, details: {...}}
        """
        from loguru import logger
        from myquant.core.market.adapters import get_adapter

        results = {
            'success': 0,
            'failed': 0,
            'details': {}
        }

        for symbol in symbols:
            results['details'][symbol] = {}

            for period in periods:
                try:
                    # 周K/月K强制使用 PyTdx（避免结算日期冲突）
                    actual_source = source
                    if period in ('1w', '1W', 'week', '1mon', '1M', 'month'):
                        actual_source = 'pytdx'
                        logger.info(f"[KlineService] {period} 强制使用 PyTdx")

                    # 获取适配器
                    adapter = get_adapter(actual_source)
                    if not adapter or not adapter.is_available():
                        logger.error(f"[KlineService] 数据源 {actual_source} 不可用")
                        results['details'][symbol][period] = {'success': False, 'error': f'{actual_source} 不可用'}
                        results['failed'] += 1
                        continue

                    logger.info(f"[KlineService] 下载临时数据 {symbol} {period} from {actual_source}")

                    # 从在线源获取数据
                    df_dict = adapter.get_kline(
                        symbols=[symbol],
                        period=period,
                        count=10000
                    )

                    if symbol not in df_dict or df_dict[symbol].empty:
                        results['details'][symbol][period] = {'success': False, 'error': '无数据'}
                        results['failed'] += 1
                        continue

                    df = df_dict[symbol]
                    logger.info(f"[KlineService] {symbol} {period}: 获取 {len(df)} 条到 HotDB")

                    # 保存到 HotDB
                    hotdb = get_adapter('hotdb')
                    if hotdb and hotdb.is_available():
                        success = hotdb.save_kline(symbol, df, period)
                        if success:
                            results['details'][symbol][period] = {'success': True, 'count': len(df)}
                            results['success'] += 1
                        else:
                            results['details'][symbol][period] = {'success': False, 'error': '保存失败'}
                            results['failed'] += 1
                    else:
                        results['details'][symbol][period] = {'success': False, 'error': 'HotDB 不可用'}
                        results['failed'] += 1

                except Exception as e:
                    logger.error(f"[KlineService] {symbol} {period} 下载失败: {e}")
                    results['details'][symbol][period] = {'success': False, 'error': str(e)}
                    results['failed'] += 1

        logger.info(f"[KlineService] 临时数据下载完成: 成功 {results['success']}, 失败 {results['failed']}")
        return results


# ─────────────────────────────────────────────
# 单例工厂
# ─────────────────────────────────────────────

_kline_service: Optional[KlineService] = None


def get_kline_service() -> KlineService:
    global _kline_service
    if _kline_service is None:
        _kline_service = KlineService()
    return _kline_service

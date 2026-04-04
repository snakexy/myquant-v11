"""
增量更新服务

在线获取填补缺失的交易日数据
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed

from myquant.core.market.models import AssetType
from myquant.core.market.routing import DataLevel, get_source_selector


class IncrementalUpdateService:
    """增量更新服务

    在线获取最新数据填补缺失
    """

    def __init__(self):
        self._selector = get_source_selector()
        self._available_sources = {}

    def update_symbols(
        self,
        symbols: List[str],
        period: str = '1d',
        days_back: int = 7,
        save_to_db: bool = False,
        parallel: bool = True
    ) -> dict:
        """更新股票数据

        Args:
            symbols: 股票列表
            period: 周期
            days_back: 回溯天数
            save_to_db: 是否保存到数据库
            parallel: 是否并行处理

        Returns:
            更新结果统计
        """
        results = {
            'success': 0,
            'failed': 0,
            'total_records': 0,
            'details': {},
            'duration': 0,
        }

        start_time = datetime.now()

        if parallel:
            results = self._update_parallel(symbols, period, days_back, save_to_db)
        else:
            results = self._update_sequential(symbols, period, days_back, save_to_db)

        results['duration'] = (datetime.now() - start_time).total_seconds()

        return results

    def _update_parallel(
        self,
        symbols: List[str],
        period: str,
        days_back: int,
        save_to_db: bool
    ) -> dict:
        """并行更新"""
        results = {
            'success': 0,
            'failed': 0,
            'total_records': 0,
            'details': {},
            'duration': 0,
        }

        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {
                executor.submit(self._update_single, symbol, period, days_back, save_to_db): symbol
                for symbol in symbols
            }

            for future in as_completed(futures):
                symbol = futures[future]

                try:
                    result = future.result(timeout=30)

                    if result.get('success'):
                        results['success'] += 1
                        results['total_records'] += result.get('records', 0)
                    else:
                        results['failed'] += 1

                    results['details'][symbol] = result

                except Exception as e:
                    results['failed'] += 1
                    results['details'][symbol] = {
                        'success': False,
                        'error': str(e)
                    }

        return results

    def _update_sequential(
        self,
        symbols: List[str],
        period: str,
        days_back: int,
        save_to_db: bool
    ) -> dict:
        """顺序更新"""
        results = {
            'success': 0,
            'failed': 0,
            'total_records': 0,
            'details': {},
            'duration': 0,
        }

        for symbol in symbols:
            result = self._update_single(symbol, period, days_back, save_to_db)

            if result.get('success'):
                results['success'] += 1
                results['total_records'] += result.get('records', 0)
            else:
                results['failed'] += 1

            results['details'][symbol] = result

        return results

    def _update_single(
        self,
        symbol: str,
        period: str,
        days_back: int,
        save_to_db: bool
    ) -> dict:
        """更新单个股票"""
        from myquant.core.market.adapters import get_adapter

        result = {
            'success': False,
            'records': 0,
            'error': None,
            'source': None,
        }

        try:
            # 检测缺失日期
            missing_dates = self._detect_missing_dates(symbol, period, days_back)

            if not missing_dates:
                result['success'] = True
                result['error'] = 'No missing data'
                return result

            # 选择在线数据源
            adapter_name = self._select_online_source(symbol)

            if adapter_name is None:
                result['error'] = 'No available adapter'
                return result

            adapter = get_adapter(adapter_name)
            if not adapter or not adapter.is_available():
                result['error'] = f'Adapter {adapter_name} not available'
                return result

            # 获取数据
            start_date = missing_dates[0].strftime('%Y%m%d')
            end_date = missing_dates[-1].strftime('%Y%m%d')

            df_dict = adapter.get_kline(
                symbols=[symbol],
                period=period,
                start_date=start_date,
                end_date=end_date
            )

            if symbol not in df_dict:
                result['error'] = 'No data returned'
                return result

            df = df_dict[symbol]
            result['records'] = len(df)
            result['source'] = adapter_name

            # 保存到数据库
            if save_to_db:
                self._archive_to_db(symbol, df, period)

            result['success'] = True

        except Exception as e:
            result['error'] = str(e)

        return result

    def _detect_missing_dates(
        self,
        symbol: str,
        period: str,
        days_back: int
    ) -> List[datetime]:
        """检测缺失日期"""
        missing = []

        # 生成应该有的日期列表
        end = datetime.now().date()
        dates = []
        for i in range(days_back):
            date = end - timedelta(days=i)
            # 排除周末
            if date.weekday() < 5:
                dates.append(date)

        # 检查本地是否有数据
        # 这里简化处理，实际应该查询 LocalDB
        # 如果没有实现，返回所有日期
        return [datetime.combine(d, datetime.min.time()) for d in dates]

    def _select_online_source(self, symbol: str) -> Optional[str]:
        """选择在线数据源"""
        from myquant.core.market.adapters import get_adapter

        asset_type = self._get_asset_type(symbol)

        if asset_type == 'stock':
            # 个股: XtQuant -> PyTdx
            for adapter in ['xtquant', 'pytdx']:
                adapter_instance = get_adapter(adapter)
                if adapter_instance and adapter_instance.is_available():
                    return adapter
        elif asset_type == 'index':
            # 指数: PyTdx -> XtQuant
            for adapter in ['pytdx', 'xtquant']:
                adapter_instance = get_adapter(adapter)
                if adapter_instance and adapter_instance.is_available():
                    return adapter
        elif asset_type == 'sector':
            # 板块: PyTdx
            adapter_instance = get_adapter('pytdx')
            if adapter_instance and adapter_instance.is_available():
                return 'pytdx'

        return None

    def _get_asset_type(self, code: str) -> str:
        """获取资产类型"""
        from myquant.core.market.models.stock import parse_asset_type
        asset_type = parse_asset_type(code)
        return asset_type.value

    def _archive_to_db(self, symbol: str, df: pd.DataFrame, period: str) -> bool:
        """归档到数据库"""
        try:
            # 这里应该调用 LocalDB 适配器的保存方法
            # 简化处理，直接返回 True
            return True
        except Exception:
            return False

    def get_same_day_closing_data(self, symbols: List[str]) -> Dict[str, dict]:
        """获取当天收盘快照

        Args:
            symbols: 股票列表

        Returns:
            {symbol: snapshot} 字典
        """
        from myquant.core.market.adapters import get_adapter

        snapshots = {}

        # 分批获取
        batch_size = 800

        for i in range(0, len(symbols), batch_size):
            batch = symbols[i:i + batch_size]

            adapter_name = self._selector.select(DataLevel.L1, AssetType.STOCK)

            if adapter_name is None:
                continue

            try:
                adapter = get_adapter(adapter_name)
                if not adapter or not adapter.is_available():
                    continue

                quotes = adapter.get_quote(batch)

                for code, quote in quotes.items():
                    if quote:
                        snapshots[code] = self._convert_snapshot_to_kline(quote)

            except Exception:
                continue

        return snapshots

    def _convert_snapshot_to_kline(self, snapshot: dict) -> dict:
        """将快照转换为 K线格式"""
        return {
            'datetime': snapshot.get('timestamp', ''),
            'open': snapshot.get('open', 0),
            'high': snapshot.get('high', 0),
            'low': snapshot.get('low', 0),
            'close': snapshot.get('price', 0),
            'volume': snapshot.get('volume', 0),
            'amount': snapshot.get('amount', 0),
        }

    def detect_missing(
        self,
        symbols: List[str],
        period: str = '1d',
        days_back: int = 30
    ) -> Dict[str, List[str]]:
        """检测缺失数据

        Args:
            symbols: 股票列表
            period: 周期
            days_back: 回溯天数

        Returns:
            {symbol: [missing_dates]} 字典
        """
        missing_info = {}

        for symbol in symbols:
            missing_dates = self._detect_missing_dates(symbol, period, days_back)
            missing_info[symbol] = [
                d.strftime('%Y-%m-%d') for d in missing_dates
            ]

        return missing_info

    def get_status(self) -> dict:
        """获取服务状态"""
        return {
            'service': 'IncrementalUpdateService',
            'available_sources': self._check_available_sources(),
        }

    def _check_available_sources(self) -> dict:
        """检查可用数据源"""
        from myquant.core.market.adapters import get_adapter

        sources = ['xtquant', 'tdxquant', 'pytdx', 'localdb']

        status = {}
        for source in sources:
            try:
                adapter = get_adapter(source)
                status[source] = adapter.is_available() if adapter else False
            except Exception:
                status[source] = False

        return status


# 单例实例
_incremental_service: Optional[IncrementalUpdateService] = None


def get_incremental_service() -> IncrementalUpdateService:
    """获取 IncrementalUpdateService 单例实例"""
    global _incremental_service
    if _incremental_service is None:
        _incremental_service = IncrementalUpdateService()
    return _incremental_service

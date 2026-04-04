"""
数据转换服务

批量转换 TDX 本地数据到 Qlib 格式
"""

from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed

from myquant.core.market.models import AssetType


class DataConversionService:
    """数据转换服务

    批量转换 TDX 本地数据到 Qlib 格式
    """

    def __init__(self):
        self._progress = {
            'total': 0,
            'converted': 0,
            'failed': 0,
            'current_symbol': None,
            'start_time': None,
        }

    def convert_batch(
        self,
        symbols: List[str],
        period: str = '1d',
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        save_to_qlib: bool = True,
        parallel: bool = True
    ) -> dict:
        """批量转换数据

        Args:
            symbols: 股票列表
            period: 周期
            start_date: 开始日期
            end_date: 结束日期
            save_to_qlib: 是否保存到 Qlib
            parallel: 是否并行处理

        Returns:
            转换结果统计
        """
        self._progress = {
            'total': len(symbols),
            'converted': 0,
            'failed': 0,
            'current_symbol': None,
            'start_time': datetime.now(),
        }

        results = {
            'success': 0,
            'failed': 0,
            'total_records': 0,
            'details': {},
            'duration': 0,
        }

        if parallel:
            results = self._convert_parallel(
                symbols, period, start_date, end_date, save_to_qlib
            )
        else:
            results = self._convert_sequential(
                symbols, period, start_date, end_date, save_to_qlib
            )

        results['duration'] = (datetime.now() - self._progress['start_time']).total_seconds()

        return results

    def _convert_parallel(
        self,
        symbols: List[str],
        period: str,
        start_date: Optional[str],
        end_date: Optional[str],
        save_to_qlib: bool
    ) -> dict:
        """并行转换"""
        results = {
            'success': 0,
            'failed': 0,
            'total_records': 0,
            'details': {},
            'duration': 0,
        }

        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {
                executor.submit(
                    self._convert_single,
                    symbol, period, start_date, end_date, save_to_qlib
                ): symbol
                for symbol in symbols
            }

            for future in as_completed(futures):
                symbol = futures[future]

                self._progress['current_symbol'] = symbol

                try:
                    result = future.result(timeout=60)

                    if result.get('success'):
                        results['success'] += 1
                        results['total_records'] += result.get('records', 0)
                        self._progress['converted'] += 1
                    else:
                        results['failed'] += 1
                        self._progress['failed'] += 1

                    results['details'][symbol] = result

                except Exception as e:
                    results['failed'] += 1
                    self._progress['failed'] += 1
                    results['details'][symbol] = {
                        'success': False,
                        'error': str(e)
                    }

        return results

    def _convert_sequential(
        self,
        symbols: List[str],
        period: str,
        start_date: Optional[str],
        end_date: Optional[str],
        save_to_qlib: bool
    ) -> dict:
        """顺序转换"""
        results = {
            'success': 0,
            'failed': 0,
            'total_records': 0,
            'details': {},
            'duration': 0,
        }

        for symbol in symbols:
            self._progress['current_symbol'] = symbol

            result = self._convert_single(
                symbol, period, start_date, end_date, save_to_qlib
            )

            if result.get('success'):
                results['success'] += 1
                results['total_records'] += result.get('records', 0)
                self._progress['converted'] += 1
            else:
                results['failed'] += 1
                self._progress['failed'] += 1

            results['details'][symbol] = result

        return results

    def _convert_single(
        self,
        symbol: str,
        period: str,
        start_date: Optional[str],
        end_date: Optional[str],
        save_to_qlib: bool
    ) -> dict:
        """转换单个股票"""
        from myquant.core.market.adapters import get_adapter

        result = {
            'success': False,
            'records': 0,
            'error': None,
            'source': 'tdxlocal',
        }

        try:
            # 使用 TdxLocal 适配器读取本地数据
            adapter = get_adapter('tdxlocal')

            if not adapter or not adapter.is_available():
                result['error'] = 'TdxLocal adapter not available'
                return result

            # 读取数据
            df_dict = adapter.get_kline(
                symbols=[symbol],
                period=period,
                start_date=start_date,
                end_date=end_date
            )

            if symbol not in df_dict:
                result['error'] = 'No data found'
                return result

            df = df_dict[symbol]

            if df.empty:
                result['error'] = 'Empty data'
                return result

            result['records'] = len(df)

            # 保存到 Qlib
            if save_to_qlib:
                self._save_to_qlib(symbol, df, period)

            result['success'] = True

        except Exception as e:
            result['error'] = str(e)

        return result

    def _save_to_qlib(
        self,
        symbol: str,
        df: pd.DataFrame,
        period: str
    ) -> bool:
        """保存到 Qlib 数据库"""
        try:
            # 这里应该调用 Qlib 的保存 API
            # 简化处理，将数据保存为 CSV
            from myquant.core.market.models.stock import normalize_stock_code

            code = normalize_stock_code(symbol)

            # 确定 Qlib 目录
            qlib_dir = Path("data/qlib_data")
            qlib_dir.mkdir(parents=True, exist_ok=True)

            # 保存为 CSV (临时方案)
            csv_path = qlib_dir / f"{code}_{period}.csv"
            df.to_csv(csv_path, index=False)

            return True

        except Exception:
            return False

    def get_progress(self) -> dict:
        """获取转换进度"""
        progress = self._progress.copy()

        if progress['start_time']:
            elapsed = (datetime.now() - progress['start_time']).total_seconds()
            progress['elapsed'] = elapsed

            if progress['total'] > 0:
                progress['percentage'] = (
                    (progress['converted'] + progress['failed']) / progress['total'] * 100
                )
            else:
                progress['percentage'] = 0

            # 估算剩余时间
            if progress['converted'] > 0:
                avg_time = elapsed / progress['converted']
                remaining = progress['total'] - progress['converted'] - progress['failed']
                progress['estimated_remaining'] = avg_time * remaining

        return progress


# 单例实例
_conversion_service: Optional[DataConversionService] = None


def get_conversion_service() -> DataConversionService:
    """获取 DataConversionService 单例实例"""
    global _conversion_service
    if _conversion_service is None:
        _conversion_service = DataConversionService()
    return _conversion_service

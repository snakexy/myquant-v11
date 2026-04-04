"""
实时监控服务

提供热点板块发现、异常股票检测等功能
"""

from typing import List, Optional
from datetime import datetime

from myquant.core.market.models import SectorData, QuoteData, AssetType
from myquant.core.market.routing import DataLevel, get_source_selector


class RealtimeMonitorService:
    """实时监控服务

    提供热点板块发现、异常检测、行情监控等功能
    """

    def __init__(self):
        self._selector = get_source_selector()

    def find_hot_sectors(
        self,
        limit: int = 20,
        min_change_pct: float = 0.5
    ) -> List[SectorData]:
        """发现热点板块

        Args:
            limit: 返回数量
            min_change_pct: 最小涨跌幅阈值

        Returns:
            热点板块列表（按涨跌幅排序）
        """
        from myquant.core.market.adapters import get_adapter

        # 选择数据源
        adapter_name = self._selector.select(DataLevel.L1, AssetType.SECTOR_BLOCK)

        if adapter_name is None:
            return []

        try:
            adapter = get_adapter(adapter_name)
            if not adapter or not adapter.is_available():
                return []

            # 获取板块列表
            sectors = self._get_all_sector_codes(adapter)

            # 获取行情
            quotes = adapter.get_quote(sectors)

            # 转换为 SectorData
            sector_list = []
            for code, quote in quotes.items():
                if quote:
                    sector_list.append(SectorData(
                        code=code,
                        name=quote.get('name', ''),
                        sector_type='sector',
                        index=quote.get('price', 0),
                        change_pct=quote.get('change_pct', 0),
                        up_count=quote.get('up_count', 0),
                        down_count=quote.get('down_count', 0),
                        component_count=quote.get('component_count', 0),
                        amount=quote.get('amount', 0),
                        volume_ratio=quote.get('volume_ratio', 0.0),
                        turnover_rate=quote.get('turnover_rate', 0.0),
                        amplitude=quote.get('amplitude', 0.0),
                        pe_ratio=quote.get('pe_ratio', 0.0),
                        pb_ratio=quote.get('pb_ratio', 0.0),
                        timestamp=datetime.now().isoformat()
                    ))

            # 过滤和排序
            hot_sectors = [
                s for s in sector_list
                if s.is_hot and s.change_pct >= min_change_pct
            ]

            hot_sectors.sort(key=lambda x: x.change_pct, reverse=True)

            return hot_sectors[:limit]

        except Exception:
            return []

    def find_hot_stocks(
        self,
        sector_code: Optional[str] = None,
        limit: int = 50,
        min_change_pct: float = 3.0
    ) -> List[QuoteData]:
        """发现热点股票

        Args:
            sector_code: 板块代码（None 表示全市场）
            limit: 返回数量
            min_change_pct: 最小涨跌幅阈值

        Returns:
            热点股票列表（按涨跌幅排序）
        """
        from myquant.core.market.adapters import get_adapter

        # 获取股票列表
        if sector_code:
            stocks = self._get_stocks_in_sector(sector_code)
        else:
            stocks = self._get_all_stock_codes()

        if not stocks:
            return []

        # 分批获取行情（每次最多 800 只）
        batch_size = 800
        all_quotes = []

        for i in range(0, len(stocks), batch_size):
            batch = stocks[i:i + batch_size]

            # 选择适配器
            adapter_name = self._selector.select(DataLevel.L1, AssetType.STOCK)

            if adapter_name is None:
                continue

            try:
                adapter = get_adapter(adapter_name)
                if not adapter or not adapter.is_available():
                    continue

                quotes = adapter.get_quote(batch)

                for code, quote in quotes.items():
                    if quote and quote.get('change_pct', 0) >= min_change_pct:
                        all_quotes.append(QuoteData(
                            code=code,
                            name=quote.get('name', ''),
                            price=quote.get('price', 0),
                            change=quote.get('change', 0),
                            change_pct=quote.get('change_pct', 0),
                            volume=quote.get('volume', 0),
                            amount=quote.get('amount', 0),
                            timestamp=quote.get('timestamp', '')
                        ))

            except Exception:
                continue

        # 排序
        all_quotes.sort(key=lambda x: x.change_pct, reverse=True)

        return all_quotes[:limit]

    def find_anomaly_stocks(
        self,
        symbols: List[str],
        volume_ratio_threshold: float = 3.0,
        swing_threshold: float = 5.0
    ) -> List[dict]:
        """发现异常股票

        Args:
            symbols: 股票列表
            volume_ratio_threshold: 成交量倍数阈值
            swing_threshold: 振幅阈值

        Returns:
            异常股票列表
        """
        from myquant.core.market.adapters import get_adapter

        anomalies = []

        # 分批获取行情
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
                    if not quote:
                        continue

                    # 检查成交量异常
                    volume = quote.get('volume', 0)
                    amount = quote.get('amount', 0)

                    # 检查振幅异常
                    high = quote.get('high', 0)
                    low = quote.get('low', 0)
                    last_close = quote.get('last_close', 0)

                    if last_close > 0:
                        amplitude = (high - low) / last_close * 100
                    else:
                        amplitude = 0

                    reasons = []

                    if amplitude >= swing_threshold:
                        reasons.append(f"振幅{amplitude:.2f}%")

                    if volume >= volume_ratio_threshold * 1000000:  # 简化判断
                        reasons.append(f"成交量{volume:,}")

                    if reasons:
                        anomalies.append({
                            'code': code,
                            'name': quote.get('name', ''),
                            'price': quote.get('price', 0),
                            'change_pct': quote.get('change_pct', 0),
                            'amplitude': amplitude,
                            'volume': volume,
                            'reasons': reasons
                        })

            except Exception:
                continue

        return anomalies

    def get_market_summary(self) -> dict:
        """获取市场概览"""
        from myquant.core.market.adapters import get_adapter

        # 获取主要指数
        indices = ['000001.SH', '399001.SZ', '000300.SH']

        adapter_name = self._selector.select(DataLevel.L1, AssetType.INDEX)

        summary = {
            'timestamp': datetime.now().isoformat(),
            'indices': {},
            'hot_sectors': [],
            'hot_stocks': [],
        }

        if adapter_name:
            try:
                adapter = get_adapter(adapter_name)
                if adapter and adapter.is_available():
                    quotes = adapter.get_quote(indices)

                    for code, quote in quotes.items():
                        if quote:
                            summary['indices'][code] = {
                                'name': quote.get('name', ''),
                                'price': quote.get('price', 0),
                                'change_pct': quote.get('change_pct', 0),
                            }

            except Exception:
                pass

        # 获取热点板块
        summary['hot_sectors'] = self.find_hot_sectors(limit=5)

        # 获取热点股票
        summary['hot_stocks'] = self.find_hot_stocks(limit=10)

        return summary

    def _get_all_sector_codes(self, adapter) -> List[str]:
        """获取所有板块代码"""
        try:
            # 尝试调用 TdxQuant 的 get_sector_list
            if hasattr(adapter, 'get_sector_list'):
                sectors = adapter.get_sector_list()
                return [s.get('code') for s in sectors if 'code' in s]
        except Exception:
            pass

        # 默认板块列表
        return ['880001', '880002', '880003', '880004', '880005']

    def _get_all_stock_codes(self) -> List[str]:
        """获取所有股票代码"""
        from myquant.core.market.adapters import get_adapter

        try:
            # 从 LocalDB 获取股票列表
            adapter = get_adapter('localdb')
            if adapter and hasattr(adapter, 'get_stock_list'):
                stocks = adapter.get_stock_list()
                return [s.get('code') for s in stocks if 'code' in s]
        except Exception:
            pass

        return []

    def _get_stocks_in_sector(self, sector_code: str) -> List[str]:
        """获取板块成分股"""
        from myquant.core.market.adapters import get_adapter

        try:
            adapter = get_adapter('tdxquant')
            if adapter and adapter.is_available() and hasattr(adapter, 'get_sector_components'):
                components = adapter.get_sector_components(sector_code)
                return [c.get('code') for c in components if 'code' in c]
        except Exception:
            pass

        return []


# 单例实例
_monitor_service: Optional[RealtimeMonitorService] = None


def get_monitor_service() -> RealtimeMonitorService:
    """获取 RealtimeMonitorService 单例实例"""
    global _monitor_service
    if _monitor_service is None:
        _monitor_service = RealtimeMonitorService()
    return _monitor_service

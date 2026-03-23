"""
V5 适配器通用基类

提供数据标准化等通用功能
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Callable
import pandas as pd
import logging

logger = logging.getLogger(__name__)


class DataAdapter(ABC):
    """V5 适配器抽象基类

    简化的适配器接口，只包含核心方法
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """适配器名称"""
        pass

    @abstractmethod
    def get_kline(
        self,
        symbols: List[str],
        period: str = '1d',
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        count: Optional[int] = None,
        adjust_type: str = 'none'
    ) -> Dict[str, pd.DataFrame]:
        """获取 K线数据

        Args:
            symbols: 代码列表
            period: 周期 (1m/5m/15m/30m/1h/1d/1w/1mon)
            start_date: 开始日期 (YYYYMMDD)
            end_date: 结束日期 (YYYYMMDD)
            count: 数据条数
            adjust_type: 复权类型 (none/qfq/hfq)

        Returns:
            {symbol: DataFrame} 字典，DataFrame 包含 OHLCV 列
        """
        pass

    @abstractmethod
    def get_quote(self, symbols: List[str]) -> Dict[str, dict]:
        """获取实时行情

        Args:
            symbols: 代码列表

        Returns:
            {symbol: quote_dict} 字典
        """
        pass

    def is_available(self) -> bool:
        """检查适配器是否可用"""
        return True


class V5DataAdapter(DataAdapter):
    """V5 适配器通用基类

    提供数据标准化、格式转换等通用功能
    """

    def __init__(self):
        self._name = ""

    @property
    def name(self) -> str:
        return self._name

    def _normalize_quote_dict(
        self, code: str, quote: dict, source: str
    ) -> dict:
        """将原始 quote 标准化为统一格式"""
        price = (
            quote.get('price') or quote.get('Now')
            or quote.get('lastPrice') or 0
        )
        pre_close = (
            quote.get('pre_close') or quote.get('LastClose')
            or quote.get('lastClose') or 0
        )
        try:
            price = float(price)
            pre_close = float(pre_close)
        except (TypeError, ValueError):
            price, pre_close = 0.0, 0.0

        change = round(price - pre_close, 4)
        change_pct = round(change / pre_close * 100, 2) if pre_close else 0

        buyp = quote.get('Buyp') or quote.get('bidPrice') or []
        sellp = quote.get('Sellp') or quote.get('askPrice') or []
        buyv = quote.get('Buyv') or quote.get('bidVol') or []
        sellv = quote.get('Sellv') or quote.get('askVol') or []

        return {
            'code': code,
            'price': price,
            'open': float(quote.get('open') or quote.get('Open') or 0),
            'high': float(quote.get('high') or quote.get('Max') or 0),
            'low': float(quote.get('low') or quote.get('Min') or 0),
            'close': price,
            'pre_close': pre_close,
            'volume': float(
                quote.get('vol') or quote.get('Volume')
                or quote.get('volume') or 0
            ),
            'amount': float(
                quote.get('amount') or quote.get('Amount') or 0
            ),
            'change': change,
            'change_pct': change_pct,
            'bid1': float(quote.get('bid1') or (buyp[0] if buyp else 0)),
            'ask1': float(quote.get('ask1') or (sellp[0] if sellp else 0)),
            'bid_vol1': float(
                quote.get('bid_vol1') or (buyv[0] if buyv else 0)
            ),
            'ask_vol1': float(
                quote.get('ask_vol1') or (sellv[0] if sellv else 0)
            ),
            'bid2': float(quote.get('bid2') or (buyp[1] if len(buyp) > 1 else 0)),
            'ask2': float(quote.get('ask2') or (sellp[1] if len(sellp) > 1 else 0)),
            'bid_vol2': float(
                quote.get('bid_vol2') or (buyv[1] if len(buyv) > 1 else 0)
            ),
            'ask_vol2': float(
                quote.get('ask_vol2') or (sellv[1] if len(sellv) > 1 else 0)
            ),
            'bid3': float(quote.get('bid3') or (buyp[2] if len(buyp) > 2 else 0)),
            'ask3': float(quote.get('ask3') or (sellp[2] if len(sellp) > 2 else 0)),
            'bid_vol3': float(
                quote.get('bid_vol3') or (buyv[2] if len(buyv) > 2 else 0)
            ),
            'ask_vol3': float(
                quote.get('ask_vol3') or (sellv[2] if len(sellv) > 2 else 0)
            ),
            'bid4': float(quote.get('bid4') or (buyp[3] if len(buyp) > 3 else 0)),
            'ask4': float(quote.get('ask4') or (sellp[3] if len(sellp) > 3 else 0)),
            'bid_vol4': float(
                quote.get('bid_vol4') or (buyv[3] if len(buyv) > 3 else 0)
            ),
            'ask_vol4': float(
                quote.get('ask_vol4') or (sellv[3] if len(sellv) > 3 else 0)
            ),
            'bid5': float(quote.get('bid5') or (buyp[4] if len(buyp) > 4 else 0)),
            'ask5': float(quote.get('ask5') or (sellp[4] if len(sellp) > 4 else 0)),
            'bid_vol5': float(
                quote.get('bid_vol5') or (buyv[4] if len(buyv) > 4 else 0)
            ),
            'ask_vol5': float(
                quote.get('ask_vol5') or (sellv[4] if len(sellv) > 4 else 0)
            ),
            'data_source': source,
        }

    def _normalize_kline_df(self, df: pd.DataFrame, source: str) -> pd.DataFrame:
        """标准化 K线 DataFrame

        Args:
            df: 原始 DataFrame
            source: 数据源名称

        Returns:
            标准化后的 DataFrame
        """
        if df is None or df.empty:
            return df

        # 确保必要的列存在
        required_cols = ['datetime', 'open', 'high', 'low', 'close', 'volume']
        for col in required_cols:
            if col not in df.columns:
                logger.warning(f"[{source}] 缺少列: {col}")

        # 添加数据源标记
        df['data_source'] = source

        return df


# 适配器注册表
_adapter_registry: Dict[str, Callable] = {}


def register_adapter(name: str, factory: Callable) -> None:
    """注册适配器工厂"""
    _adapter_registry[name.lower()] = factory
    logger.debug(f"Registered adapter: {name}")


def get_adapter(name: str) -> Optional[DataAdapter]:
    """获取适配器实例"""
    factory = _adapter_registry.get(name.lower())
    if factory is None:
        logger.warning(f"Adapter not found: {name}")
        return None
    return factory()

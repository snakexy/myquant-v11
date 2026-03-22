# -*- coding: utf-8 -*-
"""
V5 XtQuant 适配器

直接调用 xtquant.xtdata SDK，不依赖 V4 适配器
简化为单实例模式
"""

from typing import Dict, List, Optional, Callable
from loguru import logger
import pandas as pd

try:
    from xtquant import xtdata
    XTQUANT_AVAILABLE = True
except ImportError:
    XTQUANT_AVAILABLE = False
    logger.warning("xtquant 未安装")

from .base import V5DataAdapter


class V5XtQuantAdapter(V5DataAdapter):
    """V5 XtQuant 适配器

    直接调用 xtdata，简化为单实例模式
    """

    def __init__(self):
        super().__init__()
        self._name = 'xtquant'
        self._subscriptions: Dict[str, Callable] = {}

    def _ensure_xtdata(self):
        """确保 xtdata 可用"""
        if not XTQUANT_AVAILABLE:
            return False
        return True

    def _to_xt_symbol(self, symbol: str) -> str:
        """转换为 XtQuant 格式（带市场后缀）"""
        if '.' in symbol:
            return symbol

        if symbol[0] in ('6', '5', '9'):
            return f"{symbol}.SH"
        else:
            return f"{symbol}.SZ"

    def _to_xt_period(self, period: str) -> str:
        """转换周期到 XtQuant 格式"""
        period_map = {
            '1m': '1m', '5m': '5m', '15m': '15m', '30m': '30m',
            '1h': '60m', '60m': '60m',
            '1d': '1d', 'd': '1d', 'day': '1d',
            '1w': '1w', 'w': '1w', 'week': '1w',
            '1M': '1mon', 'M': '1mon', '1mon': '1mon', 'mon': '1mon',
        }
        return period_map.get(period, '1d')

    def _to_dividend_type(self, adjust_type: str) -> str:
        """转换复权类型（必须是字符串）"""
        if adjust_type in ('front', 'qf', 'qfq', 'qianfuquan'):
            return 'front'
        elif adjust_type in ('back', 'hf', 'hfq', 'houfuquan'):
            return 'back'
        else:
            return 'none'

    def get_kline(
        self,
        symbols: List[str],
        period: str = '1d',
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        count: Optional[int] = None,
        adjust_type: str = 'none'  # 参数保留（兼容性），实际强制为不复权
    ) -> Dict[str, pd.DataFrame]:
        """获取 K线数据

        注意：此方法始终返回不复权原始数据，复权由服务层统一处理。
        """
        if not self._ensure_xtdata():
            return {}

        result = {}
        xt_period = self._to_xt_period(period)

        # 始终获取不复权原始数据（复权由服务层统一处理）
        dividend_type = 'none'

        # 字段列表
        field_list = ['time', 'open', 'high', 'low', 'close', 'volume', 'amount']

        # 转换为 XtQuant 格式
        xt_symbols = [self._to_xt_symbol(s) for s in symbols]

        try:
            # 获取数据
            data = xtdata.get_market_data_ex(
                field_list=field_list,
                stock_list=xt_symbols,
                period=xt_period,
                start_time='',  # 空字符串让 SDK 使用默认值
                end_time='',
                count=count or 100,
                dividend_type=dividend_type,
                fill_data=True
            )

            # 处理返回数据
            if data:
                for xt_symbol, df in data.items():
                    if df is not None and not df.empty:
                        # 标准化
                        df_normalized = self._normalize_kline_df(df, 'xtquant')

                        # 映射回原始代码
                        original_symbol = symbols[xt_symbols.index(xt_symbol)]
                        result[original_symbol] = df_normalized

        except Exception as e:
            logger.error(f"XtQuant 获取K线失败: {e}")

        return result

    def get_quote(self, symbols: List[str]) -> Dict[str, dict]:
        """获取实时行情"""
        if not self._ensure_xtdata():
            return {}

        result = {}
        xt_symbols = [self._to_xt_symbol(s) for s in symbols]

        try:
            # 获取行情
            data = xtdata.get_full_tick(xt_symbols)

            if data:
                for xt_symbol, quote in data.items():
                    if quote:
                        original_symbol = symbols[xt_symbols.index(xt_symbol)]
                        result[original_symbol] = self._normalize_quote_dict(original_symbol, quote, 'xtquant')

        except Exception as e:
            logger.error(f"XtQuant 获取行情失败: {e}")

        return result

    def subscribe(
        self,
        symbols: List[str],
        callback: Callable,
        period: str = '1m'
    ) -> bool:
        """订阅实时推送"""
        if not self._ensure_xtdata():
            return False

        try:
            xt_symbols = [self._to_xt_symbol(s) for s in symbols]
            xt_period = self._to_xt_period(period)

            # 调用 xtdata 订阅
            result = xtdata.subscribe_quote(xt_symbols, period=xt_period)

            if result:
                # 记录订阅
                for symbol in symbols:
                    self._subscriptions[symbol] = callback
                return True

        except Exception as e:
            logger.error(f"XtQuant 订阅失败: {e}")

        return False

    def unsubscribe(self, symbols: List[str]) -> bool:
        """取消订阅"""
        try:
            # XtQuant 没有直接取消订阅的 API
            # 移除本地记录
            for symbol in symbols:
                self._subscriptions.pop(symbol, None)
            return True
        except Exception:
            return False

    def get_subscription_stats(self) -> dict:
        """获取订阅统计"""
        return {
            "subscribed_count": len(self._subscriptions),
            "subscribed_symbols": list(self._subscriptions.keys())
        }

    def get_stock_name(self, code: str) -> Optional[str]:
        """获取股票名称"""
        if not self._ensure_xtdata():
            return None

        try:
            xt_symbol = self._to_xt_symbol(code)
            # get_instrument_detail 返回详情字典
            detail = xtdata.get_instrument_detail(xt_symbol)
            if detail:
                return detail.get('InstrumentName')
        except Exception:
            pass

        return None

    def is_available(self) -> bool:
        """检查适配器是否可用"""
        return XTQUANT_AVAILABLE


def create_xtquant_adapter() -> V5XtQuantAdapter:
    """工厂函数：创建 XtQuant 适配器"""
    return V5XtQuantAdapter()

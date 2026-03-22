# -*- coding: utf-8 -*-
"""
V5 XtQuant 适配器

直接调用 xtquant.xtdata SDK，不依赖 V4 适配器
简化为单实例模式
"""

import threading
import time
from datetime import datetime, timedelta
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
    """V5 XtQuant 适配器 - 三层加载策略

    基于《K线数据获取完整设计文档_v2.0-XtQuant优化版》实现：
    1. 本地读取（6-8ms）- 已下载的历史数据
    2. 在线获取（760ms首次，6-8ms后续）- count方式
    3. 后台下载 - download_history_data 完整历史
    """

    def __init__(self):
        super().__init__()
        self._name = 'xtquant'
        self._subscriptions: Dict[str, Callable] = {}
        # 记录已下载的股票+周期，避免重复下载
        self._download_cache: Dict[str, bool] = {}

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

    def _get_cache_key(self, symbol: str, period: str) -> str:
        """生成缓存键"""
        return f"{symbol}_{period}"

    def get_kline(
        self,
        symbols: List[str],
        period: str = '1d',
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        count: Optional[int] = None,
        adjust_type: str = 'none'
    ) -> Dict[str, pd.DataFrame]:
        """获取 K线数据 - 三层加载策略

        策略：
        1. 本地读取（如果提供了时间范围且本地有数据）
        2. 在线获取（count方式，首次约760ms）
        3. 触发后台下载完整历史

        注意：始终返回不复权原始数据
        """
        if not self._ensure_xtdata():
            return {}

        result = {}
        xt_period = self._to_xt_period(period)
        dividend_type = 'none'
        field_list = ['time', 'open', 'high', 'low', 'close', 'volume', 'amount']

        for symbol in symbols:
            try:
                df = self._get_kline_three_layer(
                    symbol, xt_period, field_list,
                    start_date, end_date, count, dividend_type
                )
                if df is not None and not df.empty:
                    result[symbol] = df
            except Exception as e:
                logger.warning(f"获取 {symbol} {period} K线失败: {e}")

        return result

    def _get_kline_three_layer(
        self,
        symbol: str,
        xt_period: str,
        field_list: List[str],
        start_date: Optional[str],
        end_date: Optional[str],
        count: Optional[int],
        dividend_type: str
    ) -> Optional[pd.DataFrame]:
        """三层加载策略实现"""
        xt_symbol = self._to_xt_symbol(symbol)

        # 策略1: 本地读取（如果提供了时间范围）
        if start_date and end_date:
            df = self._read_local_data(
                xt_symbol, xt_period, field_list,
                start_date, end_date, dividend_type
            )
            if df is not None and not df.empty:
                logger.debug(f"[本地读取] {symbol} {xt_period} {len(df)}条")
                return df

        # 策略2: 在线获取（count方式）
        fetch_count = count or 100
        df = self._fetch_online_data(
            symbol, xt_symbol, xt_period, field_list,
            fetch_count, dividend_type
        )
        if df is not None and not df.empty:
            # 策略3: 触发后台下载（如果本地没有）
            cache_key = self._get_cache_key(symbol, xt_period)
            if cache_key not in self._download_cache:
                self._download_in_background(symbol, xt_period)
            return df

        return None

    def _read_local_data(
        self,
        xt_symbol: str,
        xt_period: str,
        field_list: List[str],
        start_date: str,
        end_date: str,
        dividend_type: str
    ) -> Optional[pd.DataFrame]:
        """第一层：本地读取（count=0 表示使用时间范围）"""
        try:
            data = xtdata.get_market_data_ex(
                field_list=field_list,
                stock_list=[xt_symbol],
                period=xt_period,
                start_time=start_date,
                end_time=end_date,
                count=0,
                dividend_type=dividend_type
            )
            if data and xt_symbol in data:
                df = data[xt_symbol]
                if df is not None and not df.empty:
                    return self._normalize_kline_df(df, 'xtquant_local')
        except Exception as e:
            logger.debug(f"[本地读取] {xt_symbol} {xt_period} 失败: {e}")
        return None

    def _fetch_online_data(
        self,
        symbol: str,
        xt_symbol: str,
        xt_period: str,
        field_list: List[str],
        count: int,
        dividend_type: str
    ) -> Optional[pd.DataFrame]:
        """第二层：在线获取（count方式）"""
        try:
            start = time.time()
            data = xtdata.get_market_data_ex(
                field_list=field_list,
                stock_list=[xt_symbol],
                period=xt_period,
                start_time='',
                end_time='',
                count=count,
                dividend_type=dividend_type,
                fill_data=True
            )
            elapsed = (time.time() - start) * 1000

            if data and xt_symbol in data:
                df = data[xt_symbol]
                if df is not None and not df.empty:
                    logger.info(
                        f"[在线获取] {symbol} {xt_period} "
                        f"{len(df)}条, 耗时:{elapsed:.1f}ms"
                    )
                    return self._normalize_kline_df(df, 'xtquant_online')
        except Exception as e:
            logger.warning(f"[在线获取] {symbol} {xt_period} 失败: {e}")
        return None

    def _download_in_background(self, symbol: str, xt_period: str):
        """第三层：后台下载完整历史数据"""
        def download_task():
            try:
                end_date = datetime.now()
                # 根据周期决定下载范围
                if xt_period == '1d':
                    start_date = end_date - timedelta(days=730)
                elif xt_period in ['5m', '15m']:
                    start_date = end_date - timedelta(days=60)
                elif xt_period in ['30m', '60m']:
                    start_date = end_date - timedelta(days=90)
                else:
                    start_date = end_date - timedelta(days=180)

                start_str = start_date.strftime('%Y%m%d')
                end_str = end_date.strftime('%Y%m%d')

                xt_symbol = self._to_xt_symbol(symbol)
                logger.info(
                    f"[后台下载] 开始: {symbol} {xt_period} "
                    f"{start_str}~{end_str}"
                )

                xtdata.download_history_data(
                    stock_code=xt_symbol,
                    period=xt_period,
                    start_time=start_str,
                    end_time=end_str
                )

                self._download_cache[self._get_cache_key(symbol, xt_period)] = True
                logger.info(f"[后台下载] 完成: {symbol} {xt_period}")

            except Exception as e:
                logger.error(f"[后台下载] {symbol} {xt_period} 失败: {e}")

        # 启动后台线程
        thread = threading.Thread(target=download_task, daemon=True)
        thread.start()

    def preload_kline_data(
        self,
        symbols: List[str],
        periods: List[str] = None
    ) -> Dict:
        """预下载K线数据（应用启动时调用）

        Args:
            symbols: 股票代码列表
            periods: 周期列表，默认 ['1d', '5m', '30m', '60m']

        Returns:
            {'status': 'running', 'symbols': [], 'periods': []}
        """
        if not self._ensure_xtdata():
            return {'status': 'error', 'message': 'xtquant not available'}

        periods = periods or ['1d', '5m', '30m', '60m']
        xt_periods = [self._to_xt_period(p) for p in periods]

        def preload_task():
            for symbol in symbols:
                for xt_period in xt_periods:
                    self._download_in_background(symbol, xt_period)
                    time.sleep(0.1)

        thread = threading.Thread(target=preload_task, daemon=True)
        thread.start()

        return {
            'status': 'running',
            'symbols': symbols,
            'periods': periods,
            'message': '预下载任务已启动（后台执行）'
        }

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
                        result[original_symbol] = self._normalize_quote_dict(
                            original_symbol, quote, 'xtquant'
                        )

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

    def _normalize_kline_df(self, df: pd.DataFrame, source: str) -> pd.DataFrame:
        """标准化 K线 DataFrame

        XtQuant 返回的已经是手/元，与通达信本地格式一致，无需转换
        """
        if df is None or df.empty:
            return df

        # 添加数据源标记
        df['data_source'] = source

        return df

    def _normalize_quote_dict(self, code: str, quote: dict, source: str) -> dict:
        """标准化行情数据

        XtQuant 返回的已经是手/元，与通达信本地格式一致，无需转换
        """
        # 直接调用基类方法（已经是手/元）
        return super()._normalize_quote_dict(code, quote, source)

    def is_available(self) -> bool:
        """检查适配器是否可用"""
        return XTQUANT_AVAILABLE


def create_xtquant_adapter() -> V5XtQuantAdapter:
    """工厂函数：创建 XtQuant 适配器"""
    return V5XtQuantAdapter()

# -*- coding: utf-8 -*-
"""
V5 XtQuant 适配器

直接调用 xtquant.xtdata SDK，不依赖 V4 适配器
简化为单实例模式
"""

import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable, Set

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
        # 观察列表：需要实时订阅的股票
        self._watchlist: Set[str] = set()
        # 观察列表默认周期（分钟线）
        self._watchlist_periods = ['1m', '5m', '15m', '30m']
        # XtQuant本地只支持下载5m和1d，其他周期通过订阅实时获取或从5m聚合
        self._downloadable_periods = {'5m', '1d'}  # 可下载到本地的周期集合
        self._subscribe_periods = ['1m', '5m', '15m', '30m']  # 需要订阅的周期

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
            logger.info(f"[XtQuant] 尝试本地读取: {symbol} {xt_period}, 日期范围: {start_date} ~ {end_date}")
            df = self._read_local_data(
                xt_symbol, xt_period, field_list,
                start_date, end_date, dividend_type
            )
            if df is not None and not df.empty:
                logger.info(f"[XtQuant] 本地读取成功: {symbol} {xt_period} {len(df)}条")
                return df
            else:
                logger.info(f"[XtQuant] 本地读取无数据，尝试在线获取")

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
        """第二层：在线获取（count方式）

        改进：如果本地没有数据，使用实时订阅+后台下载获取数据
        """
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

            # 如果到这里，说明本地没有数据，启动订阅+下载
            logger.info(f"[在线获取] {symbol} {xt_period} 本地无数据，启动订阅+下载...")

            # 检查是否交易时间
            from myquant.core.market.utils.trading_time import TradingTimeChecker
            is_trading = TradingTimeChecker.is_trading_time()

            # 对于分钟线，交易时间启动实时订阅，非交易时间直接下载
            if xt_period in ['1m', '5m', '15m', '30m', '60m']:
                if is_trading:
                    self._subscribe_and_download(symbol, xt_period)
                else:
                    logger.info(f"[在线获取] 非交易时间，直接下载历史数据: {symbol} {xt_period}")
                    self._sync_download_data(symbol, xt_period)
            else:
                # 日线直接同步下载
                self._sync_download_data(symbol, xt_period)

            # 等待一小段时间让数据下载完成
            time.sleep(0.5)  # 重载标记: 2026-03-25-03-47

            # 再次尝试获取
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

            if data and xt_symbol in data:
                df = data[xt_symbol]
                if df is not None and not df.empty:
                    elapsed = (time.time() - start) * 1000
                    logger.info(
                        f"[在线获取] {symbol} {xt_period} "
                        f"{len(df)}条(下载后), 总耗时:{elapsed:.1f}ms"
                    )
                    return self._normalize_kline_df(df, 'xtquant_online')

        except Exception as e:
            logger.warning(f"[在线获取] {symbol} {xt_period} 失败: {e}")
        return None

    def _subscribe_and_download(self, symbol: str, xt_period: str):
        """启动实时订阅并后台下载历史数据（用于分钟线）

        Args:
            symbol: 股票代码
            xt_period: XtQuant周期格式
        """
        try:
            xt_symbol = self._to_xt_symbol(symbol)

            # 1. 启动实时订阅（如果还没订阅）
            cache_key = self._get_cache_key(symbol, xt_period)
            if cache_key not in self._subscriptions:
                logger.info(f"[订阅+下载] 启动实时订阅: {symbol} {xt_period}")
                xtdata.subscribe_quote([xt_symbol], period=xt_period)
                self._subscriptions[cache_key] = True

            # 2. 同时后台下载历史数据
            self._download_in_background(symbol, xt_period)

        except Exception as e:
            # 订阅失败（非交易时间会失败），降级为debug日志
            logger.debug(f"[订阅+下载] {symbol} {xt_period} 失败: {e}")

    def _sync_download_data(self, symbol: str, xt_period: str) -> bool:
        """同步下载历史数据（阻塞式，用于日线等非分钟线）"""
        try:
            end_date = datetime.now()
            if xt_period == '1d':
                start_date = end_date - timedelta(days=730)
            else:
                start_date = end_date - timedelta(days=180)

            start_str = start_date.strftime('%Y%m%d')
            end_str = end_date.strftime('%Y%m%d')
            xt_symbol = self._to_xt_symbol(symbol)

            logger.info(f"[同步下载] 开始: {symbol} {xt_period} {start_str}~{end_str}")

            xtdata.download_history_data(
                stock_code=xt_symbol,
                period=xt_period,
                start_time=start_str,
                end_time=end_str
            )

            self._download_cache[self._get_cache_key(symbol, xt_period)] = True
            logger.info(f"[同步下载] 完成: {symbol} {xt_period}")
            return True

        except Exception as e:
            logger.error(f"[同步下载] {symbol} {xt_period} 失败: {e}")
            return False

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

                        # 获取额外字段（涨停跌停价、股本等）
                        self._fill_instrument_fields(result[original_symbol], xt_symbol)

        except Exception as e:
            logger.error(f"XtQuant 获取行情失败: {e}")

        return result

    def _fill_instrument_fields(self, quote: dict, xt_symbol: str) -> None:
        """从 get_instrument_detail 补充字段

        包括：
        - 涨停价
        - 跌停价
        - 总股本
        - 流通股本

        Args:
            quote: 行情数据字典（会被修改）
            xt_symbol: XtQuant 格式的股票代码
        """
        try:
            detail = xtdata.get_instrument_detail(xt_symbol)
            if detail:
                # 涨停跌停价
                quote['zt_price'] = float(detail.get('UpStopPrice', 0)) or 0
                quote['dt_price'] = float(detail.get('DownStopPrice', 0)) or 0

                # 总股本和流通股本（转换为万股）
                total_volume = detail.get('TotalVolume', 0) or 0
                float_volume = detail.get('FloatVolume', 0) or 0
                quote['total_shares'] = float(total_volume) if total_volume else 0
                quote['float_shares'] = float(float_volume) if float_volume else 0

                logger.debug(f"{xt_symbol} 获取到 instrument detail: zt_price={quote['zt_price']}, dt_price={quote['dt_price']}")
        except Exception as e:
            logger.debug(f"{xt_symbol} 获取 instrument detail 失败: {e}")

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

        XtQuant 特殊处理：time 列（时间戳）需要转换为 datetime 列（与其他适配器保持一致）
        """
        if df is None or df.empty:
            return df

        # XtQuant 返回的 index 是日期字符串（如 '20260403'），time 列是时间戳
        if 'datetime' not in df.columns:
            # 检查是否有 time 列（时间戳，毫秒）
            if 'time' in df.columns:
                # XtQuant 的 time 列直接转换为 datetime（已是北京时间）
                df['datetime'] = pd.to_datetime(df['time'], unit='ms', errors='coerce')
                df = df.drop(columns=['time'])
            elif isinstance(df.index, pd.Index) and len(df.index) > 0:
                # 降级：使用 index（仅适用于日线数据）
                first_idx = str(df.index[0])
                if first_idx.isdigit() and len(first_idx) == 8:
                    df['datetime'] = pd.to_datetime(df.index, format='%Y%m%d')

        # 添加数据源标记
        df['data_source'] = source

        return df

    def _normalize_quote_dict(self, code: str, quote: dict, source: str) -> dict:
        """标准化行情数据 - XtQuant特有字段映射

        XtQuant 返回的已经是手/元，与通达信本地格式一致，无需转换
        XtQuant 特有字段：
        - tickvol: 现手（当前tick成交量）
        - pvolume: 原始成交总量
        - stockStatus: 证券状态
        """
        # 先调用基类方法处理基础字段
        result = super()._normalize_quote_dict(code, quote, source)

        # XtQuant特有字段映射
        result.update({
            'cur_vol': quote.get('tickvol', 0),  # 现手
            # 其他扩展字段 XtQuant 不直接提供，填0
            'inner_vol': 0,  # 内盘（不支持）
            'outer_vol': 0,  # 外盘（不支持）
            'turnover_rate': 0,  # 换手率（需财务接口）
            'volume_ratio': 0,   # 量比（不支持）
            'amplitude': 0,      # 振幅（需计算）
            'pe_ratio': 0,       # 市盈率（不支持）
            'pb_ratio': 0,       # 市净率（不支持）
            'dy_ratio': 0,       # 股息率（不支持）
            'zt_price': 0,       # 涨停价（不支持）
            'dt_price': 0,       # 跌停价（不支持）
            'beta': 0,           # 贝塔系数（不支持）
            'his_high': 0,       # 历史最高（不支持）
            'his_low': 0,        # 历史最低（不支持）
            'total_shares': 0,   # 总股本（不支持）
        })

        # 盘口数据处理 - XtQuant 返回的是数组格式
        # 买盘：bidPrice(价格数组), bidVol(数量数组)
        # 卖盘：askPrice(价格数组), askVol(数量数组)
        self._parse_order_book(result, quote)

        return result

    def _parse_order_book(self, result: dict, quote: dict) -> None:
        """解析盘口数据（买卖5档）

        XtQuant get_full_tick 返回的盘口字段：
        - bidPrice: [买1价, 买2价, 买3价, 买4价, 买5价]
        - bidVol:   [买1量, 买2量, 买3量, 买4量, 买5量]
        - askPrice: [卖1价, 卖2价, 卖3价, 卖4价, 卖5价]
        - askVol:   [卖1量, 卖2量, 卖3量, 卖4量, 卖5量]
        """
        # 买盘价格和数量
        bid_prices = quote.get('bidPrice', [])
        bid_vols = quote.get('bidVol', [])

        # 卖盘价格和数量
        ask_prices = quote.get('askPrice', [])
        ask_vols = quote.get('askVol', [])

        # 映射到标准字段（确保是数字）
        for i in range(5):
            # 买盘
            if i < len(bid_prices):
                result[f'bid{i+1}'] = float(bid_prices[i]) if bid_prices[i] else 0
            if i < len(bid_vols):
                result[f'bid_vol{i+1}'] = int(bid_vols[i]) if bid_vols[i] else 0

            # 卖盘
            if i < len(ask_prices):
                result[f'ask{i+1}'] = float(ask_prices[i]) if ask_prices[i] else 0
            if i < len(ask_vols):
                result[f'ask_vol{i+1}'] = int(ask_vols[i]) if ask_vols[i] else 0

        # 调试：打印原始盘口数据
        logger.info(f"[调试] {result.get('code')} 原始盘口: bidPrice={quote.get('bidPrice')}, bidVol={quote.get('bidVol')}, askPrice={quote.get('askPrice')}, askVol={quote.get('askVol')}")

    def get_extra_indicators(self, code: str) -> dict:
        """获取额外指标（换手率、市盈率等）

        XtQuant 提供:
        - get_instrument_detail: 涨跌停价、股本
        - get_stock_info: 股票基本信息（可能不存在）

        Args:
            code: 股票代码（600519.SH 格式）

        Returns:
            包含额外指标的字典
        """
        try:
            xt_symbol = self._to_xt_symbol(code)
            result = {}

            # 尝试从 get_instrument_detail 获取数据（更稳定）
            if hasattr(xtdata, 'get_instrument_detail'):
                detail = xtdata.get_instrument_detail(xt_symbol)
                if detail:
                    logger.debug(f"{code} get_instrument_detail 返回: {list(detail.keys())[:10]}")
                    # 提取可用字段
                    if isinstance(detail, dict):
                        for key, val in detail.items():
                            if isinstance(val, (int, float)) and val > 0:
                                key_lower = key.lower()
                                if 'turnover' in key_lower or '换手' in str(key):
                                    result['turnover_rate'] = float(val)
                                elif 'pe' in key_lower or '市盈' in str(key):
                                    result['pe_ratio'] = float(val)
                                elif 'pb' in key_lower or '市净' in str(key):
                                    result['pb_ratio'] = float(val)

            # 尝试从 get_stock_info 获取（如果存在）
            if hasattr(xtdata, 'get_stock_info'):
                info = xtdata.get_stock_info(xt_symbol)
                if info:
                    logger.debug(f"{code} get_stock_info 返回字段: {list(info.keys())[:10]}")
                    if isinstance(info, dict):
                        for key, val in info.items():
                            if isinstance(val, (int, float)) and val > 0:
                                key_lower = key.lower()
                                if 'turnover' in key_lower or '换手' in str(key):
                                    result['turnover_rate'] = float(val)
                                elif 'pe' in key_lower or '市盈' in str(key):
                                    result['pe_ratio'] = float(val)
                                elif 'amplitude' in key_lower or '振幅' in str(key):
                                    result['amplitude'] = float(val)

            logger.debug(f"{code} 最终额外指标: {result}")
            return result

        except Exception as e:
            logger.info(f"{code} 获取额外指标失败: {e}")
            return {}

    def is_available(self) -> bool:
        """检查适配器是否可用"""
        return XTQUANT_AVAILABLE

    def add_to_watchlist(self, symbols: List[str]) -> Dict:
        """添加股票到观察列表并自动订阅分钟线

        这是实时行情系统的核心功能：
        - 将股票加入观察列表
        - 自动订阅分钟线（1m/5m/15m/30m）
        - 非交易时间会自动降级到历史数据

        Args:
            symbols: 股票代码列表，如 ['000858.SZ', '600519.SH']

        Returns:
            {
                'added': [],      # 成功添加的股票
                'subscribed': [], # 成功订阅的(symbol, period)列表
                'failed': []      # 失败的列表
            }
        """
        if not self._ensure_xtdata():
            return {'added': [], 'subscribed': [], 'failed': []}

        result = {'added': [], 'subscribed': [], 'failed': []}

        for symbol in symbols:
            try:
                # 1. 添加到观察列表
                if symbol not in self._watchlist:
                    self._watchlist.add(symbol)
                    result['added'].append(symbol)
                    logger.info(f"[观察列表] 添加: {symbol}")

                # 2. 自动订阅分钟线（交易时间有效，非交易时间订阅会静默失败）
                xt_symbol = self._to_xt_symbol(symbol)
                subscribe_success = False
                for period in self._watchlist_periods:
                    try:
                        cache_key = self._get_cache_key(symbol, period)
                        if cache_key not in self._subscriptions:
                            xtdata.subscribe_quote([xt_symbol], period=period)
                            self._subscriptions[cache_key] = True
                            result['subscribed'].append((symbol, period))
                            logger.info(f"[观察列表] 订阅: {symbol} {period}")
                            subscribe_success = True
                    except Exception as e:
                        # 订阅失败（非交易时间会失败）
                        logger.debug(f"[观察列表] 订阅失败: {symbol} {period} - {e}")

                # 3. 数据确保策略（先检查本地是否已有）
                for period in self._watchlist_periods:
                    cache_key = self._get_cache_key(symbol, period)
                    if cache_key in self._download_cache:
                        continue  # 已下载过，跳过

                    # 检查本地是否已有数据
                    try:
                        test_data = xtdata.get_market_data_ex(
                            field_list=['time'],  # 最少字段，快速检查
                            stock_list=[xt_symbol],
                            period=period,
                            start_time='',
                            end_time='',
                            count=1
                        )
                        if test_data and xt_symbol in test_data and not test_data[xt_symbol].empty:
                            # 本地已有数据，标记缓存
                            self._download_cache[cache_key] = True
                            logger.debug(f"[观察列表] 本地已有数据: {symbol} {period}")
                            continue
                    except Exception:
                        pass

                    # 本地没有数据，需要下载
                    if subscribe_success:
                        # 交易时间：后台下载
                        self._download_in_background(symbol, period)
                    else:
                        # 非交易时间：同步下载
                        logger.info(f"[观察列表] 同步下载: {symbol} {period}")
                        self._sync_download_data(symbol, period)

            except Exception as e:
                logger.error(f"[观察列表] 添加 {symbol} 失败: {e}")
                result['failed'].append((symbol, str(e)))

        return result

    def remove_from_watchlist(self, symbols: List[str]) -> Dict:
        """从观察列表移除股票

        Args:
            symbols: 股票代码列表

        Returns:
            {'removed': [], 'unsubscribed': []}
        """
        result = {'removed': [], 'unsubscribed': []}

        for symbol in symbols:
            try:
                if symbol in self._watchlist:
                    self._watchlist.discard(symbol)
                    result['removed'].append(symbol)

                # 取消订阅
                for period in self._watchlist_periods:
                    cache_key = self._get_cache_key(symbol, period)
                    if cache_key in self._subscriptions:
                        del self._subscriptions[cache_key]
                        # XtQuant没有真正的unsubscribe，这里只是移除本地记录
                        result['unsubscribed'].append((symbol, period))

            except Exception as e:
                logger.error(f"[观察列表] 移除 {symbol} 失败: {e}")

        return result

    def get_watchlist(self) -> Dict:
        """获取观察列表状态

        Returns:
            {
                'watchlist': [],      # 观察列表股票
                'subscriptions': [],  # 当前订阅列表
                'is_trading_time': bool  # 是否交易时间
            }
        """
        from myquant.core.market.utils.trading_time import TradingTimeChecker

        return {
            'watchlist': list(self._watchlist),
            'subscriptions': [
                {'symbol': k.split('_')[0], 'period': k.split('_')[1]}
                for k in self._subscriptions.keys()
            ],
            'is_trading_time': TradingTimeChecker.is_trading_time()
        }

    def ensure_watchlist_data(self) -> Dict:
        """确保观察列表所有股票都有数据

        在非交易时间调用，用于预加载数据
        交易时间内订阅会自动更新数据，不需要手动调用

        Returns:
            {'downloaded': [], 'failed': []}
        """
        result = {'downloaded': [], 'failed': []}

        for symbol in self._watchlist:
            for period in self._watchlist_periods:
                try:
                    cache_key = self._get_cache_key(symbol, period)
                    if cache_key not in self._download_cache:
                        # 检查本地是否有数据
                        xt_symbol = self._to_xt_symbol(symbol)
                        data = xtdata.get_market_data_ex(
                            field_list=['time', 'open', 'high', 'low', 'close', 'volume', 'amount'],
                            stock_list=[xt_symbol],
                            period=period,
                            start_time='',
                            end_time='',
                            count=10
                        )

                        if not data or xt_symbol not in data or data[xt_symbol].empty:
                            # 没有数据，触发下载
                            self._sync_download_data(symbol, period)
                            result['downloaded'].append((symbol, period))
                        else:
                            self._download_cache[cache_key] = True

                except Exception as e:
                    result['failed'].append((symbol, period, str(e)))

        return result


def create_xtquant_adapter() -> V5XtQuantAdapter:
    """工厂函数：创建 XtQuant 适配器"""
    return V5XtQuantAdapter()

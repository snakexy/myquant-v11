# -*- coding: utf-8 -*-
"""
V5 PyTdx 适配器

支持两种模式:
1. 远程行情模式 (TdxHq_API) - 连接远程服务器获取在线数据（主模式）
2. 本地文件模式 (TdxDailyBarReader) - 读通达信 .day 文件（远程失败时的fallback）

日线K线优先在线获取，失败时回退本地文件。实时行情只能在线获取。

注意：此适配器始终返回不复权原始数据，复权由服务层统一处理。
"""

from typing import Dict, List, Optional
from loguru import logger
import pandas as pd
import socket
from pathlib import Path

# 设置 socket 超时，避免远程请求无限挂起
_SOCKET_TIMEOUT = 10

try:
    from pytdx2.hq import TdxHq_API
    PYTDX_AVAILABLE = True
except ImportError:
    PYTDX_AVAILABLE = False
    logger.error("pytdx2 未安装，请运行: pip install pytdx2")

try:
    from pytdx2.reader.daily_bar_reader import TdxDailyBarReader
    from pytdx2.reader.min_bar_reader import TdxLCMinBarReader
    LOCAL_READER_AVAILABLE = True
    MIN_READER_AVAILABLE = True
except ImportError:
    LOCAL_READER_AVAILABLE = False
    MIN_READER_AVAILABLE = False

from .base import V5DataAdapter
from ..utils.data_merger import DataMerger

# 通达信本地数据目录
TDX_VIPDOC_PATH = Path("E:/new_tdx64/vipdoc")


def _get_last_trade_date() -> str:
    """获取最后一个交易日（简化版，实际应该根据交易日历）"""
    from datetime import datetime, timedelta
    now = datetime.now()
    # 简单处理：如果今天不是周末，今天就是最后交易日
    # 如果今天是周日，周五是最后交易日；周六，周五是最后交易日
    weekday = now.weekday()
    if weekday == 5:  # 周六
        last_date = now - timedelta(days=1)
    elif weekday == 6:  # 周日
        last_date = now - timedelta(days=2)
    else:
        last_date = now
    return last_date.strftime('%Y%m%d')


class V5PyTdxAdapter(V5DataAdapter):
    """V5 PyTdx 适配器

    直接调用 pytdx2 SDK，获取通达信数据

    配置：
        use_local_fallback: 是否使用本地文件回退（默认 False，强制使用在线数据）
    """

    # PyTdx 周期码定义
    # 0: 5分钟, 1: 15分钟, 2: 30分钟, 3: 60分钟
    # 4: 日线(备用), 5: 周线, 6: 月线
    # 7: 1分钟(备用), 8: 1分钟, 9: 日线
    PERIOD_CATEGORY = {
        '5min': 0,
        '15min': 1,
        '30min': 2,
        '60min': 3,
        '1h': 3,
        'day': 9,
        '1d': 9,
        'week': 5,
        '1w': 5,
        'month': 6,
        '1M': 6,
        '1mon': 6,
        '1min': 8,
        '1m': 8,
    }

    def __init__(self, use_local_fallback: bool = False):
        super().__init__()
        self._name = 'pytdx'
        self._api: Optional[TdxHq_API] = None
        self._connected = False
        self._local_reader = TdxDailyBarReader() if LOCAL_READER_AVAILABLE else None
        self._min_reader = TdxLCMinBarReader() if MIN_READER_AVAILABLE else None
        self._last_used = 0  # 上次使用时间戳
        self._use_local_fallback = use_local_fallback  # 是否使用本地文件回退

        # 服务器列表（从 pytdx2_config 复制）
        self._server_list = [
            ("180.153.18.172", 80),
            ("202.108.253.139", 80),
            ("60.12.136.250", 7709),
            ("114.80.63.12", 7709),
            ("114.80.63.35", 7709),
            ("218.6.170.47", 7709),
            ("123.125.108.14", 7709),
        ]
        self._current_server_index = 0

    def _symbol_to_tdx_filename(self, symbol: str) -> Optional[str]:
        """将 symbol (600000.SH) 转换为通达信文件名 (sh600000.day)"""
        code = symbol.replace('.SH', '').replace('.SZ', '').replace('.BJ', '')
        if not code:
            return None

        if code[0] in ('6', '5', '9'):
            prefix = 'sh'
        elif code[0] == '4' or code[0] == '8':
            prefix = 'bj'
        else:
            prefix = 'sz'

        return f"{prefix}{code}.day"

    def _get_kline_from_local(self, symbol: str, count: Optional[int] = None) -> Optional[pd.DataFrame]:
        """从本地 .day 文件读取日线K线

        文件路径: E:/new_tdx64/vipdoc/{sh|sz}/lday/{prefix}{code}.day
        """
        if not self._local_reader:
            return None

        tdx_filename = self._symbol_to_tdx_filename(symbol)
        if not tdx_filename:
            return None

        code = symbol.replace('.SH', '').replace('.SZ', '').replace('.BJ', '')
        prefix = 'sh' if code[0] in ('6', '5', '9') else 'sz'

        day_file = TDX_VIPDOC_PATH / prefix / "lday" / tdx_filename
        if not day_file.exists():
            return None

        try:
            df = self._local_reader.get_df(str(day_file))
            if df is None or df.empty:
                return None

            # 确保 datetime 列存在
            if 'date' in df.index.name or df.index.name == 'date':
                df = df.reset_index()
            if 'datetime' not in df.columns and 'date' in df.columns:
                df = df.rename(columns={'date': 'datetime'})

            # 限制条数
            if count and len(df) > count:
                df = df.tail(count)

            return df
        except Exception as e:
            logger.debug(f"读取本地文件 {day_file} 失败: {e}")
            return None

    def _get_minline_from_local(
        self, symbol: str, period: str = '5min',
        count: Optional[int] = None
    ) -> Optional[pd.DataFrame]:
        """从本地分钟线文件读取数据

        文件路径: E:/new_tdx64/vipdoc/{sh|sz}/fzline/{prefix}{code}.lc5
        支持格式: .lc5 (5分钟), .lc1 (1分钟) - TdxLCMinBarReader
        """
        if not self._min_reader:
            return None

        code = symbol.replace('.SH', '').replace('.SZ', '').replace('.BJ', '')
        prefix = 'sh' if code[0] in ('6', '5', '9') else 'sz'

        # 确定文件后缀
        if period in ('1min', '1m'):
            suffix = '.lc1'
        else:  # 默认5分钟
            suffix = '.lc5'

        min_file = TDX_VIPDOC_PATH / prefix / "fzline" / f"{prefix}{code}{suffix}"
        if not min_file.exists():
            return None

        try:
            df = self._min_reader.get_df(str(min_file))
            if df is None or df.empty:
                return None

            # 确保 datetime 列存在
            if 'date' in df.index.name or df.index.name == 'date':
                df = df.reset_index()
            if 'datetime' not in df.columns and 'date' in df.columns:
                df = df.rename(columns={'date': 'datetime'})

            # 限制条数
            if count and len(df) > count:
                df = df.tail(count)

            return df
        except Exception as e:
            logger.debug(f"读取本地分钟线 {min_file} 失败: {e}")
            return None

    # 连接空闲超过此时间后，下次使用时先断开再重连
    _IDLE_TIMEOUT = 120  # 2分钟

    def _ensure_connected(self) -> bool:
        """确保已连接远程服务器

        自动重连策略：
        - 已连接且最近使用过 → 复用连接
        - 已连接但超过空闲时间 → 断开重连（服务器可能已关闭连接）
        - 未连接 → 新建连接
        - 连接失败 → 切换下一个服务器
        """
        if not PYTDX_AVAILABLE:
            return False

        import time
        now = time.time()

        if self._connected and self._api:
            # 检查是否空闲超时，超时则断开重连
            if now - self._last_used > self._IDLE_TIMEOUT:
                logger.debug(f"连接空闲 {now - self._last_used:.0f}s，重新连接")
                self._disconnect()
                return self._connect()
            self._last_used = now
            return True

        # 尝试连接
        if self._connect():
            self._last_used = now
            return True
        return False

    def _disconnect(self):
        """断开连接"""
        try:
            if self._api:
                self._api.disconnect()
        except Exception:
            pass
        self._connected = False

    def _connect(self) -> bool:
        """连接远程服务器"""
        if not PYTDX_AVAILABLE:
            logger.error("pytdx2 不可用")
            return False

        # 设置超时，防止连接挂起
        old_timeout = socket.getdefaulttimeout()
        socket.setdefaulttimeout(_SOCKET_TIMEOUT)

        # 尝试连接服务器列表
        for host, port in self._server_list:
            try:
                if not self._api:
                    # 启用心跳包保持连接，30秒间隔（平衡保活性能和资源）
                    self._api = TdxHq_API(heartbeat=True, auto_retry=True)

                logger.debug(f"PyTdx 尝试连接: {host}:{port}")

                if self._api.connect(host, port):
                    # 强制设置 socket 超时（heartbeat 线程可能重置）
                    socket.setdefaulttimeout(_SOCKET_TIMEOUT)

                    # PyTdx2 需要调用 setup
                    try:
                        self._api.setup()
                    except Exception:
                        pass  # setup 失败不是致命错误

                    self._connected = True
                    logger.info(f"PyTdx 连接成功: {host}:{port}")
                    return True

            except Exception as e:
                logger.debug(f"PyTdx 连接失败 {host}:{port}: {e}")
                continue

        socket.setdefaulttimeout(old_timeout)
        logger.error("PyTdx 所有服务器连接失败")
        return False

    def _get_market(self, symbol: str) -> int:
        """获取市场代码：优先使用后缀，避免指数代码被误判

        .SH -> 上海 (1)，.SZ/.BJ -> 深圳 (0)
        无后缀时按代码前缀推断：6/5/9 -> 上海，88 -> 通达信特有指数 (31)
        """
        if '.SH' in symbol:
            return 1
        if '.SZ' in symbol or '.BJ' in symbol:
            return 0
        code = symbol.replace('.SH', '').replace('.SZ', '').replace('.BJ', '')
        if code.startswith('88'):
            return 31  # 通达信特有指数 (如 880005)
        elif code[0] in ('6', '5', '9'):
            return 1  # 上海
        else:
            return 0  # 深圳

    def _to_category(self, period: str) -> int:
        """转换周期到 PyTdx category"""
        return self.PERIOD_CATEGORY.get(period, 9)  # 默认日线

    def get_xdxr_info(self, symbol: str) -> List[dict]:
        """获取除权除息信息（供服务层复权计算使用）

        Args:
            symbol: 股票代码 (如 600000.SH)

        Returns:
            除权除息记录列表
        """
        if not self._ensure_connected():
            return []

        try:
            market = self._get_market(symbol)
            code = symbol.replace('.SH', '').replace('.SZ', '').replace('.BJ', '')

            xdxr_data = self._api.get_xdxr_info(market, code)

            if xdxr_data:
                logger.debug(f"[PyTdx] {symbol} 获取到 {len(xdxr_data)} 条除权记录")
            else:
                logger.debug(f"[PyTdx] {symbol} 无除权记录")

            return xdxr_data or []

        except Exception as e:
            logger.warning(f"[PyTdx] 获取 {symbol} 除权信息失败: {e}")
            return []

    def _get_kline_smart(
        self,
        symbol: str,
        period: str = '1d',
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        count: Optional[int] = None
    ) -> Optional[pd.DataFrame]:
        """智能获取K线：本地+在线无缝补齐"""
        is_daily = period in ('1d', '1D', 'day')
        is_minute = period in ('1min', '1m', '5min', '5m', '15min', '30min', '60min')

        # 1. 尝试读取本地数据
        local_df = None
        if is_daily and self._local_reader:
            local_df = self._get_kline_from_local(symbol, count)
        elif is_minute and self._min_reader:
            local_df = self._get_minline_from_local(symbol, period, count)

        # 1. 尝试读取本地数据
        local_df = None
        if self._local_reader:
            local_df = self._get_kline_from_local(symbol, count)

        if local_df is None or local_df.empty:
            # 本地没有，直接在线获取
            return self._get_kline_online(symbol, period, start_date, end_date, count)

        # 2. 检查本地数据新鲜度
        info = DataMerger.check_data_freshness(local_df)

        # 3. 如果本地数据已经是最新的，直接返回
        if info.is_fresh:
            logger.debug(f"{symbol} 本地数据已最新({info.last_date})，直接返回")
            return DataMerger.limit_count(local_df, count) if count else local_df

        # 4. 本地数据过时，需要在线补齐
        logger.info(f"{symbol} 本地({info.last_date})需要补齐到最新")

        if not self._ensure_connected():
            logger.warning(f"无法连接服务器，{symbol} 返回本地数据（可能不完整）")
            return local_df

        # 在线获取缺失部分
        online_start = info.last_date if info.last_date else start_date
        online_df = self._get_kline_online(symbol, period, online_start, end_date, count)

        if online_df is None or online_df.empty:
            return local_df

        # 5. 使用 DataMerger 合并数据
        combined = DataMerger.merge_kline_data(local_df, online_df)
        combined = DataMerger.filter_by_date(combined, start_date, end_date)
        combined = DataMerger.limit_count(combined, count) if count else combined

        if combined is not None:
            logger.info(f"{symbol} 合并: 本地{len(local_df)} + 在线{len(online_df)} = {len(combined)}")
        return combined

    def _get_kline_online(
        self,
        symbol: str,
        period: str = '1d',
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        count: Optional[int] = None
    ) -> Optional[pd.DataFrame]:
        """从在线获取K线"""
        if not self._ensure_connected():
            return None

        socket.setdefaulttimeout(_SOCKET_TIMEOUT)
        category = self._to_category(period)

        try:
            market = self._get_market(symbol)
            code = symbol.replace('.SH', '').replace('.SZ', '').replace('.BJ', '')

            # PyTdx API有单次请求限制，最多约800条
            max_bars = 800
            request_count = min(count, max_bars) if count else max_bars
            data = self._api.get_security_bars(category, market, code, 0, request_count)

            if data and len(data) > 0:
                df = pd.DataFrame(data)

                # 分钟线 vol 是股（shares），日线 vol 是手（lots），统一÷100转为手
                is_daily = period in ('1d', '1D', 'day', 'd')
                if not is_daily and 'vol' in df.columns:
                    df['vol'] = df['vol'] / 100

                # 日期过滤
                if end_date and 'datetime' in df.columns:
                    # 统一转换为 YYYYMMDD 格式进行比较
                    df['datetime_str'] = df['datetime'].astype(str).str[:10].str.replace('-', '')
                    before_count = len(df)
                    df = df[df['datetime_str'] <= end_date]
                    after_count = len(df)
                    logger.info(f"[PyTdx] {symbol} end_date过滤: {before_count} -> {after_count} 条, 范围: {df['datetime_str'].min() if not df.empty else 'N/A'} ~ {df['datetime_str'].max() if not df.empty else 'N/A'}")
                    df = df.drop(columns=['datetime_str'])

                if start_date and 'datetime' in df.columns:
                    # 统一转换为 YYYYMMDD 格式进行比较
                    df['datetime_str'] = df['datetime'].astype(str).str[:10].str.replace('-', '')
                    before_count = len(df)
                    df = df[df['datetime_str'] >= start_date]
                    after_count = len(df)
                    logger.info(f"[PyTdx] {symbol} start_date过滤: {before_count} -> {after_count} 条, start_date={start_date}")
                    df = df.drop(columns=['datetime_str'])

                if count and len(df) > count:
                    df = df.tail(count)

                return self._normalize_kline_df(df, 'pytdx')

        except Exception as e:
            logger.warning(f"在线获取 {symbol} K线失败: {e}")
            # 尝试重连一次
            self._disconnect()
            if self._ensure_connected():
                try:
                    # PyTdx API有单次请求限制，最多约800条
                    max_bars = 800
                    request_count = min(count, max_bars) if count else max_bars
                    data = self._api.get_security_bars(category, market, code, 0, request_count)
                    if data and len(data) > 0:
                        df = pd.DataFrame(data)
                        if count and len(df) > count:
                            df = df.tail(count)
                        return self._normalize_kline_df(df, 'pytdx')
                except Exception as e2:
                    logger.warning(f"重连后仍失败 {symbol}: {e2}")

        return None

    def get_kline(
        self,
        symbols: List[str],
        period: str = '1d',
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        count: Optional[int] = None,
        adjust_type: str = 'none'
    ) -> Dict[str, pd.DataFrame]:
        """获取 K线数据（智能本地+在线补齐）

        日线数据：优先本地 + 在线补齐缺失部分（无缝合并）
        分钟数据：直接在线获取

        注意：此方法始终返回不复权原始数据
        """
        result = {}
        is_daily = period in ('1d', '1D', 'day')

        for symbol in symbols:
            try:
                if is_daily:
                    # 日线：使用智能补齐
                    df = self._get_kline_smart(symbol, period, start_date, end_date, count)
                else:
                    # 分钟线：直接在线
                    df = self._get_kline_online(symbol, period, start_date, end_date, count)

                if df is not None and not df.empty:
                    result[symbol] = df

            except Exception as e:
                logger.error(f"获取 {symbol} K线异常: {e}")
                continue

        return result

    def _normalize_quote_dict(self, code: str, quote: dict, source: str) -> dict:
        """将 pytdx 原始 quote 标准化为统一格式

        单位统一：手 / 元（通达信本地格式）
        PyTdx2 返回的已经是手/元，无需转换
        """
        return {
            'code': code,
            'price': quote.get('price', 0),
            'open': quote.get('open', 0),
            'high': quote.get('high', 0),
            'low': quote.get('low', 0),
            'close': quote.get('price', 0),
            'pre_close': quote.get('last_close', 0),
            'volume': quote.get('vol', 0),      # 手（无需转换）
            'amount': quote.get('amount', 0),   # 元（无需转换）
            'change': quote.get('price', 0) - quote.get('last_close', 0),
            'change_pct': round(
                (quote.get('price', 0) - quote.get('last_close', 0)) / quote.get('last_close', 1) * 100, 2
            ) if quote.get('last_close') else 0,
            'bid1': quote.get('bid1', 0),
            'ask1': quote.get('ask1', 0),
            'bid_vol1': quote.get('bid_vol1', 0),  # 手
            'ask_vol1': quote.get('ask_vol1', 0),  # 手
            'bid2': quote.get('bid2', 0),
            'ask2': quote.get('ask2', 0),
            'bid_vol2': quote.get('bid_vol2', 0),
            'ask_vol2': quote.get('ask_vol2', 0),
            'bid3': quote.get('bid3', 0),
            'ask3': quote.get('ask3', 0),
            'bid_vol3': quote.get('bid_vol3', 0),
            'ask_vol3': quote.get('ask_vol3', 0),
            'bid4': quote.get('bid4', 0),
            'ask4': quote.get('ask4', 0),
            'bid_vol4': quote.get('bid_vol4', 0),
            'ask_vol4': quote.get('ask_vol4', 0),
            'bid5': quote.get('bid5', 0),
            'ask5': quote.get('ask5', 0),
            'bid_vol5': quote.get('bid_vol5', 0),
            'ask_vol5': quote.get('ask_vol5', 0),
            'data_source': source,
        }

    def get_quote(self, symbols: List[str]) -> Dict[str, dict]:
        """获取实时行情（只能从远程服务器获取）"""
        if not self._ensure_connected():
            return {}

        socket.setdefaulttimeout(_SOCKET_TIMEOUT)  # 每次调用前强制设置
        result = {}

        # 构建批量查询 (market, code) 元组，保留 symbol→code 映射
        batch = []
        code_to_symbol = {}
        for symbol in symbols:
            market = self._get_market(symbol)
            code = symbol.replace('.SH', '').replace('.SZ', '').replace('.BJ', '')
            batch.append((market, code))
            code_to_symbol[code] = symbol

        try:
            # 批量获取（最大800）
            quotes = self._api.get_security_quotes(batch)

            if quotes:
                for quote in quotes:
                    code = quote.get('code')
                    if code:
                        key = code_to_symbol.get(code, code)
                        result[key] = self._normalize_quote_dict(code, quote, 'pytdx')

        except Exception as e:
            logger.error(f"获取行情失败: {e}")

        return result

    def is_available(self) -> bool:
        """检查适配器是否可用

        本地文件模式不需要网络，始终可用。
        实时行情需要远程连接。
        """
        if not PYTDX_AVAILABLE:
            return False
        # 有本地文件读取能力或能连远程都算可用
        return self._local_reader is not None or self._ensure_connected()

    def get_stock_list(self) -> List[dict]:
        """获取股票列表"""
        if not self._ensure_connected():
            return []

        result = []

        # 获取上海和深圳的股票列表
        for market in [1, 0]:  # 1=上海, 0=深圳
            try:
                stocks = self._api.get_security_list(market, 0)
                if stocks:
                    result.extend(stocks)
            except Exception as e:
                logger.warning(f"获取股票列表失败 (market={market}): {e}")

        return result

    def get_index_list(self) -> List[dict]:
        """获取指数列表"""
        if not self._ensure_connected():
            return []

        result = []

        try:
            # 上海指数
            indices = self._api.get_security_list(1, 0)
            if indices:
                result.extend([i for i in indices if i.get('code', '').startswith('99')])
        except Exception as e:
            logger.warning(f"获取上海指数失败: {e}")

        try:
            # 深圳指数
            indices = self._api.get_security_list(0, 0)
            if indices:
                result.extend([i for i in indices if i.get('code', '').startswith('99')])
        except Exception as e:
            logger.warning(f"获取深圳指数失败: {e}")

        return result

    def get_instrument_detail(self, symbol: str) -> Optional[dict]:
        """获取通达信特有指数的详细信息（如 880005 涨跌分布指数）

        这些指数使用 get_instrument_detail 接口获取实时数据。

        Args:
            symbol: 指数代码 (如 880005)

        Returns:
            指数详细信息字典，包含 bid_vol1-5 (上涨分布) 和 ask_vol1-5 (下跌分布)
        """
        if not self._ensure_connected():
            return None

        code = symbol.replace('.SH', '').replace('.SZ', '').replace('.BJ', '')

        try:
            socket.setdefaulttimeout(_SOCKET_TIMEOUT)
            data = self._api.get_instrument_detail(code)

            if data and len(data) > 0:
                result = data[0] if isinstance(data, list) else data
                logger.debug(f"获取 {symbol} 详细信息成功")
                return result
            else:
                logger.warning(f"获取 {symbol} 详细信息失败：无数据返回")
                return None

        except Exception as e:
            logger.warning(f"获取 {symbol} 详细信息失败: {e}")
            return None


def create_pytdx_adapter() -> V5PyTdxAdapter:
    """工厂函数：创建 PyTdx 适配器"""
    return V5PyTdxAdapter()

"""
无缝 K线服务

提供历史 K线 + 实时 K线的无缝拼接

统一复权架构:
- 所有数据源返回不复权原始数据
- 服务层统一应用 AdjustmentCalculator 进行复权
"""

from typing import Optional
import pandas as pd
from datetime import datetime
from loguru import logger

from myquant.core.market.models import KlineDataset
from myquant.core.market.routing import DataLevel, get_source_selector
from myquant.core.market.adapters import get_adapter
from myquant.core.market.utils.trading_time import TradingTimeChecker
from myquant.core.market.utils.adjustment_calculator import get_adjustment_calculator


class SeamlessKlineService:
    """无缝 K线服务

    合并历史数据和实时数据，提供连续的 K线序列
    """

    def __init__(self):
        self._selector = get_source_selector()
        self._adapter_cache = {}

    def get_kline(
        self,
        symbol: str,
        period: str = '1d',
        count: int = 500,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        include_realtime: bool = True,
        adjust_type: str = 'none'
    ) -> pd.DataFrame:
        """获取无缝 K线数据

        Args:
            symbol: 代码
            period: 周期 (1m/5m/15m/30m/1h/1d/1w/1M)
            count: 数据条数
            start_date: 开始日期
            end_date: 结束日期
            include_realtime: 是否包含实时数据
            adjust_type: 复权类型 (none/front/back/front_ratio/back_ratio)

        Returns:
            DataFrame with OHLCV columns
        """
        # 计算实际需要获取的数据量
        # 复权时需要获取更多历史数据来覆盖除权日（至少1000条）
        actual_count = count
        if adjust_type != 'none':
            actual_count = max(count * 10, 1000)  # 复权时获取更多数据
            logger.debug(f"[复权] 扩大数据量: {count} -> {actual_count}")

        # 获取历史数据（始终获取不复权原始数据）
        # 注意：所有适配器现在都返回不复权数据，复权由服务层统一处理
        historical = self._get_historical_kline(
            symbol, period, actual_count,
            start_date, end_date, 'none'  # 始终获取不复权数据
        )

        if historical.df.empty:
            return historical.df

        # 判断是否需要补充实时数据
        if include_realtime and self._need_realtime_supplement(historical, period):
            # 获取从最后一条数据日期到今天的数据（可能覆盖同一天的数据）
            last_date = historical.df.iloc[-1]['datetime']
            start_date_formatted = last_date.strftime('%Y-%m-%d')

            logger.info(f"[数据补全] 准备获取补充数据，start_date={start_date_formatted}")

            # 实时数据也是不复权原始数据
            realtime = self._get_realtime_kline(
                symbol, period, 'none',
                start_date=start_date_formatted,
                filter_today=False, get_realtime=True
            )

            logger.info(f"[数据补全] 获取到实时数据: {len(realtime.df)} 条")
            if not realtime.df.empty:
                logger.info(f"[数据补全] 实时数据日期范围: {realtime.df['datetime'].min()} 到 {realtime.df['datetime'].max()}")
                # 合并历史和实时数据
                historical = historical.merge(realtime)
                logger.info(f"[数据补全] 合并后总计: {len(historical.df)} 条，最新日期: {historical.df['datetime'].max()}")
            else:
                logger.warning(f"[数据补全] 未获取到补充数据 (从 {start_date_formatted})")
        else:
            logger.info("[数据补全] 不需要补充数据")

        # 应用日期范围过滤
        if start_date or end_date:
            historical = historical.slice_by_date(start_date, end_date)

        # 统一应用复权（所有数据源现在都返回不复权数据）
        # 复权在数据合并后统一应用，确保一致性
        if adjust_type != 'none' and not historical.df.empty:
            historical.df = self._apply_adjustment(
                historical.df, symbol, adjust_type
            )

        # 日线数据标准化时间为 15:00:00（A股收盘时间）
        # 并过滤掉周末数据
        if period == '1d' and not historical.df.empty:
            def normalize_daily_time(dt):
                if pd.isna(dt):
                    return dt
                if isinstance(dt, str):
                    dt = pd.to_datetime(dt)
                # 标准化为北京时间 15:00
                return dt.replace(hour=15, minute=0, second=0, microsecond=0)
            historical.df['datetime'] = historical.df['datetime'].apply(normalize_daily_time)

            # 过滤周末（周六=5, 周日=6）
            historical.df = historical.df[historical.df['datetime'].dt.weekday < 5].copy()

        # 全周期通用去重：同一时间戳可能来自多个数据源，保留最后一条（在线数据）
        if not historical.df.empty:
            before_dedup = len(historical.df)
            historical.df = historical.df.drop_duplicates(subset=['datetime'], keep='last')
            after_dedup = len(historical.df)
            if before_dedup != after_dedup:
                logger.info(f"[去重] 移除 {before_dedup - after_dedup} 条重复数据（优先保留在线数据）")

        # 应用数量限制（必须在周末过滤和去重之后，确保返回的是最新的交易日数据）
        if count:
            # 复权时返回扩展后的数量，否则用户看不到除权日之前的数据
            return_count = actual_count if adjust_type != 'none' else count
            before_count = len(historical.df)
            historical = historical.filter_by_count(return_count, from_end=True)
            after_count = len(historical.df)
            logger.info(f"[数量限制] 请求={count}, actual_count={actual_count}, return_count={return_count}, 限制前={before_count}, 限制后={after_count}")

        # 标记正在形成的K线
        historical.df = self._mark_forming_kline(historical.df, period)

        return historical.df

    def _apply_adjustment(
        self,
        df: pd.DataFrame,
        symbol: str,
        adjust_type: str
    ) -> pd.DataFrame:
        """应用复权

        Args:
            df: K线数据
            symbol: 股票代码
            adjust_type: 复权类型

        Returns:
            复权后的 DataFrame
        """
        try:
            calculator = get_adjustment_calculator()

            # 获取除权除息数据
            xdxr_data = self._get_xdxr_data(symbol)

            if xdxr_data:
                df = calculator.apply_adjustment(df, xdxr_data, symbol, adjust_type)
                logger.info(f"[复权] {symbol} 应用 {adjust_type} 复权完成")
            else:
                logger.debug(f"[复权] {symbol} 无除权数据，无需复权")

        except Exception as e:
            logger.warning(f"[复权] {symbol} 复权计算失败: {e}")

        return df

    def _get_xdxr_data(self, symbol: str) -> list:
        """获取除权除息数据

        优先级: TdxQuant → PyTdx
        - TdxQuant: 覆盖范围更广（支持板块和指数）
        - PyTdx: 作为备用

        Args:
            symbol: 股票代码

        Returns:
            除权除息记录列表
        """
        # 优先从 TdxQuant 获取（覆盖范围更广，仅交易时间可用）
        if TradingTimeChecker.is_trading_time():
            try:
                tdxquant = self._get_adapter('tdxquant')
                if tdxquant and tdxquant.is_available():
                    # TdxQuant SDK 的 get_xdxr_info 方法
                    if hasattr(tdxquant._tq, 'get_xdxr_info'):
                        xdxr_data = tdxquant._tq.get_xdxr_info([symbol])
                        if xdxr_data and symbol in xdxr_data:
                            logger.debug(f"[XDXR] TdxQuant 获取 {symbol} 除权数据: {len(xdxr_data[symbol])} 条")
                            return xdxr_data[symbol]
            except Exception as e:
                logger.debug(f"[XDXR] TdxQuant 获取除权数据失败: {e}")

        # 备用: 从 PyTdx 获取
        try:
            pytdx = self._get_adapter('pytdx')
            if pytdx and pytdx.is_available():
                xdxr_data = pytdx.get_xdxr_info(symbol)
                if xdxr_data:
                    logger.debug(f"[XDXR] PyTdx 获取 {symbol} 除权数据: {len(xdxr_data)} 条")
                    return xdxr_data
        except Exception as e:
            logger.debug(f"[XDXR] PyTdx 获取除权数据失败: {e}")

        logger.debug(f"[XDXR] {symbol} 无除权数据")
        return []

    def _get_historical_kline(
        self,
        symbol: str,
        period: str,
        count: int,
        start_date: Optional[str],
        end_date: Optional[str],
        adjust_type: str
    ) -> KlineDataset:
        """获取历史 K线数据

        Args:
            period: 周期 (用于分钟级数据的交易时间判断)
            adjust_type: 复权类型，直接传递给数据源
                - PyTdx 支持原生复权 (front/back/none)
                - 其他数据源返回不复权数据，由服务层处理
        """
        # 获取基础数据源链
        chain = self._selector.get_fallback_chain_for_code(DataLevel.L3, symbol)

        # 服务层：根据交易时间调整数据源优先级
        is_trading = TradingTimeChecker.is_trading_time()

        if is_trading:
            # 开盘在线优先: tdxquant → xtquant → pytdx
            trading_priority = ['tdxquant', 'xtquant', 'pytdx']
            adjusted_chain = []
            for s in trading_priority:
                if s in chain:
                    adjusted_chain.append(s)
            # 添加其他不在列表中的源
            for s in chain:
                if s not in adjusted_chain:
                    adjusted_chain.append(s)
            chain = adjusted_chain
            logger.debug(f"[服务层] 交易时间，优先级: {chain}")
        else:
            # 收盘在线优先: xtquant → pytdx（不使用 tdxquant）
            # TdxQuant 非交易时间不可用（需要通达信终端运行）
            non_trading_priority = ['xtquant', 'pytdx']
            adjusted_chain = []
            for s in non_trading_priority:
                if s in chain:
                    adjusted_chain.append(s)
            # 添加其他不在列表中的源（但排除 tdxquant）
            for s in chain:
                if s not in adjusted_chain and s != 'tdxquant':
                    adjusted_chain.append(s)
            chain = adjusted_chain
            logger.debug(f"[服务层] 非交易时间，优先级: {chain}")

        adapter = chain[0] if chain else None

        if adapter is None:
            return KlineDataset.empty()

        # 所有适配器现在都返回不复权数据，复权由服务层统一处理
        # 不需要再根据复权类型排除特定适配器（如 LocalDB）
        attempt_chain = chain

        for try_adapter in attempt_chain:
            try:
                adapter_instance = self._get_adapter(try_adapter)
                if not adapter_instance:
                    continue

                # 始终传递 'none' 给适配器（获取不复权原始数据）
                df_dict = adapter_instance.get_kline(
                    symbols=[symbol],
                    period=period,
                    start_date=start_date,
                    end_date=end_date,
                    count=count,
                    adjust_type='none'  # 始终获取不复权数据
                )

                if symbol in df_dict and not df_dict[symbol].empty:
                    return KlineDataset.from_adapter(df_dict[symbol], try_adapter)

            except Exception:
                continue

        return KlineDataset.empty()

    def _get_realtime_kline(
        self,
        symbol: str,
        period: str,
        adjust_type: str,
        start_date: Optional[str] = None,  # 新增：指定开始日期
        filter_today: bool = True,
        get_realtime: bool = True
    ) -> KlineDataset:
        """获取补充的 K线数据（从指定日期到今天）

        Args:
            symbol: 股票代码
            period: 周期
            adjust_type: 复权类型
            start_date: 开始日期 (YYYYMMDD)，默认为今天
            filter_today: 是否只过滤今天的数据
            get_realtime: 是否获取实时数据
        """
        is_trading = TradingTimeChecker.is_trading_time()
        # 如果没有指定开始日期，使用今天
        if not start_date:
            start_date = datetime.now().strftime('%Y%m%d')

        logger.info(f"[补充数据] 开始获取 {symbol} 从 {start_date} 到现在的数据")

        # 数据源优先级链（补充数据时跳过 localdb，因为它只有历史数据）
        fallback_chain = self._selector.get_fallback_chain_for_code(DataLevel.L3, symbol)
        # 移除 localdb；非交易时间也移除 tdxquant（终端未运行）
        is_trading = TradingTimeChecker.is_trading_time()
        supplement_chain = [
            s for s in fallback_chain
            if s != 'localdb' and (is_trading or s != 'tdxquant')
        ]

        # 对于日线数据，PyTdx 有最新的交易日数据，优先使用
        if period == '1d' and 'pytdx' in supplement_chain:
            supplement_chain = [s for s in supplement_chain if s != 'pytdx']
            supplement_chain.insert(0, 'pytdx')

        # 对于分钟线数据，XtQuant OHLCV 数据质量更好（pytdx 收盘 bar 有已知的 high/low 污染问题）
        elif period != '1d' and 'xtquant' in supplement_chain:
            supplement_chain = [s for s in supplement_chain if s != 'xtquant']
            supplement_chain.insert(0, 'xtquant')

        if not supplement_chain:
            logger.debug("[补充数据] 没有可用的在线数据源")
            return KlineDataset.empty()

        logger.info(f"[补充数据] 可用数据源: {supplement_chain}")

        # 尝试各数据源获取补充数据
        for source in supplement_chain:
            try:
                adapter_instance = self._get_adapter(source)
                if not adapter_instance or not adapter_instance.is_available():
                    logger.debug(f"[补充数据] {source} 不可用，跳过")
                    continue

                logger.info(f"[补充数据] 尝试从 {source} 获取 {symbol} 数据 (start_date={start_date}, count=500)")

                # 获取从 start_date 到现在的数据（始终获取不复权数据）
                df_dict = adapter_instance.get_kline(
                    symbols=[symbol],
                    period=period,
                    start_date=start_date,
                    count=500 if not is_trading else 100,  # 收盘后多取
                    adjust_type='none'  # 始终获取不复权数据，复权由服务层统一处理
                )

                if symbol in df_dict and not df_dict[symbol].empty:
                    df = df_dict[symbol]
                    min_date = str(df['datetime'].min()) if 'datetime' in df.columns else 'N/A'
                    max_date = str(df['datetime'].max()) if 'datetime' in df.columns else 'N/A'
                    logger.info(f"[补充数据] {source} 返回 {len(df)} 条数据，日期范围: {min_date} 到 {max_date}")

                    if not df.empty:
                        # 检查数据是否足够新鲜（最新数据应该在最近7天内）
                        if 'datetime' in df.columns:
                            latest_date = df['datetime'].iloc[-1]
                            try:
                                if isinstance(latest_date, str):
                                    latest_dt = datetime.strptime(latest_date.split()[0], '%Y-%m-%d')
                                elif hasattr(latest_date, 'date'):
                                    latest_dt = latest_date
                                else:
                                    latest_dt = pd.to_datetime(latest_date)
                                days_old = (datetime.now().date() - latest_dt.date()).days
                                if days_old > 7:
                                    logger.info(f"[补充数据] {source} 数据过旧（{days_old}天前），尝试下一个数据源")
                                    continue
                            except Exception as e:
                                logger.debug(f"[补充数据] 无法检查数据新鲜度: {e}")

                        logger.info(f"[{'实时' if is_trading else '补充'}] {source} 获取 {symbol} 数据成功: {len(df)} 条 (从 {start_date})")
                        return KlineDataset.from_adapter(df, source)
                else:
                    logger.debug(f"[补充数据] {source} 没有返回 {symbol} 的数据")

            except Exception as e:
                logger.warning(f"[{'实时' if is_trading else '补充'}] {source} 获取 {symbol} 失败: {e}")
                continue

        logger.warning(f"[补充数据] 所有数据源都无法获取 {symbol} 从 {start_date} 开始的数据")
        return KlineDataset.empty()

    def _need_realtime_supplement(self, historical: KlineDataset, period: str) -> bool:
        """判断是否需要补充实时数据"""
        if historical.df.empty:
            return False

        last_time = historical.df.iloc[-1]['datetime']

        # 判断最后一条数据是否是今天
        today = datetime.now().date()
        logger.info(f"[数据补全检查] 最后数据日期: {last_time.date()}, 今天: {today}")
        if last_time.date() < today:
            logger.info(f"[数据补全] 需要补充: 最后数据({last_time.date()}) 早于今天({today})")
            return True

        # 对于分钟级别数据，检查最后一条时间是否过时
        if period in ['1m', '5m', '15m', '30m', '1h']:
            now = datetime.now()
            time_diff = (now - last_time).total_seconds()

            # 如果超过2个周期，认为需要补充
            period_minutes = {'1m': 1, '5m': 5, '15m': 15, '30m': 30, '1h': 60}.get(period, 5)
            if time_diff > period_minutes * 2 * 60:
                return True

        return False

    def _get_adapter(self, name: str):
        """获取或创建适配器（带缓存）"""
        if name not in self._adapter_cache:
            self._adapter_cache[name] = get_adapter(name)
        return self._adapter_cache[name]

    def _mark_forming_kline(self, df: pd.DataFrame, period: str) -> pd.DataFrame:
        """标记正在形成的K线

        Args:
            df: K线数据 DataFrame
            period: 周期 (1m/5m/15m/30m/1h/1d)

        Returns:
            添加了 is_complete 列的 DataFrame
        """
        if df.empty:
            return df

        # 创建 is_complete 列，默认为 True
        df = df.copy()
        df['is_complete'] = True

        # 判断最后一根K线是否正在形成
        now = datetime.now()
        last_time = df.iloc[-1]['datetime']

        # 处理 datetime 类型
        if isinstance(last_time, str):
            last_time = pd.to_datetime(last_time)
        elif not isinstance(last_time, pd.Timestamp):
            last_time = pd.Timestamp(last_time)

        is_forming = False

        # 分钟线判断
        if period in ['1m', '5m', '15m', '30m', '1h']:
            period_minutes = {'1m': 1, '5m': 5, '15m': 15, '30m': 30, '1h': 60}
            mins = period_minutes.get(period, 5)

            # 计算当前周期开始时间
            current_period_start = now.replace(
                minute=now.minute // mins * mins,
                second=0,
                microsecond=0
            )

            # 如果最后一根K线的时间 >= 当前周期开始时间，说明正在形成
            is_forming = last_time >= current_period_start

        # 日线判断
        elif period == '1d':
            # 日线：检查是否是今天且在交易时间内
            is_trading = TradingTimeChecker.is_trading_time()
            is_today = last_time.date() == now.date()

            # 交易时间内当天的K线正在形成
            is_forming = is_today and is_trading

        # 标记最后一根K线
        if is_forming:
            df.iloc[-1, df.columns.get_loc('is_complete')] = False
            logger.debug(f"[K线标记] 最后一根K线正在形成: {last_time}")

        return df

    def clear_cache(self) -> None:
        """清空适配器缓存"""
        self._adapter_cache.clear()


# 单例实例
_seamless_kline_service: Optional[SeamlessKlineService] = None


def get_seamless_kline_service() -> SeamlessKlineService:
    """获取 SeamlessKlineService 单例实例"""
    global _seamless_kline_service
    if _seamless_kline_service is None:
        _seamless_kline_service = SeamlessKlineService()
    return _seamless_kline_service

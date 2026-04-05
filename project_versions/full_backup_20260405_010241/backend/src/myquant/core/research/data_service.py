# -*- coding: utf-8 -*-
"""
Research阶段 - 统一数据服务
============================
职责：
- L0-L5分层数据访问
- 多数据源智能调度
- 数据归档和缓存管理
- 交易日历管理

架构层次：
- Research阶段：负责因子计算、特征工程的数据获取
- 不涉及回测和实盘交易逻辑
"""

from typing import List, Dict, Optional, Union, Tuple, Any
from loguru import logger
from datetime import datetime, date
from enum import Enum
from pathlib import Path
import pandas as pd
import json


class DataType(Enum):
    """数据类型枚举"""
    REALTIME_QUOTE = "realtime_quote"      # 实时行情快照
    KLINE = "kline"                        # K线数据
    TICK = "tick"                          # 分笔数据
    FINANCIAL = "financial"                # 财务数据
    SECTOR_INDEX = "sector_index"          # 板块指数
    MARKET_INDEX = "market_index"          # 市场指数
    MONEY_FLOW = "money_flow"              # 资金流向
    SHAREHOLDER = "shareholder"            # 股东信息


class ResearchDataService:
    """
    Research阶段数据服务

    核心职责：
    1. 统一数据获取接口（支持所有数据类型）
    2. 智能数据源调度（本地DB → XtQuant → PyTdx）
    3. 自动数据归档到本地数据库
    4. 交易日历管理

    与旧系统的关系：
    - 使用适配器模式包装 UnifiedDataManager
    - 逐步迁移核心功能到新架构
    - 保持向后兼容性
    """

    def __init__(
        self,
        enable_legacy_adapter: bool = True,  # 是否启用旧系统适配器
    ):
        """
        初始化Research数据服务

        Args:
            enable_legacy_adapter: 启用旧系统适配器（过渡期使用）
        """
        self.enable_legacy_adapter = enable_legacy_adapter
        self._legacy_manager = None

        # 数据源统计
        self.stats = {
            "total_requests": 0,
            "cache_hits": 0,
            "db_hits": 0,
            "xtquant_hits": 0,
            "pytdx_hits": 0,
        }

        # 初始化旧系统适配器
        if enable_legacy_adapter:
            self._init_legacy_adapter()

        logger.info("✅ ResearchDataService初始化完成")

    def _init_legacy_adapter(self):
        """初始化旧系统适配器"""
        try:
            from data.unified_data_manager import get_unified_data_manager
            self._legacy_manager = get_unified_data_manager()
            logger.info("✅ 旧系统适配器已加载（UnifiedDataManager）")
        except Exception as e:
            logger.warning(f"⚠️ 旧系统适配器加载失败: {e}")
            self._legacy_manager = None

    # ==================== 公共API接口 ====================

    async def get_kline_data(
        self,
        symbol: str,
        period: str = "day",
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        count: int = 100,
        adjust_type: str = "front",
        data_level: str = "L1"
    ) -> Optional[pd.DataFrame]:
        """
        获取K线数据

        Args:
            symbol: 股票代码（如 "000001.SZ"）
            period: 周期（day/week/month/1min/5min/15min/30min/60min）
            start_date: 开始日期（YYYY-MM-DD）
            end_date: 结束日期（YYYY-MM-DD）
            count: 数据条数（当start_date未指定时）
            adjust_type: 复权类型（front前权/none不复权/back后权）
            data_level: 数据层级（L0-L5）

        Returns:
            K线数据DataFrame，包含字段：open, high, low, close, volume, amount
        """
        self.stats["total_requests"] += 1

        # 如果启用旧系统适配器，先使用它（过渡期策略）
        if self._legacy_manager and self.enable_legacy_adapter:
            try:
                # 映射 data_level 到 data_type
                # L0/L1 -> L1 (实时快照)
                # L2/L3/L3.5 -> L2 (历史K线)
                data_type_map = {
                    'L0': 'L1',
                    'L1': 'L1',
                    'L2': 'L2',
                    'L3': 'L2',
                    'L3.5': 'L2'
                }
                data_type = data_type_map.get(data_level, 'L2')

                # 调用新的统一数据接口
                result = await self._legacy_manager.get_data_unified(
                    data_type=data_type,
                    symbols=[symbol],  # 必须是列表
                    source='auto',
                    enable_fallback=True,
                    period=period,
                    start_date=start_date,
                    end_date=end_date,
                    count=count,
                    adjust_type=adjust_type
                )

                if result and symbol in result:
                    df = result[symbol]
                    self.stats["db_hits"] += 1
                    return df

            except Exception as e:
                logger.warning(f"统一数据接口获取K线失败: {e}，尝试备用方案")

        # 实现新的K线数据获取逻辑（不依赖legacy_adapter）
        # 数据优先级：
        # 1. Redis缓存（实时/最新数据）- key: kline:{symbol}:{period}:{date}
        # 2. UnifiedDataManager（多数据源自动降级）
        try:
            # 映射 data_level 到 data_type
            data_type_map = {
                'L0': 'L1',
                'L1': 'L1',
                'L2': 'L2',
                'L3': 'L2',
                'L3.5': 'L2'
            }
            data_type = data_type_map.get(data_level, 'L2')

            # 直接使用UnifiedDataManager获取数据（v3.1实现）
            result = await self._legacy_manager.get_data_unified(
                data_type=data_type,
                symbols=[symbol],
                source='auto',
                enable_fallback=True,
                period=period,
                start_date=start_date,
                end_date=end_date,
                count=count
            )

            if result and symbol in result:
                df = result[symbol]
                if df is not None and not df.empty:
                    logger.info(f"✅ 从UnifiedDataManager获取K线数据: {symbol}, {len(df)}行")
                    return df
                else:
                    logger.warning(f"⚠️ K线数据为空: {symbol}")
                    return None
            else:
                logger.warning(f"⚠️ 未获取到K线数据: {symbol}")
                return None

        except Exception as e:
            logger.error(f"从UnifiedDataManager获取K线失败: {e}")
            import traceback
            traceback.print_exc()
            return None

    async def get_realtime_quote(
        self,
        symbols: List[str],
        fallback: bool = True
    ) -> Dict[str, Dict]:
        """
        获取实时行情

        Args:
            symbols: 股票代码列表
            fallback: 是否启用降级策略

        Returns:
            实时行情字典 {symbol: quote_data}
        """
        self.stats["total_requests"] += 1

        if self._legacy_manager and self.enable_legacy_adapter:
            try:
                # 调用旧系统实时行情接口
                result = await self._legacy_manager.get_quotes(symbols)
                self.stats["xtquant_hits"] += 1
                return result
            except Exception as e:
                logger.warning(f"旧系统适配器获取实时行情失败: {e}")

        # 实现新的实时行情获取逻辑
        # 数据优先级：
        # 1. Redis缓存（最新行情）- key: quote:{symbol}
        # 2. XtQuant实时接口（实时数据流）
        # 3. 通达信实时接口（备用）

        # 框架代码（待数据源完善后启用）:
        # results = {}
        # try:
        #     # 1. 批量从Redis获取缓存行情
        #     cache_keys = [f"quote:{symbol}" for symbol in symbols]
        #     cached_quotes = await redis.mget(cache_keys)
        #
        #     for symbol, cached in zip(symbols, cached_quotes):
        #         if cached:
        #             results[symbol] = json.loads(cached)
        #         else:
        #             # 2. 从XtQuant实时接口获取
        #             quote = await self._get_realtime_from_xtquant(symbol)
        #             if quote:
        #                 results[symbol] = quote
        #                 # 缓存到Redis（30秒过期）
        #                 await redis.setex(f"quote:{symbol}", 30, json.dumps(quote))
        #
        #     self.stats["cache_hits"] += len(results)
        #     return results
        #
        # except Exception as e:
        #     logger.error(f"新实现获取实时行情失败: {e}")

        return {}

    async def get_financial_data(
        self,
        symbol: str,
        report_type: str = "annual"
    ) -> Optional[Dict]:
        """
        获取财务数据

        Args:
            symbol: 股票代码
            report_type: 报告类型（annual/quarterly）

        Returns:
            财务数据字典
        """
        self.stats["total_requests"] += 1

        if self._legacy_manager and self.enable_legacy_adapter:
            try:
                result = await self._legacy_manager.get_data(
                    symbol_list=[symbol],
                    data_type=DataType.FINANCIAL,
                    report_type=report_type
                )
                return result.get(symbol) if result else None
            except Exception as e:
                logger.warning(f"获取财务数据失败: {e}")

        return None

    def get_trading_calendar(
        self,
        market: str = "SH",
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> List[str]:
        """
        获取交易日历

        Args:
            market: 市场代码（SH/SZ）
            start_date: 开始日期（YYYY-MM-DD）
            end_date: 结束日期（YYYY-MM-DD）

        Returns:
            交易日列表（YYYY-MM-DD格式）
        """
        if self._legacy_manager and self.enable_legacy_adapter:
            try:
                return self._legacy_manager.get_trading_calendar(
                    market=market,
                    start_date=start_date,
                    end_date=end_date
                )
            except Exception as e:
                logger.warning(f"获取交易日历失败: {e}")

        # 默认返回空列表
        return []

    def is_trading_day(self, date_str: str, market: str = "SH") -> bool:
        """
        判断是否为交易日

        Args:
            date_str: 日期字符串（YYYY-MM-DD）
            market: 市场代码（SH/SZ）

        Returns:
            True表示是交易日
        """
        try:
            trading_days = self.get_trading_calendar(
                market=market,
                start_date=date_str,
                end_date=date_str
            )
            return date_str in trading_days
        except Exception as e:
            logger.error(f"判断交易日失败: {e}")
            return False

    # ==================== 因子数据接口 ====================

    def get_factor_data(
        self,
        factor_name: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        instruments: Optional[List[str]] = None
    ) -> Optional[pd.DataFrame]:
        """
        获取因子数据

        Args:
            factor_name: 因子名称
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
            instruments: 股票列表

        Returns:
            因子数据DataFrame，包含字段: datetime, symbol, factor_value
            或 None（当数据不可用时）

        数据源优先级：
        1. QLib因子数据: ~/data/qlib_data/factors/{factor_name}.pkl
        2. 数据库表: generated_factors
        3. 旧系统适配器
        4. 降级: 返回None
        """
        self.stats["total_requests"] += 1

        try:
            # ==================== 数据源1: QLib因子文件 ====================
            factor_file = Path("~/data/qlib_data/factors").expanduser() / f"{factor_name}.pkl"
            if factor_file.exists():
                try:
                    df = pd.read_pickle(factor_file)

                    # 过滤日期范围
                    if start_date:
                        df = df[df.index >= start_date]
                    if end_date:
                        df = df[df.index <= end_date]

                    # 过滤股票列表
                    if instruments and 'symbol' in df.columns:
                        df = df[df['symbol'].isin(instruments)]

                    self.stats["db_hits"] += 1
                    logger.info(f"✅ 从QLib文件加载因子: {factor_name}, 形状: {df.shape}")
                    return df
                except Exception as e:
                    logger.warning(f"读取QLib因子文件失败: {factor_file}, 错误: {e}")

            # ==================== 数据源2: 数据库查询 ====================
            try:
                from backend.core.database import DatabaseManager
                from sqlalchemy import text

                session = DatabaseManager.get_session()
                if session:
                    query = text("""
                        SELECT datetime, symbol, factor_value
                        FROM generated_factors
                        WHERE factor_name = :factor_name
                        AND (:start_date IS NULL OR datetime >= :start_date)
                        AND (:end_date IS NULL OR datetime <= :end_date)
                        ORDER BY datetime, symbol
                    """)

                    result = session.execute(query, {
                        "factor_name": factor_name,
                        "start_date": start_date,
                        "end_date": end_date
                    })

                    rows = result.fetchall()
                    if rows:
                        df = pd.DataFrame([dict(row) for row in rows])

                        # 过滤股票列表
                        if instruments and not df.empty:
                            df = df[df['symbol'].isin(instruments)]

                        self.stats["db_hits"] += 1
                        logger.info(f"✅ 从数据库加载因子: {factor_name}, 形状: {df.shape}")
                        return df
            except Exception as e:
                logger.debug(f"数据库因子查询失败: {e}")

            # ==================== 数据源3: 旧系统适配器 ====================
            if self._legacy_manager and hasattr(self._legacy_manager, 'get_factor_data'):
                try:
                    result = self._legacy_manager.get_factor_data(
                        factor_name=factor_name,
                        start_date=start_date,
                        end_date=end_date,
                        instruments=instruments
                    )
                    if result is not None:
                        self.stats["db_hits"] += 1
                        logger.info(f"✅ 从旧系统加载因子: {factor_name}")
                        return result
                except Exception as e:
                    logger.debug(f"旧系统因子查询失败: {e}")

            # ==================== 数据源4: 降级返回 ====================
            logger.warning(f"因子数据源未找到: {factor_name}，返回None")
            return None

        except Exception as e:
            logger.error(f"获取因子数据失败: {factor_name}, 错误: {e}")
            return None

    async def get_returns_data(
        self,
        start_date: str,
        end_date: str,
        instruments: Optional[List[str]] = None,
        period: str = "1d",
        benchmark: str = "000300.SH"
    ) -> Optional[pd.DataFrame]:
        """
        获取收益率数据

        Args:
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
            instruments: 股票列表
            period: 周期 (1d/1w/1M)
            benchmark: 基准指数

        Returns:
            收益率DataFrame，包含字段: datetime, symbol, return
            或 None（当数据不可用时）

        计算方式：
        - return = (close_t - close_t-1) / close_t-1
        - 从K线数据计算收益率
        """
        self.stats["total_requests"] += 1

        try:
            # 默认股票列表（全市场）
            if not instruments:
                instruments = self._get_default_stock_list()

            returns_data = []

            # ==================== 数据源1: 从K线数据计算 ====================
            for symbol in instruments:
                try:
                    # 获取K线数据
                    kline_df = await self.get_kline_data(
                        symbol=symbol,
                        period="day",
                        start_date=start_date,
                        end_date=end_date,
                        count=-1  # 获取全部数据
                    )

                    if kline_df is not None and not kline_df.empty:
                        # 计算收益率
                        kline_df['return'] = kline_df['close'].pct_change()

                        # 添加symbol列
                        kline_df['symbol'] = symbol

                        # 重置索引以方便合并
                        if isinstance(kline_df.index, pd.DatetimeIndex):
                            kline_df = kline_df.reset_index()
                            kline_df.rename(columns={'index': 'datetime'}, inplace=True)

                        returns_data.append(kline_df[['datetime', 'symbol', 'return']])

                except Exception as e:
                    logger.debug(f"计算{symbol}收益率失败: {e}")
                    continue

            # ==================== 合并数据 ====================
            if returns_data:
                result_df = pd.concat(returns_data, ignore_index=True)
                self.stats["db_hits"] += 1
                logger.info(f"✅ 收益率数据计算完成, 形状: {result_df.shape}")
                return result_df

            # ==================== 数据源2: 从缓存文件加载 ====================
            cache_file = Path("~/data/cache/returns").expanduser() / f"{start_date}_{end_date}.pkl"
            if cache_file.exists():
                try:
                    cached_df = pd.read_pickle(cache_file)
                    self.stats["cache_hits"] += 1
                    logger.info(f"✅ 从缓存加载收益率数据")
                    return cached_df
                except Exception as e:
                    logger.debug(f"读取缓存失败: {e}")

            # ==================== 数据源3: 旧系统适配器 ====================
            if self._legacy_manager and hasattr(self._legacy_manager, 'get_returns_data'):
                try:
                    result = self._legacy_manager.get_returns_data(
                        start_date=start_date,
                        end_date=end_date,
                        instruments=instruments
                    )
                    if result is not None:
                        self.stats["db_hits"] += 1
                        logger.info(f"✅ 从旧系统加载收益率数据")
                        return result
                except Exception as e:
                    logger.debug(f"旧系统收益率查询失败: {e}")

            logger.warning("收益率数据源未找到，返回None")
            return None

        except Exception as e:
            logger.error(f"获取收益率数据失败: {e}")
            return None

    def _get_default_stock_list(self) -> List[str]:
        """
        获取默认股票列表

        Returns:
            股票代码列表
        """
        # 常见A股市场股票池
        default_stocks = []

        # 尝试从配置文件读取
        try:
            config_file = Path("backend/config/stock_pools.json")
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    default_stocks = data.get("default_pool", [])
        except Exception as e:
            logger.debug(f"读取股票池配置失败: {e}")

        # 如果配置为空，返回沪深300成分股（简化示例）
        if not default_stocks:
            default_stocks = [
                "000001.SZ", "000002.SZ", "000300.SZ", "600000.SH",
                "600036.SH", "601318.SH", "601398.SH", "601988.SH"
            ]

        return default_stocks

    def get_multi_factor_data(
        self,
        factor_names: List[str],
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        instruments: Optional[List[str]] = None
    ) -> Optional[pd.DataFrame]:
        """
        获取多因子数据

        Args:
            factor_names: 因子名称列表
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
            instruments: 股票列表

        Returns:
            多因子DataFrame，包含字段: datetime, symbol, factor_name, factor_value
            或 None（当数据不可用时）

        数据格式：
        - 长格式: datetime, symbol, factor_name, factor_value
        - 每个因子一行，方便后续处理
        """
        self.stats["total_requests"] += 1

        try:
            # ==================== 批量加载因子数据 ====================
            factors_data = {}
            failed_factors = []

            for factor_name in factor_names:
                try:
                    # 调用单因子加载
                    df = self.get_factor_data(
                        factor_name=factor_name,
                        start_date=start_date,
                        end_date=end_date,
                        instruments=instruments
                    )

                    if df is not None and not df.empty:
                        # 添加因子名称列
                        df['factor_name'] = factor_name

                        # 标准化列名
                        if 'factor_value' not in df.columns:
                            # 如果列名不同，尝试重命名
                            if 'value' in df.columns:
                                df.rename(columns={'value': 'factor_value'}, inplace=True)
                            elif 'factor' in df.columns:
                                df.rename(columns={'factor': 'factor_value'}, inplace=True)
                            else:
                                # 使用最后一列作为因子值
                                last_col = df.columns[-1]
                                df.rename(columns={last_col: 'factor_value'}, inplace=True)

                        factors_data[factor_name] = df
                        logger.debug(f"✅ 加载因子: {factor_name}, 形状: {df.shape}")
                    else:
                        failed_factors.append(factor_name)
                        logger.warning(f"因子数据为空: {factor_name}")

                except Exception as e:
                    failed_factors.append(factor_name)
                    logger.error(f"加载因子{factor_name}失败: {e}")

            # ==================== 合并为长格式 ====================
            if factors_data:
                # 合并所有因子数据
                result_df = pd.concat(
                    list(factors_data.values()),
                    ignore_index=True
                )

                # 确保必要的列存在
                required_cols = ['datetime', 'symbol', 'factor_name', 'factor_value']
                for col in required_cols:
                    if col not in result_df.columns:
                        # 尝试推断列名
                        if col == 'datetime' and 'date' in result_df.columns:
                            result_df.rename(columns={'date': 'datetime'}, inplace=True)
                        elif col == 'symbol' and 'instrument' in result_df.columns:
                            result_df.rename(columns={'instrument': 'symbol'}, inplace=True)

                self.stats["db_hits"] += len(factors_data)

                # 报告加载结果
                success_count = len(factors_data)
                total_count = len(factor_names)
                logger.info(
                    f"✅ 多因子数据加载完成: {success_count}/{total_count} 成功, "
                    f"最终形状: {result_df.shape}"
                )

                if failed_factors:
                    logger.warning(f"⚠️ 以下因子加载失败: {', '.join(failed_factors)}")

                return result_df

            # ==================== 数据源2: 从缓存文件加载 ====================
            cache_key = f"{'_'.join(sorted(factor_names))}_{start_date}_{end_date}"
            cache_file = Path("~/data/cache/multi_factor").expanduser() / f"{cache_key}.pkl"

            if cache_file.exists():
                try:
                    cached_df = pd.read_pickle(cache_file)
                    self.stats["cache_hits"] += 1
                    logger.info(f"✅ 从缓存加载多因子数据")
                    return cached_df
                except Exception as e:
                    logger.debug(f"读取多因子缓存失败: {e}")

            # ==================== 数据源3: 旧系统适配器 ====================
            if self._legacy_manager and hasattr(self._legacy_manager, 'get_multi_factor_data'):
                try:
                    result = self._legacy_manager.get_multi_factor_data(
                        factor_names=factor_names,
                        start_date=start_date,
                        end_date=end_date,
                        instruments=instruments
                    )
                    if result is not None:
                        self.stats["db_hits"] += len(factor_names)
                        logger.info(f"✅ 从旧系统加载多因子数据")
                        return result
                except Exception as e:
                    logger.debug(f"旧系统多因子查询失败: {e}")

            logger.warning("多因子数据源未找到，返回None")
            return None

        except Exception as e:
            logger.error(f"获取多因子数据失败: {e}")
            return None

    # ==================== 统计信息接口 ====================

    def get_stats(self) -> Dict[str, Any]:
        """
        获取服务统计信息

        Returns:
            统计数据字典
        """
        return {
            **self.stats,
            "adapter_enabled": self.enable_legacy_adapter,
            "adapter_available": self._legacy_manager is not None,
        }


# ==================== 全局单例 ====================

_research_data_service_instance: Optional[ResearchDataService] = None


def get_research_data_service() -> ResearchDataService:
    """
    获取Research数据服务单例

    Returns:
        ResearchDataService实例
    """
    global _research_data_service_instance

    if _research_data_service_instance is None:
        _research_data_service_instance = ResearchDataService()

    return _research_data_service_instance

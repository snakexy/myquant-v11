# -*- coding: utf-8 -*-
"""
Research阶段 - 股票服务
=========================
职责：
- 股票基本信息获取
- 股票列表管理
- 因子计算所需的数据准备
- 股票筛选和分类

架构层次：
- Research阶段：为因子计算提供股票基础数据
- 不涉及交易逻辑
"""

from typing import List, Optional, Dict, Any
from loguru import logger
from datetime import datetime, timedelta
import pandas as pd
from dataclasses import dataclass


@dataclass
class StockInfo:
    """股票基本信息"""
    symbol: str              # 股票代码
    name: str                # 股票名称
    market: str              # 市场（SH/SZ）
    industry: Optional[str]  # 所属行业
    list_date: Optional[str] # 上市日期
    current_price: float     # 当前价格
    pre_close: float         # 前收盘价
    change: float            # 涨跌额
    change_percent: float    # 涨跌幅（%）
    volume: float            # 成交量
    amount: float            # 成交额
    market_cap: Optional[float] = None  # 总市值
    pe_ratio: Optional[float] = None     # 市盈率
    pb_ratio: Optional[float] = None     # 市净率


class ResearchStockService:
    """
    Research阶段股票服务

    核心职责：
    1. 股票基本信息管理
    2. 股票列表查询和筛选
    3. 为因子计算提供数据准备
    4. 股票分类（行业/概念/板块）

    与旧系统的关系：
    - 迁移自 backend/api/api_layer/services/business/stock_service.py
    - 保持API兼容性
    - 优化为Research阶段专用服务
    """

    def __init__(
        self,
        enable_legacy_adapter: bool = True,
    ):
        """
        初始化Research股票服务

        Args:
            enable_legacy_adapter: 启用旧系统适配器（过渡期使用）
        """
        self.enable_legacy_adapter = enable_legacy_adapter
        self._legacy_service = None

        # 获取数据服务
        self.data_service = None

        # 初始化
        self._init_dependencies()

        logger.info("✅ ResearchStockService初始化完成")

    def _init_dependencies(self):
        """初始化依赖服务"""
        try:
            from .data_service import get_research_data_service
            self.data_service = get_research_data_service()
            logger.debug("✅ 数据服务依赖已注入")
        except Exception as e:
            logger.warning(f"⚠️ 数据服务依赖注入失败: {e}")

        # 初始化缓存服务
        try:
            from .data_cache_service import get_data_cache_service
            self.cache_service = get_data_cache_service()
            logger.debug("✅ 缓存服务依赖已注入")
        except Exception as e:
            logger.warning(f"⚠️ 缓存服务依赖注入失败: {e}")
            self.cache_service = None

        # 初始化旧系统适配器
        if self.enable_legacy_adapter:
            try:
                from api.api_layer.services.business.stock_service import StockService as LegacyStockService
                self._legacy_service = LegacyStockService()
                logger.info("✅ 旧系统StockService适配器已加载")
            except Exception as e:
                logger.warning(f"⚠️ 旧系统StockService适配器加载失败: {e}")

    # ==================== 公共API接口 ====================

    async def get_stock_info(self, code: str) -> Optional[StockInfo]:
        """
        获取股票信息

        Args:
            code: 股票代码（支持多种格式，自动转换为标准格式）

        Returns:
            StockInfo对象
        """
        # 如果启用旧系统适配器
        if self._legacy_service and self.enable_legacy_adapter:
            try:
                legacy_info = self._legacy_service.get_stock_info(code)
                if legacy_info:
                    # 转换为新的StockInfo对象
                    return StockInfo(
                        symbol=legacy_info.get('symbol', code),
                        name=legacy_info.get('name', ''),
                        market=self._parse_market(code),
                        industry=legacy_info.get('industry'),
                        list_date=legacy_info.get('list_date'),
                        current_price=legacy_info.get('current_price', 0.0),
                        pre_close=legacy_info.get('pre_close', 0.0),
                        change=legacy_info.get('change', 0.0),
                        change_percent=legacy_info.get('change_percent', 0.0),
                        volume=legacy_info.get('volume', 0.0),
                        amount=legacy_info.get('amount', 0.0),
                        market_cap=legacy_info.get('market_cap'),
                        pe_ratio=legacy_info.get('pe_ratio'),
                        pb_ratio=legacy_info.get('pb_ratio'),
                    )
            except Exception as e:
                logger.warning(f"旧系统适配器获取股票信息失败: {e}")

        # 实现新的股票信息获取逻辑
        # 数据优先级：
        # 1. Redis缓存（最新行情）- key: stock:info:{code}
        # 2. QLib股票池（基础信息）- ~/data/qlib_data/instruments/
        # 3. 通达信本地数据（日线行情）

        # 框架代码（待数据源完善后启用）:
        # try:
        #     # 1. 从Redis获取缓存的股票信息
        #     cached_info = await self._get_from_cache(f"stock:info:{code}")
        #     if cached_info:
        #         return StockInfo(**cached_info)
        #
        #     # 2. 从QLib获取基础信息
        #     instrument_info = await self._get_from_qlib(code)
        #     if instrument_info:
        #         # 3. 获取最新行情
        #         quote = await self._get_realtime_quote([code])
        #         return StockInfo(
        #             symbol=code,
        #             name=instrument_info['name'],
        #             market=instrument_info['market'],
        #             industry=instrument_info['industry'],
        #             list_date=instrument_info['list_date'],
        #             current_price=quote.get('price', 0),
        #             pre_close=quote.get('pre_close', 0),
        #             change=quote.get('change', 0),
        #             change_percent=quote.get('change_percent', 0),
        #             volume=quote.get('volume', 0),
        #             amount=quote.get('amount', 0)
        #         )
        #
        #     # 缓存到Redis（30秒）
        #     await self._save_to_cache(f"stock:info:{code}", stock_info.__dict__, 30)
        #
        # except Exception as e:
        #     logger.error(f"新实现获取股票信息失败: {e}")

        return None

    async def get_stock_list(
        self,
        page: int = 1,
        size: int = 20,
        market: Optional[str] = None,
        sector: Optional[str] = None,
        industry: Optional[str] = None,
        search: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        获取股票列表

        Args:
            page: 页码（从1开始）
            size: 每页大小
            market: 市场筛选（SH/SZ/全部）
            sector: 板块筛选
            industry: 行业筛选
            search: 搜索关键词（股票代码或名称）

        Returns:
            {
                "total": 总数,
                "page": 当前页,
                "size": 每页大小,
                "data": [StockInfo对象列表]
            }
        """
        if self._legacy_service and self.enable_legacy_adapter:
            try:
                legacy_result = self._legacy_service.get_stock_list(
                    page=page,
                    size=size,
                    market=market,
                    sector=sector
                )
                return legacy_result
            except Exception as e:
                logger.warning(f"旧系统适配器获取股票列表失败: {e}")

        # 实现新的股票列表查询逻辑
        # 数据源：
        # 1. QLib股票池 - ~/data/qlib_data/instruments/all_stocks.csv
        # 2. Redis缓存 - stock:list:all
        # 3. 数据库 - stock_info表

        # 框架代码（待数据源完善后启用）:
        # try:
        #     # 1. 从Redis获取缓存的股票列表
        #     cached_list = await self._get_from_cache("stock:list:all")
        #     if cached_list:
        #         total = len(cached_list)
        #         start = (page - 1) * size
        #         end = start + size
        #         return {
        #             "total": total,
        #             "page": page,
        #             "size": size,
        #             "data": cached_list[start:end]
        #         }
        #
        #     # 2. 从QLib加载股票池
        #     all_stocks = await self._load_stocks_from_qlib()
        #     if market:
        #         all_stocks = [s for s in all_stocks if s['market'] == market]
        #     if industry:
        #         all_stocks = [s for s in all_stocks if s['industry'] == industry]
        #     if search:
        #         all_stocks = [s for s in all_stocks if search in s['name'] or search in s['symbol']]
        #
        #     # 缓存到Redis（5分钟）
        #     await self._save_to_cache("stock:list:all", all_stocks, 300)
        #
        #     # 分页返回
        #     total = len(all_stocks)
        #     start = (page - 1) * size
        #     end = start + size
        #     return {
        #         "total": total,
        #         "page": page,
        #         "size": size,
        #         "data": all_stocks[start:end]
        #     }
        #
        # except Exception as e:
        #     logger.error(f"新实现获取股票列表失败: {e}")

        return {
            "total": 0,
            "page": page,
            "size": size,
            "data": []
        }

    async def get_stock_history(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
        frequency: str = "day"
    ) -> Optional[pd.DataFrame]:
        """
        获取股票历史数据

        Args:
            symbol: 股票代码
            start_date: 开始日期（YYYY-MM-DD）
            end_date: 结束日期（YYYY-MM-DD）
            frequency: 频率（day/week/month/1min/5min等）

        Returns:
            K线数据DataFrame
        """
        if self.data_service:
            try:
                return await self.data_service.get_kline_data(
                    symbol=symbol,
                    period=frequency,
                    start_date=start_date,
                    end_date=end_date
                )
            except Exception as e:
                logger.error(f"获取历史数据失败: {e}")

        return None

    async def get_stock_indicators(
        self,
        symbol: str,
        indicators: List[str]
    ) -> Dict[str, Any]:
        """
        获取股票技术指标

        Args:
            symbol: 股票代码
            indicators: 指标列表（如 ['MA5', 'MA10', 'MACD', 'KDJ']）

        Returns:
            指标数据字典
        """
        # 实现技术指标计算
        # 使用已有的indicator_service
        try:
            from .indicators import get_indicator_service
            indicator_svc = get_indicator_service()

            # 获取K线数据
            kline_df = await self.get_market_data(
                symbol=symbol,
                period=period,
                start_date=start_date,
                end_date=end_date
            )

            if kline_df is None or kline_df.empty:
                logger.warning(f"无法获取K线数据: {symbol}")
                return {}

            # 计算指标
            result = {}
            for ind_name in indicators:
                try:
                    if ind_name == "MA":
                        ma5 = kline_df['close'].rolling(window=5).mean()
                        ma10 = kline_df['close'].rolling(window=10).mean()
                        ma20 = kline_df['close'].rolling(window=20).mean()
                        result[ind_name] = {
                            "MA5": ma5.tolist()[-1] if len(ma5) > 0 else None,
                            "MA10": ma10.tolist()[-1] if len(ma10) > 0 else None,
                            "MA20": ma20.tolist()[-1] if len(ma20) > 0 else None
                        }
                    elif ind_name == "RSI":
                        delta = kline_df['close'].diff()
                        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                        rs = gain / loss
                        rsi = 100 - (100 / (1 + rs))
                        result[ind_name] = {"RSI": rsi.tolist()[-1] if len(rsi) > 0 else None}
                    # TODO: 添加更多指标计算
                    else:
                        logger.warning(f"未知指标: {ind_name}")
                except Exception as e:
                    logger.warning(f"计算指标 {ind_name} 失败: {e}")

            return result

        except ImportError:
            logger.warning("indicator_service不可用，无法计算技术指标")
            return {}
        except Exception as e:
            logger.error(f"技术指标计算失败: {e}")
            return {}

    async def screen_stocks(
        self,
        filters: Dict[str, Any]
    ) -> List[StockInfo]:
        """
        股票筛选

        Args:
            filters: 筛选条件
                {
                    "market": "SH",           # 市场
                    "industry": "银行",        # 行业
                    "min_price": 10.0,        # 最低价格
                    "max_price": 50.0,        # 最高价格
                    "min_pe": 0.0,            # 最低PE
                    "max_pe": 30.0,           # 最高PE
                    "min_market_cap": 100,    # 最小市值（亿）
                }

        Returns:
            符合条件的股票列表
        """
        # 实现股票筛选逻辑
        # 支持的筛选条件：
        # - 行业筛选
        # - 市值筛选
        # - 价格筛选
        # - 涨跌幅筛选
        # - 技术指标筛选

        # 框架代码（待数据源完善后启用）:
        # try:
        #     # 1. 获取所有股票列表
        #     all_stocks = await self.get_stock_list(page=1, size=10000)
        #     stock_list = all_stocks.get('data', [])
        #
        #     # 2. 应用筛选条件
        #     filtered = []
        #     for stock in stock_list:
        #         match = True
        #
        #         # 行业筛选
        #         if 'industry' in filters:
        #             if stock.get('industry') not in filters['industry']:
        #                 match = False
        #
        #         # 市值筛选
        #         if 'market_cap_min' in filters or 'market_cap_max' in filters:
        #             market_cap = stock.get('market_cap', 0)
        #             if 'market_cap_min' in filters and market_cap < filters['market_cap_min']:
        #                 match = False
        #             if 'market_cap_max' in filters and market_cap > filters['market_cap_max']:
        #                 match = False
        #
        #         # 价格筛选
        #         if 'price_min' in filters or 'price_max' in filters:
        #             price = stock.get('current_price', 0)
        #             if 'price_min' in filters and price < filters['price_min']:
        #                 match = False
        #             if 'price_max' in filters and price > filters['price_max']:
        #                 match = False
        #
        #         # 涨跌幅筛选
        #         if 'change_percent_min' in filters or 'change_percent_max' in filters:
        #             change_percent = stock.get('change_percent', 0)
        #             if 'change_percent_min' in filters and change_percent < filters['change_percent_min']:
        #                 match = False
        #             if 'change_percent_max' in filters and change_percent > filters['change_percent_max']:
        #                 match = False
        #
        #         if match:
        #             filtered.append(stock)
        #
        #     return filtered
        #
        # except Exception as e:
        #     logger.error(f"股票筛选失败: {e}")

        logger.warning(f"股票筛选功能尚未实现: {filters}")
        return []

    def _parse_market(self, code: str) -> str:
        """
        从股票代码解析市场

        Args:
            code: 股票代码

        Returns:
            市场代码（SH/SZ）
        """
        code = code.upper()
        if code.endswith('.SH') or code.startswith('6'):
            return 'SH'
        elif code.endswith('.SZ') or code.startswith(('0', '3')):
            return 'SZ'
        else:
            return 'UNKNOWN'

    def _format_stock_code(self, code: str) -> str:
        """
        格式化股票代码为标准格式

        Args:
            code: 股票代码

        Returns:
            标准格式代码（如 000001.SZ）
        """
        code = code.strip().upper()

        # 如果已经有后缀，直接返回
        if '.' in code:
            return code

        # 根据代码规则添加后缀
        if code.startswith('6'):
            return f"{code}.SH"
        elif code.startswith(('0', '3')):
            return f"{code}.SZ"
        else:
            # 无法识别，默认SH
            return f"{code}.SH"


    async def search_stocks_by_name(
        self,
        query: str,
        limit: int = 20,
        search_type: str = "all"
    ) -> List[Dict[str, Any]]:
        """
        按中文名称/拼音搜索股票

        Args:
            query: 搜索关键词（中文/拼音首字母/拼音完整）
            limit: 返回结果数量限制
            search_type: 搜索类型（exact/prefix/fuzzy/all）
                - exact: 精确匹配
                - prefix: 前缀匹配（拼音首字母）
                - fuzzy: 模糊匹配
                - all: 全部匹配方式

        Returns:
            匹配的股票列表

        Examples:
            >>> await service.search_stocks_by_name("平安")
            >>> await service.search_stocks_by_name("pa")  # 拼音首字母
            >>> await service.search_stocks_by_name("zgpa")  # 中国平安
        """
        from .stock_search import get_stock_search_engine

        logger.info(f"[股票搜索] 查询='{query}', 类型={search_type}, 限制={limit}")

        try:
            # 获取搜索引擎
            search_engine = get_stock_search_engine()

            # 确保索引已构建（优先从缓存加载）
            if not search_engine.stock_index:
                # 获取所有股票列表来构建索引
                all_stocks_result = await self.get_stock_list(page=1, size=5000)
                all_stocks = all_stocks_result.get('data', [])

                if all_stocks:
                    # 转换为搜索引擎需要的格式
                    stocks_for_index = []
                    for stock in all_stocks:
                        if hasattr(stock, 'dict'):
                            stock_dict = stock.dict()
                        elif isinstance(stock, dict):
                            stock_dict = stock
                        else:
                            continue

                        if 'symbol' in stock_dict and 'name' in stock_dict:
                            stocks_for_index.append(stock_dict)

                    # 使用新的 ensure_index 方法（支持缓存）
                    await search_engine.ensure_index(stocks_for_index)
                    logger.info(f"[股票搜索] 索引就绪，股票数: {len(stocks_for_index)}")

            # 执行搜索
            results = search_engine.search(
                query=query,
                limit=limit,
                search_type=search_type
            )

            logger.info(f"[股票搜索] 查询='{query}', 结果数: {len(results)}")

            return results

        except Exception as e:
            logger.error(f"[股票搜索] 搜索失败: {e}")
            return []

    async def suggest_stocks(
        self,
        query: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        智能联想股票

        Args:
            query: 搜索关键词
            limit: 返回建议数量

        Returns:
            建议的股票列表（包含match_type和match_score）
        """
        from .stock_search import get_stock_search_engine

        logger.info(f"[股票联想] 查询='{query}', 限制={limit}")

        try:
            search_engine = get_stock_search_engine()

            # 确保索引已构建（优先从缓存加载）
            if not search_engine.stock_index:
                all_stocks_result = await self.get_stock_list(page=1, size=5000)
                all_stocks = all_stocks_result.get('data', [])

                if all_stocks:
                    stocks_for_index = []
                    for stock in all_stocks:
                        if hasattr(stock, 'dict'):
                            stock_dict = stock.dict()
                        elif isinstance(stock, dict):
                            stock_dict = stock
                        else:
                            continue

                        if 'symbol' in stock_dict and 'name' in stock_dict:
                            stocks_for_index.append(stock_dict)

                    # 使用新的 ensure_index 方法（支持缓存）
                    await search_engine.ensure_index(stocks_for_index)

            # 执行联想
            suggestions = search_engine.suggest(query=query, limit=limit)

            logger.info(f"[股票联想] 查询='{query}', 建议数: {len(suggestions)}")

            return suggestions

        except Exception as e:
            logger.error(f"[股票联想] 联想失败: {e}")
            return []


# ==================== 全局单例 ====================

_research_stock_service_instance: Optional[ResearchStockService] = None


def get_research_stock_service() -> ResearchStockService:
    """
    获取Research股票服务单例

    Returns:
        ResearchStockService实例
    """
    global _research_stock_service_instance

    if _research_stock_service_instance is None:
        _research_stock_service_instance = ResearchStockService()

    return _research_stock_service_instance

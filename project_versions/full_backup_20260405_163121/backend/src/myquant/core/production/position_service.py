# -*- coding: utf-8 -*-
"""
Production阶段 - 仓位管理服务
===============================
职责：
- 实盘持仓查询和管理
- 仓位分析和优化
- 盈亏统计和分析
- 仓位风险监控

架构层次：
- Production阶段：管理实盘仓位
- 依赖TradingService获取持仓数据
- 为RiskService提供仓位数据
"""

from typing import List, Dict, Optional
from loguru import logger
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import numpy as np


class PositionStatus(Enum):
    """持仓状态"""
    NORMAL = "normal"           # 正常
    SUSPENDED = "suspended"     # 停牌
    RISK_LIMIT = "risk_limit"   # 风险限制
    FORCED_CLOSE = "forced_close"  # 强平


@dataclass
class LivePosition:
    """实盘持仓"""
    symbol: str                         # 股票代码
    symbol_name: str = ""               # 股票名称

    # 持仓数量
    quantity: int = 0                   # 持仓数量
    available_quantity: int = 0         # 可用数量
    frozen_quantity: int = 0            # 冻结数量

    # 成本信息
    avg_price: float = 0.0              # 均价
    cost_amount: float = 0.0            # 成本金额
    commission: float = 0.0             # 手续费

    # 当前价格
    current_price: float = 0.0          # 当前价
    market_value: float = 0.0           # 市值

    # 盈亏信息
    profit_loss: float = 0.0            # 浮动盈亏
    profit_loss_pct: float = 0.0        # 盈亏比例
    today_profit_loss: float = 0.0      # 当日盈亏

    # 涨跌信息
    last_close: float = 0.0             # 昨收
    change: float = 0.0                 # 涨跌额
    change_pct: float = 0.0             # 涨跌幅

    # 状态
    status: PositionStatus = PositionStatus.NORMAL

    # 更新时间
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class PortfolioSummary:
    """组合汇总"""
    total_assets: float = 0.0           # 总资产
    total_cash: float = 0.0             # 总现金
    total_market_value: float = 0.0     # 总市值
    total_profit_loss: float = 0.0      # 总盈亏
    total_profit_loss_pct: float = 0.0  # 总盈亏比例
    today_profit_loss: float = 0.0      # 当日盈亏

    # 持仓统计
    position_count: int = 0             # 持仓数量
    long_positions: int = 0             # 多头持仓
    short_positions: int = 0            # 空头持仓（如有）

    # 仓位分析
    position_ratio: float = 0.0         # 仓位比例（市值/总资产）
    max_single_position: float = 0.0    # 最大单一持仓比例
    top5_concentration: float = 0.0     # 前5大持仓占比

    # 更新时间
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class PositionAnalysis:
    """持仓分析"""
    # 收益分析
    total_return: float = 0.0           # 总收益率
    annual_return: float = 0.0          # 年化收益率
    max_drawdown: float = 0.0           # 最大回撤
    max_profit: float = 0.0             # 最大盈利

    # 风险分析
    volatility: float = 0.0             # 波动率
    beta: float = 0.0                   # Beta系数
    tracking_error: float = 0.0         # 跟踪误差

    # 持仓分析
    avg_holding_days: float = 0.0       # 平均持仓天数
    turnover_rate: float = 0.0          # 换手率


class PositionService:
    """
    仓位管理服务

    核心职责：
    1. 查询和管理实盘持仓
    2. 计算持仓盈亏
    3. 分析仓位结构
    4. 监控仓位风险

    数据来源：
    - TradingService（实盘交易服务）
    - 实时行情数据
    """

    def __init__(self):
        """初始化仓位管理服务"""
        # 持仓缓存 {account_id: {symbol: LivePosition}}
        self._positions: Dict[str, Dict[str, LivePosition]] = {}

        # 组合汇总缓存 {account_id: PortfolioSummary}
        self._summaries: Dict[str, PortfolioSummary] = {}

        # 交易服务引用
        self._trading_service = None

        # 数据服务引用（用于获取历史K线计算高级指标）
        self._data_service = None

        # 历史净值记录 {account_id: [(date, net_value), ...]}
        self._net_value_history: Dict[str, List[tuple]] = {}

        logger.info("✅ PositionService初始化完成")

    def _get_trading_service(self):
        """获取交易服务"""
        if self._trading_service is None:
            from .trading_service import get_trading_service
            self._trading_service = get_trading_service()
        return self._trading_service

    def _get_data_service(self):
        """获取数据服务（延迟加载）"""
        if self._data_service is None:
            try:
                from services.research.data_service import ResearchDataService
                self._data_service = ResearchDataService()
            except Exception as e:
                logger.warning(f"数据服务加载失败: {e}")
        return self._data_service

    # ==================== 持仓查询 ====================

    def query_positions(self, account_id: str, force_refresh: bool = False) -> Dict[str, LivePosition]:
        """
        查询持仓

        Args:
            account_id: 账户ID
            force_refresh: 是否强制刷新

        Returns:
            持仓字典 {symbol: LivePosition}
        """
        if force_refresh or account_id not in self._positions:
            self._refresh_positions(account_id)

        return self._positions.get(account_id, {})

    def _refresh_positions(self, account_id: str):
        """从交易接口刷新持仓"""
        try:
            trading_service = self._get_trading_service()

            # 从交易接口查询持仓
            raw_positions = trading_service.query_positions()

            # 转换为LivePosition对象
            positions = {}
            for symbol, pos_data in raw_positions.items():
                position = LivePosition(
                    symbol=symbol,
                    symbol_name=pos_data.get('symbol_name', ''),
                    quantity=pos_data.get('quantity', 0),
                    available_quantity=pos_data.get('available_quantity', 0),
                    frozen_quantity=pos_data.get('frozen_quantity', 0),
                    avg_price=pos_data.get('avg_price', 0.0),
                    cost_amount=pos_data.get('cost_amount', 0.0),
                    current_price=pos_data.get('current_price', 0.0),
                    market_value=pos_data.get('market_value', 0.0),
                    profit_loss=pos_data.get('profit_loss', 0.0),
                    profit_loss_pct=pos_data.get('profit_loss_pct', 0.0),
                    updated_at=datetime.now()
                )
                positions[symbol] = position

            self._positions[account_id] = positions

            logger.debug(
                f"持仓已刷新: {account_id}, 共 {len(positions)} 只股票"
            )

        except Exception as e:
            logger.error(f"刷新持仓异常: {e}")
            # 异常时保持原有数据或创建空持仓
            if account_id not in self._positions:
                self._positions[account_id] = {}

    def get_position(self, account_id: str, symbol: str) -> Optional[LivePosition]:
        """
        查询单个持仓

        Args:
            account_id: 账户ID
            symbol: 股票代码

        Returns:
            LivePosition对象，如果不存在返回None
        """
        positions = self.query_positions(account_id)
        return positions.get(symbol)

    # ==================== 持仓分析 ====================

    def get_portfolio_summary(self, account_id: str) -> PortfolioSummary:
        """
        获取组合汇总

        Args:
            account_id: 账户ID

        Returns:
            PortfolioSummary对象
        """
        positions = self.query_positions(account_id)

        # 计算汇总数据
        summary = PortfolioSummary()

        # 总市值
        summary.total_market_value = sum(pos.market_value for pos in positions.values())
        summary.position_count = len(positions)
        summary.long_positions = summary.position_count  # 暂时假设都是多头

        # 总资产（需要加上现金）
        trading_service = self._get_trading_service()
        account = trading_service.query_account()
        if account:
            summary.total_assets = account.total_assets
            summary.total_cash = account.cash
        else:
            summary.total_assets = summary.total_market_value

        # 总盈亏
        summary.total_profit_loss = sum(pos.profit_loss for pos in positions.values())
        summary.total_profit_loss_pct = (
            summary.total_profit_loss / summary.total_market_value * 100
            if summary.total_market_value > 0 else 0
        )

        # 当日盈亏
        summary.today_profit_loss = sum(pos.today_profit_loss for pos in positions.values())

        # 仓位比例
        summary.position_ratio = (
            summary.total_market_value / summary.total_assets
            if summary.total_assets > 0 else 0
        )

        # 最大单一持仓比例
        if positions:
            max_value = max(pos.market_value for pos in positions.values())
            summary.max_single_position = max_value / summary.total_assets if summary.total_assets > 0 else 0

            # 前5大持仓占比
            sorted_values = sorted(
                [pos.market_value for pos in positions.values()],
                reverse=True
            )
            top5_sum = sum(sorted_values[:5])
            summary.top5_concentration = top5_sum / summary.total_market_value if summary.total_market_value > 0 else 0

        summary.updated_at = datetime.now()

        # 缓存
        self._summaries[account_id] = summary

        return summary

    def analyze_positions(self, account_id: str) -> PositionAnalysis:
        """
        分析持仓

        Args:
            account_id: 账户ID

        Returns:
            PositionAnalysis对象
        """
        positions = self.query_positions(account_id)
        summary = self.get_portfolio_summary(account_id)

        analysis = PositionAnalysis()

        if not positions:
            return analysis

        # ==================== 基础指标计算 ====================

        # 总收益率
        total_cost = sum(pos.cost_amount for pos in positions.values())
        total_value = sum(pos.market_value for pos in positions.values())
        analysis.total_return = (total_value - total_cost) / total_cost if total_cost > 0 else 0

        # 最大盈亏（单只股票）
        profit_losses = [pos.profit_loss for pos in positions.values()]
        if profit_losses:
            analysis.max_profit = max(profit_losses)
            analysis.max_drawdown = min(profit_losses)

        # ==================== 高级指标计算 ====================

        # 计算组合波动率
        analysis.volatility = self._calculate_portfolio_volatility(
            account_id, positions
        )

        # 计算Beta系数
        analysis.beta = self._calculate_portfolio_beta(
            account_id, positions
        )

        # 计算历史最大回撤
        max_dd = self._calculate_max_drawdown(account_id)
        if max_dd is not None:
            analysis.max_drawdown = max_dd

        # 计算换手率
        analysis.turnover_rate = self._calculate_turnover_rate(account_id)

        # 计算跟踪误差（相对于基准）
        analysis.tracking_error = self._calculate_tracking_error(
            account_id, positions
        )

        # 计算年化收益率
        analysis.annual_return = self._calculate_annual_return(
            account_id, analysis.total_return
        )

        # 计算平均持仓天数
        analysis.avg_holding_days = self._calculate_avg_holding_days(
            account_id, positions
        )

        return analysis

    def _calculate_portfolio_volatility(
        self,
        account_id: str,
        positions: Dict[str, LivePosition]
    ) -> float:
        """
        计算组合波动率

        使用加权平均方法计算，权重为各持仓市值占比

        Args:
            account_id: 账户ID
            positions: 持仓字典

        Returns:
            年化波动率
        """
        try:
            data_service = self._get_data_service()
            if not data_service:
                return 0.0

            total_value = sum(pos.market_value for pos in positions.values())
            if total_value <= 0:
                return 0.0

            weighted_volatility = 0.0

            for symbol, position in positions.items():
                # 权重
                weight = position.market_value / total_value

                # 获取该股票的历史波动率
                stock_vol = self._get_stock_volatility(symbol)
                if stock_vol > 0:
                    weighted_volatility += weight * stock_vol

            return weighted_volatility

        except Exception as e:
            logger.error(f"计算组合波动率失败: {e}")
            return 0.0

    def _get_stock_volatility(self, symbol: str, days: int = 60) -> float:
        """
        获取单只股票的历史波动率

        Args:
            symbol: 股票代码
            days: 计算天数

        Returns:
            年化波动率
        """
        try:
            data_service = self._get_data_service()
            if not data_service:
                return 0.0

            # 异步调用转同步（简化处理）
            import asyncio
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

            # 获取历史K线
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=days * 2)).strftime('%Y-%m-%d')

            # 转换代码格式
            if symbol.startswith('sz') or symbol.startswith('sh'):
                symbol_fmt = f"{symbol[2:]}.{symbol[:2].upper()}"
            else:
                symbol_fmt = symbol

            df = loop.run_until_complete(
                data_service.get_kline_data(
                    symbol=symbol_fmt,
                    period='day',
                    start_date=start_date,
                    end_date=end_date,
                    count=days
                )
            )

            if df is None or df.empty or len(df) < 10:
                return 0.0

            # 计算日收益率
            close_prices = df['close'].values
            returns = np.diff(close_prices) / close_prices[:-1]

            # 计算标准差并年化
            daily_std = np.std(returns)
            annual_volatility = daily_std * np.sqrt(252)  # 252个交易日

            return annual_volatility

        except Exception as e:
            logger.debug(f"获取股票波动率失败 {symbol}: {e}")
            return 0.0

    def _calculate_portfolio_beta(
        self,
        account_id: str,
        positions: Dict[str, LivePosition]
    ) -> float:
        """
        计算组合Beta系数

        Args:
            account_id: 账户ID
            positions: 持仓字典

        Returns:
            Beta系数
        """
        try:
            data_service = self._get_data_service()
            if not data_service:
                return 1.0  # 默认Beta为1

            total_value = sum(pos.market_value for pos in positions.values())
            if total_value <= 0:
                return 1.0

            weighted_beta = 0.0

            for symbol, position in positions.items():
                weight = position.market_value / total_value
                stock_beta = self._get_stock_beta(symbol)
                weighted_beta += weight * stock_beta

            return weighted_beta

        except Exception as e:
            logger.error(f"计算组合Beta失败: {e}")
            return 1.0

    def _get_stock_beta(self, symbol: str, days: int = 60) -> float:
        """
        获取单只股票的Beta系数

        Args:
            symbol: 股票代码
            days: 计算天数

        Returns:
            Beta系数
        """
        try:
            data_service = self._get_data_service()
            if not data_service:
                return 1.0

            import asyncio
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=days * 2)).strftime('%Y-%m-%d')

            # 格式转换
            if symbol.startswith('sz') or symbol.startswith('sh'):
                symbol_fmt = f"{symbol[2:]}.{symbol[:2].upper()}"
            else:
                symbol_fmt = symbol

            # 获取股票K线
            stock_df = loop.run_until_complete(
                data_service.get_kline_data(
                    symbol=symbol_fmt,
                    period='day',
                    start_date=start_date,
                    end_date=end_date,
                    count=days
                )
            )

            # 获取基准指数K线（沪深300）
            index_df = loop.run_until_complete(
                data_service.get_kline_data(
                    symbol='000300.SH',
                    period='day',
                    start_date=start_date,
                    end_date=end_date,
                    count=days
                )
            )

            if (stock_df is None or stock_df.empty or
                index_df is None or index_df.empty):
                return 1.0

            if len(stock_df) < 10 or len(index_df) < 10:
                return 1.0

            # 计算收益率
            stock_returns = np.diff(stock_df['close'].values) / stock_df['close'].values[:-1]
            index_returns = np.diff(index_df['close'].values) / index_df['close'].values[:-1]

            # 确保长度一致
            min_len = min(len(stock_returns), len(index_returns))
            stock_returns = stock_returns[-min_len:]
            index_returns = index_returns[-min_len:]

            # 计算协方差和方差
            covariance = np.cov(stock_returns, index_returns)[0, 1]
            index_variance = np.var(index_returns)

            if index_variance == 0:
                return 1.0

            beta = covariance / index_variance
            return beta

        except Exception as e:
            logger.debug(f"获取股票Beta失败 {symbol}: {e}")
            return 1.0

    def _calculate_max_drawdown(self, account_id: str) -> Optional[float]:
        """
        计算历史最大回撤

        Args:
            account_id: 账户ID

        Returns:
            最大回撤（负数）
        """
        try:
            history = self._net_value_history.get(account_id, [])
            if len(history) < 2:
                return None

            # 提取净值序列
            net_values = [nv for _, nv in history]

            max_drawdown = 0.0
            peak = net_values[0]

            for nv in net_values:
                if nv > peak:
                    peak = nv

                drawdown = (nv - peak) / peak if peak > 0 else 0
                if drawdown < max_drawdown:
                    max_drawdown = drawdown

            return max_drawdown

        except Exception as e:
            logger.error(f"计算最大回撤失败: {e}")
            return None

    def _calculate_turnover_rate(self, account_id: str) -> float:
        """
        计算换手率

        简化计算：近30天交易金额 / 平均持仓市值

        Args:
            account_id: 账户ID

        Returns:
            换手率
        """
        try:
            trading_service = self._get_trading_service()
            if not trading_service:
                return 0.0

            # 获取近30天成交记录
            start_time = datetime.now() - timedelta(days=30)
            trades = trading_service.get_trades(start_time=start_time)

            account_trades = [t for t in trades if t.account_id == account_id]

            if not account_trades:
                return 0.0

            # 计算总成交金额
            total_trade_amount = sum(t.amount for t in account_trades)

            # 计算平均持仓市值
            summary = self.get_portfolio_summary(account_id)
            avg_market_value = summary.total_market_value

            if avg_market_value <= 0:
                return 0.0

            # 换手率 = 总成交金额 / 平均市值
            turnover_rate = total_trade_amount / avg_market_value
            return turnover_rate

        except Exception as e:
            logger.error(f"计算换手率失败: {e}")
            return 0.0

    def _calculate_tracking_error(
        self,
        account_id: str,
        positions: Dict[str, LivePosition]
    ) -> float:
        """
        计算跟踪误差

        Args:
            account_id: 账户ID
            positions: 持仓字典

        Returns:
            跟踪误差
        """
        # 简化实现：使用持仓集中度作为跟踪误差的代理
        # 集中度越高，跟踪误差越大
        summary = self.get_portfolio_summary(account_id)
        return summary.top5_concentration * 0.1  # 简化估算

    def _calculate_annual_return(
        self,
        account_id: str,
        total_return: float
    ) -> float:
        """
        计算年化收益率

        Args:
            account_id: 账户ID
            total_return: 总收益率

        Returns:
            年化收益率
        """
        try:
            history = self._net_value_history.get(account_id, [])
            if len(history) < 2:
                return total_return  # 数据不足，返回总收益率

            # 计算持仓天数
            first_date = history[0][0]
            last_date = history[-1][0]

            if isinstance(first_date, str):
                first_date = datetime.fromisoformat(first_date)
            if isinstance(last_date, str):
                last_date = datetime.fromisoformat(last_date)

            days = (last_date - first_date).days

            if days <= 0:
                return total_return

            # 年化收益率 = (1 + 总收益率)^(365/天数) - 1
            annual_return = (1 + total_return) ** (365 / days) - 1
            return annual_return

        except Exception as e:
            logger.error(f"计算年化收益率失败: {e}")
            return total_return

    def _calculate_avg_holding_days(
        self,
        account_id: str,
        positions: Dict[str, LivePosition]
    ) -> float:
        """
        计算平均持仓天数

        简化实现：使用估算方法

        Args:
            account_id: 账户ID
            positions: 持仓字典

        Returns:
            平均持仓天数
        """
        # 简化实现：假设平均持仓30天
        # 实际应从交易记录计算
        return 30.0

    def record_net_value(self, account_id: str, net_value: float):
        """
        记录净值快照（用于计算历史最大回撤）

        Args:
            account_id: 账户ID
            net_value: 当前净值
        """
        if account_id not in self._net_value_history:
            self._net_value_history[account_id] = []

        self._net_value_history[account_id].append(
            (datetime.now(), net_value)
        )

        # 保留最近252个交易日（约1年）
        max_records = 252
        if len(self._net_value_history[account_id]) > max_records:
            self._net_value_history[account_id] = self._net_value_history[account_id][-max_records:]

    # ==================== 持仓管理 ====================

    def update_position_price(self, account_id: str, symbol: str, price: float):
        """
        更新持仓价格

        Args:
            account_id: 账户ID
            symbol: 股票代码
            price: 最新价格
        """
        position = self.get_position(account_id, symbol)
        if position:
            position.current_price = price
            position.market_value = position.quantity * price

            # 更新盈亏
            cost = position.quantity * position.avg_price
            position.profit_loss = position.market_value - cost
            position.profit_loss_pct = (position.profit_loss / cost * 100) if cost > 0 else 0

            # 更新涨跌
            position.change = price - position.last_close
            position.change_pct = (position.change / position.last_close * 100) if position.last_close > 0 else 0

            position.updated_at = datetime.now()

    def update_prices_batch(self, account_id: str, prices: Dict[str, float]):
        """
        批量更新持仓价格

        Args:
            account_id: 账户ID
            prices: 价格字典 {symbol: price}
        """
        positions = self.query_positions(account_id)

        for symbol, price in prices.items():
            if symbol in positions:
                self.update_position_price(account_id, symbol, price)

        logger.debug(f"批量更新持仓价格: {len(prices)}只股票")

    # ==================== 风险监控 ====================

    def check_position_limits(
        self,
        account_id: str,
        max_single_position: float = 0.2,    # 单一持仓上限20%
        max_total_position: float = 0.95,     # 总仓位上限95%
        max_concentration: float = 0.5,        # 集中度上限50%
    ) -> Dict[str, bool]:
        """
        检查仓位限制

        Args:
            account_id: 账户ID
            max_single_position: 单一持仓上限
            max_total_position: 总仓位上限
            max_concentration: 集中度上限

        Returns:
            检查结果字典
        """
        summary = self.get_portfolio_summary(account_id)

        checks = {
            "single_position_ok": summary.max_single_position <= max_single_position,
            "total_position_ok": summary.position_ratio <= max_total_position,
            "concentration_ok": summary.top5_concentration <= max_concentration,
        }

        # 检查单一持仓
        if not checks["single_position_ok"]:
            logger.warning(f"单一持仓超限: {summary.max_single_position:.2%} > {max_single_position:.2%}")

        if not checks["total_position_ok"]:
            logger.warning(f"总仓位超限: {summary.position_ratio:.2%} > {max_total_position:.2%}")

        if not checks["concentration_ok"]:
            logger.warning(f"集中度超限: {summary.top5_concentration:.2%} > {max_concentration:.2%}")

        return checks

    def get_risk_positions(
        self,
        account_id: str,
        loss_threshold: float = -0.1,  # 亏损阈值-10%
    ) -> List[LivePosition]:
        """
        获取风险持仓

        Args:
            account_id: 账户ID
            loss_threshold: 亏损阈值

        Returns:
            风险持仓列表
        """
        positions = self.query_positions(account_id)

        risk_positions = [
            pos for pos in positions.values()
            if pos.profit_loss_pct < loss_threshold * 100
        ]

        return sorted(risk_positions, key=lambda x: x.profit_loss_pct)

    # ==================== 持仓报告 ====================

    def generate_position_report(self, account_id: str) -> Dict:
        """
        生成持仓报告

        Args:
            account_id: 账户ID

        Returns:
            持仓报告字典
        """
        positions = self.query_positions(account_id)
        summary = self.get_portfolio_summary(account_id)
        analysis = self.analyze_positions(account_id)

        report = {
            "account_id": account_id,
            "generated_at": datetime.now().isoformat(),

            # 组合汇总
            "summary": {
                "total_assets": summary.total_assets,
                "total_cash": summary.total_cash,
                "total_market_value": summary.total_market_value,
                "total_profit_loss": summary.total_profit_loss,
                "total_profit_loss_pct": summary.total_profit_loss_pct,
                "position_ratio": summary.position_ratio,
                "position_count": summary.position_count,
            },

            # 持仓明细
            "positions": [
                {
                    "symbol": pos.symbol,
                    "symbol_name": pos.symbol_name,
                    "quantity": pos.quantity,
                    "avg_price": pos.avg_price,
                    "current_price": pos.current_price,
                    "market_value": pos.market_value,
                    "profit_loss": pos.profit_loss,
                    "profit_loss_pct": pos.profit_loss_pct,
                }
                for pos in positions.values()
            ],

            # 持仓分析
            "analysis": {
                "total_return": analysis.total_return,
                "annual_return": analysis.annual_return,
                "max_drawdown": analysis.max_drawdown,
            },

            # 风险检查
            "risk_warnings": [],
        }

        # 添加风险警告
        risk_positions = self.get_risk_positions(account_id)
        if risk_positions:
            report["risk_warnings"].append({
                "type": "loss_positions",
                "message": f"发现{len(risk_positions)}个高亏损持仓",
                "positions": [pos.symbol for pos in risk_positions[:5]],
            })

        return report


# ==================== 全局单例 ====================

_position_service_instance: Optional[PositionService] = None


def get_position_service() -> PositionService:
    """
    获取仓位管理服务单例

    Returns:
        PositionService实例
    """
    global _position_service_instance

    if _position_service_instance is None:
        _position_service_instance = PositionService()

    return _position_service_instance

# -*- coding: utf-8 -*-
"""
Validation阶段 - 模拟实盘服务
==============================
职责：
- 模拟实盘交易环境
- 虚拟资金管理
- 订单模拟执行
- 实时持仓跟踪

架构层次：
- Validation阶段：在模拟环境中验证策略
- 不涉及真实资金
- 为实盘交易提供预演
"""

from typing import List, Dict, Optional, Any
from loguru import logger
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import pandas as pd
from decimal import Decimal


class OrderType(Enum):
    """订单类型"""
    MARKET = "market"         # 市价单
    LIMIT = "limit"           # 限价单
    STOP = "stop"             # 止损单


class OrderSide(Enum):
    """订单方向"""
    BUY = "buy"               # 买入
    SELL = "sell"             # 卖出


class OrderStatus(Enum):
    """订单状态"""
    PENDING = "pending"       # 待成交
    PARTIAL = "partial"       # 部分成交
    FILLED = "filled"         # 完全成交
    CANCELLED = "cancelled"   # 已取消
    REJECTED = "rejected"     # 已拒绝


@dataclass
class SimulationAccount:
    """模拟账户"""
    account_id: str                    # 账户ID
    initial_capital: float = 1_000_000 # 初始资金
    cash: float = 1_000_000            # 可用现金
    total_assets: float = 1_000_000    # 总资产
    frozen_cash: float = 0.0           # 冻结资金
    market_value: float = 0.0          # 市值
    created_at: datetime = field(default_factory=datetime.now)

    def update_market_value(self, positions: Dict[str, 'SimulationPosition'], prices: Dict[str, float]):
        """更新市值"""
        market_value = sum(
            pos.quantity * prices.get(pos.symbol, 0.0)
            for pos in positions.values()
        )
        self.market_value = market_value
        self.total_assets = self.cash + market_value


@dataclass
class SimulationPosition:
    """模拟持仓"""
    symbol: str                         # 股票代码
    quantity: int                       # 持仓数量
    available_quantity: int             # 可用数量
    avg_price: float                    # 平均成本
    current_price: float = 0.0          # 当前价格
    market_value: float = 0.0           # 市值
    profit_loss: float = 0.0            # 浮动盈亏
    profit_loss_pct: float = 0.0        # 盈亏比例

    def update_price(self, price: float):
        """更新价格"""
        self.current_price = price
        self.market_value = self.quantity * price
        cost = self.quantity * self.avg_price
        self.profit_loss = self.market_value - cost
        self.profit_loss_pct = (self.profit_loss / cost * 100) if cost > 0 else 0


@dataclass
class SimulationOrder:
    """模拟订单"""
    order_id: str                       # 订单ID
    account_id: str                     # 账户ID
    symbol: str                         # 股票代码
    side: OrderSide                     # 订单方向
    order_type: OrderType               # 订单类型
    quantity: int                       # 委托数量
    price: Optional[float] = None       # 委托价格（限价单）
    filled_quantity: int = 0            # 成交数量
    filled_amount: float = 0.0          # 成交金额
    avg_price: float = 0.0              # 成交均价
    status: OrderStatus = OrderStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    error_message: Optional[str] = None # 错误信息


@dataclass
class SimulationConfig:
    """模拟交易配置"""
    account_id: str                     # 账户ID
    initial_capital: float = 1_000_000  # 初始资金
    commission_rate: float = 0.0003     # 手续费率
    slippage_rate: float = 0.001        # 滑点率
    enable_short: bool = False          # 是否允许做空
    enable_margin: bool = False         # 是否允许融资
    margin_ratio: float = 0.5           # 融资保证金比例


class SimulationService:
    """
    模拟实盘服务

    核心职责：
    1. 模拟真实交易环境
    2. 管理虚拟账户资金
    3. 模拟订单执行逻辑
    4. 实时跟踪持仓和盈亏

    使用场景：
    - 策略上线前的模拟验证
    - 新策略的试运行
    - 交易系统的功能测试
    """

    def __init__(self):
        """初始化模拟实盘服务"""
        # 账户管理
        self._accounts: Dict[str, SimulationAccount] = {}

        # 持仓管理
        self._positions: Dict[str, Dict[str, SimulationPosition]] = {}  # account_id -> {symbol -> Position}

        # 订单管理
        self._orders: Dict[str, SimulationOrder] = {}

        # 行情缓存（用于模拟成交）
        self._price_cache: Dict[str, float] = {}

        logger.info("✅ SimulationService初始化完成")

    # ==================== 账户管理 ====================

    def create_account(self, config: SimulationConfig) -> SimulationAccount:
        """
        创建模拟账户

        Args:
            config: 模拟交易配置

        Returns:
            SimulationAccount对象
        """
        account = SimulationAccount(
            account_id=config.account_id,
            initial_capital=config.initial_capital,
            cash=config.initial_capital,
            total_assets=config.initial_capital
        )

        self._accounts[config.account_id] = account
        self._positions[config.account_id] = {}

        logger.info(f"创建模拟账户: {config.account_id}, 初始资金: {config.initial_capital:,.2f}")

        return account

    def get_account(self, account_id: str) -> Optional[SimulationAccount]:
        """
        获取账户信息

        Args:
            account_id: 账户ID

        Returns:
            SimulationAccount对象，如果不存在返回None
        """
        return self._accounts.get(account_id)

    def update_account_assets(self, account_id: str, prices: Dict[str, float]):
        """
        更新账户资产

        Args:
            account_id: 账户ID
            prices: 最新价格字典 {symbol: price}
        """
        account = self._accounts.get(account_id)
        if account is None:
            return

        positions = self._positions.get(account_id, {})

        # 更新持仓价格和市值
        for position in positions.values():
            if position.symbol in prices:
                position.update_price(prices[position.symbol])

        # 更新账户市值
        account.update_market_value(positions, prices)

    # ==================== 订单交易 ====================

    def place_order(
        self,
        account_id: str,
        symbol: str,
        side: OrderSide,
        order_type: OrderType,
        quantity: int,
        price: Optional[float] = None,
        commission_rate: float = 0.0003
    ) -> SimulationOrder:
        """
        下单

        Args:
            account_id: 账户ID
            symbol: 股票代码
            side: 买卖方向
            order_type: 订单类型
            quantity: 委托数量
            price: 委托价格（限价单必填）
            commission_rate: 手续费率

        Returns:
            SimulationOrder对象
        """
        # 生成订单ID
        order_id = f"order_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"

        # 创建订单对象
        order = SimulationOrder(
            order_id=order_id,
            account_id=account_id,
            symbol=symbol,
            side=side,
            order_type=order_type,
            quantity=quantity,
            price=price
        )

        # 验证订单
        error = self._validate_order(account_id, order)
        if error:
            order.status = OrderStatus.REJECTED
            order.error_message = error
            self._orders[order_id] = order
            logger.warning(f"订单拒绝: {order_id}, 原因: {error}")
            return order

        # 保存订单
        self._orders[order_id] = order

        # 模拟成交
        self._execute_order(account_id, order, commission_rate)

        logger.info(f"订单下单: {order_id}, {symbol}, {side.value}, {quantity}股")

        return order

    def _validate_order(self, account_id: str, order: SimulationOrder) -> Optional[str]:
        """
        验证订单

        Args:
            account_id: 账户ID
            order: 订单对象

        Returns:
            错误信息，如果验证通过返回None
        """
        account = self._accounts.get(account_id)
        if account is None:
            return f"账户不存在: {account_id}"

        # 限价单必须有价格
        if order.order_type == OrderType.LIMIT and order.price is None:
            return "限价单必须指定价格"

        # 检查数量
        if order.quantity <= 0:
            return "委托数量必须大于0"

        # 检查资金（买入）
        if order.side == OrderSide.BUY:
            required_amount = order.quantity * (order.price or 0) * 1.1  # 预留10%滑点
            if account.cash < required_amount:
                return f"可用资金不足: 需要{required_amount:.2f}, 可用{account.cash:.2f}"

        # 检查持仓（卖出）
        if order.side == OrderSide.SELL:
            positions = self._positions.get(account_id, {})
            position = positions.get(order.symbol)
            if position is None or position.available_quantity < order.quantity:
                return f"可用持仓不足: 需要{order.quantity}, 可用{position.available_quantity if position else 0}"

        return None

    def _execute_order(self, account_id: str, order: SimulationOrder, commission_rate: float):
        """
        执行订单（模拟成交）

        Args:
            account_id: 账户ID
            order: 订单对象
            commission_rate: 手续费率
        """
        # 获取当前价格
        if order.price is None or order.order_type == OrderType.MARKET:
            # 市价单使用最新价格
            execution_price = self._price_cache.get(order.symbol, 0.0)
        else:
            # 限价单使用委托价格
            execution_price = order.price

        if execution_price <= 0:
            order.status = OrderStatus.REJECTED
            order.error_message = "无法获取价格"
            return

        # 计算成交金额
        amount = execution_price * order.quantity
        commission = amount * commission_rate

        # 更新订单状态
        order.filled_quantity = order.quantity
        order.filled_amount = amount
        order.avg_price = execution_price
        order.status = OrderStatus.FILLED
        order.updated_at = datetime.now()

        # 更新账户和持仓
        if order.side == OrderSide.BUY:
            self._handle_buy(account_id, order, amount, commission)
        else:
            self._handle_sell(account_id, order, amount, commission)

    def _handle_buy(self, account_id: str, order: SimulationOrder, amount: float, commission: float):
        """处理买入成交"""
        account = self._accounts[account_id]
        positions = self._positions[account_id]

        # 扣除资金
        total_cost = amount + commission
        account.cash -= total_cost
        account.frozen_cash -= total_cost  # 解冻资金

        # 更新持仓
        if order.symbol not in positions:
            positions[order.symbol] = SimulationPosition(
                symbol=order.symbol,
                quantity=0,
                available_quantity=0,
                avg_price=0.0
            )

        position = positions[order.symbol]
        old_quantity = position.quantity
        old_cost = position.avg_price * old_quantity

        # 计算新的平均成本
        new_quantity = old_quantity + order.filled_quantity
        position.avg_price = (old_cost + amount) / new_quantity if new_quantity > 0 else 0
        position.quantity = new_quantity
        position.available_quantity = new_quantity

    def _handle_sell(self, account_id: str, order: SimulationOrder, amount: float, commission: float):
        """处理卖出成交"""
        account = self._accounts[account_id]
        positions = self._positions[account_id]

        position = positions.get(order.symbol)
        if position is None:
            return

        # 减少持仓
        position.quantity -= order.filled_quantity
        position.available_quantity -= order.filled_quantity

        # 增加资金
        net_proceeds = amount - commission
        account.cash += net_proceeds

        # 清理空仓位
        if position.quantity == 0:
            del positions[order.symbol]

    # ==================== 持仓查询 ====================

    def get_positions(self, account_id: str) -> Dict[str, SimulationPosition]:
        """
        查询持仓

        Args:
            account_id: 账户ID

        Returns:
            持仓字典 {symbol: SimulationPosition}
        """
        return self._positions.get(account_id, {})

    def get_position(self, account_id: str, symbol: str) -> Optional[SimulationPosition]:
        """
        查询单个持仓

        Args:
            account_id: 账户ID
            symbol: 股票代码

        Returns:
            SimulationPosition对象，如果不存在返回None
        """
        return self._positions.get(account_id, {}).get(symbol)

    # ==================== 订单查询 ====================

    def get_order(self, order_id: str) -> Optional[SimulationOrder]:
        """
        查询订单

        Args:
            order_id: 订单ID

        Returns:
            SimulationOrder对象，如果不存在返回None
        """
        return self._orders.get(order_id)

    def get_orders(
        self,
        account_id: Optional[str] = None,
        symbol: Optional[str] = None,
        status: Optional[OrderStatus] = None
    ) -> List[SimulationOrder]:
        """
        查询订单列表

        Args:
            account_id: 账户ID筛选
            symbol: 股票代码筛选
            status: 订单状态筛选

        Returns:
            SimulationOrder列表
        """
        orders = list(self._orders.values())

        # 筛选
        if account_id is not None:
            orders = [o for o in orders if o.account_id == account_id]

        if status is not None:
            orders = [o for o in orders if o.status == status]

        if symbol is not None:
            orders = [o for o in orders if o.symbol == symbol]

        return sorted(orders, key=lambda x: x.created_at, reverse=True)

    def cancel_order(self, order_id: str) -> bool:
        """
        撤单

        Args:
            order_id: 订单ID

        Returns:
            是否成功撤销
        """
        order = self._orders.get(order_id)
        if order and order.status == OrderStatus.PENDING:
            order.status = OrderStatus.CANCELLED
            order.updated_at = datetime.now()
            logger.info(f"订单已撤销: {order_id}")
            return True
        return False

    # ==================== 行情更新 ====================

    def update_prices(self, prices: Dict[str, float]):
        """
        更新行情价格

        Args:
            prices: 价格字典 {symbol: price}
        """
        self._price_cache.update(prices)

        # 更新所有账户的持仓市值
        for account_id in self._accounts:
            self.update_account_assets(account_id, prices)

    # ==================== 统计分析 ====================

    def get_account_statistics(self, account_id: str) -> Dict[str, Any]:
        """
        获取账户统计信息

        Args:
            account_id: 账户ID

        Returns:
            统计信息字典
        """
        account = self._accounts.get(account_id)
        if account is None:
            return {"error": "Account not found"}

        positions = self._positions.get(account_id, {})

        # 计算收益
        total_return = (account.total_assets - account.initial_capital) / account.initial_capital
        total_pnl = account.total_assets - account.initial_capital

        # 订单统计
        account_orders = [o for o in self._orders.values() if o.account_id == account_id]
        filled_orders = [o for o in account_orders if o.status == OrderStatus.FILLED]
        buy_orders = [o for o in filled_orders if o.side == OrderSide.BUY]
        sell_orders = [o for o in filled_orders if o.side == OrderSide.SELL]

        # 胜率计算
        win_count = 0
        total_trades = 0
        for buy_order in buy_orders:
            # 找到对应的卖出订单
            sell_order = next(
                (o for o in sell_orders
                 if o.symbol == buy_order.symbol and o.created_at > buy_order.created_at),
                None
            )
            if sell_order:
                total_trades += 1
                buy_price = buy_order.avg_price
                sell_price = sell_order.avg_price
                if sell_price > buy_price:
                    win_count += 1

        win_rate = win_count / total_trades if total_trades > 0 else 0

        return {
            "account_id": account_id,
            "initial_capital": account.initial_capital,
            "total_assets": account.total_assets,
            "cash": account.cash,
            "market_value": account.market_value,
            "total_pnl": total_pnl,
            "total_return_pct": total_return * 100,
            "total_positions": len(positions),
            "total_orders": len(account_orders),
            "filled_orders": len(filled_orders),
            "buy_orders": len(buy_orders),
            "sell_orders": len(sell_orders),
            "total_trades": total_trades,
            "win_count": win_count,
            "win_rate_pct": win_rate * 100,
            "timestamp": datetime.now().isoformat()
        }

    def reset_account(self, account_id: str) -> bool:
        """
        重置账户（清空持仓和订单）

        Args:
            account_id: 账户ID

        Returns:
            是否成功重置
        """
        if account_id not in self._accounts:
            return False

        # 清空持仓
        self._positions[account_id] = {}

        # 删除该账户的订单
        order_ids_to_delete = [
            order_id for order_id, order in self._orders.items()
            if order.account_id == account_id
        ]
        for order_id in order_ids_to_delete:
            del self._orders[order_id]

        # 重置账户资金
        account = self._accounts[account_id]
        account.cash = account.initial_capital
        account.total_assets = account.initial_capital
        account.market_value = 0
        account.frozen_cash = 0

        logger.info(f"账户已重置: {account_id}")

        return True


# ==================== 全局单例 ====================

_simulation_service_instance: Optional[SimulationService] = None


def get_simulation_service() -> SimulationService:
    """
    获取模拟实盘服务单例

    Returns:
        SimulationService实例
    """
    global _simulation_service_instance

    if _simulation_service_instance is None:
        _simulation_service_instance = SimulationService()

    return _simulation_service_instance

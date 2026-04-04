# -*- coding: utf-8 -*-
"""
Production阶段 - 实盘交易服务
=============================
职责：
- 真实资金交易执行
- 连接券商交易接口（XtQuant/QMT）
- 实盘订单管理
- 交易状态监控

⚠️ 重要提示：
- 此Service涉及真实资金
- 所有操作需要严格的风险控制
- 建议先经过模拟实盘验证

架构层次：
- Production阶段：真实资金交易
- 不涉及数据获取（属于Research）
- 不涉及策略验证（属于Validation）
"""

from typing import List, Dict, Optional, Any
from loguru import logger
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import time
import uuid


class TradingStatus(Enum):
    """交易状态"""
    DISCONNECTED = "disconnected"   # 未连接
    CONNECTING = "connecting"       # 连接中
    CONNECTED = "connected"         # 已连接
    AUTHENTICATED = "authenticated" # 已认证
    FAILED = "failed"               # 连接失败


class OrderType(Enum):
    """订单类型"""
    MARKET = "market"         # 市价单
    LIMIT = "limit"           # 限价单
    STOP = "stop"             # 止损单


class OrderSide(Enum):
    """订单方向"""
    BUY = "buy"               # 买入
    SELL = "sell"             # 卖出


class LiveOrderStatus(Enum):
    """实盘订单状态"""
    PENDING = "pending"           # 待报
    SUBMITTED = "submitted"       # 已报
    PARTIAL = "partial"           # 部成
    FILLED = "filled"             # 已成
    CANCELLED = "cancelled"       # 已撤
    REJECTED = "rejected"         # 已撤（拒绝）
    UNKNOWN = "unknown"           # 未知


@dataclass
class TradingAccount:
    """实盘交易账户"""
    account_id: str                    # 账户ID
    account_type: str                  # 账户类型（stock/future）
    account_name: str = ""             # 账户名称

    # 资金信息
    total_assets: float = 0.0          # 总资产
    cash: float = 0.0                  # 资金可用
    frozen_cash: float = 0.0           # 冻结资金
    market_value: float = 0.0          # 证券市值
    total_loss: float = 0.0            # 总盈亏

    # 持仓信息
    security_count: int = 0            # 持仓数量

    # 权限信息
    can_buy: bool = True               # 可买入
    can_sell: bool = True              # 可卖出

    # 更新时间
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class LiveOrder:
    """实盘订单"""
    order_id: str                       # 订单ID（本地）
    symbol: str                         # 股票代码
    side: OrderSide                     # 订单方向
    order_type: OrderType               # 订单类型
    quantity: int                       # 委托数量

    order_key: str = ""                 # 订单编号（券商）
    price: Optional[float] = None       # 委托价格

    filled_quantity: int = 0            # 成交数量
    filled_amount: float = 0.0          # 成交金额
    avg_price: float = 0.0              # 成交均价

    status: LiveOrderStatus = LiveOrderStatus.PENDING
    error_message: Optional[str] = None # 错误信息

    # 时间戳
    created_at: datetime = field(default_factory=datetime.now)
    submitted_at: Optional[datetime] = None  # 委托时间
    updated_at: datetime = field(default_factory=datetime.now)

    # 交易账号
    account_id: str = ""


@dataclass
class TradeRecord:
    """成交记录"""
    trade_id: str                       # 成交ID
    order_id: str                       # 订单ID

    symbol: str                         # 股票代码
    side: OrderSide                     # 买卖方向
    quantity: int                       # 成交数量
    price: float                        # 成交价格
    amount: float                       # 成交金额

    commission: float = 0.0             # 手续费
    stamp_tax: float = 0.0              # 印花税

    trade_time: datetime = field(default_factory=datetime.now)
    account_id: str = ""


class TradingService:
    """
    实盘交易服务

    核心职责：
    1. 连接券商交易接口（XtQuant/QMT）
    2. 执行真实资金交易
    3. 管理实盘订单
    4. 查询账户和持仓

    ⚠️ 风险警告：
    - 此Service涉及真实资金
    - 必须经过模拟实盘验证后才能使用
    - 建议设置严格的仓位和风控限制

    支持的交易接口：
    - XtQuant（MiniQMT）
    - QMT（迅投QMT）
    """

    def __init__(
        self,
        broker: str = "xtquant",        # 券商接口（xtquant/qmt）
        account_id: Optional[str] = None,
        auto_connect: bool = False,     # 自动连接
    ):
        """
        初始化实盘交易服务

        Args:
            broker: 券商接口类型
            account_id: 账户ID
            auto_connect: 是否自动连接
        """
        self.broker = broker
        self.account_id = account_id
        self.status = TradingStatus.DISCONNECTED

        # 交易接口实例
        self._trader = None

        # 订单和成交记录
        self._orders: Dict[str, LiveOrder] = {}
        self._trades: List[TradeRecord] = []

        # 账户信息
        self._account: Optional[TradingAccount] = None

        # 自动连接
        if auto_connect and account_id:
            self.connect()

        logger.info("✅ TradingService初始化完成")

    # ==================== 连接管理 ====================

    def connect(self, account_id: Optional[str] = None) -> bool:
        """
        连接交易接口

        Args:
            account_id: 账户ID

        Returns:
            是否连接成功
        """
        if account_id:
            self.account_id = account_id

        if not self.account_id:
            logger.error("账户ID未指定")
            return False

        logger.info(f"正在连接交易接口: {self.broker}, 账户: {self.account_id}")
        self.status = TradingStatus.CONNECTING

        try:
            # 根据broker类型连接
            if self.broker == "xtquant":
                success = self._connect_xtquant()
            elif self.broker == "qmt":
                success = self._connect_qmt()
            else:
                logger.error(f"不支持的broker: {self.broker}")
                success = False

            if success:
                self.status = TradingStatus.AUTHENTICATED
                logger.info("✅ 交易接口连接成功")

                # 查询账户信息
                self._query_account_info()

            else:
                self.status = TradingStatus.FAILED
                logger.error("❌ 交易接口连接失败")

            return success

        except Exception as e:
            self.status = TradingStatus.FAILED
            logger.error(f"连接异常: {e}")
            return False

    def _connect_xtquant(self) -> bool:
        """连接XtQuant交易接口"""
        try:
            from xtquant import xttrader

            # 创建交易对象
            self._trader = xttrader.ExtTrader()

            # 连接
            connect_result = self._trader.connect()
            if connect_result != 0:
                logger.error(f"XtQuant连接失败: {connect_result}")
                return False

            # 登录
            login_result = self._trader.login(account_id=self.account_id)
            if login_result != 0:
                logger.error(f"XtQuant登录失败: {login_result}")
                return False

            logger.info("✅ XtQuant交易接口已连接")
            return True

        except Exception as e:
            logger.error(f"XtQuant连接异常: {e}")
            return False

    def _connect_qmt(self) -> bool:
        """连接QMT交易接口"""
        # TODO: 实现QMT连接逻辑
        logger.warning("QMT接口尚未实现")
        return False

    def disconnect(self):
        """断开连接"""
        if self._trader:
            try:
                # 根据不同接口断开连接
                if self.broker == "xtquant":
                    self._trader.logout()
                    self._trader.release()
            except Exception as e:
                logger.warning(f"断开连接异常: {e}")

        self.status = TradingStatus.DISCONNECTED
        logger.info("交易接口已断开")

    # ==================== 订单交易 ====================

    def place_order(
        self,
        symbol: str,
        side: OrderSide,
        order_type: OrderType,
        quantity: int,
        price: Optional[float] = None
    ) -> Optional[LiveOrder]:
        """
        下单

        Args:
            symbol: 股票代码
            side: 买卖方向
            order_type: 订单类型
            quantity: 委托数量
            price: 委托价格（限价单必填）

        Returns:
            LiveOrder对象，失败返回None
        """
        if self.status != TradingStatus.AUTHENTICATED:
            logger.error("交易接口未连接或未认证")
            return None

        # 验证参数
        if order_type == OrderType.LIMIT and price is None:
            logger.error("限价单必须指定价格")
            return None

        if quantity <= 0:
            logger.error("委托数量必须大于0")
            return None

        # 生成订单ID（使用uuid确保唯一性）
        order_id = f"live_order_{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:8]}"

        # 创建订单对象
        order = LiveOrder(
            order_id=order_id,
            symbol=symbol,
            side=side,
            order_type=order_type,
            quantity=quantity,
            price=price,
            account_id=self.account_id
        )

        try:
            # 调用交易接口下单
            if self.broker == "xtquant":
                order_key = self._place_order_xtquant(order)
                if order_key:
                    order.order_key = order_key
                    order.status = LiveOrderStatus.SUBMITTED
                    order.submitted_at = datetime.now()
                else:
                    order.status = LiveOrderStatus.REJECTED
                    order.error_message = "下单失败"
            else:
                order.status = LiveOrderStatus.REJECTED
                order.error_message = f"不支持的broker: {self.broker}"

        except Exception as e:
            order.status = LiveOrderStatus.REJECTED
            order.error_message = str(e)
            logger.error(f"下单异常: {e}")

        # 保存订单
        self._orders[order_id] = order
        order.updated_at = datetime.now()

        logger.info(f"订单已下单: {order_id}, {symbol}, {side.value}, {quantity}股, "
                   f"状态: {order.status.value}")

        return order

    def _place_order_xtquant(self, order: LiveOrder) -> Optional[str]:
        """
        XtQuant下单

        Args:
            order: 订单对象

        Returns:
            订单编号（order_key），失败返回None
        """
        try:
            # 转换股票代码格式
            stock_code = order.symbol.replace('.', '')

            # 转换买卖方向
            direction = order.side.value  # buy/sell

            # 转换订单类型
            order_type = order.order_type.value  # market/limit

            # 下单
            if order.order_type == OrderType.MARKET:
                # 市价单
                result = self._trader.order_stock(
                    account=self.account_id,
                    stock_code=stock_code,
                    order_type=direction,  # 23=买入, 24=卖出
                    order_volume=order.quantity,
                    price_type=0,  # 市价单
                )
            else:
                # 限价单
                result = self._trader.order_stock(
                    account=self.account_id,
                    stock_code=stock_code,
                    order_type=direction,
                    order_volume=order.quantity,
                    price_type=11,  # 限价单
                    price=order.price,
                )

            # 返回订单编号
            if result and len(result) > 0:
                order_key = result[0]
                logger.info(f"XtQuant下单成功，订单编号: {order_key}")
                return str(order_key)

        except Exception as e:
            logger.error(f"XtQuant下单异常: {e}")

        return None

    def cancel_order(self, order_id: str) -> bool:
        """
        撤单

        Args:
            order_id: 订单ID

        Returns:
            是否成功撤销
        """
        order = self._orders.get(order_id)
        if not order:
            logger.warning(f"订单不存在: {order_id}")
            return False

        if order.status in [LiveOrderStatus.FILLED, LiveOrderStatus.CANCELLED]:
            logger.warning(f"订单状态不允许撤销: {order.status.value}")
            return False

        try:
            # 调用交易接口撤单
            success = False
            if self.broker == "xtquant":
                success = self._cancel_order_xtquant(order)

            if success:
                order.status = LiveOrderStatus.CANCELLED
                order.updated_at = datetime.now()
                logger.info(f"订单已撤销: {order_id}")
            else:
                logger.warning(f"撤销失败: {order_id}")

            return success

        except Exception as e:
            logger.error(f"撤单异常: {e}")
            return False

    def _cancel_order_xtquant(self, order: LiveOrder) -> bool:
        """
        XtQuant撤单

        Args:
            order: 订单对象

        Returns:
            是否成功
        """
        try:
            if not order.order_key:
                logger.error("订单编号为空，无法撤销")
                return False

            result = self._trader.cancel_order(order_key=order.order_key)

            if result:
                return True
            else:
                logger.warning(f"XtQuant撤单失败: {order.order_key}")
                return False

        except Exception as e:
            logger.error(f"XtQuant撤单异常: {e}")
            return False

    # ==================== 查询接口 ====================

    def query_account(self) -> Optional[TradingAccount]:
        """
        查询账户信息

        Returns:
            TradingAccount对象
        """
        if self.status != TradingStatus.AUTHENTICATED:
            return None

        self._query_account_info()
        return self._account

    def _query_account_info(self):
        """查询账户信息"""
        try:
            if self.broker == "xtquant":
                self._query_account_xtquant()
        except Exception as e:
            logger.error(f"查询账户信息异常: {e}")

    def _query_account_xtquant(self):
        """查询XtQuant账户信息"""
        try:
            # 查询资金
            capital = self._trader.query_stock_account(self.account_id)

            if capital and len(capital) > 0:
                account_info = capital[0]

                self._account = TradingAccount(
                    account_id=self.account_id,
                    account_type="stock",
                    cash=account_info.get('cash', 0.0),
                    total_assets=account_info.get('total_asset', 0.0),
                    frozen_cash=account_info.get('frozen_cash', 0.0),
                    market_value=account_info.get('market_value', 0.0),
                    security_count=account_info.get('security_count', 0),
                    updated_at=datetime.now()
                )

                logger.debug(f"账户资金: 总资产={self._account.total_assets:.2f}, "
                           f"可用={self._account.cash:.2f}")

        except Exception as e:
            logger.error(f"查询XtQuant账户信息异常: {e}")

    def get_order(self, order_id: str) -> Optional[LiveOrder]:
        """
        查询订单

        Args:
            order_id: 订单ID

        Returns:
            LiveOrder对象
        """
        return self._orders.get(order_id)

    def get_orders(
        self,
        symbol: Optional[str] = None,
        status: Optional[LiveOrderStatus] = None
    ) -> List[LiveOrder]:
        """
        查询订单列表

        Args:
            symbol: 股票代码筛选
            status: 订单状态筛选

        Returns:
            LiveOrder列表
        """
        orders = list(self._orders.values())

        if status is not None:
            orders = [o for o in orders if o.status == status]

        if symbol is not None:
            orders = [o for o in orders if o.symbol == symbol]

        return sorted(orders, key=lambda x: x.created_at, reverse=True)

    def get_trades(
        self,
        symbol: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[TradeRecord]:
        """
        查询成交记录

        Args:
            symbol: 股票代码筛选
            start_time: 开始时间
            end_time: 结束时间

        Returns:
            TradeRecord列表
        """
        trades = self._trades

        if symbol is not None:
            trades = [t for t in trades if t.symbol == symbol]

        if start_time is not None:
            trades = [t for t in trades if t.trade_time >= start_time]

        if end_time is not None:
            trades = [t for t in trades if t.trade_time <= end_time]

        return sorted(trades, key=lambda x: x.trade_time, reverse=True)

    # ==================== 持仓查询 ====================

    def query_positions(self) -> Dict[str, Dict[str, Any]]:
        """
        查询持仓

        Returns:
            持仓字典 {symbol: position_info}
        """
        if self.status != TradingStatus.AUTHENTICATED:
            logger.warning("交易接口未认证，返回空持仓")
            return {}

        try:
            if self.broker == "xtquant":
                return self._query_positions_xtquant()
            else:
                logger.warning(f"不支持的broker: {self.broker}")
                return {}

        except Exception as e:
            logger.error(f"查询持仓异常: {e}")
            return {}

    def _query_positions_xtquant(self) -> Dict[str, Dict[str, Any]]:
        """
        查询XtQuant持仓

        Returns:
            持仓字典 {symbol: position_info}
        """
        positions = {}

        try:
            # 查询持仓
            position_list = self._trader.query_stock_positions(
                self.account_id
            )

            if position_list:
                for pos in position_list:
                    symbol = pos.get('stock_code', '')

                    # 转换代码格式 (000001.SZ -> sz000001)
                    if '.' not in symbol:
                        # XtQuant返回格式可能是纯代码，需要添加后缀
                        if symbol.startswith('6'):
                            symbol = f"sh{symbol}"
                        else:
                            symbol = f"sz{symbol}"

                    positions[symbol] = {
                        'symbol': symbol,
                        'symbol_name': pos.get('stock_name', ''),
                        'quantity': pos.get('volume', 0),
                        'available_quantity': pos.get('can_use_volume', 0),
                        'frozen_quantity': pos.get('frozen_volume', 0),
                        'avg_price': pos.get('open_price', 0.0),
                        'cost_amount': pos.get('market_value', 0.0),
                        'current_price': pos.get('market_price', 0.0),
                        'market_value': pos.get('market_value', 0.0),
                        'profit_loss': pos.get('profit_loss', 0.0),
                        'profit_loss_pct': pos.get('profit_loss_ratio', 0.0),
                    }

                logger.debug(f"查询到 {len(positions)} 个持仓")

        except Exception as e:
            logger.error(f"查询XtQuant持仓异常: {e}")

        return positions

    def query_position(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        查询单个持仓

        Args:
            symbol: 股票代码

        Returns:
            持仓信息字典
        """
        positions = self.query_positions()
        return positions.get(symbol)


# ==================== 全局单例 ====================

_trading_service_instance: Optional[TradingService] = None


def get_trading_service() -> TradingService:
    """
    获取实盘交易服务单例

    Returns:
        TradingService实例
    """
    global _trading_service_instance

    if _trading_service_instance is None:
        _trading_service_instance = TradingService()

    return _trading_service_instance

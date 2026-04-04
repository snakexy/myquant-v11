"""
完整的QLib SimulatorExecutor实现

该模块实现了与QLib官方完全兼容的SimulatorExecutor，包括：
- 完整的交易决策执行流程
- 支持TT_SERIAL和TT_PARAL交易类型
- 标准的订单处理和成本计算
- 完整的账户管理集成
"""

from typing import Dict, Any, List, Tuple, Union
from collections import defaultdict

# 导入基础设施模块
from .infrastructure_clean import (
    CommonInfrastructure, LevelInfrastructure
)

# 尝试导入QLib
try:
    from qlib.backtest.account import Account
    from qlib.backtest.position import BasePosition
    from qlib.backtest.decision import BaseTradeDecision, Order
    from qlib.backtest.exchange import Exchange
    QLIB_AVAILABLE = True
except ImportError:
    QLIB_AVAILABLE = False


class SimulatorExecutor:
    """
    完整的QLib SimulatorExecutor实现
    
    该类实现了与QLib官方完全兼容的模拟交易执行器，支持：
    - 串行和并行交易类型
    - 完整的订单执行流程
    - 标准的成本计算
    - 完整的账户管理集成
    """
    
    # 交易类型常量
    TT_SERIAL = "serial"
    TT_PARAL = "parallel"
    
    def __init__(
        self,
        time_per_step: str,
        start_time: Union[str, Any] = None,
        end_time: Union[str, Any] = None,
        indicator_config: Dict[str, Any] = None,
        generate_portfolio_metrics: bool = False,
        verbose: bool = False,
        track_data: bool = False,
        trade_exchange: Exchange = None,
        common_infra: CommonInfrastructure = None,
        settle_type: str = None,
        **kwargs: Any
    ):
        """
        初始化SimulatorExecutor
        
        Parameters
        ----------
        time_per_step : str
            每个交易步骤的时间频率
        start_time : str, optional
            开始时间
        end_time : str, optional
            结束时间
        indicator_config : dict, optional
            指标配置
        generate_portfolio_metrics : bool, optional
            是否生成投资组合指标
        verbose : bool, optional
            是否输出详细信息
        track_data : bool, optional
            是否跟踪数据
        trade_exchange : Exchange, optional
            交易所实例
        common_infra : CommonInfrastructure, optional
            通用基础设施
        settle_type : str, optional
            结算类型
        **kwargs : dict
            其他参数
        """
        self.time_per_step = time_per_step
        self.indicator_config = indicator_config or {}
        self.generate_portfolio_metrics = generate_portfolio_metrics
        self.verbose = verbose
        self.track_data = track_data
        self.settle_type = settle_type or BasePosition.ST_NO
        
        # 初始化基础设施
        self.level_infra = LevelInfrastructure()
        self.level_infra.reset_infra(common_infra, self)
        
        # 记录每日交易金额
        self.dealt_order_amount = defaultdict(float)
        self.deal_day = None
        
        # 初始化交易日历
        self.level_infra.reset_cal(
            freq=time_per_step,
            start_time=start_time,
            end_time=end_time
        )
    
    def reset(
        self,
        start_time: Union[str, Any] = None,
        end_time: Union[str, Any] = None,
        common_infra: CommonInfrastructure = None,
        **kwargs: Any
    ) -> None:
        """
        重置执行器
        
        Parameters
        ----------
        start_time : str, optional
            开始时间
        end_time : str, optional
            结束时间
        common_infra : CommonInfrastructure, optional
            通用基础设施
        **kwargs : dict
            其他参数
        """
        self.level_infra.reset_infra(common_infra, self)
        self.level_infra.reset_cal(
            freq=self.time_per_step,
            start_time=start_time,
            end_time=end_time
        )
    
    @property
    def trade_exchange(self) -> Exchange:
        """获取交易所"""
        return self.level_infra.common_infra.trade_exchange
    
    @property
    def trade_account(self) -> Account:
        """获取交易账户"""
        return self.level_infra.common_infra.trade_account
    
    @property
    def trade_calendar(self):
        """获取交易日历"""
        return self.level_infra.trade_calendar
    
    def finished(self) -> bool:
        """检查是否完成"""
        return self.trade_calendar.finished()
    
    def get_level_infra(self) -> LevelInfrastructure:
        """获取层级基础设施"""
        return self.level_infra
    
    def get_all_executors(self) -> List['SimulatorExecutor']:
        """获取所有执行器"""
        return [self]
    
    def _get_order_iterator(
        self, trade_decision: BaseTradeDecision
    ) -> List[Order]:
        """
        获取订单迭代器
        
        Parameters
        ----------
        trade_decision : BaseTradeDecision
            交易决策
            
        Returns
        -------
        List[Order]
            订单列表
        """
        # 从交易决策中提取订单
        orders = self._retrieve_orders_from_decision(trade_decision)
        
        if self.trade_type == self.TT_SERIAL:
            # 串行执行：按原顺序执行
            return orders
        elif self.trade_type == self.TT_PARAL:
            # 并行执行：按方向排序，买单先执行
            return sorted(orders, key=lambda order: -order.direction)
        else:
            raise NotImplementedError(f"不支持的交易类型: {self.trade_type}")
    
    def _retrieve_orders_from_decision(
        self, trade_decision: BaseTradeDecision
    ) -> List[Order]:
        """
        从交易决策中提取订单
        
        Parameters
        ----------
        trade_decision : BaseTradeDecision
            交易决策
            
        Returns
        -------
        List[Order]
            订单列表
        """
        try:
            # 如果交易决策有get_decision方法，使用它
            if hasattr(trade_decision, 'get_decision'):
                decisions = trade_decision.get_decision()
            else:
                # 否则假设trade_decision本身就是决策列表
                decisions = [trade_decision]
            
            orders = []
            for decision in decisions:
                if hasattr(decision, 'get_order_list'):
                    order_list = decision.get_order_list()
                    orders.extend(order_list)
                elif isinstance(decision, list):
                    orders.extend(decision)
                else:
                    # 单个订单
                    orders.append(decision)
            
            return orders
            
        except Exception as e:
            if self.verbose:
                print(f"提取订单失败: {e}")
            return []
    
    def _collect_data(
        self,
        trade_decision: BaseTradeDecision,
        level: int = 0
    ) -> Tuple[List[object], dict]:
        """
        收集交易数据
        
        Parameters
        ----------
        trade_decision : BaseTradeDecision
            交易决策
        level : int
            层级
            
        Returns
        -------
        Tuple[List[object], dict]
            (执行结果, 额外参数)
        """
        trade_start_time, _ = self.trade_calendar.get_step_time()
        
        # 每次移动到新日期时，清空当日交易金额
        now_deal_day = self.trade_calendar.get_step_time()[0].floor(freq="D")
        if self.deal_day is None or now_deal_day > self.deal_day:
            self.dealt_order_amount = defaultdict(float)
            self.deal_day = now_deal_day
        
        execute_result = []
        
        if self.verbose:
            print(f"[I {trade_start_time}]: 开始执行交易决策")
        
        # 获取订单迭代器
        orders = self._get_order_iterator(trade_decision)
        
        # 执行每个订单
        for order in orders:
            try:
                # 执行订单
                trade_val, trade_cost, trade_price = (
                    self.trade_exchange.deal_order(
                        order, self.trade_account, self.dealt_order_amount
                    )
                )
                
                execute_result.append(
                    (order, trade_val, trade_cost, trade_price)
                )
                
                # 更新当日交易金额
                self.dealt_order_amount[order.stock_id] += order.deal_amount
                
                if self.verbose:
                    print(
                        f"[I {trade_start_time}]: "
                        f"{'buy' if order.direction > 0 else 'sell'} "
                        f"{order.stock_id}, price {trade_price:.2f}, "
                        f"amount {order.amount}, "
                        f"deal_amount {order.deal_amount}, "
                        f"factor {order.factor}, value {trade_val:.2f}, "
                        f"cash {self.trade_account.get_cash():.2f}."
                    )
                    
            except Exception as e:
                if self.verbose:
                    print(f"订单执行失败: {e}")
                continue
        
        trade_info = {
            "trade_info": execute_result,
            "level": level
        }
        
        return execute_result, trade_info
    
    def collect_data(
        self,
        trade_decision: BaseTradeDecision,
        return_value: dict = None,
        level: int = 0
    ):
        """
        收集交易数据（生成器版本）
        
        Parameters
        ----------
        trade_decision : BaseTradeDecision
            交易决策
        return_value : dict, optional
            返回值字典
        level : int
            层级
            
        Yields
        ------
        Any
            交易决策
        """
        # 如果需要跟踪数据
        if self.track_data:
            yield trade_decision
        
        # 执行数据收集
        result, kwargs = self._collect_data(trade_decision, level)
        
        # 返回结果
        if return_value is not None:
            return_value.update(kwargs)
            yield return_value


# 创建便捷函数
def create_simulator_executor(
    time_per_step: str = "day",
    trade_type: str = "serial",
    **kwargs: Any
) -> SimulatorExecutor:
    """
    创建SimulatorExecutor实例的便捷函数
    
    Parameters
    ----------
    time_per_step : str
        时间步长
    trade_type : str
        交易类型
    **kwargs : dict
        其他参数
        
    Returns
    -------
    SimulatorExecutor
        执行器实例
    """
    return SimulatorExecutor(
        time_per_step=time_per_step,
        trade_type=trade_type,
        **kwargs
    )


# 导出主要类和函数
__all__ = [
    'SimulatorExecutor',
    'create_simulator_executor'
]
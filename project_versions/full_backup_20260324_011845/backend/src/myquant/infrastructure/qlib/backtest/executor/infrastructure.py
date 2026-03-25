"""
QLib执行器基础设施管理模块

该模块实现了QLib标准的基础设施管理，包括：
- CommonInfrastructure: 通用基础设施管理
- LevelInfrastructure: 层级基础设施管理
- TradeCalendarManager: 交易日历管理
"""

from typing import Dict, Any, Optional

try:
    from qlib.backtest.account import Account
    from qlib.backtest.exchange import Exchange
    from qlib.backtest.position import BasePosition
    from qlib.utils.time import Freq
    QLIB_AVAILABLE = True
except ImportError:
    QLIB_AVAILABLE = False
    # 定义占位符类
    class Account:
        pass
    class Exchange:
        pass
    class BasePosition:
        pass
    class Freq:
        pass


class CommonInfrastructure:
    """
    通用基础设施管理器
    
    负责管理执行器共享的基础设施组件，包括：
    - 交易账户
    - 交易所
    - 其他共享资源
    """
    
    def __init__(self):
        """初始化通用基础设施"""
        self._components: Dict[str, Any] = {}
        self._account: Optional[Account] = None
        self._exchange: Optional[Exchange] = None
    
    def set(self, key: str, value: Any) -> None:
        """设置基础设施组件"""
        self._components[key] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取基础设施组件"""
        return self._components.get(key, default)
    
    def has(self, key: str) -> bool:
        """检查是否包含指定组件"""
        return key in self._components
    
    @property
    def trade_account(self) -> Optional[Account]:
        """获取交易账户"""
        return self._account
    
    @trade_account.setter
    def trade_account(self, account: Account) -> None:
        """设置交易账户"""
        self._account = account
    
    @property
    def trade_exchange(self) -> Optional[Exchange]:
        """获取交易所"""
        return self._exchange
    
    @trade_exchange.setter
    def trade_exchange(self, exchange: Exchange) -> None:
        """设置交易所"""
        self._exchange = exchange
    
    def update(self, other_infra: 'CommonInfrastructure') -> None:
        """更新基础设施"""
        self._components.update(other_infra._components)
        if other_infra._account:
            self._account = other_infra._account
        if other_infra._exchange:
            self._exchange = other_infra._exchange


class LevelInfrastructure:
    """
    层级基础设施管理器
    
    负责管理特定层级的基础设施，包括：
    - 交易日历
    - 子层级基础设施
    - 层级特定的配置
    """
    
    def __init__(self):
        """初始化层级基础设施"""
        self._components: Dict[str, Any] = {}
        self._trade_calendar = None
        self._sub_level_infra = None
    
    def set(self, key: str, value: Any) -> None:
        """设置层级组件"""
        self._components[key] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取层级组件"""
        return self._components.get(key, default)
    
    def has(self, key: str) -> bool:
        """检查是否包含指定组件"""
        return key in self._components
    
    def reset_infra(self, common_infra: CommonInfrastructure, 
                   executor: Any = None) -> None:
        """重置基础设施"""
        # 更新通用基础设施引用
        self._common_infra = common_infra
        
        # 如果有执行器，设置执行器引用
        if executor:
            self._executor = executor
    
    def reset_cal(self, freq: str, start_time: str = None, 
                 end_time: str = None) -> None:
        """重置交易日历"""
        if QLIB_AVAILABLE:
            self._trade_calendar = TradeCalendarManager(freq, start_time, end_time)
        else:
            # 创建简化的交易日历
            self._trade_calendar = SimpleTradeCalendarManager(freq, start_time, end_time)
    
    def set_sub_level_infra(self, sub_infra: 'LevelInfrastructure') -> None:
        """设置子层级基础设施"""
        self._sub_level_infra = sub_infra
    
    @property
    def trade_calendar(self):
        """获取交易日历"""
        return self._trade_calendar
    
    @property
    def common_infra(self):
        """获取通用基础设施"""
        return getattr(self, '_common_infra', None)


class TradeCalendarManager:
    """
    交易日历管理器
    
    负责管理交易日历，包括：
    - 交易日计算
    - 时间步进管理
    - 日期范围验证
    """
    
    def __init__(self, freq: str = "day", start_time: str = None, 
                 end_time: str = None):
        """初始化交易日历管理器"""
        self.freq = freq
        self.start_time = start_time
        self.end_time = end_time
        self.current_step = 0
        self.total_steps = 0
        
        if QLIB_AVAILABLE:
            self._init_qlib_calendar()
        else:
            self._init_simple_calendar()
    
    def _init_qlib_calendar(self):
        """初始化QLib交易日历"""
        try:
            from qlib.utils.time import Freq
            from qlib.data.dataset import D
            from qlib.data.dataset.handler import DataHandlerLP
            
            # 创建数据处理器
            handler = DataHandlerLP()
            
            # 初始化频率
            if self.freq:
                freq_obj = Freq.parse(self.freq)
            else:
                freq_obj = Freq.parse("day")
            
            # 设置时间范围
            if self.start_time and self.end_time:
                # 这里应该使用QLib的日历功能
                # 简化实现，实际应该调用QLib的交易日历
                dates = pd.date_range(
                    start=self.start_time, 
                    end=self.end_time, 
                    freq='D'
                )
                self.trading_days = dates.tolist()
                self.total_steps = len(self.trading_days)
            else:
                self.trading_days = []
                self.total_steps = 0
                
        except Exception as e:
            # 如果QLib初始化失败，使用简化版本
            self._init_simple_calendar()
    
    def _init_simple_calendar(self):
        """初始化简化的交易日历"""
        if self.start_time and self.end_time:
            dates = pd.date_range(
                start=self.start_time, 
                end=self.end_time, 
                freq='D'
            )
            # 过滤掉周末（简化处理）
            self.trading_days = [
                date for date in dates 
                if date.weekday() < 5  # 0-4是周一到周五
            ]
            self.total_steps = len(self.trading_days)
        else:
            self.trading_days = []
            self.total_steps = 0
    
    def step(self) -> None:
        """前进一步"""
        self.current_step += 1
    
    def finished(self) -> bool:
        """检查是否完成"""
        return self.current_step >= self.total_steps
    
    def get_step_time(self) -> tuple:
        """获取当前步骤的时间"""
        if self.current_step < len(self.trading_days):
            current_date = self.trading_days[self.current_step]
            next_date = self.trading_days[min(self.current_step + 1, len(self.trading_days) - 1)]
            return current_date, next_date
        else:
            return None, None
    
    def get_trade_step(self) -> int:
        """获取当前交易步骤"""
        return self.current_step
    
    def reset(self) -> None:
        """重置日历"""
        self.current_step = 0


class SimpleTradeCalendarManager(TradeCalendarManager):
    """
    简化的交易日历管理器（当QLib不可用时）
    """
    
    def _init_simple_calendar(self):
        """初始化简化的交易日历"""
        super()._init_simple_calendar()


def get_start_end_idx(calendar: TradeCalendarManager, 
                  trade_decision) -> tuple:
    """
    获取开始和结束索引
    
    Parameters
    ----------
    calendar : TradeCalendarManager
        交易日历管理器
    trade_decision : BaseTradeDecision
        交易决策
        
    Returns
    -------
    tuple
        (start_idx, end_idx)
    """
    try:
        # 如果交易决策有范围限制
        if hasattr(trade_decision, 'get_range_limit'):
            range_limit = trade_decision.get_range_limit()
            if range_limit:
                # 计算范围限制的索引
                current_step = calendar.get_trade_step()
                # 这里应该根据具体的范围限制逻辑计算
                # 简化实现
                return current_step, min(current_step + 10, calendar.total_steps - 1)
        
        # 默认返回当前步骤和结束步骤
        return calendar.get_trade_step(), calendar.total_steps - 1
    except Exception:
        # 出错时返回默认值
        return 0, calendar.total_steps - 1


def init_instance_by_config(config: Dict[str, Any], 
                       common_infra: CommonInfrastructure = None,
                       accept_types: tuple = None):
    """
    根据配置初始化实例
    
    Parameters
    ----------
    config : Dict[str, Any]
        配置字典
    common_infra : CommonInfrastructure, optional
        通用基础设施
    accept_types : tuple, optional
        接受的类型
        
    Returns
    -------
    Any
        初始化的实例
    """
    if not QLIB_AVAILABLE:
        return None
    
    try:
        from qlib.utils import init_instance_by_config as qlib_init_instance
        return qlib_init_instance(config, common_infra, accept_types)
    except Exception as e:
        # 如果QLib不可用，返回None
        return None


# 导出主要类和函数
__all__ = [
    'CommonInfrastructure',
    'LevelInfrastructure', 
    'TradeCalendarManager',
    'SimpleTradeCalendarManager',
    'get_start_end_idx',
    'init_instance_by_config'
]
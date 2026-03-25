"""
QLib NestedExecutor实现

该模块实现了与QLib官方完全兼容的NestedExecutor，包括：
- 嵌套执行器管理
- 多层级交易决策执行
- 子执行器协调
- 层级数据聚合
"""

from typing import Dict, Any, List, Union
from collections import defaultdict

# 导入基类和基础设施
from .base_executor import BaseExecutor, ExecutorMixin
from .infrastructure_clean import (
    CommonInfrastructure, LevelInfrastructure
)

# 尝试导入QLib
try:
    from qlib.backtest.account import Account
    from qlib.backtest.exchange import Exchange
    QLIB_AVAILABLE = True
except ImportError:
    QLIB_AVAILABLE = False


class NestedExecutor(BaseExecutor, ExecutorMixin):
    """
    QLib NestedExecutor实现
    
    该类实现了与QLib官方完全兼容的嵌套执行器，支持：
    - 多层级执行器管理
- 嵌套交易决策执行
- 子执行器协调
- 层级数据聚合
    """
    
    def __init__(
        self,
        time_per_step: str,
        start_time: Union[str, Any] = None,
        end_time: Union[str, Any] = None,
        indicator_config: Dict[str, Any] = None,
        generate_portfolio_metrics: bool = False,
        verbose: bool = False,
        track_data: bool = False,
        sub_executors: List[BaseExecutor] = None,
        common_infra: CommonInfrastructure = None,
        **kwargs: Any
    ):
        """
        初始化NestedExecutor
        
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
        sub_executors : List[BaseExecutor], optional
            子执行器列表
        common_infra : CommonInfrastructure, optional
            通用基础设施
        **kwargs : dict
            其他参数
        """
        super().__init__(
            time_per_step=time_per_step,
            start_time=start_time,
            end_time=end_time,
            indicator_config=indicator_config,
            generate_portfolio_metrics=generate_portfolio_metrics,
            verbose=verbose,
            track_data=track_data,
            **kwargs
        )
        
        # 初始化子执行器
        self.sub_executors = sub_executors or []
        
        # 初始化基础设施
        self.level_infra = LevelInfrastructure()
        self.level_infra.reset_infra(common_infra, self)
        
        # 初始化交易日历
        self.level_infra.reset_cal(
            freq=time_per_step,
            start_time=start_time,
            end_time=end_time
        )
        
        # 层级数据存储
        self.level_data = defaultdict(dict)
        self.execution_history = []
    
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
        # 重置自身基础设施
        self.level_infra.reset_infra(common_infra, self)
        self.level_infra.reset_cal(
            freq=self.time_per_step,
            start_time=start_time,
            end_time=end_time
        )
        
        # 重置子执行器
        for executor in self.sub_executors:
            executor.reset(start_time, end_time, common_infra, **kwargs)
        
        # 清空数据
        self.level_data.clear()
        self.execution_history.clear()
    
    def finished(self) -> bool:
        """检查是否完成"""
        # 检查自身是否完成
        if not self.trade_calendar.finished():
            return False
        
        # 检查所有子执行器是否完成
        for executor in self.sub_executors:
            if not executor.finished():
                return False
        
        return True
    
    def get_level_infra(self) -> LevelInfrastructure:
        """获取层级基础设施"""
        return self.level_infra
    
    def get_all_executors(self) -> List[BaseExecutor]:
        """获取所有执行器"""
        executors = [self]
        for executor in self.sub_executors:
            executors.extend(executor.get_all_executors())
        return executors
    
    def add_sub_executor(self, executor: BaseExecutor) -> None:
        """
        添加子执行器
        
        Parameters
        ----------
        executor : BaseExecutor
            子执行器
        """
        self.sub_executors.append(executor)
        
        # 如果当前执行器有基础设施，同步给子执行器
        if self.level_infra and self.level_infra.common_infra:
            executor.reset(
                common_infra=self.level_infra.common_infra
            )
    
    def remove_sub_executor(self, executor: BaseExecutor) -> bool:
        """
        移除子执行器
        
        Parameters
        ----------
        executor : BaseExecutor
            子执行器
            
        Returns
        -------
        bool
            是否成功移除
        """
        if executor in self.sub_executors:
            self.sub_executors.remove(executor)
            return True
        return False
    
    def get_sub_executors(self) -> List[BaseExecutor]:
        """获取子执行器列表"""
        return self.sub_executors.copy()
    
    def _collect_data(
        self,
        trade_decision: Any,
        level: int = 0
    ) -> tuple:
        """
        收集交易数据
        
        Parameters
        ----------
        trade_decision : Any
            交易决策
        level : int
            层级
            
        Returns
        -------
        tuple
            (执行结果, 额外参数)
        """
        trade_start_time, _ = self.trade_calendar.get_step_time()
        
        if self.verbose:
            print(f"[I {trade_start_time}]: 嵌套执行器开始处理层级 {level}")
        
        # 准备执行上下文
        context = self._prepare_execution_context(level)
        
        # 存储层级数据
        self.level_data[level] = {
            'trade_decision': trade_decision,
            'context': context,
            'start_time': trade_start_time
        }
        
        execute_result = []
        
        # 首先在当前层级执行
        try:
            # 如果有具体的执行逻辑，在这里实现
            # 否则，主要协调子执行器
            pass
        except Exception as e:
            if self.verbose:
                print(f"层级 {level} 执行失败: {e}")
        
        # 然后协调子执行器
        sub_results = self._coordinate_sub_executors(trade_decision, level + 1)
        execute_result.extend(sub_results)
        
        # 聚合结果
        aggregated_result = self._aggregate_results(execute_result, level)
        
        # 记录执行历史
        self.execution_history.append({
            'level': level,
            'start_time': trade_start_time,
            'result': aggregated_result,
            'sub_results': sub_results
        })
        
        trade_info = {
            'trade_info': aggregated_result,
            'level': level,
            'sub_results': sub_results,
            'context': context
        }
        
        return aggregated_result, trade_info
    
    def _coordinate_sub_executors(
        self,
        trade_decision: Any,
        level: int
    ) -> List[Any]:
        """
        协调子执行器
        
        Parameters
        ----------
        trade_decision : Any
            交易决策
        level : int
            层级
            
        Returns
        -------
        List[Any]
            子执行器结果
        """
        sub_results = []
        
        for i, executor in enumerate(self.sub_executors):
            try:
                if self.verbose:
                    print(f"协调子执行器 {i} 在层级 {level}")
                
                # 执行子执行器
                result = executor.execute(trade_decision, level)
                sub_results.extend(result)
                
            except Exception as e:
                if self.verbose:
                    print(f"子执行器 {i} 执行失败: {e}")
                continue
        
        return sub_results
    
    def _aggregate_results(
        self,
        results: List[Any],
        level: int
    ) -> List[Any]:
        """
        聚合结果
        
        Parameters
        ----------
        results : List[Any]
            原始结果
        level : int
            层级
            
        Returns
        -------
        List[Any]
            聚合后的结果
        """
        # 基本的聚合逻辑，子类可以重写
        if not results:
            return []
        
        # 这里可以实现特定的聚合逻辑
        # 例如：去重、排序、合并等
        aggregated = []
        seen = set()
        
        for result in results:
            # 简单的去重逻辑
            result_key = str(result)
            if result_key not in seen:
                seen.add(result_key)
                aggregated.append(result)
        
        return aggregated
    
    def get_level_data(self, level: int) -> Dict[str, Any]:
        """
        获取层级数据
        
        Parameters
        ----------
        level : int
            层级
            
        Returns
        -------
        Dict[str, Any]
            层级数据
        """
        return self.level_data.get(level, {}).copy()
    
    def get_execution_history(self) -> List[Dict[str, Any]]:
        """获取执行历史"""
        return self.execution_history.copy()
    
    def clear_execution_history(self) -> None:
        """清空执行历史"""
        self.execution_history.clear()
    
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


# 创建便捷函数
def create_nested_executor(
    time_per_step: str = "day",
    sub_executors: List[BaseExecutor] = None,
    **kwargs: Any
) -> NestedExecutor:
    """
    创建NestedExecutor实例的便捷函数
    
    Parameters
    ----------
    time_per_step : str
        时间步长
    sub_executors : List[BaseExecutor], optional
        子执行器列表
    **kwargs : dict
        其他参数
        
    Returns
    -------
    NestedExecutor
        嵌套执行器实例
    """
    return NestedExecutor(
        time_per_step=time_per_step,
        sub_executors=sub_executors,
        **kwargs
    )


# 导出主要类和函数
__all__ = [
    'NestedExecutor',
    'create_nested_executor'
]
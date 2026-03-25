# QLib工作流管理器

import json
import yaml
import logging
import numpy as np
from typing import Dict, Any, Optional, List
from datetime import datetime
import pandas as pd
from pathlib import Path

from .config_parser import ConfigParser
from .task_scheduler import TaskScheduler

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WorkflowManager:
    """
    QLib工作流管理器
    
    该类实现了QLib标准的工作流管理功能，包括：
    - 工作流配置解析
    - 任务调度和执行
    - 结果收集和报告
    - 自动化回测
    """
    
    def __init__(
        self,
        config_path: Optional[str] = None,
        config_dict: Optional[Dict] = None
    ):
        """
        初始化工作流管理器
        
        Args:
            config_path: 配置文件路径
            config_dict: 配置字典
        """
        self.config_parser = ConfigParser()
        self.task_scheduler = TaskScheduler()
        
        # 加载配置
        if config_path:
            self.config = self.config_parser.parse_file(config_path)
        elif config_dict:
            self.config = self.config_parser.parse_dict(config_dict)
        else:
            # 使用默认配置
            self.config = self._get_default_config()
            
        # 工作流状态
        self.workflow_id = self._generate_workflow_id()
        self.start_time = None
        self.end_time = None
        self.status = "initialized"
        self.results = {}
        self.logs = []
        
        logger.info(f"[WorkflowManager] 工作流管理器初始化完成，ID: {self.workflow_id}")
    
    def _generate_workflow_id(self) -> str:
        """生成工作流ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"workflow_{timestamp}"
    
    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            "workflow": {
                "name": "default_workflow",
                "description": "默认QLib工作流",
                "version": "1.0.0"
            },
            "data": {
                "provider": "local",
                "market": "csi300",
                "start_time": "2017-01-01",
                "end_time": "2020-08-01",
                "features": ["Alpha158"]
            },
            "model": {
                "type": "lgb",
                "loss": "mse",
                "learning_rate": 0.1,
                "num_leaves": 31,
                "num_threads": 8
            },
            "strategy": {
                "type": "topk_dropout",
                "topk": 50,
                "n_drop": 5
            },
            "backtest": {
                "account": 100000000,
                "benchmark": "SH000300",
                "exchange_kwargs": {
                    "freq": "day",
                    "limit_threshold": 0.095,
                    "deal_price": "close",
                    "open_cost": 0.0005,
                    "close_cost": 0.0015,
                    "min_cost": 5
                }
            },
            "evaluation": {
                "metrics": [
                    "annualized_return",
                    "information_ratio",
                    "max_drawdown"
                ],
                "save_results": True,
                "output_dir": "results"
            }
        }
    
    def run(self) -> Dict[str, Any]:
        """
        运行完整的工作流
        
        Returns:
            工作流执行结果
        """
        try:
            self.start_time = datetime.now()
            self.status = "running"
            self._log(f"开始执行工作流: {self.config['workflow']['name']}")
            
            # 步骤1: 数据准备
            self._log("步骤1: 数据准备")
            data = self._prepare_data()
            
            # 步骤2: 特征工程
            self._log("步骤2: 特征工程")
            features = self._feature_engineering(data)
            
            # 步骤3: 模型训练
            self._log("步骤3: 模型训练")
            model = self._train_model(features)
            
            # 步骤4: 预测生成
            self._log("步骤4: 预测生成")
            predictions = self._generate_predictions(model, features)
            
            # 步骤5: 策略执行
            self._log("步骤5: 策略执行")
            strategy_results = self._execute_strategy(predictions)
            
            # 步骤6: 回测评估
            self._log("步骤6: 回测评估")
            evaluation_results = self._evaluate_results(strategy_results)
            
            # 步骤7: 结果保存
            self._log("步骤7: 结果保存")
            self._save_results(evaluation_results)
            
            self.end_time = datetime.now()
            self.status = "completed"
            self._log(f"工作流执行完成，耗时: {self.end_time - self.start_time}")
            
            return {
                "workflow_id": self.workflow_id,
                "status": self.status,
                "start_time": self.start_time,
                "end_time": self.end_time,
                "duration": self.end_time - self.start_time,
                "results": evaluation_results,
                "config": self.config,
                "logs": self.logs
            }
            
        except Exception as e:
            self.status = "failed"
            self.end_time = datetime.now()
            self._log(f"工作流执行失败: {str(e)}")
            logger.error(f"[WorkflowManager] 工作流执行失败: {str(e)}")
            
            return {
                "workflow_id": self.workflow_id,
                "status": self.status,
                "start_time": self.start_time,
                "end_time": self.end_time,
                "duration": self.end_time - self.start_time,
                "error": str(e),
                "config": self.config,
                "logs": self.logs
            }
    
    def _prepare_data(self) -> pd.DataFrame:
        """准备数据"""
        try:
            # 这里应该集成实际的数据提供器
            # 暂时返回模拟数据
            import numpy as np
            
            # 生成模拟数据
            dates = pd.date_range(
                start=self.config["data"]["start_time"],
                end=self.config["data"]["end_time"],
                freq="D"
            )
            
            # 过滤交易日
            dates = dates[dates.weekday < 5]  # 只保留工作日
            
            # 生成股票代码
            instruments = [f"SH{600000+i:06d}" for i in range(100)]  # 100只股票
            
            # 创建数据
            data_list = []
            for date in dates:
                for instrument in instruments:
                    # 生成随机价格数据
                    base_price = 10 + np.random.randn() * 2
                    data_list.append({
                        "datetime": date,
                        "instrument": instrument,
                        "open": base_price * (1 + np.random.randn() * 0.01),
                        "high": base_price * (
                            1 + abs(np.random.randn()) * 0.02
                        ),
                        "low": base_price * (
                            1 - abs(np.random.randn()) * 0.02
                        ),
                        "close": base_price * (1 + np.random.randn() * 0.01),
                        "volume": int(1000000 + np.random.randn() * 200000),
                        "amount": base_price * (
                            1000000 + np.random.randn() * 200000
                        )
                    })
            
            df = pd.DataFrame(data_list)
            self._log(f"数据准备完成，形状: {df.shape}")
            return df
            
        except Exception as e:
            self._log(f"数据准备失败: {str(e)}")
            raise
    
    def _feature_engineering(self, data: pd.DataFrame) -> pd.DataFrame:
        """特征工程"""
        try:
            # 导入Alpha158处理器
            from qlib_core.qlib_dataprocessing.features.alpha158 import (
                Alpha158Processor
            )
            
            # 创建处理器
            processor = Alpha158Processor(verbose=True)
            
            # 按股票分组处理
            results = []
            for instrument in data["instrument"].unique():
                stock_data = data[data["instrument"] == instrument].copy()
                stock_data = stock_data.sort_values("datetime")
                
                # 计算特征
                features = processor.transform(stock_data)
                results.append(features)
            
            # 合并结果
            features_df = pd.concat(results, ignore_index=True)
            self._log(f"特征工程完成，形状: {features_df.shape}")
            return features_df
            
        except Exception as e:
            self._log(f"特征工程失败: {str(e)}")
            raise
    
    def _train_model(self, features: pd.DataFrame):
        """训练模型"""
        try:
            # 这里应该集成实际的模型训练
            # 暂时返回模拟模型
            self._log("模型训练完成（模拟）")
            return {
                "model_type": "simulated",
                "features_count": features.shape[1]
            }
            
        except Exception as e:
            self._log(f"模型训练失败: {str(e)}")
            raise
    
    def _generate_predictions(
        self, model, features: pd.DataFrame
    ) -> pd.DataFrame:
        """生成预测"""
        try:
            # 这里应该集成实际的预测生成
            # 暂时返回模拟预测
            import numpy as np
            
            # 生成随机预测分数
            predictions = features.copy()
            predictions["score"] = np.random.randn(len(features))
            
            self._log(f"预测生成完成，形状: {predictions.shape}")
            return predictions
            
        except Exception as e:
            self._log(f"预测生成失败: {str(e)}")
            raise
    
    def _execute_strategy(self, predictions: pd.DataFrame) -> Dict[str, Any]:
        """执行策略"""
        try:
            # 这里应该集成实际的策略执行
            # 暂时返回模拟结果
            import numpy as np
            
            # 生成模拟回测结果
            dates = predictions["datetime"].unique()
            returns = np.random.randn(len(dates)) * 0.01  # 日收益率
            benchmark_returns = np.random.randn(len(dates)) * 0.008  # 基准收益率
            costs = np.random.rand(len(dates)) * 0.0001  # 交易成本
            
            results = {
                "return": pd.Series(returns, index=dates),
                "bench": pd.Series(benchmark_returns, index=dates),
                "cost": pd.Series(costs, index=dates),
                "positions": predictions[
                    ["datetime", "instrument", "score"]
                ].copy()
            }
            
            self._log("策略执行完成（模拟）")
            return results
            
        except Exception as e:
            self._log(f"策略执行失败: {str(e)}")
            raise
    
    def _evaluate_results(
        self, strategy_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """评估结果"""
        try:
            # 计算评估指标
            returns = strategy_results["return"]
            benchmark_returns = strategy_results["bench"]
            costs = strategy_results["cost"]
            
            # 计算超额收益
            excess_return_without_cost = returns - benchmark_returns
            excess_return_with_cost = excess_return_without_cost - costs
            
            # 计算风险指标
            def calculate_risk_metrics(series):
                return {
                    "mean": series.mean(),
                    "std": series.std(),
                    "annualized_return": series.mean() * 252,
                    "information_ratio": (
                        series.mean() / series.std() * np.sqrt(252)
                    ),
                    "max_drawdown": self._calculate_max_drawdown(series)
                }
            
            analysis = {
                "excess_return_without_cost": calculate_risk_metrics(
                    excess_return_without_cost
                ),
                "excess_return_with_cost": calculate_risk_metrics(
                    excess_return_with_cost
                )
            }
            
            self._log("结果评估完成")
            return {
                "analysis": analysis,
                "strategy_results": strategy_results
            }
            
        except Exception as e:
            self._log(f"结果评估失败: {str(e)}")
            raise
    
    def _calculate_max_drawdown(self, returns: pd.Series) -> float:
        """计算最大回撤"""
        cumulative = (1 + returns).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        return drawdown.min()
    
    def _save_results(self, evaluation_results: Dict[str, Any]):
        """保存结果"""
        try:
            if not self.config["evaluation"]["save_results"]:
                return
            
            # 创建输出目录
            output_dir = Path(self.config["evaluation"]["output_dir"])
            output_dir.mkdir(exist_ok=True)
            
            # 保存结果
            results_file = output_dir / f"{self.workflow_id}_results.json"
            with open(results_file, 'w', encoding='utf-8') as f:
                # 转换pandas对象为可序列化格式
                serializable_results = self._make_serializable(
                    evaluation_results
                )
                json.dump(
                    serializable_results,
                    f,
                    indent=2,
                    ensure_ascii=False
                )
            
            self._log(f"结果已保存到: {results_file}")
            
        except Exception as e:
            self._log(f"结果保存失败: {str(e)}")
            raise
    
    def _make_serializable(self, obj):
        """将对象转换为可序列化格式"""
        if isinstance(obj, pd.DataFrame):
            return obj.to_dict()
        elif isinstance(obj, pd.Series):
            return obj.to_dict()
        elif isinstance(obj, dict):
            return {k: self._make_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._make_serializable(item) for item in obj]
        elif isinstance(obj, (datetime, pd.Timestamp)):
            return obj.isoformat()
        else:
            return obj
    
    def _log(self, message: str):
        """记录日志"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.logs.append(log_entry)
        logger.info(f"[WorkflowManager] {message}")
    
    def get_status(self) -> Dict[str, Any]:
        """获取工作流状态"""
        return {
            "workflow_id": self.workflow_id,
            "status": self.status,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration": (
                self.end_time - self.start_time
            ) if self.start_time and self.end_time else None,
            "config": self.config
        }
    
    def save_config(self, file_path: str):
        """保存配置到文件"""
        with open(file_path, 'w', encoding='utf-8') as f:
            if file_path.endswith('.yaml') or file_path.endswith('.yml'):
                yaml.dump(
                    self.config,
                    f,
                    default_flow_style=False,
                    allow_unicode=True
                )
            else:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        self._log(f"配置已保存到: {file_path}")


# 全局工作流管理器实例
_global_workflow_manager = None


def get_workflow_manager(
    config_path: Optional[str] = None,
    config_dict: Optional[Dict] = None
) -> WorkflowManager:
    """
    获取全局工作流管理器实例
    
    Args:
        config_path: 配置文件路径
        config_dict: 配置字典
        
    Returns:
        WorkflowManager实例
    """
    global _global_workflow_manager
    
    if _global_workflow_manager is None:
        _global_workflow_manager = WorkflowManager(config_path, config_dict)
    
    return _global_workflow_manager


def execute_workflow(
    workflow_config: Dict[str, Any],
    start_date: str,
    end_date: str,
    parallel: bool = False
) -> Dict[str, Any]:
    """
    执行工作流
    
    Args:
        workflow_config: 工作流配置
        start_date: 开始日期
        end_date: 结束日期
        parallel: 是否并行执行
        
    Returns:
        工作流执行结果
    """
    try:
        # 创建工作流管理器
        manager = WorkflowManager(config_dict=workflow_config)
        
        # 更新配置中的日期
        if "data" in workflow_config:
            workflow_config["data"]["start_time"] = start_date
            workflow_config["data"]["end_time"] = end_date
        
        # 执行工作流
        result = manager.run()
        
        # 添加执行信息
        result.update({
            "execution_time": f"{result.get('duration', 'unknown')}",
            "tasks_completed": 7,  # 默认7个步骤
            "tasks_total": 7
        })
        
        return result
        
    except Exception as e:
        logger.error(f"执行工作流失败: {e}")
        return {
            "success": False,
            "error": str(e),
            "execution_time": "0s",
            "tasks_completed": 0,
            "tasks_total": 7
        }


def list_workflows() -> List[Dict[str, Any]]:
    """
    获取工作流列表
    
    Returns:
        工作流列表
    """
    try:
        # 返回预定义的工作流模板
        workflows = [
            {
                "id": "default_workflow",
                "name": "默认工作流",
                "description": "标准的QLib量化工作流",
                "steps": [
                    "数据准备",
                    "特征工程",
                    "模型训练",
                    "预测生成",
                    "策略执行",
                    "回测评估",
                    "结果保存"
                ]
            },
            {
                "id": "simple_workflow",
                "name": "简化工作流",
                "description": "简化的量化工作流，适用于快速测试",
                "steps": [
                    "数据准备",
                    "策略执行",
                    "回测评估"
                ]
            },
            {
                "id": "advanced_workflow",
                "name": "高级工作流",
                "description": "包含高级功能的量化工作流",
                "steps": [
                    "数据准备",
                    "特征工程",
                    "特征选择",
                    "模型训练",
                    "模型验证",
                    "预测生成",
                    "策略执行",
                    "回测评估",
                    "风险分析",
                    "结果保存"
                ]
            }
        ]
        
        return workflows
        
    except Exception as e:
        logger.error(f"获取工作流列表失败: {e}")
        return []
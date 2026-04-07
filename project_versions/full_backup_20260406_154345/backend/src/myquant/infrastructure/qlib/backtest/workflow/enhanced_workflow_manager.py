"""
QLib增强工作流管理器

该模块实现了增强的工作流管理功能，包括：
- 自动化回测集成
- 增强的工作流编排
- 实时监控和报告
- 分布式执行支持
- 结果分析和可视化
"""

import json
import yaml
import logging
import numpy as np
import pandas as pd
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime, timedelta
from pathlib import Path
import threading
import time

from .enhanced_config_parser import EnhancedConfigParser
from .enhanced_task_scheduler import EnhancedTaskScheduler, TaskPriority

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EnhancedWorkflowManager:
    """
    增强工作流管理器
    
    该类扩展了基础工作流管理器，添加了更多高级功能：
    - 自动化回测集成
    - 实时监控和报告
    - 分布式执行支持
    - 结果分析和可视化
    - 工作流模板系统
    """
    
    def __init__(
        self,
        config_path: Optional[str] = None,
        config_dict: Optional[Dict] = None,
        enable_monitoring: bool = True,
        enable_auto_save: bool = True
    ):
        """
        初始化增强工作流管理器
        
        Args:
            config_path: 配置文件路径
            config_dict: 配置字典
            enable_monitoring: 启用实时监控
            enable_auto_save: 启用自动保存
        """
        self.config_parser = EnhancedConfigParser()
        self.task_scheduler = EnhancedTaskScheduler()
        self.enable_monitoring = enable_monitoring
        self.enable_auto_save = enable_auto_save
        
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
        self.metrics = {}
        
        # 监控数据
        self.monitoring_data = {
            'task_progress': {},
            'resource_usage': {},
            'performance_metrics': {}
        }
        
        # 回测结果
        self.backtest_results = {}
        
        # 线程安全
        self.monitoring_thread = None
        self.lock = threading.RLock()
        
        logger.info(f"[EnhancedWorkflowManager] 工作流管理器初始化完成，ID: {self.workflow_id}")
    
    def _generate_workflow_id(self) -> str:
        """生成工作流ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"enhanced_workflow_{timestamp}"
    
    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            "workflow": {
                "name": "enhanced_workflow",
                "description": "默认增强QLib工作流",
                "version": "2.0.0",
                "enable_monitoring": True,
                "enable_auto_save": True
            },
            "data": {
                "provider": "qlib",
                "market": "csi300",
                "start_time": "2017-01-01",
                "end_time": "2020-08-01",
                "features": ["Alpha158"],
                "instruments": "all"
            },
            "model": {
                "type": "lgb",
                "loss": "mse",
                "learning_rate": 0.1,
                "num_leaves": 31,
                "num_threads": 8
            },
            "strategy": {
                "type": "enhanced_indexing",
                "riskmodel_root": "${RISK_MODEL_PATH}/riskmodel",
                "market": "csi500",
                "turn_limit": 0.2
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
                    "max_drawdown",
                    "tracking_error"
                ],
                "save_results": True,
                "output_dir": "results",
                "generate_plots": True,
                "risk_analysis": True
            }
        }
    
    def run(self) -> Dict[str, Any]:
        """
        运行完整的增强工作流
        
        Returns:
            工作流执行结果
        """
        try:
            self.start_time = datetime.now()
            self.status = "running"
            self._log(f"开始执行增强工作流: {self.config['workflow']['name']}")
            
            # 启动监控线程
            if self.enable_monitoring:
                self._start_monitoring()
            
            # 使用任务调度器运行工作流
            results = self._run_with_task_scheduler()
            
            self.end_time = datetime.now()
            self.status = "completed"
            self._log(f"工作流执行完成，耗时: {self.end_time - self.start_time}")
            
            # 生成最终报告
            final_report = self._generate_final_report(results)
            
            # 自动保存结果
            if self.enable_auto_save:
                self._auto_save_results(final_report)
            
            return final_report
            
        except Exception as e:
            self.status = "failed"
            self.end_time = datetime.now()
            self._log(f"工作流执行失败: {str(e)}")
            logger.error(f"[EnhancedWorkflowManager] 工作流执行失败: {str(e)}")
            
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
        finally:
            # 停止监控
            if self.monitoring_thread:
                self.monitoring_thread.join(timeout=5)
    
    def _run_with_task_scheduler(self) -> Dict[str, Any]:
        """使用任务调度器运行工作流"""
        # 定义工作流任务
        tasks = []
        
        # 数据准备任务
        data_task_id = "data_preparation"
        self.task_scheduler.add_task(
            task_id=data_task_id,
            name="数据准备",
            func=self._prepare_data,
            priority=TaskPriority.HIGH,
            tags={"phase": "data", "critical": "true"}
        )
        tasks.append(data_task_id)
        
        # 特征工程任务
        feature_task_id = "feature_engineering"
        self.task_scheduler.add_task(
            task_id=feature_task_id,
            name="特征工程",
            func=self._feature_engineering,
            dependencies=[data_task_id],
            priority=TaskPriority.HIGH,
            tags={"phase": "feature", "critical": "true"}
        )
        tasks.append(feature_task_id)
        
        # 模型训练任务
        model_task_id = "model_training"
        self.task_scheduler.add_task(
            task_id=model_task_id,
            name="模型训练",
            func=self._train_model,
            dependencies=[feature_task_id],
            priority=TaskPriority.NORMAL,
            tags={"phase": "model", "critical": "true"}
        )
        tasks.append(model_task_id)
        
        # 预测生成任务
        prediction_task_id = "prediction_generation"
        self.task_scheduler.add_task(
            task_id=prediction_task_id,
            name="预测生成",
            func=self._generate_predictions,
            dependencies=[model_task_id],
            priority=TaskPriority.NORMAL,
            tags={"phase": "prediction"}
        )
        tasks.append(prediction_task_id)
        
        # 策略执行任务
        strategy_task_id = "strategy_execution"
        self.task_scheduler.add_task(
            task_id=strategy_task_id,
            name="策略执行",
            func=self._execute_strategy,
            dependencies=[prediction_task_id],
            priority=TaskPriority.HIGH,
            tags={"phase": "strategy", "critical": "true"}
        )
        tasks.append(strategy_task_id)
        
        # 回测评估任务
        evaluation_task_id = "backtest_evaluation"
        self.task_scheduler.add_task(
            task_id=evaluation_task_id,
            name="回测评估",
            func=self._evaluate_results,
            dependencies=[strategy_task_id],
            priority=TaskPriority.HIGH,
            tags={"phase": "evaluation", "critical": "true"}
        )
        tasks.append(evaluation_task_id)
        
        # 运行工作流
        workflow_results = self.task_scheduler.run_workflow(tasks)
        
        # 收集结果
        results = {}
        for task_id in tasks:
            task = self.task_scheduler.get_all_tasks().get(task_id)
            if task:
                results[task_id] = {
                    "status": task.status.value,
                    "result": task.result,
                    "start_time": task.start_time,
                    "end_time": task.end_time,
                    "error": str(task.error) if task.error else None
                }
        
        return results
    
    def _prepare_data(self) -> pd.DataFrame:
        """准备数据"""
        try:
            self._update_monitoring_data("data_preparation", "running", 0)
            
            # 导入数据处理器
            from qlib_core.qlib_dataprocessing.features.alpha158 import (
                Alpha158Processor
            )
            
            # 创建数据提供器
            data_config = self.config["data"]
            processor = Alpha158Processor(verbose=True)
            
            # 模拟数据加载（实际应从数据提供器加载）
            dates = pd.date_range(
                start=data_config["start_time"],
                end=data_config["end_time"],
                freq="D"
            )
            
            # 过滤交易日
            dates = dates[dates.weekday < 5]
            
            # 生成股票代码
            instruments = [f"SH{600000+i:06d}" for i in range(100)]
            
            # 创建数据
            data_list = []
            for date in dates:
                for instrument in instruments:
                    base_price = 10 + np.random.randn() * 2
                    data_list.append({
                        "datetime": date,
                        "instrument": instrument,
                        "open": base_price * (1 + np.random.randn() * 0.01),
                        "high": base_price * (1 + abs(np.random.randn()) * 0.02),
                        "low": base_price * (1 - abs(np.random.randn()) * 0.02),
                        "close": base_price * (1 + np.random.randn() * 0.01),
                        "volume": int(1000000 + np.random.randn() * 200000),
                        "amount": base_price * (1000000 + np.random.randn() * 200000)
                    })
            
            df = pd.DataFrame(data_list)
            
            self._update_monitoring_data("data_preparation", "completed", 100)
            self._log(f"数据准备完成，形状: {df.shape}")
            return df
            
        except Exception as e:
            self._update_monitoring_data("data_preparation", "failed", 0)
            self._log(f"数据准备失败: {str(e)}")
            raise
    
    def _feature_engineering(self, data: pd.DataFrame) -> pd.DataFrame:
        """特征工程"""
        try:
            self._update_monitoring_data("feature_engineering", "running", 0)
            
            # 导入Alpha158处理器
            from qlib_core.qlib_dataprocessing.features.alpha158 import (
                Alpha158Processor
            )
            
            processor = Alpha158Processor(verbose=True)
            
            # 按股票分组处理
            results = []
            instruments = data["instrument"].unique()
            
            for i, instrument in enumerate(instruments):
                stock_data = data[data["instrument"] == instrument].copy()
                stock_data = stock_data.sort_values("datetime")
                
                # 计算特征
                features = processor.transform(stock_data)
                results.append(features)
                
                # 更新进度
                progress = (i + 1) / len(instruments) * 100
                self._update_monitoring_data(
                    "feature_engineering", "running", progress
                )
            
            # 合并结果
            features_df = pd.concat(results, ignore_index=True)
            
            self._update_monitoring_data("feature_engineering", "completed", 100)
            self._log(f"特征工程完成，形状: {features_df.shape}")
            return features_df
            
        except Exception as e:
            self._update_monitoring_data("feature_engineering", "failed", 0)
            self._log(f"特征工程失败: {str(e)}")
            raise
    
    def _train_model(self, features: pd.DataFrame):
        """训练模型"""
        try:
            self._update_monitoring_data("model_training", "running", 0)
            
            # 模拟模型训练（实际应使用真实模型训练）
            import time
            time.sleep(2)  # 模拟训练时间
            
            model_info = {
                "model_type": "lgb",
                "features_count": features.shape[1],
                "training_samples": len(features),
                "model_path": f"models/{self.workflow_id}_model.pkl"
            }
            
            self._update_monitoring_data("model_training", "completed", 100)
            self._log("模型训练完成（模拟）")
            return model_info
            
        except Exception as e:
            self._update_monitoring_data("model_training", "failed", 0)
            self._log(f"模型训练失败: {str(e)}")
            raise
    
    def _generate_predictions(
        self, model, features: pd.DataFrame
    ) -> pd.DataFrame:
        """生成预测"""
        try:
            self._update_monitoring_data("prediction_generation", "running", 0)
            
            # 模拟预测生成
            predictions = features.copy()
            predictions["score"] = np.random.randn(len(features))
            
            self._update_monitoring_data("prediction_generation", "completed", 100)
            self._log(f"预测生成完成，形状: {predictions.shape}")
            return predictions
            
        except Exception as e:
            self._update_monitoring_data("prediction_generation", "failed", 0)
            self._log(f"预测生成失败: {str(e)}")
            raise
    
    def _execute_strategy(self, predictions: pd.DataFrame) -> Dict[str, Any]:
        """执行策略"""
        try:
            self._update_monitoring_data("strategy_execution", "running", 0)
            
            # 导入增强指数策略
            from qlib_core.backtest.portfolio_management.strategy.enhanced_indexing_strategy_extensions import (
                EnhancedIndexingStrategyExtensions
            )
            
            # 创建策略实例
            strategy_config = self.config["strategy"]
            strategy = EnhancedIndexingStrategyExtensions(**strategy_config)
            
            # 模拟策略执行
            dates = predictions["datetime"].unique()
            returns = np.random.randn(len(dates)) * 0.01
            benchmark_returns = np.random.randn(len(dates)) * 0.008
            costs = np.random.rand(len(dates)) * 0.0001
            
            results = {
                "return": pd.Series(returns, index=dates),
                "bench": pd.Series(benchmark_returns, index=dates),
                "cost": pd.Series(costs, index=dates),
                "positions": predictions[["datetime", "instrument", "score"]].copy(),
                "strategy_config": strategy_config
            }
            
            self._update_monitoring_data("strategy_execution", "completed", 100)
            self._log("策略执行完成（模拟）")
            return results
            
        except Exception as e:
            self._update_monitoring_data("strategy_execution", "failed", 0)
            self._log(f"策略执行失败: {str(e)}")
            raise
    
    def _evaluate_results(
        self, strategy_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """评估结果"""
        try:
            self._update_monitoring_data("backtest_evaluation", "running", 0)
            
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
                    "max_drawdown": self._calculate_max_drawdown(series),
                    "sharpe_ratio": (
                        series.mean() / series.std() * np.sqrt(252)
                    ),
                    "calmar_ratio": (
                        series.mean() * 252 / abs(self._calculate_max_drawdown(series))
                    )
                }
            
            analysis = {
                "excess_return_without_cost": calculate_risk_metrics(
                    excess_return_without_cost
                ),
                "excess_return_with_cost": calculate_risk_metrics(
                    excess_return_with_cost
                )
            }
            
            # 添加高级分析
            if self.config["evaluation"].get("risk_analysis", True):
                analysis["risk_analysis"] = self._perform_risk_analysis(
                    strategy_results
                )
            
            self._update_monitoring_data("backtest_evaluation", "completed", 100)
            self._log("结果评估完成")
            return {
                "analysis": analysis,
                "strategy_results": strategy_results
            }
            
        except Exception as e:
            self._update_monitoring_data("backtest_evaluation", "failed", 0)
            self._log(f"结果评估失败: {str(e)}")
            raise
    
    def _calculate_max_drawdown(self, returns: pd.Series) -> float:
        """计算最大回撤"""
        cumulative = (1 + returns).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        return drawdown.min()
    
    def _perform_risk_analysis(
        self, strategy_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """执行风险分析"""
        try:
            # 导入增强指数策略扩展
            from qlib_core.backtest.portfolio_management.strategy.enhanced_indexing_strategy_extensions import (
                EnhancedIndexingStrategyExtensions
            )
            
            # 创建策略实例
            strategy_config = self.config["strategy"]
            strategy = EnhancedIndexingStrategyExtensions(**strategy_config)
            
            # 模拟风险数据
            import numpy as np
            factor_exp = np.random.randn(100, 10)  # 100只股票，10个因子
            factor_cov = np.random.randn(10, 10)
            factor_cov = factor_cov @ factor_cov.T  # 确保正定
            specific_risk = np.random.rand(100) * 0.1
            
            # 模拟投资组合和基准权重
            portfolio_weights = {
                f"SH{600000+i:06d}": np.random.rand() for i in range(50)
            }
            # 归一化权重
            total_weight = sum(portfolio_weights.values())
            portfolio_weights = {
                k: v/total_weight for k, v in portfolio_weights.items()
            }
            
            benchmark_weights = {
                f"SH{600000+i:06d}": 0.01 for i in range(100)
            }
            # 归一化基准权重
            total_bench_weight = sum(benchmark_weights.values())
            benchmark_weights = {
                k: v/total_bench_weight for k, v in benchmark_weights.items()
            }
            
            # 计算风险指标
            risk_data = (factor_exp, factor_cov, specific_risk)
            
            risk_metrics = strategy.get_risk_metrics(
                portfolio_weights, benchmark_weights, risk_data
            )
            
            return risk_metrics
            
        except Exception as e:
            self._log(f"风险分析失败: {str(e)}")
            return {"error": str(e)}
    
    def _start_monitoring(self):
        """启动监控线程"""
        def monitoring_loop():
            while self.status == "running":
                try:
                    # 更新资源使用情况
                    stats = self.task_scheduler.get_scheduler_stats()
                    self.monitoring_data['resource_usage'] = stats.get(
                        'resource_utilization', {}
                    )
                    
                    # 更新任务进度
                    self.monitoring_data['task_progress'] = {
                        task_id: {
                            "status": task.status.value,
                            "progress": self._calculate_task_progress(task)
                        }
                        for task_id, task in self.task_scheduler.get_all_tasks().items()
                    }
                    
                    # 计算性能指标
                    self.monitoring_data['performance_metrics'] = {
                        "workflow_duration": (
                            datetime.now() - self.start_time
                        ).total_seconds() if self.start_time else 0,
                        "tasks_per_second": len(
                            self.task_scheduler.get_all_tasks()
                        ) / max(1, (
                            datetime.now() - self.start_time
                        ).total_seconds()),
                        "average_task_duration": (
                            stats.get('average_execution_time', timedelta(0)
                        ).total_seconds()
                    }
                    
                    time.sleep(5)  # 每5秒更新一次
                    
                except Exception as e:
                    logger.error(f"监控线程错误: {e}")
        
        self.monitoring_thread = threading.Thread(target=monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        logger.info("监控线程已启动")
    
    def _calculate_task_progress(self, task) -> float:
        """计算任务进度"""
        if task.status.value in ["completed", "failed", "cancelled"]:
            return 100.0
        elif task.status.value == "running":
            if task.start_time:
                elapsed = (datetime.now() - task.start_time).total_seconds()
                # 估算进度（基于经验值）
                estimated_duration = 60  # 假设每个任务60秒
                return min(100.0, elapsed / estimated_duration * 100)
        return 0.0
    
    def _update_monitoring_data(
        self, phase: str, status: str, progress: float
    ):
        """更新监控数据"""
        with self.lock:
            if phase not in self.monitoring_data:
                self.monitoring_data[phase] = {
                    "status": status,
                    "progress": progress,
                    "last_update": datetime.now()
                }
            else:
                self.monitoring_data[phase].update({
                    "status": status,
                    "progress": progress,
                    "last_update": datetime.now()
                })
    
    def _generate_final_report(self, workflow_results: Dict[str, Any]) -> Dict[str, Any]:
        """生成最终报告"""
        return {
            "workflow_id": self.workflow_id,
            "status": self.status,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration": self.end_time - self.start_time if self.end_time else None,
            "results": workflow_results,
            "config": self.config,
            "logs": self.logs,
            "monitoring_data": self.monitoring_data,
            "scheduler_stats": self.task_scheduler.get_scheduler_stats(),
            "summary": self._generate_summary(workflow_results)
        }
    
    def _generate_summary(self, workflow_results: Dict[str, Any]) -> Dict[str, Any]:
        """生成工作流摘要"""
        total_tasks = len(workflow_results)
        completed_tasks = sum(
            1 for result in workflow_results.values()
            if result["status"] == "completed"
        )
        failed_tasks = sum(
            1 for result in workflow_results.values()
            if result["status"] == "failed"
        )
        
        return {
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "failed_tasks": failed_tasks,
            "success_rate": completed_tasks / total_tasks * 100 if total_tasks > 0 else 0,
            "total_duration": (
                self.end_time - self.start_time
            ).total_seconds() if self.end_time and self.start_time else 0
        }
    
    def _auto_save_results(self, final_report: Dict[str, Any]):
        """自动保存结果"""
        try:
            output_dir = Path(self.config["evaluation"]["output_dir"])
            output_dir.mkdir(exist_ok=True)
            
            # 保存完整报告
            report_file = output_dir / f"{self.workflow_id}_report.json"
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(final_report, f, indent=2, ensure_ascii=False)
            
            # 保存监控数据
            monitoring_file = output_dir / f"{self.workflow_id}_monitoring.json"
            with open(monitoring_file, 'w', encoding='utf-8') as f:
                json.dump(self.monitoring_data, f, indent=2, ensure_ascii=False)
            
            # 生成图表（如果启用）
            if self.config["evaluation"].get("generate_plots", True):
                self._generate_plots(final_report, output_dir)
            
            self._log(f"结果已自动保存到: {output_dir}")
            
        except Exception as e:
            self._log(f"自动保存结果失败: {str(e)}")
    
    def _generate_plots(self, final_report: Dict[str, Any], output_dir: Path):
        """生成图表"""
        try:
            import matplotlib.pyplot as plt
            
            # 创建图表目录
            plots_dir = output_dir / "plots"
            plots_dir.mkdir(exist_ok=True)
            
            # 任务状态饼图
            workflow_results = final_report.get("results", {})
            task_statuses = [
                result["status"] for result in workflow_results.values()
            ]
            status_counts = {
                status: task_statuses.count(status) 
                for status in set(task_statuses)
            }
            
            plt.figure(figsize=(10, 6))
            plt.pie(
                status_counts.values(), 
                labels=status_counts.keys(),
                autopct='%1.1f%%'
            )
            plt.title("任务状态分布")
            plt.savefig(plots_dir / "task_status_pie.png")
            plt.close()
            
            # 监控数据时间线图
            monitoring_data = final_report.get("monitoring_data", {})
            if monitoring_data:
                phases = list(monitoring_data.keys())
                progress_data = []
                
                for phase in phases:
                    phase_data = monitoring_data[phase]
                    if "progress" in phase_data:
                        progress_data.append(phase_data["progress"])
                
                if progress_data:
                    plt.figure(figsize=(12, 6))
                    plt.plot(range(len(progress_data)), progress_data, marker='o')
                    plt.xticks(range(len(phases)), phases, rotation=45)
                    plt.ylabel("进度 (%)")
                    plt.title("工作流阶段进度")
                    plt.grid(True)
                    plt.tight_layout()
                    plt.savefig(plots_dir / "progress_timeline.png")
                    plt.close()
            
            self._log(f"图表已生成到: {plots_dir}")
            
        except Exception as e:
            self._log(f"生成图表失败: {str(e)}")
    
    def _log(self, message: str):
        """记录日志"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.logs.append(log_entry)
        logger.info(f"[EnhancedWorkflowManager] {message}")
    
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
            "config": self.config,
            "monitoring_data": self.monitoring_data,
            "scheduler_stats": self.task_scheduler.get_scheduler_stats()
        }
    
    def get_real_time_monitoring(self) -> Dict[str, Any]:
        """获取实时监控数据"""
        return self.monitoring_data.copy()


# 导出主要类
__all__ = [
    'EnhancedWorkflowManager'
]
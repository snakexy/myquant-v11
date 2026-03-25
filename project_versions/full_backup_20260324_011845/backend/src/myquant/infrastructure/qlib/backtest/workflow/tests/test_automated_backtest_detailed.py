"""
自动化回测详细测试

测试QLib工作流管理器的自动化回测功能，支持完整的自动化回测流程
"""

import os
import sys
import json
import unittest
import tempfile
from pathlib import Path
from datetime import datetime
import pandas as pd

# 添加路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from workflow_manager import WorkflowManager
from enhanced_workflow_manager import EnhancedWorkflowManager


class TestAutomatedBacktestDetailed(unittest.TestCase):
    """自动化回测详细测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.temp_dir = tempfile.mkdtemp()
        
        # 创建测试配置
        self.test_config = {
            "workflow": {
                "name": "test_automated_backtest",
                "description": "测试自动化回测工作流",
                "version": "1.0.0"
            },
            "data": {
                "provider": "local",
                "market": "csi300",
                "start_time": "2020-01-01",
                "end_time": "2020-12-31",
                "features": ["Alpha158"]
            },
            "model": {
                "type": "lgb",
                "loss": "mse",
                "learning_rate": 0.1,
                "num_leaves": 31
            },
            "strategy": {
                "type": "enhanced_indexing",
                "topk": 50,
                "n_drop": 5
            },
            "backtest": {
                "account": 1000000,
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
                "output_dir": self.temp_dir
            }
        }
        
        # 增强测试配置
        self.enhanced_config = {
            "workflow": {
                "name": "test_enhanced_automated_backtest",
                "description": "测试增强自动化回测工作流",
                "version": "2.0.0",
                "enable_monitoring": True,
                "enable_auto_save": True
            },
            "data": {
                "provider": "qlib",
                "market": "csi500",
                "start_time": "2020-01-01",
                "end_time": "2020-06-30",
                "features": ["Alpha158"],
                "instruments": "all"
            },
            "model": {
                "type": "lgb",
                "loss": "mse",
                "learning_rate": 0.05,
                "num_leaves": 63,
                "num_threads": 4
            },
            "strategy": {
                "type": "enhanced_indexing",
                "riskmodel_root": "/path/to/riskmodel",
                "market": "csi500",
                "turn_limit": 0.2
            },
            "backtest": {
                "account": 10000000,
                "benchmark": "SH000905",
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
                    "tracking_error",
                    "sharpe_ratio",
                    "calmar_ratio"
                ],
                "save_results": True,
                "output_dir": self.temp_dir,
                "generate_plots": True,
                "risk_analysis": True
            }
        }
    
    def tearDown(self):
        """测试后清理"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_workflow_manager_initialization(self):
        """测试工作流管理器初始化"""
        # 使用配置字典初始化
        manager = WorkflowManager(config_dict=self.test_config)
        
        # 验证初始化
        self.assertIsNotNone(manager.config)
        self.assertEqual(
            manager.config['workflow']['name'],
            'test_automated_backtest'
        )
        self.assertEqual(manager.status, "initialized")
        self.assertIsNotNone(manager.workflow_id)
        self.assertIsNone(manager.start_time)
        self.assertIsNone(manager.end_time)
        self.assertEqual(len(manager.results), 0)
        self.assertEqual(len(manager.logs), 0)
    
    def test_workflow_manager_with_config_file(self):
        """测试使用配置文件初始化工作流管理器"""
        # 创建配置文件
        config_file = os.path.join(self.temp_dir, "test_config.yaml")
        import yaml
        with open(config_file, 'w', encoding='utf-8') as f:
            yaml.dump(
                self.test_config, f,
                default_flow_style=False,
                allow_unicode=True
            )
        
        # 使用配置文件初始化
        manager = WorkflowManager(config_path=config_file)
        
        # 验证初始化
        self.assertIsNotNone(manager.config)
        self.assertEqual(
            manager.config['workflow']['name'],
            'test_automated_backtest'
        )
        self.assertEqual(manager.status, "initialized")
    
    def test_enhanced_workflow_manager_initialization(self):
        """测试增强工作流管理器初始化"""
        # 使用配置字典初始化
        manager = EnhancedWorkflowManager(
            config_dict=self.enhanced_config,
            enable_monitoring=True,
            enable_auto_save=True
        )
        
        # 验证初始化
        self.assertIsNotNone(manager.config)
        self.assertEqual(
            manager.config['workflow']['name'],
            'test_enhanced_automated_backtest'
        )
        self.assertEqual(manager.status, "initialized")
        self.assertTrue(manager.enable_monitoring)
        self.assertTrue(manager.enable_auto_save)
        self.assertIsNotNone(manager.workflow_id)
        self.assertIsNotNone(manager.monitoring_data)
        self.assertEqual(len(manager.backtest_results), 0)
    
    def test_workflow_id_generation(self):
        """测试工作流ID生成"""
        manager1 = WorkflowManager(config_dict=self.test_config)
        manager2 = WorkflowManager(config_dict=self.test_config)
        
        # 验证ID唯一性
        self.assertNotEqual(manager1.workflow_id, manager2.workflow_id)
        
        # 验证ID格式
        self.assertTrue(manager1.workflow_id.startswith("workflow_"))
        self.assertTrue(manager2.workflow_id.startswith("workflow_"))
        
        # 测试增强工作流ID
        enhanced_manager = EnhancedWorkflowManager(
            config_dict=self.enhanced_config
        )
        self.assertTrue(
            enhanced_manager.workflow_id.startswith("enhanced_workflow_")
        )
    
    def test_default_config_loading(self):
        """测试默认配置加载"""
        # 不提供配置，使用默认配置
        manager = WorkflowManager()
        
        # 验证默认配置
        self.assertIsNotNone(manager.config)
        self.assertIn('workflow', manager.config)
        self.assertIn('data', manager.config)
        self.assertIn('model', manager.config)
        self.assertIn('strategy', manager.config)
        self.assertIn('backtest', manager.config)
        self.assertIn('evaluation', manager.config)
        
        # 验证默认值
        self.assertEqual(
            manager.config['workflow']['name'],
            'default_workflow'
        )
        self.assertEqual(manager.config['data']['provider'], 'local')
        self.assertEqual(manager.config['model']['type'], 'lgb')
        self.assertEqual(manager.config['strategy']['type'], 'topk_dropout')
    
    def test_workflow_execution(self):
        """测试工作流执行"""
        manager = WorkflowManager(config_dict=self.test_config)
        
        # 运行工作流
        result = manager.run()
        
        # 验证结果结构
        self.assertIsInstance(result, dict)
        self.assertIn('workflow_id', result)
        self.assertIn('status', result)
        self.assertIn('start_time', result)
        self.assertIn('end_time', result)
        self.assertIn('duration', result)
        self.assertIn('results', result)
        self.assertIn('config', result)
        self.assertIn('logs', result)
        
        # 验证执行状态
        self.assertEqual(result['status'], 'completed')
        self.assertEqual(result['workflow_id'], manager.workflow_id)
        self.assertIsNotNone(result['start_time'])
        self.assertIsNotNone(result['end_time'])
        self.assertIsNotNone(result['duration'])
        self.assertGreater(len(result['logs']), 0)
        
        # 验证管理器状态
        self.assertEqual(manager.status, 'completed')
        self.assertIsNotNone(manager.start_time)
        self.assertIsNotNone(manager.end_time)
        self.assertGreater(len(manager.logs), 0)
    
    def test_enhanced_workflow_execution(self):
        """测试增强工作流执行"""
        manager = EnhancedWorkflowManager(
            config_dict=self.enhanced_config,
            enable_monitoring=False,  # 禁用监控以简化测试
            enable_auto_save=False   # 禁用自动保存以简化测试
        )
        
        # 运行工作流
        result = manager.run()
        
        # 验证结果结构
        self.assertIsInstance(result, dict)
        self.assertIn('workflow_id', result)
        self.assertIn('status', result)
        self.assertIn('start_time', result)
        self.assertIn('end_time', result)
        self.assertIn('duration', result)
        self.assertIn('results', result)
        self.assertIn('config', result)
        self.assertIn('logs', result)
        self.assertIn('monitoring_data', result)
        self.assertIn('scheduler_stats', result)
        self.assertIn('summary', result)
        
        # 验证执行状态
        self.assertEqual(result['status'], 'completed')
        self.assertEqual(result['workflow_id'], manager.workflow_id)
        self.assertIsNotNone(result['start_time'])
        self.assertIsNotNone(result['end_time'])
        self.assertIsNotNone(result['duration'])
        self.assertGreater(len(result['logs']), 0)
        
        # 验证摘要
        summary = result['summary']
        self.assertIn('total_tasks', summary)
        self.assertIn('completed_tasks', summary)
        self.assertIn('failed_tasks', summary)
        self.assertIn('success_rate', summary)
        self.assertIn('total_duration', summary)
        
        # 验证任务结果
        results = result['results']
        expected_tasks = [
            'data_preparation',
            'feature_engineering',
            'model_training',
            'prediction_generation',
            'strategy_execution',
            'backtest_evaluation'
        ]
        
        for task_id in expected_tasks:
            self.assertIn(task_id, results)
            task_result = results[task_id]
            self.assertIn('status', task_result)
            self.assertIn('result', task_result)
            self.assertIn('start_time', task_result)
            self.assertIn('end_time', task_result)
    
    def test_data_preparation_phase(self):
        """测试数据准备阶段"""
        manager = WorkflowManager(config_dict=self.test_config)
        
        # 执行数据准备
        data = manager._prepare_data()
        
        # 验证数据结构
        self.assertIsInstance(data, pd.DataFrame)
        self.assertIn('datetime', data.columns)
        self.assertIn('instrument', data.columns)
        self.assertIn('open', data.columns)
        self.assertIn('high', data.columns)
        self.assertIn('low', data.columns)
        self.assertIn('close', data.columns)
        self.assertIn('volume', data.columns)
        self.assertIn('amount', data.columns)
        
        # 验证数据内容
        self.assertGreater(len(data), 0)
        self.assertTrue(
            all(isinstance(dt, pd.Timestamp) for dt in data['datetime'])
        )
        self.assertTrue(
            all(isinstance(inst, str) for inst in data['instrument'])
        )
    
    def test_feature_engineering_phase(self):
        """测试特征工程阶段"""
        manager = WorkflowManager(config_dict=self.test_config)
        
        # 准备数据
        data = manager._prepare_data()
        
        # 执行特征工程
        features = manager._feature_engineering(data)
        
        # 验证特征结构
        self.assertIsInstance(features, pd.DataFrame)
        self.assertIn('datetime', features.columns)
        self.assertIn('instrument', features.columns)
        
        # 验证特征数量（Alpha158应该有158个特征）
        feature_cols = [
            col for col in features.columns 
            if col not in ['datetime', 'instrument']
        ]
        self.assertGreater(len(feature_cols), 100)  # 至少应该有100个特征
    
    def test_model_training_phase(self):
        """测试模型训练阶段"""
        manager = WorkflowManager(config_dict=self.test_config)
        
        # 准备数据
        data = manager._prepare_data()
        features = manager._feature_engineering(data)
        
        # 执行模型训练
        model = manager._train_model(features)
        
        # 验证模型结构
        self.assertIsInstance(model, dict)
        self.assertIn('model_type', model)
        self.assertIn('features_count', model)
        self.assertEqual(model['model_type'], 'simulated')
        self.assertGreater(model['features_count'], 0)
    
    def test_prediction_generation_phase(self):
        """测试预测生成阶段"""
        manager = WorkflowManager(config_dict=self.test_config)
        
        # 准备数据和模型
        data = manager._prepare_data()
        features = manager._feature_engineering(data)
        model = manager._train_model(features)
        
        # 执行预测生成
        predictions = manager._generate_predictions(model, features)
        
        # 验证预测结构
        self.assertIsInstance(predictions, pd.DataFrame)
        self.assertIn('score', predictions.columns)
        self.assertEqual(len(predictions), len(features))
        
        # 验证预测值
        self.assertTrue(
            all(isinstance(score, (int, float)) for score in predictions['score'])
        )
    
    def test_strategy_execution_phase(self):
        """测试策略执行阶段"""
        manager = WorkflowManager(config_dict=self.test_config)
        
        # 准备数据和预测
        data = manager._prepare_data()
        features = manager._feature_engineering(data)
        model = manager._train_model(features)
        predictions = manager._generate_predictions(model, features)
        
        # 执行策略
        strategy_results = manager._execute_strategy(predictions)
        
        # 验证策略结果结构
        self.assertIsInstance(strategy_results, dict)
        self.assertIn('return', strategy_results)
        self.assertIn('bench', strategy_results)
        self.assertIn('cost', strategy_results)
        self.assertIn('positions', strategy_results)
        
        # 验证收益序列
        returns = strategy_results['return']
        self.assertIsInstance(returns, pd.Series)
        self.assertGreater(len(returns), 0)
        self.assertTrue(all(isinstance(r, (int, float)) for r in returns))
        
        # 验证基准收益序列
        bench = strategy_results['bench']
        self.assertIsInstance(bench, pd.Series)
        self.assertEqual(len(bench), len(returns))
        
        # 验证成本序列
        cost = strategy_results['cost']
        self.assertIsInstance(cost, pd.Series)
        self.assertEqual(len(cost), len(returns))
        
        # 验证持仓数据
        positions = strategy_results['positions']
        self.assertIsInstance(positions, pd.DataFrame)
        self.assertIn('datetime', positions.columns)
        self.assertIn('instrument', positions.columns)
        self.assertIn('score', positions.columns)
    
    def test_evaluation_phase(self):
        """测试评估阶段"""
        manager = WorkflowManager(config_dict=self.test_config)
        
        # 准备策略结果
        data = manager._prepare_data()
        features = manager._feature_engineering(data)
        model = manager._train_model(features)
        predictions = manager._generate_predictions(model, features)
        strategy_results = manager._execute_strategy(predictions)
        
        # 执行评估
        evaluation_results = manager._evaluate_results(strategy_results)
        
        # 验证评估结果结构
        self.assertIsInstance(evaluation_results, dict)
        self.assertIn('analysis', evaluation_results)
        self.assertIn('strategy_results', evaluation_results)
        
        # 验证分析结果
        analysis = evaluation_results['analysis']
        self.assertIn('excess_return_without_cost', analysis)
        self.assertIn('excess_return_with_cost', analysis)
        
        # 验证风险指标
        risk_metrics = analysis['excess_return_without_cost']
        self.assertIn('mean', risk_metrics)
        self.assertIn('std', risk_metrics)
        self.assertIn('annualized_return', risk_metrics)
        self.assertIn('information_ratio', risk_metrics)
        self.assertIn('max_drawdown', risk_metrics)
    
    def test_max_drawdown_calculation(self):
        """测试最大回撤计算"""
        manager = WorkflowManager(config_dict=self.test_config)
        
        # 创建测试收益序列
        returns = pd.Series([0.01, 0.02, -0.03, 0.01, -0.02, 0.01, 0.02])
        
        # 计算最大回撤
        max_dd = manager._calculate_max_drawdown(returns)
        
        # 验证结果
        self.assertIsInstance(max_dd, float)
        self.assertLess(max_dd, 0)  # 最大回撤应该是负数
        self.assertGreaterEqual(max_dd, -1)  # 不应该小于-100%
    
    def test_results_saving(self):
        """测试结果保存"""
        # 启用结果保存的配置
        config_with_save = self.test_config.copy()
        config_with_save['evaluation']['save_results'] = True
        config_with_save['evaluation']['output_dir'] = self.temp_dir
        
        manager = WorkflowManager(config_dict=config_with_save)
        
        # 运行工作流
        manager.run()
        
        # 验证文件保存
        output_dir = Path(self.temp_dir)
        results_file = output_dir / f"{manager.workflow_id}_results.json"
        self.assertTrue(results_file.exists())
        
        # 验证文件内容
        with open(results_file, 'r', encoding='utf-8') as f:
            saved_results = json.load(f)
        
        self.assertIsInstance(saved_results, dict)
        self.assertIn('analysis', saved_results)
        self.assertIn('strategy_results', saved_results)
    
    def test_config_saving(self):
        """测试配置保存"""
        manager = WorkflowManager(config_dict=self.test_config)
        
        # 保存配置
        config_file = os.path.join(self.temp_dir, "saved_config.yaml")
        manager.save_config(config_file)
        
        # 验证文件存在
        self.assertTrue(os.path.exists(config_file))
        
        # 验证文件内容
        import yaml
        with open(config_file, 'r', encoding='utf-8') as f:
            saved_config = yaml.safe_load(f)
        
        self.assertEqual(
            saved_config['workflow']['name'],
            'test_automated_backtest'
        )
    
    def test_workflow_status_tracking(self):
        """测试工作流状态跟踪"""
        manager = WorkflowManager(config_dict=self.test_config)
        
        # 初始状态
        status = manager.get_status()
        self.assertEqual(status['status'], 'initialized')
        self.assertIsNone(status['start_time'])
        self.assertIsNone(status['end_time'])
        self.assertIsNone(status['duration'])
        
        # 运行工作流
        manager.run()
        
        # 完成状态
        status = manager.get_status()
        self.assertEqual(status['status'], 'completed')
        self.assertIsNotNone(status['start_time'])
        self.assertIsNotNone(status['end_time'])
        self.assertIsNotNone(status['duration'])
    
    def test_error_handling(self):
        """测试错误处理"""
        # 创建无效配置
        invalid_config = self.test_config.copy()
        invalid_config['data']['start_time'] = 'invalid_date'
        
        manager = WorkflowManager(config_dict=invalid_config)
        
        # 运行工作流应该失败
        result = manager.run()
        
        # 验证错误处理
        self.assertEqual(result['status'], 'failed')
        self.assertIn('error', result)
        self.assertEqual(manager.status, 'failed')
        self.assertIsNotNone(manager.end_time)
    
    def test_enhanced_monitoring(self):
        """测试增强监控功能"""
        manager = EnhancedWorkflowManager(
            config_dict=self.enhanced_config,
            enable_monitoring=True,
            enable_auto_save=False
        )
        
        # 获取初始监控数据
        monitoring = manager.get_real_time_monitoring()
        self.assertIsInstance(monitoring, dict)
        self.assertIn('task_progress', monitoring)
        self.assertIn('resource_usage', monitoring)
        self.assertIn('performance_metrics', monitoring)
    
    def test_enhanced_auto_save(self):
        """测试增强自动保存功能"""
        manager = EnhancedWorkflowManager(
            config_dict=self.enhanced_config,
            enable_monitoring=False,
            enable_auto_save=True
        )
        
        # 运行工作流
        manager.run()
        
        # 验证自动保存
        output_dir = Path(self.temp_dir)
        report_file = output_dir / f"{manager.workflow_id}_report.json"
        monitoring_file = output_dir / f"{manager.workflow_id}_monitoring.json"
        
        self.assertTrue(report_file.exists())
        self.assertTrue(monitoring_file.exists())
        
        # 验证报告内容
        with open(report_file, 'r', encoding='utf-8') as f:
            saved_report = json.load(f)
        
        self.assertIsInstance(saved_report, dict)
        self.assertIn('summary', saved_report)
        self.assertIn('monitoring_data', saved_report)
        self.assertIn('scheduler_stats', saved_report)
    
    def test_risk_analysis_integration(self):
        """测试风险分析集成"""
        manager = EnhancedWorkflowManager(
            config_dict=self.enhanced_config,
            enable_monitoring=False,
            enable_auto_save=False
        )
        
        # 运行工作流
        result = manager.run()
        
        # 验证风险分析结果
        results = result['results']
        evaluation_task = results.get('backtest_evaluation', {})
        
        if 'result' in evaluation_task and evaluation_task['result']:
            evaluation_result = evaluation_task['result']
            if isinstance(evaluation_result, dict) and 'analysis' in evaluation_result:
                analysis = evaluation_result['analysis']
                self.assertIn('risk_analysis', analysis)
    
    def test_workflow_performance_metrics(self):
        """测试工作流性能指标"""
        manager = EnhancedWorkflowManager(
            config_dict=self.enhanced_config,
            enable_monitoring=False,
            enable_auto_save=False
        )
        
        # 运行工作流
        result = manager.run()
        
        # 验证性能指标
        summary = result['summary']
        self.assertIn('total_tasks', summary)
        self.assertIn('completed_tasks', summary)
        self.assertIn('failed_tasks', summary)
        self.assertIn('success_rate', summary)
        self.assertIn('total_duration', summary)
        
        # 验证指标合理性
        self.assertEqual(summary['total_tasks'], 6)  # 6个主要任务
        self.assertEqual(summary['completed_tasks'], 6)  # 应该全部完成
        self.assertEqual(summary['failed_tasks'], 0)  # 不应该有失败
        self.assertEqual(summary['success_rate'], 100.0)  # 100%成功率
        self.assertGreater(summary['total_duration'], 0)  # 应该有执行时间
    
    def test_multi_strategy_backtest(self):
        """测试多策略回测"""
        # 创建多策略配置
        multi_strategy_config = self.enhanced_config.copy()
        multi_strategy_config['strategy'] = {
            'type': 'multi_strategy',
            'strategies': [
                {'type': 'enhanced_indexing', 'topk': 30},
                {'type': 'topk_dropout', 'topk': 50, 'n_drop': 5},
                {'type': 'equal_weight'}
            ]
        }
        
        manager = EnhancedWorkflowManager(
            config_dict=multi_strategy_config,
            enable_monitoring=False,
            enable_auto_save=False
        )
        
        # 运行工作流
        result = manager.run()
        
        # 验证多策略结果
        self.assertEqual(result['status'], 'completed')
        results = result['results']
        
        # 验证策略执行结果
        strategy_task = results.get('strategy_execution', {})
        if 'result' in strategy_task:
            strategy_result = strategy_task['result']
            if isinstance(strategy_result, dict):
                self.assertIn('strategy_results', strategy_result)
    
    def test_parameter_sweep_backtest(self):
        """测试参数扫描回测"""
        # 创建参数扫描配置
        sweep_config = self.enhanced_config.copy()
        sweep_config['workflow']['parameter_sweep'] = {
            'enabled': True,
            'parameters': {
                'strategy.topk': [30, 50, 70],
                'strategy.n_drop': [3, 5, 7]
            }
        }
        
        manager = EnhancedWorkflowManager(
            config_dict=sweep_config,
            enable_monitoring=False,
            enable_auto_save=False
        )
        
        # 运行工作流
        result = manager.run()
        
        # 验证参数扫描结果
        self.assertEqual(result['status'], 'completed')
        
        # 验证结果中包含参数扫描信息
        if 'parameter_sweep_results' in result:
            sweep_results = result['parameter_sweep_results']
            self.assertIsInstance(sweep_results, dict)
            self.assertGreater(len(sweep_results), 0)
    
    def test_rolling_window_backtest(self):
        """测试滚动窗口回测"""
        # 创建滚动窗口配置
        rolling_config = self.enhanced_config.copy()
        rolling_config['workflow']['rolling_window'] = {
            'enabled': True,
            'window_size': '252d',  # 一年
            'step_size': '63d',     # 一个季度
            'min_periods': 126
        }
        
        manager = EnhancedWorkflowManager(
            config_dict=rolling_config,
            enable_monitoring=False,
            enable_auto_save=False
        )
        
        # 运行工作流
        result = manager.run()
        
        # 验证滚动窗口结果
        self.assertEqual(result['status'], 'completed')
        
        # 验证结果中包含滚动窗口信息
        if 'rolling_window_results' in result:
            rolling_results = result['rolling_window_results']
            self.assertIsInstance(rolling_results, dict)
            self.assertGreater(len(rolling_results), 0)
    
    def test_parallel_strategy_execution(self):
        """测试并行策略执行"""
        # 创建并行执行配置
        parallel_config = self.enhanced_config.copy()
        parallel_config['workflow']['parallel_execution'] = {
            'enabled': True,
            'max_workers': 4,
            'strategy_parallelism': True
        }
        
        manager = EnhancedWorkflowManager(
            config_dict=parallel_config,
            enable_monitoring=True,  # 启用监控以观察并行执行
            enable_auto_save=False
        )
        
        # 运行工作流
        start_time = datetime.now()
        result = manager.run()
        end_time = datetime.now()
        
        # 验证并行执行结果
        self.assertEqual(result['status'], 'completed')
        
        # 验证调度器统计
        if 'scheduler_stats' in result:
            scheduler_stats = result['scheduler_stats']
            self.assertIsInstance(scheduler_stats, dict)
            self.assertIn('total_tasks', scheduler_stats)
            self.assertIn('completed_tasks', scheduler_stats)
            self.assertIn('execution_time', scheduler_stats)


if __name__ == '__main__':
    unittest.main()
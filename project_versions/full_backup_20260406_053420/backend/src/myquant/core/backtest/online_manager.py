# -*- coding: utf-8 -*-
"""
在线训练管理器
================
实现Qlib OnlineManager架构的在线训练调度器

核心功能：
- 每个交易日例行更新（routine）
- 滚动训练新模型
- 自动切换到在线模型
- 生成交易信号

架构层次：
- AI智能策略层：在线滚动训练
- 符合Qlib Online + Trainer模式
"""

from typing import Dict, Any, List, Optional
from loguru import logger
from datetime import datetime
from pathlib import Path

# 导入模块组件
from myquant.core.backtest.rolling_strategy import RollingStrategy
from myquant.core.backtest.data_loader import DataLoader
from myquant.core.backtest.qlib_trainer_adapter import QlibTrainerAdapter


class OnlineManager:
    """在线训练调度器（实现Qlib的OnlineManager逻辑）

    职责：
    1. 管理在线训练流程
    2. 调度滚动训练任务
    3. 切换在线模型
    4. 协调信号生成

    使用示例：
    ```python
    manager = OnlineManager(model_id="my_model")

    # 初始训练
    result = manager.first_train()

    # 每个交易日例行更新
    result = manager.routine(cur_time="2024-01-02")
    ```
    """

    def __init__(
        self,
        model_id: str,
        window_size: int = 252,
        rolling_step: int = 20,
        model_config: Optional[Dict[str, Any]] = None
    ):
        """初始化在线训练管理器

        Args:
            model_id: 模型ID
            window_size: 滚动窗口大小（交易日天数）
            rolling_step: 滚动步长（交易日天数）
            model_config: 模型配置
        """
        self.model_id = model_id
        self.window_size = window_size
        self.rolling_step = rolling_step
        self.model_config = model_config or {}

        self.is_running = False
        self.current_online_model: Optional[Dict[str, Any]] = None

        # 训练进度跟踪
        self.last_routine_time: Optional[str] = None
        self.total_routines = 0
        self.latest_signals: Dict[str, Any] = {}

        # 初始化组件
        self.strategy = RollingStrategy(
            model_id=model_id,
            window_size=window_size,
            rolling_step=rolling_step
        )

        self.data_loader = DataLoader()

        # 导入SignalGenerator（延迟导入避免循环依赖）
        from myquant.core.backtest.signal_generator import SignalGenerator
        self.signal_generator = SignalGenerator(model_id=model_id)

        logger.info(
            f"OnlineManager initialized for model '{model_id}': "
            f"window_size={window_size}, rolling_step={rolling_step}"
        )

    def first_train(self) -> Dict[str, Any]:
        """首次训练，生成初始任务和模型

        这是Qlib OnlineManager工作流程的第一步：
        1. 使用RollingStrategy准备训练任务
        2. 加载训练数据
        3. 使用QlibTrainerAdapter训练模型
        4. 选择在线模型
        5. 生成初始交易信号

        Returns:
            包含tasks、models、online_models、signals的字典

        示例：
        ```python
        manager = OnlineManager(model_id="my_model")
        result = manager.first_train()
        # {
        #     "tasks": [{"task_id": "task_1", ...}],
        #     "models": [{"model_id": "model_v1", ...}],
        #     "online_models": [...],
        #     "signals": {...},
        #     "status": "success"
        # }
        ```
        """
        logger.info(f"Starting first_train for model '{self.model_id}'")

        self.is_running = True

        # 1. 准备训练任务（使用RollingStrategy）
        logger.info("Step 1: Preparing training tasks with RollingStrategy")
        tasks = self.strategy.prepare_tasks()

        if not tasks:
            logger.error(f"Failed to prepare tasks for model '{self.model_id}'")
            return {
                "status": "error",
                "message": "Failed to prepare training tasks"
            }

        task = tasks[0]
        logger.info(
            f"Task prepared: {task['task_id']}, "
            f"train_start={task['train_start']}, train_end={task['train_end']}"
        )

        # 2. 加载训练数据
        logger.info("Step 2: Loading training data")
        try:
            dataset = self.data_loader.load_rolling_data(
                cur_time=task['cur_time'],
                window_size=task['window_size'],
                rolling_step=task['rolling_step']
            )
            logger.info(
                f"Data loaded: {dataset['shape'][0]} rows, "
                f"{dataset['shape'][1]} columns"
            )
        except Exception as e:
            logger.error(f"Failed to load data: {e}")
            return {
                "status": "error",
                "message": f"Failed to load training data: {e}"
            }

        # 3. 训练模型（使用QlibTrainerAdapter）
        logger.info("Step 3: Training model with QlibTrainerAdapter")
        try:
            trainer = QlibTrainerAdapter(
                model_id=self.model_id,
                model_config=self.model_config
            )
            model = trainer.train(dataset)

            # 添加任务信息
            model['task_id'] = task['task_id']

            logger.info(
                f"Model trained successfully: "
                f"model_id={model['model_id']}, "
                f"sharpe_ratio={model['performance']['sharpe_ratio']:.4f}"
            )
        except Exception as e:
            logger.error(f"Failed to train model: {e}")
            return {
                "status": "error",
                "message": f"Failed to train model: {e}"
            }

        models = [model]

        # 4. 选择在线模型
        logger.info("Step 4: Selecting online model")
        online_models = self.prepare_online_models(models)

        if not online_models:
            logger.warning(f"No online models selected for '{self.model_id}'")
        else:
            logger.info(
                f"Online model selected: {online_models[0]['model_id']}"
            )

        # 5. 生成交易信号
        logger.info("Step 5: Generating trading signals")
        signals = self.prepare_signals(online_models)

        # 更新任务状态
        task['status'] = 'completed'
        task['completed_at'] = datetime.now().isoformat()
        task['model_id'] = model['model_id']

        result = {
            "tasks": tasks,
            "models": models,
            "online_models": online_models,
            "current_online_model": self.current_online_model,
            "signals": signals,
            "status": "success",
            "timestamp": datetime.now().isoformat()
        }

        logger.info(
            f"first_train completed for model '{self.model_id}': "
            f"{len(tasks)} tasks, {len(models)} models, "
            f"{len(online_models)} online, "
            f"{len(signals['buy'])} buy signals, {len(signals['sell'])} sell signals"
        )

        return result

    def routine(self, cur_time: Optional[str] = None) -> Dict[str, Any]:
        """每个交易日的例行更新（Qlib OnlineManager核心方法）

        这是Qlib Online + Trainer模式的核心工作流程：
        1. prepare_tasks() - 准备训练任务
        2. train_models() - 训练新模型
        3. prepare_online_models() - 切换到在线模型
        4. prepare_signals() - 准备交易信号

        Args:
            cur_time: 当前时间（None则使用最新）

        Returns:
            routine结果字典，包含任务、模型、信号等信息

        示例：
        ```python
        manager = OnlineManager(model_id="my_model")
        result = manager.routine(cur_time="2024-01-02")
        # {
        #     "tasks_prepared": 1,
        #     "models_trained": 1,
        #     "online_models": 1,
        #     "signals": {...}
        # }
        ```
        """
        if not self.is_running:
            logger.warning(f"OnlineManager not running for model '{self.model_id}', call first_train() first")
            return {
                "status": "error",
                "message": "OnlineManager not running. Call first_train() first."
            }

        logger.info(f"Starting routine for model '{self.model_id}' at {cur_time or 'latest'}")

        # 1. 准备训练任务
        tasks = self.prepare_tasks(cur_time)

        # 2. 训练新模型
        models = self.train_models(tasks)

        # 3. 切换到在线模型
        online_models = self.prepare_online_models(models)

        # 4. 准备交易信号
        signals = self.prepare_signals(online_models)

        # 5. 更新进度跟踪
        self.last_routine_time = datetime.now().isoformat()
        self.total_routines += 1

        result = {
            "tasks_prepared": len(tasks),
            "models_trained": len(models),
            "online_models": len(online_models),
            "current_online_model": self.current_online_model,
            "signals": signals,
            "status": "success",
            "timestamp": datetime.now().isoformat()
        }

        logger.info(
            f"Routine completed for model '{self.model_id}': "
            f"{len(tasks)} tasks, {len(models)} models, {len(online_models)} online"
        )

        return result

    def prepare_tasks(self, cur_time: Optional[str] = None) -> List[Dict[str, Any]]:
        """准备新的训练任务（使用RollingStrategy）

        Args:
            cur_time: 当前时间

        Returns:
            任务列表
        """
        logger.debug(f"Preparing tasks for model '{self.model_id}' at {cur_time or 'latest'}")

        # 使用RollingStrategy准备任务
        tasks = self.strategy.prepare_tasks(cur_time)

        logger.debug(f"Prepared {len(tasks)} task(s)")

        return tasks

    def train_models(self, tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """训练模型

        Args:
            tasks: 训练任务列表

        Returns:
            训练完成的模型列表
        """
        if not tasks:
            logger.warning("No tasks provided for training")
            return []

        trained_models = []

        for task in tasks:
            try:
                logger.info(f"Training model for task '{task['task_id']}'")

                # 1. 加载数据
                dataset = self.data_loader.load_rolling_data(
                    cur_time=task.get('cur_time', datetime.now().isoformat()),
                    window_size=task.get('window_size', self.window_size),
                    rolling_step=task.get('rolling_step', self.rolling_step)
                )

                logger.info(
                    f"Data loaded for task '{task['task_id']}': "
                    f"{dataset['shape'][0]} rows"
                )

                # 2. 训练模型
                trainer = QlibTrainerAdapter(
                    model_id=self.model_id,
                    model_config=self.model_config
                )

                model = trainer.train(dataset)

                # 3. 添加任务信息
                model['task_id'] = task['task_id']
                model['task_config'] = {
                    'train_start': task.get('train_start'),
                    'train_end': task.get('train_end'),
                    'window_size': task.get('window_size'),
                    'rolling_step': task.get('rolling_step')
                }

                trained_models.append(model)

                logger.info(
                    f"Model trained for task '{task['task_id']}': "
                    f"sharpe_ratio={model['performance']['sharpe_ratio']:.4f}"
                )

            except Exception as e:
                logger.error(f"Training failed for task '{task['task_id']}': {e}")
                # 继续处理下一个任务
                continue

        logger.info(f"Training completed: {len(trained_models)}/{len(tasks)} models trained")

        return trained_models

    def prepare_online_models(self, trained_models: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """选择并切换到在线模型

        当前实现：选择第一个模型（简化实现）
        优化方向：可以基于性能指标选择最佳模型

        Args:
            trained_models: 训练完成的模型列表

        Returns:
            在线模型列表
        """
        if not trained_models:
            return []

        # 当前实现：选择第一个模型作为在线模型
        # 未来可以基于sharpe_ratio等性能指标选择最佳模型
        self.current_online_model = trained_models[0]["model_id"]
        return trained_models

    def prepare_signals(self, online_models: List[Dict[str, Any]]) -> Dict[str, Any]:
        """准备交易信号（使用SignalGenerator）

        Args:
            online_models: 在线模型列表

        Returns:
            信号字典，包含买入/卖出信号、时间戳、置信度等
        """
        # 使用SignalGenerator生成交易信号
        signals = self.signal_generator.generate_signals(online_models)

        # 保存最新信号供get_progress()使用
        self.latest_signals = signals

        logger.info(
            f"Signals prepared for model '{self.model_id}': "
            f"{len(signals['buy'])} buy, {len(signals['sell'])} sell"
        )

        return signals

    def get_progress(self) -> Dict[str, Any]:
        """获取当前训练进度

        Returns:
            包含训练进度信息的字典

        示例：
        ```python
        manager = OnlineManager(model_id="my_model")
        manager.first_train()
        progress = manager.get_progress()
        # {
        #     "model_id": "my_model",
        #     "is_running": True,
        #     "current_online_model": "my_model_v1",
        #     "total_routines": 0,
        #     "signals": {...}
        # }
        ```
        """
        return {
            "model_id": self.model_id,
            "is_running": self.is_running,
            "current_online_model": self.current_online_model,
            "last_routine_time": self.last_routine_time,
            "total_routines": self.total_routines,
            "latest_signals": self.latest_signals
        }

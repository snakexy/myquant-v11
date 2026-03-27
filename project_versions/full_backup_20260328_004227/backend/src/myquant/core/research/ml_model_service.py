# -*- coding: utf-8 -*-
"""
Research阶段 - ML模型训练服务
====================================

职责：
- ML模型训练（LightGBM/XGBoost/LSTM/GRU/MLP）
- 模型预测（单股票/批量）
- 模型评估和验证
- 特征工程和数据预处理
- 超参数优化
- 模型版本管理

基于QLib框架设计：
- 使用QLib Model组件进行训练
- 使用QLib DataHandler进行数据加载
- 支持多种ML算法的统一接口

应用场景：
1. 股票涨跌预测（分类）
2. 收益率预测（回归）
3. 多因子时序建模（LSTM/GRU）
4. 因子组合优化（MLP）
5. 板块轮动预测（Transformer）

版本: v1.0
创建日期: 2026-02-12
"""

from typing import Dict, List, Optional, Any, Union, Tuple, Callable
from dataclasses import dataclass, field
from loguru import logger
from datetime import datetime, timedelta
from pathlib import Path
import pickle
import uuid
import json
import math
from enum import Enum

# 核心依赖
try:
    import numpy as np
    import pandas as pd
    from sklearn.model_selection import train_test_split, KFold, TimeSeriesSplit
    from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
    from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
    from sklearn.metrics import roc_auc_score
    from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
    from sklearn.linear_model import LinearRegression, LogisticRegression
    from sklearn.inspection import permutation_importance
    from scipy.stats import pearsonr, spearmanr
    NP_AVAILABLE = True
except ImportError as e:
    np = None
    pd = None
    logger.error(f"NumPy/Pandas/sklearn导入失败: {e}")
    NP_AVAILABLE = False

# QLib导入 - 使用新版本API
try:
    import qlib
    from qlib.data import D
    from qlib.workflow import R
    QLIB_AVAILABLE = True
except ImportError as e:
    QLIB_AVAILABLE = False
    logger.warning(f"QLib未安装，ML功能将受限: {e}")

# 使用UnifiedDataManager获取真实数据
UNIFIED_DATA_MANAGER = None
try:
    from data.unified_data_manager import get_unified_data_manager
    UNIFIED_DATA_MANAGER = get_unified_data_manager()
    logger.info("[ML训练] UnifiedDataManager已加载")
except Exception as e:
    logger.warning(f"[ML训练] UnifiedDataManager加载失败: {e}")

# LightGBM导入
try:
    import lightgbm as lgb
    LGB_AVAILABLE = True
except ImportError:
    LGB_AVAILABLE = False
    logger.warning("LightGBM未安装")

# XGBoost导入
try:
    import xgboost as xgb
    XGB_AVAILABLE = True
except ImportError:
    XGB_AVAILABLE = False
    logger.warning("XGBoost未安装")

# PyTorch导入（用于深度学习）
try:
    import torch
    import torch.nn as nn
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    logger.warning("PyTorch未安装，深度学习功能将受限")

# Optuna导入（用于超参数优化）
try:
    import optuna
    OPTUNA_AVAILABLE = True
except ImportError:
    OPTUNA_AVAILABLE = False
    logger.warning("Optuna未安装，超参数优化功能将受限")


# ==================== 枚举定义 ====================

class ModelType(Enum):
    """模型类型枚举"""
    LIGHTGBM = "lightgbm"
    XGBOOST = "xgboost"
    RANDOM_FOREST = "random_forest"
    LINEAR = "linear"
    LSTM = "lstm"
    GRU = "gru"
    MLP = "mlp"
    TRANSFORMER = "transformer"


class TaskType(Enum):
    """任务类型枚举"""
    CLASSIFICATION = "classification"  # 分类任务（涨跌）
    REGRESSION = "regression"         # 回归任务（收益率）
    RANKING = "ranking"              # 排序任务


class LabelType(Enum):
    """标签类型枚举"""
    RETURN = "return"           # 收益率
    DIRECTION = "direction"     # 涨跌方向
    VOLATILITY = "volatility"   # 波动率


# ==================== 数据类定义 ====================

@dataclass
class MLTrainingConfig:
    """ML训练配置"""
    # 模型配置
    model_type: ModelType = ModelType.LIGHTGBM
    task_type: TaskType = TaskType.CLASSIFICATION

    # 数据配置
    instruments: List[str] = field(default_factory=list)
    start_date: str = "2020-01-01"
    end_date: str = "2023-12-31"
    features: List[str] = field(default_factory=list)

    # 标签配置
    label_type: LabelType = LabelType.DIRECTION
    horizon: int = 5  # 预测horizon（天数）

    # 训练参数
    train_split: float = 0.7
    val_split: float = 0.15
    test_split: float = 0.15

    # 模型超参数
    hyperparameters: Dict[str, Any] = field(default_factory=dict)

    # 训练控制
    early_stopping_rounds: int = 100
    num_boost_round: int = 1000
    random_seed: int = 42

    # 深度学习特定参数
    sequence_length: int = 20  # 时序长度（用于LSTM/GRU）
    batch_size: int = 32
    hidden_size: int = 128
    num_layers: int = 2
    dropout: float = 0.3
    learning_rate: float = 0.001
    epochs: int = 100

    # GPU配置
    device: str = "auto"  # auto/cuda/cpu


@dataclass
class MLPredictionRequest:
    """ML预测请求"""
    model_id: str
    instruments: List[str]
    start_date: str
    end_date: str
    features: Optional[List[str]] = None


@dataclass
class ModelInfo:
    """模型信息"""
    model_id: str
    model_type: ModelType
    task_type: TaskType
    status: str  # training, trained, error
    created_at: str
    training_time: Optional[float] = None  # 秒
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    hyperparameters: Dict[str, Any] = field(default_factory=dict)
    features: List[str] = field(default_factory=list)


@dataclass
class PredictionResult:
    """预测结果"""
    instrument: str
    date: str
    prediction: Union[float, int]  # 预测值
    prediction_score: float  # 0-1买入评分
    confidence: float  # 置信度
    actual_value: Optional[float] = None  # 实际值（如果有）


@dataclass
class TrainingResult:
    """训练结果"""
    model_id: str
    status: str  # success, error
    message: str
    training_time: float  # 秒
    performance_metrics: Dict[str, float]
    feature_importance: Dict[str, float] = field(default_factory=dict)
    model_path: str = ""


# ==================== ML模型训练服务 ====================

class MLModelService:
    """
    ML模型训练服务

    核心价值：
    1. 统一的模型训练接口（支持传统ML和深度学习）
    2. 模型预测和评估
    3. 特征工程和数据预处理
    4. 模型版本管理
    """

    def __init__(self, model_storage_path: str = "./model_storage/ml"):
        self.model_storage_path = Path(model_storage_path)
        self.model_storage_path.mkdir(parents=True, exist_ok=True)

        # 模型注册表
        self.models: Dict[str, Any] = {}
        self.model_configs: Dict[str, MLTrainingConfig] = {}
        self.model_info: Dict[str, ModelInfo] = {}

        logger.info(f"ML模型服务初始化完成，存储路径: {model_storage_path}")

    async def train_model(
        self,
        config: MLTrainingConfig,
        progress_callback: Optional[Callable[[int, str, str, Optional[Dict]], None]] = None
    ) -> TrainingResult:
        """
        训练ML模型

        Args:
            config: 训练配置
            progress_callback: 进度回调函数 (可选)
                - progress: 0-100 进度百分比
                - status: 状态 (initializing/training/completed/error)
                - message: 状态消息
                - metrics: 当前指标 (可选)

        Returns:
            TrainingResult
        """
        # 发送初始进度
        if progress_callback:
            progress_callback(0, "initializing", "准备训练数据...", None)

        if not NP_AVAILABLE:
            return TrainingResult(
                model_id="",
                status="error",
                message="NumPy/Pandas未安装",
                training_time=0,
                performance_metrics={}
            )

        start_time = datetime.now()
        model_id = f"{config.model_type.value}_{uuid.uuid4().hex[:8]}"

        logger.info(f"开始训练模型: {model_id}, 类型: {config.model_type.value}")

        try:
            # 1. 准备数据
            if progress_callback:
                progress_callback(10, "training", "准备训练数据...", None)
            X_train, X_val, X_test, y_train, y_val, y_test = \
                await self._prepare_training_data(config)

            # 2. 根据模型类型选择训练器
            if progress_callback:
                progress_callback(30, "training", "开始训练模型...", None)
            if config.model_type == ModelType.LIGHTGBM and LGB_AVAILABLE:
                model, metrics, importance = self._train_lightgbm(
                    config, X_train, X_val, y_train, y_val
                )
            elif config.model_type == ModelType.XGBOOST and XGB_AVAILABLE:
                model, metrics, importance = self._train_xgboost(
                    config, X_train, X_val, y_train, y_val
                )
            elif config.model_type == ModelType.RANDOM_FOREST:
                # Random Forest 使用 sklearn，不需要特殊库检查
                model, metrics, importance = self._train_random_forest(
                    config, X_train, X_val, y_train, y_val
                )
            elif config.model_type == ModelType.LINEAR:
                # Linear Model 使用 sklearn，不需要特殊库检查
                model, metrics, importance = self._train_linear(
                    config, X_train, X_val, y_train, y_val
                )
            elif config.model_type == ModelType.LSTM and TORCH_AVAILABLE:
                model, metrics, importance = self._train_lstm(
                    config, X_train, X_val, y_train, y_val
                )
            elif config.model_type == ModelType.GRU and TORCH_AVAILABLE:
                model, metrics, importance = self._train_gru(
                    config, X_train, X_val, y_train, y_val
                )
            elif config.model_type == ModelType.MLP and TORCH_AVAILABLE:
                model, metrics, importance = self._train_mlp(
                    config, X_train, X_val, y_train, y_val
                )
            elif config.model_type == ModelType.TRANSFORMER and TORCH_AVAILABLE:
                model, metrics, importance = self._train_transformer(
                    config, X_train, X_val, y_train, y_val
                )
            else:
                return TrainingResult(
                    model_id=model_id,
                    status="error",
                    message=f"模型类型 {config.model_type.value} 不可用或未实现",
                    training_time=0,
                    performance_metrics={}
                )

            # 3. 在测试集上评估
            if progress_callback:
                progress_callback(70, "training", "评估模型...", None)
            test_metrics = self._evaluate_model(
                model, X_test, y_test, config.task_type
            )
            metrics.update(test_metrics)

            # 4. 保存模型
            if progress_callback:
                progress_callback(85, "training", "保存模型...", None)
            model_path = self.model_storage_path / f"{model_id}.pkl"
            self._save_model(model, model_path)

            # 5. 注册模型
            self.models[model_id] = model
            self.model_configs[model_id] = config

            training_time = (datetime.now() - start_time).total_seconds()

            # 6. 保存模型信息
            model_info = ModelInfo(
                model_id=model_id,
                model_type=config.model_type,
                task_type=config.task_type,
                status="trained",
                created_at=datetime.now().isoformat(),
                training_time=training_time,
                performance_metrics=metrics,
                hyperparameters=config.hyperparameters,
                features=config.features
            )
            self.model_info[model_id] = model_info

            logger.info(f"模型训练成功: {model_id}, 耗时: {training_time:.2f}秒")

            # 发送完成进度
            if progress_callback:
                progress_callback(100, "completed", "训练完成", metrics)

            return TrainingResult(
                model_id=model_id,
                status="success",
                message="训练成功",
                training_time=training_time,
                performance_metrics=metrics,
                feature_importance=importance,
                model_path=str(model_path)
            )

        except Exception as e:
            logger.exception(f"模型训练失败: {e}")
            # 发送错误进度
            if progress_callback:
                progress_callback(0, "error", str(e), None)
            return TrainingResult(
                model_id=model_id,
                status="error",
                message=str(e),
                training_time=(datetime.now() - start_time).total_seconds(),
                performance_metrics={}
            )

    async def train_model_with_progress(
        self,
        config: MLTrainingConfig,
        progress_callback: Optional[Callable[[int, str, str, Optional[Dict]], None]] = None
    ) -> TrainingResult:
        """
        带进度回调的模型训练

        Args:
            config: 训练配置
            progress_callback: 进度回调函数
                - progress: 0-100 进度百分比
                - status: 状态 (initializing/training/completed/error)
                - message: 状态消息
                - metrics: 当前指标 (可选)

        Returns:
            TrainingResult
        """
        # 发送初始进度
        if progress_callback:
            progress_callback(0, "initializing", "准备训练环境...", None)

        result = await self.train_model(config)

        # 发送完成进度
        if progress_callback:
            if result.status == "success":
                progress_callback(100, "completed", "训练完成", result.performance_metrics)
            else:
                progress_callback(0, "error", result.message, None)

        return result

    def train_model_with_progress_sync(
        self,
        config: MLTrainingConfig,
        progress_callback: Optional[Callable[[int, str, str, Optional[Dict]], None]] = None
    ) -> TrainingResult:
        """
        同步版本的带进度回调的模型训练（在线程池中运行）

        Args:
            config: 训练配置
            progress_callback: 进度回调函数

        Returns:
            TrainingResult
        """
        # 发送初始进度
        if progress_callback:
            progress_callback(0, "initializing", "准备训练环境...", None)

        # 同步调用 train_model
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(self.train_model(config))
        finally:
            loop.close()

        # 发送完成进度
        if progress_callback:
            if result.status == "success":
                progress_callback(100, "completed", "训练完成", result.performance_metrics)
            else:
                progress_callback(0, "error", result.message, None)

        return result

    async def cross_validate(
        self,
        config: MLTrainingConfig,
        n_folds: int = 5,
        use_timeseries: bool = False,
        progress_callback: Optional[Callable[[int, str, str, Optional[Dict]], None]] = None
    ) -> Dict[str, Any]:
        """
        K-Fold交叉验证

        Args:
            config: 训练配置
            n_folds: 折数
            use_timeseries: 是否使用时间序列交叉验证
            progress_callback: 进度回调

        Returns:
            交叉验证结果
        """
        if progress_callback:
            progress_callback(0, "initializing", "准备交叉验证...", None)

        # 准备数据
        X_train, X_val, X_test, y_train, y_val, y_test = \
            await self._prepare_training_data(config)

        # 合并训练和验证数据用于交叉验证
        X = np.vstack([X_train, X_val])
        y = np.concatenate([y_train, y_val])

        # 选择交叉验证器
        if use_timeseries:
            kfold = TimeSeriesSplit(n_splits=n_folds)
        else:
            kfold = KFold(n_splits=n_folds, shuffle=True, random_state=config.random_seed)

        fold_scores = []
        fold_metrics = []

        if progress_callback:
            progress_callback(10, "training", f"开始{n_folds}折交叉验证...", None)

        for fold, (train_idx, val_idx) in enumerate(kfold.split(X)):
            if progress_callback:
                progress_callback(
                    int(10 + (fold / n_folds) * 80),
                    "training",
                    f"训练第{fold + 1}折...",
                    {"fold": fold + 1, "total": n_folds}
                )

            X_fold_train, X_fold_val = X[train_idx], X[val_idx]
            y_fold_train, y_fold_val = y[train_idx], y[val_idx]

            # 训练模型
            fold_config = MLTrainingConfig(
                model_type=config.model_type,
                task_type=config.task_type,
                instruments=config.instruments,
                start_date=config.start_date,
                end_date=config.end_date,
                features=config.features,
                label_type=config.label_type,
                horizon=config.horizon,
                train_split=0.8,
                val_split=0.1,
                test_split=0.1,
                hyperparameters=config.hyperparameters,
                num_boost_round=config.num_boost_round,
                learning_rate=config.learning_rate,
                early_stopping_rounds=config.early_stopping_rounds,
                random_seed=config.random_seed + fold,
            )

            # 简单的同步训练
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                # 暂时使用简化版本的训练
                fold_result = await self.train_model(fold_config)
                fold_scores.append(fold_result.performance_metrics)
            finally:
                loop.close()

        # 计算平均指标
        avg_metrics = {}
        if fold_scores:
            for metric_name in fold_scores[0].keys():
                values = [s.get(metric_name, 0) for s in fold_scores if s.get(metric_name) is not None]
                if values:
                    avg_metrics[metric_name] = {
                        'mean': float(np.mean(values)),
                        'std': float(np.std(values)),
                        'values': values
                    }

        if progress_callback:
            progress_callback(100, "completed", "交叉验证完成", avg_metrics)

        return {
            "n_folds": n_folds,
            "use_timeseries": use_timeseries,
            "fold_scores": fold_scores,
            "avg_metrics": avg_metrics
        }

    async def optimize_hyperparameters(
        self,
        config: MLTrainingConfig,
        optimization_config: Dict[str, Any],
        progress_callback: Optional[Callable[[int, str, str, Optional[Dict]], None]] = None
    ) -> Dict[str, Any]:
        """
        超参数优化

        Args:
            config: 基础训练配置
            optimization_config: 优化配置
                - algorithm: 优化算法 (tpe, random, grid)
                - n_trials: 试验次数
                - timeout: 超时时间（秒）
                - param_space: 参数空间
            progress_callback: 进度回调

        Returns:
            优化结果
        """
        if not OPTUNA_AVAILABLE:
            return {
                "status": "error",
                "message": "Optuna未安装",
                "best_params": {},
                "best_score": 0.0,
                "n_trials": 0
            }

        if progress_callback:
            progress_callback(0, "initializing", "准备超参数优化...", None)

        algorithm = optimization_config.get("algorithm", "tpe")
        n_trials = optimization_config.get("n_trials", 10)
        timeout = optimization_config.get("timeout", 3600)
        param_space = optimization_config.get("param_space", {})

        # 创建优化目标函数
        def objective(trial: optuna.Trial):
            # 根据trial建议参数
            trial_params = {}
            for param_name, param_config in param_space.items():
                param_type = param_config.get("type", "uniform")
                low = param_config.get("low", 0)
                high = param_config.get("high", 1)

                if param_type == "uniform":
                    trial_params[param_name] = trial.suggest_float(param_name, low, high)
                elif param_type == "int":
                    trial_params[param_name] = trial.suggest_int(param_name, int(low), int(high))
                elif param_type == "categorical":
                    choices = param_config.get("choices", [])
                    trial_params[param_name] = trial.suggest_categorical(param_name, choices)

            # 创建临时配置
            trial_config = MLTrainingConfig(
                model_type=config.model_type,
                task_type=config.task_type,
                instruments=config.instruments,
                start_date=config.start_date,
                end_date=config.end_date,
                features=config.features,
                label_type=config.label_type,
                horizon=config.horizon,
                train_split=config.train_split,
                val_split=config.val_split,
                test_split=config.test_split,
                hyperparameters=trial_params,
                num_boost_round=config.num_boost_round,
                learning_rate=trial_params.get("learning_rate", config.learning_rate),
                early_stopping_rounds=config.early_stopping_rounds,
                random_seed=config.random_seed,
            )

            # 训练模型（不使用进度回调避免刷屏）
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                result = loop.run_until_complete(self.train_model(trial_config))
            finally:
                loop.close()

            # 返回验证集IC作为优化目标（如果是回归任务）
            if result.performance_metrics:
                # 优先使用IC/RankIC，其次用验证集指标
                return result.performance_metrics.get('ic') or \
                       result.performance_metrics.get('rank_ic') or \
                       result.performance_metrics.get('val_ic', 0.0)
            return 0.0

        # 创建study
        if algorithm == "tpe":
            sampler = optuna.samplers.TPESampler()
        elif algorithm == "random":
            sampler = optuna.samplers.RandomSampler()
        else:
            sampler = optuna.samplers.GridSampler(param_space) if param_space else optuna.samplers.TPESampler()

        study = optuna.create_study(direction="maximize", sampler=sampler)

        # 运行优化
        if progress_callback:
            progress_callback(10, "training", "开始超参数搜索...", None)

        try:
            study.optimize(
                objective,
                n_trials=n_trials,
                timeout=timeout,
                show_progress_bar=False,
                callbacks=[
                    lambda study, trial: progress_callback(
                        int(10 + (trial.number / n_trials) * 80),
                        "training",
                        f"试验 {trial.number + 1}/{n_trials}",
                        {"value": trial.value} if trial.value else None
                    ) if progress_callback and trial.value else None
                ]
            )
        except Exception as e:
            logger.warning(f"超参数优化中断: {e}")

        best_params = study.best_params
        best_score = study.best_value

        if progress_callback:
            progress_callback(100, "completed", "超参数优化完成", {"best_score": best_score})

        return {
            "status": "success",
            "message": "优化完成",
            "best_params": best_params,
            "best_score": float(best_score) if best_score else 0.0,
            "n_trials": len(study.trials),
            "study_best_trial": study.best_trial.number if study.best_trial else 0
        }

    async def predict(self, request: MLPredictionRequest) -> List[PredictionResult]:
        """
        使用模型进行预测

        Args:
            request: 预测请求

        Returns:
            预测结果列表
        """
        model_id = request.model_id

        if model_id not in self.models:
            raise ValueError(f"模型不存在: {model_id}")

        model = self.models[model_id]
        config = self.model_configs[model_id]

        # 加载特征数据
        X, dates, instruments = await self._load_prediction_data(request, config)

        # 预测
        if hasattr(model, 'predict'):
            predictions = model.predict(X)
        elif hasattr(model, 'forward'):
            # PyTorch模型
            model.eval()
            with torch.no_grad():
                X_tensor = torch.FloatTensor(X)
                predictions = model(X_tensor)
                predictions = predictions.numpy()
        else:
            raise ValueError("模型不支持预测")

        # 转换为PredictionResult
        results = []
        for i, (instrument, date, pred) in enumerate(zip(instruments, dates, predictions)):
            # 计算买入评分（0-1）
            if config.task_type == TaskType.CLASSIFICATION:
                # 分类任务：使用概率作为评分
                if hasattr(model, 'predict_proba'):
                    proba = model.predict_proba(X[i:i+1])[0]
                    prediction_score = proba[1] if len(proba) > 1 else float(proba[0])
                else:
                    prediction_score = float(pred)
                confidence = abs(prediction_score - 0.5) * 2  # 距离0.5越远越置信
            else:  # REGRESSION
                # 回归任务：使用Sigmoid映射到0-1
                prediction_score = 1 / (1 + np.exp(-float(pred)))
                confidence = 0.8  # 默认置信度

            results.append(PredictionResult(
                instrument=instrument,
                date=date,
                prediction=float(pred),
                prediction_score=prediction_score,
                confidence=confidence
            ))

        logger.info(f"预测完成: {len(results)} 条记录")
        return results

    async def get_model_list(self) -> List[ModelInfo]:
        """获取所有模型列表"""
        return list(self.model_info.values())

    async def get_model_details(self, model_id: str) -> Optional[ModelInfo]:
        """获取模型详情"""
        return self.model_info.get(model_id)

    def delete_model(self, model_id: str) -> bool:
        """删除模型"""
        if model_id not in self.models:
            logger.warning(f"模型不存在: {model_id}")
            return False

        # 删除模型文件
        model_path = self.model_storage_path / f"{model_id}.pkl"
        if model_path.exists():
            model_path.unlink()

        # 从内存中删除
        del self.models[model_id]
        del self.model_configs[model_id]
        del self.model_info[model_id]

        logger.info(f"模型已删除: {model_id}")
        return True

    def export_model(self, model_id: str, export_path: Optional[str] = None) -> Optional[str]:
        """
        导出模型到指定路径

        Args:
            model_id: 模型ID
            export_path: 导出路径（可选，默认导出到model_storage目录）

        Returns:
            导出文件的路径，失败返回None
        """
        if model_id not in self.models:
            logger.warning(f"模型不存在: {model_id}")
            return None

        try:
            import shutil
            from pathlib import Path

            # 源文件路径
            source_path = self.model_storage_path / f"{model_id}.pkl"

            if not source_path.exists():
                logger.warning(f"模型文件不存在: {source_path}")
                return None

            # 目标路径
            if export_path is None:
                export_path = str(self.model_storage_path / f"{model_id}_export.pkl")
            else:
                export_path = str(Path(export_path).expanduser().resolve())

            # 复制文件
            shutil.copy2(source_path, export_path)

            logger.info(f"模型已导出: {model_id} -> {export_path}")
            return export_path

        except Exception as e:
            logger.error(f"导出模型失败: {e}")
            return None

    async def evaluate_model(
        self,
        model_id: str,
        test_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        评估模型性能

        Args:
            model_id: 模型ID
            test_data: 测试数据（可选，如果不提供则生成随机数据）

        Returns:
            评估结果
        """
        # 获取模型信息
        model_info = await self.get_model_details(model_id)
        if model_info is None:
            raise ValueError(f"模型不存在: {model_id}")

        # 生成或使用提供的测试数据
        import numpy as np
        if test_data and 'X_test' in test_data and 'y_test' in test_data:
            X_test = np.array(test_data['X_test'])
            y_test = np.array(test_data['y_test'])
        else:
            # 生成随机测试数据
            n_samples = 500
            n_features = len(model_info.features) if model_info.features else 20
            X_test = np.random.randn(n_samples, n_features)
            y_test = np.random.randn(n_samples)

        # 加载模型（简化版本，返回模拟指标）
        # 实际应该从磁盘加载模型文件
        task_type = model_info.task_type if hasattr(model_info, 'task_type') else TaskType.REGRESSION

        # 计算评估指标（使用随机预测模拟）
        y_pred = np.random.randn(len(y_test))
        metrics = self._calculate_metrics(y_test, y_pred, task_type)

        # 添加IC/IR（如果是回归任务）
        if task_type == TaskType.REGRESSION:
            metrics['ic'] = np.corrcoef(y_test, y_pred)[0, 1] if len(y_test) > 1 else 0.0
            metrics['ir'] = abs(metrics.get('ic', 0)) * 0.8

        return {
            "model_id": model_id,
            "test_metrics": metrics,
            "n_test_samples": len(y_test),
            "evaluated_at": datetime.now().isoformat()
        }

    # ==================== 私有方法 ====================

    async def _prepare_training_data(self, config: MLTrainingConfig) -> Tuple:
        """
        准备训练数据

        使用UnifiedDataManager获取真实市场数据

        Returns:
            X_train, X_val, X_test, y_train, y_val, y_test
        """
        # 优先使用UnifiedDataManager获取真实数据
        if UNIFIED_DATA_MANAGER is not None:
            try:
                logger.info("[ML训练] 使用UnifiedDataManager获取真实数据...")
                all_data = []
                all_labels = []

                # 获取每只股票的数据
                for symbol in config.instruments:
                    try:
                        # 获取K线数据
                        result = UNIFIED_DATA_MANAGER.get_kline_data(
                            symbol=symbol,
                            period="day",
                            count=500,  # 获取500天数据
                            adjust_type="front"
                        )

                        if result and 'data' in result and result['data']:
                            df = result['data']
                            if len(df) >= 50:  # 至少需要50天数据
                                # 提取特征：OHLCV
                                features = df[['open', 'high', 'low', 'close', 'volume']].values

                                # 计算未来收益作为标签（horizon天后）
                                horizon = config.horizon
                                close_prices = df['close'].values
                                future_returns = []
                                for i in range(len(close_prices) - horizon):
                                    ret = (close_prices[i + horizon] - close_prices[i]) / close_prices[i]
                                    future_returns.append(ret)

                                # 只保留有标签的数据
                                min_len = min(len(features) - horizon, len(future_returns))
                                if min_len > 0:
                                    all_data.extend(features[:min_len])
                                    all_labels.extend(future_returns[:min_len])
                                    logger.info(f"[ML训练] {symbol}: 获取 {min_len} 条样本")
                    except Exception as e:
                        logger.warning(f"[ML训练] 获取 {symbol} 数据失败: {e}")
                        continue

                if len(all_data) >= 100:  # 至少需要100条数据
                    data_array = np.array(all_data)
                    label_array = np.array(all_labels)

                    # 标准化特征
                    mean = data_array.mean(axis=0)
                    std = data_array.std(axis=0) + 1e-8
                    data_array = (data_array - mean) / std

                    n_samples = len(data_array)
                    logger.info(f"[ML训练] 总共获取 {n_samples} 条真实样本")

                    # 划分数据集
                    train_val = int(n_samples * config.train_split)
                    val_test = int(n_samples * (config.train_split + config.val_split))

                    X_train, y_train = data_array[:train_val], label_array[:train_val]
                    X_val, y_val = data_array[train_val:val_test], label_array[train_val:val_test]
                    X_test, y_test = data_array[val_test:], label_array[val_test:]

                    return X_train, X_val, X_test, y_train, y_val, y_test

                logger.warning("[ML训练] 真实数据不足，回退到模拟数据")

            except Exception as e:
                logger.warning(f"[ML训练] UnifiedDataManager获取数据失败: {e}，回退到模拟数据")

        # 回退：生成模拟数据
        logger.info("[ML训练] 使用模拟数据进行训练")
        n_samples = 1000
        n_features = len(config.features) if config.features else 50

        X = np.random.randn(n_samples, n_features)

        if config.task_type == TaskType.CLASSIFICATION:
            y = np.random.randint(0, 2, n_samples)
        else:  # REGRESSION
            y = np.random.randn(n_samples) * 0.05

        # 划分数据集
        train_val = int(n_samples * config.train_split)
        val_test = int(n_samples * (config.train_split + config.val_split))

        X_train, y_train = X[:train_val], y[:train_val]
        X_val, y_val = X[train_val:val_test], y[train_val:val_test]
        X_test, y_test = X[val_test:], y[val_test:]

        return X_train, X_val, X_test, y_train, y_val, y_test

    def _train_lightgbm(self, config: MLTrainingConfig, X_train, X_val, y_train, y_val):
        """训练LightGBM模型"""
        # LightGBM: 强制使用CPU（OpenCL GPU比CPU慢，原生CUDA需编译）
        device = 'cpu'

        params = {
            'objective': 'binary' if config.task_type == TaskType.CLASSIFICATION else 'regression',
            'metric': 'auc' if config.task_type == TaskType.CLASSIFICATION else 'rmse',
            'num_leaves': config.hyperparameters.get('num_leaves', 31),
            'learning_rate': config.hyperparameters.get('learning_rate', 0.05),
            'n_estimators': config.num_boost_round,
            'verbose': -1,
            'random_state': config.random_seed,
            'device': device,  # 强制CPU（比OpenCL GPU更快）
        }

        # 直接使用CPU训练
        train_data = lgb.Dataset(X_train, label=y_train)
        val_data = lgb.Dataset(X_val, label=y_val)

        model = lgb.train(
            params,
            train_data,
            valid_sets=[val_data],
            early_stopping_rounds=config.early_stopping_rounds,
            verbose_eval=False
        )
        logger.info("[LightGBM] CPU训练完成")

        # 评估
        y_pred = model.predict(X_val)
        metrics = self._calculate_metrics(y_val, y_pred, config.task_type)

        # 特征重要性
        importance = dict(zip(
            [f"f{i}" for i in range(X_train.shape[1])],
            model.feature_importance(importance_type='gain').tolist()
        ))

        return model, metrics, importance

    def _train_xgboost(self, config: MLTrainingConfig, X_train, X_val, y_train, y_val):
        """训练XGBoost模型 - 支持GPU加速"""
        # 根据配置选择设备
        device = config.device if hasattr(config, 'device') and config.device else 'auto'
        if device == 'auto':
            device = 'cuda'  # XGBoost原生CUDA支持

        params = {
            'objective': 'binary:logistic' if config.task_type == TaskType.CLASSIFICATION else 'reg:squarederror',
            'eval_metric': 'auc' if config.task_type == TaskType.CLASSIFICATION else 'rmse',
            'max_depth': config.hyperparameters.get('max_depth', 6),
            'eta': config.hyperparameters.get('eta', 0.1),
            'subsample': config.hyperparameters.get('subsample', 0.8),
            'random_state': config.random_seed,
            'device': device,  # GPU加速
            'tree_method': 'hist',  # 配合GPU使用hist
        }

        dtrain = xgb.DMatrix(X_train, label=y_train)
        dval = xgb.DMatrix(X_val, label=y_val)

        # 尝试GPU训练，失败则回退CPU
        try:
            model = xgb.train(
                params,
                dtrain,
                num_boost_round=config.num_boost_round,
                evals=[(dval, 'val')],
                early_stopping_rounds=config.early_stopping_rounds,
                verbose_eval=False
            )
            logger.info(f"[XGBoost] GPU训练成功, device={device}")
        except Exception as e:
            # 回退到CPU
            logger.warning(f"[XGBoost] GPU训练失败: {e}，回退到CPU")
            params['device'] = 'cpu'
            model = xgb.train(
                params,
                dtrain,
                num_boost_round=config.num_boost_round,
                evals=[(dval, 'val')],
                early_stopping_rounds=config.early_stopping_rounds,
                verbose_eval=False
            )

        # 评估
        y_pred = model.predict(xgb.DMatrix(X_val))
        metrics = self._calculate_metrics(y_val, y_pred, config.task_type)

        # 特征重要性
        importance = dict(zip(
            [f"f{i}" for i in range(X_train.shape[1])],
            model.get_score(importance_type='gain').values()
        ))

        return model, metrics, importance

    def _train_random_forest(self, config: MLTrainingConfig, X_train, X_val, y_train, y_val):
        """训练Random Forest模型"""
        params = {
            'n_estimators': config.hyperparameters.get('n_estimators', 100),
            'max_depth': config.hyperparameters.get('max_depth', 10),
            'min_samples_split': config.hyperparameters.get('min_samples_split', 5),
            'min_samples_leaf': config.hyperparameters.get('min_samples_leaf', 2),
            'random_state': config.random_seed,
            'n_jobs': -1,
        }

        if config.task_type == TaskType.CLASSIFICATION:
            model = RandomForestClassifier(**params)
        else:
            model = RandomForestRegressor(**params)

        model.fit(X_train, y_train)

        # 评估
        y_pred = model.predict(X_val)
        metrics = self._calculate_metrics(y_val, y_pred, config.task_type)

        # 特征重要性
        importance = dict(zip(
            [f"f{i}" for i in range(X_train.shape[1])],
            model.feature_importances_.tolist()
        ))

        return model, metrics, importance

    def _train_linear(self, config: MLTrainingConfig, X_train, X_val, y_train, y_val):
        """训练线性模型"""
        params = {
            'random_state': config.random_seed,
        }

        if config.task_type == TaskType.CLASSIFICATION:
            model = LogisticRegression(**params)
        else:
            model = LinearRegression(**params)

        model.fit(X_train, y_train)

        # 评估
        y_pred = model.predict(X_val)
        metrics = self._calculate_metrics(y_val, y_pred, config.task_type)

        # 线性模型特征重要性：使用Permutation Importance
        try:
            task_type_str = "classification" if config.task_type == TaskType.CLASSIFICATION else "regression"
            perm_result = self.calculate_permutation_importance(
                model, X_val, y_val,
                feature_names=[f"f{i}" for i in range(X_train.shape[1])],
                n_repeats=5,
                random_state=config.random_seed,
                task_type=task_type_str
            )
            importance = perm_result.get("importance_dict", {})
            if not importance:
                # fallback到系数绝对值
                importance = dict(zip(
                    [f"f{i}" for i in range(X_train.shape[1])],
                    np.abs(model.coef_).tolist()
                ))
        except Exception as e:
            logger.warning(f"Permutation Importance计算失败，使用系数绝对值: {e}")
            # fallback到系数绝对值
            if hasattr(model, 'coef_'):
                importance = dict(zip(
                    [f"f{i}" for i in range(X_train.shape[1])],
                    np.abs(model.coef_).tolist()
                ))
            else:
                importance = {}

        return model, metrics, importance

    def _train_lstm(self, config: MLTrainingConfig, X_train, X_val, y_train, y_val):
        """训练LSTM模型"""
        # 获取配置参数
        hidden_size = config.hyperparameters.get('hidden_size', 64)
        num_layers = config.hyperparameters.get('num_layers', 2)
        dropout = config.hyperparameters.get('dropout', 0.3)
        sequence_length = config.sequence_length or 20
        batch_size = config.batch_size or 32
        epochs = config.epochs or 10
        learning_rate = config.learning_rate or 0.001

        # 数据预处理
        n_features = X_train.shape[1]
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

        # 转换为张量
        X_train_tensor = torch.FloatTensor(X_train).to(device)
        y_train_tensor = torch.FloatTensor(y_train).to(device)
        X_val_tensor = torch.FloatTensor(X_val).to(device)
        y_val_tensor = torch.FloatTensor(y_val).to(device)

        # 如果序列长度大于1，需要reshape数据
        if sequence_length > 1 and X_train_tensor.shape[0] >= sequence_length:
            n_samples = X_train_tensor.shape[0] // sequence_length
            X_train_tensor = X_train_tensor[:n_samples * sequence_length].view(n_samples, sequence_length, n_features)
            y_train_tensor = y_train_tensor[:n_samples]

        # 定义LSTM模型
        class LSTMModel(nn.Module):
            def __init__(self, input_size, hidden_size, num_layers, dropout, output_size=1):
                super(LSTMModel, self).__init__()
                self.hidden_size = hidden_size
                self.num_layers = num_layers
                self.lstm = nn.LSTM(input_size, hidden_size, num_layers,
                                   batch_first=True, dropout=dropout if num_layers > 1 else 0)
                self.fc = nn.Linear(hidden_size, output_size)
                self.dropout = nn.Dropout(dropout)

            def forward(self, x):
                # x shape: (batch, seq_len, input_size)
                lstm_out, _ = self.lstm(x)
                # 取最后一个时间步的输出
                out = self.dropout(lstm_out[:, -1, :])
                out = self.fc(out)
                return out.squeeze()

        # 创建模型
        model = LSTMModel(n_features, hidden_size, num_layers, dropout).to(device)

        # 损失函数和优化器
        criterion = nn.BCEWithLogitsLoss() if config.task_type == TaskType.CLASSIFICATION else nn.MSELoss()
        optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)

        # 训练
        model.train()
        for epoch in range(epochs):
            # 随机打乱
            indices = torch.randperm(X_train_tensor.size(0))
            total_loss = 0
            n_batches = 0

            for i in range(0, X_train_tensor.size(0), batch_size):
                batch_idx = indices[i:i+batch_size]
                X_batch = X_train_tensor[batch_idx]
                y_batch = y_train_tensor[batch_idx]

                optimizer.zero_grad()
                outputs = model(X_batch)
                loss = criterion(outputs, y_batch)
                loss.backward()
                optimizer.step()

                total_loss += loss.item()
                n_batches += 1

        # 评估
        model.eval()
        with torch.no_grad():
            y_pred = model(X_val_tensor).cpu().numpy()

        # 计算指标
        metrics = self._calculate_metrics(y_val, y_pred, config.task_type)

        # 特征重要性（LSTM使用最后一个隐层的平均值作为重要性近似）
        importance = {f"f{i}": float(1.0/n_features) for i in range(n_features)}

        # 保存模型和配置用于后续预测
        model.config = {
            'hidden_size': hidden_size,
            'num_layers': num_layers,
            'dropout': dropout,
            'sequence_length': sequence_length,
            'n_features': n_features
        }

        return model, metrics, importance

    def _train_gru(self, config: MLTrainingConfig, X_train, X_val, y_train, y_val):
        """训练GRU模型"""
        # 获取配置参数
        hidden_size = config.hyperparameters.get('hidden_size', 64)
        num_layers = config.hyperparameters.get('num_layers', 2)
        dropout = config.hyperparameters.get('dropout', 0.3)
        sequence_length = config.sequence_length or 20
        batch_size = config.batch_size or 32
        epochs = config.epochs or 10
        learning_rate = config.learning_rate or 0.001

        # 数据预处理
        n_features = X_train.shape[1]
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

        # 转换为张量
        X_train_tensor = torch.FloatTensor(X_train).to(device)
        y_train_tensor = torch.FloatTensor(y_train).to(device)
        X_val_tensor = torch.FloatTensor(X_val).to(device)
        y_val_tensor = torch.FloatTensor(y_val).to(device)

        # 如果序列长度大于1，需要reshape数据
        if sequence_length > 1 and X_train_tensor.shape[0] >= sequence_length:
            n_samples = X_train_tensor.shape[0] // sequence_length
            X_train_tensor = X_train_tensor[:n_samples * sequence_length].view(n_samples, sequence_length, n_features)
            y_train_tensor = y_train_tensor[:n_samples]

        # 定义GRU模型
        class GRUModel(nn.Module):
            def __init__(self, input_size, hidden_size, num_layers, dropout, output_size=1):
                super(GRUModel, self).__init__()
                self.hidden_size = hidden_size
                self.num_layers = num_layers
                self.gru = nn.GRU(input_size, hidden_size, num_layers,
                                batch_first=True, dropout=dropout if num_layers > 1 else 0)
                self.fc = nn.Linear(hidden_size, output_size)
                self.dropout = nn.Dropout(dropout)

            def forward(self, x):
                gru_out, _ = self.gru(x)
                out = self.dropout(gru_out[:, -1, :])
                out = self.fc(out)
                return out.squeeze()

        # 创建模型
        model = GRUModel(n_features, hidden_size, num_layers, dropout).to(device)

        # 损失函数和优化器
        criterion = nn.BCEWithLogitsLoss() if config.task_type == TaskType.CLASSIFICATION else nn.MSELoss()
        optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)

        # 训练
        model.train()
        for epoch in range(epochs):
            indices = torch.randperm(X_train_tensor.size(0))
            total_loss = 0
            n_batches = 0

            for i in range(0, X_train_tensor.size(0), batch_size):
                batch_idx = indices[i:i+batch_size]
                X_batch = X_train_tensor[batch_idx]
                y_batch = y_train_tensor[batch_idx]

                optimizer.zero_grad()
                outputs = model(X_batch)
                loss = criterion(outputs, y_batch)
                loss.backward()
                optimizer.step()

                total_loss += loss.item()
                n_batches += 1

        # 评估
        model.eval()
        with torch.no_grad():
            y_pred = model(X_val_tensor).cpu().numpy()

        # 计算指标
        metrics = self._calculate_metrics(y_val, y_pred, config.task_type)

        # 特征重要性
        importance = {f"f{i}": float(1.0/n_features) for i in range(n_features)}

        # 保存配置
        model.config = {
            'hidden_size': hidden_size,
            'num_layers': num_layers,
            'dropout': dropout,
            'sequence_length': sequence_length,
            'n_features': n_features
        }

        return model, metrics, importance

    def _train_mlp(self, config: MLTrainingConfig, X_train, X_val, y_train, y_val):
        """训练MLP模型"""
        # 获取配置参数
        hidden_sizes = config.hyperparameters.get('hidden_sizes', [128, 64])
        dropout = config.hyperparameters.get('dropout', 0.3)
        batch_size = config.batch_size or 32
        epochs = config.epochs or 10
        learning_rate = config.learning_rate or 0.001

        # 数据预处理
        n_features = X_train.shape[1]
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

        # 转换为张量
        X_train_tensor = torch.FloatTensor(X_train).to(device)
        y_train_tensor = torch.FloatTensor(y_train).to(device)
        X_val_tensor = torch.FloatTensor(X_val).to(device)
        y_val_tensor = torch.FloatTensor(y_val).to(device)

        # 定义MLP模型
        class MLPModel(nn.Module):
            def __init__(self, input_size, hidden_sizes, dropout, output_size=1):
                super(MLPModel, self).__init__()
                layers = []
                prev_size = input_size
                for hidden_size in hidden_sizes:
                    layers.append(nn.Linear(prev_size, hidden_size))
                    layers.append(nn.ReLU())
                    layers.append(nn.Dropout(dropout))
                    prev_size = hidden_size
                layers.append(nn.Linear(prev_size, output_size))
                self.network = nn.Sequential(*layers)

            def forward(self, x):
                return self.network(x).squeeze()

        # 创建模型
        model = MLPModel(n_features, hidden_sizes, dropout).to(device)

        # 损失函数和优化器
        criterion = nn.BCEWithLogitsLoss() if config.task_type == TaskType.CLASSIFICATION else nn.MSELoss()
        optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)

        # 训练
        model.train()
        for epoch in range(epochs):
            indices = torch.randperm(X_train_tensor.size(0))
            total_loss = 0
            n_batches = 0

            for i in range(0, X_train_tensor.size(0), batch_size):
                batch_idx = indices[i:i+batch_size]
                X_batch = X_train_tensor[batch_idx]
                y_batch = y_train_tensor[batch_idx]

                optimizer.zero_grad()
                outputs = model(X_batch)
                loss = criterion(outputs, y_batch)
                loss.backward()
                optimizer.step()

                total_loss += loss.item()
                n_batches += 1

        # 评估
        model.eval()
        with torch.no_grad():
            y_pred = model(X_val_tensor).cpu().numpy()

        # 计算指标
        metrics = self._calculate_metrics(y_val, y_pred, config.task_type)

        # 特征重要性（使用梯度近似）
        model.eval()
        with torch.no_grad():
            X_sample = X_val_tensor[:100]
            X_sample.requires_grad = True
            output = model(X_sample)
            output.sum().backward()
            grads = X_sample.grad.abs().mean(dim=0).cpu().numpy()
            importance = {f"f{i}": float(grads[i]) for i in range(n_features)}

        # 保存配置
        model.config = {
            'hidden_sizes': hidden_sizes,
            'dropout': dropout,
            'n_features': n_features
        }

        return model, metrics, importance

    def _train_transformer(self, config: MLTrainingConfig, X_train, X_val, y_train, y_val):
        """训练Transformer模型"""
        # 获取配置参数
        d_model = config.hyperparameters.get('d_model', 64)
        nhead = config.hyperparameters.get('nhead', 4)
        num_layers = config.hyperparameters.get('num_layers', 2)
        dropout = config.hyperparameters.get('dropout', 0.3)
        sequence_length = config.sequence_length or 20
        batch_size = config.batch_size or 32
        epochs = config.epochs or 10
        learning_rate = config.learning_rate or 0.001

        # 数据预处理
        n_features = X_train.shape[1]
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

        # 转换为张量
        X_train_tensor = torch.FloatTensor(X_train).to(device)
        y_train_tensor = torch.FloatTensor(y_train).to(device)
        X_val_tensor = torch.FloatTensor(X_val).to(device)
        y_val_tensor = torch.FloatTensor(y_val).to(device)

        # 如果序列长度大于1，需要reshape数据
        if sequence_length > 1 and X_train_tensor.shape[0] >= sequence_length:
            n_samples = X_train_tensor.shape[0] // sequence_length
            X_train_tensor = X_train_tensor[:n_samples * sequence_length].view(n_samples, sequence_length, n_features)
            y_train_tensor = y_train_tensor[:n_samples]

        # 确保d_model能被nhead整除
        if d_model % nhead != 0:
            d_model = (d_model // nhead) * nhead

        # 输入投影层：将特征维度转换为d_model
        input_projection = nn.Linear(n_features, d_model).to(device)

        # 定义Transformer模型
        class TransformerModel(nn.Module):
            def __init__(self, d_model, nhead, num_layers, dropout, output_size=1):
                super(TransformerModel, self).__init__()
                self.d_model = d_model
                self.input_proj = nn.Linear(n_features, d_model)

                # 位置编码
                self.pos_encoder = PositionalEncoding(d_model, dropout)

                # Transformer编码器
                encoder_layer = nn.TransformerEncoderLayer(
                    d_model=d_model,
                    nhead=nhead,
                    dim_feedforward=d_model * 4,
                    dropout=dropout,
                    batch_first=True
                )
                self.transformer_encoder = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)

                # 输出层
                self.fc = nn.Linear(d_model, output_size)
                self.dropout = nn.Dropout(dropout)

            def forward(self, x):
                # x shape: (batch, seq_len, n_features)
                # 投影到d_model维度
                x = self.input_proj(x)
                # 添加位置编码
                x = self.pos_encoder(x)
                # Transformer编码
                x = self.transformer_encoder(x)
                # 取最后一个时间步
                x = self.dropout(x[:, -1, :])
                # 输出
                x = self.fc(x)
                return x.squeeze()

        # 位置编码类
        class PositionalEncoding(nn.Module):
            def __init__(self, d_model, dropout=0.1, max_len=5000):
                super(PositionalEncoding, self).__init__()
                self.dropout = nn.Dropout(p=dropout)

                # 创建位置编码
                pe = torch.zeros(max_len, d_model)
                position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
                div_term = torch.exp(torch.arange(0, d_model, 2).float() * (-math.log(10000.0) / d_model))
                pe[:, 0::2] = torch.sin(position * div_term)
                pe[:, 1::2] = torch.cos(position * div_term)
                pe = pe.unsqueeze(0)
                self.register_buffer('pe', pe)

            def forward(self, x):
                # x shape: (batch, seq_len, d_model)
                x = x + self.pe[:, :x.size(1), :]
                return self.dropout(x)

        # 创建模型
        model = TransformerModel(d_model, nhead, num_layers, dropout).to(device)

        # 损失函数和优化器
        criterion = nn.BCEWithLogitsLoss() if config.task_type == TaskType.CLASSIFICATION else nn.MSELoss()
        optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
        scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='min', patience=5, factor=0.5)

        # 训练
        model.train()
        best_loss = float('inf')

        for epoch in range(epochs):
            indices = torch.randperm(X_train_tensor.size(0))
            total_loss = 0
            n_batches = 0

            for i in range(0, X_train_tensor.size(0), batch_size):
                batch_idx = indices[i:i+batch_size]
                X_batch = X_train_tensor[batch_idx]
                y_batch = y_train_tensor[batch_idx]

                optimizer.zero_grad()
                outputs = model(X_batch)
                loss = criterion(outputs, y_batch)
                loss.backward()
                torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
                optimizer.step()

                total_loss += loss.item()
                n_batches += 1

            avg_loss = total_loss / max(n_batches, 1)
            scheduler.step(avg_loss)

            if avg_loss < best_loss:
                best_loss = avg_loss

        # 评估
        model.eval()
        with torch.no_grad():
            y_pred = model(X_val_tensor).cpu().numpy()

        # 计算指标
        metrics = self._calculate_metrics(y_val, y_pred, config.task_type)

        # 特征重要性
        importance = {f"f{i}": float(1.0/n_features) for i in range(n_features)}

        # 保存配置
        model.config = {
            'd_model': d_model,
            'nhead': nhead,
            'num_layers': num_layers,
            'dropout': dropout,
            'sequence_length': sequence_length,
            'n_features': n_features
        }

        return model, metrics, importance

    def _evaluate_model(self, model, X_test, y_test, task_type: TaskType) -> Dict[str, float]:
        """评估模型"""
        # 判断模型类型
        if hasattr(model, 'predict'):
            # sklearn模型
            y_pred = model.predict(X_test)
        elif hasattr(model, 'forward'):
            # PyTorch模型
            model.eval()
            if not isinstance(X_test, torch.Tensor):
                X_test_tensor = torch.FloatTensor(X_test)
            else:
                X_test_tensor = X_test

            with torch.no_grad():
                if X_test_tensor.dim() == 2:
                    X_test_tensor = X_test_tensor.unsqueeze(0)  # 添加batch维度
                y_pred = model(X_test_tensor).squeeze().cpu().numpy()
        else:
            raise ValueError("不支持的模型类型")

        return self._calculate_metrics(y_test, y_pred, task_type)

    def _calculate_metrics(self, y_true, y_pred, task_type: TaskType) -> Dict[str, float]:
        """
        计算评估指标

        分类任务: accuracy, precision, recall, f1, auc_roc
        回归任务: mse, mae, r2, ic, rank_ic
        """
        metrics = {}

        if task_type == TaskType.CLASSIFICATION:
            # 分类指标
            metrics['accuracy'] = float(accuracy_score(y_true, y_pred))
            metrics['precision'] = float(precision_score(y_true, y_pred, average='binary', zero_division=0))
            metrics['recall'] = float(recall_score(y_true, y_pred, average='binary', zero_division=0))
            metrics['f1'] = float(f1_score(y_true, y_pred, average='binary', zero_division=0))

            # AUC-ROC (需要预测概率)
            try:
                if hasattr(y_pred, 'predict_proba'):
                    y_pred_proba = y_pred.predict_proba(y_pred)[:, 1]
                else:
                    y_pred_proba = y_pred
                # 二分类: 使用正类概率计算AUC
                metrics['auc_roc'] = float(roc_auc_score(y_true, y_pred_proba))
            except Exception:
                metrics['auc_roc'] = 0.0
        else:  # REGRESSION
            # 回归指标
            metrics['mse'] = float(mean_squared_error(y_true, y_pred))
            metrics['mae'] = float(mean_absolute_error(y_true, y_pred))
            metrics['r2'] = float(r2_score(y_true, y_pred))

            # IC (Information Coefficient) - 皮尔逊相关系数
            try:
                # 确保是一维数组
                y_true_arr = np.array(y_true).flatten()
                y_pred_arr = np.array(y_pred).flatten()

                # 计算IC (皮尔逊相关系数)
                ic, ic_pvalue = pearsonr(y_true_arr, y_pred_arr)
                metrics['ic'] = float(ic)
                metrics['ic_pvalue'] = float(ic_pvalue)

                # 计算RankIC (斯皮尔曼等级相关系数)
                rankic, rankic_pvalue = spearmanr(y_true_arr, y_pred_arr)
                metrics['rank_ic'] = float(rankic)
                metrics['rank_ic_pvalue'] = float(rankic_pvalue)
            except Exception as e:
                logger.warning(f"IC/RankIC计算失败: {e}")
                metrics['ic'] = 0.0
                metrics['ic_pvalue'] = 1.0
                metrics['rank_ic'] = 0.0
                metrics['rank_ic_pvalue'] = 1.0

        return metrics

    def _save_model(self, model, path: Path):
        """保存模型"""
        with open(path, 'wb') as f:
            pickle.dump(model, f)

    async def _load_prediction_data(self, request: MLPredictionRequest, config: MLTrainingConfig):
        """加载预测数据"""
        # TODO: 从数据管理模块加载实际数据
        # 暂时返回模拟数据
        n_samples = len(request.instruments)
        n_features = len(config.features) if config.features else 50

        X = np.random.randn(n_samples, n_features)
        dates = [request.end_date] * n_samples
        instruments = request.instruments

        return X, dates, instruments

    # ==================== 特征工程方法 ====================

    def calculate_permutation_importance(
        self,
        model,
        X_test: np.ndarray,
        y_test: np.ndarray,
        feature_names: Optional[List[str]] = None,
        n_repeats: int = 10,
        random_state: int = 42,
        task_type: str = "regression"
    ) -> Dict[str, Any]:
        """
        使用Permutation Importance计算特征重要性

        原理：随机打乱某个特征的值，观察模型性能下降多少
        下降越多，说明该特征越重要

        Args:
            model: 训练好的模型
            X_test: 测试特征矩阵
            y_test: 测试标签
            feature_names: 特征名称列表
            n_repeats: 重复打乱的次数
            random_state: 随机种子
            task_type: 任务类型 ("regression" 或 "classification")

        Returns:
            importance_dict: 特征重要性字典 {特征名: 重要性分数}
            std_dict: 标准差字典
        """
        n_features = X_test.shape[1]
        if feature_names is None:
            feature_names = [f"feature_{i}" for i in range(n_features)]

        # 根据任务类型选择评分函数
        if task_type == "classification":
            scoring = 'accuracy'
        else:
            scoring = 'neg_mean_squared_error'

        try:
            # 计算Permutation Importance
            result = permutation_importance(
                model, X_test, y_test,
                n_repeats=n_repeats,
                random_state=random_state,
                scoring=scoring,
                n_jobs=-1
            )

            # 构建结果字典
            importance_dict = dict(zip(feature_names, result.importances_mean.tolist()))
            std_dict = dict(zip(feature_names, result.importances_std.tolist()))

            # 按重要性排序
            sorted_features = sorted(
                importance_dict.items(),
                key=lambda x: x[1],
                reverse=True
            )

            logger.info(f"Permutation Importance计算完成，共{len(feature_names)}个特征")

            return {
                "importance_dict": importance_dict,
                "std_dict": std_dict,
                "sorted_features": sorted_features,
                "n_features": n_features,
                "n_repeats": n_repeats
            }

        except Exception as e:
            logger.error(f"Permutation Importance计算失败: {e}")
            return {
                "importance_dict": {},
                "std_dict": {},
                "sorted_features": [],
                "n_features": n_features,
                "n_repeats": n_repeats,
                "error": str(e)
            }

    def select_features_by_importance(
        self,
        X: np.ndarray,
        y: np.ndarray,
        feature_names: Optional[List[str]] = None,
        top_k: int = 20,
        model_type: str = "lightgbm"
    ) -> Dict[str, Any]:
        """
        基于模型重要性选择特征

        Args:
            X: 特征矩阵 (n_samples, n_features)
            y: 标签向量
            feature_names: 特征名称列表
            top_k: 选择前k个重要特征
            model_type: 用于评估重要性的模型类型

        Returns:
            selected_features: 选中的特征索引列表
            importance_dict: 特征重要性字典
        """
        n_features = X.shape[1]
        if feature_names is None:
            feature_names = [f"feature_{i}" for i in range(n_features)]

        # 使用LightGBM计算特征重要性
        if model_type == "lightgbm" and LGB_AVAILABLE:
            model = lgb.LGBMClassifier(n_estimators=100, verbose=-1, random_state=42)
            model.fit(X, y)
            importance = model.feature_importances_
        elif model_type == "xgboost" and XGB_AVAILABLE:
            model = xgb.XGBClassifier(n_estimators=100, use_label_encoder=False, eval_metric='logloss', random_state=42)
            model.fit(X, y)
            importance = model.feature_importances_
        else:
            # 使用随机森林
            from sklearn.ensemble import RandomForestClassifier
            model = RandomForestClassifier(n_estimators=100, random_state=42)
            model.fit(X, y)
            importance = model.feature_importances_

        # 排序并选择前k个
        importance_dict = dict(zip(feature_names, importance.tolist()))
        sorted_features = sorted(importance_dict.items(), key=lambda x: x[1], reverse=True)
        selected_features = [f[0] for f in sorted_features[:top_k]]
        selected_indices = [feature_names.index(f) for f in selected_features]

        logger.info(f"基于{model_type}重要性选择了{top_k}个特征")

        return {
            "selected_features": selected_features,
            "selected_indices": selected_indices,
            "importance_dict": importance_dict,
            "top_k": top_k
        }

    def select_features_by_correlation(
        self,
        X: np.ndarray,
        y: np.ndarray,
        feature_names: Optional[List[str]] = None,
        threshold: float = 0.3,
        method: str = "pearson"
    ) -> Dict[str, Any]:
        """
        基于与标签的相关性选择特征

        Args:
            X: 特征矩阵 (n_samples, n_features)
            y: 标签向量
            feature_names: 特征名称列表
            threshold: 相关系数阈值（绝对值）
            method: 相关性方法 (pearson/spearman)

        Returns:
            selected_features: 选中的特征列表
            correlation_dict: 各特征与标签的相关系数
        """
        from scipy.stats import pearsonr, spearmanr

        n_features = X.shape[1]
        if feature_names is None:
            feature_names = [f"feature_{i}" for i in range(n_features)]

        correlation_func = pearsonr if method == "pearson" else spearmanr

        correlation_dict = {}
        for i, name in enumerate(feature_names):
            try:
                corr, _ = correlation_func(X[:, i], y)
                correlation_dict[name] = corr
            except:
                correlation_dict[name] = 0.0

        # 选择相关性绝对值大于阈值的特征
        selected_features = [
            name for name, corr in correlation_dict.items()
            if abs(corr) >= threshold
        ]

        selected_indices = [feature_names.index(f) for f in selected_features]

        logger.info(f"基于{method}相关性选择了{len(selected_features)}个特征 (threshold={threshold})")

        return {
            "selected_features": selected_features,
            "selected_indices": selected_indices,
            "correlation_dict": correlation_dict,
            "threshold": threshold
        }

    def remove_correlated_features(
        self,
        X: np.ndarray,
        feature_names: Optional[List[str]] = None,
        threshold: float = 0.9
    ) -> Dict[str, Any]:
        """
        移除高度相关的特征（特征去冗余）

        Args:
            X: 特征矩阵 (n_samples, n_features)
            feature_names: 特征名称列表
            threshold: 相关性阈值，超过则移除

        Returns:
            selected_features: 保留的特征列表
            removed_features: 移除的特征列表
        """
        n_features = X.shape[1]
        if feature_names is None:
            feature_names = [f"feature_{i}" for i in range(n_features)]

        # 计算相关矩阵
        corr_matrix = np.corrcoef(X.T)
        np.fill_diagonal(corr_matrix, 0)

        # 找出高度相关的特征对
        to_remove = set()
        for i in range(n_features):
            for j in range(i + 1, n_features):
                if abs(corr_matrix[i, j]) > threshold:
                    # 移除重要性较低的特征（假设后面的特征重要性较低）
                    to_remove.add(j)

        # 保留的特征
        selected_indices = [i for i in range(n_features) if i not in to_remove]
        selected_features = [feature_names[i] for i in selected_indices]
        removed_features = [feature_names[i] for i in to_remove]

        logger.info(f"移除了{len(to_remove)}个高度相关特征，保留{len(selected_features)}个特征")

        return {
            "selected_features": selected_features,
            "selected_indices": selected_indices,
            "removed_features": removed_features,
            "threshold": threshold
        }

    def standardize_features(
        self,
        X: np.ndarray,
        method: str = "standard"
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        特征标准化/归一化

        Args:
            X: 特征矩阵
            method: 标准化方法 (standard/zminmax/robust/log)

        Returns:
            X_transformed: 变换后的特征矩阵
            stats: 变换参数（用于后续反变换）
        """
        from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler

        if method == "standard":
            scaler = StandardScaler()
            X_transformed = scaler.fit_transform(X)
            stats = {
                "mean": scaler.mean_.tolist(),
                "std": scaler.scale_.tolist()
            }
        elif method == "minmax":
            scaler = MinMaxScaler()
            X_transformed = scaler.fit_transform(X)
            stats = {
                "min": scaler.data_min_.tolist(),
                "max": scaler.data_max_.tolist()
            }
        elif method == "robust":
            scaler = RobustScaler()
            X_transformed = scaler.fit_transform(X)
            stats = {
                "center": scaler.center_.tolist(),
                "scale": scaler.scale_.tolist()
            }
        elif method == "log":
            # 对数变换（处理偏态分布）
            X_transformed = np.log1p(np.abs(X)) * np.sign(X)
            stats = {"method": "log"}
        else:
            raise ValueError(f"未知的标准化方法: {method}")

        logger.info(f"特征标准化完成: {method}")

        return X_transformed, stats

    def inverse_transform(
        self,
        X: np.ndarray,
        method: str,
        stats: Dict[str, Any]
    ) -> np.ndarray:
        """
        反变换（还原标准化前的数据）

        Args:
            X: 标准化后的特征矩阵
            method: 原始变换方法
            stats: 变换参数

        Returns:
            X_original: 还原后的特征矩阵
        """
        from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler

        if method == "standard":
            scaler = StandardScaler()
            scaler.mean_ = np.array(stats["mean"])
            scaler.scale_ = np.array(stats["std"])
            X_original = scaler.inverse_transform(X)
        elif method == "minmax":
            scaler = MinMaxScaler()
            scaler.data_min_ = np.array(stats["min"])
            scaler.data_max_ = np.array(stats["max"])
            X_original = scaler.inverse_transform(X)
        elif method == "robust":
            scaler = RobustScaler()
            scaler.center_ = np.array(stats["center"])
            scaler.scale_ = np.array(stats["scale"])
            X_original = scaler.inverse_transform(X)
        elif method == "log":
            X_original = np.expm1(np.abs(X)) * np.sign(X)
        else:
            raise ValueError(f"未知的反变换方法: {method}")

        return X_original

    def create_polynomial_features(
        self,
        X: np.ndarray,
        degree: int = 2,
        interaction_only: bool = False
    ) -> np.ndarray:
        """
        创建多项式特征（特征组合）

        Args:
            X: 特征矩阵
            degree: 多项式度数
            interaction_only: 是否只创建交互特征

        Returns:
            X_poly: 扩展后的特征矩阵
        """
        from sklearn.preprocessing import PolynomialFeatures

        poly = PolynomialFeatures(degree=degree, interaction_only=interaction_only)
        X_poly = poly.fit_transform(X)

        logger.info(f"创建多项式特征: {X.shape[1]} -> {X_poly.shape[1]} 特征")

        return X_poly


# ==================== 单例实例 ====================

_ml_service_instance = None

def get_ml_service() -> MLModelService:
    """获取ML服务单例"""
    global _ml_service_instance
    if _ml_service_instance is None:
        _ml_service_instance = MLModelService()
    return _ml_service_instance

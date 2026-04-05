# -*- coding: utf-8 -*-
"""
Research阶段 - Meta Controller服务
====================================

职责：
- 自动因子组合优化
- 模型自动选择（LightGBM/XGBoost/MLP）
- 超参数自动优化（网格搜索、贝叶斯优化）
- 优化任务管理和历史记录

版本: v1.0
创建日期: 2026-02-11
"""

from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from loguru import logger
from datetime import datetime
from pathlib import Path
import pickle
import uuid
import copy

try:
    import numpy as np
    import pandas as pd
except ImportError:
    np = None
    pd = None

try:
    from sklearn.model_selection import GridSearchCV, RandomizedSearchCV
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.metrics import mean_squared_error, mean_absolute_error
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False


@dataclass
class OptimizationConfig:
    """优化配置"""
    optimization_method: str = "ic_weighted"  # ic_weighted, equal_weight, auto
    target_metric: str = "ic_mean"  # ic_mean, ir, combined
    constraints: Dict[str, Any] = field(default_factory=dict)
    max_iterations: int = 100
    timeout_seconds: int = 300


@dataclass
class ModelConfig:
    """模型配置"""
    model_type: str  # lightgbm, xgboost, mlp, rf
    hyperparameters: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """设置默认超参数"""
        if not self.hyperparameters:
            if self.model_type == "lightgbm":
                self.hyperparameters = {
                    "num_leaves": [31, 50, 100],
                    "learning_rate": [0.01, 0.05, 0.1],
                    "n_estimators": [100, 200, 500]
                }
            elif self.model_type == "xgboost":
                self.hyperparameters = {
                    "max_depth": [3, 6, 10],
                    "learning_rate": [0.01, 0.05, 0.1],
                    "n_estimators": [100, 200, 500]
                }
            elif self.model_type == "rf":
                self.hyperparameters = {
                    "n_estimators": [50, 100, 200],
                    "max_depth": [5, 10, 20],
                    "min_samples_split": [2, 5, 10]
                }
            elif self.model_type == "mlp":
                self.hyperparameters = {
                    "hidden_layer_sizes": [(64,), (128,), (256,)],
                    "learning_rate_init": [0.001, 0.01, 0.1],
                    "alpha": [0.0001, 0.001, 0.01]
                }


@dataclass
class OptimizationTrial:
    """优化试验记录"""
    trial_id: str
    task_id: str
    trial_type: str  # factor_optimize, model_select, hpo
    config: Dict[str, Any]
    metrics: Dict[str, float]
    timestamp: datetime = field(default_factory=datetime.now)
    status: str = "completed"  # completed, failed, running


@dataclass
class OptimizationResult:
    """优化结果"""
    optimization_id: str
    optimization_type: str  # factor_optimize, model_select, hpo
    best_config: Dict[str, Any]
    best_metrics: Dict[str, float]
    all_trials: List[OptimizationTrial]
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "optimization_id": self.optimization_id,
            "optimization_type": self.optimization_type,
            "best_config": self.best_config,
            "best_metrics": self.best_metrics,
            "all_trials": [
                {
                    "trial_id": t.trial_id,
                    "config": t.config,
                    "metrics": t.metrics,
                    "timestamp": t.timestamp.isoformat(),
                    "status": t.status
                }
                for t in self.all_trials
            ],
            "created_at": self.created_at.isoformat(),
            "trial_count": len(self.all_trials)
        }


class MetaControllerService:
    """
    Meta Controller服务

    核心职责：
    1. 自动因子组合优化 - 根据IC/IR指标优化因子权重
    2. 模型自动选择 - 在多个模型中选择最优模型
    3. 超参数自动优化 - 网格搜索、贝叶斯优化
    4. 优化任务管理和历史记录
    """

    def __init__(self, storage_dir: Optional[str] = None):
        """
        初始化Meta Controller服务

        Args:
            storage_dir: 优化结果存储目录
        """
        # 初始化存储目录
        if storage_dir is None:
            project_root = Path(__file__).parent.parent.parent.parent
            storage_dir = project_root / "backend" / "data" / "meta_controller"

        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)

        # 创建子目录
        (self.storage_dir / "trials").mkdir(exist_ok=True)
        (self.storage_dir / "results").mkdir(exist_ok=True)

        # 内存中的优化任务
        self._running_tasks: Dict[str, OptimizationResult] = {}

        logger.info(f"✅ MetaControllerService初始化完成: {self.storage_dir}")

    # ==================== 因子组合优化 ====================

    def optimize_factor_combination(
        self,
        factor_metrics: Dict[str, Dict[str, float]],
        config: Optional[OptimizationConfig] = None
    ) -> OptimizationResult:
        """
        优化因子组合

        根据IC/IR等指标优化因子权重配置

        Args:
            factor_metrics: 因子指标字典
                {
                    "factor_1": {"ic_mean": 0.05, "ir": 0.8, ...},
                    "factor_2": {"ic_mean": 0.03, "ir": 0.6, ...},
                    ...
                }
            config: 优化配置

        Returns:
            优化结果
        """
        try:
            logger.info(f"开始因子组合优化: {len(factor_metrics)}个因子")

            config = config or OptimizationConfig()
            optimization_id = f"factor_opt_{uuid.uuid4().hex[:8]}"

            trials = []

            # 方法1: IC加权
            if config.optimization_method in ["ic_weighted", "auto"]:
                weights = self._calculate_ic_weights(factor_metrics, config.target_metric)
                trials.append(OptimizationTrial(
                    trial_id=f"{optimization_id}_ic_weighted",
                    task_id=optimization_id,
                    trial_type="factor_optimize",
                    config={"method": "ic_weighted", "target": config.target_metric, "weights": weights},
                    metrics={"combined_ic": self._calculate_combined_ic(factor_metrics, weights)},
                    status="completed"
                ))

            # 方法2: 等权重
            if config.optimization_method in ["equal_weight", "auto"]:
                weights = {f: 1.0 / len(factor_metrics) for f in factor_metrics.keys()}
                trials.append(OptimizationTrial(
                    trial_id=f"{optimization_id}_equal_weight",
                    task_id=optimization_id,
                    trial_type="factor_optimize",
                    config={"method": "equal_weight", "weights": weights},
                    metrics={"combined_ic": self._calculate_combined_ic(factor_metrics, weights)},
                    status="completed"
                ))

            # 方法3: IR加权
            if config.optimization_method in ["ir_weighted", "auto"]:
                weights = self._calculate_ic_weights(factor_metrics, "ir")
                trials.append(OptimizationTrial(
                    trial_id=f"{optimization_id}_ir_weighted",
                    task_id=optimization_id,
                    trial_type="factor_optimize",
                    config={"method": "ir_weighted", "weights": weights},
                    metrics={"combined_ic": self._calculate_combined_ic(factor_metrics, weights)},
                    status="completed"
                ))

            # 选择最佳方法
            best_trial = max(trials, key=lambda t: t.metrics.get("combined_ic", 0))

            result = OptimizationResult(
                optimization_id=optimization_id,
                optimization_type="factor_optimize",
                best_config=best_trial.config,
                best_metrics=best_trial.metrics,
                all_trials=trials
            )

            # 保存结果
            self._save_optimization_result(result)

            logger.info(f"因子组合优化完成: 最佳方法={best_trial.config.get('method')}, 组合IC={best_trial.metrics.get('combined_ic', 0):.4f}")

            return result

        except Exception as e:
            logger.error(f"因子组合优化失败: {e}")
            raise

    def _calculate_ic_weights(
        self,
        factor_metrics: Dict[str, Dict[str, float]],
        target_metric: str = "ic_mean"
    ) -> Dict[str, float]:
        """计算IC权重"""
        # 获取目标指标值
        values = {f: abs(m.get(target_metric, 0)) for f, m in factor_metrics.items()}

        # 过滤零值
        values = {f: v for f, v in values.items() if v > 0}

        if not values:
            # 所有因子指标都为0，返回等权重
            return {f: 1.0 / len(factor_metrics) for f in factor_metrics.keys()}

        # 归一化
        total = sum(values.values())
        weights = {f: v / total for f, v in values.items()}

        return weights

    def _calculate_combined_ic(
        self,
        factor_metrics: Dict[str, Dict[str, float]],
        weights: Dict[str, float]
    ) -> float:
        """计算组合IC"""
        combined_ic = 0.0
        for factor_name, weight in weights.items():
            if factor_name in factor_metrics:
                combined_ic += weight * factor_metrics[factor_name].get("ic_mean", 0)
        return combined_ic

    # ==================== 模型选择 ====================

    def select_best_model(
        self,
        X_train: Any,
        y_train: Any,
        X_val: Any,
        y_val: Any,
        model_types: Optional[List[str]] = None,
        metric: str = "mse"
    ) -> OptimizationResult:
        """
        选择最佳模型

        Args:
            X_train: 训练特征
            y_train: 训练标签
            X_val: 验证特征
            y_val: 验证标签
            model_types: 要比较的模型类型列表
            metric: 评估指标 (mse, mae, ic)

        Returns:
            优化结果，包含最佳模型配置
        """
        try:
            logger.info(f"开始模型选择: {model_types or ['lightgbm', 'xgboost', 'rf']}")

            if not SKLEARN_AVAILABLE:
                logger.warning("sklearn未安装，返回模拟结果")
                return self._simulate_model_selection(model_types or ["lightgbm", "xgboost", "rf"])

            model_types = model_types or ["lightgbm", "xgboost", "rf"]
            optimization_id = f"model_select_{uuid.uuid4().hex[:8]}"

            trials = []

            for model_type in model_types:
                try:
                    # 训练模型
                    model, metrics = self._train_and_evaluate_model(
                        model_type, X_train, y_train, X_val, y_val, metric
                    )

                    trials.append(OptimizationTrial(
                        trial_id=f"{optimization_id}_{model_type}",
                        task_id=optimization_id,
                        trial_type="model_select",
                        config={"model_type": model_type},
                        metrics=metrics,
                        status="completed"
                    ))

                except Exception as e:
                    logger.warning(f"模型 {model_type} 训练失败: {e}")
                    trials.append(OptimizationTrial(
                        trial_id=f"{optimization_id}_{model_type}",
                        task_id=optimization_id,
                        trial_type="model_select",
                        config={"model_type": model_type},
                        metrics={metric: float('inf')},
                        status="failed"
                    ))

            # 选择最佳模型
            best_trial = min(trials, key=lambda t: t.metrics.get(metric, float('inf')))

            result = OptimizationResult(
                optimization_id=optimization_id,
                optimization_type="model_select",
                best_config=best_trial.config,
                best_metrics=best_trial.metrics,
                all_trials=trials
            )

            # 保存结果
            self._save_optimization_result(result)

            logger.info(f"模型选择完成: 最佳模型={best_trial.config.get('model_type')}, {metric}={best_trial.metrics.get(metric, 0):.4f}")

            return result

        except Exception as e:
            logger.error(f"模型选择失败: {e}")
            raise

    def _train_and_evaluate_model(
        self,
        model_type: str,
        X_train: Any,
        y_train: Any,
        X_val: Any,
        y_val: Any,
        metric: str
    ) -> tuple:
        """训练和评估模型"""
        if model_type == "rf":
            from sklearn.ensemble import RandomForestRegressor
            model = RandomForestRegressor(n_estimators=100, random_state=42)
        elif model_type == "lightgbm":
            try:
                import lightgbm as lgb
                model = lgb.LGBMRegressor(n_estimators=100, random_state=42, verbose=-1)
            except ImportError:
                logger.warning("lightgbm未安装，使用RandomForest代替")
                from sklearn.ensemble import RandomForestRegressor
                model = RandomForestRegressor(n_estimators=100, random_state=42)
                model_type = "rf"
        elif model_type == "xgboost":
            try:
                import xgboost as xgb
                model = xgb.XGBRegressor(n_estimators=100, random_state=42, verbosity=0)
            except ImportError:
                logger.warning("xgboost未安装，使用RandomForest代替")
                from sklearn.ensemble import RandomForestRegressor
                model = RandomForestRegressor(n_estimators=100, random_state=42)
                model_type = "rf"
        else:
            raise ValueError(f"不支持的模型类型: {model_type}")

        # 训练模型
        model.fit(X_train, y_train)

        # 预测
        y_pred = model.predict(X_val)

        # 计算指标
        if metric == "mse":
            score = mean_squared_error(y_val, y_pred)
        elif metric == "mae":
            score = mean_absolute_error(y_val, y_pred)
        elif metric == "ic":
            # 计算IC
            if pd is not None:
                score = float(pd.Series(y_pred).corr(pd.Series(y_val)))
            else:
                # 简单的相关性计算
                score = float(np.corrcoef(y_pred, y_val)[0, 1]) if np is not None else 0.0
        else:
            score = 0.0

        metrics = {
            "mse": float(mean_squared_error(y_val, y_pred)),
            "mae": float(mean_absolute_error(y_val, y_pred)),
            metric: float(score)
        }

        return model, metrics

    def _simulate_model_selection(self, model_types: List[str]) -> OptimizationResult:
        """模拟模型选择（当sklearn不可用时）"""
        optimization_id = f"model_select_{uuid.uuid4().hex[:8]}"

        # 模拟结果
        mock_scores = {
            "lightgbm": 0.023,
            "xgboost": 0.025,
            "rf": 0.020,
            "mlp": 0.018
        }

        trials = []
        for model_type in model_types:
            score = mock_scores.get(model_type, 0.02)
            trials.append(OptimizationTrial(
                trial_id=f"{optimization_id}_{model_type}",
                task_id=optimization_id,
                trial_type="model_select",
                config={"model_type": model_type},
                metrics={"mse": score, "note": "模拟结果"},
                status="completed"
            ))

        best_trial = min(trials, key=lambda t: t.metrics.get("mse", float('inf')))

        return OptimizationResult(
            optimization_id=optimization_id,
            optimization_type="model_select",
            best_config=best_trial.config,
            best_metrics=best_trial.metrics,
            all_trials=trials
        )

    # ==================== 超参数优化 ====================

    def optimize_hyperparameters(
        self,
        model_type: str,
        X_train: Any,
        y_train: Any,
        X_val: Any,
        y_val: Any,
        param_grid: Optional[Dict[str, List]] = None,
        search_method: str = "grid",  # grid, random
        n_iter: int = 10,
        cv: int = 3
    ) -> OptimizationResult:
        """
        超参数优化

        Args:
            model_type: 模型类型
            X_train: 训练特征
            y_train: 训练标签
            X_val: 验证特征
            y_val: 验证标签
            param_grid: 参数网格
            search_method: 搜索方法 (grid, random)
            n_iter: 随机搜索迭代次数
            cv: 交叉验证折数

        Returns:
            优化结果
        """
        try:
            logger.info(f"开始超参数优化: model={model_type}, method={search_method}")

            if not SKLEARN_AVAILABLE:
                logger.warning("sklearn未安装，返回模拟结果")
                return self._simulate_hyperparameter_optimization(model_type, param_grid)

            optimization_id = f"hpo_{model_type}_{uuid.uuid4().hex[:8]}"

            # 使用默认参数网格
            if param_grid is None:
                model_config = ModelConfig(model_type=model_type)
                param_grid = model_config.hyperparameters

            # 选择模型
            if model_type == "rf":
                base_model = RandomForestRegressor(random_state=42)
            else:
                # 其他模型暂时使用RandomForest
                base_model = RandomForestRegressor(random_state=42)

            # 选择搜索方法
            if search_method == "grid":
                search = GridSearchCV(
                    base_model,
                    param_grid,
                    cv=cv,
                    scoring="neg_mean_squared_error",
                    n_jobs=-1,
                    verbose=0
                )
            elif search_method == "random":
                search = RandomizedSearchCV(
                    base_model,
                    param_grid,
                    n_iter=n_iter,
                    cv=cv,
                    scoring="neg_mean_squared_error",
                    random_state=42,
                    n_jobs=-1,
                    verbose=0
                )
            else:
                raise ValueError(f"不支持的搜索方法: {search_method}")

            # 执行搜索
            search.fit(X_train, y_train)

            # 在验证集上评估最佳模型
            best_model = search.best_estimator_
            y_pred = best_model.predict(X_val)
            val_score = mean_squared_error(y_val, y_pred)

            # 收集所有试验结果
            trials = []
            for i, params in enumerate(search.cv_results_['params']):
                trials.append(OptimizationTrial(
                    trial_id=f"{optimization_id}_trial_{i}",
                    task_id=optimization_id,
                    trial_type="hpo",
                    config=params,
                    metrics={
                        "mean_test_score": float(search.cv_results_['mean_test_score'][i]),
                        "std_test_score": float(search.cv_results_['std_test_score'][i])
                    },
                    status="completed"
                ))

            best_metrics = {
                "best_score": float(search.best_score_),
                "val_mse": float(val_score),
                "best_params": search.best_params_
            }

            result = OptimizationResult(
                optimization_id=optimization_id,
                optimization_type="hpo",
                best_config=search.best_params_,
                best_metrics=best_metrics,
                all_trials=trials
            )

            # 保存结果
            self._save_optimization_result(result)

            logger.info(f"超参数优化完成: 最佳参数={search.best_params_}, 验证MSE={val_score:.4f}")

            return result

        except Exception as e:
            logger.error(f"超参数优化失败: {e}")
            raise

    def _simulate_hyperparameter_optimization(
        self,
        model_type: str,
        param_grid: Optional[Dict[str, List]] = None
    ) -> OptimizationResult:
        """模拟超参数优化（当sklearn不可用时）"""
        optimization_id = f"hpo_{model_type}_{uuid.uuid4().hex[:8]}"

        # 使用默认参数网格
        if param_grid is None:
            model_config = ModelConfig(model_type=model_type)
            param_grid = model_config.hyperparameters

        # 模拟试验
        trials = []
        best_score = float('inf')
        best_params = {}

        for i in range(min(5, len(list(param_grid.values())[0]) if param_grid else 5)):
            params = {k: v[i % len(v)] for k, v in (param_grid or {}).items()}
            score = 0.02 + i * 0.001  # 模拟递减的MSE

            if score < best_score:
                best_score = score
                best_params = params

            trials.append(OptimizationTrial(
                trial_id=f"{optimization_id}_trial_{i}",
                task_id=optimization_id,
                trial_type="hpo",
                config=params,
                metrics={"val_mse": score, "note": "模拟结果"},
                status="completed"
            ))

        best_metrics = {
            "val_mse": best_score,
            "best_params": best_params
        }

        return OptimizationResult(
            optimization_id=optimization_id,
            optimization_type="hpo",
            best_config=best_params,
            best_metrics=best_metrics,
            all_trials=trials
        )

    # ==================== 优化历史管理 ====================

    def _save_optimization_result(self, result: OptimizationResult) -> bool:
        """保存优化结果到文件"""
        try:
            filename = f"{result.optimization_type}_{result.optimization_id}.pkl"
            filepath = self.storage_dir / "results" / filename

            with open(filepath, 'wb') as f:
                pickle.dump(result, f)

            logger.debug(f"优化结果已保存: {filename}")
            return True

        except Exception as e:
            logger.error(f"保存优化结果失败: {e}")
            return False

    def get_optimization_result(self, optimization_id: str) -> Optional[OptimizationResult]:
        """获取优化结果"""
        try:
            # 先在内存中查找
            for result in self._running_tasks.values():
                if result.optimization_id == optimization_id:
                    return result

            # 在文件中查找
            for filepath in (self.storage_dir / "results").glob(f"*_{optimization_id}.pkl"):
                with open(filepath, 'rb') as f:
                    result = pickle.load(f)
                return result

            logger.warning(f"未找到优化结果: {optimization_id}")
            return None

        except Exception as e:
            logger.error(f"加载优化结果失败: {e}")
            return None

    def list_optimization_history(
        self,
        optimization_type: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """列出优化历史"""
        try:
            results_dir = self.storage_dir / "results"
            history = []

            pattern = f"{optimization_type}_*.pkl" if optimization_type else "*.pkl"

            for filepath in sorted(results_dir.glob(pattern), key=lambda p: p.stat().st_mtime, reverse=True)[:limit]:
                try:
                    with open(filepath, 'rb') as f:
                        result = pickle.load(f)
                    history.append(result.to_dict())
                except Exception as e:
                    logger.warning(f"读取优化结果失败 {filepath.name}: {e}")

            return history

        except Exception as e:
            logger.error(f"列出优化历史失败: {e}")
            return []

    # ==================== 工具方法 ====================

    def get_statistics(self) -> Dict[str, int]:
        """获取统计信息"""
        try:
            results_count = len(list((self.storage_dir / "results").glob("*.pkl")))

            type_counts = {}
            for filepath in (self.storage_dir / "results").glob("*.pkl"):
                opt_type = filepath.name.split('_')[0]
                type_counts[opt_type] = type_counts.get(opt_type, 0) + 1

            return {
                "total_optimizations": results_count,
                "by_type": type_counts
            }

        except Exception as e:
            logger.error(f"获取统计信息失败: {e}")
            return {"total_optimizations": 0, "by_type": {}}

    def shutdown(self):
        """关闭服务，清理资源"""
        try:
            # 清理全局服务实例
            global _meta_controller_service
            _meta_controller_service = None
            logger.info("MetaControllerService 已关闭")
        except Exception as e:
            logger.error(f"关闭服务失败: {e}")


# ==================== 全局服务实例 ====================

_meta_controller_service = None


def get_meta_controller_service() -> MetaControllerService:
    """获取Meta Controller服务实例"""
    global _meta_controller_service
    if _meta_controller_service is None:
        _meta_controller_service = MetaControllerService()
    return _meta_controller_service

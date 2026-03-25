"""
超参数优化器

提供多种超参数优化方法，支持网格搜索、随机搜索和贝叶斯优化
"""

import logging
import numpy as np
from typing import Dict, List, Optional, Any, Callable
from abc import ABC, abstractmethod

try:
    from sklearn.model_selection import GridSearchCV, RandomizedSearchCV
    from sklearn.model_selection import cross_val_score
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

try:
    import optuna
    OPTUNA_AVAILABLE = True
except ImportError:
    OPTUNA_AVAILABLE = False


class HyperparameterOptimizer(ABC):
    """
    超参数优化器基类

    提供统一的超参数优化接口，支持多种优化策略
    """

    def __init__(self, model_type: str = "lightgbm", **kwargs):
        """
        初始化优化器

        Parameters
        ----------
        model_type : str
            模型类型，支持 'lightgbm', 'neural_network'
        **kwargs : dict
            其他优化参数
        """
        self.model_type = model_type
        self.logger = logging.getLogger(__name__)
        self.best_params = {}
        self.best_score = float('inf')

        # 优化配置
        self.config = {
            'n_trials': 100,
            'timeout': 600,
            'random_state': 42,
            'direction': 'minimize',
            **kwargs
        }

        # 检查依赖
        self._check_dependencies()

        self.logger.info(f"初始化{model_type}超参数优化器")

    def _check_dependencies(self):
        """检查必要的依赖"""
        if not SKLEARN_AVAILABLE and not OPTUNA_AVAILABLE:
            self.logger.warning("scikit-learn和optuna未安装，优化功能受限")

    @abstractmethod
    def optimize(self, X, y, model_trainer, **kwargs):
        """
        优化超参数

        Parameters
        ----------
        X : array-like
            特征数据
        y : array-like
            目标变量
        model_trainer : ModelTrainer
            模型训练器
        **kwargs : dict
            其他优化参数

        Returns
        -------
        Dict[str, Any]
            优化结果
        """
        pass


class GridSearchOptimizer(HyperparameterOptimizer):
    """网格搜索优化器"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.search_space = {}

    def define_search_space(self, model_type: str) -> Dict[str, List]:
        """定义搜索空间"""
        if model_type == "lightgbm":
            return {
                'num_leaves': [31, 50, 100],
                'learning_rate': [0.01, 0.05, 0.1],
                'feature_fraction': [0.8, 0.9, 1.0],
                'bagging_fraction': [0.7, 0.8, 0.9],
                'bagging_freq': [1, 5, 10],
                'min_data_in_leaf': [10, 20, 50]
            }
        elif model_type == "neural_network":
            return {
                'hidden_layers': [[64], [128], [64, 128]],
                'dropout': [0.1, 0.2, 0.3],
                'learning_rate': [0.001, 0.01, 0.1],
                'batch_size': [32, 64, 128]
            }
        else:
            return {}

    def optimize(self, X, y, model_trainer, **kwargs):
        """执行网格搜索优化"""
        if not SKLEARN_AVAILABLE:
            self.logger.error("scikit-learn未安装，无法执行网格搜索")
            return {}

        # 定义搜索空间
        param_grid = self.define_search_space(self.model_type)

        # 创建网格搜索对象
        grid_search = GridSearchCV(
            estimator=model_trainer,
            param_grid=param_grid,
            cv=3,
            scoring='neg_mean_squared_error',
            n_jobs=-1,
            verbose=1
        )

        # 执行搜索
        grid_search.fit(X, y)

        # 记录最佳参数
        self.best_params = grid_search.best_params_
        self.best_score = -grid_search.best_score_

        self.logger.info(f"网格搜索完成，最佳分数: {self.best_score:.6f}")

        return {
            'best_params': self.best_params,
            'best_score': self.best_score,
            'cv_results': grid_search.cv_results_
        }


class RandomSearchOptimizer(HyperparameterOptimizer):
    """随机搜索优化器"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.search_space = {}

    def define_search_space(self, model_type: str) -> Dict[str, Any]:
        """定义搜索空间"""
        if model_type == "lightgbm":
            return {
                'num_leaves': (10, 200),
                'learning_rate': (0.001, 0.2),
                'feature_fraction': (0.6, 1.0),
                'bagging_fraction': (0.5, 1.0),
                'bagging_freq': (1, 20),
                'min_data_in_leaf': (5, 100)
            }
        elif model_type == "neural_network":
            return {
                'hidden_layers': [(32, 256), (64, 128)],
                'dropout': (0.05, 0.5),
                'learning_rate': (0.0001, 0.1),
                'batch_size': (16, 256)
            }
        else:
            return {}

    def optimize(self, X, y, model_trainer, **kwargs):
        """执行随机搜索优化"""
        if not SKLEARN_AVAILABLE:
            self.logger.error("scikit-learn未安装，无法执行随机搜索")
            return {}

        # 定义搜索空间
        param_distributions = self.define_search_space(self.model_type)

        # 创建随机搜索对象
        random_search = RandomizedSearchCV(
            estimator=model_trainer,
            param_distributions=param_distributions,
            n_iter=self.config['n_trials'],
            cv=3,
            scoring='neg_mean_squared_error',
            n_jobs=-1,
            random_state=self.config['random_state'],
            verbose=1
        )

        # 执行搜索
        random_search.fit(X, y)

        # 记录最佳参数
        self.best_params = random_search.best_params_
        self.best_score = -random_search.best_score_

        self.logger.info(f"随机搜索完成，最佳分数: {self.best_score:.6f}")

        return {
            'best_params': self.best_params,
            'best_score': self.best_score,
            'cv_results': random_search.cv_results_
        }


class BayesianOptimizer(HyperparameterOptimizer):
    """贝叶斯优化器"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.study = None

    def define_search_space(self, model_type: str, trial):
        """定义搜索空间"""
        if model_type == "lightgbm":
            trial.suggest_int('num_leaves', 10, 200)
            trial.suggest_loguniform('learning_rate', 0.001, 0.2)
            trial.suggest_uniform('feature_fraction', 0.6, 1.0)
            trial.suggest_uniform('bagging_fraction', 0.5, 1.0)
            trial.suggest_int('bagging_freq', 1, 20)
            trial.suggest_int('min_data_in_leaf', 5, 100)
        elif model_type == "neural_network":
            n_layers = trial.suggest_int('n_layers', 1, 4)
            hidden_dims = []
            for i in range(n_layers):
                hidden_dims.append(
                    trial.suggest_int(
                        f'hidden_dim_{i}', 32, 256))

            trial.suggest_uniform('dropout', 0.05, 0.5)
            trial.suggest_loguniform('learning_rate', 0.0001, 0.1)
            trial.suggest_categorical('batch_size', [16, 32, 64, 128])
        else:
            raise ValueError(f"不支持的模型类型: {model_type}")

    def objective_function(self, X, y, model_trainer):
        """目标函数"""
        def objective(trial):
            # 获取超参数
            params = {}
            if self.model_type == "lightgbm":
                params = {
                    'num_leaves': trial.suggest_int(
                        'num_leaves', 10, 200), 'learning_rate': trial.suggest_loguniform(
                        'learning_rate', 0.001, 0.2), 'feature_fraction': trial.suggest_uniform(
                        'feature_fraction', 0.6, 1.0), 'bagging_fraction': trial.suggest_uniform(
                        'bagging_fraction', 0.5, 1.0), 'bagging_freq': trial.suggest_int(
                        'bagging_freq', 1, 20), 'min_data_in_leaf': trial.suggest_int(
                            'min_data_in_leaf', 5, 100)}
            elif self.model_type == "neural_network":
                n_layers = trial.suggest_int('n_layers', 1, 4)
                params = {
                    'hidden_layers': n_layers, 'dropout': trial.suggest_uniform(
                        'dropout', 0.05, 0.5), 'learning_rate': trial.suggest_loguniform(
                        'learning_rate', 0.0001, 0.1), 'batch_size': trial.suggest_categorical(
                        'batch_size', [
                            16, 32, 64, 128])}
            else:
                raise ValueError(f"不支持的模型类型: {self.model_type}")

            # 训练模型并验证
            cv_scores = cross_val_score(model_trainer, X, y, cv=3,
                                        scoring='neg_mean_squared_error')
            mean_score = np.mean(cv_scores)

            return mean_score

        return objective

    def optimize(self, X, y, model_trainer, **kwargs):
        """执行贝叶斯优化"""
        if not OPTUNA_AVAILABLE:
            self.logger.error("optuna未安装，无法执行贝叶斯优化")
            return {}

        # 创建研究
        self.study = optuna.create_study(
            direction=self.config['direction'],
            sampler=optuna.samplers.TPESampler()
        )

        # 定义目标函数
        objective = self.objective_function(X, y, model_trainer)

        # 执行优化
        self.study.optimize(
            objective,
            n_trials=self.config['n_trials'],
            timeout=self.config['timeout']
        )

        # 记录最佳参数
        self.best_params = self.study.best_params
        self.best_score = self.study.best_value

        self.logger.info(f"贝叶斯优化完成，最佳分数: {self.best_score:.6f}")

        return {
            'best_params': self.best_params,
            'best_score': self.best_score,
            'study': self.study
        }

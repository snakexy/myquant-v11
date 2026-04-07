"""
模型训练器

提供完整的模型训练功能，支持多种训练策略和优化方法
"""

import os
import time
import logging
import pickle
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any, Callable, Tuple, Union
from abc import ABC, abstractmethod

try:
    import torch
    import torch.nn as nn
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

try:
    import lightgbm as lgb
    LGB_AVAILABLE = True
except ImportError:
    LGB_AVAILABLE = False

try:
    from sklearn.model_selection import GridSearchCV, RandomizedSearchCV
    from sklearn.metrics import mean_squared_error, mean_absolute_error
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False


class ModelTrainer(ABC):
    """
    模型训练器基类

    提供统一的训练接口，支持多种模型类型和训练策略
    """

    def __init__(self, model_type: str = "lightgbm", **kwargs):
        """
        初始化训练器

        Parameters
        ----------
        model_type : str
            模型类型，支持 'lightgbm', 'neural_network'
        **kwargs : dict
            其他训练参数
        """
        self.model_type = model_type
        self.logger = logging.getLogger(__name__)
        self.model = None
        self.training_history = []
        self.best_model = None
        self.best_score = float('inf')

        # 训练配置
        self.config = {
            'early_stopping_patience': 10,
            'early_stopping_min_delta': 0.001,
            'validation_split': 0.2,
            'random_state': 42,
            'verbose': True,
            **kwargs
        }

        # 检查依赖
        self._check_dependencies()

        self.logger.info(f"初始化{model_type}模型训练器")

    def _check_dependencies(self):
        """检查必要的依赖"""
        if self.model_type == "lightgbm" and not LGB_AVAILABLE:
            raise ImportError("LightGBM未安装，无法训练LightGBM模型")

        if self.model_type == "neural_network" and not TORCH_AVAILABLE:
            raise ImportError("PyTorch未安装，无法训练神经网络模型")

    def prepare_data(self,
                     X: Union[pd.DataFrame, np.ndarray],
                     y: Union[pd.Series, np.ndarray],
                     validation_split: float = 0.2) -> Tuple:
        """
        准备训练数据

        Parameters
        ----------
        X : pd.DataFrame or np.ndarray
            特征数据
        y : pd.Series or np.ndarray
            目标变量
        validation_split : float
            验证集比例

        Returns
        -------
        Tuple
            (X_train, X_val, y_train, y_val)
        """
        # 转换数据格式
        if isinstance(X, pd.DataFrame):
            X = X.values
        if isinstance(y, pd.Series):
            y = y.values

        # 分割数据
        n_samples = len(X)
        val_size = int(n_samples * validation_split)

        indices = np.random.permutation(n_samples)
        train_indices = indices[val_size:]
        val_indices = indices[:val_size]

        X_train = X[train_indices]
        X_val = X[val_indices]
        y_train = y[train_indices]
        y_val = y[val_indices]

        self.logger.info(f"训练集大小: {len(X_train)}, 验证集大小: {len(X_val)}")

        return X_train, X_val, y_train, y_val

    def train(self,
              X: Union[pd.DataFrame, np.ndarray],
              y: Union[pd.Series, np.ndarray],
              **kwargs) -> Dict[str, Any]:
        """
        训练模型

        Parameters
        ----------
        X : pd.DataFrame or np.ndarray
            特征数据
        y : pd.Series or np.ndarray
            目标变量
        **kwargs : dict
            训练参数

        Returns
        -------
        Dict[str, Any]
            训练结果
        """
        start_time = time.time()

        # 准备数据
        X_train, X_val, y_train, y_val = self.prepare_data(X, y)

        # 根据模型类型选择训练方法
        if self.model_type == "lightgbm":
            result = self._train_lightgbm(
                X_train, y_train, X_val, y_val, **kwargs)
        elif self.model_type == "neural_network":
            result = self._train_neural_network(
                X_train, y_train, X_val, y_val, **kwargs)
        else:
            raise ValueError(f"不支持的模型类型: {self.model_type}")

        # 记录训练历史
        training_time = time.time() - start_time
        result['training_time'] = training_time

        self.training_history.append(result)

        # 更新最佳模型
        if result['val_score'] < self.best_score:
            self.best_score = result['val_score']
            self.best_model = result['model']

        self.logger.info(f"训练完成，验证分数: {result['val_score']:.6f}, "
                         f"训练时间: {training_time:.2f}s")

        return result

    def _train_lightgbm(self, X_train, y_train, X_val, y_val, **kwargs):
        """训练LightGBM模型"""
        if not LGB_AVAILABLE:
            raise ImportError("LightGBM未安装")

        # 合并配置
        config = self.config.copy()
        config.update(kwargs)

        # 创建数据集
        train_data = lgb.Dataset(X_train, label=y_train)
        val_data = lgb.Dataset(X_val, label=y_val)

        # 训练参数
        train_params = {
            'objective': 'regression',
            'metric': 'rmse',
            'boosting_type': 'gbdt',
            'num_leaves': 31,
            'learning_rate': 0.05,
            'feature_fraction': 0.9,
            'bagging_fraction': 0.8,
            'bagging_freq': 5,
            'min_data_in_leaf': 20,
            'verbosity': -1,
            'random_state': config['random_state']
        }
        train_params.update({k: v for k, v in kwargs.items() if k in [
                            'num_leaves', 'learning_rate', 'feature_fraction']})

        # 早停回调
        callbacks = [
            lgb.early_stopping(
                stopping_rounds=config['early_stopping_patience'],
                verbose=config['verbose']
            )
        ]

        # 训练模型
        model = lgb.train(
            train_params,
            train_data,
            valid_sets=[val_data],
            num_boost_round=1000,
            callbacks=callbacks,
            verbose_eval=config['verbose']
        )

        # 验证模型
        y_pred = model.predict(X_val)
        val_score = np.sqrt(mean_squared_error(y_val, y_pred))

        return {
            'model': model,
            'val_score': val_score,
            'train_params': train_params,
            'feature_importance': model.feature_importance()
        }

    def _train_neural_network(self, X_train, y_train, X_val, y_val, **kwargs):
        """训练神经网络模型"""
        if not TORCH_AVAILABLE:
            raise ImportError("PyTorch未安装")

        # 合并配置
        config = self.config.copy()
        config.update(kwargs)

        # 转换数据为PyTorch张量
        X_train_tensor = torch.FloatTensor(X_train)
        y_train_tensor = torch.FloatTensor(y_train).unsqueeze(1)
        X_val_tensor = torch.FloatTensor(X_val)
        y_val_tensor = torch.FloatTensor(y_val).unsqueeze(1)

        # 定义模型结构
        input_dim = X_train.shape[1]
        model = nn.Sequential(
            nn.Linear(input_dim, 128),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(32, 1)
        )

        # 定义优化器和损失函数
        optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
        criterion = nn.MSELoss()

        # 训练模型
        model.train()
        best_val_loss = float('inf')
        patience_counter = 0

        for epoch in range(1000):
            # 前向传播
            outputs = model(X_train_tensor)
            loss = criterion(outputs, y_train_tensor)

            # 反向传播和优化
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            # 验证
            model.eval()
            with torch.no_grad():
                val_outputs = model(X_val_tensor)
                val_loss = criterion(val_outputs, y_val_tensor).item()

            model.train()

            # 早停检查
            if val_loss < best_val_loss - config['early_stopping_min_delta']:
                best_val_loss = val_loss
                patience_counter = 0
                # 保存最佳模型
                best_model_state = model.state_dict()
            else:
                patience_counter += 1

            if patience_counter >= config['early_stopping_patience']:
                self.logger.info(f"早停于第{epoch}轮，最佳验证损失: {best_val_loss:.6f}")
                break

            if epoch % 100 == 0 and config['verbose']:
                self.logger.info(f"Epoch {epoch}, 训练损失: {loss.item():.6f}, "
                                 f"验证损失: {val_loss:.6f}")

        # 加载最佳模型
        model.load_state_dict(best_model_state)
        model.eval()

        return {
            'model': model,
            'val_score': np.sqrt(best_val_loss),
            'train_params': config,
            'training_epochs': epoch
        }

    def save_model(self, model_path: str) -> bool:
        """
        保存模型

        Parameters
        ----------
        model_path : str
            模型保存路径

        Returns
        -------
        bool
            是否保存成功
        """
        try:
            if self.best_model is None:
                self.logger.warning("没有可保存的模型")
                return False

            # 确保目录存在
            os.makedirs(os.path.dirname(model_path), exist_ok=True)

            # 根据模型类型选择保存方法
            if self.model_type == "lightgbm":
                self.best_model.save_model(model_path)
            elif self.model_type == "neural_network":
                torch.save(self.best_model.state_dict(), model_path)
            else:
                self.logger.error(f"不支持的模型类型: {self.model_type}")
                return False

            self.logger.info(f"模型已保存到: {model_path}")
            return True

        except Exception as e:
            self.logger.error(f"保存模型失败: {e}")
            return False

    def load_model(self, model_path: str) -> bool:
        """
        加载模型

        Parameters
        ----------
        model_path : str
            模型文件路径

        Returns
        -------
        bool
            是否加载成功
        """
        try:
            if not os.path.exists(model_path):
                self.logger.error(f"模型文件不存在: {model_path}")
                return False

            # 根据模型类型选择加载方法
            if self.model_type == "lightgbm":
                self.model = lgb.Booster(model_file=model_path)
            elif self.model_type == "neural_network":
                # 需要先创建模型结构
                input_dim = self._get_input_dim_from_model_path(model_path)
                self.model = self._create_neural_network_model(input_dim)
                self.model.load_state_dict(torch.load(model_path))
                self.model.eval()
            else:
                self.logger.error(f"不支持的模型类型: {self.model_type}")
                return False

            self.logger.info(f"模型已从{model_path}加载")
            return True

        except Exception as e:
            self.logger.error(f"加载模型失败: {e}")
            return False

    def _get_input_dim_from_model_path(self, model_path: str) -> int:
        """从模型路径推断输入维度"""
        # 这里简化处理，实际应用中可以从配置文件或元数据获取
        return 128  # 默认值

    def _create_neural_network_model(self, input_dim: int):
        """创建神经网络模型结构"""
        return nn.Sequential(
            nn.Linear(input_dim, 128),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(32, 1)
        )

    def predict(self, X: Union[pd.DataFrame, np.ndarray]) -> np.ndarray:
        """
        模型预测

        Parameters
        ----------
        X : pd.DataFrame or np.ndarray
            特征数据

        Returns
        -------
        np.ndarray
            预测结果
        """
        if self.model is None:
            raise ValueError("模型尚未训练或加载")

        # 转换数据格式
        if isinstance(X, pd.DataFrame):
            X = X.values

        # 根据模型类型选择预测方法
        if self.model_type == "lightgbm":
            return self.model.predict(X)
        elif self.model_type == "neural_network":
            X_tensor = torch.FloatTensor(X)
            with torch.no_grad():
                outputs = self.model(X_tensor)
                return outputs.numpy().flatten()
        else:
            raise ValueError(f"不支持的模型类型: {self.model_type}")

    def get_training_history(self) -> List[Dict[str, Any]]:
        """获取训练历史"""
        return self.training_history.copy()

    def get_best_model_info(self) -> Dict[str, Any]:
        """获取最佳模型信息"""
        return {
            'best_score': self.best_score,
            'model_type': self.model_type,
            'model': self.best_model
        }

    @abstractmethod
    def evaluate(self, X_test, y_test) -> Dict[str, float]:
        """
        评估模型

        Parameters
        ----------
        X_test : pd.DataFrame or np.ndarray
            测试特征数据
        y_test : pd.Series or np.ndarray
            测试目标变量

        Returns
        -------
        Dict[str, float]
            评估指标
        """
        pass


class LightGBMTrainer(ModelTrainer):
    """LightGBM专用训练器"""

    def __init__(self, **kwargs):
        super().__init__(model_type="lightgbm", **kwargs)

    def evaluate(self, X_test, y_test) -> Dict[str, float]:
        """评估LightGBM模型"""
        if self.model is None:
            raise ValueError("模型尚未训练或加载")

        # 转换数据格式
        if isinstance(X_test, pd.DataFrame):
            X_test = X_test.values
        if isinstance(y_test, pd.Series):
            y_test = y_test.values

        # 预测
        y_pred = self.model.predict(X_test)

        # 计算评估指标
        mse = mean_squared_error(y_test, y_pred)
        mae = mean_absolute_error(y_test, y_pred)
        rmse = np.sqrt(mse)

        # 计算R²
        ss_res = np.sum((y_test - y_pred) ** 2)
        ss_tot = np.sum((y_test - np.mean(y_test)) ** 2)
        r2 = 1 - (ss_res / ss_tot)

        return {
            'mse': mse,
            'mae': mae,
            'rmse': rmse,
            'r2': r2
        }


def create_model_trainer(model_type: str = "lightgbm", **kwargs):
    """
    创建模型训练器实例
    
    Parameters
    ----------
    model_type : str
        模型类型，支持 'lightgbm', 'neural_network'
    **kwargs : dict
        其他训练参数
        
    Returns
    -------
    ModelTrainer
        模型训练器实例
    """
    if model_type == "lightgbm":
        return LightGBMTrainer(**kwargs)
    elif model_type == "neural_network":
        return NeuralNetworkTrainer(**kwargs)
    else:
        raise ValueError(f"不支持的模型类型: {model_type}")


def get_model_trainer(model_type: str = "lightgbm", **kwargs):
    """
    获取模型训练器实例（别名函数）
    
    Parameters
    ----------
    model_type : str
        模型类型，支持 'lightgbm', 'neural_network'
    **kwargs : dict
        其他训练参数
        
    Returns
    -------
    ModelTrainer
        模型训练器实例
    """
    return create_model_trainer(model_type, **kwargs)


class NeuralNetworkTrainer(ModelTrainer):
    """神经网络专用训练器"""

    def __init__(self, **kwargs):
        super().__init__(model_type="neural_network", **kwargs)

    def evaluate(self, X_test, y_test) -> Dict[str, float]:
        """评估神经网络模型"""
        if self.model is None:
            raise ValueError("模型尚未训练或加载")

        # 转换数据格式
        if isinstance(X_test, pd.DataFrame):
            X_test = X_test.values
        if isinstance(y_test, pd.Series):
            y_test = y_test.values

        # 预测
        y_pred = self.predict(X_test)

        # 计算评估指标
        mse = mean_squared_error(y_test, y_pred)
        mae = mean_absolute_error(y_test, y_pred)
        rmse = np.sqrt(mse)

        # 计算R²
        ss_res = np.sum((y_test - y_pred) ** 2)
        ss_tot = np.sum((y_test - np.mean(y_test)) ** 2)
        r2 = 1 - (ss_res / ss_tot)

        return {
            'mse': mse,
            'mae': mae,
            'rmse': rmse,
            'r2': r2
        }

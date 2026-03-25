"""
早停机制

提供灵活的早停策略，防止模型过拟合并优化训练过程
"""

import logging
import numpy as np
from typing import Dict, Optional, Any, Callable
from abc import ABC, abstractmethod


class EarlyStopping(ABC):
    """
    早停机制基类

    提供统一的早停接口，支持多种早停策略
    """

    def __init__(self,
                 patience: int = 10,
                 min_delta: float = 0.0,
                 restore_best_weights: bool = True,
                 verbose: bool = True):
        """
        初始化早停机制

        Parameters
        ----------
        patience : int
            容忍轮数，超过此轮数无改善则停止
        min_delta : float
            最小改善阈值
        restore_best_weights : bool
            是否恢复最佳权重
        verbose : bool
            是否打印日志
        """
        self.patience = patience
        self.min_delta = min_delta
        self.restore_best_weights = restore_best_weights
        self.verbose = verbose

        self.logger = logging.getLogger(__name__)

        # 内部状态
        self.best_score = None
        self.counter = 0
        self.best_weights = None
        self.early_stop = False
        self.scores_history = []

        self.logger.info(
            f"初始化早停机制: patience={patience}, min_delta={min_delta}")

    def __call__(self, score: float, model: Optional[Any] = None) -> bool:
        """
        检查是否应该早停

        Parameters
        ----------
        score : float
            当前评分
        model : Any, optional
            模型对象，用于保存最佳权重

        Returns
        -------
        bool
            是否应该早停
        """
        self.scores_history.append(score)

        if self.best_score is None:
            self.best_score = score
            self._save_best_weights(model)
            return False

        if self._is_improvement(score):
            self.best_score = score
            self.counter = 0
            self._save_best_weights(model)

            if self.verbose:
                self.logger.info(
                    f"评分改善: {score:.6f} (最佳: {self.best_score:.6f})")
        else:
            self.counter += 1

            if self.verbose:
                self.logger.info(
                    f"评分未改善: {score:.6f} (最佳: {self.best_score:.6f}), 计数: {self.counter}/{self.patience}")

        if self.counter >= self.patience:
            self.early_stop = True

            if self.verbose:
                self.logger.info(f"触发早停! 最佳评分: {self.best_score:.6f}")

            if self.restore_best_weights and model is not None:
                self._restore_best_weights(model)

            return True

        return False

    @abstractmethod
    def _is_improvement(self, score: float) -> bool:
        """
        判断是否有改善

        Parameters
        ----------
        score : float
            当前评分

        Returns
        -------
        bool
            是否有改善
        """
        pass

    def _save_best_weights(self, model: Optional[Any] = None):
        """保存最佳权重"""
        if model is not None:
            try:
                # 尝试不同的模型权重保存方式
                if hasattr(model, 'state_dict'):
                    # PyTorch模型
                    self.best_weights = {k: v.cpu().numpy()
                                         for k, v in model.state_dict().items()}
                elif hasattr(model, 'get_weights'):
                    # Keras模型
                    self.best_weights = model.get_weights()
                elif hasattr(model, 'coef_'):
                    # scikit-learn模型
                    self.best_weights = {
                        'coef_': model.coef_,
                        'intercept_': model.intercept_
                    }
                else:
                    self.logger.warning("无法保存模型权重: 不支持的模型类型")
            except Exception as e:
                self.logger.error(f"保存模型权重失败: {e}")

    def _restore_best_weights(self, model: Any):
        """恢复最佳权重"""
        if self.best_weights is None:
            self.logger.warning("没有可恢复的最佳权重")
            return

        try:
            # 尝试不同的模型权重恢复方式
            if hasattr(
                    model,
                    'load_state_dict') and hasattr(
                    model,
                    'state_dict'):
                # PyTorch模型
                import torch
                state_dict = {
                    k: torch.tensor(v) for k,
                    v in self.best_weights.items()}
                model.load_state_dict(state_dict)
            elif hasattr(model, 'set_weights'):
                # Keras模型
                model.set_weights(self.best_weights)
            elif hasattr(model, 'coef_'):
                # scikit-learn模型
                model.coef_ = self.best_weights['coef_']
                model.intercept_ = self.best_weights['intercept_']
            else:
                self.logger.warning("无法恢复模型权重: 不支持的模型类型")

            if self.verbose:
                self.logger.info("已恢复最佳权重")

        except Exception as e:
            self.logger.error(f"恢复模型权重失败: {e}")

    def reset(self):
        """重置早停状态"""
        self.best_score = None
        self.counter = 0
        self.best_weights = None
        self.early_stop = False
        self.scores_history = []

        if self.verbose:
            self.logger.info("早停机制已重置")

    def get_best_score(self) -> Optional[float]:
        """获取最佳评分"""
        return self.best_score

    def get_scores_history(self) -> list:
        """获取评分历史"""
        return self.scores_history.copy()


class MinEarlyStopping(EarlyStopping):
    """最小化目标早停机制"""

    def _is_improvement(self, score: float) -> bool:
        """判断是否有改善（分数越小越好）"""
        return score < self.best_score - self.min_delta


class MaxEarlyStopping(EarlyStopping):
    """最大化目标早停机制"""

    def _is_improvement(self, score: float) -> bool:
        """判断是否有改善（分数越大越好）"""
        return score > self.best_score + self.min_delta


class EarlyStoppingFactory:
    """早停机制工厂类"""

    @staticmethod
    def create_early_stopping(mode: str = 'min',
                              patience: int = 10,
                              min_delta: float = 0.0,
                              restore_best_weights: bool = True,
                              verbose: bool = True,
                              **kwargs) -> EarlyStopping:
        """
        创建早停机制

        Parameters
        ----------
        mode : str
            早停模式，'min' 或 'max'
        patience : int
            容忍轮数
        min_delta : float
            最小改善阈值
        restore_best_weights : bool
            是否恢复最佳权重
        verbose : bool
            是否打印日志
        **kwargs : dict
            其他参数

        Returns
        -------
        EarlyStopping
            早停机制实例
        """
        if mode.lower() == 'min':
            return MinEarlyStopping(
                patience=patience,
                min_delta=min_delta,
                restore_best_weights=restore_best_weights,
                verbose=verbose
            )
        elif mode.lower() == 'max':
            return MaxEarlyStopping(
                patience=patience,
                min_delta=min_delta,
                restore_best_weights=restore_best_weights,
                verbose=verbose
            )
        else:
            raise ValueError(f"不支持的早停模式: {mode}")


class EarlyStoppingCallback:
    """早停回调类，用于训练过程中的集成"""

    def __init__(self,
                 early_stopping: EarlyStopping,
                 monitor: str = 'val_loss',
                 mode: str = 'min'):
        """
        初始化早停回调

        Parameters
        ----------
        early_stopping : EarlyStopping
            早停机制实例
        monitor : str
            监控指标名称
        mode : str
            监控模式，'min' 或 'max'
        """
        self.early_stopping = early_stopping
        self.monitor = monitor
        self.mode = mode
        self.logger = logging.getLogger(__name__)

    def on_epoch_end(self,
                     epoch: int,
                     logs: Dict[str,
                                float],
                     model: Optional[Any] = None) -> bool:
        """
        训练轮次结束时的回调

        Parameters
        ----------
        epoch : int
            当前轮次
        logs : Dict[str, float]
            训练日志
        model : Any, optional
            模型对象

        Returns
        -------
        bool
            是否应该停止训练
        """
        if self.monitor not in logs:
            self.logger.warning(f"监控指标 '{self.monitor}' 不在日志中")
            return False

        current_score = logs[self.monitor]

        if self.early_stopping(current_score, model):
            self.logger.info(f"早停触发于轮次 {epoch}")
            return True

        return False

    def on_train_begin(self):
        """训练开始时的回调"""
        self.early_stopping.reset()
        self.logger.info("早停回调已重置")

    def on_train_end(self):
        """训练结束时的回调"""
        best_score = self.early_stopping.get_best_score()
        if best_score is not None:
            self.logger.info(f"训练完成，最佳{self.monitor}: {best_score:.6f}")

"""
模型评估器

提供全面的模型评估功能，包括多种评估指标和可视化功能
"""

import logging
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Optional, Any, Union
from abc import ABC, abstractmethod

try:
    from sklearn.metrics import (
        mean_squared_error, mean_absolute_error, r2_score,
        accuracy_score, precision_score, recall_score, f1_score,
        confusion_matrix, classification_report, roc_curve, auc
    )
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False


class ModelEvaluator(ABC):
    """
    模型评估器基类

    提供统一的评估接口，支持多种评估指标和可视化功能
    """

    def __init__(self, task_type: str = "regression"):
        """
        初始化评估器

        Parameters
        ----------
        task_type : str
            任务类型，支持 'regression', 'classification'
        """
        self.task_type = task_type
        self.logger = logging.getLogger(__name__)
        self.evaluation_results = {}

        self.logger.info(f"初始化{task_type}任务评估器")

    def evaluate_regression(self, y_true, y_pred, **
                            kwargs) -> Dict[str, float]:
        """
        评估回归模型

        Parameters
        ----------
        y_true : array-like
            真实值
        y_pred : array-like
            预测值
        **kwargs : dict
            其他评估参数

        Returns
        -------
        Dict[str, float]
            评估指标
        """
        if not SKLEARN_AVAILABLE:
            self.logger.error("scikit-learn未安装，无法计算详细指标")
            return self._basic_regression_metrics(y_true, y_pred)

        # 计算回归指标
        mse = mean_squared_error(y_true, y_pred)
        mae = mean_absolute_error(y_true, y_pred)
        rmse = np.sqrt(mse)
        r2 = r2_score(y_true, y_pred)

        # 计算MAPE
        mape = np.mean(np.abs((y_true - y_pred) / (y_true + 1e-8))) * 100

        return {
            'mse': mse,
            'mae': mae,
            'rmse': rmse,
            'r2': r2,
            'mape': mape
        }

    def evaluate_classification(
            self, y_true, y_pred, **kwargs) -> Dict[str, float]:
        """
        评估分类模型

        Parameters
        ----------
        y_true : array-like
            真实标签
        y_pred : array-like
            预测标签
        **kwargs : dict
            其他评估参数

        Returns
        -------
        Dict[str, float]
            评估指标
        """
        if not SKLEARN_AVAILABLE:
            self.logger.error("scikit-learn未安装，无法计算详细指标")
            return self._basic_classification_metrics(y_true, y_pred)

        # 计算分类指标
        accuracy = accuracy_score(y_true, y_pred)
        precision = precision_score(y_true, y_pred, average='weighted')
        recall = recall_score(y_true, y_pred, average='weighted')
        f1 = f1_score(y_true, y_pred, average='weighted')

        # 混淆矩阵
        cm = confusion_matrix(y_true, y_pred)

        # 分类报告
        report = classification_report(y_true, y_pred, output_dict=True)

        return {
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1': f1,
            'confusion_matrix': cm,
            'classification_report': report
        }

    def _basic_regression_metrics(self, y_true, y_pred) -> Dict[str, float]:
        """基础回归指标计算"""
        mse = np.mean((y_true - y_pred) ** 2)
        mae = np.mean(np.abs(y_true - y_pred))
        rmse = np.sqrt(mse)

        # 计算R²
        ss_res = np.sum((y_true - y_pred) ** 2)
        ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
        r2 = 1 - (ss_res / ss_tot)

        return {
            'mse': mse,
            'mae': mae,
            'rmse': rmse,
            'r2': r2
        }

    def _basic_classification_metrics(self, y_true, y_pred) -> Dict[str, Any]:
        """基础分类指标计算"""
        # 简单的准确率计算
        accuracy = np.mean(y_true == y_pred)

        # 简单的精确率和召回率计算
        tp = np.sum((y_true == 1) & (y_pred == 1))
        fp = np.sum((y_true == 0) & (y_pred == 1))
        fn = np.sum((y_true == 1) & (y_pred == 0))
        tn = np.sum((y_true == 0) & (y_pred == 0))

        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = 2 * precision * recall / \
            (precision + recall) if (precision + recall) > 0 else 0

        return {
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1': f1
        }

    def plot_predictions(self, y_true, y_pred, title: str = "模型预测结果"):
        """
        绘制预测结果

        Parameters
        ----------
        y_true : array-like
            真实值
        y_pred : array-like
            预测值
        title : str
            图表标题
        """
        try:
            plt.figure(figsize=(10, 6))

            if self.task_type == "regression":
                plt.scatter(y_true, y_pred, alpha=0.6)
                plt.plot([y_true.min(), y_true.max()],
                         [y_true.min(), y_true.max()], 'r--', alpha=0.8)
                plt.xlabel('真实值')
                plt.ylabel('预测值')
                plt.title(title)
            elif self.task_type == "classification":
                cm = confusion_matrix(y_true, y_pred)
                sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
                plt.xlabel('预测标签')
                plt.ylabel('真实标签')
                plt.title(title)

            plt.tight_layout()
            plt.show()

        except Exception as e:
            self.logger.error(f"绘制预测结果失败: {e}")

    def generate_evaluation_report(self,
                                   y_true, y_pred,
                                   model_name: str = "模型",
                                   save_path: Optional[str] = None) -> str:
        """
        生成评估报告

        Parameters
        ----------
        y_true : array-like
            真实值
        y_pred : array-like
            预测值
        model_name : str
            模型名称
        save_path : str, optional
            报告保存路径

        Returns
        -------
        str
            评估报告
        """
        # 评估模型
        if self.task_type == "regression":
            metrics = self.evaluate_regression(y_true, y_pred)
        elif self.task_type == "classification":
            metrics = self.evaluate_classification(y_true, y_pred)
        else:
            raise ValueError(f"不支持的任务类型: {self.task_type}")

        # 生成报告
        report = f"""
# {model_name} 评估报告
========================================

## 评估指标
"""

        if self.task_type == "regression":
            report += f"""
- 均方误差 (MSE): {metrics['mse']:.6f}
- 平均绝对误差 (MAE): {metrics['mae']:.6f}
- 均方根误差 (RMSE): {metrics['rmse']:.6f}
- 决定系数 (R²): {metrics['r2']:.6f}
- 平均绝对百分比误差 (MAPE): {metrics['mape']:.2f}%
"""
        elif self.task_type == "classification":
            report += f"""
- 准确率: {metrics['accuracy']:.4f}
- 精确率: {metrics['precision']:.4f}
- 召回率: {metrics['recall']:.4f}
- F1分数: {metrics['f1']:.4f}

## 混淆矩阵
{metrics['confusion_matrix']}
"""

        report += """

## 结论
"""

        if self.task_type == "regression":
            if metrics['r2'] > 0.8:
                report += "模型表现优秀，具有很强的预测能力"
            elif metrics['r2'] > 0.6:
                report += "模型表现良好，具有较好的预测能力"
            elif metrics['r2'] > 0.4:
                report += "模型表现一般，预测能力有限"
            else:
                report += "模型表现较差，需要改进"
        elif self.task_type == "classification":
            if metrics['accuracy'] > 0.9:
                report += "模型表现优秀，具有很强的分类能力"
            elif metrics['accuracy'] > 0.8:
                report += "模型表现良好，具有较好的分类能力"
            elif metrics['accuracy'] > 0.7:
                report += "模型表现一般，分类能力有限"
            else:
                report += "模型表现较差，需要改进"

        report += "\n========================================\n"

        # 保存报告
        if save_path:
            try:
                with open(save_path, 'w', encoding='utf-8') as f:
                    f.write(report)
                self.logger.info(f"评估报告已保存到: {save_path}")
            except Exception as e:
                self.logger.error(f"保存评估报告失败: {e}")

        return report

    @abstractmethod
    def evaluate(self, y_true, y_pred, **kwargs) -> Dict[str, float]:
        """
        评估模型

        Parameters
        ----------
        y_true : array-like
            真实值
        y_pred : array-like
            预测值
        **kwargs : dict
            其他评估参数

        Returns
        -------
        Dict[str, float]
            评估指标
        """
        pass


class RegressionEvaluator(ModelEvaluator):
    """回归任务评估器"""

    def __init__(self, **kwargs):
        super().__init__(task_type="regression", **kwargs)

    def evaluate(self, y_true, y_pred, **kwargs) -> Dict[str, float]:
        """评估回归模型"""
        return super().evaluate_regression(y_true, y_pred, **kwargs)


class ClassificationEvaluator(ModelEvaluator):
    """分类任务评估器"""

    def __init__(self, **kwargs):
        super().__init__(task_type="classification", **kwargs)

    def evaluate(self, y_true, y_pred, **kwargs) -> Dict[str, float]:
        """评估分类模型"""
        return super().evaluate_classification(y_true, y_pred, **kwargs)


def create_model_evaluator(task_type: str = "regression", **kwargs):
    """
    创建模型评估器实例
    
    Parameters
    ----------
    task_type : str
        任务类型，支持 'regression', 'classification'
    **kwargs : dict
        其他评估参数
        
    Returns
    -------
    ModelEvaluator
        模型评估器实例
    """
    if task_type == "regression":
        return RegressionEvaluator(**kwargs)
    elif task_type == "classification":
        return ClassificationEvaluator(**kwargs)
    else:
        raise ValueError(f"不支持的任务类型: {task_type}")


def get_model_evaluator(task_type: str = "regression", **kwargs):
    """
    获取模型评估器实例（别名函数）
    
    Parameters
    ----------
    task_type : str
        任务类型，支持 'regression', 'classification'
    **kwargs : dict
        其他评估参数
        
    Returns
    -------
    ModelEvaluator
        模型评估器实例
    """
    return create_model_evaluator(task_type, **kwargs)

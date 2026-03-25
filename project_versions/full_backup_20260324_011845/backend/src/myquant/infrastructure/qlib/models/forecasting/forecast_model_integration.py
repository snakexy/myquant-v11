#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QLib预测模型集成（完整版）
基于QLib Forecast Model接口的完整预测模型实现
合并了forecast_model_integration.py和forecast_model_integration_fixed.py的最佳功能
"""

import logging
import numpy as np
import pandas as pd
from typing import Dict, Any, Optional, Union

# 尝试导入QLib
try:
    from qlib.data.dataset import Dataset
    from qlib.data.dataset.handler import DataHandlerLP
    from qlib.contrib.model.gbdt import LGBModel
    from qlib.contrib.model.linear import LinearModel
    from qlib.contrib.model.nn import MLPModel
    from qlib.model.base import Model
    QLIB_AVAILABLE = True
except ImportError:
    QLIB_AVAILABLE = False
    logging.warning("QLib不可用，将使用模拟模式")

    # 创建占位符类
    class Model:
        def __init__(self, **kwargs):
            pass

logger = logging.getLogger(__name__)


class QLibForecastModel(Model):
    """
    基于QLib的预测模型实现
    完全兼容QLib Forecast Model接口
    """

    def __init__(self, **kwargs):
        """
        初始化QLib预测模型

        Args:
            **kwargs: 模型参数
        """
        super().__init__(**kwargs)
        self.model = None
        self.model_type = kwargs.get('model_type', 'lgb')
        self.is_trained = False
        self.feature_cols = None
        self.label_col = kwargs.get('label_col', 'label')

        # 模型参数
        self.model_params = kwargs.get('model_params', {})

        # 初始化模型
        self._initialize_model()

        logger.info(f"初始化QLib预测模型: {self.model_type}")

    def _initialize_model(self):
        """初始化具体的模型实现"""
        if not QLIB_AVAILABLE:
            logger.warning("QLib不可用，使用模拟模式")
            self.model = None
            return

        try:
            if self.model_type.lower() == 'lgb':
                # LightGBM模型
                default_params = {
                    'loss': 'mse',
                    'learning_rate': 0.1,
                    'num_leaves': 31,
                    'feature_fraction': 0.9,
                    'bagging_fraction': 0.8,
                    'bagging_freq': 5,
                    'verbose': -1,
                }
                default_params.update(self.model_params)
                self.model = LGBModel(**default_params)

            elif self.model_type.lower() == 'linear':
                # 线性模型
                default_params = {
                    'loss': 'mse',
                    'alpha': 0.5,
                    'fit_intercept': True,
                }
                default_params.update(self.model_params)
                self.model = LinearModel(**default_params)

            elif self.model_type.lower() == 'mlp':
                # 神经网络模型
                default_params = {
                    'loss': 'mse',
                    'hidden_size': [64, 32],
                    'dropout': 0.2,
                    'learning_rate': 0.001,
                    'epochs': 100,
                    'batch_size': 32,
                }
                default_params.update(self.model_params)
                self.model = MLPModel(**default_params)

            else:
                raise ValueError(f"不支持的模型类型: {self.model_type}")

            logger.info(f"成功初始化{self.model_type}模型")

        except Exception as e:
            logger.error(f"模型初始化失败: {e}")
            self.model = None

    def fit(
        self,
        dataset: Dataset,
        reweighter: Optional[Any] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        训练模型

        Args:
            dataset: QLib数据集
            reweighter: 重新加权器
            **kwargs: 其他训练参数

        Returns:
            训练结果字典
        """
        if not QLIB_AVAILABLE or self.model is None:
            # 模拟训练
            logger.warning("使用模拟训练模式")
            self.is_trained = True
            return {
                'status': 'simulated',
                'train_loss': 0.1,
                'val_loss': 0.12,
            }

        try:
            # 准备训练数据
            df_train, df_valid = dataset.prepare(
                ["train", "valid"],
                col_set=["feature", "label"],
                data_key=DataHandlerLP.DK_L
            )

            # 获取特征和标签
            if isinstance(df_train, dict):
                # 处理字典格式的数据
                X_train = df_train.get("feature")
                y_train = df_train.get("label")
                X_valid = df_valid.get("feature")
                y_valid = df_valid.get("label")
            else:
                # 处理DataFrame格式的数据
                feature_cols = [
                    col for col in df_train.columns if col != self.label_col
                ]
                self.feature_cols = feature_cols

                X_train = df_train[feature_cols]
                y_train = df_train[self.label_col]

                if df_valid is not None:
                    X_valid = df_valid[feature_cols]
                    y_valid = df_valid[self.label_col]
                else:
                    X_valid = None
                    y_valid = None

            # 获取权重
            try:
                wdf_train, wdf_valid = dataset.prepare(
                    ["train", "valid"],
                    col_set=["weight"],
                    data_key=DataHandlerLP.DK_L
                )
                w_train = wdf_train["weight"]
            except KeyError:
                # 如果没有权重，使用全1权重
                w_train = pd.DataFrame(
                    np.ones_like(y_train.values),
                    index=y_train.index
                )

            # 训练模型
            if w_train is not None:
                self.model.fit(X_train, y_train, w_train)
            else:
                self.model.fit(X_train, y_train)

            # 评估模型
            train_pred = self.model.predict(X_train)
            train_metrics = self._calculate_metrics(y_train, train_pred)

            val_metrics = {}
            if X_valid is not None and y_valid is not None:
                val_pred = self.model.predict(X_valid)
                val_metrics = self._calculate_metrics(y_valid, val_pred)

            # 设置模型为已训练状态
            self.is_trained = True

            # 返回训练结果
            result = {
                'status': 'success',
                'train_metrics': train_metrics,
                'validation_metrics': val_metrics,
                'feature_importance': self.get_feature_importance(),
            }

            logger.info(f"模型训练完成: {self.model_type}")
            return result

        except Exception as e:
            logger.error(f"模型训练失败: {e}")
            raise

    def predict(
        self,
        dataset: Dataset,
        segment: str = "test",
        **kwargs
    ) -> Union[pd.Series, np.ndarray]:
        """
        预测

        Args:
            dataset: QLib数据集
            segment: 数据段 (train/valid/test)
            **kwargs: 其他预测参数

        Returns:
            预测结果
        """
        if not self.is_trained:
            raise ValueError("模型尚未训练，无法预测")

        if not QLIB_AVAILABLE or self.model is None:
            # 模拟预测
            logger.warning("使用模拟预测模式")
            df_test = dataset.prepare(
                [segment],
                col_set=["feature"],
                data_key=DataHandlerLP.DK_L
            )
            if isinstance(df_test, dict):
                X_test = df_test.get("feature")
            else:
                if self.feature_cols:
                    X_test = df_test[self.feature_cols]
                else:
                    X_test = df_test

            return pd.Series(
                np.random.normal(0, 0.1, len(X_test)),
                index=X_test.index
            )

        try:
            # 准备预测数据
            df_test = dataset.prepare(
                [segment],
                col_set=["feature"],
                data_key=DataHandlerLP.DK_L
            )

            if isinstance(df_test, dict):
                X_test = df_test.get("feature")
            else:
                if self.feature_cols:
                    X_test = df_test[self.feature_cols]
                else:
                    X_test = df_test

            # 预测
            predictions = self.model.predict(X_test)

            # 返回预测结果
            if isinstance(predictions, np.ndarray):
                return pd.Series(predictions, index=X_test.index)
            else:
                return predictions

        except Exception as e:
            logger.error(f"模型预测失败: {e}")
            raise

    def _calculate_metrics(
        self,
        y_true: Union[pd.Series, np.ndarray],
        y_pred: Union[pd.Series, np.ndarray]
    ) -> Dict[str, float]:
        """
        计算评估指标

        Args:
            y_true: 真实标签
            y_pred: 预测标签

        Returns:
            评估指标字典
        """
        try:
            from sklearn.metrics import (
                mean_squared_error, mean_absolute_error, r2_score
            )

            # 转换为numpy数组
            if isinstance(y_true, pd.Series):
                y_true = y_true.values
            if isinstance(y_pred, pd.Series):
                y_pred = y_pred.values

            # 计算指标
            mse = mean_squared_error(y_true, y_pred)
            mae = mean_absolute_error(y_true, y_pred)
            r2 = r2_score(y_true, y_pred)

            # 计算IC和IR（如果可能）
            ic = np.corrcoef(y_true, y_pred)[0, 1] if len(y_true) > 1 else 0
            ic_ir = ic / np.std(y_pred) if np.std(y_pred) > 0 else 0

            return {
                'mse': mse,
                'mae': mae,
                'r2': r2,
                'rmse': np.sqrt(mse),
                'ic': ic,
                'ic_ir': ic_ir,
            }

        except ImportError:
            # 如果sklearn不可用，返回简单指标
            mse = np.mean((y_true - y_pred) ** 2)
            return {
                'mse': mse,
                'rmse': np.sqrt(mse),
            }

    def get_feature_importance(self) -> Optional[Dict[str, float]]:
        """
        获取特征重要性

        Returns:
            特征重要性字典
        """
        if not self.is_trained or not QLIB_AVAILABLE or self.model is None:
            return None

        try:
            if hasattr(self.model, 'feature_importances_'):
                importances = self.model.feature_importances_
                if self.feature_cols:
                    return dict(zip(self.feature_cols, importances))
                else:
                    return {
                        f'feature_{i}': imp
                        for i, imp in enumerate(importances)
                    }
            else:
                logger.warning("模型不支持特征重要性计算")
                return None

        except Exception as e:
            logger.error(f"获取特征重要性失败: {e}")
            return None

    def save_model(self, file_path: str) -> bool:
        """
        保存模型

        Args:
            file_path: 保存路径

        Returns:
            是否保存成功
        """
        if not self.is_trained:
            logger.error("模型尚未训练，无法保存")
            return False

        try:
            if QLIB_AVAILABLE and hasattr(self.model, 'save_model'):
                self.model.save_model(file_path)
            else:
                # 使用pickle保存
                import pickle
                model_data = {
                    'model': self.model,
                    'model_type': self.model_type,
                    'model_params': self.model_params,
                    'feature_cols': self.feature_cols,
                    'is_trained': self.is_trained,
                }
                with open(file_path, 'wb') as f:
                    pickle.dump(model_data, f)

            logger.info(f"模型已保存: {file_path}")
            return True

        except Exception as e:
            logger.error(f"模型保存失败: {e}")
            return False

    def load_model(self, file_path: str) -> bool:
        """
        加载模型

        Args:
            file_path: 模型路径

        Returns:
            是否加载成功
        """
        try:
            if QLIB_AVAILABLE and hasattr(self.model, 'load_model'):
                self.model.load_model(file_path)
            else:
                # 使用pickle加载
                import pickle
                with open(file_path, 'rb') as f:
                    model_data = pickle.load(f)

                self.model = model_data['model']
                self.model_type = model_data['model_type']
                self.model_params = model_data['model_params']
                self.feature_cols = model_data['feature_cols']
                self.is_trained = model_data['is_trained']

            logger.info(f"模型已加载: {file_path}")
            return True

        except Exception as e:
            logger.error(f"模型加载失败: {e}")
            return False


class QLibForecastModelFactory:
    """QLib预测模型工厂"""

    @staticmethod
    def create_model(model_type: str, **kwargs) -> QLibForecastModel:
        """
        创建预测模型

        Args:
            model_type: 模型类型
            **kwargs: 模型参数

        Returns:
            预测模型实例
        """
        return QLibForecastModel(model_type=model_type, **kwargs)

    @staticmethod
    def get_available_models() -> list:
        """
        获取可用的模型类型

        Returns:
            模型类型列表
        """
        return ['lgb', 'linear', 'mlp']


# 使用示例
def example_usage():
    """使用示例"""
    print("=" * 70)
    print("QLib预测模型集成示例（完整版）")
    print("=" * 70)

    try:
        # 1. 创建模拟数据集
        print("🔄 创建模拟数据集...")

        # 创建模拟数据
        dates = pd.date_range('2020-01-01', periods=100, freq='D')
        instruments = ['SH600000', 'SZ000001', 'SH600036']

        all_data = []
        for instrument in instruments:
            np.random.seed(hash(instrument) % 10000)

            # 生成特征数据
            n_samples = len(dates)
            feature1 = np.random.randn(n_samples)
            feature2 = np.random.randn(n_samples)
            feature3 = np.random.randn(n_samples)

            # 生成标签（收益率）
            label = (
                0.1 * feature1 + 0.2 * feature2 - 0.1 * feature3 +
                np.random.randn(n_samples) * 0.1
            )

            # 创建DataFrame
            df = pd.DataFrame({
                'feature1': feature1,
                'feature2': feature2,
                'feature3': feature3,
                'label': label,
            }, index=pd.MultiIndex.from_product(
                [[instrument], dates], names=['instrument', 'date']
            ))

            all_data.append(df)

        # 合并所有数据
        full_data = pd.concat(all_data)

        # 划分训练/验证/测试集
        train_data = full_data.loc[
            pd.IndexSlice[:, '2020-01-01':'2020-06-30'], :
        ]
        valid_data = full_data.loc[
            pd.IndexSlice[:, '2020-07-01':'2020-08-31'], :
        ]
        test_data = full_data.loc[
            pd.IndexSlice[:, '2020-09-01':'2020-10-31'], :
        ]

        print(
            f"✅ 数据集创建完成: 训练集{len(train_data)}, "
            f"验证集{len(valid_data)}, 测试集{len(test_data)}"
        )

        # 2. 创建预测模型
        print("\n🤖 创建预测模型...")
        model = QLibForecastModelFactory.create_model(
            model_type='lgb',
            model_params={
                'learning_rate': 0.05,
                'num_leaves': 31,
                'verbose': -1,
            }
        )

        # 3. 创建模拟数据集对象
        class MockDataset:
            def __init__(self, train_data, valid_data, test_data):
                self.train_data = train_data
                self.valid_data = valid_data
                self.test_data = test_data

            def prepare(self, segments, col_set, data_key):
                result = {}
                for segment in segments:
                    if segment == 'train':
                        data = self.train_data
                    elif segment == 'valid':
                        data = self.valid_data
                    elif segment == 'test':
                        data = self.test_data
                    else:
                        continue

                    if col_set == ["feature", "label"]:
                        result[segment] = data
                    elif col_set == ["feature"]:
                        result[segment] = data.drop(columns=['label'])
                    elif col_set == ["label"]:
                        result[segment] = data[['label']]
                    elif col_set == ["weight"]:
                        # 创建权重
                        result[segment] = pd.DataFrame(
                            np.ones(len(data)),
                            index=data.index,
                            columns=['weight']
                        )

                return result if len(result) > 1 else list(result.values())[0]

        dataset = MockDataset(train_data, valid_data, test_data)

        # 4. 训练模型
        print("\n🎯 训练模型...")
        train_result = model.fit(dataset)

        print("训练结果:")
        for key, value in train_result.items():
            if isinstance(value, dict):
                print(f"  {key}:")
                for sub_key, sub_value in value.items():
                    print(f"    {sub_key}: {sub_value:.4f}")
            else:
                print(f"  {key}: {value}")

        # 5. 预测
        print("\n🔮 模型预测...")
        predictions = model.predict(dataset, segment='test')

        print(f"预测结果: {len(predictions)} 个预测")
        print(f"预测范围: [{predictions.min():.4f}, {predictions.max():.4f}]")

        # 6. 特征重要性
        print("\n📊 特征重要性:")
        feature_importance = model.get_feature_importance()
        if feature_importance:
            for feature, importance in sorted(
                feature_importance.items(), key=lambda x: x[1], reverse=True
            ):
                print(f"  {feature}: {importance:.4f}")

        # 7. 保存模型
        print("\n💾 保存模型...")
        model_saved = model.save_model("./test_forecast_model.pkl")
        print(f"模型保存: {'成功' if model_saved else '失败'}")

        # 8. 加载模型
        print("\n📂 加载模型...")
        new_model = QLibForecastModelFactory.create_model('lgb')
        model_loaded = new_model.load_model("./test_forecast_model.pkl")
        print(f"模型加载: {'成功' if model_loaded else '失败'}")

        print("\n🎉 QLib预测模型集成示例完成!")

        return True

    except Exception as e:
        print(f"❌ 示例执行失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # 设置日志级别
    logging.basicConfig(level=logging.INFO)

    # 运行示例
    example_usage()

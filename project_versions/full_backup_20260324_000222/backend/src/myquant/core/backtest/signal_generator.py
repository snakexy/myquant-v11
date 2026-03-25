# -*- coding: utf-8 -*-
"""
交易信号生成器
================
实现基于模型的交易信号生成逻辑

核心功能：
- 根据在线模型预测生成买入/卖出信号
- 计算信号置信度
- 支持多模型信号聚合

使用示例：
```python
generator = SignalGenerator(model_id="my_model")
signals = generator.generate_signals(online_models)
# {
#     "buy": ["000001.SZ", "600000.SH"],
#     "sell": [],
#     "timestamp": "2024-01-02T15:00:00",
#     "confidence": 0.85
# }
```
"""

from typing import Dict, Any, List, Optional
from loguru import logger
from datetime import datetime
import pandas as pd
import numpy as np


class SignalGenerator:
    """交易信号生成器（实现Qlib的SignalGenerator逻辑）

    职责：
    1. 接收在线模型列表
    2. 基于模型预测生成交易信号
    3. 计算信号置信度
    4. 返回买卖信号列表

    实现说明：
    - 使用真实的模型预测（不使用random）
    - 支持多模型信号聚合
    - 基于预测阈值生成交易信号
    """

    def __init__(self, model_id: str):
        """初始化信号生成器

        Args:
            model_id: 模型ID
        """
        self.model_id = model_id

        # 默认股票池
        self.stock_pool = self._get_default_stock_pool()

        # 导入DataLoader用于加载预测数据
        from myquant.core.backtest.data_loader import DataLoader
        self.data_loader = DataLoader()

        logger.info(f"SignalGenerator initialized for model '{model_id}'")

    def generate_signals(self, models: List[Dict[str, Any]]) -> Dict[str, Any]:
        """基于在线模型生成交易信号

        Args:
            models: 在线模型列表

        Returns:
            信号字典，包含：
            - buy: 买入信号列表
            - sell: 卖出信号列表
            - timestamp: 生成时间
            - confidence: 信号置信度
            - models_used: 使用的模型数量

        示例：
        ```python
        generator = SignalGenerator(model_id="my_model")
        signals = generator.generate_signals([{
            "model_id": "my_model_v1",
            "performance": {"sharpe_ratio": 1.5}
        }])
        ```
        """
        if not models:
            logger.warning(f"No models provided for signal generation (model: {self.model_id})")
            return {
                "buy": [],
                "sell": [],
                "timestamp": datetime.now().isoformat(),
                "confidence": 0.0,
                "models_used": 0
            }

        logger.info(
            f"Generating signals for model '{self.model_id}' "
            f"using {len(models)} online model(s)"
        )

        # 获取股票池
        stock_pool = self.stock_pool

        # 加载最新市场数据（用于预测）
        try:
            # 加载最近1天的数据
            from datetime import timedelta
            end_date = datetime.now()
            start_date = end_date - timedelta(days=7)  # 获取最近一周数据

            dataset = self.data_loader.load(
                start_date=start_date.strftime('%Y-%m-%d'),
                end_date=end_date.strftime('%Y-%m-%d'),
                instruments=stock_pool
            )

            df = dataset['df']
            features = dataset['features']

        except Exception as e:
            logger.error(f"Failed to load prediction data: {e}")
            return {
                "buy": [],
                "sell": [],
                "timestamp": datetime.now().isoformat(),
                "confidence": 0.0,
                "models_used": len(models),
                "error": str(e)
            }

        # 对每只股票进行预测
        buy_signals = []
        sell_signals = []
        stock_predictions = {}

        # 获取所有可用的股票代码
        try:
            available_stocks = df.index.get_level_values('instrument').unique()
        except Exception:
            # 如果没有instrument级别，尝试使用第二个级别
            try:
                available_stocks = df.index.get_level_values(1).unique()
            except Exception:
                available_stocks = stock_pool

        for stock in stock_pool:
            try:
                # 检查股票是否存在于数据中
                if stock not in available_stocks:
                    continue

                # 提取该股票的最新数据（使用xs进行跨截面选择）
                try:
                    stock_data = df.xs(stock, level='instrument', drop_level=True)
                    if len(stock_data) == 0:
                        continue
                    stock_data = stock_data.iloc[[-1]]  # 获取最新一行
                except Exception as e:
                    logger.debug(f"Cannot extract data for {stock}: {e}")
                    continue

                # 使用所有模型进行预测
                predictions = []
                for model_info in models:
                    try:
                        pred = self.predict(model_info, stock_data, features)
                        predictions.append(pred)
                    except Exception as e:
                        logger.debug(f"Prediction failed for model {model_info.get('model_id')}: {e}")
                        continue

                if predictions:
                    # 聚合预测结果（平均）
                    avg_pred = np.mean(predictions)

                    # 记录预测结果
                    stock_predictions[stock] = avg_pred

                    # 生成信号（基于预测阈值）
                    if avg_pred > 0.02:  # 预测收益率 > 2%，买入
                        buy_signals.append(stock)
                    elif avg_pred < -0.02:  # 预测收益率 < -2%，卖出
                        sell_signals.append(stock)

            except Exception as e:
                logger.debug(f"Failed to generate signal for {stock}: {e}")
                continue

        # 计算置信度
        confidence = self._calculate_confidence(buy_signals, sell_signals, stock_predictions)

        logger.info(
            f"Signals generated: {len(buy_signals)} buy, "
            f"{len(sell_signals)} sell, confidence={confidence:.4f}"
        )

        return {
            "buy": sorted(buy_signals),
            "sell": sorted(sell_signals),
            "timestamp": datetime.now().isoformat(),
            "confidence": round(confidence, 4),
            "models_used": len(models),
            "predictions": stock_predictions  # 包含所有预测结果
        }

    def _get_default_stock_pool(self) -> List[str]:
        """获取默认股票池"""
        return [
            "000001.SZ",  # 平安银行
            "000002.SZ",  # 万科A
            "600000.SH",  # 浦发银行
            "600036.SH",  # 招商银行
            "600519.SH",  # 贵州茅台
            "600887.SH",  # 伊利股份
            "000858.SZ",  # 五粮液
            "002475.SZ",  # 立讯精密
            "300059.SZ",  # 东方财富
            "601318.SH"   # 中国平安
        ]

    def predict(
        self,
        model: Dict[str, Any],
        stock_data: pd.DataFrame,
        features: List[str]
    ) -> float:
        """预测单只股票的得分

        Args:
            model: 模型字典（包含model_obj）
            stock_data: 股票数据DataFrame（单行）
            features: 特征列表

        Returns:
            预测得分（预测收益率）

        Raises:
            ValueError: 如果模型对象无效
        """
        try:
            # 提取模型对象
            model_obj = model.get("model_obj")
            if model_obj is None:
                raise ValueError("Model object not found in model dict")

            # 确保model_obj已训练
            if not model_obj.get("fitted", False):
                raise ValueError("Model has not been fitted yet")

            # 提取特征
            X = stock_data[features].values

            # 进行预测
            if model_obj["type"] == "mlp":
                # 标准化
                if "scaler" in model_obj:
                    X_scaled = model_obj["scaler"].transform(X)
                else:
                    X_scaled = X

                # MLP预测
                prediction = model_obj["mlp"].predict(X_scaled)[0]

            elif model_obj["type"] == "linear":
                # 标准化
                if "scaler" in model_obj:
                    X_scaled = model_obj["scaler"].transform(X)
                else:
                    X_scaled = X

                # 线性模型预测
                prediction = model_obj["model"].predict(X_scaled)[0]

            else:
                raise ValueError(f"Unknown model type: {model_obj['type']}")

            logger.debug(f"Prediction: {prediction:.6f}")

            return float(prediction)

        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            # 返回0表示不交易
            return 0.0

    def _calculate_confidence(
        self,
        buy_signals: List[str],
        sell_signals: List[str],
        predictions: Dict[str, float]
    ) -> float:
        """计算信号置信度

        Args:
            buy_signals: 买入信号列表
            sell_signals: 卖出信号列表
            predictions: 所有股票的预测结果

        Returns:
            置信度（0-1之间）
        """
        if not predictions:
            return 0.0

        # 方法1：基于预测的绝对值（越大的预测值越有信心）
        abs_predictions = [abs(p) for p in predictions.values()]
        avg_abs_pred = np.mean(abs_predictions)

        # 标准化到0-1范围
        confidence = min(1.0, avg_abs_pred * 10)  # 假设0.1的预测值已经是高信心

        # 方法2：基于信号数量（信号越多，信心越高，但也要考虑股票池大小）
        total_signals = len(buy_signals) + len(sell_signals)
        signal_ratio = total_signals / len(predictions)

        # 综合两种方法
        final_confidence = (confidence * 0.7) + (signal_ratio * 0.3)

        return max(0.0, min(1.0, final_confidence))

"""
模型训练模块测试

测试模型训练、超参数优化、模型评估和早停机制等功能
"""

import unittest
import numpy as np
import tempfile
import os
import logging

# 设置日志
logging.basicConfig(level=logging.INFO)


class TestModelTrainer(unittest.TestCase):
    """测试模型训练器"""

    def setUp(self):
        """测试前准备"""
        self.trainer = MockModelTrainer()
        self.X_train = np.random.randn(100, 5)
        self.y_train = np.random.randn(100)
        self.X_val = np.random.randn(20, 5)
        self.y_val = np.random.randn(20)

    def test_train_basic(self):
        """测试基础训练功能"""
        history = self.trainer.train(
            self.X_train, self.y_train,
            validation_data=(self.X_val, self.y_val)
        )

        self.assertIn('train_loss', history)
        self.assertIn('val_loss', history)
        self.assertEqual(len(history['train_loss']), 10)  # 默认10轮

    def test_train_with_early_stopping(self):
        """测试带早停的训练"""
        early_stopping = MockEarlyStopping()

        history = self.trainer.train(
            self.X_train, self.y_train,
            validation_data=(self.X_val, self.y_val),
            early_stopping=early_stopping
        )

        self.assertIn('train_loss', history)
        self.assertIn('val_loss', history)

    def test_save_and_load_model(self):
        """测试模型保存和加载"""
        # 训练模型
        self.trainer.train(self.X_train, self.y_train)

        with tempfile.TemporaryDirectory() as temp_dir:
            model_path = os.path.join(temp_dir, "test_model.pkl")

            # 保存模型
            self.trainer.save_model(model_path)
            self.assertTrue(os.path.exists(model_path))

            # 加载模型
            new_trainer = MockModelTrainer()
            new_trainer.load_model(model_path)

            # 验证模型参数相同
            np.testing.assert_array_equal(
                self.trainer.model.coef_,
                new_trainer.model.coef_
            )


class TestHyperparameterOptimizer(unittest.TestCase):
    """测试超参数优化器"""

    def setUp(self):
        """测试前准备"""
        self.trainer = MockModelTrainer()
        self.optimizer = GridSearchOptimizer()
        self.X = np.random.randn(100, 5)
        self.y = np.random.randn(100)

    def test_grid_search(self):
        """测试网格搜索"""
        param_grid = {
            'learning_rate': [0.01, 0.1],
            'regularization': [0.0, 0.1]
        }

        result = self.optimizer.optimize(
            self.X, self.y, self.trainer,
            param_grid=param_grid,
            cv=3
        )

        self.assertIn('best_params', result)
        self.assertIn('best_score', result)
        self.assertIn('cv_results', result)

        # 验证最佳参数在搜索空间中
        best_params = result['best_params']
        self.assertIn(
            best_params['learning_rate'],
            param_grid['learning_rate'])
        self.assertIn(
            best_params['regularization'],
            param_grid['regularization'])


class TestModelEvaluator(unittest.TestCase):
    """测试模型评估器"""

    def setUp(self):
        """测试前准备"""
        self.evaluator = MockModelEvaluator()
        self.y_true = np.array([1, 2, 3, 4, 5])
        self.y_pred = np.array([1.1, 2.1, 2.9, 4.1, 4.9])

    def test_evaluate_regression(self):
        """测试回归评估"""
        metrics = self.evaluator.evaluate(self.y_true, self.y_pred)

        self.assertIn('mse', metrics)
        self.assertIn('mae', metrics)
        self.assertIn('rmse', metrics)
        self.assertIn('r2', metrics)

        # 验证指标计算正确性
        expected_mse = np.mean((self.y_true - self.y_pred) ** 2)
        self.assertAlmostEqual(metrics['mse'], expected_mse, places=6)

    def test_generate_evaluation_report(self):
        """测试评估报告生成"""
        report = self.evaluator.generate_evaluation_report(
            self.y_true, self.y_pred,
            model_name="测试模型"
        )

        self.assertIn("测试模型 评估报告", report)
        self.assertIn("评估指标", report)
        self.assertIn("结论", report)


class TestEarlyStopping(unittest.TestCase):
    """测试早停机制"""

    def setUp(self):
        """测试前准备"""
        self.early_stopping = MockEarlyStopping(patience=3, min_delta=0.1)

    def test_improvement_detection(self):
        """测试改善检测"""
        # 初始评分
        self.assertFalse(self.early_stopping(1.0))
        self.assertEqual(self.early_stopping.counter, 0)

        # 改善
        self.assertFalse(self.early_stopping(0.8))
        self.assertEqual(self.early_stopping.counter, 0)

        # 无改善
        self.assertFalse(self.early_stopping(0.9))
        self.assertEqual(self.early_stopping.counter, 1)

        # 继续无改善
        self.assertFalse(self.early_stopping(0.95))
        self.assertEqual(self.early_stopping.counter, 2)

        # 触发早停
        self.assertTrue(self.early_stopping(0.92))  # 第3次无改善，触发早停

    def test_best_score_tracking(self):
        """测试最佳评分跟踪"""
        scores = [1.0, 0.8, 0.9, 0.7, 0.75]

        for score in scores:
            self.early_stopping(score)

        self.assertEqual(self.early_stopping.get_best_score(), 0.7)
        self.assertEqual(self.early_stopping.get_scores_history(), scores)


class MockModel:
    """模拟模型"""

    def __init__(self):
        self.coef_ = np.random.randn(5)
        self.intercept_ = np.random.randn(1)


class MockModelTrainer:
    """模拟模型训练器"""

    def __init__(self):
        self.model = MockModel()

    def train(self, X, y, validation_data=None, early_stopping=None, **kwargs):
        """模拟训练过程"""
        epochs = kwargs.get('epochs', 10)
        history = {'train_loss': [], 'val_loss': []}

        for epoch in range(epochs):
            # 模拟训练损失递减
            train_loss = 1.0 - epoch * 0.08 + np.random.normal(0, 0.01)
            history['train_loss'].append(max(train_loss, 0.1))

            if validation_data:
                # 模拟验证损失
                val_loss = train_loss + 0.1 + np.random.normal(0, 0.01)
                history['val_loss'].append(max(val_loss, 0.1))

                # 检查早停
                if early_stopping:
                    if early_stopping(val_loss, self.model):
                        break

        return history

    def save_model(self, path):
        """模拟保存模型"""
        import pickle
        with open(path, 'wb') as f:
            pickle.dump(self.model, f)

    def load_model(self, path):
        """模拟加载模型"""
        import pickle
        with open(path, 'rb') as f:
            self.model = pickle.load(f)


class MockEarlyStopping:
    """模拟早停机制"""

    def __init__(self, patience=5, min_delta=0.0):
        self.patience = patience
        self.min_delta = min_delta
        self.best_score = None
        self.counter = 0
        self.scores_history = []

    def __call__(self, score, model=None):
        """检查是否应该早停"""
        self.scores_history.append(score)

        if self.best_score is None:
            self.best_score = score
            return False

        if score < self.best_score - self.min_delta:
            self.best_score = score
            self.counter = 0
            return False
        else:
            self.counter += 1
            return self.counter >= self.patience

    def get_best_score(self):
        """获取最佳评分"""
        return self.best_score

    def get_scores_history(self):
        """获取评分历史"""
        return self.scores_history.copy()


class GridSearchOptimizer:
    """网格搜索优化器"""

    def optimize(self, X, y, model_trainer, param_grid, cv=3, **kwargs):
        """执行网格搜索"""
        from itertools import product

        # 生成参数组合
        param_names = list(param_grid.keys())
        param_values = list(param_grid.values())
        param_combinations = list(product(*param_values))

        best_score = float('inf')
        best_params = None
        cv_results = []

        for params in param_combinations:
            param_dict = dict(zip(param_names, params))

            # 模拟交叉验证
            scores = []
            for fold in range(cv):
                # 简单的模拟评分
                score = np.random.uniform(0.5, 1.0)
                scores.append(score)

            mean_score = np.mean(scores)
            cv_results.append({
                'params': param_dict,
                'mean_score': mean_score,
                'scores': scores
            })

            if mean_score < best_score:
                best_score = mean_score
                best_params = param_dict

        return {
            'best_params': best_params,
            'best_score': best_score,
            'cv_results': cv_results
        }


class MockModelEvaluator:
    """模拟模型评估器"""

    def evaluate(self, y_true, y_pred, **kwargs):
        """评估模型"""
        mse = np.mean((y_true - y_pred) ** 2)
        mae = np.mean(np.abs(y_true - y_pred))
        rmse = np.sqrt(mse)

        # 计算R²
        ss_res = np.sum((y_true - y_pred) ** 2)
        ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
        r2 = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0

        return {
            'mse': mse,
            'mae': mae,
            'rmse': rmse,
            'r2': r2
        }

    def generate_evaluation_report(
            self,
            y_true,
            y_pred,
            model_name="模型",
            save_path=None):
        """生成评估报告"""
        metrics = self.evaluate(y_true, y_pred)

        report = f"""
# {model_name} 评估报告
========================================

## 评估指标
- 均方误差 (MSE): {metrics['mse']:.6f}
- 平均绝对误差 (MAE): {metrics['mae']:.6f}
- 均方根误差 (RMSE): {metrics['rmse']:.6f}
- 决定系数 (R²): {metrics['r2']:.6f}

## 结论
"""

        if metrics['r2'] > 0.8:
            report += "模型表现优秀，具有很强的预测能力"
        elif metrics['r2'] > 0.6:
            report += "模型表现良好，具有较好的预测能力"
        elif metrics['r2'] > 0.4:
            report += "模型表现一般，预测能力有限"
        else:
            report += "模型表现较差，需要改进"

        report += "\n========================================\n"

        if save_path:
            with open(save_path, 'w', encoding='utf-8') as f:
                f.write(report)

        return report


if __name__ == '__main__':
    # 运行所有测试
    unittest.main(verbosity=2)

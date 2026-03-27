# -*- coding: utf-8 -*-
"""
滚动策略
==========
实现Qlib RollingStrategy架构的滚动训练任务生成

核心功能：
- 基于时间窗口滚动生成训练任务
- 支持自定义窗口大小和滚动步长
- 自动计算训练数据范围

使用示例：
```python
strategy = RollingStrategy(model_id="my_model", window_size=252, rolling_step=20)
tasks = strategy.prepare_tasks(cur_time="2024-01-02")
# 返回训练任务列表
```
"""

from typing import Dict, Any, List, Optional
from loguru import logger
from datetime import datetime, timedelta


class RollingStrategy:
    """滚动策略（实现Qlib的RollingStrategy逻辑）

    职责：
    1. 基于时间窗口滚动生成训练任务
    2. 计算训练数据的时间范围
    3. 支持自定义滚动步长

    使用示例：
    ```python
    strategy = RollingStrategy(
        model_id="my_model",
        window_size=252,    # 1年交易日
        rolling_step=20     # 每月滚动
    )

    # 准备新的训练任务
    tasks = strategy.prepare_tasks(cur_time="2024-01-02")
    ```
    """

    def __init__(
        self,
        model_id: str,
        window_size: int = 252,
        rolling_step: int = 20
    ):
        """初始化滚动策略

        Args:
            model_id: 模型ID
            window_size: 滚动窗口大小（交易日天数，默认252≈1年）
            rolling_step: 滚动步长（交易日天数，默认20≈1个月）
        """
        self.model_id = model_id
        self.window_size = window_size
        self.rolling_step = rolling_step

        # 每个交易日约等于0.4个自然日（252交易日/365自然日）
        self.trading_to_natural_days = 365.0 / 252.0

        logger.info(
            f"RollingStrategy initialized for model '{model_id}': "
            f"window_size={window_size}, rolling_step={rolling_step}"
        )

    def prepare_tasks(self, cur_time: Optional[str] = None) -> List[Dict[str, Any]]:
        """准备新的训练任务（基于滚动窗口）

        Args:
            cur_time: 当前时间点（None则使用最新）

        Returns:
            训练任务列表

        示例：
        ```python
        strategy = RollingStrategy(model_id="my_model")
        tasks = strategy.prepare_tasks(cur_time="2024-01-02")
        # [{
        #     "task_id": "task_2024-01-02_my_model",
        #     "model_id": "my_model",
        #     "train_start": "2023-01-03",
        #     "train_end": "2024-01-02",
        #     "window_size": 252,
        #     "status": "pending"
        # }]
        ```
        """
        # 解析当前时间
        if cur_time:
            try:
                current_date = datetime.fromisoformat(cur_time.replace('T', ' ').split()[0])
            except (ValueError, AttributeError):
                logger.warning(f"Invalid cur_time format: {cur_time}, using current time")
                current_date = datetime.now()
        else:
            current_date = datetime.now()

        # 计算训练窗口的起止时间
        train_end = current_date
        train_start = self._calculate_train_start(train_end)

        # 生成任务ID
        task_id = f"task_{current_date.strftime('%Y%m%d')}_{self.model_id}"

        task = {
            "task_id": task_id,
            "model_id": self.model_id,
            "cur_time": cur_time or current_date.isoformat(),
            "train_start": train_start.strftime('%Y-%m-%d'),
            "train_end": train_end.strftime('%Y-%m-%d'),
            "window_size": self.window_size,
            "rolling_step": self.rolling_step,
            "status": "pending",
            "created_at": datetime.now().isoformat()
        }

        logger.info(
            f"RollingStrategy prepared task for model '{self.model_id}': "
            f"train_start={task['train_start']}, train_end={task['train_end']}"
        )

        return [task]

    def _calculate_train_start(self, train_end: datetime) -> datetime:
        """计算训练开始时间（基于窗口大小）

        Args:
            train_end: 训练结束时间

        Returns:
            训练开始时间
        """
        # 将交易日窗口转换为自然日
        natural_days = int(self.window_size * self.trading_to_natural_days)

        # 向前推算窗口大小
        train_start = train_end - timedelta(days=natural_days)

        return train_start

    def get_next_rolling_time(self, current_time: Optional[str] = None) -> str:
        """获取下次滚动时间

        Args:
            current_time: 当前时间（None则使用最新）

        Returns:
            下次滚动时间的ISO格式字符串
        """
        if current_time:
            try:
                current_date = datetime.fromisoformat(current_time.replace('T', ' ').split()[0])
            except (ValueError, AttributeError):
                current_date = datetime.now()
        else:
            current_date = datetime.now()

        # 计算下次滚动时间（当前时间 + 滚动步长）
        natural_days = int(self.rolling_step * self.trading_to_natural_days)
        next_time = current_date + timedelta(days=natural_days)

        return next_time.isoformat()

    def get_rolling_info(self) -> Dict[str, Any]:
        """获取滚动策略信息

        Returns:
            滚动策略配置信息
        """
        # 计算窗口和步长的自然日
        window_natural_days = int(self.window_size * self.trading_to_natural_days)
        step_natural_days = int(self.rolling_step * self.trading_to_natural_days)

        return {
            "model_id": self.model_id,
            "window_size": self.window_size,
            "window_natural_days": window_natural_days,
            "rolling_step": self.rolling_step,
            "rolling_step_natural_days": step_natural_days,
            "description": f"每{step_natural_days}天（约{self.rolling_step}交易日）滚动一次，使用{window_natural_days}天（约{self.window_size}交易日）数据训练"
        }

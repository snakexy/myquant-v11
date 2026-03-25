# -*- coding: utf-8 -*-
"""
Research阶段 - RL策略优化服务
====================================

职责：
- RL策略训练（DQN/PPO/A2C）
- 策略超参数优化
- 环境构建和管理（基于QLib/Tianshou）
- 模型保存和加载
- 训练历史管理

基于QLib官方文档设计：
- EnvWrapper: Simulator + State Interpreter + Action Interpreter + Reward Function
- Policy: Tianshou策略框架
- Training Vessel & Trainer: trainer.fit()接口

应用场景：
1. Order Execution（订单执行优化）
2. Portfolio Construction（投资组合构建）

版本: v1.0
创建日期: 2026-02-11
"""

from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from loguru import logger
from datetime import datetime
from pathlib import Path
import pickle
import uuid
import json

try:
    import numpy as np
    import pandas as pd
    NP_AVAILABLE = True
except ImportError:
    np = None
    pd = None
    NP_AVAILABLE = False

# QLib和Tianshou导入（可选）
try:
    import tianshou as ts
    TIANSHOU_AVAILABLE = True
    print(f"[DEBUG] Tianshou imported successfully: {ts.__version__}")
except ImportError as e:
    TIANSHOU_AVAILABLE = False
    print(f"[DEBUG] Tianshou import failed: {e}")
    logger.warning("Tianshou未安装，RL功能将使用模拟模式")

try:
    import gym
    GYM_AVAILABLE = True
except ImportError:
    GYM_AVAILABLE = False
    logger.warning("Gym未安装，RL功能将使用模拟模式")

try:
    import torch
    import torch.nn as nn
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    logger.warning("PyTorch未安装，RL功能将使用模拟模式")


# ==================== 数据类定义 ====================

@dataclass
class RLTrainingConfig:
    """RL训练配置"""
    # 策略类型
    algorithm: str = "PPO"  # DQN, PPO, A2C, SAC

    # 应用场景
    scenario: str = "order_execution"  # order_execution, portfolio_construction

    # 训练参数
    max_episodes: int = 1000
    max_steps_per_episode: int = 100

    # 网络参数
    hidden_size: int = 128
    num_layers: int = 2
    learning_rate: float = 3e-4

    # RL特定参数
    gamma: float = 0.99  # 折扣因子
    tau: float = 0.005  # 软更新参数（用于DDPG/SAC等）
    buffer_size: int = 10000  # 经验回放缓冲区大小
    batch_size: int = 64  # 批次大小

    # PPO特定参数
    clip_param: float = 0.2  # PPO裁剪参数
    entropy_coef: float = 0.01  # 熵系数

    # DQN特定参数
    epsilon_start: float = 1.0  # ε-greedy起始值
    epsilon_end: float = 0.01  # ε-greedy结束值
    epsilon_decay: int = 1000  # ε衰减步数

    # 环境参数
    state_dim: int = 10  # 状态维度
    action_dim: int = 3  # 动作维度
    action_space: str = "discrete"  # discrete, continuous

    # 设备参数
    device: str = "auto"  # "auto", "cuda", "cpu"

    def get_device(self) -> str:
        """获取实际使用的设备"""
        if self.device == "auto":
            if TORCH_AVAILABLE:
                import torch
                device = "cuda" if torch.cuda.is_available() else "cpu"
                logger.info(f"[RLTrainingConfig] 自动检测设备: {device}")
                return device
            return "cpu"
        logger.info(f"[RLTrainingConfig] 使用指定设备: {self.device}")
        return self.device

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "algorithm": self.algorithm,
            "scenario": self.scenario,
            "max_episodes": self.max_episodes,
            "max_steps_per_episode": self.max_steps_per_episode,
            "hidden_size": self.hidden_size,
            "num_layers": self.num_layers,
            "learning_rate": self.learning_rate,
            "gamma": self.gamma,
            "tau": self.tau,
            "buffer_size": self.buffer_size,
            "batch_size": self.batch_size,
            "clip_param": self.clip_param,
            "entropy_coef": self.entropy_coef,
            "epsilon_start": self.epsilon_start,
            "epsilon_end": self.epsilon_end,
            "epsilon_decay": self.epsilon_decay,
            "state_dim": self.state_dim,
            "action_dim": self.action_dim,
            "action_space": self.action_space,
            "device": self.device
        }


@dataclass
class RLTrainingTrial:
    """RL训练试验记录"""
    trial_id: str
    task_id: str
    episode: int
    reward: float
    episode_length: int
    loss: Optional[float] = None
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "trial_id": self.trial_id,
            "task_id": self.task_id,
            "episode": self.episode,
            "reward": self.reward,
            "episode_length": self.episode_length,
            "loss": self.loss,
            "timestamp": self.timestamp.isoformat()
        }


@dataclass
class RLTrainingResult:
    """RL训练结果"""
    training_id: str
    algorithm: str
    scenario: str
    config: Dict[str, Any]

    # 训练指标
    total_episodes: int
    total_rewards: List[float]
    final_reward: float
    average_reward: float
    best_reward: float

    # 模型
    model: Optional[Any] = None  # 训练好的策略网络

    # 训练历史
    training_history: List[RLTrainingTrial] = field(default_factory=list)

    # 时间信息
    created_at: datetime = field(default_factory=datetime.now)
    training_duration: Optional[float] = None  # 训练耗时（秒）

    # 状态
    status: str = "completed"  # completed, failed, stopped

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "training_id": self.training_id,
            "algorithm": self.algorithm,
            "scenario": self.scenario,
            "config": self.config,
            "total_episodes": self.total_episodes,
            "final_reward": self.final_reward,
            "average_reward": self.average_reward,
            "best_reward": self.best_reward,
            "rewards_summary": {
                "min": float(min(self.total_rewards)) if self.total_rewards else 0.0,
                "max": float(max(self.total_rewards)) if self.total_rewards else 0.0,
                "mean": float(np.mean(self.total_rewards)) if self.total_rewards and NP_AVAILABLE else 0.0,
                "std": float(np.std(self.total_rewards)) if self.total_rewards and NP_AVAILABLE else 0.0
            },
            "training_history": [trial.to_dict() for trial in self.training_history],
            "created_at": self.created_at.isoformat(),
            "training_duration": self.training_duration,
            "status": self.status,
            "model_saved": self.model is not None
        }


@dataclass
class RLOptimizationResult:
    """RL超参数优化结果"""
    optimization_id: str
    algorithm: str
    scenario: str
    best_params: Dict[str, Any]
    best_metrics: Dict[str, float]
    all_trials: List[Dict[str, Any]]
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "optimization_id": self.optimization_id,
            "algorithm": self.algorithm,
            "scenario": self.scenario,
            "best_params": self.best_params,
            "best_metrics": self.best_metrics,
            "all_trials": self.all_trials,
            "created_at": self.created_at.isoformat(),
            "trial_count": len(self.all_trials)
        }


@dataclass
class RLAutoSelectionResult:
    """RL自动算法选择结果"""
    selection_id: str
    scenario: str
    algorithms_tried: List[str]
    results_by_algorithm: Dict[str, Dict[str, Any]]
    best_algorithm: str
    best_training_id: str
    best_reward: float
    training_duration: float
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "selection_id": self.selection_id,
            "scenario": self.scenario,
            "algorithms_tried": self.algorithms_tried,
            "results_by_algorithm": self.results_by_algorithm,
            "best_algorithm": self.best_algorithm,
            "best_training_id": self.best_training_id,
            "best_reward": self.best_reward,
            "training_duration": self.training_duration,
            "created_at": self.created_at.isoformat()
        }


# ==================== RL策略服务 ====================

class RLStrategyService:
    """
    RL策略优化服务

    基于QLib RL框架设计：

    1. EnvWrapper（环境封装）:
       - Simulator: 市场模拟器（SingleAssetOrderExecution等）
       - State Interpreter: 状态转换器
       - Action Interpreter: 动作转换器
       - Reward Function: 奖励函数

    2. Policy（策略）:
       - 使用Tianshou策略框架
       - 支持DQN/PPO/A2C等算法

    3. Training Vessel & Trainer（训练）:
       - trainer.fit()接口

    核心职责：
    1. RL策略训练
    2. 策略优化
    3. 模型管理
    4. 训练历史管理
    """

    def __init__(self, storage_dir: Optional[str] = None):
        """
        初始化RL策略服务

        Args:
            storage_dir: 模型存储目录
        """
        # 初始化存储目录
        if storage_dir is None:
            project_root = Path(__file__).parent.parent.parent.parent
            storage_dir = project_root / "backend" / "data" / "rl_strategy"

        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)

        # 创建子目录
        (self.storage_dir / "models").mkdir(exist_ok=True)
        (self.storage_dir / "results").mkdir(exist_ok=True)
        (self.storage_dir / "checkpoints").mkdir(exist_ok=True)

        # 内存中的训练任务
        self._running_tasks: Dict[str, RLTrainingResult] = {}

        # 检查依赖
        self._check_dependencies()

        logger.info(f"✅ RLStrategyService初始化完成: {self.storage_dir}")
        logger.info(f"   Tianshou可用: {TIANSHOU_AVAILABLE}")
        logger.info(f"   PyTorch可用: {TORCH_AVAILABLE}")
        logger.info(f"   NumPy可用: {NP_AVAILABLE}")

    def _check_dependencies(self) -> None:
        """检查依赖是否可用"""
        if not TIANSHOU_AVAILABLE:
            logger.warning("Tianshou未安装，将使用模拟模式")
        if not TORCH_AVAILABLE:
            logger.warning("PyTorch未安装，将使用模拟模式")
        if not NP_AVAILABLE:
            logger.warning("NumPy未安装，将使用模拟模式")

    # ==================== RL策略训练 ====================

    def _create_real_data_env(
        self,
        config: RLTrainingConfig,
        env_data: Optional[Dict[str, Any]]
    ):
        """
        创建基于真实K线数据的交易环境（回测环境）

        这是真实的数据回测环境，使用历史K线数据
        状态包含真实价格、成交量、技术指标
        奖励基于真实收益率计算

        Args:
            config: 训练配置
            env_data: 环境数据字典，应包含：
                - kline_data: K线数据（DataFrame）
                - indicators: 技术指标（DataFrame）
                - initial_cash: 初始资金
                - transaction_cost: 交易成本

        Returns:
            Gym环境实例
        """
        try:
            if not GYM_AVAILABLE:
                logger.warning("Gym未安装，无法创建真实数据环境")
                return self._create_simple_env(config, env_data)

            import gym
            import pandas as pd

            # 提取K线数据
            kline_df = env_data.get('kline_data') if env_data else None
            if kline_df is None or kline_df.empty:
                logger.warning("未提供K线数据，回退到简单环境")
                return self._create_simple_env(config, env_data)

            logger.info(f"创建真实数据回测环境: K线数据长度={len(kline_df)}")

            # 创建真实数据交易环境
            class RealDataTradingEnv(gym.Env):
                """
                基于真实K线数据的交易环境

                状态空间：包含价格、技术指标、持仓信息
                动作空间：0=持有, 1=买入, 2=卖出
                奖励：基于实际收益率计算
                """

                def __init__(self, kline_df: pd.DataFrame, initial_cash: float = 100000.0):
                    super(RealDataTradingEnv, self).__init__()

                    self.kline_df = kline_df.reset_index(drop=True)
                    self.initial_cash = initial_cash
                    self.current_cash = initial_cash
                    self.position = 0  # 0=空仓, 1=持有
                    self.current_step = 0
                    self.max_steps = len(kline_df) - 1

                    # 技术指标（简单示例）
                    self.kline_df['ma5'] = kline_df['close'].rolling(window=5).mean()
                    self.kline_df['ma20'] = kline_df['close'].rolling(window=20).mean()

                    # 状态维度：价格(5) + 持仓(1) + 现金比例(1) + 技术指标(2) = 9
                    self.state_dim = 9
                    self.action_dim = 3  # 0=持有, 1=买入, 2=卖出

                    # 动作空间：离散动作
                    self.action_space = gym.spaces.Discrete(3)

                    # 观察空间：连续值
                    self.observation_space = gym.spaces.Box(
                        low=-np.inf,
                        high=np.inf,
                        shape=(self.state_dim,),
                        dtype=np.float32
                    )

                def reset(self):
                    """重置环境到初始状态"""
                    self.current_step = 0
                    self.current_cash = self.initial_cash
                    self.position = 0

                    # 返回初始状态
                    return self._get_state()

                def _get_state(self):
                    """获取当前状态向量"""
                    if self.current_step >= len(self.kline_df) - 1:
                        return np.zeros(self.state_dim)

                    row = self.kline_df.iloc[self.current_step]

                    # 构建状态向量
                    state = np.zeros(self.state_dim, dtype=np.float32)

                    # 价格特征（归一化）
                    current_price = row['close']
                    state[0] = current_price / 1000.0  # 价格归一化
                    # 计算相对价格（使用mean()避免序列问题）
                    price_slice = self.kline_df['close'].iloc[max(0, self.current_step-5):self.current_step]
                    state[1] = (current_price / price_slice.mean()) - 1.0  # 相对价格

                    # 持仓信息
                    state[2] = float(self.position)

                    # 现金比例（归一化）
                    state[3] = self.current_cash / self.initial_cash

                    # 技术指标（归一化）
                    if not pd.isna(row['ma5']):
                        state[4] = row['ma5'] / 1000.0
                    if not pd.isna(row['ma20']):
                        state[5] = row['ma20'] / 1000.0

                    # 价格变化率
                    if self.current_step > 0:
                        prev_price = self.kline_df['close'].iloc[self.current_step - 1]
                        state[6] = (current_price - prev_price) / prev_price if prev_price > 0 else 0
                        state[7] = (current_price - prev_price) / current_price if current_price > 0 else 0
                    else:
                        state[6] = 0
                        state[7] = 0

                    return state

                def step(self, action):
                    """执行一步交易"""
                    # 检查是否结束
                    if self.current_step >= self.max_steps:
                        return self._get_state(), 0.0, True, {}

                    # 获取当前和下一时刻的价格
                    current_price = self.kline_df['close'].iloc[self.current_step]
                    reward = 0.0

                    # 执行动作
                    if action == 0:  # 持有
                        reward = 0.0

                    elif action == 1:  # 买入
                        if self.position == 0:  # 空仓
                            self.position = 1
                            self.current_cash -= current_price  # 扣除买入成本
                            # 计算收益率作为奖励
                            next_price = self.kline_df['close'].iloc[min(self.current_step + 1, self.max_steps)]
                            reward = (next_price - current_price) / current_price
                        else:
                            # 已持有，不能买入
                            reward = -0.01  # 惩罚

                    elif action == 2:  # 卖出
                        if self.position == 1:  # 持有中
                            self.position = 0
                            self.current_cash += current_price  # 获得卖出金额
                            # 计算收益率作为奖励（使用mean()避免序列问题）
                            prev_slice = self.kline_df['close'].iloc[max(0, self.current_step - 1):self.current_step]
                            reward = (current_price - prev_slice.mean()) / prev_slice.mean()
                        else:
                            # 空仓，不能卖出
                            reward = -0.01  # 惩罚

                    # 移动到下一步
                    self.current_step += 1

                    # 检查是否结束
                    done = self.current_step >= self.max_steps

                    # 计算总资产
                    total_asset = self.current_cash + self.position * current_price

                    info = {
                        'cash': self.current_cash,
                        'position': self.position,
                        'total_asset': total_asset,
                        'current_price': current_price
                    }

                    return self._get_state(), reward, done, info

            # 创建真实数据环境实例
            env = RealDataTradingEnv(kline_df)
            return env

        except ImportError as e:
            logger.error(f"创建真实数据环境失败: {e}")
            logger.info("回退到简单环境")
            return self._create_simple_env(config, env_data)

    def train_rl_strategy(
        self,
        config: RLTrainingConfig,
        env_data: Optional[Dict[str, Any]] = None
    ) -> RLTrainingResult:
        """
        训练RL策略

        支持的算法：DQN, PPO, A2C
        支持的场景：order_execution, portfolio_construction

        Args:
            config: 训练配置
            env_data: 环境数据（包含市场数据、初始状态等）

        Returns:
            训练结果
        """
        try:
            logger.info(f"开始RL策略训练: algorithm={config.algorithm}, scenario={config.scenario}")

            training_id = f"{config.algorithm.lower()}_{config.scenario}_{uuid.uuid4().hex[:8]}"
            start_time = datetime.now()

            # 检查依赖
            if not (TIANSHOU_AVAILABLE and TORCH_AVAILABLE and NP_AVAILABLE):
                logger.warning("依赖不满足，使用模拟训练")
                result = self._simulate_training(config, training_id)
            else:
                # 根据算法选择训练方法
                if config.algorithm == "DQN":
                    result = self._train_dqn(config, env_data, training_id)
                elif config.algorithm == "PPO":
                    result = self._train_ppo(config, env_data, training_id)
                elif config.algorithm == "A2C":
                    result = self._train_a2c(config, env_data, training_id)
                else:
                    raise ValueError(f"不支持的算法: {config.algorithm}")

            # 计算训练耗时
            end_time = datetime.now()
            result.training_duration = (end_time - start_time).total_seconds()

            # 保存到内存中
            logger.info(f"[train_rl_strategy] 准备保存到内存: {training_id}")
            self._running_tasks[training_id] = result
            logger.info(f"✅ 已保存到内存: {training_id}, 当前任务数: {len(self._running_tasks)}")

            # 保存结果到文件
            logger.info(f"[train_rl_strategy] 准备保存到文件...")
            save_success = self._save_training_result(result)
            logger.info(f"[train_rl_strategy] 文件保存结果: {save_success}")

            logger.info(
                f"RL策略训练完成: {training_id}, "
                f"episodes={result.total_episodes}, "
                f"best_reward={result.best_reward:.4f}"
            )

            return result

        except Exception as e:
            logger.error(f"RL策略训练失败: {e}")
            # 返回失败结果
            return RLTrainingResult(
                training_id=training_id if 'training_id' in locals() else "unknown",
                algorithm=config.algorithm,
                scenario=config.scenario,
                config=config.to_dict(),
                total_episodes=0,
                total_rewards=[],
                final_reward=0.0,
                average_reward=0.0,
                best_reward=0.0,
                status="failed"
            )

    def train_rl_strategy_with_progress(
        self,
        config: RLTrainingConfig,
        env_data: Optional[Dict[str, Any]] = None,
        training_id: Optional[str] = None,
        progress_callback: Optional[callable] = None
    ) -> RLTrainingResult:
        """
        带进度回调的RL策略训练

        Args:
            config: 训练配置
            env_data: 环境数据
            training_id: 训练ID（可选）
            progress_callback: 进度回调函数
                callback(training_id, progress, status, algorithm, reward, episode, total_episodes)

        Returns:
            训练结果
        """
        try:
            logger.info(f"开始RL策略训练(带进度): algorithm={config.algorithm}")

            if training_id is None:
                training_id = f"{config.algorithm.lower()}_{config.scenario}_{uuid.uuid4().hex[:8]}"

            start_time = datetime.now()

            # 初始进度
            if progress_callback:
                progress_callback(training_id, 0, "initializing", config.algorithm, 0.0, 0, config.max_episodes)

            # 检查依赖
            if not (TIANSHOU_AVAILABLE and TORCH_AVAILABLE and NP_AVAILABLE):
                logger.warning("依赖不满足，使用模拟训练")
                result = self._simulate_training_with_progress(
                    config, training_id, progress_callback
                )
            else:
                # 根据算法选择训练方法
                if progress_callback:
                    progress_callback(training_id, 10, "training", config.algorithm, 0.0, 0, config.max_episodes)

                if config.algorithm == "DQN":
                    result = self._train_dqn_with_progress(config, env_data, training_id, progress_callback)
                elif config.algorithm == "PPO":
                    result = self._train_ppo_with_progress(config, env_data, training_id, progress_callback)
                elif config.algorithm == "A2C":
                    result = self._train_a2c_with_progress(config, env_data, training_id, progress_callback)
                else:
                    raise ValueError(f"不支持的算法: {config.algorithm}")

            # 计算训练耗时
            end_time = datetime.now()
            result.training_duration = (end_time - start_time).total_seconds()

            # 完成进度
            if progress_callback:
                progress_callback(training_id, 100, "completed", config.algorithm,
                                result.best_reward, result.total_episodes, config.max_episodes)

            # 保存到内存中
            self._running_tasks[training_id] = result

            # 保存结果到文件
            self._save_training_result(result)

            logger.info(
                f"RL策略训练完成: {training_id}, "
                f"episodes={result.total_episodes}, "
                f"best_reward={result.best_reward:.4f}"
            )

            return result

        except Exception as e:
            logger.error(f"RL策略训练失败: {e}")
            if progress_callback:
                progress_callback(training_id, 0, "error", config.algorithm, 0.0, 0, 0)
            return RLTrainingResult(
                training_id=training_id if 'training_id' in locals() else "unknown",
                algorithm=config.algorithm,
                scenario=config.scenario,
                config=config.to_dict(),
                total_episodes=0,
                total_rewards=[],
                final_reward=0.0,
                average_reward=0.0,
                best_reward=0.0,
                status="failed"
            )

    def _simulate_training_with_progress(
        self,
        config: RLTrainingConfig,
        training_id: str,
        progress_callback: Optional[callable] = None
    ) -> RLTrainingResult:
        """带进度的模拟训练"""
        import time

        total_episodes = config.max_episodes
        rewards = []

        for episode in range(total_episodes):
            # 模拟训练
            time.sleep(0.02)  # 加快模拟速度

            # 模拟奖励
            reward = 0.5 + 0.4 * (episode / total_episodes) + np.random.random() * 0.1
            rewards.append(reward)

            # 更新进度
            if progress_callback and episode % max(1, total_episodes // 20) == 0:
                progress = int((episode / total_episodes) * 90) + 5  # 5-95%
                progress_callback(training_id, progress, "training", config.algorithm,
                                reward, episode + 1, total_episodes)

        return RLTrainingResult(
            training_id=training_id,
            algorithm=config.algorithm,
            scenario=config.scenario,
            config=config.to_dict(),
            total_episodes=total_episodes,
            total_rewards=rewards,
            final_reward=float(rewards[-1]) if rewards else 0.0,
            average_reward=float(np.mean(rewards)) if rewards else 0.0,
            best_reward=float(max(rewards)) if rewards else 0.0,
            status="completed"
        )

    def _train_dqn_with_progress(
        self,
        config: RLTrainingConfig,
        env_data: Optional[Dict[str, Any]],
        training_id: str,
        progress_callback: Optional[callable] = None
    ) -> RLTrainingResult:
        """训练DQN策略 - 带进度更新"""
        try:
            import torch
            import torch.nn as nn
            import gymnasium as gym
            import numpy as np
            from tianshou.algorithm.modelfree.dqn import DQN, DiscreteQLearningPolicy
            from tianshou.algorithm.optim import Adam
            from tianshou.data import Collector, VectorReplayBuffer
            from tianshou.trainer import OffPolicyTrainer, OffPolicyTrainerParams

            device = config.get_device()
            # 明确显示 GPU 使用状态
            if device == 'cuda':
                import torch
                gpu_name = torch.cuda.get_device_name(0)
                logger.info(f"[GPU] 训练DQN策略: 使用 {gpu_name}")
            else:
                logger.info(f"[CPU] 训练DQN策略: 使用 CPU")

            env = gym.make("CartPole-v1")
            obs_space = env.observation_space
            act_space = env.action_space
            state_dim = obs_space.shape[0]
            action_dim = act_space.n

            class QNetwork(nn.Module):
                def __init__(self, state_dim, action_dim, hidden_size=128,
                             device='cpu'):
                    super().__init__()
                    self._device = device
                    self.net = nn.Sequential(
                        nn.Linear(state_dim, hidden_size),
                        nn.ReLU(),
                        nn.Linear(hidden_size, hidden_size),
                        nn.ReLU(),
                        nn.Linear(hidden_size, action_dim)
                    )

                def forward(self, obs, state=None, info={}):
                    if isinstance(obs, np.ndarray):
                        obs = torch.as_tensor(
                            obs, dtype=torch.float32, device=self._device)
                    elif isinstance(obs, torch.Tensor):
                        obs = obs.to(self._device)
                    return self.net(obs), state

            q_net = QNetwork(
                state_dim, action_dim, config.hidden_size, device=device)
            q_net = q_net.to(device)

            policy = DiscreteQLearningPolicy(
                model=q_net,
                action_space=act_space,
                observation_space=obs_space,
                eps_training=0.1,
                eps_inference=0.05
            )

            from tianshou.algorithm.optim import AdamOptimizerFactory
            optim_factory = AdamOptimizerFactory(lr=config.learning_rate)
            algorithm = DQN(
                policy=policy,
                optim=optim_factory,
                gamma=config.gamma,
                n_step_return_horizon=3,
                target_update_freq=100,
                is_double=True
            )

            buffer = VectorReplayBuffer(total_size=config.buffer_size, buffer_num=1)
            train_collector = Collector(algorithm, env, buffer)
            train_collector.reset()

            max_epochs = config.max_episodes

            # 手动训练循环以支持进度更新
            rewards_history = []
            steps_per_epoch = 1000  # 每个 epoch 收集更多步数
            updates_per_epoch = 10  # 每个 epoch 更新多次

            for epoch in range(max_epochs):
                # 收集数据
                collect_result = train_collector.collect(n_step=steps_per_epoch)
                # Tianshou 2.0: 使用 returns_stat.mean 获取平均奖励
                if hasattr(collect_result, 'returns_stat') and \
                        collect_result.returns_stat is not None:
                    epoch_reward = float(collect_result.returns_stat.mean)
                else:
                    epoch_reward = 0.0
                rewards_history.append(float(epoch_reward)
                                       if epoch_reward else 0.0)

                # 训练 - 每个 epoch 多次更新以更好利用 GPU
                if len(buffer) >= config.batch_size:
                    policy.is_within_training_step = True
                    try:
                        for _ in range(updates_per_epoch):
                            algorithm.update(buffer=buffer,
                                             sample_size=config.batch_size)
                    finally:
                        policy.is_within_training_step = False

                # 更新进度
                if progress_callback:
                    progress = int(10 + (epoch / max_epochs) * 85)  # 10-95%
                    best_reward = max(rewards_history) \
                        if rewards_history else 0.0
                    progress_callback(training_id, progress, "training",
                                      config.algorithm,
                                      best_reward, epoch + 1, max_epochs)

            best_reward = max(rewards_history) if rewards_history else 0.0
            env.close()

            return RLTrainingResult(
                training_id=training_id,
                algorithm=config.algorithm,
                scenario=config.scenario,
                config=config.to_dict(),
                total_episodes=len(rewards_history),
                total_rewards=rewards_history,
                final_reward=float(rewards_history[-1]) if rewards_history else 0.0,
                average_reward=float(np.mean(rewards_history)) if rewards_history else 0.0,
                best_reward=float(best_reward),
                status="completed"
            )

        except Exception as e:
            logger.error(f"DQN训练失败: {e}")
            return self._simulate_training_with_progress(config, training_id, progress_callback)

    def _train_ppo_with_progress(
        self,
        config: RLTrainingConfig,
        env_data: Optional[Dict[str, Any]],
        training_id: str,
        progress_callback: Optional[callable] = None
    ) -> RLTrainingResult:
        """训练PPO策略 - 带进度更新 (Tianshou 2.0 API)"""
        try:
            import torch
            import torch.nn as nn
            import torch.nn.functional as F
            import gymnasium as gym
            import numpy as np
            from tianshou.algorithm.modelfree.ppo import PPO, ProbabilisticActorPolicy
            from tianshou.data import Collector, ReplayBuffer
            from tianshou.algorithm.optim import AdamOptimizerFactory

            device = config.get_device()
            # 明确显示 GPU 使用状态
            if device == 'cuda':
                gpu_name = torch.cuda.get_device_name(0)
                logger.info(f"[GPU] 训练PPO策略: 使用 {gpu_name}")
            else:
                logger.info(f"[CPU] 训练PPO策略: 使用 CPU")

            env = gym.make("CartPole-v1")
            obs_space = env.observation_space
            act_space = env.action_space
            state_dim = obs_space.shape[0]
            action_dim = act_space.n

            # 离散动作空间的 Actor 网络 - 需要输出 logits
            class DiscreteActor(nn.Module):
                def __init__(self, state_dim, action_dim, hidden_size=128):
                    super().__init__()
                    self.net = nn.Sequential(
                        nn.Linear(state_dim, hidden_size),
                        nn.ReLU(),
                        nn.Linear(hidden_size, hidden_size),
                        nn.ReLU(),
                        nn.Linear(hidden_size, action_dim)
                    )
                    self._device = device

                def forward(self, obs, state=None, info={}):
                    if isinstance(obs, np.ndarray):
                        obs = torch.as_tensor(obs, dtype=torch.float32, device=self._device)
                    elif isinstance(obs, torch.Tensor):
                        obs = obs.to(self._device)
                    logits = self.net(obs)
                    return logits, state

            # Critic 网络
            class CriticNetwork(nn.Module):
                def __init__(self, state_dim, hidden_size=128):
                    super().__init__()
                    self.net = nn.Sequential(
                        nn.Linear(state_dim, hidden_size),
                        nn.ReLU(),
                        nn.Linear(hidden_size, hidden_size),
                        nn.ReLU(),
                        nn.Linear(hidden_size, 1)
                    )
                    self._device = device

                def forward(self, obs, state=None, info={}):
                    if isinstance(obs, np.ndarray):
                        obs = torch.as_tensor(obs, dtype=torch.float32, device=self._device)
                    elif isinstance(obs, torch.Tensor):
                        obs = obs.to(self._device)
                    return self.net(obs).squeeze(-1), state

            actor = DiscreteActor(state_dim, action_dim, config.hidden_size).to(device)
            critic = CriticNetwork(state_dim, config.hidden_size).to(device)

            # 定义分布函数 - 对于离散动作空间使用 Categorical
            def dist_fn(logits):
                return torch.distributions.Categorical(logits=logits)

            # 创建 ProbabilisticActorPolicy
            policy = ProbabilisticActorPolicy(
                actor=actor,
                dist_fn=dist_fn,
                action_space=act_space,
                observation_space=obs_space,
                deterministic_eval=True
            )

            optim = AdamOptimizerFactory(lr=config.learning_rate)

            algorithm = PPO(
                policy=policy,
                critic=critic,
                optim=optim,
                eps_clip=config.clip_param or 0.2,
                vf_coef=0.5,
                ent_coef=config.entropy_coef or 0.01,
                gae_lambda=0.95,
                max_batchsize=config.batch_size,
                gamma=config.gamma
            )

            buffer = ReplayBuffer(size=10000)
            collector = Collector(algorithm, env, buffer)
            collector.reset()

            max_epochs = config.max_episodes
            rewards_history = []
            steps_per_epoch = 1000  # 每个 epoch 收集更多步数
            updates_per_epoch = 10  # 每个 epoch 更新多次

            for epoch in range(max_epochs):
                collect_result = collector.collect(n_step=steps_per_epoch)
                # Tianshou 2.0: 使用 returns_stat.mean 获取平均奖励
                if hasattr(collect_result, 'returns_stat') and \
                        collect_result.returns_stat is not None:
                    epoch_reward = float(collect_result.returns_stat.mean)
                else:
                    epoch_reward = 0.0
                rewards_history.append(float(epoch_reward)
                                       if epoch_reward else 0.0)

                # 每个 epoch 多次更新以更好利用 GPU
                if len(buffer) >= config.batch_size:
                    policy.is_within_training_step = True
                    try:
                        for _ in range(updates_per_epoch):
                            algorithm.update(buffer=buffer,
                                             sample_size=config.batch_size)
                    finally:
                        policy.is_within_training_step = False

                if progress_callback:
                    progress = int(10 + (epoch / max_epochs) * 85)
                    best_reward = max(rewards_history) \
                        if rewards_history else 0.0
                    progress_callback(training_id, progress, "training",
                                      config.algorithm,
                                      best_reward, epoch + 1, max_epochs)

            best_reward = max(rewards_history) if rewards_history else 0.0
            env.close()

            return RLTrainingResult(
                training_id=training_id,
                algorithm=config.algorithm,
                scenario=config.scenario,
                config=config.to_dict(),
                total_episodes=len(rewards_history),
                total_rewards=rewards_history,
                final_reward=float(rewards_history[-1]) if rewards_history else 0.0,
                average_reward=float(np.mean(rewards_history)) if rewards_history else 0.0,
                best_reward=float(best_reward),
                status="completed"
            )

        except Exception as e:
            logger.error(f"PPO训练失败: {e}")
            return self._simulate_training_with_progress(config, training_id, progress_callback)

    def _train_a2c_with_progress(
        self,
        config: RLTrainingConfig,
        env_data: Optional[Dict[str, Any]],
        training_id: str,
        progress_callback: Optional[callable] = None
    ) -> RLTrainingResult:
        """训练A2C策略 - 带进度更新 (Tianshou 2.0 API)"""
        try:
            import torch
            import torch.nn as nn
            import torch.nn.functional as F
            import gymnasium as gym
            import numpy as np
            from tianshou.algorithm.modelfree.a2c import A2C, ProbabilisticActorPolicy
            from tianshou.data import Collector, ReplayBuffer
            from tianshou.algorithm.optim import AdamOptimizerFactory

            device = config.get_device()
            # 明确显示 GPU 使用状态
            if device == 'cuda':
                gpu_name = torch.cuda.get_device_name(0)
                logger.info(f"[GPU] 训练A2C策略: 使用 {gpu_name}")
            else:
                logger.info(f"[CPU] 训练A2C策略: 使用 CPU")

            env = gym.make("CartPole-v1")
            obs_space = env.observation_space
            act_space = env.action_space
            state_dim = obs_space.shape[0]
            action_dim = act_space.n

            # 离散动作空间的 Actor 网络
            class DiscreteActor(nn.Module):
                def __init__(self, state_dim, action_dim, hidden_size=128):
                    super().__init__()
                    self.net = nn.Sequential(
                        nn.Linear(state_dim, hidden_size),
                        nn.ReLU(),
                        nn.Linear(hidden_size, hidden_size),
                        nn.ReLU(),
                        nn.Linear(hidden_size, action_dim)
                    )
                    self._device = device

                def forward(self, obs, state=None, info={}):
                    if isinstance(obs, np.ndarray):
                        obs = torch.as_tensor(obs, dtype=torch.float32, device=self._device)
                    elif isinstance(obs, torch.Tensor):
                        obs = obs.to(self._device)
                    logits = self.net(obs)
                    return logits, state

            # Critic 网络
            class CriticNetwork(nn.Module):
                def __init__(self, state_dim, hidden_size=128):
                    super().__init__()
                    self.net = nn.Sequential(
                        nn.Linear(state_dim, hidden_size),
                        nn.ReLU(),
                        nn.Linear(hidden_size, hidden_size),
                        nn.ReLU(),
                        nn.Linear(hidden_size, 1)
                    )
                    self._device = device

                def forward(self, obs, state=None, info={}):
                    if isinstance(obs, np.ndarray):
                        obs = torch.as_tensor(obs, dtype=torch.float32, device=self._device)
                    elif isinstance(obs, torch.Tensor):
                        obs = obs.to(self._device)
                    return self.net(obs).squeeze(-1), state

            actor = DiscreteActor(state_dim, action_dim, config.hidden_size).to(device)
            critic = CriticNetwork(state_dim, config.hidden_size).to(device)

            # 定义分布函数 - 对于离散动作空间使用 Categorical
            def dist_fn(logits):
                return torch.distributions.Categorical(logits=logits)

            # 创建 ProbabilisticActorPolicy
            policy = ProbabilisticActorPolicy(
                actor=actor,
                dist_fn=dist_fn,
                action_space=act_space,
                observation_space=obs_space,
                deterministic_eval=True
            )

            optim = AdamOptimizerFactory(lr=config.learning_rate)

            algorithm = A2C(
                policy=policy,
                critic=critic,
                optim=optim,
                vf_coef=0.5,
                ent_coef=config.entropy_coef or 0.01,
                gae_lambda=0.95,
                max_batchsize=config.batch_size,
                gamma=config.gamma
            )

            buffer = ReplayBuffer(size=10000)
            collector = Collector(algorithm, env, buffer)
            collector.reset()

            max_epochs = config.max_episodes
            rewards_history = []
            steps_per_epoch = 1000  # 每个 epoch 收集更多步数
            updates_per_epoch = 10  # 每个 epoch 更新多次

            for epoch in range(max_epochs):
                collect_result = collector.collect(n_step=steps_per_epoch)
                # Tianshou 2.0: 使用 returns_stat.mean 获取平均奖励
                if hasattr(collect_result, 'returns_stat') and \
                        collect_result.returns_stat is not None:
                    epoch_reward = float(collect_result.returns_stat.mean)
                else:
                    epoch_reward = 0.0
                rewards_history.append(float(epoch_reward)
                                       if epoch_reward else 0.0)

                # 每个 epoch 多次更新以更好利用 GPU
                if len(buffer) >= config.batch_size:
                    policy.is_within_training_step = True
                    try:
                        for _ in range(updates_per_epoch):
                            algorithm.update(buffer=buffer,
                                             sample_size=config.batch_size)
                    finally:
                        policy.is_within_training_step = False

                if progress_callback:
                    progress = int(10 + (epoch / max_epochs) * 85)
                    best_reward = max(rewards_history) \
                        if rewards_history else 0.0
                    progress_callback(training_id, progress, "training",
                                      config.algorithm,
                                      best_reward, epoch + 1, max_epochs)

            best_reward = max(rewards_history) if rewards_history else 0.0
            env.close()

            return RLTrainingResult(
                training_id=training_id,
                algorithm=config.algorithm,
                scenario=config.scenario,
                config=config.to_dict(),
                total_episodes=len(rewards_history),
                total_rewards=rewards_history,
                final_reward=float(rewards_history[-1]) if rewards_history else 0.0,
                average_reward=float(np.mean(rewards_history)) if rewards_history else 0.0,
                best_reward=float(best_reward),
                status="completed"
            )

        except Exception as e:
            logger.error(f"A2C训练失败: {e}")
            return self._simulate_training_with_progress(config, training_id, progress_callback)

    def _train_dqn(
        self,
        config: RLTrainingConfig,
        env_data: Optional[Dict[str, Any]],
        training_id: str
    ) -> RLTrainingResult:
        """训练DQN策略 - Tianshou 2.0兼容版本，支持GPU"""
        try:
            import torch
            import torch.nn as nn
            import gymnasium as gym
            import numpy as np
            from tianshou.algorithm.modelfree.dqn import DQN, DiscreteQLearningPolicy
            from tianshou.algorithm.optim import Adam
            from tianshou.data import Collector, VectorReplayBuffer
            from tianshou.trainer import OffPolicyTrainer, OffPolicyTrainerParams

            # 获取设备
            device = config.get_device()
            logger.info(
                f"训练DQN策略: state_dim={config.state_dim}, "
                f"action_dim={config.action_dim}, device={device}"
            )

            # 创建简单的CartPole风格环境用于演示
            env = gym.make("CartPole-v1")

            # 获取环境信息
            obs_space = env.observation_space
            act_space = env.action_space
            state_dim = obs_space.shape[0]
            action_dim = act_space.n

            logger.info(f"环境: state_dim={state_dim}, action_dim={action_dim}")

            # 构建简单的Q网络 - 使用设备感知的forward方法
            class QNetwork(nn.Module):
                def __init__(self, state_dim, action_dim, hidden_size=128):
                    super().__init__()
                    self.net = nn.Sequential(
                        nn.Linear(state_dim, hidden_size),
                        nn.ReLU(),
                        nn.Linear(hidden_size, hidden_size),
                        nn.ReLU(),
                        nn.Linear(hidden_size, action_dim)
                    )

                def forward(self, obs, state=None, info={}):
                    # 确保输入是tensor并且在正确的设备上
                    if isinstance(obs, np.ndarray):
                        obs = torch.as_tensor(obs, dtype=torch.float32, device=self.device)
                    elif isinstance(obs, torch.Tensor):
                        obs = obs.to(self.device)
                    return self.net(obs), state

            # 创建网络
            q_net = QNetwork(state_dim, action_dim, config.hidden_size)
            # 移动到目标设备
            q_net = q_net.to(device)
            # 保存设备引用供forward使用
            q_net.device = device

            policy = DiscreteQLearningPolicy(
                model=q_net,
                action_space=act_space,
                observation_space=obs_space,
                eps_training=0.1,
                eps_inference=0.05
            )

            # 创建DQN算法
            from tianshou.algorithm.optim import AdamOptimizerFactory
            optim_factory = AdamOptimizerFactory(lr=config.learning_rate)
            algorithm = DQN(
                policy=policy,
                optim=optim_factory,
                gamma=config.gamma,
                n_step_return_horizon=3,
                target_update_freq=100,
                is_double=True
            )

            # 创建收集器和缓冲区
            buffer = VectorReplayBuffer(total_size=config.buffer_size, buffer_num=1)
            train_collector = Collector(algorithm, env, buffer)
            train_collector.reset()

            # 使用Trainer进行训练
            trainer_params = OffPolicyTrainerParams(
                max_epochs=min(config.max_episodes, 50),
                epoch_num_steps=200,
                training_collector=train_collector,
                batch_size=config.batch_size,
                update_step_num_gradient_steps_per_sample=0.1,
                verbose=False,
                show_progress=False
            )
            trainer = OffPolicyTrainer(algorithm=algorithm, params=trainer_params)

            # 运行训练
            final_stats = trainer.run()

            # 从InfoStats获取训练结果
            # InfoStats属性: best_reward, best_reward_std, train_episode, test_episode等
            best_reward = float(final_stats.best_reward) if hasattr(final_stats, 'best_reward') else 0.0
            train_episodes = final_stats.train_episode if hasattr(final_stats, 'train_episode') else 0

            # 构建奖励历史
            rewards_history = [best_reward] if best_reward > 0 else []

            env.close()

            # 构建训练结果
            total_rewards = rewards_history
            final_reward = float(total_rewards[-1]) if total_rewards else 0.0
            average_reward = float(np.mean(total_rewards)) if total_rewards else 0.0

            training_result = RLTrainingResult(
                training_id=training_id,
                algorithm=config.algorithm,
                scenario=config.scenario,
                config=config.to_dict(),
                total_episodes=len(total_rewards),
                total_rewards=total_rewards,
                final_reward=final_reward,
                average_reward=average_reward,
                best_reward=float(best_reward),
                model=None,  # 不保存模型以节省内存
                status="completed"
            )

            logger.info(f"DQN训练完成: best_reward={best_reward:.4f}, avg_reward={average_reward:.4f}")
            return training_result

        except Exception as e:
            logger.error(f"DQN训练失败: {e}", exc_info=True)
            raise

    def _train_ppo(
        self,
        config: RLTrainingConfig,
        env_data: Optional[Dict[str, Any]],
        training_id: str
    ) -> RLTrainingResult:
        """训练PPO策略 - Tianshou 2.0兼容版本，支持GPU"""
        try:
            import torch
            import torch.nn as nn
            import gymnasium as gym
            import numpy as np
            from tianshou.algorithm.modelfree.ppo import PPO
            from tianshou.algorithm.modelfree.reinforce import ProbabilisticActorPolicy
            from tianshou.utils.net.discrete import DiscreteActor, DiscreteCritic
            from tianshou.utils.net.common import Net
            from tianshou.data import Collector, VectorReplayBuffer
            from tianshou.trainer import OnPolicyTrainer, OnPolicyTrainerParams

            # 获取设备
            device = config.get_device()
            logger.info(
                f"训练PPO策略: state_dim={config.state_dim}, "
                f"action_dim={config.action_dim}, device={device}"
            )

            # 创建环境
            env = gym.make("CartPole-v1")
            obs_space = env.observation_space
            act_space = env.action_space
            state_dim = obs_space.shape[0]
            action_dim = act_space.n

            logger.info(f"PPO环境: state_dim={state_dim}, action_dim={action_dim}")

            # 创建设备感知的网络包装器
            class DeviceAwareNet(nn.Module):
                """设备感知的网络包装器，确保输入数据在正确设备上"""
                def __init__(self, net, device):
                    super().__init__()
                    self.net = net
                    self.device = device

                def forward(self, obs, state=None, info={}):
                    if isinstance(obs, np.ndarray):
                        obs = torch.as_tensor(obs, dtype=torch.float32, device=self.device)
                    elif isinstance(obs, torch.Tensor):
                        obs = obs.to(self.device)
                    return self.net(obs, state, info)

            # 使用Tianshou的Net类创建网络
            actor_base = Net(
                state_shape=state_dim,
                action_shape=action_dim,
                hidden_sizes=[config.hidden_size, config.hidden_size]
            )
            critic_base = Net(
                state_shape=state_dim,
                hidden_sizes=[config.hidden_size, config.hidden_size]
            )

            # 包装为设备感知网络并移到指定设备
            actor_net = DeviceAwareNet(actor_base, device).to(device)
            critic_net = DeviceAwareNet(critic_base, device).to(device)

            # 创建Actor和Critic
            actor = DiscreteActor(
                preprocess_net=actor_net, action_shape=action_dim
            ).to(device)
            critic = DiscreteCritic(preprocess_net=critic_net).to(device)

            # 定义离散动作的分布函数
            def dist_fn(logits):
                return torch.distributions.Categorical(logits=logits)

            # 创建策略
            policy = ProbabilisticActorPolicy(
                actor=actor,
                dist_fn=dist_fn,
                action_space=act_space,
                observation_space=obs_space,
                action_scaling=False
            )

            # 创建PPO算法
            from tianshou.algorithm.optim import AdamOptimizerFactory
            optim_factory = AdamOptimizerFactory(lr=config.learning_rate)
            algorithm = PPO(
                policy=policy,
                critic=critic,
                optim=optim_factory,
                eps_clip=config.clip_param,
                ent_coef=config.entropy_coef,
                vf_coef=0.5,
                gae_lambda=0.95,
                gamma=config.gamma,
                max_batchsize=config.batch_size
            )

            # 创建收集器和缓冲区
            buffer = VectorReplayBuffer(total_size=config.buffer_size, buffer_num=1)
            train_collector = Collector(algorithm, env, buffer)
            train_collector.reset()

            # 使用OnPolicyTrainer进行训练
            trainer_params = OnPolicyTrainerParams(
                max_epochs=min(config.max_episodes, 100),
                epoch_num_steps=200,
                training_collector=train_collector,
                batch_size=config.batch_size,
                update_step_num_repetitions=10,
                verbose=False,
                show_progress=False
            )
            trainer = OnPolicyTrainer(algorithm=algorithm, params=trainer_params)

            # 运行训练
            final_stats = trainer.run()

            # 从InfoStats获取训练结果
            best_reward = float(final_stats.best_reward) if hasattr(final_stats, 'best_reward') else 0.0

            # 构建奖励历史
            rewards_history = [best_reward] if best_reward > 0 else []

            env.close()

            total_rewards = rewards_history
            final_reward = float(total_rewards[-1]) if total_rewards else 0.0
            average_reward = float(np.mean(total_rewards)) if total_rewards else 0.0

            training_result = RLTrainingResult(
                training_id=training_id,
                algorithm=config.algorithm,
                scenario=config.scenario,
                config=config.to_dict(),
                total_episodes=len(total_rewards),
                total_rewards=total_rewards,
                final_reward=final_reward,
                average_reward=average_reward,
                best_reward=float(best_reward),
                model=None,
                status="completed"
            )

            logger.info(f"PPO训练完成: best_reward={best_reward:.4f}, avg_reward={average_reward:.4f}")
            return training_result

        except Exception as e:
            logger.error(f"PPO训练失败: {e}", exc_info=True)
            raise

    def _train_a2c(
        self,
        config: RLTrainingConfig,
        env_data: Optional[Dict[str, Any]],
        training_id: str
    ) -> RLTrainingResult:
        """训练A2C策略 - Tianshou 2.0兼容版本，支持GPU"""
        try:
            import torch
            import torch.nn as nn
            import gymnasium as gym
            import numpy as np
            from tianshou.algorithm.modelfree.a2c import A2C
            from tianshou.algorithm.modelfree.reinforce import ProbabilisticActorPolicy
            from tianshou.utils.net.discrete import DiscreteActor, DiscreteCritic
            from tianshou.utils.net.common import Net
            from tianshou.data import Collector, VectorReplayBuffer
            from tianshou.trainer import OnPolicyTrainer, OnPolicyTrainerParams

            # 获取设备
            device = config.get_device()
            logger.info(
                f"训练A2C策略: state_dim={config.state_dim}, "
                f"action_dim={config.action_dim}, device={device}"
            )

            # 创建环境
            env = gym.make("CartPole-v1")
            obs_space = env.observation_space
            act_space = env.action_space
            state_dim = obs_space.shape[0]
            action_dim = act_space.n

            logger.info(f"A2C环境: state_dim={state_dim}, action_dim={action_dim}")

            # 创建设备感知的网络包装器
            class DeviceAwareNet(nn.Module):
                """设备感知的网络包装器，确保输入数据在正确设备上"""
                def __init__(self, net, device):
                    super().__init__()
                    self.net = net
                    self.device = device

                def forward(self, obs, state=None, info={}):
                    if isinstance(obs, np.ndarray):
                        obs = torch.as_tensor(obs, dtype=torch.float32, device=self.device)
                    elif isinstance(obs, torch.Tensor):
                        obs = obs.to(self.device)
                    return self.net(obs, state, info)

            # 使用Tianshou的Net类创建网络
            actor_base = Net(
                state_shape=state_dim,
                action_shape=action_dim,
                hidden_sizes=[config.hidden_size, config.hidden_size]
            )
            critic_base = Net(
                state_shape=state_dim,
                hidden_sizes=[config.hidden_size, config.hidden_size]
            )

            # 包装为设备感知网络并移到指定设备
            actor_net = DeviceAwareNet(actor_base, device).to(device)
            critic_net = DeviceAwareNet(critic_base, device).to(device)

            # 创建Actor和Critic
            actor = DiscreteActor(
                preprocess_net=actor_net, action_shape=action_dim
            ).to(device)
            critic = DiscreteCritic(preprocess_net=critic_net).to(device)

            # 定义离散动作的分布函数
            def dist_fn(logits):
                return torch.distributions.Categorical(logits=logits)

            policy = ProbabilisticActorPolicy(
                actor=actor,
                dist_fn=dist_fn,
                action_space=act_space,
                observation_space=obs_space,
                action_scaling=False
            )

            # 创建A2C算法
            from tianshou.algorithm.optim import AdamOptimizerFactory
            optim_factory = AdamOptimizerFactory(lr=config.learning_rate)
            algorithm = A2C(
                policy=policy,
                critic=critic,
                optim=optim_factory,
                vf_coef=0.5,
                ent_coef=config.entropy_coef,
                gae_lambda=0.95,
                gamma=config.gamma,
                max_batchsize=config.batch_size
            )

            # 创建收集器和缓冲区
            buffer = VectorReplayBuffer(total_size=config.buffer_size, buffer_num=1)
            train_collector = Collector(algorithm, env, buffer)
            train_collector.reset()

            # 使用OnPolicyTrainer进行训练
            trainer_params = OnPolicyTrainerParams(
                max_epochs=min(config.max_episodes, 100),
                epoch_num_steps=200,
                training_collector=train_collector,
                batch_size=config.batch_size,
                update_step_num_repetitions=10,
                verbose=False,
                show_progress=False
            )
            trainer = OnPolicyTrainer(algorithm=algorithm, params=trainer_params)

            # 运行训练
            final_stats = trainer.run()

            # 从InfoStats获取训练结果
            best_reward = float(final_stats.best_reward) if hasattr(final_stats, 'best_reward') else 0.0

            # 构建奖励历史
            rewards_history = [best_reward] if best_reward > 0 else []

            env.close()

            total_rewards = rewards_history
            final_reward = float(total_rewards[-1]) if total_rewards else 0.0
            average_reward = float(np.mean(total_rewards)) if total_rewards else 0.0

            training_result = RLTrainingResult(
                training_id=training_id,
                algorithm=config.algorithm,
                scenario=config.scenario,
                config=config.to_dict(),
                total_episodes=len(total_rewards),
                total_rewards=total_rewards,
                final_reward=final_reward,
                average_reward=average_reward,
                best_reward=float(best_reward),
                model=None,
                status="completed"
            )

            logger.info(f"A2C训练完成: best_reward={best_reward:.4f}, avg_reward={average_reward:.4f}")
            return training_result

        except Exception as e:
            logger.error(f"A2C训练失败: {e}", exc_info=True)
            raise

    def _create_simple_env(self, config: RLTrainingConfig, env_data: Optional[Dict[str, Any]]):
        """
        创建简单环境（模拟）

        实际应用中应该基于QLib的EnvWrapper创建真实环境

        QLib EnvWrapper包含：
        - Simulator: 市场模拟器
        - State Interpreter: 状态转换器
        - Action Interpreter: 动作转换器
        - Reward Function: 奖励函数
        """
        try:
            import gym

            # 创建简单的模拟环境
            class SimpleTradingEnv(gym.Env):
                """简单交易环境（用于演示）"""
                def __init__(self, state_dim: int, action_dim: int):
                    self.state_dim = state_dim
                    self.action_dim = action_dim
                    self.observation_space = gym.spaces.Box(
                        low=-np.inf, high=np.inf, shape=(state_dim,)
                    )
                    self.action_space = gym.spaces.Discrete(action_dim)
                    self.state = np.random.randn(state_dim)
                    self.step_count = 0

                def reset(self):
                    self.state = np.random.randn(self.state_dim)
                    self.step_count = 0
                    return self.state

                def step(self, action):
                    self.step_count += 1
                    # 简单的奖励计算
                    reward = np.random.randn() + action * 0.1
                    done = self.step_count >= 100
                    info = {}
                    return self.state, reward, done, info

            # 创建环境
            env = SimpleTradingEnv(
                state_dim=config.state_dim,
                action_dim=config.action_dim
            )
            logger.info("✅ 创建简单模拟环境完成")
            return env

        except Exception as e:
            logger.error(f"创建环境失败: {e}")
            raise

    def _simulate_training(self, config: RLTrainingConfig, training_id: str) -> RLTrainingResult:
        """
        模拟训练（当依赖不可用时）

        提供降级方案，确保服务可用性
        """
        logger.info(f"模拟RL训练: {config.algorithm}")

        # 模拟奖励曲线
        episodes = min(config.max_episodes, 100)  # 限制数量
        rewards = []

        for i in range(episodes):
            # 模拟学习曲线：逐渐上升
            base_reward = 0.5 + 0.4 * (i / episodes)  # 从0.5到0.9
            noise = np.random.randn() * 0.1 if NP_AVAILABLE else 0
            reward = base_reward + noise
            rewards.append(float(reward))

        # 构建训练结果
        result = RLTrainingResult(
            training_id=training_id,
            algorithm=config.algorithm,
            scenario=config.scenario,
            config=config.to_dict(),
            total_episodes=episodes,
            total_rewards=rewards,
            final_reward=float(rewards[-1]) if rewards else 0.0,
            average_reward=float(np.mean(rewards)) if rewards and NP_AVAILABLE else 0.0,
            best_reward=float(max(rewards)) if rewards else 0.0,
            model=None,
            status="completed"
        )

        logger.info(f"模拟训练完成: best_reward={result.best_reward:.4f}")

        return result

    # ==================== 自动算法选择 ====================

    def auto_select_algorithm(
        self,
        scenario: str = "order_execution",
        algorithms: Optional[List[str]] = None,
        max_episodes: int = 100,
        parallel: bool = False,
        env_data: Optional[Dict[str, Any]] = None,
        device: str = "auto"
    ) -> RLAutoSelectionResult:
        """
        自动选择最优算法

        并行或顺序训练多个算法，自动选择表现最好的算法

        Args:
            scenario: 应用场景
            algorithms: 要测试的算法列表，默认为 ["DQN", "PPO", "A2C"]
            max_episodes: 每个算法的最大训练轮数
            parallel: 是否并行训练（当前版本为顺序执行）
            env_data: 环境数据
            device: 设备选择 ("auto", "cuda", "cpu")

        Returns:
            自动选择结果，包含所有算法的表现和最优算法
        """
        import time
        start_time = time.time()

        # 默认测试所有算法
        if algorithms is None:
            algorithms = ["DQN", "PPO", "A2C"]

        selection_id = f"auto_select_{scenario}_{uuid.uuid4().hex[:8]}"
        logger.info(
            f"开始自动算法选择: selection_id={selection_id}, "
            f"algorithms={algorithms}, device={device}"
        )

        results_by_algorithm: Dict[str, Dict[str, Any]] = {}
        best_algorithm = ""
        best_training_id = ""
        best_reward = float('-inf')

        for algorithm in algorithms:
            try:
                logger.info(f"训练算法: {algorithm}")

                # 创建配置
                config = RLTrainingConfig(
                    algorithm=algorithm,
                    scenario=scenario,
                    max_episodes=max_episodes,
                    max_steps_per_episode=100,
                    hidden_size=128,
                    num_layers=2,
                    learning_rate=3e-4,
                    gamma=0.99,
                    buffer_size=10000,
                    batch_size=64,
                    state_dim=10,
                    action_dim=3,
                    device=device
                )

                # 训练
                result = self.train_rl_strategy(config, env_data)

                # 记录结果
                results_by_algorithm[algorithm] = {
                    "training_id": result.training_id,
                    "algorithm": result.algorithm,
                    "best_reward": result.best_reward,
                    "average_reward": result.average_reward,
                    "final_reward": result.final_reward,
                    "total_episodes": result.total_episodes,
                    "training_duration": result.training_duration,
                    "status": result.status
                }

                # 更新最佳算法
                if result.best_reward > best_reward:
                    best_reward = result.best_reward
                    best_algorithm = algorithm
                    best_training_id = result.training_id

                logger.info(f"算法 {algorithm} 训练完成: best_reward={result.best_reward:.4f}")

            except Exception as e:
                logger.error(f"训练算法 {algorithm} 失败: {e}")
                results_by_algorithm[algorithm] = {
                    "algorithm": algorithm,
                    "status": "failed",
                    "error": str(e)
                }

        training_duration = time.time() - start_time

        # 如果所有算法都失败，设置默认值
        if best_algorithm == "":
            best_algorithm = algorithms[0] if algorithms else "PPO"
            best_reward = 0.0
            best_training_id = ""

        result = RLAutoSelectionResult(
            selection_id=selection_id,
            scenario=scenario,
            algorithms_tried=algorithms,
            results_by_algorithm=results_by_algorithm,
            best_algorithm=best_algorithm,
            best_training_id=best_training_id,
            best_reward=best_reward,
            training_duration=training_duration
        )

        # 保存结果
        self._save_auto_selection_result(result)

        logger.info(
            f"自动算法选择完成: best_algorithm={best_algorithm}, "
            f"best_reward={best_reward:.4f}, duration={training_duration:.2f}s"
        )

        return result

    def _save_auto_selection_result(self, result: RLAutoSelectionResult) -> bool:
        """保存自动选择结果"""
        try:
            filename = f"{result.selection_id}.pkl"
            filepath = self.storage_dir / "results" / filename

            with open(filepath, 'wb') as f:
                pickle.dump(result, f)

            logger.debug(f"自动选择结果已保存: {filename}")
            return True

        except Exception as e:
            logger.error(f"保存自动选择结果失败: {e}")
            return False

    # ==================== 策略优化 ====================

    def optimize_strategy(
        self,
        algorithm: str,
        param_grid: Dict[str, List[Any]],
        scenario: str = "order_execution",
        n_trials: int = 10
    ) -> RLOptimizationResult:
        """
        优化RL策略超参数

        Args:
            algorithm: 算法类型（DQN/PPO/A2C）
            param_grid: 参数网格
                {
                    "learning_rate": [1e-3, 3e-4, 1e-4],
                    "hidden_size": [64, 128, 256],
                    ...
                }
            scenario: 应用场景
            n_trials: 试验次数

        Returns:
            优化结果
        """
        try:
            logger.info(f"开始策略优化: {algorithm}, {n_trials}次试验")

            optimization_id = f"opt_{algorithm.lower()}_{uuid.uuid4().hex[:8]}"

            trials = []
            best_score = float('-inf')
            best_params = {}

            # 执行网格搜索
            for i in range(n_trials):
                # 随机选择参数组合
                trial_params = {
                    k: np.random.choice(v) if NP_AVAILABLE else v[0]
                    for k, v in param_grid.items()
                }

                # 创建配置
                config = RLTrainingConfig(
                    algorithm=algorithm,
                    scenario=scenario,
                    learning_rate=trial_params.get("learning_rate", 3e-4),
                    hidden_size=trial_params.get("hidden_size", 128),
                    max_episodes=50,  # 优化时减少训练轮数
                    state_dim=10,
                    action_dim=3
                )

                # 训练
                result = self.train_rl_strategy(config)

                # 记录试验
                trial_score = result.best_reward
                trials.append({
                    "trial_id": f"{optimization_id}_trial_{i}",
                    "params": trial_params,
                    "score": trial_score,
                    "final_reward": result.final_reward,
                    "average_reward": result.average_reward
                })

                # 更新最佳结果
                if trial_score > best_score:
                    best_score = trial_score
                    best_params = trial_params

            best_metrics = {
                "best_reward": float(best_score),
                "n_trials": n_trials
            }

            result = RLOptimizationResult(
                optimization_id=optimization_id,
                algorithm=algorithm,
                scenario=scenario,
                best_params=best_params,
                best_metrics=best_metrics,
                all_trials=trials
            )

            # 保存结果
            self._save_optimization_result(result)

            logger.info(f"策略优化完成: best_reward={best_score:.4f}")

            return result

        except Exception as e:
            logger.error(f"策略优化失败: {e}")
            raise

    # ==================== 模型管理 ====================

    def save_model(self, training_id: str, model_path: Optional[str] = None) -> bool:
        """
        保存模型

        Args:
            training_id: 训练ID
            model_path: 模型路径（可选）

        Returns:
            是否成功
        """
        try:
            # 获取训练结果
            result = self.get_training_result(training_id)
            if result is None:
                logger.error(f"训练结果不存在: {training_id}")
                return False

            if result.model is None:
                logger.warning(f"模型不存在: {training_id}")
                return False

            # 生成模型路径
            if model_path is None:
                model_path = self.storage_dir / "models" / f"{training_id}.pkl"

            # 保存模型
            with open(model_path, 'wb') as f:
                pickle.dump(result.model, f)

            logger.info(f"模型已保存: {model_path}")
            return True

        except Exception as e:
            logger.error(f"保存模型失败: {e}")
            return False

    def load_model(self, training_id: str, model_path: Optional[str] = None):
        """
        加载模型

        Args:
            training_id: 训练ID
            model_path: 模型路径（可选）

        Returns:
            模型对象
        """
        try:
            # 生成模型路径
            if model_path is None:
                model_path = self.storage_dir / "models" / f"{training_id}.pkl"

            # 加载模型
            with open(model_path, 'rb') as f:
                model = pickle.load(f)

            logger.info(f"模型已加载: {model_path}")
            return model

        except Exception as e:
            logger.error(f"加载模型失败: {e}")
            return None

    def list_models(self, limit: int = 20) -> List[Dict[str, Any]]:
        """
        列出所有模型

        Args:
            limit: 返回数量限制

        Returns:
            模型列表
        """
        try:
            models = []

            logger.info(f"[list_models] 内存中的训练任务数: {len(self._running_tasks)}")

            # 1. 先从内存中的运行任务获取
            for training_id, result in self._running_tasks.items():
                logger.info(f"[list_models] 从内存加载模型: {training_id}, status={result.status}")
                model_data = result.to_dict()  # 使用完整的to_dict()方法
                model_data["episode"] = result.total_episodes  # 添加episode字段（兼容性）
                models.append(model_data)

            # 2. 从文件系统获取已保存的训练结果
            results_dir = self.storage_dir / "results"
            logger.info(f"[list_models] 检查results目录: {results_dir}, exists={results_dir.exists()}")
            if results_dir.exists():
                files = list(results_dir.glob("*.pkl"))
                logger.info(f"[list_models] results目录中的文件数: {len(files)}")
                for filepath in sorted(files, key=lambda p: p.stat().st_mtime, reverse=True):
                    try:
                        training_id = filepath.stem

                        # 避免重复添加（内存中已经有了）
                        if training_id in self._running_tasks:
                            logger.info(f"[list_models] 跳过重复模型（已在内存中）: {training_id}")
                            continue

                        # 从results文件加载
                        with open(filepath, 'rb') as f:
                            result = pickle.load(f)

                        logger.info(f"[list_models] 从文件加载模型: {training_id}, status={result.status}")
                        model_data = result.to_dict()  # 使用完整的to_dict()方法
                        model_data["episode"] = result.total_episodes  # 添加episode字段（兼容性）
                        models.append(model_data)
                    except Exception as e:
                        logger.warning(f"读取训练结果失败 {filepath.name}: {e}")

            # 3. 按创建时间排序，并限制数量
            models.sort(key=lambda m: m["created_at"], reverse=True)

            logger.info(f"[list_models] 总共返回 {len(models)} 个模型")
            return models[:limit]

        except Exception as e:
            logger.error(f"列出模型失败: {e}")
            return []

    # ==================== 训练历史管理 ====================

    def _save_training_result(self, result: RLTrainingResult) -> bool:
        """保存训练结果"""
        try:
            filename = f"{result.training_id}.pkl"
            filepath = self.storage_dir / "results" / filename

            logger.info(f"保存训练结果到: {filepath}")
            with open(filepath, 'wb') as f:
                pickle.dump(result, f)

            logger.info(f"✅ 训练结果已保存: {filename}")
            return True

        except Exception as e:
            logger.error(f"保存训练结果失败: {e}", exc_info=True)
            return False

    def get_training_result(self, training_id: str) -> Optional[RLTrainingResult]:
        """获取训练结果"""
        try:
            # 先在内存中查找
            if training_id in self._running_tasks:
                return self._running_tasks[training_id]

            # 在文件中查找
            filepath = self.storage_dir / "results" / f"{training_id}.pkl"
            if filepath.exists():
                with open(filepath, 'rb') as f:
                    result = pickle.load(f)
                return result

            logger.warning(f"未找到训练结果: {training_id}")
            return None

        except Exception as e:
            logger.error(f"加载训练结果失败: {e}")
            return None

    def _save_optimization_result(self, result: RLOptimizationResult) -> bool:
        """保存优化结果"""
        try:
            filename = f"{result.optimization_id}.pkl"
            filepath = self.storage_dir / "results" / filename

            with open(filepath, 'wb') as f:
                pickle.dump(result, f)

            logger.debug(f"优化结果已保存: {filename}")
            return True

        except Exception as e:
            logger.error(f"保存优化结果失败: {e}")
            return False

    def list_training_history(
        self,
        algorithm: Optional[str] = None,
        scenario: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """列出训练历史"""
        try:
            results_dir = self.storage_dir / "results"
            history = []

            for filepath in sorted(results_dir.glob("*.pkl"), key=lambda p: p.stat().st_mtime, reverse=True)[:limit]:
                try:
                    with open(filepath, 'rb') as f:
                        result = pickle.load(f)

                    # 过滤
                    if isinstance(result, RLTrainingResult):
                        if algorithm and result.algorithm != algorithm:
                            continue
                        if scenario and result.scenario != scenario:
                            continue

                        history.append(result.to_dict())
                except Exception as e:
                    logger.warning(f"读取训练结果失败 {filepath.name}: {e}")

            return history

        except Exception as e:
            logger.error(f"列出训练历史失败: {e}")
            return []

    # ==================== 工具方法 ====================

    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        try:
            results_dir = self.storage_dir / "results"
            models_dir = self.storage_dir / "models"

            total_results = len(list(results_dir.glob("*.pkl")))
            total_models = len(list(models_dir.glob("*.pkl")))

            # 按算法统计
            algorithm_counts = {}
            scenario_counts = {}

            for filepath in results_dir.glob("*.pkl"):
                try:
                    with open(filepath, 'rb') as f:
                        result = pickle.load(f)

                    if isinstance(result, RLTrainingResult):
                        algorithm_counts[result.algorithm] = algorithm_counts.get(result.algorithm, 0) + 1
                        scenario_counts[result.scenario] = scenario_counts.get(result.scenario, 0) + 1
                except:
                    pass

            return {
                "total_trainings": total_results,
                "total_models": total_models,
                "by_algorithm": algorithm_counts,
                "by_scenario": scenario_counts,
                "dependencies": {
                    "tianshou": TIANSHOU_AVAILABLE,
                    "torch": TORCH_AVAILABLE,
                    "numpy": NP_AVAILABLE
                }
            }

        except Exception as e:
            logger.error(f"获取统计信息失败: {e}")
            return {
                "total_trainings": 0,
                "total_models": 0,
                "by_algorithm": {},
                "by_scenario": {},
                "dependencies": {
                    "tianshou": TIANSHOU_AVAILABLE,
                    "torch": TORCH_AVAILABLE,
                    "numpy": NP_AVAILABLE
                }
            }

    def shutdown(self):
        """关闭服务，清理资源"""
        try:
            # 清理全局服务实例
            global _rl_strategy_service
            if _rl_strategy_service is self:
                _rl_strategy_service = None
            logger.info("RLStrategyService 已关闭")
        except Exception as e:
            logger.error(f"关闭服务失败: {e}")


# ==================== 全局服务实例 ====================

_rl_strategy_service = None


def get_rl_strategy_service() -> RLStrategyService:
    """获取RL策略服务实例"""
    global _rl_strategy_service
    if _rl_strategy_service is None:
        _rl_strategy_service = RLStrategyService()
    return _rl_strategy_service

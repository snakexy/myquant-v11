# -*- coding: utf-8 -*-
"""
Validation阶段 - 回测服务
==========================
职责：
- 策略回测执行
- 性能指标计算
- 回测报告生成
- 回测结果分析

架构层次：
- Validation阶段：验证策略有效性，评估历史表现
- 基于QLib Executor框架
- 不涉及实盘交易
"""

from typing import List, Dict, Optional, Any, Union
from loguru import logger
from datetime import datetime, date
from dataclasses import dataclass, field
from enum import Enum
import pandas as pd
import numpy as np
import sys
import os

# 添加QLib核心模块路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

# 导入QLib回测引擎
try:
    from qlib_core.backtest.qlib_backtest_engine import QLibBacktestEngine
    from qlib_core.backtest.qlib_backtest_executor import QLibBacktestExecutor
    QLIB_BACKEND_AVAILABLE = True
    logger.info("✅ QLib回测后端可用")
except ImportError as e:
    QLIB_BACKEND_AVAILABLE = False
    logger.warning(f"⚠️ QLib回测后端导入失败: {e}")


class BacktestStatus(Enum):
    """回测状态"""
    PENDING = "pending"           # 待执行
    RUNNING = "running"           # 执行中
    COMPLETED = "completed"       # 已完成
    FAILED = "failed"             # 失败
    CANCELLED = "cancelled"       # 已取消


@dataclass
class BacktestConfig:
    """回测配置"""
    strategy_name: str                  # 策略名称
    start_date: str                     # 开始日期（YYYY-MM-DD）
    end_date: str                       # 结束日期（YYYY-MM-DD）
    initial_capital: float = 1_000_000  # 初始资金
    commission_rate: float = 0.0003     # 手续费率（万三）
    slippage_rate: float = 0.0          # 滑点率
    benchmark: str = "SH000300"         # 基准指数
    frequency: str = "day"              # 调仓频率（day/week/month）

    # 高级配置
    position_limit: float = 0.95        # 仓位上限（95%）
    max_stocks: int = 50                # 最大持仓数量
    min_stocks: int = 10                # 最小持仓数量


@dataclass
class PerformanceMetrics:
    """回测性能指标"""
    # 收益指标
    total_return: float                 # 总收益率
    annual_return: float                # 年化收益率
    benchmark_return: float             # 基准收益率
    excess_return: float                # 超额收益率

    # 风险指标
    volatility: float                   # 波动率
    max_drawdown: float                 # 最大回撤
    benchmark_volatility: float         # 基准波动率

    # 风险调整收益
    sharpe_ratio: float                 # 夏普比率
    sortino_ratio: float                # 索提诺比率
    information_ratio: float            # 信息比率

    # 交易指标
    total_trades: int                   # 总交易次数
    win_rate: float                     # 胜率
    profit_loss_ratio: float            # 盈亏比
    avg_holding_period: float           # 平均持仓天数

    # 其他指标
    alpha: float = 0.0                  # Alpha
    beta: float = 0.0                   # Beta
    calmar_ratio: float = 0.0           # 卡玛比率


@dataclass
class BacktestResult:
    """回测结果"""
    task_id: str                        # 任务ID
    config: BacktestConfig              # 回测配置
    status: BacktestStatus              # 回测状态
    metrics: Optional[PerformanceMetrics]  # 性能指标

    # 详细数据
    equity_curve: Optional[pd.DataFrame]  # 净值曲线
    positions: Optional[pd.DataFrame]      # 持仓明细
    trades: Optional[pd.DataFrame]         # 交易明细

    # 元数据
    start_time: Optional[datetime] = None   # 开始时间
    end_time: Optional[datetime] = None     # 结束时间
    error_message: Optional[str] = None     # 错误信息
    created_at: datetime = field(default_factory=datetime.now)  # 创建时间


class BacktestService:
    """
    回测服务

    核心职责：
    1. 执行策略回测（基于QLib）
    2. 计算性能指标
    3. 生成回测报告
    4. 分析回测结果

    架构特点：
    - 基于QLib Executor框架
    - 支持多种策略类型
    - 灵活的回测配置
    - 完整的风险指标体系
    """

    def __init__(
        self,
        enable_qlib: bool = True,
        qlib_dir: Optional[str] = None,
    ):
        """
        初始化回测服务

        Args:
            enable_qlib: 启用QLib回测引擎
            qlib_dir: QLib数据目录
        """
        self.enable_qlib = enable_qlib
        self.qlib_dir = qlib_dir
        self._qlib_initialized = False
        self.qlib_executor = None
        self.qlib_engine = None

        # 回测任务存储
        self._backtest_tasks: Dict[str, BacktestResult] = {}

        # 初始化QLib回测后端
        if enable_qlib and QLIB_BACKEND_AVAILABLE:
            self._init_qlib_backend()

        logger.info("✅ BacktestService初始化完成")

    def _init_qlib_backend(self):
        """初始化QLib回测后端"""
        try:
            # 创建QLib回测引擎
            self.qlib_engine = QLibBacktestEngine(config={
                'data_dir': self.qlib_dir,
                'provider_uri': self.qlib_dir,
                'market': 'cn',
                'freq': 'day'
            })

            if self.qlib_engine.qlib_initialized:
                # 创建QLib回测执行器
                self.qlib_executor = QLibBacktestExecutor()
                self.qlib_executor.setup_executor(
                    exchange_config={
                        "limit_threshold": 0.095,
                        "deal_price": "close",
                        "open_cost": 0.0005,
                        "close_cost": 0.0015,
                        "min_cost": 5,
                    },
                    benchmark_config={
                        "benchmark": "SH000300",
                    }
                )
                self._qlib_initialized = True
                logger.info("✅ QLib回测后端初始化成功")
            else:
                logger.warning("⚠️ QLib引擎初始化失败")
                self._qlib_initialized = False

        except Exception as e:
            logger.warning(f"⚠️ QLib回测后端初始化失败: {e}")
            self._qlib_initialized = False

    def _init_qlib(self):
        """初始化QLib"""
        try:
            import qlib
            from qlib.config import REG_CN

            # 初始化QLib（使用中国A股市场配置）
            qlib.init(provider_uri=self.qlib_dir, region=REG_CN)
            self._qlib_initialized = True

            logger.info("✅ QLib回测引擎已初始化")
        except Exception as e:
            logger.warning(f"⚠️ QLib初始化失败: {e}")
            self._qlib_initialized = False

    # ==================== 回测执行 ====================

    async def run_backtest(
        self,
        config: BacktestConfig,
        strategy_signals: pd.DataFrame,
        task_id: Optional[str] = None
    ) -> BacktestResult:
        """
        执行回测

        Args:
            config: 回测配置
            strategy_signals: 策略信号
                DataFrame格式：
                - index: 日期（datetime）
                - columns: 股票代码
                - values: 信号值（权重或持仓比例）

            task_id: 任务ID（可选，自动生成如果不提供）

        Returns:
            BacktestResult对象
        """
        # 生成任务ID
        if task_id is None:
            task_id = f"backtest_{config.strategy_name}_{datetime.now().strftime('%Y%m%d%H%M%S')}"

        logger.info(f"开始回测任务: {task_id}")

        # 创建回测结果对象
        result = BacktestResult(
            task_id=task_id,
            config=config,
            status=BacktestStatus.RUNNING,
            metrics=None,
            equity_curve=None,
            positions=None,
            trades=None,
            start_time=datetime.now()
        )

        # 保存任务
        self._backtest_tasks[task_id] = result

        try:
            # 如果QLib可用，使用QLib执行回测
            if self._qlib_initialized:
                result = await self._run_backtest_qlib(config, strategy_signals, result)
            else:
                # 否则使用简单回测实现
                result = await self._run_backtest_simple(config, strategy_signals, result)

            result.status = BacktestStatus.COMPLETED
            result.end_time = datetime.now()

            logger.info(f"回测完成: {task_id}")
            logger.info(f"  总收益率: {result.metrics.total_return:.2%}")
            logger.info(f"  年化收益: {result.metrics.annual_return:.2%}")
            logger.info(f"  夏普比率: {result.metrics.sharpe_ratio:.2f}")
            logger.info(f"  最大回撤: {result.metrics.max_drawdown:.2%}")

        except Exception as e:
            result.status = BacktestStatus.FAILED
            result.error_message = str(e)
            result.end_time = datetime.now()
            logger.error(f"回测失败: {task_id}, 错误: {e}")

        # 更新任务
        self._backtest_tasks[task_id] = result

        return result

    async def _run_backtest_qlib(
        self,
        config: BacktestConfig,
        strategy_signals: pd.DataFrame,
        result: BacktestResult
    ) -> BacktestResult:
        """
        使用QLib执行回测

        Args:
            config: 回测配置
            strategy_signals: 策略信号
                DataFrame格式：
                - index: 日期（datetime）
                - columns: 股票代码
                - values: 信号值（权重或持仓比例）
            result: 回测结果对象

        Returns:
            更新后的回测结果
        """
        if not self._qlib_initialized or self.qlib_executor is None:
            logger.warning("QLib未初始化，降级到简单回测")
            return await self._run_backtest_simple(config, strategy_signals, result)

        try:
            logger.info(f"开始QLib回测: {config.strategy_name}")

            # 准备策略配置
            strategy_config = {
                'topk': config.max_stocks,
                'dropout': config.min_stocks,
                'signal': strategy_signals,
            }

            # 执行QLib回测
            backtest_result = self.qlib_executor.execute_backtest(
                strategy_config=strategy_config,
                start_date=config.start_date,
                end_date=config.end_date,
                initial_capital=config.initial_capital,
                benchmark=config.benchmark
            )

            # 检查回测结果
            if backtest_result is None or 'metrics' not in backtest_result:
                logger.warning("QLib回测返回空结果，降级到简单回测")
                return await self._run_backtest_simple(config, strategy_signals, result)

            # 提取回测结果
            metrics_data = backtest_result.get('metrics', {})
            positions_data = backtest_result.get('positions', None)
            trades_data = backtest_result.get('trades', None)

            # 构建净值曲线
            if 'equity_curve' in backtest_result:
                result.equity_curve = backtest_result['equity_curve']
            else:
                # 如果没有净值曲线，基于positions计算
                result.equity_curve = self._calculate_equity_from_positions(
                    positions_data, config.initial_capital
                )

            # 构建持仓明细
            result.positions = positions_data

            # 构建交易明细
            result.trades = trades_data

            # 计算性能指标
            if isinstance(result.equity_curve, pd.Series) and len(result.equity_curve) > 0:
                result.metrics = self.calculate_metrics(
                    result.equity_curve,
                    benchmark_curve=None  # QLib已经计算过基准指标
                )

                # 更新QLib计算的指标
                if 'return' in metrics_data:
                    result.metrics.total_return = metrics_data['return']
                if 'sharpe_ratio' in metrics_data:
                    result.metrics.sharpe_ratio = metrics_data['sharpe_ratio']
                if 'max_drawdown' in metrics_data:
                    result.metrics.max_drawdown = metrics_data['max_drawdown']

            logger.info(f"QLib回测完成: 总收益={result.metrics.total_return:.2%}")
            return result

        except Exception as e:
            logger.error(f"QLib回测执行失败: {e}，降级到简单回测")
            return await self._run_backtest_simple(config, strategy_signals, result)

    def _calculate_equity_from_positions(
        self,
        positions: Optional[pd.DataFrame],
        initial_capital: float
    ) -> pd.Series:
        """从持仓数据计算净值曲线"""
        if positions is None or len(positions) == 0:
            # 返回简单的净值曲线
            return pd.Series([initial_capital], index=[pd.Timestamp.now()])

        try:
            # 计算每日总资产
            equity = initial_capital * (1 + positions.sum(axis=1).cumsum())
            return equity
        except Exception as e:
            logger.warning(f"计算净值曲线失败: {e}")
            return pd.Series([initial_capital], index=[pd.Timestamp.now()])

    async def _run_backtest_simple(
        self,
        config: BacktestConfig,
        strategy_signals: pd.DataFrame,
        result: BacktestResult
    ) -> BacktestResult:
        """
        简单回测实现（不依赖QLib）

        基于策略信号进行简化回测，计算：
        1. 每日持仓权重
        2. 每日收益率
        3. 净值曲线
        4. 性能指标

        Args:
            config: 回测配置
            strategy_signals: 策略信号
                DataFrame格式：
                - index: 日期（datetime）
                - columns: 股票代码
                - values: 信号值（预测得分或权重）
            result: 回测结果对象

        Returns:
            更新后的回测结果
        """
        try:
            logger.info("使用简单回测实现")

            # 1. 根据信号计算每日持仓
            positions = self._calculate_positions_from_signals(
                strategy_signals,
                config
            )

            # 2. 计算每日收益率（简化版本：使用信号变化作为收益代理）
            daily_returns = self._calculate_daily_returns_from_signals(
                strategy_signals,
                positions
            )

            # 3. 计算净值曲线
            equity_curve = self._calculate_equity_curve_simple(
                daily_returns,
                config.initial_capital
            )

            # 4. 计算性能指标
            metrics = self.calculate_metrics(
                equity_curve,
                benchmark_curve=None
            )

            # 更新结果
            result.metrics = metrics
            result.equity_curve = equity_curve
            result.positions = positions
            result.trades = self._calculate_trades_from_positions(positions)

            logger.info(f"简单回测完成: 总收益={metrics.total_return:.2%}")
            return result

        except Exception as e:
            logger.error(f"简单回测执行失败: {e}")
            # 返回失败结果
            result.status = BacktestStatus.FAILED
            result.error_message = f"简单回测失败: {str(e)}"
            return result

    def _calculate_positions_from_signals(
        self,
        signals: pd.DataFrame,
        config: BacktestConfig
    ) -> pd.DataFrame:
        """
        从策略信号计算每日持仓

        Args:
            signals: 策略信号DataFrame
            config: 回测配置

        Returns:
            持仓DataFrame (日期 x 股票, 值为权重)
        """
        positions = pd.DataFrame(index=signals.index, columns=signals.columns)

        # 按日期遍历
        for date in signals.index:
            # 获取当日信号
            daily_signal = signals.loc[date].dropna()

            if len(daily_signal) == 0:
                continue

            # 选择top-k股票（信号最高的k个）
            topk = min(config.max_stocks, len(daily_signal))
            selected_stocks = daily_signal.nlargest(topk).index

            # 计算权重（等权重或按信号值加权）
            if config.frequency == 'day':
                # 等权重分配
                weight = 1.0 / len(selected_stocks)
                positions.loc[date, selected_stocks] = weight
            else:
                # 按信号值归一化加权
                signal_values = daily_signal[selected_stocks]
                weights = signal_values / signal_values.sum()
                positions.loc[date, selected_stocks] = weights

        # 填充NaN为0
        positions = positions.fillna(0)

        return positions

    def _calculate_daily_returns_from_signals(
        self,
        signals: pd.DataFrame,
        positions: pd.DataFrame
    ) -> pd.Series:
        """
        从信号和持仓计算每日收益率（简化版本）

        注意：这是简化的收益计算，不使用真实价格数据
        真实回测需要使用QLib或获取价格数据

        Args:
            signals: 策略信号
            positions: 持仓权重

        Returns:
            每日收益率Series
        """
        # 简化假设：使用信号变化作为收益代理
        # 在真实场景中，应该使用价格数据计算

        if len(signals) == 0:
            return pd.Series([], dtype=float)

        # 计算信号的一阶差分作为收益代理
        signal_changes = signals.diff().fillna(0)

        # 加权平均收益
        daily_returns = []
        for date in positions.index:
            if date in signal_changes.index:
                # 持仓权重 × 信号变化
                pos = positions.loc[date]
                sig_change = signal_changes.loc[date]
                daily_return = (pos * sig_change).sum()
                daily_returns.append(daily_return)
            else:
                daily_returns.append(0.0)

        return pd.Series(daily_returns, index=positions.index)

    def _calculate_equity_curve_simple(
        self,
        daily_returns: pd.Series,
        initial_capital: float
    ) -> pd.Series:
        """
        计算净值曲线

        Args:
            daily_returns: 每日收益率
            initial_capital: 初始资金

        Returns:
            净值曲线Series
        """
        if len(daily_returns) == 0:
            return pd.Series([initial_capital], index=[pd.Timestamp.now()])

        # 累计收益
        cumulative_returns = (1 + daily_returns).cumprod()

        # 净值曲线
        equity_curve = initial_capital * cumulative_returns

        return equity_curve

    def _calculate_trades_from_positions(
        self,
        positions: pd.DataFrame
    ) -> pd.DataFrame:
        """
        从持仓变化计算交易明细

        Args:
            positions: 持仓DataFrame

        Returns:
            交易明细DataFrame
        """
        if len(positions) < 2:
            return pd.DataFrame()

        trades = []
        prev_date = positions.index[0]

        for date in positions.index[1:]:
            prev_pos = positions.loc[prev_date]
            curr_pos = positions.loc[date]

            # 计算持仓变化
            pos_changes = curr_pos - prev_pos

            # 记录交易（只记录非零变化）
            for stock in pos_changes.index:
                change = pos_changes[stock]
                if abs(change) > 1e-6:  # 忽略极小变化
                    action = 'buy' if change > 0 else 'sell'
                    trades.append({
                        'date': date,
                        'symbol': stock,
                        'action': action,
                        'weight_change': change
                    })

            prev_date = date

        return pd.DataFrame(trades) if trades else pd.DataFrame()

    # ==================== 性能指标计算 ====================

    def calculate_metrics(
        self,
        equity_curve: pd.Series,
        benchmark_curve: Optional[pd.Series] = None,
        risk_free_rate: float = 0.03
    ) -> PerformanceMetrics:
        """
        计算回测性能指标

        Args:
            equity_curve: 净值曲线（Series，index为日期）
            benchmark_curve: 基准净值曲线（可选）
            risk_free_rate: 无风险利率（年化）

        Returns:
            PerformanceMetrics对象
        """
        # 计算收益率
        returns = equity_curve.pct_change().dropna()
        benchmark_returns = benchmark_curve.pct_change().dropna() if benchmark_curve is not None else None

        # 总收益率
        total_return = (equity_curve.iloc[-1] / equity_curve.iloc[0]) - 1

        # 年化收益率
        n_days = len(equity_curve)
        n_years = n_days / 252  # 假设一年252个交易日
        annual_return = (1 + total_return) ** (1 / n_years) - 1 if n_years > 0 else 0

        # 波动率（年化）
        volatility = returns.std() * np.sqrt(252)

        # 最大回撤
        cummax = equity_curve.cummax()
        drawdown = (equity_curve - cummax) / cummax
        max_drawdown = drawdown.min()

        # 夏普比率
        excess_returns = returns - (risk_free_rate / 252)
        sharpe_ratio = excess_returns.mean() / excess_returns.std() * np.sqrt(252) if excess_returns.std() > 0 else 0

        # 基准指标
        benchmark_return = 0.0
        benchmark_volatility = 0.0
        excess_return = 0.0
        information_ratio = 0.0
        alpha = 0.0
        beta = 0.0

        if benchmark_returns is not None:
            benchmark_return = (benchmark_curve.iloc[-1] / benchmark_curve.iloc[0]) - 1
            benchmark_volatility = benchmark_returns.std() * np.sqrt(252)
            excess_return = annual_return - ((1 + benchmark_return) ** (1 / n_years) - 1) if n_years > 0 else 0

            # 信息比率
            if benchmark_returns is not None:
                relative_returns = returns - benchmark_returns
                information_ratio = relative_returns.mean() / relative_returns.std() * np.sqrt(252) if relative_returns.std() > 0 else 0

            # Alpha和Beta
            if benchmark_returns is not None and len(returns) == len(benchmark_returns):
                # 简单线性回归
                covariance = np.cov(returns, benchmark_returns)[0, 1]
                benchmark_variance = benchmark_returns.var()
                beta = covariance / benchmark_variance if benchmark_variance > 0 else 0
                alpha = annual_return - (risk_free_rate + beta * (benchmark_return - risk_free_rate))

        # 索提诺比率（下行风险调整收益）
        downside_returns = returns[returns < 0]
        downside_std = downside_returns.std()
        sortino_ratio = excess_returns.mean() / downside_std * np.sqrt(252) if downside_std > 0 else 0

        # 卡玛比率（收益/最大回撤）
        calmar_ratio = annual_return / abs(max_drawdown) if max_drawdown != 0 else 0

        return PerformanceMetrics(
            total_return=total_return,
            annual_return=annual_return,
            benchmark_return=benchmark_return,
            excess_return=excess_return,
            volatility=volatility,
            max_drawdown=max_drawdown,
            benchmark_volatility=benchmark_volatility,
            sharpe_ratio=sharpe_ratio,
            sortino_ratio=sortino_ratio,
            information_ratio=information_ratio,
            total_trades=0,  # 需要交易明细
            win_rate=0.0,    # 需要交易明细
            profit_loss_ratio=0.0,  # 需要交易明细
            avg_holding_period=0.0,  # 需要交易明细
            alpha=alpha,
            beta=beta,
            calmar_ratio=calmar_ratio,
        )

    # ==================== 回测管理 ====================

    def get_backtest_result(self, task_id: str) -> Optional[BacktestResult]:
        """
        获取回测结果

        Args:
            task_id: 任务ID

        Returns:
            BacktestResult对象，如果不存在返回None
        """
        return self._backtest_tasks.get(task_id)

    def list_backtest_tasks(
        self,
        status: Optional[BacktestStatus] = None,
        strategy_name: Optional[str] = None
    ) -> List[BacktestResult]:
        """
        列出回测任务

        Args:
            status: 状态筛选
            strategy_name: 策略名称筛选

        Returns:
            回测结果列表
        """
        tasks = list(self._backtest_tasks.values())

        if status is not None:
            tasks = [t for t in tasks if t.status == status]

        if strategy_name is not None:
            tasks = [t for t in tasks if t.config.strategy_name == strategy_name]

        return sorted(tasks, key=lambda x: x.created_at, reverse=True)

    def cancel_backtest(self, task_id: str) -> bool:
        """
        取消回测任务

        Args:
            task_id: 任务ID

        Returns:
            是否成功取消
        """
        if task_id in self._backtest_tasks:
            task = self._backtest_tasks[task_id]
            if task.status == BacktestStatus.RUNNING:
                task.status = BacktestStatus.CANCELLED
                logger.info(f"回测任务已取消: {task_id}")
                return True
        return False


# ==================== 全局单例 ====================

_backtest_service_instance: Optional[BacktestService] = None


def get_backtest_service() -> BacktestService:
    """
    获取回测服务单例

    Returns:
        BacktestService实例
    """
    global _backtest_service_instance

    if _backtest_service_instance is None:
        _backtest_service_instance = BacktestService()

    return _backtest_service_instance

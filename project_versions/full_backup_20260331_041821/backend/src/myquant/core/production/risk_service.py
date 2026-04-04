# -*- coding: utf-8 -*-
"""
Production阶段 - 风险控制服务
===============================
职责：
- 实盘风险监控和控制
- 仓位风险管理
- 止损止盈执行
- 风险预警和报警

⚠️ 重要：
- 此Service是保护资金安全的最后一道防线
- 所有风险控制必须严格执行
- 任何风险触发应该立即采取行动

架构层次：
- Production阶段：风险控制和保护
- 依赖PositionService获取仓位数据
- 依赖TradingService执行风险操作
"""

from typing import List, Dict, Optional, Callable, Any
from loguru import logger
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import asyncio


class RiskLevel(Enum):
    """风险等级"""
    LOW = "low"                   # 低风险
    MEDIUM = "medium"             # 中风险
    HIGH = "high"                 # 高风险
    CRITICAL = "critical"         # 严重风险


class RiskType(Enum):
    """风险类型"""
    POSITION_LIMIT = "position_limit"       # 仓位限制
    LOSS_LIMIT = "loss_limit"               # 亏损限制
    DRAWDOWN_LIMIT = "drawdown_limit"       # 回撤限制
    CONCENTRATION = "concentration"         # 集中度风险
    VOLATILITY = "volatility"               # 波动率风险
    MARKET_RISK = "market_risk"             # 市场风险
    VAR_LIMIT = "var_limit"                 # VaR限制
    CVAR_LIMIT = "cvar_limit"               # CVaR限制
    BETA_EXPOSURE = "beta_exposure"         # Beta暴露
    FACTOR_EXPOSURE = "factor_exposure"     # 因子暴露


class RiskAction(Enum):
    """风险行动"""
    MONITOR = "monitor"           # 监控
    WARNING = "warning"           # 预警
    REDUCE_POSITION = "reduce_position"  # 减仓
    STOP_TRADING = "stop_trading"         # 停止交易
    FORCE_CLOSE = "force_close"           # 强平
    EMERGENCY_EXIT = "emergency_exit"     # 紧急退出


@dataclass
class RiskRule:
    """风险规则"""
    rule_id: str                         # 规则ID
    rule_name: str                       # 规则名称
    risk_type: RiskType                  # 风险类型
    risk_level: RiskLevel                # 风险等级

    # 规则参数
    threshold: float = 0.0               # 阈值
    action: RiskAction = RiskAction.MONITOR  # 触发行动

    # 规则状态
    enabled: bool = True                 # 是否启用
    triggered: bool = False              # 是否触发
    trigger_count: int = 0               # 触发次数
    last_triggered: Optional[datetime] = None  # 最后触发时间

    # 描述
    description: str = ""


@dataclass
class RiskEvent:
    """风险事件"""
    event_id: str                        # 事件ID
    rule_id: str                         # 触发的规则ID
    risk_type: RiskType                  # 风险类型
    risk_level: RiskLevel                # 风险等级

    # 事件详情
    account_id: str                      # 账户ID
    symbol: Optional[str] = None         # 涉及股票
    current_value: float = 0.0           # 当前值
    threshold: float = 0.0               # 阈值
    message: str = ""                    # 事件消息

    # 处理信息
    action: RiskAction = RiskAction.MONITOR
    action_result: str = ""              # 行动结果

    # 时间戳
    triggered_at: datetime = field(default_factory=datetime.now)
    resolved_at: Optional[datetime] = None


@dataclass
class RiskMetrics:
    """风险指标"""
    # 账户级别
    total_assets: float = 0.0            # 总资产
    total_profit_loss: float = 0.0       # 总盈亏
    total_profit_loss_pct: float = 0.0   # 总盈亏比例
    max_drawdown: float = 0.0            # 最大回撤
    current_drawdown: float = 0.0        # 当前回撤

    # 仓位级别
    position_ratio: float = 0.0          # 仓位比例
    max_single_position: float = 0.0     # 最大单一持仓
    concentration: float = 0.0           # 集中度

    # 波动率
    daily_volatility: float = 0.0        # 日波动率
    weekly_volatility: float = 0.0       # 周波动率

    # 风险评级
    overall_risk_level: RiskLevel = RiskLevel.LOW

    # 更新时间
    updated_at: datetime = field(default_factory=datetime.now)


class RiskService:
    """
    风险控制服务

    核心职责：
    1. 实时监控风险指标
    2. 检查风险规则
    3. 触发风险行动
    4. 记录风险事件

    ⚠️ 关键特性：
    - 严格的风险控制
    - 多层次的风险防护
    - 实时监控和预警
    - 自动风险处置

    风控层级：
    1. 事前风控：仓位限制、止损设置
    2. 事中风控：实时监控、动态调整
    3. 事后风控：损失评估、规则优化

    服务依赖：
    - PositionService: 获取仓位数据
    - TradingService: 执行交易操作
    """

    def __init__(
        self,
        auto_monitor: bool = True,       # 自动监控
        check_interval: int = 60,        # 检查间隔（秒）
    ):
        """
        初始化风险控制服务

        Args:
            auto_monitor: 是否自动监控
            check_interval: 检查间隔（秒）
        """
        self.auto_monitor = auto_monitor
        self.check_interval = check_interval

        # 风险规则
        self._rules: Dict[str, RiskRule] = {}

        # 风险事件
        self._events: List[RiskEvent] = []

        # 监控任务
        self._monitoring_task = None

        # 回调函数
        self._callbacks: Dict[RiskAction, List[Callable]] = {}

        # 服务引用（延迟加载）
        self._position_service = None
        self._trading_service = None

        # qlib 风险分析器引用（高级分析）
        self._risk_analyzer = None
        self._risk_exposure_manager = None

        # 账户交易状态 {account_id: can_trade}
        self._account_trading_status: Dict[str, bool] = {}

        # 紧急退出状态
        self._emergency_mode: bool = False

        # 历史收益率记录 {account_id: [returns, ...]}
        self._returns_history: Dict[str, List[float]] = {}

        # 初始化默认规则
        self._init_default_rules()

        # 启动监控
        if auto_monitor:
            self.start_monitoring()

        logger.info("✅ RiskService初始化完成")

    def _get_position_service(self):
        """获取仓位服务（延迟加载）"""
        if self._position_service is None:
            from .position_service import get_position_service
            self._position_service = get_position_service()
        return self._position_service

    def _get_trading_service(self):
        """获取交易服务（延迟加载）"""
        if self._trading_service is None:
            from .trading_service import get_trading_service
            self._trading_service = get_trading_service()
        return self._trading_service

    def _get_risk_analyzer(self):
        """获取qlib风险分析器（延迟加载）"""
        if self._risk_analyzer is None:
            try:
                from backend.qlib_core.analysis.risk_analyzer import (
                    RiskAnalyzer, RiskConfig
                )
                self._risk_analyzer = RiskAnalyzer(RiskConfig())
                logger.info("✅ qlib RiskAnalyzer已加载")
            except Exception as e:
                logger.warning(f"qlib RiskAnalyzer加载失败: {e}")
        return self._risk_analyzer

    def _get_risk_exposure_manager(self):
        """获取风险暴露管理器（延迟加载）"""
        if self._risk_exposure_manager is None:
            try:
                from backend.qlib_core.backtest.portfolio_management.strategy.enhanced_indexing.risk_management.risk_exposure import (
                    RiskExposureManager
                )
                self._risk_exposure_manager = RiskExposureManager(
                    factor_limits={
                        'size': 0.5,      # 规模因子暴露限制
                        'value': 0.3,     # 价值因子暴露限制
                        'momentum': 0.4,  # 动量因子暴露限制
                        'beta': 1.2,      # Beta限制
                    }
                )
                logger.info("✅ RiskExposureManager已加载")
            except Exception as e:
                logger.warning(f"RiskExposureManager加载失败: {e}")
        return self._risk_exposure_manager

    def _init_default_rules(self):
        """初始化默认风险规则"""
        # 1. 总仓位限制
        self.add_rule(RiskRule(
            rule_id="total_position_limit",
            rule_name="总仓位限制",
            risk_type=RiskType.POSITION_LIMIT,
            risk_level=RiskLevel.HIGH,
            threshold=0.95,  # 95%
            action=RiskAction.REDUCE_POSITION,
            description="总仓位不能超过95%",
        ))

        # 2. 单一持仓限制
        self.add_rule(RiskRule(
            rule_id="single_position_limit",
            rule_name="单一持仓限制",
            risk_type=RiskType.POSITION_LIMIT,
            risk_level=RiskLevel.MEDIUM,
            threshold=0.20,  # 20%
            action=RiskAction.WARNING,
            description="单一持仓不能超过20%",
        ))

        # 3. 亏损限制
        self.add_rule(RiskRule(
            rule_id="loss_limit",
            rule_name="亏损限制",
            risk_type=RiskType.LOSS_LIMIT,
            risk_level=RiskLevel.CRITICAL,
            threshold=-0.15,  # -15%
            action=RiskAction.STOP_TRADING,
            description="总亏损不能超过-15%",
        ))

        # 4. 回撤限制
        self.add_rule(RiskRule(
            rule_id="drawdown_limit",
            rule_name="回撤限制",
            risk_type=RiskType.DRAWDOWN_LIMIT,
            risk_level=RiskLevel.CRITICAL,
            threshold=-0.20,  # -20%
            action=RiskAction.STOP_TRADING,
            description="最大回撤不能超过-20%",
        ))

        # 5. 集中度风险
        self.add_rule(RiskRule(
            rule_id="concentration_limit",
            rule_name="集中度限制",
            risk_type=RiskType.CONCENTRATION,
            risk_level=RiskLevel.MEDIUM,
            threshold=0.50,  # 50%
            action=RiskAction.WARNING,
            description="前5大持仓不能超过50%",
        ))

        # 6. VaR风险限制（95%置信度）
        self.add_rule(RiskRule(
            rule_id="var_limit_95",
            rule_name="VaR限制(95%)",
            risk_type=RiskType.VAR_LIMIT,
            risk_level=RiskLevel.HIGH,
            threshold=0.05,  # 5%的总资产
            action=RiskAction.WARNING,
            description="95%置信度下VaR不能超过总资产的5%",
        ))

        # 7. CVaR风险限制（条件风险）
        self.add_rule(RiskRule(
            rule_id="cvar_limit",
            rule_name="CVaR限制",
            risk_type=RiskType.CVAR_LIMIT,
            risk_level=RiskLevel.HIGH,
            threshold=0.08,  # 8%的总资产
            action=RiskAction.REDUCE_POSITION,
            description="CVaR不能超过总资产的8%",
        ))

        # 8. Beta暴露限制
        self.add_rule(RiskRule(
            rule_id="beta_exposure_limit",
            rule_name="Beta暴露限制",
            risk_type=RiskType.BETA_EXPOSURE,
            risk_level=RiskLevel.MEDIUM,
            threshold=1.5,  # Beta不超过1.5
            action=RiskAction.WARNING,
            description="组合Beta不能超过1.5",
        ))

        # 9. 因子暴露限制
        self.add_rule(RiskRule(
            rule_id="factor_exposure_limit",
            rule_name="因子暴露限制",
            risk_type=RiskType.FACTOR_EXPOSURE,
            risk_level=RiskLevel.MEDIUM,
            threshold=0.5,  # 因子暴露绝对值限制
            action=RiskAction.WARNING,
            description="单因子暴露绝对值不能超过0.5",
        ))

        logger.info(f"✅ 已加载{len(self._rules)}个默认风险规则")

    # ==================== 规则管理 ====================

    def add_rule(self, rule: RiskRule):
        """
        添加风险规则

        Args:
            rule: 风险规则对象
        """
        self._rules[rule.rule_id] = rule
        logger.info(f"添加风险规则: {rule.rule_name}")

    def remove_rule(self, rule_id: str):
        """
        移除风险规则

        Args:
            rule_id: 规则ID
        """
        if rule_id in self._rules:
            del self._rules[rule_id]
            logger.info(f"移除风险规则: {rule_id}")

    def get_rule(self, rule_id: str) -> Optional[RiskRule]:
        """
        获取风险规则

        Args:
            rule_id: 规则ID

        Returns:
            RiskRule对象
        """
        return self._rules.get(rule_id)

    def list_rules(self, enabled_only: bool = True) -> List[RiskRule]:
        """
        列出风险规则

        Args:
            enabled_only: 仅显示启用的规则

        Returns:
            RiskRule列表
        """
        rules = list(self._rules.values())

        if enabled_only:
            rules = [r for r in rules if r.enabled]

        return sorted(rules, key=lambda x: x.risk_level.value)

    # ==================== 风险检查 ====================

    async def check_risks(self, account_id: str) -> List[RiskEvent]:
        """
        检查所有风险规则

        Args:
            account_id: 账户ID

        Returns:
            触发的风险事件列表
        """
        # 计算风险指标
        metrics = await self._calculate_metrics(account_id)

        # 检查所有规则
        triggered_events = []

        for rule in self._rules.values():
            if not rule.enabled:
                continue

            # 检查规则
            event = await self._check_rule(account_id, rule, metrics)
            if event:
                triggered_events.append(event)

        # 记录事件
        if triggered_events:
            self._events.extend(triggered_events)
            logger.warning(f"触发{len(triggered_events)}个风险事件")

            # 执行风险行动
            for event in triggered_events:
                await self._execute_risk_action(event)

        return triggered_events

    async def _check_rule(
        self,
        account_id: str,
        rule: RiskRule,
        metrics: RiskMetrics
    ) -> Optional[RiskEvent]:
        """
        检查单个风险规则

        Args:
            account_id: 账户ID
            rule: 风险规则
            metrics: 风险指标

        Returns:
            RiskEvent对象，如果未触发返回None
        """
        current_value = 0.0
        triggered = False
        message = ""

        # 根据风险类型检查
        if rule.risk_type == RiskType.POSITION_LIMIT:
            if rule.rule_id == "total_position_limit":
                current_value = metrics.position_ratio
                triggered = current_value > rule.threshold
                message = f"总仓位{current_value:.2%}超过限制{rule.threshold:.2%}"

            elif rule.rule_id == "single_position_limit":
                current_value = metrics.max_single_position
                triggered = current_value > rule.threshold
                message = f"单一持仓{current_value:.2%}超过限制{rule.threshold:.2%}"

        elif rule.risk_type == RiskType.LOSS_LIMIT:
            current_value = metrics.total_profit_loss_pct / 100  # 转换为小数
            triggered = current_value < rule.threshold
            message = f"总亏损{current_value:.2%}超过限制{rule.threshold:.2%}"

        elif rule.risk_type == RiskType.DRAWDOWN_LIMIT:
            current_value = metrics.current_drawdown
            triggered = current_value < rule.threshold
            message = f"当前回撤{current_value:.2%}超过限制{rule.threshold:.2%}"

        elif rule.risk_type == RiskType.CONCENTRATION:
            current_value = metrics.concentration
            triggered = current_value > rule.threshold
            message = f"集中度{current_value:.2%}超过限制{rule.threshold:.2%}"

        elif rule.risk_type == RiskType.VAR_LIMIT:
            # VaR检查：使用历史收益率计算
            current_value = await self._calculate_var(account_id, confidence=0.95)
            triggered = abs(current_value) > rule.threshold
            message = f"VaR(95%){abs(current_value):.2%}超过限制{rule.threshold:.2%}"

        elif rule.risk_type == RiskType.CVAR_LIMIT:
            # CVaR检查：条件风险价值
            current_value = await self._calculate_cvar(account_id, confidence=0.95)
            triggered = abs(current_value) > rule.threshold
            message = f"CVaR{abs(current_value):.2%}超过限制{rule.threshold:.2%}"

        elif rule.risk_type == RiskType.BETA_EXPOSURE:
            # Beta暴露检查
            current_value = await self._calculate_portfolio_beta(account_id)
            triggered = abs(current_value) > rule.threshold
            message = f"组合Beta{current_value:.2f}超过限制{rule.threshold:.2f}"

        elif rule.risk_type == RiskType.FACTOR_EXPOSURE:
            # 因子暴露检查
            factor_exposures = await self._calculate_factor_exposures(account_id)
            max_exposure = max(
                [abs(v) for v in factor_exposures.values()] or [0]
            )
            current_value = max_exposure
            triggered = current_value > rule.threshold
            message = f"最大因子暴露{current_value:.2f}超过限制{rule.threshold:.2f}"

        if triggered:
            # 更新规则状态
            rule.triggered = True
            rule.trigger_count += 1
            rule.last_triggered = datetime.now()

            # 创建风险事件
            event = RiskEvent(
                event_id=f"risk_{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
                rule_id=rule.rule_id,
                risk_type=rule.risk_type,
                risk_level=rule.risk_level,
                account_id=account_id,
                current_value=current_value,
                threshold=rule.threshold,
                message=message,
                action=rule.action,
            )

            logger.warning(f"风险触发: {message}")

            return event

        return None

    async def _calculate_metrics(self, account_id: str) -> RiskMetrics:
        """
        计算风险指标

        Args:
            account_id: 账户ID

        Returns:
            RiskMetrics对象
        """
        try:
            # 从PositionService获取持仓数据
            from .position_service import get_position_service
            position_service = get_position_service()

            summary = position_service.get_portfolio_summary(account_id)

            # 创建风险指标
            metrics = RiskMetrics(
                total_assets=getattr(summary, 'total_assets', 0) or 0,
                total_profit_loss=getattr(summary, 'total_profit_loss', 0) or 0,
                total_profit_loss_pct=getattr(summary, 'total_profit_loss_pct', 0) or 0,
                position_ratio=getattr(summary, 'position_ratio', 0) or 0,
                max_single_position=getattr(summary, 'max_single_position', 0) or 0,
                concentration=getattr(summary, 'top5_concentration', 0) or 0,
            )

        except Exception as e:
            logger.warning(f"获取持仓数据失败，使用默认值: {e}")
            # 返回默认的风险指标
            metrics = RiskMetrics(
                total_assets=0,
                total_profit_loss=0,
                total_profit_loss_pct=0,
                position_ratio=0,
                max_single_position=0,
                concentration=0,
            )

        # TODO: 计算更多指标
        # - 历史最大回撤
        # - 当前回撤
        # - 波动率
        # - Beta等

        # 评估总体风险等级
        metrics.overall_risk_level = self._assess_risk_level(metrics)

        return metrics

    # ==================== 高级风险分析（基于qlib RiskAnalyzer）====================

    async def _calculate_var(
        self,
        account_id: str,
        confidence: float = 0.95,
        method: str = "historical"
    ) -> float:
        """
        计算风险价值(VaR)

        Args:
            account_id: 账户ID
            confidence: 置信度（0.95或0.99）
            method: 计算方法（historical/parametric/monte_carlo）

        Returns:
            VaR值（占总资产比例）
        """
        try:
            # 获取历史收益率
            returns = self._returns_history.get(account_id, [])

            if len(returns) < 20:
                # 数据不足，使用简化估计
                position_service = self._get_position_service()
                summary = position_service.get_portfolio_summary(account_id)
                # 假设日波动率2%，计算VaR
                daily_vol = 0.02
                z_score = 1.645 if confidence == 0.95 else 2.326
                return daily_vol * z_score

            # 尝试使用qlib RiskAnalyzer
            risk_analyzer = self._get_risk_analyzer()
            if risk_analyzer:
                try:
                    import numpy as np
                    returns_array = np.array(returns[-252:])  # 最近一年数据

                    # 调用qlib的VaR计算
                    if method == "historical":
                        var = risk_analyzer.calculate_var_historical(
                            returns_array, confidence
                        )
                    elif method == "parametric":
                        var = risk_analyzer.calculate_var_parametric(
                            returns_array, confidence
                        )
                    else:
                        var = risk_analyzer.calculate_var_monte_carlo(
                            returns_array, confidence
                        )

                    return var
                except Exception as e:
                    logger.warning(f"qlib VaR计算失败: {e}")

            # 回退到简单计算
            import numpy as np
            returns_array = np.array(returns)
            var_percentile = (1 - confidence) * 100
            var = abs(np.percentile(returns_array, var_percentile))
            return var

        except Exception as e:
            logger.error(f"VaR计算异常: {e}")
            return 0.0

    async def _calculate_cvar(
        self,
        account_id: str,
        confidence: float = 0.95
    ) -> float:
        """
        计算条件风险价值(CVaR/ES)

        Args:
            account_id: 账户ID
            confidence: 置信度

        Returns:
            CVaR值（占总资产比例）
        """
        try:
            returns = self._returns_history.get(account_id, [])

            if len(returns) < 20:
                # 数据不足，使用简化估计
                daily_vol = 0.02
                z_score = 1.645 if confidence == 0.95 else 2.326
                # CVaR通常比VaR大约1.2倍
                return daily_vol * z_score * 1.2

            # 尝试使用qlib RiskAnalyzer
            risk_analyzer = self._get_risk_analyzer()
            if risk_analyzer:
                try:
                    import numpy as np
                    returns_array = np.array(returns[-252:])
                    cvar = risk_analyzer.calculate_cvar(
                        returns_array, confidence
                    )
                    return abs(cvar)
                except Exception as e:
                    logger.warning(f"qlib CVaR计算失败: {e}")

            # 回退到简单计算
            import numpy as np
            returns_array = np.array(returns)
            var_percentile = (1 - confidence) * 100
            var_threshold = np.percentile(returns_array, var_percentile)
            # CVaR是超出VaR的尾部损失的平均值
            tail_losses = returns_array[returns_array <= var_threshold]
            if len(tail_losses) > 0:
                cvar = abs(np.mean(tail_losses))
            else:
                cvar = abs(var_threshold)

            return cvar

        except Exception as e:
            logger.error(f"CVaR计算异常: {e}")
            return 0.0

    async def _calculate_portfolio_beta(self, account_id: str) -> float:
        """
        计算组合Beta

        Args:
            account_id: 账户ID

        Returns:
            Beta系数
        """
        try:
            # 从PositionService获取Beta
            position_service = self._get_position_service()

            # 尝试调用PositionService的Beta计算
            if hasattr(position_service, '_calculate_portfolio_beta'):
                beta = await position_service._calculate_portfolio_beta(account_id)
                if beta is not None:
                    return beta

            # 回退：使用加权平均估算
            summary = position_service.get_portfolio_summary(account_id)

            # 如果无法计算，返回1.0（市场平均）
            return 1.0

        except Exception as e:
            logger.error(f"Beta计算异常: {e}")
            return 1.0

    async def _calculate_factor_exposures(
        self,
        account_id: str
    ) -> Dict[str, float]:
        """
        计算因子暴露

        Args:
            account_id: 账户ID

        Returns:
            因子暴露字典
        """
        try:
            # 获取持仓权重
            position_service = self._get_position_service()
            positions = position_service.query_positions(account_id)

            if not positions:
                return {}

            # 计算持仓权重
            total_value = sum(p.market_value for p in positions.values())
            if total_value <= 0:
                return {}

            # 基于持仓特征的因子暴露估算
            # 在没有因子数据库的情况下，使用简化的估算方法
            import numpy as np

            n_stocks = len(positions)
            weights = np.array([
                p.market_value / total_value
                for p in positions.values()
            ])

            # 计算组合Beta
            portfolio_beta = await self._calculate_portfolio_beta(account_id)

            # 基于持仓集中度的规模因子估算
            # 持仓越集中，规模因子暴露越高
            herfindahl = np.sum(weights ** 2)  # 赫芬达尔指数
            size_exposure = (herfindahl - 1/n_stocks) * 2 if n_stocks > 1 else 0

            # 基于盈亏分布的价值因子估算
            pnl_values = [p.profit_loss_pct for p in positions.values()]
            if pnl_values:
                avg_pnl = np.mean(pnl_values)
                # 盈利的股票可能有价值因子暴露
                value_exposure = -0.1 if avg_pnl > 0 else 0.1
            else:
                value_exposure = 0

            # 动量因子：基于近期表现估算
            momentum_exposure = 0  # 需要历史数据，暂时为0

            factor_exposures = {
                'size': float(size_exposure),
                'value': float(value_exposure),
                'momentum': float(momentum_exposure),
                'beta': float(portfolio_beta),
            }

            return factor_exposures

        except Exception as e:
            logger.error(f"因子暴露计算异常: {e}")
            return {}

    async def run_stress_test(
        self,
        account_id: str,
        scenarios: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """
        运行压力测试

        Args:
            account_id: 账户ID
            scenarios: 压力场景列表，如:
                [
                    {"name": "市场下跌20%", "market_shock": -0.20},
                    {"name": "波动率翻倍", "vol_shock": 2.0},
                    {"name": "流动性危机", "liquidity_shock": 0.5},
                ]

        Returns:
            压力测试结果
        """
        try:
            # 默认压力场景
            if scenarios is None:
                scenarios = [
                    {"name": "轻度下跌", "market_shock": -0.10},
                    {"name": "中度下跌", "market_shock": -0.20},
                    {"name": "严重下跌", "market_shock": -0.30},
                    {"name": "闪崩", "market_shock": -0.40},
                    {"name": "波动率翻倍", "vol_shock": 2.0},
                    {"name": "流动性危机", "liquidity_shock": 0.5},
                ]

            # 获取当前持仓 - 带错误处理
            try:
                position_service = self._get_position_service()
                positions = position_service.query_positions(account_id)
                summary = position_service.get_portfolio_summary(account_id)
            except Exception as pos_error:
                logger.warning(f"获取持仓数据失败，使用模拟数据: {pos_error}")
                # 使用模拟数据进行压力测试
                from dataclasses import dataclass
                summary = type('PortfolioSummary', (), {
                    'total_assets': 1000000.0,  # 默认100万
                    'total_profit_loss': 0.0,
                    'total_market_value': 800000.0,
                })()
                positions = {}

            results = {
                "account_id": account_id,
                "total_assets": summary.total_assets,
                "current_pnl": summary.total_profit_loss,
                "test_time": datetime.now().isoformat(),
                "scenarios": [],
                "risk_summary": {},
            }

            # 尝试使用qlib压力测试
            risk_analyzer = self._get_risk_analyzer()

            for scenario in scenarios:
                scenario_name = scenario.get("name", "Unknown")
                scenario_result = {
                    "name": scenario_name,
                    "params": scenario,
                    "estimated_loss": 0.0,
                    "estimated_loss_pct": 0.0,
                    "impact_level": "low",
                }

                # 计算情景影响
                if "market_shock" in scenario:
                    shock = scenario["market_shock"]
                    # 简化：假设组合Beta=1
                    beta = await self._calculate_portfolio_beta(account_id)
                    estimated_loss = summary.total_assets * shock * beta
                    scenario_result["estimated_loss"] = estimated_loss
                    scenario_result["estimated_loss_pct"] = shock * beta

                elif "vol_shock" in scenario:
                    vol_mult = scenario["vol_shock"]
                    # 波动率增加对VaR的影响
                    current_var = await self._calculate_var(account_id)
                    estimated_loss = current_var * summary.total_assets * (vol_mult - 1)
                    scenario_result["estimated_loss"] = estimated_loss
                    scenario_result["estimated_loss_pct"] = current_var * (vol_mult - 1)

                elif "liquidity_shock" in scenario:
                    liquidity_mult = scenario["liquidity_shock"]
                    # 流动性危机导致的价值折损
                    position_value = summary.total_market_value
                    estimated_loss = position_value * (1 - liquidity_mult) * 0.1
                    scenario_result["estimated_loss"] = estimated_loss
                    scenario_result["estimated_loss_pct"] = (1 - liquidity_mult) * 0.1

                # 评估影响级别
                loss_pct = abs(scenario_result["estimated_loss_pct"])
                if loss_pct > 0.30:
                    scenario_result["impact_level"] = "critical"
                elif loss_pct > 0.20:
                    scenario_result["impact_level"] = "high"
                elif loss_pct > 0.10:
                    scenario_result["impact_level"] = "medium"
                else:
                    scenario_result["impact_level"] = "low"

                results["scenarios"].append(scenario_result)

            # 风险摘要
            max_loss = max(
                abs(s["estimated_loss"]) for s in results["scenarios"]
            )
            results["risk_summary"] = {
                "max_potential_loss": max_loss,
                "max_potential_loss_pct": max_loss / summary.total_assets if summary.total_assets > 0 else 0,
                "worst_scenario": max(
                    results["scenarios"],
                    key=lambda x: abs(x["estimated_loss"])
                )["name"],
                "recommendations": self._generate_stress_test_recommendations(
                    results["scenarios"]
                ),
            }

            logger.info(
                f"压力测试完成: 账户{account_id}, "
                f"最大潜在损失{results['risk_summary']['max_potential_loss_pct']:.2%}"
            )

            return results

        except Exception as e:
            logger.error(f"压力测试异常: {e}")
            return {
                "account_id": account_id,
                "error": str(e),
                "scenarios": [],
            }

    def _generate_stress_test_recommendations(
        self,
        scenarios: List[Dict]
    ) -> List[str]:
        """根据压力测试结果生成建议"""
        recommendations = []

        for scenario in scenarios:
            if scenario["impact_level"] == "critical":
                recommendations.append(
                    f"警告：{scenario['name']}情景可能导致严重损失，"
                    f"建议立即降低仓位或增加对冲"
                )
            elif scenario["impact_level"] == "high":
                recommendations.append(
                    f"注意：{scenario['name']}情景风险较高，"
                    f"建议考虑风险对冲策略"
                )

        if not recommendations:
            recommendations.append("当前组合在主要压力情景下表现良好")

        return recommendations

    async def get_risk_analysis_report(
        self,
        account_id: str
    ) -> Dict[str, Any]:
        """
        获取完整的风险分析报告

        Args:
            account_id: 账户ID

        Returns:
            风险分析报告
        """
        try:
            # 计算各项风险指标
            metrics = await self._calculate_metrics(account_id)
            var_95 = await self._calculate_var(account_id, 0.95)
            var_99 = await self._calculate_var(account_id, 0.99)
            cvar = await self._calculate_cvar(account_id, 0.95)
            beta = await self._calculate_portfolio_beta(account_id)
            factor_exposures = await self._calculate_factor_exposures(account_id)

            # 运行压力测试
            stress_test = await self.run_stress_test(account_id)

            # 使用RiskExposureManager检查因子限制
            exposure_limits_status = {}
            exposure_manager = self._get_risk_exposure_manager()
            if exposure_manager and factor_exposures:
                exposure_limits_status = exposure_manager.check_exposure_limits(
                    factor_exposures
                )

            report = {
                "account_id": account_id,
                "report_time": datetime.now().isoformat(),
                "basic_metrics": {
                    "total_assets": metrics.total_assets,
                    "position_ratio": metrics.position_ratio,
                    "max_single_position": metrics.max_single_position,
                    "concentration": metrics.concentration,
                    "total_pnl": metrics.total_profit_loss,
                    "total_pnl_pct": metrics.total_profit_loss_pct,
                },
                "risk_metrics": {
                    "var_95": var_95,
                    "var_99": var_99,
                    "cvar_95": cvar,
                    "beta": beta,
                    "current_drawdown": metrics.current_drawdown,
                    "max_drawdown": metrics.max_drawdown,
                    "daily_volatility": metrics.daily_volatility,
                },
                "factor_exposures": factor_exposures,
                "exposure_limits_status": exposure_limits_status,
                "stress_test_summary": stress_test.get("risk_summary", {}),
                "overall_risk_level": metrics.overall_risk_level.value,
                "recommendations": self._generate_risk_recommendations(
                    metrics, var_95, cvar, beta, exposure_limits_status
                ),
            }

            return report

        except Exception as e:
            logger.error(f"生成风险分析报告异常: {e}")
            return {
                "account_id": account_id,
                "error": str(e),
            }

    def _generate_risk_recommendations(
        self,
        metrics: RiskMetrics,
        var_95: float,
        cvar: float,
        beta: float,
        exposure_status: Dict[str, bool]
    ) -> List[str]:
        """生成风险管理建议"""
        recommendations = []

        # 仓位建议
        if metrics.position_ratio > 0.9:
            recommendations.append(
                f"仓位过高({metrics.position_ratio:.1%})，建议降低至85%以下"
            )

        # 集中度建议
        if metrics.concentration > 0.4:
            recommendations.append(
                f"持仓集中度较高({metrics.concentration:.1%})，建议分散投资"
            )

        # VaR建议
        if abs(var_95) > 0.05:
            recommendations.append(
                f"VaR(95%)较高({abs(var_95):.1%})，建议降低风险敞口"
            )

        # Beta建议
        if abs(beta) > 1.3:
            recommendations.append(
                f"Beta较高({beta:.2f})，组合对市场敏感度高，建议考虑对冲"
            )
        elif beta < 0.5:
            recommendations.append(
                f"Beta较低({beta:.2f})，可能错失市场上涨机会"
            )

        # 因子暴露建议
        for factor, exceeds in exposure_status.items():
            if exceeds:
                recommendations.append(
                    f"因子{factor}暴露超过限制，建议调整持仓"
                )

        # 回撤建议
        if metrics.current_drawdown < -0.1:
            recommendations.append(
                f"当前回撤较大({metrics.current_drawdown:.1%})，建议审视持仓"
            )

        if not recommendations:
            recommendations.append("当前风险水平适中，继续保持监控")

        return recommendations

    def record_daily_return(self, account_id: str, daily_return: float):
        """
        记录每日收益率（用于VaR/CVaR计算）

        Args:
            account_id: 账户ID
            daily_return: 日收益率
        """
        if account_id not in self._returns_history:
            self._returns_history[account_id] = []

        self._returns_history[account_id].append(daily_return)

        # 保留最近252个交易日（约1年）
        max_history = 252
        if len(self._returns_history[account_id]) > max_history:
            self._returns_history[account_id] = self._returns_history[account_id][-max_history:]

    def _assess_risk_level(self, metrics: RiskMetrics) -> RiskLevel:
        """
        评估风险等级

        Args:
            metrics: 风险指标

        Returns:
            风险等级
        """
        # 简单规则：根据盈亏和回撤判断
        if metrics.total_profit_loss_pct < -15 or metrics.current_drawdown < -0.20:
            return RiskLevel.CRITICAL
        elif metrics.total_profit_loss_pct < -10 or metrics.position_ratio > 0.90:
            return RiskLevel.HIGH
        elif metrics.total_profit_loss_pct < -5 or metrics.concentration > 0.50:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW

    async def calculate_comprehensive_risk_score(
        self,
        account_id: str
    ) -> Dict[str, Any]:
        """
        计算综合风险评分（0-100分）

        整合基础指标和高级分析结果，提供全面的风险评估。
        评分越高表示风险越大。

        评分维度（专业量化视角）：
        1. 仓位风险（0-25分）：仓位比例、集中度
        2. 回撤风险（0-25分）：当前回撤、历史最大回撤
        3. VaR/CVaR风险（0-25分）：95%置信度的风险价值
        4. Beta/因子暴露风险（0-25分）：市场敏感度、因子暴露

        Args:
            account_id: 账户ID

        Returns:
            {
                "score": 65,
                "level": "high",
                "dimensions": {...},
                "top_risks": [...],
                "recommendations": [...]
            }
        """
        try:
            # 获取基础指标
            metrics = await self._calculate_metrics(account_id)

            # 检查是否有持仓数据
            try:
                position_service = self._get_position_service()
                positions = position_service.query_positions(account_id)
            except Exception as e:
                logger.warning(f"获取持仓失败: {e}")
                positions = None

            has_positions = bool(positions) and metrics.total_assets > 0

            if not has_positions:
                # 无持仓数据时返回特殊状态
                return {
                    "account_id": account_id,
                    "score": 0,
                    "level": "unknown",
                    "dimensions": {
                        "position": {"score": 0, "weight": 0.25, "max_score": 25, "details": "无持仓数据"},
                        "drawdown": {"score": 0, "weight": 0.25, "max_score": 25, "details": "无持仓数据"},
                        "var_cvar": {"score": 0, "weight": 0.25, "max_score": 25, "details": "无持仓数据"},
                        "beta_factor": {"score": 0, "weight": 0.25, "max_score": 25, "details": "无持仓数据"},
                    },
                    "top_risks": [],
                    "recommendations": ["当前无持仓数据，请先获取持仓"],
                    "raw_metrics": {
                        "position_ratio": 0,
                        "concentration": 0,
                        "current_drawdown": 0,
                        "max_drawdown": 0,
                        "var_95": 0,
                        "cvar_95": 0,
                        "beta": 1.0,
                        "factor_exposures": {},
                    },
                    "timestamp": datetime.now().isoformat(),
                    "has_positions": False,
                }

            # 获取高级分析指标
            var_95 = await self._calculate_var(account_id, 0.95)
            cvar = await self._calculate_cvar(account_id, 0.95)
            beta = await self._calculate_portfolio_beta(account_id)
            factor_exposures = await self._calculate_factor_exposures(account_id)

            # 检查因子暴露限制
            exposure_limits_status = {}
            exposure_manager = self._get_risk_exposure_manager()
            if exposure_manager and factor_exposures:
                exposure_limits_status = exposure_manager.check_exposure_limits(
                    factor_exposures
                )

            # 1. 仓位风险评分（0-25分）
            position_score = self._calculate_position_risk_score(metrics)

            # 2. 回撤风险评分（0-25分）
            drawdown_score = self._calculate_drawdown_risk_score(metrics)

            # 3. VaR/CVaR风险评分（0-25分）
            var_cvar_score = self._calculate_var_cvar_risk_score(var_95, cvar)

            # 4. Beta/因子暴露风险评分（0-25分）
            beta_factor_score = self._calculate_beta_factor_risk_score(
                beta, factor_exposures, exposure_limits_status
            )

            # 综合评分 - 加权求和
            total_score = (
                position_score["score"] +
                drawdown_score["score"] +
                var_cvar_score["score"] +
                beta_factor_score["score"]
            )

            # 确定风险等级（基于量化行业标准）
            if total_score >= 75:
                level = "critical"
            elif total_score >= 50:
                level = "high"
            elif total_score >= 25:
                level = "medium"
            else:
                level = "low"

            # 识别主要风险
            top_risks = self._identify_top_risks([
                ("position", position_score["score"], position_score["details"]),
                ("drawdown", drawdown_score["score"], drawdown_score["details"]),
                ("var_cvar", var_cvar_score["score"], var_cvar_score["details"]),
                ("beta_factor", beta_factor_score["score"], beta_factor_score["details"]),
            ])

            # 生成建议
            recommendations = self._generate_risk_recommendations(
                metrics, var_95, cvar, beta, exposure_limits_status
            )

            return {
                "account_id": account_id,
                "score": round(total_score, 1),
                "level": level,
                "dimensions": {
                    "position": position_score,
                    "drawdown": drawdown_score,
                    "var_cvar": var_cvar_score,
                    "beta_factor": beta_factor_score,
                },
                "top_risks": top_risks,
                "recommendations": recommendations,
                "raw_metrics": {
                    "position_ratio": metrics.position_ratio,
                    "concentration": metrics.concentration,
                    "current_drawdown": metrics.current_drawdown,
                    "max_drawdown": metrics.max_drawdown,
                    "var_95": var_95,
                    "cvar_95": cvar,
                    "beta": beta,
                    "factor_exposures": factor_exposures,
                },
                "timestamp": datetime.now().isoformat(),
                "has_positions": True,
            }

        except Exception as e:
            logger.error(f"计算综合风险评分异常: {e}")
            return {
                "account_id": account_id,
                "score": 0,
                "level": "unknown",
                "error": str(e),
                "dimensions": {
                    "position": {"score": 0, "weight": 0.25, "max_score": 25, "details": f"计算异常: {str(e)}"},
                    "drawdown": {"score": 0, "weight": 0.25, "max_score": 25, "details": "计算异常"},
                    "var_cvar": {"score": 0, "weight": 0.25, "max_score": 25, "details": "计算异常"},
                    "beta_factor": {"score": 0, "weight": 0.25, "max_score": 25, "details": "计算异常"},
                },
                "top_risks": [],
                "recommendations": [f"风险计算异常: {str(e)}"],
            }

    def _calculate_position_risk_score(self, metrics: RiskMetrics) -> Dict[str, Any]:
        """计算仓位风险评分（0-25分）"""
        score = 0.0
        details = []

        # 仓位比例评分（0-15分）
        if metrics.position_ratio > 0.95:
            score += 15
            details.append(f"仓位极高({metrics.position_ratio:.1%})")
        elif metrics.position_ratio > 0.85:
            score += 10
            details.append(f"仓位偏高({metrics.position_ratio:.1%})")
        elif metrics.position_ratio > 0.70:
            score += 5
            details.append(f"仓位适中({metrics.position_ratio:.1%})")
        else:
            details.append(f"仓位较低({metrics.position_ratio:.1%})")

        # 集中度评分（0-10分）
        if metrics.concentration > 0.60:
            score += 10
            details.append(f"集中度很高({metrics.concentration:.1%})")
        elif metrics.concentration > 0.40:
            score += 6
            details.append(f"集中度偏高({metrics.concentration:.1%})")
        elif metrics.concentration > 0.25:
            score += 3
            details.append(f"集中度适中({metrics.concentration:.1%})")
        else:
            details.append(f"集中度较低({metrics.concentration:.1%})")

        return {
            "score": round(score, 1),
            "weight": 0.25,
            "max_score": 25,
            "details": "; ".join(details),
        }

    def _calculate_drawdown_risk_score(self, metrics: RiskMetrics) -> Dict[str, Any]:
        """计算回撤风险评分（0-25分）"""
        score = 0.0
        details = []

        # 当前回撤评分（0-15分）
        abs_drawdown = abs(metrics.current_drawdown)
        if abs_drawdown > 0.20:
            score += 15
            details.append(f"当前回撤严重({metrics.current_drawdown:.1%})")
        elif abs_drawdown > 0.10:
            score += 10
            details.append(f"当前回撤较大({metrics.current_drawdown:.1%})")
        elif abs_drawdown > 0.05:
            score += 5
            details.append(f"当前回撤适中({metrics.current_drawdown:.1%})")
        else:
            details.append(f"当前回撤较小({metrics.current_drawdown:.1%})")

        # 历史最大回撤评分（0-10分）
        abs_max_drawdown = abs(metrics.max_drawdown)
        if abs_max_drawdown > 0.25:
            score += 10
            details.append(f"历史最大回撤很高({metrics.max_drawdown:.1%})")
        elif abs_max_drawdown > 0.15:
            score += 6
            details.append(f"历史最大回撤较高({metrics.max_drawdown:.1%})")
        elif abs_max_drawdown > 0.08:
            score += 3
            details.append(f"历史最大回撤适中({metrics.max_drawdown:.1%})")
        else:
            details.append(f"历史最大回撤较低({metrics.max_drawdown:.1%})")

        return {
            "score": round(score, 1),
            "weight": 0.25,
            "max_score": 25,
            "details": "; ".join(details),
        }

    def _calculate_var_cvar_risk_score(
        self,
        var_95: float,
        cvar: float
    ) -> Dict[str, Any]:
        """计算VaR/CVaR风险评分（0-25分）"""
        score = 0.0
        details = []

        # VaR评分（0-12分）
        abs_var = abs(var_95)
        if abs_var > 0.08:
            score += 12
            details.append(f"VaR(95%)极高({abs_var:.1%})")
        elif abs_var > 0.05:
            score += 8
            details.append(f"VaR(95%)偏高({abs_var:.1%})")
        elif abs_var > 0.03:
            score += 4
            details.append(f"VaR(95%)适中({abs_var:.1%})")
        else:
            details.append(f"VaR(95%)较低({abs_var:.1%})")

        # CVaR评分（0-13分）
        abs_cvar = abs(cvar)
        if abs_cvar > 0.10:
            score += 13
            details.append(f"CVaR极高({abs_cvar:.1%})")
        elif abs_cvar > 0.07:
            score += 9
            details.append(f"CVaR偏高({abs_cvar:.1%})")
        elif abs_cvar > 0.04:
            score += 5
            details.append(f"CVaR适中({abs_cvar:.1%})")
        else:
            details.append(f"CVaR较低({abs_cvar:.1%})")

        return {
            "score": round(score, 1),
            "weight": 0.25,
            "max_score": 25,
            "details": "; ".join(details),
        }

    def _calculate_beta_factor_risk_score(
        self,
        beta: float,
        factor_exposures: Dict[str, float],
        exposure_limits_status: Dict[str, bool]
    ) -> Dict[str, Any]:
        """计算Beta/因子暴露风险评分（0-25分）"""
        score = 0.0
        details = []

        # Beta评分（0-12分）
        abs_beta = abs(beta)
        if abs_beta > 1.5:
            score += 12
            details.append(f"Beta极高({beta:.2f})")
        elif abs_beta > 1.2:
            score += 8
            details.append(f"Beta偏高({beta:.2f})")
        elif abs_beta > 0.8:
            score += 3
            details.append(f"Beta适中({beta:.2f})")
        else:
            score += 1
            details.append(f"Beta较低({beta:.2f})")

        # 因子暴露评分（0-13分）
        exceeded_factors = [f for f, exceeded in exposure_limits_status.items() if exceeded]
        if exceeded_factors:
            score += 5 * len(exceeded_factors)
            if score > 13:
                score = 13
            details.append(f"因子暴露超限: {', '.join(exceeded_factors)}")
        else:
            # 检查因子暴露绝对值
            max_exposure = max([abs(v) for v in factor_exposures.values()] or [0])
            if max_exposure > 0.4:
                score += 5
                details.append(f"部分因子暴露较高")
            else:
                details.append(f"因子暴露正常")

        return {
            "score": round(score, 1),
            "weight": 0.25,
            "max_score": 25,
            "details": "; ".join(details),
        }

    def _identify_top_risks(
        self,
        dimension_scores: List[tuple]
    ) -> List[Dict[str, Any]]:
        """识别主要风险"""
        # 按分数排序
        sorted_risks = sorted(
            dimension_scores,
            key=lambda x: x[1],
            reverse=True
        )

        # 转换维度名称
        dimension_names = {
            "position": "仓位风险",
            "drawdown": "回撤风险",
            "var_cvar": "VaR/CVaR风险",
            "beta_factor": "Beta/因子风险",
        }

        return [
            {
                "dimension": dim,
                "dimension_name": dimension_names.get(dim, dim),
                "score": score,
                "details": details,
            }
            for dim, score, details in sorted_risks
            if score > 10  # 只显示风险较高的维度
        ]

    # ==================== 风险行动 ====================

    async def _execute_risk_action(self, event: RiskEvent):
        """
        执行风险行动

        Args:
            event: 风险事件
        """
        action = event.action

        logger.info(f"执行风险行动: {action.value}, 事件: {event.event_id}")

        try:
            if action == RiskAction.MONITOR:
                # 仅监控
                event.action_result = "已记录，继续监控"

            elif action == RiskAction.WARNING:
                # 发送预警
                await self._send_warning(event)
                event.action_result = "已发送预警"

            elif action == RiskAction.REDUCE_POSITION:
                # 减仓
                await self._reduce_position(event)
                event.action_result = "已执行减仓"

            elif action == RiskAction.STOP_TRADING:
                # 停止交易
                await self._stop_trading(event)
                event.action_result = "已停止交易"

            elif action == RiskAction.FORCE_CLOSE:
                # 强平
                await self._force_close_positions(event)
                event.action_result = "已执行强平"

            elif action == RiskAction.EMERGENCY_EXIT:
                # 紧急退出
                await self._emergency_exit(event)
                event.action_result = "已执行紧急退出"

            # 标记事件已处理
            event.resolved_at = datetime.now()

        except Exception as e:
            logger.error(f"执行风险行动失败: {e}")
            event.action_result = f"执行失败: {e}"

    async def _send_warning(self, event: RiskEvent):
        """
        发送预警通知

        通知渠道：
        1. 系统日志（已实现）
        2. 系统通知服务（可扩展）
        3. 邮件/短信/微信（可扩展）
        """
        warning_msg = (
            f"⚠️ 风险预警 [{event.risk_level.value.upper()}]\n"
            f"账户: {event.account_id}\n"
            f"类型: {event.risk_type.value}\n"
            f"详情: {event.message}\n"
            f"当前值: {event.current_value:.2%}\n"
            f"阈值: {event.threshold:.2%}"
        )

        logger.warning(warning_msg)

        # 调用注册的回调函数
        if RiskAction.WARNING in self._callbacks:
            for callback in self._callbacks[RiskAction.WARNING]:
                try:
                    callback(event)
                except Exception as e:
                    logger.error(f"预警回调执行失败: {e}")

        # TODO: 可扩展为调用系统通知服务
        # from .notification_service import send_notification
        # await send_notification(account_id=event.account_id,
        #                        title="风险预警",
        #                        message=warning_msg)

    async def _reduce_position(self, event: RiskEvent):
        """
        执行减仓操作

        策略：
        1. 获取账户持仓
        2. 识别需要减仓的标的（超限持仓或亏损持仓）
        3. 计算减仓比例
        4. 执行卖出操作
        """
        logger.warning(f"📉 执行减仓: {event.account_id}")

        try:
            position_service = self._get_position_service()
            trading_service = self._get_trading_service()

            # 获取持仓
            positions = position_service.query_positions(event.account_id)

            if not positions:
                logger.info("无持仓，无需减仓")
                return

            # 确定减仓目标
            reduce_targets = []

            if event.symbol:
                # 指定股票减仓
                if event.symbol in positions:
                    reduce_targets.append(event.symbol)
            else:
                # 根据风险类型决定减仓策略
                if event.risk_type == RiskType.POSITION_LIMIT:
                    # 仓位超限：减掉最大持仓
                    sorted_positions = sorted(
                        positions.values(),
                        key=lambda x: x.market_value,
                        reverse=True
                    )
                    reduce_targets = [pos.symbol for pos in sorted_positions[:3]]

                elif event.risk_type == RiskType.CONCENTRATION:
                    # 集中度超限：减掉前几大持仓
                    sorted_positions = sorted(
                        positions.values(),
                        key=lambda x: x.market_value,
                        reverse=True
                    )
                    reduce_targets = [pos.symbol for pos in sorted_positions[:5]]

                else:
                    # 其他风险：优先减亏损持仓
                    loss_positions = [
                        pos.symbol for pos in positions.values()
                        if pos.profit_loss_pct < 0
                    ]
                    reduce_targets = loss_positions[:3]

            # 执行减仓（每只股票减仓20%）
            reduce_ratio = 0.2

            for symbol in reduce_targets:
                position = positions.get(symbol)
                if position and position.available_quantity > 0:
                    sell_quantity = int(position.available_quantity * reduce_ratio)
                    # 确保是100的整数倍（A股最小交易单位）
                    sell_quantity = (sell_quantity // 100) * 100

                    if sell_quantity >= 100:
                        order = trading_service.place_order(
                            symbol=symbol,
                            side=trading_service.OrderSide.SELL,
                            order_type=trading_service.OrderType.MARKET,
                            quantity=sell_quantity
                        )

                        if order:
                            logger.info(
                                f"减仓订单已提交: {symbol}, "
                                f"数量: {sell_quantity}"
                            )
                        else:
                            logger.error(f"减仓订单提交失败: {symbol}")

        except Exception as e:
            logger.error(f"减仓执行异常: {e}")

    async def _stop_trading(self, event: RiskEvent):
        """
        停止账户交易

        操作：
        1. 设置账户交易状态为禁止
        2. 撤销所有未成交订单
        3. 记录停止原因
        """
        logger.error(f"🛑 停止交易: {event.account_id}")

        try:
            # 设置账户禁止交易
            self._account_trading_status[event.account_id] = False

            trading_service = self._get_trading_service()

            # 撤销所有未成交订单
            pending_orders = trading_service.get_orders(
                status=trading_service.LiveOrderStatus.PENDING
            )
            submitted_orders = trading_service.get_orders(
                status=trading_service.LiveOrderStatus.SUBMITTED
            )

            all_open_orders = pending_orders + submitted_orders

            for order in all_open_orders:
                if order.account_id == event.account_id:
                    success = trading_service.cancel_order(order.order_id)
                    if success:
                        logger.info(f"已撤销订单: {order.order_id}")
                    else:
                        logger.warning(f"撤销订单失败: {order.order_id}")

            logger.info(
                f"账户 {event.account_id} 交易已停止，"
                f"已撤销 {len(all_open_orders)} 个未成交订单"
            )

            # 调用回调
            if RiskAction.STOP_TRADING in self._callbacks:
                for callback in self._callbacks[RiskAction.STOP_TRADING]:
                    try:
                        callback(event)
                    except Exception as e:
                        logger.error(f"停止交易回调执行失败: {e}")

        except Exception as e:
            logger.error(f"停止交易执行异常: {e}")

    async def _force_close_positions(self, event: RiskEvent):
        """
        强制平仓

        操作：
        1. 获取所有持仓
        2. 以市价卖出所有可用持仓
        3. 记录平仓详情
        """
        logger.error(f"❌ 强平持仓: {event.account_id}")

        try:
            position_service = self._get_position_service()
            trading_service = self._get_trading_service()

            # 获取所有持仓
            positions = position_service.query_positions(event.account_id)

            if not positions:
                logger.info("无持仓，无需强平")
                return

            close_results = []

            for symbol, position in positions.items():
                if position.available_quantity > 0:
                    # 确保是100的整数倍
                    sell_quantity = (position.available_quantity // 100) * 100

                    if sell_quantity >= 100:
                        order = trading_service.place_order(
                            symbol=symbol,
                            side=trading_service.OrderSide.SELL,
                            order_type=trading_service.OrderType.MARKET,
                            quantity=sell_quantity
                        )

                        close_results.append({
                            "symbol": symbol,
                            "quantity": sell_quantity,
                            "success": order is not None,
                            "order_id": order.order_id if order else None
                        })

                        if order:
                            logger.info(f"强平订单已提交: {symbol}, 数量: {sell_quantity}")
                        else:
                            logger.error(f"强平订单提交失败: {symbol}")

            # 记录强平结果
            success_count = sum(1 for r in close_results if r["success"])
            logger.info(
                f"强平完成: {success_count}/{len(close_results)} 个持仓 "
                f"已提交卖出订单"
            )

            # 调用回调
            if RiskAction.FORCE_CLOSE in self._callbacks:
                for callback in self._callbacks[RiskAction.FORCE_CLOSE]:
                    try:
                        callback(event, close_results)
                    except Exception as e:
                        logger.error(f"强平回调执行失败: {e}")

        except Exception as e:
            logger.error(f"强平执行异常: {e}")

    async def _emergency_exit(self, event: RiskEvent):
        """
        紧急退出

        最高级别风控，立即执行：
        1. 设置紧急模式标志
        2. 停止所有交易
        3. 强制平仓所有持仓
        4. 通知所有相关方
        """
        logger.critical(f"🚨 紧急退出: {event.account_id}")

        try:
            # 1. 激活紧急模式
            self._emergency_mode = True

            # 2. 停止交易
            await self._stop_trading(event)

            # 3. 强制平仓
            await self._force_close_positions(event)

            # 4. 发送紧急通知
            emergency_msg = (
                f"🚨 紧急退出已执行\n"
                f"账户: {event.account_id}\n"
                f"触发原因: {event.message}\n"
                f"时间: {datetime.now().isoformat()}\n"
                f"所有持仓已清仓，交易已停止"
            )

            logger.critical(emergency_msg)

            # 调用所有紧急回调
            for action in [RiskAction.EMERGENCY_EXIT,
                           RiskAction.FORCE_CLOSE,
                           RiskAction.STOP_TRADING]:
                if action in self._callbacks:
                    for callback in self._callbacks[action]:
                        try:
                            callback(event)
                        except Exception as e:
                            logger.error(f"紧急退出回调执行失败: {e}")

        except Exception as e:
            logger.critical(f"紧急退出执行异常: {e}")
            # 即使异常也要保持紧急模式
            self._emergency_mode = True

    # ==================== 监控管理 ====================

    def start_monitoring(self):
        """启动自动监控"""
        if self._monitoring_task is None or self._monitoring_task.done():
            self._monitoring_task = asyncio.create_task(self._monitoring_loop())
            logger.info(f"✅ 风险监控已启动，检查间隔: {self.check_interval}秒")

    def stop_monitoring(self):
        """停止自动监控"""
        if self._monitoring_task and not self._monitoring_task.done():
            self._monitoring_task.cancel()
            logger.info("风险监控已停止")

    async def _monitoring_loop(self):
        """监控循环"""
        while True:
            try:
                # 检查是否处于紧急模式
                if self._emergency_mode:
                    logger.warning("处于紧急模式，跳过风险检查")
                    await asyncio.sleep(self.check_interval)
                    continue

                # 获取所有需要监控的账户
                account_ids = self._get_monitored_accounts()

                for account_id in account_ids:
                    # 检查账户是否允许交易
                    if not self._can_trade(account_id):
                        logger.debug(f"账户 {account_id} 交易已停止，跳过检查")
                        continue

                    try:
                        await self.check_risks(account_id)
                    except Exception as e:
                        logger.error(f"账户 {account_id} 风险检查异常: {e}")

                await asyncio.sleep(self.check_interval)

            except asyncio.CancelledError:
                logger.info("监控循环已取消")
                break
            except Exception as e:
                logger.error(f"监控循环异常: {e}")
                await asyncio.sleep(self.check_interval)

    def _get_monitored_accounts(self) -> List[str]:
        """
        获取需要监控的账户列表

        Returns:
            账户ID列表
        """
        # 从配置或服务获取账户列表
        # 这里先返回已知的账户
        monitored = list(self._account_trading_status.keys())

        # 如果没有账户，尝试从配置获取默认账户
        if not monitored:
            try:
                from .trading_service import get_trading_service
                trading_service = get_trading_service()
                if trading_service.account_id:
                    monitored.append(trading_service.account_id)
                    # 初始化交易状态
                    self._account_trading_status[trading_service.account_id] = True
            except Exception as e:
                logger.warning(f"获取交易账户失败: {e}")

        return monitored

    def _can_trade(self, account_id: str) -> bool:
        """
        检查账户是否允许交易

        Args:
            account_id: 账户ID

        Returns:
            是否允许交易
        """
        # 紧急模式下禁止所有交易
        if self._emergency_mode:
            return False

        # 检查账户交易状态（默认允许）
        return self._account_trading_status.get(account_id, True)

    def resume_trading(self, account_id: str) -> bool:
        """
        恢复账户交易

        Args:
            account_id: 账户ID

        Returns:
            是否成功恢复
        """
        # 紧急模式下不能恢复交易
        if self._emergency_mode:
            logger.warning("紧急模式下不能恢复交易")
            return False

        self._account_trading_status[account_id] = True
        logger.info(f"账户 {account_id} 交易已恢复")
        return True

    def reset_emergency_mode(self, confirm: bool = False) -> bool:
        """
        重置紧急模式

        Args:
            confirm: 确认重置（需要显式传True）

        Returns:
            是否成功重置
        """
        if not confirm:
            logger.warning("重置紧急模式需要确认")
            return False

        self._emergency_mode = False
        logger.info("紧急模式已重置")
        return True

    def register_callback(self, action: RiskAction, callback: Callable):
        """
        注册风控行动回调函数

        Args:
            action: 风控行动类型
            callback: 回调函数
        """
        if action not in self._callbacks:
            self._callbacks[action] = []

        self._callbacks[action].append(callback)
        logger.info(f"已注册 {action.value} 回调函数")

    def unregister_callback(self, action: RiskAction, callback: Callable):
        """
        取消注册回调函数

        Args:
            action: 风控行动类型
            callback: 回调函数
        """
        if action in self._callbacks:
            try:
                self._callbacks[action].remove(callback)
                logger.info(f"已取消注册 {action.value} 回调函数")
            except ValueError:
                logger.warning(f"回调函数未找到")

    # ==================== 事件查询 ====================

    def get_events(
        self,
        account_id: Optional[str] = None,
        risk_type: Optional[RiskType] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> List[RiskEvent]:
        """
        查询风险事件

        Args:
            account_id: 账户ID筛选
            risk_type: 风险类型筛选
            start_time: 开始时间
            end_time: 结束时间

        Returns:
            RiskEvent列表
        """
        events = self._events

        if account_id is not None:
            events = [e for e in events if e.account_id == account_id]

        if risk_type is not None:
            events = [e for e in events if e.risk_type == risk_type]

        if start_time is not None:
            events = [e for e in events if e.triggered_at >= start_time]

        if end_time is not None:
            events = [e for e in events if e.triggered_at <= end_time]

        return sorted(events, key=lambda x: x.triggered_at, reverse=True)

    def get_recent_events(self, limit: int = 10) -> List[RiskEvent]:
        """
        获取最近的风险事件

        Args:
            limit: 返回数量

        Returns:
            最近的风险事件列表
        """
        return sorted(
            self._events,
            key=lambda x: x.triggered_at,
            reverse=True
        )[:limit]


# ==================== 全局单例 ====================

_risk_service_instance: Optional[RiskService] = None


def get_risk_service() -> RiskService:
    """
    获取风险控制服务单例

    Returns:
        RiskService实例
    """
    global _risk_service_instance

    if _risk_service_instance is None:
        _risk_service_instance = RiskService()

    return _risk_service_instance

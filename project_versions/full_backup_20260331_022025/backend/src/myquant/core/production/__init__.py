# -*- coding: utf-8 -*-
"""
Production阶段Service
======================

功能: 实盘交易、仓位管理、风险控制、ML信号生成

目标: 将验证过的策略安全地应用到实盘交易

架构层次：
- TradingService: 真实资金交易执行
- PositionService: 实盘持仓管理
- RiskService: 风险监控和控制
- OnlineModelManager: 在线模型管理（P0核心）
- OnlinePredictionService: 实时预测服务（P1）
- MLSignalGenerator: ML信号生成器（P1）

⚠️ 重要提示：
- Production阶段涉及真实资金
- 必须经过模拟实盘验证后才能使用
- 风险控制是最后一道防线

作者: MyQuant v10.0.0 Team
创建时间: 2026-02-04
更新时间: 2026-02-13 (ML模块集成)
"""

from .trading_service import (
    TradingService,
    get_trading_service,
    TradingAccount,
    LiveOrder,
    TradeRecord,
    TradingStatus,
    OrderType as TradingOrderType,
    OrderSide as TradingOrderSide,
    LiveOrderStatus
)

from .position_service import (
    PositionService,
    get_position_service,
    LivePosition,
    PortfolioSummary,
    PositionAnalysis,
    PositionStatus
)

from .risk_service import (
    RiskService,
    get_risk_service,
    RiskRule,
    RiskEvent,
    RiskMetrics,
    RiskLevel,
    RiskType,
    RiskAction
)

from .online_model_manager import (
    OnlineModelManager,
    get_model_manager,
    ModelStatus,
    ModelVersion,
    ABTestConfig,
    ABTestStatus
)

from .online_prediction_service import (
    OnlinePredictionService,
    get_prediction_service,
    PredictionResult,
    PredictionDirection,
    BatchPredictionResult
)

from .ml_signal_generator import (
    MLSignalGenerator,
    get_signal_generator,
    TradingSignal,
    SignalType,
    SignalStrength,
    SignalValidationResult
)

# 导出所有公共接口
__all__ = [
    # 交易服务（9个）
    "TradingService",
    "get_trading_service",
    "TradingAccount",
    "LiveOrder",
    "TradeRecord",
    "TradingStatus",
    "TradingOrderType",
    "TradingOrderSide",
    "LiveOrderStatus",

    # 仓位服务（7个）
    "PositionService",
    "get_position_service",
    "LivePosition",
    "PortfolioSummary",
    "PositionAnalysis",
    "PositionStatus",

    # 风控服务（8个）
    "RiskService",
    "get_risk_service",
    "RiskRule",
    "RiskEvent",
    "RiskMetrics",
    "RiskLevel",
    "RiskType",
    "RiskAction",

    # 在线模型管理（6个）
    "OnlineModelManager",
    "get_model_manager",
    "ModelStatus",
    "ModelVersion",
    "ABTestConfig",
    "ABTestStatus",

    # 在线预测服务（5个）
    "OnlinePredictionService",
    "get_prediction_service",
    "PredictionResult",
    "PredictionDirection",
    "BatchPredictionResult",

    # ML信号生成器（6个）
    "MLSignalGenerator",
    "get_signal_generator",
    "TradingSignal",
    "SignalType",
    "SignalStrength",
    "SignalValidationResult",
]

# -*- coding: utf-8 -*-
"""
Validation阶段Service
====================

功能: 回测、模拟实盘、在线训练、性能评估

目标: 验证策略的有效性，评估策略风险和收益

架构层次：
- BacktestService: 历史回测（历史数据）
- SimulationService: 模拟实盘（真实行情数据 + 模拟账户）

重要说明：
模拟实盘 ≠ 模拟数据
- ✅ 使用真实行情数据（和实盘相同的数据源）
- ✅ 使用模拟账户进行交易（虚拟资金，真实下单逻辑）
- ✅ 用于验证策略在真实市场环境下的表现

作者: MyQuant v10.0.0 Team
创建时间: 2026-02-04
更新时间: 2026-02-04 (M2-9完成)
"""

from .backtest_service import (
    BacktestService,
    get_backtest_service,
    BacktestConfig,
    BacktestResult,
    BacktestStatus,
    PerformanceMetrics
)

from .simulation_service import (
    SimulationService,
    get_simulation_service,
    SimulationAccount,
    SimulationPosition,
    SimulationOrder,
    SimulationConfig,
    OrderType,
    OrderSide,
    OrderStatus
)

# 导出所有公共接口
__all__ = [
    # 回测服务
    "BacktestService",
    "get_backtest_service",
    "BacktestConfig",
    "BacktestResult",
    "BacktestStatus",
    "PerformanceMetrics",

    # 模拟实盘服务
    "SimulationService",
    "get_simulation_service",
    "SimulationAccount",
    "SimulationPosition",
    "SimulationOrder",
    "SimulationConfig",
    "OrderType",
    "OrderSide",
    "OrderStatus",
]

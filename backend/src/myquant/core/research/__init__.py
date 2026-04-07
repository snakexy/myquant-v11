# -*- coding: utf-8 -*-
"""
Research阶段Service
==================

功能: 因子计算、特征工程、信号生成、模型训练

目标: 为量化策略提供研究工具和数据分析能力

架构层次：
- ResearchDataService: 统一数据获取和管理
- ResearchStockService: 股票基本信息和数据准备
- DataCleaningService: 数据质量保证和清洗
- IndicatorService: 技术指标计算（基于ta-lib）

作者: MyQuant v10.0.0 Team
创建时间: 2026-02-04
更新时间: 2026-02-04 (M2-8完成，M2-13集成ta-lib)
"""

from .data_service import (
    ResearchDataService,
    get_research_data_service,
    DataType
)

from .stock_service import (
    ResearchStockService,
    get_research_stock_service,
    StockInfo
)

from .data_cleaning_service import (
    DataCleaningService,
    get_data_cleaning_service,
    DataQualityReport
)

from .indicators import (
    IndicatorService,
    get_indicator_service,
    IndicatorResult,
    IndicatorType
)

from .ml_model_service import (
    MLModelService,
    get_ml_service,
    ModelType,
    TaskType,
    LabelType,
    MLTrainingConfig,
    MLPredictionRequest,
    ModelInfo,
    PredictionResult,
    TrainingResult,
)

from .rl_strategy_service import (
    RLStrategyService,
    get_rl_strategy_service,
    RLTrainingConfig,
    RLTrainingResult,
    RLOptimizationResult,
)

# 导出所有公共接口
__all__ = [
    # 数据服务
    "ResearchDataService",
    "get_research_data_service",
    "DataType",

    # 股票服务
    "ResearchStockService",
    "get_research_stock_service",
    "StockInfo",

    # 数据清洗服务
    "DataCleaningService",
    "get_data_cleaning_service",
    "DataQualityReport",

    # 指标计算服务
    "IndicatorService",
    "get_indicator_service",
    "IndicatorResult",
    "IndicatorType",

    # ML模型服务
    "MLModelService",
    "get_ml_service",
    "ModelType",
    "TaskType",
    "LabelType",
    "MLTrainingConfig",
    "MLPredictionRequest",
    "ModelInfo",
    "PredictionResult",
    "TrainingResult",

    # RL策略服务
    "RLStrategyService",
    "get_rl_strategy_service",
    "RLTrainingConfig",
    "RLTrainingResult",
    "RLOptimizationResult",
]

# 数据处理模块

## 概述

本模块提供了完整的数据处理功能，包括数据质量控制、技术指标计算和因子生成。它是对原有 `enhanced_qlib_data_processor.py` 的重构和模块化，旨在提高代码的可维护性和可扩展性。

## 目录结构

```
qlib_core/data_processing/
├── __init__.py                    # 模块初始化和导出
├── data_quality.py               # 数据质量控制模块
├── technical_indicators.py        # 技术指标计算模块
├── factor_generation.py           # 因子生成模块
├── enhanced_processor.py          # 整合后的增强处理器
├── test_data_processing.py         # 测试文件
└── README.md                    # 本文档
```

## 模块说明

### 1. 数据质量控制模块 (data_quality.py)

提供数据预处理、清洗和质量验证功能：

- **数据类型优化**：自动优化数值列的数据类型
- **时间序列处理**：日期索引处理、排序和去重
- **缺失值处理**：支持插值、前向填充、后向填充
- **异常值检测和处理**：支持IQR、Z-Score、孤立森林方法
- **数据平滑**：使用中值滤波器平滑数据
- **数据质量验证**：价格逻辑检查、成交量验证

### 2. 技术指标计算模块 (technical_indicators.py)

提供各种技术指标的计算功能：

- **移动平均线**：简单移动平均 (MA)
- **指数移动平均**：指数移动平均 (EMA)
- **相对强弱指数**：RSI指标
- **MACD指标**：MACD线、信号线和柱状图
- **布林带**：上轨、中轨、下轨和带宽
- **平均真实波幅**：ATR指标
- **顺势指标**：CCI指标
- **威廉指标**：威廉%R指标
- **动量指标**：价格动量
- **随机指标**：KDJ指标

### 3. 因子生成模块 (factor_generation.py)

提供各种量化因子的生成功能：

- **动量因子**：不同周期的价格动量
- **反转因子**：短期反转和价格位置因子
- **波动率因子**：已实现波动率和ATR波动率
- **成交量因子**：成交量移动平均和价量关系
- **技术因子**：基于技术指标的衍生因子
- **截面因子**：多股票截面比较因子（预留）

### 4. 增强处理器 (enhanced_processor.py)

整合所有子模块，提供统一的数据处理接口：

- **完整处理流程**：一站式数据处理解决方案
- **模块化设计**：可单独使用各个子模块
- **配置驱动**：支持灵活的参数配置
- **缓存机制**：提高处理效率

## 与现有模块的关系

### 与 `qlib_core/qlib_dataprocessing` 的关系

- `qlib_dataprocessing`：专门为QLib标准格式设计的数据处理模块
- `data_processing`：更通用的数据处理模块，可与QLib模块协同工作

两者可以共存，各有不同的用途：

1. **QLib标准处理**：使用 `qlib_dataprocessing` 模块
2. **通用数据处理**：使用 `data_processing` 模块
3. **集成使用**：可以在QLib处理前后使用通用模块进行增强处理

### 与 `enhanced_qlib_data_processor.py` 的关系

新的 `data_processing` 模块是对原有 `enhanced_qlib_data_processor.py` 的重构：

- **功能保持**：保留所有原有功能
- **代码优化**：修复了代码格式和导入问题
- **模块化**：将功能拆分为更细粒度的模块
- **可维护性**：提高代码的可读性和可维护性

## 使用示例

### 基本使用

```python
from qlib_core.data_processing import get_enhanced_data_processor

# 创建增强处理器
processor = get_enhanced_data_processor({
    'outlier_method': 'iqr',
    'missing_method': 'interpolate',
    'indicator_windows': [5, 10, 20]
})

# 数据预处理
processed_data = processor.preprocess_data_advanced(data, '000001.SZ')

# 计算技术指标
indicator_data = processor.calculate_technical_indicators(
    processed_data, ['MA', 'RSI', 'MACD']
)

# 生成因子
factor_data = processor.generate_factors(processed_data, {
    'momentum_factors': True,
    'reversal_factors': True,
    'volatility_factors': True
})

# 完整处理流程
complete_data = processor.process_data_complete(
    data,
    instrument='000001.SZ',
    indicators=['MA', 'EMA', 'RSI'],
    factor_config={
        'momentum_factors': True,
        'technical_factors': True
    }
)
```

### 单独使用子模块

```python
from qlib_core.data_processing import (
    get_quality_controller,
    get_indicators_calculator,
    get_factor_generator
)

# 数据质量控制
quality_controller = get_quality_controller({
    'outlier_method': 'zscore',
    'missing_method': 'forward'
})
clean_data = quality_controller.preprocess_data_advanced(data)

# 技术指标计算
indicators_calc = get_indicators_calculator({
    'indicator_windows': [5, 10, 20, 60]
})
indicator_data = indicators_calc.calculate_technical_indicators(data)

# 因子生成
factor_gen = get_factor_generator()
factor_data = factor_gen.generate_factors(data, {
    'momentum_factors': True,
    'volume_factors': True
})
```

## 测试

运行测试以验证模块功能：

```bash
cd qlib_core/data_processing
python test_data_processing.py
```

测试包括：
- 数据质量控制模块测试
- 技术指标计算模块测试
- 因子生成模块测试
- 增强处理器集成测试
- 完整功能测试

## 配置参数

### 数据质量控制配置

```python
config = {
    'outlier_method': 'iqr',        # 异常值处理方法: iqr, zscore, isolation
    'missing_method': 'interpolate',    # 缺失值处理方法: interpolate, forward, backward
    'min_data_points': 20            # 最小数据点数
    'cache_enabled': True             # 是否启用缓存
}
```

### 技术指标配置

```python
config = {
    'indicator_windows': [5, 10, 20, 60]  # 技术指标计算窗口
}
```

### 因子生成配置

```python
config = {
    # 因子类型开关
    'momentum_factors': True,         # 动量因子
    'reversal_factors': True,         # 反转因子
    'volatility_factors': True,        # 波动率因子
    'volume_factors': True,            # 成交量因子
    'technical_factors': True,          # 技术因子
    'cross_sectional_factors': True     # 截面因子
}
```

## 注意事项

1. **数据格式**：输入数据应包含标准的OHLCV字段（open, high, low, close, volume）
2. **时间索引**：建议使用日期时间索引，便于时间序列处理
3. **数据质量**：模块会自动进行数据质量检查和修正
4. **性能优化**：对于大数据集，建议启用缓存机制
5. **异常处理**：模块包含完整的异常处理和日志记录

## 扩展指南

### 添加新的技术指标

1. 在 `technical_indicators.py` 中添加计算方法
2. 在 `calculate_technical_indicators` 中添加调用逻辑
3. 更新 `get_available_indicators` 方法

### 添加新的因子类型

1. 在 `factor_generation.py` 中添加生成方法
2. 在 `generate_factors` 中添加调用逻辑
3. 更新 `get_available_factor_types` 方法

### 添加新的数据质量控制方法

1. 在 `data_quality.py` 中添加处理方法
2. 在 `preprocess_data_advanced` 中添加调用逻辑
3. 更新配置参数说明
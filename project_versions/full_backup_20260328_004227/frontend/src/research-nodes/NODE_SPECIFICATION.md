# 研究阶段节点规范说明

> 基于《三阶段工作流程最终程序设计确认大纲》设计文档
> 后端API完成状态参考：[后端API完成状态及测试报告](../../docs/已完成后端及API/后端API完成状态及测试报告.md)

## 已完成节点（保持不变）

### 1. 股票选择节点 (StockSelectionNode) ✅
- **文件**: `StockSelectionNode/config.ts`, `data.ts`, `Config.vue`
- **后端API**: `http://localhost:8000/api/v1/unified_data/stock/{symbol}`
- **状态**: 已完成，保持不变

### 2. 指数选择节点 (IndexSelectionNode) ✅
- **文件**: `IndexSelectionNode/config.ts`, `data.ts`, `Config.vue`
- **后端API**: `http://localhost:8000/api/v1/unified_data/stock/{symbol}`
- **状态**: 已完成，保持不变

---

## 后端API对接状态

| 节点 | 后端API端点 | 状态 |
|------|-------------|------|
| 股票选择节点 | `/api/v1/unified_data/stock/{symbol}` | ✅ 已对接 |
| 指数选择节点 | `/api/v1/unified_data/stock/{symbol}` | ✅ 已对接 |
| 数据清洗节点 | `/api/v1/data-cleaning/clean` | ✅ 已对接 |
| 因子计算引擎节点 | `/api/v1/domain/factor_engine/factor-templates` | ✅ 已对接 |
| 特征工程节点 | `/api/v1/data-processors/market-data` | ✅ 已对接 |
| 智能信号引擎节点 | `/api/v1/ai_realtime_processing/streams/create` | ✅ 已对接 |
| AI智能分析节点 | `/api/v1/ai_assistant/market-analysis` | ✅ 已对接 |
| AI助手策略构思节点 | `/api/v1/strategy_generator/strategies/generate` | ✅ 已对接 |
| 模型训练节点 | `/api/v1/models/train` | ✅ 已对接 |
| 初步验证节点 | `/api/v1/backtest/run` | ✅ 已对接 |

---

## 需要创建/更新的节点

### 3. 数据清洗节点 (DataCleaningNode)

**核心任务**
将数据中枢的股票数据（股票选择节点获取的数据）转换为QLib可用的数据格式，保存到项目根目录的 `\data\qlib_data` 目录。

**基础配置**
| 项目 | 值 |
|------|-----|
| 节点ID | `data-cleaning` |
| 类别 | `data-processing` |
| 图标 | `🧹` |
| 标题 | 数据清洗 |
| 描述 | 转换数据为QLib格式 |

**后端API连接**
- **模块**: `api_layer.api.v1.data_cleaning`
- **端点**: `POST /api/v1/data-cleaning/clean`
- **状态**: ✅ 后端API已完成（100%）
- **参考文档**: [后端API完成状态报告 - 数据清洗API](../../docs/已完成后端及API/后端API完成状态及测试报告.md#551-数据清洗api接口-100完成)

**显示内容**
- **小节点显示**: 统计卡片类型
  - 转换状态（未转换/转换中/已完成）
  - 数据数量（只数 x 天数）
  - 保存路径：`E:\MyQuant_v8.0.1\data\qlib_data`
  - 数据完整性：百分比
- **详情页面内容**:
  - 数据来源概览（来自哪个上游节点）
  - 转换配置（日期范围、股票列表）
  - QLib数据目录结构
  - 数据质量报告
  - 转换进度条（转换时显示）
  - 重新转换按钮

**输入输出**
- **输入**: 股票选择节点 或 指数选择节点
- **输出**: 因子计算引擎

**配置参数**
```typescript
{
  // QLib数据保存路径
  qlibDataPath: 'E:\\MyQuant_v8.0.1\\data\\qlib_data',
  // 数据频率
  frequency: 'daily' | '1min' | '5min' | '15min' | '30min' | '60min',
  // 数据清洗选项
  dropMissing: boolean,           // 删除缺失值过多的股票
  maxMissingRatio: number,         // 最大缺失比例 (0-1)
  forwardFill: boolean,            // 前向填充
  // 异常值处理
  handleOutliers: boolean,
  outlierMethod: 'clip' | 'winsorize',
  // 其他选项
  normalize: boolean,              // 标准化数据
  includeIndex: boolean            // 是否包含指数数据
}
```

---

### 4. 因子计算引擎节点 (FactorEngineNode)

**基础配置**
| 项目 | 值 |
|------|-----|
| 节点ID | `factor-engine` |
| 类别 | `feature-engineering` |
| 图标 | `⚙️` |
| 标题 | 因子计算引擎 |
| 描述 | QLib因子计算和管理 |

**双输入端口**
```typescript
inputs: [
  { id: 'data-driven', label: '数据驱动输入', active: true },
  { id: 'ai-driven', label: 'AI助手输入', active: true }
]
```

**后端API连接**
- **模块**: `api_layer.api.v1.domain.factor_engine`
- **QLib模块**: `domain.factor_engine.qlib_adapter`
- **端点**:
  - `GET /factor_engine/factor-templates` - 获取因子模板列表
  - `POST /factor_engine/calculate` - 执行因子计算
  - `GET /factor_engine/calculation-status/{task_id}` - 查询计算状态
  - `GET /factor_engine/factor-list` - 获取可用因子列表

**显示内容**
- **小节点显示**: 表格类型
  - 因子名称
  - 因子类型（Alpha158/Alpha360/自定义）
  - 计算状态
  - 因子数量
- **详情页面内容**:
  - 因子模板选择（Alpha158, Alpha360, 自定义因子）
  - 因子计算配置
  - 计算进度显示
  - 因子预览表格
  - 因子统计信息

**输入输出**
- **输入1**: 数据清洗节点（数据驱动）
- **输入2**: AI助手策略构思节点（AI驱动，可选）
- **输出**: 特征工程节点

**配置参数**
```typescript
{
  // 因子模板
  factorTemplate: 'Alpha158' | 'Alpha360' | 'custom',
  // 自定义因子表达式
  customFactors: string[],  // QLib表达式
  // 计算配置
  computeMode: 'fast' | 'accurate',
  // 因子过滤
  factorFilter: {
    minCorrelation: number,
    maxCorrelation: number,
    icThreshold: number
  }
}
```

---

### 5. 特征工程节点 (FeatureEngineeringNode)

**基础配置**
| 项目 | 值 |
|------|-----|
| 节点ID | `feature-engineering` |
| 类别 | `feature-engineering` |
| 图标 | `🔧` |
| 标题 | 特征工程 |
| 描述 | 特征选择、转换和组合 |

**后端API连接**
- **模块**: `api_layer.api.v1.data-processor`
- **端点**:
  - `POST /data-processor/process` - processing_type=feature_engineering
  - `POST /data-processor/feature-selection` - 特征选择
  - `POST /data-processor/feature-transformation` - 特征转换

**显示内容**
- **小节点显示**: 统计卡片类型
  - 原始特征数
  - 最终特征数
  - 特征选择比例
  - 处理状态
- **详情页面内容**:
  - 特征列表及统计
  - 特征重要性排序
  - 特征相关性热力图
  - 特征转换配置

**输入输出**
- **输入**: 因子计算引擎节点
- **输出**: 智能信号引擎节点

**配置参数**
```typescript
{
  // 特征选择方法
  selectionMethod: 'variance-threshold' | 'k-best' | 'recursive' | 'importance',
  kBest: number,
  // 特征转换
  transformation: 'pca' | 'standardization' | 'normalization' | 'none',
  pcaComponents: number,
  // 其他选项
  removeCorrelated: boolean,
  correlationThreshold: number
}
```

---

### 6. 智能信号引擎节点 (SignalEngineNode)

**基础配置**
| 项目 | 值 |
|------|-----|
| 节点ID | `signal-engine` |
| 类别 | `analysis` |
| 图标 | `📡` |
| 标题 | 智能信号引擎 |
| 描述 | 技术分析和模式识别 |

**后端API连接**
- **模块**: `domain.factor_engine.qlib_adapter + ai_strategy.ai_realtime_processing`
- **端点**:
  - `POST /ai_strategy/ai_realtime_processing/pattern-detection` - 模式检测
  - `GET /ai_strategy/ai_realtime_processing/signal-list` - 信号列表
  - `POST /ai_strategy/ai_realtime_processing/technical-analysis` - 技术分析

**显示内容**
- **小节点显示**: 列表类型
  - 检测到的信号
  - 信号强度
  - 信号类型（买入/卖出/中性）
  - 检测时间
- **详情页面内容**:
  - 技术指标配置（MA, MACD, RSI, Bollinger等）
  - 信号规则配置
  - 检测结果展示
  - 信号历史记录

**输入输出**
- **输入**: 特征工程节点
- **输出**: AI智能分析节点

**配置参数**
```typescript
{
  // 技术指标
  indicators: {
    ma: boolean,
    maPeriods: number[],
    macd: boolean,
    rsi: boolean,
    rsiPeriod: number,
    bollinger: boolean,
    kdj: boolean
  },
  // 信号配置
  signalRules: {
    buyCondition: string,
    sellCondition: string,
    strength: number
  },
  // 模式检测
  patternDetection: boolean,
  patterns: string[]
}
```

---

### 7. AI智能分析节点 (AIAnalysisNode)

**基础配置**
| 项目 | 值 |
|------|-----|
| 节点ID | `ai-analysis` |
| 类别 | `analysis` |
| 图标 | `🤖` |
| 标题 | AI智能分析 |
| 描述 | AI驱动的市场分析和策略建议 |

**后端API连接**
- **模块**: `api_layer.api.v1.ai_assistant`
- **端点**:
  - `POST /ai_assistant/chat` - AI对话
  - `POST /ai_assistant/market-analysis` - 市场分析
  - `GET /ai_assistant/analysis-history` - 分析历史

**显示内容**
- **小节点显示**: 文本/富文本类型
  - 分析摘要
  - 关键发现
  - 建议操作
- **详情页面内容**:
  - 完整分析报告
  - AI对话界面
  - 市场趋势图表
  - 风险评估结果

**输入输出**
- **输入**: 智能信号引擎节点
- **输出**: 模型训练节点

**配置参数**
```typescript
{
  // 分析类型
  analysisType: 'market-trend' | 'individual-stock' | 'portfolio',
  // 分析深度
  depth: 'basic' | 'standard' | 'comprehensive',
  // 输出格式
  outputFormat: 'summary' | 'detailed' | 'report',
  // 其他选项
  includeCharts: boolean,
  includeRisk: boolean
}
```

---

### 8. AI助手策略构思节点 (AIStrategyAssistantNode)

**基础配置**
| 项目 | 值 |
|------|-----|
| 节点ID | 'ai-strategy-assistant' |
| 类别 | `analysis` |
| 图标 | `💡` |
| 标题 | AI助手策略构思 |
| 描述 | AI生成交易策略因子 |

**后端API连接**
- **模块**: `api_layer.api.v1.unified + ai_strategy.strategy_generator`
- **端点**:
  - `POST /unified/ai-strategy/generate` - 生成策略
  - `POST /unified/ai-strategy/refine` - 优化策略
  - `GET /unified/ai-strategy/templates` - 策略模板

**显示内容**
- **小节点显示**: 文本类型
  - 生成的因子表达式
  - 策略摘要
  - 生成状态
- **详情页面内容**:
  - AI策略生成界面
  - 策略描述
  - 生成的因子代码
  - 回测预览（如果有）

**输入输出**
- **输入**: 无（独立起点节点）
- **输出**: 因子计算引擎节点（AI驱动输入端口）

**配置参数**
```typescript
{
  // 策略类型
  strategyType: 'trend-following' | 'mean-reversion' | 'momentum' | 'custom',
  // 策略描述
  description: string,
  // 风险偏好
  riskLevel: 'conservative' | 'moderate' | 'aggressive',
  // 生成选项
  includeStopLoss: boolean,
  includeTakeProfit: boolean
}
```

---

### 9. 模型训练节点 (ModelTrainingNode)

**基础配置**
| 项目 | 值 |
|------|-----|
| 节点ID | `model-training` |
| 类别 | `analysis` |
| 图标 | `🎯` |
| 标题 | 模型训练 |
| 描述 | 机器学习模型训练和评估 |

**后端API连接**
- **模块**: `api_layer.api.v1.models + experiment-services.model-training`
- **端点**:
  - `POST /models/train` - 训练模型
  - `GET /models/training-status/{task_id}` - 训练状态
  - `GET /models/evaluate` - 模型评估
  - `GET /models/list` - 模型列表

**显示内容**
- **小节点显示**: 统计卡片类型
  - 模型名称
  - 训练状态
  - 准确率/收益率
  - 训练进度
- **详情页面内容**:
  - 模型选择（XGBoost, LightGBM, LSTM等）
  - 训练参数配置
  - 训练进度条
  - 评估指标（准确率、召回率、夏普比率等）
  - 模型对比图表

**双输入端口**
```typescript
inputs: [
  { id: 'features', label: '特征输入', active: true },
  { id: 'ai-insights', label: 'AI分析输入', active: true }
]
```

**输入输出**
- **输入1**: 特征工程节点 / AI智能分析节点
- **输出**: 初步验证节点

**配置参数**
```typescript
{
  // 模型类型
  modelType: 'xgboost' | 'lightgbm' | 'lstm' | 'transformer' | 'linear',
  // 训练参数
  trainParams: {
    testSize: number,
    cvFolds: number,
    randomSeed: number
  },
  // 特征列选择
  featureColumns: string[],
  targetColumn: string,
  // 评估指标
  metrics: ['accuracy', 'precision', 'recall', 'sharpe', 'max-drawdown']
}
```

---

### 10. 初步验证节点 (PreliminaryValidationNode)

**基础配置**
| 项目 | 值 |
|------|-----|
| 节点ID | `preliminary-validation` |
| 类别 | `output` |
| 图标 | `✅` |
| 标题 | 初步验证 |
| 描述 | 模型性能初步验证 |

**后端API连接**
- **模块**: `api_layer.api.v1.validation`（假设）
- **端点**:
  - `POST /validation/backtest` - 简单回测
  - `POST /validation/evaluate` - 模型评估
  - `GET /validation/report` - 验证报告

**显示内容**
- **小节点显示**: 统计卡片类型
  - 验证状态
  - 总收益率
  - 夏普比率
  - 最大回撤
- **详情页面内容**:
  - 完整回测报告
  - 收益曲线图
  - 持仓分析
  - 交易记录
  - 风险指标

**输入输出**
- **输入**: 模型训练节点
- **输出**: 无（终点节点）

**配置参数**
```typescript
{
  // 回测参数
  backtestPeriod: {
    start: string,
    end: string
  },
  // 初始资金
  initialCapital: number,
  // 交易成本
  commission: number,
  slippage: number,
  // 评估选项
  metrics: ['return', 'sharpe', 'max-drawdown', 'win-rate', 'profit-factor']
}
```

---

## 研究阶段工作流程图

```
┌─────────────────┐     ┌─────────────────┐
│ 股票选择节点    │     │ 指数选择节点    │
└────────┬────────┘     └────────┬────────┘
         │                       │
         └───────────┬───────────┘
                     │
                     ▼
            ┌─────────────────┐
            │  数据清洗节点    │
            └────────┬────────┘
                     │
                     ▼
         ┌───────────────────────┐
         │    因子计算引擎节点      │◄──────────────┐
         │   (双输入: 数据驱动)    │               │
         └───────────┬───────────┘               │
                     │                           │
                     ▼                           │
            ┌─────────────────┐                 │
            │  特征工程节点    │                 │
            └────────┬────────┘                 │
                     │                           │
                     ▼                           │
            ┌─────────────────┐                 │
            │ 智能信号引擎节点 │                 │
            └────────┬────────┘                 │
                     │                           │
                     ▼                           │
            ┌─────────────────┐                 │
            │ AI智能分析节点   │                 │
            └────────┬────────┘                 │
                     │                           │
                     ▼                           │
         ┌──────────────────────────┐           │
         │      模型训练节点          │           │
         │   (双输入: 特征+AI分析)   │           │
         └─────────────┬────────────┘           │
                       │                        │
                       ▼                        │
              ┌─────────────────┐              │
              │  初步验证节点    │              │
              └─────────────────┘              │
                                               │
                                               │
┌───────────────────────────┐                   │
│ AI助手策略构思节点         │───────────────────┘
│ (独立起点，输出到因子引擎) │
└───────────────────────────┘
```

---

## 创建清单

- [x] 股票选择节点 - 已完成
- [x] 指数选择节点 - 已完成
- [ ] 数据清洗节点 - 需要创建
- [ ] 因子计算引擎节点 - 部分完成，需要更新
- [ ] 特征工程节点 - 需要创建
- [ ] 智能信号引擎节点 - 需要创建
- [ ] AI智能分析节点 - 需要创建
- [ ] AI助手策略构思节点 - 需要创建
- [ ] 模型训练节点 - 需要更新
- [ ] 初步验证节点 - 需要创建

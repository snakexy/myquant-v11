/**
 * 模型训练节点配置
 *
 * 核心任务：机器学习模型训练和评估
 * 支持双输入：特征输入 + AI分析输入
 */

import type { BaseNodeConfig, NodeCategory, NodeDataType } from '../../base/BaseNode'

// 节点配置
export const modelTrainingConfig: BaseNodeConfig = {
  id: 'model-training',
  category: 'analysis' as NodeCategory,
  icon: '🎯',
  title: '模型训练',
  description: '机器学习模型训练',
  x: 1150,
  y: 100,
  // 双输入端口配置
  inputs: [
    { id: 'features', label: '特征输入', active: true },
    { id: 'ai-insights', label: 'AI分析输入', active: true }
  ],
  params: {
    // 模型类型
    modelType: 'xgboost',
    // 训练参数
    trainParams: {
      testSize: 0.2,
      cvFolds: 5,
      randomSeed: 42
    },
    // 特征列选择
    featureColumns: [],
    targetColumn: 'return',
    // 评估指标
    metrics: ['accuracy', 'precision', 'recall', 'sharpe', 'max-drawdown']
  },
  metadata: {
    data_source: 'models',
    api_endpoint: '/api/v1/models/train',
    version: '2.0',
    node_type: 'model_training',
    supports_dual_input: true
  },
  data: {
    type: 'stats' as NodeDataType,
    content: {
      modelName: '--',
      trainingStatus: 'pending',
      accuracy: '--',
      sharpe: '--'
    }
  }
}

// 默认参数
export const modelTrainingDefaultParams = {
  modelType: 'xgboost',
  trainParams: {
    testSize: 0.2,
    cvFolds: 5,
    randomSeed: 42
  },
  featureColumns: [],
  targetColumn: 'return',
  metrics: ['accuracy', 'precision', 'recall', 'sharpe', 'max-drawdown']
}

// 配置表单字段定义
export interface ConfigField {
  name: string
  label: string
  type: 'text' | 'number' | 'select' | 'multiselect' | 'date' | 'checkbox' | 'textarea'
  placeholder?: string
  options?: Array<{ label: string; value: any }>
  default?: any
  required?: boolean
  validation?: (value: any) => string | true
  description?: string
}

// 配置表单字段
export const modelTrainingConfigFields: ConfigField[] = [
  {
    name: 'modelType',
    label: '模型类型',
    type: 'select',
    options: [
      { label: 'XGBoost', value: 'xgboost' },
      { label: 'LightGBM', value: 'lightgbm' },
      { label: 'LSTM', value: 'lstm' },
      { label: 'Transformer', value: 'transformer' },
      { label: '线性回归', value: 'linear' },
      { label: '随机森林', value: 'random-forest' }
    ],
    default: 'xgboost',
    description: '选择要训练的模型类型'
  },
  {
    name: 'testSize',
    label: '测试集比例',
    type: 'number',
    default: 0.2,
    description: '测试集占总数据的比例（0-1之间）',
    validation: (value) => {
      if (value <= 0 || value >= 1) return '必须在0-1之间'
      return true
    }
  },
  {
    name: 'cvFolds',
    label: '交叉验证折数',
    type: 'number',
    default: 5,
    description: 'K折交叉验证的折数'
  },
  {
    name: 'randomSeed',
    label: '随机种子',
    type: 'number',
    default: 42,
    description: '用于结果复现的随机种子'
  },
  {
    name: 'targetColumn',
    label: '目标列',
    type: 'text',
    default: 'return',
    description: '预测目标变量的列名'
  },
  {
    name: 'metrics',
    label: '评估指标',
    type: 'multiselect',
    options: [
      { label: '准确率', value: 'accuracy' },
      { label: '精确率', value: 'precision' },
      { label: '召回率', value: 'recall' },
      { label: 'F1分数', value: 'f1' },
      { label: '夏普比率', value: 'sharpe' },
      { label: '最大回撤', value: 'max-drawdown' },
      { label: '胜率', value: 'win-rate' }
    ],
    default: ['accuracy', 'precision', 'recall', 'sharpe', 'max-drawdown']
  }
]

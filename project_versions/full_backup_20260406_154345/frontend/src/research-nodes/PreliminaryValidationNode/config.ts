/**
 * 初步验证节点配置
 *
 * 核心任务：模型性能初步验证
 * 终点节点
 */

import type { BaseNodeConfig, NodeCategory, NodeDataType } from '../../base/BaseNode'

// 节点配置
export const preliminaryValidationConfig: BaseNodeConfig = {
  id: 'preliminary-validation',
  category: 'output' as NodeCategory,
  icon: '✅',
  title: '初步验证',
  description: '模型性能初步验证',
  x: 1350,
  y: 100,
  params: {
    // 回测参数
    backtestPeriod: {
      start: '',
      end: ''
    },
    // 初始资金
    initialCapital: 100000,
    // 交易成本
    commission: 0.0003,
    slippage: 0.0001,
    // 评估选项
    metrics: ['return', 'sharpe', 'max-drawdown', 'win-rate', 'profit-factor']
  },
  metadata: {
    data_source: 'backtest',
    api_endpoint: '/api/v1/backtest/run',
    version: '2.0',
    node_type: 'preliminary_validation',
    is_end_node: true
  },
  data: {
    type: 'stats' as NodeDataType,
    content: {
      validationStatus: 'pending',
      totalReturn: '--',
      sharpeRatio: '--',
      maxDrawdown: '--',
      winRate: '--'
    }
  }
}

// 默认参数
export const preliminaryValidationDefaultParams = {
  backtestPeriod: {
    start: '',
    end: ''
  },
  initialCapital: 100000,
  commission: 0.0003,
  slippage: 0.0001,
  metrics: ['return', 'sharpe', 'max-drawdown', 'win-rate', 'profit-factor']
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
export const preliminaryValidationConfigFields: ConfigField[] = [
  {
    name: 'startDate',
    label: '回测开始日期',
    type: 'date',
    default: '',
    description: '回测的开始日期'
  },
  {
    name: 'endDate',
    label: '回测结束日期',
    type: 'date',
    default: '',
    description: '回测的结束日期'
  },
  {
    name: 'initialCapital',
    label: '初始资金',
    type: 'number',
    default: 100000,
    description: '回测的初始资金量'
  },
  {
    name: 'commission',
    label: '手续费率',
    type: 'number',
    default: 0.0003,
    description: '交易手续费率（默认万三）'
  },
  {
    name: 'slippage',
    label: '滑点率',
    type: 'number',
    default: 0.0001,
    description: '交易滑点率'
  },
  {
    name: 'metrics',
    label: '评估指标',
    type: 'multiselect',
    options: [
      { label: '总收益率', value: 'return' },
      { label: '年化收益率', value: 'annual-return' },
      { label: '夏普比率', value: 'sharpe' },
      { label: '最大回撤', value: 'max-drawdown' },
      { label: '胜率', value: 'win-rate' },
      { label: '盈亏比', value: 'profit-factor' }
    ],
    default: ['return', 'sharpe', 'max-drawdown', 'win-rate', 'profit-factor']
  }
]

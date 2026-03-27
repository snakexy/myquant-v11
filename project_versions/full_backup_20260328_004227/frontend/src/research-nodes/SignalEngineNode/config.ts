/**
 * 智能信号引擎节点配置
 *
 * 核心任务：技术分析和模式识别
 */

import type { BaseNodeConfig, NodeCategory, NodeDataType } from '../../base/BaseNode'

// 节点配置
export const signalEngineConfig: BaseNodeConfig = {
  id: 'signal-engine',
  category: 'analysis' as NodeCategory,
  icon: '📡',
  title: '智能信号引擎',
  description: '技术分析和模式识别',
  x: 750,
  y: 100,
  params: {
    // 技术指标
    indicators: {
      ma: true,
      maPeriods: [5, 10, 20, 60],
      macd: true,
      rsi: true,
      rsiPeriod: 14,
      bollinger: false,
      kdj: false
    },
    // 信号规则
    signalRules: {
      buyCondition: 'golden_cross',
      sellCondition: 'death_cross',
      strength: 0.7
    },
    // 模式检测
    patternDetection: true,
    patterns: ['trend', 'reversal', 'momentum']
  },
  metadata: {
    data_source: 'ai_realtime_processing',
    api_endpoint: '/api/v1/ai_realtime_processing/streams/create',
    version: '2.0',
    node_type: 'signal_engine'
  },
  data: {
    type: 'list' as NodeDataType,
    content: []
  }
}

// 默认参数
export const signalEngineDefaultParams = {
  indicators: {
    ma: true,
    maPeriods: [5, 10, 20, 60],
    macd: true,
    rsi: true,
    rsiPeriod: 14,
    bollinger: false,
    kdj: false
  },
  signalRules: {
    buyCondition: 'golden_cross',
    sellCondition: 'death_cross',
    strength: 0.7
  },
  patternDetection: true,
  patterns: ['trend', 'reversal', 'momentum']
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
export const signalEngineConfigFields: ConfigField[] = [
  {
    name: 'ma',
    label: '移动平均线 (MA)',
    type: 'checkbox',
    default: true,
    description: '启用移动平均线指标'
  },
  {
    name: 'maPeriods',
    label: 'MA周期',
    type: 'multiselect',
    options: [
      { label: '5日', value: 5 },
      { label: '10日', value: 10 },
      { label: '20日', value: 20 },
      { label: '60日', value: 60 }
    ],
    default: [5, 10, 20, 60],
    description: '选择要计算的MA周期'
  },
  {
    name: 'macd',
    label: 'MACD',
    type: 'checkbox',
    default: true,
    description: '启用MACD指标'
  },
  {
    name: 'rsi',
    label: '相对强弱指标 (RSI)',
    type: 'checkbox',
    default: true,
    description: '启用RSI指标'
  },
  {
    name: 'rsiPeriod',
    label: 'RSI周期',
    type: 'number',
    default: 14,
    description: 'RSI计算周期'
  },
  {
    name: 'bollinger',
    label: '布林带',
    type: 'checkbox',
    default: false,
    description: '启用布林带指标'
  },
  {
    name: 'kdj',
    label: 'KDJ',
    type: 'checkbox',
    default: false,
    description: '启用KDJ指标'
  },
  {
    name: 'patternDetection',
    label: '启用模式检测',
    type: 'checkbox',
    default: true,
    description: '检测价格形态和交易信号'
  },
  {
    name: 'patterns',
    label: '检测模式类型',
    type: 'multiselect',
    options: [
      { label: '趋势模式', value: 'trend' },
      { label: '反转模式', value: 'reversal' },
      { label: '动量模式', value: 'momentum' }
    ],
    default: ['trend', 'reversal', 'momentum']
  }
]

/**
 * 因子计算引擎节点配置
 *
 * 核心共享组件，支持双输入端：
 * - 数据驱动输入端：接收来自数据清洗的数据
 * - AI助手输入端：接收来自AI助手策略构思的数据
 */

import type { BaseNodeConfig, NodeCategory, NodeDataType } from '../../base/BaseNode'

// 节点配置
export const factorEngineConfig: BaseNodeConfig = {
  id: 'factor-engine',
  category: 'feature-engineering' as NodeCategory,
  icon: '🔬',
  title: '因子计算引擎',
  description: '计算Alpha因子，支持双输入',
  x: 350,
  y: 100,
  // 双输入端口配置
  inputs: [
    { id: 'data-driven', label: '数据驱动输入', active: true },
    { id: 'ai-driven', label: 'AI助手输入', active: true }
  ],
  params: {
    // Alpha158因子配置
    alpha158: true,
    // Alpha360因子配置
    alpha360: false,
    // 自定义因子
    customFactors: [],
    // 因子模板
    factorTemplate: 'default',
    // 计算选项
    normalize: true,
    neutralize: true
  },
  metadata: {
    data_source: 'factor_engine',
    api_endpoint: '/api/v1/factor_engine/calculate_factors',
    version: '2.0',
    node_type: 'factor_engine',
    supports_dual_input: true
  },
  data: {
    type: 'stats' as NodeDataType,
    content: {
      totalFactors: 0,
      calculatedFactors: [],
      calculationTime: '--'
    }
  }
}

// 默认参数
export const factorEngineDefaultParams = {
  // Alpha158因子
  alpha158: true,
  // Alpha360因子
  alpha360: false,
  // 自定义因子列表
  customFactors: [] as string[],
  // 因子模板选择
  factorTemplate: 'alpha158',
  // 数据标准化
  normalize: true,
  // 中性化处理
  neutralize: true,
  // 因子计算频率
  frequency: 'daily'
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
export const factorEngineConfigFields: ConfigField[] = [
  {
    name: 'factorTemplate',
    label: '因子模板',
    type: 'select',
    options: [
      { label: 'Alpha158', value: 'alpha158' },
      { label: 'Alpha360', value: 'alpha360' },
      { label: '自定义因子', value: 'custom' }
    ],
    default: 'alpha158',
    description: '选择预定义的因子模板或自定义因子'
  },
  {
    name: 'alpha158',
    label: 'Alpha158因子',
    type: 'checkbox',
    default: true,
    description: '计算经典的Alpha158因子集'
  },
  {
    name: 'alpha360',
    label: 'Alpha360因子',
    type: 'checkbox',
    default: false,
    description: '计算扩展的Alpha360因子集'
  },
  {
    name: 'customFactors',
    label: '自定义因子',
    type: 'textarea',
    placeholder: '输入自定义因子表达式，每行一个\n示例：\nclose / open - 1\nvolume / ma(volume, 20)',
    default: '',
    description: '自定义因子计算表达式'
  },
  {
    name: 'normalize',
    label: '数据标准化',
    type: 'checkbox',
    default: true,
    description: '对因子值进行标准化处理'
  },
  {
    name: 'neutralize',
    label: '中性化处理',
    type: 'checkbox',
    default: true,
    description: '去除市值和行业因子影响'
  },
  {
    name: 'frequency',
    label: '计算频率',
    type: 'select',
    options: [
      { label: '日线', value: 'daily' },
      { label: '周线', value: 'weekly' },
      { label: '月线', value: 'monthly' }
    ],
    default: 'daily'
  }
]

// 输入端口配置
export interface InputPortConfig {
  id: string
  label: string
  active: boolean
  description?: string
}

// 输入端口定义
export const factorEngineInputPorts: InputPortConfig[] = [
  {
    id: 'data-driven',
    label: '数据驱动输入',
    active: true,
    description: '接收来自数据清洗的标准量化数据'
  },
  {
    id: 'ai-driven',
    label: 'AI助手输入',
    active: true,
    description: '接收来自AI助手策略构思的数据'
  }
]

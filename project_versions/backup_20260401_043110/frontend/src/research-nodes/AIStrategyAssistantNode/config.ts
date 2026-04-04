/**
 * AI助手策略构思节点配置
 *
 * 核心任务：AI生成交易策略因子
 * 独立起点节点，输出到因子计算引擎节点的AI驱动输入端口
 */

import type { BaseNodeConfig, NodeCategory, NodeDataType } from '../../base/BaseNode'

// 节点配置
export const aiStrategyAssistantConfig: BaseNodeConfig = {
  id: 'ai-strategy-assistant',
  category: 'analysis' as NodeCategory,
  icon: '💡',
  title: 'AI助手策略构思',
  description: 'AI生成交易策略因子',
  x: 100,
  y: 500,
  params: {
    // 策略类型
    strategyType: 'trend-following',
    // 策略描述
    description: '',
    // 风险偏好
    riskLevel: 'moderate',
    // 生成选项
    includeStopLoss: true,
    includeTakeProfit: true
  },
  metadata: {
    data_source: 'strategy_generator',
    api_endpoint: '/api/v1/strategy_generator/strategies/generate',
    version: '2.0',
    node_type: 'ai_strategy_assistant',
    is_start_node: true  // 独立起点节点
  },
  data: {
    type: 'text' as NodeDataType,
    content: '等待生成策略...'
  }
}

// 默认参数
export const aiStrategyAssistantDefaultParams = {
  strategyType: 'trend-following',
  description: '',
  riskLevel: 'moderate',
  includeStopLoss: true,
  includeTakeProfit: true
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
export const aiStrategyAssistantConfigFields: ConfigField[] = [
  {
    name: 'strategyType',
    label: '策略类型',
    type: 'select',
    options: [
      { label: '趋势跟踪', value: 'trend-following' },
      { label: '均值回归', value: 'mean-reversion' },
      { label: '动量策略', value: 'momentum' },
      { label: '自定义', value: 'custom' }
    ],
    default: 'trend-following',
    description: '选择策略的基本类型'
  },
  {
    name: 'description',
    label: '策略描述',
    type: 'textarea',
    placeholder: '描述您想要的策略思路...\n例如：基于均线交叉的趋势跟踪策略，结合成交量确认',
    default: '',
    description: '详细描述您的策略想法，AI将根据描述生成因子'
  },
  {
    name: 'riskLevel',
    label: '风险偏好',
    type: 'select',
    options: [
      { label: '保守', value: 'conservative' },
      { label: '中等', value: 'moderate' },
      { label: '激进', value: 'aggressive' }
    ],
    default: 'moderate',
    description: '选择策略的风险等级'
  },
  {
    name: 'includeStopLoss',
    label: '包含止损',
    type: 'checkbox',
    default: true,
    description: '生成的策略包含止损条件'
  },
  {
    name: 'includeTakeProfit',
    label: '包含止盈',
    type: 'checkbox',
    default: true,
    description: '生成的策略包含止盈条件'
  }
]

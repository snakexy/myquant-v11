/**
 * AI智能分析节点配置
 *
 * 核心任务：AI驱动的市场分析和策略建议
 */

import type { BaseNodeConfig, NodeCategory, NodeDataType } from '../../base/BaseNode'

// 节点配置
export const aiAnalysisConfig: BaseNodeConfig = {
  id: 'ai-analysis',
  category: 'analysis' as NodeCategory,
  icon: '🤖',
  title: 'AI智能分析',
  description: 'AI驱动的市场分析',
  x: 950,
  y: 100,
  params: {
    // 分析类型
    analysisType: 'market-trend',
    // 分析深度
    depth: 'standard',
    // 输出格式
    outputFormat: 'detailed',
    // 其他选项
    includeCharts: true,
    includeRisk: true
  },
  metadata: {
    data_source: 'ai_assistant',
    api_endpoint: '/api/v1/ai_assistant/market-analysis',
    version: '2.0',
    node_type: 'ai_analysis'
  },
  data: {
    type: 'text' as NodeDataType,
    content: '等待执行AI分析...'
  }
}

// 默认参数
export const aiAnalysisDefaultParams = {
  analysisType: 'market-trend',
  depth: 'standard',
  outputFormat: 'detailed',
  includeCharts: true,
  includeRisk: true
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
export const aiAnalysisConfigFields: ConfigField[] = [
  {
    name: 'analysisType',
    label: '分析类型',
    type: 'select',
    options: [
      { label: '市场趋势分析', value: 'market-trend' },
      { label: '个股分析', value: 'individual-stock' },
      { label: '组合分析', value: 'portfolio' }
    ],
    default: 'market-trend',
    description: '选择分析的对象类型'
  },
  {
    name: 'depth',
    label: '分析深度',
    type: 'select',
    options: [
      { label: '基础', value: 'basic' },
      { label: '标准', value: 'standard' },
      { label: '综合', value: 'comprehensive' }
    ],
    default: 'standard',
    description: '选择分析的详细程度'
  },
  {
    name: 'outputFormat',
    label: '输出格式',
    type: 'select',
    options: [
      { label: '摘要', value: 'summary' },
      { label: '详细', value: 'detailed' },
      { label: '报告', value: 'report' }
    ],
    default: 'detailed',
    description: '选择输出内容的详细程度'
  },
  {
    name: 'includeCharts',
    label: '包含图表',
    type: 'checkbox',
    default: true,
    description: '生成图表分析'
  },
  {
    name: 'includeRisk',
    label: '包含风险评估',
    type: 'checkbox',
    default: true,
    description: '包含风险评估结果'
  }
]

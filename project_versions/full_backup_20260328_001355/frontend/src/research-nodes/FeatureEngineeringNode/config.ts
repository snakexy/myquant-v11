/**
 * 特征工程节点配置
 *
 * 核心任务：特征选择、转换和组合
 */

import type { BaseNodeConfig, NodeCategory, NodeDataType } from '../../base/BaseNode'

// 节点配置
export const featureEngineeringConfig: BaseNodeConfig = {
  id: 'feature-engineering',
  category: 'feature-engineering' as NodeCategory,
  icon: '🔧',
  title: '特征工程',
  description: '特征选择和转换',
  x: 550,
  y: 100,
  params: {
    // 特征选择方法
    selectionMethod: 'variance-threshold',
    kBest: 50,
    // 特征转换
    transformation: 'none',
    pcaComponents: 10,
    // 相关性过滤
    removeCorrelated: false,
    correlationThreshold: 0.95
  },
  metadata: {
    data_source: 'data_processors',
    api_endpoint: '/api/v1/data-processors/market-data',
    processing_type: 'feature_engineering',
    version: '2.0',
    node_type: 'feature_engineering'
  },
  data: {
    type: 'stats' as NodeDataType,
    content: {
      originalFeatures: 0,
      finalFeatures: 0,
      selectionRatio: 0,
      status: 'pending'
    }
  }
}

// 默认参数
export const featureEngineeringDefaultParams = {
  selectionMethod: 'variance-threshold',
  kBest: 50,
  transformation: 'none',
  pcaComponents: 10,
  removeCorrelated: false,
  correlationThreshold: 0.95
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
export const featureEngineeringConfigFields: ConfigField[] = [
  {
    name: 'selectionMethod',
    label: '特征选择方法',
    type: 'select',
    options: [
      { label: '方差阈值', value: 'variance-threshold' },
      { label: 'K个最佳特征', value: 'k-best' },
      { label: '递归特征消除', value: 'recursive' },
      { label: '特征重要性', value: 'importance' }
    ],
    default: 'variance-threshold',
    description: '选择特征筛选的方法'
  },
  {
    name: 'kBest',
    label: '保留特征数量',
    type: 'number',
    placeholder: '50',
    default: 50,
    description: '当使用K个最佳特征方法时，保留的特征数量',
    validation: (value) => {
      if (value <= 0) return '必须大于0'
      return true
    }
  },
  {
    name: 'transformation',
    label: '特征转换',
    type: 'select',
    options: [
      { label: '不转换', value: 'none' },
      { label: 'PCA降维', value: 'pca' },
      { label: '标准化', value: 'standardization' },
      { label: '归一化', value: 'normalization' }
    ],
    default: 'none'
  },
  {
    name: 'pcaComponents',
    label: 'PCA主成分数量',
    type: 'number',
    placeholder: '10',
    default: 10,
    description: 'PCA降维后保留的主成分数量'
  },
  {
    name: 'removeCorrelated',
    label: '移除高度相关特征',
    type: 'checkbox',
    default: false,
    description: '自动移除相关性过高的特征'
  },
  {
    name: 'correlationThreshold',
    label: '相关性阈值',
    type: 'number',
    placeholder: '0.95',
    default: 0.95,
    description: '特征相关性的阈值（0-1之间）'
  }
]

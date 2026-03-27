/**
 * 数据清洗节点配置
 *
 * 核心任务：将数据中枢的股票数据转换为QLib可用的数据格式
 * 保存路径：项目根目录 \data\qlib_data
 */

import type { BaseNodeConfig, NodeCategory, NodeDataType } from '../../base/BaseNode'

// 节点配置
export const dataCleaningConfig: BaseNodeConfig = {
  id: 'data-cleaning',
  category: 'data-processing' as NodeCategory,
  icon: '🗄️',
  title: '数据管理',
  description: '数据清洗和数据库管理',
  x: 100,
  y: 400,
  // 双输入端口配置
  inputs: [
    { id: 'stock-driven', label: '股票数据输入', active: true },
    { id: 'index-driven', label: '指数数据输入', active: true }
  ],
  params: {
    // 功能模式选择
    mode: 'cleaning', // 'cleaning' | 'database'
    // 数据清洗配置
    qlibDataPath: 'E:\\MyQuant_v8.0.1\\data\\qlib_data',
    frequency: 'daily',
    frequencies: ['daily'], // 多频率选择，新增字段
    dropMissing: true,
    maxMissingRatio: 0.3,
    forwardFill: true,
    handleOutliers: false,
    outlierMethod: 'clip',
    normalize: false,
    includeIndex: true,
    // 数据库管理配置
    database: {
      autoRefresh: false,
      showNeedsUpdateOnly: false,
      sortBy: 'code',
      sortOrder: 'asc',
      expiryThreshold: 7,
      batchUpdateLimit: 10
    }
  },
  metadata: {
    data_source: 'data_management',
    api_endpoint: '/api/v1/data-cleaning/clean',
    version: '3.0',
    node_type: 'data_management'
  },
  data: {
    type: 'stats' as NodeDataType,
    content: {}
  }
}

// 默认参数
export const dataCleaningDefaultParams = {
  mode: 'cleaning',
  qlibDataPath: 'E:\\MyQuant_v8.0.1\\data\\qlib_data',
  frequency: 'daily',
  frequencies: ['daily'], // 多频率选择，新增字段
  dropMissing: true,
  maxMissingRatio: 0.3,
  forwardFill: true,
  handleOutliers: false,
  outlierMethod: 'clip',
  normalize: false,
  includeIndex: true,
  database: {
    autoRefresh: false,
    showNeedsUpdateOnly: false,
    sortBy: 'code',
    sortOrder: 'asc',
    expiryThreshold: 7,
    batchUpdateLimit: 10
  }
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
export const dataCleaningConfigFields: ConfigField[] = [
  {
    name: 'qlibDataPath',
    label: 'QLib数据保存路径',
    type: 'text',
    placeholder: 'E:\\MyQuant_v8.0.1\\data\\qlib_data',
    default: 'E:\\MyQuant_v8.0.1\\data\\qlib_data',
    required: true,
    description: 'QLib格式数据保存的目录路径'
  },
  {
    name: 'frequency',
    label: '数据频率',
    type: 'select',
    options: [
      { label: '日线', value: 'daily' },
      { label: '1分钟', value: '1min' },
      { label: '5分钟', value: '5min' },
      { label: '15分钟', value: '15min' },
      { label: '30分钟', value: '30min' },
      { label: '60分钟', value: '60min' }
    ],
    default: 'daily'
  },
  {
    name: 'dropMissing',
    label: '删除缺失值过多的股票',
    type: 'checkbox',
    default: true,
    description: '自动删除数据缺失超过阈值的股票'
  },
  {
    name: 'maxMissingRatio',
    label: '最大缺失比例',
    type: 'number',
    placeholder: '0.3',
    default: 0.3,
    description: '允许的最大数据缺失比例（0-1之间）'
  },
  {
    name: 'forwardFill',
    label: '前向填充',
    type: 'checkbox',
    default: true,
    description: '用前一个有效值填充缺失值'
  },
  {
    name: 'handleOutliers',
    label: '处理异常值',
    type: 'checkbox',
    default: false,
    description: '启用异常值检测和处理'
  },
  {
    name: 'outlierMethod',
    label: '异常值处理方法',
    type: 'select',
    options: [
      { label: '截断', value: 'clip' },
      { label: '缩尾', value: 'winsorize' }
    ],
    default: 'clip'
  },
  {
    name: 'normalize',
    label: '标准化数据',
    type: 'checkbox',
    default: false,
    description: '对数据进行标准化处理'
  },
  {
    name: 'includeIndex',
    label: '包含指数数据',
    type: 'checkbox',
    default: false,
    description: '是否将上游指数数据一并转换'
  }
]

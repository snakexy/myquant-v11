/**
 * 股票选择节点配置
 */

import type { BaseNode, NodeCategory } from '../../types/node-definitions'

// 节点配置接口
export interface BaseNodeConfig extends BaseNode {
  category: NodeCategory
  params: Record<string, any>
  metadata: Record<string, any>
}

// 节点数据类型
export type NodeDataType = 'table' | 'stats' | 'list' | 'chart' | 'custom'

// 节点配置
export const stockSelectionConfig: BaseNodeConfig = {
  id: 'stock-selection',
  category: 'data-acquisition' as NodeCategory,
  icon: '📊',
  title: '股票选择',
  description: '选择股票并获取数据',
  x: 100,
  y: 100,
  params: {
    symbols: [], // 股票代码数组
    frequency: 'daily',
    frequencies: ['daily'], // 支持多频率选择
    adjust_type: 'qfq'
  },
  metadata: {
    data_source: 'unified_data_api',
    api_endpoint: '/unified_data/stock/',
    version: '2.0',
    node_type: 'simplified'
  },
  data: {
    type: 'table' as NodeDataType,
    content: []
  }
}

// 获取最后一个交易日的日期（使用标准交易日判断逻辑）
function getLastTradingDay(): string {
  const now = new Date()
  const currentHour = now.getHours()
  const currentMinute = now.getMinutes()
  
  // 检查是否是收盘时间之后（15:00）
  const isAfterMarketClose = currentHour > 15 || (currentHour === 15 && currentMinute >= 0)
  
  if (isAfterMarketClose) {
    // 收盘后，今天的数据应该已生成
    return formatDateToLocal(now)
  } else {
    // 收盘时间之前，今天的数据还未生成，最新可用数据应该是前一个交易日
    return getPreviousTradingDay(now)
  }
}

// 获取前一个交易日
function getPreviousTradingDay(currentDate: Date): string {
  const date = new Date(currentDate)
  
  // 向前查找最近的交易日（最多查找10天，覆盖最长假期）
  for (let delta = 1; delta <= 10; delta++) {
    const checkDate = new Date(date)
    checkDate.setDate(checkDate.getDate() - delta)
    
    if (isTradingDay(checkDate)) {
      return formatDateToLocal(checkDate)
    }
  }
  
  // 如果找不到交易日（极端情况），返回当前日期减1天
  const fallbackDate = new Date(date)
  fallbackDate.setDate(fallbackDate.getDate() - 1)
  return formatDateToLocal(fallbackDate)
}

// 格式化日期为本地日期字符串（YYYY-MM-DD）
function formatDateToLocal(date: Date): string {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

// 判断是否是交易日（周一到周五，排除节假日）
function isTradingDay(date: Date): boolean {
  // 周末不是交易日（0=周日, 6=周六）
  if (date.getDay() === 0 || date.getDay() === 6) {
    return false
  }
  
  // TODO: 可以添加节假日排除逻辑
  // 中国主要节假日：春节、国庆、清明节、劳动节、端午节、中秋节等
  
  return true
}

// 默认参数
export const stockSelectionDefaultParams = {
  stockCode: '',
  timeRange: '1M',
  startDate: '',
  endDate: getLastTradingDay(), // 默认为最后一个交易日的日期
  frequency: 'daily',
  frequencies: ['daily'], // 支持多频率选择
  includeDividends: false,
  adjustPrices: true,
  includeVolume: true,
  marketType: 'A股',
  stockType: 'all',
  sortBy: 'code',
  maxStocks: 50
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
export const stockSelectionConfigFields: ConfigField[] = [
  {
    name: 'stockCode',
    label: '股票代码',
    type: 'textarea',
    placeholder: '请输入股票代码，用逗号或换行分隔\n如：000001.SZ, 600036.SH',
    default: '',
    required: true
  },
  {
    name: 'timeRange',
    label: '时间范围',
    type: 'select',
    options: [
      { label: '近1周', value: '1W' },
      { label: '近1个月', value: '1M' },
      { label: '近3个月', value: '3M' },
      { label: '近6个月', value: '6M' },
      { label: '近1年', value: '1Y' },
      { label: '近2年', value: '2Y' }
    ],
    default: '1M'
  },
  {
    name: 'endDate',
    label: '结束日期',
    type: 'date',
    default: getLastTradingDay(), // 默认为最后一个交易日的日期
    description: '数据获取的结束日期，默认为最后一个交易日'
  },
  {
    name: 'frequency',
    label: '数据频率',
    type: 'select',
    options: [
      { label: '日线', value: 'daily' },
      { label: '周线', value: 'weekly' },
      { label: '月线', value: 'monthly' }
    ],
    default: 'daily'
  },
  {
    name: 'adjustPrices',
    label: '价格复权',
    type: 'checkbox',
    default: true,
    description: '对历史价格进行复权处理'
  },
  {
    name: 'includeVolume',
    label: '包含成交量',
    type: 'checkbox',
    default: true,
    description: '获取成交量数据'
  }
]

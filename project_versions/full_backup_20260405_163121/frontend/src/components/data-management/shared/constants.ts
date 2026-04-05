/**
 * 数据管理模块 - 常量定义
 */

import type { MarketType, FrequencyType } from './types'

// ==================== 市场配置 ====================

export const MARKET_CONFIG: Record<MarketType, { label: string; tagType: string }> = {
  sh: { label: '上海', tagType: 'success' },
  sz: { label: '深圳', tagType: 'warning' },
  bj: { label: '北交所', tagType: 'info' }
}

// ==================== 频率配置 ====================

export const FREQUENCY_CONFIG: Record<FrequencyType, { label: string; description: string; icon: string }> = {
  day: { label: '日线', description: '每日K线数据', icon: 'chart-line' },
  '1min': { label: '1分钟', description: '1分钟K线', icon: 'clock' },
  '5min': { label: '5分钟', description: '5分钟K线', icon: 'clock' },
  '15min': { label: '15分钟', description: '15分钟K线', icon: 'clock' },
  '30min': { label: '30分钟', description: '30分钟K线', icon: 'clock' },
  '60min': { label: '60分钟', description: '60分钟K线', icon: 'clock' },
  weekly: { label: '周线', description: '每周K线', icon: 'calendar-alt' },
  monthly: { label: '月线', description: '每月K线', icon: 'calendar-days' }
}

export const AVAILABLE_FREQUENCIES = [
  { value: 'day', label: '日线', icon: 'chart-line', description: '每日K线数据', source: 'direct' },
  { value: '1min', label: '1分钟', icon: 'clock', description: '1分钟K线', source: 'direct' },
  { value: '5min', label: '5分钟', icon: 'clock', description: '5分钟K线', source: 'direct' },
  { value: '15min', label: '15分钟', icon: 'clock', description: '15分钟K线', source: 'derived' },
  { value: '30min', label: '30分钟', icon: 'clock', description: '30分钟K线', source: 'derived' },
  { value: '60min', label: '60分钟', icon: 'clock', description: '60分钟K线', source: 'derived' },
  { value: 'weekly', label: '周线', icon: 'calendar-alt', description: '每周K线', source: 'derived' },
  { value: 'monthly', label: '月线', icon: 'calendar-days', description: '每月K线', source: 'derived' }
]

// ==================== 数据状态配置 ====================

export const DATA_STATUS_CONFIG = {
  complete: { label: '完整', type: 'success' },
  incomplete: { label: '不完整', type: 'warning' },
  need_update: { label: '需更新', type: 'danger' }
}

// ==================== 板块分类 ====================

export const SECTOR_CATEGORIES = [
  { id: 'industry', name: '行业板块', icon: 'industry' },
  { id: 'concept', name: '概念板块', icon: 'lightbulb' },
  { id: 'index', name: '指数板块', icon: 'chart-line' },
  { id: 'region', name: '地域板块', icon: 'map-marker-alt' }
]

// ==================== 导出格式 ====================

export const EXPORT_FORMATS = [
  { value: 'csv', label: 'CSV格式', extension: '.csv' },
  { value: 'excel', label: 'Excel格式', extension: '.xlsx' },
  { value: 'json', label: 'JSON格式', extension: '.json' }
]

// ==================== 时间范围 ====================

export const TIME_RANGES = [
  { value: '1week', label: '最近一周' },
  { value: '1month', label: '最近一个月' },
  { value: '3months', label: '最近三个月' },
  { value: '6months', label: '最近六个月' },
  { value: '1year', label: '最近一年' },
  { value: 'custom', label: '自定义时间范围' }
]

// ==================== 分页配置 ====================

export const PAGINATION_CONFIG = {
  pageSizes: [20, 50, 100, 200],
  defaultPageSize: 50
}

// ==================== 颜色主题 ====================

export const THEME_COLORS = {
  primary: '#2962ff',
  secondary: '#764ba2',
  success: '#10b981',
  warning: '#f59e0b',
  danger: '#ef4444',
  info: '#3b82f6',
  rise: '#ef4444',   // 涨（红色）
  fall: '#10b981'    // 跌（绿色）
}

// ==================== API端点 ====================

export const API_ENDPOINTS = {
  // 数据库管理
  DATABASE_SCAN: '/v1/database/scan',
  DATABASE_STATS: '/v1/database/statistics/summary',
  STOCK_LIST: '/v1/database/stocks/list',
  STOCK_DETAIL: '/v1/database/stocks',
  STOCK_UPDATE: '/v1/database/update/stocks',
  STOCK_DELETE: '/v1/database/stocks',

  // 数据源管理
  DATA_SOURCES: '/data-management/sources/list',
  TEST_CONNECTION: '/data-management/sources',
  TDX_DETECT: '/data-management/tdx/detect',
  TDX_CONVERT: '/data-management/tdx/convert',

  // 板块管理
  SECTORS: '/data-management/sectors',
  SECTOR_STOCKS: '/data-management/sectors',

  // 导出
  EXPORT: '/data-management/export'
}

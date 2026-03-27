/**
 * 数据管理模块 - 共享类型定义
 */

// ==================== 基础类型 ====================

export type MarketType = 'sh' | 'sz' | 'bj'
export type FrequencyType = 'day' | '1min' | '5min' | '15min' | '30min' | '60min' | 'weekly' | 'monthly'
export type DataStatus = 'complete' | 'incomplete' | 'need_update'

// ==================== 股票相关 ====================

export interface StockInfo {
  code: string
  name: string
  market: MarketType
  sector?: string
  industry?: string
}

export interface StockDataRecord {
  date: string
  open: number
  high: number
  low: number
  close: number
  volume: number
  amount: number
  change: number
}

export interface StockDetailInfo extends StockInfo {
  frequencies: FrequencyType[]
  dateRange: string
  recordCount: number
  status: DataStatus
  dataAgeDays: number
}

// ==================== 数据源相关 ====================

export interface DataSourceConfig {
  id: string
  name: string
  description: string
  type: 'api' | 'database' | 'file' | 'websocket'
  status: 'active' | 'inactive' | 'error' | 'loading' | 'development'
  statusText: string
  dataCount: string
  updateFreq: string
  latency: number
  successRate: number
}

export interface TDXInfo {
  dailyStocks: number
  minute5Stocks: number
  totalStocks: number
  dateRange: string
  lastUpdate?: string
  completeness?: number
  completenessDetails?: CompletenessDetail[]
  availableFrequencies: FrequencyType[]
  stockCounts?: GroupStockCounts
  fundCounts?: GroupStockCounts
  indexCounts?: GroupStockCounts
  otherCounts?: GroupStockCounts
}

export interface GroupStockCounts {
  day: number
  '5min': number
  '15min'?: number
  '30min'?: number
  '60min'?: number
}

export interface ConnectionStatus {
  connected: boolean
  message: string
}

export interface CompletenessDetail {
  label: string
  percent: number
  color: string
}

// ==================== 转换相关 ====================

export interface ConversionProgress {
  percent: number
  status: 'success' | 'exception' | 'warning' | undefined
  processed: number
  total: number
  currentStock?: string
  currentFrequency?: string
  elapsedTime?: string
}

export interface ConversionResult {
  success: boolean
  title: string
  message: string
  successCount: number
  failedCount: number
  totalTime: string
}

export interface ConversionOptions {
  forwardFill: boolean
  handleOutliers: boolean
  normalize: boolean
}

// ==================== 板块相关 ====================

export interface SectorNode {
  id: string
  name: string
  type: 'root' | 'category' | 'sector' | 'stock'
  stockCount?: number
  code?: string
  children?: SectorNode[]
  isLeaf?: boolean
  changePercent?: number
  amount?: string
}

export type SectorCategory = 'industry' | 'concept' | 'index' | 'region'

// 板块详细信息
export interface SectorBasicInfo {
  name: string
  type: string
  stockCount: number
  changePercent: number
  amount: string
  turnoverRate?: string
  description?: string
}

// 板块成分股信息
export interface SectorStockInfo {
  code: string
  name: string
  market: string
  industry?: string
  changePercent?: number
  contribution?: number
  amount?: string
}

// ==================== K线相关 ====================

export interface KlineData {
  date: string
  open: number
  close: number
  low: number
  high: number
  volume: number
  amount: number
}

export interface StockPrice {
  price: number
  changePercent: number
  changeAmount: number
  high: number
  low: number
  open: number
  volume: number
  amount: number
}

export interface KlineData {
  date: string
  open: number
  close: number
  low: number
  high: number
  volume: number
}

export interface StockDataRecord {
  date: string
  open: number
  high: number
  low: number
  close: number
  volume: number
  amount: number
  change: number
}

// ==================== 统计相关 ====================

export interface DatabaseStats {
  totalStocks: number
  totalRecords: number
  dateRange: string
  completeness?: number
  lastUpdate?: string
  // 以下字段用于 DatabaseManager 组件
  needsUpdate?: number
  healthyStocks?: number
}

export interface StockStats {
  recordCount: number
  dateRange: string
  completeness: number
  lastUpdate: string
}

// ==================== 筛选相关 ====================

export interface FilterOptions {
  market?: MarketType
  frequencies?: FrequencyType[]
  sector?: string
  status?: DataStatus
  keyword?: string
}

// ==================== API响应 ====================

export interface ApiResponse<T = any> {
  code: number
  message: string
  data: T
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  pageSize: number
}

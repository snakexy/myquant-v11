// API 类型定义

import type { 
  ApiResponse, 
  ErrorResponse, 
  PaginationParams, 
  SortParams,
  StockData,
  TechnicalIndicator,
  BacktestResult,
  BacktestConfig,
  StrategyConfig,
  RealtimeData,
  AlertRule,
  UserPreferences,
  SystemStatus,
  OrderInfo,
  PositionInfo,
  TradeRecord,
  RiskMetrics,
  NotificationMessage
} from '@/types/global'

// 数据API相关类型
export interface GetStockListParams extends PaginationParams {
  market?: string
  sector?: string
  industry?: string
  market_cap_min?: number
  market_cap_max?: number
  pe_min?: number
  pe_max?: number
  sort_by?: string
  sort_order?: 'asc' | 'desc'
}

export interface GetStockHistoryParams {
  symbol: string
  start_date: string
  end_date: string
  frequency?: '1m' | '5m' | '15m' | '30m' | '1h' | '1d' | '1w' | '1M'
  fields?: string[]
}

export interface GetTechnicalIndicatorsParams {
  symbol: string
  indicators: string[]
  start_date: string
  end_date: string
  params?: Record<string, any>
}

export interface GetRealtimeDataParams {
  symbols: string[]
  fields?: string[]
}

export interface GetMarketOverviewParams {
  market?: string
  date?: string
}

// 策略API相关类型
export interface CreateStrategyParams {
  name: string
  description: string
  type: string
  code: string
  parameters: Record<string, any>
  tags?: string[]
}

export interface UpdateStrategyParams extends Partial<CreateStrategyParams> {
  id: string
  version?: string
}

export interface GetStrategyListParams extends PaginationParams {
  type?: string
  author?: string
  tags?: string[]
  search?: string
}

export interface ValidateStrategyCodeParams {
  code: string
  language?: string
}

export interface CopyStrategyParams {
  id: string
  name: string
  description?: string
}

// 回测API相关类型
export interface RunBacktestParams extends BacktestConfig {
  name?: string
  description?: string
}

export interface GetBacktestListParams extends PaginationParams {
  strategy_id?: string
  status?: string
  start_date?: string
  end_date?: string
}

export interface GetBacktestDetailParams {
  id: string
  include_trades?: boolean
  include_positions?: boolean
  include_metrics?: boolean
}

export interface CompareBacktestParams {
  backtest_ids: string[]
  metrics?: string[]
}

// AI API相关类型
export interface ChatRequest {
  message: string
  context?: string
  conversation_id?: string
  parameters?: Record<string, any>
}

export interface ChatResponse {
  response: string
  conversation_id: string
  message_id: string
  timestamp: string
  strategy?: {
    id: string
    name: string
    description: string
    code: string
    parameters: Record<string, any>
  }
  suggestions?: string[]
  related_data?: any[]
}

export interface GenerateStrategyParams {
  requirements: string
  strategy_type?: string
  symbols?: string[]
  timeframe?: string
  risk_level?: string
}

export interface AnalyzeMarketParams {
  market?: string
  timeframe?: string
  indicators?: string[]
  focus_areas?: string[]
}

export interface ProcessVoiceCommandParams {
  command: string
  context?: string
  language?: string
}

export interface ProcessVoiceCommandResponse {
  result: string
  action?: {
    type: string
    path?: string
    parameters?: Record<string, any>
  }
  speech?: string
}

// 用户API相关类型
export interface LoginParams {
  username: string
  password: string
  captcha?: string
  remember_me?: boolean
}

export interface RegisterParams {
  username: string
  email: string
  password: string
  confirm_password: string
  captcha?: string
  invite_code?: string
}

export interface UpdateUserProfileParams {
  nickname?: string
  email?: string
  phone?: string
  avatar?: string
  bio?: string
}

export interface ChangePasswordParams {
  old_password: string
  new_password: string
  confirm_password: string
}

export interface ResetPasswordParams {
  email: string
  verification_code: string
  new_password: string
  confirm_password: string
}

// 通知API相关类型
export interface GetNotificationListParams extends PaginationParams {
  type?: string
  read?: boolean
  start_date?: string
  end_date?: string
}

export interface MarkNotificationReadParams {
  ids: string[]
  read?: boolean
}

export interface CreateNotificationParams {
  type: string
  title: string
  message: string
  recipients?: string[]
  action_url?: string
  metadata?: Record<string, any>
}

// 预警API相关类型
export interface CreateAlertRuleParams {
  name: string
  symbol: string
  indicator: string
  condition: string
  threshold: number
  comparison: 'greater_than' | 'less_than' | 'equal_to'
  notification_settings: {
    email: boolean
    sms: boolean
    webhook: boolean
  }
}

export interface UpdateAlertRuleParams extends Partial<CreateAlertRuleParams> {
  id: string
}

export interface GetAlertRuleListParams extends PaginationParams {
  symbol?: string
  enabled?: boolean
  alert_type?: string
}

export interface TestAlertRuleParams {
  id: string
  test_value?: number
}

// 系统API相关类型
export interface GetSystemStatusParams {
  include_metrics?: boolean
  include_logs?: boolean
  include_processes?: boolean
}

export interface GetSystemLogsParams extends PaginationParams {
  level?: string
  module?: string
  start_date?: string
  end_date?: string
  search?: string
}

export interface GetPerformanceMetricsParams {
  start_time?: string
  end_time?: string
  interval?: '1m' | '5m' | '15m' | '1h' | '1d'
  metrics?: string[]
}

// 数据管理API相关类型
export interface ImportDataParams {
  file: File
  type: string
  format?: string
  options?: Record<string, any>
}

export interface ExportDataParams {
  data_type: string
  format?: string
  filters?: Record<string, any>
  fields?: string[]
}

export interface ValidateDataParams {
  file: File
  type: string
  validation_rules?: string[]
}

export interface GetDataQualityParams {
  data_source: string
  table?: string
  date_range?: {
    start_date: string
    end_date: string
  }
}

// WebSocket API相关类型
export interface WebSocketSubscribeParams {
  channels: string[]
  symbols?: string[]
  fields?: string[]
}

export interface WebSocketUnsubscribeParams {
  channels?: string[]
  symbols?: string[]
}

export interface WebSocketMessage {
  channel: string
  data: any
  timestamp: string
  symbol?: string
}

// API响应包装类型
export type StockListResponse = ApiResponse<{
  stocks: StockData[]
  total: number
  summary: {
    total_count: number
    market_count: Record<string, number>
    sector_count: Record<string, number>
  }
}>

export type StockHistoryResponse = ApiResponse<{
  symbol: string
  data: Array<{
    date: string
    open: number
    high: number
    low: number
    close: number
    volume: number
    adj_close?: number
  }>
  metadata: {
    start_date: string
    end_date: string
    total_records: number
    frequency: string
  }
}>

export type TechnicalIndicatorsResponse = ApiResponse<{
  symbol: string
  indicators: TechnicalIndicator[]
  data: Record<string, any[]>
}>

export type RealtimeDataResponse = ApiResponse<{
  data: RealtimeData[]
  timestamp: string
  delay?: number
}>

export type StrategyListResponse = ApiResponse<{
  strategies: StrategyConfig[]
  total: number
  summary: {
    total_count: number
    type_count: Record<string, number>
    author_count: number
  }
}>

export type BacktestListResponse = ApiResponse<{
  backtests: BacktestResult[]
  total: number
  summary: {
    total_count: number
    status_count: Record<string, number>
    avg_return: number
    avg_sharpe: number
  }
}>

export type BacktestDetailResponse = ApiResponse<{
  backtest: BacktestResult
  trades?: TradeRecord[]
  positions?: PositionInfo[]
  equity_curve?: Array<{
    date: string
    equity: number
    returns: number
    benchmark?: number
  }>
  risk_metrics?: RiskMetrics
}>

export type NotificationListResponse = ApiResponse<{
  notifications: NotificationMessage[]
  total: number
  unread_count: number
}>

export type AlertRuleListResponse = ApiResponse<{
  rules: AlertRule[]
  total: number
  active_count: number
}>

export type SystemStatusResponse = ApiResponse<{
  status: SystemStatus
  metrics?: Record<string, any>
  logs?: Array<{
    level: string
    message: string
    timestamp: string
  }>
}>

export type PerformanceMetricsResponse = ApiResponse<{
  metrics: Record<string, any[]>
  summary: Record<string, number>
}>

export type DataQualityResponse = ApiResponse<{
  quality_score: number
  metrics: Record<string, number>
  issues: Array<{
    type: string
    count: number
    severity: string
    description: string
  }>
  recommendations: string[]
}>

// API错误类型
export interface ApiError extends ErrorResponse {
  endpoint?: string
  method?: string
  request_data?: any
}

// 请求配置类型
export interface RequestConfig {
  timeout?: number
  retries?: number
  retry_delay?: number
  headers?: Record<string, string>
  params?: Record<string, any>
  data?: any
}

// 上传进度类型
export interface UploadProgress {
  loaded: number
  total: number
  percentage: number
  speed: number
  time_remaining: number
}

// 批量操作类型
export interface BatchOperationParams<T> {
  items: T[]
  operation: 'create' | 'update' | 'delete'
  options?: Record<string, any>
}

export interface BatchOperationResult<T> {
  successful: T[]
  failed: Array<{
    item: T
    error: string
  }>
  summary: {
    total: number
    success_count: number
    failure_count: number
  }
}

// 缓存相关类型
export interface CacheConfig {
  ttl: number
  max_size?: number
  strategy?: 'lru' | 'fifo' | 'custom'
}

export interface CacheStats {
  hits: number
  misses: number
  hit_rate: number
  size: number
  max_size: number
}

// 分页响应类型
export interface PaginatedResponse<T> {
  data: T[]
  pagination: {
    current_page: number
    page_size: number
    total: number
    total_pages: number
    has_next: boolean
    has_prev: boolean
  }
}

// 搜索相关类型
export interface SearchParams {
  query: string
  type?: string
  filters?: Record<string, any>
  sort?: SortParams
  page?: number
  page_size?: number
}

export interface SearchResult<T> {
  items: T[]
  total: number
  took: number
  suggestions?: string[]
  facets?: Record<string, Array<{
    value: string
    count: number
  }>>
}

// 导出相关类型
export interface ExportOptions {
  format: 'csv' | 'excel' | 'json' | 'pdf'
  fields?: string[]
  filters?: Record<string, any>
  date_range?: {
    start_date: string
    end_date: string
  }
  compression?: boolean
}

// 导入相关类型
export interface ImportOptions {
  format: 'csv' | 'excel' | 'json'
  mapping?: Record<string, string>
  validation?: {
    enabled: boolean
    rules?: string[]
  }
  skip_duplicates?: boolean
  update_existing?: boolean
}

// 文件相关类型
export interface FileInfo {
  id: string
  name: string
  size: number
  type: string
  url: string
  created_at: string
  updated_at: string
  metadata?: Record<string, any>
}
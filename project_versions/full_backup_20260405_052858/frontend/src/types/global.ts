// 全局类型定义

// 主题类型
export type Theme = 'dark' | 'light'

// 屏幕尺寸断点
export type ScreenSize = 'xs' | 'sm' | 'md' | 'lg' | 'xl'

// 组件尺寸
export type ComponentSize = 'small' | 'medium' | 'large'

// 表格尺寸
export type TableSize = 'small' | 'middle' | 'large'

// 组件状态 - 包含所有可能的状态
export type ComponentStatus = 'default' | 'active' | 'disabled' | 'loading' | 'error' | 'wait' | 'process' | 'finish' | 'success' | 'normal' | 'exception' | 'pending' | 'partial' | 'draft' | 'inactive' | 'archived' | 'running' | 'stopped' | 'warning' | 'validating'

// 步骤条状态
export type StepStatus = 'wait' | 'process' | 'finish' | 'error'

// 进度条状态
export type ProgressStatus = 'normal' | 'exception' | 'active' | 'success'

// 颜色类型
export type ColorType = 'primary' | 'secondary' | 'success' | 'warning' | 'error' | 'info'

// 排序方向
export type SortDirection = 'asc' | 'desc'

// 加载状态
export type LoadingState = 'idle' | 'loading' | 'success' | 'error'

// 操作类型
export type ActionType = 'create' | 'read' | 'update' | 'delete'

// 文件类型
export type FileType = 'image' | 'document' | 'video' | 'audio' | 'archive'

// 语言类型
export type Language = 'zh' | 'en'

// 布局类型
export type LayoutType = 'grid' | 'list' | 'card' | 'table'

// 时间范围类型
export type TimeRangeType = '1d' | '1w' | '1m' | '3m' | '6m' | '1y' | 'all'

// 图表类型
export type ChartType = 'line' | 'bar' | 'candlestick' | 'area' | 'scatter' | 'pie' | 'heatmap'

// 策略类型
export type StrategyType = 'trend' | 'mean_reversion' | 'momentum' | 'arbitrage' | 'custom'

// 策略状态
export type StrategyStatus = 'draft' | 'active' | 'inactive' | 'archived'

// 交易方向
export type TradeDirection = 'long' | 'short' | 'both'

// 订单类型
export type OrderType = 'market' | 'limit' | 'stop' | 'stop_limit'

// 订单状态
export type OrderStatus = 'pending' | 'partial' | 'filled' | 'cancelled' | 'rejected'

// 持仓类型
export type PositionType = 'long' | 'short'

// 风险等级
export type RiskLevel = 'low' | 'medium' | 'high' | 'extreme'

// 通知类型
export type NotificationType = 'info' | 'success' | 'warning' | 'error'

// 预警类型
export type AlertType = 'price' | 'volume' | 'technical' | 'risk' | 'system'

// 数据源类型
export type DataSourceType = 'database' | 'api' | 'file' | 'realtime'

// 模型类型
export type ModelType = 'regression' | 'classification' | 'clustering' | 'deep_learning'

// 回测状态
export type BacktestStatus = 'pending' | 'running' | 'completed' | 'failed' | 'cancelled'

// 权限类型
export type PermissionType = 'read' | 'write' | 'admin' | 'owner'

// 用户角色
export type UserRole = 'guest' | 'user' | 'analyst' | 'admin' | 'super_admin'

// API响应类型
export interface ApiResponse<T = any> {
  success: boolean
  message: string
  data: T
  timestamp: string
  request_id?: string
}

// 错误响应类型
export interface ErrorResponse {
  success: false
  message: string
  error_code: string
  error_details?: any
  timestamp: string
  request_id?: string
}

// 分页参数
export interface PaginationParams {
  page: number
  page_size: number
  total?: number
}

// 排序参数
export interface SortParams {
  field: string
  order: 'asc' | 'desc'
}

// 时间范围
export interface TimeRange {
  start_date: string
  end_date: string
}

// 股票数据
export interface StockData {
  symbol: string
  name: string
  price: number
  change: number
  change_percent: number
  volume: number
  market_cap: number
  pe_ratio: number
}

// 技术指标数据
export interface TechnicalIndicator {
  name: string
  value: number
  signal: 'buy' | 'sell' | 'hold'
}

// 策略回测结果
export interface BacktestResult {
  strategy_id: string
  strategy_name: string
  symbols: string[]
  start_date: string
  end_date: string
  initial_capital: number
  final_capital: number
  total_return: number
  annual_return: number
  max_drawdown: number
  sharpe_ratio: number
  win_rate: number
  performance_metrics: Record<string, number>
}

// 架构图节点
export interface ArchitectureNode {
  id: string
  label: string
  type: 'data_source' | 'processor' | 'model' | 'strategy' | 'output'
  status: 'running' | 'stopped' | 'error' | 'warning'
  position: { x: number; y: number }
  data: Record<string, any>
}

// 架构图连接
export interface ArchitectureEdge {
  id: string
  from: string
  to: string
  type: 'data_flow' | 'control_flow'
  status: 'active' | 'inactive'
  data: Record<string, any>
}

// AI助手消息
export interface AIMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: string
  metadata?: Record<string, any>
}

// 实时监控数据
export interface RealtimeData {
  symbol: string
  price: number
  change: number
  change_percent: number
  volume: number
  timestamp: string
  indicators: Record<string, number>
}

// 预警规则
export interface AlertRule {
  id: string
  name: string
  symbol: string
  indicator: string
  condition: string
  threshold: number
  comparison: 'greater_than' | 'less_than' | 'equal_to'
  enabled: boolean
  notification_settings: {
    email: boolean
    sms: boolean
    webhook: boolean
  }
}

// 用户偏好设置
export interface UserPreferences {
  theme: Theme
  language: 'zh' | 'en'
  auto_refresh: boolean
  refresh_interval: number
  chart_type: 'candlestick' | 'line' | 'area'
  default_layout: 'grid' | 'list'
}

// 系统状态
export interface SystemStatus {
  cpu_usage: number
  memory_usage: number
  disk_usage: number
  network_status: 'good' | 'warning' | 'error'
  active_connections: number
  data_delay: number
  last_update: string
}

// 策略配置
export interface StrategyConfig {
  id: string
  name: string
  description: string
  type: StrategyType
  code: string
  parameters: Record<string, any>
  created_at: string
  updated_at: string
  version: string
  author: string
  tags: string[]
}

// 回测配置
export interface BacktestConfig {
  strategy_id: string
  symbols: string[]
  start_date: string
  end_date: string
  initial_capital: number
  commission: number
  slippage: number
  benchmark?: string
  parameters?: Record<string, any>
}

// 订单信息
export interface OrderInfo {
  id: string
  symbol: string
  type: OrderType
  direction: TradeDirection
  quantity: number
  price?: number
  status: OrderStatus
  created_at: string
  updated_at: string
  filled_quantity: number
  filled_price?: number
}

// 持仓信息
export interface PositionInfo {
  id: string
  symbol: string
  type: PositionType
  quantity: number
  avg_price: number
  current_price: number
  market_value: number
  unrealized_pnl: number
  unrealized_pnl_percent: number
  created_at: string
  updated_at: string
}

// 交易记录
export interface TradeRecord {
  id: string
  symbol: string
  type: OrderType
  direction: TradeDirection
  quantity: number
  price: number
  commission: number
  slippage: number
  timestamp: string
  strategy_id?: string
}

// 风险指标
export interface RiskMetrics {
  var: number // Value at Risk
  cvar: number // Conditional Value at Risk
  max_drawdown: number
  sharpe_ratio: number
  sortino_ratio: number
  beta: number
  alpha: number
  volatility: number
  correlation: Record<string, number>
}

// 通知消息
export interface NotificationMessage {
  id: string
  type: NotificationType
  title: string
  message: string
  timestamp: string
  read: boolean
  action_url?: string
  metadata?: Record<string, any>
}

// 文件上传信息
export interface UploadFileInfo {
  id: string
  name: string
  size: number
  type: FileType
  url: string
  upload_time: string
  status: 'uploading' | 'completed' | 'failed'
  progress: number
}

// 数据质量指标
export interface DataQualityMetrics {
  completeness: number // 完整性
  accuracy: number // 准确性
  consistency: number // 一致性
  timeliness: number // 及时性
  validity: number // 有效性
  uniqueness: number // 唯一性
  issues: DataQualityIssue[]
}

// 数据质量问题
export interface DataQualityIssue {
  id: string
  type: string
  description: string
  severity: 'low' | 'medium' | 'high' | 'critical'
  count: number
  affected_records: string[]
  suggested_fix: string
}

// 性能指标
export interface PerformanceMetrics {
  response_time: number
  throughput: number
  error_rate: number
  availability: number
  cpu_usage: number
  memory_usage: number
  disk_io: number
  network_io: number
}

// 用户活动记录
export interface UserActivity {
  id: string
  user_id: string
  action: string
  resource: string
  timestamp: string
  ip_address: string
  user_agent: string
  metadata?: Record<string, any>
}

// 系统日志
export interface SystemLog {
  id: string
  level: 'debug' | 'info' | 'warning' | 'error' | 'critical'
  message: string
  module: string
  timestamp: string
  user_id?: string
  session_id?: string
  context?: Record<string, any>
}

// API请求日志
export interface ApiRequestLog {
  id: string
  method: string
  endpoint: string
  status_code: number
  response_time: number
  request_size: number
  response_size: number
  user_id?: string
  timestamp: string
  ip_address: string
  user_agent: string
}

// 缓存信息
export interface CacheInfo {
  key: string
  type: string
  size: number
  ttl: number
  hits: number
  misses: number
  last_accessed: string
  created_at: string
}

// 任务信息
export interface TaskInfo {
  id: string
  name: string
  type: string
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled'
  progress: number
  created_at: string
  started_at?: string
  completed_at?: string
  error_message?: string
  result?: any
  metadata?: Record<string, any>
}

// WebSocket消息
export interface WebSocketMessage {
  type: string
  data: any
  timestamp: string
  id?: string
}

// 图表配置
export interface ChartConfig {
  type: ChartType
  title?: string
  subtitle?: string
  width?: number
  height?: number
  theme?: Theme
  animation?: boolean
  legend?: boolean
  grid?: boolean
  tooltip?: boolean
  colors?: string[]
  series: ChartSeries[]
}

// 图表系列
export interface ChartSeries {
  name: string
  type: ChartType
  data: any[]
  color?: string
  yAxisIndex?: number
  visible?: boolean
}

// 表格配置
export interface TableConfig {
  columns: TableColumn[]
  data: any[]
  pagination?: PaginationConfig
  sorting?: SortingConfig
  filtering?: FilteringConfig
  selection?: SelectionConfig
  actions?: TableAction[]
}

// 表格列
export interface TableColumn {
  key: string
  title: string
  width?: number
  sortable?: boolean
  filterable?: boolean
  resizable?: boolean
  fixed?: 'left' | 'right'
  render?: (value: any, record: any) => any
}

// 分页配置
export interface PaginationConfig {
  enabled: boolean
  page_size: number
  page_sizes?: number[]
  show_total?: boolean
  show_jumper?: boolean
  show_size_changer?: boolean
}

// 排序配置
export interface SortingConfig {
  enabled: boolean
  multiple?: boolean
  default_sort?: SortParams
}

// 过滤配置
export interface FilteringConfig {
  enabled: boolean
  filters: TableFilter[]
}

// 表格过滤器
export interface TableFilter {
  key: string
  type: 'text' | 'select' | 'date' | 'number' | 'boolean'
  options?: Array<{ label: string; value: any }>
  placeholder?: string
}

// 选择配置
export interface SelectionConfig {
  enabled: boolean
  type: 'single' | 'multiple'
  selected_row_keys?: any[]
}

// 表格操作
export interface TableAction {
  key: string
  label: string
  icon?: string
  type?: 'primary' | 'default' | 'danger'
  disabled?: (record: any) => boolean
  visible?: (record: any) => boolean
  action: (record: any) => void
}
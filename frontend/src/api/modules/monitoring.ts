/**
 * MyQuant v10.0.0 - Monitoring API
 * 实时监控相关API
 */

import { http } from '../request'

// ==================== 类型定义 ====================

// 概览指标
export interface OverviewMetrics {
  currentAssets: number
  totalReturn: number
  totalReturnRate: number
  maxDrawdown: number
  sharpeRatio: number
  updateTime: string
  trends: {
    assets: 'up' | 'down' | 'flat'
    return: 'up' | 'down' | 'flat'
    drawdown: 'up' | 'down' | 'flat'
    sharpe: 'up' | 'down' | 'flat'
  }
}

// 收益曲线数据点
export interface ReturnCurvePoint {
  time: string  // 时间戳
  value: number  // 收益值
  benchmark?: number  // 基准收益
}

// 风险指标
export interface RiskMetrics {
  maxDrawdown: number
  leverage: number
  concentration: number
  volatility: number
  status: 'normal' | 'attention' | 'warning'
}

// 持仓信息
export interface Position {
  symbol: string  // 股票代码
  name: string  // 股票名称
  quantity: number  // 持仓数量
  costPrice: number  // 成本价
  currentPrice: number  // 现价
  marketValue: number  // 市值
  profit: number  // 盈亏金额
  profitRate: number  // 盈亏比例
  weight: number  // 权重（%）
}

// 交易记录
export interface Trade {
  id: string
  time: string  // 交易时间
  symbol: string  // 股票代码
  name: string  // 股票名称
  type: 'buy' | 'sell'  // 交易类型
  quantity: number  // 数量
  price: number  // 价格
  amount: number  // 金额
}

// 预警消息
export interface AlertMessage {
  id: string
  type: 'warning' | 'error' | 'info'
  level: 'critical' | 'warning' | 'info'
  title: string
  message: string
  time: string
  read: boolean
}

// 时间周期
export type TimePeriod = 'day' | 'week' | 'month'

// ==================== 交易日历相关类型定义 ====================

// 交易日检查请求
export interface TradingDayCheckRequest {
  check_date: string  // 检查日期 (YYYY-MM-DD)
  market: string  // 市场代码 ('SH' 上海, 'SZ' 深圳)
}

// 交易日检查响应
export interface TradingDayCheckResponse {
  check_date: string
  market: string
  is_trading_day: boolean
  message: string
}

// 交易日历请求
export interface TradingCalendarRequest {
  market: string  // 市场代码 ('SH' 上海, 'SZ' 深圳)
  start_time: string  // 起始时间，8位字符串。为空表示当前市场首个交易日时间
  end_time: string  // 结束时间，8位字符串。为空表示当前时间
}

// 交易日历响应
export interface TradingCalendarResponse {
  market: string
  trading_days: string[]  // 交易日列表，格式为 'YYYYMMDD'
  count: number
  date_range: string
}

// 市场状态响应
export interface MarketStatus {
  market: string
  market_name: string
  is_trading: boolean
  current_time: string
  last_trading_day: string
  next_trading_day: string
  status_message: string
}

// ==================== 增量更新相关类型定义 ====================

// 增量更新任务状态
export interface UpdateTask {
  task_id: string
  task_type: string  // 'list', 'basic_info', 'history', 'incremental'
  status: string  // 'pending', 'running', 'completed', 'failed', 'cancelled'
  progress: number  // 0-100
  total: number
  processed: number
  error_count: number
  start_time: string
  end_time?: string
  message: string
  details?: any
}

// 更新进度信息
export interface UpdateProgress {
  task_id: string
  task_type: string
  status: string
  progress: number
  total: number
  processed: number
  current_operation: string
  estimated_remaining: string
  speed: string
}

// 更新日志
export interface UpdateLog {
  id: string
  time: string
  type: 'success' | 'warning' | 'error' | 'info'
  title: string
  message: string
  details?: any
}

// 更新计划
export interface UpdatePlan {
  plan_id: string
  plan_name: string
  description: string
  schedule: string  // cron expression or schedule type
  last_run: string
  next_run: string
  status: string
  update_types: string[]
}

// ==================== 数据源状态相关类型定义 ====================

// 数据源状态
export interface DataSource {
  id: string
  name: string
  type: string  // 'tushare', 'qmt', 'qlib', 'local_db', etc.
  status: 'active' | 'error' | 'disabled' | 'connecting'
  connection_url?: string
  last_check: string
  response_time: number  // 毫秒
  success_rate: number  // 百分比
  error_count: number
  description: string
  details?: any
}

// 数据源状态概览
export interface DataSourceOverview {
  total: number
  active: number
  error: number
  disabled: number
  overall_health: 'good' | 'warning' | 'error'
}

// 数据源切换请求
export interface DataSourceSwitchRequest {
  source: string  // 当前数据源
  target: string  // 目标数据源 (xtquant, tdxquant, pytdx, local_db)
}

// 数据源切换响应
export interface DataSourceSwitchResponse {
  source: string
  target: string
  status: string
  message: string
  effective_time: string
  current_mode: {
    mode: 'auto' | 'manual'
    mode_display: string
    forced_source: string | null
    force_mode_enabled_at: number | null
    force_duration_seconds?: number
    force_duration_display?: string
  }
  current_scenario: string
  monitoring_enabled: boolean
}

// 路由模式信息
export interface RouterModeInfo {
  mode: 'auto' | 'manual'
  mode_display: string
  forced_source: string | null
  force_mode_enabled_at: number | null
  force_duration_seconds?: number
  force_duration_display?: string
}

// ==================== 增量更新控制相关类型定义 ====================

// 增量更新触发请求
export interface IncrementalUpdateTriggerRequest {
  symbols?: string[]  // 股票代码列表（可选，为空则全部）
  strategy?: string  // 'auto', 'incremental', 'full'
  priority?: string  // 'high', 'normal', 'low'
}

// 增量更新状态
export interface IncrementalUpdateStatus {
  task_id: string
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled'
  progress: number  // 0-100
  total_symbols: number
  processed_symbols: number
  failed_symbols: number
  start_time: string
  elapsed_time: string
  estimated_remaining: string
  strategy: string
  priority: string
  error_message?: string
}

// 增量更新历史记录
export interface IncrementalUpdateHistory {
  id: string
  task_id: string
  task_type: string
  status: string
  start_time: string
  end_time?: string
  duration?: string
  symbols_count: number
  progress: number
  error_count: number
  strategy: string
  priority: string
}

// 增量更新策略信息
export interface IncrementalUpdateStrategy {
  strategy: string
  display_name: string
  description: string
  parameters: {
    max_concurrent: number
    batch_size: number
    debounce_interval: number
    retry_count: number
    retry_backoff_base: number
  }
}



// ==================== 归档管理相关类型定义 ====================

// 归档任务控制请求
export interface ArchiveTaskControlRequest {
  task_id: string
  action: 'pause' | 'resume' | 'retry' | 'skip' | 'delete'
}

// 归档任务
export interface ArchiveTask {
  id: string
  name: string
  symbol: string
  status: 'pending' | 'running' | 'paused' | 'completed' | 'failed' | 'skipped'
  progress: number
  total_symbols: number
  processed_symbols: number
  start_time: string
  end_time?: string
  error?: string
}

// 归档进度
export interface ArchiveProgress {
  task_id: string
  status: string
  progress: number
  total_symbols: number
  processed_symbols: number
  start_time: string
  end_time?: string
  duration?: string
  error?: string
}

// 归档统计
export interface ArchiveStats {
  total: number
  completed: number
  progress: number
  status: 'success' | 'warning' | 'exception'
  success: number
  failed: number
  skipped: number
  duration: string
}


// ==================== 数据质量相关类型定义 ====================

// 数据质量概览
export interface DataQualityOverview {
  total: number
  good: number
  warning: number
  bad: number
  quality_score: number  // 0-100
  last_check: string
}

// 数据质量问题（已废弃，使用 DataQualityAnomaly）
export interface DataQualityIssue {
  id: string
  issue: string  // 问题类型
  type: 'warning' | 'error' | 'info'
  count: number
  percentage: number
  description: string
  affected_symbols?: string[]
  suggestion: string
}

// 数据质量报告
export interface DataQualityReport {
  overview: DataQualityOverview
  issues: DataQualityIssue[]
  details: any
  timestamp: string
}

// 数据质量异常（后端返回格式）
export interface DataQualityAnomaly {
  id: string
  symbol: string
  name: string  // 股票名称
  type: string  // price/volume/missing/duplicate/format
  date: string  // 异常日期
  description: string  // 异常描述
  value: any  // 异常值
  expected_range?: string  // 预期范围
  status: string  // pending/processed/ignored
}

// 质量趋势数据点
export interface QualityTrendPoint {
  date: string  // 日期
  overall_score: number  // 综合质量评分
  completeness_score: number  // 完整性评分
  accuracy_score: number  // 准确性评分
  consistency_score: number  // 一致性评分
  anomaly_count: number  // 异常数量
}

// ==================== 归档管理相关类型定义 ====================

// 归档任务状态
export interface ArchiveTask {
  id: string
  name: string
  status: 'pending' | 'running' | 'completed' | 'paused' | 'failed'
  progress: number  // 0-100
  total_items: number
  processed_items: number
  success_count: number
  failed_count: number
  skipped_count: number
  start_time: string
  end_time?: string
  duration?: string
  error_message?: string
  config: {
    data_type: string  // 'daily', 'weekly', 'monthly', 'yearly'
    target_date: string
    compression_level: number
  }
}

// 归档统计
export interface ArchiveStats {
  total: number
  completed: number
  progress: number
  status: 'success' | 'warning' | 'exception'
  success: number
  failed: number
  skipped: number
  duration: string
}

// 归档报告
export interface ArchiveReport {
  task_id: string
  report_data: any
  generated_at: string
  download_url?: string
}

// ==================== API方法 ====================

export const monitoringApi = {
  /**
   * 获取概览指标
   * GET /api/v1/validation/monitoring/overview
   */
  getOverview(): Promise<{ code: number; data: OverviewMetrics; message: string }> {
    return http.get('/validation/monitoring/overview')
  },

  /**
   * 获取收益曲线数据
   * GET /api/v1/validation/monitoring/return-curve
   * @param period 时间周期（day/week/month）
   * @param startDate 开始日期
   * @param endDate 结束日期
   */
  getReturnCurve(
    period: TimePeriod = 'day',
    startDate?: string,
    endDate?: string
  ): Promise<{ code: number; data: ReturnCurvePoint[]; message: string }> {
    return http.get('/validation/monitoring/return-curve', {
      params: { period, startDate, endDate }
    })
  },

  /**
   * 获取风险指标
   * GET /api/v1/validation/monitoring/risk-metrics
   */
  getRiskMetrics(): Promise<{ code: number; data: RiskMetrics; message: string }> {
    return http.get('/validation/monitoring/risk-metrics')
  },

  /**
   * 获取当前持仓列表
   * GET /api/v1/validation/monitoring/positions
   */
  getPositions(): Promise<{ code: number; data: Position[]; message: string }> {
    return http.get('/validation/monitoring/positions')
  },

  /**
   * 获取交易记录
   * GET /api/v1/validation/monitoring/trades
   * @param limit 返回记录数量
   * @param startDate 开始日期（可选）
   * @param endDate 结束日期（可选）
   */
  getTrades(
    limit: number = 50,
    startDate?: string,
    endDate?: string
  ): Promise<{ code: number; data: Trade[]; message: string }> {
    return http.get('/validation/monitoring/trades', {
      params: { limit, startDate, endDate }
    })
  },

  /**
   * 获取预警消息
   * GET /api/v1/validation/monitoring/alerts
   * @param unreadOnly 是否只获取未读消息
   */
  getAlerts(unreadOnly: boolean = false): Promise<{ code: number; data: AlertMessage[]; message: string }> {
    return http.get('/validation/monitoring/alerts', {
      params: { unreadOnly }
    })
  },

  /**
   * 标记预警消息为已读
   * PUT /api/v1/validation/monitoring/alerts/{id}/read
   * @param alertId 预警消息ID
   */
  markAlertAsRead(alertId: string): Promise<{ code: number; data: { success: boolean }; message: string }> {
    return http.put(`/validation/monitoring/alerts/${alertId}/read`)
  },

  /**
   * 删除预警消息
   * DELETE /api/v1/validation/monitoring/alerts/{id}
   * @param alertId 预警消息ID
   */
  deleteAlert(alertId: string): Promise<{ code: number; data: { success: boolean }; message: string }> {
    return http.delete(`/validation/monitoring/alerts/${alertId}`)
  },

  /**
   * 批量标记预警消息为已读
   * PUT /api/v1/validation/monitoring/alerts/batch-read
   * @param alertIds 预警消息ID列表
   */
  batchMarkAlertsAsRead(alertIds: string[]): Promise<{ code: number; data: { success: boolean }; message: string }> {
    return http.put('/validation/monitoring/alerts/batch-read', { alertIds })
  },

  /**
   * 清空所有预警消息
   * DELETE /api/v1/validation/monitoring/alerts/all
   */
  clearAllAlerts(): Promise<{ code: number; data: { success: boolean }; message: string }> {
    return http.delete('/validation/monitoring/alerts/all')
  },

  /**
   * 刷新监控数据
   * GET /api/v1/validation/monitoring/refresh
   */
  refresh(): Promise<{
    code: number
    data: {
      overview: OverviewMetrics
      riskMetrics: RiskMetrics
      positions: Position[]
    }
    message: string
  }> {
    return http.get('/validation/monitoring/refresh')
  },

  // ==================== 交易日历相关API ====================

  /**
   * 检查是否为交易日
   * POST /api/v1/advanced-data-services/check-trading-day
   */
  checkTradingDay(request: TradingDayCheckRequest): Promise<{ code: number; data: TradingDayCheckResponse; message: string }> {
    return http.post('/advanced-data-services/check-trading-day', request)
  },

  /**
   * 获取交易日历
   * POST /api/v1/advanced-data-services/get-trading-calendar
   */
  getTradingCalendar(request: TradingCalendarRequest): Promise<{ code: number; data: TradingCalendarResponse; message: string }> {
    return http.post('/advanced-data-services/get-trading-calendar', request)
  },

  /**
   * 获取最后交易日
   * GET /api/v1/advanced-data-services/get-last-trading-day
   */
  getLastTradingDay(market: string = 'SH'): Promise<{ code: number; data: { last_trading_day: string; market: string }; message: string }> {
    return http.get('/advanced-data-services/get-last-trading-day', {
      params: { market }
    })
  },

  /**
   * 获取市场状态
   * GET /api/v1/advanced-data-services/get-market-status
   */
  getMarketStatus(market: string = 'SH'): Promise<{ code: number; data: MarketStatus; message: string }> {
    return http.get('/advanced-data-services/get-market-status', {
      params: { market }
    })
  },

  // ==================== 增量更新相关API ====================

  /**
   * 触发增量更新
   * POST /api/v1/stock-data-update/incremental-update
   */
  triggerIncrementalUpdate(params?: {
    symbols?: string[]
    start_date?: string
    end_date?: string
    frequency?: string
    source?: string
  }): Promise<{ code: number; data: { task_id: string; message: string }; message: string }> {
    return http.post('/stock-data-update/incremental-update', params || {})
  },

  /**
   * 获取任务状态
   * GET /api/v1/stock-data-update/tasks/{task_id}
   */
  getTaskStatus(taskId: string): Promise<{ code: number; data: UpdateTask; message: string }> {
    return http.get(`/stock-data-update/tasks/${taskId}`)
  },

  /**
   * 列出所有任务
   * GET /api/v1/stock-data-update/tasks
   */
  listTasks(params?: {
    limit?: number
    status?: string
    task_type?: string
  }): Promise<{ code: number; data: { tasks: UpdateTask[]; total: number }; message: string }> {
    return http.get('/stock-data-update/tasks', { params })
  },

  /**
   * 获取更新进度
   * GET /api/v1/stock-data-update/progress
   */
  getUpdateProgress(taskId?: string): Promise<{ code: number; data: UpdateProgress[]; message: string }> {
    return http.get('/stock-data-update/progress', {
      params: taskId ? { task_id: taskId } : {}
    })
  },

  /**
   * 获取更新计划
   * GET /api/v1/stock-data-update/update-plans
   */
  getUpdatePlans(): Promise<{ code: number; data: { plans: UpdatePlan[]; total: number }; message: string }> {
    return http.get('/stock-data-update/update-plans')
  },

  /**
   * 运行更新计划
   * POST /api/v1/stock-data-update/run-plan/{plan_id}
   */
  runUpdatePlan(planId: string): Promise<{ code: number; data: { task_id: string; message: string }; message: string }> {
    return http.post(`/stock-data-update/run-plan/${planId}`)
  },

  /**
   * 从数据库进行增量更新
   * POST /api/v1/stock-data-update/incremental-update-from-db
   */
  incrementalUpdateFromDatabase(params?: {
    symbols?: string[]
    start_date?: string
    end_date?: string
  }): Promise<{ code: number; data: { task_id: string; message: string }; message: string }> {
    return http.post('/stock-data-update/incremental-update-from-db', params || {})
  },

  // ==================== 数据源状态相关API ====================

  /**
   * 获取数据库状态
   * GET /api/v1/stock-data-update/database-status
   */
  getDatabaseStatus(): Promise<{ code: number; data: any; message: string }> {
    return http.get('/stock-data-update/database-status')
  },

  /**
   * 获取数据库中的股票列表
   * GET /api/v1/stock-data-update/database-stocks
   */
  getDatabaseStocks(params?: {
    limit?: number
    offset?: number
  }): Promise<{ code: number; data: any; message: string }> {
    return http.get('/stock-data-update/database-stocks', { params })
  },

  /**
   * 获取数据源状态
   * 这是一个通用的数据源状态查询接口
   */
  getDataSourceStatus(): Promise<{ code: number; data: { overview: DataSourceOverview; sources: DataSource[] }; message: string }> {
    // 使用数据库状态API作为基础数据源状态
    return http.get('/stock-data-update/database-status')
  },

  // ==================== 数据质量相关API ====================

  /**
   * 获取数据质量报告
   * GET /api/v1/data-management/data-quality/report
   */
  getDataQualityReport(params?: {
    symbol?: string
    data_type?: string
  }): Promise<{ code: number; data: { overview: any; anomalies: DataQualityAnomaly[] }; message: string }> {
    return http.get('/data-management/data-quality/report', {
      params: params || {}
    })
  },

  /**
   * 获取质量趋势
   * GET /api/v1/data-management/data-quality/trend
   */
  getDataQualityTrend(period: string = '7d'): Promise<{ code: number; data: any; message: string }> {
    return http.get('/data-management/data-quality/trend', {
      params: { period }
    })
  },

  /**
   * 获取异常数据列表
   * GET /api/v1/data-management/data-quality/anomalies
   */
  getDataQualityAnomalies(params?: {
    type?: string
    date_range?: string
    status?: string
    page?: number
    size?: number
  }): Promise<{ code: number; data: { anomalies: DataQualityIssue[]; total: number; pagination: any }; message: string }> {
    return http.get('/data-management/data-quality/anomalies', {
      params: params || {}
    })
  },

  /**
   * 检查数据质量
   * 对特定的数据源或数据集进行质量检查
   */
  checkDataQuality(params?: {
    data_source?: string
    symbols?: string[]
    date_range?: { start: string; end: string }
  }): Promise<{ code: number; data: DataQualityReport; message: string }> {
    return http.post('/data/quality-check', params || {})
  },

  // ==================== 性能统计相关API ====================

  /**
   * 获取数据源性能统计
   * GET /api/v1/data-management/data-source/performance
   */
  getDataSourcePerformance(): Promise<{ code: number; data: any; message: string }> {
    return http.get('/data-management/data-source/performance')
  },

  /**
   * 获取归档统计
   * GET /api/v1/data-management/archive/stats
   */
  getArchiveStats(): Promise<{ code: number; data: any; message: string }> {
    return http.get('/data-management/archive/stats')
  },

  /**
   * 获取增量更新策略（包含性能统计）
   * GET /api/v1/data-management/incremental-update/strategy
   */
  getIncrementalUpdateStrategy(): Promise<{ code: number; data: any; message: string }> {
    return http.get('/data-management/incremental-update/strategy')
  },

  // ==================== 归档管理相关API ====================

  /**
   * 开始归档任务
   * POST /api/v1/data/archive/start
   */
  startArchiveTask(params?: {
    data_type?: 'daily' | 'weekly' | 'monthly' | 'yearly'
    target_date?: string
    compression_level?: number
  }): Promise<{ code: number; data: { task_id: string; message: string }; message: string }> {
    return http.post('/data/archive/start', params || {})
  },

  /**
   * 暂停归档任务
   * POST /api/v1/data/archive/pause/{task_id}
   */
  pauseArchiveTask(taskId: string): Promise<{ code: number; data: { success: boolean; message: string }; message: string }> {
    return http.post(`/data/archive/pause/${taskId}`)
  },

  /**
   * 恢复归档任务
   * POST /api/v1/data/archive/resume/{task_id}
   */
  resumeArchiveTask(taskId: string): Promise<{ code: number; data: { success: boolean; message: string }; message: string }> {
    return http.post(`/data/archive/resume/${taskId}`)
  },

  /**
   * 获取归档任务列表
   * GET /api/v1/data/archive/tasks
   */
  getArchiveTasks(params?: {
    status?: string
    data_type?: string
    limit?: number
  }): Promise<{ code: number; data: { tasks: ArchiveTask[]; total: number }; message: string }> {
    return http.get('/data/archive/tasks', { params })
  },

  /**
   * 获取归档任务详情
   * GET /api/v1/data/archive/tasks/{task_id}
   */
  getArchiveTask(taskId: string): Promise<{ code: number; data: ArchiveTask; message: string }> {
    return http.get(`/data/archive/tasks/${taskId}`)
  },

  /**
   * 下载归档报告
   * GET /api/v1/data/archive/report/{task_id}
   */
  downloadArchiveReport(taskId: string): Promise<{ code: number; data: ArchiveReport; message: string }> {
    return http.get(`/data/archive/report/${taskId}`)
  },

  /**
   * 控制归档任务（暂停/恢复/重试/跳过/删除）
   * POST /api/v1/data-management/archive/control
   */
  controlArchiveTask(request: ArchiveTaskControlRequest): Promise<{ code: number; data: { success: boolean; message: string }; message: string }> {
    return http.post('/data-management/archive/control', request)
  },

  /**
   * 获取归档进度
   * GET /api/v1/data-management/archive/progress
   */
  getArchiveProgress(status?: string): Promise<{ code: number; data: { tasks: ArchiveTask[]; status_counts: any }; message: string }> {
    return http.get('/data-management/archive/progress', {
      params: status ? { status } : {}
    })
  },

  /**
   * 获取归档统计
   * GET /api/v1/data-management/archive/stats
   */
  getArchiveStats(): Promise<{ code: number; data: ArchiveStats; message: string }> {
    return http.get('/data-management/archive/stats')
  },

  // ==================== 数据源切换相关API ====================

  /**
   * 切换数据源（手动强制模式）
   * POST /api/v1/data-management/data-source/switch
   */
  switchDataSource(request: DataSourceSwitchRequest): Promise<{ code: number; data: DataSourceSwitchResponse; message: string }> {
    return http.post('/data-management/data-source/switch', request)
  },

  /**
   * 恢复数据源自动智能路由模式
   * POST /api/v1/data-management/data-source/reset-auto-mode
   */
  resetDataSourceAutoMode(): Promise<{ code: number; data: { status: string; message: string; current_mode: RouterModeInfo }; message: string }> {
    return http.post('/data-management/data-source/reset-auto-mode')
  },

  /**
   * 获取数据源路由推荐信息（包含当前模式）
   * GET /api/v1/data-management/data-source/recommendation
   */
  getDataSourceRecommendation(): Promise<{ code: number; data: { mode: RouterModeInfo; current_scenario: string; hot_stocks_count: number }; message: string }> {
    return http.get('/data-management/data-source/recommendation')
  },

  // ==================== 增量更新控制相关API ====================

  /**
   * 触发增量更新
   * POST /api/v1/data-management/incremental-update/trigger
   */
  triggerIncrementalUpdateControl(request: IncrementalUpdateTriggerRequest): Promise<{ code: number; data: { task_id: string; message: string }; message: string }> {
    return http.post('/data-management/incremental-update/trigger', request)
  },

  /**
   * 获取增量更新状态
   * GET /api/v1/data-management/incremental-update/status
   */
  getIncrementalUpdateStatus(taskId?: string): Promise<{ code: number; data: IncrementalUpdateStatus; message: string }> {
    return http.get('/data-management/incremental-update/status', {
      params: taskId ? { task_id: taskId } : {}
    })
  },

  /**
   * 获取增量更新历史
   * GET /api/v1/data-management/incremental-update/history
   */
  getIncrementalUpdateHistory(page: number = 1, size: number = 20): Promise<{ code: number; data: { history: IncrementalUpdateHistory[]; total: number; page: number; size: number }; message: string }> {
    return http.get('/data-management/incremental-update/history', {
      params: { page, size }
    })
  },

  /**
   * 获取增量更新策略
   * GET /api/v1/data-management/incremental-update/strategy
   */
  getIncrementalUpdateStrategy(): Promise<{ code: number; data: IncrementalUpdateStrategy; message: string }> {
    return http.get('/data-management/incremental-update/strategy')
  }
}

export default monitoringApi

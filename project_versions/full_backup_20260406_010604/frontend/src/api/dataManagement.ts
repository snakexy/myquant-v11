import { apiRequest } from './index'

// 数据管理API接口

// 数据库统计相关接口
export interface DatabaseStats {
  totalStocks: number
  totalRecords: string
  dataSize: string
  updateFrequency: string
  lastUpdateTime: string
  tableStats: Array<{
    tableName: string
    recordCount: number
    size: string
    lastUpdate: string
  }>
}

export const getDatabaseStats = (): Promise<DatabaseStats> => {
  // 模拟API调用，返回默认数据
  return Promise.resolve({
    totalStocks: 4856,
    totalRecords: '12.5M',
    dataSize: '8.2GB',
    updateFrequency: '实时',
    lastUpdateTime: new Date().toISOString(),
    tableStats: []
  })
}

// 数据新鲜度相关接口
export interface DataFreshness {
  overallScore: number
  latestUpdate: string
  delayedStocks: number
  missingData: number
  freshnessDetails: Array<{
    category: string
    score: number
    lastUpdate: string
    issueCount: number
  }>
  heatmapData: Array<{
    symbol: string
    name: string
    freshness: number
    lastUpdate: string
    status: 'fresh' | 'stale' | 'missing'
  }>
}

export const getDataFreshness = (): Promise<DataFreshness> => {
  // 模拟API调用，返回默认数据
  return Promise.resolve({
    overallScore: 94,
    latestUpdate: new Date().toLocaleString(),
    delayedStocks: 23,
    missingData: 5,
    freshnessDetails: [],
    heatmapData: []
  })
}

export const refreshDataFreshness = (): Promise<{ message: string }> => {
  // 模拟API调用
  return Promise.resolve({
    message: '数据新鲜度已刷新'
  })
}

// 股票分类统计相关接口
export interface StockCategory {
  id: string
  name: string
  count: number
  marketCap: string
  avgReturn: number
  changePercent: number
  topStocks: Array<{
    code: string
    name: string
    marketCap: string
    changePercent: number
  }>
}

export const getStockCategories = (): Promise<StockCategory[]> => {
  // 模拟API调用，返回默认数据
  return Promise.resolve([
    { id: 'all', name: '全部', count: 4856, marketCap: '68.2万亿', avgReturn: 2.3, changePercent: 1.2, topStocks: [] },
    { id: 'main', name: '主板', count: 1658, marketCap: '45.1万亿', avgReturn: 1.8, changePercent: 0.8, topStocks: [] },
    { id: 'sme', name: '中小板', count: 964, marketCap: '12.3万亿', avgReturn: 3.2, changePercent: 1.9, topStocks: [] },
    { id: 'chinext', name: '创业板', count: 1323, marketCap: '10.8万亿', avgReturn: 4.1, changePercent: 2.5, topStocks: [] },
    { id: 'star', name: '科创板', count: 568, marketCap: '2.8万亿', avgReturn: 5.6, changePercent: 3.8, topStocks: [] },
    { id: 'beijing', name: '北交所', count: 343, marketCap: '0.4万亿', avgReturn: 2.9, changePercent: 1.5, topStocks: [] }
  ])
}

export const getCategoryDetail = (categoryId: string): Promise<StockCategory> => {
  // 模拟API调用，返回默认数据
  const categories = [
    { id: 'all', name: '全部', count: 4856, marketCap: '68.2万亿', avgReturn: 2.3, changePercent: 1.2, topStocks: [] },
    { id: 'main', name: '主板', count: 1658, marketCap: '45.1万亿', avgReturn: 1.8, changePercent: 0.8, topStocks: [] },
    { id: 'sme', name: '中小板', count: 964, marketCap: '12.3万亿', avgReturn: 3.2, changePercent: 1.9, topStocks: [] },
    { id: 'chinext', name: '创业板', count: 1323, marketCap: '10.8万亿', avgReturn: 4.1, changePercent: 2.5, topStocks: [] },
    { id: 'star', name: '科创板', count: 568, marketCap: '2.8万亿', avgReturn: 5.6, changePercent: 3.8, topStocks: [] },
    { id: 'beijing', name: '北交所', count: 343, marketCap: '0.4万亿', avgReturn: 2.9, changePercent: 1.5, topStocks: [] }
  ]
  
  const category = categories.find(cat => cat.id === categoryId) || categories[0]
  return Promise.resolve(category)
}

// 数据源配置相关接口
export interface DataSource {
  id: string
  name: string
  enabled: boolean
  status: 'active' | 'inactive' | 'error'
  statusText: string
  hasError: boolean
  description?: string
  priority?: number
  features?: string[]
  lastUpdate?: string
  latency?: number
  errorCount?: number
  config?: Record<string, any>
}

export interface UpdateSchedule {
  id: string
  name: string
  schedule: string
  status: 'active' | 'waiting' | 'planned' | 'error'
  lastRun?: string
  nextRun?: string
  description: string
}

export const getDataSources = (): Promise<DataSource[]> => {
  // 从真实API获取数据源状态
  return apiRequest<any>('/data-management/sources/list')
    .then((response: any) => {
      if (response.success && response.data) {
        return response.data.map((source: any) => ({
          id: source.id,
          name: source.name,
          enabled: source.enabled,
          status: source.status,
          statusText: source.statusText,
          hasError: source.hasError,
          description: source.description,
          priority: source.priority,
          features: source.features || [],
          lastUpdate: source.lastUpdate,
          latency: source.latency,
          errorCount: source.errorCount,
          config: source.config
        }))
      } else {
        throw new Error(response.message || '获取数据源失败')
      }
    })
}

export const toggleDataSource = (sourceId: string): Promise<{ message: string }> => {
  // 模拟API调用
  return Promise.resolve({
    message: `数据源 ${sourceId} 状态已更新`
  })
}

export const configDataSource = (sourceId: string, config: Record<string, any>): Promise<{ message: string }> => {
  // 模拟API调用
  return Promise.resolve({
    message: `数据源 ${sourceId} 配置已更新`
  })
}

export const testDataSource = (sourceId: string): Promise<{ success: boolean, message: string, latency?: number }> => {
  // 模拟API调用
  return Promise.resolve({
    success: true,
    message: `数据源 ${sourceId} 连接测试成功`,
    latency: Math.floor(Math.random() * 100) + 20
  })
}

export const getUpdateSchedules = (): Promise<UpdateSchedule[]> => {
  // 模拟API调用，返回默认数据
  return Promise.resolve([
    {
      id: 'realtime_data',
      name: '实时数据更新',
      schedule: '每5秒',
      status: 'active',
      lastRun: new Date().toISOString(),
      nextRun: new Date().toISOString(),
      description: 'QMT优先获取实时行情数据'
    },
    {
      id: 'daily_kline',
      name: '日K线数据更新',
      schedule: '每日16:00',
      status: 'waiting',
      lastRun: new Date().toISOString(),
      nextRun: new Date().toISOString(),
      description: 'QMT/通达信获取日K线数据'
    },
    {
      id: 'stock_list',
      name: '股票列表更新',
      schedule: '每周一08:00',
      status: 'waiting',
      lastRun: new Date().toISOString(),
      nextRun: new Date().toISOString(),
      description: '更新股票基本信息列表'
    },
    {
      id: 'cache_update',
      name: '缓存更新',
      schedule: '实时 (增量更新)',
      status: 'active',
      lastRun: new Date().toISOString(),
      nextRun: new Date().toISOString(),
      description: '本地缓存增量更新'
    },
    {
      id: 'data_backup',
      name: '数据备份',
      schedule: '每周日03:00',
      status: 'planned',
      lastRun: new Date().toISOString(),
      nextRun: new Date().toISOString(),
      description: '全量数据备份到存储系统'
    }
  ])
}

export const runUpdateSchedule = (scheduleId: string): Promise<{ message: string }> => {
  // 模拟API调用
  return Promise.resolve({
    message: `更新计划 ${scheduleId} 已启动`
  })
}

// 数据操作相关接口
export interface DataSyncParams {
  source: string
  symbols?: string[]
  startDate?: string
  endDate?: string
  force?: boolean
}

export const syncData = (params: DataSyncParams): Promise<{
  message: string
  taskId: string
  estimatedTime?: number
}> => {
  // 模拟API调用
  return Promise.resolve({
    message: `数据同步已启动`,
    taskId: `sync_${Date.now()}`,
    estimatedTime: 300
  })
}

export interface DataExportParams {
  dataType: 'stocks' | 'history' | 'indicators' | 'all'
  format: 'csv' | 'excel' | 'json'
  filters?: Record<string, any>
  fields?: string[]
  startDate?: string
  endDate?: string
}

export const exportData = (params: DataExportParams): Promise<{
  message: string
  downloadUrl: string
  fileId: string
}> => {
  // 模拟API调用
  const fileId = `export_${Date.now()}`
  return Promise.resolve({
    message: '数据导出任务已创建',
    downloadUrl: `/api/download/${fileId}`,
    fileId
  })
}

export interface DataImportParams {
  file: File
  dataType: string
  format?: string
  options?: Record<string, any>
  overwrite?: boolean
}

export const importData = (params: DataImportParams): Promise<{
  message: string
  taskId: string
  preview?: any
}> => {
  // 模拟API调用
  return Promise.resolve({
    message: '数据导入任务已创建',
    taskId: `import_${Date.now()}`,
    preview: {
      totalRows: 1000,
      validRows: 950,
      invalidRows: 50
    }
  })
}

// 任务管理相关接口
export interface TaskInfo {
  id: string
  type: 'sync' | 'export' | 'import' | 'refresh'
  name: string
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled'
  progress: number
  startTime: string
  endTime?: string
  message?: string
  result?: any
}

export const getTaskList = (): Promise<TaskInfo[]> => {
  // 模拟API调用，返回默认数据
  return Promise.resolve([
    {
      id: 'task_1',
      type: 'sync',
      name: '数据同步任务',
      status: 'completed',
      progress: 100,
      startTime: new Date(Date.now() - 3600000).toISOString(),
      endTime: new Date(Date.now() - 3000000).toISOString(),
      message: '同步完成'
    },
    {
      id: 'task_2',
      type: 'export',
      name: '数据导出任务',
      status: 'running',
      progress: 65,
      startTime: new Date(Date.now() - 1800000).toISOString(),
      message: '正在导出'
    }
  ])
}

export const getTaskDetail = (taskId: string): Promise<TaskInfo> => {
  // 模拟API调用，返回默认数据
  return Promise.resolve({
    id: taskId,
    type: 'sync',
    name: '数据同步任务',
    status: 'completed',
    progress: 100,
    startTime: new Date(Date.now() - 3600000).toISOString(),
    endTime: new Date(Date.now() - 3000000).toISOString(),
    message: '同步完成'
  })
}

export const cancelTask = (taskId: string): Promise<{ message: string }> => {
  // 模拟API调用
  return Promise.resolve({
    message: `任务 ${taskId} 已取消`
  })
}

export const retryTask = (taskId: string): Promise<{ message: string }> => {
  // 模拟API调用
  return Promise.resolve({
    message: `任务 ${taskId} 已重试`
  })
}

// 系统监控相关接口
export interface SystemMetrics {
  cpu: {
    usage: number
    cores: number
  }
  memory: {
    used: number
    total: number
    usage: number
  }
  disk: {
    used: number
    total: number
    usage: number
  }
  network: {
    inbound: number
    outbound: number
  }
  database: {
    connections: number
    queries: number
    latency: number
  }
}

export const getSystemMetrics = (): Promise<SystemMetrics> => {
  // 模拟API调用，返回默认数据
  return Promise.resolve({
    cpu: { usage: 45, cores: 8 },
    memory: { used: 8.2, total: 16, usage: 51.2 },
    disk: { used: 250, total: 500, usage: 50 },
    network: { inbound: 1024, outbound: 2048 },
    database: { connections: 25, queries: 150, latency: 12 }
  })
}

export interface SystemLogs {
  logs: Array<{
    level: 'debug' | 'info' | 'warning' | 'error'
    module: string
    message: string
    timestamp: string
    details?: any
  }>
  total: number
  hasMore: boolean
}

export const getSystemLogs = (params?: {
  level?: string
  module?: string
  startTime?: string
  endTime?: string
  limit?: number
  offset?: number
}): Promise<SystemLogs> => {
  // 模拟API调用，返回默认数据
  return Promise.resolve({
    logs: [
      {
        level: 'info',
        module: 'data-sync',
        message: '数据同步完成',
        timestamp: new Date().toISOString()
      },
      {
        level: 'warning',
        module: 'cache',
        message: '缓存使用率过高',
        timestamp: new Date(Date.now() - 600000).toISOString()
      }
    ],
    total: 2,
    hasMore: false
  })
}

// 数据质量相关接口
export interface DataQualityReport {
  overallScore: number
  completeness: number
  accuracy: number
  timeliness: number
  consistency: number
  issues: Array<{
    type: string
    severity: 'low' | 'medium' | 'high' | 'critical'
    count: number
    description: string
    affectedItems?: string[]
  }>
  recommendations: string[]
  lastCheck: string
}

export const getDataQualityReport = (params?: {
  dataSource?: string
  table?: string
  dateRange?: {
    startDate: string
    endDate: string
  }
}): Promise<DataQualityReport> => {
  // 模拟API调用，返回默认数据
  return Promise.resolve({
    overallScore: 92,
    completeness: 95,
    accuracy: 90,
    timeliness: 88,
    consistency: 94,
    issues: [
      {
        type: 'missing_data',
        severity: 'medium',
        count: 23,
        description: '部分股票数据缺失',
        affectedItems: ['000001.SZ', '000002.SZ']
      }
    ],
    recommendations: ['增加数据更新频率', '优化数据验证规则'],
    lastCheck: new Date().toISOString()
  })
}

export const runDataQualityCheck = (params?: {
  dataSource?: string
  table?: string
  rules?: string[]
}): Promise<{ message: string, taskId: string }> => {
  // 模拟API调用
  return Promise.resolve({
    message: '数据质量检查已启动',
    taskId: `quality_${Date.now()}`
  })
}

// WebSocket 实时数据接口
export interface DataManagementWebSocket {
  // 订阅任务进度更新
  subscribeTaskProgress: (callback: (task: TaskInfo) => void) => void
  // 订阅系统指标更新
  subscribeSystemMetrics: (callback: (metrics: SystemMetrics) => void) => void
  // 订阅数据源状态更新
  subscribeDataSourceStatus: (callback: (source: DataSource) => void) => void
  // 取消订阅
  unsubscribe: (channel: string) => void
}

// 创建数据管理WebSocket连接
export const createDataManagementWebSocket = (): DataManagementWebSocket => {
  // 模拟WebSocket连接
  const subscriptions = new Map<string, Function>()
  
  return {
    subscribeTaskProgress: (callback) => {
      subscriptions.set('task_progress', callback)
      console.log('已订阅任务进度更新')
    },
    subscribeSystemMetrics: (callback) => {
      subscriptions.set('system_metrics', callback)
      console.log('已订阅系统指标更新')
    },
    subscribeDataSourceStatus: (callback) => {
      subscriptions.set('datasource_status', callback)
      console.log('已订阅数据源状态更新')
    },
    unsubscribe: (channel) => {
      subscriptions.delete(channel)
      console.log(`已取消订阅 ${channel}`)
    }
  }
}

// 数据时间范围相关接口
export interface DateRangeSegment {
  startDate: string  // YYYY-MM-DD 格式
  endDate: string    // YYYY-MM-DD 格式
  hasData: boolean
  dataCount?: number
  label?: string     // 悬停时显示的标签
}

export interface FrequencyTimeRange {
  frequency: string       // 'day', '5min', '1min', '30min', '60min'
  frequencyLabel: string  // '日线', '5分钟', '1分钟', '30分钟', '60分钟'
  startDate: string       // 整体开始日期
  endDate: string         // 整体结束日期
  segments: DateRangeSegment[]  // 时间段列表
  coverage: number        // 覆盖率百分比
  gaps: number            // 缺失段数
}

export interface DataTimeRangeDetail {
  sourcePath: string
  frequencyRanges: FrequencyTimeRange[]
}

export const getDataTimeRangeDetail = (params: {
  sourcePath?: string
}): Promise<DataTimeRangeDetail> => {
  // 调用真实API获取详细的时间范围数据
  return apiRequest<DataTimeRangeDetail>('/data-management/sources/time-range-detail', {
    method: 'POST',
    data: params
  })
}

// 默认导出所有接口
export default {
  // 数据库统计
  getDatabaseStats,

  // 数据新鲜度
  getDataFreshness,
  refreshDataFreshness,

  // 股票分类
  getStockCategories,
  getCategoryDetail,

  // 数据源配置
  getDataSources,
  toggleDataSource,
  configDataSource,
  testDataSource,
  getUpdateSchedules,
  runUpdateSchedule,

  // 数据操作
  syncData,
  exportData,
  importData,

  // 任务管理
  getTaskList,
  getTaskDetail,
  cancelTask,
  retryTask,

  // 系统监控
  getSystemMetrics,
  getSystemLogs,

  // 数据质量
  getDataQualityReport,
  runDataQualityCheck,

  // 数据时间范围
  getDataTimeRangeDetail,

  // WebSocket
  createDataManagementWebSocket
}
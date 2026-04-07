/**
 * 统一回测API客户端
 * 基于M3-3实现的统一回测API后端
 * @date 2026-02-07
 */

import request from './request'

// ========== TypeScript类型定义 ==========

/**
 * 任务状态枚举
 */
export enum TaskStatus {
  PENDING = 'pending',
  RUNNING = 'running',
  COMPLETED = 'completed',
  FAILED = 'failed',
  CANCELLED = 'cancelled'
}

/**
 * 回测执行请求
 */
export interface BacktestExecuteRequest {
  strategy_name: string
  start_date: string // YYYY-MM-DD
  end_date: string // YYYY-MM-DD
  initial_capital: number
  symbols: string[]
  benchmark?: string
  strategy_type?: string
  parameters?: Record<string, any>
  commission?: number
  slippage?: number
}

/**
 * 回测执行响应
 */
export interface BacktestExecuteResponse {
  code: number
  message: string
  data: {
    task_id: string
    status: string
    estimated_time: string
    submitted_at: string
  }
}

/**
 * 任务状态响应
 */
export interface TaskStatusResponse {
  task_id: string
  status: TaskStatus
  progress: number // 0-1
  current_step?: string
  started_at?: string
  completed_at?: string
  estimated_completion?: string
  error_message?: string
}

/**
 * 绩效指标
 */
export interface PerformanceMetrics {
  total_return: number
  annual_return: number
  max_drawdown: number
  sharpe_ratio: number
  win_rate: number
  profit_loss_ratio: number
}

/**
 * 净值曲线项
 */
export interface NavCurveItem {
  date: string
  value: number
  benchmark: number
}

/**
 * 持仓记录
 */
export interface PositionRecord {
  date: string
  symbol: string
  amount: number
  value: number
}

/**
 * 交易记录
 */
export interface TransactionRecord {
  date: string
  symbol: string
  action: 'buy' | 'sell'
  amount: number
  price: number
  value: number
}

/**
 * 回测结果数据
 */
export interface BacktestResultData {
  task_id: string
  strategy_name: string
  period: string
  initial_capital: number
  final_capital: number
  performance_metrics: PerformanceMetrics
  nav_curve: NavCurveItem[]
  positions: PositionRecord[]
  transactions: TransactionRecord[]
}

/**
 * 回测结果响应
 */
export interface BacktestResultResponse {
  code: number
  message: string
  data: BacktestResultData
}

/**
 * 任务摘要
 */
export interface TaskSummary {
  task_id: string
  strategy_name: string
  period: string
  status: TaskStatus
  total_return?: number
  sharpe_ratio?: number
  created_at: string
  completed_at?: string
}

/**
 * 任务列表响应
 */
export interface TaskListResponse {
  code: number
  message: string
  data: {
    total: number
    page: number
    page_size: number
    tasks: TaskSummary[]
  }
}

/**
 * 回测对比请求
 */
export interface BacktestCompareRequest {
  task_ids: string[]
  compare_metrics: string[]
}

/**
 * 回测对比响应
 */
export interface BacktestCompareResponse {
  code: number
  message: string
  data: {
    comparison_table: {
      task_id: string[]
      strategy_name: string[]
      total_return?: number[]
      annual_return?: number[]
      max_drawdown?: number[]
      sharpe_ratio?: number[]
      win_rate?: number[]
      profit_loss_ratio?: number[]
    }
    best_performer: Record<string, string>
    nav_curves: Record<string, NavCurveItem[]>
  }
}

/**
 * 导出响应
 */
export interface ExportResponse {
  code: number
  message: string
  data: {
    download_url: string
    expires_at: string
    file_size: string
  }
}

// ========== API方法 ==========

/**
 * 提交回测任务
 * @param request 回测执行请求
 * @returns 任务ID和状态信息
 */
export const executeBacktest = async (
  request: BacktestExecuteRequest
): Promise<BacktestExecuteResponse['data']> => {
  try {
    const response = await request<BacktestExecuteResponse>({
      url: '/api/v1/backtest/execute',
      method: 'POST',
      data: request
    })
    return response.data
  } catch (error) {
    console.error('提交回测任务失败:', error)
    throw error
  }
}

/**
 * 查询任务状态
 * @param taskId 任务ID
 * @returns 任务状态信息
 */
export const getTaskStatus = async (
  taskId: string
): Promise<TaskStatusResponse> => {
  try {
    const response = await request<{ code: number; message: string; data: TaskStatusResponse }>({
      url: `/api/v1/backtest/tasks/${taskId}/status`,
      method: 'GET'
    })
    return response.data
  } catch (error) {
    console.error('查询任务状态失败:', error)
    throw error
  }
}

/**
 * 获取回测结果
 * @param taskId 任务ID
 * @param includePositions 是否包含持仓详情
 * @param includeTransactions 是否包含交易详情
 * @returns 回测结果数据
 */
export const getTaskResults = async (
  taskId: string,
  includePositions: boolean = true,
  includeTransactions: boolean = true
): Promise<BacktestResultData> => {
  try {
    const response = await request<BacktestResultResponse>({
      url: `/api/v1/backtest/tasks/${taskId}/results`,
      method: 'GET',
      params: {
        include_positions: includePositions,
        include_transactions: includeTransactions
      }
    })
    return response.data
  } catch (error) {
    console.error('获取回测结果失败:', error)
    throw error
  }
}

/**
 * 获取任务列表
 * @param params 查询参数
 * @returns 任务列表
 */
export const getTaskList = async (params?: {
  page?: number
  pageSize?: number
  status?: string
  strategyName?: string
  sortBy?: string
  order?: 'asc' | 'desc'
}): Promise<TaskListResponse['data']> => {
  try {
    const response = await request<TaskListResponse>({
      url: '/api/v1/backtest/tasks',
      method: 'GET',
      params: {
        page: params?.page || 1,
        page_size: params?.pageSize || 20,
        status: params?.status,
        strategy_name: params?.strategyName,
        sort_by: params?.sortBy || 'created_at',
        order: params?.order || 'desc'
      }
    })
    return response.data
  } catch (error) {
    console.error('获取任务列表失败:', error)
    throw error
  }
}

/**
 * 对比回测结果
 * @param request 对比请求
 * @returns 对比结果
 */
export const compareBacktests = async (
  request: BacktestCompareRequest
): Promise<BacktestCompareResponse['data']> => {
  try {
    const response = await request<BacktestCompareResponse>({
      url: '/api/v1/backtest/compare',
      method: 'POST',
      data: request
    })
    return response.data
  } catch (error) {
    console.error('对比回测失败:', error)
    throw error
  }
}

/**
 * 导出回测报告
 * @param taskId 任务ID
 * @param format 导出格式 (json/excel/pdf)
 * @returns 导出信息
 */
export const exportBacktestReport = async (
  taskId: string,
  format: 'json' | 'excel' | 'pdf' = 'json'
): Promise<ExportResponse['data']> => {
  try {
    const response = await request<ExportResponse>({
      url: `/api/v1/backtest/tasks/${taskId}/export`,
      method: 'GET',
      params: { format }
    })
    return response.data
  } catch (error) {
    console.error('导出回测报告失败:', error)
    throw error
  }
}

/**
 * 健康检查
 * @returns 服务状态信息
 */
export const healthCheck = async (): Promise<{
  status: string
  service: string
  version: string
  timestamp: string
  task_count: number
}> => {
  try {
    const response = await request<{ code: number; message: string; data: any }>({
      url: '/api/v1/backtest/health',
      method: 'GET'
    })
    return response.data
  } catch (error) {
    console.error('健康检查失败:', error)
    throw error
  }
}

// ========== 辅助方法 ==========

/**
 * 轮询任务状态直到完成
 * @param taskId 任务ID
 * @param onProgress 进度回调
 * @param interval 轮询间隔（毫秒）
 * @returns 最终的任务状态
 */
export const pollTaskStatus = async (
  taskId: string,
  onProgress?: (status: TaskStatusResponse) => void,
  interval: number = 2000
): Promise<TaskStatusResponse> => {
  let status = await getTaskStatus(taskId)

  while (status.status === TaskStatus.PENDING || status.status === TaskStatus.RUNNING) {
    if (onProgress) {
      onProgress(status)
    }

    // 等待指定间隔
    await new Promise(resolve => setTimeout(resolve, interval))

    // 再次查询状态
    status = await getTaskStatus(taskId)
  }

  return status
}

/**
 * 格式化百分比
 * @param value 数值
 * @param decimals 小数位数
 * @returns 格式化后的字符串
 */
export const formatPercent = (value: number, decimals: number = 2): string => {
  return `${(value * 100).toFixed(decimals)}%`
}

/**
 * 格式化货币
 * @param value 数值
 * @returns 格式化后的字符串
 */
export const formatCurrency = (value: number): string => {
  return `¥${value.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
}

/**
 * 格式化日期
 * @param dateStr 日期字符串
 * @returns 格式化后的字符串
 */
export const formatDate = (dateStr: string): string => {
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

/**
 * 获取任务状态文本
 * @param status 任务状态
 * @returns 状态文本
 */
export const getTaskStatusText = (status: TaskStatus): string => {
  const statusMap: Record<TaskStatus, string> = {
    [TaskStatus.PENDING]: '排队中',
    [TaskStatus.RUNNING]: '运行中',
    [TaskStatus.COMPLETED]: '已完成',
    [TaskStatus.FAILED]: '失败',
    [TaskStatus.CANCELLED]: '已取消'
  }
  return statusMap[status] || status
}

/**
 * 获取任务状态颜色
 * @param status 任务状态
 * @returns 颜色类名
 */
export const getTaskStatusColor = (status: TaskStatus): string => {
  const colorMap: Record<TaskStatus, string> = {
    [TaskStatus.PENDING]: 'info',
    [TaskStatus.RUNNING]: 'primary',
    [TaskStatus.COMPLETED]: 'success',
    [TaskStatus.FAILED]: 'danger',
    [TaskStatus.CANCELLED]: 'warning'
  }
  return colorMap[status] || 'default'
}

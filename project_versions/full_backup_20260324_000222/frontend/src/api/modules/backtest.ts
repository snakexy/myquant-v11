import api from '@/api'
import type { ApiResponse, BacktestResult } from '@/types/global'

// 回测配置接口
export interface BacktestConfig {
  strategyId: string
  startDate: string
  endDate: string
  stockPool: string
  initialCapital: number
  benchmark: string
  commissionRate: number
  maxPosition?: number
  stopLoss?: number
  takeProfit?: number
  rebalanceFrequency?: string
}

// 回测任务接口
export interface BacktestTask {
  id: string
  name: string
  config: BacktestConfig
  status: 'pending' | 'running' | 'completed' | 'failed'
  progress?: number
  result?: BacktestResult
  error?: string
  createdAt: string
  updatedAt: string
}

// 回测API
export const backtestApi = {
  // 运行回测
  runBacktest: (config: BacktestConfig, timeout?: number): Promise<ApiResponse<BacktestResult>> => {
    return api.post('/backtest/run', config, {
      timeout: timeout || 300000  // 默认5分钟超时，回测可能需要较长时间
    })
  },

  // 获取回测结果
  getBacktestResult: (id: string): Promise<ApiResponse<BacktestResult>> => {
    return api.get(`/backtest/result/${id}`)
  },

  // 获取回测任务列表
  getBacktestTasks: (): Promise<ApiResponse<BacktestTask[]>> => {
    return api.get('/backtest/tasks')
  },

  // 获取回测任务详情
  getBacktestTask: (id: string): Promise<ApiResponse<BacktestTask>> => {
    return api.get(`/backtest/tasks/${id}`)
  },

  // 停止回测
  stopBacktest: (id: string): Promise<ApiResponse<void>> => {
    return api.post(`/backtest/stop/${id}`)
  },

  // 删除回测任务
  deleteBacktestTask: (id: string): Promise<ApiResponse<void>> => {
    return api.delete(`/backtest/tasks/${id}`)
  },

  // 导出回测结果
  exportBacktestResult: (id: string, format: 'json' | 'csv' | 'excel' = 'json'): Promise<ApiResponse<Blob>> => {
    return api.get(`/backtest/export/${id}`, {
      params: { format },
      responseType: 'blob'
    })
  },

  // 分享回测结果
  shareBacktestResult: (id: string): Promise<ApiResponse<{ shareUrl: string; shareId: string }>> => {
    return api.post(`/backtest/share/${id}`)
  },

  // 获取分享的回测结果
  getSharedBacktestResult: (shareId: string): Promise<ApiResponse<BacktestResult>> => {
    return api.get(`/backtest/shared/${shareId}`)
  },

  // 批量回测
  batchBacktest: (configs: BacktestConfig[], timeout?: number): Promise<ApiResponse<BacktestResult[]>> => {
    return api.post('/backtest/batch', { configs }, {
      timeout: timeout || 600000  // 默认10分钟超时，批量回测需要更长时间
    })
  },

  // 获取回测统计
  getBacktestStats: (): Promise<ApiResponse<{
    totalBacktests: number
    runningBacktests: number
    completedBacktests: number
    failedBacktests: number
    averageExecutionTime: number
  }>> => {
    return api.get('/backtest/stats')
  }
}
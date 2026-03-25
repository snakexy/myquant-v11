import { apiRequest } from '../index'
import type {
  CreateStrategyParams,
  UpdateStrategyParams,
  StrategyListResponse,
  BacktestDetailResponse,
  RunBacktestParams,
  StrategyConfig
} from '../types'

/**
 * 策略API服务
 */
export const strategyApi = {
  /**
   * 获取策略列表
   */
  async getStrategies(params?: {
    page?: number
    pageSize?: number
    status?: string
    type?: string
  }): Promise<StrategyListResponse> {
    const response = await apiRequest.get('/strategy', { params })
    return response.data
  },

  /**
   * 获取策略详情
   */
  async getStrategy(id: string): Promise<BacktestDetailResponse> {
    const response = await apiRequest.get(`/strategy/${id}`)
    return response.data
  },

  /**
   * 创建策略
   */
  async createStrategy(data: CreateStrategyParams): Promise<BacktestDetailResponse> {
    const response = await apiRequest.post('/strategy', data)
    return response.data
  },

  /**
   * 更新策略
   */
  async updateStrategy(id: string, data: UpdateStrategyParams): Promise<BacktestDetailResponse> {
    const response = await apiRequest.put(`/strategy/${id}`, data)
    return response.data
  },

  /**
   * 删除策略
   */
  async deleteStrategy(id: string): Promise<void> {
    await apiRequest.delete(`/strategy/${id}`)
  },

  /**
   * 启用/禁用策略
   */
  async toggleStrategy(id: string, enabled: boolean): Promise<BacktestDetailResponse> {
    const response = await apiRequest.patch(`/strategy/${id}/toggle`, { enabled })
    return response.data
  },

  /**
   * 策略回测
   */
  async backtestStrategy(id: string, data: RunBacktestParams, timeout?: number): Promise<BacktestDetailResponse> {
    const response = await apiRequest.post(`/strategy/${id}/backtest`, data, {
      timeout: timeout || 300000  // 默认5分钟超时，策略回测可能需要较长时间
    })
    return response.data
  },

  /**
   * 获取策略回测历史
   */
  async getBacktestHistory(id: string): Promise<any> {
    const response = await apiRequest.get(`/strategy/${id}/backtest-history`)
    return response.data
  },

  /**
   * 复制策略
   */
  async duplicateStrategy(id: string, name?: string): Promise<BacktestDetailResponse> {
    const response = await apiRequest.post(`/strategy/${id}/duplicate`, { name })
    return response.data
  },

  /**
   * 导出策略
   */
  async exportStrategy(id: string): Promise<Blob> {
    const response = await apiRequest.get(`/strategy/${id}/export`, {
      responseType: 'blob'
    })
    return response.data
  },

  /**
   * 导入策略
   */
  async importStrategy(file: File, timeout?: number): Promise<BacktestDetailResponse> {
    const formData = new FormData()
    formData.append('file', file)
    
    const response = await apiRequest.upload('/strategy/import', formData, {
      timeout: timeout || 60000  // 默认60秒超时，文件上传可能需要较长时间
    })
    return response.data
  },

  /**
   * 获取策略模板
   */
  async getStrategyTemplates(): Promise<any> {
    const response = await apiRequest.get('/strategy/templates')
    return response.data
  },

  /**
   * 从模板创建策略
   */
  async createFromTemplate(templateId: string, data: any): Promise<BacktestDetailResponse> {
    const response = await apiRequest.post(`/strategy/template/${templateId}`, data)
    return response.data
  },

  /**
   * 获取策略性能指标
   */
  async getStrategyMetrics(id: string, params?: {
    startDate?: string
    endDate?: string
  }): Promise<any> {
    const response = await apiRequest.get(`/strategy/${id}/metrics`, { params })
    return response.data
  },

  /**
   * 获取策略信号
   */
  async getStrategySignals(id: string, params?: {
    page?: number
    pageSize?: number
    startDate?: string
    endDate?: string
  }): Promise<any> {
    const response = await apiRequest.get(`/strategy/${id}/signals`, { params })
    return response.data
  }
}

export default strategyApi
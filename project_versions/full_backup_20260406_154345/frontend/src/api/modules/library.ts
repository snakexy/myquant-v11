/**
 * MyQuant v10.0.0 - Strategy Library API
 * 策略库API接口封装
 * 用于策略的持久化存储、查询和管理
 */

import { http } from '../request'

// ==================== 类型定义 ====================

// 策略状态
export type StrategyStatus = 'active' | 'paused' | 'archived' | 'deleted'

// 策略阶段
export type StrategyStage = 'research' | 'validation' | 'production' | 'library'

// 策略配置
export interface StrategyConfig {
  stockPool: string
  stockPoolZh?: string
  factors: string
  factorsZh?: string
  modelType?: string
  modelParams?: Record<string, any>
  riskParams?: {
    maxPosition?: number
    stopLoss?: number
    takeProfit?: number
  }
}

// 策略性能指标
export interface StrategyPerformance {
  annualReturn: number
  sharpeRatio: number
  maxDrawdown: number
  winRate: number
  totalTrades: number
  profitFactor: number
  calmarRatio?: number
  sortinoRatio?: number
}

// 策略实体
export interface StrategyEntity {
  strategyId: string
  strategyName: string
  strategyNameZh?: string
  description?: string
  descriptionZh?: string
  status: StrategyStatus
  stage: StrategyStage
  config: StrategyConfig
  performance?: StrategyPerformance
  tags: string[]
  createdBy?: string
  createdAt: string
  updatedAt: string
  lastRunAt?: string
  runCount: number
  isFavorite: boolean
}

// 创建策略请求
export interface CreateStrategyRequest {
  strategyName: string
  strategyNameZh?: string
  description?: string
  descriptionZh?: string
  stage?: StrategyStage
  config: StrategyConfig
  performance?: StrategyPerformance
  tags?: string[]
  isFavorite?: boolean
}

// 更新策略请求
export interface UpdateStrategyRequest {
  strategyName?: string
  strategyNameZh?: string
  description?: string
  descriptionZh?: string
  status?: StrategyStatus
  stage?: StrategyStage
  config?: Partial<StrategyConfig>
  performance?: Partial<StrategyPerformance>
  tags?: string[]
  isFavorite?: boolean
}

// 策略列表响应
export interface StrategyListResponse {
  strategies: StrategyEntity[]
  total: number
  page: number
  pageSize: number
}

// 策略查询参数
export interface StrategyQueryParams {
  page?: number
  pageSize?: number
  stage?: StrategyStage
  status?: StrategyStatus
  tags?: string[]
  keyword?: string
  sortBy?: 'createdAt' | 'updatedAt' | 'annualReturn' | 'sharpeRatio'
  sortOrder?: 'asc' | 'desc'
}

// 策略统计
export interface StrategyStatistics {
  total: number
  byStage: Record<StrategyStage, number>
  byStatus: Record<StrategyStatus, number>
  avgAnnualReturn: number
  avgSharpeRatio: number
  topPerformers: Array<{
    strategyId: string
    strategyName: string
    annualReturn: number
  }>
}

// ==================== API响应类型 ====================

interface ApiSuccessResponse<T> {
  code: number
  data: T
  message: string
}

interface ApiErrorResponse {
  code: number
  message: string
  detail?: string
}

// ==================== 策略库API ====================

export const strategyLibraryApi = {
  /**
   * 创建策略
   * POST /api/v1/library/strategies
   */
  createStrategy(request: CreateStrategyRequest): Promise<ApiSuccessResponse<StrategyEntity>> {
    return http.post('/v1/library/strategies', request)
  },

  /**
   * 获取策略列表
   * GET /api/v1/library/strategies
   */
  getStrategies(params?: StrategyQueryParams): Promise<ApiSuccessResponse<StrategyListResponse>> {
    return http.get('/v1/library/strategies', { params })
  },

  /**
   * 获取单个策略详情
   * GET /api/v1/library/strategies/{strategy_id}
   */
  getStrategy(strategyId: string): Promise<ApiSuccessResponse<StrategyEntity>> {
    return http.get(`/v1/library/strategies/${strategyId}`)
  },

  /**
   * 更新策略
   * PUT /api/v1/library/strategies/{strategy_id}
   */
  updateStrategy(strategyId: string, request: UpdateStrategyRequest): Promise<ApiSuccessResponse<StrategyEntity>> {
    return http.put(`/v1/library/strategies/${strategyId}`, request)
  },

  /**
   * 删除策略（软删除）
   * DELETE /api/v1/library/strategies/{strategy_id}
   */
  deleteStrategy(strategyId: string): Promise<ApiSuccessResponse<{ success: boolean }>> {
    return http.delete(`/v1/library/strategies/${strategyId}`)
  },

  /**
   * 保存到策略库（从其他阶段归档）
   * POST /api/v1/library/strategies/{strategy_id}/archive
   */
  archiveToLibrary(strategyId: string): Promise<ApiSuccessResponse<StrategyEntity>> {
    return http.post(`/v1/library/strategies/${strategyId}/archive`)
  },

  /**
   * 从策略库重新激活（恢复到Validation或Production阶段）
   * POST /api/v1/library/strategies/{strategy_id}/reactivate
   * @param strategyId 策略ID
   * @param targetStage 目标阶段：validation 或 production
   */
  reactivateStrategy(strategyId: string, targetStage: 'validation' | 'production'): Promise<ApiSuccessResponse<StrategyEntity>> {
    return http.post(`/v1/library/strategies/${strategyId}/reactivate`, { target_stage: targetStage })
  },

  /**
   * 获取策略库统计
   * GET /api/v1/library/strategies/statistics
   */
  getStatistics(): Promise<ApiSuccessResponse<StrategyStatistics>> {
    return http.get('/v1/library/strategies/statistics')
  },

  /**
   * 按阶段获取策略数量
   * GET /api/v1/library/strategies/count
   */
  getStrategiesCount(): Promise<ApiSuccessResponse<Record<StrategyStage, number>>> {
    return http.get('/v1/library/strategies/count')
  },

  /**
   * 收藏/取消收藏策略
   * POST /api/v1/library/strategies/{strategy_id}/favorite
   */
  toggleFavorite(strategyId: string): Promise<ApiSuccessResponse<StrategyEntity>> {
    return http.post(`/v1/library/strategies/${strategyId}/favorite`)
  },

  /**
   * 复制策略
   * POST /api/v1/library/strategies/{strategy_id}/duplicate
   */
  duplicateStrategy(strategyId: string, newName?: string): Promise<ApiSuccessResponse<StrategyEntity>> {
    return http.post(`/v1/library/strategies/${strategyId}/duplicate`, { new_name: newName })
  },

  /**
   * 批量操作
   * POST /api/v1/library/strategies/batch
   */
  batchOperation(
    operation: 'archive' | 'delete' | 'reactivate' | 'tag',
    strategyIds: string[],
    params?: { targetStage?: string; tags?: string[] }
  ): Promise<ApiSuccessResponse<{ success: boolean; affected: number }>> {
    return http.post('/v1/library/strategies/batch', {
      operation,
      strategy_ids: strategyIds,
      ...params
    })
  },

  /**
   * 搜索策略
   * GET /api/v1/library/strategies/search
   */
  searchStrategies(
    keyword: string,
    options?: {
      stage?: StrategyStage
      tags?: string[]
      minReturn?: number
      minSharpe?: number
    }
  ): Promise<ApiSuccessResponse<StrategyEntity[]>> {
    return http.get('/v1/library/strategies/search', {
      params: { keyword, ...options }
    })
  },

  /**
   * 导出策略
   * GET /api/v1/library/strategies/{strategy_id}/export
   */
  exportStrategy(strategyId: string, format: 'json' | 'yaml' = 'json'): Promise<Blob> {
    return http.get(`/v1/library/strategies/${strategyId}/export`, {
      params: { format },
      responseType: 'blob'
    })
  },

  /**
   * 导入策略
   * POST /api/v1/library/strategies/import
   */
  importStrategy(file: File): Promise<ApiSuccessResponse<StrategyEntity>> {
    const formData = new FormData()
    formData.append('file', file)
    return http.post('/v1/library/strategies/import', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },

  /**
   * 获取策略运行历史
   * GET /api/v1/library/strategies/{strategy_id}/history
   */
  getStrategyHistory(
    strategyId: string,
    params?: { page?: number; pageSize?: number }
  ): Promise<ApiSuccessResponse<{
    runs: Array<{
      runId: string
      startTime: string
      endTime?: string
      stage: StrategyStage
      status: 'completed' | 'failed' | 'running'
      performance?: StrategyPerformance
    }>
    total: number
  }>> {
    return http.get(`/v1/library/strategies/${strategyId}/history`, { params })
  }
}

export default strategyLibraryApi

/**
 * MyQuant v10.0.0 - Meta Controller API
 * Meta Controller API调用封装
 * 包含：因子组合优化、模型选择、超参数优化
 */

import { http } from './request'

// ==================== 类型定义 ====================

/**
 * 因子组合优化请求参数
 */
export interface FactorOptimizeRequest {
  /** 因子指标字典 */
  factor_metrics: Record<string, {
    ic_mean?: number
    ir?: number
    ic_positive_ratio?: number
    [key: string]: any
  }>
  /** 优化方法 */
  optimization_method?: 'ic_weighted' | 'equal_weight' | 'ir_weighted' | 'auto'
  /** 目标指标 */
  target_metric?: 'ic_mean' | 'ir' | 'combined'
  /** 最大迭代次数 */
  max_iterations?: number
}

/**
 * 因子组合优化结果
 */
export interface FactorOptimizeResult {
  /** 优化ID */
  optimization_id: string
  /** 优化类型 */
  optimization_type: string
  /** 最佳配置 */
  best_config: {
    method: string
    target: string
    weights: Record<string, number>
  }
  /** 最佳指标 */
  best_metrics: {
    combined_ic: number
  }
  /** 所有试验 */
  all_trials: Array<{
    trial_id: string
    config: any
    metrics: any
    timestamp: string
    status: string
  }>
  /** 创建时间 */
  created_at: string
  /** 试验数量 */
  trial_count: number
  /** 最佳方法 */
  best_method: string
  /** 权重 */
  weights: Record<string, number>
}

/**
 * 模型选择请求参数
 */
export interface ModelSelectRequest {
  /** 模型类型列表 */
  model_types?: ('lightgbm' | 'xgboost' | 'rf' | 'mlp')[]
  /** 评估指标 */
  metric?: 'mse' | 'mae' | 'r2'
}

/**
 * 超参数优化请求参数
 */
export interface HPORequest {
  /** 模型类型 */
  model_type: string
  /** 任务ID */
  task_id?: string
  /** 参数网格 */
  param_grid?: Record<string, any[]>
  /** 搜索方法 */
  search_method?: 'grid' | 'random' | 'bayesian'
  /** 迭代次数 */
  n_iter?: number
  /** 交叉验证折数 */
  cv?: number
}

/**
 * API响应基础结构
 */
export interface ApiResponse<T> {
  code: number
  message: string
  data: T
  timestamp: string
}

// ==================== Meta Controller API ====================

export const metaControllerAPI = {
  /**
   * 健康检查
   */
  healthCheck: () => {
    return http.get<ApiResponse<{ service: string; status: string }>>('/v1/research/meta/health')
  },

  /**
   * 因子组合优化
   */
  optimizeFactorCombination: (request: FactorOptimizeRequest) => {
    return http.post<ApiResponse<FactorOptimizeResult>>('/v1/research/meta/factor/optimize', request)
  },

  /**
   * 模型选择
   */
  selectBestModel: (request: ModelSelectRequest) => {
    return http.post<ApiResponse<any>>('/v1/research/meta/model/select', request)
  },

  /**
   * 超参数优化
   */
  hyperparameterOptimization: (request: HPORequest) => {
    return http.post<ApiResponse<any>>('/v1/research/meta/hpo/auto', request)
  },

  /**
   * 获取优化试验列表
   */
  getTrials: () => {
    return http.get<ApiResponse<any>>('/v1/research/meta/trials')
  },

  /**
   * 获取优化结果
   */
  getResult: (optimizationId: string) => {
    return http.get<ApiResponse<any>>(`/v1/research/meta/result/${optimizationId}`)
  },

  /**
   * 获取统计信息
   */
  getStatistics: () => {
    return http.get<ApiResponse<any>>('/v1/research/meta/statistics')
  }
}

export default metaControllerAPI

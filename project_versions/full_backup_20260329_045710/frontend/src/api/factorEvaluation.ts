/**
 * MyQuant v10.0.0 - Factor Evaluation API
 * 因子评估API调用封装
 * 包含：因子有效性验证、因子组合评估、健康检查
 */

import { http } from './request'

// ==================== 类型定义 ====================

/**
 * 因子有效性验证请求参数
 */
export interface ValidityRequest {
  /** 因子名称 */
  factor_name: string
  /** 开始日期 (YYYY-MM-DD) */
  start_date: string
  /** 结束日期 (YYYY-MM-DD) */
  end_date: string
  /** 阈值配置（可选） */
  threshold?: {
    /** IC均值阈值 */
    ic_mean?: number
    /** IR阈值 */
    ir?: number
    /** IC正数占比阈值 */
    ic_positive_ratio?: number
  }
}

/**
 * 因子指标评估结果
 */
export interface FactorMetricResult {
  /** 指标值 */
  value: number
  /** 阈值 */
  threshold?: number
  /** 是否通过阈值 */
  passed?: boolean
  /** 评分（0-1） */
  score?: number
  /** 描述 */
  description?: string
}

/**
 * QLib标准扩展指标
 */
export interface QLibMetrics {
  /** IC标准差 */
  ic_std: FactorMetricResult
  /** Rank IC均值 */
  rank_ic_mean: FactorMetricResult
  /** t统计量 */
  t_stat: FactorMetricResult
  /** p值 */
  p_value: FactorMetricResult
}

/**
 * 因子有效性验证结果
 */
export interface ValidityResult {
  /** 因子名称 */
  factor_name: string
  /** 是否有效 */
  is_valid: boolean
  /** 总体评分（0-100） */
  overall_score: number
  /** 各指标评估结果 */
  metrics: {
    /** IC均值评估 */
    ic_mean: FactorMetricResult
    /** IR评估 */
    ir: FactorMetricResult
    /** IC正数占比评估 */
    ic_positive_ratio: FactorMetricResult
    /** QLib标准扩展指标 */
    ic_std?: FactorMetricResult
    rank_ic_mean?: FactorMetricResult
    t_stat?: FactorMetricResult
    p_value?: FactorMetricResult
  }
  /** IC时间序列（用于稳定性和衰减分析） */
  ic_series?: number[]
  /** 建议说明 */
  recommendation: string
  /** 评估时间 */
  evaluated_at: string
}

/**
 * 组合方法类型
 */
export type CombinationMethod = 'equal_weight' | 'ic_weight' | 'custom'

/**
 * 因子组合评估请求参数
 */
export interface CombinationRequest {
  /** 因子名称列表 */
  factor_names: string[]
  /** 开始日期 (YYYY-MM-DD) */
  start_date: string
  /** 结束日期 (YYYY-MM-DD) */
  end_date: string
  /** 组合方法（可选，默认equal_weight） */
  combination_method?: CombinationMethod
  /** 自定义权重（仅combination_method为custom时需要） */
  weights?: number[]
}

/**
 * 组合因子评估指标
 */
export interface CombinationMetrics {
  /** IC均值 */
  ic_mean: number
  /** IC标准差 */
  ic_std: number
  /** IR (IC均值/IC标准差) */
  ir: number
  /** IC正数占比 */
  ic_positive_ratio: number
  /** RankIC均值 */
  rank_ic_mean: number
  /** 最大回撤 */
  max_drawdown: number
}

/**
 * 组合因子对比信息
 */
export interface CombinationComparison {
  /** 最佳因子名称 */
  best_factor: string
  /** 改进幅度 */
  improvement?: {
    /** IC均值改进 */
    ic_mean: number
    /** IR改进 */
    ir: number
  }
  /** 是否优于最佳单因子 */
  is_better: boolean
}

/**
 * 因子组合评估结果
 */
export interface CombinationResult {
  /** 组合因子名称 */
  combined_factor_name: string
  /** 组合方法 */
  combination_method: string
  /** 各因子权重 */
  weights: Record<string, number>
  /** 评估指标 */
  evaluation: CombinationMetrics
  /** 与单因子对比（可选） */
  comparison?: CombinationComparison
}

/**
 * API响应基础结构
 */
export interface ApiResponse<T> {
  /** 响应码 */
  code: number
  /** 响应消息 */
  message: string
  /** 响应数据 */
  data: T
  /** 时间戳 */
  timestamp: string
}

/**
 * 健康检查响应
 */
export interface HealthCheckResponse {
  /** 服务名称 */
  service: string
  /** 服务状态 */
  status: string
  /** 依赖项状态 */
  dependencies?: Record<string, boolean>
  /** 时间戳 */
  timestamp: string
}

/**
 * 一键智能评估请求参数
 */
export interface SmartEvaluateRequest {
  /** 待评估的因子名称列表 */
  factor_names: string[]
  /** 开始日期 (YYYY-MM-DD) */
  start_date: string
  /** 结束日期 (YYYY-MM-DD) */
  end_date: string
  /** 阈值配置（可选） */
  threshold?: {
    ic_mean?: number
    ir?: number
    ic_positive_ratio?: number
  }
}

/**
 * 因子评估详情
 */
export interface FactorDetail {
  /** 是否有效 */
  is_valid: boolean
  /** 总体评分 */
  overall_score: number
  /** 各指标评估结果 */
  metrics: {
    ic_mean: FactorMetricResult
    ir: FactorMetricResult
    ic_positive_ratio: FactorMetricResult
  }
  /** 建议说明 */
  recommendation: string
}

/**
 * 最佳组合结果
 */
export interface BestCombination {
  /** 组合方法 */
  method: string
  /** 各因子权重 */
  weights: Record<string, number>
  /** IC均值 */
  ic_mean: number
  /** IR */
  ir: number
  /** IC正数占比 */
  ic_positive_ratio: number
  /** 是否优于最佳单因子 */
  is_better_than_best_single: boolean
}

/**
 * 推荐的RL模型
 */
export interface RecommendedRLModel {
  /** 推荐算法（PPO/DQN/A2C） */
  algorithm: string
  /** 推荐理由 */
  reason: string
  /** 预期收益提升 */
  expected_improvement: string
  /** 建议训练回合数 */
  suggested_episodes: number
  /** 有效因子数量 */
  valid_factor_count: number
}

/**
 * 一键智能评估结果
 */
export interface SmartEvaluateResult {
  /** 总因子数 */
  total_factors: number
  /** 有效因子列表 */
  valid_factors: string[]
  /** 无效因子列表 */
  invalid_factors: string[]
  /** 各因子评估详情 */
  factor_details: Record<string, FactorDetail>
  /** 最佳组合 */
  best_combination: BestCombination | null
  /** 所有组合尝试结果 */
  all_combinations: BestCombination[]
  /** 推荐的RL模型 */
  recommended_rl_model: RecommendedRLModel | null
  /** 警告信息（如有） */
  warning?: string
  /** 评估时间 */
  evaluated_at?: string
}

// ==================== API函数 ====================

/**
 * 因子评估API
 */
export const factorEvaluationAPI = {
  /**
   * 健康检查
   * @returns 健康状态
   */
  healthCheck: () => {
    return http.get<ApiResponse<HealthCheckResponse>>('/v1/research/eval/health')
  },

  /**
   * 因子有效性验证
   * 评估单个因子的有效性，计算IC、IR等指标并评分
   * @param request 验证请求参数
   * @returns 验证结果
   */
  evaluateValidity: (request: ValidityRequest) => {
    return http.post<ApiResponse<ValidityResult>>('/v1/research/eval/validity', request)
  },

  /**
   * 因子组合评估
   * 将多个因子组合成一个新因子并评估其表现
   * @param request 组合评估请求参数
   * @returns 组合评估结果
   */
  evaluateCombination: (request: CombinationRequest) => {
    return http.post<ApiResponse<CombinationResult>>('/v1/research/eval/combine', request)
  },

  /**
   * 一键智能评估
   * 自动完成因子评估全流程：评估有效性、筛选有效因子、找出最佳组合、推荐RL模型
   * @param request 智能评估请求参数
   * @returns 智能评估结果
   */
  smartEvaluate: (request: SmartEvaluateRequest) => {
    return http.post<ApiResponse<SmartEvaluateResult>>('/v1/research/eval/smart', request)
  }
}

// ==================== 导出 ====================

export default factorEvaluationAPI

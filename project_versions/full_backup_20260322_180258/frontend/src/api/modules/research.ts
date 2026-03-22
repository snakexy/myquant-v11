/**
 * MyQuant v10.0.0 - Research API Module
 * Research阶段API接口封装
 * 包含：数据管理、因子计算、因子分析、因子评估、ML训练、AI助手
 */

import { http } from '../request'

// ==================== 类型定义 ====================

// 通用响应
export interface ApiResponse<T = any> {
  success: boolean
  data?: T
  message?: string
  task_id?: string
}

// ==================== 数据管理相关类型 ====================

export interface StockInfo {
  code: string
  name: string
  market: string
  industry?: string
}

export interface IndexInfo {
  code: string
  name: string
  constituent_count: number
}

export interface DataStatus {
  last_update: string
  total_stocks: number
  total_records: number
  cache_size: string
}

export interface CacheStats {
  memory: {
    size: number
    hit_rate: number
  }
  redis: {
    size: number
    hit_rate: number
  }
  database: {
    size: number
  }
}

// ==================== 因子相关类型 ====================

export interface FactorInfo {
  name: string
  type: 'momentum' | 'volatility' | 'volume' | 'technical' | 'fundamental'
  category: 'alpha158' | 'alpha360' | 'custom'
  description?: string
  ic?: number
  ir?: number
  typeZh?: string
}

export interface FactorResult {
  factor_name: string
  ic: number
  ir: number
  t_stat: number
  p_value: number
  status: 'pass' | 'fail'
}

export interface FactorCalculationRequest {
  factor_type: 'alpha158' | 'alpha360' | 'custom'
  symbols: string[]
  start_date: string
  end_date: string
  factors?: string[]
}

export interface FactorAnalysisResult {
  total_factors: number
  ic_mean: number
  ir_ratio: number
  qualified_count: number
  pass_rate: number
  top_factors: FactorResult[]
  progress: number
}

// ==================== ML模型相关类型 ====================

export interface MLModelInfo {
  model_id: string
  model_name: string
  model_type: 'lightgbm' | 'xgboost' | 'lstm' | 'transformer'
  status: 'training' | 'trained' | 'deployed' | 'deprecated'
  accuracy?: number
  ic?: number
  created_at: string
  trained_at?: string
}

export interface TrainingConfig {
  model_type: 'lightgbm' | 'xgboost' | 'lstm'
  symbols: string[]
  start_date: string
  end_date: string
  features: string[]
  label: string
  hyperparams: Record<string, any>
}

export interface TrainingStatus {
  task_id: string
  status: 'pending' | 'running' | 'completed' | 'failed'
  progress: number
  current_step: string
  metrics?: {
    loss?: number
    accuracy?: number
    ic?: number
  }
  error?: string
}

// ==================== AI助手相关类型 ====================

export interface AIMessage {
  role: 'user' | 'assistant'
  content: string
  timestamp: string
}

export interface AIStrategyRequest {
  prompt: string
  context?: string
  strategy_type?: 'factor' | 'signal' | 'portfolio'
}

export interface AIStrategyResponse {
  strategy_code: string
  explanation: string
  suggestions: string[]
}

// ==================== 工作流相关类型 ====================

export interface WorkflowStep {
  id: number
  name: string
  status: 'completed' | 'active' | 'pending'
  description: string
}

export interface WorkflowState {
  current_step: number
  steps: WorkflowStep[]
  data: Record<string, any>
}

// ==================== 数据管理API ====================

export const dataApi = {
  // 获取股票列表
  getStocks: (codes?: string[]) =>
    http.get<ApiResponse<StockInfo[]>>('/v1/research/data/stocks', {
      params: { codes: codes?.join(',') }
    }),

  // 获取指数成分股
  getIndexConstituents: (indexCode: string) =>
    http.get<ApiResponse<StockInfo[]>>(`/v1/research/data/index/${indexCode}/constituents`),

  // 获取数据状态
  getDataStatus: () =>
    http.get<ApiResponse<DataStatus>>('/v1/research/data/status'),

  // 获取缓存统计
  getCacheStats: () =>
    http.get<ApiResponse<CacheStats>>('/v1/research/data/cache-stats'),

  // 刷新数据
  refreshData: (symbols?: string[]) =>
    http.post<ApiResponse>('/v1/research/data/refresh', { symbols }),

  // 清洗数据
  cleanData: (symbols: string[], startDate: string, endDate: string) =>
    http.post<ApiResponse>('/v1/research/data/clean', {
      symbols,
      start_date: startDate,
      end_date: endDate
    }),
}

// ==================== 因子计算API ====================

export const factorApi = {
  // 获取因子库列表
  getFactorLibrary: (category?: string) =>
    http.get<ApiResponse<FactorInfo[]>>('/v1/research/factor/library', {
      params: { category }
    }),

  // 获取因子列表（从分析服务）
  getFactorList: () =>
    http.get<ApiResponse<{ factors: string[] }>>('/v1/research/analysis/factors'),

  // 计算因子
  calculateFactors: (request: FactorCalculationRequest) =>
    http.post<ApiResponse<{ task_id: string }>>('/v1/research/factor/calculate', request),

  // 获取计算状态
  getCalculationStatus: (taskId: string) =>
    http.get<ApiResponse<FactorAnalysisResult>>(`/v1/research/factor/status/${taskId}`),

  // 导出因子
  exportFactors: (taskId: string, format: 'csv' | 'excel' = 'csv') =>
    http.post<Blob>('/v1/research/factor/export', {
      task_id: taskId,
      format
    }, { responseType: 'blob' }),

  // 因子分析
  analyzeFactors: (symbols: string[], factors: string[], startDate: string, endDate: string) =>
    http.post<ApiResponse<FactorAnalysisResult>>('/v1/research/analysis/analyze', {
      symbols,
      factors,
      start_date: startDate,
      end_date: endDate
    }),

  // IC/IR分析
  calculateICIR: (symbols: string[], startDate: string, endDate: string, method: 'pearson' | 'spearman' = 'spearman') =>
    http.post<ApiResponse<{ factors: FactorResult[], summary: { ic_mean: number, ir_mean: number } }>>('/v1/research/analysis/ic-ir', {
      symbols,
      start_date: startDate,
      end_date: endDate,
      method
    }),

  // 相关性分析
  calculateCorrelation: (factors: string[], threshold: number = 0.8) =>
    http.post<ApiResponse<{ correlation_matrix: number[][], duplicate_pairs: [string, string, number][] }>>('/v1/research/analysis/correlation', {
      factors,
      threshold
    }),

  // 因子分布
  getFactorDistribution: (factorName: string, symbols: string[], date: string) =>
    http.post<ApiResponse<{ histogram: number[], q_q_plot: [number, number][], statistics: { mean: number, std: number, skewness: number, kurtosis: number } }>>('/v1/research/analysis/distribution', {
      factor_name: factorName,
      symbols,
      date
    }),
}

// ==================== 因子评估API ====================

export const evalApi = {
  // 评估因子
  evaluateFactors: (factors: string[], symbols: string[], startDate: string, endDate: string) =>
    http.post<ApiResponse<{ results: FactorResult[], summary: { total: number, passed: number, failed: number } }>>('/v1/research/eval/evaluate', {
      factors,
      symbols,
      start_date: startDate,
      end_date: endDate
    }),

  // 分组回测
  groupBacktest: (factorName: string, symbols: string[], startDate: string, endDate: string, groups: number = 5) =>
    http.post<ApiResponse<{ groups: { group_id: number, return: number, ic: number }[] }>>('/v1/research/eval/group-backtest', {
      factor_name: factorName,
      symbols,
      start_date: startDate,
      end_date: endDate,
      groups
    }),

  // 获取评估报告
  getEvalReport: (taskId: string) =>
    http.get<ApiResponse>(`/v1/research/eval/report/${taskId}`),
}

// ==================== ML模型API ====================

export const mlApi = {
  // 获取模型列表
  getModels: () =>
    http.get<ApiResponse<MLModelInfo[]>>('/v1/research/ml/models'),

  // 获取模型详情
  getModel: (modelId: string) =>
    http.get<ApiResponse<MLModelInfo>>(`/v1/research/ml/models/${modelId}`),

  // 开始训练
  startTraining: (config: TrainingConfig) =>
    http.post<ApiResponse<{ task_id: string }>>('/v1/research/ml/train', config),

  // 获取训练状态
  getTrainingStatus: (taskId: string) =>
    http.get<ApiResponse<TrainingStatus>>(`/v1/research/ml/status/${taskId}`),

  // 停止训练
  stopTraining: (taskId: string) =>
    http.post<ApiResponse>(`/v1/research/ml/stop/${taskId}`),

  // 预测
  predict: (modelId: string, symbols: string[], date: string) =>
    http.post<ApiResponse<{ predictions: { symbol: string, score: number, direction: 'up' | 'down' | 'flat' }[] }>>('/v1/research/ml/predict', {
      model_id: modelId,
      symbols,
      date
    }),

  // 超参数优化
  optimizeHyperparams: (config: TrainingConfig, nTrials: number = 50) =>
    http.post<ApiResponse<{ best_params: Record<string, any>, best_score: number }>>('/v1/research/ml/optimize', {
      config,
      n_trials: nTrials
    }),
}

// ==================== AI助手API ====================

export const aiApi = {
  // 发送消息
  sendMessage: (message: string, context?: string) =>
    http.post<ApiResponse<{ response: string }>>('/v1/research/ai/chat', {
      message,
      context
    }),

  // 生成策略
  generateStrategy: (request: AIStrategyRequest) =>
    http.post<ApiResponse<AIStrategyResponse>>('/v1/research/ai/generate', request),

  // 保存策略
  saveStrategy: (name: string, code: string, description: string) =>
    http.post<ApiResponse<{ strategy_id: string }>>('/v1/research/ai/save', {
      name,
      code,
      description
    }),

  // 获取策略历史
  getStrategyHistory: (limit: number = 20) =>
    http.get<ApiResponse<{ strategies: { id: string, name: string, created_at: string }[] }>>('/v1/research/ai/history', {
      params: { limit }
    }),

  // 分析市场
  analyzeMarket: (type: 'trend' | 'stock' | 'portfolio', symbols?: string[]) =>
    http.post<ApiResponse<{ analysis: string, recommendations: string[] }>>('/v1/research/ai/analyze', {
      type,
      symbols
    }),
}

// ==================== 工作流API ====================

export const workflowApi = {
  // 获取工作流状态
  getState: () =>
    http.get<ApiResponse<WorkflowState>>('/v1/research/workflow/state'),

  // 设置当前步骤
  setStep: (stepId: number) =>
    http.post<ApiResponse>('/v1/research/workflow/step', { step_id: stepId }),

  // 保存工作流数据
  saveData: (stepId: number, data: Record<string, any>) =>
    http.post<ApiResponse>('/v1/research/workflow/data', { step_id: stepId, data }),

  // 重置工作流
  reset: () =>
    http.post<ApiResponse>('/v1/research/workflow/reset'),
}

// 默认导出
export default {
  data: dataApi,
  factor: factorApi,
  eval: evalApi,
  ml: mlApi,
  ai: aiApi,
  workflow: workflowApi,
}

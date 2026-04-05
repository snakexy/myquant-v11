import { apiRequest, type ApiResponse } from '../index'
import type { 
  StrategyRecommendationRequest, 
  WorkflowRecommendation, 
  ParsedIntent, 
  OptimizationSuggestion
} from '../intelligent-recommendation'

/**
 * 智能推荐API模块
 * 提供自然语言解析、策略推荐、参数优化等功能
 */

// 自然语言解析API
export const parseNaturalLanguage = async (input: string): Promise<ApiResponse<ParsedIntent>> => {
  return apiRequest.post('/intelligent-recommendation/parse-natural-language', { input })
}

// 获取策略推荐API
export const getStrategyRecommendation = async (
  request: StrategyRecommendationRequest
): Promise<ApiResponse<WorkflowRecommendation>> => {
  return apiRequest.post('/intelligent-recommendation/strategy-recommendation', request)
}

// 获取参数优化建议API
export const getParameterOptimization = async (
  strategyType: string,
  currentParams: Record<string, any>,
  marketData: any
): Promise<ApiResponse<OptimizationSuggestion[]>> => {
  return apiRequest.post('/intelligent-recommendation/parameter-optimization', {
    strategyType,
    currentParams,
    marketData
  })
}

// 验证工作流API
export const validateWorkflow = async (
  workflow: WorkflowRecommendation
): Promise<ApiResponse<{
  isValid: boolean
  errors: string[]
  warnings: string[]
}>> => {
  return apiRequest.post('/intelligent-recommendation/validate-workflow', workflow)
}

// 应用推荐配置API
export const applyRecommendation = async (
  workflowId: string,
  customizations?: Record<string, any>
): Promise<ApiResponse<{ success: boolean; message: string }>> => {
  return apiRequest.post('/intelligent-recommendation/apply-recommendation', {
    workflowId,
    customizations
  })
}

// 获取推荐历史API
export const getRecommendationHistory = async (
  page = 1,
  pageSize = 10
): Promise<ApiResponse<{
  recommendations: WorkflowRecommendation[]
  total: number
  page: number
  pageSize: number
}>> => {
  return apiRequest.get(`/intelligent-recommendation/history?page=${page}&pageSize=${pageSize}`)
}

// 保存推荐配置API
export const saveRecommendation = async (
  workflow: WorkflowRecommendation,
  name: string,
  description?: string
): Promise<ApiResponse<{ id: string }>> => {
  return apiRequest.post('/intelligent-recommendation/save', {
    workflow,
    name,
    description
  })
}

// 加载保存的推荐配置API
export const loadRecommendation = async (
  id: string
): Promise<ApiResponse<WorkflowRecommendation>> => {
  return apiRequest.get(`/intelligent-recommendation/load/${id}`)
}

// 删除保存的推荐配置API
export const deleteRecommendation = async (
  id: string
): Promise<ApiResponse<{ success: boolean }>> => {
  return apiRequest.delete(`/intelligent-recommendation/delete/${id}`)
}

// 获取智能推荐统计信息API
export const getRecommendationStats = async (): Promise<ApiResponse<{
  totalRecommendations: number
  successRate: number
  averageAccuracy: number
  popularStrategies: Array<{
    strategyType: string
    count: number
    percentage: number
  }>
  recentActivity: Array<{
    date: string
    action: string
    strategyType: string
    success: boolean
  }>
}>> => {
  return apiRequest.get('/intelligent-recommendation/stats')
}

// 获取市场数据用于参数优化API
export const getMarketDataForOptimization = async (
  symbols: string[],
  dateRange: { start: string; end: string }
): Promise<ApiResponse<{
  marketData: Record<string, any>
  volatility: number
  trend: 'bull' | 'bear' | 'sideways'
  correlation: Record<string, number>
}>> => {
  return apiRequest.post('/intelligent-recommendation/market-data', {
    symbols,
    dateRange
  })
}

// 批量参数优化API
export const batchParameterOptimization = async (
  requests: Array<{
    strategyType: string
    currentParams: Record<string, any>
    marketData: any
  }>
): Promise<ApiResponse<Array<{
  requestId: string
  suggestions: OptimizationSuggestion[]
  success: boolean
  error?: string
}>>> => {
  return apiRequest.post('/intelligent-recommendation/batch-optimization', { requests })
}

// 获取推荐模板API
export const getRecommendationTemplates = async (
  strategyType?: string
): Promise<ApiResponse<Array<{
  id: string
  name: string
  description: string
  strategyType: string
  complexity: 'low' | 'medium' | 'high'
  experienceLevel: 'beginner' | 'intermediate' | 'expert'
  template: WorkflowRecommendation
  usageCount: number
  rating: number
}>>> => {
  const url = strategyType 
    ? `/intelligent-recommendation/templates?strategyType=${strategyType}`
    : '/intelligent-recommendation/templates'
  return apiRequest.get(url)
}

// 应用推荐模板API
export const applyRecommendationTemplate = async (
  templateId: string,
  customizations?: Record<string, any>
): Promise<ApiResponse<WorkflowRecommendation>> => {
  return apiRequest.post(`/intelligent-recommendation/apply-template/${templateId}`, {
    customizations
  })
}

// 评价推荐结果API
export const rateRecommendation = async (
  workflowId: string,
  rating: number,
  feedback?: string
): Promise<ApiResponse<{ success: boolean }>> => {
  return apiRequest.post('/intelligent-recommendation/rate', {
    workflowId,
    rating,
    feedback
  })
}

// 获取推荐反馈API
export const getRecommendationFeedback = async (
  workflowId: string
): Promise<ApiResponse<{
  rating: number
  feedback: string
  actualPerformance?: {
    accuracy: number
    sharpeRatio: number
    maxDrawdown: number
    annualReturn: number
  }
  improvementSuggestions: string[]
}>> => {
  return apiRequest.get(`/intelligent-recommendation/feedback/${workflowId}`)
}

// 导出推荐配置API
export const exportRecommendation = async (
  workflowId: string,
  format: 'json' | 'yaml' | 'xml' = 'json'
): Promise<void> => {
  return apiRequest.download(`/intelligent-recommendation/export/${workflowId}?format=${format}`, `recommendation-${workflowId}.${format}`)
}

// 导入推荐配置API
export const importRecommendation = async (
  file: File
): Promise<ApiResponse<WorkflowRecommendation>> => {
  const formData = new FormData()
  formData.append('file', file)
  return apiRequest.upload('/intelligent-recommendation/import', formData)
}

// 获取智能推荐帮助文档API
export const getRecommendationHelp = async (
  topic?: string
): Promise<ApiResponse<{
  sections: Array<{
    title: string
    content: string
    examples?: Array<{
      description: string
      code?: string
    }>
  }>
  faq: Array<{
    question: string
    answer: string
  }>
}>> => {
  const url = topic 
    ? `/intelligent-recommendation/help?topic=${topic}`
    : '/intelligent-recommendation/help'
  return apiRequest.get(url)
}

// 智能推荐API对象，便于统一管理
export const intelligentRecommendationApi = {
  // 核心功能
  parseNaturalLanguage,
  getStrategyRecommendation,
  getParameterOptimization,
  validateWorkflow,
  applyRecommendation,
  
  // 历史管理
  getRecommendationHistory,
  saveRecommendation,
  loadRecommendation,
  deleteRecommendation,
  
  // 统计分析
  getRecommendationStats,
  getMarketDataForOptimization,
  batchParameterOptimization,
  
  // 模板管理
  getRecommendationTemplates,
  applyRecommendationTemplate,
  
  // 反馈评价
  rateRecommendation,
  getRecommendationFeedback,
  
  // 导入导出
  exportRecommendation,
  importRecommendation,
  
  // 帮助文档
  getRecommendationHelp
}

export default intelligentRecommendationApi
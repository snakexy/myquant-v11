import { apiRequest } from '../index'

// 智能判断相关API接口

// 股票类型判断
export const judgeStockType = (data: {
  code: string
  name?: string
  market?: string
  sector?: string
  description?: string
}) => {
  return apiRequest.post('/intelligent/stock/type', data)
}

// AI输入检测
export const detectAIInput = (data: {
  input: string
  context?: string
  type?: 'strategy' | 'analysis' | 'prediction' | 'general'
}) => {
  return apiRequest.post('/intelligent/ai/input', data)
}

// 工作流程适配
export const adaptWorkflow = (data: {
  targetType: string
  sourceType?: string
  requirements?: string[]
  constraints?: Record<string, any>
}) => {
  return apiRequest.post('/intelligent/workflow/adapt', data)
}

// 智能推荐
export const getRecommendations = (data: {
  userId?: string
  context?: string
  type: 'stocks' | 'strategies' | 'workflows' | 'analysis'
  limit?: number
}) => {
  return apiRequest.post('/intelligent/recommendations', data)
}

// 模式识别
export const recognizePatterns = (data: {
  stockCode: string
  timeRange: {
    startDate: string
    endDate: string
  }
  patternTypes?: string[]
  sensitivity?: 'low' | 'medium' | 'high'
}) => {
  return apiRequest.post('/intelligent/patterns/recognize', data)
}

// 异常检测
export const detectAnomalies = (data: {
  stockCode: string
  data: Array<{
    timestamp: number
    price: number
    volume: number
  }>
  threshold?: number
  method?: 'statistical' | 'ml' | 'hybrid'
}) => {
  return apiRequest.post('/intelligent/anomalies/detect', data)
}

// 智能问答
export const askQuestion = (data: {
  question: string
  context?: string
  stockCodes?: string[]
  analysisType?: 'technical' | 'fundamental' | 'market' | 'general'
}) => {
  return apiRequest.post('/intelligent/qa', data)
}

// 风险评估
export const assessRisk = (data: {
  stockCodes: string[]
  timeHorizon?: 'short' | 'medium' | 'long'
  riskType?: 'market' | 'volatility' | 'liquidity' | 'comprehensive'
}) => {
  return apiRequest.post('/intelligent/risk/assess', data)
}

// 智能因子生成
export const generateFactors = (data: {
  universe?: string[]
  methodology?: 'technical' | 'fundamental' | 'alternative' | 'hybrid'
  constraints?: {
    maxFactors?: number
    correlationThreshold?: number
    icThreshold?: number
  }
}) => {
  return apiRequest.post('/intelligent/factors/generate', data)
}

// 策略建议
export const getSuggestedStrategies = (data: {
  marketConditions?: string
  riskTolerance?: 'conservative' | 'moderate' | 'aggressive'
  timeHorizon?: string
  objectives?: string[]
}) => {
  return apiRequest.post('/intelligent/strategies/suggest', data)
}

// 类型定义
export interface StockTypeResult {
  type: 'stock' | 'index' | 'etf' | 'bond' | 'commodity' | 'crypto'
  confidence: number
  details: {
    category: string
    subcategory?: string
    characteristics: string[]
  }
}

export interface AIInputDetection {
  isValid: boolean
  type: string
  confidence: number
  suggestions?: string[]
  warnings?: string[]
}

export interface WorkflowAdaptation {
  adaptedWorkflow: Record<string, any>
  changes: Array<{
    type: string
    description: string
    impact: string
  }>
  confidence: number
}

export interface Recommendation {
  id: string
  type: string
  title: string
  description: string
  confidence: number
  reasoning: string
  metadata: Record<string, any>
}

export interface PatternRecognition {
  patterns: Array<{
    name: string
    type: string
    confidence: number
    start_time: string
    end_time: string
    description: string
  }>
  summary: {
    total_patterns: number
    bullish_count: number
    bearish_count: number
    neutral_count: number
  }
}

export interface AnomalyDetection {
  anomalies: Array<{
    timestamp: string
    type: string
    severity: 'low' | 'medium' | 'high'
    description: string
    confidence: number
  }>
  statistics: {
    total_anomalies: number
    anomaly_rate: number
    average_confidence: number
  }
}

export interface QAResponse {
  answer: string
  confidence: number
  sources?: Array<{
    type: string
    title: string
    url?: string
  }>
  relatedQuestions?: string[]
}

export interface RiskAssessment {
  overallRisk: 'low' | 'medium' | 'high' | 'extreme'
  scores: {
    market_risk: number
    volatility_risk: number
    liquidity_risk: number
    concentration_risk: number
  }
  factors: Array<{
    name: string
    impact: 'positive' | 'negative'
    weight: number
    description: string
  }>
  recommendations: string[]
}

export interface FactorGeneration {
  factors: Array<{
    name: string
    formula: string
    type: string
    expected_ic: number
    description: string
  }>
  statistics: {
    total_factors: number
    avg_expected_ic: number
    coverage: number
  }
}

export interface StrategySuggestion {
  strategies: Array<{
    name: string
    type: string
    description: string
    expected_return: number
    risk_level: string
    complexity: string
    requirements: string[]
  }>
  market_analysis: {
    current_regime: string
    outlook: string
    key_factors: string[]
  }
}
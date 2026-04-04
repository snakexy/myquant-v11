import { apiRequest } from '../index'

// AI助手相关API接口

// 发送聊天消息
export const sendChatMessage = (data: {
  message: string
  session_id?: string
  context?: Record<string, any>
  user_preferences?: Record<string, any>
}) => {
  return apiRequest.post('/unified/ai-assistant/chat', data)
}

// 获取会话信息
export const getSessionInfo = (userId: string) => {
  return apiRequest.get(`/unified/ai-assistant/session/${userId}`)
}

// 生成AI策略
export const generateAIStrategy = (data: {
  market_condition: 'bullish' | 'bearish' | 'neutral'
  risk_level: 'low' | 'medium' | 'high'
  time_horizon: 'short' | 'medium' | 'long'
  constraints?: Record<string, any>
}) => {
  return apiRequest.post('/unified/ai-strategy/generate', data)
}

// 分析回测结果
export const analyzeBacktest = (data: {
  backtestId: string
  analysisType?: 'performance' | 'risk' | 'optimization'
}) => {
  return apiRequest.post('/unified/ai-assistant/analyze-backtest', data)
}

// 获取投资建议
export const getInvestmentAdvice = (data: {
  user_profile: Record<string, any>
  market_condition?: 'bullish' | 'bearish' | 'neutral'
}) => {
  return apiRequest.post('/unified/ai-assistant/investment-advice', data)
}

// 获取市场分析
export const getMarketAnalysis = (data: {
  market_data?: Record<string, any>
  analysis_type?: string
}) => {
  return apiRequest.post('/unified/ai-assistant/market-analysis', data)
}

// 语音识别
export const speechToText = (audioFile: File) => {
  const formData = new FormData()
  formData.append('audio', audioFile)
  return apiRequest.upload('/unified/ai-assistant/speech-to-text', formData)
}

// 文本转语音
export const textToSpeech = (data: {
  text: string
  voice?: string
  speed?: number
  language?: string
}) => {
  return apiRequest.post('/unified/ai-assistant/text-to-speech', data)
}

// 获取AI模型状态
export const getAIStatus = () => {
  return apiRequest.get('/unified/ai-assistant/status')
}

// 获取AI配置
export const getAIConfig = () => {
  return apiRequest.get('/unified/ai-assistant/config')
}

// 更新AI配置
export const updateAIConfig = (data: {
  model?: string
  temperature?: number
  maxTokens?: number
  systemPrompt?: string
}) => {
  return apiRequest.put('/unified/ai-assistant/config', data)
}

// 获取AI使用统计
export const getAIUsage = (params?: {
  startDate?: string
  endDate?: string
  granularity?: 'day' | 'week' | 'month'
}) => {
  return apiRequest.get('/unified/ai-assistant/usage', { params } as any)
}

// 清除会话
export const clearSession = (data: {
  user_id: string
}) => {
  return apiRequest.post('/unified/ai-assistant/clear-session', data)
}

// 获取市场解读
export const getMarketInterpretation = (data: {
  symbols?: string[]
  market_condition?: 'bullish' | 'bearish' | 'neutral'
  timeframe?: string
  analysis_type?: string
}) => {
  return apiRequest.post('/unified/ai-assistant/market-interpretation', data)
}

// 类型定义
export interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: string
  sessionId: string
  context?: string[]
  attachments?: {
    type: 'image' | 'file' | 'chart'
    url: string
    name: string
  }[]
}

export interface StrategyGeneration {
  id: string
  name: string
  description: string
  code: string
  parameters: Record<string, any>
  confidence: number
  reasoning: string
  alternatives?: {
    name: string
    description: string
    code: string
  }[]
  createdAt: string
}

export interface BacktestAnalysis {
  id: string
  backtestId: string
  analysisType: 'performance' | 'risk' | 'optimization'
  summary: string
  insights: string[]
  recommendations: string[]
  charts: {
    type: string
    data: any[]
    config: any
  }[]
  createdAt: string
}

export interface MarketAdvice {
  id: string
  market: string
  timeframe: string
  riskLevel: 'low' | 'medium' | 'high'
  summary: string
  opportunities: {
    symbol: string
    name: string
    reason: string
    confidence: number
    targetPrice?: number
    timeframe?: string
  }[]
  risks: {
    type: string
    description: string
    impact: 'low' | 'medium' | 'high'
    probability: number
  }[]
  timestamp: string
}

export interface RiskAlert {
  id: string
  type: 'price' | 'volume' | 'technical'
  severity: 'low' | 'medium' | 'high' | 'critical'
  symbol: string
  currentPrice?: number
  threshold?: number
  message: string
  recommendation: string
  createdAt: string
  resolved: boolean
}

export interface AIStatus {
  model: string
  status: 'online' | 'offline' | 'busy'
  queueLength: number
  averageResponseTime: number
  uptime: number
  lastUpdate: string
}

export interface AIConfig {
  model: string
  temperature: number
  maxTokens: number
  systemPrompt: string
  features: {
    chat: boolean
    strategyGeneration: boolean
    backtestAnalysis: boolean
    marketAdvice: boolean
    riskAlerts: boolean
    speechRecognition: boolean
    textToSpeech: boolean
  }
}

export interface AIUsage {
  date: string
  requests: number
  tokens: number
  cost: number
  breakdown: {
    chat: number
    strategyGeneration: number
    backtestAnalysis: number
    marketAdvice: number
    riskAlerts: number
    speechRecognition: number
    textToSpeech: number
  }
}
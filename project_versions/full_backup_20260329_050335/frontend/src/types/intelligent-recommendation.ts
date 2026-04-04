/**
 * 智能推荐系统类型定义
 */

// 经验水平类型
export type ExperienceLevel = 'beginner' | 'intermediate' | 'advanced'

// 推荐项接口
export interface Recommendation {
  id: string
  title: string
  description: string
  confidence: number
  tags: string[]
  indicators: string[]
  expectedReturn: number
  maxDrawdown: number
  sharpeRatio: number
  riskWarning: string
  parameters: Parameter[]
}

// 参数接口
export interface Parameter {
  name: string
  displayName: string
  type: 'number' | 'text' | 'select' | 'boolean' | 'date'
  value: any
  defaultValue?: any
  min?: number
  max?: number
  step?: number
  options?: Array<{
    label: string
    value: any
  }>
  placeholder?: string
  description: string
  required: boolean
  validation?: {
    pattern?: string
    minLength?: number
    maxLength?: number
  }
  error?: string | null
}

// 模板接口
export interface Template {
  id: string
  title: string
  description: string
  icon: string
  template: string
  category: string
  difficulty: ExperienceLevel
}

// 工作流预览接口
export interface WorkflowPreview {
  nodeCount: number
  connectionCount: number
  estimatedTime: string
  nodes: Array<{
    id: string
    name: string
    type: string
    position: { x: number; y: number }
  }>
  connections: Array<{
    id: string
    from: string
    to: string
    type: string
  }>
}

// 用户输入分析请求接口
export interface UserInputAnalysisRequest {
  input: string
  experienceLevel: ExperienceLevel
  context: {
    currentWorkflow?: any
    marketEnvironment: {
      market: string
      sector: string
      volatility: string
      trend: string
    }
    availableDataSources: Array<{
      id: string
      name: string
      type: string
    }>
  }
}

// 用户输入分析响应接口
export interface UserInputAnalysisResponse {
  recommendations: Recommendation[]
  analysis: {
    intent: string
    entities: Array<{
      type: string
      value: string
      confidence: number
    }>
    sentiment: 'positive' | 'negative' | 'neutral'
  }
  suggestions: string[]
}

// 参数推荐请求接口
export interface ParameterRecommendationRequest {
  recommendationId: string
  experienceLevel: ExperienceLevel
  userPreferences?: {
    riskTolerance: 'low' | 'medium' | 'high'
    timeHorizon: 'short' | 'medium' | 'long'
    investmentStyle: 'conservative' | 'balanced' | 'aggressive'
  }
}

// 工作流生成请求接口
export interface WorkflowGenerationRequest {
  recommendationId: string
  parameters: Array<{
    name: string
    value: any
  }>
  experienceLevel: ExperienceLevel
}

// 工作流生成响应接口
export interface WorkflowGenerationResponse {
  workflow: {
    id: string
    name: string
    description: string
    nodes: Array<{
      id: string
      type: string
      name: string
      config: Record<string, any>
      position: { x: number; y: number }
    }>
    connections: Array<{
      id: string
      from: string
      to: string
      type: string
      config: Record<string, any>
    }>
  }
  metadata: {
    createdAt: string
    version: string
    author: string
    tags: string[]
  }
}

// 工作流预览生成请求接口
export interface WorkflowPreviewRequest {
  recommendationId: string
  parameters: Array<{
    name: string
    value: any
  }>
}

// 配置保存接口
export interface SavedConfiguration {
  recommendation: Recommendation
  parameters: Parameter[]
  experienceLevel: ExperienceLevel
  timestamp: string
}

// 智能推荐配置接口
export interface IntelligentRecommendationConfig {
  experienceLevel: ExperienceLevel
  language: 'zh-CN' | 'en-US'
  theme: 'light' | 'dark'
  autoSave: boolean
  showAdvancedOptions: boolean
  enableRealTimeAnalysis: boolean
  analysisTimeout: number
}

// 推荐历史接口
export interface RecommendationHistory {
  id: string
  timestamp: string
  userInput: string
  experienceLevel: ExperienceLevel
  selectedRecommendation: Recommendation
  appliedParameters: Parameter[]
  result?: {
    success: boolean
    message?: string
    metrics?: Record<string, any>
  }
}

// 性能指标接口
export interface PerformanceMetrics {
  totalReturn: number
  annualizedReturn: number
  maxDrawdown: number
  sharpeRatio: number
  sortinoRatio: number
  calmarRatio: number
  winRate: number
  profitFactor: number
  avgTradeReturn: number
  avgTradeDuration: number
}

// 风险评估接口
export interface RiskAssessment {
  level: 'low' | 'medium' | 'high'
  factors: Array<{
    name: string
    impact: number
    description: string
  }>
  recommendations: string[]
}

// 市场环境分析接口
export interface MarketEnvironmentAnalysis {
  currentRegime: 'bull' | 'bear' | 'sideways'
  volatility: 'low' | 'medium' | 'high'
  trend: 'up' | 'down' | 'sideways'
  support: number[]
  resistance: number[]
  keyLevels: Array<{
    price: number
    type: 'support' | 'resistance'
    strength: number
  }>
}

// 策略类型枚举
export enum StrategyType {
  TREND_FOLLOWING = 'trend_following',
  MEAN_REVERSION = 'mean_reversion',
  MOMENTUM = 'momentum',
  BREAKOUT = 'breakout',
  PAIRS_TRADING = 'pairs_trading',
  ARBITRAGE = 'arbitrage',
  SENTIMENT = 'sentiment',
  MACHINE_LEARNING = 'machine_learning'
}

// 技术指标类型枚举
export enum IndicatorType {
  MOVING_AVERAGE = 'moving_average',
  RSI = 'rsi',
  MACD = 'macd',
  BOLLINGER_BANDS = 'bollinger_bands',
  STOCHASTIC = 'stochastic',
  ATR = 'atr',
  ADX = 'adx',
  CCI = 'cci',
  WILLIAMS_R = 'williams_r'
}

// 数据源类型枚举
export enum DataSourceType {
  STOCK = 'stock',
  FUTURES = 'futures',
  FOREX = 'forex',
  CRYPTO = 'crypto',
  BOND = 'bond',
  COMMODITY = 'commodity'
}

// 时间框架枚举
export enum TimeFrame {
  TICK = 'tick',
  MINUTE_1 = '1m',
  MINUTE_5 = '5m',
  MINUTE_15 = '15m',
  MINUTE_30 = '30m',
  HOUR_1 = '1h',
  HOUR_4 = '4h',
  DAY_1 = '1d',
  WEEK_1 = '1w',
  MONTH_1 = '1m'
}

// 资产类别枚举
export enum AssetClass {
  EQUITY = 'equity',
  FIXED_INCOME = 'fixed_income',
  COMMODITY = 'commodity',
  CURRENCY = 'currency',
  REAL_ESTATE = 'real_estate',
  ALTERNATIVE = 'alternative'
}

// 交易风格枚举
export enum TradingStyle {
  DAY_TRADING = 'day_trading',
  SWING_TRADING = 'swing_trading',
  POSITION_TRADING = 'position_trading',
  SCALPING = 'scalping',
  HIGH_FREQUENCY = 'high_frequency'
}

// 风险偏好枚举
export enum RiskPreference {
  CONSERVATIVE = 'conservative',
  MODERATE = 'moderate',
  AGGRESSIVE = 'aggressive'
}

// 投资目标枚举
export enum InvestmentGoal {
  CAPITAL_PRESERVATION = 'capital_preservation',
  INCOME_GENERATION = 'income_generation',
  CAPITAL_GROWTH = 'capital_growth',
  SPECULATION = 'speculation'
}

// 智能推荐事件类型
export interface IntelligentRecommendationEvents {
  'recommendation-generated': { recommendations: Recommendation[] }
  'parameter-updated': { parameterName: string; value: any }
  'workflow-generated': { workflow: any }
  'error-occurred': { type: string; message: string }
  'analysis-started': { input: string }
  'analysis-completed': { result: UserInputAnalysisResponse }
}

// 智能推荐状态接口
export interface IntelligentRecommendationState {
  isAnalyzing: boolean
  currentRecommendation: Recommendation | null
  selectedParameters: Parameter[]
  analysisHistory: RecommendationHistory[]
  configuration: IntelligentRecommendationConfig
  marketEnvironment: MarketEnvironmentAnalysis | null
}

// 智能推荐统计接口
export interface IntelligentRecommendationStats {
  totalAnalyses: number
  successfulGenerations: number
  averageConfidence: number
  mostUsedStrategy: StrategyType
  averageResponseTime: number
  userSatisfactionScore: number
}

// 导出格式枚举
export enum ExportFormat {
  JSON = 'json',
  CSV = 'csv',
  XML = 'xml',
  YAML = 'yaml',
  PDF = 'pdf'
}

// 导出选项接口
export interface ExportOptions {
  format: ExportFormat
  includeMetadata: boolean
  includeParameters: boolean
  includePerformance: boolean
  includeHistory: boolean
  compression?: 'gzip' | 'zip'
}

// 智能推荐错误类型
export enum IntelligentRecommendationError {
  INVALID_INPUT = 'invalid_input',
  NETWORK_ERROR = 'network_error',
  PARSING_ERROR = 'parsing_error',
  VALIDATION_ERROR = 'validation_error',
  GENERATION_ERROR = 'generation_error',
  TIMEOUT_ERROR = 'timeout_error',
  PERMISSION_ERROR = 'permission_error'
}

// 智能推荐错误详情接口
export interface IntelligentRecommendationErrorDetails {
  type: IntelligentRecommendationError
  message: string
  details?: any
  timestamp: string
  requestId?: string
}
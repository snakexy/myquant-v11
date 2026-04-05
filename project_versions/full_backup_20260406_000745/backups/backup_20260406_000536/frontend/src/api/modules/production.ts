/**
 * MyQuant v10.0.0 - Production API Module
 * Production阶段API接口封装
 * 包含：实盘交易、ML信号生成器、Meta Controller监控
 */

import { http } from '../request'

// ==================== 类型定义 ====================

// 通用响应
export interface ApiResponse<T = any> {
  success: boolean
  data?: T
  message?: string
}

// ==================== 交易相关类型 ====================

export interface Position {
  symbol: string
  name: string
  quantity: number
  cost_price: number
  current_price: number
  market_value: number
  profit_loss: number
  profit_loss_pct: number
  weight: number
}

export interface Order {
  order_id: string
  symbol: string
  name: string
  direction: 'buy' | 'sell'
  order_type: 'market' | 'limit'
  quantity: number
  price: number
  amount: number
  status: 'pending' | 'filled' | 'cancelled' | 'rejected'
  created_at: string
  filled_at?: string
  message?: string
}

export interface TradingStatus {
  is_trading: boolean
  trading_mode: string
  active_strategies: number
  today_orders: number
  today_trades: number
  account_balance: number
  total_assets: number
  today_pnl: number
  today_pnl_pct: number
}

export interface RiskMetrics {
  overall_risk_level: 'low' | 'medium' | 'high' | 'critical'
  position_concentration: number
  max_drawdown: number
  daily_loss: number
  volatility: number
  sharpe_ratio: number
  risk_alerts: RiskAlert[]
}

export interface RiskAlert {
  alert_id: string
  type: string
  severity: 'info' | 'warning' | 'critical'
  message: string
  value: number
  threshold: number
  triggered_at: string
}

// ==================== ML信号相关类型 ====================

export interface MLModel {
  model_id: string
  model_name: string
  model_type: string
  version: string
  status: 'active' | 'standby' | 'deprecated'
  accuracy: number
  ic: number
  last_trained: string
  predictions_count: number
}

export interface TradingSignal {
  signal_id: string
  symbol: string
  signal_type: 'buy' | 'sell' | 'hold'
  strength: 'strong' | 'medium' | 'weak'
  prediction_score: number
  confidence: number
  target_price?: number
  stop_loss?: number
  reason: string
  model_id: string
  generated_at: string
  expires_at?: string
}

export interface MLPrediction {
  symbol: string
  prediction_score: number
  confidence: number
  direction: 'up' | 'down' | 'flat'
  expected_return: number
  model_id: string
  features: Record<string, number>
  predicted_at: string
}

export interface SignalGenerationResult {
  success: boolean
  signals: TradingSignal[]
  model_id: string
  generated_at: string
  processing_time_ms: number
}

// ==================== Meta Controller相关类型 ====================

export interface MonitoringStatus {
  status: 'active' | 'paused' | 'stopped'
  monitoring_since: string
  monitored_models: string[]
  active_model?: string
  current_ic: number
  ic_trend: 'stable' | 'improving' | 'declining' | 'volatile'
  degradation_risk: 'low' | 'medium' | 'high' | 'critical'
  alerts_count: number
}

export interface ICMetrics {
  current: number
  ma7: number
  ma14: number
  ma30: number
  timestamp: string
}

export interface DegradationSignals {
  ic_decline_triggered: boolean
  ic_decline_value: number
  distribution_shift_triggered: boolean
  ks_statistic: number
  accuracy_decline_triggered: boolean
  accuracy_current: number
  accuracy_baseline: number
}

export interface DegradationCheckResult {
  model_id: string
  degradation_detected: boolean
  risk_level: 'low' | 'medium' | 'high' | 'critical'
  signals: DegradationSignals
  recommendation: string
  checked_at: string
  next_check_at?: string
}

export interface MonitoringAlert {
  alert_id: string
  severity: 'info' | 'warning' | 'critical'
  alert_type: string
  message: string
  model_id: string
  triggered_at: string
  status: 'active' | 'acknowledged' | 'resolved'
  acknowledged_by?: string
  acknowledged_at?: string
}

export interface ModelSwitchRecord {
  switch_id: string
  from_model: string
  to_model: string
  switch_type: 'auto' | 'manual' | 'ab_test'
  reason: string
  triggered_at: string
  executed_at?: string
  switch_time_ms: number
  success: boolean
}

// ==================== 高级风险分析类型 ====================

export interface RiskAnalysisReport {
  account_id: string
  report_time: string
  basic_metrics: {
    total_assets: number
    position_ratio: number
    max_single_position: number
    concentration: number
    total_pnl: number
    total_pnl_pct: number
  }
  risk_metrics: {
    var_95: number
    var_99: number
    cvar_95: number
    beta: number
    current_drawdown: number
    max_drawdown: number
    daily_volatility: number
  }
  factor_exposures: Record<string, number>
  exposure_limits_status: Record<string, boolean>
  stress_test_summary: {
    max_potential_loss: number
    max_potential_loss_pct: number
    worst_scenario: string
    recommendations: string[]
  }
  overall_risk_level: string
  recommendations: string[]
}

export interface VarAnalysis {
  account_id: string
  var: number
  var_pct: string
  confidence: number
  method: string
  interpretation: string
}

export interface CvarAnalysis {
  account_id: string
  cvar: number
  cvar_pct: string
  var: number
  var_pct: string
  cvar_var_ratio: number
  confidence: number
  interpretation: string
}

export interface BetaAnalysis {
  account_id: string
  beta: number
  sensitivity: string
  interpretation: string
}

export interface FactorExposureAnalysis {
  account_id: string
  exposures: Record<string, number>
  limits_status: Record<string, boolean>
  analysis: string
  warnings: string[]
}

export interface StressTestScenario {
  name: string
  params: Record<string, any>
  estimated_loss: number
  estimated_loss_pct: number
  impact_level: 'low' | 'medium' | 'high' | 'critical'
}

export interface StressTestResult {
  account_id: string
  total_assets: number
  current_pnl: number
  test_time: string
  scenarios: StressTestScenario[]
  risk_summary: {
    max_potential_loss: number
    max_potential_loss_pct: number
    worst_scenario: string
    recommendations: string[]
  }
}

export interface RiskOverview {
  account_id: string
  risk_level: string
  summary: {
    position_ratio: number
    total_pnl_pct: number
    current_drawdown: number
    var_95: number
    cvar_95: number
    beta: number
  }
  factor_exposures: Record<string, number>
  recommendations: string[]
  alerts: Array<{
    type: string
    level: string
    message: string
  }>
  charts: {
    risk_gauge: {
      value: number
      thresholds: number[]
      levels: string[]
    }
    factor_exposure_chart: {
      labels: string[]
      values: number[]
      limits: Record<string, number>
    }
  }
}

export interface RiskDimensionScore {
  score: number
  weight: number
  max_score: number
  details: string
}

export interface TopRisk {
  dimension: string
  dimension_name: string
  score: number
  details: string
}

export interface ComprehensiveRiskScore {
  account_id: string
  score: number
  level: 'low' | 'medium' | 'high' | 'critical' | 'unknown'
  dimensions: {
    position: RiskDimensionScore
    drawdown: RiskDimensionScore
    var_cvar: RiskDimensionScore
    beta_factor: RiskDimensionScore
  }
  top_risks: TopRisk[]
  recommendations: string[]
  raw_metrics?: {
    position_ratio: number
    concentration: number
    current_drawdown: number
    max_drawdown: number
    var_95: number
    cvar_95: number
    beta: number
    factor_exposures: Record<string, number>
  }
  timestamp: string
  error?: string
}

// ==================== 交易API ====================

export const tradingApi = {
  // 获取交易状态
  getStatus: () =>
    http.get<ApiResponse<TradingStatus>>('/v1/production/trading/status'),

  // 获取持仓列表
  getPositions: () =>
    http.get<ApiResponse<Position[]>>('/v1/production/trading/positions'),

  // 获取订单列表
  getOrders: (status?: string, limit?: number) =>
    http.get<ApiResponse<Order[]>>('/v1/production/trading/orders', {
      params: { status, limit }
    }),

  // 创建订单
  createOrder: (order: Partial<Order>) =>
    http.post<ApiResponse<Order>>('/v1/production/trading/orders', order),

  // 取消订单
  cancelOrder: (orderId: string) =>
    http.post<ApiResponse>(`/v1/production/trading/orders/${orderId}/cancel`),

  // 获取风险指标
  getRiskMetrics: () =>
    http.get<ApiResponse<RiskMetrics>>('/v1/production/trading/risk/metrics'),

  // 获取账户信息
  getAccount: () =>
    http.get<ApiResponse>('/v1/production/trading/account'),
}

// ==================== ML信号API ====================

export const mlSignalApi = {
  // 获取模型列表
  getModels: () =>
    http.get<ApiResponse<MLModel[]>>('/v1/production/ml/models'),

  // 获取当前激活模型
  getActiveModel: () =>
    http.get<ApiResponse<MLModel>>('/v1/production/ml/models/active'),

  // 切换模型
  switchModel: (modelId: string) =>
    http.post<ApiResponse>('/v1/production/ml/models/switch', { model_id: modelId }),

  // 获取信号列表
  getSignals: (symbol?: string, limit?: number) =>
    http.get<ApiResponse<TradingSignal[]>>('/v1/production/ml/signals', {
      params: { symbol, limit }
    }),

  // 生成信号
  generateSignals: (symbols?: string[]) =>
    http.post<ApiResponse<SignalGenerationResult>>('/v1/production/ml/signals/generate', { symbols }),

  // 获取预测
  getPredictions: (symbol?: string) =>
    http.get<ApiResponse<MLPrediction[]>>('/v1/production/ml/predictions', {
      params: { symbol }
    }),

  // 批量预测
  batchPredict: (symbols: string[]) =>
    http.post<ApiResponse<MLPrediction[]>>('/v1/production/ml/predictions/batch', { symbols }),

  // 获取信号历史
  getSignalHistory: (symbol?: string, days?: number) =>
    http.get<ApiResponse>('/v1/production/ml/signals/history', {
      params: { symbol, days }
    }),
}

// ==================== Meta Controller API ====================

export const metaControllerApi = {
  // 获取监控状态
  getStatus: () =>
    http.get<ApiResponse<MonitoringStatus>>('/v1/production/meta/status'),

  // 开始监控
  startMonitoring: (modelNames: string[]) =>
    http.post<ApiResponse>('/v1/production/meta/start', { model_names: modelNames }),

  // 停止监控
  stopMonitoring: () =>
    http.post<ApiResponse>('/v1/production/meta/stop'),

  // 获取IC跟踪数据
  getICTracking: (modelId?: string, period?: string) =>
    http.get<ApiResponse>('/v1/production/meta/ic-tracking', {
      params: { model_id: modelId, period }
    }),

  // 获取IC历史
  getICHistory: (modelId?: string, startDate?: string, endDate?: string) =>
    http.get<ApiResponse>('/v1/production/meta/ic-history', {
      params: { model_id: modelId, start_date: startDate, end_date: endDate }
    }),

  // 衰减检测
  checkDegradation: (modelId?: string) =>
    http.get<ApiResponse<DegradationCheckResult>>('/v1/production/meta/degradation/check', {
      params: { model_id: modelId }
    }),

  // 触发自动切换
  triggerAutoSwitch: (force?: boolean, targetModelId?: string) =>
    http.post<ApiResponse>('/v1/production/meta/switch/auto', {
      force,
      target_model_id: targetModelId
    }),

  // 手动切换模型
  manualSwitch: (targetModelId: string, reason: string) =>
    http.post<ApiResponse>('/v1/production/meta/switch/manual', {
      target_model_id: targetModelId,
      reason
    }),

  // 获取告警列表
  getAlerts: (status?: string, severity?: string, limit?: number) =>
    http.get<ApiResponse<{ alerts: MonitoringAlert[], critical_count: number, warning_count: number, info_count: number }>>('/v1/production/meta/alerts', {
      params: { status, severity, limit }
    }),

  // 确认告警
  acknowledgeAlert: (alertId: string, acknowledgedBy: string, note?: string) =>
    http.post<ApiResponse>('/v1/production/meta/alerts/acknowledge', {
      alert_id: alertId,
      acknowledged_by: acknowledgedBy,
      note
    }),

  // 获取性能指标
  getMetrics: () =>
    http.get<ApiResponse>('/v1/production/meta/metrics'),

  // 健康检查
  healthCheck: () =>
    http.get<ApiResponse>('/v1/production/meta/health'),
}

// ==================== 高级风险分析 API ====================

export const riskAnalysisApi = {
  // 获取完整风险分析报告
  getReport: (accountId: string) =>
    http.get<ApiResponse<RiskAnalysisReport>>(`/v1/production/risk/analysis/report/${accountId}`),

  // 获取VaR分析
  getVar: (accountId: string, confidence: number = 0.95, method: string = 'historical') =>
    http.get<ApiResponse<VarAnalysis>>(`/v1/production/risk/analysis/var/${accountId}`, {
      params: { confidence, method }
    }),

  // 获取CVaR分析
  getCvar: (accountId: string, confidence: number = 0.95) =>
    http.get<ApiResponse<CvarAnalysis>>(`/v1/production/risk/analysis/cvar/${accountId}`, {
      params: { confidence }
    }),

  // 获取Beta分析
  getBeta: (accountId: string) =>
    http.get<ApiResponse<BetaAnalysis>>(`/v1/production/risk/analysis/beta/${accountId}`),

  // 获取因子暴露分析
  getFactorExposure: (accountId: string) =>
    http.get<ApiResponse<FactorExposureAnalysis>>(`/v1/production/risk/analysis/factor-exposure/${accountId}`),

  // 运行压力测试
  runStressTest: (accountId: string, scenarios?: Array<{name: string, [key: string]: any}>) =>
    http.post<ApiResponse<StressTestResult>>(`/v1/production/risk/analysis/stress-test/${accountId}`, {
      scenarios
    }),

  // 获取风险概览（Dashboard用）
  getOverview: (accountId: string) =>
    http.get<ApiResponse<RiskOverview>>(`/v1/production/risk/analysis/overview/${accountId}`),

  // 获取综合风险评分（0-100分）
  getScore: (accountId: string) =>
    http.get<ApiResponse<ComprehensiveRiskScore>>(`/v1/production/risk/analysis/score/${accountId}`),
}

// 默认导出
export default {
  trading: tradingApi,
  mlSignal: mlSignalApi,
  metaController: metaControllerApi,
  riskAnalysis: riskAnalysisApi,
}

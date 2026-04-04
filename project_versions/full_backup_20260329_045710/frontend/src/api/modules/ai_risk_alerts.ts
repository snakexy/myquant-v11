/**
 * MyQuant v10.0.0 - AI Risk Alerts API
 * AI智能预警相关API（基于QLib原生设计）
 */

import { http } from '../request'

// ==================== 类型定义 ====================

// AI风险类型枚举
export enum AIRiskType {
  ANOMALY_DETECTION = 'anomaly_detection',      // 异常检测
  PREDICTIVE_RISK = 'predictive_risk',          // 预测性风险
  SENTIMENT_RISK = 'sentiment_risk',            // 情绪风险
  REGIME_CHANGE = 'regime_change',              // 市场制度变化
  CORRELATION_SHIFT = 'correlation_shift',        // 相关性变化
  LIQUIDITY_STRESS = 'liquidity_stress',        // 流动性压力
  VOLATILITY_CLUSTER = 'volatility_cluster'      // 波动率聚类
}

// 风险级别
export enum RiskLevel {
  LOW = 'low',
  MEDIUM = 'medium',
  HIGH = 'high',
  CRITICAL = 'critical'
}

// AI风险信号
export interface AIRiskSignal {
  id: string
  risk_type: AIRiskType
  confidence: number        // AI置信度 (0-1)
  prediction: string        // 预测结果
  factors: Record<string, number>  // 风险因子
  recommendation: string   // AI建议
  timestamp: string
  symbol?: string          // 股票代码
}

// AI模型信息
export interface AIModel {
  name: string              // 模型名称
  type: string              // 模型类型
  status: 'idle' | 'training' | 'active' | 'error'
  lastUpdate: string        // 最后更新时间
  accuracy?: number         // 准确率
  config: Record<string, any>  // 模型配置
}

// AI风险摘要
export interface AIRiskSummary {
  total_signals: number
  recent_signals: number
  risk_type_counts: Record<string, number>
  avg_confidence: Record<string, number>
  active_models: string[]
  monitored_symbols: number
}

// 警报渠道
export enum AlertChannel {
  EMAIL = 'email',
  SMS = 'sms',
  WEBHOOK = 'webhook',
  LOG = 'log',
  CONSOLE = 'console',
  DATABASE = 'database'
}

// 警报配置
export interface AlertConfig {
  channel: AlertChannel
  enabled: boolean
  risk_levels: RiskLevel[]
  recipients: string[]
  template: string
  retry_count: number
  retry_interval: number
}

// 警报消息
export interface AlertMessage {
  id: string
  alert_type: string
  alert_data: any
  channel: AlertChannel
  status: 'pending' | 'sent' | 'failed' | 'acknowledged' | 'resolved'
  created_at: string
  sent_at?: string
  error_message?: string
  retry_count: number
}

// 市场特征数据
export interface MarketFeatures {
  symbol: string
  price: number
  volume: number
  returns: number[]
  volatility: number
  momentum: number
  timestamp: string
}

// ==================== API方法 ====================

export const aiRiskAlertsApi = {
  /**
   * 获取AI风险信号列表
   * GET /api/v1/validation/ai-risk/signals
   */
  getAISignals(params?: {
    risk_type?: AIRiskType
    symbol?: string
    start_time?: string
    end_time?: string
    limit?: number
  }): Promise<{ code: number; data: AIRiskSignal[]; message: string }> {
    return http.get('/validation/ai-risk/signals', { params })
  },

  /**
   * 获取AI风险摘要
   * GET /api/v1/validation/ai-risk/summary
   */
  getAISummary(): Promise<{ code: number; data: AIRiskSummary; message: string }> {
    return http.get('/validation/ai-risk/summary')
  },

  /**
   * 获取AI模型列表
   * GET /api/v1/validation/ai-risk/models
   */
  getAIModels(): Promise<{ code: number; data: AIModel[]; message: string }> {
    return http.get('/validation/ai-risk/models')
  },

  /**
   * 更新AI模型配置
   * PUT /api/v1/validation/ai-risk/models
   */
  updateAIModels(modelUpdates: Record<string, any>): Promise<{ code: number; data: { success: boolean }; message: string }> {
    return http.put('/validation/ai-risk/models', modelUpdates)
  },

  /**
   * 更新市场特征（触发AI分析）
   * POST /api/v1/validation/ai-risk/features
   */
  updateMarketFeatures(features: MarketFeatures): Promise<{ code: number; data: { success: boolean }; message: string }> {
    return http.post('/validation/ai-risk/features', features)
  },

  /**
   * 获取警报配置
   * GET /api/v1/validation/ai-risk/alert-configs
   */
  getAlertConfigs(): Promise<{ code: number; data: AlertConfig[]; message: string }> {
    return http.get('/validation/ai-risk/alert-configs')
  },

  /**
   * 更新警报配置
   * PUT /api/v1/validation/ai-risk/alert-configs
   */
  updateAlertConfigs(configs: AlertConfig[]): Promise<{ code: number; data: { success: boolean }; message: string }> {
    return http.put('/validation/ai-risk/alert-configs', { configs })
  },

  /**
   * 启用警报渠道
   * PUT /api/v1/validation/ai-risk/alert-channels/{channel}/enable
   */
  enableAlertChannel(channel: AlertChannel): Promise<{ code: number; data: { success: boolean }; message: string }> {
    return http.put(`/validation/ai-risk/alert-channels/${channel}/enable`)
  },

  /**
   * 禁用警报渠道
   * PUT /api/v1/validation/ai-risk/alert-channels/{channel}/disable
   */
  disableAlertChannel(channel: AlertChannel): Promise<{ code: number; data: { success: boolean }; message: string }> {
    return http.put(`/validation/ai-risk/alert-channels/${channel}/disable`)
  },

  /**
   * 获取警报消息历史
   * GET /api/v1/validation/ai-risk/alert-messages
   */
  getAlertMessages(params?: {
    channel?: AlertChannel
    status?: string
    alert_type?: string
    start_time?: string
    end_time?: string
    limit?: number
  }): Promise<{ code: number; data: AlertMessage[]; message: string }> {
    return http.get('/validation/ai-risk/alert-messages', { params })
  },

  /**
   * 导出AI风险信号
   * GET /api/v1/validation/ai-risk/signals/export
   */
  exportAISignals(): Promise<{ code: number; data: Blob; message: string }> {
    return http.get('/validation/ai-risk/signals/export', {
      responseType: 'blob'
    })
  },

  /**
   * 清理旧的AI风险信号
   * DELETE /api/v1/validation/ai-risk/signals/cleanup
   */
  cleanupAISignals(days: number = 7): Promise<{ code: number; data: { deleted_count: number }; message: string }> {
    return http.delete('/validation/ai-risk/signals/cleanup', { params: { days } })
  },

  /**
   * 刷新AI风险数据
   * POST /api/v1/validation/ai-risk/refresh
   */
  refreshAIRiskData(): Promise<{
    code: number
    data: {
      signals: AIRiskSignal[]
      summary: AIRiskSummary
      models: AIModel[]
    }
    message: string
  }> {
    return http.post('/validation/ai-risk/refresh')
  }
}

export default aiRiskAlertsApi

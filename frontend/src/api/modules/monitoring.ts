/**
 * MyQuant v10.0.0 - Monitoring API
 * 实时监控相关API
 */

import { http } from '../request'

// ==================== 类型定义 ====================

// 概览指标
export interface OverviewMetrics {
  currentAssets: number
  totalReturn: number
  totalReturnRate: number
  maxDrawdown: number
  sharpeRatio: number
  updateTime: string
  trends: {
    assets: 'up' | 'down' | 'flat'
    return: 'up' | 'down' | 'flat'
    drawdown: 'up' | 'down' | 'flat'
    sharpe: 'up' | 'down' | 'flat'
  }
}

// 收益曲线数据点
export interface ReturnCurvePoint {
  time: string  // 时间戳
  value: number  // 收益值
  benchmark?: number  // 基准收益
}

// 风险指标
export interface RiskMetrics {
  maxDrawdown: number
  leverage: number
  concentration: number
  volatility: number
  status: 'normal' | 'attention' | 'warning'
}

// 持仓信息
export interface Position {
  symbol: string  // 股票代码
  name: string  // 股票名称
  quantity: number  // 持仓数量
  costPrice: number  // 成本价
  currentPrice: number  // 现价
  marketValue: number  // 市值
  profit: number  // 盈亏金额
  profitRate: number  // 盈亏比例
  weight: number  // 权重（%）
}

// 交易记录
export interface Trade {
  id: string
  time: string  // 交易时间
  symbol: string  // 股票代码
  name: string  // 股票名称
  type: 'buy' | 'sell'  // 交易类型
  quantity: number  // 数量
  price: number  // 价格
  amount: number  // 金额
}

// 预警消息
export interface AlertMessage {
  id: string
  type: 'warning' | 'error' | 'info'
  level: 'critical' | 'warning' | 'info'
  title: string
  message: string
  time: string
  read: boolean
}

// 时间周期
export type TimePeriod = 'day' | 'week' | 'month'

// ==================== API方法 ====================

export const monitoringApi = {
  /**
   * 获取概览指标
   * GET /api/v1/validation/monitoring/overview
   */
  getOverview(): Promise<{ code: number; data: OverviewMetrics; message: string }> {
    return http.get('/validation/monitoring/overview')
  },

  /**
   * 获取收益曲线数据
   * GET /api/v1/validation/monitoring/return-curve
   * @param period 时间周期（day/week/month）
   * @param startDate 开始日期
   * @param endDate 结束日期
   */
  getReturnCurve(
    period: TimePeriod = 'day',
    startDate?: string,
    endDate?: string
  ): Promise<{ code: number; data: ReturnCurvePoint[]; message: string }> {
    return http.get('/validation/monitoring/return-curve', {
      params: { period, startDate, endDate }
    })
  },

  /**
   * 获取风险指标
   * GET /api/v1/validation/monitoring/risk-metrics
   */
  getRiskMetrics(): Promise<{ code: number; data: RiskMetrics; message: string }> {
    return http.get('/validation/monitoring/risk-metrics')
  },

  /**
   * 获取当前持仓列表
   * GET /api/v1/validation/monitoring/positions
   */
  getPositions(): Promise<{ code: number; data: Position[]; message: string }> {
    return http.get('/validation/monitoring/positions')
  },

  /**
   * 获取交易记录
   * GET /api/v1/validation/monitoring/trades
   * @param limit 返回记录数量
   * @param startDate 开始日期（可选）
   * @param endDate 结束日期（可选）
   */
  getTrades(
    limit: number = 50,
    startDate?: string,
    endDate?: string
  ): Promise<{ code: number; data: Trade[]; message: string }> {
    return http.get('/validation/monitoring/trades', {
      params: { limit, startDate, endDate }
    })
  },

  /**
   * 获取预警消息
   * GET /api/v1/validation/monitoring/alerts
   * @param unreadOnly 是否只获取未读消息
   */
  getAlerts(unreadOnly: boolean = false): Promise<{ code: number; data: AlertMessage[]; message: string }> {
    return http.get('/validation/monitoring/alerts', {
      params: { unreadOnly }
    })
  },

  /**
   * 标记预警消息为已读
   * PUT /api/v1/validation/monitoring/alerts/{id}/read
   * @param alertId 预警消息ID
   */
  markAlertAsRead(alertId: string): Promise<{ code: number; data: { success: boolean }; message: string }> {
    return http.put(`/validation/monitoring/alerts/${alertId}/read`)
  },

  /**
   * 删除预警消息
   * DELETE /api/v1/validation/monitoring/alerts/{id}
   * @param alertId 预警消息ID
   */
  deleteAlert(alertId: string): Promise<{ code: number; data: { success: boolean }; message: string }> {
    return http.delete(`/validation/monitoring/alerts/${alertId}`)
  },

  /**
   * 批量标记预警消息为已读
   * PUT /api/v1/validation/monitoring/alerts/batch-read
   * @param alertIds 预警消息ID列表
   */
  batchMarkAlertsAsRead(alertIds: string[]): Promise<{ code: number; data: { success: boolean }; message: string }> {
    return http.put('/validation/monitoring/alerts/batch-read', { alertIds })
  },

  /**
   * 清空所有预警消息
   * DELETE /api/v1/validation/monitoring/alerts/all
   */
  clearAllAlerts(): Promise<{ code: number; data: { success: boolean }; message: string }> {
    return http.delete('/validation/monitoring/alerts/all')
  },

  /**
   * 刷新监控数据
   * GET /api/v1/validation/monitoring/refresh
   */
  refresh(): Promise<{
    code: number
    data: {
      overview: OverviewMetrics
      riskMetrics: RiskMetrics
      positions: Position[]
    }
    message: string
  }> {
    return http.get('/validation/monitoring/refresh')
  }
}

export default monitoringApi

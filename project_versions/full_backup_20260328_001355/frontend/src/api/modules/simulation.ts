/**
 * MyQuant v10.0.0 - Simulation API
 * 模拟实盘验证相关API
 */

import { http } from '../request'

// ==================== 类型定义 ====================

// 策略信息
export interface Strategy {
  id: string
  name: string
  description?: string
  type: 'trend_following' | 'mean_reversion' | 'ml_based' | 'momentum'
  status: 'active' | 'inactive' | 'testing'
}

// 模拟状态
export type SimulationStatus = 'idle' | 'running' | 'paused' | 'stopped'

// 模拟账户信息
export interface SimulationAccount {
  accountId: string
  initialCapital: number
  currentCapital: number
  cash: number
  totalAssets: number
  totalReturn: number
  totalReturnRate: number
  positionCount: number
  createTime: string
  updateTime: string
}

// 模拟概览指标
export interface SimulationMetrics {
  currentAssets: number
  totalReturn: number
  totalReturnRate: number
  maxDrawdown: number
  sharpeRatio: number
  positionCount: number
  lastUpdateTime: string
}

// 在线训练状态
export interface OnlineTrainingStatus {
  modelVersion: string
  lastUpdateTime: string
  trainingProgress: number
  status: 'training' | 'completed' | 'failed'
}

// 模拟详细信息
export interface SimulationDetail extends SimulationMetrics {
  simulationId: string
  strategyId: string
  status: SimulationStatus
  startTime?: string
  endTime?: string
  onlineTraining: OnlineTrainingStatus
}

// 持仓信息
export interface Position {
  symbol: string
  symbolName: string
  quantity: number
  avgPrice: number
  currentPrice: number
  marketValue: number
  costPrice: number
  unrealizedPnl: number
  unrealizedPnlRate: number
  weight: number
}

// 交易记录
export interface Order {
  orderId: string
  symbol: string
  side: 'buy' | 'sell'
  orderType: 'market' | 'limit'
  quantity: number
  price: number
  status: 'pending' | 'filled' | 'cancelled' | 'failed'
  filledQuantity: number
  filledPrice: number
  createTime: string
  updateTime: string
}

// ==================== API方法 ====================

export const simulationApi = {
  /**
   * 获取所有可用策略列表
   * GET /api/v1/validation/simulation/strategies
   */
  getStrategies(): Promise<{ code: number; data: Strategy[]; message: string }> {
    return http.get('/validation/simulation/strategies')
  },

  /**
   * 获取当前模拟状态
   * GET /api/v1/validation/simulation/status
   */
  getStatus(): Promise<{ code: number; data: SimulationDetail; message: string }> {
    return http.get('/validation/simulation/status')
  },

  /**
   * 获取模拟指标数据
   * GET /api/v1/validation/simulation/metrics
   */
  getMetrics(): Promise<{ code: number; data: SimulationMetrics; message: string }> {
    return http.get('/validation/simulation/metrics')
  },

  /**
   * 启动模拟
   * POST /api/v1/validation/simulation/start
   * @param strategyId 策略ID
   */
  startSimulation(strategyId: string): Promise<{ code: number; data: SimulationDetail; message: string }> {
    return http.post('/validation/simulation/start', { strategyId })
  },

  /**
   * 停止模拟
   * POST /api/v1/validation/simulation/stop
   */
  stopSimulation(): Promise<{ code: number; data: { success: boolean }; message: string }> {
    return http.post('/validation/simulation/stop')
  },

  /**
   * 暂停模拟
   * POST /api/v1/validation/simulation/pause
   */
  pauseSimulation(): Promise<{ code: number; data: { success: boolean }; message: string }> {
    return http.post('/validation/simulation/pause')
  },

  /**
   * 恢复模拟
   * POST /api/v1/validation/simulation/resume
   */
  resumeSimulation(): Promise<{ code: number; data: { success: boolean }; message: string }> {
    return http.post('/validation/simulation/resume')
  },

  /**
   * 刷新模拟状态
   * GET /api/v1/validation/simulation/refresh
   */
  refreshStatus(): Promise<{ code: number; data: SimulationDetail; message: string }> {
    return http.get('/validation/simulation/refresh')
  },

  /**
   * 切换策略
   * POST /api/v1/validation/simulation/switch-strategy
   * @param strategyId 新策略ID
   */
  switchStrategy(strategyId: string): Promise<{ code: number; data: { success: boolean }; message: string }> {
    return http.post('/validation/simulation/switch-strategy', { strategyId })
  },

  /**
   * 获取在线训练状态
   * GET /api/v1/validation/simulation/online-training
   */
  getOnlineTrainingStatus(): Promise<{ code: number; data: OnlineTrainingStatus; message: string }> {
    return http.get('/validation/simulation/online-training')
  },

  /**
   * 获取持仓列表
   * GET /api/v1/validation/simulation/positions/:accountId
   * @param accountId 账户ID
   */
  getPositions(accountId: string): Promise<{ code: number; data: Position[]; message: string }> {
    return http.get(`/validation/simulation/positions/${accountId}`)
  },

  /**
   * 获取交易记录
   * GET /api/v1/validation/simulation/orders/:accountId
   * @param accountId 账户ID
   */
  getOrders(accountId: string): Promise<{ code: number; data: Order[]; message: string }> {
    return http.get(`/validation/simulation/orders/${accountId}`)
  },

  /**
   * 获取账户信息
   * GET /api/v1/validation/simulation/accounts/:accountId
   * @param accountId 账户ID
   */
  getAccount(accountId: string): Promise<{ code: number; data: SimulationAccount; message: string }> {
    return http.get(`/validation/simulation/accounts/${accountId}`)
  }
}

export default simulationApi

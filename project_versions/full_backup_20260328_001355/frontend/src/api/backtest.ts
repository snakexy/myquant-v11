import axios from 'axios'

// API基础URL
const API_BASE_URL = 'http://localhost:8000/api/v1'

// 快速回测配置接口
export interface QuickBacktestConfig {
  strategy_type: string
  symbols: string[]
  days: number
  initial_capital: number
}

// 快速回测结果接口
export interface QuickBacktestResult {
  success: boolean
  backtest_id: string
  results: {
    total_return: number
    annualized_return: number
    max_drawdown: number
    sharpe_ratio: number
    win_rate: number
  }
  executed_at: string
}

// 多策略对比配置接口
export interface MultiStrategyConfig {
  strategies: Array<{
    name: string
    parameters: Record<string, any>
  }>
  symbols: string[]
  start_date: string
  end_date: string
  initial_capital: number
}

// 多策略对比结果接口
export interface MultiStrategyResult {
  success: boolean
  comparison_id: string
  results: Record<string, {
    total_return: number
    sharpe_ratio: number
    max_drawdown: number
  }>
  winner: string
  executed_at: string
}

// 执行快速回测
export const executeQuickBacktest = async (config: QuickBacktestConfig): Promise<QuickBacktestResult> => {
  try {
    const response = await axios.post(`${API_BASE_URL}/unified/quick-backtest`, config)
    return response.data
  } catch (error) {
    console.error('执行快速回测失败:', error)
    throw error
  }
}

// 执行多策略对比回测
export const executeMultiStrategyBacktest = async (config: MultiStrategyConfig): Promise<MultiStrategyResult> => {
  try {
    const response = await axios.post(`${API_BASE_URL}/advanced-backtest/multi-strategy`, config)
    return response.data
  } catch (error) {
    console.error('执行多策略对比失败:', error)
    throw error
  }
}

// 获取仪表板数据（包含回测统计信息）
export const getDashboardData = async (timeRange: string = '7d'): Promise<any> => {
  try {
    const response = await axios.get(`${API_BASE_URL}/unified/dashboard?time_range=${timeRange}`)
    return response.data
  } catch (error) {
    console.error('获取仪表板数据失败:', error)
    throw error
  }
}

// 获取系统状态（包含回测模块状态）
export const getSystemStatus = async (): Promise<any> => {
  try {
    const response = await axios.get(`${API_BASE_URL}/unified/system-status`)
    return response.data
  } catch (error) {
    console.error('获取系统状态失败:', error)
    throw error
  }
}

// 获取模块列表（包含回测相关模块）
export const getModuleList = async (): Promise<any> => {
  try {
    const response = await axios.get(`${API_BASE_URL}/unified/module-list`)
    return response.data
  } catch (error) {
    console.error('获取模块列表失败:', error)
    throw error
  }
}

// 生成AI策略（可用于回测）
export const generateAIStrategy = async (
  marketCondition: string = 'bullish',
  riskLevel: string = 'medium',
  timeHorizon: string = 'long'
): Promise<any> => {
  try {
    const response = await axios.post(
      `${API_BASE_URL}/unified/ai-strategy/generate?market_condition=${marketCondition}&risk_level=${riskLevel}&time_horizon=${timeHorizon}`
    )
    return response.data
  } catch (error) {
    console.error('生成AI策略失败:', error)
    throw error
  }
}

// 计算技术指标（用于回测分析）
export const calculateTechnicalIndicators = async (config: {
  symbols: string[]
  indicators: string[]
  period: number
  frequency: string
}): Promise<any> => {
  try {
    const response = await axios.post(`${API_BASE_URL}/analysis/technical-indicators`, config)
    return response.data
  } catch (error) {
    console.error('计算技术指标失败:', error)
    throw error
  }
}

// 获取任务统计（包含回测任务）
export const getTaskStats = async (): Promise<any> => {
  try {
    const response = await axios.get(`${API_BASE_URL}/performance/stats/tasks`)
    return response.data
  } catch (error) {
    console.error('获取任务统计失败:', error)
    throw error
  }
}

// 兼容性接口：保持与原有代码的兼容性
export const getBacktestModels = async () => {
  // 返回一些预定义的策略类型
  return [
    { id: 'momentum', name: '动量策略', description: '基于价格动量的交易策略' },
    { id: 'mean_reversion', name: '均值回归策略', description: '基于价格回归的交易策略' },
    { id: 'trend_following', name: '趋势跟踪策略', description: '基于趋势跟踪的交易策略' },
    { id: 'ai_strategy', name: 'AI策略', description: '基于机器学习的交易策略' }
  ]
}

export const startBacktestTask = async (config: any) => {
  // 转换为快速回测格式
  const quickConfig: QuickBacktestConfig = {
    strategy_type: config.modelId || 'momentum',
    symbols: [config.symbol],
    days: 30,
    initial_capital: config.initialCapital || 1000000
  }
  return executeQuickBacktest(quickConfig)
}

export const getBacktestResult = async (taskId: string) => {
  // 这里应该从任务结果中获取，暂时返回模拟数据
  return {
    status: 'completed',
    data: {
      totalReturn: 15.5,
      annualizedReturn: 18.2,
      sharpeRatio: 1.35,
      maxDrawdown: 8.5,
      winRate: 62.3,
      totalTrades: 45,
      trades: []
    }
  }
}

export const cancelBacktestTask = async (taskId: string) => {
  console.log(`取消回测任务: ${taskId}`)
}

export const getBacktestHistory = async () => {
  return []
}

export const exportBacktestResult = async (taskId: string, format: 'csv' | 'excel' | 'pdf' = 'csv') => {
  return { downloadUrl: `/api/v1/backtest/download/${taskId}.${format}` }
}
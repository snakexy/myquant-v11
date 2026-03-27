/**
 * MyQuant v10.0.0 - Unified Strategy Store
 * 统一策略与回测状态管理 - M2-17重构
 *
 * 合并来源：
 * - strategy.ts (策略配置、策略列表、回测结果、运行任务)
 * - backtest.ts (回测配置、回测结果、策略列表)
 *
 * 职责：
 * - 策略管理（CRUD操作）
 * - 回测配置与执行
 * - 回测结果存储与查询
 * - 运行任务管理
 * - 模型选择与状态跟踪
 * - localStorage持久化
 *
 * @author Claude (M2-17 Store重构)
 * @created 2026-02-04
 */

import { defineStore } from 'pinia'
import { ref, computed, watch } from 'vue'

// ========== 类型定义 ==========

/**
 * 策略状态类型
 */
export type StrategyStatus = 'active' | 'inactive' | 'testing'

/**
 * 任务类型
 */
export type TaskType = 'backtest' | 'optimization' | 'training'

/**
 * 任务状态
 */
export type TaskStatus = 'pending' | 'running' | 'completed' | 'failed'

/**
 * 导出格式
 */
export type ExportFormat = 'json' | 'csv' | 'excel'

/**
 * 策略接口
 */
export interface Strategy {
  id: string
  name: string
  description: string
  code: string
  parameters: Record<string, any>
  status: StrategyStatus
  createdAt: string
  updatedAt?: string
}

/**
 * 回测结果接口
 */
export interface BacktestResult {
  id: string
  strategyId: string
  strategyName: string
  symbol: string
  startDate: string
  endDate: string
  initialCapital: number
  finalCapital: number
  totalReturn: number
  annualizedReturn: number
  maxDrawdown: number
  sharpeRatio: number
  winRate: number
  profitLossRatio: number
  totalTrades: number
  trades: Trade[]
  timestamp: string
}

/**
 * 交易记录接口
 */
export interface Trade {
  symbol: string
  action: 'buy' | 'sell'
  price: number
  quantity: number
  timestamp: string
  profit?: number
}

/**
 * 回测配置接口
 */
export interface BacktestConfig {
  strategyId: string
  startDate: string
  endDate: string
  stockPool: string
  initialCapital: number
  benchmark: string
  commissionRate: number
  maxPosition?: number
  stopLoss?: number
  takeProfit?: number
  rebalanceFrequency?: string
}

/**
 * 运行任务接口
 */
export interface RunningTask {
  id: string
  type: TaskType
  name: string
  status: TaskStatus
  progress: number
  startTime: string
  endTime?: string
  result?: any
  error?: string
}

/**
 * 分享结果接口
 */
export interface ShareResult {
  shareId: string
  shareUrl: string
  expiryTime: string
}

// ========== 常量定义 ==========

const STORAGE_KEYS = {
  STRATEGIES: 'myquant_strategies',
  BACKTEST_RESULTS: 'myquant_backtest_results',
  CURRENT_STRATEGY: 'myquant_current_strategy',
  SELECTED_MODELS: 'myquant_selected_models'
} as const

const DEFAULT_BACKTEST_CONFIG: Partial<BacktestConfig> = {
  initialCapital: 100000,
  commissionRate: 0.0003,
  benchmark: '000001.SH',
  maxPosition: 0.3,
  stopLoss: 0.05,
  takeProfit: 0.15
}

// ========== Store定义 ==========

export const useStrategyStore = defineStore('strategy', () => {
  // ========== 状态 ==========

  /**
   * 策略列表
   */
  const strategies = ref<Strategy[]>([])

  /**
   * 当前策略
   */
  const currentStrategy = ref<Strategy | null>(null)

  /**
   * 回测结果列表
   */
  const backtestResults = ref<BacktestResult[]>([])

  /**
   * 当前回测配置
   */
  const currentBacktest = ref<BacktestConfig | null>(null)

  /**
   * 当前回测结果
   */
  const backtestResult = ref<BacktestResult | null>(null)

  /**
   * 选中的模型
   */
  const selectedModels = ref<string[]>([])

  /**
   * 运行中的任务
   */
  const runningTasks = ref<RunningTask[]>([])

  /**
   * 加载状态
   */
  const loading = ref(false)

  /**
   * 错误信息
   */
  const error = ref<string | null>(null)

  // ========== 计算属性 ==========

  /**
   * 是否有活动策略
   */
  const hasActiveStrategy = computed(() => currentStrategy.value !== null)

  /**
   * 是否有运行中的任务
   */
  const hasRunningTasks = computed(() =>
    runningTasks.value.some(task => task.status === 'running')
  )

  /**
   * 活动任务数量
   */
  const activeTaskCount = computed(() =>
    runningTasks.value.filter(task => task.status === 'running').length
  )

  /**
   * 已完成的回测数量
   */
  const completedBacktests = computed(() =>
    backtestResults.value.length
  )

  /**
   * 活动策略列表
   */
  const activeStrategies = computed(() =>
    strategies.value.filter(s => s.status === 'active')
  )

  /**
   * 策略统计
   */
  const strategyStats = computed(() => ({
    total: strategies.value.length,
    active: strategies.value.filter(s => s.status === 'active').length,
    inactive: strategies.value.filter(s => s.status === 'inactive').length,
    testing: strategies.value.filter(s => s.status === 'testing').length
  }))

  /**
   * 任务统计
   */
  const taskStats = computed(() => ({
    total: runningTasks.value.length,
    running: runningTasks.value.filter(t => t.status === 'running').length,
    completed: runningTasks.value.filter(t => t.status === 'completed').length,
    failed: runningTasks.value.filter(t => t.status === 'failed').length,
    pending: runningTasks.value.filter(t => t.status === 'pending').length
  }))

  /**
   * 回测统计
   */
  const backtestStats = computed(() => {
    if (backtestResults.value.length === 0) {
      return {
        avgReturn: 0,
        avgSharpe: 0,
        avgWinRate: 0,
        bestReturn: -Infinity,
        worstReturn: Infinity
      }
    }

    const returns = backtestResults.value.map(r => r.totalReturn)
    const sharpes = backtestResults.value.map(r => r.sharpeRatio)
    const winRates = backtestResults.value.map(r => r.winRate)

    return {
      avgReturn: returns.reduce((a, b) => a + b, 0) / returns.length,
      avgSharpe: sharpes.reduce((a, b) => a + b, 0) / sharpes.length,
      avgWinRate: winRates.reduce((a, b) => a + b, 0) / winRates.length,
      bestReturn: Math.max(...returns),
      worstReturn: Math.min(...returns)
    }
  })

  // ========== 策略操作 ==========

  /**
   * 设置当前策略
   */
  const setCurrentStrategy = (strategy: Strategy | null) => {
    currentStrategy.value = strategy
    if (strategy) {
      localStorage.setItem(STORAGE_KEYS.CURRENT_STRATEGY, JSON.stringify(strategy))
    } else {
      localStorage.removeItem(STORAGE_KEYS.CURRENT_STRATEGY)
    }
  }

  /**
   * 添加策略
   */
  const addStrategy = (strategy: Omit<Strategy, 'id' | 'createdAt'>): Strategy => {
    const newStrategy: Strategy = {
      ...strategy,
      id: generateId(),
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    }
    strategies.value.push(newStrategy)
    persistStrategies()
    return newStrategy
  }

  /**
   * 更新策略
   */
  const updateStrategy = (id: string, updates: Partial<Strategy>): boolean => {
    const index = strategies.value.findIndex(s => s.id === id)
    if (index === -1) return false

    strategies.value[index] = {
      ...strategies.value[index],
      ...updates,
      updatedAt: new Date().toISOString()
    }

    // 如果更新的是当前策略，同步更新
    if (currentStrategy.value?.id === id) {
      currentStrategy.value = { ...strategies.value[index] }
    }

    persistStrategies()
    return true
  }

  /**
   * 删除策略
   */
  const deleteStrategy = (id: string): boolean => {
    const index = strategies.value.findIndex(s => s.id === id)
    if (index === -1) return false

    strategies.value.splice(index, 1)

    // 如果删除的是当前策略，清空当前策略
    if (currentStrategy.value?.id === id) {
      setCurrentStrategy(null)
    }

    persistStrategies()
    return true
  }

  /**
   * 根据ID获取策略
   */
  const getStrategyById = (id: string): Strategy | undefined => {
    return strategies.value.find(s => s.id === id)
  }

  /**
   * 获取策略列表（从API或本地）
   */
  const fetchStrategies = async (): Promise<Strategy[]> => {
    try {
      loading.value = true
      error.value = null

      // 如果本地已有策略，直接返回
      if (strategies.value.length > 0) {
        return strategies.value
      }

      // 否则返回默认示例数据
      const mockStrategies: Strategy[] = [
        {
          id: '1',
          name: '均线策略',
          description: '基于移动平均线的趋势跟踪策略',
          code: 'def moving_average_strategy():\n  # 策略代码\n  pass',
          parameters: {
            shortPeriod: 5,
            longPeriod: 20,
            threshold: 0.02
          },
          status: 'active',
          createdAt: new Date().toISOString()
        },
        {
          id: '2',
          name: 'RSI策略',
          description: '基于相对强弱指数的超买超卖策略',
          code: 'def rsi_strategy():\n  # 策略代码\n  pass',
          parameters: {
            period: 14,
            overbought: 70,
            oversold: 30
          },
          status: 'active',
          createdAt: new Date().toISOString()
        }
      ]

      strategies.value = mockStrategies
      persistStrategies()

      return strategies.value
    } catch (err: any) {
      error.value = err.message || '获取策略列表失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  // ========== 回测操作 ==========

  /**
   * 运行回测
   */
  const runBacktest = async (config: BacktestConfig): Promise<BacktestResult> => {
    try {
      loading.value = true
      error.value = null
      currentBacktest.value = config

      // 创建回测任务
      const strategy = getStrategyById(config.strategyId)
      const task = addRunningTask({
        type: 'backtest',
        name: `回测: ${strategy?.name || config.strategyId}`,
        status: 'running',
        progress: 0
      })

      // 模拟回测进度
      await simulateProgress(task.id, (progress) => {
        updateTaskStatus(task.id, 'running', progress)
      })

      // 生成模拟回测结果
      const mockResult: BacktestResult = {
        id: generateId(),
        strategyId: config.strategyId,
        strategyName: strategy?.name || '未知策略',
        symbol: config.stockPool,
        startDate: config.startDate,
        endDate: config.endDate,
        initialCapital: config.initialCapital,
        finalCapital: config.initialCapital * (1 + Math.random() * 0.5 - 0.1),
        totalReturn: Math.random() * 40 - 10,
        annualizedReturn: Math.random() * 30 - 5,
        maxDrawdown: Math.random() * 20,
        sharpeRatio: Math.random() * 2 + 0.5,
        winRate: Math.random() * 30 + 40,
        profitLossRatio: Math.random() * 2 + 1,
        totalTrades: Math.floor(Math.random() * 200 + 50),
        trades: generateMockTrades(Math.floor(Math.random() * 200 + 50)),
        timestamp: new Date().toISOString()
      }

      backtestResult.value = mockResult
      addBacktestResult(mockResult)

      // 标记任务完成
      updateTaskStatus(task.id, 'completed', 100)

      return mockResult
    } catch (err: any) {
      error.value = err.message || '回测失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * 获取回测结果
   */
  const getBacktestResult = async (id: string): Promise<BacktestResult | null> => {
    try {
      loading.value = true
      error.value = null

      // 先从本地查找
      let result = backtestResults.value.find(r => r.id === id)

      // 如果本地没有，返回模拟数据
      if (!result) {
        await new Promise(resolve => setTimeout(resolve, 500))
        result = {
          id,
          strategyId: '1',
          strategyName: '示例策略',
          symbol: '000001.SZ',
          startDate: '2023-01-01',
          endDate: '2023-12-31',
          initialCapital: 100000,
          finalCapital: 125600,
          totalReturn: 25.6,
          annualizedReturn: 18.3,
          maxDrawdown: 8.2,
          sharpeRatio: 1.45,
          winRate: 62.5,
          profitLossRatio: 1.8,
          totalTrades: 156,
          trades: [],
          timestamp: new Date().toISOString()
        } as BacktestResult
      }

      backtestResult.value = result
      return result
    } catch (err: any) {
      error.value = err.message || '获取回测结果失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * 添加回测结果
   */
  const addBacktestResult = (result: Omit<BacktestResult, 'id' | 'timestamp'>): BacktestResult => {
    const newResult: BacktestResult = {
      ...result,
      id: result.id || generateId(),
      timestamp: result.timestamp || new Date().toISOString()
    }
    backtestResults.value.unshift(newResult)
    persistBacktestResults()
    return newResult
  }

  /**
   * 移除回测结果
   */
  const removeBacktestResult = (id: string): boolean => {
    const index = backtestResults.value.findIndex(r => r.id === id)
    if (index === -1) return false

    backtestResults.value.splice(index, 1)
    persistBacktestResults()

    // 如果删除的是当前结果，清空
    if (backtestResult.value?.id === id) {
      backtestResult.value = null
    }

    return true
  }

  /**
   * 导出回测结果
   */
  const exportBacktestResult = async (
    id: string,
    format: ExportFormat = 'json'
  ): Promise<void> => {
    try {
      loading.value = true
      error.value = null

      const result = backtestResults.value.find(r => r.id === id)
      if (!result) {
        throw new Error('回测结果不存在')
      }

      let content: string
      let mimeType: string
      let fileName: string

      if (format === 'json') {
        content = JSON.stringify(result, null, 2)
        mimeType = 'application/json'
        fileName = `backtest_result_${id}.json`
      } else if (format === 'csv') {
        content = convertToCSV(result)
        mimeType = 'text/csv'
        fileName = `backtest_result_${id}.csv`
      } else {
        // Excel format (simplified as CSV with .xlsx extension)
        content = convertToCSV(result)
        mimeType = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        fileName = `backtest_result_${id}.xlsx`
      }

      // 触发下载
      const blob = new Blob([content], { type: mimeType })
      const url = URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = fileName
      link.click()
      URL.revokeObjectURL(url)
    } catch (err: any) {
      error.value = err.message || '导出回测结果失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * 分享回测结果
   */
  const shareBacktestResult = async (id: string): Promise<ShareResult> => {
    try {
      loading.value = true
      error.value = null

      const result = backtestResults.value.find(r => r.id === id)
      if (!result) {
        throw new Error('回测结果不存在')
      }

      // 模拟分享功能
      const shareResult: ShareResult = {
        shareId: `share_${id}_${Date.now()}`,
        shareUrl: `${window.location.origin}/share/backtest/${id}`,
        expiryTime: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString()
      }

      return shareResult
    } catch (err: any) {
      error.value = err.message || '分享回测结果失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  // ========== 任务操作 ==========

  /**
   * 设置选中的模型
   */
  const setSelectedModels = (models: string[]) => {
    selectedModels.value = models
    localStorage.setItem(STORAGE_KEYS.SELECTED_MODELS, JSON.stringify(models))
  }

  /**
   * 添加运行任务
   */
  const addRunningTask = (task: Omit<RunningTask, 'id' | 'startTime'>): RunningTask => {
    const newTask: RunningTask = {
      ...task,
      id: generateId(),
      startTime: new Date().toISOString()
    }
    runningTasks.value.push(newTask)
    return newTask
  }

  /**
   * 更新任务状态
   */
  const updateTaskStatus = (
    id: string,
    status: TaskStatus,
    progress?: number
  ): boolean => {
    const task = runningTasks.value.find(t => t.id === id)
    if (!task) return false

    task.status = status
    if (progress !== undefined) {
      task.progress = progress
    }

    if (status === 'completed' || status === 'failed') {
      task.endTime = new Date().toISOString()
    }

    return true
  }

  /**
   * 移除任务
   */
  const removeTask = (id: string): boolean => {
    const index = runningTasks.value.findIndex(t => t.id === id)
    if (index === -1) return false

    runningTasks.value.splice(index, 1)
    return true
  }

  /**
   * 清空所有任务
   */
  const clearTasks = () => {
    runningTasks.value = []
  }

  // ========== 持久化操作 ==========

  /**
   * 持久化策略列表
   */
  const persistStrategies = () => {
    try {
      localStorage.setItem(STORAGE_KEYS.STRATEGIES, JSON.stringify(strategies.value))
    } catch (e) {
      console.error('[StrategyStore] 保存策略失败:', e)
    }
  }

  /**
   * 持久化回测结果
   */
  const persistBacktestResults = () => {
    try {
      localStorage.setItem(STORAGE_KEYS.BACKTEST_RESULTS, JSON.stringify(backtestResults.value))
    } catch (e) {
      console.error('[StrategyStore] 保存回测结果失败:', e)
    }
  }

  /**
   * 从localStorage恢复数据
   */
  const restoreFromStorage = () => {
    try {
      // 恢复策略列表
      const savedStrategies = localStorage.getItem(STORAGE_KEYS.STRATEGIES)
      if (savedStrategies) {
        strategies.value = JSON.parse(savedStrategies)
      }

      // 恢复回测结果
      const savedResults = localStorage.getItem(STORAGE_KEYS.BACKTEST_RESULTS)
      if (savedResults) {
        backtestResults.value = JSON.parse(savedResults)
      }

      // 恢复当前策略
      const savedCurrentStrategy = localStorage.getItem(STORAGE_KEYS.CURRENT_STRATEGY)
      if (savedCurrentStrategy) {
        currentStrategy.value = JSON.parse(savedCurrentStrategy)
      }

      // 恢复选中的模型
      const savedModels = localStorage.getItem(STORAGE_KEYS.SELECTED_MODELS)
      if (savedModels) {
        selectedModels.value = JSON.parse(savedModels)
      }

      console.log('[StrategyStore] 数据已从localStorage恢复', {
        strategies: strategies.value.length,
        backtestResults: backtestResults.value.length
      })
    } catch (e) {
      console.error('[StrategyStore] 从localStorage恢复失败:', e)
    }
  }

  /**
   * 清除错误
   */
  const clearError = () => {
    error.value = null
  }

  /**
   * 重置状态
   */
  const resetState = () => {
    currentStrategy.value = null
    currentBacktest.value = null
    backtestResult.value = null
    selectedModels.value = []
    runningTasks.value = []
    error.value = null
  }

  /**
   * 清除所有数据（包括localStorage）
   */
  const clearAllData = () => {
    strategies.value = []
    backtestResults.value = []
    resetState()

    Object.values(STORAGE_KEYS).forEach(key => {
      localStorage.removeItem(key)
    })
  }

  // ========== 初始化 ==========

  /**
   * 初始化Store
   */
  const initializeStore = () => {
    restoreFromStorage()
  }

  // ========== 辅助函数 ==========

  /**
   * 生成唯一ID
   */
  const generateId = (): string => {
    return `${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
  }

  /**
   * 模拟进度更新
   */
  const simulateProgress = async (
    taskId: string,
    onUpdate: (progress: number) => void
  ): Promise<void> => {
    const steps = [0, 10, 30, 50, 70, 90, 100]
    for (const step of steps) {
      await new Promise(resolve => setTimeout(resolve, 300))
      onUpdate(step)
    }
  }

  /**
   * 生成模拟交易记录
   */
  const generateMockTrades = (count: number): Trade[] => {
    const trades: Trade[] = []
    const actions: Array<'buy' | 'sell'> = ['buy', 'sell']

    for (let i = 0; i < count; i++) {
      trades.push({
        symbol: `00000${(i % 10) + 1}.SZ`,
        action: actions[i % 2],
        price: Math.random() * 100 + 10,
        quantity: Math.floor(Math.random() * 1000 + 100),
        timestamp: new Date(Date.now() - (count - i) * 86400000).toISOString(),
        profit: i % 2 === 1 ? Math.random() * 1000 - 200 : undefined
      })
    }

    return trades
  }

  /**
   * 转换为CSV格式
   */
  const convertToCSV = (result: BacktestResult): string => {
    const headers = [
      'ID', '策略ID', '策略名称', '标的', '开始日期', '结束日期',
      '初始资金', '最终资金', '总收益率', '年化收益率', '最大回撤',
      '夏普比率', '胜率', '盈亏比', '交易次数', '时间戳'
    ]

    const values = [
      result.id,
      result.strategyId,
      result.strategyName,
      result.symbol,
      result.startDate,
      result.endDate,
      result.initialCapital,
      result.finalCapital,
      result.totalReturn.toFixed(2),
      result.annualizedReturn.toFixed(2),
      result.maxDrawdown.toFixed(2),
      result.sharpeRatio.toFixed(2),
      result.winRate.toFixed(2),
      result.profitLossRatio.toFixed(2),
      result.totalTrades,
      result.timestamp
    ]

    return [headers.join(','), values.join(',')].join('\n')
  }

  // ========== 监听变化 ==========

  // 自动持久化策略列表
  watch(strategies, () => {
    persistStrategies()
  }, { deep: true })

  // 自动持久化回测结果
  watch(backtestResults, () => {
    persistBacktestResults()
  }, { deep: true })

  return {
    // ========== 状态 ==========
    strategies,
    currentStrategy,
    backtestResults,
    currentBacktest,
    backtestResult,
    selectedModels,
    runningTasks,
    loading,
    error,

    // ========== 计算属性 ==========
    hasActiveStrategy,
    hasRunningTasks,
    activeTaskCount,
    completedBacktests,
    activeStrategies,
    strategyStats,
    taskStats,
    backtestStats,

    // ========== 策略操作 ==========
    setCurrentStrategy,
    addStrategy,
    updateStrategy,
    deleteStrategy,
    getStrategyById,
    fetchStrategies,

    // ========== 回测操作 ==========
    runBacktest,
    getBacktestResult,
    addBacktestResult,
    removeBacktestResult,
    exportBacktestResult,
    shareBacktestResult,

    // ========== 任务操作 ==========
    setSelectedModels,
    addRunningTask,
    updateTaskStatus,
    removeTask,
    clearTasks,

    // ========== 持久化操作 ==========
    persistStrategies,
    persistBacktestResults,
    restoreFromStorage,
    clearError,
    resetState,
    clearAllData,

    // ========== 初始化 ==========
    initializeStore
  }
})

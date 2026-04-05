/**
 * MyQuant v10.0.0 - Trading Store
 * 交易管理状态管理 - 模拟交易和实盘交易
 *
 * 职责：
 * - 交易配置管理
 * - 订单管理（下单、撤单、状态更新）
 * - 持仓管理（持仓统计、盈亏计算）
 * - 交易历史记录
 * - 账户信息管理
 * - 风险规则管理
 * - localStorage持久化
 *
 * @author Claude (M2-17 Store重构)
 * @created 2026-02-04
 */

import { defineStore } from 'pinia'
import { ref, computed, watch } from 'vue'

// ========== 类型定义 ==========

/**
 * 交易模式
 */
export type TradingMode = 'simulation' | 'real'

/**
 * 订单类型
 */
export type OrderType = 'buy' | 'sell'

/**
 * 订单状态
 */
export type OrderStatus = 'pending' | 'partial' | 'filled' | 'cancelled'

/**
 * 风险规则类型
 */
export type RiskRuleType = 'loss_limit' | 'position_limit' | 'drawdown_limit'

/**
 * 风险动作
 */
export type RiskAction = 'stop_trading' | 'alert' | 'reduce_position'

/**
 * 交易配置接口
 */
export interface TradingConfig {
  mode: TradingMode           // 模拟/实盘
  broker: string              // 券商
  accountId: string           // 账户ID
  autoTrade: boolean          // 自动交易
  maxPosition: number         // 最大持仓数
  stopLoss: number            // 止损比例
  takeProfit: number          // 止盈比例
  commissionRate: number      // 手续费率
  slippage: number            // 滑点比例
}

/**
 * 订单接口
 */
export interface Order {
  id: string
  symbol: string
  type: OrderType
  price: number
  quantity: number
  status: OrderStatus
  filledQuantity: number
  filledPrice: number
  createTime: string
  updateTime: string
  strategyId?: string
}

/**
 * 持仓接口
 */
export interface Position {
  symbol: string
  quantity: number
  avgPrice: number
  currentPrice: number
  marketValue: number
  cost: number
  profitLoss: number
  profitLossPercent: number
  weight: number
}

/**
 * 交易记录接口
 */
export interface Trade {
  id: string
  symbol: string
  type: OrderType
  price: number
  quantity: number
  time: string
  profitLoss?: number
  strategyId?: string
}

/**
 * 账户信息接口
 */
export interface Account {
  totalAssets: number         // 总资产
  cash: number                // 现金
  marketValue: number         // 市值
  availableCash: number       // 可用资金
  frozenCash: number          // 冻结资金
  profitLoss: number          // 总盈亏
  profitLossPercent: number   // 盈亏比例
  updateTime: string          // 更新时间
}

/**
 * 风险规则接口
 */
export interface RiskRule {
  id: string
  name: string
  type: RiskRuleType
  threshold: number
  action: RiskAction
  enabled: boolean
}

/**
 * 持仓统计接口
 */
export interface PositionStats {
  totalMarketValue: number
  totalCost: number
  totalProfitLoss: number
  totalProfitLossPercent: number
  profitablePositions: number
  lossPositions: number
}

/**
 * 账户摘要接口
 */
export interface AccountSummary {
  totalAssets: number
  dailyProfitLoss: number
  dailyProfitLossPercent: number
  totalProfitLoss: number
  totalProfitLossPercent: number
  positionCount: number
  cashRatio: number
}

/**
 * 导出格式
 */
export type ExportFormat = 'json' | 'csv' | 'excel'

// ========== 常量定义 ==========

const STORAGE_KEYS = {
  TRADING_CONFIG: 'myquant_trading_config',
  ORDERS: 'myquant_orders',
  POSITIONS: 'myquant_positions',
  TRADES: 'myquant_trades',
  ACCOUNT: 'myquant_account',
  ORDERS_HISTORY: 'myquant_orders_history',
  RISK_RULES: 'myquant_risk_rules'
} as const

const DEFAULT_TRADING_CONFIG: TradingConfig = {
  mode: 'simulation',
  broker: '模拟券商',
  accountId: 'simulation_001',
  autoTrade: false,
  maxPosition: 5,
  stopLoss: 0.05,
  takeProfit: 0.15,
  commissionRate: 0.0003,
  slippage: 0.001
}

const DEFAULT_ACCOUNT: Account = {
  totalAssets: 1000000,
  cash: 1000000,
  marketValue: 0,
  availableCash: 1000000,
  frozenCash: 0,
  profitLoss: 0,
  profitLossPercent: 0,
  updateTime: new Date().toISOString()
}

// ========== Store定义 ==========

export const useTradingStore = defineStore('trading', () => {
  // ========== 状态 ==========

  /**
   * 交易配置
   */
  const tradingConfig = ref<TradingConfig>({ ...DEFAULT_TRADING_CONFIG })

  /**
   * 订单列表
   */
  const orders = ref<Order[]>([])

  /**
   * 持仓列表
   */
  const positions = ref<Position[]>([])

  /**
   * 交易历史
   */
  const trades = ref<Trade[]>([])

  /**
   * 账户信息
   */
  const account = ref<Account>({ ...DEFAULT_ACCOUNT })

  /**
   * 历史订单
   */
  const ordersHistory = ref<Order[]>([])

  /**
   * 风险规则
   */
  const riskRules = ref<RiskRule[]>([])

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
   * 总持仓数
   */
  const totalPositions = computed(() => positions.value.length)

  /**
   * 总订单数
   */
  const totalOrders = computed(() => orders.value.length)

  /**
   * 待成交订单
   */
  const pendingOrders = computed(() =>
    orders.value.filter(order => order.status === 'pending')
  )

  /**
   * 持仓统计
   */
  const positionStats = computed((): PositionStats => {
    if (positions.value.length === 0) {
      return {
        totalMarketValue: 0,
        totalCost: 0,
        totalProfitLoss: 0,
        totalProfitLossPercent: 0,
        profitablePositions: 0,
        lossPositions: 0
      }
    }

    const totalMarketValue = positions.value.reduce((sum, p) => sum + p.marketValue, 0)
    const totalCost = positions.value.reduce((sum, p) => sum + p.cost, 0)
    const totalProfitLoss = positions.value.reduce((sum, p) => sum + p.profitLoss, 0)
    const profitablePositions = positions.value.filter(p => p.profitLoss > 0).length
    const lossPositions = positions.value.filter(p => p.profitLoss < 0).length

    return {
      totalMarketValue,
      totalCost,
      totalProfitLoss,
      totalProfitLossPercent: totalCost > 0 ? (totalProfitLoss / totalCost) * 100 : 0,
      profitablePositions,
      lossPositions
    }
  })

  /**
   * 今日盈亏
   */
  const todayProfitLoss = computed(() => {
    const today = new Date().toISOString().split('T')[0]
    const todayTrades = trades.value.filter(trade =>
      trade.time.startsWith(today)
    )
    return todayTrades.reduce((sum, trade) => sum + (trade.profitLoss || 0), 0)
  })

  /**
   * 账户摘要
   */
  const accountSummary = computed((): AccountSummary => {
    const dailyProfitLoss = todayProfitLoss.value
    const dailyProfitLossPercent = account.value.totalAssets > 0
      ? (dailyProfitLoss / account.value.totalAssets) * 100
      : 0

    return {
      totalAssets: account.value.totalAssets,
      dailyProfitLoss,
      dailyProfitLossPercent,
      totalProfitLoss: account.value.profitLoss,
      totalProfitLossPercent: account.value.profitLossPercent,
      positionCount: positions.value.length,
      cashRatio: account.value.totalAssets > 0
        ? (account.value.cash / account.value.totalAssets) * 100
        : 0
    }
  })

  /**
   * 活跃风险规则
   */
  const activeRiskRules = computed(() =>
    riskRules.value.filter(rule => rule.enabled)
  )

  /**
   * 今日订单数
   */
  const todayOrderCount = computed(() => {
    const today = new Date().toISOString().split('T')[0]
    return orders.value.filter(order =>
      order.createTime.startsWith(today)
    ).length
  })

  /**
   * 成交订单数
   */
  const filledOrderCount = computed(() =>
    orders.value.filter(order => order.status === 'filled').length
  )

  // ========== 交易配置操作 ==========

  /**
   * 设置交易配置
   */
  const setTradingConfig = (config: Partial<TradingConfig>): boolean => {
    try {
      tradingConfig.value = {
        ...tradingConfig.value,
        ...config
      }
      persistTradingConfig()
      return true
    } catch (err: any) {
      error.value = err.message || '设置交易配置失败'
      return false
    }
  }

  /**
   * 重置交易配置
   */
  const resetTradingConfig = () => {
    tradingConfig.value = { ...DEFAULT_TRADING_CONFIG }
    persistTradingConfig()
  }

  // ========== 订单操作 ==========

  /**
   * 下单
   */
  const placeOrder = (
    symbol: string,
    type: OrderType,
    price: number,
    quantity: number,
    strategyId?: string
  ): Order => {
    try {
      // 检查资金是否充足
      if (type === 'buy') {
        const requiredAmount = price * quantity * (1 + tradingConfig.value.commissionRate)
        if (requiredAmount > account.value.availableCash) {
          throw new Error('可用资金不足')
        }
      }

      // 检查持仓数量限制
      if (type === 'buy' && positions.value.length >= tradingConfig.value.maxPosition) {
        throw new Error(`超过最大持仓数限制 (${tradingConfig.value.maxPosition})`)
      }

      // 检查风险规则
      const riskCheck = checkRiskRules()
      if (!riskCheck.passed) {
        throw new Error(`风险检查失败: ${riskCheck.message}`)
      }

      const newOrder: Order = {
        id: generateId(),
        symbol,
        type,
        price,
        quantity,
        status: 'pending',
        filledQuantity: 0,
        filledPrice: 0,
        createTime: new Date().toISOString(),
        updateTime: new Date().toISOString(),
        strategyId
      }

      orders.value.push(newOrder)
      persistOrders()

      // 冻结资金
      if (type === 'buy') {
        const frozenAmount = price * quantity
        account.value.frozenCash += frozenAmount
        account.value.availableCash -= frozenAmount
        persistAccount()
      }

      // 模拟自动成交
      if (tradingConfig.value.autoTrade) {
        simulateOrderFill(newOrder.id)
      }

      return newOrder
    } catch (err: any) {
      error.value = err.message || '下单失败'
      throw err
    }
  }

  /**
   * 撤单
   */
  const cancelOrder = (orderId: string): boolean => {
    try {
      const index = orders.value.findIndex(order => order.id === orderId)
      if (index === -1) {
        throw new Error('订单不存在')
      }

      const order = orders.value[index]
      if (order.status === 'filled' || order.status === 'cancelled') {
        throw new Error('订单已成交或已撤销，无法撤单')
      }

      // 解冻资金
      if (order.type === 'buy' && order.status === 'pending') {
        const frozenAmount = order.price * order.quantity
        account.value.frozenCash -= frozenAmount
        account.value.availableCash += frozenAmount
        persistAccount()
      }

      // 更新订单状态
      order.status = 'cancelled'
      order.updateTime = new Date().toISOString()

      // 移入历史订单
      ordersHistory.value.push({ ...order })
      orders.value.splice(index, 1)

      persistOrders()
      persistOrdersHistory()

      return true
    } catch (err: any) {
      error.value = err.message || '撤单失败'
      return false
    }
  }

  /**
   * 更新订单状态
   */
  const updateOrderStatus = (
    orderId: string,
    status: OrderStatus,
    filledQuantity?: number,
    filledPrice?: number
  ): boolean => {
    try {
      const order = orders.value.find(o => o.id === orderId)
      if (!order) {
        throw new Error('订单不存在')
      }

      order.status = status
      order.updateTime = new Date().toISOString()

      if (filledQuantity !== undefined) {
        order.filledQuantity = filledQuantity
      }

      if (filledPrice !== undefined) {
        order.filledPrice = filledPrice
      }

      // 如果订单完全成交，更新持仓和账户
      if (status === 'filled' || status === 'partial') {
        updatePositionsAfterOrder(order)
      }

      // 如果订单完成，移入历史
      if (status === 'filled' || status === 'cancelled') {
        const index = orders.value.findIndex(o => o.id === orderId)
        if (index !== -1) {
          ordersHistory.value.push({ ...order })
          orders.value.splice(index, 1)
          persistOrdersHistory()
        }
      }

      persistOrders()
      return true
    } catch (err: any) {
      error.value = err.message || '更新订单状态失败'
      return false
    }
  }

  /**
   * 模拟订单成交
   */
  const simulateOrderFill = async (orderId: string): Promise<void> => {
    await new Promise(resolve => setTimeout(resolve, 1000))

    const order = orders.value.find(o => o.id === orderId)
    if (!order || order.status !== 'pending') return

    // 模拟滑点
    const actualPrice = order.type === 'buy'
      ? order.price * (1 + tradingConfig.value.slippage)
      : order.price * (1 - tradingConfig.value.slippage)

    updateOrderStatus(orderId, 'filled', order.quantity, actualPrice)
  }

  // ========== 持仓操作 ==========

  /**
   * 订单成交后更新持仓
   */
  const updatePositionsAfterOrder = (order: Order): void => {
    const existingPosition = positions.value.find(p => p.symbol === order.symbol)

    if (order.type === 'buy') {
      // 买入
      if (existingPosition) {
        // 加仓
        const totalCost = existingPosition.cost + order.filledPrice * order.filledQuantity
        const totalQuantity = existingPosition.quantity + order.filledQuantity
        existingPosition.avgPrice = totalCost / totalQuantity
        existingPosition.quantity = totalQuantity
        existingPosition.cost = totalCost
        existingPosition.marketValue = existingPosition.quantity * existingPosition.currentPrice
        existingPosition.profitLoss = existingPosition.marketValue - existingPosition.cost
        existingPosition.profitLossPercent = (existingPosition.profitLoss / existingPosition.cost) * 100
      } else {
        // 新建持仓
        const newPosition: Position = {
          symbol: order.symbol,
          quantity: order.filledQuantity,
          avgPrice: order.filledPrice,
          currentPrice: order.filledPrice,
          marketValue: order.filledPrice * order.filledQuantity,
          cost: order.filledPrice * order.filledQuantity,
          profitLoss: 0,
          profitLossPercent: 0,
          weight: 0
        }
        positions.value.push(newPosition)
      }

      // 更新账户
      account.value.cash -= order.filledPrice * order.filledQuantity
      account.value.frozenCash -= order.price * order.quantity
    } else {
      // 卖出
      if (existingPosition) {
        const sellValue = order.filledPrice * order.filledQuantity
        const profitLoss = (order.filledPrice - existingPosition.avgPrice) * order.filledQuantity

        // 减仓
        existingPosition.quantity -= order.filledQuantity
        existingPosition.cost = existingPosition.avgPrice * existingPosition.quantity
        existingPosition.marketValue = existingPosition.quantity * existingPosition.currentPrice

        if (existingPosition.quantity === 0) {
          // 清仓，移除持仓
          const index = positions.value.findIndex(p => p.symbol === order.symbol)
          positions.value.splice(index, 1)
        } else {
          // 更新盈亏
          existingPosition.profitLoss = existingPosition.marketValue - existingPosition.cost
          existingPosition.profitLossPercent = (existingPosition.profitLoss / existingPosition.cost) * 100
        }

        // 更新账户
        account.value.cash += sellValue

        // 记录交易
        addTrade({
          symbol: order.symbol,
          type: 'sell',
          price: order.filledPrice,
          quantity: order.filledQuantity,
          profitLoss
        })
      }
    }

    // 更新账户市值和权重
    updateAccountMarketValue()
    persistPositions()
    persistAccount()
  }

  /**
   * 更新持仓价格
   */
  const updatePositions = (priceUpdates: Array<{ symbol: string; price: number }>): void => {
    priceUpdates.forEach(update => {
      const position = positions.value.find(p => p.symbol === update.symbol)
      if (position) {
        position.currentPrice = update.price
        position.marketValue = position.quantity * position.currentPrice
        position.profitLoss = position.marketValue - position.cost
        position.profitLossPercent = (position.profitLoss / position.cost) * 100
      }
    })

    updateAccountMarketValue()
    persistPositions()
    persistAccount()
  }

  /**
   * 更新账户市值
   */
  const updateAccountMarketValue = (): void => {
    const totalMarketValue = positions.value.reduce((sum, p) => sum + p.marketValue, 0)
    account.value.marketValue = totalMarketValue
    account.value.totalAssets = account.value.cash + totalMarketValue

    // 更新持仓权重
    positions.value.forEach(position => {
      position.weight = totalMarketValue > 0
        ? (position.marketValue / totalMarketValue) * 100
        : 0
    })

    // 更新总盈亏
    account.value.profitLoss = account.value.totalAssets - DEFAULT_ACCOUNT.totalAssets
    account.value.profitLossPercent = (account.value.profitLoss / DEFAULT_ACCOUNT.totalAssets) * 100
    account.value.updateTime = new Date().toISOString()
  }

  /**
   * 清空所有持仓
   */
  const clearAllPositions = (): void => {
    positions.value.forEach(position => {
      // 卖出所有持仓
      if (position.quantity > 0) {
        const sellValue = position.currentPrice * position.quantity
        account.value.cash += sellValue

        // 记录交易
        addTrade({
          symbol: position.symbol,
          type: 'sell',
          price: position.currentPrice,
          quantity: position.quantity,
          profitLoss: position.profitLoss
        })
      }
    })

    positions.value = []
    updateAccountMarketValue()
    persistPositions()
    persistAccount()
  }

  // ========== 交易历史操作 ==========

  /**
   * 添加交易记录
   */
  const addTrade = (trade: Omit<Trade, 'id' | 'time'>): Trade => {
    const newTrade: Trade = {
      ...trade,
      id: generateId(),
      time: new Date().toISOString()
    }

    trades.value.unshift(newTrade)
    persistTrades()
    return newTrade
  }

  /**
   * 获取交易历史
   */
  const getTradeHistory = (symbol?: string, limit?: number): Trade[] => {
    let filteredTrades = trades.value

    if (symbol) {
      filteredTrades = filteredTrades.filter(trade => trade.symbol === symbol)
    }

    if (limit) {
      filteredTrades = filteredTrades.slice(0, limit)
    }

    return filteredTrades
  }

  /**
   * 清空交易历史
   */
  const clearTradeHistory = (): void => {
    trades.value = []
    persistTrades()
  }

  // ========== 账户操作 ==========

  /**
   * 更新账户信息
   */
  const updateAccount = (updates: Partial<Account>): boolean => {
    try {
      account.value = {
        ...account.value,
        ...updates,
        updateTime: new Date().toISOString()
      }
      persistAccount()
      return true
    } catch (err: any) {
      error.value = err.message || '更新账户信息失败'
      return false
    }
  }

  /**
   * 重置账户
   */
  const resetAccount = (): void => {
    account.value = { ...DEFAULT_ACCOUNT }
    persistAccount()
  }

  /**
   * 存入资金
   */
  const deposit = (amount: number): boolean => {
    if (amount <= 0) {
      error.value = '存入金额必须大于0'
      return false
    }

    account.value.cash += amount
    account.value.availableCash += amount
    account.value.totalAssets += amount
    account.value.updateTime = new Date().toISOString()
    persistAccount()
    return true
  }

  /**
   * 取出资金
   */
  const withdraw = (amount: number): boolean => {
    if (amount <= 0) {
      error.value = '取出金额必须大于0'
      return false
    }

    if (amount > account.value.availableCash) {
      error.value = '可用资金不足'
      return false
    }

    account.value.cash -= amount
    account.value.availableCash -= amount
    account.value.totalAssets -= amount
    account.value.updateTime = new Date().toISOString()
    persistAccount()
    return true
  }

  // ========== 风险规则操作 ==========

  /**
   * 添加风险规则
   */
  const addRiskRule = (rule: Omit<RiskRule, 'id'>): RiskRule => {
    const newRule: RiskRule = {
      ...rule,
      id: generateId()
    }

    riskRules.value.push(newRule)
    persistRiskRules()
    return newRule
  }

  /**
   * 更新风险规则
   */
  const updateRiskRule = (id: string, updates: Partial<RiskRule>): boolean => {
    const index = riskRules.value.findIndex(rule => rule.id === id)
    if (index === -1) return false

    riskRules.value[index] = {
      ...riskRules.value[index],
      ...updates
    }

    persistRiskRules()
    return true
  }

  /**
   * 删除风险规则
   */
  const removeRiskRule = (id: string): boolean => {
    const index = riskRules.value.findIndex(rule => rule.id === id)
    if (index === -1) return false

    riskRules.value.splice(index, 1)
    persistRiskRules()
    return true
  }

  /**
   * 检查风险规则
   */
  const checkRiskRules = (): { passed: boolean; message?: string } => {
    for (const rule of activeRiskRules.value) {
      let triggered = false

      switch (rule.type) {
        case 'loss_limit':
          // 单日亏损限制
          const dailyLoss = todayProfitLoss.value
          if (dailyLoss < -rule.threshold) {
            triggered = true
          }
          break

        case 'position_limit':
          // 持仓数量限制
          if (positions.value.length >= rule.threshold) {
            triggered = true
          }
          break

        case 'drawdown_limit':
          // 回撤限制
          const drawdown = account.value.profitLossPercent
          if (drawdown < -rule.threshold) {
            triggered = true
          }
          break
      }

      if (triggered) {
        // 执行风险动作
        if (rule.action === 'stop_trading') {
          tradingConfig.value.autoTrade = false
          return {
            passed: false,
            message: `${rule.name} 触发，自动交易已停止`
          }
        } else if (rule.action === 'alert') {
          console.warn(`[TradingStore] 风险警告: ${rule.name} 触发`)
        } else if (rule.action === 'reduce_position') {
          // 可以在这里实现减仓逻辑
          console.warn(`[TradingStore] 风险警告: ${rule.name} 触发，建议减仓`)
        }
      }
    }

    return { passed: true }
  }

  /**
   * 清空风险规则
   */
  const clearRiskRules = (): void => {
    riskRules.value = []
    persistRiskRules()
  }

  // ========== 导出操作 ==========

  /**
   * 导出交易数据
   */
  const exportTradingData = async (format: ExportFormat = 'json'): Promise<void> => {
    try {
      loading.value = true
      error.value = null

      const data = {
        tradingConfig: tradingConfig.value,
        orders: orders.value,
        positions: positions.value,
        trades: trades.value,
        account: account.value,
        ordersHistory: ordersHistory.value,
        riskRules: riskRules.value,
        exportTime: new Date().toISOString()
      }

      let content: string
      let mimeType: string
      let fileName: string

      if (format === 'json') {
        content = JSON.stringify(data, null, 2)
        mimeType = 'application/json'
        fileName = `trading_data_${Date.now()}.json`
      } else if (format === 'csv') {
        content = convertToCSV(data)
        mimeType = 'text/csv'
        fileName = `trading_data_${Date.now()}.csv`
      } else {
        content = convertToCSV(data)
        mimeType = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        fileName = `trading_data_${Date.now()}.xlsx`
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
      error.value = err.message || '导出交易数据失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * 导入交易数据
   */
  const importTradingData = async (file: File): Promise<void> => {
    try {
      loading.value = true
      error.value = null

      const content = await file.text()
      const data = JSON.parse(content)

      // 验证数据格式
      if (data.tradingConfig) {
        tradingConfig.value = data.tradingConfig
      }
      if (data.orders) {
        orders.value = data.orders
      }
      if (data.positions) {
        positions.value = data.positions
      }
      if (data.trades) {
        trades.value = data.trades
      }
      if (data.account) {
        account.value = data.account
      }
      if (data.ordersHistory) {
        ordersHistory.value = data.ordersHistory
      }
      if (data.riskRules) {
        riskRules.value = data.riskRules
      }

      // 持久化所有数据
      persistToStorage()
    } catch (err: any) {
      error.value = err.message || '导入交易数据失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  // ========== 持久化操作 ==========

  /**
   * 持久化交易配置
   */
  const persistTradingConfig = () => {
    try {
      localStorage.setItem(STORAGE_KEYS.TRADING_CONFIG, JSON.stringify(tradingConfig.value))
    } catch (e) {
      console.error('[TradingStore] 保存交易配置失败:', e)
    }
  }

  /**
   * 持久化订单
   */
  const persistOrders = () => {
    try {
      localStorage.setItem(STORAGE_KEYS.ORDERS, JSON.stringify(orders.value))
    } catch (e) {
      console.error('[TradingStore] 保存订单失败:', e)
    }
  }

  /**
   * 持久化持仓
   */
  const persistPositions = () => {
    try {
      localStorage.setItem(STORAGE_KEYS.POSITIONS, JSON.stringify(positions.value))
    } catch (e) {
      console.error('[TradingStore] 保存持仓失败:', e)
    }
  }

  /**
   * 持久化交易历史
   */
  const persistTrades = () => {
    try {
      localStorage.setItem(STORAGE_KEYS.TRADES, JSON.stringify(trades.value))
    } catch (e) {
      console.error('[TradingStore] 保存交易历史失败:', e)
    }
  }

  /**
   * 持久化账户
   */
  const persistAccount = () => {
    try {
      localStorage.setItem(STORAGE_KEYS.ACCOUNT, JSON.stringify(account.value))
    } catch (e) {
      console.error('[TradingStore] 保存账户信息失败:', e)
    }
  }

  /**
   * 持久化历史订单
   */
  const persistOrdersHistory = () => {
    try {
      localStorage.setItem(STORAGE_KEYS.ORDERS_HISTORY, JSON.stringify(ordersHistory.value))
    } catch (e) {
      console.error('[TradingStore] 保存历史订单失败:', e)
    }
  }

  /**
   * 持久化风险规则
   */
  const persistRiskRules = () => {
    try {
      localStorage.setItem(STORAGE_KEYS.RISK_RULES, JSON.stringify(riskRules.value))
    } catch (e) {
      console.error('[TradingStore] 保存风险规则失败:', e)
    }
  }

  /**
   * 持久化所有数据
   */
  const persistToStorage = () => {
    persistTradingConfig()
    persistOrders()
    persistPositions()
    persistTrades()
    persistAccount()
    persistOrdersHistory()
    persistRiskRules()
  }

  /**
   * 从localStorage恢复数据
   */
  const restoreFromStorage = () => {
    try {
      // 恢复交易配置
      const savedConfig = localStorage.getItem(STORAGE_KEYS.TRADING_CONFIG)
      if (savedConfig) {
        tradingConfig.value = JSON.parse(savedConfig)
      }

      // 恢复订单
      const savedOrders = localStorage.getItem(STORAGE_KEYS.ORDERS)
      if (savedOrders) {
        orders.value = JSON.parse(savedOrders)
      }

      // 恢复持仓
      const savedPositions = localStorage.getItem(STORAGE_KEYS.POSITIONS)
      if (savedPositions) {
        positions.value = JSON.parse(savedPositions)
      }

      // 恢复交易历史
      const savedTrades = localStorage.getItem(STORAGE_KEYS.TRADES)
      if (savedTrades) {
        trades.value = JSON.parse(savedTrades)
      }

      // 恢复账户
      const savedAccount = localStorage.getItem(STORAGE_KEYS.ACCOUNT)
      if (savedAccount) {
        account.value = JSON.parse(savedAccount)
      }

      // 恢复历史订单
      const savedOrdersHistory = localStorage.getItem(STORAGE_KEYS.ORDERS_HISTORY)
      if (savedOrdersHistory) {
        ordersHistory.value = JSON.parse(savedOrdersHistory)
      }

      // 恢复风险规则
      const savedRiskRules = localStorage.getItem(STORAGE_KEYS.RISK_RULES)
      if (savedRiskRules) {
        riskRules.value = JSON.parse(savedRiskRules)
      }

      console.log('[TradingStore] 数据已从localStorage恢复', {
        orders: orders.value.length,
        positions: positions.value.length,
        trades: trades.value.length,
        riskRules: riskRules.value.length
      })
    } catch (e) {
      console.error('[TradingStore] 从localStorage恢复失败:', e)
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
    tradingConfig.value = { ...DEFAULT_TRADING_CONFIG }
    orders.value = []
    positions.value = []
    trades.value = []
    account.value = { ...DEFAULT_ACCOUNT }
    ordersHistory.value = []
    riskRules.value = []
    error.value = null
  }

  /**
   * 清除所有数据（包括localStorage）
   */
  const clearAllData = () => {
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
   * 转换为CSV格式
   */
  const convertToCSV = (data: any): string => {
    // 简化版本，只导出交易记录
    if (data.trades && data.trades.length > 0) {
      const headers = ['ID', '标的', '类型', '价格', '数量', '时间', '盈亏']
      const rows = data.trades.map((trade: Trade) => [
        trade.id,
        trade.symbol,
        trade.type,
        trade.price.toFixed(2),
        trade.quantity,
        trade.time,
        trade.profitLoss?.toFixed(2) || ''
      ])

      return [headers.join(','), ...rows.map(row => row.join(','))].join('\n')
    }

    return JSON.stringify(data, null, 2)
  }

  // ========== 监听变化 ==========

  // 自动持久化交易配置
  watch(tradingConfig, () => {
    persistTradingConfig()
  }, { deep: true })

  // 自动持久化订单
  watch(orders, () => {
    persistOrders()
  }, { deep: true })

  // 自动持久化持仓
  watch(positions, () => {
    persistPositions()
  }, { deep: true })

  // 自动持久化交易历史
  watch(trades, () => {
    persistTrades()
  }, { deep: true })

  // 自动持久化账户
  watch(account, () => {
    persistAccount()
  }, { deep: true })

  // 自动持久化风险规则
  watch(riskRules, () => {
    persistRiskRules()
  }, { deep: true })

  return {
    // ========== 状态 ==========
    tradingConfig,
    orders,
    positions,
    trades,
    account,
    ordersHistory,
    riskRules,
    loading,
    error,

    // ========== 计算属性 ==========
    totalPositions,
    totalOrders,
    pendingOrders,
    positionStats,
    todayProfitLoss,
    accountSummary,
    activeRiskRules,
    todayOrderCount,
    filledOrderCount,

    // ========== 交易配置操作 ==========
    setTradingConfig,
    resetTradingConfig,

    // ========== 订单操作 ==========
    placeOrder,
    cancelOrder,
    updateOrderStatus,
    simulateOrderFill,

    // ========== 持仓操作 ==========
    updatePositionsAfterOrder,
    updatePositions,
    clearAllPositions,

    // ========== 交易历史操作 ==========
    addTrade,
    getTradeHistory,
    clearTradeHistory,

    // ========== 账户操作 ==========
    updateAccount,
    resetAccount,
    deposit,
    withdraw,

    // ========== 风险规则操作 ==========
    addRiskRule,
    updateRiskRule,
    removeRiskRule,
    checkRiskRules,
    clearRiskRules,

    // ========== 导出操作 ==========
    exportTradingData,
    importTradingData,

    // ========== 持久化操作 ==========
    persistToStorage,
    restoreFromStorage,
    clearError,
    resetState,
    clearAllData,

    // ========== 初始化 ==========
    initializeStore
  }
})

/**
 * MyQuant v10.0.0 - Data Store (Merged)
 * 统一数据管理 Store - 合并 data.ts + market.ts + sector.ts
 *
 * 功能模块:
 * - 股票基础数据管理 (原 data.ts)
 * - 行情数据与K线管理 (原 market.ts)
 * - 板块数据与轮动管理 (原 sector.ts)
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Quote, KlineData, MarketOverview } from '@/types/market'

// ========== 类型定义 ==========

/**
 * 股票基础数据
 */
export interface StockData {
  code: string
  name: string
  market: 'SZ' | 'SH'
  currentPrice: number
  changePercent: number
  volume: number
  marketCap: number
  pe: number
  pb: number
  lastUpdate: string
}

/**
 * 指标数据
 */
export interface IndicatorData {
  code: string
  name: string
  values: Record<string, number>
  timestamp: string
}

/**
 * 实时数据
 */
export interface RealtimeData {
  code: string
  name: string
  price: number
  change: number
  changePercent: number
  volume: number
  timestamp: string
}

/**
 * 数据质量指标
 */
export interface DataQualityMetrics {
  completeness: number  // 完整性 0-100
  accuracy: number      // 准确性 0-100
  timeliness: number    // 及时性 0-100
  consistency: number   // 一致性 0-100
}

/**
 * 数据源状态
 */
export interface DataSource {
  id: string
  name: string
  status: 'connected' | 'disconnected' | 'error'
  lastUpdate: string | null
}

/**
 * 行情状态
 */
export interface QuoteState {
  [symbol: string]: Quote
}

/**
 * 自选股项
 */
export interface WatchlistItem {
  symbol: string
  name: string
  addedAt: number
}

/**
 * 自选股分组
 */
export interface WatchlistGroup {
  id: string
  name: string
  stocks: WatchlistItem[]
  createdAt: number
  refreshInterval: number  // 刷新间隔（毫秒）
  preheat?: boolean       // 是否预加载（程序启动时自动加载）
}

/**
 * 监控规则条件
 */
export interface MonitorCondition {
  type: string  // 'price' | 'change_percent' | 'volume' | 'macd' | 'kdj' | 'rsi' | 'custom'
  operator: '>' | '<' | '>=' | '<=' | '==' | 'cross_up' | 'cross_down'
  value: number
  params?: Record<string, any>  // 额外参数（如周期、指标参数等）
}

/**
 * 监控规则
 */
export interface MonitorRule {
  id: string
  name: string
  description: string
  enabled: boolean
  targetGroupId: string  // 触发后添加到的分组ID
  conditions: MonitorCondition[]
  symbols?: string[]  // 可选：监控指定股票列表，空则监控全市场
  createdAt: number
  lastTriggered?: number
  triggerCount: number
}

/**
 * 板块数据
 */
export interface Sector {
  code: string
  name: string
  stocks: string[]
  strength: number
  rank: number
  change_percent: number
  amount?: number
}

/**
 * 板块历史数据
 */
export interface SectorHistory {
  date: string
  strength: number
  rank: number
  change_percent: number
}

/**
 * 板块轮动数据
 */
export interface SectorRotation {
  hot_sectors: string[]
  cold_sectors: string[]
  rotation_score: number
}

// ========== Store 定义 ==========

export const useDataStore = defineStore('data', () => {
  // ==================== 状态定义 ====================

  // 股票基础数据
  const stocks = ref<StockData[]>([])
  const indicators = ref<IndicatorData[]>([])

  // 实时数据
  const realtimeData = ref<RealtimeData[]>([])

  // 数据质量与源
  const dataQuality = ref<DataQualityMetrics>({
    completeness: 0,
    accuracy: 0,
    timeliness: 0,
    consistency: 0
  })
  const dataSources = ref<DataSource[]>([
    { id: 'qmt', name: 'QMT', status: 'connected', lastUpdate: new Date().toISOString() },
    { id: 'mootdx', name: 'MooTDX', status: 'connected', lastUpdate: new Date().toISOString() },
    { id: 'tushare', name: 'TuShare', status: 'connected', lastUpdate: new Date().toISOString() }
  ])

  // 行情数据
  const quotes = ref<QuoteState>({})
  const klineData = ref<Map<string, KlineData[]>>(new Map())
  const watchlist = ref<WatchlistItem[]>([])
  // 自选股分组
  const watchlistGroups = ref<WatchlistGroup[]>([])
  const activeGroupId = ref<string>('')
  // 监控规则
  const monitorRules = ref<MonitorRule[]>([])
  const marketOverview = ref<MarketOverview | null>(null)
  const lastUpdate = ref<number>(0)

  // 板块数据
  const sectors = ref<Sector[]>([])
  const sectorHistory = ref<Map<string, SectorHistory[]>>(new Map())
  const rotation = ref<SectorRotation | null>(null)
  const selectedSector = ref<Sector | null>(null)
  const sortBy = ref<'strength' | 'change' | 'amount'>('strength')
  const sortOrder = ref<'asc' | 'desc'>('desc')

  // ==================== 计算属性 - 基础数据 ====================

  /**
   * 股票总数
   */
  const stockCount = computed(() => stocks.value.length)

  /**
   * 已连接的数据源
   */
  const connectedDataSources = computed(() =>
    dataSources.value.filter(ds => ds.status === 'connected')
  )

  /**
   * 是否有实时数据
   */
  const hasRealtimeData = computed(() => realtimeData.value.length > 0)

  // ==================== 计算属性 - 行情数据 ====================

  /**
   * 获取单个行情
   */
  const getQuote = (symbol: string) => {
    return computed(() => quotes.value[symbol])
  }

  /**
   * 获取所有行情列表
   */
  const quoteList = computed(() => {
    return Object.values(quotes.value)
  })

  /**
   * 涨幅榜 (前50)
   */
  const topGainers = computed(() => {
    return quoteList.value
      .filter(q => q.change_percent > 0)
      .sort((a, b) => b.change_percent - a.change_percent)
      .slice(0, 50)
  })

  /**
   * 跌幅榜 (前50)
   */
  const topLosers = computed(() => {
    return quoteList.value
      .filter(q => q.change_percent < 0)
      .sort((a, b) => a.change_percent - b.change_percent)
      .slice(0, 50)
  })

  /**
   * 成交额榜 (前50)
   */
  const topByAmount = computed(() => {
    return quoteList.value
      .sort((a, b) => (b.amount || 0) - (a.amount || 0))
      .slice(0, 50)
  })

  /**
   * 市场涨跌统计
   */
  const marketStats = computed(() => {
    const list = quoteList.value
    const up = list.filter(q => q.change_percent > 0).length
    const down = list.filter(q => q.change_percent < 0).length
    const flat = list.filter(q => q.change_percent === 0).length
    const limitUp = list.filter(q => q.change_percent >= 9.9).length
    const limitDown = list.filter(q => q.change_percent <= -9.9).length

    return {
      total: list.length,
      up,
      down,
      flat,
      limitUp,
      limitDown,
      upPercent: list.length > 0 ? ((up / list.length) * 100).toFixed(1) : '0'
    }
  })

  /**
   * 自选股行情
   */
  const watchlistQuotes = computed(() => {
    return watchlist.value
      .map(item => quotes.value[item.symbol])
      .filter(q => q !== undefined)
  })

  /**
   * 最后更新时间文本
   */
  const lastUpdateText = computed(() => {
    if (!lastUpdate.value) return '--'
    return new Date(lastUpdate.value).toLocaleTimeString()
  })

  // ==================== 计算属性 - 板块数据 ====================

  /**
   * 排序后的板块列表
   */
  const sortedSectors = computed(() => {
    const list = [...sectors.value]
    list.sort((a, b) => {
      let comparison = 0
      switch (sortBy.value) {
        case 'strength':
          comparison = a.strength - b.strength
          break
        case 'change':
          comparison = a.change_percent - b.change_percent
          break
        case 'amount':
          comparison = (a.amount || 0) - (b.amount || 0)
          break
      }
      return sortOrder.value === 'asc' ? comparison : -comparison
    })
    return list
  })

  /**
   * 热门板块 (前10)
   */
  const hotSectors = computed(() => {
    return sortedSectors.value
      .filter(s => s.change_percent > 0)
      .slice(0, 10)
  })

  /**
   * 冷门板块 (后10)
   */
  const coldSectors = computed(() => {
    return sortedSectors.value
      .filter(s => s.change_percent < 0)
      .slice(-10)
      .reverse()
  })

  /**
   * 获取单个板块
   */
  const getSector = (code: string) => {
    return computed(() => sectors.value.find(s => s.code === code))
  }

  /**
   * 获取板块历史
   */
  const getSectorHistory = (code: string) => {
    return computed(() => sectorHistory.value.get(code) || [])
  }

  /**
   * 获取板块成分股
   */
  const getSectorStocks = (code: string) => {
    return computed(() => {
      const sector = sectors.value.find(s => s.code === code)
      return sector?.stocks || []
    })
  }

  /**
   * 板块统计
   */
  const sectorStats = computed(() => {
    const total = sectors.value.length
    const up = sectors.value.filter(s => s.change_percent > 0).length
    const down = sectors.value.filter(s => s.change_percent < 0).length
    const flat = sectors.value.filter(s => s.change_percent === 0).length

    return {
      total,
      up,
      down,
      flat,
      upPercent: total > 0 ? ((up / total) * 100).toFixed(1) : '0'
    }
  })

  // ==================== Actions - 股票基础数据 ====================

  /**
   * 设置股票列表
   */
  const setStocks = (newStocks: StockData[]) => {
    stocks.value = newStocks
    saveToLocalStorage('stocks', newStocks)
  }

  /**
   * 添加单个股票
   */
  const addStock = (stock: StockData) => {
    const existingIndex = stocks.value.findIndex(s => s.code === stock.code)
    if (existingIndex > -1) {
      stocks.value[existingIndex] = stock
    } else {
      stocks.value.push(stock)
    }
    saveToLocalStorage('stocks', stocks.value)
  }

  /**
   * 更新股票价格
   */
  const updateStockPrice = (code: string, price: number) => {
    const stock = stocks.value.find(s => s.code === code)
    if (stock) {
      stock.currentPrice = price
      stock.lastUpdate = new Date().toISOString()
      saveToLocalStorage('stocks', stocks.value)
    }
  }

  /**
   * 设置指标数据
   */
  const setIndicators = (newIndicators: IndicatorData[]) => {
    indicators.value = newIndicators
  }

  /**
   * 添加指标数据
   */
  const addIndicator = (indicator: IndicatorData) => {
    indicators.value.push(indicator)
  }

  /**
   * 更新实时数据
   */
  const updateRealtimeData = (data: RealtimeData[]) => {
    realtimeData.value = data
  }

  /**
   * 添加实时数据
   */
  const setRealtimeData = (data: RealtimeData[]) => {
    realtimeData.value = data
  }

  /**
   * 添加单条实时数据
   */
  const addRealtimeData = (data: RealtimeData) => {
    const existingIndex = realtimeData.value.findIndex(d => d.code === data.code)
    if (existingIndex > -1) {
      realtimeData.value[existingIndex] = data
    } else {
      realtimeData.value.push(data)
    }
  }

  /**
   * 更新数据质量
   */
  const updateDataQuality = (metrics: Partial<DataQualityMetrics>) => {
    dataQuality.value = { ...dataQuality.value, ...metrics }
  }

  /**
   * 更新数据源状态
   */
  const updateDataSourceStatus = (id: string, status: DataSource['status']) => {
    const source = dataSources.value.find(ds => ds.id === id)
    if (source) {
      source.status = status
      source.lastUpdate = status === 'connected' ? new Date().toISOString() : null
      saveToLocalStorage('dataSources', dataSources.value)
    }
  }

  /**
   * 清空实时数据
   */
  const clearRealtimeData = () => {
    realtimeData.value = []
  }

  // ==================== Actions - 行情数据 ====================

  /**
   * 更新行情数据
   */
  const updateQuotes = (newQuotes: Quote[]) => {
    for (const quote of newQuotes) {
      quotes.value[quote.symbol] = quote
    }
    lastUpdate.value = Date.now()
  }

  /**
   * 更新单个行情
   */
  const updateQuote = (quote: Quote) => {
    quotes.value[quote.symbol] = quote
    lastUpdate.value = Date.now()
  }

  /**
   * 批量更新行情
   */
  const batchUpdateQuotes = (updates: Partial<Quote>[]) => {
    for (const update of updates) {
      if (update.symbol && quotes.value[update.symbol]) {
        quotes.value[update.symbol] = {
          ...quotes.value[update.symbol],
          ...update
        }
      }
    }
    lastUpdate.value = Date.now()
  }

  /**
   * 设置K线数据
   */
  const setKlineData = (symbol: string, data: KlineData[]) => {
    klineData.value.set(symbol, data)
  }

  /**
   * 获取K线数据
   */
  const getKlineData = (symbol: string) => {
    return computed(() => klineData.value.get(symbol))
  }

  /**
   * 更新市场概览
   */
  const setMarketOverview = (overview: MarketOverview) => {
    marketOverview.value = overview
  }

  /**
   * 添加到自选股
   */
  const addToWatchlist = (symbol: string, name: string) => {
    if (!watchlist.value.find(item => item.symbol === symbol)) {
      watchlist.value.push({
        symbol,
        name,
        addedAt: Date.now()
      })
      saveWatchlist()
    }
  }

  /**
   * 从自选股移除
   */
  const removeFromWatchlist = (symbol: string) => {
    const index = watchlist.value.findIndex(item => item.symbol === symbol)
    if (index > -1) {
      watchlist.value.splice(index, 1)
      saveWatchlist()
    }
  }

  /**
   * 检查是否在自选中
   */
  const isInWatchlist = (symbol: string) => {
    return watchlist.value.some(item => item.symbol === symbol)
  }

  /**
   * 切换自选状态
   */
  const toggleWatchlist = (symbol: string, name: string) => {
    if (isInWatchlist(symbol)) {
      removeFromWatchlist(symbol)
      return false
    } else {
      addToWatchlist(symbol, name)
      return true
    }
  }

  // ==================== Actions - 分组管理 ====================

  /**
   * 获取当前激活分组
   */
  const activeGroup = computed(() => {
    return watchlistGroups.value.find(g => g.id === activeGroupId.value) || watchlistGroups.value[0] || null
  })

  /**
   * 获取当前激活分组的股票列表
   */
  const currentWatchlist = computed(() => {
    const group = activeGroup.value
    if (group) {
      return group.stocks
    }
    // 如果没有分组，返回旧的 watchlist（向后兼容）
    return watchlist.value
  })

  /**
   * 创建新分组
   */
  const createGroup = (name: string, refreshInterval: number = 5000) => {
    const newGroup: WatchlistGroup = {
      id: `group_${Date.now()}`,
      name,
      stocks: [],
      createdAt: Date.now(),
      refreshInterval  // 默认5秒
    }
    watchlistGroups.value.push(newGroup)
    saveWatchlistGroups()
    return newGroup
  }

  /**
   * 重命名分组
   */
  const renameGroup = (groupId: string, newName: string) => {
    const group = watchlistGroups.value.find(g => g.id === groupId)
    if (group) {
      group.name = newName
      saveWatchlistGroups()
    }
  }

  /**
   * 删除分组
   */
  const deleteGroup = (groupId: string) => {
    const index = watchlistGroups.value.findIndex(g => g.id === groupId)
    if (index > -1) {
      // 如果删除的是当前激活分组，切换到第一个分组
      if (activeGroupId.value === groupId) {
        activeGroupId.value = watchlistGroups.value.length > 1
          ? watchlistGroups.value[0].id
          : ''
      }
      watchlistGroups.value.splice(index, 1)
      saveWatchlistGroups()
    }
  }

  /**
   * 切换激活分组
   */
  const setActiveGroup = (groupId: string) => {
    const group = watchlistGroups.value.find(g => g.id === groupId)
    if (group) {
      activeGroupId.value = groupId
      saveActiveGroup()
    }
  }

  /**
   * 添加股票到指定分组
   */
  const addToGroup = (groupId: string, symbol: string, name: string) => {
    const group = watchlistGroups.value.find(g => g.id === groupId)
    if (group && !group.stocks.find(s => s.symbol === symbol)) {
      group.stocks.push({
        symbol,
        name,
        addedAt: Date.now()
      })
      saveWatchlistGroups()
    }
  }

  /**
   * 从分组移除股票（同时清理热数据）
   */
  const removeFromGroup = (groupId: string, symbol: string) => {
    const group = watchlistGroups.value.find(g => g.id === groupId)
    if (group) {
      const index = group.stocks.findIndex(s => s.symbol === symbol)
      if (index > -1) {
        group.stocks.splice(index, 1)

        // 检查该股票是否还在其他分组中
        const inOtherGroups = watchlistGroups.value.some(g =>
          g.id !== groupId && g.stocks.some(s => s.symbol === symbol)
        )

        // 如果不在任何其他分组，清理热数据
        if (!inOtherGroups) {
          delete quotes.value[symbol]
          console.log(`[DataStore] 清理股票 ${symbol} 的热数据`)
        }

        saveWatchlistGroups()
      }
    }
  }

  /**
   * 设置分组刷新间隔
   */
  const setGroupRefreshInterval = (groupId: string, interval: number) => {
    const group = watchlistGroups.value.find(g => g.id === groupId)
    if (group) {
      group.refreshInterval = interval
      saveWatchlistGroups()
      console.log(`[DataStore] 分组 ${group.name} 刷新间隔设置为 ${interval}ms`)
    }
  }

  /**
   * 设置分组预热状态
   */
  const setGroupPreheat = (groupId: string, preheat: boolean) => {
    const group = watchlistGroups.value.find(g => g.id === groupId)
    if (group) {
      group.preheat = preheat
      saveWatchlistGroups()
      console.log(`[DataStore] 分组 ${group.name} 预热${preheat ? '已启用' : '已禁用'}`)
    }
  }

  /**
   * 获取需要预热的分组
   */
  const getPreheatGroups = () => {
    return watchlistGroups.value.filter(g => g.preheat && g.stocks.length > 0)
  }

  /**
   * 预热数据（加载所有标记为预热的分组数据）
   */
  const preheatData = async (fetchCallback?: (symbols: string[]) => Promise<void>) => {
    const preheatGroups = getPreheatGroups()
    if (preheatGroups.length === 0) {
      console.log('[DataStore] 没有需要预热的分组')
      return
    }

    console.log(`[DataStore] 开始预热 ${preheatGroups.length} 个分组的数据...`)

    for (const group of preheatGroups) {
      const symbols = group.stocks.map(s => s.symbol)
      console.log(`[DataStore] 预热分组: ${group.name} (${symbols.length} 只股票)`)

      if (fetchCallback) {
        try {
          await fetchCallback(symbols)
        } catch (error) {
          console.error(`[DataStore] 预热分组 ${group.name} 失败:`, error)
        }
      }
    }

    console.log('[DataStore] 数据预热完成')
  }

  // ==================== Actions - 监控规则 ====================

  /**
   * 创建监控规则
   */
  const createMonitorRule = (rule: Omit<MonitorRule, 'id' | 'createdAt' | 'triggerCount'>): MonitorRule => {
    const newRule: MonitorRule = {
      id: `rule_${Date.now()}`,
      ...rule,
      createdAt: Date.now(),
      triggerCount: 0
    }
    monitorRules.value.push(newRule)
    saveMonitorRules()
    return newRule
  }

  /**
   * 更新监控规则
   */
  const updateMonitorRule = (ruleId: string, updates: Partial<MonitorRule>) => {
    const rule = monitorRules.value.find(r => r.id === ruleId)
    if (rule) {
      Object.assign(rule, updates)
      saveMonitorRules()
    }
  }

  /**
   * 删除监控规则
   */
  const deleteMonitorRule = (ruleId: string) => {
    const index = monitorRules.value.findIndex(r => r.id === ruleId)
    if (index > -1) {
      monitorRules.value.splice(index, 1)
      saveMonitorRules()
    }
  }

  /**
   * 启用/禁用监控规则
   */
  const toggleMonitorRule = (ruleId: string) => {
    const rule = monitorRules.value.find(r => r.id === ruleId)
    if (rule) {
      rule.enabled = !rule.enabled
      saveMonitorRules()
    }
  }

  /**
   * 执行监控规则检查（预留接口）
   * TODO: 实现具体的监控逻辑
   */
  const executeMonitorRules = async (): Promise<void> => {
    const enabledRules = monitorRules.value.filter(r => r.enabled)

    for (const rule of enabledRules) {
      try {
        // TODO: 根据规则条件检查股票
        // 1. 获取待监控股票列表（rule.symbols 或全市场）
        // 2. 检查每个股票是否满足 rule.conditions
        // 3. 满足条件则添加到 rule.targetGroupId
        // 4. 更新 rule.lastTriggered 和 rule.triggerCount

        console.log(`[Monitor] 检查规则: ${rule.name}`)
        // 预留接口，以后实现
      } catch (error) {
        console.error(`[Monitor] 规则 ${rule.name} 执行失败:`, error)
      }
    }
  }

  /**
   * 保存监控规则到本地存储
   */
  const saveMonitorRules = () => {
    try {
      localStorage.setItem('myquant_monitor_rules', JSON.stringify(monitorRules.value))
    } catch (e) {
      console.error('保存监控规则失败:', e)
    }
  }

  /**
   * 从本地存储加载监控规则
   */
  const loadMonitorRules = () => {
    try {
      const saved = localStorage.getItem('myquant_monitor_rules')
      if (saved) {
        monitorRules.value = JSON.parse(saved)
      }
    } catch (e) {
      console.error('加载监控规则失败:', e)
    }
  }

  /**
   * 清空行情数据
   */
  const clearQuotes = () => {
    quotes.value = {}
  }

  /**
   * 清空K线数据
   */
  const clearKlineData = () => {
    klineData.value.clear()
  }

  /**
   * 根据涨跌幅筛选
   */
  const filterByChange = (min: number, max: number) => {
    return quoteList.value.filter(q => {
      const change = q.change_percent || 0
      return change >= min && change <= max
    })
  }

  /**
   * 搜索股票
   */
  const searchStocks = (keyword: string) => {
    const lowerKeyword = keyword.toLowerCase()
    return quoteList.value.filter(q => {
      return (
        q.symbol.toLowerCase().includes(lowerKeyword) ||
        (q.name && q.name.toLowerCase().includes(lowerKeyword)) ||
        (q.pinyin && q.pinyin.toLowerCase().includes(lowerKeyword))
      )
    })
  }

  // ==================== Actions - 板块数据 ====================

  /**
   * 设置板块列表
   */
  const setSectors = (newSectors: Sector[]) => {
    sectors.value = newSectors
  }

  /**
   * 更新板块数据
   */
  const updateSector = (sector: Sector) => {
    const index = sectors.value.findIndex(s => s.code === sector.code)
    if (index > -1) {
      sectors.value[index] = sector
    } else {
      sectors.value.push(sector)
    }
  }

  /**
   * 批量更新板块
   */
  const batchUpdateSectors = (updates: Partial<Sector>[]) => {
    for (const update of updates) {
      if (update.code) {
        const index = sectors.value.findIndex(s => s.code === update.code)
        if (index > -1) {
          sectors.value[index] = {
            ...sectors.value[index],
            ...update
          }
        }
      }
    }
  }

  /**
   * 设置板块历史
   */
  const setSectorHistory = (code: string, history: SectorHistory[]) => {
    sectorHistory.value.set(code, history)
  }

  /**
   * 添加板块历史记录
   */
  const addSectorHistory = (code: string, record: SectorHistory) => {
    if (!sectorHistory.value.has(code)) {
      sectorHistory.value.set(code, [])
    }
    const history = sectorHistory.value.get(code)!
    history.push(record)

    // 限制历史记录数量（最多保留100条）
    if (history.length > 100) {
      history.shift()
    }
  }

  /**
   * 设置轮动数据
   */
  const setRotation = (data: SectorRotation) => {
    rotation.value = data
  }

  /**
   * 选择板块
   */
  const selectSector = (code: string) => {
    selectedSector.value = sectors.value.find(s => s.code === code) || null
  }

  /**
   * 取消选择板块
   */
  const deselectSector = () => {
    selectedSector.value = null
  }

  /**
   * 设置排序
   */
  const setSort = (by: typeof sortBy.value, order: typeof sortOrder.value) => {
    sortBy.value = by
    sortOrder.value = order
  }

  /**
   * 切换排序字段
   */
  const toggleSort = (by: typeof sortBy.value) => {
    if (sortBy.value === by) {
      sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
    } else {
      sortBy.value = by
      sortOrder.value = 'desc'
    }
  }

  /**
   * 搜索板块
   */
  const searchSectors = (keyword: string) => {
    const lowerKeyword = keyword.toLowerCase()
    return sectors.value.filter(s => {
      return (
        s.code.toLowerCase().includes(lowerKeyword) ||
        s.name.toLowerCase().includes(lowerKeyword)
      )
    })
  }

  /**
   * 获取板块趋势（基于历史数据）
   */
  const getSectorTrend = (code: string) => {
    const history = sectorHistory.value.get(code)
    if (!history || history.length < 2) {
      return 'unknown'
    }

    const recent = history.slice(-5)
    const upCount = recent.filter(h => h.change_percent > 0).length
    const downCount = recent.filter(h => h.change_percent < 0).length

    if (upCount >= 4) return 'strong_up'
    if (upCount >= 3) return 'up'
    if (downCount >= 4) return 'strong_down'
    if (downCount >= 3) return 'down'
    return 'flat'
  }

  /**
   * 获取板块强度变化
   */
  const getStrengthChange = (code: string) => {
    const history = sectorHistory.value.get(code)
    if (!history || history.length < 2) {
      return 0
    }

    const latest = history[history.length - 1]
    const previous = history[history.length - 2]
    return latest.strength - previous.strength
  }

  /**
   * 清空板块数据
   */
  const clearSectors = () => {
    sectors.value = []
  }

  /**
   * 清空历史数据
   */
  const clearHistory = () => {
    sectorHistory.value.clear()
  }

  // ==================== Actions - 数据获取与订阅 ====================

  /**
   * 获取股票数据 (模拟API调用)
   */
  const fetchStockData = async (codes: string[]) => {
    try {
      console.log('Fetching stock data for:', codes)
      // 这里将实现实际的数据获取逻辑
    } catch (error) {
      console.error('Failed to fetch stock data:', error)
    }
  }

  /**
   * 获取指标数据 (模拟API调用)
   */
  const fetchIndicators = async (code: string, indicators: string[]) => {
    try {
      console.log('Fetching indicators for:', code, indicators)
      // 这里将实现实际的数据获取逻辑
    } catch (error) {
      console.error('Failed to fetch indicators:', error)
    }
  }

  /**
   * 订阅实时数据 (模拟WebSocket连接)
   */
  const subscribeRealtimeData = (codes: string[]) => {
    try {
      console.log('Subscribing to realtime data for:', codes)
      // 这里将实现实际的WebSocket订阅逻辑
    } catch (error) {
      console.error('Failed to subscribe realtime data:', error)
    }
  }

  /**
   * 取消订阅实时数据 (模拟WebSocket断开)
   */
  const unsubscribeRealtimeData = (codes: string[]) => {
    try {
      console.log('Unsubscribing from realtime data for:', codes)
      // 这里将实现实际的WebSocket取消订阅逻辑
    } catch (error) {
      console.error('Failed to unsubscribe realtime data:', error)
    }
  }

  // ==================== 本地存储辅助函数 ====================

  /**
   * 保存数据到本地存储
   */
  const saveToLocalStorage = (key: string, data: any) => {
    try {
      localStorage.setItem(`myquant_${key}`, JSON.stringify(data))
    } catch (e) {
      console.error(`Failed to save ${key} to localStorage:`, e)
    }
  }

  /**
   * 从本地存储加载数据
   */
  const loadFromLocalStorage = (key: string) => {
    try {
      const saved = localStorage.getItem(`myquant_${key}`)
      if (saved) {
        return JSON.parse(saved)
      }
    } catch (e) {
      console.error(`Failed to load ${key} from localStorage:`, e)
    }
    return null
  }

  /**
   * 保存自选列表到本地存储
   */
  const saveWatchlist = () => {
    try {
      localStorage.setItem('myquant_watchlist', JSON.stringify(watchlist.value))
    } catch (e) {
      console.error('保存自选列表失败:', e)
    }
  }

  /**
   * 从本地存储加载自选列表
   */
  const loadWatchlist = () => {
    try {
      const saved = localStorage.getItem('myquant_watchlist')
      if (saved) {
        watchlist.value = JSON.parse(saved)
      }
    } catch (e) {
      console.error('加载自选列表失败:', e)
    }
  }

  /**
   * 保存分组数据到本地存储
   */
  const saveWatchlistGroups = () => {
    try {
      localStorage.setItem('myquant_watchlist_groups', JSON.stringify(watchlistGroups.value))
    } catch (e) {
      console.error('保存分组失败:', e)
    }
  }

  /**
   * 从本地存储加载分组数据
   */
  const loadWatchlistGroups = () => {
    try {
      const saved = localStorage.getItem('myquant_watchlist_groups')
      if (saved) {
        watchlistGroups.value = JSON.parse(saved)
      } else {
        // 如果没有分组数据，创建默认分组并迁移旧数据
        const defaultGroup: WatchlistGroup = {
          id: 'group_default',
          name: '默认分组',
          stocks: [...watchlist.value],
          createdAt: Date.now()
        }
        watchlistGroups.value = [defaultGroup]
        saveWatchlistGroups()
      }
    } catch (e) {
      console.error('加载分组失败:', e)
      // 出错时创建默认分组
      const defaultGroup: WatchlistGroup = {
        id: 'group_default',
        name: '默认分组',
        stocks: [],
        createdAt: Date.now()
      }
      watchlistGroups.value = [defaultGroup]
    }
  }

  /**
   * 保存激活分组ID
   */
  const saveActiveGroup = () => {
    try {
      localStorage.setItem('myquant_active_group', activeGroupId.value)
    } catch (e) {
      console.error('保存激活分组失败:', e)
    }
  }

  /**
   * 加载激活分组ID
   */
  const loadActiveGroup = () => {
    try {
      const saved = localStorage.getItem('myquant_active_group')
      if (saved) {
        activeGroupId.value = saved
      } else if (watchlistGroups.value.length > 0) {
        // 默认激活第一个分组
        activeGroupId.value = watchlistGroups.value[0].id
        saveActiveGroup()
      }
    } catch (e) {
      console.error('加载激活分组失败:', e)
      if (watchlistGroups.value.length > 0) {
        activeGroupId.value = watchlistGroups.value[0].id
      }
    }
  }

  // ==================== 初始化 ====================

  /**
   * 初始化数据
   */
  const initializeData = () => {
    // 加载股票数据
    const savedStocks = loadFromLocalStorage('stocks')
    if (savedStocks) {
      stocks.value = savedStocks
    }

    // 加载数据源配置
    const savedDataSources = loadFromLocalStorage('dataSources')
    if (savedDataSources) {
      dataSources.value = savedDataSources
    }

    // 加载自选列表（旧数据，用于迁移）
    loadWatchlist()

    // 加载分组数据（新数据结构）
    loadWatchlistGroups()

    // 加载激活分组
    loadActiveGroup()

    // 加载监控规则
    loadMonitorRules()
  }

  /**
   * 重置所有状态
   */
  const reset = () => {
    stocks.value = []
    indicators.value = []
    realtimeData.value = []
    quotes.value = {}
    klineData.value.clear()
    watchlist.value = []
    marketOverview.value = null
    sectors.value = []
    sectorHistory.value.clear()
    rotation.value = null
    selectedSector.value = null
    sortBy.value = 'strength'
    sortOrder.value = 'desc'
    lastUpdate.value = 0
  }

  // 初始化时加载数据
  initializeData()

  // ==================== 导出 ====================

  return {
    // ========== 状态 ==========
    // 股票基础数据
    stocks,
    indicators,
    realtimeData,
    dataQuality,
    dataSources,

    // 行情数据
    quotes,
    klineData,
    watchlist,
    watchlistGroups,
    activeGroupId,
    monitorRules,
    marketOverview,
    lastUpdate,

    // 板块数据
    sectors,
    sectorHistory,
    rotation,
    selectedSector,
    sortBy,
    sortOrder,

    // ========== 计算属性 - 基础数据 ==========
    stockCount,
    connectedDataSources,
    hasRealtimeData,

    // ========== 计算属性 - 行情数据 ==========
    getQuote,
    quoteList,
    topGainers,
    topLosers,
    topByAmount,
    marketStats,
    watchlistQuotes,
    lastUpdateText,

    // ========== 计算属性 - 分组数据 ==========
    activeGroup,
    currentWatchlist,

    // ========== 计算属性 - 板块数据 ==========
    sortedSectors,
    hotSectors,
    coldSectors,
    getSector,
    getSectorHistory,
    getSectorStocks,
    sectorStats,

    // ========== Actions - 股票基础数据 ==========
    setStocks,
    addStock,
    updateStockPrice,
    setIndicators,
    addIndicator,
    setRealtimeData,
    addRealtimeData,
    updateRealtimeData,
    updateDataQuality,
    updateDataSourceStatus,
    clearRealtimeData,

    // ========== Actions - 行情数据 ==========
    updateQuotes,
    updateQuote,
    batchUpdateQuotes,
    setKlineData,
    getKlineData,
    setMarketOverview,
    addToWatchlist,
    removeFromWatchlist,
    isInWatchlist,
    toggleWatchlist,
    clearQuotes,
    clearKlineData,
    filterByChange,
    searchStocks,

    // ========== Actions - 分组管理 ==========
    createGroup,
    renameGroup,
    deleteGroup,
    setActiveGroup,
    addToGroup,
    removeFromGroup,
    setGroupRefreshInterval,
    setGroupPreheat,
    getPreheatGroups,
    preheatData,

    // ========== Actions - 监控规则 ==========
    createMonitorRule,
    updateMonitorRule,
    deleteMonitorRule,
    toggleMonitorRule,
    executeMonitorRules,

    // ========== Actions - 板块数据 ==========
    setSectors,
    updateSector,
    batchUpdateSectors,
    setSectorHistory,
    addSectorHistory,
    setRotation,
    selectSector,
    deselectSector,
    setSort,
    toggleSort,
    searchSectors,
    getSectorTrend,
    getStrengthChange,
    clearSectors,
    clearHistory,

    // ========== Actions - 数据获取与订阅 ==========
    fetchStockData,
    fetchIndicators,
    subscribeRealtimeData,
    unsubscribeRealtimeData,

    // ========== Actions - 本地存储 ==========
    saveWatchlist,
    loadWatchlist,
    initializeData,
    reset
  }
})

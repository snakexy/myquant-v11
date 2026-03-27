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
import { ref, computed, watch } from 'vue'
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
  const marketOverview = ref<MarketOverview | null>(null)
  const lastUpdate = ref<number>(0)

  // 自选股分组管理
  // 从 localStorage 恢复
  const savedGroups = localStorage.getItem('watchlistGroups')
  const watchlistGroups = ref<any[]>(savedGroups ? JSON.parse(savedGroups) : [
    { id: 'default', name: '默认分组', stocks: [], refreshInterval: 5000, preheat: false }
  ])
  const activeGroupId = ref(savedGroups ? (JSON.parse(savedGroups)[0]?.id || 'default') : 'default')

  // 监听变化并保存
  watch(watchlistGroups, (groups) => {
    try {
      localStorage.setItem('watchlistGroups', JSON.stringify(groups))
      console.log('[DataStore] 已保存 watchlistGroups 到 localStorage:', groups.length, '个分组')
    } catch (e) {
      console.error('[DataStore] 保存 watchlistGroups 失败:', e)
    }
  }, { deep: true })

  // 立即保存一次初始化数据（防止丢失）
  try {
    if (!savedGroups) {
      localStorage.setItem('watchlistGroups', JSON.stringify(watchlistGroups.value))
      console.log('[DataStore] 初始化并保存默认分组')
    }
  } catch (e) {
    console.error('[DataStore] 初始化保存失败:', e)
  }

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

  /**
   * 当前激活的自选分组
   */
  const activeGroup = computed(() => {
    const groups = watchlistGroups.value
    return groups.find(g => g.id === activeGroupId.value) || groups[0] || null
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

  // ==================== 初始化 ====================

  /**
   * 初始化数据
   */
  const initializeData = () => {
    console.log('[DataStore] initializeData 开始执行')

    // 加载股票数据
    const savedStocks = loadFromLocalStorage('stocks')
    if (savedStocks) {
      stocks.value = savedStocks
      console.log('[DataStore] 已加载 stocks:', savedStocks.length)
    }

    // 加载数据源配置
    const savedDataSources = loadFromLocalStorage('dataSources')
    if (savedDataSources) {
      dataSources.value = savedDataSources
      console.log('[DataStore] 已加载 dataSources:', savedDataSources.length)
    }

    // 加载自选列表
    loadWatchlist()

    console.log('[DataStore] initializeData 执行完成')
    console.log('[DataStore] watchlistGroups:', JSON.stringify(watchlistGroups.value, null, 2))
    console.log('[DataStore] activeGroupId:', activeGroupId.value)
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
    marketOverview,
    lastUpdate,

    // 自选股分组
    watchlistGroups,
    activeGroupId,

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

    // ========== 计算属性 - 自选股分组 ==========
    activeGroup,

    // ========== Actions - 自选股分组 ==========
    setActiveGroup: (groupId: string) => {
      activeGroupId.value = groupId
    },
    createGroup: (name: string) => {
      const newGroup = {
        id: `group_${Date.now()}`,
        name,
        stocks: [],
        refreshInterval: 5000,
        preheat: false
      }
      watchlistGroups.value.push(newGroup)
      return newGroup
    },
    deleteGroup: (groupId: string) => {
      const idx = watchlistGroups.value.findIndex(g => g.id === groupId)
      if (idx !== -1) {
        watchlistGroups.value.splice(idx, 1)
        if (activeGroupId.value === groupId) {
          activeGroupId.value = watchlistGroups.value[0]?.id || ''
        }
      }
    },
    renameGroup: (groupId: string, newName: string) => {
      const group = watchlistGroups.value.find(g => g.id === groupId)
      if (group) {
        group.name = newName
      }
    },
    addToGroup: (groupId: string, symbol: string, name: string) => {
      const group = watchlistGroups.value.find(g => g.id === groupId)
      if (group && !group.stocks.find((s: any) => s.symbol === symbol)) {
        group.stocks.push({ symbol, name })
      }
    },
    removeFromGroup: (groupId: string, symbol: string) => {
      const group = watchlistGroups.value.find(g => g.id === groupId)
      if (group) {
        group.stocks = group.stocks.filter((s: any) => s.symbol !== symbol)
      }
    },
    setGroupRefreshInterval: (groupId: string, interval: number) => {
      const group = watchlistGroups.value.find(g => g.id === groupId)
      if (group) {
        group.refreshInterval = interval
      }
    },
    togglePreheat: (groupId: string) => {
      const group = watchlistGroups.value.find(g => g.id === groupId)
      if (group) {
        group.preheat = !group.preheat
      }
    },

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

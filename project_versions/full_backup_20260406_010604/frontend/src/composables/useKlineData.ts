/**
 * useKlineData - K线数据管理 Composable
 *
 * 统一封装：
 * - HTTP 历史数据加载（fetchKline）
 * - WebSocket 实时推送（createKlineWebSocket）
 * - 周期聚合（KlineAggregator）
 *
 * 设计原则：数据逻辑与组件分离，组件只关注展示
 */

import { ref, computed, watch, onMounted, onBeforeUnmount, type Ref } from 'vue'
import { fetchKline, fetchKlineIncremental, type KlineItem } from '@/api/modules/quotes'
import { createKlineWebSocket, type KlineBar, type KlineWebSocketConfig } from '@/services/klineWebSocket'
import { createKlineAggregator, type Timeframe } from '@/services/klineAggregator'
import {
  getKlineData,
  saveKlineData,
  type IDBKlineRecord
} from '@/services/idbKline'

export interface UseKlineDataOptions {
  /** 初始加载条数（默认800） */
  initialCount?: number
  /** 复权类型（默认'qfq'前复权） */
  adjustType?: string
  /** 是否启用WebSocket（默认true） */
  enableWebSocket?: boolean
  /** 是否自动加载（默认true） */
  autoLoad?: boolean
  /** 是否启用增量模式（默认true） */
  enableIncremental?: boolean
  /** 是否启用IndexedDB缓存（默认true） */
  enableIndexedDB?: boolean
}

export interface KlineData {
  time: number
  open: number
  high: number
  low: number
  close: number
  volume: number
}

export interface UseKlineDataReturn {
  // 状态
  /** 聚合后的K线数据（响应式，直接用于图表） */
  bars: Ref<KlineData[]>
  /** 原始HTTP数据（缓存，用于重建聚合器） */
  rawBars: Ref<KlineData[]>
  /** 加载状态 */
  loading: Ref<boolean>
  /** 错误信息 */
  error: Ref<string | null>
  /** WebSocket连接状态 */
  isConnected: Ref<boolean>
  /** 数据来源标识 */
  dataSource: Ref<string>
  /** 当前股票代码 */
  currentSymbol: Ref<string>

  // 方法
  /** 加载历史数据（HTTP） */
  loadHistory: () => Promise<void>
  /** 切换股票 */
  switchSymbol: (newSymbol: string) => void
  /** 切换周期 */
  switchTimeframe: (newTimeframe: Timeframe) => Promise<void>
  /** 刷新数据（重新加载） */
  refresh: () => Promise<void>
  /** 断开WebSocket连接 */
  disconnect: () => void
  /** 连接WebSocket */
  connect: () => void
}

/**
 * K线数据管理 Composable
 *
 * @param symbol - 股票代码（响应式Ref）
 * @param timeframe - 周期（响应式Ref）
 * @param options - 配置选项
 *
 * @example
 * const { bars, loading, isConnected, switchSymbol } = useKlineData(
 *   ref('600519.SH'),
 *   ref('1d'),
 *   { initialCount: 500, adjustType: 'qfq' }
 * )
 */
export function useKlineData(
  symbol: Ref<string>,
  timeframe: Ref<Timeframe>,
  options: UseKlineDataOptions = {}
): UseKlineDataReturn {
  // 默认值
  const {
    initialCount = 800,
    adjustType = 'qfq',
    enableWebSocket = true,
    autoLoad = true,
    enableIncremental = true,
    enableIndexedDB = true
  } = options

  // ========== 状态 ==========
  /** 聚合后的K线数据（供图表使用） */
  const bars = ref<KlineData[]>([])
  /** 原始HTTP数据（缓存，用于重建聚合器） */
  const rawBars = ref<KlineData[]>([])
  /** 加载状态 */
  const loading = ref(false)
  /** 错误信息 */
  const error = ref<string | null>(null)
  /** WebSocket连接状态 */
  const isConnected = ref(false)
  /** 数据来源 */
  const dataSource = ref('')
  /** 当前股票代码（内部追踪） */
  const currentSymbol = ref(symbol.value)

  // ========== 内部实例 ==========
  /** WebSocket实例 */
  let klineWs: ReturnType<typeof createKlineWebSocket> | null = null
  /** 周期聚合器 */
  let aggregator: ReturnType<typeof createKlineAggregator> | null = null
  /** 加载取消控制器 */
  let abortController: AbortController | null = null

  // ========== 工具函数 ==========

  /** 判断是否为分钟周期 */
  const isMinutePeriod = (tf: Timeframe): boolean => {
    return ['1m', '5m', '15m', '30m', '1h'].includes(tf)
  }

  /** 转换后端数据格式为内部格式 */
  const convertKlineData = (items: KlineItem[]): KlineData[] => {
    return items
      .map((item) => {
        // 后端返回时间戳（毫秒），转为秒
        let timeValue: number
        if (typeof item.time === 'string') {
          timeValue = Math.floor(new Date(item.time).getTime() / 1000)
        } else {
          const numTime = Number(item.time)
          timeValue = numTime > 100000000000 ? Math.floor(numTime / 1000) : numTime
        }

        return {
          time: timeValue,
          open: Number(item.open),
          high: Number(item.high),
          low: Number(item.low),
          close: Number(item.close),
          volume: Number(item.volume)
        }
      })
      .filter((item) => item !== null)
  }

  /** 日线去重（同一天可能有本地和在线两条数据） */
  const dedupDailyData = (data: KlineData[]): KlineData[] => {
    const isDaily = timeframe.value === '1d' || timeframe.value === '1w'
    if (!isDaily) return data

    // 按日期去重：同一天的数据（不管时间是00:00还是15:00）只保留一条
    const map = new Map<number, KlineData>()
    for (const item of data) {
      // 将时间戳转换为当天的00:00:00作为key
      const dayKey = Math.floor(item.time / 86400) * 86400
      map.set(dayKey, item)  // 同一天后面覆盖前面
    }
    return Array.from(map.values()).sort((a, b) => a.time - b.time)
  }

  // ========== WebSocket 回调处理 ==========

  /** 处理 bar_update（当前bar实时更新） */
  const onWsBarUpdate = (bar: KlineBar) => {
    if (!aggregator || !bars.value.length) return

    // 日线及以上周期：只更新当天数据
    const isDailyOrAbove = ['1d', '1w', '1M'].includes(timeframe.value)

    if (isDailyOrAbove) {
      const now = new Date()
      const today = new Date(now.getFullYear(), now.getMonth(), now.getDate()).getTime() / 1000
      const timestamp = bar.time instanceof Date ? bar.time.getTime() / 1000 : Date.parse(String(bar.time)) / 1000

      // 只处理当天数据
      if (timestamp >= today) {
        const chartBar = {
          time: today,
          open: Number(bar.open),
          high: Number(bar.high),
          low: Number(bar.low),
          close: Number(bar.close),
          volume: Number(bar.volume)
        }
        // 更新最后一根K线
        const lastIndex = bars.value.length - 1
        if (lastIndex >= 0 && bars.value[lastIndex].time === today) {
          bars.value[lastIndex] = chartBar
        }
      }
      return
    }

    // 分钟线周期：通过聚合器处理
    const timestamp = bar.time instanceof Date ? bar.time.getTime() / 1000 : Date.parse(String(bar.time)) / 1000
    const convertedBar: KlineBar = {
      time: timestamp,
      open: Number(bar.open),
      high: Number(bar.high),
      low: Number(bar.low),
      close: Number(bar.close),
      volume: Number(bar.volume)
    }

    const result = aggregator.aggregateBar(convertedBar, true)

    if (result.update) {
      // 更新当前bar
      const updateBar = {
        ...result.update,
        time: result.update.time
      }
      // 找到并更新对应的bar
      const index = bars.value.findIndex(b => b.time === updateBar.time)
      if (index >= 0) {
        bars.value[index] = updateBar
      }
    }
  }

  /** 处理 bar_close（新bar开始） */
  const onWsBarClose = (bar: KlineBar) => {
    if (!aggregator) return

    // 日线及以上周期不处理
    const isDailyOrAbove = ['1d', '1w', '1M'].includes(timeframe.value)
    if (isDailyOrAbove) return

    const timestamp = bar.time instanceof Date ? bar.time.getTime() / 1000 : Date.parse(String(bar.time)) / 1000
    const timeValue = Math.floor(timestamp) 

    const convertedBar: KlineBar = {
      time: timeValue,
      open: Number(bar.open),
      high: Number(bar.high),
      low: Number(bar.low),
      close: Number(bar.close),
      volume: Number(bar.volume)
    }

    const result = aggregator.aggregateBar(convertedBar, true)

    // 如果有收线的bar，添加它
    if (result.close) {
      const closeBar = {
        ...result.close,
        time: result.close.time 
      }
      bars.value.push(closeBar)
    }

    // 更新当前正在形成的bar
    if (result.update) {
      const updateBar = {
        ...result.update,
        time: result.update.time 
      }
      const index = bars.value.findIndex(b => b.time === updateBar.time)
      if (index >= 0) {
        bars.value[index] = updateBar
      } else {
        bars.value.push(updateBar)
      }
    }
  }

  // ========== 核心方法 ==========

  /** 加载历史数据（HTTP） */
  const loadHistory = async (): Promise<void> => {
    if (!symbol.value || symbol.value === 'undefined') {
      error.value = '无效的股票代码'
      return
    }

    // 取消之前的请求
    if (abortController) {
      abortController.abort()
    }
    abortController = new AbortController()

    loading.value = true
    error.value = null

    try {
      console.log(`[useKlineData] 加载历史数据: ${symbol.value} ${timeframe.value}`)

      // 1. 尝试从 IndexedDB 恢复缓存（页面刷新场景）
      let idbLastTime: number | undefined
      if (enableIndexedDB && bars.value.length === 0) {
        const cached = await getKlineData(symbol.value, timeframe.value)
        if (cached && cached.data.length > 0) {
          console.log(`[useKlineData] 从 IndexedDB 恢复: ${cached.data.length} 条`)
          bars.value = cached.data
          rawBars.value = cached.data
          idbLastTime = cached.meta.lastTime
          dataSource.value = cached.meta.dataSource

          // 分钟线需要初始化聚合器
          if (isMinutePeriod(timeframe.value)) {
            aggregator = createKlineAggregator(timeframe.value)
            const historyForAggregator = cached.data.map(d => ({
              time: d.time ,
              open: d.open,
              high: d.high,
              low: d.low,
              close: d.close,
              volume: d.volume
            }))
            aggregator.setHistory(historyForAggregator)
          }

          loading.value = false // 先显示缓存数据
        }
      }

      // 根据周期决定加载条数
      let count = initialCount
      if (timeframe.value === '1h') {
        count = 200
      } else if (timeframe.value === '1d') {
        count = 500
      }

      // 2. 增量模式：从 IndexedDB 或内存的 last_time 开始获取新增数据
      let res
      const lastTime = idbLastTime || (bars.value.length > 0 ? bars.value[bars.value.length - 1].time * 1000 : undefined)

      if (enableIncremental && lastTime) {
        console.log(`[useKlineData] 增量模式，after_time: ${lastTime}`)
        res = await fetchKlineIncremental(symbol.value, timeframe.value, lastTime, count, adjustType)
      } else {
        res = await fetchKline(symbol.value, timeframe.value, count, adjustType)
      }

      if (res.data && res.data.length > 0) {
        // 转换数据格式
        const converted = convertKlineData(res.data)

        // 去重（日线）
        const deduped = dedupDailyData(converted)

        // 增量模式：合并现有数据和新数据
        const isIncremental = enableIncremental && 'incremental' in res && res.incremental
        if (isIncremental && bars.value.length > 0) {
          // 合并数据（按时间戳去重）
          const existingMap = new Map(bars.value.map(b => [b.time, b]))
          for (const newBar of deduped) {
            existingMap.set(newBar.time, newBar)
          }
          const merged = Array.from(existingMap.values()).sort((a, b) => a.time - b.time)
          bars.value = merged
          rawBars.value = merged
          console.log(`[useKlineData] 增量合并: 新增 ${deduped.length} 条, 总计 ${merged.length} 条`)
        } else {
          // 全量模式：替换所有数据
          rawBars.value = deduped
          bars.value = deduped
        }

        // 分钟线需要重新初始化聚合器
        if (isMinutePeriod(timeframe.value)) {
          if (aggregator) {
            aggregator.clear()
          }
          aggregator = createKlineAggregator(timeframe.value)

          const historyForAggregator = bars.value.map(d => ({
            time: d.time ,
            open: d.open,
            high: d.high,
            low: d.low,
            close: d.close,
            volume: d.volume
          }))
          aggregator.setHistory(historyForAggregator)
        }

        dataSource.value = res.data_source || 'api'
        console.log(`[useKlineData] 加载完成: ${bars.value.length} 条, 来源: ${dataSource.value}`)

        // 3. 保存到 IndexedDB（异步，不阻塞）
        if (enableIndexedDB && bars.value.length > 0) {
          const lastBar = bars.value[bars.value.length - 1]
          saveKlineData(symbol.value, timeframe.value, bars.value, {
            lastTime: lastBar.time,
            count: bars.value.length,
            dataSource: dataSource.value,
            updatedAt: Date.now()
          }).catch(err => {
            console.warn('[useKlineData] IndexedDB 保存失败:', err)
          })
        }
      } else {
        bars.value = []
        rawBars.value = []
        console.log('[useKlineData] 无数据返回')
      }
    } catch (err) {
      console.error('[useKlineData] 加载失败:', err)
      error.value = err instanceof Error ? err.message : '加载K线数据失败'
    } finally {
      loading.value = false
      abortController = null
    }
  }

  /** 连接WebSocket */
  const connect = (): void => {
    if (!enableWebSocket || !symbol.value) return

    // 如果已连接且股票没变，只更新聚合器
    if (klineWs?.isConnected() && currentSymbol.value === symbol.value) {
      console.log('[useKlineData] WS已连接，检查聚合器')
      if (isMinutePeriod(timeframe.value) && !aggregator) {
        aggregator = createKlineAggregator(timeframe.value)
        if (rawBars.value.length > 0) {
          const historyForAggregator = rawBars.value.map(d => ({
            time: d.time ,
            open: d.open,
            high: d.high,
            low: d.low,
            close: d.close,
            volume: d.volume
          }))
          aggregator.setHistory(historyForAggregator)
        }
      }
      return
    }

    // 断开旧连接
    disconnect()

    console.log(`[useKlineData] 连接WS: ${symbol.value}`)
    currentSymbol.value = symbol.value

    // 初始化聚合器（分钟线需要）
    if (isMinutePeriod(timeframe.value)) {
      aggregator = createKlineAggregator(timeframe.value)
      if (rawBars.value.length > 0) {
        const historyForAggregator = rawBars.value.map(d => ({
          time: d.time ,
          open: d.open,
          high: d.high,
          low: d.low,
          close: d.close,
          volume: d.volume
        }))
        aggregator.setHistory(historyForAggregator)
      }
    }

    // 创建WebSocket连接
    klineWs = createKlineWebSocket(symbol.value, {
      onConnected: () => {
        isConnected.value = true
        console.log('[useKlineData] WS已连接')
      },
      onDisconnected: () => {
        isConnected.value = false
        console.log('[useKlineData] WS已断开')
      },
      onHistory: () => {
        // 历史数据通过HTTP加载，WS的history只用于初始化聚合器
        console.log('[useKlineData] 收到WS历史数据（忽略，使用HTTP数据）')
      },
      onBarUpdate: onWsBarUpdate,
      onBarClose: onWsBarClose,
      onError: (msg) => {
        console.error('[useKlineData] WS错误:', msg)
      }
    })

    klineWs.connect()
  }

  /** 断开WebSocket连接 */
  const disconnect = (): void => {
    if (klineWs) {
      console.log('[useKlineData] 断开WS')
      klineWs.disconnect()
      klineWs = null
    }
    aggregator?.clear()
    aggregator = null
    isConnected.value = false
  }

  /** 切换股票 */
  const switchSymbol = (newSymbol: string): void => {
    if (!newSymbol || newSymbol === 'undefined' || newSymbol === symbol.value) {
      return
    }

    console.log(`[useKlineData] 切换股票: ${symbol.value} -> ${newSymbol}`)

    // 更新symbol（会触发watch）
    symbol.value = newSymbol
    currentSymbol.value = newSymbol

    // 清空数据
    bars.value = []
    rawBars.value = []
    error.value = null

    // 重新加载和连接
    loadHistory().then(() => {
      connect()
    })
  }

  /** 切换周期 */
  const switchTimeframe = async (newTimeframe: Timeframe): Promise<void> => {
    if (newTimeframe === timeframe.value) return

    console.log(`[useKlineData] 切换周期: ${timeframe.value} -> ${newTimeframe}`)

    // 更新周期
    timeframe.value = newTimeframe

    // 清空聚合器
    aggregator?.clear()
    aggregator = null

    // 重新加载历史数据
    await loadHistory()

    // 重新连接WS（会重建聚合器）
    disconnect()
    connect()
  }

  /** 刷新数据 */
  const refresh = async (): Promise<void> => {
    console.log('[useKlineData] 刷新数据')
    await loadHistory()
  }

  // ========== 生命周期 ==========

  // 监听symbol变化（外部修改时自动加载）
  watch(symbol, (newVal, oldVal) => {
    if (newVal && newVal !== oldVal && newVal !== 'undefined') {
      switchSymbol(newVal)
    }
  })

  // 监听timeframe变化（外部修改时自动切换）
  watch(timeframe, (newVal, oldVal) => {
    if (newVal && newVal !== oldVal) {
      switchTimeframe(newVal)
    }
  })

  // 组件挂载时自动加载
  onMounted(() => {
    if (autoLoad && symbol.value && symbol.value !== 'undefined') {
      loadHistory().then(() => {
        if (enableWebSocket) {
          connect()
        }
      })
    }
  })

  // 组件卸载时清理
  onBeforeUnmount(() => {
    disconnect()
    if (abortController) {
      abortController.abort()
      abortController = null
    }
  })

  // ========== 返回 ==========
  return {
    bars,
    rawBars,
    loading,
    error,
    isConnected,
    dataSource,
    currentSymbol,
    loadHistory,
    switchSymbol,
    switchTimeframe,
    refresh,
    disconnect,
    connect
  }
}

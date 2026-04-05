/**
 * useRealtimeQuote - 实时行情数据管理 Composable
 *
 * 统一管理：
 * - 五档盘口数据（买卖价格和数量）
 * - 统计数据（开高低收、成交量、成交额等）
 * - 快照数据获取和更新
 * - 符合 V5 架构：组件只展示，数据由 composable 管理
 */

import { ref, computed, type Ref } from 'vue'
import { fetchSnapshot as fetchSnapshotAPI, type QuoteSnapshot } from '@/api/modules/quotes'

export interface OrderBookLevel {
  price: string | number
  size: number
}

export interface QuoteData {
  price: string | number
  change: number
  change_percent: number
  open: string | number
  high: string | number
  low: string | number
  prev_close: string | number
  volume: number
  amount: number
  turnover_rate: number
  amplitude: number
  volume_ratio: number
  outer_vol: number
  inner_vol: number
  pe_ratio: number
  pb_ratio: number
  dy_ratio: number
  zt_price: string | number
  dt_price: string | number
  beta: number
  total_shares: number
  data_source: string
}

export interface UseRealtimeQuoteOptions {
  /** 是否自动加载快照（默认true） */
  autoLoad?: boolean
  /** 刷新间隔（毫秒，默认5000） */
  refreshInterval?: number
}

export interface UseRealtimeQuoteReturn {
  // 状态
  /** 当前行情数据 */
  quote: Ref<QuoteData>
  /** 卖盘（ask5 → ask1，价格从高到低） */
  asks: Ref<OrderBookLevel[]>
  /** 买盘（bid1 → bid5，价格从低到高） */
  bids: Ref<OrderBookLevel[]>
  /** 加载状态 */
  loading: Ref<boolean>
  /** 错误信息 */
  error: Ref<string | null>

  // 方法
  /** 获取快照数据 */
  fetchSnapshot: (symbol: string) => Promise<void>
  /** 批量获取快照（用于自选股列表） */
  fetchBatchSnapshots: (symbols: string[]) => Promise<Map<string, QuoteData>>
  /** 更新行情数据（从快照） */
  updateFromSnapshot: (snapshot: QuoteSnapshot) => void
  /** 清空数据 */
  clear: () => void
}

/**
 * 后端 change_pct 字段兼容工具
 * pytdx 返回 change_pct，部分接口返回 change_percent
 */
const getChangePct = (q: any): number => {
  return parseFloat(Number(q.change_pct ?? q.change_percent ?? 0).toFixed(2))
}

/**
 * 实时行情数据管理 Composable
 *
 * @param symbol - 股票代码（响应式Ref）
 * @param options - 配置选项
 *
 * @example
 * const { quote, asks, bids, fetchSnapshot, loading } = useRealtimeQuote(selectedStock)
 *
 * // 获取快照
 * await fetchSnapshot('600519.SH')
 *
 * // 使用数据
 * console.log(quote.value.price)  // 最新价
 * console.log(asks.value[0])      // 卖一
 * console.log(bids.value[0])      // 买一
 */
export function useRealtimeQuote(
  symbol: Ref<string>,
  options: UseRealtimeQuoteOptions = {}
): UseRealtimeQuoteReturn {
  const { autoLoad = true, refreshInterval = 5000 } = options

  // ========== 状态 ==========
  const quote = ref<QuoteData>({
    price: '--',
    change: 0,
    change_percent: 0,
    open: '--',
    high: '--',
    low: '--',
    prev_close: '--',
    volume: 0,
    amount: 0,
    turnover_rate: 0,
    amplitude: 0,
    volume_ratio: 0,
    outer_vol: 0,
    inner_vol: 0,
    pe_ratio: 0,
    pb_ratio: 0,
    dy_ratio: 0,
    zt_price: '--',
    dt_price: '--',
    beta: 0,
    total_shares: 0,
    data_source: 'unknown'
  })

  // 卖盘（ask5 → ask1，价格从高到低）
  const asks = ref<OrderBookLevel[]>([
    { price: '--', size: 0 },
    { price: '--', size: 0 },
    { price: '--', size: 0 },
    { price: '--', size: 0 },
    { price: '--', size: 0 }
  ])

  // 买盘（bid1 → bid5，价格从低到高）
  const bids = ref<OrderBookLevel[]>([
    { price: '--', size: 0 },
    { price: '--', size: 0 },
    { price: '--', size: 0 },
    { price: '--', size: 0 },
    { price: '--', size: 0 }
  ])

  const loading = ref(false)
  const error = ref<string | null>(null)

  // ========== 核心方法 ==========

  /**
   * 从快照数据更新当前行情和五档盘口
   */
  const updateFromSnapshot = (snapshot: QuoteSnapshot): void => {
    const price = Number(snapshot.price) || 0
    const prevClose = Number(snapshot.pre_close ?? snapshot.prev_close ?? snapshot.last_close) || 0
    const changeAmt = Number(snapshot.change ?? (price - prevClose))

    // 更新行情数据
    quote.value = {
      price: price ? price.toFixed(2) : '--',
      change: parseFloat(changeAmt.toFixed(2)),
      change_percent: getChangePct(snapshot),
      open: snapshot.open ? Number(snapshot.open).toFixed(2) : '--',
      high: snapshot.high ? Number(snapshot.high).toFixed(2) : '--',
      low: snapshot.low ? Number(snapshot.low).toFixed(2) : '--',
      prev_close: prevClose ? prevClose.toFixed(2) : '--',
      volume: snapshot.volume || 0,
      amount: snapshot.amount || 0,
      turnover_rate: snapshot.turnover_rate || snapshot.turnover || 0,
      volume_ratio: snapshot.volume_ratio || snapshot.LB || 0,
      amplitude: snapshot.amplitude || snapshot.ZAF || 0,
      pe_ratio: snapshot.pe_ratio || snapshot.dyna_pe || 0,
      pb_ratio: snapshot.pb_ratio || snapshot.pb_mrq || 0,
      dy_ratio: snapshot.dy_ratio || snapshot.dyr || 0,
      zt_price: snapshot.zt_price ? Number(snapshot.zt_price).toFixed(2) : '--',
      dt_price: snapshot.dt_price ? Number(snapshot.dt_price).toFixed(2) : '--',
      beta: snapshot.beta || snapshot.BetaValue || 0,
      total_shares: snapshot.total_shares || snapshot.J_zgb || 0,
      inner_vol: snapshot.inner_vol || 0,
      outer_vol: snapshot.outer_vol || 0,
      data_source: snapshot.data_source || 'unknown'
    }

    // 更新五档盘口
    // 卖盘（价格从高到低：ask5 → ask1）
    asks.value = [
      { price: snapshot.ask5 != null ? Number(snapshot.ask5).toFixed(2) : '--', size: snapshot.ask_vol5 ?? 0 },
      { price: snapshot.ask4 != null ? Number(snapshot.ask4).toFixed(2) : '--', size: snapshot.ask_vol4 ?? 0 },
      { price: snapshot.ask3 != null ? Number(snapshot.ask3).toFixed(2) : '--', size: snapshot.ask_vol3 ?? 0 },
      { price: snapshot.ask2 != null ? Number(snapshot.ask2).toFixed(2) : '--', size: snapshot.ask_vol2 ?? 0 },
      { price: snapshot.ask1 != null ? Number(snapshot.ask1).toFixed(2) : '--', size: snapshot.ask_vol1 ?? 0 }
    ]

    // 买盘（价格从低到高：bid1 → bid5）
    bids.value = [
      { price: snapshot.bid1 != null ? Number(snapshot.bid1).toFixed(2) : '--', size: snapshot.bid_vol1 ?? 0 },
      { price: snapshot.bid2 != null ? Number(snapshot.bid2).toFixed(2) : '--', size: snapshot.bid_vol2 ?? 0 },
      { price: snapshot.bid3 != null ? Number(snapshot.bid3).toFixed(2) : '--', size: snapshot.bid_vol3 ?? 0 },
      { price: snapshot.bid4 != null ? Number(snapshot.bid4).toFixed(2) : '--', size: snapshot.bid_vol4 ?? 0 },
      { price: snapshot.bid5 != null ? Number(snapshot.bid5).toFixed(2) : '--', size: snapshot.bid_vol5 ?? 0 }
    ]
  }

  /**
   * 获取单个股票的快照数据
   */
  const fetchSnapshot = async (stockSymbol: string): Promise<void> => {
    if (!stockSymbol) {
      error.value = '无效的股票代码'
      return
    }

    loading.value = true
    error.value = null

    try {
      const res = await fetchSnapshotAPI(stockSymbol)
      if (res) {
        updateFromSnapshot(res)
      }
    } catch (err) {
      console.error(`[useRealtimeQuote] 获取快照失败: ${stockSymbol}`, err)
      error.value = err instanceof Error ? err.message : '获取快照失败'
    } finally {
      loading.value = false
    }
  }

  /**
   * 批量获取快照（用于自选股列表）
   *
   * @returns Map<symbol, QuoteData>
   */
  const fetchBatchSnapshots = async (symbols: string[]): Promise<Map<string, QuoteData>> => {
    const results = new Map<string, QuoteData>()

    if (!symbols || symbols.length === 0) {
      return results
    }

    try {
      // 并发获取所有股票的快照
      const tasks = symbols.map(async (s) => {
        try {
          const res = await fetchSnapshot(s)
          if (res.data) {
            const price = Number(res.data.price) || 0
            const prevClose = Number(res.data.pre_close ?? res.data.last_close) || 0
            const changeAmt = Number(res.data.change ?? (price - prevClose))

            results.set(s, {
              price: price ? price.toFixed(2) : '--',
              change: parseFloat(changeAmt.toFixed(2)),
              change_percent: getChangePct(res.data),
              open: res.data.open ? Number(res.data.open).toFixed(2) : '--',
              high: res.data.high ? Number(res.data.high).toFixed(2) : '--',
              low: res.data.low ? Number(res.data.low).toFixed(2) : '--',
              prev_close: prevClose ? prevClose.toFixed(2) : '--',
              volume: res.data.volume || 0,
              amount: res.data.amount || 0,
              turnover_rate: res.data.turnover_rate || res.data.turnover || 0,
              volume_ratio: res.data.volume_ratio || res.data.LB || 0,
              amplitude: res.data.amplitude || res.data.ZAF || 0,
              pe_ratio: res.data.pe_ratio || res.data.dyna_pe || 0,
              pb_ratio: res.data.pb_ratio || res.data.pb_mrq || 0,
              dy_ratio: res.data.dy_ratio || res.data.dyr || 0,
              zt_price: res.data.zt_price ? Number(res.data.zt_price).toFixed(2) : '--',
              dt_price: res.data.dt_price ? Number(res.data.dt_price).toFixed(2) : '--',
              beta: res.data.beta || res.data.BetaValue || 0,
              total_shares: res.data.total_shares || res.data.J_zgb || 0,
              inner_vol: res.data.inner_vol || 0,
              outer_vol: res.data.outer_vol || 0,
              data_source: res.data.data_source || 'unknown'
            })
          }
        } catch (err) {
          console.debug(`[useRealtimeQuote] 批量获取失败: ${s}`)
        }
      })

      await Promise.all(tasks)
      console.log(`[useRealtimeQuote] 批量快照完成: ${results.size}/${symbols.length}`)
    } catch (err) {
      console.error('[useRealtimeQuote] 批量获取快照失败:', err)
    }

    return results
  }

  /**
   * 清空所有数据
   */
  const clear = (): void => {
    quote.value = {
      price: '--',
      change: 0,
      change_percent: 0,
      open: '--',
      high: '--',
      low: '--',
      prev_close: '--',
      volume: 0,
      amount: 0,
      turnover_rate: 0,
      amplitude: 0,
      volume_ratio: 0,
      outer_vol: 0,
      inner_vol: 0,
      pe_ratio: 0,
      pb_ratio: 0,
      dy_ratio: 0,
      zt_price: '--',
      dt_price: '--',
      beta: 0,
      total_shares: 0,
      data_source: 'unknown'
    }

    asks.value = [
      { price: '--', size: 0 },
      { price: '--', size: 0 },
      { price: '--', size: 0 },
      { price: '--', size: 0 },
      { price: '--', size: 0 }
    ]

    bids.value = [
      { price: '--', size: 0 },
      { price: '--', size: 0 },
      { price: '--', size: 0 },
      { price: '--', size: 0 },
      { price: '--', size: 0 }
    ]

    error.value = null
  }

  return {
    quote,
    asks,
    bids,
    loading,
    error,
    fetchSnapshot,
    fetchBatchSnapshots,
    updateFromSnapshot,
    clear
  }
}

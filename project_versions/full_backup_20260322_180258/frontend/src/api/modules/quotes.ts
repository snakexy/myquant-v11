import axios from 'axios'

// 实时行情 API 接口
// V5 路由 (/api/v5) 和 quotes 路由 (/api/v1/quotes) 均直接返回 Pydantic 模型（无 {code, data} 包装）
// 使用原始 axios 实例（避免拦截器检查 code 字段）

const _base = (import.meta.env.VITE_API_BASE_URL || '/api/v1').replace(/\/v1$/, '')

// V5 专用实例（/api/v5）
const v5Api = axios.create({
  baseURL: `${_base}/api/v5`,
  timeout: 60000
})

// quotes 专用实例（/api/v1/quotes，用于 snapshot/market_status）
const rawApi = axios.create({
  baseURL: `${_base}/api/v1`,
  timeout: 60000
})

/** K线数据结构 */
export interface KlineItem {
  time: number
  open: number
  high: number
  low: number
  close: number
  volume: number
  amount?: number
  color?: string
}

/** K线响应 */
export interface KlineResponse {
  symbol: string
  period: string
  data: KlineItem[]
  data_source: string
  count: number
  adjust_type: string
}

/** 行情快照 */
export interface QuoteSnapshot {
  symbol: string
  name: string
  price: number
  change: number
  change_percent: number
  volume: number
  amount: number
  high: number
  low: number
  open: number
  prev_close: number
  timestamp: number
  bid1: number
  bid_vol1: number
  ask1: number
  ask_vol1: number
  bid2: number
  bid_vol2: number
  ask2: number
  ask_vol2: number
  bid3: number
  bid_vol3: number
  ask3: number
  ask_vol3: number
  bid4: number
  bid_vol4: number
  ask4: number
  ask_vol4: number
  bid5: number
  bid_vol5: number
  ask5: number
  ask_vol5: number
}

/** 快照响应 */
export interface SnapshotResponse {
  data: QuoteSnapshot[]
  data_source: string
  count: number
  timestamp: number
}

/** 市场状态 */
export interface MarketStatus {
  is_open: boolean
  phase: string
  phase_description: string
  market: string
  date: string
  time: string
  status: string
  is_weekend: boolean
  refresh_interval: number
  cache_ttl: number
}

// ========== API 方法 ==========

/** 获取K线数据（V5 无缝K线）*/
export const fetchKline = async (
  symbol: string,
  period: string = '1d',
  count: number = 800,
  adjustType: string = 'qfq'
): Promise<KlineResponse> => {
  const { data } = await v5Api.get<KlineResponse>(`/kline/realtime/${symbol}`, {
    params: { period, count, adjust_type: adjustType }
  })
  return data
}

/** 获取单只股票快照 */
export const fetchSnapshot = async (symbol: string): Promise<QuoteSnapshot> => {
  const { data } = await rawApi.get<QuoteSnapshot>(`/quotes/snapshot/${symbol}`)
  return data
}

/** 批量获取快照 */
export const fetchSnapshotBatch = async (symbols: string[]): Promise<SnapshotResponse> => {
  const { data } = await rawApi.get<SnapshotResponse>('/quotes/snapshot/', {
    params: { symbols: symbols.join(',') }
  })
  return data
}

/** 获取市场状态 */
export const fetchMarketStatus = async (): Promise<MarketStatus> => {
  const { data } = await rawApi.get<MarketStatus>('/quotes/market/status')
  return data
}

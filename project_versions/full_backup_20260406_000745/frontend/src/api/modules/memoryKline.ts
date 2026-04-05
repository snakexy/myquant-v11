/**
 * 内存 K 线 API - 零延迟访问
 *
 * 直接从后端 MmapKlineStore 读取，延迟 <1ms
 * 未命中时返回 null，调用方应 fallback 到普通 API
 */

import axios from 'axios'

// 通过 Vite 代理连接后端
const v5Api = axios.create({
  baseURL: '/api/v5',
  timeout: 10000
})

/** K线数据结构（与 quotes.ts KlineItem 兼容） */
export interface KlineItem {
  time: number
  open: number
  high: number
  low: number
  close: number
  volume: number
  amount?: number
  color?: string
  is_complete?: boolean
}

/** 内存K线响应 */
export interface MemoryKlineResponse {
  symbol: string
  period: string
  data: KlineItem[]
  data_source: string
  count: number
  latency_ms: number
}

/** 内存缓存统计 */
export interface MemoryStatsResponse {
  cached_files: number
  opens: number
  hits: number
  misses: number
  hit_rate: string
}

/** 预加载响应 */
export interface PreloadResponse {
  total_symbols: number
  total_periods: number
  opened: number
  failed: number
  cached_files: number
}

/**
 * 从内存获取 K 线数据（零延迟）
 *
 * @param symbol 股票代码
 * @param period 周期
 * @param count 数量
 * @returns K线数据，未命中返回 null
 */
export const getKlineFromMemory = async (
  symbol: string,
  period: string = '1d',
  count: number = 200
): Promise<MemoryKlineResponse | null> => {
  try {
    const { data } = await v5Api.get<MemoryKlineResponse>(
      `/memory/kline/${symbol}/${period}`,
      { params: { count } }
    )
    return data
  } catch (error: any) {
    // 404 表示内存未命中，返回 null 让调用方 fallback
    if (error.response?.status === 404) {
      return null
    }
    // 其他错误也返回 null，fallback 到普通 API
    console.warn(`[MemoryAPI] 获取失败: ${symbol} ${period}`, error.message)
    return null
  }
}

/**
 * 获取内存缓存统计信息
 */
export const getMemoryStats = async (): Promise<MemoryStatsResponse> => {
  const { data } = await v5Api.get<MemoryStatsResponse>('/memory/stats')
  return data
}

/**
 * 预加载股票数据到内存
 *
 * @param symbols 股票代码列表
 * @param periods 周期列表，默认 ['1d', '5m', '15m', '30m', '1h']
 */
export const preloadToMemory = async (
  symbols: string[],
  periods?: string[]
): Promise<PreloadResponse> => {
  const { data } = await v5Api.post<PreloadResponse>('/memory/preload', {
    symbols,
    periods: periods || ['1d', '5m', '15m', '30m', '1h']
  })
  return data
}

/**
 * 清空内存缓存
 */
export const clearMemoryCache = async (): Promise<{ success: boolean; message: string }> => {
  const { data } = await v5Api.delete<{ success: boolean; message: string }>('/memory/cache')
  return data
}

/**
 * MyQuant v10.0.0 - 统一数据API
 * 遵守架构原则：前端通过统一接口获取所有数据
 *
 * > 创建日期: 2026-02-06
 * > 核心原则:
 * > - 前端只调用 /api/v1/data/unified
 * > - 后端UnifiedDataManager内部选择最优数据源
 * > - 自动应用数据格式转换规则
 *
 * 架构流程:
 * 前端组件 → unified.ts → /api/v1/data/unified → UnifiedDataManager → 数据源
 *                                                      ↓
 *                                                 按规则选择:
 *                                                 - XtQuant下载+读取
 *                                                 - 在线获取
 *                                                 - 缓存策略
 *                                                 - L0-L5层级
 */

import { http } from './request'

// ==================== 类型定义 ====================

/**
 * 支持的数据类型
 */
export type UnifiedDataType =
  | 'kline'          // K线数据
  | 'realtime_quote' // 实时行情
  | 'financial'      // 财务数据
  | 'tick'           // 分笔数据

/**
 * K线周期类型（与后端保持一致）
 */
export type KlinePeriod =
  | '1min'  // 1分钟
  | '5min'  // 5分钟
  | '15min' // 15分钟
  | '30min' // 30分钟
  | '60min' // 60分钟
  | 'day'   // 日线
  | 'week'  // 周线
  | 'month' // 月线

/**
 * 统一数据请求接口
 */
export interface UnifiedDataRequest {
  data_type: UnifiedDataType
  symbols: string[]
  params?: Record<string, any>
  use_cache?: boolean  // 是否使用缓存（默认true）
}

/**
 * K线数据项（后端返回格式）
 */
export interface KlineDataItem {
  time: string           // ISO 8601格式: "2026-02-05 15:00:00"
  open: number
  high: number
  low: number
  close: number
  volume: number
  amount?: number
  trading_day_index?: number  // 交易日历索引
}

/**
 * 统一数据响应
 */
export interface UnifiedDataResponse<T = any> {
  code: number           // 200=成功
  data?: T
  message: string
  metadata?: {
    source: string        // 数据源名称
    elapsed_ms: number   // 请求耗时
    data_level?: string  // L0-L5级别
    timestamp: string
  }
}

/**
 * Seamless K线请求（对应后端 SeamlessKlineRequest）
 */
export interface SeamlessKlineRequest {
  symbols: string[]
  period: string
  count: number
  end_date?: string
  start_date?: string
  adjust_type?: 'none' | 'front' | 'back'
}

// ==================== K线数据API ====================

/**
 * 获取K线数据（统一接口）
 *
 * ⭐ 调用后端 /api/v5/kline/seamless 接口
 *
 * @param symbol 股票代码（如 "600519.SH"）
 * @param period K线周期 (1min/5min/15min/30min/60min/day/week/month)
 * @param count 数据条数（默认500，最大1000）
 * @param end_date 结束日期 YYYY-MM-DD（获取该日期之前的数据，用于加载更多）
 * @param use_cache 是否使用缓存（默认true）
 * @returns K线数据
 *
 * @example
 * // 获取贵州茅台日K线
 * const data = await getUnifiedKline('600519.SH', 'day', 250)
 *
 * @example
 * // 获取2024-01-01之前的日K线（加载更多）
 * const data = await getUnifiedKline('600519.SH', 'day', 250, '2024-01-01')
 */
export const getUnifiedKline = async (
  symbol: string,
  period: KlinePeriod,
  count: number = 500,
  end_date?: string,
  use_cache: boolean = true
): Promise<UnifiedDataResponse<KlineDataItem[]>> => {
  // 映射周期格式：前端 period -> 后端 period
  const periodMap: Record<string, string> = {
    '1min': '1m',
    '5min': '5m',
    '15min': '15m',
    '30min': '30m',
    '60min': '1h',
    'day': '1d',
    'week': '1w',
    'month': '1mon'
  }
  const apiPeriod = periodMap[period] || period

  // 构建请求体（符合后端 SeamlessKlineRequest 格式）
  const request: SeamlessKlineRequest = {
    symbols: [symbol],
    period: apiPeriod,
    count: Math.min(count, 1000),  // 后端最大1000
    end_date: end_date,
    adjust_type: 'front'  // 前复权
  }

  // 调用后端 seamless API
  return http.post<UnifiedDataResponse<KlineDataItem[]>>('/api/v5/kline/seamless', request)
    .then(response => {
      // 后端返回格式: { code: 0, data: { symbol: { data: [...] }, message: "success" }
      if (response.code === 0 && response.data && response.data[symbol]) {
        const symbolData = response.data[symbol]
        return {
          code: 200,
          data: symbolData.data || [],
          message: response.message,
          metadata: {
            source: symbolData.source || 'seamless',
            elapsed_ms: 0,
            timestamp: new Date().toISOString()
          }
        }
      }
      return {
        code: response.code || 500,
        data: [],
        message: response.message || 'No data'
      }
    })
}

/**
 * 获取日K线数据（便捷函数）
 */
export const getDailyKline = (
  symbol: string,
  count: number = 250
): Promise<UnifiedDataResponse<KlineDataItem[]>> => {
  return getUnifiedKline(symbol, 'day', count)
}

/**
 * 获取周K线数据（便捷函数）
 */
export const getWeeklyKline = (
  symbol: string,
  count: number = 120
): Promise<UnifiedDataResponse<KlineDataItem[]>> => {
  return getUnifiedKline(symbol, 'week', count)
}

/**
 * 获取月K线数据（便捷函数）
 */
export const getMonthlyKline = (
  symbol: string,
  count: number = 60
): Promise<UnifiedDataResponse<KlineDataItem[]>> => {
  return getUnifiedKline(symbol, 'month', count)
}

/**
 * 获取60分钟K线数据（便捷函数）
 */
export const get60MinKline = (
  symbol: string,
  count: number = 120
): Promise<UnifiedDataResponse<KlineDataItem[]>> => {
  return getUnifiedKline(symbol, '60min', count)
}

/**
 * 获取5分钟K线数据（便捷函数）
 */
export const get5MinKline = (
  symbol: string,
  count: number = 500
): Promise<UnifiedDataResponse<KlineDataItem[]>> => {
  return getUnifiedKline(symbol, '5min', count)
}

/**
 * 获取1分钟K线数据（便捷函数）
 */
export const get1MinKline = (
  symbol: string,
  count: number = 500
): Promise<UnifiedDataResponse<KlineDataItem[]>> => {
  return getUnifiedKline(symbol, '1min', count)
}

// ==================== 实时行情API ====================

/**
 * 获取实时行情（统一接口）
 */
export const getRealtimeQuote = async (
  symbols: string[],
  use_cache: boolean = true
): Promise<UnifiedDataResponse<any[]>> => {
  const request: UnifiedDataRequest = {
    data_type: 'realtime_quote',
    symbols,
    use_cache: use_cache
  }

  return http.post<UnifiedDataResponse<any[]>>('/api/v1/data/unified', request)
    .then(response => response.data)
}

// ==================== 数据转换函数 ====================

/**
 * 将统一API返回的K线数据转换为lightweight-charts格式
 *
 * ⚠️ 数据转换规则:
 * - 后端返回: time = "2026-02-05 15:00:00" (ISO 8601字符串)
 * - lightweight-charts需要: time = number (秒级时间戳)
 *
 * @param apiData API返回的K线数据
 * @param includeVolume 是否包含成交量
 * @returns 转换后的数据数组
 */
export function transformUnifiedKlineData(
  apiData: KlineDataItem[],
  includeVolume: boolean = true
): Array<{
  time: number
  open: number
  high: number
  low: number
  close: number
  volume?: number
}> {
  return apiData.map(item => {
    // A股日线用 BusinessDay 格式提取 CST 日期，再转为 UTC 秒级时间戳
    let time: any
    if (typeof item.time === 'string') {
      const datePart = item.time.slice(0, 10) // "2026-03-13"
      const [year, month, day] = datePart.split('-').map(Number)
      time = { year, month, day }
    } else if (typeof item.time === 'number') {
      // 毫秒或秒 → 提取 CST 日期（UTC+8）
      const ms = item.time > 10000000000 ? item.time : item.time * 1000
      const cst = new Date(ms + 8 * 3600 * 1000) // 转 CST
      time = { year: cst.getUTCFullYear(), month: cst.getUTCMonth() + 1, day: cst.getUTCDate() }
    } else {
      const now = new Date()
      time = { year: now.getFullYear(), month: now.getMonth() + 1, day: now.getDate() }
    }
    const timestamp = typeof time === 'object'
      ? Date.UTC(time.year, time.month - 1, time.day) / 1000
      : time

    const transformed: any = {
      time: timestamp, // lightweight-charts使用秒级时间戳
      open: item.open,
      high: item.high,
      low: item.low,
      close: item.close
    }

    if (includeVolume && item.volume !== undefined) {
      transformed.volume = item.volume
    }

    return transformed
  })
}

// ==================== 常量配置 ====================

/**
 * 默认K线配置（遵守K线加载规则）
 */
export const DEFAULT_UNIFIED_KLINE_CONFIG = {
  // 默认数据条数（遵守K线加载规则）
  defaultCount: {
    'month': 60,   // 月K：5年
    'week': 120,   // 周K：2.3年
    'day': 250,    // 日K：1年
    '60min': 120,  // 60分钟K：5天
    '30min': 120,  // 30分钟K：2.5天
    '15min': 120,  // 15分钟K：1.25天
    '5min': 500,   // 5分钟K：1.7天
    '1min': 500    // 1分钟K：0.83天
  },

  // 最大数据条数
  maxCount: 10000,

  // 推荐周期
  recommendedPeriods: [
    { value: 'month', name: '月K', description: '超长期趋势' },
    { value: 'week', name: '周K', description: '中长期趋势' },
    { value: 'day', name: '日K', description: '长期趋势' },
    { value: '60min', name: '60分钟', description: '日内趋势' },
    { value: '5min', name: '5分钟', description: '短线交易' },
    { value: '1min', name: '1分钟', description: '超短线' }
  ]
} as const

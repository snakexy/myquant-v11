/**
 * MyQuant v10.0.0 - K线图API
 * 基于XtQuant的纯在线获取K线数据API
 *
 * > 创建日期: 2026-02-05
 * > 特性:
 * > - 纯在线获取，无需下载
 * > - 性能优秀：9-36ms
 * > - 支持所有K线周期（月K、周K、日K、分钟K）
 * > - 支持最大10000条数据
 */

import { http } from './request'

// ==================== 类型定义 ====================

/**
 * K线周期类型
 */
export type KlinePeriod =
  | '1mon'  // 月K
  | '1w'    // 周K
  | '1d'    // 日K
  | '1h'    // 60分钟K
  | '30m'   // 30分钟K
  | '15m'   // 15分钟K
  | '5m'    // 5分钟K
  | '1m'    // 1分钟K
  | '1min'  // 1分钟K（别名）

/**
 * K线数据项
 */
export interface KlineDataItem {
  time: string           // 时间戳（毫秒）或格式化字符串
  open: number           // 开盘价
  high: number           // 最高价
  low: number            // 最低价
  close: number          // 收盘价
  volume: number         // 成交量（手）
  amount?: number        // 成交额（元）
}

/**
 * K线API响应
 */
export interface KlineResponse {
  code: number           // 响应码（200=成功）
  data?: KlineDataItem[] // K线数据数组
  message: string        // 响应消息
  count: number          // 数据条数
  period: string         // K线周期
  elapsed_ms: number     // 请求耗时（毫秒）
}

/**
 * 支持的K线周期信息
 */
export interface KlinePeriodInfo {
  value: string          // 周期值
  name: string           // 中文名称
  name_en: string        // 英文名称
  description: string    // 描述
  max_count: number      // 最大数据条数
  performance_ms: string // 性能参考
}

/**
 * 周期列表响应
 */
export interface PeriodsResponse {
  code: number
  data?: KlinePeriodInfo[]
  message: string
}

// ==================== K线API ====================

/**
 * 获取K线数据
 *
 * @param symbol 股票代码（如 "600519.SH"）
 * @param period K线周期（1mon, 1w, 1d, 1h, 30m, 15m, 5m, 1m）
 * @param count K线数量（1-10000，默认500）
 * @returns K线数据
 *
 * @example
 * // 获取贵州茅台日K线
 * getKlineData('600519.SH', '1d', 250)
 *
 * @example
 * // 获取5分钟K线
 * getKlineData('600519.SH', '5m', 500)
 *
 * @example
 * // 获取月K线（注意：使用1mon不是1M）
 * getKlineData('600519.SH', '1mon', 60)
 */
export const getKlineData = (
  symbol: string,
  period: KlinePeriod,
  count: number = 500
): Promise<KlineResponse> => {
  return http.get<KlineResponse>('/v1/kline/data', {
    params: {
      symbol,
      period,
      count
    }
  })
}

/**
 * 获取支持的K线周期列表
 *
 * @returns 周期信息列表
 *
 * @example
 * const response = await getSupportedPeriods()
 * response.data.forEach(period => {
 *   console.log(`${period.value}: ${period.name}`)
 * })
 */
export const getSupportedPeriods = (): Promise<PeriodsResponse> => {
  return http.get<PeriodsResponse>('/v1/kline/periods')
}

/**
 * K线API健康检查
 *
 * @returns 健康状态
 */
export const pingKline = (): Promise<{ status: string; message: string; data_source: string }> => {
  return http.get('/v1/kline/ping')
}

// ==================== 便捷函数 ====================

/**
 * 获取日K线数据
 */
export const getDailyKline = (symbol: string, count: number = 250): Promise<KlineResponse> => {
  return getKlineData(symbol, '1d', count)
}

/**
 * 获取周K线数据
 */
export const getWeeklyKline = (symbol: string, count: number = 120): Promise<KlineResponse> => {
  return getKlineData(symbol, '1w', count)
}

/**
 * 获取月K线数据
 */
export const getMonthlyKline = (symbol: string, count: number = 60): Promise<KlineResponse> => {
  return getKlineData(symbol, '1mon', count)
}

/**
 * 获取60分钟K线数据
 */
export const get60MinKline = (symbol: string, count: number = 120): Promise<KlineResponse> => {
  return getKlineData(symbol, '1h', count)
}

/**
 * 获取5分钟K线数据
 */
export const get5MinKline = (symbol: string, count: number = 500): Promise<KlineResponse> => {
  return getKlineData(symbol, '5m', count)
}

/**
 * 获取1分钟K线数据
 */
export const get1MinKline = (symbol: string, count: number = 500): Promise<KlineResponse> => {
  return getKlineData(symbol, '1m', count)
}

// ==================== 数据转换函数 ====================

/**
 * 将API返回的K线数据转换为图表可用的格式
 *
 * ⚠️ 数据转换规则（遵守后端数据格式规范）:
 * - 后端返回: time = "2026-02-05 15:00:00" (ISO 8601字符串格式)
 * - lightweight-charts需要: time = number (秒级时间戳或毫秒级时间戳)
 *
 * @param apiData API返回的K线数据
 * @param includeVolume 是否包含成交量
 * @returns 转换后的数据数组
 */
export function transformKlineData(
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
    // ⚠️ 关键: 处理time字段转换
    // 后端返回格式: "2026-02-05 15:00:00" (字符串)
    // lightweight-charts需要: 秒级或毫秒级时间戳

    let timestamp: number
    if (typeof item.time === 'string') {
      // 字符串格式: "2026-02-05 15:00:00" 或 "2026-02-05"
      const date = new Date(item.time.replace(/-/g, '/')) // 替换-为/以兼容所有浏览器
      timestamp = Math.floor(date.getTime() / 1000) // 转换为秒级时间戳
    } else if (typeof item.time === 'number') {
      // 如果已经是数字，判断是秒还是毫秒
      timestamp = item.time > 10000000000 ? Math.floor(item.time / 1000) : item.time
    } else {
      timestamp = Date.now() / 1000 // 兜底：使用当前时间
    }

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

/**
 * 转换时间戳为秒级（用于lightweight-charts）
 *
 * @param milliseconds 毫秒时间戳
 * @returns 秒时间戳
 */
export function toSeconds(milliseconds: number | string): number {
  const ms = typeof milliseconds === 'string'
    ? parseInt(milliseconds)
    : milliseconds
  return Math.floor(ms / 1000)
}

/**
 * 格式化K线时间用于显示
 *
 * @param timeStr 时间字符串
 * @param period K线周期
 * @returns 格式化后的时间字符串
 */
export function formatKlineTime(timeStr: string, period: string): string {
  const time = parseInt(timeStr)
  const date = new Date(time)

  // 分钟K线：显示时间
  if (['1m', '5m', '15m', '30m', '1h'].includes(period)) {
    return date.toISOString().slice(0, 19).replace('T', ' ')
  }

  // 日K、周K、月K：只显示日期
  return date.toISOString().slice(0, 10)
}

// ==================== 常量配置 ====================

/**
 * 默认K线配置
 */
export const DEFAULT_KLINE_CONFIG = {
  // 默认数据条数
  defaultCount: {
    '1mon': 60,   // 月K：5年
    '1w': 120,    // 周K：2.3年
    '1d': 250,    // 日K：1年
    '1h': 120,    // 60分钟K：5天
    '30m': 120,   // 30分钟K：2.5天
    '15m': 120,   // 15分钟K：1.25天
    '5m': 500,    // 5分钟K：1.7天
    '1m': 500     // 1分钟K：0.83天
  },

  // 最大数据条数
  maxCount: 10000,

  // 推荐周期
  recommendedPeriods: [
    { value: '1mon', name: '月K', description: '超长期趋势' },
    { value: '1w', name: '周K', description: '中长期趋势' },
    { value: '1d', name: '日K', description: '长期趋势' },
    { value: '1h', name: '60分钟', description: '日内趋势' },
    { value: '5m', name: '5分钟', description: '短线交易' },
    { value: '1m', name: '1分钟', description: '超短线' }
  ]
} as const

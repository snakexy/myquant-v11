/**
 * MyQuant v9.0.0 - Market Type Definitions
 * 市场数据类型定义
 */

/**
 * 股票行情
 */
export interface Quote {
  symbol: string          // 股票代码
  name: string            // 股票名称
  price: number           // 当前价格
  change: number          // 涨跌额
  change_percent: number  // 涨跌幅%
  open: number            // 开盘价
  high: number            // 最高价
  low: number             // 最低价
  close: number           // 收盘价（昨收）
  volume: number          // 成交量
  amount: number          // 成交额
  bid_price?: number[]    // 买盘价
  bid_volume?: number[]   // 买盘量
  ask_price?: number[]    // 卖盘价
  ask_volume?: number[]   // 卖盘量
  timestamp: number       // 时间戳
  pinyin?: string         // 拼音缩写
}

/**
 * K线数据
 */
export interface KlineData {
  date: string            // 日期/时间
  open: number            // 开盘价
  high: number            // 最高价
  low: number             // 最低价
  close: number           // 收盘价
  volume: number          // 成交量
  amount: number          // 成交额
  change_percent?: number // 涨跌幅
}

/**
 * 分时数据
 */
export interface TimeshareData {
  time: string            // 时间
  price: number           // 价格
  volume: number          // 成交量
  amount: number          // 成交额
  avg_price?: number      // 均价
}

/**
 * 市场概览
 */
export interface MarketOverview {
  index_sh: IndexData     // 上证指数
  index_sz: IndexData     // 深证成指
  index_cyb?: IndexData   // 创业板指
  market_cap: number      // 总市值
  pe_ratio: number        // 市盈率
  volume_ratio: number    // 量比
  up_count: number        // 上涨家数
  down_count: number      // 下跌家数
  flat_count: number      // 平盘家数
  limit_up: number        // 涨停家数
  limit_down: number      // 跌停家数
}

/**
 * 指数数据
 */
export interface IndexData {
  name: string            // 指数名称
  code: string            // 指数代码
  value: number           // 指数值
  change: number          // 涨跌点
  change_percent: number  // 涨跌幅%
  high: number            // 最高
  low: number             // 最低
  volume: number          // 成交量
  amount: number          // 成交额
}

/**
 * 技术指标数据
 */
export interface TechnicalIndicators {
  ma?: MAIndicator
  boll?: BOLLIndicator
  macd?: MACDIndicator
  kdj?: KDJIndicator
  rsi?: RSIIndicator
}

/**
 * MA均线指标
 */
export interface MAIndicator {
  ma5?: number
  ma10?: number
  ma20?: number
  ma30?: number
  ma60?: number
  ma120?: number
}

/**
 * BOLL布林带指标
 */
export interface BOLLIndicator {
  upper: number           // 上轨
  middle: number          // 中轨
  lower: number           // 下轨
}

/**
 * MACD指标
 */
export interface MACDIndicator {
  dif: number             // DIF线
  dea: number             // DEA线
  macd: number            // MACD柱
}

/**
 * KDJ指标
 */
export interface KDJIndicator {
  k: number               // K值
  d: number               // D值
  j: number               // J值
}

/**
 * RSI指标
 */
export interface RSIIndicator {
  rsi6: number            // RSI6
  rsi12: number           // RSI12
  rsi24: number           // RSI24
}

/**
 * K线周期
 */
export type KlinePeriod =
  | '5min'    // 5分钟
  | '15min'   // 15分钟
  | '30min'   // 30分钟
  | '60min'   // 60分钟
  | 'day'     // 日K
  | 'week'    // 周K
  | 'month'   // 月K

/**
 * 涨跌颜色类型
 */
export type ChangeColorType = 'up' | 'down' | 'flat'

/**
 * 获取涨跌颜色类型
 */
export function getChangeColorType(changePercent: number): ChangeColorType {
  if (changePercent > 0) return 'up'
  if (changePercent < 0) return 'down'
  return 'flat'
}

/**
 * 涨跌颜色值
 */
export const CHANGE_COLORS = {
  up: '#ef4444',      // 红色涨
  down: '#10b981',    // 绿色跌
  flat: '#94a3b8'     // 灰色平
} as const

/**
 * 获取涨跌颜色
 */
export function getChangeColor(changePercent: number): string {
  const type = getChangeColorType(changePercent)
  return CHANGE_COLORS[type]
}

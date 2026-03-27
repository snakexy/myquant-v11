/**
 * 图表辅助工具函数
 * 提供图表常用的转换、格式化和处理函数
 */

import { ColorType } from 'lightweight-charts'

// ==================== 类型定义 ====================

export interface KLineDataItem {
  timestamp: number
  open: number
  high: number
  low: number
  close: number
  volume: number
}

export interface CandlestickData {
  time: number | string
  open: number
  high: number
  low: number
  close: number
}

export interface LineData {
  time: number | string
  value: number
}

export interface HistogramData {
  time: number | string
  value: number
  color?: string
}

// ==================== 时间转换函数 ====================

/**
 * 将时间戳转换为 lightweight-charts 时间格式
 * @param timestamp - 毫秒时间戳
 * @returns lightweight-charts 时间格式（秒）
 */
export function timestampToTime(timestamp: number): number {
  return Math.floor(timestamp / 1000)
}

/**
 * 将日期字符串转换为时间戳
 * @param dateStr - 日期字符串 (YYYY-MM-DD)
 * @returns 毫秒时间戳
 */
export function dateStrToTimestamp(dateStr: string): number {
  return new Date(dateStr).getTime()
}

/**
 * 将时间戳转换为日期字符串
 * @param timestamp - 毫秒时间戳
 * @param format - 格式类型 ('date' | 'datetime' | 'time')
 * @returns 格式化的日期字符串
 */
export function timestampToDateStr(
  timestamp: number,
  format: 'date' | 'datetime' | 'time' = 'date'
): string {
  const date = new Date(timestamp)

  if (format === 'date') {
    return date.toISOString().split('T')[0]!
  }

  if (format === 'time') {
    return date.toTimeString().split(' ')[0]!.slice(0, 5)
  }

  return date.toISOString().replace('T', ' ').slice(0, 19)
}

// ==================== 数据转换函数 ====================

/**
 * 转换K线数据为蜡烛图数据格式
 * @param klineData - K线数据数组
 * @returns 蜡烛图数据数组
 */
export function convertToCandlestickData(
  klineData: KLineDataItem[]
): CandlestickData[] {
  return klineData.map(item => ({
    time: timestampToTime(item.timestamp),
    open: item.open,
    high: item.high,
    low: item.low,
    close: item.close
  }))
}

/**
 * 转换为折线图数据格式
 * @param data - 数据值数组（可以包含NaN）
 * @param timestamps - 对应的时间戳数组
 * @returns 折线图数据数组
 */
export function convertToLineData(
  data: (number | undefined)[],
  timestamps: number[]
): LineData[] {
  const result: LineData[] = []

  for (let i = 0; i < Math.min(data.length, timestamps.length); i++) {
    const value = data[i]
    if (value !== undefined && !isNaN(value)) {
      result.push({
        time: timestampToTime(timestamps[i]),
        value: value
      })
    }
  }

  return result
}

/**
 * 转换为柱状图数据格式
 * @param data - 数据值数组
 * @param timestamps - 对应的时间戳数组
 * @param color - 可选的颜色值或颜色函数
 * @returns 柱状图数据数组
 */
export function convertToHistogramData(
  data: (number | undefined)[],
  timestamps: number[],
  color?: string | ((value: number) => string)
): HistogramData[] {
  const result: HistogramData[] = []

  for (let i = 0; i < Math.min(data.length, timestamps.length); i++) {
    const value = data[i]
    if (value !== undefined && !isNaN(value)) {
      result.push({
        time: timestampToTime(timestamps[i]),
        value: value,
        color: typeof color === 'function' ? color(value) : color
      })
    }
  }

  return result
}

/**
 * 转换成交量数据
 * @param klineData - K线数据数组
 * @param upColor - 上涨颜色
 * @param downColor - 下跌颜色
 * @returns 柱状图数据数组
 */
export function convertVolumeData(
  klineData: KLineDataItem[],
  upColor: string = 'rgba(239, 68, 68, 0.5)',
  downColor: string = 'rgba(16, 185, 129, 0.5)'
): HistogramData[] {
  return klineData.map(item => ({
    time: timestampToTime(item.timestamp),
    value: item.volume,
    color: item.close >= item.open ? upColor : downColor
  }))
}

/**
 * 转换MACD柱状图数据
 * @param histogram - MACD柱状图值数组
 * @param timestamps - 时间戳数组
 * @param upColor - 上涨颜色
 * @param downColor - 下跌颜色
 * @returns 柱状图数据数组
 */
export function convertMACDHistogramData(
  histogram: (number | undefined)[],
  timestamps: number[],
  upColor: string = '#ef4444',
  downColor: string = '#10b981'
): HistogramData[] {
  return convertToHistogramData(histogram, timestamps, (value) =>
    value >= 0 ? upColor : downColor
  )
}

// ==================== 数据验证函数 ====================

/**
 * 验证K线数据是否有效
 * @param data - K线数据项
 * @returns 是否有效
 */
export function isValidKLineData(data: KLineDataItem): boolean {
  return (
    data &&
    typeof data.timestamp === 'number' &&
    !isNaN(data.timestamp) &&
    typeof data.open === 'number' &&
    !isNaN(data.open) &&
    typeof data.high === 'number' &&
    !isNaN(data.high) &&
    typeof data.low === 'number' &&
    !isNaN(data.low) &&
    typeof data.close === 'number' &&
    !isNaN(data.close) &&
    typeof data.volume === 'number' &&
    !isNaN(data.volume) &&
    data.high >= data.low &&
    data.high >= data.open &&
    data.high >= data.close &&
    data.low <= data.open &&
    data.low <= data.close
  )
}

/**
 * 过滤无效的K线数据
 * @param klineData - K线数据数组
 * @returns 过滤后的K线数据数组
 */
export function filterValidKLineData(klineData: KLineDataItem[]): KLineDataItem[] {
  return klineData.filter(item => isValidKLineData(item))
}

/**
 * 检查数据是否有间隙（时间戳不连续）
 * @param timestamps - 时间戳数组
 * @param expectedPeriod - 预期周期（毫秒）
 * @returns 间隙位置数组
 */
export function findDataGaps(
  timestamps: number[],
  expectedPeriod: number
): number[] {
  const gaps: number[] = []

  for (let i = 1; i < timestamps.length; i++) {
    const diff = timestamps[i] - timestamps[i - 1]
    // 允许10%的误差
    if (diff > expectedPeriod * 1.1) {
      gaps.push(i)
    }
  }

  return gaps
}

// ==================== 数据计算函数 ====================

/**
 * 计算数据变化率
 * @param data - 数据数组
 * @returns 变化率数组
 */
export function calculateChangeRate(data: number[]): number[] {
  const result: number[] = [0] // 第一个变化率为0

  for (let i = 1; i < data.length; i++) {
    const prev = data[i - 1]
    const curr = data[i]
    const rate = prev !== 0 ? ((curr - prev) / prev) * 100 : 0
    result.push(rate)
  }

  return result
}

/**
 * 计算涨跌幅
 * @param open - 开盘价
 * @param close - 收盘价
 * @returns 涨跌幅百分比
 */
export function calculatePriceChange(open: number, close: number): number {
  if (open === 0) return 0
  return ((close - open) / open) * 100
}

/**
 * 计算涨跌额
 * @param open - 开盘价
 * @param close - 收盘价
 * @returns 涨跌额
 */
export function calculatePriceDifference(open: number, close: number): number {
  return close - open
}

// ==================== 颜色相关函数 ====================

/**
 * 判断涨跌
 * @param open - 开盘价
 * @param close - 收盘价
 * @returns 'up' | 'down' | 'flat'
 */
export function getPriceDirection(
  open: number,
  close: number
): 'up' | 'down' | 'flat' {
  if (close > open) return 'up'
  if (close < open) return 'down'
  return 'flat'
}

/**
 * 根据涨跌获取颜色
 * @param open - 开盘价
 * @param close - 收盘价
 * @param upColor - 上涨颜色
 * @param downColor - 下跌颜色
 * @param flatColor - 平盘颜色
 * @returns 颜色值
 */
export function getPriceColor(
  open: number,
  close: number,
  upColor: string = '#ef4444',
  downColor: string = '#10b981',
  flatColor: string = '#94a3b8'
): string {
  const direction = getPriceDirection(open, close)
  if (direction === 'up') return upColor
  if (direction === 'down') return downColor
  return flatColor
}

/**
 * 创建渐变色
 * @param color - 基础颜色
 * @param opacity - 透明度（0-1）
 * @returns rgba颜色字符串
 */
export function createRgbaColor(color: string, opacity: number): string {
  // 假设输入是十六进制颜色 (#RRGGBB)
  const hex = color.replace('#', '')
  const r = parseInt(hex.substring(0, 2), 16)
  const g = parseInt(hex.substring(2, 4), 16)
  const b = parseInt(hex.substring(4, 6), 16)

  return `rgba(${r}, ${g}, ${b}, ${opacity})`
}

// ==================== 格式化函数 ====================

/**
 * 格式化价格
 * @param price - 价格值
 * @param decimals - 小数位数
 * @returns 格式化的价格字符串
 */
export function formatPrice(price: number, decimals: number = 2): string {
  return price.toFixed(decimals)
}

/**
 * 格式化成交量
 * @param volume - 成交量
 * @returns 格式化的成交量字符串（带单位）
 */
export function formatVolume(volume: number): string {
  if (volume >= 100000000) {
    return (volume / 100000000).toFixed(2) + '亿'
  }
  if (volume >= 10000) {
    return (volume / 10000).toFixed(2) + '万'
  }
  return volume.toFixed(0)
}

/**
 * 格式化涨跌幅
 * @param change - 涨跌幅
 * @param sign - 是否显示正负号
 * @returns 格式化的涨跌幅字符串
 */
export function formatChangePercent(change: number, sign: boolean = true): string {
  const signStr = change > 0 && sign ? '+' : ''
  return `${signStr}${change.toFixed(2)}%`
}

// ==================== TradingView 颜色配置 ====================

export const TradingViewColors = {
  // 背景色
  backgroundColor: '#131722' as ColorType.Solid,
  gridColor: 'rgba(148, 163, 184, 0.1)',

  // K线颜色（中国股市：红涨绿跌）
  upColor: '#ef4444',
  downColor: '#10b981',
  wickUpColor: '#ef4444',
  wickDownColor: '#10b981',

  // 成交量颜色
  volumeUpColor: 'rgba(239, 68, 68, 0.5)',
  volumeDownColor: 'rgba(16, 185, 129, 0.5)',

  // 均线颜色
  ma5Color: '#FF6B6B',
  ma10Color: '#4ECDC4',
  ma20Color: '#45B7D1',
  ma30Color: '#96CEB4',
  ma60Color: '#FFA07A',

  // 布林带颜色
  bollUpperColor: '#FF9800',
  bollMiddleColor: '#FF9800',
  bollLowerColor: '#FF9800',

  // MACD颜色
  macdColor: '#26A69A',
  macdSignalColor: '#FF6B6B',
  macdHistogramUpColor: '#ef4444',
  macdHistogramDownColor: '#10b981',

  // RSI颜色
  rsi6Color: '#9C27B0',
  rsi12Color: '#E91E63',
  rsi24Color: '#673AB7',

  // KDJ颜色
  kdjKColor: '#FFEB3B',
  kdjDColor: '#9E9E9E',
  kdjJColor: '#FF5722',

  // 其他指标颜色
  cciColor: '#FF9800',
  wrColor: '#2196F3',
  atrColor: '#4CAF50',
  obvColor: '#00BCD4',

  // 交叉准星颜色
  crosshairColor: '#2962ff',
  crosshairLabelColor: '#2962ff',

  // 边框颜色
  borderColor: '#2A2E39'
}

// ==================== 指标元数据 ====================

export const IndicatorMetadata = {
  MA: {
    name: 'MA均线',
    type: 'overlay',
    defaultPeriods: [5, 10, 20, 30, 60],
    colors: [
      TradingViewColors.ma5Color,
      TradingViewColors.ma10Color,
      TradingViewColors.ma20Color,
      TradingViewColors.ma30Color,
      TradingViewColors.ma60Color
    ]
  },
  BOLL: {
    name: '布林带',
    type: 'overlay',
    defaultPeriod: 20,
    colors: {
      upper: TradingViewColors.bollUpperColor,
      middle: TradingViewColors.bollMiddleColor,
      lower: TradingViewColors.bollLowerColor
    }
  },
  MACD: {
    name: 'MACD',
    type: 'pane',
    defaultHeight: 150,
    colors: {
      macd: TradingViewColors.macdColor,
      signal: TradingViewColors.macdSignalColor,
      histogramUp: TradingViewColors.macdHistogramUpColor,
      histogramDown: TradingViewColors.macdHistogramDownColor
    }
  },
  RSI: {
    name: 'RSI',
    type: 'pane',
    defaultHeight: 120,
    colors: {
      rsi6: TradingViewColors.rsi6Color,
      rsi12: TradingViewColors.rsi12Color,
      rsi24: TradingViewColors.rsi24Color
    }
  },
  KDJ: {
    name: 'KDJ',
    type: 'pane',
    defaultHeight: 120,
    colors: {
      k: TradingViewColors.kdjKColor,
      d: TradingViewColors.kdjDColor,
      j: TradingViewColors.kdjJColor
    }
  },
  CCI: {
    name: 'CCI',
    type: 'pane',
    defaultHeight: 120,
    color: TradingViewColors.cciColor
  },
  WR: {
    name: 'WR',
    type: 'pane',
    defaultHeight: 120,
    color: TradingViewColors.wrColor
  },
  ATR: {
    name: 'ATR',
    type: 'pane',
    defaultHeight: 120,
    color: TradingViewColors.atrColor
  },
  OBV: {
    name: 'OBV',
    type: 'pane',
    defaultHeight: 120,
    color: TradingViewColors.obvColor
  }
}

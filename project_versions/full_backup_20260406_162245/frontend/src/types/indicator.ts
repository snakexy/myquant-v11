/**
 * 技术指标类型定义
 */

/**
 * 指标计算请求
 */
export interface IndicatorRequest {
  symbol: string
  period?: string
  count?: number
  indicators?: string[]
}

/**
 * 带参数的指标计算请求
 */
export interface IndicatorParamsRequest {
  symbol: string
  period?: string
  count?: number
  indicators: Record<string, Record<string, any>>
}

/**
 * 指标计算响应
 */
export interface IndicatorResponse {
  symbol: string
  period: string
  count: number
  kline: KlineData
  indicators: IndicatorDataMap
}

/**
 * K线数据
 */
export interface KlineData {
  datetime: string[]
  open: number[]
  high: number[]
  low: number[]
  close: number[]
  volume: number[]
  amount?: number[]
}

/**
 * 指标数据映射
 */
export interface IndicatorDataMap {
  [key: string]: number[] | IndicatorSeriesData
}

/**
 * 指标系列数据（多输出指标）
 */
export interface IndicatorSeriesData {
  [key: string]: number[]
}

/**
 * 指标元数据
 */
export interface IndicatorMeta {
  name: string
  type: 'overlay' | 'oscillator' | 'volume' | 'momentum' | 'volatility' | 'cycle'
  description: string
  params: IndicatorParam[]
}

/**
 * 指标参数定义
 */
export interface IndicatorParam {
  name: string
  type: 'number' | 'string' | 'boolean'
  default: any
  min?: number
  max?: number
  step?: number
  description?: string
}

/**
 * 支持的指标列表响应
 */
export interface IndicatorsListResponse {
  overlay: IndicatorMeta[]
  oscillator: IndicatorMeta[]
  volume: IndicatorMeta[]
  momentum: IndicatorMeta[]
  volatility: IndicatorMeta[]
  cycle: IndicatorMeta[]
}

/**
 * MA 指标配置
 */
export interface MAConfig {
  periods: number[]
  colors?: string[]
}

/**
 * MACD 指标配置
 */
export interface MACDConfig {
  fastPeriod?: number
  slowPeriod?: number
  signalPeriod?: number
  histogramColor?: string
}

/**
 * KDJ 指标配置
 */
export interface KDJConfig {
  fastKPeriod?: number
  slowKPeriod?: number
  slowDPeriod?: number
  overbought?: number
  oversold?: number
}

/**
 * BOLL 指标配置
 */
export interface BOLLConfig {
  period?: number
  stdDev?: number
  upperColor?: string
  lowerColor?: string
}

/**
 * RSI 指标配置
 */
export interface RSIConfig {
  period?: number
  overbought?: number
  oversold?: number
}

/**
 * CCI 指标配置
 */
export interface CCIConfig {
  period?: number
  overbought?: number
  oversold?: number
}

/**
 * K线与技术指标 API
 */

import { rawApi } from './quotes'
import type { IndicatorRequest, IndicatorParamsRequest } from '@/types/indicator'

/**
 * 计算技术指标（默认参数）
 */
export async function calculateIndicators(request: IndicatorRequest) {
  const { data } = await rawApi.post<any>('/dataget/indicators/calculate', request)
  return data
}

/**
 * 计算技术指标（自定义参数）
 */
export async function calculateIndicatorsWithParams(request: IndicatorParamsRequest) {
  const { data } = await rawApi.post<any>('/dataget/indicators/calculate_with_params', request)
  return data
}

/**
 * 获取支持的指标列表
 */
export async function getIndicatorsList() {
  const { data } = await rawApi.get<any>('/dataget/indicators/list')
  return data
}

/**
 * 获取单个指标信息
 */
export async function getIndicatorInfo(indicatorName: string) {
  const { data } = await rawApi.get<any>(`/indicators/info/${indicatorName}`)
  return data
}

/**
 * 获取带指标的K线数据（便捷方法）
 */
export async function fetchKlineWithIndicators(params: {
  symbol: string
  period?: string
  count?: number
  indicators?: string[]
}) {
  const request: IndicatorRequest = {
    symbol: params.symbol,
    period: params.period || '1d',
    count: params.count || 500,
    indicators: params.indicators || ['ma5', 'ma10', 'ma20', 'ma60', 'macd', 'kdj', 'rsi', 'boll']
  }

  return calculateIndicators(request)
}

/**
 * 获取带自定义参数的指标数据
 */
export async function fetchKlineWithIndicatorParams(params: {
  symbol: string
  period?: string
  count?: number
  indicators: Record<string, Record<string, any>>
}) {
  const request: IndicatorParamsRequest = {
    symbol: params.symbol,
    period: params.period || '1d',
    count: params.count || 500,
    indicators: params.indicators
  }

  return calculateIndicatorsWithParams(request)
}

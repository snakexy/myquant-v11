/**
 * 技术指标API服务
 *
 * 遵循数据获取与计算分离架构：
 * - K线数据：/api/v1/market/kline-data
 * - 技术指标：/api/v1/market/technical-indicators
 */

export interface TechnicalIndicatorRequest {
  symbol: string
  period: string
  indicators: string[]
  params?: Record<string, any>
  count?: number
}

export interface TechnicalIndicatorResponse {
  code: number
  message: string
  data: {
    symbol: string
    period: string
    indicators: Record<string, any>
  }
  meta?: {
    data_source: string
    calc_time_ms: number
    total_time_ms: number
  }
}

export interface KlineDataRequest {
  symbol: string
  period: string
  count?: number
}

export interface KlineDataResponse {
  code: number
  message: string
  data: Array<{
    datetime: string
    open: number
    high: number
    low: number
    close: number
    volume: number
  }>
  meta?: {
    symbol: string
    period: string
    data_source: string
    count: number
    elapsed_ms: number
  }
}

/**
 * 获取K线数据（不含技术指标）
 */
export async function fetchKlineData(request: KlineDataRequest): Promise<KlineDataResponse> {
  const { symbol, period, count = 120 } = request

  const params = new URLSearchParams({
    symbol,
    period,
    count: count.toString()
  })

  const response = await fetch(`/api/v1/market/kline-data?${params.toString()}`)

  if (!response.ok) {
    throw new Error(`获取K线数据失败: ${response.statusText}`)
  }

  return await response.json()
}

/**
 * 获取技术指标
 *
 * 调用后端计算技术指标，遵循架构分离原则：
 * 1. 后端 UnifiedDataManager 获取K线数据
 * 2. 后端 TechnicalIndicators 计算技术指标
 * 3. 返回计算结果
 */
export async function fetchTechnicalIndicators(request: TechnicalIndicatorRequest): Promise<TechnicalIndicatorResponse> {
  const response = await fetch('/api/v1/market/technical-indicators', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(request)
  })

  if (!response.ok) {
    throw new Error(`获取技术指标失败: ${response.statusText}`)
  }

  return await response.json()
}

/**
 * 获取支持的技术指标列表
 */
export async function fetchSupportedIndicators(): Promise<{
  code: number
  message: string
  data: {
    trend: string[]
    oscillator: string[]
    volume: string[]
    momentum: string[]
  }
}> {
  const response = await fetch('/api/v1/market/technical-indicators/list')

  if (!response.ok) {
    throw new Error(`获取技术指标列表失败: ${response.statusText}`)
  }

  return await response.json()
}

/**
 * 默认技术指标配置
 */
export const DEFAULT_INDICATORS = {
  // 趋势指标
  MA: {
    enabled: true,
    params: [5, 10, 20, 30, 60]
  },
  BOLL: {
    enabled: true,
    params: {
      period: 20,
      nbdevup: 2.0,
      nbdevdn: 2.0
    }
  },
  // 震荡指标
  MACD: {
    enabled: true,
    params: {
      fastperiod: 12,
      slowperiod: 26,
      signalperiod: 9
    }
  },
  KDJ: {
    enabled: true,
    params: {
      n: 9,
      m1: 3,
      m2: 3
    }
  },
  RSI: {
    enabled: true,
    params: [6, 12, 24]
  }
}

/**
 * 获取默认技术指标请求
 */
export function getDefaultIndicatorRequest(symbol: string, period: string): TechnicalIndicatorRequest {
  const indicators: string[] = []
  const params: Record<string, any> = {}

  for (const [indicator, config] of Object.entries(DEFAULT_INDICATORS)) {
    if (config.enabled) {
      indicators.push(indicator)
      if (config.params) {
        params[indicator] = config.params
      }
    }
  }

  return {
    symbol,
    period,
    indicators,
    params,
    count: 1000
  }
}

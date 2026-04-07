/**
 * 技术指标API服务 - 简化版
 *
 * 遵循数据获取与计算分离架构
 */

/**
 * 获取技术指标
 *
 * @param request - 技术指标请求
 * @returns 技术指标响应
 */
export async function fetchTechnicalIndicators(request: {
  symbol: string
  period: string
  indicators: string[]
  params?: Record<string, any>
  count?: number
}): Promise<any> {
  try {
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

    const result = await response.json()
    console.log('[技术指标API] 响应:', result)
    return result
  } catch (error) {
    console.error('[技术指标API] 请求失败:', error)
    throw error
  }
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
  try {
    const response = await fetch('/api/v1/market/technical-indicators/list')

    if (!response.ok) {
      throw new Error(`获取技术指标列表失败: ${response.statusText}`)
    }

    return await response.json()
  } catch (error) {
    console.error('[技术指标列表API] 请求失败:', error)
    throw error
  }
}

/**
 * 默认技术指标配置
 */
export const DEFAULT_INDICATORS_CONFIG = {
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
export function getDefaultIndicatorRequest(symbol: string, period: string): any {
  const indicators: string[] = []
  const params: Record<string, any> = {}

  for (const [indicator, config] of Object.entries(DEFAULT_INDICATORS_CONFIG)) {
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

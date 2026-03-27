/**
 * 技术指标 Composable
 *
 * 遵循数据获取与计算分离架构：
 * - 后端计算技术指标
 * - 前端只负责渲染
 */

import { ref, computed } from 'vue'
import { fetchTechnicalIndicators, getDefaultIndicatorRequest } from '@/api/technical-indicators-simple'

export interface IndicatorData {
  MA?: Record<string, number[]>
  MACD?: {
    MACD: number[]
    Signal: number[]
    Histogram: number[]
  }
  KDJ?: {
    K: number[]
    D: number[]
    J: number[]
  }
  BOLL?: {
    upper: number[]
    middle: number[]
    lower: number[]
  }
  RSI?: Record<string, number[]>
  CCI?: {
    CCI: number[]
  }
  OBV?: {
    OBV: number[]
  }
}

export function useTechnicalIndicators() {
  // 指标数据
  const indicatorData = ref<IndicatorData>({})

  // 加载状态
  const loading = ref(false)

  // 错误信息
  const error = ref<string | null>(null)

  // 数据源信息
  const dataSource = ref<string>('unknown')

  // 计算耗时
  const calcTimeMs = ref<number>(0)
  const totalTimeMs = ref<number>(0)

  /**
   * 获取技术指标数据
   */
  async function fetchIndicators(
    symbol: string,
    period: string,
    indicators: string[] = ['MA', 'MACD', 'KDJ', 'BOLL', 'RSI'],
    params?: Record<string, any>,
    count: number = 1000
  ): Promise<boolean> {
    try {
      loading.value = true
      error.value = null

      console.log(`[技术指标] 获取 ${symbol} ${period} 指标:`, indicators)

      const request = {
        symbol,
        period,
        indicators,
        params,
        count
      }

      const response = await fetchTechnicalIndicators(request)

      if (response.code === 200 && response.data) {
        indicatorData.value = response.data.indicators
        dataSource.value = response.meta?.data_source || 'unknown'
        calcTimeMs.value = response.meta?.calc_time_ms || 0
        totalTimeMs.value = response.meta?.total_time_ms || 0

        console.log(`[技术指标] ✓ 获取成功 (${totalTimeMs.value}ms)`)
        console.log(`[技术指标] 数据源: ${dataSource.value}`)
        console.log(`[技术指标] 指标数据:`, indicatorData.value)

        return true
      } else {
        error.value = response.message || '获取技术指标失败'
        console.error('[技术指标] ✗ 获取失败:', error.value)
        return false
      }
    } catch (e: any) {
      error.value = e.message || '获取技术指标失败'
      console.error('[技术指标] ✗ 请求失败:', e)
      return false
    } finally {
      loading.value = false
    }
  }

  /**
   * 获取MA指标数据
   */
  function getMAData(period: string): number[] | null {
    if (indicatorData.value.MA && indicatorData.value.MA[`MA${period}`]) {
      return indicatorData.value.MA[`MA${period}`]
    }
    return null
  }

  /**
   * 获取MACD指标数据
   */
  function getMACDData(): { MACD: number[]; Signal: number[]; Histogram: number[] } | null {
    return indicatorData.value.MACD || null
  }

  /**
   * 获取KDJ指标数据
   */
  function getKDJData(): { K: number[]; D: number[]; J: number[] } | null {
    return indicatorData.value.KDJ || null
  }

  /**
   * 获取BOLL指标数据
   */
  function getBOLLData(): { upper: number[]; middle: number[]; lower: number[] } | null {
    return indicatorData.value.BOLL || null
  }

  /**
   * 获取RSI指标数据
   */
  function getRSIData(period: string): number[] | null {
    if (indicatorData.value.RSI && indicatorData.value.RSI[`RSI${period}`]) {
      return indicatorData.value.RSI[`RSI${period}`]
    }
    return null
  }

  /**
   * 清空指标数据
   */
  function clearIndicators() {
    indicatorData.value = {}
    error.value = null
  }

  // 计算属性：是否有数据
  const hasData = computed(() => {
    return Object.keys(indicatorData.value).length > 0
  })

  // 计算属性：是否加载中
  const isLoading = computed(() => loading.value)

  // 计算属性：是否有错误
  const hasError = computed(() => error.value !== null)

  return {
    // 状态
    indicatorData,
    loading,
    error,
    dataSource,
    calcTimeMs,
    totalTimeMs,

    // 计算属性
    hasData,
    isLoading,
    hasError,

    // 方法
    fetchIndicators,
    getMAData,
    getMACDData,
    getKDJData,
    getBOLLData,
    getRSIData,
    clearIndicators
  }
}

/**
 * useMiniCharts - 迷你分时图数据管理 Composable
 *
 * 用于加载自选股列表的 1 分钟收盘价数据，显示小型折线图
 * 符合 V5 架构：通过统一接口获取数据
 */

import { ref, computed, type Ref } from 'vue'
import { fetchKline, type KlineItem } from '@/api/modules/quotes'

export interface MiniChartData {
  time: Date
  close: number
}

export interface MiniChartsOptions {
  /** 请求的分钟数据条数（默认240，全天交易分钟） */
  count?: number
  /** 最少数据条数（默认5） */
  minDataPoints?: number
}

export interface MiniChartsResult {
  /** 股票代码 → 迷你图数据 */
  data: Ref<Map<string, MiniChartData[]>>
  /** 加载状态 */
  loading: Ref<boolean>
  /** 加载迷你图数据 */
  loadMiniCharts: (symbols: string[]) => Promise<void>
  /** 清空数据 */
  clear: () => void
  /** 获取指定股票的迷你图数据 */
  getData: (symbol: string) => MiniChartData[]
  /** 是否有数据 */
  hasData: (symbol: string) => boolean
}

/**
 * 迷你分时图数据管理 Composable
 *
 * @example
 * const { data, loading, loadMiniCharts, getData } = useMiniCharts()
 *
 * // 加载所有自选股的迷你图
 * await loadMiniCharts(['600519.SH', '000001.SZ'])
 *
 * // 获取指定股票的数据
 * const chartData = getData('600519.SH')
 */
export function useMiniCharts(options: MiniChartsOptions = {}) {
  const {
    count = 240,
    minDataPoints = 5
  } = options

  const loading = ref(false)
  const data = ref<Map<string, MiniChartData[]>>(new Map())

  /**
   * 加载迷你图数据
   *
   * @param symbols - 股票代码列表
   */
  const loadMiniCharts = async (symbols: string[]): Promise<void> => {
    if (!symbols || symbols.length === 0) {
      console.log('[useMiniCharts] 无股票需要加载')
      return
    }

    loading.value = true
    console.log(`[useMiniCharts] 加载迷你分时图: ${symbols.length} 只股票`)

    const tasks = symbols.map(async (symbol) => {
      try {
        const res = await fetchKline(symbol, '1m', count, 'none')

        if (res.data && res.data.length >= minDataPoints) {
          // 转换为带时间戳的数据，并按时间排序
          const barsWithTime = res.data
            .map((b: KlineItem) => ({
              time: new Date(Number(b.time)),
              close: Number(b.close)
            }))
            .sort((a, b) => a.time.getTime() - b.time.getTime())

          // 简化处理：直接使用最后的数据（不做过滤）
          // 如果数据时间戳异常（如1970年），直接使用所有数据
          data.value.set(symbol, barsWithTime)

          console.log(`[useMiniCharts] ${symbol} 加载成功: ${barsWithTime.length} 条数据`)
        } else {
          data.value.set(symbol, [])
          console.log(`[useMiniCharts] ${symbol} 无数据`)
        }
      } catch (error) {
        console.error(`[useMiniCharts] ${symbol} 加载失败:`, error)
        data.value.set(symbol, [])
      }
    })

    await Promise.all(tasks)
    loading.value = false
    console.log('[useMiniCharts] 迷你图加载完成')
  }

  /**
   * 清空所有数据
   */
  const clear = (): void => {
    data.value.clear()
  }

  /**
   * 获取指定股票的迷你图数据
   */
  const getData = (symbol: string): MiniChartData[] => {
    return data.value.get(symbol) || []
  }

  /**
   * 检查是否有数据
   */
  const hasData = (symbol: string): boolean => {
    const chartData = data.value.get(symbol)
    return chartData ? chartData.length > 0 : false
  }

  return {
    data,
    loading,
    loadMiniCharts,
    clear,
    getData,
    hasData
  }
}

/**
 * 迷你图 SVG polyline points 生成工具
 *
 * @param data - 迷你图数据
 * @param width - SVG 宽度（默认120）
 * @param height - SVG 高度（默认28）
 *
 * @example
 * const points = generateSparklinePoints(chartData, 120, 28)
 * <polyline :points="points" ... />
 */
export function generateSparklinePoints(
  data: MiniChartData[],
  width: number = 120,
  height: number = 28
): string {
  if (!data || data.length < 2) return ''

  // A股交易时间：240个1分钟K线
  // 上午：9:30-11:30（120分钟）
  // 下午：13:00-15:00（120分钟）
  const TRADING_MINUTES = 240

  // 获取价格范围
  const prices = data.map(d => d.close)
  const minPrice = Math.min(...prices)
  const maxPrice = Math.max(...prices)
  const priceRange = maxPrice - minPrice || 1

  // 计算每个点的坐标
  return data
    .map(d => {
      // X轴：按交易分钟数映射
      const minutesFromOpen = (d.time.getHours() - 9) * 60 + d.time.getMinutes() - 30
      const x = Math.round((minutesFromOpen / TRADING_MINUTES) * width)

      // Y轴：价格映射（反转，高价格在上）
      const y = height - Math.round(((d.close - minPrice) / priceRange) * height)

      return `${x},${y}`
    })
    .join(' ')
}

/**
 * Supertrend超级趋势指标（叠加在主图）
 */
import { Supertrend } from 'lightweight-charts-indicators'
import type { Bar } from 'oakscriptjs'
import type { IChartApi, ISeriesApi } from 'lightweight-charts'
import { LineSeries, CandlestickSeries } from 'lightweight-charts'

interface SupertrendConfig {
  period: number
  multiplier: number
}

/**
 * 添加Supertrend指标
 * @param chart 图表实例
 * @param overlaySeries 主图叠加系列Map
 * @param bars K线数据
 * @param config Supertrend配置
 */
export async function addSupertrendIndicator(
  chart: IChartApi | null,
  overlaySeries: Map<string, ISeriesApi<'Line' | 'Candlestick'>>,
  bars: Bar[],
  config: SupertrendConfig
) {
  // 使用官方指标库计算
  const stResult = Supertrend.calculate(bars, {
    period: config.period,
    multiplier: config.multiplier,
  })

  // 过滤NaN值
  const validTrend = stResult.plots.plot0.filter((item: any) =>
    item.value != null && !isNaN(item.value)
  )

  // 【v9.2.1 修复】获取或创建series
  let trendSeries = overlaySeries.get('SUPERTREND')

  if (!trendSeries) {
    console.log('[SUPERTREND指标] 创建新的系列（主图 pane 0）')
    trendSeries = chart!.addSeries(LineSeries, {
      color: '#26A69A',
      lineWidth: 2,
      title: 'SuperTrend',
      lastValueVisible: true,
      priceLineVisible: false,
    }, 0)  // pane 0 是主图
    overlaySeries.set('SUPERTREND', trendSeries)
  }

  if (trendSeries) {
    trendSeries.setData(validTrend)
    console.log(`[SUPERTREND指标] ✓ 数据已设置，数据点: ${validTrend.length}`)
  }
}

/**
 * 默认Supertrend配置
 */
export function getSupertrendConfig(): SupertrendConfig {
  return {
    period: 10,
    multiplier: 3,
  }
}

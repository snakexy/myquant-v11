/**
 * BOLL布林带指标（叠加在主图）

【v9.2.1 修复】自动创建主图叠加系列
*/
import { BollingerBands } from 'lightweight-charts-indicators'
import { LineSeries } from 'lightweight-charts'
import type { Bar } from 'oakscriptjs'
import type { IChartApi, ISeriesApi } from 'lightweight-charts'

/**
 * 添加BOLL布林带指标
 * @param chart 图表实例
 * @param overlaySeries 主图叠加系列Map
 * @param bars K线数据
 */
export async function addBOLLIndicator(
  chart: IChartApi | null,
  overlaySeries: Map<string, ISeriesApi<'Line'>>,
  bars: Bar[]
) {
  // 使用官方指标库计算
  const bollResult = BollingerBands.calculate(bars, {
    length: 20,
    mult: 2,
  })

  // 过滤NaN值
  const validUpper = bollResult.plots.plot0.filter((item: any) =>
    item.value != null && !isNaN(item.value)
  )
  const validMiddle = bollResult.plots.plot1.filter((item: any) =>
    item.value != null && !isNaN(item.value)
  )
  const validLower = bollResult.plots.plot2.filter((item: any) =>
    item.value != null && !isNaN(item.value)
  )

  // 【v9.2.1 修复】获取或创建series
  let upperSeries = overlaySeries.get('BOLL_UPPER')
  let middleSeries = overlaySeries.get('BOLL_MIDDLE')
  let lowerSeries = overlaySeries.get('BOLL_LOWER')

  if (!upperSeries) {
    console.log('[BOLL指标] 创建 UPPER 系列（主图 pane 0）')
    upperSeries = chart!.addSeries(LineSeries, {
      color: '#FF9800',
      lineWidth: 1,
      lineStyle: 2, // Dashed
      title: 'BOLL Upper',
      lastValueVisible: true,
      priceLineVisible: false,
    }, 0)
    overlaySeries.set('BOLL_UPPER', upperSeries)
  }

  if (!middleSeries) {
    console.log('[BOLL指标] 创建 MIDDLE 系列（主图 pane 0）')
    middleSeries = chart!.addSeries(LineSeries, {
      color: '#9E9E9E',
      lineWidth: 1,
      title: 'BOLL Middle',
      lastValueVisible: false,
      priceLineVisible: false,
    }, 0)
    overlaySeries.set('BOLL_MIDDLE', middleSeries)
  }

  if (!lowerSeries) {
    console.log('[BOLL指标] 创建 LOWER 系列（主图 pane 0）')
    lowerSeries = chart!.addSeries(LineSeries, {
      color: '#FF9800',
      lineWidth: 1,
      lineStyle: 2, // Dashed
      title: 'BOLL Lower',
      lastValueVisible: true,
      priceLineVisible: false,
    }, 0)
    overlaySeries.set('BOLL_LOWER', lowerSeries)
  }

  // 设置数据
  upperSeries.setData(validUpper)
  middleSeries.setData(validMiddle)
  lowerSeries.setData(validLower)

  console.log(`[BOLL指标] ✓ 数据已设置: UPPER=${validUpper.length}, MIDDLE=${validMiddle.length}, LOWER=${validLower.length}`)
}

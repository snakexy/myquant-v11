/**
 * ATR指标（独立窗格pane 6）
 */
import { ATR } from 'lightweight-charts-indicators'
import type { Bar } from 'oakscriptjs'
import type { IChartApi, ISeriesApi } from 'lightweight-charts'
import { HistogramSeries } from 'lightweight-charts'

/**
 * 添加ATR指标
 * @param chart 图表实例
 * @param bars K线数据
 * @param indicatorPanes 窗格指标Map
 * @param paneIndex 窗格索引
 */
export async function addATRIndicator(
  chart: IChartApi | null,
  bars: Bar[],
  indicatorPanes: Map<number, ISeriesApi[]>,
  paneIndex: number = 6
) {
  if (!chart) return

  // 使用官方指标库计算
  const atrResult = ATR.calculate(bars, { length: 14 })

  const atrSeries = chart.addSeries(HistogramSeries, {
    color: '#4CAF50',
    priceFormat: { type: 'price', precision: 2 },
  }, paneIndex)

  atrSeries.setData(atrResult.plots.plot0.filter((item: any) => item.value != null && !isNaN(item.value)))

  indicatorPanes.set(paneIndex, [atrSeries])

  const atrPane = chart.panes()[paneIndex]
  if (atrPane) {
    atrPane.setHeight(120)
  }
}

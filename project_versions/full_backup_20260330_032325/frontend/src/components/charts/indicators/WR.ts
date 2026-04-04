/**
 * Williams %R指标（独立窗格pane 5）
 */
import { WilliamsPercentRange } from 'lightweight-charts-indicators'
import type { Bar } from 'oakscriptjs'
import type { IChartApi, ISeriesApi } from 'lightweight-charts'
import { LineSeries } from 'lightweight-charts'

/**
 * 添加Williams %R指标
 * @param chart 图表实例
 * @param bars K线数据
 * @param indicatorPanes 窗格指标Map
 * @param paneIndex 窗格索引
 */
export async function addWRIndicator(
  chart: IChartApi | null,
  bars: Bar[],
  indicatorPanes: Map<number, ISeriesApi[]>,
  paneIndex: number = 5
) {
  if (!chart) return

  // 使用官方指标库计算
  const wrResult = WilliamsPercentRange.calculate(bars, { length: 14 })

  const wrSeries = chart.addSeries(LineSeries, {
    color: '#2196F3',
    lineWidth: 1,
    title: 'Williams %R',
  }, paneIndex)

  wrSeries.setData(wrResult.plots.plot0.filter((item: any) => item.value != null && !isNaN(item.value)))

  indicatorPanes.set(paneIndex, [wrSeries])

  const wrPane = chart.panes()[paneIndex]
  if (wrPane) {
    wrPane.setHeight(120)
  }
}

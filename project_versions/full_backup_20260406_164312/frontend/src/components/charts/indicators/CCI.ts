/**
 * CCI指标（独立窗格pane 4）
 */
import { CCI } from 'lightweight-charts-indicators'
import type { Bar } from 'oakscriptjs'
import type { IChartApi, ISeriesApi } from 'lightweight-charts'
import { LineSeries } from 'lightweight-charts'

/**
 * 添加CCI指标
 * @param chart 图表实例
 * @param bars K线数据
 * @param indicatorPanes 窗格指标Map
 * @param paneIndex 窗格索引
 */
export async function addCCIIndicator(
  chart: IChartApi | null,
  bars: Bar[],
  indicatorPanes: Map<number, ISeriesApi[]>,
  paneIndex: number = 4
) {
  if (!chart) return

  // 使用官方指标库计算
  const cciResult = CCI.calculate(bars, { length: 14 })

  const cciSeries = chart.addSeries(LineSeries, {
    color: '#FF9800',
    lineWidth: 1,
    title: 'CCI',
  }, paneIndex)

  cciSeries.setData(cciResult.plots.plot0.filter((item: any) => item.value != null && !isNaN(item.value)))

  indicatorPanes.set(paneIndex, [cciSeries])

  const cciPane = chart.panes()[paneIndex]
  if (cciPane) {
    cciPane.setHeight(120)
  }
}

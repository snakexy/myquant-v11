/**
 * OBV指标（独立窗格pane 7）
 */
import { OBV } from 'lightweight-charts-indicators'
import type { Bar } from 'oakscriptjs'
import type { IChartApi, ISeriesApi } from 'lightweight-charts'
import { LineSeries } from 'lightweight-charts'

/**
 * 添加OBV指标
 * @param chart 图表实例
 * @param bars K线数据
 * @param indicatorPanes 窗格指标Map
 * @param paneIndex 窗格索引
 */
export async function addOBVIndicator(
  chart: IChartApi | null,
  bars: Bar[],
  indicatorPanes: Map<number, ISeriesApi[]>,
  paneIndex: number = 7
) {
  if (!chart) return

  // 使用官方指标库计算
  const obvResult = OBV.calculate(bars)

  const obvSeries = chart.addSeries(LineSeries, {
    color: '#00BCD4',
    lineWidth: 1,
    title: 'OBV',
  }, paneIndex)

  obvSeries.setData(obvResult.plots.plot0.filter((item: any) => item.value != null && !isNaN(item.value)))

  indicatorPanes.set(paneIndex, [obvSeries])

  const obvPane = chart.panes()[paneIndex]
  if (obvPane) {
    obvPane.setHeight(120)
  }
}

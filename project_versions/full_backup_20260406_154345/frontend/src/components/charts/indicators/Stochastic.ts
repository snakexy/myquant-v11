/**
 * Stochastic随机振荡器指标（独立窗格）
 */
import { Stochastic } from 'lightweight-charts-indicators'
import type { Bar } from 'oakscriptjs'
import type { IChartApi, ISeriesApi } from 'lightweight-charts'
import { LineSeries } from 'lightweight-charts'

/**
 * 添加Stochastic指标
 * @param chart 图表实例
 * @param bars K线数据
 * @param indicatorPanes 窗格指标Map
 * @param paneIndex 窗格索引
 */
export async function addStochasticIndicator(
  chart: IChartApi | null,
  bars: Bar[],
  indicatorPanes: Map<number, ISeriesApi[]>,
  paneIndex: number = 2
) {
  if (!chart) return

  // 使用官方指标库计算
  const stochResult = Stochastic.calculate(bars, {
    kPeriod: 14,
    dPeriod: 3,
    smoothK: 3,
  })

  // 在指定pane中创建系列
  const kSeries = chart.addSeries(LineSeries, {
    color: '#26A69A',
    lineWidth: 2,
    title: '%K',
  }, paneIndex)

  const dSeries = chart.addSeries(LineSeries, {
    color: '#FF6B6B',
    lineWidth: 2,
    title: '%D',
  }, paneIndex)

  // 过滤NaN值并设置数据
  const validKData = stochResult.plots.plot0.filter((item: any) =>
    item.value != null && !isNaN(item.value)
  )
  const validDData = stochResult.plots.plot1.filter((item: any) =>
    item.value != null && !isNaN(item.value)
  )

  kSeries.setData(validKData)
  dSeries.setData(validDData)

  // 保存到映射
  indicatorPanes.set(paneIndex, [kSeries, dSeries])

  // 设置pane高度
  const stochPane = chart.panes()[paneIndex]
  if (stochPane) {
    stochPane.setHeight(150)
  }
}

/**
 * ADX/DMI平均趋向指数指标（独立窗格）
 */
import { DMI } from 'lightweight-charts-indicators'
import type { Bar } from 'oakscriptjs'
import type { IChartApi, ISeriesApi } from 'lightweight-charts'
import { LineSeries } from 'lightweight-charts'

/**
 * 添加ADX/DMI指标
 * @param chart 图表实例
 * @param bars K线数据
 * @param indicatorPanes 窗格指标Map
 * @param paneIndex 窗格索引
 */
export async function addADXIndicator(
  chart: IChartApi | null,
  bars: Bar[],
  indicatorPanes: Map<number, ISeriesApi[]>,
  paneIndex: number = 3
) {
  if (!chart) return

  // 使用官方指标库计算
  const dmiResult = DMI.calculate(bars, {
    len: 14,
    lensig: 14,
  })

  // 在指定pane中创建系列
  const adxSeries = chart.addSeries(LineSeries, {
    color: '#FFFFFF',
    lineWidth: 2,
    title: 'ADX',
  }, paneIndex)

  const diPlusSeries = chart.addSeries(LineSeries, {
    color: '#26A69A',
    lineWidth: 2,
    title: '+DI',
  }, paneIndex)

  const diMinusSeries = chart.addSeries(LineSeries, {
    color: '#FF6B6B',
    lineWidth: 2,
    title: '-DI',
  }, paneIndex)

  // 过滤NaN值并设置数据
  const validADXData = dmiResult.plots.plot0.filter((item: any) =>
    item.value != null && !isNaN(item.value)
  )
  const validDIPlusData = dmiResult.plots.plot1.filter((item: any) =>
    item.value != null && !isNaN(item.value)
  )
  const validDIMinusData = dmiResult.plots.plot2.filter((item: any) =>
    item.value != null && !isNaN(item.value)
  )

  adxSeries.setData(validADXData)
  diPlusSeries.setData(validDIPlusData)
  diMinusSeries.setData(validDIMinusData)

  // 保存到映射
  indicatorPanes.set(paneIndex, [adxSeries, diPlusSeries, diMinusSeries])

  // 设置pane高度
  const adxPane = chart.panes()[paneIndex]
  if (adxPane) {
    adxPane.setHeight(150)
  }
}

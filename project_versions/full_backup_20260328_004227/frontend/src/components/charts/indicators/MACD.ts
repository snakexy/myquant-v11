/**
 * MACD指标（独立窗格pane 1）
 */
import { MACD } from 'lightweight-charts-indicators'
import type { Bar } from 'oakscriptjs'
import type { IChartApi, ISeriesApi } from 'lightweight-charts'
import { LineSeries, HistogramSeries } from 'lightweight-charts'

/**
 * 添加MACD指标
 * @param chart 图表实例
 * @param bars K线数据
 * @param indicatorPanes 窗格指标Map
 * @param paneIndex 窗格索引
 * @param paneHeight 窗格高度（可选，默认200）
 */
export async function addMACDIndicator(
  chart: IChartApi | null,
  bars: Bar[],
  indicatorPanes: Map<number, ISeriesApi[]>,
  paneIndex: number = 1,
  paneHeight: number = 200
) {
  if (!chart) return

  // 使用官方指标库计算
  const macdResult = MACD.calculate(bars, {
    fastLength: 12,
    slowLength: 26,
    signalLength: 9,
  })

  // 在指定pane中创建系列
  const macdSeries = chart.addSeries(LineSeries, {
    color: '#26A69A',
    lineWidth: 2,
    title: 'MACD',
    lastValueVisible: true,   // 显示右边数值标签
    priceLineVisible: false,  // 隐藏价格线（横虚线）
  }, paneIndex)

  const signalSeries = chart.addSeries(LineSeries, {
    color: '#FF6B6B',
    lineWidth: 2,
    title: 'Signal',
    lastValueVisible: true,   // 显示右边数值标签
    priceLineVisible: false,  // 隐藏价格线（横虚线）
  }, paneIndex)

  const histogramSeries = chart.addSeries(HistogramSeries, {
    priceFormat: { type: 'price', precision: 2 },
    lastValueVisible: true,   // 显示右边数值标签
    priceLineVisible: false,  // 隐藏价格线（横虚线）
  }, paneIndex)

  macdSeries.setData(macdResult.plots.plot0.filter((item: any) => item.value != null && !isNaN(item.value)))
  signalSeries.setData(macdResult.plots.plot1.filter((item: any) => item.value != null && !isNaN(item.value)))

  // 柱状图需要根据正负值设置颜色
  const histogramData = macdResult.plots.plot2.map((item: any) => ({
    time: item.time,
    value: item.value,
    color: item.value >= 0 ? '#ef4444' : '#10b981',
  }))
  histogramSeries.setData(histogramData)

  // 保存到映射
  indicatorPanes.set(paneIndex, [macdSeries, signalSeries, histogramSeries])

  // ✅ 设置pane高度（使用传入的高度参数）
  const macdPane = chart.panes()[paneIndex]
  if (macdPane) {
    macdPane.setHeight(paneHeight)
  }
}

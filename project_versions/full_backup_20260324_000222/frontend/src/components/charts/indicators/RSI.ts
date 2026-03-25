/**
 * RSI指标（独立窗格pane 2）
 */
import { RSI } from 'lightweight-charts-indicators'
import type { Bar } from 'oakscriptjs'
import type { IChartApi, ISeriesApi } from 'lightweight-charts'
import { LineSeries } from 'lightweight-charts'

/**
 * 添加RSI指标
 * @param chart 图表实例
 * @param bars K线数据
 * @param indicatorPanes 窗格指标Map
 * @param paneIndex 窗格索引
 * @param paneHeight 窗格高度（可选，默认200）
 */
export async function addRSIIndicator(
  chart: IChartApi | null,
  bars: Bar[],
  indicatorPanes: Map<number, ISeriesApi[]>,
  paneIndex: number = 2,
  paneHeight: number = 200
) {
  if (!chart) return

  // 使用官方指标库计算
  const rsi6Result = RSI.calculate(bars, { length: 6, src: 'close' })
  const rsi12Result = RSI.calculate(bars, { length: 12, src: 'close' })
  const rsi24Result = RSI.calculate(bars, { length: 24, src: 'close' })

  const rsi6Series = chart.addSeries(LineSeries, {
    color: '#9C27B0',
    lineWidth: 1,
    title: 'RSI 6',
    lastValueVisible: true,   // 显示右边数值标签
    priceLineVisible: false,  // 隐藏价格线（横虚线）
  }, paneIndex)

  const rsi12Series = chart.addSeries(LineSeries, {
    color: '#E91E63',
    lineWidth: 1,
    title: 'RSI 12',
    lastValueVisible: true,   // 显示右边数值标签
    priceLineVisible: false,  // 隐藏价格线（横虚线）
  }, paneIndex)

  const rsi24Series = chart.addSeries(LineSeries, {
    color: '#673AB7',
    lineWidth: 1,
    title: 'RSI 24',
    lastValueVisible: true,   // 显示右边数值标签
    priceLineVisible: false,  // 隐藏价格线（横虚线）
  }, paneIndex)

  rsi6Series.setData(rsi6Result.plots.plot0.filter((item: any) => item.value != null && !isNaN(item.value)))
  rsi12Series.setData(rsi12Result.plots.plot0.filter((item: any) => item.value != null && !isNaN(item.value)))
  rsi24Series.setData(rsi24Result.plots.plot0.filter((item: any) => item.value != null && !isNaN(item.value)))

  indicatorPanes.set(paneIndex, [rsi6Series, rsi12Series, rsi24Series])

  // ✅ 设置pane高度（使用传入的高度参数）
  const rsiPane = chart.panes()[paneIndex]
  if (rsiPane) {
    rsiPane.setHeight(paneHeight)
  }
}

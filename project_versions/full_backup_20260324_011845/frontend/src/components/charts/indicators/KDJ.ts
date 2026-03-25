/**
 * KDJ指标（独立窗格pane 3）
 * 中国股市常用KDJ格式：K、D、J三条线
 * J = 3×K - 2×D
 */
import { Stochastic } from 'lightweight-charts-indicators'
import type { Bar } from 'oakscriptjs'
import type { IChartApi, ISeriesApi } from 'lightweight-charts'
import { LineSeries } from 'lightweight-charts'

/**
 * 添加KDJ指标
 * @param chart 图表实例
 * @param bars K线数据
 * @param indicatorPanes 窗格指标Map
 * @param paneIndex 窗格索引
 * @param paneHeight 窗格高度（可选，默认200）
 */
export async function addKDJIndicator(
  chart: IChartApi | null,
  bars: Bar[],
  indicatorPanes: Map<number, ISeriesApi[]>,
  paneIndex: number = 3,
  paneHeight: number = 200
) {
  if (!chart) return

  // 使用官方Stochastic指标计算K、D
  const stochResult = Stochastic.calculate(bars, {
    k: 9,
    d: 3,
    smooth: 3,
  })

  // 合并K、D数据，确保时间点对应
  const kData = stochResult.plots.plot0.filter((item: any) => item.value != null && !isNaN(item.value))
  const dData = stochResult.plots.plot1.filter((item: any) => item.value != null && !isNaN(item.value))

  // 创建时间点映射
  const kMap = new Map(kData.map((item: any) => [item.time, item.value]))
  const dMap = new Map(dData.map((item: any) => [item.time, item.value]))

  // 计算J线：J = 3*K - 2*D（只在K和D都有值的时间点计算）
  const jData: any[] = []
  kMap.forEach((kValue, time) => {
    const dValue = dMap.get(time)
    if (dValue !== undefined) {
      const jValue = 3 * kValue - 2 * dValue
      jData.push({ time, value: jValue })
    }
  })

  const kSeries = chart.addSeries(LineSeries, {
    color: '#FFEB3B',  // 黄色
    lineWidth: 1,
    title: 'K',
  }, paneIndex)

  const dSeries = chart.addSeries(LineSeries, {
    color: '#9E9E9E',  // 灰色
    lineWidth: 1,
    title: 'D',
  }, paneIndex)

  const jSeries = chart.addSeries(LineSeries, {
    color: '#E91E63',  // 紫色 J线
    lineWidth: 1,
    title: 'J',
  }, paneIndex)

  kSeries.setData(kData)
  dSeries.setData(dData)
  jSeries.setData(jData.filter((item: any) => item.value != null && !isNaN(item.value)))

  indicatorPanes.set(paneIndex, [kSeries, dSeries, jSeries])

  // ✅ 设置pane高度（使用传入的高度参数）
  const kdjPane = chart.panes()[paneIndex]
  if (kdjPane) {
    kdjPane.setHeight(paneHeight)
  }
}

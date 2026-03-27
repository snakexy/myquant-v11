/**
 * VWAP成交量加权平均价指标（叠加在主图）
 *
 * 【v9.2.1 新增】支持主图叠加
 *
 * ⚠️ 注意：lightweight-charts-indicators@0.1.0 未导出VWAP
 * 此文件暂时禁用，待更新indicators包或手动实现
 */
// import { VWAP } from 'lightweight-charts-indicators'
import { LineSeries } from 'lightweight-charts'
import type { Bar } from 'oakscriptjs'
import type { IChartApi, ISeriesApi } from 'lightweight-charts'

/**
 * 添加VWAP指标
 * @param chart 图表实例
 * @param overlaySeries 主图叠加系列Map
 * @param bars K线数据
 */
export async function addVWAPIndicator(
  chart: IChartApi | null,
  overlaySeries: Map<string, ISeriesApi<'Line'>>,
  bars: Bar[]
) {
  // ⚠️ 临时禁用：lightweight-charts-indicators@0.1.0 未导出VWAP
  console.warn('[VWAP指标] 暂时禁用：indicators包未导出VWAP')
  return

  // 原始代码（待indicators包更新后恢复）
  /*
  if (!chart || bars.length === 0) return

  // 使用官方指标库计算
  const vwapResult = VWAP.calculate(bars)

  // 过滤NaN值
  const validVWAP = vwapResult.plots.plot0.filter((item: any) =>
    item.value != null && !isNaN(item.value)
  )

  // 【v9.2.1 修复】获取或创建series
  let vwapSeries = overlaySeries.get('VWAP')

  if (!vwapSeries) {
    console.log('[VWAP指标] 创建新的系列（主图 pane 0）')
    vwapSeries = chart.addSeries(LineSeries, {
      color: '#9C27B0',
      lineWidth: 2,
      title: 'VWAP',
      lastValueVisible: true,
      priceLineVisible: false,
    }, 0)  // pane 0 是主图
    overlaySeries.set('VWAP', vwapSeries)
  }

  if (vwapSeries) {
    vwapSeries.setData(validVWAP)
    console.log(`[VWAP指标] ✓ 数据已设置，数据点: ${validVWAP.length}`)
  }
  */
}

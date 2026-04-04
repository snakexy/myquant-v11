/**
 * PSAR抛物线指标（叠加在主图）
 *
 * 【v9.2.1 新增】支持主图叠加
 *
 * ⚠️ 注意：lightweight-charts-indicators@0.1.0 未导出PSAR
 * 此文件暂时禁用，待更新indicators包或手动实现
 */
// import { PSAR } from 'lightweight-charts-indicators'
import { LineSeries } from 'lightweight-charts'
import type { Bar } from 'oakscriptjs'
import type { IChartApi, ISeriesApi } from 'lightweight-charts'

/**
 * 添加PSAR指标
 * @param chart 图表实例
 * @param overlaySeries 主图叠加系列Map
 * @param bars K线数据
 */
export async function addPSARIndicator(
  chart: IChartApi | null,
  overlaySeries: Map<string, ISeriesApi<'Line'>>,
  bars: Bar[]
) {
  // ⚠️ 临时禁用：lightweight-charts-indicators@0.1.0 未导出PSAR
  console.warn('[PSAR指标] 暂时禁用：lightweight-charts-indicators包未导出PSAR')
  return

  // 原始代码（待indicators包更新后恢复）
  /*
  if (!chart || bars.length === 0) return

  // 使用官方指标库计算
  const psarResult = PSAR.calculate(bars, {
    step: 0.02,
    max: 0.2,
  })

  // 过滤NaN值
  const validPSAR = psarResult.plots.plot0.filter((item: any) =>
    item.value != null && !isNaN(item.value)
  )

  // 【v9.2.1 修复】获取或创建series
  let psarSeries = overlaySeries.get('PSAR')

  if (!psarSeries) {
    console.log('[PSAR指标] 创建新的系列（主图 pane 0）')
    psarSeries = chart.addSeries(LineSeries, {
      color: '#FF5252',
      lineWidth: 1,
      title: 'PSAR',
      lastValueVisible: true,
      priceLineVisible: false,
    }, 0)  // pane 0 是主图
    overlaySeries.set('PSAR', psarSeries)
  }

  if (psarSeries) {
    psarSeries.setData(validPSAR)
    console.log(`[PSAR指标] ✓ 数据已设置，数据点: ${validPSAR.length}`)
  }
  */
}
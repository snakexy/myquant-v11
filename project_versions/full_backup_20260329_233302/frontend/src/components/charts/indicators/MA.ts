/**
 * MA均线指标（叠加在主图）

【v9.2.0 新增】支持后端预计算的指标数据
【v9.2.1 修复】自动创建主图叠加系列
*/
import { SMA } from 'lightweight-charts-indicators'
import { LineSeries } from 'lightweight-charts'
import type { Bar } from 'oakscriptjs'
import type { IChartApi, ISeriesApi } from 'lightweight-charts'

interface MAConfig {
  key: string
  period: number
  color: string
}

/**
 * 添加MA均线指标

【v9.2.0】优先使用后端计算的数据，如果没有则本地计算
 * @param chart 图表实例
 * @param overlaySeries 主图叠加系列Map
 * @param bars K线数据
 * @param config MA配置
 */
export async function addMAIndicator(
  chart: IChartApi | null,
  overlaySeries: Map<string, ISeriesApi<'Line'>>,
  bars: Bar[],
  config: MAConfig
) {
  const { key, period } = config

  // 【v9.2.0 新增】检查后端是否已提供指标数据
  const backendField = key.toLowerCase()  // MA5 → ma5
  const hasBackendData = bars.length > 0 && (bars[0] as any)[backendField] !== undefined

  let validData: any[]

  if (hasBackendData) {
    // 使用后端计算的数据
    console.log(`[MA指标] 使用后端计算的 ${key} 数据，样本数据:`, {
      firstBar: {
        time: (bars[0] as any).time,
        timestamp: (bars[0] as any).timestamp,
        [backendField]: (bars[0] as any)[backendField]
      },
      barsLength: bars.length
    })

    validData = bars
      .filter((bar: any) => {
        const hasValue = bar[backendField] != null && !isNaN(bar[backendField])
        const hasTime = bar.time !== undefined && bar.time !== null
        if (!hasValue && hasTime) {
          console.debug(`[MA指标] 过滤掉无指标值的K线: time=${bar.time}, value=${bar[backendField]}`)
        }
        return hasValue && hasTime
      })
      .map((bar: any) => {
        // 确保time是lightweight-charts期望的格式（秒级Unix时间戳或时间对象）
        let time = bar.time
        // 如果time是数字，确保它是秒级时间戳（有些情况下可能是毫秒）
        if (typeof time === 'number') {
          // 如果大于10位数字（毫秒时间戳），转换为秒
          if (time > 10000000000) {
            time = Math.floor(time / 1000)
            console.debug(`[MA指标] 转换时间戳: ${bar.time} -> ${time}`)
          }
        }
        return {
          time: time,
          value: Number(bar[backendField])
        }
      })
    console.log(`[MA指标] 后端数据转换完成，有效数据点: ${validData.length}/${bars.length}`)
  } else {
    // 回退到本地计算
    console.log(`[MA指标] 本地计算 ${key} 数据`)
    const smaResult = SMA.calculate(bars, { len: period, src: 'close' })
    validData = smaResult.plots.plot0.filter((item: any) =>
      item.value != null && !isNaN(item.value)
    )
  }

  // 【v9.2.1 修复】获取或创建series
  let series = overlaySeries.get(key)

  if (!series) {
    // Series不存在，需要创建（pane 0 是主图）
    console.log(`[MA指标] 创建新的 ${key} 系列（主图 pane 0）`)
    series = chart!.addSeries(LineSeries, {
      color: config.color,
      lineWidth: 1,
      title: key,
      lastValueVisible: true,
      priceLineVisible: false,
    }, 0)  // ✅ 明确指定 pane 0（主图）
    overlaySeries.set(key, series)
  }

  if (series) {
    series.setData(validData)
    console.log(`[MA指标] ✓ ${key} 数据已设置，数据点: ${validData.length}`)
  } else {
    console.error(`[MA指标] ✗ 无法创建 ${key} 系列`)
  }
}

/**
 * MA配置映射
 */
export const MA_PERIODS: Record<string, number> = {
  'MA5': 5,
  'MA10': 10,
  'MA20': 20,
  'MA30': 30,
  'MA60': 60
}

/**
 * 获取MA指标配置
 */
export function getMAConfigs(colors: Record<string, string>): MAConfig[] {
  return [
    { key: 'MA5', period: 5, color: colors.ma5Color },
    { key: 'MA10', period: 10, color: colors.ma10Color },
    { key: 'MA20', period: 20, color: colors.ma20Color },
    { key: 'MA30', period: 30, color: colors.ma30Color },
    { key: 'MA60', period: 60, color: colors.ma60Color }
  ]
}

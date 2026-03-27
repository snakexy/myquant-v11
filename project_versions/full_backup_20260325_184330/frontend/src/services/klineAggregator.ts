/**
 * K线周期聚合器
 *
 * 将1分钟线实时聚合为5m/15m/30m/60m/日线
 * 用于WebSocket实时推送场景
 */

import type { KlineBar } from './klineWebSocket'

export type Timeframe = '1m' | '5m' | '15m' | '30m' | '1h' | '1d' | '1w' | '1M'

interface AggregatedBar {
  time: number
  open: number
  high: number
  low: number
  close: number
  volume: number
  timestamp: number // 内部使用的Unix时间戳
}

/**
 * 获取时间戳对应的周期开始时间
 */
function getPeriodStart(timestamp: number, timeframe: Timeframe): number {
  const date = new Date(timestamp * 1000)

  switch (timeframe) {
    case '1m':
      date.setSeconds(0, 0)
      break
    case '5m':
      date.setMinutes(Math.floor(date.getMinutes() / 5) * 5, 0, 0)
      break
    case '15m':
      date.setMinutes(Math.floor(date.getMinutes() / 15) * 15, 0, 0)
      break
    case '30m':
      date.setMinutes(Math.floor(date.getMinutes() / 30) * 30, 0, 0)
      break
    case '1h':
      date.setMinutes(0, 0, 0)
      break
    case '1d':
      date.setHours(0, 0, 0, 0)
      break
    case '1w': {
      const day = date.getDay()
      const diff = date.getDate() - day + (day === 0 ? -6 : 1) // 调整到周一
      date.setDate(diff)
      date.setHours(0, 0, 0, 0)
      break
    }
    case '1M':
      date.setDate(1)
      date.setHours(0, 0, 0, 0)
      break
  }

  return Math.floor(date.getTime() / 1000)
}

/**
 * K线聚合器
 */
export class KlineAggregator {
  private timeframe: Timeframe = '1m'
  private bars: Map<number, AggregatedBar> = new Map()
  private currentBar: AggregatedBar | null = null
  private historyBars: KlineBar[] = []

  constructor(timeframe: Timeframe = '1m') {
    this.timeframe = timeframe
    console.log(`[KlineAggregator] 初始化，周期: ${timeframe}`)
  }

  /**
   * 设置目标周期
   */
  setTimeframe(tf: Timeframe): void {
    if (this.timeframe === tf) return

    console.log(`[KlineAggregator] 切换周期: ${this.timeframe} -> ${tf}`)
    this.timeframe = tf
    this.rebuildFromHistory()
  }

  /**
   * 获取当前周期
   */
  getTimeframe(): Timeframe {
    return this.timeframe
  }

  /**
   * 设置历史数据（用于初始化）
   */
  setHistory(bars: KlineBar[]): AggregatedBar[] {
    this.historyBars = [...bars]
    return this.rebuildFromHistory()
  }

  /**
   * 从历史数据重建聚合K线
   */
  private rebuildFromHistory(): AggregatedBar[] {
    this.bars.clear()
    this.currentBar = null

    // 按时间戳排序
    const sorted = [...this.historyBars].sort((a, b) => {
      const ta = typeof a.time === 'string' ? Date.parse(a.time) / 1000 : a.time
      const tb = typeof b.time === 'string' ? Date.parse(b.time) / 1000 : b.time
      return ta - tb
    })

    // 聚合历史数据
    for (const bar of sorted) {
      this.aggregateBar(bar, false)
    }

    return this.getBars()
  }

  /**
   * 聚合单根1分钟线
   * @param bar 1分钟线
   * @param isRealtime 是否实时更新（需要触发回调）
   * @returns 聚合后的结果
   */
  aggregateBar(bar: KlineBar, isRealtime: boolean = true): {
    bars: AggregatedBar[],
    update?: AggregatedBar,
    close?: AggregatedBar,
    isNewBar: boolean
  } {
    const timestamp = typeof bar.time === 'string'
      ? Date.parse(bar.time) / 1000
      : bar.time

    const periodStart = getPeriodStart(timestamp, this.timeframe)

    let isNewBar = false

    if (!this.currentBar || this.currentBar.timestamp !== periodStart) {
      // 新的周期开始
      if (this.currentBar) {
        // 保存上一根完成的bar
        this.bars.set(this.currentBar.timestamp, this.currentBar)
      }

      // 创建新bar
      this.currentBar = {
        time: periodStart,
        open: bar.open,
        high: bar.high,
        low: bar.low,
        close: bar.close,
        volume: bar.volume,
        timestamp: periodStart
      }

      isNewBar = true
    } else {
      // 更新当前bar
      this.currentBar.high = Math.max(this.currentBar.high, bar.high)
      this.currentBar.low = Math.min(this.currentBar.low, bar.low)
      this.currentBar.close = bar.close
      this.currentBar.volume += bar.volume
    }

    const result: any = { bars: this.getBars(), isNewBar }

    if (isRealtime) {
      if (isNewBar && this.currentBar) {
        // 上一根bar收线
        const prevTimestamp = this.getPrevPeriodStart(periodStart)
        const closedBar = this.bars.get(prevTimestamp)
        if (closedBar) {
          result.close = closedBar
        }
      } else if (this.currentBar) {
        // 当前bar更新
        result.update = this.currentBar
      }
    }

    return result
  }

  /**
   * 获取上一周期的开始时间
   */
  private getPrevPeriodStart(currentStart: number): number {
    // 简单处理：减去一个周期的秒数
    const tfSeconds: Record<Timeframe, number> = {
      '1m': 60,
      '5m': 300,
      '15m': 900,
      '30m': 1800,
      '1h': 3600,
      '1d': 86400,
      '1w': 604800,
      '1M': 2592000 // 按30天计算
    }

    return currentStart - tfSeconds[this.timeframe]
  }

  /**
   * 获取所有聚合后的K线（用于初始化图表）
   */
  getBars(): AggregatedBar[] {
    const bars: AggregatedBar[] = []

    // 添加已完成的bars
    const sortedTimestamps = Array.from(this.bars.keys()).sort((a, b) => a - b)
    for (const ts of sortedTimestamps) {
      const bar = this.bars.get(ts)
      if (bar) bars.push({ ...bar })
    }

    // 添加当前正在形成的bar
    if (this.currentBar) {
      bars.push({ ...this.currentBar })
    }

    return bars
  }

  /**
   * 清空数据
   */
  clear(): void {
    this.bars.clear()
    this.currentBar = null
    this.historyBars = []
    console.log('[KlineAggregator] 数据已清空')
  }
}

/**
 * 创建聚合器实例
 */
export function createKlineAggregator(timeframe: Timeframe = '1m'): KlineAggregator {
  const aggregator = new KlineAggregator(timeframe)
  console.log(`[KlineAggregator] 创建实例，周期: ${timeframe}`)
  return aggregator
}

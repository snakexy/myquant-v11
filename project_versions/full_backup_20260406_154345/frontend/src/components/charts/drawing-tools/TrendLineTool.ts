/**
 * 趋势线绘图工具 - 基于官方 Primitives API
 * 参考资料: https://tradingview.github.io/lightweight-charts/plugin-examples/
 */

import {
  IChartApi,
  ISeriesApi,
  Time,
  Logical,
  SeriesPrimitivePaneView,
  SeriesPrimitivePaneViewZOrder,
} from 'lightweight-charts'

/**
 * 趋势线数据点
 */
export interface TrendLinePoint {
  price: number
  time: Time | Logical
}

/**
 * 趋势线选项
 */
export interface TrendLineOptions {
  color?: string
  lineWidth?: number
  lineStyle?: number  // 0=实线, 1=虚线, 2=点线
  title?: string
}

/**
 * 趋势线状态
 */
export interface TrendLineState {
  points: TrendLinePoint[]
  options: TrendLineOptions
}

/**
 * 趋势线绘图工具类
 * 实现 ISeriesPrimitivePaneView 接口
 */
export class TrendLineTool implements SeriesPrimitivePaneView {
  private _points: TrendLinePoint[] = []
  private _options: TrendLineOptions = {}
  private _chart: IChartApi | null = null
  private _series: ISeriesApi<any> | null = null

  constructor(
    chart: IChartApi,
    series: ISeriesApi<any>,
    points: TrendLinePoint[] = [],
    options: TrendLineOptions = {}
  ) {
    this._chart = chart
    this._series = series
    this._points = points
    this._options = {
      color: '#2962ff',
      lineWidth: 2,
      lineStyle: 0,
      ...options
    }
  }

  /**
   * 更新点位
   */
  setPoint(point: TrendLinePoint, index: number) {
    this._points[index] = point
    this.update()
  }

  /**
   * 添加点位
   */
  addPoint(point: TrendLinePoint) {
    this._points.push(point)
    this.update()
  }

  /**
   * 更新选项
   */
  setOptions(options: TrendLineOptions) {
    this._options = { ...this._options, ...options }
    this.update()
  }

  /**
   * 获取点位
   */
  getPoints(): TrendLinePoint[] {
    return this._points
  }

  /**
   * 获取选项
   */
  getOptions(): TrendLineOptions {
    return this._options
  }

  /**
   * z-order 排序
   */
  zOrder(): SeriesPrimitivePaneViewZOrder {
    return 'normal'
  }

  /**
   * 更新（渲染）
   */
  update(): void {
    if (!this._chart) return

    // TODO: 实现实际的绘图逻辑
    // 这需要使用 lightweight-charts 的 Primitives 渲染系统
    // 官方示例中会创建自定义的 pane view
  }
}

/**
 * 创建趋势线工具
 */
export function createTrendLineTool(
  chart: IChartApi,
  series: ISeriesApi<any>,
  points?: TrendLinePoint[],
  options?: TrendLineOptions
): TrendLineTool {
  return new TrendLineTool(chart, series, points, options)
}

/**
 * 趋势线工具管理器
 * 管理图表中的所有趋势线
 */
export class TrendLineManager {
  private tools: Map<string, TrendLineTool> = new Map()
  private _chart: IChartApi | null = null
  private _series: ISeriesApi<any> | null = null

  constructor(chart: IChartApi, series: ISeriesApi<any>) {
    this._chart = chart
    this._series = series
  }

  /**
   * 创建新趋势线
   */
  createTrendLine(points: TrendLinePoint[], options?: TrendLineOptions): string {
    const id = `trendline_${Date.now()}`

    const tool = new TrendLineTool(this._chart!, this._series!, points, options)
    this.tools.set(id, tool)

    return id
  }

  /**
   * 删除趋势线
   */
  removeTrendLine(id: string): void {
    const tool = this.tools.get(id)
    if (tool) {
      // TODO: 清理资源
      this.tools.delete(id)
    }
  }

  /**
   * 清除所有趋势线
   */
  clearAll(): void {
    this.tools.forEach((tool, id) => {
      this.removeTrendLine(id)
    })
    this.tools.clear()
  }

  /**
   * 获取所有趋势线
   */
  getAllTrendLines(): Map<string, TrendLineTool> {
    return this.tools
  }
}

/**
 * 标注管理器 - 使用 lightweight-charts 官方 Series Markers Plugin API
 * 参考: https://tradingview.github.io/lightweight-charts/plugins-api
 */

import type {
  IChartApi,
  ISeriesApi,
  Time
} from 'lightweight-charts/dist/typings'

import {
  createSeriesMarkers,
  type ISeriesMarkersPluginApi,
  type SeriesMarker
} from 'lightweight-charts'

/**
 * 标注类型
 */
export type AnnotationType = 'long' | 'short'

/**
 * 标注数据
 */
export interface AnnotationData {
  id: string
  type: AnnotationType
  time: Time
  price?: number
}

/**
 * 标注管理器
 * 使用官方 Series Markers Plugin API
 */
export class AnnotationManager {
  private chart: IChartApi
  private series: ISeriesApi<'Candlestick'> | null = null
  private seriesMarkersPlugin: ISeriesMarkersPluginApi<Time> | null = null
  private markers: Map<string, AnnotationData> = new Map()

  constructor(chart: IChartApi) {
    this.chart = chart
    console.log('[AnnotationManager] 标注管理器已初始化（使用官方 Series Markers Plugin API）')
  }

  /**
   * 设置关联的 series
   */
  setSeries(series: ISeriesApi<'Candlestick'>): void {
    this.series = series

    // 创建 Series Markers 插件
    this.seriesMarkersPlugin = createSeriesMarkers(series)

    console.log('[AnnotationManager] Series 已设置，Series Markers Plugin 已创建')
  }

  /**
   * 添加做多标注
   */
  addLongAnnotation(time: Time, price?: number): string {
    const id = `long_${time}`

    // 创建标记数据
    const marker: SeriesMarker<Time> = {
      time,
      position: 'belowBar',
      shape: 'arrowUp',
      color: '#26A69A',
      text: 'L'
    }

    // 保存标注数据
    this.markers.set(id, {
      id,
      type: 'long',
      time,
      price
    })

    // 更新插件中的标记列表
    this.updateMarkers()

    console.log(`[AnnotationManager] 添加做多标注:`, { time, price })

    return id
  }

  /**
   * 添加做空标注
   */
  addShortAnnotation(time: Time, price?: number): string {
    const id = `short_${time}`

    // 创建标记数据
    const marker: SeriesMarker<Time> = {
      time,
      position: 'aboveBar',
      shape: 'arrowDown',
      color: '#EF5350',
      text: 'S'
    }

    // 保存标注数据
    this.markers.set(id, {
      id,
      type: 'short',
      time,
      price
    })

    // 更新插件中的标记列表
    this.updateMarkers()

    console.log(`[AnnotationManager] 添加做空标注:`, { time, price })

    return id
  }

  /**
   * 删除标注
   */
  removeAnnotation(id: string): void {
    this.markers.delete(id)
    this.updateMarkers()

    console.log(`[AnnotationManager] 已删除标注: ${id}`)
  }

  /**
   * 清除所有标注
   */
  clearAll(): void {
    this.markers.clear()
    this.updateMarkers()

    console.log('[AnnotationManager] 已清除所有标注')
  }

  /**
   * 更新插件中的标记列表
   */
  private updateMarkers(): void {
    if (!this.seriesMarkersPlugin) return

    // 将 Map 中的标注数据转换为 SeriesMarker 数组
    const markersArray: SeriesMarker<Time>[] = Array.from(this.markers.values()).map(annotation => {
      if (annotation.type === 'long') {
        return {
          time: annotation.time,
          position: 'belowBar',
          shape: 'arrowUp',
          color: '#26A69A',
          text: 'L'
        }
      } else {
        return {
          time: annotation.time,
          position: 'aboveBar',
          shape: 'arrowDown',
          color: '#EF5350',
          text: 'S'
        }
      }
    })

    // 更新插件
    this.seriesMarkersPlugin.setMarkers(markersArray)
  }

  /**
   * 获取所有标注
   */
  getAnnotations(): Map<string, AnnotationData> {
    return this.markers
  }

  /**
   * 销毁插件
   */
  destroy(): void {
    if (this.seriesMarkersPlugin) {
      // Series Markers 插件会自动随 series 销毁
      this.seriesMarkersPlugin = null
    }
    console.log('[AnnotationManager] 已销毁')
  }
}

/**
 * 创建标注管理器
 */
export function createAnnotationManager(chart: IChartApi): AnnotationManager {
  return new AnnotationManager(chart)
}

/**
 * 绘图工具管理器
 * 参考: trading-vue-js 的 DataCube 工具管理思想
 * 基于深入研究: difurious/lightweight-charts-line-tools v3.8
 */

import type {
  IChartApi,
  ISeriesApi
} from 'lightweight-charts/dist/typings'

import {
  LineStyle
} from 'lightweight-charts'

// 自定义 LogicalPoint 类型
export interface LogicalPoint {
  x: Date | number
  y: number
}

// 绘图点类型（屏幕坐标）
export interface ScreenPoint {
  x: number
  y: number
}

// 绘图数据存储
export interface DrawingData {
  id: string
  type: string
  points: ScreenPoint[]
  options: any
  createdAt: number
}

export interface DrawingObject {
  id: string
  type: string
  data: DrawingData
  element: HTMLElement | null
}

export type ToolType =
  | 'cursor'
  | 'crosshair'
  | 'trendline'
  | 'horizontal'
  | 'vertical'
  | 'ray'
  | 'rectangle'
  | 'text'
  | 'long'
  | 'short'
  | 'zoom-in'
  | 'zoom-out'
  | 'delete'
  | 'settings'

/**
 * 绘图管理器类
 * 使用 HTML Canvas overlay 实现绘图工具
 */
export class DrawingManager {
  private chart: IChartApi
  private series: ISeriesApi<'Candlestick'> | null = null
  private activeTool: ToolType | null = null
  private drawings: Map<string, DrawingObject> = new Map()
  private startPoint: ScreenPoint | null = null
  private isDrawing = false
  private currentElement: HTMLElement | null = null
  private overlayCanvas: HTMLCanvasElement | null = null
  private overlayCtx: CanvasRenderingContext2D | null = null

  constructor(chart: IChartApi) {
    this.chart = chart
    this.createOverlayCanvas()
  }

  /**
   * 创建 overlay canvas
   */
  private createOverlayCanvas(): void {
    const chartElement = this.chart.chartElement()
    if (!chartElement) {
      console.error('[DrawingManager] 无法获取图表元素')
      return
    }

    // 创建 canvas 覆盖层
    this.overlayCanvas = document.createElement('canvas')
    this.overlayCanvas.style.position = 'absolute'
    this.overlayCanvas.style.top = '0'
    this.overlayCanvas.style.left = '0'
    this.overlayCanvas.style.pointerEvents = 'none'
    this.overlayCanvas.style.zIndex = '10'

    chartElement.appendChild(this.overlayCanvas)
    this.overlayCtx = this.overlayCanvas.getContext('2d')

    // 设置 canvas 尺寸
    this.resizeCanvas()

    // 监听窗口大小变化
    window.addEventListener('resize', () => this.resizeCanvas())

    console.log('[DrawingManager] Overlay canvas 已创建')
  }

  /**
   * 调整 canvas 尺寸
   */
  private resizeCanvas(): void {
    const chartElement = this.chart.chartElement()
    if (!chartElement || !this.overlayCanvas) return

    const rect = chartElement.getBoundingClientRect()
    this.overlayCanvas.width = rect.width
    this.overlayCanvas.height = rect.height

    // 重绘所有图形
    this.redrawAll()
  }

  /**
   * 重绘所有图形
   */
  private redrawAll(): void {
    if (!this.overlayCtx) return

    // 清空 canvas
    this.overlayCtx.clearRect(0, 0, this.overlayCanvas!.width, this.overlayCanvas!.height)

    // 重绘所有绘图
    this.drawings.forEach(drawing => {
      this.drawShape(drawing)
    })
  }

  /**
   * 绘制形状
   */
  private drawShape(drawing: DrawingObject): void {
    if (!this.overlayCtx || !drawing.data.points.length) return

    const ctx = this.overlayCtx
    const points = drawing.data.points
    const options = drawing.data.options

    ctx.save()
    ctx.beginPath()

    switch (drawing.data.type) {
      case 'trendline':
      case 'ray':
        if (points.length >= 2) {
          ctx.moveTo(points[0].x, points[0].y)
          ctx.lineTo(points[1].x, points[1].y)
        }
        ctx.strokeStyle = options.color || '#2962ff'
        ctx.lineWidth = options.lineWidth || 2
        ctx.stroke()
        break

      case 'horizontal':
        if (points.length >= 1) {
          const y = points[0].y
          ctx.moveTo(0, y)
          ctx.lineTo(this.overlayCanvas!.width, y)
        }
        ctx.strokeStyle = options.color || '#ff9800'
        ctx.lineWidth = options.lineWidth || 1
        ctx.setLineDash([5, 5])
        ctx.stroke()
        ctx.setLineDash([])
        break

      case 'vertical':
        if (points.length >= 1) {
          const x = points[0].x
          ctx.moveTo(x, 0)
          ctx.lineTo(x, this.overlayCanvas!.height)
        }
        ctx.strokeStyle = options.color || '#9c27b0'
        ctx.lineWidth = options.lineWidth || 1
        ctx.setLineDash([5, 5])
        ctx.stroke()
        ctx.setLineDash([])
        break

      case 'rectangle':
        if (points.length >= 2) {
          const x = Math.min(points[0].x, points[1].x)
          const y = Math.min(points[0].y, points[1].y)
          const w = Math.abs(points[1].x - points[0].x)
          const h = Math.abs(points[1].y - points[0].y)

          ctx.strokeStyle = options.borderColor || '#4caf50'
          ctx.lineWidth = options.borderWidth || 2
          ctx.strokeRect(x, y, w, h)

          if (options.backgroundColor) {
            ctx.fillStyle = options.backgroundColor
            ctx.fillRect(x, y, w, h)
          }
        }
        break
    }

    ctx.restore()
  }

  /**
   * 设置关联的 series（用于坐标转换）
   */
  setSeries(series: ISeriesApi<'Candlestick'>): void {
    this.series = series
    console.log('[DrawingManager] Series 已设置')
  }

  /**
   * 激活工具
   */
  activateTool(tool: ToolType): void {
    console.log(`[DrawingManager] 激活工具: ${tool}`)

    // 先停用当前工具
    if (this.activeTool) {
      this.deactivateTool()
    }

    this.activeTool = tool

    // 注册鼠标事件
    this.registerEventHandlers()

    // 改变光标样式
    this.updateCursor()
  }

  /**
   * 停用工具
   */
  deactivateTool(): void {
    console.log(`[DrawingManager] 停用工具: ${this.activeTool}`)

    // 取消当前绘图
    if (this.isDrawing) {
      this.cancelDrawing()
    }

    // 移除事件监听
    this.unregisterEventHandlers()

    // 恢复光标样式
    this.restoreCursor()

    this.activeTool = null
  }

  /**
   * 注册鼠标事件处理器
   */
  private registerEventHandlers(): void {
    const chartElement = this.chart.chartElement()

    if (!chartElement) {
      console.error('[DrawingManager] 无法获取图表元素')
      return
    }

    // 监听鼠标按下
    chartElement.addEventListener('mousedown', this.handleMouseDown as any)

    // 监听鼠标移动
    chartElement.addEventListener('mousemove', this.handleMouseMove as any)

    // 监听鼠标抬起
    chartElement.addEventListener('mouseup', this.handleMouseUp as any)

    console.log('[DrawingManager] 事件监听器已注册')
  }

  /**
   * 移除鼠标事件处理器
   */
  private unregisterEventHandlers(): void {
    const chartElement = this.chart.chartElement()

    if (!chartElement) return

    chartElement.removeEventListener('mousedown', this.handleMouseDown as any)
    chartElement.removeEventListener('mousemove', this.handleMouseMove as any)
    chartElement.removeEventListener('mouseup', this.handleMouseUp as any)

    console.log('[DrawingManager] 事件监听器已移除')
  }

  /**
   * 鼠标按下处理
   */
  private handleMouseDown = (event: MouseEvent): void => {
    if (!this.activeTool || this.isDrawing) return

    // 获取鼠标在图表中的屏幕坐标
    const point = this.getScreenPoint(event)
    if (!point) return

    console.log('[DrawingManager] 鼠标按下:', point)

    switch (this.activeTool) {
      case 'trendline':
      case 'horizontal':
      case 'vertical':
      case 'ray':
      case 'rectangle':
        this.startDrawing(point)
        break

      case 'text':
      case 'long':
      case 'short':
        this.createTextDrawing(point)
        break

      case 'delete':
        this.deleteDrawingAt(point)
        break

      case 'zoom-in':
        this.chart.timeScale().zoomIn()
        break

      case 'zoom-out':
        this.chart.timeScale().zoomOut()
        break
    }
  }

  /**
   * 鼠标移动处理
   */
  private handleMouseMove = (event: MouseEvent): void => {
    if (!this.isDrawing || !this.startPoint) return

    const point = this.getScreenPoint(event)
    if (!point) return

    this.updateDrawing(point)
  }

  /**
   * 鼠标抬起处理
   */
  private handleMouseUp = (event: MouseEvent): void => {
    if (!this.isDrawing) return

    const point = this.getScreenPoint(event)
    if (!point) return

    this.finishDrawing(point)
  }

  /**
   * 获取鼠标在图表中的屏幕坐标
   */
  private getScreenPoint(event: MouseEvent): ScreenPoint | null {
    const chartElement = this.chart.chartElement()
    if (!chartElement) return null

    const rect = chartElement.getBoundingClientRect()
    const x = event.clientX - rect.left
    const y = event.clientY - rect.top

    return { x, y }
  }

  /**
   * 开始绘图
   */
  private startDrawing(point: ScreenPoint): void {
    this.isDrawing = true
    this.startPoint = point

    console.log('[DrawingManager] 开始绘图:', this.activeTool, point)

    // 根据工具类型设置绘图选项
    let options: any = {}

    switch (this.activeTool) {
      case 'trendline':
      case 'ray':
        options = {
          color: '#2962ff',
          lineWidth: 2
        }
        break
      case 'horizontal':
        options = {
          color: '#ff9800',
          lineWidth: 1
        }
        break
      case 'vertical':
        options = {
          color: '#9c27b0',
          lineWidth: 1
        }
        break
      case 'rectangle':
        options = {
          borderColor: '#4caf50',
          borderWidth: 2,
          backgroundColor: 'rgba(76, 175, 80, 0.1)'
        }
        break
    }
  }

  /**
   * 更新绘图
   */
  private updateDrawing(point: ScreenPoint): void {
    if (!this.startPoint || !this.overlayCtx) return

    // 清空 canvas 并重绘
    this.overlayCtx.clearRect(0, 0, this.overlayCanvas!.width, this.overlayCanvas!.height)

    // 重绘已保存的图形
    this.drawings.forEach(drawing => this.drawShape(drawing))

    // 绘制当前正在拖拽的图形
    const tempDrawing: DrawingObject = {
      id: 'temp',
      type: this.activeTool!,
      data: {
        id: 'temp',
        type: this.activeTool!,
        points: [this.startPoint, point],
        options: {},
        createdAt: Date.now()
      },
      element: null
    }

    // 设置当前工具的选项
    switch (this.activeTool) {
      case 'trendline':
      case 'ray':
        tempDrawing.data.options = { color: '#2962ff', lineWidth: 2 }
        break
      case 'horizontal':
        tempDrawing.data.options = { color: '#ff9800', lineWidth: 1 }
        break
      case 'vertical':
        tempDrawing.data.options = { color: '#9c27b0', lineWidth: 1 }
        break
      case 'rectangle':
        tempDrawing.data.options = {
          borderColor: '#4caf50',
          borderWidth: 2,
          backgroundColor: 'rgba(76, 175, 80, 0.1)'
        }
        break
    }

    this.drawShape(tempDrawing)
  }

  /**
   * 完成绘图
   */
  private finishDrawing(point: ScreenPoint): void {
    console.log('[DrawingManager] 完成绘图:', this.activeTool)

    const id = `${this.activeTool}_${Date.now()}`

    // 设置绘图选项
    let options: any = {}
    switch (this.activeTool) {
      case 'trendline':
      case 'ray':
        options = { color: '#2962ff', lineWidth: 2 }
        break
      case 'horizontal':
        options = { color: '#ff9800', lineWidth: 1 }
        break
      case 'vertical':
        options = { color: '#9c27b0', lineWidth: 1 }
        break
      case 'rectangle':
        options = {
          borderColor: '#4caf50',
          borderWidth: 2,
          backgroundColor: 'rgba(76, 175, 80, 0.1)'
        }
        break
    }

    // 保存绘图数据
    const drawingData: DrawingData = {
      id,
      type: this.activeTool!,
      points: [this.startPoint!, point],
      options,
      createdAt: Date.now()
    }

    this.drawings.set(id, {
      id,
      type: this.activeTool!,
      data: drawingData,
      element: null
    })

    console.log(`[DrawingManager] 绘图已保存: ${id}`)
    console.log(`[DrawingManager] 总绘图数: ${this.drawings.size}`)

    // 重置状态
    this.isDrawing = false
    this.startPoint = null
    this.currentElement = null
  }

  /**
   * 取消绘图
   */
  private cancelDrawing(): void {
    // 清空预览
    if (this.overlayCtx) {
      this.overlayCtx.clearRect(0, 0, this.overlayCanvas!.width, this.overlayCanvas!.height)
      this.redrawAll()
    }

    this.isDrawing = false
    this.startPoint = null
    this.currentElement = null
  }

  /**
   * 创建文本绘图
   */
  private createTextDrawing(point: ScreenPoint): void {
    const text = prompt('请输入标注文本:')
    if (!text) return

    console.log('[DrawingManager] 创建文本:', { point, text })

    const id = `text_${Date.now()}`
    this.drawings.set(id, {
      id,
      type: 'text',
      primitive: null, // TODO: 使用 TextPrimitive
      data: { point, text },
      createdAt: Date.now()
    })
  }

  /**
   * 删除指定位置的绘图
   */
  private deleteDrawingAt(point: ScreenPoint): void {
    console.log('[DrawingManager] 删除绘图:', point)

    // TODO: 实现点击检测（命中测试）
    // 目前简化为删除最后一个
    const ids = Array.from(this.drawings.keys())
    if (ids.length > 0) {
      const lastId = ids[ids.length - 1]
      this.removeDrawing(lastId)
      console.log(`[DrawingManager] 已删除: ${lastId}`)
    }
  }

  /**
   * 删除指定的绘图
   */
  removeDrawing(id: string): void {
    const drawing = this.drawings.get(id)
    if (!drawing) return

    // 移除绘图数据
    this.drawings.delete(id)

    // 重绘
    this.redrawAll()

    console.log(`[DrawingManager] 已删除绘图: ${id}`)
  }

  /**
   * 删除选中的工具
   */
  removeSelectedDrawing(): void {
    console.log('[DrawingManager] 尝试删除绘图...')
    console.log('[DrawingManager] 当前绘图数量:', this.drawings.size)

    // TODO: 实现选中逻辑后，删除选中的工具
    const ids = Array.from(this.drawings.keys())
    console.log('[DrawingManager] 绘图ID列表:', ids)

    if (ids.length > 0) {
      const lastId = ids[ids.length - 1]
      this.removeDrawing(lastId)
    } else {
      console.warn('[DrawingManager] 没有可删除的绘图')
    }
  }

  /**
   * 更新光标样式
   */
  private updateCursor(): void {
    const chartElement = this.chart.chartElement()
    if (!chartElement) return

    switch (this.activeTool) {
      case 'text':
        chartElement.style.cursor = 'text'
        break
      case 'crosshair':
        chartElement.style.cursor = 'crosshair'
        break
      default:
        chartElement.style.cursor = 'default'
    }
  }

  /**
   * 恢复光标样式
   */
  private restoreCursor(): void {
    const chartElement = this.chart.chartElement()
    if (!chartElement) return

    chartElement.style.cursor = 'default'
  }

  /**
   * 获取所有绘图
   */
  getDrawings(): DrawingObject[] {
    return Array.from(this.drawings.values())
  }

  /**
   * 清空所有绘图
   */
  clearAll(): void {
    // 清空 canvas
    if (this.overlayCtx) {
      this.overlayCtx.clearRect(0, 0, this.overlayCanvas!.width, this.overlayCanvas!.height)
    }

    // 清空数据
    this.drawings.clear()
    console.log('[DrawingManager] 已清空所有绘图')
  }

  /**
   * 获取当前活动工具
   */
  getActiveTool(): ToolType | null {
    return this.activeTool
  }
}

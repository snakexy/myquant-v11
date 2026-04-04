/**
 * TradingView 绘图工具管理器
 * 使用官方 Plugin API 和自定义 Canvas Overlay 实现专业绘图功能
 */

import {
  type IChartApi,
  type ISeriesApi,
  type Time,
  type PriceLineSource,
  type PriceLineOptions
} from 'lightweight-charts'

// ==================== 类型定义 ====================

export interface PriceLineData {
  id: string
  price: number
  color: string
  lineWidth: number
  lineStyle: 'solid' | 'dotted' | 'dashed'
  axisLabelVisible: boolean
  title: string
}

export interface TrendLineData {
  id: string
  startTime: Time
  startPrice: number
  endTime: Time
  endPrice: number
  color: string
  lineWidth: number
  lineStyle: 'solid' | 'dotted' | 'dashed'
}

export interface FibonacciData {
  id: string
  startTime: Time
  startPrice: number
  endTime: Time
  endPrice: number
  levels: number[] // 默认 [0, 0.236, 0.382, 0.5, 0.618, 0.786, 1]
  colors: string[]
  lineWidth: number
}

export interface RectangleData {
  id: string
  startTime: Time
  startPrice: number
  endTime: Time
  endPrice: number
  color: string
  lineWidth: number
  fillColor: string
  fillOpacity: number
}

export interface CircleData {
  id: string
  centerTime: Time
  centerPrice: number
  radiusTime: Time // 用时间差作为半径
  color: string
  lineWidth: number
  fillColor: string
  fillOpacity: number
}

export interface TriangleData {
  id: string
  point1Time: Time
  point1Price: number
  point2Time: Time
  point2Price: number
  point3Time: Time
  point3Price: number
  color: string
  lineWidth: number
  fillColor: string
  fillOpacity: number
}

// ==================== DrawingToolsManager 类 ====================

export class DrawingToolsManager {
  private chart: IChartApi | null = null
  private series: ISeriesApi<'Candlestick'> | null = null
  private canvas: HTMLCanvasElement | null = null
  private ctx: CanvasRenderingContext2D | null = null
  private container: HTMLElement | null = null

  // 存储绘图数据
  private priceLines = new Map<string, PriceLineData & { priceLine: PriceLineSource }>()
  private trendLines = new Map<string, TrendLineData>()
  private fibonacciRetracements = new Map<string, FibonacciData>()
  private rectangles = new Map<string, RectangleData>()
  private circles = new Map<string, CircleData>()
  private triangles = new Map<string, TriangleData>()

  // 当前选中的工具
  private activeTool: 'cursor' | 'priceLine' | 'trendLine' | 'fibonacci' | 'rectangle' | 'circle' | 'triangle' | null = null
  private drawingState: {
    step: 'start' | 'end' | 'third'
    points?: Array<{ time: Time; price: number; x: number; y: number }>
  } | null = null

  // 鼠标位置（用于实时预览）
  private mouseX = 0
  private mouseY = 0

  constructor() {
    this.handleMouseMove = this.handleMouseMove.bind(this)
    this.handleClick = this.handleClick.bind(this)
    this.handleResize = this.handleResize.bind(this)
  }

  /**
   * 设置图表实例
   */
  setChart(chart: IChartApi, series: ISeriesApi<'Candlestick'>): void {
    this.chart = chart
    this.series = series

    // 创建 Canvas Overlay
    this.createCanvasOverlay()
  }

  /**
   * 创建 Canvas 覆盖层
   */
  private createCanvasOverlay(): void {
    if (!this.chart) return

    const chartElement = this.chart.chartElement()
    this.container = chartElement.parentElement

    if (!this.container) return

    // 创建 canvas 元素
    this.canvas = document.createElement('canvas')
    this.canvas.style.position = 'absolute'
    this.canvas.style.top = '0'
    this.canvas.style.left = '0'
    this.canvas.style.pointerEvents = 'none' // 让鼠标事件穿透到图表
    this.canvas.style.zIndex = '5'
    this.canvas.width = this.container.clientWidth
    this.canvas.height = this.container.clientHeight

    this.container.appendChild(this.canvas)

    this.ctx = this.canvas.getContext('2d')
    if (!this.ctx) return

    // 启用事件监听（用于绘图）
    this.canvas.style.pointerEvents = 'auto'

    // 绑定事件
    this.canvas.addEventListener('mousemove', this.handleMouseMove)
    this.canvas.addEventListener('click', this.handleClick)

    // 监听窗口大小变化
    window.addEventListener('resize', this.handleResize)

    // 启动渲染循环
    this.startRenderLoop()
  }

  /**
   * 启动渲染循环
   */
  private startRenderLoop(): void {
    const render = () => {
      this.draw()
      requestAnimationFrame(render)
    }
    requestAnimationFrame(render)
  }

  /**
   * 绘制所有图形
   */
  private draw(): void {
    if (!this.ctx || !this.canvas) return

    // 清空 canvas
    this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height)

    // 绘制趋势线
    this.trendLines.forEach(data => {
      this.drawTrendLine(data)
    })

    // 绘制斐波那契回撤
    this.fibonacciRetracements.forEach(data => {
      this.drawFibonacci(data)
    })

    // 绘制矩形
    this.rectangles.forEach(data => {
      this.drawRectangle(data)
    })

    // 绘制圆形
    this.circles.forEach(data => {
      this.drawCircle(data)
    })

    // 绘制三角形
    this.triangles.forEach(data => {
      this.drawTriangle(data)
    })

    // 绘制当前正在创建的图形预览
    if (this.drawingState && this.drawingState.points) {
      this.drawPreview()
    }
  }

  /**
   * 绘制趋势线
   */
  private drawTrendLine(data: TrendLineData): void {
    if (!this.chart || !this.ctx) return

    const startPoint = this.timePriceToCoordinates(data.startTime, data.startPrice)
    const endPoint = this.timePriceToCoordinates(data.endTime, data.endPrice)

    if (!startPoint || !endPoint) return

    this.ctx.beginPath()
    this.ctx.strokeStyle = data.color
    this.ctx.lineWidth = data.lineWidth

    // 设置线型
    if (data.lineStyle === 'dashed') {
      this.ctx.setLineDash([6, 4])
    } else if (data.lineStyle === 'dotted') {
      this.ctx.setLineDash([2, 4])
    } else {
      this.ctx.setLineDash([])
    }

    this.ctx.moveTo(startPoint.x, startPoint.y)
    this.ctx.lineTo(endPoint.x, endPoint.y)
    this.ctx.stroke()

    // 绘制端点圆点
    this.drawPoint(startPoint.x, startPoint.y, data.color)
    this.drawPoint(endPoint.x, endPoint.y, data.color)
  }

  /**
   * 绘制斐波那契回撤
   */
  private drawFibonacci(data: FibonacciData): void {
    if (!this.chart || !this.ctx) return

    const startPoint = this.timePriceToCoordinates(data.startTime, data.startPrice)
    const endPoint = this.timePriceToCoordinates(data.endTime, data.endPrice)

    if (!startPoint || !endPoint) return

    // 计算价格范围
    const priceDiff = data.endPrice - data.startPrice
    const priceRange = Math.abs(priceDiff)

    // 绘制每个斐波那契水平线
    data.levels.forEach((level, index) => {
      const price = data.startPrice + priceDiff * level
      const y = this.priceToY(price)

      if (y === null) return

      // 绘制水平线
      this.ctx.beginPath()
      this.ctx.strokeStyle = data.colors[index] || '#787b86'
      this.ctx.lineWidth = data.lineWidth
      this.ctx.setLineDash([6, 4])
      this.ctx.moveTo(startPoint.x, y)
      this.ctx.lineTo(endPoint.x, y)
      this.ctx.stroke()

      // 绘制标签
      const label = `${(level * 100).toFixed(1)}% - ${price.toFixed(2)}`
      this.ctx.fillStyle = data.colors[index] || '#787b86'
      this.ctx.font = '12px Arial'
      this.ctx.fillText(label, endPoint.x + 5, y + 4)
    })

    // 绘制连接线
    this.ctx.beginPath()
    this.ctx.strokeStyle = '#787b86'
    this.ctx.lineWidth = 1
    this.ctx.setLineDash([2, 2])
    this.ctx.moveTo(startPoint.x, startPoint.y)
    this.ctx.lineTo(endPoint.x, startPoint.y)
    this.ctx.stroke()

    this.ctx.beginPath()
    this.ctx.moveTo(startPoint.x, endPoint.y)
    this.ctx.lineTo(endPoint.x, endPoint.y)
    this.ctx.stroke()
  }

  /**
   * 绘制端点
   */
  private drawPoint(x: number, y: number, color: string): void {
    if (!this.ctx) return

    this.ctx.beginPath()
    this.ctx.fillStyle = color
    this.ctx.arc(x, y, 4, 0, Math.PI * 2)
    this.ctx.fill()
  }

  /**
   * 绘制矩形
   */
  private drawRectangle(data: RectangleData): void {
    if (!this.chart || !this.ctx) return

    const startPoint = this.timePriceToCoordinates(data.startTime, data.startPrice)
    const endPoint = this.timePriceToCoordinates(data.endTime, data.endPrice)

    if (!startPoint || !endPoint) return

    const width = endPoint.x - startPoint.x
    const height = endPoint.y - startPoint.y

    // 绘制填充
    if (data.fillOpacity > 0) {
      this.ctx.fillStyle = this.hexToRgba(data.fillColor, data.fillOpacity)
      this.ctx.fillRect(startPoint.x, startPoint.y, width, height)
    }

    // 绘制边框
    this.ctx.strokeStyle = data.color
    this.ctx.lineWidth = data.lineWidth
    this.ctx.setLineDash([])
    this.ctx.strokeRect(startPoint.x, startPoint.y, width, height)

    // 绘制角点
    this.drawPoint(startPoint.x, startPoint.y, data.color)
    this.drawPoint(endPoint.x, endPoint.y, data.color)
  }

  /**
   * 绘制圆形
   */
  private drawCircle(data: CircleData): void {
    if (!this.chart || !this.ctx) return

    const centerPoint = this.timePriceToCoordinates(data.centerTime, data.centerPrice)
    const edgePoint = this.timePriceToCoordinates(data.radiusTime, data.centerPrice)

    if (!centerPoint || !edgePoint) return

    // 计算半径（使用时间方向的距离）
    const radius = Math.abs(edgePoint.x - centerPoint.x)

    // 绘制填充
    if (data.fillOpacity > 0) {
      this.ctx.fillStyle = this.hexToRgba(data.fillColor, data.fillOpacity)
      this.ctx.beginPath()
      this.ctx.arc(centerPoint.x, centerPoint.y, radius, 0, Math.PI * 2)
      this.ctx.fill()
    }

    // 绘制边框
    this.ctx.strokeStyle = data.color
    this.ctx.lineWidth = data.lineWidth
    this.ctx.setLineDash([])
    this.ctx.beginPath()
    this.ctx.arc(centerPoint.x, centerPoint.y, radius, 0, Math.PI * 2)
    this.ctx.stroke()

    // 绘制中心点
    this.drawPoint(centerPoint.x, centerPoint.y, data.color)
  }

  /**
   * 绘制三角形
   */
  private drawTriangle(data: TriangleData): void {
    if (!this.chart || !this.ctx) return

    const point1 = this.timePriceToCoordinates(data.point1Time, data.point1Price)
    const point2 = this.timePriceToCoordinates(data.point2Time, data.point2Price)
    const point3 = this.timePriceToCoordinates(data.point3Time, data.point3Price)

    if (!point1 || !point2 || !point3) return

    // 绘制填充
    if (data.fillOpacity > 0) {
      this.ctx.fillStyle = this.hexToRgba(data.fillColor, data.fillOpacity)
      this.ctx.beginPath()
      this.ctx.moveTo(point1.x, point1.y)
      this.ctx.lineTo(point2.x, point2.y)
      this.ctx.lineTo(point3.x, point3.y)
      this.ctx.closePath()
      this.ctx.fill()
    }

    // 绘制边框
    this.ctx.strokeStyle = data.color
    this.ctx.lineWidth = data.lineWidth
    this.ctx.setLineDash([])
    this.ctx.beginPath()
    this.ctx.moveTo(point1.x, point1.y)
    this.ctx.lineTo(point2.x, point2.y)
    this.ctx.lineTo(point3.x, point3.y)
    this.ctx.closePath()
    this.ctx.stroke()

    // 绘制顶点
    this.drawPoint(point1.x, point1.y, data.color)
    this.drawPoint(point2.x, point2.y, data.color)
    this.drawPoint(point3.x, point3.y, data.color)
  }

  /**
   * 绘制预览
   */
  private drawPreview(): void {
    if (!this.ctx || !this.drawingState || !this.drawingState.points) return

    const points = this.drawingState.points

    this.ctx.strokeStyle = '#2962ff'
    this.ctx.lineWidth = 2
    this.ctx.setLineDash([4, 2])

    if (this.activeTool === 'trendLine') {
      if (points.length >= 1) {
        this.ctx.beginPath()
        this.ctx.moveTo(points[0].x, points[0].y)
        this.ctx.lineTo(this.mouseX, this.mouseY)
        this.ctx.stroke()
      }
    } else if (this.activeTool === 'fibonacci') {
      if (points.length >= 1) {
        this.ctx.beginPath()
        this.ctx.rect(
          points[0].x,
          points[0].y,
          this.mouseX - points[0].x,
          this.mouseY - points[0].y
        )
        this.ctx.stroke()
      }
    } else if (this.activeTool === 'rectangle') {
      if (points.length >= 1) {
        this.ctx.beginPath()
        this.ctx.rect(
          points[0].x,
          points[0].y,
          this.mouseX - points[0].x,
          this.mouseY - points[0].y
        )
        this.ctx.stroke()
      }
    } else if (this.activeTool === 'circle') {
      if (points.length >= 1) {
        const radius = Math.abs(this.mouseX - points[0].x)
        this.ctx.beginPath()
        this.ctx.arc(points[0].x, points[0].y, radius, 0, Math.PI * 2)
        this.ctx.stroke()
      }
    } else if (this.activeTool === 'triangle') {
      if (points.length >= 1) {
        this.ctx.beginPath()
        this.ctx.moveTo(points[0].x, points[0].y)
        if (points.length >= 2) {
          this.ctx.lineTo(points[1].x, points[1].y)
        }
        this.ctx.lineTo(this.mouseX, this.mouseY)
        this.ctx.stroke()
      }
    }
  }

  /**
   * 将十六进制颜色转换为 RGBA
   */
  private hexToRgba(hex: string, alpha: number): string {
    const r = parseInt(hex.slice(1, 3), 16)
    const g = parseInt(hex.slice(3, 5), 16)
    const b = parseInt(hex.slice(5, 7), 16)
    return `rgba(${r}, ${g}, ${b}, ${alpha})`
  }

  /**
   * 处理鼠标移动
   */
  private handleMouseMove(event: MouseEvent): void {
    if (!this.canvas) return

    const rect = this.canvas.getBoundingClientRect()
    this.mouseX = event.clientX - rect.left
    this.mouseY = event.clientY - rect.top
  }

  /**
   * 处理鼠标点击
   */
  private handleClick(event: MouseEvent): void {
    if (!this.chart || !this.series || !this.canvas) return

    const rect = this.canvas.getBoundingClientRect()
    const x = event.clientX - rect.left
    const y = event.clientY - rect.top

    // 转换为时间和价格
    const timePrice = this.coordinatesToTimePrice(x, y)
    if (!timePrice) return

    const { time, price } = timePrice

    if (this.activeTool === 'priceLine') {
      // 价格线：点击直接创建
      this.addPriceLine(price)
      this.setActiveTool(null)
    } else if (this.activeTool === 'trendLine') {
      // 趋势线：两次点击
      if (!this.drawingState || !this.drawingState.points) {
        this.drawingState = { step: 'end', points: [{ time, price, x, y }] }
      } else {
        this.addTrendLine(
          this.drawingState.points[0].time,
          this.drawingState.points[0].price,
          time,
          price
        )
        this.drawingState = null
        this.setActiveTool(null)
      }
    } else if (this.activeTool === 'fibonacci') {
      // 斐波那契：两次点击
      if (!this.drawingState || !this.drawingState.points) {
        this.drawingState = { step: 'end', points: [{ time, price, x, y }] }
      } else {
        this.addFibonacci(
          this.drawingState.points[0].time,
          this.drawingState.points[0].price,
          time,
          price
        )
        this.drawingState = null
        this.setActiveTool(null)
      }
    } else if (this.activeTool === 'rectangle') {
      // 矩形：两次点击（对角线）
      if (!this.drawingState || !this.drawingState.points) {
        this.drawingState = { step: 'end', points: [{ time, price, x, y }] }
      } else {
        this.addRectangle(
          this.drawingState.points[0].time,
          this.drawingState.points[0].price,
          time,
          price
        )
        this.drawingState = null
        this.setActiveTool(null)
      }
    } else if (this.activeTool === 'circle') {
      // 圆形：两次点击（圆心 + 边缘点）
      if (!this.drawingState || !this.drawingState.points) {
        this.drawingState = { step: 'end', points: [{ time, price, x, y }] }
      } else {
        this.addCircle(
          this.drawingState.points[0].time,
          this.drawingState.points[0].price,
          time
        )
        this.drawingState = null
        this.setActiveTool(null)
      }
    } else if (this.activeTool === 'triangle') {
      // 三角形：三次点击
      if (!this.drawingState || !this.drawingState.points) {
        this.drawingState = { step: 'end', points: [{ time, price, x, y }] }
      } else if (this.drawingState.points.length === 1) {
        this.drawingState.points.push({ time, price, x, y })
      } else {
        this.addTriangle(
          this.drawingState.points[0].time,
          this.drawingState.points[0].price,
          this.drawingState.points[1].time,
          this.drawingState.points[1].price,
          time,
          price
        )
        this.drawingState = null
        this.setActiveTool(null)
      }
    }
  }

  /**
   * 处理窗口大小变化
   */
  private handleResize(): void {
    if (!this.canvas || !this.container) return

    this.canvas.width = this.container.clientWidth
    this.canvas.height = this.container.clientHeight
  }

  /**
   * 添加价格线
   */
  addPriceLine(
    price: number,
    options?: Partial<PriceLineData>
  ): string {
    if (!this.series) throw new Error('Series not set')

    const id = `price-line-${Date.now()}-${Math.random()}`
    const color = options?.color || '#2962ff'
    const lineWidth = options?.lineWidth || 2
    const lineStyle = options?.lineStyle || 'dashed'

    // 使用官方 API 创建价格线
    const priceLineOptions: PriceLineOptions = {
      price,
      color,
      lineWidth,
      lineStyle: lineStyle === 'dashed' ? 2 : lineStyle === 'dotted' ? 3 : 0,
      axisLabelVisible: options?.axisLabelVisible ?? true,
      title: options?.title || price.toFixed(2)
    }

    const priceLine = this.series.createPriceLine(priceLineOptions)

    this.priceLines.set(id, {
      id,
      price,
      color,
      lineWidth,
      lineStyle,
      axisLabelVisible: priceLineOptions.axisLabelVisible!,
      title: priceLineOptions.title!,
      priceLine
    })

    console.log(`[DrawingToolsManager] 价格线已添加: ${price} (${id})`)
    return id
  }

  /**
   * 添加趋势线
   */
  addTrendLine(
    startTime: Time,
    startPrice: number,
    endTime: Time,
    endPrice: number,
    options?: Partial<TrendLineData>
  ): string {
    const id = `trend-line-${Date.now()}-${Math.random()}`

    const data: TrendLineData = {
      id,
      startTime,
      startPrice,
      endTime,
      endPrice,
      color: options?.color || '#2962ff',
      lineWidth: options?.lineWidth || 2,
      lineStyle: options?.lineStyle || 'solid'
    }

    this.trendLines.set(id, data)
    console.log(`[DrawingToolsManager] 趋势线已添加: ${id}`)
    return id
  }

  /**
   * 添加斐波那契回撤
   */
  addFibonacci(
    startTime: Time,
    startPrice: number,
    endTime: Time,
    endPrice: number,
    options?: Partial<FibonacciData>
  ): string {
    const id = `fibonacci-${Date.now()}-${Math.random()}`

    const data: FibonacciData = {
      id,
      startTime,
      startPrice,
      endTime,
      endPrice,
      levels: options?.levels || [0, 0.236, 0.382, 0.5, 0.618, 0.786, 1],
      colors: options?.colors || ['#ef4444', '#f97316', '#eab308', '#22c55e', '#3b82f6', '#8b5cf6', '#ec4899'],
      lineWidth: options?.lineWidth || 1
    }

    this.fibonacciRetracements.set(id, data)
    console.log(`[DrawingToolsManager] 斐波那契回撤已添加: ${id}`)
    return id
  }

  /**
   * 添加矩形
   */
  addRectangle(
    startTime: Time,
    startPrice: number,
    endTime: Time,
    endPrice: number,
    options?: Partial<RectangleData>
  ): string {
    const id = `rectangle-${Date.now()}-${Math.random()}`

    const data: RectangleData = {
      id,
      startTime,
      startPrice,
      endTime,
      endPrice,
      color: options?.color || '#4CAF50',
      lineWidth: options?.lineWidth || 2,
      fillColor: options?.fillColor || '#4CAF50',
      fillOpacity: options?.fillOpacity ?? 0.1
    }

    this.rectangles.set(id, data)
    console.log(`[DrawingToolsManager] 矩形已添加: ${id}`)
    return id
  }

  /**
   * 添加圆形
   */
  addCircle(
    centerTime: Time,
    centerPrice: number,
    radiusTime: Time,
    options?: Partial<CircleData>
  ): string {
    const id = `circle-${Date.now()}-${Math.random()}`

    const data: CircleData = {
      id,
      centerTime,
      centerPrice,
      radiusTime,
      color: options?.color || '#2196F3',
      lineWidth: options?.lineWidth || 2,
      fillColor: options?.fillColor || '#2196F3',
      fillOpacity: options?.fillOpacity ?? 0.1
    }

    this.circles.set(id, data)
    console.log(`[DrawingToolsManager] 圆形已添加: ${id}`)
    return id
  }

  /**
   * 添加三角形
   */
  addTriangle(
    point1Time: Time,
    point1Price: number,
    point2Time: Time,
    point2Price: number,
    point3Time: Time,
    point3Price: number,
    options?: Partial<TriangleData>
  ): string {
    const id = `triangle-${Date.now()}-${Math.random()}`

    const data: TriangleData = {
      id,
      point1Time,
      point1Price,
      point2Time,
      point2Price,
      point3Time,
      point3Price,
      color: options?.color || '#FF9800',
      lineWidth: options?.lineWidth || 2,
      fillColor: options?.fillColor || '#FF9800',
      fillOpacity: options?.fillOpacity ?? 0.1
    }

    this.triangles.set(id, data)
    console.log(`[DrawingToolsManager] 三角形已添加: ${id}`)
    return id
  }

  /**
   * 删除矩形
   */
  removeRectangle(id: string): void {
    this.rectangles.delete(id)
    console.log(`[DrawingToolsManager] 矩形已删除: ${id}`)
  }

  /**
   * 删除圆形
   */
  removeCircle(id: string): void {
    this.circles.delete(id)
    console.log(`[DrawingToolsManager] 圆形已删除: ${id}`)
  }

  /**
   * 删除三角形
   */
  removeTriangle(id: string): void {
    this.triangles.delete(id)
    console.log(`[DrawingToolsManager] 三角形已删除: ${id}`)
  }

  /**
   * 删除价格线
   */
  removePriceLine(id: string): void {
    const data = this.priceLines.get(id)
    if (data && this.series) {
      this.series.removePriceLine(data.priceLine)
      this.priceLines.delete(id)
      console.log(`[DrawingToolsManager] 价格线已删除: ${id}`)
    }
  }

  /**
   * 删除趋势线
   */
  removeTrendLine(id: string): void {
    this.trendLines.delete(id)
    console.log(`[DrawingToolsManager] 趋势线已删除: ${id}`)
  }

  /**
   * 删除斐波那契回撤
   */
  removeFibonacci(id: string): void {
    this.fibonacciRetracements.delete(id)
    console.log(`[DrawingToolsManager] 斐波那契回撤已删除: ${id}`)
  }

  /**
   * 清除所有绘图
   */
  clearAll(): void {
    // 删除所有价格线
    this.priceLines.forEach((data, id) => {
      this.removePriceLine(id)
    })

    // 清空趋势线
    this.trendLines.clear()

    // 清空斐波那契
    this.fibonacciRetracements.clear()

    // 清空矩形
    this.rectangles.clear()

    // 清空圆形
    this.circles.clear()

    // 清空三角形
    this.triangles.clear()

    console.log('[DrawingToolsManager] 所有绘图已清除')
  }

  /**
   * 设置当前活动工具
   */
  setActiveTool(tool: 'cursor' | 'priceLine' | 'trendLine' | 'fibonacci' | null): void {
    this.activeTool = tool
    this.drawingState = null

    console.log(`[DrawingToolsManager] 工具已切换: ${tool || 'cursor'}`)
  }

  /**
   * 获取所有价格线
   */
  getAllPriceLines(): Map<string, PriceLineData & { priceLine: PriceLineSource }> {
    return this.priceLines
  }

  /**
   * 获取所有趋势线
   */
  getAllTrendLines(): Map<string, TrendLineData> {
    return this.trendLines
  }

  /**
   * 获取所有斐波那契回撤
   */
  getAllFibonacciRetracements(): Map<string, FibonacciData> {
    return this.fibonacciRetracements
  }

  // ==================== 坐标转换工具 ====================

  /**
   * 将时间和价格转换为 Canvas 坐标
   */
  private timePriceToCoordinates(time: Time, price: number): { x: number; y: number } | null {
    if (!this.chart || !this.series) return null

    const timeScale = this.chart.timeScale()
    const x = timeScale.timeToCoordinate(time)
    const y = this.series.priceToCoordinate(price)

    if (x === null || y === null) return null

    return { x, y }
  }

  /**
   * 将 Canvas 坐标转换为时间和价格
   */
  private coordinatesToTimePrice(x: number, y: number): { time: Time; price: number } | null {
    if (!this.chart || !this.series) return null

    const timeScale = this.chart.timeScale()
    const time = timeScale.coordinateToTime(x)
    const price = this.series.coordinateToPrice(y)

    if (!time || price === null) return null

    return { time, price }
  }

  /**
   * 将价格转换为 Y 坐标
   */
  private priceToY(price: number): number | null {
    if (!this.series) return null
    return this.series.priceToCoordinate(price)
  }

  /**
   * 销毁管理器
   */
  destroy(): void {
    // 清除所有绘图
    this.clearAll()

    // 移除事件监听
    if (this.canvas) {
      this.canvas.removeEventListener('mousemove', this.handleMouseMove)
      this.canvas.removeEventListener('click', this.handleClick)
    }

    window.removeEventListener('resize', this.handleResize)

    // 移除 canvas
    if (this.canvas && this.container) {
      this.container.removeChild(this.canvas)
    }

    this.chart = null
    this.series = null
    this.canvas = null
    this.ctx = null
    this.container = null
  }
}

// ==================== 工厂函数 ====================

export function createDrawingToolsManager(): DrawingToolsManager {
  return new DrawingToolsManager()
}

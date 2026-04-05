import { reactive, ref, computed } from 'vue'
import type { Connection } from '../../../api/modules/connections'
import type { ConnectionLayoutInfo } from './NodeLayoutManager'

/**
 * 连接渲染系统
 * 负责渲染节点间的连接线，支持多种连接类型和动画效果
 */

// 连接样式接口
export interface ConnectionStyle {
  type: 'straight' | 'curved' | 'step' | 'orthogonal'
  color: string
  width: number
  opacity: number
  dashArray?: string
  lineCap: 'butt' | 'round' | 'square'
  lineJoin: 'miter' | 'round' | 'bevel'
  shadow?: {
    color: string
    blur: number
    offsetX: number
    offsetY: number
  }
}

// 连接标签接口
export interface ConnectionLabel {
  text: string
  position: 'start' | 'middle' | 'end'
  offset: { x: number; y: number }
  style: {
    fontSize: number
    fontFamily: string
    color: string
    backgroundColor?: string
    padding: { top: number; right: number; bottom: number; left: number }
    borderRadius: number
  }
  visible: boolean
}

// 连接动画接口
export interface ConnectionAnimation {
  type: 'none' | 'flow' | 'pulse' | 'dash' | 'glow'
  duration: number
  delay: number
  direction: 'forward' | 'backward' | 'alternate'
  easing: 'linear' | 'ease' | 'ease-in' | 'ease-out' | 'ease-in-out'
  loop: boolean
  paused: boolean
}

// 连接箭头接口
export interface ConnectionArrow {
  type: 'none' | 'arrow' | 'circle' | 'diamond' | 'square'
  size: number
  position: 'start' | 'end' | 'both'
  style: {
    fill: string
    stroke: string
    strokeWidth: number
  }
}

// 连接状态接口
export interface ConnectionState {
  id: string
  from: string
  to: string
  style: ConnectionStyle
  label: ConnectionLabel
  animation: ConnectionAnimation
  arrow: ConnectionArrow
  path: Array<{ x: number; y: number }>
  controlPoints: Array<{ x: number; y: number }>
  isVisible: boolean
  isHighlighted: boolean
  isSelected: boolean
  isHovered: boolean
  zIndex: number
  dataFlow?: {
    active: boolean
    speed: number
    particles: Array<{
      id: string
      position: number // 0-1 之间的位置
      size: number
      color: string
    }>
  }
}

// 渲染配置接口
export interface RenderConfig {
  canvas: {
    width: number
    height: number
    scale: number
    offsetX: number
    offsetY: number
  }
  performance: {
    enableAntialiasing: boolean
    enableOptimization: boolean
    maxConnections: number
    updateThrottle: number
  }
  interaction: {
    hoverEnabled: boolean
    selectionEnabled: boolean
    dragEnabled: boolean
    clickEnabled: boolean
  }
  effects: {
    enableGlow: boolean
    enableShadow: boolean
    enableGradient: boolean
    enableAnimation: boolean
  }
}

// 事件类型定义
export interface ConnectionRendererEvents {
  'connection-click': { connectionId: string; event: MouseEvent }
  'connection-hover': { connectionId: string; event: MouseEvent; isEntering: boolean }
  'connection-select': { connectionId: string; isSelected: boolean; isMultiSelect: boolean }
  'connection-drag': { connectionId: string; event: MouseEvent; position: { x: number; y: number } }
  'render-completed': { connectionCount: number; renderTime: number }
  'error-occurred': { type: string; message: string; connectionId?: string }
}

class ConnectionRenderer {
  private static instance: ConnectionRenderer
  private eventTarget: EventTarget
  private canvas: HTMLCanvasElement | null = null
  private ctx: CanvasRenderingContext2D | null = null
  private animationFrame: number | null = null
  private lastUpdateTime: number = 0
  
  // 响应式状态
  public state = reactive<{
    connections: Map<string, ConnectionState>
    config: RenderConfig
    isRendering: boolean
    selectedConnections: Set<string>
    hoveredConnection: string | null
    renderStats: {
      totalConnections: number
      visibleConnections: number
      renderTime: number
      fps: number
    }
  }>({
    connections: new Map(),
    config: {
      canvas: {
        width: 800,
        height: 600,
        scale: 1,
        offsetX: 0,
        offsetY: 0
      },
      performance: {
        enableAntialiasing: true,
        enableOptimization: true,
        maxConnections: 1000,
        updateThrottle: 16 // ~60fps
      },
      interaction: {
        hoverEnabled: true,
        selectionEnabled: true,
        dragEnabled: true,
        clickEnabled: true
      },
      effects: {
        enableGlow: true,
        enableShadow: true,
        enableGradient: true,
        enableAnimation: true
      }
    },
    isRendering: false,
    selectedConnections: new Set(),
    hoveredConnection: null,
    renderStats: {
      totalConnections: 0,
      visibleConnections: 0,
      renderTime: 0,
      fps: 0
    }
  })

  // 计算属性
  public get connections() {
    return Array.from(this.state.connections.values())
  }

  public get config() {
    return this.state.config
  }

  public get isRendering() {
    return this.state.isRendering
  }

  public get selectedConnections() {
    return Array.from(this.state.selectedConnections)
  }

  public get hoveredConnection() {
    return this.state.hoveredConnection
  }

  public get renderStats() {
    return this.state.renderStats
  }

  // 单例模式
  public static getInstance(): ConnectionRenderer {
    if (!ConnectionRenderer.instance) {
      ConnectionRenderer.instance = new ConnectionRenderer()
    }
    return ConnectionRenderer.instance
  }

  // 私有构造函数
  private constructor() {
    this.eventTarget = new EventTarget()
  }

  // 初始化渲染器
  public initialize(canvas: HTMLCanvasElement): void {
    this.canvas = canvas
    this.ctx = canvas.getContext('2d')
    
    if (!this.ctx) {
      throw new Error('无法获取Canvas 2D上下文')
    }

    // 设置画布大小
    this.updateCanvasSize()
    
    // 设置默认样式
    this.setupDefaultStyles()
    
    // 添加事件监听器
    this.setupEventListeners()
    
    // 开始渲染循环
    this.startRenderLoop()
  }

  // 更新画布大小
  private updateCanvasSize(): void {
    if (!this.canvas) return

    const rect = this.canvas.getBoundingClientRect()
    const dpr = window.devicePixelRatio || 1

    this.canvas.width = rect.width * dpr
    this.canvas.height = rect.height * dpr

    if (this.ctx) {
      this.ctx.scale(dpr, dpr)
    }

    this.state.config.canvas.width = rect.width
    this.state.config.canvas.height = rect.height
  }

  // 设置默认样式
  private setupDefaultStyles(): void {
    if (!this.ctx) return

    this.ctx.imageSmoothingEnabled = this.state.config.performance.enableAntialiasing
    this.ctx.imageSmoothingQuality = 'high'
  }

  // 设置事件监听器
  private setupEventListeners(): void {
    if (!this.canvas) return

    // 鼠标事件
    this.canvas.addEventListener('click', this.handleClick.bind(this))
    this.canvas.addEventListener('mousemove', this.handleMouseMove.bind(this))
    this.canvas.addEventListener('mousedown', this.handleMouseDown.bind(this))
    this.canvas.addEventListener('mouseup', this.handleMouseUp.bind(this))

    // 窗口大小变化
    window.addEventListener('resize', this.handleResize.bind(this))
  }

  // 开始渲染循环
  private startRenderLoop(): void {
    const render = (currentTime: number) => {
      // 节流控制
      if (currentTime - this.lastUpdateTime >= this.state.config.performance.updateThrottle) {
        this.render()
        this.lastUpdateTime = currentTime
      }

      this.animationFrame = requestAnimationFrame(render)
    }

    this.animationFrame = requestAnimationFrame(render)
  }

  // 停止渲染循环
  public stopRenderLoop(): void {
    if (this.animationFrame) {
      cancelAnimationFrame(this.animationFrame)
      this.animationFrame = null
    }
  }

  // 主渲染方法
  public render(): void {
    if (!this.ctx || !this.canvas) return

    const startTime = performance.now()
    this.state.isRendering = true

    try {
      // 清空画布
      this.clearCanvas()

      // 更新统计信息
      this.updateRenderStats()

      // 渲染所有连接
      this.renderConnections()

      // 更新渲染时间
      const renderTime = performance.now() - startTime
      this.state.renderStats.renderTime = renderTime

      // 触发渲染完成事件
      this.emitEvent('render-completed', {
        connectionCount: this.state.renderStats.visibleConnections,
        renderTime
      })
    } finally {
      this.state.isRendering = false
    }
  }

  // 清空画布
  private clearCanvas(): void {
    if (!this.ctx) return

    this.ctx.clearRect(0, 0, this.state.config.canvas.width, this.state.config.canvas.height)
  }

  // 渲染所有连接
  private renderConnections(): void {
    const visibleConnections = this.connections.filter(conn => conn.isVisible)
    
    // 按Z索引排序
    visibleConnections.sort((a, b) => a.zIndex - b.zIndex)

    visibleConnections.forEach(connection => {
      this.renderConnection(connection)
    })
  }

  // 渲染单个连接
  private renderConnection(connection: ConnectionState): void {
    if (!this.ctx) return

    this.ctx.save()

    // 应用变换
    this.applyTransform()

    // 设置样式
    this.applyConnectionStyle(connection)

    // 渲染路径
    this.renderConnectionPath(connection)

    // 渲染箭头
    if (connection.arrow.type !== 'none') {
      this.renderArrow(connection)
    }

    // 渲染标签
    if (connection.label.visible) {
      this.renderLabel(connection)
    }

    // 渲染数据流动画
    if (connection.dataFlow?.active && this.state.config.effects.enableAnimation) {
      this.renderDataFlow(connection)
    }

    this.ctx.restore()
  }

  // 应用变换
  private applyTransform(): void {
    if (!this.ctx) return

    const { scale, offsetX, offsetY } = this.state.config.canvas
    this.ctx.translate(offsetX, offsetY)
    this.ctx.scale(scale, scale)
  }

  // 应用连接样式
  private applyConnectionStyle(connection: ConnectionState): void {
    if (!this.ctx) return

    const { style } = connection

    // 基础样式
    this.ctx.strokeStyle = style.color
    this.ctx.lineWidth = style.width
    this.ctx.globalAlpha = style.opacity
    this.ctx.lineCap = style.lineCap
    this.ctx.lineJoin = style.lineJoin

    // 虚线样式
    if (style.dashArray) {
      this.ctx.setLineDash(style.dashArray.split(',').map(Number))
    } else {
      this.ctx.setLineDash([])
    }

    // 阴影效果
    if (style.shadow && this.state.config.effects.enableShadow) {
      this.ctx.shadowColor = style.shadow.color
      this.ctx.shadowBlur = style.shadow.blur
      this.ctx.shadowOffsetX = style.shadow.offsetX
      this.ctx.shadowOffsetY = style.shadow.offsetY
    }

    // 高亮效果
    if (connection.isHighlighted && this.state.config.effects.enableGlow) {
      this.ctx.shadowColor = connection.style.color
      this.ctx.shadowBlur = 10
    }
  }

  // 渲染连接路径
  private renderConnectionPath(connection: ConnectionState): void {
    if (!this.ctx) return

    const { path, controlPoints, style } = connection

    this.ctx.beginPath()

    switch (style.type) {
      case 'straight':
        this.renderStraightPath(path)
        break
      case 'curved':
        this.renderCurvedPath(path, controlPoints)
        break
      case 'step':
        this.renderStepPath(path)
        break
      case 'orthogonal':
        this.renderOrthogonalPath(path)
        break
    }

    this.ctx.stroke()
  }

  // 渲染直线路径
  private renderStraightPath(path: Array<{ x: number; y: number }>): void {
    if (!this.ctx || path.length < 2) return

    this.ctx.moveTo(path[0].x, path[0].y)
    this.ctx.lineTo(path[1].x, path[1].y)
  }

  // 渲染曲线路径
  private renderCurvedPath(
    path: Array<{ x: number; y: number }>,
    controlPoints: Array<{ x: number; y: number }>
  ): void {
    if (!this.ctx || path.length < 2) return

    this.ctx.moveTo(path[0].x, path[0].y)

    if (controlPoints.length >= 2) {
      // 贝塞尔曲线
      this.ctx.bezierCurveTo(
        controlPoints[0].x, controlPoints[0].y,
        controlPoints[1].x, controlPoints[1].y,
        path[1].x, path[1].y
      )
    } else if (controlPoints.length === 1) {
      // 二次曲线
      this.ctx.quadraticCurveTo(
        controlPoints[0].x, controlPoints[0].y,
        path[1].x, path[1].y
      )
    } else {
      // 简单直线
      this.ctx.lineTo(path[1].x, path[1].y)
    }
  }

  // 渲染阶梯路径
  private renderStepPath(path: Array<{ x: number; y: number }>): void {
    if (!this.ctx || path.length < 2) return

    const start = path[0]
    const end = path[1]
    const midX = (start.x + end.x) / 2

    this.ctx.moveTo(start.x, start.y)
    this.ctx.lineTo(midX, start.y)
    this.ctx.lineTo(midX, end.y)
    this.ctx.lineTo(end.x, end.y)
  }

  // 渲染正交路径
  private renderOrthogonalPath(path: Array<{ x: number; y: number }>): void {
    if (!this.ctx || path.length < 2) return

    const start = path[0]
    const end = path[1]
    const threshold = 50 // 阈值，决定何时使用水平优先还是垂直优先

    if (Math.abs(end.x - start.x) > Math.abs(end.y - start.y)) {
      // 水平优先
      this.ctx.moveTo(start.x, start.y)
      this.ctx.lineTo(end.x, start.y)
      this.ctx.lineTo(end.x, end.y)
    } else {
      // 垂直优先
      this.ctx.moveTo(start.x, start.y)
      this.ctx.lineTo(start.x, end.y)
      this.ctx.lineTo(end.x, end.y)
    }
  }

  // 渲染箭头
  private renderArrow(connection: ConnectionState): void {
    if (!this.ctx || connection.path.length < 2) return

    const { arrow, path } = connection
    const start = path[0]
    const end = path[1]

    // 计算箭头角度
    const angle = Math.atan2(end.y - start.y, end.x - start.x)

    // 渲染起点箭头
    if (arrow.position === 'start' || arrow.position === 'both') {
      this.renderSingleArrow(start, angle + Math.PI, arrow)
    }

    // 渲染终点箭头
    if (arrow.position === 'end' || arrow.position === 'both') {
      this.renderSingleArrow(end, angle, arrow)
    }
  }

  // 渲染单个箭头
  private renderSingleArrow(
    position: { x: number; y: number },
    angle: number,
    arrow: ConnectionArrow
  ): void {
    if (!this.ctx) return

    this.ctx.save()
    this.ctx.translate(position.x, position.y)
    this.ctx.rotate(angle)

    this.ctx.fillStyle = arrow.style.fill
    this.ctx.strokeStyle = arrow.style.stroke
    this.ctx.lineWidth = arrow.style.strokeWidth

    this.ctx.beginPath()

    switch (arrow.type) {
      case 'arrow':
        this.ctx.moveTo(0, 0)
        this.ctx.lineTo(-arrow.size, -arrow.size / 2)
        this.ctx.lineTo(-arrow.size, arrow.size / 2)
        this.ctx.closePath()
        break
      case 'circle':
        this.ctx.arc(-arrow.size / 2, 0, arrow.size / 2, 0, Math.PI * 2)
        break
      case 'diamond':
        this.ctx.moveTo(0, 0)
        this.ctx.lineTo(-arrow.size, -arrow.size / 2)
        this.ctx.lineTo(-arrow.size * 2, 0)
        this.ctx.lineTo(-arrow.size, arrow.size / 2)
        this.ctx.closePath()
        break
      case 'square':
        this.ctx.rect(-arrow.size, -arrow.size / 2, arrow.size, arrow.size)
        break
    }

    this.ctx.fill()
    if (arrow.style.strokeWidth > 0) {
      this.ctx.stroke()
    }

    this.ctx.restore()
  }

  // 渲染标签
  private renderLabel(connection: ConnectionState): void {
    if (!this.ctx || connection.path.length < 2) return

    const { label, path } = connection
    const start = path[0]
    const end = path[1]

    // 计算标签位置
    let labelX: number, labelY: number
    switch (label.position) {
      case 'start':
        labelX = start.x + label.offset.x
        labelY = start.y + label.offset.y
        break
      case 'end':
        labelX = end.x + label.offset.x
        labelY = end.y + label.offset.y
        break
      case 'middle':
      default:
        labelX = (start.x + end.x) / 2 + label.offset.x
        labelY = (start.y + end.y) / 2 + label.offset.y
        break
    }

    // 设置文本样式
    this.ctx.font = `${label.style.fontSize}px ${label.style.fontFamily}`
    this.ctx.fillStyle = label.style.color
    this.ctx.textAlign = 'center'
    this.ctx.textBaseline = 'middle'

    // 绘制背景
    if (label.style.backgroundColor) {
      const metrics = this.ctx.measureText(label.text)
      const padding = label.style.padding
      const bgX = labelX - metrics.width / 2 - padding.left
      const bgY = labelY - label.style.fontSize / 2 - padding.top
      const bgWidth = metrics.width + padding.left + padding.right
      const bgHeight = label.style.fontSize + padding.top + padding.bottom

      this.ctx.fillStyle = label.style.backgroundColor
      this.ctx.beginPath()
      this.ctx.roundRect(bgX, bgY, bgWidth, bgHeight, label.style.borderRadius)
      this.ctx.fill()
    }

    // 绘制文本
    this.ctx.fillStyle = label.style.color
    this.ctx.fillText(label.text, labelX, labelY)
  }

  // 渲染数据流动画
  private renderDataFlow(connection: ConnectionState): void {
    if (!this.ctx || !connection.dataFlow || connection.path.length < 2) return

    const { dataFlow, path } = connection
    const start = path[0]
    const end = path[1]
    const ctx = this.ctx // 确保ctx不为null

    dataFlow.particles.forEach(particle => {
      // 计算粒子位置
      const x = start.x + (end.x - start.x) * particle.position
      const y = start.y + (end.y - start.y) * particle.position

      // 绘制粒子
      ctx.fillStyle = particle.color
      ctx.beginPath()
      ctx.arc(x, y, particle.size, 0, Math.PI * 2)
      ctx.fill()
    })
  }

  // 更新渲染统计信息
  private updateRenderStats(): void {
    const visibleConnections = this.connections.filter(conn => conn.isVisible)
    
    this.state.renderStats.totalConnections = this.connections.length
    this.state.renderStats.visibleConnections = visibleConnections.length
    
    // 计算FPS
    const now = performance.now()
    if (this.lastUpdateTime > 0) {
      const delta = now - this.lastUpdateTime
      this.state.renderStats.fps = Math.round(1000 / delta)
    }
  }

  // 添加连接
  public addConnection(connection: Connection, layoutInfo: ConnectionLayoutInfo): void {
    const connectionState: ConnectionState = {
      id: connection.id,
      from: connection.from,
      to: connection.to,
      style: this.getDefaultStyle(connection.type),
      label: this.getDefaultLabel(connection),
      animation: this.getDefaultAnimation(),
      arrow: this.getDefaultArrow(connection.type),
      path: layoutInfo.path,
      controlPoints: layoutInfo.controlPoints,
      isVisible: true,
      isHighlighted: false,
      isSelected: false,
      isHovered: false,
      zIndex: 0,
      dataFlow: this.getDefaultDataFlow()
    }

    this.state.connections.set(connection.id, connectionState)
  }

  // 更新连接
  public updateConnection(connectionId: string, updates: Partial<ConnectionState>): void {
    const connection = this.state.connections.get(connectionId)
    if (!connection) return

    Object.assign(connection, updates)
  }

  // 删除连接
  public removeConnection(connectionId: string): void {
    this.state.connections.delete(connectionId)
    this.state.selectedConnections.delete(connectionId)
    if (this.state.hoveredConnection === connectionId) {
      this.state.hoveredConnection = null
    }
  }

  // 选择连接
  public selectConnection(connectionId: string, multiSelect = false): void {
    if (!multiSelect) {
      this.state.selectedConnections.clear()
    }
    this.state.selectedConnections.add(connectionId)
    
    const connection = this.state.connections.get(connectionId)
    if (connection) {
      connection.isSelected = true
    }
  }

  // 取消选择连接
  public deselectConnection(connectionId: string): void {
    this.state.selectedConnections.delete(connectionId)
    
    const connection = this.state.connections.get(connectionId)
    if (connection) {
      connection.isSelected = false
    }
  }

  // 清除所有选择
  public clearSelection(): void {
    this.state.selectedConnections.forEach(connectionId => {
      const connection = this.state.connections.get(connectionId)
      if (connection) {
        connection.isSelected = false
      }
    })
    this.state.selectedConnections.clear()
  }

  // 高亮连接
  public highlightConnection(connectionId: string, highlighted = true): void {
    const connection = this.state.connections.get(connectionId)
    if (connection) {
      connection.isHighlighted = highlighted
    }
  }

  // 显示/隐藏连接
  public toggleConnectionVisibility(connectionId: string): void {
    const connection = this.state.connections.get(connectionId)
    if (connection) {
      connection.isVisible = !connection.isVisible
    }
  }

  // 更新配置
  public updateConfig(newConfig: Partial<RenderConfig>): void {
    Object.assign(this.state.config, newConfig)
  }

  // 获取默认样式
  private getDefaultStyle(connectionType?: string): ConnectionStyle {
    const baseStyle: ConnectionStyle = {
      type: 'curved',
      color: '#666666',
      width: 2,
      opacity: 0.8,
      lineCap: 'round',
      lineJoin: 'round'
    }

    // 根据连接类型调整样式
    switch (connectionType) {
      case 'data':
        baseStyle.color = '#4CAF50'
        baseStyle.width = 3
        break
      case 'control':
        baseStyle.color = '#2196F3'
        baseStyle.width = 2
        baseStyle.dashArray = '5,5'
        break
      case 'dependency':
        baseStyle.color = '#FF9800'
        baseStyle.width = 1
        break
      case 'error':
        baseStyle.color = '#F44336'
        baseStyle.width = 2
        break
    }

    return baseStyle
  }

  // 获取默认标签
  private getDefaultLabel(connection: Connection): ConnectionLabel {
    return {
      text: connection.label || '',
      position: 'middle',
      offset: { x: 0, y: -10 },
      style: {
        fontSize: 12,
        fontFamily: 'Arial, sans-serif',
        color: '#333333',
        backgroundColor: 'rgba(255, 255, 255, 0.8)',
        padding: { top: 2, right: 6, bottom: 2, left: 6 },
        borderRadius: 4
      },
      visible: !!connection.label
    }
  }

  // 获取默认动画
  private getDefaultAnimation(): ConnectionAnimation {
    return {
      type: 'none',
      duration: 1000,
      delay: 0,
      direction: 'forward',
      easing: 'linear',
      loop: true,
      paused: false
    }
  }

  // 获取默认箭头
  private getDefaultArrow(connectionType?: string): ConnectionArrow {
    const baseArrow: ConnectionArrow = {
      type: 'arrow',
      size: 8,
      position: 'end',
      style: {
        fill: '#666666',
        stroke: '#666666',
        strokeWidth: 1
      }
    }

    // 根据连接类型调整箭头
    switch (connectionType) {
      case 'data':
        baseArrow.type = 'arrow'
        baseArrow.size = 10
        break
      case 'control':
        baseArrow.type = 'circle'
        baseArrow.size = 6
        break
      case 'dependency':
        baseArrow.type = 'diamond'
        baseArrow.size = 8
        break
    }

    return baseArrow
  }

  // 获取默认数据流
  private getDefaultDataFlow(): ConnectionState['dataFlow'] {
    return {
      active: false,
      speed: 1,
      particles: []
    }
  }

  // 事件处理方法
  private handleClick(event: MouseEvent): void {
    if (!this.state.config.interaction.clickEnabled) return

    const connectionId = this.getConnectionAtPosition(event.offsetX, event.offsetY)
    if (connectionId) {
      this.emitEvent('connection-click', { connectionId, event })
    }
  }

  private handleMouseMove(event: MouseEvent): void {
    if (!this.state.config.interaction.hoverEnabled) return

    const connectionId = this.getConnectionAtPosition(event.offsetX, event.offsetY)
    
    if (connectionId !== this.state.hoveredConnection) {
      // 清除之前的悬停状态
      if (this.state.hoveredConnection) {
        const prevConnection = this.state.connections.get(this.state.hoveredConnection)
        if (prevConnection) {
          prevConnection.isHovered = false
        }
        this.emitEvent('connection-hover', {
          connectionId: this.state.hoveredConnection,
          event,
          isEntering: false
        })
      }

      // 设置新的悬停状态
      this.state.hoveredConnection = connectionId
      if (connectionId) {
        const connection = this.state.connections.get(connectionId)
        if (connection) {
          connection.isHovered = true
        }
        this.emitEvent('connection-hover', {
          connectionId,
          event,
          isEntering: true
        })
      }
    }
  }

  private handleMouseDown(event: MouseEvent): void {
    if (!this.state.config.interaction.dragEnabled) return

    const connectionId = this.getConnectionAtPosition(event.offsetX, event.offsetY)
    if (connectionId) {
      this.emitEvent('connection-drag', {
        connectionId,
        event,
        position: { x: event.offsetX, y: event.offsetY }
      })
    }
  }

  private handleMouseUp(event: MouseEvent): void {
    // 处理鼠标释放事件
  }

  private handleResize(): void {
    this.updateCanvasSize()
  }

  // 获取指定位置的连接
  private getConnectionAtPosition(x: number, y: number): string | null {
    // 简化实现，返回第一个匹配的连接
    for (const [connectionId, connection] of this.state.connections) {
      if (this.isPointNearConnection(x, y, connection)) {
        return connectionId
      }
    }
    return null
  }

  // 判断点是否靠近连接
  private isPointNearConnection(x: number, y: number, connection: ConnectionState): boolean {
    if (connection.path.length < 2) return false

    const threshold = 5 // 阈值距离
    const start = connection.path[0]
    const end = connection.path[1]

    // 计算点到线段的距离
    const distance = this.pointToLineDistance(x, y, start.x, start.y, end.x, end.y)
    return distance <= threshold
  }

  // 计算点到线段的距离
  private pointToLineDistance(
    px: number, py: number,
    x1: number, y1: number,
    x2: number, y2: number
  ): number {
    const A = px - x1
    const B = py - y1
    const C = x2 - x1
    const D = y2 - y1

    const dot = A * C + B * D
    const lenSq = C * C + D * D
    let param = -1

    if (lenSq !== 0) {
      param = dot / lenSq
    }

    let xx, yy

    if (param < 0) {
      xx = x1
      yy = y1
    } else if (param > 1) {
      xx = x2
      yy = y2
    } else {
      xx = x1 + param * C
      yy = y1 + param * D
    }

    const dx = px - xx
    const dy = py - yy

    return Math.sqrt(dx * dx + dy * dy)
  }

  // 事件监听
  public addEventListener<K extends keyof ConnectionRendererEvents>(
    event: K,
    listener: (event: CustomEvent<ConnectionRendererEvents[K]>) => void
  ): void {
    this.eventTarget.addEventListener(event, listener as EventListener)
  }

  // 移除事件监听
  public removeEventListener<K extends keyof ConnectionRendererEvents>(
    event: K,
    listener: (event: CustomEvent<ConnectionRendererEvents[K]>) => void
  ): void {
    this.eventTarget.removeEventListener(event, listener as EventListener)
  }

  // 私有方法：触发事件
  private emitEvent<K extends keyof ConnectionRendererEvents>(
    event: K,
    detail: ConnectionRendererEvents[K]
  ): void {
    this.eventTarget.dispatchEvent(new CustomEvent(event, { detail }))
  }
}

// 导出单例实例
export const connectionRenderer = ConnectionRenderer.getInstance()

export default connectionRenderer
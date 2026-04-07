import { reactive, ref, computed } from 'vue'
import type { Node } from '../../../api/modules/nodes'
import type { Connection } from '../../../api/modules/connections'

/**
 * 节点布局管理器
 * 负责计算和管理节点的位置、大小和布局
 */

// 布局配置接口
export interface LayoutConfig {
  mode: 'manual' | 'auto' | 'hierarchical' | 'force-directed'
  algorithm: 'grid' | 'tree' | 'circular' | 'force'
  spacing: {
    horizontal: number
    vertical: number
  }
  alignment: 'left' | 'center' | 'right'
  direction: 'horizontal' | 'vertical'
  autoArrange: boolean
  snapToGrid: boolean
  gridSize: number
  padding: {
    top: number
    right: number
    bottom: number
    left: number
  }
}

// 层配置接口
export interface LayerConfig {
  id: string
  name: string
  color: string
  position: 'top' | 'bottom' | 'left' | 'right'
  spacing: number
  visible: boolean
  locked: boolean
}

// 布局约束接口
export interface LayoutConstraints {
  minWidth: number
  minHeight: number
  maxWidth: number
  maxHeight: number
  aspectRatio?: number
  preventOverlap: boolean
  maintainConnection: boolean
  boundary: {
    x: number
    y: number
    width: number
    height: number
  }
}

// 节点布局信息接口
export interface NodeLayoutInfo {
  nodeId: string
  position: { x: number; y: number }
  size: { width: number; height: number }
  layer: string
  zIndex: number
  isVisible: boolean
  isLocked: boolean
  connections: {
    incoming: number
    outgoing: number
  }
  lastUpdated?: string
}

// 连接布局信息接口
export interface ConnectionLayoutInfo {
  connectionId: string
  from: string
  to: string
  path: Array<{ x: number; y: number }>
  controlPoints: Array<{ x: number; y: number }>
  labelPosition: { x: number; y: number }
  isVisible: boolean
  zIndex: number
}

// 布局统计信息接口
export interface LayoutStats {
  totalNodes: number
  visibleNodes: number
  totalConnections: number
  visibleConnections: number
  canvasSize: { width: number; height: number }
  usedArea: { x: number; y: number; width: number; height: number }
  density: number
  complexity: 'low' | 'medium' | 'high'
}

// 事件类型定义
export interface LayoutManagerEvents {
  'layout-changed': { nodes: NodeLayoutInfo[]; connections: ConnectionLayoutInfo[] }
  'node-position-changed': { nodeId: string; oldPosition: { x: number; y: number }; newPosition: { x: number; y: number } }
  'node-size-changed': { nodeId: string; oldSize: { width: number; height: number }; newSize: { width: number; height: number } }
  'layer-changed': { layerId: string; oldConfig: LayerConfig; newConfig: LayerConfig }
  'layout-completed': { algorithm: string; duration: number; stats: LayoutStats }
  'error-occurred': { type: string; message: string; nodeId?: string }
}

class NodeLayoutManager {
  private static instance: NodeLayoutManager
  private eventTarget: EventTarget
  private animationFrame: number | null = null
  
  // 响应式状态
  public state = reactive<{
    nodes: Map<string, NodeLayoutInfo>
    connections: Map<string, ConnectionLayoutInfo>
    layers: Map<string, LayerConfig>
    config: LayoutConfig
    constraints: LayoutConstraints
    stats: LayoutStats | null
    isLayouting: boolean
    selectedNodes: Set<string>
    clipboard: {
      nodes: string[]
      connections: string[]
    }
  }>({
    nodes: new Map(),
    connections: new Map(),
    layers: new Map(),
    config: {
      mode: 'auto',
      algorithm: 'force',
      spacing: {
        horizontal: 50,
        vertical: 50
      },
      alignment: 'center',
      direction: 'vertical',
      autoArrange: true,
      snapToGrid: false,
      gridSize: 20,
      padding: {
        top: 20,
        right: 20,
        bottom: 20,
        left: 20
      }
    },
    constraints: {
      minWidth: 100,
      minHeight: 60,
      maxWidth: 2000,
      maxHeight: 2000,
      preventOverlap: true,
      maintainConnection: true,
      boundary: {
        x: 0,
        y: 0,
        width: 2000,
        height: 2000
      }
    },
    stats: null,
    isLayouting: false,
    selectedNodes: new Set(),
    clipboard: {
      nodes: [],
      connections: []
    }
  })

  // 计算属性
  public get nodes() {
    return Array.from(this.state.nodes.values())
  }

  public get connections() {
    return Array.from(this.state.connections.values())
  }

  public get layers() {
    return Array.from(this.state.layers.values())
  }

  public get config() {
    return this.state.config
  }

  public get constraints() {
    return this.state.constraints
  }

  public get stats() {
    return this.state.stats
  }

  public get isLayouting() {
    return this.state.isLayouting
  }

  public get selectedNodes() {
    return Array.from(this.state.selectedNodes)
  }

  public get clipboard() {
    return this.state.clipboard
  }

  // 单例模式
  public static getInstance(): NodeLayoutManager {
    if (!NodeLayoutManager.instance) {
      NodeLayoutManager.instance = new NodeLayoutManager()
    }
    return NodeLayoutManager.instance
  }

  // 私有构造函数
  private constructor() {
    this.eventTarget = new EventTarget()
    this.initializeDefaultLayers()
  }

  // 初始化默认层
  private initializeDefaultLayers(): void {
    const defaultLayers: LayerConfig[] = [
      {
        id: 'data-layer',
        name: '数据层',
        color: '#4CAF50',
        position: 'bottom',
        spacing: 100,
        visible: true,
        locked: false
      },
      {
        id: 'processing-layer',
        name: '处理层',
        color: '#2196F3',
        position: 'bottom',
        spacing: 80,
        visible: true,
        locked: false
      },
      {
        id: 'strategy-layer',
        name: '策略层',
        color: '#FF9800',
        position: 'bottom',
        spacing: 60,
        visible: true,
        locked: false
      },
      {
        id: 'analysis-layer',
        name: '分析层',
        color: '#9C27B0',
        position: 'bottom',
        spacing: 40,
        visible: true,
        locked: false
      },
      {
        id: 'visualization-layer',
        name: '可视化层',
        color: '#673AB7',
        position: 'top',
        spacing: 30,
        visible: true,
        locked: false
      }
    ]

    defaultLayers.forEach(layer => {
      this.state.layers.set(layer.id, layer)
    })
  }

  // 添加节点
  public addNode(node: Node, layerId?: string): void {
    const layoutInfo: NodeLayoutInfo = {
      nodeId: node.id,
      position: node.position || { x: 0, y: 0 },
      size: node.size || { width: 120, height: 80 },
      layer: layerId || this.getDefaultLayerForNodeType(node.type),
      zIndex: this.calculateZIndex(node.type),
      isVisible: true,
      isLocked: false,
      connections: {
        incoming: 0,
        outgoing: 0
      }
    }

    this.state.nodes.set(node.id, layoutInfo)
    this.updateNodeConnections(node.id)
    this.updateStats()
    
    if (this.state.config.autoArrange) {
      this.arrangeNodes()
    }
  }

  // 更新节点
  public updateNode(nodeId: string, updates: Partial<NodeLayoutInfo>): void {
    const node = this.state.nodes.get(nodeId)
    if (!node) return

    const oldPosition = { ...node.position }
    const oldSize = { ...node.size }

    Object.assign(node, updates)
    node.lastUpdated = new Date().toISOString()

    if (updates.position && 
        (updates.position.x !== oldPosition.x || updates.position.y !== oldPosition.y)) {
      this.emitEvent('node-position-changed', {
        nodeId,
        oldPosition,
        newPosition: updates.position
      })
    }

    if (updates.size && 
        (updates.size.width !== oldSize.width || updates.size.height !== oldSize.height)) {
      this.emitEvent('node-size-changed', {
        nodeId,
        oldSize,
        newSize: updates.size
      })
    }

    this.updateStats()
  }

  // 删除节点
  public removeNode(nodeId: string): void {
    this.state.nodes.delete(nodeId)
    this.state.selectedNodes.delete(nodeId)
    this.updateAllConnections()
    this.updateStats()
  }

  // 选择节点
  public selectNode(nodeId: string, multiSelect = false): void {
    if (!multiSelect) {
      this.state.selectedNodes.clear()
    }
    this.state.selectedNodes.add(nodeId)
  }

  // 取消选择节点
  public deselectNode(nodeId: string): void {
    this.state.selectedNodes.delete(nodeId)
  }

  // 清除所有选择
  public clearSelection(): void {
    this.state.selectedNodes.clear()
  }

  // 移动节点
  public moveNode(nodeId: string, deltaX: number, deltaY: number): void {
    const node = this.state.nodes.get(nodeId)
    if (!node || node.isLocked) return

    const newPosition = {
      x: Math.max(this.state.constraints.boundary.x, 
              Math.min(this.state.constraints.boundary.x + this.state.constraints.boundary.width - node.size.width,
                      node.position.x + deltaX)),
      y: Math.max(this.state.constraints.boundary.y, 
              Math.min(this.state.constraints.boundary.y + this.state.constraints.boundary.height - node.size.height,
                      node.position.y + deltaY))
    }

    // 网格对齐
    if (this.state.config.snapToGrid) {
      newPosition.x = Math.round(newPosition.x / this.state.config.gridSize) * this.state.config.gridSize
      newPosition.y = Math.round(newPosition.y / this.state.config.gridSize) * this.state.config.gridSize
    }

    this.updateNode(nodeId, { position: newPosition })
  }

  // 调整节点大小
  public resizeNode(nodeId: string, width: number, height: number): void {
    const node = this.state.nodes.get(nodeId)
    if (!node || node.isLocked) return

    const newSize = {
      width: Math.max(this.state.constraints.minWidth, 
                  Math.min(this.state.constraints.maxWidth, width)),
      height: Math.max(this.state.constraints.minHeight, 
                   Math.min(this.state.constraints.maxHeight, height))
    }

    // 保持宽高比
    if (this.state.constraints.aspectRatio) {
      const aspectRatio = this.state.constraints.aspectRatio
      if (width / height > aspectRatio) {
        newSize.width = height * aspectRatio
      } else {
        newSize.height = width / aspectRatio
      }
    }

    this.updateNode(nodeId, { size: newSize })
  }

  // 锁定/解锁节点
  public toggleNodeLock(nodeId: string): void {
    const node = this.state.nodes.get(nodeId)
    if (!node) return

    node.isLocked = !node.isLocked
  }

  // 显示/隐藏节点
  public toggleNodeVisibility(nodeId: string): void {
    const node = this.state.nodes.get(nodeId)
    if (!node) return

    node.isVisible = !node.isVisible
    this.updateStats()
  }

  // 添加连接
  public addConnection(connection: Connection): void {
    const layoutInfo: ConnectionLayoutInfo = {
      connectionId: connection.id,
      from: connection.from,
      to: connection.to,
      path: this.calculateConnectionPath(connection),
      controlPoints: this.calculateControlPoints(connection),
      labelPosition: this.calculateLabelPosition(connection),
      isVisible: true,
      zIndex: this.calculateConnectionZIndex(connection)
    }

    this.state.connections.set(connection.id, layoutInfo)
    this.updateNodeConnections(connection.from)
    this.updateNodeConnections(connection.to)
    this.updateStats()
  }

  // 更新连接
  public updateConnection(connectionId: string, updates: Partial<ConnectionLayoutInfo>): void {
    const connection = this.state.connections.get(connectionId)
    if (!connection) return

    Object.assign(connection, updates)
    this.updateStats()
  }

  // 删除连接
  public removeConnection(connectionId: string): void {
    const connection = this.state.connections.get(connectionId)
    if (!connection) return

    this.state.connections.delete(connectionId)
    this.updateAllConnections()
    this.updateStats()
  }

  // 自动排列节点
  public arrangeNodes(algorithm?: string): void {
    this.state.isLayouting = true
    const startTime = Date.now()

    try {
      const layoutAlgorithm = algorithm || this.state.config.algorithm
      
      switch (layoutAlgorithm) {
        case 'grid':
          this.applyGridLayout()
          break
        case 'tree':
          this.applyTreeLayout()
          break
        case 'circular':
          this.applyCircularLayout()
          break
        case 'force':
          this.applyForceLayout()
          break
        default:
          this.applyForceLayout()
      }

      const duration = Date.now() - startTime
      this.emitEvent('layout-completed', {
        algorithm: layoutAlgorithm,
        duration,
        stats: this.calculateLayoutStats()
      })
    } finally {
      this.state.isLayouting = false
    }
  }

  // 应用网格布局
  private applyGridLayout(): void {
    const nodes = Array.from(this.state.nodes.values())
    const { spacing, alignment, direction } = this.state.config
    const { padding } = this.state.config

    let currentX = padding.left
    let currentY = padding.top
    let maxWidth = 0

    nodes.forEach((node, index) => {
      if (direction === 'horizontal' && index > 0) {
        currentX += spacing.horizontal
      } else if (direction === 'vertical' && index > 0) {
        currentY += spacing.vertical
      }

      // 对齐处理
      if (alignment === 'center') {
        // 居中对齐逻辑
      } else if (alignment === 'right') {
        // 右对齐逻辑
      }

      node.position = { x: currentX, y: currentY }
      maxWidth = Math.max(maxWidth, node.size.width)

      if (direction === 'horizontal') {
        currentX += node.size.width
      } else {
        currentY += node.size.height
      }
    })
  }

  // 应用树形布局
  private applyTreeLayout(): void {
    // 简化的树形布局实现
    const nodes = Array.from(this.state.nodes.values())
    const { spacing } = this.state.config
    const { padding } = this.state.config

    // 找到根节点（没有输入连接的节点）
    const rootNodes = nodes.filter(node => 
      this.getNodeIncomingConnections(node.nodeId).length === 0
    )

    // 递归布局子节点
    const layoutSubtree = (nodeId: string, x: number, y: number, level: number): void => {
      const node = this.state.nodes.get(nodeId)
      if (!node) return

      node.position = { x, y }
      
      const children = this.getNodeOutgoingConnections(nodeId)
      const childSpacing = spacing.vertical * Math.pow(0.8, level) // 随层级减少间距

      children.forEach((child, index) => {
        const childX = x + node.size.width + spacing.horizontal
        const childY = y + index * childSpacing
        layoutSubtree(child, childX, childY, level + 1)
      })
    }

    rootNodes.forEach((root, index) => {
      const rootX = padding.left + index * 200
      const rootY = padding.top
      layoutSubtree(root.nodeId, rootX, rootY, 0)
    })
  }

  // 应用圆形布局
  private applyCircularLayout(): void {
    const nodes = Array.from(this.state.nodes.values())
    const centerX = this.state.constraints.boundary.width / 2
    const centerY = this.state.constraints.boundary.height / 2
    const radius = Math.min(centerX, centerY) - 100

    nodes.forEach((node, index) => {
      const angle = (2 * Math.PI * index) / nodes.length
      const x = centerX + radius * Math.cos(angle) - node.size.width / 2
      const y = centerY + radius * Math.sin(angle) - node.size.height / 2
      
      node.position = { x, y }
    })
  }

  // 应用力导向布局
  private applyForceLayout(): void {
    // 简化的力导向布局实现
    const nodes = Array.from(this.state.nodes.values())
    const iterations = 50
    const k = Math.sqrt((this.state.constraints.boundary.width * this.state.constraints.boundary.height) / nodes.length)
    const c = 0.1
    const centerX = this.state.constraints.boundary.width / 2
    const centerY = this.state.constraints.boundary.height / 2

    // 初始化随机位置
    nodes.forEach(node => {
      if (!node.position.x || !node.position.y) {
        node.position = {
          x: Math.random() * (this.state.constraints.boundary.width - node.size.width),
          y: Math.random() * (this.state.constraints.boundary.height - node.size.height)
        }
      }
    })

    // 迭代计算
    for (let iter = 0; iter < iterations; iter++) {
      const forces = new Map<string, { x: number; y: number }>()

      // 计算斥力
      nodes.forEach((node1, i) => {
        let fx = 0, fy = 0
        
        nodes.forEach((node2, j) => {
          if (i !== j) {
            const dx = node1.position.x - node2.position.x
            const dy = node1.position.y - node2.position.y
            const distance = Math.sqrt(dx * dx + dy * dy)
            
            if (distance > 0) {
              const force = (k * k) / distance
              fx += (dx / distance) * force
              fy += (dy / distance) * force
            }
          }
        })

        forces.set(node1.nodeId, { x: fx, y: fy })
      })

      // 计算引力（向中心）
      nodes.forEach(node => {
        const dx = centerX - node.position.x
        const dy = centerY - node.position.y
        const force = c * Math.sqrt(dx * dx + dy * dy)
        
        const existingForce = forces.get(node.nodeId) || { x: 0, y: 0 }
        existingForce.x += dx * force
        existingForce.y += dy * force
        
        forces.set(node.nodeId, existingForce)
      })

      // 更新位置
      nodes.forEach(node => {
        const force = forces.get(node.nodeId)
        if (force) {
          node.position.x += force.x
          node.position.y += force.y
          
          // 限制在边界内
          node.position.x = Math.max(this.state.constraints.boundary.x, 
                              Math.min(this.state.constraints.boundary.x + this.state.constraints.boundary.width - node.size.width,
                                          node.position.x))
          node.position.y = Math.max(this.state.constraints.boundary.y, 
                              Math.min(this.state.constraints.boundary.y + this.state.constraints.boundary.height - node.size.height,
                                          node.position.y))
        }
      })
    }
  }

  // 计算连接路径
  private calculateConnectionPath(connection: Connection): Array<{ x: number; y: number }> {
    const fromNode = this.state.nodes.get(connection.from)
    const toNode = this.state.nodes.get(connection.to)
    
    if (!fromNode || !toNode) {
      return []
    }

    const fromCenter = {
      x: fromNode.position.x + fromNode.size.width / 2,
      y: fromNode.position.y + fromNode.size.height / 2
    }
    
    const toCenter = {
      x: toNode.position.x + toNode.size.width / 2,
      y: toNode.position.y + toNode.size.height / 2
    }

    return [fromCenter, toCenter]
  }

  // 计算控制点
  private calculateControlPoints(connection: Connection): Array<{ x: number; y: number }> {
    // 简化实现，返回空数组
    return []
  }

  // 计算标签位置
  private calculateLabelPosition(connection: Connection): { x: number; y: number } {
    const path = this.calculateConnectionPath(connection)
    if (path.length < 2) {
      return { x: 0, y: 0 }
    }

    const midX = (path[0].x + path[1].x) / 2
    const midY = (path[0].y + path[1].y) / 2

    return { x: midX, y: midY }
  }

  // 计算Z索引
  private calculateZIndex(nodeType: string): number {
    const layerOrder = ['data-layer', 'processing-layer', 'strategy-layer', 'analysis-layer', 'visualization-layer']
    const typeToLayer: Record<string, number> = {
      'data_source': 0,
      'data_processing': 1,
      'strategy': 2,
      'backtest': 2,
      'analysis': 3,
      'visualization': 4,
      'export': 4
    }
    
    return typeToLayer[nodeType] || 0
  }

  // 计算连接Z索引
  private calculateConnectionZIndex(connection: Connection): number {
    return 0 // 简化实现
  }

  // 获取节点输入连接数
  private getNodeIncomingConnections(nodeId: string): string[] {
    const connections: string[] = []
    
    this.state.connections.forEach(connection => {
      if (connection.to === nodeId) {
        connections.push(connection.from)
      }
    })
    
    return connections
  }

  // 获取节点输出连接数
  private getNodeOutgoingConnections(nodeId: string): string[] {
    const connections: string[] = []
    
    this.state.connections.forEach(connection => {
      if (connection.from === nodeId) {
        connections.push(connection.to)
      }
    })
    
    return connections
  }

  // 更新节点连接信息
  private updateNodeConnections(nodeId: string): void {
    const node = this.state.nodes.get(nodeId)
    if (!node) return

    node.connections.incoming = this.getNodeIncomingConnections(nodeId).length
    node.connections.outgoing = this.getNodeOutgoingConnections(nodeId).length
  }

  // 更新所有节点连接信息
  private updateAllConnections(): void {
    this.state.nodes.forEach((_, nodeId) => {
      this.updateNodeConnections(nodeId)
    })
  }

  // 获取节点类型的默认层
  private getDefaultLayerForNodeType(nodeType: string): string {
    const typeToLayer: Record<string, string> = {
      'data_source': 'data-layer',
      'data_processing': 'processing-layer',
      'strategy': 'strategy-layer',
      'backtest': 'strategy-layer',
      'analysis': 'analysis-layer',
      'visualization': 'visualization-layer',
      'export': 'visualization-layer'
    }
    
    return typeToLayer[nodeType] || 'processing-layer'
  }

  // 计算布局统计
  private calculateLayoutStats(): LayoutStats {
    const nodes = Array.from(this.state.nodes.values())
    const connections = Array.from(this.state.connections.values())
    const visibleNodes = nodes.filter(node => node.isVisible)
    const visibleConnections = connections.filter(conn => conn.isVisible)

    // 计算使用区域
    let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity
    visibleNodes.forEach(node => {
      minX = Math.min(minX, node.position.x)
      minY = Math.min(minY, node.position.y)
      maxX = Math.max(maxX, node.position.x + node.size.width)
      maxY = Math.max(maxY, node.position.y + node.size.height)
    })

    const usedArea = {
      x: minX === Infinity ? 0 : minX,
      y: minY === Infinity ? 0 : minY,
      width: maxX === -Infinity ? 0 : maxX - minX,
      height: maxY === -Infinity ? 0 : maxY - minY
    }

    // 计算密度
    const canvasArea = this.state.constraints.boundary.width * this.state.constraints.boundary.height
    const density = canvasArea > 0 ? (visibleNodes.length / canvasArea) * 10000 : 0

    // 计算复杂度
    const totalConnections = visibleNodes.reduce((sum, node) => sum + node.connections.incoming + node.connections.outgoing, 0)
    const avgConnections = visibleNodes.length > 0 ? totalConnections / visibleNodes.length : 0
    let complexity: 'low' | 'medium' | 'high' = 'low'
    
    if (avgConnections > 4) {
      complexity = 'high'
    } else if (avgConnections > 2) {
      complexity = 'medium'
    }

    return {
      totalNodes: nodes.length,
      visibleNodes: visibleNodes.length,
      totalConnections: connections.length,
      visibleConnections: visibleConnections.length,
      canvasSize: {
        width: this.state.constraints.boundary.width,
        height: this.state.constraints.boundary.height
      },
      usedArea,
      density,
      complexity
    }
  }

  // 更新统计信息
  private updateStats(): void {
    this.state.stats = this.calculateLayoutStats()
  }

  // 更新配置
  public updateConfig(newConfig: Partial<LayoutConfig>): void {
    Object.assign(this.state.config, newConfig)
    
    if (newConfig.autoArrange) {
      this.arrangeNodes()
    }
  }

  // 更新约束
  public updateConstraints(newConstraints: Partial<LayoutConstraints>): void {
    Object.assign(this.state.constraints, newConstraints)
  }

  // 添加层
  public addLayer(layer: LayerConfig): void {
    this.state.layers.set(layer.id, layer)
    this.emitEvent('layer-changed', { 
      layerId: layer.id, 
      oldConfig: {} as LayerConfig, 
      newConfig: layer 
    })
  }

  // 更新层
  public updateLayer(layerId: string, updates: Partial<LayerConfig>): void {
    const layer = this.state.layers.get(layerId)
    if (!layer) return

    const oldConfig = { ...layer }
    Object.assign(layer, updates)
    
    this.emitEvent('layer-changed', { 
      layerId, 
      oldConfig, 
      newConfig: { ...layer } 
    })
  }

  // 删除层
  public removeLayer(layerId: string): void {
    const layer = this.state.layers.get(layerId)
    if (!layer) return

    this.state.layers.delete(layerId)
    this.emitEvent('layer-changed', { 
      layerId, 
      oldConfig: layer, 
      newConfig: {} as LayerConfig 
    })
  }

  // 复制节点
  public copyNodes(): void {
    this.state.clipboard.nodes = Array.from(this.state.selectedNodes)
    this.state.clipboard.connections = []
  }

  // 粘贴节点
  public pasteNodes(offsetX = 0, offsetY = 0): void {
    const copiedNodes = this.state.clipboard.nodes
    const copiedConnections = this.state.clipboard.connections

    // 创建新节点ID映射
    const idMap = new Map<string, string>()
    copiedNodes.forEach(oldId => {
      idMap.set(oldId, `node-${Date.now()}-${Math.random()}`)
    })

    // 复制节点
    copiedNodes.forEach(oldId => {
      const node = this.state.nodes.get(oldId)
      if (node) {
        const newNode = {
          ...node,
          nodeId: idMap.get(oldId)!,
          position: {
            x: node.position.x + offsetX,
            y: node.position.y + offsetY
          }
        }
        this.state.nodes.set(newNode.nodeId, newNode)
      }
    })

    // 复制连接
    copiedConnections.forEach(oldConnectionId => {
      const connection = this.state.connections.get(oldConnectionId)
      if (connection) {
        const newConnection = {
          ...connection,
          connectionId: `connection-${Date.now()}-${Math.random()}`,
          from: idMap.get(connection.from) || connection.from,
          to: idMap.get(connection.to) || connection.to
        }
        this.state.connections.set(newConnection.connectionId, newConnection)
      }
    })

    // 选择新粘贴的节点
    this.clearSelection()
    copiedNodes.forEach(oldId => {
      this.selectNode(idMap.get(oldId)!, true)
    })
  }

  // 缩放到适应
  public fitToScreen(): void {
    const nodes = Array.from(this.state.nodes.values())
    if (nodes.length === 0) return

    let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity

    nodes.forEach(node => {
      minX = Math.min(minX, node.position.x)
      minY = Math.min(minY, node.position.y)
      maxX = Math.max(maxX, node.position.x + node.size.width)
      maxY = Math.max(maxY, node.position.y + node.size.height)
    })

    const contentWidth = maxX - minX
    const contentHeight = maxY - minY
    const padding = 50

    // 计算缩放比例
    const scaleX = (this.state.constraints.boundary.width - padding * 2) / contentWidth
    const scaleY = (this.state.constraints.boundary.height - padding * 2) / contentHeight
    const scale = Math.min(scaleX, scaleY, 1) // 不放大，只缩小

    if (scale < 1) {
      const centerX = (minX + maxX) / 2
      const centerY = (minY + maxY) / 2
      const newCenterX = this.state.constraints.boundary.width / 2
      const newCenterY = this.state.constraints.boundary.height / 2

      const offsetX = newCenterX - centerX * scale
      const offsetY = newCenterY - centerY * scale

      nodes.forEach(node => {
        node.position.x = (node.position.x - minX) * scale + offsetX
        node.position.y = (node.position.y - minY) * scale + offsetY
      })
    }
  }

  // 事件监听
  public addEventListener<K extends keyof LayoutManagerEvents>(
    event: K,
    listener: (event: CustomEvent<LayoutManagerEvents[K]>) => void
  ): void {
    this.eventTarget.addEventListener(event, listener as EventListener)
  }

  // 移除事件监听
  public removeEventListener<K extends keyof LayoutManagerEvents>(
    event: K,
    listener: (event: CustomEvent<LayoutManagerEvents[K]>) => void
  ): void {
    this.eventTarget.removeEventListener(event, listener as EventListener)
  }

  // 私有方法：触发事件
  private emitEvent<K extends keyof LayoutManagerEvents>(
    event: K,
    detail: LayoutManagerEvents[K]
  ): void {
    this.eventTarget.dispatchEvent(new CustomEvent(event, { detail }))
  }
}

// 导出单例实例
export const nodeLayoutManager = NodeLayoutManager.getInstance()

export default nodeLayoutManager
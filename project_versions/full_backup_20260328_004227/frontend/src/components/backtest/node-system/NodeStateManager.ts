import { reactive, ref, computed } from 'vue'
import type { Node } from '../../../api/modules/nodes'
import type { Connection } from '../../../api/modules/connections'

/**
 * 节点状态管理器
 * 管理所有节点的状态、依赖关系和激活条件
 */

// 节点状态接口
export interface NodeState {
  id: string
  type: string
  title: string
  status: 'inactive' | 'active' | 'running' | 'completed' | 'error' | 'disabled'
  position: { x: number; y: number }
  size: { width: number; height: number }
  dependencies: string[] // 依赖的节点ID列表
  dependents: string[] // 被依赖的节点ID列表
  isRequired: boolean // 是否为必需节点
  isConfigured: boolean // 是否已配置
  isValid: boolean // 配置是否有效
  errorMessage?: string // 错误信息
  progress: number // 执行进度 (0-100)
  lastUpdated: string // 最后更新时间
  metadata: {
    category: string
    tags: string[]
    version: string
  }
}

// 连接状态接口
export interface ConnectionState {
  id: string
  from: string
  to: string
  type: 'data' | 'control' | 'event'
  status: 'inactive' | 'active' | 'error' | 'pending'
  isValid: boolean
  dataFlow?: {
    isActive: boolean
    bytesTransferred: number
    transferRate: number
  }
  styling: {
    color?: string
    width?: number
    style?: 'solid' | 'dashed' | 'dotted'
  }
}

// 状态管理器配置接口
export interface StateManagerConfig {
  autoValidate: boolean
  autoUpdateDependencies: boolean
  maxHistorySize: number
  refreshInterval: number
}

// 事件类型定义
export interface StateManagerEvents {
  'node-state-changed': { nodeId: string; oldState: NodeState; newState: NodeState }
  'node-activated': { nodeId: string }
  'node-deactivated': { nodeId: string }
  'dependency-added': { nodeId: string; dependencyId: string }
  'dependency-removed': { nodeId: string; dependencyId: string }
  'connection-state-changed': { connectionId: string; oldState: ConnectionState; newState: ConnectionState }
  'validation-completed': { nodeId: string; isValid: boolean; errors: string[] }
  'error-occurred': { type: string; message: string; nodeId?: string }
}

class NodeStateManager {
  private static instance: NodeStateManager
  private eventTarget: EventTarget
  private refreshTimer: number | null = null
  
  // 响应式状态
  public state = reactive<{
    nodes: Map<string, NodeState>
    connections: Map<string, ConnectionState>
    nodeHistory: Map<string, NodeState[]>
    globalErrors: Array<{
      id: string
      type: string
      message: string
      timestamp: string
      nodeId?: string
    }>
    isLoading: boolean
  }>({
    nodes: new Map(),
    connections: new Map(),
    nodeHistory: new Map(),
    globalErrors: [],
    isLoading: false
  })

  // 配置
  public config = reactive<StateManagerConfig>({
    autoValidate: true,
    autoUpdateDependencies: true,
    maxHistorySize: 50,
    refreshInterval: 30000 // 30秒
  })

  // 计算属性
  public get nodes() {
    return Array.from(this.state.nodes.values())
  }

  public get connections() {
    return Array.from(this.state.connections.values())
  }

  public get activeNodes() {
    return Array.from(this.state.nodes.values()).filter(node => 
      node.status === 'active' || node.status === 'running'
    )
  }

  public get inactiveNodes() {
    return Array.from(this.state.nodes.values()).filter(node => 
      node.status === 'inactive'
    )
  }

  public get errorNodes() {
    return Array.from(this.state.nodes.values()).filter(node => 
      node.status === 'error'
    )
  }

  public get completedNodes() {
    return Array.from(this.state.nodes.values()).filter(node => 
      node.status === 'completed'
    )
  }

  public get activeConnections() {
    return Array.from(this.state.connections.values()).filter(conn => 
      conn.status === 'active'
    )
  }

  public get errorConnections() {
    return Array.from(this.state.connections.values()).filter(conn => 
      conn.status === 'error'
    )
  }

  public get globalErrors() {
    return this.state.globalErrors
  }

  public get isLoading() {
    return this.state.isLoading
  }

  // 单例模式
  public static getInstance(): NodeStateManager {
    if (!NodeStateManager.instance) {
      NodeStateManager.instance = new NodeStateManager()
    }
    return NodeStateManager.instance
  }

  // 私有构造函数
  private constructor() {
    this.eventTarget = new EventTarget()
    this.startAutoRefresh()
  }

  // 添加或更新节点
  public addOrUpdateNode(nodeData: Partial<Node> & { id: string }): void {
    const existingNode = this.state.nodes.get(nodeData.id)
    const oldState = existingNode ? { ...existingNode } : null
    
    const newNode: NodeState = {
      id: nodeData.id,
      type: nodeData.type || 'unknown',
      title: nodeData.title || '未命名节点',
      status: existingNode?.status || 'inactive',
      position: nodeData.position || { x: 0, y: 0 },
      size: nodeData.size || { width: 120, height: 80 },
      dependencies: existingNode?.dependencies || [],
      dependents: existingNode?.dependents || [],
      isRequired: nodeData.metadata?.tags?.includes('required') || false,
      isConfigured: this.isNodeConfigured(nodeData),
      isValid: true,
      progress: existingNode?.progress || 0,
      lastUpdated: new Date().toISOString(),
      metadata: {
        category: nodeData.metadata?.category || 'default',
        tags: nodeData.metadata?.tags || [],
        version: nodeData.metadata?.version || '1.0.0'
      }
    }

    this.state.nodes.set(nodeData.id, newNode)
    
    // 更新历史记录
    this.updateNodeHistory(nodeData.id, newNode)
    
    // 自动验证
    if (this.config.autoValidate) {
      this.validateNode(nodeData.id)
    }
    
    // 自动更新依赖关系
    if (this.config.autoUpdateDependencies) {
      this.updateNodeDependencies(nodeData.id)
    }
    
    if (oldState) {
      this.emitEvent('node-state-changed', { 
        nodeId: nodeData.id, 
        oldState, 
        newState: newNode 
      })
    }
  }

  // 删除节点
  public removeNode(nodeId: string): void {
    const node = this.state.nodes.get(nodeId)
    if (!node) return
    
    // 清理相关连接
    this.cleanupNodeConnections(nodeId)
    
    // 清理依赖关系
    this.cleanupNodeDependencies(nodeId)
    
    // 删除节点
    this.state.nodes.delete(nodeId)
    
    // 清理历史记录
    this.state.nodeHistory.delete(nodeId)
    
    this.emitEvent('node-deactivated', { nodeId })
  }

  // 更新节点状态
  public updateNodeStatus(nodeId: string, status: NodeState['status'], errorMessage?: string): void {
    const node = this.state.nodes.get(nodeId)
    if (!node) return
    
    const oldState = { ...node }
    node.status = status
    node.errorMessage = errorMessage
    node.lastUpdated = new Date().toISOString()
    
    // 更新历史记录
    this.updateNodeHistory(nodeId, node)
    
    this.emitEvent('node-state-changed', { 
      nodeId, 
      oldState, 
      newState: { ...node } 
    })
    
    if (status === 'active' || status === 'running') {
      this.emitEvent('node-activated', { nodeId })
    } else if (status === 'inactive' || status === 'disabled') {
      this.emitEvent('node-deactivated', { nodeId })
    }
  }

  // 更新节点进度
  public updateNodeProgress(nodeId: string, progress: number): void {
    const node = this.state.nodes.get(nodeId)
    if (!node) return
    
    const oldState = { ...node }
    node.progress = Math.max(0, Math.min(100, progress))
    node.lastUpdated = new Date().toISOString()
    
    // 更新历史记录
    this.updateNodeHistory(nodeId, node)
    
    this.emitEvent('node-state-changed', { 
      nodeId, 
      oldState, 
      newState: { ...node } 
    })
  }

  // 添加或更新连接
  public addOrUpdateConnection(connectionData: Partial<Connection> & { id: string }): void {
    const existingConnection = this.state.connections.get(connectionData.id)
    const oldState = existingConnection ? { ...existingConnection } : null
    
    const newConnection: ConnectionState = {
      id: connectionData.id,
      from: connectionData.from || '',
      to: connectionData.to || '',
      type: (connectionData.type as any) || 'data',
      status: existingConnection?.status || 'inactive',
      isValid: this.isConnectionValid(connectionData),
      dataFlow: existingConnection?.dataFlow || {
        isActive: false,
        bytesTransferred: 0,
        transferRate: 0
      },
      styling: connectionData.styling || {
        color: '#666',
        width: 2,
        style: 'solid'
      }
    }

    this.state.connections.set(connectionData.id, newConnection)
    
    // 更新节点依赖关系
    if (connectionData.from) {
      this.updateNodeDependencies(connectionData.from)
    }
    if (connectionData.to) {
      this.updateNodeDependencies(connectionData.to)
    }
    
    this.emitEvent('connection-state-changed', {
      connectionId: connectionData.id,
      oldState: oldState as any,
      newState: newConnection
    })
  }

  // 删除连接
  public removeConnection(connectionId: string): void {
    const connection = this.state.connections.get(connectionId)
    if (!connection) return
    
    const fromNode = connection.from
    const toNode = connection.to
    
    // 删除连接
    this.state.connections.delete(connectionId)
    
    // 更新节点依赖关系
    this.updateNodeDependencies(fromNode)
    this.updateNodeDependencies(toNode)
    
    this.emitEvent('connection-state-changed', { 
      connectionId, 
      oldState: connection, 
      newState: null 
    })
  }

  // 更新连接状态
  public updateConnectionStatus(connectionId: string, status: ConnectionState['status']): void {
    const connection = this.state.connections.get(connectionId)
    if (!connection) return
    
    const oldState = { ...connection }
    connection.status = status
    
    this.emitEvent('connection-state-changed', { 
      connectionId, 
      oldState, 
      newState: { ...connection } 
    })
  }

  // 验证节点
  public validateNode(nodeId: string): { isValid: boolean; errors: string[] } {
    const node = this.state.nodes.get(nodeId)
    if (!node) {
      return { isValid: false, errors: ['节点不存在'] }
    }
    
    const errors: string[] = []
    
    // 检查配置
    if (!node.isConfigured) {
      errors.push('节点未配置')
    }
    
    // 检查依赖关系
    const missingDependencies = node.dependencies.filter(depId => 
      !this.state.nodes.has(depId)
    )
    if (missingDependencies.length > 0) {
      errors.push(`缺少依赖节点: ${missingDependencies.join(', ')}`)
    }
    
    // 检查循环依赖
    if (this.hasCircularDependency(nodeId)) {
      errors.push('存在循环依赖')
    }
    
    const isValid = errors.length === 0
    node.isValid = isValid
    
    if (!isValid) {
      node.errorMessage = errors.join('; ')
    } else {
      node.errorMessage = undefined
    }
    
    this.emitEvent('validation-completed', { nodeId, isValid, errors })
    return { isValid, errors }
  }

  // 验证连接
  public validateConnection(connectionId: string): { isValid: boolean; errors: string[] } {
    const connection = this.state.connections.get(connectionId)
    if (!connection) {
      return { isValid: false, errors: ['连接不存在'] }
    }
    
    const errors: string[] = []
    
    // 检查源节点和目标节点是否存在
    if (!this.state.nodes.has(connection.from)) {
      errors.push('源节点不存在')
    }
    
    if (!this.state.nodes.has(connection.to)) {
      errors.push('目标节点不存在')
    }
    
    // 检查连接类型兼容性
    const fromNode = this.state.nodes.get(connection.from)
    const toNode = this.state.nodes.get(connection.to)
    
    if (fromNode && toNode && !this.isConnectionTypeCompatible(fromNode.type, toNode.type, connection.type)) {
      errors.push('连接类型不兼容')
    }
    
    const isValid = errors.length === 0
    connection.isValid = isValid
    
    return { isValid, errors }
  }

  // 获取节点历史记录
  public getNodeHistory(nodeId: string): NodeState[] {
    return this.state.nodeHistory.get(nodeId) || []
  }

  // 获取节点依赖图
  public getDependencyGraph(): Map<string, string[]> {
    const graph = new Map<string, string[]>()
    
    this.state.nodes.forEach((node, nodeId) => {
      graph.set(nodeId, [...node.dependencies])
    })
    
    return graph
  }

  // 获取可激活的节点
  public getActivatableNodes(): string[] {
    return Array.from(this.state.nodes.entries())
      .filter(([_, node]) => 
        node.status === 'inactive' && 
        node.isConfigured && 
        node.isValid &&
        this.areDependenciesSatisfied(node.id)
      )
      .map(([nodeId, _]) => nodeId)
  }

  // 检查依赖是否满足
  public areDependenciesSatisfied(nodeId: string): boolean {
    const node = this.state.nodes.get(nodeId)
    if (!node || node.dependencies.length === 0) {
      return true
    }
    
    return node.dependencies.every(depId => {
      const depNode = this.state.nodes.get(depId)
      return depNode && (depNode.status === 'completed' || depNode.status === 'active')
    })
  }

  // 激活节点
  public activateNode(nodeId: string): boolean {
    const node = this.state.nodes.get(nodeId)
    if (!node) {
      this.addGlobalError('activation-failed', '节点不存在', nodeId)
      return false
    }
    
    if (node.status !== 'inactive') {
      this.addGlobalError('activation-failed', '节点状态不正确', nodeId)
      return false
    }
    
    if (!node.isConfigured) {
      this.addGlobalError('activation-failed', '节点未配置', nodeId)
      return false
    }
    
    if (!node.isValid) {
      this.addGlobalError('activation-failed', '节点配置无效', nodeId)
      return false
    }
    
    if (!this.areDependenciesSatisfied(nodeId)) {
      this.addGlobalError('activation-failed', '依赖未满足', nodeId)
      return false
    }
    
    this.updateNodeStatus(nodeId, 'active')
    return true
  }

  // 停用节点
  public deactivateNode(nodeId: string): boolean {
    const node = this.state.nodes.get(nodeId)
    if (!node) {
      this.addGlobalError('deactivation-failed', '节点不存在', nodeId)
      return false
    }
    
    if (node.status === 'inactive' || node.status === 'disabled') {
      return true // 已经是非激活状态
    }
    
    this.updateNodeStatus(nodeId, 'inactive')
    return true
  }

  // 添加全局错误
  public addGlobalError(type: string, message: string, nodeId?: string): void {
    this.state.globalErrors.push({
      id: `error-${Date.now()}`,
      type,
      message,
      timestamp: new Date().toISOString(),
      nodeId
    })
    
    // 限制错误数量
    if (this.state.globalErrors.length > 100) {
      this.state.globalErrors = this.state.globalErrors.slice(-100)
    }
    
    this.emitEvent('error-occurred', { type, message, nodeId })
  }

  // 清除全局错误
  public clearGlobalErrors(): void {
    this.state.globalErrors = []
  }

  // 更新配置
  public updateConfig(newConfig: Partial<StateManagerConfig>): void {
    Object.assign(this.config, newConfig)
    
    // 重新启动自动刷新
    if (newConfig.refreshInterval !== undefined) {
      this.stopAutoRefresh()
      this.startAutoRefresh()
    }
  }

  // 事件监听
  public addEventListener<K extends keyof StateManagerEvents>(
    event: K,
    listener: (event: CustomEvent<StateManagerEvents[K]>) => void
  ): void {
    this.eventTarget.addEventListener(event, listener as EventListener)
  }

  // 移除事件监听
  public removeEventListener<K extends keyof StateManagerEvents>(
    event: K,
    listener: (event: CustomEvent<StateManagerEvents[K]>) => void
  ): void {
    this.eventTarget.removeEventListener(event, listener as EventListener)
  }

  // 私有方法：检查节点是否已配置
  private isNodeConfigured(nodeData: Partial<Node>): boolean {
    // 简单的配置检查逻辑，可以根据实际需求调整
    return !!(nodeData.title && nodeData.type && nodeData.parameters)
  }

  // 私有方法：检查连接是否有效
  private isConnectionValid(connectionData: Partial<Connection>): boolean {
    return !!(connectionData.from && connectionData.to && connectionData.type)
  }

  // 私有方法：检查连接类型兼容性
  private isConnectionTypeCompatible(fromType: string, toType: string, connectionType: string): boolean {
    // 简单的兼容性检查逻辑，可以根据实际需求调整
    const compatibilityMap: Record<string, string[]> = {
      'data_source': ['data_processing', 'strategy', 'analysis'],
      'data_processing': ['strategy', 'analysis', 'visualization'],
      'strategy': ['backtest', 'analysis'],
      'backtest': ['analysis', 'visualization', 'export'],
      'analysis': ['visualization', 'export'],
      'visualization': ['export']
    }
    
    const allowedTargets = compatibilityMap[fromType] || []
    return allowedTargets.includes(toType)
  }

  // 私有方法：检查循环依赖
  private hasCircularDependency(nodeId: string, visited: Set<string> = new Set()): boolean {
    if (visited.has(nodeId)) {
      return true
    }
    
    visited.add(nodeId)
    
    const node = this.state.nodes.get(nodeId)
    if (!node) {
      return false
    }
    
    return node.dependencies.some(depId => 
      this.hasCircularDependency(depId, new Set(visited))
    )
  }

  // 私有方法：清理节点相关连接
  private cleanupNodeConnections(nodeId: string): void {
    const connectionsToRemove: string[] = []
    
    this.state.connections.forEach((connection, connectionId) => {
      if (connection.from === nodeId || connection.to === nodeId) {
        connectionsToRemove.push(connectionId)
      }
    })
    
    connectionsToRemove.forEach(connectionId => {
      this.removeConnection(connectionId)
    })
  }

  // 私有方法：清理节点依赖关系
  private cleanupNodeDependencies(nodeId: string): void {
    this.state.nodes.forEach(node => {
      node.dependencies = node.dependencies.filter(depId => depId !== nodeId)
      node.dependents = node.dependents.filter(depId => depId !== nodeId)
    })
  }

  // 私有方法：更新节点依赖关系
  private updateNodeDependencies(nodeId: string): void {
    const node = this.state.nodes.get(nodeId)
    if (!node) return
    
    // 清空当前依赖关系
    node.dependencies = []
    node.dependents = []
    
    // 重新计算依赖关系
    this.state.connections.forEach(connection => {
      if (connection.to === nodeId) {
        node.dependencies.push(connection.from)
      }
      if (connection.from === nodeId) {
        node.dependents.push(connection.to)
      }
    })
    
    // 去重
    node.dependencies = [...new Set(node.dependencies)]
    node.dependents = [...new Set(node.dependents)]
  }

  // 私有方法：更新节点历史记录
  private updateNodeHistory(nodeId: string, nodeState: NodeState): void {
    if (!this.state.nodeHistory.has(nodeId)) {
      this.state.nodeHistory.set(nodeId, [])
    }
    
    const history = this.state.nodeHistory.get(nodeId)!
    history.push({ ...nodeState })
    
    // 限制历史记录大小
    if (history.length > this.config.maxHistorySize) {
      history.splice(0, history.length - this.config.maxHistorySize)
    }
  }

  // 私有方法：触发事件
  private emitEvent<K extends keyof StateManagerEvents>(
    event: K,
    detail: StateManagerEvents[K]
  ): void {
    this.eventTarget.dispatchEvent(new CustomEvent(event, { detail }))
  }

  // 私有方法：开始自动刷新
  private startAutoRefresh(): void {
    if (this.refreshTimer) {
      clearInterval(this.refreshTimer)
    }
    
    this.refreshTimer = window.setInterval(() => {
      this.refreshStates()
    }, this.config.refreshInterval)
  }

  // 私有方法：停止自动刷新
  private stopAutoRefresh(): void {
    if (this.refreshTimer) {
      clearInterval(this.refreshTimer)
      this.refreshTimer = null
    }
  }

  // 私有方法：刷新状态
  private refreshStates(): void {
    this.state.isLoading = true
    
    try {
      // 验证所有节点
      this.state.nodes.forEach((_, nodeId) => {
        this.validateNode(nodeId)
      })
      
      // 验证所有连接
      this.state.connections.forEach((_, connectionId) => {
        this.validateConnection(connectionId)
      })
    } finally {
      this.state.isLoading = false
    }
  }
}

// 导出单例实例
export const nodeStateManager = NodeStateManager.getInstance()

export default nodeStateManager
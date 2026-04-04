import { reactive, ref, computed } from 'vue'
import { 
  nodesApi,
  createNode,
  getNodes,
  getNode,
  updateNode,
  deleteNode,
  duplicateNode,
  executeNode,
  stopNode,
  pauseNode,
  resumeNode,
  getNodeLogs,
  getNodeMetrics,
  getNodeUsageStats,
  getNodeTemplates,
  getNodeTemplate,
  createNodeFromTemplate,
  validateNode,
  getNodeDependencies,
  batchNodeOperation,
  exportNode,
  importNode,
  getNodeCategories,
  searchNodes
} from '../api/modules/nodes'
import type {
  Node,
  NodeTemplate,
  NodeExecutionLog,
  NodePerformanceMetrics
} from '../api/modules/nodes'
import {
  NodeStatus,
  NodeType
} from '../api/modules/nodes'

/**
 * 节点管理服务类
 * 提供节点的创建、配置、监控、管理等功能
 * 遵循单一职责原则和依赖注入模式
 */

// 节点服务状态接口
export interface NodesServiceState {
  isLoading: boolean
  nodes: Node[]
  currentNode: Node | null
  templates: NodeTemplate[]
  categories: Array<{
    name: string
    description: string
    nodeCount: number
    icon: string
    color: string
  }>
  logs: NodeExecutionLog[]
  metrics: NodePerformanceMetrics[]
  usageStats: {
    usage: {
      totalExecutions: number
      successfulExecutions: number
      failedExecutions: number
      averageExecutionTime: number
      totalExecutionTime: number
      lastUsed?: string
    }
    trends: Array<{
      date: string
      executions: number
      successRate: number
      averageTime: number
    }>
    popularParameters: Array<{
      parameter: string
      value: any
      usageCount: number
    }>
  } | null
  searchResults: Array<{
    id: string
    title: string
    type: NodeType
    category: string
    description: string
    relevanceScore: number
    matchHighlights: Array<{
      field: string
      fragments: string[]
    }>
  }>
  dependencies: {
    dependencies: Array<{
      nodeId: string
      nodeName: string
      type: 'input' | 'output' | 'parameter'
      required: boolean
      description?: string
    }>
    dependents: Array<{
      nodeId: string
      nodeName: string
      type: 'input' | 'output' | 'parameter'
      required: boolean
      description?: string
    }>
  } | null
  error: string | null
}

// 节点服务配置接口
export interface NodesServiceConfig {
  autoSave: boolean
  autoRefresh: boolean
  refreshInterval: number
  maxLogsItems: number
  maxMetricsItems: number
  defaultViewMode: 'list' | 'grid' | 'graph'
  notificationPreferences: {
    onNodeCreated: boolean
    onNodeUpdated: boolean
    onNodeDeleted: boolean
    onExecutionStart: boolean
    onExecutionComplete: boolean
    onExecutionError: boolean
  }
}

// 事件类型定义
export interface NodesServiceEvents {
  'node-created': Node
  'node-updated': Node
  'node-deleted': { id: string }
  'node-execution-started': { nodeId: string; executionId: string }
  'node-execution-completed': { nodeId: string; executionId: string; results: any }
  'node-execution-failed': { nodeId: string; executionId: string; error: string }
  'node-execution-paused': { nodeId: string }
  'node-execution-resumed': { nodeId: string }
  'node-execution-stopped': { nodeId: string }
  'batch-operation-completed': { operation: string; results: any[] }
  'error-occurred': { type: string; message: string }
}

// 依赖注入接口
export interface NodesServiceDependencies {
  apiClient: typeof nodesApi
  storage: {
    get: (key: string) => any
    set: (key: string, value: any) => void
    remove: (key: string) => void
  }
  notification: {
    show: (message: string, type: 'success' | 'error' | 'warning' | 'info') => void
  }
  logger: {
    info: (message: string, ...args: any[]) => void
    error: (message: string, error?: Error | unknown) => void
    warn: (message: string, ...args: any[]) => void
  }
}

class NodesService {
  private static instance: NodesService
  private deps: NodesServiceDependencies
  private eventTarget: EventTarget
  private refreshTimer: number | null = null
  
  // 响应式状态
  public state = reactive<NodesServiceState>({
    isLoading: false,
    nodes: [],
    currentNode: null,
    templates: [],
    categories: [],
    logs: [],
    metrics: [],
    usageStats: null,
    searchResults: [],
    dependencies: null,
    error: null
  })

  // 配置
  public config = reactive<NodesServiceConfig>({
    autoSave: true,
    autoRefresh: true,
    refreshInterval: 30000, // 30秒
    maxLogsItems: 1000,
    maxMetricsItems: 500,
    defaultViewMode: 'list',
    notificationPreferences: {
      onNodeCreated: true,
      onNodeUpdated: false,
      onNodeDeleted: true,
      onExecutionStart: true,
      onExecutionComplete: true,
      onExecutionError: true
    }
  })

  // 计算属性
  public get isLoading() {
    return this.state.isLoading
  }

  public get nodes() {
    return this.state.nodes
  }

  public get currentNode() {
    return this.state.currentNode
  }

  public get templates() {
    return this.state.templates
  }

  public get categories() {
    return this.state.categories
  }

  public get logs() {
    return this.state.logs
  }

  public get metrics() {
    return this.state.metrics
  }

  public get usageStats() {
    return this.state.usageStats
  }

  public get searchResults() {
    return this.state.searchResults
  }

  public get dependencies() {
    return this.state.dependencies
  }

  public get error() {
    return this.state.error
  }

  public get hasCurrentNode() {
    return this.state.currentNode !== null
  }

  public get runningNodes() {
    return this.state.nodes.filter(n => n.status === NodeStatus.RUNNING)
  }

  public get idleNodes() {
    return this.state.nodes.filter(n => n.status === NodeStatus.IDLE)
  }

  public get failedNodes() {
    return this.state.nodes.filter(n => n.status === NodeStatus.FAILED)
  }

  public get completedNodes() {
    return this.state.nodes.filter(n => n.status === NodeStatus.COMPLETED)
  }

  // 单例模式
  public static getInstance(dependencies?: NodesServiceDependencies): NodesService {
    if (!NodesService.instance) {
      NodesService.instance = new NodesService(dependencies)
    }
    return NodesService.instance
  }

  // 私有构造函数，支持依赖注入
  private constructor(dependencies?: NodesServiceDependencies) {
    this.eventTarget = new EventTarget()
    
    // 依赖注入，如果没有提供则使用默认实现
    this.deps = dependencies || {
      apiClient: nodesApi,
      storage: {
        get: (key: string) => {
          try {
            return JSON.parse(localStorage.getItem(key) || 'null')
          } catch {
            return null
          }
        },
        set: (key: string, value: any) => {
          try {
            localStorage.setItem(key, JSON.stringify(value))
          } catch (error) {
            this.deps.logger.error('存储失败:', error)
          }
        },
        remove: (key: string) => {
          try {
            localStorage.removeItem(key)
          } catch (error) {
            this.deps.logger.error('删除存储失败:', error)
          }
        }
      },
      notification: {
        show: (message: string, type: 'success' | 'error' | 'warning' | 'info') => {
          // 默认实现：控制台输出
          console.log(`[${type.toUpperCase()}] ${message}`)
        }
      },
      logger: {
        info: (message: string, ...args: any[]) => {
          console.info(`[NodesService] ${message}`, ...args)
        },
        error: (message: string, error?: Error | unknown) => {
          console.error(`[NodesService] ${message}`, error)
        },
        warn: (message: string, ...args: any[]) => {
          console.warn(`[NodesService] ${message}`, ...args)
        }
      }
    }

    this.loadConfigFromStorage()
    this.loadNodes()
    this.loadTemplates()
    this.loadCategories()
    this.startAutoRefresh()
  }

  // 创建节点
  public async createNode(
    node: Omit<Node, 'id' | 'metadata' | 'execution' | 'permissions'>
  ): Promise<string | null> {
    this.setLoading(true)
    this.clearError()

    try {
      this.deps.logger.info('开始创建节点:', node)
      
      const response = await this.deps.apiClient.createNode(node)
      
      if (response.success && response.data) {
        const newNode = {
          ...node,
          id: response.data.id,
          metadata: {
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString(),
            version: '1.0.0',
            category: this.getCategoryByType(node.type),
            tags: []
          },
          execution: {
            progress: 0
          },
          permissions: {
            canEdit: true,
            canDelete: true,
            canExecute: true,
            canConfigure: true
          }
        }
        
        this.state.nodes.unshift(newNode)
        this.emitEvent('node-created', newNode)
        
        if (this.config.autoSave) {
          this.saveNodesToStorage()
        }
        
        if (this.config.notificationPreferences.onNodeCreated) {
          this.deps.notification.show('节点创建成功', 'success')
        }
        
        this.deps.logger.info('节点创建成功:', newNode)
        return response.data.id
      } else {
        throw new Error(response.message || '创建节点失败')
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : '创建节点失败'
      this.setError(errorMessage)
      this.emitEvent('error-occurred', { type: 'creation-error', message: errorMessage })
      return null
    } finally {
      this.setLoading(false)
    }
  }

  // 获取节点列表
  public async getNodes(
    page = 1,
    pageSize = 10,
    filters?: {
      type?: NodeType
      status?: NodeStatus
      category?: string
      tags?: string[]
      search?: string
    }
  ): Promise<void> {
    this.setLoading(true)
    this.clearError()

    try {
      this.deps.logger.info('开始获取节点列表:', { page, pageSize, filters })
      
      const response = await this.deps.apiClient.getNodes(page, pageSize, filters)
      
      if (response.success && response.data) {
        if (page === 1) {
          this.state.nodes = response.data.nodes
        } else {
          this.state.nodes.push(...response.data.nodes)
        }
        
        this.deps.logger.info('节点列表获取成功:', response.data)
      } else {
        throw new Error(response.message || '获取节点列表失败')
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : '获取节点列表失败'
      this.setError(errorMessage)
      this.emitEvent('error-occurred', { type: 'list-error', message: errorMessage })
    } finally {
      this.setLoading(false)
    }
  }

  // 获取节点详情
  public async getNode(id: string): Promise<Node | null> {
    this.setLoading(true)
    this.clearError()

    try {
      this.deps.logger.info('开始获取节点详情:', id)
      
      const response = await this.deps.apiClient.getNode(id)
      
      if (response.success && response.data) {
        this.state.currentNode = response.data
        this.emitEvent('node-updated', response.data)
        
        this.deps.logger.info('节点详情获取成功:', response.data)
        return response.data
      } else {
        throw new Error(response.message || '获取节点详情失败')
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : '获取节点详情失败'
      this.setError(errorMessage)
      this.emitEvent('error-occurred', { type: 'detail-error', message: errorMessage })
      return null
    } finally {
      this.setLoading(false)
    }
  }

  // 更新节点
  public async updateNode(
    id: string,
    updates: Partial<Node>
  ): Promise<boolean> {
    this.setLoading(true)
    this.clearError()

    try {
      this.deps.logger.info('开始更新节点:', { id, updates })
      
      const response = await this.deps.apiClient.updateNode(id, updates)
      
      if (response.success && response.data.success) {
        // 更新本地状态
        const index = this.state.nodes.findIndex(n => n.id === id)
        if (index !== -1) {
          Object.assign(this.state.nodes[index], updates)
          this.state.nodes[index].metadata.updatedAt = new Date().toISOString()
        }
        
        // 更新当前节点
        if (this.state.currentNode && this.state.currentNode.id === id) {
          Object.assign(this.state.currentNode, updates)
          this.state.currentNode.metadata.updatedAt = new Date().toISOString()
        }
        
        this.emitEvent('node-updated', this.state.currentNode || this.state.nodes[index])
        
        if (this.config.autoSave) {
          this.saveNodesToStorage()
        }
        
        if (this.config.notificationPreferences.onNodeUpdated) {
          this.deps.notification.show('节点更新成功', 'success')
        }
        
        this.deps.logger.info('节点更新成功:', updates)
        return true
      } else {
        throw new Error(response.message || '更新节点失败')
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : '更新节点失败'
      this.setError(errorMessage)
      this.emitEvent('error-occurred', { type: 'update-error', message: errorMessage })
      return false
    } finally {
      this.setLoading(false)
    }
  }

  // 删除节点
  public async deleteNode(id: string): Promise<boolean> {
    this.setLoading(true)
    this.clearError()

    try {
      this.deps.logger.info('开始删除节点:', id)
      
      const response = await this.deps.apiClient.deleteNode(id)
      
      if (response.success && response.data.success) {
        // 从本地状态中移除
        this.state.nodes = this.state.nodes.filter(n => n.id !== id)
        
        // 清除当前节点（如果被删除的是当前节点）
        if (this.state.currentNode && this.state.currentNode.id === id) {
          this.state.currentNode = null
        }
        
        this.emitEvent('node-deleted', { id })
        
        if (this.config.autoSave) {
          this.saveNodesToStorage()
        }
        
        if (this.config.notificationPreferences.onNodeDeleted) {
          this.deps.notification.show('节点删除成功', 'success')
        }
        
        this.deps.logger.info('节点删除成功:', id)
        return true
      } else {
        throw new Error(response.message || '删除节点失败')
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : '删除节点失败'
      this.setError(errorMessage)
      this.emitEvent('error-occurred', { type: 'deletion-error', message: errorMessage })
      return false
    } finally {
      this.setLoading(false)
    }
  }

  // 复制节点
  public async duplicateNode(
    id: string,
    newPosition?: { x: number; y: number }
  ): Promise<string | null> {
    this.setLoading(true)
    this.clearError()

    try {
      this.deps.logger.info('开始复制节点:', { id, newPosition })
      
      const response = await this.deps.apiClient.duplicateNode(id, newPosition)
      
      if (response.success && response.data.newId) {
        // 重新获取节点列表以包含复制的节点
        await this.getNodes()
        
        if (this.config.autoSave) {
          this.saveNodesToStorage()
        }
        
        this.deps.notification.show('节点复制成功', 'success')
        this.deps.logger.info('节点复制成功:', response.data)
        return response.data.newId
      } else {
        throw new Error(response.message || '复制节点失败')
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : '复制节点失败'
      this.setError(errorMessage)
      this.emitEvent('error-occurred', { type: 'duplicate-error', message: errorMessage })
      return null
    } finally {
      this.setLoading(false)
    }
  }

  // 执行节点
  public async executeNode(
    id: string,
    parameters?: Record<string, any>
  ): Promise<string | null> {
    this.setLoading(true)
    this.clearError()

    try {
      this.deps.logger.info('开始执行节点:', { id, parameters })
      
      const response = await this.deps.apiClient.executeNode(id, parameters)
      
      if (response.success && response.data.executionId) {
        // 更新节点状态
        this.updateNodeStatus(id, NodeStatus.RUNNING)
        
        this.emitEvent('node-execution-started', { 
          nodeId: id, 
          executionId: response.data.executionId 
        })
        
        if (this.config.notificationPreferences.onExecutionStart) {
          this.deps.notification.show('节点执行已开始', 'info')
        }
        
        this.deps.logger.info('节点执行成功:', response.data)
        return response.data.executionId
      } else {
        throw new Error(response.message || '执行节点失败')
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : '执行节点失败'
      this.setError(errorMessage)
      this.emitEvent('error-occurred', { type: 'execution-error', message: errorMessage })
      return null
    } finally {
      this.setLoading(false)
    }
  }

  // 停止节点执行
  public async stopNode(id: string): Promise<boolean> {
    this.setLoading(true)
    this.clearError()

    try {
      this.deps.logger.info('开始停止节点执行:', id)
      
      const response = await this.deps.apiClient.stopNode(id)
      
      if (response.success && response.data.success) {
        // 更新节点状态
        this.updateNodeStatus(id, NodeStatus.IDLE)
        
        this.emitEvent('node-execution-stopped', { nodeId: id })
        
        this.deps.logger.info('节点执行停止成功:', response.data)
        return true
      } else {
        throw new Error(response.message || '停止节点执行失败')
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : '停止节点执行失败'
      this.setError(errorMessage)
      this.emitEvent('error-occurred', { type: 'stop-error', message: errorMessage })
      return false
    } finally {
      this.setLoading(false)
    }
  }

  // 暂停节点执行
  public async pauseNode(id: string): Promise<boolean> {
    this.setLoading(true)
    this.clearError()

    try {
      this.deps.logger.info('开始暂停节点执行:', id)
      
      const response = await this.deps.apiClient.pauseNode(id)
      
      if (response.success && response.data.success) {
        // 更新节点状态
        this.updateNodeStatus(id, NodeStatus.PAUSED)
        
        this.emitEvent('node-execution-paused', { nodeId: id })
        
        this.deps.logger.info('节点执行暂停成功:', response.data)
        return true
      } else {
        throw new Error(response.message || '暂停节点执行失败')
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : '暂停节点执行失败'
      this.setError(errorMessage)
      this.emitEvent('error-occurred', { type: 'pause-error', message: errorMessage })
      return false
    } finally {
      this.setLoading(false)
    }
  }

  // 恢复节点执行
  public async resumeNode(id: string): Promise<boolean> {
    this.setLoading(true)
    this.clearError()

    try {
      this.deps.logger.info('开始恢复节点执行:', id)
      
      const response = await this.deps.apiClient.resumeNode(id)
      
      if (response.success && response.data.success) {
        // 更新节点状态
        this.updateNodeStatus(id, NodeStatus.RUNNING)
        
        this.emitEvent('node-execution-resumed', { nodeId: id })
        
        this.deps.logger.info('节点执行恢复成功:', response.data)
        return true
      } else {
        throw new Error(response.message || '恢复节点执行失败')
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : '恢复节点执行失败'
      this.setError(errorMessage)
      this.emitEvent('error-occurred', { type: 'resume-error', message: errorMessage })
      return false
    } finally {
      this.setLoading(false)
    }
  }

  // 获取节点执行日志
  public async getNodeLogs(
    id: string,
    options?: {
      level?: 'debug' | 'info' | 'warning' | 'error'
      startTime?: string
      endTime?: string
      page?: number
      pageSize?: number
    }
  ): Promise<void> {
    try {
      this.deps.logger.info('开始获取节点执行日志:', { id, options })
      
      const response = await this.deps.apiClient.getNodeLogs(id, options)
      
      if (response.success && response.data) {
        if (options?.page === 1 || !options?.page) {
          this.state.logs = response.data.logs
        } else {
          this.state.logs.push(...response.data.logs)
        }
        
        // 限制日志数量
        if (this.state.logs.length > this.config.maxLogsItems) {
          this.state.logs = this.state.logs.slice(-this.config.maxLogsItems)
        }
        
        this.deps.logger.info('节点执行日志获取成功:', response.data)
      } else {
        throw new Error(response.message || '获取节点执行日志失败')
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : '获取节点执行日志失败'
      this.setError(errorMessage)
      this.emitEvent('error-occurred', { type: 'logs-error', message: errorMessage })
    }
  }

  // 获取节点性能指标
  public async getNodeMetrics(
    id: string,
    timeRange?: { start: string; end: string }
  ): Promise<void> {
    try {
      this.deps.logger.info('开始获取节点性能指标:', { id, timeRange })
      
      const response = await this.deps.apiClient.getNodeMetrics(id, timeRange)
      
      if (response.success && response.data) {
        this.state.metrics = response.data.metrics
        
        // 限制指标数量
        if (this.state.metrics.length > this.config.maxMetricsItems) {
          this.state.metrics = this.state.metrics.slice(-this.config.maxMetricsItems)
        }
        
        this.deps.logger.info('节点性能指标获取成功:', response.data)
      } else {
        throw new Error(response.message || '获取节点性能指标失败')
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : '获取节点性能指标失败'
      this.setError(errorMessage)
      this.emitEvent('error-occurred', { type: 'metrics-error', message: errorMessage })
    }
  }

  // 获取节点使用统计
  public async getNodeUsageStats(
    id: string,
    timeRange?: { start: string; end: string }
  ): Promise<void> {
    try {
      this.deps.logger.info('开始获取节点使用统计:', { id, timeRange })
      
      const response = await this.deps.apiClient.getNodeUsageStats(id, timeRange)
      
      if (response.success && response.data) {
        this.state.usageStats = response.data
        this.deps.logger.info('节点使用统计获取成功:', response.data)
      } else {
        throw new Error(response.message || '获取节点使用统计失败')
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : '获取节点使用统计失败'
      this.setError(errorMessage)
      this.emitEvent('error-occurred', { type: 'usage-stats-error', message: errorMessage })
    }
  }

  // 获取节点模板列表
  public async getNodeTemplates(
    type?: NodeType,
    category?: string
  ): Promise<void> {
    try {
      this.deps.logger.info('开始获取节点模板列表:', { type, category })
      
      const response = await this.deps.apiClient.getNodeTemplates(type, category)
      
      if (response.success && response.data) {
        this.state.templates = response.data.templates
        this.deps.logger.info('节点模板列表获取成功:', response.data)
      } else {
        throw new Error(response.message || '获取节点模板列表失败')
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : '获取节点模板列表失败'
      this.setError(errorMessage)
      this.emitEvent('error-occurred', { type: 'templates-error', message: errorMessage })
    }
  }

  // 从模板创建节点
  public async createNodeFromTemplate(
    templateId: string,
    position: { x: number; y: number },
    parameters?: Record<string, any>
  ): Promise<string | null> {
    this.setLoading(true)
    this.clearError()

    try {
      this.deps.logger.info('开始从模板创建节点:', { templateId, position, parameters })
      
      const response = await this.deps.apiClient.createNodeFromTemplate(
        templateId, 
        position, 
        parameters
      )
      
      if (response.success && response.data.nodeId) {
        // 重新获取节点列表以包含新创建的节点
        await this.getNodes()
        
        if (this.config.autoSave) {
          this.saveNodesToStorage()
        }
        
        this.deps.notification.show('从模板创建节点成功', 'success')
        this.deps.logger.info('从模板创建节点成功:', response.data)
        return response.data.nodeId
      } else {
        throw new Error(response.message || '从模板创建节点失败')
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : '从模板创建节点失败'
      this.setError(errorMessage)
      this.emitEvent('error-occurred', { type: 'template-creation-error', message: errorMessage })
      return null
    } finally {
      this.setLoading(false)
    }
  }

  // 验证节点配置
  public async validateNode(
    node: Partial<Node>
  ): Promise<{
    isValid: boolean
    errors: Array<{
      field: string
      message: string
      code: string
    }>
    warnings: Array<{
      field: string
      message: string
      code: string
    }>
  } | null> {
    try {
      this.deps.logger.info('开始验证节点配置:', node)
      
      const response = await this.deps.apiClient.validateNode(node)
      
      if (response.success && response.data) {
        this.deps.logger.info('节点配置验证成功:', response.data)
        return response.data
      } else {
        throw new Error(response.message || '验证节点配置失败')
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : '验证节点配置失败'
      this.setError(errorMessage)
      this.emitEvent('error-occurred', { type: 'validation-error', message: errorMessage })
      return null
    }
  }

  // 获取节点依赖关系
  public async getNodeDependencies(id: string): Promise<void> {
    try {
      this.deps.logger.info('开始获取节点依赖关系:', id)
      
      const response = await this.deps.apiClient.getNodeDependencies(id)
      
      if (response.success && response.data) {
        this.state.dependencies = response.data
        this.deps.logger.info('节点依赖关系获取成功:', response.data)
      } else {
        throw new Error(response.message || '获取节点依赖关系失败')
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : '获取节点依赖关系失败'
      this.setError(errorMessage)
      this.emitEvent('error-occurred', { type: 'dependencies-error', message: errorMessage })
    }
  }

  // 批量操作节点
  public async batchNodeOperation(
    operation: 'delete' | 'execute' | 'stop' | 'pause' | 'resume',
    nodeIds: string[]
  ): Promise<void> {
    this.setLoading(true)
    this.clearError()

    try {
      this.deps.logger.info('开始批量操作节点:', { operation, nodeIds })
      
      const response = await this.deps.apiClient.batchNodeOperation(operation, nodeIds)
      
      if (response.success && response.data) {
        // 更新本地状态
        if (operation === 'delete') {
          this.state.nodes = this.state.nodes.filter(n => !nodeIds.includes(n.id))
        } else if (operation === 'execute') {
          nodeIds.forEach(id => this.updateNodeStatus(id, NodeStatus.RUNNING))
        } else if (operation === 'stop') {
          nodeIds.forEach(id => this.updateNodeStatus(id, NodeStatus.IDLE))
        } else if (operation === 'pause') {
          nodeIds.forEach(id => this.updateNodeStatus(id, NodeStatus.PAUSED))
        } else if (operation === 'resume') {
          nodeIds.forEach(id => this.updateNodeStatus(id, NodeStatus.RUNNING))
        }
        
        this.emitEvent('batch-operation-completed', { operation, results: response.data.results })
        
        if (this.config.autoSave) {
          this.saveNodesToStorage()
        }
        
        this.deps.notification.show(`批量${operation}操作完成`, 'success')
        this.deps.logger.info('批量操作节点成功:', response.data)
      } else {
        throw new Error(response.message || '批量操作节点失败')
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : '批量操作节点失败'
      this.setError(errorMessage)
      this.emitEvent('error-occurred', { type: 'batch-operation-error', message: errorMessage })
    } finally {
      this.setLoading(false)
    }
  }

  // 搜索节点
  public async searchNodes(
    query: string,
    filters?: {
      type?: NodeType
      category?: string
      tags?: string[]
    }
  ): Promise<void> {
    this.setLoading(true)
    this.clearError()

    try {
      this.deps.logger.info('开始搜索节点:', { query, filters })
      
      const response = await this.deps.apiClient.searchNodes(query, filters)
      
      if (response.success && response.data) {
        this.state.searchResults = response.data.nodes
        this.deps.logger.info('节点搜索成功:', response.data)
      } else {
        throw new Error(response.message || '搜索节点失败')
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : '搜索节点失败'
      this.setError(errorMessage)
      this.emitEvent('error-occurred', { type: 'search-error', message: errorMessage })
    } finally {
      this.setLoading(false)
    }
  }

  // 获取节点分类
  public async getNodeCategories(): Promise<void> {
    try {
      this.deps.logger.info('开始获取节点分类')
      
      const response = await this.deps.apiClient.getNodeCategories()
      
      if (response.success && response.data) {
        this.state.categories = response.data.categories
        this.deps.logger.info('节点分类获取成功:', response.data)
      } else {
        throw new Error(response.message || '获取节点分类失败')
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : '获取节点分类失败'
      this.setError(errorMessage)
      this.emitEvent('error-occurred', { type: 'categories-error', message: errorMessage })
    }
  }

  // 更新配置
  public updateConfig(newConfig: Partial<NodesServiceConfig>): void {
    Object.assign(this.config, newConfig)
    this.saveConfigToStorage()
    
    // 重新启动自动刷新
    if (newConfig.autoRefresh !== undefined) {
      this.stopAutoRefresh()
      if (newConfig.autoRefresh) {
        this.startAutoRefresh()
      }
    }
    
    this.deps.logger.info('节点服务配置已更新:', this.config)
  }

  // 清除当前节点
  public clearCurrentNode(): void {
    this.state.currentNode = null
    this.state.logs = []
    this.state.metrics = []
    this.state.usageStats = null
    this.state.dependencies = null
    this.clearError()
  }

  // 清除错误
  public clearError(): void {
    this.state.error = null
  }

  // 事件监听
  public addEventListener<K extends keyof NodesServiceEvents>(
    event: K,
    listener: (event: CustomEvent<NodesServiceEvents[K]>) => void
  ): void {
    this.eventTarget.addEventListener(event, listener as EventListener)
  }

  // 移除事件监听
  public removeEventListener<K extends keyof NodesServiceEvents>(
    event: K,
    listener: (event: CustomEvent<NodesServiceEvents[K]>) => void
  ): void {
    this.eventTarget.removeEventListener(event, listener as EventListener)
  }

  // 私有方法：设置加载状态
  private setLoading(isLoading: boolean): void {
    this.state.isLoading = isLoading
  }

  // 私有方法：设置错误
  private setError(error: string | null): void {
    this.state.error = error
  }

  // 私有方法：触发事件
  private emitEvent<K extends keyof NodesServiceEvents>(
    event: K,
    detail: NodesServiceEvents[K]
  ): void {
    this.eventTarget.dispatchEvent(new CustomEvent(event, { detail }))
  }

  // 私有方法：更新节点状态
  private updateNodeStatus(id: string, status: NodeStatus): void {
    // 更新节点列表中的状态
    const index = this.state.nodes.findIndex(n => n.id === id)
    if (index !== -1) {
      this.state.nodes[index].status = status
      this.state.nodes[index].metadata.updatedAt = new Date().toISOString()
    }
    
    // 更新当前节点状态
    if (this.state.currentNode && this.state.currentNode.id === id) {
      this.state.currentNode.status = status
      this.state.currentNode.metadata.updatedAt = new Date().toISOString()
    }
    
    if (this.config.autoSave) {
      this.saveNodesToStorage()
    }
  }

  // 私有方法：根据类型获取分类
  private getCategoryByType(type: NodeType): string {
    const typeToCategoryMap: Record<NodeType, string> = {
      [NodeType.CONFIG]: '配置',
      [NodeType.DATA_SOURCE]: '数据源',
      [NodeType.DATA_PROCESSING]: '数据处理',
      [NodeType.STRATEGY]: '策略',
      [NodeType.BACKTEST]: '回测',
      [NodeType.ANALYSIS]: '分析',
      [NodeType.VISUALIZATION]: '可视化',
      [NodeType.EXPORT]: '导出'
    }
    
    return typeToCategoryMap[type] || '其他'
  }

  // 私有方法：保存配置到本地存储
  private saveConfigToStorage(): void {
    this.deps.storage.set('nodes-service-config', this.config)
  }

  // 私有方法：从本地存储加载配置
  private loadConfigFromStorage(): void {
    try {
      const saved = this.deps.storage.get('nodes-service-config')
      if (saved) {
        Object.assign(this.config, saved)
      }
    } catch (error) {
      this.deps.logger.error('加载节点服务配置失败:', error)
    }
  }

  // 私有方法：保存节点到本地存储
  private saveNodesToStorage(): void {
    try {
      this.deps.storage.set('nodes', this.state.nodes)
    } catch (error) {
      this.deps.logger.error('保存节点失败:', error)
    }
  }

  // 私有方法：从本地存储加载节点
  private loadNodes(): void {
    try {
      const saved = this.deps.storage.get('nodes')
      if (saved) {
        this.state.nodes = saved
      }
    } catch (error) {
      this.deps.logger.error('加载节点失败:', error)
    }
  }

  // 私有方法：从本地存储加载模板
  private loadTemplates(): void {
    try {
      const saved = this.deps.storage.get('node-templates')
      if (saved) {
        this.state.templates = saved
      }
    } catch (error) {
      this.deps.logger.error('加载节点模板失败:', error)
    }
  }

  // 私有方法：从本地存储加载分类
  private loadCategories(): void {
    try {
      const saved = this.deps.storage.get('node-categories')
      if (saved) {
        this.state.categories = saved
      }
    } catch (error) {
      this.deps.logger.error('加载节点分类失败:', error)
    }
  }

  // 私有方法：开始自动刷新
  private startAutoRefresh(): void {
    if (this.refreshTimer) {
      clearInterval(this.refreshTimer)
    }
    
    this.refreshTimer = window.setInterval(async () => {
      await this.getNodes()
    }, this.config.refreshInterval)
  }

  // 私有方法：停止自动刷新
  private stopAutoRefresh(): void {
    if (this.refreshTimer) {
      clearInterval(this.refreshTimer)
      this.refreshTimer = null
    }
  }
}

// 导出单例实例
export const nodesService = NodesService.getInstance()

export default nodesService
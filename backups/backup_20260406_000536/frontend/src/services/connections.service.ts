import { reactive, ref, computed } from 'vue'
import { 
  connectionsApi,
  createConnection,
  getConnections,
  getConnection,
  updateConnection,
  deleteConnection,
  enableConnection,
  disableConnection,
  testConnection,
  getConnectionLogs,
  getConnectionMetrics,
  getConnectionStats,
  getConnectionTemplates,
  getConnectionTemplate,
  createConnectionFromTemplate,
  validateConnection,
  getConnectionSuggestions,
  applyConnectionSuggestion,
  batchConnectionOperation,
  exportConnection,
  importConnection
} from '../api/modules/connections'
import type {
  Connection,
  ConnectionTemplate,
  ConnectionExecutionLog,
  ConnectionPerformanceMetrics
} from '../api/modules/connections'
import {
  ConnectionStatus,
  ConnectionType,
  ConnectionDirection
} from '../api/modules/connections'

/**
 * 连接管理服务类
 * 提供节点间连接的创建、配置、监控、管理等功能
 * 遵循单一职责原则和依赖注入模式
 */

// 连接服务状态接口
export interface ConnectionsServiceState {
  isLoading: boolean
  connections: Connection[]
  currentConnection: Connection | null
  templates: ConnectionTemplate[]
  logs: ConnectionExecutionLog[]
  metrics: ConnectionPerformanceMetrics[]
  stats: {
    totalConnections: number
    activeConnections: number
    inactiveConnections: number
    errorConnections: number
    connectionTypes: Array<{
      type: ConnectionType
      count: number
      percentage: number
    }>
    performance: {
      averageTransferRate: number
      averageLatency: number
      totalDataTransferred: number
      errorRate: number
    }
    trends: Array<{
      date: string
      activeConnections: number
      totalTransfers: number
      averageLatency: number
    }>
  } | null
  suggestions: Array<{
    targetNodeId: string
    targetNodeTitle: string
    connectionType: ConnectionType
    confidence: number
    reason: string
    estimatedPerformance?: {
      transferRate: number
      latency: number
    }
  }>
  validation: {
    isValid: boolean
    errors: Array<{
      type: 'type_mismatch' | 'circular_dependency' | 'missing_source' | 'missing_target' | 'invalid_path'
      message: string
      nodeId?: string
    }>
    warnings: Array<{
      type: 'performance' | 'best_practice' | 'redundancy'
      message: string
      nodeId?: string
    }>
    suggestions: Array<{
      type: 'optimization' | 'alternative' | 'enhancement'
      message: string
      action?: string
    }>
  } | null
  error: string | null
}

// 连接服务配置接口
export interface ConnectionsServiceConfig {
  autoSave: boolean
  autoRefresh: boolean
  refreshInterval: number
  maxLogsItems: number
  maxMetricsItems: number
  defaultViewMode: 'list' | 'graph'
  notificationPreferences: {
    onConnectionCreated: boolean
    onConnectionUpdated: boolean
    onConnectionDeleted: boolean
    onConnectionError: boolean
    onConnectionTested: boolean
  }
}

// 事件类型定义
export interface ConnectionsServiceEvents {
  'connection-created': Connection
  'connection-updated': Connection
  'connection-deleted': { id: string }
  'connection-enabled': { id: string }
  'connection-disabled': { id: string; reason?: string }
  'connection-tested': { id: string; results: any }
  'connection-error': { id: string; error: string }
  'batch-operation-completed': { operation: string; results: any[] }
  'suggestions-updated': { nodeId: string; suggestions: any[] }
  'error-occurred': { type: string; message: string }
}

// 依赖注入接口
export interface ConnectionsServiceDependencies {
  apiClient: typeof connectionsApi
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

class ConnectionsService {
  private static instance: ConnectionsService
  private deps: ConnectionsServiceDependencies
  private eventTarget: EventTarget
  private refreshTimer: number | null = null
  
  // 响应式状态
  public state = reactive<ConnectionsServiceState>({
    isLoading: false,
    connections: [],
    currentConnection: null,
    templates: [],
    logs: [],
    metrics: [],
    stats: null,
    suggestions: [],
    validation: null,
    error: null
  })

  // 配置
  public config = reactive<ConnectionsServiceConfig>({
    autoSave: true,
    autoRefresh: true,
    refreshInterval: 30000, // 30秒
    maxLogsItems: 1000,
    maxMetricsItems: 500,
    defaultViewMode: 'list',
    notificationPreferences: {
      onConnectionCreated: true,
      onConnectionUpdated: false,
      onConnectionDeleted: true,
      onConnectionError: true,
      onConnectionTested: true
    }
  })

  // 计算属性
  public get isLoading() {
    return this.state.isLoading
  }

  public get connections() {
    return this.state.connections
  }

  public get currentConnection() {
    return this.state.currentConnection
  }

  public get templates() {
    return this.state.templates
  }

  public get logs() {
    return this.state.logs
  }

  public get metrics() {
    return this.state.metrics
  }

  public get stats() {
    return this.state.stats
  }

  public get suggestions() {
    return this.state.suggestions
  }

  public get validation() {
    return this.state.validation
  }

  public get error() {
    return this.state.error
  }

  public get hasCurrentConnection() {
    return this.state.currentConnection !== null
  }

  public get activeConnections() {
    return this.state.connections.filter(c => c.status === ConnectionStatus.ACTIVE)
  }

  public get inactiveConnections() {
    return this.state.connections.filter(c => c.status === ConnectionStatus.INACTIVE)
  }

  public get errorConnections() {
    return this.state.connections.filter(c => c.status === ConnectionStatus.ERROR)
  }

  public get pendingConnections() {
    return this.state.connections.filter(c => c.status === ConnectionStatus.PENDING)
  }

  // 单例模式
  public static getInstance(dependencies?: ConnectionsServiceDependencies): ConnectionsService {
    if (!ConnectionsService.instance) {
      ConnectionsService.instance = new ConnectionsService(dependencies)
    }
    return ConnectionsService.instance
  }

  // 私有构造函数，支持依赖注入
  private constructor(dependencies?: ConnectionsServiceDependencies) {
    this.eventTarget = new EventTarget()
    
    // 依赖注入，如果没有提供则使用默认实现
    this.deps = dependencies || {
      apiClient: connectionsApi,
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
          console.info(`[ConnectionsService] ${message}`, ...args)
        },
        error: (message: string, error?: Error | unknown) => {
          console.error(`[ConnectionsService] ${message}`, error)
        },
        warn: (message: string, ...args: any[]) => {
          console.warn(`[ConnectionsService] ${message}`, ...args)
        }
      }
    }

    this.loadConfigFromStorage()
    this.loadConnections()
    this.loadTemplates()
    this.startAutoRefresh()
  }

  // 创建连接
  public async createConnection(
    connection: Omit<Connection, 'id' | 'metadata' | 'dataFlow' | 'validation' | 'permissions'>
  ): Promise<string | null> {
    this.setLoading(true)
    this.clearError()

    try {
      this.deps.logger.info('开始创建连接:', connection)
      
      const response = await this.deps.apiClient.createConnection(connection)
      
      if (response.success && response.data) {
        const newConnection = {
          ...connection,
          id: response.data.id,
          metadata: {
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString(),
            createdBy: 'current-user',
            version: '1.0.0',
            tags: []
          },
          dataFlow: {
            isActive: false,
            bytesTransferred: 0,
            transferRate: 0,
            totalTransfers: 0
          },
          validation: {
            isValid: true,
            errors: [],
            warnings: []
          },
          permissions: {
            canEdit: true,
            canDelete: true,
            canEnable: true
          }
        }
        
        this.state.connections.unshift(newConnection)
        this.emitEvent('connection-created', newConnection)
        
        if (this.config.autoSave) {
          this.saveConnectionsToStorage()
        }
        
        if (this.config.notificationPreferences.onConnectionCreated) {
          this.deps.notification.show('连接创建成功', 'success')
        }
        
        this.deps.logger.info('连接创建成功:', newConnection)
        return response.data.id
      } else {
        throw new Error(response.message || '创建连接失败')
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : '创建连接失败'
      this.setError(errorMessage)
      this.emitEvent('error-occurred', { type: 'creation-error', message: errorMessage })
      return null
    } finally {
      this.setLoading(false)
    }
  }

  // 获取连接列表
  public async getConnections(
    page = 1,
    pageSize = 10,
    filters?: {
      fromNode?: string
      toNode?: string
      type?: ConnectionType
      status?: ConnectionStatus
      tags?: string[]
    }
  ): Promise<void> {
    this.setLoading(true)
    this.clearError()

    try {
      this.deps.logger.info('开始获取连接列表:', { page, pageSize, filters })
      
      const response = await this.deps.apiClient.getConnections(page, pageSize, filters)
      
      if (response.success && response.data) {
        if (page === 1) {
          this.state.connections = response.data.connections
        } else {
          this.state.connections.push(...response.data.connections)
        }
        
        this.deps.logger.info('连接列表获取成功:', response.data)
      } else {
        throw new Error(response.message || '获取连接列表失败')
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : '获取连接列表失败'
      this.setError(errorMessage)
      this.emitEvent('error-occurred', { type: 'list-error', message: errorMessage })
    } finally {
      this.setLoading(false)
    }
  }

  // 获取连接详情
  public async getConnection(id: string): Promise<Connection | null> {
    this.setLoading(true)
    this.clearError()

    try {
      this.deps.logger.info('开始获取连接详情:', id)
      
      const response = await this.deps.apiClient.getConnection(id)
      
      if (response.success && response.data) {
        this.state.currentConnection = response.data
        this.emitEvent('connection-updated', response.data)
        
        this.deps.logger.info('连接详情获取成功:', response.data)
        return response.data
      } else {
        throw new Error(response.message || '获取连接详情失败')
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : '获取连接详情失败'
      this.setError(errorMessage)
      this.emitEvent('error-occurred', { type: 'detail-error', message: errorMessage })
      return null
    } finally {
      this.setLoading(false)
    }
  }

  // 更新连接
  public async updateConnection(
    id: string,
    updates: Partial<Connection>
  ): Promise<boolean> {
    this.setLoading(true)
    this.clearError()

    try {
      this.deps.logger.info('开始更新连接:', { id, updates })
      
      const response = await this.deps.apiClient.updateConnection(id, updates)
      
      if (response.success && response.data.success) {
        // 更新本地状态
        const index = this.state.connections.findIndex(c => c.id === id)
        if (index !== -1) {
          Object.assign(this.state.connections[index], updates)
          this.state.connections[index].metadata.updatedAt = new Date().toISOString()
        }
        
        // 更新当前连接
        if (this.state.currentConnection && this.state.currentConnection.id === id) {
          Object.assign(this.state.currentConnection, updates)
          this.state.currentConnection.metadata.updatedAt = new Date().toISOString()
        }
        
        this.emitEvent('connection-updated', this.state.currentConnection || this.state.connections[index])
        
        if (this.config.autoSave) {
          this.saveConnectionsToStorage()
        }
        
        if (this.config.notificationPreferences.onConnectionUpdated) {
          this.deps.notification.show('连接更新成功', 'success')
        }
        
        this.deps.logger.info('连接更新成功:', updates)
        return true
      } else {
        throw new Error(response.message || '更新连接失败')
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : '更新连接失败'
      this.setError(errorMessage)
      this.emitEvent('error-occurred', { type: 'update-error', message: errorMessage })
      return false
    } finally {
      this.setLoading(false)
    }
  }

  // 删除连接
  public async deleteConnection(id: string): Promise<boolean> {
    this.setLoading(true)
    this.clearError()

    try {
      this.deps.logger.info('开始删除连接:', id)
      
      const response = await this.deps.apiClient.deleteConnection(id)
      
      if (response.success && response.data.success) {
        // 从本地状态中移除
        this.state.connections = this.state.connections.filter(c => c.id !== id)
        
        // 清除当前连接（如果被删除的是当前连接）
        if (this.state.currentConnection && this.state.currentConnection.id === id) {
          this.state.currentConnection = null
        }
        
        this.emitEvent('connection-deleted', { id })
        
        if (this.config.autoSave) {
          this.saveConnectionsToStorage()
        }
        
        if (this.config.notificationPreferences.onConnectionDeleted) {
          this.deps.notification.show('连接删除成功', 'success')
        }
        
        this.deps.logger.info('连接删除成功:', id)
        return true
      } else {
        throw new Error(response.message || '删除连接失败')
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : '删除连接失败'
      this.setError(errorMessage)
      this.emitEvent('error-occurred', { type: 'deletion-error', message: errorMessage })
      return false
    } finally {
      this.setLoading(false)
    }
  }

  // 启用连接
  public async enableConnection(id: string): Promise<boolean> {
    this.setLoading(true)
    this.clearError()

    try {
      this.deps.logger.info('开始启用连接:', id)
      
      const response = await this.deps.apiClient.enableConnection(id)
      
      if (response.success && response.data.success) {
        // 更新连接状态
        this.updateConnectionStatus(id, ConnectionStatus.ACTIVE)
        
        this.emitEvent('connection-enabled', { id })
        
        this.deps.logger.info('连接启用成功:', response.data)
        return true
      } else {
        throw new Error(response.message || '启用连接失败')
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : '启用连接失败'
      this.setError(errorMessage)
      this.emitEvent('error-occurred', { type: 'enable-error', message: errorMessage })
      return false
    } finally {
      this.setLoading(false)
    }
  }

  // 禁用连接
  public async disableConnection(id: string, reason?: string): Promise<boolean> {
    this.setLoading(true)
    this.clearError()

    try {
      this.deps.logger.info('开始禁用连接:', { id, reason })
      
      const response = await this.deps.apiClient.disableConnection(id, reason)
      
      if (response.success && response.data.success) {
        // 更新连接状态
        this.updateConnectionStatus(id, ConnectionStatus.DISABLED)
        
        this.emitEvent('connection-disabled', { id, reason })
        
        this.deps.logger.info('连接禁用成功:', response.data)
        return true
      } else {
        throw new Error(response.message || '禁用连接失败')
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : '禁用连接失败'
      this.setError(errorMessage)
      this.emitEvent('error-occurred', { type: 'disable-error', message: errorMessage })
      return false
    } finally {
      this.setLoading(false)
    }
  }

  // 测试连接
  public async testConnection(id: string): Promise<{
    isValid: boolean
    canTransfer: boolean
    testResults: any
    errors: Array<{
      type: string
      message: string
    }>
  } | null> {
    this.setLoading(true)
    this.clearError()

    try {
      this.deps.logger.info('开始测试连接:', id)
      
      const response = await this.deps.apiClient.testConnection(id)
      
      if (response.success && response.data) {
        this.emitEvent('connection-tested', { id, results: response.data })
        
        if (this.config.notificationPreferences.onConnectionTested) {
          const status = response.data.isValid ? '成功' : '失败'
          this.deps.notification.show(`连接测试${status}`, response.data.isValid ? 'success' : 'warning')
        }
        
        this.deps.logger.info('连接测试成功:', response.data)
        return response.data
      } else {
        throw new Error(response.message || '测试连接失败')
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : '测试连接失败'
      this.setError(errorMessage)
      this.emitEvent('error-occurred', { type: 'test-error', message: errorMessage })
      return null
    } finally {
      this.setLoading(false)
    }
  }

  // 获取连接执行日志
  public async getConnectionLogs(
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
      this.deps.logger.info('开始获取连接执行日志:', { id, options })
      
      const response = await this.deps.apiClient.getConnectionLogs(id, options)
      
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
        
        this.deps.logger.info('连接执行日志获取成功:', response.data)
      } else {
        throw new Error(response.message || '获取连接执行日志失败')
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : '获取连接执行日志失败'
      this.setError(errorMessage)
      this.emitEvent('error-occurred', { type: 'logs-error', message: errorMessage })
    }
  }

  // 获取连接性能指标
  public async getConnectionMetrics(
    id: string,
    timeRange?: { start: string; end: string }
  ): Promise<void> {
    try {
      this.deps.logger.info('开始获取连接性能指标:', { id, timeRange })
      
      const response = await this.deps.apiClient.getConnectionMetrics(id, timeRange)
      
      if (response.success && response.data) {
        this.state.metrics = response.data.metrics
        
        // 限制指标数量
        if (this.state.metrics.length > this.config.maxMetricsItems) {
          this.state.metrics = this.state.metrics.slice(-this.config.maxMetricsItems)
        }
        
        this.deps.logger.info('连接性能指标获取成功:', response.data)
      } else {
        throw new Error(response.message || '获取连接性能指标失败')
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : '获取连接性能指标失败'
      this.setError(errorMessage)
      this.emitEvent('error-occurred', { type: 'metrics-error', message: errorMessage })
    }
  }

  // 获取连接统计信息
  public async getConnectionStats(
    timeRange?: { start: string; end: string }
  ): Promise<void> {
    try {
      this.deps.logger.info('开始获取连接统计信息:', timeRange)
      
      const response = await this.deps.apiClient.getConnectionStats(timeRange)
      
      if (response.success && response.data) {
        this.state.stats = response.data
        this.deps.logger.info('连接统计信息获取成功:', response.data)
      } else {
        throw new Error(response.message || '获取连接统计信息失败')
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : '获取连接统计信息失败'
      this.setError(errorMessage)
      this.emitEvent('error-occurred', { type: 'stats-error', message: errorMessage })
    }
  }

  // 获取连接模板列表
  public async getConnectionTemplates(
    fromNodeType?: string,
    toNodeType?: string
  ): Promise<void> {
    try {
      this.deps.logger.info('开始获取连接模板列表:', { fromNodeType, toNodeType })
      
      const response = await this.deps.apiClient.getConnectionTemplates(fromNodeType, toNodeType)
      
      if (response.success && response.data) {
        this.state.templates = response.data.templates
        this.deps.logger.info('连接模板列表获取成功:', response.data)
      } else {
        throw new Error(response.message || '获取连接模板列表失败')
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : '获取连接模板列表失败'
      this.setError(errorMessage)
      this.emitEvent('error-occurred', { type: 'templates-error', message: errorMessage })
    }
  }

  // 从模板创建连接
  public async createConnectionFromTemplate(
    templateId: string,
    fromNode: string,
    toNode: string,
    customizations?: {
      label?: string
      description?: string
      styling?: Partial<Connection['styling']>
    }
  ): Promise<string | null> {
    this.setLoading(true)
    this.clearError()

    try {
      this.deps.logger.info('开始从模板创建连接:', { templateId, fromNode, toNode, customizations })
      
      const response = await this.deps.apiClient.createConnectionFromTemplate(
        templateId, 
        fromNode, 
        toNode, 
        customizations
      )
      
      if (response.success && response.data.connectionId) {
        // 重新获取连接列表以包含新创建的连接
        await this.getConnections()
        
        if (this.config.autoSave) {
          this.saveConnectionsToStorage()
        }
        
        this.deps.notification.show('从模板创建连接成功', 'success')
        this.deps.logger.info('从模板创建连接成功:', response.data)
        return response.data.connectionId
      } else {
        throw new Error(response.message || '从模板创建连接失败')
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : '从模板创建连接失败'
      this.setError(errorMessage)
      this.emitEvent('error-occurred', { type: 'template-creation-error', message: errorMessage })
      return null
    } finally {
      this.setLoading(false)
    }
  }

  // 验证连接
  public async validateConnection(
    connection: Partial<Connection>
  ): Promise<{
    isValid: boolean
    errors: Array<{
      type: 'type_mismatch' | 'circular_dependency' | 'missing_source' | 'missing_target' | 'invalid_path'
      message: string
      nodeId?: string
    }>
    warnings: Array<{
      type: 'performance' | 'best_practice' | 'redundancy'
      message: string
      nodeId?: string
    }>
    suggestions: Array<{
      type: 'optimization' | 'alternative' | 'enhancement'
      message: string
      action?: string
    }>
  } | null> {
    try {
      this.deps.logger.info('开始验证连接:', connection)
      
      const response = await this.deps.apiClient.validateConnection(connection)
      
      if (response.success && response.data) {
        this.state.validation = response.data
        this.deps.logger.info('连接验证成功:', response.data)
        return response.data
      } else {
        throw new Error(response.message || '验证连接失败')
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : '验证连接失败'
      this.setError(errorMessage)
      this.emitEvent('error-occurred', { type: 'validation-error', message: errorMessage })
      return null
    }
  }

  // 获取连接建议
  public async getConnectionSuggestions(
    nodeId: string,
    context?: {
      workflowId?: string
      existingConnections?: string[]
      preferences?: {
        connectionType?: ConnectionType
        maxDistance?: number
        avoidCircular?: boolean
      }
    }
  ): Promise<void> {
    try {
      this.deps.logger.info('开始获取连接建议:', { nodeId, context })
      
      const response = await this.deps.apiClient.getConnectionSuggestions(nodeId, context)
      
      if (response.success && response.data) {
        this.state.suggestions = response.data.suggestions
        this.emitEvent('suggestions-updated', { nodeId, suggestions: response.data.suggestions })
        this.deps.logger.info('连接建议获取成功:', response.data)
      } else {
        throw new Error(response.message || '获取连接建议失败')
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : '获取连接建议失败'
      this.setError(errorMessage)
      this.emitEvent('error-occurred', { type: 'suggestions-error', message: errorMessage })
    }
  }

  // 应用连接建议
  public async applyConnectionSuggestion(
    nodeId: string,
    suggestionId: string
  ): Promise<string | null> {
    this.setLoading(true)
    this.clearError()

    try {
      this.deps.logger.info('开始应用连接建议:', { nodeId, suggestionId })
      
      const response = await this.deps.apiClient.applyConnectionSuggestion(nodeId, suggestionId)
      
      if (response.success && response.data.connectionId) {
        // 重新获取连接列表以包含新创建的连接
        await this.getConnections()
        
        if (this.config.autoSave) {
          this.saveConnectionsToStorage()
        }
        
        this.deps.notification.show('连接建议应用成功', 'success')
        this.deps.logger.info('连接建议应用成功:', response.data)
        return response.data.connectionId
      } else {
        throw new Error(response.message || '应用连接建议失败')
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : '应用连接建议失败'
      this.setError(errorMessage)
      this.emitEvent('error-occurred', { type: 'apply-suggestion-error', message: errorMessage })
      return null
    } finally {
      this.setLoading(false)
    }
  }

  // 批量操作连接
  public async batchConnectionOperation(
    operation: 'delete' | 'enable' | 'disable' | 'test',
    connectionIds: string[]
  ): Promise<void> {
    this.setLoading(true)
    this.clearError()

    try {
      this.deps.logger.info('开始批量操作连接:', { operation, connectionIds })
      
      const response = await this.deps.apiClient.batchConnectionOperation(operation, connectionIds)
      
      if (response.success && response.data) {
        // 更新本地状态
        if (operation === 'delete') {
          this.state.connections = this.state.connections.filter(c => !connectionIds.includes(c.id))
        } else if (operation === 'enable') {
          connectionIds.forEach(id => this.updateConnectionStatus(id, ConnectionStatus.ACTIVE))
        } else if (operation === 'disable') {
          connectionIds.forEach(id => this.updateConnectionStatus(id, ConnectionStatus.DISABLED))
        }
        
        this.emitEvent('batch-operation-completed', { operation, results: response.data.results })
        
        if (this.config.autoSave) {
          this.saveConnectionsToStorage()
        }
        
        this.deps.notification.show(`批量${operation}操作完成`, 'success')
        this.deps.logger.info('批量操作连接成功:', response.data)
      } else {
        throw new Error(response.message || '批量操作连接失败')
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : '批量操作连接失败'
      this.setError(errorMessage)
      this.emitEvent('error-occurred', { type: 'batch-operation-error', message: errorMessage })
    } finally {
      this.setLoading(false)
    }
  }

  // 更新配置
  public updateConfig(newConfig: Partial<ConnectionsServiceConfig>): void {
    Object.assign(this.config, newConfig)
    this.saveConfigToStorage()
    
    // 重新启动自动刷新
    if (newConfig.autoRefresh !== undefined) {
      this.stopAutoRefresh()
      if (newConfig.autoRefresh) {
        this.startAutoRefresh()
      }
    }
    
    this.deps.logger.info('连接服务配置已更新:', this.config)
  }

  // 清除当前连接
  public clearCurrentConnection(): void {
    this.state.currentConnection = null
    this.state.logs = []
    this.state.metrics = []
    this.state.validation = null
    this.clearError()
  }

  // 清除错误
  public clearError(): void {
    this.state.error = null
  }

  // 事件监听
  public addEventListener<K extends keyof ConnectionsServiceEvents>(
    event: K,
    listener: (event: CustomEvent<ConnectionsServiceEvents[K]>) => void
  ): void {
    this.eventTarget.addEventListener(event, listener as EventListener)
  }

  // 移除事件监听
  public removeEventListener<K extends keyof ConnectionsServiceEvents>(
    event: K,
    listener: (event: CustomEvent<ConnectionsServiceEvents[K]>) => void
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
  private emitEvent<K extends keyof ConnectionsServiceEvents>(
    event: K,
    detail: ConnectionsServiceEvents[K]
  ): void {
    this.eventTarget.dispatchEvent(new CustomEvent(event, { detail }))
  }

  // 私有方法：更新连接状态
  private updateConnectionStatus(id: string, status: ConnectionStatus): void {
    // 更新连接列表中的状态
    const index = this.state.connections.findIndex(c => c.id === id)
    if (index !== -1) {
      this.state.connections[index].status = status
      this.state.connections[index].metadata.updatedAt = new Date().toISOString()
    }
    
    // 更新当前连接状态
    if (this.state.currentConnection && this.state.currentConnection.id === id) {
      this.state.currentConnection.status = status
      this.state.currentConnection.metadata.updatedAt = new Date().toISOString()
    }
    
    if (this.config.autoSave) {
      this.saveConnectionsToStorage()
    }
  }

  // 私有方法：保存配置到本地存储
  private saveConfigToStorage(): void {
    this.deps.storage.set('connections-service-config', this.config)
  }

  // 私有方法：从本地存储加载配置
  private loadConfigFromStorage(): void {
    try {
      const saved = this.deps.storage.get('connections-service-config')
      if (saved) {
        Object.assign(this.config, saved)
      }
    } catch (error) {
      this.deps.logger.error('加载连接服务配置失败:', error)
    }
  }

  // 私有方法：保存连接到本地存储
  private saveConnectionsToStorage(): void {
    try {
      this.deps.storage.set('connections', this.state.connections)
    } catch (error) {
      this.deps.logger.error('保存连接失败:', error)
    }
  }

  // 私有方法：从本地存储加载连接
  private loadConnections(): void {
    try {
      const saved = this.deps.storage.get('connections')
      if (saved) {
        this.state.connections = saved
      }
    } catch (error) {
      this.deps.logger.error('加载连接失败:', error)
    }
  }

  // 私有方法：从本地存储加载模板
  private loadTemplates(): void {
    try {
      const saved = this.deps.storage.get('connection-templates')
      if (saved) {
        this.state.templates = saved
      }
    } catch (error) {
      this.deps.logger.error('加载连接模板失败:', error)
    }
  }

  // 私有方法：开始自动刷新
  private startAutoRefresh(): void {
    if (this.refreshTimer) {
      clearInterval(this.refreshTimer)
    }
    
    this.refreshTimer = window.setInterval(async () => {
      await this.getConnections()
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
export const connectionsService = ConnectionsService.getInstance()

export default connectionsService
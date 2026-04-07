import { reactive, ref, computed } from 'vue'
import { 
  workflowApi,
  createWorkflow,
  getWorkflows,
  getWorkflow,
  updateWorkflow,
  deleteWorkflow,
  executeWorkflow,
  pauseWorkflow,
  resumeWorkflow,
  cancelWorkflow,
  getWorkflowLogs,
  getWorkflowStats,
  cloneWorkflow,
  exportWorkflow,
  importWorkflow,
  validateWorkflow,
  getWorkflowTemplates,
  applyWorkflowTemplate,
  saveWorkflowAsTemplate,
  getWorkflowExecutionHistory,
  rerunWorkflow
} from '../api/modules/workflow'
import type {
  WorkflowDefinition,
  WorkflowType,
  WorkflowNode,
  WorkflowConnection
} from '../api/modules/workflow'

// 工作流状态枚举
export enum WorkflowStatus {
  PENDING = 'pending',
  RUNNING = 'running',
  COMPLETED = 'completed',
  FAILED = 'failed',
  PAUSED = 'paused',
  CANCELLED = 'cancelled'
}

/**
 * 工作流管理服务类
 * 提供工作流的创建、执行、监控、管理等功能
 * 遵循单一职责原则和依赖注入模式
 */

// 工作流状态接口
export interface WorkflowServiceState {
  isLoading: boolean
  workflows: WorkflowDefinition[]
  currentWorkflow: WorkflowDefinition | null
  templates: Array<{
    id: string
    name: string
    description: string
    type: WorkflowType
    complexity: 'low' | 'medium' | 'high'
    tags: string[]
    template: Omit<WorkflowDefinition, 'id' | 'metadata' | 'execution' | 'results'>
    usageCount: number
    rating: number
    preview?: string
  }>
  executionHistory: Array<{
    executionId: string
    workflowId: string
    startTime: string
    endTime?: string
    duration?: number
    status: WorkflowStatus
    triggeredBy: string
    results?: any
  }>
  logs: Array<{
    timestamp: string
    level: 'info' | 'warning' | 'error'
    nodeId?: string
    message: string
    details?: any
  }>
  stats: {
    execution: {
      totalRuns: number
      successfulRuns: number
      failedRuns: number
      averageDuration: number
      lastRunTime?: string
    }
    performance: {
      nodeStats: Array<{
        nodeId: string
        nodeName: string
        averageExecutionTime: number
        successRate: number
        errorCount: number
      }>
      connectionStats: Array<{
        connectionId: string
        dataTransferred: number
        averageTransferRate: number
        errorCount: number
      }>
    }
    resources: {
      averageCpuUsage: number
      averageMemoryUsage: number
      peakCpuUsage: number
      peakMemoryUsage: number
    }
  } | null
  error: string | null
}

// 工作流配置接口
export interface WorkflowServiceConfig {
  autoSave: boolean
  autoRefresh: boolean
  refreshInterval: number
  maxHistoryItems: number
  defaultViewMode: 'list' | 'grid' | 'graph'
  notificationPreferences: {
    onExecutionStart: boolean
    onExecutionComplete: boolean
    onExecutionError: boolean
    onWorkflowUpdate: boolean
  }
}

// 事件类型定义
export interface WorkflowServiceEvents {
  'workflow-created': WorkflowDefinition
  'workflow-updated': WorkflowDefinition
  'workflow-deleted': { id: string }
  'workflow-execution-started': { workflowId: string; executionId: string }
  'workflow-execution-completed': { workflowId: string; executionId: string; results: any }
  'workflow-execution-failed': { workflowId: string; executionId: string; error: string }
  'workflow-execution-paused': { workflowId: string; executionId: string }
  'workflow-execution-resumed': { workflowId: string; executionId: string }
  'workflow-execution-cancelled': { workflowId: string; executionId: string; reason: string }
  'error-occurred': { type: string; message: string }
}

// 依赖注入接口
export interface WorkflowServiceDependencies {
  apiClient: typeof workflowApi
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

class WorkflowService {
  private static instance: WorkflowService
  private dependencies: WorkflowServiceDependencies
  private eventTarget: EventTarget
  private refreshTimer: number | null = null
  
  // 响应式状态
  public state = reactive<WorkflowServiceState>({
    isLoading: false,
    workflows: [],
    currentWorkflow: null,
    templates: [],
    executionHistory: [],
    logs: [],
    stats: null,
    error: null
  })

  // 配置
  public config = reactive<WorkflowServiceConfig>({
    autoSave: true,
    autoRefresh: true,
    refreshInterval: 30000, // 30秒
    maxHistoryItems: 100,
    defaultViewMode: 'list',
    notificationPreferences: {
      onExecutionStart: true,
      onExecutionComplete: true,
      onExecutionError: true,
      onWorkflowUpdate: false
    }
  })

  // 计算属性
  public get isLoading() {
    return this.state.isLoading
  }

  public get workflows() {
    return this.state.workflows
  }

  public get currentWorkflow() {
    return this.state.currentWorkflow
  }

  public get templates() {
    return this.state.templates
  }

  public get executionHistory() {
    return this.state.executionHistory
  }

  public get logs() {
    return this.state.logs
  }

  public get stats() {
    return this.state.stats
  }

  public get error() {
    return this.state.error
  }

  public get hasCurrentWorkflow() {
    return this.state.currentWorkflow !== null
  }

  public get runningWorkflows() {
    return this.state.workflows.filter(w => w.status === WorkflowStatus.RUNNING)
  }

  public get completedWorkflows() {
    return this.state.workflows.filter(w => w.status === WorkflowStatus.COMPLETED)
  }

  public get failedWorkflows() {
    return this.state.workflows.filter(w => w.status === WorkflowStatus.FAILED)
  }

  // 单例模式
  public static getInstance(dependencies?: WorkflowServiceDependencies): WorkflowService {
    if (!WorkflowService.instance) {
      WorkflowService.instance = new WorkflowService(dependencies)
    }
    return WorkflowService.instance
  }

  // 私有构造函数，支持依赖注入
  private constructor(dependencies?: WorkflowServiceDependencies) {
    this.eventTarget = new EventTarget()
    
    // 依赖注入，如果没有提供则使用默认实现
    this.dependencies = dependencies || {
      apiClient: workflowApi,
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
            this.dependencies.logger.error('存储失败:', error)
          }
        },
        remove: (key: string) => {
          try {
            localStorage.removeItem(key)
          } catch (error) {
            this.dependencies.logger.error('删除存储失败:', error)
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
          console.info(`[WorkflowService] ${message}`, ...args)
        },
        error: (message: string, error?: Error | unknown) => {
          console.error(`[WorkflowService] ${message}`, error)
        },
        warn: (message: string, ...args: any[]) => {
          console.warn(`[WorkflowService] ${message}`, ...args)
        }
      }
    }

    this.loadConfigFromStorage()
    this.loadWorkflows()
    this.startAutoRefresh()
  }

  // 创建工作流
  public async createWorkflow(
    workflow: Omit<WorkflowDefinition, 'id' | 'metadata' | 'execution' | 'results'>
  ): Promise<string | null> {
    this.setLoading(true)
    this.clearError()

    try {
      this.dependencies.logger.info('开始创建工作流:', workflow)
      
      const response = await this.dependencies.apiClient.createWorkflow(workflow)
      
      if (response.success && response.data) {
        const newWorkflow = {
          ...workflow,
          id: response.data.id,
          metadata: {
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString(),
            createdBy: 'current-user',
            version: '1.0.0',
            tags: []
          },
          execution: {
            progress: 0
          }
        }
        
        this.state.workflows.unshift(newWorkflow)
        this.emitEvent('workflow-created', newWorkflow)
        
        if (this.config.autoSave) {
          this.saveWorkflowsToStorage()
        }
        
        this.dependencies.logger.info('工作流创建成功:', newWorkflow)
        return response.data.id
      } else {
        throw new Error(response.message || '创建工作流失败')
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : '创建工作流失败'
      this.setError(errorMessage)
      this.emitEvent('error-occurred', { type: 'creation-error', message: errorMessage })
      return null
    } finally {
      this.setLoading(false)
    }
  }

  // 获取工作流列表
  public async getWorkflows(
    page = 1,
    pageSize = 10,
    filters?: {
      type?: WorkflowType
      status?: WorkflowStatus
      tags?: string[]
      dateRange?: { start: string; end: string }
    }
  ): Promise<void> {
    this.setLoading(true)
    this.clearError()

    try {
      this.dependencies.logger.info('开始获取工作流列表:', { page, pageSize, filters })
      
      const response = await this.dependencies.apiClient.getWorkflows(page, pageSize, filters)
      
      if (response.success && response.data) {
        if (page === 1) {
          this.state.workflows = response.data.workflows
        } else {
          this.state.workflows.push(...response.data.workflows)
        }
        
        this.dependencies.logger.info('工作流列表获取成功:', response.data)
      } else {
        throw new Error(response.message || '获取工作流列表失败')
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : '获取工作流列表失败'
      this.setError(errorMessage)
      this.emitEvent('error-occurred', { type: 'list-error', message: errorMessage })
    } finally {
      this.setLoading(false)
    }
  }

  // 获取工作流详情
  public async getWorkflow(id: string): Promise<WorkflowDefinition | null> {
    this.setLoading(true)
    this.clearError()

    try {
      this.dependencies.logger.info('开始获取工作流详情:', id)
      
      const response = await this.dependencies.apiClient.getWorkflow(id)
      
      if (response.success && response.data) {
        this.state.currentWorkflow = response.data
        this.emitEvent('workflow-updated', response.data)
        
        this.dependencies.logger.info('工作流详情获取成功:', response.data)
        return response.data
      } else {
        throw new Error(response.message || '获取工作流详情失败')
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : '获取工作流详情失败'
      this.setError(errorMessage)
      this.emitEvent('error-occurred', { type: 'detail-error', message: errorMessage })
      return null
    } finally {
      this.setLoading(false)
    }
  }

  // 更新工作流
  public async updateWorkflow(
    id: string,
    updates: Partial<WorkflowDefinition>
  ): Promise<boolean> {
    this.setLoading(true)
    this.clearError()

    try {
      this.dependencies.logger.info('开始更新工作流:', { id, updates })
      
      const response = await this.dependencies.apiClient.updateWorkflow(id, updates)
      
      if (response.success && response.data.success) {
        // 更新本地状态
        const index = this.state.workflows.findIndex(w => w.id === id)
        if (index !== -1) {
          Object.assign(this.state.workflows[index], updates)
          this.state.workflows[index].metadata.updatedAt = new Date().toISOString()
        }
        
        // 更新当前工作流
        if (this.state.currentWorkflow && this.state.currentWorkflow.id === id) {
          Object.assign(this.state.currentWorkflow, updates)
          this.state.currentWorkflow.metadata.updatedAt = new Date().toISOString()
        }
        
        this.emitEvent('workflow-updated', this.state.currentWorkflow || this.state.workflows[index])
        
        if (this.config.autoSave) {
          this.saveWorkflowsToStorage()
        }
        
        this.dependencies.logger.info('工作流更新成功:', updates)
        return true
      } else {
        throw new Error(response.message || '更新工作流失败')
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : '更新工作流失败'
      this.setError(errorMessage)
      this.emitEvent('error-occurred', { type: 'update-error', message: errorMessage })
      return false
    } finally {
      this.setLoading(false)
    }
  }

  // 删除工作流
  public async deleteWorkflow(id: string): Promise<boolean> {
    this.setLoading(true)
    this.clearError()

    try {
      this.dependencies.logger.info('开始删除工作流:', id)
      
      const response = await this.dependencies.apiClient.deleteWorkflow(id)
      
      if (response.success && response.data.success) {
        // 从本地状态中移除
        this.state.workflows = this.state.workflows.filter(w => w.id !== id)
        
        // 清除当前工作流（如果被删除的是当前工作流）
        if (this.state.currentWorkflow && this.state.currentWorkflow.id === id) {
          this.state.currentWorkflow = null
        }
        
        this.emitEvent('workflow-deleted', { id })
        
        if (this.config.autoSave) {
          this.saveWorkflowsToStorage()
        }
        
        this.dependencies.logger.info('工作流删除成功:', id)
        return true
      } else {
        throw new Error(response.message || '删除工作流失败')
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : '删除工作流失败'
      this.setError(errorMessage)
      this.emitEvent('error-occurred', { type: 'deletion-error', message: errorMessage })
      return false
    } finally {
      this.setLoading(false)
    }
  }

  // 执行工作流
  public async executeWorkflow(
    id: string,
    options?: {
      priority?: 'low' | 'normal' | 'high'
      resources?: {
        cpu?: number
        memory?: number
        gpu?: number
      }
      notifications?: {
        email?: boolean
        webhook?: string
      }
    }
  ): Promise<string | null> {
    this.setLoading(true)
    this.clearError()

    try {
      this.dependencies.logger.info('开始执行工作流:', { id, options })
      
      const response = await this.dependencies.apiClient.executeWorkflow(id, options)
      
      if (response.success && response.data.executionId) {
        // 更新工作流状态
        const index = this.state.workflows.findIndex(w => w.id === id)
        if (index !== -1) {
          this.state.workflows[index].status = WorkflowStatus.RUNNING
          this.state.workflows[index].execution.startTime = new Date().toISOString()
          this.state.workflows[index].execution.progress = 0
        }
        
        // 更新当前工作流
        if (this.state.currentWorkflow && this.state.currentWorkflow.id === id) {
          this.state.currentWorkflow.status = WorkflowStatus.RUNNING
          this.state.currentWorkflow.execution.startTime = new Date().toISOString()
          this.state.currentWorkflow.execution.progress = 0
        }
        
        this.emitEvent('workflow-execution-started', { 
          workflowId: id, 
          executionId: response.data.executionId 
        })
        
        if (this.config.notificationPreferences.onExecutionStart) {
          this.dependencies.notification.show('工作流执行已开始', 'info')
        }
        
        this.dependencies.logger.info('工作流执行成功:', response.data)
        return response.data.executionId
      } else {
        throw new Error(response.message || '执行工作流失败')
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : '执行工作流失败'
      this.setError(errorMessage)
      this.emitEvent('error-occurred', { type: 'execution-error', message: errorMessage })
      return null
    } finally {
      this.setLoading(false)
    }
  }

  // 暂停工作流
  public async pauseWorkflow(id: string, reason?: string): Promise<boolean> {
    this.setLoading(true)
    this.clearError()

    try {
      this.dependencies.logger.info('开始暂停工作流:', { id, reason })
      
      const response = await this.dependencies.apiClient.pauseWorkflow(id, reason)
      
      if (response.success && response.data.success) {
        // 更新工作流状态
        this.updateWorkflowStatus(id, WorkflowStatus.PAUSED)
        
        this.emitEvent('workflow-execution-paused', { 
          workflowId: id, 
          executionId: this.getExecutionId(id) 
        })
        
        this.dependencies.logger.info('工作流暂停成功:', response.data)
        return true
      } else {
        throw new Error(response.message || '暂停工作流失败')
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : '暂停工作流失败'
      this.setError(errorMessage)
      this.emitEvent('error-occurred', { type: 'pause-error', message: errorMessage })
      return false
    } finally {
      this.setLoading(false)
    }
  }

  // 恢复工作流
  public async resumeWorkflow(id: string): Promise<boolean> {
    this.setLoading(true)
    this.clearError()

    try {
      this.dependencies.logger.info('开始恢复工作流:', id)
      
      const response = await this.dependencies.apiClient.resumeWorkflow(id)
      
      if (response.success && response.data.success) {
        // 更新工作流状态
        this.updateWorkflowStatus(id, WorkflowStatus.RUNNING)
        
        this.emitEvent('workflow-execution-resumed', { 
          workflowId: id, 
          executionId: this.getExecutionId(id) 
        })
        
        this.dependencies.logger.info('工作流恢复成功:', response.data)
        return true
      } else {
        throw new Error(response.message || '恢复工作流失败')
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : '恢复工作流失败'
      this.setError(errorMessage)
      this.emitEvent('error-occurred', { type: 'resume-error', message: errorMessage })
      return false
    } finally {
      this.setLoading(false)
    }
  }

  // 取消工作流
  public async cancelWorkflow(id: string, reason?: string): Promise<boolean> {
    this.setLoading(true)
    this.clearError()

    try {
      this.dependencies.logger.info('开始取消工作流:', { id, reason })
      
      const response = await this.dependencies.apiClient.cancelWorkflow(id, reason)
      
      if (response.success && response.data.success) {
        // 更新工作流状态
        this.updateWorkflowStatus(id, WorkflowStatus.CANCELLED)
        
        this.emitEvent('workflow-execution-cancelled', { 
          workflowId: id, 
          executionId: this.getExecutionId(id),
          reason: reason || '用户取消' 
        })
        
        this.dependencies.logger.info('工作流取消成功:', response.data)
        return true
      } else {
        throw new Error(response.message || '取消工作流失败')
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : '取消工作流失败'
      this.setError(errorMessage)
      this.emitEvent('error-occurred', { type: 'cancel-error', message: errorMessage })
      return false
    } finally {
      this.setLoading(false)
    }
  }

  // 获取工作流执行日志
  public async getWorkflowLogs(
    id: string,
    options?: {
      level?: 'info' | 'warning' | 'error'
      startTime?: string
      endTime?: string
      nodeId?: string
      page?: number
      pageSize?: number
    }
  ): Promise<void> {
    try {
      this.dependencies.logger.info('开始获取工作流执行日志:', { id, options })
      
      const response = await this.dependencies.apiClient.getWorkflowLogs(id, options)
      
      if (response.success && response.data) {
        if (options?.page === 1 || !options?.page) {
          this.state.logs = response.data.logs
        } else {
          this.state.logs.push(...response.data.logs)
        }
        
        this.dependencies.logger.info('工作流执行日志获取成功:', response.data)
      } else {
        throw new Error(response.message || '获取工作流执行日志失败')
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : '获取工作流执行日志失败'
      this.setError(errorMessage)
      this.emitEvent('error-occurred', { type: 'logs-error', message: errorMessage })
    }
  }

  // 获取工作流执行统计
  public async getWorkflowStats(id: string): Promise<void> {
    try {
      this.dependencies.logger.info('开始获取工作流执行统计:', id)
      
      const response = await this.dependencies.apiClient.getWorkflowStats(id)
      
      if (response.success && response.data) {
        this.state.stats = response.data
        this.dependencies.logger.info('工作流执行统计获取成功:', response.data)
      } else {
        throw new Error(response.message || '获取工作流执行统计失败')
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : '获取工作流执行统计失败'
      this.setError(errorMessage)
      this.emitEvent('error-occurred', { type: 'stats-error', message: errorMessage })
    }
  }

  // 克隆工作流
  public async cloneWorkflow(id: string, newName?: string): Promise<string | null> {
    this.setLoading(true)
    this.clearError()

    try {
      this.dependencies.logger.info('开始克隆工作流:', { id, newName })
      
      const response = await this.dependencies.apiClient.cloneWorkflow(id, newName)
      
      if (response.success && response.data.newId) {
        // 重新获取工作流列表以包含克隆的工作流
        await this.getWorkflows()
        
        const clonedWorkflow = this.state.workflows.find(w => w.id === response.data.newId)
        if (clonedWorkflow) {
          this.emitEvent('workflow-created', clonedWorkflow)
        }
        
        if (this.config.autoSave) {
          this.saveWorkflowsToStorage()
        }
        
        this.dependencies.logger.info('工作流克隆成功:', response.data)
        return response.data.newId
      } else {
        throw new Error(response.message || '克隆工作流失败')
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : '克隆工作流失败'
      this.setError(errorMessage)
      this.emitEvent('error-occurred', { type: 'clone-error', message: errorMessage })
      return null
    } finally {
      this.setLoading(false)
    }
  }

  // 更新配置
  public updateConfig(newConfig: Partial<WorkflowServiceConfig>): void {
    Object.assign(this.config, newConfig)
    this.saveConfigToStorage()
    
    // 重新启动自动刷新
    if (newConfig.autoRefresh !== undefined) {
      this.stopAutoRefresh()
      if (newConfig.autoRefresh) {
        this.startAutoRefresh()
      }
    }
    
    this.dependencies.logger.info('工作流配置已更新:', this.config)
  }

  // 清除当前工作流
  public clearCurrentWorkflow(): void {
    this.state.currentWorkflow = null
    this.state.logs = []
    this.state.stats = null
    this.clearError()
  }

  // 清除错误
  public clearError(): void {
    this.state.error = null
  }

  // 事件监听
  public addEventListener<K extends keyof WorkflowServiceEvents>(
    event: K,
    listener: (event: CustomEvent<WorkflowServiceEvents[K]>) => void
  ): void {
    this.eventTarget.addEventListener(event, listener as EventListener)
  }

  // 移除事件监听
  public removeEventListener<K extends keyof WorkflowServiceEvents>(
    event: K,
    listener: (event: CustomEvent<WorkflowServiceEvents[K]>) => void
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
  private emitEvent<K extends keyof WorkflowServiceEvents>(
    event: K,
    detail: WorkflowServiceEvents[K]
  ): void {
    this.eventTarget.dispatchEvent(new CustomEvent(event, { detail }))
  }

  // 私有方法：更新工作流状态
  private updateWorkflowStatus(id: string, status: WorkflowStatus): void {
    // 更新工作流列表中的状态
    const index = this.state.workflows.findIndex(w => w.id === id)
    if (index !== -1) {
      this.state.workflows[index].status = status
      this.state.workflows[index].metadata.updatedAt = new Date().toISOString()
    }
    
    // 更新当前工作流状态
    if (this.state.currentWorkflow && this.state.currentWorkflow.id === id) {
      this.state.currentWorkflow.status = status
      this.state.currentWorkflow.metadata.updatedAt = new Date().toISOString()
    }
    
    if (this.config.autoSave) {
      this.saveWorkflowsToStorage()
    }
  }

  // 私有方法：获取执行ID
  private getExecutionId(workflowId: string): string {
    // 这里应该从执行历史中获取最新的执行ID
    const latestExecution = this.state.executionHistory
      .filter(e => e.workflowId === workflowId)
      .sort((a, b) => new Date(b.startTime).getTime() - new Date(a.startTime).getTime())[0]
    
    return latestExecution?.executionId || ''
  }

  // 私有方法：保存配置到本地存储
  private saveConfigToStorage(): void {
    this.dependencies.storage.set('workflow-service-config', this.config)
  }

  // 私有方法：从本地存储加载配置
  private loadConfigFromStorage(): void {
    try {
      const saved = this.dependencies.storage.get('workflow-service-config')
      if (saved) {
        Object.assign(this.config, saved)
      }
    } catch (error) {
      this.dependencies.logger.error('加载工作流配置失败:', error)
    }
  }

  // 私有方法：保存工作流到本地存储
  private saveWorkflowsToStorage(): void {
    try {
      this.dependencies.storage.set('workflows', this.state.workflows)
    } catch (error) {
      this.dependencies.logger.error('保存工作流失败:', error)
    }
  }

  // 私有方法：从本地存储加载工作流
  private loadWorkflows(): void {
    try {
      const saved = this.dependencies.storage.get('workflows')
      if (saved) {
        this.state.workflows = saved
      }
    } catch (error) {
      this.dependencies.logger.error('加载工作流失败:', error)
    }
  }

  // 私有方法：开始自动刷新
  private startAutoRefresh(): void {
    if (this.refreshTimer) {
      clearInterval(this.refreshTimer)
    }
    
    this.refreshTimer = window.setInterval(async () => {
      await this.getWorkflows()
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
export const workflowService = WorkflowService.getInstance()

export default workflowService
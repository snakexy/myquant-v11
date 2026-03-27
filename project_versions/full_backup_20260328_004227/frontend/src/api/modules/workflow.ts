import { apiRequest, type ApiResponse } from '../index'

/**
 * 工作流管理API模块
 * 提供工作流的创建、执行、监控、管理等功能
 */

// 工作流状态枚举
export enum WorkflowStatus {
  PENDING = 'pending',
  RUNNING = 'running',
  COMPLETED = 'completed',
  FAILED = 'failed',
  PAUSED = 'paused',
  CANCELLED = 'cancelled'
}

// 工作流类型枚举
export enum WorkflowType {
  BACKTEST = 'backtest',
  OPTIMIZATION = 'optimization',
  ANALYSIS = 'analysis',
  DATA_PROCESSING = 'data_processing'
}

// 工作流节点接口
export interface WorkflowNode {
  id: string
  type: string
  title: string
  status: WorkflowStatus
  position: { x: number; y: number }
  parameters: Record<string, any>
  startTime?: string
  endTime?: string
  duration?: number
  error?: string
  logs?: Array<{
    timestamp: string
    level: 'info' | 'warning' | 'error'
    message: string
  }>
}

// 工作流连接接口
export interface WorkflowConnection {
  id: string
  from: string
  to: string
  type: 'data' | 'control' | 'event'
  status: 'active' | 'inactive' | 'error'
  dataFlow?: {
    bytesTransferred: number
    transferRate: number
  }
}

// 工作流定义接口
export interface WorkflowDefinition {
  id: string
  name: string
  description: string
  type: WorkflowType
  status: WorkflowStatus
  nodes: WorkflowNode[]
  connections: WorkflowConnection[]
  metadata: {
    createdAt: string
    updatedAt: string
    createdBy: string
    version: string
    tags: string[]
  }
  execution: {
    startTime?: string
    endTime?: string
    duration?: number
    progress: number
    currentStep?: string
    estimatedTimeRemaining?: number
  }
  results?: {
    summary: Record<string, any>
    artifacts: Array<{
      name: string
      type: string
      url: string
      size: number
    }>
    performance: {
      accuracy?: number
      sharpeRatio?: number
      maxDrawdown?: number
      annualReturn?: number
    }
  }
}

// 创建工作流API
export const createWorkflow = async (
  workflow: Omit<WorkflowDefinition, 'id' | 'metadata' | 'execution' | 'results'>
): Promise<ApiResponse<{ id: string }>> => {
  return apiRequest.post('/research/workflows', workflow)
}

// 获取工作流列表API
export const getWorkflows = async (
  page = 1,
  pageSize = 10,
  filters?: {
    type?: WorkflowType
    status?: WorkflowStatus
    tags?: string[]
    dateRange?: { start: string; end: string }
  }
): Promise<ApiResponse<{
  workflows: WorkflowDefinition[]
  total: number
  page: number
  pageSize: number
}>> => {
  const params = new URLSearchParams({
    page: page.toString(),
    pageSize: pageSize.toString()
  })
  
  if (filters) {
    if (filters.type) params.append('type', filters.type)
    if (filters.status) params.append('status', filters.status)
    if (filters.tags) params.append('tags', filters.tags.join(','))
    if (filters.dateRange) {
      params.append('startDate', filters.dateRange.start)
      params.append('endDate', filters.dateRange.end)
    }
  }
  
  return apiRequest.get(`/research/workflows?${params.toString()}`)
}

// 获取工作流详情API
export const getWorkflow = async (
  id: string
): Promise<ApiResponse<WorkflowDefinition>> => {
  return apiRequest.get(`/research/workflows/${id}`)
}

// 更新工作流API
export const updateWorkflow = async (
  id: string,
  updates: Partial<WorkflowDefinition>
): Promise<ApiResponse<{ success: boolean }>> => {
  return apiRequest.put(`/research/workflows/${id}`, updates)
}

// 删除工作流API
export const deleteWorkflow = async (
  id: string
): Promise<ApiResponse<{ success: boolean }>> => {
  return apiRequest.delete(`/research/workflows/${id}`)
}

// 执行工作流API
export const executeWorkflow = async (
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
  },
  timeout?: number
): Promise<ApiResponse<{ executionId: string }>> => {
  return apiRequest.post(`/research/workflows/${id}/execute`, options, {
    timeout: timeout || 600000  // 默认10分钟超时，工作流执行可能需要较长时间
  })
}

// 暂停工作流API
export const pauseWorkflow = async (
  id: string,
  reason?: string
): Promise<ApiResponse<{ success: boolean }>> => {
  return apiRequest.post(`/workflow/${id}/pause`, { reason })
}

// 恢复工作流API
export const resumeWorkflow = async (
  id: string
): Promise<ApiResponse<{ success: boolean }>> => {
  return apiRequest.post(`/workflow/${id}/resume`)
}

// 取消工作流API
export const cancelWorkflow = async (
  id: string,
  reason?: string
): Promise<ApiResponse<{ success: boolean }>> => {
  return apiRequest.post(`/workflow/${id}/cancel`, { reason })
}

// 获取工作流执行日志API
export const getWorkflowLogs = async (
  id: string,
  options?: {
    level?: 'info' | 'warning' | 'error'
    startTime?: string
    endTime?: string
    nodeId?: string
    page?: number
    pageSize?: number
  }
): Promise<ApiResponse<{
  logs: Array<{
    timestamp: string
    level: 'info' | 'warning' | 'error'
    nodeId?: string
    message: string
    details?: any
  }>
  total: number
  page: number
  pageSize: number
}>> => {
  const params = new URLSearchParams()
  
  if (options) {
    if (options.level) params.append('level', options.level)
    if (options.startTime) params.append('startTime', options.startTime)
    if (options.endTime) params.append('endTime', options.endTime)
    if (options.nodeId) params.append('nodeId', options.nodeId)
    if (options.page) params.append('page', options.page.toString())
    if (options.pageSize) params.append('pageSize', options.pageSize.toString())
  }
  
  return apiRequest.get(`/workflow/${id}/logs?${params.toString()}`)
}

// 获取工作流执行统计API
export const getWorkflowStats = async (
  id: string
): Promise<ApiResponse<{
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
}>> => {
  return apiRequest.get(`/workflow/${id}/stats`)
}

// 克隆工作流API
export const cloneWorkflow = async (
  id: string,
  newName?: string
): Promise<ApiResponse<{ newId: string }>> => {
  return apiRequest.post(`/workflow/${id}/clone`, { newName })
}

// 导出工作流API
export const exportWorkflow = async (
  id: string,
  format: 'json' | 'yaml' | 'xml' = 'json'
): Promise<void> => {
  return apiRequest.download(`/workflow/${id}/export?format=${format}`, `workflow-${id}.${format}`)
}

// 导入工作流API
export const importWorkflow = async (
  file: File,
  timeout?: number
): Promise<ApiResponse<{ id: string }>> => {
  const formData = new FormData()
  formData.append('file', file)
  return apiRequest.upload('/workflow/import', formData, {
    timeout: timeout || 120000  // 默认2分钟超时，文件上传可能需要较长时间
  })
}

// 验证工作流API
export const validateWorkflow = async (
  workflow: Partial<WorkflowDefinition>
): Promise<ApiResponse<{
  isValid: boolean
  errors: Array<{
    type: 'syntax' | 'logic' | 'dependency' | 'resource'
    message: string
    nodeId?: string
    connectionId?: string
  }>
  warnings: Array<{
    type: 'performance' | 'best_practice' | 'compatibility'
    message: string
    nodeId?: string
    connectionId?: string
  }>
}>> => {
  return apiRequest.post('/workflow/validate', workflow)
}

// 获取工作流模板API
export const getWorkflowTemplates = async (
  type?: WorkflowType
): Promise<ApiResponse<Array<{
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
}>>> => {
  const url = type 
    ? `/workflow/templates?type=${type}`
    : '/workflow/templates'
  return apiRequest.get(url)
}

// 应用工作流模板API
export const applyWorkflowTemplate = async (
  templateId: string,
  customizations?: {
    name?: string
    description?: string
    parameters?: Record<string, any>
  }
): Promise<ApiResponse<{ id: string }>> => {
  return apiRequest.post(`/workflow/templates/${templateId}/apply`, customizations)
}

// 保存工作流为模板API
export const saveWorkflowAsTemplate = async (
  id: string,
  templateInfo: {
    name: string
    description: string
    tags: string[]
    isPublic?: boolean
  }
): Promise<ApiResponse<{ templateId: string }>> => {
  return apiRequest.post(`/workflow/${id}/save-as-template`, templateInfo)
}

// 获取工作流执行历史API
export const getWorkflowExecutionHistory = async (
  id: string,
  page = 1,
  pageSize = 10
): Promise<ApiResponse<{
  executions: Array<{
    executionId: string
    startTime: string
    endTime?: string
    duration?: number
    status: WorkflowStatus
    triggeredBy: string
    results?: any
  }>
  total: number
  page: number
  pageSize: number
}>> => {
  return apiRequest.get(`/workflow/${id}/history?page=${page}&pageSize=${pageSize}`)
}

// 重新执行工作流API
export const rerunWorkflow = async (
  id: string,
  executionId: string,
  options?: {
    fromNode?: string
    parameters?: Record<string, any>
  }
): Promise<ApiResponse<{ newExecutionId: string }>> => {
  return apiRequest.post(`/workflow/${id}/rerun/${executionId}`, options)
}

// 工作流API对象，便于统一管理
export const workflowApi = {
  // 基本操作
  createWorkflow,
  getWorkflows,
  getWorkflow,
  updateWorkflow,
  deleteWorkflow,
  
  // 执行控制
  executeWorkflow,
  pauseWorkflow,
  resumeWorkflow,
  cancelWorkflow,
  
  // 监控日志
  getWorkflowLogs,
  getWorkflowStats,
  
  // 导入导出
  cloneWorkflow,
  exportWorkflow,
  importWorkflow,
  
  // 验证模板
  validateWorkflow,
  getWorkflowTemplates,
  applyWorkflowTemplate,
  saveWorkflowAsTemplate,
  
  // 历史管理
  getWorkflowExecutionHistory,
  rerunWorkflow
}

export default workflowApi
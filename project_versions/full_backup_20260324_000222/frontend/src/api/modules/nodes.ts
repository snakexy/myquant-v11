import { apiRequest, type ApiResponse } from '../index'

/**
 * 节点管理API模块
 * 提供节点的创建、配置、监控、管理等功能
 */

// 节点状态枚举
export enum NodeStatus {
  IDLE = 'idle',
  RUNNING = 'running',
  COMPLETED = 'completed',
  FAILED = 'failed',
  PAUSED = 'paused',
  DISABLED = 'disabled'
}

// 节点类型枚举
export enum NodeType {
  CONFIG = 'config',
  DATA_SOURCE = 'data_source',
  DATA_PROCESSING = 'data_processing',
  STRATEGY = 'strategy',
  BACKTEST = 'backtest',
  ANALYSIS = 'analysis',
  VISUALIZATION = 'visualization',
  EXPORT = 'export'
}

// 节点接口
export interface Node {
  id: string
  type: NodeType
  title: string
  description?: string
  status: NodeStatus
  position: { x: number; y: number }
  size?: { width: number; height: number }
  parameters: Record<string, any>
  metadata: {
    createdAt: string
    updatedAt: string
    version: string
    category: string
    tags: string[]
  }
  execution: {
    startTime?: string
    endTime?: string
    duration?: number
    progress: number
    cpuUsage?: number
    memoryUsage?: number
    lastError?: string
  }
  styling: {
    color?: string
    icon?: string
    shape?: 'rectangle' | 'circle' | 'diamond' | 'hexagon'
    borderColor?: string
    borderWidth?: number
  }
  permissions: {
    canEdit: boolean
    canDelete: boolean
    canExecute: boolean
    canConfigure: boolean
  }
}

// 节点模板接口
export interface NodeTemplate {
  id: string
  type: NodeType
  title: string
  description: string
  category: string
  icon: string
  color: string
  parameters: Array<{
    name: string
    type: 'string' | 'number' | 'boolean' | 'select' | 'file'
    label: string
    description?: string
    defaultValue?: any
    required?: boolean
    options?: string[]
    validation?: {
      min?: number
      max?: number
      pattern?: string
    }
  }>
  inputs: Array<{
    name: string
    type: string
    required?: boolean
    description?: string
  }>
  outputs: Array<{
    name: string
    type: string
    description?: string
  }>
  usageCount: number
  rating: number
  isBuiltIn: boolean
}

// 节点执行日志接口
export interface NodeExecutionLog {
  id: string
  nodeId: string
  timestamp: string
  level: 'debug' | 'info' | 'warning' | 'error'
  message: string
  details?: any
  stackTrace?: string
}

// 节点性能指标接口
export interface NodePerformanceMetrics {
  nodeId: string
  timestamp: string
  cpuUsage: number
  memoryUsage: number
  executionTime: number
  throughput: number
  errorRate: number
  dataProcessed: number
}

// 创建节点API
export const createNode = async (
  node: Omit<Node, 'id' | 'metadata' | 'execution' | 'permissions'>
): Promise<ApiResponse<{ id: string }>> => {
  return apiRequest.post('/nodes/create', node)
}

// 获取节点列表API
export const getNodes = async (
  page = 1,
  pageSize = 10,
  filters?: {
    type?: NodeType
    status?: NodeStatus
    category?: string
    tags?: string[]
    search?: string
  }
): Promise<ApiResponse<{
  nodes: Node[]
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
    if (filters.category) params.append('category', filters.category)
    if (filters.tags) params.append('tags', filters.tags.join(','))
    if (filters.search) params.append('search', filters.search)
  }
  
  return apiRequest.get(`/nodes/list?${params.toString()}`)
}

// 获取节点详情API
export const getNode = async (
  id: string
): Promise<ApiResponse<Node>> => {
  return apiRequest.get(`/nodes/${id}`)
}

// 更新节点API
export const updateNode = async (
  id: string,
  updates: Partial<Node>
): Promise<ApiResponse<{ success: boolean }>> => {
  return apiRequest.put(`/nodes/${id}`, updates)
}

// 删除节点API
export const deleteNode = async (
  id: string
): Promise<ApiResponse<{ success: boolean }>> => {
  return apiRequest.delete(`/nodes/${id}`)
}

// 复制节点API
export const duplicateNode = async (
  id: string,
  newPosition?: { x: number; y: number }
): Promise<ApiResponse<{ newId: string }>> => {
  return apiRequest.post(`/nodes/${id}/duplicate`, { newPosition })
}

// 执行节点API
export const executeNode = async (
  id: string,
  parameters?: Record<string, any>
): Promise<ApiResponse<{ executionId: string }>> => {
  return apiRequest.post(`/nodes/${id}/execute`, { parameters })
}

// 停止节点执行API
export const stopNode = async (
  id: string
): Promise<ApiResponse<{ success: boolean }>> => {
  return apiRequest.post(`/nodes/${id}/stop`)
}

// 暂停节点执行API
export const pauseNode = async (
  id: string
): Promise<ApiResponse<{ success: boolean }>> => {
  return apiRequest.post(`/nodes/${id}/pause`)
}

// 恢复节点执行API
export const resumeNode = async (
  id: string
): Promise<ApiResponse<{ success: boolean }>> => {
  return apiRequest.post(`/nodes/${id}/resume`)
}

// 获取节点执行日志API
export const getNodeLogs = async (
  id: string,
  options?: {
    level?: 'debug' | 'info' | 'warning' | 'error'
    startTime?: string
    endTime?: string
    page?: number
    pageSize?: number
  }
): Promise<ApiResponse<{
  logs: NodeExecutionLog[]
  total: number
  page: number
  pageSize: number
}>> => {
  const params = new URLSearchParams()
  
  if (options) {
    if (options.level) params.append('level', options.level)
    if (options.startTime) params.append('startTime', options.startTime)
    if (options.endTime) params.append('endTime', options.endTime)
    if (options.page) params.append('page', options.page.toString())
    if (options.pageSize) params.append('pageSize', options.pageSize.toString())
  }
  
  return apiRequest.get(`/nodes/${id}/logs?${params.toString()}`)
}

// 获取节点性能指标API
export const getNodeMetrics = async (
  id: string,
  timeRange?: { start: string; end: string }
): Promise<ApiResponse<{
  metrics: NodePerformanceMetrics[]
  summary: {
    averageCpuUsage: number
    averageMemoryUsage: number
    averageExecutionTime: number
    peakCpuUsage: number
    peakMemoryUsage: number
    totalExecutions: number
    successRate: number
  }
}>> => {
  const params = new URLSearchParams()
  
  if (timeRange) {
    params.append('startTime', timeRange.start)
    params.append('endTime', timeRange.end)
  }
  
  return apiRequest.get(`/nodes/${id}/metrics?${params.toString()}`)
}

// 获取节点模板列表API
export const getNodeTemplates = async (
  type?: NodeType,
  category?: string
): Promise<ApiResponse<{
  templates: NodeTemplate[]
  categories: string[]
}>> => {
  const params = new URLSearchParams()
  
  if (type) params.append('type', type)
  if (category) params.append('category', category)
  
  return apiRequest.get(`/nodes/templates?${params.toString()}`)
}

// 获取节点模板详情API
export const getNodeTemplate = async (
  id: string
): Promise<ApiResponse<NodeTemplate>> => {
  return apiRequest.get(`/nodes/templates/${id}`)
}

// 从模板创建节点API
export const createNodeFromTemplate = async (
  templateId: string,
  position: { x: number; y: number },
  parameters?: Record<string, any>
): Promise<ApiResponse<{ nodeId: string }>> => {
  return apiRequest.post(`/nodes/templates/${templateId}/create`, {
    position,
    parameters
  })
}

// 验证节点配置API
export const validateNode = async (
  node: Partial<Node>
): Promise<ApiResponse<{
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
}>> => {
  return apiRequest.post('/nodes/validate', node)
}

// 获取节点依赖关系API
export const getNodeDependencies = async (
  id: string
): Promise<ApiResponse<{
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
}>> => {
  return apiRequest.get(`/nodes/${id}/dependencies`)
}

// 批量操作节点API
export const batchNodeOperation = async (
  operation: 'delete' | 'execute' | 'stop' | 'pause' | 'resume',
  nodeIds: string[]
): Promise<ApiResponse<{
  results: Array<{
    nodeId: string
    success: boolean
    error?: string
  }>
  summary: {
    total: number
    successful: number
    failed: number
  }
}>> => {
  return apiRequest.post('/nodes/batch', {
    operation,
    nodeIds
  })
}

// 导出节点配置API
export const exportNode = async (
  id: string,
  format: 'json' | 'yaml' | 'xml' = 'json'
): Promise<void> => {
  return apiRequest.download(`/nodes/${id}/export?format=${format}`, `node-${id}.${format}`)
}

// 导入节点配置API
export const importNode = async (
  file: File
): Promise<ApiResponse<{ nodeId: string }>> => {
  const formData = new FormData()
  formData.append('file', file)
  return apiRequest.upload('/nodes/import', formData)
}

// 获取节点分类API
export const getNodeCategories = async (): Promise<ApiResponse<{
  categories: Array<{
    name: string
    description: string
    nodeCount: number
    icon: string
    color: string
  }>
}>> => {
  return apiRequest.get('/nodes/categories')
}

// 搜索节点API
export const searchNodes = async (
  query: string,
  filters?: {
    type?: NodeType
    category?: string
    tags?: string[]
  }
): Promise<ApiResponse<{
  nodes: Array<{
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
  total: number
}>> => {
  const params = new URLSearchParams({ query })
  
  if (filters) {
    if (filters.type) params.append('type', filters.type)
    if (filters.category) params.append('category', filters.category)
    if (filters.tags) params.append('tags', filters.tags.join(','))
  }
  
  return apiRequest.get(`/nodes/search?${params.toString()}`)
}

// 获取节点使用统计API
export const getNodeUsageStats = async (
  id: string,
  timeRange?: { start: string; end: string }
): Promise<ApiResponse<{
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
}>> => {
  const params = new URLSearchParams()
  
  if (timeRange) {
    params.append('startTime', timeRange.start)
    params.append('endTime', timeRange.end)
  }
  
  return apiRequest.get(`/nodes/${id}/usage-stats?${params.toString()}`)
}

// 节点API对象，便于统一管理
export const nodesApi = {
  // 基本操作
  createNode,
  getNodes,
  getNode,
  updateNode,
  deleteNode,
  duplicateNode,
  
  // 执行控制
  executeNode,
  stopNode,
  pauseNode,
  resumeNode,
  
  // 监控日志
  getNodeLogs,
  getNodeMetrics,
  getNodeUsageStats,
  
  // 模板管理
  getNodeTemplates,
  getNodeTemplate,
  createNodeFromTemplate,
  
  // 验证依赖
  validateNode,
  getNodeDependencies,
  
  // 批量操作
  batchNodeOperation,
  
  // 导入导出
  exportNode,
  importNode,
  
  // 搜索分类
  searchNodes,
  getNodeCategories
}

export default nodesApi
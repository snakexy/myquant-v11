import { apiRequest, type ApiResponse } from '../index'

/**
 * 连接管理API模块
 * 提供节点间连接的创建、配置、监控、管理等功能
 */

// 连接状态枚举
export enum ConnectionStatus {
  ACTIVE = 'active',
  INACTIVE = 'inactive',
  ERROR = 'error',
  PENDING = 'pending',
  DISABLED = 'disabled'
}

// 连接类型枚举
export enum ConnectionType {
  DATA = 'data',
  CONTROL = 'control',
  EVENT = 'event',
  RESOURCE = 'resource'
}

// 连接方向枚举
export enum ConnectionDirection {
  UNIDIRECTIONAL = 'unidirectional',
  BIDIRECTIONAL = 'bidirectional'
}

// 连接接口
export interface Connection {
  id: string
  from: string
  to: string
  type: ConnectionType
  direction: ConnectionDirection
  status: ConnectionStatus
  label?: string
  description?: string
  position?: {
    startX: number
    startY: number
    endX: number
    endY: number
    controlPoints?: Array<{ x: number; y: number }>
  }
  styling: {
    color?: string
    width?: number
    style?: 'solid' | 'dashed' | 'dotted'
    arrowStyle?: 'none' | 'arrow' | 'double-arrow'
    animation?: 'none' | 'flow' | 'pulse'
  }
  dataFlow: {
    isActive: boolean
    bytesTransferred: number
    transferRate: number
    lastTransferTime?: string
    totalTransfers: number
  }
  validation: {
    isValid: boolean
    errors: Array<{
      type: 'type_mismatch' | 'circular_dependency' | 'missing_source' | 'missing_target'
      message: string
    }>
    warnings: Array<{
      type: 'performance' | 'best_practice'
      message: string
    }>
  }
  metadata: {
    createdAt: string
    updatedAt: string
    createdBy: string
    version: string
    tags: string[]
  }
  permissions: {
    canEdit: boolean
    canDelete: boolean
    canEnable: boolean
  }
}

// 连接模板接口
export interface ConnectionTemplate {
  id: string
  name: string
  description: string
  fromNodeType: string
  toNodeType: string
  type: ConnectionType
  direction: ConnectionDirection
  isRequired: boolean
  validation: {
    sourceOutputType?: string
    targetInputType?: string
    constraints?: Record<string, any>
  }
  styling: {
    defaultColor: string
    defaultWidth: number
    defaultStyle: string
    defaultArrowStyle: string
  }
  usageCount: number
}

// 连接执行日志接口
export interface ConnectionExecutionLog {
  id: string
  connectionId: string
  timestamp: string
  level: 'debug' | 'info' | 'warning' | 'error'
  message: string
  details?: {
    dataSize?: number
    transferTime?: number
    sourceNode?: string
    targetNode?: string
  }
}

// 连接性能指标接口
export interface ConnectionPerformanceMetrics {
  connectionId: string
  timestamp: string
  transferRate: number
  latency: number
  errorRate: number
  throughput: number
  dataVolume: number
}

// 创建连接API
export const createConnection = async (
  connection: Omit<Connection, 'id' | 'metadata' | 'dataFlow' | 'validation' | 'permissions'>
): Promise<ApiResponse<{ id: string }>> => {
  return apiRequest.post('/connections/create', connection)
}

// 获取连接列表API
export const getConnections = async (
  page = 1,
  pageSize = 10,
  filters?: {
    fromNode?: string
    toNode?: string
    type?: ConnectionType
    status?: ConnectionStatus
    tags?: string[]
  }
): Promise<ApiResponse<{
  connections: Connection[]
  total: number
  page: number
  pageSize: number
}>> => {
  const params = new URLSearchParams({
    page: page.toString(),
    pageSize: pageSize.toString()
  })
  
  if (filters) {
    if (filters.fromNode) params.append('fromNode', filters.fromNode)
    if (filters.toNode) params.append('toNode', filters.toNode)
    if (filters.type) params.append('type', filters.type)
    if (filters.status) params.append('status', filters.status)
    if (filters.tags) params.append('tags', filters.tags.join(','))
  }
  
  return apiRequest.get(`/connections/list?${params.toString()}`)
}

// 获取连接详情API
export const getConnection = async (
  id: string
): Promise<ApiResponse<Connection>> => {
  return apiRequest.get(`/connections/${id}`)
}

// 更新连接API
export const updateConnection = async (
  id: string,
  updates: Partial<Connection>
): Promise<ApiResponse<{ success: boolean }>> => {
  return apiRequest.put(`/connections/${id}`, updates)
}

// 删除连接API
export const deleteConnection = async (
  id: string
): Promise<ApiResponse<{ success: boolean }>> => {
  return apiRequest.delete(`/connections/${id}`)
}

// 启用连接API
export const enableConnection = async (
  id: string
): Promise<ApiResponse<{ success: boolean }>> => {
  return apiRequest.post(`/connections/${id}/enable`)
}

// 禁用连接API
export const disableConnection = async (
  id: string,
  reason?: string
): Promise<ApiResponse<{ success: boolean }>> => {
  return apiRequest.post(`/connections/${id}/disable`, { reason })
}

// 测试连接API
export const testConnection = async (
  id: string
): Promise<ApiResponse<{
  isValid: boolean
  canTransfer: boolean
  testResults: {
    latency: number
    bandwidth: number
    errorRate: number
  }
  errors: Array<{
    type: string
    message: string
  }>
}>> => {
  return apiRequest.post(`/connections/${id}/test`)
}

// 获取连接执行日志API
export const getConnectionLogs = async (
  id: string,
  options?: {
    level?: 'debug' | 'info' | 'warning' | 'error'
    startTime?: string
    endTime?: string
    page?: number
    pageSize?: number
  }
): Promise<ApiResponse<{
  logs: ConnectionExecutionLog[]
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
  
  return apiRequest.get(`/connections/${id}/logs?${params.toString()}`)
}

// 获取连接性能指标API
export const getConnectionMetrics = async (
  id: string,
  timeRange?: { start: string; end: string }
): Promise<ApiResponse<{
  metrics: ConnectionPerformanceMetrics[]
  summary: {
    averageTransferRate: number
    averageLatency: number
    averageThroughput: number
    peakTransferRate: number
    peakLatency: number
    totalDataTransferred: number
    errorRate: number
  }
}>> => {
  const params = new URLSearchParams()
  
  if (timeRange) {
    params.append('startTime', timeRange.start)
    params.append('endTime', timeRange.end)
  }
  
  return apiRequest.get(`/connections/${id}/metrics?${params.toString()}`)
}

// 获取连接模板列表API
export const getConnectionTemplates = async (
  fromNodeType?: string,
  toNodeType?: string
): Promise<ApiResponse<{
  templates: ConnectionTemplate[]
}>> => {
  const params = new URLSearchParams()
  
  if (fromNodeType) params.append('fromNodeType', fromNodeType)
  if (toNodeType) params.append('toNodeType', toNodeType)
  
  return apiRequest.get(`/connections/templates?${params.toString()}`)
}

// 获取连接模板详情API
export const getConnectionTemplate = async (
  id: string
): Promise<ApiResponse<ConnectionTemplate>> => {
  return apiRequest.get(`/connections/templates/${id}`)
}

// 从模板创建连接API
export const createConnectionFromTemplate = async (
  templateId: string,
  fromNode: string,
  toNode: string,
  customizations?: {
    label?: string
    description?: string
    styling?: Partial<Connection['styling']>
  }
): Promise<ApiResponse<{ connectionId: string }>> => {
  return apiRequest.post(`/connections/templates/${templateId}/create`, {
    fromNode,
    toNode,
    customizations
  })
}

// 验证连接API
export const validateConnection = async (
  connection: Partial<Connection>
): Promise<ApiResponse<{
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
}>> => {
  return apiRequest.post('/connections/validate', connection)
}

// 批量操作连接API
export const batchConnectionOperation = async (
  operation: 'delete' | 'enable' | 'disable' | 'test',
  connectionIds: string[]
): Promise<ApiResponse<{
  results: Array<{
    connectionId: string
    success: boolean
    error?: string
  }>
  summary: {
    total: number
    successful: number
    failed: number
  }
}>> => {
  return apiRequest.post('/connections/batch', {
    operation,
    connectionIds
  })
}

// 自动连接建议API
export const getConnectionSuggestions = async (
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
): Promise<ApiResponse<{
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
}>> => {
  return apiRequest.post(`/connections/suggestions/${nodeId}`, context)
}

// 应用连接建议API
export const applyConnectionSuggestion = async (
  nodeId: string,
  suggestionId: string
): Promise<ApiResponse<{ connectionId: string }>> => {
  return apiRequest.post(`/connections/apply-suggestion/${nodeId}`, { suggestionId })
}

// 导出连接配置API
export const exportConnection = async (
  id: string,
  format: 'json' | 'yaml' | 'xml' = 'json'
): Promise<void> => {
  return apiRequest.download(`/connections/${id}/export?format=${format}`, `connection-${id}.${format}`)
}

// 导入连接配置API
export const importConnection = async (
  file: File
): Promise<ApiResponse<{ connectionId: string }>> => {
  const formData = new FormData()
  formData.append('file', file)
  return apiRequest.upload('/connections/import', formData)
}

// 获取连接统计信息API
export const getConnectionStats = async (
  timeRange?: { start: string; end: string }
): Promise<ApiResponse<{
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
}>> => {
  const params = new URLSearchParams()
  
  if (timeRange) {
    params.append('startTime', timeRange.start)
    params.append('endTime', timeRange.end)
  }
  
  return apiRequest.get(`/connections/stats?${params.toString()}`)
}

// 连接API对象，便于统一管理
export const connectionsApi = {
  // 基本操作
  createConnection,
  getConnections,
  getConnection,
  updateConnection,
  deleteConnection,
  
  // 状态控制
  enableConnection,
  disableConnection,
  testConnection,
  
  // 监控日志
  getConnectionLogs,
  getConnectionMetrics,
  getConnectionStats,
  
  // 模板管理
  getConnectionTemplates,
  getConnectionTemplate,
  createConnectionFromTemplate,
  
  // 验证建议
  validateConnection,
  getConnectionSuggestions,
  applyConnectionSuggestion,
  
  // 批量操作
  batchConnectionOperation,
  
  // 导入导出
  exportConnection,
  importConnection
}

export default connectionsApi
/**
 * 节点工作流API服务
 * Node Workflow API Service
 */

import axios from 'axios'

// API基础配置
const API_BASE_URL = 'http://localhost:8000/api/v1/intelligent-node-system'

// 创建axios实例
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
apiClient.interceptors.request.use(
  (config) => {
    console.log(`API请求: ${config.method?.toUpperCase()} ${config.url}`)
    return config
  },
  (error) => {
    console.error('API请求错误:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
apiClient.interceptors.response.use(
  (response) => {
    console.log(`API响应: ${response.config.method?.toUpperCase()} ${response.config.url}`, response.data)
    return response.data
  },
  (error) => {
    console.error('API响应错误:', error)
    return Promise.reject(error)
  }
)

// ==================== 类型定义 ====================

export interface NaturalLanguageRequest {
  input: string
  context?: Record<string, any>
}

export interface NaturalLanguageResponse {
  intent: string
  entities: Record<string, any>
  confidence: number
  suggestions: string[]
}

export interface StrategyRecommendationRequest {
  market_condition: 'bullish' | 'bearish' | 'neutral'
  risk_level: 'low' | 'medium' | 'high'
  time_horizon: 'short' | 'medium' | 'long'
  constraints?: Record<string, any>
}

export interface StrategyRecommendationResponse {
  strategies: Array<{
    id: string
    name: string
    type: string
    description: string
    parameters: Record<string, any>
    expected_return: number
    risk: number
    sharpe_ratio: number
  }>
  confidence: number
  reasoning: string
  alternatives?: Array<{
    id: string
    name: string
    type: string
    description: string
  }>
}

export interface ParameterOptimizationRequest {
  strategy_type: string
  current_params: Record<string, any>
  market_data: Record<string, any>
}

export interface ParameterOptimizationResponse {
  optimized_params: Record<string, any>
  improvement_score: number
  optimization_details: {
    original_score: number
    optimized_score: number
    improvement_percentage: number
    optimization_method: string
    iterations: number
  }
}

export interface WorkflowCreateRequest {
  name: string
  description?: string
  nodes: Array<Record<string, any>>
  connections: Array<Record<string, any>>
  parameters?: Record<string, any>
}

export interface WorkflowResponse {
  id: string
  name: string
  description?: string
  status: string
  created_at: string
  updated_at: string
  nodes: Array<Record<string, any>>
  connections: Array<Record<string, any>>
}

export interface NodeCreateRequest {
  type: string
  name: string
  config: Record<string, any>
  position?: Record<string, number>
}

export interface NodeResponse {
  id: string
  type: string
  name: string
  config: Record<string, any>
  status: string
  created_at: string
  updated_at: string
}

export interface ConnectionCreateRequest {
  source_node_id: string
  target_node_id: string
  source_output_id?: string
  target_input_id?: string
  connection_type?: string
}

export interface ConnectionResponse {
  id: string
  source_node_id: string
  target_node_id: string
  source_output_id?: string
  target_input_id?: string
  connection_type: string
  status: string
  created_at: string
}

export interface SystemStatus {
  status: string
  version: string
  uptime: string
  active_workflows: number
  active_nodes: number
  active_connections: number
  system_resources: {
    cpu_usage: number
    memory_usage: number
    disk_usage: number
  }
  services: {
    intelligent_recommendation: string
    workflow_manager: string
    node_manager: string
    connection_manager: string
  }
}

// ==================== API服务类 ====================

class NodeWorkflowService {
  // ==================== 智能推荐API ====================

  /**
   * 自然语言解析
   */
  async parseNaturalLanguage(request: NaturalLanguageRequest): Promise<NaturalLanguageResponse> {
    try {
      return await apiClient.post('/parse-natural-language', request)
    } catch (error) {
      console.error('自然语言解析失败:', error)
      throw error
    }
  }

  /**
   * 获取策略推荐
   */
  async getStrategyRecommendation(request: StrategyRecommendationRequest): Promise<StrategyRecommendationResponse> {
    try {
      return await apiClient.post('/strategy-recommendation', request)
    } catch (error) {
      console.error('策略推荐失败:', error)
      throw error
    }
  }

  /**
   * 参数优化
   */
  async optimizeParameters(request: ParameterOptimizationRequest): Promise<ParameterOptimizationResponse> {
    try {
      return await apiClient.post('/parameter-optimization', request)
    } catch (error) {
      console.error('参数优化失败:', error)
      throw error
    }
  }

  // ==================== 工作流管理API ====================

  /**
   * 获取工作流列表
   */
  async getWorkflows(
    page: number = 1,
    pageSize: number = 10,
    status?: string,
    category?: string
  ): Promise<WorkflowResponse[]> {
    try {
      const params: any = { page, page_size: pageSize }
      if (status) params.status = status
      if (category) params.category = category
      
      return await apiClient.get('/workflows', { params })
    } catch (error) {
      console.error('获取工作流列表失败:', error)
      throw error
    }
  }

  /**
   * 创建工作流
   */
  async createWorkflow(request: WorkflowCreateRequest): Promise<WorkflowResponse> {
    try {
      return await apiClient.post('/workflows', request)
    } catch (error) {
      console.error('创建工作流失败:', error)
      throw error
    }
  }

  /**
   * 执行工作流
   */
  async executeWorkflow(workflowId: string): Promise<{ message: string; status: string }> {
    try {
      return await apiClient.post(`/workflows/${workflowId}/execute`)
    } catch (error) {
      console.error('执行工作流失败:', error)
      throw error
    }
  }

  // ==================== 节点管理API ====================

  /**
   * 获取节点列表
   */
  async getNodes(
    page: number = 1,
    pageSize: number = 10,
    type?: string,
    status?: string
  ): Promise<NodeResponse[]> {
    try {
      const params: any = { page, page_size: pageSize }
      if (type) params.type = type
      if (status) params.status = status
      
      return await apiClient.get('/nodes', { params })
    } catch (error) {
      console.error('获取节点列表失败:', error)
      throw error
    }
  }

  /**
   * 创建节点
   */
  async createNode(request: NodeCreateRequest): Promise<NodeResponse> {
    try {
      return await apiClient.post('/nodes', request)
    } catch (error) {
      console.error('创建节点失败:', error)
      throw error
    }
  }

  // ==================== 连接管理API ====================

  /**
   * 获取连接列表
   */
  async getConnections(
    page: number = 1,
    pageSize: number = 10,
    type?: string,
    status?: string
  ): Promise<ConnectionResponse[]> {
    try {
      const params: any = { page, page_size: pageSize }
      if (type) params.type = type
      if (status) params.status = status
      
      return await apiClient.get('/connections', { params })
    } catch (error) {
      console.error('获取连接列表失败:', error)
      throw error
    }
  }

  /**
   * 创建连接
   */
  async createConnection(request: ConnectionCreateRequest): Promise<ConnectionResponse> {
    try {
      return await apiClient.post('/connections', request)
    } catch (error) {
      console.error('创建连接失败:', error)
      throw error
    }
  }

  // ==================== 系统监控API ====================

  /**
   * 获取系统状态
   */
  async getSystemStatus(): Promise<SystemStatus> {
    try {
      return await apiClient.get('/system/status')
    } catch (error) {
      console.error('获取系统状态失败:', error)
      throw error
    }
  }

  /**
   * 健康检查
   */
  async healthCheck(): Promise<{ status: string; timestamp: string }> {
    try {
      return await apiClient.get('/system/health')
    } catch (error) {
      console.error('健康检查失败:', error)
      throw error
    }
  }
}

// 导出单例实例
export const nodeWorkflowService = new NodeWorkflowService()

// 导出默认实例
export default nodeWorkflowService
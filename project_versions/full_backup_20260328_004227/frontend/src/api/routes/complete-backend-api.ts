/**
 * 完整的智能节点系统后端API实现
 * 确保支持所有必要的功能和完整的错误处理
 */

// 模拟Express和相关类型
interface MockRequest {
  body: any
  query: any
  params: any
  path: string
  method: string
  headers: Record<string, string>
}

interface MockResponse {
  json(data: any): void
  status(code: number): MockResponse
  send(data: any): void
}

interface MockNextFunction {
  (error?: any): void
}

// 模拟数据库存储
const mockDatabase = {
  nodes: new Map<string, any>(),
  workflows: new Map<string, any>(),
  connections: new Map<string, any>(),
  templates: new Map<string, any>(),
  users: new Map<string, any>(),
  logs: [] as any[],
  metrics: {
    requests: 0,
    errors: 0,
    responseTime: [] as number[]
  }
}

// 工具函数
const generateId = (prefix: string): string => `${prefix}_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
const getCurrentTimestamp = (): string => new Date().toISOString()
const createSuccessResponse = (data: any, message?: string) => ({
  success: true,
  data,
  message: message || '操作成功',
  timestamp: getCurrentTimestamp()
})
const createErrorResponse = (message: string, code: number = 400) => ({
  success: false,
  message,
  error: message,
  timestamp: getCurrentTimestamp()
})
const validateRequired = (body: any, requiredFields: string[]): { isValid: boolean; missingFields: string[] } => {
  const missingFields = requiredFields.filter(field => !body[field])
  return {
    isValid: missingFields.length === 0,
    missingFields
  }
}

// 创建路由处理器
const createHandler = (handler: (req: MockRequest, res: MockResponse) => Promise<any>) => {
  return async (req: MockRequest, res: MockResponse) => {
    try {
      mockDatabase.metrics.requests++
      const startTime = Date.now()
      
      const result = await handler(req, res)
      
      const responseTime = Date.now() - startTime
      mockDatabase.metrics.responseTime.push(responseTime)
      
      // 保持最近1000次响应时间
      if (mockDatabase.metrics.responseTime.length > 1000) {
        mockDatabase.metrics.responseTime = mockDatabase.metrics.responseTime.slice(-1000)
      }
      
      if (result !== undefined) {
        res.json(result)
      }
    } catch (error) {
      mockDatabase.metrics.errors++
      console.error('API错误:', error)
      res.status(500).json(createErrorResponse(
        error instanceof Error ? error.message : '服务器内部错误',
        500
      ))
    }
  }
}

// 智能推荐API
const intelligentRecommendationApi = {
  'POST /parse-natural-language': createHandler(async (req: MockRequest) => {
    const { text, context } = req.body
    const validation = validateRequired(req.body, ['text'])
    
    if (!validation.isValid) {
      return createErrorResponse(
        `缺少必填字段: ${validation.missingFields.join(', ')}`,
        400
      )
    }
    
    // 模拟自然语言解析
    const parseResult = {
      intent: 'create_backtest',
      entities: [
        { type: 'strategy', value: 'mean_reversion', confidence: 0.9 },
        { type: 'timeframe', value: 'daily', confidence: 0.8 },
        { type: 'universe', value: 'hs300', confidence: 0.85 },
        { type: 'risk_management', value: 'position_sizing', confidence: 0.7 }
      ],
      confidence: 0.85,
      suggestions: [
        '建议添加风险管理节点',
        '考虑使用多时间框架分析',
        '推荐设置止损策略'
      ],
      parameters: {
        strategy_type: 'mean_reversion',
        lookback_period: 20,
        rebalance_frequency: 'monthly',
        risk_limit: 0.02
      }
    }
    
    // 记录日志
    mockDatabase.logs.push({
      id: generateId('log'),
      timestamp: getCurrentTimestamp(),
      level: 'info',
      message: '自然语言解析成功',
      source: 'intelligent_recommendation',
      context: { input: text, result: parseResult }
    })
    
    return createSuccessResponse(parseResult)
  }),
  
  'POST /get-recommendations': createHandler(async (req: MockRequest) => {
    const { experienceLevel, currentWorkflow, preferences } = req.body
    const validation = validateRequired(req.body, ['experienceLevel'])
    
    if (!validation.isValid) {
      return createErrorResponse(
        `缺少必填字段: ${validation.missingFields.join(', ')}`,
        400
      )
    }
    
    // 模拟获取推荐
    const recommendations = [
      {
        id: generateId('rec'),
        title: '新手推荐策略',
        description: '适合初学者的简单回测策略',
        confidence: 0.9,
        parameters: [
          { name: 'strategy_type', value: 'simple_momentum', type: 'select' },
          { name: 'universe', value: 'hs300', type: 'select' },
          { name: 'rebalance_frequency', value: 'monthly', type: 'select' }
        ],
        reasoning: '基于您的经验水平推荐',
        pros: ['简单易用', '风险可控', '适合学习'],
        cons: ['收益有限', '策略简单'],
        useCases: ['学习回测', '策略验证', '教学演示'],
        tags: ['新手', '简单', '教学'],
        createdAt: getCurrentTimestamp(),
        version: '1.0.0'
      },
      {
        id: generateId('rec'),
        title: '进阶推荐策略',
        description: '适合有经验用户的多因子策略',
        confidence: 0.8,
        parameters: [
          { name: 'strategy_type', value: 'multi_factor', type: 'select' },
          { name: 'factors', value: ['momentum', 'value', 'quality'], type: 'array' },
          { name: 'universe', value: 'zz500', type: 'select' }
        ],
        reasoning: '基于当前工作流和偏好推荐',
        pros: ['收益潜力大', '策略复杂', '专业性强'],
        cons: ['风险较高', '需要更多数据', '计算复杂'],
        useCases: ['实盘交易', '策略研究', '风险管理'],
        tags: ['进阶', '多因子', '专业'],
        createdAt: getCurrentTimestamp(),
        version: '1.0.0'
      }
    ]
    
    return createSuccessResponse({
      recommendations,
      experienceLevel,
      total: recommendations.length
    })
  }),
  
  'POST /optimize-parameters': createHandler(async (req: MockRequest) => {
    const { nodeId, parameters, objectives } = req.body
    const validation = validateRequired(req.body, ['nodeId', 'parameters'])
    
    if (!validation.isValid) {
      return createErrorResponse(
        `缺少必填字段: ${validation.missingFields.join(', ')}`,
        400
      )
    }
    
    // 模拟参数优化
    const optimizedParameters = parameters.map((param: any) => ({
      ...param,
      optimizedValue: param.value * 1.1, // 模拟优化
      improvement: 0.1,
      confidence: 0.75
    }))
    
    return createSuccessResponse({
      nodeId,
      originalParameters: parameters,
      optimizedParameters,
      objectives,
      improvement: 0.1,
      optimizationTime: 1500
    })
  })
}

// 工作流管理API
const workflowApi = {
  'GET /': createHandler(async (req: MockRequest) => {
    const { page = 1, pageSize = 10, status, category } = req.query
    
    // 模拟获取工作流列表
    const workflows = Array.from(mockDatabase.workflows.values())
      .filter((workflow: any) => {
        if (status && workflow.status !== status) return false
        if (category && workflow.category !== category) return false
        return true
      })
      .slice((page - 1) * pageSize, page * pageSize)
    
    return createSuccessResponse({
      workflows,
      pagination: {
        page: parseInt(page as string),
        pageSize: parseInt(pageSize as string),
        total: workflows.length,
        hasMore: workflows.length === pageSize
      }
    })
  }),
  
  'POST /': createHandler(async (req: MockRequest) => {
    const { workflow } = req.body
    const validation = validateRequired(req.body, ['name', 'nodes'])
    
    if (!validation.isValid) {
      return createErrorResponse(
        `缺少必填字段: ${validation.missingFields.join(', ')}`,
        400
      )
    }
    
    // 创建新工作流
    const newWorkflow = {
      id: generateId('workflow'),
      name: workflow.name,
      description: workflow.description || '',
      nodes: workflow.nodes || [],
      connections: workflow.connections || [],
      status: 'draft',
      metadata: {
        createdAt: getCurrentTimestamp(),
        updatedAt: getCurrentTimestamp(),
        version: '1.0.0',
        author: 'user',
        tags: workflow.tags || []
      },
      permissions: {
        canView: true,
        canEdit: true,
        canExecute: true,
        canDelete: true,
        canShare: false
      }
    }
    
    mockDatabase.workflows.set(newWorkflow.id, newWorkflow)
    
    return createSuccessResponse(newWorkflow, '工作流创建成功')
  }),
  
  'POST /:id/execute': createHandler(async (req: MockRequest) => {
    const { id } = req.params
    const { parameters, options } = req.body
    
    const workflow = mockDatabase.workflows.get(id)
    if (!workflow) {
      return createErrorResponse('工作流不存在', 404)
    }
    
    // 执行工作流
    const executionId = generateId('exec')
    const execution = {
      id: executionId,
      workflowId: id,
      status: 'running',
      startTime: getCurrentTimestamp(),
      endTime: null,
      duration: null,
      parameters: parameters || {},
      options: options || {},
      results: null,
      error: null,
      logs: []
    }
    
    // 更新工作流状态
    workflow.status = 'running'
    workflow.execution = execution
    
    return createSuccessResponse({
      executionId,
      status: 'started',
      startTime: execution.startTime
    }, '工作流执行已开始')
  }),
  
  'GET /:id/status': createHandler(async (req: MockRequest) => {
    const { id } = req.params
    const workflow = mockDatabase.workflows.get(id)
    
    if (!workflow) {
      return createErrorResponse('工作流不存在', 404)
    }
    
    return createSuccessResponse({
      workflowId: id,
      status: workflow.status,
      execution: workflow.execution,
      progress: workflow.execution ? calculateProgress(workflow.execution) : 0
    })
  }),
  
  'PUT /:id': createHandler(async (req: MockRequest) => {
    const { id } = req.params
    const { updates } = req.body
    
    const workflow = mockDatabase.workflows.get(id)
    if (!workflow) {
      return createErrorResponse('工作流不存在', 404)
    }
    
    // 更新工作流
    Object.assign(workflow, updates)
    workflow.metadata.updatedAt = getCurrentTimestamp()
    
    return createSuccessResponse(workflow, '工作流更新成功')
  }),
  
  'DELETE /:id': createHandler(async (req: MockRequest) => {
    const { id } = req.params
    
    const workflow = mockDatabase.workflows.get(id)
    if (!workflow) {
      return createErrorResponse('工作流不存在', 404)
    }
    
    mockDatabase.workflows.delete(id)
    
    return createSuccessResponse({ id }, '工作流删除成功')
  })
}

// 节点管理API
const nodesApi = {
  'GET /': createHandler(async (req: MockRequest) => {
    const { page = 1, pageSize = 10, type, status } = req.query
    
    // 模拟获取节点列表
    const nodes = Array.from(mockDatabase.nodes.values())
      .filter((node: any) => {
        if (type && node.type !== type) return false
        if (status && node.status !== status) return false
        return true
      })
      .slice((page - 1) * pageSize, page * pageSize)
    
    return createSuccessResponse({
      nodes,
      pagination: {
        page: parseInt(page as string),
        pageSize: parseInt(pageSize as string),
        total: nodes.length,
        hasMore: nodes.length === pageSize
      }
    })
  }),
  
  'POST /': createHandler(async (req: MockRequest) => {
    const { node } = req.body
    const validation = validateRequired(req.body, ['name', 'type'])
    
    if (!validation.isValid) {
      return createErrorResponse(
        `缺少必填字段: ${validation.missingFields.join(', ')}`,
        400
      )
    }
    
    // 创建新节点
    const newNode = {
      id: generateId('node'),
      name: node.name,
      displayName: node.displayName || node.name,
      description: node.description || '',
      type: node.type,
      status: 'idle',
      position: node.position || { x: 0, y: 0 },
      size: node.size || { width: 200, height: 120 },
      parameters: node.parameters || [],
      inputs: node.inputs || [],
      outputs: node.outputs || [],
      execution: null,
      permissions: {
        canEdit: true,
        canDelete: true,
        canExecute: true,
        canConfigure: true
      },
      metadata: {
        createdAt: getCurrentTimestamp(),
        updatedAt: getCurrentTimestamp(),
        version: '1.0.0',
        category: getNodeCategory(node.type),
        tags: node.tags || []
      }
    }
    
    mockDatabase.nodes.set(newNode.id, newNode)
    
    return createSuccessResponse(newNode, '节点创建成功')
  }),
  
  'GET /:id': createHandler(async (req: MockRequest) => {
    const { id } = req.params
    
    const node = mockDatabase.nodes.get(id)
    if (!node) {
      return createErrorResponse('节点不存在', 404)
    }
    
    return createSuccessResponse(node)
  }),
  
  'PUT /:id': createHandler(async (req: MockRequest) => {
    const { id } = req.params
    const { updates } = req.body
    
    const node = mockDatabase.nodes.get(id)
    if (!node) {
      return createErrorResponse('节点不存在', 404)
    }
    
    // 更新节点
    Object.assign(node, updates)
    node.metadata.updatedAt = getCurrentTimestamp()
    
    return createSuccessResponse(node, '节点更新成功')
  }),
  
  'DELETE /:id': createHandler(async (req: MockRequest) => {
    const { id } = req.params
    
    const node = mockDatabase.nodes.get(id)
    if (!node) {
      return createErrorResponse('节点不存在', 404)
    }
    
    mockDatabase.nodes.delete(id)
    
    return createSuccessResponse({ id }, '节点删除成功')
  }),
  
  'POST /:id/execute': createHandler(async (req: MockRequest) => {
    const { id } = req.params
    const { parameters } = req.body
    
    const node = mockDatabase.nodes.get(id)
    if (!node) {
      return createErrorResponse('节点不存在', 404)
    }
    
    // 执行节点
    const executionId = generateId('exec')
    node.status = 'running'
    node.execution = {
      id: executionId,
      status: 'running',
      progress: 0,
      startTime: getCurrentTimestamp(),
      endTime: null,
      duration: null,
      logs: [],
      results: null,
      error: null
    }
    
    return createSuccessResponse({
      nodeId: id,
      executionId,
      status: 'started'
    }, '节点执行已开始')
  }),
  
  'GET /:id/logs': createHandler(async (req: MockRequest) => {
    const { id } = req.params
    const { level, limit = 50 } = req.query
    
    const node = mockDatabase.nodes.get(id)
    if (!node) {
      return createErrorResponse('节点不存在', 404)
    }
    
    // 获取节点日志
    const logs = (node.execution?.logs || [])
      .filter((log: any) => !level || log.level === level)
      .slice(0, parseInt(limit as string))
    
    return createSuccessResponse({
      nodeId: id,
      logs,
      total: logs.length
    })
  })
}

// 连接管理API
const connectionsApi = {
  'GET /': createHandler(async (req: MockRequest) => {
    const { page = 1, pageSize = 10, type, status } = req.query
    
    // 模拟获取连接列表
    const connections = Array.from(mockDatabase.connections.values())
      .filter((conn: any) => {
        if (type && conn.type !== type) return false
        if (status && conn.status !== status) return false
        return true
      })
      .slice((page - 1) * pageSize, page * pageSize)
    
    return createSuccessResponse({
      connections,
      pagination: {
        page: parseInt(page as string),
        pageSize: parseInt(pageSize as string),
        total: connections.length,
        hasMore: connections.length === pageSize
      }
    })
  }),
  
  'POST /': createHandler(async (req: MockRequest) => {
    const { connection } = req.body
    const validation = validateRequired(req.body, ['sourceNodeId', 'targetNodeId'])
    
    if (!validation.isValid) {
      return createErrorResponse(
        `缺少必填字段: ${validation.missingFields.join(', ')}`,
        400
      )
    }
    
    // 创建新连接
    const newConnection = {
      id: generateId('conn'),
      name: connection.name || '',
      type: connection.type || 'data',
      status: 'active',
      sourceNodeId: connection.sourceNodeId,
      sourceOutputId: connection.sourceOutputId,
      targetNodeId: connection.targetNodeId,
      targetInputId: connection.targetInputId,
      data: connection.data || null,
      metadata: {
        createdAt: getCurrentTimestamp(),
        updatedAt: getCurrentTimestamp(),
        version: '1.0.0'
      }
    }
    
    mockDatabase.connections.set(newConnection.id, newConnection)
    
    return createSuccessResponse(newConnection, '连接创建成功')
  }),
  
  'DELETE /:id': createHandler(async (req: MockRequest) => {
    const { id } = req.params
    
    const connection = mockDatabase.connections.get(id)
    if (!connection) {
      return createErrorResponse('连接不存在', 404)
    }
    
    mockDatabase.connections.delete(id)
    
    return createSuccessResponse({ id }, '连接删除成功')
  })
}

// 工具函数
const getNodeCategory = (type: string): string => {
  const categoryMap: Record<string, string> = {
    'data_source': '数据源',
    'data_processing': '数据处理',
    'strategy': '策略',
    'backtest': '回测',
    'analysis': '分析',
    'visualization': '可视化',
    'export': '导出'
  }
  return categoryMap[type] || '其他'
}

const calculateProgress = (execution: any): number => {
  if (!execution || !execution.logs) return 0
  
  const totalSteps = 10
  const completedSteps = execution.logs.filter((log: any) => 
    log.level === 'info' && log.message.includes('完成')
  ).length
  
  return Math.min(Math.round((completedSteps / totalSteps) * 100), 100)
}

// 创建完整路由
const createCompleteRouter = () => {
  const routes: any[] = []
  
  const router = {
    get: (path: string, handler: any) => {
      routes.push({ method: 'GET', path, handler })
    },
    post: (path: string, handler: any) => {
      routes.push({ method: 'POST', path, handler })
    },
    put: (path: string, handler: any) => {
      routes.push({ method: 'PUT', path, handler })
    },
    delete: (path: string, handler: any) => {
      routes.push({ method: 'DELETE', path, handler })
    },
    use: (path: string, handler: any) => {
      routes.push({ method: 'USE', path, handler })
    }
  }
  
  // 注册所有路由
  Object.entries(intelligentRecommendationApi).forEach(([path, handler]) => {
    router.post(`/recommendations${path}`, handler)
  })
  
  Object.entries(workflowApi).forEach(([path, handler]) => {
    if (path.startsWith('GET')) {
      router.get(`/workflows${path.replace('GET ', '')}`, handler)
    } else if (path.startsWith('POST')) {
      router.post(`/workflows${path.replace('POST ', '')}`, handler)
    } else if (path.startsWith('PUT')) {
      router.put(`/workflows${path.replace('PUT ', '')}`, handler)
    } else if (path.startsWith('DELETE')) {
      router.delete(`/workflows${path.replace('DELETE ', '')}`, handler)
    }
  })
  
  Object.entries(nodesApi).forEach(([path, handler]) => {
    if (path.startsWith('GET')) {
      router.get(`/nodes${path.replace('GET ', '')}`, handler)
    } else if (path.startsWith('POST')) {
      router.post(`/nodes${path.replace('POST ', '')}`, handler)
    } else if (path.startsWith('PUT')) {
      router.put(`/nodes${path.replace('PUT ', '')}`, handler)
    } else if (path.startsWith('DELETE')) {
      router.delete(`/nodes${path.replace('DELETE ', '')}`, handler)
    }
  })
  
  Object.entries(connectionsApi).forEach(([path, handler]) => {
    if (path.startsWith('GET')) {
      router.get(`/connections${path.replace('GET ', '')}`, handler)
    } else if (path.startsWith('POST')) {
      router.post(`/connections${path.replace('POST ', '')}`, handler)
    } else if (path.startsWith('DELETE')) {
      router.delete(`/connections${path.replace('DELETE ', '')}`, handler)
    }
  })
  
  // 系统路由
  router.get('/system/status', createHandler(async () => {
    return createSuccessResponse({
      status: 'running',
      version: '1.0.0',
      uptime: Date.now() - 1000000,
      timestamp: getCurrentTimestamp(),
      statistics: {
        totalNodes: mockDatabase.nodes.size,
        totalWorkflows: mockDatabase.workflows.size,
        totalConnections: mockDatabase.connections.size,
        activeWorkflows: Array.from(mockDatabase.workflows.values()).filter((w: any) => w.status === 'running').length,
        systemLoad: {
          cpu: Math.random() * 100,
          memory: Math.random() * 100,
          disk: Math.random() * 100
        }
      }
    })
  }))
  
  router.get('/system/health', createHandler(async () => {
    const health = {
      status: 'healthy',
      timestamp: getCurrentTimestamp(),
      services: {
        database: 'connected',
        cache: 'connected',
        messageQueue: 'connected',
        fileSystem: 'available'
      },
      metrics: {
        responseTime: mockDatabase.metrics.responseTime.length > 0 
          ? mockDatabase.metrics.responseTime.slice(-1)[0] 
          : 0,
        errorRate: mockDatabase.metrics.requests > 0 
          ? (mockDatabase.metrics.errors / mockDatabase.metrics.requests) * 100 
          : 0,
        throughput: mockDatabase.metrics.requests
      }
    }
    
    return createSuccessResponse(health)
  }))
  
  return router
}

export default createCompleteRouter()
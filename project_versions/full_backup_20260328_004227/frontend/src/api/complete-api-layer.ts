/**
 * 完整API层实现
 * 连接前端API模块与后端API路由，提供统一的API接口
 */

// 导入所有API模块
import { intelligentRecommendationApi } from './modules/intelligent-recommendation'
import { workflowApi } from './modules/workflow'
import { nodesApi } from './modules/nodes'
import { connectionsApi } from './modules/connections'
import * as dataApi from './modules/data'
import { strategyApi } from './modules/strategy'
import { backtestApi } from './modules/backtest'
import * as aiApi from './modules/ai'

// 导入API基础配置
import { apiRequest } from './index'

/**
 * 完整API层
 * 整合所有API模块，提供统一的接口
 */
export const completeApiLayer = {
  // 智能推荐API
  intelligentRecommendation: {
    // 自然语言解析
    parseNaturalLanguage: async (input: string) => {
      return apiRequest.post('/intelligent-recommendation/parse-natural-language', { input })
    },
    
    // 获取策略推荐
    getStrategyRecommendation: async (request: any) => {
      return apiRequest.post('/intelligent-recommendation/strategy-recommendation', request)
    },
    
    // 参数优化
    optimizeParameters: async (strategyType: string, currentParams: any, marketData: any) => {
      return apiRequest.post('/intelligent-recommendation/parameter-optimization', {
        strategyType,
        currentParams,
        marketData
      })
    },
    
    // 验证工作流
    validateWorkflow: async (workflow: any) => {
      return apiRequest.post('/intelligent-recommendation/validate-workflow', workflow)
    },
    
    // 应用推荐
    applyRecommendation: async (workflowId: string, customizations: any) => {
      return apiRequest.post('/intelligent-recommendation/apply-recommendation', {
        workflowId,
        customizations
      })
    },
    
    // 获取推荐历史
    getRecommendationHistory: async (page: number = 1, pageSize: number = 10) => {
      return apiRequest.get(`/intelligent-recommendation/history?page=${page}&pageSize=${pageSize}`)
    },
    
    // 保存推荐配置
    saveRecommendation: async (workflow: any, name: string, description?: string) => {
      return apiRequest.post('/intelligent-recommendation/save', {
        workflow,
        name,
        description
      })
    },
    
    // 加载推荐配置
    loadRecommendation: async (id: string) => {
      return apiRequest.get(`/intelligent-recommendation/load/${id}`)
    },
    
    // 删除推荐配置
    deleteRecommendation: async (id: string) => {
      return apiRequest.delete(`/intelligent-recommendation/delete/${id}`)
    },
    
    // 获取推荐统计
    getRecommendationStats: async () => {
      return apiRequest.get('/intelligent-recommendation/stats')
    },
    
    // 获取市场数据用于优化
    getMarketDataForOptimization: async (symbols: string[], dateRange: any) => {
      return apiRequest.post('/intelligent-recommendation/market-data', {
        symbols,
        dateRange
      })
    },
    
    // 批量参数优化
    batchParameterOptimization: async (requests: any[]) => {
      return apiRequest.post('/intelligent-recommendation/batch-optimization', { requests })
    },
    
    // 获取推荐模板
    getRecommendationTemplates: async (strategyType?: string) => {
      const url = strategyType 
        ? `/intelligent-recommendation/templates?strategyType=${strategyType}`
        : '/intelligent-recommendation/templates'
      return apiRequest.get(url)
    },
    
    // 应用推荐模板
    applyRecommendationTemplate: async (templateId: string, customizations?: any) => {
      return apiRequest.post(`/intelligent-recommendation/apply-template/${templateId}`, {
        customizations
      })
    },
    
    // 评价推荐结果
    rateRecommendation: async (workflowId: string, rating: number, feedback?: string) => {
      return apiRequest.post('/intelligent-recommendation/rate', {
        workflowId,
        rating,
        feedback
      })
    },
    
    // 获取推荐反馈
    getRecommendationFeedback: async (workflowId: string) => {
      return apiRequest.get(`/intelligent-recommendation/feedback/${workflowId}`)
    },
    
    // 导出推荐配置
    exportRecommendation: async (workflowId: string, format: string = 'json') => {
      return apiRequest.download(`/intelligent-recommendation/export/${workflowId}?format=${format}`, `recommendation-${workflowId}.${format}`)
    },
    
    // 导入推荐配置
    importRecommendation: async (file: File) => {
      const formData = new FormData()
      formData.append('file', file)
      return apiRequest.upload('/intelligent-recommendation/import', formData)
    },
    
    // 获取推荐帮助文档
    getRecommendationHelp: async (topic?: string) => {
      const url = topic 
        ? `/intelligent-recommendation/help?topic=${topic}`
        : '/intelligent-recommendation/help'
      return apiRequest.get(url)
    }
  },

  // 工作流管理API
  workflow: {
    // 获取工作流列表
    getWorkflows: async (page: number = 1, pageSize: number = 10, status?: string, category?: string) => {
      const params = new URLSearchParams({
        page: page.toString(),
        pageSize: pageSize.toString()
      })
      if (status) params.append('status', status)
      if (category) params.append('category', category)
      
      return apiRequest.get(`/workflows?${params.toString()}`)
    },
    
    // 创建工作流
    createWorkflow: async (workflow: any) => {
      return apiRequest.post('/workflows', workflow)
    },
    
    // 执行工作流
    executeWorkflow: async (id: string, parameters?: any, options?: any) => {
      return apiRequest.post(`/workflows/${id}/execute`, {
        parameters,
        options
      })
    },
    
    // 获取执行状态
    getExecutionStatus: async (id: string) => {
      return apiRequest.get(`/workflows/${id}/status`)
    },
    
    // 更新工作流
    updateWorkflow: async (id: string, updates: any) => {
      return apiRequest.put(`/workflows/${id}`, updates)
    },
    
    // 删除工作流
    deleteWorkflow: async (id: string) => {
      return apiRequest.delete(`/workflows/${id}`)
    },
    
    // 复制工作流
    duplicateWorkflow: async (id: string, name?: string) => {
      return apiRequest.post(`/workflows/${id}/duplicate`, { name })
    },
    
    // 获取工作流详情
    getWorkflowDetails: async (id: string) => {
      return apiRequest.get(`/workflows/${id}`)
    },
    
    // 获取工作流执行历史
    getExecutionHistory: async (id: string, page: number = 1, pageSize: number = 10) => {
      return apiRequest.get(`/workflows/${id}/executions?page=${page}&pageSize=${pageSize}`)
    },
    
    // 停止工作流执行
    stopExecution: async (workflowId: string, executionId: string) => {
      return apiRequest.post(`/workflows/${workflowId}/stop`, { executionId })
    },
    
    // 暂停工作流执行
    pauseExecution: async (workflowId: string, executionId: string) => {
      return apiRequest.post(`/workflows/${workflowId}/pause`, { executionId })
    },
    
    // 恢复工作流执行
    resumeExecution: async (workflowId: string, executionId: string) => {
      return apiRequest.post(`/workflows/${workflowId}/resume`, { executionId })
    }
  },

  // 节点管理API
  nodes: {
    // 获取节点列表
    getNodes: async (page: number = 1, pageSize: number = 10, type?: string, status?: string) => {
      const params = new URLSearchParams({
        page: page.toString(),
        pageSize: pageSize.toString()
      })
      if (type) params.append('type', type)
      if (status) params.append('status', status)
      
      return apiRequest.get(`/nodes?${params.toString()}`)
    },
    
    // 创建节点
    createNode: async (node: any) => {
      return apiRequest.post('/nodes', node)
    },
    
    // 获取节点详情
    getNodeDetails: async (id: string) => {
      return apiRequest.get(`/nodes/${id}`)
    },
    
    // 更新节点
    updateNode: async (id: string, updates: any) => {
      return apiRequest.put(`/nodes/${id}`, updates)
    },
    
    // 删除节点
    deleteNode: async (id: string) => {
      return apiRequest.delete(`/nodes/${id}`)
    },
    
    // 执行节点
    executeNode: async (id: string, parameters?: any) => {
      return apiRequest.post(`/nodes/${id}/execute`, { parameters })
    },
    
    // 获取节点日志
    getNodeLogs: async (id: string, level?: string, limit: number = 50) => {
      const params = new URLSearchParams({
        limit: limit.toString()
      })
      if (level) params.append('level', level)
      
      return apiRequest.get(`/nodes/${id}/logs?${params.toString()}`)
    },
    
    // 获取节点类型
    getNodeTypes: async () => {
      return apiRequest.get('/nodes/types')
    },
    
    // 获取节点模板
    getNodeTemplates: async (type?: string) => {
      const url = type 
        ? `/nodes/templates?type=${type}`
        : '/nodes/templates'
      return apiRequest.get(url)
    },
    
    // 从模板创建节点
    createNodeFromTemplate: async (templateId: string, customizations?: any) => {
      return apiRequest.post(`/nodes/create-from-template/${templateId}`, {
        customizations
      })
    },
    
    // 验证节点配置
    validateNodeConfig: async (nodeType: string, config: any) => {
      return apiRequest.post('/nodes/validate-config', {
        nodeType,
        config
      })
    },
    
    // 获取节点依赖关系
    getNodeDependencies: async (id: string) => {
      return apiRequest.get(`/nodes/${id}/dependencies`)
    },
    
    // 批量操作节点
    batchOperationNodes: async (operation: string, nodeIds: string[], data?: any) => {
      return apiRequest.post('/nodes/batch-operation', {
        operation,
        nodeIds,
        data
      })
    }
  },

  // 连接管理API
  connections: {
    // 获取连接列表
    getConnections: async (page: number = 1, pageSize: number = 10, type?: string, status?: string) => {
      const params = new URLSearchParams({
        page: page.toString(),
        pageSize: pageSize.toString()
      })
      if (type) params.append('type', type)
      if (status) params.append('status', status)
      
      return apiRequest.get(`/connections?${params.toString()}`)
    },
    
    // 创建连接
    createConnection: async (connection: any) => {
      return apiRequest.post('/connections', connection)
    },
    
    // 更新连接
    updateConnection: async (id: string, updates: any) => {
      return apiRequest.put(`/connections/${id}`, updates)
    },
    
    // 删除连接
    deleteConnection: async (id: string) => {
      return apiRequest.delete(`/connections/${id}`)
    },
    
    // 验证连接
    validateConnection: async (sourceNodeId: string, targetNodeId: string, sourceOutputId?: string, targetInputId?: string) => {
      return apiRequest.post('/connections/validate', {
        sourceNodeId,
        targetNodeId,
        sourceOutputId,
        targetInputId
      })
    },
    
    // 获取连接类型
    getConnectionTypes: async () => {
      return apiRequest.get('/connections/types')
    },
    
    // 批量操作连接
    batchOperationConnections: async (operation: string, connectionIds: string[], data?: any) => {
      return apiRequest.post('/connections/batch-operation', {
        operation,
        connectionIds,
        data
      })
    }
  },

  // 数据管理API
  data: {
    // 获取数据源列表
    getDataSources: async () => {
      return apiRequest.get('/data/sources')
    },
    
    // 创建数据源
    createDataSource: async (dataSource: any) => {
      return apiRequest.post('/data/sources', dataSource)
    },
    
    // 获取数据处理器列表
    getDataProcessors: async () => {
      return apiRequest.get('/data/processors')
    },
    
    // 创建数据处理器
    createDataProcessor: async (processor: any) => {
      return apiRequest.post('/data/processors', processor)
    },
    
    // 执行数据处理
    executeDataProcessing: async (processorId: string, data: any, config?: any) => {
      return apiRequest.post(`/data/processors/${processorId}/execute`, {
        data,
        config
      })
    },
    
    // 获取数据质量报告
    getDataQualityReport: async (dataSourceId: string, dateRange?: any) => {
      const params = dateRange 
        ? `?dataSourceId=${dataSourceId}&startDate=${dateRange.start}&endDate=${dateRange.end}`
        : `?dataSourceId=${dataSourceId}`
      return apiRequest.get(`/data/quality-report${params}`)
    },
    
    // 导入数据
    importData: async (dataSourceId: string, file: File, options?: any) => {
      const formData = new FormData()
      formData.append('file', file)
      if (options) {
        Object.entries(options).forEach(([key, value]) => {
          formData.append(key, String(value))
        })
      }
      
      return apiRequest.upload(`/data/sources/${dataSourceId}/import`, formData)
    },
    
    // 导出数据
    exportData: async (dataSourceId: string, format: string = 'csv', filters?: any) => {
      const params = filters 
        ? `?format=${format}&filters=${JSON.stringify(filters)}`
        : `?format=${format}`
      return apiRequest.download(`/data/sources/${dataSourceId}/export${params}`, `data-export.${format}`)
    }
  },

  // 策略管理API
  strategy: {
    // 获取策略列表
    getStrategies: async (page: number = 1, pageSize: number = 10, category?: string) => {
      const params = new URLSearchParams({
        page: page.toString(),
        pageSize: pageSize.toString()
      })
      if (category) params.append('category', category)
      
      return apiRequest.get(`/strategy?${params.toString()}`)
    },
    
    // 创建策略
    createStrategy: async (strategy: any) => {
      return apiRequest.post('/strategy', strategy)
    },
    
    // 获取策略详情
    getStrategyDetails: async (id: string) => {
      return apiRequest.get(`/strategy/${id}`)
    },
    
    // 更新策略
    updateStrategy: async (id: string, updates: any) => {
      return apiRequest.put(`/strategy/${id}`, updates)
    },
    
    // 删除策略
    deleteStrategy: async (id: string) => {
      return apiRequest.delete(`/strategy/${id}`)
    },
    
    // 回测策略
    backtestStrategy: async (id: string, backtestConfig?: any) => {
      return apiRequest.post(`/strategy/${id}/backtest`, { backtestConfig })
    },
    
    // 获取策略回测结果
    getBacktestResults: async (id: string, backtestId: string) => {
      return apiRequest.get(`/strategy/${id}/backtest/${backtestId}`)
    },
    
    // 获取策略性能指标
    getStrategyPerformance: async (id: string, dateRange?: any) => {
      const params = dateRange 
        ? `?startDate=${dateRange.start}&endDate=${dateRange.end}`
        : ''
      return apiRequest.get(`/strategy/${id}/performance${params}`)
    }
  },

  // 回测管理API
  backtest: {
    // 获取回测列表
    getBacktests: async (page: number = 1, pageSize: number = 10, strategyId?: string) => {
      const params = new URLSearchParams({
        page: page.toString(),
        pageSize: pageSize.toString()
      })
      if (strategyId) params.append('strategyId', strategyId)
      
      return apiRequest.get(`/backtest?${params.toString()}`)
    },
    
    // 创建回测
    createBacktest: async (backtest: any) => {
      return apiRequest.post('/backtest', backtest)
    },
    
    // 获取回测详情
    getBacktestDetails: async (id: string) => {
      return apiRequest.get(`/backtest/${id}`)
    },
    
    // 执行回测
    executeBacktest: async (id: string) => {
      return apiRequest.post(`/backtest/${id}/execute`)
    },
    
    // 停止回测
    stopBacktest: async (id: string) => {
      return apiRequest.post(`/backtest/${id}/stop`)
    },
    
    // 获取回测结果
    getBacktestResults: async (id: string) => {
      return apiRequest.get(`/backtest/${id}/results`)
    },
    
    // 获取回测性能报告
    getBacktestReport: async (id: string, format: string = 'pdf') => {
      return apiRequest.download(`/backtest/${id}/report?format=${format}`, `backtest-report.${format}`)
    }
  },

  // AI模型管理API
  ai: {
    // 获取AI模型列表
    getModels: async (type?: string, status?: string) => {
      const params = new URLSearchParams()
      if (type) params.append('type', type)
      if (status) params.append('status', status)
      
      return apiRequest.get(`/ai/models?${params.toString()}`)
    },
    
    // 创建AI模型
    createModel: async (model: any) => {
      return apiRequest.post('/ai/models', model)
    },
    
    // 训练AI模型
    trainModel: async (id: string, trainingConfig?: any) => {
      return apiRequest.post(`/ai/models/${id}/train`, { trainingConfig })
    },
    
    // 获取训练状态
    getTrainingStatus: async (id: string) => {
      return apiRequest.get(`/ai/models/${id}/training-status`)
    },
    
    // 停止训练
    stopTraining: async (id: string) => {
      return apiRequest.post(`/ai/models/${id}/stop-training`)
    },
    
    // 部署模型
    deployModel: async (id: string, deploymentConfig?: any) => {
      return apiRequest.post(`/ai/models/${id}/deploy`, { deploymentConfig })
    },
    
    // 获取模型预测
    getModelPredictions: async (id: string, data: any) => {
      return apiRequest.post(`/ai/models/${id}/predict`, { data })
    },
    
    // 获取模型性能指标
    getModelPerformance: async (id: string) => {
      return apiRequest.get(`/ai/models/${id}/performance`)
    },
    
    // 删除模型
    deleteModel: async (id: string) => {
      return apiRequest.delete(`/ai/models/${id}`)
    }
  },

  // 系统管理API
  system: {
    // 获取系统状态
    getSystemStatus: async () => {
      return apiRequest.get('/system/status')
    },
    
    // 获取系统健康检查
    getHealthCheck: async () => {
      return apiRequest.get('/system/health')
    },
    
    // 获取系统配置
    getSystemConfig: async () => {
      return apiRequest.get('/system/config')
    },
    
    // 更新系统配置
    updateSystemConfig: async (config: any) => {
      return apiRequest.put('/system/config', config)
    },
    
    // 获取系统日志
    getSystemLogs: async (level?: string, limit: number = 100) => {
      const params = new URLSearchParams({
        limit: limit.toString()
      })
      if (level) params.append('level', level)
      
      return apiRequest.get(`/system/logs?${params.toString()}`)
    },
    
    // 获取系统指标
    getSystemMetrics: async () => {
      return apiRequest.get('/system/metrics')
    },
    
    // 清理系统缓存
    clearSystemCache: async () => {
      return apiRequest.post('/system/clear-cache')
    },
    
    // 重启系统服务
    restartService: async (serviceName: string) => {
      return apiRequest.post(`/system/restart-service`, { serviceName })
    }
  }
}

// 导出完整的API层
export default completeApiLayer

// 导出类型定义
export type {
  ApiResponse,
  RequestConfig
} from './index'
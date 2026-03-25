import type { Node, Connection } from '../types/workflow'
import { getStockList, getStockDetail, getStockHistory, getRealtimeData, getIndicators } from '../api/modules/data'
import {
  recognizePatterns,
  detectAnomalies,
  assessRisk,
  generateFactors,
  askQuestion
} from '../api/modules/intelligent'

export interface WorkflowExecutionState {
  id: string
  status: 'idle' | 'running' | 'completed' | 'failed' | 'paused'
  startTime?: number
  endTime?: number
  currentStep?: string
  progress: number
  results: Record<string, any>
  errors: Array<{
    nodeId: string
    error: string
    timestamp: number
  }>
  logs: Array<{
    timestamp: number
    level: 'info' | 'warning' | 'error' | 'success'
    nodeId?: string
    message: string
  }>
}

export interface NodeExecutor {
  id: string
  type: string
  execute: (input: any, config: any) => Promise<any>
  validate?: (config: any) => boolean
  description?: string
}

export class WorkflowEngine {
  private executors: Map<string, NodeExecutor> = new Map()
  private executionState: WorkflowExecutionState | null = null
  private abortController: AbortController | null = null

  constructor() {
    // 注册默认执行器
    this.registerDefaultExecutors()
  }

  /**
   * 注册节点执行器
   */
  registerExecutor(executor: NodeExecutor) {
    this.executors.set(executor.type, executor)
  }

  /**
   * 获取执行器
   */
  getExecutor(type: string): NodeExecutor | undefined {
    return this.executors.get(type)
  }

  /**
   * 获取所有已注册的执行器
   */
  getAllExecutors(): NodeExecutor[] {
    return Array.from(this.executors.values())
  }

  /**
   * 验证工作流
   */
  validateWorkflow(nodes: Node[], connections: Connection[]): { valid: boolean; errors: string[] } {
    const errors: string[] = []

    // 检查节点
    for (const node of nodes) {
      // 检查是否有对应的执行器（按类型）
      if (!this.executors.has(node.type)) {
        errors.push(`节点 ${node.title} (${node.type}) 没有对应的执行器`)
        continue
      }

      // 检查节点配置
      const executor = this.executors.get(node.type)!
      if (executor.validate && !executor.validate(node.params)) {
        errors.push(`节点 ${node.title} 的配置无效`)
      }
    }

    // 检查连接
    const nodeMap = new Map(nodes.map(n => [n.id, n]))
    for (const conn of connections) {
      // 检查源节点和目标节点是否存在
      if (!nodeMap.has(conn.from)) {
        errors.push(`连接的源节点 ${conn.from} 不存在`)
      }
      if (!nodeMap.has(conn.to)) {
        errors.push(`连接的目标节点 ${conn.to} 不存在`)
      }

      // 检查目标节点的输入端口
      const targetNode = nodeMap.get(conn.to)
      if (targetNode && conn.toInputId) {
        const inputPort = targetNode.inputs?.find(p => p.id === conn.toInputId)
        if (!inputPort) {
          errors.push(`节点 ${targetNode.title} 没有输入端口 ${conn.toInputId}`)
        }
      }
    }

    // 检查是否有起始节点（没有输入的节点）
    const startNodes = nodes.filter(node =>
      !connections.some(conn => conn.to === node.id)
    )
    if (startNodes.length === 0) {
      errors.push('工作流没有起始节点')
    }

    return {
      valid: errors.length === 0,
      errors
    }
  }

  /**
   * 构建执行计划
   */
  private buildExecutionPlan(nodes: Node[], connections: Connection[]): Node[][] {
    const nodeMap = new Map(nodes.map(n => [n.id, n]))
    const executed = new Set<string>()
    const levels: Node[][] = []

    // 找出所有起始节点
    const startNodes = nodes.filter(node =>
      !connections.some(conn => conn.to === node.id)
    )

    // 按层级构建执行计划
    let currentLevel = [...startNodes]
    while (currentLevel.length > 0) {
      levels.push(currentLevel)
      currentLevel.forEach(node => executed.add(node.id))

      // 找出下一层节点
      const nextLevel: Node[] = []
      for (const node of currentLevel) {
        const nextNodes = connections
          .filter(conn => conn.from === node.id)
          .map(conn => nodeMap.get(conn.to))
          .filter((n): n is Node => n !== undefined && !executed.has(n.id))

        nextLevel.push(...nextNodes)
      }

      // 去重
      currentLevel = Array.from(new Set(nextLevel))
    }

    return levels
  }

  /**
   * 执行工作流
   */
  async executeWorkflow(
    nodes: Node[],
    connections: Connection[],
    onProgress?: (state: WorkflowExecutionState) => void,
    onLog?: (log: any) => void
  ): Promise<WorkflowExecutionState> {
    // 验证工作流
    const validation = this.validateWorkflow(nodes, connections)
    if (!validation.valid) {
      const errorState: WorkflowExecutionState = {
        id: Date.now().toString(),
        status: 'failed',
        progress: 0,
        results: {},
        errors: validation.errors.map((e, i) => ({
          nodeId: 'workflow',
          error: e,
          timestamp: Date.now()
        })),
        logs: [{
          timestamp: Date.now(),
          level: 'error',
          message: '工作流验证失败',
        }]
      }
      return errorState
    }

    // 初始化执行状态
    this.executionState = {
      id: Date.now().toString(),
      status: 'running',
      startTime: Date.now(),
      progress: 0,
      results: {},
      errors: [],
      logs: [{
        timestamp: Date.now(),
        level: 'info',
        message: '开始执行工作流',
      }]
    }

    this.abortController = new AbortController()

    try {
      // 构建执行计划
      const executionPlan = this.buildExecutionPlan(nodes, connections)
      const totalSteps = executionPlan.reduce((sum, level) => sum + level.length, 0)
      let completedSteps = 0

      this.log('info', `执行计划包含 ${executionPlan.length} 个层级，共 ${totalSteps} 个节点`)

      // 按层级执行
      for (let levelIndex = 0; levelIndex < executionPlan.length; levelIndex++) {
        const level = executionPlan[levelIndex]

        this.log('info', `执行第 ${levelIndex + 1} 层，包含 ${level.length} 个节点`)

        // 并行执行同一层级的节点
        const levelPromises = level.map(async (node) => {
          return this.executeNode(node, connections, this.executionState!.results)
        })

        // 等待当前层级所有节点完成
        const levelResults = await Promise.allSettled(levelPromises)

        // 处理结果
        for (let i = 0; i < level.length; i++) {
          const node = level[i]
          const result = levelResults[i]

          if (result.status === 'fulfilled') {
            this.executionState!.results[node.id] = result.value
            this.log('success', `节点 ${node.title} 执行成功`)
          } else {
            const error = result.reason
            this.executionState!.errors.push({
              nodeId: node.id,
              error: error.message || String(error),
              timestamp: Date.now()
            })
            this.log('error', `节点 ${node.title} 执行失败: ${error.message || String(error)}`, node.id)
          }

          completedSteps++
          this.executionState!.progress = Math.round((completedSteps / totalSteps) * 100)
        }

        // 更新进度
        if (onProgress) {
          onProgress(this.executionState)
        }
      }

      // 完成
      this.executionState.status = 'completed'
      this.executionState.endTime = Date.now()
      this.log('success', '工作流执行完成')

    } catch (error: any) {
      // 处理错误
      this.executionState.status = 'failed'
      this.executionState.endTime = Date.now()
      this.executionState.errors.push({
        nodeId: 'workflow',
        error: error.message || String(error),
        timestamp: Date.now()
      })
      this.log('error', `工作流执行失败: ${error.message || String(error)}`)
    }

    if (onLog) {
      this.executionState.logs.forEach(onLog)
    }

    return this.executionState
  }

  /**
   * 执行单个节点
   */
  private async executeNode(
    node: Node,
    connections: Connection[],
    results: Record<string, any>
  ): Promise<any> {
    // 检查是否被中止
    if (this.abortController?.signal.aborted) {
      throw new Error('执行被中止')
    }

    // 获取输入数据
    const inputData = this.getNodeInputData(node, connections, results)

    // 更新当前步骤
    if (this.executionState) {
      this.executionState.currentStep = node.title
    }

    // 获取执行器
    const executor = this.executors.get(node.type)
    if (!executor) {
      throw new Error(`节点 ${node.type} 没有对应的执行器`)
    }

    // 执行节点
    this.log('info', `开始执行节点: ${node.title}`, node.id)
    const startTime = Date.now()

    try {
      const result = await executor.execute(inputData, node.params || {})

      const duration = Date.now() - startTime
      this.log('info', `节点 ${node.title} 执行完成，耗时 ${duration}ms`, node.id)

      return result
    } catch (error: any) {
      const duration = Date.now() - startTime
      this.log('error', `节点 ${node.title} 执行失败，耗时 ${duration}ms: ${error.message}`, node.id)
      throw error
    }
  }

  /**
   * 获取节点输入数据
   */
  private getNodeInputData(
    node: Node,
    connections: Connection[],
    results: Record<string, any>
  ): any {
    const inputConnections = connections.filter(conn => conn.to === node.id)

    if (inputConnections.length === 0) {
      return null
    }

    // 如果有多个输入，将它们合并
    if (inputConnections.length === 1) {
      return results[inputConnections[0].from]
    }

    // 多输入情况
    const inputs: Record<string, any> = {}
    for (const conn of inputConnections) {
      const inputKey = conn.toInputId || conn.from
      inputs[inputKey] = results[conn.from]
    }

    return inputs
  }

  /**
   * 记录日志
   */
  private log(level: 'info' | 'warning' | 'error' | 'success', message: string, nodeId?: string) {
    if (!this.executionState) return

    this.executionState.logs.push({
      timestamp: Date.now(),
      level,
      nodeId,
      message
    })
  }

  /**
   * 暂停执行
   */
  pause() {
    if (this.executionState?.status === 'running') {
      this.executionState.status = 'paused'
      this.log('info', '工作流已暂停')
    }
  }

  /**
   * 恢复执行
   */
  resume() {
    if (this.executionState?.status === 'paused') {
      this.executionState.status = 'running'
      this.log('info', '工作流已恢复')
    }
  }

  /**
   * 停止执行
   */
  stop() {
    if (this.executionState?.status === 'running') {
      this.abortController?.abort()
      this.executionState.status = 'failed'
      this.executionState.endTime = Date.now()
      this.log('warning', '工作流已停止')
    }
  }

  /**
   * 获取当前执行状态
   */
  getExecutionState(): WorkflowExecutionState | null {
    return this.executionState
  }

  /**
   * 注册默认执行器
   */
  private registerDefaultExecutors() {
    // 数据获取执行器
    this.registerExecutor({
      id: 'data-acquisition',
      type: 'data-acquisition',
      description: '股票数据获取',
      execute: async (input, config) => {
        try {
          const stockCode = config.stockCode || '000001'
          const timeRange = config.timeRange || '1M'

          // 获取股票详情
          const stockDetail = await getStockDetail(stockCode)

          // 获取历史数据
          const endDate = new Date().toISOString().split('T')[0]
          const startDate = this.getStartDate(endDate, timeRange)
          const historyData = await getStockHistory(stockCode, {
            startDate,
            endDate,
            frequency: config.frequency || 'daily'
          })

          // 获取技术指标
          const indicators = await getIndicators(stockCode, config.indicators || ['ma5', 'ma10', 'ma20', 'rsi'])

          // 获取实时数据（如果是当天）
          let realtimeData = null
          if (this.isToday(startDate)) {
            realtimeData = await getRealtimeData([stockCode])
          }

          return {
            stockCode,
            stockName: stockDetail.data?.name || stockCode,
            data: historyData.data || [],
            metrics: indicators.data || {},
            realtimeData: realtimeData?.data || null,
            timestamp: new Date().toISOString()
          }
        } catch (error: any) {
          console.error('数据获取失败:', error)
          // 如果API调用失败，返回Mock数据作为后备
          const mockData = {
            stockCode: config.stockCode || '000001',
            stockName: '平安银行',
            data: this.generateMockStockData(config.timeRange || '1M'),
            metrics: {
              ma5: 12.5,
              ma20: 12.2,
              rsi: 55.5,
              volume: 1000000
            },
            error: error.message,
            isFallback: true
          }
          return mockData
        }
      },
      validate: (config) => {
        return !!(config && config.stockCode)
      }
    })

    // 数据清洗执行器
    this.registerExecutor({
      id: 'data-cleaning',
      type: 'data-cleaning',
      description: '数据清洗',
      execute: async (input, config) => {
        console.log('[DataCleaningExecutor] 接收到输入数据:', input)

        if (!input || !input.data) {
          throw new Error('没有输入数据')
        }

        try {
          // 获取API基础URL
          const apiBaseURL = (import.meta.env as any).VITE_API_BASE_URL || 'http://localhost:8010/api/v1'
          const apiEndpoint = `${apiBaseURL}/data-cleaning/clean`

          // 提取股票代码列表 - 支持多种数据格式
          let stockCodes: string[] = []

          // 格式1: input.data 是股票选择节点的返回结果数组 [{symbol, data, ...}, ...]
          if (Array.isArray(input.data) && input.data.length > 0) {
            // 检查是否是股票选择节点返回的数据结构
            if (input.data[0]?.symbol !== undefined) {
              // 股票选择节点格式: [{symbol: '000001', data: {...}, ...}, ...]
              stockCodes = input.data.map((item: any) => item.symbol).filter(Boolean)
              console.log('[DataCleaningExecutor] 从股票选择节点数据格式提取股票代码:', stockCodes)
            } else {
              // 尝试从普通数据格式中提取
              const codes = new Set<string>()
              input.data.forEach((item: any) => {
                if (item.symbol || item.stock) {
                  codes.add(item.symbol || item.stock)
                }
              })
              stockCodes = Array.from(codes)
              console.log('[DataCleaningExecutor] 从普通数据格式提取股票代码:', stockCodes)
            }
          }
          // 格式2: 直接提供stockCode
          else if (input.stockCode) {
            stockCodes = [input.stockCode]
          }
          // 格式3: 直接提供stockCodes数组
          else if (input.stockCodes && Array.isArray(input.stockCodes)) {
            stockCodes = input.stockCodes
          }

          if (stockCodes.length === 0) {
            console.warn('[DataCleaningExecutor] 无法从输入数据中提取股票代码，数据结构:', JSON.stringify(input).slice(0, 500))
            throw new Error('无法从输入数据中提取股票代码')
          }

          // 获取时间范围
          let startDate = config.startDate
          let endDate = config.endDate

          // 如果没有提供时间范围，尝试从输入数据中推断
          if (!startDate || !endDate) {
            // 对于股票选择节点格式，从第一个股票的数据中提取时间范围
            if (input.data[0]?.data?.values && Array.isArray(input.data[0].data.values)) {
              const values = input.data[0].data.values
              const columns = input.data[0].data.columns || []
              const dateIdx = columns.indexOf('date')
              const timestampIdx = columns.indexOf('timestamp')

              if (dateIdx !== -1 && values.length > 0) {
                startDate = values[0][dateIdx]
                endDate = values[values.length - 1][dateIdx]
              } else if (timestampIdx !== -1 && values.length > 0) {
                startDate = values[0][timestampIdx]
                endDate = values[values.length - 1][timestampIdx]
              }
              console.log('[DataCleaningExecutor] 从股票数据中提取时间范围:', startDate, '至', endDate)
            }
          }

          // 构建请求参数
          const requestParams = {
            node_id: config.nodeId || 'data-cleaning',
            stock_codes: stockCodes,
            start_date: startDate,
            end_date: endDate,
            config: {
              quality_assessment: {
                enabled: true,
                completeness_threshold: config.completenessThreshold ?? 0.95,
                accuracy_threshold: 0.98,
                consistency_threshold: 0.90,
                timeliness_threshold: 0.85
              },
              data_cleaning: {
                remove_duplicates: true,
                handle_missing: {
                  strategy: config.missingStrategy || 'interpolate',
                  threshold: config.maxMissingRatio ?? 0.05
                },
                outlier_detection: {
                  method: config.outlierMethod || 'iqr',
                  threshold: 3.0,
                  action: config.outlierAction || 'cap'
                },
                data_normalization: {
                  method: config.normalizationMethod || 'z_score',
                  features: ['price', 'volume', 'returns']
                }
              },
              validation_rules: {
                price_range: { min: 0, max: 10000 },
                volume_positive: true,
                returns_bounds: { min: -0.2, max: 0.2 }
              }
            }
          }

          console.log('[DataCleaningExecutor] 调用真正的数据清洗API:', apiEndpoint)
          console.log('[DataCleaningExecutor] 请求参数:', JSON.stringify(requestParams, null, 2))

          // 调用后端API
          const response = await fetch(apiEndpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(requestParams)
          })

          if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`)
          }

          const result = await response.json()
          console.log('[DataCleaningExecutor] API响应:', result)

          // 检查响应格式 - 后端返回 {code, message, data: {...}}
          if (result.code !== 200) {
            throw new Error(result.detail || result.message || '数据清洗失败')
          }

          // 提取清洗结果数据
          const cleanData = result.data || {}
          const cleanedData = cleanData.cleaned_data
          const statistics = cleanData.statistics || {}
          const qualityReport = cleanData.quality_report

          // 计算原始数据行数（统计所有股票的数据行数）
          let originalDataCount = 0
          if (Array.isArray(input.data)) {
            input.data.forEach((stockData: any) => {
              if (stockData.data?.values) {
                originalDataCount += stockData.data.values.length
              }
            })
          }

          // 返回清洗结果
          return {
            ...input,
            stockCodes: stockCodes,
            originalDataCount: originalDataCount,
            cleanedDataCount: cleanedData?.length || originalDataCount,
            data: cleanedData || input.data,
            qualityReport: qualityReport,
            statistics: statistics,
            isRealData: true,
            dataSource: cleanData.data_source
          }

        } catch (error: any) {
          console.error('[DataCleaningExecutor] 数据清洗API调用失败:', error)

          // API失败时，回退到基础清洗逻辑
          console.warn('[DataCleaningExecutor] 使用基础清洗逻辑作为后备方案')

          let cleanedData = input.data
          let originalDataCount = 0

          // 对于股票选择节点格式，进行基础过滤
          if (Array.isArray(input.data) && input.data[0]?.data?.values) {
            const filtered = input.data.map((stockData: any) => {
              if (stockData.data?.values && Array.isArray(stockData.data.values)) {
                originalDataCount += stockData.data.values.length
                const filteredValues = stockData.data.values.filter((row: any[]) => {
                  const closeIdx = stockData.data.columns?.indexOf('close') ?? -1
                  return closeIdx === -1 || row[closeIdx] > 0
                })
                return {
                  ...stockData,
                  data: {
                    ...stockData.data,
                    values: filteredValues
                  }
                }
              }
              return stockData
            })
            cleanedData = filtered
          }

          return {
            ...input,
            originalDataCount: originalDataCount,
            cleanedDataCount: cleanedData.length || input.data.length,
            data: cleanedData,
            isFallback: true,
            error: error.message
          }
        }
      },
      validate: (config) => {
        return true // 数据清洗配置总是有效的
      }
    })

    // 特征工程执行器
    this.registerExecutor({
      id: 'feature-engineering',
      type: 'feature-engineering',
      description: '特征工程',
      execute: async (input, config) => {
        if (!input || !input.data) {
          throw new Error('没有输入数据')
        }

        try {
          // 使用真实API进行特征提取
          const stockCode = input.stockCode || '000001'

          // 1. 模式识别
          const patternResult = await recognizePatterns({
            stockCode,
            timeRange: {
              startDate: input.data[0]?.date || new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
              endDate: input.data[input.data.length - 1]?.date || new Date().toISOString().split('T')[0]
            },
            patternTypes: config.patternTypes || ['trend', 'support', 'resistance'],
            sensitivity: config.sensitivity || 'medium'
          })

          // 2. 异常检测
          const anomalyResult = await detectAnomalies({
            stockCode,
            data: input.data.map((item: any) => ({
              timestamp: item.timestamp,
              price: item.close,
              volume: item.volume
            })),
            threshold: config.anomalyThreshold || 0.1,
            method: config.anomalyMethod || 'hybrid'
          })

          // 3. 智能因子生成
          const factorResult = await generateFactors({
            universe: [stockCode],
            methodology: config.factorMethodology || 'hybrid',
            constraints: {
              maxFactors: config.maxFactors || 10,
              correlationThreshold: config.correlationThreshold || 0.7,
              icThreshold: config.icThreshold || 0.05
            }
          })

          // 处理返回的特征数据
          const features = {
            patterns: patternResult.data || [],
            anomalies: anomalyResult.data?.anomalies || [],
            factors: factorResult.data?.factors || [],
            trend: patternResult.data?.trend || 'neutral',
            volatility: anomalyResult.data?.volatility || 0.15,
            technicalIndicators: {
              // 保持原有的技术指标作为后备
              macd: input.metrics?.macd || 0,
              rsi: input.metrics?.rsi || 50,
              kdj: input.metrics?.kdj || { k: 50, d: 50, j: 50 }
            }
          }

          return {
            ...input,
            features,
            featureCount: Object.keys(features).length,
            isRealData: true
          }

        } catch (error: any) {
          console.error('特征工程API调用失败，使用模拟数据:', error)

          // API失败时使用模拟特征数据
          const features = {
            trend: 'neutral',
            volatility: 0.15,
            momentum: 0.08,
            support: input.data?.[Math.floor(input.data.length * 0.3)]?.close || 0,
            resistance: input.data?.[Math.floor(input.data.length * 0.7)]?.close || 0,
            technicalIndicators: {
              macd: input.metrics?.macd || 0,
              rsi: input.metrics?.rsi || 50,
              kdj: input.metrics?.kdj || { k: 50, d: 50, j: 50 }
            },
            isFallback: true,
            error: error.message
          }

          return {
            ...input,
            features,
            featureCount: Object.keys(features).length
          }
        }
      }
    })

    // 模型训练执行器
    this.registerExecutor({
      id: 'model-training',
      type: 'model-training',
      description: '模型训练',
      execute: async (input, config) => {
        await new Promise(resolve => setTimeout(resolve, 2000))

        if (!input || !input.data) {
          throw new Error('没有输入数据')
        }

        // 模拟模型训练
        const model = {
          type: config.modelType || 'LSTM',
          accuracy: 0.85 + Math.random() * 0.1,
          loss: 0.15 - Math.random() * 0.05,
          trainingEpochs: config.epochs || 100,
          featureImportance: {
            price: 0.4,
            volume: 0.2,
            technical: 0.3,
            sentiment: 0.1
          }
        }

        return {
          ...input,
          model,
          trainedAt: new Date().toISOString()
        }
      },
      validate: (config) => {
        return true
      }
    })

    // AI助手执行器
    this.registerExecutor({
      id: 'ai-assistant',
      type: 'ai-assistant',
      description: 'AI智能分析',
      execute: async (input, config) => {
        if (!input || !input.data) {
          throw new Error('没有输入数据')
        }

        try {
          // 使用真实AI API进行分析
          const stockCode = input.stockCode || '000001'
          const currentPrice = input.data[input.data.length - 1]?.close || 0

          // 构建分析问题
          const question = config.question || `请分析股票 ${stockCode}（当前价格：${currentPrice}）的投资建议，包括买入/持有/卖出建议、目标价格、风险等级和详细理由`

          // 调用智能问答API
          const aiResult = await askQuestion({
            question,
            context: `股票代码：${stockCode}，当前价格：${currentPrice}，数据时间范围：${input.data[0]?.date} 至 ${input.data[input.data.length - 1]?.date}`,
            stockCodes: [stockCode],
            analysisType: config.analysisType || 'technical'
          })

          // 风险评估
          const riskResult = await assessRisk({
            stockCodes: [stockCode],
            timeHorizon: config.timeHorizon || 'medium',
            riskType: 'comprehensive'
          })

          // 处理AI分析结果
          const analysis = {
            recommendation: aiResult.data?.recommendation || 'HOLD',
            confidence: aiResult.data?.confidence || 0.75,
            targetPrice: aiResult.data?.targetPrice || currentPrice * 1.05,
            timeframe: config.timeframe || '1W',
            reasoning: aiResult.data?.reasoning || '基于技术指标和市场趋势分析',
            riskLevel: riskResult.data?.riskLevel || 'MEDIUM',
            riskScore: riskResult.data?.riskScore || 0.5,
            aiResponse: aiResult.data?.response || '',
            factors: aiResult.data?.factors || []
          }

          return {
            ...input,
            aiAnalysis: analysis,
            isRealData: true
          }

        } catch (error: any) {
          console.error('AI助手API调用失败，使用模拟数据:', error)

          // API失败时使用模拟AI分析
          const currentPrice = input.data?.[input.data.length - 1]?.close || 100
          const analysis = {
            recommendation: Math.random() > 0.5 ? 'BUY' : 'HOLD',
            confidence: 0.75 + Math.random() * 0.2,
            targetPrice: currentPrice * (1 + Math.random() * 0.1 - 0.05),
            timeframe: config.timeframe || '1W',
            reasoning: '基于技术指标和市场趋势分析',
            riskLevel: Math.random() > 0.7 ? 'HIGH' : Math.random() > 0.3 ? 'MEDIUM' : 'LOW',
            isFallback: true,
            error: error.message
          }

          return {
            ...input,
            aiAnalysis: analysis
          }
        }
      }
    })

    // 策略构思执行器
    this.registerExecutor({
      id: 'strategy-conception',
      type: 'strategy-conception',
      description: '策略构思',
      execute: async (input, config) => {
        await new Promise(resolve => setTimeout(resolve, 1000))

        // 模拟策略生成
        const strategy = {
          name: `量化策略_${Date.now()}`,
          type: config.strategyType || 'trend',
          description: '基于动量的趋势跟踪策略',
          parameters: {
            entryThreshold: 0.02,
            exitThreshold: 0.015,
            stopLoss: 0.05,
            takeProfit: 0.08
          },
          backtest: {
            winRate: 0.62,
            profitFactor: 1.8,
            maxDrawdown: 0.12,
            sharpeRatio: 1.45
          }
        }

        return {
          ...input,
          strategy
        }
      }
    })

    // 初步验证执行器
    this.registerExecutor({
      id: 'preliminary-validation',
      type: 'preliminary-validation',
      description: '策略验证',
      execute: async (input, config) => {
        await new Promise(resolve => setTimeout(resolve, 1200))

        if (!input || !input.strategy) {
          throw new Error('没有策略数据')
        }

        // 模拟验证结果
        const validation = {
          isValid: true,
          score: 75 + Math.random() * 20,
          checks: {
            profitability: Math.random() > 0.2,
            riskControl: Math.random() > 0.3,
            stability: Math.random() > 0.25,
            scalability: Math.random() > 0.4
          },
          recommendations: [
            '建议优化止损策略',
            '考虑增加市场情绪指标',
            '可以尝试动态调整参数'
          ]
        }

        return {
          ...input,
          validation
        }
      }
    })
  }

  /**
   * 获取开始日期
   */
  private getStartDate(endDate: string, timeRange: string): string {
    const end = new Date(endDate)
    const days = {
      '5D': 5,
      '1M': 30,
      '3M': 90,
      '6M': 180,
      '1Y': 365,
      '2Y': 730
    }

    const daysToSubtract = days[timeRange as keyof typeof days] || 30
    const start = new Date(end)
    start.setDate(start.getDate() - daysToSubtract)

    return start.toISOString().split('T')[0]
  }

  /**
   * 判断是否是今天
   */
  private isToday(date: string): boolean {
    const today = new Date().toISOString().split('T')[0]
    return date === today
  }

  /**
   * 生成模拟股票数据
   */
  private generateMockStockData(timeRange: string): any[] {
    const days = {
      '5D': 5,
      '1M': 30,
      '3M': 90,
      '6M': 180,
      '1Y': 365,
      '2Y': 730
    }

    const daysToGenerate = days[timeRange as keyof typeof days] || 30
    const data: any[] = []
    const now = Date.now()
    let price = 10 + Math.random() * 20

    for (let i = daysToGenerate; i >= 0; i--) {
      const timestamp = now - i * 24 * 60 * 60 * 1000
      const change = (Math.random() - 0.5) * 0.5
      price = Math.max(price + change, 5)

      data.push({
        timestamp,
        date: new Date(timestamp).toISOString().split('T')[0],
        open: price * (1 + Math.random() * 0.02 - 0.01),
        high: price * (1 + Math.random() * 0.03),
        low: price * (1 - Math.random() * 0.03),
        close: price,
        volume: Math.floor(Math.random() * 1000000) + 500000
      })
    }

    return data
  }
}

// 创建全局工作流引擎实例
export const workflowEngine = new WorkflowEngine()
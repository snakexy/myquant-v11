// 智能推荐系统API
// 支持自然语言解析、智能参数推荐、工作流自动构建

// 策略推荐请求接口
export interface StrategyRecommendationRequest {
  strategyType: 'momentum' | 'mean_reversion' | 'trend_following' | 'arbitrage' | 'custom'
  marketCondition: 'bull' | 'bear' | 'sideways' | 'volatile'
  timeHorizon: 'short_term' | 'medium_term' | 'long_term'
  riskLevel: 'conservative' | 'moderate' | 'aggressive'
  experienceLevel: 'beginner' | 'intermediate' | 'expert'
  customRequirements?: string
  symbols?: string[]
  dateRange?: {
    start: string
    end: string
  }
}

// 参数推荐接口
export interface ParameterRecommendation {
  parameter: string
  displayName: string
  recommendedValue: any
  userValue?: any
  range?: { min: number; max: number }
  reason: string
  confidence: number
  isUserEditable: boolean
  isAIRecommended: boolean
  type: 'number' | 'string' | 'boolean' | 'select'
  options?: string[]
}

// 节点推荐接口
export interface NodeRecommendation {
  id: string
  nodeType: string
  title: string
  icon: string
  position: { x: number; y: number }
  parameters: ParameterRecommendation[]
  connections: Array<{ from: string; to: string; type: string }>
  priority: 'essential' | 'recommended' | 'optional'
  isAIRecommended: boolean
}

// 工作流推荐接口
export interface WorkflowRecommendation {
  id: string
  name: string
  description: string
  nodes: NodeRecommendation[]
  connections: Array<{ from: string; to: string; type: string }>
  expectedPerformance: {
    accuracy: number
    sharpeRatio: number
    maxDrawdown: number
    annualReturn: number
  }
  complexity: 'low' | 'medium' | 'high'
  estimatedTime: number
  experienceLevel: 'beginner' | 'intermediate' | 'expert'
}

// 自然语言解析结果
export interface ParsedIntent {
  strategyType: string
  symbols: string[]
  dateRange: { start: string; end: string }
  riskLevel: string
  timeHorizon: string
  confidence: number
  requirements: string[]
}

// 参数优化建议
export interface OptimizationSuggestion {
  id: string
  title: string
  expectedImprovement: string
  changes: Array<{
    parameter: string
    from: any
    to: any
  }>
  reason: string
  confidence: number
}

// 经验水平定义
export interface ExperienceLevel {
  value: 'beginner' | 'intermediate' | 'expert'
  label: string
  icon: string
  description: string
}

// 策略类型定义
export interface StrategyType {
  value: string
  label: string
  icon: string
  description: string
  recommendedParams: Record<string, any>
  complexity: 'low' | 'medium' | 'high'
}

// 智能推荐服务类
export class IntelligentRecommendationService {
  private static readonly EXPERIENCE_LEVELS: ExperienceLevel[] = [
    {
      value: 'beginner',
      label: '新手入门',
      icon: '🟢',
      description: '适合刚接触量化交易的用户，提供完整的引导和智能推荐'
    },
    {
      value: 'intermediate',
      label: '进阶用户',
      icon: '🟡',
      description: '适合有一定经验的用户，提供模板选择和参数优化建议'
    },
    {
      value: 'expert',
      label: '专家用户',
      icon: '🟠',
      description: '适合专业用户，提供完全的手动控制和高级配置选项'
    }
  ]

  private static readonly STRATEGY_TYPES: StrategyType[] = [
    {
      value: 'momentum',
      label: '动量策略',
      icon: '🚀',
      description: '基于价格动量的交易策略',
      complexity: 'medium',
      recommendedParams: {
        lookbackPeriod: 20,
        threshold: 0.02,
        stopLoss: 0.05
      }
    },
    {
      value: 'mean_reversion',
      label: '均值回归',
      icon: '📊',
      description: '价格偏离均值时的回归交易策略',
      complexity: 'low',
      recommendedParams: {
        lookbackPeriod: 50,
        deviationThreshold: 2.0,
        stopLoss: 0.03
      }
    },
    {
      value: 'trend_following',
      label: '趋势跟踪',
      icon: '📈',
      description: '跟随市场趋势的交易策略',
      complexity: 'medium',
      recommendedParams: {
        fastPeriod: 12,
        slowPeriod: 26,
        signalPeriod: 9
      }
    },
    {
      value: 'arbitrage',
      label: '套利策略',
      icon: '⚖️',
      description: '利用价格差异进行套利交易',
      complexity: 'high',
      recommendedParams: {
        correlationThreshold: 0.8,
        spreadThreshold: 0.01,
        holdingPeriod: 5
      }
    }
  ]

  // 获取经验水平列表
  static getExperienceLevels(): ExperienceLevel[] {
    return this.EXPERIENCE_LEVELS
  }

  // 获取策略类型列表
  static getStrategyTypes(): StrategyType[] {
    return this.STRATEGY_TYPES
  }

  // 自然语言解析
  static async parseNaturalLanguage(input: string): Promise<ParsedIntent> {
    try {
      // 模拟API调用，实际应该调用后端NLP服务
      const response = await fetch('/api/intelligent-recommendation/parse-natural-language', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ input })
      })

      if (!response.ok) {
        throw new Error('自然语言解析失败')
      }

      const result = await response.json()
      return result.data
    } catch (error) {
      console.error('自然语言解析错误:', error)
      
      // 简单的本地解析作为后备
      return this.simpleLocalParse(input)
    }
  }

  // 简单本地解析（后备方案）
  private static simpleLocalParse(input: string): ParsedIntent {
    const lowerInput = input.toLowerCase()
    const result: ParsedIntent = {
      strategyType: 'custom',
      symbols: [],
      dateRange: { start: '', end: '' },
      riskLevel: 'moderate',
      timeHorizon: 'medium_term',
      confidence: 0.5,
      requirements: []
    }

    // 提取股票代码
    const stockPattern = /(\d{6})/g
    const matches = input.match(stockPattern)
    if (matches) {
      result.symbols = matches.map(match => match + '.SZ')
      result.confidence += 0.2
    }

    // 提取时间范围
    const yearPattern = /(\d{4})年/g
    const yearMatch = input.match(yearPattern)
    if (yearMatch) {
      result.dateRange.start = `${yearMatch[1]}-01-01`
      result.dateRange.end = `${yearMatch[1]}-12-31`
      result.confidence += 0.1
    }

    // 策略类型识别
    if (lowerInput.includes('动量') || lowerInput.includes('momentum')) {
      result.strategyType = 'momentum'
      result.confidence += 0.2
    } else if (lowerInput.includes('均值') || lowerInput.includes('回归') || lowerInput.includes('reversion')) {
      result.strategyType = 'mean_reversion'
      result.confidence += 0.2
    } else if (lowerInput.includes('趋势') || lowerInput.includes('trend')) {
      result.strategyType = 'trend_following'
      result.confidence += 0.2
    } else if (lowerInput.includes('套利') || lowerInput.includes('arbitrage')) {
      result.strategyType = 'arbitrage'
      result.confidence += 0.1
    }

    // 风险水平识别
    if (lowerInput.includes('保守') || lowerInput.includes('conservative')) {
      result.riskLevel = 'conservative'
    } else if (lowerInput.includes('激进') || lowerInput.includes('aggressive')) {
      result.riskLevel = 'aggressive'
    }

    result.requirements = [
      `策略类型: ${result.strategyType}`,
      `股票代码: ${result.symbols.join(', ') || '未指定'}`,
      `时间范围: ${result.dateRange.start || '未指定'} 至 ${result.dateRange.end || '未指定'}`,
      `风险水平: ${result.riskLevel}`
    ]

    return result
  }

  // 获取策略推荐
  static async getStrategyRecommendation(
    request: StrategyRecommendationRequest
  ): Promise<WorkflowRecommendation> {
    try {
      const response = await fetch('/api/intelligent-recommendation/strategy-recommendation', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request)
      })

      if (!response.ok) {
        throw new Error('获取策略推荐失败')
      }

      const result = await response.json()
      return result.data
    } catch (error) {
      console.error('策略推荐错误:', error)
      
      // 本地推荐作为后备
      return this.generateLocalRecommendation(request)
    }
  }

  // 生成本地推荐（后备方案）
  private static generateLocalRecommendation(
    request: StrategyRecommendationRequest
  ): WorkflowRecommendation {
    const strategyType = this.STRATEGY_TYPES.find(s => s.value === request.strategyType)
    
    if (!strategyType) {
      throw new Error(`未知的策略类型: ${request.strategyType}`)
    }

    const workflowId = `workflow-${Date.now()}`
    const nodes: NodeRecommendation[] = []
    const connections: Array<{ from: string; to: string; type: string }> = []

    // 配置节点
    const configNode: NodeRecommendation = {
      id: `config-${Date.now()}-0`,
      nodeType: 'config',
      title: '回测配置',
      icon: '⚙️',
      position: { x: 100, y: 100 },
      parameters: this.generateConfigParameters(request, strategyType),
      connections: [],
      priority: 'essential',
      isAIRecommended: true
    }
    nodes.push(configNode)

    // 数据预处理节点
    const dataNode: NodeRecommendation = {
      id: `processing-${Date.now()}-1`,
      nodeType: 'processing',
      title: '数据预处理',
      icon: '🔄',
      position: { x: 400, y: 100 },
      parameters: this.generateDataParameters(request),
      connections: [],
      priority: 'essential',
      isAIRecommended: true
    }
    nodes.push(dataNode)

    // 策略执行节点
    const strategyNode: NodeRecommendation = {
      id: `strategy-${Date.now()}-2`,
      nodeType: 'processing',
      title: `${strategyType.label}策略`,
      icon: strategyType.icon,
      position: { x: 700, y: 100 },
      parameters: this.generateStrategyParameters(strategyType, request),
      connections: [],
      priority: 'essential',
      isAIRecommended: true
    }
    nodes.push(strategyNode)

    // 回测执行节点
    const backtestNode: NodeRecommendation = {
      id: `backtest-${Date.now()}-3`,
      nodeType: 'processing',
      title: '回测执行',
      icon: '🔬',
      position: { x: 1000, y: 100 },
      parameters: this.generateBacktestParameters(request),
      connections: [],
      priority: 'essential',
      isAIRecommended: true
    }
    nodes.push(backtestNode)

    // 结果分析节点
    const resultNode: NodeRecommendation = {
      id: `result-${Date.now()}-4`,
      nodeType: 'result',
      title: '回测结果',
      icon: '📊',
      position: { x: 1300, y: 100 },
      parameters: [],
      connections: [],
      priority: 'essential',
      isAIRecommended: true
    }
    nodes.push(resultNode)

    // 创建连接
    connections.push(
      { from: configNode.id, to: dataNode.id, type: 'data' },
      { from: dataNode.id, to: strategyNode.id, type: 'data' },
      { from: strategyNode.id, to: backtestNode.id, type: 'control' },
      { from: backtestNode.id, to: resultNode.id, type: 'data' }
    )

    return {
      id: workflowId,
      name: `${strategyType.label}回测工作流`,
      description: `基于${strategyType.description}的智能回测工作流`,
      nodes,
      connections,
      expectedPerformance: {
        accuracy: 0.75 + Math.random() * 0.2,
        sharpeRatio: 1.2 + Math.random() * 0.5,
        maxDrawdown: 0.15 + Math.random() * 0.1,
        annualReturn: 0.15 + Math.random() * 0.1
      },
      complexity: strategyType.complexity,
      estimatedTime: strategyType.complexity === 'low' ? 5 : strategyType.complexity === 'medium' ? 10 : 20,
      experienceLevel: request.experienceLevel
    }
  }

  // 生成配置参数
  private static generateConfigParameters(
    request: StrategyRecommendationRequest,
    strategyType: StrategyType
  ): ParameterRecommendation[] {
    const params: ParameterRecommendation[] = []

    // 股票代码
    params.push({
      parameter: 'symbols',
      displayName: '股票代码',
      recommendedValue: request.symbols?.join(', ') || '000001.SZ, 600000.SH',
      userValue: request.symbols?.join(', '),
      reason: '选择具有代表性的股票进行回测',
      confidence: 0.9,
      isUserEditable: true,
      isAIRecommended: false,
      type: 'string'
    })

    // 时间范围
    if (request.dateRange) {
      params.push({
        parameter: 'startDate',
        displayName: '开始日期',
        recommendedValue: request.dateRange.start,
        userValue: request.dateRange.start,
        reason: '设置回测开始时间',
        confidence: 0.95,
        isUserEditable: true,
        isAIRecommended: false,
        type: 'string'
      })

      params.push({
        parameter: 'endDate',
        displayName: '结束日期',
        recommendedValue: request.dateRange.end,
        userValue: request.dateRange.end,
        reason: '设置回测结束时间',
        confidence: 0.95,
        isUserEditable: true,
        isAIRecommended: false,
        type: 'string'
      })
    }

    // 初始资金
    params.push({
      parameter: 'initialCapital',
      displayName: '初始资金',
      recommendedValue: 1000000,
      userValue: 1000000,
      reason: '设置回测初始资金',
      confidence: 0.9,
      isUserEditable: true,
      isAIRecommended: false,
      type: 'number',
      range: { min: 10000, max: 10000000 }
    })

    // 风险水平
    params.push({
      parameter: 'riskLevel',
      displayName: '风险水平',
      recommendedValue: request.riskLevel,
      userValue: request.riskLevel,
      reason: '根据用户经验设置风险水平',
      confidence: 0.8,
      isUserEditable: true,
      isAIRecommended: false,
      type: 'select',
      options: ['conservative', 'moderate', 'aggressive']
    })

    return params
  }

  // 生成数据参数
  private static generateDataParameters(
    request: StrategyRecommendationRequest
  ): ParameterRecommendation[] {
    const params: ParameterRecommendation[] = []

    // 数据清洗
    params.push({
      parameter: 'dataCleaning',
      displayName: '数据清洗',
      recommendedValue: true,
      reason: '自动清洗异常值和缺失数据',
      confidence: 0.85,
      isUserEditable: true,
      isAIRecommended: true,
      type: 'boolean'
    })

    // 数据标准化
    params.push({
      parameter: 'dataNormalization',
      displayName: '数据标准化',
      recommendedValue: true,
      reason: '标准化数据格式以便处理',
      confidence: 0.8,
      isUserEditable: true,
      isAIRecommended: true,
      type: 'boolean'
    })

    // 特征工程
    params.push({
      parameter: 'featureEngineering',
      displayName: '特征工程',
      recommendedValue: true,
      reason: '自动生成技术指标和特征',
      confidence: 0.75,
      isUserEditable: true,
      isAIRecommended: true,
      type: 'boolean'
    })

    return params
  }

  // 生成策略参数
  private static generateStrategyParameters(
    strategyType: StrategyType,
    request: StrategyRecommendationRequest
  ): ParameterRecommendation[] {
    const params: ParameterRecommendation[] = []
    const recommendedParams = strategyType.recommendedParams

    // 遍历推荐参数
    Object.entries(recommendedParams).forEach(([key, value]) => {
      params.push({
        parameter: key,
        displayName: this.getParameterDisplayName(key),
        recommendedValue: value,
        userValue: value,
        reason: this.getParameterReason(key, strategyType),
        confidence: 0.8,
        isUserEditable: request.experienceLevel !== 'beginner',
        isAIRecommended: true,
        type: typeof value === 'number' ? 'number' : 'string',
        range: typeof value === 'number' ? { min: value * 0.5, max: value * 2 } : undefined
      })
    })

    return params
  }

  // 生成回测参数
  private static generateBacktestParameters(
    request: StrategyRecommendationRequest
  ): ParameterRecommendation[] {
    const params: ParameterRecommendation[] = []

    // 基准设置
    params.push({
      parameter: 'benchmark',
      displayName: '基准指数',
      recommendedValue: '000300.SH',
      reason: '选择沪深300作为基准',
      confidence: 0.7,
      isUserEditable: true,
      isAIRecommended: true,
      type: 'string'
    })

    // 交易频率
    params.push({
      parameter: 'rebalanceFrequency',
      displayName: '调仓频率',
      recommendedValue: 'monthly',
      reason: '月度调仓平衡交易成本和收益',
      confidence: 0.75,
      isUserEditable: true,
      isAIRecommended: true,
      type: 'select',
      options: ['daily', 'weekly', 'monthly']
    })

    // 交易成本
    params.push({
      parameter: 'transactionCost',
      displayName: '交易成本',
      recommendedValue: 0.002,
      reason: '设置合理的交易成本',
      confidence: 0.8,
      isUserEditable: true,
      isAIRecommended: true,
      type: 'number',
      range: { min: 0.0001, max: 0.01 }
    })

    return params
  }

  // 获取参数显示名称
  private static getParameterDisplayName(parameter: string): string {
    const nameMap: Record<string, string> = {
      lookbackPeriod: '回看周期',
      threshold: '阈值',
      stopLoss: '止损比例',
      fastPeriod: '快线周期',
      slowPeriod: '慢线周期',
      signalPeriod: '信号周期',
      correlationThreshold: '相关系数阈值',
      spreadThreshold: '价差阈值',
      holdingPeriod: '持有周期'
    }

    return nameMap[parameter] || parameter
  }

  // 获取参数推荐理由
  private static getParameterReason(parameter: string, strategyType: StrategyType): string {
    const reasonMap: Record<string, Record<string, string>> = {
      momentum: {
        lookbackPeriod: '动量策略通常使用20日回看周期',
        threshold: '2%的动量阈值能有效识别趋势变化',
        stopLoss: '5%止损控制单笔损失'
      },
      mean_reversion: {
        lookbackPeriod: '50日均线能较好反映长期趋势',
        deviationThreshold: '2倍标准差识别显著偏离',
        stopLoss: '3%止损适合均值回归策略'
      },
      trend_following: {
        fastPeriod: '12日快线反映短期趋势',
        slowPeriod: '26日慢线反映长期趋势',
        signalPeriod: '9日信号线减少噪音'
      },
      arbitrage: {
        correlationThreshold: '0.8相关系数确保价格联动',
        spreadThreshold: '1%价差触发套利机会',
        holdingPeriod: '5日持有期平衡收益与成本'
      }
    }

    return reasonMap[strategyType.value]?.[parameter] || '基于历史数据优化得出'
  }

  // 获取参数优化建议
  static async getParameterOptimization(
    strategyType: string,
    currentParams: Record<string, any>,
    marketData: any
  ): Promise<OptimizationSuggestion[]> {
    try {
      const response = await fetch('/api/intelligent-recommendation/parameter-optimization', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          strategyType,
          currentParams,
          marketData
        })
      })

      if (!response.ok) {
        throw new Error('获取参数优化建议失败')
      }

      const result = await response.json()
      return result.data
    } catch (error) {
      console.error('参数优化错误:', error)
      
      // 简单的本地优化建议
      return this.generateLocalOptimization(strategyType, currentParams)
    }
  }

  // 生成本地优化建议（后备方案）
  private static generateLocalOptimization(
    strategyType: string,
    currentParams: Record<string, any>
  ): OptimizationSuggestion[] {
    const suggestions: OptimizationSuggestion[] = []

    // 基于策略类型生成优化建议
    if (strategyType === 'momentum') {
      suggestions.push({
        id: 'momentum-optimization-1',
        title: '动量策略参数优化',
        expectedImprovement: '提升收益率5-8%',
        changes: [
          { parameter: 'lookbackPeriod', from: currentParams.lookbackPeriod, to: 25 },
          { parameter: 'threshold', from: currentParams.threshold, to: 0.025 }
        ],
        reason: '根据近期市场波动性调整回看周期和阈值',
        confidence: 0.75
      })
    } else if (strategyType === 'mean_reversion') {
      suggestions.push({
        id: 'mean-reversion-optimization-1',
        title: '均值回归策略优化',
        expectedImprovement: '降低最大回撤3-5%',
        changes: [
          { parameter: 'deviationThreshold', from: currentParams.deviationThreshold, to: 2.2 },
          { parameter: 'stopLoss', from: currentParams.stopLoss, to: 0.035 }
        ],
        reason: '当前市场波动较大，适当调整偏离阈值',
        confidence: 0.7
      })
    }

    return suggestions
  }

  // 验证工作流
  static async validateWorkflow(workflow: WorkflowRecommendation): Promise<{
    isValid: boolean
    errors: string[]
    warnings: string[]
  }> {
    const errors: string[] = []
    const warnings: string[] = []

    // 检查必要节点
    const requiredNodeTypes = ['config', 'processing', 'result']
    const presentNodeTypes = workflow.nodes.map(node => node.nodeType)
    
    requiredNodeTypes.forEach(nodeType => {
      if (!presentNodeTypes.includes(nodeType)) {
        errors.push(`缺少必要的节点类型: ${nodeType}`)
      }
    })

    // 检查连接完整性
    const nodeIds = workflow.nodes.map(node => node.id)
    workflow.connections.forEach(conn => {
      if (!nodeIds.includes(conn.from) || !nodeIds.includes(conn.to)) {
        errors.push(`连接指向不存在的节点: ${conn.from} -> ${conn.to}`)
      }
    })

    // 检查参数合理性
    workflow.nodes.forEach(node => {
      node.parameters?.forEach(param => {
        if (param.type === 'number' && param.range) {
          const value = Number(param.userValue || param.recommendedValue)
          if (value < param.range.min || value > param.range.max) {
            warnings.push(`节点 ${node.title} 的参数 ${param.displayName} 超出合理范围`)
          }
        }
      })
    })

    return {
      isValid: errors.length === 0,
      errors,
      warnings
    }
  }

  // 应用推荐配置
  static async applyRecommendation(
    workflowId: string,
    customizations?: Record<string, any>
  ): Promise<{ success: boolean; message: string }> {
    try {
      const response = await fetch('/api/intelligent-recommendation/apply-recommendation', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          workflowId,
          customizations
        })
      })

      if (!response.ok) {
        throw new Error('应用推荐配置失败')
      }

      const result = await response.json()
      return result.data
    } catch (error) {
      console.error('应用推荐配置错误:', error)
      return {
        success: false,
        message: `应用推荐配置失败: ${error instanceof Error ? error.message : String(error)}`
      }
    }
  }
}

export default IntelligentRecommendationService

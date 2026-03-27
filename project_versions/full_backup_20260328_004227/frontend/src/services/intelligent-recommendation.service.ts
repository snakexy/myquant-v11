import { reactive, ref, computed } from 'vue'
import type { 
  StrategyRecommendationRequest, 
  WorkflowRecommendation, 
  ParsedIntent, 
  OptimizationSuggestion,
  ExperienceLevel,
  StrategyType
} from '../api/intelligent-recommendation'

/**
 * 智能推荐服务类
 * 提供智能推荐功能的状态管理和业务逻辑封装
 * 遵循单一职责原则和依赖注入模式
 */

// 推荐状态接口
export interface RecommendationState {
  isLoading: boolean
  currentRecommendation: WorkflowRecommendation | null
  parsedIntent: ParsedIntent | null
  optimizationSuggestions: OptimizationSuggestion[]
  recommendationHistory: WorkflowRecommendation[]
  templates: Array<{
    id: string
    name: string
    description: string
    strategyType: string
    complexity: 'low' | 'medium' | 'high'
    experienceLevel: 'beginner' | 'intermediate' | 'expert'
    template: WorkflowRecommendation
    usageCount: number
    rating: number
  }>
  stats: {
    totalRecommendations: number
    successRate: number
    averageAccuracy: number
    popularStrategies: Array<{
      strategyType: string
      count: number
      percentage: number
    }>
    recentActivity: Array<{
      date: string
      action: string
      strategyType: string
      success: boolean
    }>
  } | null
  error: string | null
}

// 推荐配置接口
export interface RecommendationConfig {
  experienceLevel: ExperienceLevel
  autoOptimization: boolean
  showAdvancedOptions: boolean
  preferredStrategies: string[]
  riskTolerance: 'conservative' | 'moderate' | 'aggressive'
  notificationPreferences: {
    onCompletion: boolean
    onError: boolean
    onOptimization: boolean
  }
}

// 事件类型定义
export interface RecommendationEvents {
  'recommendation-created': WorkflowRecommendation
  'recommendation-updated': WorkflowRecommendation
  'recommendation-applied': { workflowId: string; success: boolean }
  'optimization-completed': OptimizationSuggestion[]
  'error-occurred': { type: string; message: string }
}

// 依赖注入接口
export interface RecommendationDependencies {
  apiClient: {
    parseNaturalLanguage: (input: string) => Promise<ParsedIntent>
    getStrategyRecommendation: (request: StrategyRecommendationRequest) => Promise<WorkflowRecommendation>
    getParameterOptimization: (strategyType: string, currentParams: Record<string, any>, marketData: any) => Promise<OptimizationSuggestion[]>
    validateWorkflow: (workflow: WorkflowRecommendation) => Promise<{ isValid: boolean; errors: string[]; warnings: string[] }>
    applyRecommendation: (workflowId: string, customizations?: Record<string, any>) => Promise<{ success: boolean; message: string }>
  }
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

class IntelligentRecommendationService {
  private static instance: IntelligentRecommendationService
  private dependencies: RecommendationDependencies
  private eventTarget: EventTarget
  
  // 响应式状态
  public state = reactive<RecommendationState>({
    isLoading: false,
    currentRecommendation: null,
    parsedIntent: null,
    optimizationSuggestions: [],
    recommendationHistory: [],
    templates: [],
    stats: null,
    error: null
  })

  // 配置
  public config = reactive<RecommendationConfig>({
    experienceLevel: {
      value: 'intermediate',
      label: '进阶用户',
      icon: '🟡',
      description: '适合有一定经验的用户，提供模板选择和参数优化建议'
    },
    autoOptimization: true,
    showAdvancedOptions: false,
    preferredStrategies: [],
    riskTolerance: 'moderate',
    notificationPreferences: {
      onCompletion: true,
      onError: true,
      onOptimization: false
    }
  })

  // 计算属性
  public get isLoading() {
    return this.state.isLoading
  }

  public get currentRecommendation() {
    return this.state.currentRecommendation
  }

  public get parsedIntent() {
    return this.state.parsedIntent
  }

  public get optimizationSuggestions() {
    return this.state.optimizationSuggestions
  }

  public get recommendationHistory() {
    return this.state.recommendationHistory
  }

  public get templates() {
    return this.state.templates
  }

  public get stats() {
    return this.state.stats
  }

  public get error() {
    return this.state.error
  }

  public get hasCurrentRecommendation() {
    return this.state.currentRecommendation !== null
  }

  public get canOptimize() {
    return this.state.currentRecommendation !== null && this.config.autoOptimization
  }

  // 单例模式
  public static getInstance(dependencies?: RecommendationDependencies): IntelligentRecommendationService {
    if (!IntelligentRecommendationService.instance) {
      IntelligentRecommendationService.instance = new IntelligentRecommendationService(dependencies)
    }
    return IntelligentRecommendationService.instance
  }

  // 私有构造函数，支持依赖注入
  private constructor(dependencies?: RecommendationDependencies) {
    this.eventTarget = new EventTarget()
    
    // 依赖注入，如果没有提供则使用默认实现
    this.dependencies = dependencies || {
      apiClient: {
        parseNaturalLanguage: async (input: string) => {
          // 默认实现：简单的本地解析
          return this.simpleLocalParse(input)
        },
        getStrategyRecommendation: async (request: StrategyRecommendationRequest) => {
          // 默认实现：生成本地推荐
          return this.generateLocalRecommendation(request)
        },
        getParameterOptimization: async (strategyType: string, currentParams: Record<string, any>) => {
          // 默认实现：生成本地优化建议
          return this.generateLocalOptimization(strategyType, currentParams)
        },
        validateWorkflow: async (workflow: WorkflowRecommendation) => {
          // 默认实现：本地验证
          return this.validateWorkflowLocally(workflow)
        },
        applyRecommendation: async (workflowId: string) => {
          // 默认实现：模拟应用
          return { success: true, message: '应用成功' }
        }
      },
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
          console.info(`[IntelligentRecommendationService] ${message}`, ...args)
        },
        error: (message: string, error?: Error | unknown) => {
          console.error(`[IntelligentRecommendationService] ${message}`, error)
        },
        warn: (message: string, ...args: any[]) => {
          console.warn(`[IntelligentRecommendationService] ${message}`, ...args)
        }
      }
    }

    this.loadConfigFromStorage()
    this.loadRecommendationHistory()
  }

  // 自然语言解析
  public async parseNaturalLanguage(input: string): Promise<ParsedIntent | null> {
    this.setLoading(true)
    this.clearError()

    try {
      this.dependencies.logger.info('开始解析自然语言:', input)
      
      const intent = await this.dependencies.apiClient.parseNaturalLanguage(input)
      
      this.state.parsedIntent = intent
      this.saveParsedIntentToStorage(intent)
      this.emitEvent('recommendation-created', intent as any)
      
      this.dependencies.logger.info('自然语言解析完成:', intent)
      return intent
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : '解析失败'
      this.setError(errorMessage)
      this.emitEvent('error-occurred', { type: 'parse-error', message: errorMessage })
      return null
    } finally {
      this.setLoading(false)
    }
  }

  // 获取策略推荐
  public async getStrategyRecommendation(request: StrategyRecommendationRequest): Promise<WorkflowRecommendation | null> {
    this.setLoading(true)
    this.clearError()

    try {
      this.dependencies.logger.info('开始获取策略推荐:', request)
      
      const recommendation = await this.dependencies.apiClient.getStrategyRecommendation(request)
      
      this.state.currentRecommendation = recommendation
      this.saveCurrentRecommendationToStorage(recommendation)
      this.addToHistory(recommendation)
      this.emitEvent('recommendation-created', recommendation)
      
      // 触发自动优化
      if (this.config.autoOptimization) {
        await this.autoOptimize(recommendation)
      }
      
      this.dependencies.logger.info('策略推荐获取完成:', recommendation)
      return recommendation
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : '获取推荐失败'
      this.setError(errorMessage)
      this.emitEvent('error-occurred', { type: 'recommendation-error', message: errorMessage })
      return null
    } finally {
      this.setLoading(false)
    }
  }

  // 获取参数优化建议
  public async getParameterOptimization(
    strategyType: string,
    currentParams: Record<string, any>,
    marketData?: any
  ): Promise<OptimizationSuggestion[]> {
    this.setLoading(true)
    this.clearError()

    try {
      this.dependencies.logger.info('开始获取参数优化建议:', { strategyType, currentParams })
      
      // 如果没有提供市场数据，先获取
      if (!marketData && this.state.currentRecommendation) {
        marketData = await this.getMarketDataForOptimization()
      }

      const suggestions = await this.dependencies.apiClient.getParameterOptimization(strategyType, currentParams, marketData)
      
      this.state.optimizationSuggestions = suggestions
      this.emitEvent('optimization-completed', suggestions)
      
      this.dependencies.logger.info('参数优化建议获取完成:', suggestions)
      return suggestions
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : '获取优化建议失败'
      this.setError(errorMessage)
      this.emitEvent('error-occurred', { type: 'optimization-error', message: errorMessage })
      return []
    } finally {
      this.setLoading(false)
    }
  }

  // 验证工作流
  public async validateWorkflow(workflow: WorkflowRecommendation): Promise<{
    isValid: boolean
    errors: string[]
    warnings: string[]
  }> {
    try {
      this.dependencies.logger.info('开始验证工作流:', workflow)
      
      const result = await this.dependencies.apiClient.validateWorkflow(workflow)
      
      this.dependencies.logger.info('工作流验证完成:', result)
      return result
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : '验证失败'
      this.setError(errorMessage)
      this.emitEvent('error-occurred', { type: 'validation-error', message: errorMessage })
      return {
        isValid: false,
        errors: [errorMessage],
        warnings: []
      }
    }
  }

  // 应用推荐配置
  public async applyRecommendation(
    workflowId: string,
    customizations?: Record<string, any>
  ): Promise<boolean> {
    this.setLoading(true)
    this.clearError()

    try {
      this.dependencies.logger.info('开始应用推荐配置:', { workflowId, customizations })
      
      const result = await this.dependencies.apiClient.applyRecommendation(workflowId, customizations)
      
      if (result.success) {
        this.dependencies.notification.show('推荐配置已成功应用', 'success')
        this.emitEvent('recommendation-applied', { workflowId, success: true })
      } else {
        this.dependencies.notification.show(result.message, 'error')
        this.emitEvent('recommendation-applied', { workflowId, success: false })
      }
      
      this.dependencies.logger.info('推荐配置应用完成:', result)
      return result.success
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : '应用推荐失败'
      this.setError(errorMessage)
      this.emitEvent('error-occurred', { type: 'application-error', message: errorMessage })
      this.dependencies.notification.show('应用推荐失败', 'error')
      return false
    } finally {
      this.setLoading(false)
    }
  }

  // 更新配置
  public updateConfig(newConfig: Partial<RecommendationConfig>): void {
    Object.assign(this.config, newConfig)
    this.saveConfigToStorage()
    this.dependencies.logger.info('配置已更新:', this.config)
  }

  // 清除当前推荐
  public clearCurrentRecommendation(): void {
    this.state.currentRecommendation = null
    this.state.parsedIntent = null
    this.state.optimizationSuggestions = []
    this.clearErrorState()
    this.dependencies.storage.remove('current-recommendation')
    this.dependencies.storage.remove('parsed-intent')
    this.dependencies.logger.info('当前推荐已清除')
  }

  // 清除错误状态
  public clearErrorState(): void {
    this.state.error = null
  }

  // 事件监听
  public addEventListener<K extends keyof RecommendationEvents>(
    event: K,
    listener: (event: CustomEvent<RecommendationEvents[K]>) => void
  ): void {
    this.eventTarget.addEventListener(event, listener as EventListener)
  }

  // 移除事件监听
  public removeEventListener<K extends keyof RecommendationEvents>(
    event: K,
    listener: (event: CustomEvent<RecommendationEvents[K]>) => void
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
    if (error && this.config.notificationPreferences.onError) {
      this.dependencies.notification.show(error, 'error')
    }
  }

  // 私有方法：清除错误
  private clearErrorState(): void {
    this.state.error = null
  }

  // 私有方法：触发事件
  private emitEvent<K extends keyof RecommendationEvents>(
    event: K,
    detail: RecommendationEvents[K]
  ): void {
    this.eventTarget.dispatchEvent(new CustomEvent(event, { detail }))
  }

  // 私有方法：自动优化
  private async autoOptimize(workflow: WorkflowRecommendation): Promise<void> {
    if (!workflow) return

    const strategyType = this.extractStrategyTypeFromWorkflow(workflow)
    const currentParams = this.extractParametersFromWorkflow(workflow)
    
    await this.getParameterOptimization(strategyType, currentParams)
  }

  // 私有方法：简单的本地解析（后备方案）
  private simpleLocalParse(input: string): ParsedIntent {
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

  // 私有方法：生成本地推荐（后备方案）
  private generateLocalRecommendation(request: StrategyRecommendationRequest): WorkflowRecommendation {
    // 这里实现一个简单的本地推荐生成逻辑
    const workflowId = `workflow-${Date.now()}`
    
    return {
      id: workflowId,
      name: `${request.strategyType}回测工作流`,
      description: `基于${request.strategyType}的智能回测工作流`,
      nodes: [],
      connections: [],
      expectedPerformance: {
        accuracy: 0.75 + Math.random() * 0.2,
        sharpeRatio: 1.2 + Math.random() * 0.5,
        maxDrawdown: 0.15 + Math.random() * 0.1,
        annualReturn: 0.15 + Math.random() * 0.1
      },
      complexity: 'medium' as 'low' | 'medium' | 'high',
      estimatedTime: 10,
      experienceLevel: request.experienceLevel
    }
  }

  // 私有方法：生成本地优化建议（后备方案）
  private generateLocalOptimization(strategyType: string, currentParams: Record<string, any>): OptimizationSuggestion[] {
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

  // 私有方法：本地验证（后备方案）
  private validateWorkflowLocally(workflow: WorkflowRecommendation): {
    isValid: boolean
    errors: string[]
    warnings: string[]
  } {
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

    return {
      isValid: errors.length === 0,
      errors,
      warnings
    }
  }

  // 私有方法：获取市场数据用于参数优化
  private async getMarketDataForOptimization(): Promise<any> {
    if (!this.state.currentRecommendation) {
      return null
    }

    // 从当前推荐中提取股票代码和时间范围
    const symbols = this.extractSymbolsFromWorkflow(this.state.currentRecommendation)
    const dateRange = this.extractDateRangeFromWorkflow(this.state.currentRecommendation)

    // 这里应该调用市场数据API，现在返回模拟数据
    return {
      marketData: {},
      volatility: 0.2,
      trend: 'sideways' as 'bull' | 'bear' | 'sideways',
      correlation: {}
    }
  }

  // 私有方法：从工作流中提取股票代码
  private extractSymbolsFromWorkflow(workflow: WorkflowRecommendation): string[] {
    const configNode = workflow.nodes.find(node => node.nodeType === 'config')
    if (configNode && configNode.parameters) {
      const symbolsParam = configNode.parameters.find(p => p.parameter === 'symbols')
      if (symbolsParam && symbolsParam.recommendedValue) {
        return symbolsParam.recommendedValue.split(',').map((s: string) => s.trim())
      }
    }
    return []
  }

  // 私有方法：从工作流中提取时间范围
  private extractDateRangeFromWorkflow(workflow: WorkflowRecommendation): { start: string; end: string } {
    const configNode = workflow.nodes.find(node => node.nodeType === 'config')
    if (configNode && configNode.parameters) {
      const startDateParam = configNode.parameters.find(p => p.parameter === 'startDate')
      const endDateParam = configNode.parameters.find(p => p.parameter === 'endDate')
      
      if (startDateParam?.recommendedValue && endDateParam?.recommendedValue) {
        return {
          start: startDateParam.recommendedValue,
          end: endDateParam.recommendedValue
        }
      }
    }
    return { start: '', end: '' }
  }

  // 私有方法：从工作流中提取策略类型
  private extractStrategyTypeFromWorkflow(workflow: WorkflowRecommendation): string {
    const strategyNode = workflow.nodes.find(node => 
      node.nodeType === 'processing' && node.title.includes('策略')
    )
    if (strategyNode) {
      // 从节点标题中提取策略类型
      if (strategyNode.title.includes('动量')) return 'momentum'
      if (strategyNode.title.includes('均值')) return 'mean_reversion'
      if (strategyNode.title.includes('趋势')) return 'trend_following'
      if (strategyNode.title.includes('套利')) return 'arbitrage'
    }
    return 'custom'
  }

  // 私有方法：从工作流中提取参数
  private extractParametersFromWorkflow(workflow: WorkflowRecommendation): Record<string, any> {
    const params: Record<string, any> = {}
    
    workflow.nodes.forEach(node => {
      if (node.parameters) {
        node.parameters.forEach(param => {
          params[param.parameter] = param.userValue || param.recommendedValue
        })
      }
    })
    
    return params
  }

  // 私有方法：保存配置到本地存储
  private saveConfigToStorage(): void {
    this.dependencies.storage.set('recommendation-config', this.config)
  }

  // 私有方法：从本地存储加载配置
  private loadConfigFromStorage(): void {
    try {
      const saved = this.dependencies.storage.get('recommendation-config')
      if (saved) {
        Object.assign(this.config, saved)
      }
    } catch (error) {
      this.dependencies.logger.error('加载推荐配置失败:', error)
    }
  }

  // 私有方法：保存解析意图到本地存储
  private saveParsedIntentToStorage(intent: ParsedIntent): void {
    try {
      const history = this.dependencies.storage.get('parsed-intent-history') || []
      history.unshift(intent)
      // 只保留最近10条记录
      if (history.length > 10) {
        history.splice(10)
      }
      this.dependencies.storage.set('parsed-intent-history', history)
    } catch (error) {
      this.dependencies.logger.error('保存解析意图失败:', error)
    }
  }

  // 私有方法：保存当前推荐到本地存储
  private saveCurrentRecommendationToStorage(workflow: WorkflowRecommendation): void {
    try {
      this.dependencies.storage.set('current-recommendation', workflow)
    } catch (error) {
      this.dependencies.logger.error('保存当前推荐失败:', error)
    }
  }

  // 私有方法：从本地存储加载推荐历史
  private loadRecommendationHistory(): void {
    try {
      const saved = this.dependencies.storage.get('recommendation-history')
      if (saved) {
        this.state.recommendationHistory = saved
      }
    } catch (error) {
      this.dependencies.logger.error('加载推荐历史失败:', error)
    }
  }

  // 私有方法：添加到历史记录
  private addToHistory(workflow: WorkflowRecommendation): void {
    this.state.recommendationHistory.unshift(workflow)
    // 只保留最近50条记录
    if (this.state.recommendationHistory.length > 50) {
      this.state.recommendationHistory.splice(50)
    }
    
    try {
      this.dependencies.storage.set('recommendation-history', this.state.recommendationHistory)
    } catch (error) {
      this.dependencies.logger.error('保存推荐历史失败:', error)
    }
  }
}

// 导出单例实例
export const intelligentRecommendationService = IntelligentRecommendationService.getInstance()

export default intelligentRecommendationService
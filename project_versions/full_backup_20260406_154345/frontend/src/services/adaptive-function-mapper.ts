import { EventEmitter } from '@/utils/event-emitter'
import { nodeStateManager } from './node-state-manager'
import { workflowManager } from './workflow-manager'
import type { 
  NodeStateInfo, 
  ExtendedNodeStatus, 
  WorkflowContext,
  PerformanceMetrics 
} from '@/types/node-system'

/**
 * 功能节点映射接口
 */
export interface FunctionNodeMapping {
  functionId: string
  functionName: string
  description: string
  icon: string
  category: string
  requiredNodes: string[]
  optionalNodes: string[]
  nodeConnections: NodeConnection[]
  optimizationRules: OptimizationRule[]
  performanceMetrics: FunctionMetrics
  estimatedDuration: number
  complexity: number
}

/**
 * 节点连接定义
 */
export interface NodeConnection {
  fromNode: string
  toNode: string
  connectionType: 'data' | 'control' | 'dependency'
  strength: number
  conditional: boolean
  label?: string
}

/**
 * 优化规则
 */
export interface OptimizationRule {
  id: string
  condition: string
  action: 'add_node' | 'remove_node' | 'modify_connection' | 'optimize_performance'
  targetNode?: string
  priority: number
  description: string
  expectedImprovement: number
}

/**
 * 功能性能指标
 */
export interface FunctionMetrics {
  efficiency: number
  reliability: number
  responseTime: number
  resourceUsage: number
  successRate: number
  lastUpdated: Date
}

/**
 * 使用分析结果
 */
export interface UsageAnalysis {
  efficiency: number
  bottlenecks: Bottleneck[]
  optimizationOpportunities: OptimizationOpportunity[]
  usagePattern: UsagePattern
}

/**
 * 性能瓶颈
 */
export interface Bottleneck {
  nodeId: string
  description: string
  severity: number
  recommendedNode?: string
  expectedImprovement: number
}

/**
 * 优化机会
 */
export interface OptimizationOpportunity {
  type: 'add_node' | 'remove_node' | 'modify_connection'
  targetNode: string
  reason: string
  expectedImprovement: number
  priority: number
}

/**
 * 使用模式
 */
export interface UsagePattern {
  frequency: number
  peakHours: number[]
  averageSessionDuration: number
  commonErrors: string[]
}

/**
 * 节点优化推荐
 */
export interface NodeOptimizationRecommendation {
  type: 'add_node' | 'remove_node' | 'modify_connection' | 'optimize_performance'
  targetNode: string
  reason: string
  expectedImprovement: number
  priority: number
  estimatedCost?: number
  implementationComplexity: number
}

/**
 * 连接结果
 */
export interface ConnectionResult {
  success: boolean
  activatedNodes: string[]
  establishedConnections: NodeConnection[]
  validationErrors: string[]
  performanceBaseline: PerformanceMetrics
}

/**
 * 优化结果
 */
export interface OptimizationResult {
  optimized: boolean
  improvements: NodeOptimizationRecommendation[]
  performanceGain: number
  appliedAt: Date
}

/**
 * 自适应功能映射器
 * 负责管理功能与节点之间的映射关系和自适应优化
 */
export class AdaptiveFunctionMapper extends EventEmitter {
  private functionMappings: Map<string, FunctionNodeMapping> = new Map()
  private activeConnections: Map<string, NodeConnection[]> = new Map()
  private usageHistory: Map<string, UsageAnalysis[]> = new Map()
  private performanceHistory: Map<string, PerformanceMetrics[]> = new Map()

  constructor() {
    super()
    this.initializeFunctionMappings()
  }

  /**
   * 初始化功能节点映射
   */
  private initializeFunctionMappings() {
    // 数据管理功能
    const dataManagementMapping: FunctionNodeMapping = {
      functionId: 'data-management',
      functionName: '数据管理',
      description: '数据获取、清洗、预处理和特征工程',
      icon: '📊',
      category: 'data',
      requiredNodes: [
        'data_hub.data_fetcher',
        'data_hub.data_validator',
        'data_hub.data_cleaner',
        'data_hub.feature_engineer'
      ],
      optionalNodes: [
        'data_hub.data_standardizer',
        'qlib_core.data_processor',
        'data_hub.data_transformer'
      ],
      nodeConnections: [
        {
          fromNode: 'data_hub.data_fetcher',
          toNode: 'data_hub.data_validator',
          connectionType: 'data',
          strength: 1.0,
          conditional: false,
          label: '数据验证'
        },
        {
          fromNode: 'data_hub.data_validator',
          toNode: 'data_hub.data_cleaner',
          connectionType: 'data',
          strength: 0.9,
          conditional: false,
          label: '数据清洗'
        },
        {
          fromNode: 'data_hub.data_cleaner',
          toNode: 'data_hub.feature_engineer',
          connectionType: 'data',
          strength: 0.8,
          conditional: false,
          label: '特征工程'
        }
      ],
      optimizationRules: [
        {
          id: 'high_volume_data',
          condition: 'data_volume > 1000000',
          action: 'add_node',
          targetNode: 'data_hub.data_standardizer',
          priority: 8,
          description: '大数据量时添加数据标准化节点',
          expectedImprovement: 25
        },
        {
          id: 'complex_features',
          condition: 'feature_complexity > 0.8',
          action: 'add_node',
          targetNode: 'qlib_core.data_processor',
          priority: 7,
          description: '复杂特征时添加数据处理节点',
          expectedImprovement: 20
        }
      ],
      performanceMetrics: {
        efficiency: 0.85,
        reliability: 0.92,
        responseTime: 2000,
        resourceUsage: 0.65,
        successRate: 0.94,
        lastUpdated: new Date()
      },
      estimatedDuration: 120000,
      complexity: 3
    }

    // AI策略功能
    const aiStrategyMapping: FunctionNodeMapping = {
      functionId: 'ai-strategy',
      functionName: 'AI策略生成',
      description: '基于AI的量化策略生成和优化',
      icon: '🤖',
      category: 'ai',
      requiredNodes: [
        'ai_strategy.model_trainer',
        'ai_strategy.strategy_generator',
        'business_logic.market_analyzer'
      ],
      optionalNodes: [
        'ai_strategy.hyperparameter_optimizer',
        'ai_strategy.model_validator',
        'ai_strategy.strategy_optimizer',
        'qlib_core.technical_analyzer'
      ],
      nodeConnections: [
        {
          fromNode: 'business_logic.market_analyzer',
          toNode: 'ai_strategy.model_trainer',
          connectionType: 'data',
          strength: 0.9,
          conditional: false,
          label: '市场分析数据'
        },
        {
          fromNode: 'ai_strategy.model_trainer',
          toNode: 'ai_strategy.strategy_generator',
          connectionType: 'control',
          strength: 1.0,
          conditional: false,
          label: '模型控制'
        },
        {
          fromNode: 'ai_strategy.hyperparameter_optimizer',
          toNode: 'ai_strategy.model_trainer',
          connectionType: 'control',
          strength: 0.7,
          conditional: true,
          label: '参数优化'
        }
      ],
      optimizationRules: [
        {
          id: 'high_accuracy_required',
          condition: 'accuracy_requirement > 0.95',
          action: 'add_node',
          targetNode: 'ai_strategy.hyperparameter_optimizer',
          priority: 9,
          description: '高精度要求时添加超参数优化',
          expectedImprovement: 30
        },
        {
          id: 'model_validation_needed',
          condition: 'validation_required == true',
          action: 'add_node',
          targetNode: 'ai_strategy.model_validator',
          priority: 8,
          description: '需要验证时添加模型验证节点',
          expectedImprovement: 25
        }
      ],
      performanceMetrics: {
        efficiency: 0.78,
        reliability: 0.88,
        responseTime: 5000,
        resourceUsage: 0.85,
        successRate: 0.91,
        lastUpdated: new Date()
      },
      estimatedDuration: 300000,
      complexity: 5
    }

    // 传统回测功能
    const backtestMapping: FunctionNodeMapping = {
      functionId: 'traditional-backtest',
      functionName: '传统策略回测',
      description: '基于QLib的传统量化策略回测',
      icon: '📈',
      category: 'backtest',
      requiredNodes: [
        'qlib_core.backtest_executor',
        'qlib_core.strategy_builder',
        'qlib_core.result_analyzer'
      ],
      optionalNodes: [
        'qlib_core.config_parser',
        'qlib_core.task_scheduler',
        'experiment_mgmt.experiment_tracker',
        'qlib_core.report_generator'
      ],
      nodeConnections: [
        {
          fromNode: 'qlib_core.strategy_builder',
          toNode: 'qlib_core.backtest_executor',
          connectionType: 'control',
          strength: 1.0,
          conditional: false,
          label: '策略配置'
        },
        {
          fromNode: 'qlib_core.backtest_executor',
          toNode: 'qlib_core.result_analyzer',
          connectionType: 'data',
          strength: 0.95,
          conditional: false,
          label: '回测结果'
        }
      ],
      optimizationRules: [
        {
          id: 'complex_strategy',
          condition: 'strategy_complexity > 0.7',
          action: 'add_node',
          targetNode: 'qlib_core.config_parser',
          priority: 7,
          description: '复杂策略时添加配置解析器',
          expectedImprovement: 20
        },
        {
          id: 'batch_backtest',
          condition: 'batch_mode == true',
          action: 'add_node',
          targetNode: 'qlib_core.task_scheduler',
          priority: 6,
          description: '批量回测时添加任务调度器',
          expectedImprovement: 35
        }
      ],
      performanceMetrics: {
        efficiency: 0.82,
        reliability: 0.95,
        responseTime: 3000,
        resourceUsage: 0.70,
        successRate: 0.96,
        lastUpdated: new Date()
      },
      estimatedDuration: 180000,
      complexity: 4
    }

    // 实盘交易功能
    const liveTradingMapping: FunctionNodeMapping = {
      functionId: 'live-trading',
      functionName: '实盘交易',
      description: '实时交易执行和风险管理',
      icon: '💰',
      category: 'trading',
      requiredNodes: [
        'live_trading.order_executor',
        'live_trading.market_connector',
        'live_trading.risk_monitor'
      ],
      optionalNodes: [
        'live_trading.position_manager',
        'live_trading.portfolio_manager',
        'live_trading.performance_monitor',
        'live_trading.alert_manager',
        'business_logic.risk_manager'
      ],
      nodeConnections: [
        {
          fromNode: 'live_trading.market_connector',
          toNode: 'live_trading.order_executor',
          connectionType: 'data',
          strength: 1.0,
          conditional: false,
          label: '市场数据'
        },
        {
          fromNode: 'live_trading.risk_monitor',
          toNode: 'live_trading.order_executor',
          connectionType: 'control',
          strength: 0.9,
          conditional: false,
          label: '风险控制'
        }
      ],
      optimizationRules: [
        {
          id: 'high_frequency_trading',
          condition: 'trading_frequency > 100',
          action: 'add_node',
          targetNode: 'live_trading.position_manager',
          priority: 8,
          description: '高频交易时添加持仓管理',
          expectedImprovement: 25
        },
        {
          id: 'portfolio_management',
          condition: 'portfolio_size > 10',
          action: 'add_node',
          targetNode: 'live_trading.portfolio_manager',
          priority: 7,
          description: '大组合时添加组合管理',
          expectedImprovement: 30
        }
      ],
      performanceMetrics: {
        efficiency: 0.88,
        reliability: 0.97,
        responseTime: 500,
        resourceUsage: 0.75,
        successRate: 0.98,
        lastUpdated: new Date()
      },
      estimatedDuration: 60000,
      complexity: 4
    }

    // 注册功能映射
    this.functionMappings.set(dataManagementMapping.functionId, dataManagementMapping)
    this.functionMappings.set(aiStrategyMapping.functionId, aiStrategyMapping)
    this.functionMappings.set(backtestMapping.functionId, backtestMapping)
    this.functionMappings.set(liveTradingMapping.functionId, liveTradingMapping)
  }

  /**
   * 获取所有功能映射
   */
  public getAllFunctionMappings(): FunctionNodeMapping[] {
    return Array.from(this.functionMappings.values())
  }

  /**
   * 获取指定功能映射
   */
  public getFunctionMapping(functionId: string): FunctionNodeMapping | undefined {
    return this.functionMappings.get(functionId)
  }

  /**
   * 建立功能连接
   */
  public async establishFunctionConnections(functionId: string): Promise<ConnectionResult> {
    const mapping = this.functionMappings.get(functionId)
    if (!mapping) {
      throw new Error(`功能 ${functionId} 的节点映射不存在`)
    }

    try {
      // 激活必需节点
      const activationResults = await Promise.all(
        mapping.requiredNodes.map(nodeId => nodeStateManager.activateNode(nodeId))
      )

      // 建立节点连接
      const connections = await this.establishConnections(mapping.nodeConnections)

      // 验证连接完整性
      const validation = await this.validateConnections(connections)

      // 记录活跃连接
      this.activeConnections.set(functionId, connections)

      // 获取性能基线
      const performanceBaseline = await this.collectPerformanceMetrics(mapping.requiredNodes)

      this.emit('function-connections-established', {
        functionId,
        mapping,
        connections,
        performanceBaseline
      })

      return {
        success: validation.isValid,
        activatedNodes: activationResults.filter(r => r.success).map(r => r.nodeId),
        establishedConnections: connections,
        validationErrors: validation.errors,
        performanceBaseline
      }

    } catch (error) {
      this.emit('function-connection-error', { functionId, error })
      throw error
    }
  }

  /**
   * 分析功能使用情况
   */
  public analyzeFunctionUsage(functionId: string): UsageAnalysis {
    const mapping = this.functionMappings.get(functionId)
    if (!mapping) {
      throw new Error(`功能 ${functionId} 的节点映射不存在`)
    }

    const usageHistory = this.usageHistory.get(functionId) || []
    const performanceHistory = this.performanceHistory.get(functionId) || []

    // 计算效率
    const efficiency = this.calculateEfficiency(usageHistory, performanceHistory)

    // 识别瓶颈
    const bottlenecks = this.identifyBottlenecks(mapping, performanceHistory)

    // 查找优化机会
    const optimizationOpportunities = this.findOptimizationOpportunities(mapping, usageHistory)

    // 分析使用模式
    const usagePattern = this.analyzeUsagePattern(usageHistory)

    const analysis: UsageAnalysis = {
      efficiency,
      bottlenecks,
      optimizationOpportunities,
      usagePattern
    }

    this.emit('function-usage-analyzed', { functionId, analysis })
    return analysis
  }

  /**
   * 推荐节点优化
   */
  public recommendNodeOptimizations(functionId: string): NodeOptimizationRecommendation[] {
    const analysis = this.analyzeFunctionUsage(functionId)
    const recommendations: NodeOptimizationRecommendation[] = []

    // 基于性能瓶颈推荐
    analysis.bottlenecks.forEach(bottleneck => {
      recommendations.push({
        type: 'add_node',
        targetNode: bottleneck.recommendedNode || '',
        reason: `解决${bottleneck.description}的性能瓶颈`,
        expectedImprovement: bottleneck.expectedImprovement,
        priority: bottleneck.severity,
        implementationComplexity: this.calculateImplementationComplexity(bottleneck)
      })
    })

    // 基于优化机会推荐
    analysis.optimizationOpportunities.forEach(opportunity => {
      recommendations.push({
        type: opportunity.type,
        targetNode: opportunity.targetNode,
        reason: opportunity.reason,
        expectedImprovement: opportunity.expectedImprovement,
        priority: opportunity.priority,
        implementationComplexity: this.calculateImplementationComplexity(opportunity)
      })
    })

    // 基于使用模式推荐
    if (analysis.usagePattern.frequency > 10) {
      recommendations.push({
        type: 'optimize_performance',
        targetNode: '',
        reason: '高频使用功能，建议性能优化',
        expectedImprovement: 15,
        priority: 6,
        implementationComplexity: 3
      })
    }

    return recommendations.sort((a, b) => b.priority - a.priority)
  }

  /**
   * 为新功能推荐节点
   */
  public recommendNodesForNewFeature(featureDescription: string): FunctionNodeMapping[] {
    const featureAnalysis = this.analyzeFeatureRequirements(featureDescription)
    const similarFunctions = this.findSimilarFunctions(featureAnalysis)

    const recommendations = similarFunctions.map(func => ({
      ...func,
      adaptationReason: this.explainAdaptationReason(featureAnalysis, func)
    }))

    this.emit('new-feature-recommendations', { featureDescription, recommendations })
    return recommendations
  }

  /**
   * 建立节点连接
   */
  private async establishConnections(connections: NodeConnection[]): Promise<NodeConnection[]> {
    const establishedConnections: NodeConnection[] = []

    for (const connection of connections) {
      try {
        // 验证节点状态
        const fromNodeState = nodeStateManager.getNodeState(connection.fromNode)
        const toNodeState = nodeStateManager.getNodeState(connection.toNode)

        if (fromNodeState && toNodeState) {
          // 建立连接逻辑
          establishedConnections.push(connection)
          this.emit('connection-established', connection)
        }
      } catch (error) {
        console.error(`建立连接失败: ${connection.fromNode} -> ${connection.toNode}`, error)
      }
    }

    return establishedConnections
  }

  /**
   * 验证连接
   */
  private async validateConnections(connections: NodeConnection[]): Promise<{ isValid: boolean; errors: string[] }> {
    const errors: string[] = []

    for (const connection of connections) {
      // 检查节点是否存在
      const fromNode = nodeStateManager.getNodeState(connection.fromNode)
      const toNode = nodeStateManager.getNodeState(connection.toNode)

      if (!fromNode) {
        errors.push(`源节点 ${connection.fromNode} 不存在`)
      }

      if (!toNode) {
        errors.push(`目标节点 ${connection.toNode} 不存在`)
      }

      // 检查节点状态
      if (fromNode && fromNode.status === ExtendedNodeStatus.ERROR) {
        errors.push(`源节点 ${connection.fromNode} 处于错误状态`)
      }

      if (toNode && toNode.status === ExtendedNodeStatus.ERROR) {
        errors.push(`目标节点 ${connection.toNode} 处于错误状态`)
      }
    }

    return {
      isValid: errors.length === 0,
      errors
    }
  }

  /**
   * 收集性能指标
   */
  private async collectPerformanceMetrics(nodeIds: string[]): Promise<PerformanceMetrics> {
    const metrics: PerformanceMetrics[] = []

    for (const nodeId of nodeIds) {
      const nodeState = nodeStateManager.getNodeState(nodeId)
      if (nodeState) {
        metrics.push(nodeState.performance)
      }
    }

    // 聚合性能指标
    const avgCpuUsage = metrics.reduce((sum, m) => sum + m.cpuUsage, 0) / metrics.length
    const avgMemoryUsage = metrics.reduce((sum, m) => sum + m.memoryUsage, 0) / metrics.length
    const avgResponseTime = metrics.reduce((sum, m) => sum + m.responseTime, 0) / metrics.length
    const avgThroughput = metrics.reduce((sum, m) => sum + m.throughput, 0) / metrics.length
    const avgErrorRate = metrics.reduce((sum, m) => sum + m.errorRate, 0) / metrics.length
    const avgAvailability = metrics.reduce((sum, m) => sum + m.availability, 0) / metrics.length

    return {
      cpuUsage: avgCpuUsage,
      memoryUsage: avgMemoryUsage,
      responseTime: avgResponseTime,
      throughput: avgThroughput,
      errorRate: avgErrorRate,
      availability: avgAvailability,
      lastHealthCheck: new Date()
    }
  }

  /**
   * 计算效率
   */
  private calculateEfficiency(usageHistory: UsageAnalysis[], performanceHistory: PerformanceMetrics[]): number {
    if (usageHistory.length === 0 || performanceHistory.length === 0) {
      return 0.5
    }

    const avgResponseTime = performanceHistory.reduce((sum, p) => sum + p.responseTime, 0) / performanceHistory.length
    const avgSuccessRate = performanceHistory.reduce((sum, p) => sum + p.availability, 0) / performanceHistory.length

    // 效率 = (成功率 / (1 + 响应时间系数))
    const responseTimeFactor = Math.min(avgResponseTime / 1000, 2) // 响应时间因子，最大为2
    const efficiency = avgSuccessRate / (1 + responseTimeFactor)

    return Math.max(0, Math.min(1, efficiency))
  }

  /**
   * 识别瓶颈
   */
  private identifyBottlenecks(mapping: FunctionNodeMapping, performanceHistory: PerformanceMetrics[]): Bottleneck[] {
    const bottlenecks: Bottleneck[] = []

    if (performanceHistory.length === 0) {
      return bottlenecks
    }

    // 分析每个节点的性能
    for (const nodeId of mapping.requiredNodes) {
      const nodeMetrics = performanceHistory
        .filter(p => p.lastHealthCheck.getTime() > Date.now() - 3600000) // 最近1小时
        .map(p => ({ nodeId, ...p }))

      if (nodeMetrics.length > 0) {
        const avgResponseTime = nodeMetrics.reduce((sum, m) => sum + m.responseTime, 0) / nodeMetrics.length
        const avgErrorRate = nodeMetrics.reduce((sum, m) => sum + m.errorRate, 0) / nodeMetrics.length

        // 检测瓶颈
        if (avgResponseTime > 5000 || avgErrorRate > 0.1) {
          bottlenecks.push({
            nodeId,
            description: avgResponseTime > 5000 ? '响应时间过长' : '错误率过高',
            severity: avgResponseTime > 5000 ? Math.min(avgResponseTime / 1000, 10) : Math.min(avgErrorRate * 50, 10),
            recommendedNode: this.getRecommendedNodeForBottleneck(nodeId),
            expectedImprovement: avgResponseTime > 5000 ? 40 : 30
          })
        }
      }
    }

    return bottlenecks
  }

  /**
   * 查找优化机会
   */
  private findOptimizationOpportunities(mapping: FunctionNodeMapping, usageHistory: UsageAnalysis[]): OptimizationOpportunity[] {
    const opportunities: OptimizationOpportunity[] = []

    // 基于优化规则
    for (const rule of mapping.optimizationRules) {
      if (this.evaluateOptimizationRule(rule)) {
        opportunities.push({
          type: rule.action,
          targetNode: rule.targetNode || '',
          reason: rule.description,
          expectedImprovement: rule.expectedImprovement,
          priority: rule.priority
        })
      }
    }

    // 基于使用模式
    if (usageHistory.length > 5) {
      const avgEfficiency = usageHistory.reduce((sum, u) => sum + u.efficiency, 0) / usageHistory.length
      if (avgEfficiency < 0.7) {
        opportunities.push({
          type: 'optimize_performance',
          targetNode: '',
          reason: '整体效率偏低，建议性能优化',
          expectedImprovement: 25,
          priority: 7
        })
      }
    }

    return opportunities
  }

  /**
   * 分析使用模式
   */
  private analyzeUsagePattern(usageHistory: UsageAnalysis[]): UsagePattern {
    if (usageHistory.length === 0) {
      return {
        frequency: 0,
        peakHours: [],
        averageSessionDuration: 0,
        commonErrors: []
      }
    }

    const frequency = usageHistory.length
    const peakHours = this.calculatePeakHours(usageHistory)
    const averageSessionDuration = this.calculateAverageSessionDuration(usageHistory)
    const commonErrors = this.extractCommonErrors(usageHistory)

    return {
      frequency,
      peakHours,
      averageSessionDuration,
      commonErrors
    }
  }

  /**
   * 分析功能需求
   */
  private analyzeFeatureRequirements(featureDescription: string): any {
    // 简化的需求分析，实际应用中可以使用NLP
    const keywords = this.extractKeywords(featureDescription)
    const categories = this.identifyCategories(keywords)
    const complexity = this.estimateComplexity(keywords, categories)

    return {
      keywords,
      categories,
      complexity,
      description: featureDescription
    }
  }

  /**
   * 查找相似功能
   */
  private findSimilarFunctions(featureAnalysis: any): FunctionNodeMapping[] {
    const allFunctions = Array.from(this.functionMappings.values())
    
    return allFunctions.map(func => ({
      ...func,
      similarity: this.calculateSimilarity(featureAnalysis, func)
    })).sort((a, b) => b.similarity - a.similarity)
  }

  /**
   * 计算相似性
   */
  private calculateSimilarity(featureAnalysis: any, func: FunctionNodeMapping): number {
    // 简化的相似性计算
    const keywordSimilarity = this.calculateKeywordSimilarity(featureAnalysis.keywords, func.functionName)
    const categorySimilarity = featureAnalysis.categories.includes(func.category) ? 1 : 0
    const complexitySimilarity = 1 - Math.abs(featureAnalysis.complexity - func.complexity) / 5

    return (keywordSimilarity * 0.4 + categorySimilarity * 0.3 + complexitySimilarity * 0.3)
  }

  /**
   * 解释适配原因
   */
  private explainAdaptationReason(featureAnalysis: any, func: FunctionNodeMapping): string {
    const reasons: string[] = []

    if (featureAnalysis.categories.includes(func.category)) {
      reasons.push(`功能类别匹配(${func.category})`)
    }

    if (Math.abs(featureAnalysis.complexity - func.complexity) < 1) {
      reasons.push(`复杂度匹配(${func.complexity})`)
    }

    return reasons.join(', ') || '基于功能相似性推荐'
  }

  /**
   * 评估优化规则
   */
  private evaluateOptimizationRule(rule: OptimizationRule): boolean {
    // 简化的规则评估，实际应用中需要更复杂的逻辑
    return Math.random() > 0.5 // 模拟规则触发
  }

  /**
   * 获取瓶颈推荐节点
   */
  private getRecommendedNodeForBottleneck(nodeId: string): string {
    const recommendations: Record<string, string> = {
      'data_hub.data_fetcher': 'data_hub.data_cache',
      'ai_strategy.model_trainer': 'ai_strategy.hyperparameter_optimizer',
      'qlib_core.backtest_executor': 'qlib_core.task_scheduler',
      'live_trading.order_executor': 'live_trading.position_manager'
    }

    return recommendations[nodeId] || ''
  }

  /**
   * 计算实现复杂度
   */
  private calculateImplementationComplexity(bottleneck: Bottleneck | OptimizationOpportunity): number {
    return Math.min(bottleneck.expectedImprovement / 10, 5)
  }

  /**
   * 提取关键词
   */
  private extractKeywords(text: string): string[] {
    // 简化的关键词提取
    return text.toLowerCase().split(/\s+/).filter(word => word.length > 2)
  }

  /**
   * 识别类别
   */
  private identifyCategories(keywords: string[]): string[] {
    const categoryKeywords: Record<string, string[]> = {
      'data': ['数据', 'data', '获取', 'fetch', '清洗', 'clean'],
      'ai': ['ai', '人工智能', '机器学习', '深度学习', '策略', 'strategy'],
      'backtest': ['回测', 'backtest', '测试', 'test', '历史', 'history'],
      'trading': ['交易', 'trading', '实盘', 'live', '订单', 'order']
    }

    const categories: string[] = []
    for (const [category, words] of Object.entries(categoryKeywords)) {
      if (keywords.some(keyword => words.some(word => keyword.includes(word)))) {
        categories.push(category)
      }
    }

    return categories
  }

  /**
   * 估算复杂度
   */
  private estimateComplexity(keywords: string[], categories: string[]): number {
    let complexity = 1

    if (categories.includes('ai')) complexity += 2
    if (categories.includes('trading')) complexity += 1
    if (keywords.some(k => ['实时', 'real-time', '高频', 'high-frequency'].includes(k))) complexity += 1

    return Math.min(complexity, 5)
  }

  /**
   * 计算峰值时间
   */
  private calculatePeakHours(usageHistory: UsageAnalysis[]): number[] {
    // 简化实现，返回常见工作时间
    return [9, 10, 14, 15, 16]
  }

  /**
   * 计算平均会话时长
   */
  private calculateAverageSessionDuration(usageHistory: UsageAnalysis[]): number {
    return 30 // 简化实现，返回30分钟
  }

  /**
   * 提取常见错误
   */
  private extractCommonErrors(usageHistory: UsageAnalysis[]): string[] {
    return ['连接超时', '节点错误', '性能下降'] // 简化实现
  }

  /**
   * 计算关键词相似性
   */
  private calculateKeywordSimilarity(keywords: string[], functionName: string): number {
    const functionWords = functionName.toLowerCase().split(/\s+/)
    const matches = keywords.filter(keyword => 
      functionWords.some(word => word.includes(keyword) || keyword.includes(word))
    )
    
    return matches.length / Math.max(keywords.length, functionWords.length)
  }
}

// 创建单例实例
export const adaptiveFunctionMapper = new AdaptiveFunctionMapper()
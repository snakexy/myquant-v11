import { EventEmitter } from '@/utils/event-emitter'
import { nodeStateManager } from './node-state-manager'
import { ExtendedNodeStatus } from '@/types/node-system'
import type {
  NodeStateInfo,
  WorkflowContext,
  PerformanceMetrics
} from '@/types/node-system'

/**
 * 基于完整数据流程图的架构驱动激活器
 * 
 * 核心理念：连接关系已在架构图中定义好，无非就根据需求按模块依赖关系和架构设计来激活哪些节点而已
 * 
 * 严格按照 docs/05-modules/data-management/data-flow.md 中定义的六层数据流程：
 * 1. 数据源层 → 2. 数据处理层 → 3. 机器学习层 → 4. 策略生成层 → 5. 策略执行层 → 6. 分析监控层
 * 
 * 预定义架构连接
 * 基于完整数据流程图的固定连接关系，不是动态创建连接
 */
export interface ArchitectureConnection {
  id: string
  fromNode: string
  toNode: string
  connectionType: 'data_flow' | 'control_flow' | 'dependency'
  strength: number
  description: string
  layer: string
}

/**
 * 功能模块定义
 * 每个功能对应预定义的节点组合和连接路径
 */
export interface FunctionModule {
  moduleId: string
  moduleName: string
  description: string
  icon: string
  category: string
  requiredNodes: string[]
  activationSequence: string[] // 按依赖关系排序的激活序列
  architecturePath: ArchitectureConnection[] // 预定义的连接路径
  entryPoints: string[] // 入口节点
  exitPoints: string[] // 出口节点
  optimizationNodes: string[] // 可选的优化节点
  estimatedDuration: number
  complexity: number
}

/**
 * 激活状态
 */
export interface ActivationStatus {
  moduleId: string
  moduleName: string
  status: 'activating' | 'completed' | 'failed'
  startTime: number
  endTime?: number
  duration?: number
  currentStep: number
  totalSteps: number
  activatedNodes: string[]
  errors: string[]
  progress: number
}

/**
 * 优化建议
 */
export interface OptimizationSuggestion {
  type: 'add_node' | 'remove_node' | 'modify_connection' | 'optimize_performance'
  targetNode: string
  reason: string
  expectedImprovement: number
  priority: number
  basedOn: 'performance' | 'usage_pattern' | 'architecture_principle'
}

/**
 * 基于架构的激活器
 * 核心理念：连接关系已在架构图中定义好，只需按需激活节点
 */
export class ArchitectureBasedActivator extends EventEmitter {
  private functionModules: Map<string, FunctionModule> = new Map()
  private architectureConnections: ArchitectureConnection[] = []
  private activationStatus: Map<string, ActivationStatus> = new Map()
  private nodeUsageHistory: Map<string, number[]> = new Map()

  constructor() {
    super()
    this.initializeArchitecture()
    this.initializeFunctionModules()
  }

  /**
   * 初始化基于完整数据流程图的架构连接
   * 严格按照 docs/05-modules/data-management/data-flow.md 中定义的数据流向
   */
  private initializeArchitecture() {
    // 数据源层 → 数据处理层 连接
    this.architectureConnections.push(
      {
        id: 'ds_to_dp_1',
        fromNode: 'data_hub.data_fetcher',
        toNode: 'data_hub.data_validator',
        connectionType: 'data_flow',
        strength: 1.0,
        description: '外部数据源 → 数据标准化',
        layer: 'data_source_to_processing'
      },
      {
        id: 'ds_to_dp_2',
        fromNode: 'data_hub.data_validator',
        toNode: 'qlib_core.data_processor',
        connectionType: 'data_flow',
        strength: 1.0,
        description: '数据验证 → QLib数据处理器',
        layer: 'data_source_to_processing'
      }
    )

    // 数据处理层 → 机器学习层 连接
    this.architectureConnections.push(
      {
        id: 'dp_to_ml_1',
        fromNode: 'qlib_core.data_processor',
        toNode: 'qlib_core.technical_analyzer',
        connectionType: 'data_flow',
        strength: 0.9,
        description: '数据处理 → 技术分析',
        layer: 'processing_to_ml'
      },
      {
        id: 'dp_to_ml_2',
        fromNode: 'qlib_core.technical_analyzer',
        toNode: 'qlib_core.model_trainer',
        connectionType: 'data_flow',
        strength: 0.9,
        description: '技术分析 → 模型训练',
        layer: 'processing_to_ml'
      }
    )

    // 机器学习层 → 策略生成层 连接
    this.architectureConnections.push(
      {
        id: 'ml_to_sg_1',
        fromNode: 'qlib_core.model_trainer',
        toNode: 'business_logic.market_analyzer',
        connectionType: 'data_flow',
        strength: 0.8,
        description: '模型训练 → 市场分析',
        layer: 'ml_to_strategy'
      },
      {
        id: 'ml_to_sg_2',
        fromNode: 'business_logic.market_analyzer',
        toNode: 'ai_strategy.model_trainer',
        connectionType: 'data_flow',
        strength: 0.8,
        description: '市场分析 → AI模型训练',
        layer: 'ml_to_strategy'
      }
    )

    // 策略生成层 → 策略执行层 连接
    this.architectureConnections.push(
      {
        id: 'sg_to_se_1',
        fromNode: 'ai_strategy.model_trainer',
        toNode: 'ai_strategy.strategy_generator',
        connectionType: 'data_flow',
        strength: 0.9,
        description: 'AI模型训练 → 策略生成',
        layer: 'strategy_to_execution'
      },
      {
        id: 'sg_to_se_2',
        fromNode: 'ai_strategy.strategy_generator',
        toNode: 'live_trading.risk_monitor',
        connectionType: 'control_flow',
        strength: 0.8,
        description: '策略生成 → 风险监控',
        layer: 'strategy_to_execution'
      }
    )

    // 策略执行层 → 分析监控层 连接
    this.architectureConnections.push(
      {
        id: 'se_to_am_1',
        fromNode: 'live_trading.risk_monitor',
        toNode: 'live_trading.order_executor',
        connectionType: 'control_flow',
        strength: 0.9,
        description: '风险监控 → 订单执行',
        layer: 'execution_to_monitoring'
      },
      {
        id: 'se_to_am_2',
        fromNode: 'live_trading.order_executor',
        toNode: 'experiment_management.performance_analyzer',
        connectionType: 'data_flow',
        strength: 0.8,
        description: '订单执行 → 性能分析',
        layer: 'execution_to_monitoring'
      }
    )

    // 反馈循环连接（基于数据流程图的反馈机制）
    this.architectureConnections.push(
      {
        id: 'feedback_1',
        fromNode: 'experiment_management.performance_analyzer',
        toNode: 'ai_strategy.model_trainer',
        connectionType: 'control_flow',
        strength: 0.7,
        description: '性能分析 → 模型优化（反馈循环）',
        layer: 'feedback_loop'
      },
      {
        id: 'feedback_2',
        fromNode: 'live_trading.risk_monitor',
        toNode: 'business_logic.market_analyzer',
        connectionType: 'control_flow',
        strength: 0.7,
        description: '风险预警 → 策略调整（反馈循环）',
        layer: 'feedback_loop'
      }
    )
  }

  /**
   * 初始化功能模块
   * 基于完整数据流程图的六层架构设计
   */
  private initializeFunctionModules() {
    // 数据管理功能（数据源层 + 数据处理层）
    const dataManagementModule: FunctionModule = {
      moduleId: 'data_management',
      moduleName: '数据管理',
      description: '基于数据流程图的数据源和数据处理层完整流程',
      icon: '📊',
      category: 'data',
      requiredNodes: [
        'data_hub.data_fetcher',
        'data_hub.data_validator', 
        'data_hub.data_cleaner',
        'data_hub.feature_engineer'
      ],
      activationSequence: [
        'data_hub.data_fetcher',      // 1. 外部数据源获取
        'data_hub.data_validator',    // 2. 数据标准化
        'data_hub.data_cleaner',     // 3. 数据清洗
        'data_hub.feature_engineer'  // 4. 特征工程
      ],
      architecturePath: [
        {
          id: 'data_flow_1',
          fromNode: 'data_hub.data_fetcher',
          toNode: 'data_hub.data_validator',
          connectionType: 'data_flow',
          strength: 1.0,
          description: '外部数据源 → 数据标准化',
          layer: 'data_source_to_processing'
        },
        {
          id: 'data_flow_2',
          fromNode: 'data_hub.data_validator',
          toNode: 'data_hub.data_cleaner',
          connectionType: 'data_flow',
          strength: 1.0,
          description: '数据验证 → 数据清洗',
          layer: 'data_processing'
        },
        {
          id: 'data_flow_3',
          fromNode: 'data_hub.data_cleaner',
          toNode: 'data_hub.feature_engineer',
          connectionType: 'data_flow',
          strength: 1.0,
          description: '数据清洗 → 特征工程',
          layer: 'data_processing'
        }
      ],
      entryPoints: ['data_hub.data_fetcher'],
      exitPoints: ['data_hub.feature_engineer'],
      optimizationNodes: ['data_hub.data_cache'],
      estimatedDuration: 30000,
      complexity: 3
    }

    // AI策略生成功能（机器学习层 + 策略生成层）
    const aiStrategyModule: FunctionModule = {
      moduleId: 'ai_strategy_generation',
      moduleName: 'AI策略生成',
      description: '基于数据流程图的机器学习层到策略生成层完整流程',
      icon: '🤖',
      category: 'ai',
      requiredNodes: [
        'qlib_core.data_processor',
        'qlib_core.technical_analyzer',
        'qlib_core.model_trainer',
        'business_logic.market_analyzer',
        'ai_strategy.model_trainer',
        'ai_strategy.strategy_generator'
      ],
      activationSequence: [
        'qlib_core.data_processor',        // 1. 数据处理
        'qlib_core.technical_analyzer',     // 2. 技术分析
        'qlib_core.model_trainer',         // 3. QLib模型训练
        'business_logic.market_analyzer',   // 4. 市场分析
        'ai_strategy.model_trainer',         // 5. AI模型训练
        'ai_strategy.strategy_generator'     // 6. 策略生成
      ],
      architecturePath: [
        {
          id: 'ml_to_strategy_1',
          fromNode: 'qlib_core.data_processor',
          toNode: 'qlib_core.technical_analyzer',
          connectionType: 'data_flow',
          strength: 0.9,
          description: '数据处理 → 技术分析',
          layer: 'processing_to_ml'
        },
        {
          id: 'ml_to_strategy_2',
          fromNode: 'qlib_core.technical_analyzer',
          toNode: 'qlib_core.model_trainer',
          connectionType: 'data_flow',
          strength: 0.9,
          description: '技术分析 → 模型训练',
          layer: 'ml_training'
        },
        {
          id: 'ml_to_strategy_3',
          fromNode: 'qlib_core.model_trainer',
          toNode: 'business_logic.market_analyzer',
          connectionType: 'data_flow',
          strength: 0.8,
          description: '模型训练 → 市场分析',
          layer: 'ml_to_strategy'
        },
        {
          id: 'ml_to_strategy_4',
          fromNode: 'business_logic.market_analyzer',
          toNode: 'ai_strategy.model_trainer',
          connectionType: 'data_flow',
          strength: 0.8,
          description: '市场分析 → AI模型训练',
          layer: 'ai_training'
        },
        {
          id: 'ml_to_strategy_5',
          fromNode: 'ai_strategy.model_trainer',
          toNode: 'ai_strategy.strategy_generator',
          connectionType: 'data_flow',
          strength: 0.9,
          description: 'AI模型训练 → 策略生成',
          layer: 'strategy_generation'
        }
      ],
      entryPoints: ['qlib_core.data_processor'],
      exitPoints: ['ai_strategy.strategy_generator'],
      optimizationNodes: ['ai_strategy.hyperparameter_tuner'],
      estimatedDuration: 120000,
      complexity: 5
    }

    // 传统回测功能（策略执行层的回放部分）
    const backtestModule: FunctionModule = {
      moduleId: 'traditional_backtest',
      moduleName: '传统回测',
      description: '基于数据流程图的传统策略回测流程',
      icon: '📈',
      category: 'backtest',
      requiredNodes: [
        'qlib_core.strategy_builder',
        'qlib_core.backtest_executor',
        'qlib_core.result_analyzer'
      ],
      activationSequence: [
        'qlib_core.strategy_builder',   // 1. 策略构建
        'qlib_core.backtest_executor',  // 2. 回测执行
        'qlib_core.result_analyzer'     // 3. 结果分析
      ],
      architecturePath: [
        {
          id: 'backtest_flow_1',
          fromNode: 'qlib_core.strategy_builder',
          toNode: 'qlib_core.backtest_executor',
          connectionType: 'control_flow',
          strength: 0.9,
          description: '策略构建 → 回测执行',
          layer: 'backtest_execution'
        },
        {
          id: 'backtest_flow_2',
          fromNode: 'qlib_core.backtest_executor',
          toNode: 'qlib_core.result_analyzer',
          connectionType: 'data_flow',
          strength: 0.9,
          description: '回测执行 → 结果分析',
          layer: 'backtest_analysis'
        }
      ],
      entryPoints: ['qlib_core.strategy_builder'],
      exitPoints: ['qlib_core.result_analyzer'],
      optimizationNodes: ['qlib_core.parameter_optimizer'],
      estimatedDuration: 60000,
      complexity: 4
    }

    // 实盘交易功能（策略执行层 + 分析监控层）
    const liveTradingModule: FunctionModule = {
      moduleId: 'live_trading',
      moduleName: '实盘交易',
      description: '基于数据流程图的实盘交易完整流程',
      icon: '💰',
      category: 'trading',
      requiredNodes: [
        'live_trading.risk_monitor',
        'live_trading.order_executor',
        'live_trading.position_manager',
        'experiment_management.performance_analyzer'
      ],
      activationSequence: [
        'live_trading.risk_monitor',      // 1. 风险监控
        'live_trading.order_executor',    // 2. 订单执行
        'live_trading.position_manager',   // 3. 持仓管理
        'experiment_management.performance_analyzer' // 4. 性能分析
      ],
      architecturePath: [
        {
          id: 'trading_flow_1',
          fromNode: 'live_trading.risk_monitor',
          toNode: 'live_trading.order_executor',
          connectionType: 'control_flow',
          strength: 0.9,
          description: '风险监控 → 订单执行',
          layer: 'trading_execution'
        },
        {
          id: 'trading_flow_2',
          fromNode: 'live_trading.order_executor',
          toNode: 'live_trading.position_manager',
          connectionType: 'data_flow',
          strength: 0.8,
          description: '订单执行 → 持仓管理',
          layer: 'position_management'
        },
        {
          id: 'trading_flow_3',
          fromNode: 'live_trading.position_manager',
          toNode: 'experiment_management.performance_analyzer',
          connectionType: 'data_flow',
          strength: 0.8,
          description: '持仓管理 → 性能分析',
          layer: 'performance_monitoring'
        }
      ],
      entryPoints: ['live_trading.risk_monitor'],
      exitPoints: ['experiment_management.performance_analyzer'],
      optimizationNodes: ['live_trading.algorithmic_executor'],
      estimatedDuration: 45000,
      complexity: 5
    }

    // 注册功能模块
    this.functionModules.set(dataManagementModule.moduleId, dataManagementModule)
    this.functionModules.set(aiStrategyModule.moduleId, aiStrategyModule)
    this.functionModules.set(backtestModule.moduleId, backtestModule)
    this.functionModules.set(liveTradingModule.moduleId, liveTradingModule)
  }

  /**
   * 获取所有功能模块
   */
  public getAllFunctionModules(): FunctionModule[] {
    return Array.from(this.functionModules.values())
  }

  /**
   * 获取指定功能模块
   */
  public getFunctionModule(moduleId: string): FunctionModule | undefined {
    return this.functionModules.get(moduleId)
  }

  /**
   * 激活功能模块
   * 严格按照预定义的激活序列执行
   */
  public async activateFunctionModule(moduleId: string): Promise<ActivationStatus> {
    const module = this.functionModules.get(moduleId)
    if (!module) {
      throw new Error(`功能模块 ${moduleId} 不存在`)
    }

    // 初始化激活状态
    const status: ActivationStatus = {
      moduleId,
      moduleName: module.moduleName,
      status: 'activating',
      startTime: Date.now(),
      currentStep: 0,
      totalSteps: module.activationSequence.length,
      activatedNodes: [],
      errors: [],
      progress: 0
    }

    this.activationStatus.set(moduleId, status)
    this.emit('activation-started', { moduleId, status })

    try {
      // 按预定义序列激活节点
      for (let i = 0; i < module.activationSequence.length; i++) {
        const nodeId = module.activationSequence[i]
        
        // 更新当前步骤
        status.currentStep = i + 1
        status.progress = (status.currentStep / status.totalSteps) * 100
        
        this.emit('step-started', { moduleId, nodeId, step: i + 1 })
        
        // 激活节点
        await this.activateNode(nodeId)
        status.activatedNodes.push(nodeId)
        
        // 验证架构连接
        if (i < module.activationSequence.length - 1) {
          const nextNodeId = module.activationSequence[i + 1]
          await this.validateArchitectureConnection(nodeId, nextNodeId)
        }
        
        this.emit('step-completed', { moduleId, nodeId, step: i + 1 })
      }

      // 验证架构完整性
      await this.validateArchitectureIntegrity(moduleId)
      
      status.status = 'completed'
      status.endTime = Date.now()
      status.duration = status.endTime - status.startTime
      
      this.emit('activation-completed', { moduleId, status })
      
    } catch (error) {
      status.status = 'failed'
      status.errors.push(error instanceof Error ? error.message : String(error))
      status.endTime = Date.now()
      
      this.emit('activation-failed', { moduleId, status, error })
    }

    return status
  }

  /**
   * 激活单个节点
   */
  private async activateNode(nodeId: string): Promise<void> {
    // 模拟节点激活过程
    await new Promise(resolve => setTimeout(resolve, 1000 + Math.random() * 2000))
    
    this.emit('node-activated', { nodeId, timestamp: Date.now() })
  }

  /**
   * 验证架构连接
   */
  private async validateArchitectureConnection(fromNode: string, toNode: string): Promise<void> {
    // 模拟连接验证
    await new Promise(resolve => setTimeout(resolve, 500))
    
    this.emit('connection-validated', { fromNode, toNode, timestamp: Date.now() })
  }

  /**
   * 验证架构完整性
   */
  private async validateArchitectureIntegrity(moduleId: string): Promise<void> {
    const module = this.functionModules.get(moduleId)
    
    if (!module) return

    // 验证所有架构连接
    for (const connection of module.architecturePath) {
      await this.validateArchitectureConnection(connection.fromNode, connection.toNode)
    }
    
    this.emit('architecture-validated', { moduleId, timestamp: Date.now() })
  }

  /**
   * 获取激活状态
   */
  public getActivationStatus(moduleId: string): ActivationStatus | undefined {
    return this.activationStatus.get(moduleId)
  }

  /**
   * 获取所有激活状态
   */
  public getAllActivationStatus(): ActivationStatus[] {
    return Array.from(this.activationStatus.values())
  }

  /**
   * 停用功能模块
   */
  public async deactivateFunctionModule(moduleId: string): Promise<void> {
    const module = this.functionModules.get(moduleId)
    const activationStatus = this.activationStatus.get(moduleId)
    
    if (!module || !activationStatus) {
      throw new Error(`功能模块 ${moduleId} 不存在或未激活`)
    }

    try {
      // 按相反顺序停用节点
      const deactivationSequence = [...module.activationSequence].reverse()
      
      for (const nodeId of deactivationSequence) {
        try {
          // 这里应该实现停用逻辑
          console.log(`停用节点: ${nodeId}`)
          this.emit('node-deactivated', { moduleId, nodeId })
        } catch (error) {
          console.error(`停用节点 ${nodeId} 失败:`, error)
        }
      }

      // 清除激活状态
      this.activationStatus.delete(moduleId)
      this.emit('module-deactivated', { moduleId })

    } catch (error) {
      this.emit('module-deactivation-error', { moduleId, error })
      throw error
    }
  }

  /**
   * 分析优化机会
   * 基于架构原理和使用模式分析优化建议
   */
  public analyzeOptimizationOpportunities(moduleId: string): OptimizationSuggestion[] {
    const module = this.functionModules.get(moduleId)
    const activationStatus = this.activationStatus.get(moduleId)
    
    if (!module) {
      return []
    }

    const suggestions: OptimizationSuggestion[] = []

    // 基于性能分析
    if (activationStatus) {
      const performanceSuggestions = this.analyzePerformanceOptimizations(module, activationStatus)
      suggestions.push(...performanceSuggestions)
    }

    // 基于使用模式分析
    const usageSuggestions = this.analyzeUsagePatternOptimizations(module)
    suggestions.push(...usageSuggestions)

    // 基于架构原理分析
    const architectureSuggestions = this.analyzeArchitectureOptimizations(module)
    suggestions.push(...architectureSuggestions)

    return suggestions.sort((a, b) => b.priority - a.priority)
  }

  /**
   * 分析性能优化
   */
  private analyzePerformanceOptimizations(module: FunctionModule, activationStatus: ActivationStatus): OptimizationSuggestion[] {
    const suggestions: OptimizationSuggestion[] = []

    // 检查是否有节点性能不佳
    for (const nodeId of activationStatus.activatedNodes) {
      const nodeState = nodeStateManager.getNodeState(nodeId)
      
      if (nodeState && nodeState.performance.responseTime > 5000) {
        suggestions.push({
          type: 'optimize_performance',
          targetNode: nodeId,
          reason: `节点 ${nodeState.name} 响应时间过长`,
          expectedImprovement: 25,
          priority: 8,
          basedOn: 'performance'
        })
      }

      if (nodeState && nodeState.performance.errorRate > 0.1) {
        suggestions.push({
          type: 'optimize_performance',
          targetNode: nodeId,
          reason: `节点 ${nodeState.name} 错误率过高`,
          expectedImprovement: 30,
          priority: 9,
          basedOn: 'performance'
        })
      }
    }

    return suggestions
  }

  /**
   * 分析使用模式优化
   */
  private analyzeUsagePatternOptimizations(module: FunctionModule): OptimizationSuggestion[] {
    const suggestions: OptimizationSuggestion[] = []
    const usageHistory = this.nodeUsageHistory.get(module.moduleId) || []

    if (usageHistory.length > 10) {
      // 高频使用，建议添加优化节点
      suggestions.push({
        type: 'add_node',
        targetNode: module.optimizationNodes[0] || '',
        reason: '高频使用功能，建议添加优化节点',
        expectedImprovement: 20,
        priority: 7,
        basedOn: 'usage_pattern'
      })
    }

    return suggestions
  }

  /**
   * 分析架构优化
   */
  private analyzeArchitectureOptimizations(module: FunctionModule): OptimizationSuggestion[] {
    const suggestions: OptimizationSuggestion[] = []

    // 基于架构原理的优化建议
    if (module.complexity > 4) {
      // 复杂功能，建议添加辅助节点
      suggestions.push({
        type: 'add_node',
        targetNode: module.optimizationNodes[1] || '',
        reason: '复杂功能建议添加辅助节点以提高稳定性',
        expectedImprovement: 15,
        priority: 6,
        basedOn: 'architecture_principle'
      })
    }

    return suggestions
  }

  /**
   * 记录节点使用
   */
  public recordNodeUsage(moduleId: string, nodeId: string): void {
    const history = this.nodeUsageHistory.get(moduleId) || []
    history.push(Date.now())
    this.nodeUsageHistory.set(moduleId, history)
  }

  /**
   * 获取架构连接
   */
  public getArchitectureConnections(): ArchitectureConnection[] {
    return this.architectureConnections
  }

  /**
   * 获取模块的架构路径
   */
  public getModuleArchitecturePath(moduleId: string): ArchitectureConnection[] {
    const module = this.functionModules.get(moduleId)
    return module ? module.architecturePath : []
  }

  /**
   * 系统优化 - 为电路板组件提供智能优化功能
   * 基于当前系统状态和架构原理推荐最佳节点配置
   */
  public async optimizeSystemActivation(context: WorkflowContext): Promise<{
    recommendedNodes: string[]
    optimizationReasons: string[]
    expectedImprovement: number
    priority: number
  }> {
    const allNodes = Array.from(nodeStateManager.getAllNodeStates().values())
    const activeNodes = allNodes.filter(n =>
      n.status === ExtendedNodeStatus.ACTIVE || n.status === ExtendedNodeStatus.RUNNING
    )
    
    const recommendations: string[] = []
    const reasons: string[] = []
    let totalImprovement = 0

    // 1. 基于系统负载的优化
    const systemLoad = context.systemState.systemLoad || 0
    if (systemLoad > 80) {
      // 高负载时建议停用非关键节点
      const nonCriticalNodes = allNodes.filter(n =>
        n.priority < 5 && (n.status === ExtendedNodeStatus.ACTIVE || n.status === ExtendedNodeStatus.RUNNING)
      )
      recommendations.push(...nonCriticalNodes.map(n => n.id))
      reasons.push('高负载系统，建议停用非关键节点以降低负载')
      totalImprovement += 20
    } else if (systemLoad < 30) {
      // 低负载时建议激活优化节点
      const optimizationNodes = allNodes.filter(n =>
        n.status === ExtendedNodeStatus.RECOMMENDED || n.status === ExtendedNodeStatus.STANDBY
      )
      recommendations.push(...optimizationNodes.slice(0, 3).map(n => n.id))
      reasons.push('低负载系统，建议激活推荐节点以提高效率')
      totalImprovement += 15
    }

    // 2. 基于架构原理的优化
    const architectureOptimizations = this.analyzeArchitecturePrinciples(allNodes)
    recommendations.push(...architectureOptimizations.nodes)
    reasons.push(...architectureOptimizations.reasons)
    totalImprovement += architectureOptimizations.improvement

    // 3. 基于使用模式的优化
    const usageOptimizations = this.analyzeUsagePatterns(context)
    recommendations.push(...usageOptimizations.nodes)
    reasons.push(...usageOptimizations.reasons)
    totalImprovement += usageOptimizations.improvement

    // 4. 基于性能指标的优化
    const performanceOptimizations = this.analyzePerformanceMetrics(allNodes)
    recommendations.push(...performanceOptimizations.nodes)
    reasons.push(...performanceOptimizations.reasons)
    totalImprovement += performanceOptimizations.improvement

    // 去重并排序推荐
    const uniqueRecommendations = [...new Set(recommendations)]
    const priority = this.calculateOptimizationPriority(totalImprovement, systemLoad)

    return {
      recommendedNodes: uniqueRecommendations,
      optimizationReasons: reasons,
      expectedImprovement: Math.min(totalImprovement, 50), // 限制最大改进幅度
      priority
    }
  }

  /**
   * 基于架构原理分析优化机会
   */
  private analyzeArchitecturePrinciples(allNodes: NodeStateInfo[]): {
    nodes: string[]
    reasons: string[]
    improvement: number
  } {
    const nodes: string[] = []
    const reasons: string[] = []
    let improvement = 0

    // 检查数据流程完整性
    const dataHubNodes = allNodes.filter(n => n.metadata.layer === 'data_hub')
    const activeDataHubNodes = dataHubNodes.filter(n =>
      n.status === 'ACTIVE' || n.status === 'RUNNING'
    )

    if (activeDataHubNodes.length === 0 && dataHubNodes.length > 0) {
      // 建议激活数据中枢节点
      nodes.push(dataHubNodes[0].id)
      reasons.push('数据中枢是系统基础，建议激活以确保数据流程完整性')
      improvement += 10
    }

    // 检查关键路径节点
    const criticalPathNodes = [
      'data_hub.data_fetcher',
      'qlib_core.data_processor',
      'ai_strategy.model_trainer',
      'live_trading.order_executor'
    ]

    for (const nodeId of criticalPathNodes) {
      const node = allNodes.find(n => n.id === nodeId)
      if (node && node.status === ExtendedNodeStatus.INACTIVE) {
        nodes.push(nodeId)
        reasons.push(`关键路径节点 ${node.name} 未激活，建议激活以确保核心功能`)
        improvement += 8
      }
    }

    return { nodes, reasons, improvement }
  }

  /**
   * 基于使用模式分析优化机会
   */
  private analyzeUsagePatterns(context: WorkflowContext): {
    nodes: string[]
    reasons: string[]
    improvement: number
  } {
    const nodes: string[] = []
    const reasons: string[] = []
    let improvement = 0

    // 基于用户级别的优化
    if (context.userLevel === 'expert') {
      // 专家用户建议激活高级功能
      const advancedNodes = [
        'ai_strategy.hyperparameter_tuner',
        'live_trading.algorithmic_executor',
        'experiment_management.experiment_tracker'
      ]
      nodes.push(...advancedNodes)
      reasons.push('专家用户，建议激活高级功能以充分利用系统能力')
      improvement += 12
    } else if (context.userLevel === 'beginner') {
      // 初级用户建议激活基础功能
      const basicNodes = [
        'data_hub.data_fetcher',
        'qlib_core.data_processor',
        'frontend.data_visualizer'
      ]
      nodes.push(...basicNodes)
      reasons.push('初级用户，建议激活基础功能以简化操作')
      improvement += 8
    }

    // 基于当前工作流的优化
    if (context.currentWorkflow) {
      const workflowNodes = this.getWorkflowRecommendations(context.currentWorkflow)
      nodes.push(...workflowNodes)
      reasons.push(`基于当前工作流 ${context.currentWorkflow} 的优化建议`)
      improvement += 10
    }

    return { nodes, reasons, improvement }
  }

  /**
   * 基于性能指标分析优化机会
   */
  private analyzePerformanceMetrics(allNodes: NodeStateInfo[]): {
    nodes: string[]
    reasons: string[]
    improvement: number
  } {
    const nodes: string[] = []
    const reasons: string[] = []
    let improvement = 0

    // 检查高错误率节点
    const highErrorNodes = allNodes.filter(n =>
      n.performance.errorRate > 0.1 && (n.status === ExtendedNodeStatus.ACTIVE || n.status === ExtendedNodeStatus.RUNNING)
    )

    for (const node of highErrorNodes) {
      // 建议重启高错误率节点
      nodes.push(node.id)
      reasons.push(`节点 ${node.name} 错误率过高，建议重启或检查配置`)
      improvement += 15
    }

    // 检查低性能节点
    const lowPerformanceNodes = allNodes.filter(n =>
      n.performance.responseTime > 3000 && (n.status === ExtendedNodeStatus.ACTIVE || n.status === ExtendedNodeStatus.RUNNING)
    )

    for (const node of lowPerformanceNodes) {
      // 建议优化低性能节点
      nodes.push(node.id)
      reasons.push(`节点 ${node.name} 响应时间过长，建议优化或增加资源`)
      improvement += 12
    }

    // 检查高可用性节点
    const highAvailabilityNodes = allNodes.filter(n =>
      n.performance.availability > 0.95 && n.status === ExtendedNodeStatus.INACTIVE
    )

    if (highAvailabilityNodes.length > 0) {
      // 建议激活高可用性节点
      nodes.push(highAvailabilityNodes[0].id)
      reasons.push(`发现高可用性节点 ${highAvailabilityNodes[0].name}，建议激活以提高系统稳定性`)
      improvement += 8
    }

    return { nodes, reasons, improvement }
  }

  /**
   * 获取工作流推荐节点
   */
  private getWorkflowRecommendations(workflowId: string): string[] {
    const workflowMap: Record<string, string[]> = {
      'data-management': [
        'data_hub.data_fetcher',
        'data_hub.data_validator',
        'data_hub.data_cleaner',
        'data_hub.feature_engineer'
      ],
      'ai-strategy': [
        'qlib_core.technical_analyzer',
        'ai_strategy.model_trainer',
        'ai_strategy.strategy_generator'
      ],
      'backtest': [
        'qlib_core.strategy_builder',
        'qlib_core.backtest_executor',
        'qlib_core.result_analyzer'
      ],
      'live-trading': [
        'live_trading.risk_monitor',
        'live_trading.order_executor',
        'live_trading.position_manager'
      ]
    }

    return workflowMap[workflowId] || []
  }

  /**
   * 计算优化优先级
   */
  private calculateOptimizationPriority(improvement: number, systemLoad: number): number {
    let priority = improvement

    // 系统负载调整
    if (systemLoad > 80) {
      priority += 20 // 高负载时提高优先级
    } else if (systemLoad < 30) {
      priority += 10 // 低负载时适度提高优先级
    }

    // 确保优先级在合理范围内
    return Math.max(1, Math.min(10, Math.round(priority / 10)))
  }

  /**
   * 批量激活节点 - 为电路板组件提供批量操作
   */
  public async batchActivateNodes(nodeIds: string[]): Promise<{
    success: string[]
    failed: { nodeId: string; error: string }[]
  }> {
    const success: string[] = []
    const failed: { nodeId: string; error: string }[] = []

    // 按依赖关系排序
    const sortedNodes = this.sortNodesByDependencies(nodeIds)

    for (const nodeId of sortedNodes) {
      try {
        await nodeStateManager.activateNode(nodeId)
        success.push(nodeId)
        this.emit('node-batch-activated', { nodeId, timestamp: Date.now() })
      } catch (error) {
        failed.push({
          nodeId,
          error: error instanceof Error ? error.message : String(error)
        })
      }
    }

    return { success, failed }
  }

  /**
   * 批量停用节点 - 为电路板组件提供批量操作
   */
  public async batchDeactivateNodes(nodeIds: string[]): Promise<{
    success: string[]
    failed: { nodeId: string; error: string }[]
  }> {
    const success: string[] = []
    const failed: { nodeId: string; error: string }[] = []

    // 按相反依赖关系排序
    const sortedNodes = this.sortNodesByDependencies(nodeIds).reverse()

    for (const nodeId of sortedNodes) {
      try {
        // 模拟停用节点
        await new Promise(resolve => setTimeout(resolve, 500))
        success.push(nodeId)
        this.emit('node-batch-deactivated', { nodeId, timestamp: Date.now() })
      } catch (error) {
        failed.push({
          nodeId,
          error: error instanceof Error ? error.message : String(error)
        })
      }
    }

    return { success, failed }
  }

  /**
   * 按依赖关系排序节点
   */
  private sortNodesByDependencies(nodeIds: string[]): string[] {
    const allNodes = Array.from(nodeStateManager.getAllNodeStates().values())
    const nodeMap = new Map(allNodes.map(n => [n.id, n]))
    
    // 拓扑排序
    const sorted: string[] = []
    const visited = new Set<string>()
    const visiting = new Set<string>()

    const visit = (nodeId: string) => {
      if (visiting.has(nodeId)) {
        throw new Error(`检测到循环依赖: ${nodeId}`)
      }
      if (visited.has(nodeId)) {
        return
      }

      visiting.add(nodeId)
      const node = nodeMap.get(nodeId)
      if (node) {
        for (const depId of (node as any).dependencies || []) {
          if (nodeIds.includes(depId)) {
            visit(depId)
          }
        }
      }
      visiting.delete(nodeId)
      visited.add(nodeId)
      sorted.push(nodeId)
    }

    for (const nodeId of nodeIds) {
      if (!visited.has(nodeId)) {
        visit(nodeId)
      }
    }

    return sorted
  }

  /**
   * 获取系统健康状态 - 为电路板状态栏提供数据
   */
  public getSystemHealthStatus(): {
    overallHealth: number
    activeNodes: number
    totalNodes: number
    errorCount: number
    warnings: string[]
    recommendations: string[]
  } {
    const allNodes = Array.from(nodeStateManager.getAllNodeStates().values())
    const activeNodes = allNodes.filter(n =>
      n.status === ExtendedNodeStatus.ACTIVE || n.status === ExtendedNodeStatus.RUNNING
    )
    const errorNodes = allNodes.filter(n => n.status === ExtendedNodeStatus.ERROR)
    
    const overallHealth = allNodes.length > 0
      ? (activeNodes.length / allNodes.length) * 100
      : 0

    const warnings: string[] = []
    const recommendations: string[] = []

    if (overallHealth < 50) {
      warnings.push('系统健康状态较低，建议检查关键节点')
      recommendations.push('激活关键路径节点以提高系统健康度')
    }

    if (errorNodes.length > 0) {
      warnings.push(`发现 ${errorNodes.length} 个错误节点`)
      recommendations.push('检查并修复错误节点')
    }

    return {
      overallHealth: Math.round(overallHealth),
      activeNodes: activeNodes.length,
      totalNodes: allNodes.length,
      errorCount: errorNodes.length,
      warnings,
      recommendations
    }
  }
}

// 创建单例实例
export const architectureBasedActivator = new ArchitectureBasedActivator()
import { EventEmitter } from '@/utils/event-emitter'
import { nodeStateManager } from './node-state-manager'
import { nodeIdMapper } from './node-id-mapper'
import { ExtendedNodeStatus } from '@/types/node-system'
import type {
  WorkflowDefinition,
  WorkflowStep,
  WorkflowExecution,
  WorkflowContext,
  NodeStateInfo,
  ArchitectureConnection,
  DataFlowLayer
} from '@/types/node-system'

/**
 * 工作流程管理器
 *
 * 基于系统工作流文档的四大核心工作流程实现：
 * 1. AI策略生成工作流程 - 从数据获取到AI策略生成的完整流程
 * 2. 模型训练与部署工作流程 - 机器学习模型训练到部署的完整流程
 * 3. 传统回测工作流程 - 基于QLib的传统策略回测流程
 * 4. 实盘交易工作流程 - 从策略到实盘交易的完整流程
 *
 * 核心设计理念：
 * - 连接关系已在架构图中定义好，只需按需激活节点
 * - 基于模块依赖关系和架构设计来激活节点
 * - 支持步骤依赖、并行执行、回滚机制
 *
 * 基于文档：
 * - docs/02-architecture/system-design/system-workflow.md
 * - docs/05-modules/data-management/data-flow.md
 * - docs/02-architecture/project-architecture/架构关系详解.md
 */
export class WorkflowManager extends EventEmitter {
  private workflows: Map<string, WorkflowDefinition> = new Map()
  private executions: Map<string, WorkflowExecution> = new Map()
  private executionQueue: Array<{ workflowId: string; priority: number }> = []
  private isProcessingQueue = false

  constructor() {
    super()
    this.initializeWorkflows()
  }

  /**
   * 初始化四大核心工作流程
   */
  private initializeWorkflows() {
    // AI策略生成工作流程
    const aiStrategyWorkflow: WorkflowDefinition = {
      id: 'ai-strategy-generation',
      name: 'AI策略生成流程',
      description: '从数据获取到AI策略生成的完整流程',
      category: 'ai-strategy',
      estimatedDuration: 300000, // 5分钟
      steps: [
        {
          id: 'data-acquisition',
          name: '数据获取',
          description: '获取市场数据和基础数据',
          nodeIds: [
            'data_hub.data_fetcher',
            'data_hub.data_validator',
            'data_hub.data_cleaner'
          ],
          estimatedDuration: 30000,
          dependencies: [],
          parallel: true,
          required: true
        },
        {
          id: 'data-preprocessing',
          name: '数据预处理',
          description: '数据清洗、特征工程和标准化',
          nodeIds: [
            'data_hub.feature_engineer',
            'data_hub.data_standardizer',
            'qlib_core.data_processor'
          ],
          estimatedDuration: 45000,
          dependencies: ['data-acquisition'],
          parallel: false,
          required: true
        },
        {
          id: 'market-analysis',
          name: '市场分析',
          description: '技术分析和基本面分析',
          nodeIds: [
            'qlib_core.technical_analyzer',
            'qlib_core.fundamental_analyzer',
            'business_logic.market_analyzer'
          ],
          estimatedDuration: 60000,
          dependencies: ['data-preprocessing'],
          parallel: true,
          required: true
        },
        {
          id: 'ai-model-training',
          name: 'AI模型训练',
          description: '训练AI策略模型',
          nodeIds: [
            'ai_strategy.model_trainer',
            'ai_strategy.hyperparameter_optimizer',
            'ai_strategy.model_validator'
          ],
          estimatedDuration: 120000,
          dependencies: ['market-analysis'],
          parallel: false,
          required: true
        },
        {
          id: 'strategy-generation',
          name: '策略生成',
          description: '生成最终交易策略',
          nodeIds: [
            'ai_strategy.strategy_generator',
            'ai_strategy.strategy_optimizer',
            'business_logic.strategy_generator'
          ],
          estimatedDuration: 45000,
          dependencies: ['ai-model-training'],
          parallel: false,
          required: true
        }
      ],
      successCriteria: {
        minCompletedSteps: 5,
        maxFailedSteps: 0,
        maxExecutionTime: 600000,
        requiredNodes: [
          'ai_strategy.strategy_generator',
          'ai_strategy.model_trainer'
        ]
      },
      rollbackPlan: {
        enabled: true,
        rollbackSteps: ['strategy-generation', 'ai-model-training'],
        cleanupNodes: ['ai_strategy.model_trainer', 'ai_strategy.strategy_generator']
      }
    }

    // 模型训练与部署工作流程
    const modelTrainingWorkflow: WorkflowDefinition = {
      id: 'model-training-deployment',
      name: '模型训练与部署流程',
      description: '机器学习模型训练到部署的完整流程',
      category: 'model-management',
      estimatedDuration: 600000, // 10分钟
      steps: [
        {
          id: 'data-preparation',
          name: '数据准备',
          description: '准备训练数据和验证数据',
          nodeIds: [
            'data_hub.data_fetcher',
            'data_hub.data_splitter',
            'data_hub.feature_engineer'
          ],
          estimatedDuration: 60000,
          dependencies: [],
          parallel: true,
          required: true
        },
        {
          id: 'model-training',
          name: '模型训练',
          description: '训练机器学习模型',
          nodeIds: [
            'ai_strategy.model_trainer',
            'ai_strategy.hyperparameter_optimizer',
            'qlib_core.model_trainer'
          ],
          estimatedDuration: 300000,
          dependencies: ['data-preparation'],
          parallel: false,
          required: true
        },
        {
          id: 'model-validation',
          name: '模型验证',
          description: '验证模型性能和准确性',
          nodeIds: [
            'ai_strategy.model_validator',
            'qlib_core.model_validator',
            'business_logic.model_validator'
          ],
          estimatedDuration: 120000,
          dependencies: ['model-training'],
          parallel: true,
          required: true
        },
        {
          id: 'model-deployment',
          name: '模型部署',
          description: '部署模型到生产环境',
          nodeIds: [
            'ai_strategy.model_deployer',
            'live_trading.model_deployer',
            'frontend.model_manager'
          ],
          estimatedDuration: 60000,
          dependencies: ['model-validation'],
          parallel: false,
          required: true
        },
        {
          id: 'deployment-validation',
          name: '部署验证',
          description: '验证部署后的模型性能',
          nodeIds: [
            'live_trading.performance_monitor',
            'live_trading.system_monitor',
            'experiment_mgmt.experiment_tracker'
          ],
          estimatedDuration: 60000,
          dependencies: ['model-deployment'],
          parallel: true,
          required: false
        }
      ],
      successCriteria: {
        minCompletedSteps: 4,
        maxFailedSteps: 1,
        maxExecutionTime: 900000,
        requiredNodes: [
          'ai_strategy.model_trainer',
          'ai_strategy.model_deployer'
        ]
      },
      rollbackPlan: {
        enabled: true,
        rollbackSteps: ['model-deployment', 'model-validation'],
        cleanupNodes: ['ai_strategy.model_deployer', 'live_trading.model_deployer']
      }
    }

    // 传统策略回测工作流程
    const backtestWorkflow: WorkflowDefinition = {
      id: 'traditional-backtest',
      name: '传统策略回测流程',
      description: '基于QLib的传统策略回测流程',
      category: 'backtest',
      estimatedDuration: 180000, // 3分钟
      steps: [
        {
          id: 'strategy-definition',
          name: '策略定义',
          description: '定义回测策略参数',
          nodeIds: [
            'business_logic.strategy_generator',
            'qlib_core.strategy_builder'
          ],
          estimatedDuration: 30000,
          dependencies: [],
          parallel: false,
          required: true
        },
        {
          id: 'backtest-setup',
          name: '回测设置',
          description: '配置回测环境和参数',
          nodeIds: [
            'qlib_core.backtest_executor',
            'qlib_core.config_parser',
            'experiment_mgmt.experiment_tracker'
          ],
          estimatedDuration: 30000,
          dependencies: ['strategy-definition'],
          parallel: true,
          required: true
        },
        {
          id: 'backtest-execution',
          name: '回测执行',
          description: '执行策略回测',
          nodeIds: [
            'qlib_core.backtest_executor',
            'qlib_core.task_scheduler',
            'qlib_core.workflow_manager'
          ],
          estimatedDuration: 60000,
          dependencies: ['backtest-setup'],
          parallel: false,
          required: true
        },
        {
          id: 'result-analysis',
          name: '结果分析',
          description: '分析回测结果和性能指标',
          nodeIds: [
            'qlib_core.result_analyzer',
            'business_logic.performance_analyzer',
            'experiment_mgmt.experiment_tracker'
          ],
          estimatedDuration: 30000,
          dependencies: ['backtest-execution'],
          parallel: true,
          required: true
        },
        {
          id: 'report-generation',
          name: '报告生成',
          description: '生成回测报告',
          nodeIds: [
            'qlib_core.report_generator',
            'frontend.data_visualizer',
            'experiment_mgmt.experiment_tracker'
          ],
          estimatedDuration: 30000,
          dependencies: ['result-analysis'],
          parallel: false,
          required: false
        }
      ],
      successCriteria: {
        minCompletedSteps: 4,
        maxFailedSteps: 1,
        maxExecutionTime: 300000,
        requiredNodes: [
          'qlib_core.backtest_executor',
          'qlib_core.result_analyzer'
        ]
      },
      rollbackPlan: {
        enabled: true,
        rollbackSteps: ['report-generation', 'result-analysis'],
        cleanupNodes: ['qlib_core.report_generator', 'frontend.data_visualizer']
      }
    }

    // 实盘交易工作流程
    const liveTradingWorkflow: WorkflowDefinition = {
      id: 'live-trading',
      name: '实盘交易流程',
      description: '从策略到实盘交易的完整流程',
      category: 'live-trading',
      estimatedDuration: 120000, // 2分钟
      steps: [
        {
          id: 'strategy-validation',
          name: '策略验证',
          description: '验证策略的有效性和风险',
          nodeIds: [
            'business_logic.risk_manager',
            'business_logic.strategy_validator',
            'live_trading.risk_monitor'
          ],
          estimatedDuration: 30000,
          dependencies: [],
          parallel: true,
          required: true
        },
        {
          id: 'trading-setup',
          name: '交易设置',
          description: '配置交易环境和参数',
          nodeIds: [
            'live_trading.order_manager',
            'live_trading.position_manager',
            'live_trading.portfolio_manager'
          ],
          estimatedDuration: 30000,
          dependencies: ['strategy-validation'],
          parallel: true,
          required: true
        },
        {
          id: 'market-connectivity',
          name: '市场连接',
          description: '建立与市场的连接',
          nodeIds: [
            'live_trading.market_connector',
            'live_trading.data_streamer',
            'live_trading.latency_monitor'
          ],
          estimatedDuration: 15000,
          dependencies: ['trading-setup'],
          parallel: false,
          required: true
        },
        {
          id: 'trading-execution',
          name: '交易执行',
          description: '执行实时交易',
          nodeIds: [
            'live_trading.order_executor',
            'live_trading.signal_processor',
            'live_trading.trade_executor'
          ],
          estimatedDuration: 30000,
          dependencies: ['market-connectivity'],
          parallel: false,
          required: true
        },
        {
          id: 'monitoring-alerting',
          name: '监控告警',
          description: '监控交易状态和发送告警',
          nodeIds: [
            'live_trading.performance_monitor',
            'live_trading.system_monitor',
            'live_trading.alert_manager'
          ],
          estimatedDuration: 15000,
          dependencies: ['trading-execution'],
          parallel: true,
          required: false
        }
      ],
      successCriteria: {
        minCompletedSteps: 4,
        maxFailedSteps: 0,
        maxExecutionTime: 180000,
        requiredNodes: [
          'live_trading.order_executor',
          'live_trading.market_connector'
        ]
      },
      rollbackPlan: {
        enabled: true,
        rollbackSteps: ['trading-execution', 'market-connectivity'],
        cleanupNodes: ['live_trading.order_executor', 'live_trading.market_connector']
      }
    }

    // 注册工作流程
    this.workflows.set(aiStrategyWorkflow.id, aiStrategyWorkflow)
    this.workflows.set(modelTrainingWorkflow.id, modelTrainingWorkflow)
    this.workflows.set(backtestWorkflow.id, backtestWorkflow)
    this.workflows.set(liveTradingWorkflow.id, liveTradingWorkflow)
  }

  /**
   * 获取所有工作流程定义
   */
  public getAllWorkflows(): WorkflowDefinition[] {
    return Array.from(this.workflows.values())
  }

  /**
   * 获取指定工作流程定义
   */
  public getWorkflow(workflowId: string): WorkflowDefinition | undefined {
    return this.workflows.get(workflowId)
  }

  /**
   * 执行工作流程
   */
  public async executeWorkflow(
    workflowId: string, 
    context: WorkflowContext,
    priority: number = 5
  ): Promise<string> {
    const workflow = this.workflows.get(workflowId)
    if (!workflow) {
      throw new Error(`工作流程 ${workflowId} 不存在`)
    }

    const executionId = `${workflowId}-${Date.now()}`
    const execution: WorkflowExecution = {
      id: executionId,
      workflowId,
      status: 'running',
      startTime: new Date(),
      context,
      completedPhases: [],
      errors: [],
      priority,
      metadata: {
        estimatedDuration: workflow.estimatedDuration || 0,
        actualDuration: 0,
        resourceUsage: {
          cpuUsage: 0,
          memoryUsage: 0,
          networkIO: 0
        },
        errorCount: 0,
        warningCount: 0
      }
    }

    this.executions.set(executionId, execution)
    
    // 添加到执行队列
    this.executionQueue.push({ workflowId, priority })
    this.executionQueue.sort((a, b) => b.priority - a.priority)
    
    // 处理队列
    this.processExecutionQueue()
    
    this.emit('workflow-started', execution)
    
    return executionId
  }

  /**
   * 处理执行队列
   */
  private async processExecutionQueue() {
    if (this.isProcessingQueue || this.executionQueue.length === 0) {
      return
    }

    this.isProcessingQueue = true

    while (this.executionQueue.length > 0) {
      const { workflowId } = this.executionQueue.shift()!
      const execution = Array.from(this.executions.values())
        .find(e => e.workflowId === workflowId && e.status === 'running')
      
      if (execution) {
        await this.executeWorkflowSteps(execution)
      }
    }

    this.isProcessingQueue = false
  }

  /**
   * 执行工作流程步骤
   */
  private async executeWorkflowSteps(execution: WorkflowExecution) {
    const workflow = this.workflows.get(execution.workflowId)
    if (!workflow || !workflow.steps) {
      return
    }

    try {
      for (const step of workflow.steps) {
        // 检查依赖
        if (!this.checkStepDependencies(step, workflow.steps)) {
          continue
        }

        // 执行步骤
        await this.executeStep(step, execution)
      }

      // 标记完成
      execution.status = 'completed'
      execution.endTime = new Date()
      if (execution.metadata) {
        execution.metadata.actualDuration = execution.endTime.getTime() - execution.startTime.getTime()
      }

    } catch (error) {
      execution.status = 'failed'
      execution.endTime = new Date()
      if (execution.metadata) {
        execution.metadata.errorCount++
      }
      
      // 执行回滚
      if (workflow.rollbackPlan?.enabled) {
        await this.executeRollback(execution, workflow)
      }
    }

    this.emit('workflow-completed', execution)
  }

  /**
   * 检查步骤依赖
   */
  private checkStepDependencies(step: WorkflowStep, allSteps: WorkflowStep[]): boolean {
    return step.dependencies.every(depId => {
      const depStep = allSteps.find(s => s.id === depId)
      return depStep !== undefined
    })
  }

  /**
   * 执行单个步骤
   */
  private async executeStep(step: WorkflowStep, execution: WorkflowExecution) {
    try {
      // 激活步骤中的所有节点，使用节点ID映射
      const nodePromises = step.nodeIds.map(nodeId => {
        // 使用节点ID映射服务转换节点ID
        const mappedNodeId = nodeIdMapper.mapWorkflowToStateManager(nodeId)
        console.log(`映射节点ID: ${nodeId} -> ${mappedNodeId}`)
        return nodeStateManager.activateNode(mappedNodeId)
      })
      
      await Promise.all(nodePromises)
      
      // 等待步骤完成（模拟）
      await new Promise(resolve => setTimeout(resolve, step.estimatedDuration))
      
      // 检查节点状态，使用映射后的节点ID
      const allNodesCompleted = step.nodeIds.every(nodeId => {
        const mappedNodeId = nodeIdMapper.mapWorkflowToStateManager(nodeId)
        const nodeState = nodeStateManager.getNodeState(mappedNodeId)
        return nodeState && (
          nodeState.status === ExtendedNodeStatus.COMPLETED ||
          nodeState.status === ExtendedNodeStatus.ACTIVE
        )
      })

      if (!allNodesCompleted) {
        execution.errors.push(`步骤 ${step.name} 中的部分节点执行失败`)
      }

    } catch (error) {
      execution.errors.push(`步骤 ${step.name} 执行失败: ${error instanceof Error ? error.message : '未知错误'}`)
    }
  }

  /**
   * 执行回滚
   */
  private async executeRollback(execution: WorkflowExecution, workflow: WorkflowDefinition) {
    const rollbackPlan = workflow.rollbackPlan
    if (!rollbackPlan) return
    
    this.emit('rollback-started', execution)

    try {
      // 停用回滚步骤中的节点
      if (rollbackPlan.rollbackSteps) {
        for (const stepId of rollbackPlan.rollbackSteps) {
          const step = workflow.steps?.find(s => s.id === stepId)
          if (step) {
            for (const nodeId of step.nodeIds) {
              // 这里应该实现停用逻辑
              console.log('停用节点:', nodeId)
            }
          }
        }
      }

      // 清理节点
      if (rollbackPlan.cleanupNodes) {
        for (const nodeId of rollbackPlan.cleanupNodes) {
          // 这里应该实现清理逻辑
          console.log('清理节点:', nodeId)
        }
      }

      this.emit('rollback-completed', execution)

    } catch (error) {
      this.emit('rollback-failed', execution, error)
    }
  }

  /**
   * 获取执行状态
   */
  public getExecutionStatus(executionId: string): WorkflowExecution | undefined {
    return this.executions.get(executionId)
  }

  /**
   * 获取所有执行状态
   */
  public getAllExecutions(): WorkflowExecution[] {
    return Array.from(this.executions.values())
  }

  /**
   * 取消执行
   */
  public async cancelExecution(executionId: string): Promise<void> {
    const execution = this.executions.get(executionId)
    if (!execution) {
      throw new Error(`执行 ${executionId} 不存在`)
    }

    if (execution.status === 'running') {
      execution.status = 'failed'
      execution.endTime = new Date()
      
      this.emit('workflow-cancelled', execution)
    }
  }

  /**
   * 获取工作流程统计
   */
  public getWorkflowStats(): {
    totalWorkflows: number
    runningExecutions: number
    completedExecutions: number
    failedExecutions: number
    queuedExecutions: number
  } {
    const executions = Array.from(this.executions.values())
    
    return {
      totalWorkflows: this.workflows.size,
      runningExecutions: executions.filter(e => e.status === 'running').length,
      completedExecutions: executions.filter(e => e.status === 'completed').length,
      failedExecutions: executions.filter(e => e.status === 'failed').length,
      queuedExecutions: this.executionQueue.length
    }
  }

  /**
   * 清理完成的执行
   */
  public cleanupCompletedExecutions(olderThanHours: number = 24): void {
    const cutoffTime = new Date(Date.now() - olderThanHours * 60 * 60 * 1000)
    
    for (const [executionId, execution] of this.executions.entries()) {
      if (
        execution.endTime && 
        execution.endTime < cutoffTime &&
        ['completed', 'failed'].includes(execution.status)
      ) {
        this.executions.delete(executionId)
      }
    }
  }

  /**
   * 基于架构连接执行工作流程
   * 核心理念：连接关系已在架构图中定义好，只需按需激活节点
   */
  public async executeWorkflowWithArchitecture(
    workflowId: string,
    context: WorkflowContext,
    architectureConnections: ArchitectureConnection[],
    priority: number = 5
  ): Promise<string> {
    const workflow = this.workflows.get(workflowId)
    if (!workflow) {
      throw new Error(`工作流程 ${workflowId} 不存在`)
    }

    const executionId = `${workflowId}-arch-${Date.now()}`
    const execution: WorkflowExecution = {
      id: executionId,
      workflowId,
      status: 'running',
      startTime: new Date(),
      context,
      completedPhases: [],
      errors: [],
      priority,
      metadata: {
        estimatedDuration: workflow.estimatedDuration || 0,
        actualDuration: 0,
        resourceUsage: {
          cpuUsage: 0,
          memoryUsage: 0,
          networkIO: 0
        },
        errorCount: 0,
        warningCount: 0
      }
    }

    this.executions.set(executionId, execution)
    
    // 添加到执行队列
    this.executionQueue.push({ workflowId, priority })
    this.executionQueue.sort((a, b) => b.priority - a.priority)
    
    // 处理队列
    this.processExecutionQueue()
    
    this.emit('workflow-architecture-started', execution, architectureConnections)
    
    return executionId
  }

  /**
   * 基于数据流程层执行工作流程
   */
  public async executeWorkflowWithDataFlow(
    workflowId: string,
    context: WorkflowContext,
    dataFlowLayers: DataFlowLayer[],
    priority: number = 5
  ): Promise<string> {
    const workflow = this.workflows.get(workflowId)
    if (!workflow) {
      throw new Error(`工作流程 ${workflowId} 不存在`)
    }

    const executionId = `${workflowId}-dataflow-${Date.now()}`
    const execution: WorkflowExecution = {
      id: executionId,
      workflowId,
      status: 'running',
      startTime: new Date(),
      context,
      completedPhases: [],
      errors: [],
      priority,
      metadata: {
        estimatedDuration: workflow.estimatedDuration || 0,
        actualDuration: 0,
        resourceUsage: {
          cpuUsage: 0,
          memoryUsage: 0,
          networkIO: 0
        },
        errorCount: 0,
        warningCount: 0
      }
    }

    this.executions.set(executionId, execution)
    
    // 按数据流程层级顺序执行
    await this.executeDataFlowLayers(execution, dataFlowLayers, workflow)
    
    this.emit('workflow-dataflow-completed', execution, dataFlowLayers)
    
    return executionId
  }

  /**
   * 执行数据流程层级
   */
  private async executeDataFlowLayers(
    execution: WorkflowExecution,
    dataFlowLayers: DataFlowLayer[],
    workflow: WorkflowDefinition
  ) {
    try {
      // 按层级顺序执行
      for (const layer of dataFlowLayers.sort((a, b) => a.level - b.level)) {
        execution.currentPhase = layer.id
        
        // 激活输入节点
        if (layer.inputNodes.length > 0) {
          await this.activateNodesInSequence(layer.inputNodes, execution)
        }
        
        // 激活处理节点
        if (layer.processingNodes.length > 0) {
          await this.activateNodesInParallel(layer.processingNodes, execution)
        }
        
        // 激活输出节点
        if (layer.outputNodes.length > 0) {
          await this.activateNodesInSequence(layer.outputNodes, execution)
        }
        
        execution.completedPhases.push(layer.id)
        this.emit('layer-completed', execution, layer)
      }
      
      execution.status = 'completed'
      execution.endTime = new Date()
      if (execution.metadata) {
        execution.metadata.actualDuration = execution.endTime.getTime() - execution.startTime.getTime()
      }
      
    } catch (error) {
      execution.status = 'failed'
      execution.endTime = new Date()
      execution.errors.push(`数据流程执行失败: ${error instanceof Error ? error.message : '未知错误'}`)
      
      if (execution.metadata) {
        execution.metadata.errorCount++
      }
    }
  }

  /**
   * 按序列激活节点
   */
  private async activateNodesInSequence(nodeIds: string[], execution: WorkflowExecution) {
    for (const nodeId of nodeIds) {
      try {
        const mappedNodeId = nodeIdMapper.mapWorkflowToStateManager(nodeId)
        console.log(`序列激活节点映射: ${nodeId} -> ${mappedNodeId}`)
        await nodeStateManager.activateNode(mappedNodeId)
        this.emit('node-activated-in-sequence', execution, mappedNodeId)
      } catch (error) {
        execution.errors.push(`节点 ${nodeId} 激活失败: ${error instanceof Error ? error.message : '未知错误'}`)
      }
    }
  }

  /**
   * 并行激活节点
   */
  private async activateNodesInParallel(nodeIds: string[], execution: WorkflowExecution) {
    try {
      const activationPromises = nodeIds.map(nodeId => {
        const mappedNodeId = nodeIdMapper.mapWorkflowToStateManager(nodeId)
        console.log(`并行激活节点映射: ${nodeId} -> ${mappedNodeId}`)
        return nodeStateManager.activateNode(mappedNodeId).then(() => {
          this.emit('node-activated-in-parallel', execution, mappedNodeId)
          return mappedNodeId
        }).catch(error => {
          execution.errors.push(`节点 ${nodeId} 并行激活失败: ${error instanceof Error ? error.message : '未知错误'}`)
          return null
        })
      })
      
      await Promise.all(activationPromises)
    } catch (error) {
      execution.errors.push(`并行节点激活失败: ${error instanceof Error ? error.message : '未知错误'}`)
    }
  }

  /**
   * 获取工作流程的架构连接
   */
  public getWorkflowArchitectureConnections(workflowId: string): ArchitectureConnection[] {
    const workflow = this.workflows.get(workflowId)
    if (!workflow || !workflow.steps) {
      return []
    }

    const connections: ArchitectureConnection[] = []
    
    // 基于工作流程步骤生成架构连接
    for (let i = 0; i < workflow.steps.length; i++) {
      const step = workflow.steps[i]
      
      // 步骤内部连接
      for (let j = 0; j < step.nodeIds.length - 1; j++) {
        connections.push({
          id: `${step.id}-internal-${j}`,
          from: step.nodeIds[j],
          to: step.nodeIds[j + 1],
          type: 'data',
          strength: 0.8,
          description: `步骤 ${step.name} 内部数据流`,
          bidirectional: false
        })
      }
      
      // 步骤间连接
      if (i < workflow.steps.length - 1) {
        const nextStep = workflow.steps[i + 1]
        connections.push({
          id: `${step.id}-to-${nextStep.id}`,
          from: step.nodeIds[step.nodeIds.length - 1],
          to: nextStep.nodeIds[0],
          type: 'control',
          strength: 0.9,
          description: `从 ${step.name} 到 ${nextStep.name} 的控制流`,
          bidirectional: false
        })
      }
    }
    
    return connections
  }

  /**
   * 获取工作流程的数据流程层
   */
  public getWorkflowDataFlowLayers(workflowId: string): DataFlowLayer[] {
    const workflow = this.workflows.get(workflowId)
    if (!workflow || !workflow.steps) {
      return []
    }

    const layers: DataFlowLayer[] = []
    
    // 基于工作流程步骤生成数据流程层
    workflow.steps.forEach((step, index) => {
      const layer: DataFlowLayer = {
        id: `layer-${step.id}`,
        name: step.name,
        description: step.description,
        level: index + 1,
        nodes: step.nodeIds,
        connections: [],
        inputNodes: step.dependencies.length > 0 ? [step.nodeIds[0]] : [],
        outputNodes: [step.nodeIds[step.nodeIds.length - 1]],
        processingNodes: step.nodeIds.slice(1, -1)
      }
      
      layers.push(layer)
    })
    
    return layers
  }

  /**
   * 验证架构连接的完整性
   */
  public validateArchitectureConnections(
    connections: ArchitectureConnection[],
    availableNodes: string[]
  ): { valid: boolean; errors: string[] } {
    const errors: string[] = []
    const nodeSet = new Set(availableNodes)
    
    for (const connection of connections) {
      // 检查源节点是否存在
      if (!nodeSet.has(connection.from)) {
        errors.push(`连接 ${connection.id} 的源节点 ${connection.from} 不存在`)
      }
      
      // 检查目标节点是否存在
      if (!nodeSet.has(connection.to)) {
        errors.push(`连接 ${connection.id} 的目标节点 ${connection.to} 不存在`)
      }
      
      // 检查连接强度
      if (connection.strength < 0 || connection.strength > 1) {
        errors.push(`连接 ${connection.id} 的强度 ${connection.strength} 无效，应在0-1之间`)
      }
    }
    
    return {
      valid: errors.length === 0,
      errors
    }
  }

  /**
   * 优化工作流程执行路径
   */
  public optimizeWorkflowExecution(
    workflowId: string,
    architectureConnections: ArchitectureConnection[]
  ): { optimizedPath: string[]; optimizations: string[] } {
    const workflow = this.workflows.get(workflowId)
    if (!workflow || !workflow.steps) {
      return { optimizedPath: [], optimizations: [] }
    }

    const optimizations: string[] = []
    const optimizedPath: string[] = []
    
    // 分析连接强度，优化执行顺序
    const connectionMap = new Map<string, ArchitectureConnection[]>()
    
    for (const connection of architectureConnections) {
      if (!connectionMap.has(connection.from)) {
        connectionMap.set(connection.from, [])
      }
      connectionMap.get(connection.from)!.push(connection)
    }
    
    // 基于连接强度重新排序节点
    for (const step of workflow.steps) {
      for (const nodeId of step.nodeIds) {
        const connections = connectionMap.get(nodeId) || []
        const strongConnections = connections.filter(c => c.strength > 0.7)
        
        if (strongConnections.length > 0) {
          optimizedPath.push(nodeId)
          optimizations.push(`节点 ${nodeId} 基于 ${strongConnections.length} 个强连接优化`)
        } else {
          optimizedPath.push(nodeId)
        }
      }
    }
    
    return { optimizedPath, optimizations }
  }
}

// 创建单例实例
export const workflowManager = new WorkflowManager()
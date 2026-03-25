import type {
  NodeStateInfo,
  RecommendationContext,
  DynamicNodeRecommendation,
  NodeStateChangedEvent,
  NodeActivatedEvent,
  NodeErrorEvent
} from '@/types/node-system';
import { ExtendedNodeStatus, APIStatus } from '@/types/node-system';
import { apiMonitor } from './api-monitor';
import { NodeConnectionsManager } from './node-connections';

// 智能节点状态管理器
export class IntelligentNodeStateManager {
  private nodes: Map<string, NodeStateInfo> = new Map();
  private eventListeners: Map<string, Function[]> = new Map();
  
  constructor() {
    this.setupEventSystem();
    this.initializeNodes();
  }
  
  // 设置事件系统
  private setupEventSystem(): void {
    this.eventListeners.set('node-state-changed', []);
    this.eventListeners.set('node-activated', []);
    this.eventListeners.set('node-error', []);
    this.eventListeners.set('states-updated', []);
  }
  
  // 初始化节点
  private initializeNodes(): void {
    const nodeDefinitions = this.getNodeDefinitions();
    
    for (const nodeDef of nodeDefinitions) {
      const node: NodeStateInfo = {
        ...nodeDef,
        status: ExtendedNodeStatus.INACTIVE,
        previousStatus: ExtendedNodeStatus.INACTIVE,
        canActivate: false,
        isRecommended: false,
        priority: 0,
        dependencies: nodeDef.dependencies || [],
        dependents: [],
        apiStatus: APIStatus.CHECKING,
        performance: {
          cpuUsage: 0,
          memoryUsage: 0,
          responseTime: 0,
          throughput: 0,
          errorRate: 0,
          availability: 0,
          lastHealthCheck: new Date()
        },
        bounds: {
          x: this.calculateNodePosition(nodeDef.id, nodeDef.metadata.layer).x,
          y: this.calculateNodePosition(nodeDef.id, nodeDef.metadata.layer).y,
          width: 160,
          height: 100
        },
        lastUpdated: new Date(),
        activationComplexity: nodeDef.metadata.complexity || 1,
        x: this.calculateNodePosition(nodeDef.id, nodeDef.metadata.layer).x,
        y: this.calculateNodePosition(nodeDef.id, nodeDef.metadata.layer).y,
        width: 160,
        height: 100,
        ports: this.generateNodePorts(nodeDef.id, nodeDef.metadata.layer)
      };
      
      this.nodes.set(node.id, node);
    }
    
    // 构建依赖关系
    this.buildDependencies();
    
    console.log(`已初始化 ${this.nodes.size} 个节点`);
  }
  
  // 计算节点位置
  private calculateNodePosition(nodeId: string, layer: string): { x: number; y: number } {
    const layerPositions: Record<string, { baseX: number; baseY: number; spacing: number; nodesPerRow: number }> = {
      'data_hub': { baseX: 100, baseY: 100, spacing: 180, nodesPerRow: 6 },
      'business_logic': { baseX: 100, baseY: 250, spacing: 180, nodesPerRow: 6 },
      'investment_analysis': { baseX: 100, baseY: 400, spacing: 180, nodesPerRow: 6 },
      'ai_strategy': { baseX: 100, baseY: 550, spacing: 180, nodesPerRow: 8 },
      'live_trading': { baseX: 100, baseY: 700, spacing: 180, nodesPerRow: 8 },
      'experiment_mgmt': { baseX: 100, baseY: 850, spacing: 180, nodesPerRow: 6 },
      'application_service': { baseX: 100, baseY: 1000, spacing: 180, nodesPerRow: 6 }
    };
    
    const layerNodes = this.getNodeDefinitions().filter(n => n.metadata.layer === layer);
    const nodeIndex = layerNodes.findIndex(n => n.id === nodeId);
    
    const position = layerPositions[layer] || { baseX: 100, baseY: 100, spacing: 180, nodesPerRow: 6 };
    
    const row = Math.floor(nodeIndex / position.nodesPerRow);
    const col = nodeIndex % position.nodesPerRow;
    
    return {
      x: position.baseX + (col * position.spacing),
      y: position.baseY + (row * 120)
    };
  }
  
  // 生成节点端口
  private generateNodePorts(nodeId: string, layer: string): any[] {
    const ports = [];
    
    // 输入端口
    ports.push({
      id: `${nodeId}-input`,
      type: 'input',
      active: false,
      style: {
        left: '-3px',
        top: '50%',
        transform: 'translateY(-50%)'
      }
    });
    
    // 输出端口
    ports.push({
      id: `${nodeId}-output`,
      type: 'output',
      active: false,
      style: {
        right: '-3px',
        top: '50%',
        transform: 'translateY(-50%)'
      }
    });
    
    return ports;
  }
  
  // 获取节点定义
  private getNodeDefinitions(): any[] {
    return [
      // 数据中枢层
      {
        id: 'DH1',
        name: 'QuantDataHub核心',
        metadata: {
          description: '数据中枢核心模块',
          icon: '📊',
          complexity: 3,
          estimatedTime: 2000,
          category: 'data',
          tags: ['core', 'data-hub'],
          layer: 'data_hub' as any,
          apiEndpoints: [
            { id: 'dh1-overview', url: '/api/v1/data/overview', method: 'GET' as any, timeout: 5000, retryCount: 3, healthCheckInterval: 30000, expectedResponseTime: 1000 }
          ]
        },
        dependencies: []
      },
      {
        id: 'DH2',
        name: '统一数据提供器',
        metadata: {
          description: '统一数据查询接口',
          icon: '🔧',
          complexity: 2,
          estimatedTime: 1500,
          category: 'data',
          tags: ['data', 'provider'],
          layer: 'data_hub' as any,
          apiEndpoints: [
            { id: 'dh2-query', url: '/api/v1/data/query', method: 'POST' as any, timeout: 10000, retryCount: 3, healthCheckInterval: 30000, expectedResponseTime: 2000 }
          ]
        },
        dependencies: ['DH1']
      },
      {
        id: 'DH3',
        name: '缓存管理器',
        metadata: {
          description: '数据缓存管理',
          icon: '📥',
          complexity: 2,
          estimatedTime: 1000,
          category: 'data',
          tags: ['cache', 'management'],
          layer: 'data_hub' as any,
          apiEndpoints: [
            { id: 'dh3-update', url: '/api/v1/data/update', method: 'POST' as any, timeout: 15000, retryCount: 2, healthCheckInterval: 60000, expectedResponseTime: 5000 }
          ]
        },
        dependencies: ['DH1']
      },
      {
        id: 'DH4',
        name: '数据管道',
        metadata: {
          description: '数据管道处理',
          icon: '🔍',
          complexity: 3,
          estimatedTime: 2500,
          category: 'data',
          tags: ['pipeline', 'search'],
          layer: 'data_hub' as any,
          apiEndpoints: [
            { id: 'dh4-symbols', url: '/api/v1/data/symbols/search', method: 'GET' as any, timeout: 8000, retryCount: 3, healthCheckInterval: 30000, expectedResponseTime: 1500 }
          ]
        },
        dependencies: ['DH1', 'DH2']
      },
      {
        id: 'DH5',
        name: '存储管理器',
        metadata: {
          description: '存储管理服务',
          icon: '💾',
          complexity: 2,
          estimatedTime: 1200,
          category: 'data',
          tags: ['storage', 'health'],
          layer: 'data_hub' as any,
          apiEndpoints: [
            { id: 'dh5-health', url: '/api/v1/data/health', method: 'GET' as any, timeout: 3000, retryCount: 3, healthCheckInterval: 15000, expectedResponseTime: 800 }
          ]
        },
        dependencies: ['DH1']
      },
      
      // QLib核心接口层
      {
        id: 'QL1',
        name: '数据处理模块',
        metadata: {
          description: 'QLib数据处理核心',
          icon: '🔌',
          complexity: 4,
          estimatedTime: 3000,
          category: 'analysis',
          tags: ['qlib', 'processing'],
          layer: 'qlib_core' as any,
          apiEndpoints: [
            { id: 'ql1-data-processing', url: '/api/v1/qlib_core/data_processing', method: 'POST' as any, timeout: 10000, retryCount: 3, healthCheckInterval: 30000, expectedResponseTime: 2000 }
          ]
        },
        dependencies: ['DH1', 'DH2']
      },
      {
        id: 'QL2',
        name: '分析系统集成',
        metadata: {
          description: 'QLib分析工具集成',
          icon: '⚙️',
          complexity: 3,
          estimatedTime: 2500,
          category: 'analysis',
          tags: ['qlib', 'analysis'],
          layer: 'qlib_core' as any,
          apiEndpoints: [
            { id: 'ql2-analysis', url: '/api/v1/qlib_core/analysis', method: 'POST' as any, timeout: 15000, retryCount: 2, healthCheckInterval: 45000, expectedResponseTime: 3000 }
          ]
        },
        dependencies: ['DH1']
      },
      {
        id: 'QL3',
        name: '回测系统',
        metadata: {
          description: 'QLib回测引擎',
          icon: '🔄',
          complexity: 5,
          estimatedTime: 5000,
          category: 'backtest',
          tags: ['qlib', 'backtest'],
          layer: 'qlib_core' as any,
          apiEndpoints: [
            { id: 'ql3-backtest', url: '/api/v1/qlib_core/backtest', method: 'POST' as any, timeout: 30000, retryCount: 2, healthCheckInterval: 60000, expectedResponseTime: 5000 }
          ]
        },
        dependencies: ['QL1', 'QL2']
      },
      {
        id: 'QL4',
        name: '计算优化层',
        metadata: {
          description: 'QLib计算优化',
          icon: '📈',
          complexity: 4,
          estimatedTime: 3500,
          category: 'optimization',
          tags: ['qlib', 'computation'],
          layer: 'qlib_core' as any,
          apiEndpoints: [
            { id: 'ql4-computation', url: '/api/v1/qlib_core/computation', method: 'POST' as any, timeout: 12000, retryCount: 2, healthCheckInterval: 40000, expectedResponseTime: 2500 }
          ]
        },
        dependencies: ['QL1']
      },
      {
        id: 'QL5',
        name: 'QLib数据处理',
        metadata: {
          description: 'QLib高级数据处理',
          icon: '🔧',
          complexity: 4,
          estimatedTime: 3200,
          category: 'processing',
          tags: ['qlib', 'dataprocessing'],
          layer: 'qlib_core' as any,
          apiEndpoints: [
            { id: 'ql5-qlib-dataprocessing', url: '/api/v1/qlib_core/qlib_dataprocessing', method: 'POST' as any, timeout: 12000, retryCount: 2, healthCheckInterval: 40000, expectedResponseTime: 2500 }
          ]
        },
        dependencies: ['QL1', 'QL2']
      },
      {
        id: 'QL6',
        name: '模型集成层',
        metadata: {
          description: 'QLib模型集成',
          icon: '📊',
          complexity: 5,
          estimatedTime: 4000,
          category: 'models',
          tags: ['qlib', 'integration'],
          layer: 'qlib_core' as any,
          apiEndpoints: [
            { id: 'ql6-models', url: '/api/v1/qlib_core/models', method: 'GET' as any, timeout: 8000, retryCount: 3, healthCheckInterval: 30000, expectedResponseTime: 2000 }
          ]
        },
        dependencies: ['QL2', 'QL3']
      },
      {
        id: 'QL7',
        name: '集成接口',
        metadata: {
          description: 'QLib集成接口',
          icon: '🔗',
          complexity: 3,
          estimatedTime: 2800,
          category: 'integration',
          tags: ['qlib', 'interface'],
          layer: 'qlib_core' as any,
          apiEndpoints: [
            { id: 'ql7-integration', url: '/api/v1/qlib_core/integration', method: 'POST' as any, timeout: 10000, retryCount: 3, healthCheckInterval: 35000, expectedResponseTime: 2000 }
          ]
        },
        dependencies: ['QL1', 'QL2']
      },
      
      // 业务逻辑层
      {
        id: 'BL1',
        name: '因子计算引擎',
        metadata: {
          description: '量化因子计算',
          icon: '🧮',
          complexity: 4,
          estimatedTime: 4000,
          category: 'analysis',
          tags: ['factor', 'calculation'],
          layer: 'business_logic' as any,
          apiEndpoints: [
            { id: 'bl1-factor-engine', url: '/api/v1/domain/factor_engine', method: 'POST' as any, timeout: 12000, retryCount: 2, healthCheckInterval: 40000, expectedResponseTime: 3000 }
          ]
        },
        dependencies: ['QL1']
      },
      {
        id: 'BL2',
        name: '策略系统',
        metadata: {
          description: '策略管理系统',
          icon: '🔄',
          complexity: 3,
          estimatedTime: 2000,
          category: 'strategy',
          tags: ['strategy', 'management'],
          layer: 'business_logic' as any,
          apiEndpoints: [
            { id: 'bl2-strategy-system', url: '/api/v1/domain/strategy_system', method: 'POST' as any, timeout: 10000, retryCount: 3, healthCheckInterval: 30000, expectedResponseTime: 2000 }
          ]
        },
        dependencies: ['BL1']
      },
      {
        id: 'BL3',
        name: '策略回放系统',
        metadata: {
          description: '策略回放分析',
          icon: '📊',
          complexity: 3,
          estimatedTime: 3000,
          category: 'backtest',
          tags: ['strategy', 'replay'],
          layer: 'business_logic' as any,
          apiEndpoints: [
            { id: 'bl3-strategy-replay', url: '/api/v1/domain/strategy_replay', method: 'POST' as any, timeout: 15000, retryCount: 2, healthCheckInterval: 45000, expectedResponseTime: 2500 }
          ]
        },
        dependencies: ['BL2']
      },
      {
        id: 'BL4',
        name: '模型管理服务',
        metadata: {
          description: '模型管理服务',
          icon: '🔧',
          complexity: 4,
          estimatedTime: 3500,
          category: 'models',
          tags: ['model', 'management'],
          layer: 'business_logic' as any,
          apiEndpoints: [
            { id: 'bl4-model-management', url: '/api/v1/domain/model_management', method: 'POST' as any, timeout: 12000, retryCount: 2, healthCheckInterval: 40000, expectedResponseTime: 3000 }
          ]
        },
        dependencies: ['BL1', 'QL2']
      },
      {
        id: 'BL5',
        name: '投资分析系统',
        metadata: {
          description: '投资组合分析和绩效评估',
          icon: 'fas fa-chart-line',
          complexity: 4,
          estimatedTime: 4500,
          category: 'analytics',
          tags: ['investment', 'analytics'],
          layer: 'investment_analysis' as any,
          apiEndpoints: [
            { id: 'bl5-investment-analytics', url: '/api/v1/domain/investment_analytics', method: 'POST' as any, timeout: 15000, retryCount: 2, healthCheckInterval: 50000, expectedResponseTime: 4000 }
          ]
        },
        dependencies: ['BL1', 'AN1']
      },
      
      // AI智能策略层
      {
        id: 'AI1',
        name: 'AI策略实验室',
        metadata: {
          description: 'AI策略研发平台',
          icon: '🎯',
          complexity: 5,
          estimatedTime: 6000,
          category: 'ai',
          tags: ['ai', 'strategy', 'lab'],
          layer: 'ai_strategy' as any,
          apiEndpoints: [
            { id: 'ai1-ai-strategy-lab', url: '/api/v1/ai_strategy/ai_strategy_lab', method: 'POST' as any, timeout: 20000, retryCount: 2, healthCheckInterval: 60000, expectedResponseTime: 5000 }
          ]
        },
        dependencies: ['BL1', 'BL2']
      },
      {
        id: 'AI2',
        name: 'AI实时处理',
        metadata: {
          description: 'AI实时数据处理',
          icon: '🛡️',
          complexity: 4,
          estimatedTime: 4000,
          category: 'ai',
          tags: ['ai', 'realtime'],
          layer: 'ai_strategy' as any,
          apiEndpoints: [
            { id: 'ai2-ai-realtime-processing', url: '/api/v1/ai_strategy/ai_realtime_processing', method: 'POST' as any, timeout: 15000, retryCount: 2, healthCheckInterval: 40000, expectedResponseTime: 3000 }
          ]
        },
        dependencies: ['DH2', 'AI1']
      },
      {
        id: 'AI3',
        name: '元学习系统',
        metadata: {
          description: '元学习算法引擎',
          icon: '🤖',
          complexity: 5,
          estimatedTime: 5000,
          category: 'ai',
          tags: ['ai', 'meta-learning'],
          layer: 'ai_strategy' as any,
          apiEndpoints: [
            { id: 'ai3-meta-learning', url: '/api/v1/ai_strategy/meta_learning', method: 'POST' as any, timeout: 18000, retryCount: 2, healthCheckInterval: 55000, expectedResponseTime: 4000 }
          ]
        },
        dependencies: ['AI1']
      },
      {
        id: 'AI4',
        name: '多模型集成',
        metadata: {
          description: '多模型集成系统',
          icon: '📊',
          complexity: 5,
          estimatedTime: 5500,
          category: 'ai',
          tags: ['ai', 'multi-models'],
          layer: 'ai_strategy' as any,
          apiEndpoints: [
            { id: 'ai4-multi-models', url: '/api/v1/ai_strategy/multi_models', method: 'POST' as any, timeout: 20000, retryCount: 2, healthCheckInterval: 60000, expectedResponseTime: 4500 }
          ]
        },
        dependencies: ['AI1', 'AI3']
      },
      {
        id: 'AI5',
        name: '策略生成器',
        metadata: {
          description: 'AI策略生成器',
          icon: '🔧',
          complexity: 4,
          estimatedTime: 4800,
          category: 'ai',
          tags: ['ai', 'generator'],
          layer: 'ai_strategy' as any,
          apiEndpoints: [
            { id: 'ai5-strategy-generator', url: '/api/v1/ai_strategy/strategy_generator', method: 'POST' as any, timeout: 18000, retryCount: 2, healthCheckInterval: 50000, expectedResponseTime: 3500 }
          ]
        },
        dependencies: ['AI1', 'AI2']
      },
      {
        id: 'AI6',
        name: '模型可解释性',
        metadata: {
          description: '模型可解释性分析',
          icon: '📈',
          complexity: 4,
          estimatedTime: 4200,
          category: 'ai',
          tags: ['ai', 'interpretability'],
          layer: 'ai_strategy' as any,
          apiEndpoints: [
            { id: 'ai6-model-interpretability', url: '/api/v1/ai_strategy/model_interpretability', method: 'POST' as any, timeout: 15000, retryCount: 2, healthCheckInterval: 45000, expectedResponseTime: 3000 }
          ]
        },
        dependencies: ['AI1', 'AI4']
      },
      {
        id: 'AI7',
        name: '嵌套决策引擎',
        metadata: {
          description: '嵌套决策引擎',
          icon: '🔄',
          complexity: 5,
          estimatedTime: 6000,
          category: 'ai',
          tags: ['ai', 'nested-decision'],
          layer: 'ai_strategy' as any,
          apiEndpoints: [
            { id: 'ai7-nested-decision', url: '/api/v1/ai_strategy/nested_decision', method: 'POST' as any, timeout: 22000, retryCount: 2, healthCheckInterval: 65000, expectedResponseTime: 5000 }
          ]
        },
        dependencies: ['AI1', 'AI3', 'AI5']
      },
      {
        id: 'AI8',
        name: '在线滚动训练',
        metadata: {
          description: '在线滚动训练系统',
          icon: '📊',
          complexity: 5,
          estimatedTime: 6500,
          category: 'ai',
          tags: ['ai', 'online-rolling'],
          layer: 'ai_strategy' as any,
          apiEndpoints: [
            { id: 'ai8-online-rolling', url: '/api/v1/ai_strategy/online_rolling', method: 'POST' as any, timeout: 25000, retryCount: 2, healthCheckInterval: 70000, expectedResponseTime: 5500 }
          ]
        },
        dependencies: ['AI2', 'AI4']
      },
      {
        id: 'AI9',
        name: '工作流配置',
        metadata: {
          description: 'AI工作流配置',
          icon: '⚙️',
          complexity: 3,
          estimatedTime: 3000,
          category: 'ai',
          tags: ['ai', 'workflow'],
          layer: 'ai_strategy' as any,
          apiEndpoints: [
            { id: 'ai9-workflow-config', url: '/api/v1/ai_strategy/workflow_config', method: 'POST' as any, timeout: 12000, retryCount: 3, healthCheckInterval: 40000, expectedResponseTime: 2500 }
          ]
        },
        dependencies: ['AI1', 'AI5']
      },
      
      // 实盘交易层
      {
        id: 'LT1',
        name: '配置管理',
        metadata: {
          description: '交易配置管理',
          icon: '🚀',
          complexity: 2,
          estimatedTime: 1000,
          category: 'trading',
          tags: ['trading', 'config'],
          layer: 'live_trading' as any,
          apiEndpoints: [
            { id: 'lt1-config', url: '/api/v1/trading/config', method: 'POST' as any, timeout: 8000, retryCount: 3, healthCheckInterval: 30000, expectedResponseTime: 1500 }
          ]
        },
        dependencies: ['AI2']
      },
      {
        id: 'LT2',
        name: '数据处理器',
        metadata: {
          description: '实时数据处理',
          icon: '⚡',
          complexity: 3,
          estimatedTime: 2000,
          category: 'trading',
          tags: ['trading', 'data'],
          layer: 'live_trading' as any,
          apiEndpoints: [
            { id: 'lt2-data-processors', url: '/api/v1/trading/data_processors', method: 'POST' as any, timeout: 10000, retryCount: 2, healthCheckInterval: 35000, expectedResponseTime: 2000 }
          ]
        },
        dependencies: ['LT1']
      },
      {
        id: 'LT3',
        name: '实时监控',
        metadata: {
          description: '交易实时监控',
          icon: '📊',
          complexity: 2,
          estimatedTime: 1500,
          category: 'monitoring',
          tags: ['trading', 'monitor'],
          layer: 'live_trading' as any,
          apiEndpoints: [
            { id: 'lt3-real-time-monitor', url: '/api/v1/trading/real_time_monitor', method: 'GET' as any, timeout: 5000, retryCount: 3, healthCheckInterval: 20000, expectedResponseTime: 1000 }
          ]
        },
        dependencies: ['LT1', 'LT2']
      },
      {
        id: 'LT4',
        name: '流式处理',
        metadata: {
          description: '流式数据处理',
          icon: '🔄',
          complexity: 4,
          estimatedTime: 3500,
          category: 'trading',
          tags: ['trading', 'stream'],
          layer: 'live_trading' as any,
          apiEndpoints: [
            { id: 'lt4-stream-processing', url: '/api/v1/trading/stream_processing', method: 'POST' as any, timeout: 12000, retryCount: 2, healthCheckInterval: 40000, expectedResponseTime: 3000 }
          ]
        },
        dependencies: ['LT2', 'LT3']
      },
      {
        id: 'LT5',
        name: '交易执行',
        metadata: {
          description: '交易执行引擎',
          icon: '💰',
          complexity: 4,
          estimatedTime: 3000,
          category: 'trading',
          tags: ['trading', 'execution'],
          layer: 'live_trading' as any,
          apiEndpoints: [
            { id: 'lt5-trade-execution', url: '/api/v1/trading/trade_execution', method: 'POST' as any, timeout: 15000, retryCount: 2, healthCheckInterval: 45000, expectedResponseTime: 2500 }
          ]
        },
        dependencies: ['LT1', 'LT2', 'LT3']
      },
      {
        id: 'LT6',
        name: '风险管理',
        metadata: {
          description: '风险控制系统',
          icon: '🛡️',
          complexity: 3,
          estimatedTime: 2000,
          category: 'risk',
          tags: ['trading', 'risk'],
          layer: 'live_trading' as any,
          apiEndpoints: [
            { id: 'lt6-risk-management', url: '/api/v1/trading/risk_management', method: 'POST' as any, timeout: 10000, retryCount: 3, healthCheckInterval: 30000, expectedResponseTime: 2000 }
          ]
        },
        dependencies: ['LT3', 'LT5']
      },
      {
        id: 'LT7',
        name: '策略模块',
        metadata: {
          description: '交易策略模块',
          icon: '🎯',
          complexity: 4,
          estimatedTime: 3200,
          category: 'trading',
          tags: ['trading', 'strategy'],
          layer: 'live_trading' as any,
          apiEndpoints: [
            { id: 'lt7-strategy', url: '/api/v1/trading/strategy', method: 'POST' as any, timeout: 12000, retryCount: 2, healthCheckInterval: 40000, expectedResponseTime: 2500 }
          ]
        },
        dependencies: ['LT1', 'LT5', 'LT6']
      },
      {
        id: 'LT8',
        name: '工具模块',
        metadata: {
          description: '交易工具模块',
          icon: '🔧',
          complexity: 3,
          estimatedTime: 2500,
          category: 'trading',
          tags: ['trading', 'utils'],
          layer: 'live_trading' as any,
          apiEndpoints: [
            { id: 'lt8-utils', url: '/api/v1/trading/utils', method: 'POST' as any, timeout: 10000, retryCount: 3, healthCheckInterval: 35000, expectedResponseTime: 2000 }
          ]
        },
        dependencies: ['LT1', 'LT2']
      },
      
      // 实验管理层
      {
        id: 'EM1',
        name: '实验管理核心',
        metadata: {
          description: '实验管理平台',
          icon: '🚀',
          complexity: 3,
          estimatedTime: 2500,
          category: 'experiment',
          tags: ['experiment', 'management'],
          layer: 'experiment_mgmt' as any,
          apiEndpoints: [
            { id: 'em1-experiment-management', url: '/api/v1/domain/experiment_management', method: 'POST' as any, timeout: 12000, retryCount: 2, healthCheckInterval: 40000, expectedResponseTime: 2500 }
          ]
        },
        dependencies: ['AI1', 'AI3']
      },
      {
        id: 'EM2',
        name: '实验服务',
        metadata: {
          description: '实验执行服务',
          icon: '⚡',
          complexity: 2,
          estimatedTime: 1500,
          category: 'experiment',
          tags: ['experiment', 'service'],
          layer: 'experiment_mgmt' as any,
          apiEndpoints: [
            { id: 'em2-experiment-services', url: '/api/v1/experiment_services', method: 'POST' as any, timeout: 10000, retryCount: 3, healthCheckInterval: 30000, expectedResponseTime: 2000 }
          ]
        },
        dependencies: ['EM1']
      },
      {
        id: 'EM3',
        name: '实验模板',
        metadata: {
          description: '实验模板系统',
          icon: '📊',
          complexity: 3,
          estimatedTime: 2000,
          category: 'experiment',
          tags: ['experiment', 'templates'],
          layer: 'experiment_mgmt' as any,
          apiEndpoints: [
            { id: 'em3-experiment-templates', url: '/api/v1/experiment_templates', method: 'GET' as any, timeout: 8000, retryCount: 3, healthCheckInterval: 25000, expectedResponseTime: 1500 }
          ]
        },
        dependencies: ['EM1', 'EM2']
      },
      {
        id: 'EM4',
        name: '实验Web界面',
        metadata: {
          description: '实验管理Web界面',
          icon: '🔧',
          complexity: 3,
          estimatedTime: 2200,
          category: 'experiment',
          tags: ['experiment', 'web'],
          layer: 'experiment_mgmt' as any,
          apiEndpoints: [
            { id: 'em4-experiment-web', url: '/api/v1/experiment_management/web', method: 'GET' as any, timeout: 9000, retryCount: 3, healthCheckInterval: 30000, expectedResponseTime: 1800 }
          ]
        },
        dependencies: ['EM1', 'EM3']
      },
      {
        id: 'EM5',
        name: '自动化实验系统',
        metadata: {
          description: '自动化实验系统',
          icon: '🔄',
          complexity: 4,
          estimatedTime: 3500,
          category: 'automation',
          tags: ['experiment', 'automation'],
          layer: 'experiment_mgmt' as any,
          apiEndpoints: [
            { id: 'em5-automation', url: '/api/v1/automation', method: 'POST' as any, timeout: 15000, retryCount: 2, healthCheckInterval: 45000, expectedResponseTime: 3000 }
          ]
        },
        dependencies: ['EM1', 'EM2']
      },
      {
        id: 'EM6',
        name: 'QLib在线服务',
        metadata: {
          description: 'QLib在线服务',
          icon: '📊',
          complexity: 4,
          estimatedTime: 4000,
          category: 'qlib',
          tags: ['qlib', 'online'],
          layer: 'experiment_mgmt' as any,
          apiEndpoints: [
            { id: 'em6-qlib-online', url: '/api/v1/qlib_online', method: 'POST' as any, timeout: 18000, retryCount: 2, healthCheckInterval: 50000, expectedResponseTime: 3500 }
          ]
        },
        dependencies: ['EM1', 'QL6']
      },
      
      // 前端展示层
      {
        id: 'UI1',
        name: '结果分析器',
        metadata: {
          description: '分析结果展示',
          icon: '📈',
          complexity: 2,
          estimatedTime: 1000,
          category: 'visualization',
          tags: ['ui', 'analysis'],
          layer: 'frontend' as any,
          apiEndpoints: [
            { id: 'ui1-analysis', url: '/api/v1/analysis', method: 'GET' as any, timeout: 5000, retryCount: 3, healthCheckInterval: 20000, expectedResponseTime: 1000 }
          ]
        },
        dependencies: ['EM1', 'EM2']
      },
      {
        id: 'UI2',
        name: '报告生成器',
        metadata: {
          description: '报告生成工具',
          icon: '📋',
          complexity: 2,
          estimatedTime: 2000,
          category: 'report',
          tags: ['ui', 'report'],
          layer: 'frontend' as any,
          apiEndpoints: [
            { id: 'ui2-reports', url: '/api/v1/reports', method: 'GET' as any, timeout: 8000, retryCount: 3, healthCheckInterval: 25000, expectedResponseTime: 1500 }
          ]
        },
        dependencies: ['UI1']
      },
      {
        id: 'UI3',
        name: '数据导出器',
        metadata: {
          description: '数据导出工具',
          icon: '💾',
          complexity: 2,
          estimatedTime: 1500,
          category: 'export',
          tags: ['ui', 'export'],
          layer: 'frontend' as any,
          apiEndpoints: [
            { id: 'ui3-export', url: '/api/v1/export', method: 'POST' as any, timeout: 10000, retryCount: 2, healthCheckInterval: 30000, expectedResponseTime: 2000 }
          ]
        },
        dependencies: ['EM2']
      },
      {
        id: 'UI4',
        name: '可视化渲染器',
        metadata: {
          description: '数据可视化渲染',
          icon: '🎨',
          complexity: 3,
          estimatedTime: 1500,
          category: 'visualization',
          tags: ['ui', 'visualization'],
          layer: 'frontend' as any,
          apiEndpoints: [
            { id: 'ui4-visualization', url: '/api/v1/visualization', method: 'GET' as any, timeout: 6000, retryCount: 3, healthCheckInterval: 20000, expectedResponseTime: 1200 }
          ]
        },
        dependencies: ['EM3', 'UI1', 'UI2']
      },
      {
        id: 'UI5',
        name: '智能节点系统',
        metadata: {
          description: '智能节点管理界面',
          icon: '🖥️',
          complexity: 4,
          estimatedTime: 3000,
          category: 'system',
          tags: ['ui', 'node-system'],
          layer: 'frontend' as any,
          apiEndpoints: [
            { id: 'ui5-intelligent-node-system', url: '/api/v1/intelligent-node-system', method: 'GET' as any, timeout: 7000, retryCount: 3, healthCheckInterval: 25000, expectedResponseTime: 1500 }
          ]
        },
        dependencies: ['UI1', 'UI2', 'UI4']
      },
      
      // 额外的数据中枢层节点
      {
        id: 'DH6',
        name: '实时数据流',
        metadata: {
          description: '实时数据流处理',
          icon: '🌊',
          complexity: 3,
          estimatedTime: 1800,
          category: 'data',
          tags: ['realtime', 'stream'],
          layer: 'data_hub' as any,
          apiEndpoints: [
            { id: 'dh6-realtime-stream', url: '/api/v1/data/realtime/stream', method: 'GET' as any, timeout: 5000, retryCount: 3, healthCheckInterval: 15000, expectedResponseTime: 800 }
          ]
        },
        dependencies: ['DH1', 'DH2']
      },
      {
        id: 'DH7',
        name: '数据质量监控',
        metadata: {
          description: '数据质量监控服务',
          icon: '🔍',
          complexity: 2,
          estimatedTime: 1200,
          category: 'data',
          tags: ['quality', 'monitoring'],
          layer: 'data_hub' as any,
          apiEndpoints: [
            { id: 'dh7-quality-monitor', url: '/api/v1/data/quality/monitor', method: 'GET' as any, timeout: 3000, retryCount: 3, healthCheckInterval: 20000, expectedResponseTime: 1000 }
          ]
        },
        dependencies: ['DH1']
      },
      {
        id: 'DH8',
        name: '数据备份服务',
        metadata: {
          description: '数据备份和恢复',
          icon: '💿',
          complexity: 2,
          estimatedTime: 2500,
          category: 'data',
          tags: ['backup', 'recovery'],
          layer: 'data_hub' as any,
          apiEndpoints: [
            { id: 'dh8-backup', url: '/api/v1/data/backup', method: 'POST' as any, timeout: 10000, retryCount: 2, healthCheckInterval: 60000, expectedResponseTime: 3000 }
          ]
        },
        dependencies: ['DH5']
      },
      
      // 额外的QLib核心层节点
      {
        id: 'QL8',
        name: '数据预处理',
        metadata: {
          description: 'QLib数据预处理模块',
          icon: '🔧',
          complexity: 3,
          estimatedTime: 2000,
          category: 'processing',
          tags: ['qlib', 'preprocessing'],
          layer: 'qlib_core' as any,
          apiEndpoints: [
            { id: 'ql8-preprocessing', url: '/api/v1/qlib_core/preprocessing', method: 'POST' as any, timeout: 8000, retryCount: 3, healthCheckInterval: 30000, expectedResponseTime: 2000 }
          ]
        },
        dependencies: ['QL1']
      },
      {
        id: 'QL9',
        name: '特征工程',
        metadata: {
          description: 'QLib特征工程模块',
          icon: '⚗️',
          complexity: 4,
          estimatedTime: 3500,
          category: 'features',
          tags: ['qlib', 'features'],
          layer: 'qlib_core' as any,
          apiEndpoints: [
            { id: 'ql9-features', url: '/api/v1/qlib_core/features', method: 'POST' as any, timeout: 12000, retryCount: 2, healthCheckInterval: 40000, expectedResponseTime: 3000 }
          ]
        },
        dependencies: ['QL8', 'QL1']
      },
      {
        id: 'QL10',
        name: '模型评估器',
        metadata: {
          description: 'QLib模型评估工具',
          icon: '📊',
          complexity: 3,
          estimatedTime: 2500,
          category: 'evaluation',
          tags: ['qlib', 'evaluation'],
          layer: 'qlib_core' as any,
          apiEndpoints: [
            { id: 'ql10-evaluation', url: '/api/v1/qlib_core/evaluation', method: 'POST' as any, timeout: 10000, retryCount: 3, healthCheckInterval: 35000, expectedResponseTime: 2500 }
          ]
        },
        dependencies: ['QL6', 'QL3']
      },
      
      // 额外的业务逻辑层节点
      {
        id: 'BL6',
        name: '信号生成器',
        metadata: {
          description: '交易信号生成系统',
          icon: '📡',
          complexity: 4,
          estimatedTime: 3000,
          category: 'signals',
          tags: ['signals', 'generation'],
          layer: 'business_logic' as any,
          apiEndpoints: [
            { id: 'bl6-signals', url: '/api/v1/domain/signals', method: 'POST' as any, timeout: 10000, retryCount: 2, healthCheckInterval: 30000, expectedResponseTime: 2500 }
          ]
        },
        dependencies: ['BL1', 'BL2']
      },
      {
        id: 'BL7',
        name: '组合管理',
        metadata: {
          description: '投资组合构建和管理',
          icon: 'fas fa-briefcase',
          complexity: 4,
          estimatedTime: 3500,
          category: 'portfolio',
          tags: ['portfolio', 'management'],
          layer: 'investment_analysis' as any,
          apiEndpoints: [
            { id: 'bl7-portfolio', url: '/api/v1/domain/portfolio', method: 'POST' as any, timeout: 12000, retryCount: 2, healthCheckInterval: 40000, expectedResponseTime: 3000 }
          ]
        },
        dependencies: ['BL5', 'IA1']
      },
      {
        id: 'BL8',
        name: '绩效分析',
        metadata: {
          description: '投资绩效计算和分析',
          icon: 'fas fa-chart-bar',
          complexity: 3,
          estimatedTime: 2800,
          category: 'performance',
          tags: ['performance', 'analysis'],
          layer: 'investment_analysis' as any,
          apiEndpoints: [
            { id: 'bl8-performance', url: '/api/v1/domain/performance', method: 'POST' as any, timeout: 10000, retryCount: 3, healthCheckInterval: 35000, expectedResponseTime: 2500 }
          ]
        },
        dependencies: ['BL5', 'IA2']
      },
      
      // 投资分析系统节点
      {
        id: 'IA1',
        name: '投资组合分析',
        metadata: {
          description: '投资组合风险和收益分析',
          icon: 'fas fa-chart-area',
          complexity: 4,
          estimatedTime: 3500,
          category: 'portfolio',
          tags: ['portfolio', 'analysis'],
          layer: 'investment_analysis' as any,
          apiEndpoints: [
            { id: 'ia1-portfolio-analysis', url: '/api/v1/portfolio/analysis', method: 'POST' as any, timeout: 12000, retryCount: 2, healthCheckInterval: 40000, expectedResponseTime: 3000 }
          ]
        },
        dependencies: ['BL5', 'DH1']
      },
      {
        id: 'IA2',
        name: '归因分析',
        metadata: {
          description: '投资组合归因分析',
          icon: 'fas fa-chart-line',
          complexity: 4,
          estimatedTime: 3200,
          category: 'attribution',
          tags: ['attribution', 'analysis'],
          layer: 'investment_analysis' as any,
          apiEndpoints: [
            { id: 'ia2-attribution', url: '/api/v1/attribution/analysis', method: 'POST' as any, timeout: 11000, retryCount: 2, healthCheckInterval: 35000, expectedResponseTime: 2800 }
          ]
        },
        dependencies: ['BL5', 'IA1']
      },
      {
        id: 'IA3',
        name: '投资策略实现',
        metadata: {
          description: '投资策略执行和管理',
          icon: 'fas fa-cogs',
          complexity: 4,
          estimatedTime: 3800,
          category: 'strategy',
          tags: ['strategy', 'implementation'],
          layer: 'investment_analysis' as any,
          apiEndpoints: [
            { id: 'ia3-strategy-implementation', url: '/api/v1/strategy/implementation', method: 'POST' as any, timeout: 13000, retryCount: 2, healthCheckInterval: 45000, expectedResponseTime: 3200 }
          ]
        },
        dependencies: ['IA2', 'BL6']
      },
      {
        id: 'IA4',
        name: '投资风险评估',
        metadata: {
          description: '投资风险量化和管理',
          icon: 'fas fa-exclamation-triangle',
          complexity: 4,
          estimatedTime: 3000,
          category: 'risk',
          tags: ['risk', 'assessment'],
          layer: 'investment_analysis' as any,
          apiEndpoints: [
            { id: 'ia4-risk-assessment', url: '/api/v1/risk/assessment', method: 'POST' as any, timeout: 10000, retryCount: 3, healthCheckInterval: 30000, expectedResponseTime: 2500 }
          ]
        },
        dependencies: ['BL5', 'IA1', 'IA2']
      },
      
      // 额外的AI策略层节点
      {
        id: 'AI10',
        name: '强化学习',
        metadata: {
          description: '强化学习引擎',
          icon: '🎮',
          complexity: 5,
          estimatedTime: 7000,
          category: 'ai',
          tags: ['ai', 'reinforcement'],
          layer: 'ai_strategy' as any,
          apiEndpoints: [
            { id: 'ai10-reinforcement', url: '/api/v1/ai_strategy/reinforcement', method: 'POST' as any, timeout: 25000, retryCount: 2, healthCheckInterval: 70000, expectedResponseTime: 6000 }
          ]
        },
        dependencies: ['AI3', 'AI4']
      },
      {
        id: 'AI11',
        name: '深度学习',
        metadata: {
          description: '深度学习模型',
          icon: '🧠',
          complexity: 5,
          estimatedTime: 6500,
          category: 'ai',
          tags: ['ai', 'deep-learning'],
          layer: 'ai_strategy' as any,
          apiEndpoints: [
            { id: 'ai11-deep-learning', url: '/api/v1/ai_strategy/deep_learning', method: 'POST' as any, timeout: 22000, retryCount: 2, healthCheckInterval: 65000, expectedResponseTime: 5500 }
          ]
        },
        dependencies: ['AI3', 'AI4']
      },
      {
        id: 'AI12',
        name: '自然语言处理',
        metadata: {
          description: 'NLP新闻分析',
          icon: '📰',
          complexity: 4,
          estimatedTime: 4500,
          category: 'ai',
          tags: ['ai', 'nlp'],
          layer: 'ai_strategy' as any,
          apiEndpoints: [
            { id: 'ai12-nlp', url: '/api/v1/ai_strategy/nlp', method: 'POST' as any, timeout: 18000, retryCount: 2, healthCheckInterval: 50000, expectedResponseTime: 4000 }
          ]
        },
        dependencies: ['AI2', 'AI4']
      },
      
      // 额外的实盘交易层节点
      {
        id: 'LT9',
        name: '订单管理',
        metadata: {
          description: '订单管理系统',
          icon: '📋',
          complexity: 3,
          estimatedTime: 2000,
          category: 'trading',
          tags: ['trading', 'orders'],
          layer: 'live_trading' as any,
          apiEndpoints: [
            { id: 'lt9-orders', url: '/api/v1/trading/orders', method: 'POST' as any, timeout: 8000, retryCount: 3, healthCheckInterval: 30000, expectedResponseTime: 2000 }
          ]
        },
        dependencies: ['LT5', 'LT6']
      },
      {
        id: 'LT10',
        name: '仓位管理',
        metadata: {
          description: '仓位管理系统',
          icon: '⚖️',
          complexity: 3,
          estimatedTime: 2500,
          category: 'trading',
          tags: ['trading', 'positions'],
          layer: 'live_trading' as any,
          apiEndpoints: [
            { id: 'lt10-positions', url: '/api/v1/trading/positions', method: 'POST' as any, timeout: 10000, retryCount: 2, healthCheckInterval: 35000, expectedResponseTime: 2500 }
          ]
        },
        dependencies: ['LT5', 'LT9']
      },
      {
        id: 'LT11',
        name: '清算系统',
        metadata: {
          description: '交易清算系统',
          icon: '💰',
          complexity: 4,
          estimatedTime: 3000,
          category: 'trading',
          tags: ['trading', 'settlement'],
          layer: 'live_trading' as any,
          apiEndpoints: [
            { id: 'lt11-settlement', url: '/api/v1/trading/settlement', method: 'POST' as any, timeout: 12000, retryCount: 2, healthCheckInterval: 40000, expectedResponseTime: 3000 }
          ]
        },
        dependencies: ['LT9', 'LT10']
      },
      
      // 额外的实验管理层节点
      {
        id: 'EM7',
        name: '实验调度器',
        metadata: {
          description: '实验任务调度',
          icon: '⏰',
          complexity: 3,
          estimatedTime: 2000,
          category: 'experiment',
          tags: ['experiment', 'scheduler'],
          layer: 'experiment_mgmt' as any,
          apiEndpoints: [
            { id: 'em7-scheduler', url: '/api/v1/experiment/scheduler', method: 'POST' as any, timeout: 8000, retryCount: 3, healthCheckInterval: 30000, expectedResponseTime: 2000 }
          ]
        },
        dependencies: ['EM1', 'EM2']
      },
      {
        id: 'EM8',
        name: '结果分析器',
        metadata: {
          description: '实验结果分析',
          icon: '🔬',
          complexity: 4,
          estimatedTime: 3500,
          category: 'experiment',
          tags: ['experiment', 'analysis'],
          layer: 'experiment_mgmt' as any,
          apiEndpoints: [
            { id: 'em8-analysis', url: '/api/v1/experiment/analysis', method: 'POST' as any, timeout: 15000, retryCount: 2, healthCheckInterval: 45000, expectedResponseTime: 3500 }
          ]
        },
        dependencies: ['EM1', 'EM3']
      },
      
      // 额外的前端展示层节点
      {
        id: 'UI6',
        name: '实时仪表板',
        metadata: {
          description: '实时数据仪表板',
          icon: '📊',
          complexity: 3,
          estimatedTime: 2000,
          category: 'dashboard',
          tags: ['ui', 'dashboard'],
          layer: 'frontend' as any,
          apiEndpoints: [
            { id: 'ui6-dashboard', url: '/api/v1/dashboard', method: 'GET' as any, timeout: 5000, retryCount: 3, healthCheckInterval: 20000, expectedResponseTime: 1200 }
          ]
        },
        dependencies: ['UI1', 'UI4']
      },
      {
        id: 'UI7',
        name: '警报系统',
        metadata: {
          description: '系统警报管理',
          icon: '🚨',
          complexity: 2,
          estimatedTime: 1500,
          category: 'alerts',
          tags: ['ui', 'alerts'],
          layer: 'frontend' as any,
          apiEndpoints: [
            { id: 'ui7-alerts', url: '/api/v1/alerts', method: 'GET' as any, timeout: 4000, retryCount: 3, healthCheckInterval: 15000, expectedResponseTime: 800 }
          ]
        },
        dependencies: ['UI6', 'LT3']
      },
      {
        id: 'UI8',
        name: '用户管理',
        metadata: {
          description: '用户权限管理',
          icon: '👥',
          complexity: 2,
          estimatedTime: 1800,
          category: 'users',
          tags: ['ui', 'users'],
          layer: 'frontend' as any,
          apiEndpoints: [
            { id: 'ui8-users', url: '/api/v1/users', method: 'GET' as any, timeout: 6000, retryCount: 3, healthCheckInterval: 30000, expectedResponseTime: 1500 }
          ]
        },
        dependencies: ['UI1']
      },
      
      // 额外的系统支持节点
      {
        id: 'SYS1',
        name: '系统监控',
        metadata: {
          description: '系统性能监控',
          icon: '🖥️',
          complexity: 2,
          estimatedTime: 1500,
          category: 'system',
          tags: ['system', 'monitoring'],
          layer: 'frontend' as any,
          apiEndpoints: [
            { id: 'sys1-monitoring', url: '/api/v1/system/monitoring', method: 'GET' as any, timeout: 5000, retryCount: 3, healthCheckInterval: 15000, expectedResponseTime: 1000 }
          ]
        },
        dependencies: ['UI6']
      },
      {
        id: 'SYS2',
        name: '日志管理',
        metadata: {
          description: '系统日志管理',
          icon: '📝',
          complexity: 2,
          estimatedTime: 1200,
          category: 'system',
          tags: ['system', 'logs'],
          layer: 'frontend' as any,
          apiEndpoints: [
            { id: 'sys2-logs', url: '/api/v1/system/logs', method: 'GET' as any, timeout: 6000, retryCount: 3, healthCheckInterval: 20000, expectedResponseTime: 1500 }
          ]
        },
        dependencies: ['SYS1']
      },
      {
        id: 'SYS3',
        name: '配置中心',
        metadata: {
          description: '系统配置管理',
          icon: '⚙️',
          complexity: 2,
          estimatedTime: 1000,
          category: 'system',
          tags: ['system', 'config'],
          layer: 'frontend' as any,
          apiEndpoints: [
            { id: 'sys3-config', url: '/api/v1/system/config', method: 'GET' as any, timeout: 4000, retryCount: 3, healthCheckInterval: 25000, expectedResponseTime: 800 }
          ]
        },
        dependencies: ['UI8']
      },
      
      // 额外的数据处理节点
      {
        id: 'DP1',
        name: '数据清洗',
        metadata: {
          description: '数据清洗服务',
          icon: '🧹',
          complexity: 3,
          estimatedTime: 2500,
          category: 'data',
          tags: ['data', 'cleaning'],
          layer: 'data_hub' as any,
          apiEndpoints: [
            { id: 'dp1-cleaning', url: '/api/v1/data/cleaning', method: 'POST' as any, timeout: 12000, retryCount: 2, healthCheckInterval: 40000, expectedResponseTime: 3000 }
          ]
        },
        dependencies: ['DH2', 'DH7']
      },
      {
        id: 'DP2',
        name: '数据转换',
        metadata: {
          description: '数据格式转换',
          icon: '🔄',
          complexity: 2,
          estimatedTime: 1800,
          category: 'data',
          tags: ['data', 'transformation'],
          layer: 'data_hub' as any,
          apiEndpoints: [
            { id: 'dp2-transformation', url: '/api/v1/data/transformation', method: 'POST' as any, timeout: 8000, retryCount: 3, healthCheckInterval: 30000, expectedResponseTime: 2000 }
          ]
        },
        dependencies: ['DP1']
      },
      {
        id: 'DP3',
        name: '数据验证',
        metadata: {
          description: '数据完整性验证',
          icon: '✅',
          complexity: 2,
          estimatedTime: 1500,
          category: 'data',
          tags: ['data', 'validation'],
          layer: 'data_hub' as any,
          apiEndpoints: [
            { id: 'dp3-validation', url: '/api/v1/data/validation', method: 'POST' as any, timeout: 6000, retryCount: 3, healthCheckInterval: 25000, expectedResponseTime: 1500 }
          ]
        },
        dependencies: ['DP1', 'DP2']
      },
      
      // 额外的分析节点
      {
        id: 'AN1',
        name: '技术分析',
        metadata: {
          description: '技术指标分析',
          icon: '📈',
          complexity: 4,
          estimatedTime: 3000,
          category: 'analysis',
          tags: ['analysis', 'technical'],
          layer: 'business_logic' as any,
          apiEndpoints: [
            { id: 'an1-technical', url: '/api/v1/analysis/technical', method: 'POST' as any, timeout: 10000, retryCount: 2, healthCheckInterval: 35000, expectedResponseTime: 2500 }
          ]
        },
        dependencies: ['BL1', 'QL9']
      },
      {
        id: 'AN2',
        name: '基本面分析',
        metadata: {
          description: '基本面数据分析和评估',
          icon: 'fas fa-building',
          complexity: 4,
          estimatedTime: 3500,
          category: 'analysis',
          tags: ['analysis', 'fundamental'],
          layer: 'investment_analysis' as any,
          apiEndpoints: [
            { id: 'an2-fundamental', url: '/api/v1/analysis/fundamental', method: 'POST' as any, timeout: 12000, retryCount: 2, healthCheckInterval: 40000, expectedResponseTime: 3000 }
          ]
        },
        dependencies: ['DH1', 'DH2']
      },
      {
        id: 'AN3',
        name: '市场情绪分析',
        metadata: {
          description: '市场情绪指标分析',
          icon: 'fas fa-smile',
          complexity: 3,
          estimatedTime: 2800,
          category: 'analysis',
          tags: ['analysis', 'sentiment'],
          layer: 'investment_analysis' as any,
          apiEndpoints: [
            { id: 'an3-sentiment', url: '/api/v1/analysis/sentiment', method: 'POST' as any, timeout: 9000, retryCount: 3, healthCheckInterval: 30000, expectedResponseTime: 2200 }
          ]
        },
        dependencies: ['DH6', 'AN2']
      },
      
      // 额外的风险管理节点
      {
        id: 'RM1',
        name: '风险识别',
        metadata: {
          description: '风险因子识别',
          icon: '🔍',
          complexity: 3,
          estimatedTime: 2000,
          category: 'risk',
          tags: ['risk', 'identification'],
          layer: 'live_trading' as any,
          apiEndpoints: [
            { id: 'rm1-identification', url: '/api/v1/risk/identification', method: 'POST' as any, timeout: 8000, retryCount: 3, healthCheckInterval: 30000, expectedResponseTime: 2000 }
          ]
        },
        dependencies: ['LT6', 'AN3']
      },
      {
        id: 'RM2',
        name: '风险量化',
        metadata: {
          description: '风险量化评估',
          icon: '📊',
          complexity: 4,
          estimatedTime: 3000,
          category: 'risk',
          tags: ['risk', 'quantification'],
          layer: 'live_trading' as any,
          apiEndpoints: [
            { id: 'rm2-quantification', url: '/api/v1/risk/quantification', method: 'POST' as any, timeout: 10000, retryCount: 2, healthCheckInterval: 35000, expectedResponseTime: 2500 }
          ]
        },
        dependencies: ['RM1', 'BL8']
      },
      {
        id: 'RM3',
        name: '风险预警',
        metadata: {
          description: '风险预警系统',
          icon: '⚠️',
          complexity: 3,
          estimatedTime: 1800,
          category: 'risk',
          tags: ['risk', 'warning'],
          layer: 'live_trading' as any,
          apiEndpoints: [
            { id: 'rm3-warning', url: '/api/v1/risk/warning', method: 'POST' as any, timeout: 6000, retryCount: 3, healthCheckInterval: 20000, expectedResponseTime: 1500 }
          ]
        },
        dependencies: ['RM2', 'UI7']
      },
      
      // 额外的AI模型节点
      {
        id: 'ML1',
        name: '机器学习平台',
        metadata: {
          description: '机器学习训练平台',
          icon: '🤖',
          complexity: 5,
          estimatedTime: 6000,
          category: 'ml',
          tags: ['ml', 'training'],
          layer: 'ai_strategy' as any,
          apiEndpoints: [
            { id: 'ml1-training', url: '/api/v1/ml/training', method: 'POST' as any, timeout: 20000, retryCount: 2, healthCheckInterval: 60000, expectedResponseTime: 5000 }
          ]
        },
        dependencies: ['AI3', 'AI11']
      },
      {
        id: 'ML2',
        name: '模型部署',
        metadata: {
          description: '模型部署服务',
          icon: '🚀',
          complexity: 4,
          estimatedTime: 4000,
          category: 'ml',
          tags: ['ml', 'deployment'],
          layer: 'ai_strategy' as any,
          apiEndpoints: [
            { id: 'ml2-deployment', url: '/api/v1/ml/deployment', method: 'POST' as any, timeout: 15000, retryCount: 2, healthCheckInterval: 45000, expectedResponseTime: 3500 }
          ]
        },
        dependencies: ['ML1', 'AI4']
      },
      {
        id: 'ML3',
        name: '模型监控',
        metadata: {
          description: '模型性能监控',
          icon: '📈',
          complexity: 3,
          estimatedTime: 2500,
          category: 'ml',
          tags: ['ml', 'monitoring'],
          layer: 'ai_strategy' as any,
          apiEndpoints: [
            { id: 'ml3-monitoring', url: '/api/v1/ml/monitoring', method: 'GET' as any, timeout: 8000, retryCount: 3, healthCheckInterval: 25000, expectedResponseTime: 2000 }
          ]
        },
        dependencies: ['ML2', 'AI6']
      },
      
      // 额外的交易支持节点
      {
        id: 'TS1',
        name: '行情数据',
        metadata: {
          description: '实时行情数据服务',
          icon: '📊',
          complexity: 3,
          estimatedTime: 2000,
          category: 'trading',
          tags: ['trading', 'market-data'],
          layer: 'live_trading' as any,
          apiEndpoints: [
            { id: 'ts1-market-data', url: '/api/v1/trading/market-data', method: 'GET' as any, timeout: 5000, retryCount: 3, healthCheckInterval: 10000, expectedResponseTime: 800 }
          ]
        },
        dependencies: ['DH6', 'LT2']
      },
      {
        id: 'TS2',
        name: '交易接口',
        metadata: {
          description: '券商交易接口',
          icon: '🔌',
          complexity: 4,
          estimatedTime: 3000,
          category: 'trading',
          tags: ['trading', 'broker-api'],
          layer: 'live_trading' as any,
          apiEndpoints: [
            { id: 'ts2-broker-api', url: '/api/v1/trading/broker-api', method: 'POST' as any, timeout: 10000, retryCount: 2, healthCheckInterval: 30000, expectedResponseTime: 2500 }
          ]
        },
        dependencies: ['LT5', 'LT9']
      },
      {
        id: 'TS3',
        name: '交易统计',
        metadata: {
          description: '交易统计分析',
          icon: '📈',
          complexity: 3,
          estimatedTime: 2200,
          category: 'trading',
          tags: ['trading', 'statistics'],
          layer: 'live_trading' as any,
          apiEndpoints: [
            { id: 'ts3-statistics', url: '/api/v1/trading/statistics', method: 'GET' as any, timeout: 7000, retryCount: 3, healthCheckInterval: 25000, expectedResponseTime: 1800 }
          ]
        },
        dependencies: ['LT11', 'BL8']
      },
      
      // 基于实际API模块的新增节点
      
      // 数据分析模块
      {
        id: 'AN4',
        name: '数据分析核心',
        metadata: {
          description: '数据分析和可视化',
          icon: 'fas fa-chart-pie',
          complexity: 3,
          estimatedTime: 2500,
          category: 'analysis',
          tags: ['analysis', 'core'],
          layer: 'investment_analysis' as any,
          apiEndpoints: [
            { id: 'an4-analysis-core', url: '/api/v1/analysis', method: 'POST' as any, timeout: 10000, retryCount: 3, healthCheckInterval: 30000, expectedResponseTime: 2000 }
          ]
        },
        dependencies: ['AN2', 'AN3', 'DH4']
      },
      
      // 股票筛选模块
      {
        id: 'SK1',
        name: '股票筛选器',
        metadata: {
          description: '智能股票筛选系统',
          icon: '🔍',
          complexity: 3,
          estimatedTime: 2000,
          category: 'stocks',
          tags: ['stocks', 'screening'],
          layer: 'data_hub' as any,
          apiEndpoints: [
            { id: 'sk1-stocks', url: '/api/v1/stocks', method: 'GET' as any, timeout: 8000, retryCount: 3, healthCheckInterval: 25000, expectedResponseTime: 1500 }
          ]
        },
        dependencies: ['DH2', 'AN1']
      },
      
      // 市场分析模块
      {
        id: 'MK1',
        name: '市场分析器',
        metadata: {
          description: '市场分析核心模块',
          icon: '📈',
          complexity: 4,
          estimatedTime: 3000,
          category: 'market',
          tags: ['market', 'analysis'],
          layer: 'business_logic' as any,
          apiEndpoints: [
            { id: 'mk1-market', url: '/api/v1/market', method: 'POST' as any, timeout: 12000, retryCount: 2, healthCheckInterval: 35000, expectedResponseTime: 3000 }
          ]
        },
        dependencies: ['SK1', 'AN2']
      },
      
      // 在线学习模块
      {
        id: 'OL1',
        name: '在线学习引擎',
        metadata: {
          description: '在线机器学习引擎',
          icon: '🎓',
          complexity: 5,
          estimatedTime: 5000,
          category: 'online-learning',
          tags: ['online', 'learning'],
          layer: 'ai_strategy' as any,
          apiEndpoints: [
            { id: 'ol1-online-learning', url: '/api/v1/online-learning', method: 'POST' as any, timeout: 20000, retryCount: 2, healthCheckInterval: 60000, expectedResponseTime: 5000 }
          ]
        },
        dependencies: ['AI3', 'AI8']
      },
      
      // 模型可解释性模块
      {
        id: 'MI1',
        name: '模型解释器',
        metadata: {
          description: '模型可解释性分析',
          icon: '🔬',
          complexity: 4,
          estimatedTime: 3500,
          category: 'model-interpretability',
          tags: ['model', 'interpretability'],
          layer: 'ai_strategy' as any,
          apiEndpoints: [
            { id: 'mi1-model-interpretability', url: '/api/v1/model-interpretability', method: 'POST' as any, timeout: 15000, retryCount: 2, healthCheckInterval: 45000, expectedResponseTime: 3500 }
          ]
        },
        dependencies: ['AI6', 'ML2']
      },
      
      // 监控执行模块
      {
        id: 'ME1',
        name: '监控执行器',
        metadata: {
          description: '系统监控执行模块',
          icon: '👁️',
          complexity: 3,
          estimatedTime: 2000,
          category: 'monitoring',
          tags: ['monitoring', 'execution'],
          layer: 'frontend' as any,
          apiEndpoints: [
            { id: 'me1-monitoring', url: '/api/v1/monitoring', method: 'GET' as any, timeout: 6000, retryCount: 3, healthCheckInterval: 20000, expectedResponseTime: 1200 }
          ]
        },
        dependencies: ['SYS1', 'UI6']
      },
      
      // 统一业务模块
      {
        id: 'UB1',
        name: '统一业务接口',
        metadata: {
          description: '统一业务协调模块',
          icon: '🔗',
          complexity: 4,
          estimatedTime: 3000,
          category: 'unified',
          tags: ['unified', 'business'],
          layer: 'business_logic' as any,
          apiEndpoints: [
            { id: 'ub1-unified', url: '/api/v1/unified', method: 'POST' as any, timeout: 12000, retryCount: 2, healthCheckInterval: 40000, expectedResponseTime: 2500 }
          ]
        },
        dependencies: ['BL1', 'BL2', 'BL5']
      },
      
      // 风险监控模块
      {
        id: 'RK1',
        name: '风险监控器',
        metadata: {
          description: '风险监控核心模块',
          icon: '⚠️',
          complexity: 3,
          estimatedTime: 2500,
          category: 'risk',
          tags: ['risk', 'monitoring'],
          layer: 'live_trading' as any,
          apiEndpoints: [
            { id: 'rk1-risk', url: '/api/v1/risk', method: 'POST' as any, timeout: 10000, retryCount: 3, healthCheckInterval: 30000, expectedResponseTime: 2000 }
          ]
        },
        dependencies: ['RM1', 'RM2']
      },
      
      // 高级回测模块
      {
        id: 'AB1',
        name: '高级回测引擎',
        metadata: {
          description: '高级回测分析系统',
          icon: '🚀',
          complexity: 5,
          estimatedTime: 6000,
          category: 'advanced-backtest',
          tags: ['advanced', 'backtest'],
          layer: 'qlib_core' as any,
          apiEndpoints: [
            { id: 'ab1-advanced-backtest', url: '/api/v1/advanced-backtest', method: 'POST' as any, timeout: 30000, retryCount: 2, healthCheckInterval: 70000, expectedResponseTime: 6000 }
          ]
        },
        dependencies: ['QL3', 'QL4', 'BL3']
      },
      
      // AI助手模块
      {
        id: 'AA1',
        name: 'AI助手',
        metadata: {
          description: '智能AI助手',
          icon: '🤖',
          complexity: 4,
          estimatedTime: 4000,
          category: 'ai-assistant',
          tags: ['ai', 'assistant'],
          layer: 'ai_strategy' as any,
          apiEndpoints: [
            { id: 'aa1-ai-assistant', url: '/api/v1/ai-assistant', method: 'POST' as any, timeout: 15000, retryCount: 2, healthCheckInterval: 50000, expectedResponseTime: 4000 }
          ]
        },
        dependencies: ['AI1', 'AI2']
      },
      
      // 回测分析模块
      {
        id: 'BA1',
        name: '回测分析器',
        metadata: {
          description: '回测结果分析模块',
          icon: '📊',
          complexity: 4,
          estimatedTime: 3500,
          category: 'backtest',
          tags: ['backtest', 'analysis'],
          layer: 'qlib_core' as any,
          apiEndpoints: [
            { id: 'ba1-backtest', url: '/api/v1/backtest', method: 'POST' as any, timeout: 15000, retryCount: 2, healthCheckInterval: 45000, expectedResponseTime: 3500 }
          ]
        },
        dependencies: ['QL3', 'BL3']
      },
      
      // 实时监控模块
      {
        id: 'RT1',
        name: '实时监控器',
        metadata: {
          description: '实时系统监控',
          icon: '📡',
          complexity: 3,
          estimatedTime: 2000,
          category: 'real-time-monitor',
          tags: ['realtime', 'monitor'],
          layer: 'live_trading' as any,
          apiEndpoints: [
            { id: 'rt1-real-time-monitor', url: '/api/v1/real-time-monitor', method: 'GET' as any, timeout: 5000, retryCount: 3, healthCheckInterval: 15000, expectedResponseTime: 1000 }
          ]
        },
        dependencies: ['LT3', 'ME1']
      },
      
      // 性能优化模块
      {
        id: 'PF1',
        name: '性能优化器',
        metadata: {
          description: '系统性能优化模块',
          icon: '⚡',
          complexity: 3,
          estimatedTime: 2500,
          category: 'performance',
          tags: ['performance', 'optimization'],
          layer: 'frontend' as any,
          apiEndpoints: [
            { id: 'pf1-performance', url: '/api/v1/performance', method: 'POST' as any, timeout: 10000, retryCount: 3, healthCheckInterval: 30000, expectedResponseTime: 2500 }
          ]
        },
        dependencies: ['SYS1', 'QL4']
      },
      
      // 数据处理器模块
      {
        id: 'DP4',
        name: '数据处理器核心',
        metadata: {
          description: '数据处理器核心模块',
          icon: '⚙️',
          complexity: 3,
          estimatedTime: 2000,
          category: 'data-processors',
          tags: ['data', 'processors'],
          layer: 'data_hub' as any,
          apiEndpoints: [
            { id: 'dp4-data-processors', url: '/api/v1/data-processors', method: 'POST' as any, timeout: 10000, retryCount: 3, healthCheckInterval: 30000, expectedResponseTime: 2000 }
          ]
        },
        dependencies: ['DP1', 'DP2']
      },
      
      // 流式处理模块
      {
        id: 'SP1',
        name: '流式处理器',
        metadata: {
          description: '流式数据处理模块',
          icon: '🌊',
          complexity: 4,
          estimatedTime: 3000,
          category: 'streaming',
          tags: ['streaming', 'processing'],
          layer: 'data_hub' as any,
          apiEndpoints: [
            { id: 'sp1-streaming', url: '/api/v1/streaming', method: 'POST' as any, timeout: 12000, retryCount: 2, healthCheckInterval: 40000, expectedResponseTime: 3000 }
          ]
        },
        dependencies: ['DH6', 'DP4']
      },
      
      // 交易执行模块
      {
        id: 'TE1',
        name: '交易执行器',
        metadata: {
          description: '交易执行核心模块',
          icon: '💼',
          complexity: 4,
          estimatedTime: 3000,
          category: 'trading-execution',
          tags: ['trading', 'execution'],
          layer: 'live_trading' as any,
          apiEndpoints: [
            { id: 'te1-trading-execution', url: '/api/v1/trading-execution', method: 'POST' as any, timeout: 15000, retryCount: 2, healthCheckInterval: 45000, expectedResponseTime: 3000 }
          ]
        },
        dependencies: ['LT5', 'LT6']
      },
      
      // 风险管理模块
      {
        id: 'RM4',
        name: '风险管理器',
        metadata: {
          description: '风险管理核心模块',
          icon: '🛡️',
          complexity: 4,
          estimatedTime: 3000,
          category: 'risk-management',
          tags: ['risk', 'management'],
          layer: 'live_trading' as any,
          apiEndpoints: [
            { id: 'rm4-risk-management', url: '/api/v1/risk-management', method: 'POST' as any, timeout: 12000, retryCount: 2, healthCheckInterval: 40000, expectedResponseTime: 3000 }
          ]
        },
        dependencies: ['RM1', 'RM2', 'RM3']
      },
      
      // 工具模块
      {
        id: 'UT1',
        name: '工具集',
        metadata: {
          description: '系统工具模块',
          icon: '🔧',
          complexity: 2,
          estimatedTime: 1500,
          category: 'utils',
          tags: ['utils', 'tools'],
          layer: 'frontend' as any,
          apiEndpoints: [
            { id: 'ut1-utils', url: '/api/v1/utils', method: 'GET' as any, timeout: 6000, retryCount: 3, healthCheckInterval: 25000, expectedResponseTime: 1200 }
          ]
        },
        dependencies: ['SYS3']
      },
      
      // 自动化模块
      {
        id: 'AU1',
        name: '自动化引擎',
        metadata: {
          description: '自动化执行引擎',
          icon: '🤖',
          complexity: 4,
          estimatedTime: 3500,
          category: 'automation',
          tags: ['automation', 'engine'],
          layer: 'experiment_mgmt' as any,
          apiEndpoints: [
            { id: 'au1-automation', url: '/api/v1/automation', method: 'POST' as any, timeout: 15000, retryCount: 2, healthCheckInterval: 45000, expectedResponseTime: 3500 }
          ]
        },
        dependencies: ['EM5', 'EM7']
      },
      
      // QLib在线模块
      {
        id: 'QO1',
        name: 'QLib在线服务',
        metadata: {
          description: 'QLib在线服务模块',
          icon: '🌐',
          complexity: 4,
          estimatedTime: 4000,
          category: 'qlib-online',
          tags: ['qlib', 'online'],
          layer: 'experiment_mgmt' as any,
          apiEndpoints: [
            { id: 'qo1-qlib-online', url: '/api/v1/qlib-online', method: 'POST' as any, timeout: 18000, retryCount: 2, healthCheckInterval: 50000, expectedResponseTime: 4000 }
          ]
        },
        dependencies: ['EM6', 'QL6']
      },
      
      // 应用服务层节点
      {
        id: 'WS1',
        name: '工作流引擎',
        metadata: {
          description: '工作流程定义、执行、监控',
          icon: 'fas fa-cogs',
          complexity: 4,
          estimatedTime: 3000,
          category: 'workflow',
          tags: ['workflow', 'engine', 'management'],
          layer: 'application_service' as any,
          apiEndpoints: [
            { id: 'ws1-workflow-engine', url: '/api/v1/workflow/engine', method: 'POST' as any, timeout: 15000, retryCount: 2, healthCheckInterval: 40000, expectedResponseTime: 3000 }
          ]
        },
        dependencies: ['EM1', 'EM5']
      },
      {
        id: 'CF1',
        name: '配置管理',
        metadata: {
          description: '系统配置、参数管理、环境设置',
          icon: 'fas fa-sliders-h',
          complexity: 3,
          estimatedTime: 2000,
          category: 'configuration',
          tags: ['config', 'management', 'settings'],
          layer: 'application_service' as any,
          apiEndpoints: [
            { id: 'cf1-config', url: '/api/v1/config', method: 'GET' as any, timeout: 8000, retryCount: 3, healthCheckInterval: 30000, expectedResponseTime: 1500 }
          ]
        },
        dependencies: ['WS1']
      },
      {
        id: 'AS1',
        name: '智能警报系统',
        metadata: {
          description: '异常检测、警报触发、通知管理',
          icon: 'fas fa-bell',
          complexity: 3,
          estimatedTime: 2500,
          category: 'alerts',
          tags: ['alerts', 'notification', 'monitoring'],
          layer: 'application_service' as any,
          apiEndpoints: [
            { id: 'as1-alerts', url: '/api/v1/alerts', method: 'POST' as any, timeout: 10000, retryCount: 3, healthCheckInterval: 25000, expectedResponseTime: 2000 }
          ]
        },
        dependencies: ['WS1', 'LT3']
      },
      {
        id: 'CL1',
        name: '协作功能',
        metadata: {
          description: '用户协作、权限管理、团队工作',
          icon: 'fas fa-users',
          complexity: 3,
          estimatedTime: 2200,
          category: 'collaboration',
          tags: ['collaboration', 'users', 'permissions'],
          layer: 'application_service' as any,
          apiEndpoints: [
            { id: 'cl1-collaboration', url: '/api/v1/collaboration', method: 'POST' as any, timeout: 12000, retryCount: 2, healthCheckInterval: 35000, expectedResponseTime: 2500 }
          ]
        },
        dependencies: ['WS1', 'UI8']
      },
      {
        id: 'SC1',
        name: '任务调度器',
        metadata: {
          description: '定时任务、调度策略、执行监控',
          icon: 'fas fa-clock',
          complexity: 4,
          estimatedTime: 2800,
          category: 'scheduler',
          tags: ['scheduler', 'tasks', 'timing'],
          layer: 'application_service' as any,
          apiEndpoints: [
            { id: 'sc1-scheduler', url: '/api/v1/scheduler', method: 'POST' as any, timeout: 10000, retryCount: 3, healthCheckInterval: 30000, expectedResponseTime: 2000 }
          ]
        },
        dependencies: ['WS1', 'EM7']
      },
      {
        id: 'RP1',
        name: '报告输出',
        metadata: {
          description: '报告生成、格式转换、输出管理',
          icon: 'fas fa-file-alt',
          complexity: 3,
          estimatedTime: 2500,
          category: 'reports',
          tags: ['reports', 'output', 'generation'],
          layer: 'application_service' as any,
          apiEndpoints: [
            { id: 'rp1-reports', url: '/api/v1/reports', method: 'GET' as any, timeout: 12000, retryCount: 2, healthCheckInterval: 30000, expectedResponseTime: 2500 }
          ]
        },
        dependencies: ['UI2', 'EM8']
      },
      {
        id: 'AP1',
        name: '应用分析',
        metadata: {
          description: '性能分析、使用统计、趋势预测',
          icon: 'fas fa-chart-pie',
          complexity: 4,
          estimatedTime: 3000,
          category: 'analytics',
          tags: ['analytics', 'performance', 'statistics'],
          layer: 'application_service' as any,
          apiEndpoints: [
            { id: 'ap1-analytics', url: '/api/v1/analytics', method: 'POST' as any, timeout: 15000, retryCount: 2, healthCheckInterval: 40000, expectedResponseTime: 3000 }
          ]
        },
        dependencies: ['WS1', 'PF1']
      },
      {
        id: 'MG1',
        name: '监控管理',
        metadata: {
          description: '系统监控、健康检查、状态管理',
          icon: 'fas fa-tachometer-alt',
          complexity: 3,
          estimatedTime: 2000,
          category: 'monitoring',
          tags: ['monitoring', 'health', 'status'],
          layer: 'application_service' as any,
          apiEndpoints: [
            { id: 'mg1-monitoring', url: '/api/v1/monitoring', method: 'GET' as any, timeout: 8000, retryCount: 3, healthCheckInterval: 20000, expectedResponseTime: 1500 }
          ]
        },
        dependencies: ['WS1', 'SYS1']
      },
      {
        id: 'LG1',
        name: '日志管理',
        metadata: {
          description: '日志收集、分析、存储、检索',
          icon: 'fas fa-list-alt',
          complexity: 3,
          estimatedTime: 2200,
          category: 'logging',
          tags: ['logging', 'analysis', 'storage'],
          layer: 'application_service' as any,
          apiEndpoints: [
            { id: 'lg1-logging', url: '/api/v1/logging', method: 'GET' as any, timeout: 10000, retryCount: 3, healthCheckInterval: 30000, expectedResponseTime: 2000 }
          ]
        },
        dependencies: ['WS1', 'SYS2']
      },
      {
        id: 'NT1',
        name: '通知服务',
        metadata: {
          description: '消息推送、邮件通知、短信服务',
          icon: 'fas fa-network-wired',
          complexity: 3,
          estimatedTime: 2000,
          category: 'notification',
          tags: ['notification', 'messaging', 'communication'],
          layer: 'application_service' as any,
          apiEndpoints: [
            { id: 'nt1-notification', url: '/api/v1/notification', method: 'POST' as any, timeout: 8000, retryCount: 3, healthCheckInterval: 25000, expectedResponseTime: 1500 }
          ]
        },
        dependencies: ['AS1', 'CL1']
      }
    ];
  }
  
  // 构建依赖关系
  private buildDependencies(): void {
    for (const [nodeId, node] of this.nodes) {
      for (const depId of node.dependencies) {
        const depNode = this.nodes.get(depId);
        if (depNode && !depNode.dependents.includes(nodeId)) {
          depNode.dependents.push(nodeId);
        }
      }
    }
  }
  
  // 智能更新所有节点状态
  async updateAllNodeStates(context: RecommendationContext): Promise<void> {
    console.log('开始更新所有节点状态...');
    
    // 模拟推荐数据
    const recommendations = await this.generateMockRecommendations(context);
    
    for (const [nodeId, node] of this.nodes) {
      await this.updateNodeState(nodeId, recommendations, context);
    }
    
    this.emit('states-updated', {
      timestamp: new Date(),
      nodeCount: this.nodes.size,
      context
    });
    
    console.log('节点状态更新完成');
  }
  
  // 更新单个节点状态
  private async updateNodeState(
    nodeId: string, 
    recommendations: DynamicNodeRecommendation[],
    context: RecommendationContext
  ): Promise<void> {
    const node = this.nodes.get(nodeId);
    if (!node) return;
    
    const previousStatus = node.status;
    let newStatus = previousStatus;
    
    // 1. 检查API状态
    const apiAvailable = await this.checkAPIAvailability(node);
    if (!apiAvailable) {
      newStatus = ExtendedNodeStatus.DISABLED;
      node.canActivate = false;
      node.isRecommended = false;
    } else {
      // 2. 检查依赖关系
      const dependenciesMet = await this.checkDependencies(node);
      
      if (!dependenciesMet) {
        newStatus = ExtendedNodeStatus.STANDBY;
        node.canActivate = false;
        node.isRecommended = false;
      } else {
        // 3. 检查推荐状态
        const recommendation = recommendations.find(rec => rec.nodeId === nodeId);
        
        if (recommendation && recommendation.confidence > 0.7) {
          newStatus = ExtendedNodeStatus.RECOMMENDED;
          node.canActivate = true;
          node.isRecommended = true;
          node.recommendationReason = recommendation.reason;
          node.priority = recommendation.confidence * 100;
        } else {
          // 4. 检查是否应该激活
          if (node.status === ExtendedNodeStatus.ACTIVE || node.status === ExtendedNodeStatus.RUNNING) {
            newStatus = ExtendedNodeStatus.ACTIVE;
            node.canActivate = true;
          } else {
            newStatus = ExtendedNodeStatus.STANDBY;
            node.canActivate = true;
            node.isRecommended = false;
          }
        }
      }
    }
    
    // 5. 特殊状态处理
    if (node.performance.availability < 0.9) {
      newStatus = ExtendedNodeStatus.MAINTENANCE;
    }
    
    if (node.priority > 90) {
      newStatus = ExtendedNodeStatus.HIGH_PRIORITY;
    }
    
    // 更新状态
    if (newStatus !== previousStatus) {
      node.previousStatus = previousStatus;
      node.status = newStatus;
      node.lastUpdated = new Date();
      
      this.emitNodeStateChanged(nodeId, previousStatus, newStatus);
    }
  }
  
  // 检查API可用性
  private async checkAPIAvailability(node: NodeStateInfo): Promise<boolean> {
    for (const endpoint of node.metadata.apiEndpoints) {
      const status = apiMonitor.getAPIStatus(endpoint.id);
      if (status !== APIStatus.AVAILABLE && status !== APIStatus.DEGRADED) {
        return false;
      }
    }
    return true;
  }
  
  // 检查依赖关系
  private async checkDependencies(node: NodeStateInfo): Promise<boolean> {
    for (const depId of node.dependencies) {
      const depNode = this.nodes.get(depId);
      if (!depNode || depNode.status !== ExtendedNodeStatus.ACTIVE) {
        return false;
      }
    }
    return true;
  }
  
  // 激活节点
  async activateNode(nodeId: string): Promise<boolean> {
    const node = this.nodes.get(nodeId);
    if (!node || !node.canActivate) {
      return false;
    }
    
    try {
      node.status = ExtendedNodeStatus.ACTIVATING;
      
      // 模拟激活过程
      await this.performNodeActivation(node);
      
      node.status = ExtendedNodeStatus.ACTIVE;
      node.lastUpdated = new Date();
      
      // 更新依赖节点的状态
      await this.updateDependentNodes(nodeId);
      
      this.emitNodeActivated(nodeId);
      return true;
      
    } catch (error) {
      node.status = ExtendedNodeStatus.ERROR;
      this.emitNodeError(nodeId, error instanceof Error ? error.message : String(error));
      return false;
    }
  }
  
  // 执行节点激活
  private async performNodeActivation(node: NodeStateInfo): Promise<void> {
    // 模拟API调用
    for (const endpoint of node.metadata.apiEndpoints) {
      const responseTime = Math.random() * 2000 + 500;
      const success = Math.random() > 0.1; // 90% 成功率
      
      if (!success) {
        throw new Error(`API调用失败: ${endpoint.url}`);
      }
      
      // 更新性能指标
      node.performance.responseTime = responseTime;
      node.performance.cpuUsage = Math.random() * 80;
      node.performance.memoryUsage = Math.random() * 70;
      node.performance.availability = 0.9 + Math.random() * 0.1;
      
      await new Promise(resolve => setTimeout(resolve, 500));
    }
  }
  
  // 更新依赖节点状态
  private async updateDependentNodes(nodeId: string): Promise<void> {
    const node = this.nodes.get(nodeId);
    if (!node) return;
    
    for (const dependentId of node.dependents) {
      const dependentNode = this.nodes.get(dependentId);
      if (dependentNode && dependentNode.status === ExtendedNodeStatus.STANDBY) {
        // 检查依赖是否全部满足
        const dependenciesMet = await this.checkDependencies(dependentNode);
        if (dependenciesMet) {
          dependentNode.canActivate = true;
          dependentNode.status = ExtendedNodeStatus.RECOMMENDED;
          dependentNode.recommendationReason = `依赖节点 ${nodeId} 已激活`;
        }
      }
    }
  }
  
  // 停用节点
  async deactivateNode(nodeId: string): Promise<boolean> {
    const node = this.nodes.get(nodeId);
    if (!node) {
      return false;
    }
    
    try {
      node.status = ExtendedNodeStatus.DEACTIVATING;
      
      // 模拟停用过程
      await this.performNodeDeactivation(node);
      
      node.status = ExtendedNodeStatus.INACTIVE;
      node.lastUpdated = new Date();
      
      // 更新依赖节点的状态
      await this.updateDependentNodesOnDeactivation(nodeId);
      
      return true;
      
    } catch (error) {
      node.status = ExtendedNodeStatus.ERROR;
      this.emitNodeError(nodeId, error instanceof Error ? error.message : String(error));
      return false;
    }
  }
  
  // 执行节点停用
  private async performNodeDeactivation(node: NodeStateInfo): Promise<void> {
    // 模拟API调用停用
    for (const endpoint of node.metadata.apiEndpoints) {
      const responseTime = Math.random() * 1000 + 200;
      
      // 更新性能指标
      node.performance.responseTime = responseTime;
      node.performance.cpuUsage = Math.max(0, node.performance.cpuUsage - 20);
      node.performance.memoryUsage = Math.max(0, node.performance.memoryUsage - 15);
      node.performance.availability = 0.9 + Math.random() * 0.1;
      
      await new Promise(resolve => setTimeout(resolve, 300));
    }
  }
  
  // 更新依赖节点状态（停用时）
  private async updateDependentNodesOnDeactivation(nodeId: string): Promise<void> {
    const node = this.nodes.get(nodeId);
    if (!node) return;
    
    for (const dependentId of node.dependents) {
      const dependentNode = this.nodes.get(dependentId);
      if (dependentNode && (dependentNode.status === ExtendedNodeStatus.ACTIVE || dependentNode.status === ExtendedNodeStatus.RUNNING)) {
        // 检查是否还有其他依赖
        const hasOtherDependencies = dependentNode.dependencies.some(depId => {
          const depNode = this.nodes.get(depId);
          return depNode && depNode.status === ExtendedNodeStatus.ACTIVE && depId !== nodeId;
        });
        
        if (!hasOtherDependencies) {
          dependentNode.status = ExtendedNodeStatus.STANDBY;
          dependentNode.canActivate = false;
          dependentNode.recommendationReason = `依赖节点 ${nodeId} 已停用`;
        }
      }
    }
  }
  
  // 生成模拟推荐
  private async generateMockRecommendations(context: RecommendationContext): Promise<DynamicNodeRecommendation[]> {
    const recommendations: DynamicNodeRecommendation[] = [];
    
    // 基于当前工作流推荐
    if (context.currentWorkflow === 'ai-strategy-generation') {
      recommendations.push({
        nodeId: 'DH1',
        name: 'QuantDataHub核心',
        description: 'AI策略生成需要的数据支持',
        type: 'workflow_based',
        category: 'workflow_completion',
        confidence: 0.9,
        reason: 'AI策略生成工作流的起始节点',
        metadata: {
          layer: 'data_hub',
          complexity: 3,
          estimatedTime: 2000,
          dependencies: []
        },
        actions: ['activate', 'configure']
      });
      
      recommendations.push({
        nodeId: 'QL1',
        name: '数据处理模块',
        description: 'AI策略需要的数据处理',
        type: 'workflow_based',
        category: 'workflow_completion',
        confidence: 0.85,
        reason: 'AI策略生成工作流的数据处理节点',
        metadata: {
          layer: 'qlib_core',
          complexity: 4,
          estimatedTime: 3000,
          dependencies: ['DH1']
        },
        actions: ['activate', 'configure']
      });
      
      recommendations.push({
        nodeId: 'AI1',
        name: 'AI策略实验室',
        description: 'AI策略生成的核心组件',
        type: 'workflow_based',
        category: 'workflow_completion',
        confidence: 0.95,
        reason: 'AI策略生成工作流的核心节点',
        metadata: {
          layer: 'ai_strategy',
          complexity: 5,
          estimatedTime: 6000,
          dependencies: ['QL1']
        },
        actions: ['activate', 'configure']
      });
    }
    
    // 基于用户行为推荐
    if (context.userLevel === 'beginner') {
      recommendations.push({
        nodeId: 'DH1',
        name: 'QuantDataHub核心',
        description: '适合初学者的数据节点',
        type: 'behavior_based',
        category: 'existing_node',
        confidence: 0.8,
        reason: '基于初学者用户的使用模式推荐',
        metadata: {
          layer: 'data_hub',
          complexity: 3,
          estimatedTime: 2000,
          dependencies: []
        },
        actions: ['activate', 'view_details']
      });
    }
    
    return recommendations;
  }
  
  // 获取节点状态
  getNodeState(nodeId: string): NodeStateInfo | undefined {
    return this.nodes.get(nodeId);
  }
  
  // 获取所有节点状态
  getAllNodeStates(): Map<string, NodeStateInfo> {
    return new Map(this.nodes);
  }
  
  // 获取所有节点（数组格式，用于电路板组件）
  getAllNodes(): NodeStateInfo[] {
    return Array.from(this.nodes.values());
  }
  
  // 获取指定状态的节点
  getNodesByStatus(status: ExtendedNodeStatus): NodeStateInfo[] {
    return Array.from(this.nodes.values()).filter(node => node.status === status);
  }
  
  // 获取推荐节点
  getRecommendedNodes(): NodeStateInfo[] {
    return Array.from(this.nodes.values()).filter(node => node.isRecommended);
  }
  
  // 获取可激活节点
  getActivatableNodes(): NodeStateInfo[] {
    return Array.from(this.nodes.values()).filter(node => node.canActivate);
  }
  
  // 事件系统
  on(event: string, listener: Function): void {
    if (!this.eventListeners.has(event)) {
      this.eventListeners.set(event, []);
    }
    this.eventListeners.get(event)!.push(listener);
  }
  
  off(event: string, listener: Function): void {
    const listeners = this.eventListeners.get(event);
    if (listeners) {
      const index = listeners.indexOf(listener);
      if (index > -1) {
        listeners.splice(index, 1);
      }
    }
  }
  
  private emitNodeStateChanged(nodeId: string, previousStatus: ExtendedNodeStatus, newStatus: ExtendedNodeStatus): void {
    const event: NodeStateChangedEvent = {
      nodeId,
      previousStatus,
      newStatus,
      timestamp: new Date()
    };
    
    this.emit('node-state-changed', event);
  }
  
  private emitNodeActivated(nodeId: string): void {
    const event: NodeActivatedEvent = {
      nodeId,
      timestamp: new Date(),
      activationTime: Math.random() * 2000 + 500
    };
    
    this.emit('node-activated', event);
  }
  
  private emitNodeError(nodeId: string, error: string): void {
    const event: NodeErrorEvent = {
      nodeId,
      error,
      timestamp: new Date(),
      recoverable: true
    };
    
    this.emit('node-error', event);
  }
  
  private emit(event: string, data: any): void {
    const listeners = this.eventListeners.get(event);
    if (listeners) {
      listeners.forEach(listener => {
        try {
          listener(data);
        } catch (error) {
          console.error(`事件监听器错误 (${event}):`, error);
        }
      });
    }
  }
  
  // 重置所有节点状态
  resetAllNodes(): void {
    for (const [nodeId, node] of this.nodes) {
      node.status = ExtendedNodeStatus.INACTIVE;
      node.previousStatus = ExtendedNodeStatus.INACTIVE;
      node.canActivate = false;
      node.isRecommended = false;
      node.priority = 0;
      node.lastUpdated = new Date();
      node.recommendationReason = undefined;
    }
    
    this.emit('states-updated', {
      timestamp: new Date(),
      nodeCount: this.nodes.size,
      context: null
    });
  }
  
  // 批量激活节点
  async activateNodes(nodeIds: string[]): Promise<{ success: string[]; failed: string[] }> {
    const result: { success: string[]; failed: string[] } = { success: [], failed: [] };
    
    for (const nodeId of nodeIds) {
      try {
        const success = await this.activateNode(nodeId);
        if (success) {
          result.success.push(nodeId);
        } else {
          result.failed.push(nodeId);
        }
      } catch (error) {
        result.failed.push(nodeId);
      }
      
      // 添加延迟以避免同时激活太多节点
      await new Promise(resolve => setTimeout(resolve, 200));
    }
    
    return result;
  }
  
  // 获取节点统计
  getNodeStats(): {
    total: number;
    inactive: number;
    standby: number;
    recommended: number;
    active: number;
    running: number;
    error: number;
    disabled: number;
  } {
    const stats = {
      total: this.nodes.size,
      inactive: 0,
      standby: 0,
      recommended: 0,
      active: 0,
      running: 0,
      error: 0,
      disabled: 0
    };
    
    for (const node of this.nodes.values()) {
      switch (node.status) {
        case ExtendedNodeStatus.INACTIVE:
          stats.inactive++;
          break;
        case ExtendedNodeStatus.STANDBY:
          stats.standby++;
          break;
        case ExtendedNodeStatus.RECOMMENDED:
          stats.recommended++;
          break;
        case ExtendedNodeStatus.ACTIVE:
          stats.active++;
          break;
        case ExtendedNodeStatus.RUNNING:
          stats.running++;
          break;
        case ExtendedNodeStatus.ERROR:
          stats.error++;
          break;
        case ExtendedNodeStatus.DISABLED:
          stats.disabled++;
          break;
      }
    }
    
    return stats;
  }
  
  // API模块相关方法
  
  // 根据API模块获取节点
  getNodesByApiModule(apiModule: string): NodeStateInfo[] {
    return Array.from(this.nodes.values()).filter(node =>
      node.metadata.apiEndpoints.some(endpoint =>
        endpoint.url.includes(apiModule) ||
        endpoint.id.includes(apiModule)
      )
    );
  }
  
  // 获取所有API模块
  getAllApiModules(): string[] {
    const modules = new Set<string>();
    
    for (const node of this.nodes.values()) {
      for (const endpoint of node.metadata.apiEndpoints) {
        // 从URL中提取模块名
        const urlParts = endpoint.url.split('/');
        if (urlParts.length >= 3) {
          modules.add(urlParts[2]); // /api/v1/module_name
        }
        
        // 从ID中提取模块名
        const idParts = endpoint.id.split('-');
        if (idParts.length >= 2) {
          modules.add(idParts[0]);
        }
      }
    }
    
    return Array.from(modules).sort();
  }
  
  // 获取API模块统计
  getApiModuleStats(): Array<{
    module: string;
    nodeCount: number;
    activeNodes: number;
    totalEndpoints: number;
    availableEndpoints: number;
    avgResponseTime: number;
  }> {
    const modules = this.getAllApiModules();
    const stats = [];
    
    for (const module of modules) {
      const nodes = this.getNodesByApiModule(module);
      const activeNodes = nodes.filter(node => node.status === ExtendedNodeStatus.ACTIVE).length;
      
      let totalEndpoints = 0;
      let availableEndpoints = 0;
      let totalResponseTime = 0;
      let endpointCount = 0;
      
      for (const node of nodes) {
        for (const endpoint of node.metadata.apiEndpoints) {
          totalEndpoints++;
          const status = apiMonitor.getAPIStatus(endpoint.id);
          if (status === APIStatus.AVAILABLE || status === APIStatus.DEGRADED) {
            availableEndpoints++;
          }
          
          if (node.performance.responseTime > 0) {
            totalResponseTime += node.performance.responseTime;
            endpointCount++;
          }
        }
      }
      
      stats.push({
        module,
        nodeCount: nodes.length,
        activeNodes,
        totalEndpoints,
        availableEndpoints,
        avgResponseTime: endpointCount > 0 ? totalResponseTime / endpointCount : 0
      });
    }
    
    return stats.sort((a, b) => b.nodeCount - a.nodeCount);
  }
  
  // 获取API模块详细信息
  getApiModuleDetails(module: string): {
    module: string;
    nodes: Array<{
      nodeId: string;
      nodeName: string;
      status: ExtendedNodeStatus;
      endpoints: Array<{
        id: string;
        url: string;
        method: string;
        status: APIStatus;
        responseTime: number;
      }>;
    }>;
    summary: {
      totalNodes: number;
      activeNodes: number;
      totalEndpoints: number;
      availableEndpoints: number;
      healthScore: number;
    };
  } {
    const nodes = this.getNodesByApiModule(module);
    const nodeDetails = [];
    let totalEndpoints = 0;
    let availableEndpoints = 0;
    let activeNodes = 0;
    
    for (const node of nodes) {
      const endpoints = [];
      
      for (const endpoint of node.metadata.apiEndpoints) {
        totalEndpoints++;
        const status = apiMonitor.getAPIStatus(endpoint.id);
        if (status === APIStatus.AVAILABLE || status === APIStatus.DEGRADED) {
          availableEndpoints++;
        }
        
        endpoints.push({
          id: endpoint.id,
          url: endpoint.url,
          method: endpoint.method,
          status: status || APIStatus.UNAVAILABLE,
          responseTime: node.performance.responseTime
        });
      }
      
      if (node.status === ExtendedNodeStatus.ACTIVE) {
        activeNodes++;
      }
      
      nodeDetails.push({
        nodeId: node.id,
        nodeName: node.name,
        status: node.status,
        endpoints
      });
    }
    
    const healthScore = totalEndpoints > 0 ? (availableEndpoints / totalEndpoints) * 100 : 0;
    
    return {
      module,
      nodes: nodeDetails,
      summary: {
        totalNodes: nodes.length,
        activeNodes,
        totalEndpoints,
        availableEndpoints,
        healthScore
      }
    };
  }
  
  // 根据API端点获取节点
  getNodeByApiEndpoint(endpointId: string): NodeStateInfo | undefined {
    for (const node of this.nodes.values()) {
      if (node.metadata.apiEndpoints.some(endpoint => endpoint.id === endpointId)) {
        return node;
      }
    }
    return undefined;
  }
  
  // 获取所有API端点
  getAllApiEndpoints(): Array<{
    id: string;
    url: string;
    method: string;
    nodeId: string;
    nodeName: string;
    status: APIStatus;
    responseTime: number;
    timeout: number;
    retryCount: number;
  }> {
    const endpoints = [];
    
    for (const node of this.nodes.values()) {
      for (const endpoint of node.metadata.apiEndpoints) {
        const status = apiMonitor.getAPIStatus(endpoint.id);
        
        endpoints.push({
          id: endpoint.id,
          url: endpoint.url,
          method: endpoint.method,
          nodeId: node.id,
          nodeName: node.name,
          status: status || APIStatus.UNAVAILABLE,
          responseTime: node.performance.responseTime,
          timeout: endpoint.timeout,
          retryCount: endpoint.retryCount
        });
      }
    }
    
    return endpoints.sort((a, b) => a.url.localeCompare(b.url));
  }
  
  // 获取API健康状态
  getApiHealthStatus(): {
    totalEndpoints: number;
    availableEndpoints: number;
    degradedEndpoints: number;
    unavailableEndpoints: number;
    healthScore: number;
    criticalIssues: Array<{
      endpointId: string;
      nodeId: string;
      nodeName: string;
      issue: string;
    }>;
  } {
    const endpoints = this.getAllApiEndpoints();
    const totalEndpoints = endpoints.length;
    let availableEndpoints = 0;
    let degradedEndpoints = 0;
    let unavailableEndpoints = 0;
    const criticalIssues = [];
    
    for (const endpoint of endpoints) {
      switch (endpoint.status) {
        case APIStatus.AVAILABLE:
          availableEndpoints++;
          break;
        case APIStatus.DEGRADED:
          degradedEndpoints++;
          break;
        case APIStatus.UNAVAILABLE:
          unavailableEndpoints++;
          criticalIssues.push({
            endpointId: endpoint.id,
            nodeId: endpoint.nodeId,
            nodeName: endpoint.nodeName,
            issue: 'API端点不可用'
          });
          break;
        case APIStatus.ERROR:
          unavailableEndpoints++;
          criticalIssues.push({
            endpointId: endpoint.id,
            nodeId: endpoint.nodeId,
            nodeName: endpoint.nodeName,
            issue: 'API端点错误'
          });
          break;
      }
      
      // 检查响应时间过长
      if (endpoint.responseTime > endpoint.timeout * 0.8) {
        criticalIssues.push({
          endpointId: endpoint.id,
          nodeId: endpoint.nodeId,
          nodeName: endpoint.nodeName,
          issue: `响应时间过长: ${endpoint.responseTime}ms`
        });
      }
    }
    
    const healthScore = totalEndpoints > 0 ?
      ((availableEndpoints * 100 + degradedEndpoints * 50) / totalEndpoints) : 0;
    
    return {
      totalEndpoints,
      availableEndpoints,
      degradedEndpoints,
      unavailableEndpoints,
      healthScore,
      criticalIssues
    };
  }
  
  // 获取节点连接关系
  getNodeConnections(): Array<{
    from: string;
    to: string;
    type: 'dependency' | 'dataflow' | 'control' | 'layer';
    strength: number;
  }> {
    return NodeConnectionsManager.getNodeConnections();
  }
}

// 创建全局节点状态管理器实例
export const nodeStateManager = new IntelligentNodeStateManager();

// 导出节点状态管理器
export default nodeStateManager;
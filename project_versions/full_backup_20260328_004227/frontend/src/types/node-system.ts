// 节点系统类型定义

// 扩展的节点状态枚举
export enum ExtendedNodeStatus {
  INACTIVE = 'inactive',           // 非激活 - 灰色，完全不可用
  STANDBY = 'standby',            // 待机 - 黄色，备选状态
  RECOMMENDED = 'recommended',     // 推荐 - 绿色边框，推荐激活
  ACTIVATING = 'activating',       // 激活中 - 蓝色动画
  ACTIVE = 'active',              // 激活 - 绿色，可工作
  RUNNING = 'running',            // 运行中 - 橙色动画
  COMPLETED = 'completed',        // 完成 - 深绿色
  ERROR = 'error',               // 错误 - 红色
  DISABLED = 'disabled',          // 禁用 - 深灰色
  MAINTENANCE = 'maintenance',    // 维护 - 橙色
  HIGH_PRIORITY = 'high_priority', // 高优先级 - 紫色边框
  CRITICAL = 'critical',          // 关键 - 红色边框
  OPTIMIZED = 'optimized',        // 优化 - 金色边框
  DEACTIVATING = 'deactivating'   // 停用中 - 黄色动画
}

// API状态枚举
export enum APIStatus {
  AVAILABLE = 'available',
  UNAVAILABLE = 'unavailable',
  ERROR = 'error',
  CHECKING = 'checking',
  DEGRADED = 'degraded'
}

// 节点层级枚举
export enum NodeLayer {
  DATA_HUB = 'data_hub',
  QLIB_CORE = 'qlib_core',
  BUSINESS_LOGIC = 'business_logic',
  AI_STRATEGY = 'ai_strategy',
  LIVE_TRADING = 'live_trading',
  EXPERIMENT_MGMT = 'experiment_mgmt',
  FRONTEND = 'frontend'
}

// API端点定义
export interface APIEndpoint {
  id: string;
  url: string;
  method: 'GET' | 'POST' | 'PUT' | 'DELETE';
  timeout: number;
  retryCount: number;
  healthCheckInterval: number;
  expectedResponseTime: number;
}

// 性能指标
export interface PerformanceMetrics {
  cpuUsage: number;
  memoryUsage: number;
  responseTime: number;
  throughput: number;
  errorRate: number;
  availability: number;
  lastHealthCheck: Date;
}

// 节点元数据
export interface NodeMetadata {
  description: string;
  icon: string;
  complexity: number;
  estimatedTime: number;
  category: string;
  tags: string[];
  apiEndpoints: APIEndpoint[];
  layer: NodeLayer;
}

// 节点边界定义
export interface NodeBounds {
  x: number;
  y: number;
  width: number;
  height: number;
}

// 节点状态信息
export interface NodeStateInfo {
  id: string;
  name: string;
  status: ExtendedNodeStatus;
  previousStatus: ExtendedNodeStatus;
  canActivate: boolean;
  isRecommended: boolean;
  priority: number;
  dependencies: string[];
  dependents: string[];
  apiStatus: APIStatus;
  performance: PerformanceMetrics;
  metadata: NodeMetadata;
  bounds: NodeBounds;
  lastUpdated: Date;
  recommendationReason?: string;
  activationComplexity: number;
}

// 工作流阶段定义
export interface WorkflowPhase {
  id: string;
  name: string;
  nodes: string[];
  dependencies: string[];
  parallel: boolean;
  timeout: number;
  nextPhase?: string;
}

// 工作流程步骤
export interface WorkflowStep {
  id: string;
  name: string;
  description: string;
  nodeIds: string[];
  estimatedDuration: number;
  dependencies: string[];
  parallel: boolean;
  required: boolean;
}

// 工作流定义
export interface WorkflowDefinition {
  id: string;
  name: string;
  description: string;
  phases?: WorkflowPhase[];
  steps?: WorkflowStep[];
  category?: string;
  estimatedDuration?: number;
  entryPoints?: string[];
  exitPoints?: string[];
  requirements?: WorkflowRequirement[];
  successCriteria?: {
    minCompletedSteps?: number;
    minCompletedPhases?: number;
    maxFailedSteps?: number;
    maxFailedPhases?: number;
    maxExecutionTime: number;
    requiredNodes: string[];
  };
  rollbackPlan?: {
    enabled: boolean;
    rollbackSteps?: string[];
    rollbackPhases?: string[];
    cleanupNodes: string[];
  };
}

// 工作流需求
export interface WorkflowRequirement {
  type: string;
  description: string;
}

// 推荐上下文
export interface RecommendationContext {
  userId: string;
  sessionId: string;
  systemState: SystemState;
  currentTime: Date;
  userLevel: 'beginner' | 'intermediate' | 'expert';
  currentWorkflow?: string;
  activeNodes: string[];
}

// 系统状态
export interface SystemState {
  cpuUsage: number;
  memoryUsage: number;
  apiStatus: Array<{
    id: string;
    status: APIStatus;
    lastCheck: Date;
  }>;
  activeWorkflows: string[];
  systemLoad: number;
}

// 用户行为
export interface UserBehavior {
  userId: string;
  sessionId: string;
  timestamp: Date;
  action: 'node_click' | 'workflow_start' | 'config_change' | 'error_occurred';
  targetId: string;
  targetType: 'node' | 'workflow' | 'config';
  context: {
    previousActions: string[];
    currentWorkflow?: string;
    activeNodes: string[];
    systemState: SystemState;
  };
  metadata: {
    duration?: number;
    success: boolean;
    errorType?: string;
    userLevel: 'beginner' | 'intermediate' | 'expert';
  };
}

// 行为模式
export interface BehaviorPattern {
  type: 'workflow_preference' | 'node_preference' | 'error_pattern' | 'time_pattern';
  targetId: string;
  confidence: number;
  frequency: number;
  lastUsed?: Date;
  severity?: 'low' | 'medium' | 'high';
}

// 动态节点推荐
export interface DynamicNodeRecommendation {
  nodeId: string;
  name: string;
  description: string;
  type: 'existing' | 'behavior_based' | 'workflow_based' | 'custom' | 'community' | 'generated';
  category: string;
  confidence: number;
  reason: string;
  metadata: {
    layer: string;
    complexity: number;
    estimatedTime: number;
    dependencies: string[];
    [key: string]: any;
  };
  actions: string[];
}

// 融合推荐
export interface FusedRecommendation {
  type: 'workflow' | 'node';
  id: string;
  name: string;
  description: string;
  confidence: number;
  originalConfidence: number;
  reason: string;
  category: string;
  estimatedTime: number;
  priority: number;
  successRate?: number;
  complexity?: number;
}

// 创建节点请求
export interface CreateNodeRequest {
  name: string;
  description: string;
  layer: string;
  category: string;
  requirements: string[];
  preferences: {
    complexity: number;
    performance: string;
    features: string[];
  };
}

// 工作流执行状态
export interface WorkflowExecution {
  id: string;
  workflowId: string;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';
  startTime: Date;
  endTime?: Date;
  currentPhase?: string;
  currentStepIndex?: number;
  completedPhases: string[];
  completedSteps?: number;
  failedSteps?: number;
  totalSteps?: number;
  steps?: WorkflowStepExecution[];
  errors: string[];
  priority?: number;
  context?: WorkflowContext;
  metadata?: {
    estimatedDuration: number;
    actualDuration: number;
    resourceUsage: {
      cpuUsage: number;
      memoryUsage: number;
      networkIO: number;
    };
    errorCount: number;
    warningCount: number;
  };
}

// 工作流程步骤执行状态
export interface WorkflowStepExecution {
  id: string;
  name: string;
  description: string;
  nodeIds: string[];
  estimatedDuration: number;
  dependencies: string[];
  parallel: boolean;
  required: boolean;
  status: 'pending' | 'running' | 'completed' | 'failed';
  startTime?: Date;
  endTime?: Date;
  duration?: number;
  nodeStates?: Record<string, any>;
  errors?: string[];
  warnings?: string[];
}

// 工作流程上下文
export interface WorkflowContext {
  userId: string;
  sessionId: string;
  systemState: SystemState;
  currentTime: Date;
  userLevel: 'beginner' | 'intermediate' | 'expert';
  currentWorkflow?: string;
  activeNodes: string[];
  parameters?: Record<string, any>;
}

// 事件类型
export interface NodeStateChangedEvent {
  nodeId: string;
  previousStatus: ExtendedNodeStatus;
  newStatus: ExtendedNodeStatus;
  timestamp: Date;
}

export interface NodeActivatedEvent {
  nodeId: string;
  timestamp: Date;
  activationTime: number;
}

export interface NodeErrorEvent {
  nodeId: string;
  error: string;
  timestamp: Date;
  recoverable: boolean;
}

export interface RecommendationUpdatedEvent {
  recommendations: FusedRecommendation[];
  context: RecommendationContext;
  timestamp: Date;
}

// 可视化连接
export interface VisualConnection {
  from: string;
  to: string;
  type: 'data' | 'control' | 'dependency';
  active: boolean;
  strength: number;
}

// 相似用户
export interface SimilarUser {
  userId: string;
  similarity: number;
  similarityText: string;
}

// 自定义节点
export interface CustomNode {
  id: string;
  name: string;
  description: string;
  layer: NodeLayer;
  complexity: number;
  estimatedTime: number;
  dependencies: string[];
  author: string;
  version: string;
  downloadCount: number;
  rating: number;
}

// 社区节点
export interface CommunityNode {
  id: string;
  name: string;
  description: string;
  layer: NodeLayer;
  complexity: number;
  estimatedTime: number;
  dependencies: string[];
  author: string;
  rating: number;
  usageCount: number;
}

// 相似节点
export interface SimilarNode {
  id: string;
  name: string;
  layer: NodeLayer;
  complexity: number;
  estimatedTime: number;
  dependencies: string[];
  similarity: number;
}

// 节点模板
export interface NodeTemplate {
  id: string;
  name: string;
  description: string;
  layer: NodeLayer;
  complexity: number;
  estimatedTime: number;
  dependencies: string[];
  template: any;
  generatedFrom: CreateNodeRequest;
}

// 架构连接定义
export interface ArchitectureConnection {
  id: string;
  from: string;
  to: string;
  type: 'data' | 'control' | 'dependency' | 'activation';
  strength: number;
  description: string;
  layer?: NodeLayer;
  bidirectional?: boolean;
  conditions?: string[];
}

// 数据流程层定义
export interface DataFlowLayer {
  id: string;
  name: string;
  description: string;
  level: number;
  nodes: string[];
  connections: ArchitectureConnection[];
  inputNodes: string[];
  outputNodes: string[];
  processingNodes: string[];
}

// 架构层级定义
export interface ArchitectureLayer {
  id: string;
  name: string;
  description: string;
  level: number;
  nodes: string[];
  connections: ArchitectureConnection[];
  parentLayer?: string;
  childLayers?: string[];
  responsibilities: string[];
}

// 功能模块定义
export interface FunctionModule {
  id: string;
  name: string;
  description: string;
  category: string;
  entryNodes: string[];
  exitNodes: string[];
  activationSequence: string[];
  dependencies: string[];
  estimatedDuration: number;
  requirements: string[];
  successCriteria: string[];
}

// 节点激活路径
export interface NodeActivationPath {
  id: string;
  name: string;
  description: string;
  nodes: string[];
  connections: ArchitectureConnection[];
  activationOrder: string[];
  parallelGroups: string[][];
  estimatedDuration: number;
  requirements: string[];
}
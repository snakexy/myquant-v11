/**
 * 节点ID映射服务
 * 
 * 解决工作流节点ID与节点状态管理器中节点ID不匹配的问题
 */

// 节点ID映射表
export const NODE_ID_MAPPING = {
  // 数据中枢层映射
  'data_hub.data_cleaner': 'DP1',  // 数据清洗节点映射
  'data_hub.core': 'DH1',
  'data_hub.unified_provider': 'DH2',
  'data_hub.cache_manager': 'DH3',
  'data_hub.pipeline': 'DH4',
  'data_hub.storage_manager': 'DH5',
  'data_hub.realtime_stream': 'DH6',
  'data_hub.quality_monitor': 'DH7',
  'data_hub.backup_service': 'DH8',
  
  // QLib核心层映射
  'qlib_core.data_processing': 'QL1',
  'qlib_core.analysis_integration': 'QL2',
  'qlib_core.backtest_system': 'QL3',
  'qlib_core.computation_optimization': 'QL4',
  'qlib_core.data_processing_advanced': 'QL5',
  'qlib_core.model_integration': 'QL6',
  'qlib_core.integration_interface': 'QL7',
  'qlib_core.preprocessing': 'QL8',
  'qlib_core.feature_engineering': 'QL9',
  'qlib_core.model_evaluation': 'QL10',
  
  // 业务逻辑层映射
  'business_logic.factor_engine': 'BL1',
  'business_logic.strategy_system': 'BL2',
  'business_logic.strategy_replay': 'BL3',
  'business_logic.model_management': 'BL4',
  'business_logic.investment_analysis': 'BL5',
  'business_logic.signal_generator': 'BL6',
  'business_logic.portfolio_management': 'BL7',
  'business_logic.performance_analysis': 'BL8',
  
  // AI策略层映射
  'ai_strategy.ai_strategy_lab': 'AI1',
  'ai_strategy.realtime_processing': 'AI2',
  'ai_strategy.meta_learning': 'AI3',
  'ai_strategy.multi_model_integration': 'AI4',
  'ai_strategy.strategy_generator': 'AI5',
  'ai_strategy.model_interpretability': 'AI6',
  'ai_strategy.nested_decision_engine': 'AI7',
  'ai_strategy.online_rolling_training': 'AI8',
  'ai_strategy.workflow_config': 'AI9',
  'ai_strategy.reinforcement_learning': 'AI10',
  'ai_strategy.deep_learning': 'AI11',
  'ai_strategy.nlp_processing': 'AI12',
  
  // 实盘交易层映射
  'live_trading.config_management': 'LT1',
  'live_trading.data_processor': 'LT2',
  'live_trading.realtime_monitor': 'LT3',
  'live_trading.stream_processing': 'LT4',
  'live_trading.trade_execution': 'LT5',
  'live_trading.risk_management': 'LT6',
  'live_trading.strategy_module': 'LT7',
  'live_trading.utils_module': 'LT8',
  'live_trading.order_management': 'LT9',
  'live_trading.position_management': 'LT10',
  'live_trading.settlement_system': 'LT11',
  
  // 实验管理层映射
  'experiment_mgmt.experiment_management': 'EM1',
  'experiment_mgmt.experiment_services': 'EM2',
  'experiment_mgmt.experiment_templates': 'EM3',
  'experiment_mgmt.experiment_web': 'EM4',
  'experiment_mgmt.automation_system': 'EM5',
  'experiment_mgmt.qlib_online_service': 'EM6',
  'experiment_mgmt.experiment_scheduler': 'EM7',
  'experiment_mgmt.result_analyzer': 'EM8',
  
  // 前端展示层映射
  'frontend.result_analyzer': 'UI1',
  'frontend.report_generator': 'UI2',
  'frontend.data_exporter': 'UI3',
  'frontend.visualization_renderer': 'UI4',
  'frontend.intelligent_node_system': 'UI5',
  'frontend.realtime_dashboard': 'UI6',
  'frontend.alert_system': 'UI7',
  'frontend.user_management': 'UI8',
  
  // 系统支持层映射
  'frontend.system_monitoring': 'SYS1',
  'frontend.log_management': 'SYS2',
  'frontend.config_center': 'SYS3',
  
  // 数据处理节点映射
  'data_processing.data_cleaning': 'DP1',
  'data_processing.data_transformation': 'DP2',
  'data_processing.data_validation': 'DP3',
  'data_processing.data_processor_core': 'DP4',
  
  // 分析节点映射
  'analysis.technical_analysis': 'AN1',
  'analysis.fundamental_analysis': 'AN2',
  'analysis.sentiment_analysis': 'AN3',
  'analysis.data_analysis_core': 'AN4',
  
  // 风险管理节点映射
  'risk.risk_identification': 'RM1',
  'risk.risk_quantification': 'RM2',
  'risk.risk_warning': 'RM3',
  'risk.risk_management': 'RM4',
  
  // AI模型节点映射
  'ml.machine_learning_platform': 'ML1',
  'ml.model_deployment': 'ML2',
  'ml.model_monitoring': 'ML3',
  
  // 交易支持节点映射
  'trading.market_data': 'TS1',
  'trading.broker_api': 'TS2',
  'trading.trading_statistics': 'TS3',
  
  // 应用服务层映射
  'application_service.workflow_engine': 'WS1',
  'application_service.config_management': 'CF1',
  'application_service.intelligent_alert_system': 'AS1',
  'application_service.collaboration_function': 'CL1',
  'application_service.task_scheduler': 'SC1',
  'application_service.report_output': 'RP1',
  'application_service.application_analysis': 'AP1',
  'application_service.monitoring_management': 'MG1',
  'application_service.log_management': 'LG1',
  'application_service.notification_service': 'NT1'
};

// 反向映射表（从节点状态管理器ID到工作流ID）
export const REVERSE_NODE_ID_MAPPING = Object.fromEntries(
  Object.entries(NODE_ID_MAPPING).map(([key, value]) => [value, key])
);

/**
 * 节点ID映射器类
 */
export class NodeIdMapper {
  /**
   * 将工作流节点ID映射到节点状态管理器ID
   * @param workflowNodeId 工作流中的节点ID
   * @returns 节点状态管理器中的节点ID
   */
  static workflowToStateManager(workflowNodeId: string): string {
    const mappedId = NODE_ID_MAPPING[workflowNodeId as keyof typeof NODE_ID_MAPPING];
    if (mappedId) {
      console.log(`节点ID映射: ${workflowNodeId} -> ${mappedId}`);
      return mappedId;
    }
    
    console.warn(`未找到工作流节点ID映射: ${workflowNodeId}，使用原始ID`);
    return workflowNodeId;
  }
  
  /**
   * 将节点状态管理器ID映射到工作流ID
   * @param stateManagerNodeId 节点状态管理器中的节点ID
   * @returns 工作流中的节点ID
   */
  static stateManagerToWorkflow(stateManagerNodeId: string): string {
    const mappedId = REVERSE_NODE_ID_MAPPING[stateManagerNodeId];
    if (mappedId) {
      console.log(`反向节点ID映射: ${stateManagerNodeId} -> ${mappedId}`);
      return mappedId;
    }
    
    console.warn(`未找到节点状态管理器ID反向映射: ${stateManagerNodeId}，使用原始ID`);
    return stateManagerNodeId;
  }
  
  /**
   * 批量映射工作流节点ID到节点状态管理器ID
   * @param workflowNodeIds 工作流节点ID数组
   * @returns 映射后的节点状态管理器ID数组
   */
  static batchWorkflowToStateManager(workflowNodeIds: string[]): string[] {
    return workflowNodeIds.map(id => this.workflowToStateManager(id));
  }
  
  /**
   * 批量映射节点状态管理器ID到工作流ID
   * @param stateManagerNodeIds 节点状态管理器ID数组
   * @returns 映射后的工作流ID数组
   */
  static batchStateManagerToWorkflow(stateManagerNodeIds: string[]): string[] {
    return stateManagerNodeIds.map(id => this.stateManagerToWorkflow(id));
  }
  
  /**
   * 检查工作流节点ID是否有映射
   * @param workflowNodeId 工作流节点ID
   * @returns 是否有映射
   */
  static hasWorkflowMapping(workflowNodeId: string): boolean {
    return workflowNodeId in NODE_ID_MAPPING;
  }
  
  /**
   * 检查节点状态管理器ID是否有反向映射
   * @param stateManagerNodeId 节点状态管理器ID
   * @returns 是否有反向映射
   */
  static hasStateManagerMapping(stateManagerNodeId: string): boolean {
    return stateManagerNodeId in REVERSE_NODE_ID_MAPPING;
  }
  
  /**
   * 获取所有映射关系
   * @returns 所有映射关系
   */
  static getAllMappings(): Record<string, string> {
    return { ...NODE_ID_MAPPING };
  }
  
  /**
   * 获取所有反向映射关系
   * @returns 所有反向映射关系
   */
  static getAllReverseMappings(): Record<string, string> {
    return { ...REVERSE_NODE_ID_MAPPING };
  }
  
  /**
   * 根据节点类型获取映射
   * @param nodeType 节点类型
   * @returns 该类型的所有映射
   */
  static getMappingsByType(nodeType: string): Record<string, string> {
    const mappings: Record<string, string> = {};
    const prefix = nodeType + '.';
    
    for (const [workflowId, stateManagerId] of Object.entries(NODE_ID_MAPPING)) {
      if (workflowId.startsWith(prefix)) {
        mappings[workflowId] = stateManagerId;
      }
    }
    
    return mappings;
  }
}

export default NodeIdMapper;
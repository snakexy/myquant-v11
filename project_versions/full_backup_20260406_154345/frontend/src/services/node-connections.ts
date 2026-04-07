// 节点连接关系管理器
export class NodeConnectionsManager {
  // 获取节点连接关系
  static getNodeConnections(): Array<{
    from: string;
    to: string;
    type: 'dependency' | 'dataflow' | 'control' | 'layer';
    strength: number;
  }> {
    const connections = [];
    
    // 基于依赖关系生成连接
    const dependencyConnections = this.getDependencyConnections();
    connections.push(...dependencyConnections);
    
    // 添加层内连接关系
    const layerConnections = this.getLayerConnections();
    connections.push(...layerConnections);
    
    // 添加数据流连接关系
    const dataFlowConnections = this.getDataFlowConnections();
    connections.push(...dataFlowConnections);
    
    // 添加控制流连接关系
    const controlFlowConnections = this.getControlFlowConnections();
    connections.push(...controlFlowConnections);
    
    return connections;
  }
  
  // 获取依赖关系连接
  private static getDependencyConnections(): Array<{
    from: string;
    to: string;
    type: 'dependency';
    strength: number;
  }> {
    const connections = [];
    
    // 数据中枢层依赖关系
    const dataHubDependencies = [
      ['DH1', 'DH2'], ['DH1', 'DH3'], ['DH1', 'DH4'], ['DH1', 'DH5'], ['DH1', 'DH6'], ['DH1', 'DH7'], ['DH1', 'DH8'],
      ['DH2', 'DH4'], ['DH2', 'DH6'], ['DH2', 'DP1'], ['DH2', 'DP2'], ['DH2', 'SK1'],
      ['DH4', 'DP1'], ['DH5', 'DH8'], ['DH6', 'SP1'], ['DH7', 'DP1'],
      ['DP1', 'DP2'], ['DP2', 'DP3'], ['DP3', 'DP4'], ['DP4', 'SP1']
    ];
    
    // QLib核心层依赖关系
    const qlibCoreDependencies = [
      ['DH1', 'QL1'], ['DH2', 'QL1'], ['DH1', 'QL2'], ['DH2', 'QL2'],
      ['QL1', 'QL2'], ['QL1', 'QL3'], ['QL1', 'QL4'], ['QL1', 'QL5'], ['QL1', 'QL7'], ['QL1', 'QL8'],
      ['QL2', 'QL3'], ['QL2', 'QL6'], ['QL2', 'QL7'], ['QL2', 'QL9'],
      ['QL3', 'QL6'], ['QL3', 'QL10'], ['QL4', 'QL9'], ['QL5', 'QL9'],
      ['QL6', 'QL10'], ['QL7', 'QL8'], ['QL8', 'QL9'], ['QL9', 'QL10']
    ];
    
    // 业务逻辑层依赖关系
    const businessLogicDependencies = [
      ['QL1', 'BL1'], ['QL9', 'BL1'],
      ['BL1', 'BL2'], ['BL1', 'BL4'], ['BL1', 'BL6'], ['BL1', 'AN1'],
      ['BL2', 'BL3'], ['BL4', 'BL6'], ['AN1', 'MK1'], ['UB1', 'BL1'], ['UB1', 'BL2'], ['UB1', 'BL5']
    ];
    
    // 投资分析系统依赖关系
    const investmentAnalysisDependencies = [
      ['BL1', 'BL5'], ['AN1', 'BL5'],
      ['BL5', 'BL7'], ['BL5', 'BL8'], ['BL5', 'IA1'], ['BL5', 'IA2'], ['BL5', 'IA4'],
      ['DH1', 'IA1'], ['DH2', 'AN2'], ['DH6', 'AN3'],
      ['AN2', 'AN3'], ['AN2', 'AN4'], ['AN3', 'AN4'],
      ['IA1', 'IA2'], ['IA2', 'IA3'], ['IA3', 'IA4'], ['IA4', 'BL7'], ['IA4', 'BL8']
    ];
    
    // AI智能策略层依赖关系
    const aiStrategyDependencies = [
      ['BL1', 'AI1'], ['BL2', 'AI1'],
      ['DH2', 'AI2'], ['AI1', 'AI2'],
      ['AI1', 'AI3'], ['AI1', 'AI4'], ['AI1', 'AI5'], ['AI1', 'AI6'], ['AI1', 'AI7'], ['AI1', 'AI8'], ['AI1', 'AI9'],
      ['AI2', 'AI4'], ['AI2', 'AI5'], ['AI2', 'AI8'], ['AI2', 'AI12'],
      ['AI3', 'AI4'], ['AI3', 'AI7'], ['AI3', 'AI10'], ['AI3', 'AI11'],
      ['AI4', 'AI6'], ['AI4', 'AI8'], ['AI4', 'AI12'],
      ['AI5', 'AI7'], ['AI5', 'AI9'],
      ['AI6', 'AI7'], ['AI6', 'MI1'],
      ['AI7', 'AI8'], ['AI7', 'AI9'],
      ['AI8', 'OL1'],
      ['AI9', 'AI5'],
      ['AI10', 'ML1'], ['AI11', 'ML1'], ['AI12', 'AI4'],
      ['ML1', 'ML2'], ['ML2', 'ML3'], ['ML3', 'MI1'],
      ['OL1', 'ML1'], ['MI1', 'AI6'], ['AA1', 'AI1'], ['AA1', 'AI2']
    ];
    
    // 实盘交易层依赖关系
    const liveTradingDependencies = [
      ['AI2', 'LT1'],
      ['LT1', 'LT2'], ['LT1', 'LT3'], ['LT1', 'LT5'], ['LT1', 'LT7'], ['LT1', 'LT8'],
      ['LT2', 'LT4'], ['LT2', 'LT8'], ['LT2', 'TS1'],
      ['LT3', 'LT4'], ['LT3', 'LT6'], ['LT3', 'RT1'],
      ['LT4', 'LT5'], ['LT4', 'TS1'],
      ['LT5', 'LT6'], ['LT5', 'LT7'], ['LT5', 'LT9'], ['LT5', 'TE1'],
      ['LT6', 'LT7'], ['LT6', 'RM1'], ['LT6', 'RM3'],
      ['LT7', 'LT8'], ['LT7', 'LT9'],
      ['LT8', 'LT9'], ['LT8', 'LT10'],
      ['LT9', 'LT10'], ['LT9', 'LT11'], ['LT9', 'TS2'],
      ['LT10', 'LT11'], ['LT10', 'TS2'],
      ['LT11', 'TS3'],
      ['TS1', 'LT4'], ['TS2', 'TE1'], ['TS3', 'BL8'],
      ['TE1', 'RM1'], ['RM1', 'RM2'], ['RM2', 'RM3'], ['RM3', 'RM4'], ['RM4', 'RK1']
    ];
    
    // 实验管理层依赖关系
    const experimentMgmtDependencies = [
      ['AI1', 'EM1'], ['AI3', 'EM1'],
      ['EM1', 'EM2'], ['EM1', 'EM3'], ['EM1', 'EM4'], ['EM1', 'EM5'], ['EM1', 'EM6'], ['EM1', 'EM7'], ['EM1', 'EM8'],
      ['EM2', 'EM5'], ['EM2', 'EM7'],
      ['EM3', 'EM4'], ['EM3', 'EM8'],
      ['EM4', 'EM8'],
      ['EM5', 'EM7'], ['EM5', 'AU1'],
      ['EM6', 'QO1'],
      ['EM7', 'EM8'], ['EM7', 'AU1'],
      ['AU1', 'QO1']
    ];
    
    // 应用服务层依赖关系
    const applicationServiceDependencies = [
      ['EM1', 'WS1'], ['EM5', 'WS1'],
      ['WS1', 'CF1'], ['WS1', 'AS1'], ['WS1', 'CL1'], ['WS1', 'SC1'], ['WS1', 'RP1'], ['WS1', 'AP1'], ['WS1', 'MG1'], ['WS1', 'LG1'], ['WS1', 'NT1'],
      ['CF1', 'WS1'], ['AS1', 'NT1'], ['CL1', 'NT1'], ['SC1', 'WS1'], ['RP1', 'WS1'], ['AP1', 'WS1'], ['MG1', 'WS1'], ['LG1', 'WS1'], ['NT1', 'AS1']
    ];
    
    // 添加所有依赖关系连接
    const allDependencyConnections = [
      ...dataHubDependencies,
      ...qlibCoreDependencies,
      ...businessLogicDependencies,
      ...investmentAnalysisDependencies,
      ...aiStrategyDependencies,
      ...liveTradingDependencies,
      ...experimentMgmtDependencies,
      ...applicationServiceDependencies
    ];
    
    for (const [from, to] of allDependencyConnections) {
      connections.push({
        from,
        to,
        type: 'dependency' as const,
        strength: 1.0
      });
    }
    
    return connections;
  }
  
  // 获取层内连接关系
  private static getLayerConnections(): Array<{
    from: string;
    to: string;
    type: 'layer';
    strength: number;
  }> {
    const connections = [];
    
    // 数据中枢层内连接
    const dataHubConnections = [
      ['DH1', 'DH2'], ['DH1', 'DH3'], ['DH1', 'DH5'], ['DH1', 'DH7'], ['DH1', 'DH8'],
      ['DH2', 'DH4'], ['DH2', 'DH6'], ['DH2', 'DP1'], ['DH2', 'SK1'],
      ['DH4', 'DP1'], ['DH5', 'DH8'], ['DH6', 'SP1'], ['DH7', 'DP1'],
      ['DP1', 'DP2'], ['DP2', 'DP3'], ['DP3', 'DP4'], ['DP4', 'SP1']
    ];
    
    // QLib核心层内连接
    const qlibCoreConnections = [
      ['QL1', 'QL2'], ['QL1', 'QL4'], ['QL1', 'QL5'], ['QL1', 'QL7'], ['QL1', 'QL8'],
      ['QL2', 'QL3'], ['QL2', 'QL6'], ['QL2', 'QL7'], ['QL2', 'QL9'],
      ['QL3', 'QL6'], ['QL3', 'QL10'], ['QL4', 'QL9'], ['QL5', 'QL9'],
      ['QL6', 'QL10'], ['QL7', 'QL8'], ['QL8', 'QL9'], ['QL9', 'QL10']
    ];
    
    // 业务逻辑层内连接
    const businessLogicConnections = [
      ['BL1', 'BL2'], ['BL1', 'BL4'], ['BL1', 'BL6'], ['BL1', 'AN1'],
      ['BL2', 'BL3'], ['BL4', 'BL6'], ['AN1', 'MK1'], ['UB1', 'BL1'], ['UB1', 'BL2'], ['UB1', 'BL5']
    ];
    
    // 投资分析系统层内连接
    const investmentAnalysisConnections = [
      ['BL5', 'BL7'], ['BL5', 'BL8'], ['BL5', 'IA1'], ['BL5', 'IA2'], ['BL5', 'IA4'],
      ['AN2', 'AN3'], ['AN2', 'AN4'], ['AN3', 'AN4'],
      ['IA1', 'IA2'], ['IA2', 'IA3'], ['IA3', 'IA4'], ['IA4', 'BL7'], ['IA4', 'BL8']
    ];
    
    // AI智能策略层内连接
    const aiStrategyConnections = [
      ['AI1', 'AI2'], ['AI1', 'AI3'], ['AI1', 'AI4'], ['AI1', 'AI5'], ['AI1', 'AI6'], ['AI1', 'AI7'], ['AI1', 'AI8'], ['AI1', 'AI9'],
      ['AI2', 'AI4'], ['AI2', 'AI5'], ['AI2', 'AI8'], ['AI2', 'AI12'],
      ['AI3', 'AI4'], ['AI3', 'AI7'], ['AI3', 'AI10'], ['AI3', 'AI11'],
      ['AI4', 'AI6'], ['AI4', 'AI8'], ['AI4', 'AI12'],
      ['AI5', 'AI7'], ['AI5', 'AI9'],
      ['AI6', 'AI7'], ['AI6', 'MI1'],
      ['AI7', 'AI8'], ['AI7', 'AI9'],
      ['AI8', 'OL1'],
      ['AI9', 'AI5'],
      ['AI10', 'ML1'], ['AI11', 'ML1'], ['AI12', 'AI4'],
      ['ML1', 'ML2'], ['ML2', 'ML3'], ['ML3', 'MI1'],
      ['OL1', 'ML1'], ['MI1', 'AI6'], ['AA1', 'AI1'], ['AA1', 'AI2']
    ];
    
    // 实盘交易层内连接
    const liveTradingConnections = [
      ['LT1', 'LT2'], ['LT1', 'LT3'], ['LT1', 'LT5'], ['LT1', 'LT7'], ['LT1', 'LT8'],
      ['LT2', 'LT4'], ['LT2', 'LT8'], ['LT2', 'TS1'],
      ['LT3', 'LT4'], ['LT3', 'LT6'], ['LT3', 'RT1'],
      ['LT4', 'LT5'], ['LT4', 'TS1'],
      ['LT5', 'LT6'], ['LT5', 'LT7'], ['LT5', 'LT9'], ['LT5', 'TE1'],
      ['LT6', 'LT7'], ['LT6', 'RM1'], ['LT6', 'RM3'],
      ['LT7', 'LT8'], ['LT7', 'LT9'],
      ['LT8', 'LT9'], ['LT8', 'LT10'],
      ['LT9', 'LT10'], ['LT9', 'LT11'], ['LT9', 'TS2'],
      ['LT10', 'LT11'], ['LT10', 'TS2'],
      ['LT11', 'TS3'],
      ['TS1', 'LT4'], ['TS2', 'TE1'], ['TS3', 'BL8'],
      ['TE1', 'RM1'], ['RM1', 'RM2'], ['RM2', 'RM3'], ['RM3', 'RM4'], ['RM4', 'RK1']
    ];
    
    // 实验管理层内连接
    const experimentMgmtConnections = [
      ['EM1', 'EM2'], ['EM1', 'EM3'], ['EM1', 'EM4'], ['EM1', 'EM5'], ['EM1', 'EM6'], ['EM1', 'EM7'], ['EM1', 'EM8'],
      ['EM2', 'EM5'], ['EM2', 'EM7'],
      ['EM3', 'EM4'], ['EM3', 'EM8'],
      ['EM4', 'EM8'],
      ['EM5', 'EM7'], ['EM5', 'AU1'],
      ['EM6', 'QO1'],
      ['EM7', 'EM8'], ['EM7', 'AU1'],
      ['AU1', 'QO1']
    ];
    
    // 应用服务层内连接
    const applicationServiceConnections = [
      ['WS1', 'CF1'], ['WS1', 'AS1'], ['WS1', 'CL1'], ['WS1', 'SC1'], ['WS1', 'RP1'], ['WS1', 'AP1'], ['WS1', 'MG1'], ['WS1', 'LG1'], ['WS1', 'NT1'],
      ['CF1', 'WS1'], ['AS1', 'NT1'], ['CL1', 'NT1'], ['SC1', 'WS1'], ['RP1', 'WS1'], ['AP1', 'WS1'], ['MG1', 'WS1'], ['LG1', 'WS1'], ['NT1', 'AS1']
    ];
    
    // 添加所有层内连接
    const allLayerConnections = [
      ...dataHubConnections,
      ...qlibCoreConnections,
      ...businessLogicConnections,
      ...investmentAnalysisConnections,
      ...aiStrategyConnections,
      ...liveTradingConnections,
      ...experimentMgmtConnections,
      ...applicationServiceConnections
    ];
    
    for (const [from, to] of allLayerConnections) {
      connections.push({
        from,
        to,
        type: 'layer' as const,
        strength: 0.8
      });
    }
    
    return connections;
  }
  
  // 获取数据流连接关系
  private static getDataFlowConnections(): Array<{
    from: string;
    to: string;
    type: 'dataflow';
    strength: number;
  }> {
    const connections = [];
    
    // 数据中枢层到业务逻辑层的数据流
    const dataToBusinessFlow = [
      ['DH1', 'BL1'], ['DH2', 'BL1'], ['DH4', 'BL1'], ['DH6', 'BL1'],
      ['DH1', 'AN1'], ['DH2', 'AN1'], ['DH4', 'AN1'],
      ['DH1', 'UB1'], ['DH2', 'UB1']
    ];
    
    // 业务逻辑层到投资分析系统的数据流
    const businessToInvestmentFlow = [
      ['BL1', 'BL5'], ['BL1', 'IA1'], ['BL1', 'IA2'],
      ['AN1', 'AN2'], ['AN1', 'AN3'], ['AN1', 'AN4'],
      ['UB1', 'BL5'], ['UB1', 'BL7'], ['UB1', 'BL8']
    ];
    
    // 投资分析系统到AI智能策略层的数据流
    const investmentToAiFlow = [
      ['BL5', 'AI1'], ['BL5', 'AI2'], ['BL5', 'AI3'],
      ['IA1', 'AI1'], ['IA2', 'AI2'], ['IA3', 'AI3'], ['IA4', 'AI4'],
      ['AN2', 'AI12'], ['AN3', 'AI12'], ['AN4', 'AI6']
    ];
    
    // AI智能策略层到实盘交易层的数据流
    const aiToTradingFlow = [
      ['AI1', 'LT1'], ['AI2', 'LT1'], ['AI2', 'LT2'],
      ['AI5', 'LT5'], ['AI7', 'LT7'], ['AI8', 'LT4'],
      ['ML2', 'LT5'], ['OL1', 'LT2']
    ];
    
    // 实盘交易层到实验管理层的数据流
    const tradingToExperimentFlow = [
      ['LT3', 'EM1'], ['LT5', 'EM1'], ['LT11', 'EM1'],
      ['TS3', 'EM8'], ['RK1', 'EM1']
    ];
    
    // 实验管理层到应用服务层的数据流
    const experimentToApplicationFlow = [
      ['EM1', 'WS1'], ['EM2', 'WS1'], ['EM5', 'SC1'],
      ['EM6', 'QO1'], ['EM8', 'RP1']
    ];
    
    // 应用服务层到前端展示层的数据流
    const applicationToFrontendFlow = [
      ['WS1', 'UI1'], ['CF1', 'UI2'], ['AS1', 'UI7'],
      ['RP1', 'UI2'], ['MG1', 'UI6'], ['LG1', 'UI2']
    ];
    
    // 添加所有数据流连接
    const allDataFlowConnections = [
      ...dataToBusinessFlow,
      ...businessToInvestmentFlow,
      ...investmentToAiFlow,
      ...aiToTradingFlow,
      ...tradingToExperimentFlow,
      ...experimentToApplicationFlow,
      ...applicationToFrontendFlow
    ];
    
    for (const [from, to] of allDataFlowConnections) {
      connections.push({
        from,
        to,
        type: 'dataflow' as const,
        strength: 0.9
      });
    }
    
    return connections;
  }
  
  // 获取控制流连接关系
  private static getControlFlowConnections(): Array<{
    from: string;
    to: string;
    type: 'control';
    strength: number;
  }> {
    const connections = [];
    
    // 工作流引擎的控制流
    const workflowControlFlow = [
      ['WS1', 'EM1'], ['WS1', 'EM5'], ['WS1', 'SC1'],
      ['WS1', 'CF1'], ['WS1', 'AS1'], ['WS1', 'MG1']
    ];
    
    // 配置管理的控制流
    const configControlFlow = [
      ['CF1', 'DH1'], ['CF1', 'QL1'], ['CF1', 'BL1'],
      ['CF1', 'AI1'], ['CF1', 'LT1'], ['CF1', 'EM1']
    ];
    
    // 警报系统的控制流
    const alertControlFlow = [
      ['AS1', 'LT3'], ['AS1', 'RM3'], ['AS1', 'RK1'],
      ['AS1', 'MG1'], ['AS1', 'NT1']
    ];
    
    // 监控管理的控制流
    const monitoringControlFlow = [
      ['MG1', 'SYS1'], ['MG1', 'SYS2'], ['MG1', 'SYS3'],
      ['MG1', 'UI6'], ['MG1', 'UI7']
    ];
    
    // 添加所有控制流连接
    const allControlFlowConnections = [
      ...workflowControlFlow,
      ...configControlFlow,
      ...alertControlFlow,
      ...monitoringControlFlow
    ];
    
    for (const [from, to] of allControlFlowConnections) {
      connections.push({
        from,
        to,
        type: 'control' as const,
        strength: 0.7
      });
    }
    
    return connections;
  }
}

export default NodeConnectionsManager;
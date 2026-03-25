<template>
  <div class="simple-intelligent-node-system">
    <!-- 头部控制面板 -->
    <div class="control-panel">
      <h1 class="system-title">智能量化平台节点可视化系统</h1>
      <div class="workflow-controls">
        <span>选择工作流程：</span>
        <select v-model="selectedWorkflow" @change="handleWorkflowChange">
          <option value="ai-strategy">AI策略生成流程 (61节点)</option>
          <option value="traditional">传统策略执行 (25节点)</option>
          <option value="model-training">模型训练流程 (33节点)</option>
          <option value="qlib-online">QLib在线服务 (19节点)</option>
          <option value="all">全部节点 (62节点)</option>
        </select>
        <button @click="activateWorkflow" :disabled="isActivating">
          {{ isActivating ? '激活中...' : '激活流程' }}
        </button>
        <button @click="resetNodes">重置</button>
      </div>
      <div class="status-info">
        <span>总节点数：{{ totalNodes }}</span>
        <span>激活节点：{{ activeNodes }}</span>
        <span>状态：{{ systemStatus }}</span>
      </div>
    </div>

    <!-- 节点系统主体 -->
    <div class="node-container" ref="nodeContainer">
      <!-- 连接线SVG - 电路板风格 -->
      <svg class="connections-svg" v-show="!isDraggingGlobal">
        <defs>
          <marker id="arrow" markerWidth="6" markerHeight="6" refX="6" refY="2.5" orient="auto">
            <polygon points="0 0, 6 2.5, 0 5" fill="#4a90e2" />
          </marker>
          <marker id="arrow-active" markerWidth="6" markerHeight="6" refX="6" refY="2.5" orient="auto">
            <polygon points="0 0, 6 2.5, 0 5" fill="#00ff88" />
          </marker>
        </defs>
        <path v-for="connection in visibleConnections"
              :key="`${connection.from}-${connection.to}`"
              :d="getCircuitPath(connection)"
              :stroke="getConnectionColor(connection)"
              :stroke-width="getConnectionWidth(connection)"
              :stroke-dasharray="connection.isDashed ? '3,3' : 'none'"
              fill="none"
              :marker-end="getConnectionMarker(connection)"
              class="circuit-line" />
      </svg>

      <!-- 节点 -->
      <div v-for="node in visibleNodes"
           :key="node.id"
           class="node"
           :class="{ active: isNodeActive(node.id), dragging: node.isDragging }"
           :style="getNodeStyle(node)"
           @click="handleNodeClick(node, $event)"
           @mousedown="startDrag(node, $event)"
           :title="node.description">
        <div class="node-icon">{{ getNodeTypeIcon(node.type) }}</div>
        <div class="node-title">{{ node.name }}</div>
        <div class="node-id">{{ node.id }}</div>
      </div>
    </div>

    <!-- 节点详情面板 -->
    <div v-if="selectedNode" class="info-panel">
      <h3>节点详情</h3>
      <p><strong>{{ selectedNode.name }}</strong> ({{ selectedNode.id }})</p>
      <p>{{ selectedNode.description }}</p>
      <p>类型：{{ selectedNode.type }}</p>
      <p>层级：第{{ selectedNode.layer }}层</p>
      <button @click="selectedNode = null">关闭</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, reactive, onUnmounted } from 'vue'

// 状态管理
const selectedWorkflow = ref('ai-strategy')
const isActivating = ref(false)
const systemStatus = ref('idle')
const selectedNode = ref(null)

// 跟踪拖拽状态以避免点击/拖拽冲突
const hasDragged = ref(false)
const dragStartTime = ref(0)

// 工作流节点配置 - 更新为现有的节点ID
const workflowNodes = {
  'ai-strategy': ['UP', 'CM', 'DP', 'SM', 'MON', 'EXP', 'QD', 'QA', 'QF', 'QE', 'FE', 'SS', 'SR', 'MM', 'IA', 'QB', 'QP', 'QI', 'ASL', 'AE', 'ML', 'DL', 'OT', 'SG', 'MI', 'ND', 'META', 'RP', 'MC', 'EC', 'ES', 'MLPipeline', 'ModelTrain', 'ModelEval', 'StrategyGen', 'AutoML', 'RLearning', 'FeatureEng', 'TE', 'RS', 'ST', 'UT', 'Monitor', 'Logger', 'ExpDesigner', 'ParamOpt', 'ExpMonitor', 'ResultAnlys', 'Dashboard', 'UserAuth', 'AlertSys'],
  'traditional': ['UP', 'CM', 'DP', 'SM', 'MON', 'QD', 'QA', 'QF', 'QE', 'FE', 'SS', 'SR', 'IA', 'QB', 'QP', 'TE', 'RS', 'ST', 'UT', 'Monitor', 'Config', 'Dashboard', 'UserAuth', 'GlobalSet', 'RepSys'],
  'model-training': ['UP', 'CM', 'SM', 'QD', 'QF', 'QE', 'MM', 'ASL', 'AE', 'ML', 'DL', 'OT', 'MI', 'ND', 'META', 'EC', 'ES', 'MLPipeline', 'ModelTrain', 'ModelEval', 'FeatureStore', 'AutoML', 'RLearning', 'FeatureEng', 'DataPipe', 'MLMonitor', 'ExpDesigner', 'ParamOpt', 'ExpMonitor', 'VerControl'],
  'qlib-online': ['QD', 'QA', 'QF', 'QE', 'QB', 'QP', 'QI', 'UP', 'CM', 'FE', 'SS', 'AE', 'TE', 'RS', 'Dashboard', 'UserAuth', 'Logger', 'Config', 'GlobalSet'],
  'all': []
}


// 工作流节点定义 - 智能分层流水线布局
const createNodeLayout = () => {
  const nodeDefinitions = [
    // === AI策略生成流程节点定义 ===
    { id: 'UP', name: '统一数据提供器', type: 'cluster', layer: 1, description: '多源数据整合' },
    { id: 'DP', name: '数据管道', type: 'process', layer: 1, description: '预处理/标准化' },
    { id: 'CM', name: '缓存管理器', type: 'data', layer: 1, description: '智能缓存策略' },
    { id: 'SM', name: '存储管理器', type: 'data', layer: 1, description: '热冷数据分离' },
    { id: 'MON', name: '监控系统', type: 'monitor', layer: 1, description: '数据质量监控' },
    { id: 'QD', name: 'QLib数据提供器', type: 'data', layer: 1, description: '数据标准化' },
    { id: 'QA', name: 'QLib分析器', type: 'analysis', layer: 1, description: '专业性能分析' },
    { id: 'QF', name: 'QLib因子引擎', type: 'process', layer: 1, description: '表达式计算' },
    { id: 'QE', name: 'QLib环境管理', type: 'tool', layer: 1, description: '缓存优化' },
    { id: 'FE', name: '因子计算引擎', type: 'process', layer: 2, description: 'Alpha158/Alpha360' },
    { id: 'ML', name: '多模型框架', type: 'deployment', layer: 2, description: 'LightGBM/XGBoost/Transformer' },
    { id: 'DL', name: '深度学习模型', type: 'thunderbolt', layer: 2, description: 'MLP/LSTM/CNN/GNN' },
    { id: 'AE', name: 'AI策略引擎', type: 'robot', layer: 2, description: '深度学习模型' },
    { id: 'SS', name: '策略系统', type: 'cluster', layer: 2, description: '策略管理/执行' },
    { id: 'SR', name: '策略回放系统', type: 'analysis', layer: 2, description: '性能分析' },
    { id: 'IA', name: '投资分析系统', type: 'cluster', layer: 2, description: '组合分析/归因分析' },
    { id: 'SG', name: '策略生成器', type: 'function', layer: 3, description: '模型到策略转换' },
    { id: 'OT', name: '在线滚动训练', type: 'sync', layer: 3, description: '增量学习/模型更新' },
    { id: 'RP', name: 'AI实时处理', type: 'thunderbolt', layer: 3, description: '特征提取/模式检测' },
    { id: 'ND', name: '嵌套决策引擎', type: 'router', layer: 3, description: '多时间尺度决策' },
    { id: 'MC', name: '元控制器', type: 'switcher', layer: 3, description: '系统协调/流程管理' },
    { id: 'ST', name: '策略模块', type: 'cluster', layer: 5, description: '策略引擎/信号生成' },
    { id: 'TE', name: '交易执行', type: 'safety', layer: 5, description: '券商接口/订单管理' },
    { id: 'RS', name: '风险管理', type: 'security', layer: 5, description: '实时风险/仓位管理' },
    { id: 'UT', name: '工具模块', type: 'tool', layer: 5, description: '技术指标/数据压缩' },
    { id: 'Monitor', name: '实时监控', type: 'monitor', layer: 5, description: '系统实时监控' },
    { id: 'Logger', name: '日志记录', type: 'bug', layer: 5, description: '交易日志记录' },
    { id: 'Config', name: '配置管理', type: 'setting', layer: 5, description: '系统配置管理' },
    { id: 'ExpDesigner', name: '实验设计器', type: 'experiment', layer: 6, description: '策略实验设计' },
    { id: 'ExpMonitor', name: '实验监控', type: 'monitor', layer: 6, description: '实验执行监控' },
    { id: 'ParamOpt', name: '参数优化', type: 'tool', layer: 6, description: '参数调优工具' },
    { id: 'ResultAnlys', name: '结果分析', type: 'analysis', layer: 6, description: '实验结果分析' },
    { id: 'Dashboard', name: '系统概览', type: 'monitor', layer: 7, description: '系统整体状态' },
    { id: 'UserAuth', name: '用户认证', type: 'security', layer: 7, description: '用户身份验证' },
    { id: 'AlertSys', name: '警报系统', type: 'api', layer: 7, description: '智能警报通知' },

    // 其他支持节点
    { id: 'MM', name: '模型管理服务', type: 'data', layer: 2, description: '模型训练/评估' },
    { id: 'FeatureEng', name: '特征工程', type: 'process', layer: 4, description: '特征工程/选择' },
    { id: 'FeatureStore', name: '特征存储', type: 'database', layer: 4, description: '特征数据存储' },
    { id: 'MLPipeline', name: 'ML流水线', type: 'process', layer: 4, description: '机器学习流水线' },
    { id: 'DataPipe', name: '数据管道', type: 'sync', layer: 4, description: '数据预处理管道' },
    { id: 'ModelTrain', name: '模型训练', type: 'deployment', layer: 4, description: '模型训练服务' },
    { id: 'ModelEval', name: '模型评估', type: 'analysis', layer: 4, description: '模型性能评估' },
    { id: 'MLMonitor', name: 'ML监控', type: 'monitor', layer: 4, description: 'ML模型监控' },
    { id: 'AutoML', name: 'AutoML', type: 'robot', layer: 4, description: '自动化机器学习' },
    { id: 'RLearning', name: '强化学习', type: 'thunderbolt', layer: 4, description: '强化学习引擎' },
    { id: 'StrategyGen', name: '策略生成', type: 'function', layer: 4, description: '自动策略生成' },
    { id: 'ASL', name: 'AI策略实验室', type: 'cluster', layer: 2, description: 'DeepSeek API集成' },
    { id: 'Signal', name: '信号处理', type: 'sync', layer: 5, description: '交易信号处理' },
    { id: 'QB', name: 'QLib回测引擎', type: 'analysis', layer: 2, description: '真实QLib框架' },
    { id: 'QP', name: 'QLib数据处理', type: 'process', layer: 2, description: '质量控制/指标计算' },
    { id: 'QI', name: 'QLib集成', type: 'integration', layer: 2, description: '工作流管理' },
    { id: 'MI', name: '模型可解释性', type: 'bug', layer: 3, description: 'SHAP/特征重要性' },
    { id: 'META', name: '元学习系统', type: 'experiment', layer: 3, description: 'DDG-DA/迁移学习' },
    { id: 'EC', name: '实验管理核心', type: 'cluster', layer: 3, description: 'Qlib Recorder扩展' },
    { id: 'ES', name: '实验服务', type: 'api', layer: 3, description: '实验/记录/分析' },
    { id: 'PM', name: '投资组合管理', type: 'data', layer: 5, description: '投资组合优化' },
    { id: 'BrokerAPI', name: '券商接口', type: 'api', layer: 5, description: '多券商API集成' },
    { id: 'OrderMgr', name: '订单管理', type: 'data', layer: 5, description: '订单执行管理' },
    { id: 'VerControl', name: '版本控制', type: 'api', layer: 6, description: '实验版本管理' },
    { id: 'PerfCompare', name: '性能对比', type: 'function', layer: 6, description: '策略性能对比' },
    { id: 'RiskMetrics', name: '风险指标', type: 'security', layer: 6, description: '风险评估指标' },
    { id: 'ReportGen', name: '报告生成', type: 'bug', layer: 6, description: '自动报告生成' },
    { id: 'ExpStorage', name: '实验存储', type: 'database', layer: 6, description: '实验数据存储' },
    { id: 'NotifChan', name: '通知渠道', type: 'sync', layer: 7, description: '多渠道通知配置' },
    { id: 'GlobalSet', name: '全局设置', type: 'setting', layer: 7, description: '系统全局配置' },
    { id: 'ThemeMgmt', name: '主题管理', type: 'desktop', layer: 7, description: '界面主题设置' },
    { id: 'RepSys', name: '报表系统', type: 'analysis', layer: 7, description: '报表生成分析' },
    { id: 'ExportSys', name: '导出系统', type: 'api', layer: 7, description: '数据导出功能' },
    { id: 'MLflow', name: 'MLflow', type: 'experiment', layer: 7, description: 'ML生命周期管理' },
    { id: 'TensorBoard', name: 'TensorBoard', type: 'monitor', layer: 7, description: '模型训练可视化' },
    { id: 'EXP', name: '导出器系统', type: 'api', layer: 1, description: 'QLib桥接器' },
    { id: 'HyperTune', name: '超参优化', type: 'tool', layer: 4, description: '超参数调优' },
    { id: 'Ensemble', name: '集成学习', type: 'cluster', layer: 4, description: '模型集成方法' }
  ]

  const canvasWidth = 2400
  const canvasHeight = 1000
  const nodeWidth = 140
  const nodeHeight = 55
  const horizontalSpacing = 200
  const verticalSpacing = 100

  // 横向流水线布局配置 - 按业务流程从左到右
  const pipelineLayout = {
    // 第1阶段：数据源与采集
    stage1_data: {
      x: 50, y: 200, width: 220, height: 450,
      nodes: ['UP', 'DP', 'CM', 'SM', 'MON', 'QD']
    },

    // 第2阶段：数据处理与分析
    stage2_processing: {
      x: 320, y: 200, width: 220, height: 450,
      nodes: ['QA', 'QF', 'QE', 'FE', 'FeatureEng', 'DataPipe']
    },

    // 第3阶段：模型训练与优化
    stage3_modeling: {
      x: 590, y: 200, width: 240, height: 450,
      nodes: ['ML', 'DL', 'AutoML', 'RLearning', 'MLPipeline', 'ModelTrain', 'ModelEval', 'MLMonitor', 'HyperTune', 'Ensemble']
    },

    // 第4阶段：策略生成与回测
    stage4_strategy: {
      x: 880, y: 200, width: 220, height: 450,
      nodes: ['AE', 'StrategyGen', 'ASL', 'QB', 'QP', 'QI', 'SS', 'SR', 'MM']
    },

    // 第5阶段：投资分析与决策
    stage5_analysis: {
      x: 1150, y: 200, width: 220, height: 450,
      nodes: ['IA', 'SG', 'OT', 'RP', 'ND', 'MC', 'MI', 'META']
    },

    // 第6阶段：交易执行与管理
    stage6_execution: {
      x: 1420, y: 200, width: 220, height: 450,
      nodes: ['ST', 'TE', 'RS', 'PM', 'BrokerAPI', 'OrderMgr', 'UT', 'Monitor', 'Logger', 'Config', 'Signal']
    },

    // 第7阶段：实验与优化
    stage7_experiment: {
      x: 1690, y: 200, width: 240, height: 450,
      nodes: ['EC', 'ES', 'ExpDesigner', 'ExpMonitor', 'ParamOpt', 'FeatureStore', 'VerControl', 'PerfCompare', 'RiskMetrics', 'ReportGen', 'ExpStorage']
    },

    // 第8阶段：系统管理与展示
    stage8_management: {
      x: 1980, y: 200, width: 300, height: 450,
      nodes: ['Dashboard', 'UserAuth', 'AlertSys', 'NotifChan', 'GlobalSet', 'ThemeMgmt', 'RepSys', 'ExportSys', 'MLflow', 'TensorBoard']
    }
  }

  const layoutNodes = []

  // 为每个阶段计算节点位置 - 横向流水线排列
  Object.entries(pipelineLayout).forEach(([stageName, config]) => {
    const { x: stageX, y: stageY, width: stageWidth, height: stageHeight, nodes: stageNodes } = config

    // 在每个阶段内垂直排列节点
    const maxNodesPerColumn = Math.floor(stageHeight / (nodeHeight + 30))
    const nodeSpacing = Math.min(verticalSpacing, (stageHeight - maxNodesPerColumn * nodeHeight) / Math.max(maxNodesPerColumn - 1, 1))

    stageNodes.forEach((nodeId, index) => {
      const nodeDef = nodeDefinitions.find(n => n.id === nodeId)
      if (nodeDef) {
        const column = Math.floor(index / maxNodesPerColumn)
        const row = index % maxNodesPerColumn

        const x = stageX + column * (nodeWidth + 40)
        const y = stageY + row * (nodeHeight + nodeSpacing + 10)

        layoutNodes.push({
          ...nodeDef,
          x: x,
          y: y,
          width: nodeWidth,
          height: nodeHeight,
          isDragging: false
        })
      }
    })
  })

  return layoutNodes
}

const nodes = ref(createNodeLayout())

// 按工作流程顺序的连接关系
const connections = ref([
  // === 主要工作流路径 ===

  // 数据源 -> 数据处理
  { from: 'UP', to: 'DP' },
  { from: 'DB1', to: 'UP' },
  { from: 'CACHE1', to: 'CM' },
  { from: 'DP', to: 'CM' },
  { from: 'CM', to: 'SM' },
  { from: 'SM', to: 'MON' },

  // 数据处理 -> QLib集成
  { from: 'DP', to: 'QD' },
  { from: 'CM', to: 'QD', isDashed: true },
  { from: 'SM', to: 'QE', isDashed: true },
  { from: 'MON', to: 'QA', isDashed: true },
  { from: 'QD', to: 'QA' },
  { from: 'QA', to: 'QF' },
  { from: 'QF', to: 'QE' },

  // QLib -> 因子计算
  { from: 'QD', to: 'FE' },
  { from: 'QF', to: 'FE', isDashed: true },
  { from: 'FE', to: 'FeatureEng' },
  { from: 'FeatureEng', to: 'FeatureStore' },

  // 数据流水线 -> 模型训练
  { from: 'FE', to: 'MLPipeline' },
  { from: 'FeatureStore', to: 'MLPipeline', isDashed: true },
  { from: 'MLPipeline', to: 'DataPipe' },
  { from: 'DataPipe', to: 'ModelTrain' },
  { from: 'ModelTrain', to: 'ModelEval' },
  { from: 'ModelEval', to: 'MLMonitor' },

  // 模型训练 -> AI模型
  { from: 'ModelTrain', to: 'ML' },
  { from: 'ML', to: 'DL' },
  { from: 'DL', to: 'AutoML' },
  { from: 'AutoML', to: 'RLearning' },

  // AI模型 -> 策略生成
  { from: 'AE', to: 'StrategyGen' },
  { from: 'ML', to: 'AE' },
  { from: 'DL', to: 'AE' },
  { from: 'AutoML', to: 'StrategyGen' },
  { from: 'RLearning', to: 'StrategyGen' },
  { from: 'StrategyGen', to: 'ASL' },

  // 策略生成 -> 策略分析
  { from: 'StrategyGen', to: 'SS' },
  { from: 'ASL', to: 'SS' },
  { from: 'SS', to: 'SR' },
  { from: 'SR', to: 'IA' },
  { from: 'IA', to: 'SG' },

  // 策略分析 -> 实时处理
  { from: 'SG', to: 'OT' },
  { from: 'IA', to: 'RP' },
  { from: 'RP', to: 'ND' },
  { from: 'ND', to: 'MC' },

  // 实时处理 -> 交易执行
  { from: 'SS', to: 'ST' },
  { from: 'ST', to: 'Signal' },
  { from: 'Signal', to: 'TE' },
  { from: 'TE', to: 'RS' },
  { from: 'OT', to: 'ST', isDashed: true },

  // 交易执行 -> 监控与日志
  { from: 'ST', to: 'Monitor' },
  { from: 'TE', to: 'UT' },
  { from: 'RS', to: 'Logger' },
  { from: 'Monitor', to: 'Logger' },
  { from: 'Logger', to: 'Config' },

  // 监控 -> 实验管理
  { from: 'Monitor', to: 'ExpMonitor' },
  { from: 'ExpMonitor', to: 'ExpDesigner' },
  { from: 'ExpDesigner', to: 'ParamOpt' },
  { from: 'ParamOpt', to: 'ResultAnlys' },

  // 实验管理 -> 用户界面
  { from: 'ResultAnlys', to: 'Dashboard' },
  { from: 'ExpMonitor', to: 'Dashboard', isDashed: true },
  { from: 'Dashboard', to: 'UserAuth' },
  { from: 'Dashboard', to: 'AlertSys' },

  // === 辅助连接 ===

  // 模型管理支持
  { from: 'MM', to: 'ModelTrain', isDashed: true },
  { from: 'MM', to: 'AE', isDashed: true },

  // QLib回测支持
  { from: 'QB', to: 'SS' },
  { from: 'QP', to: 'FE' },
  { from: 'QI', to: 'ExpDesigner', isDashed: true },

  // 投资组合和风险管理
  { from: 'IA', to: 'PM' },
  { from: 'RS', to: 'PM' },
  { from: 'BrokerAPI', to: 'TE' },
  { from: 'OrderMgr', to: 'TE' },

  // 实验支持
  { from: 'VerControl', to: 'ExpMonitor' },
  { from: 'PerfCompare', to: 'ResultAnlys' },
  { from: 'RiskMetrics', to: 'RS' },
  { from: 'ReportGen', to: 'ResultAnlys' },
  { from: 'ExpStorage', to: 'ResultAnlys' },

  // 系统配置和通知
  { from: 'GlobalSet', to: 'Config' },
  { from: 'AlertSys', to: 'NotifChan' },
  { from: 'ThemeMgmt', to: 'Dashboard' },
  { from: 'RepSys', to: 'Dashboard' },

  // ML工具集成
  { from: 'MLflow', to: 'ModelTrain' },
  { from: 'TensorBoard', to: 'ModelTrain' },
  { from: 'ExportSys', to: 'Dashboard' },

  // 元学习支持
  { from: 'META', to: 'AutoML', isDashed: true },
  { from: 'MI', to: 'ModelEval' },

  // 数据导出
  { from: 'EXP', to: 'QI' }
])

// 节点激活状态
const activeNodesSet = reactive(new Set())

// 层级颜色配置 - 只设置边框颜色
const layerColors = {
  1: { border: '#2196F3' },  // 蓝色
  2: { border: '#9C27B0' },  // 紫色
  3: { border: '#009688' },  // 青色
  4: { border: '#FF9800' },  // 橙色
  5: { border: '#F44336' },  // 红色
  6: { border: '#607D8B' },  // 蓝灰色
  7: { border: '#795548' }   // 棕色
}

// 计算属性
const totalNodes = computed(() => nodes.value.length)
const activeNodes = computed(() => activeNodesSet.size)

// 根据当前工作流显示节点
const visibleNodes = computed(() => {
  const workflowNodeIds = workflowNodes[selectedWorkflow.value] || nodes.value.map(n => n.id)
  return nodes.value.filter(node => workflowNodeIds.includes(node.id))
})

// 根据当前工作流显示连接线 - 只显示两个端点都在当前工作流中的连接线
const visibleConnections = computed(() => {
  const workflowNodeIds = workflowNodes[selectedWorkflow.value] || nodes.value.map(n => n.id)
  return connections.value.filter(connection =>
    workflowNodeIds.includes(connection.from) && workflowNodeIds.includes(connection.to)
  )
})

// 方法
const isNodeActive = (nodeId) => activeNodesSet.has(nodeId)

const handleWorkflowChange = () => {
  resetNodes()
  // 根据选中的工作流程重新布局节点
  relayoutNodesForWorkflow(selectedWorkflow.value)
}

// 根据工作流程重新布局节点
const relayoutNodesForWorkflow = (workflowName) => {
  const workflowNodeIds = workflowNodes[workflowName]
  if (!workflowNodeIds || workflowNodeIds.length === 0) {
    return
  }

  const nodeWidth = 100
  const nodeHeight = 45
  const horizontalSpacing = 120
  const verticalSpacing = 70
  const canvasWidth = 2000
  const canvasHeight = 1000

  // 获取当前工作流程的节点
  const workflowNodesList = nodes.value.filter(node => workflowNodeIds.includes(node.id))

  // 按层级组织节点
  const nodesByLayer = {}
  workflowNodesList.forEach(node => {
    if (!nodesByLayer[node.layer]) {
      nodesByLayer[node.layer] = []
    }
    nodesByLayer[node.layer].push(node)
  })

  // 为每个层级的节点计算新位置
  Object.keys(nodesByLayer).forEach(layer => {
    const layerNodes = nodesByLayer[layer]
    const layerIndex = parseInt(layer) - 1
    const x = 50 + layerIndex * horizontalSpacing
    const totalHeight = layerNodes.length * verticalSpacing
    const startY = Math.max(50, (canvasHeight - totalHeight) / 2)

    layerNodes.forEach((node, nodeIndex) => {
      node.x = x
      node.y = startY + nodeIndex * verticalSpacing
    })
  })

  // 将不在当前工作流程的节点移到边缘
  nodes.value.forEach(node => {
    if (!workflowNodeIds.includes(node.id)) {
      node.x = canvasWidth - nodeWidth - 50
      node.y = Math.random() * (canvasHeight - nodeHeight - 100) + 50
    }
  })
}

const activateWorkflow = async () => {
  isActivating.value = true
  systemStatus.value = 'activating'

  const workflowNodeIds = workflowNodes[selectedWorkflow.value] || nodes.value.map(n => n.id)

  for (let i = 0; i < workflowNodeIds.length; i++) {
    const nodeId = workflowNodeIds[i]
    await new Promise(resolve => setTimeout(resolve, 50))
    activeNodesSet.add(nodeId)
  }

  systemStatus.value = 'running'
  isActivating.value = false
}

const resetNodes = () => {
  activeNodesSet.clear()
  systemStatus.value = 'idle'
}

const handleNodeClick = (node, event) => {
  // 如果刚刚结束拖拽，则不触发点击事件
  if (hasDragged.value) {
    hasDragged.value = false
    return
  }
  selectedNode.value = node
}

const selectNode = (node) => {
  selectedNode.value = node
}

// 拖拽状态管理
const dragState = reactive({
  isDragging: false,
  draggedNode: null,
  dragOffset: { x: 0, y: 0 }
})

// 拖拽时暂停连接线渲染
const isDraggingGlobal = ref(false)

// 修复的拖拽功能
const startDrag = (node, event) => {
  if (event.button !== 0) return // 只响应左键

  event.preventDefault()
  event.stopPropagation()

  // 初始化拖拽状态
  hasDragged.value = false
  dragStartTime.value = Date.now()

  // 清除之前的事件监听器（如果存在）
  document.removeEventListener('mousemove', handleMouseMove)
  document.removeEventListener('mouseup', stopDrag)

  dragState.isDragging = true
  dragState.draggedNode = node
  node.isDragging = true
  isDraggingGlobal.value = true // 暂停连接线渲染

  // 获取容器元素的相对位置来计算正确的偏移量
  const container = document.querySelector('.node-container')
  if (container) {
    const rect = container.getBoundingClientRect()
    dragState.dragOffset = {
      x: event.clientX - rect.left - node.x,
      y: event.clientY - rect.top - node.y
    }
  } else {
    // 回退方案
    dragState.dragOffset = {
      x: event.clientX - node.x,
      y: event.clientY - node.y
    }
  }

  // 添加新的全局事件监听
  document.addEventListener('mousemove', handleMouseMove)
  document.addEventListener('mouseup', stopDrag)
}

const handleMouseMove = (event) => {
  if (!dragState.isDragging || !dragState.draggedNode) return

  event.preventDefault()
  event.stopPropagation()

  // 获取容器元素的相对位置
  const container = document.querySelector('.node-container')
  if (!container) return

  const rect = container.getBoundingClientRect()
  const newX = event.clientX - rect.left - dragState.dragOffset.x
  const newY = event.clientY - rect.top - dragState.dragOffset.y

  // 检测是否发生了实际拖拽（移动距离超过3像素或时间超过100ms）
  const dragThreshold = 3
  const timeThreshold = 100
  const deltaX = Math.abs(newX - dragState.draggedNode.x)
  const deltaY = Math.abs(newY - dragState.draggedNode.y)
  const deltaTime = Date.now() - dragStartTime.value

  if (deltaX > dragThreshold || deltaY > dragThreshold || deltaTime > timeThreshold) {
    hasDragged.value = true
  }

  // 限制节点在画布范围内，考虑滚动
  const maxX = 2000 - dragState.draggedNode.width
  const maxY = 1000 - dragState.draggedNode.height

  dragState.draggedNode.x = Math.max(0, Math.min(newX, maxX))
  dragState.draggedNode.y = Math.max(0, Math.min(newY, maxY))
}

const stopDrag = () => {
  if (!dragState.draggedNode) return

  dragState.isDragging = false
  dragState.draggedNode.isDragging = false
  dragState.draggedNode = null
  isDraggingGlobal.value = false // 恢复连接线渲染

  // 清除事件监听
  document.removeEventListener('mousemove', handleMouseMove)
  document.removeEventListener('mouseup', stopDrag)
}

const getNodeStyle = (node) => {
  const layerColor = layerColors[node.layer] || layerColors[1]
  return {
    left: `${node.x}px`,
    top: `${node.y}px`,
    width: `${node.width}px`,
    height: `${node.height}px`,
    borderColor: layerColor.border
  }
}

const getCircuitPath = (connection) => {
  const fromNode = visibleNodes.value.find(n => n.id === connection.from)
  const toNode = visibleNodes.value.find(n => n.id === connection.to)

  if (!fromNode || !toNode) return ''

  // 计算节点中心点 - 直接使用节点坐标
  const fromCenterX = fromNode.x + fromNode.width / 2
  const fromCenterY = fromNode.y + fromNode.height / 2
  const toCenterX = toNode.x + toNode.width / 2
  const toCenterY = toNode.y + toNode.height / 2

  // 确定主要连接方向
  const dx = toCenterX - fromCenterX
  const dy = toCenterY - fromCenterY

  let fromX, fromY, toX, toY

  if (Math.abs(dx) > Math.abs(dy)) {
    // 水平方向为主 - 连接到左右边缘
    if (dx > 0) {
      fromX = fromNode.x + fromNode.width  // 源节点右边缘
      toX = toNode.x                      // 目标节点左边缘
    } else {
      fromX = fromNode.x                  // 源节点左边缘
      toX = toNode.x + toNode.width      // 目标节点右边缘
    }
    fromY = fromCenterY
    toY = toCenterY
  } else {
    // 垂直方向为主 - 连接到上下边缘
    if (dy > 0) {
      fromY = fromNode.y + fromNode.height // 源节点下边缘
      toY = toNode.y                       // 目标节点上边缘
    } else {
      fromY = fromNode.y                   // 源节点上边缘
      toY = toNode.y + toNode.height      // 目标节点下边缘
    }
    fromX = fromCenterX
    toX = toCenterX
  }

  // 使用简单的直线连接，但保持正确的边缘连接
  return `M ${fromX} ${fromY} L ${toX} ${toY}`
}

const getConnectionPath = (connection) => {
  return getCircuitPath(connection)
}

const getConnectionColor = (connection) => {
  const isActive = isNodeActive(connection.from) && isNodeActive(connection.to)
  return isActive ? '#00ff88' : '#4a90e2'
}

const getConnectionWidth = (connection) => {
  const isActive = isNodeActive(connection.from) && isNodeActive(connection.to)
  return isActive ? 2 : 1
}

const getConnectionMarker = (connection) => {
  const isActive = isNodeActive(connection.from) && isNodeActive(connection.to)
  return isActive ? 'url(#arrow-active)' : 'url(#arrow)'
}

const getNodeTypeIcon = (type) => {
  const iconMap = {
    cluster: '📊',
    data: '💾',
    process: '⚙️',
    analysis: '📈',
    monitor: '👁️',
    api: '🔌',
    tool: '🛠️',
    robot: '🤖',
    deployment: '🚀',
    thunderbolt: '⚡',
    sync: '🔄',
    function: 'ƒ',
    bug: '🐛',
    router: '🔀',
    experiment: '🧪',
    switcher: '🎛️',
    desktop: '🖥️',
    laptop: '💻',
    safety: '🛡️',
    security: '🔐',
    integration: '🔗',
    database: '🗄️',
    cache: '⚡'
  }
  return iconMap[type] || '📦'
}

// 清理拖拽事件监听器
onUnmounted(() => {
  document.removeEventListener('mousemove', handleMouseMove)
  document.removeEventListener('mouseup', stopDrag)
})
</script>

<style scoped>
.simple-intelligent-node-system {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: linear-gradient(135deg, #0f1419 0%, #1a1f2e 100%);
  color: #e2e8f0;
  font-family: 'Segoe UI', system-ui, sans-serif;
  overflow: hidden;
}

.control-panel {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 20px;
  background: rgba(15, 20, 25, 0.9);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.system-title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #00d4ff;
}

.workflow-controls {
  display: flex;
  align-items: center;
  gap: 12px;
}

.workflow-controls select {
  padding: 6px 12px;
  background: #2d3748;
  color: white;
  border: 1px solid #4a5568;
  border-radius: 4px;
}

.workflow-controls button {
  padding: 6px 16px;
  background: #3182ce;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background 0.2s;
}

.workflow-controls button:hover:not(:disabled) {
  background: #2c5282;
}

.workflow-controls button:disabled {
  background: #4a5568;
  cursor: not-allowed;
}

.status-info {
  display: flex;
  gap: 20px;
  font-size: 14px;
}

.node-container {
  flex: 1;
  position: relative;
  overflow: auto;
  background: radial-gradient(circle at 20% 50%, rgba(0, 212, 255, 0.05) 0%, transparent 50%);
}


.connections-svg {
  position: absolute;
  top: 0;
  left: 0;
  width: 2400px;
  height: 1000px;
  pointer-events: none;
  z-index: 2;
}

.circuit-line {
  transition: all 0.3s ease;
  stroke-linecap: round;
  stroke-linejoin: round;
}

.circuit-line:hover {
  stroke-width: 3;
  filter: drop-shadow(0 0 4px rgba(74, 144, 226, 0.6));
}

.node {
  position: absolute;
  background: linear-gradient(135deg, rgba(30, 60, 114, 0.9) 0%, rgba(42, 82, 152, 0.9) 100%);
  border: 2px solid;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  cursor: grab;
  transition: all 0.3s ease;
  padding: 8px 6px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
  z-index: 10;
  min-width: 90px;
  font-size: 9px;
  backdrop-filter: blur(4px);
}

.node:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(0, 212, 255, 0.3);
  border-color: rgba(0, 212, 255, 0.5);
  background: linear-gradient(135deg, rgba(30, 60, 114, 1) 0%, rgba(42, 82, 152, 1) 100%);
}

.node.active {
  border-color: #00ff88;
  box-shadow: 0 0 15px rgba(0, 255, 136, 0.6), inset 0 0 8px rgba(0, 255, 136, 0.2);
  background: linear-gradient(135deg, rgba(30, 60, 114, 0.9) 0%, rgba(42, 82, 152, 0.9) 100%);
}

.node.dragging {
  cursor: grabbing !important;
  opacity: 0.8;
  transform: scale(1.05);
  z-index: 1000;
}

.node-icon {
  font-size: 14px;
  margin-bottom: 4px;
}

.node-title {
  font-size: 10px;
  font-weight: 600;
  text-align: center;
  color: #e2e8f0;
  line-height: 1.2;
  margin-bottom: 2px;
}

.node-id {
  font-size: 8px;
  color: #a0aec0;
  background: rgba(0, 0, 0, 0.3);
  padding: 1px 3px;
  border-radius: 2px;
}

.node.active .node-id {
  color: #00ff88;
  background: rgba(0, 255, 136, 0.1);
}

.info-panel {
  position: absolute;
  top: 80px;
  right: 20px;
  width: 250px;
  background: rgba(15, 20, 25, 0.9);
  backdrop-filter: blur(10px);
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  padding: 16px;
  z-index: 100;
}

.info-panel h3 {
  margin: 0 0 12px 0;
  color: #00d4ff;
  font-size: 14px;
}

.info-panel p {
  margin: 6px 0;
  font-size: 12px;
}

.info-panel button {
  margin-top: 12px;
  padding: 6px 12px;
  background: #3182ce;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}
</style>
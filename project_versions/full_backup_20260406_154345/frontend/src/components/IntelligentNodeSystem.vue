<template>
  <div class="intelligent-node-system">
    <!-- 头部控制面板 -->
    <div class="control-panel">
      <div class="panel-left">
        <h1 class="system-title">
          <n-icon size="20">
            <AntDesignOutlined />
          </n-icon>
          智能量化平台节点可视化系统
        </h1>
        <div class="workflow-selector">
          <n-space align="center">
            <span>选择工作流程：</span>
            <n-select
              v-model:value="selectedWorkflow"
              :options="workflowOptions"
              style="width: 200px"
              @update:value="handleWorkflowChange"
            />
            <n-button
              type="primary"
              :loading="isActivating"
              @click="activateWorkflow"
            >
              <template #icon>
                <n-icon><PlayCircleOutlined /></n-icon>
              </template>
              激活流程
            </n-button>
            <n-button
              @click="resetNodes"
              :disabled="systemStatus === 'idle'"
            >
              <template #icon>
                <n-icon><SyncOutlined /></n-icon>
              </template>
              重置
            </n-button>
            <n-button
              @click="activateAllNodes"
              :disabled="systemStatus === 'running'"
            >
              全部激活
            </n-button>
          </n-space>
        </div>
      </div>

      <div class="panel-right">
        <n-space align="center">
          <n-button-group>
            <n-button @click="zoomIn" quaternary>
              <template #icon>
                <n-icon><ZoomInOutlined /></n-icon>
              </template>
            </n-button>
            <n-button @click="zoomOut" quaternary>
              <template #icon>
                <n-icon><ZoomOutOutlined /></n-icon>
              </template>
            </n-button>
            <n-button @click="fitView" quaternary>
              <template #icon>
                <n-icon><ExpandOutlined /></n-icon>
              </template>
            </n-button>
          </n-button-group>

          <n-tag :type="systemStatusType" size="small">
            <n-icon size="12">
              <component :is="systemStatusIcon" />
            </n-icon>
            {{ systemStatusText }}
          </n-tag>
        </n-space>
      </div>
    </div>

    <!-- 节点系统主体 -->
    <div class="mermaid-container" ref="mermaidContainer">
      <!-- 使用div容器 + CSS绝对定位 -->
      <div class="node-canvas" :style="{ transform: `scale(${zoomLevel})` }">
        <!-- 层级分组框 - Mermaid风格 -->
        <div v-for="layer in layerGroups" :key="layer.id"
             class="layer-group"
             :style="getLayerGroupStyle(layer)">
          <div class="layer-group-header">
            <span class="layer-group-title">{{ layer.name }}</span>
            <span class="layer-group-subtitle">{{ layer.subtitle }}</span>
          </div>
        </div>

        <!-- 连接线 - 电路板直角样式 -->
        <div class="connections">
          <svg class="connection-svg" viewBox="0 0 1400 1200">
            <!-- 定义箭头 -->
            <defs>
              <marker id="arrowhead-active" markerWidth="6" markerHeight="5"
                      refX="5" refY="2.5" orient="auto">
                <polygon points="0 0, 6 2.5, 0 5" fill="#00ff88" />
              </marker>
              <marker id="arrowhead-inactive" markerWidth="6" markerHeight="5"
                      refX="5" refY="2.5" orient="auto">
                <polygon points="0 0, 6 2.5, 0 5" fill="#4a5568" />
              </marker>
            </defs>

            <path v-for="connection in mermaidConnections" :key="connection.id"
                  :d="getOrthogonalPath(connection)"
                  :stroke="activeConnections.includes(connection) ? '#00ff88' : '#4a5568'"
                  :stroke-width="activeConnections.includes(connection) ? 2 : 1"
                  :stroke-opacity="activeConnections.includes(connection) ? 0.9 : 0.2"
                  :stroke-dasharray="connection.isDashed ? '5,5' : 'none'"
                  fill="none"
                  :marker-end="activeConnections.includes(connection) ? 'url(#arrowhead-active)' : 'url(#arrowhead-inactive)'"
                  class="connection-path"
                  :class="{ active: activeConnections.includes(connection), dashed: connection.isDashed }" />
          </svg>
        </div>

        <!-- 节点 -->
        <div v-for="node in mermaidNodes" :key="node.id"
             class="node"
             :class="{ active: nodeStates[node.id]?.active }"
             :style="getNodeStyle(node)"
             @click="handleNodeClick(node)"
             @contextmenu.prevent="handleNodeRightClick(node, $event)">

          <!-- 节点图标 -->
          <div class="node-icon" :class="`node-type-${node.type}`">
            <n-icon size="14">
              <component :is="getNodeIcon(node.type)" />
            </n-icon>
          </div>

          <!-- 节点标题 -->
          <div class="node-title">{{ node.name }}</div>

          <!-- 节点ID -->
          <div class="node-id">{{ node.id }}</div>
        </div>
      </div>
    </div>

    <!-- 右侧信息面板 -->
    <div class="info-panel">
      <n-card title="系统信息" size="small" :bordered="false">
        <div class="info-section">
          <h4>系统状态</h4>
          <div class="info-item">
            <span>总节点数：</span>
            <n-tag size="small">{{ totalNodes }}</n-tag>
          </div>
          <div class="info-item">
            <span>激活节点：</span>
            <n-tag type="success" size="small">{{ activeNodes }}</n-tag>
          </div>
          <div class="info-item">
            <span>当前流程：</span>
            <n-tag type="info" size="small">{{ selectedWorkflow }}</n-tag>
          </div>
        </div>

        <div class="info-section">
          <h4>选中节点</h4>
          <div v-if="selectedNode" class="node-info">
            <p><strong>{{ selectedNode.name }}</strong> ({{ selectedNode.id }})</p>
            <p>{{ selectedNode.description }}</p>
            <p>类型：{{ selectedNode.type }}</p>
          </div>
          <div v-else class="no-selection">
            点击节点查看详情
          </div>
        </div>
      </n-card>
    </div>

    <!-- 右键菜单 -->
    <n-dropdown
      placement="bottom-start"
      trigger="manual"
      :x="contextMenuX"
      :y="contextMenuY"
      :options="contextMenuOptions"
      :show="showContextMenu"
      :on-clickoutside="closeContextMenu"
      @select="handleContextMenuSelect"
    />

    <!-- 节点配置抽屉 -->
    <n-drawer v-model:show="showConfigDrawer" :width="400">
      <n-drawer-content title="节点配置" closable>
        <div v-if="configNode" class="node-config">
          <n-form :model="configNode" label-placement="left">
            <n-form-item label="节点ID">
              <n-input v-model:value="configNode.id" disabled />
            </n-form-item>
            <n-form-item label="节点名称">
              <n-input v-model:value="configNode.name" />
            </n-form-item>
            <n-form-item label="描述">
              <n-input type="textarea" v-model:value="configNode.description" />
            </n-form-item>
            <n-form-item label="CPU限制">
              <n-input-number v-model:value="configNode.cpuLimit" :min="0" :max="100" />
            </n-form-item>
            <n-form-item label="内存限制">
              <n-input-number v-model:value="configNode.memoryLimit" :min="0" :max="100" />
            </n-form-item>
          </n-form>

          <n-space justify="end" style="margin-top: 20px;">
            <n-button @click="showConfigDrawer = false">取消</n-button>
            <n-button type="primary" @click="saveNodeConfig">保存</n-button>
          </n-space>
        </div>
      </n-drawer-content>
    </n-drawer>

    <!-- 状态栏 -->
    <div class="status-bar">
      <div class="status-left">
        <span>最后更新：{{ lastUpdateTime }}</span>
        <span>|</span>
        <span>工作流程：{{ selectedWorkflow }}</span>
      </div>
      <div class="status-right">
        <span>系统版本：v1.0.0</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, nextTick, h } from 'vue'
import {
  ApiOutlined, ClusterOutlined, CloudServerOutlined, DatabaseOutlined, DeleteOutlined, EditOutlined,
  ExpandOutlined, InfoCircleOutlined, PlayCircleOutlined, SettingOutlined, SyncOutlined,
  ZoomInOutlined, ZoomOutOutlined, CheckCircleOutlined, AntDesignOutlined,
  NodeIndexOutlined, DeploymentUnitOutlined, ExperimentOutlined, ApiToolOutlined,
  DesktopOutlined, LaptopOutlined, BugOutlined, ToolOutlined, PartitionOutlined,
  HddOutlined, CloudOutlined, GatewayOutlined, RouterOutlined, SwitcherOutlined,
  DashboardOutlined, BarChartOutlined, LineChartOutlined, PieChartOutlined,
  RobotOutlined, ThunderboltOutlined, FireOutlined, RocketOutlined,
  SecurityScanOutlined, SafetyCertificateOutlined, ShieldOutlined,
  CodeOutlined, FunctionOutlined, IntegrationOutlined, LinkOutlined
} from '@vicons/antd'

// 层级分组框定义 - Mermaid风格
const layerGroups = ref([
  {
    id: 1,
    name: '第1层：数据中枢层',
    subtitle: 'Data Hub Layer - 10个节点',
    x: 20,
    y: 30,
    width: 1350,
    height: 140,
    color: '#fff3e0',
    borderColor: '#e65100'
  },
  {
    id: 2,
    name: '第2层：业务逻辑层',
    subtitle: 'Business Logic Layer - 12个节点',
    x: 20,
    y: 190,
    width: 1350,
    height: 140,
    color: '#e1f5fe',
    borderColor: '#01579b'
  },
  {
    id: 3,
    name: '第3层：投资分析系统',
    subtitle: 'Investment Analytics - 9个节点',
    x: 20,
    y: 350,
    width: 1350,
    height: 140,
    color: '#d4edda',
    borderColor: '#27ae60'
  },
  {
    id: 4,
    name: '第4层：AI智能策略层',
    subtitle: 'AI Strategy Layer - 18个节点',
    x: 20,
    y: 510,
    width: 1350,
    height: 140,
    color: '#e8f5e8',
    borderColor: '#1b5e20'
  },
  {
    id: 5,
    name: '第5层：实盘交易层',
    subtitle: 'Live Trading Layer - 20个节点',
    x: 20,
    y: 670,
    width: 1350,
    height: 140,
    color: '#ffebee',
    borderColor: '#d32f2f'
  },
  {
    id: 6,
    name: '第6层：实验管理层',
    subtitle: 'Experiment Management Layer - 9个节点',
    x: 20,
    y: 830,
    width: 1350,
    height: 140,
    color: '#e0f2f1',
    borderColor: '#00695c'
  },
  {
    id: 7,
    name: '第7层：应用服务层',
    subtitle: 'Application Services Layer - 10个节点',
    x: 20,
    y: 990,
    width: 1350,
    height: 140,
    color: '#fce4ec',
    borderColor: '#27ae60'
  }
])

// 完整的79个节点定义 - 基于架构文档
const mermaidNodes = ref([
  // 第1层：数据中枢层 (10个节点)
  { id: 'UP', name: '统一数据提供器', x: 50, y: 60, width: 120, height: 50, type: 'cluster', layer: 1, description: '多源数据整合' },
  { id: 'CM', name: '缓存管理器', x: 200, y: 60, width: 100, height: 50, type: 'data', layer: 1, description: '智能缓存策略' },
  { id: 'DP', name: '数据管道', x: 330, y: 60, width: 100, height: 50, type: 'process', layer: 1, description: '预处理/标准化' },
  { id: 'SM', name: '存储管理器', x: 460, y: 60, width: 100, height: 50, type: 'data', layer: 1, description: '热冷数据分离' },
  { id: 'MON', name: '监控系统', x: 590, y: 60, width: 100, height: 50, type: 'monitor', layer: 1, description: '数据质量监控' },
  { id: 'EXP', name: '导出器系统', x: 720, y: 60, width: 100, height: 50, type: 'api', layer: 1, description: 'QLib桥接器' },
  { id: 'QD', name: 'QLib数据提供器', x: 850, y: 60, width: 120, height: 50, type: 'data', layer: 1, description: '数据标准化' },
  { id: 'QA', name: 'QLib分析器', x: 1000, y: 60, width: 100, height: 50, type: 'analysis', layer: 1, description: '专业性能分析' },
  { id: 'QF', name: 'QLib因子引擎', x: 1130, y: 60, width: 100, height: 50, type: 'process', layer: 1, description: '表达式计算' },
  { id: 'QE', name: 'QLib环境管理', x: 1260, y: 60, width: 100, height: 50, type: 'tool', layer: 1, description: '缓存优化' },

  // 第2层：业务逻辑层 (12个节点)
  { id: 'FE', name: '因子计算引擎', x: 50, y: 220, width: 120, height: 50, type: 'process', layer: 2, description: 'Alpha158/Alpha360' },
  { id: 'SS', name: '策略系统', x: 200, y: 220, width: 100, height: 50, type: 'cluster', layer: 2, description: '策略管理/执行' },
  { id: 'SR', name: '策略回放系统', x: 330, y: 220, width: 100, height: 50, type: 'analysis', layer: 2, description: '性能分析' },
  { id: 'MM', name: '模型管理服务', x: 460, y: 220, width: 100, height: 50, type: 'data', layer: 2, description: '模型训练/评估' },
  { id: 'IA', name: '投资分析系统', x: 590, y: 220, width: 120, height: 50, type: 'cluster', layer: 2, description: '组合分析/归因分析' },
  { id: 'QB', name: 'QLib回测引擎', x: 740, y: 220, width: 100, height: 50, type: 'analysis', layer: 2, description: '真实QLib框架' },
  { id: 'QP', name: 'QLib数据处理', x: 870, y: 220, width: 100, height: 50, type: 'process', layer: 2, description: '质量控制/指标计算' },
  { id: 'QI', name: 'QLib集成', x: 1000, y: 220, width: 100, height: 50, type: 'integration', layer: 2, description: '工作流管理' },
  { id: 'ASL', name: 'AI策略实验室', x: 1130, y: 220, width: 100, height: 50, type: 'cluster', layer: 2, description: 'DeepSeek API集成' },
  { id: 'AE', name: 'AI策略引擎', x: 1260, y: 220, width: 100, height: 50, type: 'robot', layer: 2, description: '深度学习模型' },
  { id: 'ML', name: '多模型框架', x: 1390, y: 220, width: 100, height: 50, type: 'deployment', layer: 2, description: 'LightGBM/XGBoost/Transformer' },
  { id: 'DL', name: '深度学习模型', x: 50, y: 290, width: 100, height: 50, type: 'thunderbolt', layer: 2, description: 'MLP/LSTM/CNN/GNN' },

  // 第3层：投资分析系统 (9个节点)
  { id: 'OT', name: '在线滚动训练', x: 170, y: 380, width: 100, height: 50, type: 'sync', layer: 3, description: '增量学习/模型更新' },
  { id: 'SG', name: '策略生成器', x: 290, y: 380, width: 100, height: 50, type: 'function', layer: 3, description: '模型到策略转换' },
  { id: 'MI', name: '模型可解释性', x: 410, y: 380, width: 100, height: 50, type: 'bug', layer: 3, description: 'SHAP/特征重要性' },
  { id: 'ND', name: '嵌套决策引擎', x: 530, y: 380, width: 100, height: 50, type: 'router', layer: 3, description: '多时间尺度决策' },
  { id: 'META', name: '元学习系统', x: 650, y: 380, width: 100, height: 50, type: 'experiment', layer: 3, description: 'DDG-DA/迁移学习' },
  { id: 'RP', name: 'AI实时处理', x: 770, y: 380, width: 100, height: 50, type: 'thunderbolt', layer: 3, description: '特征提取/模式检测' },
  { id: 'MC', name: '元控制器', x: 890, y: 380, width: 100, height: 50, type: 'switcher', layer: 3, description: '系统协调/流程管理' },
  { id: 'EC', name: '实验管理核心', x: 1010, y: 380, width: 100, height: 50, type: 'cluster', layer: 3, description: 'Qlib Recorder扩展' },
  { id: 'ES', name: '实验服务', x: 1130, y: 380, width: 100, height: 50, type: 'api', layer: 3, description: '实验/记录/分析' },

  // 第4层：AI智能策略层 (18个节点)
  { id: 'ET', name: '实验模板', x: 50, y: 540, width: 100, height: 50, type: 'data', layer: 4, description: '信号/IC/回测模板' },
  { id: 'EW', name: '实验Web界面', x: 170, y: 540, width: 100, height: 50, type: 'desktop', layer: 4, description: 'RESTful API' },
  { id: 'EX', name: '自动化实验系统', x: 290, y: 540, width: 100, height: 50, type: 'robot', layer: 4, description: 'SQLite任务管理' },
  { id: 'TM', name: 'SQLite任务管理器', x: 410, y: 540, width: 100, height: 50, type: 'tool', layer: 4, description: '任务状态跟踪' },
  { id: 'FSM', name: '文件系统存储管理器', x: 530, y: 540, width: 120, height: 50, type: 'hdd', layer: 4, description: '实验数据存储' },
  { id: 'CM2', name: '配置管理器', x: 670, y: 540, width: 100, height: 50, type: 'setting', layer: 4, description: '实验配置管理' },
  { id: 'RG', name: '滚动窗口生成器', x: 790, y: 540, width: 120, height: 50, type: 'sync', layer: 4, description: '时间序列实验' },
  { id: 'PG', name: '参数网格生成器', x: 930, y: 540, width: 120, height: 50, type: 'partition', layer: 4, description: '超参数优化' },
  { id: 'MG', name: '多模型生成器', x: 1070, y: 540, width: 100, height: 50, type: 'deployment', layer: 4, description: '模型对比实验' },
  { id: 'LE', name: '本地执行器', x: 1190, y: 540, width: 100, height: 50, type: 'code', layer: 4, description: '并行任务执行' },
  { id: 'RC', name: '结果收集器', x: 1310, y: 540, width: 100, height: 50, type: 'linechart', layer: 4, description: '智能分析报告' },
  { id: 'OM', name: '在线管理器', x: 50, y: 610, width: 100, height: 50, type: 'cloud', layer: 4, description: 'OnlineManager' },
  { id: 'OSR', name: '在线策略', x: 170, y: 610, width: 100, height: 50, type: 'api', layer: 4, description: 'OnlineStrategy' },
  { id: 'OA', name: '适配器层', x: 290, y: 610, width: 100, height: 50, type: 'link', layer: 4, description: 'Adapters' },
  { id: 'OC', name: '配置管理', x: 410, y: 610, width: 100, height: 50, type: 'setting', layer: 4, description: 'ConfigManager' },
  { id: 'LTDP', name: '数据处理器', x: 530, y: 610, width: 100, height: 50, type: 'process', layer: 4, description: '市场数据/Tick数据/订单流' },
  { id: 'RM', name: '实时监控', x: 650, y: 610, width: 100, height: 50, type: 'monitor', layer: 4, description: '延迟/吞吐量/系统健康' },
  { id: 'SP', name: '流式处理', x: 770, y: 610, width: 100, height: 50, type: 'sync', layer: 4, description: '实时流/事件流/数据流管理' },

  // 第5层：实盘交易层 (20个节点)
  { id: 'TE', name: '交易执行', x: 50, y: 700, width: 100, height: 50, type: 'safety', layer: 5, description: '券商接口/订单管理/执行引擎' },
  { id: 'RS', name: '风险管理', x: 170, y: 700, width: 100, height: 50, type: 'security', layer: 5, description: '实时风险/仓位管理/风控策略' },
  { id: 'ST', name: '策略模块', x: 290, y: 700, width: 100, height: 50, type: 'cluster', layer: 5, description: '策略引擎/信号生成/复合信号' },
  { id: 'UT', name: '工具模块', x: 410, y: 700, width: 100, height: 50, type: 'tool', layer: 5, description: '缓存机制/技术指标/数据压缩' },
  { id: 'GUI', name: '图形界面', x: 530, y: 700, width: 100, height: 50, type: 'desktop', layer: 5, description: '实时监控/交互' },
  { id: 'WEB', name: 'Web界面', x: 650, y: 700, width: 100, height: 50, type: 'laptop', layer: 5, description: '远程访问/协作' },
  { id: 'AS2', name: '应用服务层', x: 770, y: 700, width: 100, height: 50, type: 'cluster', layer: 5, description: '工作流/配置/警报' },
  { id: 'TM2', name: '任务管理器', x: 890, y: 700, width: 100, height: 50, type: 'tool', layer: 5, description: '任务调度和分配' },
  { id: 'CM3', name: '配置管理器', x: 1010, y: 700, width: 100, height: 50, type: 'setting', layer: 5, description: '系统配置和参数' },
  { id: 'ALERT', name: '警报系统', x: 1130, y: 700, width: 100, height: 50, type: 'fire', layer: 5, description: '智能警报和通知' },
  { id: 'SCHED', name: '任务调度器', x: 1250, y: 700, width: 100, height: 50, type: 'sync', layer: 5, description: '定时任务和调度' },
  { id: 'WORKFLOW', name: '工作流引擎', x: 1370, y: 700, width: 100, height: 50, type: 'gateway', layer: 5, description: '工作流自动化' },
  { id: 'BACKUP', name: '备份系统', x: 50, y: 770, width: 100, height: 50, type: 'hdd', layer: 5, description: '数据备份和恢复' },
  { id: 'MON2', name: '系统监控', x: 170, y: 770, width: 100, height: 50, type: 'dashboard', layer: 5, description: '系统性能监控' },
  { id: 'LOG', name: '日志系统', x: 290, y: 770, width: 100, height: 50, type: 'bug', layer: 5, description: '日志收集和分析' },
  { id: 'AUTH', name: '认证系统', x: 410, y: 770, width: 100, height: 50, type: 'shield', layer: 5, description: '用户认证和授权' },
  { id: 'PERF', name: '性能分析', x: 530, y: 770, width: 100, height: 50, type: 'barchart', layer: 5, description: '性能指标分析' },
  { id: 'DB', name: '数据库', x: 650, y: 770, width: 100, height: 50, type: 'database', layer: 5, description: '数据存储和查询' },
  { id: 'CACHE2', name: '缓存系统', x: 770, y: 770, width: 100, height: 50, type: 'cloud', layer: 5, description: '高速缓存管理' },
  { id: 'MSG', name: '消息队列', x: 890, y: 770, width: 100, height: 50, type: 'router', layer: 5, description: '异步消息处理' },

  // 第6层：实验管理层 (9个节点)
  { id: 'COLLAB', name: '协作功能', x: 1010, y: 860, width: 100, height: 50, type: 'cluster', layer: 6, description: '团队协作和共享' },
  { id: 'APIGW', name: 'API网关', x: 1130, y: 860, width: 100, height: 50, type: 'gateway', layer: 6, description: 'API请求路由' },
  { id: 'LOADBAL', name: '负载均衡', x: 1250, y: 860, width: 100, height: 50, type: 'partition', layer: 6, description: '请求负载分配' },
  { id: 'SECURITY', name: '安全系统', x: 1370, y: 860, width: 100, height: 50, type: 'security', layer: 6, description: '系统安全防护' },
  { id: 'CLUSTER', name: '集群管理', x: 50, y: 930, width: 100, height: 50, type: 'deployment', layer: 6, description: '节点集群管理' },
  { id: 'CONTAINER', name: '容器化', x: 170, y: 930, width: 100, height: 50, type: 'api', layer: 6, description: 'Docker容器管理' },
  { id: 'ORCHESTR', name: '编排系统', x: 290, y: 930, width: 100, height: 50, type: 'router', layer: 6, description: 'Kubernetes编排' },
  { id: 'CI_CD', name: 'CI/CD系统', x: 410, y: 930, width: 100, height: 50, type: 'code', layer: 6, description: '持续集成部署' },
  { id: 'DEVOPS', name: 'DevOps工具', x: 530, y: 930, width: 100, height: 50, type: 'tool', layer: 6, description: '运维自动化工具' },

  // 第7层：应用服务层 (10个节点)
  { id: 'UI', name: '用户界面', x: 650, y: 1020, width: 100, height: 50, type: 'desktop', layer: 7, description: '前端用户界面' },
  { id: 'MOBILE', name: '移动端', x: 770, y: 1020, width: 100, height: 50, type: 'laptop', layer: 7, description: '移动应用支持' },
  { id: 'NOTIF', name: '通知系统', x: 890, y: 1020, width: 100, height: 50, type: 'fire', layer: 7, description: '消息通知服务' },
  { id: 'REPORT', name: '报表系统', x: 1010, y: 1020, width: 100, height: 50, type: 'piechart', layer: 7, description: '报表生成和分析' },
  { id: 'EXPORT', name: '导出系统', x: 1130, y: 1020, width: 100, height: 50, type: 'api', layer: 7, description: '数据导出功能' },
  { id: 'MLFLOW', name: 'MLflow', x: 1250, y: 1020, width: 100, height: 50, type: 'experiment', layer: 7, description: '机器学习生命周期管理' },
  { id: 'TENSORBOARD', name: 'TensorBoard', x: 1370, y: 1020, width: 100, height: 50, type: 'barchart', layer: 7, description: '模型训练可视化' },
  { id: 'JUPYTER', name: 'JupyterHub', x: 50, y: 1090, width: 100, height: 50, type: 'code', layer: 7, description: '交互式开发环境' },
  { id: 'GRAFANA', name: 'Grafana', x: 170, y: 1090, width: 100, height: 50, type: 'dashboard', layer: 7, description: '监控数据可视化' },
  { id: 'KIBANA', name: 'Kibana', x: 290, y: 1090, width: 100, height: 50, type: 'linechart', layer: 7, description: '日志分析平台' }
])

// 基于架构文档的业务逻辑连接关系 - 固定不变的连接
const mermaidConnections = ref([
  // 数据中枢层内部连接 (基于架构文档图)
  { id: 'UP_QD', fromNode: 'UP', toNode: 'QD', description: '统一数据提供器 -> QLib数据提供器' },
  { id: 'CM_QD', fromNode: 'CM', toNode: 'QD', description: '缓存管理器 -> QLib数据提供器' },
  { id: 'DP_QF', fromNode: 'DP', toNode: 'QF', description: '数据管道 -> QLib因子引擎' },
  { id: 'SM_QE', fromNode: 'SM', toNode: 'QE', description: '存储管理器 -> QLib环境管理' },
  { id: 'MON_QP', fromNode: 'MON', toNode: 'QP', description: '监控系统 -> QLib数据处理' },
  { id: 'EXP_QI', fromNode: 'EXP', toNode: 'QI', description: '导出器系统 -> QLib集成' },

  // QLib核心内部连接
  { id: 'QD_FE', fromNode: 'QD', toNode: 'FE', description: 'QLib数据提供器 -> 因子计算引擎' },
  { id: 'QF_AE', fromNode: 'QF', toNode: 'AE', description: 'QLib因子引擎 -> AI策略引擎' },
  { id: 'QF_DL', fromNode: 'QF', toNode: 'DL', description: 'QLib因子引擎 -> 深度学习模型' },
  { id: 'QA_SR', fromNode: 'QA', toNode: 'SR', description: 'QLib分析器 -> 策略回放系统' },
  { id: 'QA_QB', fromNode: 'QA', toNode: 'QB', description: 'QLib分析器 -> QLib回测引擎' },
  { id: 'QE_MM', fromNode: 'QE', toNode: 'MM', description: 'QLib环境管理 -> 模型管理服务' },
  { id: 'QE_DL', fromNode: 'QE', toNode: 'DL', description: 'QLib环境管理 -> 深度学习模型' },
  { id: 'QB_ASL', fromNode: 'QB', toNode: 'ASL', description: 'QLib回测引擎 -> AI策略实验室' },
  { id: 'QP_IA', fromNode: 'QP', toNode: 'IA', description: 'QLib数据处理 -> 投资分析系统' },

  // 业务逻辑层内部连接
  { id: 'FE_SS', fromNode: 'FE', toNode: 'SS', description: '因子计算引擎 -> 策略系统' },
  { id: 'SS_ASL', fromNode: 'SS', toNode: 'ASL', description: '策略系统 -> AI策略实验室' },
  { id: 'SR_QA', fromNode: 'SR', toNode: 'QA', description: '策略回放系统 -> QLib分析器' },
  { id: 'MM_AE', fromNode: 'MM', toNode: 'AE', description: '模型管理服务 -> AI策略引擎' },
  { id: 'MM_ML', fromNode: 'MM', toNode: 'ML', description: '模型管理服务 -> 多模型框架' },
  { id: 'MM_OT', fromNode: 'MM', toNode: 'OT', description: '模型管理服务 -> 在线滚动训练' },
  { id: 'MM_SG', fromNode: 'MM', toNode: 'SG', description: '模型管理服务 -> 策略生成器' },
  { id: 'MM_MI', fromNode: 'MM', toNode: 'MI', description: '模型管理服务 -> 模型可解释性' },
  { id: 'MM_DL', fromNode: 'MM', toNode: 'DL', description: '模型管理服务 -> 深度学习模型' },
  { id: 'IA_EC', fromNode: 'IA', toNode: 'EC', description: '投资分析系统 -> 实验管理核心' },
  { id: 'IA_GUI', fromNode: 'IA', toNode: 'GUI', description: '投资分析系统 -> 图形界面' },
  { id: 'IA_WEB', fromNode: 'IA', toNode: 'WEB', description: '投资分析系统 -> Web界面' },
  { id: 'IA_ES', fromNode: 'IA', toNode: 'ES', description: '投资分析系统 -> 实验服务' },
  { id: 'IA_TM', fromNode: 'IA', toNode: 'TM', description: '投资分析系统 -> SQLite任务管理器' },

  // AI智能策略层内部连接
  { id: 'ASL_AE', fromNode: 'ASL', toNode: 'AE', description: 'AI策略实验室 -> AI策略引擎' },
  { id: 'ASL_ES', fromNode: 'ASL', toNode: 'ES', description: 'AI策略实验室 -> 实验服务' },
  { id: 'ASL_OM', fromNode: 'ASL', toNode: 'OM', description: 'AI策略实验室 -> 在线管理器' },
  { id: 'ASL_SG', fromNode: 'ASL', toNode: 'SG', description: 'AI策略实验室 -> 策略生成器' },
  { id: 'ASL_GUI', fromNode: 'ASL', toNode: 'GUI', description: 'AI策略实验室 -> 图形界面' },
  { id: 'ASL_WEB', fromNode: 'ASL', toNode: 'WEB', description: 'AI策略实验室 -> Web界面' },
  { id: 'ASL_ST', fromNode: 'ASL', toNode: 'ST', description: 'AI策略实验室 -> 策略模块' },
  { id: 'ASL_TE', fromNode: 'ASL', toNode: 'TE', description: 'AI策略实验室 -> 交易执行' },
  { id: 'ASL_RS', fromNode: 'ASL', toNode: 'RS', description: 'AI策略实验室 -> 风险管理' },

  // AI策略引擎输出连接
  { id: 'AE_ES', fromNode: 'AE', toNode: 'ES', description: 'AI策略引擎 -> 实验服务' },
  { id: 'AE_OM', fromNode: 'AE', toNode: 'OM', description: 'AI策略引擎 -> 在线管理器' },
  { id: 'AE_MM', fromNode: 'AE', toNode: 'MM', description: 'AI策略引擎 -> 模型管理服务' },
  { id: 'AE_GUI', fromNode: 'AE', toNode: 'GUI', description: 'AI策略引擎 -> 图形界面' },
  { id: 'AE_WEB', fromNode: 'AE', toNode: 'WEB', description: 'AI策略引擎 -> Web界面' },
  { id: 'AE_ST', fromNode: 'AE', toNode: 'ST', description: 'AI策略引擎 -> 策略模块' },
  { id: 'AE_TE', fromNode: 'AE', toNode: 'TE', description: 'AI策略引擎 -> 交易执行' },
  { id: 'AE_RS', fromNode: 'AE', toNode: 'RS', description: 'AI策略引擎 -> 风险管理' },
  { id: 'AE_SG', fromNode: 'AE', toNode: 'SG', description: 'AI策略引擎 -> 策略生成器' },
  { id: 'AE_OSR', fromNode: 'AE', toNode: 'OSR', description: 'AI策略引擎 -> 在线策略' },

  // 多模型框架连接
  { id: 'ML_MM', fromNode: 'ML', toNode: 'MM', description: '多模型框架 -> 模型管理服务' },
  { id: 'ML_ES', fromNode: 'ML', toNode: 'ES', description: '多模型框架 -> 实验服务' },
  { id: 'ML_OM', fromNode: 'ML', toNode: 'OM', description: '多模型框架 -> 在线管理器' },
  { id: 'ML_GUI', fromNode: 'ML', toNode: 'GUI', description: '多模型框架 -> 图形界面' },
  { id: 'ML_WEB', fromNode: 'ML', toNode: 'WEB', description: '多模型框架 -> Web界面' },

  // 深度学习模型输出连接
  { id: 'DL_AE', fromNode: 'DL', toNode: 'AE', description: '深度学习模型 -> AI策略引擎' },
  { id: 'DL_ES', fromNode: 'DL', toNode: 'ES', description: '深度学习模型 -> 实验服务' },
  { id: 'DL_OM', fromNode: 'DL', toNode: 'OM', description: '深度学习模型 -> 在线管理器' },
  { id: 'DL_MM', fromNode: 'DL', toNode: 'MM', description: '深度学习模型 -> 模型管理服务' },
  { id: 'DL_GUI', fromNode: 'DL', toNode: 'GUI', description: '深度学习模型 -> 图形界面' },
  { id: 'DL_WEB', fromNode: 'DL', toNode: 'WEB', description: '深度学习模型 -> Web界面' },
  { id: 'DL_ST', fromNode: 'DL', toNode: 'ST', description: '深度学习模型 -> 策略模块' },
  { id: 'DL_TE', fromNode: 'DL', toNode: 'TE', description: '深度学习模型 -> 交易执行' },
  { id: 'DL_RS', fromNode: 'DL', toNode: 'RS', description: '深度学习模型 -> 风险管理' },
  { id: 'DL_SG', fromNode: 'DL', toNode: 'SG', description: '深度学习模型 -> 策略生成器' },
  { id: 'DL_OSR', fromNode: 'DL', toNode: 'OSR', description: '深度学习模型 -> 在线策略' },

  // 其他AI模型连接
  { id: 'OT_MM', fromNode: 'OT', toNode: 'MM', description: '在线滚动训练 -> 模型管理服务' },
  { id: 'OT_ES', fromNode: 'OT', toNode: 'ES', description: '在线滚动训练 -> 实验服务' },
  { id: 'OT_OM', fromNode: 'OT', toNode: 'OM', description: '在线滚动训练 -> 在线管理器' },
  { id: 'SG_ES', fromNode: 'SG', toNode: 'ES', description: '策略生成器 -> 实验服务' },
  { id: 'SG_OSR', fromNode: 'SG', toNode: 'OSR', description: '策略生成器 -> 在线策略' },
  { id: 'MI_ES', fromNode: 'MI', toNode: 'ES', description: '模型可解释性 -> 实验服务' },
  { id: 'MI_OM', fromNode: 'MI', toNode: 'OM', description: '模型可解释性 -> 在线管理器' },
  { id: 'ND_ES', fromNode: 'ND', toNode: 'ES', description: '嵌套决策引擎 -> 实验服务' },
  { id: 'META_ES', fromNode: 'META', toNode: 'ES', description: '元学习系统 -> 实验服务' },
  { id: 'RP_ES', fromNode: 'RP', toNode: 'ES', description: 'AI实时处理 -> 实验服务' },
  { id: 'MC_ES', fromNode: 'MC', toNode: 'ES', description: '元控制器 -> 实验服务' },

  // 实盘交易层内部连接
  { id: 'LTDP_RM', fromNode: 'LTDP', toNode: 'RM', description: '数据处理器 -> 实时监控' },
  { id: 'RM_SP', fromNode: 'RM', toNode: 'SP', description: '实时监控 -> 流式处理' },
  { id: 'SP_TE', fromNode: 'SP', toNode: 'TE', description: '流式处理 -> 交易执行' },
  { id: 'TE_RS', fromNode: 'TE', toNode: 'RS', description: '交易执行 -> 风险管理' },
  { id: 'RS_ST', fromNode: 'RS', toNode: 'ST', description: '风险管理 -> 策略模块' },
  { id: 'ST_UT', fromNode: 'ST', toNode: 'UT', description: '策略模块 -> 工具模块' },
  { id: 'UT_LTDP', fromNode: 'UT', toNode: 'LTDP', description: '工具模块 -> 数据处理器' },

  // 跨层连接到界面
  { id: 'ST_GUI', fromNode: 'ST', toNode: 'GUI', description: '策略模块 -> 图形界面' },
  { id: 'SP_WEB', fromNode: 'SP', toNode: 'WEB', description: '流式处理 -> Web界面' },
  { id: 'LTDP_GUI', fromNode: 'LTDP', toNode: 'GUI', description: '数据处理器 -> 图形界面' },
  { id: 'SP_GUI', fromNode: 'SP', toNode: 'GUI', description: '流式处理 -> 图形界面' },

  // 数据中枢到实盘交易层
  { id: 'DH_LTDP', fromNode: 'UP', toNode: 'LTDP', description: '数据中枢层 -> 数据处理器' },
  { id: 'QL_LTDP', fromNode: 'QD', toNode: 'LTDP', description: 'QLib核心 -> 数据处理器' },
  { id: 'BL_ST', fromNode: 'SS', toNode: 'ST', description: '业务逻辑层 -> 策略模块' },
  { id: 'AI_ST', fromNode: 'AE', toNode: 'ST', description: 'AI智能策略层 -> 策略模块' },
  { id: 'EM_RS', fromNode: 'EC', toNode: 'RS', description: '实验管理层 -> 风险管理' },

  // 界面输出连接
  { id: 'TE_GUI', fromNode: 'TE', toNode: 'GUI', description: '交易执行 -> 图形界面' },
  { id: 'TE_WEB', fromNode: 'TE', toNode: 'WEB', description: '交易执行 -> Web界面' },
  { id: 'RM_GUI', fromNode: 'RM', toNode: 'GUI', description: '实时监控 -> 图形界面' },
  { id: 'RM_WEB', fromNode: 'RM', toNode: 'WEB', description: '实时监控 -> Web界面' },

  // 实验管理层内部连接
  { id: 'EC_ES', fromNode: 'EC', toNode: 'ES', description: '实验管理核心 -> 实验服务' },
  { id: 'ES_ET', fromNode: 'ES', toNode: 'ET', description: '实验服务 -> 实验模板' },
  { id: 'ET_EW', fromNode: 'ET', toNode: 'EW', description: '实验模板 -> 实验Web界面' },
  { id: 'EW_GUI', fromNode: 'EW', toNode: 'GUI', description: '实验Web界面 -> 图形界面' },
  { id: 'EW_WEB', fromNode: 'EW', toNode: 'WEB', description: '实验Web界面 -> Web界面' },

  // 应用服务层连接
  { id: 'AS_GUI', fromNode: 'AS2', toNode: 'GUI', description: '应用服务层 -> 图形界面' },
  { id: 'AS_WEB', fromNode: 'AS2', toNode: 'WEB', description: '应用服务层 -> Web界面' },
  { id: 'MC_AS', fromNode: 'MC', toNode: 'AS2', description: '元控制器 -> 应用服务层' },
  { id: 'AS_EC', fromNode: 'AS2', toNode: 'EC', description: '应用服务层 -> 实验管理核心' },

  // QLib在线服务模块内部连接
  { id: 'OC_OM', fromNode: 'OC', toNode: 'OM', description: '配置管理 -> 在线管理器' },
  { id: 'OM_OSR', fromNode: 'OM', toNode: 'OSR', description: '在线管理器 -> 在线策略' },
  { id: 'OM_OA', fromNode: 'OM', toNode: 'OA', description: '在线管理器 -> 适配器层' },

  // 配置管理器的输入连接
  { id: 'ES_OC', fromNode: 'ES', toNode: 'OC', description: '实验服务 -> 配置管理' },
  { id: 'EC_OC', fromNode: 'EC', toNode: 'OC', description: '实验管理核心 -> 配置管理' },

  // 适配器层连接
  { id: 'OA_DH', fromNode: 'OA', toNode: 'UP', description: '适配器层 -> 数据中枢层' },
  { id: 'OA_QL', fromNode: 'OA', toNode: 'QD', description: '适配器层 -> QLib核心' },
  { id: 'OA_BL', fromNode: 'OA', toNode: 'SS', description: '适配器层 -> 业务逻辑层' },
  { id: 'OA_AI', fromNode: 'OA', toNode: 'AE', description: '适配器层 -> AI智能策略层' },

  // QLib在线服务输出连接
  { id: 'OM_GUI', fromNode: 'OM', toNode: 'GUI', description: '在线管理器 -> 图形界面' },
  { id: 'OM_WEB', fromNode: 'OM', toNode: 'WEB', description: '在线管理器 -> Web界面' },
  { id: 'OM_EC', fromNode: 'OM', toNode: 'EC', description: '在线管理器 -> 实验管理核心' },
  { id: 'OSR_ES', fromNode: 'OSR', toNode: 'ES', description: '在线策略 -> 实验服务' },
  { id: 'OSR_GUI', fromNode: 'OSR', toNode: 'GUI', description: '在线策略 -> 图形界面' },
  { id: 'OSR_WEB', fromNode: 'OSR', toNode: 'WEB', description: '在线策略 -> Web界面' },

  // QLib分析器输出连接
  { id: 'QA_GUI', fromNode: 'QA', toNode: 'GUI', description: 'QLib分析器 -> 图形界面' },
  { id: 'QA_WEB', fromNode: 'QA', toNode: 'WEB', description: 'QLib分析器 -> Web界面' },
  { id: 'QA_ES', fromNode: 'QA', toNode: 'ES', description: 'QLib分析器 -> 实验服务' },
  { id: 'QA_EC', fromNode: 'QA', toNode: 'EC', description: 'QLib分析器 -> 实验管理核心' },

  // QLib集成和工作流管理虚线输出连接
  { id: 'QI_GUI', fromNode: 'QI', toNode: 'GUI', description: 'QLib集成 -> 图形界面', isDashed: true },
  { id: 'QI_WEB', fromNode: 'QI', toNode: 'WEB', description: 'QLib集成 -> Web界面', isDashed: true },
  { id: 'QI_EC', fromNode: 'QI', toNode: 'EC', description: 'QLib集成 -> 实验管理核心', isDashed: true },
  { id: 'QI_EW', fromNode: 'QI', toNode: 'EW', description: 'QLib集成 -> 实验Web界面', isDashed: true },
  { id: 'QI_EX', fromNode: 'QI', toNode: 'EX', description: 'QLib集成 -> 自动化实验系统', isDashed: true },
  { id: 'QI_TM', fromNode: 'QI', toNode: 'TM', description: 'QLib集成 -> SQLite任务管理器', isDashed: true },
  { id: 'QI_FSM', fromNode: 'QI', toNode: 'FSM', description: 'QLib集成 -> 文件系统存储管理器', isDashed: true },
  { id: 'QI_CM2', fromNode: 'QI', toNode: 'CM2', description: 'QLib集成 -> 配置管理器', isDashed: true },
  { id: 'QI_RG', fromNode: 'QI', toNode: 'RG', description: 'QLib集成 -> 滚动窗口生成器', isDashed: true },
  { id: 'QI_PG', fromNode: 'QI', toNode: 'PG', description: 'QLib集成 -> 参数网格生成器', isDashed: true },
  { id: 'QI_MG', fromNode: 'QI', toNode: 'MG', description: 'QLib集成 -> 多模型生成器', isDashed: true },
  { id: 'QI_LE', fromNode: 'QI', toNode: 'LE', description: 'QLib集成 -> 本地执行器', isDashed: true },
  { id: 'QI_RC', fromNode: 'QI', toNode: 'RC', description: 'QLib集成 -> 结果收集器', isDashed: true },

  // SQLite任务管理器作为核心控制其他组件
  { id: 'TM_FSM', fromNode: 'TM', toNode: 'FSM', description: 'SQLite任务管理器 -> 文件系统存储管理器', isDashed: true },
  { id: 'TM_CM2', fromNode: 'TM', toNode: 'CM2', description: 'SQLite任务管理器 -> 配置管理器', isDashed: true },
  { id: 'TM_RG', fromNode: 'TM', toNode: 'RG', description: 'SQLite任务管理器 -> 滚动窗口生成器', isDashed: true },
  { id: 'TM_PG', fromNode: 'TM', toNode: 'PG', description: 'SQLite任务管理器 -> 参数网格生成器', isDashed: true },
  { id: 'TM_MG', fromNode: 'TM', toNode: 'MG', description: 'SQLite任务管理器 -> 多模型生成器', isDashed: true },
  { id: 'TM_LE', fromNode: 'TM', toNode: 'LE', description: 'SQLite任务管理器 -> 本地执行器', isDashed: true },
  { id: 'TM_RC', fromNode: 'TM', toNode: 'RC', description: 'SQLite任务管理器 -> 结果收集器', isDashed: true },

  // 自动化实验系统内部数据流
  { id: 'FSM_CM2', fromNode: 'FSM', toNode: 'CM2', description: '文件系统存储管理器 -> 配置管理器' },
  { id: 'CM2_RG', fromNode: 'CM2', toNode: 'RG', description: '配置管理器 -> 滚动窗口生成器' },
  { id: 'RG_PG', fromNode: 'RG', toNode: 'PG', description: '滚动窗口生成器 -> 参数网格生成器' },
  { id: 'PG_MG', fromNode: 'PG', toNode: 'MG', description: '参数网格生成器 -> 多模型生成器' },
  { id: 'MG_LE', fromNode: 'MG', toNode: 'LE', description: '多模型生成器 -> 本地执行器' },
  { id: 'LE_RC', fromNode: 'LE', toNode: 'RC', description: '本地执行器 -> 结果收集器' },
  { id: 'RC_TM', fromNode: 'RC', toNode: 'TM', description: '结果收集器 -> SQLite任务管理器' },
  { id: 'TM_GUI', fromNode: 'TM', toNode: 'GUI', description: 'SQLite任务管理器 -> 图形界面' },
  { id: 'TM_WEB', fromNode: 'TM', toNode: 'WEB', description: 'SQLite任务管理器 -> Web界面' },

  // 自动化实验系统输出连接
  { id: 'TM_ES', fromNode: 'TM', toNode: 'ES', description: 'SQLite任务管理器 -> 实验服务' },
  { id: 'FSM_ES', fromNode: 'FSM', toNode: 'ES', description: '文件系统存储管理器 -> 实验服务' },
  { id: 'CM2_ES', fromNode: 'CM2', toNode: 'ES', description: '配置管理器 -> 实验服务' },
  { id: 'RG_ES', fromNode: 'RG', toNode: 'ES', description: '滚动窗口生成器 -> 实验服务' },
  { id: 'PG_ES', fromNode: 'PG', toNode: 'ES', description: '参数网格生成器 -> 实验服务' },
  { id: 'MG_ES', fromNode: 'MG', toNode: 'ES', description: '多模型生成器 -> 实验服务' },
  { id: 'LE_ES', fromNode: 'LE', toNode: 'ES', description: '本地执行器 -> 实验服务' },
  { id: 'RC_ES', fromNode: 'RC', toNode: 'ES', description: '结果收集器 -> 实验服务' },

  // 自动化实验系统输入连接
  { id: 'EX_TM', fromNode: 'EX', toNode: 'TM', description: '自动化实验系统 -> SQLite任务管理器' },
  { id: 'TM_ES2', fromNode: 'TM', toNode: 'ES', description: 'SQLite任务管理器 -> 实验服务(重复连接)' }
])

// 工作流选项 - 基于实际业务流程
const workflowOptions = [
  { label: 'AI策略生成流程 (41节点)', value: 'ai-strategy' },
  { label: '传统策略执行 (36节点)', value: 'traditional' },
  { label: '模型训练流程 (30节点)', value: 'model-training' },
  { label: 'QLib在线服务 (22节点)', value: 'qlib-online' },
  { label: 'QLib集成管理 (79节点)', value: 'qlib-integration' }
]

// 工作流节点配置 - 基于业务逻辑选择性激活节点
const workflowNodes = {
  'ai-strategy': [
    // 数据中枢层关键节点
    'UP', 'CM', 'DP', 'SM', 'MON', 'EXP', 'QD', 'QA', 'QF', 'QE',
    // 业务逻辑层核心节点
    'FE', 'SS', 'SR', 'MM', 'IA', 'QB', 'QP', 'QI',
    // AI策略相关节点
    'ASL', 'AE', 'ML', 'DL', 'OT', 'SG', 'MI', 'ND', 'META', 'RP', 'MC',
    // 实验管理层
    'EC', 'ES', 'ET', 'EW', 'EX', 'TM', 'FSM', 'CM2', 'RG', 'PG', 'MG', 'LE', 'RC',
    // 在线服务模块
    'OM', 'OSR', 'OA', 'OC',
    // 交易层
    'LTDP', 'RM', 'SP', 'TE', 'RS', 'ST', 'UT',
    // 界面层
    'GUI', 'WEB', 'AS2'
  ],
  'traditional': [
    // 数据中枢层
    'UP', 'CM', 'DP', 'SM', 'MON', 'QD', 'QA', 'QF', 'QE',
    // 传统策略业务逻辑
    'FE', 'SS', 'SR', 'IA', 'QB', 'QP',
    // 交易执行层
    'LTDP', 'RM', 'SP', 'TE', 'RS', 'ST', 'UT',
    // 基础实验支持
    'EC', 'ES', 'GUI', 'WEB', 'AS2'
  ],
  'model-training': [
    // 数据支持
    'UP', 'CM', 'SM', 'QD', 'QF', 'QE',
    // 模型训练相关
    'MM', 'ASL', 'AE', 'ML', 'DL', 'OT', 'MI', 'ND', 'META',
    // 实验管理系统
    'EC', 'ES', 'ET', 'EW', 'EX', 'TM', 'FSM', 'CM2', 'RG', 'PG', 'MG', 'LE', 'RC',
    // 界面和监控
    'GUI', 'WEB', 'MON2', 'PERF'
  ],
  'qlib-online': [
    // QLib核心
    'QD', 'QA', 'QF', 'QE', 'QB', 'QP', 'QI',
    // 在线服务模块
    'OM', 'OSR', 'OA', 'OC',
    // 数据和策略支持
    'UP', 'CM', 'FE', 'SS', 'AE', 'ST',
    // 交易执行
    'LTDP', 'RM', 'SP', 'TE', 'RS',
    // 界面
    'GUI', 'WEB'
  ],
  'qlib-integration': mermaidNodes.value.map(n => n.id) // 全部79个节点
}

// 响应式状态
const selectedWorkflow = ref('ai-strategy')
const isActivating = ref(false)
const systemStatus = ref('idle')
const zoomLevel = ref(1)
const selectedNode = ref(null)
const showContextMenu = ref(false)
const contextMenuX = ref(0)
const contextMenuY = ref(0)
const showConfigDrawer = ref(false)
const configNode = ref(null)
const lastUpdateTime = ref('')

// 节点状态
const nodeStates = reactive({})
mermaidNodes.value.forEach(node => {
  nodeStates[node.id] = {
    active: false,
    status: 'inactive',
    lastActivated: null,
    config: {
      cpuLimit: 50,
      memoryLimit: 60,
      name: node.name,
      description: node.description
    }
  }
})

// 计算属性
const activeConnections = computed(() => {
  const activeNodeIds = Object.keys(nodeStates).filter(id => nodeStates[id].active)
  return mermaidConnections.value.filter(conn =>
    activeNodeIds.includes(conn.from) && activeNodeIds.includes(conn.to)
  )
})

const totalNodes = computed(() => mermaidNodes.value.length)
const activeNodes = computed(() => Object.values(nodeStates).filter(state => state.active).length)
const systemStatusText = computed(() => {
  const statusMap = {
    idle: '空闲',
    activating: '激活中',
    running: '运行中',
    error: '错误'
  }
  return statusMap[systemStatus.value] || '未知'
})
const systemStatusType = computed(() => {
  const typeMap = {
    idle: 'default',
    activating: 'warning',
    running: 'success',
    error: 'error'
  }
  return typeMap[systemStatus.value] || 'default'
})
const systemStatusIcon = computed(() => {
  const iconMap = {
    idle: InfoCircleOutlined,
    activating: SyncOutlined,
    running: CheckCircleOutlined,
    error: InfoCircleOutlined
  }
  return iconMap[systemStatus.value] || InfoCircleOutlined
})

// 右键菜单选项
const contextMenuOptions = [
  { label: '查看详情', key: 'view', icon: () => h(InfoCircleOutlined) },
  { label: '编辑配置', key: 'edit', icon: () => h(EditOutlined) },
  { label: '跳过节点', key: 'skip', icon: () => h(SyncOutlined) },
  { type: 'divider' },
  { label: '删除', key: 'delete', icon: () => h(DeleteOutlined) }
]

// 方法定义
const getNodeStyle = (node) => {
  return {
    left: `${node.x}px`,
    top: `${node.y}px`,
    width: `${node.width}px`,
    height: `${node.height}px`
  }
}

const getLayerStyle = (layer) => {
  return {
    left: `${layer.x}px`,
    top: `${layer.y}px`,
    color: layer.color
  }
}

const getOrthogonalPath = (connection) => {
  // 获取源节点和目标节点
  const fromNode = mermaidNodes.value.find(n => n.id === connection.fromNode)
  const toNode = mermaidNodes.value.find(n => n.id === connection.toNode)

  if (!fromNode || !toNode) return ''

  // 计算节点中心点
  const fromCenterX = fromNode.x + fromNode.width / 2
  const fromCenterY = fromNode.y + fromNode.height / 2
  const toCenterX = toNode.x + toNode.width / 2
  const toCenterY = toNode.y + toNode.height / 2

  // 计算相对位置
  const dx = toCenterX - fromCenterX
  const dy = toCenterY - fromCenterY

  // 确定连接点位置（从节点边缘到边缘）
  let fromPointX, fromPointY, toPointX, toPointY

  if (Math.abs(dx) > Math.abs(dy)) {
    // 水平方向连接较多，左右连接
    if (dx > 0) {
      // 从右边到左边
      fromPointX = fromNode.x + fromNode.width
      toPointX = toNode.x
    } else {
      // 从左边到右边
      fromPointX = fromNode.x
      toPointX = toNode.x + toNode.width
    }
    fromPointY = fromCenterY
    toPointY = toCenterY
  } else {
    // 垂直方向连接较多，上下连接
    if (dy > 0) {
      // 从下边到上边
      fromPointY = fromNode.y + fromNode.height
      toPointY = toNode.y
    } else {
      // 从上边到下边
      fromPointY = fromNode.y
      toPointY = toNode.y + toNode.height
    }
    fromPointX = fromCenterX
    toPointX = toCenterX
  }

  // 计算拐点位置 - 确保横平竖直
  let cornerX, cornerY

  if (Math.abs(dx) > Math.abs(dy)) {
    // 主要是水平连接，先走水平，再走垂直
    cornerX = fromPointX + (toPointX - fromPointX) * 0.7
    cornerY = fromPointY
  } else {
    // 主要是垂直连接，先走垂直，再走水平
    cornerX = fromPointX
    cornerY = fromPointY + (toPointY - fromPointY) * 0.7
  }

  // 生成横平竖直的直角路径（带圆角）
  const cornerRadius = 6
  return `M ${fromPointX} ${fromPointY}
          L ${fromPointX} ${cornerY - cornerRadius}
          Q ${fromPointX} ${cornerY} ${fromPointX + cornerRadius} ${cornerY}
          L ${cornerX - cornerRadius} ${cornerY}
          Q ${cornerX} ${cornerY} ${cornerX} ${cornerY + (toPointY > cornerY ? cornerRadius : -cornerRadius)}
          L ${cornerX} ${toPointY}
          L ${toPointX} ${toPointY}`
}

// 获取层级分组框样式
const getLayerGroupStyle = (layer) => {
  return {
    left: `${layer.x}px`,
    top: `${layer.y}px`,
    width: `${layer.width}px`,
    height: `${layer.height}px`,
    backgroundColor: layer.color,
    borderColor: layer.borderColor
  }
}

// 节点图标映射函数
const getNodeIcon = (type) => {
  const iconMap = {
    cluster: ClusterOutlined,
    api: ApiOutlined,
    data: DatabaseOutlined,
    process: ApiToolOutlined,
    analysis: BarChartOutlined,
    monitor: DashboardOutlined,
    tool: ToolOutlined,
    robot: RobotOutlined,
    deployment: DeploymentUnitOutlined,
    thunderbolt: ThunderboltOutlined,
    sync: SyncOutlined,
    function: FunctionOutlined,
    bug: BugOutlined,
    router: RouterOutlined,
    experiment: ExperimentOutlined,
    switcher: SwitcherOutlined,
    desktop: DesktopOutlined,
    laptop: LaptopOutlined,
    hdd: HddOutlined,
    cloud: CloudOutlined,
    setting: SettingOutlined,
    safety: SafetyCertificateOutlined,
    security: SecurityScanOutlined,
    code: CodeOutlined,
    linechart: LineChartOutlined,
    barchart: BarChartOutlined,
    piechart: PieChartOutlined,
    partition: PartitionOutlined,
    shield: ShieldOutlined,
    gateway: GatewayOutlined,
    link: LinkOutlined,
    integration: IntegrationOutlined,
    fire: FireOutlined
  }
  return iconMap[type] || NodeIndexOutlined
}

const handleWorkflowChange = () => {
  resetNodes()
}

const activateWorkflow = async () => {
  isActivating.value = true
  systemStatus.value = 'activating'

  const workflowNodeIds = workflowNodes[selectedWorkflow.value] || []

  for (let i = 0; i < workflowNodeIds.length; i++) {
    const nodeId = workflowNodeIds[i]
    await new Promise(resolve => setTimeout(resolve, 200))

    if (nodeStates[nodeId]) {
      nodeStates[nodeId].active = true
      nodeStates[nodeId].lastActivated = new Date()
    }
  }

  systemStatus.value = 'running'
  isActivating.value = false
  updateLastTime()
}

const resetNodes = () => {
  Object.keys(nodeStates).forEach(nodeId => {
    nodeStates[nodeId].active = false
    nodeStates[nodeId].lastActivated = null
  })
  systemStatus.value = 'idle'
}

const activateAllNodes = async () => {
  isActivating.value = true
  systemStatus.value = 'activating'

  for (let i = 0; i < mermaidNodes.value.length; i++) {
    const node = mermaidNodes.value[i]
    await new Promise(resolve => setTimeout(resolve, 100))

    if (nodeStates[node.id]) {
      nodeStates[node.id].active = true
      nodeStates[node.id].lastActivated = new Date()
    }
  }

  systemStatus.value = 'running'
  isActivating.value = false
  updateLastTime()
}

const handleNodeClick = (node) => {
  selectedNode.value = node
}

const handleNodeRightClick = (node, event) => {
  selectedNode.value = node
  contextMenuX.value = event.clientX
  contextMenuY.value = event.clientY
  showContextMenu.value = true
}

const closeContextMenu = () => {
  showContextMenu.value = false
}

const handleContextMenuSelect = (key) => {
  switch (key) {
    case 'view':
      // 详情查看已通过selectedNode实现
      break
    case 'edit':
      configNode.value = { ...selectedNode.value, ...nodeStates[selectedNode.value.id].config }
      showConfigDrawer.value = true
      break
    case 'skip':
      nodeStates[selectedNode.value.id].active = false
      break
    case 'delete':
      // 实际删除功能
      break
  }
  closeContextMenu()
}

const saveNodeConfig = () => {
  if (configNode.value) {
    nodeStates[configNode.value.id].config = { ...configNode.value }
    showConfigDrawer.value = false
  }
}

const zoomIn = () => {
  zoomLevel.value = Math.min(zoomLevel.value + 0.1, 2)
}

const zoomOut = () => {
  zoomLevel.value = Math.max(zoomLevel.value - 0.1, 0.5)
}

const fitView = () => {
  zoomLevel.value = 1
}

const updateLastTime = () => {
  lastUpdateTime.value = new Date().toLocaleTimeString()
}

onMounted(() => {
  updateLastTime()
})
</script>

<style scoped>
.intelligent-node-system {
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
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.panel-left {
  display: flex;
  align-items: center;
  gap: 24px;
}

.system-title {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #00d4ff;
}

.mermaid-container {
  flex: 1;
  position: relative;
  overflow: auto;
  background: radial-gradient(circle at 20% 50%, rgba(0, 212, 255, 0.05) 0%, transparent 50%),
              radial-gradient(circle at 80% 80%, rgba(123, 104, 238, 0.05) 0%, transparent 50%);
}

.node-canvas {
  position: relative;
  width: 1400px;
  height: 1200px;
  transition: transform 0.3s ease;
}

/* 层级分组框样式 - Mermaid风格 */
.layer-group {
  position: absolute;
  border: 2px solid;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(5px);
  z-index: 0;
}

.layer-group-header {
  padding: 8px 12px;
  background: rgba(0, 0, 0, 0.2);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 6px 6px 0 0;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.layer-group-title {
  font-size: 12px;
  font-weight: 600;
  color: #ffffff;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.layer-group-subtitle {
  font-size: 10px;
  color: rgba(255, 255, 255, 0.7);
  font-style: italic;
}

/* 节点样式 */
.node {
  position: absolute;
  background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
  border: 2px solid #4a5568;
  border-radius: 6px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
  padding: 6px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
  z-index: 10; /* 确保节点在分组框之上 */
  min-width: 80px;
  font-size: 10px;
}

.node:hover {
  filter: brightness(1.2);
  border-color: #00d4ff;
  border-width: 2px;
  transform: translateY(-1px);
  box-shadow: 0 6px 20px rgba(0, 212, 255, 0.3);
}

.node.active {
  border-color: #00ff88;
  border-width: 2px;
  box-shadow: 0 0 15px rgba(0, 255, 136, 0.4);
}

.node-icon {
  position: absolute;
  top: 4px;
  left: 4px;
  width: 16px;
  height: 16px;
  border-radius: 3px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.2);
  color: #ffffff;
}

.node-title {
  font-size: 10px;
  font-weight: 600;
  text-align: center;
  color: #e2e8f0;
  line-height: 1.2;
  margin-top: 8px;
  padding: 0 2px;
  word-break: break-all;
  max-width: 100%;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.node-id {
  position: absolute;
  top: 4px;
  right: 4px;
  font-size: 8px;
  font-weight: 600;
  color: #a0aec0;
  background: rgba(0, 0, 0, 0.3);
  padding: 1px 3px;
  border-radius: 2px;
}

.node.active .node-id {
  color: #00ff88;
  background: rgba(0, 255, 136, 0.1);
}

/* 连接线样式 */
.connections {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 1;
}

.connection-svg {
  position: absolute;
  width: 100%;
  height: 100%;
}

.connection-path {
  transition: all 0.3s ease;
  stroke-linecap: round;
  stroke-linejoin: round;
}

.connection-path.active {
  stroke-dasharray: 8, 4;
  animation: circuitFlow 2s linear infinite;
}

.connection-path.dashed {
  stroke-dasharray: 5, 5;
  opacity: 0.6;
}

.connection-path.dashed.active {
  stroke-dasharray: 5, 5;
  animation: circuitFlow 2s linear infinite;
}

@keyframes circuitFlow {
  0% { stroke-dashoffset: 0; }
  100% { stroke-dashoffset: -24; }
}

.connection-path:hover {
  stroke-width: 4;
  filter: drop-shadow(0 0 6px rgba(0, 255, 136, 0.5));
}

/* 层级标签样式 */
.layer-label {
  position: absolute;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 1px;
  opacity: 0.7;
  pointer-events: none;
}

/* 信息面板样式 */
.info-panel {
  position: absolute;
  top: 80px;
  right: 20px;
  width: 280px;
  max-height: 400px;
  overflow-y: auto;
  background: rgba(15, 20, 25, 0.9);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.info-section {
  margin-bottom: 20px;
}

.info-section h4 {
  margin: 0 0 8px 0;
  color: #00d4ff;
  font-size: 14px;
  font-weight: 600;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
  font-size: 13px;
}

.node-info {
  font-size: 13px;
}

.node-info p {
  margin: 4px 0;
}

.no-selection {
  text-align: center;
  opacity: 0.6;
  font-style: italic;
  padding: 20px 0;
}

.node-config {
  padding: 16px 0;
}

/* 状态栏样式 */
.status-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 20px;
  background: rgba(15, 20, 25, 0.9);
  backdrop-filter: blur(10px);
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  font-size: 12px;
  color: #718096;
}

.status-left, .status-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .info-panel {
    width: 240px;
  }
}

@media (max-width: 768px) {
  .control-panel {
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
  }

  .panel-left, .panel-right {
    justify-content: center;
  }

  .system-title {
    font-size: 16px;
  }

  .info-panel {
    position: static;
    width: 100%;
    max-height: 200px;
    margin: 16px;
  }
}
</style>
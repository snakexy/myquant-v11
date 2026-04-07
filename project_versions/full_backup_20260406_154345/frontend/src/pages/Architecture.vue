<template>
  <div class="architecture">
    <div class="architecture-header">
      <h1 class="architecture-title">系统架构图</h1>
      <p class="architecture-subtitle">可视化量化交易系统架构与数据流</p>
    </div>
    
    <div class="architecture-container">
      <!-- 架构图区域 -->
      <div class="architecture-graph">
        <ArchitectureGraph
          :nodes="graphNodes"
          :edges="graphEdges"
          :options="graphOptions"
          :loading="graphLoading"
          @node-click="handleNodeClick"
          @edge-click="handleEdgeClick"
          @select="handleSelect"
          @deselect="handleDeselect"
        />
      </div>
      
      <!-- 控制面板 -->
      <div class="architecture-controls">
        <QuantCard title="架构控制" size="medium">
          <!-- 功能选择 -->
          <div class="control-section">
            <h4>功能模块</h4>
            <div class="function-modules">
              <div
                v-for="module in functionModules"
                :key="module.id"
                :class="getModuleClass(module)"
                @click="handleModuleToggle(module)"
              >
                <n-icon :size="16">
                  <component :is="module.icon" />
                </n-icon>
                <span>{{ module.name }}</span>
              </div>
            </div>
          </div>
          
          <!-- 视图控制 -->
          <div class="control-section">
            <h4>视图控制</h4>
            <div class="view-controls">
              <QuantButton
                size="small"
                type="ghost"
                @click="handleFitView"
              >
                适应视图
              </QuantButton>
              <QuantButton
                size="small"
                type="ghost"
                @click="handleResetView"
              >
                重置视图
              </QuantButton>
              <QuantButton
                size="small"
                type="ghost"
                @click="handleTogglePhysics"
              >
                {{ physicsEnabled ? '禁用物理' : '启用物理' }}
              </QuantButton>
            </div>
          </div>
          
          <!-- 数据流控制 -->
          <div class="control-section">
            <h4>数据流控制</h4>
            <div class="dataflow-controls">
              <QuantButton
                size="small"
                :type="dataflowEnabled ? 'primary' : 'ghost'"
                @click="handleToggleDataflow"
              >
                {{ dataflowEnabled ? '停止数据流' : '启动数据流' }}
              </QuantButton>
              <div class="speed-control">
                <label>流速:</label>
                <input
                  v-model="dataflowSpeed"
                  type="range"
                  min="1"
                  max="10"
                  @change="handleSpeedChange"
                />
                <span>{{ dataflowSpeed }}</span>
              </div>
            </div>
          </div>
          
          <!-- 节点信息 -->
          <div v-if="selectedNode" class="control-section">
            <h4>节点信息</h4>
            <div class="node-info">
              <div class="info-item">
                <label>名称:</label>
                <span>{{ selectedNode.label }}</span>
              </div>
              <div class="info-item">
                <label>类型:</label>
                <span>{{ getNodeTypeName(selectedNode.group) }}</span>
              </div>
              <div class="info-item">
                <label>状态:</label>
                <span :class="getStatusClass(selectedNode.status)">
                  {{ getStatusText(selectedNode.status) }}
                </span>
              </div>
              <div v-if="selectedNode.metrics" class="info-item">
                <label>指标:</label>
                <div class="metrics">
                  <div
                    v-for="(value, key) in selectedNode.metrics"
                    :key="key"
                    class="metric-item"
                  >
                    <span class="metric-key">{{ key }}:</span>
                    <span class="metric-value">{{ value }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </QuantCard>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { NIcon } from 'naive-ui'
import QuantCard from '@/components/ui/Card.vue'
import QuantButton from '@/components/ui/Button.vue'
import QuantModal from '@/components/ui/Modal.vue'
import QuantForm from '@/components/ui/Form.vue'
import QuantFormItem from '@/components/ui/Form.vue'
import QuantInput from '@/components/ui/Input.vue'
import ArchitectureGraph from '@/components/charts/ArchitectureGraph.vue'
import { useArchitectureStore } from '@/stores'
import type {
  ArchitectureNode,
  ArchitectureEdge,
  GraphOptions,
  FunctionModule
} from '@/types'

const architectureStore = useArchitectureStore()

// 响应式数据
const graphLoading = ref(false)
const physicsEnabled = ref(true)
const dataflowEnabled = ref(false)
const dataflowSpeed = ref(5)
const selectedNode = ref<ArchitectureNode | null>(null)
const configModalVisible = ref(false)
const configModalType = ref<'node' | 'edge'>('node')

// 节点配置
const nodeConfig = reactive({
  id: '',
  label: '',
  group: 'processor',
  status: 'active'
})

const edgeConfig = reactive({
  id: '',
  label: '',
  dataType: 'realtime'
})

// 配置规则
const nodeConfigRules = {
  label: [
    { required: true, message: '请输入节点名称', trigger: 'blur' }
  ],
  group: [
    { required: true, message: '请选择节点类型', trigger: 'change' }
  ]
}

const edgeConfigRules = {
  label: [
    { required: true, message: '请输入连接名称', trigger: 'blur' }
  ],
  dataType: [
    { required: true, message: '请选择数据类型', trigger: 'change' }
  ]
}

// 功能模块
const functionModules = ref<FunctionModule[]>([
  { id: 'data', name: '数据层', icon: 'DatabaseOutlined', enabled: true },
  { id: 'processing', name: '处理层', icon: 'ApiOutlined', enabled: true },
  { id: 'model', name: '模型层', icon: 'ExperimentOutlined', enabled: true },
  { id: 'strategy', name: '策略层', icon: 'ThunderboltOutlined', enabled: true },
  { id: 'trading', name: '交易层', icon: 'TradeOutlined', enabled: true },
  { id: 'monitoring', name: '监控层', icon: 'EyeOutlined', enabled: true }
])

// 图数据
const graphNodes = computed(() => architectureStore.nodes)
const graphEdges = computed(() => architectureStore.edges)

// 图配置
const graphOptions = computed<GraphOptions>(() => ({
  nodes: {
    shape: 'dot',
    size: 20,
    font: {
      size: 12,
      color: '#ffffff'
    },
    borderWidth: 2,
    shadow: true
  },
  edges: {
    width: 2,
    arrows: {
      to: {
        enabled: true,
        scaleFactor: 0.8
      }
    },
    smooth: {
      type: 'curvedCW',
      roundness: 0.2
    }
  },
  physics: {
    enabled: physicsEnabled.value,
    barnesHut: {
      gravitationalConstant: -2000,
      centralGravity: 0.3,
      springLength: 95,
      springConstant: 0.04,
      damping: 0.09
    }
  },
  interaction: {
    hover: true,
    tooltipDelay: 200,
    zoomView: true,
    dragView: true
  }
}))

// 事件处理函数
const handleNodeClick = (node: ArchitectureNode) => {
  selectedNode.value = node
  console.log('节点点击:', node)
}

const handleEdgeClick = (edge: ArchitectureEdge) => {
  console.log('连接点击:', edge)
}

const handleSelect = (params: any) => {
  console.log('选择事件:', params)
}

const handleDeselect = (params: any) => {
  console.log('取消选择:', params)
}

const handleModuleToggle = (module: FunctionModule) => {
  module.enabled = !module.enabled
  updateGraphVisibility()
}

const handleFitView = () => {
  // 适应视图逻辑
  console.log('适应视图')
}

const handleResetView = () => {
  // 重置视图逻辑
  console.log('重置视图')
}

const handleTogglePhysics = () => {
  physicsEnabled.value = !physicsEnabled.value
  updateGraphOptions()
}

const handleToggleDataflow = () => {
  dataflowEnabled.value = !dataflowEnabled.value
  if (dataflowEnabled.value) {
    startDataflowAnimation()
  } else {
    stopDataflowAnimation()
  }
}

const handleSpeedChange = () => {
  if (dataflowEnabled.value) {
    stopDataflowAnimation()
    startDataflowAnimation()
  }
}

const handleConfigConfirm = () => {
  if (configModalType.value === 'node') {
    architectureStore.updateNode(nodeConfig)
  } else {
    architectureStore.updateEdge(edgeConfig)
  }
  configModalVisible.value = false
}

const handleConfigCancel = () => {
  configModalVisible.value = false
}

// 工具函数
const getModuleClass = (module: FunctionModule) => {
  return {
    'module-item': true,
    'module-item--active': module.enabled
  }
}

const getNodeTypeName = (group: string) => {
  const typeMap = {
    dataSource: '数据源',
    processor: '处理器',
    model: '模型',
    strategy: '策略',
    output: '输出'
  }
  return typeMap[group] || '未知'
}

const getStatusClass = (status: string) => {
  return {
    'status-active': status === 'active',
    'status-inactive': status === 'inactive',
    'status-error': status === 'error'
  }
}

const getStatusText = (status: string) => {
  const statusMap = {
    active: '运行中',
    inactive: '已停止',
    error: '错误'
  }
  return statusMap[status] || '未知'
}

const updateGraphVisibility = () => {
  const enabledModules = functionModules.value
    .filter(module => module.enabled)
    .map(module => module.id)
  
  // 更新节点和边的可见性
  architectureStore.updateGraphVisibility(enabledModules)
}

const updateGraphOptions = () => {
  // 更新图配置
  console.log('更新图配置:', physicsEnabled.value)
}

let dataflowInterval: number | null = null

const startDataflowAnimation = () => {
  dataflowInterval = setInterval(() => {
    architectureStore.simulateDataflow()
  }, 1000 / dataflowSpeed.value)
}

const stopDataflowAnimation = () => {
  if (dataflowInterval) {
    clearInterval(dataflowInterval)
    dataflowInterval = null
  }
}

// 生命周期
onMounted(async () => {
  graphLoading.value = true
  try {
    await architectureStore.fetchArchitectureData()
  } catch (error) {
    console.error('获取架构数据失败:', error)
  } finally {
    graphLoading.value = false
  }
})

onUnmounted(() => {
  stopDataflowAnimation()
})
</script>

<style lang="scss" scoped>
.architecture {
  padding: var(--spacing-4);
  max-width: 1400px;
  margin: 0 auto;
  
  &-header {
    text-align: center;
    margin-bottom: var(--spacing-6);
  }
  
  &-title {
    font-size: var(--font-size-xl);
    font-weight: 700;
    color: var(--text-primary);
    margin: 0 0 var(--spacing-2) 0;
    background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }
  
  &-subtitle {
    font-size: var(--font-size-base);
    color: var(--text-secondary);
    margin: 0;
  }
  
  &-container {
    display: grid;
    grid-template-columns: 1fr 320px;
    gap: var(--spacing-4);
    margin-bottom: var(--spacing-6);
  }
  
  &-graph {
    background: var(--bg-color-base);
    border: 1px solid var(--border-color)-base;
    border-radius: var(--border-radius-lg);
    height: 600px;
    overflow: hidden;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  }
  
  &-controls {
    .control-section {
      margin-bottom: var(--spacing-4);
      
      h4 {
        font-size: var(--font-size-base);
        font-weight: 600;
        color: var(--text-primary);
        margin: 0 0 var(--spacing-2) 0;
      }
    }
    
    .function-modules {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: var(--spacing-2);
    }
    
    .module-item {
      display: flex;
      align-items: center;
      gap: var(--spacing-1);
      padding: var(--spacing-2);
      border: 1px solid var(--border-color)-base;
      border-radius: var(--border-radius-base);
      cursor: pointer;
      transition: all var(--transition-duration-base) var(--transition-timing-function-base);
      
      &:hover {
        background-color: var(--bg-color-secondary);
      }
      
      &--active {
        background-color: var(--primary-color);
        border-color: var(--primary-color);
        color: var(--white);
      }
    }
    
    .view-controls {
      display: flex;
      flex-direction: column;
      gap: var(--spacing-2);
    }
    
    .dataflow-controls {
      display: flex;
      flex-direction: column;
      gap: var(--spacing-2);
    }
    
    .speed-control {
      display: flex;
      align-items: center;
      gap: var(--spacing-2);
      
      label {
        font-size: var(--font-size-sm);
        color: var(--text-secondary);
      }
      
      input {
        flex: 1;
      }
      
      span {
        font-size: var(--font-size-sm);
        color: var(--text-primary);
        min-width: 20px;
        text-align: center;
      }
    }
    
    .node-info {
      .info-item {
        display: flex;
        margin-bottom: var(--spacing-2);
        
        label {
          font-weight: 500;
          color: var(--text-secondary);
          min-width: 60px;
        }
        
        span {
          color: var(--text-primary);
        }
      }
      
      .metrics {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: var(--spacing-1);
        margin-top: var(--spacing-2);
      }
      
      .metric-item {
        display: flex;
        justify-content: space-between;
        padding: var(--spacing-1);
        background-color: var(--bg-color-secondary);
        border-radius: var(--border-radius-base);
      }
      
      .metric-key {
        font-size: var(--font-size-xs);
        color: var(--text-secondary);
      }
      
      .metric-value {
        font-size: var(--font-size-sm);
        font-weight: 500;
        color: var(--text-primary);
      }
    }
  }
}

.status-active {
  color: var(--success-color);
}

.status-inactive {
  color: var(--text-secondary);
}

.status-error {
  color: var(--danger-color);
}

.config-form {
  padding: var(--spacing-2) 0;
}

// 响应式设计
@media (max-width: 1024px) {
  .architecture {
    &-container {
      grid-template-columns: 1fr;
    }
    
    &-graph {
      height: 400px;
    }
  }
}

@media (max-width: 768px) {
  .architecture {
    padding: var(--spacing-2);
    
    .function-modules {
      grid-template-columns: 1fr;
    }
  }
}
</style>
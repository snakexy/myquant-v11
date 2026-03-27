<template>
  <div class="architecture-graph">
    <!-- 2.5D节点图容器 -->
    <div class="graph-container" ref="graphContainer">
      <div class="graph-canvas" ref="graphCanvas">
        <!-- 背景层：数据中枢层 -->
        <div class="layer background-layer">
          <div class="layer-title">数据中枢层</div>
          <div class="nodes-container">
            <div 
              v-for="node in dataHubNodes" 
              :key="node.id"
              :class="['node', 'data-hub', getNodeStatusClass(node.status)]"
              :style="getNodeStyle(node)"
              @click="selectNode(node)"
              @dblclick="openNodeDetails(node)"
            >
              <div class="node-icon">{{ node.icon }}</div>
              <div class="node-title">{{ node.title }}</div>
              <div class="node-progress">
                <div class="progress-bar" :style="{ width: node.progress + '%' }"></div>
              </div>
            </div>
          </div>
        </div>

        <!-- 中景层：QLib核心接口层 -->
        <div class="layer middle-layer">
          <div class="layer-title">QLib核心接口层</div>
          <div class="nodes-container">
            <div 
              v-for="node in qlibNodes" 
              :key="node.id"
              :class="['node', 'qlib', getNodeStatusClass(node.status)]"
              :style="getNodeStyle(node)"
              @click="selectNode(node)"
              @dblclick="openNodeDetails(node)"
            >
              <div class="node-icon">{{ node.icon }}</div>
              <div class="node-title">{{ node.title }}</div>
              <div class="node-progress">
                <div class="progress-bar" :style="{ width: node.progress + '%' }"></div>
              </div>
            </div>
          </div>
        </div>

        <!-- 前景层：业务逻辑层 -->
        <div class="layer foreground-layer">
          <div class="layer-title">业务逻辑层</div>
          <div class="nodes-container">
            <div 
              v-for="node in businessNodes" 
              :key="node.id"
              :class="['node', 'business', getNodeStatusClass(node.status)]"
              :style="getNodeStyle(node)"
              @click="selectNode(node)"
              @dblclick="openNodeDetails(node)"
            >
              <div class="node-icon">{{ node.icon }}</div>
              <div class="node-title">{{ node.title }}</div>
              <div class="node-progress">
                <div class="progress-bar" :style="{ width: node.progress + '%' }"></div>
              </div>
            </div>
          </div>
        </div>

        <!-- 连接线 -->
        <svg class="connections" :width="canvasWidth" :height="canvasHeight">
          <defs>
            <linearGradient id="flowGradient" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" style="stop-color:#2563eb;stop-opacity:0" />
              <stop offset="50%" style="stop-color:#2563eb;stop-opacity:1" />
              <stop offset="100%" style="stop-color:#2563eb;stop-opacity:0" />
            </linearGradient>
          </defs>
          
          <!-- 数据流连接线 -->
          <path 
            v-for="connection in connections" 
            :key="connection.id"
            :d="connection.path"
            :stroke="getConnectionColor(connection.status)"
            stroke-width="3"
            fill="none"
            class="connection-line"
          >
            <animate 
              attributeName="stroke-dasharray" 
              values="0 100;100 0" 
              dur="2s" 
              repeatCount="indefinite" 
            />
          </path>
        </svg>
      </div>
    </div>

    <!-- 节点详情浮动面板 -->
    <div 
      v-if="selectedNode" 
      class="node-details-panel"
      :style="getPanelStyle()"
    >
      <div class="panel-header">
        <span class="panel-icon">{{ selectedNode.icon }}</span>
        <h3 class="panel-title">{{ selectedNode.title }}</h3>
        <button @click="closeNodeDetails" class="close-btn">×</button>
      </div>
      <div class="panel-content">
        <div class="node-info">
          <div class="info-item">
            <label>状态:</label>
            <span :class="['status-badge', selectedNode.status]">{{ getStatusText(selectedNode.status) }}</span>
          </div>
          <div class="info-item">
            <label>进度:</label>
            <div class="progress-info">
              <div class="progress-bar-small" :style="{ width: selectedNode.progress + '%' }"></div>
              <span class="progress-text">{{ selectedNode.progress }}%</span>
            </div>
          </div>
          <div class="info-item">
            <label>描述:</label>
            <p class="node-description">{{ selectedNode.description }}</p>
          </div>
        </div>
        
        <!-- 节点特定配置 -->
        <div class="node-config" v-if="selectedNode.config">
          <h4>节点配置</h4>
          <div class="config-items">
            <div 
              v-for="(value, key) in selectedNode.config" 
              :key="key"
              class="config-item"
            >
              <label>{{ key }}:</label>
              <input 
                v-if="typeof value === 'number'"
                type="number" 
                v-model.number="selectedNode.config[key]"
                class="config-input"
              />
              <select 
                v-else-if="Array.isArray(value)"
                v-model="selectedNode.config[key]"
                class="config-select"
              >
                <option 
                  v-for="option in value" 
                  :key="option" 
                  :value="option"
                >
                  {{ option }}
                </option>
              </select>
              <input 
                v-else
                type="text" 
                v-model="selectedNode.config[key]"
                class="config-input"
              />
            </div>
          </div>
        </div>
        
        <!-- 节点操作 -->
        <div class="node-actions">
          <button @click="startNode" class="action-btn start-btn" :disabled="selectedNode.status === 'running'">
            🟢 启动
          </button>
          <button @click="pauseNode" class="action-btn pause-btn" :disabled="selectedNode.status !== 'running'">
            🟡 暂停
          </button>
          <button @click="stopNode" class="action-btn stop-btn">
            🔴 停止
          </button>
          <button @click="restartNode" class="action-btn restart-btn">
            🔄 重启
          </button>
        </div>
      </div>
    </div>

    <!-- 全局控制面板 -->
    <div class="control-panel">
      <div class="panel-header">
        <h3>🎮 回测控制台</h3>
      </div>
      <div class="panel-content">
        <div class="control-buttons">
          <button @click="startBacktest" class="control-btn start-backtest" :disabled="isBacktestRunning">
            🟢 开始回测
          </button>
          <button @click="pauseBacktest" class="control-btn pause-backtest" :disabled="!isBacktestRunning">
            🟡 暂停
          </button>
          <button @click="stopBacktest" class="control-btn stop-backtest">
            🔴 停止
          </button>
          <button @click="resetBacktest" class="control-btn reset-backtest">
            🔄 重置
          </button>
        </div>
        
        <div class="progress-section">
          <div class="progress-item">
            <label>回测进度:</label>
            <div class="progress-bar-container">
              <div class="progress-bar-large" :style="{ width: backtestProgress + '%' }"></div>
              <span class="progress-text-large">{{ backtestProgress }}%</span>
            </div>
          </div>
          <div class="progress-item">
            <label>预计剩余:</label>
            <span class="time-remaining">{{ estimatedTimeRemaining }}</span>
          </div>
        </div>
        
        <div class="performance-monitor">
          <h4>性能监控</h4>
          <div class="performance-item">
            <label>CPU:</label>
            <div class="performance-bar">
              <div class="performance-fill" :style="{ width: systemPerformance.cpu + '%' }"></div>
              <span>{{ systemPerformance.cpu }}%</span>
            </div>
          </div>
          <div class="performance-item">
            <label>内存:</label>
            <div class="performance-bar">
              <div class="performance-fill" :style="{ width: systemPerformance.memory + '%' }"></div>
              <span>{{ systemPerformance.memory }}%</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted, nextTick } from 'vue'

// 节点接口定义
interface Node {
  id: string
  title: string
  icon: string
  description: string
  status: 'running' | 'processing' | 'error' | 'waiting' | 'completed'
  progress: number
  x: number
  y: number
  layer: 'background' | 'middle' | 'foreground'
  config?: Record<string, any>
}

interface Connection {
  id: string
  from: string
  to: string
  path: string
  status: 'active' | 'processing' | 'error' | 'inactive'
}

// 响应式数据
const graphContainer = ref<HTMLElement>()
const graphCanvas = ref<HTMLElement>()
const canvasWidth = ref(800)
const canvasHeight = ref(600)
const selectedNode = ref<Node | null>(null)

// 数据中枢层节点
const dataHubNodes = ref<Node[]>([
  {
    id: 'data-provider',
    title: '统一数据提供器',
    icon: '📊',
    description: '多源数据整合，统一访问接口，数据格式转换',
    status: 'running',
    progress: 85,
    x: 150,
    y: 100,
    layer: 'background',
    config: {
      '数据源': ['股票行情', '基本面数据', '技术指标数据'],
      '更新频率': '实时',
      '缓存策略': '智能缓存'
    }
  },
  {
    id: 'cache-manager',
    title: '缓存管理器',
    icon: '💾',
    description: '智能缓存策略，内存+Redis缓存，缓存命中率优化',
    status: 'running',
    progress: 75,
    x: 400,
    y: 100,
    layer: 'background',
    config: {
      '缓存类型': 'Redis',
      '内存限制': '4GB',
      'TTL': '3600秒'
    }
  },
  {
    id: 'data-pipeline',
    title: '数据管道',
    icon: '🔄',
    description: '数据流处理，ETL流程，数据质量控制',
    status: 'processing',
    progress: 60,
    x: 650,
    y: 100,
    layer: 'background'
  }
])

// QLib核心接口层节点
const qlibNodes = ref<Node[]>([
  {
    id: 'qlib-provider',
    title: 'QLib数据提供器',
    icon: '🔌',
    description: '数据标准化，QLib格式转换，数据质量控制',
    status: 'processing',
    progress: 70,
    x: 150,
    y: 250,
    layer: 'middle',
    config: {
      '数据格式': 'QLib',
      '质量控制': '启用',
      '标准化': '自动'
    }
  },
  {
    id: 'qlib-analyzer',
    title: 'QLib分析器',
    icon: '📈',
    description: '技术分析，因子计算，统计分析',
    status: 'waiting',
    progress: 0,
    x: 400,
    y: 250,
    layer: 'middle'
  },
  {
    id: 'qlib-backtest',
    title: 'QLib回测引擎',
    icon: '🧪',
    description: '真实QLib框架，专业回测计算，性能分析',
    status: 'waiting',
    progress: 0,
    x: 650,
    y: 250,
    layer: 'middle',
    config: {
      '回测模式': '完整回测',
      '基准对比': '沪深300',
      '风险模型': 'VaR'
    }
  }
])

// 业务逻辑层节点
const businessNodes = ref<Node[]>([
  {
    id: 'factor-engine',
    title: '因子计算引擎',
    icon: '🧮',
    description: 'Alpha158/360，标准因子集，自定义因子',
    status: 'waiting',
    progress: 0,
    x: 150,
    y: 400,
    layer: 'foreground',
    config: {
      '因子库': 'Alpha158',
      '计算频率': '每日',
      '因子数量': '360'
    }
  },
  {
    id: 'strategy-system',
    title: '策略系统',
    icon: '🎯',
    description: '策略创建，策略执行，策略监控',
    status: 'waiting',
    progress: 0,
    x: 400,
    y: 400,
    layer: 'foreground'
  },
  {
    id: 'strategy-replay',
    title: '策略回放系统',
    icon: '⏮️',
    description: '历史回放，性能验证，风险分析',
    status: 'waiting',
    progress: 0,
    x: 650,
    y: 400,
    layer: 'foreground'
  }
])

// 连接线
const connections = ref<Connection[]>([
  {
    id: 'data-to-qlib',
    from: 'data-provider',
    to: 'qlib-provider',
    path: 'M 150 150 L 150 250',
    status: 'active'
  },
  {
    id: 'cache-to-qlib',
    from: 'cache-manager',
    to: 'qlib-analyzer',
    path: 'M 400 150 L 400 250',
    status: 'active'
  },
  {
    id: 'pipeline-to-qlib',
    from: 'data-pipeline',
    to: 'qlib-backtest',
    path: 'M 650 150 L 650 250',
    status: 'processing'
  },
  {
    id: 'qlib-to-factor',
    from: 'qlib-provider',
    to: 'factor-engine',
    path: 'M 150 300 L 150 400',
    status: 'inactive'
  },
  {
    id: 'analyzer-to-strategy',
    from: 'qlib-analyzer',
    to: 'strategy-system',
    path: 'M 400 300 L 400 400',
    status: 'inactive'
  },
  {
    id: 'backtest-to-replay',
    from: 'qlib-backtest',
    to: 'strategy-replay',
    path: 'M 650 300 L 650 400',
    status: 'inactive'
  }
])

// 回测状态
const isBacktestRunning = ref(false)
const backtestProgress = ref(0)
const estimatedTimeRemaining = ref('5分钟')

// 系统性能
const systemPerformance = reactive({
  cpu: 65,
  memory: 78,
  gpu: 35
})

// 方法
const getNodeStatusClass = (status: string) => {
  const statusMap = {
    running: 'status-running',
    processing: 'status-processing',
    error: 'status-error',
    waiting: 'status-waiting',
    completed: 'status-completed'
  }
  return statusMap[status] || 'status-waiting'
}

const getNodeStyle = (node: Node) => {
  const scale = node.layer === 'background' ? 0.8 : node.layer === 'middle' ? 0.9 : 1.0
  return {
    left: node.x + 'px',
    top: node.y + 'px',
    transform: `scale(${scale})`,
    zIndex: node.layer === 'background' ? 1 : node.layer === 'middle' ? 2 : 3
  }
}

const getConnectionColor = (status: string) => {
  const colorMap = {
    active: '#2563eb',
    processing: '#f59e0b',
    error: '#ef4444',
    inactive: '#64748b'
  }
  return colorMap[status] || '#64748b'
}

const getStatusText = (status: string) => {
  const textMap = {
    running: '运行中',
    processing: '处理中',
    error: '错误',
    waiting: '等待中',
    completed: '已完成'
  }
  return textMap[status] || '未知'
}

const getPanelStyle = () => {
  if (!selectedNode.value) return {}
  return {
    left: (selectedNode.value.x + 100) + 'px',
    top: selectedNode.value.y + 'px'
  }
}

const selectNode = (node: Node) => {
  selectedNode.value = node
}

const openNodeDetails = (node: Node) => {
  selectedNode.value = node
}

const closeNodeDetails = () => {
  selectedNode.value = null
}

const startNode = () => {
  if (selectedNode.value) {
    selectedNode.value.status = 'running'
    selectedNode.value.progress = 50
  }
}

const pauseNode = () => {
  if (selectedNode.value) {
    selectedNode.value.status = 'processing'
  }
}

const stopNode = () => {
  if (selectedNode.value) {
    selectedNode.value.status = 'waiting'
    selectedNode.value.progress = 0
  }
}

const restartNode = () => {
  if (selectedNode.value) {
    selectedNode.value.status = 'running'
    selectedNode.value.progress = 25
  }
}

const startBacktest = () => {
  isBacktestRunning.value = true
  backtestProgress.value = 0
  
  // 模拟回测进度
  const interval = setInterval(() => {
    backtestProgress.value += 5
    if (backtestProgress.value >= 100) {
      clearInterval(interval)
      isBacktestRunning.value = false
      backtestProgress.value = 100
    }
  }, 500)
}

const pauseBacktest = () => {
  isBacktestRunning.value = false
}

const stopBacktest = () => {
  isBacktestRunning.value = false
  backtestProgress.value = 0
}

const resetBacktest = () => {
  isBacktestRunning.value = false
  backtestProgress.value = 0
  estimatedTimeRemaining.value = '5分钟'
}

// 生命周期
onMounted(() => {
  updateCanvasSize()
  window.addEventListener('resize', updateCanvasSize)
  
  // 启动性能监控
  const performanceInterval = setInterval(() => {
    systemPerformance.cpu = Math.floor(Math.random() * 30) + 50
    systemPerformance.memory = Math.floor(Math.random() * 20) + 70
    systemPerformance.gpu = Math.floor(Math.random() * 40) + 30
  }, 2000)
  
  onUnmounted(() => {
    clearInterval(performanceInterval)
    window.removeEventListener('resize', updateCanvasSize)
  })
})

const updateCanvasSize = () => {
  if (graphContainer.value) {
    canvasWidth.value = graphContainer.value.clientWidth
    canvasHeight.value = graphContainer.value.clientHeight
  }
}
</script>

<style lang="scss" scoped>
.architecture-graph {
  position: relative;
  width: 100%;
  height: 100vh;
  background: #0a0a0f;
  color: #f8fafc;
  overflow: hidden;
}

.graph-container {
  position: relative;
  width: 100%;
  height: 100%;
  perspective: 1000px;
}

.graph-canvas {
  position: relative;
  width: 100%;
  height: 100%;
  transform-style: preserve-3d;
}

.layer {
  position: absolute;
  width: 100%;
  height: 33.33%;
  
  &.background-layer {
    top: 0;
    z-index: 1;
  }
  
  &.middle-layer {
    top: 33.33%;
    z-index: 2;
  }
  
  &.foreground-layer {
    top: 66.66%;
    z-index: 3;
  }
}

.layer-title {
  position: absolute;
  left: 20px;
  top: 10px;
  font-size: 14px;
  font-weight: 600;
  color: #94a3b8;
  background: rgba(37, 99, 235, 0.1);
  padding: 4px 8px;
  border-radius: 4px;
  border-left: 3px solid #2563eb;
}

.nodes-container {
  position: relative;
  width: 100%;
  height: 100%;
}

.node {
  position: absolute;
  width: 120px;
  height: 80px;
  background: #1a1a2e;
  border: 2px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
  
  &:hover {
    transform: translateY(-2px) scale(1.05);
    box-shadow: 0 8px 25px rgba(37, 99, 235, 0.3);
  }
  
  &.data-hub {
    border-color: rgba(0, 255, 136, 0.3);
  }
  
  &.qlib {
    border-color: rgba(255, 170, 0, 0.3);
  }
  
  &.business {
    border-color: rgba(0, 136, 255, 0.3);
  }
  
  .node-icon {
    font-size: 24px;
    margin-bottom: 4px;
  }
  
  .node-title {
    font-size: 10px;
    font-weight: 600;
    text-align: center;
    color: #f8fafc;
    margin-bottom: 6px;
  }
  
  .node-progress {
    width: 80%;
    height: 4px;
    background: rgba(255, 255, 255, 0.1);
    border-radius: 2px;
    overflow: hidden;
    
    .progress-bar {
      height: 100%;
      background: linear-gradient(90deg, #2563eb, #7c3aed);
      transition: width 0.3s ease;
    }
  }
}

.node.status-running {
  animation: pulse 2s infinite;
  border-color: rgba(16, 185, 129, 0.5);
}

.node.status-processing {
  border-color: rgba(245, 158, 11, 0.5);
}

.node.status-error {
  border-color: rgba(239, 68, 68, 0.5);
  animation: flash 1s infinite;
}

.node.status-waiting {
  border-color: rgba(100, 116, 139, 0.3);
  animation: breathe 3s infinite;
}

.node.status-completed {
  border-color: rgba(59, 130, 246, 0.5);
  box-shadow: 0 0 20px rgba(59, 130, 246, 0.3);
}

.connections {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 0;
}

.connection-line {
  stroke-width: 2;
  fill: none;
  opacity: 0.8;
}

.node-details-panel {
  position: absolute;
  width: 320px;
  background: #1a1a2e;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
  z-index: 1000;
  
  .panel-header {
    display: flex;
    align-items: center;
    padding: 12px 16px;
    background: linear-gradient(135deg, rgba(37, 99, 235, 0.15) 0%, rgba(124, 58, 237, 0.1) 100%);
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    
    .panel-icon {
      font-size: 20px;
      margin-right: 8px;
    }
    
    .panel-title {
      font-size: 16px;
      font-weight: 600;
      margin: 0;
      color: #f8fafc;
      flex: 1;
    }
    
    .close-btn {
      background: none;
      border: none;
      color: #94a3b8;
      font-size: 18px;
      cursor: pointer;
      padding: 0;
      width: 24px;
      height: 24px;
      display: flex;
      align-items: center;
      justify-content: center;
      border-radius: 4px;
      
      &:hover {
        background: rgba(239, 68, 68, 0.1);
        color: var(--market-fall);
      }
    }
  }
  
  .panel-content {
    padding: 16px;
    
    .node-info {
      margin-bottom: 16px;
      
      .info-item {
        display: flex;
        align-items: center;
        margin-bottom: 8px;
        
        label {
          font-size: 12px;
          color: #94a3b8;
          width: 60px;
          margin-right: 8px;
        }
        
        .status-badge {
          padding: 2px 6px;
          border-radius: 4px;
          font-size: 10px;
          font-weight: 600;
          
          &.running {
            background: rgba(16, 185, 129, 0.2);
            color: var(--market-rise);
          }
          
          &.processing {
            background: rgba(245, 158, 11, 0.2);
            color: #f59e0b;
          }
          
          &.error {
            background: rgba(239, 68, 68, 0.2);
            color: var(--market-fall);
          }
          
          &.waiting {
            background: rgba(100, 116, 139, 0.2);
            color: #64748b;
          }
          
          &.completed {
            background: rgba(59, 130, 246, 0.2);
            color: #3b82f6;
          }
        }
        
        .progress-info {
          display: flex;
          align-items: center;
          flex: 1;
          
          .progress-bar-small {
            height: 6px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 3px;
            margin-right: 8px;
            flex: 1;
            overflow: hidden;
            
            &::after {
              content: '';
              display: block;
              height: 100%;
              background: linear-gradient(90deg, #2563eb, #7c3aed);
              width: var(--progress, 0%);
              transition: width 0.3s ease;
            }
          }
        }
      }
      
      .node-description {
        font-size: 12px;
        color: #94a3b8;
        line-height: 1.4;
        margin: 8px 0 0 68px 0;
      }
    }
    
    .node-config {
      margin-bottom: 16px;
      
      h4 {
        font-size: 14px;
        color: #f8fafc;
        margin: 0 0 12px 0;
      }
      
      .config-items {
        .config-item {
          display: flex;
          align-items: center;
          margin-bottom: 8px;
          
          label {
            font-size: 12px;
            color: #94a3b8;
            width: 80px;
            margin-right: 8px;
          }
          
          .config-input,
          .config-select {
            flex: 1;
            padding: 6px 8px;
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 4px;
            color: #f8fafc;
            font-size: 12px;
            
            &:focus {
              outline: none;
              border-color: #2563eb;
              box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.2);
            }
          }
        }
      }
    }
    
    .node-actions {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 8px;
      
      .action-btn {
        padding: 8px 12px;
        border: none;
        border-radius: 4px;
        font-size: 12px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
        
        &:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }
        
        &.start-btn {
          background: rgba(16, 185, 129, 0.2);
          color: var(--market-rise);
          
          &:hover:not(:disabled) {
            background: rgba(16, 185, 129, 0.3);
          }
        }
        
        &.pause-btn {
          background: rgba(245, 158, 11, 0.2);
          color: #f59e0b;
          
          &:hover:not(:disabled) {
            background: rgba(245, 158, 11, 0.3);
          }
        }
        
        &.stop-btn {
          background: rgba(239, 68, 68, 0.2);
          color: var(--market-fall);
          
          &:hover:not(:disabled) {
            background: rgba(239, 68, 68, 0.3);
          }
        }
        
        &.restart-btn {
          background: rgba(59, 130, 246, 0.2);
          color: #3b82f6;
          
          &:hover:not(:disabled) {
            background: rgba(59, 130, 246, 0.3);
          }
        }
      }
    }
  }
}

.control-panel {
  position: fixed;
  right: 20px;
  top: 20px;
  width: 280px;
  background: #1a1a2e;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
  z-index: 100;
  
  .panel-header {
    padding: 12px 16px;
    background: linear-gradient(135deg, rgba(37, 99, 235, 0.15) 0%, rgba(124, 58, 237, 0.1) 100%);
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    
    h3 {
      font-size: 16px;
      font-weight: 600;
      margin: 0;
      color: #f8fafc;
    }
  }
  
  .panel-content {
    padding: 16px;
    
    .control-buttons {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 8px;
      margin-bottom: 16px;
      
      .control-btn {
        padding: 10px 12px;
        border: none;
        border-radius: 4px;
        font-size: 12px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
        
        &:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }
        
        &.start-backtest {
          background: rgba(16, 185, 129, 0.2);
          color: var(--market-rise);
          
          &:hover:not(:disabled) {
            background: rgba(16, 185, 129, 0.3);
          }
        }
        
        &.pause-backtest {
          background: rgba(245, 158, 11, 0.2);
          color: #f59e0b;
          
          &:hover:not(:disabled) {
            background: rgba(245, 158, 11, 0.3);
          }
        }
        
        &.stop-backtest {
          background: rgba(239, 68, 68, 0.2);
          color: var(--market-fall);
          
          &:hover:not(:disabled) {
            background: rgba(239, 68, 68, 0.3);
          }
        }
        
        &.reset-backtest {
          background: rgba(59, 130, 246, 0.2);
          color: #3b82f6;
          
          &:hover:not(:disabled) {
            background: rgba(59, 130, 246, 0.3);
          }
        }
      }
    }
    
    .progress-section {
      margin-bottom: 16px;
      
      .progress-item {
        margin-bottom: 8px;
        
        label {
          display: block;
          font-size: 12px;
          color: #94a3b8;
          margin-bottom: 4px;
        }
        
        .progress-bar-container {
          display: flex;
          align-items: center;
          margin-bottom: 4px;
          
          .progress-bar-large {
            height: 8px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 4px;
            flex: 1;
            margin-right: 8px;
            overflow: hidden;
            
            &::after {
              content: '';
              display: block;
              height: 100%;
              background: linear-gradient(90deg, #2563eb, #7c3aed);
              width: var(--progress, 0%);
              transition: width 0.3s ease;
            }
          }
          
          .progress-text-large {
            font-size: 12px;
            color: #2563eb;
            font-weight: 600;
          }
        }
        
        .time-remaining {
          font-size: 12px;
          color: #94a3b8;
        }
      }
    }
    
    .performance-monitor {
      h4 {
        font-size: 14px;
        color: #f8fafc;
        margin: 0 0 12px 0;
      }
      
      .performance-item {
        display: flex;
        align-items: center;
        margin-bottom: 8px;
        
        label {
          font-size: 12px;
          color: #94a3b8;
          width: 40px;
          margin-right: 8px;
        }
        
        .performance-bar {
          flex: 1;
          height: 6px;
          background: rgba(255, 255, 255, 0.1);
          border-radius: 3px;
          margin-right: 8px;
          overflow: hidden;
          position: relative;
          
          .performance-fill {
            height: 100%;
            background: linear-gradient(90deg, #2563eb, #7c3aed);
            transition: width 0.3s ease;
          }
          
          &::after {
            content: attr(data-value);
            position: absolute;
            right: -30px;
            top: -8px;
            font-size: 10px;
            color: #94a3b8;
          }
        }
        
        span {
          font-size: 10px;
          color: #94a3b8;
        }
      }
    }
  }
}

// 动画
@keyframes pulse {
  0%, 100% {
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
  }
  50% {
    box-shadow: 0 4px 12px rgba(16, 185, 129, 0.5);
  }
}

@keyframes breathe {
  0%, 100% {
    opacity: 0.8;
  }
  50% {
    opacity: 1;
  }
}

@keyframes flash {
  0%, 100% {
    border-color: rgba(239, 68, 68, 0.5);
  }
  50% {
    border-color: rgba(239, 68, 68, 1);
  }
}

// 响应式设计
@media (max-width: 1200px) {
  .node-details-panel {
    width: 280px;
  }
  
  .control-panel {
    width: 240px;
  }
}

@media (max-width: 768px) {
  .layer {
    height: 25%;
    
    &.background-layer {
      top: 0;
    }
    
    &.middle-layer {
      top: 25%;
    }
    
    &.foreground-layer {
      top: 50%;
    }
  }
  
  .node {
    width: 100px;
    height: 60px;
    
    .node-icon {
      font-size: 18px;
    }
    
    .node-title {
      font-size: 8px;
    }
  }
  
  .control-panel {
    position: relative;
    right: auto;
    top: auto;
    width: 100%;
    margin-top: 20px;
  }
}
</style>
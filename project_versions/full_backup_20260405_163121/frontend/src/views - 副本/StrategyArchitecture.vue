<template>
  <div class="strategy-architecture-page">
    <!-- 沉浸式背景 -->
    <div class="immersive-background">
      <div class="particle-system" ref="particleSystem"></div>
      <div class="data-stream-overlay"></div>
      <div class="grid-pattern"></div>
    </div>

    <!-- 页面头部 -->
    <header class="page-header">
      <div class="header-content">
        <div class="header-left">
          <h1 class="page-title">策略架构图</h1>
          <p class="page-subtitle">可视化策略生成与分析流程</p>
        </div>
        <div class="header-right">
          <div class="action-buttons">
            <button class="primary-btn" @click="resetView">
              <i class="fas fa-redo"></i>
              <span>重置视图</span>
            </button>
            <button class="secondary-btn" @click="exportArchitecture">
              <i class="fas fa-download"></i>
              <span>导出架构</span>
            </button>
          </div>
        </div>
      </div>
    </header>

    <!-- 主内容区域 -->
    <main class="main-content">
      <!-- 架构图控制面板 -->
      <section class="control-panel">
        <div class="control-group">
          <label>视图模式</label>
          <select v-model="viewMode" @change="changeViewMode">
            <option value="2d">2D 视图</option>
            <option value="3d">2.5D 视图</option>
            <option value="hierarchy">层级视图</option>
          </select>
        </div>
        
        <div class="control-group">
          <label>缩放级别</label>
          <div class="zoom-controls">
            <button @click="zoomOut" :disabled="zoomLevel <= 0.5">
              <i class="fas fa-minus"></i>
            </button>
            <span>{{ Math.round(zoomLevel * 100) }}%</span>
            <button @click="zoomIn" :disabled="zoomLevel >= 2">
              <i class="fas fa-plus"></i>
            </button>
          </div>
        </div>
        
        <div class="control-group">
          <label>数据流动画</label>
          <div class="toggle-switch">
            <input 
              type="checkbox" 
              id="dataFlowToggle" 
              v-model="dataFlowEnabled"
              @change="toggleDataFlow"
            >
            <label for="dataFlowToggle"></label>
          </div>
        </div>
      </section>

      <!-- 架构图工作区 -->
      <section class="architecture-workspace">
        <div class="workspace-container" ref="workspaceContainer">
          <div class="architecture-canvas" ref="architectureCanvas">
            <!-- 策略生成与分析架构节点 -->
            <div 
              v-for="node in strategyNodes" 
              :key="node.id"
              class="architecture-node"
              :class="[
                `node-${node.type}`,
                { 'node-active': node.active },
                { 'node-error': node.error },
                { 'node-selected': selectedNode === node.id }
              ]"
              :style="{
                left: `${node.x}px`,
                top: `${node.y}px`,
                transform: `translate(-50%, -50%) scale(${zoomLevel})`
              }"
              @click="selectNode(node)"
              @dblclick="openNodeDetails(node)"
            >
              <div class="node-icon">
                <i :class="node.icon"></i>
              </div>
              <div class="node-content">
                <h3>{{ node.title }}</h3>
                <p>{{ node.description }}</p>
                <div class="node-status" :class="node.status">
                  <span class="status-dot"></span>
                  <span class="status-text">{{ getStatusText(node.status) }}</span>
                </div>
              </div>
              <div class="node-ports">
                <div 
                  v-for="port in node.ports" 
                  :key="port.id"
                  class="port"
                  :class="port.type"
                  :style="getPortStyle(port)"
                ></div>
              </div>
            </div>

            <!-- 连接线 -->
            <svg class="connections-layer" :width="canvasWidth" :height="canvasHeight">
              <defs>
                <linearGradient id="connectionGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                  <stop offset="0%" style="stop-color:#00ff88;stop-opacity:0.8" />
                  <stop offset="100%" style="stop-color:#0088ff;stop-opacity:0.8" />
                </linearGradient>
              </defs>
              
              <g v-for="connection in connections" :key="connection.id">
                <path
                  :d="getConnectionPath(connection)"
                  stroke="url(#connectionGradient)"
                  stroke-width="2"
                  fill="none"
                  class="connection-line"
                  :class="{ 'connection-active': connection.active }"
                />
                <circle
                  v-if="dataFlowEnabled && connection.active"
                  :r="4"
                  fill="#00ff88"
                  class="data-particle"
                  :style="getDataParticleStyle(connection)"
                />
              </g>
            </svg>
          </div>
        </div>
      </section>

      <!-- 节点详情面板 -->
      <section class="node-details-panel" v-if="selectedNodeData">
        <div class="panel-header">
          <h3>{{ selectedNodeData.title }}</h3>
          <button class="close-btn" @click="closeNodeDetails">
            <i class="fas fa-times"></i>
          </button>
        </div>
        
        <div class="panel-content">
          <div class="detail-section">
            <h4>节点信息</h4>
            <div class="info-grid">
              <div class="info-item">
                <span class="info-label">类型</span>
                <span class="info-value">{{ selectedNodeData.type }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">状态</span>
                <span class="info-value" :class="selectedNodeData.status">
                  {{ getStatusText(selectedNodeData.status) }}
                </span>
              </div>
              <div class="info-item">
                <span class="info-label">处理时间</span>
                <span class="info-value">{{ selectedNodeData.processingTime }}ms</span>
              </div>
              <div class="info-item">
                <span class="info-label">吞吐量</span>
                <span class="info-value">{{ selectedNodeData.throughput }}/s</span>
              </div>
            </div>
          </div>
          
          <div class="detail-section">
            <h4>参数配置</h4>
            <div class="params-list">
              <div 
                v-for="param in selectedNodeData.parameters" 
                :key="param.name"
                class="param-item"
              >
                <label>{{ param.label }}</label>
                <div class="param-control">
                  <input 
                    v-if="param.type === 'number'"
                    type="number" 
                    v-model="param.value"
                    :min="param.min"
                    :max="param.max"
                    @change="updateNodeParameter(selectedNodeData.id, param.name, param.value)"
                  >
                  <select 
                    v-else-if="param.type === 'select'"
                    v-model="param.value"
                    @change="updateNodeParameter(selectedNodeData.id, param.name, param.value)"
                  >
                    <option 
                      v-for="option in param.options" 
                      :key="option.value"
                      :value="option.value"
                    >
                      {{ option.label }}
                    </option>
                  </select>
                  <input 
                    v-else
                    type="text" 
                    v-model="param.value"
                    @change="updateNodeParameter(selectedNodeData.id, param.name, param.value)"
                  >
                </div>
              </div>
            </div>
          </div>
          
          <div class="detail-section">
            <h4>实时指标</h4>
            <div class="metrics-chart">
              <canvas ref="metricsChart" width="300" height="150"></canvas>
            </div>
          </div>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

// 响应式数据
const viewMode = ref('2d')
const zoomLevel = ref(1)
const dataFlowEnabled = ref(true)
const selectedNode = ref(null)
const selectedNodeData = ref(null)
const canvasWidth = ref(1200)
const canvasHeight = ref(800)

// 策略生成与分析架构节点
const strategyNodes = ref([
  {
    id: 'data-input',
    type: 'data',
    title: '数据输入',
    description: '市场数据、历史数据、实时数据',
    icon: 'fas fa-database',
    x: 200,
    y: 200,
    status: 'active',
    active: true,
    error: false,
    processingTime: 12,
    throughput: 1000,
    ports: [
      { id: 'data-input-1', type: 'output', position: 'right', x: 100, y: 50 }
    ],
    parameters: [
      { name: 'dataSource', label: '数据源', type: 'select', value: 'tushare', options: [
        { label: 'Tushare', value: 'tushare' },
        { label: 'Wind', value: 'wind' },
        { label: 'Yahoo', value: 'yahoo' }
      ]},
      { name: 'updateInterval', label: '更新间隔(秒)', type: 'number', value: 60, min: 1, max: 3600 }
    ]
  },
  {
    id: 'feature-engineering',
    type: 'processor',
    title: '特征工程',
    description: '技术指标计算、特征提取、数据预处理',
    icon: 'fas fa-cogs',
    x: 400,
    y: 200,
    status: 'active',
    active: true,
    error: false,
    processingTime: 45,
    throughput: 500,
    ports: [
      { id: 'feature-input-1', type: 'input', position: 'left', x: 0, y: 50 },
      { id: 'feature-output-1', type: 'output', position: 'right', x: 100, y: 50 }
    ],
    parameters: [
      { name: 'indicators', label: '技术指标', type: 'select', value: 'ma,rsi,macd', options: [
        { label: '均线+RSI+MACD', value: 'ma,rsi,macd' },
        { label: '全套指标', value: 'all' },
        { label: '自定义', value: 'custom' }
      ]},
      { name: 'windowSize', label: '窗口大小', type: 'number', value: 20, min: 5, max: 200 }
    ]
  },
  {
    id: 'ai-strategy-generator',
    type: 'ai',
    title: 'AI策略生成器',
    description: '基于机器学习的策略自动生成',
    icon: 'fas fa-robot',
    x: 600,
    y: 200,
    status: 'active',
    active: true,
    error: false,
    processingTime: 120,
    throughput: 50,
    ports: [
      { id: 'ai-input-1', type: 'input', position: 'left', x: 0, y: 50 },
      { id: 'ai-output-1', type: 'output', position: 'right', x: 100, y: 50 }
    ],
    parameters: [
      { name: 'modelType', label: '模型类型', type: 'select', value: 'lstm', options: [
        { label: 'LSTM', value: 'lstm' },
        { label: 'Transformer', value: 'transformer' },
        { label: 'Random Forest', value: 'rf' }
      ]},
      { name: 'trainingEpochs', label: '训练轮数', type: 'number', value: 100, min: 10, max: 1000 },
      { name: 'learningRate', label: '学习率', type: 'number', value: 0.001, min: 0.0001, max: 0.1, step: 0.0001 }
    ]
  },
  {
    id: 'strategy-optimizer',
    type: 'optimizer',
    title: '策略优化器',
    description: '参数优化、策略调优、性能提升',
    icon: 'fas fa-sliders-h',
    x: 800,
    y: 200,
    status: 'active',
    active: true,
    error: false,
    processingTime: 85,
    throughput: 30,
    ports: [
      { id: 'optimizer-input-1', type: 'input', position: 'left', x: 0, y: 50 },
      { id: 'optimizer-output-1', type: 'output', position: 'right', x: 100, y: 50 }
    ],
    parameters: [
      { name: 'optimizationMethod', label: '优化方法', type: 'select', value: 'grid', options: [
        { label: '网格搜索', value: 'grid' },
        { label: '贝叶斯优化', value: 'bayesian' },
        { label: '遗传算法', value: 'genetic' }
      ]},
      { name: 'maxIterations', label: '最大迭代次数', type: 'number', value: 100, min: 10, max: 1000 }
    ]
  },
  {
    id: 'backtest-engine',
    type: 'processor',
    title: '回测引擎',
    description: '历史数据回测、策略验证',
    icon: 'fas fa-chart-line',
    x: 1000,
    y: 200,
    status: 'active',
    active: true,
    error: false,
    processingTime: 200,
    throughput: 20,
    ports: [
      { id: 'backtest-input-1', type: 'input', position: 'left', x: 0, y: 50 },
      { id: 'backtest-output-1', type: 'output', position: 'right', x: 100, y: 50 }
    ],
    parameters: [
      { name: 'startDate', label: '开始日期', type: 'text', value: '2020-01-01' },
      { name: 'endDate', label: '结束日期', type: 'text', value: '2023-12-31' },
      { name: 'initialCapital', label: '初始资金', type: 'number', value: 1000000, min: 10000, max: 100000000 }
    ]
  },
  {
    id: 'performance-analyzer',
    type: 'analyzer',
    title: '性能分析器',
    description: '收益分析、风险评估、绩效归因',
    icon: 'fas fa-analytics',
    x: 600,
    y: 400,
    status: 'active',
    active: true,
    error: false,
    processingTime: 35,
    throughput: 100,
    ports: [
      { id: 'analyzer-input-1', type: 'input', position: 'left', x: 0, y: 50 },
      { id: 'analyzer-input-2', type: 'input', position: 'top', x: 50, y: 0 },
      { id: 'analyzer-output-1', type: 'output', position: 'right', x: 100, y: 50 }
    ],
    parameters: [
      { name: 'riskMetrics', label: '风险指标', type: 'select', value: 'all', options: [
        { label: '全部指标', value: 'all' },
        { label: '基础指标', value: 'basic' },
        { label: '高级指标', value: 'advanced' }
      ]},
      { name: 'benchmark', label: '基准指数', type: 'select', value: '000300', options: [
        { label: '沪深300', value: '000300' },
        { label: '中证500', value: '000905' },
        { label: '创业板指', value: '399006' }
      ]}
    ]
  },
  {
    id: 'strategy-output',
    type: 'output',
    title: '策略输出',
    description: '最终策略、交易信号、绩效报告',
    icon: 'fas fa-file-export',
    x: 1000,
    y: 400,
    status: 'active',
    active: true,
    error: false,
    processingTime: 8,
    throughput: 200,
    ports: [
      { id: 'output-input-1', type: 'input', position: 'left', x: 0, y: 50 },
      { id: 'output-input-2', type: 'input', position: 'top', x: 50, y: 0 }
    ],
    parameters: [
      { name: 'outputFormat', label: '输出格式', type: 'select', value: 'json', options: [
        { label: 'JSON', value: 'json' },
        { label: 'CSV', value: 'csv' },
        { label: 'Excel', value: 'excel' }
      ]},
      { name: 'includeCharts', label: '包含图表', type: 'select', value: 'true', options: [
        { label: '是', value: 'true' },
        { label: '否', value: 'false' }
      ]}
    ]
  }
])

// 连接线配置
const connections = ref([
  {
    id: 'conn-1',
    from: 'data-input',
    to: 'feature-engineering',
    fromPort: 'data-input-1',
    toPort: 'feature-input-1',
    active: true
  },
  {
    id: 'conn-2',
    from: 'feature-engineering',
    to: 'ai-strategy-generator',
    fromPort: 'feature-output-1',
    toPort: 'ai-input-1',
    active: true
  },
  {
    id: 'conn-3',
    from: 'ai-strategy-generator',
    to: 'strategy-optimizer',
    fromPort: 'ai-output-1',
    toPort: 'optimizer-input-1',
    active: true
  },
  {
    id: 'conn-4',
    from: 'strategy-optimizer',
    to: 'backtest-engine',
    fromPort: 'optimizer-output-1',
    toPort: 'backtest-input-1',
    active: true
  },
  {
    id: 'conn-5',
    from: 'backtest-engine',
    to: 'performance-analyzer',
    fromPort: 'backtest-output-1',
    toPort: 'analyzer-input-2',
    active: true
  },
  {
    id: 'conn-6',
    from: 'performance-analyzer',
    to: 'strategy-output',
    fromPort: 'analyzer-output-1',
    toPort: 'output-input-1',
    active: true
  }
])

// 引用
const workspaceContainer = ref(null)
const architectureCanvas = ref(null)
const particleSystem = ref(null)
const metricsChart = ref(null)

// 方法
const getStatusText = (status: string) => {
  const statusMap = {
    active: '运行中',
    inactive: '已停止',
    error: '错误',
    warning: '警告'
  }
  return statusMap[status] || status
}

const getPortStyle = (port: any) => {
  const styles = {
    left: { left: '-8px', top: `${port.y}px` },
    right: { right: '-8px', top: `${port.y}px` },
    top: { top: '-8px', left: `${port.x}px` },
    bottom: { bottom: '-8px', left: `${port.x}px` }
  }
  return styles[port.position] || {}
}

const getConnectionPath = (connection: any) => {
  const fromNode = strategyNodes.value.find(n => n.id === connection.from)
  const toNode = strategyNodes.value.find(n => n.id === connection.to)
  
  if (!fromNode || !toNode) return ''
  
  const fromPort = fromNode.ports.find(p => p.id === connection.fromPort)
  const toPort = toNode.ports.find(p => p.id === connection.toPort)
  
  if (!fromPort || !toPort) return ''
  
  const x1 = fromNode.x + (fromPort.position === 'right' ? 50 : fromPort.position === 'left' ? -50 : fromPort.x - 50)
  const y1 = fromNode.y + (fromPort.position === 'bottom' ? 50 : fromPort.position === 'top' ? -50 : fromPort.y - 50)
  const x2 = toNode.x + (toPort.position === 'right' ? 50 : toPort.position === 'left' ? -50 : toPort.x - 50)
  const y2 = toNode.y + (toPort.position === 'bottom' ? 50 : toPort.position === 'top' ? -50 : toPort.y - 50)
  
  // 创建贝塞尔曲线路径
  const cx1 = x1 + (x2 - x1) * 0.5
  const cy1 = y1
  const cx2 = x1 + (x2 - x1) * 0.5
  const cy2 = y2
  
  return `M ${x1} ${y1} C ${cx1} ${cy1}, ${cx2} ${cy2}, ${x2} ${y2}`
}

const getDataParticleStyle = (connection: any) => {
  // 这里可以实现数据粒子动画
  return {
    animation: `dataFlow ${3 + Math.random() * 2}s linear infinite`
  }
}

const selectNode = (node: any) => {
  selectedNode.value = node.id
  selectedNodeData.value = node
}

const openNodeDetails = (node: any) => {
  selectNode(node)
  // 可以在这里添加更多详情面板的逻辑
}

const closeNodeDetails = () => {
  selectedNode.value = null
  selectedNodeData.value = null
}

const updateNodeParameter = (nodeId: string, paramName: string, value: any) => {
  const node = strategyNodes.value.find(n => n.id === nodeId)
  if (node) {
    const param = node.parameters.find(p => p.name === paramName)
    if (param) {
      param.value = value
      // 这里可以添加参数更新的逻辑
      console.log(`更新节点 ${nodeId} 参数 ${paramName} 为 ${value}`)
    }
  }
}

const changeViewMode = () => {
  // 这里可以实现视图模式切换的逻辑
  console.log('切换视图模式:', viewMode.value)
}

const zoomIn = () => {
  if (zoomLevel.value < 2) {
    zoomLevel.value += 0.1
  }
}

const zoomOut = () => {
  if (zoomLevel.value > 0.5) {
    zoomLevel.value -= 0.1
  }
}

const resetView = () => {
  zoomLevel.value = 1
  selectedNode.value = null
  selectedNodeData.value = null
}

const exportArchitecture = () => {
  // 这里可以实现架构导出功能
  console.log('导出架构图')
}

const toggleDataFlow = () => {
  // 这里可以实现数据流动画开关
  console.log('数据流动画:', dataFlowEnabled.value)
}

// 初始化粒子系统
const initParticleSystem = () => {
  const particleSystemEl = document.querySelector('.particle-system')
  if (!particleSystemEl) return
  
  const canvas = document.createElement('canvas')
  const ctx = canvas.getContext('2d')
  
  if (!ctx) return
  
  canvas.width = window.innerWidth
  canvas.height = window.innerHeight
  canvas.style.position = 'absolute'
  canvas.style.top = '0'
  canvas.style.left = '0'
  canvas.style.pointerEvents = 'none'
  
  particleSystemEl.appendChild(canvas)
  
  // 简单的粒子动画
  const particles: any[] = []
  for (let i = 0; i < 30; i++) {
    particles.push({
      x: Math.random() * canvas.width,
      y: Math.random() * canvas.height,
      vx: (Math.random() - 0.5) * 0.3,
      vy: (Math.random() - 0.5) * 0.3,
      size: Math.random() * 2 + 1,
      opacity: Math.random() * 0.5 + 0.2
    })
  }
  
  const animate = () => {
    ctx.clearRect(0, 0, canvas.width, canvas.height)
    
    particles.forEach(particle => {
      particle.x += particle.vx
      particle.y += particle.vy
      
      if (particle.x < 0 || particle.x > canvas.width) particle.vx = -particle.vx
      if (particle.y < 0 || particle.y > canvas.height) particle.vy = -particle.vy
      
      ctx.beginPath()
      ctx.arc(particle.x, particle.y, particle.size, 0, Math.PI * 2)
      ctx.fillStyle = `rgba(124, 58, 237, ${particle.opacity})`
      ctx.fill()
    })
    
    requestAnimationFrame(animate)
  }
  
  animate()
}

// 生命周期
onMounted(() => {
  initParticleSystem()
  
  // 设置画布大小
  nextTick(() => {
    if (workspaceContainer.value) {
      const rect = workspaceContainer.value.getBoundingClientRect()
      canvasWidth.value = rect.width
      canvasHeight.value = rect.height
    }
  })
})

onUnmounted(() => {
  // 清理资源
})
</script>

<style lang="scss" scoped>
.strategy-architecture-page {
  position: relative;
  min-height: 100vh;
  background: var(--bg-deep);
  color: var(--text-primary);
  font-family: var(--font-family-primary);
  overflow-x: hidden;
}

// 沉浸式背景
.immersive-background {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 0;
  pointer-events: none;
  
  .particle-system {
    position: absolute;
    width: 100%;
    height: 100%;
  }
  
  .data-stream-overlay {
    position: absolute;
    width: 100%;
    height: 100%;
    background: linear-gradient(45deg, 
      transparent 30%, 
      rgba(124, 58, 237, 0.03) 50%, 
      transparent 70%);
    animation: dataFlow 8s linear infinite;
  }
  
  .grid-pattern {
    position: absolute;
    width: 100%;
    height: 100%;
    background-image: 
      linear-gradient(rgba(255, 255, 255, 0.03) 1px, transparent 1px),
      linear-gradient(90deg, rgba(255, 255, 255, 0.03) 1px, transparent 1px);
    background-size: 50px 50px;
  }
}

// 页面头部
.page-header {
  position: relative;
  z-index: 10;
  padding: 24px 40px;
  background: rgba(26, 26, 46, 0.8);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  
  .header-content {
    display: flex;
    align-items: center;
    justify-content: space-between;
    max-width: 1400px;
    margin: 0 auto;
  }
  
  .header-left {
    .page-title {
      margin: 0 0 8px 0;
      font-size: 32px;
      font-weight: 700;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }
    
    .page-subtitle {
      margin: 0;
      color: var(--text-secondary);
      font-size: 16px;
    }
  }
  
  .header-right {
    .action-buttons {
      display: flex;
      gap: 16px;
      
      .primary-btn, .secondary-btn {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 12px 24px;
        border-radius: 8px;
        font-size: 14px;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.3s ease;
        border: none;
      }
      
      .primary-btn {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        
        &:hover {
          transform: translateY(-2px);
          box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);
        }
      }
      
      .secondary-btn {
        background: rgba(255, 255, 255, 0.05);
        color: var(--text-primary);
        border: 1px solid rgba(255, 255, 255, 0.1);
        
        &:hover {
          background: rgba(255, 255, 255, 0.1);
          border-color: rgba(255, 255, 255, 0.2);
        }
      }
    }
  }
}

// 主内容区域
.main-content {
  position: relative;
  z-index: 5;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 20px;
  height: calc(100vh - 100px);
}

// 控制面板
.control-panel {
  display: flex;
  gap: 24px;
  padding: 20px;
  background: rgba(26, 26, 46, 0.6);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  
  .control-group {
    display: flex;
    flex-direction: column;
    gap: 8px;
    
    label {
      font-size: 14px;
      font-weight: 500;
      color: var(--text-secondary);
    }
    
    select {
      padding: 8px 12px;
      background: rgba(255, 255, 255, 0.05);
      border: 1px solid rgba(255, 255, 255, 0.1);
      border-radius: 6px;
      color: var(--text-primary);
      outline: none;
    }
    
    .zoom-controls {
      display: flex;
      align-items: center;
      gap: 12px;
      
      button {
        width: 32px;
        height: 32px;
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 6px;
        color: var(--text-primary);
        cursor: pointer;
        transition: all 0.3s ease;
        
        &:hover:not(:disabled) {
          background: rgba(255, 255, 255, 0.1);
        }
        
        &:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }
      }
      
      span {
        font-size: 14px;
        color: var(--text-primary);
        min-width: 40px;
        text-align: center;
      }
    }
    
    .toggle-switch {
      position: relative;
      width: 48px;
      height: 24px;
      
      input {
        opacity: 0;
        width: 0;
        height: 0;
      }
      
      label {
        position: absolute;
        cursor: pointer;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        transition: 0.3s;
        
        &:before {
          position: absolute;
          content: "";
          height: 18px;
          width: 18px;
          left: 3px;
          bottom: 3px;
          background: white;
          border-radius: 50%;
          transition: 0.3s;
        }
      }
      
      input:checked + label {
        background: var(--secondary);
        
        &:before {
          transform: translateX(24px);
        }
      }
    }
  }
}

// 架构图工作区
.architecture-workspace {
  flex: 1;
  background: rgba(26, 26, 46, 0.6);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  overflow: hidden;
  position: relative;
  
  .workspace-container {
    width: 100%;
    height: 100%;
    position: relative;
  }
  
  .architecture-canvas {
    width: 100%;
    height: 100%;
    position: relative;
    overflow: auto;
  }
  
  .connections-layer {
    position: absolute;
    top: 0;
    left: 0;
    pointer-events: none;
    z-index: 1;
    
    .connection-line {
      stroke-dasharray: 5, 5;
      animation: connectionPulse 2s linear infinite;
      
      &.connection-active {
        stroke-dasharray: none;
        stroke-width: 3;
      }
    }
    
    .data-particle {
      animation: dataFlowParticle 3s linear infinite;
    }
  }
  
  .architecture-node {
    position: absolute;
    width: 200px;
    background: rgba(26, 26, 46, 0.9);
    backdrop-filter: blur(10px);
    border: 2px solid rgba(255, 255, 255, 0.1);
    border-radius: 12px;
    padding: 16px;
    cursor: pointer;
    transition: all 0.3s ease;
    z-index: 2;
    
    &:hover {
      transform: translate(-50%, -50%) scale(1.05);
      border-color: var(--secondary);
      box-shadow: 0 8px 32px rgba(124, 58, 237, 0.3);
    }
    
    &.node-selected {
      border-color: var(--primary);
      box-shadow: 0 0 20px rgba(37, 99, 235, 0.5);
    }
    
    &.node-active {
      border-color: var(--market-rise);
      
      .node-status .status-dot {
        background: var(--market-rise);
        animation: pulse 2s infinite;
      }
    }
    
    &.node-error {
      border-color: var(--market-fall);
      
      .node-status .status-dot {
        background: var(--market-fall);
      }
    }
    
    .node-icon {
      width: 48px;
      height: 48px;
      display: flex;
      align-items: center;
      justify-content: center;
      background: rgba(124, 58, 237, 0.1);
      border-radius: 12px;
      color: var(--secondary);
      font-size: 20px;
      margin: 0 auto 12px;
    }
    
    .node-content {
      text-align: center;
      
      h3 {
        margin: 0 0 8px 0;
        font-size: 16px;
        font-weight: 600;
        color: var(--text-primary);
      }
      
      p {
        margin: 0 0 12px 0;
        font-size: 12px;
        color: var(--text-secondary);
        line-height: 1.4;
      }
      
      .node-status {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 6px;
        
        .status-dot {
          width: 8px;
          height: 8px;
          border-radius: 50%;
          background: #6b7280;
        }
        
        .status-text {
          font-size: 12px;
          color: var(--text-secondary);
        }
      }
    }
    
    .node-ports {
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      pointer-events: none;
      
      .port {
        position: absolute;
        width: 16px;
        height: 16px;
        border-radius: 50%;
        pointer-events: auto;
        
        &.input {
          background: #0088ff;
        }
        
        &.output {
          background: #00ff88;
        }
      }
    }
    
    // 节点类型样式
    &.node-data {
      .node-icon {
        background: rgba(0, 136, 255, 0.1);
        color: #0088ff;
      }
    }
    
    &.node-processor {
      .node-icon {
        background: rgba(255, 170, 0, 0.1);
        color: #ffaa00;
      }
    }
    
    &.node-ai {
      .node-icon {
        background: rgba(124, 58, 237, 0.1);
        color: var(--secondary);
      }
    }
    
    &.node-optimizer {
      .node-icon {
        background: rgba(16, 185, 129, 0.1);
        color: var(--market-rise);
      }
    }
    
    &.node-analyzer {
      .node-icon {
        background: rgba(245, 158, 11, 0.1);
        color: #f59e0b;
      }
    }
    
    &.node-output {
      .node-icon {
        background: rgba(239, 68, 68, 0.1);
        color: var(--market-fall);
      }
    }
  }
}

// 节点详情面板
.node-details-panel {
  position: absolute;
  right: 20px;
  top: 20px;
  width: 400px;
  max-height: calc(100vh - 140px);
  background: rgba(26, 26, 46, 0.95);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  overflow: hidden;
  z-index: 10;
  
  .panel-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 20px;
    background: rgba(255, 255, 255, 0.05);
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    
    h3 {
      margin: 0;
      font-size: 18px;
      font-weight: 600;
      color: var(--text-primary);
    }
    
    .close-btn {
      width: 32px;
      height: 32px;
      background: rgba(255, 255, 255, 0.05);
      border: 1px solid rgba(255, 255, 255, 0.1);
      border-radius: 6px;
      color: var(--text-secondary);
      cursor: pointer;
      transition: all 0.3s ease;
      
      &:hover {
        background: rgba(255, 255, 255, 0.1);
        color: var(--text-primary);
      }
    }
  }
  
  .panel-content {
    padding: 20px;
    max-height: calc(100vh - 240px);
    overflow-y: auto;
    
    .detail-section {
      margin-bottom: 24px;
      
      h4 {
        margin: 0 0 16px 0;
        font-size: 16px;
        font-weight: 600;
        color: var(--text-primary);
      }
      
      .info-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 12px;
        
        .info-item {
          display: flex;
          flex-direction: column;
          gap: 4px;
          
          .info-label {
            font-size: 12px;
            color: var(--text-secondary);
          }
          
          .info-value {
            font-size: 14px;
            font-weight: 500;
            color: var(--text-primary);
            
            &.active {
              color: var(--market-rise);
            }
            
            &.error {
              color: var(--market-fall);
            }
          }
        }
      }
      
      .params-list {
        display: flex;
        flex-direction: column;
        gap: 12px;
        
        .param-item {
          display: flex;
          flex-direction: column;
          gap: 6px;
          
          label {
            font-size: 12px;
            color: var(--text-secondary);
          }
          
          .param-control {
            input, select {
              width: 100%;
              padding: 8px 12px;
              background: rgba(255, 255, 255, 0.05);
              border: 1px solid rgba(255, 255, 255, 0.1);
              border-radius: 6px;
              color: var(--text-primary);
              font-size: 14px;
              
              &:focus {
                outline: none;
                border-color: var(--secondary);
              }
            }
          }
        }
      }
      
      .metrics-chart {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 8px;
        padding: 16px;
        text-align: center;
        
        canvas {
          max-width: 100%;
          height: auto;
        }
      }
    }
  }
}

// 动画
@keyframes dataFlow {
  0% {
    transform: translateX(-100%);
  }
  100% {
    transform: translateX(100%);
  }
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

@keyframes connectionPulse {
  0% {
    stroke-dashoffset: 0;
  }
  100% {
    stroke-dashoffset: 10;
  }
}

@keyframes dataFlowParticle {
  0% {
    offset-distance: 0%;
  }
  100% {
    offset-distance: 100%;
  }
}

// 响应式设计
@media (max-width: 1024px) {
  .control-panel {
    flex-wrap: wrap;
    gap: 16px;
  }
  
  .node-details-panel {
    width: 350px;
  }
}

@media (max-width: 768px) {
  .page-header {
    padding: 16px 20px;
    
    .header-content {
      flex-direction: column;
      gap: 16px;
      text-align: center;
    }
  }
  
  .main-content {
    padding: 16px;
  }
  
  .control-panel {
    flex-direction: column;
    gap: 16px;
  }
  
  .node-details-panel {
    position: fixed;
    right: 10px;
    left: 10px;
    top: auto;
    bottom: 10px;
    width: auto;
    max-height: 50vh;
  }
  
  .architecture-node {
    width: 160px;
    padding: 12px;
    
    .node-icon {
      width: 40px;
      height: 40px;
      font-size: 16px;
    }
    
    .node-content {
      h3 {
        font-size: 14px;
      }
      
      p {
        font-size: 11px;
      }
    }
  }
}

  /* 统一滑杆样式覆盖 */
  .parameter-range {
    /* 使用全局滑杆样式 */
    -webkit-appearance: none;
    appearance: none;
    width: 100%;
    height: 6px;
    background: var(--border-color);
    border-radius: 3px;
    outline: none;
    transition: all 0.3s ease;
    border: none;
    padding: 0;
  }

  .parameter-range::-webkit-slider-thumb {
    -webkit-appearance: none;
    appearance: none;
    width: 20px;
    height: 20px;
    background: var(--bg-white);
    border: 3px solid var(--primary-color);
    border-radius: 50%;
    cursor: grab;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
    transition: all 0.3s ease;
  }

  .parameter-range::-webkit-slider-thumb:hover {
    transform: scale(1.2);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
  }

  .parameter-range::-webkit-slider-thumb:active {
    cursor: grabbing;
    transform: scale(1.1);
  }

  .parameter-range::-moz-range-thumb {
    width: 20px;
    height: 20px;
    background: var(--bg-white);
    border: 3px solid var(--primary-color);
    border-radius: 50%;
    cursor: grab;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
    transition: all 0.3s ease;
    border: none;
  }

  .parameter-range::-moz-range-thumb:hover {
    transform: scale(1.2);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
  }

  .parameter-range::-moz-range-thumb:active {
    cursor: grabbing;
    transform: scale(1.1);
  }

  .parameter-range::-webkit-slider-runnable-track {
    height: 100%;
    border-radius: 3px;
  }

  .parameter-range::-moz-range-track {
    height: 100%;
    border-radius: 3px;
  }

  .range-input-group {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 4px 0;
  }

  .range-value {
    min-width: 60px;
    padding: 4px 8px;
    background: var(--bg-secondary);
    border: 1px solid var(--border-color);
    border-radius: var(--border-radius-sm);
    font-size: var(--font-size-sm);
    font-weight: 600;
    color: var(--primary-color);
    text-align: center;
    transition: all 0.3s ease;
  }

  /* 参数配置滑杆样式增强 */
  .parameter-slider {
    display: flex;
    align-items: center;
    gap: 16px;
    padding: 12px;
    background: var(--bg-secondary);
    border-radius: var(--border-radius);
    transition: all 0.3s ease;
  }

  .parameter-slider:hover {
    background: var(--bg-hover);
  }

  .parameter-slider .parameter-info {
    flex: 1;
  }

  .parameter-slider .parameter-name {
    font-size: var(--font-size-sm);
    font-weight: 500;
    color: var(--text-primary);
    margin-bottom: 4px;
  }

  .parameter-slider .parameter-desc {
    font-size: var(--font-size-xs);
    color: var(--text-regular);
  }

  .parameter-slider .parameter-control {
    flex: 2;
    display: flex;
    align-items: center;
    gap: 12px;
  }

</style>
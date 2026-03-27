<template>
  <div class="architecture-layer">
    <!-- 沉浸式背景 -->
    <div class="immersive-background">
      <div class="particle-network" ref="particleNetwork"></div>
      <div class="data-flow-canvas" ref="dataFlowCanvas"></div>
      <div class="grid-mesh" ref="gridMesh"></div>
    </div>

    <!-- 主界面容器 -->
    <div class="main-interface">
      <!-- 顶部控制栏 -->
      <div class="top-control-bar">
        <div class="control-left">
          <div class="function-info">
            <div class="function-icon">
              <n-icon size="28" :component="getFunctionIcon(currentFunction?.icon)" />
            </div>
            <div class="function-details">
              <h2>{{ currentFunction?.name }}</h2>
              <p>{{ currentFunction?.description }}</p>
            </div>
          </div>
        </div>
        
        <div class="control-center">
          <div class="view-controls">
            <n-button-group>
              <n-button
                v-for="view in viewModes"
                :key="view.id"
                :type="currentView === view.id ? 'primary' : 'default'"
                @click="switchView(view.id)"
              >
                <n-icon size="16" :component="view.icon" />
                {{ view.name }}
              </n-button>
            </n-button-group>
          </div>
          
          <div class="interaction-controls">
            <n-button
              :type="isInteractionMode ? 'primary' : 'default'"
              @click="toggleInteractionMode"
            >
              <n-icon size="16" :component="CursorIcon" />
              {{ isInteractionMode ? '交互模式' : '观察模式' }}
            </n-button>
            
            <n-button
              :type="isDataFlowVisible ? 'primary' : 'default'"
              @click="toggleDataFlow"
            >
              <n-icon size="16" :component="FlashIcon" />
              数据流
            </n-button>
          </div>
        </div>
        
        <div class="control-right">
          <div class="layer-navigation">
            <LayerNavigation />
          </div>
        </div>
      </div>

      <!-- 架构图展示区 -->
      <div class="architecture-display" ref="architectureDisplay">
        <!-- 2D网络视图 -->
        <div v-if="currentView === '2d'" class="network-view">
          <div class="network-container" ref="networkContainer">
            <div
              v-for="node in networkNodes"
              :key="node.id"
              :class="['network-node', { active: selectedNode === node.id, highlighted: highlightedNode === node.id }]"
              :style="getNodeStyle(node)"
              @click="selectNode(node)"
              @mouseenter="highlightNode(node)"
              @mouseleave="unhighlightNode(node)"
              @mousedown="startNodeDrag(node, $event)"
            >
              <!-- 节点光环 -->
              <div class="node-aura" :class="{ active: selectedNode === node.id }"></div>
              
              <!-- 节点内容 -->
              <div class="node-content">
                <div class="node-icon">
                  <n-icon size="24" :component="getNodeIcon(node.type)" />
                  <div class="node-status" :class="node.status"></div>
                </div>
                
                <div class="node-info">
                  <h4>{{ node.name }}</h4>
                  <p>{{ node.description }}</p>
                </div>
              </div>
              
              <!-- 节点连接点 -->
              <div
                v-for="port in node.ports"
                :key="port.id"
                class="connection-port"
                :class="port.type"
                :style="getPortStyle(port)"
              ></div>
            </div>
            
            <!-- 连接线 -->
            <svg class="connections-svg" ref="connectionsSvg">
              <defs>
                <linearGradient id="dataFlowGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                  <stop offset="0%" style="stop-color:#8b5cf6;stop-opacity:0.8" />
                  <stop offset="50%" style="stop-color:#2563eb;stop-opacity:0.6" />
                  <stop offset="100%" style="stop-color:#10b981;stop-opacity:0.8" />
                </linearGradient>
                
                <filter id="glow">
                  <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
                  <feMerge in="coloredBlur" in2="SourceGraphic"/>
                </filter>
              </defs>
              
              <path
                v-for="connection in networkConnections"
                :key="`${connection.from}-${connection.to}`"
                :d="getConnectionPath(connection)"
                class="connection-path"
                :class="{ active: isConnectionActive(connection) }"
                fill="none"
                stroke="url(#dataFlowGradient)"
                stroke-width="2"
                filter="url(#glow)"
              />
              
              <!-- 数据流动画粒子 -->
              <circle
                v-for="particle in dataFlowParticles"
                :key="particle.id"
                :cx="particle.x"
                :cy="particle.y"
                r="3"
                class="data-particle"
                fill="#8b5cf6"
                filter="url(#glow)"
              />
            </svg>
          </div>
        </div>

        <!-- 3D视图 -->
        <div v-else-if="currentView === '3d'" class="three-d-view">
          <div class="three-d-container" ref="threeDContainer">
            <div class="three-d-placeholder">
              <n-icon size="64" :component="CubeIcon" />
              <p>3D架构图开发中...</p>
              <p class="placeholder-desc">将支持立体节点展示、旋转视角、深度交互</p>
            </div>
          </div>
        </div>

        <!-- 层级视图 -->
        <div v-else-if="currentView === 'layers'" class="layers-view">
          <div class="layers-container" ref="layersContainer">
            <div
              v-for="layer in architectureLayers"
              :key="layer.id"
              :class="['architecture-layer-card', { active: selectedLayer === layer.id }]"
              @click="selectLayer(layer)"
            >
              <div class="layer-header">
                <div class="layer-icon">
                  <n-icon size="32" :component="getLayerIcon(layer.type)" />
                </div>
                <div class="layer-level">
                  <span class="level-badge">{{ layer.level }}</span>
                </div>
              </div>
              
              <div class="layer-content">
                <h3>{{ layer.name }}</h3>
                <p>{{ layer.description }}</p>
                
                <div class="layer-components">
                  <div
                    v-for="component in layer.components"
                    :key="component.id"
                    class="component-item"
                  >
                    <n-icon size="16" :component="getComponentIcon(component.type)" />
                    <span>{{ component.name }}</span>
                  </div>
                </div>
              </div>
              
              <div class="layer-metrics">
                <div class="metric-item">
                  <span class="metric-label">性能</span>
                  <div class="metric-bar">
                    <div class="metric-fill" :style="{ width: `${layer.performance}%` }"></div>
                  </div>
                  <span class="metric-value">{{ layer.performance }}%</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 底部信息栏 -->
      <div class="bottom-info-bar">
        <div class="info-left">
          <div class="node-count">
            <span>{{ networkNodes.length }} 个节点</span>
            <span>{{ networkConnections.length }} 条连接</span>
          </div>
          
          <div class="performance-indicator">
            <span class="indicator-label">系统性能</span>
            <div class="indicator-bar">
              <div class="indicator-fill" :style="{ width: `${systemPerformance}%` }"></div>
            </div>
            <span class="indicator-value">{{ systemPerformance }}%</span>
          </div>
        </div>
        
        <div class="info-center">
          <div class="zoom-controls">
            <n-button size="small" @click="zoomIn">
              <n-icon :component="ZoomInIcon" />
            </n-button>
            <n-button size="small" @click="zoomOut">
              <n-icon :component="ZoomOutIcon" />
            </n-button>
            <n-button size="small" @click="resetZoom">
              <n-icon :component="ExpandIcon" />
            </n-button>
          </div>
        </div>
        
        <div class="info-right">
          <div class="real-time-status">
            <div class="status-item">
              <div class="status-dot online"></div>
              <span>实时同步</span>
            </div>
            <div class="status-item">
              <span>{{ currentTime }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 节点详情面板 -->
    <div v-if="selectedNodeData" class="node-detail-panel" @click.stop>
      <div class="panel-header">
        <h3>{{ selectedNodeData.name }}</h3>
        <n-button circle size="small" text @click="closeNodeDetail">
          <n-icon :component="CloseIcon" />
        </n-button>
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
              <span class="info-value">{{ selectedNodeData.status }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">负载</span>
              <span class="info-value">{{ selectedNodeData.load }}%</span>
            </div>
          </div>
        </div>
        
        <div class="detail-section">
          <h4>实时指标</h4>
          <div class="metrics-chart">
            <div ref="nodeMetricsChart" class="mini-chart"></div>
          </div>
        </div>
        
        <div class="detail-section">
          <h4>操作</h4>
          <div class="action-buttons">
            <n-button type="primary" size="small" @click="configureNode">
              配置
            </n-button>
            <n-button size="small" @click="restartNode">
              重启
            </n-button>
            <n-button type="error" size="small" @click="stopNode">
              停止
            </n-button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAppStore } from '@/stores'
import { functionModules, getLayerConfig } from '@/configs/functionConfig'
import LayerNavigation from '@/components/navigation/LayerNavigation.vue'
import {
  CubeOutline as CubeIcon,
  GridOutline as GridIcon,
  LayersOutline as LayersIcon,
  AnalyticsOutline as AnalyticsIcon,
  ServerOutline as ServerIcon,
  CodeSlashOutline as CodeSlashIcon,
  ServerOutline as DatabaseIcon,
  FlaskOutline as ExperimentIcon,
  AccessibilityOutline as RobotIcon,
  TrendingUpOutline as TradingIcon,
  DesktopOutline as MonitorIcon,
  BarChartOutline as ChartIcon,
  SearchOutline as SearchIcon,
  FlashOutline as FlashIcon,
  PencilOutline as CursorIcon,
  AddCircleOutline as ZoomInIcon,
  RemoveCircleOutline as ZoomOutIcon,
  ExpandOutline as ExpandIcon,
  CloseOutline as CloseIcon
} from '@vicons/ionicons5'

// 状态管理
const route = useRoute()
const router = useRouter()
const appStore = useAppStore()

// 响应式数据
const currentView = ref('2d')
const selectedNode = ref<string | null>(null)
const highlightedNode = ref<string | null>(null)
const selectedLayer = ref<string | null>(null)
const selectedNodeData = ref<any>(null)
const isInteractionMode = ref(true)
const isDataFlowVisible = ref(true)
const systemPerformance = ref(87)
const currentTime = ref('')

// DOM引用
const particleNetwork = ref<HTMLElement>()
const dataFlowCanvas = ref<HTMLElement>()
const gridMesh = ref<HTMLElement>()
const architectureDisplay = ref<HTMLElement>()
const networkContainer = ref<HTMLElement>()
const threeDContainer = ref<HTMLElement>()
const layersContainer = ref<HTMLElement>()
const connectionsSvg = ref<SVGElement>()
const nodeMetricsChart = ref<HTMLElement>()

// 视图模式
const viewModes = [
  { id: '2d', name: '2D网络', icon: GridIcon },
  { id: '3d', name: '3D视图', icon: CubeIcon },
  { id: 'layers', name: '层级视图', icon: LayersIcon }
]

// 当前功能模块
const currentFunction = computed(() => {
  const functionId = route.params.functionId as string
  return functionModules.find(module => module.id === functionId)
})

// 模拟网络节点数据
const networkNodes = ref([
  {
    id: 'data-source',
    name: '数据源',
    type: 'database',
    description: '实时数据获取与预处理',
    status: 'online',
    load: 65,
    x: 200,
    y: 150,
    ports: [
      { id: 'output-1', type: 'output', angle: 45 },
      { id: 'output-2', type: 'output', angle: 135 }
    ]
  },
  {
    id: 'data-processor',
    name: '数据处理器',
    type: 'server',
    description: '数据清洗与特征提取',
    status: 'online',
    load: 78,
    x: 500,
    y: 150,
    ports: [
      { id: 'input-1', type: 'input', angle: 225 },
      { id: 'input-2', type: 'input', angle: 315 },
      { id: 'output-1', type: 'output', angle: 45 },
      { id: 'output-2', type: 'output', angle: 135 }
    ]
  },
  {
    id: 'ai-model',
    name: 'AI模型',
    type: 'robot',
    description: '机器学习预测模型',
    status: 'online',
    load: 82,
    x: 800,
    y: 150,
    ports: [
      { id: 'input-1', type: 'input', angle: 225 },
      { id: 'input-2', type: 'input', angle: 315 },
      { id: 'output-1', type: 'output', angle: 45 }
    ]
  },
  {
    id: 'strategy-engine',
    name: '策略引擎',
    type: 'code',
    description: '策略执行与风险控制',
    status: 'online',
    load: 71,
    x: 350,
    y: 300,
    ports: [
      { id: 'input-1', type: 'input', angle: 225 },
      { id: 'output-1', type: 'output', angle: 45 },
      { id: 'output-2', type: 'output', angle: 135 }
    ]
  },
  {
    id: 'trading-system',
    name: '交易系统',
    type: 'trading',
    description: '订单执行与市场接口',
    status: 'online',
    load: 58,
    x: 650,
    y: 300,
    ports: [
      { id: 'input-1', type: 'input', angle: 225 },
      { id: 'input-2', type: 'input', angle: 315 }
    ]
  }
])

// 网络连接数据
const networkConnections = ref([
  { from: 'data-source', to: 'data-processor', fromPort: 'output-1', toPort: 'input-1' },
  { from: 'data-source', to: 'data-processor', fromPort: 'output-2', toPort: 'input-2' },
  { from: 'data-processor', to: 'ai-model', fromPort: 'output-1', toPort: 'input-1' },
  { from: 'data-processor', to: 'strategy-engine', fromPort: 'output-2', toPort: 'input-1' },
  { from: 'ai-model', to: 'strategy-engine', fromPort: 'output-1', toPort: 'input-2' },
  { from: 'strategy-engine', to: 'trading-system', fromPort: 'output-1', toPort: 'input-1' },
  { from: 'strategy-engine', to: 'trading-system', fromPort: 'output-2', toPort: 'input-2' }
])

// 数据流粒子
const dataFlowParticles = ref<Array<any>>([])

// 架构层级数据
const architectureLayers = ref([
  {
    id: 'data-layer',
    name: '数据层',
    description: '数据获取、存储、预处理',
    type: 'database',
    level: 'L1',
    performance: 92,
    components: [
      { id: 'data-source', name: '数据源', type: 'database' },
      { id: 'data-storage', name: '数据存储', type: 'server' },
      { id: 'data-processor', name: '数据处理器', type: 'server' }
    ]
  },
  {
    id: 'model-layer',
    name: '模型层',
    description: '机器学习模型训练与推理',
    type: 'robot',
    level: 'L2',
    performance: 87,
    components: [
      { id: 'ai-model', name: 'AI模型', type: 'robot' },
      { id: 'model-trainer', name: '模型训练器', type: 'code' },
      { id: 'model-validator', name: '模型验证器', type: 'analytics' }
    ]
  },
  {
    id: 'strategy-layer',
    name: '策略层',
    description: '策略生成、执行、优化',
    type: 'code',
    level: 'L3',
    performance: 78,
    components: [
      { id: 'strategy-engine', name: '策略引擎', type: 'code' },
      { id: 'risk-manager', name: '风险管理', type: 'analytics' },
      { id: 'portfolio-optimizer', name: '组合优化器', type: 'chart' }
    ]
  }
])

// 方法
const getFunctionIcon = (iconName: string) => {
  const iconMap: Record<string, any> = {
    'database': DatabaseIcon,
    'experiment': ExperimentIcon,
    'robot': RobotIcon,
    'trading': TradingIcon,
    'monitor': MonitorIcon,
    'chart': ChartIcon
  }
  return iconMap[iconName] || GridIcon
}

const getNodeIcon = (nodeType: string) => {
  const iconMap: Record<string, any> = {
    'database': DatabaseIcon,
    'server': ServerIcon,
    'robot': RobotIcon,
    'code': CodeSlashIcon,
    'trading': TradingIcon,
    'monitor': MonitorIcon,
    'chart': ChartIcon
  }
  return iconMap[nodeType] || AnalyticsIcon
}

const getLayerIcon = (layerType: string) => {
  const iconMap: Record<string, any> = {
    'database': DatabaseIcon,
    'robot': RobotIcon,
    'code': CodeSlashIcon
  }
  return iconMap[layerType] || AnalyticsIcon
}

const getComponentIcon = (componentType: string) => {
  const iconMap: Record<string, any> = {
    'database': DatabaseIcon,
    'server': ServerIcon,
    'robot': RobotIcon,
    'code': CodeSlashIcon,
    'analytics': AnalyticsIcon,
    'chart': ChartIcon
  }
  return iconMap[componentType] || ServerIcon
}

const getNodeStyle = (node: any) => {
  return {
    left: `${node.x}px`,
    top: `${node.y}px`
  }
}

const getPortStyle = (port: any) => {
  const angle = port.angle - 90
  const distance = 25
  const x = Math.cos(angle * Math.PI / 180) * distance
  const y = Math.sin(angle * Math.PI / 180) * distance
  
  return {
    left: `${50 + x}px`,
    top: `${50 + y}px`
  }
}

const getConnectionPath = (connection: any) => {
  const fromNode = networkNodes.value.find(n => n.id === connection.from)
  const toNode = networkNodes.value.find(n => n.id === connection.to)
  
  if (!fromNode || !toNode) return ''
  
  const fromPort = fromNode.ports.find((p: any) => p.id === connection.fromPort)
  const toPort = toNode.ports.find((p: any) => p.id === connection.toPort)
  
  if (!fromPort || !toPort) return ''
  
  const fromAngle = fromPort.angle - 90
  const toAngle = toPort.angle - 90
  
  const fromDistance = 25
  const toDistance = 25
  
  const fromX = fromNode.x + 50 + Math.cos(fromAngle * Math.PI / 180) * fromDistance
  const fromY = fromNode.y + 50 + Math.sin(fromAngle * Math.PI / 180) * fromDistance
  
  const toX = toNode.x + 50 + Math.cos(toAngle * Math.PI / 180) * toDistance
  const toY = toNode.y + 50 + Math.sin(toAngle * Math.PI / 180) * toDistance
  
  return `M ${fromX} ${fromY} C ${(fromX + toX) / 2} ${(fromY + toY) / 2} ${toX} ${toY}`
}

const isConnectionActive = (connection: any) => {
  const fromNode = networkNodes.value.find(n => n.id === connection.from)
  const toNode = networkNodes.value.find(n => n.id === connection.to)
  return fromNode?.status === 'online' && toNode?.status === 'online'
}

const switchView = (viewId: string) => {
  currentView.value = viewId
}

const toggleInteractionMode = () => {
  isInteractionMode.value = !isInteractionMode.value
}

const toggleDataFlow = () => {
  isDataFlowVisible.value = !isDataFlowVisible.value
}

const selectNode = (node: any) => {
  if (!isInteractionMode.value) return
  selectedNode.value = node.id
  selectedNodeData.value = node
}

const highlightNode = (node: any) => {
  highlightedNode.value = node.id
}

const unhighlightNode = (node: any) => {
  if (highlightedNode.value === node.id) {
    highlightedNode.value = null
  }
}

const selectLayer = (layer: any) => {
  selectedLayer.value = layer.id
}

const closeNodeDetail = () => {
  selectedNode.value = null
  selectedNodeData.value = null
}

const configureNode = () => {
  console.log('Configure node:', selectedNodeData.value)
}

const restartNode = () => {
  console.log('Restart node:', selectedNodeData.value)
}

const stopNode = () => {
  console.log('Stop node:', selectedNodeData.value)
}

const zoomIn = () => {
  // 实现放大功能
  console.log('Zoom in')
}

const zoomOut = () => {
  // 实现缩小功能
  console.log('Zoom out')
}

const resetZoom = () => {
  // 实现重置缩放
  console.log('Reset zoom')
}

// 初始化数据流粒子动画
const initDataFlowParticles = () => {
  if (!isDataFlowVisible.value) return
  
  const particles: any[] = []
  
  networkConnections.value.forEach((connection, index) => {
    const fromNode = networkNodes.value.find(n => n.id === connection.from)
    const toNode = networkNodes.value.find(n => n.id === connection.to)
    
    if (fromNode?.status === 'online' && toNode?.status === 'online') {
      particles.push({
        id: `particle-${index}`,
        connection: connection,
        progress: Math.random(),
        speed: 0.5 + Math.random() * 1.5
      })
    }
  })
  
  dataFlowParticles.value = particles
}

// 更新粒子位置
const updateParticles = () => {
  if (!isDataFlowVisible.value) return
  
  dataFlowParticles.value.forEach(particle => {
    particle.progress += particle.speed * 0.01
    
    if (particle.progress > 1) {
      particle.progress = 0
    }
    
    const connection = particle.connection
    const fromNode = networkNodes.value.find(n => n.id === connection.from)
    const toNode = networkNodes.value.find(n => n.id === connection.to)
    
    if (fromNode && toNode) {
      const fromPort = fromNode.ports.find((p: any) => p.id === connection.fromPort)
      const toPort = toNode.ports.find((p: any) => p.id === connection.toPort)
      
      if (fromPort && toPort) {
        const fromAngle = fromPort.angle - 90
        const toAngle = toPort.angle - 90
        
        const fromDistance = 25
        const toDistance = 25
        
        const fromX = fromNode.x + 50 + Math.cos(fromAngle * Math.PI / 180) * fromDistance
        const fromY = fromNode.y + 50 + Math.sin(fromAngle * Math.PI / 180) * fromDistance
        
        const toX = toNode.x + 50 + Math.cos(toAngle * Math.PI / 180) * toDistance
        const toY = toNode.y + 50 + Math.sin(toAngle * Math.PI / 180) * toDistance
        
        particle.x = fromX + (toX - fromX) * particle.progress
        particle.y = fromY + (toY - fromY) * particle.progress
      }
    }
  })
}

// 粒子网络背景
const initParticleNetwork = () => {
  if (!particleNetwork.value) return
  
  const canvas = document.createElement('canvas')
  const ctx = canvas.getContext('2d')
  if (!ctx) return
  
  canvas.width = window.innerWidth
  canvas.height = window.innerHeight
  particleNetwork.value.appendChild(canvas)
  
  const particles: any[] = []
  const particleCount = 60
  
  for (let i = 0; i < particleCount; i++) {
    particles.push({
      x: Math.random() * canvas.width,
      y: Math.random() * canvas.height,
      vx: (Math.random() - 0.5) * 0.2,
      vy: (Math.random() - 0.5) * 0.2,
      size: Math.random() * 1 + 0.5,
      opacity: Math.random() * 0.3 + 0.1
    })
  }
  
  const animate = () => {
    ctx.clearRect(0, 0, canvas.width, canvas.height)
    
    particles.forEach(particle => {
      particle.x += particle.vx
      particle.y += particle.vy
      
      if (particle.x < 0 || particle.x > canvas.width) particle.vx *= -1
      if (particle.y < 0 || particle.y > canvas.height) particle.vy *= -1
      
      ctx.beginPath()
      ctx.arc(particle.x, particle.y, particle.size, 0, Math.PI * 2)
      ctx.fillStyle = `rgba(139, 92, 246, ${particle.opacity})`
      ctx.fill()
    })
    
    // 连接临近粒子
    particles.forEach((p1, i) => {
      particles.slice(i + 1).forEach(p2 => {
        const distance = Math.sqrt((p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2)
        if (distance < 80) {
          ctx.beginPath()
          ctx.moveTo(p1.x, p1.y)
          ctx.lineTo(p2.x, p2.y)
          ctx.strokeStyle = `rgba(139, 92, 246, ${0.05 * (1 - distance / 80)})`
          ctx.stroke()
        }
      })
    })
    
    requestAnimationFrame(animate)
  }
  
  animate()
}

// 网格背景
const initGridMesh = () => {
  if (!gridMesh.value) return
  
  const grid = document.createElement('div')
  grid.className = 'grid-mesh-pattern'
  grid.style.cssText = `
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-image: 
      linear-gradient(rgba(139, 92, 246, 0.02) 1px, transparent 1px),
      linear-gradient(90deg, rgba(139, 92, 246, 0.02) 1px, transparent 1px);
    background-size: 60px 60px;
    pointer-events: none;
  `
  
  gridMesh.value.appendChild(grid)
}

// 更新时间
const updateTime = () => {
  const now = new Date()
  currentTime.value = now.toLocaleTimeString('zh-CN')
}

// 动画循环
const animationLoop = () => {
  updateParticles()
  requestAnimationFrame(animationLoop)
}

// 监听
watch(isDataFlowVisible, (visible) => {
  if (visible) {
    initDataFlowParticles()
    animationLoop()
  }
})

// 生命周期
onMounted(() => {
  nextTick(() => {
    initParticleNetwork()
    initGridMesh()
    
    if (isDataFlowVisible.value) {
      initDataFlowParticles()
      animationLoop()
    }
  })
  
  updateTime()
  setInterval(updateTime, 1000)
})

onUnmounted(() => {
  // 清理动画
  if (particleNetwork.value) {
    particleNetwork.value.innerHTML = ''
  }
  if (gridMesh.value) {
    gridMesh.value.innerHTML = ''
  }
})
</script>

<style lang="scss" scoped>
.architecture-layer {
  position: relative;
  width: 100vw;
  height: 100vh;
  overflow: hidden;
  background: var(--bg-deep);
  
  .immersive-background {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    z-index: 1;
    
    .particle-network {
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
    }
    
    .data-flow-canvas {
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
    }
    
    .grid-mesh {
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
    }
  }
  
  .main-interface {
    position: relative;
    z-index: 2;
    display: flex;
    flex-direction: column;
    height: 100vh;
  }
  
  .top-control-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: var(--spacing-4) var(--spacing-6);
    background: rgba(var(--surface-color), 0.05);
    backdrop-filter: blur(20px);
    border-bottom: 1px solid rgba(var(--border-color), 0.1);
    
    .control-left {
      .function-info {
        display: flex;
        align-items: center;
        gap: var(--spacing-3);
        
        .function-icon {
          padding: var(--spacing-2);
          background: rgba(var(--primary-color), 0.2);
          border-radius: var(--border-radius-lg);
        }
        
        .function-details {
          h2 {
            font-size: var(--font-size-lg);
            color: var(--text-primary);
            margin: 0 0 var(--spacing-1) 0;
          }
          
          p {
            font-size: var(--font-size-sm);
            color: var(--text-secondary);
            margin: 0;
          }
        }
      }
    }
    
    .control-center {
      display: flex;
      gap: var(--spacing-4);
      align-items: center;
      
      .view-controls {
        .n-button-group {
          background: rgba(var(--surface-color), 0.1);
          border-radius: var(--border-radius-lg);
        }
      }
      
      .interaction-controls {
        display: flex;
        gap: var(--spacing-2);
      }
    }
    
    .control-right {
      .layer-navigation {
        // 样式由LayerNavigation组件处理
      }
    }
  }
  
  .architecture-display {
    flex: 1;
    position: relative;
    overflow: hidden;
    
    .network-view {
      width: 100%;
      height: 100%;
      position: relative;
      
      .network-container {
        width: 100%;
        height: 100%;
        position: relative;
        
        .network-node {
          position: absolute;
          width: 100px;
          height: 100px;
          background: rgba(var(--surface-color), 0.1);
          border: 1px solid rgba(var(--border-color), 0.2);
          border-radius: var(--border-radius-lg);
          cursor: pointer;
          transition: all 0.3s ease;
          
          &:hover {
            transform: scale(1.05);
            background: rgba(var(--surface-color), 0.2);
            border-color: rgba(var(--primary-color), 0.4);
            
            .node-aura {
              opacity: 1;
            }
          }
          
          &.active {
            border-color: var(--primary-color);
            background: rgba(var(--primary-color), 0.1);
            
            .node-aura {
              opacity: 1;
            }
          }
          
          &.highlighted {
            border-color: var(--secondary-color);
          }
          
          .node-aura {
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, rgba(var(--primary-color), 0.2) 0%, transparent 70%);
            opacity: 0;
            transition: opacity 0.3s ease;
            pointer-events: none;
          }
          
          .node-content {
            position: relative;
            z-index: 2;
            padding: var(--spacing-3);
            height: 100%;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
           
            .node-icon {
              position: relative;
              margin-bottom: var(--spacing-2);
              
              .node-status {
                position: absolute;
                top: -4px;
                right: -4px;
                width: 10px;
                height: 10px;
                border-radius: 50%;
                
                &.online {
                  background: var(--success-color);
                  box-shadow: 0 0 8px rgba(var(--success-color), 0.6);
                }
              }
            }
           
            .node-info {
              text-align: center;
              
              h4 {
                font-size: var(--font-size-sm);
                color: var(--text-primary);
                margin: 0 0 var(--spacing-1) 0;
              }
              
              p {
                font-size: var(--font-size-xs);
                color: var(--text-secondary);
                margin: 0;
              }
            }
          }
          
          .connection-port {
            position: absolute;
            width: 8px;
            height: 8px;
            border-radius: 50%;
            
            &.input {
              background: var(--warning-color);
              box-shadow: 0 0 6px rgba(var(--warning-color), 0.6);
            }
           
            &.output {
              background: var(--success-color);
              box-shadow: 0 0 6px rgba(var(--success-color), 0.6);
            }
          }
        }
        
        .connections-svg {
          position: absolute;
          top: 0;
          left: 0;
          width: 100%;
          height: 100%;
          pointer-events: none;
          
          .connection-path {
            transition: stroke 0.3s ease;
            
            &.active {
              stroke-width: 3;
              filter: url(#glow) brightness(1.2);
            }
          }
          
          .data-particle {
            filter: url(#glow);
          }
        }
      }
    }
    
    .three-d-view {
      height: 100%;
      display: flex;
      align-items: center;
      justify-content: center;
      
      .three-d-placeholder {
        text-align: center;
        color: var(--text-secondary);
        
        .placeholder-desc {
          margin-top: var(--spacing-2);
          font-size: var(--font-size-sm);
        }
      }
    }
    
    .layers-view {
      height: 100%;
      overflow-y: auto;
      padding: var(--spacing-6);
      
      .layers-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
        gap: var(--spacing-6);
        
        .architecture-layer-card {
          background: rgba(var(--surface-color), 0.1);
          border: 1px solid rgba(var(--border-color), 0.2);
          border-radius: var(--border-radius-xl);
          padding: var(--spacing-5);
          cursor: pointer;
          transition: all 0.3s ease;
          
          &:hover {
            transform: translateY(-4px);
            background: rgba(var(--surface-color), 0.2);
            border-color: rgba(var(--primary-color), 0.4);
          }
          
          &.active {
            border-color: var(--primary-color);
            background: rgba(var(--primary-color), 0.1);
          }
          
          .layer-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: var(--spacing-4);
           
            .layer-icon {
              padding: var(--spacing-2);
              background: rgba(var(--primary-color), 0.2);
              border-radius: var(--border-radius-lg);
            }
           
            .layer-level {
              .level-badge {
                background: var(--accent-color);
                  color: white;
                  padding: var(--spacing-1) var(--spacing-2);
                  border-radius: var(--border-radius-full);
                  font-size: var(--font-size-xs);
                  font-weight: 600;
                }
              }
            }
            
            .layer-content {
              margin-bottom: var(--spacing-4);
             
              h3 {
                font-size: var(--font-size-lg);
                color: var(--text-primary);
                margin: 0 0 var(--spacing-2) 0;
              }
             
              p {
                color: var(--text-secondary);
                font-size: var(--font-size-sm);
                margin: 0 0 var(--spacing-4) 0;
              }
             
              .layer-components {
                display: flex;
                flex-wrap: wrap;
                gap: var(--spacing-2);
                
                .component-item {
                  display: flex;
                  align-items: center;
                  gap: var(--spacing-1);
                  padding: var(--spacing-2);
                  background: rgba(var(--primary-color), 0.05);
                  border-radius: var(--border-radius-md);
                 
                  span {
                    font-size: var(--font-size-xs);
                    color: var(--text-secondary);
                  }
                }
              }
            }
            
            .layer-metrics {
              .metric-item {
                display: flex;
                align-items: center;
                gap: var(--spacing-2);
                
                .metric-label {
                  font-size: var(--font-size-xs);
                  color: var(--text-tertiary);
                  min-width: 40px;
                }
                
                .metric-bar {
                  flex: 1;
                  height: 6px;
                  background: rgba(var(--border-color), 0.2);
                  border-radius: var(--border-radius-full);
                  overflow: hidden;
                 
                  .metric-fill {
                    height: 100%;
                    background: linear-gradient(90deg, var(--success-color), var(--warning-color));
                    transition: width 0.3s ease;
                  }
                }
                
                .metric-value {
                  font-size: var(--font-size-xs);
                  color: var(--text-primary);
                  font-weight: 600;
                  min-width: 30px;
                }
              }
            }
          }
        }
      }
    }
  
  .bottom-info-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: var(--spacing-3) var(--spacing-6);
    background: rgba(var(--surface-color), 0.05);
    backdrop-filter: blur(20px);
    border-top: 1px solid rgba(var(--border-color), 0.1);
    
    .info-left {
      display: flex;
      gap: var(--spacing-6);
      
      .node-count {
        display: flex;
        gap: var(--spacing-4);
        font-size: var(--font-size-sm);
        color: var(--text-secondary);
      }
      
      .performance-indicator {
        display: flex;
        align-items: center;
        gap: var(--spacing-2);
        
        .indicator-label {
          font-size: var(--font-size-sm);
          color: var(--text-secondary);
        }
        
        .indicator-bar {
          width: 100px;
          height: 6px;
          background: rgba(var(--border-color), 0.2);
          border-radius: var(--border-radius-full);
          overflow: hidden;
          
          .indicator-fill {
            height: 100%;
            background: linear-gradient(90deg, var(--success-color), var(--warning-color), var(--error-color));
            transition: width 0.3s ease;
          }
        }
        
        .indicator-value {
          font-size: var(--font-size-xs);
          color: var(--text-primary);
          font-weight: 600;
          min-width: 30px;
        }
      }
    }
    
    .info-center {
      .zoom-controls {
        display: flex;
        gap: var(--spacing-1);
      }
    }
    
    .info-right {
      .real-time-status {
        display: flex;
        gap: var(--spacing-4);
        
        .status-item {
          display: flex;
          align-items: center;
          gap: var(--spacing-2);
          
          .status-dot {
            width: 6px;
            height: 6px;
            border-radius: 50%;
           
            &.online {
              background: var(--success-color);
              box-shadow: 0 0 6px rgba(var(--success-color), 0.6);
            }
          }
        }
      }
    }
  }
  
  .node-detail-panel {
    position: fixed;
    top: 50%;
    right: var(--spacing-6);
    transform: translateY(-50%);
    width: 320px;
    background: rgba(var(--surface-color), 0.95);
    border: 1px solid rgba(var(--border-color), 0.2);
    border-radius: var(--border-radius-xl);
    backdrop-filter: blur(20px);
    z-index: 1000;
    
    .panel-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: var(--spacing-4);
      border-bottom: 1px solid rgba(var(--border-color), 0.1);
      
      h3 {
        font-size: var(--font-size-lg);
        color: var(--text-primary);
        margin: 0;
      }
    }
    
    .panel-content {
      padding: var(--spacing-4);
      
      .detail-section {
        margin-bottom: var(--spacing-6);
        
        h4 {
          font-size: var(--font-size-md);
          color: var(--text-primary);
          margin: 0 0 var(--spacing-3) 0;
        }
        
        .info-grid {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: var(--spacing-3);
          
          .info-item {
            .info-label {
              display: block;
              font-size: var(--font-size-xs);
              color: var(--text-tertiary);
              margin-bottom: var(--spacing-1);
            }
           
            .info-value {
              font-size: var(--font-size-sm);
              color: var(--text-primary);
              font-weight: 500;
            }
          }
        }
        
        .metrics-chart {
          height: 120px;
          background: rgba(var(--primary-color), 0.05);
          border-radius: var(--border-radius-lg);
        }
        
        .action-buttons {
          display: flex;
          gap: var(--spacing-2);
        }
      }
    }
  }
}

// 响应式设计
@media (max-width: 1200px) {
  .architecture-layer {
    .architecture-display {
      .layers-view .layers-container {
        grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
      }
    }
  }
}

@media (max-width: 768px) {
  .architecture-layer {
    .top-control-bar {
      flex-direction: column;
      gap: var(--spacing-4);
      padding: var(--spacing-3);
    }
    
    .architecture-display {
      .network-view .network-container .network-node {
        width: 80px;
        height: 80px;
      }
      
      .layers-view .layers-container {
        grid-template-columns: 1fr;
      }
    }
    
    .bottom-info-bar {
      flex-direction: column;
      gap: var(--spacing-3);
      padding: var(--spacing-3);
      
      .info-left,
      .info-center,
      .info-right {
        width: 100%;
        justify-content: center;
      }
    }
    
    .node-detail-panel {
      right: var(--spacing-3);
      width: 280px;
    }
  }
}
</style>
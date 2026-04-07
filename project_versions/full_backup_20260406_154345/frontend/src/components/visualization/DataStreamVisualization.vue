<template>
  <div class="data-stream-visualization" ref="visualizationContainer">
    <!-- 控制面板 -->
    <div class="control-panel" v-if="showControls">
      <div class="control-group">
        <label>可视化模式</label>
        <select v-model="visualizationMode" @change="switchMode">
          <option value="particle-flow">粒子流</option>
          <option value="network-graph">网络图</option>
          <option value="heatmap">热力图</option>
          <option value="timeline">时间线</option>
        </select>
      </div>
      
      <div class="control-group">
        <label>数据源</label>
        <select v-model="dataSource" @change="changeDataSource">
          <option value="real-time">实时数据</option>
          <option value="simulation">模拟数据</option>
          <option value="historical">历史数据</option>
        </select>
      </div>
      
      <div class="control-group">
        <label>更新频率</label>
        <input 
          type="range" 
          min="100" 
          max="5000" 
          step="100" 
          v-model="updateFrequency"
          @input="updateFrequencyChanged"
        >
        <span>{{ updateFrequency }}ms</span>
      </div>
      
      <div class="control-group">
        <label>粒子数量</label>
        <input 
          type="range" 
          min="10" 
          max="500" 
          step="10" 
          v-model="particleCount"
          @input="particleCountChanged"
        >
        <span>{{ particleCount }}</span>
      </div>
      
      <div class="control-actions">
        <button @click="toggleAnimation" :class="{ active: isAnimating }">
          <i :class="isAnimating ? 'fas fa-pause' : 'fas fa-play'"></i>
          {{ isAnimating ? '暂停' : '播放' }}
        </button>
        <button @click="resetVisualization">
          <i class="fas fa-redo"></i>
          重置
        </button>
        <button @click="exportData">
          <i class="fas fa-download"></i>
          导出
        </button>
      </div>
    </div>

    <!-- 主可视化区域 -->
    <div class="visualization-area" ref="visualizationArea">
      <!-- Canvas 用于粒子流和网络图 -->
      <canvas 
        ref="canvas" 
        class="visualization-canvas"
        v-show="visualizationMode === 'particle-flow' || visualizationMode === 'network-graph'"
      ></canvas>
      
      <!-- SVG 用于热力图和时间线 -->
      <svg 
        ref="svg" 
        class="visualization-svg"
        v-show="visualizationMode === 'heatmap' || visualizationMode === 'timeline'"
      ></svg>
      
      <!-- 性能指标叠加层 -->
      <div class="performance-overlay" v-if="showPerformanceMetrics">
        <div class="metric-card">
          <div class="metric-label">数据吞吐量</div>
          <div class="metric-value">{{ formatNumber(dataThroughput) }} ops/s</div>
        </div>
        <div class="metric-card">
          <div class="metric-label">平均延迟</div>
          <div class="metric-value">{{ averageLatency }}ms</div>
        </div>
        <div class="metric-card">
          <div class="metric-label">错误率</div>
          <div class="metric-value" :class="getErrorRateClass(errorRate)">{{ errorRate }}%</div>
        </div>
        <div class="metric-card">
          <div class="metric-label">活跃连接</div>
          <div class="metric-value">{{ activeConnections }}</div>
        </div>
      </div>
      
      <!-- 数据流图例 -->
      <div class="legend" v-if="showLegend">
        <div class="legend-title">数据流状态</div>
        <div class="legend-items">
          <div class="legend-item">
            <div class="legend-color" style="background: var(--market-rise);"></div>
            <span>正常流动</span>
          </div>
          <div class="legend-item">
            <div class="legend-color" style="background: #f59e0b;"></div>
            <span>警告状态</span>
          </div>
          <div class="legend-item">
            <div class="legend-color" style="background: var(--market-fall);"></div>
            <span>错误状态</span>
          </div>
          <div class="legend-item">
            <div class="legend-color" style="background: #8b5cf6;"></div>
            <span>AI处理中</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 数据详情弹窗 -->
    <div v-if="showDataDetails" class="data-details-modal" @click="closeDataDetails">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>数据流详情</h3>
          <button class="close-btn" @click="closeDataDetails">
            <i class="fas fa-times"></i>
          </button>
        </div>
        <div class="modal-body">
          <div class="detail-section">
            <h4>基本信息</h4>
            <div class="detail-grid">
              <div class="detail-item">
                <span class="detail-label">数据源:</span>
                <span class="detail-value">{{ selectedDataPoint?.source }}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">目标:</span>
                <span class="detail-value">{{ selectedDataPoint?.target }}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">类型:</span>
                <span class="detail-value">{{ selectedDataPoint?.type }}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">状态:</span>
                <span class="detail-value" :class="getStatusClass(selectedDataPoint?.status)">
                  {{ selectedDataPoint?.status }}
                </span>
              </div>
            </div>
          </div>
          
          <div class="detail-section">
            <h4>性能指标</h4>
            <div class="detail-grid">
              <div class="detail-item">
                <span class="detail-label">延迟:</span>
                <span class="detail-value">{{ selectedDataPoint?.latency }}ms</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">吞吐量:</span>
                <span class="detail-value">{{ selectedDataPoint?.throughput }} ops/s</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">错误率:</span>
                <span class="detail-value">{{ selectedDataPoint?.errorRate }}%</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">时间戳:</span>
                <span class="detail-value">{{ formatTimestamp(selectedDataPoint?.timestamp) }}</span>
              </div>
            </div>
          </div>
          
          <div class="detail-section" v-if="selectedDataPoint?.metadata">
            <h4>元数据</h4>
            <div class="metadata-grid">
              <div 
                v-for="(value, key) in selectedDataPoint.metadata" 
                :key="key"
                class="metadata-item"
              >
                <span class="metadata-key">{{ key }}:</span>
                <span class="metadata-value">{{ value }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { formatNumber, formatTimestamp } from '@/utils/format'

// Props
interface Props {
  width?: number
  height?: number
  showControls?: boolean
  showPerformanceMetrics?: boolean
  showLegend?: boolean
  initialMode?: string
  dataSource?: string
  updateFrequency?: number
  particleCount?: number
}

const props = withDefaults(defineProps<Props>(), {
  width: 800,
  height: 600,
  showControls: true,
  showPerformanceMetrics: true,
  showLegend: true,
  initialMode: 'particle-flow',
  dataSource: 'real-time',
  updateFrequency: 1000,
  particleCount: 100
})

// 响应式数据
const visualizationContainer = ref<HTMLElement>()
const visualizationArea = ref<HTMLElement>()
const canvas = ref<HTMLCanvasElement>()
const svg = ref<SVGSVGElement>()

const visualizationMode = ref(props.initialMode)
const dataSource = ref(props.dataSource)
const updateFrequency = ref(props.updateFrequency)
const particleCount = ref(props.particleCount)
const isAnimating = ref(true)
const showDataDetails = ref(false)
const selectedDataPoint = ref<any>(null)

// 性能指标
const dataThroughput = ref(1250)
const averageLatency = ref(8)
const errorRate = ref(0.5)
const activeConnections = ref(42)

// 粒子系统
const particles = ref<any[]>([])
const connections = ref<any[]>([])
const nodes = ref<any[]>([])

// 动画相关
let animationId: number | null = null
let updateInterval: number | null = null
let ctx: CanvasRenderingContext2D | null = null

// 数据流节点定义
const initializeNodes = () => {
  nodes.value = [
    { id: 'data-source', x: 100, y: 300, label: '数据源', type: 'input' },
    { id: 'processor-1', x: 300, y: 200, label: '处理器1', type: 'process' },
    { id: 'processor-2', x: 300, y: 400, label: '处理器2', type: 'process' },
    { id: 'ai-engine', x: 500, y: 300, label: 'AI引擎', type: 'ai' },
    { id: 'output-1', x: 700, y: 200, label: '输出1', type: 'output' },
    { id: 'output-2', x: 700, y: 400, label: '输出2', type: 'output' }
  ]
  
  connections.value = [
    { from: 'data-source', to: 'processor-1' },
    { from: 'data-source', to: 'processor-2' },
    { from: 'processor-1', to: 'ai-engine' },
    { from: 'processor-2', to: 'ai-engine' },
    { from: 'ai-engine', to: 'output-1' },
    { from: 'ai-engine', to: 'output-2' }
  ]
}

// 初始化粒子
const initializeParticles = () => {
  particles.value = []
  for (let i = 0; i < particleCount.value; i++) {
    const connection = connections.value[Math.floor(Math.random() * connections.value.length)]
    const fromNode = nodes.value.find(n => n.id === connection.from)
    const toNode = nodes.value.find(n => n.id === connection.to)
    
    if (fromNode && toNode) {
      particles.value.push({
        id: `particle-${i}`,
        x: fromNode.x,
        y: fromNode.y,
        targetX: toNode.x,
        targetY: toNode.y,
        progress: Math.random(),
        speed: 0.005 + Math.random() * 0.01,
        size: 2 + Math.random() * 4,
        color: getParticleColor(),
        connection: connection,
        status: getRandomStatus(),
        metadata: generateMetadata()
      })
    }
  }
}

// 获取粒子颜色
const getParticleColor = () => {
  const colors = ['#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#3b82f6']
  return colors[Math.floor(Math.random() * colors.length)]
}

// 获取随机状态
const getRandomStatus = () => {
  const statuses = ['normal', 'warning', 'error', 'processing']
  const weights = [0.7, 0.15, 0.05, 0.1]
  const random = Math.random()
  
  let cumulative = 0
  for (let i = 0; i < weights.length; i++) {
    cumulative += weights[i]
    if (random < cumulative) {
      return statuses[i]
    }
  }
  return 'normal'
}

// 生成元数据
const generateMetadata = () => {
  return {
    size: Math.floor(Math.random() * 1000) + 100,
    priority: ['low', 'medium', 'high'][Math.floor(Math.random() * 3)],
    source: ['api', 'database', 'cache', 'queue'][Math.floor(Math.random() * 4)],
    timestamp: Date.now()
  }
}

// 初始化Canvas
const initializeCanvas = () => {
  if (!canvas.value) return
  
  canvas.value.width = props.width
  canvas.value.height = props.height
  ctx = canvas.value.getContext('2d')
  
  if (ctx) {
    ctx.lineCap = 'round'
    ctx.lineJoin = 'round'
  }
}

// 绘制粒子流
const drawParticleFlow = () => {
  if (!ctx || !canvas.value) return
  
  // 清空画布
  ctx.clearRect(0, 0, canvas.value.width, canvas.value.height)
  
  // 绘制连接线
  ctx.strokeStyle = 'rgba(255, 255, 255, 0.1)'
  ctx.lineWidth = 1
  
  connections.value.forEach(connection => {
    const fromNode = nodes.value.find(n => n.id === connection.from)
    const toNode = nodes.value.find(n => n.id === connection.to)
    
    if (fromNode && toNode) {
      ctx.beginPath()
      ctx.moveTo(fromNode.x, fromNode.y)
      ctx.lineTo(toNode.x, toNode.y)
      ctx.stroke()
    }
  })
  
  // 绘制节点
  nodes.value.forEach(node => {
    ctx.fillStyle = getNodeColor(node.type)
    ctx.beginPath()
    ctx.arc(node.x, node.y, 20, 0, Math.PI * 2)
    ctx.fill()
    
    // 绘制节点标签
    ctx.fillStyle = '#ffffff'
    ctx.font = '12px Arial'
    ctx.textAlign = 'center'
    ctx.fillText(node.label, node.x, node.y + 35)
  })
  
  // 绘制粒子
  particles.value.forEach(particle => {
    // 更新粒子位置
    particle.progress += particle.speed
    
    if (particle.progress >= 1) {
      // 重置粒子
      const connection = connections.value[Math.floor(Math.random() * connections.value.length)]
      const fromNode = nodes.value.find(n => n.id === connection.from)
      const toNode = nodes.value.find(n => n.id === connection.to)
      
      if (fromNode && toNode) {
        particle.x = fromNode.x
        particle.y = fromNode.y
        particle.targetX = toNode.x
        particle.targetY = toNode.y
        particle.progress = 0
        particle.connection = connection
        particle.status = getRandomStatus()
        particle.color = getParticleColor()
      }
    }
    
    // 计算当前位置
    const currentX = particle.x + (particle.targetX - particle.x) * particle.progress
    const currentY = particle.y + (particle.targetY - particle.y) * particle.progress
    
    // 绘制粒子
    ctx.fillStyle = particle.color
    ctx.globalAlpha = 0.8
    ctx.beginPath()
    ctx.arc(currentX, currentY, particle.size, 0, Math.PI * 2)
    ctx.fill()
    
    // 绘制粒子光晕
    ctx.globalAlpha = 0.3
    ctx.beginPath()
    ctx.arc(currentX, currentY, particle.size * 2, 0, Math.PI * 2)
    ctx.fill()
    
    ctx.globalAlpha = 1
  })
}

// 获取节点颜色
const getNodeColor = (type: string) => {
  const colors = {
    input: '#10b981',
    process: '#3b82f6',
    ai: '#8b5cf6',
    output: '#f59e0b'
  }
  return colors[type] || '#6b7280'
}

// 绘制网络图
const drawNetworkGraph = () => {
  if (!ctx || !canvas.value) return
  
  ctx.clearRect(0, 0, canvas.value.width, canvas.value.height)
  
  // 绘制网络连接
  connections.value.forEach(connection => {
    const fromNode = nodes.value.find(n => n.id === connection.from)
    const toNode = nodes.value.find(n => n.id === connection.to)
    
    if (fromNode && toNode) {
      // 绘制连接线
      const gradient = ctx.createLinearGradient(fromNode.x, fromNode.y, toNode.x, toNode.y)
      gradient.addColorStop(0, getNodeColor(fromNode.type))
      gradient.addColorStop(1, getNodeColor(toNode.type))
      
      ctx.strokeStyle = gradient
      ctx.lineWidth = 2
      ctx.beginPath()
      ctx.moveTo(fromNode.x, fromNode.y)
      ctx.lineTo(toNode.x, toNode.y)
      ctx.stroke()
      
      // 绘制数据流动画
      const particleCount = 3
      for (let i = 0; i < particleCount; i++) {
        const progress = ((Date.now() / 1000 + i * 0.3) % 1)
        const x = fromNode.x + (toNode.x - fromNode.x) * progress
        const y = fromNode.y + (toNode.y - fromNode.y) * progress
        
        ctx.fillStyle = '#ffffff'
        ctx.globalAlpha = 0.8
        ctx.beginPath()
        ctx.arc(x, y, 3, 0, Math.PI * 2)
        ctx.fill()
        ctx.globalAlpha = 1
      }
    }
  })
  
  // 绘制节点
  nodes.value.forEach(node => {
    // 绘制节点外圈
    ctx.strokeStyle = getNodeColor(node.type)
    ctx.lineWidth = 3
    ctx.beginPath()
    ctx.arc(node.x, node.y, 25, 0, Math.PI * 2)
    ctx.stroke()
    
    // 绘制节点内圈
    ctx.fillStyle = getNodeColor(node.type)
    ctx.globalAlpha = 0.3
    ctx.beginPath()
    ctx.arc(node.x, node.y, 20, 0, Math.PI * 2)
    ctx.fill()
    ctx.globalAlpha = 1
    
    // 绘制节点标签
    ctx.fillStyle = '#ffffff'
    ctx.font = 'bold 14px Arial'
    ctx.textAlign = 'center'
    ctx.fillText(node.label, node.x, node.y + 40)
  })
}

// 绘制热力图
const drawHeatmap = () => {
  if (!svg.value) return
  
  // 清空SVG
  svg.value.innerHTML = ''
  
  const width = props.width
  const height = props.height
  const gridSize = 20
  const cols = Math.floor(width / gridSize)
  const rows = Math.floor(height / gridSize)
  
  // 创建热力图数据
  for (let row = 0; row < rows; row++) {
    for (let col = 0; col < cols; col++) {
      const value = Math.random()
      const color = getHeatmapColor(value)
      
      const rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect')
      rect.setAttribute('x', col * gridSize)
      rect.setAttribute('y', row * gridSize)
      rect.setAttribute('width', gridSize)
      rect.setAttribute('height', gridSize)
      rect.setAttribute('fill', color)
      rect.setAttribute('opacity', '0.8')
      
      // 添加交互
      rect.addEventListener('click', () => {
        showDataPointDetails({
          x: col * gridSize,
          y: row * gridSize,
          value: value,
          type: 'heatmap-cell'
        })
      })
      
      svg.value.appendChild(rect)
    }
  }
  
  // 添加颜色标尺
  const gradientId = 'heatmap-gradient'
  const defs = document.createElementNS('http://www.w3.org/2000/svg', 'defs')
  
  const gradient = document.createElementNS('http://www.w3.org/2000/svg', 'linearGradient')
  gradient.setAttribute('id', gradientId)
  gradient.setAttribute('x1', '0%')
  gradient.setAttribute('y1', '0%')
  gradient.setAttribute('x2', '0%')
  gradient.setAttribute('y2', '100%')
  
  const colors = [
    { offset: '0%', color: '#ef4444' },
    { offset: '25%', color: '#f59e0b' },
    { offset: '50%', color: '#eab308' },
    { offset: '75%', color: '#84cc16' },
    { offset: '100%', color: '#10b981' }
  ]
  
  colors.forEach(({ offset, color }) => {
    const stop = document.createElementNS('http://www.w3.org/2000/svg', 'stop')
    stop.setAttribute('offset', offset)
    stop.setAttribute('stop-color', color)
    gradient.appendChild(stop)
  })
  
  defs.appendChild(gradient)
  svg.value.appendChild(defs)
  
  // 添加标尺矩形
  const scaleRect = document.createElementNS('http://www.w3.org/2000/svg', 'rect')
  scaleRect.setAttribute('x', width - 30)
  scaleRect.setAttribute('y', 50)
  scaleRect.setAttribute('width', 20)
  scaleRect.setAttribute('height', 200)
  scaleRect.setAttribute('fill', `url(#${gradientId})`)
  scaleRect.setAttribute('stroke', '#ffffff')
  scaleRect.setAttribute('stroke-width', '1')
  svg.value.appendChild(scaleRect)
  
  // 添加标尺标签
  const labels = ['高', '中', '低']
  labels.forEach((label, index) => {
    const text = document.createElementNS('http://www.w3.org/2000/svg', 'text')
    text.setAttribute('x', width - 50)
    text.setAttribute('y', 60 + index * 80)
    text.setAttribute('fill', '#ffffff')
    text.setAttribute('font-size', '12')
    text.textContent = label
    svg.value.appendChild(text)
  })
}

// 获取热力图颜色
const getHeatmapColor = (value: number) => {
  if (value < 0.2) return '#10b981'
  if (value < 0.4) return '#84cc16'
  if (value < 0.6) return '#eab308'
  if (value < 0.8) return '#f59e0b'
  return '#ef4444'
}

// 绘制时间线
const drawTimeline = () => {
  if (!svg.value) return
  
  svg.value.innerHTML = ''
  
  const width = props.width
  const height = props.height
  const padding = 50
  const timelineWidth = width - padding * 2
  const timelineHeight = height - padding * 2
  
  // 绘制时间轴
  const timeline = document.createElementNS('http://www.w3.org/2000/svg', 'line')
  timeline.setAttribute('x1', padding)
  timeline.setAttribute('y1', height / 2)
  timeline.setAttribute('x2', width - padding)
  timeline.setAttribute('y2', height / 2)
  timeline.setAttribute('stroke', '#ffffff')
  timeline.setAttribute('stroke-width', '2')
  svg.value.appendChild(timeline)
  
  // 生成时间线数据点
  const dataPoints = []
  const now = Date.now()
  for (let i = 0; i < 20; i++) {
    dataPoints.push({
      time: now - (19 - i) * 60000, // 每分钟一个数据点
      value: Math.random() * 100,
      status: getRandomStatus()
    })
  }
  
  // 绘制数据点
  dataPoints.forEach((point, index) => {
    const x = padding + (index / (dataPoints.length - 1)) * timelineWidth
    const y = height / 2 - (point.value / 100) * (timelineHeight / 2)
    
    // 绘制连接线
    if (index > 0) {
      const prevPoint = dataPoints[index - 1]
      const prevX = padding + ((index - 1) / (dataPoints.length - 1)) * timelineWidth
      const prevY = height / 2 - (prevPoint.value / 100) * (timelineHeight / 2)
      
      const line = document.createElementNS('http://www.w3.org/2000/svg', 'line')
      line.setAttribute('x1', prevX)
      line.setAttribute('y1', prevY)
      line.setAttribute('x2', x)
      line.setAttribute('y2', y)
      line.setAttribute('stroke', getStatusColor(point.status))
      line.setAttribute('stroke-width', '2')
      line.setAttribute('opacity', '0.7')
      svg.value.appendChild(line)
    }
    
    // 绘制数据点
    const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle')
    circle.setAttribute('cx', x)
    circle.setAttribute('cy', y)
    circle.setAttribute('r', '6')
    circle.setAttribute('fill', getStatusColor(point.status))
    circle.setAttribute('stroke', '#ffffff')
    circle.setAttribute('stroke-width', '2')
    
    // 添加交互
    circle.addEventListener('click', () => {
      showDataPointDetails({
        time: point.time,
        value: point.value,
        status: point.status,
        type: 'timeline-point'
      })
    })
    
    svg.value.appendChild(circle)
    
    // 添加时间标签
    const text = document.createElementNS('http://www.w3.org/2000/svg', 'text')
    text.setAttribute('x', x)
    text.setAttribute('y', height / 2 + 40)
    text.setAttribute('fill', '#ffffff')
    text.setAttribute('font-size', '10')
    text.setAttribute('text-anchor', 'middle')
    text.textContent = formatTimestamp(point.time)
    svg.value.appendChild(text)
  })
}

// 获取状态颜色
const getStatusColor = (status: string) => {
  const colors = {
    normal: '#10b981',
    warning: '#f59e0b',
    error: '#ef4444',
    processing: '#8b5cf6'
  }
  return colors[status] || '#6b7280'
}

// 动画循环
const animate = () => {
  if (!isAnimating.value) return
  
  switch (visualizationMode.value) {
    case 'particle-flow':
      drawParticleFlow()
      break
    case 'network-graph':
      drawNetworkGraph()
      break
    case 'heatmap':
      drawHeatmap()
      break
    case 'timeline':
      drawTimeline()
      break
  }
  
  animationId = requestAnimationFrame(animate)
}

// 更新性能指标
const updatePerformanceMetrics = () => {
  dataThroughput.value = Math.max(0, dataThroughput.value + (Math.random() - 0.5) * 100)
  averageLatency.value = Math.max(0, averageLatency.value + (Math.random() - 0.5) * 2)
  errorRate.value = Math.max(0, Math.min(100, errorRate.value + (Math.random() - 0.5) * 0.5))
  activeConnections.value = Math.max(0, activeConnections.value + Math.floor((Math.random() - 0.5) * 5))
}

// 显示数据点详情
const showDataPointDetails = (dataPoint: any) => {
  selectedDataPoint.value = dataPoint
  showDataDetails.value = true
}

// 关闭数据详情
const closeDataDetails = () => {
  showDataDetails.value = false
  selectedDataPoint.value = null
}

// 获取状态样式类
const getStatusClass = (status: string) => {
  return `status-${status}`
}

// 获取错误率样式类
const getErrorRateClass = (rate: number) => {
  if (rate < 1) return 'error-good'
  if (rate < 5) return 'error-warning'
  return 'error-critical'
}

// 切换模式
const switchMode = () => {
  nextTick(() => {
    initializeVisualization()
  })
}

// 更改数据源
const changeDataSource = () => {
  // 重新初始化数据
  initializeVisualization()
}

// 更新频率变化
const updateFrequencyChanged = () => {
  if (updateInterval) {
    clearInterval(updateInterval)
    updateInterval = setInterval(updatePerformanceMetrics, updateFrequency.value)
  }
}

// 粒子数量变化
const particleCountChanged = () => {
  initializeParticles()
}

// 切换动画
const toggleAnimation = () => {
  isAnimating.value = !isAnimating.value
  if (isAnimating.value) {
    animate()
  } else if (animationId) {
    cancelAnimationFrame(animationId)
  }
}

// 重置可视化
const resetVisualization = () => {
  initializeNodes()
  initializeParticles()
  dataThroughput.value = 1250
  averageLatency.value = 8
  errorRate.value = 0.5
  activeConnections.value = 42
}

// 导出数据
const exportData = () => {
  const exportData = {
    mode: visualizationMode.value,
    dataSource: dataSource.value,
    performanceMetrics: {
      dataThroughput: dataThroughput.value,
      averageLatency: averageLatency.value,
      errorRate: errorRate.value,
      activeConnections: activeConnections.value
    },
    nodes: nodes.value,
    connections: connections.value,
    particles: particles.value.slice(0, 10), // 只导出前10个粒子作为示例
    timestamp: new Date().toISOString()
  }
  
  const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `data-stream-${Date.now()}.json`
  a.click()
  URL.revokeObjectURL(url)
}

// 初始化可视化
const initializeVisualization = () => {
  switch (visualizationMode.value) {
    case 'particle-flow':
    case 'network-graph':
      initializeCanvas()
      initializeNodes()
      initializeParticles()
      break
    case 'heatmap':
      drawHeatmap()
      break
    case 'timeline':
      drawTimeline()
      break
  }
}

// 监听窗口大小变化
const handleResize = () => {
  if (visualizationContainer.value) {
    const rect = visualizationContainer.value.getBoundingClientRect()
    // 更新画布大小
    if (canvas.value) {
      canvas.value.width = rect.width
      canvas.value.height = rect.height
    }
    if (svg.value) {
      svg.value.setAttribute('width', rect.width.toString())
      svg.value.setAttribute('height', rect.height.toString())
    }
  }
}

// 生命周期
onMounted(() => {
  initializeVisualization()
  
  if (isAnimating.value) {
    animate()
  }
  
  // 启动性能指标更新
  updateInterval = setInterval(updatePerformanceMetrics, updateFrequency.value)
  
  // 监听窗口大小变化
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  if (animationId) {
    cancelAnimationFrame(animationId)
  }
  
  if (updateInterval) {
    clearInterval(updateInterval)
  }
  
  window.removeEventListener('resize', handleResize)
})

// 监听props变化
watch(() => props.width, () => {
  handleResize()
})

watch(() => props.height, () => {
  handleResize()
})
</script>

<style lang="scss" scoped>
.data-stream-visualization {
  position: relative;
  width: 100%;
  height: 100%;
  background: var(--bg-deep);
  border-radius: 12px;
  overflow: hidden;
  
  .control-panel {
    position: absolute;
    top: 20px;
    left: 20px;
    z-index: 10;
    display: flex;
    flex-direction: column;
    gap: 16px;
    padding: 20px;
    background: rgba(26, 26, 46, 0.9);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 12px;
    min-width: 280px;
    
    .control-group {
      display: flex;
      flex-direction: column;
      gap: 8px;
      
      label {
        color: var(--text-primary);
        font-size: 14px;
        font-weight: 500;
      }
      
      select, input[type="range"] {
        padding: 8px 12px;
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 6px;
        color: var(--text-primary);
        font-size: 14px;
        
        &:focus {
          outline: none;
          border-color: var(--primary);
        }
      }
      
      input[type="range"] {
        padding: 0;
        height: 4px;
        background: rgba(255, 255, 255, 0.1);
        border: none;
        
        &::-webkit-slider-thumb {
          appearance: none;
          width: 16px;
          height: 16px;
          background: var(--primary);
          border-radius: 50%;
          cursor: pointer;
        }
      }
      
      span {
        color: var(--text-secondary);
        font-size: 12px;
      }
    }
    
    .control-actions {
      display: flex;
      gap: 8px;
      
      button {
        flex: 1;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 6px;
        padding: 10px 12px;
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 6px;
        color: var(--text-primary);
        font-size: 12px;
        cursor: pointer;
        transition: all 0.3s ease;
        
        &:hover {
          background: rgba(255, 255, 255, 0.1);
          border-color: rgba(255, 255, 255, 0.2);
        }
        
        &.active {
          background: var(--primary);
          border-color: var(--primary);
        }
        
        i {
          font-size: 12px;
        }
      }
    }
  }
  
  .visualization-area {
    position: relative;
    width: 100%;
    height: 100%;
    
    .visualization-canvas, .visualization-svg {
      width: 100%;
      height: 100%;
    }
    
    .performance-overlay {
      position: absolute;
      top: 20px;
      right: 20px;
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 12px;
      padding: 16px;
      background: rgba(26, 26, 46, 0.9);
      backdrop-filter: blur(10px);
      border: 1px solid rgba(255, 255, 255, 0.1);
      border-radius: 12px;
      
      .metric-card {
        display: flex;
        flex-direction: column;
        gap: 4px;
        padding: 12px;
        background: rgba(255, 255, 255, 0.05);
        border-radius: 8px;
        
        .metric-label {
          color: var(--text-secondary);
          font-size: 12px;
        }
        
        .metric-value {
          color: var(--text-primary);
          font-size: 18px;
          font-weight: 600;
          
          &.error-good {
            color: var(--market-rise);
          }
          
          &.error-warning {
            color: #f59e0b;
          }
          
          &.error-critical {
            color: var(--market-fall);
          }
        }
      }
    }
    
    .legend {
      position: absolute;
      bottom: 20px;
      right: 20px;
      padding: 16px;
      background: rgba(26, 26, 46, 0.9);
      backdrop-filter: blur(10px);
      border: 1px solid rgba(255, 255, 255, 0.1);
      border-radius: 12px;
      
      .legend-title {
        color: var(--text-primary);
        font-size: 14px;
        font-weight: 500;
        margin-bottom: 12px;
      }
      
      .legend-items {
        display: flex;
        flex-direction: column;
        gap: 8px;
        
        .legend-item {
          display: flex;
          align-items: center;
          gap: 8px;
          
          .legend-color {
            width: 12px;
            height: 12px;
            border-radius: 50%;
          }
          
          span {
            color: var(--text-secondary);
            font-size: 12px;
          }
        }
      }
    }
  }
  
  .data-details-modal {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    background: rgba(0, 0, 0, 0.8);
    backdrop-filter: blur(10px);
    z-index: 1000;
    display: flex;
    align-items: center;
    justify-content: center;
    
    .modal-content {
      width: 90%;
      max-width: 600px;
      max-height: 80vh;
      background: rgba(26, 26, 46, 0.95);
      backdrop-filter: blur(20px);
      border: 1px solid rgba(255, 255, 255, 0.1);
      border-radius: 16px;
      overflow: hidden;
      
      .modal-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 20px 24px;
        background: rgba(0, 0, 0, 0.3);
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        
        h3 {
          margin: 0;
          color: var(--text-primary);
          font-size: 20px;
          font-weight: 600;
        }
        
        .close-btn {
          width: 32px;
          height: 32px;
          background: transparent;
          border: none;
          border-radius: 50%;
          color: var(--text-secondary);
          cursor: pointer;
          transition: all 0.2s ease;
          
          &:hover {
            background: rgba(255, 255, 255, 0.1);
            color: var(--text-primary);
          }
        }
      }
      
      .modal-body {
        padding: 24px;
        overflow-y: auto;
        max-height: calc(80vh - 80px);
        
        .detail-section {
          margin-bottom: 24px;
          
          h4 {
            margin: 0 0 16px 0;
            color: var(--text-primary);
            font-size: 16px;
            font-weight: 600;
          }
          
          .detail-grid, .metadata-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 12px;
            
            .detail-item, .metadata-item {
              display: flex;
              justify-content: space-between;
              padding: 8px 12px;
              background: rgba(255, 255, 255, 0.05);
              border-radius: 6px;
              
              .detail-label, .metadata-key {
                color: var(--text-secondary);
                font-size: 14px;
              }
              
              .detail-value, .metadata-value {
                color: var(--text-primary);
                font-size: 14px;
                font-weight: 500;
                
                &.status-normal {
                  color: var(--market-rise);
                }
                
                &.status-warning {
                  color: #f59e0b;
                }
                
                &.status-error {
                  color: var(--market-fall);
                }
                
                &.status-processing {
                  color: #8b5cf6;
                }
              }
            }
          }
          
          .metadata-grid {
            grid-template-columns: 1fr;
          }
        }
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
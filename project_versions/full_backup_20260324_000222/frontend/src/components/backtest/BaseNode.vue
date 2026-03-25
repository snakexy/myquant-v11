<template>
  <div 
    class="base-node"
    :class="nodeClasses"
    :style="nodeStyle"
    @mousedown="handleMouseDown"
    @touchstart="handleTouchStart"
    @dblclick="handleDoubleClick"
  >
    <!-- 节点头部 -->
    <div class="node-header">
      <div class="node-icon">{{ nodeData.icon }}</div>
      <div class="node-title">{{ nodeData.title }}</div>
      <div class="node-status" :class="statusClass">
        <div class="status-dot"></div>
      </div>
    </div>
    
    <!-- 节点内容 -->
    <div class="node-content">
      <!-- 圆形进度条 -->
      <div v-if="nodeData.showProgress" class="circular-progress">
        <svg class="progress-svg" viewBox="0 0 100 100">
          <circle
            class="progress-bg"
            cx="50"
            cy="50"
            r="45"
            fill="none"
            stroke="rgba(255, 255, 255, 0.1)"
            stroke-width="8"
          />
          <circle
            class="progress-fill"
            cx="50"
            cy="50"
            r="45"
            fill="none"
            :stroke="progressColor"
            stroke-width="8"
            stroke-linecap="round"
            :stroke-dasharray="circumference"
            :stroke-dashoffset="progressOffset"
            transform="rotate(-90 50 50)"
          />
          <text
            x="50"
            y="50"
            text-anchor="middle"
            dy="0.3em"
            class="progress-text"
            :fill="textColor"
          >
            {{ nodeData.progress }}%
          </text>
        </svg>
      </div>
      
      <!-- 六边形性能图 -->
      <div v-if="nodeData.showHexagon" class="hexagon-performance">
        <svg class="hexagon-svg" viewBox="0 0 200 200">
          <!-- 六边形背景 -->
          <polygon
            class="hexagon-bg"
            points="100,20 170,60 170,140 100,180 30,140 30,60"
            fill="none"
            stroke="rgba(255, 255, 255, 0.2)"
            stroke-width="2"
          />
          
          <!-- 性能数据多边形 -->
          <polygon
            class="hexagon-data"
            :points="hexagonPoints"
            fill="rgba(37, 99, 235, 0.3)"
            stroke="#2563eb"
            stroke-width="2"
          />
          
          <!-- 数据点和标签 -->
          <g v-for="(point, index) in hexagonData" :key="index">
            <circle
              :cx="point.x"
              :cy="point.y"
              r="4"
              fill="#2563eb"
              class="data-point"
            />
            <text
              :x="point.labelX"
              :y="point.labelY"
              class="data-label"
              fill="#94a3b8"
              font-size="10"
              text-anchor="middle"
            >
              {{ point.label }}
            </text>
          </g>
        </svg>
      </div>
      
      <!-- 指标展示 -->
      <div v-if="nodeData.metrics" class="metrics-container">
        <div 
          v-for="(metric, index) in nodeData.metrics" 
          :key="index"
          class="metric-item"
        >
          <div class="metric-value">{{ metric.value }}</div>
          <div class="metric-label">{{ metric.label }}</div>
        </div>
      </div>
      
      <!-- 参数展示 -->
      <div v-if="nodeData.parameters" class="parameters-container">
        <div 
          v-for="(param, index) in nodeData.parameters" 
          :key="index"
          class="parameter-item"
        >
          <span class="param-name">{{ param.name }}:</span>
          <span class="param-value">{{ param.value }}</span>
        </div>
      </div>
    </div>
    
    <!-- 连接点 -->
    <div class="connection-points">
      <div 
        v-for="point in connectionPoints" 
        :key="point.id"
        class="connection-point"
        :class="point.type"
        :style="point.style"
        @mousedown.stop="handleConnectionStart(point)"
        @mouseup.stop="handleConnectionEnd(point)"
      >
        <div class="point-inner"></div>
      </div>
    </div>
    
    <!-- 拖拽手柄 -->
    <div class="drag-handle">
      <div class="drag-handle-icon">⋮⋮</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, onMounted, watch } from 'vue'

interface NodeData {
  id: string
  title: string
  icon: string
  type: 'config' | 'processing' | 'result' | 'metric'
  status: 'idle' | 'running' | 'completed' | 'error'
  position: { x: number; y: number }
  size: { width: number; height: number }
  showProgress?: boolean
  progress?: number
  showHexagon?: boolean
  hexagonData?: Array<{
    label: string
    value: number
    max: number
  }>
  metrics?: Array<{
    label: string
    value: string | number
  }>
  parameters?: Array<{
    name: string
    value: string | number
  }>
}

interface ConnectionPoint {
  id: string
  type: 'input' | 'output'
  position: 'top' | 'right' | 'bottom' | 'left'
  style: {
    left?: string
    top?: string
    right?: string
    bottom?: string
  }
}

const props = defineProps<{
  nodeData: NodeData
  isSelected?: boolean
}>()

const emit = defineEmits<{
  nodeClick: [nodeId: string]
  nodeDoubleClick: [nodeId: string]
  nodeDragStart: [nodeId: string, event: MouseEvent | TouchEvent]
  nodeDragMove: [nodeId: string, position: { x: number; y: number }]
  nodeDragEnd: [nodeId: string]
  connectionStart: [pointId: string, nodeId: string]
  connectionEnd: [pointId: string, nodeId: string]
}>()

// 计算属性
const nodeClasses = computed(() => ({
  'node-selected': props.isSelected,
  [`node-${props.nodeData.type}`]: true,
  [`node-${props.nodeData.status}`]: true
}))

const nodeStyle = computed(() => ({
  left: `${props.nodeData.position.x}px`,
  top: `${props.nodeData.position.y}px`,
  width: `${props.nodeData.size.width}px`,
  height: `${props.nodeData.size.height}px`
}))

const statusClass = computed(() => `status-${props.nodeData.status}`)

const progressColor = computed(() => {
  if (!props.nodeData.progress) return '#2563eb'
  if (props.nodeData.progress < 30) return '#ef4444'
  if (props.nodeData.progress < 70) return '#f59e0b'
  return '#10b981'
})

const textColor = computed(() => '#f8fafc')

const circumference = computed(() => 2 * Math.PI * 45)

const progressOffset = computed(() => {
  if (!props.nodeData.progress) return circumference.value
  return circumference.value - (props.nodeData.progress / 100) * circumference.value
})

// 六边形数据点计算
const hexagonPoints = computed(() => {
  if (!props.nodeData.hexagonData) return ''
  
  const centerX = 100
  const centerY = 100
  const radius = 60
  const angles = [0, 60, 120, 180, 240, 300]
  
  return props.nodeData.hexagonData
    .map((item, index) => {
      const angle = (angles[index] - 90) * (Math.PI / 180)
      const value = (item.value / item.max) * radius
      const x = centerX + value * Math.cos(angle)
      const y = centerY + value * Math.sin(angle)
      return `${x},${y}`
    })
    .join(' ')
})

const hexagonData = computed(() => {
  if (!props.nodeData.hexagonData) return []
  
  const centerX = 100
  const centerY = 100
  const radius = 60
  const labelRadius = 80
  const angles = [0, 60, 120, 180, 240, 300]
  
  return props.nodeData.hexagonData.map((item, index) => {
    const angle = (angles[index] - 90) * (Math.PI / 180)
    const value = (item.value / item.max) * radius
    const x = centerX + value * Math.cos(angle)
    const y = centerY + value * Math.sin(angle)
    const labelX = centerX + labelRadius * Math.cos(angle)
    const labelY = centerY + labelRadius * Math.sin(angle)
    
    return {
      x,
      y,
      labelX,
      labelY,
      label: item.label
    }
  })
})

// 连接点配置
const connectionPoints = computed<ConnectionPoint[]>(() => {
  const points: ConnectionPoint[] = []
  
  // 输入点（左侧）
  if (props.nodeData.type !== 'config') {
    points.push({
      id: `${props.nodeData.id}-input-left`,
      type: 'input',
      position: 'left',
      style: {
        left: '-8px',
        top: '50%'
      }
    })
  }
  
  // 输出点（右侧）
  if (props.nodeData.type !== 'result') {
    points.push({
      id: `${props.nodeData.id}-output-right`,
      type: 'output',
      position: 'right',
      style: {
        right: '-8px',
        top: '50%'
      }
    })
  }
  
  return points
})

// 事件处理
const handleMouseDown = (event: MouseEvent) => {
  emit('nodeClick', props.nodeData.id)
  emit('nodeDragStart', props.nodeData.id, event)
}

const handleTouchStart = (event: TouchEvent) => {
  emit('nodeClick', props.nodeData.id)
  emit('nodeDragStart', props.nodeData.id, event)
}

const handleDoubleClick = () => {
  emit('nodeDoubleClick', props.nodeData.id)
}

const handleConnectionStart = (point: ConnectionPoint) => {
  emit('connectionStart', point.id, props.nodeData.id)
}

const handleConnectionEnd = (point: ConnectionPoint) => {
  emit('connectionEnd', point.id, props.nodeData.id)
}

// 生命周期
onMounted(() => {
  // 节点初始化逻辑
})
</script>

<style lang="scss" scoped>
.base-node {
  position: absolute;
  background: #2d2d2d;
  border: 2px solid #404040;
  border-radius: 12px;
  cursor: move;
  transition: all 0.3s ease;
  user-select: none;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
  
  &:hover {
    border-color: #2563eb;
    box-shadow: 0 8px 24px rgba(37, 99, 235, 0.2);
  }
  
  &.node-selected {
    border-color: #7c3aed;
    box-shadow: 0 0 0 3px rgba(124, 58, 237, 0.2);
  }
  
  &.node-running {
    border-color: #f59e0b;
    animation: pulse-running 2s infinite;
  }
  
  &.node-completed {
    border-color: var(--market-rise);
  }
  
  &.node-error {
    border-color: var(--market-fall);
  }
}

.node-header {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  background: linear-gradient(135deg, rgba(37, 99, 235, 0.1) 0%, rgba(124, 58, 237, 0.05) 100%);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 10px 10px 0 0;
  
  .node-icon {
    font-size: 18px;
    margin-right: 8px;
  }
  
  .node-title {
    flex: 1;
    font-size: 14px;
    font-weight: 600;
    color: #f8fafc;
  }
  
  .node-status {
    width: 12px;
    height: 12px;
    border-radius: 50%;
    position: relative;
    
    .status-dot {
      width: 8px;
      height: 8px;
      border-radius: 50%;
      position: absolute;
      top: 2px;
      left: 2px;
    }
    
    &.status-idle .status-dot {
      background: #64748b;
    }
    
    &.status-running .status-dot {
      background: #f59e0b;
      animation: pulse 1.5s infinite;
    }
    
    &.status-completed .status-dot {
      background: var(--market-rise);
    }
    
    &.status-error .status-dot {
      background: var(--market-fall);
    }
  }
}

.node-content {
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.circular-progress {
  width: 80px;
  height: 80px;
  margin: 0 auto;
  
  .progress-svg {
    width: 100%;
    height: 100%;
    
    .progress-fill {
      transition: stroke-dashoffset 0.5s ease;
    }
    
    .progress-text {
      font-size: 12px;
      font-weight: 600;
    }
  }
}

.hexagon-performance {
  width: 120px;
  height: 120px;
  margin: 0 auto;
  
  .hexagon-svg {
    width: 100%;
    height: 100%;
    
    .data-point {
      cursor: pointer;
      transition: r 0.2s ease;
      
      &:hover {
        r: 6;
      }
    }
    
    .data-label {
      font-size: 10px;
      font-weight: 500;
    }
  }
}

.metrics-container {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 8px;
  
  .metric-item {
    text-align: center;
    padding: 8px;
    background: rgba(255, 255, 255, 0.05);
    border-radius: 6px;
    
    .metric-value {
      font-size: 16px;
      font-weight: 700;
      color: #2563eb;
      margin-bottom: 2px;
    }
    
    .metric-label {
      font-size: 10px;
      color: #94a3b8;
    }
  }
}

.parameters-container {
  display: flex;
  flex-direction: column;
  gap: 4px;
  
  .parameter-item {
    display: flex;
    justify-content: space-between;
    font-size: 12px;
    
    .param-name {
      color: #94a3b8;
    }
    
    .param-value {
      color: #f8fafc;
      font-weight: 500;
    }
  }
}

.connection-points {
  .connection-point {
    position: absolute;
    width: 16px;
    height: 16px;
    border-radius: 50%;
    background: #404040;
    border: 2px solid #2563eb;
    cursor: crosshair;
    transition: all 0.2s ease;
    z-index: 10;
    
    &:hover {
      transform: scale(1.2);
      background: #2563eb;
    }
    
    .point-inner {
      width: 6px;
      height: 6px;
      border-radius: 50%;
      background: #f8fafc;
      position: absolute;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
    }
    
    &.input {
      border-color: var(--market-rise);
      
      &:hover {
        background: var(--market-rise);
      }
    }
    
    &.output {
      border-color: #f59e0b;
      
      &:hover {
        background: #f59e0b;
      }
    }
  }
}

.drag-handle {
  position: absolute;
  bottom: 4px;
  right: 4px;
  width: 20px;
  height: 20px;
  cursor: move;
  opacity: 0.5;
  transition: opacity 0.2s ease;
  
  &:hover {
    opacity: 1;
  }
  
  .drag-handle-icon {
    font-size: 12px;
    color: #94a3b8;
    text-align: center;
    line-height: 20px;
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

@keyframes pulse-running {
  0%, 100% {
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
  }
  50% {
    box-shadow: 0 4px 12px rgba(245, 158, 11, 0.3);
  }
}
</style>
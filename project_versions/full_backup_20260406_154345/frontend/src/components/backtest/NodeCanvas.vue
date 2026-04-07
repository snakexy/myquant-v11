<template>
  <div 
    class="node-canvas"
    @mousedown="handleCanvasMouseDown"
    @mousemove="handleCanvasMouseMove"
    @mouseup="handleCanvasMouseUp"
    @wheel="handleCanvasWheel"
    @dragover.prevent
    @drop.prevent="handleCanvasDrop"
    ref="canvasRef"
  >
    <!-- 网格背景 -->
    <svg class="grid-background" :width="canvasWidth" :height="canvasHeight">
      <defs>
        <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
          <path d="M 40 0 L 0 0 0 40" fill="none" stroke="rgba(255, 255, 255, 0.05)" stroke-width="1"/>
        </pattern>
      </defs>
      <rect width="100%" height="100%" fill="url(#grid)" />
    </svg>

    <!-- 连接线层 -->
    <svg class="connections-layer" :width="canvasWidth" :height="canvasHeight">
      <defs>
        <filter :id="`glow-${connection.id}`" v-for="connection in connections" :key="connection.id">
          <feGaussianBlur in="SourceGraphic" stdDeviation="3" result="coloredBlur"/>
          <feMerge>
            <feMergeNode in="coloredBlur"/>
            <feMergeNode in="SourceGraphic"/>
          </feMerge>
        </filter>
      </defs>
      
      <g v-for="connection in connections" :key="connection.id">
        <path
          :d="getConnectionPath(connection)"
          :class="getConnectionClass(connection)"
          :stroke="getConnectionColor(connection)"
          :stroke-width="getConnectionWidth(connection)"
          :stroke-dasharray="getConnectionDashArray(connection)"
          :filter="`url(#glow-${connection.id})`"
          @click="handleConnectionClick(connection)"
        />
        
        <!-- 技术标签 -->
        <text
          :x="getConnectionLabelPosition(connection).x"
          :y="getConnectionLabelPosition(connection).y"
          class="technology-label"
          text-anchor="middle"
        >
          {{ connection.technology }}
        </text>
        
        <!-- 数据流粒子 -->
        <circle
          v-for="(particle, index) in getConnectionParticles(connection)"
          :key="index"
          :cx="particle.x"
          :cy="particle.y"
          r="3"
          :fill="getConnectionColor(connection)"
          class="data-particle"
        >
          <animateMotion
            :dur="particle.duration"
            :path="getConnectionPath(connection)"
            repeatCount="indefinite"
            :begin="particle.delay"
          />
        </circle>
      </g>
    </svg>

    <!-- 节点层 -->
    <div class="nodes-layer" :style="nodesLayerStyle">
      <BaseNode
        v-for="node in nodes"
        :key="node.id"
        :node-data="node"
        :is-selected="selectedNodeId === node.id"
        @node-click="handleNodeClick"
        @node-drag="handleNodeDrag"
        @node-double-click="handleNodeDoubleClick"
        @connection-start="handleConnectionStart"
        @connection-end="handleConnectionEnd"
      />
    </div>

    <!-- 连接创建预览 -->
    <svg 
      v-if="connectionPreview.active"
      class="connection-preview"
      :width="canvasWidth"
      :height="canvasHeight"
    >
      <path
        :d="connectionPreview.path"
        stroke="rgba(37, 99, 235, 0.5)"
        stroke-width="2"
        stroke-dasharray="5,5"
        fill="none"
      />
    </svg>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import BaseNode from './BaseNode.vue'

interface NodeData {
  id: string
  type: 'config' | 'processing' | 'result' | 'metric'
  title: string
  icon: string
  position: { x: number; y: number }
  size: { width: number; height: number }
  status: 'idle' | 'running' | 'completed' | 'error'
  data?: any
  parameters?: Array<{ name: string; value: string }>
  metrics?: Array<{ label: string; value: string | number }>
  showProgress?: boolean
  progress?: number
  showHexagon?: boolean
  hexagonData?: Array<{ label: string; value: number; max: number }>
}

interface ConnectionData {
  id: string
  from: string
  to: string
  type: 'data' | 'control' | 'feedback' | 'error'
  technology?: string
  status: 'active' | 'inactive' | 'error'
}

const props = defineProps<{
  nodes: NodeData[]
  connections: ConnectionData[]
  scale: number
  offset: { x: number; y: number }
}>()

const emit = defineEmits<{
  'node-click': [nodeId: string]
  'node-drag': [nodeId: string, position: { x: number; y: number }]
  'node-double-click': [nodeId: string]
  'connection-create': [connection: ConnectionData]
  'connection-delete': [connectionId: string]
  'canvas-transform': [scale: number, offset: { x: number; y: number }]
  'drop': [event: DragEvent]
}>()

// 响应式数据
const canvasRef = ref<HTMLElement>()
const canvasWidth = ref(2000)
const canvasHeight = ref(2000)
const selectedNodeId = ref<string | null>(null)
const isDragging = ref(false)
const isPanning = ref(false)
const dragStartPos = ref({ x: 0, y: 0 })
const panStartPos = ref({ x: 0, y: 0 })
const currentOffset = ref({ x: 0, y: 0 })
const currentScale = ref(1)

// 连接创建预览
const connectionPreview = ref({
  active: false,
  fromNode: null as NodeData | null,
  fromPoint: null as { x: number; y: number } | null,
  toPoint: null as { x: number; y: number } | null,
  path: ''
})

// 计算属性
const nodesLayerStyle = computed(() => ({
  transform: `translate(${currentOffset.value.x}px, ${currentOffset.value.y}px) scale(${currentScale.value})`,
  transformOrigin: '0 0'
}))

// 连接路径计算
const getConnectionPath = (connection: ConnectionData) => {
  const fromNode = props.nodes.find(n => n.id === connection.from)
  const toNode = props.nodes.find(n => n.id === connection.to)
  
  if (!fromNode || !toNode) return ''
  
  const fromX = fromNode.position.x + fromNode.size.width / 2
  const fromY = fromNode.position.y + fromNode.size.height / 2
  const toX = toNode.position.x + toNode.size.width / 2
  const toY = toNode.position.y + toNode.size.height / 2
  
  // 计算控制点
  const controlPoint1X = fromX + (toX - fromX) * 0.5
  const controlPoint1Y = fromY
  const controlPoint2X = fromX + (toX - fromX) * 0.5
  const controlPoint2Y = toY
  
  return `M ${fromX} ${fromY} C ${controlPoint1X} ${controlPoint1Y}, ${controlPoint2X} ${controlPoint2Y}, ${toX} ${toY}`
}

// 连接样式计算
const getConnectionClass = (connection: ConnectionData) => {
  return `connection-${connection.type} connection-${connection.status}`
}

const getConnectionColor = (connection: ConnectionData) => {
  const colorMap = {
    data: '#2563eb',
    control: '#10b981',
    feedback: '#f59e0b',
    error: '#ef4444'
  }
  return colorMap[connection.type] || '#2563eb'
}

const getConnectionWidth = (connection: ConnectionData) => {
  return connection.type === 'error' ? 3 : 2
}

const getConnectionDashArray = (connection: ConnectionData) => {
  const dashMap = {
    data: '0',
    control: '5,5',
    feedback: '2,2',
    error: '10,5'
  }
  return dashMap[connection.type] || '0'
}

// 连接标签位置
const getConnectionLabelPosition = (connection: ConnectionData) => {
  const fromNode = props.nodes.find(n => n.id === connection.from)
  const toNode = props.nodes.find(n => n.id === connection.to)
  
  if (!fromNode || !toNode) return { x: 0, y: 0 }
  
  const fromX = fromNode.position.x + fromNode.size.width / 2
  const fromY = fromNode.position.y + fromNode.size.height / 2
  const toX = toNode.position.x + toNode.size.width / 2
  const toY = toNode.position.y + toNode.size.height / 2
  
  return {
    x: (fromX + toX) / 2,
    y: (fromY + toY) / 2 - 10
  }
}

// 连接粒子动画
const getConnectionParticles = (connection: ConnectionData) => {
  if (connection.status !== 'active') return []
  
  const fromNode = props.nodes.find(n => n.id === connection.from)
  const toNode = props.nodes.find(n => n.id === connection.to)
  
  if (!fromNode || !toNode) return []
  
  const fromX = fromNode.position.x + fromNode.size.width / 2
  const fromY = fromNode.position.y + fromNode.size.height / 2
  const toX = toNode.position.x + toNode.size.width / 2
  const toY = toNode.position.y + toNode.size.height / 2
  
  const distance = Math.sqrt(Math.pow(toX - fromX, 2) + Math.pow(toY - fromY, 2))
  const duration = Math.max(2, distance / 100)
  
  return [
    {
      x: fromX,
      y: fromY,
      duration: `${duration}s`,
      delay: '0s'
    },
    {
      x: fromX,
      y: fromY,
      duration: `${duration}s`,
      delay: `${duration / 2}s`
    }
  ]
}

// 事件处理
const handleCanvasMouseDown = (event: MouseEvent) => {
  if (event.target === canvasRef.value) {
    isPanning.value = true
    panStartPos.value = { x: event.clientX, y: event.clientY }
    canvasRef.value?.setCursor?.('grabbing')
  }
}

const handleCanvasMouseMove = (event: MouseEvent) => {
  if (isPanning.value) {
    const deltaX = event.clientX - panStartPos.value.x
    const deltaY = event.clientY - panStartPos.value.y
    
    currentOffset.value = {
      x: props.offset.x + deltaX,
      y: props.offset.y + deltaY
    }
    
    emit('canvas-transform', currentScale.value, currentOffset.value)
  }
  
  // 更新连接预览
  if (connectionPreview.value.active && connectionPreview.value.fromPoint) {
    const rect = canvasRef.value?.getBoundingClientRect()
    if (rect) {
      connectionPreview.value.toPoint = {
        x: (event.clientX - rect.left - currentOffset.value.x) / currentScale.value,
        y: (event.clientY - rect.top - currentOffset.value.y) / currentScale.value
      }
      
      if (connectionPreview.value.fromPoint) {
        connectionPreview.value.path = `M ${connectionPreview.value.fromPoint.x} ${connectionPreview.value.fromPoint.y} L ${connectionPreview.value.toPoint.x} ${connectionPreview.value.toPoint.y}`
      }
    }
  }
}

const handleCanvasMouseUp = () => {
  isPanning.value = false
  canvasRef.value?.setCursor?.('default')
}

const handleCanvasWheel = (event: WheelEvent) => {
  event.preventDefault()
  
  const scaleFactor = event.deltaY > 0 ? 0.9 : 1.1
  const newScale = Math.max(0.1, Math.min(3, currentScale.value * scaleFactor))
  
  currentScale.value = newScale
  emit('canvas-transform', currentScale.value, currentOffset.value)
}

const handleCanvasDrop = (event: DragEvent) => {
  event.preventDefault()
  emit('drop', event)
}

const handleNodeClick = (nodeId: string) => {
  selectedNodeId.value = nodeId
  emit('node-click', nodeId)
}

const handleNodeDrag = (nodeId: string, position: { x: number; y: number }) => {
  emit('node-drag', nodeId, position)
}

const handleNodeDoubleClick = (nodeId: string) => {
  emit('node-double-click', nodeId)
}

const handleConnectionStart = (pointId: string, nodeId: string) => {
  const node = props.nodes.find(n => n.id === nodeId)
  if (node) {
    connectionPreview.value = {
      active: true,
      fromNode: node,
      fromPoint: {
        x: node.position.x + node.size.width / 2,
        y: node.position.y + node.size.height / 2
      },
      toPoint: null,
      path: ''
    }
  }
}

const handleConnectionEnd = (pointId: string, nodeId: string) => {
  if (connectionPreview.value.active && connectionPreview.value.fromNode) {
    const fromNode = connectionPreview.value.fromNode
    const toNode = props.nodes.find(n => n.id === nodeId)
    
    if (toNode && fromNode.id !== toNode.id) {
      const newConnection: ConnectionData = {
        id: `conn-${Date.now()}`,
        from: fromNode.id,
        to: toNode.id,
        type: 'data',
        technology: 'DataFlow',
        status: 'active'
      }
      
      emit('connection-create', newConnection)
    }
  }
  
  // 重置连接预览
  connectionPreview.value = {
    active: false,
    fromNode: null,
    fromPoint: null,
    toPoint: null,
    path: ''
  }
}

const handleConnectionClick = (connection: ConnectionData) => {
  // 可以实现连接点击事件
  console.log('连接点击:', connection)
}

// 重置变换
const resetTransform = () => {
  currentScale.value = 1
  currentOffset.value = { x: 0, y: 0 }
  emit('canvas-transform', currentScale.value, currentOffset.value)
}

// 监听props变化
watch(() => props.scale, (newScale) => {
  currentScale.value = newScale
})

watch(() => props.offset, (newOffset) => {
  currentOffset.value = { ...newOffset }
})

// 生命周期
onMounted(() => {
  // 初始化画布大小
  updateCanvasSize()
  window.addEventListener('resize', updateCanvasSize)
})

onUnmounted(() => {
  window.removeEventListener('resize', updateCanvasSize)
})

const updateCanvasSize = () => {
  if (canvasRef.value) {
    const rect = canvasRef.value.parentElement?.getBoundingClientRect()
    if (rect) {
      canvasWidth.value = rect.width
      canvasHeight.value = rect.height
    }
  }
}
</script>

<style lang="scss" scoped>
.node-canvas {
  position: relative;
  width: 100%;
  height: 100%;
  background: #0a0a0f;
  overflow: hidden;
  cursor: grab;
  
  &:active {
    cursor: grabbing;
  }
}

.grid-background {
  position: absolute;
  top: 0;
  left: 0;
  pointer-events: none;
}

.connections-layer {
  position: absolute;
  top: 0;
  left: 0;
  pointer-events: none;
  
  .connection-data {
    stroke: #2563eb;
    stroke-width: 2;
    fill: none;
    cursor: pointer;
    pointer-events: stroke;
    transition: all 0.3s ease;
    
    &:hover {
      stroke-width: 3;
      filter: drop-shadow(0 0 8px rgba(37, 99, 235, 0.5));
    }
  }
  
  .connection-control {
    stroke: #10b981;
    stroke-width: 2;
    stroke-dasharray: 5,5;
    fill: none;
    
    &:hover {
      stroke-width: 3;
    }
  }
  
  .connection-feedback {
    stroke: #f59e0b;
    stroke-width: 2;
    stroke-dasharray: 2,2;
    fill: none;
    
    &:hover {
      stroke-width: 3;
    }
  }
  
  .connection-error {
    stroke: #ef4444;
    stroke-width: 3;
    stroke-dasharray: 10,5;
    fill: none;
    
    &:hover {
      stroke-width: 4;
    }
  }
  
  .connection-active {
    opacity: 1;
  }
  
  .connection-inactive {
    opacity: 0.5;
  }
  
  .technology-label {
    fill: #94a3b8;
    font-size: 10px;
    font-weight: 500;
    pointer-events: none;
  }
  
  .data-particle {
    pointer-events: none;
  }
}

.connection-preview {
  position: absolute;
  top: 0;
  left: 0;
  pointer-events: none;
  z-index: 1000;
}

.nodes-layer {
  position: absolute;
  top: 0;
  left: 0;
  transform-origin: 0 0;
}
</style>
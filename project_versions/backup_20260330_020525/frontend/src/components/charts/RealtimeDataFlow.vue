<template>
  <div class="realtime-data-flow">
    <div class="flow-header">
      <n-space>
        <n-statistic label="数据流速度" :value="flowRate">
          <template #suffix>条/秒</template>
        </n-statistic>
        <n-statistic label="总处理量" :value="totalProcessed">
          <template #suffix>条</template>
        </n-statistic>
        <n-statistic label="错误率" :value="errorRate" :precision="2">
          <template #suffix>%</template>
        </n-statistic>
        <n-switch v-model:value="isPaused" @update:value="togglePause">
          <template #checked>暂停</template>
          <template #unchecked>运行</template>
        </n-switch>
      </n-space>
    </div>
    
    <div class="flow-visualization">
      <svg ref="flowSvg" class="flow-svg" :width="width" :height="height">
        <!-- 定义渐变 -->
        <defs>
          <linearGradient id="dataFlowGradient" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" style="stop-color:#00ff88;stop-opacity:1" />
            <stop offset="50%" style="stop-color:#ffaa00;stop-opacity:1" />
            <stop offset="100%" style="stop-color:#0088ff;stop-opacity:1" />
          </linearGradient>
          
          <filter id="glow">
            <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
            <feMerge>
              <feMergeNode in="coloredBlur"/>
              <feMergeNode in="SourceGraphic"/>
            </feMerge>
          </filter>
        </defs>
        
        <!-- 数据流管道 -->
        <g class="flow-pipes">
          <path
            v-for="pipe in flowPipes"
            :key="pipe.id"
            :d="pipe.path"
            stroke="url(#dataFlowGradient)"
            stroke-width="3"
            fill="none"
            filter="url(#glow)"
            class="flow-pipe"
          />
          
          <!-- 数据粒子 -->
          <circle
            v-for="particle in pipe.particles"
            :key="particle.id"
            :cx="particle.x"
            :cy="particle.y"
            r="4"
            fill="#00ff88"
            class="data-particle"
            :class="{ 'error-particle': particle.hasError }"
          />
        </g>
        
        <!-- 节点 -->
        <g class="flow-nodes">
          <g
            v-for="node in flowNodes"
            :key="node.id"
            :transform="`translate(${node.x}, ${node.y})`"
            class="flow-node"
            @click="selectNode(node)"
          >
            <!-- 节点背景 -->
            <circle
              :r="node.radius"
              :fill="node.color"
              :stroke="node.borderColor"
              stroke-width="2"
              class="node-circle"
              :class="{ 'node-error': node.hasError, 'node-active': node.isActive }"
            />
            
            <!-- 节点图标 -->
            <text
              x="0"
              y="5"
              text-anchor="middle"
              fill="white"
              font-size="12"
              font-weight="bold"
              class="node-icon"
            >
              {{ node.icon }}
            </text>
            
            <!-- 节点标签 -->
            <text
              x="0"
              :y="node.radius + 15"
              text-anchor="middle"
              fill="#94a3b8"
              font-size="11"
              class="node-label"
            >
              {{ node.label }}
            </text>
            
            <!-- 状态指示器 -->
            <circle
              v-if="node.isActive"
              :r="node.radius + 5"
              fill="none"
              stroke="#10b981"
              stroke-width="2"
              class="status-indicator"
            />
          </g>
        </g>
      </svg>
    </div>
    
    <!-- 数据流详情面板 -->
    <div v-if="selectedNode" class="flow-details">
      <n-card title="节点详情" size="small" closable @close="selectedNode = null">
        <n-descriptions :column="2" size="small">
          <n-descriptions-item label="节点名称">
            {{ selectedNode.label }}
          </n-descriptions-item>
          <n-descriptions-item label="节点类型">
            <n-tag :type="selectedNode.type" size="small">
              {{ selectedNode.type }}
            </n-tag>
          </n-descriptions-item>
          <n-descriptions-item label="状态">
            <n-tag :type="selectedNode.hasError ? 'error' : 'success'" size="small">
              {{ selectedNode.hasError ? '错误' : '正常' }}
            </n-tag>
          </n-descriptions-item>
          <n-descriptions-item label="处理速度">
            {{ selectedNode.processingRate }} 条/秒
          </n-descriptions-item>
          <n-descriptions-item label="累计处理">
            {{ selectedNode.totalProcessed.toLocaleString() }} 条
          </n-descriptions-item>
          <n-descriptions-item label="错误数量" :span="2">
            {{ selectedNode.errorCount }}
          </n-descriptions-item>
        </n-descriptions>
      </n-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed, watch } from 'vue'
import { NStatistic, NSpace, NSwitch, NCard, NDescriptions, NDescriptionsItem, NTag } from 'naive-ui'

interface DataParticle {
  id: string
  x: number
  y: number
  hasError: boolean
  progress: number
}

interface FlowPipe {
  id: string
  path: string
  particles: DataParticle[]
  startX: number
  startY: number
  endX: number
  endY: number
}

interface FlowNode {
  id: string
  label: string
  type: 'data_source' | 'processor' | 'model' | 'output'
  x: number
  y: number
  radius: number
  color: string
  borderColor: string
  icon: string
  isActive: boolean
  hasError: boolean
  processingRate: number
  totalProcessed: number
  errorCount: number
}

interface Props {
  width?: string
  height?: string
  autoRefresh?: boolean
  refreshInterval?: number
}

const props = withDefaults(defineProps<Props>(), {
  width: '100%',
  height: '400px',
  autoRefresh: true,
  refreshInterval: 1000
})

const emit = defineEmits<{
  nodeClick: [node: FlowNode]
  error: [node: FlowNode, error: any]
}>()

const flowSvg = ref<SVGElement>()
const isPaused = ref(false)
const selectedNode = ref<FlowNode | null>(null)
const animationFrameId = ref<number>()

// 模拟数据
const flowRate = ref(1250)
const totalProcessed = ref(158000)
const errorRate = ref(0.12)

// 创建流程节点
const flowNodes = ref<FlowNode[]>([
  {
    id: 'data-source',
    label: '数据源',
    type: 'data_source',
    x: 100,
    y: 200,
    radius: 30,
    color: '#e65100',
    borderColor: '#f59e0b',
    icon: '📊',
    isActive: true,
    hasError: false,
    processingRate: 450,
    totalProcessed: 45000,
    errorCount: 2
  },
  {
    id: 'processor-1',
    label: '数据清洗',
    type: 'processor',
    x: 250,
    y: 200,
    radius: 25,
    color: '#01579b',
    borderColor: '#0ea5e9',
    icon: '🔄',
    isActive: true,
    hasError: false,
    processingRate: 420,
    totalProcessed: 42000,
    errorCount: 1
  },
  {
    id: 'processor-2',
    label: '特征工程',
    type: 'processor',
    x: 400,
    y: 200,
    radius: 25,
    color: '#01579b',
    borderColor: '#0ea5e9',
    icon: '⚙️',
    isActive: true,
    hasError: false,
    processingRate: 380,
    totalProcessed: 38000,
    errorCount: 0
  },
  {
    id: 'model',
    label: 'AI模型',
    type: 'model',
    x: 550,
    y: 200,
    radius: 30,
    color: '#1b5e20',
    borderColor: '#10b981',
    icon: '🤖',
    isActive: true,
    hasError: false,
    processingRate: 0,
    totalProcessed: 33000,
    errorCount: 0
  },
  {
    id: 'output',
    label: '输出结果',
    type: 'output',
    x: 700,
    y: 200,
    radius: 25,
    color: '#00695c',
    borderColor: '#059669',
    icon: '📈',
    isActive: true,
    hasError: true,
    processingRate: 0,
    totalProcessed: 32800,
    errorCount: 5
  }
])

// 创建数据流管道
const flowPipes = ref<FlowPipe[]>([])

// 生成管道路径
const generatePipePath = (startNode: FlowNode, endNode: FlowNode): string => {
  const startX = startNode.x + startNode.radius
  const startY = startNode.y
  const endX = endNode.x - endNode.radius
  const endY = endNode.y
  
  // 创建曲线路径
  const controlX = (startX + endX) / 2
  const controlY = startY - 30
  
  return `M ${startX} ${startY} Q ${controlX} ${controlY} ${endX} ${endY}`
}

// 初始化管道
const initializePipes = () => {
  const pipes: FlowPipe[] = [
    {
      id: 'pipe-1',
      path: generatePipePath(flowNodes.value[0], flowNodes.value[1]),
      particles: [],
      startX: flowNodes.value[0].x + flowNodes.value[0].radius,
      startY: flowNodes.value[0].y,
      endX: flowNodes.value[1].x - flowNodes.value[1].radius,
      endY: flowNodes.value[1].y
    },
    {
      id: 'pipe-2',
      path: generatePipePath(flowNodes.value[1], flowNodes.value[2]),
      particles: [],
      startX: flowNodes.value[1].x + flowNodes.value[1].radius,
      startY: flowNodes.value[1].y,
      endX: flowNodes.value[2].x - flowNodes.value[2].radius,
      endY: flowNodes.value[2].y
    },
    {
      id: 'pipe-3',
      path: generatePipePath(flowNodes.value[2], flowNodes.value[3]),
      particles: [],
      startX: flowNodes.value[2].x + flowNodes.value[2].radius,
      startY: flowNodes.value[2].y,
      endX: flowNodes.value[3].x - flowNodes.value[3].radius,
      endY: flowNodes.value[3].y
    },
    {
      id: 'pipe-4',
      path: generatePipePath(flowNodes.value[3], flowNodes.value[4]),
      particles: [],
      startX: flowNodes.value[3].x + flowNodes.value[3].radius,
      startY: flowNodes.value[3].y,
      endX: flowNodes.value[4].x - flowNodes.value[4].radius,
      endY: flowNodes.value[4].y
    }
  ]
  
  flowPipes.value = pipes
}

// 创建数据粒子
const createDataParticle = (pipe: FlowPipe, hasError: boolean = false): DataParticle => {
  return {
    id: `particle-${Date.now()}-${Math.random()}`,
    x: pipe.startX,
    y: pipe.startY,
    hasError,
    progress: 0
  }
}

// 动画循环
const animate = () => {
  if (isPaused.value) return
  
  // 更新粒子位置
  flowPipes.value.forEach(pipe => {
    // 添加新粒子
    if (Math.random() < 0.1) {
      const hasError = Math.random() < 0.05 // 5% 错误率
      pipe.particles.push(createDataParticle(pipe, hasError))
    }
    
    // 更新现有粒子
    pipe.particles = pipe.particles.filter(particle => {
      particle.progress += 0.02
      
      if (particle.progress >= 1) {
        return false // 移除到达终点的粒子
      }
      
      // 计算粒子位置（沿贝塞尔曲线移动）
      const t = particle.progress
      const startX = pipe.startX
      const startY = pipe.startY
      const endX = pipe.endX
      const endY = pipe.endY
      const controlX = (startX + endX) / 2
      const controlY = startY - 30
      
      // 二次贝塞尔曲线公式
      particle.x = (1-t)*(1-t)*startX + 2*(1-t)*t*controlX + t*t*endX
      particle.y = (1-t)*(1-t)*startY + 2*(1-t)*t*controlY + t*t*endY
      
      return true
    })
  })
  
  // 更新统计数据
  updateStatistics()
  
  animationFrameId.value = requestAnimationFrame(animate)
}

// 更新统计数据
const updateStatistics = () => {
  // 模拟数据变化
  if (Math.random() < 0.1) {
    flowRate.value = Math.max(1000, flowRate.value + (Math.random() - 0.5) * 100)
    totalProcessed.value += Math.floor(flowRate.value / 10)
    errorRate.value = Math.max(0, Math.min(1, errorRate.value + (Math.random() - 0.5) * 0.01))
  }
}

// 选择节点
const selectNode = (node: FlowNode) => {
  selectedNode.value = node
  emit('nodeClick', node)
  
  if (node.hasError) {
    emit('error', node, new Error('节点处理错误'))
  }
}

// 暂停/恢复
const togglePause = (paused: boolean) => {
  isPaused.value = paused
  if (!paused) {
    animate()
  }
}

// 初始化
onMounted(() => {
  initializePipes()
  
  if (props.autoRefresh) {
    animate()
  }
})

onUnmounted(() => {
  if (animationFrameId.value) {
    cancelAnimationFrame(animationFrameId.value)
  }
})

// 暴露方法
defineExpose({
  pause: () => togglePause(true),
  resume: () => togglePause(false),
  getNodes: () => flowNodes.value,
  getPipes: () => flowPipes.value
})
</script>

<style lang="scss" scoped>
.realtime-data-flow {
  width: 100%;
  height: 100%;
  
  .flow-header {
    padding: 16px;
    background: rgba(15, 23, 42, 0.8);
    backdrop-filter: blur(10px);
    border-bottom: 1px solid rgba(148, 163, 184, 0.2);
  }
  
  .flow-visualization {
    position: relative;
    width: v-bind(width);
    height: v-bind(height);
    background: rgba(15, 23, 42, 0.6);
    backdrop-filter: blur(10px);
    border-radius: 8px;
    overflow: hidden;
    
    .flow-svg {
      width: 100%;
      height: 100%;
      
      .flow-pipe {
        filter: drop-shadow(0 0 8px rgba(0, 255, 136, 0.3));
        animation: pulse 2s ease-in-out infinite;
      }
      
      .data-particle {
        filter: drop-shadow(0 0 4px rgba(0, 255, 136, 0.6));
        transition: all 0.3s ease;
        
        &.error-particle {
          fill: #ff0066;
          filter: drop-shadow(0 0 4px rgba(255, 0, 102, 0.6));
        }
      }
      
      .flow-node {
        cursor: pointer;
        transition: all 0.3s ease;
        
        &:hover {
          transform: scale(1.1);
        }
        
        .node-circle {
          transition: all 0.3s ease;
          
          &.node-error {
            stroke: #ef4444;
            stroke-width: 3;
            animation: errorPulse 1s ease-in-out infinite;
          }
          
          &.node-active {
            stroke: #10b981;
            stroke-width: 3;
            animation: activePulse 2s ease-in-out infinite;
          }
        }
        
        .status-indicator {
          animation: rotate 2s linear infinite;
        }
      }
    }
  }
  
  .flow-details {
    position: absolute;
    top: 80px;
    right: 16px;
    z-index: 100;
    min-width: 280px;
    background: rgba(15, 23, 42, 0.9);
    backdrop-filter: blur(10px);
    border-radius: 8px;
    border: 1px solid rgba(148, 163, 184, 0.2);
  }
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.7;
  }
}

@keyframes errorPulse {
  0%, 100% {
    stroke: #ef4444;
    stroke-width: 3;
  }
  50% {
    stroke: #dc2626;
    stroke-width: 4;
  }
}

@keyframes activePulse {
  0%, 100% {
    stroke: #10b981;
    stroke-width: 3;
  }
  50% {
    stroke: #059669;
    stroke-width: 4;
  }
}

@keyframes rotate {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
</style>
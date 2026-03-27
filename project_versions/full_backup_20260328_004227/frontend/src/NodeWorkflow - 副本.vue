<template>
  <div class="node-workflow">
    <!-- 沉浸式背景 -->
    <div class="immersive-background">
      <div class="particle-system" ref="particleSystem"></div>
      <div class="data-stream-overlay"></div>
      <div class="grid-pattern"></div>
    </div>

    <header class="workflow-header">
      <h1>节点工作流</h1>
      <button class="btn-back" @click="goBack">返回研究</button>
    </header>

    <main class="main-content">
      <div class="workflow-canvas">
        <!-- 连线层 - 在画布容器外面 -->
        <svg
          class="connections-layer"
          :style="{
            position: 'absolute',
            top: '0',
            left: '0',
            width: '100%',
            height: '100%',
            pointerEvents: 'none'
          }"
        >
          <defs>
          </defs>
          <g
            :style="{
              transform: `translate(${canvasOffset.x}px, ${canvasOffset.y}px) scale(${canvasScale})`,
              transformOrigin: '0 0'
            }"
          >
            <path
              v-for="connection in connections"
              :key="`${connection.from}-${connection.to}`"
              :d="getConnectionPath(connection)"
              stroke="#8b5cf6"
              stroke-width="2"
              fill="none"
              stroke-linecap="round"
              opacity="0.7"
            />
          </g>
        </svg>

        <div
          class="canvas-container"
          :style="{
            transform: `translate(${canvasOffset.x}px, ${canvasOffset.y}px) scale(${canvasScale})`,
            transformOrigin: '0 0'
          }"
          @mousedown="startCanvasDrag"
          @wheel="handleWheel"
        >

          <!-- 节点 -->
          <div
            v-for="node in nodes"
            :key="node.id"
            class="workflow-node"
            :data-node-id="node.id"
            :class="{ 'active': activeNode === node.id, 'dragging': isDragging && draggedNode === node.id }"
            :style="{
              position: 'absolute',
              left: `${nodePositions[node.id]?.x || node.x}px`,
              top: `${nodePositions[node.id]?.y || node.y}px`,
              transition: isDragging && draggedNode === node.id ? 'none' : 'all 0.2s ease'
            }"
            @mousedown="startDrag($event, node)"
            @click="selectNode(node.id)"
          >
            <!-- 节点输入端口（上方） -->
            <div class="node-port node-input-port" @mouseenter="onPortHover" @mouseleave="onPortLeave"></div>

          <!-- 节点输出端口（下方） -->
            <div class="node-port node-output-port" @mouseenter="onPortHover" @mouseleave="onPortLeave"></div>

            <div class="node-header">
              <div class="node-icon">{{ node.icon }}</div>
              <div class="node-title">{{ node.title }}</div>
            </div>
            <div class="node-description">{{ node.description }}</div>

            <!-- 数据内容区域 -->
            <div class="node-content" v-if="node.data">
              <!-- 统计数据 -->
              <div v-if="node.data.type === 'stats'" class="stats-container">
                <div v-for="(value, key) in node.data.content" :key="key" class="stat-item">
                  <span class="stat-label">{{ formatStatLabel(key) }}:</span>
                  <span class="stat-value" :style="{ color: getValueColor(value) }">{{ formatStatValue(value) }}</span>
                </div>
              </div>

              <!-- 表格数据 -->
              <div v-else-if="node.data.type === 'table'" class="table-container">
                <div v-for="(row, index) in node.data.content" :key="index" class="table-row">
                  <div v-for="(value, key) in row" :key="key" class="table-cell" :style="{ color: formatTableValue(value).color }">
                    {{ formatTableValue(value).text }}
                  </div>
                </div>
              </div>

              <!-- 文本数据 -->
              <div v-else-if="node.data.type === 'text'" class="text-container">
                {{ node.data.content }}
              </div>

              <!-- 列表数据 -->
              <div v-else-if="node.data.type === 'list'" class="list-container">
                <div v-for="(item, index) in node.data.content" :key="index" class="list-item">
                  {{ item }}
                </div>
              </div>

              <!-- 图表数据 -->
              <div v-else-if="node.data.type === 'chart'" class="chart-container">
                <div class="chart-summary">
                  <div class="chart-item">
                    <span class="chart-label">识别模式:</span>
                    <div class="chart-patterns">
                      <span v-for="(pattern, index) in node.data.content.patterns" :key="index" class="pattern-tag">
                        {{ pattern }}
                      </span>
                    </div>
                  </div>
                  <div class="chart-stats">
                    <div class="chart-stat">
                      <span>准确率: </span>
                      <span :style="{ color: node.data.content.accuracy >= 90 ? '#ef4444' : node.data.content.accuracy >= 80 ? '#f59e0b' : '#6b7280' }">
                        {{ node.data.content.accuracy }}%
                      </span>
                    </div>
                    <div class="chart-stat">
                      <span>置信度: </span>
                      <span :style="{ color: node.data.content.confidence >= 90 ? '#ef4444' : node.data.content.confidence >= 80 ? '#f59e0b' : '#6b7280' }">
                        {{ node.data.content.confidence }}%
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

interface Node {
  id: string
  x: number
  y: number
  icon: string
  title: string
  description: string
  data?: {
    type: 'chart' | 'table' | 'stats' | 'text' | 'list'
    content: any
  }
}

// 节点数据
const nodes = ref<Node[]>([
  {
    id: 'data-acquisition',
    x: 100, y: 100,
    icon: '📈',
    title: '数据获取',
    description: '获取市场数据',
    data: {
      type: 'stats',
      content: {
        totalStocks: 4856,
        dataPoints: '2.3M',
        lastUpdate: '2024-12-15',
        sources: ['上交所', '深交所', '北交所']
      }
    }
  },
  {
    id: 'stock-selection',
    x: 350, y: 100,
    icon: '📊',
    title: '股票选择',
    description: '选择股票池',
    data: {
      type: 'table',
      content: [
        { name: '平安银行', code: '000001', change: '+2.34%', volume: '1.2亿' },
        { name: '宁德时代', code: '300750', change: '+1.89%', volume: '8900万' },
        { name: '比亚迪', code: '002594', change: '-0.45%', volume: '6700万' }
      ]
    }
  },
  {
    id: 'data-cleaning',
    x: 600, y: 100,
    icon: '🧹',
    title: '数据清洗',
    description: '清洗和预处理',
    data: {
      type: 'stats',
      content: {
        duplicateRecords: 234,
        missingValues: 1256,
        outliers: 89,
        cleanRate: '98.5%'
      }
    }
  },
  {
    id: 'feature-engineering',
    x: 100, y: 280,
    icon: '⚙️',
    title: '特征工程',
    description: '提取特征',
    data: {
      type: 'list',
      content: [
        '技术指标: MA, MACD, RSI',
        '基本面指标: PE, PB, ROE',
        '市场情绪指标: 换手率, 涨跌幅'
      ]
    }
  },
  {
    id: 'pattern-recognition',
    x: 350, y: 280,
    icon: '🔍',
    title: '模式识别',
    description: '识别模式',
    data: {
      type: 'chart',
      content: {
        patterns: ['上升趋势', '震荡整理', '突破形态'],
        accuracy: 87.5,
        confidence: 92.3
      }
    }
  },
  {
    id: 'ai-assistant',
    x: 600, y: 280,
    icon: '🤖',
    title: 'AI助手',
    description: 'AI分析辅助',
    data: {
      type: 'text',
      content: '基于深度学习的市场预测模型已训练完成，准确率85.6%，建议关注科技板块机会'
    }
  },
  {
    id: 'strategy-conception',
    x: 100, y: 460,
    icon: '💡',
    title: '策略构思',
    description: '策略设计',
    data: {
      type: 'list',
      content: [
        '动量策略: 中短期趋势跟踪',
        '均值回归: 超跌反弹机会',
        '行业轮动: 季度板块切换'
      ]
    }
  },
  {
    id: 'model-training',
    x: 350, y: 460,
    icon: '🧠',
    title: '模型训练',
    description: '训练模型',
    data: {
      type: 'stats',
      content: {
        epochs: 1000,
        accuracy: '85.6%',
        loss: 0.234,
        bestScore: 0.892
      }
    }
  },
  {
    id: 'preliminary-validation',
    x: 600, y: 460,
    icon: '✅',
    title: '初步验证',
    description: '验证策略',
    data: {
      type: 'table',
      content: [
        { metric: '夏普比率', value: '1.85', status: '优秀' },
        { metric: '最大回撤', value: '-12.3%', status: '良好' },
        { metric: '年化收益', value: '24.7%', status: '优秀' }
      ]
    }
  }
])

// 拖拽状态
const isDragging = ref(false)
const draggedNode = ref<string | null>(null)
const dragOffset = reactive({ x: 0, y: 0 })

// 画布控制状态
const canvasScale = ref(1)
const canvasOffset = reactive({ x: 200, y: 100 }) // 初始偏移，调整到更合适的位置
const isCanvasDragging = ref(false)
const canvasDragStart = reactive({ x: 0, y: 0 })
const canvasOffsetStart = reactive({ x: 0, y: 0 })

// 连线定义
const connections = ref([
  { from: 'data-acquisition', to: 'stock-selection' },
  { from: 'stock-selection', to: 'data-cleaning' },
  { from: 'data-cleaning', to: 'feature-engineering' },
  { from: 'feature-engineering', to: 'pattern-recognition' },
  { from: 'pattern-recognition', to: 'ai-assistant' },
  { from: 'ai-assistant', to: 'strategy-conception' },
  { from: 'strategy-conception', to: 'model-training' },
  { from: 'model-training', to: 'preliminary-validation' }
])

// 活跃节点
const activeNode = ref<string>('')

// 节点位置状态（响应式）
const nodePositions = ref<Record<string, { x: number; y: number; scale: number; isExpanded: boolean }>>({})

// 获取节点的实际尺寸
const getNodeDimensions = (nodeId: string) => {
  // 查找实际的DOM元素
  const nodeElement = document.querySelector(`[data-node-id="${nodeId}"]`) as HTMLElement
  if (nodeElement) {
    return {
      width: nodeElement.offsetWidth,
      height: nodeElement.offsetHeight
    }
  }

  // 回退到估算值
  const node = nodes.value.find(n => n.id === nodeId)
  if (!node) return { width: 220, height: 80 }

  // 根据数据内容估算尺寸
  const nodeWidth = node.data ? 280 : 220
  const nodeHeight = node.data ? 160 : 80

  return { width: nodeWidth, height: nodeHeight }
}

// 获取节点的输出位置（下方中间）
const getNodeOutputPosition = (nodeId: string) => {
  const nodePos = nodePositions.value[nodeId]
  if (!nodePos) return { x: 0, y: 0 }

  const dimensions = getNodeDimensions(nodeId)

  return {
    x: nodePos.x + dimensions.width / 2,
    y: nodePos.y + dimensions.height
  }
}

// 获取节点的输入位置（上方中间）
const getNodeInputPosition = (nodeId: string) => {
  const nodePos = nodePositions.value[nodeId]
  if (!nodePos) return { x: 0, y: 0 }

  const dimensions = getNodeDimensions(nodeId)

  return {
    x: nodePos.x + dimensions.width / 2,
    y: nodePos.y
  }
}

// 智能端口检测 - 根据节点位置确定最佳连接方向
const detectOptimalPorts = (fromNodeId: string, toNodeId: string) => {
  const fromNode = nodePositions.value[fromNodeId]
  const toNode = nodePositions.value[toNodeId]

  if (!fromNode || !toNode) {
    return { fromPort: 'right', toPort: 'left' }
  }

  // 获取节点中心点
  const fromCenterX = fromNode.x + 140 // 假设节点宽度280
  const fromCenterY = fromNode.y + 80  // 假设节点高度160
  const toCenterX = toNode.x + 140
  const toCenterY = toNode.y + 80

  // 计算方向向量
  const dx = toCenterX - fromCenterX
  const dy = toCenterY - fromCenterY

  // 确定主要方向
  const horizontalDistance = Math.abs(dx)
  const verticalDistance = Math.abs(dy)
  const isHorizontalPrimary = horizontalDistance > verticalDistance

  // 根据相对位置确定端口
  let fromPort: string, toPort: string

  if (isHorizontalPrimary) {
    // 水平连接为主
    if (dx > 0) {
      // from在左边，to在右边
      fromPort = 'right'
      toPort = 'left'
    } else {
      // from在右边，to在左边
      fromPort = 'left'
      toPort = 'right'
    }
  } else {
    // 垂直连接为主
    if (dy > 0) {
      // from在上边，to在下边
      fromPort = 'bottom'
      toPort = 'top'
    } else {
      // from在下边，to在上边
      fromPort = 'top'
      toPort = 'bottom'
    }
  }

  return { fromPort, toPort }
}

// 获取节点的端口位置
const getPortPosition = (nodeId: string, port: string) => {
  const nodePos = nodePositions.value[nodeId]
  if (!nodePos) return { x: 0, y: 0 }

  const nodeWidth = 280 // 节点宽度
  const nodeHeight = 160 // 节点高度
  const portSize = 12 // 端口大小

  // 根据端口类型计算位置
  switch (port) {
    case 'left':
      return {
        x: nodePos.x,
        y: nodePos.y + nodeHeight / 2
      }
    case 'right':
      return {
        x: nodePos.x + nodeWidth,
        y: nodePos.y + nodeHeight / 2
      }
    case 'top':
      return {
        x: nodePos.x + nodeWidth / 2,
        y: nodePos.y
      }
    case 'bottom':
      return {
        x: nodePos.x + nodeWidth / 2,
        y: nodePos.y + nodeHeight
      }
    default:
      return {
        x: nodePos.x + nodeWidth / 2,
        y: nodePos.y + nodeHeight / 2
      }
  }
}

// 连线路径计算 - 简洁优雅的贝塞尔曲线
const getConnectionPath = (connection: { from: string; to: string }) => {
  const fromNode = nodePositions.value[connection.from]
  const toNode = nodePositions.value[connection.to]

  if (!fromNode || !toNode) {
    return ''
  }

  // 获取实际的节点尺寸
  const getNodeActualDimensions = (nodeId: string) => {
    const nodeElement = document.querySelector(`[data-node-id="${nodeId}"]`) as HTMLElement
    if (nodeElement) {
      return {
        width: nodeElement.offsetWidth,
        height: nodeElement.offsetHeight
      }
    }
    return { width: 280, height: 160 }
  }

  const fromDimensions = getNodeActualDimensions(connection.from)
  const toDimensions = getNodeActualDimensions(connection.to)

  // 计算连接点 - 从上方中间到下方中间
  const fromX = fromNode.x + fromDimensions.width / 2
  const fromY = fromNode.y + fromDimensions.height
  const toX = toNode.x + toDimensions.width / 2
  const toY = toNode.y

  // 简单优雅的贝塞尔曲线
  const dx = toX - fromX
  const dy = toY - fromY

  // 计算控制点，创建平滑的弧线
  const controlPointOffset = Math.min(Math.abs(dy) * 0.5, 100)
  const midX = (fromX + toX) / 2
  const midY = (fromY + toY) / 2

  // 如果节点水平对齐较多，使用垂直方向的曲线
  if (Math.abs(dx) < 50) {
    return `M ${fromX} ${fromY}
            Q ${fromX + 30} ${midY}, ${midX} ${toY}`
  }

  // 横平竖直的S型直线连接（L型路径）
  // 根据节点相对位置决定路径
  if (Math.abs(toX - fromX) > 50) {
    // 水平距离较大，使用L型路径
    if (toX > fromX) {
      // 目标节点在右边，先向下再向右再向上
      const arrowX = fromX + (toX - fromX) * 0.75 // 箭头在水平段75%位置，避开转角
      return `M ${fromX} ${fromY}
              L ${fromX} ${midY}
              L ${arrowX} ${midY}
              L ${toX} ${midY}
              L ${toX} ${toY}`
    } else {
      // 目标节点在左边，先向下再向左再向上
      const arrowX = toX + (fromX - toX) * 0.75 // 箭头在水平段75%位置，避开转角
      return `M ${fromX} ${fromY}
              L ${fromX} ${midY}
              L ${arrowX} ${midY}
              L ${toX} ${midY}
              L ${toX} ${toY}`
    }
  } else {
    // 垂直对齐较多，使用更简单的路径
    const arrowY = fromY + (toY - fromY) * 0.75 // 箭头在垂直段75%位置，避开转角
    return `M ${fromX} ${fromY}
            L ${midX} ${fromY}
            L ${midX} ${arrowY}
            L ${midX} ${toY}
            L ${toX} ${toY}`
  }
}

// 创建智能路径，避开节点
const createSmartPath = (
  fromX: number,
  fromY: number,
  toX: number,
  toY: number,
  nodeBounds: Array<{ id: string; x: number; y: number; width: number; height: number }>
): string => {
  const margin = 25 // 节点周围的边距

  // 判断点是否在节点内
  const isInsideNode = (x: number, y: number) => {
    return nodeBounds.some(node =>
      x >= node.x - margin &&
      x <= node.x + node.width + margin &&
      y >= node.y - margin &&
      y <= node.y + node.height + margin
    )
  }

  // 判断线段是否与节点相交
  const lineIntersectsNode = (x1: number, y1: number, x2: number, y2: number) => {
    return nodeBounds.some(node => {
      // 扩展节点的边界框
      const expandedLeft = node.x - margin
      const expandedRight = node.x + node.width + margin
      const expandedTop = node.y - margin
      const expandedBottom = node.y + node.height + margin

      // 检查线段是否与扩展的边界框相交
      return !(x2 < expandedLeft || x1 > expandedRight ||
               y2 < expandedTop || y1 > expandedBottom)
    })
  }

  // 如果直线连接不穿过节点，使用直线
  if (!lineIntersectsNode(fromX, fromY, toX, toY)) {
    return `M ${fromX} ${fromY} L ${toX} ${toY}`
  }

  // 计算方向和距离
  const horizontalDistance = Math.abs(toX - fromX)
  const verticalDistance = Math.abs(toY - fromY)
  const movingDown = toY > fromY
  const movingRight = toX > fromX

  // 创建智能的折线路径
  const waypoints: string[] = []
  waypoints.push(`M ${fromX} ${fromY}`)

  // 尝试多个避障策略
  const strategies = [
    // 策略1：先水平后垂直
    () => {
      const midX = fromX + (toX - fromX) * 0.5
      const path = [
        `M ${fromX} ${fromY}`,
        `L ${midX} ${fromY}`,
        `L ${midX} ${toY}`,
        `L ${toX} ${toY}`
      ].join(' ')

      const intersects = lineIntersectsNode(fromX, fromY, midX, fromY) ||
                         lineIntersectsNode(midX, fromY, midX, toY) ||
                         lineIntersectsNode(midX, toY, toX, toY)
      return { path, intersects }
    },

    // 策略2：先垂直后水平
    () => {
      const midY = fromY + (toY - fromY) * 0.5
      const path = [
        `M ${fromX} ${fromY}`,
        `L ${fromX} ${midY}`,
        `L ${toX} ${midY}`,
        `L ${toX} ${toY}`
      ].join(' ')

      const intersects = lineIntersectsNode(fromX, fromY, fromX, midY) ||
                         lineIntersectsNode(fromX, midY, toX, midY) ||
                         lineIntersectsNode(toX, midY, toX, toY)
      return { path, intersects }
    },

    // 策略3：上方绕行
    () => {
      const buffer = margin + 20
      const upperY = Math.min(
        ...nodeBounds.map(n => n.y - buffer)
      )

      const path = [
        `M ${fromX} ${fromY}`,
        `L ${fromX} ${upperY}`,
        `L ${toX} ${upperY}`,
        `L ${toX} ${toY}`
      ].join(' ')

      const intersects = lineIntersectsNode(fromX, fromY, fromX, upperY) ||
                         lineIntersectsNode(fromX, upperY, toX, upperY) ||
                         lineIntersectsNode(toX, upperY, toX, toY)
      return { path, intersects }
    },

    // 策略4：下方绕行
    () => {
      const buffer = margin + 20
      const lowerY = Math.max(
        ...nodeBounds.map(n => n.y + n.height + buffer)
      )

      const path = [
        `M ${fromX} ${fromY}`,
        `L ${fromX} ${lowerY}`,
        `L ${toX} ${lowerY}`,
        `L ${toX} ${toY}`
      ].join(' ')

      const intersects = lineIntersectsNode(fromX, fromY, fromX, lowerY) ||
                         lineIntersectsNode(fromX, lowerY, toX, lowerY) ||
                         lineIntersectsNode(toX, lowerY, toX, toY)
      return { path, intersects }
    }
  ]

  // 尝试每个策略
  for (const strategy of strategies) {
    const result = strategy()
    if (!result.intersects) {
      return result.path
    }
  }

  // 如果所有策略都失败，使用简单的直角连接
  const midX = fromX + (toX - fromX) * 0.5
  return `M ${fromX} ${fromY} L ${midX} ${fromY} L ${midX} ${toY} L ${toX} ${toY}`
}

// 画布控制方法
const startCanvasDrag = (event: MouseEvent) => {
  if (event.target === event.currentTarget) {
    isCanvasDragging.value = true
    canvasDragStart.x = event.clientX
    canvasDragStart.y = event.clientY
    canvasOffsetStart.x = canvasOffset.x
    canvasOffsetStart.y = canvasOffset.y

    document.addEventListener('mousemove', onCanvasDrag)
    document.addEventListener('mouseup', stopCanvasDrag)

    event.preventDefault()
  }
}

const onCanvasDrag = (event: MouseEvent) => {
  if (!isCanvasDragging.value) return

  const deltaX = event.clientX - canvasDragStart.x
  const deltaY = event.clientY - canvasDragStart.y

  canvasOffset.x = canvasOffsetStart.x + deltaX
  canvasOffset.y = canvasOffsetStart.y + deltaY
}

const stopCanvasDrag = () => {
  isCanvasDragging.value = false
  document.removeEventListener('mousemove', onCanvasDrag)
  document.removeEventListener('mouseup', stopCanvasDrag)
}

const handleWheel = (event: WheelEvent) => {
  event.preventDefault()

  const delta = event.deltaY > 0 ? 0.9 : 1.1
  const newScale = canvasScale.value * delta

  if (newScale >= 0.1 && newScale <= 3) {
    canvasScale.value = newScale
  }
}

// 开始拖拽节点
const startDrag = (event: MouseEvent, node: Node) => {
  isDragging.value = true
  draggedNode.value = node.id

  // 获取鼠标相对于画布的位置（考虑缩放和偏移）
  const workflowCanvas = document.querySelector('.workflow-canvas') as HTMLElement
  const workflowRect = workflowCanvas.getBoundingClientRect()

  // 转换为画布坐标
  const canvasX = (event.clientX - workflowRect.left - canvasOffset.x) / canvasScale.value
  const canvasY = (event.clientY - workflowRect.top - canvasOffset.y) / canvasScale.value

  const nodePos = nodePositions.value[node.id]
  dragOffset.x = canvasX - nodePos.x
  dragOffset.y = canvasY - nodePos.y

  // 添加全局事件监听器
  document.addEventListener('mousemove', onDrag)
  document.addEventListener('mouseup', stopDrag)

  event.preventDefault()
  event.stopPropagation()
}

// 拖拽中
const onDrag = (event: MouseEvent) => {
  if (!isDragging.value || !draggedNode.value) return

  const nodePos = nodePositions.value[draggedNode.value]
  if (!nodePos) return

  // 获取鼠标相对于画布的位置（考虑缩放和偏移）
  const workflowCanvas = document.querySelector('.workflow-canvas') as HTMLElement
  const workflowRect = workflowCanvas.getBoundingClientRect()

  // 转换为画布坐标
  const canvasX = (event.clientX - workflowRect.left - canvasOffset.x) / canvasScale.value
  const canvasY = (event.clientY - workflowRect.top - canvasOffset.y) / canvasScale.value

  nodePos.x = canvasX - dragOffset.x
  nodePos.y = canvasY - dragOffset.y
}

// 停止拖拽
const stopDrag = () => {
  isDragging.value = false
  draggedNode.value = null

  // 移除全局事件监听器
  document.removeEventListener('mousemove', onDrag)
  document.removeEventListener('mouseup', stopDrag)
}

// 选择节点
const selectNode = (nodeId: string) => {
  activeNode.value = nodeId
}

// 端口事件处理
const onPortHover = (event: MouseEvent) => {
  const port = event.target as HTMLElement
  port.style.transform = port.style.transform === 'scale(1.5)' ? 'scale(1)' : 'scale(1.5)'
}

const onPortLeave = (event: MouseEvent) => {
  const port = event.target as HTMLElement
  port.style.transform = 'scale(1)'
}

// 返回
const goBack = () => {
  router.push('/research')
}

// 数据格式化函数
const formatStatLabel = (key: string): string => {
  const labelMap: Record<string, string> = {
    totalStocks: '股票总数',
    dataPoints: '数据点',
    lastUpdate: '更新时间',
    sources: '数据源',
    duplicateRecords: '重复记录',
    missingValues: '缺失值',
    outliers: '异常值',
    cleanRate: '清洗率',
    epochs: '训练轮次',
    accuracy: '准确率',
    loss: '损失值',
    bestScore: '最佳得分'
  }
  return labelMap[key] || key
}

const formatStatValue = (value: any): string => {
  if (Array.isArray(value)) {
    return value.join(', ')
  }
  return String(value)
}

// 判断数值的颜色（中国股市配色）
const getValueColor = (value: string | number): string => {
  const str = String(value)

  // 涨跌颜色判断
  if (str.includes('+') || str.startsWith('涨') ||
      (typeof value === 'number' && value > 0) ||
      str.includes('优秀') || str.includes('增长')) {
    return '#ef4444' // 红色 - 上涨
  } else if (str.includes('-') || str.startsWith('跌') ||
             (typeof value === 'number' && value < 0) ||
             str.includes('不良') || str.includes('下降')) {
    return '#22c55e' // 绿色 - 下跌
  } else if (str.includes('平') || (typeof value === 'number' && value === 0)) {
    return '#6b7280' // 灰色 - 平盘
  } else {
    return '#8b5cf6' // 默认紫色
  }
}

// 格式化表格单元格值
const formatTableValue = (value: any): { text: string; color: string } => {
  const str = String(value)
  let color = '#ffffff' // 默认白色

  // 涨跌幅颜色
  if (str.includes('+')) {
    color = '#ef4444' // 红色
  } else if (str.includes('-')) {
    color = '#22c55e' // 绿色
  }

  // 状态颜色
  if (str === '优秀') color = '#ef4444'
  if (str === '良好') color = '#f59e0b'
  if (str === '一般') color = '#6b7280'
  if (str === '差') color = '#22c55e'

  return { text: str, color }
}

// 粒子系统引用
const particleCanvas = ref<HTMLCanvasElement | null>(null)
const animationFrameId = ref<number | null>(null)

// 初始化粒子系统
const initParticleSystem = () => {
  // 延迟执行以确保DOM已完全渲染
  setTimeout(() => {
    const particleSystemEl = document.querySelector('.particle-system')
    if (!particleSystemEl) {
      console.warn('Particle system element not found')
      return
    }

    // 清理可能存在的旧canvas
    const existingCanvas = particleSystemEl.querySelector('canvas')
    if (existingCanvas) {
      existingCanvas.remove()
    }

    const canvas = document.createElement('canvas')
    const ctx = canvas.getContext('2d')

    if (!ctx) {
      console.warn('Could not get canvas context')
      return
    }

    const updateCanvasSize = () => {
      const rect = particleSystemEl.getBoundingClientRect()
      canvas.width = rect.width || window.innerWidth
      canvas.height = rect.height || window.innerHeight
    }

    updateCanvasSize()
    canvas.style.position = 'absolute'
    canvas.style.top = '0'
    canvas.style.left = '0'
    canvas.style.pointerEvents = 'none'
    canvas.style.width = '100%'
    canvas.style.height = '100%'

    particleSystemEl.appendChild(canvas)
    particleCanvas.value = canvas

    // 简单的粒子动画
    const particles: any[] = []
    for (let i = 0; i < 25; i++) {
      particles.push({
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height,
        vx: (Math.random() - 0.5) * 0.4,
        vy: (Math.random() - 0.5) * 0.4,
        size: Math.random() * 2 + 1,
        opacity: Math.random() * 0.5 + 0.2
      })
    }

    const animate = () => {
      if (!ctx || !canvas) return

      ctx.clearRect(0, 0, canvas.width, canvas.height)

      particles.forEach(particle => {
        particle.x += particle.vx
        particle.y += particle.vy

        if (particle.x < 0 || particle.x > canvas.width) particle.vx = -particle.vx
        if (particle.y < 0 || particle.y > canvas.height) particle.vy = -particle.vy

        ctx.beginPath()
        ctx.arc(particle.x, particle.y, particle.size, 0, Math.PI * 2)
        ctx.fillStyle = `rgba(59, 130, 246, ${particle.opacity})`
        ctx.fill()
      })

      animationFrameId.value = requestAnimationFrame(animate)
    }

    animate()

    // 监听窗口大小变化
    const handleResize = () => {
      updateCanvasSize()
    }

    window.addEventListener('resize', handleResize)

    // 更新清理函数
    cleanup = () => {
      window.removeEventListener('resize', handleResize)
      if (animationFrameId.value) {
        cancelAnimationFrame(animationFrameId.value)
      }
      if (canvas && canvas.parentNode) {
        canvas.parentNode.removeChild(canvas)
      }
    }
  }, 100) // 延迟100ms执行

  // 返回初始清理函数
  return () => {
    if (cleanup) cleanup()
  }
}

// 清理函数引用
let cleanup: (() => void) | null = null

// 生命周期
onMounted(async () => {
  // 确保DOM完全渲染后再初始化
  await nextTick()
  initializeNodePositions()
  cleanup = initParticleSystem()
})

// 初始化节点位置，避免重叠
const initializeNodePositions = () => {
  console.log('开始初始化节点位置，节点数量:', nodes.value.length)

  nodes.value.forEach((node, index) => {
    // 直接使用节点定义中的位置
    nodePositions.value[node.id] = {
      x: node.x,
      y: node.y,
      scale: 1,
      isExpanded: false
    }

    console.log(`节点 ${node.id} 位置设置为:`, { x: node.x, y: node.y })
  })

  // 调整画布初始偏移，确保节点在可视区域内
  canvasOffset.x = 0
  canvasOffset.y = 0

  console.log('节点位置初始化完成:', nodePositions.value)
}

onUnmounted(() => {
  if (cleanup) {
    cleanup()
  }
})
</script>

<style lang="scss" scoped>
@use '@/assets/styles/variables.scss' as *;

.node-workflow {
  position: relative;
  min-height: 100vh;
  background: var(--bg-deep);
  color: var(--text-primary);
  font-family: var(--font-family-primary);
  overflow-x: hidden;
}

/* 沉浸式背景 */
.immersive-background {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 0;
  pointer-events: none;
}

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
    rgba(59, 130, 246, 0.03) 50%,
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

.workflow-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 2rem;
  background: rgba(26, 26, 46, 0.8);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  position: relative;
  z-index: 100;
}

.workflow-header h1 {
  font-size: 1.8rem;
  font-weight: 600;
  margin: 0;
}

.btn-back {
  padding: 0.5rem 1.5rem;
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 8px;
  color: white;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-back:hover {
  background: rgba(255, 255, 255, 0.3);
}

.main-content {
  height: calc(100vh - 80px);
  position: relative;
  z-index: 5;
}

.workflow-canvas {
  height: calc(100vh - 80px);
  width: 100%;
  position: relative;
  overflow: visible;
  background: transparent;
}

.connections-layer {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 3;
}

.canvas-container {
  position: absolute;
  width: 3000px;
  height: 2000px;
  background: transparent;
  cursor: grab;
  transform-origin: 0 0;
  left: 0;
  top: 0;
  z-index: 2;
}

.canvas-container:active {
  cursor: grabbing;
}


.workflow-node {
  position: absolute;
  min-width: 220px;
  max-width: 320px;
  padding: 20px;
  background: rgba(26, 26, 46, 0.8);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  cursor: grab;
  user-select: none;
  z-index: 1;
  transition: all 0.3s ease;
}

.workflow-node:not(.dragging):hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.3);
  border-color: rgba(139, 92, 246, 0.3);
}

.workflow-node.active {
  border-color: rgba(139, 92, 246, 0.5);
  box-shadow: 0 0 30px rgba(139, 92, 246, 0.2);
}

.workflow-node.dragging {
  cursor: grabbing;
  z-index: 1000;
  opacity: 0.9;
  transform: scale(1.02);
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.4);
}

.node-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.node-icon {
  font-size: 1.5rem;
  flex-shrink: 0;
}

.node-title {
  font-size: 1.1rem;
  font-weight: 600;
  flex: 1;
  min-width: 0;
}

.node-description {
  font-size: 0.9rem;
  opacity: 0.8;
  line-height: 1.4;
  margin-bottom: 12px;
}

/* 数据内容样式 */
.node-content {
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  padding-top: 12px;
  margin-top: 8px;
}

/* 统计数据 */
.stats-container {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.85rem;
}

.stat-label {
  color: rgba(255, 255, 255, 0.7);
}

.stat-value {
  font-weight: 500;
}

/* 表格数据 */
.table-container {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.table-row {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr 1fr;
  gap: 6px;
  font-size: 0.8rem;
  padding: 4px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.table-cell {
  color: rgba(255, 255, 255, 0.9);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* 文本数据 */
.text-container {
  font-size: 0.85rem;
  line-height: 1.5;
  color: rgba(255, 255, 255, 0.9);
  padding: 8px;
  background: rgba(139, 92, 246, 0.1);
  border-radius: 8px;
  border-left: 3px solid #8b5cf6;
}

/* 列表数据 */
.list-container {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.list-item {
  font-size: 0.85rem;
  color: rgba(255, 255, 255, 0.9);
  padding: 4px 8px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 6px;
  border-left: 2px solid rgba(139, 92, 246, 0.5);
}

/* 图表数据 */
.chart-container {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.chart-summary {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.chart-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.chart-label {
  font-size: 0.8rem;
  color: rgba(255, 255, 255, 0.7);
}

.chart-patterns {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.pattern-tag {
  font-size: 0.75rem;
  padding: 2px 6px;
  background: rgba(139, 92, 246, 0.2);
  border: 1px solid rgba(139, 92, 246, 0.3);
  border-radius: 12px;
  color: #a78bfa;
}

.chart-stats {
  display: flex;
  justify-content: space-between;
}

.chart-stat {
  font-size: 0.8rem;
  color: rgba(255, 255, 255, 0.9);
  font-weight: 500;
}

/* 节点端口样式 */
.node-port {
  position: absolute;
  width: 12px;
  height: 12px;
  background: #8b5cf6;
  border: 2px solid rgba(26, 26, 46, 0.9);
  border-radius: 50%;
  z-index: 10;
  transition: all 0.2s ease;
  opacity: 0.3;
}

.node-port:hover {
  transform: scale(1.5);
  background: #a78bfa;
  box-shadow: 0 0 8px rgba(139, 92, 246, 0.6);
  opacity: 1;
}

.node-input-port {
  top: -6px;
  left: 50%;
  transform: translateX(-50%);
}

.node-output-port {
  bottom: -6px;
  left: 50%;
  transform: translateX(-50%);
}

.workflow-node.active .node-port {
  background: #3b82f6;
  border-color: rgba(59, 130, 246, 0.8);
  box-shadow: 0 0 12px rgba(59, 130, 246, 0.4);
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
</style>
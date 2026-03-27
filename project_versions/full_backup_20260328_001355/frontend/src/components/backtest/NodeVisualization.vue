<template>
  <div class="node-visualization-container">
    <!-- 工具栏 -->
    <div class="visualization-toolbar">
      <div class="toolbar-left">
        <el-button-group>
          <el-button 
            :type="viewMode === 'overview' ? 'primary' : 'default'"
            @click="setViewMode('overview')"
            size="small"
          >
            <el-icon><View /></el-icon>
            概览
          </el-button>
          <el-button 
            :type="viewMode === 'detail' ? 'primary' : 'default'"
            @click="setViewMode('detail')"
            size="small"
          >
            <el-icon><ZoomIn /></el-icon>
            详情
          </el-button>
          <el-button 
            :type="viewMode === 'edit' ? 'primary' : 'default'"
            @click="setViewMode('edit')"
            size="small"
          >
            <el-icon><Edit /></el-icon>
            编辑
          </el-button>
        </el-button-group>
      </div>
      
      <div class="toolbar-center">
        <el-button-group>
          <el-button @click="zoomIn" size="small" :disabled="zoomLevel >= maxZoom">
            <el-icon><ZoomIn /></el-icon>
          </el-button>
          <el-button @click="zoomOut" size="small" :disabled="zoomLevel <= minZoom">
            <el-icon><ZoomOut /></el-icon>
          </el-button>
          <el-button @click="resetZoom" size="small">
            <el-icon><RefreshRight /></el-icon>
          </el-button>
        </el-button-group>
        
        <el-divider direction="vertical" />
        
        <el-button-group>
          <el-button @click="fitToScreen" size="small">
            <el-icon><FullScreen /></el-icon>
            适应屏幕
          </el-button>
          <el-button @click="centerView" size="small">
            <el-icon><Position /></el-icon>
            居中
          </el-button>
        </el-button-group>
      </div>
      
      <div class="toolbar-right">
        <el-button @click="toggleGrid" size="small" :type="showGrid ? 'primary' : 'default'">
          <el-icon><Grid /></el-icon>
          网格
        </el-button>
        <el-button @click="toggleMinimap" size="small" :type="showMinimap ? 'primary' : 'default'">
          <el-icon><MapLocation /></el-icon>
          小地图
        </el-button>
        <el-button @click="exportVisualization" size="small">
          <el-icon><Download /></el-icon>
          导出
        </el-button>
      </div>
    </div>

    <!-- 主可视化区域 -->
    <div class="visualization-main" ref="visualizationContainer">
      <!-- SVG 画布 -->
      <svg 
        class="visualization-canvas"
        :width="canvasWidth"
        :height="canvasHeight"
        @mousedown="handleCanvasMouseDown"
        @mousemove="handleCanvasMouseMove"
        @mouseup="handleCanvasMouseUp"
        @wheel="handleCanvasWheel"
        @contextmenu.prevent="handleCanvasRightClick"
      >
        <!-- 定义渐变和滤镜 -->
        <defs>
          <!-- 节点阴影 -->
          <filter id="node-shadow" x="-50%" y="-50%" width="200%" height="200%">
            <feGaussianBlur in="SourceAlpha" stdDeviation="3"/>
            <feOffset dx="2" dy="2" result="offsetblur"/>
            <feFlood flood-color="#000000" flood-opacity="0.2"/>
            <feComposite in2="offsetblur" operator="in"/>
            <feMerge>
              <feMergeNode/>
              <feMergeNode in="SourceGraphic"/>
            </feMerge>
          </filter>
          
          <!-- 连接箭头 -->
          <marker 
            id="arrowhead" 
            markerWidth="10" 
            markerHeight="7" 
            refX="9" 
            refY="3.5" 
            orient="auto"
          >
            <polygon 
              points="0 0, 10 3.5, 0 7" 
              fill="#666"
            />
          </marker>
          
          <!-- 高亮箭头 -->
          <marker 
            id="arrowhead-highlight" 
            markerWidth="10" 
            markerHeight="7" 
            refX="9" 
            refY="3.5" 
            orient="auto"
          >
            <polygon 
              points="0 0, 10 3.5, 0 7" 
              fill="#409EFF"
            />
          </marker>
        </defs>

        <!-- 网格背景 -->
        <g v-if="showGrid" class="grid-background">
          <pattern 
            id="grid" 
            width="20" 
            height="20" 
            patternUnits="userSpaceOnUse"
          >
            <path 
              d="M 20 0 L 0 0 0 20" 
              fill="none" 
              stroke="#e0e0e0" 
              stroke-width="0.5"
            />
          </pattern>
          <rect 
            width="100%" 
            height="100%" 
            fill="url(#grid)" 
          />
        </g>

        <!-- 连接线组 -->
        <g class="connections-group" :transform="`translate(${panX}, ${panY}) scale(${zoomLevel})`">
          <connection-renderer
            v-for="connection in connections"
            :key="connection.id"
            :connection="connection"
            :source-node="getNodeById(connection.sourceNodeId)"
            :target-node="getNodeById(connection.targetNodeId)"
            :highlighted="isConnectionHighlighted(connection)"
            :selected="isConnectionSelected(connection)"
            @click="handleConnectionClick"
            @mouseenter="handleConnectionHover"
            @mouseleave="handleConnectionLeave"
          />
        </g>

        <!-- 节点组 -->
        <g class="nodes-group" :transform="`translate(${panX}, ${panY}) scale(${zoomLevel})`">
          <node-renderer
            v-for="node in visibleNodes"
            :key="node.id"
            :node="node"
            :selected="isNodeSelected(node)"
            :highlighted="isNodeHighlighted(node)"
            :view-mode="viewMode"
            :draggable="viewMode === 'edit'"
            @click="handleNodeClick"
            @dblclick="handleNodeDoubleClick"
            @mousedown="handleNodeMouseDown"
            @mouseenter="handleNodeHover"
            @mouseleave="handleNodeLeave"
            @contextmenu.prevent="handleNodeRightClick"
          />
        </g>

        <!-- 选择框 -->
        <rect
          v-if="selectionBox.active"
          :x="selectionBox.x"
          :y="selectionBox.y"
          :width="selectionBox.width"
          :height="selectionBox.height"
          fill="rgba(64, 158, 255, 0.1)"
          stroke="#409EFF"
          stroke-width="1"
          stroke-dasharray="5,5"
        />
      </svg>

      <!-- 小地图 -->
      <div v-if="showMinimap" class="minimap-container">
        <div class="minimap" ref="minimapRef">
          <svg 
            :width="minimapWidth" 
            :height="minimapHeight"
            class="minimap-canvas"
          >
            <!-- 小地图节点 -->
            <rect
              v-for="node in nodes"
              :key="`minimap-${node.id}`"
              :x="node.position.x * minimapScale"
              :y="node.position.y * minimapScale"
              :width="node.size.width * minimapScale"
              :height="node.size.height * minimapScale"
              :fill="getNodeColor(node)"
              :stroke="isNodeSelected(node) ? '#409EFF' : '#666'"
              :stroke-width="isNodeSelected(node) ? 2 : 1"
              rx="4"
            />
            
            <!-- 小地图连接 -->
            <line
              v-for="connection in connections"
              :key="`minimap-${connection.id}`"
              :x1="getNodeById(connection.sourceNodeId)?.position.x * minimapScale"
              :y1="getNodeById(connection.sourceNodeId)?.position.y * minimapScale"
              :x2="getNodeById(connection.targetNodeId)?.position.x * minimapScale"
              :y2="getNodeById(connection.targetNodeId)?.position.y * minimapScale"
              stroke="#666"
              stroke-width="1"
            />
            
            <!-- 视口指示器 -->
            <rect
              :x="viewportX * minimapScale"
              :y="viewportY * minimapScale"
              :width="viewportWidth * minimapScale"
              :height="viewportHeight * minimapScale"
              fill="none"
              stroke="#409EFF"
              stroke-width="2"
              rx="2"
              class="viewport-indicator"
              @mousedown="handleMinimapMouseDown"
              @mousemove="handleMinimapMouseMove"
              @mouseup="handleMinimapMouseUp"
            />
          </svg>
        </div>
      </div>

      <!-- 节点信息面板 -->
      <div 
        v-if="hoveredNode && viewMode !== 'edit'" 
        class="node-info-panel"
        :style="{
          left: `${hoveredNode.position.x + hoveredNode.size.width + 10}px`,
          top: `${hoveredNode.position.y}px`
        }"
      >
        <div class="panel-header">
          <h4>{{ hoveredNode.name }}</h4>
          <el-tag :type="getStatusTagType(hoveredNode.status)" size="small">
            {{ getStatusText(hoveredNode.status) }}
          </el-tag>
        </div>
        <div class="panel-content">
          <p class="node-description">{{ hoveredNode.description }}</p>
          <div class="node-stats">
            <div class="stat-item">
              <span class="stat-label">类型:</span>
              <span class="stat-value">{{ getNodeTypeName(hoveredNode.type) }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">进度:</span>
              <el-progress 
                :percentage="hoveredNode.execution?.progress || 0" 
                :stroke-width="4"
                :show-text="false"
              />
            </div>
            <div v-if="hoveredNode.metadata?.lastExecution" class="stat-item">
              <span class="stat-label">最后执行:</span>
              <span class="stat-value">{{ formatTime(hoveredNode.metadata.lastExecution) }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 右键菜单 -->
      <div 
        v-if="contextMenu.visible" 
        class="context-menu"
        :style="{
          left: `${contextMenu.x}px`,
          top: `${contextMenu.y}px`
        }"
        @click.stop
      >
        <div v-if="contextMenu.type === 'node'" class="menu-section">
          <div class="menu-item" @click="executeNode(contextMenu.target)">
            <el-icon><VideoPlay /></el-icon>
            执行节点
          </div>
          <div class="menu-item" @click="configureNode(contextMenu.target)">
            <el-icon><Setting /></el-icon>
            配置节点
          </div>
          <div class="menu-item" @click="duplicateNode(contextMenu.target)">
            <el-icon><CopyDocument /></el-icon>
            复制节点
          </div>
          <div class="menu-divider"></div>
          <div class="menu-item danger" @click="deleteNode(contextMenu.target)">
            <el-icon><Delete /></el-icon>
            删除节点
          </div>
        </div>
        
        <div v-else-if="contextMenu.type === 'canvas'" class="menu-section">
          <div class="menu-item" @click="addNode">
            <el-icon><Plus /></el-icon>
            添加节点
          </div>
          <div class="menu-item" @click="pasteNode">
            <el-icon><DocumentCopy /></el-icon>
            粘贴节点
          </div>
          <div class="menu-divider"></div>
          <div class="menu-item" @click="selectAllNodes">
            <el-icon><Select /></el-icon>
            全选
          </div>
          <div class="menu-item" @click="clearSelection">
            <el-icon><Remove /></el-icon>
            清除选择
          </div>
        </div>
      </div>
    </div>

    <!-- 状态栏 -->
    <div class="visualization-statusbar">
      <div class="status-left">
        <span class="status-item">
          节点: {{ nodes.length }} / {{ visibleNodes.length }} 可见
        </span>
        <span class="status-item">
          连接: {{ connections.length }}
        </span>
        <span class="status-item">
          缩放: {{ Math.round(zoomLevel * 100) }}%
        </span>
      </div>
      
      <div class="status-center">
        <span v-if="selectedNodes.length > 0" class="status-item">
          已选择 {{ selectedNodes.length }} 个节点
        </span>
        <span v-if="selectedConnections.length > 0" class="status-item">
          已选择 {{ selectedConnections.length }} 条连接
        </span>
      </div>
      
      <div class="status-right">
        <span class="status-item">
          位置: ({{ Math.round(-panX / zoomLevel) }}, {{ Math.round(-panY / zoomLevel) }})
        </span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  View, ZoomIn, ZoomOut, RefreshRight, FullScreen, Position, 
  Grid, MapLocation, Download, VideoPlay, Setting, CopyDocument, 
  Delete, Plus, DocumentCopy, Select, Remove 
} from '@element-plus/icons-vue'

// 导入类型和组件
import type { Node, NodeStatus, NodeType, Connection } from '@/types/node-system'
import NodeRenderer from './NodeRenderer.vue'
import ConnectionRenderer from './ConnectionRenderer.vue'
import { nodeStateManager } from '@/components/backtest/node-system/NodeStateManager'
import { nodeLayoutManager } from '@/components/backtest/node-system/NodeLayoutManager'

// 响应式数据
const visualizationContainer = ref<HTMLElement>()
const minimapRef = ref<HTMLElement>()

const viewMode = ref<'overview' | 'detail' | 'edit'>('overview')
const zoomLevel = ref(1)
const panX = ref(0)
const panY = ref(0)
const showGrid = ref(true)
const showMinimap = ref(true)

const minZoom = 0.1
const maxZoom = 3
const zoomStep = 0.1

const canvasWidth = ref(1200)
const canvasHeight = ref(800)
const minimapWidth = 200
const minimapHeight = 150
const minimapScale = 0.15

// 选择状态
const selectedNodes = ref<string[]>([])
const selectedConnections = ref<string[]>([])
const hoveredNode = ref<Node | null>(null)
const hoveredConnection = ref<Connection | null>(null)

// 拖拽状态
const isDragging = ref(false)
const dragStartX = ref(0)
const dragStartY = ref(0)
const draggedNode = ref<string | null>(null)

// 选择框状态
const selectionBox = reactive({
  active: false,
  x: 0,
  y: 0,
  width: 0,
  height: 0,
  startX: 0,
  startY: 0
})

// 右键菜单状态
const contextMenu = reactive({
  visible: false,
  x: 0,
  y: 0,
  type: 'node' | 'canvas' | null,
  target: null as Node | null
})

// 小地图拖拽状态
const minimapDragging = ref(false)

// 计算属性
const nodes = computed(() => nodeStateManager.getNodes())
const connections = computed(() => nodeStateManager.getConnections())

const visibleNodes = computed(() => {
  return nodes.value.filter(node => {
    // 根据视图模式过滤节点
    if (viewMode.value === 'overview') {
      return true // 显示所有节点
    } else if (viewMode.value === 'detail') {
      return node.status !== NodeStatus.IDLE // 只显示非空闲节点
    } else if (viewMode.value === 'edit') {
      return true // 编辑模式显示所有节点
    }
    return true
  })
})

const viewportX = computed(() => -panX.value / zoomLevel.value)
const viewportY = computed(() => -panY.value / zoomLevel.value)
const viewportWidth = computed(() => canvasWidth.value / zoomLevel.value)
const viewportHeight = computed(() => canvasHeight.value / zoomLevel.value)

// 方法
const setViewMode = (mode: 'overview' | 'detail' | 'edit') => {
  viewMode.value = mode
  if (mode === 'edit') {
    ElMessage.info('已切换到编辑模式，可以拖拽和修改节点')
  }
}

const zoomIn = () => {
  if (zoomLevel.value < maxZoom) {
    zoomLevel.value = Math.min(zoomLevel.value + zoomStep, maxZoom)
  }
}

const zoomOut = () => {
  if (zoomLevel.value > minZoom) {
    zoomLevel.value = Math.max(zoomLevel.value - zoomStep, minZoom)
  }
}

const resetZoom = () => {
  zoomLevel.value = 1
  centerView()
}

const fitToScreen = () => {
  if (nodes.value.length === 0) return

  const bounds = nodeLayoutManager.calculateNodesBounds(nodes.value)
  const padding = 50
  
  const scaleX = (canvasWidth.value - padding * 2) / bounds.width
  const scaleY = (canvasHeight.value - padding * 2) / bounds.height
  const scale = Math.min(scaleX, scaleY, maxZoom)
  
  zoomLevel.value = Math.max(scale, minZoom)
  
  panX.value = (canvasWidth.value - bounds.width * zoomLevel.value) / 2 - bounds.left * zoomLevel.value
  panY.value = (canvasHeight.value - bounds.height * zoomLevel.value) / 2 - bounds.top * zoomLevel.value
}

const centerView = () => {
  if (nodes.value.length === 0) return

  const bounds = nodeLayoutManager.calculateNodesBounds(nodes.value)
  const centerX = bounds.left + bounds.width / 2
  const centerY = bounds.top + bounds.height / 2
  
  panX.value = canvasWidth.value / 2 - centerX * zoomLevel.value
  panY.value = canvasHeight.value / 2 - centerY * zoomLevel.value
}

const toggleGrid = () => {
  showGrid.value = !showGrid.value
}

const toggleMinimap = () => {
  showMinimap.value = !showMinimap.value
}

const exportVisualization = () => {
  // 实现导出功能
  ElMessage.info('导出功能开发中...')
}

// 节点相关方法
const getNodeById = (id: string): Node | undefined => {
  return nodes.value.find(node => node.id === id)
}

const isNodeSelected = (node: Node): boolean => {
  return selectedNodes.value.includes(node.id)
}

const isNodeHighlighted = (node: Node): boolean => {
  return hoveredNode.value?.id === node.id
}

const isConnectionHighlighted = (connection: Connection): boolean => {
  return hoveredConnection.value?.id === connection.id
}

const isConnectionSelected = (connection: Connection): boolean => {
  return selectedConnections.value.includes(connection.id)
}

const getNodeColor = (node: Node): string => {
  switch (node.status) {
    case NodeStatus.RUNNING:
      return '#67C23A'
    case NodeStatus.COMPLETED:
      return '#409EFF'
    case NodeStatus.FAILED:
      return '#F56C6C'
    case NodeStatus.PAUSED:
      return '#E6A23C'
    default:
      return '#909399'
  }
}

const getStatusTagType = (status: NodeStatus) => {
  switch (status) {
    case NodeStatus.RUNNING:
      return 'success'
    case NodeStatus.COMPLETED:
      return 'primary'
    case NodeStatus.FAILED:
      return 'danger'
    case NodeStatus.PAUSED:
      return 'warning'
    default:
      return 'info'
  }
}

const getStatusText = (status: NodeStatus): string => {
  switch (status) {
    case NodeStatus.RUNNING:
      return '运行中'
    case NodeStatus.COMPLETED:
      return '已完成'
    case NodeStatus.FAILED:
      return '失败'
    case NodeStatus.PAUSED:
      return '已暂停'
    default:
      return '空闲'
  }
}

const getNodeTypeName = (type: NodeType): string => {
  switch (type) {
    case NodeType.DATA_SOURCE:
      return '数据源'
    case NodeType.DATA_PROCESSING:
      return '数据处理'
    case NodeType.STRATEGY:
      return '策略'
    case NodeType.BACKTEST:
      return '回测'
    case NodeType.ANALYSIS:
      return '分析'
    case NodeType.VISUALIZATION:
      return '可视化'
    case NodeType.EXPORT:
      return '导出'
    default:
      return '未知'
  }
}

const formatTime = (timestamp: string): string => {
  return new Date(timestamp).toLocaleString('zh-CN')
}

// 事件处理方法
const handleCanvasMouseDown = (event: MouseEvent) => {
  if (event.button === 0) { // 左键
    isDragging.value = true
    dragStartX.value = event.clientX - panX.value
    dragStartY.value = event.clientY - panY.value
    
    // 开始选择框
    if (viewMode.value === 'edit' && event.shiftKey) {
      selectionBox.active = true
      selectionBox.startX = event.clientX
      selectionBox.startY = event.clientY
      selectionBox.x = event.clientX
      selectionBox.y = event.clientY
      selectionBox.width = 0
      selectionBox.height = 0
    }
  }
}

const handleCanvasMouseMove = (event: MouseEvent) => {
  if (isDragging.value && !draggedNode.value) {
    // 拖拽画布
    panX.value = event.clientX - dragStartX.value
    panY.value = event.clientY - dragStartY.value
  }
  
  // 更新选择框
  if (selectionBox.active) {
    selectionBox.width = event.clientX - selectionBox.startX
    selectionBox.height = event.clientY - selectionBox.startY
    
    if (selectionBox.width < 0) {
      selectionBox.x = event.clientX
      selectionBox.width = Math.abs(selectionBox.width)
    } else {
      selectionBox.x = selectionBox.startX
    }
    
    if (selectionBox.height < 0) {
      selectionBox.y = event.clientY
      selectionBox.height = Math.abs(selectionBox.height)
    } else {
      selectionBox.y = selectionBox.startY
    }
  }
}

const handleCanvasMouseUp = (event: MouseEvent) => {
  isDragging.value = false
  draggedNode.value = null
  
  // 完成选择框
  if (selectionBox.active) {
    selectNodesInBox()
    selectionBox.active = false
  }
}

const handleCanvasWheel = (event: WheelEvent) => {
  event.preventDefault()
  
  const delta = event.deltaY > 0 ? -zoomStep : zoomStep
  const newZoom = Math.max(minZoom, Math.min(maxZoom, zoomLevel.value + delta))
  
  // 以鼠标位置为中心缩放
  const rect = visualizationContainer.value?.getBoundingClientRect()
  if (rect) {
    const mouseX = event.clientX - rect.left
    const mouseY = event.clientY - rect.top
    
    const worldX = (mouseX - panX.value) / zoomLevel.value
    const worldY = (mouseY - panY.value) / zoomLevel.value
    
    zoomLevel.value = newZoom
    
    panX.value = mouseX - worldX * zoomLevel.value
    panY.value = mouseY - worldY * zoomLevel.value
  }
}

const handleCanvasRightClick = (event: MouseEvent) => {
  event.preventDefault()
  
  contextMenu.visible = true
  contextMenu.x = event.clientX
  contextMenu.y = event.clientY
  contextMenu.type = 'canvas'
  contextMenu.target = null
}

const handleNodeClick = (node: Node, event: MouseEvent) => {
  event.stopPropagation()
  
  if (viewMode.value === 'edit') {
    if (event.ctrlKey || event.metaKey) {
      // 多选
      const index = selectedNodes.value.indexOf(node.id)
      if (index > -1) {
        selectedNodes.value.splice(index, 1)
      } else {
        selectedNodes.value.push(node.id)
      }
    } else {
      // 单选
      selectedNodes.value = [node.id]
      selectedConnections.value = []
    }
  }
}

const handleNodeDoubleClick = (node: Node) => {
  if (viewMode.value === 'edit') {
    configureNode(node)
  } else {
    // 详情模式下显示节点详情
    viewMode.value = 'detail'
    selectedNodes.value = [node.id]
  }
}

const handleNodeMouseDown = (node: Node, event: MouseEvent) => {
  if (viewMode.value === 'edit' && event.button === 0) {
    event.stopPropagation()
    draggedNode.value = node.id
    isDragging.value = true
    dragStartX.value = event.clientX - node.position.x * zoomLevel.value - panX.value
    dragStartY.value = event.clientY - node.position.y * zoomLevel.value - panY.value
  }
}

const handleNodeHover = (node: Node) => {
  hoveredNode.value = node
}

const handleNodeLeave = () => {
  hoveredNode.value = null
}

const handleNodeRightClick = (node: Node, event: MouseEvent) => {
  event.preventDefault()
  event.stopPropagation()
  
  contextMenu.visible = true
  contextMenu.x = event.clientX
  contextMenu.y = event.clientY
  contextMenu.type = 'node'
  contextMenu.target = node
}

const handleConnectionClick = (connection: Connection, event: MouseEvent) => {
  event.stopPropagation()
  
  if (viewMode.value === 'edit') {
    if (event.ctrlKey || event.metaKey) {
      const index = selectedConnections.value.indexOf(connection.id)
      if (index > -1) {
        selectedConnections.value.splice(index, 1)
      } else {
        selectedConnections.value.push(connection.id)
      }
    } else {
      selectedConnections.value = [connection.id]
      selectedNodes.value = []
    }
  }
}

const handleConnectionHover = (connection: Connection) => {
  hoveredConnection.value = connection
}

const handleConnectionLeave = () => {
  hoveredConnection.value = null
}

// 小地图事件处理
const handleMinimapMouseDown = (event: MouseEvent) => {
  minimapDragging.value = true
  updateViewportFromMinimap(event)
}

const handleMinimapMouseMove = (event: MouseEvent) => {
  if (minimapDragging.value) {
    updateViewportFromMinimap(event)
  }
}

const handleMinimapMouseUp = () => {
  minimapDragging.value = false
}

const updateViewportFromMinimap = (event: MouseEvent) => {
  const rect = minimapRef.value?.getBoundingClientRect()
  if (!rect) return
  
  const x = (event.clientX - rect.left) / minimapScale
  const y = (event.clientY - rect.top) / minimapScale
  
  panX.value = canvasWidth.value / 2 - x * zoomLevel.value
  panY.value = canvasHeight.value / 2 - y * zoomLevel.value
}

// 选择框相关方法
const selectNodesInBox = () => {
  const boxLeft = Math.min(selectionBox.x, selectionBox.x + selectionBox.width)
  const boxRight = Math.max(selectionBox.x, selectionBox.x + selectionBox.width)
  const boxTop = Math.min(selectionBox.y, selectionBox.y + selectionBox.height)
  const boxBottom = Math.max(selectionBox.y, selectionBox.y + selectionBox.height)
  
  const selectedIds: string[] = []
  
  nodes.value.forEach(node => {
    const nodeLeft = node.position.x * zoomLevel.value + panX.value
    const nodeRight = (node.position.x + node.size.width) * zoomLevel.value + panX.value
    const nodeTop = node.position.y * zoomLevel.value + panY.value
    const nodeBottom = (node.position.y + node.size.height) * zoomLevel.value + panY.value
    
    if (nodeLeft >= boxLeft && nodeRight <= boxRight &&
        nodeTop >= boxTop && nodeBottom <= boxBottom) {
      selectedIds.push(node.id)
    }
  })
  
  selectedNodes.value = selectedIds
}

// 右键菜单操作
const executeNode = (node: Node) => {
  // 实现节点执行
  ElMessage.info(`执行节点: ${node.name}`)
  contextMenu.visible = false
}

const configureNode = (node: Node) => {
  // 实现节点配置
  ElMessage.info(`配置节点: ${node.name}`)
  contextMenu.visible = false
}

const duplicateNode = (node: Node) => {
  // 实现节点复制
  ElMessage.info(`复制节点: ${node.name}`)
  contextMenu.visible = false
}

const deleteNode = (node: Node) => {
  ElMessageBox.confirm(
    `确定要删除节点 "${node.name}" 吗？`,
    '删除确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    }
  ).then(() => {
    // 实现节点删除
    ElMessage.success('节点删除成功')
    contextMenu.visible = false
  }).catch(() => {
    contextMenu.visible = false
  })
}

const addNode = () => {
  // 实现添加节点
  ElMessage.info('添加节点功能开发中...')
  contextMenu.visible = false
}

const pasteNode = () => {
  // 实现粘贴节点
  ElMessage.info('粘贴节点功能开发中...')
  contextMenu.visible = false
}

const selectAllNodes = () => {
  selectedNodes.value = nodes.value.map(node => node.id)
  contextMenu.visible = false
}

const clearSelection = () => {
  selectedNodes.value = []
  selectedConnections.value = []
  contextMenu.visible = false
}

// 监听器
watch(() => nodes.value.length, () => {
  if (nodes.value.length > 0 && !isDragging.value) {
    nextTick(() => {
      fitToScreen()
    })
  }
})

// 生命周期
onMounted(() => {
  // 初始化画布大小
  if (visualizationContainer.value) {
    const rect = visualizationContainer.value.getBoundingClientRect()
    canvasWidth.value = rect.width
    canvasHeight.value = rect.height
  }
  
  // 监听窗口大小变化
  window.addEventListener('resize', handleResize)
  
  // 监听点击事件以关闭右键菜单
  document.addEventListener('click', hideContextMenu)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  document.removeEventListener('click', hideContextMenu)
})

const handleResize = () => {
  if (visualizationContainer.value) {
    const rect = visualizationContainer.value.getBoundingClientRect()
    canvasWidth.value = rect.width
    canvasHeight.value = rect.height
  }
}

const hideContextMenu = () => {
  contextMenu.visible = false
}
</script>

<style scoped>
.node-visualization-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: #f5f5f5;
}

.visualization-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 16px;
  background: white;
  border-bottom: 1px solid #e0e0e0;
  gap: 16px;
}

.toolbar-left,
.toolbar-center,
.toolbar-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

.visualization-main {
  flex: 1;
  position: relative;
  overflow: hidden;
}

.visualization-canvas {
  width: 100%;
  height: 100%;
  cursor: grab;
  background: white;
}

.visualization-canvas:active {
  cursor: grabbing;
}

.grid-background {
  pointer-events: none;
}

.connections-group,
.nodes-group {
  transform-origin: 0 0;
}

.minimap-container {
  position: absolute;
  top: 16px;
  right: 16px;
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.minimap {
  position: relative;
}

.minimap-canvas {
  display: block;
}

.viewport-indicator {
  cursor: move;
  fill: rgba(64, 158, 255, 0.1);
}

.node-info-panel {
  position: absolute;
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 12px;
  min-width: 200px;
  max-width: 300px;
  z-index: 1000;
  pointer-events: none;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.panel-header h4 {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
}

.panel-content {
  font-size: 12px;
}

.node-description {
  margin: 0 0 8px 0;
  color: #666;
  line-height: 1.4;
}

.node-stats {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stat-label {
  color: #666;
}

.stat-value {
  font-weight: 500;
}

.context-menu {
  position: fixed;
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 4px 0;
  min-width: 120px;
  z-index: 2000;
}

.menu-section {
  display: flex;
  flex-direction: column;
}

.menu-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  cursor: pointer;
  font-size: 12px;
  color: #333;
  transition: background-color 0.2s;
}

.menu-item:hover {
  background-color: #f5f5f5;
}

.menu-item.danger {
  color: #f56c6c;
}

.menu-item.danger:hover {
  background-color: #fef0f0;
}

.menu-divider {
  height: 1px;
  background-color: #e0e0e0;
  margin: 4px 0;
}

.visualization-statusbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 4px 16px;
  background: white;
  border-top: 1px solid #e0e0e0;
  font-size: 12px;
  color: #666;
}

.status-left,
.status-center,
.status-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.status-item {
  white-space: nowrap;
}
</style>
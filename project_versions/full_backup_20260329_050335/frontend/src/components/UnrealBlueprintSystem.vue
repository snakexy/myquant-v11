<template>
  <div class="unreal-blueprint-system">
    <!-- 蓝图画布 -->
    <div class="blueprint-canvas" ref="blueprintCanvas">
      <!-- 网格背景 -->
      <div class="grid-background" ref="gridBackground"></div>
      
      <!-- 连接线层 -->
      <svg class="connections-layer" ref="connectionsLayer">
        <defs>
          <!-- 定义不同类型连接的渐变 -->
          <linearGradient id="dataFlowGradient" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" style="stop-color:#00ff88;stop-opacity:0.8" />
            <stop offset="100%" style="stop-color:#0088ff;stop-opacity:0.8" />
          </linearGradient>
          
          <linearGradient id="conditionalGradient" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" style="stop-color:#ffaa00;stop-opacity:0.8" />
            <stop offset="100%" style="stop-color:#ff6600;stop-opacity:0.8" />
          </linearGradient>
          
          <linearGradient id="eventGradient" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" style="stop-color:#00ff66;stop-opacity:0.8" />
            <stop offset="100%" style="stop-color:#00cc44;stop-opacity:0.8" />
          </linearGradient>
          
          <linearGradient id="loopGradient" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" style="stop-color:#9966ff;stop-opacity:0.8" />
            <stop offset="50%" style="stop-color:#ff66cc;stop-opacity:0.8" />
            <stop offset="100%" style="stop-color:#9966ff;stop-opacity:0.8" />
          </linearGradient>
          
          <!-- 箭头标记 -->
          <marker id="arrowDataFlow" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto" markerUnits="strokeWidth">
            <path d="M0,0 L0,6 L9,3 z" fill="url(#dataFlowGradient)" />
          </marker>
          
          <marker id="arrowConditional" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto" markerUnits="strokeWidth">
            <path d="M0,0 L0,6 L9,3 z" fill="url(#conditionalGradient)" />
          </marker>
          
          <marker id="arrowEvent" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto" markerUnits="strokeWidth">
            <circle cx="4" cy="3" r="3" fill="url(#eventGradient)" />
          </marker>
          
          <marker id="arrowLoop" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto" markerUnits="strokeWidth">
            <path d="M0,0 L0,6 L9,3 z" fill="url(#loopGradient)" />
          </marker>
        </defs>
        
        <!-- 连接线组 -->
        <g class="connections-group">
          <path
            v-for="connection in connections"
            :key="connection.id"
            :d="getConnectionPath(connection)"
            :stroke="getConnectionColor(connection.type)"
            :stroke-width="getConnectionWidth(connection)"
            :stroke-dasharray="getConnectionDashArray(connection.type)"
            fill="none"
            :marker-end="getConnectionMarker(connection.type)"
            class="connection-path"
            :class="{
              'connection-active': connection.active,
              'connection-error': connection.error,
              'connection-selected': selectedConnection === connection.id
            }"
            @click="selectConnection(connection)"
            @contextmenu="showConnectionContextMenu($event, connection)"
          />
          
          <!-- 数据流动画粒子 -->
          <circle
            v-if="connection.active && dataFlowEnabled"
            v-for="(particle, index) in getConnectionParticles(connection)"
            :key="`${connection.id}-particle-${index}`"
            :r="3"
            :fill="getConnectionColor(connection.type)"
            class="data-particle"
            :style="getParticleStyle(particle, connection)"
          />
        </g>
      </svg>
      
      <!-- 节点层 -->
      <div class="nodes-layer" ref="nodesLayer">
        <div
          v-for="node in nodes"
          :key="node.id"
          class="blueprint-node"
          :class="{
            'node-selected': selectedNode === node.id,
            'node-active': node.active,
            'node-error': node.error,
            [`node-type-${node.type}`]: true
          }"
          :style="getNodeStyle(node)"
          @mousedown="startDragNode($event, node)"
          @contextmenu="showNodeContextMenu($event, node)"
          @dblclick="openNodeDetails(node)"
        >
          <!-- 节点主体 -->
          <div class="node-body">
            <div class="node-header">
              <div class="node-icon">
                <i :class="node.icon"></i>
              </div>
              <div class="node-title">{{ node.title }}</div>
              <div class="node-status" :class="node.status">
                <span class="status-dot"></span>
              </div>
            </div>
            
            <div class="node-content">
              <p class="node-description">{{ node.description }}</p>
              
              <!-- 节点指标 -->
              <div class="node-metrics" v-if="node.metrics">
                <div 
                  v-for="metric in node.metrics" 
                  :key="metric.name"
                  class="metric-item"
                >
                  <span class="metric-label">{{ metric.label }}:</span>
                  <span class="metric-value" :class="metric.type">{{ metric.value }}</span>
                </div>
              </div>
            </div>
          </div>
          
          <!-- 连接端点 -->
          <div class="node-ports">
            <!-- 输入端点 -->
            <div
              v-for="port in node.inputPorts"
              :key="port.id"
              class="port port-input"
              :class="{
                'port-highlighted': highlightedPort === `${node.id}-${port.id}`,
                'port-occupied': isPortOccupied(node.id, port.id, 'input')
              }"
              :style="getPortStyle(port, 'input')"
              @mouseenter="highlightPort(`${node.id}-${port.id}`)"
              @mouseleave="unhighlightPort"
              @click="handlePortClick($event, node, port, 'input')"
            >
              <div class="port-indicator"></div>
              <div class="port-label">{{ port.label }}</div>
            </div>
            
            <!-- 输出端点 -->
            <div
              v-for="port in node.outputPorts"
              :key="port.id"
              class="port port-output"
              :class="{
                'port-highlighted': highlightedPort === `${node.id}-${port.id}`,
                'port-occupied': isPortOccupied(node.id, port.id, 'output')
              }"
              :style="getPortStyle(port, 'output')"
              @mouseenter="highlightPort(`${node.id}-${port.id}`)"
              @mouseleave="unhighlightPort"
              @click="handlePortClick($event, node, port, 'output')"
            >
              <div class="port-indicator"></div>
              <div class="port-label">{{ port.label }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 工具栏 -->
    <div class="blueprint-toolbar">
      <div class="toolbar-section">
        <h4>连接工具</h4>
        <div class="tool-buttons">
          <button 
            v-for="tool in connectionTools" 
            :key="tool.id"
            class="tool-btn"
            :class="{ active: activeTool === tool.id }"
            @click="setActiveTool(tool.id)"
            :title="tool.description"
          >
            <i :class="tool.icon"></i>
            <span>{{ tool.name }}</span>
          </button>
        </div>
      </div>
      
      <div class="toolbar-section">
        <h4>布局工具</h4>
        <div class="tool-buttons">
          <button 
            v-for="tool in layoutTools" 
            :key="tool.id"
            class="tool-btn"
            @click="executeLayoutTool(tool.id)"
            :title="tool.description"
          >
            <i :class="tool.icon"></i>
            <span>{{ tool.name }}</span>
          </button>
        </div>
      </div>
      
      <div class="toolbar-section">
        <h4>视图选项</h4>
        <div class="view-options">
          <label class="option-item">
            <input type="checkbox" v-model="dataFlowEnabled" />
            <span>数据流动画</span>
          </label>
          <label class="option-item">
            <input type="checkbox" v-model="gridEnabled" />
            <span>显示网格</span>
          </label>
          <label class="option-item">
            <input type="checkbox" v-model="autoLayout" />
            <span>自动布局</span>
          </label>
          <label class="option-item">
            <span>缩放: {{ Math.round(zoomLevel * 100) }}%</span>
            <input type="range" min="0.5" max="2" step="0.1" v-model="zoomLevel" />
          </label>
        </div>
      </div>
    </div>
    
    <!-- 连接上下文菜单 -->
    <div 
      v-if="connectionContextMenu.visible" 
      class="context-menu connection-context-menu"
      :style="{ left: connectionContextMenu.x + 'px', top: connectionContextMenu.y + 'px' }"
    >
      <div class="menu-item" @click="editConnection(connectionContextMenu.connection)">
        <i class="fas fa-edit"></i>
        <span>编辑连接</span>
      </div>
      <div class="menu-item" @click="deleteConnection(connectionContextMenu.connection)">
        <i class="fas fa-trash"></i>
        <span>删除连接</span>
      </div>
      <div class="menu-item" @click="setConnectionType(connectionContextMenu.connection, 'data-flow')">
        <i class="fas fa-exchange-alt"></i>
        <span>数据流连接</span>
      </div>
      <div class="menu-item" @click="setConnectionType(connectionContextMenu.connection, 'conditional')">
        <i class="fas fa-code-branch"></i>
        <span>条件连接</span>
      </div>
      <div class="menu-item" @click="setConnectionType(connectionContextMenu.connection, 'event')">
        <i class="fas fa-bolt"></i>
        <span>事件连接</span>
      </div>
      <div class="menu-item" @click="setConnectionType(connectionContextMenu.connection, 'loop')">
        <i class="fas fa-sync-alt"></i>
        <span>循环连接</span>
      </div>
    </div>
    
    <!-- 节点上下文菜单 -->
    <div 
      v-if="nodeContextMenu.visible" 
      class="context-menu node-context-menu"
      :style="{ left: nodeContextMenu.x + 'px', top: nodeContextMenu.y + 'px' }"
    >
      <div class="menu-item" @click="openNodeDetails(nodeContextMenu.node)">
        <i class="fas fa-info-circle"></i>
        <span>节点详情</span>
      </div>
      <div class="menu-item" @click="duplicateNode(nodeContextMenu.node)">
        <i class="fas fa-copy"></i>
        <span>复制节点</span>
      </div>
      <div class="menu-item" @click="deleteNode(nodeContextMenu.node)">
        <i class="fas fa-trash"></i>
        <span>删除节点</span>
      </div>
      <div class="menu-separator"></div>
      <div class="menu-item" @click="groupNodes([nodeContextMenu.node])">
        <i class="fas fa-object-group"></i>
        <span>创建分组</span>
      </div>
    </div>
    
    <!-- 连接属性面板 -->
    <div v-if="selectedConnection" class="connection-properties-panel">
      <div class="panel-header">
        <h3>连接属性</h3>
        <button class="close-btn" @click="selectedConnection = null">
          <i class="fas fa-times"></i>
        </button>
      </div>
      
      <div class="panel-content">
        <div class="property-group">
          <label>连接类型</label>
          <select v-model="selectedConnection.type">
            <option value="data-flow">数据流连接</option>
            <option value="conditional">条件连接</option>
            <option value="event">事件连接</option>
            <option value="loop">循环连接</option>
          </select>
        </div>
        
        <div class="property-group">
          <label>数据类型</label>
          <select v-model="selectedConnection.dataType">
            <option value="numeric">数值数据</option>
            <option value="text">文本数据</option>
            <option value="binary">二进制数据</option>
            <option value="json">JSON数据</option>
          </select>
        </div>
        
        <div class="property-group">
          <label>流量大小</label>
          <input type="number" v-model="selectedConnection.throughput" min="1" />
          <span class="unit">条/秒</span>
        </div>
        
        <div class="property-group" v-if="selectedConnection.type === 'conditional'">
          <label>条件表达式</label>
          <input type="text" v-model="selectedConnection.condition" placeholder="例如: value > 100" />
        </div>
        
        <div class="property-group">
          <label>高级选项</label>
          <div class="checkbox-group">
            <label>
              <input type="checkbox" v-model="selectedConnection.compression" />
              <span>启用数据压缩</span>
            </label>
            <label>
              <input type="checkbox" v-model="selectedConnection.encryption" />
              <span>启用加密传输</span>
            </label>
            <label>
              <input type="checkbox" v-model="selectedConnection.caching" />
              <span>启用缓存机制</span>
            </label>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'

// 类型定义
interface NodePort {
  id: string
  label: string
  type: 'data' | 'control' | 'event'
  dataType: 'numeric' | 'text' | 'binary' | 'json'
  position: { x: number, y: number }
}

interface BlueprintNode {
  id: string
  title: string
  description: string
  type: 'data' | 'processor' | 'ai' | 'optimizer' | 'analyzer' | 'output'
  icon: string
  x: number
  y: number
  width: number
  height: number
  active: boolean
  error: boolean
  status: 'active' | 'inactive' | 'error' | 'warning'
  inputPorts: NodePort[]
  outputPorts: NodePort[]
  metrics?: Array<{
    name: string
    label: string
    value: string | number
    type: 'success' | 'warning' | 'error' | 'info'
  }>
}

interface Connection {
  id: string
  from: string
  to: string
  fromPort: string
  toPort: string
  type: 'data-flow' | 'conditional' | 'event' | 'loop'
  dataType: 'numeric' | 'text' | 'binary' | 'json'
  active: boolean
  error: boolean
  throughput?: number
  condition?: string
  compression?: boolean
  encryption?: boolean
  caching?: boolean
  path?: { x: number, y: number }[]
}

interface NodeParameter {
  id: string
  label: string
  type: 'number' | 'text' | 'select' | 'boolean'
  value: any
  min?: number
  max?: number
  step?: number
  options?: Array<{ label: string, value: any }>
  unit?: string
}

// 响应式数据
const nodes = ref<BlueprintNode[]>([
  {
    id: 'data-source-1',
    title: '股票数据源',
    description: '实时股票数据获取',
    type: 'data',
    icon: 'fas fa-database',
    x: 100,
    y: 100,
    width: 200,
    height: 120,
    active: true,
    error: false,
    status: 'active',
    inputPorts: [],
    outputPorts: [
      { id: 'price-data', label: '价格数据', type: 'data', dataType: 'numeric', position: { x: 200, y: 30 } },
      { id: 'volume-data', label: '成交量', type: 'data', dataType: 'numeric', position: { x: 200, y: 60 } },
      { id: 'control-signal', label: '控制信号', type: 'control', dataType: 'binary', position: { x: 200, y: 90 } }
    ],
    metrics: [
      { name: 'throughput', label: '吞吐量', value: '1000/s', type: 'success' },
      { name: 'latency', label: '延迟', value: '45ms', type: 'info' }
    ]
  },
  {
    id: 'processor-1',
    title: '数据预处理',
    description: '清洗和标准化数据',
    type: 'processor',
    icon: 'fas fa-cogs',
    x: 400,
    y: 100,
    width: 200,
    height: 120,
    active: true,
    error: false,
    status: 'active',
    inputPorts: [
      { id: 'input-raw', label: '原始数据', type: 'data', dataType: 'numeric', position: { x: 0, y: 30 } },
      { id: 'input-control', label: '控制参数', type: 'control', dataType: 'text', position: { x: 0, y: 60 } }
    ],
    outputPorts: [
      { id: 'output-clean', label: '清洗数据', type: 'data', dataType: 'numeric', position: { x: 200, y: 45 } },
      { id: 'output-norm', label: '标准化数据', type: 'data', dataType: 'numeric', position: { x: 200, y: 75 } }
    ],
    metrics: [
      { name: 'processing', label: '处理中', value: '256', type: 'warning' },
      { name: 'queue', label: '队列', value: '12', type: 'info' }
    ]
  },
  {
    id: 'ai-model-1',
    title: 'AI预测模型',
    description: '机器学习价格预测',
    type: 'ai',
    icon: 'fas fa-brain',
    x: 700,
    y: 100,
    width: 200,
    height: 120,
    active: true,
    error: false,
    status: 'active',
    inputPorts: [
      { id: 'input-features', label: '特征数据', type: 'data', dataType: 'numeric', position: { x: 0, y: 45 } },
      { id: 'input-target', label: '目标变量', type: 'data', dataType: 'numeric', position: { x: 0, y: 75 } }
    ],
    outputPorts: [
      { id: 'output-prediction', label: '预测结果', type: 'data', dataType: 'numeric', position: { x: 200, y: 45 } },
      { id: 'output-confidence', label: '置信度', type: 'data', dataType: 'numeric', position: { x: 200, y: 75 } }
    ],
    metrics: [
      { name: 'accuracy', label: '准确率', value: '94.2%', type: 'success' },
      { name: 'training', label: '训练状态', value: '运行中', type: 'info' }
    ]
  },
  {
    id: 'strategy-1',
    title: '交易策略',
    description: '基于AI信号的交易策略',
    type: 'optimizer',
    icon: 'fas fa-chart-line',
    x: 1000,
    y: 100,
    width: 200,
    height: 120,
    active: true,
    error: false,
    status: 'active',
    inputPorts: [
      { id: 'input-signal', label: '交易信号', type: 'data', dataType: 'numeric', position: { x: 0, y: 45 } },
      { id: 'input-params', label: '策略参数', type: 'control', dataType: 'text', position: { x: 0, y: 75 } }
    ],
    outputPorts: [
      { id: 'output-orders', label: '交易订单', type: 'data', dataType: 'json', position: { x: 200, y: 45 } },
      { id: 'output-signals', label: '输出信号', type: 'event', dataType: 'binary', position: { x: 200, y: 75 } }
    ],
    metrics: [
      { name: 'performance', label: '收益率', value: '+15.3%', type: 'success' },
      { name: 'sharpe', label: '夏普比率', value: '1.85', type: 'success' }
    ]
  },
  {
    id: 'output-1',
    title: '结果输出',
    description: '最终结果输出模块',
    type: 'output',
    icon: 'fas fa-file-export',
    x: 1300,
    y: 100,
    width: 200,
    height: 120,
    active: true,
    error: false,
    status: 'active',
    inputPorts: [
      { id: 'input-results', label: '结果数据', type: 'data', dataType: 'json', position: { x: 0, y: 45 } },
      { id: 'input-reports', label: '报告数据', type: 'data', dataType: 'text', position: { x: 0, y: 75 } }
    ],
    outputPorts: [],
    metrics: [
      { name: 'exported', label: '已导出', value: '1,234', type: 'info' },
      { name: 'size', label: '文件大小', value: '45.2MB', type: 'info' }
    ]
  }
])

const connections = ref<Connection[]>([
  {
    id: 'conn-1',
    from: 'data-source-1',
    to: 'processor-1',
    fromPort: 'price-data',
    toPort: 'input-raw',
    type: 'data-flow',
    dataType: 'numeric',
    active: true,
    error: false,
    throughput: 1000
  },
  {
    id: 'conn-2',
    from: 'data-source-1',
    to: 'processor-1',
    fromPort: 'volume-data',
    toPort: 'input-raw',
    type: 'data-flow',
    dataType: 'numeric',
    active: true,
    error: false,
    throughput: 800
  },
  {
    id: 'conn-3',
    from: 'processor-1',
    to: 'ai-model-1',
    fromPort: 'output-clean',
    toPort: 'input-features',
    type: 'data-flow',
    dataType: 'numeric',
    active: true,
    error: false,
    throughput: 500
  },
  {
    id: 'conn-4',
    from: 'ai-model-1',
    to: 'strategy-1',
    fromPort: 'output-prediction',
    toPort: 'input-signal',
    type: 'conditional',
    dataType: 'numeric',
    active: true,
    error: false,
    condition: 'confidence > 0.8'
  },
  {
    id: 'conn-5',
    from: 'strategy-1',
    to: 'output-1',
    fromPort: 'output-orders',
    toPort: 'input-results',
    type: 'event',
    dataType: 'json',
    active: true,
    error: false
  }
])

// 工具配置
const connectionTools = ref([
  { id: 'data-flow', name: '数据流', icon: 'fas fa-arrow-right', description: '创建数据流连接' },
  { id: 'conditional', name: '条件', icon: 'fas fa-code-branch', description: '创建条件连接' },
  { id: 'event', name: '事件', icon: 'fas fa-bolt', description: '创建事件连接' },
  { id: 'loop', name: '循环', icon: 'fas fa-sync-alt', description: '创建循环连接' }
])

const layoutTools = ref([
  { id: 'auto-align', name: '自动对齐', icon: 'fas fa-align-center', description: '自动对齐选中节点' },
  { id: 'auto-distribute', name: '均匀分布', icon: 'fas fa-sitemap', description: '均匀分布选中节点' },
  { id: 'force-layout', name: '力导向布局', icon: 'fas fa-project-diagram', description: '应用力导向布局算法' },
  { id: 'hierarchical-layout', name: '层次布局', icon: 'fas fa-sitemap', description: '应用层次布局算法' },
  { id: 'circular-layout', name: '环形布局', icon: 'fas fa-circle-notch', description: '应用环形布局算法' }
])

// 状态变量
const selectedNode = ref<string | null>(null)
const selectedConnection = ref<Connection | null>(null)
const highlightedPort = ref<string | null>(null)
const activeTool = ref<string>('data-flow')
const dataFlowEnabled = ref(true)
const gridEnabled = ref(true)
const autoLayout = ref(false)
const zoomLevel = ref(1)

// 拖拽状态
const isDragging = ref(false)
const draggedNode = ref<BlueprintNode | null>(null)
const dragOffset = ref({ x: 0, y: 0 })

// 上下文菜单状态
const connectionContextMenu = ref({ visible: false, x: 0, y: 0, connection: null as Connection | null })
const nodeContextMenu = ref({ visible: false, x: 0, y: 0, node: null as BlueprintNode | null })

// 引用
const blueprintCanvas = ref<HTMLElement | null>(null)
const gridBackground = ref<HTMLElement | null>(null)
const connectionsLayer = ref<SVGElement | null>(null)
const nodesLayer = ref<HTMLElement | null>(null)

// 计算属性
const getNodeStyle = (node: BlueprintNode) => {
  return {
    left: `${node.x * zoomLevel.value}px`,
    top: `${node.y * zoomLevel.value}px`,
    width: `${node.width * zoomLevel.value}px`,
    height: `${node.height * zoomLevel.value}px`,
    transform: `scale(${zoomLevel.value})`
  }
}

const getPortStyle = (port: NodePort, type: 'input' | 'output') => {
  const position = port.position
  return {
    [type === 'input' ? 'left' : 'right']: `${position.x}px`,
    top: `${position.y}px`
  }
}

const getConnectionPath = (connection: Connection) => {
  const fromNode = nodes.value.find(n => n.id === connection.from)
  const toNode = nodes.value.find(n => n.id === connection.to)
  
  if (!fromNode || !toNode) return ''
  
  const fromPort = fromNode.outputPorts.find(p => p.id === connection.fromPort)
  const toPort = toNode.inputPorts.find(p => p.id === connection.toPort)
  
  if (!fromPort || !toPort) return ''
  
  const startX = fromNode.x + fromNode.width
  const startY = fromNode.y + fromPort.position.y
  const endX = toNode.x
  const endY = toNode.y + toPort.position.y
  
  // 创建智能贝塞尔曲线路径
  const controlPoint1X = startX + (endX - startX) * 0.5
  const controlPoint1Y = startY
  const controlPoint2X = startX + (endX - startX) * 0.5
  const controlPoint2Y = endY
  
  return `M ${startX} ${startY} C ${controlPoint1X} ${controlPoint1Y}, ${controlPoint2X} ${controlPoint2Y}, ${endX} ${endY}`
}

const getConnectionColor = (type: string) => {
  const colorMap = {
    'data-flow': 'url(#dataFlowGradient)',
    'conditional': 'url(#conditionalGradient)',
    'event': 'url(#eventGradient)',
    'loop': 'url(#loopGradient)'
  }
  return colorMap[type] || '#666'
}

const getConnectionWidth = (connection: Connection) => {
  const baseWidth = 2
  const throughputBonus = connection.throughput ? Math.min(connection.throughput / 500, 3) : 0
  return baseWidth + throughputBonus
}

const getConnectionDashArray = (type: string) => {
  const dashMap = {
    'data-flow': 'none',
    'conditional': '5,5',
    'event': '2,2',
    'loop': '10,5'
  }
  return dashMap[type] || 'none'
}

const getConnectionMarker = (type: string) => {
  const markerMap = {
    'data-flow': 'url(#arrowDataFlow)',
    'conditional': 'url(#arrowConditional)',
    'event': 'url(#arrowEvent)',
    'loop': 'url(#arrowLoop)'
  }
  return markerMap[type] || 'url(#arrowDataFlow)'
}

const getConnectionParticles = (connection: Connection) => {
  if (!connection.active || !dataFlowEnabled.value) return []
  
  const particleCount = Math.floor((connection.throughput || 100) / 100)
  return Array.from({ length: particleCount }, (_, i) => ({
    id: i,
    offset: i * 15
  }))
}

const getParticleStyle = (particle: any, connection: Connection) => {
  const pathLength = 100 // 简化的路径长度
  const progress = (particle.offset % pathLength) / pathLength
  
  return {
    animation: `dataFlow ${3 + Math.random() * 2}s linear infinite`,
    offset: `${progress * 100}%`
  }
}

const isPortOccupied = (nodeId: string, portId: string, type: 'input' | 'output') => {
  return connections.value.some(conn => {
    if (type === 'input') {
      return conn.to === nodeId && conn.toPort === portId
    } else {
      return conn.from === nodeId && conn.fromPort === portId
    }
  })
}

// 方法
const setActiveTool = (toolId: string) => {
  activeTool.value = toolId
}

const startDragNode = (event: MouseEvent, node: BlueprintNode) => {
  if (event.button !== 0) return // 只响应左键
  
  isDragging.value = true
  draggedNode.value = node
  
  const rect = (event.target as HTMLElement).getBoundingClientRect()
  dragOffset.value = {
    x: event.clientX - rect.left,
    y: event.clientY - rect.top
  }
  
  document.addEventListener('mousemove', handleDragMove)
  document.addEventListener('mouseup', handleDragEnd)
  
  event.preventDefault()
}

const handleDragMove = (event: MouseEvent) => {
  if (!isDragging.value || !draggedNode.value) return
  
  const canvasRect = blueprintCanvas.value?.getBoundingClientRect()
  if (!canvasRect) return
  
  const newX = (event.clientX - canvasRect.left - dragOffset.value.x) / zoomLevel.value
  const newY = (event.clientY - canvasRect.top - dragOffset.value.y) / zoomLevel.value
  
  // 网格对齐
  const gridSize = 20
  draggedNode.value.x = Math.round(newX / gridSize) * gridSize
  draggedNode.value.y = Math.round(newY / gridSize) * gridSize
}

const handleDragEnd = () => {
  isDragging.value = false
  draggedNode.value = null
  
  document.removeEventListener('mousemove', handleDragMove)
  document.removeEventListener('mouseup', handleDragEnd)
}

const highlightPort = (portId: string) => {
  highlightedPort.value = portId
}

const unhighlightPort = () => {
  highlightedPort.value = null
}

const handlePortClick = (event: MouseEvent, node: BlueprintNode, port: NodePort, portType: 'input' | 'output') => {
  event.stopPropagation()
  
  if (activeTool.value === 'data-flow') {
    // 数据流连接逻辑
    console.log('创建数据流连接:', node.id, port.id, portType)
  }
  // 其他连接类型的处理逻辑...
}

const selectConnection = (connection: Connection) => {
  selectedConnection.value = connection
}

const showConnectionContextMenu = (event: MouseEvent, connection: Connection) => {
  event.preventDefault()
  connectionContextMenu.value = {
    visible: true,
    x: event.clientX,
    y: event.clientY,
    connection
  }
}

const showNodeContextMenu = (event: MouseEvent, node: BlueprintNode) => {
  event.preventDefault()
  nodeContextMenu.value = {
    visible: true,
    x: event.clientX,
    y: event.clientY,
    node
  }
}

const editConnection = (connection: Connection) => {
  selectedConnection.value = connection
  connectionContextMenu.value.visible = false
}

const deleteConnection = (connection: Connection) => {
  const index = connections.value.findIndex(c => c.id === connection.id)
  if (index > -1) {
    connections.value.splice(index, 1)
  }
  connectionContextMenu.value.visible = false
}

const setConnectionType = (connection: Connection, type: string) => {
  connection.type = type as any
  connectionContextMenu.value.visible = false
}

const openNodeDetails = (node: BlueprintNode) => {
  console.log('打开节点详情:', node.id)
  // 这里可以触发节点详情面板显示
}

const duplicateNode = (node: BlueprintNode) => {
  const newNode = {
    ...node,
    id: `${node.id}-copy-${Date.now()}`,
    x: node.x + 50,
    y: node.y + 50
  }
  nodes.value.push(newNode)
  nodeContextMenu.value.visible = false
}

const deleteNode = (node: BlueprintNode) => {
  const index = nodes.value.findIndex(n => n.id === node.id)
  if (index > -1) {
    nodes.value.splice(index, 1)
    // 删除相关连接
    connections.value = connections.value.filter(c => c.from !== node.id && c.to !== node.id)
  }
  nodeContextMenu.value.visible = false
}

const groupNodes = (nodesToGroup: BlueprintNode[]) => {
  console.log('创建节点分组:', nodesToGroup.map(n => n.id))
  nodeContextMenu.value.visible = false
}

const executeLayoutTool = (toolId: string) => {
  switch (toolId) {
    case 'auto-align':
      autoAlignNodes()
      break
    case 'auto-distribute':
      autoDistributeNodes()
      break
    case 'force-layout':
      applyForceLayout()
      break
    case 'hierarchical-layout':
      applyHierarchicalLayout()
      break
    case 'circular-layout':
      applyCircularLayout()
      break
  }
}

const autoAlignNodes = () => {
  // 自动对齐选中节点的实现
  console.log('执行自动对齐')
}

const autoDistributeNodes = () => {
  // 均匀分布选中节点的实现
  console.log('执行均匀分布')
}

const applyForceLayout = () => {
  // 力导向布局算法的实现
  console.log('应用力导向布局')
}

const applyHierarchicalLayout = () => {
  // 层次布局算法的实现
  console.log('应用层次布局')
}

const applyCircularLayout = () => {
  // 环形布局算法的实现
  console.log('应用环形布局')
}

// 监听点击空白区域关闭上下文菜单
document.addEventListener('click', () => {
  connectionContextMenu.value.visible = false
  nodeContextMenu.value.visible = false
})

// 生命周期
onMounted(() => {
  nextTick(() => {
    initializeGrid()
    initializeCanvas()
  })
})

onUnmounted(() => {
  document.removeEventListener('mousemove', handleDragMove)
  document.removeEventListener('mouseup', handleDragEnd)
})

// 初始化方法
const initializeGrid = () => {
  if (gridBackground.value) {
    const canvas = document.createElement('canvas')
    const ctx = canvas.getContext('2d')
    
    if (!ctx) return
    
    canvas.width = 2000
    canvas.height = 2000
    canvas.style.position = 'absolute'
    canvas.style.top = '0'
    canvas.style.left = '0'
    canvas.style.pointerEvents = 'none'
    
    // 绘制网格
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.1)'
    ctx.lineWidth = 1
    
    const gridSize = 20
    for (let x = 0; x <= canvas.width; x += gridSize) {
      ctx.beginPath()
      ctx.moveTo(x, 0)
      ctx.lineTo(x, canvas.height)
      ctx.stroke()
    }
    
    for (let y = 0; y <= canvas.height; y += gridSize) {
      ctx.beginPath()
      ctx.moveTo(0, y)
      ctx.lineTo(canvas.width, y)
      ctx.stroke()
    }
    
    gridBackground.value.appendChild(canvas)
  }
}

const initializeCanvas = () => {
  // 初始化画布设置
  if (blueprintCanvas.value) {
    // 设置画布大小和滚动行为
  }
}
</script>

<style lang="scss" scoped>
.unreal-blueprint-system {
  position: relative;
  width: 100%;
  height: 100%;
  background: #0a0a0f;
  color: #f8fafc;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  overflow: hidden;
  
  .blueprint-canvas {
    position: relative;
    width: 100%;
    height: 100%;
    overflow: auto;
    transform-origin: 0 0;
    
    .grid-background {
      position: absolute;
      top: 0;
      left: 0;
      width: 2000px;
      height: 2000px;
      pointer-events: none;
      opacity: 0.3;
    }
    
    .connections-layer {
      position: absolute;
      top: 0;
      left: 0;
      width: 2000px;
      height: 2000px;
      pointer-events: none;
      z-index: 1;
      
      .connection-path {
        cursor: pointer;
        pointer-events: all;
        transition: all 0.3s ease;
        
        &:hover {
          stroke-width: 4;
          filter: brightness(1.2);
        }
        
        &.connection-active {
          animation: connectionPulse 2s ease-in-out infinite;
        }
        
        &.connection-error {
          stroke: #ff4444;
          stroke-dasharray: 5,5;
          animation: errorBlink 1s ease-in-out infinite;
        }
        
        &.connection-selected {
          stroke-width: 4;
          filter: drop-shadow(0 0 8px rgba(102, 126, 234, 0.6));
        }
      }
      
      .data-particle {
        animation: dataFlowParticle 3s linear infinite;
      }
    }
    
    .nodes-layer {
      position: absolute;
      top: 0;
      left: 0;
      width: 2000px;
      height: 2000px;
      z-index: 2;
      
      .blueprint-node {
        position: absolute;
        background: rgba(26, 26, 46, 0.9);
        backdrop-filter: blur(10px);
        border: 2px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        cursor: move;
        transition: all 0.3s ease;
        user-select: none;
        
        &:hover {
          border-color: #7c3aed;
          box-shadow: 0 8px 32px rgba(124, 58, 237, 0.3);
          transform: scale(1.02);
        }
        
        &.node-selected {
          border-color: #2563eb;
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
        
        .node-body {
          padding: 16px;
          
          .node-header {
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 12px;
            
            .node-icon {
              width: 32px;
              height: 32px;
              display: flex;
              align-items: center;
              justify-content: center;
              background: rgba(124, 58, 237, 0.1);
              border-radius: 8px;
              color: #7c3aed;
              font-size: 16px;
            }
            
            .node-title {
              flex: 1;
              font-size: 16px;
              font-weight: 600;
              color: #f8fafc;
            }
            
            .node-status {
              .status-dot {
                width: 8px;
                height: 8px;
                border-radius: 50%;
                background: #6b7280;
              }
            }
          }
          
          .node-content {
            .node-description {
              font-size: 12px;
              color: #cbd5e1;
              margin-bottom: 8px;
              line-height: 1.4;
            }
            
            .node-metrics {
              display: flex;
              flex-wrap: wrap;
              gap: 8px;
              
              .metric-item {
                display: flex;
                align-items: center;
                gap: 4px;
                padding: 4px 8px;
                background: rgba(255, 255, 255, 0.05);
                border-radius: 4px;
                font-size: 11px;
                
                .metric-label {
                  color: #cbd5e1;
                }
                
                .metric-value {
                  font-weight: 600;
                  
                  &.success {
                    color: var(--market-rise);
                  }
                  
                  &.warning {
                    color: #f59e0b;
                  }
                  
                  &.error {
                    color: var(--market-fall);
                  }
                  
                  &.info {
                    color: #3b82f6;
                  }
                }
              }
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
            cursor: pointer;
            pointer-events: all;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            
            &.port-input {
              background: #0088ff;
              left: -8px;
              
              &.port-highlighted {
                box-shadow: 0 0 12px rgba(0, 136, 255, 0.6);
                transform: scale(1.2);
              }
              
              &.port-occupied {
                background: #0066cc;
              }
            }
            
            &.port-output {
              background: #00ff88;
              right: -8px;
              
              &.port-highlighted {
                box-shadow: 0 0 12px rgba(0, 255, 136, 0.6);
                transform: scale(1.2);
              }
              
              &.port-occupied {
                background: #00cc66;
              }
            }
            
            .port-indicator {
              width: 6px;
              height: 6px;
              border-radius: 50%;
              background: rgba(255, 255, 255, 0.8);
            }
            
            .port-label {
              position: absolute;
              font-size: 10px;
              color: var(--text-secondary);
              white-space: nowrap;
              pointer-events: none;
              
              .port-input & {
                right: 20px;
                top: 50%;
                transform: translateY(-50%);
              }
              
              .port-output & {
                left: 20px;
                top: 50%;
                transform: translateY(-50%);
              }
            }
          }
        }
        
        // 节点类型样式
        &.node-type-data {
          .node-icon {
            background: rgba(0, 136, 255, 0.1);
            color: #0088ff;
          }
        }
        
        &.node-type-processor {
          .node-icon {
            background: rgba(255, 170, 0, 0.1);
            color: #ffaa00;
          }
        }
        
        &.node-type-ai {
          .node-icon {
            background: rgba(124, 58, 237, 0.1);
            color: var(--secondary);
          }
        }
        
        &.node-type-optimizer {
          .node-icon {
            background: rgba(16, 185, 129, 0.1);
            color: var(--market-rise);
          }
        }
        
        &.node-type-analyzer {
          .node-icon {
            background: rgba(245, 158, 11, 0.1);
            color: #f59e0b;
          }
        }
        
        &.node-type-output {
          .node-icon {
            background: rgba(239, 68, 68, 0.1);
            color: var(--market-fall);
          }
        }
      }
    }
  }
  
  .blueprint-toolbar {
    position: fixed;
    top: 20px;
    right: 20px;
    width: 300px;
    background: rgba(26, 26, 46, 0.95);
    backdrop-filter: blur(20px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 12px;
    padding: 20px;
    z-index: 10;
    
    .toolbar-section {
      margin-bottom: 20px;
      
      h4 {
        margin: 0 0 12px 0;
        font-size: 14px;
        font-weight: 600;
        color: var(--text-primary);
      }
      
      .tool-buttons {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        
        .tool-btn {
          display: flex;
          align-items: center;
          gap: 6px;
          padding: 8px 12px;
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
            background: var(--secondary);
            color: white;
            border-color: var(--secondary);
          }
          
          i {
            font-size: 14px;
          }
        }
      }
      
      .view-options {
        .option-item {
          display: flex;
          align-items: center;
          gap: 8px;
          margin-bottom: 8px;
          font-size: 12px;
          
          input[type="checkbox"] {
            width: 16px;
            height: 16px;
          }
          
          input[type="range"] {
            flex: 1;
          }
        }
      }
    }
  }
  
  .context-menu {
    position: fixed;
    background: rgba(26, 26, 46, 0.95);
    backdrop-filter: blur(20px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 8px;
    padding: 8px 0;
    z-index: 100;
    min-width: 180px;
    
    .menu-item {
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 8px 16px;
      color: var(--text-primary);
      font-size: 12px;
      cursor: pointer;
      transition: background 0.3s ease;
      
      &:hover {
        background: rgba(255, 255, 255, 0.1);
      }
      
      i {
        width: 16px;
        text-align: center;
      }
    }
    
    .menu-separator {
      height: 1px;
      background: rgba(255, 255, 255, 0.1);
      margin: 4px 0;
    }
  }
  
  .connection-properties-panel {
    position: fixed;
    bottom: 20px;
    right: 20px;
    width: 350px;
    max-height: 400px;
    background: rgba(26, 26, 46, 0.95);
    backdrop-filter: blur(20px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 12px;
    z-index: 10;
    
    .panel-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 16px 20px;
      border-bottom: 1px solid rgba(255, 255, 255, 0.1);
      
      h3 {
        margin: 0;
        font-size: 16px;
        font-weight: 600;
        color: var(--text-primary);
      }
      
      .close-btn {
        width: 24px;
        height: 24px;
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 4px;
        color: var(--text-secondary);
        cursor: pointer;
        
        &:hover {
          background: rgba(255, 255, 255, 0.1);
          color: var(--text-primary);
        }
      }
    }
    
    .panel-content {
      padding: 20px;
      max-height: 300px;
      overflow-y: auto;
      
      .property-group {
        margin-bottom: 16px;
        
        label {
          display: block;
          margin-bottom: 6px;
          font-size: 12px;
          color: var(--text-secondary);
          font-weight: 500;
        }
        
        select, input {
          width: 100%;
          padding: 8px 12px;
          background: rgba(255, 255, 255, 0.05);
          border: 1px solid rgba(255, 255, 255, 0.1);
          border-radius: 6px;
          color: var(--text-primary);
          font-size: 12px;
          
          &:focus {
            outline: none;
            border-color: var(--secondary);
          }
        }
        
        .checkbox-group {
          display: flex;
          flex-direction: column;
          gap: 8px;
          
          label {
            display: flex;
            align-items: center;
            gap: 8px;
            margin-bottom: 0;
          }
        }
        
        .unit {
          font-size: 11px;
          color: var(--text-secondary);
          margin-left: 4px;
        }
      }
    }
  }
}

// 动画
@keyframes connectionPulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.6;
  }
}

@keyframes errorBlink {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.3;
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

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}
</style>
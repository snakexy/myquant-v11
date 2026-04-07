<template>
  <div class="circuit-board-container">
    <!-- 控制面板 -->
    <div class="control-panel">
      <div class="function-selector">
        <h3>功能选择器</h3>
        <div class="function-buttons">
          <button 
            v-for="func in functions" 
            :key="func.id"
            :class="['function-btn', { active: activeFunctions.includes(func.id) }]"
            @click="toggleFunction(func.id)"
          >
            <i :class="func.icon"></i>
            <span>{{ func.name }}</span>
          </button>
        </div>
      </div>
      
      <div class="activation-controls">
        <h3>激活控制</h3>
        <button class="activate-all-btn" @click="activateAllSelected">
          <i class="fas fa-play"></i> 激活选中功能
        </button>
        <button class="deactivate-all-btn" @click="deactivateAll">
          <i class="fas fa-stop"></i> 全部取消激活
        </button>
        <button class="auto-optimize-btn" @click="autoOptimize">
          <i class="fas fa-magic"></i> 自动优化
        </button>
      </div>
      
      <div class="view-controls">
        <h3>视图控制</h3>
        <div class="zoom-controls">
          <button @click="zoomIn"><i class="fas fa-search-plus"></i></button>
          <button @click="zoomOut"><i class="fas fa-search-minus"></i></button>
          <button @click="resetView"><i class="fas fa-compress"></i></button>
        </div>
        <div class="view-modes">
          <button 
            v-for="mode in viewModes" 
            :key="mode.id"
            :class="['view-mode-btn', { active: currentViewMode === mode.id }]"
            @click="setViewMode(mode.id)"
          >
            {{ mode.name }}
          </button>
        </div>
      </div>
    </div>

    <!-- 主电路板画布 -->
    <div class="circuit-board" ref="circuitBoard">
      <canvas 
        ref="canvas" 
        :width="canvasWidth" 
        :height="canvasHeight"
        @click="handleCanvasClick"
        @mousemove="handleCanvasMouseMove"
        @wheel="handleCanvasWheel"
      ></canvas>
      
      <!-- SVG覆盖层用于连接线 -->
      <svg class="connections-layer" :width="canvasWidth" :height="canvasHeight">
        <defs>
          <!-- 电流效果渐变 -->
          <linearGradient id="currentGradient" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" style="stop-color:#00ff88;stop-opacity:0" />
            <stop offset="50%" style="stop-color:#00ff88;stop-opacity:1" />
            <stop offset="100%" style="stop-color:#00ff88;stop-opacity:0" />
          </linearGradient>
          
          <!-- 数据流渐变 -->
          <linearGradient id="dataFlowGradient" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" style="stop-color:#00aaff;stop-opacity:0" />
            <stop offset="50%" style="stop-color:#00aaff;stop-opacity:1" />
            <stop offset="100%" style="stop-color:#00aaff;stop-opacity:0" />
          </linearGradient>
          
          <!-- 控制流渐变 -->
          <linearGradient id="controlFlowGradient" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" style="stop-color:#ff6600;stop-opacity:0" />
            <stop offset="50%" style="stop-color:#ff6600;stop-opacity:1" />
            <stop offset="100%" style="stop-color:#ff6600;stop-opacity:0" />
          </linearGradient>
          
          <!-- 发光效果滤镜 -->
          <filter id="glow">
            <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
            <feMerge>
              <feMergeNode in="coloredBlur"/>
              <feMergeNode in="SourceGraphic"/>
            </feMerge>
          </filter>
          
          <!-- 强发光效果滤镜 -->
          <filter id="strongGlow">
            <feGaussianBlur stdDeviation="6" result="coloredBlur"/>
            <feMerge>
              <feMergeNode in="coloredBlur"/>
              <feMergeNode in="SourceGraphic"/>
            </feMerge>
          </filter>
          
          <!-- 脉冲效果滤镜 -->
          <filter id="pulse">
            <feGaussianBlur stdDeviation="2" result="coloredBlur"/>
            <feMerge>
              <feMergeNode in="coloredBlur"/>
              <feMergeNode in="SourceGraphic"/>
            </feMerge>
          </filter>
        </defs>
        
        <!-- 连接线背景层 -->
        <g v-for="connection in visibleConnections" :key="'bg-' + connection.id">
          <path
            :d="connection.path"
            :class="['connection-line-bg', connection.type]"
            stroke="#1a1a2e"
            stroke-width="5"
            fill="none"
            opacity="0.3"
          />
        </g>
        
        <!-- 连接线主体层 -->
        <g v-for="connection in visibleConnections" :key="connection.id">
          <path
            :d="connection.path"
            :class="['connection-line', connection.type, { 
              active: connection.active,
              highlighted: connection.highlighted,
              'workflow-highlighted': connection.highlighted
            }]"
            :stroke="getConnectionColor(connection)"
            :stroke-width="getConnectionWidth(connection)"
            :filter="getConnectionFilter(connection)"
            fill="none"
            stroke-linecap="round"
          />
          
          <!-- 数据流向箭头 -->
          <g v-if="connection.highlighted && connection.workflowType">
            <defs>
              <marker :id="'arrowhead-' + connection.id" 
                markerWidth="10" markerHeight="7" 
                refX="9" refY="3.5" orient="auto">
                <polygon 
                  points="0 0, 10 3.5, 0 7" 
                  :fill="getConnectionColor(connection)"
                />
              </marker>
            </defs>
            
            <!-- 添加箭头到路径末端 -->
            <path
              :d="connection.path"
              :stroke="getConnectionColor(connection)"
              :stroke-width="getConnectionWidth(connection)"
              fill="none"
              :marker-end="'url(#arrowhead-' + connection.id + ')'"
              stroke-linecap="round"
              opacity="0.8"
            />
          </g>
          
          <!-- 电流动画效果 -->
          <g v-if="connection.active || connection.highlighted">
            <!-- 主电流粒子 -->
            <circle r="4" :fill="getConnectionColor(connection)" :filter="getConnectionFilter(connection)">
              <animateMotion
                :dur="connection.animationDuration + 's'"
                repeatCount="indefinite"
                :path="connection.path"
              />
            </circle>
             
            <!-- 次要电流粒子 -->
            <circle r="2" :fill="getConnectionColor(connection)" opacity="0.6">
              <animateMotion
                :dur="(connection.animationDuration * 0.7) + 's'"
                repeatCount="indefinite"
                :path="connection.path"
                begin="0.5s"
              />
            </circle>
             
            <!-- 脉冲效果 -->
            <circle r="6" :fill="getConnectionColor(connection)" opacity="0.3" filter="url(#pulse)">
              <animateMotion
                :dur="(connection.animationDuration * 1.5) + 's'"
                repeatCount="indefinite"
                :path="connection.path"
                begin="1s"
              />
            </circle>
          </g>
        </g>
      </svg>
      
      <!-- 节点层 -->
      <div class="nodes-layer" :style="transformStyle">
        <div
          v-for="node in visibleNodes"
          :key="node.cacheKey || node.id"
          :class="['circuit-node', node.status, {
            active: node.status === 'ACTIVE' || node.status === 'RUNNING',
            recommended: node.status === 'RECOMMENDED',
            error: node.status === 'ERROR',
            high_priority: node.status === 'HIGH_PRIORITY'
          }]"
          :style="{
            left: node.x + 'px',
            top: node.y + 'px',
            width: node.width + 'px',
            height: node.height + 'px'
          }"
          @click="selectNode(node)"
          @mouseenter="hoverNode(node)"
          @mouseleave="unhoverNode()"
        >
          <!-- 节点背景装饰 -->
          <div class="node-background-decoration">
            <div class="circuit-pattern"></div>
            <div class="node-glow" v-if="node.status === 'ACTIVE' || node.status === 'RUNNING'"></div>
          </div>
          
          <!-- 节点核心 -->
          <div class="node-core">
            <div class="node-icon">
              <i :class="node.metadata.icon"></i>
            </div>
            <div class="node-label">{{ node.name }}</div>
            <div class="node-complexity" v-if="node.activationComplexity">
              <span v-for="i in node.activationComplexity" :key="i" class="complexity-dot"></span>
            </div>
          </div>
          
          <!-- 节点端口 -->
          <div class="node-ports">
            <div
              v-for="port in node.ports"
              :key="port.id"
              :class="['port', port.type, { active: port.active }]"
              :style="port.style"
            >
              <div class="port-glow" v-if="port.active"></div>
            </div>
          </div>
          
          <!-- 节点状态指示器 -->
          <div class="node-status-indicator">
            <div class="status-light" :class="node.status.toLowerCase()">
              <div class="status-pulse" v-if="node.status === 'ACTIVE' || node.status === 'RUNNING'"></div>
            </div>
          </div>
          
          <!-- 节点活动指示器 -->
          <div class="node-activity-indicator" v-if="node.status === 'ACTIVE' || node.status === 'RUNNING'">
            <div class="activity-wave"></div>
          </div>
        </div>
      </div>
      
      <!-- 悬浮信息面板 -->
      <div 
        v-if="hoveredNode" 
        class="node-info-panel"
        :style="{
          left: hoveredNode.x + hoveredNode.width + 10 + 'px',
          top: hoveredNode.y + 'px'
        }"
      >
        <h4>{{ hoveredNode.name }}</h4>
        <p>{{ hoveredNode.metadata.description }}</p>
        <div class="node-stats">
          <div class="stat">
            <span class="label">状态:</span>
            <span class="value" :class="hoveredNode.status.toLowerCase()">{{ hoveredNode.status }}</span>
          </div>
          <div class="stat">
            <span class="label">层级:</span>
            <span class="value">{{ hoveredNode.metadata.layer }}</span>
          </div>
          <div class="stat">
            <span class="label">复杂度:</span>
            <span class="value">{{ hoveredNode.activationComplexity }}</span>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 状态栏 -->
    <div class="status-bar">
      <div class="status-info">
        <span class="status-item">
          <i class="fas fa-microchip"></i>
          总节点: {{ totalNodes }}
        </span>
        <span class="status-item">
          <i class="fas fa-plug"></i>
          激活节点: {{ activeNodes }}
        </span>
        <span class="status-item">
          <i class="fas fa-bolt"></i>
          活跃连接: {{ activeConnections }}
        </span>
        <span class="status-item">
          <i class="fas fa-tachometer-alt"></i>
          系统负载: {{ systemLoad }}%
        </span>
      </div>
      <div class="status-actions">
        <button @click="exportConfiguration"><i class="fas fa-download"></i> 导出配置</button>
        <button @click="importConfiguration"><i class="fas fa-upload"></i> 导入配置</button>
        <button @click="resetSystem"><i class="fas fa-redo"></i> 重置系统</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { nodeStateManager } from '@/services/node-state-manager'
import { architectureBasedActivator } from '@/services/architecture-based-activator'
import type { NodeStateInfo, ArchitectureConnection, ExtendedNodeStatus } from '@/types/node-system'

// 响应式数据
const canvas = ref<HTMLCanvasElement>()
const circuitBoard = ref<HTMLDivElement>()
const hoveredNode = ref<NodeStateInfo | null>(null)
const selectedNode = ref<NodeStateInfo | null>(null)
const activeFunctions = ref<string[]>([])
const currentViewMode = ref('circuit')
const zoom = ref(1)
const panX = ref(0)
const panY = ref(0)

// 画布尺寸
const canvasWidth = ref(1920)
const canvasHeight = ref(1080)

// 功能定义 - 更新为五大工作流程
const functions = ref([
  {
    id: 'ai-strategy-generation',
    name: 'AI策略生成',
    icon: 'fas fa-brain',
    description: 'AI策略生成流程：从数据获取到AI策略生成的完整链路'
  },
  {
    id: 'traditional-strategy-execution',
    name: '传统策略执行',
    icon: 'fas fa-chart-line',
    description: '传统策略执行流程：基于规则和传统量化方法的策略执行'
  },
  {
    id: 'model-training',
    name: '模型训练',
    icon: 'fas fa-graduation-cap',
    description: '模型训练流程：机器学习模型的训练、验证和部署'
  },
  {
    id: 'qlib-online-service',
    name: 'QLib在线服务',
    icon: 'fas fa-server',
    description: 'QLib在线服务工作流程：提供QLib功能的在线服务和实验管理'
  },
  {
    id: 'qlib-integration-workflow',
    name: 'QLib集成与工作流管理',
    icon: 'fas fa-project-diagram',
    description: 'QLib集成与工作流管理流程：协调所有组件的工作'
  }
])

// 视图模式
const viewModes = ref([
  { id: 'circuit', name: '电路板' },
  { id: 'layer', name: '层级' },
  { id: 'function', name: '功能' },
  { id: '3d', name: '3D视图' }
])

// 节点和连接数据
const allNodes = ref<NodeStateInfo[]>([])
const allConnections = ref<ArchitectureConnection[]>([])

// 性能优化：使用缓存避免重复计算
const nodeCache = ref<Map<string, NodeStateInfo>>(new Map())
const connectionCache = ref<Map<string, ArchitectureConnection>>(new Map())

// 计算属性
const transformStyle = computed(() =>({
  transform: `translate(${panX.value}px, ${panY.value}px) scale(${zoom.value})`,
  transformOrigin: '0 0'
}))

const visibleNodes = computed(() => {
  let nodes = allNodes.value
  
  // 根据视图模式过滤节点
  if (currentViewMode.value === 'layer') {
    nodes = nodes.sort((a, b) => {
      const layerOrder = ['data_hub', 'qlib_core', 'business_logic', 'ai_strategy', 'live_trading', 'experiment_mgmt', 'frontend']
      return layerOrder.indexOf(a.metadata.layer) - layerOrder.indexOf(b.metadata.layer)
    })
  }
  
  // 性能优化：限制可见节点数量
  if (nodes.length > 100) {
    console.warn(`节点数量过多 (${nodes.length})，限制显示前100个节点以保持性能`)
    return nodes.slice(0, 100)
  }
  
  // 性能优化：为节点添加缓存键
  return nodes.map(node => ({
    ...node,
    cacheKey: `${node.id}-${node.status}-${node.x}-${node.y}`
  }))
})

const visibleConnections = computed(() => {
  // 性能优化：使用缓存避免重复计算
  const cacheKey = `${allNodes.value.length}-${activeFunctions.value.join(',')}-${currentViewMode.value}`
  
  if (connectionCache.value.has(cacheKey)) {
    return connectionCache.value.get(cacheKey) || []
  }
  
  const connections = allConnections.value.map(conn =>({
    ...conn,
    path: calculateConnectionPath(conn),
    active: isConnectionActive(conn),
    animationDuration: 2 + Math.random() * 2,
    highlighted: isConnectionInActiveWorkflow(conn),
    workflowType: getConnectionWorkflowType(conn)
  }))
  
  // 缓存结果
  connectionCache.value.set(cacheKey, connections)
  
  // 限制缓存大小
  if (connectionCache.value.size > 10) {
    const firstKey = connectionCache.value.keys().next().value
    if (firstKey) {
      connectionCache.value.delete(firstKey)
    }
  }
  
  return connections
})

const totalNodes = computed(() => allNodes.value.length)
const activeNodes = computed(() => allNodes.value.filter(n => 
  n.status === 'ACTIVE' || n.status === 'RUNNING'
).length)
const activeConnections = computed(() => allConnections.value.filter(c => 
  isConnectionActive(c)
).length)
const systemLoad = computed(() => {
  const activeCount = activeNodes.value
  const totalCount = totalNodes.value
  return totalCount > 0 ? Math.round((activeCount / totalCount) * 100) : 0
})

// 方法
const initializeCircuitBoard = async () => {
  // 获取所有节点状态
  allNodes.value = nodeStateManager.getAllNodes()
  
  // 生成架构连接
  allConnections.value = generateArchitectureConnections()
  
  // 初始化画布
  if (canvas.value) {
    const ctx = canvas.value.getContext('2d')
    if (ctx) {
      drawCircuitBoardBackground(ctx)
    }
  }
  
  // 初始化节点状态
  await updateNodeStates()
}

// 更新节点状态
const updateNodeStates = async () => {
  const context = {
    userId: 'circuit-board',
    sessionId: 'circuit-board-session',
    systemState: {
      cpuUsage: systemLoad.value,
      memoryUsage: systemLoad.value,
      apiStatus: [],
      activeWorkflows: activeFunctions.value,
      systemLoad: systemLoad.value
    },
    currentTime: new Date(),
    userLevel: 'expert' as any,
    activeNodes: [],
    parameters: {},
    currentWorkflow: activeFunctions.value[0] || 'ai-strategy-generation'
  }
  
  await nodeStateManager.updateAllNodeStates(context)
  allNodes.value = nodeStateManager.getAllNodes()
  
  // 清除缓存
  nodeCache.value.clear()
  connectionCache.value.clear()
}

const generateArchitectureConnections = (): ArchitectureConnection[] => {
  const connections: ArchitectureConnection[] = []
  const nodes = allNodes.value
  
  // 生成层级内连接（优化版）
  const layers = ['data_hub', 'qlib_core', 'business_logic', 'ai_strategy', 'live_trading', 'experiment_mgmt', 'frontend']
  
  layers.forEach(layer => {
    const layerNodes = nodes.filter(n => n.metadata.layer === layer)
    
    // 层级内部连接 - 使用更智能的连接策略
    if (layerNodes.length > 1) {
      // 按节点复杂度排序，优先连接重要节点
      const sortedNodes = [...layerNodes].sort((a, b) => (b.activationComplexity || 0) - (a.activationComplexity || 0))
      
      // 创建网状连接而不是线性连接
      for (let i = 0; i < sortedNodes.length; i++) {
        for (let j = i + 1; j < sortedNodes.length; j++) {
          // 只连接复杂度较高的节点到其他节点
          if (sortedNodes[i].activationComplexity >= 3 || sortedNodes[j].activationComplexity >= 3) {
            connections.push({
              id: `${layer}-internal-${i}-${j}`,
              from: sortedNodes[i].id,
              to: sortedNodes[j].id,
              type: 'data',
              strength: 0.8,
              description: `${layer}层内部数据流`,
              bidirectional: true // 层级内部使用双向连接
            })
          }
        }
      }
    }
  })
  
  // 生成跨层连接（优化版）
  for (let i = 0; i < layers.length - 1; i++) {
    const currentLayer = layers[i]
    const nextLayer = layers[i + 1]
    
    const currentNodes = nodes.filter(n => n.metadata.layer === currentLayer)
    const nextNodes = nodes.filter(n => n.metadata.layer === nextLayer)
    
    if (currentNodes.length > 0 && nextNodes.length > 0) {
      // 创建多个跨层连接，提高连接密度
      const maxConnections = Math.min(3, currentNodes.length, nextNodes.length)
      
      for (let j = 0; j < maxConnections; j++) {
        const fromNode = currentNodes[Math.floor(j * currentNodes.length / maxConnections)]
        const toNode = nextNodes[Math.floor(j * nextNodes.length / maxConnections)]
        
        connections.push({
          id: `${currentLayer}-to-${nextLayer}-${j}`,
          from: fromNode.id,
          to: toNode.id,
          type: 'control',
          strength: 0.9,
          description: `${currentLayer}到${nextLayer}的控制流`,
          bidirectional: false
        })
      }
    }
  }
  
  // 添加特殊功能连接（基于实际依赖关系）
  addSpecialFunctionConnections(connections, nodes)
  
  return connections
}

// 添加特殊功能连接
const addSpecialFunctionConnections = (connections: ArchitectureConnection[], nodes: NodeStateInfo[]) => {
  // 数据管理特殊连接
  const dataNodes = nodes.filter(n => n.metadata.category === 'data')
  addMeshConnections(connections, dataNodes, 'data', '数据管理网状连接')
  
  // AI策略特殊连接
  const aiNodes = nodes.filter(n => n.metadata.category === 'ai')
  addMeshConnections(connections, aiNodes, 'dependency', 'AI策略网状连接')
  
  // 交易系统特殊连接
  const tradingNodes = nodes.filter(n => n.metadata.category === 'trading')
  addMeshConnections(connections, tradingNodes, 'control', '交易系统网状连接')
  
  // 监控系统特殊连接
  const monitoringNodes = nodes.filter(n => n.metadata.category === 'monitoring')
  addMeshConnections(connections, monitoringNodes, 'data', '监控系统网状连接')
}

// 添加网状连接
const addMeshConnections = (
  connections: ArchitectureConnection[],
  nodes: NodeStateInfo[],
  type: string,
  description: string
) => {
  // 为重要节点创建网状连接
  const importantNodes = nodes.filter(n => n.activationComplexity >= 4)
  
  importantNodes.forEach((node, i) => {
    // 连接到其他重要节点
    importantNodes.forEach((otherNode, j) => {
      if (i !== j && Math.random() > 0.3) { // 70%概率创建连接
        connections.push({
          id: `mesh-${type}-${i}-${j}`,
          from: node.id,
          to: otherNode.id,
          type: type as any,
          strength: 0.7,
          description: description,
          bidirectional: true
        })
      }
    })
  })
}

const calculateConnectionPath = (connection: ArchitectureConnection): string => {
  const fromNode = allNodes.value.find(n => n.id === connection.from)
  const toNode = allNodes.value.find(n => n.id === connection.to)
  
  if (!fromNode || !toNode) return ''
  
  const fromX = fromNode.x + fromNode.width / 2
  const fromY = fromNode.y + fromNode.height / 2
  const toX = toNode.x + toNode.width / 2
  const toY = toNode.y + toNode.height / 2
  
  // 创建曲线路径
  const midX = (fromX + toX) / 2
  const midY = (fromY + toY) / 2
  
  return `M ${fromX} ${fromY} Q ${midX} ${fromY}, ${midX} ${midY} T ${toX} ${toY}`
}

const isConnectionActive = (connection: ArchitectureConnection): boolean => {
  const fromNode = allNodes.value.find(n => n.id === connection.from)
  const toNode = allNodes.value.find(n => n.id === connection.to)
  
  return fromNode && toNode && 
    (fromNode.status === 'ACTIVE' || fromNode.status === 'RUNNING') &&
    (toNode.status === 'ACTIVE' || toNode.status === 'RUNNING')
}

// 检查连接是否在激活的工作流程中
const isConnectionInActiveWorkflow = (connection: ArchitectureConnection): boolean => {
  if (activeFunctions.value.length === 0) return false
  
  const fromNode = allNodes.value.find(n => n.id === connection.from)
  const toNode = allNodes.value.find(n => n.id === connection.to)
  if (!fromNode || !toNode) return false
  
  // 检查连接的两个节点是否都在激活的工作流程中
  for (const functionId of activeFunctions.value) {
    const functionNodes = functionNodeMap[functionId] || []
    if (functionNodes.includes(fromNode.id) && functionNodes.includes(toNode.id)) {
      return true
    }
  }
  
  return false
}

// 获取连接的工作流程类型
const getConnectionWorkflowType = (connection: ArchitectureConnection): string => {
  if (activeFunctions.value.length === 0) return ''
  
  const fromNode = allNodes.value.find(n => n.id === connection.from)
  const toNode = allNodes.value.find(n => n.id === connection.to)
  if (!fromNode || !toNode) return ''
  
  // 检查连接属于哪个工作流程
  for (const functionId of activeFunctions.value) {
    const functionNodes = functionNodeMap[functionId] || []
    if (functionNodes.includes(fromNode.id) && functionNodes.includes(toNode.id)) {
      return functionId
    }
  }
  
  return ''
}

const drawCircuitBoardBackground = (ctx: CanvasRenderingContext2D) => {
  // 清空画布
  ctx.fillStyle = '#0a0a0f'
  ctx.fillRect(0, 0, canvasWidth.value, canvasHeight.value)
  
  // 绘制多层网格背景
  drawMultiLayerGrid(ctx)
  
  // 绘制电路板装饰
  drawCircuitBoardDecorations(ctx)
  
  // 绘制层级分隔线
  drawLayerSeparators(ctx)
  
  // 绘制电路板焊点
  drawSolderPoints(ctx)
}

// 绘制多层网格背景
const drawMultiLayerGrid = (ctx: CanvasRenderingContext2D) => {
  // 主网格
  ctx.strokeStyle = '#1a1a2e'
  ctx.lineWidth = 0.5
  
  const mainGridSize = 40
  for (let x = 0; x < canvasWidth.value; x += mainGridSize) {
    ctx.beginPath()
    ctx.moveTo(x, 0)
    ctx.lineTo(x, canvasHeight.value)
    ctx.stroke()
  }
  
  for (let y = 0; y < canvasHeight.value; y += mainGridSize) {
    ctx.beginPath()
    ctx.moveTo(0, y)
    ctx.lineTo(canvasWidth.value, y)
    ctx.stroke()
  }
  
  // 细网格
  ctx.strokeStyle = '#0f1419'
  ctx.lineWidth = 0.3
  
  const fineGridSize = 10
  for (let x = 0; x < canvasWidth.value; x += fineGridSize) {
    ctx.beginPath()
    ctx.moveTo(x, 0)
    ctx.lineTo(x, canvasHeight.value)
    ctx.stroke()
  }
  
  for (let y = 0; y < canvasHeight.value; y += fineGridSize) {
    ctx.beginPath()
    ctx.moveTo(0, y)
    ctx.lineTo(canvasWidth.value, y)
    ctx.stroke()
  }
}

// 绘制电路板装饰
const drawCircuitBoardDecorations = (ctx: CanvasRenderingContext2D) => {
  // 绘制电路板走线（简化版，更像架构图连线）
  ctx.strokeStyle = '#16213e'
  ctx.lineWidth = 1
  
  for (let i = 0; i < 80; i++) {
    const startX = Math.random() * canvasWidth.value
    const startY = Math.random() * canvasHeight.value
    const endX = startX + (Math.random() - 0.5) * 300
    const endY = startY + (Math.random() - 0.5) * 300
    
    ctx.beginPath()
    ctx.moveTo(startX, startY)
    ctx.lineTo(endX, endY)
    ctx.stroke()
  }
  
  // 绘制架构连接点（替代电子元件）
  drawArchitectureConnectionPoints(ctx)
}

// 绘制架构连接点（替代电子元件）
const drawArchitectureConnectionPoints = (ctx: CanvasRenderingContext2D) => {
  // 绘制主要连接点
  for (let i = 0; i < 30; i++) {
    const x = Math.random() * canvasWidth.value
    const y = Math.random() * canvasHeight.value
    
    // 外圈
    ctx.fillStyle = '#1e2936'
    ctx.beginPath()
    ctx.arc(x, y, 6, 0, Math.PI * 2)
    ctx.fill()
    
    // 内圈
    ctx.fillStyle = '#0f3460'
    ctx.beginPath()
    ctx.arc(x, y, 3, 0, Math.PI * 2)
    ctx.fill()
    
    // 中心点
    ctx.fillStyle = '#00ff88'
    ctx.beginPath()
    ctx.arc(x, y, 1, 0, Math.PI * 2)
    ctx.fill()
  }
  
  // 绘制次要连接点
  for (let i = 0; i < 50; i++) {
    const x = Math.random() * canvasWidth.value
    const y = Math.random() * canvasHeight.value
    
    ctx.fillStyle = '#16213e'
    ctx.beginPath()
    ctx.arc(x, y, 3, 0, Math.PI * 2)
    ctx.fill()
    
    ctx.fillStyle = '#0f3460'
    ctx.beginPath()
    ctx.arc(x, y, 1, 0, Math.PI * 2)
    ctx.fill()
  }
}

// 绘制层级分隔线
const drawLayerSeparators = (ctx: CanvasRenderingContext2D) => {
  const layers = ['data_hub', 'qlib_core', 'business_logic', 'ai_strategy', 'live_trading', 'experiment_mgmt', 'frontend']
  const layerPositions = [100, 250, 400, 550, 700, 850, 1000]
  
  ctx.strokeStyle = '#0f3460'
  ctx.lineWidth = 2
  ctx.setLineDash([10, 5])
  
  layerPositions.forEach((y, index) => {
    if (index > 0) {
      ctx.beginPath()
      ctx.moveTo(0, y)
      ctx.lineTo(canvasWidth.value, y)
      ctx.stroke()
      
      // 层级标签
      ctx.fillStyle = '#00ff88'
      ctx.font = '12px monospace'
      ctx.fillText(layers[index], 10, y - 5)
    }
  })
  
  ctx.setLineDash([])
}

// 绘制电路板焊点
const drawSolderPoints = (ctx: CanvasRenderingContext2D) => {
  for (let i = 0; i < 100; i++) {
    const x = Math.random() * canvasWidth.value
    const y = Math.random() * canvasHeight.value
    
    ctx.fillStyle = '#8b7355'
    ctx.beginPath()
    ctx.arc(x, y, 2, 0, Math.PI * 2)
    ctx.fill()
    
    // 焊点光泽
    ctx.fillStyle = '#a0826d'
    ctx.beginPath()
    ctx.arc(x - 0.5, y - 0.5, 1, 0, Math.PI * 2)
    ctx.fill()
  }
}

const toggleFunction = (functionId: string) => {
  const index = activeFunctions.value.indexOf(functionId)
  if (index > -1) {
    activeFunctions.value.splice(index, 1)
  } else {
    activeFunctions.value.push(functionId)
  }
}

const activateAllSelected = async () => {
  console.log('开始激活选中的功能:', activeFunctions.value)
  
  // 获取每个功能对应的节点（更新为包含所有新增节点）
  const functionNodeMap: Record<string, string[]> = {
    'ai-strategy-generation': [
      // 阶段1：数据准备
      'DH1', 'DH2', 'DH3', 'DH4', 'DH5', 'DH6', 'DH7', 'DH8',
      'DP1', 'DP2', 'DP3', 'DP4', 'SK1',
      // 阶段2：QLib核心处理
      'QL1', 'QL2', 'QL8', 'QL9',
      // 阶段3：业务逻辑处理
      'BL1', 'BL2', 'AN1', 'AN2', 'AN4', 'UB1',
      // 阶段4：AI智能策略
      'AI1', 'AI2', 'AI3', 'AI4', 'AI5', 'AI6', 'AI7', 'AI8', 'AI9',
      'AI10', 'AI11', 'AI12', 'ML1', 'ML2', 'ML3', 'OL1', 'MI1', 'AA1'
    ],
    'traditional-strategy-execution': [
      // 阶段1：数据获取
      'DH1', 'DH2', 'DH4', 'DH5', 'DH7',
      // 阶段2：QLib核心处理
      'QL1', 'QL2', 'QL3', 'QL4', 'QL5', 'QL6', 'QL7', 'QL8', 'QL9', 'QL10',
      'AB1', 'BA1',
      // 阶段3：业务逻辑处理
      'BL1', 'BL2', 'BL3', 'BL4', 'BL5', 'BL6', 'BL7', 'BL8',
      'AN1', 'AN2', 'AN3', 'AN4', 'UB1'
    ],
    'model-training': [
      // 阶段1：数据准备
      'DH1', 'DH2', 'DH3', 'DH4', 'DH6', 'DH7',
      'DP1', 'DP2', 'DP3', 'DP4',
      // 阶段2：QLib核心处理
      'QL1', 'QL2', 'QL8', 'QL9',
      // 阶段3：业务逻辑处理
      'BL1', 'BL2', 'AN1', 'AN4',
      // 阶段4：AI模型训练
      'AI1', 'AI3', 'AI4', 'AI6', 'AI10', 'AI11', 'AI12',
      'ML1', 'ML2', 'ML3', 'MI1'
    ],
    'qlib-online-service': [
      // 阶段1：数据准备
      'DH1', 'DH2', 'DH6',
      // 阶段2：QLib核心处理
      'QL1', 'QL2', 'QL6', 'QL8', 'QL9',
      // 阶段3：业务逻辑处理
      'BL1', 'BL2',
      // 阶段4：实验管理
      'EM1', 'EM2', 'EM3', 'EM4', 'EM5', 'EM6', 'EM7', 'EM8',
      'AU1', 'QO1',
      // 阶段5：AI支持
      'AI2', 'AI8'
    ],
    'qlib-integration-workflow': [
      // 阶段1：数据中枢层
      'DH1', 'DH2', 'DH3', 'DH4', 'DH5', 'DH6', 'DH7', 'DH8',
      // 阶段2：QLib核心接口层
      'QL1', 'QL2', 'QL3', 'QL4', 'QL5', 'QL6', 'QL7', 'QL8', 'QL9', 'QL10',
      'AB1', 'BA1',
      // 阶段3：实验管理层
      'EM1', 'EM2', 'EM3', 'EM4', 'EM5', 'EM6', 'EM7', 'EM8',
      'AU1', 'QO1',
      // 阶段4：前端展示层
      'UI1', 'UI2', 'UI3', 'UI4', 'UI5', 'UI6', 'UI7', 'UI8',
      'SYS1', 'SYS2', 'SYS3', 'ME1', 'PF1', 'UT1'
    ]
  }
  
  // 收集所有需要激活的节点
  const nodesToActivate = new Set<string>()
  for (const functionId of activeFunctions.value) {
    const functionNodes = functionNodeMap[functionId] || []
    functionNodes.forEach(nodeId => nodesToActivate.add(nodeId))
  }
  
  // 按依赖顺序激活节点
  const sortedNodes = Array.from(nodesToActivate).sort((a, b) => {
    const nodeA = allNodes.value.find(n => n.id === a)
    const nodeB = allNodes.value.find(n => n.id === b)
    return (nodeA?.activationComplexity || 0) - (nodeB?.activationComplexity || 0)
  })
  
  console.log('按依赖顺序激活节点:', sortedNodes)
  
  // 批量激活节点
  const activationResult = await nodeStateManager.activateNodes(sortedNodes)
  
  console.log('激活结果:', activationResult)
  
  // 更新节点状态
  allNodes.value = nodeStateManager.getAllNodes()
  
  // 更新端口状态
  updatePortStates()
  
  // 清除缓存
  nodeCache.value.clear()
  connectionCache.value.clear()
}

const deactivateAll = async () => {
  console.log('开始停用所有激活的节点')
  
  // 停用所有激活的节点（按激活复杂度倒序）
  const activeNodesList = allNodes.value.filter(n =>
    n.status === 'ACTIVE' || n.status === 'RUNNING'
  ).sort((a, b) => (b.activationComplexity || 0) - (a.activationComplexity || 0))
  
  console.log('停用节点列表:', activeNodesList.map(n => n.id))
  
  for (const node of activeNodesList) {
    try {
      await nodeStateManager.deactivateNode(node.id)
      console.log(`成功停用节点: ${node.id}`)
    } catch (error) {
      console.error(`停用节点 ${node.id} 失败:`, error)
    }
    
    // 添加延迟以避免同时停用太多节点
    await new Promise(resolve => setTimeout(resolve, 200))
  }
  
  // 清空激活功能
  activeFunctions.value = []
  
  // 更新节点状态
  allNodes.value = nodeStateManager.getAllNodes()
  
  // 更新端口状态
  updatePortStates()
  
  // 清除缓存
  nodeCache.value.clear()
  connectionCache.value.clear()
}

const autoOptimize = async () => {
  console.log('开始自动优化系统激活')
  
  // 自动优化节点激活
  const optimization = await architectureBasedActivator.optimizeSystemActivation({
    userId: 'system',
    sessionId: 'circuit-board',
    systemState: {
      cpuUsage: systemLoad.value,
      memoryUsage: systemLoad.value,
      apiStatus: [],
      activeWorkflows: activeFunctions.value,
      systemLoad: systemLoad.value
    },
    currentTime: new Date(),
    userLevel: 'expert',
    activeNodes: [],
    parameters: {}
  })
  
  console.log('优化建议:', optimization)
  
  // 应用优化建议
  if (optimization.recommendedNodes && optimization.recommendedNodes.length > 0) {
    console.log('激活推荐节点:', optimization.recommendedNodes)
    
    // 按依赖顺序激活推荐节点
    const sortedNodes = optimization.recommendedNodes.sort((a, b) => {
      const nodeA = allNodes.value.find(n => n.id === a)
      const nodeB = allNodes.value.find(n => n.id === b)
      return (nodeA?.activationComplexity || 0) - (nodeB?.activationComplexity || 0)
    })
    
    for (const nodeId of sortedNodes) {
      try {
        const success = await nodeStateManager.activateNode(nodeId)
        if (success) {
          console.log(`成功激活推荐节点: ${nodeId}`)
        } else {
          console.warn(`无法激活推荐节点: ${nodeId}`)
        }
      } catch (error) {
        console.error(`激活推荐节点 ${nodeId} 失败:`, error)
      }
      
      // 添加延迟以避免同时激活太多节点
      await new Promise(resolve => setTimeout(resolve, 300))
    }
  }
  
  // 更新节点状态
  allNodes.value = nodeStateManager.getAllNodes()
  
  // 更新端口状态
  updatePortStates()
  
  // 清除缓存
  nodeCache.value.clear()
  connectionCache.value.clear()
}

// 更新端口状态
const updatePortStates = () => {
  allNodes.value.forEach(node => {
    if (node.ports) {
      node.ports.forEach(port => {
        // 根据节点状态更新端口状态
        port.active = (node.status === 'ACTIVE' || node.status === 'RUNNING')
      })
    }
  })
}

// 获取连接线颜色
const getConnectionColor = (connection: any): string => {
  if (!connection.active && !connection.highlighted) return '#333366'
  
  // 如果连接在激活的工作流程中，使用工作流程特定的颜色
  if (connection.highlighted && connection.workflowType) {
    switch (connection.workflowType) {
      case 'ai-strategy-generation':
        return '#ff00ff' // 紫色 - AI策略生成
      case 'traditional-strategy-execution':
        return '#00aaff' // 蓝色 - 传统策略执行
      case 'model-training':
        return '#ffaa00' // 橙色 - 模型训练
      case 'qlib-online-service':
        return '#00ff88' // 绿色 - QLib在线服务
      case 'qlib-integration-workflow':
        return '#ff6600' // 红色 - QLib集成与工作流管理
      default:
        return '#00ff88'
    }
  }
  
  // 默认颜色逻辑
  if (!connection.active) return '#333366'
  
  switch (connection.type) {
    case 'data':
      return '#00aaff'
    case 'control':
      return '#ff6600'
    case 'dependency':
      return '#ff00ff'
    default:
      return '#00ff88'
  }
}

// 获取连接线宽度
const getConnectionWidth = (connection: any): number => {
  if (connection.highlighted && connection.workflowType) {
    return 6 // 工作流程高亮连接更粗
  }
  
  if (connection.active) {
    return 4
  }
  
  return 2
}

// 获取连接线滤镜
const getConnectionFilter = (connection: any): string => {
  if (connection.highlighted && connection.workflowType) {
    return 'url(#strongGlow)' // 工作流程高亮连接使用强发光
  }
  
  if (connection.active) {
    return 'url(#glow)'
  }
  
  return ''
}

// 启动动画循环
const startAnimationLoop = () => {
  let animationFrameId: number
  
  const animate = () => {
    // 更新电流动画
    updateCurrentFlowAnimation()
    
    // 更新节点状态动画
    updateNodeStatusAnimation()
    
    // 性能优化：使用requestAnimationFrame
    animationFrameId = requestAnimationFrame(animate)
  }
  
  animate()
  
  // 返回清理函数
  return () => {
    if (animationFrameId) {
      cancelAnimationFrame(animationFrameId)
    }
  }
}

// 更新电流动画
const updateCurrentFlowAnimation = () => {
  // 这里可以添加更复杂的电流动画逻辑
  // 例如：根据数据流量调整动画速度
}

// 更新节点状态动画
const updateNodeStatusAnimation = () => {
  // 这里可以添加节点状态的动态效果
  // 例如：根据负载调整节点亮度
}

const zoomIn = () => {
  zoom.value = Math.min(zoom.value * 1.2, 3)
}

const zoomOut = () => {
  zoom.value = Math.max(zoom.value / 1.2, 0.3)
}

const resetView = () => {
  zoom.value = 1
  panX.value = 0
  panY.value = 0
}

const setViewMode = (mode: string) => {
  currentViewMode.value = mode
}

const handleCanvasClick = (event: MouseEvent) => {
  // 处理画布点击事件
  const rect = canvas.value?.getBoundingClientRect()
  if (rect) {
    const x = event.clientX - rect.left
    const y = event.clientY - rect.top
    
    // 检查是否点击了节点
    const clickedNode = allNodes.value.find(node => 
      x >= node.x && x <= node.x + node.width &&
      y >= node.y && y <= node.y + node.height
    )
    
    if (clickedNode) {
      selectNode(clickedNode)
    }
  }
}

const handleCanvasMouseMove = (event: MouseEvent) => {
  // 性能优化：使用节流处理鼠标移动事件
  if (!mouseMoveThrottled) {
    mouseMoveThrottled = true
    setTimeout(() => {
      mouseMoveThrottled = false
      
      // 处理鼠标移动事件
      const rect = canvas.value?.getBoundingClientRect()
      if (rect) {
        const x = event.clientX - rect.left
        const y = event.clientY - rect.top
        
        // 检查是否悬停在节点上
        const hoveredNodeFound = allNodes.value.find(node => 
          x >= node.x && x <= node.x + node.width &&
          y >= node.y && y <= node.y + node.height
        )
        
        if (hoveredNodeFound) {
          hoverNode(hoveredNodeFound)
        } else {
          unhoverNode()
        }
      }
    }, 16) // 约60fps
  }
}

const handleCanvasWheel = (event: WheelEvent) => {
  event.preventDefault()
  
  if (event.deltaY < 0) {
    zoomIn()
  } else {
    zoomOut()
  }
}

const selectNode = (node: NodeStateInfo) => {
  selectedNode.value = node
  
  // 切换节点激活状态
  if (node.status === 'ACTIVE' || node.status === 'RUNNING') {
    nodeStateManager.deactivateNode(node.id)
  } else {
    nodeStateManager.activateNode(node.id)
  }
  
  // 更新节点状态
  allNodes.value = nodeStateManager.getAllNodes()
  
  // 清除缓存
  nodeCache.value.clear()
  connectionCache.value.clear()
}

const hoverNode = (node: NodeStateInfo) => {
  hoveredNode.value = node
}

const unhoverNode = () => {
  hoveredNode.value = null
}

const exportConfiguration = () => {
  const config = {
    activeFunctions: activeFunctions.value,
    nodeStates: allNodes.value.map(n => ({
      id: n.id,
      status: n.status
    })),
    viewMode: currentViewMode.value,
    zoom: zoom.value,
    pan: { x: panX.value, y: panY.value }
  }
  
  const blob = new Blob([JSON.stringify(config, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = 'circuit-board-config.json'
  a.click()
  URL.revokeObjectURL(url)
}

const importConfiguration = () => {
  const input = document.createElement('input')
  input.type = 'file'
  input.accept = '.json'
  
  input.onchange = (event) => {
    const file = (event.target as HTMLInputElement).files?.[0]
    if (file) {
      const reader = new FileReader()
      reader.onload = (e) => {
        try {
          const config = JSON.parse(e.target?.result as string)
          
          // 应用配置
          activeFunctions.value = config.activeFunctions || []
          currentViewMode.value = config.viewMode || 'circuit'
          zoom.value = config.zoom || 1
          panX.value = config.pan?.x || 0
          panY.value = config.pan?.y || 0
          
          // 恢复节点状态
          if (config.nodeStates) {
            config.nodeStates.forEach((nodeState: any) => {
              const node = allNodes.value.find(n => n.id === nodeState.id)
              if (node) {
                node.status = nodeState.status
              }
            })
          }
        } catch (error) {
          console.error('导入配置失败:', error)
        }
      }
      reader.readAsText(file)
    }
  }
  
  input.click()
}

const resetSystem = () => {
  activeFunctions.value = []
  currentViewMode.value = 'circuit'
  zoom.value = 1
  panX.value = 0
  panY.value = 0
  
  // 重置所有节点状态
  allNodes.value.forEach(node => {
    node.status = 'INACTIVE' as ExtendedNodeStatus
  })
  
  // 清除缓存
  nodeCache.value.clear()
  connectionCache.value.clear()
}

// 性能优化：鼠标移动节流
let mouseMoveThrottled = false

// 生命周期
onMounted(() => {
  initializeCircuitBoard()
  
  // 监听节点状态变化
  nodeStateManager.on('nodeStateChanged', () => {
    allNodes.value = nodeStateManager.getAllNodes()
    updatePortStates()
    
    // 清除缓存
    nodeCache.value.clear()
    connectionCache.value.clear()
  })
  
  // 启动动画循环
  const stopAnimation = startAnimationLoop()
  
  // 定期更新节点状态
  const updateInterval = setInterval(() => {
    updateNodeStates()
  }, 5000)
  
  // 性能优化：降低更新频率
  const performanceOptimizationInterval = setInterval(() => {
    // 清理过期缓存
    if (nodeCache.value.size > 50) {
      const keysToDelete = Array.from(nodeCache.value.keys()).slice(0, 25)
      keysToDelete.forEach(key => nodeCache.value.delete(key))
    }
    
    if (connectionCache.value.size > 10) {
      const keysToDelete = Array.from(connectionCache.value.keys()).slice(0, 5)
      keysToDelete.forEach(key => connectionCache.value.delete(key))
    }
  }, 10000)
  
  // 清理函数
  onUnmounted(() => {
    stopAnimation()
    clearInterval(updateInterval)
    clearInterval(performanceOptimizationInterval)
    
    // 清理缓存
    nodeCache.value.clear()
    connectionCache.value.clear()
  })
})
</script>

<style scoped>
.circuit-board-container {
  width: 100%;
  height: 100vh;
  background: #0a0a0f;
  color: #e0e0e0;
  font-family: 'Courier New', monospace;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.control-panel {
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  border-bottom: 2px solid #0f3460;
  padding: 15px;
  display: flex;
  gap: 30px;
  box-shadow: 0 4px 20px rgba(0, 255, 136, 0.1);
}

.function-selector h3,
.activation-controls h3,
.view-controls h3 {
  color: #00ff88;
  margin-bottom: 10px;
  font-size: 14px;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.function-buttons {
  display: flex;
  gap: 10px;
}

.function-btn {
  background: linear-gradient(135deg, #2d3561 0%, #1f2937 100%);
  border: 1px solid #0f3460;
  color: #e0e0e0;
  padding: 10px 15px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
}

.function-btn:hover {
  background: linear-gradient(135deg, #3d4571 0%, #2f3947 100%);
  border-color: #00ff88;
  box-shadow: 0 0 10px rgba(0, 255, 136, 0.3);
}

.function-btn.active {
  background: linear-gradient(135deg, #00ff88 0%, #00cc6a 100%);
  color: #0a0a0f;
  border-color: #00ff88;
  box-shadow: 0 0 20px rgba(0, 255, 136, 0.5);
}

.activation-controls {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.activate-all-btn,
.deactivate-all-btn,
.auto-optimize-btn {
  background: linear-gradient(135deg, #0f3460 0%, #16213e 100%);
  border: 1px solid #0f3460;
  color: #e0e0e0;
  padding: 8px 12px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 12px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.activate-all-btn:hover {
  background: linear-gradient(135deg, #00ff88 0%, #00cc6a 100%);
  color: #0a0a0f;
  border-color: #00ff88;
}

.deactivate-all-btn:hover {
  background: linear-gradient(135deg, #ff4444 0%, #cc0000 100%);
  color: #ffffff;
  border-color: #ff4444;
}

.auto-optimize-btn:hover {
  background: linear-gradient(135deg, #ffaa00 0%, #ff8800 100%);
  color: #0a0a0f;
  border-color: #ffaa00;
}

.view-controls {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.zoom-controls {
  display: flex;
  gap: 5px;
}

.zoom-controls button {
  background: #2d3561;
  border: 1px solid #0f3460;
  color: #e0e0e0;
  width: 30px;
  height: 30px;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.zoom-controls button:hover {
  background: #3d4571;
  border-color: #00ff88;
}

.view-modes {
  display: flex;
  gap: 5px;
}

.view-mode-btn {
  background: #2d3561;
  border: 1px solid #0f3460;
  color: #e0e0e0;
  padding: 6px 10px;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 11px;
}

.view-mode-btn.active {
  background: #00ff88;
  color: #0a0a0f;
  border-color: #00ff88;
}

.circuit-board {
  flex: 1;
  position: relative;
  overflow: hidden;
  background: #0a0a0f;
}

.circuit-board canvas {
  position: absolute;
  top: 0;
  left: 0;
}

.connections-layer {
  position: absolute;
  top: 0;
  left: 0;
  pointer-events: none;
}

.connection-line {
  transition: all 0.3s ease;
}

.connection-line.active {
  filter: drop-shadow(0 0 3px #00ff88);
}

.connection-line.highlighted {
  filter: drop-shadow(0 0 5px #ff00ff);
  animation: workflowHighlightPulse 2s infinite;
}

.connection-line.workflow-highlighted {
  stroke-dasharray: 10, 5;
  animation: workflowFlowAnimation 3s linear infinite;
}

.nodes-layer {
  position: absolute;
  top: 0;
  left: 0;
  transition: transform 0.3s ease;
  /* 性能优化：使用will-change优化渲染性能 */
  will-change: transform;
}

.circuit-node {
  position: absolute;
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  border: 2px solid #0f3460;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 12px;
  min-width: 160px;
  min-height: 100px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
  overflow: hidden;
  position: relative;
  /* 性能优化：使用will-change优化渲染性能 */
  will-change: transform, opacity;
}

.circuit-node:hover {
  border-color: #00ff88;
  box-shadow: 0 0 30px rgba(0, 255, 136, 0.4);
  transform: scale(1.05) translateY(-2px);
}

.circuit-node.active {
  background: linear-gradient(135deg, #00ff88 0%, #00cc6a 100%);
  border-color: #00ff88;
  color: #0a0a0f;
  box-shadow: 0 0 35px rgba(0, 255, 136, 0.6);
  animation: nodeActivePulse 2s infinite;
}

.circuit-node.recommended {
  border-color: #ffaa00;
  box-shadow: 0 0 25px rgba(255, 170, 0, 0.4);
  animation: nodeRecommendedGlow 1.5s infinite;
}

.circuit-node.error {
  border-color: #ff4444;
  box-shadow: 0 0 25px rgba(255, 68, 68, 0.4);
  animation: nodeErrorPulse 1s infinite;
}

.circuit-node.high_priority {
  border-color: #ff00ff;
  box-shadow: 0 0 30px rgba(255, 0, 255, 0.4);
}

/* 节点背景装饰 */
.node-background-decoration {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  overflow: hidden;
}

.circuit-pattern {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-image:
    radial-gradient(circle at 20% 20%, rgba(0, 255, 136, 0.1) 0%, transparent 50%),
    radial-gradient(circle at 80% 80%, rgba(0, 255, 136, 0.1) 0%, transparent 50%),
    linear-gradient(45deg, transparent 48%, rgba(0, 255, 136, 0.1) 49%, rgba(0, 255, 136, 0.1) 51%, transparent 52%);
  background-size: 100% 100%, 100% 100%, 10px 10px;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.circuit-node.active .circuit-pattern {
  opacity: 1;
}

.node-glow {
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle, rgba(0, 255, 136, 0.3) 0%, transparent 70%);
  animation: nodeGlowRotate 3s linear infinite;
}

.node-core {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  z-index: 2;
  position: relative;
}

.node-icon {
  font-size: 24px;
  color: #00ff88;
  text-shadow: 0 0 10px rgba(0, 255, 136, 0.5);
  transition: all 0.3s ease;
}

.circuit-node.active .node-icon {
  color: #0a0a0f;
  text-shadow: 0 0 15px rgba(10, 10, 15, 0.8);
}

.node-label {
  font-size: 11px;
  text-align: center;
  font-weight: bold;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: #e0e0e0;
  transition: color 0.3s ease;
}

.circuit-node.active .node-label {
  color: #0a0a0f;
}

.node-complexity {
  display: flex;
  gap: 2px;
  margin-top: 4px;
}

.complexity-dot {
  width: 4px;
  height: 4px;
  border-radius: 50%;
  background: #00ff88;
  opacity: 0.6;
  box-shadow: 0 0 3px rgba(0, 255, 136, 0.5);
}

.circuit-node.active .complexity-dot {
  background: #0a0a0f;
  box-shadow: 0 0 3px rgba(10, 10, 15, 0.5);
}

.node-ports {
  position: absolute;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

.port {
  position: absolute;
  width: 8px;
  height: 8px;
  background: #0f3460;
  border-radius: 50%;
  border: 1px solid #1a1a2e;
  transition: all 0.3s ease;
  z-index: 3;
}

.port.input {
  left: -4px;
  top: 50%;
  transform: translateY(-50%);
}

.port.output {
  right: -4px;
  top: 50%;
  transform: translateY(-50%);
}

.port.active {
  background: #00ff88;
  box-shadow: 0 0 10px #00ff88;
  border-color: #00ff88;
}

.port-glow {
  position: absolute;
  top: -6px;
  left: -6px;
  width: 20px;
  height: 20px;
  background: radial-gradient(circle, rgba(0, 255, 136, 0.6) 0%, transparent 70%);
  border-radius: 50%;
  animation: portGlowPulse 1.5s infinite;
}

.node-status-indicator {
  position: absolute;
  top: -8px;
  right: -8px;
  z-index: 4;
}

.status-light {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: #333;
  border: 2px solid #1a1a2e;
  position: relative;
  transition: all 0.3s ease;
}

.status-light.active {
  background: #00ff88;
  box-shadow: 0 0 15px #00ff88;
  border-color: #00ff88;
}

.status-light.running {
  background: #ffaa00;
  box-shadow: 0 0 15px #ffaa00;
  border-color: #ffaa00;
  animation: statusRunningPulse 1s infinite;
}

.status-light.error {
  background: #ff4444;
  box-shadow: 0 0 15px #ff4444;
  border-color: #ff4444;
  animation: statusErrorPulse 0.8s infinite;
}

.status-light.recommended {
  background: #ffaa00;
  box-shadow: 0 0 15px #ffaa00;
  border-color: #ffaa00;
  animation: statusRecommendedPulse 1.2s infinite;
}

.status-pulse {
  position: absolute;
  top: -4px;
  left: -4px;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: inherit;
  opacity: 0.3;
  animation: statusPulseExpand 1.5s infinite;
}

/* 节点活动指示器 */
.node-activity-indicator {
  position: absolute;
  bottom: -5px;
  left: 50%;
  transform: translateX(-50%);
  width: 80%;
  height: 3px;
  background: linear-gradient(90deg, transparent 0%, #00ff88 50%, transparent 100%);
  border-radius: 2px;
  overflow: hidden;
}

.activity-wave {
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent 0%, rgba(0, 255, 136, 0.8) 50%, transparent 100%);
  animation: activityWaveMove 2s linear infinite;
}

/* 动画定义 */
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

@keyframes nodeActivePulse {
  0%, 100% {
    box-shadow: 0 0 35px rgba(0, 255, 136, 0.6);
  }
  50% {
    box-shadow: 0 0 50px rgba(0, 255, 136, 0.8);
  }
}

@keyframes nodeRecommendedGlow {
  0%, 100% {
    box-shadow: 0 0 25px rgba(255, 170, 0, 0.4);
  }
  50% {
    box-shadow: 0 0 40px rgba(255, 170, 0, 0.6);
  }
}

@keyframes nodeErrorPulse {
  0%, 100% {
    box-shadow: 0 0 25px rgba(255, 68, 68, 0.4);
  }
  50% {
    box-shadow: 0 0 40px rgba(255, 68, 68, 0.6);
  }
}

@keyframes nodeGlowRotate {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

@keyframes portGlowPulse {
  0%, 100% { opacity: 0.6; }
  50% { opacity: 1; }
}

@keyframes statusRunningPulse {
  0%, 100% {
    box-shadow: 0 0 15px #ffaa00;
  }
  50% {
    box-shadow: 0 0 25px #ffaa00;
  }
}

@keyframes statusErrorPulse {
  0%, 100% {
    box-shadow: 0 0 15px #ff4444;
  }
  50% {
    box-shadow: 0 0 25px #ff4444;
  }
}

@keyframes statusRecommendedPulse {
  0%, 100% {
    box-shadow: 0 0 15px #ffaa00;
  }
  50% {
    box-shadow: 0 0 25px #ffaa00;
  }
}

@keyframes statusPulseExpand {
  0% {
    transform: scale(1);
    opacity: 0.3;
  }
  100% {
    transform: scale(2);
    opacity: 0;
  }
}

@keyframes activityWaveMove {
  0% { left: -100%; }
  100% { left: 100%; }
}

@keyframes workflowHighlightPulse {
  0%, 100% {
    opacity: 1;
    filter: drop-shadow(0 0 5px currentColor);
  }
  50% {
    opacity: 0.7;
    filter: drop-shadow(0 0 10px currentColor);
  }
}

@keyframes workflowFlowAnimation {
  0% {
    stroke-dashoffset: 0;
  }
  100% {
    stroke-dashoffset: -30;
  }
}

.node-info-panel {
  position: absolute;
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  border: 1px solid #0f3460;
  border-radius: 8px;
  padding: 15px;
  min-width: 200px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
  z-index: 1000;
}

.node-info-panel h4 {
  color: #00ff88;
  margin-bottom: 10px;
  font-size: 14px;
}

.node-info-panel p {
  font-size: 12px;
  margin-bottom: 10px;
  color: #e0e0e0;
}

.node-stats {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.stat {
  display: flex;
  justify-content: space-between;
  font-size: 11px;
}

.stat .label {
  color: #888;
}

.stat .value {
  color: #e0e0e0;
  font-weight: bold;
}

.stat .value.active {
  color: #00ff88;
}

.stat .value.running {
  color: #ffaa00;
}

.stat .value.error {
  color: #ff4444;
}

.status-bar {
  background: linear-gradient(135deg, #16213e 0%, #0f3460 100%);
  border-top: 2px solid #0f3460;
  padding: 10px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.status-info {
  display: flex;
  gap: 20px;
}

.status-item {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 12px;
  color: #e0e0e0;
}

.status-item i {
  color: #00ff88;
}

.status-actions {
  display: flex;
  gap: 10px;
}

.status-actions button {
  background: #2d3561;
  border: 1px solid #0f3460;
  color: #e0e0e0;
  padding: 6px 12px;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 11px;
  display: flex;
  align-items: center;
  gap: 5px;
}

.status-actions button:hover {
  background: #3d4571;
  border-color: #00ff88;
}
</style>
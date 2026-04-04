<template>
  <div class="intelligent-node-visualizer">
    <div class="visualizer-header">
      <div class="header-controls">
        <div class="view-controls">
          <button 
            @click="setViewMode('grid')" 
            :class="['btn', 'btn-sm', { active: viewMode === 'grid' }]"
            title="网格视图"
          >
            <i class="icon-grid"></i>
          </button>
          <button 
            @click="setViewMode('hierarchical')" 
            :class="['btn', 'btn-sm', { active: viewMode === 'hierarchical' }]"
            title="层次视图"
          >
            <i class="icon-tree"></i>
          </button>
          <button 
            @click="setViewMode('circular')" 
            :class="['btn', 'btn-sm', { active: viewMode === 'circular' }]"
            title="圆形视图"
          >
            <i class="icon-circle"></i>
          </button>
        </div>
        
        <div class="filter-controls">
          <input 
            v-model="searchQuery" 
            type="text" 
            placeholder="搜索节点..." 
            class="search-input"
            @input="onSearchInput"
          />
          
          <select v-model="statusFilter" class="status-filter" @change="onStatusFilterChange">
            <option value="all">所有状态</option>
            <option value="inactive">非激活</option>
            <option value="standby">待机</option>
            <option value="recommended">推荐</option>
            <option value="active">激活</option>
            <option value="running">运行中</option>
            <option value="error">错误</option>
          </select>
          
          <select v-model="layerFilter" class="layer-filter" @change="onLayerFilterChange">
            <option value="all">所有层级</option>
            <option value="data_hub">数据中枢层</option>
            <option value="qlib_core">QLib核心层</option>
            <option value="business_logic">业务逻辑层</option>
            <option value="ai_strategy">AI策略层</option>
            <option value="live_trading">实盘交易层</option>
            <option value="experiment_mgmt">实验管理层</option>
            <option value="frontend">前端展示层</option>
          </select>
        </div>
        
        <div class="action-controls">
          <button @click="updateNodeStates" class="btn btn-primary">
            <i class="icon-refresh"></i>
            更新状态
          </button>
          <button @click="autoActivateRecommended" class="btn btn-success">
            <i class="icon-play"></i>
            自动激活推荐
          </button>
          <button @click="resetAllNodes" class="btn btn-secondary">
            <i class="icon-reset"></i>
            重置所有
          </button>
        </div>
      </div>
    </div>
    
    <div class="visualizer-content">
      <canvas 
        ref="nodeCanvas" 
        class="node-canvas"
        @click="onCanvasClick"
        @contextmenu="onCanvasRightClick"
        @wheel="onCanvasWheel"
      ></canvas>
      
      <div class="side-panel">
        <div class="panel-section">
          <h3>节点统计</h3>
          <div class="stats-grid">
            <div class="stat-item">
              <span class="stat-label">总节点数:</span>
              <span class="stat-value">{{ nodeStats.total }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">非激活:</span>
              <span class="stat-value inactive">{{ nodeStats.inactive }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">待机:</span>
              <span class="stat-value standby">{{ nodeStats.standby }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">推荐:</span>
              <span class="stat-value recommended">{{ nodeStats.recommended }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">激活:</span>
              <span class="stat-value active">{{ nodeStats.active }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">运行中:</span>
              <span class="stat-value running">{{ nodeStats.running }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">错误:</span>
              <span class="stat-value error">{{ nodeStats.error }}</span>
            </div>
          </div>
        </div>
        
        <div class="panel-section">
          <h3>推荐节点</h3>
          <div class="recommendation-list">
            <div 
              v-for="recommendation in filteredRecommendations" 
              :key="recommendation.nodeId"
              class="recommendation-item"
              @click="activateRecommendedNode(recommendation.nodeId)"
            >
              <div class="recommendation-header">
                <div class="recommendation-icon">{{ getNodeIcon(recommendation.nodeId) }}</div>
                <div class="recommendation-info">
                  <h4>{{ recommendation.name }}</h4>
                  <div class="recommendation-meta">
                    <span class="confidence">置信度: {{ (recommendation.confidence * 100).toFixed(1) }}%</span>
                    <span class="category">{{ recommendation.category }}</span>
                  </div>
                </div>
                <div class="recommendation-actions">
                  <button class="btn btn-sm btn-primary">激活</button>
                  <button class="btn btn-sm btn-secondary">详情</button>
                </div>
              </div>
              <div class="recommendation-reason">
                <strong>推荐理由:</strong> {{ recommendation.reason }}
              </div>
            </div>
          </div>
        </div>
        
        <div class="panel-section">
          <h3>图例</h3>
          <div class="legend">
            <div class="legend-item">
              <span class="legend-color inactive"></span>
              <span>非激活</span>
            </div>
            <div class="legend-item">
              <span class="legend-color standby"></span>
              <span>待机</span>
            </div>
            <div class="legend-item recommended">
              <span class="legend-color recommended"></span>
              <span>推荐</span>
            </div>
            <div class="legend-item">
              <span class="legend-color active"></span>
              <span>激活</span>
            </div>
            <div class="legend-item">
              <span class="legend-color running"></span>
              <span>运行中</span>
            </div>
            <div class="legend-item">
              <span class="legend-color error"></span>
              <span>错误</span>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 节点详情弹窗 -->
    <div v-if="selectedNode" class="node-detail-modal" @click.self="closeNodeDetail">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>{{ selectedNode.name }}</h3>
          <button class="close-btn" @click="closeNodeDetail">×</button>
        </div>
        <div class="modal-body">
          <div class="node-info">
            <div class="info-item">
              <label>状态:</label>
              <span :class="['status-badge', selectedNode.status]">{{ getStatusText(selectedNode.status) }}</span>
            </div>
            <div class="info-item">
              <label>层级:</label>
              <span>{{ getLayerText(selectedNode.metadata.layer) }}</span>
            </div>
            <div class="info-item">
              <label>复杂度:</label>
              <span>{{ selectedNode.metadata.complexity }}/5</span>
            </div>
            <div class="info-item">
              <label>预计时间:</label>
              <span>{{ formatTime(selectedNode.metadata.estimatedTime) }}</span>
            </div>
            <div v-if="selectedNode.recommendationReason" class="info-item">
              <label>推荐理由:</label>
              <span>{{ selectedNode.recommendationReason }}</span>
            </div>
          </div>
          
          <div class="performance-metrics">
            <h4>性能指标</h4>
            <div class="metric-item">
              <label>CPU使用率:</label>
              <div class="progress-bar">
                <div class="progress-fill" :style="{ width: selectedNode.performance.cpuUsage + '%' }"></div>
              </div>
              <span>{{ selectedNode.performance.cpuUsage.toFixed(1) }}%</span>
            </div>
            <div class="metric-item">
              <label>内存使用率:</label>
              <div class="progress-bar">
                <div class="progress-fill" :style="{ width: selectedNode.performance.memoryUsage + '%' }"></div>
              </div>
              <span>{{ selectedNode.performance.memoryUsage.toFixed(1) }}%</span>
            </div>
            <div class="metric-item">
              <label>响应时间:</label>
              <span>{{ selectedNode.performance.responseTime.toFixed(0) }}ms</span>
            </div>
            <div class="metric-item">
              <label>可用性:</label>
              <span>{{ (selectedNode.performance.availability * 100).toFixed(1) }}%</span>
            </div>
          </div>
          
          <div class="node-actions">
            <button 
              v-if="selectedNode.canActivate && selectedNode.status === 'inactive'"
              @click="activateNode(selectedNode.id)" 
              class="btn btn-primary"
            >
              激活节点
            </button>
            <button 
              v-if="selectedNode.status === 'active'"
              @click="deactivateNode(selectedNode.id)" 
              class="btn btn-warning"
            >
              停用节点
            </button>
            <button 
              v-if="selectedNode.status === 'error'"
              @click="retryNode(selectedNode.id)" 
              class="btn btn-secondary"
            >
              重试
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { nodeStateManager } from '@/services/node-state-manager'
import type { NodeStateInfo, ExtendedNodeStatus } from '@/types/node-system'

// 响应式数据
const viewMode = ref('grid')
const searchQuery = ref('')
const statusFilter = ref('all')
const layerFilter = ref('all')
const selectedNode = ref<NodeStateInfo | null>(null)
const nodeCanvas = ref<HTMLCanvasElement | null>(null)
const animationFrame = ref<number | null>(null)

// 计算属性
const filteredNodes = computed(() => {
  let nodes = Array.from(nodeStateManager.getAllNodeStates().values())
  
  // 应用搜索过滤
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    nodes = nodes.filter(node => 
      node.name.toLowerCase().includes(query) ||
      node.metadata.description.toLowerCase().includes(query)
    )
  }
  
  // 应用状态过滤
  if (statusFilter.value !== 'all') {
    nodes = nodes.filter(node => node.status === statusFilter.value)
  }
  
  // 应用层级过滤
  if (layerFilter.value !== 'all') {
    nodes = nodes.filter(node => node.metadata.layer === layerFilter.value)
  }
  
  return nodes
})

const filteredRecommendations = computed(() => {
  return Array.from(nodeStateManager.getAllNodeStates().values())
    .filter(node => node.isRecommended)
    .map(node => ({
      nodeId: node.id,
      name: node.name,
      confidence: node.priority / 100,
      reason: node.recommendationReason || '系统推荐',
      category: 'existing_node'
    }))
})

const nodeStats = computed(() => nodeStateManager.getNodeStats())

// 方法
const setViewMode = (mode: string) => {
  viewMode.value = mode
  renderNodes()
}

const onSearchInput = () => {
  renderNodes()
}

const onStatusFilterChange = () => {
  renderNodes()
}

const onLayerFilterChange = () => {
  renderNodes()
}

const updateNodeStates = async () => {
  const context = {
    userId: 'current-user',
    sessionId: 'current-session',
    systemState: {
      cpuUsage: 50,
      memoryUsage: 60,
      apiStatus: [],
      activeWorkflows: [],
      systemLoad: 0.7
    },
    currentTime: new Date(),
    userLevel: 'intermediate' as const,
    currentWorkflow: 'ai-strategy-generation',
    activeNodes: []
  }
  
  await nodeStateManager.updateAllNodeStates(context)
  renderNodes()
}

const autoActivateRecommended = async () => {
  const recommendedNodes = nodeStateManager.getRecommendedNodes()
  const nodeIds = recommendedNodes.map(node => node.id)
  
  await nodeStateManager.activateNodes(nodeIds)
  renderNodes()
}

const resetAllNodes = () => {
  nodeStateManager.resetAllNodes()
  renderNodes()
}

const activateRecommendedNode = async (nodeId: string) => {
  await nodeStateManager.activateNode(nodeId)
  renderNodes()
}

const activateNode = async (nodeId: string) => {
  await nodeStateManager.activateNode(nodeId)
  renderNodes()
}

const deactivateNode = async (nodeId: string) => {
  // 这里应该实现停用逻辑
  console.log('停用节点:', nodeId)
  renderNodes()
}

const retryNode = async (nodeId: string) => {
  await nodeStateManager.activateNode(nodeId)
  renderNodes()
}

const closeNodeDetail = () => {
  selectedNode.value = null
}

const getNodeIcon = (nodeId: string): string => {
  const node = nodeStateManager.getNodeState(nodeId)
  return node?.metadata.icon || '📦'
}

const getStatusText = (status: ExtendedNodeStatus): string => {
  const statusTexts = {
    [ExtendedNodeStatus.INACTIVE]: '非激活',
    [ExtendedNodeStatus.STANDBY]: '待机',
    [ExtendedNodeStatus.RECOMMENDED]: '推荐',
    [ExtendedNodeStatus.ACTIVATING]: '激活中',
    [ExtendedNodeStatus.ACTIVE]: '激活',
    [ExtendedNodeStatus.RUNNING]: '运行中',
    [ExtendedNodeStatus.COMPLETED]: '已完成',
    [ExtendedNodeStatus.ERROR]: '错误',
    [ExtendedNodeStatus.DISABLED]: '禁用',
    [ExtendedNodeStatus.MAINTENANCE]: '维护中',
    [ExtendedNodeStatus.HIGH_PRIORITY]: '高优先级',
    [ExtendedNodeStatus.CRITICAL]: '关键',
    [ExtendedNodeStatus.OPTIMIZED]: '优化'
  }
  
  return statusTexts[status] || '未知'
}

const getLayerText = (layer: string): string => {
  const layerTexts = {
    data_hub: '数据中枢层',
    qlib_core: 'QLib核心层',
    business_logic: '业务逻辑层',
    ai_strategy: 'AI策略层',
    live_trading: '实盘交易层',
    experiment_mgmt: '实验管理层',
    frontend: '前端展示层'
  }
  
  return layerTexts[layer] || '未知'
}

const formatTime = (milliseconds: number): string => {
  const seconds = Math.floor(milliseconds / 1000)
  const minutes = Math.floor(seconds / 60)
  const hours = Math.floor(minutes / 60)
  
  if (hours > 0) {
    return `${hours}小时${minutes % 60}分钟`
  } else if (minutes > 0) {
    return `${minutes}分钟`
  } else {
    return `${seconds}秒`
  }
}

// 渲染节点
const renderNodes = () => {
  if (!nodeCanvas.value) return
  
  const canvas = nodeCanvas.value
  const ctx = canvas.getContext('2d')
  if (!ctx) return
  
  // 清空画布
  ctx.clearRect(0, 0, canvas.width, canvas.height)
  
  // 设置画布大小
  canvas.width = canvas.offsetWidth
  canvas.height = canvas.offsetHeight
  
  const nodes = filteredNodes.value
  const nodeWidth = 200
  const nodeHeight = 80
  const padding = 50
  
  // 计算布局
  let layout: Array<{ x: number; y: number; width: number; height: number }> = []
  
  if (viewMode.value === 'grid') {
    // 网格布局
    const cols = Math.floor(canvas.width / (nodeWidth + padding))
    nodes.forEach((node, index) => {
      const row = Math.floor(index / cols)
      const col = index % cols
      
      layout.push({
        x: col * (nodeWidth + padding) + padding / 2,
        y: row * (nodeHeight + padding) + padding / 2,
        width: nodeWidth,
        height: nodeHeight
      })
    })
  } else if (viewMode.value === 'hierarchical') {
    // 层次布局
    const layers = {
      data_hub: nodes.filter(n => n.metadata.layer === 'data_hub'),
      qlib_core: nodes.filter(n => n.metadata.layer === 'qlib_core'),
      business_logic: nodes.filter(n => n.metadata.layer === 'business_logic'),
      ai_strategy: nodes.filter(n => n.metadata.layer === 'ai_strategy'),
      live_trading: nodes.filter(n => n.metadata.layer === 'live_trading'),
      experiment_mgmt: nodes.filter(n => n.metadata.layer === 'experiment_mgmt'),
      frontend: nodes.filter(n => n.metadata.layer === 'frontend')
    }
    
    let currentY = padding
    Object.values(layers).forEach(layerNodes => {
      if (layerNodes.length === 0) return
      
      const layerWidth = canvas.width - padding * 2
      const nodeSpacing = layerWidth / (layerNodes.length + 1)
      
      layerNodes.forEach((node, index) => {
        layout.push({
          x: padding + index * nodeSpacing + nodeSpacing / 2,
          y: currentY,
          width: nodeWidth,
          height: nodeHeight
        })
      })
      
      currentY += nodeHeight + padding
    })
  }
  
  // 更新节点位置
  layout.forEach((layout, index) => {
    const node = nodes[index]
    if (node) {
      node.bounds = layout
    }
  })
  
  // 渲染连接线
  renderConnections(ctx, nodes)
  
  // 渲染节点
  nodes.forEach(node => {
    renderNode(ctx, node)
  })
  
  // 启动动画
  if (!animationFrame.value) {
    animate()
  }
}

// 渲染连接线
const renderConnections = (ctx: CanvasRenderingContext2D, nodes: NodeStateInfo[]) => {
  ctx.strokeStyle = '#ddd'
  ctx.lineWidth = 2
  
  nodes.forEach(node => {
    node.dependencies.forEach(depId => {
      const depNode = nodes.find(n => n.id === depId)
      if (depNode) {
        const fromX = depNode.bounds.x + depNode.bounds.width
        const fromY = depNode.bounds.y + depNode.bounds.height / 2
        const toX = node.bounds.x
        const toY = node.bounds.y + node.bounds.height / 2
        
        ctx.beginPath()
        ctx.moveTo(fromX, fromY)
        ctx.lineTo(toX, toY)
        ctx.stroke()
      }
    })
  })
}

// 渲染单个节点
const renderNode = (ctx: CanvasRenderingContext2D, node: NodeStateInfo) => {
  const { x, y, width, height } = node.bounds
  
  // 绘制节点背景
  const gradient = ctx.createLinearGradient(x, y, x, y + height)
  gradient.addColorStop(0, getNodeBackgroundColor(node.status))
  gradient.addColorStop(1, getNodeBackgroundColor(node.status))
  
  ctx.fillStyle = gradient
  drawRoundedRect(ctx, x, y, width, height, 8)
  ctx.fill()
  
  // 绘制节点边框
  ctx.strokeStyle = getNodeBorderColor(node.status)
  ctx.lineWidth = getNodeBorderWidth(node.status)
  
  if (node.status === ExtendedNodeStatus.RECOMMENDED) {
    ctx.setLineDash([5, 3])
  } else if (node.priority > 90) {
    ctx.setLineDash([10, 5])
  } else {
    ctx.setLineDash([])
  }
  
  drawRoundedRect(ctx, x, y, width, height, 8)
  ctx.stroke()
  
  // 绘制节点图标
  ctx.font = '24px Arial'
  ctx.textAlign = 'center'
  ctx.textBaseline = 'middle'
  ctx.fillText(node.metadata.icon, x + 20, y + height / 2)
  
  // 绘制节点名称
  ctx.font = '14px Arial'
  ctx.fillStyle = '#333'
  ctx.textAlign = 'left'
  ctx.fillText(node.name, x + 50, y + height / 2)
  
  // 绘制状态指示器
  renderStatusIndicator(ctx, node)
  
  // 绘制推荐徽章
  if (node.isRecommended) {
    renderRecommendationBadge(ctx, node)
  }
  
  // 绘制性能指标
  if (node.status === ExtendedNodeStatus.ACTIVE || node.status === ExtendedNodeStatus.RUNNING) {
    renderPerformanceMetrics(ctx, node)
  }
}

// 渲染状态指示器
const renderStatusIndicator = (ctx: CanvasRenderingContext2D, node: NodeStateInfo) => {
  const indicatorX = node.bounds.x + node.bounds.width - 20
  const indicatorY = node.bounds.y + 10
  const indicatorRadius = 6
  
  ctx.beginPath()
  ctx.arc(indicatorX, indicatorY, indicatorRadius, 0, Math.PI * 2)
  ctx.fillStyle = getStatusIndicatorColor(node.status)
  ctx.fill()
  
  // 动画效果
  if (node.status === ExtendedNodeStatus.RUNNING || node.status === ExtendedNodeStatus.ACTIVATING) {
    ctx.strokeStyle = getStatusIndicatorColor(node.status)
    ctx.lineWidth = 2
    ctx.globalAlpha = 0.5
    ctx.stroke()
    ctx.globalAlpha = 1
  }
}

// 渲染推荐徽章
const renderRecommendationBadge = (ctx: CanvasRenderingContext2D, node: NodeStateInfo) => {
  const badgeX = node.bounds.x + node.bounds.width / 2 - 30
  const badgeY = node.bounds.y - 10
  const badgeWidth = 60
  const badgeHeight = 16
  
  ctx.fillStyle = '#28a745'
  ctx.strokeStyle = '#1e7e34'
  ctx.lineWidth = 2
  
  ctx.beginPath()
  ctx.moveTo(badgeX, badgeY)
  ctx.lineTo(badgeX + badgeWidth, badgeY)
  ctx.lineTo(badgeX + badgeWidth - 5, badgeY + badgeHeight)
  ctx.lineTo(badgeX, badgeY + badgeHeight)
  ctx.closePath()
  
  ctx.fill()
  ctx.stroke()
  
  ctx.fillStyle = 'white'
  ctx.font = '10px Arial'
  ctx.textAlign = 'center'
  ctx.textBaseline = 'middle'
  ctx.fillText('推荐', badgeX + badgeWidth / 2, badgeY + badgeHeight / 2)
}

// 渲染性能指标
const renderPerformanceMetrics = (ctx: CanvasRenderingContext2D, node: NodeStateInfo) => {
  const metricsY = node.bounds.y + node.bounds.height - 20
  const metricsWidth = node.bounds.width - 40
  const metricsHeight = 4
  
  // CPU使用率
  const cpuWidth = (node.performance.cpuUsage / 100) * metricsWidth
  ctx.fillStyle = '#e3f2fd'
  ctx.fillRect(node.bounds.x + 20, metricsY, cpuWidth, metricsHeight)
  
  // 内存使用率
  const memWidth = (node.performance.memoryUsage / 100) * metricsWidth
  ctx.fillStyle = '#ffc107'
  ctx.fillRect(node.bounds.x + 20, metricsY + 6, memWidth, metricsHeight)
}

// 绘制圆角矩形
const drawRoundedRect = (ctx: CanvasRenderingContext2D, x: number, y: number, width: number, height: number, radius: number) => {
  ctx.beginPath()
  ctx.moveTo(x + radius, y)
  ctx.lineTo(x + width - radius, y)
  ctx.quadraticCurveTo(x + width, y, x + width, y + radius)
  ctx.lineTo(x + width, y + height - radius)
  ctx.quadraticCurveTo(x + width, y + height, x, y + height - radius)
  ctx.lineTo(x, y + height - radius)
  ctx.quadraticCurveTo(x, y + height, x + radius, y + height)
  ctx.closePath()
}

// 获取节点背景颜色
const getNodeBackgroundColor = (status: ExtendedNodeStatus): string => {
  const colors = {
    [ExtendedNodeStatus.INACTIVE]: '#f8f9fa',
    [ExtendedNodeStatus.STANDBY]: '#fff3cd',
    [ExtendedNodeStatus.RECOMMENDED]: '#d4edda',
    [ExtendedNodeStatus.ACTIVATING]: '#cce5ff',
    [ExtendedNodeStatus.ACTIVE]: '#d4edda',
    [ExtendedNodeStatus.RUNNING]: '#fff3cd',
    [ExtendedNodeStatus.COMPLETED]: '#d1ecf1',
    [ExtendedNodeStatus.ERROR]: '#f8d7da',
    [ExtendedNodeStatus.DISABLED]: '#e2e3e5',
    [ExtendedNodeStatus.MAINTENANCE]: '#fff3cd',
    [ExtendedNodeStatus.HIGH_PRIORITY]: '#e2d6f3',
    [ExtendedNodeStatus.CRITICAL]: '#f8d7da',
    [ExtendedNodeStatus.OPTIMIZED]: '#fff4e6'
  }
  
  return colors[status] || '#f8f9fa'
}

// 获取节点边框颜色
const getNodeBorderColor = (status: ExtendedNodeStatus): string => {
  const colors = {
    [ExtendedNodeStatus.INACTIVE]: '#dee2e6',
    [ExtendedNodeStatus.STANDBY]: '#ffc107',
    [ExtendedNodeStatus.RECOMMENDED]: '#28a745',
    [ExtendedNodeStatus.ACTIVATING]: '#007bff',
    [ExtendedNodeStatus.ACTIVE]: '#28a745',
    [ExtendedNodeStatus.RUNNING]: '#fd7e14',
    [ExtendedNodeStatus.COMPLETED]: '#17a2b8',
    [ExtendedNodeStatus.ERROR]: '#dc3545',
    [ExtendedNodeStatus.DISABLED]: '#6c757d',
    [ExtendedNodeStatus.MAINTENANCE]: '#fd7e14',
    [ExtendedNodeStatus.HIGH_PRIORITY]: '#6f42c1',
    [ExtendedNodeStatus.CRITICAL]: '#dc3545',
    [ExtendedNodeStatus.OPTIMIZED]: '#fd7e14'
  }
  
  return colors[status] || '#dee2e6'
}

// 获取节点边框宽度
const getNodeBorderWidth = (status: ExtendedNodeStatus): number => {
  const widths = {
    [ExtendedNodeStatus.RECOMMENDED]: 3,
    [ExtendedNodeStatus.HIGH_PRIORITY]: 3,
    [ExtendedNodeStatus.CRITICAL]: 4,
    [ExtendedNodeStatus.RUNNING]: 2,
    [ExtendedNodeStatus.ACTIVATING]: 2
  }
  
  return widths[status] || 1
}

// 获取状态指示器颜色
const getStatusIndicatorColor = (status: ExtendedNodeStatus): string => {
  const colors = {
    [ExtendedNodeStatus.INACTIVE]: '#6c757d',
    [ExtendedNodeStatus.STANDBY]: '#ffc107',
    [ExtendedNodeStatus.RECOMMENDED]: '#28a745',
    [ExtendedNodeStatus.ACTIVATING]: '#007bff',
    [ExtendedNodeStatus.ACTIVE]: '#28a745',
    [ExtendedNodeStatus.RUNNING]: '#fd7e14',
    [ExtendedNodeStatus.COMPLETED]: '#17a2b8',
    [ExtendedNodeStatus.ERROR]: '#dc3545',
    [ExtendedNodeStatus.DISABLED]: '#6c757d',
    [ExtendedNodeStatus.MAINTENANCE]: '#fd7e14',
    [ExtendedNodeStatus.HIGH_PRIORITY]: '#6f42c1',
    [ExtendedNodeStatus.CRITICAL]: '#dc3545',
    [ExtendedNodeStatus.OPTIMIZED]: '#fd7e14'
  }
  
  return colors[status] || '#6c757d'
}

// 动画循环
const animate = () => {
  const render = () => {
    renderNodes()
    animationFrame.value = requestAnimationFrame(render)
  }
  
  render()
}

// 画布点击事件
const onCanvasClick = (event: MouseEvent) => {
  if (!nodeCanvas.value) return
  
  const rect = nodeCanvas.value.getBoundingClientRect()
  const x = event.clientX - rect.left
  const y = event.clientY - rect.top
  
  // 查找点击的节点
  const nodes = filteredNodes.value
  for (const node of nodes) {
    const { x, y, width, height } = node.bounds
    
    if (x >= x && x <= x + width && y >= y && y <= y + height) {
      selectedNode.value = node
      break
    }
  }
}

// 画布右键事件
const onCanvasRightClick = (event: MouseEvent) => {
  event.preventDefault()
  // 这里可以实现右键菜单
}

// 画布滚轮事件
const onCanvasWheel = (event: WheelEvent) => {
  event.preventDefault()
  // 这里可以实现缩放功能
}

// 生命周期
onMounted(async () => {
  await nextTick()
  
  // 初始化API监控器
  const { initializeDefaultEndpoints } = await import('@/services/api-monitor')
  initializeDefaultEndpoints()
  
  // 初始化节点状态管理器
  const { default: nodeStateManager } = await import('@/services/node-state-manager')
  
  // 设置事件监听器
  nodeStateManager.on('states-updated', () => {
    renderNodes()
  })
  
  nodeStateManager.on('node-state-changed', () => {
    renderNodes()
  })
  
  // 初始化节点状态
  const context = {
    userId: 'current-user',
    sessionId: 'current-session',
    systemState: {
      cpuUsage: 50,
      memoryUsage: 60,
      apiStatus: [],
      activeWorkflows: [],
      systemLoad: 0.7
    },
    currentTime: new Date(),
    userLevel: 'intermediate' as const,
    currentWorkflow: 'ai-strategy-generation',
    activeNodes: []
  }
  
  await nodeStateManager.updateAllNodeStates(context)
})

onUnmounted(() => {
  if (animationFrame.value) {
    cancelAnimationFrame(animationFrame.value)
  }
})
</script>

<style scoped>
.intelligent-node-visualizer {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: #f5f5f5;
}

.visualizer-header {
  background: white;
  padding: 1rem;
  border-bottom: 1px solid #ddd;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-controls {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.view-controls {
  display: flex;
  gap: 0.5rem;
}

.filter-controls {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.search-input {
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  width: 200px;
}

.status-filter,
.layer-filter {
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.action-controls {
  display: flex;
  gap: 0.5rem;
}

.btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.875rem;
}

.btn-primary {
  background: #007bff;
  color: white;
}

.btn-secondary {
  background: #6c757d;
  color: white;
}

.btn-success {
  background: #28a745;
  color: white;
}

.btn-warning {
  background: #ffc107;
  color: #212529;
}

.btn-sm {
  padding: 0.25rem 0.5rem;
  font-size: 0.75rem;
}

.btn.active {
  background: #0056b3;
  color: white;
}

.visualizer-content {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.node-canvas {
  flex: 1;
  background: white;
  cursor: grab;
}

.side-panel {
  width: 300px;
  background: white;
  border-left: 1px solid #ddd;
  padding: 1rem;
  overflow-y: auto;
}

.panel-section {
  margin-bottom: 2rem;
}

.panel-section h3 {
  margin: 0 0 1rem 0;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid #eee;
}

.stats-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.5rem;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.25rem 0;
}

.stat-label {
  font-weight: 500;
  color: #666;
}

.stat-value {
  font-weight: bold;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
}

.stat-value.inactive {
  background: #f8f9fa;
  color: #6c757d;
}

.stat-value.standby {
  background: #fff3cd;
  color: #856404;
}

.stat-value.recommended {
  background: #d4edda;
  color: #155724;
}

.stat-value.active {
  background: #d4edda;
  color: #155724;
}

.stat-value.running {
  background: #fff3cd;
  color: #856404;
}

.stat-value.error {
  background: #f8d7da;
  color: #721c24;
}

.recommendation-list {
  max-height: 300px;
  overflow-y: auto;
}

.recommendation-item {
  background: #f8f9fa;
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 1rem;
  margin-bottom: 0.5rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.recommendation-item:hover {
  background: #e9ecef;
  border-color: #007bff;
}

.recommendation-header {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.recommendation-icon {
  font-size: 1.5rem;
}

.recommendation-info {
  flex: 1;
}

.recommendation-info h4 {
  margin: 0;
  font-size: 1rem;
}

.recommendation-meta {
  display: flex;
  gap: 0.5rem;
  font-size: 0.8rem;
  color: #666;
}

.confidence {
  background: #007bff;
  color: white;
  padding: 0.125rem 0.25rem;
  border-radius: 3px;
}

.category {
  background: #6c757d;
  color: white;
  padding: 0.125rem 0.25rem;
  border-radius: 3px;
}

.recommendation-actions {
  display: flex;
  gap: 0.5rem;
  margin-top: 0.5rem;
}

.recommendation-reason {
  font-size: 0.8rem;
  color: #666;
  margin-top: 0.5rem;
  padding: 0.5rem;
  background: #f8f9fa;
  border-radius: 4px;
}

.legend {
  display: grid;
  grid-template-columns: auto 1fr;
  gap: 0.5rem;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.8rem;
}

.legend-color {
  width: 16px;
  height: 16px;
  border-radius: 3px;
  border: 1px solid #ddd;
}

.legend-color.inactive {
  background: #f8f9fa;
}

.legend-color.standby {
  background: #fff3cd;
}

.legend-color.recommended {
  background: #d4edda;
  border: 2px solid #28a745;
}

.legend-color.active {
  background: #d4edda;
}

.legend-color.running {
  background: #fff3cd;
}

.legend-color.error {
  background: #f8d7da;
}

.node-detail-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 8px;
  padding: 2rem;
  max-width: 500px;
  max-height: 80vh;
  overflow-y: auto;
  position: relative;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #eee;
}

.modal-header h3 {
  margin: 0;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #666;
}

.modal-body {
  max-height: 60vh;
  overflow-y: auto;
}

.node-info {
  margin-bottom: 1.5rem;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem 0;
  border-bottom: 1px solid #eee;
}

.info-item label {
  font-weight: 500;
  color: #333;
}

.status-badge {
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: 500;
}

.status-badge.inactive {
  background: #f8f9fa;
  color: #6c757d;
}

.status-badge.standby {
  background: #fff3cd;
  color: #856404;
}

.status-badge.recommended {
  background: #d4edda;
  color: #155724;
}

.status-badge.active {
  background: #d4edda;
  color: #155724;
}

.status-badge.running {
  background: #fff3cd;
  color: #856404;
}

.status-badge.error {
  background: #f8d7da;
  color: #721c24;
}

.performance-metrics {
  margin-top: 1rem;
}

.performance-metrics h4 {
  margin: 0 0 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid #eee;
}

.metric-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.metric-item label {
  font-weight: 500;
  color: #333;
  min-width: 80px;
}

.progress-bar {
  flex: 1;
  height: 8px;
  background: #e9ecef;
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: #28a745;
  transition: width 0.3s ease;
}

.node-actions {
  display: flex;
  gap: 0.5rem;
  margin-top: 1rem;
}
</style>
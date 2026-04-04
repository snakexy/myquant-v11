<template>
  <div class="backtest-view">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title"><i class="fas fa-vial"></i> 回测实验室</h1>
        <p class="page-subtitle">节点式回测工作流</p>
      </div>
      <div class="header-right">
        <button class="header-btn" @click="resetCanvas">
          🔄 重置画布
        </button>
        <button class="header-btn" @click="saveLayout">
          💾 保存布局
        </button>
        <button class="header-btn" @click="loadLayout">
          📁 加载布局
        </button>
      </div>
    </div>

    <!-- 主内容区域 -->
    <div class="main-content">
      <!-- 左侧控制面板 -->
      <div class="control-panel">
        <div class="panel-section">
          <h3 class="section-title">🎯 回测配置</h3>
          <div class="config-form">
            <div class="form-group">
              <label>股票代码</label>
              <input
                v-model="backtestConfig.symbol"
                type="text"
                placeholder="如：000001.SZ"
                class="form-input"
              />
            </div>
            <div class="form-group">
              <label>开始日期</label>
              <input
                v-model="backtestConfig.startDate"
                type="date"
                class="form-input"
              />
            </div>
            <div class="form-group">
              <label>结束日期</label>
              <input
                v-model="backtestConfig.endDate"
                type="date"
                class="form-input"
              />
            </div>
            <div class="form-group">
              <label>初始资金</label>
              <input
                v-model.number="backtestConfig.initialCapital"
                type="number"
                placeholder="1000000"
                class="form-input"
              />
            </div>
            <div class="form-group">
              <label>策略模型</label>
              <select v-model="backtestConfig.modelId" class="form-select">
                <option value="">选择策略模型</option>
                <option
                  v-for="model in availableModels"
                  :key="model.id"
                  :value="model.id"
                >
                  {{ model.name }}
                </option>
              </select>
            </div>
          </div>
        </div>

        <div class="panel-section">
          <h3 class="section-title">🧩 节点工具箱</h3>
          <div class="node-toolbox">
            <div
              v-for="nodeType in nodeTypes"
              :key="nodeType.type"
              class="node-tool-item"
              @mousedown="startDragNode(nodeType)"
            >
              <div class="node-icon">{{ nodeType.icon }}</div>
              <div class="node-name">{{ nodeType.name }}</div>
            </div>
          </div>
        </div>

        <div class="panel-section">
          <h3 class="section-title">🎮 控制中心</h3>
          <div class="control-buttons">
            <button
              @click="startBacktest"
              :disabled="!canStartBacktest || backtestLoading"
              class="control-btn primary"
            >
              {{ backtestLoading ? '回测中...' : '▶️ 开始回测' }}
            </button>
            <button
              @click="stopBacktest"
              :disabled="!backtestLoading"
              class="control-btn secondary"
            >
              ⏹️ 停止回测
            </button>
            <button
              @click="clearResults"
              class="control-btn tertiary"
            >
              🗑️ 清空结果
            </button>
          </div>
        </div>

        <div class="panel-section">
          <h3 class="section-title">📈 回测状态</h3>
          <div class="status-info">
            <div class="status-item">
              <label>当前状态</label>
              <div class="status-value" :class="backtestStatus">
                {{ getStatusText(backtestStatus) }}
              </div>
            </div>
            <div class="status-item">
              <label>进度</label>
              <div class="progress-container">
                <div class="progress-bar">
                  <div
                    class="progress-fill"
                    :style="{ width: backtestProgress + '%' }"
                  ></div>
                </div>
                <span class="progress-text">{{ backtestProgress }}%</span>
              </div>
            </div>
            <div class="status-item">
              <label>任务ID</label>
              <div class="status-value">{{ currentTaskId || '无' }}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- 节点画布 -->
      <div class="canvas-container">
        <NodeCanvas
          ref="nodeCanvasRef"
          :nodes="nodes"
          :connections="connections"
          :scale="canvasScale"
          :offset="canvasOffset"
          @node-click="handleNodeClick"
          @node-drag="handleNodeDrag"
          @node-double-click="handleNodeDoubleClick"
          @connection-create="handleConnectionCreate"
          @connection-delete="handleConnectionDelete"
          @canvas-transform="handleCanvasTransform"
          @drop="handleCanvasDrop"
        />
      </div>
    </div>

    <!-- 状态栏 -->
    <div class="status-bar">
      <div class="status-left">
        <span class="status-item">节点数量: {{ nodes.length }}</span>
        <span class="status-item">连接数量: {{ connections.length }}</span>
        <span class="status-item">缩放: {{ Math.round(canvasScale * 100) }}%</span>
      </div>
      <div class="status-right">
        <span class="status-item">{{ lastError || '就绪' }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, nextTick } from 'vue'
import NodeCanvas from '@/components/backtest/NodeCanvas.vue'
import { getBacktestModels, startBacktestTask, getBacktestResult } from '@/api/backtest'

// 接口定义
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

interface NodeType {
  type: string
  name: string
  icon: string
  defaultSize: { width: number; height: number }
}

// 响应式数据
const backtestConfig = reactive({
  symbol: '',
  startDate: '',
  endDate: '',
  initialCapital: 1000000,
  modelId: ''
})

const availableModels = ref<Array<{
  id: string
  name: string
  description: string
  type: string
}>>([])

const nodes = ref<NodeData[]>([])
const connections = ref<ConnectionData[]>([])
const selectedNode = ref<NodeData | null>(null)
const backtestLoading = ref(false)
const backtestProgress = ref(0)
const backtestStatus = ref<'idle' | 'running' | 'completed' | 'error'>('idle')
const currentTaskId = ref('')
const lastError = ref('')

// 画布状态
const canvasScale = ref(1)
const canvasOffset = ref({ x: 0, y: 0 })
const nodeCanvasRef = ref()

// 节点类型定义
const nodeTypes: NodeType[] = [
  { type: 'config', name: '配置节点', icon: '⚙️', defaultSize: { width: 200, height: 150 } },
  { type: 'processing', name: '处理节点', icon: '⚡', defaultSize: { width: 220, height: 180 } },
  { type: 'result', name: '结果节点', icon: '📊', defaultSize: { width: 240, height: 200 } },
  { type: 'metric', name: '指标节点', icon: '📈', defaultSize: { width: 180, height: 120 } }
]

// 计算属性
const canStartBacktest = computed(() => {
  return backtestConfig.symbol && 
         backtestConfig.startDate && 
         backtestConfig.endDate && 
         backtestConfig.modelId &&
         backtestConfig.initialCapital > 0
})

// 方法
const loadModels = async () => {
  try {
    const models = await getBacktestModels()
    availableModels.value = models
    console.log('加载回测模型成功:', models)
  } catch (error) {
    console.error('加载回测模型失败:', error)
    lastError.value = '加载模型失败'
  }
}

const startBacktest = async () => {
  if (!canStartBacktest.value) return
  
  backtestLoading.value = true
  backtestProgress.value = 0
  backtestStatus.value = 'running'
  lastError.value = ''
  
  try {
    // 创建配置节点
    const configNode: NodeData = {
      id: `config-${Date.now()}`,
      type: 'config',
      title: '回测配置',
      icon: '⚙️',
      position: { x: 100, y: 100 },
      size: { width: 200, height: 150 },
      status: 'completed',
      parameters: [
        { name: '股票代码', value: backtestConfig.symbol },
        { name: '开始日期', value: backtestConfig.startDate },
        { name: '结束日期', value: backtestConfig.endDate },
        { name: '初始资金', value: backtestConfig.initialCapital.toString() },
        { name: '策略模型', value: backtestConfig.modelId }
      ]
    }
    
    // 创建处理节点
    const processingNode: NodeData = {
      id: `processing-${Date.now()}`,
      type: 'processing',
      title: '策略执行',
      icon: '⚡',
      position: { x: 400, y: 100 },
      size: { width: 220, height: 180 },
      status: 'running',
      showProgress: true,
      progress: 0
    }
    
    // 创建结果节点
    const resultNode: NodeData = {
      id: `result-${Date.now()}`,
      type: 'result',
      title: '回测结果',
      icon: '📊',
      position: { x: 700, y: 100 },
      size: { width: 240, height: 200 },
      status: 'idle'
    }
    
    // 添加节点到画布
    nodes.value.push(configNode, processingNode, resultNode)
    
    // 创建连接
    const connection1: ConnectionData = {
      id: `conn-${Date.now()}-1`,
      from: configNode.id,
      to: processingNode.id,
      type: 'data',
      technology: 'QLib',
      status: 'active'
    }
    
    const connection2: ConnectionData = {
      id: `conn-${Date.now()}-2`,
      from: processingNode.id,
      to: resultNode.id,
      type: 'data',
      technology: 'Strategy',
      status: 'active'
    }
    
    connections.value.push(connection1, connection2)
    
    // 启动回测任务
    const taskResult = await startBacktestTask(backtestConfig)
    currentTaskId.value = taskResult.taskId
    
    console.log('回测任务已启动:', taskResult.taskId)
    
    // 轮询获取回测结果
    const pollInterval = setInterval(async () => {
      try {
        const result = await getBacktestResult(currentTaskId.value)
        
        if (result.status === 'completed') {
          // 更新处理节点状态
          const procNode = nodes.value.find(n => n.id === processingNode.id)
          if (procNode) {
            procNode.status = 'completed'
            procNode.progress = 100
          }
          
          // 更新结果节点
          const resNode = nodes.value.find(n => n.id === resultNode.id)
          if (resNode && result.data) {
            resNode.status = 'completed'
            resNode.metrics = [
              { label: '总收益率', value: `${result.data.totalReturn}%` },
              { label: '年化收益率', value: `${result.data.annualizedReturn}%` },
              { label: '夏普比率', value: result.data.sharpeRatio },
              { label: '最大回撤', value: `${result.data.maxDrawdown}%` },
              { label: '胜率', value: `${result.data.winRate}%` },
              { label: '交易次数', value: result.data.totalTrades }
            ]
            
            // 添加六边形性能图数据
            resNode.showHexagon = true
            resNode.hexagonData = [
              { label: '收益', value: result.data.totalReturn, max: 100 },
              { label: '风险', value: 100 - result.data.maxDrawdown, max: 100 },
              { label: '稳定性', value: result.data.sharpeRatio * 20, max: 100 },
              { label: '胜率', value: result.data.winRate, max: 100 },
              { label: '频率', value: Math.min(result.data.totalTrades / 10, 100), max: 100 },
              { label: '效率', value: result.data.annualizedReturn, max: 50 }
            ]
          }
          
          backtestProgress.value = 100
          backtestStatus.value = 'completed'
          backtestLoading.value = false
          clearInterval(pollInterval)
          console.log('回测完成:', result.data)
        } else if (result.status === 'failed') {
          console.error('回测失败:', result.error)
          lastError.value = result.error || '回测失败'
          backtestStatus.value = 'error'
          backtestLoading.value = false
          
          // 更新处理节点状态
          const procNode = nodes.value.find(n => n.id === processingNode.id)
          if (procNode) {
            procNode.status = 'error'
          }
          
          clearInterval(pollInterval)
        } else {
          backtestProgress.value = result.progress || 0
          
          // 更新处理节点进度
          const procNode = nodes.value.find(n => n.id === processingNode.id)
          if (procNode) {
            procNode.progress = result.progress || 0
          }
        }
      } catch (error) {
        console.error('获取回测结果失败:', error)
        lastError.value = '获取结果失败'
        backtestStatus.value = 'error'
        backtestLoading.value = false
        clearInterval(pollInterval)
      }
    }, 2000) // 每2秒轮询一次
    
  } catch (error) {
    console.error('启动回测失败:', error)
    lastError.value = '启动回测失败'
    backtestStatus.value = 'error'
    backtestLoading.value = false
  }
}

const stopBacktest = () => {
  backtestLoading.value = false
  backtestStatus.value = 'idle'
  currentTaskId.value = ''
  lastError.value = '回测已停止'
}

const clearResults = () => {
  nodes.value = []
  connections.value = []
  selectedNode.value = null
  backtestProgress.value = 0
  backtestStatus.value = 'idle'
  currentTaskId.value = ''
  lastError.value = ''
}

const resetCanvas = () => {
  canvasScale.value = 1
  canvasOffset.value = { x: 0, y: 0 }
  if (nodeCanvasRef.value) {
    nodeCanvasRef.value.resetTransform()
  }
}

const saveLayout = () => {
  const layout = {
    nodes: nodes.value,
    connections: connections.value,
    canvasScale: canvasScale.value,
    canvasOffset: canvasOffset.value
  }
  localStorage.setItem('backtest-layout', JSON.stringify(layout))
  lastError.value = '布局已保存'
}

const loadLayout = () => {
  const savedLayout = localStorage.getItem('backtest-layout')
  if (savedLayout) {
    try {
      const layout = JSON.parse(savedLayout)
      nodes.value = layout.nodes || []
      connections.value = layout.connections || []
      canvasScale.value = layout.canvasScale || 1
      canvasOffset.value = layout.canvasOffset || { x: 0, y: 0 }
      lastError.value = '布局已加载'
    } catch (error) {
      console.error('加载布局失败:', error)
      lastError.value = '加载布局失败'
    }
  } else {
    lastError.value = '没有找到保存的布局'
  }
}

// 节点操作
const startDragNode = (nodeType: NodeType) => {
  // 这里可以实现拖拽创建节点的逻辑
  console.log('开始拖拽节点:', nodeType)
}

const handleNodeClick = (nodeId: string) => {
  selectedNode.value = nodes.value.find(n => n.id === nodeId) || null
  // 显示节点属性面板
  showNodeProperties(selectedNode.value)
}

const handleNodeDrag = (nodeId: string, position: { x: number; y: number }) => {
  const node = nodes.value.find(n => n.id === nodeId)
  if (node) {
    node.position = position
  }
}

const handleNodeDoubleClick = (nodeId: string) => {
  const node = nodes.value.find(n => n.id === nodeId)
  if (node) {
    // 双击节点显示详细属性或结果
    showNodeDetails(node)
  }
}

// 显示节点属性面板
const showNodeProperties = (node: NodeData | null) => {
  if (!node) return
  
  // 创建或更新属性面板
  const existingPanel = document.getElementById('node-properties-panel')
  if (existingPanel) {
    existingPanel.remove()
  }
  
  const panel = document.createElement('div')
  panel.id = 'node-properties-panel'
  panel.className = 'node-properties-panel'
  panel.style.cssText = `
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    background: #1a1a2e;
    border: 1px solid #404040;
    border-radius: 12px;
    padding: 20px;
    min-width: 300px;
    z-index: 1000;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
  `
  
  let content = `
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
      <h3 style="margin: 0; color: #f8fafc; font-size: 16px;">${node.icon} ${node.title}</h3>
      <button onclick="this.parentElement.parentElement.remove()" style="background: none; border: none; color: #94a3b8; cursor: pointer; font-size: 18px;">×</button>
    </div>
  `
  
  // 根据节点类型显示不同内容
  if (node.type === 'config') {
    content += `
      <div style="margin-bottom: 12px;">
        <label style="display: block; margin-bottom: 4px; color: #94a3b8; font-size: 12px;">配置参数</label>
        <div style="background: rgba(255, 255, 255, 0.05); border-radius: 6px; padding: 12px;">
    `
    
    if (node.parameters) {
      node.parameters.forEach(param => {
        content += `
          <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
            <span style="color: #94a3b8; font-size: 12px;">${param.name}:</span>
            <span style="color: #f8fafc; font-size: 12px; font-weight: 500;">${param.value}</span>
          </div>
        `
      })
    }
    
    content += `</div></div>`
  } else if (node.type === 'processing') {
    content += `
      <div style="margin-bottom: 12px;">
        <label style="display: block; margin-bottom: 4px; color: #94a3b8; font-size: 12px;">处理状态</label>
        <div style="display: flex; align-items: center; gap: 8px;">
          <div style="width: 12px; height: 12px; border-radius: 50%; background: ${node.status === 'running' ? '#f59e0b' : node.status === 'completed' ? '#10b981' : node.status === 'error' ? '#ef4444' : '#64748b'};"></div>
          <span style="color: #f8fafc; font-size: 12px;">${getStatusText(node.status)}</span>
        </div>
      </div>
    `
    
    if (node.showProgress && node.progress !== undefined) {
      content += `
        <div style="margin-bottom: 12px;">
          <label style="display: block; margin-bottom: 4px; color: #94a3b8; font-size: 12px;">处理进度</label>
          <div style="display: flex; align-items: center; gap: 8px;">
            <div style="flex: 1; height: 6px; background: rgba(255, 255, 255, 0.1); border-radius: 3px; overflow: hidden;">
              <div style="height: 100%; width: ${node.progress}%; background: linear-gradient(90deg, #2563eb, #7c3aed); transition: width 0.3s ease;"></div>
            </div>
            <span style="color: #2563eb; font-size: 12px; font-weight: 500; min-width: 35px;">${node.progress}%</span>
          </div>
        </div>
      `
    }
  } else if (node.type === 'result') {
    if (node.metrics) {
      content += `
        <div style="margin-bottom: 12px;">
          <label style="display: block; margin-bottom: 8px; color: #94a3b8; font-size: 12px;">回测指标</label>
          <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 8px;">
      `
      
      node.metrics.forEach(metric => {
        content += `
          <div style="background: rgba(255, 255, 255, 0.05); border-radius: 6px; padding: 8px; text-align: center;">
            <div style="color: #2563eb; font-size: 14px; font-weight: 700; margin-bottom: 2px;">${metric.value}</div>
            <div style="color: #94a3b8; font-size: 10px;">${metric.label}</div>
          </div>
        `
      })
      
      content += `</div></div>`
    }
    
    if (node.showHexagon && node.hexagonData) {
      content += `
        <div style="margin-bottom: 12px;">
          <label style="display: block; margin-bottom: 8px; color: #94a3b8; font-size: 12px;">性能雷达图</label>
          <div style="display: flex; justify-content: center;">
            <svg width="150" height="150" viewBox="0 0 200 200">
              <polygon points="100,20 170,60 170,140 100,180 30,140 30,60" fill="none" stroke="rgba(255, 255, 255, 0.2)" stroke-width="2"/>
              <polygon points="${node.hexagonData.map((item, index) => {
                const angles = [0, 60, 120, 180, 240, 300]
                const angle = (angles[index] - 90) * (Math.PI / 180)
                const value = (item.value / item.max) * 60
                const x = 100 + value * Math.cos(angle)
                const y = 100 + value * Math.sin(angle)
                return `${x},${y}`
              }).join(' ')}" fill="rgba(37, 99, 235, 0.3)" stroke="#2563eb" stroke-width="2"/>
            </svg>
          </div>
        </div>
      `
    }
  } else if (node.type === 'metric') {
    if (node.metrics) {
      content += `
        <div style="margin-bottom: 12px;">
          <label style="display: block; margin-bottom: 8px; color: #94a3b8; font-size: 12px;">指标详情</label>
      `
      
      node.metrics.forEach(metric => {
        content += `
          <div style="display: flex; justify-content: space-between; margin-bottom: 8px; padding: 8px; background: rgba(255, 255, 255, 0.05); border-radius: 6px;">
            <span style="color: #94a3b8; font-size: 12px;">${metric.label}</span>
            <span style="color: #f8fafc; font-size: 12px; font-weight: 500;">${metric.value}</span>
          </div>
        `
      })
      
      content += `</div>`
    }
  }
  
  // 添加通用信息
  content += `
    <div style="margin-bottom: 12px;">
      <label style="display: block; margin-bottom: 4px; color: #94a3b8; font-size: 12px;">节点信息</label>
      <div style="background: rgba(255, 255, 255, 0.05); border-radius: 6px; padding: 8px;">
        <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
          <span style="color: #94a3b8; font-size: 12px;">节点ID:</span>
          <span style="color: #f8fafc; font-size: 12px;">${node.id}</span>
        </div>
        <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
          <span style="color: #94a3b8; font-size: 12px;">节点类型:</span>
          <span style="color: #f8fafc; font-size: 12px;">${node.type}</span>
        </div>
        <div style="display: flex; justify-content: space-between;">
          <span style="color: #94a3b8; font-size: 12px;">状态:</span>
          <span style="color: ${node.status === 'running' ? '#f59e0b' : node.status === 'completed' ? '#10b981' : node.status === 'error' ? '#ef4444' : '#64748b'}; font-size: 12px;">${getStatusText(node.status)}</span>
        </div>
      </div>
    </div>
  `
  
  panel.innerHTML = content
  document.body.appendChild(panel)
}

// 显示节点详细信息
const showNodeDetails = (node: NodeData) => {
  // 可以实现更详细的节点信息展示
  console.log('显示节点详情:', node)
  showNodeProperties(node)
}

const handleConnectionCreate = (connection: ConnectionData) => {
  connections.value.push(connection)
}

const handleConnectionDelete = (connectionId: string) => {
  connections.value = connections.value.filter(c => c.id !== connectionId)
}

const handleCanvasTransform = (scale: number, offset: { x: number; y: number }) => {
  canvasScale.value = scale
  canvasOffset.value = offset
}

const handleCanvasDrop = (event: DragEvent) => {
  // 处理拖拽放置
  console.log('画布放置事件:', event)
}

// 节点属性操作
const updateNodeProperty = (property: string, value: any) => {
  if (selectedNode.value) {
    (selectedNode.value as any)[property] = value
  }
}

const addParameter = () => {
  if (selectedNode.value && selectedNode.value.type === 'config') {
    if (!selectedNode.value.parameters) {
      selectedNode.value.parameters = []
    }
    selectedNode.value.parameters.push({ name: '', value: '' })
  }
}

const removeParameter = (index: number) => {
  if (selectedNode.value && selectedNode.value.parameters) {
    selectedNode.value.parameters.splice(index, 1)
  }
}

const getStatusText = (status: string) => {
  const statusMap: Record<string, string> = {
    idle: '空闲',
    running: '运行中',
    completed: '已完成',
    error: '错误'
  }
  return statusMap[status] || status
}

// 生命周期
onMounted(() => {
  loadModels()
  
  // 设置默认日期
  const today = new Date()
  const lastYear = new Date(today.getFullYear() - 1, today.getMonth(), today.getDate())
  
  backtestConfig.endDate = today.toISOString().split('T')[0]
  backtestConfig.startDate = lastYear.toISOString().split('T')[0]
  
  // 尝试加载保存的布局
  loadLayout()
})
</script>

<style lang="scss" scoped>
.backtest-view {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: #0a0a0f;
  color: #f8fafc;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  background: linear-gradient(135deg, rgba(37, 99, 235, 0.1) 0%, rgba(124, 58, 237, 0.05) 100%);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  
  .header-left {
    .page-title {
      font-size: 24px;
      font-weight: 700;
      margin: 0 0 4px 0;
      background: linear-gradient(135deg, #2563eb 0%, #7c3aed 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
    }
    
    .page-subtitle {
      font-size: 14px;
      color: #94a3b8;
      margin: 0;
    }
  }
  
  .header-right {
    display: flex;
    gap: 8px;
    
    .header-btn {
      padding: 8px 16px;
      background: rgba(255, 255, 255, 0.05);
      border: 1px solid rgba(255, 255, 255, 0.1);
      border-radius: 6px;
      color: #94a3b8;
      font-size: 12px;
      cursor: pointer;
      transition: all 0.3s ease;
      
      &:hover {
        background: rgba(255, 255, 255, 0.1);
        border-color: rgba(255, 255, 255, 0.2);
        color: #f8fafc;
      }
    }
  }
}

.main-content {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.control-panel {
  width: 280px;
  background: #1a1a2e;
  border-right: 1px solid rgba(255, 255, 255, 0.1);
  overflow-y: auto;
  padding: 16px;
  
  .panel-section {
    margin-bottom: 24px;
    
    .section-title {
      font-size: 14px;
      font-weight: 600;
      color: #f8fafc;
      margin: 0 0 12px 0;
      display: flex;
      align-items: center;
      gap: 8px;
    }
  }
  
  .config-form {
    display: flex;
    flex-direction: column;
    gap: 12px;
    
    .form-group {
      display: flex;
      flex-direction: column;
      gap: 6px;
      
      label {
        font-size: 12px;
        font-weight: 500;
        color: #94a3b8;
      }
      
      .form-input,
      .form-select {
        padding: 8px 12px;
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 6px;
        color: #f8fafc;
        font-size: 12px;
        transition: all 0.3s ease;
        
        &:focus {
          outline: none;
          border-color: #2563eb;
          box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.2);
        }
        
        &.readonly {
          background: rgba(255, 255, 255, 0.02);
          color: #64748b;
        }
        
        &::placeholder {
          color: #64748b;
        }
      }
    }
  }
  
  .node-toolbox {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 8px;
    
    .node-tool-item {
      display: flex;
      flex-direction: column;
      align-items: center;
      padding: 12px 8px;
      background: rgba(255, 255, 255, 0.05);
      border: 1px solid rgba(255, 255, 255, 0.1);
      border-radius: 8px;
      cursor: grab;
      transition: all 0.3s ease;
      
      &:hover {
        background: rgba(255, 255, 255, 0.1);
        border-color: #2563eb;
        transform: translateY(-2px);
      }
      
      &:active {
        cursor: grabbing;
      }
      
      .node-icon {
        font-size: 20px;
        margin-bottom: 4px;
      }
      
      .node-name {
        font-size: 10px;
        color: #94a3b8;
        text-align: center;
      }
    }
  }
  
  .control-buttons {
    display: flex;
    flex-direction: column;
    gap: 8px;
    
    .control-btn {
      padding: 10px 16px;
      border: none;
      border-radius: 6px;
      font-size: 12px;
      font-weight: 500;
      cursor: pointer;
      transition: all 0.3s ease;
      
      &.primary {
        background: linear-gradient(135deg, #2563eb 0%, #7c3aed 100%);
        color: white;
        
        &:hover:not(:disabled) {
          transform: translateY(-1px);
          box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
        }
      }
      
      &.secondary {
        background: rgba(245, 158, 11, 0.1);
        color: #f59e0b;
        border: 1px solid rgba(245, 158, 11, 0.3);
        
        &:hover:not(:disabled) {
          background: rgba(245, 158, 11, 0.2);
        }
      }
      
      &.tertiary {
        background: rgba(239, 68, 68, 0.1);
        color: var(--market-fall);
        border: 1px solid rgba(239, 68, 68, 0.3);
        
        &:hover:not(:disabled) {
          background: rgba(239, 68, 68, 0.2);
        }
      }
      
      &:disabled {
        opacity: 0.5;
        cursor: not-allowed;
      }
    }
  }
}

.canvas-container {
  flex: 1;
  position: relative;
  background: #0a0a0f;
  overflow: hidden;
}

.properties-panel {
  width: 280px;
  background: #1a1a2e;
  border-left: 1px solid rgba(255, 255, 255, 0.1);
  overflow-y: auto;
  padding: 16px;
  
  .panel-section {
    margin-bottom: 24px;
    
    .section-title {
      font-size: 14px;
      font-weight: 600;
      color: #f8fafc;
      margin: 0 0 12px 0;
      display: flex;
      align-items: center;
      gap: 8px;
    }
  }
  
  .node-properties {
    .property-item {
      margin-bottom: 12px;
      
      label {
        display: block;
        font-size: 12px;
        font-weight: 500;
        color: #94a3b8;
        margin-bottom: 4px;
      }
      
      .form-input,
      .form-select {
        width: 100%;
        padding: 6px 10px;
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 4px;
        color: #f8fafc;
        font-size: 12px;
        transition: all 0.3s ease;
        
        &:focus {
          outline: none;
          border-color: #2563eb;
          box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.2);
        }
      }
    }
    
    .config-properties {
      margin-top: 16px;
      padding-top: 16px;
      border-top: 1px solid rgba(255, 255, 255, 0.1);
      
      .parameter-list {
        display: flex;
        flex-direction: column;
        gap: 8px;
        
        .parameter-item {
          display: flex;
          gap: 4px;
          
          .param-input {
            flex: 1;
            padding: 4px 8px;
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 4px;
            color: #f8fafc;
            font-size: 11px;
            
            &:focus {
              outline: none;
              border-color: #2563eb;
            }
          }
          
          .param-remove-btn {
            padding: 4px 6px;
            background: rgba(239, 68, 68, 0.1);
            border: 1px solid rgba(239, 68, 68, 0.3);
            border-radius: 4px;
            color: var(--market-fall);
            font-size: 10px;
            cursor: pointer;
            
            &:hover {
              background: rgba(239, 68, 68, 0.2);
            }
          }
        }
        
        .param-add-btn {
          padding: 6px 12px;
          background: rgba(37, 99, 235, 0.1);
          border: 1px solid rgba(37, 99, 235, 0.3);
          border-radius: 4px;
          color: #2563eb;
          font-size: 11px;
          cursor: pointer;
          margin-top: 4px;
          
          &:hover {
            background: rgba(37, 99, 235, 0.2);
          }
        }
      }
    }
  }
  
  .no-selection {
    text-align: center;
    padding: 20px;
    color: #64748b;
    font-size: 12px;
  }
  
  .status-info {
    .status-item {
      margin-bottom: 12px;
      
      label {
        display: block;
        font-size: 12px;
        font-weight: 500;
        color: #94a3b8;
        margin-bottom: 4px;
      }
      
      .status-value {
        padding: 6px 10px;
        background: rgba(255, 255, 255, 0.05);
        border-radius: 4px;
        font-size: 12px;
        
        &.idle {
          color: #64748b;
        }
        
        &.running {
          color: #f59e0b;
          animation: pulse 2s infinite;
        }
        
        &.completed {
          color: var(--market-rise);
        }
        
        &.error {
          color: var(--market-fall);
        }
      }
      
      .progress-container {
        display: flex;
        align-items: center;
        gap: 8px;
        
        .progress-bar {
          flex: 1;
          height: 6px;
          background: rgba(255, 255, 255, 0.1);
          border-radius: 3px;
          overflow: hidden;
          
          .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #2563eb, #7c3aed);
            transition: width 0.3s ease;
          }
        }
        
        .progress-text {
          font-size: 11px;
          color: #2563eb;
          font-weight: 500;
          min-width: 35px;
        }
      }
    }
  }
}

.status-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 24px;
  background: #1a1a2e;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  font-size: 11px;
  color: #94a3b8;
  
  .status-left,
  .status-right {
    display: flex;
    gap: 16px;
    
    .status-item {
      display: flex;
      align-items: center;
      gap: 4px;
    }
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

// 响应式设计
@media (max-width: 1200px) {
  .control-panel,
  .properties-panel {
    width: 240px;
  }
}

@media (max-width: 768px) {
  .main-content {
    flex-direction: column;
  }
  
  .control-panel,
  .properties-panel {
    width: 100%;
    height: 200px;
  }
  
  .canvas-container {
    height: 400px;
  }
}
</style>
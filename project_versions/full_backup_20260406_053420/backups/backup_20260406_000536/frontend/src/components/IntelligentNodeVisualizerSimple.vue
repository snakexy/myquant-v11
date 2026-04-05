<template>
  <div class="intelligent-node-visualizer-simple">
    <div class="visualizer-header">
      <div class="header-title">
        <h2>智能节点可视化系统</h2>
        <p>基于七层架构的完整量化交易平台节点管理</p>
      </div>
      
      <div class="header-controls">
        <div class="view-controls">
          <button 
            @click="setViewMode('grid')" 
            :class="['btn', 'btn-sm', { active: viewMode === 'grid' }]"
            title="网格视图"
          >
            <i class="fas fa-th"></i>
          </button>
          <button 
            @click="setViewMode('hierarchical')" 
            :class="['btn', 'btn-sm', { active: viewMode === 'hierarchical' }]"
            title="层次视图"
          >
            <i class="fas fa-sitemap"></i>
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
            <option value="inactive">未激活</option>
            <option value="active">已激活</option>
            <option value="skipped">跳过</option>
          </select>
          
          <select v-model="layerFilter" class="layer-filter" @change="onLayerFilterChange">
            <option value="all">所有层级</option>
            <option value="data_hub">数据中枢层</option>
            <option value="qlib_core">QLib核心层</option>
            <option value="business_logic">业务逻辑层</option>
            <option value="investment_analysis">投资分析系统</option>
            <option value="ai_strategy">AI智能策略层</option>
            <option value="live_trading">实盘交易层</option>
            <option value="experiment_mgmt">实验管理层</option>
            <option value="application_service">应用服务层</option>
          </select>
        </div>
        
        <div class="action-controls">
          <button @click="resetAllNodes" class="btn btn-secondary">
            <i class="fas fa-redo"></i>
            重置所有
          </button>
          <button @click="showHelp" class="btn btn-info">
            <i class="fas fa-question"></i>
            帮助
          </button>
        </div>
      </div>
    </div>
    
    <div class="visualizer-content">
      <div class="nodes-container" ref="nodesContainer">
        <div 
          v-for="node in filteredNodes" 
          :key="node.id"
          :class="['node-item', `status-${node.status}`, `layer-${node.metadata.layer}`]"
          :style="getNodeStyle(node)"
          @click="selectNode(node)"
          @contextmenu.prevent="showNodeContextMenu(node, $event)"
        >
          <div class="node-header">
            <div class="node-icon">{{ node.metadata.icon }}</div>
            <div class="node-id">{{ node.id }}</div>
          </div>
          <div class="node-title">{{ node.name }}</div>
          <div class="node-description">{{ node.metadata.description }}</div>
          <div class="node-status">
            <span :class="['status-badge', node.status]">{{ getStatusText(node.status) }}</span>
          </div>
        </div>
      </div>
      
      <div class="side-panel">
        <div class="panel-section">
          <h3>节点统计</h3>
          <div class="stats-grid">
            <div class="stat-item">
              <span class="stat-label">总节点数:</span>
              <span class="stat-value">{{ nodeStats.total }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">未激活:</span>
              <span class="stat-value inactive">{{ nodeStats.inactive }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">已激活:</span>
              <span class="stat-value active">{{ nodeStats.active }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">跳过:</span>
              <span class="stat-value skipped">{{ nodeStats.skipped }}</span>
            </div>
          </div>
        </div>
        
        <div class="panel-section">
          <h3>图例</h3>
          <div class="legend">
            <div class="legend-item">
              <span class="legend-color inactive"></span>
              <span>未激活</span>
            </div>
            <div class="legend-item">
              <span class="legend-color active"></span>
              <span>已激活</span>
            </div>
            <div class="legend-item">
              <span class="legend-color skipped"></span>
              <span>跳过</span>
            </div>
          </div>
        </div>
        
        <div class="panel-section" v-if="selectedNode">
          <h3>节点详情</h3>
          <div class="node-details">
            <div class="detail-item">
              <label>节点ID:</label>
              <span>{{ selectedNode.id }}</span>
            </div>
            <div class="detail-item">
              <label>名称:</label>
              <span>{{ selectedNode.name }}</span>
            </div>
            <div class="detail-item">
              <label>描述:</label>
              <span>{{ selectedNode.metadata.description }}</span>
            </div>
            <div class="detail-item">
              <label>层级:</label>
              <span>{{ getLayerText(selectedNode.metadata.layer) }}</span>
            </div>
            <div class="detail-item">
              <label>复杂度:</label>
              <span>{{ selectedNode.metadata.complexity }}/5</span>
            </div>
            <div class="detail-item">
              <label>状态:</label>
              <span :class="['status-badge', selectedNode.status]">{{ getStatusText(selectedNode.status) }}</span>
            </div>
            <div class="detail-actions">
              <button 
                v-if="selectedNode.status === 'inactive'"
                @click="activateNode(selectedNode.id)" 
                class="btn btn-sm btn-primary"
              >
                激活节点
              </button>
              <button 
                v-if="selectedNode.status === 'active'"
                @click="skipNode(selectedNode.id)" 
                class="btn btn-sm btn-warning"
              >
                跳过节点
              </button>
              <button 
                v-if="selectedNode.status === 'skipped'"
                @click="deactivateNode(selectedNode.id)" 
                class="btn btn-sm btn-secondary"
              >
                取消跳过
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 帮助弹窗 -->
    <div v-if="showHelpModal" class="modal-overlay" @click="closeHelpModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>系统帮助</h3>
          <button class="close-btn" @click="closeHelpModal">×</button>
        </div>
        <div class="modal-body">
          <div class="help-section">
            <h4>基本操作</h4>
            <ul>
              <li><strong>点击节点:</strong> 查看节点详细信息</li>
              <li><strong>右键节点:</strong> 显示上下文菜单</li>
              <li><strong>搜索节点:</strong> 使用搜索框过滤节点</li>
              <li><strong>状态过滤:</strong> 按节点状态过滤显示</li>
              <li><strong>层级过滤:</strong> 按架构层级过滤显示</li>
            </ul>
          </div>
          
          <div class="help-section">
            <h4>节点状态说明</h4>
            <ul>
              <li><span class="status-indicator inactive"></span> <strong>未激活:</strong> 节点未激活，可以点击激活</li>
              <li><span class="status-indicator active"></span> <strong>已激活:</strong> 节点已激活，正在工作</li>
              <li><span class="status-indicator skipped"></span> <strong>跳过:</strong> 节点被跳过，数据流将绕过此节点</li>
            </ul>
          </div>
          
          <div class="help-section">
            <h4>七层架构说明</h4>
            <ul>
              <li><strong>数据中枢层:</strong> 数据获取、处理和存储</li>
              <li><strong>QLib核心层:</strong> 量化分析核心功能</li>
              <li><strong>业务逻辑层:</strong> 业务逻辑和因子计算</li>
              <li><strong>投资分析系统:</strong> 投资组合分析和绩效评估</li>
              <li><strong>AI智能策略层:</strong> AI策略生成和优化</li>
              <li><strong>实盘交易层:</strong> 实时交易和风险管理</li>
              <li><strong>实验管理层:</strong> 实验管理和结果分析</li>
              <li><strong>应用服务层:</strong> 工作流、配置和监控服务</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'

// 节点状态枚举
enum NodeState {
  INACTIVE = 'inactive',    // 未激活 - 灰色
  ACTIVE = 'active',      // 已激活 - 绿色
  SKIPPED = 'skipped'     // 跳过 - 黄色
}

// 响应式数据
const viewMode = ref('grid')
const searchQuery = ref('')
const statusFilter = ref('all')
const layerFilter = ref('all')
const selectedNode = ref<any>(null)
const nodesContainer = ref<HTMLElement | null>(null)
const showHelpModal = ref(false)

// 节点数据
const nodes = ref<any[]>([])

// 初始化节点数据
const initializeNodes = () => {
  nodes.value = [
    // 数据中枢层
    {
      id: 'DH1',
      name: 'QuantDataHub核心',
      metadata: {
        description: '数据中枢核心模块',
        icon: '📊',
        complexity: 3,
        layer: 'data_hub'
      },
      status: NodeState.INACTIVE,
      x: 100,
      y: 100
    },
    {
      id: 'DH2',
      name: '统一数据提供器',
      metadata: {
        description: '统一数据查询接口',
        icon: '🔧',
        complexity: 2,
        layer: 'data_hub'
      },
      status: NodeState.INACTIVE,
      x: 300,
      y: 100
    },
    {
      id: 'DH3',
      name: '缓存管理器',
      metadata: {
        description: '数据缓存管理',
        icon: '📥',
        complexity: 2,
        layer: 'data_hub'
      },
      status: NodeState.INACTIVE,
      x: 500,
      y: 100
    },
    {
      id: 'DH4',
      name: '数据管道',
      metadata: {
        description: '数据管道处理',
        icon: '🔍',
        complexity: 3,
        layer: 'data_hub'
      },
      status: NodeState.INACTIVE,
      x: 700,
      y: 100
    },
    {
      id: 'DH5',
      name: '存储管理器',
      metadata: {
        description: '存储管理服务',
        icon: '💾',
        complexity: 2,
        layer: 'data_hub'
      },
      status: NodeState.INACTIVE,
      x: 900,
      y: 100
    },
    
    // QLib核心层
    {
      id: 'QL1',
      name: '数据处理模块',
      metadata: {
        description: 'QLib数据处理核心',
        icon: '🔌',
        complexity: 4,
        layer: 'qlib_core'
      },
      status: NodeState.INACTIVE,
      x: 100,
      y: 250
    },
    {
      id: 'QL2',
      name: '分析系统集成',
      metadata: {
        description: 'QLib分析工具集成',
        icon: '⚙️',
        complexity: 3,
        layer: 'qlib_core'
      },
      status: NodeState.INACTIVE,
      x: 300,
      y: 250
    },
    {
      id: 'QL3',
      name: '回测系统',
      metadata: {
        description: 'QLib回测引擎',
        icon: '🔄',
        complexity: 5,
        layer: 'qlib_core'
      },
      status: NodeState.INACTIVE,
      x: 500,
      y: 250
    },
    {
      id: 'QL4',
      name: '计算优化层',
      metadata: {
        description: 'QLib计算优化',
        icon: '📈',
        complexity: 4,
        layer: 'qlib_core'
      },
      status: NodeState.INACTIVE,
      x: 700,
      y: 250
    },
    
    // 业务逻辑层
    {
      id: 'BL1',
      name: '因子计算引擎',
      metadata: {
        description: '量化因子计算',
        icon: '🧮',
        complexity: 4,
        layer: 'business_logic'
      },
      status: NodeState.INACTIVE,
      x: 100,
      y: 400
    },
    {
      id: 'BL2',
      name: '策略系统',
      metadata: {
        description: '策略管理系统',
        icon: '🔄',
        complexity: 3,
        layer: 'business_logic'
      },
      status: NodeState.INACTIVE,
      x: 300,
      y: 400
    },
    {
      id: 'BL3',
      name: '策略回放系统',
      metadata: {
        description: '策略回放分析',
        icon: '📊',
        complexity: 3,
        layer: 'business_logic'
      },
      status: NodeState.INACTIVE,
      x: 500,
      y: 400
    },
    {
      id: 'BL4',
      name: '模型管理服务',
      metadata: {
        description: '模型管理服务',
        icon: '🔧',
        complexity: 4,
        layer: 'business_logic'
      },
      status: NodeState.INACTIVE,
      x: 700,
      y: 400
    },
    
    // 投资分析系统
    {
      id: 'BL5',
      name: '投资分析系统',
      metadata: {
        description: '投资组合分析和绩效评估',
        icon: '📈',
        complexity: 4,
        layer: 'investment_analysis'
      },
      status: NodeState.INACTIVE,
      x: 100,
      y: 550
    },
    {
      id: 'IA1',
      name: '投资组合分析',
      metadata: {
        description: '投资组合风险和收益分析',
        icon: '📊',
        complexity: 4,
        layer: 'investment_analysis'
      },
      status: NodeState.INACTIVE,
      x: 300,
      y: 550
    },
    {
      id: 'IA2',
      name: '归因分析',
      metadata: {
        description: '投资组合归因分析',
        icon: '📈',
        complexity: 4,
        layer: 'investment_analysis'
      },
      status: NodeState.INACTIVE,
      x: 500,
      y: 550
    },
    {
      id: 'IA3',
      name: '投资策略实现',
      metadata: {
        description: '投资策略执行和管理',
        icon: '⚙️',
        complexity: 4,
        layer: 'investment_analysis'
      },
      status: NodeState.INACTIVE,
      x: 700,
      y: 550
    },
    {
      id: 'IA4',
      name: '投资风险评估',
      metadata: {
        description: '投资风险量化和管理',
        icon: '⚠️',
        complexity: 4,
        layer: 'investment_analysis'
      },
      status: NodeState.INACTIVE,
      x: 900,
      y: 550
    },
    
    // AI智能策略层
    {
      id: 'AI1',
      name: 'AI策略实验室',
      metadata: {
        description: 'AI策略研发平台',
        icon: '🎯',
        complexity: 5,
        layer: 'ai_strategy'
      },
      status: NodeState.INACTIVE,
      x: 100,
      y: 700
    },
    {
      id: 'AI2',
      name: 'AI实时处理',
      metadata: {
        description: 'AI实时数据处理',
        icon: '🛡️',
        complexity: 4,
        layer: 'ai_strategy'
      },
      status: NodeState.INACTIVE,
      x: 300,
      y: 700
    },
    {
      id: 'AI3',
      name: '元学习系统',
      metadata: {
        description: '元学习算法引擎',
        icon: '🤖',
        complexity: 5,
        layer: 'ai_strategy'
      },
      status: NodeState.INACTIVE,
      x: 500,
      y: 700
    },
    
    // 实盘交易层
    {
      id: 'LT1',
      name: '配置管理',
      metadata: {
        description: '交易配置管理',
        icon: '🚀',
        complexity: 2,
        layer: 'live_trading'
      },
      status: NodeState.INACTIVE,
      x: 100,
      y: 850
    },
    {
      id: 'LT2',
      name: '数据处理器',
      metadata: {
        description: '实时数据处理',
        icon: '⚡',
        complexity: 3,
        layer: 'live_trading'
      },
      status: NodeState.INACTIVE,
      x: 300,
      y: 850
    },
    {
      id: 'LT3',
      name: '实时监控',
      metadata: {
        description: '交易实时监控',
        icon: '📊',
        complexity: 2,
        layer: 'live_trading'
      },
      status: NodeState.INACTIVE,
      x: 500,
      y: 850
    },
    
    // 实验管理层
    {
      id: 'EM1',
      name: '实验管理核心',
      metadata: {
        description: '实验管理平台',
        icon: '🚀',
        complexity: 3,
        layer: 'experiment_mgmt'
      },
      status: NodeState.INACTIVE,
      x: 100,
      y: 1000
    },
    {
      id: 'EM2',
      name: '实验服务',
      metadata: {
        description: '实验执行服务',
        icon: '⚡',
        complexity: 2,
        layer: 'experiment_mgmt'
      },
      status: NodeState.INACTIVE,
      x: 300,
      y: 1000
    },
    
    // 应用服务层
    {
      id: 'WS1',
      name: '工作流引擎',
      metadata: {
        description: '工作流程定义、执行、监控',
        icon: '⚙️',
        complexity: 4,
        layer: 'application_service'
      },
      status: NodeState.INACTIVE,
      x: 100,
      y: 1150
    },
    {
      id: 'CF1',
      name: '配置管理',
      metadata: {
        description: '系统配置、参数管理、环境设置',
        icon: '🎚️',
        complexity: 3,
        layer: 'application_service'
      },
      status: NodeState.INACTIVE,
      x: 300,
      y: 1150
    },
    {
      id: 'AS1',
      name: '智能警报系统',
      metadata: {
        description: '异常检测、警报触发、通知管理',
        icon: '🔔',
        complexity: 3,
        layer: 'application_service'
      },
      status: NodeState.INACTIVE,
      x: 500,
      y: 1150
    }
  ]
}

// 计算属性
const filteredNodes = computed(() => {
  let filtered = nodes.value
  
  // 应用搜索过滤
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(node => 
      node.name.toLowerCase().includes(query) ||
      node.metadata.description.toLowerCase().includes(query) ||
      node.id.toLowerCase().includes(query)
    )
  }
  
  // 应用状态过滤
  if (statusFilter.value !== 'all') {
    filtered = filtered.filter(node => node.status === statusFilter.value)
  }
  
  // 应用层级过滤
  if (layerFilter.value !== 'all') {
    filtered = filtered.filter(node => node.metadata.layer === layerFilter.value)
  }
  
  return filtered
})

const nodeStats = computed(() => {
  const stats = {
    total: nodes.value.length,
    inactive: 0,
    active: 0,
    skipped: 0
  }
  
  for (const node of nodes.value) {
    switch (node.status) {
      case NodeState.INACTIVE:
        stats.inactive++
        break
      case NodeState.ACTIVE:
        stats.active++
        break
      case NodeState.SKIPPED:
        stats.skipped++
        break
    }
  }
  
  return stats
})

// 方法
const setViewMode = (mode: string) => {
  viewMode.value = mode
}

const onSearchInput = () => {
  // 搜索输入处理
}

const onStatusFilterChange = () => {
  // 状态过滤变化处理
}

const onLayerFilterChange = () => {
  // 层级过滤变化处理
}

const getNodeStyle = (node: any) => {
  if (viewMode.value === 'grid') {
    return {
      position: 'absolute',
      left: `${node.x}px`,
      top: `${node.y}px`
    }
  } else if (viewMode.value === 'hierarchical') {
    // 层次布局
    const layerPositions: Record<string, number> = {
      'data_hub': 100,
      'qlib_core': 250,
      'business_logic': 400,
      'investment_analysis': 550,
      'ai_strategy': 700,
      'live_trading': 850,
      'experiment_mgmt': 1000,
      'application_service': 1150
    }
    
    const layerNodes = nodes.value.filter(n => n.metadata.layer === node.metadata.layer)
    const nodeIndex = layerNodes.findIndex(n => n.id === node.id)
    
    return {
      position: 'absolute',
      left: `${100 + nodeIndex * 200}px`,
      top: `${layerPositions[node.metadata.layer] || 100}px`
    }
  }
  
  return {}
}

const selectNode = (node: any) => {
  selectedNode.value = node
}

const showNodeContextMenu = (node: any, event: MouseEvent) => {
  // 右键菜单处理
  console.log('右键点击节点:', node, event)
}

const activateNode = (nodeId: string) => {
  const node = nodes.value.find(n => n.id === nodeId)
  if (node) {
    node.status = NodeState.ACTIVE
  }
}

const skipNode = (nodeId: string) => {
  const node = nodes.value.find(n => n.id === nodeId)
  if (node) {
    node.status = NodeState.SKIPPED
  }
}

const deactivateNode = (nodeId: string) => {
  const node = nodes.value.find(n => n.id === nodeId)
  if (node) {
    node.status = NodeState.INACTIVE
  }
}

const resetAllNodes = () => {
  for (const node of nodes.value) {
    node.status = NodeState.INACTIVE
  }
  selectedNode.value = null
}

const showHelp = () => {
  showHelpModal.value = true
}

const closeHelpModal = () => {
  showHelpModal.value = false
}

const getStatusText = (status: string): string => {
  const statusTexts = {
    [NodeState.INACTIVE]: '未激活',
    [NodeState.ACTIVE]: '已激活',
    [NodeState.SKIPPED]: '跳过'
  }
  return statusTexts[status] || '未知'
}

const getLayerText = (layer: string): string => {
  const layerTexts = {
    'data_hub': '数据中枢层',
    'qlib_core': 'QLib核心层',
    'business_logic': '业务逻辑层',
    'investment_analysis': '投资分析系统',
    'ai_strategy': 'AI智能策略层',
    'live_trading': '实盘交易层',
    'experiment_mgmt': '实验管理层',
    'application_service': '应用服务层'
  }
  return layerTexts[layer] || '未知'
}

// 生命周期
onMounted(() => {
  initializeNodes()
})
</script>

<style scoped>
.intelligent-node-visualizer-simple {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: var(--bg-deep);
  color: var(--text-primary);
  font-family: var(--font-family-primary);
}

.visualizer-header {
  background: var(--bg-surface);
  padding: 1rem;
  border-bottom: 1px solid var(--border-color);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-title h2 {
  margin: 0;
  font-size: 1.5rem;
  color: var(--text-primary);
}

.header-title p {
  margin: 0.25rem 0 0 0;
  color: var(--text-secondary);
  font-size: 0.9rem;
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
  border: 1px solid var(--border-color);
  border-radius: var(--radius-sm);
  width: 200px;
  background: var(--bg-elevated);
  color: var(--text-primary);
}

.status-filter,
.layer-filter {
  padding: 0.5rem;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-sm);
  background: var(--bg-elevated);
  color: var(--text-primary);
}

.action-controls {
  display: flex;
  gap: 0.5rem;
}

.btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: var(--radius-sm);
  cursor: pointer;
  font-size: 0.875rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: var(--transition-normal);
}

.btn-primary {
  background: var(--primary-color);
  color: white;
}

.btn-secondary {
  background: #6c757d;
  color: white;
}

.btn-warning {
  background: #ffc107;
  color: #212529;
}

.btn-info {
  background: #17a2b8;
  color: white;
}

.btn-sm {
  padding: 0.25rem 0.5rem;
  font-size: 0.75rem;
}

.btn.active {
  background: var(--primary-hover);
  color: white;
}

.visualizer-content {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.nodes-container {
  flex: 1;
  background: var(--bg-deep);
  position: relative;
  overflow: auto;
}

.node-item {
  width: 180px;
  padding: 1rem;
  border: 2px solid var(--border-color);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: var(--transition-normal);
  background: var(--bg-surface);
  color: var(--text-primary);
}

.node-item:hover {
  border-color: var(--primary-color);
  box-shadow: var(--shadow-md);
}

.node-item.status-inactive {
  border-color: var(--border-light);
  background: var(--bg-elevated);
  opacity: 0.7;
}

.node-item.status-active {
  border-color: var(--success-color);
  background: rgba(16, 185, 129, 0.1);
}

.node-item.status-skipped {
  border-color: var(--warning-color);
  background: rgba(245, 158, 11, 0.1);
}

.node-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.node-icon {
  font-size: 1.5rem;
}

.node-id {
  font-weight: bold;
  color: var(--text-primary);
}

.node-title {
  font-weight: 500;
  color: var(--text-primary);
  margin-bottom: 0.25rem;
}

.node-description {
  font-size: 0.8rem;
  color: var(--text-secondary);
  margin-bottom: 0.5rem;
}

.node-status {
  text-align: center;
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

.status-badge.active {
  background: #d4edda;
  color: #155724;
}

.status-badge.skipped {
  background: #fff3cd;
  color: #856404;
}

.side-panel {
  width: 300px;
  background: var(--bg-surface);
  border-left: 1px solid var(--border-color);
  padding: 1rem;
  overflow-y: auto;
}

.panel-section {
  margin-bottom: 2rem;
}

.panel-section h3 {
  margin: 0 0 1rem 0;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid var(--border-color);
  font-size: 1.1rem;
  color: var(--text-primary);
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
  color: var(--text-secondary);
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

.stat-value.active {
  background: #d4edda;
  color: #155724;
}

.stat-value.skipped {
  background: #fff3cd;
  color: #856404;
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
  border: 1px solid var(--border-color);
}

.legend-color.inactive {
  background: #f8f9fa;
}

.legend-color.active {
  background: #d4edda;
}

.legend-color.skipped {
  background: #fff3cd;
}

.node-details {
  background: var(--bg-elevated);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-sm);
  padding: 1rem;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem 0;
  border-bottom: 1px solid var(--border-color);
}

.detail-item:last-child {
  border-bottom: none;
}

.detail-item label {
  font-weight: 500;
  color: var(--text-primary);
}

.detail-actions {
  display: flex;
  gap: 0.5rem;
  margin-top: 1rem;
}

.modal-overlay {
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
  background: var(--bg-surface);
  border-radius: var(--radius-lg);
  padding: 2rem;
  max-width: 600px;
  max-height: 80vh;
  overflow-y: auto;
  position: relative;
  color: var(--text-primary);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--border-color);
}

.modal-header h3 {
  margin: 0;
  color: var(--text-primary);
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: var(--text-secondary);
}

.help-section {
  margin-bottom: 2rem;
}

.help-section h4 {
  margin: 0 0 1rem 0;
  color: var(--text-primary);
}

.help-section ul {
  margin: 0;
  padding-left: 1.5rem;
}

.help-section li {
  margin-bottom: 0.5rem;
  line-height: 1.5;
}

.status-indicator {
  display: inline-block;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  margin-right: 0.5rem;
}

.status-indicator.inactive {
  background: #6c757d;
}

.status-indicator.active {
  background: #28a745;
}

.status-indicator.skipped {
  background: #ffc107;
}
</style>
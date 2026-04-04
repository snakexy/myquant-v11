<template>
  <div class="adaptive-function-entrance">
    <div class="entrance-header">
      <h2>智能功能入口</h2>
      <p>每个功能自动配置最优节点组合，智能优化性能</p>
      
      <div class="header-controls">
        <div class="view-toggle">
          <button 
            @click="viewMode = 'grid'" 
            :class="['btn', 'btn-sm', { active: viewMode === 'grid' }]"
          >
            <i class="icon-grid"></i>
            网格视图
          </button>
          <button 
            @click="viewMode = 'list'" 
            :class="['btn', 'btn-sm', { active: viewMode === 'list' }]"
          >
            <i class="icon-list"></i>
            列表视图
          </button>
        </div>
        
        <div class="filter-controls">
          <input 
            v-model="searchQuery" 
            type="text" 
            placeholder="搜索功能..." 
            class="search-input"
            @input="onSearchInput"
          />
          <select v-model="categoryFilter" class="category-filter" @change="onCategoryFilter">
            <option value="">所有类别</option>
            <option value="data">数据管理</option>
            <option value="ai">AI策略</option>
            <option value="backtest">策略回测</option>
            <option value="trading">实盘交易</option>
          </select>
        </div>
      </div>
    </div>

    <div class="function-grid" v-if="viewMode === 'grid'">
      <div 
        v-for="func in filteredFunctions" 
        :key="func.functionId"
        class="function-card"
        @click="enterFunction(func.functionId)"
        @mouseenter="showFunctionPreview(func)"
        @mouseleave="hideFunctionPreview"
      >
        <div class="function-header">
          <div class="function-icon">{{ func.icon }}</div>
          <div class="function-title">
            <h3>{{ func.functionName }}</h3>
            <span class="function-category">{{ getCategoryText(func.category) }}</span>
          </div>
          <div class="function-status">
            <div class="status-indicator" :class="getFunctionStatusClass(func)"></div>
          </div>
        </div>
        
        <div class="function-description">
          <p>{{ func.description }}</p>
        </div>
        
        <div class="function-metrics">
          <div class="metric-item">
            <span class="metric-label">节点状态:</span>
            <span class="metric-value">{{ func.activeNodes }}/{{ func.totalNodes }}</span>
          </div>
          <div class="metric-item">
            <span class="metric-label">性能:</span>
            <span class="metric-value" :class="getPerformanceClass(func)">
              {{ getPerformanceText(func) }}
            </span>
          </div>
          <div class="metric-item">
            <span class="metric-label">复杂度:</span>
            <div class="complexity-bar">
              <div class="complexity-fill" :style="{ width: (func.complexity / 5 * 100) + '%' }"></div>
            </div>
          </div>
        </div>
        
        <div class="function-optimizations" v-if="func.optimizationSuggestions.length > 0">
          <div class="optimization-hint">
            <i class="icon-lightbulb"></i>
            <span>{{ func.optimizationSuggestions.length }} 个优化建议</span>
          </div>
          <div class="optimization-preview">
            <div 
              v-for="suggestion in func.optimizationSuggestions.slice(0, 2)" 
              :key="suggestion.id"
              class="suggestion-item"
            >
              <span class="suggestion-type">{{ suggestion.type }}</span>
              <span class="suggestion-impact">+{{ suggestion.expectedImprovement }}%</span>
            </div>
          </div>
        </div>
        
        <div class="function-actions">
          <button @click.stop="quickActivate(func.functionId)" class="btn btn-sm btn-primary">
            快速激活
          </button>
          <button @click.stop="showFunctionDetails(func)" class="btn btn-sm btn-secondary">
            详细信息
          </button>
          <button @click.stop="optimizeFunction(func.functionId)" class="btn btn-sm btn-info">
            优化配置
          </button>
        </div>
      </div>
    </div>

    <div class="function-list" v-else>
      <div 
        v-for="func in filteredFunctions" 
        :key="func.functionId"
        class="list-item"
        @click="enterFunction(func.functionId)"
      >
        <div class="list-item-content">
          <div class="list-item-main">
            <div class="function-icon">{{ func.icon }}</div>
            <div class="function-info">
              <h3>{{ func.functionName }}</h3>
              <p>{{ func.description }}</p>
            </div>
          </div>
          
          <div class="list-item-metrics">
            <div class="metric-row">
              <span class="metric-label">节点:</span>
              <span class="metric-value">{{ func.activeNodes }}/{{ func.totalNodes }}</span>
            </div>
            <div class="metric-row">
              <span class="metric-label">性能:</span>
              <span class="metric-value" :class="getPerformanceClass(func)">
                {{ getPerformanceText(func) }}
              </span>
            </div>
            <div class="metric-row">
              <span class="metric-label">优化:</span>
              <span class="metric-value">{{ func.optimizationSuggestions.length }}</span>
            </div>
          </div>
          
          <div class="list-item-actions">
            <button @click.stop="quickActivate(func.functionId)" class="btn btn-sm btn-primary">
              激活
            </button>
            <button @click.stop="showFunctionDetails(func)" class="btn btn-sm btn-secondary">
              详情
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 功能预览弹窗 -->
    <div 
      v-if="previewFunction" 
      class="function-preview-tooltip"
      :style="{ left: previewPosition.x + 'px', top: previewPosition.y + 'px' }"
    >
      <div class="preview-content">
        <h4>{{ previewFunction.functionName }}</h4>
        <p>{{ previewFunction.description }}</p>
        <div class="preview-nodes">
          <div class="node-list">
            <div 
              v-for="nodeId in previewFunction.requiredNodes" 
              :key="nodeId"
              class="node-item"
            >
              <span class="node-icon">{{ getNodeIcon(nodeId) }}</span>
              <span class="node-name">{{ getNodeName(nodeId) }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 功能详情弹窗 -->
    <div v-if="detailFunction" class="modal-overlay" @click="closeFunctionDetails">
      <div class="modal-content function-detail-modal" @click.stop>
        <div class="modal-header">
          <h3>{{ detailFunction.functionName }} - 详细信息</h3>
          <button class="close-btn" @click="closeFunctionDetails">×</button>
        </div>
        
        <div class="modal-body">
          <div class="detail-section">
            <h4>基本信息</h4>
            <div class="detail-grid">
              <div class="detail-item">
                <label>功能ID:</label>
                <span>{{ detailFunction.functionId }}</span>
              </div>
              <div class="detail-item">
                <label>类别:</label>
                <span>{{ getCategoryText(detailFunction.category) }}</span>
              </div>
              <div class="detail-item">
                <label>复杂度:</label>
                <span>{{ detailFunction.complexity }}/5</span>
              </div>
              <div class="detail-item">
                <label>预计时长:</label>
                <span>{{ formatDuration(detailFunction.estimatedDuration) }}</span>
              </div>
            </div>
          </div>
          
          <div class="detail-section">
            <h4>节点配置</h4>
            <div class="node-configuration">
              <div class="node-group">
                <h5>必需节点 ({{ detailFunction.requiredNodes.length }})</h5>
                <div class="node-list">
                  <div 
                    v-for="nodeId in detailFunction.requiredNodes" 
                    :key="nodeId"
                    class="node-item"
                  >
                    <span class="node-icon">{{ getNodeIcon(nodeId) }}</span>
                    <span class="node-name">{{ getNodeName(nodeId) }}</span>
                    <span class="node-status" :class="getNodeStatusClass(nodeId)"></span>
                  </div>
                </div>
              </div>
              
              <div class="node-group" v-if="detailFunction.optionalNodes.length > 0">
                <h5>可选节点 ({{ detailFunction.optionalNodes.length }})</h5>
                <div class="node-list">
                  <div 
                    v-for="nodeId in detailFunction.optionalNodes" 
                    :key="nodeId"
                    class="node-item optional"
                  >
                    <span class="node-icon">{{ getNodeIcon(nodeId) }}</span>
                    <span class="node-name">{{ getNodeName(nodeId) }}</span>
                    <span class="node-status" :class="getNodeStatusClass(nodeId)"></span>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <div class="detail-section">
            <h4>性能指标</h4>
            <div class="performance-chart">
              <div class="chart-item">
                <label>效率:</label>
                <div class="progress-bar">
                  <div class="progress-fill" :style="{ width: (detailFunction.performanceMetrics.efficiency * 100) + '%' }"></div>
                </div>
                <span>{{ (detailFunction.performanceMetrics.efficiency * 100).toFixed(1) }}%</span>
              </div>
              <div class="chart-item">
                <label>可靠性:</label>
                <div class="progress-bar">
                  <div class="progress-fill" :style="{ width: (detailFunction.performanceMetrics.reliability * 100) + '%' }"></div>
                </div>
                <span>{{ (detailFunction.performanceMetrics.reliability * 100).toFixed(1) }}%</span>
              </div>
              <div class="chart-item">
                <label>成功率:</label>
                <div class="progress-bar">
                  <div class="progress-fill" :style="{ width: (detailFunction.performanceMetrics.successRate * 100) + '%' }"></div>
                </div>
                <span>{{ (detailFunction.performanceMetrics.successRate * 100).toFixed(1) }}%</span>
              </div>
            </div>
          </div>
          
          <div class="detail-section" v-if="detailFunction.optimizationSuggestions.length > 0">
            <h4>优化建议</h4>
            <div class="optimization-list">
              <div 
                v-for="suggestion in detailFunction.optimizationSuggestions" 
                :key="suggestion.id"
                class="optimization-item"
              >
                <div class="optimization-header">
                  <span class="optimization-type">{{ suggestion.type }}</span>
                  <span class="optimization-priority">优先级: {{ suggestion.priority }}</span>
                  <span class="optimization-impact">预期提升: {{ suggestion.expectedImprovement }}%</span>
                </div>
                <div class="optimization-content">
                  <p>{{ suggestion.reason }}</p>
                </div>
                <div class="optimization-actions">
                  <button @click="applyOptimization(suggestion)" class="btn btn-sm btn-primary">
                    应用优化
                  </button>
                  <button @click="ignoreOptimization(suggestion)" class="btn btn-sm btn-secondary">
                    忽略
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <div class="modal-footer">
          <button @click="enterFunction(detailFunction.functionId)" class="btn btn-primary">
            进入功能
          </button>
          <button @click="quickActivate(detailFunction.functionId)" class="btn btn-success">
            快速激活
          </button>
          <button @click="closeFunctionDetails" class="btn btn-secondary">
            关闭
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { adaptiveFunctionMapper } from '@/services/adaptive-function-mapper'
import { nodeStateManager } from '@/services/node-state-manager'
import type { FunctionNodeMapping, NodeOptimizationRecommendation } from '@/services/adaptive-function-mapper'

// 响应式数据
const viewMode = ref<'grid' | 'list'>('grid')
const searchQuery = ref('')
const categoryFilter = ref('')
const previewFunction = ref<FunctionNodeMapping | null>(null)
const detailFunction = ref<FunctionNodeMapping | null>(null)
const previewPosition = reactive({ x: 0, y: 0 })

// 功能数据
const functionMappings = ref<FunctionNodeMapping[]>([])

// 计算属性
const filteredFunctions = computed(() => {
  let functions = functionMappings.value

  // 应用搜索过滤
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    functions = functions.filter(func => 
      func.functionName.toLowerCase().includes(query) ||
      func.description.toLowerCase().includes(query)
    )
  }

  // 应用类别过滤
  if (categoryFilter.value) {
    functions = functions.filter(func => func.category === categoryFilter.value)
  }

  return functions.map(func => ({
    ...func,
    activeNodes: getActiveNodeCount(func),
    totalNodes: func.requiredNodes.length + func.optionalNodes.length,
    optimizationSuggestions: getOptimizationSuggestions(func.functionId)
  }))
})

// 方法
const initializeFunctions = () => {
  functionMappings.value = adaptiveFunctionMapper.getAllFunctionMappings()
}

const onSearchInput = () => {
  // 搜索输入处理
}

const onCategoryFilter = () => {
  // 类别过滤处理
}

const enterFunction = async (functionId: string) => {
  try {
    const result = await adaptiveFunctionMapper.establishFunctionConnections(functionId)
    
    if (result.success) {
      console.log(`功能 ${functionId} 连接建立成功`)
      // 这里可以导航到功能页面
    } else {
      console.error(`功能 ${functionId} 连接建立失败:`, result.validationErrors)
    }
  } catch (error) {
    console.error(`进入功能 ${functionId} 失败:`, error)
  }
}

const quickActivate = async (functionId: string) => {
  try {
    const result = await adaptiveFunctionMapper.establishFunctionConnections(functionId)
    
    if (result.success) {
      console.log(`功能 ${functionId} 快速激活成功`)
    }
  } catch (error) {
    console.error(`快速激活功能 ${functionId} 失败:`, error)
  }
}

const optimizeFunction = async (functionId: string) => {
  try {
    const recommendations = adaptiveFunctionMapper.recommendNodeOptimizations(functionId)
    console.log(`功能 ${functionId} 优化建议:`, recommendations)
    
    // 可以显示优化建议弹窗
  } catch (error) {
    console.error(`优化功能 ${functionId} 失败:`, error)
  }
}

const showFunctionPreview = (func: FunctionNodeMapping, event: MouseEvent) => {
  previewFunction.value = func
  previewPosition.x = event.clientX + 10
  previewPosition.y = event.clientY + 10
}

const hideFunctionPreview = () => {
  previewFunction.value = null
}

const showFunctionDetails = (func: FunctionNodeMapping) => {
  detailFunction.value = func
}

const closeFunctionDetails = () => {
  detailFunction.value = null
}

const applyOptimization = async (suggestion: NodeOptimizationRecommendation) => {
  try {
    console.log('应用优化建议:', suggestion)
    // 实现优化逻辑
  } catch (error) {
    console.error('应用优化失败:', error)
  }
}

const ignoreOptimization = (suggestion: NodeOptimizationRecommendation) => {
  console.log('忽略优化建议:', suggestion)
  // 实现忽略逻辑
}

const getActiveNodeCount = (func: FunctionNodeMapping): number => {
  return func.requiredNodes.filter(nodeId => {
    const nodeState = nodeStateManager.getNodeState(nodeId)
    return nodeState && nodeState.status === 'active'
  }).length
}

const getOptimizationSuggestions = (functionId: string): NodeOptimizationRecommendation[] => {
  try {
    return adaptiveFunctionMapper.recommendNodeOptimizations(functionId)
  } catch (error) {
    return []
  }
}

const getFunctionStatusClass = (func: any): string => {
  const ratio = func.activeNodes / func.totalNodes
  if (ratio === 1) return 'status-active'
  if (ratio > 0.5) return 'status-partial'
  return 'status-inactive'
}

const getPerformanceClass = (func: any): string => {
  const efficiency = func.performanceMetrics.efficiency
  if (efficiency > 0.8) return 'performance-good'
  if (efficiency > 0.6) return 'performance-medium'
  return 'performance-poor'
}

const getPerformanceText = (func: any): string => {
  const efficiency = func.performanceMetrics.efficiency
  if (efficiency > 0.8) return '优秀'
  if (efficiency > 0.6) return '良好'
  return '需优化'
}

const getCategoryText = (category: string): string => {
  const categoryTexts: Record<string, string> = {
    'data': '数据管理',
    'ai': 'AI策略',
    'backtest': '策略回测',
    'trading': '实盘交易'
  }
  return categoryTexts[category] || category
}

const getNodeIcon = (nodeId: string): string => {
  const nodeState = nodeStateManager.getNodeState(nodeId)
  return nodeState?.metadata.icon || '📦'
}

const getNodeName = (nodeId: string): string => {
  const nodeState = nodeStateManager.getNodeState(nodeId)
  return nodeState?.name || nodeId
}

const getNodeStatusClass = (nodeId: string): string => {
  const nodeState = nodeStateManager.getNodeState(nodeId)
  if (!nodeState) return 'status-unknown'
  return `status-${nodeState.status}`
}

const formatDuration = (milliseconds: number): string => {
  const seconds = Math.floor(milliseconds / 1000)
  const minutes = Math.floor(seconds / 60)
  const hours = Math.floor(minutes / 60)
  
  if (hours > 0) {
    return `${hours}小时${minutes % 60}分钟`
  } else if (minutes > 0) {
    return `${minutes}分钟${seconds % 60}秒`
  } else {
    return `${seconds}秒`
  }
}

// 生命周期
onMounted(() => {
  initializeFunctions()
  
  // 设置鼠标移动监听器
  document.addEventListener('mousemove', (e) => {
    if (previewFunction.value) {
      previewPosition.x = e.clientX + 10
      previewPosition.y = e.clientY + 10
    }
  })
})

onUnmounted(() => {
  document.removeEventListener('mousemove', () => {})
})
</script>

<style scoped>
.adaptive-function-entrance {
  padding: 2rem;
  background: #f8f9fa;
  min-height: 100vh;
}

.entrance-header {
  margin-bottom: 2rem;
}

.entrance-header h2 {
  margin: 0 0 0.5rem 0;
  color: #333;
  font-size: 1.8rem;
}

.entrance-header p {
  margin: 0 0 1rem 0;
  color: #666;
  font-size: 1rem;
}

.header-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
}

.view-toggle {
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

.category-filter {
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.875rem;
}

.btn-sm {
  padding: 0.25rem 0.5rem;
  font-size: 0.75rem;
}

.btn-primary {
  background: #007bff;
  color: white;
}

.btn-secondary {
  background: #6c757d;
  color: white;
}

.btn-info {
  background: #17a2b8;
  color: white;
}

.btn-success {
  background: #28a745;
  color: white;
}

.btn.active {
  background: #0056b3;
  color: white;
}

.function-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 1.5rem;
}

.function-card {
  background: white;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
}

.function-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}

.function-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
}

.function-icon {
  font-size: 2rem;
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f8f9fa;
  border-radius: 8px;
}

.function-title h3 {
  margin: 0;
  font-size: 1.2rem;
  color: #333;
}

.function-category {
  font-size: 0.8rem;
  color: #666;
  background: #e9ecef;
  padding: 0.2rem 0.5rem;
  border-radius: 12px;
}

.function-status {
  margin-left: auto;
}

.status-indicator {
  width: 12px;
  height: 12px;
  border-radius: 50%;
}

.status-active {
  background: #28a745;
}

.status-partial {
  background: #ffc107;
}

.status-inactive {
  background: #6c757d;
}

.function-description {
  margin-bottom: 1rem;
}

.function-description p {
  margin: 0;
  color: #666;
  line-height: 1.5;
}

.function-metrics {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.metric-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem;
  background: #f8f9fa;
  border-radius: 4px;
}

.metric-label {
  font-size: 0.8rem;
  color: #666;
}

.metric-value {
  font-weight: bold;
  color: #333;
}

.performance-good {
  color: #28a745;
}

.performance-medium {
  color: #ffc107;
}

.performance-poor {
  color: #dc3545;
}

.complexity-bar {
  flex: 1;
  height: 4px;
  background: #e9ecef;
  border-radius: 2px;
  overflow: hidden;
}

.complexity-fill {
  height: 100%;
  background: #007bff;
  transition: width 0.3s ease;
}

.function-optimizations {
  margin-bottom: 1rem;
}

.optimization-hint {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem;
  background: #fff3cd;
  border-radius: 4px;
  font-size: 0.8rem;
  color: #856404;
}

.optimization-preview {
  margin-top: 0.5rem;
}

.suggestion-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.25rem 0.5rem;
  background: #f8f9fa;
  border-radius: 4px;
  margin-bottom: 0.25rem;
}

.suggestion-type {
  font-size: 0.7rem;
  color: #666;
}

.suggestion-impact {
  font-size: 0.7rem;
  font-weight: bold;
  color: #28a745;
}

.function-actions {
  display: flex;
  gap: 0.5rem;
}

.function-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.list-item {
  background: white;
  border-radius: 8px;
  padding: 1rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  transition: all 0.3s ease;
}

.list-item:hover {
  transform: translateX(4px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

.list-item-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.list-item-main {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex: 1;
}

.list-item-main h3 {
  margin: 0;
  color: #333;
}

.list-item-main p {
  margin: 0.25rem 0 0 0;
  color: #666;
  font-size: 0.9rem;
}

.list-item-metrics {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.metric-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  min-width: 120px;
}

.list-item-actions {
  display: flex;
  gap: 0.5rem;
}

.function-preview-tooltip {
  position: fixed;
  background: white;
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 1rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  z-index: 1000;
  max-width: 300px;
}

.preview-content h4 {
  margin: 0 0 0.5rem 0;
  color: #333;
}

.preview-content p {
  margin: 0 0 1rem 0;
  color: #666;
  font-size: 0.9rem;
}

.preview-nodes {
  max-height: 200px;
  overflow-y: auto;
}

.node-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.node-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem;
  background: #f8f9fa;
  border-radius: 4px;
}

.node-item.optional {
  opacity: 0.7;
}

.node-icon {
  font-size: 1rem;
}

.node-name {
  flex: 1;
  font-size: 0.8rem;
  color: #333;
}

.node-status {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.status-unknown {
  background: #6c757d;
}

.status-inactive {
  background: #6c757d;
}

.status-active {
  background: #28a745;
}

.status-running {
  background: #ffc107;
}

.status-error {
  background: #dc3545;
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
  background: white;
  border-radius: 8px;
  padding: 2rem;
  max-width: 800px;
  max-height: 80vh;
  overflow-y: auto;
  position: relative;
}

.function-detail-modal {
  max-width: 900px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #eee;
}

.modal-header h3 {
  margin: 0;
  color: #333;
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

.detail-section {
  margin-bottom: 2rem;
}

.detail-section h4 {
  margin: 0 0 1rem 0;
  color: #333;
  border-bottom: 1px solid #eee;
  padding-bottom: 0.5rem;
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem;
  background: #f8f9fa;
  border-radius: 4px;
}

.detail-item label {
  font-weight: 500;
  color: #666;
}

.node-configuration {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
}

.node-group h5 {
  margin: 0 0 1rem 0;
  color: #333;
}

.performance-chart {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.chart-item {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.chart-item label {
  min-width: 80px;
  font-weight: 500;
  color: #666;
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

.optimization-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.optimization-item {
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 1rem;
}

.optimization-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.optimization-type {
  font-weight: bold;
  color: #333;
}

.optimization-priority {
  background: #007bff;
  color: white;
  padding: 0.2rem 0.5rem;
  border-radius: 12px;
  font-size: 0.8rem;
}

.optimization-impact {
  color: #28a745;
  font-weight: bold;
}

.optimization-content {
  margin-bottom: 1rem;
}

.optimization-content p {
  margin: 0;
  color: #666;
}

.optimization-actions {
  display: flex;
  gap: 0.5rem;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 2rem;
  padding-top: 1rem;
  border-top: 1px solid #eee;
}
</style>
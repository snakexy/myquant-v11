<template>
  <div class="architecture-based-entrance">
    <div class="entrance-header">
      <h2>架构驱动功能入口</h2>
      <p>基于预定义架构连接的智能节点激活系统</p>
      
      <div class="header-info">
        <div class="info-item">
          <span class="info-label">架构连接:</span>
          <span class="info-value">{{ totalConnections }} 条预定义连接</span>
        </div>
        <div class="info-item">
          <span class="info-label">功能模块:</span>
          <span class="info-value">{{ functionModules.length }} 个功能模块</span>
        </div>
        <div class="info-item">
          <span class="info-label">激活状态:</span>
          <span class="info-value">{{ activeModules.length }} 个模块运行中</span>
        </div>
      </div>
    </div>

    <div class="function-modules">
      <div 
        v-for="module in functionModules" 
        :key="module.moduleId"
        class="module-card"
        :class="{ 'module-active': isModuleActive(module.moduleId), 'module-error': hasModuleError(module.moduleId) }"
      >
        <div class="module-header">
          <div class="module-icon">{{ module.icon }}</div>
          <div class="module-info">
            <h3>{{ module.moduleName }}</h3>
            <p>{{ module.description }}</p>
          </div>
          <div class="module-status">
            <div class="status-indicator" :class="getModuleStatusClass(module.moduleId)"></div>
            <span class="status-text">{{ getModuleStatusText(module.moduleId) }}</span>
          </div>
        </div>

        <div class="module-nodes">
          <div class="nodes-section">
            <h4>节点序列 ({{ module.activationSequence.length }}个节点)</h4>
            <div class="activation-sequence">
              <div 
                v-for="(nodeId, index) in module.activationSequence" 
                :key="nodeId"
                class="sequence-item"
                :class="{ 
                  'node-active': isNodeActive(module.moduleId, nodeId),
                  'node-current': isCurrentNode(module.moduleId, nodeId),
                  'node-failed': hasNodeFailed(module.moduleId, nodeId)
                }"
              >
                <div class="sequence-number">{{ index + 1 }}</div>
                <div class="node-info">
                  <div class="node-icon">{{ getNodeIcon(nodeId) }}</div>
                  <div class="node-name">{{ getNodeName(nodeId) }}</div>
                  <div class="node-status">{{ getNodeStatusText(module.moduleId, nodeId) }}</div>
                </div>
                <div class="connection-arrow" v-if="index < module.activationSequence.length - 1">→</div>
              </div>
            </div>
          </div>

          <div class="architecture-section" v-if="module.architecturePath.length > 0">
            <h4>架构连接路径</h4>
            <div class="architecture-connections">
              <div 
                v-for="connection in module.architecturePath" 
                :key="connection.id"
                class="connection-item"
              >
                <div class="connection-from">
                  <span class="node-icon">{{ getNodeIcon(connection.fromNode) }}</span>
                  <span class="node-name">{{ getNodeName(connection.fromNode) }}</span>
                </div>
                <div class="connection-arrow">{{ getConnectionArrow(connection.connectionType) }}</div>
                <div class="connection-to">
                  <span class="node-icon">{{ getNodeIcon(connection.toNode) }}</span>
                  <span class="node-name">{{ getNodeName(connection.toNode) }}</span>
                </div>
                <div class="connection-info">
                  <span class="connection-type">{{ getConnectionTypeText(connection.connectionType) }}</span>
                  <span class="connection-strength">强度: {{ connection.strength }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="module-actions">
          <button 
            @click="activateModule(module.moduleId)" 
            class="btn btn-primary"
            :disabled="isModuleActive(module.moduleId)"
          >
            <i class="icon-play"></i>
            {{ isModuleActive(module.moduleId) ? '运行中' : '激活模块' }}
          </button>
          <button 
            @click="showModuleDetails(module)" 
            class="btn btn-secondary"
          >
            <i class="icon-info"></i>
            架构详情
          </button>
          <button 
            @click="analyzeOptimizations(module.moduleId)" 
            class="btn btn-info"
          >
            <i class="icon-lightbulb"></i>
            优化分析
          </button>
          <button 
            @click="deactivateModule(module.moduleId)" 
            class="btn btn-warning"
            :disabled="!isModuleActive(module.moduleId)"
          >
            <i class="icon-stop"></i>
            停用模块
          </button>
        </div>

        <div class="module-progress" v-if="isModuleActive(module.moduleId)">
          <div class="progress-header">
            <span>激活进度</span>
            <span class="progress-text">{{ getActivationProgress(module.moduleId) }}</span>
          </div>
          <div class="progress-bar">
            <div 
              class="progress-fill" 
              :style="{ width: getActivationProgressPercent(module.moduleId) + '%' }"
            ></div>
          </div>
        </div>
      </div>
    </div>

    <!-- 模块详情弹窗 -->
    <div v-if="detailModule" class="modal-overlay" @click="closeModuleDetails">
      <div class="modal-content architecture-detail-modal" @click.stop>
        <div class="modal-header">
          <h3>{{ detailModule.moduleName }} - 架构详情</h3>
          <button class="close-btn" @click="closeModuleDetails">×</button>
        </div>
        
        <div class="modal-body">
          <div class="detail-section">
            <h4>模块信息</h4>
            <div class="detail-grid">
              <div class="detail-item">
                <label>模块ID:</label>
                <span>{{ detailModule.moduleId }}</span>
              </div>
              <div class="detail-item">
                <label>类别:</label>
                <span>{{ getCategoryText(detailModule.category) }}</span>
              </div>
              <div class="detail-item">
                <label>复杂度:</label>
                <span>{{ detailModule.complexity }}/5</span>
              </div>
              <div class="detail-item">
                <label>预计时长:</label>
                <span>{{ formatDuration(detailModule.estimatedDuration) }}</span>
              </div>
              <div class="detail-item">
                <label>入口节点:</label>
                <span>{{ detailModule.entryPoints.join(', ') }}</span>
              </div>
              <div class="detail-item">
                <label>出口节点:</label>
                <span>{{ detailModule.exitPoints.join(', ') }}</span>
              </div>
            </div>
          </div>
          
          <div class="detail-section">
            <h4>节点依赖关系</h4>
            <div class="dependency-graph">
              <div class="graph-legend">
                <div class="legend-item">
                  <span class="legend-color entry"></span>
                  <span>入口节点</span>
                </div>
                <div class="legend-item">
                  <span class="legend-color exit"></span>
                  <span>出口节点</span>
                </div>
                <div class="legend-item">
                  <span class="legend-color optimization"></span>
                  <span>优化节点</span>
                </div>
              </div>
              <div class="dependency-nodes">
                <div 
                  v-for="nodeId in detailModule.requiredNodes" 
                  :key="nodeId"
                  class="dependency-node"
                  :class="{ 
                    'entry-node': detailModule.entryPoints.includes(nodeId),
                    'exit-node': detailModule.exitPoints.includes(nodeId)
                  }"
                >
                  <div class="node-icon">{{ getNodeIcon(nodeId) }}</div>
                  <div class="node-name">{{ getNodeName(nodeId) }}</div>
                  <div class="node-role">
                    <span v-if="detailModule.entryPoints.includes(nodeId)">入口</span>
                    <span v-else-if="detailModule.exitPoints.includes(nodeId)">出口</span>
                    <span v-else>中间</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <div class="detail-section" v-if="detailModule.optimizationNodes.length > 0">
            <h4>可选优化节点</h4>
            <div class="optimization-nodes">
              <div 
                v-for="nodeId in detailModule.optimizationNodes" 
                :key="nodeId"
                class="optimization-node"
              >
                <div class="node-icon">{{ getNodeIcon(nodeId) }}</div>
                <div class="node-name">{{ getNodeName(nodeId) }}</div>
                <div class="node-description">{{ getNodeDescription(nodeId) }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 优化建议弹窗 -->
    <div v-if="showOptimizationModal" class="modal-overlay" @click="closeOptimizationModal">
      <div class="modal-content optimization-modal" @click.stop>
        <div class="modal-header">
          <h3>优化建议 - {{ currentOptimizationModule?.moduleName }}</h3>
          <button class="close-btn" @click="closeOptimizationModal">×</button>
        </div>
        
        <div class="modal-body">
          <div class="optimization-list">
            <div 
              v-for="suggestion in optimizationSuggestions" 
              :key="suggestion.targetNode"
              class="suggestion-item"
            >
              <div class="suggestion-header">
                <div class="suggestion-type">{{ getSuggestionTypeText(suggestion.type) }}</div>
                <div class="suggestion-priority">优先级: {{ suggestion.priority }}</div>
                <div class="suggestion-impact">预期提升: {{ suggestion.expectedImprovement }}%</div>
              </div>
              <div class="suggestion-content">
                <p>{{ suggestion.reason }}</p>
                <div class="suggestion-basis">
                  <span class="basis-label">基于:</span>
                  <span class="basis-value">{{ getSuggestionBasisText(suggestion.basedOn) }}</span>
                </div>
              </div>
              <div class="suggestion-actions">
                <button @click="applySuggestion(suggestion)" class="btn btn-primary">
                  应用建议
                </button>
                <button @click="ignoreSuggestion(suggestion)" class="btn btn-secondary">
                  忽略建议
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { architectureBasedActivator } from '@/services/architecture-based-activator'
import { nodeStateManager } from '@/services/node-state-manager'
import type { 
  FunctionModule, 
  ActivationStatus, 
  OptimizationSuggestion,
  ArchitectureConnection 
} from '@/services/architecture-based-activator'

// 响应式数据
const detailModule = ref<FunctionModule | null>(null)
const showOptimizationModal = ref(false)
const currentOptimizationModule = ref<FunctionModule | null>(null)
const optimizationSuggestions = ref<OptimizationSuggestion[]>([])

// 计算属性
const functionModules = computed(() => architectureBasedActivator.getAllFunctionModules())
const totalConnections = computed(() => architectureBasedActivator.getArchitectureConnections().length)
const activeModules = computed(() => architectureBasedActivator.getAllActivationStatus().filter(status => status.status === 'active'))

// 方法
const isModuleActive = (moduleId: string): boolean => {
  const status = architectureBasedActivator.getActivationStatus(moduleId)
  return status ? status.status === 'active' : false
}

const hasModuleError = (moduleId: string): boolean => {
  const status = architectureBasedActivator.getActivationStatus(moduleId)
  return status ? status.status === 'error' : false
}

const isNodeActive = (moduleId: string, nodeId: string): boolean => {
  const status = architectureBasedActivator.getActivationStatus(moduleId)
  return status ? status.activatedNodes.includes(nodeId) : false
}

const isCurrentNode = (moduleId: string, nodeId: string): boolean => {
  const status = architectureBasedActivator.getActivationStatus(moduleId)
  if (!status) return false
  const currentIndex = status.currentStep - 1
  return currentIndex < status.activatedNodes.length && status.activatedNodes[currentIndex] === nodeId
}

const hasNodeFailed = (moduleId: string, nodeId: string): boolean => {
  const status = architectureBasedActivator.getActivationStatus(moduleId)
  return status ? status.failedNodes.includes(nodeId) : false
}

const getModuleStatusClass = (moduleId: string): string => {
  if (isModuleActive(moduleId)) return 'status-active'
  if (hasModuleError(moduleId)) return 'status-error'
  return 'status-inactive'
}

const getModuleStatusText = (moduleId: string): string => {
  if (isModuleActive(moduleId)) return '运行中'
  if (hasModuleError(moduleId)) return '错误'
  return '未激活'
}

const getActivationProgress = (moduleId: string): string => {
  const status = architectureBasedActivator.getActivationStatus(moduleId)
  if (!status) return '0/0'
  return `${status.currentStep}/${status.totalSteps}`
}

const getActivationProgressPercent = (moduleId: string): number => {
  const status = architectureBasedActivator.getActivationStatus(moduleId)
  if (!status) return 0
  return (status.currentStep / status.totalSteps) * 100
}

const getNodeIcon = (nodeId: string): string => {
  const nodeState = nodeStateManager.getNodeState(nodeId)
  return nodeState?.metadata.icon || '📦'
}

const getNodeName = (nodeId: string): string => {
  const nodeState = nodeStateManager.getNodeState(nodeId)
  return nodeState?.name || nodeId
}

const getNodeDescription = (nodeId: string): string => {
  const nodeState = nodeStateManager.getNodeState(nodeId)
  return nodeState?.metadata.description || ''
}

const getNodeStatusText = (moduleId: string, nodeId: string): string => {
  const status = architectureBasedActivator.getActivationStatus(moduleId)
  if (!status) return '未知'
  
  if (status.activatedNodes.includes(nodeId)) return '已激活'
  if (status.failedNodes.includes(nodeId)) return '激活失败'
  return '待激活'
}

const getConnectionArrow = (connectionType: string): string => {
  const arrows: Record<string, string> = {
    'data': '⇢',
    'control': '⇢',
    'dependency': '⇢'
  }
  return arrows[connectionType] || '⇢'
}

const getConnectionTypeText = (connectionType: string): string => {
  const typeTexts: Record<string, string> = {
    'data': '数据流',
    'control': '控制流',
    'dependency': '依赖关系'
  }
  return typeTexts[connectionType] || connectionType
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

const activateModule = async (moduleId: string) => {
  try {
    const status = await architectureBasedActivator.activateFunctionModule(moduleId)
    console.log(`模块 ${moduleId} 激活状态:`, status)
  } catch (error) {
    console.error(`激活模块 ${moduleId} 失败:`, error)
  }
}

const deactivateModule = async (moduleId: string) => {
  try {
    await architectureBasedActivator.deactivateFunctionModule(moduleId)
    console.log(`模块 ${moduleId} 已停用`)
  } catch (error) {
    console.error(`停用模块 ${moduleId} 失败:`, error)
  }
}

const showModuleDetails = (module: FunctionModule) => {
  detailModule.value = module
}

const closeModuleDetails = () => {
  detailModule.value = null
}

const analyzeOptimizations = async (moduleId: string) => {
  try {
    const suggestions = architectureBasedActivator.analyzeOptimizationOpportunities(moduleId)
    const module = architectureBasedActivator.getFunctionModule(moduleId)
    
    currentOptimizationModule.value = module || null
    optimizationSuggestions.value = suggestions
    showOptimizationModal.value = true
  } catch (error) {
    console.error(`分析优化机会失败:`, error)
  }
}

const closeOptimizationModal = () => {
  showOptimizationModal.value = false
  currentOptimizationModule.value = null
  optimizationSuggestions.value = []
}

const getSuggestionTypeText = (type: string): string => {
  const typeTexts: Record<string, string> = {
    'add_node': '添加节点',
    'remove_node': '移除节点',
    'modify_connection': '修改连接',
    'optimize_performance': '优化性能'
  }
  return typeTexts[type] || type
}

const getSuggestionBasisText = (basedOn: string): string => {
  const basisTexts: Record<string, string> = {
    'performance': '性能分析',
    'usage_pattern': '使用模式',
    'architecture_principle': '架构原理'
  }
  return basisTexts[basedOn] || basedOn
}

const applySuggestion = async (suggestion: OptimizationSuggestion) => {
  try {
    console.log('应用优化建议:', suggestion)
    // 实现优化建议应用逻辑
  } catch (error) {
    console.error('应用优化建议失败:', error)
  }
}

const ignoreSuggestion = (suggestion: OptimizationSuggestion) => {
  console.log('忽略优化建议:', suggestion)
  // 实现忽略逻辑
}

// 生命周期
onMounted(() => {
  // 初始化时可以设置事件监听器
  architectureBasedActivator.on('module-activation-started', (status) => {
    console.log('模块激活开始:', status)
  })
  
  architectureBasedActivator.on('module-activation-completed', (status) => {
    console.log('模块激活完成:', status)
  })
  
  architectureBasedActivator.on('connection-established', (data) => {
    console.log('架构连接建立:', data)
  })
})

onUnmounted(() => {
  // 清理事件监听器
})
</script>

<style scoped>
.architecture-based-entrance {
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

.header-info {
  display: flex;
  gap: 2rem;
  margin-bottom: 1rem;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.info-label {
  font-weight: 500;
  color: #666;
}

.info-value {
  font-weight: bold;
  color: #333;
  background: #e9ecef;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
}

.function-modules {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 2rem;
}

.module-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  border: 2px solid transparent;
}

.module-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
}

.module-active {
  border-color: #28a745;
  background: linear-gradient(135deg, #f8fff8 0%, #e8f5e8 100%);
}

.module-error {
  border-color: #dc3545;
  background: linear-gradient(135deg, #fff8f8 0%, #ffe8e8 100%);
}

.module-header {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.module-icon {
  font-size: 2.5rem;
  width: 70px;
  height: 70px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f8f9fa;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.module-info {
  flex: 1;
}

.module-info h3 {
  margin: 0 0 0.5rem 0;
  color: #333;
  font-size: 1.3rem;
}

.module-info p {
  margin: 0;
  color: #666;
  line-height: 1.5;
}

.module-status {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-left: auto;
}

.status-indicator {
  width: 12px;
  height: 12px;
  border-radius: 50%;
}

.status-active {
  background: #28a745;
  box-shadow: 0 0 8px rgba(40, 167, 69, 0.4);
}

.status-error {
  background: #dc3545;
  box-shadow: 0 0 8px rgba(220, 53, 69, 0.4);
}

.status-inactive {
  background: #6c757d;
}

.status-text {
  font-size: 0.9rem;
  font-weight: 500;
}

.module-nodes {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.nodes-section h4 {
  margin: 0 0 1rem 0;
  color: #333;
  font-size: 1.1rem;
}

.activation-sequence {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.sequence-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem;
  border-radius: 8px;
  background: #f8f9fa;
  transition: all 0.3s ease;
}

.sequence-item:hover {
  background: #e9ecef;
}

.node-active {
  background: #d4edda;
  border: 1px solid #28a745;
}

.node-current {
  background: #fff3cd;
  border: 1px solid #ffc107;
  animation: pulse 2s infinite;
}

.node-failed {
  background: #f8d7da;
  border: 1px solid #dc3545;
}

.sequence-number {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: #007bff;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.8rem;
  font-weight: bold;
}

.node-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex: 1;
}

.node-icon {
  font-size: 1.2rem;
}

.node-name {
  font-weight: 500;
  color: #333;
}

.node-status {
  font-size: 0.8rem;
  color: #666;
}

.connection-arrow {
  font-size: 1.2rem;
  color: #007bff;
  font-weight: bold;
}

.architecture-section h4 {
  margin: 0 0 1rem 0;
  color: #333;
  font-size: 1.1rem;
}

.architecture-connections {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.connection-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem;
  background: #f8f9fa;
  border-radius: 6px;
  border-left: 3px solid #007bff;
}

.connection-from,
.connection-to {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.connection-arrow {
  font-size: 1rem;
  color: #007bff;
}

.connection-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  font-size: 0.8rem;
}

.connection-type {
  background: #007bff;
  color: white;
  padding: 0.2rem 0.4rem;
  border-radius: 3px;
}

.connection-strength {
  color: #666;
}

.module-actions {
  display: flex;
  gap: 0.75rem;
  margin-top: 1rem;
}

.btn {
  padding: 0.75rem 1rem;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 500;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.btn-primary {
  background: #007bff;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #0056b3;
  transform: translateY(-1px);
}

.btn-secondary {
  background: #6c757d;
  color: white;
}

.btn-secondary:hover:not(:disabled) {
  background: #545b62;
}

.btn-info {
  background: #17a2b8;
  color: white;
}

.btn-info:hover:not(:disabled) {
  background: #138496;
}

.btn-warning {
  background: #ffc107;
  color: #212529;
}

.btn-warning:hover:not(:disabled) {
  background: #e0a800;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.module-progress {
  margin-top: 1rem;
  padding: 1rem;
  background: #e9ecef;
  border-radius: 8px;
}

.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.progress-text {
  font-weight: bold;
  color: #007bff;
}

.progress-bar {
  width: 100%;
  height: 8px;
  background: #dee2e6;
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #007bff, #0056b3);
  transition: width 0.5s ease;
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
  border-radius: 12px;
  padding: 2rem;
  max-width: 900px;
  max-height: 80vh;
  overflow-y: auto;
  position: relative;
}

.architecture-detail-modal {
  max-width: 1000px;
}

.optimization-modal {
  max-width: 700px;
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
  font-size: 1.3rem;
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
  font-size: 1.1rem;
  border-bottom: 1px solid #eee;
  padding-bottom: 0.5rem;
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem;
  background: #f8f9fa;
  border-radius: 6px;
}

.detail-item label {
  font-weight: 500;
  color: #666;
}

.dependency-graph {
  margin-top: 1rem;
}

.graph-legend {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.legend-color {
  width: 16px;
  height: 16px;
  border-radius: 3px;
}

.legend-color.entry {
  background: #28a745;
}

.legend-color.exit {
  background: #dc3545;
}

.legend-color.optimization {
  background: #ffc107;
}

.dependency-nodes {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.dependency-node {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem;
  border-radius: 8px;
  background: #f8f9fa;
  border: 2px solid #dee2e6;
}

.dependency-node.entry-node {
  border-color: #28a745;
  background: #d4edda;
}

.dependency-node.exit-node {
  border-color: #dc3545;
  background: #f8d7da;
}

.node-role {
  font-size: 0.8rem;
  padding: 0.25rem 0.5rem;
  border-radius: 12px;
  background: #007bff;
  color: white;
}

.optimization-nodes {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
  margin-top: 1rem;
}

.optimization-node {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #ffc107;
}

.node-description {
  font-size: 0.8rem;
  color: #666;
}

.optimization-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.suggestion-item {
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 1rem;
}

.suggestion-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
}

.suggestion-type {
  font-weight: bold;
  color: #333;
}

.suggestion-priority {
  background: #007bff;
  color: white;
  padding: 0.25rem 0.5rem;
  border-radius: 12px;
  font-size: 0.8rem;
}

.suggestion-impact {
  color: #28a745;
  font-weight: bold;
}

.suggestion-content {
  margin-bottom: 1rem;
}

.suggestion-content p {
  margin: 0 0 0.5rem 0;
  color: #666;
}

.suggestion-basis {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.basis-label {
  font-weight: 500;
  color: #666;
}

.basis-value {
  background: #e9ecef;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.8rem;
}

.suggestion-actions {
  display: flex;
  gap: 0.5rem;
}

@keyframes pulse {
  0% {
    box-shadow: 0 0 0 0 rgba(255, 193, 7, 0.7);
  }
  70% {
    box-shadow: 0 0 0 10px rgba(255, 193, 7, 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(255, 193, 7, 0);
  }
}
</style>
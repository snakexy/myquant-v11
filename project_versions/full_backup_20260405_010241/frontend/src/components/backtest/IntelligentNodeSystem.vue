<template>
  <div class="intelligent-node-system">
    <!-- 系统头部 -->
    <div class="system-header">
      <div class="header-left">
        <h2 class="system-title">智能节点回测系统</h2>
        <el-tag :type="getSystemStatusTagType()" size="small">
          {{ getSystemStatusText() }}
        </el-tag>
      </div>
      
      <div class="header-center">
        <el-button-group>
          <el-button 
            :type="activeTab === 'workflow' ? 'primary' : 'default'"
            @click="setActiveTab('workflow')"
            size="small"
          >
            <el-icon><Connection /></el-icon>
            工作流
          </el-button>
          <el-button 
            :type="activeTab === 'recommendation' ? 'primary' : 'default'"
            @click="setActiveTab('recommendation')"
            size="small"
          >
            <el-icon><MagicStick /></el-icon>
            智能推荐
          </el-button>
          <el-button 
            :type="activeTab === 'parameters' ? 'primary' : 'default'"
            @click="setActiveTab('parameters')"
            size="small"
          >
            <el-icon><Setting /></el-icon>
            参数配置
          </el-button>
          <el-button 
            :type="activeTab === 'templates' ? 'primary' : 'default'"
            @click="setActiveTab('templates')"
            size="small"
          >
            <el-icon><DocumentCopy /></el-icon>
            模板库
          </el-button>
        </el-button-group>
      </div>
      
      <div class="header-right">
        <el-button @click="executeWorkflow" type="primary" :loading="isExecuting">
          <el-icon><VideoPlay /></el-icon>
          执行工作流
        </el-button>
        <el-button @click="saveWorkflow" type="success">
          <el-icon><DocumentAdd /></el-icon>
          保存工作流
        </el-button>
        <el-button @click="exportWorkflow">
          <el-icon><Download /></el-icon>
          导出
        </el-button>
      </div>
    </div>

    <!-- 主内容区域 -->
    <div class="system-content">
      <!-- 工作流标签页 -->
      <div v-show="activeTab === 'workflow'" class="tab-content workflow-tab">
        <div class="workflow-toolbar">
          <div class="toolbar-left">
            <el-button @click="addNode" type="primary" size="small">
              <el-icon><Plus /></el-icon>
              添加节点
            </el-button>
            <el-button @click="addConnection" size="small">
              <el-icon><Connection /></el-icon>
              添加连接
            </el-button>
            <el-button @click="autoLayout" size="small">
              <el-icon><Grid /></el-icon>
              自动布局
            </el-button>
          </div>
          
          <div class="toolbar-center">
            <el-input
              v-model="searchQuery"
              placeholder="搜索节点..."
              prefix-icon="Search"
              clearable
              size="small"
              style="width: 200px"
              @input="handleSearch"
            />
          </div>
          
          <div class="toolbar-right">
            <el-button-group>
              <el-button 
                :type="viewMode === 'overview' ? 'primary' : 'default'"
                @click="setViewMode('overview')"
                size="small"
              >
                概览
              </el-button>
              <el-button 
                :type="viewMode === 'detail' ? 'primary' : 'default'"
                @click="setViewMode('detail')"
                size="small"
              >
                详情
              </el-button>
              <el-button 
                :type="viewMode === 'edit' ? 'primary' : 'default'"
                @click="setViewMode('edit')"
                size="small"
              >
                编辑
              </el-button>
            </el-button-group>
          </div>
        </div>
        
        <!-- 节点可视化区域 -->
        <div class="visualization-container">
          <node-visualization
            ref="nodeVisualizationRef"
            :view-mode="viewMode"
            @node-selected="handleNodeSelected"
            @connection-selected="handleConnectionSelected"
            @node-executed="handleNodeExecuted"
            @workflow-executed="handleWorkflowExecuted"
          />
        </div>
      </div>

      <!-- 智能推荐标签页 -->
      <div v-show="activeTab === 'recommendation'" class="tab-content recommendation-tab">
        <intelligent-recommendation-panel
          ref="recommendationPanelRef"
          :experience-level="experienceLevel"
          :current-workflow="currentWorkflow"
          @recommendation-applied="handleRecommendationApplied"
          @workflow-generated="handleWorkflowGenerated"
          @experience-level-changed="handleExperienceLevelChanged"
        />
      </div>

      <!-- 参数配置标签页 -->
      <div v-show="activeTab === 'parameters'" class="tab-content parameters-tab">
        <hybrid-parameter-config
          ref="parameterConfigRef"
          :mode="configMode"
          :parameters="currentParameters"
          :templates="parameterTemplates"
          @parameters-changed="handleParametersChanged"
          @template-applied="handleParameterTemplateApplied"
          @mode-changed="handleConfigModeChanged"
        />
      </div>

      <!-- 模板库标签页 -->
      <div v-show="activeTab === 'templates'" class="tab-content templates-tab">
        <div class="templates-toolbar">
          <div class="toolbar-left">
            <el-input
              v-model="templateSearchQuery"
              placeholder="搜索模板..."
              prefix-icon="Search"
              clearable
              size="small"
              style="width: 200px"
              @input="handleTemplateSearch"
            />
            <el-select v-model="templateCategoryFilter" placeholder="分类" size="small" style="width: 120px">
              <el-option label="全部" value="" />
              <el-option label="数据源" value="data_source" />
              <el-option label="策略" value="strategy" />
              <el-option label="回测" value="backtest" />
              <el-option label="分析" value="analysis" />
              <el-option label="可视化" value="visualization" />
            </el-select>
          </div>
          
          <div class="toolbar-right">
            <el-button @click="createTemplate" type="primary" size="small">
              <el-icon><Plus /></el-icon>
              创建模板
            </el-button>
          </div>
        </div>
        
        <div class="templates-grid">
          <div
            v-for="template in filteredTemplates"
            :key="template.id"
            class="template-card"
            @click="selectTemplate(template)"
          >
            <div class="template-header">
              <el-icon :size="24" :color="template.color || '#409EFF'">
                <component :is="getTemplateIcon(template.type)" />
              </el-icon>
              <h4 class="template-name">{{ template.name }}</h4>
            </div>
            <p class="template-description">{{ template.description }}</p>
            <div class="template-footer">
              <el-tag size="small" :type="getTemplateTypeTagType(template.type)">
                {{ getTemplateTypeName(template.type) }}
              </el-tag>
              <span class="template-usage">
                使用次数: {{ template.usage?.useCount || 0 }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 系统状态栏 -->
    <div class="system-statusbar">
      <div class="status-left">
        <span class="status-item">
          节点: {{ nodeCount }}
        </span>
        <span class="status-item">
          连接: {{ connectionCount }}
        </span>
        <span class="status-item">
          状态: {{ getSystemStatusText() }}
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
          最后更新: {{ lastUpdated }}
        </span>
      </div>
    </div>

    <!-- 节点配置对话框 -->
    <el-dialog
      v-model="nodeConfigDialog.visible"
      :title="`配置节点: ${nodeConfigDialog.node?.name || ''}`"
      width="800px"
      destroy-on-close
    >
      <node-config-form
        v-if="nodeConfigDialog.node"
        :node="nodeConfigDialog.node"
        :mode="viewMode"
        @config-changed="handleNodeConfigChanged"
        @config-saved="handleNodeConfigSaved"
      />
    </el-dialog>

    <!-- 工作流保存对话框 -->
    <el-dialog
      v-model="saveWorkflowDialog.visible"
      title="保存工作流"
      width="600px"
      destroy-on-close
    >
      <el-form :model="saveWorkflowDialog.form" label-width="100px">
        <el-form-item label="工作流名称" required>
          <el-input v-model="saveWorkflowDialog.form.name" placeholder="请输入工作流名称" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input
            v-model="saveWorkflowDialog.form.description"
            type="textarea"
            :rows="3"
            placeholder="请输入工作流描述"
          />
        </el-form-item>
        <el-form-item label="标签">
          <el-select
            v-model="saveWorkflowDialog.form.tags"
            multiple
            filterable
            allow-create
            placeholder="请选择或输入标签"
            style="width: 100%"
          >
            <el-option
              v-for="tag in availableTags"
              :key="tag"
              :label="tag"
              :value="tag"
            />
          </el-select>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="saveWorkflowDialog.visible = false">取消</el-button>
        <el-button type="primary" @click="confirmSaveWorkflow" :loading="saveWorkflowDialog.saving">
          保存
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Connection, MagicStick, Setting, DocumentCopy, VideoPlay, DocumentAdd, 
  Download, Plus, Grid, Search 
} from '@element-plus/icons-vue'

// 导入组件
import NodeVisualization from './NodeVisualization.vue'
import IntelligentRecommendationPanel from './IntelligentRecommendationPanel.vue'
import HybridParameterConfig from './HybridParameterConfig.vue'
import NodeConfigForm from './NodeConfigForm.vue'

// 导入类型和服务
import type { 
  Node, Connection, NodeTemplate, NodeWorkflow, NodeType, 
  ExperienceLevel, ConfigMode 
} from '@/types/node-system'
import { nodesService } from '@/services/nodes.service'
import { workflowService } from '@/services/workflow.service'
import { intelligentRecommendationService } from '@/services/intelligent-recommendation.service'
import { hybridParameterConfigService } from '@/services/hybrid-parameter-config.service'

// 响应式数据
const nodeVisualizationRef = ref()
const recommendationPanelRef = ref()
const parameterConfigRef = ref()

const activeTab = ref<'workflow' | 'recommendation' | 'parameters' | 'templates'>('workflow')
const viewMode = ref<'overview' | 'detail' | 'edit'>('overview')
const experienceLevel = ref<ExperienceLevel>('beginner')
const configMode = ref<ConfigMode>('hybrid')

const searchQuery = ref('')
const templateSearchQuery = ref('')
const templateCategoryFilter = ref('')

const selectedNodes = ref<string[]>([])
const selectedConnections = ref<string[]>([])
const isExecuting = ref(false)

const nodeConfigDialog = reactive({
  visible: false,
  node: null as Node | null
})

const saveWorkflowDialog = reactive({
  visible: false,
  saving: false,
  form: {
    name: '',
    description: '',
    tags: [] as string[]
  }
})

// 计算属性
const nodeCount = computed(() => nodesService.nodes.length)
const connectionCount = computed(() => {
  // 这里应该从连接服务获取，暂时使用计算值
  return 0
})

const currentWorkflow = computed((): NodeWorkflow => {
  return {
    id: 'current',
    name: '当前工作流',
    displayName: '当前工作流',
    description: '当前正在编辑的工作流',
    nodes: nodesService.nodes,
    connections: [], // 这里应该从连接服务获取
    metadata: {
      id: 'current',
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      version: '1.0.0',
      tags: []
    },
    permissions: {
      canView: true,
      canEdit: true,
      canExecute: true,
      canDelete: true,
      canShare: true
    }
  }
})

const currentParameters = computed(() => {
  return hybridParameterConfigService.getParameters()
})

const parameterTemplates = computed(() => {
  return hybridParameterConfigService.getTemplates()
})

const filteredTemplates = computed(() => {
  let templates = workflowService.templates
  
  if (templateSearchQuery.value) {
    const query = templateSearchQuery.value.toLowerCase()
    templates = templates.filter(template => 
      template.name.toLowerCase().includes(query) ||
      template.description.toLowerCase().includes(query)
    )
  }
  
  if (templateCategoryFilter.value) {
    templates = templates.filter(template => 
      template.type === templateCategoryFilter.value
    )
  }
  
  return templates
})

const availableTags = computed(() => {
  return ['回测', '策略', '数据分析', '机器学习', '风险管理', '高频交易']
})

const lastUpdated = computed(() => {
  return new Date().toLocaleString('zh-CN')
})

// 方法
const setActiveTab = (tab: typeof activeTab.value) => {
  activeTab.value = tab
}

const setViewMode = (mode: typeof viewMode.value) => {
  viewMode.value = mode
  if (nodeVisualizationRef.value) {
    nodeVisualizationRef.value.setViewMode(mode)
  }
}

const getSystemStatusTagType = () => {
  if (isExecuting.value) return 'warning'
  return 'success'
}

const getSystemStatusText = () => {
  if (isExecuting.value) return '执行中'
  return '就绪'
}

const addNode = () => {
  // 实现添加节点逻辑
  ElMessage.info('添加节点功能开发中...')
}

const addConnection = () => {
  // 实现添加连接逻辑
  ElMessage.info('添加连接功能开发中...')
}

const autoLayout = () => {
  // 实现自动布局逻辑
  ElMessage.info('自动布局功能开发中...')
}

const handleSearch = (query: string) => {
  // 实现搜索逻辑
  console.log('搜索:', query)
}

const handleTemplateSearch = (query: string) => {
  // 模板搜索已在计算属性中处理
  console.log('模板搜索:', query)
}

const executeWorkflow = async () => {
  if (isExecuting.value) {
    ElMessage.warning('工作流正在执行中...')
    return
  }
  
  try {
    isExecuting.value = true
    ElMessage.info('开始执行工作流...')
    
    // 这里应该调用工作流执行服务
    await new Promise(resolve => setTimeout(resolve, 2000)) // 模拟执行
    
    ElMessage.success('工作流执行完成')
  } catch (error) {
    ElMessage.error('工作流执行失败')
    console.error('工作流执行错误:', error)
  } finally {
    isExecuting.value = false
  }
}

const saveWorkflow = () => {
  saveWorkflowDialog.visible = true
  saveWorkflowDialog.form.name = currentWorkflow.value.name
  saveWorkflowDialog.form.description = currentWorkflow.value.description
  saveWorkflowDialog.form.tags = currentWorkflow.value.metadata.tags
}

const exportWorkflow = () => {
  // 实现导出工作流逻辑
  ElMessage.info('导出工作流功能开发中...')
}

const createTemplate = () => {
  // 实现创建模板逻辑
  ElMessage.info('创建模板功能开发中...')
}

const selectTemplate = (template: NodeTemplate) => {
  // 实现选择模板逻辑
  ElMessage.info(`选择模板: ${template.name}`)
}

const getTemplateIcon = (type: NodeType) => {
  // 返回对应的图标组件
  switch (type) {
    case NodeType.DATA_SOURCE:
      return Connection
    case NodeType.STRATEGY:
      return MagicStick
    case NodeType.BACKTEST:
      return VideoPlay
    case NodeType.ANALYSIS:
      return Setting
    default:
      return DocumentCopy
  }
}

const getTemplateTypeTagType = (type: NodeType) => {
  switch (type) {
    case NodeType.DATA_SOURCE:
      return 'primary'
    case NodeType.STRATEGY:
      return 'success'
    case NodeType.BACKTEST:
      return 'warning'
    case NodeType.ANALYSIS:
      return 'info'
    default:
      return 'default'
  }
}

const getTemplateTypeName = (type: NodeType): string => {
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

const confirmSaveWorkflow = async () => {
  if (!saveWorkflowDialog.form.name.trim()) {
    ElMessage.warning('请输入工作流名称')
    return
  }
  
  try {
    saveWorkflowDialog.saving = true
    
    // 这里应该调用工作流保存服务
    await new Promise(resolve => setTimeout(resolve, 1000)) // 模拟保存
    
    ElMessage.success('工作流保存成功')
    saveWorkflowDialog.visible = false
  } catch (error) {
    ElMessage.error('工作流保存失败')
    console.error('工作流保存错误:', error)
  } finally {
    saveWorkflowDialog.saving = false
  }
}

// 事件处理方法
const handleNodeSelected = (nodes: Node[]) => {
  selectedNodes.value = nodes.map(node => node.id)
}

const handleConnectionSelected = (connections: Connection[]) => {
  selectedConnections.value = connections.map(conn => conn.id)
}

const handleNodeExecuted = (nodeId: string) => {
  ElMessage.info(`节点 ${nodeId} 执行完成`)
}

const handleWorkflowExecuted = (result: any) => {
  ElMessage.success('工作流执行完成')
  console.log('工作流执行结果:', result)
}

const handleRecommendationApplied = (recommendation: any) => {
  ElMessage.success('智能推荐已应用')
  setActiveTab('workflow')
}

const handleWorkflowGenerated = (workflow: NodeWorkflow) => {
  ElMessage.success('工作流已生成')
  setActiveTab('workflow')
}

const handleExperienceLevelChanged = (level: ExperienceLevel) => {
  experienceLevel.value = level
}

const handleParametersChanged = (parameters: any[]) => {
  console.log('参数已更改:', parameters)
}

const handleParameterTemplateApplied = (templateId: string) => {
  ElMessage.success('参数模板已应用')
}

const handleConfigModeChanged = (mode: ConfigMode) => {
  configMode.value = mode
}

const handleNodeConfigChanged = (config: any) => {
  console.log('节点配置已更改:', config)
}

const handleNodeConfigSaved = (node: Node) => {
  ElMessage.success('节点配置已保存')
  nodeConfigDialog.visible = false
}

// 监听器
watch(activeTab, (newTab) => {
  nextTick(() => {
    // 根据当前标签页初始化相应的组件
    if (newTab === 'recommendation' && recommendationPanelRef.value) {
      recommendationPanelRef.value.refreshRecommendations()
    } else if (newTab === 'parameters' && parameterConfigRef.value) {
      parameterConfigRef.value.refreshParameters()
    }
  })
})

// 生命周期
onMounted(() => {
  // 初始化系统
  console.log('智能节点系统已启动')
})

onUnmounted(() => {
  // 清理资源
  console.log('智能节点系统已关闭')
})
</script>

<style scoped>
.intelligent-node-system {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: #f5f5f5;
}

.system-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 24px;
  background: white;
  border-bottom: 1px solid #e0e0e0;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.system-title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #262626;
}

.header-center {
  display: flex;
  align-items: center;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

.system-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.tab-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 16px;
}

.workflow-tab {
  padding: 0;
}

.workflow-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: white;
  border-bottom: 1px solid #e0e0e0;
}

.toolbar-left,
.toolbar-center,
.toolbar-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

.visualization-container {
  flex: 1;
  position: relative;
  overflow: hidden;
}

.recommendation-tab,
.parameters-tab,
.templates-tab {
  padding: 16px;
  background: white;
  margin: 16px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.templates-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.templates-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
  overflow-y: auto;
}

.template-card {
  padding: 16px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  background: white;
}

.template-card:hover {
  border-color: #1890ff;
  box-shadow: 0 4px 12px rgba(24, 144, 255, 0.15);
  transform: translateY(-2px);
}

.template-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.template-name {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #262626;
}

.template-description {
  margin: 0 0 12px 0;
  color: #8c8c8c;
  font-size: 14px;
  line-height: 1.4;
  flex: 1;
}

.template-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.template-usage {
  font-size: 12px;
  color: #8c8c8c;
}

.system-statusbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 24px;
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
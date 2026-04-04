<template>
  <div class="workflow-page">
    <!-- 顶部导航 -->
    <header class="page-header">
      <div class="header-left">
        <h1>{{ isZh ? '工作流管理' : 'Workflow Management' }}</h1>
        <span class="subtitle">{{ isZh ? '单次执行流水线 + 批量任务管理' : 'Single Pipeline + Batch Task Management' }}</span>
      </div>
      <div class="header-right">
        <button class="btn-icon" @click="toggleLanguage">
          {{ isZh ? 'EN' : '中文' }}
        </button>
        <button class="btn-primary" @click="showCreateModal = true">
          <span>+</span> {{ isZh ? '新建工作流' : 'New Workflow' }}
        </button>
      </div>
    </header>

    <!-- 标签页切换 -->
    <div class="tabs-container">
      <button
        :class="['tab', { active: activeTab === 'workflow' }]"
        @click="activeTab = 'workflow'"
      >
        🔬 {{ isZh ? '单次流水线' : 'Single Pipeline' }}
      </button>
      <button
        :class="['tab', { active: activeTab === 'task' }]"
        @click="activeTab = 'task'"
      >
        📦 {{ isZh ? '批量任务' : 'Batch Tasks' }}
      </button>
      <button
        :class="['tab', { active: activeTab === 'templates' }]"
        @click="activeTab = 'templates'"
      >
        📋 {{ isZh ? '模板库' : 'Templates' }}
      </button>
    </div>

    <!-- 单次流水线内容 -->
    <div v-if="activeTab === 'workflow'" class="tab-content">
      <div class="content-header">
        <h2>{{ isZh ? '工作流列表' : 'Workflow List' }}</h2>
        <div class="filters">
          <select v-model="workflowFilter.status" class="filter-select">
            <option value="all">{{ isZh ? '全部状态' : 'All Status' }}</option>
            <option value="pending">{{ isZh ? '等待中' : 'Pending' }}</option>
            <option value="running">{{ isZh ? '运行中' : 'Running' }}</option>
            <option value="completed">{{ isZh ? '已完成' : 'Completed' }}</option>
            <option value="failed">{{ isZh ? '失败' : 'Failed' }}</option>
          </select>
        </div>
      </div>

      <!-- 工作流列表 -->
      <div v-if="isLoadingWorkflows" class="loading">
        <div class="spinner"></div>
        <p>{{ isZh ? '加载中...' : 'Loading...' }}</p>
      </div>

      <div v-else class="workflow-grid">
        <div
          v-for="workflow in filteredWorkflows"
          :key="workflow.id"
          class="workflow-card"
          @click="selectWorkflow(workflow)"
        >
          <div class="card-header">
            <span class="workflow-name">{{ workflow.name }}</span>
            <span :class="['status-badge', workflow.status]">
              {{ getStatusText(workflow.status) }}
            </span>
          </div>
          <p class="workflow-desc">{{ workflow.description }}</p>
          <div class="card-meta">
            <span>📊 {{ workflow.type }}</span>
            <span>🕐 {{ formatTime(workflow.metadata?.createdAt) }}</span>
          </div>
          <div class="progress-bar" v-if="workflow.status === 'running'">
            <div class="progress-fill" :style="{ width: `${workflow.execution?.progress || 0}%` }"></div>
          </div>
          <div class="card-actions">
            <button
              v-if="workflow.status === 'pending'"
              class="btn-action start"
              @click.stop="startWorkflow(workflow.id)"
            >
              ▶ {{ isZh ? '启动' : 'Start' }}
            </button>
            <button
              v-if="workflow.status === 'running'"
              class="btn-action pause"
              @click.stop="pauseWorkflow(workflow.id)"
            >
              ⏸ {{ isZh ? '暂停' : 'Pause' }}
            </button>
            <button
              v-if="workflow.status === 'paused'"
              class="btn-action resume"
              @click.stop="resumeWorkflow(workflow.id)"
            >
              ▶ {{ isZh ? '恢复' : 'Resume' }}
            </button>
            <button class="btn-action delete" @click.stop="deleteWorkflow(workflow.id)">
              🗑 {{ isZh ? '删除' : 'Delete' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 批量任务内容 -->
    <div v-if="activeTab === 'task'" class="tab-content">
      <div class="content-header">
        <h2>{{ isZh ? '任务池管理' : 'Task Pool Management' }}</h2>
        <button class="btn-secondary" @click="showCreatePoolModal = true">
          + {{ isZh ? '新建任务池' : 'New Pool' }}
        </button>
      </div>

      <!-- 任务池列表 -->
      <div class="pool-list">
        <div v-if="isLoadingPools" class="loading">
          <div class="spinner"></div>
        </div>

        <div
          v-for="pool in taskPools"
          :key="pool.name"
          class="pool-card"
        >
          <div class="pool-header">
            <h3>{{ pool.name }}</h3>
            <span class="pool-desc">{{ pool.description }}</span>
          </div>

          <!-- 任务统计 -->
          <div class="pool-stats" v-if="poolStats[pool.name]">
            <div class="stat-item">
              <span class="stat-value">{{ poolStats[pool.name].total }}</span>
              <span class="stat-label">{{ isZh ? '总任务' : 'Total' }}</span>
            </div>
            <div class="stat-item waiting">
              <span class="stat-value">{{ poolStats[pool.name].waiting }}</span>
              <span class="stat-label">{{ isZh ? '等待' : 'Waiting' }}</span>
            </div>
            <div class="stat-item running">
              <span class="stat-value">{{ poolStats[pool.name].running }}</span>
              <span class="stat-label">{{ isZh ? '运行' : 'Running' }}</span>
            </div>
            <div class="stat-item done">
              <span class="stat-value">{{ poolStats[pool.name].done }}</span>
              <span class="stat-label">{{ isZh ? '完成' : 'Done' }}</span>
            </div>
          </div>

          <!-- 任务生成器 -->
          <div class="task-generator">
            <h4>{{ isZh ? '任务生成' : 'Task Generation' }}</h4>
            <div class="gen-options">
              <select v-model="pool.genType" class="gen-select">
                <option value="rolling">{{ isZh ? '滚动任务' : 'Rolling' }}</option>
                <option value="multi_loss">{{ isZh ? '多损失函数' : 'Multi Loss' }}</option>
                <option value="optuna">{{ isZh ? '超参搜索' : 'Optuna Search' }}</option>
              </select>
              <button class="btn-generate" @click="generateTasks(pool.name, pool.genType)">
                🔧 {{ isZh ? '生成任务' : 'Generate' }}
              </button>
            </div>
          </div>

          <!-- 操作按钮 -->
          <div class="pool-actions">
            <button
              class="btn-action start"
              @click="startTraining(pool.name)"
              :disabled="!poolStats[pool.name]?.waiting"
            >
              ▶ {{ isZh ? '启动训练' : 'Start' }}
            </button>
            <button class="btn-action" @click="viewResults(pool.name)">
              📊 {{ isZh ? '查看结果' : 'Results' }}
            </button>
            <button class="btn-action" @click="resetPool(pool.name)">
              🔄 {{ isZh ? '重置' : 'Reset' }}
            </button>
            <button class="btn-action delete" @click="deletePool(pool.name)">
              🗑
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 模板库内容 -->
    <div v-if="activeTab === 'templates'" class="tab-content">
      <div class="content-header">
        <h2>{{ isZh ? '工作流模板' : 'Workflow Templates' }}</h2>
      </div>

      <div class="templates-grid">
        <div
          v-for="template in templates"
          :key="template.id"
          class="template-card"
        >
          <div class="template-icon">
            {{ getTemplateIcon(template.type || template.genType) }}
          </div>
          <h3>{{ template.name }}</h3>
          <p>{{ template.description }}</p>
          <div class="template-meta">
            <span class="complexity" :class="template.complexity">
              {{ isZh ? getComplexityText(template.complexity) : template.complexity }}
            </span>
            <span class="rating">⭐ {{ template.rating }}</span>
          </div>
          <button class="btn-use" @click="useTemplate(template)">
            {{ isZh ? '使用模板' : 'Use Template' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 创建工作流弹窗 -->
    <div v-if="showCreateModal" class="modal-overlay" @click="showCreateModal = false">
      <div class="modal-content" @click.stop>
        <h2>{{ isZh ? '新建工作流' : 'Create Workflow' }}</h2>
        <div class="form-group">
          <label>{{ isZh ? '名称' : 'Name' }}</label>
          <input v-model="newWorkflow.name" type="text" :placeholder="isZh ? '输入工作流名称' : 'Enter workflow name'">
        </div>
        <div class="form-group">
          <label>{{ isZh ? '描述' : 'Description' }}</label>
          <textarea v-model="newWorkflow.description" :placeholder="isZh ? '描述工作流用途' : 'Describe the workflow'"></textarea>
        </div>
        <div class="form-group">
          <label>{{ isZh ? '类型' : 'Type' }}</label>
          <select v-model="newWorkflow.type">
            <option value="backtest">{{ isZh ? '回测分析' : 'Backtest' }}</option>
            <option value="model_training">{{ isZh ? '模型训练' : 'Model Training' }}</option>
            <option value="factor_analysis">{{ isZh ? '因子分析' : 'Factor Analysis' }}</option>
            <option value="optimization">{{ isZh ? '策略优化' : 'Optimization' }}</option>
          </select>
        </div>
        <div class="modal-actions">
          <button class="btn-secondary" @click="showCreateModal = false">{{ isZh ? '取消' : 'Cancel' }}</button>
          <button class="btn-primary" @click="createWorkflow">{{ isZh ? '创建' : 'Create' }}</button>
        </div>
      </div>
    </div>

    <!-- 创建任务池弹窗 -->
    <div v-if="showCreatePoolModal" class="modal-overlay" @click="showCreatePoolModal = false">
      <div class="modal-content" @click.stop>
        <h2>{{ isZh ? '新建任务池' : 'Create Task Pool' }}</h2>
        <div class="form-group">
          <label>{{ isZh ? '名称' : 'Name' }}</label>
          <input v-model="newPool.name" type="text" :placeholder="isZh ? '输入任务池名称' : 'Enter pool name'">
        </div>
        <div class="form-group">
          <label>{{ isZh ? '描述' : 'Description' }}</label>
          <textarea v-model="newPool.description" :placeholder="isZh ? '描述任务池用途' : 'Describe the pool'"></textarea>
        </div>
        <div class="modal-actions">
          <button class="btn-secondary" @click="showCreatePoolModal = false">{{ isZh ? '取消' : 'Cancel' }}</button>
          <button class="btn-primary" @click="createPool">{{ isZh ? '创建' : 'Create' }}</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { workflowApi, WorkflowStatus, WorkflowType } from '@/api/modules/workflow'
import { taskApi, type TaskPool, type TaskPoolStats, type TaskTemplate } from '@/api/modules/task'
import { useAppStore } from '@/stores/core/AppStore'

const appStore = useAppStore()

// 语言切换
const isZh = computed(() => appStore.language === 'zh')
const toggleLanguage = () => {
  appStore.setLanguage(isZh.value ? 'en' : 'zh')
}

// 标签页
const activeTab = ref('workflow')

// ==================== Workflow 单次流水线 ====================

interface Workflow {
  id: string
  name: string
  description: string
  type: string
  status: string
  metadata?: { createdAt?: string }
  execution?: { progress?: number }
}

const workflows = ref<Workflow[]>([])
const isLoadingWorkflows = ref(false)
const workflowFilter = ref({ status: 'all' })

const filteredWorkflows = computed(() => {
  if (workflowFilter.value.status === 'all') {
    return workflows.value
  }
  return workflows.value.filter(w => w.status === workflowFilter.value.status)
})

const loadWorkflows = async () => {
  isLoadingWorkflows.value = true
  try {
    const response = await workflowApi.getWorkflows()
    if (response.code === 200) {
      workflows.value = response.data.workflows
    }
  } catch (error) {
    console.error('Failed to load workflows:', error)
    // 使用模拟数据
    workflows.value = [
      { id: 'wf-001', name: 'Alpha158回测', description: '使用Alpha158因子进行沪深300回测', type: 'backtest', status: 'completed', metadata: { createdAt: '2026-02-13T10:00:00' } },
      { id: 'wf-002', name: 'LightGBM训练', description: '训练LightGBM预测模型', type: 'model_training', status: 'running', execution: { progress: 67 }, metadata: { createdAt: '2026-02-13T09:00:00' } },
      { id: 'wf-003', name: '因子相关性分析', description: '分析因子间的相关性矩阵', type: 'factor_analysis', status: 'pending', metadata: { createdAt: '2026-02-13T08:00:00' } }
    ]
  } finally {
    isLoadingWorkflows.value = false
  }
}

const startWorkflow = async (id: string) => {
  try {
    await workflowApi.executeWorkflow(id)
    await loadWorkflows()
  } catch (error) {
    console.error('Failed to start workflow:', error)
  }
}

const pauseWorkflow = async (id: string) => {
  try {
    await workflowApi.pauseWorkflow(id)
    await loadWorkflows()
  } catch (error) {
    console.error('Failed to pause workflow:', error)
  }
}

const resumeWorkflow = async (id: string) => {
  try {
    await workflowApi.resumeWorkflow(id)
    await loadWorkflows()
  } catch (error) {
    console.error('Failed to resume workflow:', error)
  }
}

const deleteWorkflow = async (id: string) => {
  if (confirm(isZh.value ? '确定要删除吗？' : 'Are you sure?')) {
    try {
      await workflowApi.deleteWorkflow(id)
      await loadWorkflows()
    } catch (error) {
      console.error('Failed to delete workflow:', error)
    }
  }
}

const selectWorkflow = (workflow: Workflow) => {
  console.log('Selected workflow:', workflow)
}

// ==================== Task 批量任务 ====================

const taskPools = ref<TaskPool[]>([])
const poolStats = ref<Record<string, TaskPoolStats>>({})
const isLoadingPools = ref(false)

const loadTaskPools = async () => {
  isLoadingPools.value = true
  try {
    const response = await taskApi.getPools()
    if (response.code === 200) {
      taskPools.value = response.data
      // 加载每个池的统计
      for (const pool of response.data) {
        loadPoolStats(pool.name)
      }
    }
  } catch (error) {
    console.error('Failed to load task pools:', error)
    // 使用模拟数据
    taskPools.value = [
      { name: 'rolling_exp', description: '滚动训练实验', created_at: '2026-02-13', total_tasks: 12, completed_tasks: 8 },
      { name: 'multi_model', description: '多模型对比', created_at: '2026-02-12', total_tasks: 6, completed_tasks: 3 }
    ]
    poolStats.value = {
      'rolling_exp': { total: 12, waiting: 2, running: 2, done: 8, failed: 0, part_done: 0 },
      'multi_model': { total: 6, waiting: 2, running: 1, done: 3, failed: 0, part_done: 0 }
    }
  } finally {
    isLoadingPools.value = false
  }
}

const loadPoolStats = async (poolName: string) => {
  try {
    const response = await taskApi.getPoolStats(poolName)
    if (response.code === 200) {
      poolStats.value[poolName] = response.data
    }
  } catch (error) {
    console.error('Failed to load pool stats:', error)
  }
}

const generateTasks = async (poolName: string, genType: string) => {
  try {
    await taskApi.generateTasks(poolName, {
      taskTemplate: { model: {}, dataset: {}, record: [] },
      genType: genType as any,
      rollSteps: [['2015-01-01', '2016-01-01'], ['2016-01-01', '2017-01-01']],
      losses: ['mse', 'mae'],
      nTrials: 10
    })
    await loadPoolStats(poolName)
  } catch (error) {
    console.error('Failed to generate tasks:', error)
  }
}

const startTraining = async (poolName: string) => {
  try {
    await taskApi.startTraining(poolName)
    await loadPoolStats(poolName)
  } catch (error) {
    console.error('Failed to start training:', error)
  }
}

const viewResults = async (poolName: string) => {
  try {
    const response = await taskApi.getResults(poolName)
    console.log('Results:', response.data)
  } catch (error) {
    console.error('Failed to get results:', error)
  }
}

const resetPool = async (poolName: string) => {
  try {
    await taskApi.resetPool(poolName)
    await loadPoolStats(poolName)
  } catch (error) {
    console.error('Failed to reset pool:', error)
  }
}

const deletePool = async (poolName: string) => {
  if (confirm(isZh.value ? '确定要删除任务池吗？' : 'Delete this pool?')) {
    try {
      await taskApi.deletePool(poolName)
      await loadTaskPools()
    } catch (error) {
      console.error('Failed to delete pool:', error)
    }
  }
}

// ==================== 模板 ====================

const templates = ref<TaskTemplate[]>([])

const loadTemplates = async () => {
  try {
    const [wfTemplates, taskTemplates] = await Promise.all([
      workflowApi.getWorkflowTemplates(),
      taskApi.getTemplates()
    ])
    templates.value = [
      ...(wfTemplates.data || []),
      ...(taskTemplates.data || [])
    ]
  } catch (error) {
    console.error('Failed to load templates:', error)
    templates.value = [
      { id: 'tpl-001', name: 'LightGBM滚动训练', description: '使用LightGBM进行滚动训练', genType: 'rolling' },
      { id: 'tpl-002', name: '多损失函数对比', description: '对比不同损失函数的效果', genType: 'multi_loss' },
      { id: 'tpl-003', name: '超参数搜索', description: '使用Optuna搜索最优参数', genType: 'optuna' }
    ]
  }
}

const useTemplate = (template: TaskTemplate) => {
  console.log('Using template:', template)
  showCreateModal.value = true
}

// ==================== 创建弹窗 ====================

const showCreateModal = ref(false)
const showCreatePoolModal = ref(false)

const newWorkflow = ref({
  name: '',
  description: '',
  type: 'backtest'
})

const newPool = ref({
  name: '',
  description: ''
})

const createWorkflow = async () => {
  try {
    await workflowApi.createWorkflow(newWorkflow.value)
    showCreateModal.value = false
    newWorkflow.value = { name: '', description: '', type: 'backtest' }
    await loadWorkflows()
  } catch (error) {
    console.error('Failed to create workflow:', error)
  }
}

const createPool = async () => {
  try {
    await taskApi.createPool(newPool.value)
    showCreatePoolModal.value = false
    newPool.value = { name: '', description: '' }
    await loadTaskPools()
  } catch (error) {
    console.error('Failed to create pool:', error)
  }
}

// ==================== 工具函数 ====================

const getStatusText = (status: string) => {
  const texts: Record<string, { zh: string; en: string }> = {
    pending: { zh: '等待中', en: 'Pending' },
    running: { zh: '运行中', en: 'Running' },
    completed: { zh: '已完成', en: 'Completed' },
    failed: { zh: '失败', en: 'Failed' },
    paused: { zh: '已暂停', en: 'Paused' }
  }
  return isZh.value ? texts[status]?.zh : texts[status]?.en
}

const formatTime = (time?: string) => {
  if (!time) return '-'
  const date = new Date(time)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))
  if (days === 0) return isZh.value ? '今天' : 'Today'
  if (days === 1) return isZh.value ? '昨天' : 'Yesterday'
  return isZh.value ? `${days}天前` : `${days} days ago`
}

const getTemplateIcon = (type?: string) => {
  const icons: Record<string, string> = {
    rolling: '🔄',
    multi_loss: '📊',
    optuna: '🎯',
    backtest: '📈',
    model_training: '🤖',
    factor_analysis: '🔬'
  }
  return icons[type || ''] || '📋'
}

const getComplexityText = (complexity?: string) => {
  const texts: Record<string, string> = {
    low: '简单',
    medium: '中等',
    high: '复杂'
  }
  return texts[complexity || ''] || complexity
}

// 初始化
onMounted(() => {
  loadWorkflows()
  loadTaskPools()
  loadTemplates()
})
</script>

<style scoped>
/* TradingView 风格配色 */
.workflow-page {
  --bg-primary: #131722;
  --bg-secondary: #1e222d;
  --bg-tertiary: #2a2e39;
  --text-primary: #d1d4dc;
  --text-secondary: #787b86;
  --accent-blue: #2962ff;
  --accent-green: #26a69a;
  --accent-red: #ef5350;
  --accent-orange: #ff9800;
  --border-color: #363a45;

  min-height: 100vh;
  background: var(--bg-primary);
  color: var(--text-primary);
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

/* 头部 */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border-color);
}

.header-left h1 {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
}

.subtitle {
  color: var(--text-secondary);
  font-size: 14px;
}

.header-right {
  display: flex;
  gap: 12px;
}

/* 按钮 */
.btn-primary {
  background: var(--accent-blue);
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
}

.btn-secondary {
  background: var(--bg-tertiary);
  color: var(--text-primary);
  border: 1px solid var(--border-color);
  padding: 10px 20px;
  border-radius: 6px;
  cursor: pointer;
}

.btn-icon {
  background: transparent;
  color: var(--text-secondary);
  border: 1px solid var(--border-color);
  padding: 8px 12px;
  border-radius: 6px;
  cursor: pointer;
}

/* 标签页 */
.tabs-container {
  display: flex;
  gap: 8px;
  padding: 16px 24px;
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border-color);
}

.tab {
  background: transparent;
  color: var(--text-secondary);
  border: 1px solid var(--border-color);
  padding: 10px 20px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.tab.active {
  background: var(--accent-blue);
  color: white;
  border-color: var(--accent-blue);
}

.tab:hover:not(.active) {
  background: var(--bg-tertiary);
}

/* 内容区域 */
.tab-content {
  padding: 24px;
}

.content-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.content-header h2 {
  margin: 0;
  font-size: 18px;
}

/* 过滤器 */
.filters {
  display: flex;
  gap: 12px;
}

.filter-select {
  background: var(--bg-tertiary);
  color: var(--text-primary);
  border: 1px solid var(--border-color);
  padding: 8px 12px;
  border-radius: 6px;
}

/* 加载状态 */
.loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 60px;
  color: var(--text-secondary);
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid var(--bg-tertiary);
  border-top-color: var(--accent-blue);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* 工作流网格 */
.workflow-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 16px;
}

.workflow-card {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 16px;
  cursor: pointer;
  transition: all 0.2s;
}

.workflow-card:hover {
  border-color: var(--accent-blue);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.workflow-name {
  font-weight: 600;
  font-size: 16px;
}

.status-badge {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.status-badge.pending { background: #3d3d00; color: #ffeb3b; }
.status-badge.running { background: #0d3d0d; color: #4caf50; }
.status-badge.completed { background: #0d2d3d; color: #29b6f6; }
.status-badge.failed { background: #3d0d0d; color: #ef5350; }
.status-badge.paused { background: #3d2d0d; color: #ff9800; }

.workflow-desc {
  color: var(--text-secondary);
  font-size: 14px;
  margin: 0 0 12px;
}

.card-meta {
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: var(--text-secondary);
  margin-bottom: 12px;
}

.progress-bar {
  height: 4px;
  background: var(--bg-tertiary);
  border-radius: 2px;
  margin-bottom: 12px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--accent-blue), var(--accent-green));
  transition: width 0.3s;
}

.card-actions {
  display: flex;
  gap: 8px;
}

.btn-action {
  background: var(--bg-tertiary);
  color: var(--text-primary);
  border: none;
  padding: 6px 12px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
}

.btn-action.start { color: var(--accent-green); }
.btn-action.pause { color: var(--accent-orange); }
.btn-action.resume { color: var(--accent-blue); }
.btn-action.delete { color: var(--accent-red); }

.btn-action:hover {
  background: var(--border-color);
}

/* 任务池列表 */
.pool-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 16px;
}

.pool-card {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 20px;
}

.pool-header {
  margin-bottom: 16px;
}

.pool-header h3 {
  margin: 0 0 4px;
  font-size: 18px;
}

.pool-desc {
  color: var(--text-secondary);
  font-size: 14px;
}

.pool-stats {
  display: flex;
  gap: 20px;
  margin-bottom: 16px;
  padding: 12px;
  background: var(--bg-primary);
  border-radius: 6px;
}

.stat-item {
  text-align: center;
}

.stat-value {
  display: block;
  font-size: 24px;
  font-weight: 600;
}

.stat-label {
  font-size: 12px;
  color: var(--text-secondary);
}

.stat-item.waiting .stat-value { color: #ffeb3b; }
.stat-item.running .stat-value { color: var(--accent-green); }
.stat-item.done .stat-value { color: var(--accent-blue); }

.task-generator {
  margin-bottom: 16px;
  padding: 12px;
  background: var(--bg-tertiary);
  border-radius: 6px;
}

.task-generator h4 {
  margin: 0 0 12px;
  font-size: 14px;
}

.gen-options {
  display: flex;
  gap: 12px;
}

.gen-select {
  flex: 1;
  background: var(--bg-primary);
  color: var(--text-primary);
  border: 1px solid var(--border-color);
  padding: 8px 12px;
  border-radius: 4px;
}

.btn-generate {
  background: var(--accent-blue);
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
}

.pool-actions {
  display: flex;
  gap: 8px;
}

/* 模板网格 */
.templates-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
}

.template-card {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 20px;
  text-align: center;
}

.template-icon {
  font-size: 48px;
  margin-bottom: 12px;
}

.template-card h3 {
  margin: 0 0 8px;
  font-size: 16px;
}

.template-card p {
  color: var(--text-secondary);
  font-size: 14px;
  margin: 0 0 12px;
}

.template-meta {
  display: flex;
  justify-content: center;
  gap: 12px;
  margin-bottom: 12px;
  font-size: 12px;
}

.complexity {
  padding: 2px 8px;
  border-radius: 4px;
}

.complexity.low { background: #0d3d0d; color: #4caf50; }
.complexity.medium { background: #3d2d0d; color: #ff9800; }
.complexity.high { background: #3d0d0d; color: #ef5350; }

.btn-use {
  width: 100%;
  background: var(--accent-blue);
  color: white;
  border: none;
  padding: 10px;
  border-radius: 6px;
  cursor: pointer;
}

/* 弹窗 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 24px;
  width: 400px;
  max-width: 90%;
}

.modal-content h2 {
  margin: 0 0 20px;
  font-size: 20px;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-size: 14px;
  color: var(--text-secondary);
}

.form-group input,
.form-group textarea,
.form-group select {
  width: 100%;
  background: var(--bg-tertiary);
  color: var(--text-primary);
  border: 1px solid var(--border-color);
  padding: 10px 12px;
  border-radius: 6px;
  font-size: 14px;
}

.form-group textarea {
  min-height: 80px;
  resize: vertical;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 20px;
}
</style>

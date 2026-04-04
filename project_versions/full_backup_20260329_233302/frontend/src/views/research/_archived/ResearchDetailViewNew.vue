<template>
  <div class="research-detail-view">
    <!-- 顶部导航 -->
    <header class="navbar">
      <!-- 返回按钮 - 放在最左边 -->
      <button class="back-btn" @click="goBack" :title="isZh ? '返回工作流' : 'Back to Workflow'">
        <svg class="icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M19 12H5M12 19l-7-7 7-7"/>
        </svg>
        {{ isZh ? '返回' : 'Back' }}
      </button>

      <div class="logo">
        <div class="logo-icon">M</div>
        <span>MyQuant</span>
      </div>

      <!-- 阶段相关导航菜单 -->
      <nav class="stage-nav">
        <button :class="['stage-btn', { active: currentStageModule === 'research' }]" @click="switchStageModule('research')">
          <svg class="icon-nav" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="11" cy="11" r="8"/>
            <path d="M21 21l-4.35-4.35"/>
          </svg>
          {{ isZh ? '研究分析' : 'Research' }}
        </button>
        <button :class="['stage-btn', { active: currentStageModule === 'backtest' }]" @click="switchStageModule('backtest')">
          <svg class="icon-nav" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
            <circle cx="12" cy="12" r="3"/>
          </svg>
          {{ isZh ? '回测' : 'Backtest' }}
        </button>
        <button :class="['stage-btn', { active: currentStageModule === 'signal' }]" @click="switchStageModule('signal')">
          <svg class="icon-nav" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M22 12h-4l-3 9L9 3l-3 9H2"/>
          </svg>
          {{ isZh ? '信号生成' : 'Signal' }}
        </button>
      </nav>

      <!-- 用户菜单 -->
      <div class="user-menu">
        <button class="icon-btn" @click="toggleLanguage" :title="isZh ? '切换语言' : 'Toggle Language'">
          {{ isZh ? '🇨🇳' : '🇺🇸' }}
        </button>
        <button class="icon-btn" @click="showNotifications" :title="isZh ? '通知' : 'Notifications'">
          🔔
        </button>
        <div class="user-avatar" @click="showUserMenu">U</div>
      </div>
    </header>

    <!-- 主容器 -->
    <div class="main-container">
      <!-- 左侧：工作流步骤 -->
      <aside class="panel workflow-panel">
        <div class="panel-header">
          <span class="panel-title">
            <svg class="icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="9 11 12 14 22 4"/>
              <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/>
            </svg>
            {{ isZh ? '工作流步骤' : 'Workflow Steps' }}
          </span>
        </div>
        <div class="workflow-list">
          <div
            v-for="step in workflowSteps"
            :key="step.id"
            :class="['workflow-step', step.status, { selected: currentStep === step.id }]"
            @click="selectStep(step.id)"
          >
            <div class="step-icon">
              <!-- 完成：打勾图标 -->
              <svg v-if="step.status === 'completed'" class="icon-check" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
                <polyline points="20 6 9 17 4 12"/>
              </svg>
              <!-- 进行中/待处理：数字或图标 -->
              <template v-else>
                <svg v-if="step.id === 1" class="icon-step" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <ellipse cx="12" cy="5" rx="9" ry="3"/>
                  <path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/>
                  <path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/>
                </svg>
                <svg v-else-if="step.id === 2" class="icon-step" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <rect x="4" y="4" width="16" height="16" rx="2"/>
                  <path d="M9 9h6M9 13h6M9 17h4"/>
                </svg>
                <svg v-else-if="step.id === 3" class="icon-step" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M21 21H3V3"/>
                  <path d="M21 9l-6 6-4-4-6 6"/>
                </svg>
                <svg v-else-if="step.id === 4" class="icon-step" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
                </svg>
                <svg v-else-if="step.id === 5" class="icon-step" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M12 2L2 7l10 5 10-5-10-5z"/>
                  <path d="M2 17l10 5 10-5"/>
                  <path d="M2 12l10 5 10-5"/>
                </svg>
                <svg v-else class="icon-step" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
                  <polyline points="22 4 12 14.01 9 11.01"/>
                </svg>
              </template>
            </div>
            <div class="step-content">
              <div class="step-title">{{ isZh ? step.nameZh : step.name }}</div>
              <div class="step-desc">{{ isZh ? step.descriptionZh : step.description }}</div>
            </div>
          </div>
        </div>
      </aside>

      <!-- 中间：内容区域 -->
      <main class="content-panel">
        <!-- 任务配置信息栏 -->
        <div class="task-config-info">
          <div class="config-item">
            <span class="config-label">{{ isZh ? '任务ID' : 'Task ID' }}</span>
            <span class="config-value">{{ taskId }}</span>
          </div>
          <div class="config-item">
            <span class="config-label">{{ isZh ? '股票池' : 'Stock Pool' }}</span>
            <span class="config-value">{{ currentTask?.stockPoolZh || currentTask?.stockPool }}</span>
          </div>
          <div class="config-item">
            <span class="config-label">{{ isZh ? '日期范围' : 'Date Range' }}</span>
            <span class="config-value">{{ currentTask?.dateStart }} ~ {{ currentTask?.dateEnd }}</span>
          </div>
          <div class="config-item">
            <span class="config-label">{{ isZh ? '进度' : 'Progress' }}</span>
            <span class="config-value">{{ currentTask?.progress || 0 }}%</span>
          </div>
        </div>

        <!-- 步骤组件内容 -->
        <div class="step-content-wrapper">
          <!-- 步骤1：数据配置 -->
          <ResearchStep1DataConfig
            v-if="currentStep === 1"
            :task-id="taskId"
            :is-zh="isZh"
            :current-step="currentStep"
            @data-update="handleDataUpdate"
            @step-complete="handleStepComplete"
          />

          <!-- 步骤2：因子计算 -->
          <ResearchStep2FactorCalculation
            v-else-if="currentStep === 2"
            :task-id="taskId"
            :is-zh="isZh"
          />

          <!-- 步骤3：因子分析 -->
          <ResearchStep3FactorAnalysis
            v-else-if="currentStep === 3"
            :task-id="taskId"
            :is-zh="isZh"
          />

          <!-- 步骤4：因子评估 -->
          <ResearchStep4FactorEvaluation
            v-else-if="currentStep === 4"
            :task-id="taskId"
            :is-zh="isZh"
          />

          <!-- 步骤5：模型训练 -->
          <ResearchStep5ModelTraining
            v-else-if="currentStep === 5"
            :task-id="taskId"
            :is-zh="isZh"
          />

          <!-- 步骤6：可行性检查 -->
          <ResearchStep6FeasibilityCheck
            v-else-if="currentStep === 6"
            :task-id="taskId"
            :is-zh="isZh"
          />
        </div>
      </main>

      <!-- 右侧：因子库 -->
      <aside class="panel factor-panel">
        <div class="panel-header">
          <span class="panel-title">
            <svg class="icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
            </svg>
            {{ isZh ? '因子库' : 'Factor Library' }}
          </span>
          <div class="panel-actions">
            <button class="icon-btn" @click="addCustomFactor" :title="isZh ? '添加自定义因子' : 'Add Custom Factor'">
              <svg class="icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="12" y1="5" x2="12" y2="19"/>
                <line x1="5" y1="12" x2="19" y2="12"/>
              </svg>
            </button>
            <button class="icon-btn" @click="openFactorSettings" :title="isZh ? '设置' : 'Settings'">
              <svg class="icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="3"/>
                <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/>
              </svg>
            </button>
          </div>
        </div>
        <div class="factor-list">
          <div
            v-for="factor in factorLibrary"
            :key="factor.name"
            :class="['factor-item', { selected: selectedFactor === factor.name }]"
            @click="selectFactor(factor)"
          >
            <div class="factor-header">
              <div class="factor-name">
                <span class="factor-status-dot" :class="getFactorStatus(factor.ic ?? undefined)"></span>
                {{ factor.name }}
              </div>
              <div class="factor-score" :class="getFactorScoreClass(factor.ic ?? undefined)">
                <svg class="icon-xs" viewBox="0 0 24 24" fill="currentColor">
                  <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
                </svg>
                {{ factor.ic?.toFixed(2) ?? 'N/A' }}
              </div>
            </div>
            <div class="factor-type">
              <span class="type-tag">{{ factor.category || 'alpha158' }}</span>
              <span class="type-separator">•</span>
              {{ isZh ? (factor.typeZh || factor.type) : factor.type }}
            </div>
            <div class="factor-metrics">
              <span class="metric">
                <svg class="icon-xs" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M23 18l-9.5-9.5-5 5L1 6"/>
                </svg>
                IC: <span :class="['metric-value', { positive: (factor.ic ?? 0) > 0.03, negative: (factor.ic ?? 0) < 0 }]">{{ factor.ic?.toFixed(3) ?? 'N/A' }}</span>
              </span>
              <span class="metric">
                <svg class="icon-xs" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M12 2L2 7l10 5 10-5-10-5z"/>
                  <path d="M2 17l10 5 10-5"/>
                  <path d="M2 12l10 5 10-5"/>
                </svg>
                IR: <span :class="['metric-value', { positive: (factor.ir ?? 0) > 0.5, negative: (factor.ir ?? 0) < 0 }]">{{ factor.ir?.toFixed(2) ?? 'N/A' }}</span>
              </span>
            </div>
          </div>
        </div>
      </aside>
    </div>
  </div>
</template>

<script setup lang="ts">
// ============================================================================
// Imports
// ============================================================================
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { factorApi, type FactorInfo } from '@/api/modules/research'

// 导入步骤组件
import ResearchStep1DataConfig from './components/ResearchStep1DataConfig.vue'
import ResearchStep2FactorCalculation from './components/ResearchStep2FactorCalculation.vue'
import ResearchStep3FactorAnalysis from './components/ResearchStep3FactorAnalysis.vue'
import ResearchStep4FactorEvaluation from './components/ResearchStep4FactorEvaluation.vue'
import ResearchStep5ModelTraining from './components/ResearchStep5ModelTraining.vue'
import ResearchStep6FeasibilityCheck from './components/ResearchStep6FeasibilityCheck.vue'

// ============================================================================
// 路由和状态
// ============================================================================
const router = useRouter()
const route = useRoute()

// 任务ID - 从URL获取
const taskId = computed(() => route.query.taskId as string || 'default')

// 语言设置
const isZh = ref(true)

// 当前阶段模块
const currentStageModule = ref('research')

// 当前步骤
const currentStep = ref(1)

// ============================================================================
// 任务配置数据
// ============================================================================
interface TaskConfig {
  id: string
  title: string
  titleZh: string
  stockPool: string
  stockPoolZh: string
  dateStart: string
  dateEnd: string
  periods?: string[]
  period?: string
  factors: string
  factorsZh: string
  model?: string
  icMethod: string
  icThreshold: number
  progress: number
}

// 模拟任务数据存储
const taskStore = reactive<Record<string, TaskConfig>>({
  'RES-2024-001': {
    id: 'RES-2024-001',
    title: 'Alpha158 Factor Analysis',
    titleZh: 'Alpha158因子分析',
    stockPool: 'CSI300',
    stockPoolZh: '沪深300',
    dateStart: '2021-01-01',
    dateEnd: '2024-12-31',
    periods: ['1d'],
    factors: 'Alpha158',
    factorsZh: 'Alpha158因子集',
    icMethod: 'spearman',
    icThreshold: 0.03,
    progress: 67
  },
  'default': {
    id: 'default',
    title: 'New Research Task',
    titleZh: '新建研究任务',
    stockPool: 'CSI300',
    stockPoolZh: '沪深300',
    dateStart: '2023-01-01',
    dateEnd: '2024-12-31',
    periods: ['1d'],
    factors: 'Alpha158',
    factorsZh: 'Alpha158因子集',
    icMethod: 'spearman',
    icThreshold: 0.03,
    progress: 0
  }
})

// 当前任务配置
const currentTask = computed(() => taskStore[taskId.value] || taskStore['default'])

// ============================================================================
// 工作流步骤
// ============================================================================
interface WorkflowStep {
  id: number
  name: string
  nameZh: string
  description: string
  descriptionZh: string
  status: 'pending' | 'active' | 'completed'
}

const workflowSteps = ref<WorkflowStep[]>([
  { id: 1, name: 'Data Configuration', nameZh: '数据配置', status: 'active', description: 'Configure data sources and date range', descriptionZh: '配置数据源和日期范围' },
  { id: 2, name: 'Factor Calculation', nameZh: '因子计算', status: 'pending', description: 'Calculate factor values for selected stocks', descriptionZh: '计算选定股票的因子值' },
  { id: 3, name: 'Factor Analysis', nameZh: '因子分析', status: 'pending', description: 'Analyze factor performance using IC/IR metrics', descriptionZh: '使用IC/IR指标分析因子表现' },
  { id: 4, name: 'Factor Evaluation', nameZh: '因子评估', status: 'pending', description: 'Evaluate factor effectiveness', descriptionZh: '评估因子有效性' },
  { id: 5, name: 'Model Training', nameZh: '模型训练', status: 'pending', description: 'Train ML models with selected factors', descriptionZh: '使用选定因子训练ML模型' },
  { id: 6, name: 'Feasibility Check', nameZh: '可行性检查', status: 'pending', description: 'Check model feasibility for validation', descriptionZh: '检查模型是否可用于验证' }
])

// ============================================================================
// 因子库数据
// ============================================================================
const factorLibrary = ref<FactorInfo[]>([])
const selectedFactor = ref<string | null>(null)

// 加载因子库数据
const loadFactorLibrary = async () => {
  try {
    const factors = await factorApi.getFactorList()
    factorLibrary.value = factors.data || []
  } catch (error) {
    console.error('Failed to load factor library:', error)
    // 使用模拟数据
    factorLibrary.value = [
      { name: 'MA_Cross_60', type: 'momentum', typeZh: '动量', ic: 0.045, ir: 0.78 },
      { name: 'RSI_14', type: 'momentum', typeZh: '动量', ic: 0.038, ir: 0.65 },
      { name: 'Volatility_20', type: 'volatility', typeZh: '波动率', ic: 0.028, ir: 0.52 },
      { name: 'Volume_Ratio_5', type: 'volume', typeZh: '成交量', ic: 0.032, ir: 0.58 }
    ] as FactorInfo[]
  }
}

// ============================================================================
// 事件处理
// ============================================================================
const selectStep = (stepId: number) => {
  currentStep.value = stepId
}

const switchStageModule = (module: string) => {
  currentStageModule.value = module
  ElMessage.info(isZh.value ? `切换到${module === 'research' ? '研究分析' : module === 'backtest' ? '回测' : '信号生成'}模块` : `Switched to ${module} module`)
}

const goBack = () => {
  router.push('/research')
}

const toggleLanguage = () => {
  isZh.value = !isZh.value
  ElMessage.success(isZh.value ? '已切换到中文' : 'Switched to English')
}

const showNotifications = () => {
  ElMessage.info(isZh.value ? '暂无新通知' : 'No new notifications')
}

const showUserMenu = () => {
  ElMessage.info(isZh.value ? '用户菜单' : 'User menu')
}

const selectFactor = (factor: FactorInfo) => {
  selectedFactor.value = factor.name
  console.log('Selected factor:', factor)
}

const addCustomFactor = () => {
  ElMessage.info(isZh.value ? '添加自定义因子功能开发中' : 'Add custom factor feature coming soon')
}

const openFactorSettings = () => {
  ElMessage.info(isZh.value ? '因子设置功能开发中' : 'Factor settings feature coming soon')
}

// 步骤组件事件处理
const handleDataUpdate = (data: any) => {
  console.log('Data updated:', data)
  // 更新任务配置
  if (data.stockPool) {
    const task = taskStore[taskId.value] || taskStore['default']
    if (task) {
      task.stockPool = data.stockPool
      const poolNames: Record<string, string> = {
        'CSI300': '沪深300',
        'CSI500': '中证500',
        'CSI1000': '中证1000',
        'All A-shares': '全市场'
      }
      task.stockPoolZh = poolNames[data.stockPool] || data.stockPool
    }
  }
  if (data.dateRange) {
    const task = taskStore[taskId.value] || taskStore['default']
    if (task) {
      task.dateStart = data.dateRange[0]
      task.dateEnd = data.dateRange[1]
    }
  }
}

const handleStepComplete = (data: any) => {
  console.log('Step completed:', data)
  // 标记当前步骤为完成
  const currentStepObj = workflowSteps.value.find(s => s.id === currentStep.value)
  if (currentStepObj) {
    currentStepObj.status = 'completed'
  }

  // 激活下一步
  const nextStep = workflowSteps.value.find(s => s.id === currentStep.value + 1)
  if (nextStep) {
    nextStep.status = 'active'
    currentStep.value = nextStep.id
    ElMessage.success(isZh.value ? `已完成${currentStepObj?.nameZh || currentStepObj?.name}` : `Completed ${currentStepObj?.name}`)
  }
}

// 因子状态辅助函数
const getFactorStatus = (ic: number | undefined): string => {
  if (ic === undefined) return 'unknown'
  if (ic >= 0.05) return 'excellent'
  if (ic >= 0.03) return 'good'
  if (ic >= 0) return 'average'
  return 'poor'
}

const getFactorStatusText = (ic: number | undefined): string => {
  if (ic === undefined) return isZh.value ? '未知' : 'Unknown'
  if (ic >= 0.05) return isZh.value ? '优秀' : 'Excellent'
  if (ic >= 0.03) return isZh.value ? '良好' : 'Good'
  if (ic >= 0.01) return isZh.value ? '一般' : 'Fair'
  return isZh.value ? '较差' : 'Poor'
}

const getFactorScoreClass = (ic: number | undefined): string => {
  return getFactorStatus(ic)
}

// ============================================================================
// 生命周期
// ============================================================================
onMounted(() => {
  loadFactorLibrary()
})
</script>

<style scoped lang="scss">
// ============================================================================
// 全局样式
// ============================================================================
.research-detail-view {
  // CSS变量定义
  --bg-primary: #131722;
  --bg-secondary: #1e222d;
  --bg-tertiary: #2a2e39;
  --bg-hover: #2a2e39;
  --text-primary: #d1d4dc;
  --text-secondary: #787b86;
  --accent-blue: #2962ff;
  --accent-orange: #ff9800;
  --accent-red: #ef5350;
  --accent-green: #26a69a;
  --border-color: #2a2e39;
  --primary-color: #2962ff;
  --primary-color-light: rgba(41, 98, 255, 0.1);

  width: 100vw;
  height: 100vh;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  flex-direction: column;
  background: #131722;
  color: #d1d4dc;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
  overflow: hidden;
  z-index: 1;
}

// ============================================================================
// 顶部导航栏
// ============================================================================
.navbar {
  height: 56px;
  display: flex;
  align-items: center;
  padding: 0 20px;
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border-color);
  gap: 20px;
}

.back-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  border: none;
  background: transparent;
  color: var(--text-secondary);
  cursor: pointer;
  border-radius: 8px;
  transition: all 0.2s;

  &:hover {
    background: var(--bg-hover);
    color: var(--text-primary);
  }
}

.logo {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 16px;
  font-weight: 700;
  color: var(--text-primary);
}

.logo-icon {
  width: 32px;
  height: 32px;
  background: linear-gradient(135deg, var(--accent-blue), var(--accent-orange));
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 700;
}

.stage-nav {
  display: flex;
  gap: 4px;
  flex: 1;
  margin-left: 16px;
}

.stage-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border: none;
  background: transparent;
  color: var(--text-secondary);
  cursor: pointer;
  border-bottom: 2px solid transparent;
  border-radius: 0;
  font-size: 13px;
  font-weight: 500;
  transition: all 0.15s;
  white-space: nowrap;

  &:hover {
    background: transparent;
    color: var(--text-primary);
  }

  &.active {
    background: transparent;
    color: var(--accent-blue);
    border-bottom-color: var(--accent-blue);
  }
}

.icon-nav {
  width: 14px;
  height: 14px;
  flex-shrink: 0;
}

.user-menu {
  display: flex;
  align-items: center;
  gap: 8px;
}

.user-menu {
  display: flex;
  align-items: center;
  gap: 12px;
}

.icon-btn {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  background: transparent;
  color: var(--text-secondary);
  cursor: pointer;
  border-radius: 8px;
  transition: all 0.2s;

  &:hover {
    background: var(--bg-hover);
    color: var(--text-primary);
  }
}

.user-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 600;
  cursor: pointer;
}

// ============================================================================
// 主容器
// ============================================================================
.main-container {
  flex: 1;
  display: grid;
  grid-template-columns: 280px 1fr 320px;
  grid-template-rows: 1fr;
  height: calc(100vh - 56px);
  gap: 1px;
  background: var(--border-color);
  overflow: hidden;
}

// ============================================================================
// 面板通用样式
// ============================================================================
.panel {
  background: var(--bg-primary);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.panel-header {
  background: var(--bg-secondary);
  padding: 12px 16px;
  font-size: 12px;
  font-weight: 600;
  color: var(--text-primary);
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid var(--border-color);
}

.panel-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: var(--text-primary);
  font-size: 12px;
}

.panel-actions {
  display: flex;
  gap: 8px;
}

.icon-sm {
  width: 16px;
  height: 16px;
}

// ============================================================================
// 工作流面板
// ============================================================================
.workflow-panel {
  .workflow-list {
    flex: 1;
    overflow-y: auto;
    padding: 12px;
  }

  .workflow-step {
    display: flex;
    align-items: flex-start;
    gap: 12px;
    padding: 12px;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.2s;
    margin-bottom: 8px;

    &:hover {
      background: var(--bg-hover);
    }

    &.selected {
      background: var(--primary-color-light);
      border: 1px solid var(--primary-color);
    }

    &.completed .step-icon {
      color: #10b981;
    }
  }

  .step-icon {
    width: 24px;
    height: 24px;
    flex-shrink: 0;
  }

  .icon-check {
    width: 100%;
    height: 100%;
    color: #10b981;
  }

  .icon-step {
    width: 100%;
    height: 100%;
    color: var(--text-secondary);
  }

  .step-content {
    flex: 1;
  }

  .step-title {
    font-weight: 500;
    color: var(--text-primary);
    margin-bottom: 4px;
  }

  .step-desc {
    font-size: 12px;
    color: var(--text-secondary);
  }
}

// ============================================================================
// 内容面板
// ============================================================================
.content-panel {
  overflow-y: auto;
  padding: 0;
  background: transparent;
  border: none;
}

.task-config-info {
  display: flex;
  gap: 24px;
  padding: 16px;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.config-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.config-label {
  font-size: 12px;
  color: var(--text-secondary);
  font-weight: 500;
}

.config-value {
  font-size: 14px;
  color: var(--text-primary);
  font-weight: 600;
}

.step-content-wrapper {
  padding: 20px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  min-height: 400px;
}

// ============================================================================
// 因子库面板
// ============================================================================
.factor-panel {
  .factor-list {
    flex: 1;
    overflow-y: auto;
  }

  .factor-item {
    padding: 12px 16px;
    border-bottom: 1px solid var(--border-color);
    cursor: pointer;
    transition: background 0.15s;

    &:hover {
      background: var(--bg-tertiary);
    }

    &.selected {
      background: var(--bg-tertiary);
    }
  }

  .factor-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;
  }

  .factor-name {
    font-size: 13px;
    font-weight: 600;
    color: var(--text-primary);
    display: flex;
    align-items: center;
    gap: 6px;
  }

  .factor-status-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    display: inline-block;

    &.excellent {
      background: var(--accent-red);
      box-shadow: 0 0 6px rgba(239, 83, 80, 0.6);
    }

    &.good {
      background: var(--accent-blue);
    }

    &.average {
      background: var(--accent-orange);
    }

    &.poor, &.unknown {
      background: var(--text-secondary);
    }
  }

  .factor-score {
    font-size: 12px;
    font-weight: 600;
    display: flex;
    align-items: center;
    gap: 4px;
    padding: 2px 8px;
    border-radius: 4px;

    &.excellent {
      background: rgba(239, 83, 80, 0.15);
      color: var(--accent-red);
    }

    &.good {
      background: rgba(41, 98, 255, 0.15);
      color: var(--accent-blue);
    }

    &.average {
      background: rgba(255, 152, 0, 0.15);
      color: var(--accent-orange);
    }

    &.poor, &.unknown {
      background: rgba(120, 123, 134, 0.15);
      color: var(--text-secondary);
    }
  }

  .icon-xs {
    width: 12px;
    height: 12px;
  }

  .factor-type {
    font-size: 11px;
    color: var(--text-secondary);
    margin-bottom: 8px;
    display: flex;
    align-items: center;
    gap: 6px;
  }

  .type-tag {
    background: var(--bg-tertiary);
    padding: 2px 6px;
    border-radius: 3px;
    font-size: 10px;
  }

  .type-separator {
    color: var(--border-color);
  }

  .factor-metrics {
    display: flex;
    gap: 12px;
    font-size: 11px;
  }

  .metric {
    color: var(--text-secondary);
    display: flex;
    align-items: center;
    gap: 4px;
  }

  .metric-value {
    font-weight: 600;
    color: var(--text-primary);

    &.positive {
      color: var(--color-up);  /* 红色 - 正面 */
    }

    &.negative {
      color: var(--color-down);  /* 绿色 - 负面 */
    }
  }
}

// ============================================================================
// 滚动条样式
// ============================================================================
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

::-webkit-scrollbar-track {
  background: transparent;
}

::-webkit-scrollbar-thumb {
  background: var(--border-color);
  border-radius: 3px;

  &:hover {
    background: var(--text-secondary);
  }
}
</style>

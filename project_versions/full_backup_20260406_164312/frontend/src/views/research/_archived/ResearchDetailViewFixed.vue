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
                <svg v-else-if="step.id === 6" class="icon-step" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
                  <polyline points="22 4 12 14.01 9 11.01"/>
                </svg>
                <span v-else class="step-number">{{ step.id }}</span>
              </template>
            </div>
            <div class="step-info">
              <div class="step-title">{{ isZh ? step.nameZh : step.name }}</div>
              <div :class="['step-status', step.status]">
                <span class="status-dot"></span>
                {{ getStepStatusText(step.status) }}
              </div>
            </div>
          </div>
        </div>
      </aside>

      <!-- 中间：主内容区 -->
      <main class="panel content-panel">
        <div class="content-area">
          <!-- 任务标题和ID -->
          <div class="task-header-info">
            <h1 class="page-title">{{ taskTitle }}</h1>
            <span class="task-id-badge">#{{ taskId }}</span>
          </div>
          <p class="page-subtitle">{{ isZh ? currentStepData?.descriptionZh : currentStepData?.description }}</p>

          <!-- 步骤组件内容 -->
          <ResearchStep1DataConfig
            v-if="currentStep === 1"
            :task-id="taskId"
            :is-zh="isZh"
            :current-step="currentStep"
            @data-update="handleDataUpdate"
            @step-complete="handleStepComplete"
          />

          <ResearchStep2FactorCalculation
            v-else-if="currentStep === 2"
            :task-id="taskId"
            :is-zh="isZh"
          />

          <ResearchStep3FactorAnalysis
            v-else-if="currentStep === 3"
            :task-id="taskId"
            :is-zh="isZh"
          />

          <ResearchStep4FactorEvaluation
            v-else-if="currentStep === 4"
            :task-id="taskId"
            :is-zh="isZh"
          />

          <ResearchStep5ModelTraining
            v-else-if="currentStep === 5"
            :task-id="taskId"
            :is-zh="isZh"
          />

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
import { ref, reactive, computed, onMounted } from 'vue'
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

// 任务标题
const taskTitle = ref('Alpha158 Factor Analysis')

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

// 当前步骤数据
const currentStepData = computed(() => {
  return workflowSteps.value.find(s => s.id === currentStep.value)
})

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

// 步骤状态文本
const getStepStatusText = (status: string): string => {
  if (status === 'completed') return isZh.value ? '已完成' : 'Completed'
  if (status === 'active') return isZh.value ? '进行中' : 'In Progress'
  return isZh.value ? '待处理' : 'Pending'
}

// 因子状态辅助函数
const getFactorStatus = (ic: number | undefined): string => {
  if (ic === undefined) return 'unknown'
  if (ic >= 0.05) return 'excellent'
  if (ic >= 0.03) return 'good'
  if (ic >= 0) return 'average'
  return 'poor'
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

<style scoped>
/* 主容器 - 使用固定定位覆盖整个屏幕 */
.research-detail-view {
  --bg-primary: #131722;
  --bg-secondary: #1e222d;
  --bg-tertiary: #2a2e39;
  --text-primary: #d1d4dc;
  --text-secondary: #787b86;
  --accent-blue: #2962ff;
  /* A股颜色规则：红涨绿跌 */
  --color-up: #ef5350;      /* 红色 - 上涨/正面 */
  --color-down: #26a69a;    /* 绿色 - 下跌/负面 */
  --accent-red: #ef5350;    /* 红色 - 保持兼容 */
  --accent-green: #26a69a;  /* 绿色 - 保持兼容 */
  --accent-orange: #ff9800;
  --border-color: #2a2e39;

  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 1000;
  display: flex;
  flex-direction: column;
  background: #131722;
  color: #d1d4dc;
  font-size: 13px;
  overflow: hidden;
}

/* 顶部导航 */
.navbar {
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border-color);
  padding: 0 20px;
  height: 56px;
  display: flex;
  align-items: center;
  gap: 20px;
}

.logo {
  font-size: 16px;
  font-weight: 700;
  color: var(--text-primary);
  display: flex;
  align-items: center;
  gap: 10px;
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

/* 阶段导航菜单样式 */
.stage-nav {
  display: flex;
  gap: 4px;
  flex: 1;
  margin-left: 16px;
}

.stage-btn {
  padding: 8px 16px;
  background: transparent;
  border: none;
  border-bottom: 2px solid transparent;
  border-radius: 0;
  color: var(--text-secondary);
  cursor: pointer;
  font-size: 13px;
  font-weight: 500;
  transition: all 0.15s;
  white-space: nowrap;
  display: flex;
  align-items: center;
  gap: 6px;
}

.stage-btn:hover {
  color: var(--text-primary);
  background: transparent;
}

.stage-btn.active {
  color: var(--accent-blue);
  border-bottom-color: var(--accent-blue);
  background: transparent;
}

.icon-nav {
  width: 14px;
  height: 14px;
  flex-shrink: 0;
}

/* 用户菜单 */
.user-menu {
  display: flex;
  align-items: center;
  gap: 8px;
}

.user-avatar {
  width: 32px;
  height: 32px;
  background: linear-gradient(135deg, var(--accent-blue), var(--accent-orange));
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 700;
  font-size: 14px;
  cursor: pointer;
  transition: transform 0.2s;
}

.user-avatar:hover {
  transform: scale(1.1);
}

.back-btn {
  padding: 6px 12px;
  background: transparent;
  border: 1px solid var(--border-color);
  color: var(--text-secondary);
  cursor: pointer;
  font-size: 12px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  gap: 4px;
  transition: all 0.2s;
  margin-right: 16px;
}

.back-btn:hover {
  background: var(--bg-tertiary);
  color: var(--text-primary);
  border-color: var(--accent-blue);
}

/* 图标样式 */
.icon-sm {
  width: 16px;
  height: 16px;
  flex-shrink: 0;
}

.icon-xs {
  width: 12px;
  height: 12px;
  flex-shrink: 0;
}

.icon-check {
  width: 18px;
  height: 18px;
}

.icon-step {
  width: 18px;
  height: 18px;
}

.step-number {
  font-size: 14px;
  font-weight: 700;
}

/* 主容器布局 */
.main-container {
  display: grid;
  grid-template-columns: 280px 1fr 320px;
  grid-template-rows: 1fr;
  height: calc(100vh - 56px);
  gap: 1px;
  background: var(--border-color);
}

/* 面板通用样式 */
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

.panel-actions {
  display: flex;
  gap: 4px;
}

.icon-btn {
  width: 24px;
  height: 24px;
  background: transparent;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  border-radius: 3px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.icon-btn:hover {
  background: var(--bg-tertiary);
  color: var(--text-primary);
}

/* 工作流列表 */
.workflow-list {
  flex: 1;
  overflow-y: auto;
}

.workflow-step {
  padding: 14px 16px;
  border-bottom: 1px solid var(--border-color);
  cursor: pointer;
  transition: background 0.15s;
  display: flex;
  align-items: center;
  gap: 12px;
}

.workflow-step:hover {
  background: var(--bg-secondary);
}

.workflow-step.selected {
  background: var(--bg-tertiary);
  border-left: 2px solid var(--accent-blue);
}

.step-icon {
  width: 32px;
  height: 32px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 700;
}

.workflow-step.completed .step-icon {
  background: var(--accent-green);
  color: white;
}

.workflow-step.active .step-icon {
  background: var(--accent-blue);
  color: white;
}

.workflow-step.pending .step-icon {
  background: var(--bg-tertiary);
  color: var(--text-secondary);
}

.step-info {
  flex: 1;
}

.step-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 2px;
}

.step-status {
  font-size: 11px;
  color: var(--text-secondary);
}

.step-status.completed {
  color: var(--accent-green);
}

/* 主内容区 */
.content-area {
  padding: 24px;
  overflow-y: auto;
}

.page-title {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.page-subtitle {
  font-size: 13px;
  color: var(--text-secondary);
  margin-bottom: 16px;
}

/* Tabs */
.content-tabs {
  display: flex;
  gap: 4px;
  margin-bottom: 16px;
  border-bottom: 1px solid var(--border-color);
}

.content-tab {
  padding: 10px 16px;
  background: transparent;
  border: none;
  border-bottom: 2px solid transparent;
  color: var(--text-secondary);
  cursor: pointer;
  font-size: 12px;
  font-weight: 600;
  transition: all 0.15s;
  display: flex;
  align-items: center;
  gap: 6px;
}

.tab-icon {
  width: 14px;
  height: 14px;
}

.content-tab:hover {
  color: var(--text-primary);
}

.content-tab.active {
  color: var(--accent-blue);
  border-bottom-color: var(--accent-blue);
}

.tab-pane {
  display: none;
}

.tab-pane.active {
  display: block;
}

/* 统计卡片 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 16px;
}

.summary-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 12px;
  margin-bottom: 16px;
  padding: 0;

  .summary-card {
    background: var(--bg-secondary, #1e222d);
    padding: 12px;
    border-radius: 8px;
    border: 1px solid var(--border-color, #2a2e39);
    display: flex;
    align-items: center;
    gap: 12px;
    transition: all 0.2s;

    &:hover {
      border-color: var(--accent-blue, #2962ff);
    }

    .card-icon {
      width: 42px;
      height: 42px;
      border-radius: 8px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 20px;
      color: white;
      background: linear-gradient(135deg, #2962ff 0%, #1e88e5 100%);

      &.factors-icon {
        background: linear-gradient(135deg, #7c4dff 0%, #651fff 100%);
      }

      &.ic-icon {
        background: linear-gradient(135deg, #2962ff 0%, #1e88e5 100%);
      }

      &.ir-icon {
        background: linear-gradient(135deg, #00bfa5 0%, #00897b 100%);
      }

      &.qualified-icon {
        background: linear-gradient(135deg, #ef5350 0%, #c62828 100%);
      }
    }

    .card-content {
      flex: 1;
      min-width: 0;
      display: flex;
      flex-direction: column;
      justify-content: center;
    }

    .stat-label {
      font-size: 10px;
      color: var(--text-secondary, #787b86);
      margin-bottom: 2px;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      line-height: 1.2;
    }

    .stat-value {
      font-size: 18px;
      font-weight: 700;
      color: var(--text-primary, #d1d4dc);
      line-height: 1.2;

      &.positive {
        color: var(--color-up, #ef5350);
      }

      &.negative {
        color: var(--color-down, #26a69a);
      }
    }

    .stat-change {
      font-size: 10px;
      color: var(--text-secondary, #787b86);
      margin-top: 2px;
      line-height: 1.2;
    }
  }
}

.stat-card {
  background: transparent;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  padding: 12px;
}

.stat-label {
  font-size: 11px;
  color: var(--text-secondary);
  margin-bottom: 8px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
}

/* A股规则：红涨/好，绿跌/坏 */
.stat-value.positive {
  color: var(--color-up);  /* 红色 - 正面 */
}

.stat-value.negative {
  color: var(--color-down);  /* 绿色 - 负面 */
}

.stat-change {
  font-size: 11px;
  color: var(--text-secondary);
  margin-top: 4px;
}

/* 因子库质量雷达图 */
.radar-section {
  width: 100%;
  box-sizing: border-box;
  background: var(--bg-secondary);
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 12px;
}

.radar-chart-container {
  width: 100%;
  height: 300px;
}

.radar-chart {
  width: 100%;
  height: 100%;
}

/* 质量指标面板 */
.quality-metrics-panel {
  display: flex;
  gap: 0;
  padding: 12px 0;
  align-items: center;
}

/* 质量指标列表 - 行内布局 */
.quality-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  flex: 0 0 500px;
}

.quality-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.quality-item-icon {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-secondary);

  svg {
    width: 16px;
    height: 16px;
  }
}

.quality-item-label {
  font-size: 14px;
  color: var(--text-secondary);
  width: 70px;
}

.quality-item-score {
  font-size: 20px;
  font-weight: 700;
  width: 50px;
  text-align: right;
}

.quality-item-bar {
  flex: 1;
  height: 6px;
  background: rgba(255,255,255,0.1);
  border-radius: 3px;
  overflow: hidden;
  min-width: 80px;
}

.quality-bar-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.3s ease;
}

.quality-item-raw {
  font-size: 12px;
  color: var(--text-secondary);
  width: 50px;
  text-align: right;
}

.quality-metrics-panel .radar-chart-wrapper {
  flex: 1;
  min-width: 300px;
  height: 280px;
}

.quality-metrics-panel .radar-chart-wrapper .radar-chart {
  width: 100%;
  height: 100%;
}

/* 因子库综合评分样式 */
.quality-total-score {
  flex: 0 0 160px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 12px 16px;
  background: linear-gradient(135deg, rgba(239, 83, 80, 0.15) 0%, rgba(30, 34, 45, 0.9) 100%);
  border-radius: 10px;
  border: 1px solid rgba(239, 83, 80, 0.3);
  margin-left: 16px;
  transition: all 0.3s;

  &:hover {
    border-color: rgba(239, 83, 80, 0.5);
    background: linear-gradient(135deg, rgba(239, 83, 80, 0.2) 0%, rgba(30, 34, 45, 0.95) 100%);
  }
}

.quality-total-header {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 8px;
}

.quality-total-label {
  font-size: 12px;
  color: var(--text-secondary);
  font-weight: 500;
}

.quality-total-value {
  font-size: 40px;
  font-weight: 700;
  line-height: 1;
  margin-bottom: 8px;
}

/* 星级和字母等级 */
.quality-rating {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  margin-bottom: 10px;
}

.star-rating {
  display: flex;
  gap: 2px;

  .star-icon {
    width: 14px;
    height: 14px;
    color: #787b86;

    &.filled {
      color: inherit;
    }
  }
}

.letter-grade {
  font-size: 16px;
  font-weight: 700;
}

.quality-total-bar {
  width: 100%;
  height: 5px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 3px;
  overflow: hidden;
}

.quality-total-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.3s ease;
}

/* 个体因子评估面板样式 */
.single-factor-evaluation-section {
  background: var(--bg-secondary);
  padding: 12px;
  border-radius: 8px;
  border: 1px solid var(--border-color);
  margin-bottom: 4px;
}

.evaluation-metrics-panel {
  display: flex;
  gap: 0;
  padding: 12px 0;
  align-items: flex-start;
}

/* 评估指标列表 - 两列布局 */
.evaluation-list {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px 24px;
  flex: 0 0 620px;
  padding-bottom: 0;
}

.evaluation-item {
  display: flex;
  align-items: center;
  gap: 6px;
}

.evaluation-item-icon {
  width: 22px;
  height: 22px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-secondary);

  svg {
    width: 14px;
    height: 14px;
  }
}

.evaluation-item-label {
  font-size: 12px;
  color: var(--text-secondary);
  width: 60px;
}

.evaluation-item-score {
  font-size: 16px;
  font-weight: 700;
  width: 40px;
  text-align: right;
}

.evaluation-item-bar {
  flex: 1;
  height: 4px;
  background: rgba(255,255,255,0.1);
  border-radius: 2px;
  overflow: hidden;
  min-width: 60px;
}

.evaluation-bar-fill {
  height: 100%;
  border-radius: 2px;
  transition: width 0.3s ease;
}

.evaluation-item-raw {
  font-size: 10px;
  color: var(--text-secondary);
  width: 45px;
  text-align: right;
  font-family: monospace;
}

.evaluation-radar-wrapper {
  flex: 1;
  min-width: 280px;
  height: 320px;
}

.evaluation-radar-wrapper .radar-chart {
  width: 100%;
  height: 100%;
}

/* 综合评分（内联在指标列表下方） */
.evaluation-total-score-inline {
  grid-column: 1 / -1;
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 12px 16px;
  background: linear-gradient(135deg, rgba(239, 83, 80, 0.15) 0%, rgba(30, 34, 45, 0.9) 100%);
  border-radius: 10px;
  border: 1px solid rgba(239, 83, 80, 0.3);
  margin-top: 40px;
}

.total-inline-header {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}

.total-inline-label {
  font-size: 14px;
  color: var(--text-secondary);
  font-weight: 600;
  white-space: nowrap;
}

.total-inline-content {
  display: flex;
  align-items: center;
  gap: 16px;
  flex: 1;
}

.total-inline-value {
  font-size: 36px;
  font-weight: 700;
  line-height: 1;
  min-width: 70px;
}

/* 星级和字母等级（内联） */
.total-inline-rating {
  display: flex;
  align-items: center;
  gap: 8px;
}

.star-rating-inline {
  display: flex;
  gap: 2px;

  .star-icon-inline {
    width: 14px;
    height: 14px;
    color: #787b86;

    &.filled {
      color: inherit;
    }
  }
}

.letter-grade-inline {
  font-size: 14px;
  font-weight: 700;
}

.total-inline-bar {
  flex: 1;
  height: 8px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
  overflow: hidden;
  max-width: 200px;
}

.total-inline-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.3s ease;
}

/* 综合指标面板样式 */
.metrics-panel {
  display: flex;
  gap: 12px;
  padding: 8px 0;
  align-items: center;
  justify-content: flex-end;
}

.metrics-panel .metrics-list {
  flex: 0 0 200px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.metrics-panel .metric-score-item .metric-score-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2px;
}

.metrics-panel .metric-name {
  font-size: 12px;
  color: var(--text-secondary, #a0a0a0);
}

.metrics-panel .metric-value {
  font-size: 13px;
  font-weight: 600;
  color: #409ee1;
}

.metrics-panel .metric-progress-bar {
  height: 4px;
  background: rgba(255,255,255,0.1);
  border-radius: 2px;
  overflow: hidden;
}

.metrics-panel .metric-progress-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.3s ease;
}

.metrics-panel .metric-raw-value {
  font-size: 11px;
  color: var(--text-secondary, #666);
  margin-top: 2px;
  text-align: right;
}

.metrics-panel .radar-chart-wrapper {
  flex: 1;
  min-width: 280px;
  height: 260px;
}

.metrics-panel .radar-chart-wrapper .radar-chart {
  width: 100%;
  height: 100%;
}

/* 进度条/配置区域 - 与BacktestPerformanceChart对齐 */
.progress-section {
  width: 100%;
  box-sizing: border-box;
  background: var(--bg-secondary);
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 16px;
}

.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.progress-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}

.progress-percent {
  font-size: 14px;
  font-weight: 700;
  color: var(--accent-blue);
}

.progress-bar {
  height: 6px;
  background: var(--bg-tertiary);
  border-radius: 3px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--accent-blue), var(--accent-green));
  border-radius: 3px;
  transition: width 0.3s;
}

/* 因子计算类型卡片 */
.type-cards {
  display: flex;
  gap: 12px;
}

.type-card {
  flex: 1;
  display: flex;
  align-items: center;
  padding: 16px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.type-card:hover {
  background: var(--bg-tertiary);
  border-color: var(--primary-color);
}

.type-card.active {
  background: var(--primary-color-light);
  border-color: var(--primary-color);
}

.type-card-icon {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 12px;
  color: var(--primary-color);
}

.type-card-icon svg {
  width: 24px;
  height: 24px;
}

.type-card-content {
  flex: 1;
}

.type-card-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.type-card-desc {
  font-size: 12px;
  color: var(--text-secondary);
}

.type-card-check {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-left: 8px;
}

.check-icon {
  width: 20px;
  height: 20px;
  color: var(--primary-color);
}

/* 技术指标区域 */
.indicator-section {
  padding: 16px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
}

.indicator-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.indicator-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}

.indicator-icon {
  width: 18px;
  height: 18px;
  color: var(--primary-color);
}

.indicator-options {
  padding-top: 12px;
  border-top: 1px solid var(--border-color);
}

.preset-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
}

/* 任务列表样式 */
.task-list-section {
  margin-top: 24px;
}

/* 结果查看器样式 */
.result-stats {
  background: rgba(64, 158, 255, 0.1);
  color: var(--primary-color);
}

.task-status.completed {
  background: rgba(103, 194, 58, 0.1);
  color: var(--success-color);
}

.task-status.failed {
  background: rgba(245, 108, 108, 0.1);
  color: var(--danger-color);
}

.task-info {
  margin-bottom: 8px;
}

/* 任务列表表格样式 */
.task-id-cell {
  font-size: 12px;
  color: var(--text-secondary);
  font-family: monospace;
}

.task-expression-cell {
  font-size: 13px;
  color: var(--text-primary);
}

.progress-cell {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100px;
}

.progress-text {
  font-size: 11px;
  color: var(--text-secondary);
  min-width: 30px;
}

.time-cell {
  font-size: 12px;
  color: var(--text-secondary);
}

.action-buttons-cell {
  display: flex;
  gap: 4px;
}

/* 结果查看器样式 */
.result-stats {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 16px;
  margin-top: 16px;
  margin-bottom: 16px;
  background: transparent;
}

.result-stats .stat-card {
  background: var(--bg-secondary, #1e222d);
  border: 1px solid var(--border-color, #2a2e39);
  border-radius: 8px;
  padding: 16px;
  text-align: center;
  transition: all 0.2s;
}

.result-stats .stat-card:hover {
  border-color: var(--accent-blue, #2962ff);
}

.result-stats .stat-icon {
  width: 24px;
  height: 24px;
  margin: 0 auto 8px;
  color: var(--primary-color);
}

.result-stats .stat-icon svg {
  width: 100%;
  height: 100%;
}

/* 修复按钮组之间的白线 */
.result-btn-group {
  display: inline-flex;
  gap: 4px;
}

.result-btn-group .el-button {
  border-color: var(--border-color, #2a2e39) !important;
  border-radius: 6px !important;
}

.result-btn-group .el-button:hover {
  border-color: var(--primary-color) !important;
}

.stat-label {
  font-size: 12px;
  color: var(--text-secondary);
  margin-bottom: 8px;
}

.stat-value {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
}

.icon-xs {
  width: 14px;
  height: 14px;
  margin-right: 4px;
}

/* 数据表格 */
.section-title {
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 16px;
  color: var(--text-primary);
  display: flex;
  align-items: center;
  gap: 8px;
}

.section-icon {
  width: 16px;
  height: 16px;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 16px;
}

.data-table th {
  background: var(--bg-secondary);
  padding: 10px 12px;
  text-align: left;
  font-size: 11px;
  font-weight: 600;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  border-bottom: 1px solid var(--border-color);
}

.data-table td {
  padding: 12px;
  border-bottom: 1px solid var(--border-color);
  font-size: 13px;
  color: var(--text-primary);
}

.data-table tr:hover {
  background: var(--bg-secondary);
}

/* A股规则：红涨/好，绿跌/坏 */
.value.positive {
  color: var(--color-up);  /* 红色 - 正面 */
  font-weight: 600;
}

.value.negative {
  color: var(--color-down);  /* 绿色 - 负面 */
  font-weight: 600;
}

.status-badge {
  padding: 3px 8px;
  border-radius: 3px;
  font-size: 11px;
  font-weight: 600;
}

.status-badge.pass {
  background: rgba(239, 83, 80, 0.2);
  color: var(--accent-red);
}

.status-badge.fail {
  background: rgba(38, 166, 154, 0.2);
  color: var(--accent-green);
}

.status-badge.pending {
  background: rgba(128, 128, 128, 0.2);
  color: var(--text-secondary);
}

.status-badge.running {
  background: rgba(64, 158, 255, 0.2);
  color: var(--primary-color);
}

/* 表单 - 使用响应式网格与上面的统计卡片对齐 */
.config-form {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

@media (max-width: 1400px) {
  .config-form {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 600px) {
  .config-form {
    grid-template-columns: 1fr;
  }
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group.full-width {
  grid-column: 1 / -1;
}

.form-label {
  font-size: 11px;
  color: var(--text-secondary);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.form-input,
.form-select {
  padding: 10px 12px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 4px;
  color: var(--text-primary);
  font-size: 13px;
  transition: border-color 0.15s;
}

.form-input:focus,
.form-select:focus {
  outline: none;
  border-color: var(--accent-blue);
}

/* 下拉框选项样式 */
.form-select option {
  background: var(--bg-secondary);
  color: var(--text-primary);
  padding: 8px 12px;
}

.form-select option:hover,
.form-select option:checked {
  background: var(--accent-blue);
  color: white;
}

.form-hint {
  font-size: 10px;
  color: var(--text-secondary);
  margin-top: 4px;
}

.checkbox-group {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.checkbox-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  cursor: pointer;
}

.checkbox-item input[type="checkbox"] {
  width: 16px;
  height: 16px;
  accent-color: var(--accent-blue);
}

/* 操作按钮 */
.action-buttons {
  display: flex;
  gap: 12px;
  padding-top: 24px;
  border-top: 1px solid var(--border-color);
}

.btn {
  padding: 12px 24px;
  border: none;
  border-radius: 4px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-primary {
  background: var(--accent-blue);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #1e4bd8;
}

.btn-success {
  background: var(--accent-green);
  color: white;
}

.btn-success:hover:not(:disabled) {
  background: #1e8a80;
}

.btn-secondary {
  background: var(--bg-tertiary);
  color: var(--text-primary);
  border: 1px solid var(--border-color);
}

.btn-secondary:hover {
  background: #363a45;
}

/* 占位符 */
.heatmap-placeholder {
  text-align: center;
  padding: 40px;
  color: var(--text-secondary);
}

.placeholder-icon {
  font-size: 48px;
  display: block;
  margin-bottom: 16px;
}

.hint {
  font-size: 13px;
  margin-top: 8px;
}

/* 因子列表 */
.factor-list {
  flex: 1;
  overflow-y: auto;
}

.factor-item {
  padding: 12px 16px;
  border-bottom: 1px solid var(--border-color);
  cursor: pointer;
  transition: background 0.15s;
}

.factor-item:hover {
  background: var(--bg-secondary);
}

.factor-item.selected {
  background: var(--bg-secondary);
}

.factor-name {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.factor-type {
  font-size: 10px;
  color: var(--text-secondary);
  margin-bottom: 8px;
}

.factor-metrics {
  display: flex;
  gap: 12px;
  font-size: 11px;
}

.metric {
  color: var(--text-secondary);
}

.metric-value {
  font-weight: 600;
  color: var(--text-primary);
}

/* A股规则：红涨/好，绿跌/坏 */
.metric-value.positive {
  color: var(--color-up);  /* 红色 - 正面 */
}

.metric-value.negative {
  color: var(--color-down);  /* 绿色 - 负面 */
}

/* 滚动条 */
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

::-webkit-scrollbar-track {
  background: var(--bg-primary);
}

::-webkit-scrollbar-thumb {
  background: var(--bg-tertiary);
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: #363a45;
}

/* 面板标题带图标 */
.panel-title {
  display: flex;
  align-items: center;
  gap: 8px;
}

/* 步骤状态指示点 */
.step-status {
  display: flex;
  align-items: center;
  gap: 6px;
}

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--text-secondary);
}

.step-status.completed .status-dot {
  background: var(--color-up);  /* 红色 - 完成 */
  box-shadow: 0 0 6px var(--color-up);
}

.step-status.active .status-dot {
  background: var(--accent-blue);
  box-shadow: 0 0 6px var(--accent-blue);
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

/* 因子项新样式 */
.factor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}

.factor-status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  margin-right: 8px;
}

.factor-status-dot.excellent {
  background: var(--color-up);  /* 红色 - 极好 */
  box-shadow: 0 0 6px var(--color-up);
}

.factor-status-dot.good {
  background: var(--accent-orange);
}

.factor-status-dot.average {
  background: var(--text-secondary);
}

.factor-status-dot.poor {
  background: var(--color-down);  /* 绿色 - 差 */
}

.factor-score {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  font-weight: 700;
}

.factor-score.excellent {
  color: var(--color-up);  /* 红色 - 极好 */
}

.factor-score.good {
  color: var(--accent-orange);
}

.factor-score.average {
  color: var(--text-secondary);
}

.factor-score.poor {
  color: var(--color-down);  /* 绿色 - 差 */
}

.type-tag {
  display: inline-block;
  padding: 2px 6px;
  background: var(--bg-tertiary);
  border-radius: 3px;
  font-size: 10px;
  font-weight: 600;
  color: var(--accent-blue);
}

.type-separator {
  margin: 0 6px;
  color: var(--text-secondary);
}

/* 指标带图标样式 */
.metric {
  display: flex;
  align-items: center;
  gap: 4px;
  color: var(--text-secondary);
}

/* 任务头部信息 */
.task-header-info {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.task-id-badge {
  padding: 4px 10px;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  border-radius: 4px;
  font-size: 11px;
  font-weight: 600;
  color: var(--accent-blue);
  font-family: monospace;
}

/* 任务配置信息 */
.task-config-info {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  padding: 12px 16px;
  margin-bottom: 8px;
}

.config-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.stock-pool-wrap {
  display: flex;
  align-items: center;
}

.stock-pool-wrap .el-select {
  width: auto;
  min-width: 100px;
}

.custom-stocks-count {
  font-size: 12px;
  color: var(--accent-blue);
  margin-left: 8px;
}

.dialog-header-with-icon {
  display: flex;
  align-items: center;
  gap: 10px;

  .dialog-header-icon {
    width: 20px;
    height: 20px;
    color: var(--accent-blue);
  }

  span {
    font-size: 16px;
    font-weight: 600;
    color: var(--text-primary);
  }
}

.custom-stock-dialog-content {
  .dialog-desc {
    margin-bottom: 12px;
    color: var(--text-secondary);
  }

  :deep(.el-textarea__inner) {
    background: var(--bg-tertiary);
    color: var(--text-primary);
    border-color: var(--border-color);
  }

  .dialog-tips {
    margin-top: 12px;
    padding: 12px;
    background: var(--bg-tertiary);
    border-radius: 4px;
    font-size: 12px;
    color: var(--text-secondary);

    p {
      margin-bottom: 8px;
    }

    ul {
      margin: 0;
      padding-left: 20px;
    }

    li {
      margin-bottom: 4px;
    }
  }
}

.config-label {
  font-size: 10px;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  display: flex;
  align-items: center;
  gap: 4px;
}

.config-icon {
  width: 12px;
  height: 12px;
}

.config-value {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
}

/* 日期选择器样式修复 */
.el-date-editor {
  background: rgba(255, 255, 255, 0.05) !important;
}

/* 强制所有日期编辑器背景透明 */
.el-date-editor.el-range-editor,
.el-date-editor.el-range-editor.el-input__wrapper,
.el-date-editor.el-range-editor .el-range-input,
.el-range-editor .el-range-input {
  background: transparent !important;
  background-color: transparent !important;
}

.el-date-editor .el-range-input {
  color: #e0e0e0 !important;
  background: transparent !important;
}

.el-date-editor .el-range-input::placeholder {
  color: rgba(255, 255, 255, 0.4) !important;
}

.el-date-editor .el-range-separator {
  color: rgba(255, 255, 255, 0.4) !important;
}

/* 日期范围编辑器背景强制透明 */
.el-range-editor.el-input__wrapper,
.el-range-editor.el-input__wrapper:hover,
.el-range-editor.el-input__wrapper.is-focus {
  background: transparent !important;
  box-shadow: none !important;
}

/* 日期选择器样式修复 */
.el-picker-panel__body {
  --el-datepicker-active-color: var(--el-color-primary);
}

/* 选中日期单元格背景透明 */
.el-date-table td.current .cell,
.el-date-table td.start-date .cell,
.el-date-table td.end-date .cell,
.el-date-table td.selected .cell {
  background: transparent !important;
  color: var(--el-color-primary) !important;
  border: 1px solid var(--el-color-primary) !important;
}

.el-date-table td.in-range .cell,
.el-date-table td.start-range .cell,
.el-date-table td.end-range .cell {
  background: rgba(102, 126, 234, 0.15) !important;
  color: var(--el-color-primary) !important;
}

.el-date-table td .cell:hover {
  background: rgba(102, 126, 234, 0.2) !important;
}

/* 强制覆盖所有td背景 */
.el-date-table td {
  background: transparent !important;
}

/* el-select 下拉框样式统一 */
.el-select-dropdown,
.el-select-dropdown.el-popper,
.el-select-dropdown__popper,
div.el-select-dropdown {
  background-color: rgba(26, 26, 46, 0.98) !important;
  border: 1px solid rgba(102, 126, 234, 0.3) !important;
  box-shadow: none !important;
}

/* 下拉框输入框和弹出框背景统一 */
.el-select .el-input__wrapper,
.el-select-dropdown {
  background-color: rgba(26, 26, 46, 0.98) !important;
  border-color: rgba(102, 126, 234, 0.3) !important;
}

.el-select-dropdown__item {
  color: #e0e0e0 !important;
  background-color: transparent !important;
}

.el-select-dropdown__item.hover,
.el-select-dropdown__item:hover,
.el-select-dropdown__item:focus,
.el-select-dropdown__item.is-hovering,
.el-select-dropdown__item.is-focus {
  background-color: #2a2a4e !important;
  color: #e0e0e0 !important;
}

.el-select-dropdown__item:last-child {
  background-color: transparent !important;
}

.el-select-dropdown__item.selected {
  color: #409eff !important;
  font-weight: 500;
}

.el-select-dropdown__empty {
  color: #888 !important;
}

/* 多选标签样式 */
.el-select {
  width: auto !important;
}

.el-select .el-select__wrapper {
  min-width: 80px;
  background-color: rgba(26, 26, 46, 0.98) !important;
  border-color: rgba(102, 126, 234, 0.3) !important;
  box-shadow: none !important;
}

.el-select .el-select__wrapper:hover {
  border-color: rgba(64, 158, 255, 0.5) !important;
}

.el-select .el-select__wrapper.is-focused {
  border-color: #409eff !important;
}

.el-select .el-select__wrapper .el-select__placeholder {
  color: rgba(255, 255, 255, 0.4) !important;
}

.el-select .el-select__wrapper .el-select__selected-item {
  color: #e0e0e0 !important;
}

.el-select__tags {
  gap: 2px;
}

.el-select__tags > span {
  display: flex;
  flex-wrap: wrap;
  gap: 2px;
}

/* 日期选择器范围选中样式 - 使用 :deep() 穿透 */
:deep(.el-date-table td.in-range .cell),
:deep(.el-date-table td.start-date .cell),
:deep(.el-date-table td.end-date .cell) {
  background-color: #1E222D !important;
  color: #ffffff !important;
}

:deep(.el-date-table td.in-range .cell span),
:deep(.el-date-table td.start-date .cell span),
:deep(.el-date-table td.end-date .cell span) {
  background-color: transparent !important;
  color: #ffffff !important;
}

/* 范围背景 */
:deep(.el-date-table td.in-range > div),
:deep(.el-date-table td.start-date > div),
:deep(.el-date-table td.end-date > div) {
  background-color: rgba(102, 126, 234, 0.2) !important;
}

:deep(.el-date-table td.start-date > div),
:deep(.el-date-table td.end-date > div) {
  background-color: #667eea !important;
}

/* 自定义日期范围类名样式 */
:deep(.custom-date-inrange .cell),
:deep(.custom-date-start .cell),
:deep(.custom-date-end .cell) {
  background-color: #1E222D !important;
  color: #ffffff !important;
}

:deep(.custom-date-inrange .cell span),
:deep(.custom-date-start .cell span),
:deep(.custom-date-end .cell span) {
  background-color: transparent !important;
  color: #ffffff !important;
}

:deep(.custom-date-inrange > div) {
  background-color: rgba(102, 126, 234, 0.2) !important;
}

:deep(.custom-date-start > div),
:deep(.custom-date-end > div) {
  background-color: #667eea !important;
}
</style>

<style lang="scss">
// 全局样式 - 预设按钮深色主题
.preset-buttons {
  // 直接选择 el-button，不加限定
  .el-button {
    transition: all 0.2s !important;
    border-radius: 4px !important;
    font-size: 12px !important;
    padding: 6px 12px !important;

    // 选中状态 - 淡蓝色背景
    &[class*="el-button--primary"] {
      background: rgba(41, 98, 255, 0.2) !important;
      border-color: #2962ff !important;
      color: #2962ff !important;

      &:hover {
        background: rgba(41, 98, 255, 0.3) !important;
        border-color: #2962ff !important;
        color: #2962ff !important;
      }
    }

    // 未选中状态 - 深色主题
    &[class*="is-plain"] {
      background: #131722 !important;
      border-color: #2a2e39 !important;
      color: #787b86 !important;

      &:hover {
        background: #1e222d !important;
        border-color: #d1d4dc !important;
        color: #d1d4dc !important;
      }
    }
  }
}

// 复选框样式 - 白色勾选
.el-checkbox {
  .el-checkbox__input.is-checked {
    .el-checkbox__inner {
      background-color: rgba(41, 98, 255, 0.2) !important;
      border-color: #2962ff !important;

      &::after {
        border-color: #ffffff !important;
      }
    }
  }

  .el-checkbox__inner {
    background-color: transparent !important;
    border-color: #787b86 !important;

    &:hover {
      border-color: #2962ff !important;
    }
  }

  .el-checkbox__label {
    color: var(--text-secondary, #787b86) !important;
  }
}
</style>

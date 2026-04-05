<template>
  <div class="backtest-page">
    <h1 class="page-title">
      <svg class="icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline>
      </svg>
      {{ isZh ? '策略回测' : 'Strategy Backtest' }}
    </h1>
    <p class="page-subtitle">{{ isZh ? '验证策略在历史数据上的表现' : 'Validate strategy performance on historical data' }}</p>

    <!-- 回测绩效图表 -->
    <BacktestPerformanceChart
      :task-id="taskId"
      :is-zh="isZh"
    />

    <!-- 回测配置 -->
    <div class="progress-section">
      <h3 class="section-title" style="margin-bottom: 16px;">
        <svg class="icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="3"></circle>
          <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path>
        </svg>
        {{ isZh ? '回测配置' : 'Backtest Configuration' }}
      </h3>
      <div class="config-form">
        <div class="form-group">
          <label class="form-label">{{ isZh ? '开始日期' : 'Start Date' }}</label>
          <input type="date" class="form-input" v-model="backtestConfig.startDate" />
        </div>
        <div class="form-group">
          <label class="form-label">{{ isZh ? '结束日期' : 'End Date' }}</label>
          <input type="date" class="form-input" v-model="backtestConfig.endDate" />
        </div>
        <div class="form-group">
          <label class="form-label">{{ isZh ? '初始资金' : 'Initial Capital' }}</label>
          <input type="number" class="form-input" v-model.number="backtestConfig.initialCapital" />
        </div>
        <div class="form-group">
          <label class="form-label">{{ isZh ? '手续费率' : 'Commission' }}</label>
          <input type="number" class="form-input" step="0.0001" v-model.number="backtestConfig.commission" />
        </div>
      </div>
    </div>

    <!-- 操作按钮 -->
    <div class="action-buttons">
      <ActionButton
        type="primary"
        :label="isBacktesting ? (isZh ? '回测中...' : 'Backtesting...') : (isZh ? '运行回测' : 'Run Backtest')"
        :loading="isBacktesting"
        :disabled="isBacktesting"
        @click="runBacktest"
      />
      <ActionButton
        type="default"
        :label="isZh ? '导出报告' : 'Export Report'"
        @click="exportBacktest"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import ActionButton from '@/components/ui/ActionButton.vue'
import BacktestPerformanceChart from '../BacktestPerformanceChart.vue'
import { useAppStore } from '@/stores/core/AppStore'

interface Props {
  taskId: string
  isZh: boolean
}

const props = defineProps<Props>()

const appStore = useAppStore()
const isZh = computed(() => props.isZh || appStore.language === 'zh')

// 回测配置
const backtestConfig = reactive({
  startDate: '2023-01-01',
  endDate: '2024-12-31',
  initialCapital: 1000000,
  commission: 0.0003
})

const isBacktesting = ref(false)

const runBacktest = async () => {
  isBacktesting.value = true
  console.log('Running backtest with config:', backtestConfig)
  // 调用后端回测API
  setTimeout(() => {
    isBacktesting.value = false
  }, 2000)
}

const exportBacktest = () => {
  console.log('Exporting backtest report...')
}
</script>

<style scoped lang="scss">
@import '../styles/_variables.scss';

.backtest-page {
  --accent-blue: #2962ff;
  --border-color: #2a2e39;

  width: 100%;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.page-subtitle {
  font-size: 14px;
  color: var(--text-secondary);
  margin-bottom: 24px;
}

.progress-section {
  padding: 16px;
  background: var(--bg-secondary);
  border-radius: 6px;
  border: 1px solid var(--border-color);
  margin-bottom: 20px;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 12px;
}

.icon-sm {
  width: 16px;
  height: 16px;
}

.config-form {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-label {
  font-size: 12px;
  color: var(--text-secondary);
}

.form-input {
  padding: 8px 12px;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  border-radius: 4px;
  color: var(--text-primary);
  font-size: 13px;

  &:focus {
    outline: none;
    border-color: var(--accent-blue);
  }
}

.action-buttons {
  display: flex;
  gap: 12px;
}

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary {
  background: var(--accent-blue);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #2952cc;
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-secondary {
  background: var(--bg-tertiary);
  color: var(--text-primary);
  border: 1px solid var(--border-color);
}

.btn-secondary:hover {
  background: var(--bg-secondary);
}
</style>

<template>
  <div class="research-backtest">
    <h1 class="page-title">{{ isZh ? '策略回测' : 'Strategy Backtest' }}</h1>
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
      <button class="btn btn-primary" @click="runBacktest" :disabled="isBacktesting">
        {{ isBacktesting ? (isZh ? '回测中...' : 'Backtesting...') : (isZh ? '运行回测' : 'Run Backtest') }}
      </button>
      <button class="btn btn-secondary" @click="exportBacktest">{{ isZh ? '导出报告' : 'Export Report' }}</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import BacktestPerformanceChart from '../BacktestPerformanceChart.vue'

interface Props {
  taskId?: string
  isZh?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  taskId: 'default',
  isZh: true
})

const emit = defineEmits<{
  (e: 'backtest-complete', result: any): void
}>()

// 回测配置数据
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
  // TODO: 调用后端回测API
  setTimeout(() => {
    isBacktesting.value = false
    emit('backtest-complete', { success: true })
  }, 2000)
}

const exportBacktest = () => {
  console.log('Exporting backtest report...')
}
</script>

<style scoped>
@import '../ResearchDetailView.vue';
</style>

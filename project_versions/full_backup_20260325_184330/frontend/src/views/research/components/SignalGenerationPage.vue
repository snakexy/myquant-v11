<template>
  <div class="signal-generation-page">
    <h1 class="page-title">{{ isZh ? '交易信号生成' : 'Trading Signal Generation' }}</h1>
    <p class="page-subtitle">{{ isZh ? '基于策略模型生成买卖信号' : 'Generate buy/sell signals based on strategy model' }}</p>

    <!-- 信号统计 -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-label">
          <svg class="icon-xs" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"></circle>
            <line x1="12" y1="8" x2="12" y2="12"></line>
            <line x1="12" y1="16" x2="12.01" y2="16"></line>
          </svg>
          {{ isZh ? '今日信号' : 'Today Signals' }}
        </div>
        <div class="stat-value positive">{{ signalStats.todaySignals }}</div>
        <div class="stat-change">{{ isZh ? '个股票' : 'stocks' }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">
          <svg class="icon-xs" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 19V5M5 12l7-7 7 7"/>
          </svg>
          {{ isZh ? '买入信号' : 'Buy Signals' }}
        </div>
        <div class="stat-value positive">{{ signalStats.buySignals }}</div>
        <div class="stat-change">{{ isZh ? '看涨' : 'Bullish' }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">
          <svg class="icon-xs" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 5v14M5 12l7 7 7-7"/>
          </svg>
          {{ isZh ? '卖出信号' : 'Sell Signals' }}
        </div>
        <div class="stat-value negative">{{ signalStats.sellSignals }}</div>
        <div class="stat-change">{{ isZh ? '看跌' : 'Bearish' }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">
          <svg class="icon-xs" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
            <polyline points="22 4 12 14.01 9 11.01"/>
          </svg>
          {{ isZh ? '信号准确率' : 'Accuracy' }}
        </div>
        <div :class="['stat-value', { positive: signalStats.accuracy > 60 }]">
          {{ signalStats.accuracy.toFixed(1) }}%
        </div>
        <div class="stat-change">{{ isZh ? '近30天' : 'Last 30 days' }}</div>
      </div>
    </div>

    <!-- 最新信号列表 -->
    <div class="progress-section">
      <h3 class="section-title" style="margin-bottom: 16px;">
        <svg class="icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M22 12h-4l-3 9L9 3l-3 9H2"/>
        </svg>
        {{ isZh ? '最新交易信号' : 'Latest Trading Signals' }}
      </h3>
      <table class="data-table">
        <thead>
          <tr>
            <th>{{ isZh ? '股票代码' : 'Code' }}</th>
            <th>{{ isZh ? '股票名称' : 'Name' }}</th>
            <th>{{ isZh ? '信号类型' : 'Signal' }}</th>
            <th>{{ isZh ? '信号强度' : 'Strength' }}</th>
            <th>{{ isZh ? '生成时间' : 'Time' }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="signal in latestSignals" :key="signal.code">
            <td>{{ signal.code }}</td>
            <td>{{ signal.name }}</td>
            <td>
              <span :class="['status-badge', signal.type === 'buy' ? 'pass' : 'fail']">
                {{ signal.type === 'buy' ? (isZh ? '买入' : 'Buy') : (isZh ? '卖出' : 'Sell') }}
              </span>
            </td>
            <td :class="['value', { positive: signal.strength > 0.7 }]">{{ (signal.strength * 100).toFixed(0) }}%</td>
            <td>{{ signal.time }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 操作按钮 -->
    <div class="action-buttons">
      <ActionButton
        type="primary"
        :label="isGenerating ? (isZh ? '生成中...' : 'Generating...') : (isZh ? '生成信号' : 'Generate Signals')"
        :loading="isGenerating"
        :disabled="isGenerating"
        @click="generateSignals"
      />
      <ActionButton
        type="default"
        :label="isZh ? '导出信号' : 'Export Signals'"
        @click="exportSignals"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import ActionButton from '@/components/ui/ActionButton.vue'
import { useAppStore } from '@/stores/core/AppStore'

interface Props {
  taskId: string
  isZh: boolean
}

const props = defineProps<Props>()

const appStore = useAppStore()
const isZh = computed(() => props.isZh || appStore.language === 'zh')

// 信号统计数据
const signalStats = reactive({
  todaySignals: 15,
  buySignals: 10,
  sellSignals: 5,
  accuracy: 62.5
})

// 最新信号列表
const latestSignals = ref([
  { code: '000001.SZ', name: '平安银行', type: 'buy', strength: 0.85, time: '09:35:12' },
  { code: '600000.SH', name: '浦发银行', type: 'buy', strength: 0.72, time: '09:42:33' },
  { code: '000002.SZ', name: '万科A', type: 'sell', strength: 0.68, time: '10:15:45' },
  { code: '600036.SH', name: '招商银行', type: 'buy', strength: 0.91, time: '10:28:18' },
  { code: '601318.SH', name: '中国平安', type: 'sell', strength: 0.55, time: '11:05:22' }
])

const isGenerating = ref(false)

const generateSignals = async () => {
  isGenerating.value = true
  console.log('Generating signals for task:', props.taskId)
  setTimeout(() => {
    isGenerating.value = false
  }, 2000)
}

const exportSignals = () => {
  console.log('Exporting signals...')
}
</script>

<style scoped lang="scss">
@import '../styles/_variables.scss';

.signal-generation-page {
  --accent-blue: #2962ff;
  --color-up: #ef5350;
  --color-down: #26a69a;
  --accent-red: #ef5350;
  --accent-green: #26a69a;
  --border-color: #2a2e39;

  width: 100%;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.page-subtitle {
  font-size: 14px;
  color: var(--text-secondary);
  margin-bottom: 24px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  padding: 16px;
  background: var(--bg-secondary);
  border-radius: 6px;
  border: 1px solid var(--border-color);
}

.stat-label {
  font-size: 12px;
  color: var(--text-primary);
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  gap: 6px;

  .icon-xs {
    width: 16px;
    height: 16px;
    flex-shrink: 0;
  }
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 4px;

  &.positive {
    color: var(--accent-red);
  }

  &.negative {
    color: var(--accent-green);
  }
}

.stat-change {
  font-size: 11px;
  color: var(--text-secondary);
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

.status-badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 3px;
  font-size: 11px;
  font-weight: 500;

  &.pass {
    background: rgba(239, 83, 80, 0.2);
    color: var(--accent-red);
  }

  &.fail {
    background: rgba(38, 166, 154, 0.2);
    color: var(--accent-green);
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

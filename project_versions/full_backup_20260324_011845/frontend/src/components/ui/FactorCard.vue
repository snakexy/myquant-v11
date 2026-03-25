<template>
  <div :class="['factor-card', status, colorClass, sizeClass]">
    <template v-if="size === 'large'">
      <div class="factor-card-rank">#{{ rank }}</div>
      <div class="factor-card-name">{{ name }}</div>
      <div class="factor-card-metrics">
        <div class="metric">
          <span class="metric-label">IC</span>
          <span :class="['metric-value', { positive: ic > 0.03, negative: ic < 0 }]">
            {{ ic.toFixed(3) }}
          </span>
        </div>
        <div class="metric">
          <span class="metric-label">IR</span>
          <span :class="['metric-value', { positive: ir > 0.5, negative: ir < 0 }]">
            {{ ir.toFixed(2) }}
          </span>
        </div>
        <div class="metric">
          <span class="metric-label">t</span>
          <span :class="['metric-value', { positive: tStat > 2 }]">
            {{ tStat.toFixed(1) }}
          </span>
        </div>
      </div>
      <div :class="['factor-card-status', status]">
        {{ status === 'pass' ? '通过' : '失败' }}
      </div>
    </template>
    <template v-else>
      <div class="factor-card-small-content">
        <span class="factor-card-rank-small">#{{ rank }}</span>
        <span class="factor-card-name-small">{{ name }}</span>
        <span :class="['factor-card-ic-small', { positive: ic > 0.03, negative: ic < 0 }]">
          IC {{ ic.toFixed(3) }}
        </span>
        <span :class="['factor-card-status-small', status]">
          {{ status === 'pass' ? '通过' : '失败' }}
        </span>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  rank?: number
  name: string
  ic: number
  ir: number
  tStat: number
  status: 'pass' | 'fail'
  size?: 'large' | 'small'
}

const props = withDefaults(defineProps<Props>(), {
  rank: 0,
  size: 'large'
})

const sizeClass = computed(() => `factor-card-${props.size}`)

// 根据因子名称判断颜色类型
const colorClass = computed(() => {
  const name = props.name.toLowerCase()
  if (name.includes('momentum') || name.includes('return') || name.includes('ma') || name.includes('roc') || name.includes('trend')) {
    return 'factor-momentum'
  }
  if (name.includes('volatility') || name.includes('std') || name.includes('var') || name.includes('atr')) {
    return 'factor-volatility'
  }
  if (name.includes('volume') || name.includes('liquidity') || name.includes('turnover') || name.includes('obv')) {
    return 'factor-volume'
  }
  if (name.includes('rsi') || name.includes('macd') || name.includes('boll') || name.includes('kdj') || name.includes('cci') || name.includes('adx') || name.includes('williams')) {
    return 'factor-technical'
  }
  if (name.startsWith('alpha158') || name.startsWith('alpha360')) {
    return 'factor-alpha'
  }
  return 'factor-other'
})
</script>

<style scoped>
/* 大尺寸卡片 */
.factor-card-large {
  background: var(--bg-secondary, #1e222d);
  border-radius: 8px;
  padding: 12px;
  border: 1px solid var(--border-color, #363a45);
  position: relative;
  transition: transform 0.2s, box-shadow 0.2s;
}

.factor-card-large:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

/* 小尺寸卡片 */
.factor-card-small {
  background: var(--bg-secondary, #1e222d);
  border-radius: 4px;
  padding: 6px 10px;
  border: 1px solid var(--border-color, #363a45);
  transition: background 0.2s;
}

.factor-card-small:hover {
  background: var(--bg-tertiary, #2a2f3d);
}

.factor-card.pass {
  border-left: 3px solid #ef4444;
}

.factor-card.fail {
  border-left: 3px solid #10b981;
  opacity: 0.7;
}

/* 因子类型颜色边框 */
.factor-card.factor-momentum {
  border-left-color: #10b981 !important;
}
.factor-card.factor-volatility {
  border-left-color: #f97316 !important;
}
.factor-card.factor-volume {
  border-left-color: #3b82f6 !important;
}
.factor-card.factor-technical {
  border-left-color: #8b5cf6 !important;
}
.factor-card.factor-alpha {
  border-left-color: #ef4444 !important;
}
.factor-card.factor-other {
  border-left-color: #6b7280 !important;
}

/* 大卡片样式 */
.factor-card-rank {
  position: absolute;
  top: 8px;
  right: 8px;
  font-size: 10px;
  color: var(--text-secondary, #9ca3af);
  font-weight: 600;
}

.factor-card-name {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-primary, #e5e7eb);
  margin-bottom: 8px;
  margin-right: 24px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.factor-card-metrics {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}

.metric {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.metric-label {
  font-size: 9px;
  color: var(--text-secondary, #9ca3af);
  text-transform: uppercase;
}

.metric-value {
  font-size: 14px;
  font-weight: 700;
  color: var(--text-primary, #e5e7eb);
}

.metric-value.positive {
  color: #ef4444;
}

.metric-value.negative {
  color: #10b981;
}

.factor-card-status {
  text-align: center;
  font-size: 10px;
  font-weight: 600;
  padding: 4px 8px;
  border-radius: 4px;
  text-transform: uppercase;
}

.factor-card-status.pass {
  background: rgba(239, 68, 68, 0.2);
  color: #ef4444;
}

.factor-card-status.fail {
  background: rgba(16, 185, 129, 0.2);
  color: #10b981;
}

/* 小卡片样式 */
.factor-card-small-content {
  display: flex;
  align-items: center;
  gap: 8px;
}

.factor-card-rank-small {
  font-size: 9px;
  color: var(--text-secondary, #9ca3af);
  font-weight: 600;
  min-width: 20px;
}

.factor-card-name-small {
  font-size: 11px;
  font-weight: 500;
  color: var(--text-primary, #e5e7eb);
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.factor-card-ic-small {
  font-size: 10px;
  font-weight: 600;
  color: var(--text-secondary, #9ca3af);
}

.factor-card-ic-small.positive {
  color: #ef4444;
}

.factor-card-ic-small.negative {
  color: #10b981;
}

.factor-card-status-small {
  font-size: 9px;
  font-weight: 600;
  padding: 2px 6px;
  border-radius: 3px;
  text-transform: uppercase;
}

.factor-card-status-small.pass {
  background: rgba(239, 68, 68, 0.2);
  color: #ef4444;
}

.factor-card-status-small.fail {
  background: rgba(16, 185, 129, 0.2);
  color: #10b981;
}
</style>

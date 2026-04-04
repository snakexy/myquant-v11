<template>
  <div class="chart-card">
    <div class="chart-header">
      <div class="chart-title">
        <svg class="icon-md" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M12 2L2 7l10 5 10-5-10-5z"></path>
          <path d="M2 17l10 5 10-5"></path>
          <path d="M2 12l10 5 10-5"></path>
        </svg>
        {{ title }}
      </div>
    </div>
    <div class="chart-content">
      <div class="h-bar-chart-container">
        <template v-for="(item, idx) in data" :key="idx">
          <!-- 实际值 -->
          <div class="h-bar-item">
            <span class="h-bar-label">
              {{ item.name }}
              <span class="trend-hint" :title="item.higherIsBetter ? '越高越好' : '越低越好'">
                <!-- 箭头向上代表 value > benchmark，箭头向下代表 value < benchmark -->
                <!-- 红色代表比基准好，绿色代表比基准差 -->
                <svg v-if="isAboveBenchmark(item)" :class="['trend-icon', isBetterThanBenchmark(item) ? 'up-better' : 'up-worse']" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <polyline points="18 15 12 9 6 15"></polyline>
                </svg>
                <svg v-else :class="['trend-icon', isBetterThanBenchmark(item) ? 'down-better' : 'down-worse']" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <polyline points="6 9 12 15 18 9"></polyline>
                </svg>
              </span>
            </span>
            <div class="h-bar-track">
              <div
                class="h-bar-fill"
                :style="{
                  width: getBarWidth(item.value, item.max),
                  background: item.color || '#2962ff'
                }"
              ></div>
            </div>
            <span class="h-bar-value">{{ formatValue(item.value) }}</span>
          </div>
          <!-- 基准值 -->
          <div class="h-bar-item benchmark">
            <span class="h-bar-label">{{ benchmarkLabel }}</span>
            <div class="h-bar-track">
              <div
                class="h-bar-fill benchmark-fill"
                :style="{ width: getBarWidth(item.benchmark, item.max) }"
              ></div>
            </div>
            <span class="h-bar-value">{{ formatValue(item.benchmark) }}</span>
          </div>
          <!-- 间隔 -->
          <div v-if="idx < data.length - 1" class="h-bar-gap"></div>
        </template>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface RiskIndicator {
  name: string
  value: number
  benchmark: number
  max?: number
  color?: string
  higherIsBetter?: boolean
}

interface Props {
  title?: string
  data?: RiskIndicator[]
  benchmarkLabel?: string
}

const props = withDefaults(defineProps<Props>(), {
  title: '风险指标对比',
  data: () => [
    { name: '波动率', value: 15.2, benchmark: 17.2, max: 25, color: '#2962ff', higherIsBetter: false },
    { name: '最大回撤', value: 12.5, benchmark: 15.8, max: 25, color: '#ff9800', higherIsBetter: false }
  ],
  benchmarkLabel: '基准'
})

// 判断是否比基准好
const isBetterThanBenchmark = (item: RiskIndicator): boolean => {
  if (item.higherIsBetter) {
    return item.value > item.benchmark
  } else {
    return item.value < item.benchmark
  }
}

// 判断箭头方向：向上代表 value > benchmark
const isAboveBenchmark = (item: RiskIndicator): boolean => {
  return item.value > item.benchmark
}

// 计算进度条宽度
const getBarWidth = (value: number, max: number = 100): string => {
  if (!value && value !== 0) return '0%'
  const percentage = Math.min((value / max) * 100, 100)
  return `${percentage}%`
}

// 格式化数值
const formatValue = (value: number): string => {
  if (value === undefined || value === null) return '-'
  return value.toFixed(1) + '%'
}
</script>

<style lang="scss" scoped>
.chart-card {
  background: var(--bg-secondary, #1e222d);
  border: 1px solid var(--border-color, #2a2e39);
  border-radius: 8px;
  padding: 20px;
  display: flex;
  flex-direction: column;
  width: 100%;
}

.chart-header {
  flex-shrink: 0;
  padding-bottom: 12px;
}

.chart-title {
  font-size: 13px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
}

.icon-md {
  width: 18px;
  height: 18px;
  color: #ff9800;
}

.chart-content {
  flex: 1;
  min-height: 120px;
}

.h-bar-chart-container {
  padding-top: 8px;
}

.h-bar-item {
  display: flex;
  align-items: center;
  gap: 10px;

  &.benchmark {
    .h-bar-label {
      color: #787b86;
      font-weight: 400;
    }
    .h-bar-value {
      color: #787b86;
    }
  }
}

.h-bar-label {
  min-width: 70px;
  font-size: 12px;
  color: #d1d4dc;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 2px;
}

.trend-hint {
  display: inline-flex;
  align-items: center;
  cursor: help;

  .trend-icon {
    width: 12px;
    height: 12px;

    &.up-better {
      color: #ef5350;
    }

    &.up-worse {
      color: #4caf50;
    }

    &.down-better {
      color: #ef5350;
    }

    &.down-worse {
      color: #4caf50;
    }
  }
}

.h-bar-track {
  flex: 1;
  height: 6px;
  background: #2a2e39;
  border-radius: 3px;
  overflow: hidden;
}

.h-bar-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.3s ease;

  &.benchmark-fill {
    background: #787b86 !important;
  }
}

.h-bar-value {
  min-width: 50px;
  text-align: right;
  font-size: 12px;
  color: #d1d4dc;
  font-weight: 500;
}

.h-bar-gap {
  height: 16px;
}
</style>

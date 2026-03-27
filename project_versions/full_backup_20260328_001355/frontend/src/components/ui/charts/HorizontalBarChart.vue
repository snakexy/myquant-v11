<template>
  <div class="h-bar-chart-container">
    <div v-if="title" class="chart-header">
      <div class="chart-title">
        <svg class="icon-md" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M12 2L2 7l10 5 10-5-10-5z"></path>
          <path d="M2 17l10 5 10-5"></path>
          <path d="M2 12l10 5 10-5"></path>
        </svg>
        {{ title }}
      </div>
    </div>
    <div class="h-bar-chart">
      <template v-for="(item, idx) in data" :key="idx">
        <!-- 实际值 -->
        <div class="h-bar-item">
          <span class="h-bar-label">
            {{ item.name }}
            <span class="trend-hint" :title="item.higherIsBetter ? '越高越好' : '越低越好'">
              <svg v-if="item.higherIsBetter" class="trend-icon up" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="18 15 12 9 6 15"></polyline>
              </svg>
              <svg v-else class="trend-icon down" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="6 9 12 15 18 9"></polyline>
              </svg>
            </span>
          </span>
          <div class="h-bar-track">
            <div
              class="h-bar-fill"
              :style="{
                width: getBarWidth(item.value, item.max),
                background: getBarColor(item)
              }"
            ></div>
          </div>
          <span class="h-bar-value">{{ formatValue(item) }}</span>
        </div>
        <!-- 基准值 -->
        <div class="h-bar-item benchmark">
          <span class="h-bar-label">基准</span>
          <div class="h-bar-track">
            <div
              class="h-bar-fill benchmark-fill"
              :style="{ width: getBarWidth(item.benchmark, item.max) }"
            ></div>
          </div>
          <span class="h-bar-value">{{ formatBenchmark(item) }}</span>
        </div>
        <!-- 间隔 -->
        <div v-if="idx < data.length - 1" class="h-bar-gap"></div>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
interface RiskIndicator {
  name: string
  value: number
  benchmark: number
  max?: number  // 用于计算进度条宽度
  color?: string  // 指标颜色
  higherIsBetter?: boolean  // true=越高越好，false=越低越好
}

interface Props {
  title?: string
  data?: RiskIndicator[]
}

const props = withDefaults(defineProps<Props>(), {
  data: () => [
    { name: '波动率', value: 15.2, benchmark: 17.2, max: 25, color: '#2962ff', higherIsBetter: false },
    { name: '最大回撤', value: 12.5, benchmark: 15.8, max: 25, color: '#ff9800', higherIsBetter: false }
  ]
})

// 计算进度条宽度
const getBarWidth = (value: number, max: number = 100): string => {
  const percentage = Math.min((Math.abs(value) / max) * 100, 100)
  return `${percentage}%`
}

// 获取进度条颜色
const getBarColor = (item: RiskIndicator): string => {
  return item.color || '#2962ff'
}

// 格式化实际值
const formatValue = (item: RiskIndicator): string => {
  const val = item.value
  if (item.name.includes('比率')) {
    return val.toFixed(2)
  }
  return val.toFixed(1) + '%'
}

// 格式化基准值
const formatBenchmark = (item: RiskIndicator): string => {
  if (item.name.includes('比率')) {
    return item.benchmark.toFixed(2)
  }
  return item.benchmark.toFixed(1) + '%'
}
</script>

<style lang="scss" scoped>
.h-bar-chart-container {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
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

.h-bar-chart {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.h-bar-item {
  display: flex;
  align-items: center;
  gap: 8px;

  &.benchmark {
    margin-top: 4px;
  }
}

.h-bar-label {
  min-width: 55px;
  font-size: 11px;
  color: #787b86;
  display: flex;
  align-items: center;
  gap: 4px;
}

.trend-hint {
  display: inline-flex;
  align-items: center;
  cursor: help;
}

.trend-icon {
  width: 12px;
  height: 12px;

  &.up {
    color: #ef5350;  // 红色=好（越高越好）
  }

  &.down {
    color: #ef5350;  // 红色=好（越低越好）
  }
}

.benchmark .h-bar-label {
  font-size: 10px;
  color: #595c66;
}

.h-bar-track {
  flex: 1;
  height: 6px;
  background: #1e222d;
  border-radius: 3px;
  overflow: hidden;
}

.h-bar-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.3s ease;

  &.benchmark-fill {
    background: #787b86;
  }
}

.h-bar-value {
  min-width: 55px;
  text-align: right;
  font-size: 11px;
  color: #d1d4dc;

  &.positive {
    color: #ef5350;  // 红色=好
  }

  &.negative {
    color: #26a69a;  // 绿色=差
  }
}

.benchmark .h-bar-value {
  font-size: 10px;
  color: #787b86;
}

.h-bar-gap {
  height: 12px;
}
</style>

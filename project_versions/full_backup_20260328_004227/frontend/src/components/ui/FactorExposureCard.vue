<template>
  <div class="factor-card">
    <div class="panel-header">
      <div class="panel-title">
        <svg class="icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
          <line x1="3" y1="9" x2="21" y2="9"></line>
          <line x1="9" y1="21" x2="9" y2="9"></line>
        </svg>
        因子暴露分析
      </div>
    </div>
    <div class="factor-exposures">
      <div v-for="item in factors" :key="item.name" class="factor-item">
        <div class="factor-name">{{ item.name }}</div>
        <div class="factor-bar-container">
          <div class="factor-bar negative">
            <div
              class="bar-fill"
              :style="{
                width: Math.max(0, -item.value) * 100 + '%',
                background: getNegativeGradient(item.value)
              }"
            ></div>
          </div>
          <div class="factor-center"></div>
          <div class="factor-bar positive">
            <div
              class="bar-fill"
              :style="{
                width: Math.max(0, item.value) * 100 + '%',
                background: getPositiveGradient(item.value)
              }"
            ></div>
          </div>
        </div>
        <div class="factor-value" :class="{ warning: Math.abs(item.value) > 0.5 }">
          {{ item.value > 0 ? '+' : '' }}{{ item.value.toFixed(2) }}
        </div>
      </div>
    </div>
    <div class="factor-legend">
      <span class="legend-item">
        <span class="legend-dot negative"></span>
        负向
      </span>
      <span class="legend-item">
        <span class="legend-dot positive"></span>
        正向
      </span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface FactorItem {
  name: string
  value: number
}

interface Props {
  factors?: FactorItem[]
}

const props = withDefaults(defineProps<Props>(), {
  factors: () => [
    { name: '市值', value: 0.35 },
    { name: '价值', value: -0.22 },
    { name: '动量', value: 0.18 },
    { name: '质量', value: -0.15 },
    { name: '波动', value: 0.28 }
  ]
})

// 负向渐变 - 从中间(右边)到边缘(左边): 浅绿 -> 深绿（负向=差=绿色）
// 由于进度条从右往左延伸，渐变方向也应该是从右到左
const getNegativeGradient = (value: number) => {
  const absValue = Math.abs(value)
  if (absValue < 0.1) return 'transparent'

  if (absValue < 0.3) {
    return `linear-gradient(90deg, #26a69a 0%, #4db6ac 100%)`
  } else if (absValue < 0.6) {
    return `linear-gradient(90deg, #00897b 0%, #26a69a 100%)`
  } else {
    return `linear-gradient(90deg, #004d40 0%, #00897b 100%)`
  }
}

// 正向渐变 - 从中间(左边)到边缘(右边): 浅红 -> 深红（正向=好=红色）
const getPositiveGradient = (value: number) => {
  const absValue = Math.abs(value)
  if (absValue < 0.1) return 'transparent'

  if (absValue < 0.3) {
    return `linear-gradient(90deg, #ef5350 0%, #ff8a80 100%)`
  } else if (absValue < 0.6) {
    return `linear-gradient(90deg, #c62828 0%, #ef5350 100%)`
  } else {
    return `linear-gradient(90deg, #8b0000 0%, #c62828 100%)`
  }
}
</script>

<style lang="scss" scoped>
.factor-card {
  background: #1e222d;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid transparent;

  &:hover {
    border-color: transparent !important;
  }

  .panel-header {
    padding: 12px 16px;
    border-bottom: 1px solid #2a2e39;
  }

  .panel-title {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 13px;
    font-weight: 600;
    color: #d1d4dc;
  }

  .icon-sm {
    width: 16px;
    height: 16px;
    color: #2962ff;
  }

  .factor-exposures {
    display: flex;
    flex-direction: column;
    gap: 8px;
    padding: 12px 16px 10px;
  }

  .factor-item {
    display: flex;
    align-items: center;
    gap: 10px;

    .factor-name {
      width: 45px;
      font-size: 11px;
      color: #a0aec0;
      flex-shrink: 0;
    }

    .factor-bar-container {
      flex: 1;
      display: flex;
      align-items: center;
      height: 8px;

      .factor-bar {
        flex: 1;
        height: 4px;
        background: #2a2e39;
        border-radius: 2px;
        overflow: hidden;
        position: relative;

        .bar-fill {
          position: absolute;
          top: 0;
          height: 100%;
          border-radius: 2px;
          transition: width 0.3s ease;
        }
      }

      // 负向进度条：从中间(右边)往左延伸
      .factor-bar.negative {
        .bar-fill {
          right: 0; // 从右边开始
        }
      }

      .factor-center {
        width: 2px;
        height: 4px;
        background: #ffffff;
        opacity: 0.5;
        flex-shrink: 0;
        border-radius: 1px;
      }
    }

    .factor-value {
      width: 40px;
      text-align: right;
      font-size: 11px;
      font-weight: 600;
      color: #d1d4dc;
      flex-shrink: 0;

      &.warning {
        color: #ff9800;
      }
    }
  }

  .factor-legend {
    display: flex;
    justify-content: center;
    gap: 20px;
    padding: 0 16px 12px;

    .legend-item {
      display: flex;
      align-items: center;
      gap: 6px;
      font-size: 10px;
      color: #787b86;

      .legend-dot {
        width: 8px;
        height: 8px;
        border-radius: 2px;

        &.negative {
          background: linear-gradient(90deg, #26a69a, #00897b);
        }

        &.positive {
          background: linear-gradient(90deg, #ef5350, #c62828);
        }
      }
    }
  }
}
</style>

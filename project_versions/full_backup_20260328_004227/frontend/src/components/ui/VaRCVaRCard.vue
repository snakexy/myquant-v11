<template>
  <div class="var-card">
    <div class="panel-header">
      <div class="panel-title">
        <svg class="icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M12 2L2 7l10 5 10-5-10-5z"></path>
          <path d="M2 17l10 5 10-5M2 12l10 5 10-5"></path>
        </svg>
        VaR/CVaR 分析
      </div>
    </div>
    <div class="var-bars">
      <div class="var-bar-item">
        <div class="bar-label">VaR(95%)</div>
        <div class="bar-track">
          <div class="bar-fill var" :style="{ width: varWidth + '%' }"></div>
        </div>
        <div class="bar-value">{{ formattedVaR }}</div>
      </div>
      <div class="var-bar-item">
        <div class="bar-label">CVaR(95%)</div>
        <div class="bar-track">
          <div class="bar-fill cvar" :style="{ width: cvarWidth + '%' }"></div>
        </div>
        <div class="bar-value">{{ formattedCVaR }}</div>
      </div>
    </div>
    <div class="var-interpretation">
      <svg class="icon-xs" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <circle cx="12" cy="12" r="10"></circle>
        <line x1="12" y1="16" x2="12" y2="12"></line>
        <line x1="12" y1="8" x2="12.01" y2="8"></line>
      </svg>
      <span>有95%信心预计最大日损失不超过 {{ formattedVaR }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  var95?: number
  cvar95?: number
}

const props = withDefaults(defineProps<Props>(), {
  var95: 0.02,
  cvar95: 0.035
})

// 计算VaR进度条宽度 (放大500倍显示)
const varWidth = computed(() => Math.min(Math.abs(props.var95) * 500, 100))

// 计算CVaR进度条宽度
const cvarWidth = computed(() => Math.min(Math.abs(props.cvar95) * 500, 100))

// 格式化VaR
const formattedVaR = computed(() => {
  return (props.var95 * 100).toFixed(2) + '%'
})

// 格式化CVaR
const formattedCVaR = computed(() => {
  return (props.cvar95 * 100).toFixed(2) + '%'
})
</script>

<style lang="scss" scoped>
.var-card {
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
    color: #ef5350;
  }

  .var-bars {
    display: flex;
    flex-direction: column;
    gap: 10px;
    padding: 12px 16px;
  }

  .var-bar-item {
    display: flex;
    align-items: center;
    gap: 12px;

    .bar-label {
      width: 70px;
      font-size: 11px;
      color: #a0aec0;
    }

    .bar-track {
      flex: 1;
      height: 8px;
      background: #2a2e39;
      border-radius: 4px;
      overflow: hidden;

      .bar-fill {
        height: 100%;
        border-radius: 4px;
        transition: width 0.3s ease;

        &.var {
          background: linear-gradient(90deg, #ef5350, #ff8a80);
        }

        &.cvar {
          background: linear-gradient(90deg, #f7931a, #ffb74d);
        }
      }
    }

    .bar-value {
      min-width: 50px;
      text-align: right;
      font-size: 12px;
      font-weight: 600;
      color: #d1d4dc;
    }
  }

  .var-interpretation {
    display: flex;
    align-items: flex-start;
    gap: 8px;
    margin: 0 16px 16px;
    padding: 10px;
    background: #2a2e39;
    border-radius: 6px;

    .icon-xs {
      flex-shrink: 0;
      width: 14px;
      height: 14px;
      color: #ff9800;
      margin-top: 2px;
    }

    span {
      font-size: 11px;
      color: #a0aec0;
      line-height: 1.5;
    }
  }
}
</style>

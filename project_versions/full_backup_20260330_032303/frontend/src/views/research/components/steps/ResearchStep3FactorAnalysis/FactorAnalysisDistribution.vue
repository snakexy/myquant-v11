<template>
  <div class="factor-analysis-distribution">
    <!-- 配置面板 -->
    <div class="config-panel">
      <div class="config-header">
        <h3 class="config-title">
          <svg class="config-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="3"></circle>
            <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path>
          </svg>
          {{ isZh ? '分布配置' : 'Distribution Configuration' }}
        </h3>
      </div>

      <div class="config-body">
        <!-- 图表类型选择 -->
        <div class="config-section">
          <label class="config-label">{{ isZh ? '图表类型' : 'Chart Types' }}</label>
          <div class="checkbox-group">
            <label class="checkbox-item">
              <input
                type="checkbox"
                v-model="config.histogram"
                @change="onConfigChange"
              />
              <span class="checkbox-custom"></span>
              <span class="checkbox-label">{{ isZh ? '直方图' : 'Histogram' }}</span>
            </label>
            <label class="checkbox-item">
              <input
                type="checkbox"
                v-model="config.qqPlot"
                @change="onConfigChange"
              />
              <span class="checkbox-custom"></span>
              <span class="checkbox-label">QQ Plot</span>
            </label>
            <label class="checkbox-item">
              <input
                type="checkbox"
                v-model="config.boxPlot"
                @change="onConfigChange"
              />
              <span class="checkbox-custom"></span>
              <span class="checkbox-label">{{ isZh ? '箱线图' : 'Box Plot' }}</span>
            </label>
          </div>
        </div>

        <!-- 直方图参数 -->
        <div v-if="config.histogram" class="config-section">
          <label class="config-label">{{ isZh ? '直方图参数' : 'Histogram Parameters' }}</label>
          <div class="param-row">
            <span class="param-label">{{ isZh ? '分组数' : 'Bins' }}</span>
            <input
              type="number"
              v-model.number="config.bins"
              min="10"
              max="200"
              class="param-input"
              @change="onConfigChange"
            />
          </div>
        </div>
      </div>
    </div>

    <!-- 图表展示区域 -->
    <div class="chart-container">
      <FactorDistributionChart
        v-if="config.histogram || config.qqPlot || config.boxPlot"
        :task-id="taskId"
        :histogram="config.histogram"
        :qq-plot="config.qqPlot"
        :box-plot="config.boxPlot"
        :bins="config.bins"
        :is-zh="isZh"
      />
      <div v-else class="empty-state">
        <svg class="empty-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <line x1="18" y1="20" x2="18" y2="10"></line>
          <line x1="12" y1="20" x2="12" y2="4"></line>
          <line x1="6" y1="20" x2="6" y2="14"></line>
        </svg>
        <p class="empty-text">{{ isZh ? '请选择至少一种图表类型' : 'Please select at least one chart type' }}</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import FactorDistributionChart from '../../../FactorDistributionChart.vue'
import { useAppStore } from '@/stores/core/AppStore'

interface Props {
  taskId: string
  isZh: boolean
}

const props = defineProps<Props>()
const appStore = useAppStore()
const isZh = computed(() => props.isZh || appStore.language === 'zh')

// 分布配置
const config = reactive({
  histogram: true,
  qqPlot: true,
  boxPlot: false,
  bins: 50
})

// 配置变化处理
const onConfigChange = () => {
  console.log('Distribution config changed:', config)
}
</script>

<style scoped lang="scss">
.factor-analysis-distribution {
  /* CSS 变量定义 */
  --bg-primary: #131722;
  --bg-secondary: #1e222d;
  --bg-tertiary: #2a2e39;
  --text-primary: #d1d4dc;
  --text-secondary: #787b86;
  --accent-blue: #2962ff;
  --border-color: #2a2e39;

  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.config-panel {
  background: var(--bg-secondary);
  border-radius: 6px;
  border: 1px solid var(--border-color);
  overflow: hidden;
}

.config-header {
  padding: 16px;
  border-bottom: 1px solid var(--border-color);
}

.config-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.config-icon {
  width: 16px;
  height: 16px;
  color: var(--text-secondary);
}

.config-body {
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.config-section {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.config-label {
  font-size: 12px;
  font-weight: 500;
  color: var(--text-secondary);
}

.checkbox-group {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
}

.checkbox-item {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  user-select: none;

  input[type="checkbox"] {
    position: absolute;
    opacity: 0;
    cursor: pointer;
    height: 0;
    width: 0;
  }

  .checkbox-custom {
    position: relative;
    width: 16px;
    height: 16px;
    background: var(--bg-tertiary);
    border: 2px solid #3a3f4b;
    border-radius: 3px;
    transition: all 0.2s;
    flex-shrink: 0;

    &::after {
      content: '';
      position: absolute;
      display: none;
      left: 4px;
      top: 1px;
      width: 4px;
      height: 8px;
      border: solid var(--accent-blue);
      border-width: 0 2px 2px 0;
      transform: rotate(45deg);
    }
  }

  input:checked ~ .checkbox-custom {
    background: var(--accent-blue);
    border-color: var(--accent-blue);

    &::after {
      display: block;
    }
  }

  input:hover ~ .checkbox-custom {
    border-color: var(--accent-blue);
  }

  .checkbox-label {
    font-size: 13px;
    color: var(--text-primary);
  }
}

.param-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.param-label {
  min-width: 80px;
  font-size: 12px;
  color: var(--text-secondary);
}

.param-input {
  width: 100px;
  padding: 6px 10px;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  border-radius: 4px;
  color: var(--text-primary);
  font-size: 13px;

  &:focus {
    outline: none;
    border-color: var(--accent-blue);
  }

  /* 去除数字输入框的默认箭头 */
  &::-webkit-inner-spin-button,
  &::-webkit-outer-spin-button {
    -webkit-appearance: none;
    margin: 0;
  }

  &[type="number"] {
    -moz-appearance: textfield;
  }
}

.chart-container {
  background: var(--bg-secondary);
  border-radius: 6px;
  border: 1px solid var(--border-color);
  min-height: 400px;
  overflow: hidden;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  color: var(--text-secondary);
}

.empty-icon {
  width: 64px;
  height: 64px;
  margin-bottom: 16px;
  opacity: 0.3;
}

.empty-text {
  font-size: 13px;
  color: var(--text-secondary);
  margin: 0;
}
</style>

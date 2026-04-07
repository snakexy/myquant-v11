<template>
  <div class="slider-demo-page">
    <div class="page-header">
      <h1>滑杆组件演示</h1>
      <p class="page-description">展示统一的滑杆调节参数效果</p>
    </div>

    <div class="demo-container">
      <!-- 基础滑杆 -->
      <div class="demo-section">
        <h2 class="section-title">基础滑杆</h2>
        <div class="demo-item">
          <h3>默认滑杆</h3>
          <UniSlider
            v-model="basicValue"
            :min="0"
            :max="100"
            label="数值调节"
            unit="%"
          />
          <p>当前值: {{ basicValue }}</p>
        </div>

        <div class="demo-item">
          <h3>带刻度的滑杆</h3>
          <UniSlider
            v-model="markedValue"
            :min="0"
            :max="100"
            :marks="marks"
            label="带刻度"
            unit="%"
            show-range-labels
          />
          <p>当前值: {{ markedValue }}</p>
        </div>

        <div class="demo-item">
          <h3>可编辑的滑杆</h3>
          <UniSlider
            v-model="editableValue"
            :min="0"
            :max="1000"
            :step="10"
            label="投资金额"
            unit="元"
            :editable="true"
            :format="formatCurrency"
          />
          <p>当前值: {{ formatCurrency(editableValue) }}</p>
        </div>
      </div>

      <!-- 尺寸变化 -->
      <div class="demo-section">
        <h2 class="section-title">尺寸变化</h2>
        <div class="demo-item">
          <h3>小型滑杆</h3>
          <UniSlider
            v-model="smallValue"
            size="small"
            label="风险系数"
            :min="0"
            :max="1"
            :step="0.01"
          />
        </div>

        <div class="demo-item">
          <h3>大型滑杆</h3>
          <UniSlider
            v-model="largeValue"
            size="large"
            label="收益率目标"
            unit="%"
            :min="-50"
            :max="100"
          />
        </div>
      </div>

      <!-- 颜色变体 -->
      <div class="demo-section">
        <h2 class="section-title">颜色变体</h2>
        <div class="demo-item">
          <h3>成功状态</h3>
          <UniSlider
            v-model="successValue"
            variant="success"
            label="成功率"
            unit="%"
            :min="0"
            :max="100"
          />
        </div>

        <div class="demo-item">
          <h3>警告状态</h3>
          <UniSlider
            v-model="warningValue"
            variant="warning"
            label="风险等级"
            :min="1"
            :max="10"
          />
        </div>

        <div class="demo-item">
          <h3>危险状态</h3>
          <UniSlider
            v-model="dangerValue"
            variant="danger"
            label="损失率"
            unit="%"
            :min="0"
            :max="100"
          />
        </div>

        <div class="demo-item">
          <h3>市场上涨</h3>
          <UniSlider
            v-model="marketRiseValue"
            variant="market-rise"
            label="涨幅"
            unit="%"
            :min="0"
            :max="20"
          />
        </div>

        <div class="demo-item">
          <h3>市场下跌</h3>
          <UniSlider
            v-model="marketFallValue"
            variant="market-fall"
            label="跌幅"
            unit="%"
            :min="0"
            :max="20"
          />
        </div>
      </div>

      <!-- 参数配置滑杆 -->
      <div class="demo-section">
        <h2 class="section-title">参数配置示例</h2>
        <div class="parameter-sliders">
          <div class="parameter-slider">
            <div class="parameter-info">
              <div class="parameter-name">止损比例</div>
              <div class="parameter-desc">当亏损达到此比例时自动卖出</div>
            </div>
            <div class="parameter-control">
              <input
                type="range"
                class="parameter-range"
                v-model="stopLoss"
                min="1"
                max="20"
                step="0.5"
              />
              <div class="parameter-value">{{ stopLoss }}%</div>
            </div>
          </div>

          <div class="parameter-slider">
            <div class="parameter-info">
              <div class="parameter-name">持仓天数</div>
              <div class="parameter-desc">策略推荐的最大持仓时间</div>
            </div>
            <div class="parameter-control">
              <input
                type="range"
                class="parameter-range"
                v-model="holdingDays"
                min="1"
                max="60"
                step="1"
              />
              <div class="parameter-value">{{ holdingDays }}天</div>
            </div>
          </div>

          <div class="parameter-slider">
            <div class="parameter-info">
              <div class="parameter-name">仓位比例</div>
              <div class="parameter-desc">单只股票占总资金的比例</div>
            </div>
            <div class="parameter-control">
              <input
                type="range"
                class="parameter-range"
                v-model="positionRatio"
                min="5"
                max="50"
                step="5"
              />
              <div class="parameter-value">{{ positionRatio }}%</div>
            </div>
          </div>

          <div class="parameter-slider">
            <div class="parameter-info">
              <div class="parameter-name">RSI阈值</div>
              <div class="parameter-desc">RSI指标的超买超卖判断阈值</div>
            </div>
            <div class="parameter-control">
              <input
                type="range"
                class="parameter-range"
                v-model="rsiThreshold"
                min="20"
                max="80"
                step="5"
              />
              <div class="parameter-value">{{ rsiThreshold }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import UniSlider from '@/components/ui/UniSlider.vue'

// 基础滑杆值
const basicValue = ref(50)
const markedValue = ref(30)
const editableValue = ref(50000)

// 尺寸
const smallValue = ref(0.5)
const largeValue = ref(20)

// 颜色变体
const successValue = ref(75)
const warningValue = ref(5)
const dangerValue = ref(30)
const marketRiseValue = ref(5)
const marketFallValue = ref(3)

// 参数配置
const stopLoss = ref(5)
const holdingDays = ref(10)
const positionRatio = ref(20)
const rsiThreshold = ref(50)

// 刻度
const marks = ref([
  { value: 0, label: '0%' },
  { value: 25, label: '25%' },
  { value: 50, label: '50%' },
  { value: 75, label: '75%' },
  { value: 100, label: '100%' }
])

// 格式化函数
const formatCurrency = (value: number): string => {
  return `¥${value.toLocaleString()}`
}
</script>

<style scoped>
.slider-demo-page {
  padding: 24px;
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 32px;
  text-align: center;
}

.page-header h1 {
  font-size: 32px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.page-description {
  font-size: 16px;
  color: var(--text-regular);
}

.demo-container {
  display: flex;
  flex-direction: column;
  gap: 40px;
}

.demo-section {
  background: var(--bg-white);
  border-radius: var(--border-radius-lg);
  padding: 24px;
  box-shadow: var(--shadow-sm);
}

.section-title {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 20px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--border-color);
}

.demo-item {
  padding: 20px;
  background: var(--bg-secondary);
  border-radius: var(--border-radius);
  margin-bottom: 16px;
}

.demo-item:last-child {
  margin-bottom: 0;
}

.demo-item h3 {
  font-size: 16px;
  font-weight: 500;
  color: var(--text-primary);
  margin-bottom: 16px;
}

.demo-item p {
  margin-top: 12px;
  font-size: 14px;
  color: var(--text-regular);
}

.parameter-sliders {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
</style>
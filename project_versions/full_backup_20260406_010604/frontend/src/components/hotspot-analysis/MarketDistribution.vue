<template>
  <div class="market-distribution clickable" @click="handleClick">
    <div class="distribution-header">
      <h3 class="distribution-title">
        <i class="fas fa-chart-bar"></i>
        市场涨跌分布
      </h3>
      <span class="distribution-subtitle">全市场股票涨跌幅区间统计</span>
    </div>

    <!-- 市场总览信息 -->
    <div class="market-overview" v-if="marketStats">
      <div class="overview-item">
        <span class="overview-label">成交额</span>
        <span class="overview-value">{{ formatAmount(marketStats.total_amount_yi) }}</span>
      </div>
      <div class="overview-divider"></div>
      <div class="overview-item">
        <span class="overview-label">涨停</span>
        <span class="overview-value limit-up">{{ marketStats.limit_up_count }}</span>
      </div>
      <div class="overview-divider"></div>
      <div class="overview-item">
        <span class="overview-label">跌停</span>
        <span class="overview-value limit-down">{{ marketStats.limit_down_count }}</span>
      </div>
    </div>

    <div class="distribution-content" v-if="distribution">
      <!-- 涨幅分布 -->
      <div class="rise-section">
        <div class="section-title">
          <i class="fas fa-arrow-up text-rise"></i>
          <span>涨幅分布</span>
        </div>

        <div class="bars-container">
          <!-- 涨停 >9% -->
          <div class="bar-item" v-if="distribution.rise_9_plus > 0">
            <div class="bar-label">
              <span class="label-text">涨停</span>
              <span class="label-percent">>9%</span>
            </div>
            <div class="bar-wrapper">
              <div class="bar-fill rise-bar" :style="{ width: getBarWidth(distribution.rise_9_plus) + '%' }"></div>
              <span class="bar-value">{{ distribution.rise_9_plus }}</span>
            </div>
          </div>

          <!-- 涨幅 7-9% -->
          <div class="bar-item" v-if="distribution.rise_7_9 > 0">
            <div class="bar-label">
              <span class="label-text"></span>
              <span class="label-percent">7-9%</span>
            </div>
            <div class="bar-wrapper">
              <div class="bar-fill rise-bar" :style="{ width: getBarWidth(distribution.rise_7_9) + '%' }"></div>
              <span class="bar-value">{{ distribution.rise_7_9 }}</span>
            </div>
          </div>

          <!-- 涨幅 5-7% -->
          <div class="bar-item" v-if="distribution.rise_5_7 > 0">
            <div class="bar-label">
              <span class="label-text"></span>
              <span class="label-percent">5-7%</span>
            </div>
            <div class="bar-wrapper">
              <div class="bar-fill rise-bar" :style="{ width: getBarWidth(distribution.rise_5_7) + '%' }"></div>
              <span class="bar-value">{{ distribution.rise_5_7 }}</span>
            </div>
          </div>

          <!-- 涨幅 3-5% -->
          <div class="bar-item" v-if="distribution.rise_3_5 > 0">
            <div class="bar-label">
              <span class="label-text"></span>
              <span class="label-percent">3-5%</span>
            </div>
            <div class="bar-wrapper">
              <div class="bar-fill rise-bar" :style="{ width: getBarWidth(distribution.rise_3_5) + '%' }"></div>
              <span class="bar-value">{{ distribution.rise_3_5 }}</span>
            </div>
          </div>

          <!-- 涨幅 0-3% -->
          <div class="bar-item" v-if="distribution.rise_0_3 > 0">
            <div class="bar-label">
              <span class="label-text">小涨</span>
              <span class="label-percent">0-3%</span>
            </div>
            <div class="bar-wrapper">
              <div class="bar-fill rise-bar-light" :style="{ width: getBarWidth(distribution.rise_0_3) + '%' }"></div>
              <span class="bar-value">{{ distribution.rise_0_3 }}</span>
            </div>
          </div>
        </div>

        <div class="section-total">
          <span class="total-label">上涨总计:</span>
          <span class="total-value rise">{{ totalRise }}家</span>
        </div>
      </div>

      <!-- 跌幅分布 -->
      <div class="fall-section">
        <div class="section-title">
          <i class="fas fa-arrow-down text-fall"></i>
          <span>跌幅分布</span>
        </div>

        <div class="bars-container">
          <!-- 跌停 >9% -->
          <div class="bar-item" v-if="distribution.fall_9_plus > 0">
            <div class="bar-label">
              <span class="label-text">跌停</span>
              <span class="label-percent">>9%</span>
            </div>
            <div class="bar-wrapper">
              <div class="bar-fill fall-bar-deep" :style="{ width: getBarWidth(distribution.fall_9_plus) + '%' }"></div>
              <span class="bar-value">{{ distribution.fall_9_plus }}</span>
            </div>
          </div>

          <!-- 跌幅 7-9% -->
          <div class="bar-item" v-if="distribution.fall_7_9 > 0">
            <div class="bar-label">
              <span class="label-text"></span>
              <span class="label-percent">7-9%</span>
            </div>
            <div class="bar-wrapper">
              <div class="bar-fill fall-bar" :style="{ width: getBarWidth(distribution.fall_7_9) + '%' }"></div>
              <span class="bar-value">{{ distribution.fall_7_9 }}</span>
            </div>
          </div>

          <!-- 跌幅 5-7% -->
          <div class="bar-item" v-if="distribution.fall_5_7 > 0">
            <div class="bar-label">
              <span class="label-text"></span>
              <span class="label-percent">5-7%</span>
            </div>
            <div class="bar-wrapper">
              <div class="bar-fill fall-bar" :style="{ width: getBarWidth(distribution.fall_5_7) + '%' }"></div>
              <span class="bar-value">{{ distribution.fall_5_7 }}</span>
            </div>
          </div>

          <!-- 跌幅 3-5% -->
          <div class="bar-item" v-if="distribution.fall_3_5 > 0">
            <div class="bar-label">
              <span class="label-text"></span>
              <span class="label-percent">3-5%</span>
            </div>
            <div class="bar-wrapper">
              <div class="bar-fill fall-bar" :style="{ width: getBarWidth(distribution.fall_3_5) + '%' }"></div>
              <span class="bar-value">{{ distribution.fall_3_5 }}</span>
            </div>
          </div>

          <!-- 跌幅 0-3% -->
          <div class="bar-item" v-if="distribution.fall_0_3 > 0">
            <div class="bar-label">
              <span class="label-text">小跌</span>
              <span class="label-percent">0-3%</span>
            </div>
            <div class="bar-wrapper">
              <div class="bar-fill fall-bar-light" :style="{ width: getBarWidth(distribution.fall_0_3) + '%' }"></div>
              <span class="bar-value">{{ distribution.fall_0_3 }}</span>
            </div>
          </div>
        </div>

        <div class="section-total">
          <span class="total-label">下跌总计:</span>
          <span class="total-value fall">{{ totalFall }}家</span>
        </div>
      </div>
    </div>

    <!-- 加载状态 -->
    <div class="loading-state" v-else>
      <i class="fas fa-spinner fa-spin"></i>
      <span>加载中...</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Distribution {
  rise_0_3: number
  rise_3_5: number
  rise_5_7: number
  rise_7_9: number
  rise_9_plus: number
  fall_0_3: number
  fall_3_5: number
  fall_5_7: number
  fall_7_9: number
  fall_9_plus: number
}

interface MarketStats {
  total_amount_yi: number
  limit_up_count: number
  limit_down_count: number
}

interface Props {
  distribution?: Distribution
  marketStats?: MarketStats
}

const props = defineProps<Props>()

// 定义emit
const emit = defineEmits<{
  (e: 'showMarketKline'): void
}>()

// 处理点击事件
const handleClick = () => {
  emit('showMarketKline')
}

// 计算总上涨和下跌家数（排除涨停跌停）
const totalRise = computed(() => {
  if (!props.distribution) return 0
  // 不包含涨停（rise_9_plus）
  return props.distribution.rise_0_3 +
         props.distribution.rise_3_5 +
         props.distribution.rise_5_7 +
         props.distribution.rise_7_9
})

const totalFall = computed(() => {
  if (!props.distribution) return 0
  // 不包含跌停（fall_9_plus）
  return props.distribution.fall_0_3 +
         props.distribution.fall_3_5 +
         props.distribution.fall_5_7 +
         props.distribution.fall_7_9
})

// 计算最大值用于条形图宽度比例
const maxCount = computed(() => {
  if (!props.distribution) return 1
  const allValues = [
    props.distribution.rise_0_3,
    props.distribution.rise_3_5,
    props.distribution.rise_5_7,
    props.distribution.rise_7_9,
    props.distribution.rise_9_plus,
    props.distribution.fall_0_3,
    props.distribution.fall_3_5,
    props.distribution.fall_5_7,
    props.distribution.fall_7_9,
    props.distribution.fall_9_plus
  ]
  return Math.max(...allValues, 1)
})

// 获取条形图宽度百分比
const getBarWidth = (value: number) => {
  if (value === 0) return 0
  return (value / maxCount.value) * 100
}

// 格式化成交额
const formatAmount = (amount: number) => {
  if (amount >= 10000) {
    return (amount / 10000).toFixed(2) + '万亿'
  }
  return amount.toFixed(2) + '亿'
}
</script>

<style scoped>
.market-distribution {
  background: var(--card-bg);
  border-radius: 8px;
  padding: 16px;
  height: 100%;
  transition: all 0.3s ease;
  cursor: pointer;
}

.market-distribution:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
  border: 1px solid rgba(239, 68, 68, 0.3);
}

.market-distribution.clickable:active {
  transform: translateY(0);
}

.distribution-header {
  margin-bottom: 12px;
}

.distribution-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 4px 0;
  display: flex;
  align-items: center;
  gap: 8px;
}

.distribution-subtitle {
  font-size: 12px;
  color: var(--text-secondary);
}

/* 市场总览 */
.market-overview {
  display: flex;
  align-items: center;
  justify-content: space-around;
  padding: 12px 16px;
  background: linear-gradient(135deg, rgba(239, 68, 68, 0.05) 0%, rgba(34, 197, 94, 0.05) 100%);
  border-radius: 6px;
  margin-bottom: 16px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.overview-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.overview-label {
  font-size: 11px;
  color: var(--text-secondary);
  font-weight: 500;
}

.overview-value {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-primary);
}

.overview-value.limit-up {
  color: #ef4444;
}

.overview-value.limit-down {
  color: #22c55e;
}

.overview-divider {
  width: 1px;
  height: 30px;
  background: var(--border-color);
  opacity: 0.5;
}

.distribution-content {
  display: flex;
  gap: 16px;
  height: calc(100% - 120px);
}

.rise-section,
.fall-section {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.section-title {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-primary);
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.bars-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 6px;
  overflow-y: auto;
}

.bar-item {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.bar-label {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 11px;
  color: var(--text-secondary);
}

.label-text {
  font-weight: 500;
}

.label-percent {
  font-size: 10px;
  opacity: 0.8;
}

.bar-wrapper {
  display: flex;
  align-items: center;
  gap: 6px;
  height: 20px;
}

.bar-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.3s ease;
  min-width: 2px;
}

.rise-bar {
  background: linear-gradient(90deg, #ef4444 0%, #dc2626 100%);
}

.rise-bar-light {
  background: linear-gradient(90deg, #fca5a5 0%, #f87171 100%);
}

.fall-bar {
  background: linear-gradient(90deg, #22c55e 0%, #16a34a 100%);
}

.fall-bar-light {
  background: linear-gradient(90deg, #86efac 0%, #4ade80 100%);
}

.fall-bar-deep {
  background: linear-gradient(90deg, #15803d 0%, #166534 100%);
}

.bar-value {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-primary);
  min-width: 30px;
  text-align: right;
}

.section-total {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid var(--border-color);
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 13px;
}

.total-label {
  color: var(--text-secondary);
}

.total-value {
  font-weight: 600;
  font-size: 14px;
}

.total-value.rise {
  color: #ef4444;
}

.total-value.fall {
  color: #22c55e;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 200px;
  gap: 12px;
  color: var(--text-secondary);
}

.text-rise {
  color: #ef4444;
}

.text-fall {
  color: #22c55e;
}
</style>

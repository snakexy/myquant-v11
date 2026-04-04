<!--
  技术指标集成示例

  展示如何使用新的技术指标API：
  1. 调用 /api/v1/market/technical-indicators 获取指标数据
  2. 将指标数据渲染到图表中
-->
<template>
  <div class="technical-indicators-example">
    <h2>技术指标集成示例</h2>

    <!-- 控制面板 -->
    <div class="controls">
      <div class="control-group">
        <label>股票代码:</label>
        <input v-model="symbol" placeholder="600000.SH" />
      </div>

      <div class="control-group">
        <label>周期:</label>
        <select v-model="period">
          <option value="day">日线</option>
          <option value="week">周线</option>
          <option value="60min">60分钟</option>
          <option value="30min">30分钟</option>
          <option value="15min">15分钟</option>
          <option value="5min">5分钟</option>
        </select>
      </div>

      <div class="control-group">
        <label>指标:</label>
        <div class="indicator-checkboxes">
          <label v-for="indicator in availableIndicators" :key="indicator">
            <input
              type="checkbox"
              :value="indicator"
              v-model="selectedIndicators"
            />
            {{ indicator }}
          </label>
        </div>
      </div>

      <button @click="fetchIndicators" :disabled="loading">
        {{ loading ? '加载中...' : '获取指标' }}
      </button>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading">
      正在加载技术指标...
    </div>

    <!-- 错误信息 -->
    <div v-if="error" class="error">
      {{ error }}
    </div>

    <!-- 结果显示 -->
    <div v-if="!loading && indicatorData" class="results">
      <h3>指标数据</h3>

      <div class="meta-info">
        <p>数据源: {{ dataSource }}</p>
        <p>计算耗时: {{ calcTimeMs }}ms</p>
        <p>总耗时: {{ totalTimeMs }}ms</p>
      </div>

      <!-- MA指标 -->
      <div v-if="indicatorData.MA" class="indicator-group">
        <h4>MA均线</h4>
        <div v-for="(data, key) in indicatorData.MA" :key="key" class="indicator-item">
          <strong>{{ key }}:</strong> {{ data.slice(0, 5).join(', ') }}... (共{{ data.length }}条)
        </div>
      </div>

      <!-- MACD指标 -->
      <div v-if="indicatorData.MACD" class="indicator-group">
        <h4>MACD</h4>
        <div class="indicator-item">
          <strong>MACD:</strong> {{ indicatorData.MACD.MACD.slice(0, 5).join(', ') }}...
        </div>
        <div class="indicator-item">
          <strong>Signal:</strong> {{ indicatorData.MACD.Signal.slice(0, 5).join(', ') }}...
        </div>
        <div class="indicator-item">
          <strong>Histogram:</strong> {{ indicatorData.MACD.Histogram.slice(0, 5).join(', ') }}...
        </div>
      </div>

      <!-- KDJ指标 -->
      <div v-if="indicatorData.KDJ" class="indicator-group">
        <h4>KDJ</h4>
        <div class="indicator-item">
          <strong>K:</strong> {{ indicatorData.KDJ.K.slice(0, 5).join(', ') }}...
        </div>
        <div class="indicator-item">
          <strong>D:</strong> {{ indicatorData.KDJ.D.slice(0, 5).join(', ') }}...
        </div>
        <div class="indicator-item">
          <strong>J:</strong> {{ indicatorData.KDJ.J.slice(0, 5).join(', ') }}...
        </div>
      </div>

      <!-- BOLL指标 -->
      <div v-if="indicatorData.BOLL" class="indicator-group">
        <h4>BOLL布林带</h4>
        <div class="indicator-item">
          <strong>Upper:</strong> {{ indicatorData.BOLL.upper.slice(0, 5).join(', ') }}...
        </div>
        <div class="indicator-item">
          <strong>Middle:</strong> {{ indicatorData.BOLL.middle.slice(0, 5).join(', ') }}...
        </div>
        <div class="indicator-item">
          <strong>Lower:</strong> {{ indicatorData.BOLL.lower.slice(0, 5).join(', ') }}...
        </div>
      </div>

      <!-- RSI指标 -->
      <div v-if="indicatorData.RSI" class="indicator-group">
        <h4>RSI相对强弱</h4>
        <div v-for="(data, key) in indicatorData.RSI" :key="key" class="indicator-item">
          <strong>{{ key }}:</strong> {{ data.slice(0, 5).join(', ') }}...
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useTechnicalIndicators } from '@/composables/useTechnicalIndicatorsBackend'

// 状态
const symbol = ref('600000.SH')
const period = ref('day')
const selectedIndicators = ref<string[]>(['MA', 'MACD', 'KDJ', 'BOLL', 'RSI'])

// 可用指标列表
const availableIndicators = [
  'MA',      // 趋势指标
  'EMA',
  'MACD',
  'BOLL',
  'KDJ',     // 震荡指标
  'RSI',
  'CCI',
  'OBV',     // 成交量指标
  'MOM',     // 动量指标
  'ROC'
]

// 使用技术指标composable
const {
  indicatorData,
  loading,
  error,
  dataSource,
  calcTimeMs,
  totalTimeMs,
  fetchIndicators
} = useTechnicalIndicators()

// 获取指标
async function handleFetchIndicators() {
  const success = await fetchIndicators(
    symbol.value,
    period.value,
    selectedIndicators.value
  )

  if (success) {
    console.log('指标数据获取成功:', indicatorData.value)
  } else {
    console.error('指标数据获取失败:', error.value)
  }
}
</script>

<style scoped>
.technical-indicators-example {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.controls {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  margin-bottom: 20px;
  padding: 15px;
  background: #f5f5f5;
  border-radius: 4px;
}

.control-group {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.control-group label {
  font-weight: bold;
}

.indicator-checkboxes {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.indicator-checkboxes label {
  display: flex;
  align-items: center;
  gap: 5px;
  font-weight: normal;
}

button {
  padding: 10px 20px;
  background: #1890ff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

button:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.loading {
  padding: 20px;
  text-align: center;
  color: #1890ff;
}

.error {
  padding: 15px;
  background: #fff1f0;
  border: 1px solid #ffccc7;
  border-radius: 4px;
  color: #ff4d4f;
}

.results {
  margin-top: 20px;
}

.meta-info {
  padding: 10px;
  background: #f0f0f0;
  border-radius: 4px;
  margin-bottom: 20px;
}

.meta-info p {
  margin: 5px 0;
}

.indicator-group {
  margin-bottom: 20px;
  padding: 15px;
  background: white;
  border: 1px solid #e8e8e8;
  border-radius: 4px;
}

.indicator-group h4 {
  margin-top: 0;
  margin-bottom: 10px;
  color: #1890ff;
}

.indicator-item {
  padding: 5px 0;
  border-bottom: 1px solid #f0f0f0;
}

.indicator-item:last-child {
  border-bottom: none;
}

.indicator-item strong {
  display: inline-block;
  min-width: 100px;
}
</style>

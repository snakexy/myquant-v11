<template>
  <Teleport to="body">
    <div v-if="show" class="modal-overlay" @click="$emit('close')">
      <div class="modal-container" @click.stop>
        <div class="modal-header">
          <h2>{{ stock?.name }} ({{ stock?.code }})</h2>
          <button class="close-btn" @click="$emit('close')">
            <i class="fas fa-times"></i>
          </button>
        </div>

        <div class="modal-content">
          <div class="stock-summary" v-if="!loading">
            <div class="summary-item">
              <span class="label">涨跌幅</span>
              <span
                class="value"
                :class="getChangeClass(calculatedChangePercent)"
              >
                {{ calculatedChangePercent > 0 ? '+' : '' }}{{ calculatedChangePercent.toFixed(2) }}%
              </span>
            </div>
            <div class="summary-item">
              <span class="label">成交额</span>
              <span class="value">{{ formatAmount(calculatedAmount) }}</span>
            </div>
            <div class="summary-item">
              <span class="label">市场</span>
              <span class="value">{{ marketName }}</span>
            </div>
          </div>

          <!-- 加载状态 -->
          <div class="stock-summary loading" v-else>
            <div class="loading-text">
              <i class="fas fa-spinner fa-spin"></i>
              正在获取实时数据...
            </div>
          </div>

          <!-- 图表区域 -->
          <div class="kline-section">
            <!-- 图表类型切换 -->
            <div class="chart-tabs">
              <button
                :class="['tab-btn', { active: chartType === 'intraday' }]"
                @click="chartType = 'intraday'"
              >
                分时
              </button>
              <button
                :class="['tab-btn', { active: chartType === 'kline' }]"
                @click="chartType = 'kline'"
              >
                K线
              </button>
              <button
                :class="['tab-btn', 'config-btn']"
                @click="showIndicatorConfig = true"
                title="配置技术指标参数"
              >
                <i class="fas fa-sliders-h"></i>
                指标配置
              </button>
            </div>

            <!-- 分时图 (1分钟K线) -->
            <TradingViewKLineUnified
              v-if="stock?.code && chartType === 'intraday'"
              :symbol="formattedSymbol"
              :stock-name="stock.name"
              period="1m"
              height="500px"
            />

            <!-- K线图 -->
            <TradingViewKLineUnified
              v-if="stock?.code && chartType === 'kline'"
              :key="stock.code"
              :symbol="formattedSymbol"
              :stock-name="stock.name"
              period="day"
              height="500px"
            />
          </div>

          <div class="detail-sections">
            <div class="detail-section">
              <h3>技术指标</h3>
              <p class="placeholder-text">Qlib技术指标分析加载中...</p>
            </div>

            <div class="detail-section">
              <h3>因子评分</h3>
              <p class="placeholder-text">Qlib因子评分计算中...</p>
            </div>

            <div class="detail-section">
              <h3>ML预测</h3>
              <p class="placeholder-text">机器学习模型预测中...</p>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn btn-secondary" @click="$emit('close')">
            关闭
          </button>
          <button class="btn btn-primary">
            添加到自选
          </button>
        </div>
      </div>

      <!-- 指标配置面板 -->
      <Teleport to="body">
        <div v-if="showIndicatorConfig" class="config-panel-overlay" @click="showIndicatorConfig = false">
          <div class="config-panel-container" @click.stop>
            <IndicatorConfigPanel
              v-if="stock"
              :stock-code="stock.code"
              @close="showIndicatorConfig = false"
              @config-change="handleIndicatorConfigChange"
            />
          </div>
        </div>
      </Teleport>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import TradingViewKLineUnified from '@/components/charts/TradingViewKLineUnified.vue'
import IndicatorConfigPanel from '@/components/config/IndicatorConfigPanel.vue'

interface IndicatorConfig {
  // MA均线
  ma5: number
  ma10: number
  ma20: number
  ma30: number
  ma60: number
  // BOLL
  bollPeriod: number
  bollStdDev: number
  // MACD
  macdFast: number
  macdSlow: number
  macdSignal: number
  // RSI
  rsi6: number
  rsi12: number
  rsi24: number
  // KDJ
  kdjK: number
  kdjD: number
  kdjJ: number
  preset?: string
}

interface Stock {
  code: string
  name: string
  changePercent: number
  amount: number
  market: string
}

interface Props {
  stock: Stock | null
  show: boolean
}

const props = defineProps<Props>()

const emit = defineEmits<{
  close: []
}>()

// 实时K线数据
const realtimeData = ref<any>(null)
const loading = ref(false)

// 图表类型：分时或K线
const chartType = ref<'intraday' | 'kline'>('kline')

// 指标配置面板
const showIndicatorConfig = ref(false)
const indicatorConfig = ref<IndicatorConfig | null>(null)

// 处理指标配置变化
const handleIndicatorConfigChange = (config: IndicatorConfig) => {
  indicatorConfig.value = config
  console.log('指标配置已更新:', config)
  // TODO: 刷新图表以应用新配置
  // 可以通过事件或ref调用图表组件的方法来刷新
}

// 获取实时行情数据
const fetchRealtimeData = async (code: string) => {
  if (!code) return

  loading.value = true
  try {
    const response = await fetch(`/api/v1/market/stock/${code}/quote`)
    const result = await response.json()

    if (result.success && result.data) {
      realtimeData.value = result.data
      console.log('获取到实时数据:', result.data)
    }
  } catch (error) {
    console.error('获取实时数据失败:', error)
  } finally {
    loading.value = false
  }
}

// 监听stock变化，获取实时数据
watch(() => props.stock, (newStock) => {
  if (newStock?.code) {
    fetchRealtimeData(newStock.code)
  }
}, { immediate: true })

// 计算实际的涨跌幅
const calculatedChangePercent = computed(() => {
  // 如果API返回了change_percent，使用API数据
  if (realtimeData.value?.change_percent !== undefined && realtimeData.value.change_percent !== null) {
    return realtimeData.value.change_percent
  }
  // 如果stock对象有changePercent且不为0，使用stock中的数据
  if (props.stock?.changePercent && props.stock.changePercent !== 0) {
    return props.stock.changePercent
  }
  // 默认返回0
  return 0
})

// 计算实际的成交额
const calculatedAmount = computed(() => {
  // 如果API返回了amount，使用API数据
  if (realtimeData.value?.amount) {
    return realtimeData.value.amount
  }
  // 如果stock对象有amount且不为0，使用stock中的数据
  if (props.stock?.amount && props.stock.amount !== 0) {
    return props.stock.amount
  }
  // 默认返回0
  return 0
})

// 市场名称
const marketName = computed(() => {
  if (props.stock?.market === 'SH' || props.stock?.market === '1') {
    return '上海'
  } else if (props.stock?.market === 'SZ' || props.stock?.market === '0') {
    return '深圳'
  }
  return 'A股大盘'
})

const getChangeClass = (change?: number) => {
  if (!change) return ''
  if (change > 0) return 'rise'
  if (change < 0) return 'fall'
  return 'flat'
}

const formatAmount = (amount?: number) => {
  if (!amount) return '--'
  if (amount >= 100000000) {
    return `${(amount / 100000000).toFixed(2)}亿`
  } else if (amount >= 10000) {
    return `${(amount / 10000).toFixed(2)}万`
  }
  return amount.toString()
}

// 格式化股票代码 (添加市场后缀)
const formattedSymbol = computed(() => {
  if (!props.stock?.code) return ''
  const code = props.stock.code
  // 如果已经包含市场后缀,直接返回
  if (code.includes('.')) return code
  // 根据代码规则添加市场后缀
  if (code.startsWith('6')) {
    return `${code}.SH`  // 上海市场
  } else if (code.startsWith('0') || code.startsWith('3')) {
    return `${code}.SZ`  // 深圳市场
  }
  return code
})
</script>

<style scoped lang="scss">
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn 0.2s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.modal-container {
  width: 90%;
  max-width: 800px;
  max-height: 90vh;
  background: var(--bg-surface);
  border-radius: 16px;
  border: 1px solid var(--border-light);
  display: flex;
  flex-direction: column;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  animation: slideUp 0.3s ease;
}

@keyframes slideUp {
  from {
    transform: translateY(20px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

.modal-header {
  padding: 20px 24px;
  border-bottom: 1px solid var(--border-light);
  display: flex;
  justify-content: space-between;
  align-items: center;

  h2 {
    font-size: 20px;
    font-weight: 700;
    color: var(--text-primary);
    margin: 0;
  }

  .close-btn {
    width: 36px;
    height: 36px;
    border-radius: 8px;
    border: 1px solid var(--border-light);
    background: transparent;
    color: var(--text-secondary);
    cursor: pointer;
    transition: all 0.3s;
    display: flex;
    align-items: center;
    justify-content: center;

    &:hover {
      background: var(--bg-elevated);
      border-color: var(--primary-color);
      color: var(--primary-color);
    }
  }
}

.modal-content {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
}

.kline-section {
  margin-bottom: 24px;
  padding: 20px;
  background: var(--bg-elevated);
  border-radius: 12px;
}

/* 图表类型切换tabs */
.chart-tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
  border-bottom: 1px solid #374151;
  padding-bottom: 8px;
}

.tab-btn {
  background: transparent;
  border: none;
  color: #9ca3af;
  padding: 6px 16px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 13px;
  font-weight: 500;
  transition: all 0.2s;
}

.tab-btn:hover {
  color: #f8fafc;
  background: #374151;
}

.tab-btn.active {
  color: #3b82f6;
  background: #1e3a5f;
}

.config-btn {
  margin-left: auto;
  gap: 6px;
}

.config-panel-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1100;
  animation: fadeIn 0.2s ease;
}

.config-panel-container {
  max-width: 500px;
  width: 90%;
  animation: slideUp 0.3s ease;
}

:deep(.kline-container) {
  .chart-controls {
    margin-bottom: 16px;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .kline-chart {
    width: 100%;
    height: 400px;
  }
}

.stock-summary {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-bottom: 24px;

  &.loading {
    grid-template-columns: 1fr;
    padding: 20px;
  }

  .loading-text {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    font-size: 14px;
    color: var(--text-secondary);
  }

  .summary-item {
    padding: 16px;
    background: var(--bg-elevated);
    border-radius: 12px;
    text-align: center;

    .label {
      display: block;
      font-size: 12px;
      color: var(--text-secondary);
      margin-bottom: 8px;
    }

    .value {
      font-size: 20px;
      font-weight: 700;
      color: var(--text-primary);

      &.rise {
        color: #ef4444;
      }

      &.fall {
        color: #10b981;
      }

      &.flat {
        color: var(--text-secondary);
      }
    }
  }
}

.detail-sections {
  display: grid;
  gap: 16px;

  .detail-section {
    padding: 20px;
    background: var(--bg-elevated);
    border-radius: 12px;

    h3 {
      font-size: 16px;
      font-weight: 600;
      color: var(--text-primary);
      margin: 0 0 12px 0;
    }

    .placeholder-text {
      font-size: 14px;
      color: var(--text-secondary);
      margin: 0;
    }
  }
}

.modal-footer {
  padding: 16px 24px;
  border-top: 1px solid var(--border-light);
  display: flex;
  justify-content: flex-end;
  gap: 12px;

  .btn {
    padding: 10px 24px;
    border-radius: 8px;
    font-size: 14px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s;
    border: none;

    &.btn-secondary {
      background: var(--bg-elevated);
      color: var(--text-primary);

      &:hover {
        background: var(--bg-deep);
      }
    }

    &.btn-primary {
      background: var(--primary-color);
      color: white;

      &:hover {
        opacity: 0.9;
        transform: translateY(-1px);
      }
    }
  }
}
</style>

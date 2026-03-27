<template>
  <div class="stock-detail-view" v-loading="loading">
    <!-- 股票信息头部 -->
    <div class="stock-header">
      <div class="stock-info">
        <h1 class="stock-title">{{ stockInfo.name || stockInfo.symbol }} ({{ stockInfo.symbol }})</h1>
        <div class="stock-price" :class="getChangeClass(quoteData.change_percent)">
          <span class="current-price">{{ formatNumber(quoteData.price) }}</span>
          <span class="price-change" v-if="quoteData.change">
            {{ formatChange(quoteData.change, quoteData.change_percent) }}
          </span>
        </div>
      </div>
      <div class="stock-actions">
        <el-button @click="refreshData" :loading="refreshing">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
      </div>
    </div>

    <!-- K线图表（带技术指标） -->
    <div class="chart-section">
      <div class="chart-header">
        <h3>K线图与技术指标</h3>
        <div class="period-tabs">
          <el-radio-group v-model="selectedPeriod" @change="handlePeriodChange">
            <el-radio-button label="day">日K</el-radio-button>
            <el-radio-button label="week">周K</el-radio-button>
            <el-radio-button label="month">月K</el-radio-button>
            <el-radio-button label="5min">5分</el-radio-button>
            <el-radio-button label="15min">15分</el-radio-button>
            <el-radio-button label="30min">30分</el-radio-button>
            <el-radio-button label="60min">60分</el-radio-button>
          </el-radio-group>
        </div>
      </div>
      <div class="chart-container">
        <TradingViewKLineUnified
          :symbol="formattedSymbol"
          :stock-name="stockInfo.name"
          :period="selectedPeriod"
          height="600px"
        />
      </div>
    </div>

    <!-- 详细数据表格 -->
    <div class="detail-section">
      <h3>详细数据</h3>
      <el-descriptions :column="3" border>
        <el-descriptions-item label="今开">{{ formatNumber(quoteData.open) }}</el-descriptions-item>
        <el-descriptions-item label="最高">{{ formatNumber(quoteData.high) }}</el-descriptions-item>
        <el-descriptions-item label="最低">{{ formatNumber(quoteData.low) }}</el-descriptions-item>
        <el-descriptions-item label="昨收">{{ formatNumber(quoteData.close) }}</el-descriptions-item>
        <el-descriptions-item label="成交量">{{ formatVolume(quoteData.volume) }}</el-descriptions-item>
        <el-descriptions-item label="成交额">{{ formatAmount(quoteData.amount) }}</el-descriptions-item>
        <el-descriptions-item label="振幅">
          {{ calculateAmplitude(quoteData.open, quoteData.high, quoteData.low) }}%
        </el-descriptions-item>
        <el-descriptions-item label="换手率">
          {{ quoteData.turnover_rate || '--' }}
        </el-descriptions-item>
        <el-descriptions-item label="市盈率">
          {{ quoteData.pe || '--' }}
        </el-descriptions-item>
      </el-descriptions>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, onActivated, computed } from 'vue'
import { useRoute } from 'vue-router'
import { Refresh } from '@element-plus/icons-vue'
import TradingViewKLineUnified from '@/components/charts/TradingViewKLineUnified.vue'
import { getQuotes } from '@/api/market'

const route = useRoute()
const symbol = ref(route.query.symbol as string || '600519')

// 格式化股票代码 (添加市场后缀)
const formattedSymbol = computed(() => {
  const code = symbol.value
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

const stockInfo = ref<any>({
  symbol: symbol.value,
  name: ''
})

const quoteData = ref<any>({})
const loading = ref(false)
const refreshing = ref(false)
const selectedPeriod = ref('day')

// 行情定时器
let quoteTimer: ReturnType<typeof setInterval> | null = null

// 获取股票行情
const fetchQuote = async () => {
  try {
    const data = await getQuotes(symbol.value)
    if (data && data.length > 0) {
      quoteData.value = data[0]
      stockInfo.value.name = data[0].name || symbol.value
    }
  } catch (error) {
    console.error('Failed to fetch quote:', error)
  }
}

// 切换周期
const handlePeriodChange = async () => {
  loading.value = true
  await fetchQuote()
  loading.value = false
}

// 刷新数据
const refreshData = () => {
  refreshing.value = true
  handlePeriodChange().finally(() => {
    refreshing.value = false
  })
}

// 计算振幅
const calculateAmplitude = (open: number, high: number, low: number) => {
  if (!open || !high || !low) return '--'
  const amplitude = ((high - low) / open) * 100
  return amplitude.toFixed(2)
}

// 格式化函数
const formatNumber = (num: number) => {
  if (!num) return '--'
  return num.toFixed(2)
}

const formatChange = (change: number, percent: number) => {
  if (!change || !percent) return '--'
  const mark = change > 0 ? '+' : ''
  return `${mark}${change.toFixed(2)} (${mark}${percent.toFixed(2)}%)`
}

const formatVolume = (vol: number) => {
  if (!vol) return '--'
  return vol.toLocaleString() + '手'
}

const formatAmount = (amount: number) => {
  if (!amount) return '--'
  if (amount >= 100000000) {
    return (amount / 100000000).toFixed(2) + '亿'
  } else if (amount >= 10000) {
    return (amount / 10000).toFixed(2) + '万'
  }
  return amount.toFixed(2) + '元'
}

const getChangeClass = (change: number) => {
  if (!change) return ''
  if (change > 0) return 'text-up'
  if (change < 0) return 'text-down'
  return 'text-flat'
}

// 生命周期
onMounted(async () => {
  await fetchQuote()

  // 启动行情定时刷新（每5秒刷新一次，类似通达信）
  quoteTimer = setInterval(() => {
    fetchQuote()
  }, 5000)
})

onUnmounted(() => {
  // 清理定时器
  if (quoteTimer) {
    clearInterval(quoteTimer)
    quoteTimer = null
  }
})

// 页面激活时（从其他页面切回来）立即刷新数据
onActivated(async () => {
  await fetchQuote()
})
</script>

<style scoped lang="scss">
@import '@/styles/variables.scss';

.stock-detail-view {
  padding: $spacing-lg;

  .stock-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: $spacing-xl;

    .stock-info {
      .stock-title {
        margin: 0 0 $spacing-sm 0;
        font-size: $font-2xl;
        color: $text-primary;
      }

      .stock-price {
        display: flex;
        align-items: baseline;
        gap: $spacing-lg;

        .current-price {
          font-size: $font-3xl;
          font-weight: 700;
        }

        .price-change {
          font-size: $font-lg;
        }
      }
    }
  }

  .chart-section {
    background: $bg-surface;
    border: 1px solid $border-light;
    border-radius: $radius-lg;
    padding: $spacing-lg;
    margin-bottom: $spacing-xl;

    .chart-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: $spacing-lg;
      flex-wrap: wrap;
      gap: $spacing-md;

      h3 {
        margin: 0;
        font-size: $font-lg;
        color: $text-primary;
      }

      .period-tabs {
        :deep(.el-radio-group) {
          flex-wrap: wrap;
        }
      }
    }

    .chart-container {
      width: 100%;
    }
  }

  .detail-section {
    background: $bg-surface;
    border: 1px solid $border-light;
    border-radius: $radius-lg;
    padding: $spacing-lg;

    h3 {
      margin: 0 0 $spacing-lg 0;
      font-size: $font-lg;
      color: $text-primary;
    }
  }
}

.text-up {
  color: var(--color-up);
}

.text-down {
  color: var(--color-down);
}

.text-flat {
  color: $text-secondary;
}
</style>

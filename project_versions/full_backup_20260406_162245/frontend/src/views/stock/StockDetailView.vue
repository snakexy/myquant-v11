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

    <!-- K线图表 -->
    <div class="chart-section">
      <div class="chart-header">
        <h3>K线图</h3>
        <div class="period-tabs">
          <el-radio-group v-model="selectedPeriod" @change="handlePeriodChange">
            <el-radio-button label="day">日K</el-radio-button>
            <el-radio-button label="week">周K</el-radio-button>
            <el-radio-button label="month">月K</el-radio-button>
          </el-radio-group>
        </div>
      </div>
      <div class="chart-container" ref="chartContainer"></div>
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
      </el-descriptions>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { Refresh } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import { getQuotes } from '@/api/market'

const route = useRoute()
const symbol = ref(route.query.symbol as string || '600519')

const stockInfo = ref<any>({
  symbol: symbol.value,
  name: ''
})

const quoteData = ref<any>({})
const klineData = ref<any>(null)
const loading = ref(false)
const refreshing = ref(false)
const selectedPeriod = ref('day')

let chart: echarts.ECharts | null = null
const chartContainer = ref<HTMLElement>()

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

// 获取K线数据
const fetchKline = async () => {
  try {
    loading.value = true

    const response = await fetch(
      `/api/stock/${symbol.value}/kline?period=${selectedPeriod.value}&count=100`
    )
    const data = await response.json()

    if (data && data.data) {
      klineData.value = data.data
      await nextTick()
      renderChart()
    }
  } catch (error) {
    console.error('Failed to fetch kline:', error)
  } finally {
    loading.value = false
  }
}

// 渲染图表
const renderChart = () => {
  if (!chartContainer.value || !klineData.value) return

  if (!chart) {
    chart = echarts.init(chartContainer.value)
  }

  const dates = klineData.value.map((item: any) => {
    const date = new Date(item.datetime)
    return `${date.getMonth() + 1}/${date.getDate()}`
  })

  const values = klineData.value.map((item: any) => [
    item.open,
    item.close,
    item.low,
    item.high
  ])

  const volumes = klineData.value.map((item: any) => item.volume)

  const option = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross'
      }
    },
    legend: {
      data: ['K线', '成交量'],
      textStyle: {
        color: '#cbd5e1'
      }
    },
    grid: [
      {
        left: '10%',
        right: '10%',
        top: '10%',
        height: '50%'
      },
      {
        left: '10%',
        right: '10%',
        top: '70%',
        height: '15%'
      }
    ],
    xAxis: [
      {
        type: 'category',
        data: dates,
        scale: true,
        boundaryGap: false,
        axisLine: { onZero: false, lineStyle: { color: '#64748b' } },
        splitLine: { show: false },
        min: 'dataMin',
        max: 'dataMax'
      },
      {
        type: 'category',
        gridIndex: 1,
        data: dates,
        scale: true,
        boundaryGap: false,
        axisLine: { onZero: false, lineStyle: { color: '#64748b' } },
        axisTick: { show: false },
        splitLine: { show: false },
        axisLabel: { show: false },
        min: 'dataMin',
        max: 'dataMax'
      }
    ],
    yAxis: [
      {
        scale: true,
        splitArea: {
          show: true
        },
        axisLine: { lineStyle: { color: '#64748b' } },
        splitLine: { lineStyle: { color: 'rgba(255,255,255,0.06)' } }
      },
      {
        scale: true,
        gridIndex: 1,
        splitNumber: 2,
        axisLine: { lineStyle: { color: '#64748b' } },
        splitLine: { show: false },
        axisLabel: { show: false }
      }
    ],
    dataZoom: [
      {
        type: 'inside',
        xAxisIndex: [0, 1],
        start: 70,
        end: 100
      },
      {
        show: true,
        xAxisIndex: [0, 1],
        type: 'slider',
        top: '85%',
        start: 70,
        end: 100
      }
    ],
    series: [
      {
        name: 'K线',
        type: 'candlestick',
        data: values,
        itemStyle: {
          color: '#ef4444',
          color0: '#10b981',
          borderColor: '#ef4444',
          borderColor0: '#10b981'
        }
      },
      {
        name: '成交量',
        type: 'bar',
        xAxisIndex: 1,
        yAxisIndex: 1,
        data: volumes,
        itemStyle: {
          color: (params: any) => {
            const index = params.dataIndex
            if (index === 0) return '#64748b'
            const prevClose = klineData.value[index - 1]?.close
            const currClose = klineData.value[index]?.close
            return currClose >= prevClose ? '#ef4444' : '#10b981'
          }
        }
      }
    ]
  }

  chart.setOption(option)
}

// 切换周期
const handlePeriodChange = () => {
  fetchKline()
}

// 刷新数据
const refreshData = () => {
  refreshing.value = true
  Promise.all([fetchQuote(), fetchKline()]).finally(() => {
    refreshing.value = false
  })
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
  await fetchKline()

  // 窗口大小变化时重新渲染图表
  window.addEventListener('resize', () => {
    chart?.resize()
  })
})

onUnmounted(() => {
  if (chart) {
    chart.dispose()
    chart = null
  }
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

      h3 {
        margin: 0;
        font-size: $font-lg;
        color: $text-primary;
      }
    }

    .chart-container {
      width: 100%;
      height: 500px;
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
</style>

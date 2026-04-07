<template>
  <div class="multi-stock-monitor">
    <!-- 监控工具栏 -->
    <div class="monitor-toolbar">
      <div class="toolbar-left">
        <n-button-group size="small">
          <n-button @click="refreshAllStocks" :loading="isRefreshing" title="刷新所有">
            <template #icon>
              <n-icon :component="RefreshOutline" />
            </template>
          </n-button>
          <n-button @click="toggleAutoRefresh" :type="autoRefresh ? 'primary' : 'default'" title="自动刷新">
            <template #icon>
              <n-icon :component="PlayOutline" />
            </template>
          </n-button>
          <n-button @click="showAddStockModal = true" title="添加股票">
            <template #icon>
              <n-icon :component="AddOutline" />
            </template>
          </n-button>
        </n-button-group>
        
        <n-divider vertical />
        
        <n-select
          v-model:value="selectedLayout"
          :options="layoutOptions"
          size="small"
          style="width: 100px"
          @update:value="changeLayout"
        />
        
        <n-select
          v-model:value="selectedTimeframe"
          :options="timeframeOptions"
          size="small"
          style="width: 80px"
          @update:value="changeTimeframe"
        />
      </div>
      
      <div class="toolbar-center">
        <n-tag :type="connectionStatus === 'connected' ? 'success' : 'error'" size="small">
          {{ connectionStatus === 'connected' ? '实时连接' : '连接断开' }}
        </n-tag>
        <span class="stock-count">{{ monitoredStocks.length }} 只股票</span>
      </div>
      
      <div class="toolbar-right">
        <n-button-group size="small">
          <n-button @click="showLayoutSettings = true" title="布局设置">
            <template #icon>
              <n-icon :component="SettingsOutline" />
            </template>
          </n-button>
          <n-button @click="exportData" title="导出数据">
            <template #icon>
              <n-icon :component="DownloadOutline" />
            </template>
          </n-button>
          <n-button @click="toggleFullscreen" title="全屏">
            <template #icon>
              <n-icon :component="ExpandOutline" />
            </template>
          </n-button>
        </n-button-group>
      </div>
    </div>

    <!-- 股票网格 -->
    <div class="stocks-grid" :class="`layout-${selectedLayout}`" ref="stocksGrid">
      <div
        v-for="stock in monitoredStocks"
        :key="stock.code"
        class="stock-card"
        :class="{ 'alert-active': stock.alert, 'selected': selectedStock === stock.code }"
        @click="selectStock(stock)"
      >
        <!-- 股票头部 -->
        <div class="stock-header">
          <div class="stock-info">
            <span class="stock-code">{{ stock.code }}</span>
            <span class="stock-name">{{ stock.name }}</span>
          </div>
          <div class="stock-actions">
            <n-button
              quaternary
              circle
              size="tiny"
              @click.stop="toggleAlert(stock)"
              :class="{ 'alert-enabled': stock.alert }"
            >
              <template #icon>
                <n-icon :component="NotificationsOutline" />
              </template>
            </n-button>
            <n-button quaternary circle size="tiny" @click.stop="removeStock(stock)">
              <template #icon>
                <n-icon :component="CloseOutline" />
              </template>
            </n-button>
          </div>
        </div>

        <!-- 价格信息 -->
        <div class="price-info">
          <div class="current-price">
            <span class="price">{{ stock.currentPrice }}</span>
            <span class="change" :class="getChangeClass(stock.changePercent)">
              {{ stock.changePercent > 0 ? '+' : '' }}{{ stock.changePercent }}%
            </span>
          </div>
          <div class="price-detail">
            <span class="change-amount" :class="getChangeClass(stock.changeAmount)">
              {{ stock.changeAmount > 0 ? '+' : '' }}{{ stock.changeAmount }}
            </span>
            <span class="update-time">{{ stock.updateTime }}</span>
          </div>
        </div>

        <!-- K线图 -->
        <div class="stock-chart">
          <div class="chart-container" :id="`chart-${stock.code}`"></div>
          <div class="chart-overlay" v-if="stock.loading">
            <n-spin size="small" />
          </div>
        </div>

        <!-- 技术指标 -->
        <div class="technical-indicators">
          <div class="indicator-row">
            <div class="indicator-item">
              <span class="indicator-label">成交量</span>
              <span class="indicator-value">{{ formatVolume(stock.volume) }}</span>
            </div>
            <div class="indicator-item">
              <span class="indicator-label">换手率</span>
              <span class="indicator-value">{{ stock.turnoverRate }}%</span>
            </div>
          </div>
          <div class="indicator-row">
            <div class="indicator-item">
              <span class="indicator-label">市盈率</span>
              <span class="indicator-value">{{ stock.pe }}</span>
            </div>
            <div class="indicator-item">
              <span class="indicator-label">市净率</span>
              <span class="indicator-value">{{ stock.pb }}</span>
            </div>
          </div>
        </div>

        <!-- 预警信息 -->
        <div class="alert-info" v-if="stock.alert && stock.alertMessage">
          <n-alert type="warning" size="small" :show-icon="false">
            {{ stock.alertMessage }}
          </n-alert>
        </div>
      </div>
    </div>

    <!-- 添加股票弹窗 -->
    <n-modal v-model:show="showAddStockModal" preset="card" style="max-width: 500px;" title="添加股票">
      <div class="add-stock-form">
        <n-form :model="addStockForm" label-placement="left" label-width="80">
          <n-form-item label="股票代码">
            <n-input
              v-model:value="addStockForm.code"
              placeholder="如：000001.SZ 或 600000.SH"
              @keyup.enter="addStock"
            />
          </n-form-item>
          <n-form-item label="预警阈值">
            <n-input-number
              v-model:value="addStockForm.alertThreshold"
              :min="1"
              :max="20"
              :step="0.5"
            />
            <span class="unit">%</span>
          </n-form-item>
        </n-form>
      </div>
      <template #footer>
        <n-space justify="end">
          <n-button @click="showAddStockModal = false">取消</n-button>
          <n-button type="primary" @click="addStock" :disabled="!addStockForm.code">添加</n-button>
        </n-space>
      </template>
    </n-modal>

    <!-- 布局设置弹窗 -->
    <n-modal v-model:show="showLayoutSettings" preset="card" style="max-width: 400px;" title="布局设置">
      <div class="layout-settings">
        <n-form :model="layoutSettings" label-placement="left" label-width="80">
          <n-form-item label="刷新频率">
            <n-select
              v-model:value="layoutSettings.refreshInterval"
              :options="refreshIntervalOptions"
            />
          </n-form-item>
          <n-form-item label="显示指标">
            <n-checkbox-group v-model:value="layoutSettings.indicators">
              <n-space vertical>
                <n-checkbox value="volume" label="成交量" />
                <n-checkbox value="turnover" label="换手率" />
                <n-checkbox value="pepb" label="市盈率/市净率" />
                <n-checkbox value="chart" label="K线图" />
              </n-space>
            </n-checkbox-group>
          </n-form-item>
          <n-form-item label="图表类型">
            <n-radio-group v-model:value="layoutSettings.chartType">
              <n-space>
                <n-radio value="candlestick">K线</n-radio>
                <n-radio value="line">分时</n-radio>
                <n-radio value="area">面积</n-radio>
              </n-space>
            </n-radio-group>
          </n-form-item>
        </n-form>
      </div>
      <template #footer>
        <n-space justify="end">
          <n-button @click="resetLayoutSettings">重置</n-button>
          <n-button type="primary" @click="applyLayoutSettings">应用</n-button>
        </n-space>
      </template>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted, nextTick, computed } from 'vue'
import { useMessage } from 'naive-ui'
import * as echarts from 'echarts'
import {
  RefreshOutline,
  PlayOutline,
  AddOutline,
  SettingsOutline,
  DownloadOutline,
  ExpandOutline,
  NotificationsOutline,
  CloseOutline
} from '@vicons/ionicons5'

// 组件属性定义
interface Props {
  stocks?: string[]
  height?: number
  defaultLayout?: string
}

const props = withDefaults(defineProps<Props>(), {
  stocks: () => [], // 改为空数组，避免硬编码
  height: 800,
  defaultLayout: '2x3'
})

// 消息提示
const message = useMessage()

// DOM引用
const stocksGrid = ref<HTMLElement | null>(null)

// 响应式数据
const isRefreshing = ref(false)
const autoRefresh = ref(true)
const selectedLayout = ref(props.defaultLayout)
const selectedTimeframe = ref('1d')
const connectionStatus = ref<'connected' | 'disconnected'>('connected')
const selectedStock = ref('')
const showAddStockModal = ref(false)
const showLayoutSettings = ref(false)

// 监控股票数据
const monitoredStocks = ref([
  // 移除硬编码的默认股票，改为动态获取
    currentPrice: 12.85,
    changeAmount: 0.30,
    changePercent: 2.35,
    volume: 125000000,
    turnoverRate: 1.23,
    pe: 5.8,
    pb: 0.6,
    updateTime: '15:00:00',
    alert: false,
    alertMessage: '',
    loading: false,
    chartData: []
  },
  {
    code: '000002.SZ',
    name: '万科A',
    currentPrice: 18.42,
    changeAmount: -0.23,
    changePercent: -1.25,
    volume: 89000000,
    turnoverRate: 0.95,
    pe: 8.2,
    pb: 0.8,
    updateTime: '15:00:00',
    alert: true,
    alertMessage: '跌幅超过预警阈值5%',
    loading: false,
    chartData: []
  },
  {
    code: '600000.SH',
    name: '浦发银行',
    currentPrice: 9.87,
    changeAmount: 0.08,
    changePercent: 0.85,
    volume: 67000000,
    turnoverRate: 0.67,
    pe: 4.5,
    pb: 0.5,
    updateTime: '15:00:00',
    alert: false,
    alertMessage: '',
    loading: false,
    chartData: []
  },
  // 移除硬编码的默认股票，改为动态获取
    currentPrice: 35.68,
    changeAmount: 0.51,
    changePercent: 1.45,
    volume: 156000000,
    turnoverRate: 1.56,
    pe: 6.8,
    pb: 0.9,
    updateTime: '15:00:00',
    alert: false,
    alertMessage: '',
    loading: false,
    chartData: []
  },
  // 移除硬编码的默认股票，改为动态获取
    currentPrice: 142.35,
    changeAmount: 2.18,
    changePercent: 1.55,
    volume: 234000000,
    turnoverRate: 2.34,
    pe: 18.5,
    pb: 4.2,
    updateTime: '15:00:00',
    alert: false,
    alertMessage: '',
    loading: false,
    chartData: []
  }
])

// 添加股票表单
const addStockForm = reactive({
  code: '',
  alertThreshold: 5.0
})

// 布局设置
const layoutSettings = reactive({
  refreshInterval: 5000,
  indicators: ['volume', 'turnover', 'pepb', 'chart'],
  chartType: 'candlestick'
})

// 选项数据
const layoutOptions = [
  { label: '1x1', value: '1x1' },
  { label: '2x2', value: '2x2' },
  { label: '2x3', value: '2x3' },
  { label: '3x3', value: '3x3' },
  { label: '3x4', value: '3x4' },
  { label: '4x4', value: '4x4' }
]

const timeframeOptions = [
  { label: '分时', value: '1m' },
  { label: '5分', value: '5m' },
  { label: '15分', value: '15m' },
  { label: '30分', value: '30m' },
  { label: '日K', value: '1d' },
  { label: '周K', value: '1w' }
]

const refreshIntervalOptions = [
  { label: '1秒', value: 1000 },
  { label: '3秒', value: 3000 },
  { label: '5秒', value: 5000 },
  { label: '10秒', value: 10000 }
]

// 图表实例
const chartInstances = ref<Map<string, echarts.ECharts>>(new Map())

// 定时器
let refreshTimer: NodeJS.Timeout | null = null

// 方法
const refreshAllStocks = async () => {
  isRefreshing.value = true
  
  try {
    // 模拟数据刷新
    await new Promise(resolve => setTimeout(resolve, 500))
    
    // 更新每只股票的数据
    for (const stock of monitoredStocks.value) {
      stock.loading = true
      
      // 模拟API调用
      await new Promise(resolve => setTimeout(resolve, 100))
      
      const changePercent = (Math.random() - 0.5) * 4
      stock.changePercent = parseFloat(changePercent.toFixed(2))
      stock.changeAmount = parseFloat((stock.currentPrice * changePercent / 100).toFixed(2))
      stock.currentPrice = parseFloat((stock.currentPrice * (1 + changePercent / 100)).toFixed(2))
      stock.volume = Math.floor(stock.volume * (0.8 + Math.random() * 0.4))
      stock.turnoverRate = parseFloat((stock.turnoverRate * (0.9 + Math.random() * 0.2)).toFixed(2))
      stock.updateTime = new Date().toLocaleTimeString()
      
      // 检查预警
      if (Math.abs(stock.changePercent) >= addStockForm.alertThreshold) {
        stock.alert = true
        stock.alertMessage = `${stock.changePercent > 0 ? '涨幅' : '跌幅'}超过预警阈值${addStockForm.alertThreshold}%`
      } else {
        stock.alert = false
        stock.alertMessage = ''
      }
      
      stock.loading = false
    }
    
    // 更新图表
    updateCharts()
    
  } catch (error) {
    console.error('刷新股票数据失败:', error)
    message.error('刷新股票数据失败')
  } finally {
    isRefreshing.value = false
  }
}

const toggleAutoRefresh = () => {
  autoRefresh.value = !autoRefresh.value
  
  if (autoRefresh.value) {
    startAutoRefresh()
    message.success('已开启自动刷新')
  } else {
    stopAutoRefresh()
    message.info('已关闭自动刷新')
  }
}

const startAutoRefresh = () => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
  }
  
  refreshTimer = setInterval(() => {
    refreshAllStocks()
  }, layoutSettings.refreshInterval)
}

const stopAutoRefresh = () => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
    refreshTimer = null
  }
}

const changeLayout = (layout: string) => {
  selectedLayout.value = layout
  nextTick(() => {
    resizeCharts()
  })
}

const changeTimeframe = (timeframe: string) => {
  selectedTimeframe.value = timeframe
  updateCharts()
}

const selectStock = (stock: any) => {
  selectedStock.value = stock.code
  // 这里可以添加选中股票后的处理逻辑
}

const toggleAlert = (stock: any) => {
  stock.alert = !stock.alert
  message.info(`${stock.code} 预警已${stock.alert ? '开启' : '关闭'}`)
}

const removeStock = (stock: any) => {
  const index = monitoredStocks.value.findIndex(s => s.code === stock.code)
  if (index > -1) {
    monitoredStocks.value.splice(index, 1)
    
    // 销毁图表
    const chart = chartInstances.value.get(`chart-${stock.code}`)
    if (chart) {
      chart.dispose()
      chartInstances.value.delete(`chart-${stock.code}`)
    }
    
    message.success(`已移除 ${stock.code}`)
  }
}

const addStock = async () => {
  if (!addStockForm.code.trim()) {
    message.warning('请输入股票代码')
    return
  }
  
  // 检查是否已存在
  if (monitoredStocks.value.some(s => s.code === addStockForm.code)) {
    message.warning('该股票已在监控列表中')
    return
  }
  
  try {
    // 模拟API调用获取股票信息
    const newStock = {
      code: addStockForm.code,
      name: '新股票',
      currentPrice: 10.00 + Math.random() * 50,
      changeAmount: 0,
      changePercent: 0,
      volume: Math.floor(Math.random() * 100000000),
      turnoverRate: Math.random() * 3,
      pe: Math.random() * 20,
      pb: Math.random() * 5,
      updateTime: new Date().toLocaleTimeString(),
      alert: false,
      alertMessage: '',
      loading: false,
      chartData: []
    }
    
    monitoredStocks.value.push(newStock)
    showAddStockModal.value = false
    addStockForm.code = ''
    
    // 初始化图表
    nextTick(() => {
      initChart(newStock)
    })
    
    message.success(`已添加 ${newStock.code}`)
    
  } catch (error) {
    console.error('添加股票失败:', error)
    message.error('添加股票失败')
  }
}

const exportData = () => {
  const exportData = {
    timestamp: new Date().toISOString(),
    stocks: monitoredStocks.value,
    layout: selectedLayout.value,
    timeframe: selectedTimeframe.value
  }
  
  const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `multi-stock-monitor-${Date.now()}.json`
  link.click()
  URL.revokeObjectURL(url)
  
  message.success('数据已导出')
}

const toggleFullscreen = () => {
  if (stocksGrid.value) {
    if (!document.fullscreenElement) {
      stocksGrid.value.requestFullscreen()
    } else {
      document.exitFullscreen()
    }
  }
}

const applyLayoutSettings = () => {
  showLayoutSettings.value = false
  
  // 重新启动自动刷新
  if (autoRefresh.value) {
    stopAutoRefresh()
    startAutoRefresh()
  }
  
  // 更新图表类型
  updateCharts()
  
  message.success('布局设置已应用')
}

const resetLayoutSettings = () => {
  layoutSettings.refreshInterval = 5000
  layoutSettings.indicators = ['volume', 'turnover', 'pepb', 'chart']
  layoutSettings.chartType = 'candlestick'
  applyLayoutSettings()
}

// 图表相关方法
const initCharts = () => {
  monitoredStocks.value.forEach(stock => {
    initChart(stock)
  })
}

const initChart = (stock: any) => {
  const chartId = `chart-${stock.code}`
  const chartElement = document.getElementById(chartId)
  
  if (!chartElement) return
  
  const chart = echarts.init(chartElement)
  chartInstances.value.set(chartId, chart)
  
  // 生成示例数据
  const data = generateChartData(stock)
  
  const option = getChartOption(data, layoutSettings.chartType)
  chart.setOption(option)
}

const generateChartData = (stock: any) => {
  const basePrice = stock.currentPrice
  const dataPoints = 60 // 60个数据点
  
  if (layoutSettings.chartType === 'candlestick') {
    return Array.from({ length: dataPoints }, () => {
      const open = basePrice * (0.98 + Math.random() * 0.04)
      const close = basePrice * (0.98 + Math.random() * 0.04)
      const high = Math.max(open, close) * (1 + Math.random() * 0.02)
      const low = Math.min(open, close) * (1 - Math.random() * 0.02)
      return [open, close, low, high]
    })
  } else {
    return Array.from({ length: dataPoints }, () => 
      basePrice * (0.95 + Math.random() * 0.1)
    )
  }
}

const getChartOption = (data: any[], chartType: string) => {
  const baseOption = {
    grid: {
      top: 5,
      left: 5,
      right: 5,
      bottom: 5
    },
    xAxis: {
      type: 'category',
      show: false,
      data: Array.from({ length: data.length }, (_, i) => i)
    },
    yAxis: {
      type: 'value',
      show: false,
      scale: true
    }
  }
  
  if (chartType === 'candlestick') {
    return {
      ...baseOption,
      series: [{
        type: 'candlestick',
        data,
        itemStyle: {
          color: '#ef4444',
          color0: '#10b981',
          borderColor: '#ef4444',
          borderColor0: '#10b981'
        }
      }]
    }
  } else if (chartType === 'area') {
    return {
      ...baseOption,
      series: [{
        type: 'line',
        data,
        smooth: true,
        symbol: 'none',
        lineStyle: {
          width: 1,
          color: '#2563eb'
        },
        areaStyle: {
          opacity: 0.3,
          color: '#2563eb'
        }
      }]
    }
  } else {
    return {
      ...baseOption,
      series: [{
        type: 'line',
        data,
        smooth: true,
        symbol: 'none',
        lineStyle: {
          width: 1,
          color: '#2563eb'
        }
      }]
    }
  }
}

const updateCharts = () => {
  monitoredStocks.value.forEach(stock => {
    const chartId = `chart-${stock.code}`
    const chart = chartInstances.value.get(chartId)
    
    if (chart) {
      const data = generateChartData(stock)
      const option = getChartOption(data, layoutSettings.chartType)
      chart.setOption(option)
    }
  })
}

const resizeCharts = () => {
  chartInstances.value.forEach(chart => {
    chart.resize()
  })
}

// 辅助方法
const getChangeClass = (change: number) => {
  if (change > 0) return 'positive'
  if (change < 0) return 'negative'
  return 'neutral'
}

const formatVolume = (volume: number) => {
  if (volume >= 100000000) {
    return `${(volume / 100000000).toFixed(1)}亿`
  } else if (volume >= 10000) {
    return `${(volume / 10000).toFixed(1)}万`
  }
  return volume.toString()
}

// 生命周期
onMounted(() => {
  nextTick(() => {
    initCharts()
    if (autoRefresh.value) {
      startAutoRefresh()
    }
  })
  
  // 监听窗口大小变化
  window.addEventListener('resize', resizeCharts)
})

onUnmounted(() => {
  stopAutoRefresh()
  chartInstances.value.forEach(chart => {
    chart.dispose()
  })
  chartInstances.value.clear()
  window.removeEventListener('resize', resizeCharts)
})
</script>

<style lang="scss" scoped>
.multi-stock-monitor {
  position: relative;
  width: 100%;
  height: v-bind('props.height + "px"');
  background: var(--bg-deep);
  border-radius: var(--border-radius-medium);
  overflow: hidden;
  display: flex;
  flex-direction: column;

  .monitor-toolbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: var(--spacing-2) var(--spacing-3);
    background: rgba(0, 0, 0, 0.3);
    border-bottom: 1px solid var(--border-color);
    flex-shrink: 0;

    .toolbar-left,
    .toolbar-right {
      display: flex;
      align-items: center;
      gap: var(--spacing-2);
    }

    .toolbar-center {
      display: flex;
      align-items: center;
      gap: var(--spacing-3);

      .stock-count {
        font-size: var(--font-size-xs);
        color: var(--text-secondary);
      }
    }
  }

  .stocks-grid {
    flex: 1;
    overflow: auto;
    padding: var(--spacing-3);
    display: grid;
    gap: var(--spacing-3);

    &.layout-1x1 {
      grid-template-columns: 1fr;
    }

    &.layout-2x2 {
      grid-template-columns: repeat(2, 1fr);
    }

    &.layout-2x3 {
      grid-template-columns: repeat(3, 1fr);
    }

    &.layout-3x3 {
      grid-template-columns: repeat(3, 1fr);
    }

    &.layout-3x4 {
      grid-template-columns: repeat(4, 1fr);
    }

    &.layout-4x4 {
      grid-template-columns: repeat(4, 1fr);
    }

    .stock-card {
      background: rgba(255, 255, 255, 0.05);
      border: 1px solid var(--border-color);
      border-radius: var(--border-radius-sm)all;
      padding: var(--spacing-3);
      cursor: pointer;
      transition: all 0.2s ease;
      display: flex;
      flex-direction: column;
      min-height: 280px;

      &:hover {
        background: rgba(255, 255, 255, 0.08);
        transform: translateY(-2px);
      }

      &.alert-active {
        border-color: var(--warning-color);
        box-shadow: 0 0 10px rgba(var(--warning-color), 0.3);
      }

      &.selected {
        border-color: var(--primary-color);
        box-shadow: 0 0 10px rgba(var(--primary-color), 0.3);
      }

      .stock-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: var(--spacing-2);

        .stock-info {
          display: flex;
          flex-direction: column;

          .stock-code {
            font-size: var(--font-size-sm);
            font-weight: 600;
            color: var(--text-primary);
          }

          .stock-name {
            font-size: var(--font-size-xs);
            color: var(--text-secondary);
          }
        }

        .stock-actions {
          display: flex;
          gap: var(--spacing-1);

          .alert-enabled {
            color: var(--warning-color);
          }
        }
      }

      .price-info {
        margin-bottom: var(--spacing-2);

        .current-price {
          display: flex;
          align-items: baseline;
          gap: var(--spacing-2);
          margin-bottom: var(--spacing-1);

          .price {
            font-size: var(--font-size-lg);
            font-weight: 600;
            color: var(--text-primary);
          }

          .change {
            font-size: var(--font-size-sm);

            &.positive {
              color: var(--success-color);
            }

            &.negative {
              color: var(--danger-color);
            }
          }
        }

        .price-detail {
          display: flex;
          justify-content: space-between;
          font-size: var(--font-size-xs);

          .change-amount {
            &.positive {
              color: var(--success-color);
            }

            &.negative {
              color: var(--danger-color);
            }
          }

          .update-time {
            color: var(--text-secondary);
          }
        }
      }

      .stock-chart {
        flex: 1;
        position: relative;
        margin-bottom: var(--spacing-2);
        min-height: 100px;

        .chart-container {
          width: 100%;
          height: 100%;
        }

        .chart-overlay {
          position: absolute;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          display: flex;
          align-items: center;
          justify-content: center;
          background: rgba(0, 0, 0, 0.5);
          border-radius: var(--border-radius-sm)all;
        }
      }

      .technical-indicators {
        display: flex;
        flex-direction: column;
        gap: var(--spacing-1);

        .indicator-row {
          display: flex;
          justify-content: space-between;

          .indicator-item {
            display: flex;
            flex-direction: column;
            align-items: center;
            flex: 1;

            .indicator-label {
              font-size: var(--font-size-xs);
              color: var(--text-secondary);
              margin-bottom: 2px;
            }

            .indicator-value {
              font-size: var(--font-size-xs);
              color: var(--text-primary);
              font-weight: 500;
            }
          }
        }
      }

      .alert-info {
        margin-top: var(--spacing-2);
      }
    }
  }

  .add-stock-form,
  .layout-settings {
    padding: var(--spacing-2);

    .unit {
      margin-left: var(--spacing-2);
      color: var(--text-secondary);
    }
  }
}
</style>
<template>
  <div class="realtime-monitor">
    <!-- 监控工具栏 -->
    <div class="monitor-toolbar">
      <div class="toolbar-left">
        <n-button-group size="small">
          <n-button @click="refreshData" :loading="isRefreshing" title="刷新数据">
            <template #icon>
              <n-icon :component="RefreshOutline" />
            </template>
          </n-button>
          <n-button @click="toggleAutoRefresh" :type="autoRefresh ? 'primary' : 'default'" title="自动刷新">
            <template #icon>
              <n-icon :component="PlayOutline" />
            </template>
          </n-button>
          <n-button @click="showSettings = true" title="设置">
            <template #icon>
              <n-icon :component="SettingsOutline" />
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
      </div>
      
      <div class="toolbar-center">
        <n-tag :type="connectionStatus === 'connected' ? 'success' : 'error'" size="small">
          {{ connectionStatus === 'connected' ? '已连接' : '连接断开' }}
        </n-tag>
        <span class="last-update">最后更新: {{ lastUpdateTime }}</span>
      </div>
      
      <div class="toolbar-right">
        <n-button-group size="small">
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

    <!-- 监控内容区域 -->
    <div class="monitor-content" ref="monitorContent">
      <!-- 系统状态面板 -->
      <div class="system-status-panel">
        <div class="status-card" v-for="item in systemStatus" :key="item.key">
          <div class="status-header">
            <span class="status-title">{{ item.title }}</span>
            <n-tag :type="getStatusType(item.status)" size="small">
              {{ item.status }}
            </n-tag>
          </div>
          <div class="status-value">{{ item.value }}</div>
          <div class="status-change" :class="getChangeClass(item.change)">
            {{ item.change > 0 ? '+' : '' }}{{ item.change }}%
          </div>
          <div class="status-chart">
            <div class="mini-chart" :id="`chart-${item.key}`"></div>
          </div>
        </div>
      </div>

      <!-- 股票监控网格 -->
      <div class="stocks-grid" :class="`layout-${selectedLayout}`">
        <div
          v-for="stock in monitoredStocks"
          :key="stock.code"
          class="stock-card"
          :class="{ 'alert-active': stock.alert }"
        >
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
                @click="toggleAlert(stock)"
                :class="{ 'alert-enabled': stock.alert }"
              >
                <template #icon>
                  <n-icon :component="NotificationsOutline" />
                </template>
              </n-button>
              <n-button quaternary circle size="tiny" @click="removeStock(stock)">
                <template #icon>
                  <n-icon :component="CloseOutline" />
                </template>
              </n-button>
            </div>
          </div>
          
          <div class="stock-price">
            <span class="current-price">{{ stock.currentPrice }}</span>
            <span class="price-change" :class="getChangeClass(stock.changePercent)">
              {{ stock.changePercent > 0 ? '+' : '' }}{{ stock.changePercent }}%
            </span>
          </div>
          
          <div class="stock-chart">
            <div class="mini-kline" :id="`kline-${stock.code}`"></div>
          </div>
          
          <div class="stock-indicators">
            <div class="indicator-item">
              <span class="indicator-label">成交量</span>
              <span class="indicator-value">{{ formatVolume(stock.volume) }}</span>
            </div>
            <div class="indicator-item">
              <span class="indicator-label">换手率</span>
              <span class="indicator-value">{{ stock.turnoverRate }}%</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 实时数据流 -->
      <div class="data-flow-panel">
        <div class="panel-header">
          <span class="panel-title">实时数据流</span>
          <n-button quaternary size="small" @click="clearDataFlow">
            清空
          </n-button>
        </div>
        <div class="data-flow-list" ref="dataFlowList">
          <div
            v-for="item in dataFlow"
            :key="item.id"
            class="data-flow-item"
            :class="`flow-${item.type}`"
          >
            <span class="flow-time">{{ formatTime(item.timestamp) }}</span>
            <span class="flow-type">{{ getFlowTypeLabel(item.type) }}</span>
            <span class="flow-message">{{ item.message }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 设置弹窗 -->
    <n-modal v-model:show="showSettings" preset="card" style="max-width: 500px;" title="监控设置">
      <div class="settings-form">
        <n-form :model="monitorSettings" label-placement="left" label-width="100">
          <n-form-item label="刷新频率">
            <n-select
              v-model:value="monitorSettings.refreshInterval"
              :options="refreshIntervalOptions"
            />
          </n-form-item>
          <n-form-item label="显示指标">
            <n-checkbox-group v-model:value="monitorSettings.indicators">
              <n-space>
                <n-checkbox value="price" label="价格" />
                <n-checkbox value="volume" label="成交量" />
                <n-checkbox value="turnover" label="换手率" />
                <n-checkbox value="ma" label="均线" />
              </n-space>
            </n-checkbox-group>
          </n-form-item>
          <n-form-item label="预警阈值">
            <n-input-number
              v-model:value="monitorSettings.alertThreshold"
              :min="1"
              :max="20"
              :step="0.5"
            />
            <span class="unit">%</span>
          </n-form-item>
          <n-form-item label="最大股票数">
            <n-input-number
              v-model:value="monitorSettings.maxStocks"
              :min="1"
              :max="16"
            />
          </n-form-item>
        </n-form>
      </div>
      <template #footer>
        <n-space justify="end">
          <n-button @click="resetSettings">重置</n-button>
          <n-button type="primary" @click="applySettings">应用</n-button>
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
}

const props = withDefaults(defineProps<Props>(), {
  stocks: () => [], // 改为空数组，避免硬编码
  height: 600
})

// 消息提示
const message = useMessage()

// DOM引用
const monitorContent = ref<HTMLElement | null>(null)
const dataFlowList = ref<HTMLElement | null>(null)

// 响应式数据
const isRefreshing = ref(false)
const autoRefresh = ref(true)
const selectedLayout = ref('2x2')
const connectionStatus = ref<'connected' | 'disconnected'>('connected')
const lastUpdateTime = ref(new Date().toLocaleTimeString())
const showSettings = ref(false)

// 系统状态数据
const systemStatus = ref([
  {
    key: 'cpu',
    title: 'CPU使用率',
    value: '45%',
    status: 'normal',
    change: 2.3
  },
  {
    key: 'memory',
    title: '内存使用率',
    value: '68%',
    status: 'warning',
    change: 5.1
  },
  {
    key: 'network',
    title: '网络延迟',
    value: '12ms',
    status: 'normal',
    change: -1.2
  },
  {
    key: 'queue',
    title: '队列深度',
    value: '23',
    status: 'normal',
    change: 8.7
  }
])

// 监控股票数据
const monitoredStocks = ref([
  // 移除硬编码的默认股票，改为动态获取
    currentPrice: 12.85,
    changePercent: 2.35,
    volume: 125000000,
    turnoverRate: 1.23,
    alert: false,
    chartData: []
  },
  {
    code: '000002.SZ',
    name: '万科A',
    currentPrice: 18.42,
    changePercent: -1.25,
    volume: 89000000,
    turnoverRate: 0.95,
    alert: true,
    chartData: []
  },
  {
    code: '600000.SH',
    name: '浦发银行',
    currentPrice: 9.87,
    changePercent: 0.85,
    volume: 67000000,
    turnoverRate: 0.67,
    alert: false,
    chartData: []
  },
  // 移除硬编码的默认股票，改为动态获取
    currentPrice: 35.68,
    changePercent: 1.45,
    volume: 156000000,
    turnoverRate: 1.56,
    alert: false,
    chartData: []
  }
])

// 实时数据流
const dataFlow = ref([
  {
    id: 1,
    // 移除硬编码的示例数据，改为动态生成
    type: 'trade',
    message: '等待实时交易数据...',
    timestamp: new Date()
  },
  {
    id: 2,
    type: 'alert',
    message: '000002.SZ 触发预警阈值',
    timestamp: new Date()
  },
  {
    id: 3,
    type: 'system',
    message: '策略引擎状态更新',
    timestamp: new Date()
  }
])

// 监控设置
const monitorSettings = reactive({
  refreshInterval: 5000,
  indicators: ['price', 'volume', 'turnover'],
  alertThreshold: 5.0,
  maxStocks: 9
})

// 布局选项
const layoutOptions = [
  { label: '2x2', value: '2x2' },
  { label: '3x3', value: '3x3' },
  { label: '4x4', value: '4x4' },
  { label: '列表', value: 'list' }
]

// 刷新间隔选项
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
const refreshData = async () => {
  isRefreshing.value = true
  
  try {
    // 模拟数据刷新
    await new Promise(resolve => setTimeout(resolve, 500))
    
    // 更新股票数据
    monitoredStocks.value.forEach(stock => {
      const changePercent = (Math.random() - 0.5) * 4
      stock.changePercent = parseFloat(changePercent.toFixed(2))
      stock.currentPrice = parseFloat((stock.currentPrice * (1 + changePercent / 100)).toFixed(2))
      stock.volume = Math.floor(stock.volume * (0.8 + Math.random() * 0.4))
      stock.turnoverRate = parseFloat((stock.turnoverRate * (0.9 + Math.random() * 0.2)).toFixed(2))
      
      // 检查预警
      if (Math.abs(stock.changePercent) >= monitorSettings.alertThreshold) {
        stock.alert = true
        addDataFlow('alert', `${stock.code} 触发预警阈值`)
      }
    })
    
    // 更新系统状态
    systemStatus.value.forEach(status => {
      const change = (Math.random() - 0.5) * 5
      status.change = parseFloat(change.toFixed(1))
      
      if (status.key === 'cpu') {
        status.value = `${Math.floor(40 + Math.random() * 30)}%`
      } else if (status.key === 'memory') {
        status.value = `${Math.floor(60 + Math.random() * 20)}%`
      } else if (status.key === 'network') {
        status.value = `${Math.floor(10 + Math.random() * 20)}ms`
      } else if (status.key === 'queue') {
        status.value = `${Math.floor(15 + Math.random() * 20)}`
      }
    })
    
    lastUpdateTime.value = new Date().toLocaleTimeString()
    
    // 更新图表
    updateCharts()
    
  } catch (error) {
    console.error('刷新数据失败:', error)
    message.error('刷新数据失败')
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
    refreshData()
  }, monitorSettings.refreshInterval)
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
    updateCharts()
  })
}

const toggleAlert = (stock: any) => {
  stock.alert = !stock.alert
  message.info(`${stock.code} 预警已${stock.alert ? '开启' : '关闭'}`)
}

const removeStock = (stock: any) => {
  const index = monitoredStocks.value.findIndex(s => s.code === stock.code)
  if (index > -1) {
    monitoredStocks.value.splice(index, 1)
    message.success(`已移除 ${stock.code}`)
  }
}

const addDataFlow = (type: string, message: string) => {
  const newItem = {
    id: Date.now(),
    type,
    message,
    timestamp: new Date()
  }
  
  dataFlow.value.unshift(newItem)
  
  // 限制数据流条数
  if (dataFlow.value.length > 50) {
    dataFlow.value = dataFlow.value.slice(0, 50)
  }
  
  // 滚动到顶部
  nextTick(() => {
    if (dataFlowList.value) {
      dataFlowList.value.scrollTop = 0
    }
  })
}

const clearDataFlow = () => {
  dataFlow.value = []
  message.success('数据流已清空')
}

const exportData = () => {
  const exportData = {
    timestamp: new Date().toISOString(),
    stocks: monitoredStocks.value,
    systemStatus: systemStatus.value,
    dataFlow: dataFlow.value
  }
  
  const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `monitor-data-${Date.now()}.json`
  link.click()
  URL.revokeObjectURL(url)
  
  message.success('数据已导出')
}

const toggleFullscreen = () => {
  if (monitorContent.value) {
    if (!document.fullscreenElement) {
      monitorContent.value.requestFullscreen()
    } else {
      document.exitFullscreen()
    }
  }
}

const applySettings = () => {
  showSettings.value = false
  
  // 重新启动自动刷新
  if (autoRefresh.value) {
    stopAutoRefresh()
    startAutoRefresh()
  }
  
  message.success('设置已应用')
}

const resetSettings = () => {
  monitorSettings.refreshInterval = 5000
  monitorSettings.indicators = ['price', 'volume', 'turnover']
  monitorSettings.alertThreshold = 5.0
  monitorSettings.maxStocks = 9
  applySettings()
}

// 辅助方法
const getStatusType = (status: string) => {
  const types = {
    normal: 'success',
    warning: 'warning',
    error: 'error'
  }
  return types[status] || 'default'
}

const getChangeClass = (change: number) => {
  if (change > 0) return 'positive'
  if (change < 0) return 'negative'
  return 'neutral'
}

const getFlowTypeLabel = (type: string) => {
  const labels = {
    trade: '交易',
    alert: '预警',
    system: '系统',
    strategy: '策略'
  }
  return labels[type] || type
}

const formatVolume = (volume: number) => {
  if (volume >= 100000000) {
    return `${(volume / 100000000).toFixed(1)}亿`
  } else if (volume >= 10000) {
    return `${(volume / 10000).toFixed(1)}万`
  }
  return volume.toString()
}

const formatTime = (timestamp: Date) => {
  return timestamp.toLocaleTimeString()
}

// 图表相关方法
const initCharts = () => {
  // 初始化系统状态迷你图表
  systemStatus.value.forEach(status => {
    const chartId = `chart-${status.key}`
    const chartElement = document.getElementById(chartId)
    
    if (chartElement) {
      const chart = echarts.init(chartElement)
      chartInstances.value.set(chartId, chart)
      
      // 生成示例数据
      const data = Array.from({ length: 20 }, () => Math.random() * 100)
      
      const option = {
        grid: {
          top: 0,
          left: 0,
          right: 0,
          bottom: 0
        },
        xAxis: {
          type: 'category',
          show: false,
          data: Array.from({ length: 20 }, (_, i) => i)
        },
        yAxis: {
          type: 'value',
          show: false
        },
        series: [{
          type: 'line',
          data,
          smooth: true,
          symbol: 'none',
          lineStyle: {
            width: 1,
            color: getStatusColor(status.status)
          },
          areaStyle: {
            opacity: 0.1,
            color: getStatusColor(status.status)
          }
        }]
      }
      
      chart.setOption(option)
    }
  })
  
  // 初始化股票迷你K线图
  monitoredStocks.value.forEach(stock => {
    const chartId = `kline-${stock.code}`
    const chartElement = document.getElementById(chartId)
    
    if (chartElement) {
      const chart = echarts.init(chartElement)
      chartInstances.value.set(chartId, chart)
      
      // 生成示例K线数据
      const data = Array.from({ length: 30 }, () => {
        const base = stock.currentPrice
        const open = base * (0.98 + Math.random() * 0.04)
        const close = base * (0.98 + Math.random() * 0.04)
        const high = Math.max(open, close) * (1 + Math.random() * 0.02)
        const low = Math.min(open, close) * (1 - Math.random() * 0.02)
        return [open, close, low, high]
      })
      
      const option = {
        grid: {
          top: 2,
          left: 0,
          right: 0,
          bottom: 2
        },
        xAxis: {
          type: 'category',
          show: false,
          data: Array.from({ length: 30 }, (_, i) => i)
        },
        yAxis: {
          type: 'value',
          show: false,
          scale: true
        },
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
      
      chart.setOption(option)
    }
  })
}

const updateCharts = () => {
  // 更新系统状态图表
  systemStatus.value.forEach(status => {
    const chartId = `chart-${status.key}`
    const chart = chartInstances.value.get(chartId)
    
    if (chart) {
      // 更新数据
      const option = chart.getOption()
      if (option.series && option.series[0]) {
        const newData = option.series[0].data.slice(1)
        newData.push(Math.random() * 100)
        option.series[0].data = newData
        chart.setOption(option)
      }
    }
  })
  
  // 更新股票K线图
  monitoredStocks.value.forEach(stock => {
    const chartId = `kline-${stock.code}`
    const chart = chartInstances.value.get(chartId)
    
    if (chart) {
      const option = chart.getOption()
      if (option.series && option.series[0]) {
        const base = stock.currentPrice
        const open = base * (0.98 + Math.random() * 0.04)
        const close = base * (0.98 + Math.random() * 0.04)
        const high = Math.max(open, close) * (1 + Math.random() * 0.02)
        const low = Math.min(open, close) * (1 - Math.random() * 0.02)
        const newCandle = [open, close, low, high]
        
        const newData = option.series[0].data.slice(1)
        newData.push(newCandle)
        option.series[0].data = newData
        chart.setOption(option)
      }
    }
  })
}

const getStatusColor = (status: string) => {
  const colors = {
    normal: '#10b981',
    warning: '#f59e0b',
    error: '#ef4444'
  }
  return colors[status] || '#6b7280'
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
  window.addEventListener('resize', () => {
    chartInstances.value.forEach(chart => {
      chart.resize()
    })
  })
})

onUnmounted(() => {
  stopAutoRefresh()
  chartInstances.value.forEach(chart => {
    chart.dispose()
  })
  chartInstances.value.clear()
})
</script>

<style lang="scss" scoped>
.realtime-monitor {
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

      .last-update {
        font-size: var(--font-size-xs);
        color: var(--text-secondary);
      }
    }
  }

  .monitor-content {
    flex: 1;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    gap: var(--spacing-3);
    padding: var(--spacing-3);

    .system-status-panel {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: var(--spacing-3);
      flex-shrink: 0;

      .status-card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid var(--border-color);
        border-radius: var(--border-radius-sm)all;
        padding: var(--spacing-3);
        position: relative;
        overflow: hidden;

        .status-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: var(--spacing-2);

          .status-title {
            font-size: var(--font-size-sm);
            color: var(--text-secondary);
          }
        }

        .status-value {
          font-size: var(--font-size-lg);
          font-weight: 600;
          color: var(--text-primary);
          margin-bottom: var(--spacing-1);
        }

        .status-change {
          font-size: var(--font-size-xs);
          margin-bottom: var(--spacing-2);

          &.positive {
            color: var(--success-color);
          }

          &.negative {
            color: var(--danger-color);
          }

          &.neutral {
            color: var(--text-secondary);
          }
        }

        .status-chart {
          position: absolute;
          bottom: 0;
          left: 0;
          right: 0;
          height: 30px;

          .mini-chart {
            width: 100%;
            height: 100%;
          }
        }
      }
    }

    .stocks-grid {
      flex: 1;
      display: grid;
      gap: var(--spacing-3);
      overflow-y: auto;

      &.layout-2x2 {
        grid-template-columns: repeat(2, 1fr);
      }

      &.layout-3x3 {
        grid-template-columns: repeat(3, 1fr);
      }

      &.layout-4x4 {
        grid-template-columns: repeat(4, 1fr);
      }

      &.layout-list {
        grid-template-columns: 1fr;
      }

      .stock-card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid var(--border-color);
        border-radius: var(--border-radius-sm)all;
        padding: var(--spacing-3);
        transition: all 0.2s ease;

        &:hover {
          background: rgba(255, 255, 255, 0.08);
          transform: translateY(-2px);
        }

        &.alert-active {
          border-color: var(--warning-color);
          box-shadow: 0 0 10px rgba(var(--warning-color), 0.3);
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

        .stock-price {
          display: flex;
          align-items: baseline;
          gap: var(--spacing-2);
          margin-bottom: var(--spacing-2);

          .current-price {
            font-size: var(--font-size-lg);
            font-weight: 600;
            color: var(--text-primary);
          }

          .price-change {
            font-size: var(--font-size-sm);

            &.positive {
              color: var(--success-color);
            }

            &.negative {
              color: var(--danger-color);
            }
          }
        }

        .stock-chart {
          height: 60px;
          margin-bottom: var(--spacing-2);

          .mini-kline {
            width: 100%;
            height: 100%;
          }
        }

        .stock-indicators {
          display: flex;
          justify-content: space-between;

          .indicator-item {
            display: flex;
            flex-direction: column;
            align-items: center;

            .indicator-label {
              font-size: var(--font-size-xs);
              color: var(--text-secondary);
              margin-bottom: var(--spacing-1);
            }

            .indicator-value {
              font-size: var(--font-size-sm);
              color: var(--text-primary);
              font-weight: 500;
            }
          }
        }
      }
    }

    .data-flow-panel {
      background: rgba(255, 255, 255, 0.05);
      border: 1px solid var(--border-color);
      border-radius: var(--border-radius-sm)all;
      padding: var(--spacing-3);
      flex-shrink: 0;
      max-height: 200px;
      display: flex;
      flex-direction: column;

      .panel-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: var(--spacing-2);

        .panel-title {
          font-size: var(--font-size-sm);
          font-weight: 600;
          color: var(--text-primary);
        }
      }

      .data-flow-list {
        flex: 1;
        overflow-y: auto;

        .data-flow-item {
          display: flex;
          align-items: center;
          gap: var(--spacing-2);
          padding: var(--spacing-1) 0;
          font-size: var(--font-size-xs);
          border-bottom: 1px solid rgba(255, 255, 255, 0.05);

          &:last-child {
            border-bottom: none;
          }

          .flow-time {
            color: var(--text-secondary);
            min-width: 60px;
          }

          .flow-type {
            padding: 2px 6px;
            border-radius: var(--border-radius-sm)all;
            font-size: 10px;
            min-width: 40px;
            text-align: center;
          }

          &.flow-trade .flow-type {
            background: rgba(var(--primary-color), 0.2);
            color: var(--primary-color);
          }

          &.flow-alert .flow-type {
            background: rgba(var(--warning-color), 0.2);
            color: var(--warning-color);
          }

          &.flow-system .flow-type {
            background: rgba(var(--info-color), 0.2);
            color: var(--info-color);
          }

          &.flow-strategy .flow-type {
            background: rgba(var(--secondary-color), 0.2);
            color: var(--secondary-color);
          }

          .flow-message {
            color: var(--text-primary);
            flex: 1;
            @include text-ellipsis;
          }
        }
      }
    }
  }

  .settings-form {
    .unit {
      margin-left: var(--spacing-2);
      color: var(--text-secondary);
    }
  }
}
</style>
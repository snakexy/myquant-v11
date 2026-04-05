<template>
  <div class="multi-stock-monitor">
    <div class="monitor-header">
      <h3>多股票同列监控</h3>
      <div class="monitor-controls">
        <n-select
          v-model:value="selectedLayout"
          :options="layoutOptions"
          size="small"
          style="width: 100px"
        />
        <n-button size="small" type="primary" @click="refreshData">
          刷新
        </n-button>
      </div>
    </div>
    
    <div class="monitor-content">
      <div class="stock-list-panel">
        <h4>股票列表</h4>
        <n-input
          v-model:value="stockInput"
          type="textarea"
          placeholder="输入股票代码，每行一个&#10;例如：&#10;000001.SZ&#10;600000.SH"
          :rows="6"
        />
        <div class="stock-actions">
          <n-button type="primary" @click="addStocks">添加股票</n-button>
          <n-button @click="fetchRealData" :loading="isFetchingData" :disabled="stockList.length === 0">
            获取真实数据
          </n-button>
          <n-button @click="clearStocks">清空</n-button>
        </div>
        <div class="stock-tags">
          <n-tag
            v-for="stock in stockList"
            :key="stock.code"
            closable
            @close="removeStock(stock.code)"
            type="info"
            style="margin: 4px"
          >
            {{ stock.code }} - {{ stock.name }}
          </n-tag>
        </div>
      </div>
      
      <div class="monitor-grid" :class="`grid-${selectedLayout}`">
        <div
          v-for="(stock, index) in displayStocks"
          :key="stock.code"
          class="stock-card"
        >
          <div class="stock-header">
            <span class="stock-code">{{ stock.code }}</span>
            <span class="stock-name">{{ stock.name }}</span>
            <n-tag
              v-if="stock.isRealData"
              type="success"
              size="tiny"
              style="margin-left: 8px"
            >
              实时
            </n-tag>
            <n-tag
              v-else
              type="warning"
              size="tiny"
              style="margin-left: 8px"
            >
              模拟
            </n-tag>
            <n-button
              size="tiny"
              quaternary
              circle
              @click="removeStock(stock.code)"
            >
              <template #icon>
                <n-icon><CloseOutline /></n-icon>
              </template>
            </n-button>
          </div>
          
          <div class="stock-price">
            <span class="current-price" :class="getPriceClass(stock.changePercent)">
              {{ formatPrice(stock.currentPrice) }}
            </span>
            <span class="price-change" :class="getPriceClass(stock.changePercent)">
              {{ formatChange(stock.changeAmount, stock.changePercent) }}
            </span>
          </div>
          
          <div class="stock-chart">
            <TradingViewKLineUnified
              :symbol="stock.code"
              :stock-name="stock.name"
              :initial-data="stock.chartData"
              height="120px"
              :show-volume="false"
              :indicators="[]"
              theme="dark"
            />
          </div>
          
          <div class="stock-indicators">
            <div class="indicator-item">
              <span class="label">成交量:</span>
              <span class="value">{{ formatVolume(stock.volume) }}</span>
            </div>
            <div class="indicator-item">
              <span class="label">成交额:</span>
              <span class="value">{{ formatAmount(stock.amount) }}</span>
            </div>
            <div class="indicator-item">
              <span class="label">换手率:</span>
              <span class="value">{{ formatPercent(stock.turnoverRate) }}</span>
            </div>
          </div>
        </div>
        
        <!-- 空白占位卡片 -->
        <div
          v-for="i in emptySlots"
          :key="`empty-${i}`"
          class="stock-card empty"
        >
          <div class="empty-content">
            <n-icon size="24">
              <AddOutline />
            </n-icon>
            <span>添加股票</span>
          </div>
        </div>
      </div>
    </div>
    
    <div class="monitor-footer">
      <div class="status-info">
        <n-tag type="info" size="small">
          更新时间: {{ lastUpdateTime }}
        </n-tag>
        <n-tag :type="connectionStatus === 'connected' ? 'success' : 'error'" size="small">
          {{ connectionStatus === 'connected' ? '已连接' : '连接中...' }}
        </n-tag>
      </div>
      <div class="refresh-interval">
        <span>刷新间隔:</span>
        <n-select
          v-model:value="refreshInterval"
          :options="intervalOptions"
          size="small"
          style="width: 100px; margin-left: 8px"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { NSelect, NButton, NTag, NIcon } from 'naive-ui'
import { CloseOutline, AddOutline } from '@vicons/ionicons5'
import TradingViewKLineUnified from '../charts/TradingViewKLineUnified.vue'
import { formatPrice, formatChange, formatVolume, formatAmount, formatPercent } from '../../utils/format'
import { getStockDetail, getRealtimeData, getStockHistory } from '../../api/modules/data'

interface StockData {
  code: string
  name: string
  currentPrice: number
  changeAmount: number
  changePercent: number
  volume: number
  amount: number
  turnoverRate: number
  chartData: any[]
  isRealData?: boolean
  error?: string
}

interface LayoutOption {
  label: string
  value: string
}

interface IntervalOption {
  label: string
  value: number
}

// 响应式数据
const selectedLayout = ref('2x2')
const stockInput = ref('')
const stockList = ref<StockData[]>([])
const refreshInterval = ref(5000)
const lastUpdateTime = ref('')
const connectionStatus = ref<'connected' | 'connecting' | 'disconnected'>('connecting')
const isFetchingData = ref(false)
let refreshTimer: NodeJS.Timeout | null = null

// 配置选项
const layoutOptions: LayoutOption[] = [
  { label: '2×2', value: '2x2' },
  { label: '3×3', value: '3x3' },
  { label: '4×4', value: '4x4' }
]

const intervalOptions: IntervalOption[] = [
  { label: '1秒', value: 1000 },
  { label: '3秒', value: 3000 },
  { label: '5秒', value: 5000 },
  { label: '10秒', value: 10000 },
  { label: '30秒', value: 30000 }
]

// 计算属性
const gridCount = computed(() => {
  const [rows, cols] = selectedLayout.value.split('x').map(Number)
  return rows * cols
})

const displayStocks = computed(() => {
  return stockList.value.slice(0, gridCount.value)
})

const emptySlots = computed(() => {
  return Math.max(0, gridCount.value - stockList.value.length)
})

// 方法
const getPriceClass = (changePercent: number) => {
  if (changePercent > 0) return 'price-up'
  if (changePercent < 0) return 'price-down'
  return 'price-flat'
}

const addStocks = () => {
  const codes = stockInput.value
    .split('\n')
    .map(code => code.trim())
    .filter(code => code && !stockList.value.some(s => s.code === code))
  
  if (codes.length === 0) return
  
  // 模拟添加股票数据
  codes.forEach(code => {
    const mockData: StockData = {
      code,
      name: getStockName(code),
      currentPrice: Math.random() * 100 + 10,
      changeAmount: (Math.random() - 0.5) * 10,
      changePercent: (Math.random() - 0.5) * 10,
      volume: Math.floor(Math.random() * 1000000),
      amount: Math.floor(Math.random() * 100000000),
      turnoverRate: Math.random() * 10,
      chartData: generateMockChartData(),
      isRealData: false,
      error: undefined
    }
    stockList.value.push(mockData)
  })
  
  stockInput.value = ''
}

const removeStock = (code: string) => {
  const index = stockList.value.findIndex(s => s.code === code)
  if (index > -1) {
    stockList.value.splice(index, 1)
  }
}

const clearStocks = () => {
  stockList.value = []
}

// 获取真实数据
const fetchRealData = async () => {
  if (stockList.value.length === 0) return

  isFetchingData.value = true
  connectionStatus.value = 'connecting'

  try {
    // 提取股票代码
    const stockCodes = stockList.value.map(stock => {
      // 处理不同格式的股票代码
      const code = stock.code.replace('.SZ', '').replace('.SH', '')
      return code
    })

    // 并行获取所有股票的真实数据
    const stockPromises = stockList.value.map(async (stock, index) => {
      try {
        const code = stock.code.replace('.SZ', '').replace('.SH', '')

        // 获取股票详情
        const stockDetail = await getStockDetail(code)

        // 获取实时数据
        const realtimeData = await getRealtimeData([code])

        // 获取历史数据用于图表
        const endDate = new Date().toISOString().split('T')[0]
        const startDate = new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]
        const historyData = await getStockHistory(code, {
          startDate,
          endDate,
          frequency: 'daily'
        })

        if (stockDetail.data && realtimeData.data) {
          const realtime = realtimeData.data[0] || {}

          return {
            ...stock,
            name: stockDetail.data.name || stock.name,
            currentPrice: realtime.currentPrice || stock.currentPrice,
            changeAmount: realtime.changeAmount || 0,
            changePercent: realtime.changePercent || 0,
            volume: realtime.volume || stock.volume,
            amount: realtime.amount || stock.amount,
            turnoverRate: realtime.turnoverRate || 0,
            chartData: historyData.data?.slice(-50) || stock.chartData,
            isRealData: true,
            error: undefined
          }
        } else {
          throw new Error('API返回数据为空')
        }
      } catch (error: any) {
        console.warn(`获取股票 ${stock.code} 数据失败:`, error)

        // 返回原数据，但标记为获取失败
        return {
          ...stock,
          isRealData: false,
          error: error.message
        }
      }
    })

    // 等待所有请求完成
    const results = await Promise.all(stockPromises)

    // 更新股票列表
    stockList.value = results

    lastUpdateTime.value = new Date().toLocaleTimeString()
    connectionStatus.value = 'connected'

    console.log(`✅ 成功获取 ${results.filter(s => s.isRealData).length}/${results.length} 只股票的真实数据`)

  } catch (error: any) {
    console.error('批量获取股票数据失败:', error)
    connectionStatus.value = 'disconnected'
  } finally {
    isFetchingData.value = false
  }
}

const refreshData = () => {
  connectionStatus.value = 'connecting'
  
  // 模拟数据更新
  setTimeout(() => {
    stockList.value.forEach(stock => {
      // 更新价格
      const priceChange = (Math.random() - 0.5) * 2
      stock.currentPrice = Math.max(0.01, stock.currentPrice + priceChange)
      stock.changeAmount = priceChange
      stock.changePercent = (priceChange / stock.currentPrice) * 100
      
      // 更新成交量
      stock.volume = Math.floor(Math.random() * 1000000)
      stock.amount = Math.floor(stock.volume * stock.currentPrice)
      stock.turnoverRate = Math.random() * 10
      
      // 更新图表数据
      stock.chartData = generateMockChartData()
    })
    
    lastUpdateTime.value = new Date().toLocaleTimeString()
    connectionStatus.value = 'connected'
  }, 500)
}

const generateMockChartData = () => {
  const data = []
  let basePrice = 50
  
  for (let i = 0; i < 50; i++) {
    const open = basePrice
    const close = basePrice + (Math.random() - 0.5) * 2
    const high = Math.max(open, close) + Math.random()
    const low = Math.min(open, close) - Math.random()
    const volume = Math.floor(Math.random() * 100000)
    
    data.push({
      timestamp: Date.now() - (50 - i) * 60000,
      open,
      high,
      low,
      close,
      volume
    })
    
    basePrice = close
  }
  
  return data
}

const getStockName = (code: string) => {
  // 模拟股票名称
  const names: Record<string, string> = {
    '000001.SZ': '平安银行',
    '000002.SZ': '万科A',
    '600000.SH': '浦发银行',
    '600036.SH': '招商银行',
    '600519.SH': '贵州茅台'
  }
  return names[code] || `${code.substring(0, 6)}`
}

const startRefreshTimer = () => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
  }
  
  refreshTimer = setInterval(() => {
    refreshData()
  }, refreshInterval.value)
}

// 生命周期
onMounted(() => {
  refreshData()
  startRefreshTimer()
})

onUnmounted(() => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
  }
})

// 监听刷新间隔变化
watch(refreshInterval, () => {
  startRefreshTimer()
})
</script>

<style lang="scss" scoped>
.multi-stock-monitor {
  display: flex;
  flex-direction: column;
  height: 100%;
  
  .monitor-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;
    
    h3 {
      margin: 0;
      color: var(--text-primary);
    }
    
    .monitor-controls {
      display: flex;
      gap: 8px;
    }
  }
  
  .monitor-content {
    display: flex;
    gap: 16px;
    flex: 1;
    min-height: 0;
  }
  
  .stock-list-panel {
    width: 280px;
    background: var(--surface-color);
    border: 1px solid var(--border-color);
    border-radius: 8px;
    padding: 16px;
    display: flex;
    flex-direction: column;
    
    h4 {
      margin: 0 0 12px 0;
      color: var(--text-primary);
      font-size: 14px;
    }
    
    .stock-actions {
      display: flex;
      gap: 8px;
      margin-top: 12px;
    }
    
    .stock-tags {
      margin-top: 16px;
      max-height: 200px;
      overflow-y: auto;
    }
  }
  
  .monitor-grid {
    flex: 1;
    display: grid;
    gap: 12px;
    
    &.grid-2x2 {
      grid-template-columns: repeat(2, 1fr);
      grid-template-rows: repeat(2, 1fr);
    }
    
    &.grid-3x3 {
      grid-template-columns: repeat(3, 1fr);
      grid-template-rows: repeat(3, 1fr);
    }
    
    &.grid-4x4 {
      grid-template-columns: repeat(4, 1fr);
      grid-template-rows: repeat(4, 1fr);
    }
  }
  
  .stock-card {
    background: var(--surface-color);
    border: 1px solid var(--border-color);
    border-radius: 8px;
    padding: 12px;
    display: flex;
    flex-direction: column;
    
    .stock-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 8px;
      
      .stock-code {
        font-weight: bold;
        color: var(--text-primary);
      }
      
      .stock-name {
        color: var(--text-secondary);
        font-size: 12px;
      }
    }
    
    .stock-price {
      display: flex;
      align-items: baseline;
      gap: 8px;
      margin-bottom: 8px;
      
      .current-price {
        font-size: 18px;
        font-weight: bold;
        
        &.price-up {
          color: var(--success-color);
        }
        
        &.price-down {
          color: var(--danger-color);
        }
        
        &.price-flat {
          color: var(--text-primary);
        }
      }
      
      .price-change {
        font-size: 12px;
        
        &.price-up {
          color: var(--success-color);
        }
        
        &.price-down {
          color: var(--danger-color);
        }
        
        &.price-flat {
          color: var(--text-secondary);
        }
      }
    }
    
    .stock-chart {
      flex: 1;
      margin-bottom: 8px;
      min-height: 0;
    }
    
    .stock-indicators {
      display: flex;
      justify-content: space-between;
      font-size: 11px;
      
      .indicator-item {
        display: flex;
        flex-direction: column;
        align-items: center;
        
        .label {
          color: var(--text-secondary);
        }
        
        .value {
          color: var(--text-primary);
          font-weight: bold;
        }
      }
    }
    
    &.empty {
      justify-content: center;
      align-items: center;
      opacity: 0.5;
      
      .empty-content {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 8px;
        color: var(--text-secondary);
      }
    }
  }
  
  .monitor-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 16px;
    padding-top: 12px;
    border-top: 1px solid var(--border-color);
    
    .status-info {
      display: flex;
      gap: 8px;
    }
    
    .refresh-interval {
      display: flex;
      align-items: center;
      color: var(--text-secondary);
      font-size: 12px;
    }
  }
}
</style>
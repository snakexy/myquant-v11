<template>
  <div class="realtime-test-view">
    <div class="header">
      <h1>实时数据流测试</h1>
      <p>Real-time Data Streaming Test</p>
    </div>

    <!-- WebSocket状态 -->
    <div class="status-panel">
      <el-card>
        <template #header>
          <span>WebSocket状态</span>
        </template>
        <div class="status-grid">
          <div class="status-item">
            <span class="label">连接状态:</span>
            <el-tag :type="connected ? 'success' : 'danger'">
              {{ connected ? '已连接' : '未连接' }}
            </el-tag>
          </div>
          <div class="status-item">
            <span class="label">订阅行情:</span>
            <el-tag type="info">{{ subscribedQuotes.size }}</el-tag>
          </div>
          <div class="status-item">
            <span class="label">订阅K线:</span>
            <el-tag type="info">{{ subscribedKlines.size }}</el-tag>
          </div>
          <div class="status-item">
            <span class="label">订阅板块:</span>
            <el-tag type="info">{{ subscribedSectors.size }}</el-tag>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 订阅控制 -->
    <div class="control-panel">
      <el-card>
        <template #header>
          <span>订阅控制</span>
        </template>

        <el-form :inline="true">
          <!-- 行情订阅 -->
          <el-form-item label="订阅行情">
            <el-select
              v-model="quoteSymbols"
              multiple
              placeholder="选择股票"
              style="width: 300px"
            >
              <el-option
                v-for="stock in hotStocks"
                :key="stock.value"
                :label="stock.label"
                :value="stock.value"
              />
            </el-select>
            <el-button
              type="primary"
              @click="handleSubscribeQuotes"
              :disabled="!connected"
              style="margin-left: 10px"
            >
              订阅
            </el-button>
          </el-form-item>

          <!-- K线订阅 -->
          <el-form-item label="订阅K线">
            <el-select v-model="klineSymbol" placeholder="选择股票" style="width: 150px">
              <el-option
                v-for="stock in hotStocks"
                :key="stock.value"
                :label="stock.label"
                :value="stock.value"
              />
            </el-select>
            <el-select v-model="klinePeriod" style="width: 100px; margin-left: 10px">
              <el-option label="日K" value="day" />
              <el-option label="5分" value="5min" />
              <el-option label="15分" value="15min" />
              <el-option label="30分" value="30min" />
              <el-option label="60分" value="60min" />
            </el-select>
            <el-button
              type="primary"
              @click="handleSubscribeKline"
              :disabled="!connected"
              style="margin-left: 10px"
            >
              订阅
            </el-button>
          </el-form-item>

          <!-- 板块订阅 -->
          <el-form-item label="订阅板块">
            <el-select
              v-model="sectorCodes"
              multiple
              placeholder="选择板块"
              style="width: 300px"
            >
              <el-option
                v-for="sector in sectors"
                :key="sector.code"
                :label="sector.name"
                :value="sector.code"
              />
            </el-select>
            <el-button
              type="primary"
              @click="handleSubscribeSectors"
              :disabled="!connected"
              style="margin-left: 10px"
            >
              订阅
            </el-button>
          </el-form-item>
        </el-form>
      </el-card>
    </div>

    <!-- 实时数据显示 -->
    <el-row :gutter="20">
      <!-- 行情数据 -->
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>实时行情</span>
          </template>
          <el-table :data="quoteData" stripe max-height="400">
            <el-table-column prop="symbol" label="代码" width="100" />
            <el-table-column prop="price" label="价格" width="100">
              <template #default="{ row }">
                <span :class="getPriceClass(row.change_percent)">
                  {{ row.price?.toFixed(2) || '--' }}
                </span>
              </template>
            </el-table-column>
            <el-table-column prop="change_percent" label="涨跌幅" width="100">
              <template #default="{ row }">
                <span :class="getPriceClass(row.change_percent)">
                  {{ formatPercent(row.change_percent) }}
                </span>
              </template>
            </el-table-column>
            <el-table-column prop="volume" label="成交量">
              <template #default="{ row }">
                {{ formatVolume(row.volume) }}
              </template>
            </el-table-column>
            <el-table-column prop="timestamp" label="时间" width="180">
              <template #default="{ row }">
                {{ formatTime(row.timestamp) }}
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>

      <!-- K线图表 -->
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>实时K线</span>
          </template>
          <TradingViewKLineUnified
            v-if="klineSymbol"
            :symbol="formattedKlineSymbol"
            :period="mapPeriodToKlinePeriod(klinePeriod)"
            height="400px"
          />
          <div v-else class="empty-state">
            <p>请选择股票订阅K线数据</p>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 板块数据 -->
    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="24">
        <el-card>
          <template #header>
            <span>实时板块</span>
          </template>
          <el-table :data="sectorData" stripe max-height="300">
            <el-table-column prop="sector_name" label="板块名称" width="150" />
            <el-table-column label="强度得分" width="120">
              <template #default="{ row }">
                <el-tag :type="getStrengthType(row.strength?.strength_score)">
                  {{ row.strength?.strength_score?.toFixed(2) || '--' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="平均涨跌幅" width="120">
              <template #default="{ row }">
                <span :class="getPriceClass(row.strength?.avg_change)">
                  {{ formatPercent(row.strength?.avg_change) }}
                </span>
              </template>
            </el-table-column>
            <el-table-column prop="strength.up_count" label="上涨" width="80" />
            <el-table-column prop="strength.down_count" label="下跌" width="80" />
            <el-table-column prop="strength.up_ratio" label="上涨占比" width="120">
              <template #default="{ row }">
                {{ row.strength?.up_ratio?.toFixed(2) || '--' }}%
              </template>
            </el-table-column>
            <el-table-column prop="timestamp" label="更新时间" width="180">
              <template #default="{ row }">
                {{ formatTime(row.timestamp) }}
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>

    <!-- 消息日志 -->
    <el-card style="margin-top: 20px">
      <template #header>
        <span>消息日志</span>
      </template>
      <div class="message-log">
        <div
          v-for="(msg, index) in messageLog"
          :key="index"
          class="log-entry"
          :class="msg.type"
        >
          <span class="log-time">{{ msg.time }}</span>
          <span class="log-type">{{ msg.type }}</span>
          <span class="log-message">{{ msg.message }}</span>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import TradingViewKLineUnified from '@/components/charts/TradingViewKLineUnified.vue'
import { useGlobalWebSocketEnhanced } from '@/composables/useWebSocketEnhanced'

// WebSocket
const ws = useGlobalWebSocketEnhanced()
const connected = computed(() => ws.connected.value)
const subscribedQuotes = computed(() => ws.subscribedQuotes.value)
const subscribedKlines = computed(() => ws.subscribedKlines.value)
const subscribedSectors = computed(() => ws.subscribedSectors.value)

// 热门股票
const hotStocks = ref([
  { label: '贵州茅台 (600519)', value: '600519' },
  { label: '浦发银行 (600000)', value: '600000' },
  { label: '招商银行 (600036)', value: '600036' },
  { label: '中国平安 (601318)', value: '601318' },
  { label: '工商银行 (601398)', value: '601398' },
  { label: '平安银行 (000001)', value: '000001' },
  { label: '万科A (000002)', value: '000002' },
  { label: '五粮液 (000858)', value: '000858' },
  { label: '海康威视 (002415)', value: '002415' },
  { label: '比亚迪 (002594)', value: '002594' }
])

// 板块
const sectors = ref([
  { code: 'BK0001', name: '金融' },
  { code: 'BK0002', name: '科技' },
  { code: 'BK0003', name: '医药' },
  { code: 'BK0004', name: '消费' },
  { code: 'BK0005', name: '能源' },
  { code: 'BK0006', name: '地产' },
  { code: 'BK0007', name: '汽车' },
  { code: 'BK0008', name: '军工' },
  { code: 'BK0009', name: '新能源' },
  { code: 'BK0010', name: '半导体' }
])

// 订阅控制
const quoteSymbols = ref<string[]>(['600519', '600000'])
const klineSymbol = ref('600519')
const klinePeriod = ref('day')
const sectorCodes = ref<string[]>(['BK0001', 'BK0002'])

// 格式化K线股票代码
const formattedKlineSymbol = computed(() => {
  const code = klineSymbol.value
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

// 映射周期到K线周期
const mapPeriodToKlinePeriod = (period: string) => {
  const periodMap: Record<string, string> = {
    'day': 'day',
    '5min': '5m',
    '15min': '15m',
    '30min': '30m',
    '60min': '60m'
  }
  return periodMap[period] || 'day'
}

// 数据
const quoteData = ref<any[]>([])
const sectorData = ref<any[]>([])
const messageLog = ref<any[]>([])

// 添加日志
const addLog = (type: string, message: string) => {
  messageLog.value.unshift({
    time: new Date().toLocaleTimeString('zh-CN'),
    type,
    message
  })
  // 保持最多100条日志
  if (messageLog.value.length > 100) {
    messageLog.value = messageLog.value.slice(0, 100)
  }
}

// 订阅行情
const handleSubscribeQuotes = () => {
  if (quoteSymbols.value.length === 0) {
    ElMessage.warning('请选择要订阅的股票')
    return
  }

  ws.subscribeQuotes(quoteSymbols.value)
  addLog('info', `订阅行情: ${quoteSymbols.value.join(', ')}`)
}

// 订阅K线
const handleSubscribeKline = () => {
  if (!klineSymbol.value) {
    ElMessage.warning('请选择股票')
    return
  }

  ws.subscribeKlines(klineSymbol.value, klinePeriod.value, 100)
  addLog('info', `订阅K线: ${klineSymbol.value} (${klinePeriod.value})`)
}

// 订阅板块
const handleSubscribeSectors = () => {
  if (sectorCodes.value.length === 0) {
    ElMessage.warning('请选择要订阅的板块')
    return
  }

  ws.subscribeSectors(sectorCodes.value)
  addLog('info', `订阅板块: ${sectorCodes.value.join(', ')}`)
}

// 格式化函数
const formatPercent = (value: number) => {
  if (value === undefined || value === null) return '--'
  return `${value > 0 ? '+' : ''}${value.toFixed(2)}%`
}

const formatVolume = (value: number) => {
  if (!value) return '--'
  if (value >= 100000000) return `${(value / 100000000).toFixed(2)}亿`
  if (value >= 10000) return `${(value / 10000).toFixed(2)}万`
  return value.toString()
}

const formatTime = (timestamp: string) => {
  if (!timestamp) return '--'
  return new Date(timestamp).toLocaleTimeString('zh-CN')
}

const getPriceClass = (value: number) => {
  if (!value) return ''
  if (value > 0) return 'text-up'
  if (value < 0) return 'text-down'
  return 'text-flat'
}

const getStrengthType = (value: number) => {
  if (!value) return 'info'
  if (value >= 50) return 'success'
  if (value >= 20) return ''
  if (value >= 0) return 'info'
  return 'danger'
}

// WebSocket消息处理
ws.onQuoteUpdate.value = (update: any) => {
  addLog('quote', `${update.symbol}: ${update.data.price?.toFixed(2)} (${formatPercent(update.data.change_percent)})`)

  // 更新行情数据
  const existingIndex = quoteData.value.findIndex(item => item.symbol === update.symbol)
  if (existingIndex >= 0) {
    quoteData.value[existingIndex] = {
      ...update.data,
      timestamp: update.timestamp
    }
  } else {
    quoteData.value.push({
      ...update.data,
      timestamp: update.timestamp
    })
  }
}

ws.onKlineUpdate.value = (update: any) => {
  addLog('kline', `${update.symbol} (${update.period}): 新K线数据`)
}

ws.onSectorUpdate.value = (update: any) => {
  addLog('sector', `${update.data.sector_name}: 强度 ${update.data.strength.strength_score.toFixed(2)}`)

  // 更新板块数据
  const existingIndex = sectorData.value.findIndex(item => item.sector_code === update.sector_code)
  if (existingIndex >= 0) {
    sectorData.value[existingIndex] = {
      ...update.data,
      timestamp: update.timestamp
    }
  } else {
    sectorData.value.push({
      ...update.data,
      timestamp: update.timestamp
    })
  }
}

// 初始化
onMounted(() => {
  addLog('info', '页面加载完成')

  // 自动订阅默认股票
  setTimeout(() => {
    if (ws.connected.value) {
      handleSubscribeQuotes()
      handleSubscribeKline()
      handleSubscribeSectors()
    } else {
      addLog('warn', 'WebSocket未连接，等待连接...')
    }
  }, 1000)
})
</script>

<style scoped lang="scss">
.realtime-test-view {
  padding: 20px;

  .header {
    text-align: center;
    margin-bottom: 30px;

    h1 {
      font-size: 32px;
      color: #f8fafc;
      margin-bottom: 8px;
    }

    p {
      font-size: 16px;
      color: #94a3b8;
    }
  }

  .status-panel,
  .control-panel {
    margin-bottom: 20px;

    .status-grid {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 20px;

      .status-item {
        display: flex;
        align-items: center;
        gap: 10px;

        .label {
          font-weight: bold;
          color: #cbd5e1;
        }
      }
    }
  }

  .empty-state {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 400px;
    color: #94a3b8;
  }

  .message-log {
    max-height: 300px;
    overflow-y: auto;
    background: #0a0a0f;
    border-radius: 6px;
    padding: 12px;

    .log-entry {
      display: flex;
      gap: 12px;
      padding: 6px 0;
      border-bottom: 1px solid rgba(255, 255, 255, 0.05);
      font-family: 'Courier New', monospace;
      font-size: 13px;

      &:last-child {
        border-bottom: none;
      }

      &.quote {
        .log-type { color: #3b82f6; }
      }

      &.kline {
        .log-type { color: #a855f7; }
      }

      &.sector {
        .log-type { color: #f59e0b; }
      }

      &.info {
        .log-type { color: #10b981; }
      }

      &.warn {
        .log-type { color: #f59e0b; }
      }

      .log-time {
        color: #64748b;
        min-width: 80px;
      }

      .log-type {
        font-weight: bold;
        min-width: 60px;
      }

      .log-message {
        color: #cbd5e1;
        flex: 1;
      }
    }
  }

  .text-up {
    color: #ef4444;
    font-weight: bold;
  }

  .text-down {
    color: #10b981;
    font-weight: bold;
  }

  .text-flat {
    color: #94a3b8;
  }
}
</style>

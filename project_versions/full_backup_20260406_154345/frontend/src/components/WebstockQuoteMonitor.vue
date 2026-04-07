<template>
  <div class="websocket-quote-monitor">
    <!-- 连接状态 -->
    <div class="connection-status">
      <el-tag :type="statusTagType" size="large">
        {{ statusText }}
      </el-tag>
      <el-button
        v-if="!connected"
        type="primary"
        @click="handleConnect"
        :loading="connecting"
      >
        连接
      </el-button>
      <el-button
        v-else
        type="danger"
        @click="handleDisconnect"
      >
        断开
      </el-button>
    </div>

    <!-- 统计信息 -->
    <div class="stats" v-if="connected">
      <el-descriptions :column="4" size="small" border>
        <el-descriptions-item label="订阅股票">
          {{ subscriptionList.length }}
        </el-descriptions-item>
        <el-descriptions-item label="总消息数">
          {{ stats.totalMessages }}
        </el-descriptions-item>
        <el-descriptions-item label="行情更新">
          {{ stats.quoteUpdates }}
        </el-descriptions-item>
        <el-descriptions-item label="最后更新">
          {{ stats.lastUpdateTime || '-' }}
        </el-descriptions-item>
      </el-descriptions>
    </div>

    <!-- 订阅管理 -->
    <div class="subscription-manager">
      <el-input
        v-model="symbolInput"
        placeholder="输入股票代码，用逗号分隔（如：600000.SH,000001.SZ）"
        @keyup.enter="handleSubscribe"
      >
        <template #append>
          <el-button @click="handleSubscribe">订阅</el-button>
        </template>
      </el-input>

      <div class="subscription-list" v-if="subscriptionList.length > 0">
        <el-tag
          v-for="symbol in subscriptionList"
          :key="symbol"
          closable
          @close="handleUnsubscribe(symbol)"
          style="margin: 5px"
        >
          {{ symbol }}
        </el-tag>
      </div>
    </div>

    <!-- 行情列表 -->
    <div class="quotes-table" v-if="subscriptionList.length > 0">
      <el-table :data="quoteList" stripe>
        <el-table-column prop="symbol" label="代码" width="120" />
        <el-table-column prop="name" label="名称" width="120" />
        <el-table-column label="最新价" width="100">
          <template #default="{ row }">
            <span :class=" getPriceClass(row)">
              {{ row.last_price }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="涨跌幅" width="100">
          <template #default="{ row }">
            <span :class=" getChangeClass(row)">
              {{ row.change_pct }}%
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="volume" label="成交量" width="120" />
        <el-table-column prop="amount" label="成交额" width="120" />
        <el-table-column prop="time" label="时间" width="100" />
      </el-table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useWebSocketStore } from '@/stores/websocket'
import { ElMessage } from 'element-plus'

const wsStore = useWebSocketStore()

// 输入的股票代码
const symbolInput = ref('')

// 连接状态
const connected = computed(() => wsStore.connected)
const connecting = computed(() => wsStore.connecting)
const subscriptionList = computed(() => wsStore.subscriptionList)
const stats = computed(() => wsStore.stats)
const quotes = computed(() => wsStore.quotes)

// 状态文本和类型
const statusText = computed(() => {
  if (connecting.value) return '连接中...'
  if (connected.value) return '已连接'
  return '未连接'
})

const statusTagType = computed(() => {
  if (connecting.value) return 'warning'
  if (connected.value) return 'success'
  return 'info'
})

// 行情列表
const quoteList = computed(() => {
  return subscriptionList.value.map(symbol => {
    const quote = quotes.value[symbol] || {}
    return {
      symbol,
      name: quote.name || '-',
      last_price: quote.last_price || '-',
      change_pct: quote.change_pct || 0,
      volume: quote.volume || 0,
      amount: quote.amount || 0,
      time: quote.time || '-'
    }
  })
})

/**
 * 连接WebSocket
 */
async function handleConnect() {
  try {
    await wsStore.connect()
    ElMessage.success('WebSocket连接成功')
  } catch (error) {
    console.error('连接失败:', error)
    ElMessage.error('WebSocket连接失败')
  }
}

/**
 * 断开连接
 */
function handleDisconnect() {
  wsStore.disconnect()
  ElMessage.info('WebSocket已断开')
}

/**
 * 订阅股票
 */
function handleSubscribe() {
  const symbols = symbolInput.value
    .split(',')
    .map(s => s.trim())
    .filter(s => s.length > 0)

  if (symbols.length === 0) {
    ElMessage.warning('请输入股票代码')
    return
  }

  wsStore.subscribe(symbols)
  symbolInput.value = ''
  ElMessage.success(`已订阅 ${symbols.length} 只股票`)
}

/**
 * 取消订阅
 */
function handleUnsubscribe(symbol: string) {
  wsStore.unsubscribe([symbol])
  ElMessage.info(`已取消订阅 ${symbol}`)
}

/**
 * 获取价格样式类
 */
function getPriceClass(row: any) {
  const change = row.change_pct || 0
  if (change > 0) return 'text-up'
  if (change < 0) return 'text-down'
  return ''
}

/**
 * 获取涨跌幅样式类
 */
function getChangeClass(row: any) {
  const change = row.change_pct || 0
  if (change > 0) return 'text-up'
  if (change < 0) return 'text-down'
  return ''
}

// 组件挂载时自动连接
onMounted(() => {
  // 自动连接
  handleConnect()
})

// 组件卸载时断开连接
onUnmounted(() => {
  if (connected.value) {
    wsStore.disconnect()
  }
})
</script>

<style scoped>
.websocket-quote-monitor {
  padding: 20px;
}

.connection-status {
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.stats {
  margin-bottom: 20px;
}

.subscription-manager {
  margin-bottom: 20px;
}

.subscription-list {
  margin-top: 10px;
  display: flex;
  flex-wrap: wrap;
}

.quotes-table {
  margin-top: 20px;
}

.text-up {
  color: #f56c6c;
  font-weight: bold;
}

.text-down {
  color: #67c23a;
  font-weight: bold;
}
</style>

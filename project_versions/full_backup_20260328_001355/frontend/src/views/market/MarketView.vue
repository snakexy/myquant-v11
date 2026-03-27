<template>
  <div class="market-view">
    <!-- 市场概览 -->
    <div class="market-overview">
      <div class="overview-card">
        <div class="card-title">上证指数</div>
        <div class="card-value" :class="getIndexClass(indexData.sh?.change_percent)">
          {{ indexData.sh?.price || '--' }}
        </div>
        <div class="card-change" :class="getIndexClass(indexData.sh?.change_percent)">
          {{ indexData.sh?.change_percent?.toFixed(2) || '--' }}%
        </div>
      </div>
      <div class="overview-card">
        <div class="card-title">深证成指</div>
        <div class="card-value" :class="getIndexClass(indexData.sz?.change_percent)">
          {{ indexData.sz?.price || '--' }}
        </div>
        <div class="card-change" :class="getIndexClass(indexData.sz?.change_percent)">
          {{ indexData.sz?.change_percent?.toFixed(2) || '--' }}%
        </div>
      </div>
      <div class="overview-card">
        <div class="card-title">沪深300</div>
        <div class="card-value" :class="getIndexClass(indexData.hs300?.change_percent)">
          {{ indexData.hs300?.price || '--' }}
        </div>
        <div class="card-change" :class="getIndexClass(indexData.hs300?.change_percent)">
          {{ indexData.hs300?.change_percent?.toFixed(2) || '--' }}%
        </div>
      </div>
      <div class="overview-card stats">
        <div class="stats-row">
          <span class="stats-label">上涨:</span>
          <span class="stats-value text-up">{{ marketStats.rise }}</span>
        </div>
        <div class="stats-row">
          <span class="stats-label">下跌:</span>
          <span class="stats-value text-down">{{ marketStats.fall }}</span>
        </div>
        <div class="stats-row">
          <span class="stats-label">平盘:</span>
          <span class="stats-value text-flat">{{ marketStats.flat }}</span>
        </div>
      </div>
    </div>

    <!-- 股票列表 -->
    <div class="stock-list-section">
      <div class="section-header">
        <h3 class="section-title">股票行情</h3>
        <div class="section-actions">
          <el-button size="small" @click="refreshData">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>
      </div>
      <el-table
        :data="stockList"
        stripe
        height="calc(100vh - 300px)"
        @row-click="handleRowClick"
        style="width: 100%"
      >
        <el-table-column prop="symbol" label="代码" width="100" />
        <el-table-column prop="name" label="名称" width="120" />
        <el-table-column label="现价" width="100">
          <template #default="{ row }">
            <span :class="getChangeClass(row.change_percent)">
              {{ row.price?.toFixed(2) || '--' }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="涨跌幅" width="100">
          <template #default="{ row }">
            <span :class="getChangeClass(row.change_percent)">
              {{ row.change_percent?.toFixed(2) || '--' }}%
            </span>
          </template>
        </el-table-column>
        <el-table-column label="涨跌额" width="100">
          <template #default="{ row }">
            <span :class="getChangeClass(row.change_percent)">
              {{ row.change?.toFixed(2) || '--' }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="volume" label="成交量(手)" width="120">
          <template #default="{ row }">
            {{ formatNumber(row.volume) }}
          </template>
        </el-table-column>
        <el-table-column prop="amount" label="成交额" width="120">
          <template #default="{ row }">
            {{ formatAmount(row.amount) }}
          </template>
        </el-table-column>
        <el-table-column prop="high" label="最高" width="100">
          <template #default="{ row }">
            {{ row.high?.toFixed(2) || '--' }}
          </template>
        </el-table-column>
        <el-table-column prop="low" label="最低" width="100">
          <template #default="{ row }">
            {{ row.low?.toFixed(2) || '--' }}
          </template>
        </el-table-column>
        <el-table-column prop="open" label="今开" width="100">
          <template #default="{ row }">
            {{ row.open?.toFixed(2) || '--' }}
          </template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, onActivated, onDeactivated } from 'vue'
import { useRouter } from 'vue-router'
import { Refresh } from '@element-plus/icons-vue'
import { getMarketOverview, getQuotes } from '@/api/market'

// 定义组件名称用于KeepAlive缓存
defineOptions({
  name: 'MarketView'
})

const router = useRouter()

// 数据
const indexData = ref<any>({
  sh: null,
  sz: null,
  hs300: null
})

const marketStats = ref({
  rise: 0,
  fall: 0,
  flat: 0
})

const stockList = ref<any[]>([])
let refreshTimer: number | null = null

// 获取市场概览
const fetchMarketOverview = async () => {
  try {
    const data = await getMarketOverview()

    if (data.indexes) {
      data.indexes.forEach((item: any) => {
        if (item.symbol === '000001') indexData.value.sh = item
        else if (item.symbol === '399001') indexData.value.sz = item
        else if (item.symbol === '000300') indexData.value.hs300 = item
      })
    }

    if (data.statistics) {
      marketStats.value = data.statistics
    }
  } catch (error) {
    console.error('Failed to fetch market overview:', error)
  }
}

// 获取股票列表
const fetchStockList = async () => {
  try {
    // 热门股票列表（包含各大板块龙头股）
    const symbols = [
      // 银行
      '600000', '600036', '601166', '601288', '601398', '601939', '601328', '002142',
      // 白酒食品
      '600519', '000858', '000568', '002304', '600887', '000596',
      // 科技
      '000063', '002415', '300750', '688981', '600745', '002236', '000725',
      // 医药
      '000661', '600276', '000538', '002007', '300015',
      // 新能源
      '300750', '002594', '601012', '002460', '002129',
      // 地产
      '000002', '001979', '600048',
      // 其他
      '000001', '600030', '601318', '600019', '601888'
    ]
    const data = await getQuotes(symbols.join(','))
    stockList.value = data
  } catch (error) {
    console.error('Failed to fetch stock list:', error)
  }
}

// 刷新数据
const refreshData = () => {
  fetchMarketOverview()
  fetchStockList()
}

// 行点击
const handleRowClick = (row: any) => {
  router.push({
    name: 'stock',
    query: { symbol: row.symbol }
  })
}

// 格式化数字
const formatNumber = (num: number) => {
  if (!num) return '--'
  return num.toLocaleString()
}

// 格式化金额
const formatAmount = (amount: number) => {
  if (!amount) return '--'
  if (amount >= 100000000) {
    return (amount / 100000000).toFixed(2) + '亿'
  } else if (amount >= 10000) {
    return (amount / 10000).toFixed(2) + '万'
  }
  return amount.toFixed(2)
}

// 获取涨跌颜色类
const getChangeClass = (change: number) => {
  if (change > 0) return 'text-up'
  if (change < 0) return 'text-down'
  return 'text-flat'
}

const getIndexClass = (change: number) => {
  return getChangeClass(change || 0)
}

// 生命周期
onMounted(() => {
  refreshData()
  startTimer()
})

onUnmounted(() => {
  stopTimer()
})

// 页面激活时刷新并启动定时器
onActivated(() => {
  refreshData()
  startTimer()
})

// 页面停用时停止定时器以节省资源
onDeactivated(() => {
  stopTimer()
})

// 启动定时器
const startTimer = () => {
  if (!refreshTimer) {
    refreshTimer = window.setInterval(() => {
      refreshData()
    }, 10000)
  }
}

// 停止定时器
const stopTimer = () => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
    refreshTimer = null
  }
}
</script>

<style scoped lang="scss">
@import '@/styles/variables.scss';

.market-view {
  .market-overview {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: $spacing-lg;
    margin-bottom: $spacing-xl;

    .overview-card {
      padding: $spacing-lg;
      background: $bg-surface;
      border: 1px solid $border-light;
      border-radius: $radius-lg;
      text-align: center;

      .card-title {
        font-size: $font-sm;
        color: $text-muted;
        margin-bottom: $spacing-sm;
      }

      .card-value {
        font-size: $font-2xl;
        font-weight: 700;
        margin-bottom: $spacing-xs;
      }

      .card-change {
        font-size: $font-sm;
      }

      &.stats {
        display: flex;
        flex-direction: column;
        justify-content: center;
        gap: $spacing-sm;

        .stats-row {
          display: flex;
          justify-content: space-between;
          align-items: center;

          .stats-label {
            font-size: $font-sm;
            color: $text-muted;
          }

          .stats-value {
            font-size: $font-md;
            font-weight: 600;
          }
        }
      }
    }
  }

  .stock-list-section {
    .section-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: $spacing-lg;

      .section-title {
        margin: 0;
        font-size: $font-lg;
        color: $text-primary;
      }
    }

    :deep(.el-table) {
      background: $bg-surface;
      border-color: $border-light;

      .el-table__header th {
        background: $bg-elevated;
        border-color: $border-light;
        color: $text-secondary;
      }

      .el-table__body tr {
        cursor: pointer;

        &:hover {
          background: $bg-hover;
        }
      }

      .el-table__body td {
        border-color: $border-light;
      }
    }
  }
}
</style>

<template>
  <div class="multi-stock-view">
    <!-- 控制栏 -->
    <div class="control-bar">
      <div class="layout-selector">
        <span class="label">布局:</span>
        <el-radio-group v-model="layoutMode" @change="handleLayoutChange">
          <el-radio-button :label="4">2×2</el-radio-button>
          <el-radio-button :label="9">3×3</el-radio-button>
          <el-radio-button :label="16">4×4</el-radio-button>
        </el-radio-group>
      </div>
      <div class="stock-selector">
        <el-button @click="showStockDialog = true">
          <el-icon><Plus /></el-icon>
          选择股票
        </el-button>
      </div>
    </div>

    <!-- 股票网格 -->
    <div class="stock-grid" :class="`grid-${layoutMode}`">
      <div
        v-for="stock in displayStocks"
        :key="stock.symbol"
        class="stock-card"
        @click="viewStockDetail(stock.symbol)"
      >
        <div class="card-header">
          <span class="stock-name">{{ stock.name || stock.symbol }}</span>
          <span class="stock-symbol">{{ stock.symbol }}</span>
        </div>
        <div class="card-body" :class="getChangeClass(stock.change_percent)">
          <div class="price">{{ formatNumber(stock.price) }}</div>
          <div class="change">
            <div class="change-value">{{ formatChange(stock.change, stock.change_percent) }}</div>
            <div class="change-percent">{{ formatPercent(stock.change_percent) }}</div>
          </div>
        </div>
        <div class="card-footer">
          <span class="label">成交量:</span>
          <span class="value">{{ formatVolume(stock.volume) }}</span>
        </div>
      </div>
    </div>

    <!-- 股票选择对话框 -->
    <el-dialog
      v-model="showStockDialog"
      title="选择股票"
      width="600px"
    >
      <el-input
        v-model="searchKeyword"
        placeholder="输入股票代码或名称搜索"
        clearable
        @input="searchStocks"
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
      </el-input>

      <div class="stock-list" v-loading="searching">
        <div
          v-for="stock in searchResults"
          :key="stock.symbol"
          class="stock-list-item"
          @click="addStock(stock)"
        >
          <span class="symbol">{{ stock.symbol }}</span>
          <span class="name">{{ stock.name }}</span>
          <el-button size="small" :disabled="isSelected(stock.symbol)">
            {{ isSelected(stock.symbol) ? '已添加' : '添加' }}
          </el-button>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { Plus, Search } from '@element-plus/icons-vue'
import { getQuotes } from '@/api/market'

const router = useRouter()

const layoutMode = ref(4)
const showStockDialog = ref(false)
const searchKeyword = ref('')
const searchResults = ref<any[]>([])
const searching = ref(false)

// 默认股票列表
const defaultStocks = [
  '600519', '600000', '600036', '601318',
  '000001', '000002', '000858', '002415',
  '601398', '600030', '000333', '000651',
  '600887', '002594', '000725', '002063'
]

const selectedStocks = ref<string[]>(defaultStocks.slice(0, 4))
const stockQuotes = ref<any[]>([])

// 显示的股票
const displayStocks = computed(() => {
  const stocks = selectedStocks.value.slice(0, layoutMode.value)
  return stocks.map(symbol => {
    const quote = stockQuotes.value.find(q => q.symbol === symbol)
    return quote || { symbol, name: symbol, price: 0, change: 0, change_percent: 0, volume: 0 }
  })
})

// 获取股票行情
const fetchQuotes = async () => {
  try {
    if (selectedStocks.value.length === 0) return

    const symbols = selectedStocks.value.slice(0, layoutMode.value).join(',')
    const data = await getQuotes(symbols)
    stockQuotes.value = data
  } catch (error) {
    console.error('Failed to fetch quotes:', error)
  }
}

// 搜索股票
const searchStocks = async () => {
  if (!searchKeyword.value) {
    searchResults.value = []
    return
  }

  try {
    searching.value = true

    // 使用默认股票列表模拟搜索
    const allStocks = [
      { symbol: '600519', name: '贵州茅台' },
      { symbol: '600000', name: '浦发银行' },
      { symbol: '600036', name: '招商银行' },
      { symbol: '601318', name: '中国平安' },
      { symbol: '601398', name: '工商银行' },
      { symbol: '600030', name: '中信证券' },
      { symbol: '000001', name: '平安银行' },
      { symbol: '000002', name: '万科A' },
      { symbol: '000858', name: '五粮液' },
      { symbol: '002415', name: '海康威视' },
      { symbol: '000333', name: '美的集团' },
      { symbol: '000651', name: '格力电器' },
    ]

    searchResults.value = allStocks.filter(stock =>
      stock.symbol.includes(searchKeyword.value) ||
      stock.name.includes(searchKeyword.value)
    )
  } finally {
    searching.value = false
  }
}

// 添加股票
const addStock = (stock: any) => {
  if (selectedStocks.value.length >= layoutMode.value) {
    selectedStocks.value.shift()
  }
  selectedStocks.value.push(stock.symbol)
  fetchQuotes()
  showStockDialog.value = false
}

// 是否已选择
const isSelected = (symbol: string) => {
  return selectedStocks.value.includes(symbol)
}

// 查看股票详情
const viewStockDetail = (symbol: string) => {
  router.push({
    name: 'stock',
    query: { symbol }
  })
}

// 切换布局
const handleLayoutChange = () => {
  // 调整股票数量
  if (selectedStocks.value.length < layoutMode.value) {
    const addCount = layoutMode.value - selectedStocks.value.length
    const toAdd = defaultStocks.slice(0, addCount)
    selectedStocks.value.push(...toAdd)
  }

  fetchQuotes()
}

// 格式化函数
const formatNumber = (num: number) => {
  if (!num) return '--'
  return num.toFixed(2)
}

const formatChange = (change: number, percent: number) => {
  if (!change || !percent) return '--'
  const mark = change > 0 ? '+' : ''
  return `${mark}${change.toFixed(2)}`
}

const formatPercent = (percent: number) => {
  if (!percent) return '--'
  return `${percent > 0 ? '+' : ''}${percent.toFixed(2)}%`
}

const formatVolume = (vol: number) => {
  if (!vol) return '--'
  return (vol / 10000).toFixed(2) + '万手'
}

const getChangeClass = (change: number) => {
  if (!change) return ''
  if (change > 0) return 'text-up'
  if (change < 0) return 'text-down'
  return 'text-flat'
}

// 定时刷新
let refreshTimer: number | null = null

onMounted(() => {
  fetchQuotes()

  // 每5秒刷新
  refreshTimer = window.setInterval(() => {
    fetchQuotes()
  }, 5000)
})

onUnmounted(() => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
  }
})
</script>

<style scoped lang="scss">
@import '@/styles/variables.scss';

.multi-stock-view {
  padding: $spacing-lg;

  .control-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: $spacing-xl;
    padding: $spacing-lg;
    background: $bg-surface;
    border: 1px solid $border-light;
    border-radius: $radius-lg;

    .layout-selector {
      display: flex;
      align-items: center;
      gap: $spacing-md;

      .label {
        font-size: $font-md;
        color: $text-secondary;
      }
    }
  }

  .stock-grid {
    display: grid;
    gap: $spacing-lg;

    &.grid-4 {
      grid-template-columns: repeat(2, 1fr);
      grid-template-rows: repeat(2, 1fr);
      height: calc(100vh - 200px);
    }

    &.grid-9 {
      grid-template-columns: repeat(3, 1fr);
      grid-template-rows: repeat(3, 1fr);
      height: calc(100vh - 200px);
    }

    &.grid-16 {
      grid-template-columns: repeat(4, 1fr);
      grid-template-rows: repeat(4, 1fr);
      height: calc(100vh - 200px);
    }

    .stock-card {
      background: $bg-surface;
      border: 1px solid $border-light;
      border-radius: $radius-lg;
      padding: $spacing-lg;
      cursor: pointer;
      transition: all $transition-base;

      &:hover {
        border-color: $border-medium;
        box-shadow: $shadow-lg;
        transform: translateY(-2px);
      }

      .card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: $spacing-md;

        .stock-name {
          font-size: $font-lg;
          font-weight: 600;
          color: $text-primary;
        }

        .stock-symbol {
          font-size: $font-sm;
          color: $text-muted;
        }
      }

      .card-body {
        text-align: center;
        padding: $spacing-lg 0;

        .price {
          font-size: $font-3xl;
          font-weight: 700;
          margin-bottom: $spacing-sm;
        }

        .change {
          .change-value {
            font-size: $font-lg;
            margin-bottom: $spacing-xs;
          }

          .change-percent {
            font-size: $font-md;
          }
        }
      }

      .card-footer {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding-top: $spacing-md;
        border-top: 1px solid $border-light;

        .label {
          font-size: $font-sm;
          color: $text-muted;
        }

        .value {
          font-size: $font-sm;
          color: $text-secondary;
        }
      }
    }
  }

  .stock-list {
    max-height: 400px;
    overflow-y: auto;
    margin-top: $spacing-lg;

    .stock-list-item {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: $spacing-md;
      border-bottom: 1px solid $border-light;
      cursor: pointer;

      &:hover {
        background: $bg-hover;
      }

      .symbol {
        font-weight: 600;
        color: $text-primary;
      }

      .name {
        flex: 1;
        margin-left: $spacing-md;
        color: $text-secondary;
      }
    }
  }
}
</style>

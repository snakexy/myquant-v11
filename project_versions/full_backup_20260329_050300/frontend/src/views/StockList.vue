<template>
  <div class="stock-list-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">
          <i class="fas fa-chart-line"></i>
          股票列表
        </h1>
        <p class="page-subtitle">实时行情数据 - TradingView风格</p>
      </div>
      <div class="header-right">
        <div class="update-info">
          <span class="update-indicator" :class="{ active: isRealtime }"></span>
          <span class="update-text">{{ updateTime }}</span>
        </div>
        <button class="refresh-btn" @click="refreshData" :disabled="loading">
          <i class="fas fa-sync-alt" :class="{ 'fa-spin': loading }"></i>
          刷新
        </button>
      </div>
    </div>

    <!-- 加载进度条 -->
    <div v-if="loading" class="loading-progress">
      <div class="progress-bar">
        <div class="progress-fill" :style="{ width: loadingProgress + '%' }"></div>
      </div>
      <div class="progress-info">
        <span class="progress-text">{{ loadingStatus }}</span>
        <span class="progress-percent">{{ loadingProgress }}%</span>
      </div>
    </div>

    <!-- TradingView风格股票列表 -->
    <TradingViewStockList
      :rankings="rankings"
      :loading="loading"
      :update-time="updateTime"
      @stock-click="showStockDetail"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import TradingViewStockList from '@/components/hotspot-analysis/TradingViewStockList.vue'

const router = useRouter()

interface Stock {
  code: string
  name: string
  current_price?: number
  changePercent: number | string
  volume: number
  amount: number | string
  market: string
}

// 状态管理
const loading = ref(false)
const loadingProgress = ref(0)
const loadingStatus = ref('')
const isRealtime = ref(false)
const updateTime = ref('等待更新')

// 排行榜数据
const rankings = ref({
  topRise: [] as Stock[],
  topFall: [] as Stock[],
  topAmount: [] as Stock[]
})

// 加载数据
const loadData = async () => {
  loading.value = true
  loadingStatus.value = '正在加载股票列表...'

  try {
    console.log('开始加载股票列表数据...')

    // 请求股票列表数据（只请求80只，符合分页策略）
    const stocksRes = await fetch(`/api/v1/market/stocks?page=1&page_size=80`)

    const stocksData = await stocksRes.json()

    // 处理股票数据
    if (stocksData.success && stocksData.stocks) {
      const stocks = stocksData.stocks

      // 按涨跌幅排序 - 涨幅榜（取前30名）
      const sortedByRise = [...stocks].sort((a, b) => b.change_pct - a.change_pct)
      rankings.value.topRise = sortedByRise.slice(0, 30).map((s: any) => ({
        code: s.symbol,
        name: s.name,
        current_price: s.current_price,
        change: s.change || 0,  // 添加涨跌额
        changePercent: Number(s.change_pct).toFixed(2),
        amount: s.amount,
        volume: s.volume || 0,
        market: s.market
      }))

      // 按跌幅排序 - 跌幅榜（取前30名）
      const sortedByFall = [...stocks].sort((a, b) => a.change_pct - b.change_pct)
      rankings.value.topFall = sortedByFall.slice(0, 30).map((s: any) => ({
        code: s.symbol,
        name: s.name,
        current_price: s.current_price,
        change: s.change || 0,  // 添加涨跌额
        changePercent: Number(s.change_pct).toFixed(2),
        amount: s.amount,
        volume: s.volume || 0,
        market: s.market
      }))

      // 按成交额排序 - 成交额榜（取前30名）
      const sortedByAmount = [...stocks].sort((a, b) => {
        const amountA = parseFloat(a.amount) || 0
        const amountB = parseFloat(b.amount) || 0
        return amountB - amountA
      })
      rankings.value.topAmount = sortedByAmount.slice(0, 30).map((s: any) => ({
        code: s.symbol,
        name: s.name,
        current_price: s.current_price,
        change: s.change || 0,  // 添加涨跌额
        changePercent: Number(s.change_pct).toFixed(2),
        amount: s.amount,
        volume: s.volume || 0,
        market: s.market
      }))

      console.log('✅ 股票列表加载完成:', {
        topRise: rankings.value.topRise.length,
        topFall: rankings.value.topFall.length,
        topAmount: rankings.value.topAmount.length,
        total: stocks.length
      })
    }

    updateTime.value = '刚刚更新'
  } catch (error) {
    loadingStatus.value = '加载失败，请重试'
    console.error('加载股票列表数据失败:', error)
  } finally {
    loading.value = false
  }
}

// 刷新数据
const refreshData = () => {
  loadData()
}

// 显示股票详情 - 跳转到K线图页面
const showStockDetail = (stock: Stock) => {
  router.push({
    name: 'KlineChart',
    query: {
      code: stock.code,
      name: stock.name
    }
  })
}

// 生命周期
onMounted(() => {
  console.log('onMounted: 初始加载股票列表数据')
  loadData()
})
</script>

<style scoped lang="scss">
.stock-list-page {
  width: 100%;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 8px;
  background: var(--bg-deep);
  overflow-y: auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #1E222D;
  border-radius: 4px;
  border: 1px solid #2A2E39;

  .header-left {
    .page-title {
      font-size: 16px;
      font-weight: 600;
      color: #B2B5BE;
      margin: 0 0 4px 0;
      display: flex;
      align-items: center;
      gap: 8px;

      i {
        color: #2962FF;
      }
    }

    .page-subtitle {
      font-size: 11px;
      color: #787B86;
      margin: 0;
    }
  }

  .header-right {
    display: flex;
    align-items: center;
    gap: 12px;

    .update-info {
      display: flex;
      align-items: center;
      gap: 6px;
      padding: 4px 12px;
      background: #2A2E39;
      border-radius: 12px;

      .update-indicator {
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background: #787B86;
        transition: all 0.3s;

        &.active {
          background: #26A69A;
          box-shadow: 0 0 6px #26A69A;
        }
      }

      .update-text {
        font-size: 11px;
        color: #787B86;
      }
    }

    .refresh-btn {
      padding: 6px 16px;
      background: #2962FF;
      color: white;
      border: none;
      border-radius: 4px;
      font-size: 11px;
      font-weight: 500;
      cursor: pointer;
      transition: all 0.3s;
      display: flex;
      align-items: center;
      gap: 6px;

      &:hover:not(:disabled) {
        opacity: 0.9;
      }

      &:disabled {
        opacity: 0.6;
        cursor: not-allowed;
      }

      i {
        font-size: 10px;
      }
    }
  }
}

/* 加载进度条 */
.loading-progress {
  background: #1E222D;
  border: 1px solid #2A2E39;
  border-radius: 8px;
  padding: 16px;
  margin: 8px 0;

  .progress-bar {
    height: 6px;
    background: #2A2E39;
    border-radius: 3px;
    overflow: hidden;
    margin-bottom: 12px;

    .progress-fill {
      height: 100%;
      background: linear-gradient(90deg, #2962FF 0%, #26A69A 100%);
      border-radius: 3px;
      transition: width 0.3s ease;
      box-shadow: 0 0 10px rgba(41, 98, 255, 0.5);
    }
  }

  .progress-info {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 12px;

    .progress-text {
      color: #B2B5BE;
    }

    .progress-percent {
      color: #26A69A;
      font-weight: 600;
    }
  }
}

/* 响应式 */
@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    gap: 8px;
    align-items: stretch;
  }
}
</style>

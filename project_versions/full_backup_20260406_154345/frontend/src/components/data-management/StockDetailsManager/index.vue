<template>
  <div class="stock-details-manager">
    <!-- 头部 -->
    <div class="section-header">
      <h3>📊 股票详情</h3>
      <div class="header-actions">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索股票代码或名称"
          clearable
          size="small"
          style="width: 250px;"
          @input="handleSearch"
        >
          <template #prefix>
            <font-awesome-icon icon="search" />
          </template>
        </el-input>
      </div>
    </div>

    <!-- 股票列表 -->
    <StockList
      :data="stockList"
      v-model="selectedStock"
      @select="selectStock"
    />

    <!-- 股票详情 -->
    <div v-if="selectedStock" class="stock-detail-panel">
      <!-- 基本信息 -->
      <div class="stock-header">
        <div class="stock-title">
          <h2>{{ selectedStockInfo?.name }} ({{ selectedStock }})</h2>
          <el-tag :type="getMarketTagType(selectedStockInfo?.market || '')" size="large">
            {{ selectedStockInfo?.market }}
          </el-tag>
        </div>
        <div class="stock-price-info" v-if="stockPrice">
          <div class="price-item">
            <span class="price-label">最新价:</span>
            <span class="price-value" :class="stockPrice.changePercent >= 0 ? 'up' : 'down'">
              {{ stockPrice.price }}
            </span>
          </div>
          <div class="price-item">
            <span class="price-label">涨跌幅:</span>
            <span class="price-value" :class="stockPrice.changePercent >= 0 ? 'up' : 'down'">
              {{ stockPrice.changePercent >= 0 ? '+' : '' }}{{ stockPrice.changePercent }}%
            </span>
          </div>
        </div>
      </div>

      <!-- 标签页 -->
      <el-tabs v-model="activeTab" class="detail-tabs">
        <!-- K线图 -->
        <el-tab-pane label="K线图" name="kline">
          <TradingViewKLineUnified
            :symbol="formattedStockCode"
            :stock-name="selectedStockInfo?.name"
            :stock-code="selectedStock || ''"
            height="500px"
            @periodChange="handlePeriodChange"
          />
        </el-tab-pane>

        <!-- 数据详情 -->
        <el-tab-pane label="数据详情" name="data">
          <DataTable :data="stockDataRecords" />
        </el-tab-pane>

        <!-- 统计信息 -->
        <el-tab-pane label="统计信息" name="stats">
          <StatsInfo :stats="stockStats" />
        </el-tab-pane>
      </el-tabs>
    </div>

    <!-- 空状态 -->
    <div v-else class="empty-state">
      <font-awesome-icon icon="chart-line" size="5x" style="color: rgba(255, 255, 255, 0.1);" />
      <p>请从上方选择股票查看详情</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import StockList from './StockList.vue'
import TradingViewKLineUnified from '@/components/charts/TradingViewKLineUnified.vue'
import DataTable from './DataTable.vue'
import StatsInfo from './StatsInfo.vue'
import type { StockInfo, StockPrice, StockStats, KlineData, StockDataRecord } from '@/components/data-management/shared/types'

interface Props {
  selectedStocks?: string[]
}

const props = defineProps<Props>()

// 状态
const searchKeyword = ref('')
const selectedStock = ref<string | null>(null)
const selectedStockInfo = ref<StockInfo | null>(null)
const stockPrice = ref<StockPrice | null>(null)
const activeTab = ref('kline')
const klineData = ref<KlineData[]>([])
const stockDataRecords = ref<StockDataRecord[]>([])
const stockStats = ref<StockStats>({
  recordCount: 0,
  dateRange: '-',
  completeness: 0,
  lastUpdate: '-'
})

// 计算格式化的股票代码（添加市场后缀）
const formattedStockCode = computed(() => {
  if (!selectedStock.value) return ''

  const code = selectedStock.value
  const market = selectedStockInfo.value?.market

  // 如果已经有后缀，直接返回
  if (code.includes('.') || code.includes('.SH') || code.includes('.SZ')) {
    return code
  }

  // 根据市场添加后缀
  if (market === '上海') {
    return `${code}.SH`
  } else if (market === '深圳') {
    return `${code}.SZ`
  } else if (market === '北交所') {
    return `${code}.BJ`
  }

  // 默认尝试上海
  return `${code}.SH`
})

// 模拟股票列表
const stockList = ref<StockInfo[]>([
  { code: '600000', name: '浦发银行', market: '上海' },
  { code: '600036', name: '招商银行', market: '上海' },
  { code: '000001', name: '平安银行', market: '深圳' },
  { code: '000002', name: '万科A', market: '深圳' }
])

// 选择股票
const selectStock = async (stock: StockInfo) => {
  selectedStockInfo.value = stock
  await loadStockDetail(stock.code)
}

// 加载股票详情
const loadStockDetail = async (code: string) => {
  try {
    // 加载股票价格信息
    // TODO: 从 API 加载
    stockPrice.value = {
      price: 12.34,
      changePercent: 2.5
    }

    // 加载统计信息
    loadStockStats(code)
  } catch (error) {
    ElMessage.error('加载股票详情失败')
  }
}

// 加载统计信息
const loadStockStats = (code: string) => {
  // TODO: 从 API 加载统计信息
  stockStats.value = {
    recordCount: 1250,
    dateRange: '2024-01-01 ~ 2026-01-06',
    completeness: 98,
    lastUpdate: '2026-01-06 15:00:00'
  }
}

// 处理搜索
const handleSearch = () => {
  // TODO: 实现搜索功能
}

// 处理周期变化
const handlePeriodChange = (period: string) => {
  // TODO: 重新加载数据
}

// 处理日期范围变化
const handleDateRangeChange = (range: [Date, Date] | null) => {
  // TODO: 重新加载数据
}

// 获取市场标签类型
const getMarketTagType = (market: string) => {
  const typeMap: Record<string, string> = {
    '上海': 'success',
    '深圳': 'warning',
    '北交所': 'info'
  }
  return typeMap[market] || 'info'
}

// 初始化
onMounted(() => {
  if (props.selectedStocks && props.selectedStocks.length > 0) {
    const stock = stockList.value.find(s => s.code === props.selectedStocks![0])
    if (stock) {
      selectStock(stock)
    }
  }
})
</script>

<style scoped>
.stock-details-manager {
  padding: 20px;
  background: rgba(26, 26, 46, 0.95);
  border-radius: 8px;
  min-height: 600px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #ffffff;
}

.stock-detail-panel {
  background: rgba(255, 255, 255, 0.02);
  border-radius: 6px;
  padding: 20px;
}

.stock-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.stock-title {
  display: flex;
  align-items: center;
  gap: 12px;
}

.stock-title h2 {
  margin: 0;
  font-size: 24px;
  font-weight: 700;
  color: #ffffff;
}

.stock-price-info {
  display: flex;
  gap: 24px;
}

.price-item {
  display: flex;
  gap: 8px;
  align-items: center;
}

.price-label {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.6);
}

.price-value {
  font-size: 20px;
  font-weight: 700;
}

.price-value.up {
  color: #ef4444;
}

.price-value.down {
  color: #10b981;
}

.detail-tabs {
  margin-top: 20px;
}

:deep(.el-tabs__item) {
  color: rgba(255, 255, 255, 0.6);
}

:deep(.el-tabs__item.is-active) {
  color: #2962ff;
}

:deep(.el-tabs__active-bar) {
  background-color: #2962ff;
}

:deep(.el-input__wrapper) {
  background: rgba(102, 126, 234, 0.08);
  border: 1px solid rgba(102, 126, 234, 0.3);
  box-shadow: none;
}

:deep(.el-input__wrapper:hover) {
  background: rgba(102, 126, 234, 0.12);
  border-color: rgba(102, 126, 234, 0.6);
}

:deep(.el-input__wrapper.is-focus) {
  background: rgba(102, 126, 234, 0.15);
  border-color: #2962ff;
  box-shadow: 0 0 0 1px rgba(102, 126, 234, 0.3);
}

:deep(.el-input__inner) {
  color: rgba(255, 255, 255, 0.9);
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  color: rgba(255, 255, 255, 0.3);
}

.empty-state p {
  margin-top: 16px;
  font-size: 16px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .section-header {
    flex-direction: column;
    gap: 12px;
    align-items: flex-start;
  }

  .stock-header {
    flex-direction: column;
    gap: 16px;
    align-items: flex-start;
  }

  .stock-price-info {
    flex-direction: column;
    gap: 12px;
    width: 100%;
  }

  .stock-title {
    flex-wrap: wrap;
  }

  .stock-title h2 {
    font-size: 18px;
  }
}
</style>

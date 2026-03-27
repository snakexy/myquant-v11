<template>
  <div class="tv-stock-list-container">
    <!-- 工具栏 -->
    <div class="tv-toolbar">
      <div class="tv-title">
        <i class="fas fa-list"></i>
        股票列表
      </div>
      <div class="tv-controls">
        <el-select
          v-model="selectedCategory"
          size="small"
          placeholder="分类"
          class="tv-select"
          @change="handleCategoryChange"
        >
          <el-option label="全部" value="all"></el-option>
          <el-option label="涨幅榜" value="topRise"></el-option>
          <el-option label="跌幅榜" value="topFall"></el-option>
          <el-option label="成交额榜" value="topAmount"></el-option>
        </el-select>
        <el-button
          size="small"
          @click="handleExport"
          class="tv-btn"
        >
          <i class="fas fa-download"></i>
          导出
        </el-button>
      </div>
    </div>

    <!-- TradingView风格表格 -->
    <div class="tv-table-wrapper">
      <el-table
        ref="tableRef"
        :data="displayData"
        :height="tableHeight"
        :row-style="{ height: '28px' }"
        :cell-style="{ padding: '4px 8px' }"
        :header-cell-style="{
          height: '32px',
          padding: '4px 8px',
          background: '#1E222D',
          color: '#787B86',
          'font-weight': 'normal',
          'font-size': '11px'
        }"
        class="tv-table"
        @sort-change="handleSort"
        @row-click="handleRowClick"
      >
        <el-table-column
          type="index"
          label="#"
          width="40"
          align="center"
          class-name="tv-index"
        />

        <el-table-column
          prop="code"
          label="代码"
          width="80"
          class-name="tv-code"
        >
          <template #default="{ row }">
            <span class="tv-code-text">{{ row.code }}</span>
          </template>
        </el-table-column>

        <el-table-column
          prop="name"
          label="名称"
          width="100"
          class-name="tv-name"
        >
          <template #default="{ row }">
            <span class="tv-name-text">{{ row.name }}</span>
          </template>
        </el-table-column>

        <el-table-column
          prop="current_price"
          label="现价"
          width="70"
          align="right"
          sortable
          class-name="tv-price"
        >
          <template #default="{ row }">
            <span :class="getPriceClass(row.changePercent)">
              {{ formatPrice(row.current_price) }}
            </span>
          </template>
        </el-table-column>

        <el-table-column
          prop="change"
          label="涨跌"
          width="70"
          align="right"
          sortable
          class-name="tv-change"
        >
          <template #default="{ row }">
            <span :class="getPriceClass(row.changePercent)">
              {{ formatChange(row.change) }}
            </span>
          </template>
        </el-table-column>

        <el-table-column
          prop="changePercent"
          label="涨跌幅"
          width="80"
          align="right"
          sortable
          class-name="tv-change-percent"
        >
          <template #default="{ row }">
            <span :class="getPriceClass(row.changePercent)">
              {{ formatPercent(row.changePercent) }}
            </span>
          </template>
        </el-table-column>

        <el-table-column
          prop="volume"
          label="成交量"
          width="100"
          align="right"
          sortable
          class-name="tv-volume"
        >
          <template #default="{ row }">
            <span class="tv-volume-text">{{ formatVolume(row.volume) }}</span>
          </template>
        </el-table-column>

        <el-table-column
          prop="amount"
          label="成交额"
          width="100"
          align="right"
          sortable
          class-name="tv-amount"
        >
          <template #default="{ row }">
            <span class="tv-amount-text">{{ formatAmount(row.amount) }}</span>
          </template>
        </el-table-column>

        <el-table-column
          prop="turnover_rate"
          label="换手率"
          width="80"
          align="right"
          sortable
          class-name="tv-turnover"
        >
          <template #default="{ row }">
            <span :class="getTurnoverClass(row.turnover_rate)">
              {{ formatTurnover(row.turnover_rate) }}
            </span>
          </template>
        </el-table-column>

        <el-table-column
          prop="pe_ratio"
          label="市盈率"
          width="80"
          align="right"
          sortable
          class-name="tv-pe"
        >
          <template #default="{ row }">
            <span class="tv-pe-text">{{ formatPE(row.pe_ratio) }}</span>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 底部状态栏 -->
    <div class="tv-footer">
      <div class="tv-stats">
        <span class="tv-stat-item">
          共 <strong>{{ displayData.length }}</strong> 只股票
        </span>
        <span class="tv-stat-item" v-if="selectedCategory !== 'all'">
          上涨 <strong class="tv-up">{{ riseCount }}</strong>
          平盘 <strong class="tv-flat">{{ flatCount }}</strong>
          下跌 <strong class="tv-down">{{ fallCount }}</strong>
        </span>
      </div>
      <div class="tv-update-time">
        <i class="fas fa-clock"></i>
        {{ updateTime }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'

interface Stock {
  code: string
  name: string
  current_price?: number
  changePercent: number | string
  volume?: number
  amount?: number | string
  turnover_rate?: number
  pe_ratio?: number
  market?: string
}

interface Props {
  rankings?: {
    topRise: Stock[]
    topFall: Stock[]
    topAmount: Stock[]
  }
  loading?: boolean
  updateTime?: string
}

const props = withDefaults(defineProps<Props>(), {
  rankings: () => ({ topRise: [], topFall: [], topAmount: [] }),
  loading: false,
  updateTime: '刚刚'
})

const emit = defineEmits<{
  'stock-click': [stock: Stock]
}>()

const selectedCategory = ref<string>('all')
const tableRef = ref()
const tableHeight = ref('calc(100vh - 180px)')

// 当前显示的数据
const displayData = computed(() => {
  if (selectedCategory.value === 'all') {
    // 合并所有榜单,去重
    const allStocks = [
      ...props.rankings.topRise,
      ...props.rankings.topFall,
      ...props.rankings.topAmount
    ]
    const uniqueStocks = new Map()
    allStocks.forEach(stock => {
      uniqueStocks.set(stock.code, stock)
    })
    return Array.from(uniqueStocks.values())
  } else {
    return props.rankings[selectedCategory.value] || []
  }
})

// 统计数据 - 性能优化：只过滤一次（M2-16）
// 避免在多个computed中重复过滤displayData
const stockStats = computed(() => {
  let rise = 0
  let flat = 0
  let fall = 0

  displayData.value.forEach(s => {
    const pct = parseFloat(String(s.changePercent).replace('%', ''))
    if (pct > 0) rise++
    else if (pct === 0) flat++
    else fall++
  })

  return { rise, flat, fall }
})

const riseCount = computed(() => stockStats.value.rise)
const flatCount = computed(() => stockStats.value.flat)
const fallCount = computed(() => stockStats.value.fall)

// 获取价格颜色类名
const getPriceClass = (changePercent: number | string) => {
  const pct = parseFloat(String(changePercent).replace('%', ''))
  if (pct > 0) return 'tv-up'
  if (pct < 0) return 'tv-down'
  return 'tv-flat'
}

// 获取换手率颜色类名
const getTurnoverClass = (turnover: number | undefined) => {
  if (!turnover) return 'tv-text-secondary'
  if (turnover > 5) return 'tv-up'
  if (turnover > 2) return 'tv-text-warning'
  return 'tv-text-secondary'
}

// 格式化价格
const formatPrice = (price: number | undefined) => {
  if (!price) return '--'
  return price.toFixed(2)
}

// 格式化涨跌（价格变动）
const formatChange = (change: number | string) => {
  const val = parseFloat(String(change))
  if (isNaN(val)) return '--'
  const sign = val > 0 ? '+' : ''
  return `${sign}${val.toFixed(2)}`
}

// 格式化涨跌幅
const formatPercent = (changePercent: number | string) => {
  const pct = parseFloat(String(changePercent).replace('%', ''))
  if (isNaN(pct)) return '--'
  const sign = pct > 0 ? '+' : ''
  return `${sign}${pct.toFixed(2)}%`
}

// 格式化成交量
const formatVolume = (volume: number | undefined) => {
  if (!volume || volume === 0) return '--'
  if (volume >= 100000000) {
    return `${(volume / 100000000).toFixed(2)}亿`
  } else if (volume >= 10000) {
    return `${(volume / 10000).toFixed(2)}万`
  }
  return volume.toString()
}

// 格式化成交额
const formatAmount = (amount: number | string | undefined) => {
  if (!amount) return '--'
  if (typeof amount === 'string') {
    return amount
  }
  if (amount >= 100000000) {
    return `${(amount / 100000000).toFixed(2)}亿`
  } else if (amount >= 10000) {
    return `${(amount / 10000).toFixed(2)}万`
  }
  return amount.toString()
}

// 格式化换手率
const formatTurnover = (turnover: number | undefined) => {
  if (!turnover) return '--'
  return `${turnover.toFixed(2)}%`
}

// 格式化市盈率
const formatPE = (pe: number | undefined) => {
  if (!pe) return '--'
  return pe.toFixed(2)
}

// 处理分类切换
const handleCategoryChange = (category: string) => {
  console.log('切换分类:', category)
}

// 处理排序
const handleSort = (sortData: any) => {
  console.log('排序:', sortData)
}

// 处理行点击
const handleRowClick = (row: Stock) => {
  emit('stock-click', row)
}

// 处理导出
const handleExport = () => {
  console.log('导出数据')
  // TODO: 实现导出功能
}

onMounted(() => {
  // 计算表格高度
  const updateTableHeight = () => {
    const headerHeight = 60
    const footerHeight = 32
    const padding = 16
    tableHeight.value = `calc(100vh - ${headerHeight + footerHeight + padding + 80}px)`
  }

  updateTableHeight()
  window.addEventListener('resize', updateTableHeight)
})
</script>

<style scoped lang="scss">
/* 紧凑暗色主题变量 */
:root {
  --tv-bg-primary: #131722;      /* 主背景 */
  --tv-bg-secondary: #1E222D;    /* 次级背景 */
  --tv-bg-tertiary: #2A2E39;     /* 卡片背景 */
  --tv-bg-hover: #363C45;        /* 悬停背景 */

  --tv-text-primary: #B2B5BE;     /* 主文字 */
  --tv-text-secondary: #787B86;   /* 次级文字 */
  --tv-text-tertiary: #575E6A;    /* 三级文字 */

  --tv-color-brand: #2962FF;     /* 品牌 - 蓝色 */

  --tv-border: #2A2E39;
  --tv-border-light: #363C45;

  --tv-font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  --tv-font-size-xs: 10px;
  --tv-font-size-sm: 11px;
  --tv-font-size-base: 12px;
}

.tv-stock-list-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: var(--tv-bg-primary);
  font-family: var(--tv-font-family);
  font-size: var(--tv-font-size-base);
  color: var(--tv-text-primary);
}

/* 工具栏 */
.tv-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: var(--tv-bg-secondary);
  border-bottom: 1px solid var(--tv-border);
  min-height: 36px;

  .tv-title {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: var(--tv-font-size-base);
    font-weight: 500;
    color: var(--tv-text-primary);

    i {
      font-size: 12px;
      color: var(--tv-color-brand);
    }
  }

  .tv-controls {
    display: flex;
    gap: 8px;
    align-items: center;

    .tv-select {
      width: 100px;

      :deep(.el-input__wrapper) {
        background: var(--tv-bg-tertiary);
        border-color: var(--tv-border);
        box-shadow: none;
        height: 24px;
        font-size: var(--tv-font-size-sm);

        &:hover {
          border-color: var(--tv-border-light);
        }
      }

      :deep(.el-input__inner) {
        color: var(--tv-text-primary);
        font-size: var(--tv-font-size-sm);
      }
    }

    .tv-btn {
      height: 24px;
      padding: 0 12px;
      background: var(--tv-bg-tertiary);
      border: 1px solid var(--tv-border);
      color: var(--tv-text-primary);
      font-size: var(--tv-font-size-sm);

      &:hover {
        background: var(--tv-bg-hover);
        border-color: var(--tv-border-light);
      }

      i {
        font-size: 10px;
        margin-right: 4px;
      }
    }
  }
}

/* 表格容器 */
.tv-table-wrapper {
  flex: 1;
  overflow: hidden;
  position: relative;
}

/* TradingView表格样式 */
:deep(.tv-table) {
  background: transparent;
  font-size: var(--tv-font-size-sm);
  font-family: var(--tv-font-family);

  /* 表头 */
  .el-table__header-wrapper {
    background: var(--tv-bg-secondary);

    th {
      background: var(--tv-bg-secondary) !important;
      color: var(--tv-text-secondary) !important;
      font-weight: normal !important;
      font-size: var(--tv-font-size-sm) !important;
      border-color: var(--tv-border) !important;
      padding: 4px 8px !important;
      height: 32px !important;

      .cell {
        padding: 0 !important;
        line-height: normal;
      }
    }
  }

  /* 表格行 */
  .el-table__row {
    height: 28px !important;
    background: transparent !important;
    transition: background 0.15s ease;

    &:hover {
      background: var(--tv-bg-hover) !important;
    }

    td {
      border-color: var(--tv-border) !important;
      padding: 4px 8px !important;

      .cell {
        padding: 0 !important;
        line-height: 20px;
        height: 20px;
        display: flex;
        align-items: center;
        justify-content: inherit;
      }
    }
  }

  /* 滚动条 */
  .el-table__body-wrapper {
    &::-webkit-scrollbar {
      width: 6px;
      height: 6px;
    }

    &::-webkit-scrollbar-track {
      background: var(--tv-bg-primary);
    }

    &::-webkit-scrollbar-thumb {
      background: var(--tv-bg-tertiary);
      border-radius: 3px;

      &:hover {
        background: var(--tv-border-light);
      }
    }
  }

  /* 排序图标 */
  .caret-wrapper {
    .sort-caret.ascending {
      border-bottom-color: var(--tv-text-secondary);
    }

    .sort-caret.descending {
      border-top-color: var(--tv-text-secondary);
    }
  }
}

/* 列样式 */
.tv-code-text {
  color: var(--tv-color-brand);
  font-family: 'Roboto Mono', 'Consolas', monospace;
  font-size: var(--tv-font-size-sm);
  font-weight: 500;
}

.tv-name-text {
  color: var(--tv-text-primary);
  font-size: var(--tv-font-size-sm);
}

.tv-volume-text,
.tv-amount-text,
.tv-pe-text {
  color: var(--tv-text-primary);
  font-size: var(--tv-font-size-sm);
}

/* 中国股市价格颜色（红涨绿跌） */
.tv-up {
  color: #ef4444 !important; /* 红色上涨 */
}

.tv-down {
  color: #10b981 !important; /* 绿色下跌 */
}

.tv-flat {
  color: #787B86 !important; /* 灰色平盘 */
}

.tv-text-secondary {
  color: var(--tv-text-secondary);
}

.tv-text-warning {
  color: #F5A623;
}

/* 底部状态栏 */
.tv-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 4px 12px;
  background: var(--tv-bg-secondary);
  border-top: 1px solid var(--tv-border);
  height: 28px;
  font-size: var(--tv-font-size-xs);
  color: var(--tv-text-secondary);

  .tv-stats {
    display: flex;
    gap: 16px;

    .tv-stat-item {
      display: flex;
      align-items: center;
      gap: 4px;

      strong {
        color: var(--tv-text-primary);
        font-weight: 500;
      }
    }
  }

  .tv-update-time {
    display: flex;
    align-items: center;
    gap: 4px;

    i {
      font-size: 10px;
    }
  }
}

/* 响应式 */
@media (max-width: 768px) {
  .tv-toolbar {
    flex-direction: column;
    gap: 8px;
    align-items: stretch;

    .tv-controls {
      justify-content: space-between;
    }
  }
}
</style>

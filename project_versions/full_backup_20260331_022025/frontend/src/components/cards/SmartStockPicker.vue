<template>
  <n-card class="smart-stock-picker" hoverable>
    <template #header>
      <div class="card-header">
        <div class="card-icon">
          <n-icon size="24" color="#7c3aed">
            <Search />
          </n-icon>
        </div>
        <div class="card-title">
          <h3>智能选股</h3>
          <p class="card-subtitle">基于AI技术指标筛选</p>
        </div>
        <div class="card-actions">
          <n-button @click="resetFilters" size="small" quaternary>
            <template #icon>
              <n-icon><Refresh /></n-icon>
            </template>
            重置
          </n-button>
        </div>
      </div>
    </template>
    
    <div class="card-content">
      <!-- 筛选条件 -->
      <div class="filter-section">
        <n-collapse v-model:expanded-names="expandedPanels" accordion>
          <n-collapse-item title="技术指标筛选" name="technical">
            <div class="filter-grid">
              <div class="filter-item">
                <n-label>均线类型</n-label>
                <n-select
                  v-model:value="filters.maType"
                  :options="maTypeOptions"
                  placeholder="选择均线类型"
                  clearable
                />
              </div>
              <div class="filter-item">
                <n-label>RSI区间</n-label>
                <n-slider
                  v-model:value="filters.rsiRange"
                  :min="0"
                  :max="100"
                  :step="1"
                  range
                  :marks="{ 30: '超卖', 70: '超买' }"
                />
              </div>
              <div class="filter-item">
                <n-label>MACD信号</n-label>
                <n-select
                  v-model:value="filters.macdSignal"
                  :options="macdOptions"
                  placeholder="选择MACD信号"
                  clearable
                />
              </div>
              <div class="filter-item">
                <n-label>布林带位置</n-label>
                <n-select
                  v-model:value="filters.bollingerPosition"
                  :options="bollingerOptions"
                  placeholder="选择布林带位置"
                  clearable
                />
              </div>
            </div>
          </n-collapse-item>
          
          <n-collapse-item title="基本面筛选" name="fundamental">
            <div class="filter-grid">
              <div class="filter-item">
                <n-label>市盈率范围</n-label>
                <n-slider
                  v-model:value="filters.peRange"
                  :min="0"
                  :max="100"
                  :step="1"
                  range
                  :marks="{ 0: '不限', 20: '20', 50: '50' }"
                />
              </div>
              <div class="filter-item">
                <n-label>市净率范围</n-label>
                <n-slider
                  v-model:value="filters.pbRange"
                  :min="0"
                  :max="20"
                  :step="0.1"
                  range
                  :marks="{ 0: '不限', 5: '5', 10: '10' }"
                />
              </div>
              <div class="filter-item">
                <n-label>ROE范围</n-label>
                <n-slider
                  v-model:value="filters.roeRange"
                  :min="0"
                  :max="50"
                  :step="1"
                  range
                  :marks="{ 0: '不限', 15: '15%', 30: '30%' }"
                />
              </div>
              <div class="filter-item">
                <n-label>市值范围</n-label>
                <n-select
                  v-model:value="filters.marketCapRange"
                  :options="marketCapOptions"
                  placeholder="选择市值范围"
                  clearable
                />
              </div>
            </div>
          </n-collapse-item>
          
          <n-collapse-item title="市场筛选" name="market">
            <div class="filter-grid">
              <div class="filter-item">
                <n-label>所属板块</n-label>
                <n-select
                  v-model:value="filters.sector"
                  :options="sectorOptions"
                  placeholder="选择板块"
                  multiple
                  clearable
                />
              </div>
              <div class="filter-item">
                <n-label>交易所</n-label>
                <n-select
                  v-model:value="filters.exchange"
                  :options="exchangeOptions"
                  placeholder="选择交易所"
                  clearable
                />
              </div>
              <div class="filter-item">
                <n-label>价格区间</n-label>
                <n-input-number
                  v-model:value="filters.priceRange[0]"
                  placeholder="最低价"
                  :min="0"
                  :precision="2"
                  style="margin-bottom: 8px;"
                />
                <n-input-number
                  v-model:value="filters.priceRange[1]"
                  placeholder="最高价"
                  :min="0"
                  :precision="2"
                />
              </div>
            </div>
          </n-collapse-item>
        </n-collapse>
      </div>
      
      <!-- 操作按钮 -->
      <div class="action-section">
        <n-space>
          <n-button
            type="primary"
            :loading="isSearching"
            @click="searchStocks"
          >
            <template #icon>
              <n-icon><Search /></n-icon>
            </template>
            开始筛选
          </n-button>
          <n-button
            @click="getHotStocks"
          >
            <template #icon>
              <n-icon><Flame /></n-icon>
            </template>
            热门股票
          </n-button>
          <n-button
            @click="saveStrategy"
          >
            <template #icon>
              <n-icon><Save /></n-icon>
            </template>
            保存策略
          </n-button>
        </n-space>
      </div>
      
      <!-- 筛选结果 -->
      <div v-if="searchResults.length > 0" class="results-section">
        <div class="results-header">
          <n-space justify="space-between">
            <n-text>找到 {{ searchResults.length }} 只股票</n-text>
            <n-button @click="exportResults" size="small" quaternary>
              <template #icon>
                <n-icon><Download /></n-icon>
              </template>
              导出结果
            </n-button>
          </n-space>
        </div>
        
        <div class="results-table">
          <n-data-table
            :columns="tableColumns"
            :data="searchResults"
            :pagination="pagination"
            :loading="isSearching"
            @update:page="handlePageChange"
            size="small"
            striped
          >
            <template #empty>
              <n-empty description="暂无数据" />
            </template>
          </n-data-table>
        </div>
      </div>
      
      <!-- AI建议 -->
      <div v-if="aiSuggestion" class="ai-suggestion">
        <n-alert type="info" :show-icon="false">
          <template #header>
            <div class="suggestion-header">
              <n-icon><Bulb /></n-icon>
              <span>AI建议</span>
            </div>
          </template>
          {{ aiSuggestion }}
        </n-alert>
      </div>
    </div>
  </n-card>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { NCard, NIcon, NButton, NCollapse, NCollapseItem, NLabel, NSelect, NSlider, NInputNumber, NSpace, NText, NDataTable, NEmpty, NAlert } from 'naive-ui'
import { Search, Refresh, Flame, Save, Download, Bulb } from '@vicons/ionicons5'

interface FilterOptions {
  maType: string
  rsiRange: [number, number]
  macdSignal: string
  bollingerPosition: string
  peRange: [number, number]
  pbRange: [number, number]
  roeRange: [number, number]
  marketCapRange: string
  sector: string[]
  exchange: string
  priceRange: [number, number]
}

interface StockResult {
  code: string
  name: string
  price: number
  changePercent: number
  volume: number
  marketCap: number
  pe: number
  pb: number
  roe: number
  sector: string
  score: number
}

interface Props {
  onSearch?: (filters: FilterOptions) => Promise<StockResult[]>
  onGetHotStocks?: () => Promise<StockResult[]>
  onSaveStrategy?: (filters: FilterOptions) => void
}

const props = defineProps<Props>()

const emit = defineEmits<{
  search: [results: StockResult[]]
  export: [results: StockResult[]]
}>()

// 筛选条件
const filters = ref<FilterOptions>({
  maType: '',
  rsiRange: [30, 70],
  macdSignal: '',
  bollingerPosition: '',
  peRange: [0, 50],
  pbRange: [0, 10],
  roeRange: [0, 30],
  marketCapRange: '',
  sector: [],
  exchange: '',
  priceRange: [0, 1000]
})

// 展开的面板
const expandedPanels = ref(['technical'])

// 搜索状态
const isSearching = ref(false)
const searchResults = ref<StockResult[]>([])
const currentPage = ref(1)
const pageSize = ref(10)

// AI建议
const aiSuggestion = ref('')

// 选项配置
const maTypeOptions = [
  { label: 'MA5', value: 'ma5' },
  { label: 'MA10', value: 'ma10' },
  { label: 'MA20', value: 'ma20' },
  { label: 'MA60', value: 'ma60' }
]

const macdOptions = [
  { label: '金叉', value: 'golden_cross' },
  { label: '死叉', value: 'death_cross' },
  { label: '多头', value: 'bullish' },
  { label: '空头', value: 'bearish' }
]

const bollingerOptions = [
  { label: '上轨突破', value: 'upper_break' },
  { label: '下轨支撑', value: 'lower_support' },
  { label: '中轨回归', value: 'middle_return' }
]

const marketCapOptions = [
  { label: '小市值', value: 'small' },
  { label: '中市值', value: 'medium' },
  { label: '大市值', value: 'large' },
  { label: '巨无霸', value: 'mega' }
]

const sectorOptions = [
  { label: '科技', value: 'technology' },
  { label: '金融', value: 'finance' },
  { label: '医疗', value: 'healthcare' },
  { label: '消费', value: 'consumer' },
  { label: '能源', value: 'energy' },
  { label: '工业', value: 'industrial' }
]

const exchangeOptions = [
  { label: '上海证券交易所', value: 'SH' },
  { label: '深圳证券交易所', value: 'SZ' },
  { label: '北京证券交易所', value: 'BJ' }
]

// 表格列配置
const tableColumns = computed(() => [
  {
    title: '代码',
    key: 'code',
    width: 80,
    fixed: 'left'
  },
  {
    title: '名称',
    key: 'name',
    width: 120
  },
  {
    title: '价格',
    key: 'price',
    width: 80,
    render: (row: StockResult) => `¥${row.price.toFixed(2)}`
  },
  {
    title: '涨跌幅',
    key: 'changePercent',
    width: 80,
    render: (row: StockResult) => {
      const value = row.changePercent
      const color = value > 0 ? 'var(--market-rise)' : value < 0 ? 'var(--market-fall)' : 'var(--market-neutral)'
      return `<span style="color: ${color}">${value > 0 ? '+' : ''}${value.toFixed(2)}%</span>`
    }
  },
  {
    title: '市值',
    key: 'marketCap',
    width: 100,
    render: (row: StockResult) => `${(row.marketCap / 100000000).toFixed(1)}亿`
  },
  {
    title: 'PE',
    key: 'pe',
    width: 60,
    render: (row: StockResult) => row.pe.toFixed(2)
  },
  {
    title: 'ROE',
    key: 'roe',
    width: 60,
    render: (row: StockResult) => `${row.roe.toFixed(1)}%`
  },
  {
    title: '评分',
    key: 'score',
    width: 80,
    render: (row: StockResult) => {
      const score = row.score
      let color = '#64748b'
      if (score >= 80) color = '#10b981'
      else if (score >= 60) color = '#f59e0b'
      else if (score >= 40) color = '#eab308'
      return `<span style="color: ${color}">${score.toFixed(1)}</span>`
    }
  }
])

// 分页配置
const pagination = computed(() => ({
  page: currentPage.value,
  pageSize: pageSize.value,
  itemCount: searchResults.value.length,
  showSizePicker: true,
  pageSizes: [10, 20, 50, 100]
}))

// 搜索股票
const searchStocks = async () => {
  isSearching.value = true
  try {
    let results: StockResult[] = []
    
    if (props.onSearch) {
      results = await props.onSearch(filters.value)
    } else {
      // 模拟搜索结果
      results = generateMockResults()
    }
    
    searchResults.value = results
    emit('search', results)
    
    // 生成AI建议
    generateAISuggestion(results)
  } catch (error) {
    console.error('搜索股票失败:', error)
  } finally {
    isSearching.value = false
  }
}

// 获取热门股票
const getHotStocks = async () => {
  isSearching.value = true
  try {
    let results: StockResult[] = []
    
    if (props.onGetHotStocks) {
      results = await props.onGetHotStocks()
    } else {
      // 模拟热门股票
      results = generateMockResults()
    }
    
    searchResults.value = results
    emit('search', results)
  } catch (error) {
    console.error('获取热门股票失败:', error)
  } finally {
    isSearching.value = false
  }
}

// 保存策略
const saveStrategy = () => {
  if (props.onSaveStrategy) {
    props.onSaveStrategy(filters.value)
  }
}

// 重置筛选
const resetFilters = () => {
  filters.value = {
    maType: '',
    rsiRange: [30, 70],
    macdSignal: '',
    bollingerPosition: '',
    peRange: [0, 50],
    pbRange: [0, 10],
    roeRange: [0, 30],
    marketCapRange: '',
    sector: [],
    exchange: '',
    priceRange: [0, 1000]
  }
  searchResults.value = []
  aiSuggestion.value = ''
}

// 导出结果
const exportResults = () => {
  emit('export', searchResults.value)
}

// 处理分页变化
const handlePageChange = (page: number) => {
  currentPage.value = page
}

// 生成模拟结果
const generateMockResults = (): StockResult[] => {
  const mockData: StockResult[] = []
  // 改为动态获取，避免硬编码股票列表
  const stocks = ref<Array<{ code: string; name: string; sector: string }>>([])
  ]
  
  for (let i = 0; i < 50; i++) {
    const stock = stocks[i % stocks.length]
    mockData.push({
      code: stock.code,
      name: stock.name,
      price: Math.random() * 100 + 10,
      changePercent: (Math.random() - 0.5) * 10,
      volume: Math.floor(Math.random() * 1000000),
      marketCap: Math.random() * 10000000000,
      pe: Math.random() * 50,
      pb: Math.random() * 10,
      roe: Math.random() * 30,
      sector: stock.sector,
      score: Math.random() * 100
    })
  }
  
  return mockData.sort((a, b) => b.score - a.score)
}

// 生成AI建议
const generateAISuggestion = (results: StockResult[]) => {
  if (results.length === 0) {
    aiSuggestion.value = '建议调整筛选条件以获得更多结果'
    return
  }
  
  const topStocks = results.slice(0, 5)
  const avgScore = results.reduce((sum, stock) => sum + stock.score, 0) / results.length
  
  if (avgScore > 70) {
    aiSuggestion.value = `筛选结果质量较高，建议关注前5名股票，特别是${topStocks[0].name}(${topStocks[0].code})，评分达到${topStocks[0].score.toFixed(1)}分`
  } else if (avgScore > 50) {
    aiSuggestion.value = '筛选结果中等，建议结合基本面分析进一步筛选'
  } else {
    aiSuggestion.value = '筛选结果质量一般，建议放宽筛选条件或关注热门板块'
  }
}

onMounted(() => {
  // 组件初始化
})
</script>

<style lang="scss" scoped>
.smart-stock-picker {
  height: 100%;
  
  .card-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    
    .card-icon {
      display: flex;
      align-items: center;
      justify-content: center;
      width: 48px;
      height: 48px;
      border-radius: 12px;
      background: rgba(124, 58, 237, 0.1);
      border: 1px solid rgba(124, 58, 237, 0.2);
    }
    
    .card-title {
      flex: 1;
      margin-left: 12px;
      
      h3 {
        margin: 0;
        font-size: 16px;
        font-weight: 600;
        color: #f8fafc;
        line-height: 1.2;
      }
      
      .card-subtitle {
        margin: 4px 0 0 0;
        font-size: 12px;
        color: #94a3b8;
        line-height: 1.2;
      }
    }
    
    .card-actions {
      margin-left: auto;
    }
  }
  
  .card-content {
    .filter-section {
      margin-bottom: 20px;
      
      .filter-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 16px;
        
        .filter-item {
          .n-label {
            margin-bottom: 8px;
            color: #94a3b8;
          }
        }
      }
    }
    
    .action-section {
      margin-bottom: 20px;
      padding: 16px;
      background: rgba(15, 23, 42, 0.4);
      border-radius: 8px;
      border: 1px solid rgba(148, 163, 184, 0.1);
    }
    
    .results-section {
      .results-header {
        margin-bottom: 16px;
        padding: 12px;
        background: rgba(37, 99, 235, 0.1);
        border-radius: 6px;
        border: 1px solid rgba(37, 99, 235, 0.2);
      }
      
      .results-table {
        border-radius: 8px;
        overflow: hidden;
      }
    }
    
    .ai-suggestion {
      margin-top: 20px;
      
      .suggestion-header {
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 8px;
        font-weight: 600;
        color: #3b82f6;
      }
    }
  }
}

  /* 统一滑杆样式覆盖 */
  .parameter-range {
    /* 使用全局滑杆样式 */
    -webkit-appearance: none;
    appearance: none;
    width: 100%;
    height: 6px;
    background: var(--border-color);
    border-radius: 3px;
    outline: none;
    transition: all 0.3s ease;
    border: none;
    padding: 0;
  }

  .parameter-range::-webkit-slider-thumb {
    -webkit-appearance: none;
    appearance: none;
    width: 20px;
    height: 20px;
    background: var(--bg-white);
    border: 3px solid var(--primary-color);
    border-radius: 50%;
    cursor: grab;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
    transition: all 0.3s ease;
  }

  .parameter-range::-webkit-slider-thumb:hover {
    transform: scale(1.2);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
  }

  .parameter-range::-webkit-slider-thumb:active {
    cursor: grabbing;
    transform: scale(1.1);
  }

  .parameter-range::-moz-range-thumb {
    width: 20px;
    height: 20px;
    background: var(--bg-white);
    border: 3px solid var(--primary-color);
    border-radius: 50%;
    cursor: grab;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
    transition: all 0.3s ease;
    border: none;
  }

  .parameter-range::-moz-range-thumb:hover {
    transform: scale(1.2);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
  }

  .parameter-range::-moz-range-thumb:active {
    cursor: grabbing;
    transform: scale(1.1);
  }

  .parameter-range::-webkit-slider-runnable-track {
    height: 100%;
    border-radius: 3px;
  }

  .parameter-range::-moz-range-track {
    height: 100%;
    border-radius: 3px;
  }

  .range-input-group {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 4px 0;
  }

  .range-value {
    min-width: 60px;
    padding: 4px 8px;
    background: var(--bg-secondary);
    border: 1px solid var(--border-color);
    border-radius: var(--border-radius-sm);
    font-size: var(--font-size-sm);
    font-weight: 600;
    color: var(--primary-color);
    text-align: center;
    transition: all 0.3s ease;
  }

  /* 参数配置滑杆样式增强 */
  .parameter-slider {
    display: flex;
    align-items: center;
    gap: 16px;
    padding: 12px;
    background: var(--bg-secondary);
    border-radius: var(--border-radius);
    transition: all 0.3s ease;
  }

  .parameter-slider:hover {
    background: var(--bg-hover);
  }

  .parameter-slider .parameter-info {
    flex: 1;
  }

  .parameter-slider .parameter-name {
    font-size: var(--font-size-sm);
    font-weight: 500;
    color: var(--text-primary);
    margin-bottom: 4px;
  }

  .parameter-slider .parameter-desc {
    font-size: var(--font-size-xs);
    color: var(--text-regular);
  }

  .parameter-slider .parameter-control {
    flex: 2;
    display: flex;
    align-items: center;
    gap: 12px;
  }

</style>
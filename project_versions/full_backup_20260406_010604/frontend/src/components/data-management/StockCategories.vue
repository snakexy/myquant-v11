<template>
  <section class="stock-categories-section">
    <div class="section-header">
      <h2>股票分类统计</h2>
      <p>按板块和市场分类统计股票数量和表现</p>
    </div>

    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>加载中...</p>
    </div>

    <div v-else-if="error" class="error-state">
      <i class="fas fa-exclamation-circle"></i>
      <p>{{ error }}</p>
      <button @click="loadData" class="retry-btn">重试</button>
    </div>

    <div v-else class="categories-grid">
      <StockCategoryCard
        v-for="category in categories"
        :key="category.id"
        :category="category"
      />
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import StockCategoryCard from './StockCategoryCard.vue'

interface Stock {
  code: string
  name: string
  changePercent: number
}

interface Category {
  id: string
  name: string
  description: string
  count: number
  avgReturn: number
  topStocks: Stock[]
  chartData?: number[]
}

const loading = ref(true)
const error = ref('')
const categories = ref<Category[]>([])

// 默认分类数据
const defaultCategories: Category[] = [
  {
    id: 'hs300',
    name: '沪深300',
    description: '沪深市场核心300只股票',
    count: 300,
    avgReturn: 0,
    topStocks: [],
    chartData: []
  },
  {
    id: 'zz500',
    name: '中证500',
    description: '中型企业代表500只股票',
    count: 500,
    avgReturn: 0,
    topStocks: [],
    chartData: []
  },
  {
    id: 'sz50',
    name: '上证50',
    description: '上海证券交易所50只龙头股票',
    count: 50,
    avgReturn: 0,
    topStocks: [],
    chartData: []
  },
  {
    id: 'cyb',
    name: '创业板指',
    description: '创业板市场100只股票',
    count: 100,
    avgReturn: 0,
    topStocks: [],
    chartData: []
  },
  {
    id: 'kc50',
    name: '科创50',
    description: '科创板50只核心股票',
    count: 50,
    avgReturn: 0,
    topStocks: [],
    chartData: []
  }
]

const loadData = async () => {
  loading.value = true
  error.value = ''

  try {
    const response = await fetch('/api/v1/data-management/categories/stats')
    const result = await response.json()

    if (result.success && result.data && result.data.categories) {
      // 直接使用API返回的数据
      categories.value = result.data.categories.map((apiCat: any) => ({
        id: apiCat.id,
        name: apiCat.name,
        description: apiCat.description || defaultCategories.find(c => c.id === apiCat.id)?.description || '',
        count: apiCat.count,
        avgReturn: apiCat.avgReturn || 0,
        topStocks: apiCat.topStocks || [],
        chartData: apiCat.chartData || []
      }))
    } else {
      // 使用默认数据
      categories.value = defaultCategories.map(cat => ({
        ...cat,
        topStocks: generateTopStocks(cat.name, cat.count),
        chartData: generateChartData(cat.avgReturn)
      }))
    }
  } catch (err) {
    console.error('获取股票分类统计失败:', err)
    error.value = '加载失败，请重试'
    // 使用默认数据
    categories.value = defaultCategories.map(cat => ({
      ...cat,
      topStocks: generateTopStocks(cat.name, cat.count),
      chartData: generateChartData(cat.avgReturn)
    }))
  } finally {
    loading.value = false
  }
}

// 生成热门股票（模拟数据，作为后备方案）
const generateTopStocks = (categoryName: string, count: number): Stock[] => {
  const stocks: Stock[] = []
  const stockNames = [
    { code: '600036.SH', name: '招商银行' },
    { code: '000858.SZ', name: '五粮液' },
    { code: '600519.SH', name: '贵州茅台' },
    { code: '000001.SZ', name: '平安银行' },
    { code: '600276.SH', name: '恒瑞医药' }
  ]

  for (let i = 0; i < Math.min(3, stockNames.length); i++) {
    const changePercent = parseFloat((Math.random() * 6 - 2).toFixed(2))
    stocks.push({
      ...stockNames[i],
      changePercent
    })
  }

  return stocks
}

// 生成图表数据（模拟数据，作为后备方案）
const generateChartData = (avgReturn: number): number[] => {
  const data: number[] = []
  let value = 100

  for (let i = 0; i < 20; i++) {
    value += (Math.random() - 0.5 + avgReturn / 100) * 2
    data.push(Math.max(95, Math.min(110, value)))
  }

  return data
}

onMounted(() => {
  loadData()
})
</script>

<style scoped lang="scss">
.stock-categories-section {
  margin-bottom: 32px;
}

.section-header {
  margin-bottom: 24px;

  h2 {
    font-size: 20px;
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 4px;
  }

  p {
    font-size: 14px;
    color: var(--text-secondary);
  }
}

.loading-state,
.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  background: var(--card-bg);
  border-radius: 12px;
  color: var(--text-secondary);
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid var(--border-color);
  border-top-color: var(--primary-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.error-state {
  color: var(--error-color);

  i {
    font-size: 48px;
    margin-bottom: 16px;
  }
}

.retry-btn {
  margin-top: 16px;
  padding: 8px 24px;
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;

  &:hover {
    opacity: 0.9;
    transform: translateY(-1px);
  }
}

.categories-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
  gap: 20px;
}

@media (max-width: 768px) {
  .categories-grid {
    grid-template-columns: 1fr;
  }
}
</style>

<template>
  <div class="news-panel">
    <div class="news-header">
      <span class="header-title">新闻</span>
      <div class="header-actions">
        <button class="icon-btn" title="刷新">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
            <path d="M17.65 6.35C16.2 4.9 14.21 4 12 4c-4.42 0-7.99 3.58-7.99 8s3.57 8 7.99 8c3.73 0 6.84-2.55 7.73-6h-2.08c-.82 2.33-3.04 4-5.65 4-3.31 0-6-2.69-6-6s2.69-6 6-6c1.66 0 3.14.69 4.22 1.78L13 11h7V4l-2.35 2.35z"/>
          </svg>
        </button>
      </div>
    </div>

    <div class="news-tabs">
      <button :class="['tab-btn', { active: activeTab === 'all' }]" @click="activeTab = 'all'">
        全部
      </button>
      <button :class="['tab-btn', { active: activeTab === 'stock' }]" @click="activeTab = 'stock'">
        个股
      </button>
    </div>

    <div class="news-list">
      <a
        v-for="news in displayedNews"
        :key="news.id"
        :href="news.url"
        target="_blank"
        class="news-item"
      >
        <div class="news-source">
          <span class="source-name">{{ news.source }}</span>
          <span class="news-time">{{ news.time }}</span>
        </div>
        <div class="news-title">{{ news.title }}</div>
        <div class="news-meta" v-if="news.sentiment">
          <span :class="['sentiment', news.sentiment]">
            {{ getSentimentText(news.sentiment) }}
          </span>
        </div>
      </a>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'

interface NewsItem {
  id: string
  title: string
  source: string
  time: string
  url: string
  sentiment?: 'bullish' | 'bearish' | 'neutral'
  published_at?: string
}

const props = defineProps<{
  stockSymbol?: string
}>()

const activeTab = ref<'all' | 'stock'>('all')
const loading = ref(false)
const error = ref<string | null>(null)

// 全部新闻
const allNews = ref<NewsItem[]>([
  {
    id: '1',
    title: '央行：继续实施稳健的货币政策',
    source: '央行网站',
    time: '2小时前',
    url: '#',
    sentiment: 'neutral'
  },
  {
    id: '2',
    title: 'A股三大指数集体收涨，北向资金净流入超50亿',
    source: '证券时报',
    time: '3小时前',
    url: '#',
    sentiment: 'bullish'
  },
  {
    id: '3',
    title: '科技股领涨市场，芯片板块涨幅居前',
    source: '东方财富',
    time: '4小时前',
    url: '#',
    sentiment: 'bullish'
  },
  {
    id: '4',
    title: '全球经济面临不确定性，市场观望情绪浓厚',
    source: '彭博社',
    time: '5小时前',
    url: '#',
    sentiment: 'bearish'
  },
  {
    id: '5',
    title: '新能源汽车销量创历史新高',
    source: '汽车之家',
    time: '6小时前',
    url: '#',
    sentiment: 'bullish'
  }
])

// 个股新闻
const stockNews = ref<NewsItem[]>([
  {
    id: 's1',
    title: '公司发布2025年业绩预告，净利润预增30%',
    source: '公司公告',
    time: '1小时前',
    url: '#',
    sentiment: 'bullish'
  },
  {
    id: 's2',
    title: '机构调研：多家基金公司密集调研',
    source: '券商中国',
    time: '3小时前',
    url: '#',
    sentiment: 'neutral'
  }
])

// 显示的新闻列表
const displayedNews = computed(() => {
  return activeTab.value === 'all' ? allNews.value : stockNews.value
})

/**
 * 获取市场新闻
 */
const fetchMarketNews = async () => {
  if (loading.value) return

  loading.value = true
  error.value = null

  try {
    const response = await fetch('/api/v1/market/news?limit=10')
    const result = await response.json()

    if (result.success && result.data) {
      allNews.value = result.data.map((item: any) => ({
        id: item.id || item.news_id || String(Date.now() + Math.random()),
        title: item.title || '新闻标题',
        source: item.source || item.provider || '未知来源',
        time: formatNewsTime(item.published_at || item.time),
        url: item.url || item.link || '#',
        sentiment: analyzeSentiment(item.title),
        published_at: item.published_at || item.time,
      }))
      console.log('[NewsPanel] ✅ 市场新闻加载成功')
    } else {
      console.error('[NewsPanel] ❌ 新闻数据格式错误:', result)
      error.value = '新闻数据格式错误'
    }
  } catch (err) {
    console.error('[NewsPanel] ❌ 获取市场新闻失败:', err)
    error.value = '获取新闻失败'
    // 保持模拟数据作为降级方案
  } finally {
    loading.value = false
  }
}

/**
 * 获取个股新闻
 */
const fetchStockNews = async (symbol: string) => {
  if (loading.value) return

  loading.value = true
  error.value = null

  try {
    const response = await fetch(`/api/v1/market/stock-news?symbol=${symbol}&limit=5`)
    const result = await response.json()

    if (result.success && result.data) {
      stockNews.value = result.data.map((item: any) => ({
        id: item.id || item.news_id || String(Date.now() + Math.random()),
        title: item.title || '新闻标题',
        source: item.source || item.provider || '未知来源',
        time: formatNewsTime(item.published_at || item.time),
        url: item.url || item.link || '#',
        sentiment: analyzeSentiment(item.title),
        published_at: item.published_at || item.time,
      }))
      console.log(`[NewsPanel] ✅ 个股新闻加载成功: ${symbol}`)
    } else {
      console.error('[NewsPanel] ❌ 个股新闻数据格式错误:', result)
      error.value = '个股新闻数据格式错误'
    }
  } catch (err) {
    console.error('[NewsPanel] ❌ 获取个股新闻失败:', err)
    error.value = '获取个股新闻失败'
    // 保持模拟数据作为降级方案
  } finally {
    loading.value = false
  }
}

/**
 * 格式化新闻时间
 */
const formatNewsTime = (timestamp: string | number): string => {
  if (!timestamp) return '刚刚'

  const now = Date.now()
  const time = typeof timestamp === 'string' ? new Date(timestamp).getTime() : timestamp
  const diff = now - time

  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)
  const days = Math.floor(diff / 86400000)

  if (minutes < 60) return `${minutes}分钟前`
  if (hours < 24) return `${hours}小时前`
  if (days < 7) return `${days}天前`

  return new Date(time).toLocaleDateString('zh-CN')
}

/**
 * 分析新闻情感（简单版）
 * 实际项目中可以使用 NLP 模型或第三方情感分析 API
 */
const analyzeSentiment = (title: string): 'bullish' | 'bearish' | 'neutral' => {
  const bullish = ['上涨', '增长', '利好', '突破', '新高', '盈利', '增长', '领涨', '收涨', '净流入']
  const bearish = ['下跌', '亏损', '利空', '跌破', '新低', '下滑', '回调', '领跌', '收跌', '净流出']

  const lower = title.toLowerCase()

  if (bullish.some(kw => lower.includes(kw))) return 'bullish'
  if (bearish.some(kw => lower.includes(kw))) return 'bearish'
  return 'neutral'
}

/**
 * 获取情感文本
 */
const getSentimentText = (sentiment: string) => {
  const map = {
    bullish: '利好',
    bearish: '利空',
    neutral: '中性'
  }
  return map[sentiment as keyof typeof map] || ''
}

/**
 * 刷新新闻
 */
const refresh = () => {
  if (activeTab.value === 'all') {
    fetchMarketNews()
  } else {
    if (props.stockSymbol) {
      fetchStockNews(props.stockSymbol)
    }
  }
}

// 自动刷新定时器
let refreshTimer: number | null = null

/**
 * 启动自动刷新
 */
const startAutoRefresh = () => {
  // 每10分钟刷新一次新闻
  refreshTimer = window.setInterval(() => {
    refresh()
  }, 600000) // 10分钟
}

/**
 * 停止自动刷新
 */
const stopAutoRefresh = () => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
    refreshTimer = null
  }
}

// 监听股票代码变化
watch(() => props.stockSymbol, (newSymbol) => {
  if (newSymbol && activeTab.value === 'stock') {
    fetchStockNews(newSymbol)
  }
})

// 组件挂载时
onMounted(() => {
  console.log('[NewsPanel] 组件已挂载')
  // 初始加载新闻
  fetchMarketNews()
  // 启动自动刷新
  startAutoRefresh()
})

// 组件卸载时
onUnmounted(() => {
  console.log('[NewsPanel] 组件已卸载')
  stopAutoRefresh()
})

// 暴露方法供父组件调用
defineExpose({
  refresh,
  fetchMarketNews,
  fetchStockNews,
})
</script>

<style scoped lang="scss">
// TradingView 官方紧凑设计
.news-panel {
  width: 280px;
  height: 100%;
  background: #131722;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  border-top: 1px solid #2a2e39;
}

.news-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  border-bottom: 1px solid #2a2e39;
  min-height: 40px;

  .header-title {
    font-size: 13px;
    font-weight: 600;
    color: #d1d4dc;
  }

  .header-actions {
    display: flex;
    gap: 4px;

    .icon-btn {
      width: 24px;
      height: 24px;
      border: none;
      background: transparent;
      color: #787b86;
      border-radius: 4px;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: all 0.15s ease;

      &:hover {
        background: #2a2e39;
        color: #d1d4dc;
      }
    }
  }
}

.news-tabs {
  display: flex;
  gap: 1px;
  padding: 4px 8px 0;
  border-bottom: 1px solid #2a2e39;

  .tab-btn {
    flex: 1;
    padding: 6px 8px;
    background: transparent;
    border: none;
    color: #787b86;
    font-size: 12px;
    font-weight: 500;
    cursor: pointer;
    border-radius: 4px 4px 0 0;
    transition: all 0.15s ease;
    border-bottom: 2px solid transparent;

    &:hover {
      color: #d1d4dc;
      background: #1e222d;
    }

    &.active {
      color: #2962ff;
      border-bottom-color: #2962ff;
    }
  }
}

.news-list {
  flex: 1;
  overflow-y: auto;

  /* 自定义滚动条 */
  &::-webkit-scrollbar {
    width: 6px;
  }

  &::-webkit-scrollbar-track {
    background: #131722;
  }

  &::-webkit-scrollbar-thumb {
    background: #2a2e39;
    border-radius: 3px;

    &:hover {
      background: #363a45;
    }
  }
}

.news-item {
  display: block;
  padding: 10px 12px;
  border-bottom: 1px solid #2a2e39;
  text-decoration: none;
  transition: background 0.1s ease;

  &:hover {
    background: #1e222d;
  }

  &:last-child {
    border-bottom: none;
  }

  .news-source {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 4px;

    .source-name {
      font-size: 11px;
      color: #787b86;
    }

    .news-time {
      font-size: 10px;
      color: #787b86;
    }
  }

  .news-title {
    font-size: 12px;
    font-weight: 500;
    color: #d1d4dc;
    line-height: 1.4;
    margin-bottom: 4px;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }

  .news-meta {
    .sentiment {
      font-size: 10px;
      padding: 2px 6px;
      border-radius: 3px;
      font-weight: 500;

      &.bullish {
        color: #26A69A;
        background: rgba(38, 166, 154, 0.1);
      }

      &.bearish {
        color: #EF5350;
        background: rgba(239, 83, 80, 0.1);
      }

      &.neutral {
        color: #787b86;
        background: rgba(120, 123, 134, 0.1);
      }
    }
  }
}
</style>

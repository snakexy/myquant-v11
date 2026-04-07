<template>
  <div class="stock-search-box">
    <input
      v-model="searchText"
      type="text"
      class="search-input"
      :placeholder="isZh ? '代码/名称/拼音' : 'Symbol/Name/Pinyin'"
      @input="handleSearchInput"
      @focus="showResults = true"
      @blur="handleBlur"
    />

    <!-- 搜索结果下拉列表 -->
    <div v-if="showResults && searchText && searchResults.length > 0" class="search-dropdown">
      <div
        v-for="stock in searchResults.slice(0, 8)"
        :key="stock.symbol"
        class="search-result-item"
        @mousedown="selectStock(stock)"
      >
        <span class="result-symbol">{{ stock.symbol }}</span>
        <span class="result-name">{{ stock.name }}</span>
      </div>
      <div v-if="searchResults.length > 8" class="search-more">
        还有 {{ searchResults.length - 8 }} 个...
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { STOCK_PINYIN_MAPPING } from '@/assets/stock-pinyin-mapping.js'

interface StockInfo {
  symbol: string
  name: string
  pinyin_initials: string
  pinyin_full: string
}

const emit = defineEmits<{
  select: [symbol: string, name: string]
}>()

const isZh = ref(navigator.language === 'zh-CN')
const searchText = ref('')
const showResults = ref(false)

// 搜索结果
const searchResults = computed(() => {
  if (!searchText.value) return []

  const term = searchText.value.toLowerCase().trim()
  const results: StockInfo[] = []

  // 检查是否是纯数字（股票代码）
  const isNumeric = /^\d+$/.test(term)

  for (const [symbol, info] of Object.entries(STOCK_PINYIN_MAPPING)) {
    const stockInfo = info as StockInfo

    // 1. 代码匹配
    const symbolMatch = symbol.toLowerCase().includes(term)
    const codeOnly = symbol.replace(/\.(SH|SZ|BJ)$/i, '')
    const codeMatch = isNumeric && codeOnly.includes(term)

    // 2. 名称匹配
    const nameMatch = stockInfo.name.toLowerCase().includes(term)

    // 3. 拼音首字母匹配
    const initialsMatch = stockInfo.pinyin_initials?.toLowerCase().includes(term)

    // 4. 全拼匹配
    const fullMatch = stockInfo.pinyin_full?.toLowerCase().includes(term)

    if (symbolMatch || codeMatch || nameMatch || initialsMatch || fullMatch) {
      results.push({
        symbol,
        name: stockInfo.name,
        pinyin_initials: stockInfo.pinyin_initials || '',
        pinyin_full: stockInfo.pinyin_full || ''
      })
    }
  }

  // 排序：代码完全匹配 > 代码开头匹配 > 名称匹配 > 拼音匹配
  results.sort((a, b) => {
    const aCode = a.symbol.replace(/\.(SH|SZ|BJ)$/i, '')
    const bCode = b.symbol.replace(/\.(SH|SZ|BJ)$/i, '')

    if (a.symbol.toLowerCase() === term) return -1
    if (b.symbol.toLowerCase() === term) return 1

    if (isNumeric && aCode === term) return -1
    if (isNumeric && bCode === term) return 1

    if (isNumeric && aCode.startsWith(term)) return -1
    if (isNumeric && bCode.startsWith(term)) return 1

    return 0
  })

  return results
})

// 处理搜索输入
const handleSearchInput = () => {
  showResults.value = true
}

// 处理失焦
const handleBlur = () => {
  setTimeout(() => {
    showResults.value = false
  }, 200)
}

// 选择股票
const selectStock = (stock: StockInfo) => {
  searchText.value = ''
  showResults.value = false
  emit('select', stock.symbol, stock.name)
}
</script>

<style scoped>
.stock-search-box {
  flex: 1;
  position: relative;
}

.search-input {
  width: 100%;
  padding: 6px 10px;
  background: #2a2e39;
  border: 1px solid #363a45;
  border-radius: 4px;
  color: #d1d4dc;
  font-size: 12px;
}

.search-input:focus {
  outline: none;
  border-color: #ef5350;
}

.search-input::placeholder {
  color: #787b86;
}

/* 搜索结果下拉列表 */
.search-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  margin-top: 4px;
  background: #1e222d;
  border: 1px solid #2a2e39;
  border-radius: 4px;
  max-height: 250px;
  overflow-y: auto;
  z-index: 1000;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.search-dropdown::-webkit-scrollbar {
  width: 6px;
}

.search-dropdown::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 3px;
}

.search-result-item {
  display: flex;
  align-items: center;
  padding: 8px 12px;
  cursor: pointer;
  transition: background 0.2s ease;
  border-bottom: 1px solid #2a2e39;
}

.search-result-item:last-child {
  border-bottom: none;
}

.search-result-item:hover {
  background: #2a2e39;
}

.result-symbol {
  font-size: 12px;
  font-weight: 500;
  color: #ef5350;
  min-width: 90px;
}

.result-name {
  flex: 1;
  font-size: 12px;
  color: #d1d4dc;
  margin-left: 8px;
}

.search-more {
  padding: 8px 12px;
  font-size: 11px;
  color: #787b86;
  text-align: center;
  background: rgba(255, 255, 255, 0.03);
}
</style>

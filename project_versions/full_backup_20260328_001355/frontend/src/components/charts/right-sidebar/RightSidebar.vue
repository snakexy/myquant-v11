<template>
  <div class="right-sidebar">
    <Watchlist
      :current-stock="currentStock"
      @select-stock="handleStockSelect"
    />
    <NewsPanel
      :stock-symbol="currentStock.symbol"
    />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import Watchlist from './Watchlist.vue'
import NewsPanel from './NewsPanel.vue'

interface StockQuote {
  symbol: string
  name: string
  price: number
  change: number
  changePercent: number
}

const props = defineProps<{
  currentStock: { symbol: string; name: string }
}>()

const emit = defineEmits<{
  selectStock: [stock: StockQuote]
}>()

/**
 * 处理股票选择事件
 * 当用户在观察列表中点击某只股票时触发
 */
const handleStockSelect = (stock: StockQuote) => {
  console.log('[RightSidebar] 股票选择事件:', stock)
  emit('selectStock', stock)
}

// 暴露方法供父组件调用
defineExpose({
  handleStockSelect,
})
</script>

<style scoped lang="scss">
.right-sidebar {
  width: 280px;
  height: 100%;
  background: #131722;
  border-left: 1px solid #2a2e39;
  display: flex;
  flex-direction: column;
  overflow: hidden;

  // ✅ 确保边栏不会阻挡图表的鼠标事件
  // 边栏只在280px宽度内接收事件，不会溢出到图表区域
  pointer-events: auto;
}
</style>

<template>
  <div class="kline-page">
    <TradingViewKLineUnified
      :key="stockCode"
      :symbol="formattedSymbol"
      :stock-name="stockName"
      :stock-code="stockCode"
      :height="'100%'"
      :show-toolbar="true"
    />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import TradingViewKLineUnified from '@/components/charts/TradingViewKLineUnified.vue'

const route = useRoute()

const stockCode = computed(() => (route.query.code as string) || '')
const stockName = computed(() => (route.query.name as string) || '股票详情')

// 格式化股票代码为完整格式（如 000001.SZ）
const formattedSymbol = computed(() => {
  const code = stockCode.value
  if (!code) return ''

  // 如果已经是完整格式，直接返回
  if (code.includes('.')) return code

  // 根据代码规则添加市场后缀
  if (code.startsWith('6')) {
    return `${code}.SH`
  } else if (code.startsWith(('0', '3'))) {
    return `${code}.SZ`
  }
  return code
})
</script>

<style scoped lang="scss">
.kline-page {
  position: fixed;
  top: 48px;  // App.vue header 高度
  left: 0;
  right: 0;
  bottom: 32px;  // App.vue footer 高度
  background: #0f0f23;
  display: flex;
  flex-direction: column;
  z-index: 999;  // ✅ 大幅提高 z-index，确保在最上层

  // ✅ 确保可以接收鼠标事件
  pointer-events: auto !important;

  // ✅ 确保所有子元素都能接收鼠标事件
  & > * {
    pointer-events: auto !important;
  }
}
</style>

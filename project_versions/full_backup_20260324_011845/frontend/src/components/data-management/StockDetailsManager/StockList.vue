<template>
  <div class="stock-list-panel">
    <div class="stock-list">
      <div
        v-for="stock in data"
        :key="stock.code"
        :class="['stock-item', { active: modelValue === stock.code }]"
        @click="handleSelect(stock)"
      >
        <div class="stock-code">{{ stock.code }}</div>
        <div class="stock-name">{{ stock.name }}</div>
        <div class="stock-market">
          <el-tag :type="getMarketTagType(stock.market)" size="small">{{ stock.market }}</el-tag>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface StockInfo {
  code: string
  name: string
  market: string
  sector?: string
}

interface Props {
  data: StockInfo[]
  modelValue?: string | null
}

const props = defineProps<Props>()

const emit = defineEmits<{
  'update:modelValue': [code: string]
  'select': [stock: StockInfo]
}>()

// 获取市场标签类型
const getMarketTagType = (market: string) => {
  const typeMap: Record<string, string> = {
    '上海': 'success',
    '深圳': 'warning',
    '北交所': 'info'
  }
  return typeMap[market] || 'info'
}

// 处理选择
const handleSelect = (stock: StockInfo) => {
  emit('update:modelValue', stock.code)
  emit('select', stock)
}
</script>

<style scoped>
.stock-list-panel {
  margin-bottom: 20px;
}

.stock-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 12px;
}

.stock-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.stock-item:hover {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(102, 126, 234, 0.5);
  transform: translateY(-2px);
}

.stock-item.active {
  background: rgba(102, 126, 234, 0.2);
  border-color: #2962ff;
}

.stock-code {
  font-size: 14px;
  font-weight: 600;
  color: #2962ff;
  min-width: 60px;
}

.stock-name {
  flex: 1;
  font-size: 14px;
  color: rgba(255, 255, 255, 0.8);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .stock-list {
    grid-template-columns: 1fr;
  }
}
</style>

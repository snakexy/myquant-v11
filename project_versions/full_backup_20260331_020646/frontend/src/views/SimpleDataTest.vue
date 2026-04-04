<template>
  <div style="padding: 20px; background: #1a1a2e; min-height: 100vh; color: white;">
    <h1>简单测试页面</h1>
    <p>如果你能看到这个页面，说明基本的渲染没有问题。</p>
    <div style="margin-top: 20px;">
      <h2>测试数据：</h2>
      <ul>
        <li>数据库统计: {{ stats.totalStocks }} 只股票</li>
        <li>数据新鲜度: {{ freshness.overallScore }}%</li>
        <li>数据源数量: {{ sources.length }}</li>
      </ul>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const stats = ref({
  totalStocks: 4856,
  totalRecords: '12.5M'
})

const freshness = ref({
  overallScore: 94
})

const sources = ref([
  { name: 'QMT', status: 'active' },
  { name: '通达信', status: 'active' }
])

onMounted(() => {
  console.log('简单测试页面已加载')
})
</script>
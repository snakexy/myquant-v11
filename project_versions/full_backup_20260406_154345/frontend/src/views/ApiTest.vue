<template>
  <div class="api-test-container">
    <h1>API测试页面</h1>
    
    <div class="test-section">
      <h2>数据管理API测试</h2>
      
      <div class="test-buttons">
        <button @click="testDatabaseStats" :disabled="loading.dbStats">
          测试数据库统计
        </button>
        <button @click="testDataFreshness" :disabled="loading.freshness">
          测试数据新鲜度
        </button>
        <button @click="testStockCategories" :disabled="loading.categories">
          测试股票分类
        </button>
        <button @click="testDataSources" :disabled="loading.sources">
          测试数据源
        </button>
        <button @click="testUpdateSchedules" :disabled="loading.schedules">
          测试更新计划
        </button>
      </div>
      
      <div class="test-results">
        <div v-if="results.length === 0" class="no-results">
          点击上方按钮测试API
        </div>
        
        <div v-for="(result, index) in results" :key="index" class="result-item">
          <h3>{{ result.title }}</h3>
          <div class="result-status" :class="result.success ? 'success' : 'error'">
            {{ result.success ? '✅ 成功' : '❌ 失败' }}
          </div>
          <pre class="result-data">{{ JSON.stringify(result.data, null, 2) }}</pre>
          <div v-if="result.error" class="result-error">
            错误信息: {{ result.error }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { 
  testDatabaseStats, 
  testDataFreshness, 
  testStockCategories, 
  testDataSources,
  testUpdateSchedules
} from '@/api/simple-test.js'

const loading = ref({
  dbStats: false,
  freshness: false,
  categories: false,
  sources: false,
  schedules: false
})

const results = ref<Array<{
  title: string
  success: boolean
  data: any
  error?: string
}>>([])

const addResult = (title: string, success: boolean, data: any, error?: string) => {
  results.value.unshift({
    title,
    success,
    data,
    error
  })
  
  // 只保留最近10条结果
  if (results.value.length > 10) {
    results.value = results.value.slice(0, 10)
  }
}

const testDatabaseStats = async () => {
  loading.value.dbStats = true
  try {
    const data = await testDatabaseStats()
    console.log('数据库统计API响应:', data)
    addResult('数据库统计', true, data)
  } catch (error) {
    console.error('数据库统计API错误:', error)
    addResult('数据库统计', false, null, error.message)
  } finally {
    loading.value.dbStats = false
  }
}

const testDataFreshness = async () => {
  loading.value.freshness = true
  try {
    const data = await testDataFreshness()
    console.log('数据新鲜度API响应:', data)
    addResult('数据新鲜度', true, data)
  } catch (error) {
    console.error('数据新鲜度API错误:', error)
    addResult('数据新鲜度', false, null, error.message)
  } finally {
    loading.value.freshness = false
  }
}

const testStockCategories = async () => {
  loading.value.categories = true
  try {
    const data = await testStockCategories()
    console.log('股票分类API响应:', data)
    addResult('股票分类', true, data)
  } catch (error) {
    console.error('股票分类API错误:', error)
    addResult('股票分类', false, null, error.message)
  } finally {
    loading.value.categories = false
  }
}

const testDataSources = async () => {
  loading.value.sources = true
  try {
    const data = await testDataSources()
    console.log('数据源API响应:', data)
    addResult('数据源', true, data)
  } catch (error) {
    console.error('数据源API错误:', error)
    addResult('数据源', false, null, error.message)
  } finally {
    loading.value.sources = false
  }
}

const testUpdateSchedules = async () => {
  loading.value.schedules = true
  try {
    const data = await testUpdateSchedules()
    console.log('更新计划API响应:', data)
    addResult('更新计划', true, data)
  } catch (error) {
    console.error('更新计划API错误:', error)
    addResult('更新计划', false, null, error.message)
  } finally {
    loading.value.schedules = false
  }
}
</script>

<style lang="scss" scoped>
.api-test-container {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
  background: #0a0a0f;
  color: #f8fafc;
  min-height: 100vh;
}

h1 {
  color: #2563eb;
  margin-bottom: 30px;
}

.test-section {
  background: #1a1a2e;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
}

h2 {
  color: #f8fafc;
  margin-bottom: 20px;
}

.test-buttons {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  margin-bottom: 20px;
  
  button {
    padding: 10px 20px;
    background: #2563eb;
    color: white;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    transition: all 0.3s ease;
    
    &:hover:not(:disabled) {
      background: #1d4ed8;
    }
    
    &:disabled {
      background: #64748b;
      cursor: not-allowed;
    }
  }
}

.test-results {
  .no-results {
    text-align: center;
    color: #94a3b8;
    padding: 40px;
    background: #0f172a;
    border-radius: 6px;
  }
  
  .result-item {
    background: #0f172a;
    border-radius: 6px;
    padding: 15px;
    margin-bottom: 15px;
    
    h3 {
      margin: 0 0 10px 0;
      color: #f8fafc;
    }
    
    .result-status {
      margin-bottom: 10px;
      font-weight: bold;
      
      &.success {
        color: #10b981;
      }
      
      &.error {
        color: #ef4444;
      }
    }
    
    .result-error {
      color: #ef4444;
      margin-top: 10px;
      padding: 10px;
      background: rgba(239, 68, 68, 0.1);
      border-radius: 4px;
    }
    
    .result-data {
      background: #1a1a2e;
      border: 1px solid #334155;
      border-radius: 4px;
      padding: 10px;
      font-size: 12px;
      color: #e2e8f0;
      overflow-x: auto;
      max-height: 300px;
      overflow-y: auto;
    }
  }
}
</style>
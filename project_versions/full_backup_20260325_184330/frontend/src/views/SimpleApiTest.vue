<template>
  <div class="simple-test">
    <h1>简单API测试</h1>
    <button @click="testAPI">测试API</button>
    <div v-if="result">
      <h3>结果:</h3>
      <pre>{{ result }}</pre>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      result: null
    }
  },
  methods: {
    async testAPI() {
      try {
        // 直接使用fetch测试
        const response = await fetch('http://localhost:8000/api/v1/data-management/database/stats')
        const data = await response.json()
        console.log('API响应:', data)
        this.result = JSON.stringify(data, null, 2)
      } catch (error) {
        console.error('API错误:', error)
        this.result = '错误: ' + error.message
      }
    }
  }
}
</script>

<style scoped>
.simple-test {
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
  color: white;
}

button {
  padding: 10px 20px;
  background: #2563eb;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  margin-bottom: 20px;
}

pre {
  background: #1a1a2e;
  padding: 10px;
  border-radius: 4px;
  overflow-x: auto;
}
</style>
<template>
  <div class="test-home">
    <h1>测试页面</h1>
    <p>如果你能看到这个页面，说明Vue路由工作正常</p>
    <div class="test-cards">
      <div class="test-card" v-for="i in 6" :key="i">
        <h3>测试卡片 {{ i }}</h3>
        <p>这是一个测试卡片</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// 简单的测试页面
</script>

<style scoped>
.test-home {
  padding: 20px;
  color: white;
  background: #0a0a0f;
  min-height: 100vh;
}

h1 {
  color: #667eea;
  margin-bottom: 20px;
}

.test-cards {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  margin-top: 20px;
}

.test-card {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  padding: 20px;
  color: white;
}

.test-card h3 {
  margin-top: 0;
  color: #667eea;
}
</style>
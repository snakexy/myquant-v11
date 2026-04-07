<template>
  <div class="test-page">
    <h1>智能节点系统测试页面</h1>
    <p>如果你能看到这个页面，说明路由和基本组件加载正常。</p>
    <div class="node-test">
      <div class="sample-node">测试节点</div>
    </div>
  </div>
</template>

<script setup lang="ts">
console.log('Test component loaded')
</script>

<style scoped>
.test-page {
  padding: 20px;
  background: #1a1a1a;
  color: white;
  min-height: 100vh;
}

.node-test {
  margin-top: 20px;
}

.sample-node {
  display: inline-block;
  padding: 10px 20px;
  background: #2196F3;
  border-radius: 4px;
  color: white;
  font-weight: bold;
}
</style>
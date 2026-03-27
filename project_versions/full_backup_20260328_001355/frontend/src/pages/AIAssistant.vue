<template>
  <div class="ai-assistant">
    <h1>AI助手</h1>
    <div class="ai-container">
      <AIStrategyAssistant size="large" :height="600" />
    </div>
  </div>
</template>

<script setup lang="ts">
import AIStrategyAssistant from '../components/cards/AIStrategyAssistant.vue'
</script>

<style lang="scss" scoped>
.ai-assistant {
  padding: 24px;
  height: calc(100vh - 120px);
  
  h1 {
    margin: 0 0 24px 0;
    color: var(--text-primary);
  }
  
  .ai-container {
    height: 100%;
  }
}
</style>
<template>
  <nav class="stage-nav">
    <button
      :class="['stage-btn', { active: currentStageModule === 'research' }]"
      @click="$emit('switch-module', 'research')"
    >
      <svg class="icon-nav" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <circle cx="11" cy="11" r="8"/>
        <path d="M21 21l-4.35-4.35"/>
      </svg>
      {{ isZh ? '研究分析' : 'Research' }}
    </button>
    <button
      :class="['stage-btn', { active: currentStageModule === 'backtest' }]"
      @click="$emit('switch-module', 'backtest')"
    >
      <svg class="icon-nav" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
        <circle cx="12" cy="12" r="3"/>
      </svg>
      {{ isZh ? '回测' : 'Backtest' }}
    </button>
    <button
      :class="['stage-btn', { active: currentStageModule === 'signal' }]"
      @click="$emit('switch-module', 'signal')"
    >
      <svg class="icon-nav" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M22 12h-4l-3 9L9 3l-3 9H2"/>
      </svg>
      {{ isZh ? '信号生成' : 'Signal' }}
    </button>
  </nav>
</template>

<script setup lang="ts">
import { PropType } from 'vue'

defineProps({
  currentStageModule: {
    type: String as PropType<'research' | 'backtest' | 'signal'>,
    required: true
  },
  isZh: {
    type: Boolean,
    default: true
  }
})

defineEmits<{
  'switch-module': [module: 'research' | 'backtest' | 'signal']
}>()
</script>

<style scoped lang="scss">
/* 阶段导航菜单样式 */
.stage-nav {
  display: flex;
  gap: 4px;
  flex: 1;
  margin-left: 16px;
}

.stage-btn {
  padding: 8px 16px;
  background: transparent;
  border: none;
  border-bottom: 2px solid transparent;
  border-radius: 0;
  color: var(--text-secondary);
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s ease;
  white-space: nowrap;
  display: flex;
  align-items: center;
  gap: 6px;
}

.stage-btn:hover {
  color: var(--text-primary);
  background: transparent;
}

.stage-btn.active {
  color: var(--accent-blue);
  border-bottom-color: var(--accent-blue);
  background: transparent;
}

.icon-nav {
  width: 14px;
  height: 14px;
  flex-shrink: 0;
}
</style>

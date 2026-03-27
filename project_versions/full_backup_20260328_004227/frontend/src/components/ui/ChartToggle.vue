<template>
  <button
    class="chart-toggle"
    :class="{ active }"
    :title="title"
    @click="handleClick"
  >
    <span v-html="icon"></span>
  </button>
</template>

<script setup lang="ts">
interface Props {
  icon: string
  title?: string
  active?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  title: '',
  active: false
})

const emit = defineEmits<{
  click: []
}>()

const handleClick = () => {
  emit('click')
}
</script>

<style lang="scss" scoped>
.chart-toggle {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  padding: 0;
  background: var(--bg-tertiary, #2a2e39);
  border: 1px solid var(--border-color, #2a2e39);
  border-radius: 4px;
  color: var(--text-secondary, #787b86);
  cursor: pointer;
  transition: all 0.2s;

  :deep(svg) {
    width: 14px;
    height: 14px;
  }

  &:hover {
    border-color: var(--accent-blue, #2962ff);
    color: var(--text-primary, #d1d4dc);
  }

  &.active {
    background: var(--accent-blue, #2962ff);
    border-color: var(--accent-blue, #2962ff);
    color: #fff;
  }
}
</style>

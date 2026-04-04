<template>
  <div :class="['stage-status-card', stageType]" @click="handleClick">
    <div class="stage-icon">{{ icon }}</div>
    <div class="stage-content">
      <div class="stage-label">{{ title }}</div>
      <div class="stage-count">{{ count }}</div>
      <div class="stage-detail">{{ detail }}</div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  icon: string
  title: string
  count: number
  detail: string
  stageType?: 'research' | 'validation' | 'production'
}

withDefaults(defineProps<Props>(), {
  stageType: 'research'
})

const emit = defineEmits<{
  click: [event: MouseEvent]
}>()

const handleClick = (event: MouseEvent) => {
  emit('click', event)
}
</script>

<style lang="scss" scoped>
.stage-status-card {
  background: var(--bg-primary);
  padding: 20px 24px;
  display: flex;
  align-items: center;
  gap: 16px;
  cursor: pointer;
  transition: background 0.15s;

  &:hover {
    background: var(--bg-secondary);
  }
}

.stage-icon {
  width: 48px;
  height: 48px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
}

.stage-status-card.research .stage-icon {
  background: rgba(41, 98, 255, 0.15);
  color: var(--accent-blue);
}

.stage-status-card.validation .stage-icon {
  background: rgba(255, 152, 0, 0.15);
  color: var(--accent-orange);
}

.stage-status-card.production .stage-icon {
  background: rgba(38, 166, 154, 0.15);
  color: var(--accent-green);
}

.stage-content {
  flex: 1;
}

.stage-label {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-secondary);
}

.stage-count {
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary);
  margin-top: -2px;
}

.stage-detail {
  font-size: 12px;
  color: var(--text-muted);
  margin-top: 2px;
}
</style>

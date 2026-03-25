<template>
  <div class="risk-event-card">
    <div class="event-marker">
      <span :class="['marker-dot', event.level]"></span>
      <span class="marker-line"></span>
    </div>
    <div :class="['event-card', event.level]">
      <div class="event-header">
        <span class="event-level">{{ event.level.toUpperCase() }}</span>
        <span class="event-time">{{ formattedTime }}</span>
      </div>
      <div class="event-message">{{ event.message }}</div>
      <div v-if="event.details" class="event-details">{{ event.details }}</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface RiskEvent {
  event_id: string
  level: 'info' | 'warning' | 'error' | 'success'
  message: string
  details?: string
  timestamp: string
}

interface Props {
  event: RiskEvent
}

const props = defineProps<Props>()

const formattedTime = computed(() => {
  const date = new Date(props.event.timestamp)
  return date.toLocaleString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
})
</script>

<style lang="scss" scoped>
.risk-event-card {
  display: flex;
  gap: 12px;
}

.event-marker {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 12px;
  flex-shrink: 0;
}

.marker-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  flex-shrink: 0;

  &.info {
    background: #409EFF;
    box-shadow: 0 0 6px rgba(64, 158, 255, 0.5);
  }

  &.warning {
    background: #E6A23C;
    box-shadow: 0 0 6px rgba(230, 162, 60, 0.5);
  }

  &.error {
    background: #F56C6C;
    box-shadow: 0 0 6px rgba(245, 108, 108, 0.5);
  }

  &.success {
    background: #67C23A;
    box-shadow: 0 0 6px rgba(103, 194, 58, 0.5);
  }
}

.marker-line {
  flex: 1;
  width: 2px;
  background: var(--border-color, #2a2e39);
  margin-top: 4px;
}

.event-card {
  flex: 1;
  padding: 12px 16px;
  background: var(--bg-secondary, #1e222d);
  border: 1px solid var(--border-color, #2a2e39);
  border-radius: 8px;
  margin-bottom: 12px;
  transition: all 0.2s ease;

  &:hover {
    border-color: var(--accent-blue, #409EFF);
  }

  &.error {
    border-left: 3px solid #F56C6C;
  }

  &.warning {
    border-left: 3px solid #E6A23C;
  }

  &.info {
    border-left: 3px solid #409EFF;
  }

  &.success {
    border-left: 3px solid #67C23A;
  }
}

.event-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}

.event-level {
  font-size: 10px;
  font-weight: 600;
  padding: 2px 6px;
  border-radius: 4px;
  text-transform: uppercase;

  .error & {
    color: #F56C6C;
    background: rgba(245, 108, 108, 0.15);
  }

  .warning & {
    color: #E6A23C;
    background: rgba(230, 162, 60, 0.15);
  }

  .info & {
    color: #409EFF;
    background: rgba(64, 158, 255, 0.15);
  }

  .success & {
    color: #67C23A;
    background: rgba(103, 194, 58, 0.15);
  }
}

.event-time {
  font-size: 11px;
  color: var(--text-muted, #787b86);
}

.event-message {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-primary, #d1d4dc);
  margin-bottom: 4px;
}

.event-details {
  font-size: 12px;
  color: var(--text-muted, #787b86);
}
</style>

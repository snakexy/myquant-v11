<template>
  <div class="task-card" @click="handleClick">
    <div class="task-header">
      <div class="task-info">
        <div class="task-title">{{ title }}</div>
        <div class="task-id">#{{ taskId }}</div>
      </div>
      <span :class="['task-badge', status]">
        {{ statusText }}
      </span>
    </div>
    <div v-if="description" class="task-description">
      {{ description }}
    </div>
    <div v-if="configTags.length" class="task-config">
      <span v-for="(tag, index) in configTags" :key="index" class="config-tag">
        {{ tag }}
      </span>
    </div>
    <div v-if="created || duration" class="task-meta">
      <div v-if="created" class="meta-item">📅 {{ created }}</div>
      <div v-if="duration" class="meta-item">⏱️ {{ duration }}</div>
    </div>
    <div v-if="showProgress" class="task-progress">
      <div class="progress-header">
        <span>进度</span>
        <span>{{ progress }}%</span>
      </div>
      <div class="progress-bar">
        <div class="progress-fill" :style="{ width: progress + '%' }"></div>
      </div>
    </div>
    <!-- 操作按钮 -->
    <div class="task-actions" @click.stop>
      <button class="action-btn archive" title="保存到策略库">
        💾
      </button>
      <button class="action-btn restore" title="重新激活">
        ⚡
      </button>
      <button class="action-btn delete" title="删除任务">
        🗑️
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  title: string
  taskId?: string | number
  status?: 'running' | 'completed' | 'queued' | 'failed'
  description?: string
  configTags?: string[]
  created?: string
  duration?: string
  showProgress?: boolean
  progress?: number
}

const props = withDefaults(defineProps<Props>(), {
  status: 'running',
  configTags: () => [],
  showProgress: false,
  progress: 0
})

const emit = defineEmits<{
  click: [event: MouseEvent]
}>()

const statusText = computed(() => {
  const map: Record<string, string> = {
    running: '运行中',
    completed: '已完成',
    queued: '排队中',
    failed: '失败'
  }
  return map[props.status] || props.status
})

const handleClick = (event: MouseEvent) => {
  emit('click', event)
}
</script>

<style lang="scss" scoped>
.task-card {
  background: #1e222d;
  border: 1px solid #2a2e39;
  border-radius: 8px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.2s;

  &:hover {
    border-color: #2962ff;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  }
}

.task-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
}

.task-info {
  flex: 1;
}

.task-title {
  font-size: 15px;
  font-weight: 600;
  color: #d1d4dc;
  margin-bottom: 4px;
}

.task-id {
  font-size: 11px;
  color: #787b86;
  font-family: monospace;
}

.task-badge {
  padding: 4px 10px;
  border-radius: 4px;
  font-size: 10px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.3px;
}

.task-badge.running {
  background: rgba(41, 98, 255, 0.2);
  color: #2962ff;
}

.task-badge.completed {
  background: rgba(38, 166, 154, 0.2);
  color: #26a69a;
}

.task-badge.queued {
  background: rgba(255, 152, 0, 0.2);
  color: #ff9800;
}

.task-badge.failed {
  background: rgba(239, 83, 80, 0.2);
  color: #ef5350;
}

.task-description {
  font-size: 13px;
  color: #787b86;
  line-height: 1.6;
  margin-bottom: 12px;
}

.task-config {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 12px;
}

.config-tag {
  display: inline-flex;
  align-items: center;
  padding: 4px 8px;
  background: #2a2e39;
  border: 1px solid #363a45;
  border-radius: 4px;
  font-size: 11px;
  color: #787b86;
}

.task-meta {
  display: flex;
  gap: 16px;
  font-size: 11px;
  color: #787b86;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
}

.task-progress {
  margin-top: 12px;
}

.progress-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 6px;
  font-size: 11px;
  color: #787b86;
}

.progress-bar {
  height: 4px;
  background: #2a2e39;
  border-radius: 2px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #2962ff, #26a69a);
  border-radius: 2px;
  transition: width 0.3s;
}

/* 任务操作按钮 */
.task-actions {
  display: flex;
  gap: 8px;
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #2a2e39;
  justify-content: flex-end;
}

.action-btn {
  width: 32px;
  height: 32px;
  border: 1px solid #2a2e39;
  border-radius: 6px;
  background: #2a2e39;
  cursor: pointer;
  font-size: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  opacity: 0.7;

  &:hover {
    opacity: 1;
    transform: scale(1.1);
  }

  &.archive:hover {
    border-color: #2962ff;
    background: rgba(41, 98, 255, 0.1);
  }

  &.restore:hover {
    border-color: #26a69a;
    background: rgba(38, 166, 154, 0.1);
  }

  &.delete:hover {
    border-color: #ef5350;
    background: rgba(239, 83, 80, 0.1);
  }
}
</style>

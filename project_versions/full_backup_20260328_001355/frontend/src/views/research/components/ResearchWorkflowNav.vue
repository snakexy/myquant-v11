<template>
  <aside class="panel workflow-panel">
    <div class="panel-header">
      <span class="panel-title">
        <svg class="icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polyline points="9 11 12 14 22 4"/>
          <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/>
        </svg>
        {{ isZh ? '工作流步骤' : 'Workflow Steps' }}
      </span>
    </div>
    <div class="workflow-list">
      <div
        v-for="step in workflowSteps"
        :key="step.id"
        :class="['workflow-step', step.status, { selected: currentStep === step.id }]"
        @click="$emit('select-step', step.id)"
      >
        <div class="step-icon">
          <!-- 完成：打勾图标 -->
          <svg v-if="step.status === 'completed'" class="icon-check" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
            <polyline points="20 6 9 17 4 12"/>
          </svg>
          <!-- 进行中/待处理：数字或图标 -->
          <template v-else>
            <svg v-if="step.id === 1" class="icon-step" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <ellipse cx="12" cy="5" rx="9" ry="3"/>
              <path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/>
              <path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/>
            </svg>
            <svg v-else-if="step.id === 2" class="icon-step" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <rect x="4" y="4" width="16" height="16" rx="2"/>
              <path d="M9 9h6M9 13h6M9 17h4"/>
            </svg>
            <svg v-else-if="step.id === 3" class="icon-step" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M21 21H3V3"/>
              <path d="M21 9l-6 6-4-4-6 6"/>
            </svg>
            <svg v-else-if="step.id === 4" class="icon-step" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
            </svg>
            <svg v-else-if="step.id === 5" class="icon-step" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M12 2L2 7l10 5 10-5-10-5z"/>
              <path d="M2 17l10 5 10-5"/>
              <path d="M2 12l10 5 10-5"/>
            </svg>
            <svg v-else-if="step.id === 6" class="icon-step" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
              <polyline points="22 4 12 14.01 9 11.01"/>
            </svg>
            <span v-else class="step-number">{{ step.id }}</span>
          </template>
        </div>
        <div class="step-info">
          <div class="step-title">{{ isZh ? step.nameZh : step.name }}</div>
          <div :class="['step-status', step.status]">
            <span class="status-dot"></span>
            {{ getStepStatusText(step.status) }}
          </div>
        </div>
      </div>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { PropType } from 'vue'

interface WorkflowStep {
  id: number
  name: string
  nameZh: string
  status: 'pending' | 'active' | 'completed'
}

defineProps({
  workflowSteps: {
    type: Array as PropType<WorkflowStep[]>,
    required: true
  },
  currentStep: {
    type: Number,
    required: true
  },
  isZh: {
    type: Boolean,
    default: true
  }
})

defineEmits<{
  'select-step': [stepId: number]
}>()

const getStepStatusText = (status: string) => {
  const statusMapZh: Record<string, string> = {
    completed: '已完成',
    active: '进行中',
    pending: '待处理'
  }
  const statusMapEn: Record<string, string> = {
    completed: 'Completed',
    active: 'In Progress',
    pending: 'Pending'
  }

  // 简化处理，默认使用中文
  return statusMapZh[status] || status
}
</script>

<style scoped lang="scss">
/* 面板基础样式 */
.panel {
  background: var(--bg-primary);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.panel-header {
  background: var(--bg-secondary);
  padding: 12px 16px;
  font-size: 12px;
  font-weight: 600;
  color: var(--text-primary);
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid var(--border-color);
}

.panel-title {
  display: flex;
  align-items: center;
  gap: 8px;
}

.icon-sm {
  width: 16px;
  height: 16px;
}

/* 工作流列表 */
.workflow-list {
  flex: 1;
  overflow-y: auto;
}

.workflow-step {
  padding: 14px 16px;
  border-bottom: 1px solid var(--border-color);
  cursor: pointer;
  transition: background 0.15s;
  display: flex;
  align-items: center;
  gap: 12px;
}

.workflow-step:hover {
  background: var(--bg-secondary);
}

.workflow-step.selected {
  background: var(--bg-tertiary);
  border-left: 2px solid var(--accent-blue);
}

.step-icon {
  width: 32px;
  height: 32px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 700;
}

.workflow-step.completed .step-icon {
  background: var(--accent-green);
  color: white;
}

.workflow-step.active .step-icon {
  background: var(--accent-blue);
  color: white;
}

.workflow-step.pending .step-icon {
  background: var(--bg-tertiary);
  color: var(--text-secondary);
}

.step-info {
  flex: 1;
}

.step-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 2px;
}

.step-status {
  font-size: 11px;
  color: var(--text-secondary);
}

.step-status.completed {
  color: var(--accent-green);
}

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--text-secondary);
}

.step-status.completed .status-dot {
  background: var(--color-up);
  box-shadow: 0 0 6px var(--color-up);
}

.step-status.active .status-dot {
  background: var(--accent-blue);
  box-shadow: 0 0 6px var(--accent-blue);
  animation: pulse 1.5s infinite;
}

.icon-check {
  width: 18px;
  height: 18px;
}

.icon-step {
  width: 18px;
  height: 18px;
}

.step-number {
  font-size: 14px;
  font-weight: 700;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}
</style>

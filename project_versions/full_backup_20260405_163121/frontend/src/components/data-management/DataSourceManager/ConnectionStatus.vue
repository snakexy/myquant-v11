<template>
  <div v-if="status" class="connection-status">
    <div :class="['status-badge', status.connected ? 'success' : 'error']">
      <font-awesome-icon :icon="status.connected ? 'check-circle' : 'times-circle'" />
      {{ status.message }}
    </div>
  </div>
</template>

<script setup lang="ts">
import type { ConnectionStatus } from '../../shared/types'

interface Props {
  status: ConnectionStatus | null
}

defineProps<Props>()
</script>

<style scoped>
.connection-status {
  padding: 12px;
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.05);
}

.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 500;
}

.status-badge.success {
  background: rgba(16, 185, 129, 0.2);
  color: #10b981;
  border: 1px solid rgba(16, 185, 129, 0.3);
}

.status-badge.error {
  background: rgba(239, 68, 68, 0.2);
  color: #ef4444;
  border: 1px solid rgba(239, 68, 68, 0.3);
}
</style>

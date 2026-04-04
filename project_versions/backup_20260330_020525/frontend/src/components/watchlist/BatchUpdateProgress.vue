<template>
  <div class="batch-update-progress" v-if="visible">
    <div class="progress-header">
      <h3>批量更新 LocalDB</h3>
      <el-button
        v-if="status !== 'in_progress'"
        type="primary"
        size="small"
        @click="close"
      >
        关闭
      </el-button>
    </div>

    <div class="progress-content">
      <!-- 进度条 -->
      <div class="progress-bar-container">
        <el-progress
          :percentage="progressPercentage"
          :status="progressStatus"
          :stroke-width="20"
        >
          <span class="progress-text">{{ completed }}/{{ total }}</span>
        </el-progress>
      </div>

      <!-- 当前处理项 -->
      <div v-if="status === 'in_progress'" class="current-item">
        <el-icon class="is-loading"><Loading /></el-icon>
        <span>正在更新: <strong>{{ currentSymbol }}</strong> {{ currentPeriod }}</span>
      </div>

      <!-- 状态消息 -->
      <div class="status-message" :class="status">
        <el-icon v-if="status === 'complete'"><CircleCheck /></el-icon>
        <el-icon v-if="status === 'error'"><CircleClose /></el-icon>
        <span>{{ message }}</span>
      </div>

      <!-- 结果汇总（完成后显示） -->
      <div v-if="status === 'complete' && results" class="results-summary">
        <el-divider>更新结果</el-divider>
        <div class="summary-stats">
          <span class="success-count">成功: {{ successCount }}</span>
          <span class="failed-count">失败: {{ failedCount }}</span>
        </div>
        <el-collapse v-if="failedCount > 0">
          <el-collapse-item title="查看失败项目" name="failed">
            <div class="failed-list">
              <div
                v-for="(result, key) in failedResults"
                :key="key"
                class="failed-item"
              >
                <span class="item-key">{{ key }}</span>
                <span class="item-error">{{ result.error }}</span>
              </div>
            </div>
          </el-collapse-item>
        </el-collapse>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onUnmounted } from 'vue';
import { Loading, CircleCheck, CircleClose } from '@element-plus/icons-vue';
import { ElMessage } from 'element-plus';

interface ProgressData {
  type: 'progress' | 'complete' | 'error';
  task_id: string;
  total: number;
  completed: number;
  current_symbol?: string;
  current_period?: string;
  status?: 'in_progress' | 'complete' | 'error';
  message?: string;
  results?: Record<string, { success: boolean; count?: number; error?: string }>;
}

const props = defineProps<{
  taskId: string;
  autoClose?: boolean; // 完成后自动关闭（延迟）
}>();

const emit = defineEmits<{
  close: [];
  complete: [results: Record<string, { success: boolean; count?: number; error?: string }>];
}>();

// 状态
const visible = ref(false);
const status = ref<'in_progress' | 'complete' | 'error'>('in_progress');
const total = ref(0);
const completed = ref(0);
const currentSymbol = ref('');
const currentPeriod = ref('');
const message = ref('准备中...');
const results = ref<Record<string, { success: boolean; count?: number; error?: string }> | null>(null);

let ws: WebSocket | null = null;

// 计算属性
const progressPercentage = computed(() => {
  if (total.value === 0) return 0;
  return Math.round((completed.value / total.value) * 100);
});

const progressStatus = computed(() => {
  if (status.value === 'error') return 'exception';
  if (status.value === 'complete') return 'success';
  return undefined;
});

const successCount = computed(() => {
  if (!results.value) return 0;
  return Object.values(results.value).filter(r => r.success).length;
});

const failedCount = computed(() => {
  if (!results.value) return 0;
  return Object.values(results.value).filter(r => !r.success).length;
});

const failedResults = computed(() => {
  if (!results.value) return {};
  return Object.fromEntries(
    Object.entries(results.value).filter(([_, r]) => !r.success)
  );
});

// 连接 WebSocket
const connectWebSocket = () => {
  const wsUrl = `ws://localhost:8000/ws/batch-update/${props.taskId}`;
  ws = new WebSocket(wsUrl);

  ws.onopen = () => {
    console.log('[批量更新] WebSocket 已连接');
    visible.value = true;
  };

  ws.onmessage = (event) => {
    const data: ProgressData = JSON.parse(event.data);
    handleProgress(data);
  };

  ws.onerror = (error) => {
    console.error('[批量更新] WebSocket 错误:', error);
    status.value = 'error';
    message.value = '连接错误';
  };

  ws.onclose = () => {
    console.log('[批量更新] WebSocket 已关闭');
    if (status.value === 'in_progress') {
      status.value = 'error';
      message.value = '连接意外关闭';
    }
  };
};

// 处理进度更新
const handleProgress = (data: ProgressData) => {
  total.value = data.total || 0;
  completed.value = data.completed || 0;

  if (data.current_symbol) currentSymbol.value = data.current_symbol;
  if (data.current_period) currentPeriod.value = data.current_period;

  if (data.message) message.value = data.message;

  if (data.status) {
    status.value = data.status;
  }

  if (data.type === 'complete' && data.results) {
    results.value = data.results;
    emit('complete', data.results);

    // 自动关闭
    if (props.autoClose) {
      setTimeout(() => {
        close();
      }, 3000);
    }
  }

  if (data.type === 'error') {
    status.value = 'error';
    message.value = data.message || '更新失败';
  }
};

// 关闭对话框
const close = () => {
  visible.value = false;

  // 关闭 WebSocket
  if (ws) {
    ws.close();
    ws = null;
  }

  emit('close');
};

// 组件挂载时连接
connectWebSocket();

// 组件卸载时清理
onUnmounted(() => {
  if (ws) {
    ws.close();
    ws = null;
  }
});
</script>

<style scoped>
.batch-update-progress {
  width: 500px;
  max-width: 90vw;
}

.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.progress-header h3 {
  margin: 0;
  font-size: 18px;
  color: #e2e8f0;
}

.progress-content {
  padding: 10px 0;
}

.progress-bar-container {
  margin-bottom: 20px;
}

.progress-text {
  font-size: 14px;
  color: #cbd5e1;
  font-weight: 500;
}

.current-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px;
  background: rgba(139, 92, 246, 0.1);
  border-radius: 8px;
  margin-bottom: 15px;
  color: #cbd5e1;
}

.current-item .is-loading {
  animation: rotate 1s linear infinite;
}

@keyframes rotate {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.current-item strong {
  color: #a78bfa;
  margin: 0 4px;
}

.status-message {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px;
  border-radius: 8px;
  font-size: 14px;
  color: #cbd5e1;
}

.status-message.in_progress {
  background: rgba(59, 130, 246, 0.1);
  color: #93c5fd;
}

.status-message.complete {
  background: rgba(34, 197, 94, 0.1);
  color: #86efac;
}

.status-message.error {
  background: rgba(239, 68, 68, 0.1);
  color: #f87171;
}

.results-summary {
  margin-top: 15px;
}

.summary-stats {
  display: flex;
  gap: 20px;
  padding: 10px;
  background: rgba(30, 30, 60, 0.5);
  border-radius: 8px;
  margin-bottom: 10px;
}

.success-count {
  color: #86efac;
  font-weight: 500;
}

.failed-count {
  color: #f87171;
  font-weight: 500;
}

.failed-list {
  max-height: 200px;
  overflow-y: auto;
}

.failed-item {
  display: flex;
  justify-content: space-between;
  padding: 8px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  font-size: 12px;
}

.failed-item:last-child {
  border-bottom: none;
}

.item-key {
  color: #cbd5e1;
  font-family: monospace;
}

.item-error {
  color: #f87171;
}
</style>

<template>
  <Teleport to="body">
    <transition name="slide-up">
      <div
        v-if="visible"
        class="batch-update-statusbar"
        :class="{ 'minimized': isMinimized }"
      >
        <!-- 迷你模式（进度条 + 图标） -->
        <div v-if="isMinimized" class="minimized-view" @click="expand">
          <div class="mini-progress">
            <el-icon class="is-loading" v-if="status === 'in_progress'"><Loading /></el-icon>
            <el-icon v-else-if="status === 'complete'" class="success-icon"><CircleCheck /></el-icon>
            <el-icon v-else class="error-icon"><CircleClose /></el-icon>

            <div class="mini-bar">
              <div
                class="mini-bar-fill"
                :style="{ width: `${progressPercentage}%` }"
                :class="status"
              ></div>
            </div>

            <span class="mini-text">{{ completed }}/{{ total }}</span>
          </div>
        </div>

        <!-- 完整模式 -->
        <div v-else class="full-view">
          <div class="status-header">
            <div class="status-info">
              <span class="status-title">{{ title }}</span>
              <span class="status-count">{{ completed }}/{{ total }}</span>
            </div>
            <div class="status-actions">
              <el-button
                size="small"
                :icon="Close"
                circle
                @click="close"
              />
            </div>
          </div>

          <!-- 进度条 -->
          <div class="progress-bar">
            <el-progress
              :percentage="progressPercentage"
              :status="progressStatus"
              :stroke-width="8"
              :show-text="false"
            />
          </div>

          <!-- 当前项 -->
          <div v-if="status === 'in_progress'" class="current-item">
            <span>{{ currentSymbol }} {{ currentPeriod }}</span>
          </div>

          <!-- 完成消息 -->
          <div v-if="status === 'complete'" class="complete-message">
            <el-icon><CircleCheck /></el-icon>
            <span>更新完成</span>
          </div>

          <!-- 错误消息 -->
          <div v-if="status === 'error'" class="error-message">
            <el-icon><CircleClose /></el-icon>
            <span>{{ errorMessage }}</span>
          </div>
        </div>
      </div>
    </transition>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, computed, onUnmounted } from 'vue';
import { Loading, CircleCheck, CircleClose, Close } from '@element-plus/icons-vue';

interface ProgressData {
  type: 'progress' | 'complete' | 'error';
  total: number;
  completed: number;
  current_symbol?: string;
  current_period?: string;
  status?: 'in_progress' | 'complete' | 'error';
  message?: string;
}

const props = defineProps<{
  taskId: string;
  autoClose?: boolean;
  autoMinimize?: boolean; // 完成后自动最小化
}>();

const emit = defineEmits<{
  close: [];
  complete: [results: any];
}>();

// 状态
const visible = ref(true);
const isMinimized = ref(false);
const status = ref<'in_progress' | 'complete' | 'error'>('in_progress');
const total = ref(0);
const completed = ref(0);
const currentSymbol = ref('');
const currentPeriod = ref('');
const errorMessage = ref('');

let ws: WebSocket | null = null;

// 计算属性
const title = computed(() => {
  switch (status.value) {
    case 'in_progress': return '批量更新中...';
    case 'complete': return '更新完成';
    case 'error': return '更新失败';
    default: return '批量更新';
  }
});

const progressPercentage = computed(() => {
  if (total.value === 0) return 0;
  return Math.round((completed.value / total.value) * 100);
});

const progressStatus = computed(() => {
  if (status.value === 'error') return 'exception';
  if (status.value === 'complete') return 'success';
  return undefined;
});

// WebSocket 连接
const connectWebSocket = () => {
  const wsUrl = `ws://localhost:8000/ws/batch-update/${props.taskId}`;
  ws = new WebSocket(wsUrl);

  ws.onmessage = (event) => {
    const data: ProgressData = JSON.parse(event.data);
    handleProgress(data);
  };

  ws.onerror = () => {
    status.value = 'error';
    errorMessage.value = '连接错误';
  };

  ws.onclose = () => {
    if (status.value === 'in_progress') {
      status.value = 'error';
      errorMessage.value = '连接意外关闭';
    }
  };
};

// 处理进度更新
const handleProgress = (data: ProgressData) => {
  total.value = data.total || 0;
  completed.value = data.completed || 0;

  if (data.current_symbol) currentSymbol.value = data.current_symbol;
  if (data.current_period) currentPeriod.value = data.current_period;

  if (data.type === 'complete') {
    status.value = 'complete';
    emit('complete', data.results);

    // 自动最小化
    if (props.autoMinimize) {
      setTimeout(() => {
        isMinimized.value = true;
      }, 2000);
    }

    // 自动关闭
    if (props.autoClose) {
      setTimeout(() => {
        close();
      }, 5000);
    }
  }

  if (data.type === 'error') {
    status.value = 'error';
    errorMessage.value = data.message || '更新失败';
  }
};

// 展开
const expand = () => {
  isMinimized.value = false;
};

// 关闭
const close = () => {
  visible.value = false;
  if (ws) {
    ws.close();
    ws = null;
  }
  emit('close');
};

// 连接 WebSocket
connectWebSocket();

// 清理
onUnmounted(() => {
  if (ws) {
    ws.close();
  }
});
</script>

<style scoped>
.batch-update-statusbar {
  position: fixed;
  bottom: 20px;
  right: 20px;
  z-index: 9999;
  background: rgba(30, 30, 46, 0.95);
  border: 1px solid rgba(139, 92, 246, 0.3);
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(10px);
}

.batch-update-statusbar.minimized {
  padding: 10px 15px;
}

.batch-update-statusbar:not(.minimized) {
  width: 320px;
  padding: 15px;
}

/* 迷你模式 */
.minimized-view {
  cursor: pointer;
  transition: all 0.3s;
}

.minimized-view:hover {
  transform: scale(1.02);
}

.mini-progress {
  display: flex;
  align-items: center;
  gap: 10px;
}

.mini-progress .is-loading {
  color: #8b5cf6;
  animation: rotate 1s linear infinite;
  font-size: 16px;
}

.mini-progress .success-icon {
  color: #22c55e;
  font-size: 16px;
}

.mini-progress .error-icon {
  color: #ef4444;
  font-size: 16px;
}

.mini-bar {
  width: 80px;
  height: 6px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 3px;
  overflow: hidden;
}

.mini-bar-fill {
  height: 100%;
  transition: width 0.3s ease, background-color 0.3s ease;
}

.mini-bar-fill.in_progress {
  background: linear-gradient(90deg, #8b5cf6, #6366f1);
}

.mini-bar-fill.complete {
  background: #22c55e;
}

.mini-bar-fill.error {
  background: #ef4444;
}

.mini-text {
  color: #cbd5e1;
  font-size: 12px;
  font-weight: 500;
  white-space: nowrap;
}

/* 完整模式 */
.full-view .status-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.status-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.status-title {
  color: #e2e8f0;
  font-size: 14px;
  font-weight: 500;
}

.status-count {
  color: #94a3b8;
  font-size: 12px;
}

.progress-bar {
  margin-bottom: 10px;
}

.current-item {
  color: #a78bfa;
  font-size: 13px;
  margin-bottom: 8px;
}

.complete-message,
.error-message {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  padding: 8px;
  border-radius: 6px;
}

.complete-message {
  background: rgba(34, 197, 94, 0.1);
  color: #86efac;
}

.error-message {
  background: rgba(239, 68, 68, 0.1);
  color: #f87171;
}

/* 动画 */
.slide-up-enter-active,
.slide-up-leave-active {
  transition: all 0.3s ease;
}

.slide-up-enter-from,
.slide-up-leave-to {
  opacity: 0;
  transform: translateY(20px);
}

@keyframes rotate {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
</style>

<template>
  <div v-if="showProgress" class="data-update-progress">
    <div class="progress-info">
      <i class="fas fa-sync fa-spin"></i>
      <span class="update-text">{{ updateText }}</span>
      <span class="update-percent">{{ progress }}%</span>
    </div>
    <div class="progress-bar-container">
      <div class="progress-bar" :style="{ width: progress + '%' }"></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { dataUpdateProgress, type UpdateTask } from '@/services/dataUpdateProgress'

const currentTask = ref<UpdateTask | null>(null)

// 订阅服务更新
let unsubscribe: (() => void) | null = null

onMounted(() => {
  unsubscribe = dataUpdateProgress.subscribe((task) => {
    currentTask.value = task
  })
})

onUnmounted(() => {
  if (unsubscribe) {
    unsubscribe()
  }
})

// 计算属性
const showProgress = computed(() => currentTask.value !== null)

const updateText = computed(() => {
  if (!currentTask.value) return ''

  const { symbol, period, status, message } = currentTask.value

  if (message) return message

  if (status === 'downloading') {
    return `正在下载 ${symbol} ${period} 数据...`
  } else if (status === 'processing') {
    return `正在处理 ${symbol} ${period} 数据...`
  } else if (status === 'completed') {
    return `${symbol} ${period} 数据更新完成`
  } else if (status === 'failed') {
    return `${symbol} ${period} 数据更新失败`
  }

  return '数据更新中...'
})

const progress = computed(() => {
  return currentTask.value ? Math.round(currentTask.value.progress) : 0
})
</script>

<style lang="scss" scoped>
.data-update-progress {
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 200px;
  max-width: 300px;

  .progress-info {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 12px;
    color: var(--text-secondary);

    i {
      color: var(--primary);
      font-size: 10px;
    }

    .update-text {
      flex: 1;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }

    .update-percent {
      font-weight: 600;
      color: var(--primary);
    }
  }

  .progress-bar-container {
    height: 3px;
    background: rgba(255, 255, 255, 0.1);
    border-radius: 2px;
    overflow: hidden;

    .progress-bar {
      height: 100%;
      background: linear-gradient(90deg, var(--primary), var(--success));
      border-radius: 2px;
      transition: width 0.3s ease;
      position: relative;

      &::after {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
        animation: shimmer 1.5s infinite;
      }
    }
  }
}

@keyframes shimmer {
  0% {
    transform: translateX(-100%);
  }
  100% {
    transform: translateX(100%);
  }
}
</style>

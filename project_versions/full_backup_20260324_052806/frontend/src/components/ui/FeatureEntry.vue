<template>
  <div class="feature-entry" @click="handleClick">
    <div class="feature-entry-icon" :style="iconStyle">
      <span>{{ icon }}</span>
    </div>
    <div class="feature-entry-content">
      <div class="feature-entry-title">{{ title }}</div>
      <!-- 大数字显示 -->
      <div v-if="stage" class="feature-entry-count">{{ stage }}</div>
      <!-- 状态信息 -->
      <div v-if="statusText" class="feature-entry-status">
        {{ statusText }}
      </div>
    </div>
    <div class="feature-entry-arrow">→</div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  icon: string
  title: string
  description?: string
  color?: string
  to?: string
  stage?: number | string
  statusText?: string
}

const props = withDefaults(defineProps<Props>(), {
  color: '#2962ff'
})

const emit = defineEmits<{
  click: [event: MouseEvent]
}>()

// 图标样式
const iconStyle = computed(() => ({
  color: props.color
}))

const handleClick = (event: MouseEvent) => {
  emit('click', event)
}
</script>

<style lang="scss" scoped>
.feature-entry {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px 24px;
  cursor: pointer;
  transition: all 0.3s ease;
  border-radius: 10px;

  &:hover {
    .feature-entry-icon {
      animation: bounce 0.5s ease infinite;
    }

    .feature-entry-arrow {
      transform: translateX(4px);
    }
  }
}

@keyframes bounce {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-4px);
  }
}

.feature-entry-icon {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32px;
}

.feature-entry-content {
  flex: 1;
  line-height: 1.2;
}

.feature-entry-title {
  font-size: 14px;
  font-weight: 500;
  color: #d1d4dc !important;
}

.feature-entry-count {
  font-size: 28px;
  font-weight: 700;
  color: #d1d4dc !important;
  margin-top: -4px;
}

.feature-entry-status {
  margin-top: -2px;
  font-size: 12px;
  color: #787b86;
}

.feature-entry-arrow {
  color: #787b86;
  font-size: 18px;
  transition: all 0.3s ease;
}
</style>

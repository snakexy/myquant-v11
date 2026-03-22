<template>
  <div
    class="function-card"
    :class="{ 'function-card--active': isActive, [`function-card--${status}`]: true }"
    @click="handleClick"
    @mouseenter="isHovered = true"
    @mouseleave="isHovered = false"
  >
    <!-- 背景粒子效果 -->
    <div class="function-card__particles" ref="particlesContainer"></div>
    
    <!-- 数据流线条 -->
    <svg class="function-card__dataflow" viewBox="0 0 400 200">
      <defs>
        <linearGradient id="dataflow-gradient" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" style="stop-color:#00ff88;stop-opacity:0" />
          <stop offset="50%" style="stop-color:#00ff88;stop-opacity:1" />
          <stop offset="100%" style="stop-color:#00ff88;stop-opacity:0" />
        </linearGradient>
      </defs>
      <path
        v-for="(path, index) in dataflowPaths"
        :key="index"
        :d="path"
        stroke="url(#dataflow-gradient)"
        stroke-width="2"
        fill="none"
        class="dataflow-path"
      />
    </svg>
    
    <!-- 核心内容区域 -->
    <div class="function-card__core">
      <!-- 左侧图标区域 -->
      <div class="function-card__icon-container">
        <div class="function-card__icon-bg" :class="`function-card__icon-bg--${iconTheme}`">
          <component :is="iconComponent" :size="40" class="function-card__icon" />
        </div>
        <div class="function-card__pulse-ring"></div>
      </div>
      
      <!-- 中间信息区域 -->
      <div class="function-card__content">
        <h3 class="function-card__title">
          <span class="function-card__title-text">{{ title }}</span>
          <div class="function-card__title-glow"></div>
        </h3>
        <p class="function-card__description">{{ description }}</p>
        
        <!-- 状态指示器 -->
        <div class="function-card__status">
          <div class="function-card__status-indicator" :class="`function-card__status-indicator--${status}`">
            <div class="function-card__status-core"></div>
            <div class="function-card__status-wave"></div>
          </div>
          <span class="function-card__status-text">{{ getStatusText(status) }}</span>
        </div>
        
        <!-- 性能指标 -->
        <div class="function-card__metrics" v-if="metrics">
          <div
            v-for="(metric, index) in metrics"
            :key="index"
            class="function-card__metric"
          >
            <span class="function-card__metric-value">{{ metric.value }}</span>
            <span class="function-card__metric-label">{{ metric.label }}</span>
          </div>
        </div>
      </div>
      
      <!-- 右侧导航区域 -->
      <div class="function-card__navigation">
        <div class="function-card__layer-indicator">
          <div class="function-card__layer-dot" v-for="i in 4" :key="i" :class="{ 'function-card__layer-dot--active': i === 1 }"></div>
        </div>
        <div class="function-card__enter-text">进入</div>
        <div class="function-card__arrow-container">
          <ChevronForwardOutline class="function-card__arrow" />
        </div>
      </div>
    </div>
    
    <!-- 底部科技线条 -->
    <div class="function-card__tech-lines">
      <div class="function-card__tech-line" v-for="i in 3" :key="i" :style="{ animationDelay: `${i * 0.2}s` }"></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from 'vue'
import {
  ServerOutline,
  SearchOutline,
  FlaskOutline,
  AccessibilityOutline,
  DesktopOutline,
  SettingsOutline,
  TrendingUpOutline,
  BarChartOutline,
  AlertCircleOutline,
  BugOutline,
  EyeOutline,
  ChevronForwardOutline
} from '@vicons/ionicons5'

interface Props {
  id: string
  title: string
  description: string
  icon: string
  status?: 'online' | 'offline' | 'warning' | 'error'
  isActive?: boolean
  metrics?: Array<{ label: string; value: string }>
}

const props = withDefaults(defineProps<Props>(), {
  status: 'offline',
  isActive: false
})

const emit = defineEmits<{
  click: [id: string]
}>()

const isHovered = ref(false)
const particlesContainer = ref<HTMLElement>()

// 图标映射和主题
const iconMap: Record<string, any> = {
  database: ServerOutline,
  search: SearchOutline,
  experiment: FlaskOutline,
  robot: AccessibilityOutline,
  monitor: DesktopOutline,
  setting: SettingsOutline,
  trading: TrendingUpOutline,
  chart: BarChartOutline,
  alert: AlertCircleOutline,
  bug: BugOutline,
  eye: EyeOutline
}

const iconThemeMap: Record<string, string> = {
  database: 'blue',
  search: 'green',
  experiment: 'purple',
  robot: 'orange',
  monitor: 'cyan',
  setting: 'gray',
  trading: 'red',
  chart: 'yellow',
  alert: 'pink',
  bug: 'indigo',
  eye: 'teal'
}

const iconComponent = computed(() => iconMap[props.icon] || DatabaseOutlined)
const iconTheme = computed(() => iconThemeMap[props.icon] || 'blue')

// 数据流路径
const dataflowPaths = computed(() => [
  'M10,100 Q100,50 200,100 T390,100',
  'M10,120 Q150,80 250,120 T390,120',
  'M10,140 Q200,100 300,140 T390,140'
])

const handleClick = () => {
  emit('click', props.id)
}

const getStatusText = (status: string) => {
  const statusMap: Record<string, string> = {
    online: '系统运行中',
    offline: '系统离线',
    warning: '性能警告',
    error: '系统错误'
  }
  return statusMap[status] || '未知状态'
}

// 创建粒子效果
onMounted(() => {
  nextTick(() => {
    if (particlesContainer.value) {
      createParticles()
    }
  })
})

const createParticles = () => {
  if (!particlesContainer.value) return
  
  const particleCount = 20
  for (let i = 0; i < particleCount; i++) {
    const particle = document.createElement('div')
    particle.className = 'function-card__particle'
    particle.style.left = `${Math.random() * 100}%`
    particle.style.top = `${Math.random() * 100}%`
    particle.style.animationDelay = `${Math.random() * 5}s`
    particle.style.animationDuration = `${3 + Math.random() * 4}s`
    particlesContainer.value.appendChild(particle)
  }
}
</script>

<style lang="scss" scoped>
.function-card {
  position: relative;
  display: flex;
  align-items: center;
  min-height: 180px;
  padding: 0;
  background: linear-gradient(135deg, rgba(10, 10, 15, 0.9), rgba(26, 26, 46, 0.9));
  border: 1px solid rgba(37, 99, 235, 0.2);
  border-radius: 16px;
  cursor: pointer;
  overflow: hidden;
  backdrop-filter: blur(10px);
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);

  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(0, 255, 136, 0.1), transparent);
    transition: left 0.6s ease;
  }

  &:hover {
    transform: translateY(-4px) scale(1.02);
    border-color: rgba(37, 99, 235, 0.6);
    box-shadow:
      0 20px 40px rgba(0, 0, 0, 0.3),
      0 0 60px rgba(37, 99, 235, 0.2),
      inset 0 0 20px rgba(37, 99, 235, 0.1);

    &::before {
      left: 100%;
    }

    .function-card__arrow {
      transform: translateX(8px) rotate(-45deg);
      color: #00ff88;
    }

    .function-card__icon-bg {
      transform: scale(1.1) rotate(5deg);
      box-shadow: 0 0 30px currentColor;
    }

    .function-card__title-glow {
      opacity: 1;
      transform: scaleX(1);
    }

    .function-card__dataflow {
      opacity: 1;
    }
  }

  &--active {
    border-color: rgba(0, 255, 136, 0.6);
    background: linear-gradient(135deg, rgba(0, 255, 136, 0.1), rgba(37, 99, 235, 0.1));
  }

  &--online {
    border-color: rgba(16, 185, 129, 0.4);
  }

  &--warning {
    border-color: rgba(245, 158, 11, 0.4);
  }

  &--error {
    border-color: rgba(239, 68, 68, 0.4);
  }

  &__particles {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    pointer-events: none;
    opacity: 0.3;
  }

  &__particle {
    position: absolute;
    width: 2px;
    height: 2px;
    background: #00ff88;
    border-radius: 50%;
    animation: float-particle 8s infinite linear;
  }

  &__dataflow {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    opacity: 0;
    transition: opacity 0.4s ease;
    pointer-events: none;

    .dataflow-path {
      stroke-dasharray: 10, 5;
      animation: dataflow-move 3s linear infinite;
    }
  }

  &__core {
    position: relative;
    display: flex;
    align-items: center;
    width: 100%;
    padding: 24px;
    z-index: 2;
  }

  &__icon-container {
    position: relative;
    margin-right: 24px;
  }

  &__icon-bg {
    position: relative;
    display: flex;
    align-items: center;
    justify-content: center;
    width: 80px;
    height: 80px;
    border-radius: 20px;
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);

    &--blue {
      background: linear-gradient(135deg, rgba(37, 99, 235, 0.2), rgba(37, 99, 235, 0.1));
      border: 1px solid rgba(37, 99, 235, 0.3);
      color: #2563eb;
    }

    &--green {
      background: linear-gradient(135deg, rgba(16, 185, 129, 0.2), rgba(16, 185, 129, 0.1));
      border: 1px solid rgba(16, 185, 129, 0.3);
      color: var(--market-rise);
    }

    &--purple {
      background: linear-gradient(135deg, rgba(124, 58, 237, 0.2), rgba(124, 58, 237, 0.1));
      border: 1px solid rgba(124, 58, 237, 0.3);
      color: #7c3aed;
    }

    &--orange {
      background: linear-gradient(135deg, rgba(245, 158, 11, 0.2), rgba(245, 158, 11, 0.1));
      border: 1px solid rgba(245, 158, 11, 0.3);
      color: #f59e0b;
    }
  }

  &__pulse-ring {
    position: absolute;
    top: 50%;
    left: 50%;
    width: 100px;
    height: 100px;
    border: 2px solid currentColor;
    border-radius: 50%;
    transform: translate(-50%, -50%);
    opacity: 0;
    animation: pulse-ring 2s ease-out infinite;
  }

  &__content {
    flex: 1;
    min-width: 0;
  }

  &__title {
    position: relative;
    font-size: 20px;
    font-weight: 700;
    color: #f8fafc;
    margin: 0 0 8px 0;
    letter-spacing: 0.5px;
  }

  &__title-glow {
    position: absolute;
    bottom: -2px;
    left: 0;
    width: 100%;
    height: 2px;
    background: linear-gradient(90deg, #00ff88, #2563eb, #7c3aed);
    opacity: 0;
    transform: scaleX(0);
    transition: all 0.4s ease;
  }

  &__description {
    font-size: 14px;
    color: #94a3b8;
    line-height: 1.6;
    margin: 0 0 16px 0;
  }

  &__status {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 12px;
  }

  &__status-indicator {
    position: relative;
    width: 12px;
    height: 12px;
    border-radius: 50%;

    &--online {
      background: var(--market-rise);
    }

    &--offline {
      background: #64748b;
    }

    &--warning {
      background: #f59e0b;
    }

    &--error {
      background: var(--market-fall);
    }
  }

  &__status-core {
    width: 100%;
    height: 100%;
    border-radius: 50%;
    animation: status-pulse 2s ease-in-out infinite;
  }

  &__status-wave {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    border-radius: 50%;
    border: 2px solid currentColor;
    animation: status-wave 2s ease-out infinite;
  }

  &__status-text {
    font-size: 12px;
    color: #94a3b8;
    font-weight: 500;
  }

  &__metrics {
    display: flex;
    gap: 16px;
  }

  &__metric {
    display: flex;
    flex-direction: column;
    gap: 2px;
  }

  &__metric-value {
    font-size: 16px;
    font-weight: 700;
    color: #00ff88;
  }

  &__metric-label {
    font-size: 11px;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  &__navigation {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 8px;
    margin-left: 16px;
  }

  &__layer-indicator {
    display: flex;
    flex-direction: column;
    gap: 4px;
  }

  &__layer-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: #1e293b;
    border: 1px solid #334155;
    transition: all 0.3s ease;

    &--active {
      background: #00ff88;
      border-color: #00ff88;
      box-shadow: 0 0 8px rgba(0, 255, 136, 0.6);
    }
  }

  &__enter-text {
    font-size: 11px;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 1px;
    writing-mode: vertical-rl;
  }

  &__arrow-container {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 32px;
    height: 32px;
    border-radius: 50%;
    background: rgba(37, 99, 235, 0.1);
    border: 1px solid rgba(37, 99, 235, 0.3);
  }

  &__arrow {
    color: #64748b;
    transition: all 0.3s ease;
  }

  &__tech-lines {
    position: absolute;
    bottom: 0;
    left: 0;
    width: 100%;
    height: 3px;
    display: flex;
    overflow: hidden;
  }

  &__tech-line {
    flex: 1;
    height: 100%;
    background: linear-gradient(90deg, transparent, #00ff88, transparent);
    animation: tech-line-scan 3s ease-in-out infinite;
  }
}

// 动画定义
@keyframes float-particle {
  0% {
    transform: translateY(0) translateX(0);
    opacity: 0;
  }
  10% {
    opacity: 1;
  }
  90% {
    opacity: 1;
  }
  100% {
    transform: translateY(-100px) translateX(50px);
    opacity: 0;
  }
}

@keyframes dataflow-move {
  0% {
    stroke-dashoffset: 0;
  }
  100% {
    stroke-dashoffset: -30;
  }
}

@keyframes pulse-ring {
  0% {
    transform: translate(-50%, -50%) scale(1);
    opacity: 0.8;
  }
  100% {
    transform: translate(-50%, -50%) scale(1.5);
    opacity: 0;
  }
}

@keyframes status-pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.6;
  }
}

@keyframes status-wave {
  0% {
    transform: scale(1);
    opacity: 0.8;
  }
  100% {
    transform: scale(2);
    opacity: 0;
  }
}

@keyframes tech-line-scan {
  0%, 100% {
    transform: translateX(-100%);
  }
  50% {
    transform: translateX(100%);
  }
}

// 响应式设计
@media (max-width: 768px) {
  .function-card {
    min-height: 160px;
    
    &__core {
      flex-direction: column;
      text-align: center;
      padding: 20px;
    }
    
    &__icon-container {
      margin-right: 0;
      margin-bottom: 16px;
    }
    
    &__navigation {
      margin-left: 0;
      margin-top: 16px;
      flex-direction: row;
    }
    
    &__enter-text {
      writing-mode: horizontal-tb;
    }
  }
}
</style>
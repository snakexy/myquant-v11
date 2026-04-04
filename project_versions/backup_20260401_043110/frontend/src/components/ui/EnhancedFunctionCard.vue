<template>
  <div 
    class="enhanced-function-card"
    :class="[`card-${card.id}`, { 'is-hovered': isHovered }]"
    @mouseenter="isHovered = true"
    @mouseleave="isHovered = false"
    @click="handleClick"
  >
    <!-- 卡片背景层 -->
    <div class="card-background">
      <div class="glass-morphism"></div>
      <div class="neon-border"></div>
    </div>
    
    <!-- 卡片内容 -->
    <div class="card-content">
      <!-- 图标区域 -->
      <div class="icon-container">
        <div class="icon-glow">{{ card.icon }}</div>
      </div>
      
      <!-- 文字区域 -->
      <div class="text-content">
        <h3 class="card-title">{{ card.title }}</h3>
        <p class="card-description">{{ card.description }}</p>
      </div>
      
    </div>
    
    <!-- 粒子效果 -->
    <div class="particle-container" ref="particleContainer"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick } from 'vue'

// 定义卡片接口
interface FunctionCard {
  id: string
  icon: string
  title: string
  description: string
  color: string
  features: string[]
  panelComponent: string
}

// Props定义
interface Props {
  card: FunctionCard
}

const props = defineProps<Props>()

// Emits定义
interface Emits {
  (e: 'click', cardId: string): void
}

const emit = defineEmits<Emits>()

// 响应式数据
const isHovered = ref(false)
const particleContainer = ref<HTMLElement>()

// 点击处理
const handleClick = () => {
  emit('click', props.card.id)
}

// 粒子效果
let particleInterval: NodeJS.Timeout | null = null

const createParticle = () => {
  if (!particleContainer.value || !isHovered.value) return
  
  const particle = document.createElement('div')
  particle.className = 'particle'
  particle.style.left = Math.random() * 100 + '%'
  particle.style.animationDelay = Math.random() * 2 + 's'
  particle.style.animationDuration = (Math.random() * 3 + 2) + 's'
  
  particleContainer.value.appendChild(particle)
  
  // 移除过期粒子
  setTimeout(() => {
    if (particle.parentNode) {
      particle.parentNode.removeChild(particle)
    }
  }, 5000)
}

onMounted(() => {
  nextTick(() => {
    // 启动粒子效果
    particleInterval = setInterval(() => {
      if (isHovered.value) {
        createParticle()
      }
    }, 300)
  })
})

onUnmounted(() => {
  if (particleInterval) {
    clearInterval(particleInterval)
  }
})
</script>

<style lang="scss" scoped>
@use '@/assets/styles/variables.scss' as *;
.enhanced-function-card {
  position: relative;
  width: 100%;
  height: 280px;
  cursor: pointer;
  border-radius: var(--radius-xl);
  overflow: hidden;
  transition: all var(--transition-normal);
  
  // 卡片背景层
  .card-background {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    z-index: 1;
    
    .glass-morphism {
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: var(--glass-bg);
      backdrop-filter: blur(var(--glass-blur));
      -webkit-backdrop-filter: blur(var(--glass-blur));
      border: 1px solid var(--glass-border);
      border-radius: var(--radius-xl);
      transition: all var(--transition-normal);
    }
    
    .neon-border {
      position: absolute;
      top: -2px;
      left: -2px;
      right: -2px;
      bottom: -2px;
      border-radius: var(--radius-xl);
      opacity: 0;
      transition: opacity var(--transition-normal);
      z-index: -1;
    }
  }
  
  // 卡片内容
  .card-content {
    position: relative;
    z-index: 2;
    height: 100%;
    padding: var(--spacing-xl);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    
    .icon-container {
      margin-bottom: var(--spacing-lg);
      
      .icon-glow {
        font-size: 64px;
        line-height: 1;
        filter: drop-shadow(0 0 10px currentColor);
        transition: all var(--transition-normal);
      }
    }
    
    .text-content {
      .card-title {
        font-size: var(--font-size-xl);
        font-weight: 600;
        margin-bottom: var(--spacing-sm);
        color: var(--text-primary);
        transition: all var(--transition-normal);
      }
      
      .card-description {
        font-size: var(--font-size-sm);
        color: var(--text-secondary);
        line-height: 1.5;
        transition: all var(--transition-normal);
      }
    }
    
  }
  
  // 粒子容器
  .particle-container {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    pointer-events: none;
    z-index: 3;
    overflow: hidden;
    border-radius: var(--radius-xl);
  }
  
  // 悬停效果
  &:hover {
    transform: translateY(-8px) scale(1.02);
    
    .card-background {
      .glass-morphism {
        background: rgba(255, 255, 255, 0.08);
        border-color: var(--glass-border);
      }
      
      .neon-border {
        opacity: 1;
      }
    }
    
    .card-content {
      .icon-container .icon-glow {
        transform: scale(1.1);
        filter: drop-shadow(0 0 20px currentColor);
      }
      
      .features-hint {
        opacity: 1;
        transform: translateY(0);
      }
    }
  }
  
  // 点击效果
  &:active {
    transform: translateY(-6px) scale(1.01);
  }
}

// 卡片特定颜色
.card-data-management {
  color: var(--data-management);
  
  .neon-border {
    background: linear-gradient(45deg, 
      var(--data-management), 
      transparent, 
      var(--data-management));
    filter: drop-shadow(0 0 10px var(--data-management));
  }
}

.card-backtest {
  color: var(--backtest);
  
  .neon-border {
    background: linear-gradient(45deg, 
      var(--backtest), 
      transparent, 
      var(--backtest));
    filter: drop-shadow(0 0 10px var(--backtest));
  }
}

.card-strategy {
  color: var(--strategy);
  
  .neon-border {
    background: linear-gradient(45deg, 
      var(--strategy), 
      transparent, 
      var(--strategy));
    filter: drop-shadow(0 0 10px var(--strategy));
  }
}

.card-trading {
  color: var(--trading);
  
  .neon-border {
    background: linear-gradient(45deg, 
      var(--trading), 
      transparent, 
      var(--trading));
    filter: drop-shadow(0 0 10px var(--trading));
  }
}

.card-monitoring {
  color: var(--monitoring);
  
  .neon-border {
    background: linear-gradient(45deg, 
      var(--monitoring), 
      transparent, 
      var(--monitoring));
    filter: drop-shadow(0 0 10px var(--monitoring));
  }
}

.card-model-management {
  color: var(--model-management);
  
  .neon-border {
    background: linear-gradient(45deg, 
      var(--model-management), 
      transparent, 
      var(--model-management));
    filter: drop-shadow(0 0 10px var(--model-management));
  }
}

// 粒子效果
.particle {
  position: absolute;
  width: 4px;
  height: 4px;
  background: currentColor;
  border-radius: 50%;
  opacity: 0.8;
  animation: float-up linear infinite;
  filter: blur(1px);
}

@keyframes float-up {
  0% {
    transform: translateY(100vh) scale(0);
    opacity: 0;
  }
  10% {
    opacity: 0.8;
  }
  90% {
    opacity: 0.8;
  }
  100% {
    transform: translateY(-100px) scale(1);
    opacity: 0;
  }
}

// 响应式设计
@media (max-width: 768px) {
  .enhanced-function-card {
    height: 220px;
    
    .card-content {
      padding: var(--spacing-lg);
      
      .icon-container .icon-glow {
        font-size: 48px;
      }
      
      .text-content {
        .card-title {
          font-size: var(--font-size-lg);
        }
        
        .card-description {
          font-size: var(--font-size-xs);
        }
      }
      
    }
  }
}
</style>
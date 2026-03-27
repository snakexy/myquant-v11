<template>
  <div
    ref="containerRef"
    class="lazy-chart"
    :style="{ height: height, width: width }"
  >
    <!-- 加载占位符 -->
    <div v-if="!isVisible" class="loading-placeholder">
      <el-icon class="is-loading" :size="32">
        <loading />
      </el-icon>
      <p>加载中...</p>
    </div>

    <!-- 实际图表 -->
    <component
      v-if="isVisible"
      :is="chartComponent"
      v-bind="$attrs"
      @ready="onChartReady"
    />

    <!-- 错误状态 -->
    <div v-if="error" class="error-state">
      <el-icon :size="32"><warning /></el-icon>
      <p>{{ error }}</p>
      <el-button size="small" @click="retry">重试</el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, defineAsyncComponent, watch } from 'vue'
import { Loading, Warning } from '@element-plus/icons-vue'

interface Props {
  chartType: string
  height?: string
  width?: string
  rootMargin?: string
}

const props = withDefaults(defineProps<Props>(), {
  height: '400px',
  width: '100%',
  rootMargin: '50px'
})

const emit = defineEmits(['ready', 'error'])

const containerRef = ref<HTMLElement>()
const isVisible = ref(false)
const error = ref<string>('')
const isLoaded = ref(false)

// Intersection Observer
let observer: IntersectionObserver | null = null

// 动态导入图表组件
const chartComponent = ref<any>(null)

// 加载图表组件
const loadChartComponent = async () => {
  try {
    isLoaded.value = true

    // 根据chartType动态导入组件
    switch (props.chartType) {
      case 'kline-advanced':
      case 'kline-realtime':
      case 'kline':
        // 所有K线图类型都使用统一的TradingViewKLineUnified组件
        chartComponent.value = defineAsyncComponent(() =>
          import('@/components/charts/TradingViewKLineUnified.vue')
        )
        break
      case 'sector-heatmap':
        chartComponent.value = defineAsyncComponent(() =>
          import('@/components/charts/SectorHeatmap.vue')
        )
        break
      case 'rotation-chart':
        chartComponent.value = defineAsyncComponent(() =>
          import('@/components/charts/RotationChart.vue')
        )
        break
      default:
        throw new Error(`Unknown chart type: ${props.chartType}`)
    }

    emit('ready')
  } catch (e: any) {
    error.value = e.message || '加载图表失败'
    emit('error', e)
  }
}

// 重试加载
const retry = () => {
  error.value = ''
  isLoaded.value = false
  isVisible.value = false
  initObserver()
}

// 图表准备就绪
const onChartReady = () => {
  emit('ready')
}

// 初始化Intersection Observer
const initObserver = () => {
  if (!containerRef.value) return

  // 清理旧的observer
  if (observer) {
    observer.disconnect()
  }

  // 创建新的observer
  observer = new IntersectionObserver(
    (entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting && !isLoaded.value) {
          isVisible.value = true
          loadChartComponent()

          // 停止观察
          if (observer) {
            observer.disconnect()
            observer = null
          }
        }
      })
    },
    {
      rootMargin: props.rootMargin,
      threshold: 0.1  // 10%可见时触发
    }
  )

  observer.observe(containerRef.value)
}

// 生命周期
onMounted(() => {
  initObserver()
})

onUnmounted(() => {
  if (observer) {
    observer.disconnect()
    observer = null
  }
})

// 监听chartType变化
watch(() => props.chartType, () => {
  // 重置状态
  isVisible.value = false
  isLoaded.value = false
  error.value = ''
  chartComponent.value = null

  // 重新初始化
  initObserver()
})
</script>

<style scoped lang="scss">
.lazy-chart {
  position: relative;
  background: #1a1a2e;
  border-radius: 8px;
  overflow: hidden;

  .loading-placeholder,
  .error-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100%;
    min-height: 200px;
    color: #94a3b8;

    .el-icon {
      margin-bottom: 12px;
      color: #8b5cf6;
    }

    p {
      margin: 0;
      font-size: 14px;
    }
  }

  .error-state {
    .el-icon {
      color: #ef4444;
    }

    .el-button {
      margin-top: 12px;
    }
  }
}
</style>

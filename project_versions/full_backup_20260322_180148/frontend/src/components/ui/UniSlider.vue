<template>
  <div class="uni-slider" :class="[size, variant, { disabled: disabled }]">
    <!-- 标签 -->
    <div v-if="label || unit" class="slider-label">
      <span class="label-title">{{ label }}</span>
      <span v-if="unit" class="label-unit">{{ unit }}</span>
    </div>

    <!-- 滑杆容器 -->
    <div class="slider-container">
      <!-- 滑杆轨道 -->
      <div
        class="slider-track"
        @click="handleTrackClick"
        ref="trackRef"
      >
        <!-- 已选择的进度 -->
        <div
          class="slider-fill"
          :style="{ width: fillWidth }"
        ></div>

        <!-- 刻度标记 -->
        <div v-if="marks && marks.length > 0" class="slider-marks">
          <div
            v-for="mark in marks"
            :key="mark.value"
            class="slider-mark"
            :class="{ active: modelValue >= mark.value }"
            :style="{ left: `${getMarkPosition(mark.value)}%` }"
          ></div>
        </div>

        <!-- 滑杆按钮 -->
        <div
          class="slider-thumb"
          :class="{ active: isDragging }"
          :style="{ left: fillWidth }"
          @mousedown="handleMouseDown"
          @touchstart="handleTouchStart"
          ref="thumbRef"
        >
          <!-- 提示信息 -->
          <div
            class="slider-tooltip"
            :class="{ visible: showTooltip }"
          >
            {{ formatValue(modelValue) }}
          </div>
        </div>
      </div>

      <!-- 数值显示 -->
      <div v-if="showValue" class="slider-value">
        <input
          v-if="editable"
          type="number"
          :value="modelValue"
          :min="min"
          :max="max"
          :step="step"
          @input="handleInput"
          @change="handleChange"
        />
        <span v-else>{{ formatValue(modelValue) }}</span>
      </div>
    </div>

    <!-- 范围标签 -->
    <div v-if="showRangeLabels" class="slider-range-labels">
      <span class="range-label min">{{ formatValue(min) }}</span>
      <span class="range-label max">{{ formatValue(max) }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'

interface Mark {
  value: number
  label?: string
}

interface Props {
  modelValue: number
  min?: number
  max?: number
  step?: number
  label?: string
  unit?: string
  disabled?: boolean
  size?: 'small' | 'default' | 'large'
  variant?: 'default' | 'success' | 'warning' | 'danger' | 'market-rise' | 'market-fall'
  showValue?: boolean
  editable?: boolean
  showTooltip?: boolean
  showRangeLabels?: boolean
  marks?: Mark[]
  format?: (value: number) => string
}

const props = withDefaults(defineProps<Props>(), {
  min: 0,
  max: 100,
  step: 1,
  disabled: false,
  size: 'default',
  variant: 'default',
  showValue: true,
  editable: false,
  showTooltip: false,
  showRangeLabels: false,
  marks: () => []
})

const emit = defineEmits<{
  'update:modelValue': [value: number]
  'change': [value: number]
}>()

// 引用
const trackRef = ref<HTMLElement>()
const thumbRef = ref<HTMLElement>()

// 状态
const isDragging = ref(false)
const startX = ref(0)
const startValue = ref(0)

// 计算填充宽度
const fillWidth = computed(() => {
  const percentage = ((props.modelValue - props.min) / (props.max - props.min)) * 100
  return `${Math.min(Math.max(percentage, 0), 100)}%`
})

// 格式化值
const formatValue = (value: number): string => {
  if (props.format) {
    return props.format(value)
  }
  return Number.isInteger(value) ? value.toString() : value.toFixed(2)
}

// 获取刻度位置
const getMarkPosition = (value: number): number => {
  return ((value - props.min) / (props.max - props.min)) * 100
}

// 处理轨道点击
const handleTrackClick = (event: MouseEvent) => {
  if (props.disabled || !trackRef.value) return

  const rect = trackRef.value.getBoundingClientRect()
  const percentage = (event.clientX - rect.left) / rect.width
  const newValue = props.min + percentage * (props.max - props.min)
  const steppedValue = Math.round(newValue / props.step) * props.step

  emitValue(steppedValue)
}

// 处理鼠标按下
const handleMouseDown = (event: MouseEvent) => {
  if (props.disabled) return

  event.preventDefault()
  isDragging.value = true
  startX.value = event.clientX
  startValue.value = props.modelValue

  document.addEventListener('mousemove', handleMouseMove)
  document.addEventListener('mouseup', handleMouseUp)
}

// 处理鼠标移动
const handleMouseMove = (event: MouseEvent) => {
  if (!isDragging.value || !trackRef.value) return

  const rect = trackRef.value.getBoundingClientRect()
  const deltaX = event.clientX - startX.value
  const deltaValue = (deltaX / rect.width) * (props.max - props.min)
  const newValue = startValue.value + deltaValue
  const steppedValue = Math.min(Math.max(newValue, props.min), props.max)
  const finalValue = Math.round(steppedValue / props.step) * props.step

  emitValue(finalValue)
}

// 处理鼠标释放
const handleMouseUp = () => {
  isDragging.value = false
  document.removeEventListener('mousemove', handleMouseMove)
  document.removeEventListener('mouseup', handleMouseUp)
}

// 处理触摸开始
const handleTouchStart = (event: TouchEvent) => {
  if (props.disabled) return

  event.preventDefault()
  isDragging.value = true
  startX.value = event.touches[0].clientX
  startValue.value = props.modelValue

  document.addEventListener('touchmove', handleTouchMove)
  document.addEventListener('touchend', handleTouchEnd)
}

// 处理触摸移动
const handleTouchMove = (event: TouchEvent) => {
  if (!isDragging.value || !trackRef.value) return

  const rect = trackRef.value.getBoundingClientRect()
  const deltaX = event.touches[0].clientX - startX.value
  const deltaValue = (deltaX / rect.width) * (props.max - props.min)
  const newValue = startValue.value + deltaValue
  const steppedValue = Math.min(Math.max(newValue, props.min), props.max)
  const finalValue = Math.round(steppedValue / props.step) * props.step

  emitValue(finalValue)
}

// 处理触摸结束
const handleTouchEnd = () => {
  isDragging.value = false
  document.removeEventListener('touchmove', handleTouchMove)
  document.removeEventListener('touchend', handleTouchEnd)
}

// 处理输入
const handleInput = (event: Event) => {
  const target = event.target as HTMLInputElement
  const value = Number(target.value)

  if (!isNaN(value)) {
    emitValue(value)
  }
}

// 处理变化
const handleChange = (event: Event) => {
  const target = event.target as HTMLInputElement
  const value = Number(target.value)

  if (!isNaN(value)) {
    emitValue(value, true)
  }
}

// 发出值
const emitValue = (value: number, isChange = false) => {
  const clampedValue = Math.min(Math.max(value, props.min), props.max)
  emit('update:modelValue', clampedValue)

  if (isChange) {
    emit('change', clampedValue)
  }
}

// 清理
onUnmounted(() => {
  document.removeEventListener('mousemove', handleMouseMove)
  document.removeEventListener('mouseup', handleMouseUp)
  document.removeEventListener('touchmove', handleTouchMove)
  document.removeEventListener('touchend', handleTouchEnd)
})
</script>

<style scoped>
/* 使用全局样式 */

/* 统一滑杆样式覆盖 */
.parameter-range {
    /* 使用全局滑杆样式 */
    -webkit-appearance: none;
    appearance: none;
    width: 100%;
    height: 6px;
    background: var(--border-color);
    border-radius: 3px;
    outline: none;
    transition: all 0.3s ease;
    border: none;
    padding: 0;
  }

  .parameter-range::-webkit-slider-thumb {
    -webkit-appearance: none;
    appearance: none;
    width: 20px;
    height: 20px;
    background: var(--bg-white);
    border: 3px solid var(--primary-color);
    border-radius: 50%;
    cursor: grab;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
    transition: all 0.3s ease;
  }

  .parameter-range::-webkit-slider-thumb:hover {
    transform: scale(1.2);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
  }

  .parameter-range::-webkit-slider-thumb:active {
    cursor: grabbing;
    transform: scale(1.1);
  }

  .parameter-range::-moz-range-thumb {
    width: 20px;
    height: 20px;
    background: var(--bg-white);
    border: 3px solid var(--primary-color);
    border-radius: 50%;
    cursor: grab;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
    transition: all 0.3s ease;
    border: none;
  }

  .parameter-range::-moz-range-thumb:hover {
    transform: scale(1.2);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
  }

  .parameter-range::-moz-range-thumb:active {
    cursor: grabbing;
    transform: scale(1.1);
  }

  .parameter-range::-webkit-slider-runnable-track {
    height: 100%;
    border-radius: 3px;
  }

  .parameter-range::-moz-range-track {
    height: 100%;
    border-radius: 3px;
  }

  .range-input-group {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 4px 0;
  }

  .range-value {
    min-width: 60px;
    padding: 4px 8px;
    background: var(--bg-secondary);
    border: 1px solid var(--border-color);
    border-radius: var(--border-radius-sm);
    font-size: var(--font-size-sm);
    font-weight: 600;
    color: var(--primary-color);
    text-align: center;
    transition: all 0.3s ease;
  }

  /* 参数配置滑杆样式增强 */
  .parameter-slider {
    display: flex;
    align-items: center;
    gap: 16px;
    padding: 12px;
    background: var(--bg-secondary);
    border-radius: var(--border-radius);
    transition: all 0.3s ease;
  }

  .parameter-slider:hover {
    background: var(--bg-hover);
  }

  .parameter-slider .parameter-info {
    flex: 1;
  }

  .parameter-slider .parameter-name {
    font-size: var(--font-size-sm);
    font-weight: 500;
    color: var(--text-primary);
    margin-bottom: 4px;
  }

  .parameter-slider .parameter-desc {
    font-size: var(--font-size-xs);
    color: var(--text-regular);
  }

  .parameter-slider .parameter-control {
    flex: 2;
    display: flex;
    align-items: center;
    gap: 12px;
  }

</style>
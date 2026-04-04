<template>
  <canvas
    v-show="isActive"
    ref="canvasRef"
    class="vp-canvas-overlay"
    @mousedown="onMouseDown"
    @mousemove="onMouseMove"
    @mouseup="onMouseUp"
    @mouseleave="onMouseUp"
  ></canvas>
</template>

<script setup lang="ts">
import { ref, watch, nextTick, onMounted, onUnmounted } from 'vue'
import { useVolumeProfile, type VPBucket } from '@/composables/useVolumeProfile'

interface Props {
  isActive: boolean
  chart: any
  candleSeries: any
  chartContainer: HTMLElement | undefined
  klineData: any[]
}

const props = defineProps<Props>()
const emit = defineEmits<{
  calculated: [stats: { pocPrice: string; vaLow: string; vaHigh: string }]
}>()

const canvasRef = ref<HTMLCanvasElement>()
const { startSelection, updateSelection, endSelection, calculateVP, drawSelection, drawVP, clearCanvas } = useVolumeProfile()

let isSelecting = false
let resizeObserver: ResizeObserver | null = null

// 同步canvas尺寸
const syncCanvasSize = () => {
  if (!canvasRef.value || !props.chartContainer) return

  const rect = props.chartContainer.getBoundingClientRect()
  canvasRef.value.width = rect.width
  canvasRef.value.height = rect.height
  canvasRef.value.style.width = rect.width + 'px'
  canvasRef.value.style.height = rect.height + 'px'
  clearCanvas(canvasRef.value.getContext('2d')!, rect.width, rect.height)
}

// 监听激活状态
watch(() => props.isActive, async (active) => {
  if (active) {
    await nextTick()
    // 延迟一点确保图表已渲染
    setTimeout(syncCanvasSize, 100)
  }
})

// 监听尺寸变化
onMounted(() => {
  if (props.chartContainer) {
    resizeObserver = new ResizeObserver(syncCanvasSize)
    resizeObserver.observe(props.chartContainer)
    // 初始同步
    syncCanvasSize()
  }
})

onUnmounted(() => {
  resizeObserver?.disconnect()
})

// 坐标转换
const getTimeAndPrice = (e: MouseEvent) => {
  if (!canvasRef.value || !props.chart || !props.candleSeries) return null

  const rect = canvasRef.value.getBoundingClientRect()
  const x = e.clientX - rect.left
  const y = e.clientY - rect.top

  const time = props.chart.timeScale().coordinateToTime(x)
  const price = props.candleSeries.coordinateToPrice(y)

  if (!time || price === null) return null
  return { x, y, time: time as number, price }
}

// 鼠标事件
const onMouseDown = (e: MouseEvent) => {
  if (!props.isActive) return
  const point = getTimeAndPrice(e)
  if (point) {
    startSelection(point.x, point.y, point.time, point.price)
    isSelecting = true
    if (canvasRef.value) {
      clearCanvas(canvasRef.value.getContext('2d')!, canvasRef.value.width, canvasRef.value.height)
    }
  }
}

const onMouseMove = (e: MouseEvent) => {
  if (!isSelecting || !canvasRef.value) return
  const point = getTimeAndPrice(e)
  if (point) {
    updateSelection(point.x, point.y, point.time, point.price)
    const ctx = canvasRef.value.getContext('2d')
    if (ctx) {
      clearCanvas(ctx, canvasRef.value.width, canvasRef.value.height)
      drawSelection(ctx, canvasRef.value.width, canvasRef.value.height)
    }
  }
}

const onMouseUp = () => {
  if (!isSelecting || !canvasRef.value) return
  isSelecting = false

  const selection = endSelection()
  if (!selection) return

  // 计算VP
  const startTime = Math.min(selection.start.time, selection.end.time)
  const endTime = Math.max(selection.start.time, selection.end.time)

  const result = calculateVP(
    props.klineData,
    startTime,
    endTime,
    Math.min(selection.start.price, selection.end.price),
    Math.max(selection.start.price, selection.end.price),
    (price) => props.candleSeries.priceToCoordinate(price)
  )

  if (result && canvasRef.value) {
    const ctx = canvasRef.value.getContext('2d')
    if (ctx) {
      drawVP(
        ctx,
        canvasRef.value.width,
        canvasRef.value.height,
        result.buckets,
        result.maxVolume,
        result.pocIndex,
        result.vaLow,
        result.vaHigh,
        Math.min(selection.start.price, selection.end.price),
        Math.max(selection.start.price, selection.end.price),
        (price) => props.candleSeries.priceToCoordinate(price)
      )
    }
    emit('calculated', {
      pocPrice: result.buckets[result.pocIndex].price.toFixed(2),
      vaLow: result.buckets[result.vaLow].price.toFixed(2),
      vaHigh: result.buckets[result.vaHigh].price.toFixed(2)
    })
  }
}

// 暴露方法给父组件
defineExpose({
  clear: () => {
    if (canvasRef.value) {
      clearCanvas(canvasRef.value.getContext('2d')!, canvasRef.value.width, canvasRef.value.height)
    }
  },
  syncSize: syncCanvasSize
})
</script>

<style scoped>
.vp-canvas-overlay {
  position: absolute;
  top: 0;
  left: 0;
  pointer-events: auto;
  cursor: crosshair;
  z-index: 20;
  /* 调试用边框，确认canvas位置 */
  border: 1px dashed rgba(239, 83, 80, 0.3);
}
</style>

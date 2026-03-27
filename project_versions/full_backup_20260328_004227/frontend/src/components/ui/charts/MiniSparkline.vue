<template>
  <div class="mini-sparkline">
    <svg
      :viewBox="`0 0 ${width} ${height}`"
      preserveAspectRatio="none"
      class="sparkline-svg"
      overflow="visible"
    >
      <!-- 平均线 -->
      <line
        v-if="showAverageLine"
        class="sparkline-avg-line"
        x1="0"
        :y1="averageY"
        :x2="width"
        :y2="averageY"
        :stroke="avgLineColor"
        stroke-width="0.8"
        stroke-dasharray="3,3"
        opacity="0.8"
      />
      <!-- 最高点区域 -->
      <rect
        v-if="showHighLowPoints"
        :x="highPoint.x - 5"
        :y="highPoint.y - 3"
        width="10"
        height="10"
        :fill="highPointColor"
        rx="2"
      />
      <!-- 最低点区域 -->
      <rect
        v-if="showHighLowPoints"
        :x="lowPoint.x - 5"
        :y="lowPoint.y - 3"
        width="10"
        height="10"
        :fill="lowPointColor"
        rx="2"
      />
      <!-- 趋势线 -->
      <polyline
        :points="polylinePoints"
        fill="none"
        :stroke="lineColor"
        stroke-width="1.5"
        stroke-linecap="round"
        stroke-linejoin="round"
      />
      <!-- 端点 -->
      <circle
        class="sparkline-endpoint"
        :cx="endPoint.x"
        :cy="endPoint.y"
        r="2"
        :fill="endpointColor"
      />
    </svg>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  data?: number[]
  width?: number
  height?: number
  lineColor?: string
  endpointColor?: string
  avgLineColor?: string
  highPointColor?: string
  lowPointColor?: string
  showAverageLine?: boolean
  showHighLowPoints?: boolean
  margin?: number
}

const props = withDefaults(defineProps<Props>(), {
  data: () => [],
  width: 120,
  height: 48,
  lineColor: '#d1d4dc',
  endpointColor: '#d1d4dc',
  avgLineColor: '#b0b3bc',
  highPointColor: 'rgba(244,67,54,0.4)',
  lowPointColor: 'rgba(38,166,154,0.4)',
  showAverageLine: true,
  showHighLowPoints: true,
  margin: 4
})

// 计算趋势线的点
const polylinePoints = computed(() => {
  const data = props.data
  if (data.length === 0) return `0,${props.height / 2} ${props.width},${props.height / 2}`

  const effectiveHeight = props.height - props.margin * 2

  const points = data.map((val, i) => {
    const x = (i / Math.max(data.length - 1, 1)) * props.width
    const y = props.height - props.margin - (val * effectiveHeight)
    return `${x.toFixed(1)},${y.toFixed(1)}`
  })
  return points.join(' ')
})

// 计算平均线Y坐标
const averageY = computed(() => {
  const data = props.data
  if (data.length === 0) return props.height / 2

  const avg = data.reduce((a, b) => a + b, 0) / data.length
  const effectiveHeight = props.height - props.margin * 2
  return props.height - props.margin - (avg * effectiveHeight)
})

// 计算端点坐标
const endPoint = computed(() => {
  const data = props.data
  if (data.length === 0) return { x: props.width, y: props.height / 2 }

  const lastVal = data[data.length - 1]
  const effectiveHeight = props.height - props.margin * 2
  return {
    x: props.width,
    y: props.height - props.margin - (lastVal * effectiveHeight)
  }
})

// 计算最高点坐标
const highPoint = computed(() => {
  const data = props.data
  if (data.length === 0) return { x: props.width / 2, y: props.margin }

  let maxIdx = 0
  let maxVal = data[0]
  data.forEach((val, i) => {
    if (val > maxVal) {
      maxVal = val
      maxIdx = i
    }
  })

  const effectiveHeight = props.height - props.margin * 2
  return {
    x: (maxIdx / Math.max(data.length - 1, 1)) * props.width,
    y: props.height - props.margin - (maxVal * effectiveHeight)
  }
})

// 计算最低点坐标
const lowPoint = computed(() => {
  const data = props.data
  if (data.length === 0) return { x: props.width / 2, y: props.height - props.margin }

  let minIdx = 0
  let minVal = data[0]
  data.forEach((val, i) => {
    if (val < minVal) {
      minVal = val
      minIdx = i
    }
  })

  const effectiveHeight = props.height - props.margin * 2
  return {
    x: (minIdx / Math.max(data.length - 1, 1)) * props.width,
    y: props.height - props.margin - (minVal * effectiveHeight)
  }
})
</script>

<style lang="scss" scoped>
.mini-sparkline {
  width: 100%;
  height: 100%;
  overflow: visible;

  .sparkline-svg {
    width: 100%;
    height: 100%;
    overflow: visible;
  }

  .sparkline-avg-line {
    transition: y1 0.3s ease, y2 0.3s ease;
  }

  .sparkline-endpoint {
    transition: cx 0.3s ease, cy 0.3s ease;
  }
}
</style>

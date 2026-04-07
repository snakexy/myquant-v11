<template>
  <div class="mini-chart" ref="chartContainer">
    <canvas ref="chartCanvas" :width="width" :height="height"></canvas>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, nextTick } from 'vue'

interface Props {
  data: number[]
  width?: number
  height?: number
  type?: 'line' | 'bar' | 'area'
  color?: string
  backgroundColor?: string
}

const props = withDefaults(defineProps<Props>(), {
  width: 120,
  height: 40,
  type: 'line',
  color: '#8b5cf6',
  backgroundColor: 'rgba(139, 92, 246, 0.1)'
})

const chartContainer = ref<HTMLElement>()
const chartCanvas = ref<HTMLCanvasElement>()

// 绘制图表
const drawChart = () => {
  const canvas = chartCanvas.value
  if (!canvas || !props.data || props.data.length === 0) return
  
  const ctx = canvas.getContext('2d')
  if (!ctx) return
  
  const width = props.width
  const height = props.height
  const padding = 4
  
  // 清除画布
  ctx.clearRect(0, 0, width, height)
  
  // 计算数据范围
  const minValue = Math.min(...props.data)
  const maxValue = Math.max(...props.data)
  const range = maxValue - minValue || 1
  
  // 绘制背景
  if (props.type === 'area') {
    ctx.fillStyle = props.backgroundColor
    ctx.fillRect(padding, padding, width - padding * 2, height - padding * 2)
  }
  
  // 绘制数据
  const stepX = (width - padding * 2) / (props.data.length - 1)
  const scaleY = (height - padding * 2) / range
  
  if (props.type === 'line' || props.type === 'area') {
    // 绘制线条
    ctx.beginPath()
    ctx.strokeStyle = props.color
    ctx.lineWidth = 2
    ctx.lineCap = 'round'
    ctx.lineJoin = 'round'
    
    props.data.forEach((value, index) => {
      const x = padding + index * stepX
      const y = height - padding - (value - minValue) * scaleY
      
      if (index === 0) {
        ctx.moveTo(x, y)
      } else {
        ctx.lineTo(x, y)
      }
    })
    
    ctx.stroke()
    
    // 填充区域
    if (props.type === 'area') {
      ctx.lineTo(width - padding, height - padding)
      ctx.lineTo(padding, height - padding)
      ctx.closePath()
      ctx.fillStyle = props.backgroundColor
      ctx.fill()
    }
  } else if (props.type === 'bar') {
    // 绘制柱状图
    const barWidth = stepX * 0.6
    const barSpacing = stepX * 0.4
    
    props.data.forEach((value, index) => {
      const x = padding + index * stepX + barSpacing / 2
      const barHeight = (value - minValue) * scaleY
      const y = height - padding - barHeight
      
      ctx.fillStyle = props.color
      ctx.fillRect(x, y, barWidth, barHeight)
    })
  }
  
  // 绘制数据点
  if (props.type === 'line' || props.type === 'area') {
    props.data.forEach((value, index) => {
      const x = padding + index * stepX
      const y = height - padding - (value - minValue) * scaleY
      
      ctx.beginPath()
      ctx.arc(x, y, 3, 0, Math.PI * 2)
      ctx.fillStyle = props.color
      ctx.fill()
      
      // 白色边框
      ctx.beginPath()
      ctx.arc(x, y, 3, 0, Math.PI * 2)
      ctx.strokeStyle = 'white'
      ctx.lineWidth = 1
      ctx.stroke()
    })
  }
}

// 监听数据变化
watch(() => props.data, () => {
  nextTick(() => {
    drawChart()
  })
}, { deep: true })

// 监听类型变化
watch(() => props.type, () => {
  nextTick(() => {
    drawChart()
  })
})

onMounted(() => {
  nextTick(() => {
    drawChart()
  })
})
</script>

<style lang="scss" scoped>
.mini-chart {
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.02);
  border-radius: 4px;
  overflow: hidden;
  
  canvas {
    display: block;
  }
}
</style>
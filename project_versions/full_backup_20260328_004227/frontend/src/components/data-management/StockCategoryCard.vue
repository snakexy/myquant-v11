<template>
  <div class="category-card">
    <div class="category-header">
      <div class="category-info">
        <h3>{{ category.name }}</h3>
        <p>{{ category.description }}</p>
      </div>
      <div class="category-stats">
        <div class="stat-item">
          <span class="stat-label">股票数量</span>
          <span class="stat-value">{{ category.count }}</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">平均涨幅</span>
          <span class="stat-value" :class="performanceClass">
            {{ category.avgReturn > 0 ? '+' : '' }}{{ category.avgReturn.toFixed(2) }}%
          </span>
        </div>
      </div>
    </div>

    <div class="category-content">
      <div class="performance-chart">
        <canvas :ref="chartRef" width="200" height="80"></canvas>
      </div>

      <div class="top-stocks">
        <h4>热门股票</h4>
        <div class="stock-list">
          <div
            v-for="stock in category.topStocks"
            :key="stock.code"
            class="stock-item"
          >
            <span class="stock-code">{{ stock.code }}</span>
            <span class="stock-name">{{ stock.name }}</span>
            <span class="stock-change" :class="getPerformanceClass(stock.changePercent)">
              {{ stock.changePercent > 0 ? '+' : '' }}{{ stock.changePercent.toFixed(2) }}%
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'

interface Stock {
  code: string
  name: string
  changePercent: number
}

interface Category {
  id: string
  name: string
  description: string
  count: number
  avgReturn: number
  topStocks: Stock[]
  chartData?: number[]
}

const props = defineProps<{
  category: Category
}>()

const chartRef = ref<HTMLCanvasElement | null>(null)

const performanceClass = computed(() => {
  if (props.category.avgReturn > 0) return 'positive'
  if (props.category.avgReturn < 0) return 'negative'
  return 'neutral'
})

const getPerformanceClass = (value: number) => {
  if (value > 0) return 'positive'
  if (value < 0) return 'negative'
  return 'neutral'
}

const drawChart = () => {
  const canvas = chartRef.value
  if (!canvas) return

  const ctx = canvas.getContext('2d')
  if (!ctx) return

  const width = canvas.width
  const height = canvas.height
  const data = props.category.chartData || []

  // 清空画布
  ctx.clearRect(0, 0, width, height)

  // 绘制背景网格
  ctx.strokeStyle = 'rgba(255, 255, 255, 0.05)'
  ctx.lineWidth = 1
  for (let i = 0; i < 4; i++) {
    const y = (height / 4) * i
    ctx.beginPath()
    ctx.moveTo(0, y)
    ctx.lineTo(width, y)
    ctx.stroke()
  }

  // 绘制折线图
  if (data.length > 1) {
    const padding = 5
    const chartWidth = width - padding * 2
    const chartHeight = height - padding * 2

    // 计算数据范围
    const min = Math.min(...data)
    const max = Math.max(...data)
    const range = max - min || 1

    // 绘制线条
    ctx.beginPath()
    ctx.strokeStyle = props.category.avgReturn >= 0 ? '#ef4444' : '#10b981' // 红色涨，绿色跌
    ctx.lineWidth = 2

    data.forEach((value, index) => {
      const x = padding + (index / (data.length - 1)) * chartWidth
      const y = padding + chartHeight - ((value - min) / range) * chartHeight

      if (index === 0) {
        ctx.moveTo(x, y)
      } else {
        ctx.lineTo(x, y)
      }
    })

    ctx.stroke()

    // 绘制渐变填充
    const gradient = ctx.createLinearGradient(0, 0, 0, height)
    const color = props.category.avgReturn >= 0 ? '239, 68, 68' : '16, 185, 129' // 红色涨，绿色跌
    gradient.addColorStop(0, `rgba(${color}, 0.3)`)
    gradient.addColorStop(1, `rgba(${color}, 0)`)

    ctx.lineTo(padding + chartWidth, padding + chartHeight)
    ctx.lineTo(padding, padding + chartHeight)
    ctx.closePath()
    ctx.fillStyle = gradient
    ctx.fill()
  }
}

onMounted(() => {
  drawChart()
})
</script>

<style scoped lang="scss">
.category-card {
  background: var(--card-bg);
  border-radius: 12px;
  padding: 20px;
  transition: all 0.3s ease;
  border: 1px solid var(--border-color);

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
  }
}

.category-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--border-color);
}

.category-info {
  flex: 1;

  h3 {
    font-size: 16px;
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 4px;
  }

  p {
    font-size: 12px;
    color: var(--text-secondary);
  }
}

.category-stats {
  display: flex;
  gap: 24px;
}

.stat-item {
  text-align: center;

  .stat-label {
    display: block;
    font-size: 11px;
    color: var(--text-secondary);
    margin-bottom: 4px;
  }

  .stat-value {
    display: block;
    font-size: 18px;
    font-weight: 600;
    color: var(--text-primary);

    &.positive {
      color: #ef4444; // 红色表示上涨
    }

    &.negative {
      color: #10b981; // 绿色表示下跌
    }

    &.neutral {
      color: var(--text-secondary);
    }
  }
}

.category-content {
  display: flex;
  gap: 16px;
}

.performance-chart {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-secondary);
  border-radius: 8px;
  padding: 8px;

  canvas {
    width: 100%;
    height: 100%;
  }
}

.top-stocks {
  flex: 1;

  h4 {
    font-size: 12px;
    font-weight: 500;
    color: var(--text-secondary);
    margin-bottom: 8px;
  }
}

.stock-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.stock-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 6px 10px;
  background: var(--bg-secondary);
  border-radius: 6px;
  font-size: 12px;
  transition: all 0.2s ease;

  &:hover {
    background: var(--hover-bg);
  }
}

.stock-code {
  font-weight: 600;
  color: var(--text-primary);
  margin-right: 8px;
}

.stock-name {
  flex: 1;
  color: var(--text-secondary);
}

.stock-change {
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 4px;

  &.positive {
    color: #ef4444; // 红色表示上涨
    background: rgba(239, 68, 68, 0.1);
  }

  &.negative {
    color: #10b981; // 绿色表示下跌
    background: rgba(16, 185, 129, 0.1);
  }

  &.neutral {
    color: var(--text-secondary);
  }
}

@media (max-width: 768px) {
  .category-header {
    flex-direction: column;
    gap: 12px;
  }

  .category-content {
    flex-direction: column;
  }

  .performance-chart,
  .top-stocks {
    width: 100%;
  }
}
</style>

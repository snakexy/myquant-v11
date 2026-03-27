<template>
  <div class="chart-test-page">
    <!-- 步骤1：测试顶部工具栏 -->
    <div class="test-toolbar">
      <h1>步骤1：添加顶部工具栏</h1>
      <div class="toolbar-content">
        <button @click="changePeriod('5min')">5分</button>
        <button @click="changePeriod('day')">日线</button>
        <button class="active">{{ currentPeriod }}</button>
      </div>
    </div>

    <div class="chart-container" ref="chartContainer"></div>

    <div class="status">
      <p>状态: {{ status }}</p>
      <p>✅ 请测试：鼠标滚轮、拖动、十字准星</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { createChart, CandlestickSeries } from 'lightweight-charts'

const chartContainer = ref<HTMLElement>()
const status = ref('初始化中...')
const currentPeriod = ref('日线')

let chart: any = null
let series: any = null

onMounted(() => {
  try {
    status.value = '创建图表中...'

    if (!chartContainer.value) {
      status.value = '❌ 找不到容器'
      return
    }

    const width = chartContainer.value.clientWidth
    const height = chartContainer.value.clientHeight

    // 创建图表
    chart = createChart(chartContainer.value, {
      width,
      height,
      layout: {
        background: { color: '#131722' },
        textColor: '#d1d4dc',
      },
      grid: {
        vertLines: { color: 'rgba(42, 46, 57, 0.5)' },
        horzLines: { color: 'rgba(42, 46, 57, 0.5)' },
      },
      handleScroll: true,
      handleScale: true,
      kineticScroll: true,
    })

    console.log('[ChartTest] ✅ 步骤1：图表创建成功（带顶部工具栏）')

    // 创建K线系列
    series = chart.addSeries(CandlestickSeries, {
      upColor: '#26a69a',
      downColor: '#ef5350',
      borderVisible: false,
      wickUpColor: '#26a69a',
      wickDownColor: '#ef5350',
    })

    // 生成测试数据
    const generateData = () => {
      const data = []
      let time = Math.floor(Date.now() / 1000) - 86400 * 100
      let price = 100

      for (let i = 0; i < 100; i++) {
        const open = price
        const change = (Math.random() - 0.5) * 2
        const close = open + change
        const high = Math.max(open, close) + Math.random()
        const low = Math.min(open, close) - Math.random()

        data.push({
          time,
          open: parseFloat(open.toFixed(2)),
          high: parseFloat(high.toFixed(2)),
          low: parseFloat(low.toFixed(2)),
          close: parseFloat(close.toFixed(2)),
        })

        price = close
        time += 86400
      }

      return data
    }

    const data = generateData()
    series.setData(data)
    chart.timeScale().fitContent()

    status.value = '✅ 步骤1完成：请测试鼠标事件'

  } catch (error) {
    console.error('[ChartTest] 创建失败:', error)
    status.value = '❌ 创建失败: ' + error
  }
})

onUnmounted(() => {
  if (chart) {
    chart.remove()
  }
})

const changePeriod = (period: string) => {
  currentPeriod.value = period === '5min' ? '5分' : '日线'
  console.log('[ChartTest] 切换周期:', period)
}
</script>

<style scoped>
.chart-test-page {
  width: 100vw;
  height: 100vh;
  background: #0f0f23;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* 测试工具栏 */
.test-toolbar {
  padding: 10px 20px;
  background: #131722;
  border-bottom: 1px solid #2a2e39;
  display: flex;
  align-items: center;
  gap: 20px;
  flex-shrink: 0;
}

.test-toolbar h1 {
  color: #d1d4dc;
  margin: 0;
  font-size: 16px;
  font-weight: 600;
}

.toolbar-content {
  display: flex;
  gap: 8px;
}

.toolbar-content button {
  padding: 6px 12px;
  background: transparent;
  border: 1px solid #2a2e39;
  color: #d1d4dc;
  border-radius: 4px;
  cursor: pointer;
  font-size: 13px;
  transition: all 0.15s ease;
}

.toolbar-content button:hover {
  background: #2a2e39;
}

.toolbar-content button.active {
  background: #2962ff;
  border-color: #2962ff;
  color: white;
}

/* 图表容器 */
.chart-container {
  flex: 1;
  background: #131722;
  min-height: 400px;
}

/* 状态栏 */
.status {
  padding: 10px 20px;
  background: #1e222d;
  border-top: 1px solid #2a2e39;
  color: #d1d4dc;
  font-family: monospace;
  font-size: 13px;
  flex-shrink: 0;
}

.status p {
  margin: 3px 0;
}
</style>

<template>
  <div class="chart-test-page">
    <h1>Lightweight-Charts 纯净测试</h1>
    <div class="chart-container" ref="chartContainer"></div>
    <div class="status">
      <p>状态: {{ status }}</p>
      <p>图表尺寸: {{ chartSize }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { createChart, CandlestickSeries } from 'lightweight-charts'

const chartContainer = ref<HTMLElement>()
const status = ref('初始化中...')
const chartSize = ref({ width: 0, height: 0 })

let chart: any = null
let series: any = null

onMounted(() => {
  try {
    status.value = '创建图表中...'

    if (!chartContainer.value) {
      status.value = '❌ 找不到容器'
      return
    }

    // 获取容器尺寸
    const width = chartContainer.value.clientWidth
    const height = chartContainer.value.clientHeight
    chartSize.value = { width, height }

    console.log('[ChartTest] 容器尺寸:', { width, height })

    // 创建图表（最简单的配置）
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
      // ✅ 明确启用所有鼠标事件
      handleScroll: true,
      handleScale: true,
      kineticScroll: true,
    })

    console.log('[ChartTest] 图表创建成功')
    console.log('[ChartTest] handleScroll:', chart.options().handleScroll)
    console.log('[ChartTest] handleScale:', chart.options().handleScale)

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
      let time = Math.floor(Date.now() / 1000) - 86400 * 100 // 从100天前开始
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
        time += 86400 // 每天一个数据点
      }

      return data
    }

    const data = generateData()
    series.setData(data)

    console.log('[ChartTest] 数据设置完成，数据点数:', data.length)

    // 自适应视图
    chart.timeScale().fitContent()

    status.value = '✅ 图表创建成功，请测试鼠标事件'

    // 添加测试事件监听
    chart.subscribeClick((param: any) => {
      console.log('[ChartTest] 点击事件:', param)
    })

    chart.subscribeCrosshairMove((param: any) => {
      if (!param.time) return
      console.log('[ChartTest] 十字准星移动:', param.time, param.point?.price)
    })

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
</script>

<style scoped>
.chart-test-page {
  width: 100vw;
  height: 100vh;
  background: #0f0f23;
  padding: 20px;
  display: flex;
  flex-direction: column;
}

h1 {
  color: #d1d4dc;
  margin: 0 0 10px 0;
  font-size: 20px;
}

.chart-container {
  flex: 1;
  background: #131722;
  border-radius: 8px;
  min-height: 500px;
}

.status {
  margin-top: 10px;
  padding: 10px;
  background: #1e222d;
  border-radius: 4px;
  color: #d1d4dc;
  font-family: monospace;
  font-size: 14px;
}

.status p {
  margin: 5px 0;
}
</style>

<template>
  <div class="chart-test-page">
    <!-- 步骤3：测试左侧工具栏 -->
    <div class="test-toolbar">
      <h1>步骤3：添加左侧工具栏</h1>
      <div class="toolbar-content">
        <button @click="changePeriod('5min')">5分</button>
        <button @click="changePeriod('day')">日线</button>
        <button class="active">{{ currentPeriod }}</button>
      </div>
    </div>

    <div class="main-content">
      <!-- 左侧工具栏 -->
      <div class="test-left-toolbar">
        <button class="tool-btn active" title="光标">🖱️</button>
        <button class="tool-btn" title="十字准星">✛</button>
        <button class="tool-btn" title="趋势线">📈</button>
        <button class="tool-btn" title="水平线">➖</button>
        <button class="tool-btn" title="做多">🟢</button>
        <button class="tool-btn" title="做空">🔴</button>
      </div>

      <div class="chart-container" ref="chartContainer"></div>

      <!-- 右侧边栏 -->
      <div class="test-sidebar">
        <h3>观察列表</h3>
        <div class="stock-item" v-for="i in 5" :key="i">
          <span class="code">60000{{ i }}</span>
          <span class="name">测试股票{{ i }}</span>
        </div>
      </div>
    </div>

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

    console.log('[ChartTest] ✅ 步骤3：图表创建成功（完整布局：顶部工具栏 + 左侧工具栏 + 右侧边栏）')

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

    status.value = '✅ 步骤3完成：请测试鼠标事件'

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

/* 主内容区 */
.main-content {
  flex: 1;
  display: flex;
  overflow: hidden;
  position: relative;
}

/* 左侧工具栏 */
.test-left-toolbar {
  position: absolute;
  left: 6px;
  top: 6px;
  width: 40px;
  background: #131722;
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
  display: flex;
  flex-direction: column;
  gap: 2px;
  padding: 3px;
  z-index: 100;
}

.tool-btn {
  width: 32px;
  height: 32px;
  background: transparent;
  border: none;
  color: #d1d4dc;
  border-radius: 3px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  transition: all 0.1s ease;
}

.tool-btn:hover {
  background: #1e222d;
}

.tool-btn.active {
  background: #2962ff;
  color: white;
}

/* 图表容器 */
.chart-container {
  flex: 1;
  background: #131722;
  min-width: 0;
  margin-left: 50px; /* 为左侧工具栏留空间 */
}

/* 右侧边栏 */
.test-sidebar {
  width: 280px;
  background: #131722;
  border-left: 1px solid #2a2e39;
  overflow-y: auto;
  flex-shrink: 0;
}

.test-sidebar h3 {
  color: #d1d4dc;
  padding: 12px 16px;
  margin: 0;
  font-size: 14px;
  border-bottom: 1px solid #2a2e39;
}

.stock-item {
  padding: 10px 16px;
  display: flex;
  justify-content: space-between;
  border-bottom: 1px solid #2a2e39;
  cursor: pointer;
  transition: background 0.15s ease;
}

.stock-item:hover {
  background: #1e222d;
}

.stock-item .code {
  color: #d1d4dc;
  font-size: 13px;
  font-weight: 500;
}

.stock-item .name {
  color: #787b86;
  font-size: 12px;
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

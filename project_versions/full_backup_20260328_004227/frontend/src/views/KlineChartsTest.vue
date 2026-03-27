<template>
  <div class="kline-test-page">
    <div class="page-header">
      <h1>KlineCharts 测试页面</h1>
      <p>专业级金融图表 - 包含做多/做空标注功能</p>
    </div>

    <div class="chart-wrapper">
      <TradingViewKLineUnified
        ref="klineChartRef"
        symbol="000001.SZ"
        stock-name="平安银行"
        :initial-data="formattedKlineData"
        height="700px"
        period="day"
        @chart-ready="onChartReady"
      />
    </div>

    <div class="info-panel">
      <h3>使用说明</h3>
      <ul>
        <li>📈 点击 <strong>做多</strong> 按钮，然后点击 K 线添加买入标记</li>
        <li>📉 点击 <strong>做空</strong> 按钮，然后点击 K 线添加卖出标记</li>
        <li>🗑️ 点击 <strong>清除</strong> 按钮删除所有标注</li>
        <li>支持鼠标滚轮缩放、拖拽平移</li>
      </ul>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import TradingViewKLineUnified from '@/components/charts/TradingViewKLineUnified.vue'
import type { KLineDataItem } from '@/components/charts/TradingViewKLineUnified.vue'

const klineChartRef = ref()
const klineData = ref<KLineDataItem[]>([])

// 格式化K线数据以适配lightweight-charts格式
const formattedKlineData = computed(() => {
  return klineData.value.map(item => ({
    time: item.timestamp / 1000 as any,  // 转换为秒级时间戳
    open: item.open,
    high: item.high,
    low: item.low,
    close: item.close,
    volume: item.volume
  }))
})

/**
 * 图表初始化完成
 */
function onChartReady() {
  console.log('[KlineChartsTest] 图表已初始化')

  // 加载测试数据
  loadTestData()
}

/**
 * 加载测试数据
 */
async function loadTestData() {
  try {
    // 生成模拟数据
    const mockData = generateMockData()
    klineData.value = mockData
  } catch (error) {
    console.error('[KlineChartsTest] 加载数据失败:', error)
  }
}

/**
 * 生成模拟数据
 */
function generateMockData(): KLineDataItem[] {
  const data: KLineDataItem[] = []
  const basePrice = 12.0  // 使用更合理的股票价格
  const now = Date.now()
  const dayInMs = 24 * 60 * 60 * 1000

  let price = basePrice

  for (let i = 0; i < 100; i++) {
    const timestamp = now - (100 - i) * dayInMs
    const volatility = 0.02 // 2% 波动

    const open = price
    const change = (Math.random() - 0.5) * 2 * volatility * price
    const close = open + change
    const high = Math.max(open, close) + Math.random() * volatility * price
    const low = Math.min(open, close) - Math.random() * volatility * price
    const volume = Math.floor(Math.random() * 1000000) + 500000

    data.push({
      timestamp: timestamp / 1000 as any,  // 转换为秒级时间戳
      open: Number(open.toFixed(2)),
      high: Number(high.toFixed(2)),
      low: Number(low.toFixed(2)),
      close: Number(close.toFixed(2)),
      volume,
    })

    price = close
  }

  return data
}
</script>

<style scoped lang="scss">
.kline-test-page {
  padding: 20px;
  background: #121212;
  min-height: 100vh;
  color: #d9d9d9;

  .page-header {
    text-align: center;
    margin-bottom: 30px;

    h1 {
      font-size: 32px;
      font-weight: 600;
      margin-bottom: 10px;
      background: linear-gradient(135deg, #26A69A, #2962FF);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }

    p {
      font-size: 16px;
      color: #868686;
    }
  }

  .chart-wrapper {
    background: #1e1e1e;
    border-radius: 12px;
    padding: 20px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  }

  .info-panel {
    margin-top: 20px;
    background: #1e1e1e;
    border-radius: 12px;
    padding: 20px;

    h3 {
      font-size: 18px;
      margin-bottom: 15px;
      color: #26A69A;
    }

    ul {
      list-style: none;
      padding: 0;

      li {
        padding: 10px 0;
        border-bottom: 1px solid #2a2a2a;
        color: #868686;

        &:last-child {
          border-bottom: none;
        }

        strong {
          color: #d9d9d9;
        }
      }
    }
  }
}
</style>

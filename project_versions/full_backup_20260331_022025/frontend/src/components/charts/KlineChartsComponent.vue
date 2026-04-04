<template>
  <div class="klinecharts-container">
    <!-- 图表容器 -->
    <div ref="chartContainer" class="chart-container"></div>

    <!-- 多头/空头工具栏 -->
    <div v-if="showToolbar" class="annotation-toolbar">
      <button
        @click="toggleAnnotationMode('long')"
        :class="{ active: annotationMode === 'long' }"
        class="tool-btn long-btn"
        title="多头买入 (B)"
      >
        <span class="icon">📈</span>
        <span>做多</span>
      </button>

      <button
        @click="toggleAnnotationMode('short')"
        :class="{ active: annotationMode === 'short' }"
        class="tool-btn short-btn"
        title="空头卖出 (S)"
      >
        <span class="icon">📉</span>
        <span>做空</span>
      </button>

      <button
        @click="clearAnnotations"
        class="tool-btn clear-btn"
        title="清除所有标注"
      >
        <span class="icon">🗑️</span>
        <span>清除</span>
      </button>
    </div>

    <!-- 提示信息 -->
    <div v-if="annotationMode" class="annotation-hint">
      {{ annotationMode === 'long' ? '点击K线添加做多标记' : '点击K线添加做空标记' }}
      <span @click="annotationMode = null" class="close-hint">×</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, watch, PropType } from 'vue'
import { init, dispose, Chart } from 'klinecharts'
import type { KLineData } from './types'

interface Props {
  data?: KLineData[]
  height?: string
  showToolbar?: boolean
  symbol?: string
}

const props = withDefaults(defineProps<Props>(), {
  height: '600px',
  showToolbar: true,
  symbol: 'BTC/USDT'
})

const emit = defineEmits<{
  ready: [chart: Chart]
  annotationAdded: [type: 'long' | 'short', data: KLineData]
}>()

const chartContainer = ref<HTMLElement>()
let chart: Chart | null = null
const annotationMode = ref<'long' | 'short' | null>(null)

/**
 * 初始化图表
 */
onMounted(() => {
  if (!chartContainer.value) return

  // 创建图表实例
  chart = init(chartContainer.value)

  // 配置样式（专业深色主题）
  chart?.setStyles({
    grid: {
      show: true,
      size: 1,
      color: '#2962FF',
      style: 1,
    },
    candle: {
      type: 'candle_solid',
      bar: {
        upColor: '#26A69A',
        downColor: '#EF5350',
        noChangeColor: '#888888',
      },
      tooltip: {
        showRule: 'always',
        showType: 'standard',
        labels: ['时间: ', '开: ', '高: ', '低: ', '收: ', '成交量: '],
        text: {
          size: 12,
          color: '#D9D9D9',
        },
      },
    },
    indicator: {
      tooltip: {
        showRule: 'always',
        showType: 'standard',
        text: {
          size: 12,
          color: '#D9D9D9',
        },
      },
    },
    xAxis: {
      show: true,
      axisLine: {
        show: true,
        color: '#868686',
      },
      tickLine: {
        show: true,
        length: 5,
        color: '#868686',
      },
      tickText: {
        show: true,
        color: '#D9D9D9',
        size: 12,
      },
    },
    yAxis: {
      show: true,
      position: 'right',
      axisLine: {
        show: true,
        color: '#868686',
      },
      tickLine: {
        show: true,
        length: 5,
        color: '#868686',
      },
      tickText: {
        show: true,
        color: '#D9D9D9',
        size: 12,
      },
    },
  })

  // 添加技术指标
  chart?.createIndicator('MA', true, { id: 'candle_pane' })
  chart?.createIndicator('VOL', false, { id: 'volume_pane' })

  // 启用缩放和平移
  chart?.setScaleEnabled(true)
  chart?.setScrollEnabled(true)

  // 注册点击事件（用于添加标注）
  chart?.subscribeClickClick(onChartClick)

  emit('ready', chart!)
})

/**
 * 销毁图表
 */
onBeforeUnmount(() => {
  if (chart) {
    dispose(chartContainer.value!)
    chart = null
  }
})

/**
 * 监听数据变化
 */
watch(
  () => props.data,
  (newData) => {
    if (!chart || !newData) return

    // 转换数据格式为 KlineCharts 格式
    const klineData = newData.map(item => ({
      timestamp: item.timestamp,
      open: item.open,
      high: item.high,
      low: item.low,
      close: item.close,
      volume: item.volume,
    }))

    chart?.applyNewData(klineData)
  },
  { deep: true }
)

/**
 * 切换标注模式
 */
function toggleAnnotationMode(mode: 'long' | 'short') {
  if (annotationMode.value === mode) {
    annotationMode.value = null
  } else {
    annotationMode.value = mode
  }
}

/**
 * 清除所有标注
 */
function clearAnnotations() {
  // TODO: 实现清除标注逻辑
  console.log('[KlineChartsComponent] 清除所有标注')
}

/**
 * 图表点击事件处理
 */
function onChartClick(params: any) {
  if (!annotationMode.value || !props.data) return

  // 获取点击位置的数据
  const { dataIndex } = params
  if (dataIndex !== undefined && props.data[dataIndex]) {
    const klineData = props.data[dataIndex]

    // 添加标注
    addAnnotation(annotationMode.value, klineData)

    // 触发事件
    emit('annotationAdded', annotationMode.value, klineData)

    // 退出标注模式
    annotationMode.value = null
  }
}

/**
 * 添加标注
 */
function addAnnotation(type: 'long' | 'short', data: KLineData) {
  if (!chart) return

  // 使用 KlineCharts 的标注 API
  if (type === 'long') {
    chart?.createAnnotation({
      point: {
        timestamp: data.timestamp,
        value: data.low,
      },
      options: {
        mark: 'circle',
        color: '#26A69A',
        size: 12,
      },
    })
  } else {
    chart?.createAnnotation({
      point: {
        timestamp: data.timestamp,
        value: data.high,
      },
      options: {
        mark: 'circle',
        color: '#EF5350',
        size: 12,
      },
    })
  }

  console.log(`[KlineChartsComponent] 添加${type === 'long' ? '做多' : '做空'}标注:`, data)
}

/**
 * 更新数据
 */
function updateData(data: KLineData[]) {
  if (!chart) return

  const klineData = data.map(item => ({
    timestamp: item.timestamp,
    open: item.open,
    high: item.high,
    low: item.low,
    close: item.close,
    volume: item.volume,
  }))

  chart.applyNewData(klineData)
}

/**
 * 暴露方法给父组件
 */
defineExpose({
  updateData,
  clearAnnotations,
})
</script>

<style scoped lang="scss">
.klinecharts-container {
  position: relative;
  width: 100%;
  height: v-bind(height);

  .chart-container {
    width: 100%;
    height: 100%;
    background: #1e1e1e;
    border-radius: 8px;
    overflow: hidden;
  }

  .annotation-toolbar {
    position: absolute;
    top: 10px;
    left: 10px;
    display: flex;
    gap: 8px;
    background: rgba(30, 30, 30, 0.9);
    padding: 8px;
    border-radius: 8px;
    backdrop-filter: blur(10px);
    z-index: 100;

    .tool-btn {
      display: flex;
      align-items: center;
      gap: 6px;
      padding: 8px 16px;
      border: none;
      border-radius: 6px;
      font-size: 14px;
      font-weight: 500;
      cursor: pointer;
      transition: all 0.2s;
      background: #2a2a2a;
      color: #d9d9d9;

      &:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
      }

      &.active {
        box-shadow: 0 0 0 2px currentColor;
      }

      .icon {
        font-size: 16px;
      }
    }

    .long-btn {
      &:hover,
      &.active {
        background: rgba(38, 166, 154, 0.2);
        color: #26A69A;
      }
    }

    .short-btn {
      &:hover,
      &.active {
        background: rgba(239, 83, 80, 0.2);
        color: #EF5350;
      }
    }

    .clear-btn {
      &:hover {
        background: rgba(255, 152, 0, 0.2);
        color: #ff9800;
      }
    }
  }

  .annotation-hint {
    position: absolute;
    top: 10px;
    right: 10px;
    background: rgba(41, 98, 255, 0.9);
    color: white;
    padding: 10px 16px;
    border-radius: 6px;
    font-size: 14px;
    backdrop-filter: blur(10px);
    z-index: 100;

    .close-hint {
      margin-left: 10px;
      cursor: pointer;
      font-size: 20px;
      opacity: 0.8;

      &:hover {
        opacity: 1;
      }
    }
  }
}
</style>

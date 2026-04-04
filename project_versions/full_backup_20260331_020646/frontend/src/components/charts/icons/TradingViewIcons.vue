<template>
  <component :is="`svg-${icon}`" />
</template>

<script setup lang="ts">
import { defineComponent, h, type Component } from 'vue'

// ==================== 图标组件定义 ====================

// 基础工具图标
const SvgCursor = defineComponent({
  setup() {
    return () => h('svg', {
      width: '18',
      height: '18',
      viewBox: '0 0 24 24',
      fill: 'currentColor'
    }, [
      h('path', {
        d: 'M7 2l12 11.2-5.8.5 3.3 7.3 1.3-7.3-7.3 5.8-.5z'
      })
    ])
  }
})

const SvgCrosshair = defineComponent({
  setup() {
    return () => h('svg', {
      width: '18',
      height: '18',
      viewBox: '0 0 24 24',
      fill: 'currentColor'
    }, [
      h('path', {
        d: 'M11 2v7H4v2h7v7h2v-7h7V9h-7V2z'
      })
    ])
  }
})

// 绘图工具图标
const SvgTrendLine = defineComponent({
  setup() {
    return () => h('svg', {
      width: '18',
      height: '18',
      viewBox: '0 0 24 24',
      fill: 'none',
      stroke: 'currentColor',
      'stroke-width': '2',
      'stroke-linecap': 'round',
      'stroke-linejoin': 'round'
    }, [
      h('path', { d: 'M4 20L20 4' })
    ])
  }
})

const SvgPriceLine = defineComponent({
  setup() {
    return () => h('svg', {
      width: '18',
      height: '18',
      viewBox: '0 0 24 24',
      fill: 'none',
      stroke: 'currentColor',
      'stroke-width': '2',
      'stroke-linecap': 'round'
    }, [
      h('line', { x1: '4', y1: '12', x2: '20', y2: '12' })
    ])
  }
})

const SvgVerticalLine = defineComponent({
  setup() {
    return () => h('svg', {
      width: '18',
      height: '18',
      viewBox: '0 0 24 24',
      fill: 'none',
      stroke: 'currentColor',
      'stroke-width': '2',
      'stroke-linecap': 'round'
    }, [
      h('line', { x1: '12', y1: '4', x2: '12', y2: '20' })
    ])
  }
})

const SvgRayLine = defineComponent({
  setup() {
    return () => h('svg', {
      width: '18',
      height: '18',
      viewBox: '0 0 24 24',
      fill: 'none',
      stroke: 'currentColor',
      'stroke-width': '2',
      'stroke-linecap': 'round'
    }, [
      h('line', { x1: '4', y1: '12', x2: '20', y2: '12' }),
      h('circle', { cx: '4', cy: '12', r: '2', fill: 'currentColor' })
    ])
  }
})

const SvgParallelChannel = defineComponent({
  setup() {
    return () => h('svg', {
      width: '18',
      height: '18',
      viewBox: '0 0 24 24',
      fill: 'none',
      stroke: 'currentColor',
      'stroke-width': '2',
      'stroke-linecap': 'round'
    }, [
      h('line', { x1: '4', y1: '8', x2: '20', y2: '8' }),
      h('line', { x1: '4', y1: '16', x2: '20', y2: '16' }),
      h('line', { x1: '4', y1: '8', x2: '4', y2: '16' }),
      h('line', { x1: '20', y1: '8', x2: '20', y2: '16' })
    ])
  }
})

// 斐波那契工具图标
const SvgFibonacci = defineComponent({
  setup() {
    return () => h('svg', {
      width: '18',
      height: '18',
      viewBox: '0 0 24 24',
      fill: 'none',
      stroke: 'currentColor',
      'stroke-width': '1.5'
    }, [
      h('path', { d: 'M5 5h14v14H5z' }),
      h('path', { d: 'M5 9h14M5 12h14M5 15h14' })
    ])
  }
})

// 几何形状图标
const SvgRectangle = defineComponent({
  setup() {
    return () => h('svg', {
      width: '18',
      height: '18',
      viewBox: '0 0 24 24',
      fill: 'none',
      stroke: 'currentColor',
      'stroke-width': '2'
    }, [
      h('rect', { x: '4', y: '4', width: '16', height: '16' })
    ])
  }
})

const SvgCircle = defineComponent({
  setup() {
    return () => h('svg', {
      width: '18',
      height: '18',
      viewBox: '0 0 24 24',
      fill: 'none',
      stroke: 'currentColor',
      'stroke-width': '2'
    }, [
      h('circle', { cx: '12', cy: '12', r: '8' })
    ])
  }
})

const SvgTriangle = defineComponent({
  setup() {
    return () => h('svg', {
      width: '18',
      height: '18',
      viewBox: '0 0 24 24',
      fill: 'none',
      stroke: 'currentColor',
      'stroke-width': '2',
      'stroke-linejoin': 'round'
    }, [
      h('path', { d: 'M12 4L20 20H4z' })
    ])
  }
})

// 注释工具图标
const SvgText = defineComponent({
  setup() {
    return () => h('svg', {
      width: '18',
      height: '18',
      viewBox: '0 0 24 24',
      fill: 'currentColor'
    }, [
      h('path', { d: 'M5 4v14h14V4H5zm2 2h10v2H7V6zm0 4h10v2H7v-2zm0 4h7v2H7v-2z' })
    ])
  }
})

const SvgPriceNote = defineComponent({
  setup() {
    return () => h('svg', {
      width: '18',
      height: '18',
      viewBox: '0 0 24 24',
      fill: 'currentColor'
    }, [
      h('path', { d: 'M4 4v12h12V4H4zm2 2h8v2H6V6zm0 4h8v2H6v-2z' }),
      h('text', {
        x: '10',
        y: '11',
        'text-anchor': 'middle',
        'font-size': '10',
        'font-weight': 'bold',
        fill: 'currentColor'
      }, '$')
    ])
  }
})

const SvgBrush = defineComponent({
  setup() {
    return () => h('svg', {
      width: '18',
      height: '18',
      viewBox: '0 0 24 24',
      fill: 'currentColor'
    }, [
      h('path', { d: 'M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25zM20.71 7.04c.39-.39.39-1.02 0-1.41l-2.34-2.34c-.39-.39-1.02-.39-1.41 0l-1.83 1.83 3.75 3.75 1.83-1.83z' })
    ])
  }
})

// 交易工具图标
const SvgLong = defineComponent({
  setup() {
    return () => h('svg', {
      width: '18',
      height: '18',
      viewBox: '0 0 24 24',
      fill: 'currentColor'
    }, [
      h('path', { d: 'M16 6l2.29 2.29-4.88 4.88-4-4L2 16.59 3.41 18l6-6 4 4 6.3-6.29L22 12V6z' })
    ])
  }
})

const SvgShort = defineComponent({
  setup() {
    return () => h('svg', {
      width: '18',
      height: '18',
      viewBox: '0 0 24 24',
      fill: 'currentColor'
    }, [
      h('path', { d: 'M16 18l2.29-2.29-4.88-4.88-4 4L2 7.41 3.41 6l6 6 4-4 6.3 6.29L22 12v6z' })
    ])
  }
})

const SvgMeasure = defineComponent({
  setup() {
    return () => h('svg', {
      width: '18',
      height: '18',
      viewBox: '0 0 24 24',
      fill: 'currentColor'
    }, [
      h('path', { d: 'M9 2l-2 6h6l-2-6H9zm-4 9l-1 3h10l-1-3H5zm8 4l1 3H8l1-3h4z' })
    ])
  }
})

// 缩放工具图标
const SvgZoomIn = defineComponent({
  setup() {
    return () => h('svg', {
      width: '18',
      height: '18',
      viewBox: '0 0 24 24',
      fill: 'currentColor'
    }, [
      h('path', { d: 'M15.5 14h-.79l-.28-.27C15.41 12.59 16 11.11 16 9.5 16 5.91 13.09 3 9.5 3S3 5.91 3 9.5 5.91 16 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z' }),
      h('path', { d: 'M12 10h-2v2H9v-2H7V9h2V7h1v2h2v1z' })
    ])
  }
})

const SvgZoomOut = defineComponent({
  setup() {
    return () => h('svg', {
      width: '18',
      height: '18',
      viewBox: '0 0 24 24',
      fill: 'currentColor'
    }, [
      h('path', { d: 'M15.5 14h-.79l-.28-.27C15.41 12.59 16 11.11 16 9.5 16 5.91 13.09 3 9.5 3S3 5.91 3 9.5 5.91 16 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z' }),
      h('path', { d: 'M7 9h5v1H7z' })
    ])
  }
})

// 操作工具图标
const SvgDelete = defineComponent({
  setup() {
    return () => h('svg', {
      width: '18',
      height: '18',
      viewBox: '0 0 24 24',
      fill: 'currentColor'
    }, [
      h('path', { d: 'M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z' })
    ])
  }
})

const SvgSettings = defineComponent({
  setup() {
    return () => h('svg', {
      width: '18',
      height: '18',
      viewBox: '0 0 24 24',
      fill: 'currentColor'
    }, [
      h('path', { d: 'M19.14 12.94c.04-.3.06-.61.06-.94 0-.32-.02-.64-.07-.94l2.03-1.58c.18-.14.23-.41.12-.61l-1.92-3.32c-.12-.22-.37-.29-.59-.22l-2.39.96c-.5-.38-1.03-.7-1.62-.94l-.36-2.54c-.04-.24-.24-.41-.48-.41h-3.84c-.24 0-.43.17-.47.41l-.36 2.54c-.59.24-1.13.57-1.62.94l-2.39-.96c-.22-.08-.47 0-.59.22L3.16 8.87c-.12.21-.08.47.12.61l2.03 1.58c-.05.3-.09.63-.09.94s.04.64.09.94l-2.03 1.58c-.18.14-.23.41-.12.61l1.92 3.32c.12.22.37.29.59.22l2.39-.96c.5.38 1.03.7 1.62.94l.36 2.54c.05.24.24.41.48.41h3.84c.24 0 .44-.17.47-.41l.36-2.54c.59-.24 1.13-.56 1.62-.94l2.39.96c.22.08.47 0 .59-.22l1.92-3.32c.12-.22.07-.47-.12-.61l-2.01-1.58zM12 15.6c-1.98 0-3.6-1.62-3.6-3.6s1.62-3.6 3.6-3.6 3.6 1.62 3.6 3.6-1.62 3.6-3.6 3.6z' })
    ])
  }
})

// 侧边栏图标
const SvgAdd = defineComponent({
  setup() {
    return () => h('svg', {
      width: '16',
      height: '16',
      viewBox: '0 0 24 24',
      fill: 'currentColor'
    }, [
      h('path', { d: 'M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z' })
    ])
  }
})

const SvgSort = defineComponent({
  setup() {
    return () => h('svg', {
      width: '16',
      height: '16',
      viewBox: '0 0 24 24',
      fill: 'currentColor'
    }, [
      h('path', { d: 'M3 18h6v-2H3v2zM3 6v2h18V6H3zm0 7h12v-2H3v2z' })
    ])
  }
})

const SvgRefresh = defineComponent({
  setup() {
    return () => h('svg', {
      width: '14',
      height: '14',
      viewBox: '0 0 24 24',
      fill: 'currentColor'
    }, [
      h('path', { d: 'M17.65 6.35C16.2 4.9 14.21 4 12 4c-4.42 0-7.99 3.58-7.99 8s3.57 8 7.99 8c3.73 0 6.84-2.55 7.73-6h-2.08c-.82 2.33-3.04 4-5.65 4-3.31 0-6-2.69-6-6s2.69-6 6-6c1.66 0 3.14.69 4.22 1.78L13 11h7V4l-2.35 2.35z' })
    ])
  }
})

// ==================== 图标映射表 ====================

const iconMap: Record<string, Component> = {
  'cursor': SvgCursor,
  'crosshair': SvgCrosshair,
  'trend-line': SvgTrendLine,
  'price-line': SvgPriceLine,
  'vertical-line': SvgVerticalLine,
  'ray-line': SvgRayLine,
  'parallel-channel': SvgParallelChannel,
  'fibonacci': SvgFibonacci,
  'rectangle': SvgRectangle,
  'circle': SvgCircle,
  'triangle': SvgTriangle,
  'text': SvgText,
  'price-note': SvgPriceNote,
  'brush': SvgBrush,
  'long': SvgLong,
  'short': SvgShort,
  'measure': SvgMeasure,
  'zoom-in': SvgZoomIn,
  'zoom-out': SvgZoomOut,
  'delete': SvgDelete,
  'settings': SvgSettings,
  'add': SvgAdd,
  'sort': SvgSort,
  'refresh': SvgRefresh,
}

// ==================== 组件 Props ====================

interface Props {
  icon: string
}

const props = defineProps<Props>()

// 获取对应的图标组件
const iconComponent = iconMap[props.icon] || SvgCursor
</script>

<script lang="ts">
// 导出所有可用图标名称，供外部使用
export const AVAILABLE_ICONS = Object.keys({
  cursor: '光标',
  crosshair: '十字准星',
  'trend-line': '趋势线',
  'price-line': '水平线',
  'vertical-line': '垂直线',
  'ray-line': '射线',
  'parallel-channel': '平行通道',
  fibonacci: '斐波那契回撤',
  rectangle: '矩形',
  circle: '圆形',
  triangle: '三角形',
  text: '文本',
  'price-note': '价格注释',
  brush: '画笔',
  long: '做多',
  short: '做空',
  measure: '测量',
  'zoom-in': '放大',
  'zoom-out': '缩小',
  delete: '清除标注',
  settings: '设置',
  add: '添加',
  sort: '排序',
  refresh: '刷新',
})
</script>

<template>
  <div class="drawing-toolbar">
    <!-- 工具组 -->
    <div v-for="group in toolGroups" :key="group.id" class="tool-group">
      <!-- 工具组标题（可折叠） -->
      <div class="group-header" @click="toggleGroup(group.id)">
        <span class="group-title">{{ group.title }}</span>
        <span class="group-toggle" :class="{ expanded: isGroupExpanded(group.id) }">▼</span>
      </div>

      <!-- 工具按钮列表 -->
      <div v-show="isGroupExpanded(group.id)" class="group-content">
        <button
          v-for="tool in group.tools"
          :key="tool.id"
          :class="['tool-btn', { active: activeTool === tool.id }]"
          :data-tool="tool.id"
          :data-category="tool.category"
          @click="selectTool(tool.id)"
          :title="tool.name"
        >
          <svg v-html="tool.svg" width="18" height="18" viewBox="0 0 24 24"></svg>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import type { DrawingTool } from '../drawing-tools/types'

// 工具栏折叠状态
const expandedGroups = ref<Set<string>>(new Set(['basic', 'drawing', 'trading']))

// 切换工具组展开/折叠
const toggleGroup = (groupId: string) => {
  if (expandedGroups.value.has(groupId)) {
    expandedGroups.value.delete(groupId)
  } else {
    expandedGroups.value.add(groupId)
  }
  // 强制触发响应式更新
  expandedGroups.value = new Set(expandedGroups.value)
}

// 判断工具组是否展开
const isGroupExpanded = (groupId: string) => expandedGroups.value.has(groupId)

// 基础工具 - 使用TradingView官方SVG图标
const basicTools: DrawingTool[] = [
  {
    id: 'cursor',
    name: '光标',
    icon: 'cursor',
    svg: '<path fill="currentColor" d="M7 2l12 11.2-5.8 .5 3.3 7.3 1.3-7.3 -7.3 5.8-.5z"/>',
    category: 'basic'
  },
  {
    id: 'crosshair',
    name: '十字准星',
    icon: 'crosshair',
    svg: '<path fill="currentColor" d="M11 2v7H4v2h7v7h2v-7h7V9h-7V2z"/>',
    category: 'basic'
  },
]

// 趋势线工具 - 根据 TradingView 官方文档
const trendLineTools: DrawingTool[] = [
  {
    id: 'trend-line',
    name: '趋势线',
    icon: 'trend-line',
    svg: '<path fill="currentColor" d="M4.5 16.5l3-3 2.5 2.5 7.5-7.5 1.5 1.5-9 9-2.5-2.5-3 3z"/>',
    category: 'trendline'
  },
  {
    id: 'price-line',
    name: '水平线',
    icon: 'horizontal-line',
    svg: '<path fill="currentColor" d="M4 11h16v2H4z"/>',
    category: 'trendline'
  },
  {
    id: 'vertical-line',
    name: '垂直线',
    icon: 'vertical-line',
    svg: '<path fill="currentColor" d="M11 4h2v16h-2z"/>',
    category: 'trendline'
  },
  {
    id: 'ray-line',
    name: '射线',
    icon: 'ray-line',
    svg: '<path fill="currentColor" d="M4 12h13v2H4z"/>',
    category: 'trendline'
  },
  {
    id: 'parallel-channel',
    name: '平行通道',
    icon: 'parallel-channel',
    svg: '<path fill="currentColor" d="M4 6v12h16V6H4zm14 10H6V8h12v8z"/>',
    category: 'trendline'
  },
]

// 斐波那契工具
const fibonacciTools: DrawingTool[] = [
  {
    id: 'fibonacci',
    name: '斐波那契回撤',
    icon: 'fibonacci',
    svg: '<path fill="none" stroke="currentColor" stroke-width="1.5" d="M5 5v14h14V5H5zm2 2h10v10H7V7z M7 9h10M7 11h10M7 13h10M7 15h10"/>',
    category: 'fibonacci'
  },
  {
    id: 'fibonacci-channel',
    name: '斐波那契通道',
    icon: 'fibonacci-channel',
    svg: '<path fill="none" stroke="currentColor" stroke-width="1.5" d="M4 8h16M4 12h16M4 16h16"/>',
    category: 'fibonacci'
  },
]

// ⚠️ 已移除形状工具（矩形、圆形、三角形）
// 这些不是专业股票交易工具，保留专业绘图工具（趋势线、斐波那契等）
const shapeTools: DrawingTool[] = []

// 注释工具
const annotationTools: DrawingTool[] = [
  {
    id: 'text',
    name: '文本',
    icon: 'text',
    svg: '<path fill="currentColor" d="M5 4v14h14V4H5zm12 12H7V6h10v10z"/><text x="12" y="15" text-anchor="middle" font-size="8" fill="currentColor">T</text>',
    category: 'annotation'
  },
  {
    id: 'price-note',
    name: '价格注释',
    icon: 'price-note',
    svg: '<path fill="currentColor" d="M4 4v12h12V4H4zm10 10H6V6h8v8z"/><text x="10" y="11" text-anchor="middle" font-size="6" fill="currentColor">$</text>',
    category: 'annotation'
  },
  {
    id: 'brush',
    name: '画笔',
    icon: 'brush',
    svg: '<path fill="currentColor" d="M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25zM20.71 7.04c.39-.39.39-1.02 0-1.41l-2.34-2.34c-.39-.39-1.02-.39-1.41 0l-1.83 1.83 3.75 3.75 1.83-1.83z"/>',
    category: 'annotation'
  },
]

// 交易工具（做多/做空）
const tradingTools: DrawingTool[] = [
  {
    id: 'long',
    name: '做多',
    icon: 'trend-up',
    svg: '<path fill="currentColor" d="M16 6l2.29 2.29-4.88 4.88-4-4L2 16.59 3.41 18l6-6 4 4 6.3-6.29L22 12V6z"/>',
    category: 'trading'
  },
  {
    id: 'short',
    name: '做空',
    icon: 'trend-down',
    svg: '<path fill="currentColor" d="M16 18l2.29-2.29-4.88-4.88-4 4L2 7.41 3.41 6l6 6 4-4 6.3 6.29L22 12v6z"/>',
    category: 'trading'
  },
  {
    id: 'measure',
    name: '测量',
    icon: 'measure',
    svg: '<path fill="currentColor" d="M9 2l-2 6h6l-2-6H9zm-4 9l-1 3h10l-1-3H5zm8 4l1 3H8l1-3h4z"/>',
    category: 'trading'
  },
]

// 缩放工具
const zoomTools: DrawingTool[] = [
  {
    id: 'zoom-in',
    name: '放大',
    icon: 'zoom-in',
    svg: '<path fill="currentColor" d="M15.5 14h-.79l-.28-.27C15.41 12.59 16 11.11 16 9.5 16 5.91 13.09 3 9.5 3S3 5.91 3 9.5 5.91 16 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/> <path d="M12 10h-2v2H9v-2H7V9h2V7h1v2h2v1z"/>',
    category: 'zoom'
  },
  {
    id: 'zoom-out',
    name: '缩小',
    icon: 'zoom-out',
    svg: '<path fill="currentColor" d="M15.5 14h-.79l-.28-.27C15.41 12.59 16 11.11 16 9.5 16 5.91 13.09 3 9.5 3S3 5.91 3 9.5 5.91 16 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/> <path d="M7 9h5v1H7z"/>',
    category: 'zoom'
  },
]

// 操作工具
const actionTools: DrawingTool[] = [
  {
    id: 'delete',
    name: '清除标注',
    icon: 'delete',
    svg: '<path fill="currentColor" d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/>',
    category: 'other'
  },
  {
    id: 'settings',
    name: '设置',
    icon: 'settings',
    svg: '<path fill="currentColor" d="M19.14 12.94c.04-.3.06-.61.06-.94 0-.32-.02-.64-.07-.94l2.03-1.58c.18-.14.23-.41.12-.61l-1.92-3.32c-.12-.22-.37-.29-.59-.22l-2.39.96c-.5-.38-1.03-.7-1.62-.94l-.36-2.54c-.04-.24-.24-.41-.48-.41h-3.84c-.24 0-.43.17-.47.41l-.36 2.54c-.59.24-1.13.57-1.62.94l-2.39-.96c-.22-.08-.47 0-.59.22L3.16 8.87c-.12.21-.08.47.12.61l2.03 1.58c-.05.3-.09.63-.09.94s.04.64.09.94l-2.03 1.58c-.18.14-.23.41-.12.61l1.92 3.32c.12.22.37.29.59.22l2.39-.96c.5.38 1.03.7 1.62.94l.36 2.54c.05.24.24.41.48.41h3.84c.24 0 .44-.17.47-.41l.36-2.54c.59-.24 1.13-.56 1.62-.94l2.39.96c.22.08.47 0 .59-.22l1.92-3.32c.12-.22.07-.47-.12-.61l-2.01-1.58zM12 15.6c-1.98 0-3.6-1.62-3.6-3.6s1.62-3.6 3.6-3.6 3.6 1.62 3.6 3.6-1.62 3.6-3.6 3.6z"/>',
    category: 'other'
  },
]

// 工具组定义 - 移除形状工具，只保留专业股票工具
const toolGroups = [
  { id: 'basic', title: '基础', tools: basicTools },
  { id: 'drawing', title: '绘图', tools: [...trendLineTools, ...fibonacciTools] },
  { id: 'annotation', title: '注释', tools: annotationTools },
  { id: 'trading', title: '交易', tools: tradingTools },
  { id: 'zoom', title: '缩放', tools: zoomTools },
  { id: 'other', title: '其他', tools: actionTools },
]

const activeTool = ref('cursor')

const emit = defineEmits<{
  toolChange: [tool: string]
}>()

const selectTool = (toolId: string) => {
  activeTool.value = toolId
  emit('toolChange', toolId)
}
</script>

<style scoped lang="scss">
// TradingView 官方样式 - 紧凑版，支持折叠
.drawing-toolbar {
  position: absolute;
  left: 6px;
  top: 56px;
  display: flex;
  flex-direction: column;
  gap: 2px;
  z-index: 100;
  padding: 3px;
  background: #131722; // TradingView 官方深色背景
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
  max-height: calc(100vh - 80px);
  max-width: 42px; // ✅ 限制最大宽度，确保不覆盖图表
  overflow-y: auto;

  // ✅ 确保工具栏只在自己的区域内接收鼠标事件
  pointer-events: auto;

  // 自定义滚动条
  &::-webkit-scrollbar {
    width: 4px;
  }

  &::-webkit-scrollbar-track {
    background: #131722;
  }

  &::-webkit-scrollbar-thumb {
    background: #2a2e39;
    border-radius: 2px;

    &:hover {
      background: #363a45;
    }
  }

  .tool-group {
    display: flex;
    flex-direction: column;
    padding: 2px 0;

    &:not(:last-child) {
      border-bottom: 1px solid #2a2e39;
      padding-bottom: 3px;
      margin-bottom: 2px;
    }
  }

  // 工具组标题
  .group-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 4px 6px;
    cursor: pointer;
    user-select: none;
    transition: background 0.15s ease;
    border-radius: 3px;

    &:hover {
      background: #1e222d;
    }

    .group-title {
      font-size: 10px;
      font-weight: 600;
      color: #787b86;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }

    .group-toggle {
      font-size: 8px;
      color: #787b86;
      transition: transform 0.2s ease;

      &.expanded {
        transform: rotate(180deg);
      }
    }
  }

  // 工具按钮列表
  .group-content {
    display: flex;
    flex-direction: column;
    gap: 1px;
    padding: 2px 0;
    animation: slideDown 0.2s ease;
  }

  @keyframes slideDown {
    from {
      opacity: 0;
      transform: translateY(-5px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

  .tool-btn {
    width: 32px;
    height: 32px;
    background: transparent;
    border: none;
    color: #d1d4dc; // TradingView 官方图标颜色
    border-radius: 3px;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.1s ease;
    position: relative;
    padding: 0;
    margin: 0 auto;

    &:hover {
      background: #1e222d;
    }

    &.active {
      background: #2962ff;
      color: #ffffff;

      &::before {
        content: '';
        position: absolute;
        left: 0;
        top: 50%;
        transform: translateY(-50%);
        width: 3px;
        height: 18px;
        background: #ffffff;
        border-radius: 0 2px 2px 0;
      }
    }

    svg {
      width: 18px;
      height: 18px;
      fill: currentColor;
      stroke: currentColor;
      stroke-width: 0;
    }

    // 趋势线工具特殊颜色
    &[data-category="trendline"] {
      &[data-tool="trend-line"]:hover,
      &[data-tool="trend-line"].active {
        color: #2962ff;
      }

      &[data-tool="price-line"]:hover,
      &[data-tool="price-line"].active {
        color: #9C27B0;
      }

      &[data-tool="vertical-line"]:hover,
      &[data-tool="vertical-line"].active {
        color: #FF5722;
      }

      &[data-tool="ray-line"]:hover,
      &[data-tool="ray-line"].active {
        color: #00BCD4;
      }

      &[data-tool="parallel-channel"]:hover,
      &[data-tool="parallel-channel"].active {
        color: #3F51B5;
      }
    }

    // 斐波那契工具特殊颜色
    &[data-category="fibonacci"] {
      &:hover,
      &.active {
        color: #FF9800;
      }
    }

    // 交易工具特殊颜色
    &[data-category="trading"] {
      &[data-tool="long"]:hover,
      &[data-tool="long"].active {
        color: #26A69A;
      }

      &[data-tool="short"]:hover,
      &[data-tool="short"].active {
        color: #EF5350;
      }

      &[data-tool="measure"]:hover,
      &[data-tool="measure"].active {
        color: #FFC107;
      }
    }

    // 注释工具特殊颜色
    &[data-category="annotation"] {
      &[data-tool="text"]:hover,
      &[data-tool="text"].active {
        color: #795548;
      }

      &[data-tool="price-note"]:hover,
      &[data-tool="price-note"].active {
        color: #607D8B;
      }

      &[data-tool="brush"]:hover,
      &[data-tool="brush"].active {
        color: #E91E63;
      }
    }

    // 激活状态下，特定颜色覆盖
    &[data-category="trendline"][data-tool="trend-line"].active {
      background: #2962ff;
    }

    &[data-category="trendline"][data-tool="price-line"].active {
      background: #9C27B0;
    }

    &[data-category="trendline"][data-tool="vertical-line"].active {
      background: #FF5722;
    }

    &[data-category="trendline"][data-tool="ray-line"].active {
      background: #00BCD4;
    }

    &[data-category="trendline"][data-tool="parallel-channel"].active {
      background: #3F51B5;
    }

    &[data-category="fibonacci"].active {
      background: #FF9800;
    }

    &[data-category="trading"][data-tool="long"].active {
      background: #26A69A;
    }

    &[data-category="trading"][data-tool="short"].active {
      background: #EF5350;
    }

    &[data-category="trading"][data-tool="measure"].active {
      background: #FFC107;
    }

    &[data-category="annotation"][data-tool="text"].active {
      background: #795548;
    }

    &[data-category="annotation"][data-tool="price-note"].active {
      background: #607D8B;
    }

    &[data-category="annotation"][data-tool="brush"].active {
      background: #E91E63;
    }

    // 所有激活状态的左侧指示条
    &.active::before {
      background: #ffffff;
    }
  }
}
</style>

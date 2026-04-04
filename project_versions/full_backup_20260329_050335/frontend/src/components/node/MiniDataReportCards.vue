<template>
  <div class="mini-data-report-cards">
    <div
      v-for="card in visibleCards"
      :key="card.key"
      class="mini-report-card"
    >
      <div class="mini-report-icon" :class="getIconClass(card)">
        <font-awesome-icon :icon="card.icon" />
      </div>
      <div class="mini-report-content">
        <div class="mini-report-label">{{ card.label }}</div>
        <div class="mini-report-value-small">{{ card.value }}</div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, watch } from 'vue'
import { miniReportConfig as stockMiniReportConfig } from '../../research-nodes/StockSelectionNode'
import { miniReportConfig as indexMiniReportConfig } from '../../research-nodes/IndexSelectionNode'

interface CardData {
  key: string
  label: string
  value: string
  icon: string
  iconClass: string | ((metadata: any) => string)
  cardClass?: string | Record<string, boolean> | ((metadata: any) => string)
}

const props = defineProps<{
  nodeType: string
  metadata?: {
    totalDataPoints?: number
    startDate?: string
    endDate?: string
    successCount?: number
    totalCount?: number
    frequencies?: string[]
    frequenciesLabel?: string
    frequency?: string
    [key: string]: any
  }
  params?: {
    frequency?: string
    frequencies?: string[]
    [key: string]: any
  }
  frequencies?: string[] // 🔧 直接传递的 frequencies 数组
  content?: any // 节点数据内容，用于计算股票/指数数量
}>()

// 根据节点类型选择配置
const config = computed(() => {
  switch (props.nodeType) {
    case 'stock-selection':
      return stockMiniReportConfig
    case 'index-selection':
      return indexMiniReportConfig
    default:
      return null
  }
})

// 获取图标容器的 class
const getIconClass = (card: CardData) => {
  if (typeof card.iconClass === 'function') {
    return card.iconClass(props.metadata)
  }
  return card.iconClass || ''
}

// 监听 props 变化
watch(() => props.params, (newParams) => {
  if (!newParams) return

  // 仅在调试模式下输出
  if (import.meta.env.DEV) {
    console.log('[MiniDataReportCards] params changed:', newParams)
  }
}, { deep: true, immediate: false })

// 计算可见卡片
const visibleCards = computed((): CardData[] => {
  if (!config.value) return []

  return config.value.cards
    .map(cardConfig => {
      let value = '--'
      let icon = cardConfig.icon
      try {
        // 🔧 构建一个增强的 params 对象，优先使用直接传递的 frequencies
        const enhancedParams = {
          ...props.params,
          frequencies: props.frequencies || props.params?.frequencies
        }

        // 调用卡片配置中的函数获取值（传入 metadata, content, params）
        value = cardConfig.getValue(props.metadata, props.content, enhancedParams)

        // 🔧 状态卡片：根据成功/失败动态更改图标
        if (cardConfig.key === 'status' && props.metadata) {
          const success = props.metadata.successCount || 0
          const total = props.metadata.totalCount || 0
          if (total === 0) {
            icon = 'clock'  // 待获取图标（黄色警告）
          } else if (success === total) {
            icon = 'check-circle'  // 成功图标（绿色）
          } else {
            icon = 'times-circle'  // 失败图标（红色）
          }
        }
      } catch (e) {
        console.error('[MiniDataReportCards] Error getting value for card:', cardConfig.key, e)
      }
      return {
        ...cardConfig,
        icon,
        value
      }
    })
    .filter(card => {
      // 过滤掉值为空或 '--' 的卡片
      return card.value && card.value !== '--' && card.value !== '0' && card.value !== '0只' && card.value !== '0个'
    })
})
</script>

<style scoped>
/* 小组件卡片样式 - 深色主题 */
.mini-data-report-cards {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 6px;
  padding: 8px;
  background: transparent;
  border-radius: 6px;
}

.mini-report-card {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 8px;
  background: rgba(26, 26, 46, 0.9);
  border-radius: 4px;
  border: none;
  transition: all 0.2s ease;
}

.mini-report-card:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
  transform: translateY(-1px);
  background: rgba(26, 26, 46, 1);
}

.mini-report-card .mini-report-label,
.mini-report-card .mini-report-value-small {
  color: white;
}

/* 图标渐变色背景 */
.mini-report-icon.primary-gradient {
  background: linear-gradient(135deg, #2962ff 0%, #764ba2 100%);
}

.mini-report-icon.success-gradient {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
}

.mini-report-icon.purple-gradient {
  background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
}

.mini-report-icon.info-gradient {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
}

.mini-report-icon.warning-gradient {
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
}

.mini-report-icon.danger-gradient {
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
}

.mini-report-icon {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  font-size: 12px;
  flex-shrink: 0;
}

/* 确保图标在渐变背景上清晰可见 */
.mini-report-icon :deep(svg) {
  color: #ffffff;
  filter: drop-shadow(0 1px 2px rgba(0, 0, 0, 0.3));
}

.mini-report-content {
  flex: 1;
  min-width: 0;
}

.mini-report-label {
  font-size: 10px;
  color: rgba(255, 255, 255, 0.8);
  margin-bottom: 2px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.mini-report-value-small {
  font-size: 11px;
  font-weight: 600;
  color: white;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
</style>

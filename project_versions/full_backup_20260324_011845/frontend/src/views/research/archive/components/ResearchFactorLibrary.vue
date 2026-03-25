<!-- ResearchFactorLibrary.vue - 因子库面板组件 -->
<template>
  <aside class="panel factor-panel">
    <div class="panel-header">
      <span class="panel-title">
        <svg class="icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
        </svg>
        {{ isZh ? '因子库' : 'Factor Library' }}
      </span>
      <div class="panel-actions">
        <button class="icon-btn" @click="handleAddCustomFactor" :title="isZh ? '添加自定义因子' : 'Add Custom Factor'">
          <svg class="icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="12" y1="5" x2="12" y2="19"/>
            <line x1="5" y1="12" x2="19" y2="12"/>
          </svg>
        </button>
        <button class="icon-btn" @click="handleOpenSettings" :title="isZh ? '设置' : 'Settings'">
          <svg class="icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="3"/>
            <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/>
          </svg>
        </button>
      </div>
    </div>
    <div class="factor-list">
      <div
        v-for="factor in factorLibrary"
        :key="factor.name"
        :class="['factor-item', { selected: selectedFactor === factor.name }]"
        @click="handleSelectFactor(factor)"
      >
        <div class="factor-header">
          <div class="factor-name">
            <span class="factor-status-dot" :class="getFactorStatus(factor.ic ?? undefined)"></span>
            {{ factor.name }}
          </div>
          <div class="factor-score" :class="getFactorScoreClass(factor.ic ?? undefined)">
            <svg class="icon-xs" viewBox="0 0 24 24" fill="currentColor">
              <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
            </svg>
            {{ factor.ic?.toFixed(2) ?? 'N/A' }}
          </div>
        </div>
        <div class="factor-type">
          <span class="type-tag">{{ factor.category }}</span>
          <span class="type-separator">•</span>
          {{ isZh ? factor.typeZh : factor.type }}
        </div>
        <div class="factor-metrics">
          <span class="metric">
            <svg class="icon-xs" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M23 18l-9.5-9.5-5 5L1 6"/>
            </svg>
            IC: <span :class="['metric-value', { positive: (factor.ic ?? 0) > 0.03, negative: (factor.ic ?? 0) < 0 }]">{{ factor.ic?.toFixed(3) ?? 'N/A' }}</span>
          </span>
          <span class="metric">
            <svg class="icon-xs" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10"/>
              <polyline points="12 6 12 12 16 14"/>
            </svg>
            IR: <span :class="['metric-value', { positive: (factor.ir ?? 0) > 0.5 }]">{{ factor.ir?.toFixed(2) ?? 'N/A' }}</span>
          </span>
        </div>
      </div>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { PropType } from 'vue'
import type { FactorInfo } from '@/api/modules/research'

/**
 * 因子库面板组件
 * 显示和管理因子库中的所有因子
 */
defineProps({
  /** 因子库数据列表 */
  factorLibrary: {
    type: Array as PropType<(FactorInfo & { typeZh?: string })[]>,
    required: true
  },
  /** 当前选中的因子名称 */
  selectedFactor: {
    type: String as PropType<string | null>,
    default: null
  },
  /** 是否显示中文 */
  isZh: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits<{
  /** 选中因子事件 */
  'select-factor': [factor: FactorInfo]
  /** 添加自定义因子事件 */
  'add-custom-factor': []
  /** 打开设置事件 */
  'open-settings': []
}>()

/**
 * 处理选择因子
 */
const handleSelectFactor = (factor: FactorInfo) => {
  emit('select-factor', factor)
}

/**
 * 处理添加自定义因子
 */
const handleAddCustomFactor = () => {
  emit('add-custom-factor')
}

/**
 * 处理打开设置
 */
const handleOpenSettings = () => {
  emit('open-settings')
}

/**
 * 获取因子状态
 * @param ic - IC值
 * @returns 状态类名
 */
const getFactorStatus = (ic: number | undefined): string => {
  if (ic === undefined) return 'unknown'
  if (ic >= 0.05) return 'excellent'
  if (ic >= 0.03) return 'good'
  if (ic >= 0) return 'average'
  return 'poor'
}

/**
 * 获取因子评分类名
 * @param ic - IC值
 * @returns 评分类名
 */
const getFactorScoreClass = (ic: number | undefined): string => {
  return getFactorStatus(ic)
}
</script>

<style scoped lang="scss">
/* 面板标题带图标 */
.panel-title {
  display: flex;
  align-items: center;
  gap: 8px;
}

/* 因子列表 */
.factor-list {
  flex: 1;
  overflow-y: auto;
}

.factor-item {
  padding: 12px 16px;
  border-bottom: 1px solid var(--border-color);
  cursor: pointer;
  transition: background 0.15s;
}

.factor-item:hover {
  background: var(--bg-secondary);
}

.factor-item.selected {
  background: var(--bg-secondary);
}

/* 因子头部 */
.factor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}

.factor-name {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 4px;
  display: flex;
  align-items: center;
}

/* 因子状态点 */
.factor-status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  margin-right: 8px;
}

.factor-status-dot.excellent {
  background: var(--color-up);  /* 红色 - 极好 */
  box-shadow: 0 0 6px var(--color-up);
}

.factor-status-dot.good {
  background: var(--accent-orange);
}

.factor-status-dot.average {
  background: var(--text-secondary);
}

.factor-status-dot.poor {
  background: var(--color-down);  /* 绿色 - 差 */
}

/* 因子评分 */
.factor-score {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  font-weight: 700;
}

.factor-score.excellent {
  color: var(--color-up);  /* 红色 - 极好 */
}

.factor-score.good {
  color: var(--accent-orange);
}

.factor-score.average {
  color: var(--text-secondary);
}

.factor-score.poor {
  color: var(--color-down);  /* 绿色 - 差 */
}

/* 因子类型 */
.factor-type {
  font-size: 10px;
  color: var(--text-secondary);
  margin-bottom: 8px;
}

.type-tag {
  display: inline-block;
  padding: 2px 6px;
  background: var(--bg-tertiary);
  border-radius: 3px;
  font-size: 10px;
  font-weight: 600;
  color: var(--accent-blue);
}

.type-separator {
  margin: 0 6px;
  color: var(--text-secondary);
}

/* 因子指标 */
.factor-metrics {
  display: flex;
  gap: 12px;
  font-size: 11px;
}

.metric {
  display: flex;
  align-items: center;
  gap: 4px;
  color: var(--text-secondary);
}

.metric-value {
  font-weight: 600;
  color: var(--text-primary);
}

/* A股规则：红涨/好，绿跌/坏 */
.metric-value.positive {
  color: var(--color-up);  /* 红色 - 正面 */
}

.metric-value.negative {
  color: var(--color-down);  /* 绿色 - 负面 */
}

/* 滚动条样式 */
.factor-list::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

.factor-list::-webkit-scrollbar-track {
  background: var(--bg-primary);
}

.factor-list::-webkit-scrollbar-thumb {
  background: var(--bg-tertiary);
  border-radius: 3px;
}

.factor-list::-webkit-scrollbar-thumb:hover {
  background: #363a45;
}
</style>

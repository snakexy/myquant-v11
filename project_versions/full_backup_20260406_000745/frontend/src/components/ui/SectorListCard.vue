<template>
  <div class="sector-list-card" :class="type">
    <div class="sector-header" :class="headerClass">
      <span v-html="iconSvg"></span>
      {{ title }}
    </div>
    <div class="sector-list">
      <div
        v-for="(item, index) in items"
        :key="item.code || index"
        class="sector-item"
        :class="{ 'my-sector': type === 'my' }"
      >
        <span v-if="showRank" class="sector-rank">{{ index + 1 }}</span>
        <span class="sector-name">{{ item.name }}</span>
        <span v-if="item.weight !== undefined" class="sector-weight">{{ (item.weight * 100).toFixed(0) }}%</span>
        <span class="sector-change" :class="getChangeClass(item.change)">
          {{ formatChange(item.change) }}
        </span>
      </div>
    </div>
    <div v-if="type === 'my' && summary" class="sector-summary">
      {{ summary }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface SectorItem {
  name: string
  code?: string
  change: number
  weight?: number
}

interface Props {
  items: SectorItem[]
  type: 'gainers' | 'losers' | 'my'
  title: string
  icon: string
  showRank?: boolean
  summary?: string
  isZh?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  showRank: true,
  isZh: true
})

const iconSvg = computed(() => props.icon)

const headerClass = computed(() => {
  if (props.type === 'gainers') return 'up'
  if (props.type === 'losers') return 'down'
  return 'highlight'
})

const getChangeClass = (change: number): string => {
  if (change > 0) return 'positive'
  if (change < 0) return 'negative'
  return ''
}

const formatChange = (change: number): string => {
  const prefix = change > 0 ? '+' : ''
  return `${prefix}${(change * 100).toFixed(2)}%`
}
</script>

<style lang="scss" scoped>
.sector-list-card {
  background: var(--bg-secondary, #1e222d);
  border-radius: 8px;
  border: 1px solid var(--border-color, #2a2e39);
  overflow: hidden;
}

.sector-header {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 12px;
  font-size: 12px;
  font-weight: 600;
  background: var(--bg-tertiary, #2a2e39);

  :deep(svg) {
    width: 14px;
    height: 14px;
  }

  &.up {
    color: #f44336;
    background: rgba(244, 67, 54, 0.1);
  }

  &.down {
    color: #26a69a;
    background: rgba(38, 166, 154, 0.1);
  }

  &.highlight {
    color: #2962ff;
    background: rgba(41, 98, 255, 0.1);
  }
}

.sector-list {
  padding: 8px 0;
}

.sector-item {
  display: flex;
  align-items: center;
  padding: 6px 12px;
  font-size: 12px;
  transition: background 0.15s;

  &:hover {
    background: rgba(255, 255, 255, 0.03);
  }

  &.my-sector {
    .sector-name {
      flex: 1;
    }
    .sector-weight {
      color: var(--text-secondary, #787b86);
      font-size: 11px;
      min-width: 28px;
      text-align: right;
    }
  }
}

.sector-rank {
  width: 18px;
  height: 18px;
  border-radius: 4px;
  background: var(--bg-tertiary, #2a2e39);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 10px;
  font-weight: 600;
  color: var(--text-muted, #787b86);
  flex-shrink: 0;
}

.sector-name {
  flex: 1;
  color: var(--text-primary, #d1d4dc);
}

.sector-change {
  font-weight: 600;
  font-size: 11px;

  &.positive {
    color: #ef5350;
  }

  &.negative {
    color: #26a69a;
  }
}

.sector-summary {
  padding: 8px 12px;
  font-size: 11px;
  color: var(--text-muted, #787b86);
  border-top: 1px solid var(--border-color, #2a2e39);

  .highlight-text {
    color: var(--accent-blue, #409EFF);
    font-weight: 500;
  }
}
</style>

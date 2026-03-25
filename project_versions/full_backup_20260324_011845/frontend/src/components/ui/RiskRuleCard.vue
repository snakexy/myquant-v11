<template>
  <div class="risk-rule-card">
    <div class="rule-card-header">
      <span class="rule-card-name">{{ rule.rule_name }}</span>
      <label class="switch">
        <input type="checkbox" :checked="rule.enabled" @change="handleToggle" />
        <span class="slider"></span>
      </label>
    </div>
    <div class="rule-card-body">
      <div class="rule-meta">
        <span class="rule-type-tag">{{ ruleTypeText }}</span>
        <span class="rule-id">{{ rule.rule_id }}</span>
      </div>
      <div class="rule-params">
        <template v-for="(value, key) in rule.params" :key="key">
          <div class="param-item">
            <span class="param-key">{{ formatKey(key) }}:</span>
            <span class="param-value">{{ formatValue(value) }}</span>
          </div>
        </template>
      </div>
    </div>
    <div class="rule-card-footer">
      <button class="btn-icon" @click="$emit('edit', rule)" :title="editTitle">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
          <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
        </svg>
      </button>
      <button class="btn-icon" @click="$emit('backtest', rule)" :title="backtestTitle">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline>
        </svg>
      </button>
      <button class="btn-icon danger" @click="$emit('delete', rule)" :title="deleteTitle">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polyline points="3 6 5 6 21 6"></polyline>
          <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
        </svg>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Rule {
  rule_id: string
  rule_name: string
  rule_type: string
  params: Record<string, any>
  enabled: boolean
  triggerCount?: number
}

interface Props {
  rule: Rule
  isZh?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  isZh: true
})

const emit = defineEmits<{
  toggle: [rule: Rule]
  edit: [rule: Rule]
  backtest: [rule: Rule]
  delete: [rule: Rule]
}>()

const ruleTypeText = computed(() => {
  const typeMap: Record<string, string> = {
    position_limit: '仓位限制',
    single_position_limit: '单票限制',
    drawdown_limit: '回撤限制',
    loss_limit: '亏损限制',
    volatility_limit: '波动率限制',
    concentration_limit: '集中度限制'
  }
  return typeMap[props.rule.rule_type] || props.rule.rule_type
})

const editTitle = computed(() => props.isZh ? '编辑' : 'Edit')
const backtestTitle = computed(() => props.isZh ? '回测' : 'Backtest')
const deleteTitle = computed(() => props.isZh ? '删除' : 'Delete')

const formatKey = (key: string): string => {
  const keyMap: Record<string, string> = {
    max_ratio: '最大比例',
    max_drawdown: '最大回撤',
    max_daily_loss: '日亏损上限',
    min_cash: '最低现金',
    max_volatility: '最大波动率'
  }
  return keyMap[key] || key
}

const formatValue = (value: any): string => {
  if (typeof value === 'number') {
    return (value * 100).toFixed(1) + '%'
  }
  return String(value)
}

const handleToggle = (event: Event) => {
  const target = event.target as HTMLInputElement
  emit('toggle', { ...props.rule, enabled: target.checked })
}
</script>

<style lang="scss" scoped>
.risk-rule-card {
  background: var(--bg-secondary, #1e222d);
  border: 1px solid var(--border-color, #2a2e39);
  border-radius: 8px;
  overflow: hidden;
  transition: all 0.2s ease;

  &:hover {
    border-color: var(--accent-blue, #409EFF);
    box-shadow: 0 2px 8px rgba(64, 158, 255, 0.15);
  }
}

.rule-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid var(--border-color, #2a2e39);
}

.rule-card-name {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary, #d1d4dc);
}

.rule-card-body {
  padding: 12px 16px;
}

.rule-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.rule-type-tag {
  display: inline-flex;
  align-items: center;
  padding: 2px 8px;
  font-size: 11px;
  font-weight: 500;
  color: var(--accent-blue, #409EFF);
  background: rgba(64, 158, 255, 0.15);
  border-radius: 4px;
}

.rule-id {
  font-size: 11px;
  color: var(--text-muted, #787b86);
}

.rule-params {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.param-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
}

.param-key {
  color: var(--text-muted, #787b86);
}

.param-value {
  color: var(--text-primary, #d1d4dc);
  font-weight: 500;
}

.rule-card-footer {
  display: flex;
  gap: 12px;
  padding: 8px 16px;
  border-top: 1px solid var(--border-color, #2a2e39);
  background: var(--bg-primary, #131722);
}

.btn-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  padding: 0;
  background: transparent;
  border: none;
  border-radius: 4px;
  color: var(--text-muted, #787b86);
  cursor: pointer;
  transition: all 0.2s ease;

  svg {
    width: 14px;
    height: 14px;
  }

  &:hover {
    background: var(--bg-secondary, #1e222d);
    color: var(--accent-blue, #409EFF);
  }

  &.danger:hover {
    color: #ef5350;
  }
}

// 开关样式
.switch {
  position: relative;
  display: inline-block;
  width: 36px;
  height: 20px;

  input {
    opacity: 0;
    width: 0;
    height: 0;
  }

  .slider {
    position: absolute;
    cursor: pointer;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: var(--bg-primary, #2a2e39);
    transition: 0.3s;
    border-radius: 20px;

    &:before {
      position: absolute;
      content: "";
      height: 14px;
      width: 14px;
      left: 3px;
      bottom: 3px;
      background-color: var(--text-muted, #787b86);
      transition: 0.3s;
      border-radius: 50%;
    }
  }

  input:checked + .slider {
    background-color: var(--accent-blue, #409EFF);
  }

  input:checked + .slider:before {
    transform: translateX(16px);
    background-color: white;
  }
}
</style>

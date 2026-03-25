<template>
  <div class="weight-editor">
    <div class="editor-header">
      <h4 class="editor-title">{{ title }}</h4>
      <el-tag v-if="totalPercent > 0" type="info" size="small">
        {{ totalLabelText }}: {{ totalPercent.toFixed(0) }}%
      </el-tag>
    </div>

    <div v-if="factors.length === 0" class="empty-state">
      <p>{{ emptyText }}</p>
    </div>

    <div v-else class="weights-list">
      <div
        v-for="factor in factors"
        :key="factor"
        class="weight-item"
      >
        <span class="weight-label">{{ factor }}</span>
        <el-slider
          :model-value="weights[factor] || 0"
          @update:model-value="(val) => updateWeight(factor, val)"
          :min="0"
          :max="1"
          :step="step"
          :show-input="showInput"
          :format-tooltip="formatTooltip"
          style="flex: 1; max-width: 200px;"
        />
        <span class="weight-value">{{ ((weights[factor] || 0) * 100).toFixed(0) }}%</span>
        <el-button
          v-if="showRemove"
          type="danger"
          size="small"
          :icon="Close"
          circle
          @click="removeFactor(factor)"
        />
      </div>
    </div>

    <!-- 归一化按钮 -->
    <div v-if="showNormalize && needsNormalization" class="normalize-hint">
      <el-alert
        :title="normalizeHintText"
        type="warning"
        :closable="false"
        show-icon
      />
      <el-button type="primary" size="small" @click="normalize" style="margin-top: 8px;">
        {{ normalizeButtonText }}
      </el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Close } from '@element-plus/icons-vue'

interface Weights {
  [key: string]: number
}

interface Props {
  factors: string[]
  weights: Weights
  step?: number
  showInput?: boolean
  showRemove?: boolean
  showNormalize?: boolean
  isZh?: boolean
  title?: string
  emptyText?: string
}

const props = withDefaults(defineProps<Props>(), {
  step: 0.05,
  showInput: true,
  showRemove: false,
  showNormalize: true,
  isZh: true,
  title: '',
  emptyText: ''
})

const emit = defineEmits<{
  'update:weights': [weights: Weights]
  'remove': [factor: string]
}>()

const title = computed(() => props.title || (props.isZh ? '自定义权重' : 'Custom Weights'))
const emptyText = computed(() => props.emptyText || (props.isZh ? '请先选择因子' : 'Please select factors first'))
const totalLabelText = computed(() => props.isZh ? '总计' : 'Total')
const normalizeHintText = computed(() => props.isZh ? '权重总和不为100%，建议归一化' : 'Weights do not sum to 100%, consider normalizing')
const normalizeButtonText = computed(() => props.isZh ? '归一化权重' : 'Normalize Weights')

const totalPercent = computed(() => {
  return Object.values(props.weights).reduce((sum, w) => sum + w, 0) * 100
})

const needsNormalization = computed(() => {
  const total = Object.values(props.weights).reduce((sum, w) => sum + w, 0)
  return total > 0 && Math.abs(total - 1) > 0.01
})

const formatTooltip = (value: number) => {
  return (value * 100).toFixed(0) + '%'
}

const updateWeight = (factor: string, value: number) => {
  emit('update:weights', {
    ...props.weights,
    [factor]: value
  })
}

const removeFactor = (factor: string) => {
  emit('remove', factor)
}

const normalize = () => {
  const total = Object.values(props.weights).reduce((sum, w) => sum + w, 0)
  if (total > 0) {
    const normalized: Weights = {}
    Object.keys(props.weights).forEach(factor => {
      normalized[factor] = props.weights[factor] / total
    })
    emit('update:weights', normalized)
  }
}
</script>

<style scoped lang="scss">
.weight-editor {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 16px;
  background: var(--bg-primary);
  border-radius: 6px;
  border: 1px solid var(--border-color);
}

.editor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.editor-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.empty-state {
  text-align: center;
  padding: 20px;
  color: var(--text-secondary);
  font-size: 12px;
}

.weights-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.weight-item {
  display: flex;
  align-items: center;
  gap: 12px;
}

.weight-label {
  min-width: 80px;
  font-size: 12px;
  font-weight: 600;
  color: var(--text-primary);
}

.weight-value {
  min-width: 45px;
  font-size: 12px;
  font-weight: 600;
  color: var(--accent-blue);
  text-align: right;
}

.normalize-hint {
  margin-top: 8px;
}
</style>

<template>
  <div class="metrics-details-table">
    <el-table :data="data" stripe border style="width: 100%">
      <el-table-column :label="labelColumn" prop="name" width="120" />
      <el-table-column :label="valueLabel" prop="value" width="100">
        <template #default="{ row }">
          {{ formatValue(row.value) }}
        </template>
      </el-table-column>
      <el-table-column :label="thresholdLabel" prop="threshold" width="100">
        <template #default="{ row }">
          {{ formatValue(row.threshold) }}
        </template>
      </el-table-column>
      <el-table-column :label="statusLabel" prop="status" width="100">
        <template #default="{ row }">
          <el-tag :type="row.passed ? 'success' : 'danger'" size="small">
            {{ row.passed ? passText : failText }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column :label="scoreLabel" prop="score">
        <template #default="{ row }">
          <el-progress
            :percentage="Math.round(row.score)"
            :show-text="true"
            :color="getScoreColor(row.score)"
          />
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

export interface MetricRow {
  name: string
  value: number
  threshold: number
  passed: boolean
  score: number
}

interface Props {
  data: MetricRow[]
  isZh?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  isZh: true
})

const labelColumn = computed(() => props.isZh ? '指标' : 'Metric')
const valueLabel = computed(() => props.isZh ? '数值' : 'Value')
const thresholdLabel = computed(() => props.isZh ? '阈值' : 'Threshold')
const statusLabel = computed(() => props.isZh ? '状态' : 'Status')
const scoreLabel = computed(() => props.isZh ? '评分' : 'Score')
const passText = computed(() => props.isZh ? '通过' : 'Pass')
const failText = computed(() => props.isZh ? '未通过' : 'Fail')

const formatValue = (value: number) => {
  return value.toFixed(4)
}

const getScoreColor = (score: number) => {
  if (score >= 35) return '#67c23a'
  if (score >= 25) return '#e6a23c'
  if (score >= 15) return '#f56c6c'
  return '#909399'
}
</script>

<style scoped lang="scss">
.metrics-details-table {
  width: 100%;
}

:deep(.el-table) {
  --el-table-bg-color: var(--bg-primary);
  --el-table-header-bg-color: var(--bg-tertiary);
  --el-table-text-color: var(--text-primary);
  --el-table-header-text-color: var(--text-primary);
  --el-table-border-color: var(--border-color);
  --el-table-row-hover-bg-color: var(--bg-tertiary);
}

:deep(.el-tag--success) {
  background-color: rgba(103, 194, 58, 0.2);
  border-color: #67c23a;
}

:deep(.el-tag--danger) {
  background-color: rgba(245, 108, 108, 0.2);
  border-color: #f56c6c;
}
</style>

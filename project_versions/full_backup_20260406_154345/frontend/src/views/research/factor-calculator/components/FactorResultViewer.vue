<template>
  <el-card v-if="result" class="result-viewer">
    <template #header>
      <div class="card-header">
        <h3>{{ resultTitle }}</h3>
        <el-button-group>
          <el-button size="small" @click="handleExport('csv')">
            <el-icon><Download /></el-icon>
            导出CSV
          </el-button>
          <el-button size="small" @click="handleExport('excel')">
            <el-icon><Document /></el-icon>
            导出Excel
          </el-button>
          <el-button size="small" @click="handleSaveQlib" type="primary">
            <el-icon><FolderOpened /></el-icon>
            保存QLib
          </el-button>
        </el-button-group>
      </div>
    </template>

    <!-- 统计信息 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :span="6" v-for="(stat, key) in statistics" :key="key">
        <el-statistic :title="stat.label" :value="stat.value" :precision="stat.precision || 0" />
      </el-col>
    </el-row>

    <!-- 图表展示 -->
    <el-card v-if="showChart" class="chart-card" shadow="never">
      <h4>数据分布</h4>
      <div class="chart-placeholder">
        <el-empty description="图表组件待集成" />
      </div>
    </el-card>

    <!-- 数据表格 -->
    <el-card class="table-card" shadow="never">
      <template #header>
        <div class="table-header">
          <h4>数据详情</h4>
          <el-text type="info">共 {{ totalRows }} 条记录</el-text>
        </div>
      </template>
      <el-table
        :data="paginatedData"
        stripe
        border
        max-height="400"
        :empty-text="emptyText"
      >
        <el-table-column
          v-for="col in columns"
          :key="col.key"
          :prop="col.key"
          :label="col.label"
          :width="col.width"
          :formatter="col.formatter"
        />
      </el-table>

      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[20, 50, 100, 200]"
        :total="totalRows"
        layout="total, sizes, prev, pager, next, jumper"
        class="pagination"
        @size-change="handleSizeChange"
      />
    </el-card>
  </el-card>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { Download, Document, FolderOpened } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

// Props定义
interface ResultColumn {
  key: string
  label: string
  width?: number
  formatter?: (row: any, column: any, cellValue: any) => string
}

interface ResultStatistics {
  [key: string]: {
    label: string
    value: number | string
    precision?: number
  }
}

interface Props {
  resultType: 'indicator' | 'alpha158' | 'alpha360' | 'custom'
  result: any
  showChart?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  showChart: true
})

// Emits定义
const emit = defineEmits<{
  (e: 'export', format: 'csv' | 'excel' | 'parquet'): void
  (e: 'save-qlib'): void
}>()

// 状态
const currentPage = ref(1)
const pageSize = ref(50)

// 计算属性
const resultTitle = computed(() => {
  const titles = {
    indicator: '技术指标计算结果',
    alpha158: 'Alpha158因子结果',
    alpha360: 'Alpha360因子结果',
    custom: '自定义因子结果'
  }
  return titles[props.resultType] || '计算结果'
})

const statistics = computed((): ResultStatistics => {
  if (!props.result) return {}

  if (props.resultType === 'indicator') {
    return {
      symbol: { label: '股票代码', value: props.result.symbol || '-' },
      indicators: { label: '指标数量', value: Object.keys(props.result.indicators || {}).length },
      dataPoints: { label: '数据点数', value: props.result.data_points || 0 }
    }
  } else if (props.resultType === 'alpha158' || props.resultType === 'alpha360') {
    const factorCount = props.resultType === 'alpha158' ? 158 : 360
    return {
      symbols: { label: '股票数量', value: props.result.symbols?.length || 0 },
      factors: { label: '因子数量', value: factorCount },
      startDate: { label: '开始日期', value: props.result.start_date || '-' },
      endDate: { label: '结束日期', value: props.result.end_date || '-' }
    }
  } else if (props.resultType === 'custom') {
    return {
      expression: { label: '表达式', value: props.result.expression || '-' },
      symbols: { label: '股票数量', value: props.result.symbols?.length || 0 }
    }
  }
  return {}
})

const columns = computed((): ResultColumn[] => {
  if (props.resultType === 'indicator') {
    return [
      { key: 'name', label: '指标名称', width: 150 },
      { key: 'preview', label: '数据预览', width: 300 },
      { key: 'count', label: '数据点数', width: 100 }
    ]
  } else if (props.resultType === 'alpha158' || props.resultType === 'alpha360') {
    return [
      { key: 'factor', label: '因子名称', width: 150 },
      { key: 'preview', label: '数据预览' }
    ]
  } else if (props.resultType === 'custom') {
    return [
      { key: 'symbol', label: '股票代码', width: 120 },
      { key: 'datetime', label: '时间', width: 180 },
      {
        key: 'value',
        label: '因子值',
        width: 120,
        formatter: (row, column, cellValue) => cellValue ? cellValue.toFixed(4) : '-'
      }
    ]
  }
  return []
})

const tableData = computed(() => {
  if (!props.result) return []

  if (props.resultType === 'indicator') {
    return Object.entries(props.result.indicators || {}).map(([name, data]: [string, any]) => ({
      name,
      preview: (data.values || []).slice(0, 5).join(', '),
      count: (data.values || []).length
    }))
  } else if (props.resultType === 'alpha158' || props.resultType === 'alpha360') {
    const factors = props.result.factors || {}
    return Object.keys(factors).slice(0, 100).map(key => ({
      factor: key,
      preview: '数据预览...'
    }))
  } else if (props.resultType === 'custom') {
    return props.result.data || []
  }
  return []
})

const totalRows = computed(() => tableData.value.length)

const paginatedData = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return tableData.value.slice(start, end)
})

const emptyText = computed(() => {
  return props.result ? '暂无数据' : '请先进行计算'
})

// 方法
const handleExport = (format: 'csv' | 'excel' | 'parquet') => {
  emit('export', format)
  ElMessage.success(`正在导出为 ${format.toUpperCase()} 格式...`)
}

const handleSaveQlib = () => {
  emit('save-qlib')
  ElMessage.success('正在保存为QLib格式...')
}

const handleSizeChange = (size: number) => {
  pageSize.value = size
  currentPage.value = 1
}
</script>

<style scoped lang="scss">
.result-viewer {
  margin-top: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;

  h3 {
    margin: 0;
    font-size: 16px;
    font-weight: 600;
  }
}

.stats-row {
  margin-bottom: 20px;

  :deep(.el-statistic) {
    text-align: center;
  }
}

.chart-card,
.table-card {
  margin-top: 20px;
}

.chart-placeholder {
  height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;

  h4 {
    margin: 0;
    font-size: 14px;
    font-weight: 600;
  }
}

.pagination {
  margin-top: 15px;
  display: flex;
  justify-content: flex-end;
}
</style>

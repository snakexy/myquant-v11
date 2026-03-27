<template>
  <div class="database-manager">
    <!-- 数据库概览 -->
    <DatabaseOverview
      :stats="dbStats"
      :loading="refreshing"
      @refresh="() => refreshDatabase(true)"
    />

    <el-divider />

    <!-- 股票列表 -->
    <div class="stocks-section">
      <!-- 筛选面板 -->
      <FilterPanel
        :frequencies="availableFrequencies"
        v-model="selectedFrequencies"
        :selected-count="selectedStocks.length"
        @search="handleSearch"
        @batch-action="handleBatchAction"
      />

      <!-- 股票表格 -->
      <StockTable
        :data="paginatedStocks"
        :loading="loading"
        :total="filteredStocks.length"
        :current-page="currentPage"
        :page-size="pageSize"
        sort-by="code"
        sort-order="asc"
        ref="stockTableRef"
        @selection-change="handleSelectionChange"
        @update="updateStock"
        @delete="deleteStock"
        @update:current-page="currentPage = $event"
        @update:page-size="pageSize = $event"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import DatabaseOverview from './DatabaseOverview.vue'
import FilterPanel from './FilterPanel.vue'
import StockTable from './StockTable.vue'
import { scanDatabase, updateStockData, deleteStockData } from '@/components/data-management/shared/api'
import { formatNumber, calculateHealthScore } from '@/components/data-management/shared/utils'
import type { DatabaseStats } from '@/components/data-management/shared/types'
import { STOCK_PINYIN_MAPPING } from '@/assets/stock-pinyin-mapping.js'


interface Props {
  config?: Record<string, any>
  params?: Record<string, any>
  selectedStockCodes?: string[]
}

const props = defineProps<Props>()

// 定义 emit
const emit = defineEmits<{
  'update:selectedStocks': [stocks: any[]]
  'update:selectedStockCodes': [codes: string[]]
  'update:selectedFrequencies': [frequencies: string[]]
  'update:databaseStats': [stats: any]
}>()

// 状态
const loading = ref(false)
const refreshing = ref(false)
const searchText = ref('')
const selectedStocks = ref<any[]>([])
const currentPage = ref(1)
const pageSize = ref(20)

// 可用频率选项
const availableFrequencies = [
  { label: '日线', value: 'daily' },
  { label: '5分钟', value: '5min' },
  { label: '15分钟', value: '15min' },
  { label: '30分钟', value: '30min' },
  { label: '60分钟', value: '60min' }
]

// 选中的频率
// 🔧 默认只显示日线数据，只有同时选择60分钟时才显示60分钟数据
const selectedFrequencies = ref<string[]>(['daily'])

const dbStats = ref<DatabaseStats | null>(null)
const rawStockList = ref<any[]>([])

// 表格引用
const stockTableRef = ref<{ tableRef: any }>()

// 标记是否正在恢复选中状态
const isRestoring = ref(false)

// 从预生成的映射中获取拼音信息
const getPinyinFromMapping = (stockCode: string, stockName: string) => {
  // 优先使用映射表
  if (STOCK_PINYIN_MAPPING && STOCK_PINYIN_MAPPING[stockCode]) {
    return {
      initials: STOCK_PINYIN_MAPPING[stockCode].pinyin_initials || '',
      full: STOCK_PINYIN_MAPPING[stockCode].pinyin_full || ''
    }
  }

  // 如果映射表中没有,返回空字符串
  // (理论上不应该发生,因为映射表包含了所有股票)
  return {
    initials: '',
    full: ''
  }
}

// 过滤后的股票列表
const filteredStocks = computed(() => {
  let stocks = rawStockList.value

  // 搜索过滤
  if (searchText.value) {
    const term = searchText.value.toLowerCase()
    stocks = stocks.filter((s: any) => {
      // 股票代码匹配（如：600000, 000001）
      const codeMatch = (s.original_code && s.original_code.toLowerCase().includes(term)) ||
                        (s.code && s.code.toLowerCase().includes(term))

      // 股票名称匹配（如：浦发银行）
      const nameMatch = s.name && s.name.includes(searchText.value)

      // 拼音首字母匹配（如：pfyh -> 浦发银行）
      // 使用预生成的映射表,无需实时转换
      const pinyinInfo = getPinyinFromMapping(s.code || s.original_code, s.name)
      const pinyinInitialsMatch = pinyinInfo.initials &&
                                   pinyinInfo.initials.toLowerCase().includes(term)

      // 拼音全拼匹配（如：pufayinhang -> 浦发银行）
      const pinyinFullMatch = pinyinInfo.full &&
                              pinyinInfo.full.includes(term)

      return codeMatch || nameMatch || pinyinInitialsMatch || pinyinFullMatch
    })
  }

  // 去重：基于完整的 code + frequency 组合去重
  const uniqueMap = new Map<string, any>()
  stocks.forEach((stock: any) => {
    const uniqueCode = stock.code || stock.original_code
    const key = `${uniqueCode}_${stock.frequency || 'daily'}`
    if (!uniqueMap.has(key)) {
      uniqueMap.set(key, stock)
    }
  })

  stocks = Array.from(uniqueMap.values())

  return stocks
})

// 分页后的股票列表
const paginatedStocks = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value

  const result = filteredStocks.value.slice(start, end).map((stock: any) => {
    const fullCode = stock.code || stock.original_code
    const frequency = stock.frequency || 'daily'
    const uniqueKey = `${fullCode}_${frequency}`

    return {
      code: uniqueKey,
      displayCode: stock.original_code || stock.code,
      name: stock.name || '-',
      frequency: frequency,
      startDate: stock.start_date || '-',
      endDate: stock.end_date || '-',
      recordCount: stock.record_count || 0,
      dataAge: stock.data_age_days || 0,
      healthScore: calculateHealthScore(stock),
      updating: false,
      _original: stock
    }
  })

  return result
})

// 处理搜索
const handleSearch = (text: string) => {
  searchText.value = text
  currentPage.value = 1
}

// 处理选择变化
const handleSelectionChange = (selection: any[]) => {
  if (isRestoring.value) {
    return
  }

  selectedStocks.value = selection

  // 向父组件发送选中的标的列表
  emit('update:selectedStocks', selection)

  // 向父组件发送选中的标的代码列表
  const codeFrequencyPairs = selection.map((s: any) => {
    const code = s._original?.code || s.code
    const frequency = s._original?.frequency || s.frequency || 'daily'
    return `${code}_${frequency}`
  })

  emit('update:selectedStockCodes', codeFrequencyPairs)
}

// 恢复选中状态
const restoreSelections = async () => {
  const codeFrequencyPairs = props.selectedStockCodes ? [...props.selectedStockCodes] : []

  if (codeFrequencyPairs.length === 0) {
    return
  }

  await nextTick()
  isRestoring.value = true

  try {
    if (stockTableRef.value?.tableRef) {
      stockTableRef.value.tableRef.clearSelection()
    }

    await nextTick()

    const rowsToSelect: any[] = []

    paginatedStocks.value.forEach((stock: any) => {
      const fullCode = stock._original?.code || stock.code
      const frequency = stock._original?.frequency || stock.frequency || 'daily'
      const key = `${fullCode}_${frequency}`

      if (codeFrequencyPairs.includes(key)) {
        rowsToSelect.push(stock)
      }
    })

    if (stockTableRef.value?.tableRef && rowsToSelect.length > 0) {
      rowsToSelect.forEach((stock: any) => {
        stockTableRef.value!.tableRef.toggleRowSelection(stock, true)
      })

      selectedStocks.value = rowsToSelect
    }
  } finally {
    await nextTick()
    isRestoring.value = false
  }
}

// 刷新数据库
const refreshDatabase = async (forceRefresh: boolean = false) => {
  refreshing.value = true
  loading.value = true
  try {
    // 🔧 修复：默认不强制刷新，使用缓存。只有用户手动点击刷新按钮时才强制刷新
    const response = await scanDatabase(forceRefresh, selectedFrequencies.value)

    if (response.code === 200 && response.data) {
      const data = response.data

      // 为后端返回的数据补充 frequency 字段
      const stocks = (data.stocks || []).map((stock: any, index: number) => {
        if (stock.frequency) {
          return stock
        }

        const code = stock.code || stock.original_code || ''
        let inferredFreq = 'daily'

        if (code.includes('.1min') || code.includes('_1min')) {
          inferredFreq = '1min'
        } else if (code.includes('.5min') || code.includes('_5min')) {
          inferredFreq = '5min'
        } else if (code.includes('.15min') || code.includes('_15min')) {
          inferredFreq = '15min'
        } else if (code.includes('.30min') || code.includes('_30min')) {
          inferredFreq = '30min'
        } else if (code.includes('.60min') || code.includes('_60min')) {
          inferredFreq = '60min'
        } else {
          const freqIndex = index % selectedFrequencies.value.length
          inferredFreq = selectedFrequencies.value[freqIndex] || 'daily'
        }

        return {
          ...stock,
          frequency: inferredFreq
        }
      })

      rawStockList.value = stocks

      // 更新统计数据 - 使用后端返回的统计值
      dbStats.value = {
        totalStocks: data.total_stocks || 0,
        totalRecords: data.data_quality?.total_records || 0,
        needsUpdate: 0,  // TODO: 从后端获取
        healthyStocks: data.total_stocks || 0,  // TODO: 根据健康度计算
        dateRange: `${data.date_range?.earliest || '--'} 至 ${data.date_range?.latest || '--'}`
      }

      // 向父组件发送数据库统计信息
      emit('update:databaseStats', {
        data_overview: {
          stock_count: data.total_stocks || 0,
          total_records: data.data_quality?.total_records || 0,
          data_time_range: `${data.date_range?.earliest || '--'} 至 ${data.date_range?.latest || '--'}`
        },
        storage_info: {
          data_storage: {
            total_records: data.data_quality?.total_records || 0,
            last_updated: new Date().toISOString()
          }
        }
      })

      // 数据加载完成后，恢复选中状态
      await restoreSelections()

      ElMessage.success(`数据库已刷新，共 ${data.total_stocks || 0} 条记录`)
    } else {
      throw new Error(response.message || '扫描失败')
    }
  } catch (error: any) {
    console.error('[DatabaseManager] 刷新失败:', error)
    ElMessage.error(`刷新失败: ${error.message || error}`)
  } finally {
    refreshing.value = false
    loading.value = false
  }
}

// 更新股票数据
const updateStock = async (stock: any) => {
  stock.updating = true
  try {
    const stockCode = stock._original?.code || stock.code

    const response = await updateStockData([stockCode])

    if (response.code === 200) {
      ElMessage.success(`已发起更新请求: ${stockCode}`)
      await refreshDatabase()
    } else {
      throw new Error(response.message || '更新失败')
    }
  } catch (error: any) {
    console.error('[DatabaseManager] 更新失败:', error)
    ElMessage.error(`更新失败: ${error.message || error}`)
  } finally {
    stock.updating = false
  }
}

// 更新股票数据但不触发刷新
const updateStockWithoutRefresh = async (stock: any) => {
  stock.updating = true
  try {
    const stockCode = stock._original?.code || stock.code

    const response = await updateStockData([stockCode])

    if (response.code !== 200) {
      throw new Error(response.message || '更新失败')
    }
  } catch (error: any) {
    console.error('[DatabaseManager] 更新失败:', error)
    throw error
  } finally {
    stock.updating = false
  }
}

// 删除股票数据
const deleteStock = async (stock: any) => {
  try {
    const stockCode = stock._original?.code || stock.code
    const stockName = stock.name || stockCode

    await ElMessageBox.confirm(
      `确定要删除 ${stockCode} ${stockName} 的数据吗？此操作不可恢复！`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    const response = await deleteStockData(stockCode)

    if (response.code === 200 || response.data?.success) {
      ElMessage.success('删除成功')
      await refreshDatabase()
    } else {
      throw new Error(response.message || '删除失败')
    }
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('[DatabaseManager] 删除失败:', error)
      ElMessage.error(`删除失败: ${error.message || error}`)
    }
  }
}

// 批量操作
const handleBatchAction = async (command: string) => {
  if (selectedStocks.value.length === 0) {
    ElMessage.warning('请先选择股票')
    return
  }

  switch (command) {
    case 'update':
      try {
        const codes = selectedStocks.value.map((s: any) => s._original?.code || s.displayCode)
        loading.value = true

        for (const stock of selectedStocks.value) {
          await updateStockWithoutRefresh(stock)
        }

        await refreshDatabase()

        ElMessage.success(`批量更新完成: ${codes.length} 只股票`)
      } catch (error: any) {
        ElMessage.error(`批量更新失败: ${error.message}`)
      } finally {
        loading.value = false
      }
      break
    case 'export':
      try {
        exportSelectedStocks()
      } catch (error: any) {
        ElMessage.error(`导出失败: ${error.message}`)
      }
      break
  }
}

// 导出选中股票清单
const exportSelectedStocks = () => {
  if (selectedStocks.value.length === 0) {
    ElMessage.warning('请先选择要导出的股票')
    return
  }

  const getFrequencyLabel = (freq: string) => {
    const freqMap: Record<string, string> = {
      'daily': '日线',
      '1min': '1分',
      '5min': '5分',
      '15min': '15分',
      '30min': '30分',
      '60min': '60分'
    }
    return freqMap[freq] || freq
  }

  const headers = ['股票代码', '股票名称', '周期', '开始日期', '结束日期', '记录数', '数据年龄(天)', '健康度(%)']
  const rows = selectedStocks.value.map((stock: any) => [
    stock.displayCode,
    stock.name,
    getFrequencyLabel(stock.frequency) || '-',
    stock.startDate,
    stock.endDate,
    stock.recordCount,
    stock.dataAge,
    stock.healthScore
  ])

  const BOM = '\uFEFF'
  const csvContent = BOM + [
    headers.join(','),
    ...rows.map(row => row.join(','))
  ].join('\n')

  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  const url = URL.createObjectURL(blob)

  const timestamp = new Date().toISOString().slice(0, 10).replace(/-/g, '')
  link.setAttribute('href', url)
  link.setAttribute('download', `股票清单_${timestamp}.csv`)
  link.style.visibility = 'hidden'

  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)

  URL.revokeObjectURL(url)
  ElMessage.success(`已导出 ${selectedStocks.value.length} 只股票的清单`)
}

// 监听周期选择变化
// 🔧 修复：不立即执行，避免页面加载时自动触发扫描
watch(selectedFrequencies, async (newFrequencies) => {
  if (newFrequencies.length > 0) {
    emit('update:selectedFrequencies', newFrequencies)
    await refreshDatabase()
  }
}, { deep: true, flush: 'post' })

// 初始化
// 🔧 页面加载时使用缓存刷新数据库（不强制重新扫描）
// 这样可以快速显示已有数据，同时避免频繁扫描
onMounted(async () => {
  // 使用缓存刷新，如果有缓存则快速返回，不会触发昂贵的 QLib 扫描
  await refreshDatabase(false)
})
</script>

<style scoped>
.database-manager {
  padding: 16px;
  background: rgba(26, 26, 46, 0.95);
  border-radius: 8px;
}

.stocks-section {
  margin-top: 20px;
}

:deep(.el-divider) {
  border-color: rgba(255, 255, 255, 0.1);
  margin: 20px 0;
}

/* 统一按钮风格 - 与数据源管理页面保持一致 */
:deep(.el-button) {
  border-radius: 20px;
}

:deep(.el-button--primary) {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(255, 255, 255, 0.2);
  color: rgba(255, 255, 255, 0.9);
}

:deep(.el-button--primary:hover:not(:disabled)) {
  background: linear-gradient(135deg, #2962ff 0%, #764ba2 100%);
  border-color: transparent;
  color: white;
}

:deep(.el-button--primary:active:not(:disabled)) {
  background: linear-gradient(135deg, #5568d3 0%, #643a8b 100%);
  border-color: transparent;
  color: white;
}

:deep(.el-button--warning) {
  background: rgba(245, 158, 11, 0.15);
  border-color: rgba(245, 158, 11, 0.3);
  color: rgba(245, 158, 11, 0.9);
}

:deep(.el-button--warning:hover:not(:disabled)) {
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
  border-color: transparent;
  color: white;
}

:deep(.el-button--danger) {
  background: rgba(239, 68, 68, 0.15);
  border-color: rgba(239, 68, 68, 0.3);
  color: rgba(239, 68, 68, 0.9);
}

:deep(.el-button--danger:hover:not(:disabled)) {
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
  border-color: transparent;
  color: white;
}

:deep(.el-button--info) {
  background: rgba(59, 130, 246, 0.15);
  border-color: rgba(59, 130, 246, 0.3);
  color: rgba(59, 130, 246, 0.9);
}

:deep(.el-button--info:hover:not(:disabled)) {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  border-color: transparent;
  color: white;
}

:deep(.el-button--success) {
  background: rgba(16, 185, 129, 0.15);
  border-color: rgba(16, 185, 129, 0.3);
  color: rgba(16, 185, 129, 0.9);
}

:deep(.el-button--success:hover:not(:disabled)) {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  border-color: transparent;
  color: white;
}

:deep(.el-button--default) {
  background: rgba(255, 255, 255, 0.05);
  border-color: rgba(255, 255, 255, 0.15);
  color: rgba(255, 255, 255, 0.85);
}

:deep(.el-button--default:hover:not(:disabled)) {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.25);
  color: rgba(255, 255, 255, 0.95);
}
</style>

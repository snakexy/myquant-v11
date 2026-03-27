<template>
  <div class="database-manager">
    <!-- 数据库概览 -->
    <div class="overview-section">
      <div class="section-header">
        <h3>数据库概览</h3>
        <div class="header-actions">
          <el-button size="small" @click="refreshDatabase" :loading="refreshing" class="custom-secondary-btn">
            <font-awesome-icon icon="sync-alt" :spin="refreshing" />
            刷新
          </el-button>
        </div>
      </div>

      <div class="stats-grid" v-if="dbStats">
        <div class="stat-card">
          <div class="stat-icon">
            <font-awesome-icon icon="database" />
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ dbStats.totalStocks || 0 }}</div>
            <div class="stat-label">总股票数</div>
          </div>
        </div>

        <div class="stat-card">
          <div class="stat-icon needs-update">
            <font-awesome-icon icon="exclamation-triangle" />
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ dbStats.needsUpdate || 0 }}</div>
            <div class="stat-label">需要更新</div>
          </div>
        </div>

        <div class="stat-card">
          <div class="stat-icon success">
            <font-awesome-icon icon="check-circle" />
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ dbStats.healthyStocks || 0 }}</div>
            <div class="stat-label">数据健康</div>
          </div>
        </div>

        <div class="stat-card">
          <div class="stat-icon">
            <font-awesome-icon icon="calendar-alt" />
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ formatDateRange(dbStats.dateRange) }}</div>
            <div class="stat-label">数据范围</div>
          </div>
        </div>
      </div>

      <!-- 空状态提示 -->
      <div v-else class="empty-state">
        <div class="empty-icon">
          <font-awesome-icon icon="database" />
        </div>
        <div class="empty-text">
          <h4>暂无数据库信息</h4>
          <p>点击"刷新"按钮扫描数据库</p>
        </div>
      </div>
    </div>

    <el-divider />

    <!-- 股票列表 -->
    <div class="stocks-section">
      <div class="section-header">
        <div class="header-left">
          <!-- 周期筛选 -->
          <div class="frequency-filter">
            <label class="filter-label">周期:</label>
            <div class="frequency-chips">
              <label
                v-for="freq in availableFrequencies"
                :key="freq.value"
                :class="['freq-chip', { active: selectedFrequencies.includes(freq.value) }]"
              >
                <input
                  type="checkbox"
                  :value="freq.value"
                  v-model="selectedFrequencies"
                />
                <span>{{ freq.label }}</span>
              </label>
            </div>
          </div>
        </div>

        <div class="header-actions">
          <input
            v-model="searchText"
            class="search-input"
            placeholder="搜索股票代码或名称"
          />

          <el-dropdown trigger="click" @command="handleBatchAction">
            <el-button size="small" :disabled="selectedStocks.length === 0">
              批量操作
              <font-awesome-icon icon="caret-down" style="margin-left: 4px" />
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="update">
                  <font-awesome-icon icon="sync-alt" style="margin-right: 8px" />
                  批量更新
                </el-dropdown-item>
                <el-dropdown-item command="export">
                  <font-awesome-icon icon="download" style="margin-right: 8px" />
                  导出清单
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </div>

      <!-- 股票表格 -->
      <el-table
        :data="paginatedStocks"
        :loading="loading"
        size="default"
        @selection-change="handleSelectionChange"
        :default-sort="{ prop: sortBy, order: sortOrder === 'asc' ? 'ascending' : 'descending' }"
        class="stocks-table"
        :row-key="(row: any) => row.code"
        ref="tableRef"
      >
        <el-table-column type="selection" width="60" align="center" />
        <el-table-column prop="displayCode" label="股票代码" width="110" sortable align="center" />
        <el-table-column prop="name" label="股票名称" width="130" sortable align="left">
          <template #default="{ row }">
            <div style="display: flex; align-items: center; justify-content: flex-start; padding-left: 16px;">
              <span>{{ row.name || '-' }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="frequency" label="周期" width="90" sortable align="center">
          <template #default="{ row }">
            <el-tag :type="getFrequencyTagType(row.frequency)" size="small">
              {{ getFrequencyLabel(row.frequency) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="startDate" label="开始日期" width="125" sortable align="center">
          <template #default="{ row }">
            <span style="white-space: nowrap; color: var(--text-secondary);">
              {{ row.startDate || '-' }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="endDate" label="结束日期" width="125" sortable align="center">
          <template #default="{ row }">
            <span :class="getDataAgeClass(row.dataAge)" style="white-space: nowrap;">
              {{ row.endDate || '-' }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="recordCount" label="记录数" width="110" sortable align="right" />
        <el-table-column prop="dataAge" label="数据年龄" width="120" sortable align="center">
          <template #default="{ row }">
            <el-tag :type="getDataAgeTagType(row.dataAge)" size="small">
              {{ row.dataAge || 0 }} 天
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="healthScore" label="健康度" width="110" sortable align="center">
          <template #default="{ row }">
            <div style="display: flex; align-items: center; justify-content: center;">
              <span :style="{
                fontSize: '13px',
                fontWeight: '500',
                color: getHealthColor(row.healthScore || 0)
              }">
                {{ row.healthScore || 0 }}%
              </span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="110" align="center">
          <template #default="{ row }">
            <el-button-group size="small">
              <el-button @click="updateStock(row)" :loading="row.updating">
                <font-awesome-icon icon="sync-alt" />
              </el-button>
              <el-button type="danger" @click="deleteStock(row)">
                <font-awesome-icon icon="trash" />
              </el-button>
            </el-button-group>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-wrapper">
        <div class="pagination-info">
          共 {{ filteredStocks.length }} 条
        </div>
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[20, 50, 100]"
          :total="filteredStocks.length"
          layout="prev, pager, next"
          size="small"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import {
  ElMessage,
  ElMessageBox,
  ElTable,
  ElTableColumn,
  ElButton,
  ElButtonGroup,
  ElInput,
  ElDropdown,
  ElDropdownMenu,
  ElDropdownItem,
  ElTag,
  ElProgress,
  ElPagination,
  ElDivider
} from 'element-plus'
import type { TableColumnCtx } from 'element-plus'
import * as databaseApi from '../../api/modules/database'

interface Props {
  config?: Record<string, any>
  params?: Record<string, any>
  selectedStockCodes?: string[]
}

const props = defineProps<Props>()

// 配置
const databaseConfig = computed(() => props.config || {})
const sortBy = computed(() => databaseConfig.value.sortBy || 'code')
const sortOrder = computed(() => databaseConfig.value.sortOrder || 'asc')

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
const selectedFrequencies = ref<string[]>(['daily'])

const dbStats = ref<any>(null)
const stockList = ref<any[]>([])

// QLib 数据路径（从配置获取或使用默认值）
const qlibDataPath = computed(() => {
  return props.params?.qlibDataPath || props.config?.qlibDataPath || 'E:\\MyQuant_v8.0.1\\data\\qlib_data'
})

// 原始后端数据（保持原始格式用于显示）
const rawStockList = ref<any[]>([])

// 获取数据年龄样式类
const getDataAgeClass = (age: number) => {
  if (age > 30) return 'text-danger'
  if (age > 14) return 'text-warning'
  return 'text-success'
}

// 获取数据年龄标签类型
const getDataAgeTagType = (age: number) => {
  if (age > 30) return 'danger'
  if (age > 14) return 'warning'
  return 'success'
}

// 获取健康度颜色
const getHealthColor = (score: number) => {
  if (score >= 80) return '#67c23a'
  if (score >= 60) return '#e6a23c'
  return '#f56c6c'
}

// 获取周期标签
const getFrequencyLabel = (freq: string) => {
  const freqMap: Record<string, string> = {
    'daily': '日线',
    '5min': '5分',
    '15min': '15分',
    '30min': '30分',
    '60min': '60分'
  }
  return freqMap[freq] || freq
}

// 获取周期标签类型
const getFrequencyTagType = (freq: string) => {
  const typeMap: Record<string, string> = {
    'daily': 'primary',
    '5min': 'info',
    '15min': '',
    '30min': 'warning',
    '60min': 'danger'
  }
  return typeMap[freq] || ''
}

// 格式化日期范围
const formatDateRange = (range: any) => {
  if (!range) return '-'

  const start = range.start || '~'
  const end = range.end || '~'

  // 🔧 如果日期包含时间部分，只显示日期
  const extractDate = (dateStr: string) => {
    if (dateStr === '~' || dateStr === '-') return dateStr
    if (dateStr.includes(' ')) {
      return dateStr.split(' ')[0] // "2025-07-07 10:30:00" -> "2025-07-07"
    }
    return dateStr
  }

  const startClean = extractDate(start)
  const endClean = extractDate(end)

  return `${startClean} 至 ${endClean}`
}

// 过滤后的股票列表
const filteredStocks = computed(() => {
  let stocks = rawStockList.value

  // 搜索过滤
  if (searchText.value) {
    const term = searchText.value.toLowerCase()
    stocks = stocks.filter((s: any) =>
      (s.original_code && s.original_code.toLowerCase().includes(term)) ||
      (s.code && s.code.toLowerCase().includes(term))
    )
  }

  // 仅显示需要更新的股票
  if (databaseConfig.value.showNeedsUpdateOnly) {
    const threshold = databaseConfig.value.expiryThreshold || 7
    stocks = stocks.filter((s: any) => (s.data_age_days || 0) > threshold)
  }

  // 🔧 去重：基于完整的 code + frequency 组合去重（优先使用 code，因为它包含市场前缀如 sh/sz）
  const uniqueMap = new Map<string, any>()
  stocks.forEach((stock: any) => {
    // 🔧 优先使用完整的 code（带市场前缀），只有当 code 不存在时才使用 original_code
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

  // 将后端数据格式转换为前端显示格式
  const result = filteredStocks.value.slice(start, end).map((stock: any) => {
    // 🔧 构建唯一的 rowKey：组合完整的 code（带市场前缀）和 frequency
    const fullCode = stock.code || stock.original_code  // 🔧 优先使用完整 code
    const frequency = stock.frequency || 'daily'
    const uniqueKey = `${fullCode}_${frequency}`

    return {
      // 🔧 rowKey 使用唯一键
      code: uniqueKey,
      // displayCode 用于显示（不带频率后缀）
      displayCode: stock.original_code || stock.code,
      name: stock.name || '-',
      frequency: frequency,
      startDate: stock.start_date || '-',
      endDate: stock.end_date || '-',
      recordCount: stock.record_count || 0,
      dataAge: stock.data_age_days || 0,
      healthScore: calculateHealthScore(stock),
      updating: false,
      // 保留原始数据用于操作
      _original: stock
    }
  })

  return result
})

// 计算健康度分数（基于数据完整性和新鲜度）
const calculateHealthScore = (stock: any) => {
  let score = 100

  // 数据年龄扣分
  const age = stock.data_age_days || 0
  if (age > 30) {
    score -= 40
  } else if (age > 14) {
    score -= 20
  } else if (age > 7) {
    score -= 10
  }

  // 记录数扣分（少于100条认为不完整）
  const count = stock.record_count || 0
  if (count < 100) {
    score -= 30
  } else if (count < 500) {
    score -= 10
  }

  return Math.max(score, 0)
}

// 刷新数据库 - 使用真实 API，支持多周期
const refreshDatabase = async () => {
  refreshing.value = true
  loading.value = true
  try {
    // 调用真实 API 扫描数据库，传递选中的频率
    const response = await databaseApi.scanDatabase(true, selectedFrequencies.value)

    if (response.code === 200 && response.data) {
      const data = response.data

      // 🔧 为后端返回的数据补充 frequency 字段
      // 如果后端返回的数据没有 frequency 字段，我们尝试从 code 字段推断
      const stocks = (data.stocks || []).map((stock: any, index: number) => {
        // 如果已经有 frequency 字段，直接使用
        if (stock.frequency) {
          return stock
        }

        // 🔧 尝试从 code 字段推断频率（例如 "000001.daily" 或 "sh000001_1min"）
        const code = stock.code || stock.original_code || ''
        let inferredFreq = 'daily'

        // 检查 code 中是否包含频率标识
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
        } else if (code.includes('.day') || code.includes('_day') || code.includes('.daily') || code.includes('_daily')) {
          inferredFreq = 'daily'
        } else {
          // 🔧 如果无法从 code 推断，根据选中的频率列表和索引推断
          // 假设后端为每个股票返回多条数据（每个频率一条），按频率列表的顺序排列
          const freqIndex = index % selectedFrequencies.value.length
          inferredFreq = selectedFrequencies.value[freqIndex] || 'daily'
        }

        return {
          ...stock,
          frequency: inferredFreq
        }
      })

      rawStockList.value = stocks

      // 更新统计数据
      dbStats.value = {
        totalStocks: data.total_stocks || 0,
        needsUpdate: rawStockList.value.filter((s: any) => s.needs_update).length,
        healthyStocks: rawStockList.value.filter((s: any) => calculateHealthScore(s) >= 80).length,
        dateRange: {
          start: data.date_range?.earliest || '-',
          end: data.date_range?.latest || '-'
        }
      }

      // 🔧 向父组件发送数据库统计信息（用于 MiniDataReport 显示）
      emit('update:databaseStats', {
        data_overview: {
          stock_count: data.total_stocks || 0,
          total_records: rawStockList.value.reduce((sum: number, s: any) => sum + (s.record_count || 0), 0),
          data_time_range: `${data.date_range?.earliest || '--'} 至 ${data.date_range?.latest || '--'}`
        },
        storage_info: {
          data_storage: {
            total_records: rawStockList.value.reduce((sum: number, s: any) => sum + (s.record_count || 0), 0),
            last_updated: new Date().toISOString()
          }
        }
      })

      // 🔧 数据加载完成后，恢复选中状态
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

// 🔧 恢复选中状态（数据加载完成后调用）
const restoreSelections = async () => {
  // 🔧 立即保存 selectedStockCodes 的副本，避免响应式变化
  const codeFrequencyPairs = props.selectedStockCodes ? [...props.selectedStockCodes] : []

  // 如果没有传入的选中代码，直接返回
  if (codeFrequencyPairs.length === 0) {
    return
  }

  // 等待 DOM 更新
  await nextTick()

  // 标记开始恢复（防止触发 selection-change 事件）
  isRestoring.value = true

  try {
    // 清空当前选中
    if (tableRef.value) {
      tableRef.value.clearSelection()
    }

    // 等待清空完成
    await nextTick()

    const rowsToSelect: any[] = []

    // 🔧 在 paginatedStocks 中查找匹配的股票（使用 code_frequency 组合）
    paginatedStocks.value.forEach((stock: any) => {
      const fullCode = stock._original?.code || stock.code
      const frequency = stock._original?.frequency || stock.frequency || 'daily'
      const key = `${fullCode}_${frequency}`

      // 检查是否在选中的列表中
      if (codeFrequencyPairs.includes(key)) {
        rowsToSelect.push(stock)
      }
    })

    // 使用 toggleRowSelection 选中行
    if (tableRef.value && rowsToSelect.length > 0) {
      rowsToSelect.forEach((stock: any) => {
        tableRef.value!.toggleRowSelection(stock, true)
      })

      // 更新 selectedStocks
      selectedStocks.value = rowsToSelect
    }
  } finally {
    // 等待 DOM 更新完成后，再恢复事件处理
    await nextTick()
    isRestoring.value = false
  }
}

// 更新股票数据 - 使用真实 API
const updateStock = async (stock: any) => {
  stock.updating = true
  try {
    const stockCode = stock._original?.code || stock.code

    const response = await databaseApi.updateStockData([stockCode])

    if (response.code === 200) {
      ElMessage.success(`已发起更新请求: ${stockCode}`)
      // 刷新数据库以查看最新状态
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

// 🔧 新增：更新股票数据但不触发刷新（用于批量更新）
const updateStockWithoutRefresh = async (stock: any) => {
  stock.updating = true
  try {
    const stockCode = stock._original?.code || stock.code

    const response = await databaseApi.updateStockData([stockCode])

    if (response.code !== 200) {
      throw new Error(response.message || '更新失败')
    }
    // 🔧 不调用 refreshDatabase()，让批量更新完成后统一刷新
  } catch (error: any) {
    console.error('[DatabaseManager] 更新失败:', error)
    throw error // 🔧 抛出错误，让批量更新知道失败了
  } finally {
    stock.updating = false
  }
}

// 删除股票数据 - 使用真实 API
const deleteStock = async (stock: any) => {
  console.log('[DatabaseManager] deleteStock 开始')

  try {
    console.log('[DatabaseManager] deleteStock called with:', stock)
    const stockCode = stock._original?.code || stock.code
    const stockName = stock.name || stockCode

    console.log('[DatabaseManager] 准备删除股票:', stockCode, stockName)

    // 检查 ElMessageBox 是否可用
    if (typeof ElMessageBox === 'undefined') {
      console.error('[DatabaseManager] ElMessageBox 未定义')
      ElMessage.error('组件未正确加载，请刷新页面')
      return
    }

    console.log('[DatabaseManager] ElMessageBox 可用，准备弹出确认对话框')

    try {
      await ElMessageBox.confirm(
        `确定要删除 ${stockCode} ${stockName} 的数据吗？此操作不可恢复！`,
        '确认删除',
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        }
      )
      console.log('[DatabaseManager] 用户确认删除')
    } catch (confirmError: any) {
      if (confirmError === 'cancel') {
        console.log('[DatabaseManager] 用户取消删除')
        return
      }
      console.error('[DatabaseManager] 确认对话框错误:', confirmError)
      throw confirmError
    }

    console.log('[DatabaseManager] 开始调用API删除:', stockCode)

    const response = await databaseApi.deleteStockData(stockCode)

    console.log('[DatabaseManager] API响应:', response)

    if (response.code === 200 || response.data?.success) {
      ElMessage.success('删除成功')
      console.log('[DatabaseManager] 删除成功，准备刷新数据库')
      // 刷新数据库
      await refreshDatabase()
      console.log('[DatabaseManager] 数据库刷新完成')
    } else {
      throw new Error(response.message || '删除失败')
    }
  } catch (error: any) {
    console.error('[DatabaseManager] 删除过程出错:', error)
    ElMessage.error(`删除失败: ${error.message || error}`)
  }
}

// 🔧 定义 emit，向父组件传递选中的标的、频率和数据库扫描结果
const emit = defineEmits<{
  'update:selectedStocks': [stocks: any[]]
  'update:selectedStockCodes': [codes: string[]]
  'update:selectedFrequencies': [frequencies: string[]]
  'update:databaseStats': [stats: any]
}>()

// 🔧 表格引用（用于程序化操作选中状态）
const tableRef = ref<InstanceType<typeof ElTable>>()

// 🔧 标记是否正在恢复选中状态（防止事件循环）
const isRestoring = ref(false)

// 处理选择变化
const handleSelectionChange = (selection: any[]) => {
  // 🔧 如果正在恢复选中状态，不处理事件（防止循环）
  if (isRestoring.value) {
    return
  }

  selectedStocks.value = selection

  // 🔧 向父组件发送选中的标的列表
  emit('update:selectedStocks', selection)

  // 🔧 向父组件发送选中的标的代码列表（使用 code_frequency 组合格式）
  const codeFrequencyPairs = selection.map((s: any) => {
    const code = s._original?.code || s.code
    const frequency = s._original?.frequency || s.frequency || 'daily'
    return `${code}_${frequency}`
  })

  emit('update:selectedStockCodes', codeFrequencyPairs)
}

// 批量操作
const handleBatchAction = async (command: string) => {
  if (selectedStocks.value.length === 0) {
    ElMessage.warning('请先选择股票')
    return
  }

  switch (command) {
    case 'update':
      // 批量更新选中的股票
      try {
        const codes = selectedStocks.value.map((s: any) => s._original?.code || s.displayCode) // 🔧 使用 _original.code 或 displayCode
        loading.value = true

        // 🔧 依次更新每只股票（不每次都刷新，等全部完成后再刷新）
        for (const stock of selectedStocks.value) {
          // 🔧 调用更新但不触发 refreshDatabase
          await updateStockWithoutRefresh(stock)
        }

        // 🔧 所有更新完成后，统一刷新一次数据库（强制刷新，忽略缓存）
        await refreshDatabase()

        ElMessage.success(`批量更新完成: ${codes.length} 只股票`)
      } catch (error: any) {
        ElMessage.error(`批量更新失败: ${error.message}`)
      } finally {
        loading.value = false
      }
      break
    case 'export':
      // 导出选中股票的清单为 CSV
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

  // 构建 CSV 内容
  const headers = ['股票代码', '股票名称', '周期', '开始日期', '结束日期', '记录数', '数据年龄(天)', '健康度(%)']
  const rows = selectedStocks.value.map((stock: any) => [
    stock.displayCode, // 🔧 使用 displayCode（不带频率后缀）
    stock.name,
    getFrequencyLabel(stock.frequency) || '-',
    stock.startDate,
    stock.endDate,
    stock.recordCount,
    stock.dataAge,
    stock.healthScore
  ])

  // 添加 BOM 以支持 Excel 正确显示中文
  const BOM = '\uFEFF'
  const csvContent = BOM + [
    headers.join(','),
    ...rows.map(row => row.join(','))
  ].join('\n')

  // 创建 Blob 并下载
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

// 监听周期选择变化，自动刷新数据
watch(selectedFrequencies, async (newFrequencies) => {
  // 当选择的周期变化时，重新扫描数据库
  if (newFrequencies.length > 0) {
    // 🔧 向父组件发送频率变化
    emit('update:selectedFrequencies', newFrequencies)

    await refreshDatabase()
  }
}, { deep: true })

// 初始化 - 直接调用真实 API
onMounted(async () => {
  // 自动扫描数据库（restoreSelections 会在 refreshDatabase 完成后自动调用）
  await refreshDatabase()
})
</script>

<style scoped>
.database-manager {
  padding: 16px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.section-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

.header-actions {
  display: flex;
  gap: 8px;
  align-items: center;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: var(--card-bg);
  border-radius: 8px;
  border: 1px solid var(--border-color);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  border-color: var(--primary-color);
}

.stat-icon {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
  color: white;
  border-radius: 8px;
  font-size: 20px;
  box-shadow: 0 2px 8px rgba(37, 99, 235, 0.3);
}

.stat-icon.needs-update {
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
  box-shadow: 0 2px 8px rgba(245, 158, 11, 0.3);
}

.stat-icon.success {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  box-shadow: 0 2px 8px rgba(16, 185, 129, 0.3);
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
  line-height: 1;
}

.stat-label {
  font-size: 12px;
  color: var(--text-secondary);
  margin-top: 4px;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  text-align: center;
}

.empty-icon {
  font-size: 48px;
  color: var(--text-muted);
  margin-bottom: 16px;
}

.empty-text h4 {
  margin: 0 0 8px 0;
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

.empty-text p {
  margin: 0;
  font-size: 14px;
  color: var(--text-secondary);
}

.pagination-wrapper {
  margin-top: 16px;
  display: flex;
  justify-content: center;
}

.text-danger {
  color: #f56c6c;
}

.text-warning {
  color: #e6a23c;
}

.text-success {
  color: #67c23a;
}

/* 自定义按钮样式 - 统一风格 */
.custom-primary-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 10px 20px;
  background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%) !important;
  color: white !important;
  border: none !important;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
}

.custom-primary-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(37, 99, 235, 0.4);
  filter: brightness(1.1);
}

.custom-primary-btn:active:not(:disabled) {
  transform: scale(0.98);
}

.custom-secondary-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 8px 16px;
  background: var(--card-bg) !important;
  color: var(--text-primary) !important;
  border: 1px solid var(--border-color) !important;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.custom-secondary-btn:hover:not(:disabled) {
  background: var(--hover-bg) !important;
  border-color: var(--primary-color) !important;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(37, 99, 235, 0.2);
}

.custom-secondary-btn:active:not(:disabled) {
  transform: scale(0.98);
}

/* ==================== 表格自定义样式 ==================== */
/* 表格容器 */
.stocks-section :deep(.el-table) {
  background: transparent;
  border-radius: 12px;
  overflow: hidden;
  border: none;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

/* 表格头部 */
.stocks-section :deep(.el-table__header-wrapper) {
  background: linear-gradient(180deg, rgba(37, 99, 235, 0.05) 0%, transparent 100%);
}

.stocks-section :deep(.el-table__header th) {
  background: transparent !important;
  color: var(--text-primary) !important;
  font-weight: 600;
  font-size: 13px;
  border-bottom: none;
  padding: 16px 12px;
  text-align: center;
  letter-spacing: 0.5px;
}

.stocks-section :deep(.el-table__header tr) {
  background: transparent !important;
}

/* 隐藏排序指示器（小点） */
.stocks-section :deep(.el-table__header th .caret-wrapper) {
  display: none;
}

/* 表格单元格内边距优化 */
.stocks-section :deep(.el-table__body td) {
  border-bottom: none;
  padding: 14px 12px;
  color: var(--text-secondary);
}

/* 表格行样式 */
.stocks-section :deep(.el-table__body tr) {
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  background: transparent !important;
  border-bottom: 1px solid rgba(0, 0, 0, 0.04);
}

.stocks-section :deep(.el-table__body tr:last-child) {
  border-bottom: none;
}

/* 表格行悬停效果 */
.stocks-section :deep(.el-table__body tr:hover > td) {
  background: rgba(37, 99, 235, 0.04) !important;
}

.stocks-section :deep(.el-table__body tr:hover) {
  transform: scale(1.002);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.stocks-section :deep(.el-table__body tr.current-row > td) {
  background: rgba(37, 99, 235, 0.08) !important;
}

/* 移除表格边框 */
.stocks-section :deep(.el-table--border .el-table__cell) {
  border-right: none;
}

.stocks-section :deep(.el-table--border::after),
.stocks-section :deep(.el-table--group::after),
.stocks-section :deep(.el-table::before) {
  display: none;
}

/* 斑马纹效果 */
.stocks-section :deep(.el-table__body tr:nth-child(even)) {
  background: rgba(0, 0, 0, 0.01) !important;
}

/* 空表格状态 */
.stocks-section :deep(.el-table__empty-block) {
  background: var(--bg-surface);
  color: var(--text-secondary);
}

.stocks-section :deep(.el-table__empty-text) {
  color: var(--text-secondary);
}

/* ==================== 表格内组件样式 ==================== */
/* 按钮组 - 移除外边框并居中 */
.stocks-section :deep(.el-button-group) {
  border: none;
  border-radius: 0;
  overflow: visible;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

/* 复选框列居中对齐 */
.stocks-section :deep(.el-table__body td.el-table__cell:nth-child(1)),
.stocks-section :deep(.el-table__header th.el-table__cell:nth-child(1)) {
  text-align: center !important;
  vertical-align: middle;
}

/* 股票代码列居中对齐 */
.stocks-section :deep(.el-table__body td.el-table__cell:nth-child(2)),
.stocks-section :deep(.el-table__header th.el-table__cell:nth-child(2)) {
  text-align: center !important;
  vertical-align: middle;
}

/* 记录数列单元格居中对齐 */
.stocks-section :deep(.el-table__body td.el-table__cell:nth-child(5)),
.stocks-section :deep(.el-table__header th.el-table__cell:nth-child(5)) {
  text-align: center !important;
  vertical-align: middle;
}

/* 数据年龄列单元格居中对齐 */
.stocks-section :deep(.el-table__body td.el-table__cell:nth-child(6)),
.stocks-section :deep(.el-table__header th.el-table__cell:nth-child(6)) {
  text-align: center !important;
  vertical-align: middle;
}

/* 健康度列单元格居中对齐 */
.stocks-section :deep(.el-table__body td.el-table__cell:nth-child(7)),
.stocks-section :deep(.el-table__header th.el-table__cell:nth-child(7)) {
  text-align: center !important;
  vertical-align: middle !important;
}

/* 健康度列表头强制居中 */
.stocks-section :deep(.el-table__header th.el-table__cell:nth-child(7) .cell) {
  text-align: center !important;
  justify-content: center !important;
  display: flex !important;
  align-items: center !important;
}

/* 操作列单元格居中对齐 */
.stocks-section :deep(.el-table__body td.el-table__cell:nth-child(8)),
.stocks-section :deep(.el-table__header th.el-table__cell:nth-child(8)) {
  text-align: center;
  vertical-align: middle;
}

.stocks-section :deep(.el-button-group .el-button) {
  background: transparent;
  border: none;
  color: var(--text-secondary);
  padding: 6px 8px;
  transition: all 0.2s ease;
}

.stocks-section :deep(.el-button-group .el-button:hover) {
  background: var(--primary-color);
  color: white;
  transform: scale(1.1);
}

.stocks-section :deep(.el-button-group .el-button--danger:hover) {
  background: #f56c6c;
}

/* Tag 标签 */
.stocks-section :deep(.el-tag) {
  border-radius: 12px;
  padding: 2px 10px;
  font-weight: 500;
  border: none;
}

.stocks-section :deep(.el-tag--success) {
  background: linear-gradient(135deg, rgba(103, 194, 58, 0.15) 0%, rgba(103, 194, 58, 0.08) 100%);
  color: #67c23a;
}

.stocks-section :deep(.el-tag--warning) {
  background: linear-gradient(135deg, rgba(230, 162, 60, 0.15) 0%, rgba(230, 162, 60, 0.08) 100%);
  color: #e6a23c;
}

.stocks-section :deep(.el-tag--danger) {
  background: linear-gradient(135deg, rgba(245, 108, 108, 0.15) 0%, rgba(245, 108, 108, 0.08) 100%);
  color: #f56c6c;
}

/* Progress 进度条 */
.stocks-section :deep(.el-progress) {
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.stocks-section :deep(.el-progress-bar__outer) {
  background: var(--border-color);
  border-radius: 4px;
  height: 6px !important;
}

.stocks-section :deep(.el-progress-bar__inner) {
  border-radius: 4px;
  transition: all 0.3s ease;
}

/* 分页样式 */
.pagination-wrapper :deep(.el-pagination) {
  background: transparent;
  color: var(--text-secondary);
}

.pagination-wrapper :deep(.el-pagination button) {
  background: var(--card-bg);
  border: 1px solid var(--border-color);
  color: var(--text-secondary);
  border-radius: 6px;
  transition: all 0.2s ease;
}

.pagination-wrapper :deep(.el-pagination button:hover) {
  border-color: var(--primary-color);
  color: var(--primary-color);
}

.pagination-wrapper :deep(.el-pagination .el-pager li) {
  background: var(--card-bg);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  margin: 0 2px;
  transition: all 0.2s ease;
}

.pagination-wrapper :deep(.el-pagination .el-pager li:hover) {
  border-color: var(--primary-color);
  color: var(--primary-color);
}

.pagination-wrapper :deep(.el-pagination .el-pager li.is-active) {
  background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
  border-color: transparent;
  color: white;
}

.pagination-wrapper :deep(.el-pagination .el-pager li.is-active:hover) {
  color: white;
}

.pagination-wrapper :deep(.el-pagination .el-select .el-input__wrapper) {
  background: var(--card-bg);
  border: 1px solid var(--border-color);
  border-radius: 6px;
}

.pagination-wrapper :deep(.el-pagination .el-select .el-input__wrapper:hover) {
  border-color: var(--primary-color);
}

.pagination-wrapper :deep(.el-pagination .el-select .el-input__inner) {
  color: var(--text-secondary);
}

/* 分页器容器布局 */
.pagination-wrapper {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 0;
}

.pagination-info {
  font-size: 13px;
  color: var(--text-secondary);
  font-weight: 500;
}

.pagination-wrapper :deep(.el-pagination) {
  flex: 1;
  display: flex;
  justify-content: flex-end;
}

/* 搜索框样式 - 完全复制股票选择节点的样式 */
.stocks-section .search-input {
  width: 200px;
  margin-right: 8px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 6px;
  padding: 10px 12px;
  color: rgba(255, 255, 255, 0.9);
  font-size: 14px;
  transition: all 0.2s ease;
}

.stocks-section .search-input:focus {
  outline: none;
  border-color: #2563eb;
  background: rgba(255, 255, 255, 0.08);
}

.stocks-section .search-input::placeholder {
  color: rgba(255, 255, 255, 0.4);
}

/* 周期筛选样式 */
.frequency-filter {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 12px 8px 0;
  margin-right: 16px;
}

.filter-label {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-secondary);
  white-space: nowrap;
}

.frequency-chips {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.freq-chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  cursor: pointer;
  transition: all 0.2s ease;
  user-select: none;
}

.freq-chip:hover {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(255, 255, 255, 0.2);
}

.freq-chip.active {
  background: rgba(37, 99, 235, 0.2);
  border-color: #2563eb;
  color: #60a5fa;
}

.freq-chip input[type="checkbox"] {
  display: none;
}

.freq-chip span {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-secondary);
}

.freq-chip.active span {
  color: #60a5fa;
}

/* 下拉菜单样式 - 强制覆盖 */
.stocks-section :deep(.el-dropdown-menu) {
  background: #1e293b !important;
  border: 1px solid #334155 !important;
  border-radius: 8px !important;
  padding: 8px !important;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3) !important;
  min-width: 170px !important;
}

/* Element Plus 使用 el-dropdown-item (带连字符) */
.stocks-section :deep(.el-dropdown-menu .el-dropdown-menu__item) {
  color: #94a3b8 !important;
  border-radius: 6px !important;
  padding: 12px 16px !important;
  transition: all 0.2s ease !important;
  font-size: 14px !important;
  font-weight: 500 !important;
  display: flex !important;
  align-items: center !important;
  gap: 10px !important;
  margin: 3px 0 !important;
  background: transparent !important;
}

.stocks-section :deep(.el-dropdown-menu .el-dropdown-menu__item:hover) {
  background: #3b82f6 !important;
  color: #ffffff !important;
  cursor: pointer !important;
  transform: translateX(4px) !important;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4) !important;
  border: 1px solid #60a5fa !important;
}

.stocks-section :deep(.el-dropdown-menu .el-dropdown-menu__item i),
.stocks-section :deep(.el-dropdown-menu .el-dropdown-menu__item svg) {
  width: 18px !important;
  text-align: center !important;
  transition: all 0.2s ease !important;
  color: #94a3b8 !important;
}

.stocks-section :deep(.el-dropdown-menu .el-dropdown-menu__item:hover i),
.stocks-section :deep(.el-dropdown-menu .el-dropdown-menu__item:hover svg) {
  transform: scale(1.2) !important;
  color: #ffffff !important;
}

/* 批量操作按钮样式 */
.stocks-section :deep(.el-button) {
  background: var(--card-bg);
  border: 1px solid var(--border-color);
  color: var(--text-secondary);
  border-radius: 8px;
  padding: 8px 16px;
  font-size: 13px;
  font-weight: 500;
  transition: all 0.2s ease;
}

.stocks-section :deep(.el-button:hover:not(:disabled)) {
  background: var(--hover-bg);
  border-color: var(--primary-color);
  color: var(--primary-color);
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(37, 99, 235, 0.2);
}

.stocks-section :deep(.el-button:active:not(:disabled)) {
  transform: translateY(0);
}

.stocks-section :deep(.el-button.is-disabled) {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 加载遮罩 */
.stocks-section :deep(.el-loading-mask) {
  background: rgba(0, 0, 0, 0.5);
  border-radius: 8px;
}

.stocks-section :deep(.el-loading-spinner .el-loading-text) {
  color: var(--text-primary);
  margin-top: 8px;
}

/* ==================== 对话框样式 ==================== */
:deep(.el-dialog) {
  background: var(--bg-elevated);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
}

:deep(.el-dialog__header) {
  border-bottom: 1px solid var(--border-color);
  padding: 16px 20px;
}

:deep(.el-dialog__title) {
  color: var(--text-primary);
  font-size: 16px;
  font-weight: 600;
}

:deep(.el-dialog__body) {
  padding: 20px;
}

:deep(.el-dialog__headerbtn .el-dialog__close) {
  color: var(--text-secondary);
  transition: color 0.2s ease;
}

:deep(.el-dialog__headerbtn:hover .el-dialog__close) {
  color: var(--primary-color);
}

/* 描述列表 */
:deep(.el-descriptions) {
  background: transparent;
}

:deep(.el-descriptions__header) {
  background: var(--bg-surface);
  color: var(--text-primary);
}

:deep(.el-descriptions__body .el-descriptions__table) {
  background: var(--bg-surface);
}

:deep(.el-descriptions__body .el-descriptions__table .el-descriptions__cell) {
  background: var(--bg-surface);
  border-color: var(--border-color);
  color: var(--text-secondary);
}

:deep(.el-descriptions__label) {
  font-weight: 500;
  color: var(--text-primary);
}

:deep(.el-descriptions__content) {
  color: var(--text-secondary);
}

/* 分割线 */
:deep(.el-divider) {
  border-color: var(--border-color);
}

/* 对话框确认框样式 */
:deep(.el-message-box) {
  background: var(--bg-elevated);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
}

:deep(.el-message-box__header) {
  padding: 16px 20px;
  border-bottom: 1px solid var(--border-color);
}

:deep(.el-message-box__title) {
  color: var(--text-primary);
  font-weight: 600;
}

:deep(.el-message-box__content) {
  padding: 20px;
  color: var(--text-secondary);
}

:deep(.el-message-box__btns) {
  padding: 12px 20px 16px;
  border-top: 1px solid var(--border-color);
}

:deep(.el-message-box__btn .el-button) {
  border-radius: 8px;
  padding: 8px 20px;
  font-weight: 500;
}
</style>

<!-- 全局样式：处理Teleport到body的下拉菜单 -->
<style>
/* 数据库管理节点的下拉菜单全局样式 */
.el-dropdown-menu[data-popper-placement][class*="bottom"] {
  background: #1e293b !important;
  border: 1px solid #334155 !important;
  border-radius: 8px !important;
  padding: 8px !important;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3) !important;
  min-width: 170px !important;
}

.el-dropdown-menu__item {
  color: #94a3b8 !important;
  border-radius: 6px !important;
  padding: 12px 16px !important;
  transition: color 0.2s ease !important;
  font-size: 14px !important;
  font-weight: 500 !important;
  display: flex !important;
  align-items: center !important;
  gap: 10px !important;
  margin: 3px 0 !important;
  background: transparent !important;
}

.el-dropdown-menu__item:hover {
  color: #3b82f6 !important;
  cursor: pointer !important;
}

.el-dropdown-menu__item i,
.el-dropdown-menu__item svg {
  width: 18px !important;
  text-align: center !important;
  color: #94a3b8 !important;
  transition: color 0.2s ease !important;
}

.el-dropdown-menu__item:hover i,
.el-dropdown-menu__item:hover svg {
  color: #3b82f6 !important;
}
</style>

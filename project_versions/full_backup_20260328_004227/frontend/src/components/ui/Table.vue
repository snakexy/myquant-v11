<template>
  <div :class="containerClass">
    <!-- 工具栏 -->
    <div v-if="showToolbar" class="quant-table__toolbar">
      <div class="quant-table__toolbar-left">
        <slot name="toolbar-left" />
      </div>
      <div class="quant-table__toolbar-right">
        <slot name="toolbar-right">
          <QuantInput
            v-if="searchable"
            v-model="searchQuery"
            placeholder="搜索..."
            size="small"
            clearable
            prefix-icon="SearchOutline"
            class="quant-table__search"
          />
        </slot>
      </div>
    </div>
    
    <!-- 表格容器 -->
    <div :class="tableWrapperClass">
      <table :class="tableClass">
        <!-- 表头 -->
        <thead v-if="showHeader" :class="headerClass">
          <tr>
            <th
              v-for="column in columns"
              :key="column.key"
              :class="getHeaderCellClass(column)"
              :style="getHeaderCellStyle(column)"
              @click="handleHeaderClick(column)"
            >
              <div class="quant-table__header-cell-content">
                <span v-if="column.title" class="quant-table__header-title">
                  {{ column.title }}
                </span>
                <slot
                  v-else
                  :name="`header-${column.key}`"
                  :column="column"
                />
                
                <!-- 排序图标 -->
                <div v-if="column.sortable" class="quant-table__sort-icons">
                  <n-icon
                    :class="getSortIconClass(column, 'asc')"
                    size="12"
                  >
                    <ChevronUpOutline />
                  </n-icon>
                  <n-icon
                    :class="getSortIconClass(column, 'desc')"
                    size="12"
                  >
                    <ChevronDownOutline />
                  </n-icon>
                </div>
              </div>
            </th>
          </tr>
        </thead>
        
        <!-- 表体 -->
        <tbody :class="bodyClass">
          <template v-if="paginatedData.length > 0">
            <tr
              v-for="(row, rowIndex) in paginatedData"
              :key="getRowKey(row, rowIndex)"
              :class="getRowClass(row, rowIndex)"
              @click="handleRowClick(row, rowIndex)"
              @dblclick="handleRowDblClick(row, rowIndex)"
            >
              <td
                v-for="column in columns"
                :key="column.key"
                :class="getCellClass(column, row, rowIndex)"
                :style="getCellStyle(column)"
              >
                <slot
                  :name="`cell-${column.key}`"
                  :row="row"
                  :column="column"
                  :value="getCellValue(row, column)"
                  :rowIndex="rowIndex"
                >
                  <span v-if="column.render" v-html="column.render(row, column)" />
                  <span v-else>{{ getCellValue(row, column) }}</span>
                </slot>
              </td>
            </tr>
          </template>
          <tr v-else class="quant-table__empty-row">
            <td :colspan="columns.length" class="quant-table__empty-cell">
              <div class="quant-table__empty-content">
                <n-icon size="48" class="quant-table__empty-icon">
                  <FileTrayOutline />
                </n-icon>
                <div class="quant-table__empty-text">{{ emptyText }}</div>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    
    <!-- 分页 -->
    <div v-if="paginated && total > pageSize" class="quant-table__pagination">
      <n-pagination
        v-model:page="currentPage"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="pageSizes"
        show-size-picker
        show-quick-jumper
        @update:page="handlePageChange"
        @update:page-size="handlePageSizeChange"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch, onMounted } from 'vue'
import { NIcon, NPagination } from 'naive-ui'
import {
  ChevronUpOutline,
  ChevronDownOutline,
  SearchOutline,
  FileTrayOutline
} from '@vicons/ionicons5'
import QuantInput from './Input.vue'
import type { TableColumn } from '@/types/components'

interface Props {
  data: any[]
  columns: TableColumn[]
  size?: 'small' | 'medium' | 'large'
  striped?: boolean
  bordered?: boolean
  hoverable?: boolean
  showHeader?: boolean
  showToolbar?: boolean
  searchable?: boolean
  paginated?: boolean
  pageSize?: number
  pageSizes?: number[]
  emptyText?: string
  rowKey?: string | ((row: any) => string | number)
  defaultSort?: {
    key: string
    order: 'asc' | 'desc'
  }
  loading?: boolean
  height?: string | number
  maxHeight?: string | number
}

const props = withDefaults(defineProps<Props>(), {
  data: () => [],
  columns: () => [],
  size: 'medium',
  striped: true,
  bordered: false,
  hoverable: true,
  showHeader: true,
  showToolbar: false,
  searchable: false,
  paginated: false,
  pageSize: 10,
  pageSizes: () => [10, 20, 50, 100],
  emptyText: '暂无数据',
  rowKey: 'id',
  defaultSort: undefined,
  loading: false,
  height: 'auto',
  maxHeight: 'auto'
})

const emit = defineEmits<{
  rowClick: [row: any, index: number]
  rowDblClick: [row: any, index: number]
  sortChange: [column: TableColumn, order: 'asc' | 'desc' | null]
  pageChange: [page: number]
  pageSizeChange: [pageSize: number]
}>()

const searchQuery = ref('')
const currentPage = ref(1)
const pageSize = ref(props.pageSize)
const sortKey = ref(props.defaultSort?.key || '')
const sortOrder = ref(props.defaultSort?.order || null)

// 过滤后的数据
const filteredData = computed(() => {
  if (!searchQuery.value.trim()) {
    return props.data
  }
  
  const query = searchQuery.value.toLowerCase()
  return props.data.filter(row => {
    return props.columns.some(column => {
      const value = getCellValue(row, column)
      return value != null && value.toString().toLowerCase().includes(query)
    })
  })
})

// 排序后的数据
const sortedData = computed(() => {
  if (!sortKey.value || !sortOrder.value) {
    return filteredData.value
  }
  
  const column = props.columns.find(col => col.key === sortKey.value)
  if (!column) return filteredData.value
  
  return [...filteredData.value].sort((a, b) => {
    const valueA = getCellValue(a, column)
    const valueB = getCellValue(b, column)
    
    if (valueA === valueB) return 0
    
    let result = 0
    if (valueA < valueB) result = -1
    else if (valueA > valueB) result = 1
    
    return sortOrder.value === 'asc' ? result : -result
  })
})

// 分页后的数据
const paginatedData = computed(() => {
  if (!props.paginated) {
    return sortedData.value
  }
  
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return sortedData.value.slice(start, end)
})

// 总数
const total = computed(() => filteredData.value.length)

const containerClass = computed(() => {
  const classes = ['quant-table']
  
  if (props.size) classes.push(`quant-table--${props.size}`)
  if (props.striped) classes.push('quant-table--striped')
  if (props.bordered) classes.push('quant-table--bordered')
  if (props.hoverable) classes.push('quant-table--hoverable')
  if (props.loading) classes.push('quant-table--loading')
  
  return classes
})

const tableWrapperClass = computed(() => {
  const classes = ['quant-table__wrapper']
  
  if (props.height !== 'auto') {
    classes.push('quant-table__wrapper--fixed-height')
  }
  
  return classes
})

const tableClass = computed(() => {
  const classes = ['quant-table__table']
  
  if (props.size) classes.push(`quant-table__table--${props.size}`)
  
  return classes
})

const headerClass = computed(() => {
  return ['quant-table__header']
})

const bodyClass = computed(() => {
  return ['quant-table__body']
})

const getRowKey = (row: any, index: number) => {
  if (typeof props.rowKey === 'function') {
    return props.rowKey(row)
  }
  return row[props.rowKey] || index
}

const getCellValue = (row: any, column: TableColumn) => {
  if (column.dataIndex) {
    return row[column.dataIndex]
  }
  return row[column.key]
}

const getHeaderCellClass = (column: TableColumn) => {
  const classes = ['quant-table__header-cell']
  
  if (column.sortable) classes.push('quant-table__header-cell--sortable')
  if (column.align) classes.push(`quant-table__header-cell--${column.align}`)
  if (column.width) classes.push('quant-table__header-cell--fixed')
  
  return classes
}

const getHeaderCellStyle = (column: TableColumn) => {
  const style: Record<string, string> = {}
  
  if (column.width) style.width = column.width
  if (column.minWidth) style.minWidth = column.minWidth
  
  return style
}

const getRowClass = (row: any, index: number) => {
  const classes = ['quant-table__row']
  
  if (props.striped && index % 2 === 1) classes.push('quant-table__row--striped')
  
  return classes
}

const getCellClass = (column: TableColumn, row: any, rowIndex: number) => {
  const classes = ['quant-table__cell']
  
  if (column.align) classes.push(`quant-table__cell--${column.align}`)
  
  return classes
}

const getCellStyle = (column: TableColumn) => {
  const style: Record<string, string> = {}
  
  if (column.width) style.width = column.width
  if (column.minWidth) style.minWidth = column.minWidth
  
  return style
}

const getSortIconClass = (column: TableColumn, order: 'asc' | 'desc') => {
  const classes = ['quant-table__sort-icon']
  
  if (sortKey.value === column.key && sortOrder.value === order) {
    classes.push('quant-table__sort-icon--active')
  }
  
  return classes
}

const handleHeaderClick = (column: TableColumn) => {
  if (!column.sortable) return
  
  if (sortKey.value === column.key) {
    if (sortOrder.value === 'asc') {
      sortOrder.value = 'desc'
    } else if (sortOrder.value === 'desc') {
      sortOrder.value = null
      sortKey.value = ''
    } else {
      sortOrder.value = 'asc'
    }
  } else {
    sortKey.value = column.key
    sortOrder.value = 'asc'
  }
  
  emit('sortChange', column, sortOrder.value)
}

const handleRowClick = (row: any, index: number) => {
  emit('rowClick', row, index)
}

const handleRowDblClick = (row: any, index: number) => {
  emit('rowDblClick', row, index)
}

const handlePageChange = (page: number) => {
  currentPage.value = page
  emit('pageChange', page)
}

const handlePageSizeChange = (size: number) => {
  pageSize.value = size
  currentPage.value = 1
  emit('pageSizeChange', size)
}

// 监听搜索查询变化
watch(searchQuery, () => {
  currentPage.value = 1
})

// 监听数据变化
watch(() => props.data, () => {
  currentPage.value = 1
})

// 监听pageSize变化
watch(() => props.pageSize, (newSize) => {
  pageSize.value = newSize
  currentPage.value = 1
})
</script>

<style lang="scss" scoped>
.quant-table {
  width: 100%;
  background-color: var(--bg-color-base);
  border-radius: var(--border-radius-base);
  overflow: hidden;
  
  // 工具栏
  &__toolbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: var(--spacing-3) var(--spacing-4);
    border-bottom: 1px solid var(--border-color)-base;
    background-color: var(--bg-color-secondary);
  }
  
  &__toolbar-left {
    display: flex;
    align-items: center;
    gap: var(--spacing-2);
  }
  
  &__toolbar-right {
    display: flex;
    align-items: center;
    gap: var(--spacing-2);
  }
  
  &__search {
    width: 200px;
  }
  
  // 表格容器
  &__wrapper {
    overflow-x: auto;
    
    &--fixed-height {
      height: v-bind(height);
      max-height: v-bind(maxHeight);
      overflow-y: auto;
    }
  }
  
  // 表格
  &__table {
    width: 100%;
    border-collapse: collapse;
    font-size: var(--font-size-sm);
    
    &--small {
      font-size: var(--font-size-xs);
    }
    
    &--large {
      font-size: var(--font-size-base);
    }
  }
  
  // 表头
  &__header {
    background-color: var(--bg-color-secondary);
    
    .quant-table__header-cell {
      padding: var(--spacing-3) var(--spacing-4);
      font-weight: 600;
      color: var(--text-primary);
      border-bottom: 1px solid var(--border-color)-base;
      text-align: left;
      white-space: nowrap;
      
      &--sortable {
        cursor: pointer;
        user-select: none;
        
        &:hover {
          background-color: var(--bg-color-tertiary);
        }
      }
      
      &--center {
        text-align: center;
      }
      
      &--right {
        text-align: right;
      }
      
      &--fixed {
        position: sticky;
        z-index: 1;
      }
    }
  }
  
  // 表体
  &__body {
    .quant-table__row {
      transition: background-color var(--transition-duration-base) var(--transition-timing-function-base);
      
      &:hover {
        background-color: var(--bg-color-secondary);
      }
      
      &--striped {
        background-color: var(--bg-color-secondary);
      }
    }
    
    .quant-table__cell {
      padding: var(--spacing-3) var(--spacing-4);
      color: var(--text-primary);
      border-bottom: 1px solid var(--border-color)-light;
      
      &--center {
        text-align: center;
      }
      
      &--right {
        text-align: right;
      }
    }
  }
  
  // 空状态
  &__empty-row {
    height: 200px;
  }
  
  &__empty-cell {
    padding: 0;
    border-bottom: none;
  }
  
  &__empty-content {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 200px;
    color: var(--text-muted);
  }
  
  &__empty-icon {
    margin-bottom: var(--spacing-2);
    opacity: 0.5;
  }
  
  &__empty-text {
    font-size: var(--font-size-sm);
  }
  
  // 分页
  &__pagination {
    display: flex;
    justify-content: flex-end;
    padding: var(--spacing-3) var(--spacing-4);
    border-top: 1px solid var(--border-color)-base;
    background-color: var(--bg-color-secondary);
  }
  
  // 样式变体
  &--bordered {
    .quant-table__header-cell,
    .quant-table__cell {
      border-right: 1px solid var(--border-color)-light;
    }
  }
  
  &--hoverable {
    .quant-table__row {
      &:hover {
        background-color: var(--bg-color-secondary);
      }
    }
  }
  
  &--loading {
    position: relative;
    
    &::after {
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background-color: rgba(var(--bg-color-base), 0.7);
      z-index: 10;
      cursor: not-allowed;
    }
  }
}

// 表头单元格内容
.quant-table__header-cell-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
}

.quant-table__header-title {
  flex: 1;
}

.quant-table__sort-icons {
  display: flex;
  flex-direction: column;
  margin-left: var(--spacing-1);
}

.quant-table__sort-icon {
  color: var(--text-muted);
  transition: color var(--transition-duration-base) var(--transition-timing-function-base);
  
  &--active {
    color: var(--primary-color);
  }
  
  &:hover {
    color: var(--text-secondary);
  }
}
</style>
<template>
  <div class="panel watchlist-panel">
    <!-- 分组 Tab 栏 -->
    <div class="tabs-bar">
      <button
        v-if="showScrollLeft"
        class="scroll-btn scroll-left"
        @click="scrollTabs('left')"
        title="向左滚动"
      >
        ‹
      </button>
      <div ref="tabsListRef" class="tabs-list" @scroll="updateScrollButtons">
        <div
          v-for="group in dataStore.watchlistGroups"
          :key="group.id"
          :class="['tab-item', { active: group.id === dataStore.activeGroupId }]"
          @click="selectGroup(group.id)"
          @contextmenu.prevent="showGroupMenu($event, group)"
        >
          <span class="tab-name">{{ group.name }}</span>
          <span class="tab-count">({{ group.stocks.length }})</span>
        </div>
      </div>
      <button
        v-if="showScrollRight"
        class="scroll-btn scroll-right"
        @click="scrollTabs('right')"
        title="向右滚动"
      >
        ›
      </button>
      <button class="add-tab-btn" @click="createNewGroup" title="新建分组">+</button>
      <button class="monitor-btn" @click="showMonitor" title="调度器监控">🔧</button>
    </div>

    <!-- 分组右键菜单 -->
    <div
      v-if="groupMenuVisible"
      class="context-menu"
      :style="{ left: groupMenuX + 'px', top: groupMenuY + 'px' }"
      @click="hideGroupMenu"
    >
      <div class="menu-item" @click.stop="showRenameDialog">{{ isZh ? '重命名' : 'Rename' }}</div>
      <div class="menu-item" @click.stop="showRefreshIntervalDialog">{{ isZh ? '设置刷新频率' : 'Refresh Rate' }}</div>
      <div
        :class="['menu-item', { checked: selectedGroupForMenu?.preheat }]"
        @click.stop="togglePreheat"
      >
        <span>{{ isZh ? '启动时预加载' : 'Preheat' }}</span>
        <span v-if="selectedGroupForMenu?.preheat" class="check-mark">✓</span>
      </div>
      <div
        v-if="(dataStore.watchlistGroups?.length ?? 0) > 1"
        class="menu-item danger"
        @click.stop="deleteGroup"
      >
        {{ isZh ? '删除分组' : 'Delete' }}
      </div>
    </div>

    <!-- 重命名对话框 -->
    <div v-if="renameDialogVisible" class="dialog-overlay" @click="hideRenameDialog">
      <div class="dialog-box" @click.stop>
        <div class="dialog-header">{{ isZh ? '重命名分组' : 'Rename Group' }}</div>
        <div class="dialog-body">
          <input
            ref="renameInputRef"
            v-model="newGroupName"
            type="text"
            class="dialog-input"
            @keyup.enter="confirmRename"
            @keyup.esc="hideRenameDialog"
          />
        </div>
        <div class="dialog-footer">
          <button class="dialog-btn cancel" @click="hideRenameDialog">
            {{ isZh ? '取消' : 'Cancel' }}
          </button>
          <button class="dialog-btn confirm" @click="confirmRename">
            {{ isZh ? '确定' : 'Confirm' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 刷新频率对话框 -->
    <div v-if="refreshDialogVisible" class="dialog-overlay" @click="hideRefreshIntervalDialog">
      <div class="dialog-box" @click.stop>
        <div class="dialog-header">{{ isZh ? '设置刷新频率' : 'Set Refresh Rate' }}</div>
        <div class="dialog-body">
          <div class="refresh-options">
            <div
              v-for="option in refreshOptions"
              :key="option.value"
              :class="['refresh-option', { active: selectedRefreshInterval === option.value }]"
              @click="selectedRefreshInterval = option.value"
            >
              <span class="option-label">{{ option.label }}</span>
              <span class="option-desc">{{ option.desc }}</span>
            </div>
          </div>
        </div>
        <div class="dialog-footer">
          <button class="dialog-btn cancel" @click="hideRefreshIntervalDialog">
            {{ isZh ? '取消' : 'Cancel' }}
          </button>
          <button class="dialog-btn confirm" @click="confirmRefreshInterval">
            {{ isZh ? '确定' : 'Confirm' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 搜索添加股票 -->
    <div class="search-section">
      <StockSearchBox @select="handleAddStock" />
    </div>

    <!-- 股票列表 -->
    <div class="stock-list">
      <div
        v-for="item in displayList"
        :key="item.symbol"
        :class="['stock-item', { selected: selectedStock === item.symbol }]"
        @click="selectStock(item.symbol)"
        @contextmenu.prevent="showStockMenu($event, item.symbol)"
      >
        <!-- 股票信息（左列） -->
        <div class="stock-info">
          <div class="stock-code">{{ item.symbol }}</div>
          <div class="stock-name">{{ item.name }}</div>
        </div>

        <!-- 迷你折线图（中列） -->
        <svg v-if="miniChartsData[item.symbol]" class="mini-chart" viewBox="0 0 120 28" preserveAspectRatio="none">
          <polyline
            :points="sparklinePoints(miniChartsData[item.symbol])"
            fill="none"
            :stroke="item.change >= 0 ? '#ef5350' : '#26a69a'"
            stroke-width="1.5"
            stroke-linejoin="round"
          />
        </svg>
        <div v-else class="mini-chart"></div>

        <!-- 价格和涨跌幅（右列） -->
        <div class="stock-right">
          <div :class="['stock-price', getPriceClass(item)]">
            {{ formatPrice(item) }}
          </div>
          <div :class="['stock-change', getChangeClass(item)]">
            {{ formatChange(item) }}
          </div>
        </div>

        <!-- 删除按钮（hover显示） -->
        <div class="delete-hint" @click.stop="handleRemoveStock(item.symbol)">×</div>
      </div>

      <!-- 股票右键菜单 -->
      <div
        v-if="stockMenuVisible"
        class="context-menu stock-context-menu"
        :style="{ left: stockMenuX + 'px', top: stockMenuY + 'px' }"
        @click="hideStockMenu"
      >
        <div class="menu-item" @click.stop="handleRefreshStock">
          <span>{{ isZh ? '重新下载数据' : 'Refresh Data' }}</span>
        </div>
        <div class="menu-item danger" @click.stop="handleRemoveStockFromMenu">
          <span>{{ isZh ? '删除自选' : 'Remove' }}</span>
        </div>
      </div>

      <!-- 空状态 -->
      <div v-if="displayList.length === 0" class="empty-state">
        <div class="empty-text">{{ isZh ? '暂无自选股' : 'No stocks' }}</div>
      </div>
    </div>

    <!-- 调度器监控面板 -->
    <SchedulerMonitorPanel :visible="monitorVisible" @close="monitorVisible = false" />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { useDataStore } from '@/stores/core/DataStore'
import StockSearchBox from './StockSearchBox.vue'
import SchedulerMonitorPanel from '../monitor/SchedulerMonitorPanel.vue'
import { deleteHotDBSymbol, preheatHotDB } from '@/api/modules/quotes'

interface Props {
  selectedStock?: string
  miniChartsData?: Record<string, Array<{time: Date, close: number}>>
}

const props = withDefaults(defineProps<Props>(), {
  selectedStock: '',
  miniChartsData: () => ({})
})

const emit = defineEmits<{
  selectStock: [code: string]
}>()

const dataStore = useDataStore()
const isZh = ref(navigator.language === 'zh-CN')

// 分组右键菜单
const groupMenuVisible = ref(false)
const groupMenuX = ref(0)
const groupMenuY = ref(0)
const selectedGroupForMenu = ref<any>(null)

// 股票右键菜单
const stockMenuVisible = ref(false)
const stockMenuX = ref(0)
const stockMenuY = ref(0)
const selectedStockForMenu = ref<string>('')

// 重命名对话框
const renameDialogVisible = ref(false)
const newGroupName = ref('')
const renameInputRef = ref<HTMLInputElement | null>(null)
const renamingGroupId = ref<string | null>(null)  // 保存正在重命名的分组ID

// 刷新频率对话框
const refreshDialogVisible = ref(false)
const selectedRefreshInterval = ref(5000)

// 监控面板
const monitorVisible = ref(false)

// 刷新频率选项
const refreshOptions = computed(() => [
  { value: 3000, label: isZh.value ? '3秒 (高频)' : '3s (High)', desc: isZh.value ? '核心关注' : 'Core focus' },
  { value: 5000, label: isZh.value ? '5秒 (中频)' : '5s (Medium)', desc: isZh.value ? '一般关注' : 'Normal focus' },
  { value: 10000, label: isZh.value ? '10秒 (低频)' : '10s (Low)', desc: isZh.value ? '观察列表' : 'Watch list' },
  { value: 30000, label: isZh.value ? '30秒 (超低)' : '30s (Ultra low)', desc: isZh.value ? '长期观察' : 'Long term' }
])

// Tab 滚动相关
const tabsListRef = ref<HTMLElement | null>(null)
const showScrollLeft = ref(false)
const showScrollRight = ref(false)

// 显示列表：使用当前激活分组的股票
const displayList = computed(() => {
  const currentGroup = dataStore.activeGroup
  if (!currentGroup) return []

  return currentGroup.stocks.map(item => {
    const quote = dataStore.quotes[item.symbol]
    // 调试日志
    if (item.symbol === '601628.SH') {
      console.log('[WatchlistPanel] 中国人寿 quote:', quote)
      console.log('[WatchlistPanel] change_percent:', quote?.change_percent)
    }
    return {
      symbol: item.symbol,
      name: item.name,
      price: quote?.price ?? 0,
      change: quote?.change_percent ?? 0,
      hasQuote: !!quote
    }
  })
})

// 选中股票
const selectStock = (code: string) => {
  emit('selectStock', code)
}

// 选中分组
const selectGroup = (groupId: string) => {
  dataStore.setActiveGroup(groupId)
}

// 新建分组
const createNewGroup = () => {
  const defaultName = isZh.value ? '新建分组' : 'New Group'
  const counter = (dataStore.watchlistGroups?.length ?? 0) + 1
  const name = `${defaultName} ${counter}`

  const newGroup = dataStore.createGroup(name)
  dataStore.setActiveGroup(newGroup.id)
}

// 显示分组右键菜单
const showGroupMenu = (event: MouseEvent, group: any) => {
  selectedGroupForMenu.value = group
  groupMenuX.value = event.clientX
  groupMenuY.value = event.clientY
  groupMenuVisible.value = true
}

// 隐藏分组右键菜单
const hideGroupMenu = () => {
  groupMenuVisible.value = false
  selectedGroupForMenu.value = null
}

// 显示重命名对话框
const showRenameDialog = () => {
  if (!selectedGroupForMenu.value) return
  // 保存分组ID，因为 hideGroupMenu() 会清空 selectedGroupForMenu
  renamingGroupId.value = selectedGroupForMenu.value.id
  newGroupName.value = selectedGroupForMenu.value.name
  renameDialogVisible.value = true
  hideGroupMenu()

  // 聚焦输入框
  nextTick(() => {
    renameInputRef.value?.focus()
    renameInputRef.value?.select()
  })
}

// 隐藏重命名对话框
const hideRenameDialog = () => {
  renameDialogVisible.value = false
  newGroupName.value = ''
}

// 确认重命名
const confirmRename = () => {
  console.log('[confirmRename] 开始执行')
  console.log('[confirmRename] renamingGroupId:', renamingGroupId.value)
  console.log('[confirmRename] newGroupName:', newGroupName.value)

  if (!renamingGroupId.value) {
    console.warn('[confirmRename] 没有正在重命名的分组')
    return
  }

  const name = newGroupName.value.trim()
  console.log('[confirmRename] 处理后的名称:', name)

  if (name) {
    console.log('[confirmRename] 调用 dataStore.renameGroup:', renamingGroupId.value, name)
    dataStore.renameGroup(renamingGroupId.value, name)
    console.log('[confirmRename] renameGroup 调用完成')
  } else {
    console.warn('[confirmRename] 名称为空，不执行重命名')
  }

  hideRenameDialog()
}

// 显示刷新频率对话框
const showRefreshIntervalDialog = () => {
  if (!selectedGroupForMenu.value) return

  selectedRefreshInterval.value = selectedGroupForMenu.value.refreshInterval || 5000
  refreshDialogVisible.value = true
  hideGroupMenu()
}

// 隐藏刷新频率对话框
const hideRefreshIntervalDialog = () => {
  refreshDialogVisible.value = false
}

// 确认刷新频率
const confirmRefreshInterval = () => {
  if (!selectedGroupForMenu.value) return

  dataStore.setGroupRefreshInterval(selectedGroupForMenu.value.id, selectedRefreshInterval.value)
  hideRefreshIntervalDialog()
}

// 切换预热状态
const togglePreheat = () => {
  if (!selectedGroupForMenu.value) return

  const newPreheatState = !selectedGroupForMenu.value.preheat
  dataStore.setGroupPreheat(selectedGroupForMenu.value.id, newPreheatState)
  hideGroupMenu()
}

// 显示监控面板
const showMonitor = () => {
  monitorVisible.value = true
}

// 删除分组
const deleteGroup = () => {
  if (!selectedGroupForMenu.value) return

  const confirmMsg = isZh.value
    ? `确定要删除分组"${selectedGroupForMenu.value.name}"吗？`
    : `Delete group "${selectedGroupForMenu.value.name}"?`

  if (confirm(confirmMsg)) {
    dataStore.deleteGroup(selectedGroupForMenu.value.id)
  }

  hideGroupMenu()
}

// 添加股票（从搜索框）- 添加到当前激活分组
const handleAddStock = async (symbol: string, name: string) => {
  const currentGroup = dataStore.activeGroup
  if (currentGroup) {
    dataStore.addToGroup(currentGroup.id, symbol, name)
  } else {
    // 如果没有分组，创建默认分组
    const newGroup = dataStore.createGroup(isZh.value ? '默认分组' : 'Default')
    dataStore.setActiveGroup(newGroup.id)
    dataStore.addToGroup(newGroup.id, symbol, name)
  }

  // 自动预热该股票数据到 HotDB
  try {
    console.log(`[handleAddStock] 预热 ${symbol} 到 HotDB`)
    const result = await preheatHotDB([symbol])
    if (result.success) {
      console.log(`[handleAddStock] ${symbol} 预热成功: 保存 ${result.saved_count} 条数据`)
    } else {
      console.warn(`[handleAddStock] ${symbol} 预热失败`)
    }
  } catch (error) {
    console.error(`[handleAddStock] ${symbol} 预热出错:`, error)
  }

  // 自动选中新添加的股票
  selectStock(symbol)
}

// 显示股票右键菜单
const showStockMenu = (event: MouseEvent, symbol: string) => {
  stockMenuX.value = event.clientX
  stockMenuY.value = event.clientY
  selectedStockForMenu.value = symbol
  stockMenuVisible.value = true
}

// 隐藏股票右键菜单
const hideStockMenu = () => {
  stockMenuVisible.value = false
  selectedStockForMenu.value = ''
}

// 重新下载单只股票数据
const handleRefreshStock = async () => {
  if (!selectedStockForMenu.value) return

  const symbol = selectedStockForMenu.value
  hideStockMenu()

  try {
    // 使用 Element Plus 消息提示
    const { ElMessage } = await import('element-plus')
    ElMessage.info(`${symbol} 正在下载最新数据...`)

    // 调用批量更新 API，下载到 HotDB（临时数据）
    const response = await fetch('/api/v5/hotdata/update-localdb', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        symbols: [symbol],
        periods: ['1d', '5m'],
        source: 'xtquant'  // 使用 XtQuant 获取更多数据
      })
    })

    if (response.ok) {
      const data = await response.json()
      if (data.success) {
        ElMessage.success(`${symbol} 数据已更新到 HotDB`)
        // 刷新行情数据
        setTimeout(() => {
          dataStore.fetchQuotes([symbol])
        }, 1000)
      } else {
        throw new Error(data.error || '下载失败')
      }
    } else {
      throw new Error('下载请求失败')
    }

  } catch (error) {
    console.error('[刷新股票] 失败:', error)
    const { ElMessage } = await import('element-plus')
    ElMessage.error(`下载失败: ${error}`)
  }
}

// 从菜单删除股票
const handleRemoveStockFromMenu = () => {
  if (selectedStockForMenu.value) {
    handleRemoveStock(selectedStockForMenu.value)
    hideStockMenu()
  }
}

// 删除股票 - 从当前激活分组删除，同时清理 HotDB 数据
const handleRemoveStock = async (symbol: string) => {
  const currentGroup = dataStore.activeGroup
  if (currentGroup) {
    // 先从分组列表中删除
    dataStore.removeFromGroup(currentGroup.id, symbol)

    // 然后异步删除 HotDB 中的数据
    try {
      const result = await deleteHotDBSymbol(symbol)
      if (result.success) {
        console.log(`[handleRemoveStock] 已删除 HotDB 中的 ${symbol} 数据`)
      } else {
        console.warn(`[handleRemoveStock] 删除 HotDB 失败: ${result.message}`)
      }
    } catch (error) {
      console.error(`[handleRemoveStock] 删除 HotDB 出错:`, error)
    }
  }
}

// 格式化价格
const formatPrice = (item: any): string => {
  if (!item.hasQuote) return '--'
  return item.price.toFixed(2)
}

// 格式化涨跌幅
const formatChange = (item: any): string => {
  if (!item.hasQuote) return '--'
  const value = item.change
  const sign = value >= 0 ? '+' : ''
  return `${sign}${value.toFixed(2)}%`
}

// 价格颜色class
const getPriceClass = (item: any): string => {
  if (!item.hasQuote) return ''
  return item.change >= 0 ? 'positive' : 'negative'
}

// 涨跌幅颜色class
const getChangeClass = (item: any): string => {
  if (!item.hasQuote) return ''
  return item.change >= 0 ? 'positive' : 'negative'
}

// SVG polyline points
const sparklinePoints = (data: Array<{time: Date, close: number}>): string => {
  if (!data || data.length < 2) return ''
  const W = 120, H = 28
  const TOTAL_TRADING_MINUTES = 240

  const prices = data.map(d => d.close)
  const min = Math.min(...prices)
  const max = Math.max(...prices)
  const range = max - min || 1

  return data.map((d) => {
    const hour = d.time.getHours()
    const minute = d.time.getMinutes()

    let tradingMinutes = (hour - 9) * 60 + (minute - 30)
    if (hour >= 13) {
      tradingMinutes -= 90
    }

    const position = tradingMinutes / TOTAL_TRADING_MINUTES
    const clampedPos = Math.max(0, Math.min(1, position))
    const x = clampedPos * W
    const y = H - ((d.close - min) / range) * (H - 4) - 2
    return `${x.toFixed(1)},${y.toFixed(1)}`
  }).join(' ')
}

// 点击其他地方关闭右键菜单
const handleClickOutside = () => {
  if (groupMenuVisible.value) {
    hideGroupMenu()
  }
  if (stockMenuVisible.value) {
    hideStockMenu()
  }
}

// Tab 滚动相关方法
const updateScrollButtons = () => {
  if (!tabsListRef.value) return

  const el = tabsListRef.value
  showScrollLeft.value = el.scrollLeft > 0
  showScrollRight.value = el.scrollLeft < el.scrollWidth - el.clientWidth
}

const scrollTabs = (direction: 'left' | 'right') => {
  if (!tabsListRef.value) return

  const el = tabsListRef.value
  const scrollAmount = 150 // 每次滚动的像素

  if (direction === 'left') {
    el.scrollBy({ left: -scrollAmount, behavior: 'smooth' })
  } else {
    el.scrollBy({ left: scrollAmount, behavior: 'smooth' })
  }
}

// 监听分组数量变化，更新滚动按钮
const watchGroups = computed(() => dataStore.watchlistGroups)

// 监听分组数量变化，更新滚动按钮
watch(() => dataStore.watchlistGroups?.length ?? 0, () => {
  nextTick(() => {
    updateScrollButtons()
  })
})

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
  // 延迟检查，等待 DOM 渲染完成
  nextTick(() => {
    updateScrollButtons()
  })
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
.panel {
  background: #131722;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

/* 分组 Tab 栏 */
.tabs-bar {
  background: #1e222d;
  display: flex;
  align-items: center;
  padding: 6px 8px 0;
  border-bottom: 1px solid #2a2e39;
  gap: 4px;
  position: relative;
}

.scroll-btn {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #2a2e39;
  border: none;
  border-radius: 4px;
  color: #787b86;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.2s;
  flex-shrink: 0;
  padding: 0;
  line-height: 1;
}

.scroll-btn:hover {
  background: #363a45;
  color: #d1d4dc;
}

.scroll-btn:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.tabs-list {
  display: flex;
  gap: 4px;
  flex: 1;
  overflow-x: auto;
  scrollbar-width: none;
  -ms-overflow-style: none;
}

.tabs-list::-webkit-scrollbar {
  display: none;
}

.tab-item {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 6px 12px;
  background: #2a2e39;
  border-radius: 4px 4px 0 0;
  cursor: pointer;
  transition: background 0.2s;
  white-space: nowrap;
  user-select: none;
}

.tab-item:hover {
  background: #363a45;
}

.tab-item.active {
  background: #363a45;
  border-bottom: 2px solid #ef5350;
}

.tab-name {
  font-size: 12px;
  color: #d1d4dc;
  font-weight: 500;
}

.tab-count {
  font-size: 11px;
  color: #787b86;
}

.add-tab-btn {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #2a2e39;
  border: none;
  border-radius: 4px;
  color: #787b86;
  font-size: 18px;
  cursor: pointer;
  transition: all 0.2s;
  flex-shrink: 0;
}

.add-tab-btn:hover {
  background: #363a45;
  color: #d1d4dc;
}

.monitor-btn {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #2a2e39;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
  flex-shrink: 0;
}

.monitor-btn:hover {
  background: #363a45;
  transform: scale(1.1);
}

/* 右键菜单 */
.context-menu {
  position: fixed;
  background: #1e222d;
  border: 1px solid #2a2e39;
  border-radius: 4px;
  padding: 4px 0;
  min-width: 120px;
  z-index: 9999;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.5);
}

.menu-item {
  padding: 8px 16px;
  font-size: 13px;
  color: #d1d4dc;
  cursor: pointer;
  transition: background 0.2s;
}

.menu-item:hover {
  background: #2a2e39;
}

.menu-item.danger {
  color: #ef5350;
}

.menu-item.danger:hover {
  background: rgba(239, 83, 80, 0.15);
}

/* 搜索区域 */
.search-section {
  padding: 10px;
  display: flex;
  gap: 6px;
  border-bottom: 1px solid #2a2e39;
}

/* 股票列表 */
.stock-list {
  flex: 1;
  overflow-y: auto;
}

.stock-list::-webkit-scrollbar {
  width: 6px;
}

.stock-list::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 3px;
}

.stock-item {
  display: grid;
  grid-template-columns: 1fr 80px 52px;
  gap: 6px;
  padding: 8px 14px;
  border-bottom: 1px solid #2a2e39;
  cursor: pointer;
  transition: background 0.15s;
  align-items: center;
  position: relative;
}

.mini-chart {
  width: 80px;
  height: 28px;
  opacity: 0.9;
}

.stock-right {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 2px;
}

.stock-item:hover {
  background: #1e222d;
}

.stock-item.selected {
  background: #2a2e39;
  border-left: 2px solid #ef5350;
}

.stock-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.stock-code {
  color: #d1d4dc;
  font-size: 13px;
  font-weight: 600;
}

.stock-name {
  color: #787b86;
  font-size: 11px;
}

.stock-price {
  text-align: right;
  font-weight: 600;
  font-size: 13px;
}

.stock-price.positive { color: #ef5350; }
.stock-price.negative { color: #26a69a; }

.stock-change {
  text-align: right;
  font-size: 11px;
  padding: 2px 6px;
  border-radius: 3px;
  font-weight: 600;
}

.stock-change.positive {
  background: rgba(239, 83, 80, 0.15);
  color: #ef5350;
}

.stock-change.negative {
  background: rgba(38, 166, 154, 0.15);
  color: #26a69a;
}

/* 删除提示 */
.delete-hint {
  position: absolute;
  right: 8px;
  top: 50%;
  transform: translateY(-50%);
  width: 18px;
  height: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(239, 83, 80, 0.8);
  border-radius: 4px;
  color: white;
  font-size: 16px;
  line-height: 1;
  cursor: pointer;
  opacity: 0;
  transition: opacity 0.2s ease;
}

.stock-item:hover .delete-hint {
  opacity: 1;
}

.delete-hint:hover {
  background: #ef5350;
}

.empty-state {
  padding: 40px 20px;
  text-align: center;
}

.empty-text {
  color: #787b86;
  font-size: 13px;
}

/* 自定义对话框 */
.dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10000;
  backdrop-filter: blur(2px);
}

.dialog-box {
  background: #1e222d;
  border: 1px solid #2a2e39;
  border-radius: 8px;
  min-width: 320px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.6);
}

.dialog-header {
  padding: 16px 20px;
  font-size: 14px;
  font-weight: 600;
  color: #d1d4dc;
  border-bottom: 1px solid #2a2e39;
}

.dialog-body {
  padding: 20px;
}

.dialog-input {
  width: 100%;
  padding: 10px 12px;
  background: #131722;
  border: 1px solid #2a2e39;
  border-radius: 4px;
  color: #d1d4dc;
  font-size: 13px;
  outline: none;
  box-sizing: border-box;
}

.dialog-input:focus {
  border-color: #ef5350;
}

.dialog-input::placeholder {
  color: #787b86;
}

.dialog-footer {
  padding: 12px 20px;
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  border-top: 1px solid #2a2e39;
}

.dialog-btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.dialog-btn.cancel {
  background: #2a2e39;
  color: #d1d4dc;
}

.dialog-btn.cancel:hover {
  background: #363a45;
}

.dialog-btn.confirm {
  background: #ef5350;
  color: white;
}

.dialog-btn.confirm:hover {
  background: #f46f6c;
}

/* 刷新频率选项 */
.refresh-options {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.refresh-option {
  display: flex;
  flex-direction: column;
  padding: 12px 16px;
  background: #131722;
  border: 1px solid #2a2e39;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.refresh-option:hover {
  background: #1e222d;
  border-color: #363a45;
}

.refresh-option.active {
  background: rgba(239, 83, 80, 0.1);
  border-color: #ef5350;
}

.option-label {
  font-size: 13px;
  font-weight: 600;
  color: #d1d4dc;
}

.option-desc {
  font-size: 11px;
  color: #787b86;
  margin-top: 2px;
}

/* 菜单项选中状态 */
.menu-item.checked {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.menu-item .check-mark {
  margin-left: auto;
  font-weight: bold;
}

.menu-item.checked:hover {
  background: rgba(16, 185, 129, 0.2);
}
</style>

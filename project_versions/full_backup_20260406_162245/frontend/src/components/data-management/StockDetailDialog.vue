<template>
  <el-dialog
    v-model="visible"
    :title="`${stockInfo.name} (${stockInfo.symbol}) - 数据管理`"
    width="700px"
    @close="handleClose"
  >
    <!-- 股票基本信息 -->
    <div class="stock-info">
      <el-tag size="large">{{ stockInfo.symbol }}</el-tag>
      <el-tag size="large" type="success">{{ stockInfo.name }}</el-tag>
      <span class="update-time" v-if="stockStatus">
        最后更新: {{ formatTime(stockStatus.updateTime) }}
      </span>
    </div>

    <!-- 数据状态概览 -->
    <div class="data-status" v-if="stockStatus">
      <div class="status-grid">
        <div
          v-for="(status, period) in stockStatus.periods"
          :key="period"
          class="status-item"
          :class="{ 'has-gap': status.hasGap, 'no-data': status.noData }"
        >
          <span class="period-label">{{ period }}</span>
          <span class="period-status">
            <el-tag v-if="status.noData" type="danger" size="small">无数据</el-tag>
            <el-tag v-else-if="status.hasGap" type="warning" size="small">有缺口</el-tag>
            <el-tag v-else type="success" size="small">正常</el-tag>
          </span>
          <span class="period-detail" v-if="!status.noData">
            {{ status.count }} 条
            <span v-if="status.latest">~ {{ status.latest.slice(0, 10) }}</span>
          </span>
        </div>
      </div>
    </div>

    <!-- 功能 Tab -->
    <el-tabs v-model="activeTab" class="function-tabs">
      <!-- 检查数据缺口 -->
      <el-tab-pane label="检查数据缺口" name="check">
        <el-form :model="checkForm" label-width="100px">
          <el-form-item label="选择周期">
            <el-checkbox-group v-model="checkForm.periods">
              <el-checkbox-button label="5m">5分钟</el-checkbox-button>
              <el-checkbox-button label="15m">15分钟</el-checkbox-button>
              <el-checkbox-button label="30m">30分钟</el-checkbox-button>
              <el-checkbox-button label="1h">1小时</el-checkbox-button>
              <el-checkbox-button label="1d">日线</el-checkbox-button>
              <el-checkbox-button label="1w">周线</el-checkbox-button>
            </el-checkbox-group>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleCheckGaps" :loading="checking">
              开始检查
            </el-button>
          </el-form-item>
        </el-form>

        <!-- 检查结果 -->
        <div v-if="gapResults.length > 0" class="gap-results">
          <h4>检查结果：</h4>
          <div v-for="gap in gapResults" :key="gap.period" class="gap-item">
            <div class="gap-header">
              <el-tag :type="gap.hasGap ? 'warning' : 'success'">{{ gap.period }}</el-tag>
              <span>{{ gap.gap_description }}</span>
            </div>
            <div class="gap-detail" v-if="gap.has_data">
              {{ gap.count }} 条 | {{ gap.earliest }} ~ {{ gap.latest }}
            </div>
          </div>
        </div>
      </el-tab-pane>

      <!-- 智能补全 -->
      <el-tab-pane label="智能补全" name="update">
        <el-form :model="updateForm" label-width="100px">
          <el-form-item label="选择周期">
            <el-checkbox-group v-model="updateForm.periods">
              <el-checkbox-button label="5m">5分钟</el-checkbox-button>
              <el-checkbox-button label="15m">15分钟</el-checkbox-button>
              <el-checkbox-button label="30m">30分钟</el-checkbox-button>
              <el-checkbox-button label="1h">1小时</el-checkbox-button>
              <el-checkbox-button label="1d">日线</el-checkbox-button>
            </el-checkbox-group>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleSmartUpdate" :loading="updating">
              开始补全
            </el-button>
          </el-form-item>
        </el-form>
        <el-alert v-if="updateResult" :type="updateResult.successCount > 0 ? 'success' : 'warning'" :closable="false">
          {{ updateResult.summary }}
        </el-alert>
      </el-tab-pane>

      <!-- 下载数据 -->
      <el-tab-pane label="下载数据" name="download">
        <el-form :model="downloadForm" label-width="100px">
          <el-form-item label="选择周期">
            <el-checkbox-group v-model="downloadForm.periods">
              <el-checkbox-button label="1m">1分钟</el-checkbox-button>
              <el-checkbox-button label="5m">5分钟</el-checkbox-button>
              <el-checkbox-button label="15m">15分钟</el-checkbox-button>
              <el-checkbox-button label="30m">30分钟</el-checkbox-button>
              <el-checkbox-button label="1h">1小时</el-checkbox-button>
              <el-checkbox-button label="1d">日线</el-checkbox-button>
              <el-checkbox-button label="1w">周线</el-checkbox-button>
              <el-checkbox-button label="1M">月线</el-checkbox-button>
            </el-checkbox-group>
          </el-form-item>
          <el-form-item label="时间范围">
            <el-date-picker
              v-model="downloadForm.dateRange"
              type="daterange"
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              format="YYYY-MM-DD"
              value-format="YYYY-MM-DD"
              style="width: 100%"
            />
          </el-form-item>
          <el-form-item label="数据源">
            <el-radio-group v-model="downloadForm.source">
              <el-radio-button label="pytdx">PyTdx</el-radio-button>
              <el-radio-button label="xtquant">XtQuant</el-radio-button>
              <el-radio-button label="tdxquant">TdxQuant</el-radio-button>
            </el-radio-group>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleDownload" :loading="downloading">
              开始下载
            </el-button>
          </el-form-item>
        </el-form>
        <el-alert v-if="downloadResult" :type="downloadResult.successCount > 0 ? 'success' : 'warning'" :closable="false">
          {{ downloadResult.summary }}
        </el-alert>
      </el-tab-pane>

      <!-- 清除数据 -->
      <el-tab-pane label="清除数据" name="clear">
        <el-form :model="clearForm" label-width="100px">
          <el-form-item label="选择周期">
            <el-checkbox-group v-model="clearForm.periods">
              <el-checkbox-button label="1m">1分钟</el-checkbox-button>
              <el-checkbox-button label="5m">5分钟</el-checkbox-button>
              <el-checkbox-button label="15m">15分钟</el-checkbox-button>
              <el-checkbox-button label="30m">30分钟</el-checkbox-button>
              <el-checkbox-button label="1h">1小时</el-checkbox-button>
              <el-checkbox-button label="1d">日线</el-checkbox-button>
              <el-checkbox-button label="1w">周线</el-checkbox-button>
              <el-checkbox-button label="1M">月线</el-checkbox-button>
            </el-checkbox-group>
          </el-form-item>
          <el-form-item>
            <el-button type="danger" @click="handleClear" :loading="clearing">
              清除选中周期
            </el-button>
          </el-form-item>
        </el-form>
        <el-alert v-if="clearResult" type="info" :closable="false">
          {{ clearResult.summary }}
        </el-alert>
      </el-tab-pane>
    </el-tabs>

    <template #footer>
      <el-button @click="handleClose">关闭</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, watch } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'

interface StockInfo {
  symbol: string
  name: string
}

interface StockStatus {
  symbol: string
  periods: Record<string, {
    count: number
    earliest?: string
    latest?: string
    hasGap?: boolean
    noData?: boolean
  }>
  updateTime?: string
}

const props = defineProps<{
  visible: boolean
  stockInfo: StockInfo
}>()

const emit = defineEmits<{
  'update:visible': [value: boolean]
  'data-updated': []
}>()

const visible = ref(props.visible)
const activeTab = ref('check')
const stockStatus = ref<StockStatus | null>(null)

// 表单数据
const checkForm = reactive({
  periods: ['5m', '15m', '30m', '1h', '1d']
})

const updateForm = reactive({
  periods: ['5m', '15m', '30m', '1h']
})

const downloadForm = reactive({
  periods: ['5m'],
  dateRange: null as [string, string] | null,
  source: 'pytdx'
})

const clearForm = reactive({
  periods: ['5m']
})

// 状态和结果
const checking = ref(false)
const updating = ref(false)
const downloading = ref(false)
const clearing = ref(false)

const gapResults = ref<any[]>([])
const updateResult = ref<any>(null)
const downloadResult = ref<any>(null)
const clearResult = ref<any>(null)

// 监听 visible 变化
watch(() => props.visible, (val) => {
  visible.value = val
  if (val) {
    loadStockStatus()
  }
})

watch(visible, (val) => {
  emit('update:visible', val)
})

// 加载股票数据状态
async function loadStockStatus() {
  try {
    const response = await axios.get(`/api/dataget/hotdb/status/${props.stockInfo.symbol}`)
    stockStatus.value = {
      ...response.data,
      periods: formatPeriodStatus(response.data.periods)
    }
  } catch (error: any) {
    console.error('加载状态失败:', error)
  }
}

function formatPeriodStatus(periods: Record<string, any>) {
  const result: Record<string, any> = {}
  for (const [period, data] of Object.entries(periods)) {
    result[period] = {
      ...data,
      hasGap: false,
      noData: !data.has_data
    }
  }
  return result
}

function formatTime(time: string) {
  if (!time) return ''
  return new Date(time).toLocaleString('zh-CN')
}

// 检查数据缺口
async function handleCheckGaps() {
  checking.value = true
  gapResults.value = []

  try {
    const response = await axios.post('/api/dataget/hotdb/check_gaps', {
      symbol: props.stockInfo.symbol,
      periods: checkForm.periods
    })

    gapResults.value = response.data.gaps
    ElMessage.success('检查完成')
  } catch (error: any) {
    ElMessage.error('检查失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    checking.value = false
  }
}

// 智能补全
async function handleSmartUpdate() {
  updating.value = true
  updateResult.value = null

  try {
    const response = await axios.post('/api/dataget/hotdb/smart_update', {
      symbol: props.stockInfo.symbol,
      periods: updateForm.periods
    })

    updateResult.value = {
      summary: response.data.summary,
      successCount: Object.values(response.data.results).filter((r: any) => r.success).length
    }

    ElMessage.success('补全完成')
    emit('data-updated')
    loadStockStatus()
  } catch (error: any) {
    ElMessage.error('补全失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    updating.value = false
  }
}

// 下载数据
async function handleDownload() {
  downloading.value = true
  downloadResult.value = null

  try {
    const [startDate, endDate] = downloadForm.dateRange || [null, null]

    const response = await axios.post('/api/dataget/hotdb/download', {
      symbol: props.stockInfo.symbol,
      periods: downloadForm.periods,
      source: downloadForm.source,
      start_date: startDate ? startDate.replace(/-/g, '') : null,
      end_date: endDate ? endDate.replace(/-/g, '') : null
    })

    downloadResult.value = {
      summary: response.data.summary,
      successCount: Object.values(response.data.results).filter((r: any) => r.success).length
    }

    ElMessage.success('下载完成')
    emit('data-updated')
    loadStockStatus()
  } catch (error: any) {
    ElMessage.error('下载失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    downloading.value = false
  }
}

// 清除数据
async function handleClear() {
  clearing.value = true
  clearResult.value = null

  try {
    const response = await axios.delete('/api/dataget/hotdb/clear', {
      data: {
        symbol: props.stockInfo.symbol,
        periods: clearForm.periods
      }
    })

    clearResult.value = response.data
    ElMessage.success('清除完成')
    emit('data-updated')
    loadStockStatus()
  } catch (error: any) {
    ElMessage.error('清除失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    clearing.value = false
  }
}

function handleClose() {
  visible.value = false
}
</script>

<style scoped>
.stock-info {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 0;
  border-bottom: 1px solid #eee;
  margin-bottom: 16px;
}

.update-time {
  margin-left: auto;
  color: #999;
  font-size: 12px;
}

.data-status {
  margin-bottom: 20px;
}

.status-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 10px;
}

.status-item {
  padding: 10px;
  border: 1px solid #eee;
  border-radius: 4px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.status-item.has-gap {
  background-color: #fef0f0;
  border-color: #fbc4c4;
}

.status-item.no-data {
  background-color: #f5f5f5;
}

.period-label {
  font-weight: bold;
}

.period-detail {
  font-size: 12px;
  color: #666;
}

.function-tabs {
  margin-top: 16px;
}

.gap-results {
  margin-top: 16px;
  padding: 12px;
  background-color: #f9f9f9;
  border-radius: 4px;
}

.gap-item {
  padding: 8px 0;
  border-bottom: 1px solid #eee;
}

.gap-item:last-child {
  border-bottom: none;
}

.gap-header {
  display: flex;
  align-items: center;
  gap: 8px;
}

.gap-detail {
  margin-left: 32px;
  font-size: 12px;
  color: #666;
}
</style>

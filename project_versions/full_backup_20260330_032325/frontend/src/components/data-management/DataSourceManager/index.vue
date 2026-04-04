<template>
  <div class="data-source-manager">
    <!-- 通达信路径配置 -->
    <div class="config-section">
      <div class="section-header">
        <h3><font-awesome-icon icon="hdd" /> 通达信离线数据源</h3>
        <div class="header-actions">
          <TDXPathConfig
            v-model:tdx-path="tdxPath"
            @select-path="selectTDXPath"
          />
          <el-button
            size="small"
            @click="detectTDX"
            :loading="detecting"
            type="primary"
          >
            <font-awesome-icon icon="search" />
            快速检测
          </el-button>
          <el-button
            size="small"
            @click="deepAnalysis"
            :loading="deepScanning"
            type="warning"
          >
            <font-awesome-icon icon="microscope" />
            深度分析
          </el-button>
        </div>
      </div>

      <ConnectionStatus :status="connectionStatus" />
    </div>

    <!-- 数据源概览 -->
    <DataSourceOverview
      v-if="connectionStatus?.connected"
      :tdx-info="tdxInfo"
      :tdx-path="tdxPath"
      :loading="detecting"
      :has-detected="!!tdxInfo"
      @refresh="detectTDX"
    />

    <!-- 转换设置 -->
    <div class="conversion-settings" v-if="tdxInfo">
      <div class="section-header">
        <h3>⚙️ 转换设置</h3>
      </div>

      <DataStatistics :tdx-info="tdxInfo" />

      <GroupedFrequencySelector
        v-model="groupedSelectedFrequencies"
        v-model:enabled-groups="enabledGroups"
        :tdx-info="tdxInfo"
        :available-frequencies="groupedAvailableFrequencies"
      />

      <!-- 高级选项 -->
      <el-collapse class="advanced-options" style="margin-top: 16px;">
        <el-collapse-item title="高级选项" name="advanced">
          <el-form label-position="top" size="small">
            <el-form-item>
              <el-checkbox v-model="advancedOptions.forwardFill">
                前向填充缺失值
              </el-checkbox>
            </el-form-item>
            <el-form-item>
              <el-checkbox v-model="advancedOptions.handleOutliers">
                异常值检测和处理
              </el-checkbox>
            </el-form-item>
            <el-form-item>
              <el-checkbox v-model="advancedOptions.normalize">
                标准化数据
              </el-checkbox>
            </el-form-item>
          </el-form>
        </el-collapse-item>
      </el-collapse>
    </div>

    <!-- 转换操作 - 只在检测连接后才显示 -->
    <div class="conversion-action" v-if="tdxInfo && !conversionResult">
      <!-- 转换中状态 -->
      <div v-if="converting" class="converting-buttons">
        <el-button
          size="large"
          @click="cancelConversion"
          class="cancel-button"
        >
          <font-awesome-icon icon="times-circle" />
          <span>取消转换</span>
        </el-button>
      </div>

      <!-- 未开始转换状态 -->
      <el-button
        v-else
        type="primary"
        size="large"
        :disabled="!canStartConversion"
        @click="startConversion"
        class="convert-button"
      >
        <font-awesome-icon icon="rocket" />
        <span>一键清洗转换为QLib格式</span>
      </el-button>

      <div class="button-tip" v-if="!converting && !canStartConversion">
        {{ getDisabledReason() }}
      </div>
    </div>

    <!-- 转换进度 -->
    <ConversionProgress :progress="conversionProgress" />

    <!-- 保存进度 -->
    <div v-if="savingProgress" class="saving-progress">
      <div class="progress-header">
        <span class="progress-label">正在保存到 QLib</span>
        <span class="progress-percent">{{ savingProgress.percent }}%</span>
      </div>

      <el-progress
        :percentage="savingProgress.percent"
        :stroke-width="16"
        status="success"
        :show-text="false"
      />

      <div class="progress-details">
        <div class="detail-item">
          <span class="detail-label">已保存:</span>
          <span class="detail-value">{{ savingProgress.current }} / {{ savingProgress.total }}</span>
        </div>
        <div class="detail-item">
          <span class="detail-label">当前标的:</span>
          <span class="detail-value">{{ savingProgress.symbol }}</span>
        </div>
        <div class="detail-item">
          <span class="detail-label">数据频率:</span>
          <span class="detail-value">{{ getFrequencyLabel(savingProgress.frequency) }}</span>
        </div>
      </div>
    </div>

    <!-- 转换完成 -->
    <div v-if="conversionResult" class="conversion-result">
      <el-result
        :icon="conversionResult.success ? 'success' : 'error'"
        :title="conversionResult.title"
        :sub-title="conversionResult.message"
      >
        <template #extra>
          <div class="result-stats">
            <div class="stat-item">
              <span class="stat-label">成功转换:</span>
              <span class="stat-value success">{{ conversionResult.successCount }} 只</span>
            </div>
            <div class="stat-item" v-if="conversionResult.failedCount > 0">
              <span class="stat-label">转换失败:</span>
              <span class="stat-value error">{{ conversionResult.failedCount }} 只</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">总耗时:</span>
              <span class="stat-value">{{ conversionResult.totalTime }}</span>
            </div>
          </div>
          <el-button type="primary" @click="resetConversion">再次转换</el-button>
        </template>
      </el-result>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import TDXPathConfig from './TDXPathConfig.vue'
import ConnectionStatus from './ConnectionStatus.vue'
import DataSourceOverview from './DataSourceOverview.vue'
import DataStatistics from './DataStatistics.vue'
import FrequencySelector from './FrequencySelector.vue'
import GroupedFrequencySelector from './GroupedFrequencySelector.vue'
import ConversionProgress from './ConversionProgress.vue'
import type { ConnectionStatus as ConnectionStatusType, TDXInfo, ConversionProgress as ConversionProgressType, ConversionResult, ConversionOptions, FrequencyType } from '@/components/data-management/shared/types'
import { AVAILABLE_FREQUENCIES } from '@/components/data-management/shared/constants'
import { formatElapsedTime } from '@/components/data-management/shared/utils'
import { API_PATHS, buildApiUrl } from '@/config/api'

const emit = defineEmits<{
  'conversion-complete': [result: ConversionResult]
}>()

// 状态
const tdxPath = ref('')
const detecting = ref(false)
const deepScanning = ref(false)
const converting = ref(false)
const cancelRequested = ref(false)

// 分组选择的频率 - 默认所有类别都勾选日线
const groupedSelectedFrequencies = ref<Record<string, FrequencyType[]>>({
  stock: ['day'],
  fund: ['day'],
  index: ['day'],
  other: ['day']
})

// 分组可用的频率
const groupedAvailableFrequencies = ref<Record<string, FrequencyType[]>>({
  stock: ['day', '5min'],
  fund: ['day', '5min'],
  index: ['day', '5min'],
  other: ['day']
})

// 启用的分组（通过复选框选择） - 默认只启用股票和指数
const enabledGroups = ref<string[]>(['stock', 'index'])

// 连接状态
const connectionStatus = ref<ConnectionStatusType | null>(null)

// TDX信息
const tdxInfo = ref<TDXInfo | null>(null)

// 高级选项
const advancedOptions = ref<ConversionOptions>({
  forwardFill: true,
  handleOutliers: false,
  normalize: false
})

// 可用频率
const availableFrequencies = ref(AVAILABLE_FREQUENCIES)

// 转换进度
const conversionProgress = ref<ConversionProgressType | null>(null)

// 保存进度
const savingProgress = ref<{ percent: number; current: number; total: number; symbol: string; frequency: string } | null>(null)

// AbortController for cancelling conversion
let abortController: AbortController | null = null

// 转换结果
const conversionResult = ref<ConversionResult | null>(null)

// 计算属性
const canStartConversion = computed(() => {
  // 检查是否有任何分组选择了频率
  const hasSelectedFrequencies = Object.values(groupedSelectedFrequencies.value).some(
    freqs => freqs.length > 0
  )

  return tdxInfo.value !== null &&
         hasSelectedFrequencies &&
         !converting.value
})

// 获取所有选中的证券类型（基于复选框状态）
const selectedSecurityTypes = computed(() => {
  return enabledGroups.value.filter(group => {
    // 只返回已启用且有选中频率的分组
    return groupedSelectedFrequencies.value[group]?.length > 0
  })
})

// 获取所有选中的频率（合并所有分组）
const allSelectedFrequencies = computed(() => {
  const allFreqs = new Set<FrequencyType>()
  Object.values(groupedSelectedFrequencies.value).forEach(freqs => {
    freqs.forEach(freq => allFreqs.add(freq))
  })
  return Array.from(allFreqs)
})

// 方法
const selectTDXPath = () => {
  ElMessage.info({
    message: '请在系统设置中配置通达信数据目录路径，或直接修改mootdx配置文件',
    duration: 5000,
    showClose: true
  })
}

// 组件挂载时自动加载通达信配置并进行检测
onMounted(async () => {
  try {
    // 创建一个超时控制器
    const controller = new AbortController()
    const timeoutId = setTimeout(() => controller.abort(), 30000) // 30秒超时

    // 调用后端API获取QuantDataHub配置的通达信路径
    const response = await fetch(buildApiUrl(API_PATHS.TDX_CONFIG), {
      signal: controller.signal
    })

    clearTimeout(timeoutId)

    if (response.ok) {
      const result = await response.json()
      if (result.success && result.data.configured) {
        tdxPath.value = result.data.data_dir
        console.log('成功加载通达信配置:', tdxPath.value)

        // 自动进行一次数据检测
        await detectTDX()
      }
    } else {
      console.warn('获取通达信配置失败，响应状态:', response.status)
    }
  } catch (error) {
    console.error('获取通达信配置失败:', error)
    // 失败时使用默认值
    tdxPath.value = ''
  }
})

const detectTDX = async () => {
  detecting.value = true
  connectionStatus.value = null

  try {
    // 创建一个超时控制器
    const controller = new AbortController()
    const timeoutId = setTimeout(() => controller.abort(), 120000) // 2分钟超时

    // 调用后端API检测通达信数据，使用深度扫描获取真实日期范围
    const response = await fetch(buildApiUrl(`${API_PATHS.TDX_DETECT}?deep_scan=true&sample_size=50`), {
      signal: controller.signal
    })

    clearTimeout(timeoutId)

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`)
    }

    const result = await response.json()

    console.log('后端返回的完整数据:', result)

    if (!result.success) {
      throw new Error(result.message || '检测失败')
    }

    const data = result.data
    console.log('解析后的数据:', data)

    connectionStatus.value = {
      connected: data.total_stocks > 0,
      message: result.message || `检测完成 - 发现 ${data.total_stocks} 只股票`
    }

    // 使用真实的检测数据
    tdxInfo.value = {
      dailyStocks: data.daily_stocks || 0,
      minute5Stocks: data.minute5_stocks || 0,
      totalStocks: data.total_stocks || 0,
      dateRange: data.date_range || '未知',
      lastUpdate: data.last_update || new Date().toLocaleDateString(),
      completeness: data.completeness || 0,
      completenessDetails: data.completeness_details || [],
      availableFrequencies: data.available_frequencies || [],
      stockCounts: data.stock_counts || { day: 0, '5min': 0 },
      fundCounts: data.fund_counts || { day: 0, '5min': 0 },
      indexCounts: data.index_counts || { day: 0, '5min': 0 },
      otherCounts: data.other_counts || { day: 0, '5min': 0 }
    }

    // 根据每个分组实际拥有的数据，确定可用的频率
    const getGroupAvailableFrequencies = (counts: any): FrequencyType[] => {
      const freqs: FrequencyType[] = []
      if (counts?.day > 0) freqs.push('day')
      if (counts?.['5min'] > 0) freqs.push('5min')
      return freqs
    }

    // 如果后端返回了分组统计，使用分组统计判断；否则所有分组都使用相同的可用频率
    const hasGroupStats = data.stock_counts !== undefined
    const availFreqs = data.available_frequencies || []

    groupedAvailableFrequencies.value = {
      stock: hasGroupStats ? getGroupAvailableFrequencies(data.stock_counts) : availFreqs,
      fund: hasGroupStats ? getGroupAvailableFrequencies(data.fund_counts) : availFreqs,
      index: hasGroupStats ? getGroupAvailableFrequencies(data.index_counts) : availFreqs,
      other: hasGroupStats ? getGroupAvailableFrequencies(data.other_counts) : availFreqs
    }

    console.log('可用频率:', availFreqs)
    console.log('是否有分组统计:', hasGroupStats)
    console.log('分组可用频率:', groupedAvailableFrequencies.value)

    console.log('设置的tdxInfo:', tdxInfo.value)
    console.log('tdxInfo.totalStocks:', tdxInfo.value.totalStocks)
    console.log('tdxInfo.completenessDetails:', tdxInfo.value.completenessDetails)
    console.log('connectionStatus:', connectionStatus.value)
    console.log('!!tdxInfo:', !!tdxInfo.value)

    ElMessage.success('通达信数据检测成功')
  } catch (error: any) {
    console.error('检测失败:', error)
    connectionStatus.value = {
      connected: false,
      message: `连接失败: ${error.message}`
    }
    ElMessage.error(`通达信数据检测失败: ${error.message}`)
  } finally {
    detecting.value = false
  }
}

const deepAnalysis = async () => {
  deepScanning.value = true
  connectionStatus.value = null

  try {
    ElMessage.info({
      message: '正在进行深度分析，这可能需要一些时间...',
      duration: 3000
    })

    // 调用后端API进行深度分析
    const params = new URLSearchParams({
      deep_scan: 'true',
      sample_size: '100'  // 抽样100只股票进行分析
    })

    // 创建一个超时控制器
    const controller = new AbortController()
    const timeoutId = setTimeout(() => controller.abort(), 180000) // 3分钟超时

    const response = await fetch(buildApiUrl(`${API_PATHS.TDX_DETECT}?${params}`), {
      signal: controller.signal
    })

    clearTimeout(timeoutId)

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`)
    }

    const result = await response.json()

    console.log('深度分析返回的完整数据:', result)

    if (!result.success) {
      throw new Error(result.message || '深度分析失败')
    }

    const data = result.data
    console.log('深度分析解析后的数据:', data)

    connectionStatus.value = {
      connected: data.total_stocks > 0,
      message: result.message || `深度分析完成 - 分析了 ${data.sample_size || 100} 只股票样本`
    }

    // 使用深度分析的真实数据
    tdxInfo.value = {
      dailyStocks: data.daily_stocks || 0,
      minute5Stocks: data.minute5_stocks || 0,
      totalStocks: data.total_stocks || 0,
      dateRange: data.date_range || '未知',
      lastUpdate: data.last_update || new Date().toLocaleDateString(),
      completeness: data.completeness || 0,
      completenessDetails: data.completeness_details || [],
      availableFrequencies: data.available_frequencies || [],
      stockCounts: data.stock_counts || { day: 0, '5min': 0 },
      fundCounts: data.fund_counts || { day: 0, '5min': 0 },
      indexCounts: data.index_counts || { day: 0, '5min': 0 },
      otherCounts: data.other_counts || { day: 0, '5min': 0 }
    }

    // 根据每个分组实际拥有的数据，确定可用的频率
    const getGroupAvailableFrequencies = (counts: any): FrequencyType[] => {
      const freqs: FrequencyType[] = []
      if (counts?.day > 0) freqs.push('day')
      if (counts?.['5min'] > 0) freqs.push('5min')
      return freqs
    }

    // 如果后端返回了分组统计，使用分组统计判断；否则所有分组都使用相同的可用频率
    const hasGroupStats = data.stock_counts !== undefined
    const availFreqs = data.available_frequencies || []

    groupedAvailableFrequencies.value = {
      stock: hasGroupStats ? getGroupAvailableFrequencies(data.stock_counts) : availFreqs,
      fund: hasGroupStats ? getGroupAvailableFrequencies(data.fund_counts) : availFreqs,
      index: hasGroupStats ? getGroupAvailableFrequencies(data.index_counts) : availFreqs,
      other: hasGroupStats ? getGroupAvailableFrequencies(data.other_counts) : availFreqs
    }

    console.log('深度分析后的tdxInfo:', tdxInfo.value)
    console.log('分析方式:', data.analysis_method)

    // 根据分析方式显示不同的提示
    if (data.analysis_method === 'deep_scan') {
      ElMessage.success({
        message: `深度分析完成！数据完整度: ${data.completeness || 0}%`,
        duration: 5000
      })
    } else {
      ElMessage.success('数据分析完成')
    }
  } catch (error: any) {
    console.error('深度分析失败:', error)
    connectionStatus.value = {
      connected: false,
      message: `分析失败: ${error.message}`
    }
    ElMessage.error(`深度分析失败: ${error.message}`)
  } finally {
    deepScanning.value = false
  }
}

const startConversion = async () => {
  if (!canStartConversion.value) return

  cancelRequested.value = false
  converting.value = true
  conversionResult.value = null

  // 计算合成规则
  const SYNTHESIS_MAP: Record<string, { source: string; label: string } | null> = {
    '1min': null,
    '5min': { source: '1min', label: '1分钟' },
    '15min': { source: '5min', label: '5分钟' },
    '30min': { source: '5min', label: '5分钟' },
    '60min': { source: '5min', label: '5分钟' },
    'day': null,
    'weekly': { source: 'day', label: '日线' },
    'monthly': { source: 'day', label: '日线' }
  }

  // 使用所有选中的频率（合并所有分组）
  const allSelectedFrequenciesList = allSelectedFrequencies.value

  // 分析需要直接转换和需要合成的频率
  const frequenciesToConvert = allSelectedFrequenciesList.filter(freq => {
    const synthesis = SYNTHESIS_MAP[freq]
    return synthesis === null || !allSelectedFrequenciesList.includes(synthesis.source)
  })

  const frequenciesToSynthesize = allSelectedFrequenciesList.filter(freq => {
    const synthesis = SYNTHESIS_MAP[freq]
    return synthesis !== null && !allSelectedFrequenciesList.includes(synthesis.source)
  })

  // 初始化进度 - 使用0开始，等待后端返回实际总数
  const startTime = Date.now()
  conversionProgress.value = {
    percent: 0,
    status: undefined,
    processed: 0,
    total: 0
  }

  console.log('转换计划:', {
    选中分组: selectedSecurityTypes.value,
    直接转换: frequenciesToConvert,
    自动合成: frequenciesToSynthesize
  })

  // 创建新的 AbortController
  abortController = new AbortController()
  cancelRequested.value = false

  try {
    // 准备请求参数
    const requestBody: any = {
      frequencies: frequenciesToConvert,
      forward_fill: advancedOptions.value.forwardFill,
      handle_outliers: advancedOptions.value.handleOutliers,
      normalize: advancedOptions.value.normalize,
      limit: null  // 不限制股票数量，转换所有股票
    }

    // 只有当选择了证券类型时才传递该字段
    if (selectedSecurityTypes.value.length > 0) {
      requestBody.security_types = selectedSecurityTypes.value
    }

    console.log('发送SSE转换请求到后端:', requestBody)

    // 使用SSE流式接口获取实时进度
    const response = await fetch(buildApiUrl(API_PATHS.TDX_CONVERT_STREAM), {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(requestBody),
      signal: abortController.signal
    })

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`)
    }

    // 读取流式响应
    const reader = response.body?.getReader()
    if (!reader) {
      throw new Error('无法获取响应流')
    }

    const decoder = new TextDecoder()
    let buffer = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      // 解码数据块
      buffer += decoder.decode(value, { stream: true })

      // 处理每个SSE消息（格式: "data: {...}\n\n"）
      const lines = buffer.split('\n')
      buffer = lines.pop() || ''  // 保留最后一个不完整的行

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const data = JSON.parse(line.substring(6))
            console.log('收到进度更新:', data)

            // 处理不同类型的事件
            if (data.type === 'start') {
              // 转换开始，设置总数
              conversionProgress.value!.total = data.total
              conversionProgress.value!.currentFrequency = Array.isArray(data.frequencies) ? data.frequencies.join(", ") : "" || ''
            } else if (data.type === 'progress') {
              // 进度更新
              const percent = Math.floor((data.current / data.total) * 100)
              conversionProgress.value!.percent = percent
              conversionProgress.value!.processed = data.current
              conversionProgress.value!.total = data.total
              conversionProgress.value!.currentStock = data.symbol
            } else if (data.type === 'saving') {
              // 开始保存
              savingProgress.value = { percent: 0, current: 0, total: 0, symbol: '', frequency: '' }
            } else if (data.type === 'saving_progress') {
              // 保存进度更新
              if (savingProgress.value) {
                savingProgress.value.percent = data.percent
                savingProgress.value.current = data.current
                savingProgress.value.total = data.total
                savingProgress.value.symbol = data.symbol
                savingProgress.value.frequency = data.frequency
              }
            } else if (data.type === 'saving_complete') {
              // 保存完成
              savingProgress.value = null
            } else if (data.type === 'complete') {
              // 转换完成
              conversionProgress.value!.status = 'success'
              conversionProgress.value!.percent = 100
              conversionProgress.value!.processed = conversionProgress.value!.total

              // 计算总耗时
              const elapsedMs = Date.now() - startTime
              const totalTime = formatElapsedTime(elapsedMs)
              conversionProgress.value!.elapsedTime = totalTime

              // 构建结果消息（显示详细的转换信息）
              let message = `✅ 成功将 ${data.success} 只证券的数据转换为QLib格式\n`

              // 添加保存统计
              if (data.total_saved !== undefined) {
                message += `💾 已保存 ${data.total_saved} 个频率的数据\n`
              }

              // 显示错误统计
              if (data.errors > 0) {
                message += `⚠️ ${data.errors} 个保存任务失败\n`
              }

              // 显示频率统计
              if (data.frequency_stats && Object.keys(data.frequency_stats).length > 0) {
                message += `\n📊 转换详情:\n`
                for (const [freq, stats] of Object.entries(data.frequency_stats)) {
                  const freqLabel = freq === 'day' ? '日线' :
                                   freq === '5min' ? '5分钟' :
                                   freq === '15min' ? '15分钟' :
                                   freq === '30min' ? '30分钟' :
                                   freq === '60min' ? '60分钟' : freq
                  message += `  • ${freqLabel}: ${stats.stocks} 只股票 / ${stats.count.toLocaleString()} 条数据\n`
                }
              }

              conversionResult.value = {
                success: true,
                title: '转换完成',
                message: message,
                successCount: data.success || 0,
                failedCount: data.failed || 0,
                totalTime: totalTime,
                data: data
              }

              ElMessage.success({
                message: '数据转换完成！',
                duration: 3000
              })
            } else if (data.type === 'error') {
              // 转换出错
              throw new Error(data.message || '转换失败')
            }
          } catch (parseError) {
            console.error('解析SSE消息失败:', parseError)
          }
        }
      }
    }

  } catch (error: any) {
    console.error('转换失败:', error)

    conversionProgress.value!.status = 'exception'
    conversionResult.value = {
      success: false,
      title: '转换失败',
      message: error.message || '数据转换过程中发生错误',
      successCount: 0,
      failedCount: 0,
      totalTime: '-'
    }
    ElMessage.error(`数据转换失败: ${error.message}`)
  } finally {
    converting.value = false
    cancelRequested.value = false
  }
}

const cancelConversion = () => {
  if (abortController) {
    abortController.abort()
    abortController = null
    ElMessage.warning('已取消转换')
    converting.value = false
    conversionProgress.value = null
    savingProgress.value = null
  }
}

const resetConversion = () => {
  conversionResult.value = null
  conversionProgress.value = null
  savingProgress.value = null
}

const getFrequencyLabel = (freq: string) => {
  const labels: Record<string, string> = {
    'day': '日线',
    '1min': '1分钟',
    '5min': '5分钟',
    '15min': '15分钟',
    '30min': '30分钟',
    '60min': '60分钟'
  }
  return labels[freq] || freq
}

const getDisabledReason = () => {
  if (tdxInfo.value === null) {
    return '请先检测通达信数据连接'
  }
  const hasSelectedFrequencies = Object.values(groupedSelectedFrequencies.value).some(
    freqs => freqs.length > 0
  )
  if (!hasSelectedFrequencies) {
    return '请至少为一种证券类型选择数据频率'
  }
  return ''
}
</script>

<style scoped>
.saving-progress {
  padding: 16px;
  background: rgba(103, 194, 58, 0.1);
  border: 1px solid rgba(103, 194, 58, 0.3);
  border-radius: 8px;
  margin-bottom: 16px;
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% {
    box-shadow: 0 0 0 0 rgba(103, 194, 58, 0.4);
  }
  50% {
    box-shadow: 0 0 0 8px rgba(103, 194, 58, 0);
  }
}

.data-source-manager {
  padding: 20px;
  background: rgba(26, 26, 46, 0.95);
  border-radius: 8px;
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
  color: #ffffff;
}

.header-actions {
  display: flex;
  gap: 8px;
}

.config-section {
  margin-bottom: 20px;
}

.conversion-settings {
  margin-bottom: 20px;
}

.conversion-action {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 12px 0;
  margin-bottom: 20px;
}

.convert-button {
  width: 100%;
  height: 50px;
  font-size: 16px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.cancel-button {
  width: 100%;
  height: 50px;
  font-size: 16px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  background: rgba(239, 68, 68, 0.1);
  border-color: rgba(239, 68, 68, 0.3);
  color: rgba(239, 68, 68, 0.9);
  border-radius: 20px;
}

.cancel-button:hover {
  background: rgba(239, 68, 68, 0.2);
  border-color: rgba(239, 68, 68, 0.5);
  color: #ef4444;
}

.button-tip {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
}

.conversion-result {
  margin-top: 20px;
}

.result-stats {
  display: flex;
  gap: 24px;
  margin-bottom: 16px;
}

.stat-item {
  display: flex;
  gap: 8px;
}

.stat-item .stat-label {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.6);
}

.stat-item .stat-value {
  font-size: 16px;
  font-weight: 600;
}

.stat-item .stat-value.success {
  color: #10b981;
}

.stat-item .stat-value.error {
  color: #ef4444;
}

:deep(.el-collapse) {
  background: transparent;
  border: none;
}

:deep(.el-collapse-item__header) {
  background: rgba(255, 255, 255, 0.05);
  color: rgba(255, 255, 255, 0.8);
  border-radius: 4px;
  padding: 0 16px;
  height: 40px;
  border: none;
}

:deep(.el-collapse-item__wrap) {
  background: transparent;
  border: none;
}

:deep(.el-collapse-item__content) {
  padding: 16px 0 0 0;
}

/* 移除 collapse-item 的底部边框 */
:deep(.el-collapse-item) {
  border: none;
}

/* 统一按钮风格 */
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

:deep(.el-button--warning:active:not(:disabled)) {
  background: linear-gradient(135deg, #d97706 0%, #b45309 100%);
  border-color: transparent;
  color: white;
}

/* 自定义分隔线样式 - 与深色主题协调 */
:deep(.el-divider) {
  border-color: rgba(255, 255, 255, 0.1);
  margin: 20px 0;
}
</style>

<template>
  <div class="stock-detail-advanced">
    <!-- 股票头部信息 -->
    <div class="stock-header">
      <el-row :gutter="20">
        <el-col :span="16">
          <div class="stock-info">
            <h2>{{ stockInfo.symbol }} - {{ stockInfo.name }}</h2>
            <div class="price-info">
              <span class="price" :class="getPriceClass(stockInfo.change_percent)">
                {{ stockInfo.price ? stockInfo.price.toFixed(2) : '--' }}
              </span>
              <span class="change" :class="getPriceClass(stockInfo.change_percent)">
                {{ stockInfo.change_percent ? (stockInfo.change_percent > 0 ? '+' : '') + stockInfo.change_percent.toFixed(2) + '%' : '--' }}
              </span>
              <el-tag v-if="connected" type="success" size="small">实时</el-tag>
            </div>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="actions">
            <el-button-group>
              <el-button @click="refreshData" :loading="loading">
                <el-icon><Refresh /></el-icon> 刷新
              </el-button>
              <el-button @click="toggleSettings">
                <el-icon><Setting /></el-icon> 设置
              </el-button>
            </el-button-group>
          </div>
        </el-col>
      </el-row>
    </div>

    <!-- 高级K线图 -->
    <el-card class="chart-card">
      <TradingViewKLineUnified
        :symbol="formattedSymbol"
        :stock-name="stockInfo.name"
        :period="selectedPeriod"
        height="600px"
        @chart-ready="handleChartReady"
      />
    </el-card>

    <!-- 技术指标详情 -->
    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>指标参数</span>
            <el-button style="float: right" size="small" @click="resetAllParams">
              重置默认
            </el-button>
          </template>

          <el-descriptions :column="2" border size="small">
            <el-descriptions-item label="MA周期">
              {{ indicatorParams.ma.periods.join(', ') }}
            </el-descriptions-item>
            <el-descriptions-item label="BOLL周期">
              {{ indicatorParams.boll.period }}
            </el-descriptions-item>
            <el-descriptions-item label="MACD快线">
              {{ indicatorParams.macd.fastperiod }}
            </el-descriptions-item>
            <el-descriptions-item label="MACD慢线">
              {{ indicatorParams.macd.slowperiod }}
            </el-descriptions-item>
            <el-descriptions-item label="KDJ周期">
              {{ indicatorParams.kdj.fastk_period }}
            </el-descriptions-item>
            <el-descriptions-item label="RSI周期">
              {{ indicatorParams.rsi.period }}
            </el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>

      <el-col :span="12">
        <el-card>
          <template #header>
            <span>快捷操作</span>
          </template>

          <div class="quick-actions">
            <el-button type="primary" @click="switchToDayK">日K</el-button>
            <el-button @click="switchToWeekK">周K</el-button>
            <el-button @click="switchToMonthK">月K</el-button>
            <el-button @click="switchTo5MinK">5分</el-button>
            <el-button @click="switchTo30MinK">30分</el-button>
          </div>

          <el-divider />

          <div class="presets">
            <h4>指标预设</h4>
            <el-space wrap>
              <el-button size="small" @click="applyPreset('conservative')">保守型</el-button>
              <el-button size="small" @click="applyPreset('aggressive')">激进型</el-button>
              <el-button size="small" @click="applyPreset('balanced')">平衡型</el-button>
            </el-space>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 设置对话框 -->
    <el-dialog v-model="showSettings" title="图表设置" width="500px">
      <el-form label-width="120px">
        <el-form-item label="默认周期">
          <el-select v-model="defaultPeriod">
            <el-option label="日K" value="day" />
            <el-option label="周K" value="week" />
            <el-option label="月K" value="month" />
            <el-option label="5分" value="5min" />
            <el-option label="15分" value="15min" />
            <el-option label="30分" value="30min" />
            <el-option label="60分" value="60min" />
          </el-select>
        </el-form-item>

        <el-form-item label="自动刷新">
          <el-switch v-model="autoRefresh" />
        </el-form-item>

        <el-form-item label="刷新间隔">
          <el-input-number v-model="refreshInterval" :min="3" :max="60" />
          <span style="margin-left: 10px">秒</span>
        </el-form-item>

        <el-form-item label="启用动画">
          <el-switch v-model="animationEnabled" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showSettings = false">取消</el-button>
        <el-button type="primary" @click="saveSettings">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { storeToRefs } from 'pinia'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Refresh, Setting } from '@element-plus/icons-vue'
import TradingViewKLineUnified from '@/components/charts/TradingViewKLineUnified.vue'
import { useGlobalWebSocketEnhanced } from '@/composables/useWebSocketEnhanced'
import { useUserStore } from '@/stores'

const route = useRoute()
const symbol = computed(() => route.params.symbol as string || '600519')

// 格式化股票代码 (添加市场后缀)
const formattedSymbol = computed(() => {
  const code = symbol.value
  // 如果已经包含市场后缀,直接返回
  if (code.includes('.')) return code
  // 根据代码规则添加市场后缀
  if (code.startsWith('6')) {
    return `${code}.SH`  // 上海市场
  } else if (code.startsWith('0') || code.startsWith('3')) {
    return `${code}.SZ`  // 深圳市场
  }
  return code
})

// WebSocket
const ws = useGlobalWebSocketEnhanced()
const connected = computed(() => ws.connected.value)

// 数据
const stockInfo = ref({
  symbol: symbol.value,
  name: '贵州茅台',
  price: 1428.01,
  change_percent: 1.25
})

const loading = ref(false)
const selectedPeriod = ref('day')

// 设置
const showSettings = ref(false)
const defaultPeriod = ref('day')
const autoRefresh = ref(true)
const refreshInterval = ref(3)
const animationEnabled = ref(false)

// 指标参数 - 性能优化：使用storeToRefs（M2-16）
// 解构Store时使用storeToRefs保持响应性
const userStore = useUserStore()
const { settings } = storeToRefs(userStore)
const indicatorParams = computed(() => settings.value.indicatorParams)

// 切换周期
const switchToDayK = () => selectedPeriod.value = 'day'
const switchToWeekK = () => selectedPeriod.value = 'week'
const switchToMonthK = () => selectedPeriod.value = 'month'
const switchTo5MinK = () => selectedPeriod.value = '5min'
const switchTo30MinK = () => selectedPeriod.value = '30min'

// 刷新数据
const refreshData = () => {
  loading.value = true
  setTimeout(() => {
    loading.value = false
    ElMessage.success('数据已刷新')
  }, 500)
}

// 切换设置
const toggleSettings = () => {
  showSettings.value = true
}

// 保存设置
const saveSettings = () => {
  showSettings.value = false
  ElMessage.success('设置已保存')
}

// 图表就绪
const handleChartReady = () => {
  console.log('Chart ready')
}

// 指标变化 (保留兼容性)
const handleIndicatorChange = (data: any) => {
  console.log('Indicator changed:', data)
}

// 参数变化 (保留兼容性)
const handleParamChange = (params: any) => {
  console.log('Params changed:', params)
}

// 重置所有参数
const resetAllParams = () => {
  userStore.indicatorParamsManager.reset()
  ElMessage.success('参数已重置')
}

// 应用预设
const applyPreset = (type: string) => {
  switch (type) {
    case 'conservative':
      userStore.indicatorParamsManager.update('ma', { periods: [10, 20, 30, 60] })
      userStore.indicatorParamsManager.update('boll', { period: 20, nbdevup: 2, nbdevdn: 2 })
      break
    case 'aggressive':
      userStore.indicatorParamsManager.update('ma', { periods: [5, 10, 20] })
      userStore.indicatorParamsManager.update('rsi', { period: 6, overbought: 80, oversold: 20 })
      break
    case 'balanced':
      userStore.indicatorParamsManager.reset()
      break
  }
  ElMessage.success(`已应用${type === 'conservative' ? '保守型' : type === 'aggressive' ? '激进型' : '平衡型'}预设`)
}

// 格式化
const getPriceClass = (value: number) => {
  if (!value) return ''
  if (value > 0) return 'text-up'
  if (value < 0) return 'text-down'
  return ''
}

onMounted(() => {
  // 订阅股票行情
  ws.subscribeQuotes([symbol.value])
})

onUnmounted(() => {
  ws.unsubscribeQuotes([symbol.value])
})
</script>

<style scoped lang="scss">
@import '@/styles/variables.scss';

.stock-detail-advanced {
  padding: 20px;

  .stock-header {
    margin-bottom: 20px;
    padding: 20px;
    background: $bg-surface;
    border-radius: $radius-lg;
    border: 1px solid $border-light;

    .stock-info {
      h2 {
        margin: 0 0 10px 0;
        font-size: 24px;
        color: $text-primary;
      }

      .price-info {
        display: flex;
        align-items: center;
        gap: 15px;

        .price {
          font-size: 32px;
          font-weight: bold;
        }

        .change {
          font-size: 20px;
        }
      }
    }
  }

  .chart-card {
    background: $bg-surface;
    border: 1px solid $border-light;
  }

  .quick-actions {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
  }

  .presets {
    h4 {
      margin: 0 0 10px 0;
      font-size: 14px;
      color: $text-primary;
    }
  }

  .text-up {
    color: #ef4444;
  }

  .text-down {
    color: #10b981;
  }
}
</style>

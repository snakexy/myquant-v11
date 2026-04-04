<template>
  <div class="signal-engine-config">
    <el-form label-position="top" size="small">
      <!-- 技术指标 -->
      <div class="section-title">技术指标</div>

      <el-form-item>
        <el-checkbox v-model="localParams.indicators.ma">
          移动平均线 (MA)
        </el-checkbox>
      </el-form-item>

      <el-form-item label="MA周期" v-if="localParams.indicators.ma">
        <el-checkbox-group v-model="localParams.indicators.maPeriods">
          <el-checkbox :value="5">5日</el-checkbox>
          <el-checkbox :value="10">10日</el-checkbox>
          <el-checkbox :value="20">20日</el-checkbox>
          <el-checkbox :value="60">60日</el-checkbox>
        </el-checkbox-group>
      </el-form-item>

      <el-form-item>
        <el-checkbox v-model="localParams.indicators.macd">
          MACD
        </el-checkbox>
      </el-form-item>

      <el-form-item>
        <el-checkbox v-model="localParams.indicators.rsi">
          相对强弱指标 (RSI)
        </el-checkbox>
      </el-form-item>

      <el-form-item label="RSI周期" v-if="localParams.indicators.rsi">
        <el-input-number
          v-model="localParams.indicators.rsiPeriod"
          :min="2"
          :max="100"
          style="width: 100%"
        />
      </el-form-item>

      <el-form-item>
        <el-checkbox v-model="localParams.indicators.bollinger">
          布林带
        </el-checkbox>
      </el-form-item>

      <el-form-item>
        <el-checkbox v-model="localParams.indicators.kdj">
          KDJ
        </el-checkbox>
      </el-form-item>

      <!-- 信号规则 -->
      <div class="section-title">信号规则</div>

      <el-form-item label="买入条件">
        <el-select v-model="localParams.signalRules.buyCondition" style="width: 100%">
          <el-option label="金叉" value="golden_cross" />
          <el-option label="RSI超卖" value="rsi_oversold" />
          <el-option label="突破阻力" value="breakout_resistance" />
          <el-option label="MACD正背离" value="macd_bullish_divergence" />
        </el-select>
      </el-form-item>

      <el-form-item label="卖出条件">
        <el-select v-model="localParams.signalRules.sellCondition" style="width: 100%">
          <el-option label="死叉" value="death_cross" />
          <el-option label="RSI超买" value="rsi_overbought" />
          <el-option label="跌破支撑" value="breakdown_support" />
          <el-option label="MACD负背离" value="macd_bearish_divergence" />
        </el-select>
      </el-form-item>

      <el-form-item label="信号强度阈值">
        <el-slider
          v-model="localParams.signalRules.strength"
          :min="0"
          :max="1"
          :step="0.1"
          :format-tooltip="(v) => (v * 100).toFixed(0) + '%'"
        />
        <div class="form-tip">只显示强度高于此阈值的信号</div>
      </el-form-item>

      <!-- 模式检测 -->
      <div class="section-title">模式检测</div>

      <el-form-item>
        <el-checkbox v-model="localParams.patternDetection">
          启用模式检测
        </el-checkbox>
        <div class="form-tip">检测价格形态和交易信号</div>
      </el-form-item>

      <el-form-item
        label="检测模式类型"
        v-if="localParams.patternDetection"
      >
        <el-checkbox-group v-model="localParams.patterns">
          <el-checkbox value="trend">趋势模式</el-checkbox>
          <el-checkbox value="reversal">反转模式</el-checkbox>
          <el-checkbox value="momentum">动量模式</el-checkbox>
        </el-checkbox-group>
      </el-form-item>
    </el-form>

    <!-- 检测状态显示 -->
    <div class="detection-status" v-if="detectionData">
      <el-divider />
      <div class="status-header">检测结果</div>
      <div class="status-content">
        <el-tag type="success" size="large">
          检测到 {{ detectionData.length }} 个信号
        </el-tag>
        <div class="signal-list" v-if="detectionData.length > 0">
          <div v-for="(signal, index) in detectionData.slice(0, 5)" :key="index" class="signal-item">
            <span class="signal-type">{{ signal.signal }}</span>
            <el-tag
              :type="signal.direction === 'buy' ? 'success' : signal.direction === 'sell' ? 'danger' : 'info'"
              size="small"
            >
              {{ signal.direction }}
            </el-tag>
            <span class="signal-strength">{{ signal.strength }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'

interface Props {
  params: Record<string, any>
  data?: any
}

interface Emits {
  (e: 'update:params', value: Record<string, any>): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

// 本地参数副本
const localParams = ref<Record<string, any>>({
  indicators: {
    ma: true,
    maPeriods: [5, 10, 20, 60],
    macd: true,
    rsi: true,
    rsiPeriod: 14,
    bollinger: false,
    kdj: false
  },
  signalRules: {
    buyCondition: 'golden_cross',
    sellCondition: 'death_cross',
    strength: 0.7
  },
  patternDetection: true,
  patterns: ['trend', 'reversal', 'momentum'],
  ...props.params
})

// 检测数据
const detectionData = computed(() => {
  const content = props.data?.content
  if (Array.isArray(content) && content.length > 0 && typeof content[0] === 'object' && 'signal' in content[0]) {
    return content
  }
  return null
})

// 监听参数变化
watch(localParams, (newParams) => {
  emit('update:params', { ...newParams })
}, { deep: true })
</script>

<style scoped>
.signal-engine-config {
  padding: 8px;
  max-height: 500px;
  overflow-y: auto;
}

.section-title {
  font-size: 13px;
  font-weight: 600;
  color: #374151;
  margin: 12px 0 8px 0;
  padding-bottom: 4px;
  border-bottom: 1px solid #e5e7eb;
}

.form-tip {
  font-size: 12px;
  color: #9ca3af;
  margin-top: 4px;
  line-height: 1.4;
}

.detection-status {
  margin-top: 16px;
}

.status-header {
  font-size: 13px;
  font-weight: 600;
  color: #374151;
  margin-bottom: 8px;
}

.status-content {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.signal-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.signal-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  padding: 4px 8px;
  background: #f9fafb;
  border-radius: 4px;
}

.signal-type {
  flex: 1;
  color: #374151;
}

.signal-strength {
  color: #6b7280;
  font-size: 11px;
}
</style>

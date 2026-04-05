/**
 * IndicatorPanel - 技术指标统一面板
 *
 * 提供独立分窗的技术指标显示：
 * - 支持多个副图指标（MACD、KDJ、RSI、CCI、OBV）
 * - 每个指标独立显示，可调整高度
 * - 支持主图叠加指标（MA、BOLL）
 * - 支持添加/删除指标
 * - 指标参数配置
 */

<template>
  <div class="indicator-panel">
    <!-- 主图区域（由父组件管理） -->
    <slot name="main-chart">
      <!-- 主图指标叠加（MA、BOLL等）将通过 LightweightCharts API 直接添加到主图 -->
    </slot>

    <!-- 副图指标区域 -->
    <div class="sub-indicators-container">
      <IndicatorPane
        v-for="indicator in visibleSubIndicators"
        :key="indicator.id"
        :id="indicator.id"
        :title="indicator.name"
        :height="indicator.height"
        :resizable="true"
        @resize="handleIndicatorResize(indicator.id, $event)"
        @close="removeSubIndicator(indicator.id)"
      >
        <!-- MACD 指标 -->
        <MACDIndicator
          v-if="indicator.id === 'MACD'"
          :data="indicatorData[indicator.id]"
          :width="containerWidth"
          :height="indicator.height"
        />

        <!-- KDJ 指标 -->
        <KDJIndicator
          v-else-if="indicator.id === 'KDJ'"
          :data="indicatorData[indicator.id]"
          :width="containerWidth"
          :height="indicator.height"
        />

        <!-- RSI 指标 -->
        <RSIIndicator
          v-else-if="indicator.id === 'RSI'"
          :data="indicatorData[indicator.id]"
          :width="containerWidth"
          :height="indicator.height"
        />

        <!-- CCI 指标 -->
        <CCIIndicator
          v-else-if="indicator.id === 'CCI'"
          :data="indicatorData[indicator.id]"
          :width="containerWidth"
          :height="indicator.height"
        />

        <!-- OBV 指标 -->
        <OBVIndicator
          v-else-if="indicator.id === 'OBV'"
          :data="indicatorData[indicator.id]"
          :width="containerWidth"
          :height="indicator.height"
        />
      </IndicatorPane>
    </div>

    <!-- 指标配置面板 -->
    <IndicatorConfigPanel
      v-if="configPanelVisible"
      :available-indicators="availableIndicators"
      :active-main-indicators="mainIndicators"
      :active-sub-indicators="subIndicators"
      @add-main="addMainIndicator"
      @add-sub="addSubIndicator"
      @remove-main="removeMainIndicator"
      @remove-sub="removeSubIndicator"
      @update-params="updateIndicatorParams"
      @close="configPanelVisible = false"
    />

    <!-- 快捷按钮 -->
    <div class="indicator-toolbar">
      <button
        class="toolbar-btn"
        @click="configPanelVisible = true"
        title="指标配置"
      >
        <span>📊</span>
      </button>
      <button
        class="toolbar-btn"
        @click="resetLayout"
        title="重置布局"
      >
        <span>🔄</span>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { useIndicatorWindows } from '@/composables/useIndicatorWindows'
import IndicatorPane from '@/components/charts/IndicatorPane.vue'
import IndicatorConfigPanel from './IndicatorConfigPanel.vue'
import MACDIndicator from './indicators/MACDIndicator.vue'
import KDJIndicator from './indicators/KDJIndicator.vue'
import RSIIndicator from './indicators/RSIIndicator.vue'
import CCIIndicator from './indicators/CCIIndicator.vue'
import OBVIndicator from './indicators/OBVIndicator.vue'

interface Props {
  symbol?: string
  period?: string
  containerWidth?: number
}

const props = withDefaults(defineProps<Props>(), {
  containerWidth: 800
})

// Emits
const emit = defineEmits<{
  'indicator-added': [indicator: string, type: 'main' | 'sub']
  'indicator-removed': [indicator: string, type: 'main' | 'sub']
}>()

// 使用指标窗口管理
const {
  mainIndicators,
  subIndicators,
  availableIndicators,
  addMainIndicator,
  removeMainIndicator,
  hasMainIndicator,
  addSubIndicator,
  removeSubIndicator,
  toggleSubIndicator,
  updateSubIndicatorHeight,
  resetLayout
} = useIndicatorWindows({
  symbol: props.symbol,
  period: props.period
})

// UI 状态
const configPanelVisible = ref(false)

// 指标数据
const indicatorData = ref<Record<string, any>>({})

// 可见的副图指标
const visibleSubIndicators = computed(() => {
  return subIndicators.value.filter(ind => ind.visible)
})

/**
 * 处理指标窗口大小调整
 */
const handleIndicatorResize = (indicatorId: string, newHeight: number) => {
  updateSubIndicatorHeight(indicatorId, newHeight)
}

/**
 * 添加主图指标
 */
const handleAddMainIndicator = (indicator: string, params?: any) => {
  addMainIndicator(indicator, params)
  emit('indicator-added', indicator, 'main')
  // 重新获取数据
  refreshIndicatorData()
}

/**
 * 添加副图指标
 */
const handleAddSubIndicator = (indicator: string, params?: any) => {
  addSubIndicator(indicator, params)
  emit('indicator-added', indicator, 'sub')
  // 重新获取数据
  refreshIndicatorData()
}

/**
 * 移除主图指标
 */
const handleRemoveMainIndicator = (indicator: string) => {
  removeMainIndicator(indicator)
  emit('indicator-removed', indicator, 'main')
  // 重新获取数据
  refreshIndicatorData()
}

/**
 * 移除副图指标
 */
const handleRemoveSubIndicator = (indicator: string) => {
  removeSubIndicator(indicator)
  emit('indicator-removed', indicator, 'sub')
}

/**
 * 更新指标参数
 */
const updateIndicatorParams = (indicator: string, params: any) => {
  // 更新参数并刷新数据
  refreshIndicatorData()
}

/**
 * 刷新指标数据
 */
const refreshIndicatorData = async () => {
  // 获取所有激活的指标
  const activeSubIndicators = subIndicators.value
    .filter(ind => ind.visible)
    .map(ind => ind.id)

  // 调用后端 API 获取指标数据
  // 实际实现需要在父组件中调用
  console.log('[IndicatorPanel] 刷新指标数据:', activeSubIndicators)
}

/**
 * 设置指标数据
 */
const setIndicatorData = (data: Record<string, any>) => {
  indicatorData.value = data
}

/**
 * 暴露方法给父组件
 */
defineExpose({
  setIndicatorData,
  refreshIndicatorData,
  mainIndicators,
  subIndicators
})
</script>

<style scoped lang="scss">
.indicator-panel {
  display: flex;
  flex-direction: column;
  width: 100%;
  height: 100%;
}

.sub-indicators-container {
  display: flex;
  flex-direction: column;
  flex: 1;
  overflow: hidden;
}

.indicator-toolbar {
  position: absolute;
  top: 8px;
  right: 8px;
  display: flex;
  gap: 8px;
  z-index: 100;
}

.toolbar-btn {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #1E222D;
  border: 1px solid #2A2E39;
  border-radius: 4px;
  color: #B2B5BE;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;

  &:hover {
    background: #2A2E39;
    color: #D1D5DB;
  }

  &:active {
    transform: scale(0.95);
  }
}
</style>

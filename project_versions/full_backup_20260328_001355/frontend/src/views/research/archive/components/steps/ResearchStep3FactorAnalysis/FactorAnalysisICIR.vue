<template>
  <div class="factor-analysis-icir">
    <!-- IC/IR Trend Chart Component -->
    <ICIRTrendChart
      :task-id="taskId"
      :target-period="icConfig.targetPeriod"
      :method="icConfig.method"
      :is-zh="isZh"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, PropType } from 'vue'
import ICIRTrendChart from '../../ICIRTrendChart.vue'
import { useAppStore } from '@/stores/core/AppStore'

interface Props {
  taskId: string
  isZh: boolean
}

const props = defineProps<Props>()

const appStore = useAppStore()
const isZh = computed(() => props.isZh || appStore.language === 'zh')

// IC/IR配置
const icConfig = reactive({
  method: 'spearman' as 'pearson' | 'spearman',
  threshold: 0.03,
  targetPeriod: 1,
  includeAlpha158: true,
  includeAlpha360: false,
  includeCustom: true
})
</script>

<style scoped lang="scss">
.factor-analysis-icir {
  /* CSS 变量定义 - 继承自父组件 */
  --bg-primary: #131722;
  --bg-secondary: #1e222d;
  --bg-tertiary: #2a2e39;
  --text-primary: #d1d4dc;
  --text-secondary: #787b86;
  --accent-blue: #2962ff;
  --color-up: #ef5350;
  --color-down: #26a69a;
  --accent-red: #ef5350;
  --accent-green: #26a69a;
  --accent-orange: #ff9800;
  --border-color: #2a2e39;

  width: 100%;
}
</style>

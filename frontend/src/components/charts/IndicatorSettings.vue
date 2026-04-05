<template>
  <n-modal
    :show="visible"
    preset="card"
    :title="config?.name + ' 参数设置'"
    style="width: 400px"
    :mask-closable="false"
    @close="handleCancel"
    @update:show="handleUpdateShow"
  >
    <n-form
      ref="formRef"
      :model="formValue"
      label-placement="left"
      label-width="100"
    >
      <n-form-item
        v-for="(value, key) in formValue"
        :key="key"
        :label="getParamLabel(key)"
      >
        <n-input-number
          v-if="typeof value === 'number'"
          v-model:value="formValue[key]"
          :min="1"
          :max="200"
          style="width: 100%"
        />
        <n-input
          v-else
          :value="JSON.stringify(value)"
          disabled
        />
      </n-form-item>
    </n-form>

    <template #footer>
      <n-space justify="end">
        <n-button @click="handleCancel">取消</n-button>
        <n-button type="primary" @click="handleConfirm">应用</n-button>
      </n-space>
    </template>
  </n-modal>
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import {
  NModal,
  NCard,
  NForm,
  NFormItem,
  NInputNumber,
  NInput,
  NButton,
  NSpace
} from 'naive-ui'
import { getIndicatorConfig } from './indicator-registry'

interface Props {
  visible: boolean
  indicatorId: string
  currentParams: Record<string, number | number[]>
}

const props = defineProps<Props>()
const emit = defineEmits<{
  'update:visible': [value: boolean]
  confirm: [params: Record<string, number | number[]>]
  cancel: []
}>()

const formRef = ref()
const formValue = ref<Record<string, any>>({})

// 获取指标配置
const config = computed(() => getIndicatorConfig(props.indicatorId))

// 参数标签映射
const paramLabels: Record<string, string> = {
  fast: '快线周期',
  slow: '慢线周期',
  signal: '信号周期',
  kPeriod: 'K周期',
  dPeriod: 'D周期',
  jPeriod: 'J周期',
  period: '周期',
  stdDev: '标准差',
  periods: '均线周期'
}

function getParamLabel(key: string): string {
  return paramLabels[key] || key
}

// 监听打开时初始化表单
watch(() => props.visible, (newVal) => {
  if (newVal && props.currentParams) {
    formValue.value = { ...props.currentParams }
  }
})

function handleUpdateShow(val: boolean) {
  emit('update:visible', val)
}

function handleCancel() {
  emit('cancel')
  emit('update:visible', false)
}

function handleConfirm() {
  emit('confirm', { ...formValue.value })
  emit('update:visible', false)
}
</script>

<style scoped>
:deep(.n-card-header) {
  padding-bottom: 12px;
  border-bottom: 1px solid var(--border-color);
}
</style>

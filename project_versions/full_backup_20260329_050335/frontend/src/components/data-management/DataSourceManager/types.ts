/**
 * DataSourceManager 组件 - 类型定义
 */

import type { FrequencyType, TDXInfo, ConnectionStatus, ConversionProgress, ConversionResult, ConversionOptions } from '../shared/types'

export interface DataSourceManagerProps {
  modelValue?: string
}

export interface DataSourceManagerEmits {
  (e: 'update:modelValue', value: string): void
  (e: 'conversion-complete', result: ConversionResult): void
}

export interface FrequencyOption {
  value: FrequencyType
  label: string
  icon: string
  description: string
}

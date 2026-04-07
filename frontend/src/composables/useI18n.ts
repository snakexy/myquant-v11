/**
 * 国际化 Composable
 */

import { computed } from 'vue'
import { useAppStore } from '@/stores'
import { translations } from '@/locales'

/**
 * 获取翻译文本
 * @param key 翻译键，支持点号分隔的路径，如 'indicators.title'
 * @returns 翻译后的文本
 */
export function useI18n() {
  const appStore = useAppStore()

  const t = (key: string): string => {
    const lang = appStore.language
    const keys = key.split('.')
    let value: any = translations[lang]

    for (const k of keys) {
      if (value && typeof value === 'object' && k in value) {
        value = value[k]
      } else {
        // 如果翻译不存在，返回键名
        console.warn(`[i18n] Translation not found: ${key}`)
        return key
      }
    }

    return typeof value === 'string' ? value : key
  }

  const currentLanguage = computed(() => appStore.language)

  return {
    t,
    currentLanguage
  }
}

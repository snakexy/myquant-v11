/**
 * 国际化 Composable
 */

import { computed } from 'vue'
import { useAppStore } from '@/stores/core/AppStore'
import { translations } from '@/locales/index'

/**
 * 获取翻译文本
 * @param key 翻译键，支持点号分隔的路径，如 'indicators.title'
 * @returns 翻译后的文本
 */
export function useI18n() {
  const t = (key: string): string => {
    try {
      const appStore = useAppStore()
      const lang = appStore.language
      const keys = key.split('.')
      let value: any = translations[lang as keyof typeof translations]

      for (const k of keys) {
        if (value && typeof value === 'object' && k in value) {
          value = value[k]
        } else {
          // 如果翻译不存在，返回键名
          return key
        }
      }

      return typeof value === 'string' ? value : key
    } catch (e) {
      console.error('[i18n] Error:', e)
      return key
    }
  }

  const currentLanguage = computed(() => {
    try {
      const appStore = useAppStore()
      return appStore.language
    } catch {
      return 'zh'
    }
  })

  return {
    t,
    currentLanguage
  }
}

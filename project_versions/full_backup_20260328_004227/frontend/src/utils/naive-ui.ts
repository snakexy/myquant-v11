import { createDiscreteApi } from 'naive-ui'
import type { GlobalThemeOverrides } from 'naive-ui'

// 创建暗黑科技主题
export const createNaiveUI = () => {
  const themeOverrides: GlobalThemeOverrides = {
    common: {
      primaryColor: '#2563eb',
      primaryColorHover: '#4096ff',
      primaryColorPressed: '#1d4ed8',
      primaryColorSuppl: '#4096ff',
      infoColor: '#3b82f6',
      infoColorHover: '#57abff',
      infoColorPressed: '#2b5cb8',
      infoColorSuppl: '#57abff',
      successColor: '#10b981',
      successColorHover: '#34d058',
      successColorPressed: '#059669',
      successColorSuppl: '#34d058',
      warningColor: '#f59e0b',
      warningColorHover: '#f7b955',
      warningColorPressed: '#d48806',
      warningColorSuppl: '#f7b955',
      errorColor: '#ef4444',
      errorColorHover: '#f56565',
      errorColorPressed: '#dc2626',
      errorColorSuppl: '#f56565',
      textColorBase: '#ffffff',
      textColor1: '#ffffff',
      textColor2: '#e6e6e6',
      textColor3: '#b8b8b8',
      textColorDisabled: '#64748b',
      placeholderColor: '#64748b',
      placeholderColorDisabled: '#4a4a4a',
      iconColor: '#ffffff',
      iconColorDisabled: '#64748b',
      iconColorHover: '#ffffff',
      iconColorPressed: '#ffffff',
      borderColor: '#334155',
      dividerColor: '#334155',
      tableHeaderColor: '#1a1a2e',
      tableHeaderTextColor: '#ffffff',
      tableColorStriped: '#181820',
      tableColorHover: '#252530',
      tableTextColor: '#ffffff',
      tableTextColorDisabled: '#64748b',
      loaderColor: '#2563eb',
      loadingColor: '#2563eb',
      scrollbarColor: '#334155',
      scrollbarColorHover: '#4096ff',
      scrollbarColorPressed: '#1d4ed8',
      scrollbarColorDisabled: '#1a1a2e',
      progressRailColor: '#1a1a2e',
      progressRailColorHover: '#252530',
      progressRailColorPressed: '#181820',
      progressColor: '#2563eb',
      progressColorHover: '#4096ff',
      progressColorPressed: '#1d4ed8',
      radioButtonColor: '#2563eb',
      radioButtonColorHover: '#4096ff',
      radioButtonColorPressed: '#1d4ed8',
      radioButtonColorDisabled: '#1a1a2e',
      radioButtonColorActive: '#2563eb',
      switchColor: '#1a1a2e',
      switchColorHover: '#252530',
      switchColorPressed: '#181820',
      switchColorDisabled: '#1a1a2e',
      switchColorActive: '#2563eb',
      tagColor: '#2563eb',
      tagColorHover: '#4096ff',
      tagColorPressed: '#1d4ed8',
      tagColorDisabled: '#1a1a2e',
      tagColorTextActive: '#ffffff',
      tagColorTextHover: '#ffffff',
      tagColorTextPressed: '#ffffff',
      tagColorTextDisabled: '#64748b',
      avatarColor: '#1a1a2e',
      avatarColorHover: '#252530',
      avatarColorPressed: '#181820',
      avatarColorDisabled: '#1a1a2e',
      avatarColorTextActive: '#ffffff',
      avatarColorTextHover: '#ffffff',
      avatarColorTextPressed: '#ffffff',
      avatarColorTextDisabled: '#64748b',
      inputColor: '#1a1a2e',
      inputColorHover: '#252530',
      inputColorPressed: '#181820',
      inputColorDisabled: '#1a1a2e',
      inputColorFocus: '#2563eb',
      inputTextColor: '#ffffff',
      inputTextColorDisabled: '#64748b',
      inputPlaceholderColor: '#64748b',
      inputPlaceholderColorDisabled: '#4a4a4a',
      inputIconColor: '#64748b',
      inputIconColorHover: '#ffffff',
      inputIconColorPressed: '#ffffff',
      inputIconColorDisabled: '#4a4a4a',
      inputBorder: '#334155',
      inputBorderHover: '#4096ff',
      inputBorderPressed: '#1d4ed8',
      inputBorderDisabled: '#1a1a2e',
      inputBorderFocus: '#2563eb',
      inputBoxShadow: 'none',
      inputBoxShadowHover: '0 0 0 2px rgba(64, 158, 255, 0.2)',
      inputBoxShadowPressed: '0 0 0 2px rgba(64, 158, 255, 0.3)',
      inputBoxShadowFocus: '0 0 0 2px rgba(64, 158, 255, 0.4)',
      buttonColor: '#2563eb',
      buttonColorHover: '#4096ff',
      buttonColorPressed: '#1d4ed8',
      buttonColorDisabled: '#1a1a2e',
      buttonColorActive: '#2563eb',
      buttonTextColor: '#ffffff',
      buttonTextColorHover: '#ffffff',
      buttonTextColorPressed: '#ffffff',
      buttonTextColorDisabled: '#64748b',
      buttonTextColorActive: '#ffffff',
      buttonBorder: '1px solid #334155',
      buttonBorderHover: '1px solid #4096ff',
      buttonBorderPressed: '1px solid #1d4ed8',
      buttonBorderDisabled: '1px solid #1a1a2e',
      buttonBorderActive: '1px solid #2563eb',
      boxShadow1: 'none',
      boxShadow2: '0 2px 8px rgba(0, 0, 0, 0.12)',
      boxShadow3: '0 4px 16px rgba(0, 0, 0, 0.16)',
      popoverColor: '#1a1a2e',
      popoverTextColor: '#ffffff'
    },
    dark: {
      bodyColor: '#0a0a0f',
      invertedColor: '#ffffff'
    },
    light: {
      bodyColor: '#ffffff',
      invertedColor: '#000000'
    }
  }

  return createDiscreteApi({
    themeOverrides,
    componentOptions: {
      // 自定义组件配置
      Button: {
        border: true,
        round: true
      },
      Card: {
        bordered: false,
        round: true
      },
      DataTable: {
        striped: true
      },
      Modal: {
        round: true
      }
    }
  })
}

export default createNaiveUI
/**
 * Naive UI 自定义主题配置
 * 使用 Naive UI 的主题覆盖系统，而不是 CSS 强制覆盖
 */
import { darkTheme } from 'naive-ui'
import type { GlobalTheme } from 'naive-ui'

// 自定义暗色主题 - 基于紫色系
export const customDarkTheme: GlobalTheme = {
  name: 'custom-dark',
  common: {
    primaryColor: '#8b5cf6',
    primaryColorHover: '#a78bfa',
    primaryColorPressed: '#7c3aed',
    primaryColorSuppl: '#a78bfa',
  },
  Button: {
    textColor: '#e2e8f0',
    textColorHover: '#ffffff',
    textColorPressed: '#ffffff',
    textColorFocus: '#ffffff',
    color: 'rgba(139, 92, 246, 0.1)',
    colorHover: 'rgba(139, 92, 246, 0.2)',
    colorPressed: 'rgba(139, 92, 246, 0.25)',
    colorFocus: 'rgba(139, 92, 246, 0.15)',
    colorDisabled: 'rgba(139, 92, 246, 0.05)',
    borderColor: 'rgba(139, 92, 246, 0.2)',
    borderColorHover: 'rgba(139, 92, 246, 0.4)',
    borderColorPressed: 'rgba(139, 92, 246, 0.5)',
    borderColorFocus: 'rgba(139, 92, 246, 0.3)',
    borderColorDisabled: 'rgba(139, 92, 246, 0.15)',
  },
  Input: {
    color: 'rgba(139, 92, 246, 0.08)',
    colorFocus: 'rgba(139, 92, 246, 0.15)',
    textColor: '#e2e8f0',
    caretColor: '#8b5cf6',
    border: '1px solid rgba(139, 92, 246, 0.2)',
    borderHover: '1px solid rgba(139, 92, 246, 0.3)',
    borderFocus: '1px solid #8b5cf6',
    placeholderColor: '#94a3b8',
  },
  Select: {
    peers: {
      InternalSelection: {
        color: 'rgba(139, 92, 246, 0.08)',
        colorActive: 'rgba(139, 92, 246, 0.15)',
        textColor: '#e2e8f0',
        caretColor: '#8b5cf6',
        border: '1px solid rgba(139, 92, 246, 0.2)',
        borderHover: '1px solid rgba(139, 92, 246, 0.3)',
        borderActive: '1px solid rgba(139, 92, 246, 0.3)',
        borderFocus: '1px solid #8b5cf6',
        placeholderColor: '#94a3b8',
      }
    }
  },
  InternalSelectMenu: {
    color: 'rgba(139, 92, 246, 0.08)',
    colorScroll: 'rgba(139, 92, 246, 0.05)',
  },
  Card: {
    color: 'rgba(139, 92, 246, 0.02)',
    borderColor: 'rgba(139, 92, 246, 0.15)',
  },
  Modal: {
    color: 'rgba(26, 26, 46, 0.95)',
    textColor: '#f8fafc',
  },
  Dropdown: {
    color: 'rgba(139, 92, 246, 0.08)',
    optionColorHover: 'rgba(139, 92, 246, 0.15)',
    optionTextColor: '#e2e8f0',
    optionTextColorActive: '#a78bfa',
  },
  Tabs: {
    tabTextColorBar: '#ffffff',
    tabTextColorActiveBar: '#a78bfa',
    tabColorBar: 'transparent',
    barColor: 'transparent',
  },
  Switch: {
    railColor: 'rgba(139, 92, 246, 0.2)',
    railColorActive: '#8b5cf6',
    buttonColor: '#ffffff',
  },
  Checkbox: {
    borderColor: 'rgba(139, 92, 246, 0.3)',
    checkMarkColor: '#8b5cf6',
  },
  Radio: {
    buttonBorderColor: 'rgba(139, 92, 246, 0.3)',
    buttonBorderColorActive: 'rgba(139, 92, 246, 0.5)',
    buttonColorActive: 'rgba(139, 92, 246, 0.25)',
    textColor: '#e2e8f0',
  },
}

export default customDarkTheme

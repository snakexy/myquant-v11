import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import Button from '../Button.vue'

describe('Button组件测试', () => {
  it('应该正确渲染默认按钮', () => {
    const wrapper = mount(Button, {
      slots: {
        default: '测试按钮'
      }
    })
    
    expect(wrapper.text()).toBe('测试按钮')
    expect(wrapper.find('button').exists()).toBe(true)
  })

  it('应该支持不同尺寸', () => {
    const wrapper = mount(Button, {
      props: {
        size: 'large'
      },
      slots: {
        default: '大按钮'
      }
    })
    
    expect(wrapper.find('button').classes()).toContain('btn-large')
  })

  it('应该支持不同类型', () => {
    const wrapper = mount(Button, {
      props: {
        type: 'primary'
      },
      slots: {
        default: '主要按钮'
      }
    })
    
    expect(wrapper.find('button').classes()).toContain('btn-primary')
  })

  it('应该支持禁用状态', () => {
    const wrapper = mount(Button, {
      props: {
        disabled: true
      },
      slots: {
        default: '禁用按钮'
      }
    })
    
    const button = wrapper.find('button')
    expect(button.attributes('disabled')).toBeDefined()
    expect(button.classes()).toContain('btn-disabled')
  })

  it('应该支持加载状态', () => {
    const wrapper = mount(Button, {
      props: {
        loading: true
      },
      slots: {
        default: '加载中'
      }
    })
    
    expect(wrapper.find('.loading-icon').exists()).toBe(true)
    expect(wrapper.find('button').classes()).toContain('btn-loading')
  })

  it('应该正确处理点击事件', async () => {
    const wrapper = mount(Button, {
      slots: {
        default: '点击按钮'
      }
    })
    
    await wrapper.find('button').trigger('click')
    
    expect(wrapper.emitted()).toHaveProperty('click')
  })

  it('应该在禁用时不触发点击事件', async () => {
    const wrapper = mount(Button, {
      props: {
        disabled: true
      },
      slots: {
        default: '禁用按钮'
      }
    })
    
    await wrapper.find('button').trigger('click')
    
    expect(wrapper.emitted('click')).toBeUndefined()
  })

  it('应该支持自定义类名', () => {
    const wrapper = mount(Button, {
      props: {
        className: 'custom-class'
      },
      slots: {
        default: '自定义按钮'
      }
    })
    
    expect(wrapper.find('button').classes()).toContain('custom-class')
  })

  it('应该支持图标', () => {
    const wrapper = mount(Button, {
      props: {
        icon: 'search'
      },
      slots: {
        default: '搜索'
      }
    })
    
    expect(wrapper.find('.btn-icon').exists()).toBe(true)
  })
})
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import { library } from '@fortawesome/fontawesome-svg-core'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
import { faDatabase, faCalendarAlt, faCheckCircle, faClock, faSearch, faChartLine } from '@fortawesome/free-solid-svg-icons'
import router from './router'
import App from './App.vue'

// 添加FontAwesome图标到库
library.add(faDatabase, faCalendarAlt, faCheckCircle, faClock, faSearch, faChartLine)

// 导入全局样式
import '@/assets/styles/main.scss'

// 注册所有 Element Plus 图标
const app = createApp(App)

// 注册 FontAwesome 图标组件
app.component('font-awesome-icon', FontAwesomeIcon)

// 遍历注册所有图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

const pinia = createPinia()
pinia.use(piniaPluginPersistedstate)

// 使用插件
app.use(pinia)
app.use(router)
app.use(ElementPlus, {
  // 设置全局 z-index
  zIndex: 30000,
})

// 初始化应用状态
const initializeApp = () => {
  // 这里可以添加应用初始化逻辑
  console.log('Quant-UI 应用已启动')

  // 开发环境验证API配置
  if (import.meta.env.DEV) {
    console.log('\n*** 开发模式：正在验证前端API配置 ***')

    // 验证关键配置项
    const requiredEnvVars = ['VITE_API_BASE_URL', 'VITE_WS_BASE_URL']
    const missingVars = requiredEnvVars.filter(varName => !import.meta.env[varName])

    if (missingVars.length > 0) {
      console.warn('⚠️  警告：以下环境变量未配置:', missingVars)
      console.warn('请检查 .env.development 文件')
    } else {
      console.log('✅ API 配置验证通过')
      console.log('   API Base URL:', import.meta.env.VITE_API_BASE_URL)
      console.log('   WebSocket URL:', import.meta.env.VITE_WS_BASE_URL)
    }
  }

  // 动态设置深色主题
  applyDarkTheme()

  // 监听路由变化，确保主题持续生效
  router.afterEach(() => {
    applyDarkTheme()
  })
}

// 应用深色主题的简化版本
const applyDarkTheme = () => {
  // 只设置最基础的颜色，不覆盖组件样式
  document.documentElement.style.setProperty('--el-bg-color', '#0f0f23')
  document.documentElement.style.setProperty('--el-text-color-primary', '#f8fafc')
  document.documentElement.style.setProperty('--el-text-color-regular', '#cbd5e1')
  document.documentElement.style.setProperty('--el-border-color', '#334155')
  document.documentElement.style.setProperty('--el-fill-color-blank', '#1a1a2e')
  document.documentElement.style.setProperty('--el-fill-color', '#252530')
  document.documentElement.style.setProperty('--el-color-primary', '#2563eb')
}

// 挂载应用
app.mount('#app')

// 执行初始化
initializeApp()

console.log('应用启动完成 - 使用 Element Plus 原生样式')

import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

// 页面组件
import Home from '../views/Home.vue'
import UnrealBlueprintTest from '../views/UnrealBlueprintTest.vue'

// 路由配置
const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'Home',
    component: Home,
    meta: {
      title: 'Quant-UI - 智能量化交易平台',
      requiresAuth: false,
      keepAlive: false
    }
  },
  {
    path: '/unreal-test',
    name: 'UnrealBlueprintTest',
    component: UnrealBlueprintTest,
    meta: {
      title: 'Unreal蓝图测试 - Quant-UI',
      requiresAuth: false,
      keepAlive: false
    }
  }
]

// 创建路由实例
const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    }
    return { top: 0, left: 0 }
  }
})

// 全局前置守卫
router.beforeEach(async (to, from, next) => {
  // 设置页面标题
  if (to.meta?.title) {
    document.title = to.meta.title as string
  }
  next()
})

// 导出路由实例
export default router
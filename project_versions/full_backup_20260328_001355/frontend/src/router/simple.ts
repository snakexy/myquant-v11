import { createRouter, createWebHistory } from 'vue-router'

// 简化的路由配置，用于测试
const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('../views/Home.vue')
  },
  {
    path: '/test-simple',
    name: 'TestSimple',
    component: () => import('../views/TestSimple.vue')
  },
  {
    path: '/data-management-simple',
    name: 'DataManagementSimple',
    component: () => import('../views/DataManagementSimple.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
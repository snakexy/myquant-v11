<template>
  <header class="global-navbar">
    <div class="logo">
      <div class="logo-icon">M</div>
      <span>MyQuant</span>
    </div>

    <nav class="nav-tabs">
      <button
        :class="['nav-tab', { active: currentNav === 'dashboard' }]"
        @click="goTo('/')"
      >
        <svg class="icon-nav" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polyline points="3 17 9 11 15 15"></polyline>
          <polyline points="15 5 21 12 21 3"></polyline>
          <line x1="12" y1="3" x2="12" y2="21"></line>
        </svg>
        实时行情
      </button>
      <button
        :class="['nav-tab', { active: currentNav === 'workflow' }]"
        @click="goTo('/workflow')"
      >
        <svg class="icon-nav" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polyline points="9 11 12 14 22 4"></polyline>
          <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"></path>
        </svg>
        工作流
      </button>
      <button
        :class="['nav-tab', { active: currentNav === 'monitor' }]"
        @click="goTo('/monitoring')"
      >
        <svg class="icon-nav" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
          <circle cx="12" cy="12" r="3"></circle>
        </svg>
        监控
      </button>
      <button
        :class="['nav-tab', { active: currentNav === 'risk' }]"
        @click="goTo('/production/risk')"
      >
        <svg class="icon-nav" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
        </svg>
        风险管理
      </button>
      <button
        :class="['nav-tab', { active: currentNav === 'strategy' }]"
        @click="goTo('/strategy')"
      >
        <svg class="icon-nav" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon>
        </svg>
        策略
      </button>
      <button
        :class="['nav-tab', { active: currentNav === 'data' }]"
        @click="goTo('/data')"
      >
        <svg class="icon-nav" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 1 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path>
          <polyline points="3.27 6.96 12 12.01 20.73 6.96"></polyline>
          <line x1="12" y1="22.08" x2="12" y2="12"></line>
        </svg>
        数据管理
      </button>
    </nav>

    <div class="user-menu">
      <button class="icon-btn" @click="toggleLanguage" title="切换语言">
        🇨🇳
      </button>
      <button class="icon-btn" @click="showNotifications" title="通知">
        🔔
      </button>
      <span class="version">v10.0.0</span>
      <div class="user-avatar">U</div>
    </div>
  </header>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()

// 导航状态
const currentNav = ref('')

// 根据当前路由确定激活的导航
const updateCurrentNav = () => {
  const path = route.path
  if (path.startsWith('/dashboard')) {
    currentNav.value = 'dashboard'
  } else if (path.startsWith('/workflow')) {
    currentNav.value = 'workflow'
  } else if (path.startsWith('/monitoring')) {
    currentNav.value = 'monitor'
  } else if (path.startsWith('/production/risk')) {
    currentNav.value = 'risk'
  } else if (path.startsWith('/data')) {
    currentNav.value = 'data'
  } else if (path.startsWith('/strategy')) {
    currentNav.value = 'strategy'
  } else {
    currentNav.value = ''
  }
}

// 监听路由变化
watch(() => route.path, () => {
  updateCurrentNav()
}, { immediate: true })

// 方法
const goTo = (path: string) => {
  router.push(path)
}

const toggleLanguage = () => {
  console.log('切换语言')
}

const showNotifications = () => {
  console.log('显示通知')
}
</script>

<style scoped lang="scss">
.global-navbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 56px;
  padding: 0 20px;
  background: #1e222d;
  border-bottom: 1px solid #2a2e39;
  z-index: 100;

  .logo {
    display: flex;
    align-items: center;
    gap: 10px;

    .logo-icon {
      width: 28px;
      height: 28px;
      background: linear-gradient(135deg, #2962ff, #7c3aed);
      border-radius: 6px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: bold;
      font-size: 16px;
      color: white;
    }

    span {
      font-size: 18px;
      font-weight: 600;
      color: #d1d4dc;
    }
  }

  .nav-tabs {
    display: flex;
    gap: 8px;
    flex: 1;
    padding: 0 20px;

    .nav-tab {
      display: flex;
      align-items: center;
      gap: 6px;
      padding: 8px 16px;
      background: transparent;
      border: none;
      border-bottom: 2px solid transparent;
      color: #cbd5e1;
      font-size: 13px;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.2s;

      .icon-nav {
        width: 14px;
        height: 14px;
        flex-shrink: 0;
      }

      &:hover {
        color: #d1d4dc;
      }

      &.active {
        color: #2962ff;
        border-bottom-color: #2962ff;
      }
    }
  }

  .user-menu {
    display: flex;
    align-items: center;
    gap: 8px;

    .icon-btn {
      width: 32px;
      height: 32px;
      background: transparent;
      border: 1px solid #2a2e39;
      border-radius: 6px;
      cursor: pointer;
      font-size: 14px;
      display: flex;
      align-items: center;
      justify-content: center;
      color: #787b86;
      transition: all 0.2s;

      &:hover {
        background: rgba(255, 255, 255, 0.05);
        border-color: #2962ff;
        color: #d1d4dc;
      }
    }

    .version {
      font-size: 12px;
      color: #575e6a;
      padding: 0 4px;
    }

    .user-avatar {
      width: 32px;
      height: 32px;
      background: #2962ff;
      color: #ffffff;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 600;
      font-size: 13px;
    }
  }
}
</style>

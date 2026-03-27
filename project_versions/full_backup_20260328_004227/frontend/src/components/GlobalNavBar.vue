<template>
  <header class="navbar">
    <div class="logo">
      <div class="logo-icon">M</div>
      <span>MyQuant</span>
    </div>

    <nav class="nav-tabs">
      <button :class="['nav-tab', { active: currentNav === 'realtime' }]" @click="goTo('/RealtimeQuotes')">
        <svg class="icon-nav" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline>
        </svg>
        {{ isZh ? '实时行情' : 'Market' }}
      </button>
      <button :class="['nav-tab', { active: currentNav === 'workflow' }]" @click="goTo('/workflow')">
        <svg class="icon-nav" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polyline points="9 11 12 14 22 4"></polyline>
          <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"></path>
        </svg>
        {{ isZh ? '工作流' : 'Workflow' }}
      </button>
      <button :class="['nav-tab', { active: currentNav === 'monitor' }]" @click="goTo('/monitoring')">
        <svg class="icon-nav" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
          <circle cx="12" cy="12" r="3"></circle>
        </svg>
        {{ isZh ? '监控' : 'Monitor' }}
      </button>
      <button :class="['nav-tab', { active: currentNav === 'risk' }]" @click="goTo('/production/risk')">
        <svg class="icon-nav" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
        </svg>
        {{ isZh ? '风险管理' : 'Risk' }}
      </button>
      <button :class="['nav-tab', { active: currentNav === 'strategy' }]" @click="goTo('/strategy')">
        <svg class="icon-nav" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon>
        </svg>
        {{ isZh ? '策略' : 'Strategy' }}
      </button>
      <button :class="['nav-tab', { active: currentNav === 'ml-models' }]" @click="goTo('/research/ml/management')">
        <svg class="icon-nav" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"></path>
        </svg>
        {{ isZh ? 'ML模型' : 'ML Models' }}
      </button>
    </nav>

    <div class="user-menu">
      <button class="icon-btn" @click="toggleLanguage" :title="isZh ? '切换语言' : 'Toggle Language'">
        {{ isZh ? '🇨🇳' : '🇺🇸' }}
      </button>
      <button class="icon-btn" title="通知">🔔</button>
      <span class="version">v11.0.0</span>
      <div class="user-avatar">U</div>
    </div>
  </header>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAppStore } from '@/stores/core/AppStore'

const route = useRoute()
const router = useRouter()
const appStore = useAppStore()

const isZh = computed(() => appStore.language === 'zh')

const currentNav = computed(() => {
  const path = route.path
  if (path.includes('RealtimeQuotes') || path.includes('dashboard')) return 'realtime'
  if (path.includes('workflow')) return 'workflow'
  if (path.includes('monitoring') || path.includes('monitor')) return 'monitor'
  if (path.includes('risk')) return 'risk'
  if (path.includes('strategy')) return 'strategy'
  if (path.includes('ml') || path.includes('research')) return 'ml-models'
  return ''
})

const goTo = (path: string) => {
  router.push(path)
}

const toggleLanguage = () => {
  appStore.setLanguage(isZh.value ? 'en' : 'zh')
}
</script>

<style scoped>
.navbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 56px;
  padding: 0 20px;
  background: var(--bg-secondary, #1e222d);
  border-bottom: 1px solid var(--border-color, #2a2e39);
  flex-shrink: 0;
}

.logo {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 18px;
  font-weight: 600;
}

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

.nav-tabs {
  display: flex;
  gap: 8px;
  flex: 1;
}

.nav-tab {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: transparent;
  border: none;
  border-bottom: 2px solid transparent;
  color: var(--text-secondary, #cbd5e1);
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}
.nav-tab:hover {
  color: var(--text-primary, #d1d4dc);
}
.nav-tab.active {
  color: var(--accent-blue, #2962ff);
  border-bottom-color: var(--accent-blue, #2962ff);
}

.icon-nav {
  width: 14px;
  height: 14px;
  flex-shrink: 0;
}

.user-menu {
  display: flex;
  align-items: center;
  gap: 8px;
}

.icon-btn {
  width: 32px;
  height: 32px;
  background: transparent;
  border: 1px solid var(--border-color, #2a2e39);
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.icon-btn:hover {
  background: rgba(255, 255, 255, 0.05);
  border-color: var(--accent-blue, #2962ff);
}

.version {
  font-size: 11px;
  color: var(--text-secondary, #cbd5e1);
  padding: 2px 6px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 4px;
}

.user-avatar {
  width: 28px;
  height: 28px;
  background: linear-gradient(135deg, #2962ff, #7c3aed);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 600;
  color: white;
}
</style>

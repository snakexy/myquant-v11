<template>
  <div class="indicator-selector">
    <button class="tv-indicator-btn" @click="toggleMenu">
      <svg class="tv-indicator-icon" viewBox="0 0 18 18" fill="none" xmlns="http://www.w3.org/2000/svg">
        <rect x="2" y="2" width="14" height="14" rx="2" stroke="currentColor" stroke-width="1.2"/>
        <text x="5" y="12" fill="currentColor" font-size="7" font-family="Arial" font-weight="bold">f</text>
        <text x="9" y="12" fill="currentColor" font-size="6" font-family="Arial">(x)</text>
      </svg>
      <span class="tv-indicator-text">指标</span>
    </button>

    <!-- 指标菜单 -->
    <div v-if="showMenu" class="indicator-menu" :style="menuStyle">
      <div class="indicator-menu-header">
        <span>技术指标</span>
        <button class="close-btn" @click="closeMenu">✕</button>
      </div>
      <div class="indicator-menu-content">
        <!-- 独立指标 -->
        <div class="indicator-group">
          <div class="indicator-group-label">独立指标</div>
          <div
            v-for="ind in oscillators"
            :key="ind.id"
            class="indicator-item"
          >
            <label class="indicator-checkbox">
              <input
                type="checkbox"
                :checked="props.active.includes(ind.id)"
                @change="toggleOscillator(ind.id)"
              />
              <span class="checkmark"></span>
              <span class="indicator-name">{{ ind.name }}</span>
            </label>
            <button class="settings-btn" @click="openSettings(ind.id, $event)">⚙️</button>
          </div>
        </div>

        <!-- 分隔线 -->
        <div class="indicator-divider"></div>

        <!-- 主图叠加 -->
        <div class="indicator-group">
          <div class="indicator-group-label">主图叠加</div>
          <div
            v-for="ind in overlays"
            :key="ind.id"
            class="indicator-item"
          >
            <label class="indicator-checkbox">
              <input
                type="checkbox"
                :checked="props.overlay.includes(ind.id)"
                @change="toggleOverlay(ind.id)"
              />
              <span class="checkmark"></span>
              <span class="indicator-name">{{ ind.name }}</span>
            </label>
            <button class="settings-btn" @click="openSettings(ind.id, $event)">⚙️</button>
          </div>
        </div>
      </div>
    </div>

    <!-- 遮罩层 -->
    <div v-if="showMenu" class="indicator-menu-overlay" @click="closeMenu"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import {
  INDICATOR_REGISTRY,
  getOscillatorIndicators,
  getOverlayIndicators,
  type IndicatorId
} from './indicator-registry'

interface Props {
  active?: string[]
  overlay?: string[]
}

const props = withDefaults(defineProps<Props>(), {
  active: () => [],
  overlay: () => []
})

const emit = defineEmits<{
  'update:active': [indicators: string[]]
  'update:overlay': [indicators: string[]]
  'settings': [indicatorId: string]
}>()

const showMenu = ref(false)
const menuStyle = ref({})

const oscillators = computed(() => getOscillatorIndicators())
const overlays = computed(() => getOverlayIndicators())

function toggleMenu(e: MouseEvent) {
  showMenu.value = !showMenu.value
  if (showMenu.value) {
    const rect = (e.currentTarget as HTMLElement).getBoundingClientRect()
    menuStyle.value = {
      top: `${rect.bottom + 4}px`,
      left: `${rect.left}px`
    }
  }
}

function closeMenu() {
  showMenu.value = false
}

function toggleOscillator(id: string) {
  const current = [...props.active]
  const index = current.indexOf(id)
  if (index > -1) {
    current.splice(index, 1)
  } else {
    current.push(id)
  }
  emit('update:active', current)
}

function toggleOverlay(id: string) {
  const current = [...props.overlay]
  const index = current.indexOf(id)
  if (index > -1) {
    current.splice(index, 1)
  } else {
    current.push(id)
  }
  emit('update:overlay', current)
}

function openSettings(id: string, e: Event) {
  e.stopPropagation()
  emit('settings', id)
  closeMenu()
}
</script>

<style scoped>
.indicator-selector {
  display: inline-block;
  position: relative;
}

/* TradingView风格按钮 */
.tv-indicator-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  background: #2a2e39;
  border: 1px solid #434651;
  border-radius: 4px;
  color: #d1d4dc;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
  font-family: inherit;
  height: 28px;
}

.tv-indicator-btn:hover {
  background: #363a45;
  border-color: #4e5460;
}

.tv-indicator-icon {
  width: 18px;
  height: 18px;
  opacity: 0.9;
  flex-shrink: 0;
}

.tv-indicator-text {
  font-weight: 500;
}

/* 菜单样式 - 与项目统一 */
.indicator-menu {
  position: fixed;
  background: #1e222d;
  border: 1px solid #2a2e39;
  border-radius: 8px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.6);
  z-index: 1000;
  min-width: 200px;
  max-width: 280px;
}

.indicator-menu-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 999;
}

.indicator-menu-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 14px;
  border-bottom: 1px solid #2a2e39;
  font-size: 13px;
  font-weight: 600;
  color: #d1d4dc;
}

.close-btn {
  background: none;
  border: none;
  color: #787b86;
  font-size: 14px;
  cursor: pointer;
  padding: 2px 6px;
  border-radius: 4px;
  transition: all 0.2s;
}

.close-btn:hover {
  color: #d1d4dc;
  background: #2a2e39;
}

.indicator-menu-content {
  padding: 8px 0;
}

.indicator-group {
  padding: 4px 0;
}

.indicator-group-label {
  padding: 6px 14px;
  font-size: 11px;
  color: #787b86;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.indicator-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 14px;
  cursor: pointer;
  transition: background 0.2s;
}

.indicator-item:hover {
  background: #2a2e39;
}

.indicator-checkbox {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  flex: 1;
}

.indicator-checkbox input {
  display: none;
}

.checkmark {
  width: 16px;
  height: 16px;
  border: 1px solid #434651;
  border-radius: 3px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  flex-shrink: 0;
}

.indicator-checkbox input:checked + .checkmark {
  background: #2196F3;
  border-color: #2196F3;
}

.indicator-checkbox input:checked + .checkmark::after {
  content: '✓';
  color: white;
  font-size: 11px;
  font-weight: bold;
}

.indicator-name {
  font-size: 13px;
  color: #d1d4dc;
}

.settings-btn {
  background: none;
  border: none;
  color: #787b86;
  font-size: 14px;
  cursor: pointer;
  padding: 2px 6px;
  border-radius: 4px;
  opacity: 0;
  transition: all 0.2s;
}

.indicator-item:hover .settings-btn {
  opacity: 1;
}

.settings-btn:hover {
  color: #d1d4dc;
  background: #363a45;
}

.indicator-divider {
  height: 1px;
  background: #2a2e39;
  margin: 8px 0;
}
</style>

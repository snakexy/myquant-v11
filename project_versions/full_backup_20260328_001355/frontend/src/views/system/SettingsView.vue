<template>
  <div class="settings-view">
    <div class="page-header">
      <h2>系统设置</h2>
      <p>个性化配置和偏好设置</p>
    </div>

    <div class="settings-content">
      <el-card class="settings-section">
        <template #header>
          <span>外观设置</span>
        </template>

        <el-form label-width="120px">
          <el-form-item label="主题模式">
            <el-radio-group v-model="themeMode" @change="handleThemeChange">
              <el-radio-button value="light">亮色</el-radio-button>
              <el-radio-button value="dark">暗色</el-radio-button>
              <el-radio-button value="auto">跟随系统</el-radio-button>
            </el-radio-group>
          </el-form-item>

          <el-form-item label="主色调">
            <div class="color-options">
              <div
                v-for="color in colors"
                :key="color.key"
                class="color-option"
                :class="{ active: primaryColor === color.key }"
                :style="{ background: color.primary }"
                @click="handleColorChange(color.key)"
              >
                <el-icon v-if="primaryColor === color.key"><Check /></el-icon>
              </div>
            </div>
          </el-form-item>

          <el-form-item label="紧凑模式">
            <el-switch v-model="compactMode" @change="handleCompactChange" />
          </el-form-item>

          <el-form-item label="动画效果">
            <el-switch v-model="animationEnabled" @change="handleAnimationChange" />
          </el-form-item>
        </el-form>
      </el-card>

      <el-card class="settings-section">
        <template #header>
          <span>性能设置</span>
        </template>

        <el-form label-width="120px">
          <el-form-item label="数据预加载">
            <el-switch v-model="preloadingEnabled" />
            <span class="form-tip">提前加载可能查看的数据</span>
          </el-form-item>

          <el-form-item label="请求防抖">
            <el-switch v-model="debounceEnabled" />
            <span class="form-tip">减少频繁的API请求</span>
          </el-form-item>

          <el-form-item label="缓存大小">
            <el-slider v-model="cacheSize" :min="10" :max="100" show-input />
            <span class="form-tip">最大缓存条目数</span>
          </el-form-item>
        </el-form>
      </el-card>

      <el-card class="settings-section">
        <template #header>
          <span>关于</span>
        </template>

        <div class="about-info">
          <div class="logo">
            <span class="logo-text">MyQuant</span>
            <span class="version">v9.0.0</span>
          </div>
          <p class="description">现代化股票行情分析系统</p>
          <el-button type="primary" @click="checkUpdate">检查更新</el-button>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { Check } from '@element-plus/icons-vue'
import { useThemeStore } from '@/stores'

const themeStore = useThemeStore()

const themeMode = ref(themeStore.mode)
const primaryColor = ref(themeStore.primaryColor)
const compactMode = ref(themeStore.compactMode)
const animationEnabled = ref(themeStore.animationEnabled)

const preloadingEnabled = ref(true)
const debounceEnabled = ref(true)
const cacheSize = ref(50)

const colors = [
  { key: 'purple', primary: '#8b5cf6', name: '紫色' },
  { key: 'blue', primary: '#3b82f6', name: '蓝色' },
  { key: 'green', primary: '#10b981', name: '绿色' },
  { key: 'orange', primary: '#f59e0b', name: '橙色' },
  { key: 'red', primary: '#ef4444', name: '红色' }
]

const handleThemeChange = (value: string) => {
  themeStore.setMode(value as any)
}

const handleColorChange = (color: string) => {
  themeStore.setPrimaryColor(color as any)
}

const handleCompactChange = (value: boolean) => {
  themeStore.toggleCompactMode()
}

const handleAnimationChange = (value: boolean) => {
  themeStore.toggleAnimation()
}

const checkUpdate = () => {
  console.log('检查更新')
}
</script>

<style scoped lang="scss">
@import '@/styles/variables.scss';

.settings-view {
  padding: $spacing-lg;
  max-width: 900px;
  margin: 0 auto;

  .page-header {
    margin-bottom: $spacing-xl;
    text-align: center;

    h2 {
      margin: 0 0 $spacing-sm 0;
      font-size: $font-2xl;
      color: $text-primary;
    }

    p {
      margin: 0;
      color: $text-muted;
    }
  }

  .settings-content {
    display: flex;
    flex-direction: column;
    gap: $spacing-lg;
  }

  .settings-section {
    .form-tip {
      margin-left: $spacing-sm;
      font-size: $font-sm;
      color: $text-muted;
    }
  }

  .color-options {
    display: flex;
    gap: $spacing-md;

    .color-option {
      width: 40px;
      height: 40px;
      border-radius: $radius-md;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      border: 2px solid transparent;
      transition: all $transition-base;

      &:hover {
        transform: scale(1.1);
      }

      &.active {
        border-color: $text-primary;
      }

      .el-icon {
        color: white;
        font-size: $font-lg;
      }
    }
  }

  .about-info {
    text-align: center;
    padding: $spacing-xl;

    .logo {
      display: flex;
      align-items: baseline;
      justify-content: center;
      gap: $spacing-sm;
      margin-bottom: $spacing-md;

      .logo-text {
        font-size: $font-3xl;
        font-weight: 700;
        background: $gradient-primary;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
      }

      .version {
        font-size: $font-lg;
        color: $text-muted;
      }
    }

    .description {
      margin-bottom: $spacing-xl;
      color: $text-secondary;
    }
  }
}
</style>

<template>
  <div class="settings">
    <h1>系统设置</h1>
    <div class="settings-container">
      <div class="settings-sidebar">
        <h3>设置分类</h3>
        <div class="setting-categories">
          <div 
            v-for="category in categories" 
            :key="category.id"
            :class="['category-item', { active: selectedCategory === category.id }]"
            @click="selectedCategory = category.id"
          >
            <div class="category-icon">{{ category.icon }}</div>
            <span>{{ category.name }}</span>
          </div>
        </div>
      </div>
      <div class="settings-content">
        <h3>{{ getCurrentCategoryName() }}</h3>
        <div class="setting-form">
          <!-- 主题设置 -->
          <div v-if="selectedCategory === 'theme'" class="setting-section">
            <div class="form-group">
              <label>主题模式</label>
              <select v-model="themeSettings.mode" class="form-control">
                <option value="dark">暗黑模式</option>
                <option value="light">明亮模式</option>
                <option value="auto">跟随系统</option>
              </select>
            </div>
            <div class="form-group">
              <label>主题颜色</label>
              <div class="color-options">
                <div 
                  v-for="color in themeColors" 
                  :key="color.value"
                  :class="['color-option', { active: themeSettings.primaryColor === color.value }]"
                  :style="{ backgroundColor: color.value }"
                  @click="themeSettings.primaryColor = color.value"
                ></div>
              </div>
            </div>
          </div>
          
          <!-- 数据源设置 -->
          <div v-if="selectedCategory === 'data'" class="setting-section">
            <div class="form-group">
              <label>默认数据源</label>
              <select v-model="dataSettings.defaultSource" class="form-control">
                <option value="tushare">Tushare</option>
                <option value="akshare">AkShare</option>
                <option value="baostock">BaoStock</option>
              </select>
            </div>
            <div class="form-group">
              <label>数据更新频率</label>
              <select v-model="dataSettings.updateFrequency" class="form-control">
                <option value="realtime">实时</option>
                <option value="1min">1分钟</option>
                <option value="5min">5分钟</option>
                <option value="15min">15分钟</option>
              </select>
            </div>
          </div>
          
          <!-- 通知设置 -->
          <div v-if="selectedCategory === 'notification'" class="setting-section">
            <div class="form-group">
              <label>启用通知</label>
              <input type="checkbox" v-model="notificationSettings.enabled" />
            </div>
            <div class="form-group">
              <label>通知类型</label>
              <div class="checkbox-group">
                <label v-for="type in notificationTypes" :key="type.value">
                  <input type="checkbox" v-model="notificationSettings.types" :value="type.value" />
                  {{ type.label }}
                </label>
              </div>
            </div>
          </div>
          
          <!-- 系统设置 -->
          <div v-if="selectedCategory === 'system'" class="setting-section">
            <div class="form-group">
              <label>语言</label>
              <select v-model="systemSettings.language" class="form-control">
                <option value="zh-CN">简体中文</option>
                <option value="en-US">English</option>
              </select>
            </div>
            <div class="form-group">
              <label>自动保存</label>
              <input type="checkbox" v-model="systemSettings.autoSave" />
            </div>
          </div>
          
          <div class="setting-actions">
            <button class="btn-primary" @click="saveSettings">保存设置</button>
            <button class="btn-secondary" @click="resetSettings">重置默认</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useMessage } from 'naive-ui'
import { useAppStore, useUserStore } from '@/stores'

interface Category {
  id: string
  name: string
  icon: string
}

interface ThemeSettings {
  mode: 'dark' | 'light' | 'auto'
  primaryColor: string
}

interface DataSettings {
  defaultSource: string
  updateFrequency: string
}

interface NotificationSettings {
  enabled: boolean
  types: string[]
}

interface SystemSettings {
  language: string
  autoSave: boolean
}

const categories = ref<Category[]>([
  { id: 'theme', name: '主题设置', icon: '🎨' },
  { id: 'data', name: '数据源', icon: '📊' },
  { id: 'notification', name: '通知设置', icon: '🔔' },
  { id: 'system', name: '系统设置', icon: '⚙️' }
])

const selectedCategory = ref('theme')

const themeColors = [
  { value: '#2563eb', label: '蓝色' },
  { value: '#7c3aed', label: '紫色' },
  { value: '#10b981', label: '绿色' },
  { value: '#f59e0b', label: '橙色' },
  { value: '#ef4444', label: '红色' }
]

const notificationTypes = [
  { value: 'strategy', label: '策略通知' },
  { value: 'backtest', label: '回测完成' },
  { value: 'alert', label: '价格预警' },
  { value: 'system', label: '系统消息' }
]

const themeSettings = ref<ThemeSettings>({
  mode: 'dark',
  primaryColor: '#2563eb'
})

const dataSettings = ref<DataSettings>({
  defaultSource: 'tushare',
  updateFrequency: 'realtime'
})

const notificationSettings = ref<NotificationSettings>({
  enabled: true,
  types: ['strategy', 'backtest', 'alert']
})

const systemSettings = ref<SystemSettings>({
  language: 'zh-CN',
  autoSave: true
})

// 获取store
const appStore = useAppStore()
const userStore = useUserStore()
const message = useMessage()

const getCurrentCategoryName = () => {
  const category = categories.value.find(c => c.id === selectedCategory.value)
  return category ? category.name : ''
}

const loadSettings = () => {
  // 从store加载设置
  themeSettings.value = {
    mode: appStore.theme,
    primaryColor: appStore.primaryColor
  }
  
  dataSettings.value = {
    defaultSource: userStore.preferences.defaultDataSource || 'tushare',
    updateFrequency: userStore.preferences.dataUpdateFrequency || 'realtime'
  }
  
  notificationSettings.value = {
    enabled: userStore.preferences.notificationsEnabled || true,
    types: userStore.preferences.notificationTypes || ['strategy', 'backtest', 'alert']
  }
  
  systemSettings.value = {
    language: appStore.language,
    autoSave: userStore.preferences.autoSave || true
  }
}

const saveSettings = () => {
  try {
    // 保存主题设置
    appStore.setTheme(themeSettings.value.mode)
    appStore.setPrimaryColor(themeSettings.value.primaryColor)
    
    // 保存用户偏好设置
    userStore.updatePreferences({
      defaultDataSource: dataSettings.value.defaultSource,
      dataUpdateFrequency: dataSettings.value.updateFrequency,
      notificationsEnabled: notificationSettings.value.enabled,
      notificationTypes: notificationSettings.value.types,
      autoSave: systemSettings.value.autoSave
    })
    
    // 保存语言设置
    appStore.setLanguage(systemSettings.value.language)
    
    message.success('设置已保存')
  } catch (error) {
    console.error('保存设置失败:', error)
    message.error('保存设置失败，请重试')
  }
}

const resetSettings = () => {
  // 重置为默认值
  themeSettings.value = {
    mode: 'dark',
    primaryColor: '#2563eb'
  }
  
  dataSettings.value = {
    defaultSource: 'tushare',
    updateFrequency: 'realtime'
  }
  
  notificationSettings.value = {
    enabled: true,
    types: ['strategy', 'backtest', 'alert']
  }
  
  systemSettings.value = {
    language: 'zh-CN',
    autoSave: true
  }
  
  message.info('设置已重置为默认值')
}

// 生命周期
onMounted(() => {
  loadSettings()
})
</script>

<style lang="scss" scoped>
.settings {
  padding: 24px;
  
  .settings-container {
    display: grid;
    grid-template-columns: 250px 1fr;
    gap: 24px;
    margin-top: 24px;
  }
  
  .settings-sidebar, .settings-content {
    background: var(--surface-color);
    border: 1px solid var(--border-color);
    border-radius: 12px;
    padding: 24px;
    
    h3 {
      margin-top: 0;
      color: var(--text-primary);
    }
  }
  
  .setting-categories {
    .category-item {
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 12px;
      border-radius: 8px;
      cursor: pointer;
      margin-bottom: 8px;
      
      &:hover {
        background: var(--bg-color);
      }
      
      &.active {
        background: var(--primary-color);
        color: white;
      }
      
      .category-icon {
        font-size: 18px;
      }
    }
  }
  
  .setting-form {
    .setting-section {
      margin-bottom: 32px;
      
      .form-group {
        margin-bottom: 20px;
        
        label {
          display: block;
          margin-bottom: 8px;
          color: var(--text-primary);
          font-weight: 500;
        }
        
        .form-control {
          width: 100%;
          padding: 8px 12px;
          border: 1px solid var(--border-color);
          border-radius: 4px;
          background: var(--bg-color);
          color: var(--text-primary);
          
          &:focus {
            outline: none;
            border-color: var(--primary-color);
          }
        }
        
        .color-options {
          display: flex;
          gap: 8px;
          
          .color-option {
            width: 32px;
            height: 32px;
            border-radius: 50%;
            cursor: pointer;
            border: 2px solid transparent;
            
            &:hover {
              border-color: var(--text-secondary);
            }
            
            &.active {
              border-color: var(--text-primary);
            }
          }
        }
        
        .checkbox-group {
          display: flex;
          flex-direction: column;
          gap: 8px;
          
          label {
            display: flex;
            align-items: center;
            gap: 8px;
            cursor: pointer;
          }
        }
      }
    }
    
    .setting-actions {
      display: flex;
      gap: 12px;
      
      button {
        padding: 10px 20px;
        border: none;
        border-radius: 4px;
        cursor: pointer;
        
        &.btn-primary {
          background: var(--primary-color);
          color: white;
          
          &:hover {
            background: var(--primary-color-dark);
          }
        }
        
        &.btn-secondary {
          background: var(--secondary-color);
          color: white;
          
          &:hover {
            background: var(--secondary-color-dark);
          }
        }
      }
    }
  }
}
</style>
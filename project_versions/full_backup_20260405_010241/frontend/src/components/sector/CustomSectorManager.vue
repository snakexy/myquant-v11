<template>
  <div class="custom-sector-manager">
    <div class="header">
      <h3>自定义板块管理</h3>
      <el-button type="primary" size="small" @click="showCreateDialog = true">
        <el-icon><plus /></el-icon> 新建板块
      </el-button>
    </div>

    <!-- 板块列表 -->
    <div class="sector-list">
      <el-card
        v-for="sector in customSectors"
        :key="sector.id"
        class="sector-card"
        shadow="hover"
      >
        <template #header>
          <div class="card-header">
            <span class="sector-name">{{ sector.name }}</span>
            <div class="actions">
              <el-button size="small" text @click="editSector(sector)">
                <el-icon><edit /></el-icon>
              </el-button>
              <el-button size="small" text type="danger" @click="deleteSector(sector.id)">
                <el-icon><delete /></el-icon>
              </el-button>
            </div>
          </div>
        </template>

        <div class="sector-info">
          <p v-if="sector.description" class="description">{{ sector.description }}</p>
          <div class="stocks-info">
            <el-tag size="small">包含 {{ sector.stocks.length }} 只股票</el-tag>
            <el-tag
              v-if="sector.color"
              size="small"
              :style="{ backgroundColor: sector.color, border: 'none' }"
            >
              颜色标识
            </el-tag>
          </div>
          <div class="stocks-preview">
            <el-tag
              v-for="stock in sector.stocks.slice(0, 10)"
              :key="stock"
              size="small"
              class="stock-tag"
            >
              {{ stock }}
            </el-tag>
            <el-tag v-if="sector.stocks.length > 10" size="small" type="info">
              +{{ sector.stocks.length - 10 }}
            </el-tag>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 空状态 -->
    <el-empty
      v-if="customSectors.length === 0"
      description="暂无自定义板块，点击上方按钮创建"
    />

    <!-- 创建/编辑对话框 -->
    <el-dialog
      v-model="showCreateDialog"
      :title="editingSector ? '编辑板块' : '新建板块'"
      width="600px"
      :close-on-click-modal="false"
    >
      <el-form :model="formData" :rules="formRules" ref="formRef" label-width="100px">
        <el-form-item label="板块名称" prop="name">
          <el-input v-model="formData.name" placeholder="请输入板块名称" />
        </el-form-item>

        <el-form-item label="板块描述" prop="description">
          <el-input
            v-model="formData.description"
            type="textarea"
            :rows="3"
            placeholder="请输入板块描述（可选）"
          />
        </el-form-item>

        <el-form-item label="包含股票" prop="stocks">
          <div class="stocks-input">
            <el-select
              v-model="formData.stocks"
              multiple
              filterable
              allow-create
              placeholder="输入股票代码或名称，按回车添加"
              style="width: 100%"
              :max-collapse-tags="10"
            >
              <el-option
                v-for="stock in availableStocks"
                :key="stock.value"
                :label="stock.label"
                :value="stock.value"
              />
            </el-select>
            <div class="stock-count">
              已选择 {{ formData.stocks.length }} 只股票
            </div>
          </div>
        </el-form-item>

        <el-form-item label="颜色标识">
          <el-color-picker v-model="formData.color" />
          <span class="color-hint">选择一个颜色用于图表显示（可选）</span>
        </el-form-item>

        <el-form-item label="导入股票">
          <el-button size="small" @click="showImportDialog = true">
            <el-icon><upload /></el-icon> 从文件导入
          </el-button>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="cancelEdit">取消</el-button>
        <el-button type="primary" @click="saveSector" :loading="saving">
          {{ editingSector ? '保存' : '创建' }}
        </el-button>
      </template>
    </el-dialog>

    <!-- 导入股票对话框 -->
    <el-dialog
      v-model="showImportDialog"
      title="导入股票列表"
      width="500px"
    >
      <el-alert
        title="支持格式"
        type="info"
        :closable="false"
        style="margin-bottom: 16px"
      >
        <ul style="margin: 8px 0 0 0; padding-left: 20px;">
          <li>每行一个股票代码（如：600519）</li>
          <li>支持CSV格式（代码,名称）</li>
          <li>最多支持1000只股票</li>
        </ul>
      </el-alert>

      <el-input
        v-model="importText"
        type="textarea"
        :rows="10"
        placeholder="请输入股票列表，每行一个股票代码&#10;示例：&#10;600519&#10;600000&#10;000001"
      />

      <template #footer>
        <el-button @click="showImportDialog = false">取消</el-button>
        <el-button type="primary" @click="importStocks">
          导入 ({{ stockList.length }} 只股票)
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Edit, Delete, Upload } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores'

const userStore = useUserStore()

// 自定义板块列表
const customSectors = computed(() => userStore.customSectorManager.getAll())

// 对话框状态
const showCreateDialog = ref(false)
const showImportDialog = ref(false)
const editingSector = ref<any>(null)
const saving = ref(false)

// 表单数据
const formData = ref({
  name: '',
  description: '',
  stocks: [] as string[],
  color: ''
})

const importText = ref('')

// 表单引用
const formRef = ref()

// 表单验证规则
const formRules = {
  name: [
    { required: true, message: '请输入板块名称', trigger: 'blur' }
  ],
  stocks: [
    { required: true, message: '请选择至少一只股票', trigger: 'change' }
  ]
}

// 可选股票列表（示例）
const availableStocks = ref([
  { label: '贵州茅台 (600519)', value: '600519' },
  { label: '浦发银行 (600000)', value: '600000' },
  { label: '招商银行 (600036)', value: '600036' },
  { label: '中国平安 (601318)', value: '601318' },
  { label: '工商银行 (601398)', value: '601398' },
  { label: '平安银行 (000001)', value: '000001' },
  { label: '万科A (000002)', value: '000002' },
  { label: '五粮液 (000858)', value: '000858' },
  { label: '海康威视 (002415)', value: '002415' },
  { label: '比亚迪 (002594)', value: '002594' }
])

// 从导入文本解析股票列表
const stockList = computed(() => {
  if (!importText.value.trim()) {
    return []
  }

  const lines = importText.value.trim().split('\n')
  const stocks: string[] = []

  lines.forEach(line => {
    line = line.trim()
    if (!line) return

    // CSV格式：代码,名称
    if (line.includes(',')) {
      const parts = line.split(',')
      const code = parts[0].trim()
      if (/^\d{6}$/.test(code)) {
        stocks.push(code)
      }
    } else {
      // 纯代码
      if (/^\d{6}$/.test(line)) {
        stocks.push(line)
      }
    }
  })

  return stocks
})

// 编辑板块
const editSector = (sector: any) => {
  editingSector.value = sector
  formData.value = {
    name: sector.name,
    description: sector.description || '',
    stocks: [...sector.stocks],
    color: sector.color || ''
  }
  showCreateDialog.value = true
}

// 删除板块
const deleteSector = async (id: string) => {
  try {
    await ElMessageBox.confirm(
      '确定要删除这个自定义板块吗？',
      '确认删除',
      {
        confirmButtonText: '删除',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    const success = userStore.customSectorManager.delete(id)

    if (success) {
      ElMessage.success('删除成功')
    } else {
      ElMessage.error('删除失败')
    }
  } catch {
    // 用户取消
  }
}

// 保存板块
const saveSector = async () => {
  try {
    await formRef.value?.validate()

    saving.value = true

    if (editingSector.value) {
      // 更新
      userStore.customSectorManager.update(editingSector.value.id, {
        name: formData.value.name,
        description: formData.value.description,
        stocks: formData.value.stocks,
        color: formData.value.color
      })
      ElMessage.success('更新成功')
    } else {
      // 创建
      userStore.customSectorManager.add({
        name: formData.value.name,
        description: formData.value.description,
        stocks: formData.value.stocks,
        color: formData.value.color
      })
      ElMessage.success('创建成功')
    }

    cancelEdit()
  } catch (e) {
    console.error('保存失败:', e)
  } finally {
    saving.value = false
  }
}

// 取消编辑
const cancelEdit = () => {
  showCreateDialog.value = false
  editingSector.value = null
  formData.value = {
    name: '',
    description: '',
    stocks: [],
    color: ''
  }
  formRef.value?.resetFields()
}

// 导入股票
const importStocks = () => {
  if (stockList.value.length === 0) {
    ElMessage.warning('未找到有效的股票代码')
    return
  }

  // 合并到现有股票
  const existingStocks = new Set(formData.value.stocks)
  let addedCount = 0

  stockList.value.forEach(stock => {
    if (!existingStocks.has(stock)) {
      formData.value.stocks.push(stock)
      addedCount++
    }
  })

  ElMessage.success(`成功导入 ${addedCount} 只股票`)
  showImportDialog.value = false
  importText.value = ''
}

onMounted(() => {
  // 加载可选股票列表（可以从API获取）
})
</script>

<style scoped lang="scss">
.custom-sector-manager {
  padding: 20px;

  .header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;

    h3 {
      margin: 0;
      font-size: 18px;
      color: #f8fafc;
    }
  }

  .sector-list {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
    gap: 16px;

    .sector-card {
      background: #1a1a2e;
      border: 1px solid rgba(139, 92, 246, 0.2);

      :deep(.el-card__header) {
        background: rgba(139, 92, 246, 0.05);
        padding: 12px 16px;
      }

      :deep(.el-card__body) {
        padding: 16px;
      }

      .card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;

        .sector-name {
          font-weight: bold;
          color: #f8fafc;
        }

        .actions {
          display: flex;
          gap: 4px;
        }
      }

      .sector-info {
        .description {
          margin: 0 0 12px 0;
          color: #cbd5e1;
          font-size: 14px;
        }

        .stocks-info {
          display: flex;
          gap: 8px;
          margin-bottom: 12px;
        }

        .stocks-preview {
          display: flex;
          flex-wrap: wrap;
          gap: 6px;

          .stock-tag {
            font-family: 'Courier New', monospace;
          }
        }
      }
    }
  }

  .stocks-input {
    .stock-count {
      margin-top: 8px;
      font-size: 12px;
      color: #94a3b8;
    }
  }

  .color-hint {
    margin-left: 12px;
    font-size: 12px;
    color: #94a3b8;
  }
}
</style>

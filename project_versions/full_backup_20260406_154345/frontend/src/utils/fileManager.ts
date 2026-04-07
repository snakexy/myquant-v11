import type { Node, Connection } from '../views/NodeWorkflow.vue'

export interface WorkflowFile {
  version: string
  name: string
  description?: string
  createdAt: string
  updatedAt: string
  nodes: Node[]
  connections: Connection[]
  canvasOffset: { x: number; y: number }
  canvasScale: number
  metadata?: {
    tags?: string[]
    category?: string
    author?: string
  }
}

export interface ExportOptions {
  format: 'json' | 'csv' | 'xlsx'
  includeResults?: boolean
  includeLogs?: boolean
}

class FileManager {
  private readonly FILE_VERSION = '1.0.0'
  private readonly STORAGE_KEY = 'myquant-workflows'

  /**
   * 保存工作流到文件
   */
  async saveWorkflow(
    workflow: Omit<WorkflowFile, 'version' | 'createdAt' | 'updatedAt'>,
    filename?: string
  ): Promise<void> {
    const workflowFile: WorkflowFile = {
      version: this.FILE_VERSION,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      ...workflow
    }

    // 生成默认文件名
    if (!filename) {
      const timestamp = new Date().toISOString().replace(/[:.]/g, '-')
      filename = `${workflow.name || 'workflow'}-${timestamp}.json`
    }

    // 确保文件名有扩展名
    if (!filename.endsWith('.json')) {
      filename += '.json'
    }

    // 创建并下载文件
    const blob = new Blob([JSON.stringify(workflowFile, null, 2)], {
      type: 'application/json'
    })

    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)

    // 同时保存到本地存储
    this.saveToLocalStorage(workflowFile)
  }

  /**
   * 从文件加载工作流
   */
  async loadWorkflow(file: File): Promise<WorkflowFile> {
    return new Promise((resolve, reject) => {
      const reader = new FileReader()

      reader.onload = (e) => {
        try {
          const content = e.target?.result as string
          const workflow = JSON.parse(content) as WorkflowFile

          // 验证文件格式
          if (!this.validateWorkflowFile(workflow)) {
            reject(new Error('无效的工作流文件格式'))
            return
          }

          resolve(workflow)
        } catch (error) {
          reject(new Error('解析工作流文件失败: ' + (error as Error).message))
        }
      }

      reader.onerror = () => {
        reject(new Error('读取文件失败'))
      }

      reader.readAsText(file)
    })
  }

  /**
   * 导出工作流执行结果
   */
  async exportResults(
    results: any,
    options: ExportOptions = { format: 'json' }
  ): Promise<void> {
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-')
    let filename = `workflow-results-${timestamp}`
    let content: string | Blob
    let mimeType: string

    switch (options.format) {
      case 'json':
        filename += '.json'
        content = JSON.stringify(results, null, 2)
        mimeType = 'application/json'
        break

      case 'csv':
        filename += '.csv'
        content = this.convertToCSV(results)
        mimeType = 'text/csv'
        break

      case 'xlsx':
        filename += '.xlsx'
        content = await this.convertToXLSX(results)
        mimeType = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        break

      default:
        throw new Error(`不支持的导出格式: ${options.format}`)
    }

    const blob = content instanceof Blob ? content : new Blob([content], { type: mimeType })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
  }

  /**
   * 保存工作流配置到本地存储
   */
  private saveToLocalStorage(workflow: WorkflowFile): void {
    try {
      const stored = this.getStoredWorkflows()
      const existingIndex = stored.findIndex(w => w.name === workflow.name)

      if (existingIndex >= 0) {
        stored[existingIndex] = workflow
      } else {
        stored.push(workflow)
      }

      // 限制存储数量（最多保存20个）
      if (stored.length > 20) {
        stored.splice(0, stored.length - 20)
      }

      localStorage.setItem(this.STORAGE_KEY, JSON.stringify(stored))
    } catch (error) {
      console.warn('保存到本地存储失败:', error)
    }
  }

  /**
   * 获取存储的工作流列表
   */
  getStoredWorkflows(): WorkflowFile[] {
    try {
      const stored = localStorage.getItem(this.STORAGE_KEY)
      return stored ? JSON.parse(stored) : []
    } catch (error) {
      console.warn('读取本地存储失败:', error)
      return []
    }
  }

  /**
   * 删除存储的工作流
   */
  deleteStoredWorkflow(name: string): void {
    try {
      const stored = this.getStoredWorkflows()
      const filtered = stored.filter(w => w.name !== name)
      localStorage.setItem(this.STORAGE_KEY, JSON.stringify(filtered))
    } catch (error) {
      console.warn('删除存储的工作流失败:', error)
    }
  }

  /**
   * 验证工作流文件格式
   */
  private validateWorkflowFile(workflow: any): workflow is WorkflowFile {
    if (!workflow || typeof workflow !== 'object') {
      return false
    }

    // 检查必需的数组字段
    if (!Array.isArray(workflow.nodes) || !Array.isArray(workflow.connections)) {
      return false
    }

    // 检查节点是否有必要的字段
    const hasValidNodes = workflow.nodes.every((node: any) =>
      node && typeof node.id === 'string' && typeof node.title === 'string'
    )

    if (!hasValidNodes) {
      return false
    }

    // canvasOffset 和 canvasScale 是可选的，如果不存在则使用默认值
    if (typeof workflow.canvasOffset !== 'object') {
      workflow.canvasOffset = { x: 0, y: 0 }
    }
    if (typeof workflow.canvasScale !== 'number') {
      workflow.canvasScale = 1
    }

    return true
  }

  /**
   * 转换为CSV格式
   */
  private convertToCSV(data: any): string {
    if (!data || typeof data !== 'object') {
      return ''
    }

    // 如果是数组
    if (Array.isArray(data)) {
      if (data.length === 0) return ''

      const headers = Object.keys(data[0])
      const rows = data.map(item =>
        headers.map(header => {
          const value = item[header]
          return typeof value === 'string' && value.includes(',')
            ? `"${value.replace(/"/g, '""')}"`
            : String(value)
        })
      )

      return [headers, ...rows].map(row => row.join(',')).join('\n')
    }

    // 如果是对象
    const headers = ['Property', 'Value']
    const rows = Object.entries(data).map(([key, value]) => {
      const strValue = typeof value === 'object' ? JSON.stringify(value) : String(value)
      return `"${key}","${strValue.replace(/"/g, '""')}"`
    })

    return [headers, ...rows].join('\n')
  }

  /**
   * 转换为XLSX格式（简化版）
   */
  private async convertToXLSX(data: any): Promise<Blob> {
    // 这里应该使用库如 xlsx 或 exceljs
    // 为了简化，我们返回CSV格式的blob
    const csvContent = this.convertToCSV(data)
    return new Blob([csvContent], { type: 'application/vnd.ms-excel' })
  }

  /**
   * 导出节点数据为单独文件
   */
  async exportNodeData(
    nodeId: string,
    nodeName: string,
    data: any,
    format: 'json' | 'csv' = 'json'
  ): Promise<void> {
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-')
    const filename = `${nodeName}_${nodeId}_${timestamp}`

    let content: string | Blob
    let mimeType: string

    if (format === 'json') {
      content = JSON.stringify(data, null, 2)
      mimeType = 'application/json'
    } else {
      content = this.convertToCSV(data)
      mimeType = 'text/csv'
    }

    const blob = content instanceof Blob ? content : new Blob([content], { type: mimeType })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `${filename}.${format}`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
  }

  /**
   * 批量导出多个节点数据
   */
  async exportMultipleNodeData(
    nodeDataMap: Record<string, { name: string; data: any }>,
    format: 'json' | 'csv' = 'json'
  ): Promise<void> {
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-')
    const filename = `workflow_nodes_${timestamp}`

    if (format === 'json') {
      const combinedData = Object.fromEntries(
        Object.entries(nodeDataMap).map(([id, { name, data }]) => [`${name}_${id}`, data])
      )

      await this.exportResults(combinedData, { format: 'json' })
    } else {
      // CSV格式 - 为每个节点创建一个工作表
      const csvContent = Object.entries(nodeDataMap)
        .map(([id, { name, data }]) => {
          const csv = this.convertToCSV(data)
          return `=== ${name} (${id}) ===\n${csv}\n`
        })
        .join('\n')

      const blob = new Blob([csvContent], { type: 'text/csv' })
      const url = URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `${filename}.csv`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      URL.revokeObjectURL(url)
    }
  }

  /**
   * 创建工作流模板
   */
  createWorkflowTemplate(
    name: string,
    description: string,
    nodes: Node[],
    connections: Connection[]
  ): WorkflowFile {
    return {
      version: this.FILE_VERSION,
      name,
      description,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      nodes,
      connections,
      canvasOffset: { x: 0, y: 0 },
      canvasScale: 1,
      metadata: {
        tags: ['template'],
        category: 'template'
      }
    }
  }

  /**
   * 从模板加载工作流
   */
  loadFromTemplate(template: WorkflowFile): Omit<WorkflowFile, 'name' | 'createdAt' | 'updatedAt'> {
    const { name, createdAt, updatedAt, ...templateData } = template
    return {
      ...templateData,
      name: `${name} - Copy`,
      description: template.description ? `Copy of ${template.description}` : undefined
    }
  }
}

// 创建全局文件管理器实例
export const fileManager = new FileManager()
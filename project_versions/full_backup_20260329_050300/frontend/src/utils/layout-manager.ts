/**
 * 工作流布局管理器
 * 提供布局的保存、加载、导入、导出功能
 */

export interface LayoutData {
  nodePositions: Record<string, { x: number; y: number }>
  canvasOffset: { x: number; y: number }
  canvasScale: number
  timestamp: string
}

class LayoutManager {
  private readonly STORAGE_KEY = 'node-workflow-layout'

  /**
   * 保存布局到浏览器存储并下载文件
   */
  saveLayout(layoutData: LayoutData): void {
    try {
      // 保存到 localStorage
      localStorage.setItem(this.STORAGE_KEY, JSON.stringify(layoutData))
      console.log('布局已保存到浏览器缓存', layoutData)

      // 下载文件
      this.downloadLayoutFile(layoutData)
    } catch (error) {
      console.error('保存布局失败:', error)
      throw error
    }
  }

  /**
   * 下载布局文件
   */
  private downloadLayoutFile(layoutData: LayoutData): void {
    const dataStr = JSON.stringify(layoutData, null, 2)
    const dataBlob = new Blob([dataStr], { type: 'application/json' })
    const url = URL.createObjectURL(dataBlob)

    const link = document.createElement('a')
    link.href = url
    link.download = `node-workflow-layout-${new Date().toISOString().slice(0, 10)}.json`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
  }

  /**
   * 从浏览器存储加载布局
   */
  loadLayoutFromStorage(): LayoutData | null {
    try {
      const savedLayout = localStorage.getItem(this.STORAGE_KEY)
      if (savedLayout) {
        return JSON.parse(savedLayout)
      }
      return null
    } catch (error) {
      console.error('加载布局失败:', error)
      return null
    }
  }

  /**
   * 从文件加载布局
   */
  async loadLayoutFromFile(file: File): Promise<LayoutData> {
    return new Promise((resolve, reject) => {
      const reader = new FileReader()
      reader.onload = (e) => {
        try {
          const layoutData = JSON.parse(e.target?.result as string)

          // 验证布局数据格式
          if (!this.validateLayoutData(layoutData)) {
            throw new Error('无效的布局文件格式')
          }

          // 同时保存到 localStorage
          localStorage.setItem(this.STORAGE_KEY, JSON.stringify(layoutData))

          resolve(layoutData)
        } catch (error) {
          reject(new Error('文件解析失败: ' + (error as Error).message))
        }
      }
      reader.onerror = () => reject(new Error('文件读取失败'))
      reader.readAsText(file)
    })
  }

  /**
   * 验证布局数据格式
   */
  private validateLayoutData(data: any): data is LayoutData {
    return (
      data &&
      typeof data === 'object' &&
      typeof data.nodePositions === 'object' &&
      typeof data.canvasOffset === 'object' &&
      typeof data.canvasScale === 'number' &&
      typeof data.timestamp === 'string'
    )
  }

  /**
   * 重置布局
   */
  resetLayout(): void {
    localStorage.removeItem(this.STORAGE_KEY)
    console.log('布局已重置')
  }

  /**
   * 导出布局文件
   */
  exportLayout(): void {
    const layoutData = this.loadLayoutFromStorage()
    if (layoutData) {
      this.downloadLayoutFile(layoutData)
    } else {
      throw new Error('没有找到保存的布局')
    }
  }
}

export const layoutManager = new LayoutManager()
export default layoutManager
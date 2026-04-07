import { apiRequest, type ApiResponse } from '../index'

/**
 * 工作流布局API
 * 用于保存和加载工作流的可视化布局
 */

// 布局数据接口
export interface WorkflowLayout {
  nodePositions: Record<string, { x: number; y: number }>
  canvasOffset: { x: number; y: number }
  canvasScale: number
  timestamp: string
}

// 保存工作流布局到文件
export const saveWorkflowLayoutToFile = async (
  layoutData: WorkflowLayout
): Promise<ApiResponse<{ success: boolean; filePath?: string }>> => {
  return apiRequest.post('/workflow/layout/save', layoutData)
}

// 从文件加载工作流布局
export const loadWorkflowLayoutFromFile = async (): Promise<ApiResponse<WorkflowLayout | null>> => {
  return apiRequest.get('/workflow/layout/load')
}

// 删除保存的工作流布局文件
export const deleteWorkflowLayoutFile = async (): Promise<ApiResponse<{ success: boolean }>> => {
  return apiRequest.delete('/workflow/layout/delete')
}

// 导出工作流布局到指定位置
export const exportWorkflowLayout = async (
  filePath?: string
): Promise<ApiResponse<{ success: boolean; downloadUrl?: string }>> => {
  const url = filePath ? `/workflow/layout/export?path=${encodeURIComponent(filePath)}` : '/workflow/layout/export'
  return apiRequest.get(url)
}

// 导入工作流布局
export const importWorkflowLayout = async (
  layoutData: WorkflowLayout
): Promise<ApiResponse<{ success: boolean }>> => {
  return apiRequest.post('/workflow/layout/import', layoutData)
}

// 布局API对象
export const layoutApi = {
  save: saveWorkflowLayoutToFile,
  load: loadWorkflowLayoutFromFile,
  delete: deleteWorkflowLayoutFile,
  export: exportWorkflowLayout,
  import: importWorkflowLayout
}

export default layoutApi
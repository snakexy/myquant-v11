export interface DrawingTool {
  id: string
  name: string
  icon: string
  category: 'basic' | 'drawing' | 'zoom' | 'other'
  starred?: boolean  // 是否标星收藏
}

export interface DrawingState {
  activeTool: string
  tools: DrawingTool[]
  drawings: Map<string, any>
}

export interface Position {
  x: number
  y: number
}

export interface DrawingObject {
  id: string
  type: string
  points: Position[]
  options: Record<string, any>
}

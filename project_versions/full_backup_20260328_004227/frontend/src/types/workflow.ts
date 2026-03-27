export interface Node {
  id: string
  type: string
  title: string
  description?: string
  position: { x: number; y: number }
  params?: Record<string, any>
  inputs?: Array<{
    id: string
    name: string
    type: string
    required?: boolean
  }>
  outputs?: Array<{
    id: string
    name: string
    type: string
  }>
  status?: 'idle' | 'running' | 'completed' | 'failed'
}

export interface Connection {
  id: string
  from: string
  to: string
  fromOutputId?: string
  toInputId?: string
  type?: 'data' | 'control'
}
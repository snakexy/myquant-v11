// 组件类型定义

import type { 
  ComponentSize, 
  ComponentStatus, 
  ColorType, 
  LoadingState,
  ChartType,
  LayoutType,
  NotificationType,
  AlertType,
  OrderType,
  OrderStatus,
  PositionType,
  TradeDirection,
  StrategyType,
  BacktestStatus,
  RiskLevel,
  TableSize,
  StepStatus,
  ProgressStatus,
  StrategyStatus
} from '@/types/global'

// 基础组件Props类型
export interface BaseComponentProps {
  size?: ComponentSize
  status?: ComponentStatus
  disabled?: boolean
  loading?: boolean
  className?: string
  style?: Record<string, any>
}

// 按钮组件Props
export interface ButtonProps extends BaseComponentProps {
  type?: ColorType
  variant?: 'primary' | 'secondary' | 'outline' | 'text' | 'link'
  shape?: 'rounded' | 'square' | 'circle'
  icon?: string
  iconPosition?: 'left' | 'right'
  block?: boolean
  ghost?: boolean
  dashed?: boolean
  href?: string
  target?: '_blank' | '_self' | '_parent' | '_top'
  htmlType?: 'button' | 'submit' | 'reset'
  onClick?: (event: MouseEvent) => void
}

// 输入框组件Props
export interface InputProps extends BaseComponentProps {
  type?: 'text' | 'password' | 'number' | 'email' | 'url' | 'tel' | 'search'
  placeholder?: string
  value?: string | number
  defaultValue?: string | number
  maxLength?: number
  minLength?: number
  readonly?: boolean
  autocomplete?: string
  pattern?: string
  step?: number
  min?: number
  max?: number
  precision?: number
  prefix?: string
  suffix?: string
  clearable?: boolean
  showCount?: boolean
  allowClear?: boolean
  onChange?: (value: string | number) => void
  onBlur?: (event: FocusEvent) => void
  onFocus?: (event: FocusEvent) => void
  onEnter?: (event: KeyboardEvent) => void
}

// 选择器组件Props
export interface SelectProps extends BaseComponentProps {
  options: Array<{
    label: string
    value: any
    disabled?: boolean
    icon?: string
    description?: string
  }>
  value?: any
  defaultValue?: any
  placeholder?: string
  multiple?: boolean
  searchable?: boolean
  clearable?: boolean
  showSearch?: boolean
  filterOption?: boolean | ((input: string, option: any) => boolean)
  maxTagCount?: number
  loading?: boolean
  showArrow?: boolean
  onChange?: (value: any) => void
  onSearch?: (value: string) => void
}

// 模态框组件Props
export interface ModalProps extends BaseComponentProps {
  visible?: boolean
  title?: string
  width?: number | string
  height?: number | string
  centered?: boolean
  closable?: boolean
  maskClosable?: boolean
  keyboard?: boolean
  mask?: boolean
  zIndex?: number
  wrapClassName?: string
  footer?: any
  onCancel?: () => void
  onOk?: () => void
  afterClose?: () => void
}

// 卡片组件Props
export interface CardProps extends BaseComponentProps {
  title?: string
  subtitle?: string
  extra?: any
  cover?: string
  actions?: any[]
  hoverable?: boolean
  bordered?: boolean
  shadow?: boolean
  bodyStyle?: Record<string, any>
  headStyle?: Record<string, any>
  onClick?: () => void
}

// 表格组件Props
export interface TableProps extends Omit<BaseComponentProps, 'size'> {
  columns: Array<{
    key: string
    title: string
    dataIndex?: string
    width?: number | string
    align?: 'left' | 'center' | 'right'
    fixed?: 'left' | 'right'
    sortable?: boolean
    filterable?: boolean
    resizable?: boolean
    render?: (value: any, record: any, index: number) => any
  }>
  data: any[]
  rowKey?: string | ((record: any) => string)
  loading?: boolean
  pagination?: {
    current?: number
    pageSize?: number
    total?: number
    showSizeChanger?: boolean
    showQuickJumper?: boolean
    showTotal?: boolean
  }
  scroll?: {
    x?: number | string
    y?: number | string
  }
  size?: TableSize
  bordered?: boolean
  striped?: boolean
  hoverable?: boolean
  selectable?: boolean
  expandable?: boolean
  onRowClick?: (record: any, index: number) => void
  onSelectionChange?: (selectedRows: any[], selectedRowKeys: any[]) => void
  onPageChange?: (page: number, pageSize: number) => void
  onSortChange?: (sorter: any) => void
  onFilterChange?: (filters: any) => void
}

// 表单组件Props
export interface FormProps extends BaseComponentProps {
  modelValue?: Record<string, any>
  rules?: Record<string, any[]>
  layout?: 'horizontal' | 'vertical' | 'inline'
  labelWidth?: string | number
  labelAlign?: 'left' | 'right'
  colon?: boolean
  disabled?: boolean
  validateOnRuleChange?: boolean
  hideRequiredMark?: boolean
  onSubmit?: (values: Record<string, any>) => void
  onValidate?: (errors: any) => void
}

// 表单项Props
export interface FormItemProps extends BaseComponentProps {
  name?: string
  label?: string
  required?: boolean
  rules?: any[]
  validateStatus?: 'success' | 'warning' | 'error' | 'validating'
  help?: string
  extra?: string
  colon?: boolean
  hasFeedback?: boolean
}

// 加载组件Props
export interface LoadingProps extends BaseComponentProps {
  tip?: string
  delay?: number
  spin?: boolean
  indicator?: any
  size?: ComponentSize
  wrapperClassName?: string
}

// 通知组件Props
export interface NotificationProps {
  type?: NotificationType
  title?: string
  message?: string
  duration?: number
  closable?: boolean
  showIcon?: boolean
  onClick?: () => void
  onClose?: () => void
}

// 警告组件Props
export interface AlertProps extends BaseComponentProps {
  type?: AlertType
  title?: string
  message?: string
  description?: string
  closable?: boolean
  showIcon?: boolean
  banner?: boolean
  action?: any
  afterClose?: () => void
}

// 标签页组件Props
export interface TabsProps extends BaseComponentProps {
  activeKey?: string
  defaultActiveKey?: string
  type?: 'line' | 'card' | 'editable-card'
  size?: ComponentSize
  tabPosition?: 'top' | 'right' | 'bottom' | 'left'
  animated?: boolean
  hideAdd?: boolean
  centered?: boolean
  onChange?: (activeKey: string) => void
  onTabClick?: (activeKey: string, event: MouseEvent) => void
  onEdit?: (targetKey: string, action: 'add' | 'remove') => void
}

// 标签页项Props
export interface TabPaneProps {
  key: string
  tab: string
  disabled?: boolean
  closable?: boolean
  forceRender?: boolean
}

// 步骤条组件Props
export interface StepsProps extends BaseComponentProps {
  current?: number
  initial?: number
  direction?: 'horizontal' | 'vertical'
  size?: ComponentSize
  status?: StepStatus
  labelPlacement?: 'horizontal' | 'vertical'
  onChange?: (current: number) => void
}

// 步骤条项Props
export interface StepProps {
  title?: string
  description?: string
  icon?: any
  status?: StepStatus
  disabled?: boolean
  subTitle?: string
}

// 进度条组件Props
export interface ProgressProps extends BaseComponentProps {
  type?: 'line' | 'circle' | 'dashboard'
  percent?: number
  format?: (percent?: number) => string
  status?: ProgressStatus
  showInfo?: boolean
  strokeWidth?: number
  strokeLinecap?: 'butt' | 'round' | 'square'
  trailColor?: string
  strokeColor?: string
  gapDegree?: number
  gapPosition?: 'top' | 'bottom' | 'left' | 'right'
  width?: number
  successPercent?: number
}

// 时间选择器Props
export interface DatePickerProps extends BaseComponentProps {
  value?: string | Date
  defaultValue?: string | Date
  format?: string
  showTime?: boolean
  showToday?: boolean
  disabled?: boolean
  disabledDate?: (currentDate: Date) => boolean
  placeholder?: string
  onChange?: (date: Date, dateString: string) => void
  onOk?: (date: Date) => void
}

// 时间范围选择器Props
export interface RangePickerProps extends BaseComponentProps {
  value?: [string, string] | [Date, Date]
  defaultValue?: [string, string] | [Date, Date]
  format?: string
  showTime?: boolean
  separator?: string
  disabled?: boolean
  disabledDate?: (currentDate: Date) => boolean
  placeholder?: [string, string]
  onChange?: (dates: [Date, Date] | null, dateStrings: [string, string]) => void
}

// 数字输入框Props
export interface InputNumberProps extends BaseComponentProps {
  value?: number
  defaultValue?: number
  min?: number
  max?: number
  step?: number
  precision?: number
  disabled?: boolean
  placeholder?: string
  formatter?: (value: number | string) => string
  parser?: (value: string) => number
  onChange?: (value: number) => void
  onFocus?: (event: FocusEvent) => void
  onBlur?: (event: FocusEvent) => void
}

// 开关组件Props
export interface SwitchProps extends BaseComponentProps {
  checked?: boolean
  defaultChecked?: boolean
  disabled?: boolean
  loading?: boolean
  checkedChildren?: any
  unCheckedChildren?: any
  onChange?: (checked: boolean) => void
}

// 单选框组件Props
export interface RadioProps extends BaseComponentProps {
  checked?: boolean
  defaultChecked?: boolean
  disabled?: boolean
  value?: any
  onChange?: (event: Event) => void
}

// 单选框组Props
export interface RadioGroupProps extends BaseComponentProps {
  value?: any
  defaultValue?: any
  disabled?: boolean
  buttonStyle?: 'outline' | 'solid'
  optionType?: 'default' | 'button'
  onChange?: (value: any) => void
}

// 复选框组件Props
export interface CheckboxProps extends BaseComponentProps {
  checked?: boolean
  defaultChecked?: boolean
  disabled?: boolean
  indeterminate?: boolean
  onChange?: (event: Event) => void
}

// 复选框组Props
export interface CheckboxGroupProps extends BaseComponentProps {
  value?: any[]
  defaultValue?: any[]
  disabled?: boolean
  options?: Array<{
    label: string
    value: any
    disabled?: boolean
  }>
  onChange?: (checkedValue: any[]) => void
}

// 滑块组件Props
export interface SliderProps extends BaseComponentProps {
  value?: number | [number, number]
  defaultValue?: number | [number, number]
  min?: number
  max?: number
  step?: number
  marks?: Record<number, string>
  disabled?: boolean
  range?: boolean
  vertical?: boolean
  included?: boolean
  tooltipVisible?: boolean
  tooltipPlacement?: string
  onChange?: (value: number | [number, number]) => void
  onAfterChange?: (value: number | [number, number]) => void
}

// 速率选择器Props
export interface RateProps extends BaseComponentProps {
  value?: number
  defaultValue?: number
  count?: number
  disabled?: boolean
  allowHalf?: boolean
  character?: any
  tooltips?: string[]
  onChange?: (value: number) => void
  onHoverChange?: (value: number) => void
}

// 上传组件Props
export interface UploadProps extends BaseComponentProps {
  action?: string
  accept?: string
  multiple?: boolean
  disabled?: boolean
  listType?: 'text' | 'picture' | 'picture-card'
  data?: Record<string, any>
  headers?: Record<string, string>
  withCredentials?: boolean
  showUploadList?: boolean
  directory?: boolean
  beforeUpload?: (file: File, fileList: File[]) => boolean | Promise<boolean>
  onChange?: (info: any) => void
  onPreview?: (file: File) => void
  onRemove?: (file: File) => void | boolean
  onDrop?: (e: DragEvent) => void
}

// 树形组件Props
export interface TreeProps extends BaseComponentProps {
  treeData: any[]
  value?: any[]
  defaultValue?: any[]
  multiple?: boolean
  checkable?: boolean
  selectable?: boolean
  disabled?: boolean
  expandedKeys?: any[]
  defaultExpandedKeys?: any[]
  autoExpandParent?: boolean
  defaultExpandAll?: boolean
  checkStrictly?: boolean
  showLine?: boolean
  showIcon?: boolean
  draggable?: boolean
  blockNode?: boolean
  filterTreeNode?: (node: any) => boolean
  onSelect?: (selectedKeys: any[], info: any) => void
  onCheck?: (checkedKeys: any[], info: any) => void
  onExpand?: (expandedKeys: any[], info: any) => void
  onDragStart?: (info: any) => void
  onDragEnter?: (info: any) => void
  onDragLeave?: (info: any) => void
  onDrop?: (info: any) => void
}

// 图表组件Props
export interface ChartProps extends BaseComponentProps {
  type: ChartType
  data: any[]
  width?: number | string
  height?: number | string
  title?: string
  subtitle?: string
  xAxis?: any
  yAxis?: any
  series?: any[]
  legend?: any
  tooltip?: any
  grid?: any
  colors?: string[]
  theme?: 'light' | 'dark'
  animation?: boolean
  loading?: boolean
  empty?: boolean
  onEvents?: Record<string, Function>
}

// 架构图组件Props
export interface ArchitectureGraphProps extends BaseComponentProps {
  nodes: any[]
  edges: any[]
  layout?: 'hierarchical' | 'physics' | 'circular' | 'grid'
  height?: number
  width?: number
  physics?: boolean
  animation?: boolean
  onNodeClick?: (node: any) => void
  onEdgeClick?: (edge: any) => void
  onDoubleClick?: (params: any) => void
  onContext?: (params: any) => void
}

// K线图组件Props
export interface KLineChartProps extends BaseComponentProps {
  data: any[]
  symbol?: string
  timeframe?: string
  height?: number
  width?: number
  showVolume?: boolean
  showMA?: boolean
  maPeriods?: number[]
  showTooltip?: boolean
  showLegend?: boolean
  theme?: 'light' | 'dark'
  onCrosshairMove?: (params: any) => void
  onDataZoom?: (params: any) => void
}

// 实时数据流组件Props
export interface RealtimeDataFlowProps extends BaseComponentProps {
  data: any[]
  height?: number
  width?: number
  speed?: 'slow' | 'normal' | 'fast'
  direction?: 'horizontal' | 'vertical'
  particleCount?: number
  color?: string
  animation?: boolean
}

// 股票卡片组件Props
export interface StockCardProps extends BaseComponentProps {
  symbol: string
  name: string
  price: number
  change: number
  changePercent: number
  volume: number
  marketCap?: number
  peRatio?: number
  pbRatio?: number
  chart?: any[]
  timeframe?: string
  showChart?: boolean
  showIndicators?: boolean
  alert?: boolean
  onClick?: (stock: any) => void
  onAlert?: (stock: any) => void
}

// 策略卡片组件Props
export interface StrategyCardProps extends BaseComponentProps {
  id: string
  name: string
  description: string
  type: StrategyType
  status?: StrategyStatus
  performance?: {
    totalReturn?: number
    sharpeRatio?: number
    maxDrawdown?: number
    winRate?: number
  }
  tags?: string[]
  author?: string
  createdAt?: string
  updatedAt?: string
  onClick?: (strategy: any) => void
  onEdit?: (strategy: any) => void
  onDelete?: (strategy: any) => void
  onClone?: (strategy: any) => void
}

// 回测卡片组件Props
export interface BacktestCardProps extends Omit<BaseComponentProps, 'status'> {
  id: string
  name: string
  status?: BacktestStatus
  progress?: number
  startDate?: string
  endDate?: string
  initialCapital?: number
  finalCapital?: number
  totalReturn?: number
  sharpeRatio?: number
  maxDrawdown?: number
  winRate?: number
  createdAt?: string
  completedAt?: string
  onClick?: (backtest: any) => void
  onView?: (backtest: any) => void
  onDownload?: (backtest: any) => void
}

// AI助手卡片组件Props
export interface AIAssistantCardProps extends BaseComponentProps {
  messages: any[]
  loading?: boolean
  inputPlaceholder?: string
  showVoice?: boolean
  onSendMessage?: (message: string) => void
  onVoiceStart?: () => void
  onVoiceEnd?: () => void
}

// 监控面板组件Props
export interface MonitorPanelProps extends BaseComponentProps {
  stocks: any[]
  layout?: LayoutType
  autoRefresh?: boolean
  refreshInterval?: number
  showAlerts?: boolean
  showIndicators?: boolean
  timeframe?: string
  onStockSelect?: (stock: any) => void
  onAlert?: (alert: any) => void
  onRefresh?: () => void
}

// 预警规则组件Props
export interface AlertRuleCardProps extends BaseComponentProps {
  id: string
  name: string
  symbol: string
  indicator: string
  condition: string
  threshold: number
  comparison: 'greater_than' | 'less_than' | 'equal_to'
  enabled: boolean
  notificationSettings: {
    email: boolean
    sms: boolean
    webhook: boolean
  }
  createdAt?: string
  updatedAt?: string
  onEdit?: (rule: any) => void
  onDelete?: (rule: any) => void
  onToggle?: (rule: any) => void
  onTest?: (rule: any) => void
}

// 订单面板组件Props
export interface OrderPanelProps extends Omit<BaseComponentProps, 'status'> {
  orders: any[]
  symbols?: string[]
  status?: OrderStatus
  type?: OrderType
  direction?: TradeDirection
  showActions?: boolean
  onCancel?: (order: any) => void
  onModify?: (order: any) => void
  onView?: (order: any) => void
}

// 持仓面板组件Props
export interface PositionPanelProps extends BaseComponentProps {
  positions: any[]
  symbols?: string[]
  type?: PositionType
  showActions?: boolean
  showChart?: boolean
  onClose?: (position: any) => void
  onAdjust?: (position: any) => void
  onView?: (position: any) => void
}

// 风险仪表盘组件Props
export interface RiskGaugeProps extends BaseComponentProps {
  value: number
  min?: number
  max?: number
  thresholds?: Array<{
    value: number
    color: string
    label: string
  }>
  title?: string
  unit?: string
  format?: (value: number) => string
  onChange?: (value: number) => void
}

// 数据质量面板组件Props
export interface DataQualityPanelProps extends BaseComponentProps {
  metrics: {
    completeness: number
    accuracy: number
    consistency: number
    timeliness: number
    validity: number
    uniqueness: number
  }
  issues?: any[]
  lastUpdated?: string
  onRefresh?: () => void
  onViewDetails?: (metric: string) => void
}

// 性能监控面板组件Props
export interface PerformancePanelProps extends BaseComponentProps {
  metrics: {
    responseTime: number
    throughput: number
    errorRate: number
    availability: number
    cpuUsage: number
    memoryUsage: number
    diskIO: number
    networkIO: number
  }
  timeRange?: string
  autoRefresh?: boolean
  refreshInterval?: number
  onTimeRangeChange?: (range: string) => void
  onRefresh?: () => void
}
// 组件类型定义
import type { CSSProperties } from 'vue'

// 基础组件Props
export interface BaseComponentProps {
  size?: 'small' | 'medium' | 'large'
  disabled?: boolean
  loading?: boolean
  className?: string
  style?: CSSProperties
}

// 按钮组件Props
export interface ButtonProps extends BaseComponentProps {
  type?: 'primary' | 'secondary' | 'ghost' | 'danger' | 'warning' | 'success' | 'info'
  icon?: string
  round?: boolean
  circle?: boolean
  block?: boolean
  text?: boolean
  link?: boolean
  plain?: boolean
  hairline?: boolean
  color?: string
}

// 输入框组件Props
export interface InputProps extends BaseComponentProps {
  type?: 'text' | 'password' | 'textarea' | 'number' | 'email' | 'url' | 'tel'
  value?: string | number
  placeholder?: string
  clearable?: boolean
  readonly?: boolean
  maxlength?: number
  minlength?: number
  showWordLimit?: boolean
  prefixIcon?: string
  suffixIcon?: string
  rows?: number
  autosize?: boolean | { minRows?: number; maxRows?: number }
  resize?: 'none' | 'both' | 'horizontal' | 'vertical'
  autoFocus?: boolean
  format?: (value: string | number) => string
  parse?: (value: string) => string | number
  debounce?: number
  size?: 'small' | 'medium' | 'large'
}

// 选择器组件Props
export interface SelectProps extends BaseComponentProps {
  value?: string | number | Array<string | number>
  placeholder?: string
  clearable?: boolean
  multiple?: boolean
  filterable?: boolean
  remote?: boolean
  loading?: boolean
  remoteMethod?: (query: string) => void
  loadingText?: string
  noMatchText?: string
  noDataText?: string
  popperClass?: string
  reserveKeyword?: boolean
  defaultFirstOption?: boolean
  teleported?: boolean
  persistent?: boolean
  automaticDropdown?: boolean
  fitInputWidth?: boolean
  size?: 'small' | 'medium' | 'large'
}

// 选项组件Props
export interface OptionProps extends BaseComponentProps {
  value?: string | number | boolean | object
  label?: string
  disabled?: boolean
}

// 表格列定义
export interface TableColumn {
  key: string
  title: string
  dataIndex?: string
  width?: number
  minWidth?: number
  maxWidth?: number
  fixed?: boolean | 'left' | 'right'
  align?: 'left' | 'center' | 'right'
  sortable?: boolean
  filterable?: boolean
  filterMultiple?: boolean
  filterOptions?: Array<{ label: string; value: any }>
  render?: (value: any, record: any, index: number) => any
  children?: TableColumn[]
}

// 表格组件Props
export interface TableProps extends BaseComponentProps {
  data: any[]
  columns: TableColumn[]
  loading?: boolean
  bordered?: boolean
  striped?: boolean
  hoverable?: boolean
  size?: 'small' | 'medium' | 'large'
  showHeader?: boolean
  emptyText?: string
  pagination?: boolean | PaginationProps
  scroll?: { x?: number; y?: number }
  rowKey?: string | ((record: any) => string)
  rowClassName?: string | ((record: any, index: number) => string)
  rowSelection?: RowSelectionProps
  expandable?: ExpandableProps
  paginated?: boolean
  pageSize?: number
  total?: number
  currentPage?: number
}

// 分页组件Props
export interface PaginationProps extends BaseComponentProps {
  total: number
  pageSize?: number
  currentPage?: number
  pageSizes?: number[]
  layout?: string
  background?: boolean
  small?: boolean
  disabled?: boolean
  hideOnSinglePage?: boolean
}

// 行选择Props
export interface RowSelectionProps {
  type?: 'checkbox' | 'radio'
  selectedRowKeys?: (string | number)[]
  onChange?: (selectedRowKeys: (string | number)[], selectedRows: any[]) => void
  getCheckboxProps?: (record: any) => { disabled?: boolean }
  onSelect?: (record: any, selected: boolean, selectedRows: any[]) => void
  onSelectAll?: (selected: boolean, selectedRows: any[], changeRows: any[]) => void
  columnWidth?: string | number
  columnTitle?: string
  fixed?: boolean | 'left' | 'right'
}

// 可展开Props
export interface ExpandableProps {
  expandedRowKeys?: (string | number)[]
  defaultExpandedRowKeys?: (string | number)[]
  expandedRowRender?: (record: any, index: number, indent: number, expanded: boolean) => any
  expandRowByClick?: boolean
  expandIcon?: (props: any) => any
  columnWidth?: string | number
  rowExpandable?: (record: any) => boolean
  onExpand?: (expanded: boolean, record: any) => void
  onExpandedRowsChange?: (expandedRows: any[]) => void
}

// 模态框组件Props
export interface ModalProps extends BaseComponentProps {
  visible?: boolean
  title?: string
  width?: string | number
  height?: string | number
  closable?: boolean
  maskClosable?: boolean
  mask?: boolean
  zIndex?: number
  centered?: boolean
  footer?: boolean | string
  okText?: string
  cancelText?: string
  okType?: string
  confirmLoading?: boolean
  destroyOnClose?: boolean
  getContainer?: () => HTMLElement
  forceRender?: boolean
  afterClose?: () => void
  bodyStyle?: CSSProperties
  maskStyle?: CSSProperties
  wrapClassName?: string
}

// 表单组件Props
export interface FormProps extends BaseComponentProps {
  modelValue?: Record<string, any>
  rules?: Record<string, any>
  labelWidth?: string | number
  labelPosition?: 'left' | 'right' | 'top'
  labelSuffix?: string
  hideRequiredAsterisk?: boolean
  showMessage?: boolean
  inlineMessage?: boolean
  statusIcon?: boolean
  validateOnRuleChange?: boolean
  disabled?: boolean
  size?: 'small' | 'medium' | 'large'
  scrollToError?: boolean
  scrollToErrorOffset?: number
}

// 表单项组件Props
export interface FormItemProps extends BaseComponentProps {
  prop?: string
  label?: string
  labelWidth?: string | number
  required?: boolean
  rules?: any[]
  error?: string
  showMessage?: boolean
  inline?: boolean
  size?: 'small' | 'medium' | 'large'
}

// 卡片组件Props
export interface CardProps extends Omit<BaseComponentProps, 'size'> {
  title?: string
  subTitle?: string
  extra?: string
  avatar?: string
  bordered?: boolean
  hoverable?: boolean
  loading?: boolean
  size?: 'small' | 'default' | 'large'
  type?: 'inner'
  shadow?: 'always' | 'hover' | 'never'
  bodyStyle?: CSSProperties
}

// 加载组件Props
export interface LoadingProps extends BaseComponentProps {
  text?: string
  textColor?: string
  background?: string
  spinner?: string
  icon?: string
  iconSize?: number
  iconViewBox?: string
  fullscreen?: boolean
  lock?: boolean
  customClass?: string
  target?: string | HTMLElement
  body?: boolean
}

// 标签组件Props
export interface TagProps extends BaseComponentProps {
  type?: 'primary' | 'success' | 'info' | 'warning' | 'danger' | 'default'
  effect?: 'dark' | 'light' | 'plain'
  closable?: boolean
  color?: string
  size?: 'small' | 'medium' | 'large'
  hit?: boolean
}

// 策略模板类型
export interface StrategyTemplate {
  id: string
  name: string
  description: string
  icon: string
  code?: string
  config?: Record<string, any>
}

// 策略类型
export interface Strategy {
  id: string
  name: string
  description: string
  status: 'active' | 'inactive' | 'testing' | 'error'
  performance: number
  risk: 'low' | 'medium' | 'high'
  updatedAt: string
  code?: string
  config?: Record<string, any>
  backtestResult?: BacktestResult
}

// 回测结果类型
export interface BacktestResult {
  totalReturn: number
  annualReturn: number
  maxDrawdown: number
  sharpeRatio: number
  winRate: number
  profitLossRatio: number
  totalTrades: number
  startDate: string
  endDate: string
}
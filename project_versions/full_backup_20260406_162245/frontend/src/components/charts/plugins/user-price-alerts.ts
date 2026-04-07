import type {
  IChartApi,
  ISeriesApi,
  SeriesType,
  IPriceLine,
  PriceLineOptions,
} from 'lightweight-charts';
import { Delegate, type ISubscription } from './delegate';

export interface PriceAlert {
  id: string;
  price: number;
  title?: string;
  color?: string;
  lineWidth?: number;
  lineStyle?: number;
  axisLabelVisible?: boolean;
  enableAlert?: boolean;  // 是否启用提醒
}

export interface PriceAlertOptions {
  color: string;
  lineWidth: number;
  lineStyle: number;
  axisLabelVisible: boolean;
  title: string;
}

export class UserPriceAlerts {
  private _chart: IChartApi | null = null;
  private _series: ISeriesApi<SeriesType> | null = null;
  private _alerts: Map<string, PriceAlert & { line: IPriceLine }> = new Map();
  private _defaultOptions: PriceAlertOptions;

  // 事件委托
  private _alertAdded: Delegate<PriceAlert> = new Delegate();
  private _alertRemoved: Delegate<string> = new Delegate();
  private _alertTriggered: Delegate<PriceAlert> = new Delegate();

  constructor(defaultOptions?: Partial<PriceAlertOptions>) {
    this._defaultOptions = {
      color: '#2196F3',
      lineWidth: 1,
      lineStyle: 2, // dashed
      axisLabelVisible: false,  // 默认禁用右侧价格轴标签
      title: '',
      ...defaultOptions,
    };
  }

  /**
   * 附加到图表系列
   */
  attach(chart: IChartApi, series: ISeriesApi<SeriesType>): void {
    this._chart = chart;
    this._series = series;
  }

  /**
   * 分离插件
   */
  detach(): void {
    this.clearAll();
    this._chart = null;
    this._series = null;
  }

  /**
   * 添加价格提醒
   */
  addAlert(price: number, options?: Partial<PriceAlertOptions>): string {
    if (!this._series) {
      throw new Error('UserPriceAlerts not attached to series');
    }

    const id = this._generateId();
    const mergedOptions = { ...this._defaultOptions, ...options };

    // 创建价格线（禁用原生标签）
    const lineOptions: PriceLineOptions = {
      price: price,
      color: mergedOptions.color,
      lineWidth: mergedOptions.lineWidth,
      lineStyle: mergedOptions.lineStyle,
      axisLabelVisible: false,
      title: '',
    };

    const line = this._series.createPriceLine(lineOptions);

    const alert: PriceAlert & { line: IPriceLine } = {
      id,
      price,
      title: mergedOptions.title,
      color: mergedOptions.color,
      lineWidth: mergedOptions.lineWidth,
      lineStyle: mergedOptions.lineStyle,
      axisLabelVisible: mergedOptions.axisLabelVisible,
      enableAlert: true,  // 默认启用提醒
      line,
    };

    this._alerts.set(id, alert);
    this._alertAdded.fire({ ...alert, line: undefined as unknown as IPriceLine });

    return id;
  }

  /**
   * 删除价格提醒
   */
  removeAlert(id: string): boolean {
    const alert = this._alerts.get(id);
    if (!alert) return false;

    // 从系列中移除价格线
    if (this._series) {
      this._series.removePriceLine(alert.line);
    }

    this._alerts.delete(id);
    this._alertRemoved.fire(id);
    return true;
  }

  /**
   * 更新价格提醒
   */
  updateAlert(id: string, updates: Partial<PriceAlertOptions>): boolean {
    const alert = this._alerts.get(id);
    if (!alert) return false;

    // 先移除旧的价格线
    if (this._series) {
      this._series.removePriceLine(alert.line);
    }

    // 更新选项（强制禁用原生标签，只使用左侧自定义标签）
    const newOptions = {
      color: updates.color ?? alert.color ?? this._defaultOptions.color,
      lineWidth: updates.lineWidth ?? alert.lineWidth ?? this._defaultOptions.lineWidth,
      lineStyle: updates.lineStyle ?? alert.lineStyle ?? this._defaultOptions.lineStyle,
      axisLabelVisible: false,  // 强制禁用右侧价格轴原生标签
      title: updates.title ?? alert.title ?? this._defaultOptions.title,
    };

    // 创建新的价格线
    if (this._series) {
      const line = this._series.createPriceLine({
        price: alert.price,
        color: newOptions.color,
        lineWidth: newOptions.lineWidth,
        lineStyle: newOptions.lineStyle,
        axisLabelVisible: false,  // 强制禁用右侧价格轴原生标签
        title: '',  // 禁用内置标题
      });

      // 更新存储
      this._alerts.set(id, {
        ...alert,
        ...newOptions,
        line,
      });
    }

    return true;
  }

  /**
   * 更新价格提醒价格
   */
  updateAlertPrice(id: string, newPrice: number): boolean {
    const alert = this._alerts.get(id);
    if (!alert) return false;

    // 先移除旧的价格线
    if (this._series) {
      this._series.removePriceLine(alert.line);
    }

    // 创建新的价格线（禁用内置标签）
    if (this._series) {
      const line = this._series.createPriceLine({
        price: newPrice,
        color: alert.color ?? this._defaultOptions.color,
        lineWidth: alert.lineWidth ?? this._defaultOptions.lineWidth,
        lineStyle: alert.lineStyle ?? this._defaultOptions.lineStyle,
        axisLabelVisible: false,  // 禁用右侧价格轴标签
        title: '',  // 禁用内置标题
      });

      // 更新存储
      this._alerts.set(id, {
        ...alert,
        price: newPrice,
        title: alert.title || `${newPrice.toFixed(2)}`,
        line,
      });
    }

    return true;
  }

  /**
   * 获取所有价格提醒
   */
  getAlerts(): PriceAlert[] {
    return Array.from(this._alerts.values()).map(a => ({
      id: a.id,
      price: a.price,
      title: a.title,
      color: a.color,
      lineWidth: a.lineWidth,
      lineStyle: a.lineStyle,
      axisLabelVisible: a.axisLabelVisible,
      enableAlert: a.enableAlert ?? true,  // 默认启用提醒
    }));
  }

  /**
   * 清空所有价格提醒
   */
  clearAll(): void {
    for (const [id, alert] of this._alerts) {
      if (this._series) {
        this._series.removePriceLine(alert.line);
      }
    }
    this._alerts.clear();
  }

  /**
   * 设置默认选项
   */
  setDefaultOptions(options: Partial<PriceAlertOptions>): void {
    this._defaultOptions = { ...this._defaultOptions, ...options };
  }

  /**
   * 事件订阅
   */
  get alertAdded(): ISubscription<PriceAlert> {
    return this._alertAdded;
  }

  get alertRemoved(): ISubscription<string> {
    return this._alertRemoved;
  }

  get alertTriggered(): ISubscription<PriceAlert> {
    return this._alertTriggered;
  }

  /**
   * 从 localStorage 加载提醒
   */
  loadFromStorage(symbol: string): void {
    try {
      const key = `price_alerts_${symbol}`;
      const data = localStorage.getItem(key);
      if (data) {
        const alerts: PriceAlert[] = JSON.parse(data);
        alerts.forEach(alert => {
          this.addAlert(alert.price, {
            color: alert.color,
            lineWidth: alert.lineWidth,
            lineStyle: alert.lineStyle,
            axisLabelVisible: alert.axisLabelVisible,
            title: alert.title,
          });
        });
      }
    } catch (e) {
      console.error('[UserPriceAlerts] Failed to load from storage:', e);
    }
  }

  /**
   * 保存提醒到 localStorage
   */
  saveToStorage(symbol: string): void {
    try {
      const key = `price_alerts_${symbol}`;
      const alerts = this.getAlerts();
      localStorage.setItem(key, JSON.stringify(alerts));
    } catch (e) {
      console.error('[UserPriceAlerts] Failed to save to storage:', e);
    }
  }

  /**
   * 生成唯一ID
   */
  private _generateId(): string {
    return `alert_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }
}

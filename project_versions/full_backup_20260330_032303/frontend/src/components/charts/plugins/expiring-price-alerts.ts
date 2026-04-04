import type {
  IChartApi,
  ISeriesApi,
  SeriesType,
  IPriceLine,
  PriceLineOptions,
  UTCTimestamp,
} from 'lightweight-charts';
import { Delegate, type ISubscription } from './delegate';

export interface ExpiringPriceAlert {
  id: string;
  price: number;
  startTime: number; // UTC timestamp
  endTime: number;   // UTC timestamp
  title?: string;
  color?: string;
  lineWidth?: number;
  lineStyle?: number;
  axisLabelVisible?: boolean;
  crossed?: boolean;
  expired?: boolean;
}

export interface ExpiringAlertOptions {
  color: string;
  lineWidth: number;
  lineStyle: number;
  axisLabelVisible: boolean;
  title: string;
  clearTimeout: number; // 触发/过期后多久清除(ms)
}

export class ExpiringPriceAlerts {
  private _chart: IChartApi | null = null;
  private _series: ISeriesApi<SeriesType> | null = null;
  private _alerts: Map<string, ExpiringPriceAlert & { line: IPriceLine | null }> = new Map();
  private _defaultOptions: ExpiringAlertOptions;
  private _checkInterval: number | null = null;
  private _lastValue: number | null = null;

  // 事件委托
  private _alertAdded: Delegate<ExpiringPriceAlert> = new Delegate();
  private _alertRemoved: Delegate<string> = new Delegate();
  private _alertCrossed: Delegate<ExpiringPriceAlert> = new Delegate();
  private _alertExpired: Delegate<ExpiringPriceAlert> = new Delegate();

  constructor(defaultOptions?: Partial<ExpiringAlertOptions>) {
    this._defaultOptions = {
      color: '#FF9800',
      lineWidth: 1,
      lineStyle: 2, // dashed
      axisLabelVisible: true,
      title: '',
      clearTimeout: 5000, // 5秒后自动清除
      ...defaultOptions,
    };
  }

  /**
   * 附加到图表系列
   */
  attach(chart: IChartApi, series: ISeriesApi<SeriesType>): void {
    this._chart = chart;
    this._series = series;
    this._startChecking();
  }

  /**
   * 分离插件
   */
  detach(): void {
    this._stopChecking();
    this.clearAll();
    this._chart = null;
    this._series = null;
  }

  /**
   * 添加过期价格提醒
   * @param price 目标价格
   * @param startTime 开始时间 (UTC timestamp)
   * @param endTime 结束时间 (UTC timestamp)
   * @param options 其他选项
   */
  addAlert(
    price: number,
    startTime: number,
    endTime: number,
    options?: Partial<ExpiringAlertOptions>
  ): string {
    if (!this._series) {
      throw new Error('ExpiringPriceAlerts not attached to series');
    }

    const id = this._generateId();
    const mergedOptions = { ...this._defaultOptions, ...options };

    // 检查是否在当前有效时间内
    const now = Date.now() / 1000;
    const isActive = now >= startTime && now <= endTime;

    let line: IPriceLine | null = null;

    if (isActive) {
      // 创建价格线
      const lineOptions: PriceLineOptions = {
        price: price,
        color: mergedOptions.color,
        lineWidth: mergedOptions.lineWidth,
        lineStyle: mergedOptions.lineStyle,
        axisLabelVisible: mergedOptions.axisLabelVisible,
        title: mergedOptions.title || `${price.toFixed(2)}`,
      };
      line = this._series.createPriceLine(lineOptions);
    }

    const alert: ExpiringPriceAlert & { line: IPriceLine | null } = {
      id,
      price,
      startTime,
      endTime,
      title: mergedOptions.title,
      color: mergedOptions.color,
      lineWidth: mergedOptions.lineWidth,
      lineStyle: mergedOptions.lineStyle,
      axisLabelVisible: mergedOptions.axisLabelVisible,
      crossed: false,
      expired: now > endTime,
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
    if (alert.line && this._series) {
      this._series.removePriceLine(alert.line);
    }

    this._alerts.delete(id);
    this._alertRemoved.fire(id);
    return true;
  }

  /**
   * 获取所有价格提醒
   */
  getAlerts(): ExpiringPriceAlert[] {
    return Array.from(this._alerts.values()).map(a => ({
      id: a.id,
      price: a.price,
      startTime: a.startTime,
      endTime: a.endTime,
      title: a.title,
      color: a.color,
      lineWidth: a.lineWidth,
      lineStyle: a.lineStyle,
      axisLabelVisible: a.axisLabelVisible,
      crossed: a.crossed,
      expired: a.expired,
    }));
  }

  /**
   * 获取活跃的价格提醒
   */
  getActiveAlerts(): ExpiringPriceAlert[] {
    const now = Date.now() / 1000;
    return this.getAlerts().filter(a => !a.expired && now >= a.startTime && now <= a.endTime);
  }

  /**
   * 清空所有价格提醒
   */
  clearAll(): void {
    for (const [id, alert] of this._alerts) {
      if (alert.line && this._series) {
        this._series.removePriceLine(alert.line);
      }
    }
    this._alerts.clear();
  }

  /**
   * 清空已过期的提醒
   */
  clearExpired(): void {
    const now = Date.now() / 1000;
    for (const [id, alert] of this._alerts) {
      if (alert.expired || now > alert.endTime) {
        this.removeAlert(id);
      }
    }
  }

  /**
   * 设置默认选项
   */
  setDefaultOptions(options: Partial<ExpiringAlertOptions>): void {
    this._defaultOptions = { ...this._defaultOptions, ...options };
  }

  /**
   * 事件订阅
   */
  get alertAdded(): ISubscription<ExpiringPriceAlert> {
    return this._alertAdded;
  }

  get alertRemoved(): ISubscription<string> {
    return this._alertRemoved;
  }

  get alertCrossed(): ISubscription<ExpiringPriceAlert> {
    return this._alertCrossed;
  }

  get alertExpired(): ISubscription<ExpiringPriceAlert> {
    return this._alertExpired;
  }

  /**
   * 开始检查价格穿越和过期
   */
  private _startChecking(): void {
    if (this._checkInterval) return;
    this._checkInterval = window.setInterval(() => {
      this._checkAlerts();
    }, 1000); // 每秒检查一次
  }

  /**
   * 停止检查
   */
  private _stopChecking(): void {
    if (this._checkInterval) {
      clearInterval(this._checkInterval);
      this._checkInterval = null;
    }
  }

  /**
   * 检查所有提醒
   */
  private _checkAlerts(): void {
    if (!this._series) return;

    const now = Date.now() / 1000;

    // 获取最新价格
    const data = this._series.data();
    if (data.length === 0) return;

    const lastPoint = data[data.length - 1] as { value?: number; close?: number; time: UTCTimestamp };
    const currentValue = lastPoint.value ?? lastPoint.close ?? null;
    if (currentValue === null) return;

    for (const [id, alert] of this._alerts) {
      // 检查是否过期
      if (!alert.expired && now > alert.endTime) {
        alert.expired = true;
        this._alertExpired.fire({ ...alert, line: undefined as unknown as IPriceLine });

        // 延迟清除
        setTimeout(() => {
          this.removeAlert(id);
        }, this._defaultOptions.clearTimeout);
        continue;
      }

      // 检查是否开始
      if (!alert.line && now >= alert.startTime && now <= alert.endTime) {
        // 创建价格线
        const lineOptions: PriceLineOptions = {
          price: alert.price,
          color: alert.color ?? this._defaultOptions.color,
          lineWidth: alert.lineWidth ?? this._defaultOptions.lineWidth,
          lineStyle: alert.lineStyle ?? this._defaultOptions.lineStyle,
          axisLabelVisible: alert.axisLabelVisible ?? this._defaultOptions.axisLabelVisible,
          title: alert.title || `${alert.price.toFixed(2)}`,
        };
        alert.line = this._series.createPriceLine(lineOptions);
      }

      // 检查价格穿越
      if (!alert.crossed && alert.line && this._lastValue !== null) {
        const crossedUp = this._lastValue <= alert.price && currentValue > alert.price;
        const crossedDown = this._lastValue >= alert.price && currentValue < alert.price;

        if (crossedUp || crossedDown) {
          alert.crossed = true;
          this._alertCrossed.fire({ ...alert, line: undefined as unknown as IPriceLine });

          // 延迟清除
          setTimeout(() => {
            this.removeAlert(id);
          }, this._defaultOptions.clearTimeout);
        }
      }
    }

    this._lastValue = currentValue;
  }

  /**
   * 生成唯一ID
   */
  private _generateId(): string {
    return `exp_alert_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }
}

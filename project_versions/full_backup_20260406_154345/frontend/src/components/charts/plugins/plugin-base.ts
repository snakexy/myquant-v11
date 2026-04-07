import type { IChartApi, ISeriesApi, SeriesType } from 'lightweight-charts';

/**
 * Lightweight Charts 插件基类
 * 提供图表和系列引用管理，以及数据更新订阅
 */
export abstract class PluginBase {
  private _chart: IChartApi | undefined = undefined;
  private _series: ISeriesApi<SeriesType> | undefined = undefined;

  protected requestUpdate(): void {
    if (this._requestUpdate) this._requestUpdate();
  }

  private _requestUpdate?: () => void;

  public attached({ chart, series, requestUpdate }: { chart: IChartApi; series: ISeriesApi<SeriesType>; requestUpdate: () => void }) {
    this._chart = chart;
    this._series = series;
    this._requestUpdate = requestUpdate;
    this.requestUpdate();
  }

  public detached() {
    this._chart = undefined;
    this._series = undefined;
    this._requestUpdate = undefined;
  }

  public get chart(): IChartApi {
    if (!this._chart) {
      throw new Error('Chart not attached');
    }
    return this._chart;
  }

  public get series(): ISeriesApi<SeriesType> {
    if (!this._series) {
      throw new Error('Series not attached');
    }
    return this._series;
  }
}

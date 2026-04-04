import { DeepPartial } from '../helpers/strict-type-checks';
import { LineData, WhitespaceData } from '../model/data-consumer';
import { SeriesPartialOptionsMap, SeriesType } from '../model/series-options';
import { SeriesDefinition } from '../model/series/series-def';
import { YieldCurveChartOptions } from '../model/yield-curve-horz-scale-behavior/yield-curve-chart-options';
import { ChartApi } from './chart-api';
import { ISeriesApi } from './iseries-api';
import { IYieldCurveChartApi } from './iyield-chart-api';
export declare class YieldChartApi extends ChartApi<number> implements IYieldCurveChartApi {
    constructor(container: HTMLElement, options?: DeepPartial<YieldCurveChartOptions>);
    addSeries<T extends SeriesType>(definition: SeriesDefinition<T>, options?: SeriesPartialOptionsMap[T], paneIndex?: number): ISeriesApi<T, number, WhitespaceData<number> | LineData<number>>;
    private _initWhitespaceSeries;
}

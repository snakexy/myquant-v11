import { IChartWidgetBase } from '../gui/chart-widget';
import { DeepPartial } from '../helpers/strict-type-checks';
import { PriceScaleOptions } from '../model/price-scale';
import { IRange } from '../model/time-data';
import { IPriceScaleApi } from './iprice-scale-api';
export declare class PriceScaleApi implements IPriceScaleApi {
    private _chartWidget;
    private readonly _priceScaleId;
    private readonly _paneIndex;
    constructor(chartWidget: IChartWidgetBase, priceScaleId: string, paneIndex?: number);
    applyOptions(options: DeepPartial<PriceScaleOptions>): void;
    options(): Readonly<PriceScaleOptions>;
    width(): number;
    setVisibleRange(range: IRange<number>): void;
    getVisibleRange(): IRange<number> | null;
    setAutoScale(on: boolean): void;
    private _priceScale;
}

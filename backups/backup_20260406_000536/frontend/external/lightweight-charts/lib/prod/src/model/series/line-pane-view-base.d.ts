import { IPaneRenderer } from '../../renderers/ipane-renderer';
import { BarPrice } from '../bar';
import { IChartModelBase } from '../chart-model';
import { ISeries } from '../iseries';
import { PricedValue, PriceScale } from '../price-scale';
import { ISeriesBarColorer } from '../series-bar-colorer';
import { TimedValue, TimePointIndex } from '../time-data';
import { ITimeScale } from '../time-scale';
import { SeriesPaneViewBase } from './series-pane-view-base';
export declare abstract class LinePaneViewBase<TSeriesType extends 'Line' | 'Area' | 'Baseline' | 'Histogram', ItemType extends PricedValue & TimedValue, TRenderer extends IPaneRenderer> extends SeriesPaneViewBase<TSeriesType, ItemType, TRenderer> {
    constructor(series: ISeries<TSeriesType>, model: IChartModelBase);
    protected _convertToCoordinates(priceScale: PriceScale, timeScale: ITimeScale, firstValue: number): void;
    protected abstract _createRawItem(time: TimePointIndex, price: BarPrice, colorer: ISeriesBarColorer<TSeriesType>): ItemType;
    protected _createRawItemBase(time: TimePointIndex, price: BarPrice): PricedValue & TimedValue;
    protected _fillRawPoints(): void;
}

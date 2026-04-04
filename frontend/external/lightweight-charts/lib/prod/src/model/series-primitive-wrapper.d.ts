import { IPaneView } from '../views/pane/ipane-view';
import { IPriceAxisView } from '../views/price-axis/iprice-axis-view';
import { ITimeAxisView } from '../views/time-axis/itime-axis-view';
import { PrimitivePaneViewZOrder } from './ipane-primitive';
import { ISeriesPrimitiveBase } from './iseries-primitive';
import { PrimitiveWrapper } from './pane-primitive-wrapper';
import { Series } from './series';
import { AutoscaleInfo, SeriesType } from './series-options';
import { TimePointIndex } from './time-data';
export interface ISeriesPrimitivePaneViewWrapper extends IPaneView {
    zOrder(): PrimitivePaneViewZOrder;
}
export declare class SeriesPrimitiveWrapper<TSeriesAttachedParameters = unknown> extends PrimitiveWrapper<ISeriesPrimitiveBase<TSeriesAttachedParameters>> {
    private readonly _series;
    private _timeAxisViewsCache;
    private _priceAxisViewsCache;
    private _priceAxisPaneViewsCache;
    private _timeAxisPaneViewsCache;
    constructor(primitive: ISeriesPrimitiveBase<TSeriesAttachedParameters>, series: Series<SeriesType>);
    timeAxisViews(): readonly ITimeAxisView[];
    priceAxisViews(): readonly IPriceAxisView[];
    priceAxisPaneViews(): readonly ISeriesPrimitivePaneViewWrapper[];
    timeAxisPaneViews(): readonly ISeriesPrimitivePaneViewWrapper[];
    autoscaleInfo(startTimePoint: TimePointIndex, endTimePoint: TimePointIndex): AutoscaleInfo | null;
}

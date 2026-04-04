import { IPriceFormatter } from '../formatters/iprice-formatter';
import { IDestroyable } from '../helpers/idestroyable';
import { IPaneView } from '../views/pane/ipane-view';
import { IUpdatablePaneView } from '../views/pane/iupdatable-pane-view';
import { IPriceAxisView } from '../views/price-axis/iprice-axis-view';
import { ITimeAxisView } from '../views/time-axis/itime-axis-view';
import { AutoscaleInfoImpl } from './autoscale-info-impl';
import { IChartModelBase } from './chart-model';
import { Coordinate } from './coordinate';
import { CustomPriceLine } from './custom-price-line';
import { CustomConflationReducer, CustomData, CustomSeriesWhitespaceData, ICustomSeriesPaneView, WhitespaceCheck } from './icustom-series';
import { PrimitiveHoveredItem, PrimitivePaneViewZOrder } from './ipane-primitive';
import { FirstValue } from './iprice-data-source';
import { ISeries, LastValueDataInternalResult, MarkerData, SeriesDataAtTypeMap } from './iseries';
import { ISeriesPrimitiveBase } from './iseries-primitive';
import { Pane } from './pane';
import { PriceDataSource } from './price-data-source';
import { PriceLineOptions } from './price-line-options';
import { PriceScale } from './price-scale';
import { SeriesBarColorer } from './series-bar-colorer';
import { SeriesPlotList, SeriesPlotRow } from './series-data';
import { SeriesOptionsMap, SeriesPartialOptionsMap, SeriesType } from './series-options';
import { ISeriesCustomPaneView } from './series/pane-view';
import { TimePointIndex } from './time-data';
type CustomDataToPlotRowValueConverter<HorzScaleItem> = (item: CustomData<HorzScaleItem> | CustomSeriesWhitespaceData<HorzScaleItem>) => number[];
export interface SeriesUpdateInfo {
    lastBarUpdatedOrNewBarsAddedToTheRight: boolean;
    historicalUpdate: boolean;
}
export type SeriesOptionsInternal<T extends SeriesType = SeriesType> = SeriesOptionsMap[T];
export type SeriesPartialOptionsInternal<T extends SeriesType = SeriesType> = SeriesPartialOptionsMap[T];
export declare class Series<T extends SeriesType> extends PriceDataSource implements IDestroyable, ISeries<SeriesType> {
    private readonly _seriesType;
    private _data;
    private readonly _priceAxisViews;
    private readonly _panePriceAxisView;
    private _formatter;
    private readonly _priceLineView;
    private readonly _customPriceLines;
    private readonly _baseHorizontalLineView;
    private _paneView;
    private readonly _lastPriceAnimationPaneView;
    private _barColorerCache;
    private readonly _options;
    private _animationTimeoutId;
    private _primitives;
    private readonly _dataConflater;
    private readonly _conflationByFactorCache;
    private _customConflationReducer;
    constructor(model: IChartModelBase, seriesType: T, options: SeriesOptionsInternal<T>, createPaneView: (series: ISeries<T>, model: IChartModelBase, customPaneView?: ICustomSeriesPaneView<unknown>) => IUpdatablePaneView | ISeriesCustomPaneView, customPaneView?: ICustomSeriesPaneView<unknown>);
    destroy(): void;
    priceLineColor(lastBarColor: string): string;
    lastValueData(globalLast: boolean): LastValueDataInternalResult;
    barColorer(): SeriesBarColorer<T>;
    options(): Readonly<SeriesOptionsMap[T]>;
    applyOptions(options: SeriesPartialOptionsInternal<T>): void;
    setData(data: readonly SeriesPlotRow<T>[], updateInfo?: SeriesUpdateInfo): void;
    createPriceLine(options: PriceLineOptions): CustomPriceLine;
    removePriceLine(line: CustomPriceLine): void;
    priceLines(): CustomPriceLine[];
    seriesType(): T;
    firstValue(): FirstValue | null;
    firstBar(): SeriesPlotRow<T> | null;
    bars(): SeriesPlotList<T>;
    setCustomConflationReducer(reducer: CustomConflationReducer<unknown>): void;
    /**
     * Check if conflation is currently enabled for this series.
     */
    isConflationEnabled(): boolean;
    /**
     * Efficiently update conflation when only the last data point changes.
     * This avoids rebuilding all conflated chunks.
     */
    updateLastConflatedChunk(newLastRow: SeriesPlotRow<T>): void;
    conflatedBars(): SeriesPlotList<T>;
    dataAt(time: TimePointIndex): SeriesDataAtTypeMap[SeriesType] | null;
    topPaneViews(pane: Pane): readonly IPaneView[];
    paneViews(): readonly IPaneView[];
    bottomPaneViews(): readonly IPaneView[];
    pricePaneViews(zOrder: PrimitivePaneViewZOrder): readonly IPaneView[];
    timePaneViews(zOrder: PrimitivePaneViewZOrder): readonly IPaneView[];
    primitiveHitTest(x: Coordinate, y: Coordinate): PrimitiveHoveredItem[];
    labelPaneViews(): readonly IPaneView[];
    priceAxisViews(pane: Pane, priceScale: PriceScale): readonly IPriceAxisView[];
    timeAxisViews(): readonly ITimeAxisView[];
    autoscaleInfo(startTimePoint: TimePointIndex, endTimePoint: TimePointIndex): AutoscaleInfoImpl | null;
    base(): number;
    formatter(): IPriceFormatter;
    updateAllViews(): void;
    priceScale(): PriceScale;
    markerDataAtIndex(index: TimePointIndex): MarkerData | null;
    title(): string;
    visible(): boolean;
    attachPrimitive(primitive: ISeriesPrimitiveBase): void;
    detachPrimitive(source: ISeriesPrimitiveBase): void;
    customSeriesPlotValuesBuilder(): CustomDataToPlotRowValueConverter<unknown> | undefined;
    customSeriesWhitespaceCheck<HorzScaleItem>(): WhitespaceCheck<HorzScaleItem> | undefined;
    fulfilledIndices(): readonly TimePointIndex[];
    private _isOverlay;
    private _autoscaleInfoImpl;
    private _markerRadius;
    private _markerBorderColor;
    private _markerBorderWidth;
    private _markerBackgroundColor;
    private _recreateFormatter;
    private _extractPaneViews;
    private _calculateConflationFactor;
    private _getConflationParams;
    private _buildConflatedListByFactor;
    private _regenerateConflatedDataByFactor;
    private _precomputeConflationLevels;
    private _precomputeConflationLevel;
}
export {};

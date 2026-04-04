import { IPriceFormatter } from '../formatters/iprice-formatter';
import { ISubscription } from '../helpers/isubscription';
import { DeepPartial } from '../helpers/strict-type-checks';
import { BarCoordinates, BarPrice, BarPrices } from './bar';
import { ColorParser } from './colors';
import { Coordinate } from './coordinate';
import { IPriceDataSource } from './iprice-data-source';
import { LayoutOptions } from './layout-options';
import { LocalizationOptionsBase } from './localization-options';
import { PriceRangeImpl } from './price-range-impl';
import { LogFormula } from './price-scale-conversions';
import { RangeImpl } from './range-impl';
import { SeriesItemsIndexesRange, TimePointIndex } from './time-data';
/**
 * Represents the price scale mode.
 */
export declare const enum PriceScaleMode {
    /**
     * Price scale shows prices. Price range changes linearly.
     */
    Normal = 0,
    /**
     * Price scale shows prices. Price range changes logarithmically.
     */
    Logarithmic = 1,
    /**
     * Price scale shows percentage values according the first visible value of the price scale.
     * The first visible value is 0% in this mode.
     */
    Percentage = 2,
    /**
     * The same as percentage mode, but the first value is moved to 100.
     */
    IndexedTo100 = 3
}
export interface PriceScaleState {
    autoScale: boolean;
    isInverted: boolean;
    mode: PriceScaleMode;
}
export interface PriceMark {
    coord: Coordinate;
    label: string;
    logical: number;
}
export interface PricedValue {
    price: BarPrice;
    y: Coordinate;
}
/** Defines margins of the price scale. */
export interface PriceScaleMargins {
    /**
     * Top margin in percentages. Must be greater or equal to 0 and less than 1.
     */
    top: number;
    /**
     * Bottom margin in percentages. Must be greater or equal to 0 and less than 1.
     */
    bottom: number;
}
/** Structure that describes price scale options */
export interface PriceScaleOptions {
    /**
     * Autoscaling is a feature that automatically adjusts a price scale to fit the visible range of data.
     * Note that overlay price scales are always auto-scaled.
     *
     * @defaultValue `true`
     */
    autoScale: boolean;
    /**
     * Price scale mode.
     *
     * @defaultValue {@link PriceScaleMode.Normal}
     */
    mode: PriceScaleMode;
    /**
     * Invert the price scale, so that a upwards trend is shown as a downwards trend and vice versa.
     * Affects both the price scale and the data on the chart.
     *
     * @defaultValue `false`
     */
    invertScale: boolean;
    /**
     * Align price scale labels to prevent them from overlapping.
     *
     * @defaultValue `true`
     */
    alignLabels: boolean;
    /**
     * Price scale margins.
     *
     * @defaultValue `{ bottom: 0.1, top: 0.2 }`
     * @example
     * ```js
     * chart.priceScale('right').applyOptions({
     *     scaleMargins: {
     *         top: 0.8,
     *         bottom: 0,
     *     },
     * });
     * ```
     */
    scaleMargins: PriceScaleMargins;
    /**
     * Set true to draw a border between the price scale and the chart area.
     *
     * @defaultValue `true`
     */
    borderVisible: boolean;
    /**
     * Price scale border color.
     *
     * @defaultValue `'#2B2B43'`
     */
    borderColor: string;
    /**
     * Price scale text color.
     * If not provided {@link LayoutOptions.textColor} is used.
     *
     * @defaultValue `undefined`
     */
    textColor?: string;
    /**
     * Show top and bottom corner labels only if entire text is visible.
     *
     * @defaultValue `false`
     */
    entireTextOnly: boolean;
    /**
     * Indicates if this price scale visible. Ignored by overlay price scales.
     *
     * @defaultValue `true` for the right price scale and `false` for the left.
     * For the yield curve chart, the default is for the left scale to be visible.
     */
    visible: boolean;
    /**
     * Draw small horizontal line on price axis labels.
     *
     * @defaultValue `false`
     */
    ticksVisible: boolean;
    /**
     * Define a minimum width for the price scale.
     * Note: This value will be exceeded if the
     * price scale needs more space to display it's contents.
     *
     * Setting a minimum width could be useful for ensuring that
     * multiple charts positioned in a vertical stack each have
     * an identical price scale width, or for plugins which
     * require a bit more space within the price scale pane.
     *
     * @defaultValue 0
     */
    minimumWidth: number;
    /**
     * Ensures that tick marks are always visible at the very top and bottom of the price scale,
     * regardless of the data range. When enabled, a tick mark will be drawn at both edges of the scale,
     * providing clear boundary indicators.
     *
     * @defaultValue false
     */
    ensureEdgeTickMarksVisible: boolean;
    /**
     * Tick mark label density on the price scale.
     * A higher value results in more spacing between tick marks, and thus fewer tick marks.
     * A lower value results in less spacing and more tick marks.
     *
     * @defaultValue `2.5`
     */
    tickMarkDensity: number;
}
export declare class PriceScale {
    private readonly _id;
    private readonly _layoutOptions;
    private readonly _localizationOptions;
    private readonly _options;
    private _height;
    private _internalHeightCache;
    private _priceRange;
    private _priceRangeSnapshot;
    private _invalidatedForRange;
    private _isCustomPriceRange;
    private _marginAbove;
    private _marginBelow;
    private _markBuilder;
    private _onMarksChanged;
    private _modeChanged;
    private _dataSources;
    private _formatterSource;
    private _cachedOrderedSources;
    private _marksCache;
    private _scaleStartPoint;
    private _scrollStartPoint;
    private _formatter;
    private _logFormula;
    private _colorParser;
    constructor(id: string, options: PriceScaleOptions, layoutOptions: LayoutOptions, localizationOptions: LocalizationOptionsBase, colorParser: ColorParser);
    id(): string;
    options(): Readonly<PriceScaleOptions>;
    applyOptions(options: DeepPartial<PriceScaleOptions>): void;
    isAutoScale(): boolean;
    isCustomPriceRange(): boolean;
    isLog(): boolean;
    isPercentage(): boolean;
    isIndexedTo100(): boolean;
    getLogFormula(): LogFormula;
    mode(): PriceScaleState;
    setMode(newMode: Partial<PriceScaleState>): void;
    modeChanged(): ISubscription<PriceScaleState, PriceScaleState>;
    fontSize(): number;
    height(): number;
    setHeight(value: number): void;
    internalHeight(): number;
    priceRange(): PriceRangeImpl | null;
    setPriceRange(newPriceRange: PriceRangeImpl | null, isForceSetValue?: boolean): void;
    setCustomPriceRange(newPriceRange: PriceRangeImpl | null): void;
    isEmpty(): boolean;
    invertedCoordinate(coordinate: number): number;
    priceToCoordinate(price: number, baseValue: number): Coordinate;
    pointsArrayToCoordinates<T extends PricedValue>(points: T[], baseValue: number, visibleRange?: SeriesItemsIndexesRange): void;
    barPricesToCoordinates<T extends BarPrices & BarCoordinates>(pricesList: T[], baseValue: number, visibleRange?: SeriesItemsIndexesRange): void;
    coordinateToPrice(coordinate: Coordinate, baseValue: number): BarPrice;
    logicalToPrice(logical: number, baseValue: number): BarPrice;
    dataSources(): readonly IPriceDataSource[];
    orderedSources(): readonly IPriceDataSource[];
    addDataSource(source: IPriceDataSource): void;
    removeDataSource(source: IPriceDataSource): void;
    firstValue(): number | null;
    isInverted(): boolean;
    marks(): PriceMark[];
    onMarksChanged(): ISubscription;
    startScale(x: number): void;
    scaleTo(x: number): void;
    endScale(): void;
    startScroll(x: number): void;
    scrollTo(x: number): void;
    endScroll(): void;
    formatter(): IPriceFormatter;
    formatPrice(price: number, firstValue: number): string;
    formatLogical(logical: number): string;
    formatLogicalTickmarks(logicals: readonly number[]): string[];
    formatPriceAbsolute(price: number): string;
    formatPricePercentage(price: number, baseValue: number): string;
    sourcesForAutoScale(): readonly IPriceDataSource[];
    recalculatePriceRange(visibleBars: RangeImpl<TimePointIndex>): void;
    updateAllViews(): void;
    hasVisibleEdgeMarks(): boolean;
    getEdgeMarksPadding(): number;
    updateFormatter(): void;
    invalidateSourcesCache(): void;
    minMove(): number;
    colorParser(): ColorParser;
    private _toggleCustomPriceRange;
    private _topMarginPx;
    private _bottomMarginPx;
    private _makeSureItIsValid;
    private _invalidateInternalHeightCache;
    private _logicalToCoordinate;
    private _coordinateToLogical;
    private _onIsInvertedChanged;
    private _recalculatePriceRangeImpl;
    private _getCoordinateTransformer;
    private _formatValue;
    private _formatValues;
    private _formatPrice;
    private _formatTickmarks;
    private _formatPercentage;
    private _formatPercentageTickmarks;
}

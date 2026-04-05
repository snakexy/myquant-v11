import { CanvasRenderingTarget2D } from 'fancy-canvas';
import { IPaneRenderer } from '../../renderers/ipane-renderer';
import { IChartModelBase } from '../chart-model';
import { CustomConflationContext, CustomData, CustomSeriesPricePlotValues, CustomSeriesWhitespaceData, ICustomSeriesPaneRenderer, ICustomSeriesPaneView, PriceToCoordinateConverter } from '../icustom-series';
import { ISeries } from '../iseries';
import { PriceScale } from '../price-scale';
import { SeriesOptionsMap } from '../series-options';
import { TimedValue } from '../time-data';
import { ITimeScale } from '../time-scale';
import { ISeriesCustomPaneView } from './pane-view';
import { SeriesPaneViewBase } from './series-pane-view-base';
type CustomBarItemBase = TimedValue;
interface CustomBarItem extends CustomBarItemBase {
    barColor: string;
    originalData?: Record<string, unknown>;
}
declare class CustomSeriesPaneRendererWrapper implements IPaneRenderer {
    private _sourceRenderer;
    private _priceScale;
    constructor(sourceRenderer: ICustomSeriesPaneRenderer, priceScale: PriceToCoordinateConverter);
    draw(target: CanvasRenderingTarget2D, isHovered: boolean, hitTestData?: unknown): void;
}
export declare class SeriesCustomPaneView extends SeriesPaneViewBase<'Custom' & keyof SeriesOptionsMap, CustomBarItem, CustomSeriesPaneRendererWrapper> implements ISeriesCustomPaneView {
    protected readonly _renderer: CustomSeriesPaneRendererWrapper;
    private readonly _paneView;
    constructor(series: ISeries<'Custom' & keyof SeriesOptionsMap>, model: IChartModelBase, paneView: ICustomSeriesPaneView<unknown>);
    get conflationReducer(): ((item1: CustomConflationContext<unknown, CustomData<unknown>>, item2: CustomConflationContext<unknown, CustomData<unknown>>) => CustomData<unknown>) | undefined;
    priceValueBuilder(plotRow: CustomData<unknown> | CustomSeriesWhitespaceData<unknown>): CustomSeriesPricePlotValues;
    isWhitespace(data: CustomData<unknown> | CustomSeriesWhitespaceData<unknown>): data is CustomSeriesWhitespaceData<unknown>;
    protected _fillRawPoints(): void;
    protected _convertToCoordinates(priceScale: PriceScale, timeScale: ITimeScale): void;
    protected _prepareRendererData(): void;
}
export {};

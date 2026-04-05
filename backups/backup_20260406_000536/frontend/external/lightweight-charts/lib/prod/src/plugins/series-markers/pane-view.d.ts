import { IChartApiBase } from '../../api/ichart-api';
import { ISeriesApi } from '../../api/iseries-api';
import { IPrimitivePaneView, PrimitivePaneViewZOrder } from '../../model/ipane-primitive';
import { SeriesType } from '../../model/series-options';
import { TimePointIndex } from '../../model/time-data';
import { UpdateType } from '../../views/pane/iupdatable-pane-view';
import { SeriesMarkersOptions } from './options';
import { SeriesMarkersRenderer } from './renderer';
import { InternalSeriesMarker } from './types';
export declare class SeriesMarkersPaneView<HorzScaleItem> implements IPrimitivePaneView {
    private readonly _series;
    private readonly _chart;
    private _data;
    private _markers;
    private _options;
    private _invalidated;
    private _dataInvalidated;
    private _renderer;
    constructor(series: ISeriesApi<SeriesType, HorzScaleItem>, chart: IChartApiBase<HorzScaleItem>, options: SeriesMarkersOptions);
    renderer(): SeriesMarkersRenderer | null;
    setMarkers(markers: InternalSeriesMarker<TimePointIndex>[]): void;
    update(updateType?: UpdateType): void;
    updateOptions(options: SeriesMarkersOptions): void;
    zOrder(): PrimitivePaneViewZOrder;
    protected _makeValid(): void;
}

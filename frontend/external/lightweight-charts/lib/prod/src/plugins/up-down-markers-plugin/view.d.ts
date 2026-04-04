import { ISeriesApi } from '../../api/iseries-api';
import { ITimeScaleApi } from '../../api/itime-scale-api';
import { IPrimitivePaneView } from '../../model/ipane-primitive';
import { UpDownMarkersPluginOptions } from './options';
import { MarkersPrimitiveRenderer } from './renderer';
import { SeriesUpDownMarker, UpDownMarkersSupportedSeriesTypes } from './types';
export declare class MarkersPrimitivePaneView<HorzScaleItem, TSeriesType extends UpDownMarkersSupportedSeriesTypes> implements IPrimitivePaneView {
    private readonly _series;
    private readonly _timeScale;
    private readonly _options;
    private _data;
    constructor(series: ISeriesApi<TSeriesType, HorzScaleItem>, timeScale: ITimeScaleApi<HorzScaleItem>, options: UpDownMarkersPluginOptions);
    update(markers: readonly SeriesUpDownMarker<HorzScaleItem>[]): void;
    renderer(): MarkersPrimitiveRenderer;
}

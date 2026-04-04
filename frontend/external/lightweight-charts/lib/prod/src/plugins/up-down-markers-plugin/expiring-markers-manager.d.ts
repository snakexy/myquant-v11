import { InternalHorzScaleItemKey } from '../../model/ihorz-scale-behavior';
import { SeriesUpDownMarker } from './types';
export declare class ExpiringMarkerManager<HorzScaleItem> {
    private _markers;
    private _updateCallback;
    constructor(updateCallback: () => void);
    setMarker(marker: SeriesUpDownMarker<HorzScaleItem>, key: InternalHorzScaleItemKey, timeout?: number): void;
    clearMarker(key: InternalHorzScaleItemKey): void;
    clearAllMarkers(): void;
    getMarkers(): SeriesUpDownMarker<HorzScaleItem>[];
    setUpdateCallback(callback: () => void): void;
    private _triggerUpdate;
}

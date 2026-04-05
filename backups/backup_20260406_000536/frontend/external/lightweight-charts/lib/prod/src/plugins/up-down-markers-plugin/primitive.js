import { ensureDefined } from '../../helpers/assertions';
import { isFulfilledData, isWhitespaceData } from '../../model/data-consumer';
import { ExpiringMarkerManager } from './expiring-markers-manager';
import { upDownMarkersPluginOptionDefaults, } from './options';
import { MarkersPrimitivePaneView } from './view';
function isLineData(item, type) {
    return type === 'Line' || type === 'Area';
}
export class UpDownMarkersPrimitive {
    constructor(options) {
        this._private__chart = undefined;
        this._private__series = undefined;
        this._private__paneViews = [];
        this._private__horzScaleBehavior = null;
        this._private__managedDataPoints = new Map();
        this._private__markersManager = new ExpiringMarkerManager(() => this._internal_requestUpdate());
        this._private__options = {
            ...upDownMarkersPluginOptionDefaults,
            ...options,
        };
    }
    _internal_applyOptions(options) {
        this._private__options = {
            ...this._private__options,
            ...options,
        };
        this._internal_requestUpdate();
    }
    _internal_setMarkers(markers) {
        this._private__markersManager._internal_clearAllMarkers();
        const horzBehaviour = this._private__horzScaleBehavior;
        if (!horzBehaviour) {
            return;
        }
        markers.forEach((marker) => {
            this._private__markersManager._internal_setMarker(marker, horzBehaviour.key(marker.time));
        });
    }
    _internal_markers() {
        return this._private__markersManager._internal_getMarkers();
    }
    _internal_requestUpdate() {
        this._private__requestUpdate?.();
    }
    attached(params) {
        const { chart, series, requestUpdate, horzScaleBehavior, } = params;
        this._private__chart = chart;
        this._private__series = series;
        this._private__horzScaleBehavior = horzScaleBehavior;
        const seriesType = this._private__series.seriesType();
        if (seriesType !== 'Area' && seriesType !== 'Line') {
            throw new Error('UpDownMarkersPrimitive is only supported for Area and Line series types');
        }
        this._private__paneViews = [
            new MarkersPrimitivePaneView(this._private__series, this._private__chart.timeScale(), this._private__options),
        ];
        this._private__requestUpdate = requestUpdate;
        this._internal_requestUpdate();
    }
    detached() {
        this._private__chart = undefined;
        this._private__series = undefined;
        this._private__requestUpdate = undefined;
    }
    _internal_chart() {
        return ensureDefined(this._private__chart);
    }
    _internal_series() {
        return ensureDefined(this._private__series);
    }
    updateAllViews() {
        this._private__paneViews.forEach((pw) => pw._internal_update(this._internal_markers()));
    }
    paneViews() {
        return this._private__paneViews;
    }
    _internal_setData(data) {
        if (!this._private__series) {
            throw new Error('Primitive not attached to series');
        }
        const seriesType = this._private__series.seriesType();
        this._private__managedDataPoints.clear();
        const horzBehaviour = this._private__horzScaleBehavior;
        if (horzBehaviour) {
            data.forEach((d) => {
                if (isFulfilledData(d) && isLineData(d, seriesType)) {
                    this._private__managedDataPoints.set(horzBehaviour.key(d.time), d.value);
                }
            });
        }
        ensureDefined(this._private__series).setData(data);
    }
    _internal_update(data, historicalUpdate) {
        if (!this._private__series || !this._private__horzScaleBehavior) {
            throw new Error('Primitive not attached to series');
        }
        const seriesType = this._private__series.seriesType();
        const horzKey = this._private__horzScaleBehavior.key(data.time);
        if (isWhitespaceData(data)) {
            this._private__managedDataPoints.delete(horzKey);
        }
        if (isFulfilledData(data) && isLineData(data, seriesType)) {
            const existingPrice = this._private__managedDataPoints.get(horzKey);
            if (existingPrice) {
                this._private__markersManager._internal_setMarker({
                    time: data.time,
                    value: data.value,
                    sign: getSign(data.value, existingPrice),
                }, horzKey, this._private__options.updateVisibilityDuration);
            }
        }
        ensureDefined(this._private__series).update(data, historicalUpdate);
    }
    _internal_clearMarkers() {
        this._private__markersManager._internal_clearAllMarkers();
    }
}
function getSign(newValue, oldValue) {
    if (newValue === oldValue) {
        return 0;
    }
    return newValue - oldValue > 0 ? 1 : -1;
}

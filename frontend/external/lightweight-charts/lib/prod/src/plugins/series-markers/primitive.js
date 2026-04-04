import { ensureNotNull } from '../../helpers/assertions';
import { seriesMarkerOptionsDefaults } from './options';
import { SeriesMarkersPaneView } from './pane-view';
import { calculateAdjustedMargin, calculateShapeHeight, shapeMargin as calculateShapeMargin, } from './utils';
function mergeOptionsWithDefaults(options) {
    return {
        ...seriesMarkerOptionsDefaults,
        ...options,
    };
}
export class SeriesMarkersPrimitive {
    constructor(options) {
        this._private__paneView = null;
        this._private__markers = [];
        this._private__indexedMarkers = [];
        this._private__dataChangedHandler = null;
        this._private__series = null;
        this._private__chart = null;
        this._private__autoScaleMarginsInvalidated = true;
        this._private__autoScaleMargins = null;
        this._private__markersPositions = null;
        this._private__cachedBarSpacing = null;
        this._private__recalculationRequired = true;
        this._private__options = mergeOptionsWithDefaults(options);
    }
    attached(param) {
        this._private__recalculateMarkers();
        this._private__chart = param.chart;
        this._private__series = param.series;
        this._private__paneView = new SeriesMarkersPaneView(this._private__series, ensureNotNull(this._private__chart), this._private__options);
        this._private__requestUpdate = param.requestUpdate;
        this._private__series.subscribeDataChanged((scope) => this._private__onDataChanged(scope));
        this._private__recalculationRequired = true;
        this._internal_requestUpdate();
    }
    _internal_requestUpdate() {
        if (this._private__requestUpdate) {
            this._private__requestUpdate();
        }
    }
    detached() {
        if (this._private__series && this._private__dataChangedHandler) {
            this._private__series.unsubscribeDataChanged(this._private__dataChangedHandler);
        }
        this._private__chart = null;
        this._private__series = null;
        this._private__paneView = null;
        this._private__dataChangedHandler = null;
    }
    _internal_setMarkers(markers) {
        this._private__recalculationRequired = true;
        this._private__markers = markers;
        this._private__recalculateMarkers();
        this._private__autoScaleMarginsInvalidated = true;
        this._private__markersPositions = null;
        this._internal_requestUpdate();
    }
    _internal_markers() {
        return this._private__markers;
    }
    paneViews() {
        return this._private__paneView ? [this._private__paneView] : [];
    }
    updateAllViews() {
        this._private__updateAllViews();
    }
    hitTest(x, y) {
        if (this._private__paneView) {
            return this._private__paneView.renderer()?._internal_hitTest(x, y) ?? null;
        }
        return null;
    }
    autoscaleInfo(startTimePoint, endTimePoint) {
        if (this._private__options.autoScale && this._private__paneView) {
            const margins = this._private__getAutoScaleMargins();
            if (margins) {
                return {
                    priceRange: null,
                    margins: margins,
                };
            }
        }
        return null;
    }
    _internal_applyOptions(options) {
        this._private__options = mergeOptionsWithDefaults({ ...this._private__options, ...options });
        if (this._internal_requestUpdate) {
            this._internal_requestUpdate();
        }
    }
    _private__getAutoScaleMargins() {
        const chart = ensureNotNull(this._private__chart);
        const barSpacing = chart.timeScale().options().barSpacing;
        if (this._private__autoScaleMarginsInvalidated || barSpacing !== this._private__cachedBarSpacing) {
            this._private__cachedBarSpacing = barSpacing;
            if (this._private__markers.length > 0) {
                const shapeMargin = calculateShapeMargin(barSpacing);
                const marginValue = calculateShapeHeight(barSpacing) * 1.5 + shapeMargin * 2;
                const positions = this._private__getMarkerPositions();
                this._private__autoScaleMargins = {
                    above: calculateAdjustedMargin(marginValue, positions.aboveBar, positions.inBar),
                    below: calculateAdjustedMargin(marginValue, positions.belowBar, positions.inBar),
                };
            }
            else {
                this._private__autoScaleMargins = null;
            }
            this._private__autoScaleMarginsInvalidated = false;
        }
        return this._private__autoScaleMargins;
    }
    _private__getMarkerPositions() {
        if (this._private__markersPositions === null) {
            this._private__markersPositions = this._private__markers.reduce((acc, marker) => {
                if (!acc[marker.position]) {
                    acc[marker.position] = true;
                }
                return acc;
            }, {
                inBar: false,
                aboveBar: false,
                belowBar: false,
                atPriceTop: false,
                atPriceBottom: false,
                atPriceMiddle: false,
            });
        }
        return this._private__markersPositions;
    }
    _private__recalculateMarkers() {
        if (!this._private__recalculationRequired || !this._private__chart || !this._private__series) {
            return;
        }
        const timeScale = this._private__chart.timeScale();
        const seriesData = this._private__series?.data();
        if (timeScale.getVisibleLogicalRange() == null || !this._private__series || seriesData.length === 0) {
            this._private__indexedMarkers = [];
            return;
        }
        const firstDataIndex = timeScale.timeToIndex(ensureNotNull(seriesData[0].time), true);
        this._private__indexedMarkers = this._private__markers.map((marker, index) => {
            const timePointIndex = timeScale.timeToIndex(marker.time, true);
            const searchMode = timePointIndex < firstDataIndex ? 1 /* MismatchDirection.NearestRight */ : -1 /* MismatchDirection.NearestLeft */;
            const seriesDataByIndex = ensureNotNull(this._private__series).dataByIndex(timePointIndex, searchMode);
            const finalIndex = timeScale.timeToIndex(ensureNotNull(seriesDataByIndex).time, false);
            // You must explicitly define the types so that the minification build processes the field names correctly
            const baseMarker = {
                time: finalIndex,
                position: marker.position,
                shape: marker.shape,
                color: marker.color,
                id: marker.id,
                _internal_internalId: index,
                text: marker.text,
                size: marker.size,
                price: marker.price,
                _internal_originalTime: marker.time,
            };
            if (marker.position === 'atPriceTop' ||
                marker.position === 'atPriceBottom' ||
                marker.position === 'atPriceMiddle') {
                if (marker.price === undefined) {
                    throw new Error(`Price is required for position ${marker.position}`);
                }
                return {
                    ...baseMarker,
                    position: marker.position, // TypeScript knows this is SeriesMarkerPricePosition
                    price: marker.price,
                };
            }
            else {
                return {
                    ...baseMarker,
                    position: marker.position, // TypeScript knows this is SeriesMarkerBarPosition
                    price: marker.price, // Optional for bar positions
                };
            }
        });
        this._private__recalculationRequired = false;
    }
    _private__updateAllViews(updateType) {
        if (this._private__paneView) {
            this._private__recalculateMarkers();
            this._private__paneView._internal_setMarkers(this._private__indexedMarkers);
            this._private__paneView._internal_updateOptions(this._private__options);
            this._private__paneView._internal_update(updateType);
        }
    }
    _private__onDataChanged(scope) {
        this._private__recalculationRequired = true;
        this._internal_requestUpdate();
    }
}

import { ensureNever, ensureNotNull } from '../../helpers/assertions';
import { isNumber } from '../../helpers/strict-type-checks';
import { RangeImpl } from '../../model/range-impl';
import { visibleTimedValues } from '../../model/time-data';
import { SeriesMarkersRenderer, } from './renderer';
import { calculateShapeHeight, shapeMargin as calculateShapeMargin, } from './utils';
;
function isPriceMarker(position) {
    return position === 'atPriceTop' || position === 'atPriceBottom' || position === 'atPriceMiddle';
}
function getPrice(seriesData, marker, isInverted) {
    if (isPriceMarker(marker.position) && marker.price !== undefined) {
        return marker.price;
    }
    if (isValueData(seriesData)) {
        return seriesData.value;
    }
    if (isOhlcData(seriesData)) {
        if (marker.position === 'inBar') {
            return seriesData.close;
        }
        if (marker.position === 'aboveBar') {
            if (!isInverted) {
                return seriesData.high;
            }
            return seriesData.low;
        }
        if (marker.position === 'belowBar') {
            if (!isInverted) {
                return seriesData.low;
            }
            return seriesData.high;
        }
    }
    return;
}
// eslint-disable-next-line max-params, complexity
function fillSizeAndY(rendererItem, marker, seriesData, offsets, textHeight, shapeMargin, series, chart) {
    const price = getPrice(seriesData, marker, series.priceScale().options().invertScale);
    if (price === undefined) {
        return;
    }
    const ignoreOffset = isPriceMarker(marker.position);
    const timeScale = chart.timeScale();
    const sizeMultiplier = isNumber(marker.size) ? Math.max(marker.size, 0) : 1;
    const shapeSize = calculateShapeHeight(timeScale.options().barSpacing) * sizeMultiplier;
    const halfSize = shapeSize / 2;
    rendererItem._internal_size = shapeSize;
    const position = marker.position;
    switch (position) {
        case 'inBar':
        case 'atPriceMiddle': {
            rendererItem._internal_y = ensureNotNull(series.priceToCoordinate(price));
            if (rendererItem._internal_text !== undefined) {
                rendererItem._internal_text._internal_y = rendererItem._internal_y + halfSize + shapeMargin + textHeight * (0.5 + 0.1 /* Constants.TextMargin */);
            }
            return;
        }
        case 'aboveBar':
        case 'atPriceTop': {
            const offset = ignoreOffset ? 0 : offsets._internal_aboveBar;
            rendererItem._internal_y = (ensureNotNull(series.priceToCoordinate(price)) - halfSize - offset);
            if (rendererItem._internal_text !== undefined) {
                rendererItem._internal_text._internal_y = rendererItem._internal_y - halfSize - textHeight * (0.5 + 0.1 /* Constants.TextMargin */);
                offsets._internal_aboveBar += textHeight * (1 + 2 * 0.1 /* Constants.TextMargin */);
            }
            if (!ignoreOffset) {
                offsets._internal_aboveBar += shapeSize + shapeMargin;
            }
            return;
        }
        case 'belowBar':
        case 'atPriceBottom': {
            const offset = ignoreOffset ? 0 : offsets._internal_belowBar;
            rendererItem._internal_y = (ensureNotNull(series.priceToCoordinate(price)) + halfSize + offset);
            if (rendererItem._internal_text !== undefined) {
                rendererItem._internal_text._internal_y = (rendererItem._internal_y + halfSize + shapeMargin + textHeight * (0.5 + 0.1 /* Constants.TextMargin */));
                offsets._internal_belowBar += textHeight * (1 + 2 * 0.1 /* Constants.TextMargin */);
            }
            if (!ignoreOffset) {
                offsets._internal_belowBar += shapeSize + shapeMargin;
            }
            return;
        }
    }
    ensureNever(position);
}
function isValueData(data) {
    // eslint-disable-next-line no-restricted-syntax
    return 'value' in data && typeof data.value === 'number';
}
function isOhlcData(data) {
    // eslint-disable-next-line no-restricted-syntax
    return 'open' in data && 'high' in data && 'low' in data && 'close' in data;
}
export class SeriesMarkersPaneView {
    constructor(series, chart, options) {
        this._private__markers = [];
        this._private__invalidated = true;
        this._private__dataInvalidated = true;
        this._private__renderer = new SeriesMarkersRenderer();
        this._private__series = series;
        this._private__chart = chart;
        this._private__data = {
            _internal_items: [],
            _internal_visibleRange: null,
        };
        this._private__options = options;
    }
    renderer() {
        if (!this._private__series.options().visible) {
            return null;
        }
        if (this._private__invalidated) {
            this._internal__makeValid();
        }
        const layout = this._private__chart.options()['layout'];
        this._private__renderer._internal_setParams(layout.fontSize, layout.fontFamily, this._private__options.zOrder);
        this._private__renderer._internal_setData(this._private__data);
        return this._private__renderer;
    }
    _internal_setMarkers(markers) {
        this._private__markers = markers;
        this._internal_update('data');
    }
    _internal_update(updateType) {
        this._private__invalidated = true;
        if (updateType === 'data') {
            this._private__dataInvalidated = true;
        }
    }
    _internal_updateOptions(options) {
        this._private__invalidated = true;
        this._private__options = options;
    }
    zOrder() {
        return this._private__options.zOrder === 'aboveSeries' ? 'top' : this._private__options.zOrder;
    }
    _internal__makeValid() {
        const timeScale = this._private__chart.timeScale();
        const seriesMarkers = this._private__markers;
        if (this._private__dataInvalidated) {
            this._private__data._internal_items = seriesMarkers.map((marker) => ({
                _internal_time: marker.time,
                _internal_x: 0,
                _internal_y: 0,
                _internal_size: 0,
                _internal_shape: marker.shape,
                _internal_color: marker.color,
                _internal_externalId: marker.id,
                _internal_internalId: marker._internal_internalId,
                _internal_text: undefined,
            }));
            this._private__dataInvalidated = false;
        }
        const layoutOptions = this._private__chart.options()['layout'];
        this._private__data._internal_visibleRange = null;
        const visibleBars = timeScale.getVisibleLogicalRange();
        if (visibleBars === null) {
            return;
        }
        const visibleBarsRange = new RangeImpl(Math.floor(visibleBars.from), Math.ceil(visibleBars.to));
        const firstValue = this._private__series.data()[0];
        if (firstValue === null) {
            return;
        }
        if (this._private__data._internal_items.length === 0) {
            return;
        }
        let prevTimeIndex = NaN;
        const shapeMargin = calculateShapeMargin(timeScale.options().barSpacing);
        const offsets = {
            _internal_aboveBar: shapeMargin,
            _internal_belowBar: shapeMargin,
        };
        this._private__data._internal_visibleRange = visibleTimedValues(this._private__data._internal_items, visibleBarsRange, true);
        for (let index = this._private__data._internal_visibleRange.from; index < this._private__data._internal_visibleRange.to; index++) {
            const marker = seriesMarkers[index];
            if (marker.time !== prevTimeIndex) {
                // new bar, reset stack counter
                offsets._internal_aboveBar = shapeMargin;
                offsets._internal_belowBar = shapeMargin;
                prevTimeIndex = marker.time;
            }
            const rendererItem = this._private__data._internal_items[index];
            rendererItem._internal_x = ensureNotNull(timeScale.logicalToCoordinate(marker.time));
            if (marker.text !== undefined && marker.text.length > 0) {
                rendererItem._internal_text = {
                    _internal_content: marker.text,
                    _internal_x: 0,
                    _internal_y: 0,
                    _internal_width: 0,
                    _internal_height: 0,
                };
            }
            const dataAt = this._private__series.dataByIndex(marker.time, 0 /* MismatchDirection.None */);
            if (dataAt === null) {
                continue;
            }
            fillSizeAndY(rendererItem, marker, dataAt, offsets, layoutOptions.fontSize, shapeMargin, this._private__series, this._private__chart);
        }
        this._private__invalidated = false;
    }
}

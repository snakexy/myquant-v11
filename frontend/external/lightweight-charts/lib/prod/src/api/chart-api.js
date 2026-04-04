/// <reference types="_build-time-constants" />
import { ChartWidget } from '../gui/chart-widget';
import { assert, ensure, ensureDefined } from '../helpers/assertions';
import { Delegate } from '../helpers/delegate';
import { warn } from '../helpers/logger';
import { clone, isBoolean, merge } from '../helpers/strict-type-checks';
import { isFulfilledData } from '../model/data-consumer';
import { DataLayer } from '../model/data-layer';
import { Series } from '../model/series';
import { fillUpDownCandlesticksColors, precisionByMinMove, } from '../model/series-options';
import { createCustomSeriesDefinition } from '../model/series/custom-series';
import { isSeriesDefinition } from '../model/series/series-def';
import { getSeriesDataCreator } from './get-series-data-creator';
import { chartOptionsDefaults } from './options/chart-options-defaults';
import { seriesOptionsDefaults } from './options/series-options-defaults';
import { PaneApi } from './pane-api';
import { PriceScaleApi } from './price-scale-api';
import { SeriesApi } from './series-api';
import { TimeScaleApi } from './time-scale-api';
function patchPriceFormat(priceFormat) {
    if (priceFormat === undefined || priceFormat.type === 'custom') {
        return;
    }
    const priceFormatBuiltIn = priceFormat;
    if (priceFormatBuiltIn.minMove !== undefined && priceFormatBuiltIn.precision === undefined) {
        priceFormatBuiltIn.precision = precisionByMinMove(priceFormatBuiltIn.minMove);
    }
}
function migrateHandleScaleScrollOptions(options) {
    if (isBoolean(options['handleScale'])) {
        const handleScale = options['handleScale'];
        options['handleScale'] = {
            axisDoubleClickReset: {
                time: handleScale,
                price: handleScale,
            },
            axisPressedMouseMove: {
                time: handleScale,
                price: handleScale,
            },
            mouseWheel: handleScale,
            pinch: handleScale,
        };
    }
    else if (options['handleScale'] !== undefined) {
        const { axisPressedMouseMove, axisDoubleClickReset } = options['handleScale'];
        if (isBoolean(axisPressedMouseMove)) {
            options['handleScale'].axisPressedMouseMove = {
                time: axisPressedMouseMove,
                price: axisPressedMouseMove,
            };
        }
        if (isBoolean(axisDoubleClickReset)) {
            options['handleScale'].axisDoubleClickReset = {
                time: axisDoubleClickReset,
                price: axisDoubleClickReset,
            };
        }
    }
    const handleScroll = options['handleScroll'];
    if (isBoolean(handleScroll)) {
        options['handleScroll'] = {
            horzTouchDrag: handleScroll,
            vertTouchDrag: handleScroll,
            mouseWheel: handleScroll,
            pressedMouseMove: handleScroll,
        };
    }
}
function toInternalOptions(options) {
    migrateHandleScaleScrollOptions(options);
    return options;
}
export class ChartApi {
    constructor(container, horzScaleBehavior, options) {
        this._private__seriesMap = new Map();
        this._private__seriesMapReversed = new Map();
        this._private__clickedDelegate = new Delegate();
        this._private__dblClickedDelegate = new Delegate();
        this._private__crosshairMovedDelegate = new Delegate();
        this._private__panes = new WeakMap();
        this._private__dataLayer = new DataLayer(horzScaleBehavior);
        const internalOptions = (options === undefined) ?
            clone(chartOptionsDefaults()) :
            merge(clone(chartOptionsDefaults()), toInternalOptions(options));
        this._internal__horzScaleBehavior = horzScaleBehavior;
        this._private__chartWidget = new ChartWidget(container, internalOptions, horzScaleBehavior);
        this._private__chartWidget._internal_clicked()._internal_subscribe((paramSupplier) => {
            if (this._private__clickedDelegate._internal_hasListeners()) {
                this._private__clickedDelegate._internal_fire(this._private__convertMouseParams(paramSupplier()));
            }
        }, this);
        this._private__chartWidget._internal_dblClicked()._internal_subscribe((paramSupplier) => {
            if (this._private__dblClickedDelegate._internal_hasListeners()) {
                this._private__dblClickedDelegate._internal_fire(this._private__convertMouseParams(paramSupplier()));
            }
        }, this);
        this._private__chartWidget._internal_crosshairMoved()._internal_subscribe((paramSupplier) => {
            if (this._private__crosshairMovedDelegate._internal_hasListeners()) {
                this._private__crosshairMovedDelegate._internal_fire(this._private__convertMouseParams(paramSupplier()));
            }
        }, this);
        const model = this._private__chartWidget._internal_model();
        this._private__timeScaleApi = new TimeScaleApi(model, this._private__chartWidget._internal_timeAxisWidget(), this._internal__horzScaleBehavior);
    }
    remove() {
        this._private__chartWidget._internal_clicked()._internal_unsubscribeAll(this);
        this._private__chartWidget._internal_dblClicked()._internal_unsubscribeAll(this);
        this._private__chartWidget._internal_crosshairMoved()._internal_unsubscribeAll(this);
        this._private__timeScaleApi._internal_destroy();
        this._private__chartWidget._internal_destroy();
        this._private__seriesMap.clear();
        this._private__seriesMapReversed.clear();
        this._private__clickedDelegate._internal_destroy();
        this._private__dblClickedDelegate._internal_destroy();
        this._private__crosshairMovedDelegate._internal_destroy();
        this._private__dataLayer._internal_destroy();
    }
    resize(width, height, forceRepaint) {
        if (this.autoSizeActive()) {
            // We return early here instead of checking this within the actual _chartWidget.resize method
            // because this should only apply to external resize requests.
            warn(`Height and width values ignored because 'autoSize' option is enabled.`);
            return;
        }
        this._private__chartWidget._internal_resize(width, height, forceRepaint);
    }
    addCustomSeries(customPaneView, options = {}, paneIndex = 0) {
        const paneView = ensure(customPaneView);
        const definition = createCustomSeriesDefinition(paneView);
        return this._private__addSeriesImpl(definition, options, paneIndex);
    }
    addSeries(definition, options = {}, paneIndex = 0) {
        return this._private__addSeriesImpl(definition, options, paneIndex);
    }
    removeSeries(seriesApi) {
        const series = ensureDefined(this._private__seriesMap.get(seriesApi));
        const update = this._private__dataLayer._internal_removeSeries(series);
        const model = this._private__chartWidget._internal_model();
        model._internal_removeSeries(series);
        this._private__sendUpdateToChart(update);
        this._private__seriesMap.delete(seriesApi);
        this._private__seriesMapReversed.delete(series);
    }
    _internal_applyNewData(series, data) {
        this._private__sendUpdateToChart(this._private__dataLayer._internal_setSeriesData(series, data));
    }
    _internal_updateData(series, data, historicalUpdate) {
        this._private__sendUpdateToChart(this._private__dataLayer._internal_updateSeriesData(series, data, historicalUpdate));
    }
    _internal_popData(series, count) {
        const [poppedData, update] = this._private__dataLayer._internal_popSeriesData(series, count);
        if (poppedData.length !== 0) {
            this._private__sendUpdateToChart(update);
        }
        return poppedData;
    }
    subscribeClick(handler) {
        this._private__clickedDelegate._internal_subscribe(handler);
    }
    unsubscribeClick(handler) {
        this._private__clickedDelegate._internal_unsubscribe(handler);
    }
    subscribeCrosshairMove(handler) {
        this._private__crosshairMovedDelegate._internal_subscribe(handler);
    }
    unsubscribeCrosshairMove(handler) {
        this._private__crosshairMovedDelegate._internal_unsubscribe(handler);
    }
    subscribeDblClick(handler) {
        this._private__dblClickedDelegate._internal_subscribe(handler);
    }
    unsubscribeDblClick(handler) {
        this._private__dblClickedDelegate._internal_unsubscribe(handler);
    }
    priceScale(priceScaleId, paneIndex = 0) {
        return new PriceScaleApi(this._private__chartWidget, priceScaleId, paneIndex);
    }
    timeScale() {
        return this._private__timeScaleApi;
    }
    applyOptions(options) {
        if (process.env.NODE_ENV === 'development') {
            const colorSpace = options.layout?.colorSpace;
            if (colorSpace !== undefined && colorSpace !== this.options().layout.colorSpace) {
                throw new Error(`colorSpace option should not be changed once the chart has been created.`);
            }
            const colorParsers = options.layout?.colorParsers;
            if (colorParsers !== undefined && colorParsers !== this.options().layout.colorParsers) {
                throw new Error(`colorParsers option should not be changed once the chart has been created.`);
            }
        }
        this._private__chartWidget._internal_applyOptions(toInternalOptions(options));
    }
    options() {
        return this._private__chartWidget._internal_options();
    }
    takeScreenshot(addTopLayer = false, includeCrosshair = false) {
        let crosshairMode;
        let screenshotCanvas;
        try {
            if (!includeCrosshair) {
                crosshairMode = this._private__chartWidget._internal_model()._internal_options().crosshair.mode;
                this._private__chartWidget._internal_applyOptions({
                    crosshair: {
                        mode: 2 /* CrosshairMode.Hidden */,
                    },
                });
            }
            screenshotCanvas = this._private__chartWidget._internal_takeScreenshot(addTopLayer);
        }
        finally {
            if (!includeCrosshair && crosshairMode !== undefined) {
                this._private__chartWidget._internal_model()._internal_applyOptions({
                    crosshair: {
                        mode: crosshairMode,
                    },
                });
            }
        }
        return screenshotCanvas;
    }
    addPane(preserveEmptyPane = false) {
        const pane = this._private__chartWidget._internal_model()._internal_addPane();
        pane._internal_setPreserveEmptyPane(preserveEmptyPane);
        return this._private__getPaneApi(pane);
    }
    removePane(index) {
        this._private__chartWidget._internal_model()._internal_removePane(index);
    }
    swapPanes(first, second) {
        this._private__chartWidget._internal_model()._internal_swapPanes(first, second);
    }
    autoSizeActive() {
        return this._private__chartWidget._internal_autoSizeActive();
    }
    chartElement() {
        return this._private__chartWidget._internal_element();
    }
    panes() {
        return this._private__chartWidget._internal_model()._internal_panes().map((pane) => this._private__getPaneApi(pane));
    }
    paneSize(paneIndex = 0) {
        const size = this._private__chartWidget._internal_paneSize(paneIndex);
        return {
            height: size.height,
            width: size.width,
        };
    }
    setCrosshairPosition(price, horizontalPosition, seriesApi) {
        const series = this._private__seriesMap.get(seriesApi);
        if (series === undefined) {
            return;
        }
        const pane = this._private__chartWidget._internal_model()._internal_paneForSource(series);
        if (pane === null) {
            return;
        }
        this._private__chartWidget._internal_model()._internal_setAndSaveSyntheticPosition(price, horizontalPosition, pane);
    }
    clearCrosshairPosition() {
        this._private__chartWidget._internal_model()._internal_clearCurrentPosition(true);
    }
    horzBehaviour() {
        return this._internal__horzScaleBehavior;
    }
    _private__addSeriesImpl(definition, options = {}, paneIndex = 0) {
        assert(isSeriesDefinition(definition));
        patchPriceFormat(options.priceFormat);
        if (definition.type === 'Candlestick') {
            fillUpDownCandlesticksColors(options);
        }
        const strictOptions = merge(clone(seriesOptionsDefaults), clone(definition.defaultOptions), options);
        const createPaneView = definition._internal_createPaneView;
        const series = new Series(this._private__chartWidget._internal_model(), definition.type, strictOptions, createPaneView, definition._internal_customPaneView);
        this._private__chartWidget._internal_model()._internal_addSeriesToPane(series, paneIndex);
        const res = new SeriesApi(series, this, this, this, this._internal__horzScaleBehavior, (pane) => this._private__getPaneApi(pane));
        this._private__seriesMap.set(res, series);
        this._private__seriesMapReversed.set(series, res);
        return res;
    }
    _private__sendUpdateToChart(update) {
        const model = this._private__chartWidget._internal_model();
        model._internal_updateTimeScale(update._internal_timeScale._internal_baseIndex, update._internal_timeScale._internal_points, update._internal_timeScale._internal_firstChangedPointIndex);
        update._internal_series.forEach((value, series) => series._internal_setData(value._internal_data, value._internal_info));
        model._internal_timeScale()._internal_recalculateIndicesWithData();
        model._internal_recalculateAllPanes();
    }
    _private__mapSeriesToApi(series) {
        return ensureDefined(this._private__seriesMapReversed.get(series));
    }
    _private__convertMouseParams(param) {
        const seriesData = new Map();
        param._internal_seriesData.forEach((plotRow, series) => {
            const seriesType = series._internal_seriesType();
            const data = getSeriesDataCreator(seriesType)(plotRow);
            if (seriesType !== 'Custom') {
                assert(isFulfilledData(data));
            }
            else {
                const customWhitespaceChecker = series._internal_customSeriesWhitespaceCheck();
                assert(!customWhitespaceChecker || customWhitespaceChecker(data) === false);
            }
            seriesData.set(this._private__mapSeriesToApi(series), data);
        });
        const hoveredSeries = param._internal_hoveredSeries === undefined ||
            !this._private__seriesMapReversed.has(param._internal_hoveredSeries)
            ? undefined
            : this._private__mapSeriesToApi(param._internal_hoveredSeries);
        return {
            time: param._internal_originalTime,
            logical: param._internal_index,
            point: param._internal_point,
            paneIndex: param._internal_paneIndex,
            hoveredSeries,
            hoveredObjectId: param._internal_hoveredObject,
            seriesData,
            sourceEvent: param._internal_touchMouseEventData,
        };
    }
    _private__getPaneApi(pane) {
        let result = this._private__panes.get(pane);
        if (!result) {
            result = new PaneApi(this._private__chartWidget, (series) => this._private__mapSeriesToApi(series), pane, this);
            this._private__panes.set(pane, result);
        }
        return result;
    }
}

/// <reference types="_build-time-constants" />
import { assert, ensureNotNull } from '../helpers/assertions';
import { Delegate } from '../helpers/delegate';
import { merge } from '../helpers/strict-type-checks';
import { PriceAxisRendererOptionsProvider } from '../renderers/price-axis-renderer-options-provider';
import { ColorParser } from './colors';
import { Crosshair } from './crosshair';
import { isDefaultPriceScale } from './default-price-scale';
import { InvalidateMask } from './invalidate-mask';
import { Magnet } from './magnet';
import { DEFAULT_STRETCH_FACTOR, MIN_PANE_HEIGHT, Pane } from './pane';
import { hitTestPane } from './pane-hit-test';
import { TimeScale } from './time-scale';
;
/**
 * Determine how to exit the tracking mode.
 *
 * By default, mobile users will long press to deactivate the scroll and have the ability to check values and dates.
 * Another press is required to activate the scroll, be able to move left/right, zoom, etc.
 */
export var TrackingModeExitMode;
(function (TrackingModeExitMode) {
    /**
     * Tracking Mode will be deactivated on touch end event.
     */
    TrackingModeExitMode[TrackingModeExitMode["OnTouchEnd"] = 0] = "OnTouchEnd";
    /**
     * Tracking Mode will be deactivated on the next tap event.
     */
    TrackingModeExitMode[TrackingModeExitMode["OnNextTap"] = 1] = "OnNextTap";
})(TrackingModeExitMode || (TrackingModeExitMode = {}));
function isPanePrimitive(source) {
    return source instanceof Pane;
}
export class ChartModel {
    constructor(invalidateHandler, options, horzScaleBehavior) {
        this._private__panes = [];
        this._private__serieses = [];
        this._private__visibleSerieses = null;
        this._private__width = 0;
        this._private__hoveredSource = null;
        this._private__priceScalesOptionsChanged = new Delegate();
        this._private__crosshairMoved = new Delegate();
        this._private__gradientColorsCache = null;
        this._private__invalidateHandler = invalidateHandler;
        this._private__options = options;
        this._private__horzScaleBehavior = horzScaleBehavior;
        this._private__colorParser = new ColorParser(this._private__options.layout.colorParsers);
        this._private__rendererOptionsProvider = new PriceAxisRendererOptionsProvider(this);
        this._private__timeScale = new TimeScale(this, options.timeScale, this._private__options.localization, horzScaleBehavior);
        this._private__crosshair = new Crosshair(this, options.crosshair);
        this._private__magnet = new Magnet(options.crosshair);
        if (options.addDefaultPane) {
            this._private__getOrCreatePane(0);
            this._private__panes[0]._internal_setStretchFactor(DEFAULT_STRETCH_FACTOR * 2);
        }
        this._private__backgroundTopColor = this._private__getBackgroundColor(0 /* BackgroundColorSide.Top */);
        this._private__backgroundBottomColor = this._private__getBackgroundColor(1 /* BackgroundColorSide.Bottom */);
    }
    _internal_fullUpdate() {
        this._private__invalidate(InvalidateMask._internal_full());
    }
    _internal_lightUpdate() {
        this._private__invalidate(InvalidateMask._internal_light());
    }
    _internal_cursorUpdate() {
        this._private__invalidate(new InvalidateMask(1 /* InvalidationLevel.Cursor */));
    }
    _internal_updateSource(source) {
        const inv = this._private__invalidationMaskForSource(source);
        this._private__invalidate(inv);
    }
    _internal_hoveredSource() {
        return this._private__hoveredSource;
    }
    _internal_setHoveredSource(source) {
        if (this._private__hoveredSource?._internal_source === source?._internal_source && this._private__hoveredSource?._internal_object?._internal_externalId === source?._internal_object?._internal_externalId) {
            return;
        }
        const prevSource = this._private__hoveredSource;
        this._private__hoveredSource = source;
        if (prevSource !== null) {
            this._internal_updateSource(prevSource._internal_source);
        }
        // additional check to prevent unnecessary updates of same source
        if (source !== null && source._internal_source !== prevSource?._internal_source) {
            this._internal_updateSource(source._internal_source);
        }
    }
    _internal_options() {
        return this._private__options;
    }
    _internal_applyOptions(options) {
        merge(this._private__options, options);
        this._private__panes.forEach((p) => p._internal_applyScaleOptions(options));
        if (options.timeScale !== undefined) {
            this._private__timeScale._internal_applyOptions(options.timeScale);
        }
        if (options.localization !== undefined) {
            this._private__timeScale._internal_applyLocalizationOptions(options.localization);
        }
        if (options.leftPriceScale || options.rightPriceScale) {
            this._private__priceScalesOptionsChanged._internal_fire();
        }
        this._private__backgroundTopColor = this._private__getBackgroundColor(0 /* BackgroundColorSide.Top */);
        this._private__backgroundBottomColor = this._private__getBackgroundColor(1 /* BackgroundColorSide.Bottom */);
        this._internal_fullUpdate();
    }
    _internal_applyPriceScaleOptions(priceScaleId, options, paneIndex = 0) {
        const pane = this._private__panes[paneIndex];
        if (pane === undefined) {
            if (process.env.NODE_ENV === 'development') {
                throw new Error(`Trying to apply price scale options with incorrect pane index: ${paneIndex}`);
            }
            return;
        }
        // eslint-disable-next-line @typescript-eslint/no-unsafe-enum-comparison
        if (priceScaleId === "left" /* DefaultPriceScaleId.Left */) {
            merge(this._private__options, {
                leftPriceScale: options,
            });
            pane._internal_applyScaleOptions({
                leftPriceScale: options,
            });
            this._private__priceScalesOptionsChanged._internal_fire();
            this._internal_fullUpdate();
            return;
            // eslint-disable-next-line @typescript-eslint/no-unsafe-enum-comparison
        }
        else if (priceScaleId === "right" /* DefaultPriceScaleId.Right */) {
            merge(this._private__options, {
                rightPriceScale: options,
            });
            pane._internal_applyScaleOptions({
                rightPriceScale: options,
            });
            this._private__priceScalesOptionsChanged._internal_fire();
            this._internal_fullUpdate();
            return;
        }
        const res = this._internal_findPriceScale(priceScaleId, paneIndex);
        if (res === null) {
            if (process.env.NODE_ENV === 'development') {
                throw new Error(`Trying to apply price scale options with incorrect ID: ${priceScaleId}`);
            }
            return;
        }
        res._internal_priceScale._internal_applyOptions(options);
        this._private__priceScalesOptionsChanged._internal_fire();
    }
    _internal_findPriceScale(priceScaleId, paneIndex) {
        const pane = this._private__panes[paneIndex];
        if (pane === undefined) {
            return null;
        }
        const priceScale = pane._internal_priceScaleById(priceScaleId);
        if (priceScale !== null) {
            return {
                _internal_pane: pane,
                _internal_priceScale: priceScale,
            };
        }
        return null;
    }
    _internal_timeScale() {
        return this._private__timeScale;
    }
    _internal_panes() {
        return this._private__panes;
    }
    _internal_crosshairSource() {
        return this._private__crosshair;
    }
    _internal_crosshairMoved() {
        return this._private__crosshairMoved;
    }
    _internal_setPaneHeight(pane, height) {
        pane._internal_setHeight(height);
        this._internal_recalculateAllPanes();
    }
    _internal_setWidth(width) {
        this._private__width = width;
        this._private__timeScale._internal_setWidth(this._private__width);
        this._private__panes.forEach((pane) => pane._internal_setWidth(width));
        this._internal_recalculateAllPanes();
    }
    _internal_removePane(index) {
        if (this._private__panes.length === 1) {
            return;
        }
        assert(index >= 0 && index < this._private__panes.length, 'Invalid pane index');
        this._private__panes.splice(index, 1);
        this._internal_fullUpdate();
    }
    _internal_changePanesHeight(paneIndex, height) {
        if (this._private__panes.length < 2) {
            return;
        }
        assert(paneIndex >= 0 && paneIndex < this._private__panes.length, 'Invalid pane index');
        const targetPane = this._private__panes[paneIndex];
        const totalStretch = this._private__panes.reduce((prevValue, pane) => prevValue + pane._internal_stretchFactor(), 0);
        const totalHeight = this._private__panes.reduce((prevValue, pane) => prevValue + pane._internal_height(), 0);
        const maxPaneHeight = totalHeight - MIN_PANE_HEIGHT * (this._private__panes.length - 1);
        height = Math.min(maxPaneHeight, Math.max(MIN_PANE_HEIGHT, height));
        const pixelStretchFactor = totalStretch / totalHeight;
        const oldHeight = targetPane._internal_height();
        targetPane._internal_setStretchFactor(height * pixelStretchFactor);
        let otherPanesChange = height - oldHeight;
        let panesCount = this._private__panes.length - 1;
        for (const pane of this._private__panes) {
            if (pane !== targetPane) {
                const newPaneHeight = Math.min(maxPaneHeight, Math.max(30, pane._internal_height() - otherPanesChange / panesCount));
                otherPanesChange -= (pane._internal_height() - newPaneHeight);
                panesCount -= 1;
                const newStretchFactor = newPaneHeight * pixelStretchFactor;
                pane._internal_setStretchFactor(newStretchFactor);
            }
        }
        this._internal_fullUpdate();
    }
    _internal_swapPanes(first, second) {
        assert(first >= 0 && first < this._private__panes.length && second >= 0 && second < this._private__panes.length, 'Invalid pane index');
        const firstPane = this._private__panes[first];
        const secondPane = this._private__panes[second];
        this._private__panes[first] = secondPane;
        this._private__panes[second] = firstPane;
        this._internal_fullUpdate();
    }
    _internal_movePane(from, to) {
        assert(from >= 0 && from < this._private__panes.length && to >= 0 && to < this._private__panes.length, 'Invalid pane index');
        if (from === to) {
            return;
        }
        const [paneToMove] = this._private__panes.splice(from, 1);
        this._private__panes.splice(to, 0, paneToMove);
        this._internal_fullUpdate();
    }
    _internal_startScalePrice(pane, priceScale, x) {
        pane._internal_startScalePrice(priceScale, x);
    }
    _internal_scalePriceTo(pane, priceScale, x) {
        pane._internal_scalePriceTo(priceScale, x);
        this._internal_updateCrosshair();
        this._private__invalidate(this._private__paneInvalidationMask(pane, 2 /* InvalidationLevel.Light */));
    }
    _internal_endScalePrice(pane, priceScale) {
        pane._internal_endScalePrice(priceScale);
        this._private__invalidate(this._private__paneInvalidationMask(pane, 2 /* InvalidationLevel.Light */));
    }
    _internal_startScrollPrice(pane, priceScale, x) {
        if (priceScale._internal_isAutoScale()) {
            return;
        }
        pane._internal_startScrollPrice(priceScale, x);
    }
    _internal_scrollPriceTo(pane, priceScale, x) {
        if (priceScale._internal_isAutoScale()) {
            return;
        }
        pane._internal_scrollPriceTo(priceScale, x);
        this._internal_updateCrosshair();
        this._private__invalidate(this._private__paneInvalidationMask(pane, 2 /* InvalidationLevel.Light */));
    }
    _internal_endScrollPrice(pane, priceScale) {
        if (priceScale._internal_isAutoScale()) {
            return;
        }
        pane._internal_endScrollPrice(priceScale);
        this._private__invalidate(this._private__paneInvalidationMask(pane, 2 /* InvalidationLevel.Light */));
    }
    _internal_resetPriceScale(pane, priceScale) {
        pane._internal_resetPriceScale(priceScale);
        this._private__invalidate(this._private__paneInvalidationMask(pane, 2 /* InvalidationLevel.Light */));
    }
    _internal_startScaleTime(position) {
        this._private__timeScale._internal_startScale(position);
    }
    /**
     * Zoom in/out the chart (depends on scale value).
     *
     * @param pointX - X coordinate of the point to apply the zoom (the point which should stay on its place)
     * @param scale - Zoom value. Negative value means zoom out, positive - zoom in.
     */
    _internal_zoomTime(pointX, scale) {
        const timeScale = this._internal_timeScale();
        if (timeScale._internal_isEmpty() || scale === 0) {
            return;
        }
        const timeScaleWidth = timeScale._internal_width();
        pointX = Math.max(1, Math.min(pointX, timeScaleWidth));
        timeScale._internal_zoom(pointX, scale);
        this._internal_recalculateAllPanes();
    }
    _internal_scrollChart(x) {
        this._internal_startScrollTime(0);
        this._internal_scrollTimeTo(x);
        this._internal_endScrollTime();
    }
    _internal_scaleTimeTo(x) {
        this._private__timeScale._internal_scaleTo(x);
        this._internal_recalculateAllPanes();
    }
    _internal_endScaleTime() {
        this._private__timeScale._internal_endScale();
        this._internal_lightUpdate();
    }
    _internal_startScrollTime(x) {
        this._private__timeScale._internal_startScroll(x);
    }
    _internal_scrollTimeTo(x) {
        this._private__timeScale._internal_scrollTo(x);
        this._internal_recalculateAllPanes();
    }
    _internal_endScrollTime() {
        this._private__timeScale._internal_endScroll();
        this._internal_lightUpdate();
    }
    _internal_serieses() {
        return this._private__serieses;
    }
    _internal_visibleSerieses() {
        if (this._private__visibleSerieses === null) {
            this._private__visibleSerieses = this._private__serieses.filter((s) => s._internal_visible());
        }
        return this._private__visibleSerieses;
    }
    _internal_invalidateVisibleSeries() {
        this._private__visibleSerieses = null;
    }
    _internal_setAndSaveCurrentPosition(x, y, event, pane, skipEvent) {
        this._private__crosshair._internal_saveOriginCoord(x, y);
        let price = NaN;
        let index = this._private__timeScale._internal_coordinateToIndex(x, true);
        const visibleBars = this._private__timeScale._internal_visibleStrictRange();
        if (visibleBars !== null) {
            index = Math.min(Math.max(visibleBars._internal_left(), index), visibleBars._internal_right());
        }
        index = this._private__crosshair._internal_snapToVisibleSeriesIfNeeded(index);
        const priceScale = pane._internal_defaultPriceScale();
        const firstValue = priceScale._internal_firstValue();
        if (firstValue !== null) {
            price = priceScale._internal_coordinateToPrice(y, firstValue);
        }
        price = this._private__magnet._internal_align(price, index, pane);
        this._private__crosshair._internal_setPosition(index, price, pane);
        this._internal_cursorUpdate();
        if (!skipEvent) {
            const hitTest = hitTestPane(pane, x, y);
            this._internal_setHoveredSource(hitTest && { _internal_source: hitTest._internal_source, _internal_object: hitTest._internal_object, _internal_cursorStyle: hitTest._internal_cursorStyle || null });
            this._private__crosshairMoved._internal_fire(this._private__crosshair._internal_appliedIndex(), { x, y }, event);
        }
    }
    // A position provided external (not from an internal event listener)
    _internal_setAndSaveSyntheticPosition(price, horizontalPosition, pane) {
        const priceScale = pane._internal_defaultPriceScale();
        const firstValue = priceScale._internal_firstValue();
        const y = priceScale._internal_priceToCoordinate(price, ensureNotNull(firstValue));
        const index = this._private__timeScale._internal_timeToIndex(horizontalPosition, true);
        const x = this._private__timeScale._internal_indexToCoordinate(ensureNotNull(index));
        this._internal_setAndSaveCurrentPosition(x, y, null, pane, true);
    }
    _internal_clearCurrentPosition(skipEvent) {
        const crosshair = this._internal_crosshairSource();
        crosshair._internal_clearPosition();
        this._internal_cursorUpdate();
        if (!skipEvent) {
            this._private__crosshairMoved._internal_fire(null, null, null);
        }
    }
    _internal_updateCrosshair() {
        // apply magnet
        const pane = this._private__crosshair._internal_pane();
        if (pane !== null) {
            const x = this._private__crosshair._internal_originCoordX();
            const y = this._private__crosshair._internal_originCoordY();
            this._internal_setAndSaveCurrentPosition(x, y, null, pane);
        }
        this._private__crosshair._internal_updateAllViews();
    }
    _internal_updateTimeScale(newBaseIndex, newPoints, firstChangedPointIndex) {
        const oldFirstTime = this._private__timeScale._internal_indexToTime(0);
        if (newPoints !== undefined && firstChangedPointIndex !== undefined) {
            this._private__timeScale._internal_update(newPoints, firstChangedPointIndex);
        }
        const newFirstTime = this._private__timeScale._internal_indexToTime(0);
        const currentBaseIndex = this._private__timeScale._internal_baseIndex();
        const visibleBars = this._private__timeScale._internal_visibleStrictRange();
        // if time scale cannot return current visible bars range (e.g. time scale has zero-width)
        // then we do not need to update right offset to shift visible bars range to have the same right offset as we have before new bar
        // (and actually we cannot)
        if (visibleBars !== null && oldFirstTime !== null && newFirstTime !== null) {
            const isLastSeriesBarVisible = visibleBars._internal_contains(currentBaseIndex);
            const isLeftBarShiftToLeft = this._private__horzScaleBehavior.key(oldFirstTime) > this._private__horzScaleBehavior.key(newFirstTime);
            const isSeriesPointsAdded = newBaseIndex !== null && newBaseIndex > currentBaseIndex;
            const isSeriesPointsAddedToRight = isSeriesPointsAdded && !isLeftBarShiftToLeft;
            const allowShiftWhenReplacingWhitespace = this._private__timeScale._internal_options().allowShiftVisibleRangeOnWhitespaceReplacement;
            const replacedExistingWhitespace = firstChangedPointIndex === undefined;
            const needShiftVisibleRangeOnNewBar = isLastSeriesBarVisible && (!replacedExistingWhitespace || allowShiftWhenReplacingWhitespace) && this._private__timeScale._internal_options().shiftVisibleRangeOnNewBar;
            if (isSeriesPointsAddedToRight && !needShiftVisibleRangeOnNewBar) {
                const compensationShift = newBaseIndex - currentBaseIndex;
                this._private__timeScale._internal_setRightOffset(this._private__timeScale._internal_rightOffset() - compensationShift);
            }
        }
        this._private__timeScale._internal_setBaseIndex(newBaseIndex);
    }
    _internal_recalculatePane(pane) {
        if (pane !== null) {
            pane._internal_recalculate();
        }
    }
    _internal_paneForSource(source) {
        if (isPanePrimitive(source)) {
            return source;
        }
        const pane = this._private__panes.find((p) => p._internal_orderedSources().includes(source));
        return pane === undefined ? null : pane;
    }
    _internal_recalculateAllPanes() {
        this._private__panes.forEach((p) => p._internal_recalculate());
        this._internal_updateCrosshair();
    }
    _internal_destroy() {
        this._private__panes.forEach((p) => p._internal_destroy());
        this._private__panes.length = 0;
        // to avoid memleaks
        this._private__options.localization.priceFormatter = undefined;
        this._private__options.localization.percentageFormatter = undefined;
        this._private__options.localization.timeFormatter = undefined;
    }
    _internal_rendererOptionsProvider() {
        return this._private__rendererOptionsProvider;
    }
    _internal_priceAxisRendererOptions() {
        return this._private__rendererOptionsProvider._internal_options();
    }
    _internal_priceScalesOptionsChanged() {
        return this._private__priceScalesOptionsChanged;
    }
    _internal_addSeriesToPane(series, paneIndex) {
        const pane = this._private__getOrCreatePane(paneIndex);
        this._private__addSeriesToPane(series, pane);
        this._private__serieses.push(series);
        this._internal_invalidateVisibleSeries();
        if (this._private__serieses.length === 1) {
            // call fullUpdate to recalculate chart's parts geometry
            this._internal_fullUpdate();
        }
        else {
            this._internal_lightUpdate();
        }
    }
    _internal_removeSeries(series) {
        const pane = this._internal_paneForSource(series);
        const seriesIndex = this._private__serieses.indexOf(series);
        assert(seriesIndex !== -1, 'Series not found');
        const paneImpl = ensureNotNull(pane);
        this._private__serieses.splice(seriesIndex, 1);
        paneImpl._internal_removeDataSource(series);
        if (series._internal_destroy) {
            series._internal_destroy();
        }
        this._internal_invalidateVisibleSeries();
        this._private__timeScale._internal_recalculateIndicesWithData();
        this._private__cleanupIfPaneIsEmpty(paneImpl);
    }
    _internal_moveSeriesToScale(series, targetScaleId) {
        const pane = ensureNotNull(this._internal_paneForSource(series));
        pane._internal_removeDataSource(series, true);
        pane._internal_addDataSource(series, targetScaleId, true);
    }
    _internal_fitContent() {
        const mask = InvalidateMask._internal_light();
        mask._internal_setFitContent();
        this._private__invalidate(mask);
    }
    _internal_setTargetLogicalRange(range) {
        const mask = InvalidateMask._internal_light();
        mask._internal_applyRange(range);
        this._private__invalidate(mask);
    }
    _internal_resetTimeScale() {
        const mask = InvalidateMask._internal_light();
        mask._internal_resetTimeScale();
        this._private__invalidate(mask);
    }
    _internal_setBarSpacing(spacing) {
        const mask = InvalidateMask._internal_light();
        mask._internal_setBarSpacing(spacing);
        this._private__invalidate(mask);
    }
    _internal_setRightOffset(offset) {
        const mask = InvalidateMask._internal_light();
        mask._internal_setRightOffset(offset);
        this._private__invalidate(mask);
    }
    _internal_setTimeScaleAnimation(animation) {
        const mask = InvalidateMask._internal_light();
        mask._internal_setTimeScaleAnimation(animation);
        this._private__invalidate(mask);
    }
    _internal_stopTimeScaleAnimation() {
        const mask = InvalidateMask._internal_light();
        mask._internal_stopTimeScaleAnimation();
        this._private__invalidate(mask);
    }
    _internal_defaultVisiblePriceScaleId() {
        return this._private__options.rightPriceScale.visible ? "right" /* DefaultPriceScaleId.Right */ : "left" /* DefaultPriceScaleId.Left */;
    }
    _internal_moveSeriesToPane(series, newPaneIndex) {
        assert(newPaneIndex >= 0, 'Index should be greater or equal to 0');
        const fromPaneIndex = this._private__seriesPaneIndex(series);
        if (newPaneIndex === fromPaneIndex) {
            return;
        }
        const previousPane = ensureNotNull(this._internal_paneForSource(series));
        previousPane._internal_removeDataSource(series);
        const newPane = this._private__getOrCreatePane(newPaneIndex);
        this._private__addSeriesToPane(series, newPane);
        let paneWasRemoved = false;
        if (previousPane._internal_dataSources().length === 0) {
            paneWasRemoved = this._private__cleanupIfPaneIsEmpty(previousPane);
        }
        if (!paneWasRemoved) {
            this._internal_fullUpdate();
        }
    }
    _internal_backgroundBottomColor() {
        return this._private__backgroundBottomColor;
    }
    _internal_backgroundTopColor() {
        return this._private__backgroundTopColor;
    }
    _internal_backgroundColorAtYPercentFromTop(percent) {
        const bottomColor = this._private__backgroundBottomColor;
        const topColor = this._private__backgroundTopColor;
        if (bottomColor === topColor) {
            // solid background
            return bottomColor;
        }
        // gradient background
        // percent should be from 0 to 100 (we're using only integer values to make cache more efficient)
        percent = Math.max(0, Math.min(100, Math.round(percent * 100)));
        if (this._private__gradientColorsCache === null ||
            this._private__gradientColorsCache._internal_topColor !== topColor || this._private__gradientColorsCache._internal_bottomColor !== bottomColor) {
            this._private__gradientColorsCache = {
                _internal_topColor: topColor,
                _internal_bottomColor: bottomColor,
                _internal_colors: new Map(),
            };
        }
        else {
            const cachedValue = this._private__gradientColorsCache._internal_colors.get(percent);
            if (cachedValue !== undefined) {
                return cachedValue;
            }
        }
        const result = this._private__colorParser._internal_gradientColorAtPercent(topColor, bottomColor, percent / 100);
        this._private__gradientColorsCache._internal_colors.set(percent, result);
        return result;
    }
    _internal_getPaneIndex(pane) {
        return this._private__panes.indexOf(pane);
    }
    _internal_colorParser() {
        return this._private__colorParser;
    }
    _internal_addPane() {
        return this._private__addPane();
    }
    _private__addPane(index) {
        const pane = new Pane(this._private__timeScale, this);
        this._private__panes.push(pane);
        const idx = index ?? this._private__panes.length - 1;
        // we always do autoscaling on the creation
        // if autoscale option is true, it is ok, just recalculate by invalidation mask
        // if autoscale option is false, autoscale anyway on the first draw
        // also there is a scenario when autoscale is true in constructor and false later on applyOptions
        const mask = InvalidateMask._internal_full();
        mask._internal_invalidatePane(idx, {
            _internal_level: 0 /* InvalidationLevel.None */,
            _internal_autoScale: true,
        });
        this._private__invalidate(mask);
        return pane;
    }
    _private__getOrCreatePane(index) {
        assert(index >= 0, 'Index should be greater or equal to 0');
        index = Math.min(this._private__panes.length, index);
        if (index < this._private__panes.length) {
            return this._private__panes[index];
        }
        return this._private__addPane(index);
    }
    _private__seriesPaneIndex(series) {
        return this._private__panes.findIndex((pane) => pane._internal_series().includes(series));
    }
    _private__paneInvalidationMask(pane, level) {
        const inv = new InvalidateMask(level);
        if (pane !== null) {
            const index = this._private__panes.indexOf(pane);
            inv._internal_invalidatePane(index, {
                _internal_level: level,
            });
        }
        return inv;
    }
    _private__invalidationMaskForSource(source, invalidateType) {
        if (invalidateType === undefined) {
            invalidateType = 2 /* InvalidationLevel.Light */;
        }
        return this._private__paneInvalidationMask(this._internal_paneForSource(source), invalidateType);
    }
    _private__invalidate(mask) {
        if (this._private__invalidateHandler) {
            this._private__invalidateHandler(mask);
        }
        this._private__panes.forEach((pane) => pane._internal_grid()._internal_paneView()._internal_update());
    }
    _private__addSeriesToPane(series, pane) {
        const priceScaleId = series._internal_options().priceScaleId;
        const targetScaleId = priceScaleId !== undefined ? priceScaleId : this._internal_defaultVisiblePriceScaleId();
        pane._internal_addDataSource(series, targetScaleId);
        if (!isDefaultPriceScale(targetScaleId)) {
            // let's apply that options again to apply margins
            series._internal_applyOptions(series._internal_options());
        }
    }
    _private__getBackgroundColor(side) {
        const layoutOptions = this._private__options['layout'];
        if (layoutOptions.background.type === "gradient" /* ColorType.VerticalGradient */) {
            return side === 0 /* BackgroundColorSide.Top */ ?
                layoutOptions.background.topColor :
                layoutOptions.background.bottomColor;
        }
        return layoutOptions.background.color;
    }
    _private__cleanupIfPaneIsEmpty(pane) {
        if (!pane._internal_preserveEmptyPane() && (pane._internal_dataSources().length === 0 && this._private__panes.length > 1)) {
            this._private__panes.splice(this._internal_getPaneIndex(pane), 1);
            this._internal_fullUpdate();
            return true;
        }
        return false;
    }
}

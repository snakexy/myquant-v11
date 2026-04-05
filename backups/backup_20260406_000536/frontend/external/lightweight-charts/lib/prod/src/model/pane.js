import { assert, ensureDefined, ensureNotNull } from '../helpers/assertions';
import { Delegate } from '../helpers/delegate';
import { clamp } from '../helpers/mathex';
import { clone } from '../helpers/strict-type-checks';
import { isDefaultPriceScale } from './default-price-scale';
import { Grid } from './grid';
import { PanePrimitiveWrapper } from './pane-primitive-wrapper';
import { PriceScale } from './price-scale';
import { Series } from './series';
import { sortSources } from './sort-sources';
function isSeries(source) {
    return source instanceof Series;
}
export const DEFAULT_STRETCH_FACTOR = 1;
export const MIN_PANE_HEIGHT = 30;
export class Pane {
    constructor(timeScale, model) {
        this._private__dataSources = [];
        this._private__overlaySourcesByScaleId = new Map();
        this._private__height = 0;
        this._private__width = 0;
        this._private__stretchFactor = DEFAULT_STRETCH_FACTOR;
        this._private__cachedOrderedSources = null;
        this._private__preserveEmptyPane = false;
        this._private__destroyed = new Delegate();
        this._private__primitives = [];
        this._private__timeScale = timeScale;
        this._private__model = model;
        this._private__grid = new Grid(this);
        const options = model._internal_options();
        this._private__leftPriceScale = this._private__createPriceScale("left" /* DefaultPriceScaleId.Left */, options.leftPriceScale);
        this._private__rightPriceScale = this._private__createPriceScale("right" /* DefaultPriceScaleId.Right */, options.rightPriceScale);
        this._private__leftPriceScale._internal_modeChanged()._internal_subscribe(this._private__onPriceScaleModeChanged.bind(this, this._private__leftPriceScale), this);
        this._private__rightPriceScale._internal_modeChanged()._internal_subscribe(this._private__onPriceScaleModeChanged.bind(this, this._private__rightPriceScale), this);
        this._internal_applyScaleOptions(options);
    }
    _internal_applyScaleOptions(options) {
        if (options.leftPriceScale) {
            this._private__leftPriceScale._internal_applyOptions(options.leftPriceScale);
        }
        if (options.rightPriceScale) {
            this._private__rightPriceScale._internal_applyOptions(options.rightPriceScale);
        }
        if (options.localization) {
            this._private__leftPriceScale._internal_updateFormatter();
            this._private__rightPriceScale._internal_updateFormatter();
        }
        if (options.overlayPriceScales) {
            const sourceArrays = Array.from(this._private__overlaySourcesByScaleId.values());
            for (const arr of sourceArrays) {
                const priceScale = ensureNotNull(arr[0]._internal_priceScale());
                priceScale._internal_applyOptions(options.overlayPriceScales);
                if (options.localization) {
                    priceScale._internal_updateFormatter();
                }
            }
        }
    }
    _internal_priceScaleById(id) {
        switch (id) {
            // eslint-disable-next-line @typescript-eslint/no-unsafe-enum-comparison
            case "left" /* DefaultPriceScaleId.Left */: {
                return this._private__leftPriceScale;
            }
            // eslint-disable-next-line @typescript-eslint/no-unsafe-enum-comparison
            case "right" /* DefaultPriceScaleId.Right */: {
                return this._private__rightPriceScale;
            }
        }
        if (this._private__overlaySourcesByScaleId.has(id)) {
            return ensureDefined(this._private__overlaySourcesByScaleId.get(id))[0]._internal_priceScale();
        }
        return null;
    }
    _internal_destroy() {
        this._internal_model()._internal_priceScalesOptionsChanged()._internal_unsubscribeAll(this);
        this._private__leftPriceScale._internal_modeChanged()._internal_unsubscribeAll(this);
        this._private__rightPriceScale._internal_modeChanged()._internal_unsubscribeAll(this);
        this._private__dataSources.forEach((source) => {
            if (source._internal_destroy) {
                source._internal_destroy();
            }
        });
        this._private__primitives = this._private__primitives.filter((primitive) => {
            const p = primitive._internal_primitive();
            if (p.detached) {
                p.detached();
            }
            return false;
        });
        this._private__destroyed._internal_fire();
    }
    _internal_stretchFactor() {
        return this._private__stretchFactor;
    }
    _internal_setStretchFactor(factor) {
        this._private__stretchFactor = factor;
    }
    _internal_model() {
        return this._private__model;
    }
    _internal_width() {
        return this._private__width;
    }
    _internal_height() {
        return this._private__height;
    }
    _internal_setWidth(width) {
        this._private__width = width;
        this._internal_updateAllSources();
    }
    _internal_setHeight(height) {
        this._private__height = height;
        this._private__leftPriceScale._internal_setHeight(height);
        this._private__rightPriceScale._internal_setHeight(height);
        // process overlays
        this._private__dataSources.forEach((ds) => {
            if (this._internal_isOverlay(ds)) {
                const priceScale = ds._internal_priceScale();
                if (priceScale !== null) {
                    priceScale._internal_setHeight(height);
                }
            }
        });
        this._internal_updateAllSources();
    }
    _internal_setPreserveEmptyPane(preserve) {
        this._private__preserveEmptyPane = preserve;
    }
    _internal_preserveEmptyPane() {
        return this._private__preserveEmptyPane;
    }
    _internal_series() {
        return this._private__dataSources.filter(isSeries);
    }
    _internal_dataSources() {
        return this._private__dataSources;
    }
    _internal_isOverlay(source) {
        const priceScale = source._internal_priceScale();
        if (priceScale === null) {
            return true;
        }
        return this._private__leftPriceScale !== priceScale && this._private__rightPriceScale !== priceScale;
    }
    _internal_addDataSource(source, targetScaleId, keepSourcesOrder) {
        this._private__insertDataSource(source, targetScaleId, keepSourcesOrder ? source._internal_zorder() : this._private__dataSources.length);
    }
    _internal_removeDataSource(source, keepSourceOrder) {
        const index = this._private__dataSources.indexOf(source);
        assert(index !== -1, 'removeDataSource: invalid data source');
        this._private__dataSources.splice(index, 1);
        if (!keepSourceOrder) {
            this._private__dataSources.forEach((ds, i) => ds._internal_setZorder(i));
        }
        const priceScaleId = ensureNotNull(source._internal_priceScale())._internal_id();
        if (this._private__overlaySourcesByScaleId.has(priceScaleId)) {
            const overlaySources = ensureDefined(this._private__overlaySourcesByScaleId.get(priceScaleId));
            const overlayIndex = overlaySources.indexOf(source);
            if (overlayIndex !== -1) {
                overlaySources.splice(overlayIndex, 1);
                if (overlaySources.length === 0) {
                    this._private__overlaySourcesByScaleId.delete(priceScaleId);
                }
            }
        }
        const priceScale = source._internal_priceScale();
        // if source has owner, it returns owner's price scale
        // and it does not have source in their list
        if (priceScale && priceScale._internal_dataSources().indexOf(source) >= 0) {
            priceScale._internal_removeDataSource(source);
            this._internal_recalculatePriceScale(priceScale);
        }
        this._private__cachedOrderedSources = null;
    }
    _internal_priceScalePosition(priceScale) {
        if (priceScale === this._private__leftPriceScale) {
            return 'left';
        }
        if (priceScale === this._private__rightPriceScale) {
            return 'right';
        }
        return 'overlay';
    }
    _internal_leftPriceScale() {
        return this._private__leftPriceScale;
    }
    _internal_rightPriceScale() {
        return this._private__rightPriceScale;
    }
    _internal_startScalePrice(priceScale, x) {
        priceScale._internal_startScale(x);
    }
    _internal_scalePriceTo(priceScale, x) {
        priceScale._internal_scaleTo(x);
        // TODO: be more smart and update only affected views
        this._internal_updateAllSources();
    }
    _internal_endScalePrice(priceScale) {
        priceScale._internal_endScale();
    }
    _internal_startScrollPrice(priceScale, x) {
        priceScale._internal_startScroll(x);
    }
    _internal_scrollPriceTo(priceScale, x) {
        priceScale._internal_scrollTo(x);
        this._internal_updateAllSources();
    }
    _internal_endScrollPrice(priceScale) {
        priceScale._internal_endScroll();
    }
    _internal_updateAllSources() {
        this._private__dataSources.forEach((source) => {
            source._internal_updateAllViews();
        });
    }
    _internal_defaultPriceScale() {
        let priceScale = null;
        if (this._private__model._internal_options().rightPriceScale.visible && this._private__rightPriceScale._internal_dataSources().length !== 0) {
            priceScale = this._private__rightPriceScale;
        }
        else if (this._private__model._internal_options().leftPriceScale.visible && this._private__leftPriceScale._internal_dataSources().length !== 0) {
            priceScale = this._private__leftPriceScale;
        }
        else if (this._private__dataSources.length !== 0) {
            priceScale = this._private__dataSources[0]._internal_priceScale();
        }
        if (priceScale === null) {
            priceScale = this._private__rightPriceScale;
        }
        return priceScale;
    }
    _internal_defaultVisiblePriceScale() {
        let priceScale = null;
        if (this._private__model._internal_options().rightPriceScale.visible) {
            priceScale = this._private__rightPriceScale;
        }
        else if (this._private__model._internal_options().leftPriceScale.visible) {
            priceScale = this._private__leftPriceScale;
        }
        return priceScale;
    }
    _internal_recalculatePriceScale(priceScale) {
        if (priceScale === null || !priceScale._internal_isAutoScale()) {
            return;
        }
        this._private__recalculatePriceScaleImpl(priceScale);
    }
    _internal_resetPriceScale(priceScale) {
        const visibleBars = this._private__timeScale._internal_visibleStrictRange();
        priceScale._internal_setMode({ _internal_autoScale: true });
        if (visibleBars !== null) {
            priceScale._internal_recalculatePriceRange(visibleBars);
        }
        this._internal_updateAllSources();
    }
    _internal_momentaryAutoScale() {
        this._private__recalculatePriceScaleImpl(this._private__leftPriceScale);
        this._private__recalculatePriceScaleImpl(this._private__rightPriceScale);
    }
    _internal_recalculate() {
        this._internal_recalculatePriceScale(this._private__leftPriceScale);
        this._internal_recalculatePriceScale(this._private__rightPriceScale);
        this._private__dataSources.forEach((ds) => {
            if (this._internal_isOverlay(ds)) {
                this._internal_recalculatePriceScale(ds._internal_priceScale());
            }
        });
        this._internal_updateAllSources();
        this._private__model._internal_lightUpdate();
    }
    _internal_orderedSources() {
        if (this._private__cachedOrderedSources === null) {
            this._private__cachedOrderedSources = sortSources(this._private__dataSources);
        }
        return this._private__cachedOrderedSources;
    }
    _internal_setSeriesOrder(series, order) {
        order = clamp(order, 0, this._private__dataSources.length - 1);
        const index = this._private__dataSources.indexOf(series);
        assert(index !== -1, 'setSeriesOrder: invalid data source');
        this._private__dataSources.splice(index, 1);
        this._private__dataSources.splice(order, 0, series);
        this._private__dataSources.forEach((ps, i) => ps._internal_setZorder(i));
        this._private__cachedOrderedSources = null;
        for (const ps of [this._private__leftPriceScale, this._private__rightPriceScale]) {
            ps._internal_invalidateSourcesCache();
            ps._internal_updateFormatter();
        }
        this._private__model._internal_lightUpdate();
    }
    _internal_orderedSeries() {
        return this._internal_orderedSources().filter(isSeries);
    }
    _internal_onDestroyed() {
        return this._private__destroyed;
    }
    _internal_grid() {
        return this._private__grid;
    }
    _internal_attachPrimitive(primitive) {
        this._private__primitives.push(new PanePrimitiveWrapper(primitive));
    }
    _internal_detachPrimitive(source) {
        this._private__primitives = this._private__primitives.filter((wrapper) => wrapper._internal_primitive() !== source);
        if (source.detached) {
            source.detached();
        }
        this._private__model._internal_lightUpdate();
    }
    _internal_primitives() {
        return this._private__primitives;
    }
    _internal_primitiveHitTest(x, y) {
        return this._private__primitives
            .map((primitive) => primitive._internal_hitTest(x, y))
            .filter((result) => result !== null);
    }
    _private__recalculatePriceScaleImpl(priceScale) {
        // TODO: can use this checks
        const sourceForAutoScale = priceScale._internal_sourcesForAutoScale();
        if (sourceForAutoScale && sourceForAutoScale.length > 0 && !this._private__timeScale._internal_isEmpty()) {
            const visibleBars = this._private__timeScale._internal_visibleStrictRange();
            if (visibleBars !== null) {
                priceScale._internal_recalculatePriceRange(visibleBars);
            }
        }
        priceScale._internal_updateAllViews();
    }
    _private__insertDataSource(source, priceScaleId, order) {
        let priceScale = this._internal_priceScaleById(priceScaleId);
        if (priceScale === null) {
            priceScale = this._private__createPriceScale(priceScaleId, this._private__model._internal_options().overlayPriceScales);
        }
        this._private__dataSources.splice(order, 0, source);
        if (!isDefaultPriceScale(priceScaleId)) {
            const overlaySources = this._private__overlaySourcesByScaleId.get(priceScaleId) || [];
            overlaySources.push(source);
            this._private__overlaySourcesByScaleId.set(priceScaleId, overlaySources);
        }
        source._internal_setZorder(order);
        priceScale._internal_addDataSource(source);
        source._internal_setPriceScale(priceScale);
        this._internal_recalculatePriceScale(priceScale);
        this._private__cachedOrderedSources = null;
    }
    _private__onPriceScaleModeChanged(priceScale, oldMode, newMode) {
        if (oldMode._internal_mode === newMode._internal_mode) {
            return;
        }
        // momentary auto scale if we toggle percentage/indexedTo100 mode
        this._private__recalculatePriceScaleImpl(priceScale);
    }
    _private__createPriceScale(id, options) {
        const actualOptions = { visible: true, autoScale: true, ...clone(options) };
        const priceScale = new PriceScale(id, actualOptions, this._private__model._internal_options()['layout'], this._private__model._internal_options().localization, this._private__model._internal_colorParser());
        priceScale._internal_setHeight(this._internal_height());
        return priceScale;
    }
}

import { TimeAxisViewRenderer } from '../renderers/time-axis-view-renderer';
import { PriceAxisView } from '../views/price-axis/price-axis-view';
import { PrimitiveWrapper } from './pane-primitive-wrapper';
import { drawingUtils } from './primitive-drawing-utils';
class SeriesPrimitiveRendererWrapper {
    constructor(baseRenderer) {
        this._private__baseRenderer = baseRenderer;
    }
    _internal_draw(target, isHovered, hitTestData) {
        this._private__baseRenderer.draw(target, drawingUtils);
    }
    _internal_drawBackground(target, isHovered, hitTestData) {
        this._private__baseRenderer.drawBackground?.(target, drawingUtils);
    }
}
class SeriesPrimitivePaneViewWrapper {
    constructor(paneView) {
        this._private__cache = null;
        this._private__paneView = paneView;
    }
    _internal_renderer() {
        const baseRenderer = this._private__paneView.renderer();
        if (baseRenderer === null) {
            return null;
        }
        if (this._private__cache?._internal_base === baseRenderer) {
            return this._private__cache._internal_wrapper;
        }
        const wrapper = new SeriesPrimitiveRendererWrapper(baseRenderer);
        this._private__cache = {
            _internal_base: baseRenderer,
            _internal_wrapper: wrapper,
        };
        return wrapper;
    }
    _internal_zOrder() {
        return this._private__paneView.zOrder?.() ?? 'normal';
    }
}
function getAxisViewData(baseView) {
    return {
        _internal_text: baseView.text(),
        _internal_coordinate: baseView.coordinate(),
        _internal_fixedCoordinate: baseView.fixedCoordinate?.(),
        _internal_color: baseView.textColor(),
        _internal_background: baseView.backColor(),
        _internal_visible: baseView.visible?.() ?? true,
        _internal_tickVisible: baseView.tickVisible?.() ?? true,
    };
}
class SeriesPrimitiveTimeAxisViewWrapper {
    constructor(baseView, timeScale) {
        this._private__renderer = new TimeAxisViewRenderer();
        this._private__baseView = baseView;
        this._private__timeScale = timeScale;
    }
    _internal_renderer() {
        this._private__renderer._internal_setData({
            _internal_width: this._private__timeScale._internal_width(),
            ...getAxisViewData(this._private__baseView),
        });
        return this._private__renderer;
    }
}
class SeriesPrimitivePriceAxisViewWrapper extends PriceAxisView {
    constructor(baseView, priceScale) {
        super();
        this._private__baseView = baseView;
        this._private__priceScale = priceScale;
    }
    _internal__updateRendererData(axisRendererData, paneRendererData, commonRendererData) {
        const data = getAxisViewData(this._private__baseView);
        commonRendererData._internal_background = data._internal_background;
        axisRendererData._internal_color = data._internal_color;
        const additionalPadding = 2 / 12 * this._private__priceScale._internal_fontSize();
        commonRendererData._internal_additionalPaddingTop = additionalPadding;
        commonRendererData._internal_additionalPaddingBottom = additionalPadding;
        commonRendererData._internal_coordinate = data._internal_coordinate;
        commonRendererData._internal_fixedCoordinate = data._internal_fixedCoordinate;
        axisRendererData._internal_text = data._internal_text;
        axisRendererData._internal_visible = data._internal_visible;
        axisRendererData._internal_tickVisible = data._internal_tickVisible;
    }
}
export class SeriesPrimitiveWrapper extends PrimitiveWrapper {
    constructor(primitive, series) {
        super(primitive);
        this._private__timeAxisViewsCache = null;
        this._private__priceAxisViewsCache = null;
        this._private__priceAxisPaneViewsCache = null;
        this._private__timeAxisPaneViewsCache = null;
        this._private__series = series;
    }
    _internal_timeAxisViews() {
        const base = this._internal__primitive.timeAxisViews?.() ?? [];
        if (this._private__timeAxisViewsCache?._internal_base === base) {
            return this._private__timeAxisViewsCache._internal_wrapper;
        }
        const timeScale = this._private__series._internal_model()._internal_timeScale();
        const wrapper = base.map((aw) => new SeriesPrimitiveTimeAxisViewWrapper(aw, timeScale));
        this._private__timeAxisViewsCache = {
            _internal_base: base,
            _internal_wrapper: wrapper,
        };
        return wrapper;
    }
    _internal_priceAxisViews() {
        const base = this._internal__primitive.priceAxisViews?.() ?? [];
        if (this._private__priceAxisViewsCache?._internal_base === base) {
            return this._private__priceAxisViewsCache._internal_wrapper;
        }
        const priceScale = this._private__series._internal_priceScale();
        const wrapper = base.map((aw) => new SeriesPrimitivePriceAxisViewWrapper(aw, priceScale));
        this._private__priceAxisViewsCache = {
            _internal_base: base,
            _internal_wrapper: wrapper,
        };
        return wrapper;
    }
    _internal_priceAxisPaneViews() {
        const base = this._internal__primitive.priceAxisPaneViews?.() ?? [];
        if (this._private__priceAxisPaneViewsCache?._internal_base === base) {
            return this._private__priceAxisPaneViewsCache._internal_wrapper;
        }
        const wrapper = base.map((pw) => new SeriesPrimitivePaneViewWrapper(pw));
        this._private__priceAxisPaneViewsCache = {
            _internal_base: base,
            _internal_wrapper: wrapper,
        };
        return wrapper;
    }
    _internal_timeAxisPaneViews() {
        const base = this._internal__primitive.timeAxisPaneViews?.() ?? [];
        if (this._private__timeAxisPaneViewsCache?._internal_base === base) {
            return this._private__timeAxisPaneViewsCache._internal_wrapper;
        }
        const wrapper = base.map((pw) => new SeriesPrimitivePaneViewWrapper(pw));
        this._private__timeAxisPaneViewsCache = {
            _internal_base: base,
            _internal_wrapper: wrapper,
        };
        return wrapper;
    }
    _internal_autoscaleInfo(startTimePoint, endTimePoint) {
        return (this._internal__primitive.autoscaleInfo?.(startTimePoint, endTimePoint) ?? null);
    }
}

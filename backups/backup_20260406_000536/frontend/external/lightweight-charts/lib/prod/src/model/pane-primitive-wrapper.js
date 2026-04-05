import { drawingUtils } from './primitive-drawing-utils';
class PrimitiveRendererWrapper {
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
class PrimitivePaneViewWrapper {
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
        const wrapper = new PrimitiveRendererWrapper(baseRenderer);
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
export class PrimitiveWrapper {
    constructor(primitive) {
        this._private__paneViewsCache = null;
        this._internal__primitive = primitive;
    }
    _internal_primitive() {
        return this._internal__primitive;
    }
    _internal_updateAllViews() {
        this._internal__primitive.updateAllViews?.();
    }
    _internal_paneViews() {
        const base = this._internal__primitive.paneViews?.() ?? [];
        if (this._private__paneViewsCache?._internal_base === base) {
            return this._private__paneViewsCache._internal_wrapper;
        }
        const wrapper = base.map((pw) => new PrimitivePaneViewWrapper(pw));
        this._private__paneViewsCache = {
            _internal_base: base,
            _internal_wrapper: wrapper,
        };
        return wrapper;
    }
    _internal_hitTest(x, y) {
        return this._internal__primitive.hitTest?.(x, y) ?? null;
    }
}
export class PanePrimitiveWrapper extends PrimitiveWrapper {
    _internal_labelPaneViews() {
        return [];
    }
}

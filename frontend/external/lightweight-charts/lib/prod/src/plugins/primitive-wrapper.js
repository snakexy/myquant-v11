export class PrimitiveWrapper {
    constructor(primitive, options) {
        this._internal__primitive = primitive;
        this._internal__options = options;
    }
    _internal_detach() {
        this._internal__primitive.detached?.();
    }
    _internal__attachToPrimitive(params) {
        this._internal__primitive.attached?.(params);
    }
    _internal__requestUpdate() {
        this._internal__primitive.updateAllViews?.();
    }
}

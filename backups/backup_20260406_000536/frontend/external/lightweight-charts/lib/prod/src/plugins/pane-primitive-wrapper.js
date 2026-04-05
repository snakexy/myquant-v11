export class PanePrimitiveWrapper {
    constructor(pane, primitive) {
        this._private__pane = pane;
        this._private__primitive = primitive;
        this._private__attach();
    }
    detach() {
        this._private__pane.detachPrimitive(this._private__primitive);
    }
    getPane() {
        return this._private__pane;
    }
    applyOptions(options) {
        this._private__primitive._internal_applyOptions?.(options);
    }
    _private__attach() {
        this._private__pane.attachPrimitive(this._private__primitive);
    }
}

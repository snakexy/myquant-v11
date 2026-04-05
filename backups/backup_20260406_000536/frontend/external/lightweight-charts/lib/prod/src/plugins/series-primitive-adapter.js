export class SeriesPrimitiveAdapter {
    constructor(series, primitive) {
        this._internal__series = series;
        this._internal__primitive = primitive;
        this._private__attach();
    }
    detach() {
        this._internal__series.detachPrimitive(this._internal__primitive);
    }
    getSeries() {
        return this._internal__series;
    }
    applyOptions(options) {
        if (this._internal__primitive && this._internal__primitive._internal_applyOptions) {
            this._internal__primitive._internal_applyOptions(options);
        }
    }
    _private__attach() {
        this._internal__series.attachPrimitive(this._internal__primitive);
    }
}

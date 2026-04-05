import { assert } from '../helpers/assertions';
import { PriceScaleApi } from './price-scale-api';
export class PaneApi {
    constructor(chartWidget, seriesApiGetter, pane, chartApi) {
        this._private__chartWidget = chartWidget;
        this._private__pane = pane;
        this._private__seriesApiGetter = seriesApiGetter;
        this._internal__chartApi = chartApi;
    }
    getHeight() {
        return this._private__pane._internal_height();
    }
    setHeight(height) {
        const chartModel = this._private__chartWidget._internal_model();
        const paneIndex = chartModel._internal_getPaneIndex(this._private__pane);
        chartModel._internal_changePanesHeight(paneIndex, height);
    }
    getStretchFactor() {
        return this._private__pane._internal_stretchFactor();
    }
    setStretchFactor(stretchFactor) {
        this._private__pane._internal_setStretchFactor(stretchFactor);
        this._private__chartWidget._internal_model()._internal_fullUpdate();
    }
    paneIndex() {
        return this._private__chartWidget._internal_model()._internal_getPaneIndex(this._private__pane);
    }
    moveTo(paneIndex) {
        const currentIndex = this.paneIndex();
        if (currentIndex === paneIndex) {
            return;
        }
        assert(paneIndex >= 0 && paneIndex < this._private__chartWidget._internal_paneWidgets().length, 'Invalid pane index');
        this._private__chartWidget._internal_model()._internal_movePane(currentIndex, paneIndex);
    }
    getSeries() {
        return this._private__pane._internal_series().map((source) => this._private__seriesApiGetter(source)) ?? [];
    }
    getHTMLElement() {
        const widgets = this._private__chartWidget._internal_paneWidgets();
        if (!widgets || widgets.length === 0 || !widgets[this.paneIndex()]) {
            return null;
        }
        return widgets[this.paneIndex()]._internal_getElement();
    }
    attachPrimitive(primitive) {
        this._private__pane._internal_attachPrimitive(primitive);
        if (primitive.attached) {
            primitive.attached({
                chart: this._internal__chartApi,
                requestUpdate: () => this._private__pane._internal_model()._internal_fullUpdate(),
            });
        }
    }
    detachPrimitive(primitive) {
        this._private__pane._internal_detachPrimitive(primitive);
    }
    priceScale(priceScaleId) {
        const priceScale = this._private__pane._internal_priceScaleById(priceScaleId);
        if (priceScale === null) {
            throw new Error(`Cannot find price scale with id: ${priceScaleId}`);
        }
        return new PriceScaleApi(this._private__chartWidget, priceScaleId, this.paneIndex());
    }
    setPreserveEmptyPane(preserve) {
        this._private__pane._internal_setPreserveEmptyPane(preserve);
    }
    preserveEmptyPane() {
        return this._private__pane._internal_preserveEmptyPane();
    }
    addCustomSeries(customPaneView, options = {}, paneIndex = 0) {
        return this._internal__chartApi.addCustomSeries(customPaneView, options, paneIndex);
    }
    addSeries(definition, options = {}) {
        return this._internal__chartApi.addSeries(definition, options, this.paneIndex());
    }
}

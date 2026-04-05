import { makeFont } from '../../helpers/make-font';
import { TextWatermarkRenderer, } from './pane-renderer';
export class TextWatermarkPaneView {
    constructor(options) {
        this._private__options = buildRendererOptions(options);
    }
    _internal_update(options) {
        this._private__options = buildRendererOptions(options);
    }
    renderer() {
        return new TextWatermarkRenderer(this._private__options);
    }
}
function buildRendererLineOptions(lineOption) {
    return {
        ...lineOption,
        _internal_font: makeFont(lineOption.fontSize, lineOption.fontFamily, lineOption.fontStyle),
        lineHeight: lineOption.lineHeight || lineOption.fontSize * 1.2,
        _internal_vertOffset: 0,
        _internal_zoom: 0,
    };
}
function buildRendererOptions(options) {
    return {
        ...options,
        lines: options.lines.map(buildRendererLineOptions),
    };
}

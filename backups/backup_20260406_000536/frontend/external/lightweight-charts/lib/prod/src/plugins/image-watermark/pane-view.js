import { ImageWatermarkRenderer, } from './pane-renderer';
export class ImageWatermarkPaneView {
    constructor(options) {
        this._private__image = null;
        this._private__imageWidth = 0; // don't draw until loaded
        this._private__imageHeight = 0;
        this._private__options = options;
        this._private__rendererOptions = buildRendererOptions(this._private__options, this._private__image, this._private__imageWidth, this._private__imageHeight);
    }
    _internal_stateUpdate(state) {
        if (state._internal_imageWidth !== undefined) {
            this._private__imageWidth = state._internal_imageWidth;
        }
        if (state._internal_imageHeight !== undefined) {
            this._private__imageHeight = state._internal_imageHeight;
        }
        if (state._internal_image !== undefined) {
            this._private__image = state._internal_image;
        }
        this._internal_update();
    }
    _internal_optionsUpdate(options) {
        this._private__options = options;
        this._internal_update();
    }
    zOrder() {
        return 'bottom';
    }
    _internal_update() {
        this._private__rendererOptions = buildRendererOptions(this._private__options, this._private__image, this._private__imageWidth, this._private__imageHeight);
    }
    renderer() {
        return new ImageWatermarkRenderer(this._private__rendererOptions);
    }
}
function buildRendererOptions(options, imgElement, imgWidth, imgHeight) {
    return {
        ...options,
        _internal_imgElement: imgElement,
        _internal_imgWidth: imgWidth,
        _internal_imgHeight: imgHeight,
    };
}

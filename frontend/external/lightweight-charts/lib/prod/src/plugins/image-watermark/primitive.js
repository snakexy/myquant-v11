import { PanePrimitiveWrapper } from '../pane-primitive-wrapper';
import { imageWatermarkOptionsDefaults, } from './options';
import { ImageWatermarkPaneView } from './pane-view';
function mergeOptionsWithDefaults(options) {
    return {
        ...imageWatermarkOptionsDefaults,
        ...options,
    };
}
class ImageWatermark {
    constructor(imageUrl, options) {
        this._private__imgElement = null;
        this._private__imageUrl = imageUrl;
        this._private__options = mergeOptionsWithDefaults(options);
        this._private__paneViews = [new ImageWatermarkPaneView(this._private__options)];
    }
    updateAllViews() {
        this._private__paneViews.forEach((pw) => pw._internal_update());
    }
    paneViews() {
        return this._private__paneViews;
    }
    attached(attachedParams) {
        const { requestUpdate } = attachedParams;
        this._private__requestUpdate = requestUpdate;
        this._private__imgElement = new Image();
        this._private__imgElement.onload = () => {
            const imageHeight = this._private__imgElement?.naturalHeight ?? 1;
            const imageWidth = this._private__imgElement?.naturalWidth ?? 1;
            this._private__paneViews.forEach((pv) => pv._internal_stateUpdate({
                _internal_imageHeight: imageHeight,
                _internal_imageWidth: imageWidth,
                _internal_image: this._private__imgElement,
            }));
            if (this._private__requestUpdate) {
                this._private__requestUpdate();
            }
        };
        this._private__imgElement.src = this._private__imageUrl;
    }
    detached() {
        this._private__requestUpdate = undefined;
        this._private__imgElement = null;
    }
    _internal_applyOptions(options) {
        this._private__options = mergeOptionsWithDefaults({ ...this._private__options, ...options });
        this._private__updateOptions();
        if (this._internal_requestUpdate) {
            this._internal_requestUpdate();
        }
    }
    _internal_requestUpdate() {
        if (this._private__requestUpdate) {
            this._private__requestUpdate();
        }
    }
    _private__updateOptions() {
        this._private__paneViews.forEach((pw) => pw._internal_optionsUpdate(this._private__options));
    }
}
/**
 * Creates an image watermark.
 *
 * @param pane - Target pane.
 * @param imageUrl - Image URL.
 * @param options - Watermark options.
 *
 * @returns Image watermark wrapper.
 *
 * @example
 * ```js
 * import { createImageWatermark } from 'lightweight-charts';
 *
 * const firstPane = chart.panes()[0];
 * const imageWatermark = createImageWatermark(firstPane, '/images/my-image.png', {
 *   alpha: 0.5,
 *   padding: 20,
 * });
 * // to change options
 * imageWatermark.applyOptions({ padding: 10 });
 * // to remove watermark from the pane
 * imageWatermark.detach();
 * ```
 */
export function createImageWatermark(pane, imageUrl, options) {
    return new PanePrimitiveWrapper(pane, new ImageWatermark(imageUrl, options));
}

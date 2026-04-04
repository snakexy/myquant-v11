import { PanePrimitiveWrapper } from '../pane-primitive-wrapper';
import { textWatermarkLineOptionsDefaults, textWatermarkOptionsDefaults, } from './options';
import { TextWatermarkPaneView } from './pane-view';
function mergeLineOptionsWithDefaults(options) {
    return {
        ...textWatermarkLineOptionsDefaults,
        ...options,
    };
}
function mergeOptionsWithDefaults(options) {
    return {
        ...textWatermarkOptionsDefaults,
        ...options,
        lines: options.lines?.map(mergeLineOptionsWithDefaults) ?? [],
    };
}
class TextWatermark {
    constructor(options) {
        this._private__options = mergeOptionsWithDefaults(options);
        this._private__paneViews = [new TextWatermarkPaneView(this._private__options)];
    }
    updateAllViews() {
        this._private__paneViews.forEach((pw) => pw._internal_update(this._private__options));
    }
    paneViews() {
        return this._private__paneViews;
    }
    attached({ requestUpdate }) {
        this._internal_requestUpdate = requestUpdate;
    }
    detached() {
        this._internal_requestUpdate = undefined;
    }
    _internal_applyOptions(options) {
        this._private__options = mergeOptionsWithDefaults({ ...this._private__options, ...options });
        if (this._internal_requestUpdate) {
            this._internal_requestUpdate();
        }
    }
}
/**
 * Creates an image watermark.
 *
 * @param pane - Target pane.
 * @param options - Watermark options.
 *
 * @returns Image watermark wrapper.
 *
 * @example
 * ```js
 * import { createTextWatermark } from 'lightweight-charts';
 *
 * const firstPane = chart.panes()[0];
 * const textWatermark = createTextWatermark(firstPane, {
 * 	  horzAlign: 'center',
 * 	  vertAlign: 'center',
 * 	  lines: [
 * 	    {
 * 	      text: 'Hello',
 * 	      color: 'rgba(255,0,0,0.5)',
 * 	      fontSize: 100,
 * 	      fontStyle: 'bold',
 * 	    },
 * 	    {
 * 	      text: 'This is a text watermark',
 * 	      color: 'rgba(0,0,255,0.5)',
 * 	      fontSize: 50,
 * 	      fontStyle: 'italic',
 * 	      fontFamily: 'monospace',
 * 	    },
 * 	  ],
 * });
 * // to change options
 * textWatermark.applyOptions({ horzAlign: 'left' });
 * // to remove watermark from the pane
 * textWatermark.detach();
 * ```
 */
export function createTextWatermark(pane, options) {
    return new PanePrimitiveWrapper(pane, new TextWatermark(options));
}

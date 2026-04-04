import { IPaneApi } from '../../api/ipane-api';
import { DeepPartial } from '../../helpers/strict-type-checks';
import { IPanePrimitiveWrapper } from '../pane-primitive-wrapper';
import { PrimitiveHasApplyOptions } from '../types';
import { TextWatermarkOptions } from './options';
export type ITextWatermarkPluginApi<T> = PrimitiveHasApplyOptions<IPanePrimitiveWrapper<T, TextWatermarkOptions>>;
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
export declare function createTextWatermark<T>(pane: IPaneApi<T>, options: DeepPartial<TextWatermarkOptions>): ITextWatermarkPluginApi<T>;

import { IPaneApi } from '../../api/ipane-api';
import { DeepPartial } from '../../helpers/strict-type-checks';
import { IPanePrimitiveWrapper } from '../pane-primitive-wrapper';
import { PrimitiveHasApplyOptions } from '../types';
import { ImageWatermarkOptions } from './options';
export type IImageWatermarkPluginApi<T> = PrimitiveHasApplyOptions<IPanePrimitiveWrapper<T, ImageWatermarkOptions>>;
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
export declare function createImageWatermark<T>(pane: IPaneApi<T>, imageUrl: string, options: DeepPartial<ImageWatermarkOptions>): IImageWatermarkPluginApi<T>;

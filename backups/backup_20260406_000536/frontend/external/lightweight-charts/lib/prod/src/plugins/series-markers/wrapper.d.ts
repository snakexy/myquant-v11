import { ISeriesApi } from '../../api/iseries-api';
import { DeepPartial } from '../../helpers/strict-type-checks';
import { SeriesType } from '../../model/series-options';
import { ISeriesPrimitiveWrapper } from '../series-primitive-adapter';
import { SeriesMarkersOptions } from './options';
import { SeriesMarker } from './types';
/**
 * Interface for a series markers plugin
 */
export interface ISeriesMarkersPluginApi<HorzScaleItem> extends ISeriesPrimitiveWrapper<HorzScaleItem> {
    /**
     * Set markers to the series.
     * @param markers - An array of markers to be displayed on the series.
     */
    setMarkers: (markers: SeriesMarker<HorzScaleItem>[]) => void;
    /**
     * Returns current markers.
     */
    markers: () => readonly SeriesMarker<HorzScaleItem>[];
    /**
     * Detaches the plugin from the series.
     */
    detach: () => void;
}
/**
 * A function to create a series markers primitive.
 *
 * @param series - The series to which the primitive will be attached.
 *
 * @param markers - An array of markers to be displayed on the series.
 *
 * @param options - Options for the series markers plugin.
 *
 * @example
 * ```js
 * import { createSeriesMarkers } from 'lightweight-charts';
 *
 *	const seriesMarkers = createSeriesMarkers(
 *		series,
 *		[
 *			{
 *				color: 'green',
 *				position: 'inBar',
 * 				shape: 'arrowDown',
 *				time: 1556880900,
 *			},
 *		]
 *	);
 *  // and then you can modify the markers
 *  // set it to empty array to remove all markers
 *  seriesMarkers.setMarkers([]);
 *
 *  // `seriesMarkers.markers()` returns current markers
 * ```
 */
export declare function createSeriesMarkers<HorzScaleItem>(series: ISeriesApi<SeriesType, HorzScaleItem>, markers?: SeriesMarker<HorzScaleItem>[], options?: DeepPartial<SeriesMarkersOptions>): ISeriesMarkersPluginApi<HorzScaleItem>;

import { CustomData, ICustomSeriesPaneView } from '../icustom-series';
import { CustomSeriesOptions, CustomStyleOptions } from '../series-options';
import { SeriesDefinition } from './series-def';
export declare const customStyleDefaults: CustomStyleOptions;
export declare const createCustomSeriesDefinition: <HorzScaleItem, TData extends CustomData<HorzScaleItem> = CustomData<HorzScaleItem>, TSeriesOptions extends CustomSeriesOptions = CustomSeriesOptions>(paneView: ICustomSeriesPaneView<HorzScaleItem, TData, TSeriesOptions>) => SeriesDefinition<"Custom">;

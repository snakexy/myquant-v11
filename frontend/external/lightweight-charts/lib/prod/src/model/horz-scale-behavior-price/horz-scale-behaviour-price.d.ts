import { Mutable } from '../../helpers/mutable';
import { ChartOptionsImpl } from '../chart-model';
import { SeriesDataItemTypeMap } from '../data-consumer';
import { DataItem, HorzScaleItemConverterToInternalObj, IHorzScaleBehavior, InternalHorzScaleItem, InternalHorzScaleItemKey } from '../ihorz-scale-behavior';
import { LocalizationOptions } from '../localization-options';
import { SeriesType } from '../series-options';
import { TickMark } from '../tick-marks';
import { TickMarkWeightValue, TimeScalePoint } from '../time-data';
import { TimeMark } from '../time-scale';
import { PriceChartLocalizationOptions } from './options';
import { HorzScalePriceItem } from './types';
export declare class HorzScaleBehaviorPrice implements IHorzScaleBehavior<HorzScalePriceItem> {
    private _options;
    options(): ChartOptionsImpl<HorzScalePriceItem>;
    setOptions(options: ChartOptionsImpl<HorzScalePriceItem>): void;
    preprocessData(data: DataItem<HorzScalePriceItem> | DataItem<HorzScalePriceItem>[]): void;
    updateFormatter(options: PriceChartLocalizationOptions): void;
    createConverterToInternalObj(data: SeriesDataItemTypeMap<HorzScalePriceItem>[SeriesType][]): HorzScaleItemConverterToInternalObj<HorzScalePriceItem>;
    key(internalItem: InternalHorzScaleItem | HorzScalePriceItem): InternalHorzScaleItemKey;
    cacheKey(internalItem: InternalHorzScaleItem): number;
    convertHorzItemToInternal(item: HorzScalePriceItem): InternalHorzScaleItem;
    formatHorzItem(item: InternalHorzScaleItem): string;
    formatTickmark(item: TickMark, localizationOptions: LocalizationOptions<HorzScalePriceItem>): string;
    maxTickMarkWeight(marks: TimeMark[]): TickMarkWeightValue;
    fillWeightsForPoints(sortedTimePoints: readonly Mutable<TimeScalePoint>[], startIndex: number): void;
    private _precision;
}

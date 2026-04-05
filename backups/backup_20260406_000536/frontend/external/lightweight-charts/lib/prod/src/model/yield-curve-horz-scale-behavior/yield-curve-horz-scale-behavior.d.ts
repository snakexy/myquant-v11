import { ISubscription } from '../../helpers/isubscription';
import { Mutable } from '../../helpers/mutable';
import { SeriesDataItemTypeMap } from '../data-consumer';
import { DataItem, HorzScaleItemConverterToInternalObj, IHorzScaleBehavior, InternalHorzScaleItem, InternalHorzScaleItemKey } from '../ihorz-scale-behavior';
import { LocalizationOptions } from '../localization-options';
import { SeriesType } from '../series-options';
import { TickMark } from '../tick-marks';
import { TickMarkWeightValue, TimeScalePoint } from '../time-data';
import { TimeMark } from '../time-scale';
import { YieldCurveChartOptions } from './yield-curve-chart-options';
export declare class YieldCurveHorzScaleBehavior implements IHorzScaleBehavior<number> {
    private _options;
    private readonly _pointsChangedDelegate;
    private _invalidateWhitespace;
    private _largestIndex;
    /** Data changes might require that the whitespace be generated again */
    whitespaceInvalidated(): ISubscription<number>;
    destroy(): void;
    options(): YieldCurveChartOptions;
    setOptions(options: YieldCurveChartOptions): void;
    preprocessData(data: DataItem<number> | DataItem<number>[]): void;
    updateFormatter(options: LocalizationOptions<number>): void;
    createConverterToInternalObj(data: SeriesDataItemTypeMap<number>[SeriesType][]): HorzScaleItemConverterToInternalObj<number>;
    key(internalItem: InternalHorzScaleItem | number): InternalHorzScaleItemKey;
    cacheKey(internalItem: InternalHorzScaleItem): number;
    convertHorzItemToInternal(item: number): InternalHorzScaleItem;
    formatHorzItem(item: InternalHorzScaleItem): string;
    formatTickmark(item: TickMark): string;
    maxTickMarkWeight(marks: TimeMark[]): TickMarkWeightValue;
    fillWeightsForPoints(sortedTimePoints: readonly Mutable<TimeScalePoint>[], startIndex: number): void;
    private _formatTime;
}

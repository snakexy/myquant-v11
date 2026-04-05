import { TimePoint } from './horz-scale-behavior-time/types';
import { CustomConflationReducer } from './icustom-series';
import { SeriesPlotRow } from './series-data';
import { SeriesType } from './series-options';
import { TimePointIndex } from './time-data';
/**
 * Represents a conflated chunk of data points with remainder handling.
 */
export interface ConflatedChunk {
    startIndex: TimePointIndex;
    endIndex: TimePointIndex;
    startTime: TimePoint;
    endTime: TimePoint;
    open: number;
    high: number;
    low: number;
    close: number;
    data?: unknown;
    originalDataCount: number;
    conflatedData?: unknown;
    isRemainder?: boolean;
}
export declare class DataConflater<T extends SeriesType, HorzScaleItem = unknown> {
    private _dataCache;
    calculateConflationLevelWithSmoothing(barSpacing: number, devicePixelRatio: number, smoothingFactor: number): number;
    conflateByFactor(data: readonly SeriesPlotRow<T>[], barsToMerge: number, customReducer?: CustomConflationReducer<HorzScaleItem>, isCustomSeries?: boolean, priceValueBuilder?: (item: unknown) => number[]): readonly SeriesPlotRow<T>[];
    /**
     * Efficiently update the last conflated chunk when new data arrives.
     * This avoids rebuilding all chunks when just the last data point changes.
     */
    updateLastConflatedChunk(originalData: readonly SeriesPlotRow<T>[], newLastRow: SeriesPlotRow<T>, conflationLevel: number, customReducer?: CustomConflationReducer<HorzScaleItem>, isCustomSeries?: boolean, priceValueBuilder?: (item: unknown) => number[]): readonly SeriesPlotRow<T>[];
    private _normalizeConflationLevel;
    private _getDataVersion;
    /**
     * Build conflation recursively, reusing previous level results.
     */
    private _buildRecursively;
    /**
     * Build a conflation level directly from original data (used for level 2).
     */
    private _buildLevelFromOriginal;
    /**
     * Build a conflation level from the previous level's result.
     */
    private _buildLevelFromPrevious;
    private _buildChunksFromData;
    private _sumCount;
    private _mergeTwoRows;
    private _mergeChunkAndRow;
    private _mergeRangeWithOverride;
    private _convertToContext;
    private _chunkToSeriesPlotRow;
    private _chunksToSeriesPlotRows;
    /**
     * Update only the last chunk in cached conflated data efficiently.
     */
    private _updateLastChunkInCache;
    private _plotRowToChunk;
    private _getValidatedCacheEntry;
    private _ensureCacheEntry;
}

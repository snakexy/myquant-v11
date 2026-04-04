import { CONFLATION_LEVELS, DPR_CONFLATION_THRESHOLD, MAX_CONFLATION_LEVEL } from './conflation/constants';
export class DataConflater {
    constructor() {
        this._private__dataCache = new WeakMap();
    }
    _internal_calculateConflationLevelWithSmoothing(barSpacing, devicePixelRatio, smoothingFactor) {
        const conflationThreshold = (DPR_CONFLATION_THRESHOLD / devicePixelRatio) * smoothingFactor;
        if (barSpacing >= conflationThreshold) {
            return 1;
        }
        // calculate conflation level as power of 2
        const ratio = conflationThreshold / barSpacing;
        const conflationLevel = Math.pow(2, Math.floor(Math.log2(ratio)));
        // ensure we don't exceed maximum conflation level
        return Math.min(conflationLevel, MAX_CONFLATION_LEVEL);
    }
    _internal_conflateByFactor(data, barsToMerge, customReducer, isCustomSeries = false, priceValueBuilder) {
        if (data.length === 0 || barsToMerge <= 1) {
            return data;
        }
        const conflationLevel = this._private__normalizeConflationLevel(barsToMerge);
        if (conflationLevel <= 1) {
            return data;
        }
        const entry = this._private__getValidatedCacheEntry(data);
        let cachedRows = entry._internal_levelResults.get(conflationLevel);
        if (cachedRows !== undefined) {
            return cachedRows;
        }
        cachedRows = this._private__buildRecursively(data, conflationLevel, customReducer, isCustomSeries, priceValueBuilder, entry._internal_levelResults);
        entry._internal_levelResults.set(conflationLevel, cachedRows);
        return cachedRows;
    }
    /**
     * Efficiently update the last conflated chunk when new data arrives.
     * This avoids rebuilding all chunks when just the last data point changes.
     */
    _internal_updateLastConflatedChunk(originalData, newLastRow, conflationLevel, customReducer, isCustomSeries = false, priceValueBuilder) {
        if (conflationLevel < 1 || originalData.length === 0) {
            return originalData;
        }
        const entry = this._private__getValidatedCacheEntry(originalData);
        const cachedRows = entry._internal_levelResults.get(conflationLevel);
        if (!cachedRows) {
            return this._internal_conflateByFactor(originalData, conflationLevel, customReducer, isCustomSeries, priceValueBuilder);
        }
        const updatedRows = this._private__updateLastChunkInCache(originalData, newLastRow, conflationLevel, cachedRows, isCustomSeries, customReducer, priceValueBuilder);
        entry._internal_levelResults.set(conflationLevel, updatedRows);
        return updatedRows;
    }
    _private__normalizeConflationLevel(barsToMerge) {
        if (barsToMerge <= 2) {
            return 2;
        }
        for (const level of CONFLATION_LEVELS) {
            if (barsToMerge <= level) {
                return level;
            }
        }
        return MAX_CONFLATION_LEVEL;
    }
    _private__getDataVersion(data) {
        if (data.length === 0) {
            return 0;
        }
        // Simple hash based on data length and first/last items
        const first = data[0];
        const last = data[data.length - 1];
        return data.length * 31 + first._internal_index * 17 + last._internal_index * 13;
    }
    /**
     * Build conflation recursively, reusing previous level results.
     */
    _private__buildRecursively(data, targetLevel, customReducer, isCustomSeries = false, priceValueBuilder, levelResults = new Map()) {
        if (targetLevel === 2) {
            return this._private__buildLevelFromOriginal(data, 2, customReducer, isCustomSeries, priceValueBuilder);
        }
        const prevLevel = targetLevel / 2;
        let prevData = levelResults.get(prevLevel);
        if (!prevData) {
            prevData = this._private__buildRecursively(data, prevLevel, customReducer, isCustomSeries, priceValueBuilder, levelResults);
            levelResults.set(prevLevel, prevData);
        }
        return this._private__buildLevelFromPrevious(prevData, customReducer, isCustomSeries, priceValueBuilder);
    }
    /**
     * Build a conflation level directly from original data (used for level 2).
     */
    _private__buildLevelFromOriginal(data, level, customReducer, isCustomSeries = false, priceValueBuilder) {
        const chunks = this._private__buildChunksFromData(data, level, customReducer, isCustomSeries, priceValueBuilder);
        return this._private__chunksToSeriesPlotRows(chunks, isCustomSeries);
    }
    /**
     * Build a conflation level from the previous level's result.
     */
    _private__buildLevelFromPrevious(prevData, customReducer, isCustomSeries = false, priceValueBuilder) {
        // Always merge 2 chunks from the previous level
        const chunks = this._private__buildChunksFromData(prevData, 2, customReducer, isCustomSeries, priceValueBuilder);
        return this._private__chunksToSeriesPlotRows(chunks, isCustomSeries);
    }
    _private__buildChunksFromData(data, mergeFactor, customReducer, isCustomSeries = false, priceValueBuilder) {
        const chunks = [];
        for (let i = 0; i < data.length; i += mergeFactor) {
            const remaining = data.length - i;
            if (remaining >= mergeFactor) {
                const merged = this._private__mergeTwoRows(data[i], data[i + 1], customReducer, isCustomSeries, priceValueBuilder);
                merged._internal_isRemainder = false;
                chunks.push(merged);
            }
            else {
                // remainder of 1 -> fold into previous chunk if possible
                if (chunks.length === 0) {
                    chunks.push(this._private__plotRowToChunk(data[i], true));
                }
                else {
                    const prev = chunks[chunks.length - 1];
                    chunks[chunks.length - 1] = this._private__mergeChunkAndRow(prev, data[i], customReducer, isCustomSeries, priceValueBuilder);
                }
            }
        }
        return chunks;
    }
    _private__sumCount(a, b) {
        return (a ?? 1) + (b ?? 1);
    }
    _private__mergeTwoRows(a, b, customReducer, isCustomSeries = false, priceValueBuilder) {
        if (!isCustomSeries || !customReducer || !priceValueBuilder) {
            const high = a._internal_value[1 /* PlotRowValueIndex.High */] > b._internal_value[1 /* PlotRowValueIndex.High */] ? a._internal_value[1 /* PlotRowValueIndex.High */] : b._internal_value[1 /* PlotRowValueIndex.High */];
            const low = a._internal_value[2 /* PlotRowValueIndex.Low */] < b._internal_value[2 /* PlotRowValueIndex.Low */] ? a._internal_value[2 /* PlotRowValueIndex.Low */] : b._internal_value[2 /* PlotRowValueIndex.Low */];
            return {
                _internal_startIndex: a._internal_index,
                _internal_endIndex: b._internal_index,
                _internal_startTime: a._internal_time,
                _internal_endTime: b._internal_time,
                _internal_open: a._internal_value[0 /* PlotRowValueIndex.Open */],
                _internal_high: high,
                _internal_low: low,
                _internal_close: b._internal_value[3 /* PlotRowValueIndex.Close */],
                _internal_originalDataCount: this._private__sumCount(a._internal_originalDataCount, b._internal_originalDataCount),
                _internal_conflatedData: undefined,
                _internal_isRemainder: false,
            };
        }
        const c1 = this._private__convertToContext(a, priceValueBuilder);
        const c2 = this._private__convertToContext(b, priceValueBuilder);
        const aggregated = customReducer(c1, c2);
        const prices = priceValueBuilder(aggregated);
        const p = prices.length ? prices[prices.length - 1] : 0;
        return {
            _internal_startIndex: a._internal_index,
            _internal_endIndex: b._internal_index,
            _internal_startTime: a._internal_time,
            _internal_endTime: b._internal_time,
            _internal_open: a._internal_value[0 /* PlotRowValueIndex.Open */],
            _internal_high: Math.max(a._internal_value[1 /* PlotRowValueIndex.High */], p),
            _internal_low: Math.min(a._internal_value[2 /* PlotRowValueIndex.Low */], p),
            _internal_close: p,
            _internal_originalDataCount: this._private__sumCount(a._internal_originalDataCount, b._internal_originalDataCount),
            _internal_conflatedData: aggregated,
            _internal_isRemainder: false,
        };
    }
    _private__mergeChunkAndRow(chunk, row, customReducer, isCustomSeries = false, priceValueBuilder) {
        if (!isCustomSeries || !customReducer || !priceValueBuilder) {
            return {
                _internal_startIndex: chunk._internal_startIndex,
                _internal_endIndex: row._internal_index,
                _internal_startTime: chunk._internal_startTime,
                _internal_endTime: row._internal_time,
                _internal_open: chunk._internal_open,
                _internal_high: chunk._internal_high > row._internal_value[1 /* PlotRowValueIndex.High */] ? chunk._internal_high : row._internal_value[1 /* PlotRowValueIndex.High */],
                _internal_low: chunk._internal_low < row._internal_value[2 /* PlotRowValueIndex.Low */] ? chunk._internal_low : row._internal_value[2 /* PlotRowValueIndex.Low */],
                _internal_close: row._internal_value[3 /* PlotRowValueIndex.Close */],
                _internal_originalDataCount: chunk._internal_originalDataCount + (row._internal_originalDataCount ?? 1),
                _internal_conflatedData: chunk._internal_conflatedData,
                _internal_isRemainder: false,
            };
        }
        const prevAgg = chunk._internal_conflatedData;
        const ctx = this._private__convertToContext(row, priceValueBuilder);
        // if prevAgg is missing (e.g single-item remainder chunk)
        // treat the row as the first aggregate seed to avoid calling builder on undefined.
        const prevCtx = prevAgg
            ? {
                data: prevAgg,
                index: chunk._internal_startIndex,
                originalTime: chunk._internal_startTime,
                time: chunk._internal_startTime,
                priceValues: priceValueBuilder(prevAgg),
            }
            : null;
        const aggregated = prevCtx ? customReducer(prevCtx, ctx) : (ctx.data);
        const prices = prevCtx ? priceValueBuilder(aggregated) : ctx.priceValues;
        const p = prices.length ? prices[prices.length - 1] : 0;
        return {
            _internal_startIndex: chunk._internal_startIndex,
            _internal_endIndex: row._internal_index,
            _internal_startTime: chunk._internal_startTime,
            _internal_endTime: row._internal_time,
            _internal_open: chunk._internal_open,
            _internal_high: Math.max(chunk._internal_high, p),
            _internal_low: Math.min(chunk._internal_low, p),
            _internal_close: p,
            _internal_originalDataCount: chunk._internal_originalDataCount + (row._internal_originalDataCount ?? 1),
            _internal_conflatedData: aggregated,
            _internal_isRemainder: false,
        };
    }
    // fold [start, end) with override at overrideIndex
    // eslint-disable-next-line max-params
    _private__mergeRangeWithOverride(data, start, end, overrideIndex, overrideRow, customReducer, isCustomSeries = false, priceValueBuilder) {
        const first = (start === overrideIndex) ? overrideRow : data[start];
        if (end - start === 1) {
            return this._private__plotRowToChunk(first, true);
        }
        const second = (start + 1 === overrideIndex) ? overrideRow : data[start + 1];
        let chunk = this._private__mergeTwoRows(first, second, customReducer, isCustomSeries, priceValueBuilder);
        for (let i = start + 2; i < end; i++) {
            const row = (i === overrideIndex) ? overrideRow : data[i];
            chunk = this._private__mergeChunkAndRow(chunk, row, customReducer, isCustomSeries, priceValueBuilder);
        }
        return chunk;
    }
    _private__convertToContext(item, priceValueBuilder) {
        const itemData = item._internal_data ?? {};
        return {
            data: item._internal_data,
            index: item._internal_index,
            originalTime: item._internal_originalTime,
            time: item._internal_time,
            priceValues: priceValueBuilder(itemData),
        };
    }
    _private__chunkToSeriesPlotRow(chunk, isCustomSeries = false) {
        const isCustom = isCustomSeries === true;
        const hasCustomData = !!chunk._internal_conflatedData;
        const base = {
            _internal_index: chunk._internal_startIndex,
            _internal_time: chunk._internal_startTime,
            _internal_originalTime: chunk._internal_startTime,
            _internal_value: [
                isCustom ? chunk._internal_close : chunk._internal_open,
                chunk._internal_high,
                chunk._internal_low,
                chunk._internal_close,
            ],
            _internal_originalDataCount: chunk._internal_originalDataCount,
        };
        const data = isCustom
            ? (hasCustomData ? chunk._internal_conflatedData : { _internal_time: chunk._internal_startTime })
            : undefined;
        return {
            ...base,
            _internal_data: data,
        };
    }
    _private__chunksToSeriesPlotRows(chunks, isCustomSeries = false) {
        return chunks.map((chunk) => this._private__chunkToSeriesPlotRow(chunk, isCustomSeries));
    }
    /**
     * Update only the last chunk in cached conflated data efficiently.
     */
    // eslint-disable-next-line max-params
    _private__updateLastChunkInCache(originalData, newLastRow, conflationLevel, cachedRows, isCustomSeries = false, customReducer, priceValueBuilder) {
        if (cachedRows.length === 0) {
            return cachedRows;
        }
        const lastOriginalIndex = originalData.length - 1;
        const chunkStartIndex = Math.floor(lastOriginalIndex / conflationLevel) * conflationLevel;
        const chunkEndIndex = Math.min(chunkStartIndex + conflationLevel, originalData.length);
        if (chunkEndIndex - chunkStartIndex < conflationLevel && originalData.length > conflationLevel) {
            // we must allocate a new array here to do a full rebuild.
            const newOriginalData = originalData.slice();
            newOriginalData[newOriginalData.length - 1] = newLastRow;
            return this._internal_conflateByFactor(newOriginalData, conflationLevel, customReducer, isCustomSeries, priceValueBuilder);
        }
        const lastChunkIndex = Math.floor((lastOriginalIndex - 1) / conflationLevel);
        const newChunkIndex = Math.floor(lastOriginalIndex / conflationLevel);
        if (lastChunkIndex === newChunkIndex || cachedRows.length === 1) {
            // Data length is within the same chunk OR it's the only chunk
            const actualEndIndex = Math.min(chunkStartIndex + conflationLevel, originalData.length);
            const count = actualEndIndex - chunkStartIndex;
            if (count <= 0) {
                // This can happen if originalData.length was 0, though we guard at the top.
                return cachedRows;
            }
            const mergedChunk = count === 1
                ? this._private__plotRowToChunk((chunkStartIndex === lastOriginalIndex) ? newLastRow : originalData[chunkStartIndex], /* isRemainder*/ true)
                : this._private__mergeRangeWithOverride(originalData, chunkStartIndex, actualEndIndex, lastOriginalIndex, newLastRow, customReducer, isCustomSeries, priceValueBuilder);
            // in-place update of the cached result: avoid allocating a new array
            cachedRows[cachedRows.length - 1] = this._private__chunkToSeriesPlotRow(mergedChunk, isCustomSeries);
            return cachedRows;
        }
        else {
            // update affects chunk structure
            // we must allocate a new array here to do a full rebuild.
            const newOriginalData = originalData.slice();
            newOriginalData[newOriginalData.length - 1] = newLastRow;
            return this._internal_conflateByFactor(newOriginalData, conflationLevel, customReducer, isCustomSeries, priceValueBuilder);
        }
    }
    _private__plotRowToChunk(item, isRemainder = false) {
        const chunk = {
            _internal_startIndex: item._internal_index,
            _internal_endIndex: item._internal_index,
            _internal_startTime: item._internal_time,
            _internal_endTime: item._internal_time,
            _internal_open: item._internal_value[0 /* PlotRowValueIndex.Open */],
            _internal_high: item._internal_value[1 /* PlotRowValueIndex.High */],
            _internal_low: item._internal_value[2 /* PlotRowValueIndex.Low */],
            _internal_close: item._internal_value[3 /* PlotRowValueIndex.Close */],
            _internal_originalDataCount: item._internal_originalDataCount ?? 1,
            _internal_conflatedData: item._internal_data,
            _internal_isRemainder: isRemainder,
        };
        return chunk;
    }
    _private__getValidatedCacheEntry(data) {
        const entry = this._private__ensureCacheEntry(data);
        const dataVersion = this._private__getDataVersion(data);
        if (entry._internal_version !== dataVersion) {
            entry._internal_levelResults.clear();
            entry._internal_version = dataVersion;
        }
        return entry;
    }
    _private__ensureCacheEntry(data) {
        let entry = this._private__dataCache.get(data);
        if (entry === undefined) {
            entry = {
                _internal_version: this._private__getDataVersion(data),
                _internal_levelResults: new Map(),
            };
            this._private__dataCache.set(data, entry);
        }
        return entry;
    }
}

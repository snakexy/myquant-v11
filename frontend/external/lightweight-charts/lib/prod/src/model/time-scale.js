import { lowerBound } from '../helpers/algorithms';
import { ensureNotNull } from '../helpers/assertions';
import { Delegate } from '../helpers/delegate';
import { clamp } from '../helpers/mathex';
import { isInteger, merge } from '../helpers/strict-type-checks';
import { FormattedLabelsCache } from './formatted-labels-cache';
import { areRangesEqual, RangeImpl } from './range-impl';
import { TickMarks } from './tick-marks';
import { TimeScaleVisibleRange } from './time-scale-visible-range';
const defaultTickMarkMaxCharacterLength = 8;
;
export function markWithGreaterWeight(a, b) {
    return a.weight > b.weight ? a : b;
}
export class TimeScale {
    constructor(model, options, localizationOptions, horzScaleBehavior) {
        this._private__width = 0;
        this._private__baseIndexOrNull = null;
        this._private__points = [];
        this._private__scrollStartPoint = null;
        this._private__scaleStartPoint = null;
        this._private__tickMarks = new TickMarks();
        this._private__formattedByWeight = new Map();
        this._private__visibleRange = TimeScaleVisibleRange._internal_invalid();
        this._private__visibleRangeInvalidated = true;
        this._private__visibleBarsChanged = new Delegate();
        this._private__logicalRangeChanged = new Delegate();
        this._private__optionsApplied = new Delegate();
        this._private__commonTransitionStartState = null;
        this._private__timeMarksCache = null;
        this._private__indicesWithData = new Map();
        this._private__indicesWithDataUpdateId = -1;
        this._private__labels = [];
        this._private__conflationFactor = 1;
        this._private__options = options;
        this._private__localizationOptions = localizationOptions;
        this._private__rightOffset = options.rightOffset;
        this._private__barSpacing = options.barSpacing;
        this._private__model = model;
        this._private__checkRightOffsetPixels(options);
        this._private__horzScaleBehavior = horzScaleBehavior;
        this._private__updateDateTimeFormatter();
        this._private__tickMarks._internal_setUniformDistribution(options.uniformDistribution);
        this._private__updateConflationFactor();
        this._internal_recalculateIndicesWithData();
    }
    _internal_options() {
        return this._private__options;
    }
    _internal_applyLocalizationOptions(localizationOptions) {
        merge(this._private__localizationOptions, localizationOptions);
        this._private__invalidateTickMarks();
        this._private__updateDateTimeFormatter();
    }
    _internal_applyOptions(options, localizationOptions) {
        merge(this._private__options, options);
        if (this._private__options.fixLeftEdge) {
            this._private__doFixLeftEdge();
        }
        if (this._private__options.fixRightEdge) {
            this._private__doFixRightEdge();
        }
        // note that bar spacing should be applied before right offset
        // because right offset depends on bar spacing
        if (options.barSpacing !== undefined) {
            this._private__model._internal_setBarSpacing(options.barSpacing);
        }
        if (options.rightOffset !== undefined) {
            this._private__model._internal_setRightOffset(options.rightOffset);
        }
        this._private__checkRightOffsetPixels(options);
        if (options.minBarSpacing !== undefined || options.maxBarSpacing !== undefined) {
            // yes, if we apply bar spacing constrains then we need to correct bar spacing
            // the easiest way is to apply it once again
            this._private__model._internal_setBarSpacing(options.barSpacing ?? this._private__barSpacing);
        }
        if (options.ignoreWhitespaceIndices !== undefined && options.ignoreWhitespaceIndices !== this._private__options.ignoreWhitespaceIndices) {
            this._internal_recalculateIndicesWithData();
        }
        this._private__invalidateTickMarks();
        this._private__updateDateTimeFormatter();
        // Recompute conflation factor when options that may affect it change
        if (options.enableConflation !== undefined || options.conflationThresholdFactor !== undefined) {
            this._private__updateConflationFactor();
        }
        this._private__optionsApplied._internal_fire();
    }
    _internal_indexToTime(index) {
        return this._private__points[index]?.time ?? null;
    }
    _internal_indexToTimeScalePoint(index) {
        return this._private__points[index] ?? null;
    }
    _internal_timeToIndex(time, findNearest) {
        if (this._private__points.length < 1) {
            // no time points available
            return null;
        }
        if (this._private__horzScaleBehavior.key(time) > this._private__horzScaleBehavior.key(this._private__points[this._private__points.length - 1].time)) {
            // special case
            return findNearest ? this._private__points.length - 1 : null;
        }
        const index = lowerBound(this._private__points, this._private__horzScaleBehavior.key(time), (a, b) => this._private__horzScaleBehavior.key(a.time) < b);
        if (this._private__horzScaleBehavior.key(time) < this._private__horzScaleBehavior.key(this._private__points[index].time)) {
            return findNearest ? index : null;
        }
        return index;
    }
    _internal_isEmpty() {
        return this._private__width === 0 || this._private__points.length === 0 || this._private__baseIndexOrNull === null;
    }
    _internal_hasPoints() {
        return this._private__points.length > 0;
    }
    // strict range: integer indices of the bars in the visible range rounded in more wide direction
    _internal_visibleStrictRange() {
        this._private__updateVisibleRange();
        return this._private__visibleRange._internal_strictRange();
    }
    _internal_visibleLogicalRange() {
        this._private__updateVisibleRange();
        return this._private__visibleRange._internal_logicalRange();
    }
    _internal_visibleTimeRange() {
        const visibleBars = this._internal_visibleStrictRange();
        if (visibleBars === null) {
            return null;
        }
        const range = {
            from: visibleBars._internal_left(),
            to: visibleBars._internal_right(),
        };
        return this._internal_timeRangeForLogicalRange(range);
    }
    _internal_timeRangeForLogicalRange(range) {
        const from = Math.round(range.from);
        const to = Math.round(range.to);
        const firstIndex = ensureNotNull(this._private__firstIndex());
        const lastIndex = ensureNotNull(this._private__lastIndex());
        return {
            from: ensureNotNull(this._internal_indexToTimeScalePoint(Math.max(firstIndex, from))),
            to: ensureNotNull(this._internal_indexToTimeScalePoint(Math.min(lastIndex, to))),
        };
    }
    _internal_logicalRangeForTimeRange(range) {
        return {
            from: ensureNotNull(this._internal_timeToIndex(range.from, true)),
            to: ensureNotNull(this._internal_timeToIndex(range.to, true)),
        };
    }
    _internal_width() {
        return this._private__width;
    }
    _internal_setWidth(newWidth) {
        if (!isFinite(newWidth) || newWidth <= 0) {
            return;
        }
        if (this._private__width === newWidth) {
            return;
        }
        // when we change the width and we need to correct visible range because of fixing left edge
        // we need to check the previous visible range rather than the new one
        // because it might be updated by changing width, bar spacing, etc
        // but we need to try to keep the same range
        const previousVisibleRange = this._internal_visibleLogicalRange();
        const oldWidth = this._private__width;
        this._private__width = newWidth;
        this._private__visibleRangeInvalidated = true;
        if (this._private__options.lockVisibleTimeRangeOnResize && oldWidth !== 0) {
            // recalculate bar spacing
            const newBarSpacing = this._private__barSpacing * newWidth / oldWidth;
            this._private__barSpacing = newBarSpacing;
        }
        // if time scale is scrolled to the end of data and we have fixed right edge
        // keep left edge instead of right
        // we need it to avoid "shaking" if the last bar visibility affects time scale width
        if (this._private__options.fixLeftEdge) {
            // note that logical left range means not the middle of a bar (it's the left border)
            if (previousVisibleRange !== null && previousVisibleRange._internal_left() <= 0) {
                const delta = oldWidth - newWidth;
                // reduce  _rightOffset means move right
                // we could move more than required - this will be fixed by _correctOffset()
                this._private__rightOffset -= Math.round(delta / this._private__barSpacing) + 1;
                this._private__visibleRangeInvalidated = true;
            }
        }
        // updating bar spacing should be first because right offset depends on it
        this._private__correctBarSpacing();
        this._private__correctOffset();
    }
    _internal_indexToCoordinate(index) {
        if (this._internal_isEmpty() || !isInteger(index)) {
            return 0;
        }
        const baseIndex = this._internal_baseIndex();
        const deltaFromRight = baseIndex + this._private__rightOffset - index;
        const coordinate = this._private__width - (deltaFromRight + 0.5) * this._private__barSpacing - 1;
        return coordinate;
    }
    _internal_indexesToCoordinates(points, visibleRange) {
        const baseIndex = this._internal_baseIndex();
        const indexFrom = (visibleRange === undefined) ? 0 : visibleRange.from;
        const indexTo = (visibleRange === undefined) ? points.length : visibleRange.to;
        for (let i = indexFrom; i < indexTo; i++) {
            const index = points[i]._internal_time;
            const deltaFromRight = baseIndex + this._private__rightOffset - index;
            const coordinate = this._private__width - (deltaFromRight + 0.5) * this._private__barSpacing - 1;
            points[i]._internal_x = coordinate;
        }
    }
    _internal_coordinateToIndex(x, considerIgnoreWhitespace) {
        const index = Math.ceil(this._private__coordinateToFloatIndex(x));
        if (!considerIgnoreWhitespace ||
            !this._private__options.ignoreWhitespaceIndices ||
            this._private__shouldConsiderIndex(index)) {
            return index;
        }
        return this._private__findNearestIndexWithData(index);
    }
    _internal_setRightOffset(offset) {
        this._private__visibleRangeInvalidated = true;
        this._private__rightOffset = offset;
        this._private__correctOffset();
        this._private__model._internal_recalculateAllPanes();
        this._private__model._internal_lightUpdate();
    }
    _internal_barSpacing() {
        return this._private__barSpacing;
    }
    _internal_setBarSpacing(newBarSpacing) {
        const oldBarSpacing = this._private__barSpacing;
        this._private__setBarSpacing(newBarSpacing);
        if (this._private__options.rightOffsetPixels !== undefined && oldBarSpacing !== 0) {
            // when in pixel mode, zooming should keep the pixel offset, so we need to
            // recalculate the bar offset.
            const newRightOffset = this._private__rightOffset * oldBarSpacing / this._private__barSpacing;
            this._private__rightOffset = newRightOffset;
        }
        // do not allow scroll out of visible bars
        this._private__correctOffset();
        this._private__model._internal_recalculateAllPanes();
        this._private__model._internal_lightUpdate();
    }
    _internal_rightOffset() {
        return this._private__rightOffset;
    }
    // eslint-disable-next-line complexity
    _internal_marks() {
        if (this._internal_isEmpty()) {
            return null;
        }
        if (this._private__timeMarksCache !== null) {
            return this._private__timeMarksCache;
        }
        const spacing = this._private__barSpacing;
        const fontSize = this._private__model._internal_options()['layout'].fontSize;
        const pixelsPer8Characters = (fontSize + 4) * 5;
        const pixelsPerCharacter = pixelsPer8Characters / defaultTickMarkMaxCharacterLength;
        const maxLabelWidth = pixelsPerCharacter * (this._private__options.tickMarkMaxCharacterLength || defaultTickMarkMaxCharacterLength);
        const indexPerLabel = Math.round(maxLabelWidth / spacing);
        const visibleBars = ensureNotNull(this._internal_visibleStrictRange());
        const firstBar = Math.max(visibleBars._internal_left(), visibleBars._internal_left() - indexPerLabel);
        const lastBar = Math.max(visibleBars._internal_right(), visibleBars._internal_right() - indexPerLabel);
        const items = this._private__tickMarks._internal_build(spacing, maxLabelWidth, this._private__options.ignoreWhitespaceIndices, this._private__indicesWithData, this._private__indicesWithDataUpdateId);
        // according to indexPerLabel value this value means "earliest index which _might be_ used as the second label on time scale"
        const earliestIndexOfSecondLabel = this._private__firstIndex() + indexPerLabel;
        // according to indexPerLabel value this value means "earliest index which _might be_ used as the second last label on time scale"
        const indexOfSecondLastLabel = this._private__lastIndex() - indexPerLabel;
        const isAllScalingAndScrollingDisabled = this._private__isAllScalingAndScrollingDisabled();
        const isLeftEdgeFixed = this._private__options.fixLeftEdge || isAllScalingAndScrollingDisabled;
        const isRightEdgeFixed = this._private__options.fixRightEdge || isAllScalingAndScrollingDisabled;
        let targetIndex = 0;
        for (const tm of items) {
            if (!(firstBar <= tm.index && tm.index <= lastBar)) {
                continue;
            }
            let label;
            if (targetIndex < this._private__labels.length) {
                label = this._private__labels[targetIndex];
                label.coord = this._internal_indexToCoordinate(tm.index);
                label.label = this._private__formatLabel(tm);
                label.weight = tm.weight;
            }
            else {
                label = {
                    needAlignCoordinate: false,
                    coord: this._internal_indexToCoordinate(tm.index),
                    label: this._private__formatLabel(tm),
                    weight: tm.weight,
                };
                this._private__labels.push(label);
            }
            if (this._private__barSpacing > (maxLabelWidth / 2) && !isAllScalingAndScrollingDisabled) {
                // if there is enough space then let's show all tick marks as usual
                label.needAlignCoordinate = false;
            }
            else {
                // if a user is able to scroll after a tick mark then show it as usual, otherwise the coordinate might be aligned
                // if the index is for the second (last) label or later (earlier) then most likely this label might be displayed without correcting the coordinate
                label.needAlignCoordinate = (isLeftEdgeFixed && tm.index <= earliestIndexOfSecondLabel) || (isRightEdgeFixed && tm.index >= indexOfSecondLastLabel);
            }
            targetIndex++;
        }
        this._private__labels.length = targetIndex;
        this._private__timeMarksCache = this._private__labels;
        return this._private__labels;
    }
    _internal_restoreDefault() {
        this._private__visibleRangeInvalidated = true;
        this._internal_setBarSpacing(this._private__options.barSpacing);
        let newOffset;
        if (this._private__options.rightOffsetPixels !== undefined) {
            newOffset = this._private__options.rightOffsetPixels / this._internal_barSpacing();
        }
        else {
            newOffset = this._private__options.rightOffset;
        }
        this._internal_setRightOffset(newOffset);
    }
    _internal_setBaseIndex(baseIndex) {
        this._private__visibleRangeInvalidated = true;
        this._private__baseIndexOrNull = baseIndex;
        this._private__correctOffset();
        this._private__doFixLeftEdge();
    }
    /**
     * Zoom in/out the scale around a `zoomPoint` on `scale` value.
     *
     * @param zoomPoint - X coordinate of the point to apply the zoom.
     * If `rightBarStaysOnScroll` option is disabled, then will be used to restore right offset.
     * @param scale - Zoom value (in 1/10 parts of current bar spacing).
     * Negative value means zoom out, positive - zoom in.
     */
    _internal_zoom(zoomPoint, scale) {
        const floatIndexAtZoomPoint = this._private__coordinateToFloatIndex(zoomPoint);
        const barSpacing = this._internal_barSpacing();
        const newBarSpacing = barSpacing + scale * (barSpacing / 10);
        // zoom in/out bar spacing
        this._internal_setBarSpacing(newBarSpacing);
        if (!this._private__options.rightBarStaysOnScroll) {
            // and then correct right offset to move index under zoomPoint back to its coordinate
            this._internal_setRightOffset(this._internal_rightOffset() + (floatIndexAtZoomPoint - this._private__coordinateToFloatIndex(zoomPoint)));
        }
    }
    _internal_startScale(x) {
        if (this._private__scrollStartPoint) {
            this._internal_endScroll();
        }
        if (this._private__scaleStartPoint !== null || this._private__commonTransitionStartState !== null) {
            return;
        }
        if (this._internal_isEmpty()) {
            return;
        }
        this._private__scaleStartPoint = x;
        this._private__saveCommonTransitionsStartState();
    }
    _internal_scaleTo(x) {
        if (this._private__commonTransitionStartState === null) {
            return;
        }
        const startLengthFromRight = clamp(this._private__width - x, 0, this._private__width);
        const currentLengthFromRight = clamp(this._private__width - ensureNotNull(this._private__scaleStartPoint), 0, this._private__width);
        if (startLengthFromRight === 0 || currentLengthFromRight === 0) {
            return;
        }
        this._internal_setBarSpacing(this._private__commonTransitionStartState._internal_barSpacing * startLengthFromRight / currentLengthFromRight);
    }
    _internal_endScale() {
        if (this._private__scaleStartPoint === null) {
            return;
        }
        this._private__scaleStartPoint = null;
        this._private__clearCommonTransitionsStartState();
    }
    _internal_startScroll(x) {
        if (this._private__scrollStartPoint !== null || this._private__commonTransitionStartState !== null) {
            return;
        }
        if (this._internal_isEmpty()) {
            return;
        }
        this._private__scrollStartPoint = x;
        this._private__saveCommonTransitionsStartState();
    }
    _internal_scrollTo(x) {
        if (this._private__scrollStartPoint === null) {
            return;
        }
        const shiftInLogical = (this._private__scrollStartPoint - x) / this._internal_barSpacing();
        this._private__rightOffset = ensureNotNull(this._private__commonTransitionStartState)._internal_rightOffset + shiftInLogical;
        this._private__visibleRangeInvalidated = true;
        // do not allow scroll out of visible bars
        this._private__correctOffset();
    }
    _internal_endScroll() {
        if (this._private__scrollStartPoint === null) {
            return;
        }
        this._private__scrollStartPoint = null;
        this._private__clearCommonTransitionsStartState();
    }
    _internal_scrollToRealTime() {
        this._internal_scrollToOffsetAnimated(this._private__options.rightOffset);
    }
    _internal_scrollToOffsetAnimated(offset, animationDuration = 400 /* Constants.DefaultAnimationDuration */) {
        if (!isFinite(offset)) {
            throw new RangeError('offset is required and must be finite number');
        }
        if (!isFinite(animationDuration) || animationDuration <= 0) {
            throw new RangeError('animationDuration (optional) must be finite positive number');
        }
        const source = this._private__rightOffset;
        const animationStart = performance.now();
        this._private__model._internal_setTimeScaleAnimation({
            _internal_finished: (time) => (time - animationStart) / animationDuration >= 1,
            _internal_getPosition: (time) => {
                const animationProgress = (time - animationStart) / animationDuration;
                const finishAnimation = animationProgress >= 1;
                return finishAnimation ? offset : source + (offset - source) * animationProgress;
            },
        });
    }
    _internal_update(newPoints, firstChangedPointIndex) {
        this._private__visibleRangeInvalidated = true;
        this._private__points = newPoints;
        this._private__tickMarks._internal_setTimeScalePoints(newPoints, firstChangedPointIndex);
        this._private__correctOffset();
    }
    _internal_visibleBarsChanged() {
        return this._private__visibleBarsChanged;
    }
    _internal_logicalRangeChanged() {
        return this._private__logicalRangeChanged;
    }
    _internal_optionsApplied() {
        return this._private__optionsApplied;
    }
    _internal_baseIndex() {
        // null is used to known that baseIndex is not set yet
        // so in methods which should known whether it is set or not
        // we should check field `_baseIndexOrNull` instead of getter `baseIndex()`
        // see minRightOffset for example
        return this._private__baseIndexOrNull || 0;
    }
    _internal_setVisibleRange(range, applyDefaultOffset) {
        const length = range._internal_count();
        const pixelOffset = (applyDefaultOffset && this._private__options.rightOffsetPixels) || 0;
        this._private__setBarSpacing((this._private__width - pixelOffset) / length);
        this._private__rightOffset = range._internal_right() - this._internal_baseIndex();
        if (applyDefaultOffset) {
            this._private__rightOffset = pixelOffset
                ? pixelOffset / this._internal_barSpacing()
                : this._private__options.rightOffset;
        }
        this._private__correctOffset();
        this._private__visibleRangeInvalidated = true;
        this._private__model._internal_recalculateAllPanes();
        this._private__model._internal_lightUpdate();
    }
    _internal_fitContent() {
        const first = this._private__firstIndex();
        const last = this._private__lastIndex();
        if (first === null || last === null) {
            return;
        }
        // If we are not using rightOffsetPixels then we should include the user defined rightOffset
        // in the Range so that the bar scaling considers the space required for the offset.
        const rightOffsetBars = (!this._private__options.rightOffsetPixels && this._private__options.rightOffset) || 0;
        this._internal_setVisibleRange(new RangeImpl(first, last + rightOffsetBars), true);
    }
    _internal_setLogicalRange(range) {
        const barRange = new RangeImpl(range.from, range.to);
        this._internal_setVisibleRange(barRange);
    }
    _internal_formatDateTime(timeScalePoint) {
        if (this._private__localizationOptions.timeFormatter !== undefined) {
            return this._private__localizationOptions.timeFormatter(timeScalePoint.originalTime);
        }
        return this._private__horzScaleBehavior.formatHorzItem(timeScalePoint.time);
    }
    _internal_recalculateIndicesWithData() {
        if (!this._private__options.ignoreWhitespaceIndices) {
            return;
        }
        this._private__indicesWithData.clear();
        const series = this._private__model._internal_serieses();
        for (const s of series) {
            for (const index of s._internal_fulfilledIndices()) {
                this._private__indicesWithData.set(index, true);
            }
        }
        this._private__indicesWithDataUpdateId++;
    }
    /**
     * Returns the current data conflation factor.
     * Factor \> 1 means data points should be conflated for performance.
     */
    _internal_conflationFactor() {
        return this._private__conflationFactor;
    }
    /**
     * Provides an array of possible conflations factors based on the current
     * minBarSpacing setting for the chart.
     * @returns Arrays of conflation factors (number of bars to merge)
     */
    _internal_possibleConflationFactors() {
        const devicePixelRatio = window.devicePixelRatio || 1;
        const conflationThreshold = 1.0 / devicePixelRatio;
        const minBarSpacing = this._private__options.minBarSpacing;
        if (minBarSpacing >= conflationThreshold) {
            return [1];
        }
        // Return all power-of-2 conflation levels that might be used
        const factors = [1];
        let currentLevel = 2;
        const maxLevel = 512;
        while (currentLevel <= maxLevel) {
            const levelThreshold = conflationThreshold / currentLevel;
            if (minBarSpacing < levelThreshold) {
                factors.push(currentLevel);
            }
            currentLevel *= 2;
        }
        return factors;
    }
    _private__isAllScalingAndScrollingDisabled() {
        const handleScroll = this._private__model._internal_options()['handleScroll'];
        const handleScale = this._private__model._internal_options()['handleScale'];
        return !handleScroll.horzTouchDrag
            && !handleScroll.mouseWheel
            && !handleScroll.pressedMouseMove
            && !handleScroll.vertTouchDrag
            && !handleScale.axisDoubleClickReset.time
            && !handleScale.axisPressedMouseMove.time
            && !handleScale.mouseWheel
            && !handleScale.pinch;
    }
    _private__firstIndex() {
        return this._private__points.length === 0 ? null : 0;
    }
    _private__lastIndex() {
        return this._private__points.length === 0 ? null : (this._private__points.length - 1);
    }
    _private__rightOffsetForCoordinate(x) {
        return (this._private__width - 1 - x) / this._private__barSpacing;
    }
    _private__coordinateToFloatIndex(x) {
        const deltaFromRight = this._private__rightOffsetForCoordinate(x);
        const baseIndex = this._internal_baseIndex();
        const index = baseIndex + this._private__rightOffset - deltaFromRight;
        // JavaScript uses very strange rounding
        // we need rounding to avoid problems with calculation errors
        return Math.round(index * 1000000) / 1000000;
    }
    _private__setBarSpacing(newBarSpacing) {
        const oldBarSpacing = this._private__barSpacing;
        this._private__barSpacing = newBarSpacing;
        this._private__correctBarSpacing();
        // this._barSpacing might be changed in _correctBarSpacing
        if (oldBarSpacing !== this._private__barSpacing) {
            this._private__visibleRangeInvalidated = true;
            this._private__resetTimeMarksCache();
            this._private__updateConflationFactor();
        }
    }
    _private__updateVisibleRange() {
        if (!this._private__visibleRangeInvalidated) {
            return;
        }
        this._private__visibleRangeInvalidated = false;
        if (this._internal_isEmpty()) {
            this._private__setVisibleRange(TimeScaleVisibleRange._internal_invalid());
            return;
        }
        const baseIndex = this._internal_baseIndex();
        const newBarsLength = this._private__width / this._private__barSpacing;
        const rightBorder = this._private__rightOffset + baseIndex;
        const leftBorder = rightBorder - newBarsLength + 1;
        const logicalRange = new RangeImpl(leftBorder, rightBorder);
        this._private__setVisibleRange(new TimeScaleVisibleRange(logicalRange));
    }
    _private__correctBarSpacing() {
        const barSpacing = clamp(this._private__barSpacing, this._private__minBarSpacing(), this._private__maxBarSpacing());
        if (this._private__barSpacing !== barSpacing) {
            this._private__barSpacing = barSpacing;
            this._private__visibleRangeInvalidated = true;
        }
    }
    _private__maxBarSpacing() {
        if (this._private__options.maxBarSpacing > 0) {
            // option takes precedance
            return this._private__options.maxBarSpacing;
        }
        else {
            // half of the width is default value for maximum bar spacing
            return this._private__width * 0.5;
        }
    }
    _private__minBarSpacing() {
        // if both options are enabled then limit bar spacing so that zooming-out is not possible
        // if it would cause either the first or last points to move too far from an edge
        if (this._private__options.fixLeftEdge && this._private__options.fixRightEdge && this._private__points.length !== 0) {
            return this._private__width / this._private__points.length;
        }
        return this._private__options.minBarSpacing;
    }
    /**
     * Updates the conflation factor based on current bar spacing using DPR-aware power-of-2 calculation with optional smoothing factor.
     * The smoothing factor allows intentional over-conflation for smoother appearance in small charts and sparklines.
     */
    _private__updateConflationFactor() {
        if (!this._private__options.enableConflation) {
            this._private__conflationFactor = 1;
            return;
        }
        // Use DPR-aware threshold calculation with smoothing factor
        const devicePixelRatio = window.devicePixelRatio || 1;
        const smoothingFactor = this._private__options.conflationThresholdFactor ?? 1;
        const adjustedThreshold = (1.0 / devicePixelRatio) * smoothingFactor;
        if (this._private__barSpacing >= adjustedThreshold) {
            this._private__conflationFactor = 1;
            return;
        }
        // Calculate conflation level as power of 2
        const ratio = adjustedThreshold / this._private__barSpacing;
        const conflationLevel = Math.pow(2, Math.floor(Math.log2(ratio)));
        // Ensure we don't exceed maximum conflation level (512)
        this._private__conflationFactor = Math.min(conflationLevel, 512);
    }
    _private__correctOffset() {
        // block scrolling of to past
        const minRightOffset = this._private__minRightOffset();
        if (minRightOffset !== null && this._private__rightOffset < minRightOffset) {
            this._private__rightOffset = minRightOffset;
            this._private__visibleRangeInvalidated = true;
        }
        // block scrolling of to future
        const maxRightOffset = this._private__maxRightOffset();
        if (this._private__rightOffset > maxRightOffset) {
            this._private__rightOffset = maxRightOffset;
            this._private__visibleRangeInvalidated = true;
        }
    }
    _private__minRightOffset() {
        const firstIndex = this._private__firstIndex();
        const baseIndex = this._private__baseIndexOrNull;
        if (firstIndex === null || baseIndex === null) {
            return null;
        }
        const barsEstimation = this._private__options.fixLeftEdge
            ? this._private__width / this._private__barSpacing
            : Math.min(2 /* Constants.MinVisibleBarsCount */, this._private__points.length);
        return firstIndex - baseIndex - 1 + barsEstimation;
    }
    _private__maxRightOffset() {
        return this._private__options.fixRightEdge
            ? 0
            : (this._private__width / this._private__barSpacing) - Math.min(2 /* Constants.MinVisibleBarsCount */, this._private__points.length);
    }
    _private__saveCommonTransitionsStartState() {
        this._private__commonTransitionStartState = {
            _internal_barSpacing: this._internal_barSpacing(),
            _internal_rightOffset: this._internal_rightOffset(),
        };
    }
    _private__clearCommonTransitionsStartState() {
        this._private__commonTransitionStartState = null;
    }
    _private__formatLabel(tickMark) {
        let formatter = this._private__formattedByWeight.get(tickMark.weight);
        if (formatter === undefined) {
            formatter = new FormattedLabelsCache((mark) => {
                return this._private__formatLabelImpl(mark);
            }, this._private__horzScaleBehavior);
            this._private__formattedByWeight.set(tickMark.weight, formatter);
        }
        return formatter._internal_format(tickMark);
    }
    _private__formatLabelImpl(tickMark) {
        return this._private__horzScaleBehavior.formatTickmark(tickMark, this._private__localizationOptions);
    }
    _private__setVisibleRange(newVisibleRange) {
        const oldVisibleRange = this._private__visibleRange;
        this._private__visibleRange = newVisibleRange;
        if (!areRangesEqual(oldVisibleRange._internal_strictRange(), this._private__visibleRange._internal_strictRange())) {
            this._private__visibleBarsChanged._internal_fire();
        }
        if (!areRangesEqual(oldVisibleRange._internal_logicalRange(), this._private__visibleRange._internal_logicalRange())) {
            this._private__logicalRangeChanged._internal_fire();
        }
        // TODO: reset only coords in case when this._visibleBars has not been changed
        this._private__resetTimeMarksCache();
    }
    _private__resetTimeMarksCache() {
        this._private__timeMarksCache = null;
    }
    _private__invalidateTickMarks() {
        this._private__resetTimeMarksCache();
        this._private__formattedByWeight.clear();
    }
    _private__updateDateTimeFormatter() {
        this._private__horzScaleBehavior.updateFormatter(this._private__localizationOptions);
    }
    _private__doFixLeftEdge() {
        if (!this._private__options.fixLeftEdge) {
            return;
        }
        const firstIndex = this._private__firstIndex();
        if (firstIndex === null) {
            return;
        }
        const visibleRange = this._internal_visibleStrictRange();
        if (visibleRange === null) {
            return;
        }
        const delta = visibleRange._internal_left() - firstIndex;
        if (delta < 0) {
            const leftEdgeOffset = this._private__rightOffset - delta - 1;
            this._internal_setRightOffset(leftEdgeOffset);
        }
        this._private__correctBarSpacing();
    }
    _private__doFixRightEdge() {
        this._private__correctOffset();
        this._private__correctBarSpacing();
    }
    _private__shouldConsiderIndex(index) {
        if (!this._private__options.ignoreWhitespaceIndices) {
            return true;
        }
        return this._private__indicesWithData.get(index) || false;
    }
    _private__findNearestIndexWithData(x) {
        const gen = testNearestIntegers(x);
        const maxIndex = this._private__lastIndex();
        while (maxIndex) {
            const index = gen.next().value;
            if (this._private__indicesWithData.get(index)) {
                return index;
            }
            if (index < 0 || index > maxIndex) {
                break;
            }
        }
        return x; // fallback to original index
    }
    _private__checkRightOffsetPixels(options) {
        if (options.rightOffsetPixels !== undefined) {
            const newOffset = options.rightOffsetPixels / (options.barSpacing || this._private__barSpacing);
            this._private__model._internal_setRightOffset(newOffset);
        }
    }
}
function* testNearestIntegers(num) {
    const rounded = Math.round(num);
    const isRoundedDown = rounded < num;
    let offset = 1;
    while (true) {
        if (isRoundedDown) {
            yield rounded + offset;
            yield rounded - offset;
        }
        else {
            yield rounded - offset;
            yield rounded + offset;
        }
        offset++;
    }
}

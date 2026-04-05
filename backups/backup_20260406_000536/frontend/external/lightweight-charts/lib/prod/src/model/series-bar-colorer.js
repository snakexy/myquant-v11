import { ensure, ensureNotNull } from '../helpers/assertions';
const barStyleFnMap = {
    // eslint-disable-next-line @typescript-eslint/naming-convention
    Bar: (findBar, barStyle, barIndex, precomputedBars) => {
        const upColor = barStyle.upColor;
        const downColor = barStyle.downColor;
        const currentBar = ensureNotNull(findBar(barIndex, precomputedBars));
        const isUp = ensure(currentBar._internal_value[0 /* PlotRowValueIndex.Open */]) <= ensure(currentBar._internal_value[3 /* PlotRowValueIndex.Close */]);
        return {
            _internal_barColor: currentBar._internal_color ?? (isUp ? upColor : downColor),
        };
    },
    // eslint-disable-next-line @typescript-eslint/naming-convention
    Candlestick: (findBar, candlestickStyle, barIndex, precomputedBars) => {
        const upColor = candlestickStyle.upColor;
        const downColor = candlestickStyle.downColor;
        const borderUpColor = candlestickStyle.borderUpColor;
        const borderDownColor = candlestickStyle.borderDownColor;
        const wickUpColor = candlestickStyle.wickUpColor;
        const wickDownColor = candlestickStyle.wickDownColor;
        const currentBar = ensureNotNull(findBar(barIndex, precomputedBars));
        const isUp = ensure(currentBar._internal_value[0 /* PlotRowValueIndex.Open */]) <= ensure(currentBar._internal_value[3 /* PlotRowValueIndex.Close */]);
        return {
            _internal_barColor: currentBar._internal_color ?? (isUp ? upColor : downColor),
            _internal_barBorderColor: currentBar._internal_borderColor ?? (isUp ? borderUpColor : borderDownColor),
            _internal_barWickColor: currentBar._internal_wickColor ?? (isUp ? wickUpColor : wickDownColor),
        };
    },
    // eslint-disable-next-line @typescript-eslint/naming-convention
    Custom: (findBar, customStyle, barIndex, precomputedBars) => {
        const currentBar = ensureNotNull(findBar(barIndex, precomputedBars));
        return {
            _internal_barColor: currentBar._internal_color ?? customStyle.color,
        };
    },
    // eslint-disable-next-line @typescript-eslint/naming-convention
    Area: (findBar, areaStyle, barIndex, precomputedBars) => {
        const currentBar = ensureNotNull(findBar(barIndex, precomputedBars));
        return {
            _internal_barColor: currentBar._internal_lineColor ?? areaStyle.lineColor,
            _internal_lineColor: currentBar._internal_lineColor ?? areaStyle.lineColor,
            _internal_topColor: currentBar._internal_topColor ?? areaStyle.topColor,
            _internal_bottomColor: currentBar._internal_bottomColor ?? areaStyle.bottomColor,
        };
    },
    // eslint-disable-next-line @typescript-eslint/naming-convention
    Baseline: (findBar, baselineStyle, barIndex, precomputedBars) => {
        const currentBar = ensureNotNull(findBar(barIndex, precomputedBars));
        const isAboveBaseline = currentBar._internal_value[3 /* PlotRowValueIndex.Close */] >= baselineStyle.baseValue.price;
        return {
            _internal_barColor: isAboveBaseline ? baselineStyle.topLineColor : baselineStyle.bottomLineColor,
            _internal_topLineColor: currentBar._internal_topLineColor ?? baselineStyle.topLineColor,
            _internal_bottomLineColor: currentBar._internal_bottomLineColor ?? baselineStyle.bottomLineColor,
            _internal_topFillColor1: currentBar._internal_topFillColor1 ?? baselineStyle.topFillColor1,
            _internal_topFillColor2: currentBar._internal_topFillColor2 ?? baselineStyle.topFillColor2,
            _internal_bottomFillColor1: currentBar._internal_bottomFillColor1 ?? baselineStyle.bottomFillColor1,
            _internal_bottomFillColor2: currentBar._internal_bottomFillColor2 ?? baselineStyle.bottomFillColor2,
        };
    },
    // eslint-disable-next-line @typescript-eslint/naming-convention
    Line: (findBar, lineStyle, barIndex, precomputedBars) => {
        const currentBar = ensureNotNull(findBar(barIndex, precomputedBars));
        return {
            _internal_barColor: currentBar._internal_color ?? lineStyle.color,
            _internal_lineColor: currentBar._internal_color ?? lineStyle.color,
        };
    },
    // eslint-disable-next-line @typescript-eslint/naming-convention
    Histogram: (findBar, histogramStyle, barIndex, precomputedBars) => {
        const currentBar = ensureNotNull(findBar(barIndex, precomputedBars));
        return {
            _internal_barColor: currentBar._internal_color ?? histogramStyle.color,
        };
    },
};
export class SeriesBarColorer {
    constructor(series) {
        this._private__findBar = (barIndex, precomputedBars) => {
            if (precomputedBars !== undefined) {
                return precomputedBars._internal_value;
            }
            return this._private__series._internal_bars()._internal_valueAt(barIndex);
        };
        this._private__series = series;
        this._private__styleGetter = barStyleFnMap[series._internal_seriesType()];
    }
    _internal_barStyle(barIndex, precomputedBars) {
        // precomputedBars: {value: [Array BarValues], previousValue: [Array BarValues] | undefined}
        // Used to avoid binary search if bars are already known
        return this._private__styleGetter(this._private__findBar, this._private__series._internal_options(), barIndex, precomputedBars);
    }
}

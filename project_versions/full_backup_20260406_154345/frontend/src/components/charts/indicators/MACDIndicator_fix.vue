  // 过滤 null/None 值
  const macdData = data.macd
    .map((val, i) => ({ time: timeData[i], value: val }))
    .filter(item => item.value !== null && item.value !== undefined && !isNaN(item.value))
  macdSeries?.setData(macdData)

  const signalData = data.signal
    .map((val, i) => ({ time: timeData[i], value: val }))
    .filter(item => item.value !== null && item.value !== undefined && !isNaN(item.value))
  signalSeries?.setData(signalData)

  if (data.histogram && histogramSeries) {
    const histogramData = data.histogram
      .map((val, i) => ({
        time: timeData[i],
        value: Math.abs(val),
        color: val >= 0 ? props.colors.histogramPositive : props.colors.histogramNegative
      }))
      .filter(item => item.value !== null && item.value !== undefined && !isNaN(item.value))
    histogramSeries?.setData(histogramData)
  }

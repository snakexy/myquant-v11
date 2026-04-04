: 60)}
print("=" * 60)

# Get TdxQuant adapter
tdx = get_adapter('tdxquant')
if tdx and tdx._ensure_initialized():
    # Get daily data
    df_dict = tdx.get_kline([symbol], period='1d', count=100)

    if symbol in df_dict and not df_dict[symbol].empty:
        df = df_dict[symbol]
        df['datetime'] = pd.to_datetime(df.index)

        # Filter October 2025 data
        oct_start = pd.Timestamp('2025-10-01')
        oct_end = pd.Timestamp('2025-10-31')
        df_oct = df[(df['datetime'] >= oct_start) & (df['datetime'] <= oct_end)]

        print(f"\nTdxQuant返回的2025年10月日线数据:")
        if not df_oct.empty:
            print(df_oct[['datetime', 'volume', 'open', 'close', 'amount']].to_string())

            # Check volume values
            print(f"\n2025-10-28 volume: {df_oct[df_oct['datetime'] == '2025-10-28']['volume'].values}")
            print(f"2025-10-29 volume: {df_oct[df_oct['datetime'] == '2025-10-29']['volume'].values}")
        else:
            print("无10月数据")
    else:
        print("TdxQuant未返回数据")
else:
    print("TdxQuant不可用")
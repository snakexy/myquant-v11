: 60)}
print("=" * 60)

# Get TdxQuant adapter
tdx = get_adapter('tdxquant')
if tdx and tdx._ensure_initialized():
    # Get data for March 9
    df_dict = tdx.get_kline([symbol], period=period, count=100)

    if symbol in df_dict and not df_dict[symbol].empty:
        df = df_dict[symbol]
        df['datetime'] = pd.to_datetime(df.index)

        # Filter March 9 data
        march_9_start = pd.Timestamp('2026-03-09 09:30:00')
        march_9_end = pd.Timestamp('2026-03-09 15:00:00')
        df_march_9 = df[(df['datetime'] >= march_9_start) & (df['datetime'] <= march_9_end)]

        print(f"\nTdxQuant返回的3月9日数据 (原始数据):")
        if not df_march_9.empty:
            print(df_march_9[['volume', 'open', 'close', 'amount']].head(10))
            sample_vol = df_march_9['volume'].iloc[0]
            print(f"\n样本volume: {sample_vol:,.0f}")
            if sample_vol > 1000000:
                print("(股单位 - 数值过大，未转换)")
            else:
                print("(手单位 - 已转换)")
        else:
            print("无3月9日数据")

        # Check the raw data from get_kline
        print("\n" + "=" * 60)
        print("检查TdxQuant.get_kline返回的原始数据:")
        print("=" * 60)
        print(f"数据条数: {len(df)}")
        print(f"时间范围: {df.index[0]} ~ {df.index[-1]}")
        print(f"\n前5条数据:")
        print(df[['volume', 'open', 'close']].head())
        print(f"\n最后5条数据:")
        print(df[['volume', 'open', 'close']].tail())

        # Check if _normalize_kline_df is working
        print("\n" + "=" * 60)
        print("手动调用_normalize_kline_df检查:")
        print("=" * 60)
        # Get raw data without normalization
        raw_df = tdx.get_kline([symbol], period=period, count=10)[symbol]
        print(f"原始数据volume (前3条): {raw_df['volume'].head(3).tolist()}")
        print(f"原始数据volume均值: {raw_df['volume'].mean():,.0f}")

    else:
        print("TdxQuant未返回数据")
else:
    print("TdxQuant不可用")

# Check what's actually stored in HotDB
print("\n" + "=" * 60)
print("对比HotDB中存储的数据:")
print("=" * 60)

hotdb = get_adapter('hotdb')
df_dict_hot = hotdb.get_kline([symbol], period=period, count=5000, allow_stale=True)

if symbol in df_dict_hot and not df_dict_hot[symbol].empty:
    df_hot = df_dict_hot[symbol]
    df_hot['datetime'] = pd.to_datetime(df_hot['datetime'])

    # Filter March 9
    df_hot_march_9 = df_hot[(df_hot['datetime'] >= march_9_start) & (df_hot['datetime'] <= march_9_end)]

    if not df_hot_march_9.empty:
        print(f"\nHotDB中3月9日数据:")
        print(df_hot_march_9[['datetime', 'volume', 'open', 'close']].head(10))
        hot_vol = df_hot_march_9['volume'].iloc[0]
        print(f"\nHotDB样本volume: {hot_vol:,.0f}")
        if hot_vol > 1000000:
            print("(股单位 - 数值过大)")
        else:
            print("(手单位 - 已转换)")

        # Show latest data
        print(f"\nHotDB最新10条数据:")
        print(df_hot[['datetime', 'volume', 'open', 'close']].tail(10))
    else:
        print("HotDB中无3月9日数据")
else:
    print("HotDB中无数据")
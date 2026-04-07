"""
测试 300046.SZ 5m 智能补全
"""

from myquant.core.market.services.hotdb_service import get_hotdb_service

symbol = "300046.SZ"
period = "5m"

print(f"\n{'='*60}")
print(f"测试 {symbol} {period} 智能补全")
print(f"{'='*60}\n")

hotdb_service = get_hotdb_service()

# 补全前
hotdb = hotdb_service._get_hotdb_adapter()
if hotdb and hotdb.is_available():
    info = hotdb.get_data_info(symbol, period)
    if info and info.get('has_data'):
        print(f"[补全前] HotDB: {info.get('count')} 条, 最新: {info.get('latest')}")

# 执行智能补全
print(f"\n[执行] smart_update...")
result = hotdb_service.smart_update(symbol, period)

print(f"\n[结果]")
print(f"  success: {result.get('success')}")
print(f"  has_gap: {result.get('has_gap')}")
print(f"  reason: {result.get('reason')}")

if result.get('added_count'):
    print(f"  added_count: {result.get('added_count')}")

# 补全后
if hotdb and hotdb.is_available():
    info = hotdb.get_data_info(symbol, period)
    if info and info.get('has_data'):
        print(f"\n[补全后] HotDB: {info.get('count')} 条, 最新: {info.get('latest')}")

        # 检查 3月17-25日
        df_dict = hotdb.get_kline(
            symbols=[symbol],
            period=period,
            start_date="20260317",
            end_date="20260325"
        )

        if symbol in df_dict and not df_dict[symbol].empty:
            df = df_dict[symbol]
            print(f"\n[3月17-25日] {len(df)} 条")
        else:
            print(f"\n[3月17-25日] 仍然无数据")

print(f"\n{'='*60}\n")

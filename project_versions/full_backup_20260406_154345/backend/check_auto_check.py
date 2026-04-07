"""检查自动检查调度器状态"""
import sys
sys.path.insert(0, 'E:/MyQuant_v11/backend')

import asyncio
from datetime import datetime
from myquant.core.market.utils.trading_time_detector import TradingTimeDetectorV2
from myquant.core.market.services.daily_data_status import get_daily_status_service
from myquant.api.dataget.watchlist import get_watchlist

async def main():
    print("=" * 70)
    print("检查自动检查调度器状态")
    print("=" * 70)

    # 1. 检查今天是否是交易日
    detector = TradingTimeDetectorV2()
    today_str = datetime.now().strftime('%Y%m%d')
    is_trading = detector.is_trading_day()

    print(f"\n[今天状态]")
    print(f"  日期: {datetime.now().strftime('%Y-%m-%d')}")
    print(f"  是否交易日: {is_trading}")
    print(f"  当前时间: {datetime.now().strftime('%H:%M')}")

    # 2. 检查自选股
    response = await get_watchlist()
    data = response.data if hasattr(response, 'data') else response
    all_symbols = []
    for group in data.get('groups', []):
        for stock in group.get('stocks', []):
            all_symbols.append(stock['symbol'])

    print(f"\n[自选股]")
    print(f"  分组数: {len(data.get('groups', []))}")
    print(f"  股票数: {len(all_symbols)}")
    if len(all_symbols) > 0:
        print(f"  示例: {all_symbols[:5]}")

    # 3. 检查状态文件
    status_service = get_daily_status_service()
    status = status_service.get_status()

    print(f"\n[状态文件]")
    print(f"  总股票数: {len(status.get('data', {}))}")
    print(f"  今天记录: {today_str}")

    if status.get('data'):
        for symbol, dates in list(status.get('data', {}).items())[:3]:
            print(f"  {symbol}: {list(dates.keys())}")

    # 4. 检查今天是否已检查
    checked_symbols = []
    for symbol in all_symbols:
        if status_service.is_checked_today(symbol, today_str):
            checked_symbols.append(symbol)

    print(f"\n[今天已检查]")
    print(f"  已检查: {len(checked_symbols)}/{len(all_symbols)}")

    # 5. 手动触发一次检查测试
    print(f"\n[手动触发测试]")
    if len(all_symbols) > 0:
        from myquant.core.market.services.hotdb_service import get_hotdb_service

        hotdb_service = get_hotdb_service()
        test_symbol = all_symbols[0]

        print(f"  测试股票: {test_symbol}")
        result = hotdb_service.smart_update(test_symbol, '5m')
        print(f"  smart_update 结果:")
        print(f"    success: {result.get('success')}")
        print(f"    has_gap: {result.get('has_gap')}")
        print(f"    reason: {result.get('reason')}")

    print("\n" + "=" * 70)

if __name__ == "__main__":
    asyncio.run(main())

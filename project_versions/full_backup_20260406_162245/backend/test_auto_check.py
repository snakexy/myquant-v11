"""手动触发一次完整的自动检查"""
import sys
import asyncio
sys.path.insert(0, 'E:/MyQuant_v11/backend')

from datetime import datetime
from myquant.core.market.services.daily_data_status import get_daily_status_service
from myquant.api.dataget.watchlist import get_watchlist
from myquant.core.market.services.hotdb_service import get_hotdb_service

async def main():
    print("=" * 70)
    print("手动触发完整自动检查")
    print("=" * 70)

    # 获取自选股
    response = await get_watchlist()
    data = response.data if hasattr(response, 'data') else response
    all_symbols = []
    for group in data.get('groups', []):
        for stock in group.get('stocks', []):
            all_symbols.append(stock['symbol'])

    print(f"\n[自选股] {len(all_symbols)} 只: {all_symbols}")

    # 获取服务
    hotdb_service = get_hotdb_service()
    status_service = get_daily_status_service()

    today_str = datetime.now().strftime('%Y%m%d')
    print(f"[今天日期] {today_str}")

    # 手动调用 auto_check_and_fill_today
    print(f"\n[触发检查]")
    result = hotdb_service.auto_check_and_fill_today(all_symbols)

    print(f"\n[检查结果]")
    print(f"  checked: {result.get('checked')}")
    print(f"  filled: {result.get('filled')}")
    print(f"  gaps_found: {result.get('gaps_found')}")
    print(f"  already_complete: {result.get('already_complete', 0)}")

    # 检查状态文件是否被更新
    status = status_service.get_status()
    print(f"\n[状态文件更新后]")
    print(f"  总股票数: {len(status.get('data', {}))}")

    if status.get('data'):
        for symbol, dates in list(status.get('data', {}).items())[:3]:
            print(f"  {symbol}: {list(dates.keys())}")

    print("\n" + "=" * 70)

if __name__ == "__main__":
    asyncio.run(main())

#!/usr/bin/env python3
"""验证000001.SZ的5分钟数据已被清除，并触发重新预热（使用修复后的单位转换逻辑）"""
import sys
sys.path.insert(0, r'E:\MyQuant_v11\backend\src')

from myquant.core.market.services.hotdb_service import HotDBService
from myquant.core.market.adapters import get_adapter

symbol = '000001.SZ'
period = '5m'

print("=" * 60)
print("验证清除结果并重新预热")
print("=" * 60)

service = HotDBService()

# 1. 验证数据已被清除
print("\n1. 验证数据清除:")
hotdb = service._get_hotdb_adapter()
df_dict = hotdb.get_kline([symbol], period=period, count=5)

if symbol not in df_dict or df_dict[symbol].empty:
    print("   [OK] 000001.SZ 的 5m 数据已清除")

    # 2. 触发智能更新（会从LocalDB复制，使用修复后的逻辑）
    print("\n2. 触发智能更新（使用修复后的单位转换）:")
    result = service.smart_update(symbol, period)

    if result.get('success') and result.get('has_data'):
        print(f"   [OK] 智能更新成功")
        print(f"   数据来源: {result.get('reason', 'unknown')}")
        print(f"   最新时间: {result.get('latest')}")

        # 3. 验证新数据的单位
        print("\n3. 验证新数据单位:")
        df_dict_new = hotdb.get_kline([symbol], period=period, count=5)
        if symbol in df_dict_new and not df_dict_new[symbol].empty:
            df = df_dict_new[symbol]
            vol = df['volume'].iloc[-1]
            print(f"   最后一条volume: {vol:,.0f}")

            # 对比LocalDB原始数据
            localdb = get_adapter('localdb')
            df_dict_local = localdb.get_kline([symbol], period=period, count=5)
            if symbol in df_dict_local and not df_dict_local[symbol].empty:
                local_vol = df_dict_local[symbol]['volume'].iloc[-1]
                print(f"   LocalDB原始: {local_vol:,.0f} (股)")
                print(f"   转换后预期: {local_vol/100:,.0f} (手)")

                ratio = vol / (local_vol/100) if local_vol > 0 else 0
                print(f"   实际/预期比例: {ratio:.2f}")

                if 0.9 < ratio < 1.1:
                    print("   [OK] 单位转换正确！数据已是'手'单位")
                else:
                    print("   [警告] 单位可能仍有问题")
    else:
        print(f"   [错误] 智能更新失败: {result.get('error', 'unknown')}")
else:
    print(f"   [警告] 数据仍存在，可能需要手动删除文件")
    print(f"   数据条数: {len(df_dict[symbol])}")

print("\n" + "=" * 60)

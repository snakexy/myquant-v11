# -*- coding: utf-8 -*-
"""
测试批量更新 LocalDB 功能

1. 创建批量更新任务
2. 连接 WebSocket 监听进度
3. 显示实时进度
"""

import asyncio
import json
import sys
from pathlib import Path

import websockets
from loguru import logger

# 添加 src 到路径
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))


async def test_batch_update():
    """测试批量更新"""
    print("\n" + "="*60)
    print("  批量更新 LocalDB 测试")
    print("="*60)

    # 1. 创建任务
    print("\n[1] 创建批量更新任务...")
    import requests

    task_request = {
        "symbols": ["000001.SZ", "600519.SH"],  # 测试2只股票
        "periods": ["1d"],  # 只更新日线（更快）
        "source": "pytdx"
    }

    try:
        response = requests.post(
            'http://localhost:8000/api/v5/hotdata/update-localdb',
            json=task_request,
            timeout=10
        )

        if response.status_code != 200:
            print(f"[X] 创建任务失败: {response.status_code}")
            print(response.text)
            return

        data = response.json()
        if not data.get('success'):
            print(f"[X] 任务创建失败: {data.get('error')}")
            return

        task_id = data.get('task_id')
        total = data.get('total', 0)

        print(f"[OK] 任务已创建")
        print(f"   任务ID: {task_id}")
        print(f"   总数量: {total}")

        # 2. 连接 WebSocket 监听进度
        print(f"\n[2] 连接 WebSocket: ws://localhost:8000/ws/batch-update/{task_id}")
        ws_url = f"ws://localhost:8000/ws/batch-update/{task_id}"

        async with websockets.connect(ws_url) as websocket:
            print("[OK] WebSocket 已连接，等待进度推送...\n")

            # 接收进度消息
            while True:
                try:
                    message = await asyncio.wait_for(
                        websocket.recv(),
                        timeout=30.0  # 30秒超时
                    )
                    data = json.loads(message)

                    # 解析消息
                    msg_type = data.get('type', '')
                    completed = data.get('completed', 0)
                    total = data.get('total', 0)

                    if msg_type == 'progress':
                        current_symbol = data.get('current_symbol', '')
                        current_period = data.get('current_period', '')

                        # 显示进度
                        percentage = int((completed / total) * 100) if total > 0 else 0
                        print(f"[{percentage:3d}%] {completed}/{total} - {current_symbol} {current_period}")

                    elif msg_type == 'complete':
                        print(f"\n{'='*60}")
                        print(f"  完成!")
                        print(f"  总数: {total}")
                        print(f"  结果: {data.get('results', {})}")
                        print(f"{'='*60}")
                        break

                    elif msg_type == 'error':
                        print(f"\n[X] 错误: {data.get('message', '未知错误')}")
                        break

                except asyncio.TimeoutError:
                    print("[!] WebSocket 超时（30秒无消息）")
                    # 检查任务是否仍在后台运行
                    print("   提示：任务可能仍在后台执行，可以稍后查看 LocalDB")
                    break

    except requests.exceptions.RequestException as e:
        print(f"[X] 请求失败: {e}")
    except Exception as e:
        print(f"[X] 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    try:
        asyncio.run(test_batch_update())
    except KeyboardInterrupt:
        print("\n\n测试已取消")
    except Exception as e:
        logger.error(f"测试异常: {e}")

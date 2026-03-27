"""测试 KlineService V5 双层路由"""
import asyncio
import websockets
import json


async def test_kline_service():
    symbol = "000001.SZ"
    uri = f"ws://localhost:8001/ws/kline/{symbol}"

    try:
        async with websockets.connect(uri) as ws:
            print(f"[OK] Connected to {uri}")

            messages_received = 0

            # 接收消息（超时 10 秒）
            try:
                while messages_received < 5:
                    msg = await asyncio.wait_for(ws.recv(), timeout=10.0)
                    data = json.loads(msg)
                    msg_type = data.get("type", "unknown")
                    print(f"  Received: {msg_type}")

                    if msg_type == "history":
                        bars_count = len(data.get("bars", []))
                        print(f"    History bars: {bars_count}")
                    elif msg_type in ["bar_update", "bar_close"]:
                        bar = data.get("bar", {})
                        print(f"    {msg_type}: {bar}")

                    messages_received += 1

            except asyncio.TimeoutError:
                print("  Timeout (expected if not in trading hours)")

            print(f"\n[OK] Test complete, {messages_received} messages received")

    except Exception as e:
        print(f"[ERROR] Connection failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_kline_service())

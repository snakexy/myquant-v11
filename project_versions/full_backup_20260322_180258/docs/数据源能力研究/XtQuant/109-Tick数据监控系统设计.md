# XtQuant Tick数据监控系统设计

> **版本**: v10.0.0
> **创建日期**: 2026-02-05
> **基于**: XtQuant实际API能力

---

## 📋 目录

1. [设计目标](#设计目标)
2. [核心概念](#核心概念)
3. [系统架构](#系统架构)
4. [数据源设计](#数据源设计)
5. [异常检测设计](#异常检测设计)
6. [API接口设计](#api接口设计)
7. [存储策略](#存储策略)
8. [实现方案](#实现方案)

---

## 设计目标

### 核心目标

1. **实时监控** - 监控自选股的实时行情变化
2. **异常检测** - 检测突然拉涨、放量、强买等异常
3. **分级告警** - 根据异常严重程度分级处理
4. **历史追溯** - 保存异常事件供后续分析

### 约束条件

基于XtQuant实际能力：
- ✅ `get_full_tick()` - 获取最新快照（6.5ms/100只）
- ✅ `subscribe_quote()` + `register_callback()` - 订阅推送（约3秒）
- ✅ `get_market_data_ex(period='1m')` - 获取分钟K线
- ❌ 逐笔成交数据 - 数据量太大，不使用

---

## 核心概念

### Tick快照 vs 逐笔成交

**重要**：XtQuant中的"tick"指的是**行情快照**，不是逐笔成交。

```python
# XtQuant提供的Tick快照（17个字段）
tick_snapshot = {
    'lastPrice': 1525,              # 最新价
    'lastClose': 1474.92,           # 昨收
    'volume': 109123,              # 成交量
    'amount': 16444346000,         # 成交额
    'askPrice': [1525, 0, ...],    # 卖盘价（5档）
    'bidPrice': [1524.94, ...],    # 买盘价（5档）
    'timetag': '20260204 15:00:02',
    ... (共17个字段)
}
```

### 监控模式

| 模式 | API | 更新频率 | 适用场景 | 监控数量 |
|------|-----|---------|---------|---------|
| **轮询模式** | `get_full_tick()` | 每3秒 | 扩展监控 | 无限制 |
| **推送模式** | `register_callback()` | 约3秒 | 核心监控 | 300-500只 |

---

## 系统架构

### 整体架构

```
┌─────────────────────────────────────────────────────────────┐
│                      前端展示层                              │
│  - 实时行情显示                                              │
│  - 异常告警推送                                              │
│  - 历史事件查询                                              │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│                    API接口层                                 │
│  GET /api/v1/tick-monitor/status                           │
│  GET /api/v1/tick-monitor/watchlist                        │
│  GET /api/v1/tick-monitor/anomalies                        │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│                   Tick监控服务层                             │
│                                                             │
│  ┌──────────────────┐        ┌──────────────────┐          │
│  │  轮询监控器       │        │  订阅监控器       │          │
│  │  (扩展股票)      │        │  (核心股票)      │          │
│  └──────────────────┘        └──────────────────┘          │
│            ↓                           ↓                       │
│  ┌──────────────────────────────────────────┐               │
│  │        异常检测引擎                      │               │
│  │  - 价格变化检测                          │               │
│  │  - 成交量检测                            │               │
│  │  - 买卖盘对比                            │               │
│  │  - 动态阈值                              │               │
│  └──────────────────────────────────────────┘               │
│            ↓                                                   │
│  ┌──────────────────┐        ┌──────────────────┐          │
│  │  分级存储管理     │        │  告警通知         │          │
│  └──────────────────┘        └──────────────────┘          │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│                   XtQuant数据源                              │
│  - get_full_tick()      (轮询模式)                           │
│  - subscribe_quote()     (推送模式)                           │
│  - get_market_data_ex() (历史数据)                            │
└─────────────────────────────────────────────────────────────┘
```

---

## 数据源设计

### 混合数据源策略

```python
class HybridTickDataSource:
    """混合Tick数据源"""

    def __init__(self):
        # 核心100只：使用订阅（实时推送）
        self.core_symbols = self._load_core_watchlist()
        self.poller = SubscriptionTickMonitor(self.core_symbols)

        # 扩展200只：使用轮询（每3秒）
        self.extended_symbols = self._load_extended_watchlist()
        self.subscriber = PollingTickMonitor(self.extended_symbols)

    def get_snapshots(self, symbols):
        """获取股票快照（自动选择数据源）"""
        core_data = self.poller.get_snapshots(
            [s for s in symbols if s in self.core_symbols]
        )

        extended_data = self.subscriber.get_snapshots(
            [s for s in symbols if s in self.extended_symbols]
        )

        return {**core_data, **extended_data}
```

### 轮询模式实现

```python
import time
from xtquant import xtdata

class PollingTickMonitor:
    """轮询模式Tick监控"""

    def __init__(self, symbols, interval=3):
        self.symbols = symbols
        self.interval = interval  # 3秒
        self.cache = {}
        self.callbacks = []

    def start(self):
        """启动轮询监控"""
        while True:
            # 获取快照
            snapshots = xtdata.get_full_tick(self.symbols)

            # 检测变化
            for symbol, data in snapshots.items():
                if symbol in self.cache:
                    self._check_for_anomaly(symbol, data, self.cache[symbol])

            # 更新缓存
            self.cache = snapshots

            # 通知回调
            for callback in self.callbacks:
                callback(snapshots)

            # 等待下一次轮询
            time.sleep(self.interval)
```

### 订阅模式实现

```python
from xtquant import xtdata

class SubscriptionTickMonitor:
    """订阅模式Tick监控"""

    def __init__(self, symbols):
        self.symbols = symbols
        self.cache = {}
        self.callbacks = []

    def start(self):
        """启动订阅监控"""
        # 1. 注册回调
        xtdata.register_callback(self._on_tick_update)

        # 2. 订阅股票
        for symbol in self.symbols:
            xtdata.subscribe_quote(symbol, period='tick', count=0)

        # 3. 保持运行
        while True:
            time.sleep(1)

    def _on_tick_update(self, data):
        """Tick更新回调"""
        for symbol, tick_data in data.items():
            if symbol in self.cache:
                self._check_for_anomaly(symbol, tick_data, self.cache[symbol])

            self.cache[symbol] = tick_data

        # 通知回调
        for callback in self.callbacks:
            callback(data)
```

---

## 异常检测设计

### 异常类型

#### 1. 突然拉涨/下跌

```python
def detect_price_surge(current, previous):
    """检测价格突然变化"""

    price_current = current['lastPrice']
    price_previous = previous['lastPrice']

    if price_previous == 0:
        return None

    change_pct = ((price_current - price_previous) / price_previous) * 100

    # 3秒内涨跌幅超过2%
    if abs(change_pct) > 2:
        return {
            'type': 'price_surge' if change_pct > 0 else 'price_drop',
            'severity': 'high' if abs(change_pct) > 5 else 'medium',
            'score': min(abs(change_pct) / 5, 1.0),
            'details': {
                'change_pct': round(change_pct, 2),
                'price_previous': price_previous,
                'price_current': price_current
            }
        }

    return None
```

#### 2. 异常放量

```python
def detect_volume_surge(current, previous, history_avg):
    """检测异常放量"""

    volume_current = current['volume']
    volume_previous = previous['volume']

    # 3秒内成交量增加超过平均值的2倍
    volume_increase = volume_current - volume_previous

    if volume_increase > history_avg * 2:
        return {
            'type': 'volume_surge',
            'severity': 'medium',
            'score': 0.7,
            'details': {
                'volume_increase': volume_increase,
                'history_avg': history_avg
            }
        }

    return None
```

#### 3. 强买/强卖

```python
def detect_strong_pressure(current):
    """检测买卖压力"""

    bid_vols = current.get('bidVol', [0, 0, 0, 0, 0])
    ask_vols = current.get('askVol', [0, 0, 0, 0, 0])

    # 计算前3档买卖盘总量
    bid_strength = sum(bid_vols[:3])
    ask_strength = sum(ask_vols[:3])

    if bid_strength == 0 or ask_strength == 0:
        return None

    # 买盘是卖盘的2倍以上
    buy_ratio = bid_strength / ask_strength

    if buy_ratio >= 2:
        return {
            'type': 'strong_buying',
            'severity': 'high' if buy_ratio >= 3 else 'medium',
            'score': min(buy_ratio / 5, 1.0),
            'details': {
                'buy_ratio': round(buy_ratio, 2),
                'bid_strength': bid_strength,
                'ask_strength': ask_strength
            }
        }

    # 卖盘是买盘的2倍以上
    sell_ratio = ask_strength / bid_strength

    if sell_ratio >= 2:
        return {
            'type': 'strong_selling',
            'severity': 'high' if sell_ratio >= 3 else 'medium',
            'score': min(sell_ratio / 5, 1.0),
            'details': {
                'sell_ratio': round(sell_ratio, 2),
                'bid_strength': bid_strength,
                'ask_strength': ask_strength
            }
        }

    return None
```

#### 4. 涨停/跌停

```python
def detect_limit_move(current):
    """检测涨跌停"""

    last_price = current['lastPrice']
    last_close = current['lastClose']

    if last_close == 0:
        return None

    change_pct = ((last_price - last_close) / last_close) * 100

    # A股涨跌停限制（约10%，ST股5%）
    LIMIT_UP = 9.9
    LIMIT_DOWN = -9.9

    if change_pct >= LIMIT_UP:
        return {
            'type': 'limit_up',
            'severity': 'high',
            'score': 1.0,
            'details': {
                'change_pct': round(change_pct, 2),
                'price': last_price
            }
        }

    if change_pct <= LIMIT_DOWN:
        return {
            'type': 'limit_down',
            'severity': 'high',
            'score': 1.0,
            'details': {
                'change_pct': round(change_pct, 2),
                'price': last_price
            }
        }

    return None
```

### 综合异常检测器

```python
class TickAnomalyDetector:
    """Tick异常检测器"""

    def __init__(self):
        self.history = {}  # 历史数据

    def detect(self, symbol, current, previous):
        """综合异常检测"""

        anomalies = []

        # 1. 价格异常
        price_anomaly = detect_price_surge(current, previous)
        if price_anomaly:
            anomalies.append(price_anomaly)

        # 2. 成交量异常
        if symbol in self.history:
            volume_avg = self.history[symbol].get('avg_volume', 0)
            volume_anomaly = detect_volume_surge(current, previous, volume_avg)
            if volume_anomaly:
                anomalies.append(volume_anomaly)

        # 3. 买卖盘压力
        pressure_anomaly = detect_strong_pressure(current)
        if pressure_anomaly:
            anomalies.append(pressure_anomaly)

        # 4. 涨跌停
        limit_anomaly = detect_limit_move(current)
        if limit_anomaly:
            anomalies.append(limit_anomaly)

        return anomalies

    def update_history(self, symbol, data):
        """更新历史数据"""
        if symbol not in self.history:
            self.history[symbol] = {
                'avg_volume': data['volume'],
                'samples': 1
            }
        else:
            # 更新移动平均
            old_avg = self.history[symbol]['avg_volume']
            samples = self.history[symbol]['samples']

            new_avg = (old_avg * samples + data['volume']) / (samples + 1)

            self.history[symbol]['avg_volume'] = new_avg
            self.history[symbol]['samples'] = samples + 1
```

---

## API接口设计

### 1. 监控服务管理

#### 获取监控状态

```http
GET /api/v1/tick-monitor/status
```

**响应**:
```json
{
  "code": 200,
  "data": {
    "enabled": true,
    "core_symbols_count": 100,
    "extended_symbols_count": 200,
    "polling_interval": 3,
    "last_update": "2026-02-05 10:30:15"
  }
}
```

#### 启用/禁用监控

```http
POST /api/v1/tick-monitor/enable
POST /api/v1/tick-monitor/disable
```

---

### 2. 监控列表管理

#### 获取监控列表

```http
GET /api/v1/tick-monitor/watchlist
```

**响应**:
```json
{
  "code": 200,
  "data": {
    "core": ["600519.SH", "000001.SZ", ...],
    "extended": ["600036.SH", "000002.SZ", ...],
    "total": 300
  }
}
```

#### 添加股票

```http
POST /api/v1/tick-monitor/watchlist/add
Content-Type: application/json

{
  "symbols": ["600519.SH", "000001.SZ"],
  "mode": "core"  // or "extended"
}
```

#### 移除股票

```http
POST /api/v1/tick-monitor/watchlist/remove
Content-Type: application/json

{
  "symbols": ["600519.SH"]
}
```

---

### 3. 异常事件查询

#### 查询异常事件

```http
GET /api/v1/tick-monitor/anomalies?level=high&start_date=2026-02-01&symbol=600519.SH
```

**查询参数**:
- `level`: 异常级别（high/medium/low）
- `start_date`: 开始日期
- `end_date`: 结束日期
- `symbol`: 股票代码（可选）

**响应**:
```json
{
  "code": 200,
  "data": {
    "events": [
      {
        "id": "evt_20260205_093215_600519_sh",
        "symbol": "600519.SH",
        "event_time": "2026-02-05 09:32:15",
        "anomaly_type": "price_surge",
        "severity": "high",
        "score": 0.85,
        "details": {
          "change_pct": 4.25,
          "price_previous": 1480,
          "price_current": 1543
        }
      }
    ],
    "total": 15,
    "page": 1
  }
}
```

#### 获取最新异常（实时）

```http
GET /api/v1/tick-monitor/anomalies/latest
```

**响应**:
```json
{
  "code": 200,
  "data": {
    "events": [...],
    "count": 5
  }
}
```

---

### 4. 实时行情接口

#### 获取监控股票实时行情

```http
GET /api/v1/tick-monitor/quotes
```

**响应**:
```json
{
  "code": 200,
  "data": {
    "snapshots": {
      "600519.SH": {
        "lastPrice": 1525,
        "changePct": 3.37,
        "volume": 109123,
        ...
      },
      ...
    },
    "timestamp": "2026-02-05 10:30:15"
  }
}
```

---

## 存储策略

### 分级存储

```python
class AnomalyGradedStorage:
    """异常事件分级存储"""

    def __init__(self, base_dir="data/anomaly_events"):
        self.base_dir = base_dir
        self.high_dir = f"{base_dir}/archive"     # 永久保留
        self.medium_dir = f"{base_dir}/medium"     # 30天
        self.low_dir = f"{base_dir}/low"           # 5天

    def save(self, anomaly_event):
        """保存异常事件（自动分级）"""

        score = anomaly_event['score']

        # 高危：>=0.8分
        if score >= 0.8:
            self._save_to_dir(anomaly_event, self.high_dir)

        # 中等：0.5-0.8分
        elif score >= 0.5:
            self._save_to_dir(anomaly_event, self.medium_dir)

        # 轻微：<0.5分
        else:
            self._save_to_dir(anomaly_event, self.low_dir)

    def cleanup(self):
        """清理过期数据"""
        import time
        from datetime import datetime, timedelta

        # 清理低级异常（5天）
        cutoff_low = datetime.now() - timedelta(days=5)
        self._cleanup_dir(self.low_dir, cutoff_low)

        # 清理中级异常（30天）
        cutoff_medium = datetime.now() - timedelta(days=30)
        self._cleanup_dir(self.medium_dir, cutoff_medium)

        # 高级异常不清理
```

### 存储格式

使用Parquet格式（高效压缩）：

```python
import pandas as pd

def save_anomaly_parquet(event, filepath):
    """保存为Parquet格式"""

    df = pd.DataFrame([event])
    df.to_parquet(filepath, compression='snappy')

def load_anomaly_parquet(filepath):
    """读取Parquet格式"""

    return pd.read_parquet(filepath)
```

---

## 实现方案

### 文件结构

```
backend/
├── services/
│   └── tick_monitor_service.py          # ✅ Tick监控服务
│
├── data/
│   └── anomaly/
│       ├── detector.py                   # ✅ 异常检测器
│       └── storage.py                    # ✅ 分级存储
│
└── api/
    └── api_layer/
        └── api/
            └── v1/
                └── tick_monitor/
                    └── routers.py       # ✅ API路由
```

### 完整服务类

```python
# backend/services/tick_monitor_service.py

import asyncio
import time
from typing import List, Dict, Callable
from loguru import logger
from xtquant import xtdata

from data.anomaly.detector import TickAnomalyDetector
from data.anomaly.storage import AnomalyGradedStorage


class TickMonitorService:
    """Tick监控服务"""

    def __init__(
        self,
        core_symbols: List[str],
        extended_symbols: List[str] = None,
        polling_interval: int = 3
    ):
        self.core_symbols = core_symbols
        self.extended_symbols = extended_symbols or []
        self.polling_interval = polling_interval

        self.detector = TickAnomalyDetector()
        self.storage = AnomalyGradedStorage()

        self.is_running = False
        self.callbacks = []

    def add_callback(self, callback: Callable):
        """添加回调函数"""
        self.callbacks.append(callback)

    def start(self):
        """启动监控服务"""
        if self.is_running:
            logger.warning("Tick监控服务已在运行")
            return

        self.is_running = True
        logger.info("Tick监控服务已启动")

        # 启动核心股票订阅
        if self.core_symbols:
            self._start_subscription_monitor()

        # 启动扩展股票轮询
        if self.extended_symbols:
            self._start_polling_monitor()

    def _start_subscription_monitor(self):
        """启动订阅监控（核心股票）"""

        # 注册回调
        xtdata.register_callback(self._on_tick_update)

        # 订阅
        for symbol in self.core_symbols:
            xtdata.subscribe_quote(symbol, period='tick', count=0)

        logger.info(f"订阅监控已启动: {len(self.core_symbols)} 只股票")

    def _start_polling_monitor(self):
        """启动轮询监控（扩展股票）"""

        def polling_loop():
            previous_snapshots = {}

            while self.is_running:
                try:
                    # 获取快照
                    snapshots = xtdata.get_full_tick(self.extended_symbols)

                    # 检测异常
                    for symbol, data in snapshots.items():
                        if symbol in previous_snapshots:
                            anomalies = self.detector.detect(
                                symbol, data, previous_snapshots[symbol]
                            )

                            for anomaly in anomalies:
                                self._handle_anomaly(symbol, anomaly, data)

                    previous_snapshots = snapshots

                    # 通知回调
                    for callback in self.callbacks:
                        callback(snapshots)

                except Exception as e:
                    logger.error(f"轮询监控错误: {e}")

                # 等待
                time.sleep(self.polling_interval)

        # 启动线程
        import threading
        thread = threading.Thread(target=polling_loop, daemon=True)
        thread.start()

        logger.info(f"轮询监控已启动: {len(self.extended_symbols)} 只股票")

    def _on_tick_update(self, data):
        """订阅回调处理"""
        # 处理推送数据
        ...

    def _handle_anomaly(self, symbol, anomaly, snapshot):
        """处理异常事件"""
        event = {
            'id': f"evt_{int(time.time())}_{symbol}",
            'symbol': symbol,
            'event_time': snapshot.get('timetag'),
            'anomaly_type': anomaly['type'],
            'severity': anomaly['severity'],
            'score': anomaly['score'],
            'details': anomaly['details']
        }

        # 保存到分级存储
        self.storage.save(event)

        # 通知回调
        for callback in self.callbacks:
            callback({'type': 'anomaly', 'data': event})

        logger.warning(f"检测到异常: {symbol} - {anomaly['type']} (分数: {anomaly['score']})")

    def stop(self):
        """停止监控服务"""
        self.is_running = False
        logger.info("Tick监控服务已停止")
```

---

## 待设计模块

以下模块基于XtQuant的tick能力，但需要进一步设计和实现：

### 1. 实时分时图 ⭐ 待设计

**用途**: 显示股票当天的实时分时走势图（9:30-15:00）

**技术方案**:
```python
# 订阅tick推送 + 自己聚合成分钟数据

class RealtimeIntradayChart:
    """实时分时图"""

    def __init__(self, symbol):
        self.symbol = symbol
        self.minute_data = []  # 聚合后的分钟数据

    def start(self):
        """启动实时更新"""

        def on_tick_push(data):
            """tick推送回调"""
            if self.symbol in data:
                tick = data[self.symbol]

                # 聚合tick到分钟级
                self._aggregate_to_minute(tick)

                # 更新分时图
                self._update_chart()

        # 订阅tick推送
        xtdata.subscribe_quote(
            stock_code=self.symbol,
            period='tick',
            count=-1,
            callback=on_tick_push
        )

        # 在独立线程中接收推送
        import threading
        thread = threading.Thread(target=xtdata.run, daemon=True)
        thread.start()

    def _aggregate_to_minute(self, tick):
        """将tick聚合为分钟数据"""
        # tick快照 → 1分钟OHLCV
        # 需要维护当前分钟的状态
        ...
```

**实现要点**:
- ✅ 使用 `subscribe_quote(period='tick')` + callback
- ✅ 在独立线程中调用 `xtdata.run()` 接收推送
- ✅ 自己实现tick→1分钟的聚合逻辑
- ✅ 实时更新分时图（约3秒延迟）

**聚合逻辑**:
```python
def aggregate_tick_to_minute(tick_snapshot):
    """
    将tick快照聚合为1分钟K线

    输入: tick快照 {lastPrice, volume, amount, timetag}
    输出: 1分钟K线 {time, open, high, low, close, volume}
    """
    # 1. 提取时间（精确到分钟）
    timestamp = tick_snapshot['timetag']
    minute_time = timestamp[:14] + '00'  # 20260204 09:32:00

    # 2. 聚合逻辑
    if current_minute != minute_time:
        # 新的一分钟，保存上一分钟
        save_minute_data()
        current_minute = minute_time
        current_bar = {
            'open': tick_snapshot['lastPrice'],
            'high': tick_snapshot['lastPrice'],
            'low': tick_snapshot['lastPrice'],
            'close': tick_snapshot['lastPrice'],
            'volume': 0
        }
    else:
        # 同一分钟，更新当前bar
        current_bar['high'] = max(current_bar['high'], tick_snapshot['lastPrice'])
        current_bar['low'] = min(current_bar['low'], tick_snapshot['lastPrice'])
        current_bar['close'] = tick_snapshot['lastPrice']
```

**与现有功能的区别**:
| 功能 | 数据源 | 更新方式 | 延迟 |
|------|--------|---------|------|
| **分时图** | tick推送 | 主动推送（3秒） | 3秒 |
| **分钟K线** | `get_market_data_ex(period='1m')` | 手动获取 | 延迟较高 |

**状态**: ⏳ 待设计 - 需要设计聚合算法和前端展示

---

### 2. 历史tick序列分析 ⭐ 待设计

**用途**: 回测、历史数据分析、机器学习训练

**技术方案**:
```python
# 下载历史tick数据

class HistoricalTickAnalyzer:
    """历史tick数据分析器"""

    def download_tick_data(self, symbol, start_date, end_date):
        """
        下载历史tick数据

        注意: tick数据量巨大，建议按需下载
        """
        xtdata.download_history_data(
            stock_code=symbol,
            period='tick',  # ⭐ tick周期
            start_time=start_date,
            end_time=end_date
        )

    def load_tick_data(self, symbol, start_date, end_date):
        """加载已下载的tick数据"""
        tick_data = xtdata.get_market_data_ex(
            stock_list=[symbol],
            period='tick',
            start_time=start_date,
            end_time=end_date
        )

        # 返回: DataFrame，每行一个tick
        # 数据量: 每天3-5万行
        return tick_data

    def analyze_tick_patterns(self, tick_data):
        """分析tick模式"""
        # 1. 统计分析
        # 2. 模式识别
        # 3. 特征提取
        ...
```

**数据量估算**:
```
单只股票单日tick数据:
- 活跃股票: 3-5万条
- 一般股票: 1-2万条
- 不活跃股票: 几千条

单只股票单月:
- 约60-100万条
- 文件大小: 约50-100MB

全市场单日:
- 5186只 × 3万条 ≈ 1.5亿条
- 不建议全市场下载
```

**使用建议**:
- ✅ 只下载需要的股票（自选股、异常股）
- ✅ 只下载需要的周期（最近1个月）
- ✅ 下载后及时分析，不长期存储
- ❌ 不要全市场下载（数据量太大）

**应用场景**:
1. **回测验证** - 验证异常检测算法的历史表现
2. **特征工程** - 提取tick特征用于机器学习
3. **模式识别** - 发现价格变化模式
4. **性能分析** - 分析历史交易性能

**状态**: ⏳ 待设计 - 需要设计数据管理和分析流程

---

### 待设计模块优先级

| 模块 | 优先级 | 预计耗时 | 价值 |
|------|--------|---------|------|
| **实时分时图** | 高 | 4小时 | 核心功能，用户体验 |
| **历史tick分析** | 中 | 8小时 | 回测验证，机器学习 |

**实施建议**:
1. 先实现实时分时图（用户可见功能）
2. 后续根据需要实现历史tick分析（研究功能）

---

## 总结

### 设计特点

1. ✅ **基于XtQuant实际能力** - 不假设不存在的功能
2. ✅ **混合模式** - 订阅+轮询，兼顾性能和容量
3. ✅ **实用导向** - 关注实际可用的监控场景
4. ✅ **异常检测** - 多维度检测，动态阈值
5. ✅ **分级存储** - 合理保留，节省空间

### 与v9设计的区别

| 项目 | v9设计 | v10设计 |
|------|--------|---------|
| **数据源** | Hook拦截 | `get_full_tick()` + 订阅 |
| **数据粒度** | 逐笔成交 | 快照变化 |
| **更新频率** | 实时 | 3秒轮询/推送 |
| **监控数量** | 无限 | 核心订阅100只 + 扩展轮询无限制 |

### 下一步

1. 实现核心监控服务
2. 实现异常检测器
3. 实现API接口
4. 编写测试

---

**文档版本**: v10.0.0
**创建日期**: 2026-02-05
**基于**: XtQuant API实际能力

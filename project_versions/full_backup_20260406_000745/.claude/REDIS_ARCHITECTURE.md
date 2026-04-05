# HotDB Redis 跨进程共享架构设计

## 当前架构问题

```
进程A (Uvicorn Worker 1)          进程B (Uvicorn Worker 2)          进程C (Uvicorn Worker 3)
┌─────────────────────┐          ┌─────────────────────┐          ┌─────────────────────┐
│  HotDB Adapter      │          │  HotDB Adapter      │          │  HotDB Adapter      │
│  ├─ L1: 内存缓存     │          │  ├─ L1: 内存缓存     │          │  ├─ L1: 内存缓存     │
│  ├─ L2: 文件(mmap)   │          │  ├─ L2: 文件(mmap)   │          │  ├─ L2: 文件(mmap)   │
│  └─ L3: 元数据JSON   │          │  └─ L3: 元数据JSON   │          │  └─ L3: 元数据JSON   │
└─────────────────────┘          └─────────────────────┘          └─────────────────────┘
         ↓                                 ↓                                 ↓
    data/hotdata/                   data/hotdata/                   data/hotdata/
    (独立文件访问)                   (独立文件访问)                   (独立文件访问)
```

**问题**:
1. 每个 worker 进程独立读取文件，重复 I/O
2. 内存缓存无法共享（每个进程一份）
3. 数据更新时，其他进程无法感知
4. 无法水平扩展（多台服务器无法共享）

---

## 目标架构：Redis 中心化缓存

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                              Redis Cluster (中心化缓存)                               │
│  ┌─────────────────────────────────────────────────────────────────────────────┐   │
│  │  L1: Hot Data (TTL 5min)                                                    │   │
│  │     ├─ hotdb:kline:600519.SH:1d  → Hash {data: bin, meta: json}            │   │
│  │     ├─ hotdb:kline:600519.SH:5m  → Hash {data: bin, meta: json}            │   │
│  │     └─ ...                                                                 │   │
│  ├─────────────────────────────────────────────────────────────────────────────┤   │
│  │  L2: Warm Data (TTL 1hour)                                                  │   │
│  │     ├─ hotdb:kline:600000.SH:1d  → Hash {data: bin, meta: json}            │   │
│  │     └─ ...                                                                 │   │
│  ├─────────────────────────────────────────────────────────────────────────────┤   │
│  │  Pub/Sub: 数据更新通知                                                      │   │
│  │     ├─ channel: hotdb:update:600519.SH:1d  → {action: 'update', ts: xxx}   │   │
│  │     └─ channel: hotdb:invalidate:*          → 批量失效通知                 │   │
│  └─────────────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────────────┘
                                          ↑
                    ┌─────────────────────┼─────────────────────┐
                    │                     │                     │
┌───────────────────▼────┐   ┌───────────▼────────┐   ┌────────▼───────────┐
│  进程A (Worker 1)       │   │  进程B (Worker 2)   │   │  进程C (Worker 3)   │
│  ┌──────────────────┐   │   │  ┌──────────────────┐   │   ┌──────────────────┐   │
│  │ HotDB Adapter    │   │   │  │ HotDB Adapter    │   │   │ HotDB Adapter    │   │
│  │ ├─ L1: 本地缓存   │   │   │  │ ├─ L1: 本地缓存   │   │   │ ├─ L1: 本地缓存   │   │
│  │ ├─ L2: Redis    ◄┼───┼───┼──┼►┼─ L2: Redis    ◄┼───┼───┼►┼─ L2: Redis     │   │
│  │ └─ L3: 文件兜底   │   │   │  │ └─ L3: 文件兜底   │   │   │ └─ L3: 文件兜底   │   │
│  └──────────────────┘   │   │  └──────────────────┘   │   └──────────────────┘   │
└────────────────────────┘   └────────────────────────┘   └────────────────────────┘
```

---

## 核心设计

### 1. 缓存层级

| 层级 | 存储 | TTL | 用途 |
|------|------|-----|------|
| L1 | 进程内 dict | 5分钟 | 极端热点数据（当前股票） |
| L2 | Redis | 60分钟 | 跨进程共享缓存 |
| L3 | 文件(bin) | 永久 | 持久化兜底 |

### 2. Redis Key 设计

```
# K线数据
hotdb:kline:{symbol}:{period}  → Hash
  ├─ data: bytes (parquet序列化的DataFrame)
  ├─ count: int (数据条数)
  ├─ last_time: str (最后数据时间)
  ├─ updated_at: str (更新时间ISO格式)
  └─ source: str (数据来源: hotdb/localdb/online)

# 元数据索引
hotdb:meta:symbols  → Set (所有有数据的股票代码)
hotdb:meta:{symbol}:periods  → Set (该股票支持的周期列表)

# 统计信息
hotdb:stats:hit  → Counter (缓存命中)
hotdb:stats:miss → Counter (缓存未命中)
hotdb:stats:load → Counter (从文件加载次数)
```

### 3. 数据序列化

```python
# 使用 Apache Arrow / Parquet 格式（比 pickle 快10倍，体积小50%）
import pyarrow as pa
import pyarrow.parquet as pq
import io

def df_to_bytes(df: pd.DataFrame) -> bytes:
    """DataFrame → bytes (parquet格式)"""
    table = pa.Table.from_pandas(df)
    buf = io.BytesIO()
    pq.write_table(table, buf, compression='zstd')
    return buf.getvalue()

def bytes_to_df(data: bytes) -> pd.DataFrame:
    """bytes → DataFrame"""
    buf = io.BytesIO(data)
    table = pq.read_table(buf)
    return table.to_pandas()
```

### 4. 缓存一致性

```python
# 使用 Redis Pub/Sub 实现缓存失效通知
class HotDBCacheInvalidator:
    def __init__(self, redis_client):
        self.redis = redis_client
        self.pubsub = redis_client.pubsub()
        self.pubsub.subscribe('hotdb:invalidate:*')
        
    def invalidate(self, symbol: str, period: str = '*'):
        """发布失效通知"""
        key = f'hotdb:kline:{symbol}:{period}'
        self.redis.publish(f'hotdb:invalidate:{symbol}:{period}', 
                          json.dumps({'action': 'invalidate', 'key': key}))
        self.redis.delete(key)
        
    def listen(self):
        """监听失效通知（在后台线程运行）"""
        for message in self.pubsub.listen():
            if message['type'] == 'message':
                data = json.loads(message['data'])
                self._clear_local_cache(data['key'])
```

### 5. 读写流程

#### 读取流程 (get_kline)

```
开始
  ↓
[1] 检查本地缓存(L1) ──命中──► 返回数据
  ↓ 未命中
[2] 检查Redis(L2) ─────命中──► 写入L1 ──► 返回数据
  ↓ 未命中
[3] 读取文件(L3) ──────命中──► 写入L2 ──► 写入L1 ──► 返回数据
  ↓ 未命中
[4] 返回None
```

#### 写入流程 (save_kline)

```
开始
  ↓
[1] 写入文件(L3) ──► 更新元数据
  ↓
[2] 写入Redis(L2) ──► 设置TTL
  ↓
[3] 发布更新通知(Pub/Sub)
  ↓
[4] 其他进程收到通知，清除本地L1缓存
  ↓
结束
```

---

## 代码实现结构

```python
# backend/src/myquant/core/market/adapters/hotdb_adapter.py

class V5HotDBAdapter(V5DataAdapter):
    def __init__(self):
        # ... 现有代码 ...
        
        # Redis 客户端（可选，如果Redis不可用则回退到文件）
        self._redis = self._init_redis()
        self._cache_ttl = 3600  # 1小时
        
    def _init_redis(self) -> Optional[redis.Redis]:
        """初始化Redis连接（失败则返回None，回退到文件模式）"""
        try:
            import redis
            r = redis.Redis(
                host=os.getenv('REDIS_HOST', 'localhost'),
                port=int(os.getenv('REDIS_PORT', 6379)),
                db=int(os.getenv('REDIS_DB', 0)),
                decode_responses=False,  # 二进制数据
                socket_connect_timeout=1,
                socket_timeout=1,
                max_connections=20
            )
            r.ping()
            logger.info("[HotDB] Redis 连接成功")
            return r
        except Exception as e:
            logger.warning(f"[HotDB] Redis 连接失败，回退到文件模式: {e}")
            return None
    
    def get_kline(self, symbols, period='1d', ...):
        """获取K线（支持Redis缓存）"""
        result = {}
        
        for symbol in symbols:
            # 1. 尝试从Redis获取
            if self._redis:
                df = self._get_from_redis(symbol, period)
                if df is not None:
                    result[symbol] = df
                    continue
            
            # 2. 从文件读取（现有逻辑）
            df = self._read_from_file(symbol, period)
            if df is not None:
                # 写入Redis（异步，不阻塞）
                if self._redis:
                    self._async_save_to_redis(symbol, period, df)
                result[symbol] = df
                
        return result
    
    def _get_from_redis(self, symbol: str, period: str) -> Optional[pd.DataFrame]:
        """从Redis获取数据"""
        if not self._redis:
            return None
            
        key = f'hotdb:kline:{symbol}:{period}'
        try:
            data = self._redis.hgetall(key)
            if not data:
                return None
                
            # 反序列化
            df = bytes_to_df(data[b'data'])
            return df
        except Exception as e:
            logger.warning(f"[HotDB] Redis读取失败: {e}")
            return None
```

---

## 部署配置

### Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes --maxmemory 256mb --maxmemory-policy allkeys-lru
    
  backend:
    build: ./backend
    environment:
      - REDIS_HOST=redis
      - REDIS_PORT=6379
      - REDIS_DB=0
    depends_on:
      - redis
    # 多个worker进程
    command: gunicorn -w 4 -k uvicorn.workers.UvicornWorker myquant.main:app

volumes:
  redis_data:
```

### 环境变量

```bash
# .env
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=  # 生产环境设置密码
HOTDB_CACHE_TTL=3600  # Redis缓存1小时
HOTDB_L1_TTL=300      # 本地缓存5分钟
```

---

## 性能预期

| 场景 | 当前(文件) | 目标(Redis) | 提升 |
|------|-----------|------------|------|
| 热点数据读取 | ~10ms | ~1ms | 10x |
| 跨进程共享 | 无 | 有 | 新能力 |
| 内存占用 | N进程×N数据 | 1份共享 | 节省70% |
| 并发能力 | 文件锁竞争 | 无锁 | 线性扩展 |

---

## 实施计划

1. **Phase 1**: 添加 Redis 支持（可选依赖，失败自动回退）
2. **Phase 2**: 添加 Pub/Sub 缓存同步
3. **Phase 3**: 移除 L1 本地缓存（如果Redis性能足够）
4. **Phase 4**: 多服务器部署验证

---

**下一步**: 确认设计后，开始 Phase 1 实现
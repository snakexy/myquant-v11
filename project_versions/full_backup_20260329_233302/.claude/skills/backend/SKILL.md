# MyQuant v11 后端开发规范

## 运行环境
- Python 3.11.8，虚拟环境：`E:/MyQuant_v11/.venv/`
- 启动命令（手动重启，不依赖 --reload）：
  ```bash
  cd E:/MyQuant_v11/backend
  E:/MyQuant_v11/.venv/Scripts/uvicorn.exe myquant.main:app --port 8000
  ```

## 代码风格
- 使用 `loguru` 代替 `print`
- 类型注解必须完整
- 异步函数使用 `async/await`
- 错误处理具体，不捕获通用 Exception

## 分层规范

### API 路由层（`api/`）
- 只做参数校验和路由转发，**不含业务逻辑**
- 调用 Service 层，不直接调用 Adapter
```python
@router.get("/kline/{symbol}")
async def get_kline(symbol: str, period: str = "1d"):
    return await kline_service.get_kline(symbol, period)
```

### Service 层（`core/*/services/`）
- 包含业务逻辑和数据源选择逻辑
- 通过 `get_adapter()` 获取 Adapter，**不能直接实例化**
```python
from core.market.adapters import get_adapter

adapter = get_adapter("pytdx2")  # 正确
adapter = PyTdx2Adapter()        # ❌ 错误
```

### Adapter 层（`core/*/adapters/`）
- 对接具体数据源，负责格式转换和单位统一
- 单例模式（AdapterFactory 缓存实例）

## 架构违规快速检测

**定期运行，确保无违规：**
```bash
# 1. 检查直接实例化 Adapter（应改用 get_adapter）
grep -rn "V5.*Adapter()" backend/src/myquant/ | grep -v __pycache__

# 2. 检查旧路径残留（重构后必查）
grep -rn "adapters\.v5\|adapters/v5" backend/src/myquant/ | grep -v __pycache__
```

两条命令输出均为空 = 无违规 ✅

## API 响应格式

**直接返回 Pydantic 模型**（单资源响应）：
```python
class KlineDataResponse(BaseModel):
    symbol: str
    period: str
    data: List[KlineItem]
    count: int
```

**统一包装**（批量/复杂响应）：
```python
class MarketResponse(BaseModel):
    code: int = 0
    data: Optional[dict] = None
    message: str = "success"
```

## 错误处理
```python
raise HTTPException(status_code=503, detail="数据源不可用")  # 业务错误
raise HTTPException(status_code=400, detail="无效的股票代码")  # 参数错误
```

## 日志规范
```python
from loguru import logger
logger.info("[Market] 获取K线: {} {}", symbol, period)
logger.debug("[Adapter] 使用: {}", adapter_name)
logger.warning("[Fallback] 降级到: {}", fallback)
logger.error("[Error] 获取失败: {}", e)
```

## 已知问题
- `uvicorn --reload` 在 Windows 上不可靠，改动后必须手动重启
- pytdx2 的 `get_security_bars` 只有5个参数，没有 `fq_type`
- TdxQuant SDK 是单例，不能重复初始化（AdapterFactory 已处理）

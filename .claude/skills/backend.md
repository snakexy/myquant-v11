# MyQuant v11 后端开发规范

## 代码风格
- 使用 `loguru` 代替 `print`
- 类型注解必须完整
- 异步函数使用 `async/await`
- 错误处理具体，不捕获通用 Exception

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

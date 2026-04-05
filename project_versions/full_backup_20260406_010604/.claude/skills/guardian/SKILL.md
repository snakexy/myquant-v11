# Guardian - 架构守护者

检查代码是否符合 MyQuant V5 架构规范。

## 触发条件

- 修改涉及 HotDB/Service/Adapter/多层架构
- 不确定修改是否符合架构规范
- 代码审查时

## 架构规范检查项

### 数据流方向（绝对禁止违反）
```
前端 → API路由层(api/) → Service层(core/*/services/) → Adapter层(core/*/adapters/) → 数据源
```

### 关键检查点

1. **HotDB 检查**
   - ❌ 禁止：HotDB 直接调用 Adapter
   - ✅ 正确：HotDB → KlineService → Adapter

2. **Service 层检查**
   - ❌ 禁止：Service 直接 `TdxQuantAdapter()`
   - ✅ 正确：Service 用 `get_adapter('tdxquant')`

3. **API 层检查**
   - ❌ 禁止：API 层直接调用 Adapter
   - ✅ 正确：API → Service → Adapter

## 使用方式

```
/guardian <文件路径>
```

或

```
Agent: "检查 backend/src/myquant/core/market/services/hotdb_service.py 是否违反 V5 架构规范，重点关注：\n1. HotDB 是否直接调用 Adapter\n2. Service 是否正确使用 get_adapter()\n3. 数据流是否符合 前端→API→Service→Adapter→数据源"
```

## 输出

架构守护者检查报告，包含：
- 检查结果（通过/违规）
- 违规详情（如有）
- 建议修正方案

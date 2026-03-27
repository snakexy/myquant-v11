---
name: pytdx2-api-differences
description: |
  pytdx2 与 pytdx 的 API 差异。Use when: (1) get_security_bars 报参数错误，
  (2) 从 pytdx 迁移到 pytdx2 后数据返回 None，(3) 调用行情 API 无数据。
  核心差异：pytdx2.get_security_bars 只有5个参数，没有 fq_type 参数。
author: Claude Code
version: 1.0.0
date: 2026-03-22
---

# pytdx2 与 pytdx API 差异

## 问题
从 pytdx 迁移到 pytdx2 后，`get_security_bars` 多传了 `fq_type` 参数导致返回 None。

## 触发条件
- `get_security_bars` 返回 None 而不报错
- 连接成功但拿不到数据
- 代码里调用 `api.get_security_bars(category, market, code, start, count, fq_type)`

## pytdx2 正确签名

```python
# ❌ pytdx 的签名（6个参数）
api.get_security_bars(category, market, code, start, count, fq_type)

# ✅ pytdx2 的签名（5个参数，无 fq_type）
api.get_security_bars(category, market, code, start, count)
```

## 其他差异

| 方法 | 状态 | 说明 |
|------|------|------|
| `setup()` | 可选 | 调用失败不影响连接 |
| `get_security_quotes(batch)` | 相同 | batch 是 (market, code) 元组列表 |
| `get_xdxr_info(market, code)` | 相同 | 获取除权信息 |

## 验证
```python
api = TdxHq_API(heartbeat=False)
api.connect("180.153.18.172", 80)
data = api.get_security_bars(9, 0, "000001", 0, 5)  # 5个参数
assert data is not None and len(data) > 0
```

## 注意
- pytdx2 存放在 `backend/external/pytdx2/`（本地包，非 pip 安装）
- pyproject.toml 的 `where = ["src", "external"]` 确保能被 import

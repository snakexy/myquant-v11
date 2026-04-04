---
name: python-silent-import-in-try-except
description: |
  try/except 块吞掉 ImportError，导致错误的 import 路径完全静默失败。
  Use when: (1) 代码在 try/except 里做 lazy import，(2) 架构重构后路径变了但旧文件没更新，
  (3) 代码"正常运行"但某个功能实际上悄悄跳过了。
  典型场景：从旧路径 `adapters/v5/pytdx_adapter` 重构到平铺 `adapters/pytdx_adapter`，
  旧文件里的 lazy import 因为 except: pass 而静默失败，程序不报错但功能缺失。
author: Claude Code
version: 1.0.0
date: 2026-03-23
---

# Python try/except 静默吞掉 ImportError

## 问题

代码重构后路径变了，但旧文件里的 lazy import 用 `try/except` 包裹，
`ImportError` 被静默吞掉，程序继续运行但该功能实际上被跳过了。

## 触发条件

- 代码库发生了目录结构重构（如 `adapters/v5/` 改成 `adapters/`）
- 旧文件有类似这样的 lazy import：
  ```python
  try:
      from myquant.core.market.adapters.v5.pytdx_adapter import V5PyTdxAdapter
      adapter = V5PyTdxAdapter()
  except Exception:
      pass  # ← 静默吞掉 ImportError
  ```
- 程序不抛异常，但功能不工作（e.g. 复权数据总是空）

## 根本原因

`except Exception` 或 `except:` 会捕获 `ImportError`，
路径不存在时不报错，整个 try 块被跳过，程序继续执行 fallback（或返回空值）。

## 检测方法

**重构完路径后必须执行这条命令：**

```bash
# 搜索旧路径残留（把 "adapters.v5" 换成实际的旧路径模式）
grep -rn "旧路径关键词" backend/src/ --include="*.py" | grep -v __pycache__
```

**MyQuant 具体命令：**
```bash
grep -rn "adapters\.v5\|adapters/v5" backend/src/myquant/ | grep -v __pycache__
```

输出为空 = 无残留 ✅

## 修复方式

把旧路径替换为新路径：

```python
# ❌ 旧路径（v5 子目录）
from myquant.core.market.adapters.v5.pytdx_adapter import V5PyTdxAdapter

# ✅ 新路径（平铺结构）
from myquant.core.market.adapters.pytdx_adapter import V5PyTdxAdapter
```

**更好的方式**：直接用工厂函数，彻底避免路径硬编码：

```python
from myquant.core.market.adapters import get_adapter
adapter = get_adapter('pytdx')  # 无路径，无迁移问题
```

## 教训：架构重构后的检查清单

1. `grep -rn "旧路径" src/` — 搜索所有旧路径残留
2. `grep -rn "V5.*Adapter()" src/` — 搜索直接实例化（应改用 `get_adapter()`）
3. 检查 `try/except` 块是否吞掉了 `ImportError`
4. 不要用 `except Exception: pass`，至少 `except ImportError: logger.warning(...)`

## MyQuant 特定说明

- v11 适配器路径：`myquant.core.market.adapters.{name}_adapter`（平铺，无 `v5/` 子目录）
- 正确获取方式：`from myquant.core.market.adapters import get_adapter; get_adapter('pytdx')`
- `get_adapter()` 使用单例缓存，不会重复初始化

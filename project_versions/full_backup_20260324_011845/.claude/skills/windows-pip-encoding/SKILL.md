---
name: windows-pip-encoding
description: |
  Windows 上 pip install -r requirements.txt 报 GBK/UTF-8 编码错误。
  Use when: (1) requirements.txt 含中文注释，(2) UnicodeDecodeError gbk codec，
  (3) pip 无法读取 requirements.txt。修复：去掉中文字符，保留纯 ASCII 内容。
author: Claude Code
version: 1.0.0
date: 2026-03-22
---

# Windows pip 安装 requirements.txt 编码错误

## 问题
```
UnicodeDecodeError: 'gbk' codec can't decode byte 0xad in position 93
```
requirements.txt 含有中文注释（如 `# 数据科学`），Windows pip 用 GBK 解码失败。

## 解决方案

用 Python 脚本清除非 ASCII 字符：

```python
with open('requirements.txt', 'rb') as f:
    data = f.read()
# 去除所有非 ASCII 字节
clean = ''.join(chr(b) if b < 128 else '' for b in data)
with open('requirements.txt', 'w', encoding='utf-8') as f:
    f.write(clean)
```

## 预防
写 requirements.txt 只用英文注释：
```
# Web framework        ✅
# Web 框架             ❌
```

## 注意
- 这是 Windows pip 的已知问题，Linux/macOS 不受影响
- 清理后检查包名是否有被截断（中文字符在包名旁边时）

# MyQuant v11 系统防护配置

> 三层防护机制确保代码质量和架构规范

## 配置清单

- [x] settings.json - Hook 配置
- [x] agents/session-starter.json - 会话启动器
- [x] agents/guardian.json - 架构守护者
- [x] agents/validator.json - 代码验证器
- [x] skills/session-start/ - 启动技能
- [x] skills/guardian/ - 架构检查技能
- [x] skills/validator/ - 验证技能

## 三层防护

| 层级 | 触发点 | 功能 |
|------|--------|------|
| L1 | SessionStart | 会话启动检查 |
| L2 | PreToolUse | Write/Edit 强制阻断 |
| L3 | PostToolUse | 修改后验证 |

## 快捷命令

```
/skill session-start    # 启动会话预加载
/skill guardian         # 架构检查说明
/skill validator        # 验证说明
```

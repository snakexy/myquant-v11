# Session Start Skill

每次新会话开始时自动执行，确保上下文完整。

## 触发时机

- 新对话开始
- 用户输入 `/start` 或 `/init`

## 执行流程

1. **读取核心文档**
   ```
   Read: .claude/skills/project-context.md
   Read: CLAUDE.md
   ```

2. **识别任务类型**
   - 后端任务 → 读取 backend skill
   - 前端任务 → 读取 frontend skill
   - 架构任务 → 读取 architecture skill

3. **输出会话报告**
   - 项目状态摘要
   - 关键规则提醒
   - 建议读取的技能文件

## 使用方式

自动触发：新会话开始时会自动执行

手动触发：
```
/start
```

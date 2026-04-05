# MyQuant v11 - AI 工作规则

## 🚨 唯一规则

**改任何文件前，先问用户。**

## 📚 规范文件（自动加载）

以下规范在每次会话自动加载，我必须遵守：

### 核心规范
- **架构约束**: `.claude/rules/architecture.md` - 分层架构、数据流、HotDB补全规范
- **代码风格**: `.claude/rules/coding-style.md` - Python/Vue命名、格式、注释规范
- **测试规范**: `.claude/rules/testing.md` - 测试范围、用例模板、运行方法

### 技能模块（按需加载）
- `architecture` - V5架构规范
- `backend` - Python后端开发规范
- `frontend` - Vue3前端开发规范
- `data-architecture` - 数据架构规范
- `guardian` - 架构守护者
- `validator` - 代码验证器

## 🔒 自动强制（无需我"自觉"）

以下规则由工具自动执行，不需要我"记住"：

1. **PreToolUse Hook** - 改文件前：
   - 检查是否存在计划文件
   - 显示规范文件路径
   - 提醒"先问用户"

2. **PostToolUse Hook** - 改文件后：
   - 显示改动统计（哪些文件被改）
   - 检查架构违规（Service层是否直接import Adapter）
   - 检查文件数量（超过3个文件输出警告）

3. **架构检查脚本** - 自动验证：
   - Service层不能直接import Adapter
   - 单次最多改3个文件
   - 必须通过 `get_adapter()` 获取Adapter实例

## 提交规则

- 不主动提交，由用户决定何时提交
- 提交前确认没有 __pycache__、.env、.venv 等文件混入

# MyQuant v11 - AI 工作规则

## 每次对话开始必做
1. 读取 `.claude/skills/project-context.md` 了解当前项目状态
2. 如果涉及架构决策，读取 `.claude/skills/architecture.md`
3. 如果涉及后端代码，读取 `.claude/skills/backend.md`
4. 如果涉及前端代码，读取 `.claude/skills/frontend.md`

---

## 编码工作流（必须遵守，不得跳过）

### 第一步：理解需求
- 先读相关文件，理解现有代码结构
- 不清楚的地方先问，不要假设
- 复杂任务使用 EnterPlanMode 制定计划，经用户确认后再写代码

### 第二步：写代码前
- 检查是否有现成的实现可以复用
- 确认修改范围，避免影响不相关的代码
- 尽量修改已有文件，而不是新建文件

### 第三步：写完代码后（必做）
- 通读写好的代码，检查逻辑是否正确
- 检查是否有遗漏的边界情况
- 检查是否引入了新的依赖但未安装
- 需要时运行测试验证功能

### 第四步：验证
- API 修改后：用 curl 测试端点
- 前端修改后：提示用户刷新浏览器验证
- 重要改动：重启后端服务再验证

---

## 禁止行为
- ❌ 不读现有代码就直接写新代码
- ❌ 没有计划就改多个文件
- ❌ 写完代码不检查就提交
- ❌ 依赖 uvicorn --reload 热重载（不可靠，手动重启）
- ❌ 过度设计，只做当前需要的

## 提交规则
- 不主动提交，由用户决定何时提交
- 提交前确认没有 __pycache__、.env、.venv 等文件混入

---

## 项目关键路径
- 后端入口: `backend/src/myquant/main.py`
- 路由层: `backend/src/myquant/api/data/`
- 业务逻辑: `backend/src/myquant/core/market/`
- 数据适配器: `backend/src/myquant/core/market/adapters/`
- 前端公共导航: `E:/MyQuant_v10.0.0/frontend/src/components/GlobalNavBar.vue`
- 前端实时行情: `E:/MyQuant_v10.0.0/frontend/src/views/market/RealtimeQuotes.vue`

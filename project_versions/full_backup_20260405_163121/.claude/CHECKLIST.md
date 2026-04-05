# 强制检查清单

> 写代码前必须逐项确认，勾选后才能继续

## Write/Edit 前检查

- [ ] 1. 已用 Read 读取目标文件及所有依赖文件
- [ ] 2. old_string 完全匹配文件内容（含缩进）
- [ ] 3. 只改用户要求的范围，不顺手改其他文件
- [ ] 4. 不违反架构规范（HotDB→Service→Adapter）
- [ ] 5. 涉及多层/架构改动已用 EnterPlanMode
- [ ] 6. 修改后能用 curl/日志/测试验证

## 数据验证检查

- [ ] 返回数据量正常（没有出现 5892→4）
- [ ] 字段类型正确
- [ ] 边界情况处理

## 架构守护检查（如涉及）

- [ ] HotDB 没有直接调用 Adapter
- [ ] Service 使用 get_adapter() 而非直接实例化
- [ ] API 层调用 Service 而非 Adapter

---

**全部勾选后才能执行 Write/Edit**

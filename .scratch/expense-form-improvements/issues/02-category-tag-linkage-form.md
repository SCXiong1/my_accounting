## Parent

[PRD](../PRD.md)

## What to build

基于历史记录实现分类和标签的隐式联动，应用于记账表单。

**后端**：
- 新增 API：查询某分类下用过的标签（GET /v1/categories/{id}/tags）
- 新增 API：查询某标签用过的分类（GET /v1/tags/{id}/categories）
- 查询逻辑基于 expense 和 expense_tag_index 表的关联关系
- 全局标签（未关联任何分类的标签）在未选分类时显示

**前端**：
- CategoryPicker 选中后触发联动，通知 TagCheckbox 更新标签列表
- TagCheckbox 选中后触发联动，通知 CategoryPicker 更新分类列表
- 切换分类时自动清空标签选择
- 清空分类时自动清空标签选择
- 选择全局标签时，分类列表显示所有分类

## Acceptance criteria

- [ ] 选择分类后，标签列表只显示该分类下用过的标签（不含全局标签）
- [ ] 选择标签后，分类列表只显示该标签用过的分类
- [ ] 选择全局标签后，分类列表显示所有分类
- [ ] 切换分类时，已选标签自动清空
- [ ] 清空分类时，已选标签自动清空
- [ ] 未选分类时，标签列表显示所有标签（全局标签 + 各分类下用过的标签）
- [ ] 记账提交功能正常，tag_ids 正确关联

## Blocked by

None - can start immediately

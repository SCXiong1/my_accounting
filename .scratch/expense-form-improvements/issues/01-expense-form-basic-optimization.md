## Parent

[PRD](../PRD.md)

## What to build

在"我的"页面添加"分类管理"入口，并调整记账表单字段顺序。

1. ProfilePage 添加"分类管理"导航链接，指向已有的 /categories 路由
2. ExpenseFormPage 字段顺序调整为：分类 → 标签 → 日期 → 备注 → 金额 → 提交

## Acceptance criteria

- [ ] "我的"页面显示"分类管理"入口，点击可跳转到分类管理页面
- [ ] 记账表单字段顺序为：分类 → 标签 → 日期 → 备注 → 金额 → 提交
- [ ] 新增分类后，记账表单的分类选择器能立即显示新分类
- [ ] 已有功能不受影响（分类 CRUD、记账提交等）

## Blocked by

None - can start immediately

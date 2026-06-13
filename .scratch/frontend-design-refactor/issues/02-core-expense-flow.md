Status: ready-for-agent

# 02 - 记账核心流程视觉重构

## Parent

[PRD - EzExpense 前端视觉重构](../PRD.md)

## What to build

对记账核心流程涉及的 2 个认证页面 + 3 个主页面 + 5 个共享组件进行视觉重构，将所有静态内联样式抽成 scoped CSS class 并引用 Token 变量。

**页面（5 个）：**
- `LoginPage.vue` — 登录表单
- `RegisterPage.vue` — 注册表单
- `HomePage.vue` — 首页仪表盘（今日/周/月/年统计卡片、最近支出列表）
- `ExpenseFormPage.vue` — 新增/编辑支出表单
- `ExpenseListPage.vue` — 支出列表（搜索、筛选、滑动删除、无限滚动）

**组件（6 个）：**
- `AmountField.vue` — 金额输入框
- `CategoryPicker.vue` — 分类选择器
- `TagCheckbox.vue` — 标签多选
- `ExpenseCard.vue` — 支出卡片行
- `FilterPicker.vue` — 筛选 Picker
- `NotifyBar.vue` — 全局通知条（颜色改为引用 CSS 变量：`var(--color-success)` 等）

**改造要点：**
- 所有硬编码颜色值替换为 Token 变量
- 静态内联样式（如 `style="display: flex; padding: 12px;"`）抽成 `<style scoped>` class
- 动态内联样式（`:style="{ width: percent + '%' }"`）保留
- 间距、圆角、阴影统一使用 Token
- NotifyBar 的颜色常量改为引用 CSS 变量

## Acceptance criteria

- [ ] 5 个页面的硬编码颜色/间距/圆角已替换为 Token 变量
- [ ] 6 个组件的硬编码颜色/间距/圆角已替换为 Token 变量
- [ ] 静态内联样式已抽成 scoped CSS class
- [ ] NotifyBar 颜色常量改为引用 CSS 变量
- [ ] `npm run build` 编译通过
- [ ] `npx vitest run` 单元测试通过
- [ ] 不改动任何 `data-testid` 属性
- [ ] 不改动任何中文文案（按钮文字、placeholder、toast 消息等）

## Blocked by

- [01 - Token 基础 + Vant 主题覆盖](01-token-foundation.md)

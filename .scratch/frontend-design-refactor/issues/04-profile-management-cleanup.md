Status: ready-for-agent

# 04 - 个人中心 + 分类标签管理 + 收尾

## Parent

[PRD - EzExpense 前端视觉重构](../PRD.md)

## What to build

对剩余页面进行视觉重构，并执行全局收尾工作（扫描残留硬编码值、App.vue 微调、最终全量 E2E 验证）。

**页面（4 个）：**
- `ProfilePage.vue` — 个人中心（头像、昵称/密码编辑、标签管理/回收站入口）
- `CategoryManagePage.vue` — 分类管理（CRUD、图标/颜色选择器、滑动删除）
- `TagManagePage.vue` — 标签管理（标签 chip 列表、新增/编辑/删除）
- `TrashPage.vue` — 回收站（已删除支出列表、恢复按钮）

**收尾工作：**
- `App.vue` — Tabbar 样式微调（如需要）
- 全局扫描所有 `.vue` 文件，检查是否还有残留的硬编码颜色值（hex 色值如 `#1989fa`、`#323233`、`#969799` 等），替换为 Token 变量
- 检查 `CategoryManagePage.vue` 中的图标/颜色选项数组是否需要更新（14 个 emoji 图标 + 10 个 hex 颜色）
- 运行最终全量 E2E 测试确认所有 31 个用例通过

## Acceptance criteria

- [ ] 4 个页面的硬编码颜色/间距/圆角已替换为 Token 变量
- [ ] 静态内联样式已抽成 scoped CSS class
- [ ] 全局扫描无残留硬编码色值（Vant 组件默认值除外）
- [ ] `npm run build` 编译通过
- [ ] `npx vitest run` 单元测试通过
- [ ] E2E 测试全部通过（S1-S7，31 用例，4 个浏览器项目）
- [ ] 不改动任何 `data-testid` 属性
- [ ] 不改动任何中文文案

## Blocked by

- [01 - Token 基础 + Vant 主题覆盖](01-token-foundation.md)
- [02 - 记账核心流程视觉重构](02-core-expense-flow.md)
- [03 - 统计与图表视觉重构](03-statistics-charts.md)

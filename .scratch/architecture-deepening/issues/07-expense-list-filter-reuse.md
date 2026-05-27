# 07: ExpenseListPage 筛选器复用 CategoryPicker/TagCheckbox

**Status:** done
**PRD:** [architecture-deepening](../PRD.md)
**Stage:** 3 — 前端结构深化
**Dependencies:** 无（独立）

## Summary

ExpenseListPage 内联了分类/标签筛选的 `van-popup` + `van-picker` 逻辑，与 CategoryPicker/TagCheckbox 组件功能重叠。替换为复用。

## Acceptance Criteria

- [ ] ExpenseListPage 的分类筛选器使用 CategoryPicker（或共享的选取器模式）
- [ ] ExpenseListPage 的标签筛选器使用 TagCheckbox（或共享的选取器模式）
- [ ] 筛选行为与当前一致
- [ ] `npm run build` 通过

## Files

- `frontend/src/views/ExpenseListPage.vue` — 替换内联选取器

## Test Strategy

- `npm run build` 类型检查
- 手动验证：筛选器交互正常

## Comments

注意：ExpenseListPage 的筛选是多选的（可同时选多个分类/标签），而 ExpenseFormPage 的 CategoryPicker 是单选。可能需要给 CategoryPicker 和 TagCheckbox 增加 `multiple` prop，或者只在 ExpenseListPage 中复用选取器的 UI 部分。


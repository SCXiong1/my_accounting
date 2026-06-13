# Issue 01: 前端 data-testid 注入 + Helper 重写

Status: done

## Parent
- [PRD: E2E 测试选择器加固](../PRD.md)

## What to build

为所有被 E2E 测试命中的前端元素添加 `data-testid` 属性，并重写 E2E helper 基础设施。纯前端改动 + helper 改动，不涉及测试文件。

### Helper 重写（`e2e/helpers/gestures.ts`）

1. **`swipeCellLeft()`**：移除 XPath，改为 `el.closest('.van-swipe-cell')` 定位。`__vueParentComponent` 保留（Vue 3 技术限制，见下方例外说明）。
2. **`pullDown()`**：移除硬编码坐标，改为动态视口计算：`viewport.width / 2`，从 `viewport.height * 0.3` 拖到 `viewport.height * 0.7`。
3. **`selectPickerOption()`**：`.van-picker__confirm` → `getByRole('button', { name: '确认' })`，新增可选 `pickerTestId` 参数。

### 共享组件加 `data-testid`

1. **`ExpenseCard.vue`**：`expense-card`、`expense-card__amount`、`expense-card__category`、`expense-card__note`、`expense-card__time`
2. **`AmountField.vue`**：`amount-field`
3. **`CategoryPicker.vue`**：`category-picker`、`category-picker__popup`、`category-picker__column`
4. **`TagCheckbox.vue`**：`tag-checkbox`、`tag-checkbox__popup`、`tag-checkbox__group`、`tag-checkbox__cell`
5. **`ChartPie.vue`**：`chart-pie`
6. **`ChartBar.vue`**：`chart-bar`

### 页面组件加 `data-testid`

1. **`App.vue`**：`app-tabbar`
2. **`LoginPage.vue`**：`login-username`、`login-password`、`login-submit`
3. **`RegisterPage.vue`**：`register-username`、`register-hint`、`register-password`、`register-password-confirm`、`register-submit`
4. **`HomePage.vue`**：`home-stat-today`、`home-stat-week`、`home-stat-month`、`home-stat-year`
5. **`ProfilePage.vue`**：`profile-logout`、`profile-nav-tags`
6. **`ExpenseListPage.vue`**：`expense-list-nav`、`expense-list-delete-btn`、`expense-list-swipe-cell`
7. **`ExpenseFormPage.vue`**：`expense-form-nav`、`expense-form-date`、`expense-form-note`、`expense-form-submit`、`expense-form-date-popup`
8. **`StatisticsPage.vue`**：`stats-period-btn`、`stats-chart-pie`、`stats-category-row`、`stats-tag-row`
9. **`CategoryManagePage.vue`**：`category-manage-nav`、`category-manage-add-btn`、`category-manage-popup`、`category-manage-name`、`category-manage-save`、`category-manage-icon`、`category-manage-color`、`category-manage-swipe-cell`、`category-manage-delete-btn`
10. **`TagManagePage.vue`**：`tag-manage-add-btn`、`tag-manage-dialog`、`tag-manage-name`、`tag-manage-confirm`、`tag-manage-tag`

## Acceptance criteria

- [x] 16 个前端组件均有 `data-testid` 属性，命名符合 BEM 规范
- [x] `gestures.ts` 中不再有 XPath 和硬编码坐标
- [ ] `gestures.ts` 中不再有 `__vueParentComponent`（4 处残留，Vue 3 技术限制）
- [x] 前端 `npm run build` 通过（无编译错误）
- [x] 现有 E2E 测试仍全部通过（62/62 chromium），确认 `data-testid` 属性未破坏任何现有功能

## 例外说明

### `__vueParentComponent`（gestures.ts，4 处）

Vant 的 `SwipeCell.open()` 通过 `defineExpose` 暴露在组件实例上。在 Vue 3 中，从 DOM 元素访问组件暴露方法的唯一方式是通过 `__vueParentComponent.proxy`。即使前端加 template ref，从 `page.evaluate` 访问 ref 仍需要此 API。

### `tag-manage-tag-close` 未添加

Vant 的 `van-tag` 组件的 close 图标是内部渲染的 `<i class="van-tag__close">`，没有 `close-icon` slot，无法添加自定义 `data-testid`。

## Blocked by

None

# Issue 02: E2E 测试选择器替换 + 全量验证

Status: done

## Parent
- [PRD: E2E 测试选择器加固](../PRD.md)

## What to build

将所有 7 个 E2E 测试 spec 文件中的脆弱选择器替换为 `getByTestId`，统一 helper 用法，并全量验证测试通过。

### 选择器替换策略

| 选择器类型 | 处理方式 |
|-----------|---------|
| `getByRole` | 保留不动 |
| `getByPlaceholder` | 保留不动 |
| `getByText` 用于定位 | 替换为 `getByTestId` |
| `getByText` 用于断言 | 保留不动 |
| `locator('.van-*')` | 替换为 `getByTestId` |
| `locator('.expense-card*')` | 替换为 `getByTestId` |
| `locator('span[style*="..."]')` | 替换为 `getByTestId` |
| `.first()` / `.nth()` / `.last()` | 用 `getByTestId` 容器消歧 |

### 测试文件更新清单

1. **`s1-auth.spec.ts`**：`getByText('退出登录')` → `getByTestId('profile-logout')`，其余保留
2. **`s2-expense-crud.spec.ts`**：
   - `.expense-card` / `.expense-card__*` → `getByTestId`
   - `.van-popup .van-checkbox-group .van-cell` → `getByTestId('tag-checkbox__cell')`
   - `.van-button--danger` → `getByTestId('expense-list-delete-btn')`，用 `filter({ has: card })` 消歧
3. **`s3-expense-form-interactions.spec.ts`**：
   - `.van-popup` + `.van-picker` → `getByTestId('category-picker__popup')`
   - `.van-field` + hasText + input → `getByTestId('category-picker')` + `.locator('input')`
   - `.van-popup` + hasText 选择标签 → `getByTestId('tag-checkbox__popup')`
   - `.van-cell` + hasText → `getByTestId('tag-checkbox__cell')`
   - `.van-field` + hasText 日期 → `getByTestId('expense-form-date')`
4. **`s4-statistics.spec.ts`**：
   - `canvas.first()` → `getByTestId('chart-pie')` 内的 canvas
   - `getByText('餐饮').first()` → `getByTestId('stats-category-row')` + filter
   - `getByText('餐饮').nth(1)` → `getByTestId('stats-tag-row')` + filter
5. **`s5-pull-refresh-tabbar.spec.ts`**：
   - `.van-tabbar` → `getByTestId('app-tabbar')`
   - `.van-tabbar` + getByText → `getByRole('tab', { name })`
   - `.van-pull-refresh__loading` → 保留（PRD 明确说保留）
6. **`s6-category-manage.spec.ts`**：
   - 删除 inline `openSwipeCell`，统一使用 `gestures.ts` 的 `swipeCellLeft`
   - `popup.getByText('🐱')` → `getByTestId('category-manage-icon')` + filter
   - `popup.locator('span[style*="border-radius: 50%"]')` → `getByTestId('category-manage-color')`
   - `.van-cell` / `.van-swipe-cell` + hasText → `getByTestId('category-manage-swipe-cell')`
   - `.van-button--danger` → `getByTestId('category-manage-delete-btn')`
7. **`s7-tag-manage.spec.ts`**：
   - `.van-nav-bar__title` → `getByText`（仅用于断言）
   - `.van-dialog` → `getByTestId('tag-manage-dialog')`（使用 footer slot）
   - `.van-dialog__confirm` → `getByTestId('tag-manage-confirm')`（使用 footer slot）
   - `.van-tag` → `getByTestId('tag-manage-tag')`
   - `.van-tag__close` → 保留 CSS 选择器（Vant 内部渲染，无 close-icon slot）
   - `getByText('标签管理').click()` → `getByTestId('profile-nav-tags').click()`

## Acceptance criteria

- [x] 7 个测试文件中 `.expense-card*` CSS 选择器已清除
- [x] 7 个测试文件中内联样式选择器已清除
- [x] `s6-category-manage.spec.ts` 不再有 inline `openSwipeCell`
- [x] `getByRole` 和 `getByPlaceholder` 保留不动
- [x] `getByText` 不再用于元素定位（仅用于断言）
- [x] 全量 E2E 测试 62/62 通过（chromium）
- [ ] 7 个测试文件中 `.van-*` CSS 选择器残留 3 处（Vant 技术限制，见下方例外）
- [ ] 位置选择器残留 1 处（s6 颜色选择器 `.first()`，行为语义明确）

## 例外说明

### `.van-tag__close`（s7，1 处）

Vant 的 `van-tag` 组件的 close 图标是内部渲染的 `<i class="van-tag__close">`，没有 `close-icon` slot，无法添加自定义 `data-testid`。

### `.van-pull-refresh__loading`（s5，2 处）

PRD 明确说保留（"Vant 不换，且无对应 data-testid"）。

### s6 `.first()` 选颜色（1 处）

`popup.getByTestId('category-manage-color').first().click()` — 行为语义明确（选任意颜色），可接受。

## Blocked by

- [01-infrastructure-and-shared-components.md](01-infrastructure-and-shared-components.md)

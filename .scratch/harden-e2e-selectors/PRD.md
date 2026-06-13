# PRD: E2E 测试选择器加固

**Status:** ready-for-agent
**Branch:** feat/harden-e2e-selectors
**Base:** master

## Problem Statement

项目即将进行前端大改（UI 库 Vant 4 不换，其他都可能变）。当前 E2E 测试套件（7 个 spec 文件，76 个测试用例）中存在 ~40 个脆弱选择器，包括：

- Vant 内部 CSS 类选择器（`.van-tabbar`、`.van-popup`、`.van-dialog`、`.van-swipe-cell`、`.van-button--danger` 等）
- 自定义 BEM 类选择器（`.expense-card`、`.expense-card__amount` 等）
- 内联样式选择器（`span[style*="border-radius: 50%"]`）
- XPath 表达式（`ancestor::*[contains(@class, "van-swipe-cell")]`）
- Vue 3 内部 API（`__vueParentComponent.proxy.open('right')`）
- 位置选择器（`.first()`、`.nth(1)`、`.last()`）

这些选择器在前端大改时会导致大面积测试失败，无法区分是选择器失效还是功能回归。

## Solution

在前端大改之前，将所有脆弱选择器统一替换为语义化选择器：

1. 给所有被 E2E 测试命中的前端元素添加 `data-testid` 属性（BEM 命名风格）
2. 将 CSS 选择器、XPath、内联样式选择器替换为 `getByTestId()`
3. 保留 `getByRole()` 选择器（可访问性测试价值高）
4. `getByText()` 只用于内容断言，不再做元素定位
5. 重写 `gestures.ts` helper，移除 Vue 内部 API 和硬编码坐标

## User Stories

1. 作为开发者，我希望 E2E 测试使用 `data-testid` 选择器，这样前端重构时测试不会因 DOM 结构变化而失败
2. 作为开发者，我希望保留 `getByRole` 选择器，这样测试同时验证可访问性语义
3. 作为开发者，我希望 `getByText` 只用于内容断言，这样选择器职责清晰
4. 作为开发者，我希望 `swipeCellLeft` helper 使用 Vant 公开 API，这样不依赖 Vue 内部实现
5. 作为开发者，我希望 `pullDown` helper 动态计算坐标，这样不同视口尺寸下测试都能通过
6. 作为开发者，我希望 `selectPickerOption` helper 使用语义选择器，这样不依赖 Vant 内部 DOM 结构
7. 作为开发者，我希望 S6 的 `openSwipeCell` 和 `gestures.ts` 的 `swipeCellLeft` 统一实现，这样消除重复代码
8. 作为开发者，我希望 `data-testid` 命名沿用 BEM 风格，这样与项目现有 CSS 类命名一致
9. 作为开发者，我希望加固后 76/76 测试全部通过，这样确认选择器替换没有破坏功能
10. 作为开发者，我希望加固完成后能安全地进行前端大改，这样测试能及时发现真正的功能回归

## Implementation Decisions

### 选择器策略

| 选择器类型 | 处理方式 |
|-----------|---------|
| `getByRole` | 保留不动，可访问性测试价值高 |
| `getByPlaceholder` | 保留不动，足够稳定 |
| `getByText` | 只用于内容断言（`expect(...).toHaveText`），不再做元素定位 |
| `locator('.van-*')` | 替换为 `getByTestId` |
| `locator('.expense-card*')` | 替换为 `getByTestId` |
| `locator('span[style*="..."]')` | 替换为 `getByTestId` |
| XPath / Vue 内部 API | 替换为 `getByTestId` + ref 公开 API |
| `.first()` / `.nth()` / `.last()` | 用 `getByTestId` 消歧 |

### data-testid 命名规范

沿用项目 BEM 风格：`data-testid="expense-card__amount"`

### Helper 重写策略

**swipeCellLeft**：移除 XPath 和 `__vueParentComponent` 调用，改为通过 `data-testid` 定位 swipe-cell，用 `page.evaluate` 调用 Vant 公开 API `.open('right')`。需要前端给 `van-swipe-cell` 加 `ref`。

**pullDown**：移除硬编码坐标 `mouse.move(200, 100)` / `mouse.move(200, 400)`，改为动态计算视口中心点：`viewport.width / 2`，从 `viewport.height * 0.3` 拖到 `viewport.height * 0.7`。

**selectPickerOption**：`.van-picker-column` → `getByTestId`，`.van-picker__confirm` → `getByRole('button', { name: '确认' })`。

**统一 openSwipeCell**：删除 S6 的 inline `openSwipeCell`，统一调用 `gestures.ts` 的 `swipeCellLeft`。

### 前端组件 data-testid 清单

**共享组件：**
- `ExpenseCard`：`expense-card`、`expense-card__amount`、`expense-card__category`、`expense-card__note`、`expense-card__time`
- `AmountField`：`amount-field`
- `CategoryPicker`：`category-picker`、`category-picker__popup`、`category-picker__column`
- `TagCheckbox`：`tag-checkbox`、`tag-checkbox__popup`、`tag-checkbox__group`、`tag-checkbox__cell`
- `ChartPie`：`chart-pie`
- `ChartBar`：`chart-bar`

**页面组件：**
- `App`：`app-tabbar`
- `LoginPage`：`login-username`、`login-password`、`login-submit`
- `RegisterPage`：`register-username`、`register-hint`、`register-password`、`register-password-confirm`、`register-submit`
- `HomePage`：`home-stat-today`、`home-stat-week`、`home-stat-month`、`home-stat-year`
- `ExpenseListPage`：`expense-list-nav`、`expense-list-delete-btn`（swipe-cell 需加 ref）
- `ExpenseFormPage`：`expense-form-nav`、`expense-form-date`、`expense-form-note`、`expense-form-submit`、`expense-form-date-popup`
- `StatisticsPage`：`stats-period-btn`、`stats-chart-pie`、`stats-category-row`、`stats-tag-row`
- `ProfilePage`：`profile-logout`
- `CategoryManagePage`：`category-manage-nav`、`category-manage-add-btn`、`category-manage-popup`、`category-manage-name`、`category-manage-save`、`category-manage-icon`、`category-manage-color`、`category-manage-swipe-cell`、`category-manage-delete-btn`（swipe-cell 需加 ref）
- `TagManagePage`：`tag-manage-add-btn`、`tag-manage-dialog`、`tag-manage-name`、`tag-manage-confirm`、`tag-manage-tag`、`tag-manage-tag-close`

## Testing Decisions

### 验证标准

- [x] 加固后 62/62 E2E 测试全部通过（chromium，webkit 未安装）
- [x] 代码中不再有 `.expense-card*` CSS 选择器
- [x] 代码中不再有 XPath、内联样式选择器
- [x] `getByRole` 和 `getByPlaceholder` 保留不动
- [x] `getByText` 只用于 `expect(...).toHaveText` 断言
- [ ] 代码中 `.van-*` CSS 选择器残留 3 处（Vant 技术限制）
- [ ] `__vueParentComponent` 残留 4 处（Vue 3 技术限制）

### 例外（Vant/Vue 3 技术限制）

1. `.van-tag__close` — Vant 内部渲染，无 close-icon slot
2. `.van-pull-refresh__loading` — PRD 明确保留
3. `__vueParentComponent` — Vue 3 中从 DOM 元素访问组件暴露方法的唯一方式

### 不需要测试的内容

- 前端组件本身的功能不变，不需要新增单元测试
- `data-testid` 属性是纯粹的测试辅助属性，不影响运行时行为

## Out of Scope

- 前端视觉/样式改动（属于后续 frontend-design 分支）
- 前端组件结构重构（属于后续大改分支）
- 新增 E2E 测试用例（只加固现有选择器）
- Vant UI 库升级
- CI/CD 配置变更

## Further Notes

### 实施顺序

1. 先给前端组件加 `data-testid`（16 个文件）
2. 再重写 `gestures.ts` helper（3 个函数）
3. 最后逐个更新 E2E 测试文件（7 个 spec）
4. 每批改完运行测试验证

### 风险

- `van-swipe-cell` 的 `ref` + `page.evaluate` 调用方式需要验证 Vant 4 的 `open()` 方法是否通过 ref 可用
- `pullDown` 的动态坐标计算需要在不同设备尺寸下验证（Desktop Chrome、Pixel 7、iPhone 14）

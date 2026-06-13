Status: ready-for-agent

# EzExpense 前端视觉重构 — 温暖柔和风格

## Problem Statement

EzExpense 的前端当前使用 Vant 4 默认蓝色主题，没有统一的设计 Token 体系，颜色值散落在各处（4 个 CSS 变量覆盖、10+ 硬编码 hex 值、组件内联样式），视觉上"能用但没有设计感"。作为一个高频使用的个人记账工具，当前的冷色调默认风格缺乏辨识度和情感温度。

## Solution

对前端样式层进行渐进式重构，建立统一的设计 Token 体系（CSS 变量），将视觉风格从 Vant 默认蓝色主题切换为"温暖柔和"风格（奶油白底色 + 琥珀橙主色 + 圆润卡片 + 暖色调阴影），同时保持 Vant 组件库不变，确保所有现有测试通过。

## User Stories

1. 作为移动端用户，我希望看到温暖的奶油色页面背景而不是冰冷的白色，这样记账时感觉更舒适
2. 作为移动端用户，我希望按钮和强调元素使用琥珀橙色而不是默认蓝色，这样界面有辨识度
3. 作为移动端用户，我希望卡片有更大的圆角和柔和的暖色调阴影，这样界面看起来更圆润友好
4. 作为移动端用户，我希望弹窗、Picker、Tabbar 等 Vant 组件也融入温暖色调，这样视觉体验一致
5. 作为移动端用户，我希望统计图表的颜色和整体风格协调，这样看图表时不会割裂
6. 作为移动端用户，我希望通知 Toast 的颜色也融入温暖风格，这样整体体验统一
7. 作为开发者，我希望所有颜色、间距、圆角、阴影都通过 CSS 变量统一管理，这样后续改主题只需改 Token
8. 作为开发者，我希望静态内联样式被抽成 scoped CSS class，这样代码更整洁且引用 Token 更自然
9. 作为开发者，我希望 E2E 测试全部通过（S1-S7，31 个用例），这样确认重构没有破坏功能
10. 作为开发者，我希望前端单元测试全部通过（feedback.ts、auth store），这样确认重构没有破坏逻辑
11. 作为开发者，我希望 `npm run build`（vue-tsc + vite）编译通过，这样确认类型安全

## Implementation Decisions

### 1. 保留 Vant 组件库，只改样式层

Vant 4 的 23 个 van-* 组件和 2 个函数调用保持不变。E2E 测试中有 3 个 CSS 选择器直接依赖 Vant 内部类名（`.van-swipe-cell`、`.van-pull-refresh__loading`、`.van-tag__close`），替换组件会导致这些测试全部重写。Vant 的 CSS 变量系统（`--van-*`）已足够支撑主题定制。

### 2. 设计风格：温暖柔和

- 奶油/米白底色（`#FFF9F0`）替代默认白底
- 琥珀橙主色（`#E8915A`）替代默认蓝色
- 柔和的功能色（绿 `#7DB88B`、红 `#D96B6B`、蓝 `#7BA7C9`）
- 大圆角（卡片 12px、弹窗 16px、药丸 9999px）
- 暖色调阴影（rgba 基于暖黑 `#2D2A26` 而非纯黑 `#000`）

### 3. 设计 Token 体系（深度版）

新建 `tokens.css`，定义完整的 Token 变量集，包含：
- 6 个基础色（背景、表面、文字三级、边框）
- 5 个功能色（主色、主色浅、成功、危险、信息）
- 6 个间距 Token（基于 4px 网格：4/8/12/16/24/32）
- 4 个圆角 Token（8/12/16/9999）
- 3 个阴影 Token（sm/md/lg）
- 8 色图表调色板

同时覆盖约 20 个 Vant CSS 变量（`--van-primary-color`、`--van-background`、`--van-text-color` 等全局性变量），让 Vant 组件自动融入温暖风格。

### 4. 字体：系统字体栈

使用各平台原生字体，零加载开销：`-apple-system, "SF Pro Text", "PingFang SC", "Helvetica Neue", "Noto Sans SC", sans-serif`。

### 5. 图表和 NotifyBar 的颜色处理

- NotifyBar 引用 CSS 变量（`var(--color-success)` 等），因为它渲染在 DOM 中
- ECharts `TAG_PALETTE` 在 JS 中直接定义 8 个 hex 值，值和 Token 色板保持一致，但不引用 CSS 变量（ECharts option 是纯 JS 对象）

### 6. 内联样式清理

改造组件和页面时，将静态内联样式（如 `style="display: flex; padding: 12px;"`）抽成 `<style scoped>` 中的 CSS class 并引用 Token。动态内联样式（`:style="{ width: percent + '%' }"`）保留。

### 7. 现有 CSS class 原地改造

`global.css` 中的 `.page-container`、`.stat-card`、`.expense-card` 等 class 保持名称不变，将内部硬编码值替换为 Token 变量。

### 8. 渐进式 4 阶段实施

| 阶段 | 范围 | 验证 |
|---|---|---|
| 1. Token 基础 | 新建 `tokens.css`，改 `global.css`，改 `main.ts`，扩展 Vant 变量覆盖 | build + vitest + E2E |
| 2. 组件层 | 8 个共享组件（AmountField、CategoryPicker、ChartBar、ChartPie、ExpenseCard、FilterPicker、NotifyBar、TagCheckbox） | build + vitest |
| 3. 页面层 | 10 个页面（Home、Login、Register、ExpenseList、ExpenseForm、Statistics、Profile、CategoryManage、TagManage、Trash） | build + vitest |
| 4. 收尾 | App.vue 微调、全局扫描残留硬编码值、图表色板更新 | build + vitest + E2E |

## Testing Decisions

### 测试验证点

- **构建验证**：`npm run build`（vue-tsc 类型检查 + vite 生产构建）在每个阶段结束时运行
- **单元测试**：`npx vitest run` 在每个阶段结束时运行，覆盖 `feedback.test.ts`（3 个用例）和 `auth.test.ts`（2 个用例）
- **E2E 测试**：`cd e2e && npm test` 仅在阶段 1 和阶段 4 运行，覆盖 S1-S7 共 31 个用例，跨 4 个浏览器项目（Desktop Chrome、Desktop Safari、Pixel 7、iPhone 14）

### 不需要新增测试

本次是纯视觉重构（CSS/样式变更），不涉及新的业务逻辑或交互行为。现有测试覆盖了所有用户可见的行为（表单提交、弹窗交互、滑动删除、下拉刷新、图表渲染等），足以验证重构未破坏功能。

### 关键约束

- E2E 测试依赖 `data-testid` 属性（约 40 个）、文本内容选择器、角色选择器、以及 3 个 Vant 内部 CSS 选择器。本次重构不改动任何 `data-testid`、不改动任何中文文案、不改动 Vant 组件结构，因此 E2E 选择器不受影响。

## Out of Scope

- Vant 组件替换或升级
- 新增页面或功能
- 暗色模式支持
- 响应式断点调整（当前仅移动端）
- 后端 API 变更
- PWA manifest 颜色更新（`theme_color`、`background_color`）
- 动画或过渡效果

## Further Notes

- Token 变量的命名遵循 `--category-detail` 模式（如 `--color-primary`、`--space-md`、`--radius-lg`），与 Vant 的 `--van-*` 命名空间隔离
- Vant CSS 变量覆盖放在 `global.css` 的 `:root` 块中，与现有覆盖方式一致
- 图表调色板 `TAG_PALETTE` 的 8 个色值手动与 Token 色板保持一致，不需要机械绑定
- 阶段 1 完成后 Vant 组件会自动变色（CSS 变量生效），这一步就能看到显著的视觉效果

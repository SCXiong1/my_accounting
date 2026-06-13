Status: ready-for-agent

# 01 - Token 基础 + Vant 主题覆盖

## Parent

[PRD - EzExpense 前端视觉重构](../PRD.md)

## What to build

建立完整的 CSS 设计 Token 体系，并通过 Vant CSS 变量覆盖让所有 Vant 组件自动融入温暖柔和风格。

具体包括：

1. 新建 `tokens.css`，定义所有设计 Token 变量：
   - 6 个基础色：`--color-bg`（`#FFF9F0`）、`--color-surface`（`#FFFFFF`）、`--color-text-primary`（`#2D2A26`）、`--color-text-secondary`（`#8C8580`）、`--color-text-placeholder`（`#C4BEB8`）、`--color-border`（`#EDE8E3`）
   - 5 个功能色：`--color-primary`（`#E8915A`）、`--color-primary-light`（`#FCEEE4`）、`--color-success`（`#7DB88B`）、`--color-danger`（`#D96B6B`）、`--color-info`（`#7BA7C9`）
   - 6 个间距：`--space-xs`（4px）、`--space-sm`（8px）、`--space-md`（12px）、`--space-lg`（16px）、`--space-xl`（24px）、`--space-2xl`（32px）
   - 4 个圆角：`--radius-sm`（8px）、`--radius-md`（12px）、`--radius-lg`（16px）、`--radius-full`（9999px）
   - 3 个阴影：`--shadow-sm`、`--shadow-md`、`--shadow-lg`（rgba 基于暖黑 `#2D2A26`）
   - 系统字体栈变量

2. 在 `global.css` 的 `:root` 中扩展 Vant CSS 变量覆盖（约 20 个），包括：
   - `--van-primary-color`、`--van-success-color`、`--van-danger-color`
   - `--van-background`、`--van-background-2`
   - `--van-text-color`、`--van-text-color-2`、`--van-text-color-3`
   - `--van-border-color`、`--van-active-color`
   - `--van-border-radius`、`--van-border-radius-sm`、`--van-border-radius-lg`
   - NavBar、Tabbar、Button、Cell 等高频组件的变量
   - `font-family` 系统字体栈声明

3. 将 `global.css` 中所有现有 class（`.page-container`、`.stat-card`、`.expense-card` 等）的硬编码值替换为 Token 变量引用。

4. 在 `main.ts` 中 import `tokens.css`（在 `global.css` 之前）。

## Acceptance criteria

- [ ] `tokens.css` 定义了完整的 Token 变量集（颜色、间距、圆角、阴影、字体）
- [ ] `global.css` 的 `:root` 覆盖了约 20 个 Vant CSS 变量
- [ ] `global.css` 中所有现有 class 的硬编码值已替换为 Token 变量
- [ ] `main.ts` 正确 import `tokens.css`
- [ ] `npm run build` 编译通过（vue-tsc + vite）
- [ ] `npx vitest run` 单元测试通过（feedback.test.ts 3 用例 + auth.test.ts 2 用例）
- [ ] E2E 测试全部通过（S1-S7，31 用例，4 个浏览器项目）
- [ ] 视觉效果：Vant 组件（按钮、弹窗、Tabbar、NavBar 等）自动融入温暖色调

## Blocked by

None - 可以立即开始

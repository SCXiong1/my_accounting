Status: ready-for-agent

# 03 - 统计与图表视觉重构

## Parent

[PRD - EzExpense 前端视觉重构](../PRD.md)

## What to build

对统计页面和图表组件进行视觉重构，将 ECharts 图表的颜色与 Token 色板对齐，页面样式引用 Token 变量。

**页面（1 个）：**
- `StatisticsPage.vue` — 统计页面（周期筛选、分类饼图、标签饼图、月度柱状图）

**组件（2 个）：**
- `ChartPie.vue` — ECharts 饼图/环形图
- `ChartBar.vue` — ECharts 堆叠柱状图

**改造要点：**
- `StatisticsPage.vue` 中的 `TAG_PALETTE` 数组更新为新色板值：`['#E8915A', '#7DB88B', '#7BA7C9', '#D96B6B', '#C49BD9', '#E8C76B', '#6BC5C5', '#B8927A']`
- TAG_PALETTE 值在 JS 中直接定义（不引用 CSS 变量），与 Token 色板保持一致
- 页面和组件中的硬编码颜色/间距/圆角替换为 Token 变量
- 静态内联样式抽成 scoped CSS class
- 图表 ECharts option 中的颜色值（如 `itemStyle.color`）更新为新色板

## Acceptance criteria

- [ ] `TAG_PALETTE` 更新为新色板的 8 个色值
- [ ] `StatisticsPage.vue` 的硬编码值已替换为 Token 变量
- [ ] `ChartPie.vue` 和 `ChartBar.vue` 的硬编码值已替换为 Token 变量
- [ ] 静态内联样式已抽成 scoped CSS class
- [ ] `npm run build` 编译通过
- [ ] `npx vitest run` 单元测试通过
- [ ] 不改动任何 `data-testid` 属性
- [ ] 不改动任何中文文案

## Blocked by

- [01 - Token 基础 + Vant 主题覆盖](01-token-foundation.md)

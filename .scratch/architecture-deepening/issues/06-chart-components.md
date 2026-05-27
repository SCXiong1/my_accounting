# 06: 图表组件提取 + StatisticsPage 去重

**Status:** done
**PRD:** [architecture-deepening](../PRD.md)
**Stage:** 3 — 前端结构深化
**Dependencies:** 建议在 01（withMutate）之后，减轻视图 refactor 工作量

## Summary

StatisticsPage ~300 行，包含内联 ECharts 配置和重复的 loadAll/loadFiltered。提取图表组件，合并加载函数。

## Acceptance Criteria

- [ ] 创建 `ChartPie.vue` 组件：接收 `{ name, amount, percent }[]`，封装 ECharts 饼图
- [ ] 创建 `ChartBar.vue` 组件：接收月度分组数据，封装 ECharts 柱状图
- [ ] 合并 `loadAll()` 和 `loadFiltered()` 为单一 `loadData(options)`
- [ ] 概览获取移入 `statistics` store
- [ ] StatisticsPage 从 ~300 行缩减到 ~120 行
- [ ] `npm run build` 通过
- [ ] 手动验证：统计页面图表展示正常，切换时间范围/分类筛选正常

## Files

- `frontend/src/components/ChartPie.vue` — 新建
- `frontend/src/components/ChartBar.vue` — 新建
- `frontend/src/views/StatisticsPage.vue` — 瘦身
- `frontend/src/stores/statistics.ts` — 新增 overview 获取

## Test Strategy

- `npm run build` 类型检查
- 手动验证图表交互（ECharts DOM 依赖使单元测试不切实际）

## Comments

`useECharts` composable 两个组件内部都需要用。


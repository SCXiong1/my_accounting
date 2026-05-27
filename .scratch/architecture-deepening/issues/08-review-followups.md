# 08: Code Review 跟进优化

**Status:** ready-for-agent
**PRD:** [architecture-deepening](../PRD.md)
**Source:** feature/simplify-code-architecture 分支 review
**Dependencies:** 无

## 优先级排序（性价比）

### P1 — 数据库迁移脚本

**问题**：`ExpenseTagIndex` 新增 `deleted`/`deleted_at` 列，新部署自动创建，已部署实例需手动 ALTER TABLE。

**方案**：在 `backend/` 下创建 `migration_v2.sql`：
```sql
ALTER TABLE expense_tag_index ADD COLUMN deleted INTEGER NOT NULL DEFAULT 0;
ALTER TABLE expense_tag_index ADD COLUMN deleted_at INTEGER NOT NULL DEFAULT 0;
```
并在项目说明书部署章节加一句引用。

### P2 — delete_category 重复查询

**问题**：`category_service.py:delete_category` 先调 `find_or_404` 做关联支出检查，再调 `soft_delete`（内部又做一次 `find_or_404`），同一行查两次。

**方案**：`catalog_core.py` 新增 `soft_delete_obj(db, obj)` —— 接受已查到的 model 对象，跳过重复查询。`delete_category` 改为先 `find_or_404`，检查关联，再 `soft_delete_obj`。

### P3 — ChartBar 类型收窄

**问题**：`ChartBar.vue` 中 `monthlyStats: any[]` 和 `getDetails: (m: any) => DetailItem[]`。

**方案**：定义最小接口 `MonthlyRow { year: number; month: number }`，替换 `any`。

### P4 — _apply_filters 包装删除

**问题**：`_apply_filters` 已拆分为 `_apply_time_filter` + `_apply_tag_category_filter`，但旧包装仍保留，调用方未直接使用子函数。

**方案**：by_category/by_tag/monthly 三处调用改用子函数，删除 `_apply_filters` 包装。

## Acceptance Criteria

- [ ] P1: migration_v2.sql 存在，项目说明书提及
- [ ] P2: delete_category 不做重复查询
- [ ] P3: ChartBar 无 `any` 类型
- [ ] P4: 删除 `_apply_filters` 包装

## Comments

4 项均为低风险优化，可一次 commit 完成。

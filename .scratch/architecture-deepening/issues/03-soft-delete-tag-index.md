# 03: 修复 ExpenseTagIndex 软删除不一致

**Status:** done
**PRD:** [architecture-deepening](../PRD.md)
**Stage:** 1 — 地基
**Dependencies:** 无（独立于 01、02）

## Summary

`update_expense()` 中对标签关联做硬删除（物理 DELETE），与整个系统的软删除策略不一致。改为软删除。

## Acceptance Criteria

- [ ] `ExpenseTagIndex` 模型新增 `deleted`（Integer, default=0）和 `deleted_at`（Integer, nullable）字段
- [ ] `update_expense()` 中将 `delete(ExpenseTagIndex).where(...)` 改为 UPDATE 设置 `deleted=1, deleted_at=now`
- [ ] `_fill_relations()` / `_build_response()` 读取标签关联时加 `deleted=0` 过滤
- [ ] `delete_expense()` 同步软删除关联的标签索引行
- [ ] `test_api.py` 全部 26 个测试通过
- [ ] 数据库迁移脚本（或手动说明：需 `ALTER TABLE expense_tag_index ADD COLUMN deleted ...`）

## Files

- `backend/models/expense_tag_index.py` — 新增 deleted 字段
- `backend/services/expense_service.py` — 改硬删除为软删除

## Test Strategy

- 现有 `test_api.py` 集成测试作为回归安全网
- 重点关注：创建支出（标签关联）→ 更新标签 → 恢复支出 → 标签应保留

## Comments

如果不想改数据库 schema，可以考虑另一种方案：`create_expense` 时复用旧行而非 INSERT 新行。但加 deleted 字段更一致。


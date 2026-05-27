# 05: 统一统计聚合策略

**Status:** done
**PRD:** [architecture-deepening](../PRD.md)
**Stage:** 2 — 后端结构深化
**Dependencies:** 无（独立执行，但建议在 04 之后以保持一致的 service 模式）

## Summary

统计模块三种聚合策略（SQL CASE WHEN / SQL GROUP BY / Python 内存聚合）统一为纯 SQL。`_apply_filters` 接口显式化。

## Acceptance Criteria

- [ ] `monthly` 端点从 Python 字典聚合迁移到 SQL GROUP BY
- [ ] `_apply_filters` 拆分为独立的筛选函数（时间筛选、分类筛选、标签筛选），不在不同查询上下文中混用
- [ ] 删除 `_sum_amount`（已于上一轮优化移除）
- [ ] `_aggregate_tags` 的两次数据库往返合并为一次 JOIN
- [ ] `test_api.py` 全部 26 个测试通过

## Files

- `backend/services/statistics_service.py` — 重构

## Test Strategy

- 现有 `test_api.py` 统计相关测试作为回归
- 可选：为纯 SQL 查询函数写单元测试（对内存 SQLite），验证聚合结果数字正确

## Comments


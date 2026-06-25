# 软删除策略简化：仅 Transaction 保留软删除

## Status: IMPLEMENTED (2026-06-24)

## 背景

原系统所有数据表（expense、expense_category、expense_tag、expense_tag_index）都有软删除（deleted + deleted_at）。重构后简化策略。

## 决策

- Transaction：保留软删除（deleted + deleted_at），支持回收站恢复
- Category：硬删除，无软删除
- Tag：硬删除，无软删除
- TransactionTag：硬删除，无软删除（简化为复合主键）

## 理由

1. **使用频率**：Transaction 误删概率高，需要恢复功能；Category/Tag 删除是管理操作，误删概率低
2. **复杂度**：软删除增加查询复杂度（所有查询需带 deleted=0），Category/Tag 简化后可降低维护成本
3. **数据完整性**：Category/Tag 删除时检查关联 Transaction，硬删除+删除保护比软删除更清晰

## 备选方案

- **全表保留软删除**：保持现有设计，但增加查询复杂度
- **全表硬删除**：简化彻底，但 Transaction 误删无法恢复

## 实施记录

- Category/Tag 模型移除 `SoftDeleteMixin`，改为硬删除
- 新增删除保护：删除 Category/Tag 时检查关联 Transaction，有则拒绝（400）
- `transaction_tag` 关联表为硬删除，随 Transaction 删除级联
- 新增 `test_delete_protection.py` 测试删除保护行为

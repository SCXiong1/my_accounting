# 04: 合并 CRUD 模板（category + tag）

**Status:** done
**PRD:** [architecture-deepening](../PRD.md)
**Stage:** 2 — 后端结构深化
**Dependencies:** 无（独立于阶段 1 的所有 issue）

## Summary

提取 category_service 和 tag_service 中 ~70% 重复的 CRUD 逻辑到共享基类，两个 service 仅保留差异化业务规则。

## Acceptance Criteria

- [ ] 创建 `backend/services/catalog_service.py`，包含通用 CRUD 基类或辅助函数
- [ ] list / create / update / delete / sort 的通用逻辑不重复出现在 category 和 tag service 中
- [ ] 差异化逻辑正确注入：分类删除检查关联支出、标签创建检查重名
- [ ] `category_service.py` 和 `tag_service.py` 大幅缩减（仅含差异逻辑）
- [ ] `test_api.py` 全部 26 个测试通过

## Interface Design

```python
# catalog_service.py — 泛型基类
class CatalogService:
    model: type        # ExpenseCategory | ExpenseTag
    schema_create: type
    schema_update: type
    schema_response: type
    check_before_delete: Callable | None  # 返回 str 错误或 None
    check_before_create: Callable | None

    async def list_models(db, uid) -> list[Model]
    async def create_model(db, uid, data) -> Model
    async def update_model(db, uid, id, data) -> Model
    async def delete_model(db, uid, id) -> dict
    async def sort_models(db, uid, orders) -> list[Model]
```

## Files

- `backend/services/catalog_service.py` — 新建
- `backend/services/category_service.py` — 瘦身为差异化逻辑
- `backend/services/tag_service.py` — 瘦身为差异化逻辑

## Test Strategy

- 现有 `test_api.py` 作为回归安全网
- 可选：为 `CatalogService` 基类方法写单元测试（对内存 SQLite）

## Comments

注意：category 的 list 聚合了 expense_count + total_amount，tag 的 list 聚合了 expense_count。这些聚合查询与 CRUD 基类的关系需要设计好——可以选择不在基类中处理聚合。


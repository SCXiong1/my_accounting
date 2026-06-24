# 核心实体从 Expense 改为 Transaction

## 背景

原系统只支持支出记录，核心实体命名为 `expense`。现需支持收入和支出，核心实体改为 `transaction`，用 `type` 字段区分方向。

## 决策

- 表名：`expense` → `transaction`
- 新增字段：`type`（枚举：income/expense）
- 金额：统一存储正数，方向由 type 决定
- 关联表：`expense_tag_index` → `transaction_tag`，简化为复合主键

## 理由

1. **语义中立**：`transaction` 不绑定「支出」含义，同时支持收入和支出
2. **扩展性好**：未来可增加其他类型（转账、退款）只需扩展枚举
3. **一致性**：Category 和 Tag 也通过 type 字段区分，保持统一设计

## 备选方案

- **保持 expense + 新增 income 表**：两张表增加查询复杂度，统计需要 UNION
- **用 entry/record**：语义太通用，不如 transaction 在金融领域精确

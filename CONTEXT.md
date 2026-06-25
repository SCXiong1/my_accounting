# EzExpense 领域上下文

移动端个人记账 Web 应用，支持收入和支出记录、分类管理、标签筛选、多维度统计分析。

## 语言

**PIN码**:
用户的认证凭证，纯数字4-6位，存储为bcrypt哈希。用于替代传统密码，简化内网家庭使用场景。
_Avoid_: 密码、password、口令

**安全问题**:
用于PIN码重置的固定问题，所有用户共用同一问题。用户回答正确后可重置PIN码。
_Avoid_: 密保问题、安全验证

**Transaction（记账）**:
用户记录的一笔收入或支出。核心实体，包含金额、分类、时间、备注等信息。
_Avoid_: expense（仅指出账）、账单、记录

**Type（类型）**:
Transaction 的方向，枚举值：`income`（收入）、`expense`（支出）。
_Avoid_: direction、kind

**Category（分类）**:
Transaction 的归类，按类型分为收入分类和支出分类。注册时预设常用分类，用户可自定义。
_Avoid_: expense_category（旧表名）、类型

**Tag（标签）**:
Transaction 的自由标记，不区分收入/支出，可跨类型使用。
_Avoid_: expense_tag（旧表名）、标记

**Amount（金额）**:
Transaction 的金额，以「分」为单位的正整数。收入/支出的方向由 Type 决定。
_Avoid_: price、cost

**TransactionTime（记账时间）**:
Transaction 的发生时间，Unix 时间戳（秒）。
_Avoid_: created_at（创建时间，系统自动）、date

**TransactionTag（记账标签关联）**:
Transaction 和 Tag 的多对多关联，复合主键设计。
_Avoid_: expense_tag_index（旧表名）

**User（用户）**:
系统的使用者，所有数据按用户隔离。
_Avoid_: account、member

## 页面术语

**主页（HomePage）**:
应用入口，显示概览卡片（本月收入/支出/净收入/笔数）和最近明细列表。
_Avoid_: 首页、dashboard

**明细页（TransactionListPage）**:
显示收入和支出记录列表，支持按类型/时间/分类/标签筛选，入口通往统计页。
_Avoid_: 支出列表、账单列表

**统计页（StatisticsPage）**:
图表分析页面，入口在明细页。图表按需加载，用户选择图表类型/收支类型/时间范围后生成。
_Avoid_: 报表页、分析页

**记账表单（TransactionFormPage）**:
新增和编辑 Transaction 的表单，顶部有收入/支出切换按钮。
_Avoid_: 记账页、编辑页

## 设计规则

1. **金额整数存储**：以「分」为单位，int64，避免浮点精度问题
2. **时间统一 Unix 秒**：存储和计算用时间戳，展示时按用户时区格式化
3. **软删除仅限 Transaction**：`deleted` + `deleted_at`，Category 和 Tag 硬删除
4. **删除保护**：禁止删除有关联 Transaction 的 Category 或 Tag
5. **用户数据严格隔离**：所有查询带 `uid = ?` 条件
6. **分类标签隐式关联**：Category 和 Tag 通过 Transaction 间接关联，无直接外键
7. **未来账单默认隐藏**：明细页默认只显示到今天的记录，未来账单需主动查看
8. **标签分组显示**：记账表单选择标签时，分组显示「推荐标签」（当前分类历史）和「全部标签」（可折叠）
9. **PIN码认证**：使用纯数字4-6位PIN码替代传统密码，存储为bcrypt哈希
10. **Cookie Session**：使用服务端session，24小时过期，浏览器关闭不自动失效
11. **预置用户**：通过数据库迁移预置两个用户，移除注册功能
12. **安全问题重置**：通过固定安全问题重置PIN码，移除邮箱验证

## 已实施决策

- **ADR-0001** Transaction as Core Entity — 已实施（2026-06-24）：表名 expense→transaction，新增 type 字段
- **ADR-0002** Soft Delete Strategy — 已实施（2026-06-24）：仅 Transaction 保留软删除，Category/Tag 改为硬删除+删除保护

## 实体关系

```
User (1) ──────< (N) Transaction
User (1) ──────< (N) Category
User (1) ──────< (N) Tag
Category (1) ──< (N) Transaction
Transaction (1) >──< (N) Tag   [via TransactionTag]
```

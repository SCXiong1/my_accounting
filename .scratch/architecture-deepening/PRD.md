# PRD: 架构深化——消除浅模块、提升可测试性

**Status:** done
**Branch:** `feature/simplify-code-architecture`
**Base:** `feature/simplify-code` → `master`

---

## Problem Statement

当前代码库存在多个浅模块（interface 几乎和 implementation 一样复杂）和跨模块的样板重复。后端 API 层是纯传递层（26 个路由 = 26 行委托代码），category/tag service 有 ~70% 的 CRUD 模板重复，statistics service 用三种不同策略做同一件事（聚合），前端的错误处理模式在 10 个视图中重复 ~15 次，StatisticsPage 超过 300 行且包含内联 ECharts 配置。这些问题不造成 bug，但持续增加新功能的认知负担和修改成本。

## Solution

一轮系统性的架构深化，按优先级分 4 个阶段执行，降低修改成本并提升 AI 可导航性：

- **阶段 1（地基）**：提取错误处理包装函数 → 解耦 auth store → 修复软删除不一致
- **阶段 2（后端）**：合并 CRUD 模板 → 统一统计聚合策略
- **阶段 3（前端）**：图表组件提取 + StatisticsPage 去重
- **阶段 4（可选）**：API 传递层消除（按需决定）

## User Stories

1. 作为开发者，我想在处理所有 API 变更操作时用一行包装函数替代 5 行 try-catch 样板，减少重复代码
2. 作为开发者，我想让 auth store 独立于 Vue Router，使其可从非组件上下文调用和测试
3. 作为开发者，我想让 ExpenseTagIndex 的删除策略与支出保持一致（软删除），确保数据完整性
4. 作为开发者，我想让 category 和 tag 的 CRUD 操作共享一个通用的 Catelog 基类，这样添加新实体时只需定义差异部分
5. 作为开发者，我想让所有统计 API 使用统一的 SQL 聚合策略，而非三种不同的聚合方式
6. 作为开发者，我想把 ECharts 图表配置封装为独立组件，使其可在多个页面复用
7. 作为开发者，我想让 StatisticsPage 的重复加载函数合并，从 ~300 行缩减到 ~120 行
8. 作为开发者，我想让 ExpenseListPage 的分类/标签筛选器复用已有的 CategoryPicker 和 TagCheckbox 组件
9. 作为开发者，我想让概览数据通过 statistics store 获取，而非各页面直接调 API

## Implementation Decisions

### 阶段 1：地基（零依赖）

**1.1 提取 `withMutate` 错误处理包装函数**

- 位置：`frontend/src/lib/feedback.ts`（已有 `showSuccess`/`showError`/`showTip`）
- 接口：`async function withMutate(fn: () => Promise<void>, successMsg: string, fallbackMsg: string): Promise<void>`
- 行为：调用 fn()，成功时 `showSuccess(successMsg)`，失败时 `showError(getErrorMessage(e, fallbackMsg))`
- 替代所有视图中 ~15 处重复的 try-catch 模式

**1.2 解耦 auth store 与 Router**

- 从 `stores/auth.ts` 移除 `useRouter()` 和 `logout()` 内的 `router.push('/login')`
- `logout()` 只清除 token 和 user 状态
- 方案一（推荐）：在 `App.vue` 中 watch token，token 变为 null 时自动 `router.push('/login')`
- 方案二：让调用 logout 的视图自行处理导航

**1.3 修复 ExpenseTagIndex 软删除**

- `update_expense()` 中将 `delete(ExpenseTagIndex).where(...)` 硬删除改为：批量标记旧关联为 `deleted=1` + 插入新关联
- `ExpenseTagIndex` 模型需新增 `deleted` 和 `deleted_at` 字段（或继承 SoftDeleteMixin）
- `delete_expense()` 中同步软删除关联的标签索引行

### 阶段 2：后端结构深化

**2.1 合并 CRUD 模板（category + tag）**

- 提取共享的 `CatalogService` 基类或泛型辅助函数，处理：
  - `list_models(db, uid)` — 带排序的列表查询
  - `create_model(db, uid, data)` — 计算 display_order 后创建
  - `update_model(db, uid, id, data)` — 查找 + 更新
  - `delete_model(db, uid, id)` — 软删除
  - `sort_models(db, uid, orders)` — 批量更新 display_order
- 差异化逻辑注入：分类删除前检查关联支出、标签创建前检查重名
- 两个 service 文件保留但变薄，仅含差异化逻辑

**2.2 统一统计聚合策略**

- 选择纯 SQL 作为主导策略（overview 的 CASE WHEN 模式已验证可行）
- `monthly` 端点从 Python 内存聚合迁移到 SQL GROUP BY
- `_apply_filters` 接口显式化：`def _apply_time_filters(query, start, end)` + 单独的分类/标签筛选
- 移除非聚合上下文中对 `_apply_filters` 的复用

### 阶段 3：前端结构深化

**3.1 提取图表组件**

- `ChartPie.vue`：接收 `{ name, amount, percent }[]` 数据 + 标题，封装 ECharts 饼图 option
- `ChartBar.vue`：接收月度分组数据 + 图例，封装 ECharts 柱状图 option
- 两个组件内部管理自己的 ECharts 实例（使用 `useECharts`）

**3.2 StatisticsPage 去重**

- 合并 `loadAll()` 和 `loadFiltered()` 为单一 `loadData(options)` 函数
- 概览获取移入 `statistics` store

**3.3 ExpenseListPage 筛选器复用**

- 将内联的 `van-popup` + `van-picker` 替换为 `CategoryPicker` 和 `TagCheckbox` 组件

### 阶段 4（可选）：API 传递层消除

- 将 6 个 `api/*.py` 路由注册合并到集中的路由模块
- 收益有争议：FastAPI 社区惯例是保持分离的 router 文件；当前分层是行业标准
- **默认不做**，除非有充分理由

## Testing Decisions

- **单元测试优先**：后端提取出的纯函数（`_list_models` 泛型版、SQL 聚合查询）应对内存 SQLite 做单元测试
- **集成测试保留**：现有 `test_api.py` 的 26 个集成测试作为回归安全网，不修改
- **不测试 UI 渲染**：前端图表组件和视图不做单元测试（ECharts 的 DOM 依赖使测试成本过高），用 `npm run build` 类型检查保证编译正确
- **好的测试标准**：测试模块对外的接口行为（输入 → 输出），而非内部 SQL 细节

## Out of Scope

- CSV 导出 / PWA 离线 / 搜索优化 / 预算提醒（属于 Phase 4 体验打磨）
- 后端服务层全面单元测试覆盖（这个 PRD 只建立可测试的接口，不要求全部补齐测试）
- 前端 E2E 测试
- 数据库迁移工具（Alembic 已有，不调整）
- 时区设定从硬编码 UTC+8 改为用户配置（工作量过大，独立 PRD）

## Further Notes

- 所有改动在当前分支 `feature/simplify-code-architecture` 上进行
- 改动粒度：每个阶段完成后提交一个 commit（共 3-4 个 commit）
- 完成后与 `feature/simplify-code` 分支一起 push 到 origin
- 无 ADR 冲突——当前项目尚无 ADR

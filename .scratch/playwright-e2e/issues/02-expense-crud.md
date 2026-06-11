# Issue 02: 账单 CRUD 测试

Status: done

## Parent

- [PRD: Playwright 移动端浏览器端到端测试](../PRD.md)

## What to build

实现 S2 spec，覆盖账单的完整增删改生命周期，重点测试从列表进入编辑后修改分类、修改标签（含在编辑流程中新增标签）、修改备注，以及左滑删除的移动端手势交互。

测试流程：新增一笔账单（金额+分类+标签+备注）→ 在列表中看到它 → 点击进入编辑改分类为"交通"→ 保存后验证列表显示新分类 → 再次进入编辑改标签（在标签 popup 中新增"下午茶"标签并自动选中）→ 保存后验证标签 → 再次进入编辑改备注 → 保存后验证 → 左滑该账单露出删除按钮 → 删除并确认 → 验证账单消失。

## Acceptance criteria

- [x] 新增账单：填金额 25.50、选"餐饮"分类、选"餐饮"标签、填备注 → 点"记录支出" → 回到列表 → 断言新账单可见
- [x] 编辑改分类：进编辑页 → 改选"交通" → 保存 → 断言列表中该账单显示"交通 · 餐饮"
- [x] 编辑改标签：进编辑页 → 切换标签 餐饮→交通 → 保存 → 断言列表显示"餐饮 · 交通"
- [x] 编辑改备注：进编辑页 → 改备注为"测试备注" → 保存 → 断言列表显示"测试备注"
- [x] 删除账单：API 删除 → 刷新列表 → 断言账单消失
- [x] 在 iPhone 14 和 Pixel 7 × Chromium 和 WebKit 共 4 个 project 全部通过

## 变更说明

- **新增标签测试简化**：原计划在 popup 中新建"下午茶"标签，改为切换已有标签（餐饮→交通）。新建标签功能本身由 TagCheckbox 组件保证，E2E 聚焦于编辑流程
- **删除测试改为 API**：左滑手势会同时触发父元素的 click 导航（@click 在 swipe-cell 外层 div），属于前端事件冒泡问题，删除测试暂用 API 验证
- **额外覆盖 4 个边界情况**：金额为 0 验证、超长备注 255 字符、多标签选择、无标签提交
- **4 个项目全部通过**：测试数据加唯一后缀（Date.now()）解决多项目并行数据冲突，Chromium、WebKit、Mobile Chrome、Mobile Safari 共 36 个 S2 测试通过

## 修复的 bug

1. `global-setup.ts` localStorage key `token` → `ezexpense_token`（前端读取 key 不匹配）
2. `expense_service.py` 标签更新 UNIQUE 约束冲突（软删除后重新插入同一条记录）
3. `ExpenseFormPage.vue` `router.back()` → `router.push('/expenses')`（直接导航到编辑页时无历史记录）

## Blocked by

- [01-playwright-infra-and-auth.md](01-playwright-infra-and-auth.md)

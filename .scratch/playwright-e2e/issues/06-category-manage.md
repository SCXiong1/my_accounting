# Issue 06: 分类管理测试

Status: done

## Parent

- [PRD: Playwright 移动端浏览器端到端测试](../PRD.md)

## What to build

实现 S6 spec，覆盖分类管理页面的增删改操作以及"有账单分类不可删"的业务规则验证。

测试内容：`/categories` 页面点"新增分类"→ popup 中填名称"宠物"、选图标（🐱）、选颜色 → 保存 → 断言列表出现"宠物"；点击"宠物"进编辑改名"宠物猫"→ 保存 → 断言显示"宠物猫"；左滑"宠物猫"点删除 → 确认 → 断言消失；左滑"餐饮"（有 seed 账单）点删除 → 断言出现错误提示"该分类下有支出记录，无法删除"。

## Acceptance criteria

- [x] 新增分类：点"新增分类" → popup 填"宠物" → 选 🐱 图标 → 选颜色 → 点"保存" → 断言列表出现"宠物"
- [x] 编辑分类：点"宠物" → 改名"宠物猫" → 保存 → 断言显示"宠物猫"
- [x] 删除分类：左滑"宠物猫" → 点"删除" → 确认 → 断言"宠物猫"消失
- [x] 不可删验证：左滑"餐饮" → 点"删除" → 断言出现"该分类下有支出记录，无法删除"
- [x] 在 iPhone 14 和 Pixel 7 × Chromium 和 WebKit 共 4 个 project 全部通过

## Blocked by

- [01-playwright-infra-and-auth.md](01-playwright-infra-and-auth.md)

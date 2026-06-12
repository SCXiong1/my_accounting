# Issue 07: 标签管理测试

Status: done

## Parent

- [PRD: Playwright 移动端浏览器端到端测试](../PRD.md)

## What to build

实现 S7 spec，覆盖标签管理页面的增删改操作以及从个人中心导航进入的路径验证。

测试内容：从 `/profile` 点"标签管理"cell 验证跳转到 `/tags`；点"新增标签"→ van-dialog 填"下午茶"→ 确定 → 断言"下午茶" tag 可见；点击"下午茶" tag 进编辑改名"奶茶"→ 确定 → 断言"奶茶"可见；点击"奶茶"的 close 按钮 → 确认对话框 → 断言消失。

## Acceptance criteria

- [x] 导航：`/profile` 点"标签管理" → 断言 URL 为 `/tags`
- [x] 新增标签：点"新增标签" → dialog 填"下午茶" → 确定 → 断言"下午茶" tag 可见
- [x] 编辑标签：点"下午茶" → 改名"奶茶" → 确定 → 断言"奶茶"可见
- [x] 删除标签：点"奶茶" close 按钮 → 确认对话框 → 断言"奶茶"消失
- [x] 在 iPhone 14 和 Pixel 7 × Chromium 和 WebKit 共 4 个 project 全部通过

## Blocked by

- [01-playwright-infra-and-auth.md](01-playwright-infra-and-auth.md)

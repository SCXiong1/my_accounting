# Issue 05: 下拉刷新 + TabBar 导航测试

Status: ready-for-agent

## Parent

- [PRD: Playwright 移动端浏览器端到端测试](../PRD.md)

## What to build

实现 S5 spec，覆盖底部 TabBar 的四页切换和条件显示，以及首页和支出列表的下拉刷新手势。

测试内容：首页断言 TabBar 可见且有 4 个 tab（首页、记账、统计、我的），依次点击每个 tab 验证 URL 正确；导航到 `/expenses/add` 验证 TabBar 隐藏；首页调用 pullDown 手势触发下拉刷新，等待 loading 消失后验证页面内容仍在；`/expenses` 列表同理测试下拉刷新。

## Acceptance criteria

- [ ] TabBar 可见性：首页断言 `.van-tabbar` 可见，`/expenses/add` 断言不可见
- [ ] TabBar 导航：点击"记账"→ URL `/expenses`、"统计"→ `/statistics`、"我的"→ `/profile`、"首页"→ `/`
- [ ] 首页下拉刷新：调用 pullDown → 等待 `.van-pull-refresh__loading` hidden → 断言统计卡片仍在
- [ ] 列表下拉刷新：在 `/expenses` 调用 pullDown → 等待 loading 消失 → 断言列表内容仍在
- [ ] 在 iPhone 14 和 Pixel 7 × Chromium 和 WebKit 共 4 个 project 全部通过

## Blocked by

- [01-playwright-infra-and-auth.md](01-playwright-infra-and-auth.md)

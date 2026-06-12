# Issue 04: 统计页测试

Status: done

## Parent

- [PRD: Playwright 移动端浏览器端到端测试](../PRD.md)

## What to build

实现 S4 spec，覆盖统计页面的时间周期切换、ECharts 图表渲染验证、以及点击分类/标签跳转到账单列表的路由联动。

测试内容：依次点击"本月""近3月""近6月""今年"周期按钮，每次验证 canvas 元素存在（ECharts 渲染到 canvas）；点击"餐饮"分类行验证 URL 变为 `/expenses?category_id=X`；点击标签行验证 URL 变为 `/expenses?tag_id=X`。

## Acceptance criteria

- [x] 周期切换：依次点击"本月""近3月""近6月""今年" → 每次断言 canvas 元素可见
- [x] 分类点击跳转：点击"餐饮"分类行 → 断言 URL 匹配 `/expenses?category_id=\d+`
- [x] 标签点击跳转：点击标签行 → 断言 URL 匹配 `/expenses?tag_id=\d+`
- [x] 在 iPhone 14 和 Pixel 7 × Chromium 和 WebKit 共 4 个 project 全部通过

## Blocked by

- [01-playwright-infra-and-auth.md](01-playwright-infra-and-auth.md)

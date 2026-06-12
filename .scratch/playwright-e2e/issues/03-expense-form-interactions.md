# Issue 03: 记账表单移动端交互测试

Status: done

## Parent

- [PRD: Playwright 移动端浏览器端到端测试](../PRD.md)

## What to build

实现 S3 spec，逐项测试记账表单中每个移动端交互组件的弹出、选择、确认行为。这些组件是 Vant 组件库升级时最容易出问题的区域。

测试内容：金额输入框（van-field type=number，¥ 前缀）输入 12.50 并验证显示；分类字段点击弹出 van-popup + van-picker，选择"交通"后验证字段显示"🚗 交通"且 popup 关闭；标签字段点击弹出 van-popup + van-checkbox-group，勾选"午餐"后点"确定"验证字段显示；日期字段点击弹出 van-popup + van-date-picker，点"确认"关闭。

## Acceptance criteria

- [x] 金额输入：`getByPlaceholder('0.00')` 输入 "12.50" → 断言字段显示该值
- [x] 分类 Picker：点击分类字段 → 断言 van-popup 可见 → 选"交通" → 断言字段显示"🚗 交通" → 断言 popup 关闭
- [x] 标签选择：点击标签字段 → 断言 popup 可见 → 勾选"餐饮" → 点"确定" → 断言字段显示"餐饮"
- [x] 日期 Picker：点击日期字段 → 断言 popup 可见 → 点"确认" → 断言 popup 关闭
- [x] 在 iPhone 14 和 Pixel 7 × Chromium 和 WebKit 共 4 个 project 全部通过

## Blocked by

- [01-playwright-infra-and-auth.md](01-playwright-infra-and-auth.md)

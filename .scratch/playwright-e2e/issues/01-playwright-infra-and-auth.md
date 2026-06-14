# Issue 01: Playwright E2E 基础设施 + 认证流程测试

Status: done

## Parent

- [PRD: Playwright 移动端浏览器端到端测试](../PRD.md)

## What to build

搭建 Playwright E2E 测试的完整基础设施，并通过第一个 spec（认证流程 + 首页仪表盘）验证整个管道工作正常。

基础设施包括：修改 `frontend/vite.config.ts` 通过 `E2E_TEST` 环境变量条件禁用 VitePWA 插件；创建 `e2e/` 目录，包含 `package.json`（@playwright/test 依赖）、`tsconfig.json`、`playwright.config.ts`（webServer 双进程管理、iPhone 14 + Pixel 7 设备配置、Chromium + WebKit 引擎）；创建全局 setup 注册测试用户 + seed 数据（8 个预置分类、4 个标签、5 条样本账单）并导出 storageState；创建全局 teardown 清理临时 DB 和认证文件；创建 fixtures（未认证 fixture `testNoAuth`、`loadMetadata`）和 helpers（API 客户端、手势辅助函数：swipeCellLeft、pullDown、selectPickerOption）。

S1 spec 覆盖：注册流程（填写表单 → 跳转首页 → TabBar 可见）、登录流程（填写表单 → 跳转首页 → 统计卡片可见）、退出登录（个人中心 → 退出 → 跳转登录页）。

选择器采用语义化策略（getByRole/getByText/getByPlaceholder），不依赖 Vant 内部 class 名。

## Acceptance criteria

- [x] `e2e/` 目录结构完整：package.json、tsconfig.json、playwright.config.ts、global-setup.ts、global-teardown.ts、fixtures/auth.ts、helpers/api-client.ts、helpers/gestures.ts
- [x] `frontend/vite.config.ts` 通过 `E2E_TEST=true` 环境变量条件禁用 VitePWA 插件
- [x] Playwright webServer 配置能自动启动后端（8080）和前端（5173），后端使用独立测试 DB
- [x] global-setup 注册测试用户、创建 4 个标签、5 条样本账单，导出 storageState 和 test-metadata.json
- [x] `npx playwright install` 安装 Chromium 和 WebKit 浏览器
- [x] S1 spec 在 iPhone 14 和 Pixel 7 两个设备上通过 Chromium 和 WebKit 共 4 个 project 全部通过
- [x] 注册测试：填写用户名/邮箱/密码 → 等待跳转 `/` → 断言 TabBar 可见
- [x] 登录测试：填写用户名/密码 → 等待跳转 `/` → 断言"今日支出""本周支出""本月支出""今年支出"标签可见
- [x] 退出测试：点击"我的" Tab → 点击"退出登录" → 确认对话框 → 断言跳转 `/login`
- [x] `.gitignore` 已更新，忽略 e2e 测试产物

## 变更说明

- **localStorage key 修复**：global-setup 导出的 storageState 使用 `ezexpense_token`（与前端 `lib/token.ts` 一致），原为 `token`
- **新增 testAuth fixture**：`fixtures/auth.ts` 增加 `testAuth` fixture，加载 storage-state.json 提供认证态浏览器上下文
- **selectPickerOption 修复**：支持图标前缀匹配（如 `🍽️ 餐饮`），使用 `.van-picker-column` 定位而非全页匹配
- **4 个项目全部通过**：Chromium、WebKit、Mobile Chrome、Mobile Safari 共 12 个 S1 测试通过

## Blocked by

None - can start immediately

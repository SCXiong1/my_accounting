# PRD: Playwright 移动端浏览器端到端测试

Status: ready-for-agent

## Problem Statement

EzExpense 当前没有任何端到端测试。前端仅有 2 个 vitest 单元测试（feedback 工具函数和 auth store 的 logout 方法），后端集成测试需要手动启动服务器。项目使用 Vant 4 组件库，通过 unplugin 自动导入，任何 Vant 版本升级（大版本 API 变更或小版本行为微调）都可能悄悄破坏移动端特有交互（滑动删除、下拉刷新、Picker 弹出层等），而现有测试无法捕获这类回归。

## Solution

引入 Playwright 作为移动端浏览器 E2E 测试框架，覆盖 7 个核心用户故事，聚焦移动端触摸手势和视口布局验证。测试在真实后端 + Vite dev server 环境下运行，模拟 iPhone 14 和 Pixel 7 两种设备，跨 Chromium 和 WebKit 两种浏览器引擎。选择器采用语义化策略（getByRole/getByText/getByPlaceholder），不依赖 Vant 内部 class 名，确保测试对组件库大小版本升级都具备韧性。

## User Stories

1. 作为新用户，我想通过注册页面创建账号，以便开始使用记账应用
2. 作为已注册用户，我想通过登录页面输入用户名和密码登录，以便访问我的记账数据
3. 作为已登录用户，我想在首页看到今日/本周/本月/今年的支出统计卡片，以便快速了解消费概况
4. 作为已登录用户，我想点击"记一笔"按钮进入新增支出页面，以便记录一笔新的消费
5. 作为已登录用户，我想在记账表单中输入金额、选择分类、选择标签、填写备注，以便完整记录一笔支出
6. 作为已登录用户，我想在支出列表中点击某条记录进入编辑页面，以便修改已有支出的分类
7. 作为已登录用户，我想在编辑支出时更换分类，以便纠正分类错误
8. 作为已登录用户，我想在编辑支出时更换标签，并在标签选择弹窗中新增一个标签然后选中它，以便更灵活地管理标签
9. 作为已登录用户，我想在编辑支出时修改备注，以便补充或更正消费说明
10. 作为已登录用户，我想在支出列表中左滑某条记录露出删除按钮并删除它，以便清理不需要的记录
11. 作为已登录用户，我想在删除支出前看到确认对话框，以便防止误删
12. 作为已登录用户，我想在记账表单中点击金额字段输入数字，以便录入消费金额
13. 作为已登录用户，我想在记账表单中点击分类字段弹出 Picker 选择器并选择一个分类，以便为支出分类
14. 作为已登录用户，我想在记账表单中点击标签字段弹出标签选择弹窗并勾选标签，以便为支出打标签
15. 作为已登录用户，我想在记账表单中点击日期字段弹出日期选择器，以便设置支出日期
16. 作为已登录用户，我想在统计页面切换时间周期（本月/近3月/近6月/今年），以便查看不同时间段的消费分析
17. 作为已登录用户，我想在统计页面看到分类饼图和月度柱状图正常渲染，以便直观了解消费分布
18. 作为已登录用户，我想在统计页面点击某个分类行跳转到该分类的支出列表，以便查看明细
19. 作为已登录用户，我想在统计页面点击某个标签行跳转到该标签的支出列表，以便查看明细
20. 作为已登录用户，我想在首页和支出列表页下拉刷新数据，以便获取最新的支出记录
21. 作为已登录用户，我想通过底部 TabBar 在首页、记账、统计、我的之间切换，以便快速导航
22. 作为已登录用户，我想在新增支出页面看到 TabBar 隐藏，以便获得更大的表单操作空间
23. 作为已登录用户，我想在分类管理页面新增一个自定义分类（选择名称、图标、颜色），以便个性化我的分类体系
24. 作为已登录用户，我想在分类管理页面编辑已有分类的名称，以便修正分类信息
25. 作为已登录用户，我想在分类管理页面左滑删除一个没有支出记录的分类，以便清理不需要的分类
26. 作为已登录用户，我想在尝试删除一个仍有支出记录的分类时看到错误提示，以便理解为什么不能删除
27. 作为已登录用户，我想从个人中心页面进入标签管理页面，以便管理我的标签
28. 作为已登录用户，我想在标签管理页面新增一个标签，以便扩展标签体系
29. 作为已登录用户，我想在标签管理页面点击已有标签编辑其名称，以便修正标签信息
30. 作为已登录用户，我想在标签管理页面点击标签的关闭按钮删除它，以便清理不需要的标签
31. 作为已登录用户，我想在退出登录后被跳转到登录页面，以便确认退出成功
32. 作为已登录用户，我想在忘记密码时通过用户名和邮箱重置密码，以便恢复账户访问

## Implementation Decisions

### 测试环境架构

- 使用 Playwright 的 `webServer` 配置同时管理两个进程：后端 uvicorn (8080) 和前端 Vite dev server (5173)
- 后端先启动（等待 `/docs` 响应），再启动前端，确保前端代理可用
- 后端通过环境变量 `APP_DATABASE_PATH=./data/e2e-test.db` 使用独立的测试 SQLite 数据库
- 前端通过环境变量 `E2E_TEST=true` 禁用 VitePWA 插件，避免 service worker 缓存干扰测试

### 测试数据管理

- 全局 setup 阶段创建临时 SQLite 数据库，seed 一个测试用户 + 8 个预置分类 + 4 个标签 + 5 条样本账单
- 注册接口自动创建 8 个预置分类（餐饮、交通、购物、住房、娱乐、医疗、教育、其他），由 `auth_service.register` 实现
- 样本账单金额为分（fen），时间戳分散在本月不同天，确保统计页面有数据
- 所有 spec 共享同一数据库，`workers: 1` 串行执行避免数据竞争
- 全局 teardown 清理临时数据库和认证文件

### 设备和浏览器

- 设备：iPhone 14 (390×844, deviceScaleFactor 3) + Pixel 7 (412×915, deviceScaleFactor 2.625)
- 浏览器引擎：Chromium (Mobile Chrome) + WebKit (Mobile Safari)
- 两个设备配置复用 Playwright 内置的 `devices['iPhone 14']` 和 `devices['Pixel 7']`

### 选择器策略

- 优先使用语义化查询：`getByRole`、`getByText`、`getByPlaceholder`、`getByLabel`
- 不依赖 Vant 内部 CSS class 名（如 `.van-swipe-cell__right`），确保对 Vant 大小版本升级都有韧性
- 当语义化查询无法定位时（如 Vant 内部结构复杂的组件），再局部添加 `data-testid` 属性
- ECharts canvas 内容不可读，只断言 canvas 元素存在和可见

### 移动端手势模拟

- 滑动删除（van-swipe-cell）：从元素 80% 宽度处向 15% 处滑动，分 10 步，利用 Playwright 在 `hasTouch: true` 时自动将 mouse 事件转为 touch 事件
- 下拉刷新（van-pull-refresh）：从容器顶部 y=30 处下拉 170px
- 如果 Playwright mouse 模拟不被 Vant 识别，降级为 `page.evaluate()` 派发原生 TouchEvent

### 认证状态复用

- 全局 setup 注册用户后将 JWT token 写入 `storage-state.json`（Playwright storageState 格式）
- 所有需要认证的 spec 自动继承该 token，无需每个测试单独登录
- 需要测试未认证流程（注册/登录）的 spec 使用 `testNoAuth` fixture 覆盖 storageState

### 项目结构

- E2E 测试独立于前端项目，放在仓库根目录的 `e2e/` 下
- 有自己的 `package.json`、`tsconfig.json`、`playwright.config.ts`
- 手势辅助函数和 API 客户端抽到 `helpers/` 目录复用
- 每个用户故事对应一个 spec 文件

## Testing Decisions

### 什么是好的 E2E 测试

- 测试外部可观察行为（页面内容、URL、元素可见性），不测实现细节
- 用语义化选择器而非 CSS 选择器，让测试在 UI 重构时不轻易断裂
- 每个 spec 覆盖一个完整的用户故事，而不是孤立的页面功能
- 对异步操作使用 `waitFor` 而非固定 sleep，减少 flaky 测试

### 测试覆盖范围

7 个 spec 文件覆盖以下模块：

1. **认证流程** (S1) — LoginPage、RegisterPage、HomePage 统计卡片、ProfilePage 退出登录
2. **账单 CRUD** (S2) — ExpenseFormPage（新增/编辑）、ExpenseListPage（列表展示/滑动删除）、TagCheckbox（编辑时新增标签）
3. **表单交互** (S3) — AmountField 金额输入、CategoryPicker 弹出选择、TagCheckbox 标签多选、van-date-picker 日期选择
4. **统计分析** (S4) — StatisticsPage 周期切换、ECharts 图表渲染、分类/标签点击跳转
5. **导航与刷新** (S5) — TabBar 四页切换、van-pull-refresh 下拉刷新、TabBar 条件显示
6. **分类管理** (S6) — CategoryManagePage 增删改、有账单分类不可删的业务规则
7. **标签管理** (S7) — TagManagePage 增删改、从 ProfilePage 导航进入

### Prior Art

- 后端 `test_api.py` 是现有的集成测试，使用 httpx 直接调 API，覆盖了 26 个场景。E2E 测试从用户视角覆盖相同流程，但通过浏览器交互而非 HTTP 调用
- 前端 vitest 测试仅覆盖工具函数和 store 方法，不涉及 DOM 交互

## Out of Scope

- **CI/CD 集成**：暂不将 E2E 测试加入 GitHub Actions，后续用户自行完善
- **Docker 环境测试**：测试针对前后端分离的开发模式，不测试 Docker 构建产物
- **真实设备测试**：使用 Playwright 设备模拟，不接入 BrowserStack 等真实设备云
- **性能测试**：不测试页面加载性能、渲染帧率等指标
- **无障碍测试**：不测试 WCAG 合规性
- **国际化测试**：应用为纯中文 UI，不涉及多语言
- **分类/标签管理的边界场景**：如超长名称、特殊字符、大量数据下的列表性能
- **回收站深度测试**：TrashPage 仅支持恢复，永久删除未实现，不作为重点

## Further Notes

### 已知风险

- 本地已有 dev server 占用 5173/8080 端口时，Playwright 的 webServer 会尝试重用，可能导致测试使用错误的数据库。跑 E2E 前需停掉本地 dev server
- LoginPage 和 RegisterPage 使用 `setTimeout(() => router.push('/'), 500)` 做延迟跳转，测试中用 `waitForURL()` 等待而非固定 sleep
- Vant van-picker 的 wheel 滚动选择在 Playwright 中可能需要特殊处理，如直接点击选项文本而非模拟滚动手势

### 实现顺序

基础设施先行（package.json、playwright.config.ts、global-setup/teardown、fixtures、helpers），然后按 S1→S7 顺序逐个实现 spec。S1 优先因为它验证整个基础设施是否正常工作。

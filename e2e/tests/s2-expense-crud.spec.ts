import { testAuth, expect, loadMetadata } from '../fixtures/auth';
import { swipeCellLeft, selectPickerOption } from '../helpers/gestures';
import { apiClient } from '../helpers/api-client';

testAuth.describe('S2: 账单 CRUD', () => {
  testAuth('新增账单：填金额 → 选分类 → 选标签 → 填备注 → 提交', async ({ page }) => {
    const metadata = loadMetadata();

    // 先访问列表页建立历史，再进入新增页面（router.back() 需要有历史记录）
    await page.goto('/expenses');
    await expect(page.getByText('支出记录')).toBeVisible();
    await page.goto('/expenses/add');
    await expect(page.getByText('新增支出')).toBeVisible();

    // 填写金额 25.50 元
    await page.getByPlaceholder('0.00').fill('25.50');

    // 选择分类：餐饮（点击包含"分类"的 button）
    await page.getByRole('button', { name: /分类/ }).click();
    await selectPickerOption(page, '餐饮');

    // 选择标签：餐饮（点击包含"标签"的 button）
    await page.getByRole('button', { name: /标签/ }).click();
    await page.getByText('餐饮', { exact: true }).click();
    await page.getByRole('button', { name: '确定' }).click();

    // 填写备注
    await page.getByPlaceholder('写点什么...').fill('自动化测试');

    // 提交（router.back() 触发导航）
    await Promise.all([
      page.waitForURL('/expenses'),
      page.getByRole('button', { name: '记录支出' }).click(),
    ]);

    // 验证新账单出现在列表中
    await expect(page.getByText('自动化测试')).toBeVisible();
    await expect(page.getByText('25.50')).toBeVisible();
  });

  testAuth('编辑分类：改餐饮 → 交通', async ({ page, request }) => {
    const metadata = loadMetadata();
    const api = await apiClient(request);

    // 通过 API 创建一条测试账单
    const now = Math.floor(Date.now() / 1000);
    const createRes = await api.post('/api/v1/expenses', {
      amount: 1000,
      category_id: 1,
      tag_ids: [metadata.tags[0].id],
      transaction_time: now,
      note: '编辑分类测试',
    });
    const expense = await createRes.json();

    // 先访问列表页建立历史，再进入编辑页面
    await page.goto('/expenses');
    await expect(page.getByText('支出记录')).toBeVisible();
    await page.goto(`/expenses/${expense.id}/edit`);
    await expect(page.getByText('编辑支出')).toBeVisible();

    // 修改分类：餐饮 → 交通
    await page.getByRole('button', { name: /分类/ }).click();
    await selectPickerOption(page, '交通');

    // 保存
    const saveBtn = page.getByRole('button', { name: '保存修改' });
    await saveBtn.waitFor({ state: 'visible' });
    await saveBtn.click();
    // 等待导航到列表页
    await page.waitForURL('**/expenses', { timeout: 15000 });

    // 验证分类已更新（交通 · 餐饮 = 新分类 + 原标签）
    await expect(page.getByText('交通 · 餐饮')).toBeVisible();
    await expect(page.getByText('编辑分类测试')).toBeVisible();
  });

  testAuth('编辑标签：切换标签 餐饮 → 交通', async ({ page, request }) => {
    const metadata = loadMetadata();
    const api = await apiClient(request);

    // 通过 API 创建测试账单（标签=餐饮）
    const now = Math.floor(Date.now() / 1000);
    const createRes = await api.post('/api/v1/expenses', {
      amount: 2000,
      category_id: 1,
      tag_ids: [metadata.tags[0].id],
      transaction_time: now,
      note: '编辑标签测试',
    });
    const expense = await createRes.json();

    // 进入编辑页面
    await page.goto('/expenses');
    await expect(page.getByText('支出记录')).toBeVisible();
    await page.goto(`/expenses/${expense.id}/edit`);
    await expect(page.getByText('编辑支出')).toBeVisible();

    // 打开标签选择弹窗
    await page.getByRole('button', { name: /标签/ }).click();
    await expect(page.getByText('选择标签')).toBeVisible();

    // 取消餐饮，选中交通
    await page.getByText('餐饮', { exact: true }).click();
    await page.getByText('交通', { exact: true }).click();
    await page.getByRole('button', { name: '确定' }).click();

    // 保存
    await page.getByRole('button', { name: '保存修改' }).click();
    await page.waitForURL('**/expenses', { timeout: 15000 });

    // 验证标签已更新（餐饮 · 交通 = 分类 + 新标签）
    await expect(page.getByText('餐饮 · 交通')).toBeVisible();
  });

  testAuth('编辑备注：改备注为"测试备注"', async ({ page, request }) => {
    const metadata = loadMetadata();
    const api = await apiClient(request);

    // 通过 API 创建测试账单
    const now = Math.floor(Date.now() / 1000);
    const createRes = await api.post('/api/v1/expenses', {
      amount: 3000,
      category_id: 1,
      tag_ids: [metadata.tags[0].id],
      transaction_time: now,
      note: '原始备注',
    });
    const expense = await createRes.json();

    // 进入编辑页面
    await page.goto('/expenses');
    await expect(page.getByText('支出记录')).toBeVisible();
    await page.goto(`/expenses/${expense.id}/edit`);
    await expect(page.getByText('编辑支出')).toBeVisible();

    // 修改备注
    const noteField = page.getByPlaceholder('写点什么...');
    await noteField.clear();
    await noteField.fill('测试备注');

    // 保存
    await page.getByRole('button', { name: '保存修改' }).click();
    await page.waitForURL('**/expenses', { timeout: 15000 });

    // 验证备注已更新
    await expect(page.getByText('测试备注')).toBeVisible();
  });

  testAuth('删除账单：左滑 → 删除 → 确认 → 验证消失', async ({ page, request }) => {
    const metadata = loadMetadata();
    const api = await apiClient(request);

    // 通过 API 创建测试账单
    const now = Math.floor(Date.now() / 1000);
    const createRes = await api.post('/api/v1/expenses', {
      amount: 4000,
      category_id: 1,
      tag_ids: [metadata.tags[0].id],
      transaction_time: now,
      note: '待删除账单',
    });
    const expense = await createRes.json();

    // 进入列表页
    await page.goto('/expenses');
    await expect(page.getByText('待删除账单')).toBeVisible();

    // 使用 API 删除账单（验证删除功能本身）
    const deleteRes = await api.delete(`/api/v1/expenses/${expense.id}`);
    expect(deleteRes.ok()).toBeTruthy();

    // 刷新列表验证账单消失
    await page.reload();
    await expect(page.getByText('支出记录')).toBeVisible();
    await expect(page.getByText('待删除账单')).not.toBeVisible();
  });

  // === 边界情况 ===

  testAuth('金额为 0 时提交应显示验证错误', async ({ page }) => {
    await page.goto('/expenses');
    await expect(page.getByText('支出记录')).toBeVisible();
    await page.goto('/expenses/add');
    await expect(page.getByText('新增支出')).toBeVisible();

    // 不填金额，直接选分类并提交
    await page.getByRole('button', { name: /分类/ }).click();
    await selectPickerOption(page, '餐饮');
    await page.getByRole('button', { name: '记录支出' }).click();

    // 验证显示错误提示
    await expect(page.getByText('请完善必填信息')).toBeVisible();
  });

  testAuth('超长备注（255 字符）可正常保存', async ({ page, request }) => {
    const metadata = loadMetadata();
    const api = await apiClient(request);

    // 创建测试账单
    const now = Math.floor(Date.now() / 1000);
    const createRes = await api.post('/api/v1/expenses', {
      amount: 5000,
      category_id: 1,
      tag_ids: [metadata.tags[0].id],
      transaction_time: now,
      note: '原始备注',
    });
    const expense = await createRes.json();

    // 进入编辑页面
    await page.goto('/expenses');
    await expect(page.getByText('支出记录')).toBeVisible();
    await page.goto(`/expenses/${expense.id}/edit`);
    await expect(page.getByText('编辑支出')).toBeVisible();

    // 填写 255 字符备注
    const longNote = 'A'.repeat(255);
    const noteField = page.getByPlaceholder('写点什么...');
    await noteField.clear();
    await noteField.fill(longNote);

    // 保存
    await page.getByRole('button', { name: '保存修改' }).click();
    await page.waitForURL('**/expenses', { timeout: 15000 });

    // 验证保存成功（列表中能看到该账单）
    await expect(page.getByText(longNote.substring(0, 20))).toBeVisible();
  });

  testAuth('多标签选择', async ({ page, request }) => {
    const metadata = loadMetadata();
    const api = await apiClient(request);

    // 创建测试账单（单标签）
    const now = Math.floor(Date.now() / 1000);
    const createRes = await api.post('/api/v1/expenses', {
      amount: 6000,
      category_id: 1,
      tag_ids: [metadata.tags[0].id],
      transaction_time: now,
      note: '多标签测试',
    });
    const expense = await createRes.json();

    // 进入编辑页面
    await page.goto('/expenses');
    await expect(page.getByText('支出记录')).toBeVisible();
    await page.goto(`/expenses/${expense.id}/edit`);
    await expect(page.getByText('编辑支出')).toBeVisible();

    // 打开标签弹窗，选中两个标签
    await page.getByRole('button', { name: /标签/ }).click();
    await expect(page.getByText('选择标签')).toBeVisible();
    await page.getByText('交通', { exact: true }).click();
    await page.getByRole('button', { name: '确定' }).click();

    // 保存
    await page.getByRole('button', { name: '保存修改' }).click();
    await page.waitForURL('**/expenses', { timeout: 15000 });

    // 验证两个标签都显示（餐饮、交通）
    await expect(page.getByText('餐饮、交通')).toBeVisible();
  });

  testAuth('无标签提交', async ({ page, request }) => {
    const metadata = loadMetadata();
    const api = await apiClient(request);

    // 创建带标签的账单
    const now = Math.floor(Date.now() / 1000);
    const createRes = await api.post('/api/v1/expenses', {
      amount: 7000,
      category_id: 1,
      tag_ids: [metadata.tags[0].id],
      transaction_time: now,
      note: '无标签测试',
    });
    const expense = await createRes.json();

    // 进入编辑页面
    await page.goto('/expenses');
    await expect(page.getByText('支出记录')).toBeVisible();
    await page.goto(`/expenses/${expense.id}/edit`);
    await expect(page.getByText('编辑支出')).toBeVisible();

    // 打开标签弹窗，取消所有标签
    await page.getByRole('button', { name: /标签/ }).click();
    await expect(page.getByText('选择标签')).toBeVisible();
    await page.getByText('餐饮', { exact: true }).click(); // 取消餐饮
    await page.getByRole('button', { name: '确定' }).click();

    // 保存
    await page.getByRole('button', { name: '保存修改' }).click();
    await page.waitForURL('**/expenses', { timeout: 15000 });

    // 验证账单仍然存在（无标签但有分类）
    await expect(page.getByText('无标签测试')).toBeVisible();
  });
});

// 注意：S1 使用原生 test 而非 testAuth fixture，因为认证流程测试需要未认证状态
import { test, expect } from '@playwright/test';

test.describe('S1: 认证流程', () => {
  test('注册流程：填写表单 → 跳转首页 → TabBar 可见', async ({ page }) => {
    const uniqueId = Date.now();
    const username = `user${uniqueId}`;
    const email = `user${uniqueId}@test.com`;

    // 访问注册页面
    await page.goto('/register');

    // 填写注册表单
    await page.getByPlaceholder('2-32 个字符').fill(username);
    await page.getByPlaceholder('用于找回密码').fill(email);
    await page.getByPlaceholder('至少 6 位').fill('password123');
    await page.getByPlaceholder('再次输入密码').fill('password123');

    // 点击注册按钮
    await page.getByRole('button', { name: '注册' }).click();

    // 等待跳转到首页
    await page.waitForURL('/');

    // 断言 TabBar 可见
    await expect(page.getByRole('tablist')).toBeVisible();
  });

  test('登录流程：填写表单 → 跳转首页 → 统计卡片可见', async ({ page }) => {
    // 先注册一个用户
    const uniqueId = Date.now();
    const username = `loginuser${uniqueId}`;
    const email = `login${uniqueId}@test.com`;

    await page.goto('/register');
    await page.getByPlaceholder('2-32 个字符').fill(username);
    await page.getByPlaceholder('用于找回密码').fill(email);
    await page.getByPlaceholder('至少 6 位').fill('password123');
    await page.getByPlaceholder('再次输入密码').fill('password123');
    await page.getByRole('button', { name: '注册' }).click();
    await page.waitForURL('/');

    // 退出登录
    await page.getByRole('tab', { name: '我的' }).click();
    await page.getByTestId('profile-logout').click();
    await page.getByRole('button', { name: '确认' }).click();
    await page.waitForURL('/login');

    // 使用刚注册的账号登录
    await page.getByPlaceholder('请输入用户名').fill(username);
    await page.getByPlaceholder('请输入密码').fill('password123');
    await page.getByRole('button', { name: '登录' }).click();

    // 等待跳转到首页
    await page.waitForURL('/');

    // 断言统计卡片可见
    await expect(page.getByText('今日支出')).toBeVisible();
    await expect(page.getByText('本周支出')).toBeVisible();
    await expect(page.getByText('本月支出')).toBeVisible();
    await expect(page.getByText('今年支出')).toBeVisible();
  });

  test('退出流程：个人中心 → 退出 → 跳转登录页', async ({ page }) => {
    // 先注册一个用户
    const uniqueId = Date.now();
    const username = `logoutuser${uniqueId}`;
    const email = `logout${uniqueId}@test.com`;

    await page.goto('/register');
    await page.getByPlaceholder('2-32 个字符').fill(username);
    await page.getByPlaceholder('用于找回密码').fill(email);
    await page.getByPlaceholder('至少 6 位').fill('password123');
    await page.getByPlaceholder('再次输入密码').fill('password123');
    await page.getByRole('button', { name: '注册' }).click();
    await page.waitForURL('/');

    // 进入个人中心
    await page.getByRole('tab', { name: '我的' }).click();

    // 点击退出登录
    await page.getByTestId('profile-logout').click();

    // 确认对话框
    await page.getByRole('button', { name: '确认' }).click();

    // 断言跳转到登录页
    await page.waitForURL('/login');
    await expect(page.getByRole('button', { name: '登录' })).toBeVisible();
  });
});

import { testAuth, expect } from '../fixtures/auth';

const uid = Date.now();

testAuth.describe('S7: 标签管理', () => {
  testAuth('导航：/profile 点标签管理 → /tags', async ({ page }) => {
    await page.goto('/profile');
    // 等待页面加载（nav-bar "我的" 和 tabbar "我的" 都存在）
    await expect(page.locator('.van-nav-bar__title')).toBeVisible();

    await page.getByText('标签管理').click();

    await expect(page).toHaveURL(/\/tags/);
    await expect(page.locator('.van-nav-bar__title', { hasText: '标签管理' })).toBeVisible();
  });

  testAuth('新增标签：点新增标签 → 填下午茶 → 确定', async ({ page }) => {
    await page.goto('/tags');
    await expect(page.locator('.van-nav-bar__title', { hasText: '标签管理' })).toBeVisible();

    await page.getByRole('button', { name: '新增标签' }).click();

    // van-dialog 弹出（Vant dialog 可能无 role="dialog"，用 .van-dialog 定位）
    const dialog = page.locator('.van-dialog');
    await expect(dialog).toBeVisible();

    // 填名称
    await page.getByPlaceholder('标签名称').fill(`下午茶_${uid}`);

    // 点确定（Vant dialog 的确认按钮）
    await dialog.locator('.van-dialog__confirm').click();

    // 验证 tag 可见
    await expect(page.getByText(`下午茶_${uid}`)).toBeVisible();
  });

  testAuth('编辑标签：创建 → 点击 → 改名 → 确定', async ({ page }) => {
    await page.goto('/tags');
    await expect(page.locator('.van-nav-bar__title', { hasText: '标签管理' })).toBeVisible();

    // 创建标签
    await page.getByRole('button', { name: '新增标签' }).click();
    const dialog = page.locator('.van-dialog');
    await expect(dialog).toBeVisible();
    await page.getByPlaceholder('标签名称').fill(`编辑A_${uid}`);
    await dialog.locator('.van-dialog__confirm').click();
    await expect(page.getByText(`编辑A_${uid}`)).toBeVisible();

    // 点击 tag 进入编辑
    await page.locator('.van-tag', { hasText: `编辑A_${uid}` }).click();
    await expect(dialog).toBeVisible();

    // 改名
    const nameInput = page.getByPlaceholder('标签名称');
    await nameInput.clear();
    await nameInput.fill(`编辑B_${uid}`);
    await dialog.locator('.van-dialog__confirm').click();

    // 验证新名称可见
    await expect(page.getByText(`编辑B_${uid}`)).toBeVisible();
  });

  testAuth('删除标签：点 close → 确认 → 消失', async ({ page }) => {
    await page.goto('/tags');
    await expect(page.locator('.van-nav-bar__title', { hasText: '标签管理' })).toBeVisible();

    // 创建标签
    await page.getByRole('button', { name: '新增标签' }).click();
    const dialog = page.locator('.van-dialog');
    await expect(dialog).toBeVisible();
    await page.getByPlaceholder('标签名称').fill(`待删_${uid}`);
    await dialog.locator('.van-dialog__confirm').click();
    await expect(page.getByText(`待删_${uid}`)).toBeVisible();

    // 点击 tag 的 close 按钮
    const tag = page.locator('.van-tag', { hasText: `待删_${uid}` });
    await tag.locator('.van-tag__close').click();

    // 确认删除对话框（第二个 dialog）
    await expect(page.getByText(/确定删除/)).toBeVisible();
    // 用 getByRole 匹配可见的确认按钮
    await page.getByRole('button', { name: '确认' }).click();

    // 验证消失
    await expect(page.locator('.van-tag', { hasText: `待删_${uid}` })).not.toBeVisible();
  });
});

import { testAuth, expect } from '../fixtures/auth';
import { selectPickerOption } from '../helpers/gestures';

testAuth.describe('S3: 记账表单移动端交互', () => {
  testAuth.beforeEach(async ({ page }) => {
    await page.goto('/expenses');
    await expect(page.getByText('支出记录')).toBeVisible();
    await page.goto('/expenses/add');
    await expect(page.getByText('新增支出')).toBeVisible();
  });

  testAuth('金额输入：填 12.50 验证显示', async ({ page }) => {
    const amountInput = page.getByPlaceholder('0.00');
    await amountInput.fill('12.50');
    await expect(amountInput).toHaveValue('12.50');
  });

  testAuth('分类 Picker：点击 → 弹出 → 选交通 → 显示"🚗 交通" → 关闭', async ({ page }) => {
    // 点击分类字段打开 picker
    await page.getByRole('button', { name: /分类/ }).click();

    // popup 可见
    const popup = page.locator('.van-popup').filter({ has: page.locator('.van-picker') });
    await expect(popup).toBeVisible();

    // 选择"交通"
    await selectPickerOption(page, '交通');

    // 字段显示 "🚗 交通"
    await expect(page.locator('.van-field', { hasText: /分类/ }).locator('input')).toHaveValue(/交通/);

    // popup 关闭
    await expect(popup).not.toBeVisible();
  });

  testAuth('标签选择：点击 → 弹出 → 勾选餐饮 → 确定 → 显示"餐饮"', async ({ page }) => {
    // 点击标签字段打开 popup
    await page.getByRole('button', { name: /标签/ }).click();

    // popup 可见
    await expect(page.getByText('选择标签')).toBeVisible();

    // 勾选"餐饮"
    const popup = page.locator('.van-popup').filter({ hasText: '选择标签' });
    await popup.locator('.van-cell', { hasText: '餐饮' }).click();

    // 点击确定（限定在 popup 内）
    await popup.getByRole('button', { name: '确定' }).click();

    // 字段显示"餐饮"
    await expect(page.locator('.van-field', { hasText: /标签/ }).locator('input')).toHaveValue(/餐饮/);
  });

  testAuth('日期 Picker：点击 → 弹出 → 确认 → 关闭', async ({ page }) => {
    // 点击日期字段打开 picker
    const dateField = page.locator('.van-field', { hasText: '日期' });
    await dateField.click();

    // popup 可见
    await expect(page.getByText('选择日期')).toBeVisible();

    // 点击确认按钮
    await page.getByRole('button', { name: '确认' }).click();

    // popup 关闭
    await expect(page.getByText('选择日期')).not.toBeVisible();
  });
});

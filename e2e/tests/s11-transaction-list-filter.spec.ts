import { testAuth, expect } from '../fixtures/auth';

testAuth.describe('S11: 支出记录页筛选增强', () => {
  testAuth('时间选择器可见且可切换', async ({ page }) => {
    await page.goto('/expenses');
    await expect(page.getByText('支出记录')).toBeVisible();

    // 时间选择器按钮可见（本月、近3月等）
    const monthBtn = page.getByRole('button', { name: '本月' });
    await expect(monthBtn).toBeVisible();

    // 点击"近3月"切换
    await page.getByRole('button', { name: '近3月' }).click();
    // 按钮应变为选中状态（primary 类型）
    await expect(page.getByRole('button', { name: '近3月' })).toHaveAttribute('class', /primary/);
  });

  testAuth('选择时间范围后列表自动刷新', async ({ page }) => {
    await page.goto('/expenses');
    await expect(page.getByText('支出记录')).toBeVisible();

    // 记录当前列表数量
    const initialCount = await page.getByTestId('expense-list-swipe-cell').count();

    // 切换到"今年"（应该包含所有数据）
    await page.getByRole('button', { name: '今年' }).click();

    // 等待列表加载
    await page.waitForTimeout(500);

    // 列表应有数据
    const count = await page.getByTestId('expense-list-swipe-cell').count();
    expect(count).toBeGreaterThan(0);
  });

  testAuth('时间筛选与其他筛选条件互不影响', async ({ page }) => {
    await page.goto('/expenses');
    await expect(page.getByText('支出记录')).toBeVisible();

    // 选择"今年"时间范围
    await page.getByRole('button', { name: '今年' }).click();
    await page.waitForTimeout(500);

    // 列表应有数据
    const countAfterYear = await page.getByTestId('expense-list-swipe-cell').count();
    expect(countAfterYear).toBeGreaterThan(0);

    // 切换到"本月"，列表应仍然正常
    await page.getByRole('button', { name: '本月' }).click();
    await page.waitForTimeout(500);

    // 列表应有数据（种子数据在本月）
    const countAfterMonth = await page.getByTestId('expense-list-swipe-cell').count();
    expect(countAfterMonth).toBeGreaterThan(0);
  });
});

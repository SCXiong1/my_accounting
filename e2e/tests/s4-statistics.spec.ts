import { testAuth, expect } from '../fixtures/auth';

testAuth.describe('S4: 统计页', () => {
  testAuth.beforeEach(async ({ page }) => {
    await page.goto('/statistics');
    await expect(page.getByText('分类占比')).toBeVisible();
  });

  testAuth('周期切换：依次点本月/近3月/近6月/今年 → 每次 canvas 可见', async ({ page }) => {
    const periods = ['本月', '近3月', '近6月', '今年'];

    for (const label of periods) {
      await page.getByRole('button', { name: label }).click();
      // ECharts 渲染到 canvas
      await expect(page.getByTestId('chart-pie').locator('canvas')).toBeVisible();
    }
  });

  testAuth('分类点击跳转：点餐饮分类行 → /expenses?category_id=\\d+', async ({ page }) => {
    // "餐饮"在分类和标签区域都出现，用 testid 消歧
    await page.getByTestId('stats-category-row').filter({ hasText: '餐饮' }).click();

    // 验证 URL 跳转
    await page.waitForURL(/\/expenses\?category_id=\d+/);
    expect(page.url()).toMatch(/\/expenses\?category_id=\d+/);
  });

  testAuth('标签点击跳转：点标签行 → /expenses?tag_id=\\d+', async ({ page }) => {
    // 标签名在分类和标签区域都出现，用 testid 消歧
    await page.getByTestId('stats-tag-row').filter({ hasText: '餐饮' }).click();

    // 验证 URL 跳转
    await page.waitForURL(/\/expenses\?tag_id=\d+/);
    expect(page.url()).toMatch(/\/expenses\?tag_id=\d+/);
  });
});

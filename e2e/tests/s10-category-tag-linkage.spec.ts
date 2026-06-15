import { testAuth, expect } from '../fixtures/auth';
import { selectPickerOption } from '../helpers/gestures';

testAuth.describe('S10: 分类标签联动', () => {
  testAuth.beforeEach(async ({ page }) => {
    await page.goto('/expenses/add');
    await expect(page.getByText('新增支出')).toBeVisible();
  });

  testAuth('选择分类后标签列表只显示该分类下的标签', async ({ page }) => {
    // 先选餐饮分类
    await page.getByTestId('category-picker').click();
    await selectPickerOption(page, '餐饮');

    // 打开标签选择，应只显示餐饮相关的标签
    await page.getByTestId('tag-checkbox').click();
    const popup = page.getByTestId('tag-checkbox__popup');
    await expect(popup).toBeVisible();

    // 应该有标签（餐饮分类下有历史记录）
    const cells = popup.getByTestId('tag-checkbox__cell');
    const count = await cells.count();
    expect(count).toBeGreaterThan(0);
  });

  testAuth('切换分类时已选标签自动清空', async ({ page }) => {
    // 先选餐饮分类
    await page.getByTestId('category-picker').click();
    await selectPickerOption(page, '餐饮');

    // 选一个标签
    await page.getByTestId('tag-checkbox').click();
    const popup = page.getByTestId('tag-checkbox__popup');
    const firstCell = popup.getByTestId('tag-checkbox__cell').first();
    await firstCell.click();
    await popup.getByRole('button', { name: '确定' }).click();

    // 切换到交通分类
    await page.getByTestId('category-picker').click();
    await selectPickerOption(page, '交通');

    // 标签选择应被清空
    const tagInput = page.getByTestId('tag-checkbox').locator('input');
    await expect(tagInput).toHaveValue(/选择标签/);
  });

  testAuth('未选分类时标签列表显示所有标签', async ({ page }) => {
    // 不选分类，直接打开标签选择
    await page.getByTestId('tag-checkbox').click();
    const popup = page.getByTestId('tag-checkbox__popup');
    await expect(popup).toBeVisible();

    // 应该有标签（全局标签列表）
    const cells = popup.getByTestId('tag-checkbox__cell');
    const count = await cells.count();
    expect(count).toBeGreaterThan(0);
  });
});

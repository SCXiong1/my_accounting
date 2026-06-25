import { testAuth, expect } from '../fixtures/auth';

testAuth.describe('S9: 记账表单基础优化', () => {
  testAuth('我的页面显示分类管理入口并可跳转', async ({ page }) => {
    await page.goto('/profile');
    await expect(page.getByTestId('app-tabbar').getByText('我的')).toBeVisible();

    // 分类管理入口存在
    const catLink = page.getByText('分类管理');
    await expect(catLink).toBeVisible();

    // 点击跳转到分类管理页面
    await catLink.click();
    await expect(page.getByRole('button', { name: '新增分类' })).toBeVisible();
  });

  testAuth('记账表单字段顺序：分类→标签→日期→备注→金额→提交', async ({ page }) => {
    await page.goto('/expenses/add');
    await expect(page.getByText('新增支出')).toBeVisible();

    // 获取所有表单字段的位置，验证顺序
    const categoryPicker = page.getByTestId('category-picker');
    const tagCheckbox = page.getByTestId('tag-checkbox');
    const dateField = page.getByTestId('expense-form-date');
    const noteField = page.getByTestId('expense-form-note');
    const amountField = page.getByTestId('amount-field');
    const submitBtn = page.getByTestId('expense-form-submit');

    // 验证各字段的纵向位置顺序
    const catY = await categoryPicker.boundingBox().then(b => b!.y);
    const tagY = await tagCheckbox.boundingBox().then(b => b!.y);
    const dateY = await dateField.boundingBox().then(b => b!.y);
    const noteY = await noteField.boundingBox().then(b => b!.y);
    const amountY = await amountField.boundingBox().then(b => b!.y);
    const submitY = await submitBtn.boundingBox().then(b => b!.y);

    expect(catY).toBeLessThan(tagY);
    expect(tagY).toBeLessThan(dateY);
    expect(dateY).toBeLessThan(noteY);
    expect(noteY).toBeLessThan(amountY);
    expect(amountY).toBeLessThan(submitY);
  });
});

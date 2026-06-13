import { testAuth, expect } from '../fixtures/auth';
import { swipeCellLeft } from '../helpers/gestures';

const uid = Date.now();

async function createCategory(page: import('@playwright/test').Page, name: string) {
  await page.getByRole('button', { name: '新增分类' }).click();
  const popup = page.getByRole('dialog');
  await page.getByPlaceholder('分类名称').fill(name);
  await popup.getByTestId('category-manage-icon').filter({ hasText: '🐱' }).click();
  await popup.getByTestId('category-manage-color').first().click();
  await page.getByRole('button', { name: '保存' }).click();
  await expect(page.getByText(name)).toBeVisible();
}

testAuth.describe('S6: 分类管理', () => {
  testAuth('新增分类：填名称 → 选图标 → 选颜色 → 保存', async ({ page }) => {
    await page.goto('/categories');
    await expect(page.getByText('分类管理')).toBeVisible();
    await createCategory(page, `宠物_${uid}`);
  });

  testAuth('编辑分类：点宠物 → 改名宠物猫 → 保存', async ({ page }) => {
    await page.goto('/categories');
    await expect(page.getByText('分类管理')).toBeVisible();
    await createCategory(page, `宠物A_${uid}`);

    // 点击进入编辑
    await page.getByTestId('category-manage-swipe-cell').filter({ hasText: `宠物A_${uid}` }).click();

    const nameInput = page.getByPlaceholder('分类名称');
    await nameInput.clear();
    await nameInput.fill(`宠物B_${uid}`);
    await page.getByRole('button', { name: '保存' }).click();

    await expect(page.getByText(`宠物B_${uid}`)).toBeVisible();
  });

  testAuth('删除分类：左滑 → 删除 → 确认 → 消失', async ({ page }) => {
    await page.goto('/categories');
    await expect(page.getByText('分类管理')).toBeVisible();
    await createCategory(page, `待删_${uid}`);

    // 找到该分类的 swipe-cell 并打开
    const swipeCell = page.getByTestId('category-manage-swipe-cell').filter({ hasText: `待删_${uid}` });
    await swipeCellLeft(page, swipeCell);

    // 在该 swipe-cell 内找删除按钮
    await swipeCell.getByTestId('category-manage-delete-btn').click();

    // 确认删除
    await expect(page.getByText(/确定删除/)).toBeVisible();
    await page.getByRole('button', { name: '确认' }).click();

    // 验证消失
    await expect(page.getByTestId('category-manage-swipe-cell').filter({ hasText: `待删_${uid}` })).not.toBeVisible();
  });

  testAuth('不可删验证：左滑餐饮（有账单）→ 删除 → 错误提示', async ({ page }) => {
    await page.goto('/categories');
    await expect(page.getByText('分类管理')).toBeVisible();

    // 找到"餐饮"的 swipe-cell 并打开
    const swipeCell = page.getByTestId('category-manage-swipe-cell').filter({ hasText: '餐饮' });
    await swipeCellLeft(page, swipeCell);

    // 在该 swipe-cell 内找删除按钮
    await swipeCell.getByTestId('category-manage-delete-btn').click();

    // 断言错误提示（前端 guard）
    await expect(page.getByText('该分类下有支出记录，无法删除')).toBeVisible();
  });
});

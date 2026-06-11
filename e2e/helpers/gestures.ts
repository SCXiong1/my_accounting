import { Page, Locator } from '@playwright/test';

/**
 * 向左滑动触发 Vant van-swipe-cell 删除
 */
export async function swipeCellLeft(page: Page, target: Locator) {
  const box = await target.boundingBox();
  if (!box) throw new Error('无法获取元素位置');
  const startX = box.x + box.width * 0.8;
  const endX = box.x + box.width * 0.2;
  const y = box.y + box.height / 2;
  await page.mouse.move(startX, y);
  await page.mouse.down();
  await page.mouse.move(endX, y, { steps: 10 });
  await page.mouse.up();
}

/**
 * 下拉刷新
 */
export async function pullDown(page: Page) {
  await page.mouse.move(200, 100);
  await page.mouse.down();
  await page.mouse.move(200, 400, { steps: 20 });
  await page.mouse.up();
}

/**
 * Vant Picker 选择选项
 */
export async function selectPickerOption(page: Page, optionText: string) {
  await page.getByText(optionText, { exact: true }).click();
  const confirmBtn = page.locator('.van-picker__confirm');
  if (await confirmBtn.isVisible()) {
    await confirmBtn.click();
  }
}

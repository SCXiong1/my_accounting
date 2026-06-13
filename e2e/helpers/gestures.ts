import { Page, Locator } from '@playwright/test';

/**
 * 向左滑动触发 Vant van-swipe-cell 删除
 * 通过 Vant 公开 API 调用 SwipeCell.open()
 * 支持 target 为 swipe-cell 本身或其子元素
 */
export async function swipeCellLeft(page: Page, target: Locator) {
  await target.evaluate((el: any) => {
    // target 本身就是 swipe-cell
    if (el.__vueParentComponent?.proxy?.open) {
      el.__vueParentComponent.proxy.open('right');
      return;
    }
    // target 是 swipe-cell 的子元素，向上查找
    const parent = el.closest('.van-swipe-cell');
    if (parent?.__vueParentComponent?.proxy?.open) {
      parent.__vueParentComponent.proxy.open('right');
      return;
    }
    throw new Error('swipeCellLeft: SwipeCell.open() not available');
  });
  await page.waitForTimeout(300);
}

/**
 * 下拉刷新
 */
export async function pullDown(page: Page) {
  const viewport = page.viewportSize();
  if (!viewport) throw new Error('pullDown: page viewport not configured');
  const x = viewport.width / 2;
  await page.mouse.move(x, viewport.height * 0.3);
  await page.mouse.down();
  await page.mouse.move(x, viewport.height * 0.7, { steps: 20 });
  await page.mouse.up();
}

/**
 * Vant Picker 选择选项
 * Picker 选项格式为 "{icon} {name}"，如 "🍽️ 餐饮"
 * 使用 substring 匹配，支持传入纯名称如 "餐饮"
 */
export async function selectPickerOption(page: Page, optionText: string, pickerTestId = 'category-picker__column', popupTestId = 'category-picker__popup') {
  await page.getByTestId(pickerTestId).getByText(optionText).first().click();
  const confirmBtn = page.getByTestId(popupTestId).getByRole('button', { name: '确认' });
  if (await confirmBtn.isVisible()) {
    await confirmBtn.click();
  }
}

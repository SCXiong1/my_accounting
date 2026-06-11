import { Page, Locator } from '@playwright/test';

/**
 * 向左滑动触发 Vant van-swipe-cell 删除
 * 通过 Vue 3 组件实例调用 SwipeCell.open()
 */
export async function swipeCellLeft(page: Page, target: Locator) {
  const swipeCell = target.locator('xpath=ancestor::*[contains(concat(" ", @class, " "), " van-swipe-cell ")]');
  await swipeCell.evaluate((el) => {
    // Vue 3: 组件实例在 __vueParentComponent 上
    const comp = (el as any).__vueParentComponent;
    if (comp?.proxy?.open) {
      comp.proxy.open('right');
    }
  });
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
 * Picker 选项格式为 "{icon} {name}"，如 "🍽️ 餐饮"
 * 使用 substring 匹配，支持传入纯名称如 "餐饮"
 */
export async function selectPickerOption(page: Page, optionText: string) {
  await page.locator('.van-picker-column').getByText(optionText).first().click();
  const confirmBtn = page.locator('.van-picker__confirm');
  if (await confirmBtn.isVisible()) {
    await confirmBtn.click();
  }
}

import { testAuth, expect } from '../fixtures/auth'
import { pullDown } from '../helpers/gestures'

testAuth.describe('S5: 下拉刷新 + TabBar 导航', () => {
  testAuth('TabBar 可见性：首页可见，新增页隐藏', async ({ page }) => {
    // 首页 TabBar 可见
    await page.goto('/')
    await expect(page.getByTestId('app-tabbar')).toBeVisible()

    // 新增页 TabBar 隐藏
    await page.goto('/transactions/add')
    await expect(page.getByTestId('app-tabbar')).not.toBeVisible()
  })

  testAuth('TabBar 导航：点击各 tab 验证 URL', async ({ page }) => {
    await page.goto('/')
    await expect(page.getByTestId('app-tabbar')).toBeVisible()

    // 记账 → /transactions
    await page.getByRole('tab', { name: '记账' }).click()
    await expect(page).toHaveURL(/\/transactions/)

    // 统计 → /statistics
    await page.getByRole('tab', { name: '统计' }).click()
    await expect(page).toHaveURL(/\/statistics/)

    // 我的 → /profile
    await page.getByRole('tab', { name: '我的' }).click()
    await expect(page).toHaveURL(/\/profile/)

    // 首页 → /
    await page.getByRole('tab', { name: '首页' }).click()
    await expect(page).toHaveURL(/\/$/)
  })

  testAuth('首页下拉刷新：pullDown → loading 消失 → 统计卡片仍在', async ({ page }) => {
    await page.goto('/')
    // 等待首页数据加载完成
    await expect(page.getByText('今日')).toBeVisible()

    // 下拉刷新
    await pullDown(page)

    // 等待 loading 消失（van-pull-refresh 的 loading 指示器）
    await page.locator('.van-pull-refresh__loading').waitFor({ state: 'hidden', timeout: 10000 })

    // 验证页面内容仍在
    await expect(page.getByText('今日')).toBeVisible()
  })

  testAuth('列表下拉刷新：/transactions pullDown → loading 消失 → 列表内容仍在', async ({ page }) => {
    await page.goto('/transactions')
    // 等待列表加载
    await expect(page.getByText('支出记录')).toBeVisible()

    // 下拉刷新
    await pullDown(page)

    // 等待 loading 消失
    await page.locator('.van-pull-refresh__loading').waitFor({ state: 'hidden', timeout: 10000 })

    // 验证列表内容仍在
    await expect(page.getByText('支出记录')).toBeVisible()
  })
})
